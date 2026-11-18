"""Shared-runner job for PLUS-ONE-20261118-001B-E001.

Part census: every settled growing arrangement with a birth in TOUCH-CENSUS-20261118-001's run (runs/touch-census, 26,341 read),
regrown 15 rounds to read its births; scored against that census's measured dimension.  Part six: random connected arrangements of
six knots of three to five places (uniform sizes, then multiplicities added one shared distinction at a time at random while degrees
allow, kept if connected), grown under the fewest counts with the census's dimension reader."""
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import linked as Lk  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
A = Lk.A
_SEL = None


def setup(params):
    global _SEL
    _SEL = select()


def select():
    from longrun import load_results
    R = load_results(str(ROOT / 'runs/touch-census'))
    out = []
    for c, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        for a in r['result']['arrangements']:
            if a['any_birth'] and a['dim'] is not None:
                out.append((a['key'], a['dim'], a['rule']))
    return out


def six(seed):
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(6)]
        deg = [0] * 6
        M = [[0] * 6 for _ in range(6)]
        pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
        for _ in range(rng.randint(5, 12)):
            i, j = rng.choice(pairs)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                M[i][j] += 1
                M[j][i] += 1
                deg[i] += 1
                deg[j] += 1
        if A.connected(6, M):
            return A.canon(sizes, M)


def cases():
    sel = _SEL if _SEL is not None else select()
    for s in range(0, len(sel), 200):
        yield f'census-{s // 200:03d}', {'part': 'census', 'lo': s, 'hi': min(len(sel), s + 200)}
    for s in range(400):
        yield f'six-{s:03d}', {'part': 'six', 'seed': 50000 + s}


def run(case_id, p):
    if p['part'] == 'census':
        sel = _SEL if _SEL is not None else select()
        out = []
        for key, dim, rule in sel[p['lo']:p['hi']]:
            k = (tuple(key[0]), tuple(key[1]))
            P, o, births = Lk.grow_births(A.stars_of(k), rounds=15, deadline=time.time() + 60)
            bc, bs, sh = Lk.linked_rule(P, births)
            out.append({'key': key, 'dim': dim, 'census_rule': rule, 'largest_class': bc, 'linked_sum': bs, 'shapes': sh, 'outcome15': o})
        return {'rows': out}
    key = six(p['seed'])
    P, o, births = Lk.grow_births(A.stars_of(key), rounds=30, deadline=time.time() + 300)
    d = A.measured_dimension(P, o if o != 'timed' else 'big')
    bc, bs, sh = Lk.linked_rule(P, births)
    return {'key': [list(key[0]), list(key[1])], 'outcome': o, 'dim': d, 'any_birth': any(births), 'largest_class': bc,
            'linked_sum': bs, 'shapes': sh, 'last': P.counts_by_round()[-5:]}
