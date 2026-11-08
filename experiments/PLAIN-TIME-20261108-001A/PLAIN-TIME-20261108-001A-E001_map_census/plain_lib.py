"""Distance without freezing (PLAIN-TIME-20261108-001): orientably regular maps as networks of rule-60 rings, and the plain first need
against the directed distance.

A map comes from a group G with an element x (the rotation at a ring, of order m) and an involution y (the half-turn of a contact), with
G = <x, y> and y not in <x> (no contact joins a ring to itself): darts are the elements, a ring is a coset g<x> with its contacts in the
order g, gx, gx^2, ..., a contact is a coset {g, gy}, and faces are the cosets of <xy>, of size f. As a network of equally spaced rule-60
rings with law (12, 12) contacts (LOOP-NET-20261108-001A, Theorem 3: every contact persists), its contact graph sends the contact
{g, gy} to {gx, gxy} along the ring of g and to {gyx, gyxy} along the ring of gy (DISTANCE-20261108-001A's distance_lib.regular_map and
loopnet_lib.corners give the same graph). G acts on the left, preserving rings, contacts and arcs, transitively on contacts, so one
target contact settles every ring-contact pair. Tori {4,4}_(b,c), {3,6}_(b,c) and {6,3}_(b,c) are built as rotation systems on the plane
lattices modulo a rotation-invariant sublattice, and read through loopnet_lib like every other network.

The plain first need of contact c on ring r is on time when it comes at the directed distance delta(r -> c): by DISTANCE-20261108-001B,
Theorem 4, exactly when an odd number of shortest routes lead to c from one of r's contacts at distance delta(r -> c)."""
from __future__ import annotations

import collections
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes"))
import distance_lib as D  # noqa: E402

LN, T = D.LN, D.T


# ---------- permutation groups: elements are tuples, (a * b)(i) = a[b[i]]
def mul(a, b):
    return tuple(a[i] for i in b)


def closure(gens):
    one = tuple(range(len(gens[0])))
    seen, todo = {one}, [one]
    while todo:
        a = todo.pop()
        for g in gens:
            b = mul(a, g)
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


def generates(gens, size):
    one = tuple(range(len(gens[0])))
    seen, todo = {one}, [one]
    while todo:
        a = todo.pop()
        for g in gens:
            b = mul(a, g)
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return len(seen) == size


def order(a):
    one = tuple(range(len(a)))
    k, p = 1, a
    while p != one:
        p, k = mul(p, a), k + 1
    return k


def inverse(a):
    out = [0] * len(a)
    for i, j in enumerate(a):
        out[j] = i
    return tuple(out)


def perm_of(f, points):
    idx = {p: i for i, p in enumerate(points)}
    return tuple(idx[f(p)] for p in points)


def proj_line(p):
    return [(1, a) for a in range(p)] + [(0, 1)]


def proj_norm(v, p):
    a, b = v[0] % p, v[1] % p
    if a:
        inv = pow(a, p - 2, p)
        return (1, b * inv % p)
    return (0, 1)


def matrix_on_line(M, p):
    pts = proj_line(p)
    return perm_of(lambda v: proj_norm((M[0] * v[0] + M[1] * v[1], M[2] * v[0] + M[3] * v[1]), p), pts)


def matrix_on_vectors(M, p):
    pts = [(a, b) for a in range(p) for b in range(p) if (a, b) != (0, 0)]
    return perm_of(lambda v: ((M[0] * v[0] + M[1] * v[1]) % p, (M[2] * v[0] + M[3] * v[1]) % p), pts)


