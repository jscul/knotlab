"""Library for WEAVE-PAIR-20261118-001B-E001: the 3 x 1 weave pair with the twist set explicitly.

The weave: distinctions v(i, j), column i around a cylinder of width w, row j along it.  Up knot U(i, j) on (v(i,j), v(i+1,j),
v(i,j+1)); down knot D(i, j) on (v(i+1,j), v(i,j+1), v(i+1,j+1)); code k in P = (000, 100, 010, 001) excludes {P[k], its
complement} (WEAVE-MIX-20261117-001's encoding).  The twist: every knot crossing the seam (column w - 1 to column 0) reads the
column-0 values flipped.  The knots are closed under the global flip in both sectors, so the transfer splits into flip-even and
flip-odd parts.

The row transfer M[a, b] = 1 when rows a then b satisfy every knot between them.  u = M v is applied site by site, replacing the
bits of b by those of a from column w - 1 down to 0, with one extra bit holding b's last column for the seam."""
import numpy as np
import scipy.sparse.linalg as sla

P = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]


def bad(code, x, y, z):
    p = P[code]
    hit = (x == p[0]) & (y == p[1]) & (z == p[2])
    return hit | ((x == 1 - p[0]) & (y == 1 - p[1]) & (z == 1 - p[2]))


def codes(arr, w):
    return [arr[(i % 3, "U")] for i in range(w)], [arr[(i % 3, "D")] for i in range(w)]


def dense_transfer(w, arr, twist):
    """M[a, b] for w <= 12."""
    R = 1 << w
    bits = (np.arange(R)[:, None] >> np.arange(w)[None, :]) & 1
    U, D = codes(arr, w)
    ok = np.ones((R, R), dtype=bool)
    for i in range(w):
        j = (i + 1) % w
        seam = twist and i == w - 1
        ai, aj = bits[:, i][:, None], bits[:, j][:, None]
        bi, bj = bits[:, i][None, :], bits[:, j][None, :]
        if seam:
            aj, bj = 1 - aj, 1 - bj
        ok &= ~bad(U[i], ai, aj, bi)
        ok &= ~bad(D[i], aj, bi, bj)
    return ok.astype(np.float64)


class SiteTransfer:
    """u = M v, site by site.  State bits 0..w-1 are the row (b, then a as they are replaced) and bit w holds b_{w-1}."""

    def __init__(self, w, arr, twist):
        self.w, self.twist = w, twist
        self.U, self.D = codes(arr, w)
        S = 1 << (w + 1)
        idx = np.arange(S)
        self.bit = lambda k: (idx >> k) & 1
        self.S = S
        self.idx = idx
        self.masks = []
        for i in range(w - 1, -1, -1):
            row = {}
            for ai in (0, 1):
                for bi in (0, 1):
                    allowed = np.ones(S, dtype=bool)
                    if i < w - 1:
                        allowed &= ~bad(self.U[i], ai, self.bit(i + 1), bi)                 # U(i): (a_i, a_{i+1}, b_i)
                    if i >= 1:
                        allowed &= ~bad(self.D[i - 1], ai, self.bit(i - 1), bi)             # D(i-1): (a_i, b_{i-1}, b_i)
                    if i == 0:
                        e = self.bit(w)
                        a_last = self.bit(w - 1)
                        a0 = 1 - ai if twist else ai
                        b0 = 1 - bi if twist else bi
                        allowed &= ~bad(self.U[w - 1], a_last, a0, e)                       # U(w-1): (a_{w-1}, a_0, b_{w-1})
                        allowed &= ~bad(self.D[w - 1], a0, e, b0)                           # D(w-1): (a_0, b_{w-1}, b_0)
                    row[(ai, bi)] = allowed
            self.masks.append((i, row))

    def matvec(self, v):
        w, S = self.w, self.S
        v = np.asarray(v, dtype=np.float64).reshape(-1)
        b_last = (np.arange(1 << w) >> (w - 1)) & 1
        x = np.zeros(S)
        x[np.arange(1 << w) | (b_last << w)] = v
        for i, row in self.masks:
            shape = (S >> (i + 1), 2, 1 << i)            # axis 1 is bit i
            xr = x.reshape(shape)
            y = np.empty(shape)
            for ai in (0, 1):
                acc = np.zeros((shape[0], shape[2]))
                for bi in (0, 1):
                    m = row[(ai, bi)].reshape(shape)[:, bi, :]   # the masks do not depend on bit i itself
                    acc += xr[:, bi, :] * m
                y[:, ai, :] = acc
            x = y.reshape(S)
        return x[: 1 << w] + x[1 << w:]


