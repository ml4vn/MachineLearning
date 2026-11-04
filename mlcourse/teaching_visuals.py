"""Minh họa  dùng lại thuật toán của từng bài, không huấn luyện mô hình mới."""
import json
import textwrap
import numpy as np
from .common import ROOT, COLORS, figure, save_figure, write_csv


def recap(args, lesson):
    """Bản đồ ba chặng lấy từ cùng nguồn với hướng dẫn thực hành."""
    config = json.loads((ROOT / f'examples/bai{lesson:02d}/teaching.json').read_text(encoding='utf-8'))
    fig, axes = figure(f'Bài {lesson} · {config["recap_title"]}', 3)
    for i, (ax, stage) in enumerate(zip(axes[0], config['stages'])):
        ax.axis('off')
        ax.text(.05, .88, str(i+1), fontsize=34, weight='bold', color=COLORS[i], transform=ax.transAxes)
        ax.text(.05, .73, stage['title'], fontsize=20, weight='bold', transform=ax.transAxes)
        ax.text(.05, .58, '\n'.join(textwrap.wrap(stage['explain'], 29)), fontsize=16,
                va='top', linespacing=1.5, transform=ax.transAxes)
        ax.text(.05, .22, stage['formula'], fontsize=17, color=COLORS[i], transform=ax.transAxes)
        if i < 2:
            ax.annotate('', xy=(1.06,.73), xytext=(.9,.73), xycoords='axes fraction',
                        arrowprops=dict(arrowstyle='->', lw=2, color=COLORS[2]), annotation_clip=False)
    fig.text(.08, .18, '\n'.join(textwrap.wrap(config['takeaway'], 112)), fontsize=15, weight='bold')
    save_figure(fig, args, 'summary', 'Tổng kết ví dụ chuẩn · Dự đoán bằng tay → chạy ví dụ → đọc số liệu → giải thích giới hạn.')


def gd_two_parameters(args):
    from examples.bai04.algorithms import loss_gradient
    x=np.array([1.,2.,3.,4.]); y=np.array([3.,4.,6.,7.]); A=np.c_[x,np.ones(4)]
    old=np.array([.5,1.]); eta=.05
    loss, grad=loss_gradient(A,y,old); updated=old-eta*grad
    # Use the existing gradient implementation for every simultaneous update.
    theta=old.copy(); rows=[]
    for step in range(81):
        j,g=loss_gradient(A,y,theta)
        rows.append(dict(step=step,w=theta[0],b=theta[1],J=j,gradient_w=g[0],gradient_b=g[1]))
        theta=theta-eta*g
    write_csv(args.output_dir/'toy_wb_history.csv',rows)
    fig,axes=figure('Bài 4 · Cùng tham số cũ, cập nhật đồng thời w và b',2)
    ax=axes[0,0]; ax.axis('off')
    lines=[r'$\hat y_i=wx_i+b,\quad e_i=\hat y_i-y_i$',
           r'$J(w,b)=\frac{1}{2n}\sum_i e_i^2$',
           r'$g_w=\frac{1}{n}\sum_i e_ix_i,\quad g_b=\frac{1}{n}\sum_i e_i$',
           r'$(w,b)\leftarrow(w-\eta g_w,\ b-\eta g_b)$']
    for j,line in enumerate(lines): ax.text(0,.92-j*.23,line,fontsize=20)
    ax=axes[0,1]; ax.axis('off')
    lines=['Khởi tạo: w = 0,5; b = 1; η = 0,05',
           f'Gradient cùng điểm cũ: ({grad[0]:g}; {grad[1]:g})',
           f'Sau một bước: w = {updated[0]:.4f}; b = {updated[1]:.4f}',
           f'J: {loss:.6f} → {loss_gradient(A,y,updated)[0]:.6f}',
           'Lặp: dự đoán → tính hai gradient → cập nhật.',
           'Dừng theo số bước hoặc tiêu chí hội tụ đã chọn.']
    for j,line in enumerate(lines): ax.text(0,.92-j*.145,line,fontsize=16,color=COLORS[0])
    save_figure(fig,args,'toy_wb_update','Ví dụ mô phỏng · Tính cả hai gradient trước khi thay bất kỳ tham số nào; η = 0,05 chỉ là cấu hình của ví dụ.')
    fig,axes=figure('Bài 4 · Mặt J(w,b) và đường đồng mức là cùng một hàm',2)
    axes[0,0].remove(); ax=fig.add_subplot(1,2,1,projection='3d')
    ws=np.linspace(-.4,2.8,75); bs=np.linspace(-1,4,75); W,B=np.meshgrid(ws,bs)
    J=np.mean((W[...,None]*x+B[...,None]-y)**2,axis=-1)/2
    ax.plot_surface(W,B,J,cmap='viridis',alpha=.8,linewidth=0)
    ax.plot([r['w'] for r in rows],[r['b'] for r in rows],[r['J'] for r in rows],c=COLORS[3],lw=3)
    ax.set(xlabel='w',ylabel='b',zlabel='J (ngày²)',title='Chiều cao là mức sai số'); ax.view_init(27,-65)
    ax=axes[0,1]; cs=ax.contour(W,B,J,levels=[.03,.08,.2,.5,1,2,5,10,20],cmap='viridis')
    ax.clabel(cs,fontsize=10); ax.plot([r['w'] for r in rows],[r['b'] for r in rows],'.-',c=COLORS[3],label='GD: 80 bước')
    ax.scatter([1.4],[1.5],s=180,marker='*',c=COLORS[1],label='OLS: (1,4; 1,5)')
    ax.set(xlabel='w',ylabel='b',title='Mỗi đường nối các điểm có cùng J'); ax.legend(fontsize=11)
    save_figure(fig,args,'toy_loss_surface','Cùng bốn quan sát · Mỗi điểm (w,b) là một mô hình; trục w và b không phải hai đặc trưng của đơn hàng.')


