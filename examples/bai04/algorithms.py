import numpy as np

def loss_gradient(X,y,theta):
    """X đã bao gồm cột 1 nếu học intercept; J = mean(error²)/2."""
    X,y,theta=np.asarray(X,float),np.asarray(y,float),np.asarray(theta,float)
    if X.ndim!=2 or not len(X) or y.shape!=(len(X),) or theta.shape!=(X.shape[1],):
        raise ValueError('Kích thước X, y, theta không phù hợp')
    if not all(np.isfinite(a).all() for a in [X,y,theta]): raise ValueError('Cần dữ liệu hữu hạn')
    error=X@theta-y
    return float(np.mean(error**2)/2),X.T@error/len(y)

def gradient_descent(X,y,eta=.1,steps=100,initial=None):
    X=np.asarray(X,float)
    if X.ndim!=2: raise ValueError('X phải là ma trận')
    if not np.isfinite(eta) or eta<=0 or not isinstance(steps,(int,np.integer)) or not 0<=steps<=10000:
        raise ValueError('eta > 0 và steps nguyên trong [0,10000]')
    theta=np.zeros(X.shape[1]) if initial is None else np.asarray(initial,float).copy()
    history=[]
    for step in range(steps+1):
        loss,gradient=loss_gradient(X,y,theta)
        if not np.isfinite(loss) or not np.isfinite(gradient).all():
            raise FloatingPointError('GD phân kỳ; giảm learning rate hoặc chuẩn hóa')
        history.append({'step':step,'loss':loss,**{f'theta_{j}':float(t) for j,t in enumerate(theta)}})
        if step<steps: theta=theta-eta*gradient  # Mọi thành phần dùng gradient tại cùng theta cũ.
    return theta,history
