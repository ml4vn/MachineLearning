"""Suy luận từ tham số NPZ và một ảnh NPY uint8 28×28, không cần fit lại."""
from pathlib import Path
import sys
if __package__ in (None, ""): sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import argparse
import json
import numpy as np
from mlcourse.fashion import NAMES
from examples.bai10.algorithms import forward

def predict_image(model_path,image_path):
    pixels=np.load(image_path,allow_pickle=False)
    if pixels.shape!=(28,28) or pixels.dtype!=np.uint8: raise ValueError("Ảnh phải là NPY uint8 shape (28,28).")
    with np.load(model_path,allow_pickle=False) as model:
        params=[model[k] for k in ["W1","b1","W2","b2"]]
        shapes=[(784,64),(64,),(64,10),(10,)]
        if any(a.shape!=s or not np.isfinite(a).all() for a,s in zip(params,shapes)): raise ValueError("Shape/tham số mô hình không hợp lệ.")
        _,_,p=forward(pixels.reshape(1,784).astype(float)/255,*params)
    label=int(p.argmax(1)[0])
    return dict(label=label,name=NAMES[label],probabilities=p[0].tolist())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--model",type=Path,required=True);p.add_argument("--image",type=Path,required=True);args=p.parse_args()
    print(json.dumps(predict_image(args.model,args.image),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
