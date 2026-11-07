"""Island restrictions of the knot sphere, for SPHERE-SIZE-20261107-001A.

An island packing is a set of balls of radius s in the point graph of K_k (centres away from the corners), pairwise at distance at
least D_sep, each coloured by one constant label in a frame developed over the island. A random hard-core packing proposes every
admissible point as a centre with probability eps and keeps a proposal when no other proposal lies within 2s + D_sep.

Restricting the knot formula by an island packing fixes the island points. Label states compatible with the restriction are decided
by the window criterion of SPHERE-WIDTH-20261107-001A with the island points as permanent pebbles; this module adds the packing, the
island colours, a cut star that avoids the islands, and the island-relative arc representatives the proof uses.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/SPHERE-WIDTH-20261107-001A/SPHERE-WIDTH-20261107-001A-P001_the_spheres_count_needs_width_sqrt_n"))
import width_lib as W  # noqa: E402

F = W.F


def packing(K, s, d_sep, eps, rng, corner_margin=None):
    """a random hard-core island packing: list of (centre, set of points)"""
    n, adj = K["n"], K["adj"]
    cm = corner_margin if corner_margin is not None else s + d_sep
    dc = W.bfs(adj, list(K["corner_pts"]), n)
    cand = [p for p in range(n) if dc[p] > cm]
    prop = [p for p in cand if rng.random() < eps]
    keep = []
    pset = set(prop)
    for c in prop:
        d = W.bfs(adj, [c], n)
        if not any(q != c and d[q] <= 2 * s + d_sep for q in pset):
            keep.append((c, {p for p in range(n) if d[p] <= s}))
    return keep


def island_colours(K, islands, labels):
    """fixed colours: each island read in a frame developed from its centre along lines inside it"""
    col = {}
    for (c, pts), lab in zip(islands, labels):
        frame = {c: (0, 0)}
        stack = [c]
        while stack:
            a = stack.pop()
            for l in K["lines_of"][a]:
                L = K["lines"][l]
                if not all(q in pts for q in L):
                    continue
                for b in L:
                    if b in frame or b == a:
                        continue
                    o, e = F.step(K, l, a, b)
                    frame[b] = ((frame[a][0] + o) % 3, frame[a][1] ^ e)
                    stack.append(b)
        assert set(frame) == pts, "island not connected through its lines"
        for p, (sg, g) in frame.items():
            col[p] = F.PATTERNS[lab][sg] ^ g
    return col


def trivialize_avoiding(K, z, islands):
    """a cut star from z to the corners through triangles that meet no island point"""
    isl = set().union(*[pts for _, pts in islands]) if islands else set()
    G = K["G"]
    allowed = {v for v in G if not any(p in isl for p in F.vertex_points(K, v))}
    star = F.disjoint_paths(G, F.triangles_at(K, G, z), [("f", fi) for fi in F.corner_faces(K)], z, None, allowed=allowed)
    if star is None:
        return None
    base = next(p for p in range(K["n"]) if p != z)
    fr = F.develop(K, z, star, base)
    T = dict(z=z, star=star, fr=fr, shift={})
    import itertools
    for l, L in enumerate(K["lines"]):
        for a, b in itertools.permutations([p for p in L if p != z], 2):
            o, e = F.step(K, l, a, b)
            d = (fr[a][0] + o - fr[b][0]) % 3
            t = (2 * d + 3 * (fr[a][1] ^ e ^ fr[b][1])) % 6
            T["shift"].setdefault((a, b), []).append({0: 0, 1: 1, 5: -1}[t])
    return T


def island_label(T, pts, col):
    """the island's constant label in the developed frame (the one label every point's arc contains)"""
    common = set(range(6))
    for p in pts:
        sg, g = T["fr"][p]
        common &= {lab for lab in range(6) if F.PATTERNS[lab][sg] ^ g == col[p]}
    assert len(common) == 1, common
    return common.pop()


def relative_starts(T, islands, col, peb):
    """arc starts a_p, island points taken in [l - 2, l] around their island's label l in 0..5, other pebbles in 0..5"""
    a = {p: W.arc_start(T["fr"][p], c) for p, c in peb.items()}
    where = {}
    for j, (c, pts) in enumerate(islands):
        lab = island_label(T, pts, col)
        for p in pts:
            x = a[p]
            while x > lab:
                x -= 6
            while x < lab - 2:
                x += 6
            a[p] = x
            where[p] = j
    return a, where


