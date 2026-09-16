"""Đối chiếu đầu ra đã chạy với các phép tính tay của slide/tài liệu v3."""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'outputs/v3');p.add_argument('--report',type=Path);a=p.parse_args()
    checks=[]
    def check(name,ok): checks.append({'name':name,'passed':bool(ok)})
    def rows(n,file):
        with (a.output_dir/f'bai{n:02d}'/file).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    def close(x,y):return math.isclose(float(x),y,abs_tol=1e-9)
    threshold=next(r for r in rows(3,'toy_thresholds.csv') if close(r['threshold'],.8))
    check('B03 tau .80: TN5 FP1 FN2 TP2',[int(threshold[k]) for k in ['tn','fp','fn','tp']]==[5,1,2,2])
    check('B03 score of C stays .85',close(next(r for r in rows(3,'toy_rows.csv') if r['id']=='C')['score'],.85))
    hist=rows(4,'toy_wb_history.csv')
    check('B04 first gradient (-8,-2.75)',close(hist[0]['gradient_w'],-8) and close(hist[0]['gradient_b'],-2.75))
    check('B04 simultaneous first step (.9,1.1375)',close(hist[1]['w'],.9) and close(hist[1]['b'],1.1375))
    check('B04 J after first step 1.481328125',close(hist[1]['J'],1.481328125))
    check('B04 GD decreases J at chosen eta',all(float(b['J'])<=float(c['J'])+1e-12 for c,b in zip(hist,hist[1:])))
    errors=rows(4,'test_predictions.csv')
    check('B04 sign and predictions agree',all(close(r['error_prediction_minus_actual'],float(r['distance'])-float(r['delivery_days'])) and close(r['error_prediction_minus_actual'],-float(r['residual_actual_minus_prediction'])) for r in errors))
    g=rows(6,'toy_gini_trace.csv')
    check('B06 counts and Gini',[(int(r['n']),int(r['positive'])) for r in g]==[(12,6),(4,4),(8,2)] and all(close(r['gini'],v) for r,v in zip(g,[.5,0,.375])))
    check('B06 weighted children .25',close(sum(float(r['n'])/12*float(r['gini']) for r in g[1:]),.25))
    r=json.loads((a.output_dir/'bai08/results.json').read_text(encoding='utf-8'))['results']['toy']
    check('B08 silhouette of point 2 is 7/9',close(r['silhouette'][1],7/9))
    tiny=rows(10,'toy_backprop.csv')[0]
    check('B10 old parameter and slide name',tiny['parameter']=='W11' and tiny['slide_parameter']=='w11')
    expected=(1/(1+math.exp(-.204))-1)*.7*.6
    check('B10 chain rule w11 and update',close(tiny['analytic'],expected) and close(tiny['after_GD_eta_0_1'],.5-.1*expected))
    for n in range(1,11):
        config=json.loads((ROOT/f'lessons/bai{n:02d}/teaching.json').read_text(encoding='utf-8'))
        check(f'B{n:02d} documented outputs exist',all((a.output_dir/f'bai{n:02d}'/f).is_file() for f in config['outputs']))
    result={'passed':all(c['passed'] for c in checks),'checks':checks,'check_count':len(checks)}
    if a.report:a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':main()
