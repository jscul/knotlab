"""Enumerate the starts of the census (B2) and check the registered counts: 19, 200, 3,157 and 82,656 starts on 3 to 6
knots (86,032 in all), of which 0, 59, 1,564 and 54,148 have a dead knot (55,771 in all).  Two independent checks:
for n = 3, 4 a brute-force canonical form over all n! relabellings of every labelled connected graph; for every n the
number of classes on each atlas graph by Burnside's lemma (the mean number of admissible loose tuples fixed by an
automorphism), compared with the number listed (the atlas lists each graph once).  Writes census_count.json."""
import itertools
from collections import Counter

import networkx as nx

from bref import census_starts, connected_graphs, graph_autos, graph_edges, log, resources, write

EXPECTED = {3: (19, 0), 4: (200, 59), 5: (3157, 1564), 6: (82656, 54148)}


def brute_canon(n, edges, loose):
    """Canonical form of a coloured graph over all n! relabellings: least (sorted edge list, loose tuple)."""
    best = None
    for perm in itertools.permutations(range(n)):
        e = tuple(sorted(tuple(sorted((perm[a], perm[b]))) for a, b in edges))
        lo = [0] * n
        for v in range(n):
            lo[perm[v]] = loose[v]
        key = (e, tuple(lo))
        if best is None or key < best:
            best = key
    return best


def brute_count(n):
    """All labelled connected graphs on n vertices with all loose assignments, reduced by the brute canonical form."""
    pairs = list(itertools.combinations(range(n), 2))
    seen = set()
    for mask in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        if not nx.is_connected(g):
            continue
        deg = [g.degree(v) for v in range(n)]
        for loose in itertools.product(range(4), repeat=n):
            if any(deg[v] + loose[v] < 3 for v in range(n)) or not any(loose):
                continue
            seen.add(brute_canon(n, edges, loose))
    return seen


def burnside(n):
    """Classes of admissible loose tuples per atlas graph by Burnside's lemma; returns (total, with a dead knot)."""
    tot = dead_tot = 0
    for gi, g in connected_graphs(n):
        deg = [g.degree(v) for v in range(n)]
        autos = graph_autos(gi)
        fix_all = fix_live = 0          # fixed tuples (all admissible) and fixed tuples with no dead knot
        for sg in autos:
            # cycles of the permutation; a fixed tuple is constant on each cycle
            seen, cycles = set(), []
            for v in range(n):
                if v in seen:
                    continue
                c, x = [], v
                while x not in seen:
                    seen.add(x)
                    c.append(x)
                    x = sg[x]
                cycles.append(c)
            # automorphisms preserve degree, so each cycle has one degree; count constant choices per cycle
            choices_any = [[a for a in range(4) if deg[c[0]] + a >= 3] for c in cycles]
            n_any = 1
            n_pos = 1
            for ch in choices_any:
                n_any *= len(ch)
                n_pos *= len([a for a in ch if a >= 1])
            zero_ok = all(0 in ch for ch in choices_any)   # the all-zero tuple (excluded: no live knot)
            fix_all += n_any - (1 if zero_ok else 0)
            fix_live += n_pos
        assert fix_all % len(autos) == 0 and fix_live % len(autos) == 0
        tot += fix_all // len(autos)
        dead_tot += (fix_all - fix_live) // len(autos)
    return tot, dead_tot


def main():
    out = {'by_n': {}, 'ok': True}
    total = dead_total = 0
    for n in (3, 4, 5, 6):
        starts = list(census_starts(n))
        dead = sum(1 for s in starts if 0 in s['loose'])
        ng = len(connected_graphs(n))
        row = {'graphs': ng, 'starts': len(starts), 'with_dead_knot': dead,
               'expected': EXPECTED[n], 'ok': (len(starts), dead) == EXPECTED[n],
               'by_number_of_dead': dict(sorted(Counter(s['loose'].count(0) for s in starts).items())),
               'by_number_of_members': dict(sorted(Counter(n - s['loose'].count(0) for s in starts).items()))}
        if n <= 4:
            # independent check: brute-force canonical forms over all labelled graphs
            bc = brute_count(n)
            mine = {brute_canon(n, graph_edges(s['g']), s['loose']) for s in starts}
            row['brute_force_classes'] = len(bc)
            row['brute_force_equal'] = (mine == bc and len(mine) == len(starts))
            row['ok'] = row['ok'] and row['brute_force_equal']
        bt, bd = burnside(n)
        row['burnside'] = [bt, bd]
        row['burnside_equal'] = (bt, bd) == (len(starts), dead)
        row['ok'] = row['ok'] and row['burnside_equal']
        out['by_n'][str(n)] = row
        out['ok'] = out['ok'] and row['ok']
        total += len(starts)
        dead_total += dead
        log('n = %d: %d graphs, %d starts, %d with a dead knot; expected %s; %s' % (
            n, ng, len(starts), dead, EXPECTED[n], 'OK' if row['ok'] else 'MISMATCH'), row)
    out['total'] = total
    out['dead_total'] = dead_total
    out['total_ok'] = (total, dead_total) == (86032, 55771)
    out['ok'] = out['ok'] and out['total_ok']
    out['resources'] = resources()
    log('total %d starts, %d with a dead knot: %s' % (total, dead_total, 'OK' if out['ok'] else 'MISMATCH'))
    write('census_count.json', out)


if __name__ == '__main__':
    main()
