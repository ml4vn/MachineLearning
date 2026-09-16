"""Từ bốn điểm tính tay đến hồi quy thời gian giao hàng Olist."""
from pathlib import Path
import sys
if __package__ in (None,''): sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from threadpoolctl import threadpool_limits
from mlcourse.common import parser,setup,figure,save_figure,write_csv,write_json,finish,COLORS
from mlcourse.olist import prepare_olist,FEATURES
from lessons.bai04.algorithms import loss_gradient,gradient_descent

def toy(args):
    from mlcourse.teaching_visuals import gd_two_parameters
    gd_two_parameters(args)
    x=np.array([1.,2.,3.,4.]);y=np.array([3.,4.,6.,7.]);z=x-x.mean()
    # Giữ trung tâm y=5, nên biến đích của bài toán một tham số là y-5.
    theta,hist=gradient_descent(z[:,None],y-5,eta=args.toy_eta,steps=8)
    frame=pd.DataFrame(hist);write_csv(args.output_dir/'toy_gd.csv',frame)
    e=5-y
    write_csv(args.output_dir/'toy_first_gradient.csv',pd.DataFrame({'x':x,'z':z,'y':y,'prediction':5,'error':e,'z_times_error':z*e}))
    fig,axes=figure('Bài 4 · Một bước GD nhìn trong hai không gian',2)
    axes[0,0].scatter(x,y,s=130,c=COLORS[3],label='Quan sát mô phỏng')
    for t in [0,1,2]:
        w=hist[t]['theta_0'];axes[0,0].plot(x,5+w*z,'o-',label=f'Bước {t}: w = {w:.3f}',alpha=.8)
    axes[0,0].set(xlabel='Khoảng cách x (đơn vị 100 km)',ylabel='Thời gian (ngày)',title=r'$\hat y=5+w(x-2.5)$')
    axes[0,0].legend()
    ws=np.linspace(min(-.4,frame.theta_0.min()-.2),max(3.4,frame.theta_0.max()+.2),300)
    js=[loss_gradient(z[:,None],y-5,[w])[0] for w in ws]
    axes[0,1].plot(ws,js,label=r'$J(w)=\frac{1}{2n}\sum_i(\hat y_i-y_i)^2$')
    axes[0,1].plot(frame.theta_0,frame.loss,'o-',color=COLORS[3],label=f'GD: eta = {args.toy_eta:g}')
    axes[0,1].scatter([1.4],[.025],marker='*',s=200,c=COLORS[2],label='Nghiệm w = 1,4')
    axes[0,1].set(xlabel='w',ylabel='J (ngày²)',title='Đường đi trên hàm mất mát');axes[0,1].legend()
    save_figure(fig,args,'toy_gd','Ví dụ mô phỏng · Căn giữa x và giữ trung tâm y = 5 để luyện một tham số; chương trình thật học cả b và w.')
    rates=[]
    fig,axes=figure('Bài 4 · Learning rate thay đổi đường đi',2)
    for rate,color in zip([.1,.4,.8,1.2,1.6,1.8],COLORS+['#253348']):
        _,h=gradient_descent(z[:,None],y-5,eta=rate,steps=12)
        for row in h: rates.append({'eta':rate,**row})
        axes[0,0].plot([r['step'] for r in h],[r['theta_0'] for r in h],'.-',color=color,label=f'eta={rate}')
        axes[0,1].semilogy([r['step'] for r in h],[r['loss'] for r in h],'.-',color=color,label=f'eta={rate}')
    axes[0,0].axhline(1.4,ls='--',c='gray');axes[0,0].set(xlabel='Số bước',ylabel='w',title='Tham số')
    axes[0,1].set(xlabel='Số bước',ylabel='J (trục log)',title='Hàm mất mát');axes[0,1].legend(ncol=2)
    save_figure(fig,args,'toy_learning_rates','Chỉ với ví dụ này: 0 < eta < 1,6 hội tụ từ mọi khởi tạo; eta = 1,6 dao động nếu chưa ở nghiệm.')
    write_csv(args.output_dir/'toy_rates.csv',rates)
    A=np.column_stack([x,np.ones(4)]);old=np.array([.5,1.])
    j,g=loss_gradient(A,y,old);new=old-.05*g
    return {'one_parameter_history':hist,'optimum':{'w':1.4,'J':.025},
            'two_parameter':{'order':['w','b'],'before':old,'gradient':g,'after':new,'J_before':j,'J_after':loss_gradient(A,y,new)[0]}}

