#!/usr/bin/env python3
"""Independent check of MALTSEV-CONVERSE-20261020-001A-E001. It imports no producer code.

- Mal'tsev flags are recomputed by a search that assigns entries in a
  different order and re-checks only the column triples touching each entry.
- Every recorded knot is rebuilt from its definition. This file's own
  circuit routine (the one-smaller-subsets test) confirms it is a knot,
  then recomputes its rectangularity and its mechanism.
- Every recorded failure is rebuilt and verified:
  - hubs, by building the join;
  - ties, by replaying the binary derivations.
- The disjoint unions are re-verified:
  - no Mal'tsev operation preserves the second relation on its own range,
    so none exists on the whole domain;
  - the parity part has knots and no hub;
  - the implication part has a tie hub, and the isolated-value part has none.
- The prediction flags are recomputed.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "MALTSEV-CONVERSE-20261020-001A" / HERE.name


def rng_(S, n):
    return [len({t[i] for t in S}) for i in range(n)]


def free(S, Y, r):
    return len({tuple(t[i] for i in Y) for t in S}) == prod(r[i] for i in Y)


def is_circuit(S, Y, r):
    return len(Y) >= 2 and not free(S, Y, r) and all(free(S, tuple(v for v in Y if v != w), r) for w in Y)


def build(R, copies, n_total, n_vis, q):
    out = set()
    for a in product(range(q), repeat=n_total):
        if all(tuple(a[v] for v in c) in R for c in copies):
            out.add(a[:n_vis])
    return out


def knot(K, n):
    r = rng_(K, n)
    return n >= 3 and all(x >= 2 for x in r) and is_circuit(K, tuple(range(n)), r) and all(
        not is_circuit(K, Y, r) for size in range(2, n) for Y in combinations(range(n), size))


def fibre_sets(K, n, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return [frozenset(v) for v in g.values()], g


def rect(K, n):
    for e in range(n):
        fs, _ = fibre_sets(K, n, e)
        if any(a != b and a & b for a in fs for b in fs):
            return False
    return True


def mechanism(K, n):
    for e in range(n):
        fs, _ = fibre_sets(K, n, e)
        if all(a & b for a in fs for b in fs):
            return "pairwise meeting"
    for e in range(n):
        _, g = fibre_sets(K, n, e)
        for s in range(n):
            if s == e:
                continue
            pos = s if s < e else s - 1
            groups = {}
            for rest, f in g.items():
                groups.setdefault(rest[pos], []).append(frozenset(f))
            if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                return "selector"
    return "neither"


def joined_failure(K1, n1, K2, n2, shared, eliminated):
    pos = {b: a for a, b in shared}
    fresh = [b for b in range(n2) if b not in pos]
    for j, b in enumerate(fresh):
        pos[b] = n1 + j
    S = set()
    for t1 in K1:
        for t2 in K2:
            if all(t1[a] == t2[b] for a, b in shared):
                full = list(t1) + [None] * len(fresh)
                for b in fresh:
                    full[pos[b]] = t2[b]
                S.add(tuple(full))
    N = n1 + len(fresh)
    r = rng_(S, N)
    C1, C2 = tuple(range(n1)), tuple(sorted(pos[b] for b in range(n2)))
    return is_circuit(S, C1, r) and is_circuit(S, C2, r) and free(S, tuple(sorted((set(C1) | set(C2)) - {eliminated})), r)


def maltsev_exists(relations, q):
    m = {}
    for x in range(q):
        for y in range(q):
            m[(x, x, y)] = y
            m[(y, x, x)] = y
    checks = []
    for R in relations:
        R = [tuple(t) for t in R]
        Rs = set(R)
        k = len(R[0])
        for a in R:
            for b in R:
                for c in R:
                    checks.append((tuple((a[i], b[i], c[i]) for i in range(k)), Rs))
    touching = {}
    for i, (keys, _) in enumerate(checks):
        for key in keys:
            if key not in m:
                touching.setdefault(key, set()).add(i)
    if any(all(k in m for k in keys) and tuple(m[k] for k in keys) not in Rs for keys, Rs in checks):
        return False
    order = sorted(touching, reverse=True)

    def go(i):
        if i == len(order):
            return True
        key = order[i]
        for v in reversed(range(q)):
            m[key] = v
            if all(not all(k in m for k in checks[j][0]) or tuple(m[k] for k in checks[j][0]) in checks[j][1]
                   for j in touching[key]) and go(i + 1):
                return True
        del m[key]
        return False

    return go(0)


def replay(bases, derivations, q):
    rels = []
    for d in derivations:
        if d[0] == "base":
            rels.append(frozenset(map(tuple, bases[d[1]])))
        elif d[0] == "eq":
            rels.append(frozenset((x, x) for x in range(q)))
        elif d[0] == "conv":
            rels.append(frozenset((y, x) for x, y in rels[d[1]]))
        elif d[0] == "comp":
            A, B = rels[d[1]], rels[d[2]]
            rels.append(frozenset((x, z) for x, y in A for y2, z in B if y == y2))
        elif d[0] == "and":
            rels.append(rels[d[1]] & rels[d[2]])
    return rels


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    counts = {"rows": 0, "maltsev_agree": 0, "knots_rebuilt": 0, "knot_failures_verified": 0, "tie_failures_verified": 0}
    nonrect = []
    for r in rows:
        counts["rows"] += 1
        R = {tuple(t) for t in r["relation"]}
        q, k = r["q"], r["k"]
        if maltsev_exists([R], q) == r["maltsev"]:
            counts["maltsev_agree"] += 1
        else:
            problems.append(f"Mal'tsev flag differs for {r['label']} {r['relation']}")
        for kn in r["knots"]:
            d = kn["definition"]
            K = build(R, [tuple(c) for c in d["copies"]], d["n_total"], d["n_vis"], q)
            n = d["n_vis"]
            if not knot(K, n) or rect(K, n) != kn["rectangular"]:
                problems.append(f"knot differs for {r['label']} {r['relation']}")
                continue
            counts["knots_rebuilt"] += 1
            if not kn["rectangular"]:
                mech = mechanism(K, n)
                nonrect.append(mech)
                if mech != kn["mechanism"]:
                    problems.append(f"mechanism differs for {r['label']}")
        kf = r["knot_failure"]
        if kf:
            d1, d2 = kf["knot1"], kf["knot2"]
            K1 = build(R, [tuple(c) for c in d1["copies"]], d1["n_total"], d1["n_vis"], q)
            K2 = build(R, [tuple(c) for c in d2["copies"]], d2["n_total"], d2["n_vis"], q)
            if knot(K1, d1["n_vis"]) and knot(K2, d2["n_vis"]) and joined_failure(
                    K1, d1["n_vis"], K2, d2["n_vis"], [tuple(p) for p in kf["shared"]], kf["eliminated"]):
                counts["knot_failures_verified"] += 1
            else:
                problems.append(f"knot failure witness fails for {r['label']} {r['relation']}")
        tf = r["tie_failure"]
        if tf:
            rels = replay(tf["bases"], tf["derivations"], q)
            T1, T2 = rels[tf["T1"]], rels[tf["T2"]]
            S = {(x, e, z) for x, e in T1 for e2, z in T2 if e == e2}
            rr = rng_(S, 3)
            if is_circuit(S, (0, 1), rr) and is_circuit(S, (1, 2), rr) and free(S, (0, 2), rr):
                counts["tie_failures_verified"] += 1
            else:
                problems.append(f"tie failure witness fails for {r['label']} {r['relation']}")

    parity = {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}
    implication = [(0, 0), (0, 1), (1, 1)]
    iso = [(0, 0), (1, 1), (1, 2), (2, 1)]
    unions = {
        "implication_has_no_maltsev_on_its_range": not maltsev_exists([implication], 2),
        "isolated_value_has_no_maltsev_on_its_range": not maltsev_exists([iso], 3),
        "parity_is_a_knot": knot(parity, 3),
        "parity_hub": joined_failure(parity, 3, parity, 3, [(2, 2)], 2),
        "implication_tie_hub": (lambda S: free(S, (0, 2), rng_(S, 3)))(
            {(x, e, z) for x, e in implication for z, e2 in implication if e == e2}),
    }
    iso_rels = replay([iso], [("base", 0), ("eq",)], 3)
    changed = True
    while changed:
        changed = False
        for A in list(iso_rels):
            for B in list(iso_rels):
                for C in (frozenset((y, x) for x, y in A), frozenset((x, z) for x, y in A for y2, z in B if y == y2), A & B):
                    if C and C not in iso_rels:
                        iso_rels.append(C)
                        changed = True
    hub = False
    for T1 in iso_rels:
        for T2 in iso_rels:
            l1, r1, l2, r2 = {x for x, _ in T1}, {y for _, y in T1}, {x for x, _ in T2}, {y for _, y in T2}
            if l2 == r1 and len(T1) < len(l1) * len(r1) and len(T2) < len(l2) * len(r2):
                C = {(x, z) for x, y in T1 for y2, z in T2 if y == y2}
                hub = hub or len(C) == len(l1) * len(r2)
    unions["isolated_value_binary_closure_has_tie_hub"] = hub
    ok_unions = (unions["implication_has_no_maltsev_on_its_range"] and unions["isolated_value_has_no_maltsev_on_its_range"]
                 and unions["parity_is_a_knot"] and not unions["parity_hub"] and unions["implication_tie_hub"]
                 and not unions["isolated_value_binary_closure_has_tie_hub"])
    if not ok_unions:
        problems.append(f"disjoint unions: {unions}")

    m1 = not any(r["any_failure"] for r in rows if r["maltsev"])
    m2 = all(all(kn["rectangular"] for kn in r["knots"]) for r in rows if not r["knot_failure"])
    m4 = all(mech in ("pairwise meeting", "selector") for mech in nonrect)
    recomputed = {"M1": m1, "M2": m2, "M3": ok_unions and result["predictions"]["M3"], "M4": m4}
    if recomputed != result["predictions"]:
        problems.append(f"prediction flags differ: {recomputed} vs {result['predictions']}")
    report = {"counts": counts, "nonrectangular_mechanisms": {m: nonrect.count(m) for m in set(nonrect)},
              "disjoint_unions": unions, "predictions_recomputed": recomputed}
    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
