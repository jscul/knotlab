"""Rule (b) of the frozen statement: name the family that every moment functional kills (post hoc diagnosis, after E001).

    .venv/bin/python3 -B killed_family.py    writes killed_family.json beside this file

The inverse-counting identities: for an affine function a of the hole label (a = 1 or a = h_t) and a hole bit j,
kappa_{a,j} = sum_h a(h) g_h,j + sum_x x_j a(f_x), with a(f_x) = 1 or f_x,t (so the second sum is the constant c_j when a = 1). Under
the substitution g(h) := sum_x [f_x = h] x it says "sum over holes of a(h) g(h)_j equals sum over pigeons of a(f(x)) x_j", true for
an inverse map, and not a consequence of LP_n. Family F_2: the kappa's, and kappa_{a,j} times a degree-1 row-linear monomial M, where
the product is row-linear after x^2 = x (the overlap, if any, is the same bit twice). For n = 4, 8, 16: does F_2 lie in K_2, and does
it span K_2?"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel"
spec = importlib.util.spec_from_file_location("hole_sep_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["hole_sep_run"] = R
spec.loader.exec_module(R)


def poly_image(S, poly):
    """poly: dict monomial(frozenset of (kind, row, bit)) -> 1; constant is the empty frozenset"""
    v = 0
    for mono in poly:
        v ^= S.image(sorted(mono))
    return v


def kappa(S, a, j):
    p = {}
    def add(m):
        m = frozenset(m)
        if m in p:
            del p[m]
        else:
            p[m] = 1
    for h in range(S.n):
        if a is None or (h >> a) & 1:
            add({("g", h, j)})
    for x in range(S.m):
        if (x >> j) & 1:
            add(set() if a is None else {("f", x, a)})
    return p


def times(p, mono):
    """p * mono, None unless every product is row-linear after x^2 = x"""
    out = {}
    (kind, r, b), = mono
    for m in p:
        rows = {(k2, r2): b2 for k2, r2, b2 in m}
        if (kind, r) in rows:
            if rows[(kind, r)] != b:
                return None
            q = frozenset(m)
        else:
            q = frozenset(set(m) | {mono[0]})
        if q in out:
            del out[q]
        else:
            out[q] = 1
    return out


def main():
    res = {}
    for n in (4, 8, 16):
        S = R.Space(n, 2)
        basis = {}
        for v in S.relations():
            R.insert(basis, v)
        rel = dict(basis)
        family = []
        for j in range(S.lg):
            for a in [None] + list(range(S.l)):
                k1 = kappa(S, a, j)
                family.append(k1)
                for mono in [[("f", x, t)] for x in range(S.m) for t in range(S.l)] + [[("g", h, jj)] for h in range(S.n) for jj in range(S.lg)]:
                    q = times(k1, mono)
                    if q is not None:
                        family.append(q)
        inside = True
        for p in family:
            w = poly_image(S, p)
            while w:
                b = w.bit_length() - 1
                if b not in rel:
                    break
                w ^= rel[b]
            inside &= w == 0
        # rank of the family as polynomials (coordinates: monomials)
        idx = {}
        fb = {}
        rank = 0
        for p in family:
            v = 0
            for m in p:
                v ^= 1 << idx.setdefault(m, len(idx))
            rank += R.insert(fb, v)
        kd = R.kernel_dim(n, 2)[0]
        res[n] = {"family size": len(family), "family rank": rank, "family inside K_2": inside, "dim K_2": kd["dim K_k"],
                  "dim L_2": kd["dim L_k"], "family spans K_2": inside and rank == kd["dim K_k"]}
        print(n, res[n], flush=True)
    (HERE / "killed_family.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
