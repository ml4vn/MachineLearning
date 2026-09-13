"""Chạy Bài 2: theo dấu SMS thật và giải thích kNN."""
from pathlib import Path
import sys
if __package__ in (None,""):sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import textwrap
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix,f1_score
from sklearn.preprocessing import StandardScaler
from mlcourse.common import parser,setup,finish,figure,save_figure,write_csv,COLORS
from mlcourse.sms import FEATURES,fit_sms
from lessons.bai02.algorithms import knn_steps

def toy(args):
    X=np.array([[0,0],[2,0],[0,3],[4,4],[1,4]],float)
    y=np.array([0,1,1,0,0]);q=np.array([1,1])
    a=knn_steps(X,y,q,3);b=knn_steps(X,y,q,5)
    experiment=knn_steps(X,y,q,args.k,args.weighted)
    np.testing.assert_array_equal(a["d2"],[2,2,5,18,9])
    rows=[{"point":f"P{i+1}","x1":x[0],"x2":x[1],"label":int(y[i]),"d2":a["d2"][i],
           "selected_k3":bool(i in a["chosen"])} for i,x in enumerate(X)]
    write_csv(args.output_dir/"toy_neighbors.csv",rows)
    fig,axs=figure("Bài 2 · Đo khoảng cách, chọn láng giềng, rồi bỏ phiếu",ncols=2)
    ax=axs[0,0]
    for label,color in [(0,COLORS[0]),(1,COLORS[1])]:
        ax.scatter(X[y==label,0],X[y==label,1],s=170,color=color,label=f"Nhãn {label}")
    for i,x in enumerate(X):ax.annotate(f"P{i+1}",x,xytext=(9,8),textcoords="offset points")
    for j in a["chosen"]:ax.plot([q[0],X[j,0]],[q[1],X[j,1]],"--",alpha=.5,color="#718091")
    ax.scatter(*q,s=230,marker="*",color="#B64A64",label="Query (1,1)")
    ax.set(xlim=(-.5,5),ylim=(-.5,5),xlabel="Đặc trưng 1",ylabel="Đặc trưng 2");ax.legend(loc="lower right")
    axs[0,1].bar(["k=3","k=5"],[a["vote_fraction"],b["vote_fraction"]],color=COLORS[:2])
    axs[0,1].axhline(.5,color="#617084",ls="--");axs[0,1].set(ylim=(0,1),ylabel="Tỷ lệ phiếu cho nhãn 1",title="Cùng query, đổi k có thể đổi nhãn")
    save_figure(fig,args,"toy_knn","Dữ liệu mô phỏng · k=3 dự đoán 1; k=5 dự đoán 0 · Phiếu không đồng nghĩa chắc chắn.")
    return {"k3":a,"k5":b,"your_experiment":{"k":args.k,"weighted":args.weighted,**experiment}}

