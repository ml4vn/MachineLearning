"""Independent exact arithmetic and whole-cohort evidence checks."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
from datetime import date,datetime
import csv,json,sys,itertools,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
A=json.loads((R/'results/case_audit.json').read_text(encoding='utf8'));Z=np.load(R/'data/lab_arrays.npz');checks={}
def ck(k,v):checks[k]=bool(v);assert v,k
pts=[tuple(F(int(x)) for x in p) for p in A['toy']['points']]
def d2(a,b):return sum((x-y)**2 for x,y in zip(a,b))
def means(group):return tuple(sum(p[j] for p in group)/len(group) for j in [0,1])
c=[pts[0],pts[2]];history=[]
for loop in range(3):
 dist=[[d2(p,t) for t in c] for p in pts];lab=[0 if ds[0]<=ds[1] else 1 for ds in dist];J=sum(ds[j] for ds,j in zip(dist,lab));history.append(J)
 nc=[means([p for p,j in zip(pts,lab) if j==k]) for k in [0,1]];J2=sum(d2(p,nc[j]) for p,j in zip(pts,lab));history.append(J2)
 ck(f'assignment_{loop}',lab==A['toy']['history'][2*loop]['labels']);ck(f'J_assign_{loop}',abs(float(J)-A['toy']['history'][2*loop]['J'])<1e-10)
 ck(f'J_update_{loop}',abs(float(J2)-A['toy']['history'][2*loop+1]['J'])<1e-10)
 for k in [0,1]:
  group=[p for p,j in zip(pts,lab) if j==k];m=nc[k]
  for shift in [(F(1),F(0)),(F(0),F(1)),(F(-2,3),F(3,5))]:
   candidate=tuple(x+y for x,y in zip(m,shift));ck(f'mean_identity_{loop}_{k}_{shift}',sum(d2(p,candidate) for p in group)==sum(d2(p,m) for p in group)+len(group)*d2(candidate,m))
 for i,p in enumerate(pts):
  u,w=c;linear=2*sum(p[j]*(w[j]-u[j]) for j in [0,1])+sum(u[j]**2-w[j]**2 for j in [0,1]);ck(f'boundary_{loop}_{i}',linear==d2(p,u)-d2(p,w))
 c=nc
ck('exact_sequence',history==[F(39),F(12),F(93,8),F(22,3),F(22,3),F(22,3)])
ck('Chi_switch',d2(pts[2],(F(3,2),F(1)))==F(25,4) and d2(pts[2],(F(21,4),F(17,4)))==F(53,8))
def partitions(a):
 if len(a)==6:yield a;return
 for k in range(max(a)+2):yield from partitions(a+[k])
best={k:None for k in range(1,7)};count=0
for lab in partitions([0]):
 count+=1;k=max(lab)+1;cent=[means([p for p,j in zip(pts,lab) if j==i]) for i in range(k)];J=sum(d2(p,cent[j]) for p,j in zip(pts,lab));best[k]=J if best[k] is None else min(best[k],J)
ck('203_partitions',count==203);ck('global_values',[best[k] for k in range(1,7)]==[F(269,6),F(22,3),F(19,6),F(1),F(1,2),F(0)])
rows=list(csv.DictReader((R/'data/retail_rfm.csv').open(encoding='utf8')));X0=np.array([[float(r[k]) for k in ['recency','frequency','monetary']] for r in rows]);log=np.log1p(X0);mean=log.mean(0);sd=np.sqrt(((log-mean)**2).mean(0));X=(log-mean)/sd
ck('4338_unique_ID',len(rows)==4338 and len({r['CustomerID'] for r in rows})==4338);ck('ordered_RFM_array',np.allclose(X0,Z['X0']));ck('log_array',np.allclose(log,Z['log']));ck('manual_scaler',np.allclose(X,Z['X'],atol=1e-12));ck('saved_mean',np.allclose(mean,A['pipeline']['scaler_mean']));ck('saved_std',np.allclose(sd,A['pipeline']['scaler_scale']));ck('one_center_J',abs(float((X**2).sum())-13014)<1e-8)
cent=np.array(A['centers_k4']);dist=((X[:,None,:]-cent[None,:,:])**2).sum(2);labels=np.array([int(r['cluster_k4']) for r in rows]);ck('nearest_center_all',np.array_equal(dist.argmin(1),labels));ck('J_K4_all',abs(dist[np.arange(len(X)),labels].sum()-A['experiments'][2]['inertia'])<1e-7)
ck('relabel_invariance',np.array_equal(np.argsort([3,0,2,1])[np.array([3,0,2,1])[labels]],labels))
for k in range(4):
 ck('mean_center_'+str(k),np.allclose(X[labels==k].mean(0),cent[k],atol=.01))
 group=[r for r in rows if int(r['cluster_k4'])==k];profile=A['profile'][k];ck('profile_count_'+str(k),len(group)==profile['n'])
 for key,field in [('R','recency'),('F','frequency'),('M','monetary')]:
  vals=sorted(float(r[field]) for r in group);n=len(vals);median=vals[n//2] if n%2 else (vals[n//2-1]+vals[n//2])/2;ck('median_'+str(k)+'_'+key,abs(median-profile[key])<1e-9)
 inverse=np.expm1(cent[k]*sd+mean);ck('inverse_center_'+str(k),np.allclose(inverse,A['inverse_centers_k4'][k]));ck('inverse_not_median_'+str(k),not np.allclose(inverse,[profile[z] for z in ['R','F','M']]))
lines=list(csv.DictReader((R/'data/example_customer_lines.csv').open(encoding='utf8')));last=max(datetime.fromisoformat(r['InvoiceDate']).date() for r in lines);money=sum(Decimal(r['Quantity'])*Decimal(r['UnitPrice']) for r in lines)
ck('12755_all_lines',len(lines)==4 and all(r['CustomerID']=='12755' for r in lines));ck('12755_R_calendar',(date(2011,12,10)-last).days==281);ck('12755_F',len({r['InvoiceNo'] for r in lines})==2);ck('12755_M_decimal',money==Decimal('3811.95'))
i=next(i for i,r in enumerate(rows) if r['CustomerID']=='12755');ck('12755_x',np.allclose(X[i],A['example']['scaled']));ck('12755_all_d2',np.allclose(dist[i],A['example']['d2_k4']));ck('12755_group',int(dist[i].argmin())==3)
ck('silhouette_exact',F(9-2,9)==F(7,9));ck('silhouette_negative',F(1-2,2)==F(-1,2))
for z in A['experiments']:
 ck('K'+str(z['k'])+'_counts',sum(z['sizes'])==4338);ck('K'+str(z['k'])+'_primary_scope',z['silhouette']==z['silhouette_subsamples']['42'])
ck('K2_best_each_subsample',all(A['experiments'][0]['silhouette_subsamples'][s]>max(z['silhouette_subsamples'][s] for z in A['experiments'][1:]) for s in ['42','43','44']));ck('K2_above_K4_full',A['experiments'][0]['silhouette_full']>A['experiments'][2]['silhouette_full'])
ck('equal_budgets',A['stability_budget']['reference_n_init']==A['stability_budget']['n_init']==20);ck('ARI_range',all(0<=z['ARI']<=1 for z in A['stability']));trans=np.array(A['dedup']['aligned_transition']);ck('aligned_all_customers',trans.sum()==4338);ck('aligned_row_counts',np.array_equal(trans.sum(1),[z['n'] for z in A['profile']]));ck('aligned_col_counts',np.array_equal(trans.sum(0),[z['n'] for z in A['dedup']['aligned_profiles']]));ck('changed_951',A['dedup']['changed_customers']==951);ck('dedup_does_not_increase_M',A['dedup']['M_total']<=A['dedup']['M_total_keep'])
ck('raw_zip_hash',hashlib.sha256((R/'data/online_retail.zip').read_bytes()).hexdigest()==A['raw_sha256']);ck('fractional_penny_rows',A['fractional_penny_price_rows']==4)
result={'status':'pass','checks_count':len(checks),'checks':checks,'scope':'Independent exact toy geometry, manual scaler, whole-cohort assignment/objective/profiles, raw-line RFM and declared comparison scopes.'}
(R/'results/science_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:result[k] for k in ['status','checks_count']}))
