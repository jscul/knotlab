import sys, json
from joins import *
import fastlib; fastlib.install(F)
R = ([4,4,4,4,5], ring_edges(5))
Pp = ([3,3], [(0,1)])
spR = spares(*R); spP = spares(*Pp)
kind, r = sys.argv[1], int(sys.argv[2])
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 34
if kind == 'ring': nk, e, sp = 5, R[1], spR
elif kind == 'pair': nk, e, sp = 2, Pp[1], spP
elif kind == 'dist': nk, e, sp = 7, ring_edges(5) + [(5, 6), (r, 5)], spR + spP
elif kind == 'knot': nk, e, sp = 6, ring_edges(5) + [(r, 5)], spR + [spP[1]]
elif kind == 'path1': nk, e, sp = 8, ring_edges(5) + [(5, 6), (r, 7), (7, 5)], spR + spP + [0]
elif kind == 'rr-dist':
    i, j = divmod(r, 5); nk, e, sp = 10, ring_edges(5) + ring_edges(5, 5) + [(i, 5 + j)], spR + spR
elif kind == 'rr-knot':
    i, j = divmod(r, 5)
    eB = [(i, 5), (5, 6), (6, 7), (7, 8), (8, i)]
    spB = spR[j+1:] + spR[:j]
    sp = spR + spB
    sp[i] = spR[i] + spR[j]
    nk, e = 9, ring_edges(5) + eB
sz = joined_sizes(nk, e, sp)
import time; t = time.time()
prog = lambda P: print(json.dumps(dict(kind=kind, r=r, sizes=sz, out='partial', rounds=P.rounds, c=P.counts_by_round(), desc=None, secs=round(time.time()-t))), flush=True)
P, out = grow(stars_from(sz, e), rounds=rounds, tmax=1500, maxj=200000, progress=prog, linalg=False)
c = P.counts_by_round()
print(json.dumps(dict(kind=kind, r=r, sizes=sz, spare=sp, out=out, rounds=len(c) - 1, c=c, desc=describe(c), secs=round(time.time() - t))), flush=True)
