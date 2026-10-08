"""Rebuild the historical teaching table from the bundled Olist raw archive.

The task predicts fractional days from approval to customer delivery.
Completed-only selection and label cutoffs limit the interpretation.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'.build/pydeps').exists():sys.path.insert(0,str(ROOT/'.build/pydeps'))
import numpy as np
import pandas as pd

def prepare():
    raw=ROOT.parent/'datasets/olist.zip'
    with ZipFile(raw) as z:
        def read(n):return pd.read_csv(z.open('olist_'+n+'_dataset.csv'))
        orders=read('orders');items=read('order_items');products=read('products')
        customers=read('customers');sellers=read('sellers');geo=read('geolocation')
    for c in ['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']:
        orders[c]=pd.to_datetime(orders[c],errors='coerce')
    # Median coordinates per postal prefix. These are geographical snapshots,
    # not outcome-derived features or an audited historical address registry.
    g=geo.groupby('geolocation_zip_code_prefix')[['geolocation_lat','geolocation_lng']].median()
    c=customers.merge(g,left_on='customer_zip_code_prefix',right_index=True,how='left',validate='many_to_one').rename(columns={'geolocation_lat':'clat','geolocation_lng':'clng'})
    s=sellers.merge(g,left_on='seller_zip_code_prefix',right_index=True,how='left',validate='many_to_one').rename(columns={'geolocation_lat':'slat','geolocation_lng':'slng'})
    a=items.merge(products[['product_id','product_weight_g']],on='product_id',how='left',validate='many_to_one')
    a=a.merge(s[['seller_id','slat','slng']],on='seller_id',how='left',validate='many_to_one')
    addresses=orders[['order_id','customer_id']].merge(c[['customer_id','clat','clng']],on='customer_id',validate='many_to_one')
    a=a.merge(addresses,on='order_id',validate='many_to_one')
    p1,p2=np.radians(a.clat),np.radians(a.slat)
    h=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(np.radians(a.slng-a.clng)/2)**2
    a['distance_km']=6371.0088*2*np.arcsin(np.sqrt(np.clip(h,0,1)))
    agg=a.groupby('order_id').agg(price=('price','sum'),freight_value=('freight_value','sum'),n_items=('order_item_id','count'),weight_g=('product_weight_g','sum'),distance_km=('distance_km','mean'))
    d=orders.merge(agg,left_on='order_id',right_index=True,how='left',validate='one_to_one')
    d['delivery_days']=(d.order_delivered_customer_date-d.order_approved_at).dt.total_seconds()/86400
    d['promised_days']=(d.order_estimated_delivery_date-d.order_approved_at).dt.total_seconds()/86400
    d['late']=(d.order_delivered_customer_date.dt.normalize()>d.order_estimated_delivery_date.dt.normalize()).astype(int)
    eligible=d.order_status.eq('delivered')&d.order_approved_at.notna()&d.order_delivered_customer_date.notna()&d.order_estimated_delivery_date.notna()&d.delivery_days.ge(0)&d.promised_days.ge(0)&d.n_items.notna()
    d=d[eligible].copy();d['split']='outside_window'
    d.loc[d.order_approved_at.ge('2017-01-01')&d.order_approved_at.lt('2017-11-01')&d.order_delivered_customer_date.lt('2017-11-01'),'split']='train'
    d.loc[d.order_approved_at.ge('2017-11-01')&d.order_approved_at.lt('2018-01-01')&d.order_delivered_customer_date.lt('2018-01-01'),'split']='validation'
    d.loc[d.order_approved_at.ge('2018-01-01')&d.order_approved_at.lt('2018-07-01'),'split']='test'
    clean=d[d.split!='outside_window'].copy()
    cols=['order_id','order_approved_at','order_delivered_customer_date','order_estimated_delivery_date','distance_km','promised_days','price','freight_value','n_items','weight_g','delivery_days','late','split']
    target=ROOT/'data/prepared';target.mkdir(parents=True,exist_ok=True)
    clean[cols].to_csv(target/'olist_model_table.csv',index=False)
    available=clean[clean.split=='train'].dropna(subset=['distance_km']).copy();picks=[]
    for km in [100,400,800,1400]:
        i=(available.distance_km-km).abs().idxmin();picks.append(i);available=available.drop(index=i)
    examples=clean.loc[picks,['order_id','distance_km','delivery_days','promised_days']]
    examples.to_csv(target/'olist_four_real_orders.csv',index=False)
    report=dict(raw_orders=len(orders),eligible_completed_orders=len(d),split_counts={k:int(v) for k,v in clean.split.value_counts().items()},
        distance_recipe='Median latitude/longitude per postal prefix; haversine radius6371.0088km; mean per item within order.',
        four_order_selection='Nearest available train distance to100,400,800,1400km; no selection by delivery label.',
        target='(delivered−approved).total_seconds()/86400',
        sha256_raw=hashlib.sha256(raw.read_bytes()).hexdigest(),sha256_prepared=hashlib.sha256((target/'olist_model_table.csv').read_bytes()).hexdigest(),
        limitations=['Completed-only cohort; excluded late completion at train/validation cutoff.','Static geographical snapshots do not prove address availability at historical approval time.','Historical test already inspected in earlier course versions.'])
    (ROOT/'results/data_provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report
if __name__=='__main__':print(json.dumps(prepare(),ensure_ascii=False,indent=2))
