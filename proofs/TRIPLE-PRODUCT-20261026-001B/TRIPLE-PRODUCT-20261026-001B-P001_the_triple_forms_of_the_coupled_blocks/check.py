"""Check for TRIPLE-PRODUCT-20261026-001B-P001: the triple forms of the coupled blocks.
Standard library only; imports tp_lib.py from the closed proof TRIPLE-PRODUCT-20261026-001A-P001 read-only.
Run: python3 check.py [--write]   (about two minutes)"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/TRIPLE-PRODUCT-20261026-001A/TRIPLE-PRODUCT-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum"))
import tp_lib as T  # noqa: E402

fm = T.fmul


def coupled_word(n):
    return [i for i in range(1, n) for _ in range(3)] + [i for _ in range(n) for i in range(1, n)]


def f4_rref(vecs):
    rows = [list(v) for v in vecs]
    piv, r = [], 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        iv = T.FINV[rows[r][c]]
        rows[r] = [fm(iv, x) for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                g = rows[i][c]
                rows[i] = [x ^ fm(g, y) for x, y in zip(rows[i], rows[r])]
        piv.append(c)
        r += 1
    return rows[:r], piv


def f4_rank(vecs):
    return len(f4_rref(vecs)[0]) if vecs else 0


def contract(Tf, a):
    d = len(Tf)
    M = [[0] * d for _ in range(d)]
    for i in range(d):
        if a[i]:
            for j in range(d):
                for k in range(d):
                    if Tf[i][j][k]:
                        M[j][k] ^= fm(a[i], Tf[i][j][k])
    return M


def count_and_dist(Tf):
    d = len(Tf)
    dist = {}
    for a in itertools.product(range(4), repeat=d):
        c = d - f4_rank(contract(Tf, a))
        dist[c] = dist.get(c, 0) + 1
    return sum(v * 4 ** k for k, v in dist.items()), dict(sorted(dist.items()))


def change_basis(Tf, P):
    d, D = len(P), len(Tf)
    out = [[[0] * d for _ in range(d)] for _ in range(d)]
    for i, j, k in itertools.product(range(d), repeat=3):
        s = 0
        for a in range(D):
            if P[i][a]:
                for b in range(D):
                    if P[j][b]:
                        for c in range(D):
                            if P[k][c] and Tf[a][b][c]:
                                s ^= fm(fm(P[i][a], P[j][b]), fm(P[k][c], Tf[a][b][c]))
        out[i][j][k] = s
    return out


def left_kernel(M):
    d = len(M)
    rows, piv = f4_rref([[M[j][k] for j in range(d)] for k in range(d)])
    out = []
    for f in (j for j in range(d) if j not in piv):
        v = [0] * d
        v[f] = 1
        for r, p in zip(rows, piv):
            v[p] = r[f]
        out.append(v)
    return out


def split_singletons(Tf):
    """split off 1-dimensional blocks F4 e with T(e, K(e), .) = 0 and V = F4 e + K(e); returns (big block, singleton values)"""
    singles = []
    while True:
        d = len(Tf)
        found = None
        for a in itertools.product(range(4), repeat=d):
            if not any(a):
                continue
            M = contract(Tf, a)
            if d - f4_rank(M) == d - 1:
                K = left_kernel(M)
                if f4_rank(K + [list(a)]) == d:
                    T2 = change_basis(Tf, [list(a)] + K)
                    if all(T2[0][j][k] == 0 for j in range(1, d) for k in range(d)) and all(T2[0][0][k] == 0 for k in range(1, d)):
                        found = T2
                        break
        if not found:
            return Tf, singles
        singles.append(found[0][0][0])
        Tf = [[[found[i][j][k] for k in range(1, d)] for j in range(1, d)] for i in range(1, d)]


def f4_form(word, n):
    """the twisted triple product in an F4 basis, up to one scalar per block (injective symmetric solution)"""
    U, rels, _ = T.presentation(word, n, 3)
    H, Bm, _ = T.obstruction_data(U, rels)
    sols, t_of, w, inj, Om = T.recover_trace_form(H, Bm, U)
    t = t_of(T.injective_solution(sols, inj))
    d2 = len(H)
    def tt(ma, mb, mc):
        s = 0
        for i in range(d2):
            if ma >> i & 1:
                for j in range(d2):
                    if mb >> j & 1:
                        for k in range(d2):
                            if mc >> k & 1:
                                s ^= t[i][j][k]
        return s
    def mul_w(mask):
        r = 0
        for i in range(d2):
            if mask >> i & 1:
                r ^= Om[i]
        return r
    span, basis = {}, []
    for i in range(d2):
        if T.span_add(span, 1 << i):
            T.span_add(span, mul_w(1 << i))
            basis.append(1 << i)
    d = len(basis)
    Tf = [[[0] * d for _ in range(d)] for _ in range(d)]
    for i, j, k in itertools.product(range(d), repeat=3):
        x1 = tt(basis[i], basis[j], basis[k])
        x0 = tt(basis[i], basis[j], mul_w(basis[k])) ^ x1
        Tf[i][j][k] = x0 | (x1 << 1)
    return Tf, T.kernel_count(H, Bm)


def with_alternating(Tf, entries):
    d = len(Tf)
    T2 = [[[Tf[i][j][k] for k in range(d)] for j in range(d)] for i in range(d)]
    for i, j, k in itertools.permutations(range(d), 3):
        T2[i][j][k] = 0
    for (i, j, k), v in entries.items():
        for p in itertools.permutations((i, j, k)):
            T2[p[0]][p[1]][p[2]] = v
    return T2


def main():
    t0 = time.time()
    out, ok_all = {}, True
    expect = {6: (3, 244), 9: (5, 8176), 12: (7, 367684)}
    blocks = {}
    for n, (d_exp, c_exp) in expect.items():
        ts = time.time()
        Tf, N = f4_form(coupled_word(n), n)
        sym = all(Tf[i][j][k] == Tf[j][i][k] == Tf[i][k][j] for i, j, k in itertools.product(range(len(Tf)), repeat=3))
        big, singles = split_singletons(Tf)
        d = len(big)
        D = [[big[i][i][k] for k in range(d)] for i in range(d)]
        alt = {(i, j, k): big[i][j][k] for i, j, k in itertools.combinations(range(d), 3) if big[i][j][k]}
        c, dist = count_and_dist(big)
        good = (sym and d == d_exp and len(singles) == n // 3 - 1 and f4_rank(D) == d - 1 and len(alt) > 0 and c == c_exp
                and c * 7 ** len(singles) == N)
        out[f"n = {n}"] = {"dim V": len(Tf), "symmetric": sym, "singletons": len(singles), "block d": d, "rank D (Bockstein part)": f4_rank(D),
                           "nonzero alternating entries (this basis)": len(alt), "block count": c, "corank distribution": dist,
                           "total N = block count x 7^singletons": N, "ok": good, "seconds": round(time.time() - ts, 1)}
        print(f"n = {n}:", out[f"n = {n}"], flush=True)
        ok_all &= good
        blocks[n] = big
    # the counts are not functions of the Bockstein part
    b3 = blocks[6]
    var3 = {s: count_and_dist(with_alternating(b3, {(0, 1, 2): s}))[0] for s in range(4)}
    b5 = blocks[9]
    rng = random.Random(20261026)
    trip = list(itertools.combinations(range(5), 3))
    var5 = sorted({count_and_dist(with_alternating(b5, {t: rng.randrange(4) for t in trip}))[0] for _ in range(8)})
    d_only5 = count_and_dist(with_alternating(b5, {}))[0]
    ctl = {"d = 3, alternating coefficient s -> count": var3, "d = 5, no alternating part": d_only5,
           "d = 5, eight random alternating parts": var5}
    ok_ctl = var3[0] != var3[1] and var3[1] == var3[2] == var3[3] == 244 and d_only5 != 8176 and len(set(var5)) > 1
    ctl["ok"] = ok_ctl
    out["alternating part matters"] = ctl
    print("controls:", ctl, flush=True)
    ok_all &= ok_ctl
    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "TRIPLE-PRODUCT-20261026-001B-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
