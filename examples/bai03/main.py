"""Chạy: python -m examples.bai03.main --mode all."""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import textwrap
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (roc_curve, precision_recall_curve, roc_auc_score,
                             average_precision_score, f1_score)
from threadpoolctl import threadpool_limits
from mlcourse.common import parser, setup, figure, save_figure, finish, write_csv, write_json, COLORS
from mlcourse.sms import load_sms, FEATURES
from examples.bai03.algorithms import measure, auc_pairwise, select_votes

def matrix(ax, report, title):
    values = np.array([[report['tn'], report['fp']], [report['fn'], report['tp']]])
    ax.imshow(values, cmap='Blues', vmin=0)
    for i, row in enumerate([['TN', 'FP'], ['FN', 'TP']]):
        for j, name in enumerate(row):
            ax.text(j, i, f'{name}\n{values[i,j]}', ha='center', va='center', fontsize=24,
                    color='white' if values[i,j] > values.max()*.55 else '#172C43')
    ax.set(xticks=[0,1], yticks=[0,1], xticklabels=['Ham (0)', 'Spam (1)'],
           yticklabels=['Ham (0)', 'Spam (1)'], xlabel='Dự đoán', ylabel='Nhãn thật', title=title)

def toy(args):
    y = np.array([1,0,1,1,0,1,0,0,0,0])
    s = np.array([.95,.90,.85,.70,.60,.55,.40,.30,.20,.10])
    reports = [dict(threshold=t, **measure(y, s >= t)) for t in [.5,.8,.9,args.threshold]]
    d = pd.DataFrame({'id':list('ABCDEFGHIJ'), 'y':y, 'score':s, 'prediction':s >= args.threshold})
    write_csv(args.output_dir/'toy_rows.csv', d)
    write_csv(args.output_dir/'toy_thresholds.csv', reports)
    fig, axes = figure('Bài 3 · Từ điểm số đến bốn ô đếm', 2)
    ax = axes[0,0]
    for truth, label, color in [(0,'Ham thật',COLORS[0]),(1,'Spam thật',COLORS[3])]:
        mask = y == truth
        ax.scatter(s[mask], np.arange(10)[mask], s=120, label=label, color=color)
    ax.axvline(args.threshold, color=COLORS[2], ls='--', label=f'Ngưỡng {args.threshold:g}')
    ax.set(xlabel='Điểm', yticks=range(10), yticklabels=list('ABCDEFGHIJ'), xlim=(-.04,1.04))
    ax.invert_yaxis();ax.legend(loc='lower right')
    matrix(axes[0,1], reports[-1], r'Quyết định: $\hat y=1$ nếu $s\geq t$')
    save_figure(fig,args,'toy_confusion','Dữ liệu mô phỏng · Tăng ngưỡng không bảo đảm precision tăng; hãy so ngưỡng 0,80 và 0,90.')
    return {'thresholds':reports, 'auc_four_points':auc_pairwise([1,1,0,0],[.8,.4,.6,.2])}

