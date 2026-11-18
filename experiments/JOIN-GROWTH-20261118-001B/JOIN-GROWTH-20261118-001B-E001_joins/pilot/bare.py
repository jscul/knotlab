"""Bare start: argv name, json {n: knots, edges: [[i, j]...], spare: {knot: k}, rounds, maxj, tmax}.  Each knot gets
max(3, shared + round-1 demand) places plus its listed spare distinctions."""
import sys, json, time, gc
gc.disable()
from joins import *
import fastlib; fastlib.install(F)
name, spec = sys.argv[1], json.loads(sys.argv[2])
nk, edges = spec['n'], [tuple(e) for e in spec['edges']]
sh, d = demand_of(nk, edges)
spare = [0] * nk
for k, v in spec.get('spare', {}).items():
    spare[int(k)] += v
sz = [max(3, sh[k] + d[k]) + spare[k] for k in range(nk)]
t = time.time()
prog = lambda P: print(json.dumps(dict(kind=name, sizes=sz, out='partial', rounds=P.rounds, c=P.counts_by_round(), secs=round(time.time() - t))), flush=True)
P, out = grow(stars_from(sz, edges), rounds=spec.get('rounds', 60), tmax=spec.get('tmax', 2000), maxj=spec.get('maxj', 500000), progress=prog, linalg=False)
print(json.dumps(dict(kind=name, sizes=sz, out=out, rounds=P.rounds, c=P.counts_by_round(), secs=round(time.time() - t))), flush=True)
