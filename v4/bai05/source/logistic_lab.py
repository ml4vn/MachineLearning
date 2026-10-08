"""Bài5v4: stable logistic GD toy and reproducible Olist policy, train-only preprocessing."""
from pathlib import Path
import sys,json,warnings
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix,average_precision_score,roc_auc_score,log_loss,brier_score_loss
from threadpoolctl import threadpool_limits
FEATURES=['distance_km','promised_days','price','freight_value','n_items','weight_g']
DATES=['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']
GRID=[.02,.03,.05,.10,.15,.20,.30,.50,.80]

def loss(theta,x,y,lam=0):
    w,b=theta;z=b+w*x
    return float(np.mean(np.logaddexp(0,z)-y*z)+lam*w*w/2)
def gradient(theta,x,y,lam=0):
    w,b=theta;e=expit(b+w*x)-y
    return np.array([np.mean(x*e)+lam*w,np.mean(e)])
def gradient_descent(x,y,eta=1,steps=20,lam=0,theta=(0,0)):
    th=np.array(theta,dtype=float);out=[]
    for t in range(steps+1):
        z=th[1]+th[0]*x;p=expit(z);g=gradient(th,x,y,lam)
        out.append(dict(step=t,w=float(th[0]),b=float(th[1]),logits=z.tolist(),probabilities=p.tolist(),residuals=(p-y).tolist(),contributions=(x*(p-y)).tolist(),gradient=g.tolist(),loss=loss(th,x,y,lam),sample_losses=(np.logaddexp(0,z)-y*z).tolist()))
        th=th-eta*g
    return out
def measure(y,p,t=None):
    pred=np.zeros(len(y),dtype=bool) if t is None else p>=t
    tn,fp,fn,tp=map(int,confusion_matrix(y,pred,labels=[0,1]).ravel())
    precision=tp/(tp+fp) if tp+fp else 0.0 # reporting convention; denominator zero means mathematically undefined.
    recall=tp/(tp+fn)
    return dict(n=len(y),tn=tn,fp=fp,fn=fn,tp=tp,accuracy=(tn+tp)/len(y),precision=precision,precision_defined=bool(tp+fp),recall=recall,f1=2*tp/(2*tp+fp+fn),alerts=tp+fp,cost=fp+5*fn,log_loss=float(log_loss(y,p)),brier=float(brier_score_loss(y,p)),ap=float(average_precision_score(y,p)),auc=float(roc_auc_score(y,p)))

