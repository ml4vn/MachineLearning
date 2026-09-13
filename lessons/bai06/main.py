"""CART: quét nhát cắt, theo đường đi và kiểm trên Olist."""
from pathlib import Path
import sys
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier,plot_tree
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from threadpoolctl import threadpool_limits
from mlcourse.common import parser,setup,figure,save_figure,write_json,write_csv,finish,COLORS
from mlcourse.olist import prepare_olist,FEATURES
from mlcourse.classification import fit_logistic,transform,evaluate,select_threshold,plot_confusion
from lessons.bai06.algorithms import gini,enumerate_splits,export_tree,walk,impurity_contributions,toy_data

def toy(args):
    X,y=toy_data();root=enumerate_splits(X,y);best=max(root,key=lambda r:r['gain'])
    right=X[:,1]>15;child=enumerate_splits(X[right],y[right]);best_child=max(child,key=lambda r:r['gain'])
    m=DecisionTreeClassifier(random_state=args.seed).fit(X,y)
    nodes=export_tree(m);terms=impurity_contributions(nodes,2)
    write_csv(args.output_dir/'toy_12_orders.csv',pd.DataFrame({'id':[f'M{i:02d}' for i in range(1,13)],'distance_100km':X[:,0],'promised_days':X[:,1],'late':y}))
    write_csv(args.output_dir/'toy_root_candidates.csv',root);write_csv(args.output_dir/'toy_child_candidates.csv',child)
    write_json(args.output_dir/'toy_tree_nodes.json',nodes)
    fig,axes=figure('Bài 6 · Từ các điểm dữ liệu đến một cây',2)
    for label,name,c in [(0,'Đúng hạn',COLORS[0]),(1,'Trễ',COLORS[3])]:
        mask=y==label;axes[0,0].scatter(X[mask,0],X[mask,1],s=120,c=c,label=name)
    for i,(a,b) in enumerate(X): axes[0,0].annotate(f'M{i+1:02d}',(a,b),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
    axes[0,0].axhline(15,ls='--',c=COLORS[2]);axes[0,0].plot([10,10],[15,24],'--',c=COLORS[4])
    axes[0,0].set(xlabel='Khoảng cách (đơn vị 100 km)',ylabel='Hứa giao (ngày)',ylim=(6,25),title='12 đơn mô phỏng');axes[0,0].legend(loc='upper left')
    plot_tree(m,feature_names=['distance_100km','promised_days'],class_names=['Đúng hạn','Trễ'],filled=True,rounded=True,fontsize=12,ax=axes[0,1])
    axes[0,1].set_title('Cây nhỏ đầy đủ: 3 lá, 5 nút')
    save_figure(fig,args,'toy_tree','Nhát cắt thứ hai chỉ áp dụng trong nhánh phải · value = [số đúng hạn, số trễ]; samples là tổng số mẫu.')
    prune=[{'alpha':a,'leaves':l,'R':r,'objective':r+a*l} for a in [0,.1,.25,.3] for l,r in [(3,0),(2,.25),(1,.5)]]
    write_csv(args.output_dir/'toy_pruning.csv',prune)
    ccp=m.cost_complexity_pruning_path(X,y)
    xx=np.array([[0,0],[0,1],[1,0],[1,1]]);yy=np.array([0,1,1,0]);xor=[]
    for dep,minimum in [(1,0),(2,0),(2,.01)]:
        q=DecisionTreeClassifier(max_depth=dep,min_impurity_decrease=minimum,random_state=args.seed).fit(xx,yy)
        xor.append({'depth':dep,'min_impurity_decrease':minimum,'accuracy':q.score(xx,yy),'leaves':q.get_n_leaves()})
    write_csv(args.output_dir/'toy_xor.csv',xor)
    xm,ym=make_moons(n_samples=600,noise=.30,random_state=17)
    ids=np.arange(len(xm));it,iv=train_test_split(ids,test_size=.5,stratify=ym,random_state=42)
    write_csv(args.output_dir/'toy_moons.csv',pd.DataFrame({'id':ids,'x1':xm[:,0],'x2':xm[:,1],'y':ym,'split':np.where(np.isin(ids,it),'train','validation')}))
    complexity=[];models={}
    for dep in [1,2,3,4,5,6,8,12,None]:
        q=DecisionTreeClassifier(max_depth=dep,random_state=args.seed).fit(xm[it],ym[it]);models[dep]=q
        complexity.append({'depth':'unlimited' if dep is None else dep,'leaves':q.get_n_leaves(),'train_accuracy':q.score(xm[it],ym[it]),'validation_accuracy':q.score(xm[iv],ym[iv])})
    write_csv(args.output_dir/'toy_complexity.csv',complexity)
    fig,axes=figure('Bài 6 · Cây sâu có thể ghi nhớ nhiễu',2)
    gx,gy=np.meshgrid(np.linspace(xm[:,0].min()-.3,xm[:,0].max()+.3,200),np.linspace(xm[:,1].min()-.3,xm[:,1].max()+.3,160))
    for ax,dep in zip(axes[0],[2,None]):
        pred=models[dep].predict(np.c_[gx.ravel(),gy.ravel()]).reshape(gx.shape)
        ax.contourf(gx,gy,pred,levels=[-.5,.5,1.5],colors=[COLORS[0],COLORS[3]],alpha=.2)
        ax.scatter(xm[iv,0],xm[iv,1],c=ym[iv],cmap='coolwarm',s=16,edgecolor='none')
        title='Không giới hạn' if dep is None else f'Độ sâu {dep}'
        ax.set(xlabel='x1 mô phỏng',ylabel='x2 mô phỏng',title=f'{title} · {models[dep].get_n_leaves()} lá')
    save_figure(fig,args,'toy_regions','Moons mô phỏng có nhiễu · Nền là vùng dự đoán; chấm là validation · Không dùng dữ liệu này như kết quả Olist.')
    fig,axes=figure('Bài 6 · Độ phức tạp cần đi cùng đánh giá',2)
    q=np.arange(len(complexity))
    for key,label in [('train_accuracy','Train'),('validation_accuracy','Validation')]:axes[0,0].plot(q,[r[key] for r in complexity],'o-',label=label)
    axes[0,0].set(xticks=q,xticklabels=[str(r['depth']).replace('unlimited','∞') for r in complexity],xlabel='Độ sâu tối đa',ylabel='Accuracy',title='Moons: train tốt hơn chưa đủ');axes[0,0].legend()
    alphas=np.linspace(0,.4,150)
    for leaves,R in [(3,0),(2,.25),(1,.5)]:axes[0,1].plot(alphas,R+alphas*leaves,label=f'{leaves} lá; R={R}')
    axes[0,1].axvline(.25,ls='--',c='gray');axes[0,1].set(xlabel='Alpha',ylabel=r'$R(T)+\alpha |L(T)|$',title='Cắt tỉa cây 12 đơn mô phỏng');axes[0,1].legend()
    save_figure(fig,args,'toy_complexity','R là tổng Gini lá có trọng số theo toàn train · Đường cắt tỉa không tìm kiếm mọi cây có thể có.')
    return {'root_best':best,'child_best':best_child,'global_gain':best['gain']+8/12*best_child['gain'],
            'mdi':terms/terms.sum(),'ccp_alphas':ccp.ccp_alphas,'ccp_impurities':ccp.impurities,'xor':xor,'complexity':complexity}

def real(args):
    d,audit=prepare_olist(args.data_dir);tr=d[d.split=='train'];va=d[d.split=='validation'];te=d[d.split=='test']
    write_json(args.output_dir/'preparation_audit.json',audit)
    imp=SimpleImputer(strategy='median').fit(tr[FEATURES]);sc=StandardScaler().fit(imp.transform(tr[FEATURES]))
    xt,xv=transform(tr,imp,sc),transform(va,imp,sc)
    candidates=[];models={}
    for depth in [3,6]:
        model=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=args.min_leaf,random_state=args.seed).fit(xt,tr.late)
        pv=model.predict_proba(xv)[:,1];models[depth]=(model,pv)
        candidates.append({'depth':depth,'leaves':model.get_n_leaves(),'nodes':model.tree_.node_count,'validation_ap':evaluate(va.late,pv,.5)['ap']})
    chosen=max(candidates,key=lambda r:(r['validation_ap'],-r['leaves']))
    model,pv=models[chosen['depth']];scan,pick=select_threshold(va.late,pv);t=pick['threshold']
    write_json(args.output_dir/'model_policy.json',{'candidates':candidates,'chosen_depth':chosen['depth'],'threshold':t,'min_samples_leaf':args.min_leaf,
               'selection':'validation AP; tie fewer leaves; threshold minimizes FP+5FN on validation','refit':False})
    xe=transform(te,imp,sc);pt=model.predict_proba(xe)[:,1];nodes=export_tree(model,sc.mean_,sc.scale_)
    write_json(args.output_dir/'tree_nodes.json',nodes)
    manual=np.array([walk(nodes,x)[1] for x in xe])
    if not np.allclose(manual,pt,rtol=0,atol=1e-15):raise AssertionError('Duyệt tự viết không khớp sklearn trên test')
    leaves=model.apply(xt)
    for row in nodes:
        if row['left']<0:
            if not np.isclose(tr.late.to_numpy()[leaves==row['node']].mean(),row['p']):raise AssertionError('Tỷ lệ lá sai')
    terms=impurity_contributions(nodes,len(FEATURES))
    if terms.sum()>0 and not np.allclose(terms/terms.sum(),model.feature_importances_):raise AssertionError('MDI sai')
    default=evaluate(te.late,pt,.5);selected=evaluate(te.late,pt,t)
    # Logistic cũng tự fit từ cùng raw, không đọc báo cáo của Bài 05.
    li,ls,lm=fit_logistic(tr);lpv=lm.predict_proba(transform(va,li,ls))[:,1];_,lchoice=select_threshold(va.late,lpv)
    lp=lm.predict_proba(transform(te,li,ls))[:,1];logistic=evaluate(te.late,lp,lchoice['threshold'])
    predictions=te[['order_id','late']+FEATURES].copy();predictions['score']=pt;predictions['leaf']=model.apply(xe);predictions['prediction']=(pt>=t).astype(int)
    write_csv(args.output_dir/'test_predictions.csv',predictions)
    write_csv(args.output_dir/'validation_thresholds.csv',scan);write_csv(args.output_dir/'depth_candidates.csv',candidates)
    with threadpool_limits(limits=2):
        pi=permutation_importance(model,xv,va.late,scoring='average_precision',n_repeats=5,random_state=args.seed,n_jobs=1)
    importance=pd.DataFrame({'feature':FEATURES,'mdi':model.feature_importances_,'permutation_mean_AP_drop':pi.importances_mean,'permutation_sd':pi.importances_std})
    write_csv(args.output_dir/'importance.csv',importance)
    fig,axes=figure('Bài 6 · Ba tầng đầu của cây Olist')
    plot_tree(model,max_depth=2,feature_names=FEATURES,class_names=['Đúng hạn','Trễ'],filled=True,rounded=True,fontsize=11,ax=axes[0,0])
    save_figure(fig,args,'real_tree_top','Ngưỡng trong hệ chuẩn hóa · Dấu (...) còn nhánh phía dưới; toàn bộ cây và ngưỡng hệ gốc có trong tree_nodes.json.')
    fig,axes=figure('Bài 6 · Đổi ngưỡng làm thay đổi cả hai loại lỗi',2)
    plot_confusion(axes[0,0],default,'Ngưỡng 0,50');plot_confusion(axes[0,1],selected,f'Ngưỡng validation chọn {t:.2f}')
    save_figure(fig,args,'real_confusion','Test Olist cùng nhóm đơn Bài 05 · Tỷ lệ lớp ở lá chưa bảo đảm hiệu chuẩn hay chất lượng cho từng đơn.')
    fig,axes=figure('Bài 6 · Hai cách đo tầm quan trọng',2);fig.subplots_adjust(left=.16,wspace=.65)
    names=['Khoảng cách','Hứa giao','Giá','Cước','Số món','Cân nặng']
    axes[0,0].barh(names,importance.mdi);axes[0,0].set(xlabel='MDI (tổng = 1 nếu có gain)',title='Giảm Gini trên train')
    axes[0,1].barh(names,pi.importances_mean,xerr=pi.importances_std,capsize=4,color=COLORS[2]);axes[0,1].axvline(0,c='gray')
    axes[0,1].set(xlabel='Mức giảm AP validation',title='Hoán vị từng cột, năm lần')
    save_figure(fig,args,'real_importance','Thanh sai số là SD qua năm lần hoán vị, không phải khoảng tin cậy · Hai biểu đồ có thang đo khác nhau.')
    # Chọn một TP nếu có, nếu không chọn dòng đầu. Ví dụ được chọn có chủ đích để đọc đường đi.
    positions=np.flatnonzero((te.late.to_numpy()==1)&(pt>=t));pos=int(positions[0]) if len(positions) else 0
    leaf,prob,path=walk(nodes,xe[pos]);example=te.iloc[pos]
    rows=[{**r,'feature_name':FEATURES[r['feature']],
           'raw_value':float(imp.transform(te.iloc[[pos]][FEATURES])[0,r['feature']])} for r in path]
    write_csv(args.output_dir/'one_order_path.csv',rows)
    fig,axes=figure('Bài 6 · Theo đúng đường đi của một đơn thật');ax=axes[0,0];ax.axis('off')
    lines=[f'ID {example.order_id} · Nhãn thật: {int(example.late)}']
    for r in path:
        j=r['feature'];value=float(imp.transform(te.iloc[[pos]][FEATURES])[0,j])
        lines.append(f'Nút {r["node"]}: {FEATURES[j]} = {value:.4f}  '+('≤' if r['go_left'] else '>')+f'  {r["threshold_raw"]:.4f} → '+('trái' if r['go_left'] else 'phải'))
    lines.append(f'Lá {leaf}: {nodes[leaf]["positive"]}/{nodes[leaf]["n"]} đơn train trễ → p = {prob:.6f}')
    lines.append(f'Ngưỡng {t:.2f} → '+('cảnh báo' if prob>=t else 'không cảnh báo'))
    ax.text(0,.98,'\n\n'.join(lines),fontsize=17,va='top',transform=ax.transAxes)
    save_figure(fig,args,'real_one_path','Số hiển thị được làm tròn; tính toán dùng ngưỡng đầy đủ và float32 theo sklearn · Đây là ví dụ được chọn có chủ đích.')
    return {'preparation':audit,'depth_candidates':candidates,'selected_depth':chosen['depth'],'selected_threshold':t,
            'test_default':default,'test_selected':selected,'logistic_test_selected':logistic,
            'nodes':len(nodes),'leaves':model.get_n_leaves(),'manual_all_test_matches':True,
            'importance':importance.to_dict('records'),'example':{'order_id':example.order_id,'leaf':leaf,'p':prob},
            'test_scope':'Historical course holdout; no independent new test.'}

def main():
    p=parser(6,'Cây quyết định và cảnh báo giao trễ Olist')
    p.add_argument('--min-leaf',type=int,default=200,help='Số mẫu train tối thiểu ở lá cây thật')
    args=p.parse_args()
    if args.min_leaf<1:p.error('--min-leaf phải >= 1')
    setup(args);out={}
    if args.mode in ['toy','all']:out['toy']=toy(args)
    if args.mode in ['real','all']:out['real']=real(args)
    finish(args,6,out)

if __name__=='__main__':main()
