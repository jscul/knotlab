"""Summarize stage samples with each independent draw as an uncertainty cluster."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KEY = "BOND-READING-WEIGHTINGS-20261119-001"
FAMILY = ROOT / "artifacts" / KEY / (KEY + "-E001_weightings")
sys.path.insert(0,str(ROOT / "research" / KEY))
from structural_features import degree_two_free_start


def describe(rows):
    if not rows:
        return {"N": 0}
    return {"N": len(rows), "exact": sum(r["lo"] == r["hi"] for r in rows),
            "orders": dict(sorted(Counter(str(r["lo"]) if r["lo"] == r["hi"] else
                                         f'{r["lo"]}..{r["hi"]}' for r in rows).items())),
            "junctions_min_median_max": [int(np.min([x["J"] for x in rows])),
                  float(np.median([x["J"] for x in rows])), int(np.max([x["J"] for x in rows]))],
            "distinctions_min_median_max": [int(np.min([x["n"] for x in rows])),
                  float(np.median([x["n"] for x in rows])), int(np.max([x["n"] for x in rows]))],
            "order_quartiles_lower": np.quantile([r["lo"] for r in rows], [0.25, 0.5, 0.75], method="inverted_cdf").tolist(),
            "order_quartiles_upper": np.quantile([r["hi"] for r in rows], [0.25, 0.5, 0.75], method="inverted_cdf").tolist(),
            "range": [min(r["lo"] for r in rows), max(r["hi"] for r in rows)],
            "residual_exception": sum(r["residual_except"] for r in rows),
            "short_exception": sum(r["short_except"] for r in rows),
            "more_than_two_proved": sum(r["lo"] > 2 for r in rows),
            "more_than_two_possible": sum(r["hi"] > 2 for r in rows)}


def grouped(rows, field, limits):
    bins = {}
    for low, high in limits:
        bins[f"{low}..{high}"] = describe([s for s in rows if low <= s[field] <= high])
    return bins


def cluster_intervals(rows, seed):
    rng = np.random.default_rng(seed)
    sizes = (4, 6, 8, 12, 20, 32)
    counts = np.zeros((len(sizes), 64, 3),dtype=int)
    for r in rows:
        v = counts[sizes.index(r["m"]), r["replicate"]]
        v += (1, int(r["lo"] > 2), int(r["hi"] > 2))
    boot = np.zeros((4000,3),dtype=int)
    for cell in counts:
        boot += cell[rng.integers(64, size=(len(boot),64))].sum(axis=1)
    defined = boot[:,0] > 0
    return [float(np.quantile(boot[defined,col]/boot[defined,0],q)) for col,q in [(1,.025),(2,.975)]]


def auc(rows, feature):
    pos = [x[feature] for x in rows if x["lo"] > 2]
    neg = [x[feature] for x in rows if x["hi"] <= 2]
    if not pos or not neg:
        return None
    return sum((a>b)+0.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg))


def predictive(rows):
    keys = ("J","n","exhausted_touching_live","most_old_neighbors_one_live",
            "largest_older_part_attachment","movable_names","residual_except","short_except")
    matched = defaultdict(list)
    for r in rows:
        matched[r["age"],r["m"]].append(r)
    def stratified(key):
        numerator = denominator = 0
        for group in matched.values():
            value = auc(group,key)
            if value is None:
                continue
            pairs = sum(r["lo"]>2 for r in group)*sum(r["hi"]<=2 for r in group)
            numerator += value*pairs
            denominator += pairs
        return None if not denominator else numerator/denominator
    return {k: {"overall_auc":auc(rows,k), "initial_size_age_matched_auc":stratified(k)} for k in keys}


def analyze():
    records = [json.loads(x) for x in gzip.open(FAMILY/'sample_stages.jsonl.gz','rt')]
    shapes = json.loads((FAMILY/'sample_shape_index.json').read_text())['shapes']
    certified = json.loads(gzip.decompress((FAMILY/'reading_certificates.json.gz').read_bytes()))
    extra = json.loads((FAMILY/'short_bonds.json').read_text())
    short = {r['shape']:r['results']['6']['certified'] for r in extra['cases']}
    escalations = json.loads((FAMILY/'order_refined.json').read_text())
    if isinstance(escalations, dict):
        escalations = escalations.get('cases',escalations.get('rows',escalations.get('records',escalations)))
    if isinstance(escalations,list):
        escalations = {int(r['shape']):r for r in escalations}
    else:
        escalations = {int(k):v for k,v in escalations.items()}
    scores, rows = [], []
    starts = {(s['weighting'],s['m'],s['replicate']):s for s in records if s['kind']=='start'}
    for shape, base in zip(shapes,certified,strict=True):
        i = shape['shape']
        assert i == base['shape']
        lo,hi=base['lo'],base['hi']
        if i in escalations:
            val = escalations[i]
            if 'result' in val:
                val=val['result']
            lo,hi=max(lo,val['lo']),min(hi,val['hi'])
        if short.get(i):
            hi=min(hi,2)
        assert lo<=hi
        coarse=base.get('coarse',{})
        residual_except=bool(shape['can_grow'] and coarse.get('hi',0)>2)
        short_except=bool(residual_except and not short.get(i,False))
        scores.append(dict(shape=i,lo=lo,hi=hi,observations=len(shape['observations']),
                           residual_except=residual_except,short_except=short_except))
        for w,m,replicate,age in shape['observations']:
            rows.append(dict(weighting=w,m=m,replicate=replicate,age=age,J=shape['J'],n=shape['n'],
                             lo=lo,hi=hi,shape=i,residual_except=residual_except,short_except=short_except,
                             **shape['boundary']))
    summary={}
    for w in sorted({x['weighting'] for x in rows}):
        group=[x for x in rows if x['weighting']==w]
        continuing=[x for x in group if x['hi']>0]
        summary[w]={
            "stages":describe(group), "continuing":describe(continuing),
            "bootstrap_95_share_above_two":cluster_intervals(group,20261119),
            "by_age":{i:describe([x for x in group if x['age']==i]) for i in (1,2,3)},
            "by_start_size":{m:describe([x for x in group if x['m']==m]) for m in (4,6,8,12,20,32)},
            "by_junctions":grouped(group,'J',((1,9),(10,19),(20,39),(40,79),(80,150))),
            "by_distinctions":grouped(group,'n',((1,19),(20,39),(40,79),(80,149),(150,240))),
            "by_older_part_attachments":grouped(continuing,'largest_older_part_attachment',((0,1),(2,2),(3,3),(4,6),(7,12),(13,100))),
            "by_total_attachments":grouped(continuing,'exhausted_touching_live',((0,2),(3,5),(6,9),(10,19),(20,49),(50,200))),
            "features_on_continuing":predictive(continuing),
            "first_age_in_degree_two_free_family":sum(bool(degree_two_free_start(starts[(w,r['m'],r['replicate'])]['stars']))
                                     for r in group if r['age']==1),
            "draws_with_exception":len({(r['m'],r['replicate']) for r in group if r['lo']>2}),
            "reaching_draws":sum(r['age']==1 for r in group)}
    result={"bootstrap":"4,000 draws of complete initial-start clusters, separately within weighting and 6 initial-size strata. Both endpoints use certified bounds.",
            "summary":summary,"shape_scores":scores}
    (FAMILY/'distribution.json').write_text(json.dumps(result,indent=2)+'\n')
    return summary


if __name__ == '__main__':
    opts=argparse.ArgumentParser(description=__doc__).parse_args()
    for w,cell in analyze().items():
        print(w,cell['stages']['orders'],cell['bootstrap_95_share_above_two'])
