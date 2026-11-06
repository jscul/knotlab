"""Explicit surgery diagrams and twisted cohomology for CLASSK-DICHOTOMY-20261026-001B (any p, r with r | p - 1).

Copied from PATTERN1-CHECKPOINT-20261026-001-E001 pc_core.py (sha256 e540b8c298fb62fe158d765a20755754e928370ca73f1ad71fecc0f356bb01f6) and changed only to take (p, r) from
configure(p, r, zeta) instead of the constants 7, 6, 3: functions read P and R at call time (p may still be passed).

Geometry: every link component is a closed polygon in R^3 (x = strand position, y = height, z = depth towards the viewer).
The diagram is the projection to the xy-plane after a fixed small generic rotation; the over-strand at a crossing is the one
with larger depth. From the diagram: Wirtinger arcs, crossing relators x_j = x_o^-s x_i x_o^s (the convention of cp_lib),
Seifert longitudes, linking numbers, and framing relators mu^f lambda. Twisted cohomology and the Heisenberg lifting obstruction
are computed by Fox calculus mod p with a per-generator value of psi (1 on the base knot, 0 on clasper components).
"""
import itertools
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def find_root():
    for parent in [HERE] + list(HERE.parents):
        if (parent / "proofs" / "COPRIME-CLASS2-20261026-001B").exists():
            return parent
    return Path("/home/jscul/p-vs-np-contact-first")


ROOT = find_root()
sys.path.insert(0, str(next((ROOT / "proofs/COPRIME-CLASS2-20261026-001B").glob("COPRIME-CLASS2-20261026-001B-P001_*"))))
import cp_lib as C  # noqa: E402  (read-only: Group, braid words)

P, R, ZETA = 7, 6, 3            # defaults (F_7, C_6, zeta = 3); change with configure()


def configure(p, r, zeta):
    """set the field, the cyclic group and the chosen generator of mu_r(F_p)"""
    global P, R, ZETA
    assert (p - 1) % r == 0 and pow(zeta, r, p) == 1 and all(pow(zeta, d, p) != 1 for d in range(1, r))
    P, R, ZETA = p, r, zeta
T31, S61, K52 = ([1, 1, 1], 2), ([1, 1, 2, -1, -3, 2, -3], 4), ([1, 1, 1, 2, -1, 2], 3)

# ------------------------------------------------------------------------------------------------ geometry helpers


class Comp:
    def __init__(self, name, pts, psi, framing, role):
        self.name, self.pts, self.psi, self.framing, self.role = name, [tuple(map(float, p)) for p in pts], psi, framing, role


def dedupe(pts):
    out = []
    for p in pts:
        if not out or max(abs(a - b) for a, b in zip(p, out[-1])) > 1e-12:
            out.append(tuple(p))
    if len(out) > 1 and max(abs(a - b) for a, b in zip(out[0], out[-1])) < 1e-12:
        out.pop()
    return out


class BraidLayout:
    """Closure of a braid word on n strands; crossing k occupies [y_k, y_k + 1], then a vertical gap of height gaps[k]."""

    def __init__(self, word, n, gaps=None, H=0.3, CD=0.6, XRET=1.0):
        self.word, self.n = word, n
        gaps = gaps or {}
        self.y = [0.0]
        for k in range(len(word)):
            self.y.append(self.y[k] + 1.0 + gaps.get(k, 1.0))
        self.ytop = self.y[-1]
        self.x = [float(q) for q in range(n)]
        pts, pos, seen = [], 0, set()
        while True:
            seen.add(pos)
            pts.append((self.x[pos], 0.0, 0.0))
            q = pos
            for k, g in enumerate(word):
                i = abs(g) - 1
                if q in (i, i + 1):
                    left = q == i
                    over = (left and g > 0) or ((not left) and g < 0)
                    q2 = i + 1 if left else i
                    pts.append((self.x[q], self.y[k], 0.0))
                    pts.append(((self.x[q] + self.x[q2]) / 2, self.y[k] + 0.5, H if over else -H))
                    pts.append((self.x[q2], self.y[k] + 1.0, 0.0))
                    q = q2
            d = n - q
            xr = self.x[n - 1] + XRET + d * CD
            pts += [(self.x[q], self.ytop, 0.0), (self.x[q], self.ytop + d * CD, 0.0), (xr, self.ytop + d * CD, 0.0),
                    (xr, -d * CD, 0.0), (self.x[q], -d * CD, 0.0)]
            pos = q
            if pos == 0:
                break
        self.is_knot = len(seen) == n
        self.pts = dedupe(pts)

    def gap(self, k):
        """height range of the vertical gap after crossing k"""
        return self.y[k] + 1.0, self.y[k + 1]


