"""Referee R1 for CUBIC-FROM-A-KNOT-20261117-001 (own code; the study's check.py, cut_control.py and path_check.py are not imported).

  ../../../.venv/bin/python -B referee_cubic.py <part> > referee_cubic_<part>.json      (from this directory)

Parts:
  grow    the parallel policy, written from the proof's section 1 (incidence and loose bits only), from one ternary parity knot,
          rounds 0..11; is round t's incidence isomorphic to the orthant layer I_t = {v in N^3 : sum v <= t}?  (The study replayed
          to 220 junctions, I_9; I_10 and I_11 are one and two sizes past.)  Also the same rule with two fresh bits and groups of at
          most two: does it give the quarter plane?
  grow4   four fresh bits, groups of at most three: does it still follow N^4's layers?
  boxes   open boxes of side n = 2..5 at the corner: junctions, shared and loose bits, rank of the parity equations, the number of
          allowed states; the eight marked bits K and the cut relation S on them (Y); the marginal on K; the marginal on one
          distinguished-direction bit per junction; every junction's star a K1-K3 knot (in Y as well); the disagreement count of
          every pair.  Side 5 is one size past the study's 4.
  bonds   the long bonds: for random pairs of edges in the side-9 box, the boundary of a shortest monotone path between their
          nearest endpoints, tested by GF(2) ranks as a K1-K3 bond (one check on it, its full parity, and no check on any part),
          its size against 4d + 6; and the lower bound: for every bond up to a size cap found by enumerating connected vertex sets
          with connected complement near the corner and in the interior, the sup-norm spread of its anchors against |F| - 1.
  whitney 3-connectivity of each box's graph with one vertex for the loose bits (then, by Whitney's 2-isomorphism theorem, the
          allowed states determine the junction graph up to isomorphism).
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict

import networkx as nx

AX = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


# ---------------------------------------------------------------- growth, from incidence alone
class Branch:
    def __init__(self, fresh=3):
        self.fresh = fresh
        self.junctions = [list(range(fresh))]          # junction -> its bits
        self.owners = defaultdict(list)                 # bit -> junctions
        for b in range(fresh):
            self.owners[b].append(0)
        self.nbits = fresh

    def neighbours(self, j):
        return {k for b in self.junctions[j] for k in self.owners[b] if k != j}

    def loose(self, j):
        return [b for b in self.junctions[j] if len(self.owners[b]) == 1]

    def round(self, max_group=3):
        front = [j for j in range(len(self.junctions)) if self.loose(j)]
        nb = {j: self.neighbours(j) for j in range(len(self.junctions))}
        cand = {frozenset(p) for p in itertools.combinations(front, 2) if nb[p[0]] & nb[p[1]]}
        triples = []
        if max_group >= 3:
            for t in itertools.combinations(front, 3):
                if all(frozenset(p) in cand for p in itertools.combinations(t, 2)) and not (nb[t[0]] & nb[t[1]] & nb[t[2]]):
                    triples.append(t)
        in_triple = {frozenset(p) for t in triples for p in itertools.combinations(t, 2)}
        pairs = [tuple(sorted(p)) for p in cand if p not in in_triple] if max_group >= 2 else []
        groups = [tuple(t) for t in triples] + sorted(pairs)
        free = {j: list(self.loose(j)) for j in front}
        new = []
        for g in groups:
            if any(not free[j] for j in g):
                raise RuntimeError("not enough loose bits for the groups")
            new.append([free[j].pop() for j in g])
        for j in front:
            for b in free[j]:
                new.append([b])
        for bits in new:
            j = len(self.junctions)
            fresh = list(range(self.nbits, self.nbits + self.fresh))
            self.nbits += self.fresh
            self.junctions.append(bits + fresh)
            for b in bits + fresh:
                self.owners[b].append(j)
        return Counter(len(g) for g in groups)

    def graph(self):
        G = nx.Graph()
        for j, bits in enumerate(self.junctions):
            G.add_node(("j", j), kind="junction")
            for b in bits:
                G.add_node(("b", b), kind="bit")
                G.add_edge(("j", j), ("b", b))
        return G


def orthant_layer(t, dim=3):
    """The expected incidence: a junction at every v in N^dim with sum <= t, each with dim outgoing bits (v -> v + e_i)."""
    G = nx.Graph()
    pts = [v for v in itertools.product(range(t + 1), repeat=dim) if sum(v) <= t]
    S = set(pts)
    for v in pts:
        G.add_node(("j", v), kind="junction")
        for i in range(dim):
            w = tuple(v[k] + (k == i) for k in range(dim))
            b = ("b", v, i)
            G.add_node(b, kind="bit")
            G.add_edge(("j", v), b)
            if w in S:
                G.add_edge(("j", w), b)
    return G


def iso(G, H):
    if G.number_of_nodes() != H.number_of_nodes() or G.number_of_edges() != H.number_of_edges():
        return False
    if nx.weisfeiler_lehman_graph_hash(G, node_attr="kind") != nx.weisfeiler_lehman_graph_hash(H, node_attr="kind"):
        return False
    return nx.is_isomorphic(G, H, node_match=lambda a, b: a["kind"] == b["kind"])      # VF2 (vf2pp stalled at round 4)


def part_grow():
    out = {"three_fresh_bits": [], "two_fresh_bits_pairs_only": []}
    B = Branch(3)
    for t in range(0, 12):
        G = B.graph()
        nj = len(B.junctions)
        row = {"round": t, "junctions": nj, "expected_I_t": len(list(v for v in itertools.product(range(t + 1), repeat=3) if sum(v) <= t))}
        row["isomorphic_to_I_t"] = iso(G, orthant_layer(t)) if t <= 11 else None
        out["three_fresh_bits"].append(row)
        print("grow3", json.dumps(row), file=sys.stderr, flush=True)
        if t < 11:
            row["groups_next_round"] = dict(B.round(3))
    B = Branch(2)
    for t in range(0, 15):
        row = {"round": t, "junctions": len(B.junctions), "isomorphic_to_quarter_plane_layer": iso(B.graph(), orthant_layer(t, 2))}
        out["two_fresh_bits_pairs_only"].append(row)
        if t < 14:
            B.round(2)
    print("grow2", json.dumps(out["two_fresh_bits_pairs_only"][-1]), file=sys.stderr, flush=True)
    return out


def part_grow4():
    """Four fresh bits, groups of at most three: junction counts against N^4's layers C(t + 4, 4), and the WL hash (VF2 is too slow
    on N^4's symmetric layers; a differing hash or count proves non-isomorphism, an equal one is only consistent)."""
    out = []
    B = Branch(4)
    for t in range(0, 7):
        G = B.graph()
        H = orthant_layer(t, 4)
        row = {"round": t, "junctions": len(B.junctions), "N4_layer_junctions": sum(1 for n in H if n[0] == "j"),
               "same_WL_hash_as_N4_layer": nx.weisfeiler_lehman_graph_hash(G, node_attr="kind") ==
               nx.weisfeiler_lehman_graph_hash(H, node_attr="kind")}
        out.append(row)
        print("grow4", json.dumps(row), file=sys.stderr, flush=True)
        if t < 6:
            try:
                row["groups_next_round"] = dict(B.round(3))
            except RuntimeError as e:
                row["next_round"] = str(e)
                break
    return out


