import json, sys, time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import kindlib as K
ROOT = HERE.parents[3]
pop = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json').read_text())
ids = [int(a) for a in sys.argv[1].split(',')]
rounds = int(sys.argv[2]); Rs = [int(a) for a in sys.argv[3].split(',')]
for R in Rs:
    sigs = defaultdict(set); perround = []
    t0 = time.time()
    for i in ids:
        counts, pr = K.grow_kinds(pop[i], rounds, R)
        for t, (kind, sig) in enumerate(pr, start=1):
            ks = Counter(kind.values())
            perround.append((i, t, len(ks)))
            for j, k in kind.items():
                sigs[k].add(tuple(sorted(sig[j].items())))
    det = sum(1 for k, s in sigs.items() if len(s) == 1)
    print(f'R={R}: kinds {len(sigs)}, deterministic {det}, time {time.time()-t0:.1f}s')
    by = defaultdict(list)
    for i, t, n in perround: by[i].append(n)
    for i in ids: print('  start', i, 'kinds per round', by[i])
