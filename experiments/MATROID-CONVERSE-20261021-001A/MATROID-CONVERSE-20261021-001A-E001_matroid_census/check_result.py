#!/usr/bin/env python3
"""Independent check of MATROID-CONVERSE-20261021-001A-E001. It imports no producer code.

- Both Vamos relations are rebuilt (the codes from the recorded columns) and their free sets recomputed over all 256
  subsets with this file's own rank-free routine (projection sizes).
- Every recorded failure is rebuilt and verified with this file's own solver (index-order backtracking) and circuit
  routine: the two-copy joins of the Vamos circuit projections, the perturbation witnesses, the direct cases and
  fibre-distance cases of perturbations (by building the relevant two-copy join), and the Z6 control.
- Group systems: the recorded systems are re-solved; ranges, maximal normal subgroups (by brute force over subsets
  closed under multiplication), top images and free sets are recomputed; 20 fresh systems per group are added.
- Survivors of the perturbation part are re-decided against x+y+z=0 over Z3 on 150 fresh systems each.
- Summary counts are recomputed from the rows where the rows carry them.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "MATROID-CONVERSE-20261021-001A" / HERE.name
P = 7
SPECIAL = {(0, 1, 2, 3), (0, 1, 4, 5), (0, 1, 6, 7), (2, 3, 4, 5), (2, 3, 6, 7)}


def vamos_indep(Y):
    return len(Y) <= 3 or (len(Y) == 4 and tuple(sorted(Y)) not in SPECIAL)


def all_subsets(n):
    return [Y for k in range(1, n + 1) for Y in combinations(range(n), k)]


def solve(rels, doms, cons):
    n = len(doms)
    last = {}
    for r, c in cons:
        last.setdefault(max(c), []).append((rels[r] if isinstance(rels, dict) else rels, c))
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        for x in doms[i]:
            a[i] = x
            if all(tuple(a[v] for v in c) in R for R, c in last.get(i, ())):
                go(i + 1)

    go(0)
    return out


def cfn(S, n):
    rg = [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in memo:
            memo[Y] = len({tuple(t[i] for i in Y) for t in S}) < prod(rg[i] for i in Y)
        return memo[Y]

    return f


def circuits(f, n):
    return [Y for Y in all_subsets(n) if f(Y) and all(not f(tuple(x for x in Y if x != w)) for w in Y)]


def has_failure(f, n):
    cs = circuits(f, n)
    return any(not f(tuple(sorted((set(a) | set(b)) - {e}))) for a, b in combinations(cs, 2) for e in set(a) & set(b))


def verify_witness(f, w):
    C1, C2, e = tuple(w["C1"]), tuple(w["C2"]), w["e"]
    ok = lambda C: f(C) and all(not f(tuple(x for x in C if x != v)) for v in C)
    return ok(C1) and ok(C2) and not f(tuple(sorted((set(C1) | set(C2)) - {e})))


def two_copies_fail(K, k, shared, e):
    rg = [sorted({t[i] for t in K}) for i in range(k)]
    second, nxt = [], k
    for p in range(k):
        if p in shared:
            second.append(p)
        else:
            second.append(nxt)
            nxt += 1
    doms = rg + [rg[p] for p in range(k) if p not in shared]
    S = solve(K, doms, [(None, tuple(range(k))), (None, tuple(second))])
    return verify_witness(cfn(S, len(doms)), {"C1": list(range(k)), "C2": sorted(second), "e": e})


def fibres(K, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return g


def direct_case(K, k):
    for e in range(k):
        g = fibres(K, e)
        others = [i for i in range(k) if i != e]
        for size in range(k - 1):
            for T in combinations(range(k - 1), size):
                groups = {}
                for rest, fb in g.items():
                    groups.setdefault(tuple(rest[p] for p in T), []).append(fb)
                if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                    return e, [others[p] for p in T]
    return None


def fibre_composed_failure(K, e):
    fib = fibres(K, e)
    share = {(a, b) for f in fib.values() for a in f for b in f}
    dom = {t[e] for t in K}
    rel = {(a, a) for a in dom}
    for _ in range(len(dom)):
        rel = {(a, c) for (a, b) in rel for (b2, c) in share if b == b2}
        Kc = {rest[:e] + (c,) + rest[e:] for rest, f in fib.items() for c in {c for (a, c) in rel if a in f}}
        fs = [frozenset(x) for x in fibres(Kc, e).values()]
        if all(a & b for a in fs for b in fs):
            return any(len(x) < len(dom) for x in fs) and two_copies_fail(Kc, 3, {e}, e)
    return False


def group_from(gens, n):
    G = {tuple(range(n))}
    changed = True
    while changed:
        changed = False
        for x in list(G):
            for s in gens:
                y = tuple(x[s[i]] for i in range(n))
                if y not in G:
                    G.add(y)
                    changed = True
    G = sorted(G)
    idx = {g: i for i, g in enumerate(G)}
    mul = [[idx[tuple(a[b[i]] for i in range(n))] for b in G] for a in G]
    return G, mul


def maximal_normal(H, mul, order):
    """All subgroups of H by brute force over subsets closed under multiplication, then maximal normal ones."""
    H = sorted(H)
    inv = {h: next(j for j in range(order) if mul[h][j] == 0) for h in H}
    subs = []
    for mask in range(1 << len(H)):
        N = {H[i] for i in range(len(H)) if mask >> i & 1}
        if 0 in N and all(mul[a][b] in N for a in N for b in N):
            subs.append(frozenset(N))
    normals = [N for N in subs if N != frozenset(H) and all(mul[mul[h][m]][inv[h]] in N for h in H for m in N)]
    return [N for N in normals if not any(N < N2 for N2 in normals)]


GROUP_GENS = {"Z4": ([(1, 2, 3, 0)], 4), "Z9": ([tuple((i + 1) % 9 for i in range(9))], 9), "S3": ([(1, 0, 2), (1, 2, 0)], 3),
              "D5": ([(1, 2, 3, 4, 0), (0, 4, 3, 2, 1)], 5), "AGL(1,5)": ([(1, 2, 3, 4, 0), (0, 2, 4, 1, 3)], 5)}


def check_group_system(law, n, cons, mul, order, cache):
    S = solve(law, [list(range(order))] * n, cons)
    ranges = [frozenset(t[i] for t in S) for i in range(n)]
    mus = []
    for H in ranges:
        if H not in cache:
            cache[H] = maximal_normal(H, mul, order) if len(H) > 1 else []
        mus.append(cache[H][0] if len(cache[H]) == 1 else None)
    unique = all(len(cache[H]) == 1 for H in ranges if len(H) > 1)
    Sbar = list({tuple(frozenset(mul[t[i]][m] for m in mus[i]) if mus[i] else 0 for i in range(n)) for t in S})
    fS, fB = cfn(S, n), cfn(Sbar, n)
    primes = [len(H) // len(mus[i]) if mus[i] else 1 for i, H in enumerate(ranges)]
    mixing = any(len({primes[i] for i in C if primes[i] > 1}) > 1 for C in circuits(fS, n))
    return unique and not has_failure(fS, n) and all(fS(Y) == fB(Y) for Y in all_subsets(n)) and not mixing


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems, report = [], {}

    cols = next(r for r in rows if r["part"] == "vamos_columns")
    code = lambda cl: {tuple(sum(w[i] * c[i] for i in range(4)) % P for c in cl) for w in product(range(P), repeat=4)}
    rels = {"union of codes": code(cols["C1"]) | code(cols["C2"]),
            "support relation": {x for x in product((0, 1), repeat=8) if vamos_indep(tuple(i for i in range(8) if x[i]))}}
    vam = {}
    for row in (r for r in rows if r["part"] == "vamos"):
        S = list(rels[row["name"]])
        f = cfn(S, 8)
        exact = all((not f(Y)) == vamos_indep(Y) for Y in all_subsets(8))
        case = row["circuit_projection_case"]
        K = {tuple(t[i] for i in case["circuit"]) for t in S}
        dc = direct_case(K, 4)
        fails = two_copies_fail(K, 4, set(case["direct"]["T"]) | {case["direct"]["e"]}, case["direct"]["e"])
        vam[row["name"]] = {"vamos": exact, "direct_case_recomputed": dc is not None, "two_copies_fail": fails}
        if not (exact == row["free_sets_are_vamos"] and fails == case["two_copies_fail"] and dc is not None):
            problems.append(f"vamos {row['name']}: recheck differs")
    report["vamos"] = vam

    grp = {}
    rng = random.Random(99)
    for name, (gens, npts) in GROUP_GENS.items():
        G, mul = group_from(gens, npts)
        order, cache = len(G), {}
        recorded = [r for r in rows if r["part"] == "group" and r["group"] == name]
        ok = 0
        for r in recorded:
            law = {k: {tuple(t) for t in v} for k, v in r["law"].items()}
            res = check_group_system(law, r["n"], [(str(k), tuple(c)) for k, c in r["cons"]], mul, order, cache)
            ok += res == (r["matroid"] and r["equal_to_top_image"])
        fresh_ok = fresh = 0
        while fresh < 20:
            law = {}
            for j in range(rng.randint(1, 3)):
                gensub = [tuple(rng.randrange(order) for _ in range(3)) for _ in range(rng.randint(1, 2))]
                H = {tuple([0] * 3)} | set(gensub)
                changed = True
                while changed:
                    changed = False
                    for x in list(H):
                        for y in list(H):
                            z = tuple(mul[a][b] for a, b in zip(x, y))
                            if z not in H:
                                H.add(z)
                                changed = True
                if len(H) < order ** 3:
                    law[str(j)] = H
            if not law:
                continue
            n = rng.randint(3, 4)
            cons = [(rng.choice(list(law)), tuple(rng.randrange(n) for _ in range(3))) for _ in range(rng.randint(1, 3))]
            if len({v for _, c in cons for v in c}) < n:
                continue
            fresh += 1
            fresh_ok += check_group_system(law, n, cons, mul, order, cache)
        grp[name] = {"recorded": len(recorded), "recorded_agree": ok, "fresh": fresh, "fresh_ok": fresh_ok}
        if ok != len(recorded) or fresh_ok != fresh:
            problems.append(f"group {name}: recheck differs")
    report["groups"] = grp

    ctl = {}
    for r in (r for r in rows if r["part"] == "control"):
        if r["witness"]:
            q = 6 if r["name"] == "Z6" else 3
            R = {t for t in product(range(q), repeat=3) if sum(t) % q == 0}
            S = solve(R, [list(range(q))] * r["witness"]["n"], [(None, tuple(c)) for c in r["witness"]["cons"]])
            ctl[r["name"]] = verify_witness(cfn(S, r["witness"]["n"]), r["witness"])
        else:
            ctl[r["name"]] = None
    report["controls"] = ctl
    if ctl.get("Z6") is not True:
        problems.append("Z6 control witness does not verify")

    M = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    g = (0, 1, 2, 2)
    L = {t for t in product(range(4), repeat=3) if tuple(g[x] for x in t) in M}
    pert = {"rows": 0, "witnesses_verified": 0, "structural_verified": 0, "survivors": 0, "survivors_agree": 0}
    recount = {}
    for r in (r for r in rows if r["part"] == "perturbation"):
        B, q = (M, 3) if r["base"] == "M" else (L, 4)
        t = tuple(r["tuple"])
        K = B - {t} if r["kind"] == "remove" else B | {t}
        pert["rows"] += 1
        c = recount.setdefault(r["base"], {"failures": 0, "survivors": 0})
        if r["structural_case"] == "direct":
            dc = direct_case(K, 3)
            good = dc is not None and two_copies_fail(K, 3, set(dc[1]) | {dc[0]}, dc[0])
            pert["structural_verified"] += good
            c["failures"] += 1
            if not good:
                problems.append(f"perturbation {r['kind']} {t} of {r['base']}: direct case does not verify")
        elif r["structural_case"] == "fibre distance":
            good = any(fibre_composed_failure(K, e) for e in range(3))
            pert["structural_verified"] += good
            c["failures"] += 1
            if not good:
                problems.append(f"perturbation {r['kind']} {t} of {r['base']}: fibre distance does not verify")
        elif r["witness"]:
            w = r["witness"]
            S = solve(K, [list(range(q))] * w["n"], [(None, tuple(cc)) for cc in w["cons"]])
            good = verify_witness(cfn(S, w["n"]), w)
            pert["witnesses_verified"] += good
            c["failures"] += 1
            if not good:
                problems.append(f"perturbation {r['kind']} {t} of {r['base']}: witness does not verify")
        else:
            pert["survivors"] += 1
            c["survivors"] += 1
            agree = 0
            for _ in range(150):
                while True:
                    n = rng.randint(3, 6)
                    cons = [tuple(rng.randrange(n) for _ in range(3)) for _ in range(rng.randint(1, 6))]
                    if len({v for cc in cons for v in cc}) == n:
                        break
                SK = solve(K, [list(range(q))] * n, [(None, cc) for cc in cons])
                SM = solve(M, [list(range(3))] * n, [(None, cc) for cc in cons])
                fK, fM = cfn(SK, n), cfn(SM, n)
                agree += (not SK) or all(fK(Y) == fM(Y) for Y in all_subsets(n))
            pert["survivors_agree"] += agree == 150
    for base, c in recount.items():
        s = result["summary"]["perturbations"][base]
        if c["failures"] != s["failures_found"] or c["survivors"] != s["survivors"]:
            problems.append(f"perturbations of {base}: summary counts differ from rows")
    report["perturbations"] = pert
    if pert["survivors_agree"] != pert["survivors"]:
        problems.append("a survivor disagrees with M on fresh systems")

    status = "passed: every recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
