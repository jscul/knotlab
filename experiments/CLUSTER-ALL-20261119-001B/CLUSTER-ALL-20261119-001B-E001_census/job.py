"""Shared-runner job for CLUSTER-ALL-20261119-001B-E001: the extended cluster rule (clusters.py) against regrown growths.

T1: every five-knot arrangement of the touch census (arrlib, 24,502), in shards of 50.  T3: 2,000 random connected six-knot
arrangements (sizes 3 to 5 uniform, 5 to 12 shared distinctions added at random while places allow, as PLUS-ONE-20261118-001B's
sampler, seeds 70000 to 71999), in shards of 50.  Each arrangement is grown under the fewest counts to 20 rounds, 20,000
junctions or 120 seconds and compared, round by round, with the rule.  (T2, JOIN-GROWTH's recorded starts, is scored in merge.py as a
consistency check: the chain and relay clauses came from that line.)  T4: the advisor's falsifiers, hand-built (scored like T1).
T5: every 100th in-scope five-knot arrangement that the rule says does not stall, by sorted key, regrown to 45 rounds (the
horizon check)."""
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clusters as Cl  # noqa: E402
J = Cl.J
sys.path.insert(0, str(Cl.ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib  # noqa: E402

ROUNDS, MAXJ, TMAX = 20, 20000, 120.0


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def six(seed):
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(6)]
        deg = [0] * 6
        M = [[0] * 6 for _ in range(6)]
        pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
        for _ in range(rng.randint(5, 12)):
            i, j = rng.choice(pairs)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                M[i][j] += 1
                M[j][i] += 1
                deg[i] += 1
                deg[j] += 1
        if arrlib.connected(6, M):
            return arrlib.canon(sizes, M)


def with_sizes(edges, n, extra):
    """Sizes = shared + extra[k] for each knot."""
    sh = [0] * n
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
    return [sh[k] + extra[k] for k in range(n)], edges


def falsifiers():
    R = J.ring_edges
    F = {}
    F['T4-two-triangles-one-knot'] = with_sizes([(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (2, 4)], 5, [2, 2, 2, 2, 2])
    F['T4-two-triangles-two-knots'] = with_sizes([(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)], 4, [2, 2, 2, 2])
    F['T4-ring6'] = ([4] * 6, R(6))
    e = R(5) + [(2, 5)]
    F['T4-ring5-unequal-pendant'] = (J.bare_sizes(6, e, {'1': 1, '2': 2, '5': 1}), e)
    e = [(0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (1, 5)]
    for extra in (0, 1):
        F[f'T4-overlap-simplices-b{extra}'] = (J.bare_sizes(6, e, {'3': extra}), e)
    F['T4-two-pieces-relays'] = ([4, 6], [(0, 1)])
    F['T4-triangle-single'] = with_sizes([(0, 1), (1, 2), (0, 2)], 3, [2, 2, 2])
    F['T4-triangle-double'] = with_sizes([(0, 1), (0, 1), (1, 2), (1, 2), (0, 2), (0, 2)], 3, [2, 2, 2])
    F['T4-triangle-pendant-knot'] = with_sizes([(0, 1), (1, 2), (0, 2), (2, 3)], 4, [2, 2, 2, 3])
    e = R(7) + [(1, 7), (4, 8)]
    F['T4-ring7-two-lone'] = (J.bare_sizes(9, e), e)
    F['T4-three-touching-five'] = with_sizes([(0, 1), (1, 2), (0, 2)], 3, [3, 3, 3])
    return F


def cases():
    five = sorted(k for k in arrlib.arrangements(5) if len(k[0]) == 5)
    for s in range(0, len(five), 50):
        yield f'T1-{s // 50:04d}', {'keys': [[list(a), list(b)] for a, b in five[s:s + 50]]}
    seeds = list(range(70000, 72000))
    for s in range(0, len(seeds), 50):
        yield f'T3-{s // 50:04d}', {'seeds': seeds[s:s + 50]}
    for cid, (sz, e) in falsifiers().items():
        yield cid, {'start': [sz, [list(x) for x in e]]}
    live = []
    for k in five:
        a = Cl.analyse(*edges_of(k))
        if a['scope'] and not a['stall']:
            live.append(k)
    pick = live[::100]
    for s in range(0, len(pick), 10):
        yield f'T5-{s // 10:04d}', {'keys': [[list(a), list(b)] for a, b in pick[s:s + 10]], 'rounds': 45}


def judge(sizes, e, rounds=ROUNDS):
    pred = Cl.series(sizes, e, rounds + 1)
    g = J.grow(sizes, e, rounds=rounds, maxj=MAXJ if rounds == ROUNDS else 200000, tmax=TMAX if rounds == ROUNDS else 600.0)
    c, out = g['counts'], g['outcome']
    if pred is None:
        v = 'out of scope'
    elif pred == 'stall':
        v = 'match' if out == 'stall' else 'miss'
    elif out == 'stall':
        v = 'miss'
    else:
        v = 'match' if pred[:len(c)] == c and (out != 'closed' or not any(pred[len(c):len(c) + 3])) else 'miss'
    fd = None
    if v == 'miss' and isinstance(pred, list):
        fd = next((t for t in range(min(len(c), len(pred))) if pred[t] != c[t]), len(c))
    return {'verdict': v, 'outcome': out, 'rounds': g['rounds'], 'counts': c, 'first_difference': fd,
            'why': Cl.analyse(sizes, e).get('why') if pred is None else None}


def run(case_id, payload):
    out = []
    if 'start' in payload:
        sz, e = payload['start']
        out.append(dict(judge(sz, [tuple(x) for x in e]), key=case_id))
    elif 'keys' in payload:
        for a, b in payload['keys']:
            key = (tuple(a), tuple(b))
            out.append(dict(judge(*edges_of(key), rounds=payload.get('rounds', ROUNDS)), key=[list(a), list(b)]))
    else:
        for sd in payload['seeds']:
            key = six(sd)
            out.append(dict(judge(*edges_of(key)), key=[list(key[0]), list(key[1])], seed=sd))
    return {'arrangements': out}