def random_compatible_state(K, z, T, fixed, rng):
    """a random label state with vortex z whose colours agree with the fixed ones (solver, random phases); None if none"""
    import itertools
    from pysat.formula import IDPool
    from pysat.solvers import Solver
    pool = IDPool()
    var = lambda v, c: pool.id((v, c))  # noqa: E731
    cl = []
    for v in range(K["n"]):
        if v == z:
            continue
        cl.append([var(v, c) for c in range(6)])
        cl += [[-var(v, c), -var(v, d)] for c, d in itertools.combinations(range(6), 2)]
    for p, colour in fixed.items():
        ap = W.arc_start(T["fr"][p], colour)
        cl.append([var(p, (ap + i) % 6) for i in range(3)])
    for (u, v), ts in T["shift"].items():
        for t in ts:
            for lu in range(6):
                for lv in range(6):
                    if min((lv + t - lu) % 6, (lu - lv - t) % 6) > 1:
                        cl.append([-var(u, lu), -var(v, lv)])
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        S.set_phases([var(v, c) * rng.choice((1, -1)) for v in range(K["n"]) if v != z for c in range(6)])
        if not S.solve():
            return None
        mod = set(S.get_model())
    x = [0] * K["n"]
    for v in range(K["n"]):
        if v != z:
            lab = next(c for c in range(6) if var(v, c) in mod)
            sg, g = T["fr"][v]
            x[v] = F.PATTERNS[lab][sg] ^ g
    return x


def term_audit(K, T, islands, col, peb, spoiler, cert):
    """per-segment terms of a certificate with island-relative representatives: (cycle sum, bad negative terms, same-island minimum,
    worst slack of the between-island bound b >= floor((dist - 11) / 6), walk length, Spoiler pebbles on the cycle)"""
    cyc, walk, bsum, _ = cert
    a, where = relative_starts(T, islands, col, peb)
    Wt = W.weights(T)
    total, bad_neg, same_min, between_slack = 0, 0, None, None
    for p, q in zip(cyc, cyc[1:] + cyc[:1]):
        D = W.dists(Wt, p, K["n"])[q]
        b = (D + a[p] + 2 - a[q]) // 6
        total += b
        if b < 0 and p not in spoiler and q not in spoiler:
            bad_neg += 1
        if p in where and q in where:
            if where[p] == where[q]:
                same_min = b if same_min is None else min(same_min, b)
            else:
                dd = W.bfs(K["adj"], [p], K["n"])[q]
                sl = b - (dd - 11) // 6
                between_slack = sl if between_slack is None else min(between_slack, sl)
    return total, bad_neg, same_min, between_slack, len(walk) - 1, sum(1 for p in cyc if p in spoiler)


def greedy_packing(K, s, d_sep, rng, corner_margin=None):
    """a maximal packing in random order: a centre is kept when it is at distance >= 2s + d_sep from every kept centre"""
    n, adj = K["n"], K["adj"]
    cm = corner_margin if corner_margin is not None else s + 3
    dc = W.bfs(adj, list(K["corner_pts"]), n)
    cand = [p for p in range(n) if dc[p] > cm]
    rng.shuffle(cand)
    keep, near = [], [None] * n
    for c in cand:
        if near[c] is not None and near[c] < 2 * s + d_sep:
            continue
        d = W.bfs(adj, [c], n)
        keep.append((c, {p for p in range(n) if d[p] <= s}))
        for p in range(n):
            if near[p] is None or d[p] < near[p]:
                near[p] = d[p]
    return keep
