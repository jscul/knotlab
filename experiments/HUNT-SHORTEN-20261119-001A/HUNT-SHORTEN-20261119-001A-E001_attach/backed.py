"""HUNT-SHORTEN-20261119-001A, after the read-out (exploratory, not frozen): Part 1 split by whether the attachment is one the law
could make.  The law joins two or three live junctions only when every two of them are met by a common junction (candidates;
PARENT-RULE's backed pairs).  For each Part 1 attachment with |S| >= 2: is S backed on side a (every two members have a common
neighbour other than themselves)?  Do failures occur among backed attachments?
Run: .venv/bin/python -B backed.py -> backed.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import attach as H  # noqa: E402
L, EX = H.L, H.EX


def backed(stars, S):
    nb = L.neighbours(stars)
    return all((nb[u] & nb[v]) - {u, v} for u, v in combinations(S, 2))


def one(item):
    kind, A, B, meta = item
    a = [frozenset(s) for s in A]
    b = [frozenset(s) for s in B]
    c = Counter()
    ta, la = L.table(a)
    tb, lb = L.table(b)
    m = isomorphism.GraphMatcher(L.coloured(ta, la), L.coloured(tb, lb), node_match=lambda x, y: x['k'] == y['k'],
                                 edge_match=lambda x, y: x['d'] == y['d'])
    cache = {}
    n = 0
    for phi in m.isomorphisms_iter():
        n += 1
        if n > H.CAP_ISO:
            break
        for S, f in H.attachments(a, b, phi):
            if len(S) < 2:
                continue
            us = [u for u, _, _ in S]
            vs = [v for _, v, _ in S]
            ba, bb = backed(a, us), backed(b, vs)
            a1, fa = H.attach(a, [x for _, _, x in S], f)
            b1, fb = H.attach(b, [phi[x] for _, _, x in S], f)
            for k, arr in ((frozenset(a1), a1), (frozenset(b1), b1)):
                if k not in cache:
                    cache[k] = L.table(arr)
            (ta1, _), (tb1, _) = cache[frozenset(a1)], cache[frozenset(b1)]
            phi1 = dict(phi)
            phi1.update(dict(zip(fa, fb)))
            ok = all(ta1[(x, y)] == tb1[tuple(sorted((phi1[x], phi1[y])))] for (x, y) in ta1)
            key = 'backed both' if ba and bb else ('backed one side' if ba or bb else 'backed neither')
            c[f'{key}: tested'] += 1
            c[f'{key}: fails'] += not ok
    return dict(c)


def main():
    its = [x for x in EX.items() if x[0] == 'static']
    with Pool(8) as pool:
        rs = pool.map(one, its, chunksize=2)
    s = Counter()
    for r in rs:
        s.update(r)
    dest = ROOT / 'artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach'
    (dest / 'backed.json').write_text(json.dumps(dict(sorted(s.items())), indent=1))
    print(json.dumps(dict(sorted(s.items())), indent=1))


if __name__ == '__main__':
    main()
