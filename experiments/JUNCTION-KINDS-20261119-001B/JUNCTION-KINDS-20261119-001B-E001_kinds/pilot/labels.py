"""Pilot: do the junctions' own labels (parents, fresh) stay bounded?  Max parents and max fresh per round, and the number of
distinct (parents, fresh) labels per round, for the given starts."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import kindlib as K
ROOT = HERE.parents[3]
pop = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json').read_text())
cat = json.loads((ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
rounds = int(sys.argv[1])
todo = [('G-%03d' % i, pop[i]) for i in [28, 44, 52, 55, 56, 58, 61, 65, 66, 68]] + [('C-%d' % i, c) for i, c in enumerate(cat)]
for name, st in todo:
    P = K.start(st)
    mp, mf, nl, cs = [], [], [], []
    for t in range(rounds):
        r = P.step(K.E.J.F.fewest, None)
        if r is None or r['new'] == 0 or len(P.bits_of) > 150000:
            break
        born = [j for j in range(len(P.bits_of)) if P.round_of[j] == P.rounds]
        mp.append(max(P.parents[j] for j in born)); mf.append(max(P.fresh[j] for j in born))
        nl.append(len({(P.parents[j], P.fresh[j]) for j in born})); cs.append(len(born))
    print(name, 'counts', cs[-3:], 'max parents', mp[::3], 'max fresh', mf[::3], 'labels', nl[::3], flush=True)
