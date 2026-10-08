"""Fixed protocol, exact teaching anchors and fully traceable neural-network experiment."""
from pathlib import Path
import sys,os,json,hashlib,shutil,time,copy,warnings
R=Path(__file__).resolve().parents[1];COURSE=R.parent
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('MPLCONFIGDIR',str(R/'.build/mplconfig'))
import numpy as np
import sklearn
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix,f1_score
from threadpoolctl import threadpool_limits
NAMES=['T-shirt/top','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Ankle boot']
XOR=np.array([[0,0],[0,1],[1,0],[1,1]],float);YOR=np.array([0,1,1,0])
def savej(name,a):(R/name).write_text(json.dumps(a,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf8')
def sigmoid(z):return np.exp(-np.logaddexp(0,-np.asarray(z)))
def softmax(z):
 z=z-z.max(axis=-1,keepdims=True);a=np.exp(z);return a/a.sum(axis=-1,keepdims=True)
def ce_logits(z,y):return float(np.mean(np.logaddexp.reduce(z,axis=1)-z[np.arange(len(y)),y]))
def bce(s,y):return float(np.mean(np.logaddexp(0,s)-y*s))
def finite(fun,theta,eps=1e-6):
 g=[]
 for i in range(len(theta)):
  e=np.zeros_like(theta);e[i]=eps;g.append((fun(theta+e)-fun(theta-e))/(2*eps))
 return np.array(g)
def tiny_forward(t):
 x=np.array([.6,.2]);W=t[:4].reshape(2,2);b=t[4:6];v=t[6:8];c=t[8]
 a=W@x+b;h=np.maximum(a,0);s=float(v@h+c);p=float(sigmoid(s));d=p-1;dh=d*v*(a>0)
 g=np.r_[np.outer(dh,x).ravel(),dh,d*h,d]
 return dict(x=x,z=a,h=h,s=s,p=p,loss=bce(s,1),delta=d,delta_hidden=dh,gradient=g)
def forward(X,W1,b1,W2,b2):
 h=np.maximum(X@W1+b1,0);s=h@W2+b2;return h,s,softmax(s)
def score(z,y):
 pred=z.argmax(1);cm=confusion_matrix(y,pred,labels=np.arange(10));hits=int((pred==y).sum())
 return dict(n=len(y),correct=hits,accuracy=hits/len(y),cross_entropy=ce_logits(z,y),macro_f1=float(f1_score(y,pred,average='macro')),confusion=cm.tolist(),recall=(cm.diagonal()/cm.sum(1)).tolist())
def load_inputs():
 # The delivered lesson carries the exact B9 reference, so a source ZIP is self-contained.
 snapshot=R/'data/bai09_reference.npz';reference=R/'data/bai09_reference.json'
 if snapshot.exists() and reference.exists():
  old=json.loads(reference.read_text(encoding='utf8'))
  assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==old['reference_sha256']
  return np.load(R/'data/fashion_subset.npz'),np.load(snapshot),old,old['subset_sha256']
 raise FileNotFoundError('Keep data/fashion_subset.npz and the bundled bai09_reference.npz/json alongside this source file. Extract the complete teaching package before running.')
def main():
 if (R/'results/case_audit.json').exists() and '--force' not in sys.argv:
  print('Existing completed experiment preserved; --force explicitly reruns protocol.');return
 checks={}
 def ck(k,v):
  checks[k]=bool(v)
  if not v:raise AssertionError(k)
 D,A,old,subset_sha=load_inputs()
 ck('subset_bytes_identical_B9',hashlib.sha256((R/'data/fashion_subset.npz').read_bytes()).hexdigest()==subset_sha)
 ck('train_validation_disjoint',not set(D['train_indices'])&set(D['validation_indices']))
 ck('split_shapes',D['train_images'].shape==(12000,784) and D['validation_images'].shape==(3000,784) and D['test_images'].shape==(10000,784))
 ck('label_counts',np.array_equal(np.bincount(D['train_labels']),[1200]*10) and np.array_equal(np.bincount(D['validation_labels']),[300]*10) and np.array_equal(np.bincount(D['test_labels']),[1000]*10))
 ck('raw_uint8',D['train_images'].dtype==np.uint8 and D['train_images'].min()==0 and D['train_images'].max()==255)
 ck('B9_content_overlap_zero',all(v==0 for v in old['duplicate_audit'].values()))
 H=np.c_[np.maximum(XOR.sum(1),0),np.maximum(XOR.sum(1)-1,0)];theta=np.zeros(3)
 loss=lambda t:bce(H@t[:2]+t[2],YOR)
 p=sigmoid(H@theta[:2]+theta[2]);d=p-YOR;g=np.r_[H.T@d/4,d.mean()];nextt=theta-8*g;target=np.array([2,-4,-1.])
 cov=((H-H.mean(0))*(YOR-YOR.mean())[:,None]).mean(0)
 ck('toy_hidden_exact',np.array_equal(H,[[0,0],[1,0],[1,0],[2,1]]))
 ck('relu_negative_vs_zero',int((XOR.sum(1)-1<0).sum())==1 and int((XOR.sum(1)-1==0).sum())==2)
 ck('initial_probability',np.all(p==.5));ck('initial_loss',np.isclose(loss(theta),np.log(2)))
 ck('gradient_exact',np.array_equal(g,[0,.125,0]));ck('output_finite_difference',np.allclose(g,finite(loss,theta),atol=1e-9))
 ck('first_update',np.array_equal(nextt,[0,-1,0]));ck('first_loss_formula',np.isclose(loss(nextt),(3*np.log(2)+np.logaddexp(0,-1))/4))
 ck('descent_first_step',loss(nextt)<loss(theta));ck('target_logits',np.array_equal(H@target[:2]+target[2],[-1,1,1,-1]))
 ck('target_hits',int(((H@target[:2]+target[2]>=0)==YOR).sum())==4)
 ck('target_loss',np.isclose(loss(target),np.logaddexp(0,-1)))
 ck('covariance_exact',np.array_equal(cov,[0,-.125]));ck('covariance_gradient_balanced',np.array_equal(g[:2],-cov))
 yu=np.array([0,1,1,1]);gu=H.T@(.5-yu)/4;cu=((H-H.mean(0))*(yu-yu.mean())[:,None]).mean(0)
 ck('covariance_general_identity',np.allclose(gu,-cu+(.5-yu.mean())*H.mean(0)))
 ck('covariance_counterexample',not np.allclose(gu,-cu))
 ck('uniform_loss_unbalanced',np.isclose(bce(np.zeros(4),yu),np.log(2)))
 rng=np.random.RandomState(10);w=rng.normal(size=(20000,3));vals=np.c_[XOR,np.ones(4)]@w.T
 ck('affine_identity',np.allclose(vals[0]+vals[3],vals[1]+vals[2]))
 ck('sampled_affine_at_most_three',int(((vals>=0)==YOR[:,None]).sum(0).max())==3)
 ck('explicit_affine_three',int(((XOR.sum(1)-.5>=0)==YOR).sum())==3)
 tt=np.array([.5,-.4,.3,.8,.1,.1,.7,-.5,.2]);tiny=tiny_forward(tt);fn=finite(lambda z:tiny_forward(z)['loss'],tt)
 ck('tiny_away_from_kink',np.min(np.abs(tiny['z']))>.3);ck('tiny_logits',np.isclose(tiny['s'],.204))
 ck('full_backprop_finite_difference',np.allclose(tiny['gradient'],fn,rtol=1e-7,atol=1e-9))
 ck('full_network_descent',tiny_forward(tt-.1*tiny['gradient'])['loss']<tiny['loss'])
 ck('toy_permutation_invariant',np.allclose(H[:,::-1]@target[:2][::-1]+target[2],H@target[:2]+target[2]))
 ck('toy_positive_scale_same_decisions',np.array_equal(H@target[:2]+target[2]>=0,H@(target[:2]*10)+target[2]*10>=0))
 ck('same_accuracy_different_loss',loss(target*10)<loss(target))
 W1=rng.normal(size=(3,5));W2=rng.normal(size=(5,2));b1=rng.normal(size=5);b2=rng.normal(size=2);xx=rng.normal(size=(200,3))
 ck('affine_composition',np.allclose((xx@W1+b1)@W2+b2,xx@(W1@W2)+(b1@W2+b2)))
 zz=np.array([[1000,1001,999.]])
 ck('stable_softmax',np.all(np.isfinite(softmax(zz))) and np.isclose(softmax(zz).sum(),1))
 ck('softmax_shift',np.allclose(softmax(zz),softmax(zz-1000)))
 ck('uniform_ten_CE',np.isclose(ce_logits(np.zeros((4,10)),np.array([0,3,3,8])),np.log(10)))
 X=D['train_images'].astype(float)/255;V=D['validation_images'].astype(float)/255;y=D['train_labels'];yv=D['validation_labels']
 baseline=V@A['pixel_coef'].T+A['pixel_intercept'];base=score(baseline,yv)
 ck('baseline_predictions_identical_B9',np.array_equal(baseline.argmax(1),A['validation_pixel_predictions']))
 ck('baseline_accuracy_identical_B9',base['accuracy']==old['baseline_pixel']['validation_accuracy'])
 protocol=dict(train=12000,validation=3000,test=10000,pixels='uint8 / 255 to float64',hidden=64,activation='relu',solver='adam',learning_rate=.001,alpha=.0001,batch_size=256,epochs=50,seeds=[42,43,44],primary_seed=42,selection='minimum validation mean cross-entropy; earliest epoch on exact tie',test_use='baseline and primary seed after frozen checkpoint; public benchmark, pilot previously viewed')
 protocol.update(random_state='one persistent RandomState per run',shuffle='fresh library permutation recorded each epoch',dependency='scikit-learn==1.6.1')
 savej('results/protocol_before_fit.json',protocol)
 allhistory=[];runs=[];primary=None;allwarn=[];start=time.time()
 orders=[]
 with threadpool_limits(limits=2):
  for seed in protocol['seeds']:
   run_rng=np.random.RandomState(seed)
   model=MLPClassifier(hidden_layer_sizes=(64,),activation='relu',solver='adam',alpha=.0001,batch_size=256,learning_rate_init=.001,random_state=run_rng,shuffle=True,early_stopping=False)
   history=[];bestloss=float('inf');best=None
   for epoch in range(1,51):
    with warnings.catch_warnings(record=True) as warn:
     warnings.simplefilter('always')
     import sklearn.neural_network._multilayer_perceptron as impl
     original_shuffle=impl.shuffle
     epoch_orders=[]
     def logged_shuffle(*args,**kwargs):
      result=original_shuffle(*args,**kwargs)
      epoch_orders.append(np.asarray(result).copy())
      return result
     impl.shuffle=logged_shuffle
     try:model.partial_fit(X,y,classes=np.arange(10))
     finally:impl.shuffle=original_shuffle
     ck(f'one_shuffle_seed_{seed}_epoch_{epoch}',len(epoch_orders)==1 and len(epoch_orders[0])==len(X))
     order=epoch_orders[0]
     ck(f'permutation_seed_{seed}_epoch_{epoch}',np.array_equal(np.sort(order),np.arange(len(X))))
     orders.append(order.astype(np.int32))
     if epoch>1:ck(f'fresh_shuffle_seed_{seed}_epoch_{epoch}',not np.array_equal(orders[-1],orders[-2]))
    allwarn.extend(str(a.message) for a in warn)
    _,zt,_=forward(X,*[model.coefs_[0],model.intercepts_[0],model.coefs_[1],model.intercepts_[1]])
    _,zv,_=forward(V,*[model.coefs_[0],model.intercepts_[0],model.coefs_[1],model.intercepts_[1]])
    vt=ce_logits(zv,yv);history.append(dict(epoch=epoch,train_ce=ce_logits(zt,y),validation_ce=vt,train_correct=int((zt.argmax(1)==y).sum()),validation_correct=int((zv.argmax(1)==yv).sum())))
    if vt<bestloss:bestloss=vt;best=copy.deepcopy(model);beste=epoch
    if epoch%10==0:print('Seed',seed,'epoch',epoch,'validation CE',round(vt,4),flush=True)
   _,zv,pv=forward(V,best.coefs_[0],best.intercepts_[0],best.coefs_[1],best.intercepts_[1]);sc=score(zv,yv)
   ck(f'checkpoint_argmin_seed_{seed}',beste==1+int(np.argmin([a['validation_ce'] for a in history])))
   ck(f'manual_forward_seed_{seed}',np.allclose(pv,best.predict_proba(V),rtol=1e-10,atol=1e-12))
   ck(f'parameters_seed_{seed}',sum(z.size for z in best.coefs_+best.intercepts_)==50890)
   ck(f'probabilities_seed_{seed}',np.all(pv>=0) and np.allclose(pv.sum(1),1))
   ck(f'confusion_hits_seed_{seed}',np.trace(np.array(sc['confusion']))==sc['correct'] and np.sum(sc['confusion'])==3000)
   runs.append(dict(seed=seed,selected_epoch=beste,validation=sc));allhistory.append(dict(seed=seed,epochs=history))
   if seed==42:primary=best
 # Freeze choice before measuring either fixed model on the public test benchmark.
 frozen=dict(protocol=protocol,primary_seed=42,selected_epoch=runs[0]['selected_epoch'],all_validation_runs=runs,selection_inputs='validation only',frozen_before_test_metrics=True)
 savej('results/frozen_decision_before_test.json',frozen)
 np.savez_compressed(R/'data/epoch_orders.npz',orders=np.array(orders).reshape(3,50,12000),seeds=np.array([42,43,44]))
 arrays=dict(W1=primary.coefs_[0],b1=primary.intercepts_[0],W2=primary.coefs_[1],b2=primary.intercepts_[1],baseline_W=A['pixel_coef'].T,baseline_b=A['pixel_intercept'],pca_mean=A['mean'],pca_components=A['components'][:64],pca64_coef=A['pca64_coef'],pca64_intercept=A['pca64_intercept'],pca64_predictions=A['validation_pca64_predictions'],toy_H=H,toy_gradient=g,toy_next=nextt,toy_target=target,tiny_theta=tt,tiny_numeric_gradient=fn)
 with threadpool_limits(limits=2):
  _,vp,vprob=forward(V,arrays['W1'],arrays['b1'],arrays['W2'],arrays['b2'])
  T=D['test_images'].astype(float)/255;yt=D['test_labels'];_,ztest,pt=forward(T,arrays['W1'],arrays['b1'],arrays['W2'],arrays['b2']);bt=T@arrays['baseline_W']+arrays['baseline_b']
  test_primary=score(ztest,yt);test_baseline=score(bt,yt)
 ck('frozen_before_test',json.loads((R/'results/frozen_decision_before_test.json').read_text(encoding='utf8'))['frozen_before_test_metrics'])
 ck('test_counts',test_primary['n']==10000 and test_baseline['n']==10000 and sum(map(sum,test_primary['confusion']))==10000)
 ck('test_diagonal',int(np.trace(test_primary['confusion']))==test_primary['correct'])
 ck('test_probabilities',np.allclose(pt.sum(1),1) and np.all(np.isfinite(pt)))
 ck('epochs_not_convergence_claim',all(len(a['epochs'])==50 for a in allhistory))
 display=np.array([np.flatnonzero(yv==j)[0] for j in range(10)])
 # Deterministic examples: first 3 baseline-only mistakes, first 3 shared mistakes, then general examples.
 bpred=baseline.argmax(1);mpred=vp.argmax(1)
 corrected=np.flatnonzero((bpred!=yv)&(mpred==yv))[:3];shared=np.flatnonzero((bpred!=yv)&(mpred!=yv))[:3]
 newwrong=np.flatnonzero((bpred==yv)&(mpred!=yv))[:3]
 arrays.update(validation_logits=vp,validation_predictions=mpred,validation_baseline_predictions=bpred,validation_baseline_logits=baseline,test_predictions=ztest.argmax(1),test_baseline_predictions=bt.argmax(1),display_positions=display,corrected_positions=corrected,shared_error_positions=shared,new_error_positions=newwrong)
 np.savez_compressed(R/'data/lab_arrays.npz',**arrays)
 ck('example_trace',all(np.array_equal(D['validation_images'][i].reshape(28,28).ravel(),D['validation_images'][i]) for i in np.r_[display,corrected,shared]))
 toy=dict(hidden=H.tolist(),gradient=g.tolist(),covariance=cov.tolist(),initial_loss=loss(theta),next_parameters=nextt.tolist(),next_logits=(H@nextt[:2]+nextt[2]).tolist(),next_probabilities=sigmoid(H@nextt[:2]+nextt[2]).tolist(),next_loss=loss(nextt),target_parameters=target.tolist(),target_loss=loss(target),target_logits=(H@target[:2]+target[2]).tolist(),cov_unbalanced=cu.tolist(),gradient_unbalanced=gu.tolist(),finite_gradient=finite(loss,theta).tolist())
 tiny={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in tiny.items()};tiny['after_update']=tiny_forward(tt-.1*np.array(tiny['gradient']))
 tiny['after_update']={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in tiny['after_update'].items()}
 tiny['updated_theta']=(tt-.1*np.array(tiny['gradient'])).tolist()
 tiny['numeric_gradient']=fn.tolist();tiny['max_gradient_error']=float(np.max(np.abs(np.array(tiny['gradient'])-fn)))
 pca_logits=(V-A['mean'])@A['components'][:64].T@A['pca64_coef'].T+A['pca64_intercept']
 ck('pca64_reference_predictions',np.array_equal(pca_logits.argmax(1),A['validation_pca64_predictions']))
 ck('pca64_reference_correct',int((pca_logits.argmax(1)==yv).sum())==2511)
 pca_score=score(pca_logits,yv)
 pairs={'both_correct':int(((bpred==yv)&(mpred==yv)).sum()),'corrected':int(((bpred!=yv)&(mpred==yv)).sum()),'newly_wrong':int(((bpred==yv)&(mpred!=yv)).sum()),'both_wrong':int(((bpred!=yv)&(mpred!=yv)).sum())}
 ck('paired_total',sum(pairs.values())==3000)
 ck('paired_delta',pairs['corrected']-pairs['newly_wrong']==runs[0]['validation']['correct']-base['correct'])
 report=dict(pca64_validation=pca_score,paired_validation=pairs,status='pass',checks_count=len(checks),checks=checks,protocol=protocol,split={'train':12000,'validation':3000,'test':10000},toy=toy,tiny=tiny,baseline_validation=base,mlp_runs=runs,history=allhistory,baseline_test=test_baseline,mlp_test=test_primary,validation_delta_correct=runs[0]['validation']['correct']-base['correct'],test_delta_correct=test_primary['correct']-test_baseline['correct'],warnings=allwarn,elapsed_seconds=time.time()-start,environment={'python':sys.version.split()[0],'sklearn':sklearn.__version__,'numpy':np.__version__},limitations=['Two prespecified configurations, not exhaustive tuning comparison','50-epoch budget; no claim of numerical convergence','Three seeds only; spread is descriptive, not confidence interval','Public test benchmark had earlier pilot results; not freshly sealed','No product IDs in source to verify group independence','28x28 grayscale benchmark does not represent arbitrary shop photographs'])
 savej('results/case_audit.json',report)
 print('PASS',len(checks),'checks; validation:',base['accuracy'],[r['validation']['accuracy'] for r in runs],'test:',test_baseline['accuracy'],test_primary['accuracy'],flush=True)
if __name__=='__main__':main()
