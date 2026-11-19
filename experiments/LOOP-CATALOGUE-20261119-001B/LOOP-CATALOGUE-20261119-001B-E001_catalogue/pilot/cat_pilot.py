import sys, time, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import catalogue as C
t = time.time()
nmax = int(sys.argv[1])
res = C.enumerate_minimal(nmax, max_spares=int(sys.argv[2]))
print(len(res), round(time.time() - t, 1))
from collections import Counter
print(Counter((v['n'], sum(v['spares'])) for v in res.values()))
json.dump([v for v in res.values()], open(HERE / f'cat_{nmax}.json', 'w'))
