"""Mô hình và phép đánh giá Olist dùng chung; không tự chọn bằng test."""
import warnings
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,brier_score_loss,average_precision_score,roc_auc_score
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
from mlcourse.olist import FEATURES
from examples.bai03.algorithms import measure

THRESHOLDS=[.05,.10,.15,.20,.30,.50]

def fit_logistic(train,C=1.):
    if not np.isfinite(C) or C<=0: raise ValueError('C phải dương và hữu hạn')
    imp=SimpleImputer(strategy='median').fit(train[FEATURES])
    sc=StandardScaler().fit(imp.transform(train[FEATURES]))
    model=LogisticRegression(solver='newton-cg',max_iter=100,C=C,penalty='l2')
    with threadpool_limits(limits=2),warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        model.fit(sc.transform(imp.transform(train[FEATURES])),train.late)
    return imp,sc,model

def transform(part,imp,sc): return sc.transform(imp.transform(part[FEATURES]))

def evaluate(y,p,threshold):
    y,p=np.asarray(y),np.asarray(p,float)
    if p.shape!=y.shape or not np.isfinite(p).all() or not ((p>=0)&(p<=1)).all():
        raise ValueError('Điểm cần trong [0,1] và khớp nhãn')
    if not 0<=threshold<=1: raise ValueError('Ngưỡng cần trong [0,1]')
    out=measure(y,p>=threshold)
    out.update(threshold=threshold,cost=out['cost_fp_5fn'],log_loss=float(log_loss(y,p,labels=[0,1])),
               brier=float(brier_score_loss(y,p)),ap=float(average_precision_score(y,p)) if (y==1).any() else None,
               auc=float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None)
    return out

def select_threshold(y,p,grid=THRESHOLDS):
    rows=[evaluate(y,p,t) for t in grid]
    best=min(rows,key=lambda r:(r['cost'],r['alerts'],-r['threshold']))
    return rows,best

def plot_confusion(ax,report,title,labels=('Đúng hạn','Trễ')):
    values=np.array([[report['tn'],report['fp']],[report['fn'],report['tp']]])
    ax.imshow(values,cmap='Blues',vmin=0)
    for i,row in enumerate([['TN','FP'],['FN','TP']]):
        for j,name in enumerate(row):
            ax.text(j,i,f'{name}\n{values[i,j]:,}',ha='center',va='center',fontsize=23,
                    color='white' if values[i,j]>values.max()*.55 else '#172C43')
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=labels,yticklabels=labels,
           xlabel='Dự đoán',ylabel='Nhãn thật',title=title)
