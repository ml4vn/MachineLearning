"""Một con số tốt chỉ có ý nghĩa khi cách tạo ra nó hợp lệ."""
from pathlib import Path
import sys
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import zipfile
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold,StratifiedKFold,GroupShuffleSplit,train_test_split,GridSearchCV
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score,average_precision_score
from threadpoolctl import threadpool_limits
from mlcourse.common import parser,setup,figure,save_figure,write_csv,write_json,finish,COLORS,require_file
from mlcourse.olist import prepare_olist,FEATURES,DATES
from mlcourse.classification import plot_confusion
from lessons.bai03.algorithms import measure
from lessons.bai07.algorithms import asof_fold,memorize_groups,repeated_selection

def pipeline():
    return Pipeline([('imputer',SimpleImputer(strategy='median')),('scaler',StandardScaler()),
                     ('model',LogisticRegression(solver='newton-cg',C=1,max_iter=200))])

def nested_demo(args):
    X,y=make_classification(n_samples=300,n_features=12,n_informative=4,n_redundant=2,random_state=args.seed)
    outer=StratifiedKFold(n_splits=3,shuffle=True,random_state=args.seed);rows=[];membership=[]
    with threadpool_limits(limits=2):
        for fold,(tr,va) in enumerate(outer.split(X,y),1):
            inner=StratifiedKFold(n_splits=3,shuffle=True,random_state=args.seed+fold)
            search=GridSearchCV(pipeline(),{'model__C':[.1,1.,10.]},scoring='accuracy',cv=inner,refit=True,n_jobs=1,error_score='raise')
            search.fit(X[tr],y[tr])
            pred=search.predict(X[va])
            rows.append({'outer_fold':fold,'selected_C':search.best_params_['model__C'],'inner_best_accuracy':float(search.best_score_),
                         'outer_accuracy':float(accuracy_score(y[va],pred)),'train_n':len(tr),'outer_n':len(va)})
            for role,ids in [('train',tr),('outer_validation',va)]:membership.extend({'outer_fold':fold,'id':int(i),'role':role} for i in ids)
            write_csv(args.output_dir/f'nested_inner_candidates_fold{fold}.csv',pd.DataFrame(search.cv_results_).drop(columns=['params']))
    write_csv(args.output_dir/'nested_outer_results.csv',rows);write_csv(args.output_dir/'nested_membership.csv',membership)
    write_csv(args.output_dir/'nested_synthetic_data.csv',pd.DataFrame(X,columns=[f'x{i}' for i in range(12)]).assign(y=y))
    return rows

