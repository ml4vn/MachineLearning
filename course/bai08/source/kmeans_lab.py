from pathlib import Path
import sys,os,json,zipfile,hashlib,itertools,shutil
from decimal import Decimal
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'.build/pydeps'))
os.environ.setdefault('MPLCONFIGDIR',str(R/'.build/mplconfig'))
import numpy as np,pandas as pd,sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score,silhouette_samples,adjusted_rand_score
from sklearn.datasets import make_moons
from threadpoolctl import threadpool_limits
P=np.array([[1,1],[2,1],[3,3],[5,4],[6,5],[7,5]],dtype=float)
NAMES=['An','Bình','Chi','Dung','Hà','Lan']
def dump(name,x): (R/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_raw():
 with zipfile.ZipFile(R/'data/online_retail.zip') as z:return pd.read_excel(z.open(next(n for n in z.namelist() if n.endswith('.xlsx'))))
def prepare(d):
 valid=d.CustomerID.notna()&d.Quantity.gt(0)&d.UnitPrice.gt(0)&~d.InvoiceNo.astype(str).str.lower().str.startswith('c')
 a=d[valid].copy();a['CustomerID']=a.CustomerID.astype('int64');a['InvoiceNo']=a.InvoiceNo.astype(str);a['line_value']=a.Quantity*a.UnitPrice
 f=a.groupby('CustomerID').agg(last_date=('InvoiceDate','max'),frequency=('InvoiceNo','nunique'),monetary=('line_value','sum'),retained_lines=('InvoiceNo','size'))
 f['recency']=(pd.Timestamp('2011-12-10')-f.last_date.dt.normalize()).dt.days
 return a,f
def lloyd(points,centers):
 c=np.array(centers,dtype=float);history=[];previous=None
 for t in range(50):
  d=((points[:,None,:]-c[None,:,:])**2).sum(axis=2);labels=d.argmin(axis=1)
  if len(np.unique(labels))<len(c):return None
  history.append(dict(phase='assign',centers=c.tolist(),labels=labels.tolist(),d2=d.tolist(),J=float(d[np.arange(len(points)),labels].sum())))
  new=np.array([points[labels==j].mean(axis=0) for j in range(len(c))])
  history.append(dict(phase='update',centers=new.tolist(),labels=labels.tolist(),J=float(((points-new[labels])**2).sum())))
  if np.allclose(c,new,atol=1e-12,rtol=0):break
  c=new
 return history
def partitions(n):
 def rec(a):
  if len(a)==n:yield a;return
  for k in range(max(a)+2):yield from rec(a+[k])
 yield from rec([0])
def run():
 checks={}
 def ck(name,x):checks[name]=bool(x);assert checks[name],name
 d=load_raw();a,f=prepare(d);X0=f[['recency','frequency','monetary']].to_numpy();lg=np.log1p(X0);sc=StandardScaler().fit(lg);X=sc.transform(lg)
 ck('raw_rows',len(d)==541909);ck('missing_id',d.CustomerID.isna().sum()==135080);ck('retained_rows',len(a)==397884);ck('customer_count',len(f)==4338);ck('unique_customer',f.index.is_unique);ck('calendar_min',f.recency.min()==1)
 # Separate Python-date and Decimal arithmetic for every customer; do not round source prices.
 lookup={}
 for row in a.itertuples():
  z=lookup.setdefault(int(row.CustomerID),dict(day=row.InvoiceDate.date(),invoices=set(),money=Decimal('0')))
  z['day']=max(z['day'],row.InvoiceDate.date());z['invoices'].add(row.InvoiceNo);z['money']+=Decimal(str(row.Quantity))*Decimal(str(row.UnitPrice))
 ck('calendar_independent_all',all((pd.Timestamp('2011-12-10').date()-z['day']).days==int(f.loc[c,'recency']) for c,z in lookup.items()))
 ck('distinct_invoices_independent_all',all(len(z['invoices'])==int(f.loc[c,'frequency']) for c,z in lookup.items()))
 ck('money_decimal_independent_all',all(abs(float(z['money'])-f.loc[c,'monetary'])<1e-7 for c,z in lookup.items()))
 old=pd.read_csv(R/'data/pilot_rfm_whole_days.csv').set_index('CustomerID');ck('calendar_vs_whole_days',np.array_equal(f.recency.to_numpy()-old.loc[f.index,'recency'].to_numpy(),np.ones(len(f))))
 ck('scaler_mean',np.allclose(X.mean(axis=0),0,atol=1e-12));ck('scaler_variance',np.allclose(X.var(axis=0),1));ck('J_one_cluster',np.isclose((X**2).sum(),4338*3));ck('transform_inverse',np.allclose(np.expm1(sc.inverse_transform(X)),X0))
 hist=lloyd(P,P[[0,2]]);ck('toy_assign1',hist[0]['labels']==[0,0,1,1,1,1]);ck('toy_J_sequence',np.allclose([h['J'] for h in hist[:4]],[39,12,93/8,22/3]));ck('toy_chi_margin',np.isclose(hist[2]['d2'][2][1]-hist[2]['d2'][2][0],3/8));ck('toy_monotonic',np.all(np.diff([h['J'] for h in hist])<=1e-10));ck('toy_fixed_point',hist[-1]['labels']==hist[-3]['labels']);ck('toy_centers',np.allclose(hist[3]['centers'],[[2,5/3],[6,14/3]]))
 best={i:float('inf') for i in range(1,7)}
 for labels in partitions(6):
  lab=np.array(labels);k=max(labels)+1;cent=np.array([P[lab==j].mean(axis=0) for j in range(k)]);cost=float(((P-cent[lab])**2).sum());best[k]=min(best[k],cost)
 ck('exhaustive_K2',np.isclose(best[2],22/3));ck('exhaustive_K3',np.isclose(best[3],19/6));ck('exhaustive_J_nonincreasing',np.all(np.diff(list(best.values()))<=1e-10));ck('exhaustive_K6_zero',best[6]==0)
 starts=[]
 for ids in itertools.combinations(range(6),3):
  h=lloyd(P,P[list(ids)]);starts.append(dict(initial=list(ids),J=h[-1]['J'],labels=h[-1]['labels']))
 ck('all20_starts',len(starts)==20);ck('different_local_solutions',len(set(round(z['J'],8) for z in starts))>1)
 # One fixed sample across every silhouette comparison. These are exploratory fits, not predictions.
 sample=np.random.RandomState(42).permutation(len(f))[:2000];experiments=[];models={}
 samples={seed:np.random.RandomState(seed).permutation(len(f))[:2000] for seed in [42,43,44]}
 with threadpool_limits(limits=2):
  for k in range(2,7):
   m=KMeans(n_clusters=k,n_init=20,random_state=42,algorithm='lloyd').fit(X);models[k]=m
   sil=float(silhouette_score(X[sample],m.labels_[sample]));experiments.append(dict(k=k,inertia=float(m.inertia_),silhouette=sil,silhouette_subsamples={str(seed):float(silhouette_score(X[ids],m.labels_[ids])) for seed,ids in samples.items()},silhouette_full=float(silhouette_score(X,m.labels_)) if k in [2,4] else None,sizes=np.bincount(m.labels_).tolist(),iterations=int(m.n_iter_)))
   ck(f'K{k}_all_customers',np.bincount(m.labels_).sum()==len(f));ck(f'K{k}_valid_silhouette',-1<=sil<=1)
  raw=KMeans(n_clusters=2,n_init=20,random_state=42,algorithm='lloyd').fit(X0)
  raw_sil=float(silhouette_score(X0[sample],raw.labels_[sample]));raw_full=float(silhouette_score(X0,raw.labels_))
  stable=[]
  for seed in range(12):
   m=KMeans(n_clusters=4,n_init=20,random_state=seed,algorithm='lloyd').fit(X);stable.append(dict(seed=seed,inertia=float(m.inertia_),ARI=float(adjusted_rand_score(models[4].labels_,m.labels_))))
  moons,y=make_moons(n_samples=180,noise=.06,random_state=8);mm=KMeans(n_clusters=2,n_init=20,random_state=42).fit(moons)
 ck('label_permutation_ARI',adjusted_rand_score([0,0,1,1],[8,8,3,3])==1)
 siltoy=silhouette_samples(np.array([[0.],[2.],[10.],[12.]]),[0,0,1,1]);ck('silhouette_hand',np.isclose(siltoy[1],7/9))
 f['cluster_k2']=models[2].labels_;f['cluster_k4']=models[4].labels_;f.reset_index().to_csv(R/'data/retail_rfm.csv',index=False)
 profile=f.groupby('cluster_k4').agg(n=('recency','size'),R=('recency','median'),F=('frequency','median'),M=('monetary','median')).reset_index();profile.to_csv(R/'data/cluster_profiles.csv',index=False)
 # A compact customer with exactly two invoices; keep every retained line for arithmetic.
 exid=int(f[(f.frequency==2)&f.retained_lines.between(4,7)].index[0]);ex=a[a.CustomerID==exid].sort_values(['InvoiceDate','InvoiceNo','StockCode']);ex.to_csv(R/'data/example_customer_lines.csv',index=False)
 ids=[exid]+[int(g.index[0]) for _,g in f.groupby('cluster_k4')]+[int(g.index[-1]) for _,g in f.groupby('cluster_k4')];ids=list(dict.fromkeys(ids));a[a.CustomerID.isin(ids)].sort_values(['CustomerID','InvoiceDate']).to_csv(R/'data/explorer_lines.csv',index=False)
 ck('example_two_invoices',ex.InvoiceNo.nunique()==2);ck('example_rows_exceed_F',len(ex)>2)
 dedup=d.drop_duplicates();ad,fd=prepare(dedup)
 with threadpool_limits(limits=2):
  ds=StandardScaler().fit(np.log1p(fd[['recency','frequency','monetary']].to_numpy()));Xd=ds.transform(np.log1p(fd[['recency','frequency','monetary']].to_numpy()));dm=KMeans(n_clusters=4,n_init=20,random_state=42,algorithm='lloyd').fit(Xd)
 fd['cluster_k4']=dm.labels_
 from scipy.optimize import linear_sum_assignment
 transition=np.zeros((4,4),dtype=int)
 for left,right in zip(f.cluster_k4,fd.cluster_k4):transition[int(left),int(right)]+=1
 rr,cc=linear_sum_assignment(-transition);aligned=transition[:,cc];mapping={int(j):int(i) for i,j in zip(rr,cc)}
 fd['aligned_cluster']=fd.cluster_k4.map(mapping)
 dedup_profile=fd.groupby('aligned_cluster').agg(n=('recency','size'),R=('recency','median'),F=('frequency','median'),M=('monetary','median')).reset_index()
 ck('dedup_customer_count',len(fd)==len(f));ck('dedup_money_not_increase',(fd.monetary<=f.monetary+1e-8).all())
 np.savez_compressed(R/'data/lab_arrays.npz',X=X,X0=X0,log=lg,sample=sample,raw_labels=raw.labels_,labels4=models[4].labels_,centers4=models[4].cluster_centers_,moons=moons,moon_true=y,moon_labels=mm.labels_,moon_centers=mm.cluster_centers_)
 filters=[];mask=np.ones(len(d),dtype=bool)
 for name,ok in [('Có CustomerID',d.CustomerID.notna()),('Quantity > 0',d.Quantity.gt(0)),('UnitPrice > 0',d.UnitPrice.gt(0)),('InvoiceNo không bắt đầu C',~d.InvoiceNo.astype(str).str.lower().str.startswith('c'))]:
  before=mask.sum();mask&=ok.to_numpy();filters.append(dict(rule=name,removed=int(before-mask.sum()),remaining=int(mask.sum())))
 audit=dict(status='pass',checks=checks,checks_count=len(checks),versions=dict(numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__),raw_sha256=sha(R/'data/online_retail.zip'),raw_rows=len(d),retained_rows=len(a),missing_id=int(d.CustomerID.isna().sum()),exact_duplicate_rows=int(d.duplicated().sum()),eligible_duplicate_rows=int(a.duplicated().sum()),customers=len(f),snapshot='2011-12-10',R_definition='calendar days, after normalizing last retained purchase date',filters=filters,example=dict(id=exid,lines=len(ex),last=str(f.loc[exid,'last_date']),R=int(f.loc[exid,'recency']),F=int(f.loc[exid,'frequency']),M=float(f.loc[exid,'monetary'])),toy=dict(points=P.tolist(),names=NAMES,history=hist,global_optima=best,starts_k3=starts),experiments=experiments,raw_k2=dict(silhouette_sample=raw_sil,silhouette_full=raw_full,sizes=np.bincount(raw.labels_).tolist()),stability=stable,profile=profile.to_dict(orient='records'),variance_share=(X0.var(axis=0)/X0.var(axis=0).sum()).tolist(),silhouette_toy=siltoy.tolist(),dedup=dict(retained_rows=len(ad),customers=len(fd),M_total=float(fd.monetary.sum()),M_total_keep=float(f.monetary.sum()),changed_customers=int((abs(fd.monetary-f.monetary)>1e-8).sum()),ARI=float(adjusted_rand_score(f.cluster_k4,fd.cluster_k4)),transition=transition.tolist(),aligned_transition=aligned.tolist(),mapping=mapping,aligned_profiles=dedup_profile.to_dict(orient='records'),inertia=float(dm.inertia_)))
 audit['stability_budget']={'n_init':20,'seeds':list(range(12)),'reference_seed':42,'reference_n_init':20};audit['silhouette_scope']='Primary: within the fixed 2000-customer subset, seed 42; sensitivity seeds 43/44; full-cohort values separately for K=2/4.'
 audit['pipeline']={'log':'natural log(1+x)','scaler_mean':sc.mean_.tolist(),'scaler_scale':sc.scale_.tolist(),'variance_ddof':0,'n_init':20,'random_state':42,'algorithm':'lloyd','init':'k-means++','fitting_scope':'entire exploratory historical cohort, not future validation'}
 example_index=f.index.get_loc(exid);example_x=X[example_index];example_dist=((models[4].cluster_centers_-example_x)**2).sum(1)
 audit['example'].update(raw=X0[example_index].tolist(),log=lg[example_index].tolist(),scaled=example_x.tolist(),d2_k4=example_dist.tolist(),cluster_k4=int(f.loc[exid,'cluster_k4']))
 audit['centers_k4']=models[4].cluster_centers_.tolist();audit['inverse_centers_k4']=np.expm1(sc.inverse_transform(models[4].cluster_centers_)).tolist()
 audit['fractional_penny_price_rows']=int((abs(a.UnitPrice*100-np.round(a.UnitPrice*100))>1e-8).sum())
 ck('dedup_transition_all',int(transition.sum())==4338);ck('full_silhouette_scopes',all(e['silhouette_full'] is not None for e in experiments if e['k'] in [2,4]));ck('stability_equal_budget',audit['stability_budget']['n_init']==20);audit['checks_count']=len(checks)
 dump('results/case_audit.json',audit);dump('results/preparation_checks.json',dict(status='pass',calendar_days_all_customers=True,distinct_invoices_all_customers=True,decimal_money_all_customers=True,source_sha256=audit['raw_sha256'],rows=len(f),definition_changed_from_pilot='R calendar = prior whole-day R + 1 for all 4338; all model results recalculated'))
 print(json.dumps({k:audit[k] for k in ['status','checks_count','example','experiments','raw_k2','exact_duplicate_rows','dedup']},ensure_ascii=False));return audit
if __name__=='__main__':run()
