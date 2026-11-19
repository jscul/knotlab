"""Shared-runner job for CENSUS-READ-20261118-001A-E001, Amendment 5 (pass 5): the whole census again with the two instrument
faults fixed (exact_table_v2: closed stages; reader3n_v2: dependent candidates kept) and a test of the table's symmetries.

Stages: every arrangement, every stage of at most 40 junctions; stages of 41 to 120 junctions for every 10th arrangement in
sorted order (index divisible by 10).  Per stage: R3 (census naming) and R3n (version 2), one seeded renaming each, and their
horizons where exact (R1 and R3m are not rerun: pass 3 scored them on 1,925 arrangements); and the symmetry test:
- twins (stages of at most 40 junctions): two distinctions in different junctions with the same distance to every other distinction (their exchange is a table
  symmetry that moves a junction);
- at stages of at most 10 junctions, a search of the table's symmetries (VF2 on the complete graph of distinctions labelled by
  distance, at most 20,000 of them) for one that moves the junction set: 'moves', 'fixes' (all enumerated, none moves), or
  'unknown' (limit reached, none found).
"""
import json
import random
import sys
import zlib
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import exact_table_v2 as X  # noqa: E402
import reader3n_v2 as N  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A
SHARD = 10
SMALL = 40
EVERY = 10
SYM_JUNCTIONS = 10
SYM_LIMIT = 20000
RENAMINGS = 1


def setup(params):
    job.setup(params)


def cases():
    data = job._ARR
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:05d}', {'part': 'census', 'lo': s, 'hi': min(len(data), s + SHARD)}
    for s in range(60):
        yield f'mixed-{s:02d}', {'part': 'mixed', 'seed': 700000 + s}


def renamed(reader, table, perm, top):
    t = {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}
    inv = {v: k for k, v in perm.items()}
    return {frozenset(inv[x] for x in s) for s in reader(t, top)}


def horizons(reader, table, truth, K, H):
    by_h = {}
    for h in range(H - 1, 0, -1):
        by_h[h] = reader(R.pooled(table, h), h + 1) == truth
        if not by_h[h] and h <= K - 2:
            break
    least = None
    for h in range(H - 1, 0, -1):
        if by_h.get(h):
            least = h
        else:
            break
    return least, {str(h): v for h, v in by_h.items()}


def symmetry(stars, table):
    labels = sorted(R.owners(stars))
    holder = {}
    for j, s in enumerate(stars):
        for b in s:
            holder.setdefault(b, set()).add(j)
    row = {x: tuple(table[tuple(sorted((x, z)))] for z in labels if z != x) for x in labels}
    twins = False
    for x, y in combinations(labels, 2):
        if holder[x] != holder[y]:
            rx = tuple(table[tuple(sorted((x, z)))] for z in labels if z not in (x, y))
            ry = tuple(table[tuple(sorted((y, z)))] for z in labels if z not in (x, y))
            if rx == ry:
                twins = True
                break
    out = {'twins_across_junctions': twins}
    if len(stars) > SYM_JUNCTIONS:
        out['search'] = 'not_checked'
        return out
    if twins:
        out['search'] = 'moves'
        return out
    G = nx.Graph()
    G.add_nodes_from(labels)
    for (a, b), d in table.items():
        G.add_edge(a, b, d=d)
    for x in labels:
        G.nodes[x]['row'] = tuple(sorted(row[x]))
    gm = isomorphism.GraphMatcher(G, G, node_match=lambda u, v: u['row'] == v['row'],
                                  edge_match=lambda u, v: u['d'] == v['d'])
    truth = {frozenset(s) for s in stars}
    count = 0
    for sigma in gm.isomorphisms_iter():
        count += 1
        if {frozenset(sigma[b] for b in s) for s in truth} != truth:
            out['search'] = 'moves'
            out['automorphisms_seen'] = count
            return out
        if count >= SYM_LIMIT:
            out['search'] = 'unknown'
            out['automorphisms_seen'] = count
            return out
    out['search'] = 'fixes'
    out['automorphisms_seen'] = count
    return out