def toy(args):
    correct=StandardScaler().fit([[0],[2]]);leaky=StandardScaler().fit([[0],[2],[10]])
    scalers=[{'method':name,'mean':s.mean_[0],'std':s.scale_[0],'test_z':s.transform([[10]])[0,0]} for name,s in [('train_only',correct),('all_data_wrong',leaky)]]
    write_csv(args.output_dir/'toy_scalers.csv',scalers)
    X=np.arange(0,12,2.)[:,None];y=np.array([0,0,0,1,1,1]);folds=[];mask=np.zeros((3,6),int)
    for fold,(tr,va) in enumerate(KFold(3).split(X),1):
        pipe=pipeline().fit(X[tr],y[tr]);mean=pipe.named_steps['scaler'].mean_[0]
        if not np.isclose(mean,X[tr].mean()):raise AssertionError('Scaler đã thấy ngoài train fold')
        folds.append({'fold':fold,'train_ids':(tr+1).tolist(),'validation_ids':(va+1).tolist(),'scaler_train_mean':mean,'accuracy':pipe.score(X[va],y[va])})
        mask[fold-1,va]=1
    write_json(args.output_dir/'toy_folds.json',folds)
    fig,axes=figure('Bài 7 · Fit đúng nơi, transform đúng dữ liệu',2)
    q=np.arange(3);width=.35
    for offset,s,label in [(-width/2,correct,'Fit train [0,2]'),(width/2,leaky,'Fit sai cả [0,2,10]')]:
        values=s.transform([[0],[2],[10]]).ravel();axes[0,0].bar(q+offset,values,width,label=label)
    axes[0,0].set(xticks=q,xticklabels=['Train: 0','Train: 2','Điểm mới: 10'],ylabel='Giá trị chuẩn hóa',title='Điểm mới có z = 9 nếu fit đúng');axes[0,0].legend()
    axes[0,1].imshow(mask,cmap='Blues',vmin=0,vmax=1,aspect='auto')
    for i in range(3):
        for j in range(6):axes[0,1].text(j,i,'Val' if mask[i,j] else 'Train',ha='center',va='center',fontsize=13,color='white' if mask[i,j] else '#172C43')
    axes[0,1].set(xticks=range(6),xticklabels=range(1,7),yticks=range(3),yticklabels=['Fold 1','Fold 2','Fold 3'],xlabel='ID dòng mô phỏng',title='Mỗi fold fit một pipeline mới')
    save_figure(fig,args,'toy_scaler_folds','K-fold sáu dòng chỉ minh họa cơ chế · Chọn phương án chia còn phải xét thời gian, nhóm và mục tiêu dự đoán.')
    group=np.repeat(np.arange(200),4);rng=np.random.default_rng(73);ygroup=rng.permutation(np.repeat([0,1],100))[group]
    splits=[('row',train_test_split(np.arange(800),test_size=.2,random_state=args.seed)),
            ('group',next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=args.seed).split(group,groups=group)))]
    group_rows=[];pred_rows=[]
    for name,(tr,va) in splits:
        pred,report=memorize_groups(group,ygroup,tr,va);group_rows.append({'split':name,'train':len(tr),'validation':len(va),**report})
        pred_rows.extend({'split':name,'id':int(i),'group':int(group[i]),'y':int(ygroup[i]),'prediction':int(p)} for i,p in zip(va,pred))
    write_csv(args.output_dir/'toy_groups.csv',pd.DataFrame({'group':group,'y':ygroup}));write_csv(args.output_dir/'toy_group_predictions.csv',pred_rows)
    selection,details=repeated_selection();write_csv(args.output_dir/'toy_selection.csv',selection);write_csv(args.output_dir/'toy_selection_repeats.csv',details)
    fig,axes=figure('Bài 7 · Hai cách tạo ra một điểm số lạc quan',2)
    vals=[r['accuracy'] for r in group_rows];axes[0,0].bar(['Chia theo dòng','Chia theo nhóm'],vals,color=[COLORS[3],COLORS[0]])
    for i,r in enumerate(group_rows):axes[0,0].text(i,r['accuracy']+.03,f'{r["accuracy"]:.1%}\n{r["shared_groups"]} nhóm giao nhau',ha='center',fontsize=16)
    axes[0,0].set(ylim=(0,1.16),ylabel='Accuracy validation',title='Mô phỏng bộ ghi nhớ nhóm')
    for key,label in [('selected_mean','Điểm dùng để chọn'),('fresh_mean','Điểm trên mẫu mới')]:axes[0,1].plot([r['candidates'] for r in selection],[r[key] for r in selection],'o-',label=label)
    axes[0,1].set(xscale='log',xticks=[1,10,100],xticklabels=['1','10','100'],xlabel='Số ứng viên ngẫu nhiên',ylabel='Accuracy trung bình 500 lần',title='Mô phỏng chọn nhiều ứng viên');axes[0,1].legend()
    save_figure(fig,args,'toy_group_selection','Cả hai thí nghiệm là mô phỏng · Test bị dùng để chọn mất vai trò đánh giá độc lập, dù không gọi model.fit trên test.')
    nested=nested_demo(args)
    fig,axes=figure('Bài 7 · Nested CV đánh giá cả thủ tục chọn mô hình')
    ax=axes[0,0];q=np.arange(3)
    ax.bar(q-.18,[r['inner_best_accuracy'] for r in nested],.36,label='Inner: điểm tốt nhất để chọn C')
    ax.bar(q+.18,[r['outer_accuracy'] for r in nested],.36,label='Outer: điểm đánh giá thủ tục')
    ax.set(xticks=q,xticklabels=[f'Outer {r["outer_fold"]}\nChọn C = {r["selected_C"]:g}' for r in nested],ylabel='Accuracy',ylim=(0,1.08),title='Dữ liệu phân loại mô phỏng riêng: 300 dòng, 12 đặc trưng');ax.legend(loc='upper left')
    save_figure(fig,args,'toy_nested_cv','Pipeline được fit lại trong từng inner fold; best estimator refit outer-train · SD giữa fold không tự là khoảng tin cậy.')
    return {'scalers':scalers,'folds':folds,'groups':group_rows,'selection':selection,'nested_cv_added_demo':nested}

