import numpy as np

def gini(y):
    y=np.asarray(y)
    if y.ndim!=1 or not len(y) or not np.isin(y,[0,1]).all():
        raise ValueError('Cần vector nhãn nhị phân không rỗng')
    p=float(np.mean(y));return 2*p*(1-p)

def enumerate_splits(X,y):
    X,y=np.asarray(X,float),np.asarray(y)
    if X.ndim!=2 or y.shape!=(len(X),) or not np.isfinite(X).all():
        raise ValueError('Ma trận hữu hạn và nhãn phải khớp')
    before=gini(y);rows=[]
    for j in range(X.shape[1]):
        unique=np.unique(X[:,j]);thresholds=unique[:-1]+(unique[1:]-unique[:-1])/2
        for t in thresholds:
            left=X[:,j]<=t;nl=int(left.sum());nr=len(y)-nl
            if not nl or not nr: continue
            gl,gr=gini(y[left]),gini(y[~left]);after=(nl*gl+nr*gr)/len(y)
            rows.append({'feature':j,'threshold':float(t),'n_left':nl,'n_right':nr,
                         'pos_left':int(y[left].sum()),'pos_right':int(y[~left].sum()),
                         'g_left':gl,'g_right':gr,'after':after,'gain':before-after})
    return rows

def export_tree(model,mean=None,scale=None):
    tree=model.tree_
    if list(model.classes_)!=[0,1]: raise ValueError('Ví dụ này cần cả hai lớp 0/1')
    mean=np.zeros(tree.n_features) if mean is None else np.asarray(mean)
    scale=np.ones(tree.n_features) if scale is None else np.asarray(scale)
    rows=[]
    for i in range(tree.node_count):
        j=int(tree.feature[i]);p=float(tree.value[i,0,1]/tree.value[i,0].sum())
        rows.append({'node':i,'left':int(tree.children_left[i]),'right':int(tree.children_right[i]),
                     'feature':j,'threshold':float(tree.threshold[i]),
                     'threshold_raw':float(tree.threshold[i]*scale[j]+mean[j]) if j>=0 else None,
                     'n':int(tree.n_node_samples[i]),'positive':int(round(p*tree.n_node_samples[i])),
                     'p':p,'gini':float(tree.impurity[i])})
    return rows

def walk(nodes,x):
    """sklearn CART chuyển input float32 khi dự đoán; mô phỏng cùng quy ước."""
    x=np.asarray(x,dtype=np.float32)
    if x.ndim!=1 or not np.isfinite(x).all(): raise ValueError('x phải là vector hữu hạn')
    node=0;path=[]
    while nodes[node]['left']>=0:
        row=nodes[node];j=row['feature'];left=bool(float(x[j])<=row['threshold'])
        path.append({'node':node,'feature':j,'value_standardized_float32':float(x[j]),
                     'threshold_standardized':row['threshold'],'threshold_raw':row['threshold_raw'],'go_left':left})
        node=row['left'] if left else row['right']
    return node,nodes[node]['p'],path

def impurity_contributions(nodes,n_features):
    terms=np.zeros(n_features);root_n=nodes[0]['n']
    for row in nodes:
        if row['left']>=0:
            left,right=nodes[row['left']],nodes[row['right']]
            terms[row['feature']]+=(row['n']*row['gini']-left['n']*left['gini']-right['n']*right['gini'])/root_n
    residual=sum(row['n']/root_n*row['gini'] for row in nodes if row['left']<0)
    if not np.isclose(terms.sum(),nodes[0]['gini']-residual): raise AssertionError('Tổng gain không khớp')
    return terms

def toy_data():
    x=np.arange(1.,13.);short=np.isin(x,[1,4,7,10]);y=(short|(x>=11)).astype(int)
    return np.column_stack([x,np.where(short,10,20)]),y
