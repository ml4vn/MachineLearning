"""Reproduce B2's historical SMS predictions and B3's decision policies.

Run from any directory: python path/to/source/metrics_lab.py
All paths resolve inside this lesson. No test-based model/threshold tuning.
"""
from pathlib import Path
import sys,json,hashlib,zipfile,io
ROOT=Path(__file__).resolve().parents[1]
extra=ROOT/'.build/pydeps'
if extra.exists():sys.path.insert(0,str(extra))
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (confusion_matrix,accuracy_score,precision_score,
    recall_score,f1_score,roc_auc_score,average_precision_score,
    precision_recall_curve,roc_curve,classification_report)
from threadpoolctl import threadpool_limits
from sms_lab import load_data,FEATURES

K=11

def measure(y,pred):
    """Return counts, definedness and reporting values (zero_division=0)."""
    y=np.asarray(y,dtype=int);pred=np.asarray(pred,dtype=int)
    if len(y)==0 or y.shape!=pred.shape:raise ValueError('Nonempty aligned arrays required')
    if not np.isin(y,[0,1]).all() or not np.isin(pred,[0,1]).all():raise ValueError('Binary labels only')
    tn,fp,fn,tp=map(int,confusion_matrix(y,pred,labels=[0,1]).ravel())
    return dict(tn=tn,fp=fp,fn=fn,tp=tp,n=len(y),alerts=tp+fp,
        accuracy=(tn+tp)/len(y),precision=tp/(tp+fp) if tp+fp else 0.,
        recall=tp/(tp+fn) if tp+fn else 0.,
        f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.,
        precision_defined=bool(tp+fp),recall_defined=bool(tp+fn),
        f1_count_defined=bool(2*tp+fp+fn),zero_division=0,
        cost_5fp_fn=5*fp+fn,cost_fp_5fn=fp+5*fn)

def predict_votes(votes,min_votes):
    v=np.asarray(votes)
    if not np.isin(v,np.arange(K+1)).all():raise ValueError('votes must be integer 0..11')
    if min_votes not in range(K+2):raise ValueError('min_votes must be 0..12')
    return (v>=min_votes).astype(int)

def select_policy(scan,cost_name):
    """Rule declared before applying a policy to the historical test."""
    return min(scan,key=lambda x:(x[cost_name],x['alerts'],-x['min_votes']))

def toy_data():
    return pd.DataFrame(dict(id=list('ABCDEFGHIJ'),score=[.95,.90,.85,.70,.60,.55,.40,.30,.20,.10],y=[1,0,1,1,0,1,0,0,0,0]))

