"""Gate checks for LOOP-CATALOGUE-20261119-001B-E001 (run before the frozen run; output in checks_output.json).

G1  the eddy rule picks exactly the touch census's 13 exponential starts (CLUSTER-ALL's posthoc_dimension.json) of 26,441.
G2  loopweight's W gives the known rates: ring of five with a spare 1.1347 (RING-GROWTH), five five-place knots the golden ratio,
    a ring of five with a lone knot of one spare 1.2032 (JOIN-GROWTH, F_1), ring of seven with a spare the root of x^8 = x + 1.
G3  growth_class on known growths: the bare ring of five (dim1), two touching three-place knots (dim2), the lone knot (closed),
    the ring of five with a spare (exp).
G4  the sampler is reproducible and connected (100 seeds at each of 6, 9, 12 knots).
G5  minimality: the ring of five with one spare is minimal; with two spares it is not; the bare ring of five is no eddy.
G6  graphs8 lists 11,117 connected graphs on eight points (OEIS A001349).
"""
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
import sampler as SM  # noqa: E402
import catalogue as CT  # noqa: E402
import loopweight as LW  # noqa: E402

R5 = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]


def g1():
    exp = {(tuple(r[0][0]), tuple(r[0][1])) for r in json.load(open(
        E.ROOT / 'artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/posthoc_dimension.json'))['exponential']}
    picked, total = set(), 0
    for k in CT.arrlib.arrangements(5):
        total += 1
        sz, flat = k
        e = []
        for (i, j), m in zip(itertools.combinations(range(len(sz)), 2), flat):
            e += [(i, j)] * m
        if E.eddy(list(sz), e) is True:
            picked.add(k)
    return {'arrangements': total, 'picked': len(picked), 'pass': picked == exp and total == 26441}


def rate(sz, e):
    return 1 / LW.root(LW.round_weight(sz, e, 30))


def g2():
    r = {'ring5+spare': rate([5, 4, 4, 4, 4], R5), 'five five-place': rate([5] * 5, R5),
         'ring5+lone(s=1)': rate([5, 5, 5, 4, 4, 4], R5 + [(1, 5)]),
         'ring7+spare': rate([5, 4, 4, 4, 4, 4, 4], [(i, (i + 1) % 7) for i in range(7)])}
    import numpy as np
    want = {'ring5+spare': max(np.roots([1, 0, 0, 0, 0, -1, -1]).real), 'five five-place': (1 + 5 ** 0.5) / 2,
            'ring5+lone(s=1)': 1.2032, 'ring7+spare': max(x.real for x in np.roots([1, 0, 0, 0, 0, 0, 0, -1, -1]) if abs(x.imag) < 1e-9)}
    ok = all(abs(r[k] - want[k]) < (1e-4 if k == 'ring5+lone(s=1)' else 1e-6) for k in r)
    return {'rates': {k: round(v, 6) for k, v in r.items()}, 'want': {k: round(float(v), 6) for k, v in want.items()}, 'pass': ok}


def g3():
    cases = {'bare ring of five': ([4] * 5, R5, 'dim1'), 'two touching knots': ([3, 3], [(0, 1)], 'dim2'),
             'lone knot': ([3], [], 'closed'), 'ring of five with a spare': ([5, 4, 4, 4, 4], R5, 'exp')}
    got = {k: E.growth_class(sz, e, rounds=36, maxj=30000, tmax=60)[0] for k, (sz, e, _) in cases.items()}
    return {'got': got, 'pass': all(got[k].startswith(w) for k, (_, _, w) in cases.items())}


def g4():
    ok = True
    for n in (6, 9, 12):
        for s in range(100):
            a, b = SM.sample(n, s), SM.sample(n, s)
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from(a[1])
            ok &= a == b and nx.is_connected(G) and all(sum(1 for x in a[1] if k in x) <= a[0][k] for k in range(n))
    return {'pass': ok}


def g5():
    a = CT.minimal(5, R5, [1, 0, 0, 0, 0])
    b = CT.minimal(5, R5, [1, 0, 1, 0, 0])
    c = CT.feeds(5, R5, [0] * 5)
    return {'ring5+spare minimal': a, 'ring5+two spares minimal': b, 'bare ring feeds': c, 'pass': a and not b and not c}


def g6():
    n = len(CT.graphs8())
    return {'graphs': n, 'pass': n == 11117}


if __name__ == '__main__':
    res = {'G1': g1(), 'G2': g2(), 'G3': g3(), 'G4': g4(), 'G5': g5(), 'G6': g6()}
    res['all_pass'] = all(v['pass'] for v in res.values() if isinstance(v, dict))
    (HERE / 'checks_output.json').write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v) for k, v in res.items()}))
