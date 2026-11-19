"""Shared-runner job for DROPPED-JUNCTION-20261119-001B-E001.

Starts: the catalogue's five minimal eddies, the touch census's 13 rings (CLUSTER-ALL's exponential list), rings of 9 to 13 knots
with one spare, and 300 random five-knot census arrangements that grow (seed 20261119).  For each, every dropped-junction choice of
the completed system (droplib.rechoices) is grown under parity, the cheapest growth, to 30 rounds or 60,000 junctions, and its
class read by LOOP-CATALOGUE's eddy.growth_class rule applied to the counts; each choice also records its degree in the completed
system."""
import importlib.util
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import droplib as D  # noqa: E402
ROOT = D.ROOT
_spec = importlib.util.spec_from_file_location('lc_job_iso', ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/job_iso.py')
_ISO = importlib.util.module_from_spec(_spec)
sys.modules['lc_job_iso'] = _ISO
_spec.loader.exec_module(_ISO)
classify = _ISO.classify


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def study(name, sizes, edges):
    stars = D.J.stars_from(sizes, edges)
    lines = D.completed_lines(stars)
    deg = {}
    for x, y in lines:
        deg[x] = deg.get(x, 0) + 1
        deg[y] = deg.get(y, 0) + 1
    rows = []
    for v, st in D.rechoices(stars).items():
        key = 'out' if v == 'out' else int(v)
        c, out = D.grow(st, rounds=30, maxj=60000)
        rows.append({'drop': v, 'degree': deg.get(key, 0), 'class': classify(c, out), 'counts': c[:20], 'outcome': out})
    top = max(deg.values())
    tops = [k for k, d in deg.items() if d == top]
    return {'name': name, 'sizes': sizes, 'edges': [list(x) for x in edges], 'choices': rows,
            'original_is_unique_top': tops == ['out']}


def starts():
    cat = json.loads((ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
    for i, ent in enumerate(cat):
        yield f'cat-{i}', 'eddy', ent['sizes'], [tuple(x) for x in ent['edges']]
    exp = json.loads((ROOT / 'artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/posthoc_dimension.json').read_text())['exponential']
    for i, r in enumerate(exp):
        sz, e = edges_of(r[0])
        yield f'ring-{i}', 'eddy', sz, e
    for n in range(9, 14):
        e = [tuple(sorted((i, (i + 1) % n))) for i in range(n)]
        sz = D.J.bare_sizes(n, e)
        sz[0] += 1
        yield f'R-{n}', 'eddy', sz, e
    sys.path.insert(0, str(ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
    import arrlib
    sys.path.insert(0, str(ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue'))
    import eddy as EE
    keys = sorted(k for k in arrlib.arrangements(5) if len(k[0]) == 5)
    rng = random.Random(20261119)
    rng.shuffle(keys)
    k = 0
    for key in keys:
        sz, e = edges_of(key)
        A = EE.Cl.analyse(sz, e)
        if A.get('stall') or not A.get('scope', True):
            continue
        yield f'S-{k:03d}', 'sample', sz, e
        k += 1
        if k == 300:
            break


def cases():
    batch = []
    for i, (name, kind, sz, e) in enumerate(starts()):
        batch.append({'name': name, 'kind': kind, 'sizes': sz, 'edges': [list(x) for x in e]})
        if len(batch) == 10:
            yield f'C-{i // 10:03d}', {'starts': batch}
            batch = []
    if batch:
        yield 'C-last', {'starts': batch}


def run(case_id, payload):
    return {'starts': [dict(study(s['name'], s['sizes'], [tuple(x) for x in s['edges']]), kind=s['kind']) for s in payload['starts']]}
