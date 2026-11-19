"""Pilot: rebuild STATES-GROWTH's undefined points, list their presentations, grow each 3 rounds."""
import itertools, json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import manylib as ML
sys.path.insert(0, str(ML.ROOT / 'scripts'))
from longrun import load_results
import importlib.util
spec = importlib.util.spec_from_file_location('sgjob', ML.ROOT / 'experiments/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/job.py')
SG = importlib.util.module_from_spec(spec); spec.loader.exec_module(SG)
R = load_results(str(ML.ROOT / 'runs/states-growth'))
T = [t for c, r in sorted(R.items()) if c.startswith('C-') for t in r['result']['trajectories'] if 'undefined' in t['verdicts']]
print('undefined trajectories', len(T))
tab = Counter(); rows = []
for t in T[:40]:
    a, b = t['key']
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(a)), 2), b):
        e += [(i, j)] * m
    stars = SG.J.stars_from(list(a), e)
    k = t['verdicts'].index('undefined')
    for _ in range(k):
        n = 1 + max(x for s in stars for x in s)
        _, M = SG.core_of(stars, n)
        v = SG.SL.verdict(stars, M)
        stars, _ = SG.step(SG.renumber(M) if v != 'saturated' else stars)
    for pool in ('M', 'stage'):
        pres, nc = ML.presentations(stars, pool=pool)
        if pres is None:
            tab[(pool, 'too many candidates')] += 1; continue
        cls = ML.iso_classes(pres)
        own = sorted(map(sorted, stars)) in [sorted(map(sorted, p)) for p in pres]
        outs = [tuple(ML.grow(c[0])) for c in cls]
        tab[(pool, len(pres), len(cls), 'own' if own else 'not own', 'agree' if len(set(outs)) <= 1 else 'differ')] += 1
    pres = None
print(dict(tab))
for r in rows[:6]: print(r)