def sector_gaps(w, arr, twist, k=6):
    """Top flip-even eigenvalue, second flip-even and top flip-odd, in log base 3 per row; states per distinction."""
    n = 1 << w
    full = n - 1
    flip = np.arange(n) ^ full
    if w <= 12:
        M = dense_transfer(w, arr, twist)
        mv = lambda v: M @ v
    else:
        T = SiteTransfer(w, arr, twist)
        mv = T.matvec
    out = {"width": w, "twist": twist}
    tops = {}
    for name, sgn in (("even", 1.0), ("odd", -1.0)):
        proj = lambda v, s=sgn: 0.5 * (v + s * v[flip])
        op = sla.LinearOperator((n, n), matvec=lambda v, p=proj: p(mv(p(np.asarray(v).reshape(-1)))), dtype=np.float64)
        rng = np.random.default_rng(12345 + w + (1 if twist else 0))
        v0 = proj(rng.random(n) + 1.0)
        kk = k if name == "even" else 4
        vals = sla.eigs(op, k=kk, which="LM", v0=v0, tol=1e-10, maxiter=100000, return_eigenvectors=False)
        tops[name] = np.sort(np.abs(vals))[::-1]
    lam0 = tops["even"][0]
    second = [x for x in tops["even"] if x < lam0 * (1 - 1e-9)]
    out["per_site"] = float(lam0 ** (1.0 / w))
    out["spin_gap"] = float(np.log(lam0 / tops["odd"][0]) / np.log(3)) if tops["odd"][0] > 1e-12 else float("inf")
    out["energy_gap"] = float(np.log(lam0 / second[0]) / np.log(3)) if second and second[0] > 1e-12 else float("inf")
    out["even_top"] = [float(x) for x in tops["even"][:4]]
    out["odd_top"] = [float(x) for x in tops["odd"][:2]]
    return out


def correlations(w, arr, twist, rmax=20):
    """Exact (dense, w <= 12): the connected correlation of each column's spin along the transfer (r rows) and around (c columns)
    under the infinite-cylinder measure; the spins are 2v - 1, whose mean is 0 by the flip symmetry."""
    M = dense_transfer(w, arr, twist)
    vals, R = np.linalg.eig(M)
    i0 = int(np.argmax(np.abs(vals)))
    lam = vals[i0].real
    r = np.abs(R[:, i0].real)
    valsL, L = np.linalg.eig(M.T)
    l = np.abs(L[:, int(np.argmax(np.abs(valsL)))].real)
    pi = l * r / (l @ r)
    n = 1 << w
    spins = 2.0 * ((np.arange(n)[:, None] >> np.arange(w)[None, :]) & 1) - 1.0
    along, around = {}, {}
    for c in range(3):
        s = spins[:, c]
        vec = s * r
        seq = []
        for k in range(1, rmax + 1):
            vec = M @ vec / lam
            seq.append(float((l * s) @ vec / (l @ r)))
        along[c] = seq
        around[c] = [float(pi @ (s * spins[:, (c + d) % w])) for d in range(1, w // 2 + 1)]
    return {"width": w, "twist": twist, "along": along, "around": around, "mean_spin": [float(pi @ spins[:, c]) for c in range(3)]}


# ---------- weave symmetries ----------

def triangles(arr, span=6):
    """The knots of a periodic arrangement in a window, as {frozenset of vertices: (ordered vertices, excluded pattern)}."""
    out = {}
    for i in range(-span, span):
        for j in range(-span, span):
            for t in "UD":
                vs = ((i, j), (i + 1, j), (i, j + 1)) if t == "U" else ((i + 1, j), (i, j + 1), (i + 1, j + 1))
                out[frozenset(vs)] = (vs, P[arr[(i % 3, t)]])
    return out


def point_group():
    """The 12 linear maps of Z^2 preserving the weave's six bond directions."""
    dirs = {(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)}
    out = []
    for a in range(-1, 2):
        for b in range(-1, 2):
            for c in range(-1, 2):
                for d in range(-1, 2):
                    g = ((a, b), (c, d))
                    img = {(a * x + b * y, c * x + d * y) for x, y in dirs}
                    if img == dirs and a * d - b * c in (1, -1):
                        out.append(g)
    return out


def image_inconsistent(arr, g, shift):
    """The inconsistent bonds of g(arr) translated by shift, read in one 3 x 1 cell, or None if g(arr) is not 3 x 1 periodic there."""
    (a, b), (c, d) = g
    tri = triangles(arr)
    mapped = {}
    for key, (vs, p) in tri.items():
        img = [(a * x + b * y + shift[0], c * x + d * y + shift[1]) for x, y in vs]
        mapped[frozenset(img)] = dict(zip(img, p))
    new = {}
    for i in range(3):
        for t in "UD":
            vs = ((i, 0), (i + 1, 0), (i, 1)) if t == "U" else ((i + 1, 0), (i, 1), (i + 1, 1))
            if frozenset(vs) not in mapped:
                return None
            vals = mapped[frozenset(vs)]
            p = tuple(vals[v] for v in vs)
            q = p if p in P else tuple(1 - x for x in p)
            new[(i, 0, t)] = P.index(q)
    # periodicity check on a few more cells
    for i in range(3, 6):
        for j in (1, 2):
            for t in "UD":
                vs = ((i, j), (i + 1, j), (i, j + 1)) if t == "U" else ((i + 1, j), (i, j + 1), (i + 1, j + 1))
                key = frozenset(vs)
                if key not in mapped:
                    return None
                p = tuple(mapped[key][v] for v in vs)
                q = p if p in P else tuple(1 - x for x in p)
                if P.index(q) != new[(i % 3, 0, t)]:
                    return None
    return new
