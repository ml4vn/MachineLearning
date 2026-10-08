"""Independent recomputation of the evidence displayed in Bài 9 v4."""
from pathlib import Path
import sys,json,hashlib,re
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
from PIL import Image
from lxml import html as H
from threadpoolctl import threadpool_limits
from sklearn.metrics import accuracy_score,f1_score

def main():
    A=json.loads((R/'results/case_audit.json').read_text(encoding='utf8'))
    S=json.loads((R/'source/slide_manifest.json').read_text(encoding='utf8'))
    D=np.load(R/'data/fashion_subset.npz'); F=np.load(R/'data/lab_arrays.npz')
    checks=[]
    def ck(name,condition,detail=None):
        checks.append(dict(name=name,passed=bool(condition),detail=detail))
        if not condition:raise AssertionError((name,detail))
    P=np.array([[3.,4.],[4.,3.],[6.,7.],[7.,6.]])
    mu=P.mean(0);xc=P-mu;w=np.array([1.,1.])/np.sqrt(2);v=np.array([1.,-1.])/np.sqrt(2)
    C=xc.T@xc/len(P);z=xc@w;foot=z[:,None]*w;rec=foot+mu;err=xc-foot
    ck('toy_source',np.array_equal(F['toy'],P))
    ck('toy_mean',np.array_equal(mu,[5,5]))
    ck('center_sum',np.allclose(xc.sum(0),0))
    ck('unit_length',np.isclose(w@w,1) and np.isclose(v@v,1))
    ck('orthogonal_axes',np.isclose(w@v,0))
    ck('covariance_population',np.array_equal(C,[[2.5,2],[2,2.5]]))
    ck('eig1',np.allclose(C@w,4.5*w));ck('eig2',np.allclose(C@v,.5*v))
    ck('scores',np.allclose(z,[-3,-3,3,3]/np.sqrt(2)))
    ck('feet',np.allclose(foot,[[-1.5,-1.5],[-1.5,-1.5],[1.5,1.5],[1.5,1.5]]))
    ck('reconstruction',np.allclose(rec,F['toy_reconstruction']))
    ck('residual_orthogonal',np.allclose(err@w,0))
    ck('residual_squared_each',np.allclose((err**2).sum(1),.5))
    ck('MSE_two_denominators',np.isclose(np.mean(err**2),.25) and np.isclose(np.mean((err**2).sum(1)),.5))
    ck('variance_budget',np.isclose(np.mean((xc**2).sum(1)),5) and np.isclose(np.var(z),4.5))
    ck('projection_collision',z[0]==z[1] and not np.array_equal(P[0],P[1]))
    ck('flip_sign_invariance',np.allclose((xc@(-w))[:,None]*(-w),foot))
    ck('score_scaling_square',np.isclose(np.var(xc@(10*w)),100*np.var(z)))
    ck('sample_covariance_factor',np.allclose(np.cov(P,rowvar=False),C*4/3))
    ck('sample_eigenvalues',np.allclose(np.linalg.eigvalsh(np.cov(P,rowvar=False)),[2/3,6]))
    for deg in [0,15,30,45,60,90,120,135,180]:
        t=np.deg2rad(deg);u=np.array([np.cos(t),np.sin(t)])
        var=np.var(xc@u);error=np.mean(np.sum((xc-(xc@u)[:,None]*u)**2,1))
        ck('angle_'+str(deg),np.isclose(var,2.5+2*np.sin(2*t)) and np.isclose(var+error,5))
    out=np.vstack([P,[9,0]]);om=out.mean(0);oc=np.cov(out,rowvar=False,bias=True)
    lam,W=np.linalg.eigh(oc);ow=W[:,-1]
    ck('outlier_mean',np.allclose(om,A['outlier']['mean']))
    ck('outlier_direction_sign_free',np.allclose(np.outer(ow,ow),np.outer(A['outlier']['PC1'],A['outlier']['PC1'])))
    ck('low_variance_labels',np.allclose(xc@v,[-1,1,-1,1]/np.sqrt(2)))
    tr=D['train_indices'];va=D['validation_indices']
    ck('disjoint_IDs',not set(tr)&set(va))
    ck('split_sizes',len(tr)==12000 and len(va)==3000)
    ck('train_balance',np.array_equal(np.bincount(D['train_labels']),[1200]*10))
    ck('validation_balance',np.array_equal(np.bincount(D['validation_labels']),[300]*10))
    X=D['train_images'].astype(float)/255;V=D['validation_images'].astype(float)/255
    m=F['mean'];W=F['components'];Z=F['validation_scores'];lam=F['eigenvalues'];ev=F['evr'];cum=np.cumsum(ev)
    ck('train_mean',np.allclose(X.mean(0),m,atol=1e-13))
    with threadpool_limits(limits=2):
        ck('orthonormal_full_basis',np.allclose(W@W.T,np.eye(784),atol=1e-10))
        ck('validation_scores_recomputed',np.allclose((V-m)@W[:128].T,Z,atol=1e-11))
    ck('EVR_eigenvalue_ratio',np.allclose(ev,lam/lam.sum()))
    ck('EVR_sum',np.isclose(ev.sum(),1))
    ck('EVR_sorted',np.all(np.diff(ev)<=1e-12))
    ck('eigenvalue_variance_sum',np.isclose(lam.sum(),X.var(0,ddof=1).sum()))
    ck('k90_minimal',cum[80]<.9<=cum[81] and A['k90']==82)
    positions=F['display_positions']
    for c,i in enumerate(positions):
        ck('display_first_class_'+str(c),D['validation_labels'][i]==c and i==np.flatnonzero(D['validation_labels']==c)[0])
        ck('source_ID_'+str(c),A['display_examples'][c]['source_id']=='train:'+str(va[i]))
        im=np.array(Image.open(R/f'source/figures/original_{c}.png').convert('L'))
        ck('original_matrix_'+str(c),np.array_equal(im[::10,::10].ravel(),D['validation_images'][i]))
    ck('trace_pixel',va[positions[0]]==24814 and V[positions[0]].reshape(28,28)[12,12]==203/255)
    for j,k in enumerate([2,16,64,128]):
        reconstruction=Z[:,:k]@W[:k]+m; mse=float(np.mean((V-reconstruction)**2));item=A['reconstruction'][j]
        ck('MSE_unclipped_'+str(k),np.isclose(mse,item['validation_mse_pixel'],atol=1e-13))
        ck('train_EVR_'+str(k),np.isclose(cum[k-1],item['train_evr']))
        tail=lam[k:].sum()*11999/12000/784
        ck('train_MSE_tail_'+str(k),np.isclose(tail,item['train_mse_pixel'],atol=1e-13))
        ck('saved_recon_'+str(k),np.allclose(reconstruction[positions],F['display_recon'][j]))
        ck('display_clipping_'+str(k),np.isclose(np.mean((V-np.clip(reconstruction,0,1))**2),item['validation_mse_clipped']))
    y=D['validation_labels'];pred=F['validation_pixel_predictions'];pred64=F['validation_pca64_predictions']
    for key,XX,beta,b,stored in [('pixel',V,F['pixel_coef'],F['pixel_intercept'],pred),('PCA64',Z[:,:64],F['pca64_coef'],F['pca64_intercept'],pred64)]:
        ck('LR_argmax_'+key,np.array_equal(np.argmax(XX@beta.T+b,axis=1),stored))
        ck('accuracy_'+key,np.isclose(accuracy_score(y,stored),2500/3000 if key=='pixel' else 2511/3000))
        ck('macro_F1_'+key,np.isclose(f1_score(y,stored,average='macro'),.8335812760763197 if key=='pixel' else .836599754189951))
    p=pred==y;q=pred64==y
    ck('paired_145_134_2366_355',np.array_equal([sum(~p&q),sum(p&~q),sum(p&q),sum(~p&~q)],[145,134,2366,355]))
    ck('net_improvement',int(q.sum()-p.sum())==11)
    ck('no_test_metric',not any('test_accuracy' in str(s) for s in S))
    ck('coords_not_bytes',np.isclose(64/784*100,8.1632653061) and np.isclose((1-64/784)*100,91.8367346939))
    ck('65_slides',len(S)==65 and [s['slide'] for s in S]==list(range(1,66)))
    ck('summary_locations',[s['slide'] for s in S if s['summary']]==[12,25,39,53,62,64])
    Q=json.loads((R/'source/quiz_bank_v4.json').read_text(encoding='utf8'))
    ck('balanced_quiz_answers',''.join(q['answer'] for q in Q.values())=='ACDABC')
    for n,q in Q.items():ck('quiz_'+n,len(q['options'])==4 and len(q['explanations'])==4 and q['answer_slide']==q['question_slide']+1)
    ck('150_plus10',sum(s['minutes'] for s in S if s['kind']!='break')==150 and sum(s['minutes'] for s in S if s['kind']=='break')==10)
    for s in S:
        ck('notes_'+str(s['slide']),bool(s['notes']) and 'PGS.TS.' not in s['notes'] and not any(x in s['notes'] for x in ['Mục tiêu:','Nội dung:','Phút:']))
    ck('B10_MLP_bridge','MLP' in S[-1]['notes'] and 'MLP' in S[-1]['body'])
    report=dict(status='pass',checks_count=len(checks),checks=checks)
    (R/'results/science_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(status='pass',checks_count=len(checks)),ensure_ascii=False))

if __name__=='__main__':main()