def real(args):
    d,audit=prepare_olist(args.data_dir)
    write_json(args.output_dir/'preparation_audit.json',audit)
    parts={k:d[d.split==k] for k in ['train','validation','test']}
    counts=[{'split':k,'n':len(v),'late':int(v.late.sum()),'rate':float(v.late.mean())} for k,v in parts.items()]
    write_csv(args.output_dir/'split_counts.csv',counts)
    te=parts['test'];future=(te.order_delivered_customer_date.dt.normalize()-te.order_estimated_delivery_date.dt.normalize()).dt.days
    pred=(future>0).astype(int);bad=measure(te.late,pred)
    if not np.array_equal(pred,te.late):raise AssertionError('Cột tạo nhãn phải tái tạo đúng nhãn')
    write_csv(args.output_dir/'INVALID_future_column_predictions.csv',te[['order_id','late']].assign(INVALID_future_late_days=future,prediction=pred))
    with zipfile.ZipFile(require_file(args.data_dir,'olist.zip')) as z:
        with z.open('olist_orders_dataset.csv') as f:orders=pd.read_csv(f,parse_dates=DATES)
    delayed=orders[(orders.order_approved_at>='2017-01-01')&(orders.order_approved_at<'2017-11-01')&(orders.order_delivered_customer_date>='2017-11-01')]
    write_csv(args.output_dir/'labels_after_cutoff.csv',delayed[['order_id']+DATES])
    shared=set(parts['train'].customer_unique_id)&set(te.customer_unique_id)
    write_csv(args.output_dir/'shared_customers.csv',[{'customer_unique_id':c} for c in sorted(shared)])
    example=d[d.order_id=='66e4624ae69e7dc89bd50222b59f581f'].iloc[0]
    fig,axes=figure('Bài 7 · Một cột tương lai có thể tạo điểm tuyệt đối',2)
    plot_confusion(axes[0,0],bad,'KHÔNG HỢP LỆ tại lúc duyệt đơn')
    axes[0,1].bar([r['split'] for r in counts],[r['rate']*100 for r in counts],color=COLORS[:3])
    for i,r in enumerate(counts):axes[0,1].text(i,r['rate']*100+.15,f'{r["rate"]:.2%}',ha='center',fontsize=18)
    axes[0,1].set(ylabel='Tỷ lệ trễ (%)',ylim=(0,max(r['rate'] for r in counts)*115),title='Tỷ lệ lớp thật thay đổi theo thời kỳ')
    save_figure(fig,args,'real_leakage','Cột dùng ngày giao thực tế đã chứa đáp án; pipeline không làm cột này hợp lệ · Rò rỉ khác dịch chuyển phân phối.')
    fig,axes=figure('Bài 7 · Nhãn phải được biết trước lúc huấn luyện')
    ax=axes[0,0];ax.set_ylim(-.5,1.5);ax.set_yticks([])
    ts=[example.order_approved_at,pd.Timestamp('2018-04-01'),example.order_estimated_delivery_date,example.order_delivered_customer_date]
    ax.plot([min(ts),max(ts)],[0,0],lw=3,c=COLORS[0])
    labels=['Duyệt đơn','Cutoff minh họa','Ngày hứa giao','Giao thực tế']
    for i,(t,label) in enumerate(zip(ts,labels)):
        ax.scatter([t],[0],s=120,c=COLORS[i%5],zorder=3)
        ax.annotate(label+'\n'+t.strftime('%d/%m/%Y'),(mdates.date2num(t),0),
                    xytext=([.12,.43,.65,.87][i],.72),textcoords='axes fraction',
                    ha='center',fontsize=15,arrowprops={'arrowstyle':'-'})
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'));ax.set_xlabel('Thời gian năm 2018')
    ax.margins(x=.12)
    save_figure(fig,args,'real_timeline','Đơn thật duyệt 09/03, giao 03/04 · Tại cutoff minh họa 01/04 chưa biết kết quả; cutoff này khác split chính của khóa học.')
    provenance=[{'column':c,'role':'candidate feature','availability':'assumed at approval; static snapshot cannot prove historical state'} for c in FEATURES]
    provenance.extend([{'column':c,'role':'future outcome / label construction','availability':'not available at approval'} for c in ['order_delivered_customer_date','delivery_days','late']])
    write_csv(args.output_dir/'column_provenance.csv',provenance)
    # Ba cửa sổ bổ sung chỉ trong giai đoạn train lịch sử; không đụng holdout test.
    pool=parts['train'].reset_index(drop=True);fold_rows=[];members=[]
    with threadpool_limits(limits=2):
        for fold,(cut,end) in enumerate([('2017-05-01','2017-07-01'),('2017-07-01','2017-09-01'),('2017-09-01','2017-11-01')],1):
            tr,va=asof_fold(pool,'2017-01-01',cut,end)
            pipe=pipeline().fit(pool.iloc[tr][FEATURES],pool.iloc[tr].late)
            p=pipe.predict_proba(pool.iloc[va][FEATURES])[:,1]
            fold_rows.append({'fold':fold,'cutoff':cut,'validation_end':end,'train_n':len(tr),'validation_n':len(va),
                              'train_last_label':pool.iloc[tr].order_delivered_customer_date.max().isoformat(),
                              'validation_AP':float(average_precision_score(pool.iloc[va].late,p))})
            for role,ids in [('train',tr),('validation',va)]:members.extend({'fold':fold,'order_id':pool.iloc[i].order_id,'role':role} for i in ids)
    write_csv(args.output_dir/'rolling_folds.csv',fold_rows);write_csv(args.output_dir/'rolling_membership.csv',members)
    return {'preparation':audit,'split_counts':counts,'INVALID_future_rule':bad,
            'approval_before_but_delivery_after_cutoff_raw':len(delayed),'shared_train_test_customers':len(shared),
            'rolling_evaluation_added_demo':fold_rows,'example':{c:str(example[c]) for c in ['order_id']+DATES},
            'scope':'Delivered-only and cutoff-filtered; metadata availability assumed; historical test previously seen.'}

def main():
    args=parser(7,'Rò rỉ, nhóm, thời gian và nested cross-validation').parse_args();setup(args);out={}
    if args.mode in ['toy','all']:out['toy']=toy(args)
    if args.mode in ['real','all']:out['real']=real(args)
    finish(args,7,out)

if __name__=='__main__':main()
