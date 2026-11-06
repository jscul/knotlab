"""Check for CORRECTIONS-20261026-001C-P001: Borromean insertions steer the twisted triple product.
Standard library only; imports tp_lib.py from the reissued proof CORRECTIONS-20261026-001A-P001 read-only.
Run: python3 check.py [--write]"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CORRECTIONS-20261026-001A/CORRECTIONS-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum_reissued"))
import tp_lib as T  # noqa: E402


def setup(word, n):
    U, rels, arc = T.presentation(word, n, 3)
    H, Bm, _ = T.obstruction_data(U, rels)
    return U, rels, arc, H, Bm


def leaves_for(H, U, arc, tops, offsets, scale=None, l2r=False):
    out = []
    for e, (L, o) in enumerate(zip(tops, offsets)):
        lam = []
        for j, bq in enumerate(T.window(o)):
            pos = list(reversed(bq)) if l2r else list(bq)
            vals = T.leaf_values(H, U, arc, L, pos)
            if scale and scale.get(e) and j == 0:   # scale one leaf: the determinant is multiplied by the scalar
                vals = [T.fmul(scale[e], v) for v in vals]
            lam.append(vals)
        out.append(lam)
    return out


def level0(H, U, arc, n):
    return [T._pack([T._vals(h, U)[arc[(0, q)]] for q in range(n)]) for h in H]


def same_cocycles(base, new, n):
    """the cocycles of the two knots, read on the top arcs, span the same space (with coboundaries)"""
    cob = [T._pack([T.fmul(T.W, v)] * n) for v in (1, 2)]
    sb, sn = {}, {}
    for v in base + cob:
        T.span_add(sb, v)
    for v in new + cob:
        T.span_add(sn, v)
    return len(base) == len(new) and all(T.reduce_into(sb, v) == 0 for v in new + cob) and len(sb) == len(sn)


def main():
    t0 = time.time()
    out, ok_all = {}, True
    k, n = 5, 11
    base = T.fig8_sum(k)
    Ub, _, arcb, Hb, Bmb = setup(base, n)
    lb = level0(Hb, Ub, arcb, n)

    # part 1: one insertion at every level of (4_1)^#5, window on positions 1..9
    rows1, ok1 = {}, True
    for L in range(len(base)):
        w, tops = T.insert_at(base, [(L, 1)])
        U, rels, arc, H, Bm = setup(w, n)
        lam = leaves_for(H, U, arc, tops, [1])
        rank = len({tuple(x[i] for x in lam[0]) for i in range(len(H))} | {(0, 0, 0)})
        N, bad = T.compare_kernels(Bm, T.predicted_rows(H, lam))
        good = bad == 0 and T.smith_invariants(U, rels) == [3] and same_cocycles(lb, level0(H, U, arc, n), n)
        rows1[f"level {L}"] = {"N": N, "mismatching a": bad, "leaf images on basis": rank, "ok": good}
        ok1 &= good
    out["1_single_insertions"] = {"rows": rows1, "ok": ok1}
    print("part 1:", {k_: (v["N"], v["mismatching a"]) for k_, v in rows1.items()}, flush=True)
    ok_all &= ok1

    # part 2: additivity with the same constant, and controls that must fail
    rows2, ok2 = {}, True
    for levels in ((6, 13), (7, 14), (6, 14), (6, 13, 14)):
        ins = [(L, 1) for L in levels]
        w, tops = T.insert_at(base, ins)
        U, rels, arc, H, Bm = setup(w, n)
        lam = leaves_for(H, U, arc, tops, [1] * len(ins))
        N, bad = T.compare_kernels(Bm, T.predicted_rows(H, lam))
        lam_w = leaves_for(H, U, arc, tops, [1] * len(ins), scale={1: T.W})
        _, bad_w = T.compare_kernels(Bm, T.predicted_rows(H, lam_w))
        lam_l = leaves_for(H, U, arc, tops, [1] * len(ins), l2r=True)
        _, bad_l = T.compare_kernels(Bm, T.predicted_rows(H, lam_l))
        good = bad == 0 and bad_w > 0 and bad_l > 0 and T.smith_invariants(U, rels) == [3]
        rows2[str(levels)] = {"N": N, "mismatching a (constant 1)": bad, "control: second insertion scaled by w": bad_w,
                              "control: left-to-right leaves": bad_l, "ok": good}
        ok2 &= good
    out["2_additivity"] = {"rows": rows2, "ok": ok2}
    print("part 2:", rows2, flush=True)
    ok_all &= ok2

    # part 3: a base with T0 != 0: 3_1 # (4_1)^#4 on 10 strands; prediction T0 + det(leaves), T0 recovered from the base
    n3 = 10
    base3 = [1, 1, 1] + [x + (1 if x > 0 else -1) for x in T.fig8_sum(4)]
    U0, _, arc0, H0, Bm0 = setup(base3, n3)
    sols, t_of, wdim, inj, _ = T.recover_trace_form(H0, Bm0, U0)
    cands = [s for s in (sols[0], sols[1], sols[0] ^ sols[1])] if len(sols) == 2 else []
    l0 = level0(H0, U0, arc0, n3)
    cob = [T._pack([T.fmul(T.W, v)] * n3) for v in (1, 2)]
    solve = T._coords_solver(l0 + cob)
    full = (1 << len(H0)) - 1
    rows3, ok3 = {"symmetric solutions (F2 dim)": len(sols)}, len(sols) == 2
    for (L, o) in ((5, 0), (12, 0)):
        w, tops = T.insert_at(base3, [(L, o)])
        U, rels, arc, H, Bm = setup(w, n3)
        Mc = [solve(v) & full for v in level0(H, U, arc, n3)]
        lam = leaves_for(H, U, arc, tops, [o])
        res = []
        for s in cands:
            t0f = t_of(s)
            d2 = len(H)
            extra = []
            for i in range(d2):
                row = []
                for b in range(d2):
                    r = 0
                    for c in range(d2):
                        v = 0
                        for i0 in range(d2):
                            if Mc[i] >> i0 & 1:
                                for b0 in range(d2):
                                    if Mc[b] >> b0 & 1:
                                        for c0 in range(d2):
                                            if Mc[c] >> c0 & 1:
                                                v ^= t0f[i0][b0][c0]
                        r |= v << c
                    row.append(r)
                extra.append(row)
            N, bad = T.compare_kernels(Bm, T.predicted_rows(H, lam, extra))
            res.append((N, bad))
        N_zero, bad_zero = T.compare_kernels(Bm, T.predicted_rows(H, lam))
        good = all(b == 0 for _, b in res) and bad_zero > 0 and T.smith_invariants(U, rels) == [3]
        rows3[f"window {(L, o)}"] = {"(N, mismatching a) for the three scalars of T0": res,
                                     "control: dropping T0 (mismatching a)": bad_zero, "ok": good}
        ok3 &= good
    out["3_nonzero_base_form"] = {"rows": rows3, "ok": ok3}
    print("part 3:", rows3, flush=True)
    ok_all &= ok3

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "CORRECTIONS-20261026-001C-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