def nonresidue(p):
    return next(g for g in range(2, p) if pow(g, (p - 1) // 2, p) == p - 1)


def group(name):
    """the census's groups, as permutation groups: (elements, a list of generators)"""
    kind, _, arg = name.partition(" ")
    if kind == "PSL(2,p)":
        p = int(arg)
        gens = [matrix_on_line((1, 1, 0, 1), p), matrix_on_line((0, p - 1, 1, 0), p)]
    elif kind == "PGL(2,p)":
        p = int(arg)
        gens = [matrix_on_line((1, 1, 0, 1), p), matrix_on_line((0, p - 1, 1, 0), p), matrix_on_line((nonresidue(p), 0, 0, 1), p)]
    elif kind == "SL(2,p)":
        p = int(arg)
        gens = [matrix_on_vectors((1, 1, 0, 1), p), matrix_on_vectors((0, p - 1, 1, 0), p)]
    elif kind == "GL(2,p)":
        p = int(arg)
        g = 2 if p == 3 else nonresidue(p)
        gens = [matrix_on_vectors((1, 1, 0, 1), p), matrix_on_vectors((0, p - 1, 1, 0), p), matrix_on_vectors((g, 0, 0, 1), p)]
    elif kind == "S":
        n = int(arg)
        gens = [tuple([1, 0] + list(range(2, n))), tuple(list(range(1, n)) + [0])]
    elif kind == "A":
        n = int(arg)
        c3 = tuple([1, 2, 0] + list(range(3, n)))
        long = tuple((i + 1) % n for i in range(n)) if n % 2 else tuple([0] + [1 + i % (n - 1) for i in range(1, n)])
        gens = [c3, long]
    elif kind == "D":
        n = int(arg)
        gens = [tuple((i + 1) % n for i in range(n)), tuple((-i) % n for i in range(n))]
    else:
        raise ValueError(name)
    return sorted(closure(gens)), gens


def involution_classes(G, gens):
    """one involution from each conjugacy class"""
    invs = [g for g in G if g != tuple(range(len(g))) and mul(g, g) == tuple(range(len(g)))]
    seen, reps = set(), []
    ginv = [inverse(g) for g in gens]
    for y in invs:
        if y in seen:
            continue
        reps.append(y)
        cls, todo = {y}, [y]
        while todo:
            a = todo.pop()
            for g, gi in zip(gens, ginv):
                b = mul(mul(g, a), gi)
                if b not in cls:
                    cls.add(b)
                    todo.append(b)
        seen |= cls
    return reps


def generating_pairs(G, gens):
    """(x, y): y one involution per conjugacy class, x of order at least 2 with <x, y> = G and y not in <x>, one x per orbit of the
    centraliser of y acting by conjugation (conjugating by it gives an isomorphic map)"""
    size = len(G)
    one = tuple(range(len(G[0])))
    for y in involution_classes(G, gens):
        cent = [g for g in G if mul(g, y) == mul(y, g)]
        cinv = [inverse(g) for g in cent]
        seen = set()
        for x in G:
            if x == one or x in seen:
                continue
            seen |= {mul(mul(g, x), gi) for g, gi in zip(cent, cinv)}
            if y in closure([x]):
                continue
            if generates([x, y], size):
                yield x, y


# ---------- the contact graph of a group map, and the verdicts
def group_map(G, x, y):
    """(contact count, out-arcs with multiplicity, ring -> contacts, target contact, m, f)"""
    idx = {g: i for i, g in enumerate(G)}
    one = tuple(range(len(G[0])))
    cid, contacts = {}, 0
    for g in G:
        if g not in cid:
            cid[g] = cid[mul(g, y)] = contacts
            contacts += 1
    rid, rings = {}, 0
    for g in G:
        if g not in rid:
            h = g
            while True:
                rid[h] = rings
                h = mul(h, x)
                if h == g:
                    break
            rings += 1
    out = [None] * contacts
    ring_contacts = [set() for _ in range(rings)]
    for g in G:
        c = cid[g]
        ring_contacts[rid[g]].add(c)
        if out[c] is None:
            out[c] = [cid[mul(g, x)], cid[mul(mul(g, y), x)]]
    return contacts, out, [sorted(s) for s in ring_contacts], cid[one], order(x), order(mul(x, y))


def network_map(sizes, contacts):
    """the same data for a network in net_lib format, through loopnet_lib.corners"""
    out = [[] for _ in contacts]
    for d, e, ring, l in LN.corners(sizes, contacts):
        out[d].append(e)
    rc = collections.defaultdict(set)
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        rc[ra].add(c)
        rc[rb].add(c)
    return len(contacts), out, [sorted(rc[r]) for r in sorted(rc)]


def verdicts(n, out, ring_contacts, target):
    """the directed distance and shortest-route count from every contact to the target, the least odd walk length (exact, by the
    span of rows mod 2), and the ring-level and contact-level verdicts"""
    inn = [[] for _ in range(n)]
    for d in range(n):
        for e in out[d]:
            inn[e].append(d)
    dist, cnt = [None] * n, [0] * n
    dist[target], cnt[target] = 0, 1
    order_, q = [target], collections.deque([target])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order_.append(b)
    for b in order_[1:]:
        cnt[b] = sum(cnt[e] for e in out[b] if dist[e] is not None and dist[e] == dist[b] - 1)
    ins = [0] * n
    for d in range(n):
        for e in out[d]:
            ins[e] ^= 1 << d
    first = T.reach(ins, target)[1]
    late = never = mismatch = 0
    for cs in ring_contacts:
        if all(dist[e] is None for e in cs):
            continue
        dr = min(dist[e] for e in cs if dist[e] is not None)
        on = any(dist[e] == dr and cnt[e] % 2 for e in cs)
        ks = [first[e] for e in cs if e in first]
        kr = min(ks) if ks else None
        mismatch += (kr == dr) != on or (kr is not None and kr < dr)
        if kr is None:
            never += 1
        elif kr > dr:
            late += 1
    c_late = sum(1 for e in range(n) if dist[e] is not None and e in first and first[e] > dist[e])
    c_never = sum(1 for e in range(n) if dist[e] is not None and e not in first)
    reachable = [e for e in range(n) if dist[e] is not None]
    multi = [dist[e] for e in reachable if cnt[e] >= 2]
    even = [dist[e] for e in reachable if cnt[e] % 2 == 0]
    return {"diameter": max(dist[e] for e in reachable), "unreachable": n - len(reachable),
            "rings late": late, "rings never": never, "contacts late": c_late, "contacts never": c_never,
            "shortest pair of equal routes": min(multi) if multi else None, "first even count": min(even) if even else None,
            "largest count": max(cnt), "parallel arcs": sum(1 for d in range(n) if len(set(out[d])) < len(out[d])),
            "cone mismatches": mismatch,
            "distance profile": sorted(collections.Counter(dist[e] for e in reachable).items())}


# ---------- tori of every shape
def reduce_mod(v, B):
    """the representative of v modulo the lattice with basis rows B = ((a, b), (c, d)), in its fundamental parallelogram"""
    (a, b), (c, d) = B
    det = a * d - b * c
    i, j = v
    s = (i * d - j * c)
    t = (j * a - i * b)
    fs, ft = s // det if det > 0 else -((-s) // det), t // det if det > 0 else -((-t) // det)
    return (i - fs * a - ft * c, j - fs * b - ft * d)


def lattice_torus(kind, b, c):
    """{4,4}_(b,c), {3,6}_(b,c) or {6,3}_(b,c) as (rot, edges); vertices are lattice points modulo the rotation-invariant sublattice
    spanned by (b, c) and its image under the rotation (the honeycomb: two vertices per point)"""
    if kind == "square":
        rot_v = lambda v: (-v[1], v[0])
        dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    elif kind in ("triangular", "honeycomb"):
        # triangular lattice in the basis e1 (0 degrees), e2 (120 degrees): the 60-degree turn sends (i, j) to (i - j, i);
        # LN's triangular directions (1,0), (1,1), (0,1), ... are counterclockwise there. The honeycomb's translations turn by
        # 120 degrees: t1 -> t2 - t1, t2 -> -t1 (its A vertex joins B(t), B(t - t1), B(t - t2))
        rot_v = (lambda v: (v[0] - v[1], v[0])) if kind == "triangular" else (lambda v: (-v[0] - v[1], v[0]))
        dirs = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))
    B = ((b, c), rot_v((b, c)))
    det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    if det < 0:
        B = (B[1], B[0])
        det = -det
    pts = sorted({reduce_mod((i, j), B) for i in range(-det, det + 1) for j in range(-det, det + 1)})
    assert len(pts) == det, (kind, b, c, len(pts), det)
    red = lambda v: reduce_mod(v, B)
    if kind in ("square", "triangular"):
        edges, eid = [], {}
        for v in pts:
            for d in dirs[:len(dirs) // 2]:
                w = red((v[0] + d[0], v[1] + d[1]))
                eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
                edges.append((v, w))
        return {v: [eid[(v, d)] for d in dirs] for v in pts}, edges
    verts = [(p, s) for p in pts for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for p in pts:
        a = (p, 0)
        for k, q in enumerate((p, red((p[0] - 1, p[1])), red((p[0], p[1] - 1)))):
            rot[a][k] = rot[(q, 1)][k] = len(edges)
            edges.append((a, (q, 1)))
    return rot, edges


def torus_shapes(kind, nmax):
    """(b, c) with 0 <= c <= b and index at most nmax, one per index and chirality pair"""
    out = []
    for b in range(1, nmax + 1):
        for c in range(0, b + 1):
            N = b * b + c * c if kind == "square" else b * b + b * c + c * c
            if 3 <= N <= nmax:
                out.append((b, c, N))
    return out
