import sys, time, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import catalogue as C
t = time.time()
nmax = int(sys.argv[1])
gs = list(C.graphs(7)) if nmax <= 7 else C.graphs8()
gs = [g for g in gs if g[0] <= nmax]
res = C.enumerate_minimal_lazy(gs, 2, log=lambda m: print(m, round(time.time() - t, 1), flush=True))
print(len(res), round(time.time() - t, 1), Counter((v['n'], sum(v['spares']), v['by']) for v in res.values()), flush=True)
json.dump([v for v in res.values()], open(HERE / f'catlazy_{nmax}.json', 'w'))