def read_stage(stars, seed, fresh_reader=None):
    stars = [frozenset(s) for s in stars]
    truth = set(stars)
    own = R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    n = len(stars)
    K = max(map(len, stars))
    H = K + 2
    table = X.exact_table(stars, H)
    shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
    out = {'junctions': n, 'distinctions': len(own), 'largest': K, 'loose': len(loose),
           'max_shared': max(shared.values()) if shared else 0, 'connectivity': job.connectivity(stars),
           'min_distance': min(table.values()) if table else None}
    flags = Counter()
    readers = [('r3', R3.r3), ('r3n', lambda t, top: N.r3n(t, top, flags))]
    for name, reader in readers:
        got = reader(table, H + 1)
        out[name] = job.verdict(got, truth, loose)
        if out[name] != 'exact':
            out[name + '_missed'] = len(truth - got)
            out[name + '_extra'] = len(got - truth)
    out['r3n_flags'] = dict(flags)
    if fresh_reader is not None:
        out['fresh_reader'] = fresh_reader(stars)
    labels = sorted(own)
    rng = random.Random(seed)
    perms = []
    for _ in range(RENAMINGS):
        img = list(labels)
        rng.shuffle(img)
        perms.append(dict(zip(labels, img)))
    out['r3_renamed'] = [job.verdict(renamed(R3.r3, table, p, H + 1), truth, loose) for p in perms]
    out['r3n_renamed'] = [job.verdict(renamed(N.r3n, table, p, H + 1), truth, loose) for p in perms]
    for name, reader in (('r3', R3.r3), ('r3n', N.r3n)):
        if out[name] == 'exact':
            least, by_h = horizons(reader, table, truth, K, H)
            out[name + '_least_horizon'] = least
            out[name + '_by_horizon'] = by_h
    out['symmetry'] = symmetry(stars, table) if n <= SMALL else {'search': 'not_checked'}
    return out


def census_stages(i):
    key = job._ARR[i]
    sampled = i % EVERY == 0
    P = S.from_junctions(A.stars_of(key))
    stages, outcome = [], 'alive'
    tag = json.dumps([list(key[0]), list(key[1])])
    for r in range(job.RMAX + 1):
        n = len(P.bits_of)
        if n > job.JCAP:
            outcome = 'cap'
            break
        if n > SMALL and not sampled:
            outcome = 'not_sampled_beyond_40'
            break
        st = read_stage(P.bits_of, zlib.crc32(f'{tag}/{r}'.encode()))
        st['round'] = r
        stages.append(st)
        if r == job.RMAX:
            break
        res = P.step(S.gf2(F.fewest), None)
        if res is None:
            outcome = 'stall'
            break
        if res['new'] == 0:
            outcome = 'closed'
            break
    return {'key': [list(key[0]), list(key[1])], 'index': i, 'knots': len(key[0]), 'outcome': outcome,
            'sampled_beyond_40': sampled, 'stages': stages}


def mixed_stages(seed):
    rng = random.Random(seed)
    a = rng.choice([3, 4])
    q = rng.choice([0.1, 0.2, 0.4])
    P = F.Presentation(a)
    stages = []
    for _ in range(6):
        if len(P.bits_of) > 16:
            break
        st = read_stage(P.bits_of, zlib.crc32(f'mixed/{seed}/{P.rounds}'.encode()), job.fresh_reader())
        st['round'] = P.rounds
        stages.append(st)
        s = P.step(F.surplus(q), None, rng)
        if s is None or s['new'] == 0:
            break
    return {'seed': seed, 'a': a, 'q': q, 'stages': stages}


def run(case_id, p):
    if p['part'] == 'mixed':
        return mixed_stages(p['seed'])
    return {'arrangements': [census_stages(i) for i in range(p['lo'], p['hi'])]}
