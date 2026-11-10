"""Post hoc, after conjecture C failed at k = 2 (stop rule (c)): the top hole bit decodes to a single pigeon.

    .venv/bin/python3 -B top_bit_family.py    writes top_bit_family.json beside this file

In LP_n the hole rows carry l + 1 bits, but only pigeon n (code 100...0) has the top bit set, so tau~(g_h,l) = X_n,h: "pigeon n sits in
hole h". Two such factors on different holes multiply to zero (row exclusion), and g_h,j * g_h,l (j < l) decodes to zero too (pigeon n's
low bits are 0). Z_k: the span of the multilinear monomials of degree <= k whose decoded image is zero. Does (I_k + Z_k) ∩ L_k reach K_k
at k = 2 (n = 4, 8, 16)? And the share at the needed degree: the row-linear monomials with at least two top hole bits lie in K_k; their
share of L_k, computed exactly by counting (l = 14 to 22), against the bound's allowance 1 - exp(-k*^2/(6n))."""
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/KERNEL-FRAC-20261110-001B/KERNEL-FRAC-20261110-001B-E001_conjecture_c"
spec = importlib.util.spec_from_file_location("kf_run", X / "run.py")
KR = importlib.util.module_from_spec(spec)
sys.modules["kf_run"] = KR
spec.loader.exec_module(KR)
R = KR.R


def zero_image(n, mono):
    """decoded image is identically zero: two top bits on different holes, or a top and a low bit on one hole"""
    l = n.bit_length() - 1
    tops = [r for k, r, b in mono if k == "g" and b == l]
    if len(set(tops)) >= 2:
        return True
    rows = {}
    for k, r, b in mono:
        rows.setdefault((k, r), []).append(b)
    return any(k == "g" and l in bs and len(bs) >= 2 for (k, r), bs in rows.items())


def dims(n, k):
    l, m, lg, allbits = KR.bits(n)
    ks = KR.kappas(n)
    idx, full, nrl = {}, {}, {}
    rf = rn = 0
    gens = []
    for d in range(k):
        for M in itertools.combinations(allbits, d):
            Ms = frozenset(M)
            for kap in ks:
                prod = set()
                for mono in kap:
                    prod ^= {mono | Ms}
                gens.append(prod)
    for d in range(k + 1):
        for M in itertools.combinations(allbits, d):
            if zero_image(n, M):
                gens.append({frozenset(M)})
    for prod in gens:
        vf = vn = 0
        for mono in prod:
            i = idx.setdefault(mono, len(idx))
            vf ^= 1 << i
            if not KR.row_linear(mono):
                vn ^= 1 << i
        rf += R.insert(full, vf)
        rn += R.insert(nrl, vn)
    return rf - rn


def share_with_two_tops(n, k):
    """share of L_k (all degrees <= k) spanned by row-linear monomials with >= 2 top hole bits, exactly (integers)"""
    l = n.bit_length() - 1
    m = n + 1
    allm = low = 0
    for d in range(k + 1):
        for b in range(0, min(n, d) + 1):               # hole rows used
            a = d - b                                    # pigeon rows used
            if a > m:
                continue
            pa = math.comb(m, a) * l ** a * math.comb(n, b)
            allm += pa * (l + 1) ** b
            low += pa * (l ** b + b * l ** (b - 1) if b >= 1 else 1)
    return 1 - low / allm


def main():
    res = {"(I_2 + Z_2) ∩ L_2 against K_2": {}}
    for n, kd in ((4, 173), (8, 839), (16, 3423)):
        d = dims(n, 2)
        res["(I_2 + Z_2) ∩ L_2 against K_2"][n] = {"dim (I_2 + Z_2) ∩ L_2": d, "dim K_2": kd, "equal": d == kd}
        print(n, d, kd, flush=True)
    rows = []
    for l in range(14, 23):
        n = 2 ** l
        ks = (n + 1) // (2 * l * (12 * l + 2))
        if ks < 2:
            continue
        s = share_with_two_tops(n, ks)
        allow = 1 - math.exp(-ks * ks / (6 * n))
        rows.append({"l": l, "k*": ks, "share of the two-top family": s, "allowance 1 - exp(-k*^2/(6n))": allow, "exceeds": s > allow})
        print(rows[-1], flush=True)
    res["two-top family at k*"] = rows
    (HERE / "top_bit_family.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
