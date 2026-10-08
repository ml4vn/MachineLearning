"""Bài 6 v4: CART tính tay, cắt tỉa và Olist tái lập. Chạy từ mọi thư mục."""
from pathlib import Path
import sys, json, hashlib
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix,average_precision_score,roc_auc_score,brier_score_loss,log_loss,accuracy_score,precision_recall_curve
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from threadpoolctl import threadpool_limits
FEATURES=['distance_km','promised_days','price','freight_value','n_items','weight_g']
DATES=['order_approved_at','order_delivered_customer_date','order_estimated_delivery_date']
GRID=[.02,.03,.05,.1,.15,.2,.3,.5,.8]

def save(name,obj):
    p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')

def gini(y):
    p=np.bincount(np.asarray(y,dtype=int),minlength=2)/len(y)
    return float(1-p@p)

def split_score(X,y,j,t):
    mask=X[:,j]<=t;n=len(y);nl=int(mask.sum());nr=n-nl
    if not nl or not nr:return None
    gl,gr=gini(y[mask]),gini(y[~mask]);after=nl/n*gl+nr/n*gr
    return dict(feature=j,threshold=float(t),n_left=nl,n_right=nr,pos_left=int(y[mask].sum()),pos_right=int(y[~mask].sum()),g_left=gl,g_right=gr,after=after,gain=gini(y)-after)

def enumerate_splits(X,y):
    out=[]
    for j in range(X.shape[1]):
        v=np.unique(X[:,j])
        out.extend(split_score(X,y,j,t) for t in (v[:-1]+v[1:])/2)
    return out

def toy_data():
    x=np.arange(1,13,dtype=float);short=np.isin(x,[1,4,7,10]);y=(short|(x>=11)).astype(int)
    return np.column_stack([x,np.where(short,10,20)]),y

def metrics(y,p,t=.5):
    pred=np.zeros(len(y),dtype=bool) if t is None else p>=t
    tn,fp,fn,tp=map(int,confusion_matrix(y,pred,labels=[0,1]).ravel())
    return dict(n=len(y),tn=tn,fp=fp,fn=fn,tp=tp,alerts=tp+fp,precision=tp/(tp+fp) if tp+fp else None,precision_defined=bool(tp+fp),recall=tp/(tp+fn),accuracy=(tn+tp)/len(y),f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,cost=fp+5*fn,ap=float(average_precision_score(y,p)),auc=float(roc_auc_score(y,p)),brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,p,labels=[0,1])))

def choose_policy(y,p):
    scan=[dict(threshold=t,**metrics(y,p,t)) for t in GRID+[None]]
    pick=min(scan,key=lambda a:(a['cost'],a['alerts'],-(float('inf') if a['threshold'] is None else a['threshold'])))
    return pick,scan

def export_tree(model):
    t=model.tree_
    return [dict(node=i,left=int(t.children_left[i]),right=int(t.children_right[i]),feature=int(t.feature[i]),threshold=float(t.threshold[i]) if t.feature[i]>=0 else None,n=int(t.n_node_samples[i]),positive=int(round(t.value[i,0,1]*t.n_node_samples[i])),p=float(t.value[i,0,1]),gini=float(t.impurity[i])) for i in range(t.node_count)]

def walk(nodes,x):
    node=0;path=[];x=np.asarray(x,dtype=np.float32)
    while nodes[node]['left']>=0:
        a=nodes[node];left=bool(float(x[a['feature']])<=a['threshold']);path.append(dict(node=node,feature=a['feature'],value=float(x[a['feature']]),threshold=a['threshold'],go_left=left));node=a['left'] if left else a['right']
    return node,nodes[node]['p'],path

