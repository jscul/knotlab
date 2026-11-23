"""Finer vertex search around a point (lam0, mu0) of the reference search: grid lam0 +- h, mu0 +- h in steps of s, N_LP random-objective
linear programs per point (see reference_vertices.py).  usage: reference_fine.py LAM0 MU0 H S N_LP SEED TAG"""
import sys, time, json
import numpy as np
import common as c
from reference_vertices import sample_point

lam0, mu0, h, s, nlp, seed = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
tag = sys.argv[7]
rng = np.random.default_rng(seed)
n = int(round(h / s))
t0 = time.time(); out = []; best = (0, None)
for i in range(-n, n + 1):
    for j in range(-n, n + 1):
        lam = round(lam0 + i * s, 6); mu = round(mu0 + j * s, 6)
        if not (0.5 < lam < 2 and 0.5 < mu < 2): continue
        V = sample_point(lam, mu, nlp, rng)
        if V is None: continue
        sc = c.score_batch_c(V)
        q = int(np.argmax(sc))
        out.append((lam, mu, len(V), float(sc[q])))
        if sc[q] > best[0]: best = (float(sc[q]), dict(lam=lam, mu=mu, M=V[q].tolist()))
    if time.time() - t0 > 560: print('time limit'); break
json.dump(dict(center=[lam0, mu0], out=out, best=best), open(f'{c.ART}/reference_fine_{tag}.json', 'w'))
print(f'{tag}: {len(out)} points, {time.time() - t0:.0f}s, best {best[0]:.9f} at lam {best[1]["lam"]} mu {best[1]["mu"]}')
