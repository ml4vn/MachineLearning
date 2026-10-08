"""Independent arithmetic, data and model audit; no sklearn metric calls."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib
R=Path(__file__).resolve().parents[1]
if (R/'.build/pydeps').exists():sys.path.insert(0,str(R/'.build/pydeps'))
import numpy as np
import pandas as pd

def run():
    A=json.loads((R/'results/case_audit.json').read_text(encoding='utf-8'))
    D=json.loads((R/'results/data_provenance.json').read_text(encoding='utf-8'))
    nodes=json.loads((R/'results/chosen_tree.json').read_text(encoding='utf-8'))
    d=pd.read_csv(R/'data/prepared/olist_model_table.csv',float_precision='round_trip')
    checks={}
    def ck(n,v):checks[n]=bool(v);assert v,n
    ck('raw_hash',hashlib.sha256((R.parent/'datasets/olist.zip').read_bytes()).hexdigest()==D['sha256_raw'])
    ck('prepared_hash',hashlib.sha256((R/'data/prepared/olist_model_table.csv').read_bytes()).hexdigest()==D['sha256_prepared'])
    ck('toy_balanced_fraction',F(1,2)-(F(6,12)*F(4,9)+F(6,12)*F(4,9))==F(1,18))
    ck('toy_promised_fraction',F(1,2)-(F(4,12)*0+F(8,12)*F(3,8))==F(1,4))
    ck('toy_child_global_fraction',F(8,12)*F(3,8)==F(1,4))
    T=A['toy'];X=np.array(T['x']);y=np.array(T['y'])
    for i,c in enumerate(T['root_candidates']):
        mask=X[:,c['feature']]<=c['threshold'];pL=F(int(y[mask].sum()),int(mask.sum()));pR=F(int(y[~mask].sum()),int((~mask).sum()));gL=2*pL*(1-pL);gR=2*pR*(1-pR)
        after=F(int(mask.sum()),12)*gL+F(int((~mask).sum()),12)*gR
        ck('toy_candidate_'+str(i),np.isclose(float(F(1,2)-after),c['gain']))
    for alpha in [F(1,10),F(1,4),F(3,10)]:
        z=[3*alpha,F(1,4)+2*alpha,F(1,2)+alpha]
        ck('pruning_objective_'+str(alpha),z.index(min(z))==({F(1,10):0,F(1,4):0,F(3,10):2}[alpha]))
    train=d[d.split=='train'];features=A['features'];values=train[features].fillna(dict(zip(features,A['imputer']))).to_numpy(dtype=np.float32);labels=train.late.to_numpy()
    def verify_node(node,idx):
        n=nodes[node];ys=labels[idx];p=ys.mean()
        ck(f'node_{node}_count',len(idx)==n['n'] and int(ys.sum())==n['positive'])
        ck(f'node_{node}_Gini',np.isclose(2*p*(1-p),n['gini']))
        if n['left']<0:ck(f'leaf_{node}_p',np.isclose(p,n['p']));return
        mask=values[idx,n['feature']]<=n['threshold'];ck(f'node_{node}_partition',0<mask.sum()<len(mask))
        verify_node(n['left'],idx[mask]);verify_node(n['right'],idx[~mask])
    verify_node(0,np.arange(len(train)))
    for k in ['validation','test']:
        pred=pd.read_csv(R/f'data/{k}_predictions.csv',float_precision='round_trip');s=A['validation_selected'] if k=='validation' else A['test_selected'];t=A['policy']['selected_threshold']
        yh=np.zeros(len(pred),bool) if t is None else pred.p.to_numpy()>=t;y=pred.late.to_numpy().astype(bool)
        counts=dict(tp=int((yh&y).sum()),fp=int((yh&~y).sum()),fn=int((~yh&y).sum()),tn=int((~yh&~y).sum()))
        ck(k+'_confusion',all(counts[j]==s[j] for j in counts))
        ck(k+'_cost',counts['fp']+5*counts['fn']==s['cost'])
        # AP by tied score blocks, accumulating TP/all predictions at each score.
        grouped=pred.groupby('p').late.agg(['sum','size']).sort_index(ascending=False)
        tp=0;n=0;ap=0;pos=int(pred.late.sum());neg=len(pred)-pos
        for _,g in grouped.iterrows():tp+=g['sum'];n+=g['size'];ap+=g['sum']/pos*tp/n
        ck(k+'_AP_tie_blocks',np.isclose(ap,s['ap'],atol=1e-12))
        neg_before=0;pairs=0
        for _,g in grouped.sort_index().iterrows():
            np_=g['sum'];nn=g['size']-np_;pairs+=np_*(neg_before+.5*nn);neg_before+=nn
        ck(k+'_AUC_pairs',np.isclose(pairs/(pos*neg),s['auc'],atol=1e-12))
    val=pd.read_csv(R/'data/validation_predictions.csv',float_precision='round_trip');scan=[]
    for t in A['policy']['threshold_grid']+[None]:
        yh=np.zeros(len(val),bool) if t is None else val.p.to_numpy()>=t;yy=val.late.to_numpy().astype(bool);fp=int((yh&~yy).sum());fn=int((~yh&yy).sum())
        scan.append((fp+5*fn,int(yh.sum()),-(float('inf') if t is None else t),t))
    ck('validation_policy_independent',min(scan)[3]==A['policy']['selected_threshold'])
    pair=pd.read_csv(R/'data/paired_test_predictions.csv');tc=pair.tree_prediction.eq(pair.late);lc=pair.logistic_prediction.eq(pair.late)
    actual={'both_correct':int((tc&lc).sum()),'tree_fixes':int((tc&~lc).sum()),'tree_new_errors':int((~tc&lc).sum()),'both_wrong':int((~tc&~lc).sum())}
    ck('paired_all_cohort',all(actual[k]==A['paired_counts'][k] for k in actual) and sum(actual.values())==len(pair))
    masks={'both_correct':tc&lc,'tree_fixes':tc&~lc,'tree_new_errors':~tc&lc,'both_wrong':~tc&~lc}
    for k,mask in masks.items():ck('deterministic_example_'+k,pair.loc[mask].sort_values('order_id').order_id.head(2).tolist()==[x['order_id'] for x in A['paired_examples'][k]])
    out=dict(status='pass',checks_count=len(checks),checks=checks,method='Exact fractions; recursive train-node partitions; Boolean confusion counts; score-block AP; pairwise AUC; independent threshold scan; whole-cohort paired errors.')
    (R/'results/science_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status='pass',checks=len(checks))));return out

if __name__=='__main__':run()
