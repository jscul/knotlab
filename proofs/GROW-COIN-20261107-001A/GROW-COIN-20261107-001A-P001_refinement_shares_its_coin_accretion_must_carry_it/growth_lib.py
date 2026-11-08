"""Refinement shares its coin, accretion must carry it, for GROW-COIN-20261107-001A.

Spheres are the two-kind knot spheres of SPHERE-GROWTH-20261107-001A (co-lines of two or three points, T-degree 4 or 6); K_m is the
octahedral knot sphere. Two ways to grow them:

- Refinement: `subdivide(tris, j)` splits every triangle into j * j, with the points on an edge shared by its two triangles.
- Accretion by rings around a corner: `Growth` starts from a corner (four triangles) and adds whole annuli. Each ring vertex is
  completed to degree 6, except convex turns (two triangles so far) that are chosen as corners (degree 4). `grow(choose)` runs it
  with a choice function; `enumerate_closed` tries every choice pattern up to a size.
- Single-strip accretion: `ring_order` and `greedy_grow` add K_m's triangles one at a time, annulus after annulus in angular order,
  recording the boundary word of triangle counts before each move (ADD: a triangle on one boundary edge with a new vertex; CAP: a
  triangle on two consecutive boundary edges; FINAL: the last triangle)."""
import copy
import itertools
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SPHERE-GROWTH-20261107-001A/SPHERE-GROWTH-20261107-001A-P001_round_spheres_need_one_hidden_bit"))
import seam_lib as SM  # noqa: E402
SL = SM.SL


def is_K(S):
    return any(SM.isomorphic(SL.octahedral_sphere(m), S) for m in range(1, 80) if 8 * m * m == S.nt)


def two_kind_sphere(S):
    return S.validate() and S.euler() == 2 and set(SM.degrees(S)) <= {4, 6}


# ------------------------------------------------------------------------------------------------ refinement
def subdivide(tris, j):
    """split every triangle (P, Q, R) into j * j by barycentric points a + b + c = j; a point on an edge is named by its edge
    and position, so the two triangles of the edge share it"""
    def pt(t, a, b, c):
        P, Q, R = t
        if a == j:
            return P
        if b == j:
            return Q
        if c == j:
            return R
        if c == 0:
            return ("e", frozenset(((P, a), (Q, b))))
        if b == 0:
            return ("e", frozenset(((P, a), (R, c))))
        if a == 0:
            return ("e", frozenset(((Q, b), (R, c))))
        return ("i", t, a, b, c)
    out = []
    for t in tris:
        for a in range(j):
            for b in range(j - a):
                c = j - 1 - a - b
                out.append((pt(t, a + 1, b, c), pt(t, a, b + 1, c), pt(t, a, b, c + 1)))
        for a in range(j - 1):
            for b in range(j - 1 - a):
                c = j - 2 - a - b
                out.append((pt(t, a, b + 1, c + 1), pt(t, a + 1, b, c + 1), pt(t, a + 1, b + 1, c)))
    return out