def gini_trace(args):
    from examples.bai06.algorithms import toy_data, gini
    X,y=toy_data(); left=X[:,1]<=15
    groups=[('Gốc',y),('Trái: ≤ 15 ngày',y[left]),('Phải: > 15 ngày',y[~left])]
    rows=[dict(node=name,n=len(labels),positive=int(labels.sum()),p=float(labels.mean()),gini=gini(labels)) for name,labels in groups]
    weighted=sum(r['n']/len(y)*r['gini'] for r in rows[1:]); gain=rows[0]['gini']-weighted
    write_csv(args.output_dir/'toy_gini_trace.csv',rows)
    fig,axes=figure('Bài 6 · Đếm lớp → tính tỷ lệ → đo độ lẫn → so nhát cắt',2)
    p=np.linspace(0,1,200); ax=axes[0,0]; ax.plot(p,2*p*(1-p),lw=3)
    ax.scatter([0,.5,1],[0,.5,0],s=110,c=COLORS[3]);ax.set(xlabel='p = tỷ lệ lớp trễ tại nút',ylabel='Gini',ylim=(-.05,.63),title=r'$G=1-p^2-(1-p)^2$')
    ax.text(.04,.55,'p = 0 hoặc 1: thuần một lớp',fontsize=15)
    ax.text(.5,.15,'p = 0,5: lẫn nhiều nhất (hai lớp)',fontsize=13,ha='center')
    ax=axes[0,1]; ax.axis('off')
    for j,r in enumerate(rows):
        yy=.88-j*.22
        ax.text(0,yy,r['node'],fontsize=17,weight='bold')
        ax.text(0,yy-.08,f"{r['positive']}/{r['n']} trễ → p={r['p']:.2f} → G={r['gini']:.3f}",fontsize=16)
    ax.text(0,.14,rf'$G_{{sau}}=\frac{{4}}{{12}}0+\frac{{8}}{{12}}0.375={weighted:.2f}$',fontsize=20)
    ax.text(0,.01,rf'$\Delta G=G_{{goc}}-G_{{sau}}={gain:.2f}$',fontsize=20,color=COLORS[2])
    save_figure(fig,args,'toy_gini_trace','Trọng số là số mẫu của từng nhánh / số mẫu tại nút cha; không lấy trung bình đều khi hai nhánh khác kích thước.')


def silhouette_trace(args):
    from examples.bai08.algorithms import silhouette_manual
    X=np.array([[0.],[2.],[10.],[12.]])
    s=silhouette_manual(X,[0,0,1,1])
    fig,axes=figure('Bài 8 · Silhouette: gần cụm mình, xa cụm khác',2)
    ax=axes[0,0];ax.scatter(X[:,0],[0]*4,c=[COLORS[0]]*2+[COLORS[1]]*2,s=180)
    for value in X[:,0]: ax.text(value,.1,f'{value:g}',ha='center',fontsize=17)
    for dest,height in [(0,-.2),(10,-.4),(12,-.6)]:
        ax.annotate('',xy=(dest,height),xytext=(2,height),arrowprops=dict(arrowstyle='<->',color=COLORS[2]))
        ax.text((2+dest)/2,height-.08,f'd = {abs(dest-2)}',ha='center',fontsize=14)
    ax.set(xlim=(-1,13),ylim=(-.9,.4),yticks=[],xlabel='Tọa độ mô phỏng',title='Xét điểm có tọa độ 2')
    ax=axes[0,1];ax.axis('off')
    for j,line in enumerate([r'$a(2)=|2-0|=2$',r'$b(2)=\frac{|2-10|+|2-12|}{2}=9$',r'$s(2)=\frac{b-a}{\max(a,b)}=\frac{7}{9}$',f'Kết quả mã: s(2) = {s[1]:.6f}', 'a không tính khoảng cách từ điểm tới chính nó.']):
        ax.text(0,.88-j*.18,line,fontsize=18 if j<4 else 14)
    save_figure(fig,args,'toy_silhouette','b là khoảng cách trung bình nhỏ nhất tới một cụm khác; singleton dùng quy ước s = 0.')