def run():
    checks={}
    def ck(name,ok):checks[name]=bool(ok);assert ok,name
    d=pd.read_csv(R/'data/prepared/olist_model_table.csv',parse_dates=DATES)
    ref=json.loads((R/'data/logistic_bai05_reference.json').read_text(encoding='utf-8'))
    provenance=json.loads((R/'results/data_provenance.json').read_text(encoding='utf-8'))
    ck('corrected_data_hash',hashlib.sha256((R/'data/prepared/olist_model_table.csv').read_bytes()).hexdigest()==provenance['sha256_prepared'])
    ck('unique_order',d.order_id.is_unique);ck('split_counts',d.split.value_counts().to_dict()==ref['split_counts'])
    ck('positive_counts',d.groupby('split').late.sum().to_dict()==ref['positive_counts'])
    ck('calendar_label',np.array_equal(d.late,(d[DATES[1]].dt.normalize()>d[DATES[2]].dt.normalize()).astype(int)))
    parts={k:d[d.split==k].copy() for k in ['train','validation','test']};tr=parts['train']
    ck('train_label_cutoff',tr[DATES[1]].lt('2017-11-01').all());ck('validation_label_cutoff',parts['validation'][DATES[1]].lt('2018-01-01').all())
    ck('missing_weight_is_unknown',tr.weight_g.isna().sum()==16)
    imp=SimpleImputer(strategy='median').fit(tr[FEATURES]);Xs={k:imp.transform(a[FEATURES]) for k,a in parts.items()}
    ck('same_train_median_as_Bai05',np.allclose(imp.statistics_,ref['imputer']))
    candidates=[];models={}
    for depth in [3,6]:
        m=DecisionTreeClassifier(criterion='gini',max_depth=depth,min_samples_leaf=200,ccp_alpha=0,random_state=42).fit(Xs['train'],tr.late);models[depth]=m
        nodes=export_tree(m);vp=m.predict_proba(Xs['validation'])[:,1]
        candidates.append(dict(depth=depth,leaves=m.get_n_leaves(),nodes=m.tree_.node_count,train=metrics(tr.late,m.predict_proba(Xs['train'])[:,1]),validation=metrics(parts['validation'].late,vp)))
        ck(f'depth{depth}_leaf_min',all(a['n']>=200 for a in nodes if a['left']<0))
        ck(f'depth{depth}_node_identity',m.tree_.node_count==2*m.get_n_leaves()-1)
        ids=m.apply(Xs['train'])
        ck(f'depth{depth}_leaf_probability',all(np.isclose(tr.late.to_numpy()[ids==a['node']].mean(),a['p']) for a in nodes if a['left']<0))
        save(f'results/tree_depth{depth}.json',nodes)
    chosen=max(candidates,key=lambda a:(a['validation']['ap'],-a['leaves']));m=models[chosen['depth']];nodes=export_tree(m)
    vp=m.predict_proba(Xs['validation'])[:,1];pick,scan=choose_policy(parts['validation'].late,vp)
    policy=dict(features=FEATURES,criterion='gini',depth_candidates=[3,6],selected_depth=chosen['depth'],min_samples_leaf=200,ccp_alpha=0,random_state=42,class_weight=None,preprocessing='Median fit train only; original units; no scaler',structure_selection='validation AP; ties fewer leaves',threshold_grid=GRID,include_no_alerts=True,selected_threshold=pick['threshold'],criterion_policy='hypothetical K=FP+5FN; not money',threshold_selection='validation K; ties fewer alerts then larger threshold',refit=False,test_exposure='Historical cohort viewed in earlier course versions; not a new blind evaluation')
    save('results/model_policy.json',policy)
    p=m.predict_proba(Xs['test'])[:,1];y=parts['test'].late.to_numpy();t=pick['threshold']
    manual=np.array([walk(nodes,x)[1] for x in Xs['test']]);ck('manual_path_all_test',np.array_equal(manual,p))
    selected=metrics(y,p,t);baseline=metrics(y,np.full(len(y),tr.late.mean()),None)
    ck('confusion_total',selected['tn']+selected['fp']+selected['fn']+selected['tp']==len(y))
    contributions=np.zeros(len(FEATURES))
    for a in nodes:
        if a['left']>=0:
            l,r=nodes[a['left']],nodes[a['right']];contributions[a['feature']]+=(a['n']*a['gini']-l['n']*l['gini']-r['n']*r['gini'])/len(tr)
    residual=sum(a['n']/len(tr)*a['gini'] for a in nodes if a['left']<0)
    ck('impurity_telescoping',np.isclose(contributions.sum(),nodes[0]['gini']-residual));ck('MDI_independent',np.allclose(contributions/contributions.sum(),m.feature_importances_))
    # Logistic is refitted under its original protocol solely to verify same-cohort comparison.
    sc=StandardScaler().fit(Xs['train']);Zs={k:sc.transform(x) for k,x in Xs.items()}
    lr=LogisticRegression(solver='newton-cg',C=1,penalty='l2',tol=1e-6,max_iter=1000,random_state=42).fit(Zs['train'],tr.late)
    lvp=lr.predict_proba(Zs['validation'])[:,1];lpick,lscan=choose_policy(parts['validation'].late,lvp)
    lp=lr.predict_proba(Zs['test'])[:,1];lt=lpick['threshold'];lm=metrics(y,lp,lt)
    ck('Logistic_reference_policy',lt==ref['policy']['selected'])
    ck('Logistic_reference_confusion',all(lm[k]==ref['test_selected'][k] for k in ['tp','fp','tn','fn','cost']))
    ck('Logistic_reference_scores',np.isclose(lm['ap'],ref['test_selected']['ap'],atol=1e-10))
    pred=np.zeros(len(y),dtype=int) if t is None else (p>=t).astype(int);lpred=np.zeros(len(y),dtype=int) if lt is None else (lp>=lt).astype(int)
    tc=pred==y;lc=lpred==y;groups={'both_correct':tc&lc,'tree_fixes':tc&~lc,'tree_new_errors':~tc&lc,'both_wrong':~tc&~lc}
    examples={};pair={k:int(mask.sum()) for k,mask in groups.items()}
    ck('paired_total',sum(pair.values())==len(y))
    ids=parts['test'].order_id.to_numpy()
    for k,mask in groups.items():
        indices=sorted(np.flatnonzero(mask),key=lambda i:ids[i])[:2]
        examples[k]=[dict(order_id=ids[i],late=int(y[i]),tree_p=float(p[i]),tree_prediction=int(pred[i]),logistic_p=float(lp[i]),logistic_prediction=int(lpred[i])) for i in indices]
    pair['fn_fixed']=int(((y==1)&(lpred==0)&(pred==1)).sum());pair['fn_new']=int(((y==1)&(lpred==1)&(pred==0)).sum())
    pair['fp_fixed']=int(((y==0)&(lpred==1)&(pred==0)).sum());pair['fp_new']=int(((y==0)&(lpred==0)&(pred==1)).sum())
    one_id=ref['one_order']['order_id'];row=d[d.order_id==one_id].iloc[0];raw=row[FEATURES].to_numpy(dtype=float);filled=imp.transform(row[FEATURES].to_frame().T)[0]
    leaf,prob,path=walk(nodes,filled);ck('one_ID_leaf',int(m.apply(filled.reshape(1,-1))[0])==leaf)
    one=dict(order_id=one_id,split=row.split,late=int(row.late),raw={f:float(v) if np.isfinite(v) else None for f,v in zip(FEATURES,raw)},filled=filled.tolist(),leaf=leaf,p=prob,path=path,leaf_counts=nodes[leaf],approved=str(row[DATES[0]]),delivered=str(row[DATES[1]]),estimated=str(row[DATES[2]]))
    perm=permutation_importance(m,Xs['validation'],parts['validation'].late,scoring='average_precision',n_repeats=5,random_state=42,n_jobs=1)
    real_pr=precision_recall_curve(y,p);pr=dict(precision=real_pr[0].tolist(),recall=real_pr[1].tolist(),thresholds=real_pr[2].tolist())
    XX,yy=toy_data();cand=enumerate_splits(XX,yy);best=max(cand,key=lambda a:a['gain']);balanced=split_score(XX,yy,0,6.5);right=XX[:,1]>15;child=split_score(XX[right],yy[right],0,10)
    toy_m=DecisionTreeClassifier(random_state=42).fit(XX,yy);cp=toy_m.cost_complexity_pruning_path(XX,yy)
    ck('toy_candidate_count',len(cand)==12);ck('toy_best_root',best['feature']==1 and best['threshold']==15 and np.isclose(best['gain'],.25))
    ck('toy_balanced',np.isclose(balanced['after'],4/9) and np.isclose(balanced['gain'],1/18))
    ck('toy_child_gain',np.isclose(child['gain'],3/8) and np.isclose(right.mean()*child['gain'],.25))
    ck('toy_full_tree',toy_m.get_n_leaves()==3 and toy_m.get_depth()==2 and np.array_equal(toy_m.predict(XX),yy))
    ck('toy_pruning_actual_path',np.allclose(cp.ccp_alphas,[0,.25]) and np.allclose(cp.impurities,[0,.5]))
    tie=DecisionTreeClassifier(min_samples_split=3,random_state=42).fit([[0],[1]],[0,1]);ck('predict_tie_vs_explicit_policy',tie.predict([[.5]])[0]==0 and tie.predict_proba([[.5]])[0,1]>=.5)
    xor_X=np.array([[0,0],[0,1],[1,0],[1,1]]);xor_y=[0,1,1,0];xor=DecisionTreeClassifier(random_state=42).fit(xor_X,xor_y);ck('zero_gain_not_universal_stop',np.array_equal(xor.predict(xor_X),xor_y))
    toy=dict(x=XX.tolist(),y=yy.tolist(),ids=[f'M{i:02}' for i in range(1,13)],root_candidates=cand,balanced=balanced,best_root=best,child_candidates=enumerate_splits(XX[right],yy[right]),child=child,tree=export_tree(toy_m),pruning_alphas=cp.ccp_alphas.tolist(),pruning_impurities=cp.impurities.tolist())
    moonX,moony=make_moons(n_samples=600,noise=.3,random_state=17);mi,mv=train_test_split(np.arange(600),test_size=.5,stratify=moony,random_state=42)
    mooncurves=[];moontrees={}
    for depth in [1,2,3,4,5,6,8,12,None]:
        model=DecisionTreeClassifier(max_depth=depth,random_state=42).fit(moonX[mi],moony[mi]);key='all' if depth is None else str(depth)
        mooncurves.append(dict(depth=depth,plot_depth=16 if depth is None else depth,leaves=model.get_n_leaves(),train=float(accuracy_score(moony[mi],model.predict(moonX[mi]))),validation=float(accuracy_score(moony[mv],model.predict(moonX[mv])))))
        if depth in [2,None]:moontrees[key]=export_tree(model)
    moon=dict(x=moonX.tolist(),y=moony.tolist(),train_indices=mi.tolist(),validation_indices=mv.tolist(),curves=mooncurves,trees=moontrees)
    for k,a in parts.items():
        scores=m.predict_proba(Xs[k])[:,1]
        pd.DataFrame(dict(order_id=a.order_id,late=a.late,p=scores,leaf_id=m.apply(Xs[k]),prediction=np.zeros(len(a),dtype=int) if t is None else (scores>=t).astype(int))).to_csv(R/f'data/{k}_predictions.csv',index=False)
    pd.DataFrame(dict(order_id=ids,late=y,tree_p=p,tree_prediction=pred,logistic_p=lp,logistic_prediction=lpred)).to_csv(R/'data/paired_test_predictions.csv',index=False)
    pd.DataFrame(dict(order_id=toy['ids'],x_100km=XX[:,0],promised_days=XX[:,1],late=yy)).to_csv(R/'data/toy_12_simulated.csv',index=False)
    pd.DataFrame(cand).to_csv(R/'data/toy_root_candidates.csv',index=False)
    save('results/chosen_tree.json',nodes);save('results/toy.json',toy);save('results/moons.json',moon)
    result=dict(status='pass',sklearn_version=sklearn.__version__,checks_count=len(checks),checks=checks,split_counts={k:len(v) for k,v in parts.items()},positive_counts={k:int(v.late.sum()) for k,v in parts.items()},prevalences={k:float(v.late.mean()) for k,v in parts.items()},features=FEATURES,imputer=imp.statistics_.tolist(),candidates=candidates,policy=policy,validation_scan=scan,validation_selected=pick,test_selected=selected,test_half=metrics(y,p,.5),baseline=baseline,one_order=one,logistic=dict(policy=lpick,test_selected=lm),paired_counts=pair,paired_examples=examples,example_rule='first two lexicographic IDs in each group',mdi=m.feature_importances_.tolist(),permutation_mean=perm.importances_mean.tolist(),permutation_std=perm.importances_std.tolist(),pr=pr,toy=toy,moons=moon)
    save('results/case_audit.json',result)
    print(json.dumps(dict(status='pass',checks=len(checks),tree_depth=chosen['depth'],threshold=t,test=selected,paired=pair),ensure_ascii=False))
    return result

if __name__=='__main__':
    with threadpool_limits(limits=1):run()
