"""Logistic: mô hình xác suất, BCE và chính sách cảnh báo giao trễ."""
from pathlib import Path
import sys
if __package__ in (None,''): sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from mlcourse.common import parser,setup,figure,save_figure,write_csv,write_json,finish,COLORS
from mlcourse.olist import prepare_olist,FEATURES
from mlcourse.classification import fit_logistic,transform,evaluate,select_threshold,plot_confusion
from examples.bai05.algorithms import sigmoid,logistic_loss_gradient,logistic_gd

def toy(args):
    x=np.array([-1.,0.,1.,2.]);y=np.array([0,0,1,1]);X=np.column_stack([np.ones(4),x])
    theta,hist=logistic_gd(X,y,args.eta,20)
    write_csv(args.output_dir/'toy_history.csv',hist)
    steps=[]
    for step in [0,1,5,20]:
        th=np.array([hist[step]['theta_0'],hist[step]['theta_1']]);p=sigmoid(X@th)
        for i in range(4): steps.append({'step':step,'id':chr(65+i),'x':x[i],'y':y[i],'logit':float(X[i]@th),'p':float(p[i]),'prediction':int(p[i]>=.5)})
    write_csv(args.output_dir/'toy_predictions.csv',steps)
    fig,axes=figure('Bài 5 · Quan sát một mô hình xác suất học dần',2)
    xx=np.linspace(-3,4,200)
    for step in [0,1,5,20]:
        b,w=hist[step]['theta_0'],hist[step]['theta_1']
        axes[0,0].plot(xx,sigmoid(b+w*xx),label=f'Bước {step}')
    axes[0,0].scatter(x,y,s=130,c=COLORS[3],zorder=6,label='Nhãn mô phỏng')
    axes[0,0].axhline(.5,c='gray',ls='--');axes[0,0].set(xlabel='Đặc trưng x mô phỏng',ylabel='Xác suất mô hình',title=r'$p=\sigma(b+wx)$');axes[0,0].legend(loc='upper left')
    axes[0,1].plot([r['step'] for r in hist],[r['loss'] for r in hist],'o-')
    axes[0,1].set(xlabel='Số bước',ylabel='BCE trung bình',title=f'GD không phạt · eta = {args.eta:g}')
    save_figure(fig,args,'toy_learning','Bốn điểm phân tách hoàn toàn · Chỉ minh họa 20 bước; không tuyên bố MLE không phạt có nghiệm hữu hạn.')
    fig,axes=figure('Bài 5 · Điểm, xác suất và cách chấm lỗi',2)
    z=np.linspace(-7,7,300);pp=np.linspace(.005,.995,300)
    axes[0,0].plot(z,sigmoid(z));axes[0,0].scatter([0],[.5],s=100,c=COLORS[3])
    axes[0,0].set(xlabel='Logit z',ylabel='p',title=r'$\sigma(z)=1/(1+e^{-z})$')
    axes[0,1].plot(pp,-np.log(pp),label=r'Nhãn y=1: $-\log p$')
    axes[0,1].plot(pp,-np.log1p(-pp),label=r'Nhãn y=0: $-\log(1-p)$')
    axes[0,1].set(xlabel='Xác suất dự đoán p',ylabel='BCE một mẫu',title='Tự tin sai chịu phạt lớn');axes[0,1].legend()
    save_figure(fig,args,'toy_sigmoid_bce','Sigmoid là hàm dự đoán; BCE là hàm mất mát; GD là thuật toán học; ngưỡng là chính sách quyết định.')
    # 19 quan sát: bốn nhóm x, mỗi nhóm đúng một mẫu dương.
    gx=np.arange(1.,5.);n=np.array([9,5,3,2]);th=np.array([-np.log(16),np.log(2)])
    G=np.column_stack([np.ones(4),gx]);gp=sigmoid(G@th)
    score=G.T@(n*gp-1);H=G.T@np.diag(n*gp*(1-gp))@G
    rx=np.repeat(gx,n);ry=np.concatenate([np.r_[1,np.zeros(k-1)] for k in n])
    with threadpool_limits(limits=2):
        m=LogisticRegression(penalty=None,solver='newton-cg',tol=1e-10,max_iter=1000).fit(rx[:,None],ry)
    if not np.allclose([m.intercept_[0],m.coef_[0,0]],th,atol=1e-6): raise AssertionError('Nghiệm gộp không khớp')
    write_csv(args.output_dir/'toy_grouped19.csv',pd.DataFrame({'x':gx,'n':n,'positives':1,'empirical_rate':1/n,'model_p':gp}))
    return {'history':hist,'first_step_probabilities':sigmoid(X@np.array([hist[1]['theta_0'],hist[1]['theta_1']])),
            'grouped19':{'b':th[0],'w':th[1],'score_equation':score,'hessian_min_eigenvalue':float(np.linalg.eigvalsh(H).min()),'sklearn_matches':True}}

