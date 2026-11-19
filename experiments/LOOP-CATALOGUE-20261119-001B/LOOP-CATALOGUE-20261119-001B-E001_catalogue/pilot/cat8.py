import sys, time, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import catalogue as C
t = time.time()
gs = C.graphs8()
print('graphs', len(gs), round(time.time() - t, 1), flush=True)
res = C.enumerate_minimal_graphs(gs, 2)
print(len(res), round(time.time() - t, 1), Counter(sum(v['spares']) for v in res.values()), flush=True)
json.dump([v for v in res.values()], open(HERE / 'cat_8.json', 'w'))