def run():
    checks={}
    def ck(name,v):checks[name]=bool(v);assert v,name
    d=pd.read_csv(R/'data/prepared/olist_model_table.csv',parse_dates=DATES)
    ck('unique_order',d.order_id.is_unique);ck('split_counts',d.split.value_counts().to_dict()=={'test':40266,'train':29031,'validation':10389})
    ck('label_from_calendar',np.array_equal(d.late,(d[DATES[1]].dt.normalize()>d[DATES[2]].dt.normalize()).astype(int)))
    parts={k:d[d.split==k].copy() for k in ['train','validation','test']}
    for k,lo,hi in [('train','2017-01-01','2017-11-01'),('validation','2017-11-01','2018-01-01'),('test','2018-01-01','2018-07-01')]:
        a=parts[k];ck(k+'_time_window',a[DATES[0]].ge(lo).all() and a[DATES[0]].lt(hi).all())
        if k!='test':ck(k+'_label_cutoff',a[DATES[1]].lt(hi).all())
    tr=parts['train'];imp=SimpleImputer(strategy='median').fit(tr[FEATURES]);Xraw=imp.transform(tr[FEATURES]);sc=StandardScaler().fit(Xraw);X=sc.transform(Xraw);y=tr.late.to_numpy()
    ck('train_median',np.allclose(imp.statistics_,tr[FEATURES].median()));ck('train_standardized',np.allclose(X.mean(0),0,atol=1e-12) and np.allclose(X.std(0),1,atol=1e-12))
    model=LogisticRegression(solver='newton-cg',C=1,penalty='l2',max_iter=100,tol=1e-6)
    with threadpool_limits(limits=2),warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always');model.fit(X,y)
    ck('no_solver_warning',not captured)
    scores={};Z={}
    for k,a in parts.items():
        xx=sc.transform(imp.transform(a[FEATURES]));z=model.intercept_[0]+xx@model.coef_[0];p=model.predict_proba(xx)[:,1];Z[k]=z;scores[k]=p
        ck(k+'_sigmoid_manual',np.allclose(p,expit(z),rtol=1e-12))
        a['score']=p;a['prediction_05']=(p>=.5).astype(int)
    scan=[dict(policy='threshold',threshold=t,**measure(parts['validation'].late,scores['validation'],t)) for t in GRID]
    scan.append(dict(policy='no_alerts',threshold=None,**measure(parts['validation'].late,scores['validation'],None)))
    best=min(scan,key=lambda a:(a['cost'],a['alerts'],-(a['threshold'] if a['threshold'] is not None else float('inf'))))
    selected=best['threshold'];q=float(y.mean());testy=parts['test'].late.to_numpy()
    default=measure(testy,scores['test'],.5);chosen=measure(testy,scores['test'],selected);base=measure(testy,np.full(len(testy),q),None)
    ck('stable_BCE_matches',np.isclose(np.mean(np.logaddexp(0,Z['test'])-testy*Z['test']),default['log_loss']))
    lam=1/len(tr);e=expit(model.intercept_[0]+X@model.coef_[0])-y;g=np.r_[X.T@e/len(tr)+lam*model.coef_[0],e.mean()]
    ck('penalty_scaling_stationarity',np.linalg.norm(g)<3e-6)
    coeffraw=model.coef_[0]/sc.scale_;interceptraw=model.intercept_[0]-coeffraw@sc.mean_
    ck('raw_unit_equivalence',np.allclose(expit(interceptraw+imp.transform(parts['test'][FEATURES])@coeffraw),scores['test']))
    toyx=np.array([-1.,0.,1.,2.]);toyy=np.array([0.,0.,1.,1.]);hist=gradient_descent(toyx,toyy)
    ck('toy_gradient',np.array_equal(hist[0]['gradient'],[-.5,0.]));ck('toy_step1',hist[1]['w']==.5 and hist[1]['b']==0)
    ck('toy_step2',np.allclose([hist[2]['w'],hist[2]['b']],[.8232410450840703,-.057764644657501224]))
    ck('toy_loss_decreases',all(a['loss']>=b['loss'] for a,b in zip(hist,hist[1:])))
    for i,th in enumerate([(0,0),(.5,0),(.7,-.2)]):
        for l in [0,.1]:
            th=np.array(th);fd=np.array([(loss(th+np.eye(2)[j]*1e-5,toyx,toyy,l)-loss(th-np.eye(2)[j]*1e-5,toyx,toyy,l))/2e-5 for j in range(2)])
            ck(f'finite_difference_{i}_{l}',np.allclose(fd,gradient(th,toyx,toyy,l),atol=1e-9))
    opt=minimize(lambda th:loss(th,toyx,toyy,.1),[0.,0.],jac=lambda th:gradient(th,toyx,toyy,.1),method='BFGS',options={'gtol':1e-10})
    ck('L2_stationary',np.linalg.norm(gradient(opt.x,toyx,toyy,.1))<1e-8)
    ray=[dict(k=k,w=2*k,b=-k,loss=loss((2*k,-k),toyx,toyy)) for k in [1,2,4,8,16]]
    ck('separating_ray',all(a['loss']>b['loss'] for a,b in zip(ray,ray[1:])))
    ck('AP_toy',np.isclose(average_precision_score([1,0,1,0],[.9,.7,.4,.1]),5/6));ck('AUC_toy',np.isclose(roc_auc_score([1,0,1,0],[.9,.7,.4,.1]),.75))
    examples=pd.concat([parts['train'].query('late==@cls').sort_values('order_id').head(2) for cls in [0,1]])
    examples.to_csv(R/'data/prepared/four_real_orders.csv',index=False)
    one=tr[tr.order_id=='fc9bc4bac939adaa600ad59dee9a106f'].iloc[0];filled=imp.transform(one[FEATURES].to_frame().T.astype(float))[0];scaled=sc.transform(filled.reshape(1,-1))[0];cont=scaled*model.coef_[0];z=float(model.intercept_[0]+cont.sum());p=float(expit(z))
    trace=dict(order_id=one.order_id,late=int(one.late),raw=one[FEATURES].to_dict(),filled=filled.tolist(),standardized=scaled.tolist(),contributions=cont.tolist(),intercept=float(model.intercept_[0]),z=z,p=p,prediction=int(p>=(selected if selected is not None else float('inf'))))
    ck('one_ID_prediction',np.isclose(p,float(parts['train'].loc[parts['train'].order_id==one.order_id,'score'].iloc[0])))
    bins=np.array([0,.02,.04,.06,.08,.10,.15,.20,.30,1]);idx=np.minimum(np.searchsorted(bins,scores['test'],side='right')-1,len(bins)-2);reliability=[]
    for j in range(len(bins)-1):
        m=idx==j
        if m.any():reliability.append(dict(lower=float(bins[j]),upper=float(bins[j+1]),n=int(m.sum()),mean_p=float(scores['test'][m].mean()),late_rate=float(testy[m].mean())))
    ck('reliability_population',sum(a['n'] for a in reliability)==len(testy))
    for k,a in parts.items():a['prediction_selected']=((a.score>=selected).astype(int) if selected is not None else 0);a.to_csv(R/f'data/prepared/{k}_predictions.csv',index=False)
    pd.DataFrame({'id':list('ABCD'),'x':toyx,'y':toyy}).to_csv(R/'data/prepared/toy_four_orders.csv',index=False)
    policy=dict(features=FEATURES,solver='newton-cg',C=1,penalty='l2',objective_mean_penalty_lambda=lam,threshold_grid=GRID,selected=selected,selected_policy=best['policy'],criterion='hypothetical K=FP+5FN; not monetary',tie_rule='fewer alerts then larger threshold; no alerts allowed',fit_split='train only; no refit',selection_split='validation',test_exposure='historical cohort inspected in previous course versions')
    out=dict(status='pass',checks_count=len(checks),checks=checks,split_counts={k:len(a) for k,a in parts.items()},positive_counts={k:int(a.late.sum()) for k,a in parts.items()},prevalences={k:float(a.late.mean()) for k,a in parts.items()},features=FEATURES,imputer=imp.statistics_.tolist(),scaler_mean=sc.mean_.tolist(),scaler_scale=sc.scale_.tolist(),coef=model.coef_[0].tolist(),intercept=float(model.intercept_[0]),solver_iterations=model.n_iter_.tolist(),real_objective_gradient_norm=float(np.linalg.norm(g)),policy=policy,validation_scan=scan,selected=best,test_default=default,test_selected=chosen,baseline=base,four_orders=json.loads(examples.to_json(orient='records',date_format='iso')),one_order=trace,reliability=reliability,toy=dict(x=toyx.tolist(),y=toyy.tolist(),history=hist,eta_histories={str(v):gradient_descent(toyx,toyy,eta=v,steps=15) for v in [.1,1,10,100]},L2=dict(lam=.1,w=float(opt.x[0]),b=float(opt.x[1]),loss=float(opt.fun)),separating_ray=ray),versions=dict(python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__,sklearn=__import__('sklearn').__version__,scipy=__import__('scipy').__version__))
    for name,value in [('case_audit',out),('model_policy',policy)]: (R/f'results/{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:out[k] for k in ['status','checks_count','coef','intercept','test_selected']},ensure_ascii=False));return out
if __name__=='__main__':run()
