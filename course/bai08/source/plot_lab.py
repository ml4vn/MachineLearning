"""Scientific lab figures from audited outputs. Run from lesson root."""
import os
os.environ["MPLBACKEND"]="Agg"
from pathlib import Path
import sys,os,json
ROOT=Path.cwd()
if not (ROOT/"source/kmeans_lab.py").exists():raise RuntimeError("Mở notebook trong thư mục bài đã giải nén")
if (ROOT/".build/pydeps").exists():sys.path.insert(0,str(ROOT/".build/pydeps"))
sys.path.insert(0,str(ROOT/"source"))
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from kmeans_lab import P,NAMES,lloyd,run
from sklearn.metrics import silhouette_samples
from threadpoolctl import threadpool_limits
OUT=ROOT/"results/lab_figures";OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"figure.figsize":(10,5),"axes.grid":True})
print("Cửa sổ lịch sử, tiền GBP, snapshot 10/12/2011")

audit=json.loads((ROOT/"results/case_audit.json").read_text(encoding="utf8"))
history=lloyd(P,P[[0,2]])
assert np.allclose([z["J"] for z in history],[39,12,93/8,22/3,22/3,22/3])
print(pd.DataFrame({"Điểm":NAMES,"d1^2":np.array(history[0]["d2"])[:,0],"d2^2":np.array(history[0]["d2"])[:,1],"Nhóm":np.array(history[0]["labels"])+1}))
for i,z in enumerate(history):print(i+1,z["phase"],"centers=",z["centers"],"J=",z["J"])

fig,axes=plt.subplots(1,4,figsize=(16,4),sharex=True,sharey=True)
for ax,z in zip(axes,history[:4]):
    lab=np.array(z["labels"]);cent=np.array(z["centers"])
    ax.scatter(P[:,0],P[:,1],c=np.array(["#245a84","#bc761a"])[lab],s=45)
    ax.scatter(cent[:,0],cent[:,1],c=["#245a84","#bc761a"],marker="D",s=100,facecolors="none")
    for name,pnt in zip(NAMES,P):ax.annotate(name,pnt,xytext=(3,6),textcoords="offset points")
    ax.set(xlim=(0,8),ylim=(0,6),xlabel="x1",title=z["phase"]+"; J="+str(round(z["J"],3)));ax.set_aspect("equal")
fig.tight_layout();fig.savefig(OUT/"lloyd_states.png",dpi=180);plt.close('all')

lines=pd.read_csv(ROOT/"data/example_customer_lines.csv")
rfm=pd.read_csv(ROOT/"data/retail_rfm.csv")
arrays=np.load(ROOT/"data/lab_arrays.npz")
print(lines[["InvoiceNo","InvoiceDate","StockCode","Quantity","UnitPrice","line_value"]].to_string(index=False))
assert lines.InvoiceNo.nunique()==2
assert np.isclose(lines.line_value.sum(),3811.95)
print("RFM và gán:",audit["example"])

fig,axes=plt.subplots(1,2,figsize=(12,4))
axes[0].hist(arrays["X0"][:,2],bins=30,color="#245a84");axes[0].set(xlabel="M (GBP)",ylabel="Số khách",title="Gốc")
axes[1].hist(arrays["log"][:,2],bins=30,color="#167a72");axes[1].set(xlabel="ln(1+M)",ylabel="Số khách",title="Cùng khách sau log")
fig.tight_layout();fig.savefig(OUT/"money_before_after.png",dpi=180);plt.close('all')
print(pd.DataFrame({"r":audit["example"]["raw"],"u":audit["example"]["log"],"x":audit["example"]["scaled"]},index=["R","F","M"]))

ss=silhouette_samples(np.array([[0.],[2.],[10.],[12.]]),[0,0,1,1])
assert np.isclose(ss[1],7/9)
print("Silhouette:",ss,"tại điểm 2:",ss[1])
print("a=2,b=1:",(1-2)/max(2,1))
print("Mẫu và toàn cohort K2/K4:",[(z["k"],z["silhouette"],z["silhouette_full"]) for z in audit["experiments"] if z["k"] in [2,4]])

fig,axes=plt.subplots(1,2,figsize=(12,4))
ks=[z["k"] for z in audit["experiments"]]
axes[0].plot(ks,[z["inertia"] for z in audit["experiments"]],"o-",color="#245a84");axes[0].set(xlabel="K",ylabel="J toàn cohort")
axes[1].plot(ks,[z["silhouette"] for z in audit["experiments"]],"o-",color="#167a72");axes[1].set(xlabel="K",ylabel="S trong mẫu 2000 seed42")
fig.tight_layout();fig.savefig(OUT/"K_evidence.png",dpi=180);plt.close('all')
print(pd.DataFrame(audit["profile"]))
print("Tâm đổi về gốc:",np.array(audit["inverse_centers_k4"]))

print(pd.DataFrame(audit["stability"]))
print("Ngân sách:",audit["stability_budget"])
print("ARI bỏ trùng:",audit["dedup"]["ARI"])
print(pd.DataFrame(audit["dedup"]["aligned_transition"],index=["Giữ:N0","Giữ:N1","Giữ:N2","Giữ:N3"],columns=["Bỏ:N0","Bỏ:N1","Bỏ:N2","Bỏ:N3"]))
assert np.array(audit["dedup"]["aligned_transition"]).sum()==4338
print(pd.DataFrame(audit["dedup"]["aligned_profiles"]))

import runpy
runpy.run_path(str(ROOT/"source/science_audit.py"),run_name="__main__")
assert json.loads((ROOT/"results/science_audit.json").read_text(encoding="utf8"))["status"]=="pass"
print("Gợi ý: K2 có S cao hơn; K4 có nhiều hồ sơ hơn. Chưa có dữ liệu hiệu quả hành động.")
print("Tự học: thay từng K/seed/recipe, giữ và báo cáo điều kiện so sánh.")