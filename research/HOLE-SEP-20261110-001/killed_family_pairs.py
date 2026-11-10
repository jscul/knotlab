"""Rule (b), continued (post hoc): add to killed_family.py's family the products kappa_{a,j} * M whose overlap is two different bits of
one row, paired so the overlaps cancel: kappa_{a,j} * g_h,j' + kappa_{a,j'} * g_h,j (the overlap g_h,j g_h,j' appears twice), and
kappa_{h_t,j} * f_y,s + kappa_{h_s,j} * f_y,t (the overlap y_j f_y,t f_y,s appears twice). Does the enlarged family span K_2?

    .venv/bin/python3 -B killed_family_pairs.py    writes killed_family_pairs.json beside this file"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("kf", HERE / "killed_family.py")
KF = importlib.util.module_from_spec(spec)
sys.modules["kf"] = KF
spec.loader.exec_module(KF)
R = KF.R


def raw_times(p, mono):
    """p * mono with x^2 = x, keeping non-row-linear products"""
    out = {}
    for m in p:
        q = frozenset(set(m) | {mono})
        if q in out:
            del out[q]
        else:
            out[q] = 1
    return out


def add(p, q):
    out = dict(p)
    for m in q:
        if m in out:
            del out[m]
        else:
            out[m] = 1
    return out


def row_linear(p):
    for m in p:
        rows = [(k, r) for k, r, _ in m]
        if len(set(rows)) != len(rows):
            return False
    return True


def main():
    res = {}
    for n in (4, 8, 16):
        S = R.Space(n, 2)
        basis = {}
        for v in S.relations():
            R.insert(basis, v)
        rel = dict(basis)
        family = []
        kap = {(a, j): KF.kappa(S, a, j) for j in range(S.lg) for a in [None] + list(range(S.l))}
        for (a, j), k1 in kap.items():
            family.append(k1)
            for mono in [[("f", x, t)] for x in range(S.m) for t in range(S.l)] + [[("g", h, jj)] for h in range(S.n) for jj in range(S.lg)]:
                q = KF.times(k1, mono)
                if q is not None:
                    family.append(q)
        pairs = 0
        for a in [None] + list(range(S.l)):
            for j in range(S.lg):
                for j2 in range(j + 1, S.lg):
                    for h in range(S.n):
                        q = add(raw_times(kap[(a, j)], ("g", h, j2)), raw_times(kap[(a, j2)], ("g", h, j)))
                        if row_linear(q):
                            family.append(q)
                            pairs += 1
        for j in range(S.lg):
            for t in range(S.l):
                for s in range(t + 1, S.l):
                    for y in range(S.m):
                        q = add(raw_times(kap[(t, j)], ("f", y, s)), raw_times(kap[(s, j)], ("f", y, t)))
                        if row_linear(q):
                            family.append(q)
                            pairs += 1
        inside = True
        for p in family:
            w = KF.poly_image(S, p)
            while w:
                b = w.bit_length() - 1
                if b not in rel:
                    break
                w ^= rel[b]
            inside &= w == 0
        idx, fb, rank = {}, {}, 0
        for p in family:
            v = 0
            for m in p:
                v ^= 1 << idx.setdefault(m, len(idx))
            rank += R.insert(fb, v)
        kd = R.kernel_dim(n, 2)[0]["dim K_k"]
        res[n] = {"family size": len(family), "paired products": pairs, "family rank": rank, "inside K_2": inside, "dim K_2": kd,
                  "spans K_2": inside and rank == kd}
        print(n, res[n], flush=True)
    (HERE / "killed_family_pairs.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
