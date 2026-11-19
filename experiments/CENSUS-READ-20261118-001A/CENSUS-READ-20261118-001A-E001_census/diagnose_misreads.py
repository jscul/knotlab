"""Diagnosis after the preliminary readout (not a prediction): small R3n misreads without shared pairs, with their tables."""
import sys, json
from collections import Counter
from itertools import combinations
sys.setrecursionlimit(100000)
sys.path.insert(0, '.')
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/scripts')
import job, exact_table as X, reader3n as N
from longrun import load_results
R, S, F, A = job.R, job.S, job.F, job.A
recs = load_results('/home/jscul/p-vs-np-contact-first/runs/census-exact')
shown = 0
for cid, r in sorted(recs.items()):
    for a in r['result']['arrangements']:
        for st in a['stages']:
            if st['r3n'] == 'misread' and st['max_shared'] < 2 and st['junctions'] <= 12 and shown < 4:
                key = (tuple(a['key'][0]), tuple(a['key'][1]))
                P = S.from_junctions(A.stars_of(key))
                for _ in range(st['round']):
                    P.step(S.gf2(F.fewest), None)
                stars = [frozenset(b) for b in P.bits_of]
                K = max(map(len, stars)); H = K + 2
                tab = X.exact_table(stars, H)
                fl = Counter()
                got = N.r3n(tab, H + 1, fl)
                truth = set(stars)
                print('key', a['key'], 'round', st['round'], 'conn', st['connectivity'], 'flags', dict(fl))
                print('  truth', sorted(map(sorted, truth)))
                print('  missed', sorted(map(sorted, truth - got)), 'extra', sorted(map(sorted, got - truth)))
                for m in truth - got:
                    print('   missed', sorted(m), 'size', len(m), 'pair distances', sorted(Counter(tab[tuple(sorted(p))] for p in combinations(m, 2)).items()))
                shown += 1
    if shown >= 4: break