def real(args):
    result=fit_sms(args.data_dir,args.seed)
    d,tr,va,te=(result[k] for k in ["data","train","validation","test"])
    sc=result["scaler"]
    write_csv(args.output_dir/"real_features.csv",d.drop(columns="normal"))
    write_csv(args.output_dir/"validation_grid.csv",result["grid"])
    for split,ids,scores in [("validation",va,result["val_score"]),("test",te,result["test_score"])]:
        out=d.loc[ids,["source_record","message_id","label","y",*FEATURES]].copy()
        out["score"]=scores;out["prediction"]=(scores>.5).astype(int)
        write_csv(args.output_dir/f"{split}_predictions.csv",out)
    query_rows=d.loc[d.source_record==4500]
    if len(query_rows)!=1:raise ValueError("Không tìm thấy SMS minh họa nguồn 4500")
    qi=query_rows.index[0];q=d.loc[[qi],FEATURES].to_numpy()
    if qi in tr:
        qi=va[0]  # Khi đổi seed, chọn một query validation thay vì cho train tự bỏ phiếu.
        q=d.loc[[qi],FEATURES].to_numpy()
    query_source=int(d.loc[qi,"source_record"])
    demo=[]
    fig,axs=figure("Bài 2 · Một SMS thật đi qua hai cách đo gần",ncols=2)
    for j,scaled in enumerate([False,True]):
        X=d.loc[tr,FEATURES].to_numpy();query=q[0]
        if scaled:X=sc.transform(X);query=sc.transform(q)[0]
        manual=knn_steps(X,d.loc[tr,"y"].to_numpy(),query,3)
        ax=axs[0,j]
        for label,color in [(0,COLORS[0]),(1,COLORS[1])]:
            mask=d.loc[tr,"y"].to_numpy()==label
            ax.scatter(X[mask,0],X[mask,1],s=10,alpha=.3,color=color,label=["ham","spam"][label])
        ax.scatter(*query,s=160,marker="*",color="#BA4262",label=f"SMS nguồn {query_source}")
        for rank,pos in enumerate(manual["chosen"],1):
            row=d.loc[tr[pos]]
            ax.scatter(*X[pos],s=110,facecolors="none",edgecolors="black")
            demo.append({"scaled":scaled,"rank":rank,"source_record":int(row.source_record),
                         "label":row.label,"text":row.text,"n_chars":int(row.n_chars),
                         "digit_fraction":float(row.digit_fraction),"d2":float(manual["d2"][pos])})
        ax.set(xlabel="n_chars (z)" if scaled else "n_chars",ylabel="digit_fraction (z)" if scaled else "digit_fraction",
               title=f"{'Có' if scaled else 'Không'} scale · k=3 → {['ham','spam'][manual['prediction']]}")
        ax.legend(loc="upper right",fontsize=10)
    save_figure(fig,args,"real_neighbors","Nguồn UCI SMS · Chỉ train được bỏ phiếu · Query chọn để minh họa, không là bằng chứng chất lượng chung.")
    write_csv(args.output_dir/"real_query_neighbors.csv",demo)
    fig,axs=figure("Bài 2 · Truy tới đúng ba láng giềng của một SMS",ncols=2)
    for j,scaled in enumerate([False,True]):
        ax=axs[0,j];ax.axis("off")
        cells=[[r["rank"],r["source_record"],r["label"],r["n_chars"],
                f'{r["digit_fraction"]:.4f}',f'{np.sqrt(r["d2"]):.4f}']
               for r in demo if r["scaled"]==scaled]
        tab=ax.table(cellText=cells,colLabels=["Hạng","ID nguồn","Nhãn","Ký tự","Tỷ lệ số","d"],
                     loc="center",cellLoc="center",colWidths=[.11,.19,.14,.16,.21,.19])
        tab.auto_set_font_size(False);tab.set_fontsize(12);tab.scale(1,3)
        for (i,k),cell in tab.get_celld().items():
            cell.set_edgecolor("#D5E0E9")
            if i==0:cell.set_facecolor(COLORS[0]);cell.set_text_props(color="white",weight="bold")
            else:cell.set_facecolor("#EAF2F7" if i%2 else "#F8FAFC")
        spam=sum(r["label"]=="spam" for r in demo if r["scaled"]==scaled)
        ax.set_title(f"{'Sau' if scaled else 'Trước'} chuẩn hóa: {spam} spam, {3-spam} ham")
    save_figure(fig,args,"real_neighbor_table",
                "Cột ký tự và tỷ lệ vẫn là giá trị gốc · d tính trong không gian tương ứng · Văn bản đầy đủ ở CSV.")
    selected=d.loc[[qi],["source_record","label","text","n_chars","n_digits","digit_fraction","split"]]
    write_csv(args.output_dir/"real_query_source.csv",selected)
    fig,axs=figure("Bài 2 · Nhìn tin nhắn trước khi nhìn điểm dữ liệu")
    ax=axs[0,0];ax.axis("off");row=selected.iloc[0]
    ax.text(0,.94,f"SMS #{int(row.source_record)} · nhãn thật: {row.label} · tập: {row.split}",
            transform=ax.transAxes,weight="bold",fontsize=18)
    ax.text(0,.8,textwrap.fill(row.text,width=90),transform=ax.transAxes,fontsize=17,va="top",
            bbox={"boxstyle":"round,pad=1","facecolor":"#EDF3F8","edgecolor":"#B8CDDD"})
    ax.text(0,.37,f"len(text) = {int(row.n_chars)} ký tự\n"
            f"sum(c.isdigit() for c in text) = {int(row.n_digits)} chữ số\n"
            f"digit_fraction = {int(row.n_digits)}/{int(row.n_chars)} = {row.digit_fraction:.6f}",
            transform=ax.transAxes,fontsize=21,linespacing=1.7)
    save_figure(fig,args,"real_sms_text","Đếm trên văn bản gốc, gồm khoảng trắng và dấu câu · isdigit() đếm ký tự chữ số, không đếm nhóm số.")
    cm=confusion_matrix(d.loc[te,"y"],result["test_pred"],labels=[0,1])
    return {"raw_rows":result["raw_count"],"deduplicated_rows":len(d),"split_sizes":[len(tr),len(va),len(te)],
            "scaler_mean":sc.mean_,"scaler_scale_ddof0":sc.scale_,"selected":result["best"],
            "validation_grid":result["grid"],"test_confusion":cm,"test_f1":f1_score(d.loc[te,"y"],result["test_pred"]),
            "query":selected.to_dict("records"),"query_neighbors":demo,
            "scope":"Hai đặc trưng hình thức SMS; chưa mô hình hóa ngữ nghĩa. Test dùng sau khi chọn cấu hình."}

def main(argv=None):
    p=parser(2,__doc__)
    p.add_argument("--k",type=int,default=3,help="k để tự thử trên năm điểm toy, trong [1,5]")
    p.add_argument("--weighted",action="store_true",help="Thử bỏ phiếu 1/khoảng cách trong toy")
    args=p.parse_args(argv);setup(args);out={}
    if args.mode in ("toy","all"):out["toy"]=toy(args)
    if args.mode in ("real","all"):out["real"]=real(args)
    finish(args,2,out)
if __name__=="__main__":main()
