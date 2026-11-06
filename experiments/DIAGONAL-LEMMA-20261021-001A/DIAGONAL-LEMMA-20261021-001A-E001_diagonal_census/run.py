#!/usr/bin/env python3
"""Census for DIAGONAL-LEMMA-20261021-001A-E001 (contract.json): where the diagonal lemma holds.

Parts:
- random 3-variable knots on 3, 4, 5 and 6 values (L1, L2);
- random 4-variable knots on 2 and 3 values (L3);
- group-action knots c = g(u) (L4);
- shadow products M x K, decided by brute force over the product's allowed states (L5);
- 3-variable knots on 4 and 5 values lifted from x+y+z=0 over Z3 (L6).

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, permutations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "DIAGONAL-LEMMA-20261021-001A" / HERE.name
NEITHER_BOOLEAN = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}


# ------------------------------------------------------------------ relations

def proj(S, Y):
    return {tuple(t[i] for i in Y) for t in S}


def ranges(S, k):
    return [sorted({t[i] for t in S}) for i in range(k)]


def is_knot(K, k):
    if not K:
        return False
    rg = [len(r) for r in ranges(K, k)]
    if k < 3 or any(r < 2 for r in rg):
        return False
    return all(len(proj(K, Y)) == prod(rg[i] for i in Y) for Y in combinations(range(k), k - 1)) and len(K) < prod(rg)


def fibres(K, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return {key: frozenset(v) for key, v in g.items()}


def rectangular(K, k):
    for e in range(k):
        fs = set(fibres(K, e).values())
        if any(a != b and a & b for a in fs for b in fs):
            return False
    return True


def direct_case(K, k):
    """A variable e and a set T of at most k-2 others such that, for each assignment of T, the e-fibres pairwise meet."""
    for e in range(k):
        g = fibres(K, e)
        others = [i for i in range(k) if i != e]
        for size in range(k - 1):
            for T in combinations(range(k - 1), size):
                groups = {}
                for rest, f in g.items():
                    groups.setdefault(tuple(rest[p] for p in T), []).append(f)
                if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                    return {"kind": "meeting" if size == 0 else "selector", "e": e, "T": [others[p] for p in T]}
    return None


def fibre_distance(K, k):
    """Smallest k with composed fibres pairwise meeting while one is not the whole range, at some variable."""
    for e in range(k):
        fs = list(set(fibres(K, e).values()))
        dom = {t[e] for t in K}
        adj = {v: set() for v in dom}
        for f in fs:
            for a in f:
                adj[a] |= f
        balls = fs
        for step in range(1, len(dom) + 1):
            balls = [frozenset(set().union(*(adj[a] for a in b))) for b in balls]
            if all(a & b for a in balls for b in balls):
                if any(len(b) < len(dom) for b in balls):
                    return {"e": e, "steps": step}
                break
    return None


def diagonal(K, q):
    return {(a, b, c) for a in range(q) for b in range(q) for c in range(q)
            if any((a, a, h) in K and (b, c, h) in K for h in range(q))}


def diagonal_case(K, q):
    for pm in permutations(range(3)):
        Kp = {tuple(t[pm[i]] for i in range(3)) for t in K}
        D = diagonal(Kp, q)
        if is_knot(D, 3):
            d = direct_case(D, 3)
            if d:
                return {"perm": list(pm), "derived_direct": d}
    return None


# ------------------------------------------------------------------ systems

def solve(R, doms, cons):
    """Allowed states of a system: doms[v] is variable v's candidate values, cons lists tuples of variable indices."""
    n = len(doms)
    order = []
    for c in cons:
        for v in c:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    check_at = {}
    for c in cons:
        check_at.setdefault(max(pos[v] for v in c), []).append(c)
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in doms[v]:
            a[v] = x
            if all(tuple(a[w] for w in c) in R for c in check_at.get(i, ())):
                go(i + 1)
        a[v] = None

    go(0)
    return out