# ------------------------------------------------------------------------------------------------ accretion by whole annuli
class Growth:
    """a disc grown by annuli around a corner c; `k` counts triangles at each ring vertex"""

    def __init__(self):
        self.tris = [("c", 0, 1), ("c", 1, 2), ("c", 2, 3), ("c", 3, 0)]
        self.ring = [0, 1, 2, 3]
        self.k = Counter({0: 2, 1: 2, 2: 2, 3: 2})
        self.n = 4

    def new(self):
        self.n += 1
        return self.n - 1

    def add(self, t):
        self.tris.append(t)
        for x in t:
            self.k[x] += 1

    def turns(self):
        return [v for v in self.ring if self.k[v] == 2]

    def annulus(self, corners):
        """complete every ring vertex: to 4 if it is in `corners` (a convex turn), else to 6"""
        R = list(self.ring)
        target = {v: (4 if v in corners else 6) for v in R}
        if any(self.k[v] != 2 for v in corners):
            raise ValueError("a corner must be a convex turn")
        need = {v: target[v] - self.k[v] for v in R}
        if any(x < 1 for x in need.values()):
            raise ValueError("over degree")
        changed = True
        while changed and len(R) > 3:                      # a vertex needing one triangle closes by joining its neighbours
            changed = False
            for i, v in enumerate(R):
                if need[v] == 1:
                    a, b = R[i - 1], R[(i + 1) % len(R)]
                    self.add((a, v, b))
                    need[a] -= 1
                    need[b] -= 1
                    R.pop(i)
                    changed = True
                    break
        if len(R) == 3:
            if all(need[v] == 1 for v in R):
                self.add(tuple(R))
                self.ring = []
                return
            raise ValueError("stuck at three")
        if len(R) == 4 and all(need[v] == 2 for v in R):    # the last corner
            t = self.new()
            for i in range(4):
                self.add((R[i], R[(i + 1) % 4], t))
            self.ring = []
            return
        if any(x < 2 for x in need.values()):
            raise ValueError("stuck")
        L = len(R)
        twos = [i for i in range(L) if need[R[i]] == 2 and need[R[i - 1]] != 2]
        if twos:
            R = R[twos[0]:] + R[:twos[0]]
        elif all(need[v] == 2 for v in R):
            raise ValueError("all corners")
        first = prev = None
        for i, v in enumerate(R):
            j = need[v]
            left = prev if prev is not None else self.new()
            if first is None:
                first = left
            mids = [self.new() for _ in range(j - 3)] if j >= 3 else []
            if j == 2:
                right = left
                if i == L - 1 and left != first:
                    raise ValueError("wrap mismatch")
            elif i == L - 1:
                right = first
            else:
                right = self.new()
            fan = [left] + mids + ([right] if right != left else [])
            for t in range(len(fan) - 1):
                self.add((v, fan[t], fan[t + 1]))
            self.add((v, R[(i + 1) % L], right))
            prev = right
        self.ring = self._boundary()

    def _boundary(self):
        edges = Counter()
        for t in self.tris:
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                edges[frozenset((a, b))] += 1
        nb = defaultdict(list)
        for e, c in edges.items():
            if c == 1:
                a, b = tuple(e)
                nb[a].append(b)
                nb[b].append(a)
        if not nb:
            return []
        if any(len(x) != 2 for x in nb.values()):
            raise ValueError("pinched boundary")
        start = next(iter(nb))
        ring, prev, cur = [start], None, start
        while True:
            nx = [x for x in nb[cur] if x != prev][0]
            if nx == start:
                return ring
            ring.append(nx)
            prev, cur = cur, nx


def grow(choose, maxrings=80):
    """choose(r, G, turns) -> the turns of ring r made corners"""
    G = Growth()
    for r in range(maxrings):
        if not G.ring:
            return G, "closed"
        try:
            G.annulus(set(choose(r, G, G.turns())))
        except ValueError:
            return G, "stuck"
    return G, "too big"


def uniform(m):
    """the four turns of ring m - 1 (at distance m from c) become corners, nothing else"""
    return grow(lambda r, G, cv: cv if r == m - 1 else [])


def enumerate_closed(max_tris, max_depth=14):
    """every choice pattern (any subset of the turns at each annulus) until closed, stuck or larger than max_tris; returns
    the closed spheres with their patterns"""
    out = []

    def rec(G, depth, pattern):
        if not G.ring:
            out.append((SM.from_triangles("g", G.tris), pattern))
            return
        if len(G.tris) > max_tris or depth > max_depth:
            return
        cv = G.turns()
        for r in range(len(cv) + 1):
            for sub in itertools.combinations(cv, r):
                H = copy.deepcopy(G)
                try:
                    H.annulus(set(sub))
                except ValueError:
                    continue
                rec(H, depth + 1, pattern + ((depth, len(sub), len(cv)),))
    rec(Growth(), 0, ())
    return out


def distinct(spheres):
    reps = []
    for S in spheres:
        if not any(R.nt == S.nt and SM.isomorphic(S, R) for R in reps):
            reps.append(S)
    return reps


# ------------------------------------------------------------------------------------------------ single-strip accretion
class Disc:
    """a disc grown one triangle at a time; B is the boundary cycle, k the triangle counts"""

    def __init__(self, tri):
        self.tris = [tuple(tri)]
        self.k = Counter(tri)
        self.B = list(tri)

    def attachable(self, t):
        pos = {v: i for i, v in enumerate(self.B)}
        L = len(self.B)
        on = [v for v in t if v in pos]
        new = [v for v in t if v not in pos]
        if len(on) == 2 and len(new) == 1 and new[0] not in self.k:
            i, j = pos[on[0]], pos[on[1]]
            return (i + 1) % L == j or (j + 1) % L == i
        if len(on) == 3:
            return L == 3 or any({self.B[pos[x] - 1], self.B[(pos[x] + 1) % L]} == set(on) - {x} for x in on)
        return False

    def attach(self, t):
        pos = {v: i for i, v in enumerate(self.B)}
        L = len(self.B)
        on = [v for v in t if v in pos]
        new = [v for v in t if v not in pos]
        for v in t:
            self.k[v] += 1
        self.tris.append(tuple(t))
        if len(on) == 2:
            i, j = pos[on[0]], pos[on[1]]
            idx = i if (i + 1) % L == j else j
            self.B.insert(idx + 1, new[0])
            return "ADD", idx
        if L == 3:
            self.B = []
            return "FINAL", 0
        for x in on:
            i = pos[x]
            if {self.B[i - 1], self.B[(i + 1) % L]} == set(on) - {x}:
                self.B.pop(i)
                return "CAP", i
        raise ValueError("bad attachment")


