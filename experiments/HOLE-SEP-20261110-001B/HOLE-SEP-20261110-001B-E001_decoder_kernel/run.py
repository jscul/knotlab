"""HOLE-SEP-20261110-001B-E001: the kernel of the reduced decoder on bit LeftPigeon's row-linear space (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel/run/result.json

For LP_n (n = 2^l holes, m = n + 1 pigeons, pigeon rows of l bits, hole rows of l + 1 bits) and its row-linear space L_k, compute
dim K_k, K_k = {p in L_k : tau~(p) in Ideal_k(F^fun_{m,n})}, exactly over GF(2). Pol_<=k / Ideal_k is the span of matchings of size
at most k modulo the row-sum relations sum_{h not in cols(T)} X_{T + (x,h)} = X_T (|T| < k, x not in rows(T)) (Braun's Lemma on
complete moment equations). tau~ sends f_x,t to sum_{z : z_t = 1} X_x,z and g_h,j to sum_y y_j X_y,h; a row-linear monomial goes to
the product, reduced to matchings (a repeated row or column kills a term unless the two cells coincide). Also checks that the
(l + 1)^2 known kernel elements of the frozen statement lie in K_1 and are independent."""
import itertools
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "HOLE-SEP-20261110-001B" / "HOLE-SEP-20261110-001B-E001_decoder_kernel" / "run"
ROSTER = [(4, 1), (4, 2), (4, 3), (8, 1), (8, 2), (8, 3), (16, 1), (16, 2)]


class Space:
    def __init__(self, n, k):
        self.n, self.k = n, k
        self.l = n.bit_length() - 1
        self.m = n + 1
        self.lg = (self.m - 1).bit_length()
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

    def image(self, mono):
        """mono: list of ('f', x, t) and ('g', h, j), distinct rows"""
        choices = []
        for kind, r, b in mono:
            if kind == "f":
                choices.append([(r, z) for z in range(self.n) if (z >> b) & 1])
            else:
                choices.append([(y, r) for y in range(self.m) if (y >> b) & 1])
        v = 0
        for cells in itertools.product(*choices):
            T = frozenset(cells)
            xs = [x for x, _ in T]
            hs = [h for _, h in T]
            if len(set(xs)) == len(xs) and len(set(hs)) == len(hs):
                v ^= 1 << self.index[T]
        return v

    def row_linear(self, k):
        rows = [("f", x, list(range(self.l))) for x in range(self.m)] + [("g", h, list(range(self.lg))) for h in range(self.n)]
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


def kernel_dim(n, k):
    S = Space(n, k)
    basis = {}
    r0 = sum(insert(basis, v) for v in S.relations())
    mons = S.row_linear(k)
    img = 0
    for mono in mons:
        img += insert(basis, S.image(mono))
    return {"n": n, "k": k, "matchings": len(S.index), "relations rank": r0, "dim L_k": len(mons), "image rank": img,
            "dim K_k": len(mons) - img, "kernel fraction": round((len(mons) - img) / len(mons), 6), "(l + 1)^2": (S.l + 1) ** 2}, S


def known_elements_check(S):
    """the (l + 1)^2 known elements: their images lie in the span of the relations (k = 1), and they are independent"""
    basis = {}
    for v in S.relations():
        insert(basis, v)
    ok_in = True
    vecs = []
    for j in range(S.lg):
        for a in [None] + list(range(S.l)):
            v = 0
            for h in range(S.n):
                if a is None or (h >> a) & 1:
                    v ^= S.image([("g", h, j)])
            if a is None:
                if sum((x >> j) & 1 for x in range(S.m)) & 1:
                    v ^= 1 << S.index[frozenset()]
            else:
                for x in range(S.m):
                    if (x >> j) & 1:
                        v ^= S.image([("f", x, a)])
            w = v
            while w:
                b = w.bit_length() - 1
                if b not in basis:
                    break
                w ^= basis[b]
            ok_in &= w == 0
            vecs.append((j, a))
    return ok_in, len(vecs)


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    log = open(OUT / "progress.txt", "w")
    readings = []
    known = {}
    for n, k in ROSTER:
        r, S = kernel_dim(n, k)
        r["seconds"] = round(time.time() - t0, 1)
        readings.append(r)
        print(json.dumps(r), file=log, flush=True)
        if k == 1:
            ok, cnt = known_elements_check(S)
            known[n] = {"known elements in K_1": ok, "count": cnt}
    by = {(r["n"], r["k"]): r for r in readings}
    p1 = all(by[(n, 1)]["dim K_k"] == by[(n, 1)]["(l + 1)^2"] and known[n]["known elements in K_1"] for n in (4, 8, 16))
    p2_fall = all(by[(8, k)]["kernel fraction"] < by[(4, k)]["kernel fraction"] for k in (2, 3)) and \
        by[(16, 2)]["kernel fraction"] < by[(8, 2)]["kernel fraction"]
    p2 = p2_fall and by[(16, 2)]["kernel fraction"] < 0.01
    result = {"experiment": "HOLE-SEP-20261110-001B-E001", "readings": readings, "known elements": known,
              "P1 dim K_1 = (l + 1)^2, spanned by the known elements": p1,
              "P2 the kernel fraction falls with n (k = 2, 3) and is below 1% at n = 16, k = 2": p2,
              "stop (b) triggered: kernel fraction above 10% at n = 16, k = 2, or not falling": (not p2_fall) or by[(16, 2)]["kernel fraction"] > 0.1,
              "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "readings"}, indent=1))
    for r in readings:
        print(r)


if __name__ == "__main__":
    main()
