#!/usr/bin/env python3
"""Independent check of DIAGONAL-LEMMA-20261021-001A-E001. It imports no producer code.

- Every recorded resolution witness is rebuilt from its definition and verified by building the system that
  fails and deciding its circuits with this file's own solver (brute force over each variable's values,
  variables taken in index order) and its own circuit routine:
  - direct cases: two copies sharing the selector set and the eliminated variable;
  - fibre distance: the composed relation, built by relational composition of the fibre-sharing relation,
    then two copies sharing the variable;
  - diagonal derivations: the derived relation, then two copies;
  - positional systems and random systems: rebuilt from the recorded copies or constraints.
- Rectangularity and knot status are recomputed for every recorded knot.
- Shadow products: 200 fresh random systems per product are decided by brute force, comparing the product's
  constrained sets with M's and looking for failures; the recorded failure of the inner factor is rebuilt.
- The summary counts of the random and lifted parts are recomputed from the rows.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "DIAGONAL-LEMMA-20261021-001A" / HERE.name


def states(R, doms, cons):
    out = []
    for a in product(*doms):
        if all(tuple(a[v] for v in c) in R for c in cons):
            out.append(a)
    return out


def states_fast(R, doms, cons):
    """Backtracking in index order (a different order from the producer's)."""
    n = len(doms)
    last = {}
    for c in cons:
        last.setdefault(max(c), []).append(c)
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        for x in doms[i]:
            a[i] = x
            if all(tuple(a[v] for v in c) in R for c in last.get(i, ())):
                go(i + 1)

    go(0)
    return out


def constrained_fn(S, n):
    rg = [len({t[i] for t in S}) for i in range(n)]
    cache = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in cache:
            cache[Y] = len({tuple(t[i] for i in Y) for t in S}) < prod(rg[i] for i in Y)
        return cache[Y]

    return f


def is_circuit(S, n, C):
    f = constrained_fn(S, n)
    return f(C) and all(not f(tuple(x for x in C if x != w)) for w in C)


def fails(S, n, C1, C2, e):
    f = constrained_fn(S, n)
    return is_circuit(S, n, C1) and is_circuit(S, n, C2) and e in C1 and e in C2 and \
        not f(tuple(sorted((set(C1) | set(C2)) - {e})))


def knot(K, k):
    rg = [len({t[i] for t in K}) for i in range(k)]
    return k >= 3 and min(rg) >= 2 and is_circuit(list(K), k, tuple(range(k)))


def rectangular(K, k):
    for e in range(k):
        fib = {}
        for t in K:
            fib.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
        fs = [frozenset(x) for x in fib.values()]
        for a in fs:
            for b in fs:
                if a != b and a & b:
                    return False
    return True


def ranges_of(K, k):
    return [sorted({t[i] for t in K}) for i in range(k)]


def two_copies_fail(K, k, shared, e):
    """Copy 1 on variables 0..k-1; copy 2 shares the positions in `shared` (which include e) and has fresh others."""
    rg = ranges_of(K, k)
    second, nxt = [], k
    for p in range(k):
        if p in shared:
            second.append(p)
        else:
            second.append(nxt)
            nxt += 1
    doms = rg + [rg[p] for p in range(k) if p not in shared]
    S = states_fast(K, doms, [tuple(range(k)), tuple(second)])
    return fails(S, nxt, tuple(range(k)), tuple(sorted(second)), e)


def composed(K, k, e, steps):
    fib = {}
    for t in K:
        fib.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    share = {(a, b) for f in fib.values() for a in f for b in f}
    rel = {(a, a) for f in fib.values() for a in f}
    for _ in range(steps):
        rel = {(a, c) for (a, b) in rel for (b2, c) in share if b == b2}
    out = set()
    for rest, f in fib.items():
        for c in {c for (a, c) in rel if a in f}:
            out.add(rest[:e] + (c,) + rest[e:])
    return out


def diagonal(K, q):
    return {(a, b, c) for a in range(q) for b in range(q) for c in range(q)
            if any((a, a, h) in K and (b, c, h) in K for h in range(q))}


def verify_direct(K, k, d):
    return two_copies_fail(K, k, set(d["T"]) | {d["e"]}, d["e"])


def verify_positional(K, k, w):
    m = w["m"]
    used = sorted({p * m + t[p] for t in w["copies"] for p in range(k)})
    idx = {v: j for j, v in enumerate(used)}
    rg = ranges_of(K, k)
    doms = [rg[v // m] for v in used]
    cons = [tuple(idx[p * m + t[p]] for p in range(k)) for t in w["copies"]]
    S = states_fast(K, doms, cons)
    return fails(S, len(doms), tuple(w["C1"]), tuple(w["C2"]), w["e"]) and min(len(w["C1"]), len(w["C2"])) >= 3


def verify_random(K, k, q, w):
    S = states_fast(K, [list(range(q))] * w["n"], [tuple(c) for c in w["cons"]])
    return fails(S, w["n"], tuple(w["C1"]), tuple(w["C2"]), w["e"]) and min(len(w["C1"]), len(w["C2"])) >= 3


def verify_row(row, k, q):
    K = {tuple(t) for t in row["tuples"]}
    problems = []
    if not knot(K, k) or rectangular(K, k):
        problems.append("not a non-rectangular knot")
    ok = []
    if row.get("direct"):
        ok.append(verify_direct(K, k, row["direct"]))
    if row.get("fibre_distance"):
        fd = row["fibre_distance"]
        C = composed(K, k, fd["e"], fd["steps"])
        ok.append(knot(C, k) and two_copies_fail(C, k, {fd["e"]}, fd["e"]))
    if row.get("diagonal"):
        pm = row["diagonal"]["perm"]
        Kp = {tuple(t[pm[i]] for i in range(3)) for t in K}
        D = diagonal(Kp, q)
        dd = row["diagonal"]["derived_direct"]
        ok.append(knot(D, 3) and verify_direct(D, 3, dd))
    if row.get("positional"):
        ok.append(verify_positional(K, k, row["positional"]))
    if row.get("random_search"):
        ok.append(verify_random(K, k, q, row["random_search"]))
    if not all(ok):
        problems.append("a recorded witness does not verify")
    return problems, bool(ok) and all(ok)


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    report = {}

    for part, k in (("random_3", 3), ("random_4", 4)):
        recount = {}
        for row in (r for r in rows if r["part"] == part):
            q = row["q"]
            pr, resolved = verify_row(row, k, q)
            problems += [f"{part} q={q}: {p}" for p in pr]
            c = recount.setdefault(str(q), {"neither": 0, "resolved_neither": 0, "positional_resolved_neither": 0})
            if not row.get("direct"):
                c["neither"] += 1
                c["resolved_neither"] += resolved
                c["positional_resolved_neither"] += bool(row.get("fibre_distance") or row.get("positional"))
        for q, c in recount.items():
            s = result["summary"][part][q]
            if c["neither"] != s["neither"] or c["neither"] - c["resolved_neither"] != s["unresolved"]:
                problems.append(f"{part} q={q}: summary counts differ from rows")
        report[part] = recount

    acts = {}
    for row in (r for r in rows if r["part"] == "action"):
        K = {tuple(t) for t in row["tuples"]}
        w = row.get("positional_m2") or row.get("positional_m3")
        verified = bool(w) and verify_positional(K, 3, w)
        acts[row["name"]] = {"knot": knot(K, 3), "rectangular": rectangular(K, 3), "failure_verified": verified}
        if bool(w) != verified:
            problems.append(f"action {row['name']}: witness does not verify")
        if knot(K, 3) != row["knot"] or rectangular(K, 3) != row["rectangular"]:
            problems.append(f"action {row['name']}: knot or rectangularity differs")
    report["actions"] = acts

    rng = random.Random(77)
    shadows = []
    for row in (r for r in rows if r["part"] == "shadow"):
        K = {tuple(t) for t in row["tuples"]}
        M = {tuple(t) for t in row["M"]}
        inner = {tuple(t) for t in row["inner"]}
        k, q, qm, qb = row["k"], row["domain"], row["qm"], row["qb"]
        nmax = 5 if q <= 6 else (4 if k == 3 else 6)
        checked = equal = failures = 0
        while checked < 200:
            n = rng.randint(k, nmax)
            cons = [tuple(rng.randrange(n) for _ in range(k)) for _ in range(rng.randint(1, 5))]
            if len({v for c in cons for v in c}) < n:
                continue
            SK = states_fast(K, [list(range(q))] * n, cons)
            if not SK:
                continue
            SM = states_fast(M, [list(range(qm))] * n, cons)
            fK, fM = constrained_fn(SK, n), constrained_fn(SM, n)
            subsets = [Y for size in range(1, n + 1) for Y in combinations(range(n), size)]
            checked += 1
            equal += all(fK(Y) == fM(Y) for Y in subsets)
            circuits = [Y for Y in subsets if fK(Y) and all(not fK(tuple(x for x in Y if x != w)) for w in Y)]
            failures += any(not fK(tuple(sorted((set(C1) | set(C2)) - {e})))
                            for C1, C2 in combinations(circuits, 2) for e in set(C1) & set(C2))
        ex = row.get("inner_failure")
        if row["inner_failures"] > 0:
            inner_ok = bool(ex) and fails(states_fast(inner, [list(range(qb))] * ex["n"], [tuple(c) for c in ex["cons"]]),
                                          ex["n"], tuple(ex["C1"]), tuple(ex["C2"]), ex["e"])
        else:
            inner_ok = ex is None  # nothing recorded, nothing to rebuild; the prediction's own clause decides

        nonrect_knot = knot(K, k) and not rectangular(K, k)
        shadows.append({"name": row["name"], "checked": checked, "equal_to_M": equal, "failures": failures,
                        "inner_failure_verified": inner_ok, "non_rectangular_knot": nonrect_knot})
        if equal != checked or failures or not inner_ok or not nonrect_knot:
            problems.append(f"shadow {row['name']}: recheck differs")
    report["shadows"] = shadows

    lifted = {}
    for row in (r for r in rows if r["part"] == "lifted"):
        pr, resolved = verify_row(row, 3, row["q"])
        problems += [f"lifted {row['g']}: {p}" for p in pr]
        key = "".join(map(str, row["g"]))
        c = lifted.setdefault(key, {"knots": 0, "resolved": 0})
        c["knots"] += 1
        c["resolved"] += resolved
    for key, c in lifted.items():
        s = result["summary"]["lifted"][key]
        if c["knots"] != s["non_rectangular_knots"] or c["knots"] - c["resolved"] != s["unresolved"]:
            problems.append(f"lifted {key}: summary counts differ from rows")
    report["lifted"] = lifted

    status = "passed: every recorded witness and recount agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
