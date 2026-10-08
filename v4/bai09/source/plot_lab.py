"""Scientific figures from independently audited case outputs."""
import os
os.environ["MPLBACKEND"]="Agg"
from pathlib import Path
import sys,json
ROOT=Path.cwd()
if not (ROOT/"source/pca_lab.py").exists():raise RuntimeError("Mở notebook trong thư mục bài")
if (ROOT/".build/pydeps").exists():sys.path.insert(0,str(ROOT/".build/pydeps"))
sys.path.insert(0,str(ROOT/"source"))
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from pca_lab import P,main
from threadpoolctl import threadpool_limits
from sklearn.decomposition import PCA
OUT=ROOT/"results/lab_figures";OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"figure.figsize":(10,5),"axes.grid":True})
print("PCA: tâm và hướng train; validation dùng lại tham số")

mu=P.mean(0);xc=P-mu;w=np.array([1,1])/np.sqrt(2);z=xc@w;rec=mu+z[:,None]*w;r=P-rec
assert np.allclose(r@w,0)
print(pd.DataFrame({"Điểm":list("ABCD"),"score":z,"x_hat1":rec[:,0],"x_hat2":rec[:,1],"error_point":(r*r).sum(1)}))
assert np.isclose(np.mean(r*r),.25)
print("MSE mỗi tọa độ",np.mean(r*r))

fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,points,reconstructed,origin in zip(axes,[P,xc],[rec,rec-mu],[mu,[0,0]]):
    ax.scatter(points[:,0],points[:,1],color="#245a84");ax.scatter(reconstructed[:,0],reconstructed[:,1],color="#bc761a",marker="D")
    for label,pnt,q in zip("ABCD",points,reconstructed):ax.annotate(label,pnt);ax.plot([pnt[0],q[0]],[pnt[1],q[1]],color="#bf514b")
    oo=np.array(origin);ends=oo+np.array([[-3], [3]])*w
    ax.plot(ends[:,0],ends[:,1],color="#bc761a");ax.set_aspect("equal");ax.set(xlabel="x1",ylabel="x2")
axes[0].set(xlim=(0,10),ylim=(0,10),title="Hệ gốc");axes[1].set(xlim=(-3,3),ylim=(-3,3),title="Căn giữa")
fig.tight_layout();fig.savefig(OUT/"projection.png",dpi=180);plt.close('all')

theta=np.linspace(0,np.pi,181);C=xc.T@xc/4;directions=np.column_stack([np.cos(theta),np.sin(theta)])
variance=np.einsum("bi,ij,bj->b",directions,C,directions);error=5-variance
assert np.isclose(variance.max(),4.5)
fig,ax=plt.subplots();ax.plot(np.degrees(theta),variance,label="Retained variance");ax.plot(np.degrees(theta),error,label="Mean squared point error");ax.axhline(5,color="gray",label="Total variance");ax.set(xlabel="Angle (degree)",ylabel="Population variance / squared error");ax.legend();fig.tight_layout();fig.savefig(OUT/"direction_choice.png",dpi=180);plt.close('all')
p=PCA(svd_solver="full").fit(P);assert np.allclose(p.explained_variance_,[6,2/3]);print("sklearn covariance sample:",p.explained_variance_,p.explained_variance_ratio_)

assert (ROOT/"results/case_audit.json").exists(),"Run pca_lab.py first"
audit=json.loads((ROOT/"results/case_audit.json").read_text(encoding="utf8"))
assert audit["status"]=="pass"
arrays=np.load(ROOT/"data/lab_arrays.npz");data=np.load(ROOT/"data/fashion_subset.npz")
print("Kiểm case",audit["checks_count"],"k90",audit["k90"])
print(pd.DataFrame(audit["reconstruction"]))

i=int(arrays["display_positions"][0]);image=data["validation_images"][i].reshape(28,28)
assert data["validation_indices"][i]==24814 and image[12,12]==203
print("ID train:24814; role validation; position",i)
print(pd.DataFrame(image[12:17,12:17],index=range(12,17),columns=range(12,17)))
print("Ba score đầu",arrays["validation_scores"][i,:3])
plt.imshow(image,cmap="gray",vmin=0,vmax=255);plt.title("train:24814 ·validation");plt.colorbar(label="Pixel byte");plt.grid(False);plt.savefig(OUT/"trace_image.png",dpi=180);plt.close('all')

fig,axes=plt.subplots(1,5,figsize=(15,3));axes[0].imshow(image,cmap="gray",vmin=0,vmax=255);axes[0].set_title("Original")
for j,k in enumerate([2,16,64,128]):
    reconstruct=arrays["validation_scores"][i,:k]@arrays["components"][:k]+arrays["mean"]
    assert np.allclose(reconstruct,arrays["display_recon"][j,0])
    axes[j+1].imshow(np.clip(reconstruct.reshape(28,28),0,1),cmap="gray",vmin=0,vmax=1);axes[j+1].set_title("k="+str(k))
for ax in axes:ax.axis("off")
fig.tight_layout();fig.savefig(OUT/"reconstruction.png",dpi=180);plt.close('all')
print("Số tọa độ64/784:",64/784,"không là byte compression rate")

cum=arrays["cumulative_evr"];assert cum[80]<.9<=cum[81]
fig,axes=plt.subplots(1,2,figsize=(12,4));axes[0].plot(np.arange(1,201),cum[:200]);axes[0].axhline(.9,color="#bc761a");axes[0].set(xlabel="k",ylabel="Cumulative train EVR")
axes[1].plot([x["k"] for x in audit["reconstruction"]],[x["validation_mse_pixel"] for x in audit["reconstruction"]],"o-");axes[1].set(xlabel="k",ylabel="Validation MSE per pixel (unclipped)")
fig.tight_layout();fig.savefig(OUT/"dimension_evidence.png",dpi=180);plt.close('all')
print("81/82:",cum[80:82])

scores=arrays["validation_scores"][:1000,:2];labels=data["validation_labels"][:1000]
fig,ax=plt.subplots(figsize=(7,7));ax.scatter(scores[:,0],scores[:,1],c=labels,cmap="tab10",s=10,alpha=.7);ax.set(xlim=(-15,15),ylim=(-15,15),xlabel="PC1 score",ylabel="PC2 score",title="Fixed first1000 validation images");ax.set_aspect("equal");fig.tight_layout();fig.savefig(OUT/"scores2d.png",dpi=180);plt.close('all')
y=data["validation_labels"];p=arrays["validation_pixel_predictions"]==y;q=arrays["validation_pca64_predictions"]==y
print(pd.DataFrame([[sum(p&q),sum(p&~q)],[sum(~p&q),sum(~p&~q)]],index=["Pixel correct","Pixel wrong"],columns=["PCA correct","PCA wrong"]))
assert sum(~p&q)==145 and sum(p&~q)==134
print("Net11 /3000; one split does not establish general superiority")

from science_audit import main as independent_audit
independent_audit()
print("EVR cao không bảo đảm dự đoán tốt: nhãn theo dấuPC2 của toy")
print("Gợi ý thử: giữk16/64/128 vàso cùngprotocol; không chọn bằngtest")