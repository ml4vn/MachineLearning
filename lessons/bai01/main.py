"""Chạy: python -m lessons.bai01.main --mode all"""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import io
import zipfile
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from mlcourse.common import (parser, setup, finish, figure, save_figure,
                             write_csv, require_file, COLORS)
from mlcourse.data import entries, verify
from lessons.bai01.algorithms import cosine, multi_hot, genre_set, contributions

AXES = ["Action", "Comedy", "Sci-Fi"]
CANDIDATES = [260, 1580, 480, 1214, 1]

def toy(args):
    query = np.array([1., 0., 1.])
    examples = [[1,0,1], [1,1,1], [0,0,1], [0,1,0], [0,0,0]]
    rows = []
    for i, vector in enumerate(examples, 1):
        result = contributions(query, vector)
        library = float(cosine_similarity([query], [vector])[0,0])
        if result["cosine"] is not None:
            np.testing.assert_allclose(result["cosine"], library, atol=1e-12)
        rows.append({"example": i, "vector": str(vector), **result, "sklearn": library})
    write_csv(args.output_dir/"toy_steps.csv", rows)
    fig, axs = figure("Bài 1 · Cùng hướng khác với ở gần", ncols=2)
    ax = axs[0,0]
    for label, vector, color in zip(["u=(1,0)", "v=(3,0)", "w=(1,1)"],
                                   [[1,0],[3,0],[1,1]], COLORS):
        ax.arrow(0,0,*vector, width=.018, length_includes_head=True, color=color)
        ax.text(vector[0]+.08, vector[1]+.08, label, color=color)
    ax.set(xlim=(-.2,4.2), ylim=(-.5,2.2), xlabel="Tọa độ 1", ylabel="Tọa độ 2")
    ax.set_aspect("equal"); ax.grid(alpha=.2)
    axs[0,1].bar(["u với v", "u với w"], [cosine([1,0],[3,0]),cosine([1,0],[1,1])],
                 color=COLORS[:2])
    axs[0,1].set(ylim=(0,1.15), ylabel="Cosine", title="v xa u hơn, nhưng cùng hướng với u")
    save_figure(fig,args,"toy_vectors","Ví dụ tổng hợp · Cosine đo hướng; khoảng cách Euclid đo độ xa.")
    return {"examples": rows, "zero_vector_math": None, "zero_vector_sklearn_policy": 0,
            "positive_scale_invariant": cosine([1,2],[2,1]) == cosine([3,6],[2,1])}

def load_movies(data_dir):
    raw = require_file(data_dir,"movielens.zip")
    verify(raw,entries("movielens")[0]["sha256"])
    with zipfile.ZipFile(raw) as z:
        names = [n for n in z.namelist() if n.split("/")[-1]=="movies.csv"]
        if len(names)!=1: raise ValueError("ZIP phải có đúng một movies.csv")
        movies = pd.read_csv(io.BytesIO(z.read(names[0])))
    if movies["movieId"].duplicated().any() or movies[["movieId","genres"]].isna().any().any():
        raise ValueError("movieId trùng hoặc trường bắt buộc bị thiếu")
    return movies.set_index("movieId",drop=False)

