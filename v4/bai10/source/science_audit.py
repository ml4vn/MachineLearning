"""Independent math, raw-data lineage, prediction and diagram verification."""
from pathlib import Path
import json,hashlib,gzip,struct,sys,re
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
from PIL import Image
from lxml import html as H
from sklearn.metrics import confusion_matrix,f1_score
from threadpoolctl import threadpool_limits
checks=[]
def ck(name,ok,detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
    if not ok:raise AssertionError((name,detail))
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def save(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
A=read('results/case_audit.json');S=read('source/slide_manifest.json');D=np.load(R/'data/fashion_subset.npz');F=np.load(R/'data/lab_arrays.npz');E=read('source/evidence.json')
ck('case_completed',A['status']=='pass' and all(A['checks'].values()))
for item in read('data/source_manifest.json')['files']:
    raw=R/Path(item['path'].replace('\\','/'));ck('raw_sha_'+raw.name,hashlib.sha256(raw.read_bytes()).hexdigest()==item['sha256'])
def idx(name):
    data=gzip.decompress((R/'data/raw'/name).read_bytes());magic=struct.unpack('>I',data[:4])[0];dims=magic&255;shape=struct.unpack('>'+'I'*dims,data[4:4+4*dims]);return np.frombuffer(data[4+4*dims:],dtype=np.uint8).reshape(shape)
raw=idx('fashion_train_images.gz').reshape(60000,784);labels=idx('fashion_train_labels.gz')
for key in ['train','validation']:
    ck('raw_pixels_'+key,np.array_equal(D[key+'_images'],raw[D[key+'_indices']]))
    ck('raw_labels_'+key,np.array_equal(D[key+'_labels'],labels[D[key+'_indices']]))
ck('raw_test_pixels',np.array_equal(D['test_images'],idx('fashion_test_images.gz').reshape(10000,784)))
ck('raw_test_labels',np.array_equal(D['test_labels'],idx('fashion_test_labels.gz')))
ck('split_disjoint',not set(D['train_indices'])&set(D['validation_indices']))
old=read('data/bai09_reference.json');ck('subset_B9_hash',hashlib.sha256((R/'data/fashion_subset.npz').read_bytes()).hexdigest()==old['subset_sha256'])
ck('reference_hash',hashlib.sha256((R/'data/bai09_reference.npz').read_bytes()).hexdigest()==old['reference_sha256'])
# Recompute the nine-parameter binary network without using the lab function.
t=np.array([.5,-.4,.3,.8,.1,.1,.7,-.5,.2]);x=np.array([.6,.2])
def loss(theta,xx=x,yy=1):
    z=theta[:4].reshape(2,2)@xx+theta[4:6];h=np.maximum(z,0);s=theta[6:8]@h+theta[8];return float(np.logaddexp(0,s)-yy*s)
z=t[:4].reshape(2,2)@x+t[4:6];h=np.maximum(z,0);s=t[6:8]@h+t[8];p=1/(1+np.exp(-s));delta=p-1;dz=delta*t[6:8]*(z>0)
g=np.r_[np.outer(dz,x).ravel(),dz,delta*h,delta]
eps=1e-6;gn=np.array([(loss(t+eps*np.eye(9)[j])-loss(t-eps*np.eye(9)[j]))/(2*eps) for j in range(9)])
ck('tiny_forward',np.allclose(z,[.32,.44]) and np.isclose(s,.204) and np.isclose(loss(t),.596340185239002))
ck('all9_backprop',np.allclose(g,A['tiny']['gradient'],atol=1e-13) and np.allclose(g,gn,atol=1e-9))
ck('all9_update',np.allclose(t-.1*g,A['tiny']['updated_theta']) and np.isclose(loss(t-.1*g),.5506370864617522))
ck('second_sample',np.isclose(loss(t,np.array([.2,.6]),0),.6349461015956135))
ck('two_sample_mean',np.isclose((loss(t)+loss(t,np.array([.2,.6]),0))/2,.6156431434173077))
ck('chain_local',2*1*10==20 and 20+3==23)
ck('finite_slope',np.isclose(((2*1.001+3)**2-25)/.001,20.004))
ck('learning_rate',np.isclose((2*(1-.01*20)+3)**2,21.16) and (2*(1-.5*20)+3)**2==225)
xor=np.array([[0,0],[0,1],[1,0],[1,1]]);hh=np.c_[np.maximum(xor.sum(1),0),np.maximum(xor.sum(1)-1,0)]
ck('XOR_fixed',np.array_equal(hh,F['toy_H']) and np.array_equal(hh@[2,-4]-1,[-1,1,1,-1]))
# Stable multiclass CE and its score gradient.
def multiclass_loss(ss,label):return np.logaddexp.reduce(ss)-ss[label]
ss=np.array([2.,1.,0.]);probs=np.exp(ss-ss.max());probs/=probs.sum();target=np.array([0,1,0]);gm=probs-target
gmn=np.array([(multiclass_loss(ss+eps*np.eye(3)[j],1)-multiclass_loss(ss-eps*np.eye(3)[j],1))/(2*eps) for j in range(3)])
ck('softmax_score_gradient',np.allclose(gm,gmn,atol=1e-9) and np.isclose(gm.sum(),0))
ck('softmax_values',np.allclose(probs,[.6652409557748218,.24472847105479764,.09003057317038046]))
ck('parameters_and_batches',F['W1'].shape==(784,64) and F['W2'].shape==(64,10) and sum(F[k].size for k in ['W1','W2','b1','b2'])==50890 and int(np.ceil(12000/256))==47)
with threadpool_limits(limits=2):
    for key,report in [('validation',A['mlp_runs'][0]['validation']),('test',A['mlp_test'])]:
        xx=D[key+'_images'].astype(float)/255;yy=D[key+'_labels'];hidden=np.maximum(xx@F['W1']+F['b1'],0);scores=hidden@F['W2']+F['b2'];pr=scores.argmax(1)
        ck('prediction_'+key,np.array_equal(pr,F[key+'_predictions']))
        matrix=confusion_matrix(yy,pr,labels=np.arange(10));ck('confusion_'+key,np.array_equal(matrix,report['confusion']) and int(matrix.trace())==report['correct'] and matrix.sum()==len(yy))
        ck('CE_'+key,np.isclose(np.mean(np.logaddexp.reduce(scores,axis=1)-scores[np.arange(len(yy)),yy]),report['cross_entropy'],atol=1e-12))
        ck('macro_F1_'+key,np.isclose(f1_score(yy,pr,average='macro'),report['macro_f1']))
        ck('recall_'+key,np.allclose(matrix.diagonal()/matrix.sum(1),report['recall']))
    xx=D['validation_images'].astype(float)/255;yy=D['validation_labels'];baseline=xx@F['baseline_W']+F['baseline_b'];b=baseline.argmax(1);m=F['validation_predictions']
    ck('baseline_unchanged',np.array_equal(b,F['validation_baseline_predictions']) and (b==yy).sum()==2500)
    pcalogits=(xx-F['pca_mean'])@F['pca_components'].T@F['pca64_coef'].T+F['pca64_intercept']
    ck('pca_unchanged',np.array_equal(pcalogits.argmax(1),F['pca64_predictions']) and (pcalogits.argmax(1)==yy).sum()==2511)
    counts=[int(((b==yy)&(m==yy)).sum()),int(((b!=yy)&(m==yy)).sum()),int(((b==yy)&(m!=yy)).sum()),int(((b!=yy)&(m!=yy)).sum())]
    ck('paired_2433_165_67_335',counts==[2433,165,67,335] and 165-67==A['validation_delta_correct'])
orders=np.load(R/'data/epoch_orders.npz')['orders'];ck('150_epoch_orders',orders.shape==(3,50,12000))
for i,seed in enumerate([42,43,44]):
    ck('shuffle_different_'+str(seed),all(not np.array_equal(orders[i,j],orders[i,j-1]) for j in range(1,50)))
    history=A['history'][i]['epochs'];selected=A['mlp_runs'][i]['selected_epoch'];ck('checkpoint_'+str(seed),selected==1+int(np.argmin([z['validation_ce'] for z in history])) and len(history)==50)
ck('frozen_before_test',read('results/frozen_decision_before_test.json')['frozen_before_test_metrics'])
Q=read('source/quiz_bank_v4.json');ck('eight_balanced_quizzes',''.join(q['answer'] for q in Q.values())=='ACBDACBD')
ck('87_order_and_timing',len(S)==87 and [s['slide'] for s in S]==list(range(1,88)) and sum(s['minutes'] for s in S if s['kind']!='break')==180 and sum(s['minutes'] for s in S if s['kind']=='break')==10)
ck('six_summaries',[s['slide'] for s in S if s['summary']]==[18,34,62,74,84,86])
for s in S:
    ck('notes_'+str(s['slide']),len(s['notes'].split('\n\n')[0])>170 and not any(k in s['notes'] for k in ['Mục tiêu:','Nội dung:','Phút:']))
for k,positions in E['groups'].items():
    expected=np.flatnonzero(((b!=yy)&(m==yy)) if k=='corrected' else ((b==yy)&(m!=yy)) if k=='new' else ((b!=yy)&(m!=yy)))[:2]
    ck('example_rule_'+k,np.array_equal(expected,positions))
    for j,i in enumerate(positions):ck('image_'+k+str(j),np.array_equal(np.array(Image.open(R/f'source/figures/{k}_{j}.png'))[::10,::10].ravel(),D['validation_images'][i]))
save('results/science_audit.json',dict(status='pass',checks_count=len(checks),checks=checks))
# Check literal coordinates and actual values in the authored diagrams.
dc=[]
for slide in S:
    tree=H.fromstring((R/'source/html'/slide['html']).read_text(encoding='utf8'))
    for sv in tree.xpath('//svg[contains(@class,"evidence")]'):
        dots=sv.xpath('.//circle[@data-point-id]')
        if dots:
            points=np.array([[float(q.get('data-math-x')),float(q.get('data-math-y'))] for q in dots]);px=np.array([[float(q.get('cx')),float(q.get('cy'))] for q in dots])
            # Each plot has four IDs; infographic contains two separate plots.
            for start in range(0,len(dots),4):
                q=points[start:start+4];actual=px[start:start+4];is_hidden=dots[start].get('data-space')=='h';expected=hh if is_hidden else xor
                sx,bx=np.linalg.lstsq(np.c_[q[:,0],np.ones(4)],actual[:,0],rcond=None)[0];sy,by=np.linalg.lstsq(np.c_[q[:,1],np.ones(4)],actual[:,1],rcond=None)[0]
                assert np.allclose(q,expected) and np.isclose(sx,-sy) and sx>0 and np.allclose(actual[:,0],sx*q[:,0]+bx) and np.allclose(actual[:,1],sy*q[:,1]+by)
                dc.append(dict(slide=slide['slide'],space='h' if is_hidden else 'x',passed=True,equal_unit_scale=float(sx)))
        hidden=sv.xpath('.//rect[@data-neuron]');prob=sv.xpath('.//rect[@data-probability]')
        if hidden:
            assert len(hidden)==64 and np.allclose([float(q.get('data-value')) for q in hidden],E['real_hidden']);dc.append(dict(slide=slide['slide'],type='64_actual_activations',passed=True))
        if prob:
            assert len(prob)==10 and np.allclose([float(q.get('data-probability')) for q in prob],E['real_probabilities']);dc.append(dict(slide=slide['slide'],type='10_actual_probabilities',passed=True))
save('results/diagram_math_check.json',dict(passed=True,checks_count=len(dc),checks=dc))
cs=read('source/chart_specs.json');cc=[]
for name,c in cs.items():
    for series in c['series']:
        xx=np.array(series['xValues']);val=np.array(series['values']);assert len(xx)==len(val) and np.isfinite(val).all() and min(xx)>=c['xmin']-1e-9 and max(xx)<=c['xmax']+1e-9 and min(val)>=c['ymin']-1e-9 and max(val)<=c['ymax']+1e-9
        cc.append(dict(chart=name,series=series['name'],passed=True))
assert np.allclose(cs['history']['series'][0]['values'],[h['train_ce'] for h in A['history'][0]['epochs']])
assert np.allclose(cs['history']['series'][1]['values'],[h['validation_ce'] for h in A['history'][0]['epochs']])
assert cs['checkpoint']['series'][1]['xValues']==[34]
save('results/chart_range_check.json',dict(passed=True,checks_count=len(cc),checks=cc))
print(json.dumps(dict(status='pass',independent_checks=len(checks),diagram_checks=len(dc),chart_series=len(cc))))
