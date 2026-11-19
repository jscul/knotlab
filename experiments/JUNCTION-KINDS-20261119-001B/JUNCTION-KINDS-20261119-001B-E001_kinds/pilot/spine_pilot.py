import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import spinelib as S
ROOT = HERE.parents[3]
pop = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json').read_text())
cat = json.loads((ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
nm, T, lags = sys.argv[1], int(sys.argv[2]), tuple(int(a) for a in sys.argv[3].split(','))
st = pop[int(nm[2:])] if nm.startswith('G-') else cat[int(nm[2:])]
t0 = time.time()
P = S.grow(st, T, 60000)
par, ch, br = S.family(P)
s = S.out_shares(P, ch)
per = [len({s[j] for j in br[t]}) for t in range(P.rounds)]
print(nm, 'counts', P.counts_by_round(), 'distinct out-shares per round', per, f'{time.time()-t0:.1f}s')
k = S.sum_kinds(P, ch, 6)
print(' sum-kinds per round', [len({k[j] for j in br[t]}) for t in range(P.rounds - 6 + 1)])
for t in range(max(lags) + 1, P.rounds + 1, 3):
    a = S.spine(P, par, br, t, lags); b = S.spine(P, par, br, t, lags, only_single=True)
    print(' t', t, 'all:', a['left'], a['right'], a['matched'], ' m=1:', b['matched'], 'deg L', b['deg_left'][:6], 'deg R', b['deg_right'][:6], flush=True)
