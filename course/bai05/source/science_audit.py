"""Independent raw-data and arithmetic audit; no call to the training lab."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import rankdata

def run():
    checks={}
    def ck(name,ok):
        checks[name]=bool(ok)
        assert ok,name
    a=json.loads((R/'results/case_audit.json').read_text(encoding='utf8'))
    prov=json.loads((R/'results/data_provenance.json').read_text(encoding='utf8'))
    cols=a['features'];dates=['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']
    d=pd.read_csv(R/'data/prepared/olist_model_table.csv',parse_dates=dates).set_index('order_id')
    with ZipFile(R.parent/'datasets/olist.zip') as z:
        get=lambda n:pd.read_csv(z.open('olist_'+n+'_dataset.csv'))
        o,it,pr,cu,se,ge=[get(n) for n in ['orders','order_items','products','customers','sellers','geolocation']]
    ck('raw_sha',hashlib.sha256((R.parent/'datasets/olist.zip').read_bytes()).hexdigest()==prov['sha256_raw'])
    ck('prepared_sha',hashlib.sha256((R/'data/prepared/olist_model_table.csv').read_bytes()).hexdigest()==prov['sha256_prepared'])
    o=o.set_index('order_id');o[dates]=o[dates].apply(pd.to_datetime)
    ck('unique_raw_ID',o.index.is_unique and d.index.is_unique)
    for c in dates:ck('raw_timestamp_'+c,o.loc[d.index,c].equals(d[c]))
    ck('delivered_only',o.loc[d.index,'order_status'].eq('delivered').all())
    ck('nonnegative_durations',d.delivery_days.ge(0).all() and d.promised_days.ge(0).all())
    ck('calendar_label',np.array_equal(d.late,(o.loc[d.index,dates[1]].dt.date>o.loc[d.index,dates[2]].dt.date).astype(int)))
    ck('promised_days',np.allclose(d.promised_days,(o.loc[d.index,dates[2]]-o.loc[d.index,dates[0]]).dt.total_seconds()/86400))
    parts={k:d[d.split==k] for k in ['train','validation','test']}
    for k,lo,hi in [('train','2017-01-01','2017-11-01'),('validation','2017-11-01','2018-01-01'),('test','2018-01-01','2018-07-01')]:
        x=parts[k];ck(k+'_window',x[dates[0]].ge(lo).all() and x[dates[0]].lt(hi).all())
        ck(k+'_count',len(x)==a['split_counts'][k]);ck(k+'_late_count',int(x.late.sum())==a['positive_counts'][k])
        if k!='test':ck(k+'_labels_known',x[dates[1]].lt(hi).all())
    item=it.merge(pr[['product_id','product_weight_g']],on='product_id',validate='many_to_one');g=item.groupby('order_id')
    for c in ['price','freight_value']:ck(c+'_sum_from_raw',np.allclose(g[c].sum().loc[d.index],d[c]))
    ck('item_rows_from_raw',np.array_equal(g.size().loc[d.index],d.n_items))
    w=g.product_weight_g.sum(min_count=1);w[g.product_weight_g.count()<g.size()]=np.nan
    ck('unknown_weight_rule',np.allclose(w.loc[d.index],d.weight_g,equal_nan=True))
    correction=pd.read_csv(R/'data/prepared/weight_corrections.csv')
    ck('weight_fix_16_train',len(correction)==16 and correction.split.eq('train').all() and correction.weight_g_before.eq(0).all() and correction.weight_g_corrected.isna().all())
    # Recompute postal medians and spherical distance without prepare_olist.py.
    geo=ge.groupby('geolocation_zip_code_prefix')[['geolocation_lat','geolocation_lng']].median()
    loc=lambda frame,prefix:frame.merge(geo,left_on=prefix,right_index=True,how='left')
    c=loc(cu,'customer_zip_code_prefix');s=loc(se,'seller_zip_code_prefix')
    t=it.merge(s[['seller_id','geolocation_lat','geolocation_lng']],on='seller_id',how='left').rename(columns={'geolocation_lat':'a','geolocation_lng':'b'})
    t=t.merge(o[['customer_id']],left_on='order_id',right_index=True).merge(c[['customer_id','geolocation_lat','geolocation_lng']],on='customer_id',how='left')
    lat1,lat2=np.deg2rad(t.a),np.deg2rad(t.geolocation_lat);delta=np.deg2rad(t.b-t.geolocation_lng)
    h=np.sin((lat1-lat2)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta/2)**2
    t['km']=2*6371.0088*np.arctan2(np.sqrt(np.clip(h,0,1)),np.sqrt(1-np.clip(h,0,1)))
    ck('distance_from_raw',np.allclose(t.groupby('order_id').km.mean().loc[d.index],d.distance_km,equal_nan=True))
    tr=parts['train'];med=tr[cols].median();filled=tr[cols].fillna(med)
    ck('train_only_median',np.allclose(med,a['imputer']))
    ck('train_only_mean',np.allclose(filled.mean(),a['scaler_mean']))
    ck('train_only_std_ddof0',np.allclose(filled.std(ddof=0),a['scaler_scale']))
    def manual_metrics(y,p,tau):
        y=np.asarray(y);p=np.asarray(p);pred=p>=tau
        tp=int(np.sum((y==1)&pred));fp=int(np.sum((y==0)&pred));fn=int(np.sum((y==1)&~pred));tn=int(np.sum((y==0)&~pred))
        # Group equal scores together for AP, and assign half credit to AUC ties.
        order=np.argsort(-p,kind='stable');yy=y[order];pp=p[order];ends=np.r_[np.flatnonzero(np.diff(pp)!=0),len(y)-1]
        cum=np.cumsum(yy)[ends];precision=cum/(ends+1);recall=cum/y.sum();ap=float(np.sum(np.diff(np.r_[0,recall])*precision))
        pos=int(y.sum());neg=len(y)-pos;r=rankdata(p,method='average');auc=float((r[y==1].sum()-pos*(pos+1)/2)/(pos*neg))
        return dict(tn=tn,fp=fp,fn=fn,tp=tp,cost=fp+5*fn,alerts=fp+tp,precision=tp/(tp+fp) if tp+fp else 0.,recall=tp/(tp+fn),ap=ap,auc=auc,brier=float(np.mean((p-y)**2)),log_loss=float(-np.mean(y*np.log(p)+(1-y)*np.log1p(-p))))
    for k in parts:
        x=parts[k];u=(x[cols].fillna(med)-np.asarray(a['scaler_mean']))/np.asarray(a['scaler_scale']);z=a['intercept']+u.to_numpy()@np.asarray(a['coef']);p=expit(z)
        stored=pd.read_csv(R/f'data/prepared/{k}_predictions.csv').set_index('order_id').loc[x.index]
        ck(k+'_probability_recomputed',np.allclose(p,stored.score,atol=1e-14))
        if k=='test':
            for name,tau in [('test_default',.5),('test_selected',a['policy']['selected'])]:
                out=manual_metrics(x.late,p,tau)
                for metric,v in out.items():ck(name+'_'+metric,np.isclose(v,a[name][metric],atol=1e-12))
        if k=='validation':
            scan=[(manual_metrics(x.late,p,t)['cost'],manual_metrics(x.late,p,t)['alerts'],-t,t) for t in [.02,.03,.05,.1,.15,.2,.3,.5,.8]]
            scan.append((5*int(x.late.sum()),0,-float('inf'),None))
            ck('validation_policy_no_test',min(scan)[-1]==a['policy']['selected'])
    x=np.array([-1.,0.,1.,2.]);y=np.array([0.,0.,1.,1.]);theta=np.zeros(2)
    objective=lambda th,l:np.mean(np.logaddexp(0,th[1]+th[0]*x)-y*(th[1]+th[0]*x))+l*th[0]**2/2
    for i in range(3):
        h=a['toy']['history'][i];ck('toy_parameters_'+str(i),np.allclose(theta,[h['w'],h['b']]))
        pp=expit(theta[1]+theta[0]*x);grad=np.array([np.mean(x*(pp-y)),np.mean(pp-y)])
        ck('toy_loss_'+str(i),np.isclose(objective(theta,0),h['loss']));ck('toy_grad_'+str(i),np.allclose(grad,h['gradient']))
        for l in [0,.1]:
            fd=np.array([(objective(theta+np.eye(2)[j]*1e-5,l)-objective(theta-np.eye(2)[j]*1e-5,l))/2e-5 for j in range(2)])
            ck('finite_diff_'+str(i)+'_'+str(l),np.allclose(fd,grad+[l*theta[0],0],atol=2e-9))
        theta=theta-grad
    ck('toy_sigmoid_anchor',np.isclose(expit(-.8),.31002551887238755))
    ck('toy_AP_AUC',np.isclose(manual_metrics([1,0,1,0],[.9,.7,.4,.1],.5)['ap'],5/6) and np.isclose(manual_metrics([1,0,1,0],[.9,.7,.4,.1],.5)['auc'],.75))
    out=dict(status='pass',checks_count=len(checks),checks=checks,method='Independent raw joins, calendar labels, train statistics, direct-count metrics, grouped-score AP, rank AUC, finite-difference gradients. No call to training code.',sha256_prepared=prov['sha256_prepared'])
    (R/'results/science_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('Independent audit:',len(checks),'checks passed.');return out
if __name__=='__main__':run()
