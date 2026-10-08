"""Scientific lab plots. Run from lesson root."""
import os
os.environ["MPLBACKEND"]="Agg"
from pathlib import Path
import sys
ROOT=Path.cwd()
if not (ROOT/"source/tree_lab.py").exists():raise RuntimeError("Mở notebook tại thư mục bài đã giải nén")
if (ROOT/".build/pydeps").exists():sys.path.insert(0,str(ROOT/".build/pydeps"))
sys.path.insert(0,str(ROOT/"source"))
import json,numpy as np,pandas as pd,matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier,plot_tree
from tree_lab import toy_data,gini,enumerate_splits,walk,run
from prepare_olist import prepare
from threadpoolctl import threadpool_limits
OUT=ROOT/"results/lab_figures";OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"figure.figsize":(10,5),"axes.grid":True})

X,y=toy_data();print(pd.DataFrame({"ID":[f"M{i:02}" for i in range(1,13)],"x_100km":X[:,0],"h_days":X[:,1],"y":y}).to_string(index=False))
print("Gini gốc",gini(y));candidates=enumerate_splits(X,y);print(pd.DataFrame(candidates).to_string(index=False))
fig,ax=plt.subplots();ax.scatter(X[:,0],X[:,1],c=np.where(y,"#bc761a","#245a84"));ax.axhline(15,color="#167a72");ax.set(xlabel="x (100 km), synthetic",ylabel="promised days");fig.tight_layout();fig.savefig(OUT/"toy_root.png",dpi=240);plt.close('all')

best=max(candidates,key=lambda c:c["gain"]);right=X[:,1]>15;print("Best root",best);print("Right subset",enumerate_splits(X[right],y[right]))
toy=DecisionTreeClassifier(random_state=42).fit(X,y);fig,ax=plt.subplots(figsize=(12,6));plot_tree(toy,feature_names=["x_100km","h_days"],class_names=["on time","late"],filled=True,ax=ax);fig.tight_layout();fig.savefig(OUT/"toy_tree.png",dpi=240);plt.close('all')
assert toy.get_n_leaves()==3 and toy.get_depth()==2

path=toy.cost_complexity_pruning_path(X,y);print("alpha",path.ccp_alphas,"R",path.impurities)
for alpha in [.1,.25,.3]:print(alpha,[3*alpha,.25+2*alpha,.5+alpha])
fig,ax=plt.subplots();alphas=np.linspace(0,.4,100)
for L,r in [(3,0),(2,.25),(1,.5)]:ax.plot(alphas,r+alphas*L,label=f"{L} leaves")
ax.set(xlabel="alpha",ylabel="R + alpha*L");ax.legend();fig.tight_layout();fig.savefig(OUT/"pruning_objective.png",dpi=240);plt.close('all')

provenance=prepare()
with threadpool_limits(limits=1):audit=run()
print("Data",provenance["split_counts"],"unknown weights",provenance["weight_correction_count"])
print("Policy",audit["policy"]);print("Candidates",[(c["depth"],c["validation"]["ap"]) for c in audit["candidates"]])
assert audit["status"]=="pass"

scan=pd.DataFrame(audit["validation_scan"]);print(scan[["threshold","fp","fn","alerts","cost"]].to_string(index=False))
fig,ax=plt.subplots();points=scan[scan.threshold.notna()];ax.plot(points.threshold,points.cost,marker="o");ax.axhline(scan.loc[scan.threshold.isna(),"cost"].iloc[0],ls="--",color="gray",label="no alerts");ax.set(xlabel="tau (validation)",ylabel="hypothetical K=FP+5FN");ax.legend();fig.tight_layout();fig.savefig(OUT/"validation_policy.png",dpi=240);plt.close('all')

o=audit["one_order"];nodes=json.loads((ROOT/"results/chosen_tree.json").read_text());print("ID",o["order_id"]);print(pd.DataFrame(o["path"]).to_string(index=False));print("Leaf",o["leaf_counts"]);print("Policy",audit["policy"]["selected_threshold"],"truth",o["late"])
leaf,p,path=walk(nodes,o["filled"]);assert leaf==o["leaf"] and np.isclose(p,o["p"])
print("Test",audit["test_selected"],"Logistic",audit["logistic"]["test_selected"])

print("Paired error counts",audit["paired_counts"]);print("Deterministic examples",audit["paired_examples"])
fig,ax=plt.subplots();labels=["FN fixed","FN new","FP fixed","FP new"];keys=["fn_fixed","fn_new","fp_fixed","fp_new"];ax.bar(labels,[audit["paired_counts"][k] for k in keys],color=["#167a72","#bc761a","#167a72","#bc761a"]);ax.set(ylabel="orders, full historical test");fig.tight_layout();fig.savefig(OUT/"paired_errors.png",dpi=240);plt.close('all')

fig,axs=plt.subplots(1,2,figsize=(13,5));features=audit["features"];axs[0].barh(features,audit["mdi"]);axs[0].set(xlabel="MDI (train)");axs[1].barh(features,audit["permutation_mean"],xerr=audit["permutation_std"]);axs[1].set(xlabel="AP drop (validation), mean +/- std of 5 permutations");fig.tight_layout();fig.savefig(OUT/"importance.png",dpi=240);plt.close('all')
print("Feature importance and decision rules do not establish causality.")

from science_audit import run as independent_audit
report=independent_audit();assert report["status"]=="pass"
print("Independent checks",report["checks_count"])
print("Exit: G_right=3/8; gain at node=3/8; global contribution=(8/12)*(3/8)=1/4.")
print("Conclusion: tree trades higher recall for more false alerts on this historical cohort. Choose configuration on validation; keep test history disclosed.")