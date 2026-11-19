"""Pilot: the eddy rule on every touch-census arrangement against the census's exponential set (CLUSTER-ALL's 13)."""
import itertools, json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E  # noqa: E402
sys.path.insert(0, str(E.ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib  # noqa: E402

def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e

exp = {(tuple(r[0][0]), tuple(r[0][1])) for r in json.load(open(E.ROOT / 'artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/posthoc_dimension.json'))['exponential']}
tab = Counter()
rank_counts = Counter()
for k in arrlib.arrangements(5):
    sz, e = edges_of(k)
    v = E.eddy(sz, e)
    vh = E.eddy(sz, e, skip_hyper=False)
    tab[(str(v), str(vh), k in exp)] += 1
    L = E.loops(sz, e)
    if L:
        rank_counts[(L['rank_with_hyperedges'], L['rank_without'])] += 1
print(dict(tab))
print(dict(rank_counts))
