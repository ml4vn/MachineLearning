"""Reproduce the frozen SMS experiment. Paths are relative to this self-contained package."""
from pathlib import Path
import os,sys,json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[1]
extra=R/'.build/pydeps'
if extra.exists():sys.path.insert(0,str(extra))
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,f1_score
from threadpoolctl import threadpool_limits
FEATURES=['n_chars','digit_fraction']
def load_data():
 with zipfile.ZipFile(R/'data/sms.zip') as z:
  d=pd.read_csv(io.BytesIO(z.read('SMSSpamCollection')),sep='\t',names=['label','text'],quoting=3)
 d['source_record']=np.arange(1,len(d)+1)
 d['normal']=d.text.str.replace(r'\s+',' ',regex=True).str.strip().str.casefold()
 assert d.groupby('normal').label.nunique().max()==1
 d=d.drop_duplicates('normal').reset_index(drop=True)
 d['message_id']=d.normal.map(lambda t:hashlib.sha256(t.encode()).hexdigest())
 d['y']=(d.label=='spam').astype(int);d['n_chars']=d.text.str.len();d['n_digits']=d.text.map(lambda t:sum(c.isdigit() for c in t));d['digit_fraction']=d.n_digits/d.n_chars
 tr,o=train_test_split(d.index,test_size=.4,stratify=d.y,random_state=42)
 va,te=train_test_split(o,test_size=.5,stratify=d.loc[o,'y'],random_state=42)
 d['split']='train';d.loc[va,'split']='validation';d.loc[te,'split']='test'
 return d,tr,va,te
