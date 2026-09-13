"""Hình khoa học tái tạo được từ phép tính và kết quả huấn luyện."""
import numpy as np
from mlcourse.common import figure, save_figure, COLORS
from mlcourse.fashion import NAMES
from .algorithms import XOR, XOR_Y, TINY_THETA, PARAM_NAMES, xor_hidden, sigmoid, forward

def plot_toy(args, report):
    fig, axes = figure("XOR: biểu diễn phi tuyến giúp tách bốn điểm", ncols=3)
    for c in [0,1]:
        sel=XOR_Y==c
        axes[0,0].scatter(*XOR[sel].T,s=140,color=COLORS[c],label=f"y={c}")
        axes[0,1].scatter(*xor_hidden(XOR)[sel].T,s=140,color=COLORS[c],label=f"y={c}")
    axes[0,0].set(xlim=(-.3,1.3),ylim=(-.3,1.3),xlabel="x₁",ylabel="x₂",title="Tọa độ gốc"); axes[0,0].legend()
    line=np.linspace(-.2,2.2,100); axes[0,1].plot(line,(2*line-1)/4,"--",color=COLORS[2])
    axes[0,1].set(xlim=(-.3,2.3),ylim=(-.3,1.3),xlabel="h₁=ReLU(x₁+x₂)",ylabel="h₂=ReLU(x₁+x₂−1)",title="Hai điểm y=1 trùng nhau")
    xx,yy=np.meshgrid(np.linspace(-.3,1.3,180),np.linspace(-.3,1.3,180)); grid=np.c_[xx.ravel(),yy.ravel()]
    z=(xor_hidden(grid)@[2,-4]-1).reshape(xx.shape)
    axes[0,2].contourf(xx,yy,z>=0,levels=[-.5,.5,1.5],colors=COLORS[:2],alpha=.25)
    axes[0,2].contour(xx,yy,z,levels=[0],colors=[COLORS[2]])
    axes[0,2].scatter(*XOR.T,c=[COLORS[c] for c in XOR_Y],s=140)
    axes[0,2].set(xlabel="x₁",ylabel="x₂",title="Nghiệm dựng: z=2h₁−4h₂−1")
    save_figure(fig,args,"toy_xor","Tầng ẩn được đặt sẵn trong ví dụ này. Nghiệm dựng đúng 4/4 điểm; không phải kết quả học sau một bước GD.")
    fig,axes=figure("Một bước GD: tính lại xác suất rồi mới kết luận",ncols=2)
    labels=["(0,0)","(0,1)","(1,0)","(1,1)"]; pos=np.arange(4)
    axes[0,0].bar(pos-.18,np.full(4,.5),width=.35,label="Trước bước",color=COLORS[0])
    axes[0,0].bar(pos+.18,report["next_probabilities"],width=.35,label="Sau bước η=8",color=COLORS[1])
    axes[0,0].set(xticks=pos,xticklabels=labels,ylim=(0,1),xlabel="Điểm XOR",ylabel="p(y=1)");axes[0,0].legend()
    vals=[report["initial_loss"],report["next_loss"],report["constructed_loss"]]
    bars=axes[0,1].bar(["Ban đầu","Sau 1 bước","Nghiệm dựng"],vals,color=COLORS[:3]);axes[0,1].bar_label(bars,fmt="%.4f",padding=5);axes[0,1].set(ylabel="BCE trung bình",ylim=(0,.85))
    save_figure(fig,args,"toy_update",r"$\nabla_{(v_1,v_2,c)}L=(0,1/8,0)$; sau bước: (0,−1,0). η=8 chỉ được kiểm trên ví dụ riêng này.")
    fig,axes=figure("Backpropagation: chín đạo hàm được kiểm độc lập",ncols=2)
    ax=axes[0,0];ax.axis("off");t=report["tiny"]
    text=["x = (0,6; 0,2),  y = 1",f"a = W x + b = ({t['preactivation'][0]:.2f}; {t['preactivation'][1]:.2f})",f"h = ReLU(a) = ({t['hidden'][0]:.2f}; {t['hidden'][1]:.2f})",f"z = vᵀh+c = {t['logit']:.3f}",f"p = σ(z) = {t['probability']:.6f}",f"δ = p−y = {t['delta']:.6f}",r"$\delta_h=\delta\,v\odot\mathbf{1}_{a>0}$",r"$\nabla_W L=\delta_h x^T$"]
    for i,line in enumerate(text): ax.text(.02,.93-i*.115,line,fontsize=17,color=COLORS[0 if i<5 else 3])
    ax=axes[0,1];ax.scatter(t["gradient"],report["numeric_gradient"],s=65,color=COLORS[2]);ax.plot([-.5,.2],[-.5,.2],"--",color=COLORS[0]);ax.set(xlabel="Gradient theo quy tắc dây chuyền",ylabel="Gradient sai phân hữu hạn",title=f"Sai khác lớn nhất: {report['max_gradient_error']:.2e}")
    for i,name in enumerate(PARAM_NAMES): ax.annotate(name,(t["gradient"][i],report["numeric_gradient"][i]),xytext=(4,7 if i%2 else -13),textcoords="offset points",fontsize=10)
    save_figure(fig,args,"toy_backprop","Tất cả gradient dùng cùng tham số cũ. Ví dụ tránh điểm gãy ReLU; bảng 9 tham số và cập nhật nằm trong CSV.")

