"""posthoc_tie.py: on a sample of the census's parity hits (the first 60 in case order, W1 under R1), the signed weighting
of the four read values: its support and whether one read of each reader is tied there (A5 and C4 predict both)."""
import sys, json, collections, itertools
import numpy as np
sys.path.insert(0, '../../scripts')
from longrun import load_results
import sides as S

recs = load_results('../../runs/side-sign-census'); F = S.forbid(); starts = S.census_starts()
seen, out = 0, collections.Counter()
for case in sorted(recs):
    for row in recs[case]['result']['rows']:
        if row['law'] != 'parity' or isinstance(row['classes'], str): continue
        for c in row['classes']:
            H = c['weightings'].get('W1', {}).get('R1', {}).get('hits', [])
            if not H or seen >= 60: continue
            st, _ = S.grow_rounds(F.supports_of(starts[row['start']]), 'parity', row['round'])
            P = S.Pattern(st[row['round']]); x = S.states(P, 'parity')
            if x is None: continue
            sig = P.lift(tuple(c['perm']), c['lift'] == 'max')
            w, _ = S.weightings(P, sig, c['kind'], None if c['kind'] != 'two' else
                                [cc for cc in P.sides(tuple(c['perm']), sig)[1]], x, 'parity')
            w = w['W1']; h = H[0]; reads = list(h[0]) + list(h[1])
            J = collections.Counter()
            for v, ww in zip(x.tolist(), w.tolist()): J[tuple((v >> i) & 1 for i in reads)] += ww
            supp = [k for k, v in J.items() if v]
            ties = [u for u in itertools.product((0, 1), repeat=4) if any(u) and len({sum(a * b for a, b in zip(u, y)) % 2 for y in supp}) == 1]
            cross = any((u[0] or u[1]) and (u[2] or u[3]) and sum(u) == 2 for u in ties)
            out[(len(supp), cross)] += 1; seen += 1
print(json.dumps({'hits checked': seen, '(support size, one read of each reader tied)': {str(k): v for k, v in out.items()}}))
