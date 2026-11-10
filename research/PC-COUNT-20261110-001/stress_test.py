"""Stress test of PC-COUNT-20261110-001 one size past what its tickets checked (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. Lemma 1 of ticket A (FPHP_G reduces to LeftPigeon, decoding within 2 Delta reads), checked there for N <= 3: 200 random graphs with
   N = 4, 64 random assignments each, and graphs whose holes have degree up to 5.
2. The composed chain of ticket A, checked there with N = 2: 20 random FPHP_G instances with N = 3 (grid side 336).
3. Ticket B's degrees by an independent solver: a pure-Python RREF elimination (not pcdeg.c's semi-echelon code) recomputes the
   count's polynomial-calculus degree on K_2 (3), its Nullstellensatz degree on K_2 (not 5, yes 6) and that the polynomial calculus does
   not refute K_3 at degree 3. pcdeg.c was cross-checked before freezing on formulas of at most 12 variables; these have 16 and 36."""
import importlib.util
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / "proofs/PC-COUNT-20261110-001A/PC-COUNT-20261110-001A-P001_degree_through_the_pigeonhole_principle"
spec = importlib.util.spec_from_file_location("pc_count_a", A / "check.py")
CA = importlib.util.module_from_spec(spec)
sys.modules["pc_count_a"] = CA
spec.loader.exec_module(CA)
B = ROOT / "experiments/PC-COUNT-20261110-001B/PC-COUNT-20261110-001B-E001_small_sphere_degrees"
spec = importlib.util.spec_from_file_location("pc_count_b", B / "run.py")
RB = importlib.util.module_from_spec(spec)
sys.modules["pc_count_b"] = RB
spec.loader.exec_module(RB)
C, T = CA.C, CA.T
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)


def closure_contains_one(n, axioms, D, pc):
    """independent reference: RREF over python integers, columns by degree (highest monomials in the high bits)"""
    cols = [sum(1 << v for v in c) for d in range(D, -1, -1) for c in itertools.combinations(range(n), d)]
    N = len(cols)
    idx = {m: N - 1 - i for i, m in enumerate(cols)}
    deg = [0] * N
    for m, b in idx.items():
        deg[b] = bin(m).count("1")
    basis = {}

    def vec(poly):
        v = 0
        for m in poly:
            v ^= 1 << idx[m]
        return v

    def red(v):
        while v:
            b = v.bit_length() - 1
            if b not in basis:
                return v
            v ^= basis[b]
        return 0

    def ins(v):
        v = red(v)
        if not v:
            return False
        b = v.bit_length() - 1
        for k in [k for k, w in basis.items() if (w >> b) & 1]:
            basis[k] ^= v
        basis[b] = v
        return True
    for a in axioms:
        if max(bin(m).count("1") for m in a) > D:
            continue
        if pc:
            ins(vec(a))
        else:
            S = 0
            for m in a:
                S |= m
            da = max(bin(m).count("1") for m in a)
            free = [x for x in range(n) if not (S >> x) & 1]
            for s in range(D - da + 1):
                for c in itertools.combinations(free, s):
                    mm = sum(1 << x for x in c)
                    p = set()
                    for m in a:
                        p ^= {m | mm}
                    ins(vec(p))
        if 0 in basis:
            return True
    if pc:
        done = set()
        while True:
            todo = [b for b in basis if deg[b] <= D - 1 and (b, basis[b]) not in done]
            if not todo:
                break
            for b in todo:
                v = basis.get(b)
                if v is None:
                    continue
                done.add((b, v))
                mons = [cols[N - 1 - i] for i in range(v.bit_length()) if (v >> i) & 1]
                for x in range(n):
                    p = set()
                    for m in mons:
                        p ^= {m | (1 << x)}
                    ins(vec(p))
                    if 0 in basis:
                        return True
    return 0 in basis


def main():
    rng = random.Random(20261111)
    # 1. Lemma 1 at N = 4, holes of degree up to 5
    ok, n_x, n_ans, worst = True, 0, 0, 0
    for G in CA.graphs(4, rng, 200):
        edges = [(p, h) for p in range(5) for h in G[p]]
        for _ in range(64):
            x = {e: rng.randint(0, 1) for e in edges}
            f, g, holes_of = CA.reduce_to_left_pigeon(4, G, x)
            delta = max([3] + [len(v) for v in holes_of.values()])
            ans = [p for p in range(5) if C.left_pigeon_violation(f, g, p)]
            n_x += 1
            ok &= bool(ans)
            for p in ans:
                c, read = CA.decode(4, G, holes_of, x, p)
                n_ans += 1
                worst = max(worst, len(read))
                ok &= CA.falsified(4, G, x, c) and len(read) <= 2 * delta
    record("1_lemma_1_at_N_4", ok, {"graphs": 200, "assignments": n_x, "answers decoded": n_ans, "most reads": worst})
    # 2. the composed chain at N = 3
    ok2, n2, tri = True, 0, 0
    L = T.layout(4)
    for G in CA.graphs(3, rng, 20):
        edges = [(p, h) for p in range(4) for h in G[p]]
        x = {e: rng.randint(0, 1) for e in edges}
        f, g, holes_of = CA.reduce_to_left_pigeon(3, G, x)
        succ, pred = C.to_sink(3, f, g)
        col, route, clash, cr = T.colouring(L, succ, pred)
        full = [t for t, o in T.full_triangles(col, L["m"]) if o == 1]
        n2 += 1
        tri += len(full)
        ok2 &= not clash and bool(full)
        for t in full:
            v = T.back_map(succ, pred, T.triangle_node(L, t))
            c, read = CA.decode(3, G, holes_of, x, v)
            ok2 &= T.is_sink_solution(succ, pred, v) and C.left_pigeon_violation(f, g, v) and CA.falsified(3, G, x, c)
    record("2_chain_at_N_3", ok2, {"instances": n2, "grid side": L["m"], "counterclockwise full triangles decoded": tri})
    # 3. ticket B's degrees by the independent solver
    n2p, f2 = RB.formulas(2)
    n3p, f3 = RB.formulas(3)
    got = {"K_2 count pc refuted at 3": closure_contains_one(n2p, f2["count"], 3, True),
           "K_2 count ns refuted at 5": closure_contains_one(n2p, f2["count"], 5, False),
           "K_2 count ns refuted at 6": closure_contains_one(n2p, f2["count"], 6, False),
           "K_3 count pc refuted at 3": closure_contains_one(n3p, f3["count"], 3, True),
           "K_3 control pc refuted at 3": closure_contains_one(n3p, f3["control"], 3, True)}
    want = {"K_2 count pc refuted at 3": True, "K_2 count ns refuted at 5": False, "K_2 count ns refuted at 6": True,
            "K_3 count pc refuted at 3": False, "K_3 control pc refuted at 3": True}
    record("3_degrees_by_an_independent_solver", got == want, {"independent": got, "ticket B": want})
    out = {"epic": "PC-COUNT-20261110-001", "checks": OUT, "status": "passed" if all(v["pass"] for v in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