def plot_real(args,d,report,arrays):
    W1,b1,W2,b2=[arrays[k] for k in ["W1","b1","W2","b2"]]
    p=report["protocol"];runs=report["mlp_runs"];history=np.asarray(arrays["history"])
    fig,axes=figure("Mạng ảnh 784 → 64 → 10: 50.890 tham số cần học")
    ax=axes[0,0];ax.axis("off")
    boxes=[(.02,"Ảnh xám\n28 × 28\n784 pixel / 255"),(.36,"Tầng ẩn\n64 neuron ReLU\nh = ReLU(xW₁+b₁)"),(.70,"Tầng ra\n10 logits → softmax\np₀ + … + p₉ = 1")]
    for x,label in boxes: ax.text(x,.6,label,transform=ax.transAxes,fontsize=20,va="center",bbox=dict(boxstyle="round,pad=.7",fc="#E5EDF3",ec=COLORS[0]))
    for x in [.29,.63]: ax.annotate("",xy=(x+.065,.6),xytext=(x,.6),xycoords="axes fraction",arrowprops=dict(arrowstyle="->",lw=3,color=COLORS[2]))
    ax.text(.02,.24,"W₁: 784×64; b₁: 64       W₂: 64×10; b₂: 10",fontsize=22,color=COLORS[0])
    ax.text(.02,.1,f"Một epoch: {p['train']:,} ảnh, batch=256 → {p['updates_per_epoch']} lần cập nhật Adam",fontsize=20)
    save_figure(fig,args,"real_architecture","Backprop tính gradient; Adam dùng gradient và trạng thái tích lũy để cập nhật trọng số. Nhãn dùng cho loss khi học.")
    h=history[history[:,0]==p["primary_seed"]];selected=runs[0]["selected_epoch"]
    fig,axes=figure("Epoch cuối chưa chắc là checkpoint phù hợp nhất",ncols=2)
    ax=axes[0,0];ax.plot(h[:,1],h[:,2],label="Train CE");ax.plot(h[:,1],h[:,3],label="Validation CE");ax.axvline(selected,linestyle=":",color=COLORS[2],label=f"Chọn epoch {selected}");ax.set(xlabel="Epoch",ylabel="CE trung bình, chưa cộng L2");ax.legend()
    ax=axes[0,1]
    for run in runs:
        hs=history[history[:,0]==run["seed"]];ax.plot(hs[:,1],hs[:,5]/p["validation"],label=f"Seed {run['seed']}")
    ax.set(xlabel="Epoch",ylabel="Accuracy validation");ax.legend()
    save_figure(fig,args,"real_learning","Chọn epoch bằng validation CE; seed chính được ấn định trước. Các seed còn lại mô tả biến động của quá trình học.")
    fig,axes=figure("Đọc lỗi theo từng lớp trên cùng tập validation",ncols=2)
    matrices=[np.asarray(report["baseline_validation"]["confusion"]),np.asarray(runs[0]["validation"]["confusion"])]
    vmax=max(cm.max() for cm in matrices)
    for ax,cm,title in zip(axes.flat,matrices,["Logistic 784 pixel",f"MLP, seed {p['primary_seed']}, epoch {selected}"]):
        ax.imshow(cm,cmap="Blues",vmin=0,vmax=vmax)
        for i in range(10):
            for j in range(10): ax.text(j,i,str(cm[i,j]),ha="center",va="center",fontsize=10,color="white" if cm[i,j]>vmax*.55 else "#253348")
        ax.set(title=title,xticks=range(10),yticks=range(10),xlabel="Nhãn dự đoán (0–9)",ylabel="Nhãn thật (0–9)")
    save_figure(fig,args,"real_confusion","Mỗi hàng có 300 ảnh thật; ô chéo là dự đoán đúng. Mã 0–9 và tên sản phẩm được giải thích trong README.")
    fig,axes=figure("Xem cả ảnh được sửa lỗi lẫn ảnh mô hình mới làm sai",ncols=3,nrows=3)
    fig.subplots_adjust(hspace=.58)
    categories=["MLP sửa lỗi baseline","Cả hai cùng sai","MLP sai, baseline đúng"]
    for row,category in enumerate(categories):
        examples=[e for e in report["examples"] if e["category"]==category]
        for col,ax in enumerate(axes[row]):
            ax.set_xticks([]);ax.set_yticks([])
            if col>=len(examples): ax.axis("off");continue
            e=examples[col];pos=e["validation_position"]
            ax.imshow(d["validation"][pos].reshape(28,28),cmap="gray",vmin=0,vmax=1,interpolation="nearest")
            ax.set_title(f"{e['source_id']} · thật {e['truth']}\nMLP {e['mlp']} / baseline {e['baseline']}",fontsize=11)
            if col==0: ax.set_ylabel(category,fontsize=11)
    save_figure(fig,args,"real_error_images","Mỗi hàng lấy tối đa 3 ảnh đầu tiên thỏa điều kiện trên validation. Chỉ minh họa lỗi, không suy ra nguyên nhân nhân quả.")
    chosen=int(arrays["chosen_position"]);_,logits,prob=forward(d["validation"][[chosen]],W1,b1,W2,b2)
    fig,axes=figure("Theo dấu một ảnh: 784 số → 64 kích hoạt → 10 xác suất",ncols=2)
    ax=axes[0,0];ax.imshow(d["validation"][chosen].reshape(28,28),cmap="gray",vmin=0,vmax=1,interpolation="nearest");ax.axis("off");ax.set_title(f"train:{d['validation_ids'][chosen]} · thật: {NAMES[d['y_validation'][chosen]]}")
    ax=axes[0,1];bars=ax.barh(NAMES,prob[0],color=[COLORS[2] if j==logits.argmax(1)[0] else COLORS[0] for j in range(10)]);ax.bar_label(bars,labels=[f"{v:.3f}" for v in prob[0]],padding=4,fontsize=10);ax.set(xlim=(0,1.12),xlabel="Xác suất mô hình (chưa hiệu chỉnh)");ax.invert_yaxis()
    save_figure(fig,args,"real_one_image","Xác suất lớn nhất không bảo đảm dự đoán đúng. Pixel, 64 kích hoạt, logits và xác suất của ảnh đều có tệp số đi kèm.")
    fig,axes=figure("Kết quả test của hai cấu hình đã chốt",ncols=2)
    vals=[report["baseline_test"]["accuracy"],report["mlp_test"]["accuracy"]]
    bars=axes[0,0].bar(["Logistic","MLP chính"],vals,color=COLORS[:2]);axes[0,0].bar_label(bars,labels=[f"{v:.2%}" for v in vals],padding=5);axes[0,0].set(ylim=(0,1),ylabel="Accuracy trên 10.000 ảnh test")
    axes[0,1].plot(range(10),report["baseline_test"]["recall"],"o-",label="Logistic");axes[0,1].plot(range(10),report["mlp_test"]["recall"],"s-",label="MLP chính");axes[0,1].set(xticks=range(10),ylim=(0,1.05),xlabel="Mã lớp",ylabel="Recall từng lớp");axes[0,1].legend()
    save_figure(fig,args,"real_test_results",f"Chênh {report['test_delta_correct']} ảnh đúng; test công khai đã có kết quả pilot trước đó. Chưa đại diện ảnh cửa hàng tùy ý.")
