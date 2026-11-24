"""Shared helpers of RING-IN-BALANCE-20261123-001B-E001 (ticket B).

Imports ticket A's engine (experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py)
without copying or changing it.  Ticket A's folder is appended to sys.path and only `engine` is imported from it.

Contents: output folder and JSON writing; the census of starts (enumeration, canonical forms, stars); the record of a
run that tickets B1, B2 and B3 share (kind, returns with which members waited, shapes of returning parts, the
ordinary-law checks of gate G).  Readings are those of deviations.md in this folder and ticket A's D1-D22.
"""
from __future__ import annotations

import itertools
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
ENGINE_DIR = os.path.join(ROOT, 'experiments', 'RING-IN-BALANCE-20261123-001A',
                          'RING-IN-BALANCE-20261123-001A-E001_ring')
OUT = os.path.join(ROOT, 'artifacts', 'RING-IN-BALANCE-20261123-001B', 'RING-IN-BALANCE-20261123-001B-E001_reference')
if ENGINE_DIR not in sys.path:
    sys.path.append(ENGINE_DIR)          # appended: nothing of ticket A shadows this folder's modules

import networkx as nx  # noqa: E402
from networkx.generators.atlas import graph_atlas_g  # noqa: E402

import engine as E  # noqa: E402

T0 = time.time()

LAWS3 = (('ordinary', E.ORDINARY), ('two', E.TWO_ADDED), ('three', E.THREE_ADDED))


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def resources():
    return {'seconds': round(time.time() - T0, 1), 'peak_rss_mb': peak_mb()}


def write(name, obj):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    print('wrote', path, resources(), flush=True)
    return path


def load(name):
    with open(os.path.join(OUT, name)) as f:
        return json.load(f)


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


def has_waiting(law):
    """A law with waiting: the treatment CANCEL-WAIT (with or without NO-OFFSHOOT).  deviations.md, B4."""
    return law.treatment == 'CANCEL-WAIT'


# =================================================================================================  the census

_ATLAS = None


def atlas():
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = graph_atlas_g()
    return _ATLAS


def connected_graphs(n):
    """(atlas index, graph) for every connected simple graph on n vertices, one per isomorphism class."""
    return [(i, g) for i, g in enumerate(atlas()) if g.number_of_nodes() == n and nx.is_connected(g)]


def automorphisms(g):
    n = g.number_of_nodes()
    gm = nx.algorithms.isomorphism.GraphMatcher(g, g)
    out = []
    for m in gm.isomorphisms_iter():
        out.append(tuple(m[v] for v in range(n)))
    return out


def canonical_loose(loose, autos):
    """Least loose-count tuple over the automorphisms of the graph (b[sigma(v)] = a[v])."""
    best = None
    n = len(loose)
    for sg in autos:
        b = [0] * n
        for v in range(n):
            b[sg[v]] = loose[v]
        b = tuple(b)
        if best is None or b < best:
            best = b
    return best


_AUTOS = {}


def graph_autos(gi):
    if gi not in _AUTOS:
        _AUTOS[gi] = automorphisms(atlas()[gi])
    return _AUTOS[gi]


def census_starts(n):
    """Every start of the census on n knots, in a fixed order: atlas order of the meeting graph, then the loose-count
    tuple in lexicographic order, each class up to isomorphism once (its least tuple).  Yields dicts."""
    for gi, g in connected_graphs(n):
        deg = [g.degree(v) for v in range(n)]
        autos = graph_autos(gi)
        for loose in itertools.product(range(4), repeat=n):
            if any(deg[v] + loose[v] < 3 for v in range(n)):
                continue
            if not any(loose):
                continue
            if canonical_loose(loose, autos) != loose:
                continue
            yield {'g': gi, 'n': n, 'loose': list(loose)}


def graph_edges(gi):
    g = atlas()[gi]
    return sorted(tuple(sorted(e)) for e in g.edges())


def census_stars(gi, loose):
    """Stars: one shared distinction for each pair that meets (numbered in sorted edge order), then the loose
    distinctions of knot 0, knot 1, ..."""
    edges = graph_edges(gi)
    n = len(loose)
    stars = [[] for _ in range(n)]
    for d, (a, b) in enumerate(edges):
        stars[a].append(d)
        stars[b].append(d)
    nxt = len(edges)
    for v in range(n):
        for _ in range(loose[v]):
            stars[v].append(nxt)
            nxt += 1
    return stars


def is_cycle_graph(gi):
    g = atlas()[gi]
    n = g.number_of_nodes()
    return n >= 3 and g.number_of_edges() == n and all(d == 2 for _, d in g.degree()) and nx.is_connected(g)


# ===========================================================================================  shapes of parts

def part_maxsets(roster, members):
    ms = set(members)
    return [M for M in roster.maxsets if next(iter(M)) in ms]


