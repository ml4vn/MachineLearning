"""Reproducible lesson 1: metadata similarity, not personalized recommendation."""
from pathlib import Path
import sys, csv, json, math
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'.build/pydeps').is_dir():sys.path.insert(0,str(ROOT/'.build/pydeps'))
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

AXES3=('Action','Comedy','Sci-Fi')
QUERY=2571
CANDIDATES=(260,1580,480,1214,1)
MISSING='(no genres listed)'

def load_movies(path=None):
    with Path(path or ROOT/'data/movies.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    result={int(r['movieId']):r for r in rows}
    if len(result)!=len(rows): raise ValueError('Duplicate movieId')
    return result

def labels(row):
    return set(row['genres'].split('|'))-{MISSING}

def encode(row,axes):
    if len(axes)!=len(set(axes)) or not axes: raise ValueError('Axes must be unique and nonempty')
    return np.array([float(a in labels(row)) for a in axes])

def cosine_safe(u,v):
    """None denotes undefined cosine for a zero vector. Same schema is caller's duty."""
    u,v=np.asarray(u,dtype=float),np.asarray(v,dtype=float)
    if u.ndim!=1 or v.ndim!=1 or u.shape!=v.shape or u.size==0:
        raise ValueError('Two nonempty 1D vectors of equal length are required')
    if not np.isfinite(u).all() or not np.isfinite(v).all():
        raise ValueError('Input contains NaN or infinity')
    nu,nv=np.linalg.norm(u),np.linalg.norm(v)
    if nu==0 or nv==0: return None
    if not np.isfinite(nu) or not np.isfinite(nv): raise ValueError('Norm overflow')
    return float((u/nu)@(v/nv))

def run():
    movies=load_movies();axes=sorted(set().union(*(labels(m) for m in movies.values())))
    q=encode(movies[QUERY],AXES3);qf=encode(movies[QUERY],axes)
    checks={}
    def ck(name,condition):
        checks[name]=bool(condition)
        assert condition,name
    records=[]
    for mid in CANDIDATES:
        v=encode(movies[mid],AXES3);vf=encode(movies[mid],axes)
        hand=sum(a*b for a,b in zip(q,v))/math.sqrt(sum(q*q)*sum(v*v))
        own=cosine_safe(q,v);library=float(cosine_similarity([q],[v])[0,0])
        ck(f'hand_numpy_sklearn_{mid}',abs(hand-own)<1e-12 and abs(own-library)<1e-12)
        a,b=labels(movies[QUERY]),labels(movies[mid])
        set_cos=len(a&b)/math.sqrt(len(a)*len(b))
        ck(f'independent_label_intersection_{mid}',abs(set_cos-cosine_safe(qf,vf))<1e-12)
        records.append({'movieId':mid,'title':movies[mid]['title'],'vector3':v.astype(int).tolist(),
                        'dot':int(q@v),'norm_v_squared':int(v@v),'hand':hand,'numpy':own,'sklearn':library,'full':set_cos})
    eligible=[];equal=[];max_error=0.
    for mid,row in movies.items():
        v=encode(row,axes)
        if mid==QUERY or not v.any():continue
        a,b=labels(movies[QUERY]),labels(row)
        independent=len(a&b)/math.sqrt(len(a)*len(b))
        score=cosine_safe(qf,v)
        max_error=max(max_error,abs(score-independent))
        eligible.append({'movieId':mid,'title':row['title'],'genres':row['genres'],'cosine':score})
        if a==b:equal.append(mid)
    ck('all_9707_scores_match_set_formula',len(eligible)==9707 and max_error<1e-12)
    ck('exactly_42_full_label_matches',len(equal)==42)
    ck('19_metadata_labels_with_IMAX',len(axes)==19 and 'IMAX' in axes and MISSING not in axes)
    ck('34_missing_rows',sum(not labels(r) for r in movies.values())==34)
    ck('4196_zero_3d_rows',sum(not encode(r,AXES3).any() for r in movies.values())==4196)
    ck('Casablanca_projected_zero',cosine_safe(q,encode(movies[912],AXES3)) is None)
    ck('Casablanca_full_orthogonal',cosine_safe(qf,encode(movies[912],axes))==0)
    ck('sklearn_zero_policy_differs',float(cosine_similarity([q],[[0,0,0]])[0,0])==0)
    ck('exit_ticket_vector_110',abs(cosine_safe(q,[1,1,0])-.5)<1e-12)
    ck('exit_vector_011',abs(cosine_safe(q,[0,1,1])-.5)<1e-12)
    ck('normalize_6_8',np.allclose(np.array([6,8])/np.linalg.norm([6,8]),[.6,.8]))
    ck('general_dot_2_1_1_2',np.array([2,1])@np.array([1,2])==4)
    ck('norm_3_4',np.linalg.norm([3,4])==5)
    ck('positive_scaling',abs(cosine_safe([1,2],[2,1])-cosine_safe([3,6],[2,1]))<1e-12)
    ck('Euclidean_counterexample',np.linalg.norm(np.array([1,0])-[1,1])<np.linalg.norm(np.array([1,0])-[3,0]) and cosine_safe([1,0],[1,1])<cosine_safe([1,0],[3,0]))
    ck('adding_axis_increases',abs(cosine_safe([1,0,1],[0,1,1])-.5)<1e-12)
    ck('adding_axis_decreases',cosine_safe([1,0],[1,1])<cosine_safe([1],[1]))
    ck('negative_cosine_squared_wrong_order',(-.9)**2>.5**2 and -.9<.5)
    u=np.array([1.,2.,3.]);v=np.array([3.,1.,2.]);un=u/np.linalg.norm(u);vn=v/np.linalg.norm(v)
    ck('unit_euclidean_identity',abs(np.linalg.norm(un-vn)**2-(2-2*cosine_safe(u,v)))<1e-12)
    w=np.array([2.,1.,.5]);weighted=float((w*u*v).sum()/math.sqrt((w*u*u).sum()*(w*v*v).sum()))
    ck('weighted_cosine_sqrt_transform',abs(weighted-cosine_safe(np.sqrt(w)*u,np.sqrt(w)*v))<1e-12)
    ck('weighted_not_direct_alpha_transform',abs(weighted-cosine_safe(w*u,w*v))>1e-4)
    ck('negative_scaling_flips_sign',cosine_safe([1,0],[-2,0])==-1)
    ck('checksum_seven',sum(r['dot'] for r in records)==7)
    for name,a,b in [('different_dimensions',[1,0],[1,0,1]),('nan',[math.nan,1],[1,1]),('inf',[math.inf,1],[1,1]),('empty',[],[]),('matrix',[[1,1]],[[1,1]])]:
        try:cosine_safe(a,b)
        except ValueError:ck('reject_'+name,True)
        else:ck('reject_'+name,False)
    # ID only stabilizes display within exact equal-label ties; it is not a preference signal.
    eligible.sort(key=lambda r:(-r['cosine'],r['movieId']))
    report={'status':'pass','checks_count':len(checks),'checks':checks,'tolerance':1e-12,
            'maximum_full_score_error':max_error,'candidate_pool':len(eligible),'exact_equal_label_count':len(equal),
            'axes_full':axes,'comparison':records,'same_label_ids':sorted(equal),'top10_display':eligible[:10],
            'weighted_example':weighted,'library_zero_convention':0,'own_zero_convention':None,
            'interpretation':'Similarity of encoded item metadata; no user-preference or usefulness claim.'}
    (ROOT/'results/lab_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    with (ROOT/'data/So_sanh_tay_numpy_sklearn.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
    print(json.dumps({'status':report['status'],'checks':len(checks),'candidate_pool':len(eligible),'maximum_error':max_error},ensure_ascii=False))
    return report

if __name__=='__main__':run()