def run():
    (ROOT/'results').mkdir(exist_ok=True);(ROOT/'data').mkdir(exist_ok=True)
    checks={}
    def ck(name,ok):
        checks[name]=bool(ok)
        if not ok:raise AssertionError(name)
    frozen=json.loads((ROOT/'results/case_audit_frozen.json').read_text(encoding='utf8'))
    d,tr,va,te=load_data()
    with zipfile.ZipFile(ROOT/'data/sms.zip') as z:
        raw=pd.read_csv(io.BytesIO(z.read('SMSSpamCollection')),sep='\t',names=['label','text'],quoting=3)
    ck('raw_counts_5574_4827_747',len(raw)==5574 and raw.label.value_counts().to_dict()=={'ham':4827,'spam':747})
    ck('dedup_counts_5159_4517_642',len(d)==5159 and d.label.value_counts().to_dict()=={'ham':4517,'spam':642})
    ck('415_duplicates_removed',len(raw)-len(d)==415)
    ck('split_sizes',list(map(len,[tr,va,te]))==[3095,1032,1032])
    ck('split_disjoint',not(set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te)))
    ck('normalized_text_split_disjoint',not(set(d.loc[tr,'normal'])&set(d.loc[va,'normal']) or set(d.loc[tr,'normal'])&set(d.loc[te,'normal']) or set(d.loc[va,'normal'])&set(d.loc[te,'normal'])))
    ck('validation_903_ham_129_spam',d.loc[va,'y'].value_counts().to_dict()=={0:903,1:129})
    ck('test_904_ham_128_spam',d.loc[te,'y'].value_counts().to_dict()=={0:904,1:128})
    ck('positive_spam_consistent',np.array_equal(d.y,(d.label=='spam').astype(int)))
    ck('features_nonempty_valid',d.n_chars.min()>0 and d.digit_fraction.between(0,1).all())
    saved_features=pd.read_csv(ROOT/'data/sms_features.csv').set_index('message_id')
    joined=d.set_index('message_id').loc[saved_features.index]
    ck('frozen_ids_splits_features',set(d.message_id)==set(saved_features.index) and (joined.split==saved_features.split).all() and np.allclose(joined[FEATURES],saved_features[FEATURES],rtol=0,atol=1e-15))
    ck('features_from_original_text',all(len(t)==n and sum(ch.isdigit() for ch in t)==nd for t,n,nd in zip(d.text,d.n_chars,d.n_digits)))
    X=d.loc[tr,FEATURES].to_numpy();scaler=StandardScaler().fit(X)
    ck('scaler_train_mean',np.allclose(scaler.mean_,[79.31017770597738,.01805199024951043]))
    ck('scaler_train_ddof0',np.allclose(scaler.scale_,X.std(0,ddof=0)))
    model=KNeighborsClassifier(n_neighbors=K,weights='uniform',metric='minkowski',p=2)
    model.fit(scaler.transform(X),d.loc[tr,'y'])
    ck('class_order_ham_spam',model.classes_.tolist()==[0,1])
    frames={}
    with threadpool_limits(limits=2):
        for key,idx in [('validation',va),('test',te)]:
            frame=d.loc[idx,['message_id','source_record','text','y','label','n_chars','n_digits','digit_fraction']].copy()
            score=model.predict_proba(scaler.transform(d.loc[idx,FEATURES].to_numpy()))[:,1]
            votes=np.rint(score*K).astype(int)
            ck(key+'_integer_vote_score',np.allclose(score,votes/K,rtol=0,atol=1e-14))
            frame['score']=score;frame['votes']=votes;frame['prediction']=predict_votes(votes,6)
            ck(key+'_default_predict_equivalence',np.array_equal(frame.prediction,model.predict(scaler.transform(d.loc[idx,FEATURES].to_numpy()))))
            frames[key]=frame
    v,t=frames['validation'],frames['test']
    old=pd.read_csv(ROOT/'data/sms_core_test_predictions.csv').set_index('message_id').loc[t.message_id]
    ck('test_predictions_identical_B2',np.array_equal(old.prediction,t.prediction))
    ck('test_scores_identical_B2',np.allclose(old.neighbor_vote_fraction,t.score,rtol=0,atol=1e-14))
    ck('test_truth_identical_B2',np.array_equal(old.y,t.y))
    prediction_hash=hashlib.sha256((ROOT/'data/sms_core_test_predictions.csv').read_bytes()).hexdigest()
    ck('frozen_prediction_SHA256',prediction_hash==frozen['source_prediction_sha256'])
    base=measure(t.y,t.prediction)
    ck('frozen_confusion_matrix',[[base['tn'],base['fp']],[base['fn'],base['tp']]]==[[892,12],[17,111]])
    ck('1003_correct_29_wrong',base['tn']+base['tp']==1003 and base['fp']+base['fn']==29)
    for key,fun in [('accuracy',accuracy_score),('precision',precision_score),('recall',recall_score),('f1',f1_score)]:
        ck('manual_'+key,np.isclose(base[key],fun(t.y,t.prediction)))
    ck('F1_two_forms',np.isclose(base['f1'],2*base['precision']*base['recall']/(base['precision']+base['recall'])))
    always_ham=measure(t.y,np.zeros(len(t),int))
    ck('baseline_accuracy_recall',np.isclose(always_ham['accuracy'],904/1032) and always_ham['recall']==0)
    ck('baseline_precision_undefined_reported_zero',not always_ham['precision_defined'] and always_ham['precision']==0 and precision_score(t.y,np.zeros(len(t)),zero_division=0)==0)
    scan=[dict(min_votes=m,**measure(v.y,predict_votes(v.votes,m))) for m in range(13)]
    ck('13_decision_policies',len(scan)==13 and scan[0]['alerts']==1032 and scan[-1]['alerts']==0)
    ck('fixed_validation_margins',all(a['tp']+a['fn']==129 and a['tn']+a['fp']==903 for a in scan))
    ck('alerts_nonincreasing',all(a['alerts']>=b['alerts'] for a,b in zip(scan,scan[1:])))
    ck('recall_nonincreasing',all(a['recall']>=b['recall'] for a,b in zip(scan,scan[1:])))
    ck('TP_FP_nonincreasing',all(a['tp']>=b['tp'] and a['fp']>=b['fp'] for a,b in zip(scan,scan[1:])))
    ck('FN_TN_nondecreasing',all(a['fn']<=b['fn'] and a['tn']<=b['tn'] for a,b in zip(scan,scan[1:])))
    selected={}
    for key,expected_m in [('cost_5fp_fn',8),('cost_fp_5fn',4)]:
        best=select_policy(scan,key)
        ck('validation_select_'+key,best['min_votes']==expected_m and best[key]==min(x[key] for x in scan))
        selected[key]=dict(min_votes=best['min_votes'],validation=best.copy())
    policy=dict(model='StandardScaler(train) + uniform kNN(11); two B2 features',candidates=list(range(13)),positive_label='spam=1',selection_uses='validation only',costs_are_hypothetical=True,tie_rule='minimum cost, then fewer alerts, then larger min_votes',validation_reuse='The same validation selected k in B2; it is not an independent evaluation.',previous_test_exposure='Already published historical B2/B3 test, not a new independent blind test.',chosen=selected)
    (ROOT/'results/threshold_policy.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2),encoding='utf8')
    for key,a in selected.items():
        a['test']=measure(t.y,predict_votes(t.votes,a['min_votes']))
        ck('historical_test_'+key,all(a['test'][k]==frozen['selected'][key]['test'][k] for k in ['tn','fp','fn','tp']))
    tied=[dict(min_votes=2,alerts=7,cost=9),dict(min_votes=3,alerts=5,cost=9),dict(min_votes=4,alerts=5,cost=9)]
    ck('declared_tie_rule',select_policy(tied,'cost')['min_votes']==4)
    toy=toy_data();toy_results={}
    for tau in [.50,.80,.85,.90]:
        toy_results[str(tau)]=measure(toy.y,(toy.score>=tau).astype(int))
    a,b=toy_results['0.5'],toy_results['0.8']
    ck('toy_default_counts',[a[k] for k in ['tn','fp','fn','tp']]==[4,2,0,4])
    ck('toy_high_counts',[b[k] for k in ['tn','fp','fn','tp']]==[5,1,2,2])
    ck('toy_two_costs',[a['cost_5fp_fn'],b['cost_5fp_fn'],a['cost_fp_5fn'],b['cost_fp_5fn']]==[10,7,2,11])
    ck('toy_precision_counterexample',toy_results['0.85']['precision']==2/3 and toy_results['0.9']['precision']==.5)
    ck('toy_F1_default_high',a['f1']==.8 and b['f1']==4/7)
    ck('same_accuracy_different_errors',measure([0]*6+[1]*4,[0]*4+[1]*6)['accuracy']==measure([0]*6+[1]*4,[0]*8+[1]*2)['accuracy']==.8)
    examples=[]
    for record in [9,1056,1501,4]:
        row=t.loc[t.source_record==record].iloc[0].to_dict()
        row['outcome']=['TN','FP','FN','TP'][2*row['y']+row['prediction']];examples.append(row)
    ck('four_real_outcomes',set(a['outcome'] for a in examples)=={'TN','FP','FN','TP'})
    ck('FP1056_FN1501_votes',next(a for a in examples if a['source_record']==1056)['votes']==6 and next(a for a in examples if a['source_record']==1501)['votes']==4)
    ck('unanimous_errors_exist',bool(((t.score.isin([0,1]))&(t.y!=t.prediction)).any()))
    edge=measure([0,0],[0,0])
    ck('all_negative_zero_denominators',not edge['precision_defined'] and not edge['recall_defined'] and not edge['f1_count_defined'])
    ck('all_negative_library_convention',f1_score([0,0],[0,0],zero_division=0)==edge['f1']==0)
    p,r,thresholds=precision_recall_curve(t.y,t.score)
    fpr,tpr,roc_thresholds=roc_curve(t.y,t.score,drop_intermediate=False)
    ap=float(-np.sum(np.diff(r)*p[:-1]));auc=float(roc_auc_score(t.y,t.score))
    ck('AP_weighted_recall_steps',np.isclose(ap,average_precision_score(t.y,t.score)))
    sp=t.loc[t.y==1,'score'].to_numpy();sn=t.loc[t.y==0,'score'].to_numpy()
    pair_auc=float(np.mean((sp[:,None]>sn)+.5*(sp[:,None]==sn)))
    ck('AUC_pairs_half_ties',np.isclose(pair_auc,auc))
    ck('ROC_AUC_historical',np.isclose(auc,frozen['roc_auc']))
    ck('AP_historical',np.isclose(ap,frozen['ap']))
    ck('PR_extra_endpoint',len(p)==len(r)==len(thresholds)+1 and p[-1]==1 and r[-1]==0)
    ck('scores_within_12_possible_levels',set(t.votes.unique()).issubset(set(range(12))))
    exit=measure([1]*5+[0]*15,[1]*3+[0]*2+[1]*2+[0]*13)
    ck('exit_counts',[exit[k] for k in ['tn','fp','fn','tp']]==[13,2,2,3])
    ck('exit_P_R_F1',exit['precision']==exit['recall']==exit['f1']==.6)
    for key,frame in frames.items():frame.to_csv(ROOT/f'data/{key}_predictions.csv',index=False)
    toy.to_csv(ROOT/'data/toy_scores.csv',index=False)
    pd.DataFrame(scan).to_csv(ROOT/'data/validation_threshold_scan.csv',index=False)
    pd.DataFrame(dict(precision=p,recall=r,threshold=np.r_[thresholds,np.nan])).to_csv(ROOT/'data/pr_curve.csv',index=False)
    pd.DataFrame(dict(fpr=fpr,tpr=tpr,threshold=roc_thresholds)).to_csv(ROOT/'data/roc_curve.csv',index=False)
    out=dict(status='pass',checks_count=len(checks),checks=checks,base=base,always_ham=always_ham,validation_scan=scan,selected=selected,toy=toy_results,toy_rows=toy.to_dict('records'),examples=examples,exit=exit,roc_auc=auc,ap=ap,prevalence=float(t.y.mean()),source_prediction_sha256=prediction_hash,scaler_mean=scaler.mean_.tolist(),scaler_scale=scaler.scale_.tolist(),versions=dict(python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__,sklearn=__import__('sklearn').__version__),protocol=policy)
    for name in ['lab_checks.json','case_audit.json']:(ROOT/'results'/name).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    return out

if __name__=='__main__':
    out=run()
    print(json.dumps({k:out[k] for k in ['status','checks_count','base','selected','roc_auc','ap']},ensure_ascii=False,indent=2))
