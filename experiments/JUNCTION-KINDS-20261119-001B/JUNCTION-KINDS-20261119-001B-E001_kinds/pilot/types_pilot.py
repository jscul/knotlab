import json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import spinelib as S
ROOT = HERE.parents[3]
pop = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json').read_text())
cat = json.loads((ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
nm, T, lags, t0 = sys.argv[1], int(sys.argv[2]), tuple(int(a) for a in sys.argv[3].split(',')), int(sys.argv[4])
st = pop[int(nm[2:])] if nm.startswith('G-') else cat[int(nm[2:])]
P = S.grow(st, T, 60000)
par, ch, br = S.family(P)
c = P.counts_by_round()
print(nm, c)
rels = {t: S.typed_relation(P, par, br, t, lags) for t in range(t0, P.rounds + 1)}
freq = Counter(ty for rel in rels.values() for *_, ty in rel)
types = [ty for ty, _ in freq.most_common(10)]
print(' types', len(freq), [(str(ty)[:40], n) for ty, n in freq.most_common(10)])
half = (t0 + P.rounds) // 2
first = {t: r for t, r in rels.items() if t <= half}
second = {t: r for t, r in rels.items() if t > half}
g = S.biregular_sets(first, br, lags, types, 3)
print(' biregular on the first half:', [(tuple(str(x)[:30] for x in Tt), e) for Tt, e in g][:10])
for Tt, e in g:
    print('   second half:', S.biregular_sets(second, br, lags, list(Tt), len(Tt)))
