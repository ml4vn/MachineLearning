"""Chuẩn bị SMS dùng chung cho Bài 2–3; mỗi bài tự fit từ train."""
from __future__ import annotations
import csv
import hashlib
import io
import zipfile
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits
from mlcourse.common import require_file
from mlcourse.data import verify, entries

FEATURES = ["n_chars", "digit_fraction"]

def text_features(text):
    if not isinstance(text,str) or len(text)==0:
        raise ValueError("Cần một chuỗi khác rỗng")
    digits=sum(c.isdigit() for c in text)
    return {"n_chars":len(text),"n_digits":digits,"digit_fraction":digits/len(text)}

def load_sms(data_dir, seed=42):
    raw=require_file(data_dir,"sms.zip");verify(raw,entries("sms")[0]["sha256"])
    with zipfile.ZipFile(raw) as z:
        d=pd.read_csv(io.BytesIO(z.read("SMSSpamCollection")),sep="\t",
                      names=["label","text"],quoting=csv.QUOTE_NONE)
    raw_count=len(d)
    if d[["label","text"]].isna().any().any() or not d.label.isin(["ham","spam"]).all():
        raise ValueError("Thiếu văn bản/nhãn hoặc có nhãn ngoài ham/spam")
    d["source_record"]=np.arange(1,len(d)+1)
    d["normal"]=d.text.str.replace(r"\s+"," ",regex=True).str.strip().str.casefold()
    if d.groupby("normal").label.nunique().max()!=1:
        raise ValueError("Cùng văn bản chuẩn hóa nhưng nhãn mâu thuẫn")
    d=d.drop_duplicates("normal",keep="first").reset_index(drop=True)
    d["message_id"]=d.normal.map(lambda s:hashlib.sha256(s.encode("utf-8")).hexdigest())
    d["y"]=(d.label=="spam").astype(int)
    # Đặc trưng được đếm trên text gốc, không trên chuỗi normal dùng loại trùng.
    feats=pd.DataFrame([text_features(s) for s in d.text])
    d=pd.concat([d,feats],axis=1)
    train,other=train_test_split(d.index,test_size=.4,stratify=d.y,random_state=seed)
    validation,test=train_test_split(other,test_size=.5,stratify=d.loc[other,"y"],random_state=seed)
    d["split"]="train";d.loc[validation,"split"]="validation";d.loc[test,"split"]="test"
    return d, np.asarray(train),np.asarray(validation),np.asarray(test),raw_count

def fit_sms(data_dir, seed=42):
    d,tr,va,te,raw_count=load_sms(data_dir,seed)
    X=d.loc[tr,FEATURES].to_numpy();y=d.loc[tr,"y"].to_numpy()
    scaler=StandardScaler().fit(X)
    models={};rows=[]
    with threadpool_limits(limits=2):
        for scaled in [False,True]:
            for k in [3,5,11]:
                model=KNeighborsClassifier(n_neighbors=k).fit(scaler.transform(X) if scaled else X,y)
                xv=d.loc[va,FEATURES].to_numpy()
                pred=model.predict(scaler.transform(xv) if scaled else xv)
                rows.append({"scaled":scaled,"k":k,"validation_f1":float(f1_score(d.loc[va,"y"],pred)),
                             "errors":int((pred!=d.loc[va,"y"]).sum())})
                models[(scaled,k)]=model
    # Tiêu chí phụ cố định trước khi xem test: ưu tiên k nhỏ, rồi không scale.
    best=sorted(rows,key=lambda r:(-r["validation_f1"],r["k"],r["scaled"]))[0]
    model=models[(best["scaled"],best["k"])]
    def transform(ids):
        x=d.loc[ids,FEATURES].to_numpy()
        return scaler.transform(x) if best["scaled"] else x
    with threadpool_limits(limits=2):
        val_score=model.predict_proba(transform(va))[:,list(model.classes_).index(1)]
        test_score=model.predict_proba(transform(te))[:,list(model.classes_).index(1)]
        test_pred=model.predict(transform(te))
    return {"data":d,"train":tr,"validation":va,"test":te,"raw_count":raw_count,
            "scaler":scaler,"models":models,"grid":rows,"best":best,
            "val_score":val_score,"test_score":test_score,"test_pred":test_pred}