def is_ring_like(roster, members):
    """A cycle of met pairs: every inclusion-maximal met set of the part has two members, there are as many as members
    (at least three), each member is in two, and they connect the part."""
    msets = part_maxsets(roster, members)
    n = len(members)
    if n < 3 or len(msets) != n or any(len(M) != 2 for M in msets):
        return False
    G = nx.Graph()
    G.add_nodes_from(members)
    for M in msets:
        G.add_edge(*sorted(M))
    return G.number_of_edges() == n and nx.is_connected(G) and all(d == 2 for _, d in G.degree())


def part_shape(roster, members):
    msets = part_maxsets(roster, members)
    return {'n': len(members), 'h': sorted(roster.h[u] for u in members), 'k': sorted(roster.k[u] for u in members),
            'metset_sizes': sorted(len(M) for M in msets), 'ring_like': is_ring_like(roster, members)}


# ========================================================================================  the record of a run

def return_detail(run, r):
    """One return: rounds, parts off, the members of the returned copy and whether each waited in round t; the members
    of Y and whether each was a member also before round s (it waited in round s; None for s = 0)."""
    t, s = r['t'], r['s']
    waiting_t = set(run.records[t - 1]['waiting'])
    copy = list(r['same_part'])
    copy_waited = [u in waiting_t for u in copy]
    if s >= 1:
        waiting_s = set(run.records[s - 1]['waiting'])
        y_waited = [u in waiting_s for u in r['part']]
    else:
        y_waited = None
    shape = part_shape(run.rosters[s], r['part'])
    return {'s': s, 't': t, 'period': r['period'], 'part_size': r['part_size'], 'n_off': r['n_off'],
            'off_sizes': r['off_sizes'], 'copy_members': copy, 'copy_waited': copy_waited,
            'copy_all_waited': all(copy_waited), 'copy_n_waited': sum(copy_waited),
            'y_members': list(r['part']), 'y_waited_in_s': y_waited,
            'y_all_waited_in_s': (all(y_waited) if y_waited is not None else None),
            'ring_like': shape['ring_like'], 'shape': shape}


def size_bucket(z):
    return '1-3' if z <= 3 else '4+'


def run_record(run, keep_all_off=False):
    """The small record of one run (census and B1/B3).  keep_all_off: also list every return giving parts off."""
    rets = run.find_returns()
    off = [r for r in rets if r['n_off'] > 0]
    rec = {'kind': run.kind(), 'first_event': run.first_event(), 'rounds_done': run.rounds_done,
           'cut_off': run.cut_off, 'knots': run.S.n_knots, 'n_returns': len(rets), 'n_off_returns': len(off),
           'mixed_parts': len(getattr(run, 'mixed_parts', []))}
    rec['first_return'] = return_detail(run, rets[0]) if rets else None
    rec['first_off_return'] = return_detail(run, off[0]) if off else None
    if off:
        details = [return_detail(run, r) for r in off]
        agg = {'n': len(details), 'copy_all_waited': sum(d['copy_all_waited'] for d in details),
               'y_all_waited_in_s': sum(1 for d in details if d['y_all_waited_in_s']),
               'sizes': sorted({d['part_size'] for d in details}),
               'ring_like': sum(d['ring_like'] for d in details)}
        by = {}
        for d in details:
            for key in ('size:' + size_bucket(d['part_size']), 'ring_like:' + str(d['ring_like']),
                        'parity_of_s:' + ('even' if d['s'] % 2 == 0 else 'odd')):
                b = by.setdefault(key, {'n': 0, 'copy_all_waited': 0, 'y_all_waited_in_s': 0})
                b['n'] += 1
                b['copy_all_waited'] += int(d['copy_all_waited'])
                b['y_all_waited_in_s'] += int(bool(d['y_all_waited_in_s']))
        agg['by'] = by
        bad = [d for d in details if not d['copy_all_waited']]
        agg['first_not_all_waited'] = bad[0] if bad else None
        smallest = min(details, key=lambda d: (d['part_size'], d['s'], d['t']))
        agg['smallest'] = smallest
        rec['off'] = agg
        if keep_all_off:
            rec['off_all'] = details
    else:
        rec['off'] = None
    return rec


def ordinary_checks(run):
    """Gate G under the ordinary law: no return giving parts off, and no knot a member for two rounds (over the rounds
    that do not stall; a stalled round changes nothing and keeps every member, deviations.md B2)."""
    viol = []
    stalled = 0
    for t in range(1, run.rounds_done + 1):
        if run.records[t - 1]['stalled']:
            stalled += 1
            continue
        both = run.rosters[t - 1].member_set & run.rosters[t].member_set
        if both:
            viol.append({'round': t, 'n': len(both), 'example': sorted(both)[:5]})
    off = [r for r in run.find_returns() if r['n_off'] > 0]
    return {'n_off_returns': len(off), 'member_two_rounds_violations': viol, 'stalled_rounds': stalled,
            'ok': not off and not viol}
