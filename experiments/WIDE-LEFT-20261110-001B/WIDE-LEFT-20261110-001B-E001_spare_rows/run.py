"""WIDE-LEFT-20261110-001B-E001: the spare-row lemma's checks for the 2n-pigeon left-pigeon principle (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/WIDE-LEFT-20261110-001B/WIDE-LEFT-20261110-001B-E001_spare_rows/run/result.json

WLP_n: n = 2^l holes, 2n pigeons, pigeon rows f_x (l bits), hole rows g_h (l + 1 bits, every code a pigeon). The reduced decoder sends
f_x,t to sum_{z : z_t = 1} X_x,z and g_h,j to sum_y y_j X_y,h, into Braun's unary system F^fun_{2n,n}, whose degree-k ideal is the span
of matchings modulo the row-sum relations. Q1: U_0 (row-linear monomials of degree <= k avoiding the spare hole and pigeon stars) meets
the kernel only in zero. Q2: the cube of the planned proof isolates each top monomial. Q3: the whole kernel's fraction. Q4: the density
count (D) at l = 20 to 60."""
import itertools
import json
import math
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "WIDE-LEFT-20261110-001B" / "WIDE-LEFT-20261110-001B-E001_spare_rows" / "run"


class WLP:
    def __init__(self, n, k):
        self.n, self.k = n, k
        self.l = n.bit_length() - 1
        self.m = 2 * n
        self.lg = self.l + 1
        self.index = {}
        for s in range(k + 1):
            for xs in itertools.combinations(range(self.m), s):
                for hs in itertools.permutations(range(n), s):
                    self.index[frozenset(zip(xs, hs))] = len(self.index)

    def relations(self):
        for T, i in list(self.index.items()):
            if len(T) >= self.k:
                continue
            rows = {x for x, _ in T}
            cols = {h for _, h in T}
            for x in range(self.m):
                if x in rows:
                    continue
                v = 1 << i
                for h in range(self.n):
                    if h not in cols:
                        v ^= 1 << self.index[T | {(x, h)}]
                yield v

    def cells(self, bit):
        kind, r, b = bit
        if kind == "f":
            return [(r, z) for z in range(self.n) if (z >> b) & 1]
        return [(y, r) for y in range(self.m) if (y >> b) & 1]

    def image(self, mono):
        v = 0
        for cells in itertools.product(*[self.cells(b) for b in mono]):
            T = frozenset(cells)
            xs = [x for x, _ in T]
            hs = [h for _, h in T]
            if len(set(xs)) == len(xs) and len(set(hs)) == len(hs):
                v ^= 1 << self.index[T]
        return v

    def monomials(self, pigeons, holes, k):
        rows = [("f", x, list(range(self.l))) for x in pigeons] + [("g", h, list(range(self.lg))) for h in holes]
        out = [[]]
        for d in range(1, k + 1):
            for chosen in itertools.combinations(rows, d):
                for bits in itertools.product(*[c[2] for c in chosen]):
                    out.append([(c[0], c[1], b) for c, b in zip(chosen, bits)])
        return out


def insert(basis, v):
    while v:
        b = v.bit_length() - 1
        if b not in basis:
            basis[b] = v
            return True
        v ^= basis[b]
    return False


def stars(width, centers):
    out = []
    for c in centers:
        out.append([c] + [c ^ (1 << t) for t in range(width)])
    return out


SPARES = {  # (n, k): (hole stars, pigeon stars), centers at pairwise distance >= 3
    (4, 1): (stars(2, [0]), stars(3, [0])),
    (8, 1): (stars(3, [0]), stars(4, [0])),
    (16, 2): (stars(4, [0, 15]), stars(5, [0, 31])),
}


def q1(n, k):
    W = WLP(n, k)
    hs, ps = SPARES[(n, k)]
    E = {h for s in hs for h in s}
    P = {p for s in ps for p in s}
    assert len(E) == sum(len(s) for s in hs) and len(P) == sum(len(s) for s in ps)
    basis = {}
    r0 = sum(insert(basis, v) for v in W.relations())
    mons = W.monomials([x for x in range(W.m) if x not in P], [h for h in range(n) if h not in E], k)
    new = sum(insert(basis, W.image(mono)) for mono in mons)
    return {"n": n, "k": k, "spare holes": sorted(E), "spare pigeons": sorted(P), "dim U_0": len(mons), "independent": new,
            "dim U_0 ∩ K_k": len(mons) - new}, W, E, P, hs, ps


def cube_value(W, mono, coords):
    """sum over the cube of the substituted image of mono: coords are ('f', x, t, (z0, z1)) or ('g', h, j, (y0, y1), e).
    Returns the image as a dict over residual matchings (frozenset of cells) with GF(2) coefficients."""
    total = {}
    for eps in itertools.product((0, 1), repeat=len(coords)):
        fixed = {}            # cell -> 0/1 for cells in selected rows or columns
        sel_rows, sel_cols = set(), set()
        for (c, e) in zip(coords, eps):
            if c[0] == "f":
                _, x, t, (z0, z1) = c
                z = (z0, z1)[e]
                sel_rows.add(x); sel_cols.update((z0, z1))
                fixed[(x, z)] = 1
            else:
                _, h, j, (y0, y1), park = c
                y, yo = ((y0, y1)[e], (y0, y1)[1 - e])
                sel_rows.update((y0, y1)); sel_cols.update((h, park))
                fixed[(y, h)] = 1
                fixed[(yo, park)] = 1
        prod = {frozenset(): 1}
        for b in mono:
            form = {}
            for cell in W.cells(b):
                if cell[0] in sel_rows or cell[1] in sel_cols:
                    if fixed.get(cell, 0):
                        form[frozenset()] = form.get(frozenset(), 0) ^ 1
                else:
                    form[frozenset([cell])] = form.get(frozenset([cell]), 0) ^ 1
            new = {}
            for a, ca in prod.items():
                if not ca:
                    continue
                for bb, cb in form.items():
                    if not cb:
                        continue
                    T = a | bb
                    xs = [x for x, _ in T]
                    hs = [h for _, h in T]
                    if len(set(xs)) == len(xs) and len(set(hs)) == len(hs):
                        new[T] = new.get(T, 0) ^ 1
            prod = new
        for T, c in prod.items():
            if c:
                total[T] = total.get(T, 0) ^ 1
    return {T: 1 for T, c in total.items() if c}


