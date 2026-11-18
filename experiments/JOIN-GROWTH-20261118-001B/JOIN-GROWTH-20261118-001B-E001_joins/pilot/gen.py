"""Generic pilot join.  argv: name, json spec {parts: [[sizes, edges], ...], join: [[i, j], ...] on global indices (parts numbered in
order, then extra knots), extra: number of path knots, mode: keep | consume | raw, rounds}.  In 'raw' mode, sizes are given
explicitly in spec['sizes']."""
import sys, json, time, gc
gc.disable()
from joins import *
import fastlib; fastlib.install(F)

name, spec = sys.argv[1], json.loads(sys.argv[2])
sizes0, edges, spare, off = [], [], [], 0
for sz, ed in spec['parts']:
    sp = spares(sz, [tuple(e) for e in ed])
    edges += [(off + i, off + j) for i, j in ed]
    sizes0 += sz; spare += sp; off += len(sz)
spare += [0] * spec.get('extra', 0)
nk = off + spec.get('extra', 0)
edges += [tuple(e) for e in spec['join']]
mode = spec.get('mode', 'keep')
if mode == 'raw':
    sz = spec['sizes']
else:
    sh, d = demand_of(nk, edges)
    jn = Counter()
    for i, j in spec['join']:
        jn[i] += 1; jn[j] += 1
    if mode == 'consume':
        spare = [max(0, s - jn[k]) for k, s in enumerate(spare)]
    sz = [max(3, sh[k] + d[k] + spare[k]) for k in range(nk)]
t = time.time()
prog = lambda P: print(json.dumps(dict(kind=name, r=0, sizes=sz, out='partial', rounds=P.rounds, c=P.counts_by_round(), desc=None,
                                       secs=round(time.time() - t))), flush=True)
P, out = grow(stars_from(sz, edges), rounds=spec.get('rounds', 40), tmax=spec.get("tmax", 1500), maxj=spec.get("maxj", 400000), progress=prog, linalg=False)
c = P.counts_by_round()
print(json.dumps(dict(kind=name, r=0, sizes=sz, spare=spare, out=out, rounds=len(c) - 1, c=c, desc=describe(c),
                      secs=round(time.time() - t))), flush=True)
