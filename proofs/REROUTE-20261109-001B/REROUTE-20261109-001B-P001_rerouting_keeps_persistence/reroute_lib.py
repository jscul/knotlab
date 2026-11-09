"""Re-routing networks of rings (REROUTE-20261109-001B).

A map is a permutation sig of darts 0 .. 2E - 1 as in FLIP-RULE-20261109-001B (contact(d) = d >> 1, alpha(d) = d xor 1, rings the cycles
of sig, faces the cycles of sig alpha); the contact graph has an arc contact(d) -> contact(sig d) for every dart. Re-routing at a set S of
contacts exchanges, at each contact of S, which of its two rings each arriving ring continues on: sig_S = tau_S sig, tau_S swapping the two
darts of every contact in S. Lattice tori come from PLANE-PLAIN-20261109-001A-E001's tiling_lib. The plain first need of a ring is on time
for a target exactly when one of its contacts closest to the target has an odd number of shortest routes to it (a walk shorter than the
distance does not exist, and at the distance the walk count is the route count), as plain_lib.verdicts reads it."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLANE-PLAIN-20261109-001A/PLANE-PLAIN-20261109-001A-E001_tilings"))
import tiling_lib as TL  # noqa: E402

P = TL.P


def to_sig(rot, edges):
    sig, inv, at = TL.darts(rot, edges)
    s = [None] * (2 * len(edges))
    for d, e in sig.items():
        s[2 * d[0] + d[1]] = 2 * e[0] + e[1]
    return tuple(s)


def lattice(kind, n, m=None):
    """the torus Z^2 / <(n, 0), (0, m)> of the lattice as a dart permutation, with its rotation system"""
    B = ((n, 0), (0, m or n))
    rot, edges = TL.torus(kind, B)
    return to_sig(rot, edges), rot, edges, B


def cycles(perm):
    seen, out = set(), []
    for s in range(len(perm)):
        if s in seen:
            continue
        cyc, x = [], s
        while x not in seen:
            seen.add(x)
            cyc.append(x)
            x = perm[x]
        out.append(cyc)
    return out


def reroute(sig, S):
    return tuple(x ^ 1 if x >> 1 in S else x for x in sig)


def arcs(sig):
    return [sig[d] >> 1 for d in range(len(sig))]


def rings(sig):
    return [sorted({d >> 1 for d in r}) for r in cycles(sig)]


def is_network(sig):
    """no contact joins a ring to itself"""
    ring_of = {}
    for i, r in enumerate(cycles(sig)):
        for d in r:
            ring_of[d] = i
    return all(ring_of[2 * c] != ring_of[2 * c + 1] for c in range(len(sig) // 2))


def faces(sig):
    return cycles([sig[d ^ 1] for d in range(len(sig))])


def genus(sig):
    E = len(sig) // 2
    return (2 - (len(cycles(sig)) - E + len(faces(sig)))) // 2


def ring_graph_balls(sig, radius, roots=None):
    ring_of = {}
    for i, r in enumerate(cycles(sig)):
        for d in r:
            ring_of[d] = i
    adj = collections.defaultdict(set)
    for c in range(len(sig) // 2):
        a, b = ring_of[2 * c], ring_of[2 * c + 1]
        adj[a].add(b)
        adj[b].add(a)
    out = []
    for r0 in (roots if roots is not None else sorted(adj)):
        dist, layer, sizes = {r0: 0}, [r0], [1]
        for r in range(radius):
            nxt = [y for x in layer for y in adj[x] if y not in dist]
            nxt = list(dict.fromkeys(nxt))
            for y in nxt:
                dist[y] = r + 1
            layer = nxt
            sizes.append(sizes[-1] + len(nxt))
        out.append(sizes)
    return out


def routes_to(sig, target):
    """directed distance, and the shortest-route count as (count mod 2, min(count, 2)), from every contact to the target"""
    E = len(sig) // 2
    out = [(sig[2 * c] >> 1, sig[2 * c + 1] >> 1) for c in range(E)]
    inn = [[] for _ in range(E)]
    for a in range(E):
        for b in out[a]:
            inn[b].append(a)
    dist, par, low = [None] * E, [0] * E, [0] * E
    dist[target], par[target], low[target] = 0, 1, 1
    order, q = [target], collections.deque([target])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order.append(b)
    for b in order[1:]:
        nx = [e for e in out[b] if dist[e] == dist[b] - 1]
        par[b] = sum(par[e] for e in nx) & 1
        low[b] = min(2, sum(low[e] for e in nx))
    return dist, par, low


def late_pairs(sig, targets=None, single=False):
    """(ring, target) pairs whose plain first need is not on time; with single=True, pairs with no closest contact reached by exactly one
    shortest route (the single fastest way of RESCUE-MAP-20261109-001A)"""
    rs = rings(sig)
    E = len(sig) // 2
    bad = 0
    for t in (range(E) if targets is None else targets):
        dist, par, low = routes_to(sig, t)
        for cs in rs:
            ds = [dist[e] for e in cs if dist[e] is not None]
            if not ds:
                bad += 1
                continue
            m = min(ds)
            close = [e for e in cs if dist[e] == m]
            if single:
                bad += not any(low[e] == 1 for e in close)
            else:
                bad += not any(par[e] for e in close)
    return bad


def classes(kind, rot):
    """contacts by direction class: square and triangular by the direction they leave a ring in, honeycomb by k of e_k(p)"""
    cl = collections.defaultdict(set)
    for v, lst in rot.items():
        if kind == "honeycomb":
            if v[1] == 0:
                for k, e in enumerate(lst):
                    cl[k].add(e)
        else:
            for k, e in enumerate(lst[:len(lst) // 2]):
                cl[k].add(e)
    return cl


def face_moves(sig):
    return [sorted({d >> 1 for d in f}) for f in faces(sig)]