def real(args):
    d,audit=prepare_olist(args.data_dir);tr=d[d.split=='train'];va=d[d.split=='validation'];te=d[d.split=='test']
    write_json(args.output_dir/'preparation_audit.json',audit);write_csv(args.output_dir/'prepared_orders.csv',d)
    imp,sc,model=fit_logistic(tr,args.C)
    pv=model.predict_proba(transform(va,imp,sc))[:,1]
    scan,chosen=select_threshold(va.late,pv);t=chosen['threshold']
    write_json(args.output_dir/'model_policy.json',{'model':'logistic newton-cg, L2','C':args.C,'features':FEATURES,
               'selection_split':'validation','threshold':t,'cost':'FP + 5FN, hypothetical','tie_rule':'fewer alerts then larger threshold'})
    p=model.predict_proba(transform(te,imp,sc))[:,1]
    z=model.intercept_[0]+transform(te,imp,sc)@model.coef_[0]
    if not np.allclose(sigmoid(z),p,atol=1e-12): raise AssertionError('Sigmoid không khớp')
    default=evaluate(te.late,p,.5);selected=evaluate(te.late,p,t)
    bce=float(np.mean(np.logaddexp(0,(1-2*te.late.to_numpy())*z)))
    if not np.isclose(bce,selected['log_loss']): raise AssertionError('BCE không khớp sklearn')
    baseline=evaluate(te.late,np.full(len(te),tr.late.mean()),.5)
    raw_w=model.coef_[0]/sc.scale_;raw_b=float(model.intercept_[0]-raw_w@sc.mean_)
    if not np.allclose(sigmoid(raw_b+imp.transform(te[FEATURES])@raw_w),p): raise AssertionError('Đổi đơn vị sai')
    for name,part,score in [('validation',va,pv),('test',te,p)]:
        rows=part[['order_id','late']+FEATURES].copy();rows['score']=score;rows['prediction_05']=(score>=.5).astype(int);rows['prediction_selected']=(score>=t).astype(int)
        write_csv(args.output_dir/f'{name}_predictions.csv',rows)
    write_csv(args.output_dir/'validation_thresholds.csv',scan)
    write_csv(args.output_dir/'coefficients.csv',pd.DataFrame({'feature':FEATURES,'median_train':imp.statistics_,'mean_train':sc.mean_,'std_train':sc.scale_,'coef_standardized':model.coef_[0],'coef_raw':raw_w}))
    fig,axes=figure('Bài 5 · Cùng điểm số, hai chính sách quyết định',2)
    plot_confusion(axes[0,0],default,'Ngưỡng 0,50')
    plot_confusion(axes[0,1],selected,f'Ngưỡng validation chọn: {t:.2f}')
    save_figure(fig,args,'real_confusion','Test Olist · Giảm bỏ lọt phải đi cùng việc đọc số cảnh báo sai · Không chọn ngưỡng bằng test.')
    fig,axes=figure('Bài 5 · Vì sao đổi ngưỡng chỉ giúp được một phần?',2)
    for label,name,color in [(0,'Đúng hạn',COLORS[0]),(1,'Trễ',COLORS[3])]:
        axes[0,0].hist(p[te.late.to_numpy()==label],bins=np.linspace(0,1,81),density=True,alpha=.5,label=name,color=color)
    axes[0,0].axvline(t,ls='--',c=COLORS[2]);axes[0,0].set(xlabel='Xác suất mô hình',ylabel='Mật độ mỗi lớp',title='Phân bố điểm trên toàn test');axes[0,0].legend()
    costs=[baseline['cost'],default['cost'],selected['cost']]
    axes[0,1].bar(['Luôn đúng hạn','Logistic 0,50',f'Logistic {t:.2f}'],costs,color=[COLORS[4],COLORS[0],COLORS[2]])
    for i,v in enumerate(costs): axes[0,1].text(i,v+max(costs)*.012,f'{v:,}',ha='center',fontsize=17)
    axes[0,1].set(ylabel='Chi phí giả định FP + 5FN',ylim=(0,max(costs)*1.15),title='So cùng một hàm chi phí')
    save_figure(fig,args,'real_scores_cost','Histogram chuẩn hóa riêng từng lớp để so hình dạng · Cải thiện chi phí không chứng minh tác động kinh doanh.')
    available=tr.dropna(subset=['distance_km']);i=(available.distance_km-100).abs().idxmin();row=available.loc[[i]]
    original=imp.transform(row[FEATURES])[0];scaled=transform(row,imp,sc)[0];terms=scaled*model.coef_[0]
    logit=float(model.intercept_[0]+terms.sum());prob=float(sigmoid(logit))
    table=pd.DataFrame({'feature':FEATURES,'value_after_imputation':original,'standardized':scaled,'coefficient':model.coef_[0],'contribution_to_logit':terms})
    write_csv(args.output_dir/'one_order_calculation.csv',table)
    fig,axes=figure('Bài 5 · Theo một đơn thật qua phép tính',2)
    fig.subplots_adjust(left=.13)
    labels=['Khoảng cách','Hứa giao','Giá','Cước','Số món','Cân nặng','Hệ số chặn']
    values=np.r_[terms,model.intercept_[0]]
    axes[0,0].barh(labels,values,color=[COLORS[2] if v>=0 else COLORS[3] for v in values]);axes[0,0].axvline(0,c='gray')
    axes[0,0].set(xlabel='Đóng góp vào logit',title='Nhân từng hệ số với đặc trưng chuẩn hóa')
    axes[0,1].axis('off')
    axes[0,1].text(0,.85,f'ID: {row.order_id.iloc[0]}\n\nKhoảng cách: {float(row.distance_km.iloc[0]):.2f} km\n\nTổng logit z = {logit:.6f}\n\nSigmoid(z) = {prob:.6f}\n\nNgưỡng {t:.2f} → '+('cảnh báo trễ' if prob>=t else 'không cảnh báo'),fontsize=17,va='top',transform=axes[0,1].transAxes)
    save_figure(fig,args,'real_one_order','Chọn đơn train gần 100 km, không chọn theo nhãn · Đóng góp logit không phải tác động nhân quả của đặc trưng.')
    return {'preparation':audit,'C':args.C,'iterations':model.n_iter_,'validation_scan':scan,'selected_threshold':t,
            'test_default':default,'test_selected':selected,'baseline':baseline,'bce_from_logits':bce,
            'coef_standardized':model.coef_[0],'intercept_standardized':model.intercept_[0],
            'coef_raw':raw_w,'intercept_raw':raw_b,'example':{'order_id':row.order_id.iloc[0],'logit':logit,'p':prob},
            'cost_reduction_vs_baseline':baseline['cost']-selected['cost'],'test_scope':'Historical course holdout; not a new independent study.'}

def main():
    p=parser(5,'Logistic Regression và nguy cơ giao trễ Olist')
    p.add_argument('--eta',type=float,default=1.,help='Learning rate GD trong ví dụ nhỏ')
    p.add_argument('--C',type=float,default=1.,help='Nghịch đảo độ mạnh phạt L2 của mô hình thật')
    args=p.parse_args()
    if not np.isfinite(args.eta) or not 0<args.eta<=10: p.error('--eta cần trong (0,10]')
    if not np.isfinite(args.C) or args.C<=0: p.error('--C phải dương và hữu hạn')
    setup(args);out={}
    if args.mode in ['toy','all']: out['toy']=toy(args)
    if args.mode in ['real','all']: out['real']=real(args)
    finish(args,5,out)

if __name__=='__main__': main()
