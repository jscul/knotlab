"""heldout.py OUT.jsonl: hypothesis H of README.md "Frozen", one size past (the stop rule's next check), on the 900 fresh
starts of six to eight knots (forbid.sampled, seed 20261206 + n), round 0, with the presentation search capped at 5,000
per start."""
import sys, json, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import presentations as PR
tally = collections.Counter()
with open(sys.argv[1], 'w') as f:
    for n in (6, 7, 8):
        for j, s in enumerate(PR.forbid.sampled(n, 300, 20261206 + n)):
            S = PR.forbid.supports_of(s); pres, capped = PR.presentations(S, limit=5000)
            pres = [P for P in pres if PR.connected(P)]; trees = {PR.tree_of(P) for P in pres}
            own = PR.tree_of(S)
            rec = {'start': 'held out %d-%d' % (n, j), 'presentations': len(pres), 'capped': capped,
                   'family partitions': len({t[0] for t in trees}), 'trees': len(trees), 'own tree among them': own in trees}
            if len(trees) > 1:
                rec['example'] = [[list(map(list, P)) for P in pres if PR.tree_of(P) != t][:1] for t in list(trees)[:2]]
            tally['starts'] += 1; tally['more than one presentation'] += len(pres) > 1
            tally['partition not recovered'] += len({t[0] for t in trees}) > 1; tally['tree not recovered'] += len(trees) > 1; tally['capped'] += capped
            f.write(json.dumps(rec) + '\n'); f.flush()
    f.write(json.dumps({'tally': dict(tally)}) + '\n')
print(dict(tally))
