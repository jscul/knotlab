#!/usr/bin/env python3
"""Stress run for FULL-REACH-PROOF-20261108-001 (FULL-REACH-PROOF-S1 in docs/LONG_RUNNING.md), one size past each computed claim:
1. the collapse at every side 3 to 64 (ticket A's check 9 reads 3 to 24);
2. the k(k + 1)/2 multiplicities at 32 and 64 (check 10 reads 4, 8, 16);
3. the ring-level reach census at 49 and 50 (FULL-REACH-20261108-001A read to 48) and the failing set at 64 (it read 8, 16, 32).
Writes stress_test.json after each stage, so a partial result is readable while the run continues.

    .venv/bin/python3 -B stress_test.py
Uses ticket A's library and functions; the censuses run in 12 processes."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROOF = ROOT / "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two"
sys.path.insert(0, str(PROOF))
import reach_lib as R  # noqa: E402
import check as C  # noqa: E402

OUT = HERE / "stress_test.json"
STATE = {}


def save(res):
    done = [k for k in ("collapse", "jordan", "census") if k in res]
    res["pass"] = all(res[k]["pass"] for k in done) if len(done) == 3 else ("pending" if all(res[k]["pass"] for k in done) else False)
    OUT.write_text(json.dumps(res, indent=1, default=str) + "\n")


def init(n):
    P, ix, A = R.box(n)
    STATE.update(P=P, A=A, rings={(i, j): sum(1 << ix[q] for q in R.ring(n, i, j)) for i in range(n) for j in range(n)})


def reach(k):
    A, row, union, basis = STATE["A"], 1 << k, 0, {}
    while True:
        x = row
        while x and (x.bit_length() - 1) in basis:
            x ^= basis[x.bit_length() - 1]
        if not x:
            return k, union
        basis[x.bit_length() - 1] = x
        union |= row
        row = R.vec_mat(row, A)


def census(n):
    init(n)
    with Pool(12, initializer=init, initargs=(n,)) as pool:
        res = pool.map(reach, range(2 * n * (n - 1)), chunksize=16)
    full = (1 << len(STATE["P"])) - 1
    fail = {STATE["P"][k]: sorted(r for r, m in STATE["rings"].items() if not m & u) for k, u in res}
    fail = {p: v for p, v in fail.items() if v}
    pred = C.predicted(n) if (n & (n - 1) == 0 and n >= 8) else set()
    return {"contacts missing some contact": sum(1 for k, u in res if u != full), "contacts missing some ring": len(fail),
            "failing set = predicted": set(fail) == pred, "each misses three rings": all(len(v) == 3 for v in fail.values())}


def main():
    t0 = time.time()
    res = json.loads(OUT.read_text()) if OUT.is_file() and "--resume" in sys.argv else {}
    if "collapse" not in res:
        col = C.collapse(range(3, 65))
        roots = [n for n, r in col.items() if r["roots of unity of order dividing 2n - 1 (lower bound)"]]
        e = {n: col[n].get("least power of two e with A^(e(2n - 1)) = I (exact)") for n in roots}
        res["collapse"] = {"pass": roots == [4, 8, 16, 32, 64] and all(v is not None for v in e.values()),
                           "sides where every eigenvalue is a (2n - 1)-th root of unity": roots, "e": e,
                           "seconds": round(time.time() - t0)}
        save(res)
        print("collapse", res["collapse"], flush=True)
    if "jordan" not in res:
        jd = {n: C.jordan(n) for n in (32, 64)}
        res["jordan"] = {"pass": all(j["triangular with geometric 2k - 1"] and j["accounted"] == j["layer dimension"] for j in jd.values()),
                         "detail": jd, "seconds": round(time.time() - t0)}
        save(res)
        print("jordan", res["jordan"]["pass"], flush=True)
    if "census" not in res:
        cen = {n: census(n) for n in (49, 50, 64)}
        res["census"] = {"pass": cen[49]["contacts missing some ring"] == 0 and cen[50]["contacts missing some ring"] == 0
                         and cen[64]["failing set = predicted"] and cen[64]["each misses three rings"], "detail": cen,
                         "seconds": round(time.time() - t0)}
        save(res)
        print("census", res["census"], flush=True)


if __name__ == "__main__":
    main()
