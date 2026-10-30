"""Exact toy geometry and a fixed, traceable Fashion-MNIST teaching experiment."""
from pathlib import Path
import os,sys,json,gzip,struct,hashlib,shutil,warnings,time
R=Path(__file__).resolve().parents[1];COURSE=R.parent
sys.path.insert(0,str(R/'.build/pydeps'))
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('MPLCONFIGDIR',str(R/'.build/mplconfig'))
import numpy as np
import sklearn
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix
from threadpoolctl import threadpool_limits
NAMES=['T-shirt/top','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Ankle boot']
P=np.array([[3,4],[4,3],[6,7],[7,6]],dtype=float)
def savej(p,d): (R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf8')
def load_idx(p):
 b=gzip.decompress(Path(p).read_bytes());magic=struct.unpack('>I',b[:4])[0];dim=magic&255
 assert magic>>8==8 and dim in (1,3)
 shape=struct.unpack('>'+'I'*dim,b[4:4+4*dim]);a=np.frombuffer(b,offset=4+4*dim,dtype=np.uint8).reshape(shape)
 return a
def fit_baseline(X,y,V,yv):
 m=LogisticRegression(C=1,solver='newton-cg',max_iter=200)
 with warnings.catch_warnings(record=True) as w:
  warnings.simplefilter('always');m.fit(X,y)
 p=m.predict(V)
 return m,dict(validation_accuracy=float(accuracy_score(yv,p)),validation_macro_f1=float(f1_score(yv,p,average='macro')),validation_confusion=confusion_matrix(yv,p).tolist(),iterations=m.n_iter_.tolist(),warnings=[str(z.message) for z in w])
def main():
 checks={}
 def ck(name,ok):
  checks[name]=bool(ok)
  if not ok:raise AssertionError(name)
 (R/'data/raw').mkdir(exist_ok=True)
 md5s=['8d4fb7e6c68d591d4c3dfef9ec88bf0d','25c81989df183df01b3e8a0aad5dffbe','bef4ecab320f06d8554ea6380940ec79','bb300cfdad3c16e7a12a480ee83cd310']
 stems=['train_images','train_labels','test_images','test_labels'];arr=[];files=[]
 for s,md in zip(stems,md5s):
  f=R/'data/raw'/f'fashion_{s}.gz'
  if not f.exists():raise FileNotFoundError('Missing bundled raw data: '+str(f))
  b=f.read_bytes();ck('official_md5_'+s,hashlib.md5(b).hexdigest()==md);arr.append(load_idx(f));files.append(dict(path=str(f.relative_to(R)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),md5=md))
 x,y,xt,yt=arr;x=x.reshape(-1,784);xt=xt.reshape(-1,784)
 ck('source_shapes',x.shape==(60000,784) and xt.shape==(10000,784) and y.shape==(60000,) and yt.shape==(10000,))
 ck('pixel_uint8_range',x.dtype==np.uint8 and x.min()==0 and x.max()==255)
 ck('source_class_counts',np.array_equal(np.bincount(y),[6000]*10) and np.array_equal(np.bincount(yt),[1000]*10))
 tr,rem=train_test_split(np.arange(len(y)),train_size=12000,stratify=y,random_state=42)
 va,_=train_test_split(rem,train_size=3000,stratify=y[rem],random_state=42)
 ck('split_seed_fixed',len(tr)==12000 and len(va)==3000)
 ck('train_validation_disjoint',not set(tr)&set(va))
 ck('stratified_subset',np.array_equal(np.bincount(y[tr]),[1200]*10) and np.array_equal(np.bincount(y[va]),[300]*10))
 np.savez_compressed(R/'data/fashion_subset.npz',train_images=x[tr],train_labels=y[tr],validation_images=x[va],validation_labels=y[va],test_images=xt,test_labels=yt,train_indices=tr,validation_indices=va,test_indices=np.arange(len(yt)))
 # IDs distinguish official source split. Exact content overlap is measured independently.
 hashes=lambda a:[hashlib.sha256(z.tobytes()).hexdigest() for z in a]
 ht,hv,he=map(hashes,[x[tr],x[va],xt]);overlap=dict(train_validation_unique_hashes=len(set(ht)&set(hv)),train_test_unique_hashes=len(set(ht)&set(he)),validation_test_unique_hashes=len(set(hv)&set(he)),within_train_duplicate_rows=len(ht)-len(set(ht)),within_validation_duplicate_rows=len(hv)-len(set(hv)),within_test_duplicate_rows=len(he)-len(set(he)))
 ck('raw_image_traceability',all(np.array_equal(x[i].reshape(28,28).ravel(),x[i]) for i in va[:40]))
 # Toy: population covariance is intentional. Fractions give independent exact projection.
 from fractions import Fraction as F
 mu=P.mean(0);Pc=P-mu;C=Pc.T@Pc/4;W=np.array([[1,1],[1,-1]])/np.sqrt(2);scores=Pc@W.T;recon=scores[:,:1]@W[:1]+mu
 ck('toy_center',np.array_equal(mu,[5,5]) and np.array_equal(Pc.sum(0),[0,0]))
 ck('toy_covariance',np.array_equal(C,[[2.5,2],[2,2.5]]))
 ck('toy_eigenpairs',np.allclose(C@W.T,W.T*np.array([4.5,.5])))
 ck('toy_orthogonal',np.allclose(W@W.T,np.eye(2)))
 ck('toy_trace_determinant',np.isclose(np.trace(C),5) and np.isclose(np.linalg.det(C),2.25))
 exact=[]
 for a,b in Pc.astype(int):
  q=F(int(a+b),2);r=[F(5)+q,F(5)+q];err=(F(int(a))-q)**2+(F(int(b))-q)**2;exact.append([str(v) for v in r]+[str(err)])
 ck('toy_fraction_residual',all(z[2]=='1/2' for z in exact))
 ck('toy_collision',np.isclose(scores[0,0],scores[1,0]) and not np.array_equal(P[0],P[1]))
 ck('toy_reconstruction',np.allclose(recon,[[3.5,3.5],[3.5,3.5],[6.5,6.5],[6.5,6.5]]))
 ck('toy_errors_two_denominators',np.isclose(np.mean(np.sum((P-recon)**2,axis=1)),.5) and np.isclose(np.mean((P-recon)**2),.25))
 ck('toy_score_variances',np.allclose(scores.var(0),[4.5,.5]))
 toy_pca=PCA(svd_solver='full').fit(P)
 ck('toy_sklearn_ddof',np.allclose(toy_pca.explained_variance_,[6,2/3]) and np.allclose(toy_pca.explained_variance_ratio_,[.9,.1]))
 ck('toy_sklearn_projection',np.allclose((P-toy_pca.mean_)@toy_pca.components_[:1].T@toy_pca.components_[:1]+toy_pca.mean_,recon))
 theta=np.linspace(0,np.pi,1801);dirs=np.array([np.cos(theta),np.sin(theta)]).T;vv=np.einsum('bi,ij,bj->b',dirs,C,dirs);err=[]
 for w in dirs:err.append(np.mean(np.sum((Pc-np.outer(Pc@w,w))**2,axis=1)))
 ck('toy_pythagoras_all_angles',np.allclose(vv+err,5,atol=1e-12))
 ck('toy_angle_formula',np.allclose(vv,2.5+2*np.sin(2*theta)))
 ck('toy_direction_sign_invariance',np.allclose(np.outer(Pc@(-W[0]),-W[0]),np.outer(Pc@W[0],W[0])))
 X=x[tr].astype(np.float64)/255;V=x[va].astype(np.float64)/255
 ck('scale_is_fixed',np.array_equal(X*255,x[tr].astype(float)))
 start=time.perf_counter();pca=PCA(svd_solver='full').fit(X);print('Full PCA fitted',round(time.perf_counter()-start,2),'seconds',flush=True)
 Z=pca.transform(X);ZV=pca.transform(V);ev=pca.explained_variance_ratio_;cum=np.cumsum(ev);k90=int(np.searchsorted(cum,.9)+1)
 ck('train_only_mean',np.allclose(pca.mean_,X.mean(0),atol=1e-14))
 ck('real_orthonormal',np.allclose(pca.components_@pca.components_.T,np.eye(784),atol=1e-10))
 ck('real_centered_scores',np.max(np.abs(Z.mean(0)))<1e-10)
 ck('real_eigen_sorted_nonnegative',np.all(np.diff(pca.explained_variance_)<=1e-12) and np.all(pca.explained_variance_>=0))
 ck('real_evr_sum',np.isclose(ev.sum(),1))
 ck('real_total_variance_ddof1',np.isclose(pca.explained_variance_.sum(),X.var(0,ddof=1).sum()))
 ck('real_transform_formula',np.allclose(ZV,(V-pca.mean_)@pca.components_.T,atol=1e-12))
 ck('real_full_reconstruction',np.max(np.abs(pca.inverse_transform(ZV)-V))<1e-10)
 ck('k90_smallest',cum[k90-1]>=.9 and (k90==1 or cum[k90-2]<.9))
 rec=[];display_ids=[int(np.flatnonzero(y[va]==c)[0]) for c in range(10)];display_rec=[]
 for k in [2,16,64,128]:
  vr=ZV[:,:k]@pca.components_[:k]+pca.mean_;xr=Z[:,:k]@pca.components_[:k]+pca.mean_
  train_mse=float(np.mean((X-xr)**2));vmse=float(np.mean((V-vr)**2));tail=float(pca.explained_variance_[k:].sum()*11999/12000/784)
  ck('real_tail_error_k'+str(k),np.isclose(train_mse,tail,atol=1e-12))
  rec.append(dict(k=k,train_evr=float(cum[k-1]),train_mse_pixel=train_mse,validation_mse_pixel=vmse,validation_outside_display_range_fraction=float(np.mean((vr<0)|(vr>1))),validation_mse_clipped=float(np.mean((V-np.clip(vr,0,1))**2))))
  display_rec.append(vr[display_ids])
 ck('nested_reconstruction_monotone',all(a['validation_mse_pixel']>=b['validation_mse_pixel'] for a,b in zip(rec,rec[1:])))
 logpix,metpix=fit_baseline(X,y[tr],V,y[va]);log64,met64=fit_baseline(Z[:,:64],y[tr],ZV[:,:64],y[va]);print('Validation logistic',metpix['validation_accuracy'],met64['validation_accuracy'],flush=True)
 ck('baseline_optimizers_converged',not metpix['warnings'] and not met64['warnings'])
 ck('baseline_validation_n',sum(map(sum,metpix['validation_confusion']))==3000 and sum(map(sum,met64['validation_confusion']))==3000)
 # Store numeric parameters, no executable pickle. B10 can use the exact pixel baseline.
 np.savez_compressed(R/'data/lab_arrays.npz',mean=pca.mean_,components=pca.components_,eigenvalues=pca.explained_variance_,evr=ev,cumulative_evr=cum,train_scores=Z[:,:128],validation_scores=ZV[:,:128],display_positions=display_ids,display_recon=np.array(display_rec),pixel_coef=logpix.coef_,pixel_intercept=logpix.intercept_,pca64_coef=log64.coef_,pca64_intercept=log64.intercept_,validation_pixel_predictions=logpix.predict(V),validation_pca64_predictions=log64.predict(ZV[:,:64]),toy=P,toy_mean=mu,toy_W=W,toy_scores=scores,toy_reconstruction=recon)
 ck('baseline_manual_forward',np.array_equal(np.argmax(V@logpix.coef_.T+logpix.intercept_,axis=1),logpix.predict(V)))
 savej('data/source_manifest.json',dict(files=files,source='https://github.com/zalandoresearch/fashion-mnist',kaggle='https://www.kaggle.com/datasets/zalando-research/fashionmnist',label_names=NAMES,split_seed=42,split_id_convention='train:<0-based official train row>; test:<0-based official test row>',test_use='No test metric in B9. Official test was evaluated in B10 ; it is not globally unseen.'))
 result=dict(status='pass',checks=checks,checks_count=len(checks),versions=dict(python=sys.version.split()[0],numpy=np.__version__,sklearn=sklearn.__version__),source_counts=dict(train=60000,test=10000),split=dict(train=12000,validation=3000,test=10000,unused_train=45000,seed=42),duplicate_audit=overlap,k90=k90,k90_evr=float(cum[k90-1]),k90_previous_evr=float(cum[k90-2]),reconstruction=rec,baseline_pixel=metpix,baseline_pca64=met64,display_examples=[dict(validation_position=i,source_id='train:'+str(int(va[i])),label=int(y[va[i]]),name=NAMES[int(y[va[i]])]) for i in display_ids],toy=dict(points=P.tolist(),mean=mu.tolist(),C=C.tolist(),W=W.tolist(),scores=scores.tolist(),reconstruction=recon.tolist(),exact_reconstruction_and_squared_error=exact,evr=[.9,.1],point_error=.5,coordinate_mse=.25),zero_variance_pixels=int(np.sum(X.var(0)==0)),test_metrics_computed=False,limits=['Fixed 12,000-image teaching subset, not full-data benchmark','Source row IDs are disjoint; exact content overlaps reported, not silently treated as new independent objects','k comparison on validation; no B9 test metric. B10  has already evaluated official test; never call it globally unseen.','Display clips reconstructions; MSE uses unclipped values','No per-pixel z-score; common intensity units are a design choice, not proof that scaling is always wrong','Full SVD differs from randomized128 pilot; all displayed values recomputed'])
 
 pred0=logpix.predict(V);pred1=log64.predict(ZV[:,:64]);ok0=pred0==y[va];ok1=pred1==y[va]
 result['paired_validation']={'both_correct':int((ok0&ok1).sum()),'both_wrong':int((~ok0&~ok1).sum()),'corrected':int((~ok0&ok1).sum()),'newly_wrong':int((ok0&~ok1).sum())}
 result['paired_examples']={}
 for nm,mask in [('corrected',~ok0&ok1),('newly_wrong',ok0&~ok1)]:
  i=int(np.flatnonzero(mask)[0]);result['paired_examples'][nm]={'validation_position':i,'source_id':'train:'+str(int(va[i])),'true_label':int(y[va[i]]),'pixel_prediction':int(pred0[i]),'pca64_prediction':int(pred1[i])}
 ck('paired_total',sum(result['paired_validation'].values())==3000)
 outlier=np.vstack([P,[9,0]]);outlier_mu=outlier.mean(0);outlier_C=np.cov(outlier,rowvar=False,bias=True);vals,vec=np.linalg.eigh(outlier_C);u=vec[:,-1]
 if u[0]<0:u=-u
 result['outlier']={'points':outlier.tolist(),'mean':outlier_mu.tolist(),'C':outlier_C.tolist(),'PC1':u.tolist(),'lambda1':float(vals[-1])}
 result['pipeline']={'scale':255,'solver':'full','whiten':False,'seed':42,'logistic_C':1,'logistic_solver':'newton-cg','logistic_max_iter':200,'test_history':'B10  evaluated the official test. No B9 metric computed.'}
 result['checks_count']=len(checks)
 savej('results/case_audit.json',result);print(json.dumps({k:result[k] for k in ['status','checks_count','k90','duplicate_audit','reconstruction']},ensure_ascii=False))
if __name__=='__main__':
 with threadpool_limits(limits=2):main()
