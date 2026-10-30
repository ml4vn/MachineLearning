"""Run all notebook demonstrations as a complete script. Run from lesson root."""
import os
os.environ["MPLBACKEND"]="Agg"
from pathlib import Path
import sys
ROOT=Path.cwd()
if not (ROOT/"source/gd_lab.py").exists():
    raise RuntimeError("Mở notebook tại thư mục Bài 4 đã giải nén")
if (ROOT/".build/pydeps").exists(): sys.path.insert(0,str(ROOT/".build/pydeps"))
sys.path.insert(0,str(ROOT/"source"))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from gd_lab import toy_one_parameter, batch_gd, metrics, run
plt.rcParams.update({"figure.figsize":(9,5),"axes.grid":True})
OUT=ROOT/"results/lab_figures"; OUT.mkdir(parents=True,exist_ok=True)

h=toy_one_parameter(.4,8)
print(pd.DataFrame([{k:r[k] for k in ["t","w","g","J"]} for r in h[:3]]).to_string(index=False))
assert np.isclose(h[1]["w"],.7) and np.isclose(h[2]["J"],.1015625)

x=np.arange(1.,5.); y=np.array([3.,4.,6.,7.]); z=x-2.5
fig,ax=plt.subplots();ax.scatter(x,y,label="Mo phong");
for r in h[:3]: ax.plot(x,r["predictions"],label=f"t={r[chr(116)]}; w={r[chr(119)]:.2f}")
ax.set(xlabel="x / 100 km",ylabel="y, prediction / day");ax.legend();fig.tight_layout();fig.savefig(OUT/"toy_predictions.png",dpi=240);plt.close('all')

J=lambda w: np.mean((5+w*z-y)**2)/2
g=lambda w: np.mean(z*(5+w*z-y))
for w in [0,.7,1.4,2.1]:
    fd=(J(w+1e-5)-J(w-1e-5))/2e-5
    assert np.isclose(fd,g(w),atol=1e-8)
    print(w,g(w),fd)

fig,axes=plt.subplots(2,1,figsize=(10,8));
for eta in [.1,.4,1.2,1.8]:
    hs=toy_one_parameter(eta,8); t=[r["t"] for r in hs]
    axes[0].plot(t,[r["w"] for r in hs],marker="o",label=f"eta={eta}")
    axes[1].semilogy(t,[r["J"] for r in hs],marker="o",label=f"eta={eta}")
axes[0].axhline(1.4,color="gray",ls="--");axes[0].set_ylabel("w / day per 100 km");axes[1].set(xlabel="step t",ylabel="J / day squared");axes[0].legend();fig.tight_layout();fig.savefig(OUT/"learning_rates.png",dpi=240);plt.close('all')

w,b,h2=batch_gd(x,y,eta=.05,steps=1,w0=.5,b0=1)
print(pd.DataFrame(h2).to_string(index=False))
assert np.allclose([w,b],[.9,1.1375])
H=np.array([[7.5,2.5],[2.5,1.]])
print("Hessian eigenvalues",np.linalg.eigvalsh(H))

audit=run(rebuild=False)
print(audit["status"],len(audit["checks"]))
print(pd.DataFrame(audit["real"]["four_orders"]).to_string(index=False))

train=pd.read_csv(ROOT/"data/prepared/olist_model_table.csv");train=train.loc[train["split"]=="train"].copy()
fig,ax=plt.subplots(); valid=train.dropna(subset=["distance_km","delivery_days"])
ax.hexbin(valid.distance_km,valid.delivery_days,gridsize=(30,18),extent=(0,3000,0,45),mincnt=1,bins="log",cmap="Blues")
r=audit["real"];xx=np.linspace(0,3000,200);ax.plot(xx,r["b_raw"]+r["w_raw"]*xx,color="#bc761a",label="GD 100")
ax.set(xlim=(0,3000),ylim=(0,45),xlabel="distance / km",ylabel="delivery from approval / day");ax.legend();fig.tight_layout();fig.savefig(OUT/"olist_density.png",dpi=240);plt.close('all')

history=pd.DataFrame(audit["real"]["history"])
fig,ax=plt.subplots();ax.plot(history.t,history.J,label="Batch GD eta=.1");ax.set(xlabel="step t",ylabel="train J / day squared");ax.legend();fig.tight_layout();fig.savefig(OUT/"olist_GD_loss.png",dpi=240);plt.close('all')
print(audit["real"]["metrics"])

pred=pd.read_csv(ROOT/"data/test_predictions.csv")
print(pred.columns.tolist())
e=pred["prediction_GD"]-pred["delivery_days"]
fig,ax=plt.subplots();ax.hist(np.clip(e,-40,40),bins=np.linspace(-40,40,21),color="#245a84");ax.set(xlabel="GD residual / day (outside +/-40 merged at edges)",ylabel="test orders");fig.tight_layout();fig.savefig(OUT/"test_residuals.png",dpi=240);plt.close('all')
print("MAE",np.abs(e).mean(),"RMSE",np.sqrt(np.mean(e**2)))
assert len(e)==40266
assert np.isclose(np.abs(e).mean(),5.9396250620880835)