def circuits_and_failure(S, n, knots_only=True):
    if not S:
        return [], None, {}
    rg = [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def constrained(Y):
        if Y not in memo:
            memo[Y] = len(proj(S, Y)) < prod(rg[i] for i in Y)
        return memo[Y]

    found = []
    for size in range(1, n + 1):
        for Y in combinations(range(n), size):
            if not any(set(C) <= set(Y) for C in found) and constrained(Y):
                found.append(Y)
    for C1, C2 in combinations(found, 2):
        if knots_only and min(len(C1), len(C2)) < 3:
            continue
        for e in sorted(set(C1) & set(C2)):
            if not constrained(tuple(sorted((set(C1) | set(C2)) - {e}))):
                return found, {"C1": list(C1), "C2": list(C2), "e": e}, constrained
    return found, None, constrained


def positional_system(K, k, m, copies):
    """Variables: position p, index i -> p*m+i, compacted to the variables used. Returns (doms, cons)."""
    rg = ranges(K, k)
    used = sorted({p * m + t[p] for t in copies for p in range(k)})
    idx = {v: j for j, v in enumerate(used)}
    doms = [rg[v // m] for v in used]
    cons = [tuple(idx[p * m + t[p]] for p in range(k)) for t in copies]
    return doms, cons


def positional_search(K, k, m, max_copies, sample=None, rng=None):
    base = (0,) * k
    rest = [t for t in product(range(m), repeat=k) if t != base]
    if sample is None:
        candidates = ([base] + list(c) for size in range(1, max_copies) for c in combinations(rest, size))
    else:
        candidates = ([base] + rng.sample(rest, rng.randint(2, min(max_copies - 1, len(rest)))) for _ in range(sample))
    for copies in candidates:
        doms, cons = positional_system(K, k, m, copies)
        S = solve(K, doms, cons)
        _, fail, _ = circuits_and_failure(S, len(doms))
        if fail:
            return {"m": m, "copies": [list(t) for t in copies], **fail}
    return None


def random_system(rng, k, nmax):
    while True:
        n = rng.randint(k, nmax)
        cons = [tuple(rng.randrange(n) for _ in range(k)) for _ in range(rng.randint(1, 5))]
        if len({v for c in cons for v in c}) == n:
            return n, cons


def random_search(K, k, q, nmax, count, rng):
    for _ in range(count):
        n, cons = random_system(rng, k, nmax)
        S = solve(K, [list(range(q))] * n, cons)
        _, fail, _ = circuits_and_failure(S, n)
        if fail:
            return {"n": n, "cons": [list(c) for c in cons], **fail}
    return None


# ------------------------------------------------------------------ parts

def random_knot(rng, q, k, lo, hi):
    while True:
        p = rng.uniform(lo, hi)
        K = {t for t in product(range(q), repeat=k) if rng.random() < p}
        if is_knot(K, k) and all(len(r) == q for r in ranges(K, k)) and not rectangular(K, k):
            return K


def analyse_random(K, k, q, with_diagonal):
    row = {"q": q, "k": k, "tuples": sorted(K)}
    d = direct_case(K, k)
    row["direct"] = d
    if d:
        row["resolved"] = row["positional_resolved"] = True
        return row
    row["fibre_distance"] = fibre_distance(K, k)
    row["diagonal"] = diagonal_case(K, q) if with_diagonal else None
    row["positional"] = positional_search(K, k, 2, 5 if k == 3 else 4)
    row["positional_resolved"] = bool(row["fibre_distance"] or row["positional"])
    row["resolved"] = bool(row["positional_resolved"] or row["diagonal"])
    return row


def part_random(rng, k, qs, lo, hi, target, cap, rows):
    summary = {}
    for q in qs:
        t0 = time.time()
        s = {"non_rectangular_knots": 0, "direct": 0, "neither": 0, "fibre_distance": 0, "diagonal": 0, "positional": 0,
             "resolved": 0, "positional_resolved": 0, "unresolved": 0}
        direct_kept = 0
        while s["neither"] < target and time.time() - t0 < cap:
            K = random_knot(rng, q, k, lo, hi)
            s["non_rectangular_knots"] += 1
            row = analyse_random(K, k, q, with_diagonal=(k == 3))
            if row["direct"]:
                s["direct"] += 1
                s["resolved"] += 1
                s["positional_resolved"] += 1
                if direct_kept < 5:
                    direct_kept += 1
                    rows.append({"part": f"random_{k}", **row})
                continue
            s["neither"] += 1
            s["fibre_distance"] += bool(row["fibre_distance"])
            s["diagonal"] += bool(row["diagonal"])
            s["positional"] += bool(row["positional"])
            s["resolved"] += row["resolved"]
            s["positional_resolved"] += row["positional_resolved"]
            s["unresolved"] += not row["resolved"]
            rows.append({"part": f"random_{k}", **row})
        s["seconds"] = round(time.time() - t0, 1)
        summary[str(q)] = s
        print(f"random {k}-variable q={q}: {s}", flush=True)
    return summary


def group(gens, n):
    G = {tuple(range(n))}
    frontier = list(G)
    while frontier:
        g = frontier.pop()
        for s in gens:
            h = tuple(s[g[i]] for i in range(n))
            if h not in G:
                G.add(h)
                frontier.append(h)
    return sorted(G)


def action_knot(perms, n):
    return {(u, gi, p[u]) for gi, p in enumerate(perms) for u in range(n)}


def part_actions(rng, rows):
    roster = {
        "S3 on 3 points": (group([(1, 0, 2), (1, 2, 0)], 3), 3),
        "D4 on the corners of a square": (group([(1, 2, 3, 0), (0, 3, 2, 1)], 4), 4),
        "A4 on 4 points": (group([(1, 2, 0, 3), (0, 2, 3, 1)], 4), 4),
        "AGL(1,5) on 5 points": ([tuple((a * x + b) % 5 for x in range(5)) for a in range(1, 5) for b in range(5)], 5),
        "regular Z3 (control)": ([tuple((x + b) % 3 for x in range(3)) for b in range(3)], 3),
    }
    summary = {}
    for name, (perms, n) in roster.items():
        t0 = time.time()
        K = action_knot(perms, n)
        row = {"part": "action", "name": name, "group_order": len(perms), "points": n, "tuples": sorted(K),
               "knot": is_knot(K, 3), "rectangular": rectangular(K, 3), "direct": direct_case(K, 3)}
        row["positional_m2"] = positional_search(K, 3, 2, 8)
        row["positional_m3"] = None if row["positional_m2"] else positional_search(K, 3, 3, 7, sample=400, rng=rng)
        row["failure_found"] = bool(row["positional_m2"] or row["positional_m3"])
        row["seconds"] = round(time.time() - t0, 1)
        rows.append(row)
        summary[name] = {k: row[k] for k in ("group_order", "points", "knot", "rectangular", "failure_found", "seconds")}
        summary[name]["direct"] = bool(row["direct"])
        summary[name]["witness_copies"] = len((row["positional_m2"] or row["positional_m3"] or {}).get("copies", []))
        print(f"action {name}: {summary[name]}", flush=True)
    return summary


def shadow_product(M, qm, inner, qb):
    return {tuple(a * qb + b for a, b in zip(s, t)) for s in M for t in inner}


def part_shadows(rng, rows):
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    M4 = {t for t in product(range(2), repeat=4) if sum(t) % 2 == 0}
    specs = [("Z3 sum-zero, h onto 2 values", M3, 3, 3, 2), ("Z3 sum-zero, h onto 2 values", M3, 3, 3, 2),
             ("Z3 sum-zero, h onto 2 values", M3, 3, 3, 2), ("Z3 sum-zero, h the identity", M3, 3, 3, 3),
             ("4-ary Z2 sum-zero, h the identity", M4, 2, 4, 2), ("4-ary Z2 sum-zero, h the identity", M4, 2, 4, 2)]
    summary = []
    for name, M, qm, k, qb in specs:
        while True:
            if qb == qm:
                h = list(range(qm))
            else:
                while True:
                    h = [rng.randrange(qb) for _ in range(qm)]
                    if len(set(h)) == qb:
                        break
            inner = {tuple(h[x] for x in t) for t in M}
            extra = rng.randint(0, 2)
            pool = [t for t in product(range(qb), repeat=k) if t not in inner]
            inner |= set(rng.sample(pool, min(extra, len(pool))))
            K = shadow_product(M, qm, inner, qb)
            if len(inner) < qb ** k and is_knot(K, k) and not rectangular(K, k):
                break
        q = qm * qb
        nmax = 5 if q <= 6 else (4 if k == 3 else 6)
        s = {"name": name, "h": h, "inner": sorted(inner), "domain": q, "k": k, "systems": 0, "equal_to_M": 0,
             "product_failures": 0, "inner_failures": 0}
        examples = {}
        t0 = time.time()
        while s["systems"] < 1500:
            n, cons = random_system(rng, k, nmax)
            SK = solve(K, [list(range(q))] * n, cons)
            if not SK:
                continue
            SM = solve(M, [list(range(qm))] * n, cons)
            SI = solve(inner, [list(range(qb))] * n, cons)
            _, fK, cK = circuits_and_failure(SK, n, knots_only=False)
            _, fM, cM = circuits_and_failure(SM, n, knots_only=False)
            _, fI, _ = circuits_and_failure(SI, n, knots_only=False)
            allY = [Y for size in range(1, n + 1) for Y in combinations(range(n), size)]
            equal = all(cK(Y) == cM(Y) for Y in allY)
            s["systems"] += 1
            s["equal_to_M"] += equal
            s["product_failures"] += fK is not None
            s["inner_failures"] += fI is not None
            if fI is not None and "inner_failure" not in examples:
                examples["inner_failure"] = {"n": n, "cons": [list(c) for c in cons], **fI}
            if len(examples.get("systems", [])) < 40:
                examples.setdefault("systems", []).append({"n": n, "cons": [list(c) for c in cons], "equal": equal,
                                                           "product_failure": fK is not None})
        s["seconds"] = round(time.time() - t0, 1)
        rows.append({"part": "shadow", **s, "tuples": sorted(K), "M": sorted(M), "qm": qm, "qb": qb, **examples})
        summary.append(s)
        print(f"shadow {name}: { {x: s[x] for x in ('domain', 'systems', 'equal_to_M', 'product_failures', 'inner_failures')} }", flush=True)
    return summary


def part_lifted(rng, rows):
    M3 = sorted(t for t in product(range(3), repeat=3) if sum(t) % 3 == 0)
    summary = {}
    for g in ((0, 1, 2, 2), (0, 1, 2, 2, 2), (0, 1, 1, 2, 2)):
        q = len(g)
        pre = {a: [x for x in range(q) if g[x] == a] for a in range(3)}
        s = {"non_rectangular_knots": 0, "direct": 0, "fibre_distance": 0, "diagonal": 0, "positional": 0, "random_search": 0,
             "unresolved": 0}
        t0 = time.time()
        tries = 0
        while s["non_rectangular_knots"] < (40 if q == 4 else 20) and tries < 20000:
            tries += 1
            K = set()
            for t in M3:
                lifts = list(product(*(pre[a] for a in t)))
                K |= set(rng.sample(lifts, rng.randint(1, len(lifts))))
            if not (is_knot(K, 3) and all(len(r) == q for r in ranges(K, 3)) and not rectangular(K, 3)):
                continue
            s["non_rectangular_knots"] += 1
            row = {"part": "lifted", "g": list(g), "q": q, "tuples": sorted(K), "direct": direct_case(K, 3)}
            if row["direct"]:
                s["direct"] += 1
            else:
                row["fibre_distance"] = fibre_distance(K, 3)
                row["diagonal"] = None if row["fibre_distance"] else diagonal_case(K, q)
                row["positional"] = None if (row["fibre_distance"] or row["diagonal"]) else positional_search(K, 3, 2, 5)
                done = row["fibre_distance"] or row["diagonal"] or row["positional"]
                row["random_search"] = None if done else random_search(K, 3, q, 5, 2000, rng)
                for key in ("fibre_distance", "diagonal", "positional", "random_search"):
                    if row[key]:
                        s[key] += 1
                        break
                else:
                    s["unresolved"] += 1
            row["resolved"] = bool(row["direct"] or row.get("fibre_distance") or row.get("diagonal") or row.get("positional")
                                   or row.get("random_search"))
            rows.append(row)
        s["seconds"] = round(time.time() - t0, 1)
        summary["".join(map(str, g))] = s
        print(f"lifted g={g}: {s}", flush=True)
    return summary


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261021)
    rows = []
    t_all = time.time()
    summary = {}
    control_diag = diagonal_case(NEITHER_BOOLEAN, 2)
    summary["random_3"] = part_random(rng, 3, (3, 4, 5, 6), 0.25, 0.97, 40, 600, rows)
    summary["random_4"] = part_random(rng, 4, (2, 3), 0.4, 0.97, 25, 600, rows)
    summary["actions"] = part_actions(rng, rows)
    summary["shadows"] = part_shadows(rng, rows)
    summary["lifted"] = part_lifted(rng, rows)
    r3, r4, ac, sh, li = (summary[x] for x in ("random_3", "random_4", "actions", "shadows", "lifted"))
    predictions = {
        "L1": all(v["unresolved"] == 0 and v["neither"] > 0 for v in r3.values()),
        "L2": all(v["positional_resolved"] == v["non_rectangular_knots"] for v in r3.values()),
        "L3": all(v["positional_resolved"] == v["non_rectangular_knots"] and v["neither"] > 0 for v in r4.values()),
        "L4": all(v["knot"] and not v["rectangular"] and not v["direct"] and v["failure_found"]
                  for name, v in ac.items() if "control" not in name)
        and not ac["regular Z3 (control)"]["failure_found"],
        "L5": all(s["equal_to_M"] == s["systems"] and s["product_failures"] == 0 and s["inner_failures"] > 0 for s in sh),
        "L6": all(v["unresolved"] == 0 for v in li.values()),
    }
    controls = {
        "C1_boolean_neither_knot_resolved_by_diagonal": {"witness": control_diag, "passed": control_diag is not None},
        "C2_regular_action_no_failure": {"passed": not ac["regular Z3 (control)"]["failure_found"]},
        "C3_inner_factor_alone_fails": {"passed": all(s["inner_failures"] > 0 for s in sh)},
        "C4_neither_knots_exist": {"passed": any(v["neither"] > 0 for v in r3.values())},
    }
    result = {
        "schema_version": 1, "experiment_id": "DIAGONAL-LEMMA-20261021-001A-E001", "status": "complete",
        "evidence_stage": "exploratory", "summary": summary, "predictions": predictions, "controls": controls,
        "signal": all(predictions.values()) and all(c["passed"] for c in controls.values()),
        "seconds": round(time.time() - t_all, 1),
    }
    (OUT / "raw_rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"predictions": predictions, "controls": {k: v["passed"] for k, v in controls.items()},
                      "signal": result["signal"], "seconds": result["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