def ring_order(m):
    """K_m's triangles (coordinates |x| + |y| + |z| = m) by annulus around the corner (0, 0, -m), then by angle from +x"""
    S = SM.octahedral(m)

    def key(t):
        d = min(v[2] for v in t) + m
        th = math.atan2(sum(v[1] for v in t) / 3, sum(v[0] for v in t) / 3) % (2 * math.pi)
        return (d, th)
    return sorted(S.vtris, key=key), S


def greedy_grow(order):
    """attach in order, each time the first remaining triangle that can attach; log (move, index, word before, triangle)"""
    rest = list(order[1:])
    D = Disc(order[0])
    log = []
    while rest:
        i = next(i for i, t in enumerate(rest) if D.attachable(t))
        t = rest.pop(i)
        word = tuple(D.k[v] for v in D.B)
        Bv = list(D.B)
        kind, idx = D.attach(t)
        log.append((kind, idx, word, Bv, t))
    return D, log


def window(word, i, w):
    L = len(word)
    return tuple(word[(i + j) % L] for j in range(-w, w + 1))


def turn_decisions(m, w):
    """for each ring vertex of K_m's single-strip growth that is a convex turn when its annulus starts (except the turn where the
    annulus starts), the radius-w boundary window centred on it at the moment it is decided (it has three triangles and its left
    boundary neighbour two), with the decision: 'corner' if it is next closed at degree 4, 'flat' if it next gets an ADD"""
    order, S = ring_order(m)
    D, log = greedy_grow(order)
    ring = {v: v[2] + m for t in S.vtris for v in t}
    out = []
    for step, (kind, idx, word, Bv, t) in enumerate(log):
        L = len(word)
        for i, v in enumerate(Bv):
            if word[i] != 3 or word[i - 1] != 2 or ring[Bv[i - 1]] != ring[v] + 1:
                continue
            if v[0] != 0 and v[1] != 0:                  # turns lie on the four rays x = 0 or y = 0
                continue
            if v[1] == 0 and v[0] > 0:                    # the turn where annuli start
                continue
            if kind == "CAP" and idx == i:
                out.append((ring[v], "corner", window(word, i, w)))
            elif kind == "ADD" and idx == i - 1:
                out.append((ring[v], "flat", window(word, i, w)))
    return out


# ------------------------------------------------------------------------------------------------ a label-free window law
def edge_window(word, i, w):
    L = len(word)
    return tuple(word[(i + j) % L] for j in range(-w + 1, w + 1))


def window_law(ms, w):
    """every (window, move) seen in the single-strip growths of K_m, m in ms: CAP by the window centred on the vertex, ADD by
    the window centred on the edge, FINAL by the last three counts"""
    law = set()
    for m in ms:
        order, S = ring_order(m)
        D, log = greedy_grow(order)
        for kind, idx, word, Bv, t in log:
            if kind == "CAP":
                law.add(("V",) + window(word, idx, w))
            elif kind == "ADD":
                law.add(("E",) + edge_window(word, idx, w))
            else:
                law.add(("F",) + tuple(sorted(word)))
    return law


def legal(D, law, w):
    word = [D.k[v] for v in D.B]
    L = len(word)
    if L == 3 and ("F",) + tuple(sorted(word)) in law and all(x + 1 in (4, 6) for x in word):
        return [("FINAL", 0)]
    out = []
    for i in range(L):
        if L > 3 and word[i] + 1 in (4, 6) and ("V",) + window(word, i, w) in law:
            out.append(("CAP", i))
        if ("E",) + edge_window(word, i, w) in law:
            out.append(("ADD", i))
    return out


def random_order_run(law, w, rng, maxt=3000):
    """from one triangle, take a uniformly random legal move until closed or stuck"""
    D = Disc((0, 1, 2))
    fresh = 3
    while D.B:
        mv = legal(D, law, w)
        if not mv:
            return D, "stuck"
        kind, i = rng.choice(mv)
        L = len(D.B)
        if kind == "ADD":
            D.attach((D.B[i], D.B[(i + 1) % L], fresh))
            fresh += 1
        elif kind == "CAP":
            D.attach((D.B[i - 1], D.B[i], D.B[(i + 1) % L]))
        else:
            D.attach(tuple(D.B))
        if len(D.tris) > maxt:
            return D, "too big"
    return D, "closed"
