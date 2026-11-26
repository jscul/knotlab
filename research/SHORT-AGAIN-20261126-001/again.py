"""again.py: once a change from afar has been heard, can a second be heard, and a third?  Third study after the first
checkpoint of SHORT-AGAIN-20261126-001.  AGAIN.md has the design and the expectations, written before the full run.

The pairs are those of the jam study (jam.py, three steps by a meeting) in which the receiver's own knots hear a
change three steps away or more under a law with waiting.  For each pair and law:
    W    the growth without a change
    G1   the growth with the first change heard from three steps or more (the first in jam.py's order); h1 the
         first round A's own births differ from W
    G2   in G1, after round h1, one more loose distinction at each of the five members of B's own knots nearest (in
         sharings) to A's own knots, each in turn; h2 the first later round A's own births differ from G1
    G3   the same again in the first G2 heard, after round h2
Read for each change: the round it was set, its distance in sharings from A's own knots then, the round heard or
none, and whether A has a waiting own knot (an own member that is short) in the round it is heard, in either growth.
A pattern hears a signal again when h2 is found, three times when h3 is.

    again.py one I J RATION     one pair and law, a JSON line"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ring_line, jam
bench, eng = ring_line.bench, ring_line.eng
ROUNDS, BOUND = 12, 1500


def waiting_own(g, rnd):
    """does A have an own member that is short in round `rnd` (1-based) of g?"""
    if rnd > len(g.rows): return None
    return g.rows[rnd - 1]['short by'].get('A', 0) > 0


def sharing_distance(g, c):
    """sharings, after round c, from each knot to the nearest of A's own knots"""
    S = g.snaps[c]; adj = collections.defaultdict(set)
    for hs in S.holders:
        for u in hs: adj[u].update(v for v in hs if v != u)
    dist = {u: 0 for u in range(S.n_knots) if ring_line.cls(g.anc[u]) == 'A'}; fr = list(dist)
    while fr:
        nx_ = []
        for u in fr:
            for v in adj[u]:
                if v not in dist: dist[v] = dist[u] + 1; nx_.append(v)
        fr = nx_
    return dist


def nearest_B(g, c, n=5):
    dist = sharing_distance(g, c); S = g.snaps[c]
    mem = [u for u, h, k in eng.live_members(S) if ring_line.cls(g.anc[u]) == 'B']
    return [(u, dist.get(u)) for u in sorted(mem, key=lambda u: (dist.get(u, 10 ** 6), u))[:n]]


def grow_from(stars, role, law, bar=None):
    g = ring_line.Growth(stars, role, law)
    if bar is not None:
        us = g.S.usable(bar)
        if not us: return None
        g.S.barred[us[-1]] = True; g.snaps[0] = g.S.copy()
    g.run(ROUNDS, BOUND); return g


def again(A, B, d, ration, treatment, first):
    law = jam.law_of(ration, treatment)
    st, ro, bar = jam.changed(A, B, d, None, 'meeting'); W = grow_from(st, ro, law)
    k = ''.join(ch for ch in first if not ch.isdigit()); i = int(''.join(ch for ch in first if ch.isdigit()))
    st, ro, bar = jam.changed(A, B, d, (k, i), 'meeting'); G1 = grow_from(st, ro, law, bar)
    h1, n = ring_line.first_own_diff(W, G1, 0)
    out = {'A': A, 'B': B, 'd': d, 'law': [ration, treatment], 'first': first, 'rounds': [len(W.rows), len(G1.rows)], 'h1': h1,
           'waiting at h1': None if h1 is None else [waiting_own(W, h1), waiting_own(G1, h1)], 'again': []}
    G, h = G1, h1
    for step in (2, 3):
        if h is None or h >= len(G.rows): break
        tried = []; got = None
        for u, du in nearest_B(G, h):
            H = ring_line.fork_at(G, h); ring_line.mark(H, u); H.run(ROUNDS, BOUND)
            r, m = ring_line.first_own_diff(G, H, h)
            tried.append({'set after round': h, 'knot': u, 'sharings from A': du, 'heard': r, 'rounds': m,
                          'waiting': None if r is None else [waiting_own(G, r), waiting_own(H, r)]})
            if r is not None and got is None: got = (r, H)
        out['again'].append(tried)
        if got is None: break
        h, G = got
    return out


if __name__ == '__main__':
    S = jam.starts() + [('stub', None, None)]
    if sys.argv[1] == 'one':
        i, j, ration, first = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
        print(json.dumps(again(S[i][0], S[j][0], 3, ration, 'CANCEL-WAIT', first)))