def covariance_trace(args):
    from examples.bai09.algorithms import POINTS,fit_pca_eigh
    mean,values,W=fit_pca_eigh(POINTS); C=(POINTS-mean).T@(POINTS-mean)/len(POINTS)
    fig,axes=figure('Bài 9 · Hiệp phương sai dẫn tới hướng giữ nhiều biến thiên',2)
    ax=axes[0,0]; ax.imshow(C,cmap='Blues',vmin=0,vmax=3)
    for i in range(2):
        for j in range(2): ax.text(j,i,f'{C[i,j]:.1f}',ha='center',va='center',fontsize=30,color='white')
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['x₁','x₂'],yticklabels=['x₁','x₂'],title=r'$S=\frac{1}{n}X_c^T X_c$ (toy: n = 4)')
    ax=axes[0,1]; ax.scatter(*(POINTS-mean).T,s=120,c=COLORS[0])
    for i in range(2):
        end=W[i]*np.sqrt(values[i]); ax.annotate('',xy=end,xytext=(0,0),arrowprops=dict(arrowstyle='->',lw=3,color=COLORS[i+1]))
        ax.text(end[0]+.08,end[1]+.1,f'λ{i+1} = {values[i]:g}',fontsize=17)
    ax.set(xlim=(-3,3),ylim=(-3,3),xlabel='x₁ − mean₁',ylabel='x₂ − mean₂',title='Hướng mũi tên: eigenvector; độ dài: √λ');ax.set_aspect('equal');ax.grid(alpha=.2)
    save_figure(fig,args,'toy_covariance','Toy chia n: λ = 4,5 và 0,5; sklearn chia n−1: λ = 6 và 2/3. Cả hai có EVR = 90% và 10%.')


def backprop_path(args, tiny):
    from examples.bai10.algorithms import TINY_THETA
    d=float(tiny['delta']); v=float(TINY_THETA[6]); x=float(tiny['x'][0]); grad=d*v*x
    np.testing.assert_allclose(grad,tiny['gradient'][0],atol=1e-14)
    fig,axes=figure('Bài 10 · Theo đúng một đường từ w₁₁ đến loss',2)
    ax=axes[0,0];ax.axis('off')
    labels=[r'$w_{11}=0.5$',r'$a_1=0.32$',r'$h_1=0.32$',r'$s=0.204$',r'$p=0.550824$']
    for j,label in enumerate(labels):
        yy=.91-j*.19;ax.text(.2,yy,label,fontsize=23,ha='center')
        if j<4: ax.annotate('',xy=(.2,yy-.11),xytext=(.2,yy-.035),arrowprops=dict(arrowstyle='->',color=COLORS[2],lw=2))
    ax.text(.53,.81,r'$x_1=0.6$',fontsize=18);ax.text(.53,.62,r"$ReLU'(a_1)=1$",fontsize=18);ax.text(.53,.43,r'$v_1=0.7$',fontsize=18)
    ax=axes[0,1];ax.axis('off')
    lines=[r'$\delta=\partial L/\partial s=p-y$',f'δ = {d:.6f} (y = 1)',r'$\frac{\partial L}{\partial w_{11}}=\delta\,v_1\,1_{a_1>0}\,x_1$',f'= ({d:.6f}) × 0,7 × 1 × 0,6',f'= {grad:.6f}',f'w₁₁ mới = 0,5 − 0,1 × ({grad:.6f})',f'= {0.5-.1*grad:.6f}']
    for j,line in enumerate(lines): ax.text(0,.93-j*.135,line,fontsize=20 if j==2 else 17,color=COLORS[3 if j>1 else 0])
    save_figure(fig,args,'toy_backprop_path','Đi xuôi tính a, h, s, p; đi ngược nhân đạo hàm dọc đường. Dùng toàn bộ trọng số cũ trước khi cập nhật đồng thời.')
