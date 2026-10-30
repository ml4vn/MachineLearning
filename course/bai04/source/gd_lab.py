"""Complete batch GD lab for Bài 4. All analytical figures share these values.

Usage: python source/gd_lab.py [--rebuild-data]
No network is needed once requirements are installed. Train-only median and
population standard deviation are reused unchanged for validation/test.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'.build/pydeps').exists():sys.path.insert(0,str(ROOT/'.build/pydeps'))
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def batch_gd(x,y,eta=.1,steps=100,w0=0.,b0=0.):
    """One feature, free intercept; all gradients use the same old residual."""
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if x.ndim!=1 or y.shape!=x.shape or not len(x):raise ValueError('x,y must be nonempty equal-length vectors')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):raise ValueError('Input must be finite')
    if eta<=0 or steps<0:raise ValueError('eta>0, steps>=0')
    w,b=float(w0),float(b0);history=[]
    for t in range(steps+1):
        pred=b+w*x;error=pred-y
        gw=float(np.mean(x*error));gb=float(np.mean(error));J=float(np.mean(error**2)/2)
        if not np.isfinite([w,b,gw,gb,J]).all():raise FloatingPointError('Nonfinite state; inspect eta and scale')
        history.append(dict(t=t,w=w,b=b,g_w=gw,g_b=gb,J=J))
        if t<steps:w,b=w-eta*gw,b-eta*gb
    return w,b,history

def toy_one_parameter(eta=.4,steps=8):
    x=np.array([1.,2.,3.,4.]);y=np.array([3.,4.,6.,7.]);z=x-x.mean();a=y.mean();w=0.;history=[]
    for t in range(steps+1):
        pred=a+w*z;e=pred-y;g=float(np.mean(z*e));J=float(np.mean(e**2)/2)
        history.append(dict(t=t,w=w,a=float(a),b_raw=float(a-w*x.mean()),predictions=pred.tolist(),residuals=e.tolist(),contributions=(z*e).tolist(),g=g,J=J))
        if t<steps:w-=eta*g
    return history

def metrics(y,pred):
    e=np.asarray(pred)-np.asarray(y)
    return dict(MAE_days=float(np.abs(e).mean()),RMSE_days=float(np.sqrt(np.mean(e**2))))

def run(rebuild=False):
    if rebuild:
        from prepare_olist import prepare
        prepare()
    checks=[]
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail))
        if not bool(ok):raise AssertionError((name,detail))
    h=toy_one_parameter()
    check('1Dstep1',np.allclose([h[1]['w'],h[1]['J']],[.7,.33125]))
    check('1Dstep2',np.allclose([h[2]['w'],h[2]['g'],h[2]['J']],[1.05,-.4375,.1015625]))
    x=np.arange(1.,5.);y=np.array([3.,4.,6.,7.]);z=x-2.5
    loss=lambda w:float(np.mean((5+w*z-y)**2)/2)
    grad=lambda w:float(np.mean(z*(5+w*z-y)))
    for w in [-1.,0.,.7,1.4,2.2]:
        fd=(loss(w+1e-5)-loss(w-1e-5))/2e-5
        check('finite_difference_1D_'+str(w),abs(fd-grad(w))<1e-7)
    check('minimum_positive_loss',abs(grad(1.4))<1e-12 and abs(loss(1.4)-.025)<1e-12)
    rates={str(eta):toy_one_parameter(eta,8) for eta in [.1,.4,.8,1.2,1.6,1.8]}
    check('overshoot_converges',rates['1.2'][1]['w']>1.4 and rates['1.2'][1]['J']<loss(0) and abs(rates['1.2'][-1]['w']-1.4)<.01)
    check('boundary_not_convergent',np.isclose(abs(rates['1.6'][-1]['w']-1.4),1.4))
    check('large_rate_diverges',rates['1.8'][1]['J']>loss(0) and abs(rates['1.8'][-1]['w']-1.4)>1.4)
    w2,b2,h2=batch_gd(x,y,.05,1,.5,1.)
    check('2D_shared_old_gradient',np.allclose([h2[0]['g_w'],h2[0]['g_b']],[-8,-2.75]))
    check('2Dsimultaneous',np.allclose([w2,b2,h2[0]['J'],h2[1]['J']],[.9,1.1375,4.3125,1.481328125]))
    def J2(theta):return float(np.mean((theta[1]+theta[0]*x-y)**2)/2)
    for theta in [[.5,1],[.9,1.1375],[1.4,1.5]]:
        theta=np.array(theta);e=theta[1]+theta[0]*x-y;g=np.array([np.mean(x*e),np.mean(e)])
        fd=np.array([(J2(theta+np.eye(2)[i]*1e-5)-J2(theta-np.eye(2)[i]*1e-5))/2e-5 for i in range(2)])
        check('finite_difference_2D_'+str(theta.tolist()),np.allclose(g,fd,atol=1e-7))
    H=np.column_stack([x,np.ones(4)]).T@np.column_stack([x,np.ones(4)])/4
    eigenvalues,eigenvectors=np.linalg.eigh(H)
    check('convex_unique_toy',np.min(eigenvalues)>0 and np.allclose(np.linalg.lstsq(np.column_stack([x,np.ones(4)]),y,rcond=None)[0],[1.4,1.5]))
    s=x.std(ddof=0);mu=x.mean();u=(x-mu)/s
    check('scaling_equivalent_toy',np.allclose(1+.5*x,2.25+(.5*s)*u))
    d=pd.read_csv(ROOT/'data/prepared/olist_model_table.csv')
    check('unique_order',d.order_id.is_unique)
    for k in ['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']:d[k]=pd.to_datetime(d[k])
    check('target_from_timestamps',np.allclose(d.delivery_days,(d.order_delivered_customer_date-d.order_approved_at).dt.total_seconds()/86400))
    check('label_calendar_day',np.array_equal(d.late,(d.order_delivered_customer_date.dt.normalize()>d.order_estimated_delivery_date.dt.normalize()).astype(int)))
    sets={k:d[d.split==k].copy() for k in ['train','validation','test']}
    check('split_counts',[len(sets[k]) for k in sets]==[29031,10389,40266])
    for k,begin,end,cutoff in [('train','2017-01-01','2017-11-01','2017-11-01'),('validation','2017-11-01','2018-01-01','2018-01-01'),('test','2018-01-01','2018-07-01',None)]:
        q=sets[k];check(k+'_window',q.order_approved_at.ge(begin).all() and q.order_approved_at.lt(end).all())
        if cutoff:check(k+'_labels_available',q.order_delivered_customer_date.lt(cutoff).all())
    train=sets['train'];median=float(train.distance_km.median())
    X=train.distance_km.fillna(median).to_numpy();Y=train.delivery_days.to_numpy()
    mu=float(X.mean());s=float(X.std(ddof=0));U=(X-mu)/s
    check('train_scaler',abs(U.mean())<1e-12 and abs(U.std(ddof=0)-1)<1e-12)
    w,b,real_history=batch_gd(U,Y,.1,100)
    ols=LinearRegression().fit(U[:,None],Y)
    check('GDnearOLS',abs(w-ols.coef_[0])<.001 and abs(b-ols.intercept_)<.001)
    raw_w=w/s;raw_b=b-w*mu/s
    predictions={};result={}
    for k in ['validation','test']:
        q=sets[k];xx=q.distance_km.fillna(median).to_numpy();yy=q.delivery_days.to_numpy()
        pred=raw_b+raw_w*xx;baseline=np.full(len(q),Y.mean());ols_pred=ols.predict(((xx-mu)/s)[:,None])
        check(k+'_coordinate_equivalence',np.allclose(pred,b+w*(xx-mu)/s))
        result[k]=dict(GD=metrics(yy,pred),baseline=metrics(yy,baseline),OLS=metrics(yy,ols_pred))
        q['prediction_GD']=pred;q['prediction_baseline']=baseline;q['residual_GD']=pred-yy
        q[['order_id','split','distance_km','delivery_days','prediction_GD','prediction_baseline','residual_GD']].to_csv(ROOT/f'data/{k}_predictions.csv',index=False)
        predictions[k]=(yy,pred)
    ref=json.loads((ROOT/'results/olist_pilot.json').read_text(encoding='utf8'))
    for k in ['validation','test']:
        for model,name in [('baseline','constant'),('OLS','distance')]:
            old=next(v for v in ref['regression'] if v['name']==name)[k]
            check(k+'_'+name+'_reproduced',np.allclose([result[k][model]['MAE_days'],result[k][model]['RMSE_days']],[old['mae'],old['rmse']],atol=1e-9))
    check('GDtest_expected',np.allclose(list(result['test']['GD'].values()),[5.9396250620880835,9.351597901427297],atol=1e-9))
    test_y,test_pred=predictions['test'];errors=test_pred-test_y
    counts,edges=np.histogram(errors.clip(-40,40),bins=np.linspace(-40,40,21))
    check('histogram_preserves_count',counts.sum()==len(test_y))
    inside=train.distance_km.between(0,3000)&train.delivery_days.between(0,45)
    # Native evidence chart: regular count bins, exact count per rectangle.
    density,xe,ye=np.histogram2d(train.loc[inside,'distance_km'],train.loc[inside,'delivery_days'],bins=[np.linspace(0,3000,31),np.linspace(0,45,19)])
    check('density_count',int(density.sum())==int(inside.sum()))
    examples=pd.read_csv(ROOT/'data/prepared/olist_four_real_orders.csv')
    check('four_ids_from_train',examples.order_id.isin(train.order_id).all())
    examples['prediction_GD']=raw_b+raw_w*examples.distance_km
    example_rows=examples.merge(train[['order_id','order_approved_at','order_delivered_customer_date']],on='order_id',validate='one_to_one')
    report=dict(status='pass',checks_count=len(checks),checks=checks,toy=dict(x=x.tolist(),y=y.tolist(),z=z.tolist(),history=h,rates=rates,optimum_w=1.4,optimum_J=.025),
        two_parameter=dict(order=['w','b'],history=h2,Hessian=H.tolist(),eigenvalues=eigenvalues.tolist(),eigenvectors=eigenvectors.tolist()),
        real=dict(split_counts={k:len(v) for k,v in sets.items()},median_distance_train=median,mean_train=mu,std_train_ddof0=s,eta=.1,steps=100,
                  b_raw=raw_b,w_raw=raw_w,b_standardized=b,w_standardized=w,b_ols_raw=float(ols.intercept_-ols.coef_[0]*mu/s),w_ols_raw=float(ols.coef_[0]/s),
                  history=real_history,metrics=result,four_orders=json.loads(example_rows.to_json(orient='records',date_format='iso')),
                  density=dict(counts=density.astype(int).tolist(),xedges=xe.tolist(),yedges=ye.tolist(),in_window=int(inside.sum()),train_total=len(train)),
                  histogram=dict(counts=counts.tolist(),edges=edges.tolist(),clipped=int((np.abs(errors)>40).sum()),total=len(errors)),
                  absolute_error_quantiles={str(q):float(np.quantile(np.abs(errors),q)) for q in [.1,.5,.9,.95]}),
        limitations=['Completed-order historical cohort; selection and cutoff effects.','Static geographical data assumed available; feature history not proven.','Test previously inspected;  reproduces a fixed teaching configuration.'])
    (ROOT/'results/case_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    pd.DataFrame(h).drop(columns=['predictions','residuals','contributions']).to_csv(ROOT/'data/toy_GD_history.csv',index=False)
    pd.DataFrame(real_history).to_csv(ROOT/'data/real_GD_history.csv',index=False)
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rebuild-data',action='store_true');args=ap.parse_args()
    r=run(args.rebuild_data)
    print(json.dumps(dict(status=r['status'],checks=r['checks_count'],metrics=r['real']['metrics'],parameters=[r['real']['w_raw'],r['real']['b_raw']]),ensure_ascii=False,indent=2))