def real(args):
    movies=load_movies(args.data_dir)
    labels={int(mid):genre_set(row["genres"]) for mid,row in movies.iterrows()}
    axes=sorted(set().union(*labels.values()))
    query_id=args.query_id
    if query_id not in labels: raise ValueError(f"Không có movieId={query_id}")
    q3=multi_hot(labels[query_id],AXES); qfull=multi_hot(labels[query_id],axes)
    if not qfull.any(): raise ValueError("Phim tham chiếu thiếu nhãn; cosine không xác định")
    comparison=[]
    for mid in CANDIDATES:
        v3=multi_hot(labels[mid],AXES); vf=multi_hot(labels[mid],axes)
        c3=cosine(q3,v3); cf=cosine(qfull,vf)
        independent=len(labels[query_id]&labels[mid])/np.sqrt(len(labels[query_id])*len(labels[mid]))
        np.testing.assert_allclose(cf,independent,atol=1e-12)
        comparison.append({"movieId":mid,"title":movies.loc[mid,"title"],
                           "genres":movies.loc[mid,"genres"],"vector3":v3.astype(int).tolist(),
                           "dot3":float(q3@v3),"cosine3":c3,"cosine_full":cf})
    candidates=movies.loc[[mid for mid in movies.index if mid!=query_id and labels[mid]]].copy()
    matrix=np.vstack([multi_hot(labels[mid],axes) for mid in candidates.index])
    scores=cosine_similarity([qfull],matrix)[0]
    independent=np.array([len(labels[query_id]&labels[mid])/np.sqrt(len(labels[query_id])*len(labels[mid]))
                          for mid in candidates.index])
    np.testing.assert_allclose(scores,independent,atol=1e-12)
    candidates["cosine"]=np.clip(scores,0,1)
    # Làm tròn khóa xếp hạng ở dung sai số học; ID chỉ định thứ tự hiển thị.
    candidates["score_key"]=candidates["cosine"].round(12)
    ranked=candidates.reset_index(drop=True).sort_values(["score_key","movieId"],ascending=[False,True])
    ranked=ranked.drop(columns="score_key")
    write_csv(args.output_dir/"real_movie_comparison.csv",comparison)
    write_csv(args.output_dir/"real_ranked_movies.csv",ranked)
    preview=movies.loc[[query_id]+[x for x in CANDIDATES if x!=query_id]]
    write_csv(args.output_dir/"real_source_rows.csv",preview)
    fig,axs=figure("Bài 1 · Cùng phim, thay bộ trục thì điểm giống thay đổi",ncols=2)
    x=np.arange(len(comparison))
    short=[str(row["movieId"]) for row in comparison]
    axs[0,0].bar(x-.18,[np.nan if r["cosine3"] is None else r["cosine3"] for r in comparison],.36,label="3 trục")
    axs[0,0].bar(x+.18,[r["cosine_full"] for r in comparison],.36,label=f"{len(axes)} nhãn")
    axs[0,0].set(xticks=x,xticklabels=short,ylim=(0,1.12),xlabel="movieId (đối chiếu tên trong CSV)",ylabel="Cosine")
    axs[0,0].legend()
    heat=np.vstack([multi_hot(labels[mid],AXES) for mid in preview.index])
    axs[0,1].imshow(heat,vmin=0,vmax=1,cmap="Blues",aspect="auto")
    axs[0,1].set(xticks=range(3),xticklabels=AXES,yticks=range(len(preview)),
                 yticklabels=[str(x) for x in preview.index],title="Truy từ nhãn thật sang bảng multi-hot")
    for i in range(len(heat)):
        for j in range(3):axs[0,1].text(j,i,str(int(heat[i,j])),ha="center",va="center",color="white" if heat[i,j] else "black")
    save_figure(fig,args,"real_metadata","Nguồn: MovieLens latest-small (2018) · Ví dụ được chọn để giảng, không phải mẫu ngẫu nhiên.")
    ties=sum(labels[mid]==labels[query_id] for mid in candidates.index)
    return {"movies":len(movies),"axes":axes,"missing_metadata":sum(not s for s in labels.values()),
            "query_id":query_id,"candidate_pool":len(candidates),"same_label_ties":ties,
            "comparison":comparison,"top10":ranked.head(10).to_dict("records"),
            "scope":"Độ tương đồng metadata; chưa đánh giá gợi ý cá nhân hoặc xác suất yêu thích."}

def main(argv=None):
    p=parser(1,__doc__);p.add_argument("--query-id",type=int,default=2571,help="movieId tham chiếu")
    args=p.parse_args(argv);setup(args);results={}
    if args.mode in ("toy","all"):results["toy"]=toy(args)
    if args.mode in ("real","all"):results["real"]=real(args)
    finish(args,1,results)

if __name__=="__main__":main()
