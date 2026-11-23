"""Targeted search (exploratory): seeded random sides with up to 6 knots, written as a side-table file in the format of sides.py so
that pairs.py combines them exactly as in the census.

usage: targeted.py CUT MODE SEED SECONDS MAXTABLES [SUFFIX]
  MODE alloc : x2 and x3 held by one knot, x1 by a different knot (the pre-registered target)
  MODE free  : no allocation condition (extension, reported separately)
A side has 3 observer distinctions (one holder each), CUT cut distinctions (one holder each), I internal distinctions (one or two
holders; at most 9, so at most 14 distinctions), and k knots (2..6) of arity 3 or 4 with law even, odd or not-all-equal.
"""
import sys, json, time
import numpy as np
import common as c

cut = int(sys.argv[1]); mode = sys.argv[2]; seed = int(sys.argv[3]); seconds = float(sys.argv[4]); maxt = int(sys.argv[5])
suffix = sys.argv[6] if len(sys.argv) > 6 else ''
tag = f'c{cut}_t6{mode}{suffix}'
rng = np.random.default_rng(seed)
LAWS = ('even', 'odd', 'nae')

def gen():
    k = int(rng.integers(2, 7))
    sizes = [int(rng.choice([3, 4])) for _ in range(k)]
    S = sum(sizes); R = S - 3 - cut                # = i + d (internal distinctions plus doubly held ones)
    if R < 0: return None
    lo = (R + 1) // 2
    hi = min(R, 9)
    if lo > hi: return None
    i = int(rng.integers(lo, hi + 1)); d = R - i
    if d > i or d < 0: return None
    n = 3 + cut + i
    cap = list(sizes); mem = [[] for _ in range(k)]
    def put(dist, kn):
        if cap[kn] == 0 or dist in mem[kn]: return False
        mem[kn].append(dist); cap[kn] -= 1; return True
    if mode == 'alloc':
        k1 = int(rng.integers(k)); k2 = int(rng.integers(k))
        if k2 == k1: return None
        if cap[k1] < 2 or cap[k2] < 1: return None
        put(1, k1); put(2, k1); put(0, k2)
    else:
        for dist in range(3):
            kn = int(rng.integers(k))
            if not put(dist, kn): return None
    holders = [1] * cut + [2] * d + [1] * (i - d)
    dists = list(range(3, n)); order = rng.permutation(len(dists))
    for q in order:
        dist = dists[q]; h = holders[q]
        free = [kn for kn in range(k) if cap[kn] > 0]
        if len(free) < h: return None
        pick = rng.choice(free, size=h, replace=False)
        for kn in pick: put(dist, int(kn))
    if any(cap): return None
    laws = [LAWS[int(rng.integers(3))] for _ in range(k)]
    return n, i, [(tuple(sorted(m)), l) for m, l in zip(mem, laws)]

def table(n, i, knots):
    idx = np.arange(2 ** n)
    bits = [((idx >> (n - 1 - j)) & 1) for j in range(n)]
    ok = np.ones(2 ** n, dtype=bool)
    for m, law in knots:
        s = sum(bits[j] for j in m)
        if law == 'nae': ok &= (s != 0) & (s != len(m))
        elif law == 'even': ok &= (s % 2 == 0)
        else: ok &= (s % 2 == 1)
    return ok.reshape(8, 2 ** cut, 2 ** i).sum(-1)

def names(i):
    return ['x1', 'x2', 'x3'] + [f's{j + 1}' for j in range(cut)] + [f'h{j + 1}' for j in range(i)]

t0 = time.time(); tabs = {}; tried = 0; valid = 0
while time.time() - t0 < seconds and len(tabs) < maxt:
    g = gen(); tried += 1
    if g is None: continue
    valid += 1
    n, i, knots = g
    T = table(n, i, knots)
    if T.sum() == 0: continue
    key = T.astype(np.int16).tobytes()
    if key not in tabs:
        nm = names(i)
        st = dict(internal=i, knots=[dict(members=[nm[j] for j in m], law=l) for m, l in knots])
        tabs[key] = (T.astype(np.int16), st)
keys = list(tabs)
Tarr = np.stack([tabs[k][0] for k in keys])
alloc = np.ones(len(keys), dtype=bool) if mode == 'alloc' else np.zeros(len(keys), dtype=bool)
np.savez_compressed(f'{c.ART}/sides_{tag}.npz', T=Tarr, alloc=alloc, nonempty=np.ones(len(keys), dtype=bool))
json.dump(dict(cut=cut, kmax=6, mode=mode, seed=seed, seconds=time.time() - t0, tried=tried, valid=valid,
               structures=[dict(struct=tabs[k][1], alloc_struct=(tabs[k][1] if mode == 'alloc' else None)) for k in keys]),
          open(f'{c.ART}/sides_{tag}.json', 'w'))
print(f'{tag}: {tried} draws, {valid} lawful structures, {len(keys)} distinct nonempty tables, {time.time() - t0:.0f}s')