def scores(y,p):
    return {'mae_days':float(mean_absolute_error(y,p)),'rmse_days':float(root_mean_squared_error(y,p)), 'r2':float(r2_score(y,p))}

def real(args):
    d,audit=prepare_olist(args.data_dir)
    write_json(args.output_dir/'preparation_audit.json',audit)
    write_csv(args.output_dir/'prepared_orders.csv',d)
    tr=d[d.split=='train'];va=d[d.split=='validation'];te=d[d.split=='test']
    imp=SimpleImputer(strategy='median').fit(tr[['distance_km']])
    scaler=StandardScaler().fit(imp.transform(tr[['distance_km']]))
    xt=scaler.transform(imp.transform(tr[['distance_km']])).ravel()
    xe=scaler.transform(imp.transform(te[['distance_km']])).ravel()
    X=np.column_stack([np.ones(len(tr)),xt]);y=tr.delivery_days.to_numpy()
    with threadpool_limits(limits=2):
        theta,hist=gradient_descent(X,y,eta=args.real_eta,steps=args.steps)
        ols=LinearRegression().fit(xt[:,None],y)
    delta=float(np.max(np.abs(theta-np.array([ols.intercept_,ols.coef_[0]]))))
    write_csv(args.output_dir/'real_gd_history.csv',hist)
    pred_gd=theta[0]+theta[1]*xe
    pred_ols=ols.predict(xe[:,None])
    rows=[]
    models={'mean_train':(['distance_km'],None),'median_train':(['distance_km'],None),
            'distance':(['distance_km'],LinearRegression()),'promise':(['promised_days'],LinearRegression()),
            'six_features':(FEATURES,LinearRegression())}
    prediction_table=te[['order_id','distance_km','delivery_days']].copy()
    for name,(cols,model) in models.items():
        prep=SimpleImputer(strategy='median').fit(tr[cols])
        if model is not None:
            with threadpool_limits(limits=2): model.fit(prep.transform(tr[cols]),y)
        for split,part in [('validation',va),('test',te)]:
            pred=(model.predict(prep.transform(part[cols])) if model is not None else
                  np.full(len(part),np.median(y) if name=='median_train' else y.mean()))
            rows.append({'model':name,'split':split,**scores(part.delivery_days,pred)})
            if split=='test': prediction_table[name]=pred
    rows.append({'model':f'GD_{args.steps}_steps','split':'test',**scores(te.delivery_days,pred_gd)})
    if not np.allclose(pred_ols,prediction_table.distance,atol=1e-10): raise AssertionError('OLS không khớp sau đổi thang')
    prediction_table['GD']=pred_gd
    prediction_table['error_prediction_minus_actual']=pred_ols-te.delivery_days.to_numpy()
    prediction_table['residual_actual_minus_prediction']=te.delivery_days.to_numpy()-pred_ols
    write_csv(args.output_dir/'test_predictions.csv',prediction_table);write_csv(args.output_dir/'model_metrics.csv',rows)
    raw_w=float(ols.coef_[0]/scaler.scale_[0]);raw_b=float(ols.intercept_-ols.coef_[0]*scaler.mean_[0]/scaler.scale_[0])
    example=tr[tr.distance_km.notna()].copy()
    selected=[example.iloc[np.abs(example.distance_km-km).argmin()] for km in [100,400,800,1400]]
    example=pd.DataFrame(selected)[['order_id','distance_km','delivery_days','promised_days']]
    write_csv(args.output_dir/'real_order_examples.csv',example)
    fig,axes=figure('Bài 4 · Khoảng cách có ích nhưng chưa giải thích hết',2)
    sample=tr.sample(min(4000,len(tr)),random_state=args.seed)
    axes[0,0].scatter(sample.distance_km,sample.delivery_days,s=9,alpha=.2,label='Tối đa 4.000 đơn train')
    xx=np.linspace(0,float(tr.distance_km.max()),200)
    axes[0,0].plot(xx,raw_b+raw_w*xx,c=COLORS[3],lw=2,label='OLS trên toàn train')
    axes[0,0].set(xlabel='Khoảng cách đường chim bay (km)',ylabel='Thời gian giao thành công (ngày)',title='Dữ liệu thật và mô hình');axes[0,0].legend()
    residual=prediction_table.error_prediction_minus_actual
    axes[0,1].hist(residual,bins=70,color=COLORS[0],alpha=.85)
    axes[0,1].axvline(0,ls='--',c=COLORS[3]);axes[0,1].set(xlabel='Dự đoán − thực tế (ngày)',ylabel='Số đơn',title='Sai số e trên toàn bộ test')
    save_figure(fig,args,'real_regression','Dữ liệu Olist lịch sử · e dương: mô hình dự đoán thời gian dài hơn thực tế · Không phải khoảng cam kết.')
    fig,axes=figure('Bài 4 · Đường hội tụ và mốc so sánh',2)
    axes[0,0].plot([r['step'] for r in hist],[r['loss'] for r in hist])
    optimum=np.mean((ols.predict(xt[:,None])-y)**2)/2
    axes[0,0].axhline(optimum,c=COLORS[3],ls='--',label=f'OLS J = {optimum:.3f}')
    axes[0,0].set(xlabel='Số bước GD',ylabel='J train (ngày²)',title=f'GD trên x chuẩn hóa · eta = {args.real_eta:g}');axes[0,0].legend()
    table=pd.DataFrame(rows);testrows=table[(table.split=='test')&table.model.isin(['mean_train','distance','six_features'])]
    q=np.arange(len(testrows));axes[0,1].bar(q-.18,testrows.mae_days,.36,label='MAE');axes[0,1].bar(q+.18,testrows.rmse_days,.36,label='RMSE')
    axes[0,1].set(xticks=q,xticklabels=['Trung bình train','Khoảng cách','Sáu đặc trưng'],ylabel='Ngày',title='Sai số trên cùng test');axes[0,1].legend()
    save_figure(fig,args,'real_metrics','GD và OLS cùng tối ưu bình phương sai số · Thêm đặc trưng chỉ cải thiện vừa phải trong phép thử lịch sử này.')
    return {'preparation':audit,'metrics':rows,'gd_ols_parameter_max_gap':delta,
            'gd_matches_ols_at_1e_minus3':bool(delta<.001),'ols_raw_units':{'intercept_days':raw_b,'slope_days_per_km':raw_w},
            'distance_query_km':args.distance,'prediction_days':raw_b+raw_w*args.distance,
            'scaler_mean_km':float(scaler.mean_[0]),'scaler_std_km':float(scaler.scale_[0]),
            'median_imputation_km':float(imp.statistics_[0]),'scope':'Delivered-only, static metadata, historical holdout.'}

def main():
    p=parser(4,'Hồi quy thời gian giao hàng và Gradient Descent')
    p.add_argument('--toy-eta',type=float,default=.4)
    p.add_argument('--real-eta',type=float,default=.1)
    p.add_argument('--steps',type=int,default=100)
    p.add_argument('--distance',type=float,default=600,help='Khoảng cách km cần dự đoán')
    args=p.parse_args()
    if not np.isfinite(args.distance) or args.distance<0: p.error('--distance phải hữu hạn và không âm')
    if not 0<args.toy_eta<=2 or not 0<args.real_eta<=2: p.error('learning rate minh họa cần trong (0,2]')
    setup(args);out={}
    if args.mode in ['toy','all']: out['toy']=toy(args)
    if args.mode in ['real','all']: out['real']=real(args)
    finish(args,4,out)

if __name__=='__main__': main()