def real(args):
    d,tr,va,te,raw_count = load_sms(args.data_dir,args.seed)
    scaler = StandardScaler().fit(d.loc[tr,FEATURES].to_numpy())
    model = KNeighborsClassifier(n_neighbors=11).fit(scaler.transform(d.loc[tr,FEATURES].to_numpy()),d.loc[tr,'y'])
    def predict(ids):
        a=d.loc[ids,['message_id','source_record','text','y']].copy()
        with threadpool_limits(limits=2):
            a['score']=model.predict_proba(scaler.transform(d.loc[ids,FEATURES].to_numpy()))[:,1]
        a['votes']=np.rint(a.score*11).astype(int)
        if not np.allclose(a.score,a.votes/11): raise AssertionError('Sai quy ước phiếu')
        a['prediction']=(a.votes>=6).astype(int)
        return a
    validation=predict(va)
    scan, chosen = select_votes(validation.y,validation.votes)
    # Khóa chính sách trước khi tính và báo điểm test.
    policy={key: {'min_votes':row['min_votes'],'validation':row} for key,row in chosen.items()}
    write_json(args.output_dir/'threshold_policy.json', {'selection':'validation only', 'policies':policy,
               'tie_rule':'min cost, then fewer alerts, then larger threshold', 'costs':'hypothetical'})
    test=predict(te)
    base=measure(test.y,test.prediction)
    assert np.isclose(base['f1'],f1_score(test.y,test.prediction))
    for key,row in policy.items():
        row['test']=measure(test.y,test.votes>=row['min_votes'])
    write_csv(args.output_dir/'validation_scan.csv',scan)
    write_csv(args.output_dir/'validation_predictions.csv',validation)
    write_csv(args.output_dir/'test_predictions.csv',test)
    baseline=measure(test.y,np.zeros(len(test),int))
    fig,axes=figure('Bài 3 · Accuracy cần được đọc cùng cấu trúc lỗi',2)
    matrix(axes[0,0],baseline,f'Luôn ham · Accuracy = {baseline["accuracy"]:.3f}')
    matrix(axes[0,1],base,f'kNN(11) · Accuracy = {base["accuracy"]:.3f}')
    save_figure(fig,args,'real_confusion','Test SMS lịch sử · Luôn ham có recall spam = 0; precision không xác định vì không có cảnh báo.')
    fig,axes=figure('Bài 3 · Chọn chính sách trên validation',2)
    frame=pd.DataFrame(scan)
    for ax,key,title in zip(axes[0],policy,['Chặn nhầm đắt hơn: 5FP + FN','Bỏ lọt đắt hơn: FP + 5FN']):
        ax.plot(frame.min_votes,frame[key],'o-')
        m=policy[key]['min_votes'];v=chosen[key][key]
        ax.scatter([m],[v],s=190,c=COLORS[3],zorder=5)
        ax.annotate(f'Chọn m={m}\nChi phí={v}',(m,v),xytext=(12,25),textcoords='offset points')
        ax.set(xlabel='Số phiếu spam tối thiểu (trên 11)',ylabel='Chi phí giả định',title=title,xticks=range(1,13))
        ax.grid(alpha=.18)
    save_figure(fig,args,'real_cost','Ngưỡng được khóa trước khi báo test · m = 12 không tạo cảnh báo · Không dùng chi phí này như tiền thật.')
    p,r,_=precision_recall_curve(test.y,test.score)
    fpr,tpr,_=roc_curve(test.y,test.score)
    auc=auc_pairwise(test.y,test.score);ap=float(-np.sum(np.diff(r)*p[:-1]))
    assert np.isclose(auc,roc_auc_score(test.y,test.score))
    assert np.isclose(ap,average_precision_score(test.y,test.score))
    fig,axes=figure('Bài 3 · Đánh giá thứ tự điểm trên test',2)
    axes[0,0].plot(fpr,tpr,'o-',label=f'ROC AUC = {auc:.4f}')
    axes[0,0].plot([0,1],[0,1],'--',color='gray')
    axes[0,0].set(xlabel='FPR = FP / (FP + TN)',ylabel='TPR = recall',title='ROC')
    axes[0,1].step(r,p,where='post',label=f'AP = {ap:.4f}')
    axes[0,1].axhline(test.y.mean(),ls='--',color='gray',label=f'Tỷ lệ spam = {test.y.mean():.3f}')
    axes[0,1].set(xlabel='Recall',ylabel='Precision',title='Precision–recall')
    for ax in axes[0]: ax.set_xlim(-.02,1.02);ax.set_ylim(-.02,1.03);ax.legend(loc='lower left');ax.grid(alpha=.2)
    write_csv(args.output_dir/'roc_points.csv',pd.DataFrame({'fpr':fpr,'tpr':tpr}))
    write_csv(args.output_dir/'pr_points.csv',pd.DataFrame({'recall':r,'precision':p}))
    save_figure(fig,args,'real_ranking','AP được tính theo bước tăng recall, không dùng công thức hình thang · Tỷ lệ phiếu chưa bảo đảm hiệu chuẩn.')
    examples=[]
    fig,axes=figure('Bài 3 · Một chỉ số bắt đầu từ những SMS cụ thể',2,2)
    for ax,(name,truth,pred) in zip(axes.flat,[('TP',1,1),('FP',0,1),('FN',1,0),('TN',0,0)]):
        group=test[(test.y==truth)&(test.prediction==pred)].sort_values('source_record')
        short=group[group.text.str.len()<=180]
        row=(short if len(short) else group).head(1)
        ax.axis('off')
        if len(row):
            item=row.iloc[0].to_dict();item['outcome']=name;examples.append(item)
            ax.set_title(f'{name} · ID {item["source_record"]} · {item["votes"]}/11 phiếu',loc='left',color=COLORS[3] if name in ['FP','FN'] else COLORS[0])
            ax.text(0,.83,textwrap.fill(item['text'],55),fontsize=14,va='top',transform=ax.transAxes)
        else: ax.set_title(f'{name}: không có mẫu trong lần chạy này')
    write_csv(args.output_dir/'error_examples.csv',examples)
    save_figure(fig,args,'real_sms_errors','Trích nguyên văn corpus lịch sử · Hai đặc trưng hình thức chưa hiểu đầy đủ nội dung tin nhắn.')
    return {'raw_rows':raw_count,'split_sizes':[len(tr),len(va),len(te)], 'model':'train scaler + fixed kNN(11)',
            'base':base,'always_ham':baseline,'selected':policy,'roc_auc':auc,'average_precision':ap,
            'test_scope':'Same historical B2 holdout; not an independent new test.'}

def main():
    p=parser(3,'Ma trận nhầm lẫn, chỉ số và ngưỡng cảnh báo spam')
    p.add_argument('--threshold',type=float,default=.5,help='Ngưỡng cho ví dụ mô phỏng')
    args=p.parse_args()
    if not 0<=args.threshold<=1: p.error('--threshold cần nằm trong [0,1]')
    setup(args);out={}
    if args.mode in ['toy','all']: out['toy']=toy(args)
    if args.mode in ['real','all']: out['real']=real(args)
    finish(args,3,out)

if __name__=='__main__': main()