# ---------------------------------------------------------------- GF(2) linear algebra on boxes
def rank(rows):
    """Rank over GF(2) of a list of int bit-rows."""
    piv = {}
    r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                piv[h] = x
                r += 1
                break
    return r


def box(n):
    """Open box of side n at the corner: junction at each v in [0, n)^3, bits = every outgoing edge (v, i)."""
    verts = list(itertools.product(range(n), repeat=3))
    edges = [(v, i) for v in verts for i in range(3)]
    eid = {e: k for k, e in enumerate(edges)}
    inc = defaultdict(list)
    for (v, i), k in eid.items():
        inc[v].append(k)
        w = tuple(v[a] + (a == i) for a in range(3))
        if max(w) < n:
            inc[w].append(k)
    H = [sum(1 << k for k in inc[v]) for v in verts]
    return verts, edges, eid, inc, H


def checks_within(H, cols_mask, nbits):
    """dim of {y H : supp(y H) within cols_mask} = rank(H) - rank(H restricted to the other columns)."""
    out_mask = ((1 << nbits) - 1) ^ cols_mask
    return rank(H) - rank([h & out_mask for h in H])


def is_bond(H, F, nbits):
    m = sum(1 << k for k in F)
    if checks_within(H, m, nbits) != 1:
        return False
    return all(checks_within(H, m ^ (1 << k), nbits) == 0 for k in F)


S_ROWS = None