def helix(cx, y0, rad, turns, pitch, direction, npt=16, phi0=math.pi):
    """points of a helix around the vertical line x = cx, z = 0, starting at angle phi0, rising pitch per turn"""
    out = []
    steps = max(1, int(round(abs(turns) * npt)))
    for s in range(steps + 1):
        u = s / steps * turns
        phi = phi0 + direction * 2 * math.pi * u
        out.append((cx + rad * math.cos(phi), y0 + pitch * u, rad * math.sin(phi)))
    return out


# leaf geometry constants (strand spacing is 1)
RHO, HL, EPS, RW, PITCH, MARG = 0.25, 0.2, 0.05, 0.45, 0.4, 0.12
XSP, XRAIL = -0.55, -0.8          # spine and rail, relative to strand a


def copy_loop(xa, yc):
    """band loop around a (at xa) and b (at xa + 1) at height yc, from the upper attachment to the lower attachment"""
    xb = xa + 1.0
    att = xa - RHO - 0.05
    return [(att, yc + EPS, 0.0), (xa - RHO, yc + EPS, -HL), (xa + RHO, yc + EPS, -HL), (xb - RHO, yc + EPS, HL),
            (xb + RHO, yc + EPS, HL), (xb + RHO + 0.1, yc, 0.0), (xb + RHO, yc - EPS, -HL), (xb - RHO, yc - EPS, -HL),
            (xa + RHO, yc - EPS, HL), (xa - RHO, yc - EPS, HL), (att, yc - EPS, 0.0)]


def tooth_centerline(xa, s_c, j, wdir):
    """from the spine at height s_c: right to the helix start, j turns around strand a (direction wdir), right to the copy"""
    pts = [(xa + XSP, s_c, 0.0)]
    if j:
        pts += helix(xa, s_c, RW, j, PITCH, wdir)
    else:
        pts.append((xa - RW, s_c, 0.0))
    yc = s_c + j * PITCH
    pts.append((xa - RHO - 0.05, yc, 0.0))
    return pts, yc


def projector_leaf(xa, ytop, mult, wdir, cut=None):
    """comb: spine down from the root, one tooth per copy (copies grouped by j with multiplicity mult[j]), rail back up.
    Returns (points starting at the root-segment midpoint, bottom height, info). If cut is a height on the rail, the polygon
    is returned as a path from (rail, cut - EPS) around to (rail, cut + EPS) instead (for band sums)."""
    copies = [j for j in range(len(mult)) for _ in range(mult[j])]
    yroot = ytop
    teeth, t = [], ytop - 0.6
    for j in copies:
        yc = t - MARG - EPS
        s_c = yc - j * PITCH
        teeth.append((j, s_c))
        t = s_c - EPS - MARG
    ybot = t - 0.3
    xs, xr = xa + XSP, xa + XRAIL
    body = [((xr + xs) / 2, yroot, 0.0), (xs, yroot, 0.0)]
    for j, s_c in teeth:
        cl, yc = tooth_centerline(xa, s_c, j, wdir)
        out_edge = [(x, y + EPS, z) for x, y, z in cl]
        back_edge = [(x, y - EPS, z) for x, y, z in reversed(cl)]
        body += out_edge + copy_loop(xa, yc) + back_edge
    body += [(xs, ybot, 0.0), (xr, ybot, 0.0)]
    if cut is None:
        body += [(xr, yroot, 0.0)]
        return dedupe(body), ybot, {"copies": len(copies), "yroot": yroot, "root_mid": ((xr + xs) / 2, yroot)}
    # path from (xr, cut - EPS) going up the rail, round the root, down the spine ... back up the rail to (xr, cut + EPS)
    assert ybot < cut - EPS and cut + EPS < yroot
    path = [(xr, cut + EPS, 0.0), (xr, yroot, 0.0)] + body + [(xr, cut - EPS, 0.0)]
    return dedupe_path(path), ybot, {"copies": len(copies), "yroot": yroot, "root_mid": ((xr + xs) / 2, yroot)}


