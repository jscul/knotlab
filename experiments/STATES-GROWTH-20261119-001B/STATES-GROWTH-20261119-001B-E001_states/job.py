"""Shared-runner job for STATES-GROWTH-20261119-001B-E001: a growth that reads only the allowed states (challenging A108).

The states-only growth (the advisor's rank 1): at each stage compute M, the minimal not-all-equal constraints the allowed states
satisfy (statelib.nae_core, up to one place more than the largest junction); if M is an admissible presentation, grow one round of
the cheapest growth on M; otherwise it is undefined.  Each stage's verdict: saturated (M is the presentation), sharpened (M differs
but is admissible), undefined.
Part A: replays: the advisor's six-distinction example (the stars and the triangles of the literature's K4) and the duplicate pair.
Part B: the verdict of every stage of NAE-GROWTH's part B (2,715 stages, up to 15 distinctions), with its redundancy.
Part C: trajectories from the census arrangements of one to four knots: the states-only growth and the cheapest growth under
not-all-equal (naelib) side by side while the stage has at most 18 distinctions, up to 6 rounds.
Part D: parity's same-state pairs among the same stages: is each pair's completed system (the presentation plus the implied
junction holding every loose distinction) the same graph up to renaming, and where not, is it below three-connected?"""
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import statelib as SL  # noqa: E402
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'))
import bondlib as B  # noqa: E402
import naelib as N  # noqa: E402
J = N.J
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

BMAX, CROUNDS = 18, 6


def core_of(stars, n=None):
    n = n or 1 + max(b for s in stars for b in s)
    st = B.states(n, stars, 'nae')
    return st, SL.nae_core(n, st, kmax=max(len(x) for x in stars) + 1)


def part_a():
    e = {p: i for i, p in enumerate(itertools.combinations(range(4), 2))}
    stars = [sorted(e[tuple(sorted((v, w)))] for w in range(4) if w != v) for v in range(4)]
    tris = [sorted(e[p] for p in itertools.combinations(t, 2)) for t in itertools.combinations(range(4), 3)]
    s1, M = core_of(stars, 6)
    s2 = B.states(6, tris, 'nae')
    reps = []
    for sub in itertools.combinations(M, 4):
        held = {}
        for S in sub:
            for b in S:
                held[b] = held.get(b, 0) + 1
        if max(held.values()) > 2 or len(held) < 6:
            continue
        if sorted(B.states(6, [list(x) for x in sub], 'nae').tolist()) == sorted(s1.tolist()):
            irr = all(len(B.states(6, [list(x) for x in sub if x != y], 'nae')) != len(s1) for y in sub)
            if irr:
                reps.append(sorted(sub))
    dup_st, dup_core = core_of([[0, 1, 2], [0, 1, 2]], 3)
    return {'states_stars': len(s1), 'states_triangles': len(s2), 'same_states': sorted(s1.tolist()) == sorted(s2.tolist()),
            'minimal_constraints': len(M), 'admissible_irredundant_presentations': len(reps), 'duplicate_pair_minimal': len(dup_core)}


def b_stages():
    R = load_results(str(ROOT / 'runs/nae-growth'))
    for c, r in sorted(R.items()):
        if c.startswith('B-'):
            for a in r['result']['arrangements']:
                for s in a['stages']:
                    yield a['key'], s


def part_b(lo, hi):
    out = []
    for i, (key, s) in enumerate(b_stages()):
        if not lo <= i < hi:
            continue
        st, M = core_of(s['stars'], s['bits'])
        out.append({'i': i, 'key': key, 'round': s['round'], 'verdict': SL.verdict(s['stars'], M),
                    'redundant': s['nae']['redundant'], 'core_size': len(M), 'junctions': len(s['stars'])})
    return {'stages': out}


def step(stars):
    P = N.S.from_junctions([list(x) for x in stars])
    P.linalg = False
    r = P.step(N.nae_rule(N.F.fewest), None)                 # the cheapest growth under not-all-equal (naelib)
    if r is None:
        return None, 'stall'
    if r['new'] == 0:
        return None, 'closed'
    return [list(x) for x in P.bits_of], r['new']


def renumber(stars):
    bits = sorted({b for s in stars for b in s})
    m = {b: i for i, b in enumerate(bits)}
    return [sorted(m[b] for b in s) for s in stars]


def part_c(keys):
    out = []
    for a, b in keys:
        sizes, flat = a, b
        e = []
        for (i, j), mlt in zip(itertools.combinations(range(len(sizes)), 2), flat):
            e += [(i, j)] * mlt
        stars = J.stars_from(list(sizes), e)
        cheap, states_only, verdicts, agree = stars, stars, [], []
        for t in range(CROUNDS):
            n = 1 + max(x for s in states_only for x in s)
            if n > BMAX:
                break
            _, M = core_of(states_only, n)
            v = SL.verdict(states_only, M)
            verdicts.append(v)
            if v == 'undefined':
                break
            nxt_s, ns = step(renumber(M) if v != 'saturated' else states_only)
            nxt_c, nc = step(cheap)
            agree.append(ns == nc)
            if nxt_s is None or nxt_c is None:
                verdicts.append(f'end: {ns} / {nc}')
                break
            states_only, cheap = nxt_s, nxt_c
        out.append({'key': [a, b], 'verdicts': verdicts, 'agree': agree})
    return {'trajectories': out}


def part_d():
    spec = importlib.util.spec_from_file_location('ng_merge', ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/merge.py')
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    st = [dict(s, key=k) for k, s in b_stages()]
    reps = M.distinct(st)
    found = M.collisions(st, reps, 'parity')
    rows = []
    for i, k in found:
        if M.same_states(st[i], st[k], 'parity') is not True:
            continue
        ga, gb = completed(st[i]['stars']), completed(st[k]['stars'])
        iso = nx.is_isomorphic(ga, gb)
        rows.append({'iso': iso, 'three_connected_a': three_connected(ga), 'three_connected_b': three_connected(gb)})
    return {'pairs': rows}


def completed(stars):
    """The completed system as a multigraph: junctions and one implied junction ('out') as points, distinctions as lines."""
    own = {}
    for j, s in enumerate(stars):
        for b in s:
            own.setdefault(b, []).append(j)
    G = nx.MultiGraph()
    G.add_nodes_from(list(range(len(stars))) + ['out'])
    for b, js in own.items():
        G.add_edge(js[0], js[1] if len(js) == 2 else 'out')
    return G


def three_connected(G):
    H = nx.Graph(G)
    if H.number_of_nodes() < 4:
        return False
    return nx.node_connectivity(H) >= 3


def cases():
    yield 'A', {'part': 'A'}
    for lo in range(0, 2800, 200):
        yield f'B-{lo // 200:02d}', {'part': 'B', 'lo': lo, 'hi': lo + 200}
    sys.path.insert(0, str(ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
    import arrlib
    keys = sorted(k for k in arrlib.arrangements(4))
    for s in range(0, len(keys), 100):
        yield f'C-{s // 100:02d}', {'part': 'C', 'keys': [[list(a), list(b)] for a, b in keys[s:s + 100]]}
    yield 'D', {'part': 'D'}


def run(case_id, payload):
    p = payload['part']
    if p == 'A':
        return part_a()
    if p == 'B':
        return part_b(payload['lo'], payload['hi'])
    if p == 'C':
        return part_c(payload['keys'])
    return part_d()