def cut_relation():
    """The eight-place cut cube S, on positions v in {0,1}^3 (bit k of a row = value at position k), literal betweenness."""
    pos = list(itertools.product((0, 1), repeat=3))
    rows = {0, 255}
    for i in range(3):
        m = sum(1 << k for k, v in enumerate(pos) if v[i])
        rows |= {m, 255 ^ m}
    # literal check: S is the set of rows allowed by every betweenness B(a, b, c) where b lies on a shortest path from a to c
    trip = [(a, b, c) for a, b, c in itertools.permutations(range(8), 3) if a < c and
            all(pos[b][i] in (pos[a][i], pos[c][i]) for i in range(3))]
    allowed = {x for x in range(256) if all(not ((x >> a & 1) == (x >> c & 1) != (x >> b & 1)) for a, b, c in trip)}
    return pos, sorted(rows), sorted(allowed)


def solvable(H, nbits, fixed):
    """Is there z with H z = 0 and z_k = fixed[k] for the given bits?  Gaussian elimination on [H | 0] with the fixed columns
    moved to the right-hand side."""
    fmask = sum(1 << k for k in fixed)
    rows = []
    for h in H:
        rhs = bin(h & sum(1 << k for k, val in fixed.items() if val)).count("1") & 1
        rows.append(((h & ~fmask), rhs))
    piv = {}
    for x, r in rows:
        while x:
            hbit = x.bit_length() - 1
            if hbit in piv:
                px, pr = piv[hbit]
                x ^= px
                r ^= pr
            else:
                piv[hbit] = (x, r)
                break
        if x == 0 and r == 1:
            return False
    return True