def dedupe_path(pts):
    out = []
    for p in pts:
        if not out or max(abs(a - b) for a, b in zip(p, out[-1])) > 1e-12:
            out.append(tuple(p))
    return out


def ribbon(path, eps, normal=(0.0, 1.0, 0.0)):
    """two edges of a thin band along a path, offset by +-eps along a fixed normal"""
    nx, ny, nz = normal
    a = [(x + eps * nx, y + eps * ny, z + eps * nz) for x, y, z in path]
    b = [(x - eps * nx, y - eps * ny, z - eps * nz) for x, y, z in path]
    return a, b


# ------------------------------------------------------------------------------------------------ diagrams

ROT = None


def rotation():
    ax, ay, az = 0.0137, 0.0219, 0.0071
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class Diagram:
    """crossings, arcs, presentation of the link complement, longitudes, linking numbers"""

    def __init__(self, comps, min_dz=0.01, cell=0.5):
        self.comps = comps
        Rm = rotation()
        segs, owner = [], []
        self.seg_start = []
        for ci, c in enumerate(comps):
            pts = np.array(c.pts) @ Rm.T
            n = len(pts)
            self.seg_start.append(len(segs))
            for k in range(n):
                segs.append((pts[k], pts[(k + 1) % n]))
                owner.append((ci, k, n))
        self.nseg = len(segs)
        A = np.array([s[0] for s in segs])
        B = np.array([s[1] for s in segs])
        self.A, self.B, self.owner = A, B, owner
        # grid hashing in the projection
        lo = np.minimum(A[:, :2], B[:, :2])
        hi = np.maximum(A[:, :2], B[:, :2])
        cells = {}
        for s in range(len(segs)):
            for gx in range(int(math.floor(lo[s, 0] / cell)), int(math.floor(hi[s, 0] / cell)) + 1):
                for gy in range(int(math.floor(lo[s, 1] / cell)), int(math.floor(hi[s, 1] / cell)) + 1):
                    cells.setdefault((gx, gy), []).append(s)
        pairs = set()
        for lst in cells.values():
            if len(lst) > 1:
                for i in range(len(lst)):
                    for j in range(i + 1, len(lst)):
                        pairs.add((lst[i], lst[j]) if lst[i] < lst[j] else (lst[j], lst[i]))
        pairs = np.array(sorted(pairs), dtype=np.int64).reshape(-1, 2)
        # drop adjacent segments of one component
        ci_ = np.array([o[0] for o in owner])
        k_ = np.array([o[1] for o in owner])
        n_ = np.array([o[2] for o in owner])
        i, j = pairs[:, 0], pairs[:, 1]
        same = ci_[i] == ci_[j]
        adj = same & (((k_[i] + 1) % n_[i] == k_[j]) | ((k_[j] + 1) % n_[j] == k_[i]))
        pairs = pairs[~adj]
        i, j = pairs[:, 0], pairs[:, 1]
        p, r = A[i, :2], B[i, :2] - A[i, :2]
        q, s = A[j, :2], B[j, :2] - A[j, :2]
        den = r[:, 0] * s[:, 1] - r[:, 1] * s[:, 0]
        qp = q - p
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (qp[:, 0] * s[:, 1] - qp[:, 1] * s[:, 0]) / den
            u = (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / den
        tol = 1e-9
        hit = (np.abs(den) > 1e-14) & (t > tol) & (t < 1 - tol) & (u > tol) & (u < 1 - tol)
        near_end = (np.abs(den) > 1e-14) & (((t > -1e-7) & (t <= tol)) | ((t >= 1 - tol) & (t < 1 + 1e-7)) |
                                            ((u > -1e-7) & (u <= tol)) | ((u >= 1 - tol) & (u < 1 + 1e-7))) & \
            (t > -1e-7) & (t < 1 + 1e-7) & (u > -1e-7) & (u < 1 + 1e-7)
        assert not near_end.any(), "degenerate crossing at a vertex; change the rotation"
        i, j, t, u = i[hit], j[hit], t[hit], u[hit]
        zi = A[i, 2] + t * (B[i, 2] - A[i, 2])
        zj = A[j, 2] + u * (B[j, 2] - A[j, 2])
        dz = zi - zj
        self.min_dz = float(np.min(np.abs(dz))) if len(dz) else float("inf")
        assert self.min_dz > min_dz, f"curves too close at a crossing (|dz| = {self.min_dz})"
        over_i = dz > 0
        so = np.where(over_i, i, j)
        su = np.where(over_i, j, i)
        to = np.where(over_i, t, u)
        tu = np.where(over_i, u, t)
        do = B[so, :2] - A[so, :2]
        du = B[su, :2] - A[su, :2]
        sign = np.sign(do[:, 0] * du[:, 1] - do[:, 1] * du[:, 0]).astype(int)
        self.crossings = list(zip(so.tolist(), to.tolist(), su.tolist(), tu.tolist(), sign.tolist()))
        self._build()

    def _build(self):
        comps = self.comps
        ev = {ci: [] for ci in range(len(comps))}           # component -> [(pos, crossing id, 'o'|'u')]
        for x, (so, to, su, tu, s) in enumerate(self.crossings):
            co, ko, _ = self.owner[so]
            cu, ku, _ = self.owner[su]
            ev[co].append((ko + to, x, "o"))
            ev[cu].append((ku + tu, x, "u"))
        self.gens = []                                     # (component, arc index)
        self.arc_of = {}                                   # (component, arc index) -> generator
        self.events = {}
        under_in, under_out, over_arc = {}, {}, {}
        for ci in range(len(comps)):
            evs = sorted(ev[ci])
            self.events[ci] = evs
            unders = [k for k, e in enumerate(evs) if e[2] == "u"]
            nu = len(unders)
            base = len(self.gens)
            narcs = max(nu, 1)
            for a in range(narcs):
                self.gens.append((ci, a))
            # arc index of position: arcs start right after under event k (arc k+1 mod nu ... ) ; arc 0 contains the start
            # walking from position 0: arc 0 until the first under event, then arc 1, ...; last arc wraps to 0
            cur = 0
            for k, (pos, x, kind) in enumerate(evs):
                if kind == "u":
                    under_in[x] = base + (cur % narcs)
                    cur += 1
                    under_out[x] = base + (cur % narcs)
                else:
                    over_arc[x] = base + (cur % narcs)
            self.arc_of[ci] = (base, narcs)
        self.under_in, self.under_out, self.over_arc = under_in, under_out, over_arc
        self.psi = [comps[ci].psi for ci, _ in self.gens]
        rels = []
        for x, (so, to, su, tu, s) in enumerate(self.crossings):
            o, i, j = over_arc[x], under_in[x], under_out[x]
            rels.append([(o, -s), (i, 1), (o, s), (j, -1)])
        self.crossing_rels = rels
        # linking numbers and writhes
        nc = len(comps)
        L = np.zeros((nc, nc), dtype=np.int64)
        W = [0] * nc
        for x, (so, to, su, tu, s) in enumerate(self.crossings):
            co, cu = self.owner[so][0], self.owner[su][0]
            if co == cu:
                W[co] += s
            else:
                L[co, cu] += s
                L[cu, co] += s
        assert np.all(L % 2 == 0)
        self.lk = L // 2
        self.writhe = W
        # longitudes (Seifert), read from position 0 of each component
        self.mu = {}
        self.lam = {}
        for ci in range(nc):
            base, narcs = self.arc_of[ci]
            self.mu[ci] = base                       # arc 0 contains position 0
            word = [(over_arc[x], s) for (pos, x, kind) in self.events[ci] if kind == "u"
                    for s in [self.crossings[x][4]]]
            w = W[ci]
            word += [(base, -1)] * w if w >= 0 else [(base, 1)] * (-w)
            self.lam[ci] = word

    def framing_rels(self, framings=None):
        out = []
        for ci, c in enumerate(self.comps):
            f = c.framing if framings is None else framings[ci]
            if f is None:
                continue
            m = self.mu[ci]
            out.append(([(m, 1)] * f if f >= 0 else [(m, -1)] * (-f)) + self.lam[ci])
        return out

    def locate(self, ci, point, tol=1e-6):
        """generator of the arc of component ci containing a point of its polygon (unrotated coordinates)"""
        pts = self.comps[ci].pts
        n = len(pts)
        best = None
        for k in range(n):
            a, b = np.array(pts[k]), np.array(pts[(k + 1) % n])
            d = b - a
            L2 = float(d @ d)
            if L2 == 0:
                continue
            t = float((np.array(point) - a) @ d / L2)
            if -1e-9 <= t <= 1 + 1e-9:
                dist = float(np.linalg.norm(a + t * d - np.array(point)))
                if dist < tol:
                    best = k + t
                    break
        assert best is not None, "point not on the component"
        base, narcs = self.arc_of[ci]
        cur = 0
        for pos, x, kind in self.events[ci]:
            if pos > best:
                break
            if kind == "u":
                cur += 1
        return base + (cur % narcs)


# ------------------------------------------------------------------------------------------------ linear algebra mod p

def rref_mod(M, p=None):
    p = P if p is None else p
    A = np.array(M, dtype=np.int64) % p
    m, n = A.shape
    piv, r = [], 0
    for c in range(n):
        if r == m:
            break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + int(nz[0])
        if k != r:
            A[[r, k]] = A[[k, r]]
        A[r] = (A[r] * pow(int(A[r, c]), p - 2, p)) % p
        rows = np.nonzero(A[:, c])[0]
        rows = rows[rows != r]
        if len(rows):
            A[rows] = (A[rows] - A[rows, c][:, None] * A[r]) % p
        piv.append(c)
        r += 1
    return A[:r], piv


def nullspace_mod(M, n, p=None):
    p = P if p is None else p
    if len(M) == 0:
        return np.eye(n, dtype=np.int64)
    Rr, piv = rref_mod(M, p)
    free = [j for j in range(n) if j not in set(piv)]
    out = np.zeros((len(free), n), dtype=np.int64)
    for k, f in enumerate(free):
        out[k, f] = 1
        for row, c in zip(Rr, piv):
            out[k, c] = (-row[f]) % p
    return out


def rank_mod(M, p=None):
    p = P if p is None else p
    if len(M) == 0:
        return 0
    return len(rref_mod(M, p)[0])


class Reducer:
    def __init__(self, vectors, p=None):
        p = P if p is None else p
        self.p = p
        if len(vectors):
            self.R, self.piv = rref_mod(vectors, p)
        else:
            self.R, self.piv = np.zeros((0, 0), dtype=np.int64), []

    def reduce(self, v):
        v = np.array(v, dtype=np.int64) % self.p
        if len(self.piv):
            v = (v - v[self.piv] @ self.R) % self.p
        return tuple(int(x) for x in v)


# ------------------------------------------------------------------------------------------------ twisted cohomology

def fox_matrix(ngen, rels, psi, chi, p=None):
    p = P if p is None else p
    M = np.zeros((len(rels), ngen), dtype=np.int64)
    act = [pow(chi, int(psi[g]) % R, p) for g in range(ngen)]
    inv = [pow(a, p - 2, p) for a in act]
    for r, rel in enumerate(rels):
        pref = 1
        row = M[r]
        for g, s in rel:
            for _ in range(abs(s)):
                if s > 0:
                    row[g] = (row[g] + pref) % p
                    pref = pref * act[g] % p
                else:
                    pref = pref * inv[g] % p
                    row[g] = (row[g] - pref) % p
    return M


def cohomology(ngen, rels, psi, chi, p=None):
    """(H1 basis as cocycle vectors complementing the coboundaries, dim Z1, dim B1)"""
    p = P if p is None else p
    Z = nullspace_mod(fox_matrix(ngen, rels, psi, chi, p), ngen, p)
    b = np.array([(pow(chi, int(psi[g]) % R, p) - 1) % p for g in range(ngen)], dtype=np.int64)
    basis = [b] if b.any() else []
    H = []
    for z in Z:
        if rank_mod(np.array(basis + [z]), p) > len(basis):
            basis.append(z)
            H.append(z)
    return [np.array(h) for h in H], len(Z), (1 if b.any() else 0)


def evaluate(word, values, psi, chi, p=None):
    """c(word) for a cocycle with values c(x_g) (left action: c(gh) = c(g) + chi^psi(g) c(h))"""
    p = P if p is None else p
    tot, pref = 0, 1
    for g, s in word:
        a = pow(chi, int(psi[g]) % R, p)
        for _ in range(abs(s)):
            if s > 0:
                tot = (tot + pref * int(values[g])) % p
                pref = pref * a % p
            else:
                pref = pref * pow(a, p - 2, p) % p
                tot = (tot - pref * int(values[g])) % p
    return tot


def obstruction_bimap(ngen, rels, psi, a, b, Hx, Hy, p=None, k=1, red=None):
    """canonical classes of c_x u c_y for the Heisenberg group H(F_p) x| C_r with h -> (a x, b y, ab z); red: an optional
    precomputed Reducer for the coboundary image of the character ab (added in this copy, to reuse it across pairs)"""
    p = P if p is None else p
    G = C.Group(p, R, a, b)
    if red is None:
        Dz = fox_matrix(ngen, rels, psi, a * b % p, p)
        red = Reducer(Dz.T, p)
    out = {}
    for i, hx in enumerate(Hx):
        for j, hy in enumerate(Hy):
            imgs = [(int(hx[g]), int(hy[g]), 0, (k * int(psi[g])) % R) for g in range(ngen)]
            q = []
            for rel in rels:
                X, Y, Zc, e = G.word(rel, imgs)
                assert X == 0 and Y == 0 and e == 0, "not a cocycle or psi not well defined"
                q.append(Zc)
            out[(i, j)] = red.reduce(q)
    return out


def counts_from_bimaps(B12, B13, B23, d1, d2, d3, p=None):
    """N_free3 = #{(c1, c2, c3) : c1 u c2 = 0, c1 u c3 = 0, c2 u c3 = 0}, and the three single-component counts"""
    p = P if p is None else p
    def lin(B, a, bvec, da, db):
        L = len(next(iter(B.values()))) if B else 0
        v = [0] * L
        for i in range(da):
            if a[i]:
                for j in range(db):
                    if bvec[j]:
                        f = a[i] * bvec[j] % p
                        v = [(x + f * y) % p for x, y in zip(v, B[(i, j)])]
        return v

    def kdim(cols, n):
        if not cols or not cols[0]:
            return n
        rows = [[cols[j][t] for j in range(n)] for t in range(len(cols[0]))]
        return n - rank_mod(np.array(rows), p)

    unit = lambda l, d: [int(l == t) for t in range(d)]
    out = {"free3": 0, "H12": 0, "H13": 0, "H23": 0}
    for c1 in itertools.product(range(p), repeat=d1):
        out["H12"] += p ** kdim([lin(B12, c1, unit(j, d2), d1, d2) for j in range(d2)], d2) if d2 else 1
        out["H13"] += p ** kdim([lin(B13, c1, unit(l, d3), d1, d3) for l in range(d3)], d3) if d3 else 1
        for c2 in itertools.product(range(p), repeat=d2):
            if any(lin(B12, c1, c2, d1, d2)):
                continue
            cols = [lin(B13, c1, unit(l, d3), d1, d3) + lin(B23, c2, unit(l, d3), d2, d3) for l in range(d3)]
            out["free3"] += p ** kdim(cols, d3) if d3 else 1
    for c2 in itertools.product(range(p), repeat=d2):
        out["H23"] += p ** kdim([lin(B23, c2, unit(l, d3), d2, d3) for l in range(d3)], d3) if d3 else 1
    return out


def smith_diagonal(M):
    """invariant factors of an integer matrix (small)"""
    A = [list(map(int, row)) for row in M]
    m, n = len(A), len(A[0]) if A else 0
    diag = []
    r = 0
    for c in range(min(m, n)):
        # find the smallest nonzero entry in the submatrix
        while True:
            best = None
            for i in range(r, m):
                for j in range(r, n):
                    if A[i][j] and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                        best = (i, j)
            if best is None:
                return diag + [0] * (min(m, n) - r)
            i, j = best
            A[r], A[i] = A[i], A[r]
            for row in A:
                row[r], row[j] = row[j], row[r]
            piv = A[r][r]
            done = True
            for i in range(r + 1, m):
                f = A[i][r] // piv
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
                if A[i][r]:
                    done = False
            for j in range(r + 1, n):
                f = A[r][j] // piv
                for i in range(m):
                    A[i][j] -= f * A[i][r]
                if A[r][j]:
                    done = False
            if done:
                bad = any(A[i][j] % piv for i in range(r + 1, m) for j in range(r + 1, n))
                if bad:
                    for j in range(r + 1, n):
                        if any(A[i][j] % piv for i in range(r + 1, m)):
                            for i in range(m):
                                A[i][r] += A[i][j]
                            break
                    continue
                diag.append(abs(piv))
                r += 1
                break
    return diag
