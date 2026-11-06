#!/usr/bin/env python3
"""Census for MATROID-CONVERSE-20261021-001A-E001 (contract.json).

Parts:
- the Vamos matroid as the free sets of a support relation and of a union of two GF(7) codes, and the direct cases of
  their circuit projections (Q1, Q2);
- random laws of subgroups over Z4, Z9, S3, D5 and AGL(1,5): free sets against the image in the product of tops (Q3);
- controls x+y+z=0 over Z6 and Z3 (C1, C2);
- every single-tuple perturbation of x+y+z=0 over Z3 and of its lift with 2 doubled (Q4, Q5).

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "MATROID-CONVERSE-20261021-001A" / HERE.name
P7 = 7


# ------------------------------------------------------------------ relations and systems

def proj(S, Y):
    return {tuple(t[i] for i in Y) for t in S}


def solve(R, doms, cons):
    """R may be a single relation or a dict {name: relation}; cons are (name or None, tuple of variables)."""
    n = len(doms)
    order = []
    for _, c in cons:
        for v in c:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    check_at = {}
    for k, c in cons:
        check_at.setdefault(max(pos[v] for v in c), []).append((R[k] if isinstance(R, dict) else R, c))
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in doms[v]:
            a[v] = x
            if all(tuple(a[w] for w in c) in rel for rel, c in check_at.get(i, ())):
                go(i + 1)
        a[v] = None

    go(0)
    return out


def constrained_fn(S, n, ranges=None):
    rg = ranges if ranges is not None else [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in memo:
            memo[Y] = len(proj(S, Y)) < prod(rg[i] for i in Y)
        return memo[Y]

    return f


def subsets(n):
    return [Y for size in range(1, n + 1) for Y in combinations(range(n), size)]


def circuits(f, n):
    found = []
    for Y in subsets(n):
        if not any(set(C) <= set(Y) for C in found) and f(Y):
            found.append(Y)
    return found


def failure_of(f, n):
    found = circuits(f, n)
    for C1, C2 in combinations(found, 2):
        for e in sorted(set(C1) & set(C2)):
            if not f(tuple(sorted((set(C1) | set(C2)) - {e}))):
                return {"C1": list(C1), "C2": list(C2), "e": e}, found
    return None, found


def is_knot(K, k):
    rg = [len({t[i] for t in K}) for i in range(k)]
    if k < 3 or min(rg) < 2:
        return False
    return all(len(proj(K, Y)) == prod(rg[i] for i in Y) for Y in combinations(range(k), k - 1)) and len(K) < prod(rg)


def fibres(K, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return {key: frozenset(v) for key, v in g.items()}


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
                    return {"e": e, "T": [others[p] for p in T]}
    return None


def fibre_distance(K, k):
    for e in range(k):
        fs = list(set(fibres(K, e).values()))
        dom = {t[e] for t in K}
        adj = {v: set() for v in dom}
        for fb in fs:
            for a in fb:
                adj[a] |= fb
        balls = fs
        for _ in range(len(dom)):
            balls = [frozenset(set().union(*(adj[a] for a in b))) for b in balls]
            if all(a & b for a in balls for b in balls):
                if any(len(b) < len(dom) for b in balls):
                    return {"e": e}
                break
    return None


def two_copies(K, k, shared):
    rg = [sorted({t[i] for t in K}) for i in range(k)]
    second, nxt = [], k
    for p in range(k):
        if p in shared:
            second.append(p)
        else:
            second.append(nxt)
            nxt += 1
    doms = rg + [rg[p] for p in range(k) if p not in shared]
    return doms, [(None, tuple(range(k))), (None, tuple(second))], tuple(sorted(second))


def random_system(rng, k, nmax, cmax):
    while True:
        n = rng.randint(k, nmax)
        cons = [tuple(rng.randrange(n) for _ in range(k)) for _ in range(rng.randint(1, cmax))]
        if len({v for c in cons for v in c}) == n:
            return n, cons


# ------------------------------------------------------------------ part 1: Vamos

PAIRS = {"A": (0, 1), "B": (2, 3), "C": (4, 5), "D": (6, 7)}
SPECIAL = [tuple(sorted(PAIRS[x] + PAIRS[y])) for x, y in (("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"))]


def vamos_independent(Y):
    return len(Y) <= 3 or (len(Y) == 4 and tuple(sorted(Y)) not in SPECIAL)


def gf_rank(vecs):
    rows, r = [list(v) for v in vecs], 0
    for c in range(4):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % P7), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], P7 - 2, P7)
        rows[r] = [x * inv % P7 for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % P7:
                fct = rows[i][c]
                rows[i] = [(x - fct * y) % P7 for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def part_vamos(rng, rows):
    point = (1, 0, 0, 0)
    target1 = {Y: vamos_independent(Y) and tuple(sorted(Y)) != (4, 5, 6, 7) for Y in subsets(8)}
    for attempt in range(10000):
        u = [tuple(rng.randrange(P7) for _ in range(4)) for _ in range(4)]
        cols1 = [w for ux in u for w in (ux, tuple((a + b) % P7 for a, b in zip(ux, point)))]
        if all((gf_rank([cols1[i] for i in Y]) == len(Y)) == target1[Y] for Y in target1):
            break
    e = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    add = lambda x, y, k=1: tuple((a + k * b) % P7 for a, b in zip(x, y))
    cols2 = [(1, 2, 3, 5), (1, 2, 3, 5), add(e[0], e[2]), add(e[0], e[2], 2), add(e[0], e[1]), add(e[0], e[1], 2),
             add(e[2], e[3]), add(e[2], e[3], 2)]
    code = lambda cols: {tuple(sum(w[i] * c[i] for i in range(4)) % P7 for c in cols) for w in product(range(P7), repeat=4)}
    union = code(cols1) | code(cols2)
    support = {x for x in product((0, 1), repeat=8) if vamos_independent(tuple(i for i in range(8) if x[i]))}
    summary = {}
    for name, S in (("support relation", support), ("union of codes", union)):
        f = constrained_fn(list(S), 8)
        exact = all((not f(Y)) == vamos_independent(Y) for Y in subsets(8))
        case = None
        for C in SPECIAL:
            K = proj(S, C)
            d = direct_case(K, 4) if is_knot(K, 4) else None
            if d:
                doms, cons, C2 = two_copies(K, 4, set(d["T"]) | {d["e"]})
                J = solve(K, doms, cons)
                g = constrained_fn(J, len(doms))
                circ = set(circuits(g, len(doms)))
                fails = (0, 1, 2, 3) in circ and C2 in circ and not g(tuple(sorted(({0, 1, 2, 3} | set(C2)) - {d["e"]})))
                case = {"circuit": list(C), "direct": d, "two_copies_fail": fails}
                break
        summary[name] = {"tuples": len(S), "free_sets_are_vamos": exact, "circuit_projection_case": case}
        rows.append({"part": "vamos", "name": name, **summary[name]})
        print(f"vamos {name}: {summary[name]}", flush=True)
    summary["columns"] = {"C1": cols1, "C2": cols2, "attempts": attempt + 1}
    rows.append({"part": "vamos_columns", "C1": cols1, "C2": cols2})
    return summary


# ------------------------------------------------------------------ part 2: group laws

def perm_group(gens, n):
    G = {tuple(range(n))}
    frontier = list(G)
    while frontier:
        x = frontier.pop()
        for s in gens:
            y = tuple(s[x[i]] for i in range(n))
            if y not in G:
                G.add(y)
                frontier.append(y)
    G = sorted(G)
    idx = {g: i for i, g in enumerate(G)}
    mul = [[idx[tuple(a[b[i]] for i in range(n))] for b in G] for a in G]
    return G, mul


def generated(elems, mul, k):
    H = {tuple([0] * k)} | set(elems)
    frontier = list(H)
    while frontier:
        x = frontier.pop()
        for y in list(H):
            for z in (tuple(mul[a][b] for a, b in zip(x, y)), tuple(mul[a][b] for a, b in zip(y, x))):
                if z not in H:
                    H.add(z)
                    frontier.append(z)
    return frozenset(H)


def tops(mul, order):
    subs = {frozenset(t[0] for t in generated([(a,), (b,)], mul, 1)) for a in range(order) for b in range(order)}
    inv = [next(j for j in range(order) if mul[i][j] == 0) for i in range(order)]
    out = {}
    for H in subs:
        if len(H) == 1:
            out[H] = None
            continue
        normals = [N for N in subs if N < H and all(mul[mul[h][m]][inv[h]] in N for h in H for m in N)]
        maximal = [N for N in normals if not any(N < N2 for N2 in normals)]
        out[H] = maximal
    return out


GROUPS = {
    "Z4": ([(1, 2, 3, 0)], 4, 6),
    "Z9": ([tuple((i + 1) % 9 for i in range(9))], 9, 5),
    "S3": ([(1, 0, 2), (1, 2, 0)], 3, 6),
    "D5": ([(1, 2, 3, 4, 0), (0, 4, 3, 2, 1)], 5, 5),
    "AGL(1,5)": ([(1, 2, 3, 4, 0), (0, 2, 4, 1, 3)], 5, 4),
}


def part_groups(rng, rows):
    summary = {}
    for name, (gens, npts, nmax) in GROUPS.items():
        G, mul = perm_group(gens, npts)
        q = len(G)
        top = tops(mul, q)
        unique = all(v is None or len(v) == 1 for v in top.values())
        s = {"order": q, "subgroups": len(top), "unique_maximal_normal": unique, "systems": 0, "matroids": 0,
             "equal_to_top_image": 0, "circuits_mixing_primes": 0, "systems_with_two_top_primes": 0, "top_primes": [],
             "unknown_ranges": 0}
        primes_seen = set()
        t0 = time.time()
        while s["systems"] < 150 and time.time() - t0 < 300:
            law = {}
            for j in range(rng.randint(1, 3)):
                H = generated([tuple(rng.randrange(q) for _ in range(3)) for _ in range(rng.randint(1, 2))], mul, 3)
                if len(H) < q ** 3:
                    law[j] = H
            if not law:
                continue
            n = rng.randint(3, nmax)
            cons = [(rng.choice(list(law)), tuple(rng.randrange(n) for _ in range(3))) for _ in range(rng.randint(1, 4))]
            if len({v for _, c in cons for v in c}) < n:
                continue
            S = solve(law, [list(range(q))] * n, cons)
            ranges = [frozenset(t[i] for t in S) for i in range(n)]
            s["unknown_ranges"] += sum(1 for H in ranges if H not in top)
            mus = [top[H][0] if top.get(H) else None for H in ranges]
            primes = [len(H) // len(mus[i]) if mus[i] is not None else 1 for i, H in enumerate(ranges)]
            coset = [{h: frozenset(mul[h][m] for m in mus[i]) for h in ranges[i]} if mus[i] is not None else None
                     for i in range(n)]
            Sbar = list({tuple(coset[i][t[i]] if coset[i] else 0 for i in range(n)) for t in S})
            fS = constrained_fn(S, n)
            fB = constrained_fn(Sbar, n)
            fail, circ = failure_of(fS, n)
            s["systems"] += 1
            s["matroids"] += fail is None
            s["equal_to_top_image"] += all(fS(Y) == fB(Y) for Y in subsets(n))
            s["circuits_mixing_primes"] += sum(1 for C in circ if len({primes[i] for i in C if primes[i] > 1}) > 1)
            present = {p for p in primes if p > 1}
            s["systems_with_two_top_primes"] += len(present) > 1
            primes_seen |= present
            if len(rows) < 100000 and s["systems"] <= 40:
                rows.append({"part": "group", "group": name, "law": {str(k): sorted(v) for k, v in law.items()}, "n": n,
                             "cons": [[k, list(c)] for k, c in cons], "matroid": fail is None,
                             "equal_to_top_image": all(fS(Y) == fB(Y) for Y in subsets(n)), "top_primes": primes})
        s["top_primes"] = sorted(primes_seen)
        s["seconds"] = round(time.time() - t0, 1)
        summary[name] = s
        print(f"group {name}: {s}", flush=True)
    return summary


# ------------------------------------------------------------------ parts 3 and 4: controls and perturbations

def search_failure(K, q, rng, nmax, seconds, max_systems=None, base=None, qm=None, gmap=None):
    t0 = time.time()
    tried = agree = 0
    while time.time() - t0 < seconds and (max_systems is None or tried < max_systems):
        n, cons = random_system(rng, 3, nmax, 5)
        cons = cons + [tuple(rng.randrange(n) for _ in range(3)) for _ in range(rng.randint(0, 2))]
        S = solve(K, [list(range(q))] * n, [(None, c) for c in cons])
        if not S:
            continue
        tried += 1
        f = constrained_fn(S, n)
        fail, _ = failure_of(f, n)
        if fail:
            return {"n": n, "cons": [list(c) for c in cons], **fail}, tried, agree
        if base is not None:
            fM = constrained_fn(solve(base, [list(range(qm))] * n, [(None, c) for c in cons]), n)
            agree += all(f(Y) == fM(Y) for Y in subsets(n))
    return None, tried, agree


def part_controls(rng, rows):
    Z6 = {t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}
    Z3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    w6, n6, _ = search_failure(Z6, 6, rng, 6, 600, max_systems=400)
    w3, n3, _ = search_failure(Z3, 3, rng, 6, 600, max_systems=400)
    rows.append({"part": "control", "name": "Z6", "witness": w6, "systems": n6})
    rows.append({"part": "control", "name": "Z3", "witness": w3, "systems": n3})
    out = {"Z6_failure_found": w6 is not None, "Z6_systems": n6, "Z3_failure_found": w3 is not None, "Z3_systems": n3}
    print(f"controls: {out}", flush=True)
    return out


def part_perturbations(rng, rows):
    M = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    g = (0, 1, 2, 2)
    L = {t for t in product(range(4), repeat=3) if tuple(g[x] for x in t) in M}
    summary = {}
    for bname, B, q in (("M", M, 3), ("lift", L, 4)):
        s = {"perturbations": 0, "failures_found": 0, "survivors": 0, "survivors_agreeing_with_M": 0,
             "block_removals_surviving": 0, "additions_failing": 0, "additions": 0}
        t0 = time.time()
        perts = [("remove", t) for t in sorted(B)] + [("add", t) for t in product(range(q), repeat=3) if t not in B]
        for kind, t in perts:
            K = B - {t} if kind == "remove" else B | {t}
            s["perturbations"] += 1
            row = {"part": "perturbation", "base": bname, "kind": kind, "tuple": list(t), "q": q}
            pre = None
            if is_knot(K, 3):
                pre = direct_case(K, 3) and "direct" or (fibre_distance(K, 3) and "fibre distance")
            row["structural_case"] = pre
            witness, tried, agree = (None, 0, 0) if pre else search_failure(K, q, rng, 7, 60, base=M, qm=3)
            row.update({"witness": witness, "systems": tried, "agree_with_M": agree})
            failed = bool(pre or witness)
            s["failures_found"] += failed
            if not failed:
                s["survivors"] += 1
                s["survivors_agreeing_with_M"] += agree == tried and tried > 0
                if kind == "remove" and bname == "lift" and all(x in (2, 3) for x in t):
                    s["block_removals_surviving"] += 1
            if kind == "add":
                s["additions"] += 1
                s["additions_failing"] += failed
            rows.append(row)
        s["seconds"] = round(time.time() - t0, 1)
        summary[bname] = s
        print(f"perturbations of {bname}: {s}", flush=True)
    return summary


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261022)
    rows = []
    t_all = time.time()
    summary = {"vamos": part_vamos(rng, rows), "groups": part_groups(rng, rows), "controls": part_controls(rng, rows),
               "perturbations": part_perturbations(rng, rows)}
    v, gr, ct, pt = summary["vamos"], summary["groups"], summary["controls"], summary["perturbations"]
    predictions = {
        "Q1": v["support relation"]["free_sets_are_vamos"] and v["union of codes"]["free_sets_are_vamos"],
        "Q2": all(v[x]["circuit_projection_case"] and v[x]["circuit_projection_case"]["two_copies_fail"]
                  for x in ("support relation", "union of codes")),
        "Q3": all(s["unique_maximal_normal"] and s["systems"] > 0 and s["matroids"] == s["systems"]
                  and s["equal_to_top_image"] == s["systems"] and s["circuits_mixing_primes"] == 0 and s["unknown_ranges"] == 0
                  for s in gr.values())
        and all(gr[x]["systems_with_two_top_primes"] > 0 for x in ("S3", "D5", "AGL(1,5)")),
        "Q4": all(s["survivors_agreeing_with_M"] == s["survivors"] for s in pt.values()),
        "Q5": pt["lift"]["block_removals_surviving"] == 8 and all(s["additions_failing"] == s["additions"] for s in pt.values()),
    }
    controls = {
        "C1_Z6_fails": {"passed": ct["Z6_failure_found"]},
        "C2_Z3_shows_no_failure": {"passed": not ct["Z3_failure_found"]},
        "C3_single_relation_carries_vamos": {"passed": predictions["Q1"]},
        "C4_some_perturbation_changes_constrained_sets": {"passed": any(s["failures_found"] > 0 for s in pt.values())},
    }
    result = {"schema_version": 1, "experiment_id": "MATROID-CONVERSE-20261021-001A-E001", "status": "complete",
              "evidence_stage": "exploratory", "summary": summary, "predictions": predictions, "controls": controls,
              "signal": all(predictions.values()) and all(c["passed"] for c in controls.values()),
              "seconds": round(time.time() - t_all, 1)}
    (OUT / "raw_rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True, default=list) + "\n" for r in rows))
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n")
    print(json.dumps({"predictions": predictions, "controls": {k: c["passed"] for k, c in controls.items()},
                      "signal": result["signal"], "seconds": result["seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
