import numpy as np

def sigmoid(z):
    """Hai nhánh tránh exp(1000); có thể làm tròn về 0/1 ở giới hạn máy."""
    z=np.asarray(z,float)
    if not np.isfinite(z).all(): raise ValueError('Logit phải hữu hạn')
    out=np.empty_like(z);positive=z>=0
    out[positive]=1/(1+np.exp(-z[positive]))
    ez=np.exp(z[~positive]);out[~positive]=ez/(1+ez)
    return out

def logistic_loss_gradient(X,y,theta):
    X,y,theta=np.asarray(X,float),np.asarray(y,float),np.asarray(theta,float)
    if X.ndim!=2 or not len(X) or y.shape!=(len(X),) or theta.shape!=(X.shape[1],):
        raise ValueError('Kích thước X/y/theta không hợp lệ')
    if not np.isfinite(X).all() or not np.isfinite(theta).all() or not np.isin(y,[0,1]).all():
        raise ValueError('Đầu vào hữu hạn; nhãn phải 0/1')
    logits=X@theta
    # Với nhãn 0/1: softplus(-z) nếu y=1, softplus(z) nếu y=0.
    # Công thức này còn tránh phép trừ hai số lớn gần nhau ở logit dương.
    loss=float(np.mean(np.logaddexp(0,(1-2*y)*logits)))
    gradient=X.T@(sigmoid(logits)-y)/len(y)
    return loss,gradient

def logistic_gd(X,y,eta=1.,steps=20):
    if not np.isfinite(eta) or eta<=0 or not isinstance(steps,int) or not 0<=steps<=10000:
        raise ValueError('eta dương và steps nguyên trong [0,10000]')
    X=np.asarray(X,float)
    if X.ndim!=2: raise ValueError('X phải là ma trận')
    theta=np.zeros(X.shape[1]);history=[]
    for step in range(steps+1):
        loss,g=logistic_loss_gradient(X,y,theta)
        history.append({'step':step,'loss':loss,**{f'theta_{j}':float(v) for j,v in enumerate(theta)}})
        if step<steps: theta=theta-eta*g
    return theta,history
