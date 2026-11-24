"""The thread's own checks for PARENTS-FROM-HOLDERS-20261124-001, written independently of the study's code.

Run from the repository root:  .venv/bin/python -B research/PARENTS-FROM-HOLDERS-20261124-001/checks/thread_checks.py

1. The advisor's pair. Two-knot start under (FLOOR1, CANCEL-OFFSHOOT, RELEASE), grown R rounds with the ring study's
   engine. x is the first offshoot of start knot 0; a is its place shared with knot 0 (a parent place); b is its place
   shared with its join (a child place). The look within d holder steps is built here as a graph of knots and places and
   compared with networkx. Claim: the two looks are alike exactly when d <= R - 2.
2. The lone four-place knot under ordinary growth, grown until it stops: its knots and shared distinctions form the
   literature's four-dimensional hypercube graph, and some renaming of the whole structure swaps the start knot with one
   of its offshoots, carrying a parent place onto a child place.
"""
import functools, pathlib, sys
print = functools.partial(print, flush=True)
import networkx as nx
from networkx.algorithms import isomorphism as iso
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring'))
import engine as E


def holders(S):
    h = {}
    for u in range(S.n_knots):
        for d in S.places[u]:
            h.setdefault(d, []).append(u)
    return h


def look(S, x, a, d):
    """Graph of what is looked at within d holder steps of x, with the place a chosen.

    A knot's loose places and its shared places whose other holder is not shown are kept as counts on the knot
    (usable, barred, shared with a holder not shown); a distinction shared by two shown knots is a node of its own."""
    H = holders(S)
    dist = {x: 0}; frontier = [x]
    for step in range(d):
        nxt = []
        for u in frontier:
            for p in S.places[u]:
                for v in H[p]:
                    if v not in dist:
                        dist[v] = step + 1; nxt.append(v)
        frontier = nxt
    G = nx.Graph()
    for u in dist:
        usable = barred = out = 0
        for p in S.places[u]:
            hs = H[p]
            if len(hs) == 1:
                if p in S.barred: barred += 1
                else: usable += 1
            else:
                other = hs[0] if hs[1] == u else hs[1]
                if other in dist:
                    n = ('d', p)
                    if n not in G: G.add_node(n, kind='shared')
                    G.add_edge(('k', u), n)
                else:
                    out += 1
        G.add_node(('k', u), kind=('centre' if u == x else 'knot', usable, barred, out))
    G.nodes[('d', a)]['kind'] = 'chosen'
    return G


def alike(G1, G2):
    return nx.is_isomorphic(G1, G2, node_match=iso.categorical_node_match('kind', None))


print('1. The advisor\'s pair, two-knot start, (FLOOR1, CANCEL-OFFSHOOT, RELEASE)')
law = E.Law(ration='FLOOR1', treatment='CANCEL-OFFSHOOT')
S = E.from_stars([[0, 1, 2], [0, 3, 4]])
for R in range(1, 7):
    S, rec = E.round_step(S, law)
    if R < 3: continue
    H = holders(S)
    x = next(u for u in range(S.n_knots) if S.parents[u] == (0,))
    a = next(p for p in S.places[x] if 0 in H[p])
    kids = [u for u in range(S.n_knots) if x in S.parents[u] and len(S.parents[u]) == 2]
    b = next(p for p in S.places[x] if kids[0] in H[p])
    res = [alike(look(S, x, a, d), look(S, x, b, d)) for d in range(1, R + 1)]
    thr = max([d for d, ok in zip(range(1, R + 1), res) if ok], default=0)
    print('   round %d: knots %d; alike at d = %s; greatest such d = %d; R - 2 = %d; holds: %s'
          % (R, S.n_knots, [d for d, ok in zip(range(1, R + 1), res) if ok], thr, R - 2, thr == R - 2 and all(res[:thr])))

print('2. The lone four-place knot under ordinary growth')
S = E.from_stars([[0, 1, 2, 3]]); law = E.Law()
for r in range(1, 10):
    S, rec = E.round_step(S, law)
    if rec['stopped'] or rec['n_births'] == 0: break
H = holders(S)
K = nx.Graph(); K.add_nodes_from(range(S.n_knots))
for p, hs in H.items():
    if len(hs) == 2: K.add_edge(*hs)
print('   rounds %d; knots %d; places per knot %s; distinctions %d, all shared by two: %s'
      % (r, S.n_knots, sorted(set(len(S.places[u]) for u in range(S.n_knots))), len(H), all(len(h) == 2 for h in H.values())))
print('   the literature\'s four-dimensional hypercube graph:', nx.is_isomorphic(K, nx.hypercube_graph(4)))
child = next(u for u in range(S.n_knots) if S.parents[u] == (0,))
GM = iso.GraphMatcher(K, K)
swap = next((m for m in GM.isomorphisms_iter() if m[0] == child and m[child] == 0), None)
print('   a renaming of the whole structure that swaps start knot 0 with its offshoot %d exists: %s' % (child, swap is not None))
print('   parents of knot %d: %s; parents of knot 0: %s' % (child, S.parents[child], S.parents[0]))
