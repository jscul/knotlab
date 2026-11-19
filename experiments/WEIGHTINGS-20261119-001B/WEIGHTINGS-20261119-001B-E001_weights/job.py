"""Shared-runner job for WEIGHTINGS-20261119-001B-E001.

Weightings (weightlib): tree, tree-s25, tree-s50, tree-s100, tree+, grow, config; sizes n = 5, 6, 7, 8, 10, 12, 16, 20; 2,000
independent samples per (weighting, size), seeded by the case id.  Each sample records DOUBLE-IDENT's fine class (stall; out, with
(S3) or (S4); none; one loose; in), the theorem's growth class and reason outside stalls and 'out', the largest knot, the numbers of
lines and of knot pairs, for tree the leaves beside a knot of degree 2, and for tree+ the extra lines.  At n = 8, 12 and 20 a stratified
regrowth: every in-class sample predicted three-or-more or exponential (up to 50) and the first 30 other in-class growers, compared
round by round to round 6 with the relayed cover (DOUBLE-IDENT's model)."""
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import weightlib as W  # noqa: E402

KINDS = ('tree', 'tree-s25', 'tree-s50', 'tree-s100', 'tree+', 'grow', 'config')
SIZES = (5, 6, 7, 8, 10, 12, 16, 20)
N = 2000
DC, SL = W.SL.DC, W.SL


def cases():
    for k in KINDS:
        for n in SIZES:
            yield f'{k}-n{n:02d}', {'kind': k, 'n': n}


def run(case_id, payload):
    kind, n = payload['kind'], payload['n']
    rng = random.Random(f'weightings-{case_id}')
    out = []
    hard_done = easy_done = 0
    for _ in range(N):
        sizes, e = W.sample(kind, n, rng)
        c, D, why, sz, ce = W.classify(sizes, e)
        rec = {'cls': c, 'max_places': max(sizes), 'lines': len(e), 'pairs': len(set(e))}
        if kind == 'tree':
            deg = Counter()
            for a, b in e:
                deg[a] += 1
                deg[b] += 1
            nbr = {a: b for a, b in e if deg[a] == 1}
            nbr.update({b: a for a, b in e if deg[b] == 1})
            rec['ray_leaves'] = sum(1 for k, w in nbr.items() if deg[w] == 2)
        if kind == 'tree+':
            rec['extra'] = len(e) - (n - 1)
        if c == 'out':
            nn, nb, opn, live, groups, d = DC.data(sz, ce)
            rec['why'] = 'S3' if any(len(g) > 2 for g in groups) else 'S4'
        elif c != 'stall':
            rec['growth'] = SL.label(D)
            rec['why'] = why
            hard = D == 'exp' or (isinstance(D, int) and D >= 3)
            if c == 'in' and n in (8, 12, 20) and D != 0 and ((hard and hard_done < 50) or (not hard and easy_done < 30)):
                a, b = DC.growth(sz, ce), DC.model(sz, ce)
                rec['regrown_agree'] = all(a.get(t, {}) == b.get(t, {}) for t in range(DC.T + 1) if t in a or t in b)
                rec['regrown_kind'] = 'hard' if hard else 'other'
                if hard:
                    hard_done += 1
                else:
                    easy_done += 1
        out.append(rec)
    return {'samples': out}
