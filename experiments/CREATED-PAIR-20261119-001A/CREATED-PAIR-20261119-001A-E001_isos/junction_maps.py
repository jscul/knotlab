"""CREATED-PAIR-20261119-001A, after the run: which junctions every full-table isometry of the created pair exchanges.
Run: .venv/bin/python -B junction_maps.py -> junction_maps.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'))
import plib as L  # noqa: E402
# GROW-SMALL's created pair: round 1 from atlas 448 (loose 1121212) and atlas 581 (loose 0212121); junctions 0-6 are the starts
A = [[0, 1, 8], [0, 2, 3, 9], [2, 4, 10, 11], [4, 5, 12], [5, 6, 13, 14], [1, 6, 7, 15], [3, 7, 16, 17], [8, 10, 13, 16, 18, 19, 20],
     [9, 12, 15, 21], [11, 22, 23], [14, 24, 25], [17, 26, 27]]
B = [[0, 1, 2], [0, 3, 9, 10], [3, 4, 5, 11], [4, 6, 12, 13], [6, 7, 8, 14], [1, 7, 15, 16], [2, 5, 8, 17], [9, 12, 15, 17, 18, 19, 20],
     [11, 14, 21], [10, 22, 23], [13, 24, 25], [16, 26, 27]]


def main():
    a, b = [frozenset(s) for s in A], [frozenset(s) for s in B]
    ta, la = L.table(a)
    tb, lb = L.table(b)
    m = isomorphism.GraphMatcher(L.coloured(ta, la), L.coloured(tb, lb), node_match=lambda x, y: x['k'] == y['k'],
                                 edge_match=lambda x, y: x['d'] == y['d'])
    maps, starts = Counter(), Counter()
    idx = {s: j for j, s in enumerate(b)}
    for phi in m.isomorphisms_iter():
        jm = tuple(idx.get(frozenset(phi[x] for x in s)) for s in a)
        maps[jm] += 1
        starts[sum(1 for j in range(7) if jm[j] is not None and jm[j] < 7)] += 1
    out = {'junction_maps_A_to_B': [{'map': list(k), 'isometries': v} for k, v in maps.items()],
           'start_knots_of_A_onto_start_knots_of_B': dict(starts)}
    dest = ROOT / 'artifacts/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos'
    (dest / 'junction_maps.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out))


if __name__ == '__main__':
    main()