def run():
 d,tr,va,te=load_data();X=d.loc[tr,FEATURES].to_numpy();y=d.loc[tr,'y'].to_numpy();sc=StandardScaler().fit(X);Z=sc.transform(X)
 checks={}
 def ck(name,ok):checks[name]=bool(ok);assert ok,name
 ck('row_count',len(d)==5159);ck('split_counts',list(map(len,[tr,va,te]))==[3095,1032,1032]);ck('no_overlap',len(set(tr)&set(va))==len(set(tr)&set(te))==len(set(va)&set(te))==0)
 ck('all_nonempty',d.n_chars.min()>0);ck('ratios_in_range',d.digit_fraction.between(0,1).all())
 expected=json.loads((R/'results/case_audit.json').read_text(encoding='utf-8'))
 ck('train_mean',np.allclose(sc.mean_,expected['train_mean']));ck('train_scale',np.allclose(sc.scale_,expected['train_scale_ddof0']))
 ck('scale_unit_invariance',np.allclose(StandardScaler().fit_transform(X*np.array([1,100])),Z))
 models={};val=[]
 with threadpool_limits(limits=2):
  for scaled in [False,True]:
   for k in [3,5,11]:
    m=KNeighborsClassifier(n_neighbors=k).fit(Z if scaled else X,y);models[(scaled,k)]=m
    xv=d.loc[va,FEATURES].to_numpy();pred=m.predict(sc.transform(xv) if scaled else xv)
    score=f1_score(d.loc[va,'y'],pred);old=next(t for t in expected['validation_configurations'] if t['k']==k and t['scaled']==scaled)
    ck(f'validation_{scaled}_{k}',np.isclose(score,old['validation_f1']) and int((pred!=d.loc[va,'y']).sum())==old['wrong']);val.append(dict(scaled=scaled,k=k,f1=float(score),errors=int((pred!=d.loc[va,'y']).sum())))
  core=models[(True,11)];xt=sc.transform(d.loc[te,FEATURES].to_numpy());pred=core.predict(xt);score=core.predict_proba(xt)[:,1]
  saved=pd.read_csv(R/'data/sms_core_test_predictions.csv').set_index('message_id').loc[d.loc[te,'message_id']]
  ck('test_prediction_unchanged',np.array_equal(pred,saved.prediction));ck('test_score_unchanged',np.allclose(score,saved.neighbor_vote_fraction));ck('test_truth_unchanged',np.array_equal(d.loc[te,'y'],saved.y))
  cm=confusion_matrix(d.loc[te,'y'],pred,labels=[0,1]);ck('confusion_matrix',np.array_equal(cm,[[892,12],[17,111]]))
  demo={};q=d.loc[d.source_record==4500,FEATURES].to_numpy()
  for scaled in [False,True]:
   a=sc.transform(q)[0] if scaled else q[0];t=Z if scaled else X;dd=((t-a)**2).sum(1);idx=np.argsort(dd,kind='stable')[:3];dist,indices=models[(scaled,3)].kneighbors(a[None,:])
   ck(f'manual_neighbors_{scaled}',set(idx)==set(indices[0]));ck(f'manual_distance_{scaled}',np.allclose(np.sort(dd[idx]),np.sort(dist[0]**2)))
   vote=int(y[idx].sum()>1);ck(f'manual_vote_{scaled}',vote==models[(scaled,3)].predict(a[None,:])[0]);demo[str(scaled)]=dict(ids=d.loc[tr[idx],'source_record'].tolist(),prediction=vote)
 P=np.array([[0,0],[2,0],[0,3],[4,4],[1,4]])
 ck('toy_distances',np.array_equal(((P-[1,1])**2).sum(1),[2,2,5,18,9]));ck('exit_distances',np.array_equal(((P-[2,1])**2).sum(1),[5,1,8,13,10]));ck('far_query',np.array_equal(((P-[12,12])**2).sum(1),[288,244,225,128,185]));ck('zero_distance_exists',((P-P[0])**2).sum(1)[0]==0)
 result=dict(status='pass',checks_count=len(checks),checks=checks,validation=val,test_confusion_matrix=cm.tolist(),query_demo=demo,scaler_mean=sc.mean_.tolist(),scaler_scale=sc.scale_.tolist(),versions={'python':sys.version.split()[0],'numpy':np.__version__,'sklearn':__import__('sklearn').__version__})
 (R/'results/lab_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result
def audit():
 a=run();checks=a['checks']
 def ck(name,ok):checks[name]=bool(ok);assert ok,name
 d,tr,va,te=load_data();X=d.loc[tr,FEATURES].to_numpy();y=d.loc[tr,'y'].to_numpy();sc=StandardScaler().fit(X);Z=sc.transform(X)
 with zipfile.ZipFile(R/'data/sms.zip') as z:
  raw=pd.read_csv(io.BytesIO(z.read('SMSSpamCollection')),sep='\t',names=['label','text'],quoting=3)
 raw['normal']=raw.text.str.replace(r'\s+',' ',regex=True).str.strip().str.casefold()
 ck('raw_5574_4827_ham_747_spam',len(raw)==5574 and raw.label.value_counts().to_dict()=={'ham':4827,'spam':747})
 ck('no_conflicting_duplicate_labels',raw.groupby('normal').label.nunique().max()==1)
 ck('dedup_removes_415',len(raw)-len(d)==415)
 ck('dedup_4517_ham_642_spam',d.label.value_counts().to_dict()=={'ham':4517,'spam':642})
 ck('no_normalized_text_overlap',not(set(d.loc[tr,'normal'])&set(d.loc[va,'normal']) or set(d.loc[tr,'normal'])&set(d.loc[te,'normal']) or set(d.loc[va,'normal'])&set(d.loc[te,'normal'])))
 saved=pd.read_csv(R/'data/sms_features.csv').set_index('message_id');joined=d.set_index('message_id').loc[saved.index]
 ck('all_saved_ids_splits_and_features',set(saved.index)==set(d.message_id) and (joined.split==saved.split).all() and np.allclose(joined[FEATURES],saved[FEATURES],rtol=0,atol=1e-15))
 ck('all_feature_counts_from_original_text',all(len(t)==c and sum(ch.isdigit() for ch in t)==nd for t,c,nd in zip(d.text,d.n_chars,d.n_digits)))
 ck('scaler_ddof0',np.allclose(sc.scale_,X.std(axis=0,ddof=0)))
 ck('train_z_mean_zero_std_one',np.allclose(Z.mean(0),0,atol=1e-12) and np.allclose(Z.std(0),1,atol=1e-12))
 ck('validation_not_forced_to_zero_mean',not np.allclose(sc.transform(d.loc[va,FEATURES].to_numpy()).mean(0),0,atol=1e-4))
 Q=np.array([80,80,120,120.],float);ck('toy_train_mu100_sigma20_ddof0',Q.mean()==100 and Q.std(ddof=0)==20)
 ck('toy_z_values',np.array_equal((np.array([80,110,120])-100)/20,[-1,.5,1]))
 ck('centering_cancels_in_distance',np.allclose(Z[0]-Z[1],(X[0]-X[1])/sc.scale_))
 const=StandardScaler().fit([[5,1],[5,3]]);ck('constant_column_no_divide_by_zero',const.scale_[0]==1 and np.array_equal(const.transform([[5,1],[5,3]])[:,0],[0,0]))
 ck('z_not_limited_to_zero_one',Z.min()<0 and Z.max()>1)
 # A change of units alone reverses the nearest neighbor in raw coordinates.
 q=np.array([100,.1]);p=np.array([[101,.1],[100,.2]])
 ck('unit_change_reverses_raw_neighbor',np.argmin(((p-q)**2).sum(1))==1 and np.argmin((((p-q)*[1,100])**2).sum(1))==0)
 P=np.array([[0,0],[2,0],[0,3],[4,4],[1,4]],float);Y=np.array([0,1,1,0,0]);dd=((P-[1,1])**2).sum(1)
 ck('sqrt_preserves_nonnegative_rank',np.array_equal(np.argsort(dd,kind='stable'),np.argsort(np.sqrt(dd),kind='stable')))
 ck('toy_k3_spam_k5_ham',Y[np.argsort(dd,kind='stable')[:3]].sum()==2 and Y.sum()==2)
 ck('exit_ticket_top3_spam',np.argsort(((P-[2,1])**2).sum(1),kind='stable')[:3].tolist()==[1,0,2])
 ck('odd_k_multiclass_tie_exists',max(np.bincount([0,0,1,1,2]))==2)
 # A concrete counterexample in the already published test snapshot: unanimous
 # neighbor votes can still disagree with the source label. This does not retune
 # or select a configuration using test; it verifies a limit of interpretation.
 snapshot=pd.read_csv(R/'data/sms_core_test_predictions.csv')
 unanimous_error=(snapshot.neighbor_vote_fraction.isin([0,1]) & (snapshot.prediction!=snapshot.y))
 ck('vote_fraction_not_label_guarantee',bool(unanimous_error.any()))
 rows=[]
 with threadpool_limits(limits=2):
  for scaled in [False,True]:
   for k in [3,5,11]:
    m=KNeighborsClassifier(n_neighbors=k).fit(Z if scaled else X,y);V=d.loc[va,FEATURES].to_numpy();pv=m.predict(sc.transform(V) if scaled else V)
    cm=confusion_matrix(d.loc[va,'y'],pv,labels=[0,1]);tn,fp,fn,tp=map(int,cm.ravel());manual=2*tp/(2*tp+fp+fn)
    ck(f'independent_f1_count_formula_{scaled}_{k}',abs(manual-f1_score(d.loc[va,'y'],pv))<1e-12)
    rows.append(dict(scaled=scaled,k=k,tn=tn,fp=fp,fn=fn,tp=tp,errors=fp+fn,f1=manual))
 ck('same_query4500_positive_distances_no_boundary_tie',all((lambda dx:dx[0]>0 and dx[2]<dx[3])(np.sort(((T-A)**2).sum(1))) for T,A in [(X,d.loc[d.source_record==4500,FEATURES].to_numpy()[0]),(Z,sc.transform(d.loc[d.source_record==4500,FEATURES].to_numpy())[0])]))
 qrow=d.loc[d.source_record==4500].iloc[0];ck('query_123_chars_14_digits',qrow.n_chars==123 and qrow.n_digits==14 and np.isclose(qrow.digit_fraction,14/123))
 # Compare all feature scales and the full test snapshot, never retune with test.
 frozen=json.loads((R/'results/case_audit_frozen.json').read_text(encoding='utf8'))
 ck('raw_zip_and_text_sha_preserved',hashlib.sha256((R/'data/sms.zip').read_bytes()).hexdigest()==frozen['raw_sha256'] and hashlib.sha256((R/'data/SMSSpamCollection').read_bytes()).hexdigest()==frozen['text_file_sha256'])
 a.update(checks_count=len(checks),validation_counts=rows,raw_rows=len(raw),deduplicated_rows=len(d),runtime_pandas=pd.__version__,frozen_test_policy='Reproduce the already published  snapshot; do not retune using test.')
 (R/'results/lab_checks.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
 (R/'results/validation_counts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 return a
if __name__=='__main__':
 a=audit();print(json.dumps({k:a[k] for k in ['status','checks_count','test_confusion_matrix','query_demo','versions']},ensure_ascii=False))