def part_boxes():
    pos, S, S_lit = cut_relation()
    out = {"S_from_constants_and_thresholds": S, "S_equals_literal_betweenness_rows": S == S_lit, "boxes": []}
    for n in (2, 3, 4, 5):
        verts, edges, eid, inc, H = box(n)
        nb = len(edges)
        shared = sum(1 for v, i in edges if v[i] + 1 < n)
        r = rank(H)
        row = {"side": n, "junctions": len(verts), "shared_bits": shared, "loose_bits": nb - shared,
               "parity_rank": r, "log2_allowed_states": nb - r}
        K = [eid[(v, 2)] for v in pos]                         # the marked bits: distinguished-direction edges at {0,1}^3
        Kmask = sum(1 << k for k in K)
        row["checks_on_K"] = checks_within(H, Kmask, nb)       # 0: every one of the 256 tuples on K extends
        P = [eid[(v, 2)] for v in verts]                       # one distinguished-direction bit per junction
        row["checks_on_position_bits"] = checks_within(H, sum(1 << k for k in P), nb)
        # Y = C with K restricted to S: rows = 2^(free) * |S| / 2^8 when K is free in C
        row["log2_rows_of_Y"] = (nb - r) - 8 + 3 if row["checks_on_K"] == 0 else None
        # stars: each junction's incident bits form a K1-K3 knot in C (one check, its full parity)
        stars_ok = sum(1 for v in verts if is_bond(H, inc[v], nb))
        row["stars_that_are_bonds_in_C"] = f"{stars_ok}/{len(verts)}"
        # stars in Y (nonlinear): the projection onto the star is exactly even parity, by enumeration and linear feasibility
        if n <= 4:
            okY = 0
            for v in verts:
                F = inc[v]
                allowed = set()
                for a in range(1 << len(F)):
                    fixed = {k: (a >> t) & 1 for t, k in enumerate(F)}
                    for s in S:
                        fx = dict(fixed)
                        clash = False
                        for t, k in enumerate(K):
                            val = (s >> t) & 1
                            if k in fx and fx[k] != val:
                                clash = True
                                break
                            fx[k] = val
                        if not clash and solvable(H, nb, fx):
                            allowed.add(a)
                            break
                even = {a for a in range(1 << len(F)) if bin(a).count("1") % 2 == 0}
                okY += allowed == even
            row["stars_exactly_even_parity_in_Y"] = f"{okY}/{len(verts)}"
        # disagreement count of every pair of bits in C: free pairs differ in exactly half the states
        pair_checks = Counter()
        for a, b in itertools.combinations(range(nb), 2) if nb <= 200 else []:
            pair_checks[checks_within(H, (1 << a) | (1 << b), nb)] += 1
        if pair_checks:
            row["pairs_by_checks_on_them"] = dict(pair_checks)
        out["boxes"].append(row)
        print("box", json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_bonds(n=9, samples=200, seed=5):
    verts, edges, eid, inc, H = box(n)
    nb = len(edges)
    rng = random.Random(seed)
    inner = [e for e in edges if max(e[0]) <= n - 4]                 # anchors well inside, so tubes stay in the box

    def ends(e):
        v, i = e
        return v, tuple(v[a] + (a == i) for a in range(3))

    res = Counter()
    worst_ratio = 0.0
    for _ in range(samples):
        e, f = rng.sample(inner, 2)
        best = None
        for x in ends(e):
            for y in ends(f):
                d = sum(abs(a - b) for a, b in zip(x, y))
                if best is None or d < best[0]:
                    best = (d, x, y)
        d, x, y = best
        # a shortest monotone path from x to y: move along each axis in turn (axis order chosen at random)
        order = rng.sample(range(3), 3)
        path = [x]
        cur = list(x)
        for a in order:
            step = 1 if y[a] > cur[a] else -1
            while cur[a] != y[a]:
                cur[a] += step
                path.append(tuple(cur))
        P = set(path)
        F = sorted({k for (v, i), k in eid.items()
                    if (v in P) != (tuple(v[a] + (a == i) for a in range(3)) in P)})
        bond = is_bond(H, F, nb) and eid[e] in F and eid[f] in F
        res["bond" if bond else "NOT a bond"] += 1
        res["size<=4d+6" if len(F) <= 4 * d + 6 else "size>4d+6"] += 1
        worst_ratio = max(worst_ratio, (len(F) - 1) / max(1, d))
    out = {"box_side": n, "pairs": samples, "tally": dict(res), "largest_(|F|-1)/d": worst_ratio}
    print("bonds tubes", json.dumps(out), file=sys.stderr, flush=True)
    # the lower bound, by enumeration: every connected vertex set U (in N^3) with connected complement, |U| <= 5, near a centre;
    # its boundary is a bond (minimal cut); the sup-norm spread of the anchors of its edges must be <= |F| - 1
    def nbrs(v):
        for a in range(3):
            for s in (1, -1):
                w = tuple(v[k] + (s if k == a else 0) for k in range(3))
                if min(w) >= 0:
                    yield w

    def boundary(U):
        F = []
        for v in U:
            for w in nbrs(v):
                if w not in U:
                    F.append((min(v, w), max(v, w)))
            for a in range(3):                                       # include the orthant's edges only
                pass
        return F

    def complement_connected(U):
        # in the orthant, within a box around U plus one outside layer
        hi = max(max(v) for v in U) + 2
        cells = [v for v in itertools.product(range(hi + 1), repeat=3) if v not in U]
        start = (hi, hi, hi)
        seen = {start}
        stack = [start]
        cs = set(cells)
        while stack:
            v = stack.pop()
            for w in nbrs(v):
                if w in cs and w not in seen and max(w) <= hi:
                    seen.add(w)
                    stack.append(w)
        return len(seen) == len(cells)

    spread_violations = 0
    counted = 0
    for centre in ((0, 0, 0), (3, 3, 3)):
        found = {frozenset([centre])}
        frontier = {frozenset([centre])}
        for size in range(2, 6):
            nxt = set()
            for U in frontier:
                for v in U:
                    for w in nbrs(v):
                        if w not in U:
                            nxt.add(U | {w})
            found |= nxt
            frontier = nxt
        for U in found:
            if not complement_connected(U):
                continue
            F = boundary(U)
            anchors = [min(a, b) for a, b in F]
            spread = max(max(abs(p[k] - q[k]) for k in range(3)) for p in anchors for q in anchors)
            counted += 1
            spread_violations += spread > len(F) - 1
    out["enumerated_bonds"] = counted
    out["bonds_with_anchor_spread_above_size_minus_one"] = spread_violations
    return out


def part_whitney():
    out = {}
    for n in (2, 3, 4):
        verts, edges, eid, inc, H = box(n)
        G = nx.MultiGraph()
        for (v, i) in edges:
            w = tuple(v[a] + (a == i) for a in range(3))
            G.add_edge(v, w if max(w) < n else "infinity")
        S = nx.Graph(G)
        out[n] = {"vertices": S.number_of_nodes(), "node_connectivity": nx.node_connectivity(S),
                  "parallel_edges": G.number_of_edges() - S.number_of_edges()}
        print("whitney", n, json.dumps(out[n]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    res = {"grow": part_grow, "grow4": part_grow4, "boxes": part_boxes, "bonds": part_bonds, "whitney": part_whitney}[part]()
    print(json.dumps(res, indent=1, default=str))
