"""Rebuild Olist classification cohort; missing component weights stay unknown."""
from pathlib import Path
from zipfile import ZipFile
import sys,json,hashlib
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import pandas as pd
import numpy as np

def prepare():
    raw=R.parent/'datasets/olist.zip'
    with ZipFile(raw) as z:
        def read(n):return pd.read_csv(z.open('olist_'+n+'_dataset.csv'))
        o,it,pr,cu,se,ge=[read(n) for n in ['orders','order_items','products','customers','sellers','geolocation']]
    dates=['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']
    for c in dates:o[c]=pd.to_datetime(o[c],errors='coerce')
    g=ge.groupby('geolocation_zip_code_prefix')[['geolocation_lat','geolocation_lng']].median()
    cu=cu.merge(g,left_on='customer_zip_code_prefix',right_index=True,how='left',validate='many_to_one').rename(columns={'geolocation_lat':'clat','geolocation_lng':'clng'})
    se=se.merge(g,left_on='seller_zip_code_prefix',right_index=True,how='left',validate='many_to_one').rename(columns={'geolocation_lat':'slat','geolocation_lng':'slng'})
    a=it.merge(pr[['product_id','product_weight_g']],on='product_id',how='left',validate='many_to_one').merge(se[['seller_id','slat','slng']],on='seller_id',how='left',validate='many_to_one')
    a=a.merge(o[['order_id','customer_id']].merge(cu[['customer_id','clat','clng']],on='customer_id',validate='many_to_one'),on='order_id',validate='many_to_one')
    p1,p2=np.radians(a.clat),np.radians(a.slat)
    h=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(np.radians(a.slng-a.clng)/2)**2
    a['distance_km']=6371.0088*2*np.arcsin(np.sqrt(np.clip(h,0,1)))
    group=a.groupby('order_id')
    agg=group.agg(price=('price','sum'),freight_value=('freight_value','sum'),n_items=('order_item_id','count'),distance_km=('distance_km','mean'))
    agg['weight_g']=group.product_weight_g.sum(min_count=1)
    # A partial sum is not the total weight either: unknown if ANY component unknown.
    agg.loc[group.product_weight_g.count()<group.size(),'weight_g']=np.nan
    d=o.merge(agg,left_on='order_id',right_index=True,how='left',validate='one_to_one')
    d['delivery_days']=(d[dates[1]]-d[dates[0]]).dt.total_seconds()/86400
    d['promised_days']=(d[dates[2]]-d[dates[0]]).dt.total_seconds()/86400
    d['late']=(d[dates[1]].dt.normalize()>d[dates[2]].dt.normalize()).astype(int)
    mask=d.order_status.eq('delivered')&d[dates].notna().all(axis=1)&d.delivery_days.ge(0)&d.promised_days.ge(0)&d.n_items.notna()
    eligible=d[mask].copy();eligible['split']='outside_window'
    for k,lo,hi in [('train','2017-01-01','2017-11-01'),('validation','2017-11-01','2018-01-01'),('test','2018-01-01','2018-07-01')]:
        m=eligible[dates[0]].ge(lo)&eligible[dates[0]].lt(hi)
        if k!='test':m&=eligible[dates[1]].lt(hi)
        eligible.loc[m,'split']=k
    d=eligible[eligible.split!='outside_window'].copy()
    cols=['order_id',*dates,'distance_km','promised_days','price','freight_value','n_items','weight_g','delivery_days','late','split']
    d=d[cols];d.to_csv(R/'data/prepared/olist_model_table.csv',index=False)
    old=pd.read_csv(R/'data/frozen_v3/olist_model_table.csv',parse_dates=dates).set_index('order_id');new=d.set_index('order_id').loc[old.index]
    changed=~(old.weight_g.eq(new.weight_g)|(old.weight_g.isna()&new.weight_g.isna()))
    assert len(old)==len(new) and all((old[c].equals(new[c]) if c in dates or c=='split' else np.allclose(old[c],new[c],equal_nan=True)) for c in cols if c not in ['order_id','weight_g'])
    correction=pd.DataFrame({'split':new.split,'weight_g_v3':old.weight_g,'weight_g_v4':new.weight_g})[changed];correction.to_csv(R/'data/prepared/weight_corrections.csv')
    out=dict(status='pass',raw_orders=len(o),eligible_completed_orders=len(eligible),split_counts=d.split.value_counts().to_dict(),positive_counts=d.groupby('split').late.sum().to_dict(),weight_correction_count=int(changed.sum()),weight_corrections_by_split=correction.split.value_counts().to_dict(),missing_by_split=d.groupby('split').weight_g.apply(lambda s:int(s.isna().sum())).to_dict(),other_columns_preserved=True,weight_rule='Total weight is unknown if any item weight is unknown; do not replace unknown with zero.',distance_recipe='Median coordinate per postal prefix; haversine radius6371.0088km; mean item distance per order.',label='date(delivered)>date(estimated); same calendar day is on time.',sha256_raw=hashlib.sha256(raw.read_bytes()).hexdigest(),sha256_prepared=hashlib.sha256((R/'data/prepared/olist_model_table.csv').read_bytes()).hexdigest(),limitations=['Completed-only eligible cohort; train/validation labels complete before cutoff.','Static product/geographic metadata: historical availability is assumed.','Test has been inspected in earlier versions; this is a historical reproduction.'])
    (R/'results/data_provenance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(out,ensure_ascii=False));return out
if __name__=='__main__':prepare()
