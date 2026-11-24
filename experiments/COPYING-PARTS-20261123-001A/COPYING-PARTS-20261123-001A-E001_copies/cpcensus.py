"""The census of starts of up to five knots (deviations.md C12), written again here from the description in ticket B's
deviations.md (B1), not imported: the connected graphs of networkx's graph atlas on n vertices (each isomorphism class
once), a loose count 0-3 on each knot with degree + loose count >= 3 and at least one live knot, each tuple kept when
it is the least of its orbit under the graph's automorphisms; stars: one shared distinction for each edge (sorted
edge order), then the loose distinctions of knot 0, knot 1, ...

`earlier_census(n_values)` reads the earlier census's runner records (ticket B, census/results.jsonl.gz) for the start
identities and set-aside flags only."""
import gzip
import itertools
import json
import os

import networkx as nx
from networkx.generators.atlas import graph_atlas_g

from cpcommon import ROOT

_ATLAS = None
_AUTOS = {}

EARLIER = os.path.join(ROOT, 'artifacts', 'RING-IN-BALANCE-20261123-001B', 'RING-IN-BALANCE-20261123-001B-E001_reference',
                       'census', 'results.jsonl.gz')


def atlas():
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = graph_atlas_g()
    return _ATLAS


def connected_graphs(n):
    return [(i, g) for i, g in enumerate(atlas()) if g.number_of_nodes() == n and nx.is_connected(g)]


def autos(gi):
    if gi not in _AUTOS:
        g = atlas()[gi]
        n = g.number_of_nodes()
        _AUTOS[gi] = [tuple(m[v] for v in range(n))
                      for m in nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
    return _AUTOS[gi]


def least_in_orbit(loose, auts):
    n = len(loose)
    best = None
    for sg in auts:
        b = [0] * n
        for v in range(n):
            b[sg[v]] = loose[v]
        b = tuple(b)
        if best is None or b < best:
            best = b
    return best


def starts(n):
    """(atlas index, loose tuple) of every census start on n knots, in atlas order then lexicographic order."""
    out = []
    for gi, g in connected_graphs(n):
        deg = [g.degree(v) for v in range(n)]
        auts = autos(gi)
        for loose in itertools.product(range(4), repeat=n):
            if any(deg[v] + loose[v] < 3 for v in range(n)) or not any(loose):
                continue
            if least_in_orbit(loose, auts) != loose:
                continue
            out.append((gi, list(loose)))
    return out


def edges(gi):
    return sorted(tuple(sorted(e)) for e in atlas()[gi].edges())


def stars(gi, loose):
    es = edges(gi)
    st = [[] for _ in loose]
    for d, (a, b) in enumerate(es):
        st[a].append(d)
        st[b].append(d)
    nxt = len(es)
    for v, c in enumerate(loose):
        for _ in range(c):
            st[v].append(nxt)
            nxt += 1
    return st


def earlier_census(n_values):
    """From the earlier census's records: for each n, the list of (g, loose, set_aside) in its order."""
    out = {n: [] for n in n_values}
    blocks = {}
    with gzip.open(EARLIER, 'rt') as f:
        for line in f:
            rec = json.loads(line)
            case = rec.get('case', '')
            n = int(case[1]) if case.startswith('n') else None
            if n not in out or rec.get('status') != 'ok':
                continue
            res = rec['result']
            blocks[(n, res['block'])] = [(s['g'], list(s['loose']), bool(s.get('set_aside'))) for s in res['starts']]
    for (n, b) in sorted(blocks):
        out[n].extend(blocks[(n, b)])
    return out
