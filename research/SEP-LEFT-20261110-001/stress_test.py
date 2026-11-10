"""Stress test of SEP-LEFT-20261110-001 one size past what its tickets checked (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. Ticket B's readings by an independent solver: a pure-Python RREF closure (not pcsep.c) recomputes BPHP_4 and LP_4 degree by degree
   (pcsep.c was cross-checked before freezing on random formulas of at most 8 variables; LP_4 has 22).
2. The control one size past: bit PHP with n = 16 holes and m = 16 pigeons (64 variables, the solver's limit; Braun's row-linear
   separation holds for every m) at B = 2 to 5, inside Braun's range (B <= 8): L1 and L2 fully separated. The first run used m = 17,
   68 variables, past the solver's 64-bit masks, and its reading was invalid. LP_16 (148 variables) is not readable at all with this
   solver, so ticket B's comparison has no size past n = 8.
3. Ticket A's identities (Lemmas 1 and 3) at n = 32 on 100 random pigeon assignments (checked to n = 16), and Theorem 2's inequality for
   l = 21 to 24 (checked to 20)."""
import importlib.util
import itertools
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/SEP-LEFT-20261110-001B/SEP-LEFT-20261110-001B-E001_row_linear_separation"
spec = importlib.util.spec_from_file_location("sep_left_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["sep_left_run"] = R
spec.loader.exec_module(R)
A = ROOT / "proofs/SEP-LEFT-20261110-001A/SEP-LEFT-20261110-001A-P001_what_transfers_from_bit_php"
spec = importlib.util.spec_from_file_location("sep_left_a", A / "check.py")
CA = importlib.util.module_from_spec(spec)
sys.modules["sep_left_a"] = CA
spec.loader.exec_module(CA)
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)


def reference(v, axioms, B, probes):
    """closure by RREF over python integers; returns (refuted, [new count per probe set])"""
    cols = [sum(1 << x for x in c) for d in range(B, -1, -1) for c in itertools.combinations(range(v), d)]
    N = len(cols)
    idx = {m: N - 1 - i for i, m in enumerate(cols)}
    deg = {b: bin(m).count("1") for m, b in idx.items()}
    basis = {}

    def vec(poly):
        out = 0
        for m in poly:
            out ^= 1 << idx[m]
        return out

    def red(w, bas):
        while w:
            b = w.bit_length() - 1
            if b not in bas:
                return w
            w ^= bas[b]
        return 0

    def ins(w, bas):
        w = red(w, bas)
        if not w:
            return False
        bas[w.bit_length() - 1] = w
        return True
    queue = []
    for a in axioms:
        if max(bin(m).count("1") for m in a) <= B and ins(vec(a), basis):
            queue.append(max(basis))
    done = 0
    order = list(basis)
    while done < len(order):
        b = order[done]
        done += 1
        w = basis[b]
        if deg[b] > B - 1:
            continue
        mons = [cols[N - 1 - i] for i in range(w.bit_length()) if (w >> i) & 1]
        for x in range(v):
            p = set()
            for m in mons:
                p ^= {m | (1 << x)}
            w2 = red(vec(p), basis)
            if w2:
                nb = w2.bit_length() - 1
                basis[nb] = w2
                order.append(nb)
        if idx[0] in basis:
            return True, [0] * len(probes)
    if red(1 << idx[0], basis) == 0:
        return True, [0] * len(probes)
    news = []
    for P in probes:
        bas = dict(basis)
        news.append(sum(ins(1 << idx[m], bas) for m in P))
    return False, news


def main():
    got, want = {}, {}
    res = json.loads((ROOT / "artifacts/SEP-LEFT-20261110-001B/SEP-LEFT-20261110-001B-E001_row_linear_separation/run/result.json").read_text())
    for name, build, n in (("BPHP", R.bphp, 4), ("LP", R.left_pigeon, 4)):
        v, axioms, prow, arow = build(n)
        sets = {"L1 pigeon rows": R.row_linear(prow, 1), "L1 all rows": R.row_linear(arow, 1),
                "L2 pigeon rows": R.row_linear(prow, 2), "L2 all rows": R.row_linear(arow, 2)}
        key = "%s_%d" % (name, n)
        for B, rd in res["readings"][key]["by degree"].items():
            use = [s for s in sets if int(s[1]) <= int(B)]
            refuted, news = reference(v, axioms, int(B), [sets[s] for s in use])
            got["%s B=%s" % (key, B)] = [refuted] + news
            want["%s B=%s" % (key, B)] = [rd["refuted"]] + ([0] * len(use) if rd["refuted"] else [rd["separated"][s] for s in use])
    record("1_ticket_B_by_an_independent_solver", got == want, {"independent": got, "ticket B": want})

    binary = HERE / "pcsep_stress"
    subprocess.run(["gcc", "-O3", "-march=native", "-o", str(binary), str(X / "pcsep.c")], check=True)
    l, m = 4, 16
    prow = [[i * l + t for t in range(l)] for i in range(m)]
    axioms = []
    for i, j in itertools.combinations(range(m), 2):
        P = {0}
        for t in range(l):
            P = R.mul(P, {0, 1 << prow[i][t], 1 << prow[j][t]})
        axioms.append(P)
    v = m * l
    assert v <= 64
    rows = {}
    ok2 = True
    for B in (2, 3, 4, 5):
        probes = [R.row_linear(prow, 1), R.row_linear(prow, 2)]
        r = R.run(binary, B, v, axioms, probes)
        rows[B] = r.get("probes", r)
        ok2 &= "probes" in r and all(p[0] == p[1] for p in r["probes"])
    binary.unlink()
    record("2_control_BPHP_16_inside_Braun_range", ok2, {"pigeons": m, "variables": v, "B: [size, separated] for L1, L2": rows})

    rng = random.Random(20261111)
    ok1, ok3, cases = CA.lemma_1_and_3(32, rng, 100)
    worst = math.inf
    for l in range(21, 25):
        n = 2 ** l
        m = n + 1
        v = m * l + n * (l + 1)
        h = 3 * l
        for k in sorted({1, 8, n // 64, n // 8, n // 2}):
            worst = min(worst, CA.log_ek(m, l, n, l + 1, k) - CA.log_binom(v + k, k) + h * k * k / (v + k) - (k * k / (3 * n) - 2))
    record("3_ticket_A_one_size_past", ok1 and ok3 and worst >= 0,
           {"n = 32 assignments": cases, "Lemma 1": ok1, "Lemma 3": ok3, "Theorem 2 margin, l = 21 to 24": round(worst, 3)})
    out = {"epic": "SEP-LEFT-20261110-001", "checks": OUT, "status": "passed" if all(v["pass"] for v in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
