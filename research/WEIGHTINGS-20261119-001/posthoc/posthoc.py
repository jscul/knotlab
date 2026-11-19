"""Post-hoc checks of WEIGHTINGS-20261119-001 (after the frozen run was read; not part of its predictions).

1. The five-place lemma on bare trees: every unlabelled tree of 3 to 14 knots is read at bare sizes; among those whose knots all
   have at most five places, no growth class is three-or-more dimensional or exponential (the theorem's reading, dims.predict).
2. The dead-hub start: ten knots of at most five places, in the class, read as three-dimensional; its growth is compared with the
   relayed cover to round 6, and grown by the program's engine (joinlib.grow) to round 20.
python3 -B posthoc.py <out.json>"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
_s = importlib.util.spec_from_file_location('w_lib', ROOT / 'experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
W = importlib.util.module_from_spec(_s)
sys.modules['w_lib'] = W
_s.loader.exec_module(W)
DC, SL, J = W.SL.DC, W.SL, W.J


def trees():
    out = {}
    for n in range(3, 15):
        c = Counter()
        for T in nx.nonisomorphic_trees(n):
            e = sorted(tuple(sorted(x)) for x in T.edges())
            sizes = J.bare_sizes(n, e)
            cls, D, why, sz, ce = W.classify(sizes, e)
            small = max(sizes) <= 5
            c[('<=5' if small else '>5', cls, SL.label(D) if D is not None else None)] += 1
        out[n] = {' '.join(map(str, k)): v for k, v in sorted(c.items(), key=str)}
    bad = [(n, k) for n, row in out.items() for k in row if k.startswith('<=5') and ('exponential' in k or any(
        f'dimension {d}' in k for d in range(3, 15)))]
    return out, bad


def dead_hub():
    # hub 0 (three places, all shared: dead); arms 0 - a_i - x_i - k_i with a_i = 1..3 (five places), x_i = 4..6, k_i = 7..9
    e = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9)]
    sizes = [3, 5, 5, 5, 3, 3, 3, 3, 3, 3]
    cls, D, why, sz, ce = W.classify(sizes, e)
    a, b = DC.growth(sz, ce), DC.model(sz, ce)
    agree = all(a.get(t, {}) == b.get(t, {}) for t in range(DC.T + 1) if t in a or t in b)
    counts = J.grow(sz, ce, rounds=20)
    return {'sizes': sizes, 'edges': e, 'class': cls, 'reading': SL.label(D), 'agree_to_round_6': agree,
            'per_round_to_6': {t: int(sum(v.values())) for t, v in sorted(a.items())}, 'engine_per_round': counts}


if __name__ == '__main__':
    tr, bad = trees()
    res = {'bare_trees_by_size': tr, 'five_place_trees_with_three_plus_or_exponential': bad, 'dead_hub': dead_hub()}
    Path(sys.argv[1]).write_text(json.dumps(res, indent=1, default=str))
    print('bad:', bad)
    print(json.dumps(res['dead_hub'], default=str)[:1500])
