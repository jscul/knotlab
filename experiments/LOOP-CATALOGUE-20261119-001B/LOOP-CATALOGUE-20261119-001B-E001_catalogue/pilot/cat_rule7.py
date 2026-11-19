import sys, time, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import catalogue as C
t = time.time()
res = C.enumerate_minimal_lazy(list(C.graphs(7)), 2, log=lambda m: print(m, round(time.time() - t, 1), flush=True), grow=False)
und = res.pop('_undecided')
json.dump(und, open(HERE / 'undecided_7.json', 'w'))
print(len(res), 'undecided', len(und), round(time.time() - t, 1), Counter((v['n'], sum(v['spares'])) for v in res.values()), flush=True)
json.dump([v for v in res.values()], open(HERE / 'catrule_7.json', 'w'))