def q2(W, E, P, hs, ps, k):
    """for every monomial M0 of U_0 of degree t >= 1, build its cube from the stars and check: cube(M0) = 1 and cube(M) = 0 for every
    other monomial of U_0 of degree <= t"""
    pigeons = [x for x in range(W.m) if x not in P]
    holes = [h for h in range(W.n) if h not in E]
    mons = W.monomials(pigeons, holes, k)
    ok, tops = True, 0
    for M0 in mons:
        if not M0:
            continue
        hstars = [list(s) for s in hs]
        pstars = [list(s) for s in ps]
        coords = []
        hi = pi = 0
        for (kind, r, b) in M0:
            if kind == "f":
                s = hstars[hi]; hi += 1
                coords.append(("f", r, b, (s[0], s[0] ^ (1 << b))))
            else:
                s = pstars[pi]; pi += 1
                park = hstars[hi][0]; hi += 1
                coords.append(("g", r, b, (s[0], s[0] ^ (1 << b)), park))
        tops += 1
        for M in mons:
            if len(M) > len(M0):
                continue
            val = cube_value(W, M, coords)
            want = {frozenset(): 1} if M == M0 else {}
            ok &= val == want
    return ok, tops


def q3(n, k):
    W = WLP(n, k)
    basis = {}
    for v in W.relations():
        insert(basis, v)
    mons = W.monomials(list(range(W.m)), list(range(n)), k)
    new = sum(insert(basis, W.image(mono)) for mono in mons)
    v = W.m * W.l + n * W.lg
    return {"n": n, "k": k, "dim L_k": len(mons), "dim K_k": len(mons) - new, "fraction": round((len(mons) - new) / len(mons), 4),
            "(l + 1)^2 k / v": round((W.l + 1) ** 2 * k / v, 4)}


def log_binom(a, b):
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def log_ek(m, a, n, b, k):
    terms = [log_binom(m, i) + i * math.log(a) + log_binom(n, k - i) + (k - i) * math.log(b) for i in range(max(0, k - n), min(m, k) + 1)]
    top = max(terms)
    return top + math.log(sum(math.exp(t - top) for t in terms))


def q4():
    rows = []
    for l in range(20, 61):
        n = 2 ** l
        k = n // (64 * l ** 3)
        h = math.floor(((n + 1) / (2 * l * k) - 2) / 4)
        v = 2 * n * l + n * (l + 1)
        mp = 2 * n - k * (l + 2)          # pigeon rows outside the stars
        nh = n - 2 * k * (l + 1)          # hole rows outside the stars
        log_dim = log_ek(mp, l, nh, l + 1, k)  # degree exactly k: a lower bound for dim U_0
        val = log_dim - log_binom(v + k, k) + h * k * k / (v + k)
        rows.append({"l": l, "k": k, "h": h, "D >= 2h + l + 1": 4 * h + 1 >= 2 * h + l + 1, "log bound": val, "ratio to n / l^5": val / (n / l ** 5)})
    return rows


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    log = open(OUT / "progress.txt", "w")
    res = {"experiment": "WIDE-LEFT-20261110-001B-E001", "Q1": [], "Q2": [], "Q3": []}
    for n, k in ((4, 1), (8, 1), (16, 2)):
        r, W, E, P, hs, ps = q1(n, k)
        res["Q1"].append(r)
        print("Q1", json.dumps(r), round(time.time() - t0), file=log, flush=True)
        ok, tops = q2(W, E, P, hs, ps, k)
        res["Q2"].append({"n": n, "k": k, "cubes": tops, "identities hold": ok})
        print("Q2", n, k, ok, tops, round(time.time() - t0), file=log, flush=True)
    for n, k in ((4, 2), (8, 2)):
        r = q3(n, k)
        res["Q3"].append(r)
        print("Q3", json.dumps(r), round(time.time() - t0), file=log, flush=True)
    res["Q4"] = q4()
    res["Q1 holds"] = all(r["dim U_0 ∩ K_k"] == 0 for r in res["Q1"])
    res["Q2 holds"] = all(r["identities hold"] for r in res["Q2"])
    res["Q3 below LP_{n+1}'s 0.73 and 0.49"] = res["Q3"][0]["fraction"] < 0.73 and res["Q3"][1]["fraction"] < 0.49
    q4r = [r["ratio to n / l^5"] for r in res["Q4"]]
    res["Q4 positive from some l on, ratio bounded below"] = {"first l with a positive bound": next((r["l"] for r in res["Q4"] if r["log bound"] > 0), None),
                                                             "smallest ratio over l >= 40": round(min(r["ratio to n / l^5"] for r in res["Q4"] if r["l"] >= 40), 6)}
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("Q4",)}, indent=1))


if __name__ == "__main__":
    main()
