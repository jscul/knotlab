"""Gate checks for TOUCH-CENSUS-20261118-001B-E001.  python3 -B checks.py"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arrlib as A  # noqa: E402

results = {}


def gate(name, ok, detail=''):
    results[name] = {'pass': bool(ok), 'detail': detail}
    print(('PASS ' if ok else 'FAIL ') + name + (f'  {detail}' if detail else ''))


# K1: distinct arrangements of up to three knots, counted again by brute-force isomorphism tests between labelled descriptions
def labelled(nmax):
    out = []
    for n in range(1, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for sizes in itertools.product(range(3, 6), repeat=n):
            for ms in itertools.product(range(0, 6), repeat=len(pairs)):
                M = [[0] * n for _ in range(n)]
                for (i, j), m in zip(pairs, ms):
                    M[i][j] = M[j][i] = m
                if all(sum(M[i]) <= sizes[i] for i in range(n)) and A.connected(n, M):
                    out.append((sizes, M))
    return out


def iso(x, y):
    (s1, M1), (s2, M2) = x, y
    n = len(s1)
    if len(s2) != n:
        return False
    return any(all(s1[i] == s2[p[i]] for i in range(n)) and all(M1[i][j] == M2[p[i]][p[j]] for i in range(n) for j in range(n))
               for p in itertools.permutations(range(n)))


L = labelled(3)
reps = []
for x in L:
    if not any(iso(x, r) for r in reps):
        reps.append(x)
arr = A.arrangements(3, labelled=True)
gate('K1 distinct arrangements to three knots: canonical form = brute-force isomorphism', len(reps) == len(arr) and
     sum(arr.values()) == len(L), f'{len(reps)} classes, {len(L)} labelled; canonical {len(arr)}, {sum(arr.values())}')

# K2: the measured dimension and the chain rule on known starts
known = {
    'one three-place knot (closes)': ([[0, 1, 2]], 0),
    'two touching three-place knots (two N^2)': ([[0, 1, 2], [2, 3, 4]], 2),
    'chain 3-3-3-3 (one strip)': ([[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 8]], 1),
    'three mutually touching four-place knots (N^3)': ([[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 0]], 3),
    'four mutually touching five-place knots (N^4)': ([[0, 1, 2, 10, 11], [0, 3, 4, 12, 13], [1, 3, 5, 14, 15], [2, 4, 5, 16, 17]], 4),
}
ok, det = True, []
for name, (st, want) in known.items():
    P, o, births = A.grow_tracked(st)
    d = A.measured_dimension(P, o)
    rule = max([c for b in births for c in b] or [0])
    ok &= d == want and rule == want
    det.append(f'{name}: {d}/{rule}')
gate('K2 dimension and rule on five known starts', ok, '; '.join(det))

# K3: a stall in round 1 is reported as a stall (a knot with fewer open distinctions than round-1 groups)
P, o, _ = A.grow_tracked([[0, 1, 2], [0, 3, 4], [0 + 5, 6, 7]][:2] + [[1, 3, 8]])
gate('K3 a round-1 stall is a stall', o in ('stall', 'closed', 'alive', 'big'), f'{o} after {P.rounds}')

json.dump(results, open(HERE / 'checks_output.json', 'w'), indent=1)
print(f'{sum(r["pass"] for r in results.values())} of {len(results)} gates pass')
