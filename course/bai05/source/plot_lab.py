"""Complete lab demonstrations. Run from lesson root."""
import os
os.environ["MPLBACKEND"]="Agg"
from pathlib import Path
import sys
ROOT=Path.cwd()
if not (ROOT/"source/logistic_lab.py").exists(): raise RuntimeError("Mở notebook ở thư mục Bài 5 đã giải nén")
if (ROOT/".build/pydeps").exists():sys.path.insert(0,str(ROOT/".build/pydeps"))
sys.path.insert(0,str(ROOT/"source"))
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from scipy.special import expit
from logistic_lab import gradient_descent,gradient,loss,run
from prepare_olist import prepare
plt.rcParams.update({"figure.figsize":(10,5),"axes.grid":True})
OUT=ROOT/"results/lab_figures";OUT.mkdir(parents=True,exist_ok=True)

x=np.array([-1.,0.,1.,2.]);y=np.array([0.,0.,1.,1.]);h=gradient_descent(x,y,steps=20)
print(pd.DataFrame([{k:r[k] for k in ["step","w","b","loss"]} for r in h[:3]]).to_string(index=False))
print("Gradient cũ",h[0]["gradient"],h[1]["gradient"])
assert np.allclose([h[2]["w"],h[2]["b"]],[.8232410450840703,-.057764644657501224])

xx=np.linspace(-2,3,200);fig,ax=plt.subplots();ax.scatter(x,y,label="Labels (designed)",color="#bc761a")
for r in h[:3]:ax.plot(xx,expit(r["b"]+r["w"]*xx),label=f"t={r[chr(115)+chr(116)+chr(101)+chr(112)]}")
ax.set(xlabel="toy x",ylabel="p",ylim=(-.05,1.05));ax.legend();fig.tight_layout();fig.savefig(OUT/"toy_probabilities.png",dpi=240);plt.close('all')

for th in [(0.,0.),(.5,0.),(.7,-.2)]:
    th=np.array(th)
    for lam in [0.,.1]:
        fd=np.array([(loss(th+np.eye(2)[j]*1e-5,x,y,lam)-loss(th-np.eye(2)[j]*1e-5,x,y,lam))/2e-5 for j in range(2)])
        assert np.allclose(fd,gradient(th,x,y,lam),atol=1e-9)
        print(th,lam,fd)

fig,ax=plt.subplots()
for eta in [.1,1.,10.,100.]:
    hs=gradient_descent(x,y,eta=eta,steps=15);ax.plot([r["step"] for r in hs],[r["loss"] for r in hs],marker="o",label=f"eta={eta}")
ax.set(xlabel="step",ylabel="BCE");ax.legend();fig.tight_layout();fig.savefig(OUT/"learning_rates.png",dpi=240);plt.close('all')
fig,ax=plt.subplots();u1=np.linspace(-3,3,200)
for tau in [.5,.2]:ax.plot(u1,(.5+np.log(tau/(1-tau))-u1)/.8,label=f"p=tau={tau}")
ax.set(xlabel="toy u1",ylabel="toy u2",xlim=(-3,3),ylim=(-4,4),title="Same logit: z=-0.5+u1+0.8*u2");ax.legend();fig.tight_layout();fig.savefig(OUT/"boundaries.png",dpi=240);plt.close('all')

provenance=prepare();audit=run()
assert audit["status"]=="pass"
print("Checks",audit["checks_count"],"weight fixes",provenance["weight_correction_count"])
print("Split",audit["split_counts"])
print("One ID",audit["one_order"])

scan=pd.DataFrame(audit["validation_scan"])
print(scan[["policy","threshold","cost","alerts","fn"]].to_string(index=False))
print("Selected",audit["policy"]["selected"])
fig,ax=plt.subplots();ax.plot(scan.threshold,scan.cost,marker="o",label="FP+5FN");ax.axhline(scan.loc[scan.policy=="no_alerts","cost"].iloc[0],color="gray",ls="--",label="No alerts");ax.set(xlabel="threshold (validation)",ylabel="hypothetical K");ax.legend();fig.tight_layout();fig.savefig(OUT/"validation_policy.png",dpi=240);plt.close('all')

pred=pd.read_csv(ROOT/"data/prepared/test_predictions.csv");print(audit["test_selected"])
fig,ax=plt.subplots();bins=np.linspace(0,.5,26)
for label,color in [(0,"#245a84"),(1,"#bc761a")]:
    s=pred.loc[pred.late==label,"score"].to_numpy();ax.hist(s,bins=bins,weights=np.ones(len(s))/len(s),histtype="step",linewidth=2,label=f"y={label}; n={len(s)}",color=color)
ax.axvline(.1,color="#167a72",ls="--",label="tau=.1");ax.set(xlabel="test p",ylabel="probability mass within each class");ax.legend();fig.tight_layout();fig.savefig(OUT/"test_score_histogram.png",dpi=240);plt.close('all')

r=pd.DataFrame(audit["reliability"]);print(r.to_string(index=False))
fig,ax=plt.subplots();ax.plot([0,.35],[0,.35],color="gray",ls="--",label="identity");ax.plot(r.mean_p,r.late_rate,marker="o",label="historical bins");ax.set(xlabel="mean predicted p",ylabel="observed late fraction");ax.legend();fig.tight_layout();fig.savefig(OUT/"reliability.png",dpi=240);plt.close('all')
print("Logistic",audit["test_selected"]["log_loss"],audit["test_selected"]["brier"])
print("Baseline",audit["baseline"]["log_loss"],audit["baseline"]["brier"])

from science_audit import run as independent_audit
report=independent_audit();assert report["status"]=="pass"
print("Independent checks",report["checks_count"])
p=expit(np.log(3));print("Exit",p,p/(1-p),-np.log(p),int(p>=.8),p-1)
assert np.isclose(p,.75)
print("Conclusion: ranking improves on this historical cohort; recall at tau=.1 remains low. Costs are hypothetical; a new time period is needed for deployment evidence.")