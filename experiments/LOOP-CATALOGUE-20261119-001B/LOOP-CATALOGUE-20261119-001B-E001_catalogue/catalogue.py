"""The catalogue of minimal self-feeding loops (LOOP-CATALOGUE-20261119-001B).

Starts: a connected simple knot graph G (every pair of knots shares at most one distinction) on at most `nmax` knots, from
networkx's atlas of all graphs up to seven points, with each knot given the fewest places that let round 1 start (joinlib's bare
sizes: shared distinctions plus first-round demand, at least three) plus `spares[k]` more.  A start is a **minimal eddy** when the
eddy rule (eddy.py) says it feeds itself, and removing any one spare, or any one knot (its touches gone, the other knots' sizes
re-made bare plus their spares), leaves no piece that feeds itself.  Whether a start feeds itself is the eddy rule's verdict, or
growth's where the rule is unreliable (`verdict`).  Patterns are counted up to renaming (arrlib.canon)."""
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
J = E.J
sys.path.insert(0, str(E.ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib  # noqa: E402


def start(n, edges, spares):
    return [s + x for s, x in zip(J.bare_sizes(n, edges), spares)], list(edges)


def canon(sizes, edges):
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    return arrlib.canon(sizes, M)


def feeds(n, edges, spares):
    if n == 0:
        return False
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    for comp in nx.connected_components(G):
        idx = sorted(comp)
        m = {v: i for i, v in enumerate(idx)}
        e = [(m[a], m[b]) for a, b in edges if a in comp]
        if len(idx) == 1:
            continue
        sz, ee = start(len(idx), e, [spares[v] for v in idx])
        if verdict(sz, ee) is True:
            return True
    return False


_GROWN = {}


def verdict(sz, e):
    """The eddy rule, and growth where the rule is unreliable or the start is outside its scope with a loop (36 rounds, 20,000
    junctions or 60 s; exponential by eddy.growth_class).  Outside the scope with no loop counts as no eddy."""
    v = E.eddy(sz, e)
    if v == 'out' and E.loop_rank_any(sz, e):
        v = 'unreliable'                     # outside the rule's scope, with a loop through distinct blocks: growth decides
    if v != 'unreliable':
        return v
    key = canon(sz, e)
    if key not in _GROWN:
        cls, c = E.growth_class(sz, e, rounds=30, maxj=8000, tmax=30.0)
        _GROWN[key] = (cls, c)
    return _GROWN[key][0].startswith('exp')


def minimal(n, edges, spares):
    if not feeds(n, edges, spares):
        return False
    for k in range(n):
        if spares[k]:
            sp = list(spares)
            sp[k] -= 1
            if feeds(n, edges, sp):
                return False
    for k in range(n):
        keep = [v for v in range(n) if v != k]
        m = {v: i for i, v in enumerate(keep)}
        e = [(m[a], m[b]) for a, b in edges if k not in (a, b)]
        if feeds(n - 1, e, [spares[v] for v in keep]):
            return False
    return True


def graphs(nmax):
    for G in nx.graph_atlas_g():
        n = G.number_of_nodes()
        if 2 <= n <= nmax and nx.is_connected(G):
            yield n, sorted(tuple(sorted(e)) for e in G.edges())


def enumerate_minimal(nmax, max_spares=2):
    seen = {}
    for n, edges in graphs(nmax):
        for tot in range(0, max_spares + 1):
            for where in itertools.combinations_with_replacement(range(n), tot):
                sp = [0] * n
                for w in where:
                    sp[w] += 1
                sz, e = start(n, edges, sp)
                key = canon(sz, e)
                if key in seen:
                    continue
                if minimal(n, edges, sp):
                    seen[key] = {'n': n, 'edges': edges, 'spares': sp, 'sizes': sz}
    return seen


def graphs8():
    """Every connected simple graph on eight points, once: each is a connected seven-point graph plus a point (remove a leaf of a
    spanning tree), deduplicated by Weisfeiler-Lehman hash and an exact isomorphism test."""
    buckets = {}
    out = []
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() != 7 or not nx.is_connected(G):
            continue
        for r in range(1, 8):
            for nb in itertools.combinations(range(7), r):
                H = G.copy()
                H.add_node(7)
                H.add_edges_from((7, v) for v in nb)
                h = nx.weisfeiler_lehman_graph_hash(H, iterations=4)
                lst = buckets.setdefault(h, [])
                if any(nx.is_isomorphic(H, K) for K in lst):
                    continue
                lst.append(H)
                out.append((8, sorted(tuple(sorted(e)) for e in H.edges())))
    return out


def enumerate_minimal_graphs(gs, max_spares=2):
    seen = {}
    for n, edges in gs:
        for tot in range(0, max_spares + 1):
            for where in itertools.combinations_with_replacement(range(n), tot):
                sp = [0] * n
                for w in where:
                    sp[w] += 1
                sz, e = start(n, edges, sp)
                if verdict(sz, e) is not True:
                    continue
                key = canon(sz, e)
                if key in seen:
                    continue
                if minimal(n, edges, sp):
                    seen[key] = {'n': n, 'edges': edges, 'spares': sp, 'sizes': sz}
    return seen


def rule_verdict(sz, e):
    """The rule alone: True, False, or None (growth needed: unreliable, or outside the scope with a loop)."""
    v = E.eddy(sz, e)
    if v == 'out':
        return None if E.loop_rank_any(sz, e) else False
    if v == 'unreliable':
        return None
    return v is True


def reductions(n, edges, spares):
    """Each single reduction as a list of its pieces (n, edges, spares) with two or more knots."""
    out = []
    for k in range(n):
        if spares[k]:
            sp = list(spares)
            sp[k] -= 1
            out.append([(n, edges, sp)])
    for k in range(n):
        keep = [v for v in range(n) if v != k]
        m = {v: i for i, v in enumerate(keep)}
        e = [(m[a], m[b]) for a, b in edges if k not in (a, b)]
        G = nx.Graph()
        G.add_nodes_from(range(n - 1))
        G.add_edges_from(e)
        parts = []
        for comp in nx.connected_components(G):
            idx = sorted(comp)
            if len(idx) < 2:
                continue
            mm = {v: i for i, v in enumerate(idx)}
            parts.append((len(idx), [(mm[a], mm[b]) for a, b in e if a in comp], [spares[keep[v]] for v in idx]))
        out.append(parts)
    return out


def enumerate_minimal_lazy(gs, max_spares=2, log=None, grow=True):
    """Minimal eddies among the graphs gs: the rule decides where it is reliable; growth only for a start, or a reduction, whose
    status the rule cannot give and that could still be minimal (no reduction already a known eddy).  With grow=False the rule
    alone decides, and the starts it cannot decide are counted in `undecided` instead of grown."""
    seen, grown = {}, 0
    undecided = {}

    def status(n, edges, sp):
        nonlocal grown
        sz, e = start(n, edges, sp)
        v = rule_verdict(sz, e)
        if v is None and not grow:
            undecided.setdefault(canon(sz, e), {'n': n, 'edges': [list(x) for x in edges], 'spares': list(sp), 'sizes': sz})
            return False
        if v is None:
            key = canon(sz, e)
            if key not in _GROWN:
                grown += 1
            v = verdict(sz, e)
        return v
    for gi, (n, edges) in enumerate(gs):
        for tot in range(0, max_spares + 1):
            for where in itertools.combinations_with_replacement(range(n), tot):
                sp = [0] * n
                for w in where:
                    sp[w] += 1
                sz, e = start(n, edges, sp)
                v = rule_verdict(sz, e)
                if v is False:
                    continue
                reds = reductions(n, edges, sp)
                # cheap first: a reduction the rule already calls an eddy rules the start out
                if any(any(rule_verdict(*start(*p)) is True for p in parts) for parts in reds):
                    continue
                if v is None and status(n, edges, sp) is not True:
                    continue
                if v is None and not grow:
                    continue
                if any(any(status(*p) is True for p in parts) for parts in reds):
                    continue
                key = canon(sz, e)
                if key not in seen:
                    seen[key] = {'n': n, 'edges': edges, 'spares': sp, 'sizes': sz, 'by': 'rule' if v else 'growth'}
        if log and gi % 1000 == 0:
            log(f'{gi} graphs, {len(seen)} minimal, {grown} grown, {len(undecided)} undecided')
    seen['_undecided'] = list(undecided.values())
    return seen
