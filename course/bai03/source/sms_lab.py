"""Reproduce the frozen SMS experiment. Paths are relative to this self-contained package."""
from pathlib import Path
import os,sys,json,zipfile,io,hashlib
R=Path(__file__).resolve().parents[1]
extra=R/'.build/pydeps'
if extra.exists():sys.path.insert(0,str(extra))
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,f1_score
from threadpoolctl import threadpool_limits
FEATURES=['n_chars','digit_fraction']
def load_data():
 with zipfile.ZipFile(R/'data/sms.zip') as z:
  d=pd.read_csv(io.BytesIO(z.read('SMSSpamCollection')),sep='\t',names=['label','text'],quoting=3)
 d['source_record']=np.arange(1,len(d)+1)
 d['normal']=d.text.str.replace(r'\s+',' ',regex=True).str.strip().str.casefold()
 assert d.groupby('normal').label.nunique().max()==1
 d=d.drop_duplicates('normal').reset_index(drop=True)
 d['message_id']=d.normal.map(lambda t:hashlib.sha256(t.encode()).hexdigest())
 d['y']=(d.label=='spam').astype(int);d['n_chars']=d.text.str.len();d['n_digits']=d.text.map(lambda t:sum(c.isdigit() for c in t));d['digit_fraction']=d.n_digits/d.n_chars
 tr,o=train_test_split(d.index,test_size=.4,stratify=d.y,random_state=42)
 va,te=train_test_split(o,test_size=.5,stratify=d.loc[o,'y'],random_state=42)
 d['split']='train';d.loc[va,'split']='validation';d.loc[te,'split']='test'
 return d,tr,va,te

if __name__ == "__main__":
    from metrics_lab import run
    print(json.dumps(run(), ensure_ascii=False, indent=2))
