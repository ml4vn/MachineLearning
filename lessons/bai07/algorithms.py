import numpy as np
import pandas as pd

def asof_fold(d,train_start,cutoff,validation_end):
    """Train biết nhãn trước cutoff; validation chấm khi kết thúc cửa sổ."""
    start,cut,end=map(pd.Timestamp,[train_start,cutoff,validation_end])
    if not start<cut<end: raise ValueError('Cần start < cutoff < validation_end')
    approved=d.order_approved_at;delivered=d.order_delivered_customer_date
    train=np.flatnonzero((approved>=start)&(approved<cut)&(delivered<cut))
    validation=np.flatnonzero((approved>=cut)&(approved<end)&(delivered<end))
    if set(train)&set(validation): raise AssertionError('Trùng fold')
    return train,validation

def memorize_groups(groups,y,train,validation):
    groups,y=np.asarray(groups),np.asarray(y)
    train,validation=np.asarray(train,int),np.asarray(validation,int)
    if groups.ndim!=1 or groups.shape!=y.shape or not np.isin(y,[0,1]).all():raise ValueError('Nhóm và nhãn phải khớp')
    if not len(train) or not len(validation) or set(train)&set(validation):raise ValueError('Hai tập khác rỗng, không giao nhau')
    known={}
    for group,label in zip(groups[train],y[train]):
        if group in known and known[group]!=label:raise ValueError('Ví dụ ghi nhớ yêu cầu nhãn mỗi nhóm đồng nhất')
        known[group]=label
    fallback=int(y[train].mean()>.5)
    pred=np.array([known.get(g,fallback) for g in groups[validation]])
    return pred,{'shared_groups':len(set(groups[train])&set(groups[validation])),
                 'accuracy':float(np.mean(pred==y[validation])),'fallback':fallback}

def repeated_selection(seed=2026,repetitions=500):
    if not isinstance(repetitions,int) or repetitions<1:raise ValueError('repetitions phải nguyên dương')
    rng=np.random.default_rng(seed)
    score=rng.binomial(100,.5,size=(repetitions,100))/100
    fresh=rng.binomial(100,.5,size=(repetitions,100))/100
    rows=[];details=[]
    for k in [1,10,100]:
        chosen=np.argmax(score[:,:k],axis=1);a=score[np.arange(repetitions),chosen];b=fresh[np.arange(repetitions),chosen]
        rows.append({'candidates':k,'selected_mean':float(a.mean()),'fresh_mean':float(b.mean())})
        details.extend({'repeat':i,'candidates':k,'chosen_candidate':int(chosen[i]),'selected_score':float(a[i]),'fresh_score':float(b[i])} for i in range(repetitions))
    return rows,details
