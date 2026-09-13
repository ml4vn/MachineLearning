"""Olist gốc → một hàng mỗi đơn; công thức thống nhất cho Bài 4–7.

Không fit mô hình hoặc sử dụng nhãn để tạo các đặc trưng đầu vào.
Snapshot địa lý/sản phẩm tĩnh không chứng minh tính sẵn có trong lịch sử.
"""
import zipfile
import numpy as np
import pandas as pd
from mlcourse.common import require_file
from mlcourse.data import entries, verify

FEATURES=['distance_km','promised_days','price','freight_value','n_items','weight_g']
DATES=['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']

def haversine_km(lat1,lon1,lat2,lon2):
    p1,p2=np.radians(lat1),np.radians(lat2)
    a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(np.radians(np.asarray(lon2)-np.asarray(lon1))/2)**2
    return 6371.0088*2*np.arcsin(np.sqrt(np.clip(a,0,1)))

def calendar_late(delivered,estimated):
    a,b=pd.to_datetime(delivered),pd.to_datetime(estimated)
    if a.isna().any() or b.isna().any(): raise ValueError('Không thể gán nhãn khi thiếu ngày')
    return (a.dt.normalize()>b.dt.normalize()).astype(int)

def temporal_split(d):
    split=pd.Series('outside_window',index=d.index)
    for name,start,end,cutoff in [('train','2017-01-01','2017-11-01','2017-11-01'),
                                 ('validation','2017-11-01','2018-01-01','2018-01-01'),
                                 ('test','2018-01-01','2018-07-01',None)]:
        mask=d.order_approved_at.ge(start)&d.order_approved_at.lt(end)
        if cutoff: mask &= d.order_delivered_customer_date.lt(cutoff)
        split.loc[mask]=name
    return split

def prepare_olist(data_dir):
    raw=require_file(data_dir,'olist.zip');verify(raw,entries('olist')[0]['sha256'])
    with zipfile.ZipFile(raw) as z:
        def read(name):
            with z.open(f'olist_{name}_dataset.csv') as f: return pd.read_csv(f)
        orders=read('orders');items=read('order_items');products=read('products')
        customers=read('customers');sellers=read('sellers');geo=read('geolocation')
    if not orders.order_id.is_unique: raise ValueError('Trùng order_id trong bảng orders')
    for c in DATES: orders[c]=pd.to_datetime(orders[c],errors='coerce')
    g=geo.groupby('geolocation_zip_code_prefix')[['geolocation_lat','geolocation_lng']].median()
    cust=customers.merge(g,left_on='customer_zip_code_prefix',right_index=True,how='left',validate='many_to_one')
    cust=cust.rename(columns={'geolocation_lat':'clat','geolocation_lng':'clng'})
    sell=sellers.merge(g,left_on='seller_zip_code_prefix',right_index=True,how='left',validate='many_to_one')
    sell=sell.rename(columns={'geolocation_lat':'slat','geolocation_lng':'slng'})
    it=items.merge(products[['product_id','product_weight_g']],on='product_id',how='left',validate='many_to_one')
    it=it.merge(sell[['seller_id','slat','slng']],on='seller_id',how='left',validate='many_to_one')
    addr=orders[['order_id','customer_id']].merge(cust[['customer_id','clat','clng']],on='customer_id',validate='many_to_one')
    it=it.merge(addr,on='order_id',validate='many_to_one')
    it['distance_km']=haversine_km(it.clat,it.clng,it.slat,it.slng)
    # Giữ sum mặc định của pilot: cả nhóm thiếu cân nặng cho tổng 0.
    # Cột đếm thiếu và báo cáo bên dưới giúp phân biệt 0 này với trọng lượng đo được.
    agg=it.groupby('order_id').agg(price=('price','sum'),freight_value=('freight_value','sum'),
          n_items=('order_item_id','count'),weight_g=('product_weight_g','sum'),
          known_weights=('product_weight_g','count'),distance_km=('distance_km','mean'))
    d=orders.merge(agg,left_on='order_id',right_index=True,how='left',validate='one_to_one')
    d=d.merge(customers[['customer_id','customer_unique_id']],on='customer_id',how='left',validate='many_to_one')
    d['delivery_days']=(d.order_delivered_customer_date-d.order_approved_at).dt.total_seconds()/86400
    d['promised_days']=(d.order_estimated_delivery_date-d.order_approved_at).dt.total_seconds()/86400
    eligible=(d.order_status.eq('delivered')&d[DATES].notna().all(axis=1)&d.delivery_days.ge(0)&d.promised_days.ge(0)&d.n_items.notna())
    d=d.loc[eligible].copy()
    d['late']=calendar_late(d.order_delivered_customer_date,d.order_estimated_delivery_date)
    d['split']=temporal_split(d)
    audit={'raw_orders':len(orders),'eligible_delivered_orders':len(d),
           'excluded_by_split_or_label_cutoff':int(d.split.eq('outside_window').sum())}
    clean=d.loc[d.split!='outside_window',['order_id','customer_unique_id']+DATES+FEATURES+['known_weights','delivery_days','late','split']].reset_index(drop=True)
    if not clean.order_id.is_unique: raise AssertionError('Bảng cuối phải duy nhất theo đơn')
    audit.update(rows=len(clean),split_counts=clean.split.value_counts().to_dict(),
                 missing_features=clean[FEATURES].isna().sum().to_dict(),
                 all_weights_missing=int(clean.known_weights.eq(0).sum()),
                 some_weights_missing=int(clean.known_weights.lt(clean.n_items).sum()),
                 weight_warning='All-missing weights sum to 0 in frozen pilot; not a measured zero.')
    return clean,audit
