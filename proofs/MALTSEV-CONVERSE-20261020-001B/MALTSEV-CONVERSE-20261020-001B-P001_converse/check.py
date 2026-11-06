#!/usr/bin/env python3
"""Checks for MALTSEV-CONVERSE-20261020-001B-P001. The statements are in proof.md.

Circuits are range-relative, as in KNOT-CIRCUITS-20261020-001B-P001. A knot is
rectangular at e when its fibres over e are pairwise equal or disjoint.

Checks:
- Proposition 1 (the naive converse fails). Two laws are tested on random
  systems:
  - law A: parity on {0,1} beside x <= y on {2,3};
  - law B: parity beside an isolated-value relation on {2,3,4}.
  The checks:
  - every system splits into parts;
  - law A has no failure between knots but has one between ties, and law B
    has no failure at all;
  - knots occur;
  - no Mal'tsev operation exists, because none preserves the second
    relation on its own range.
- Lemma 2 (direct hubs). On random knots over two and three values, fibres
  that pairwise meet at e, or a selector (s, e), make two copies fail.
- Theorem 3 (two values). Every affine Boolean knot on 3 or 4 variables is a
  single parity. Every other Boolean knot on 3 variables has a failure
  between knots in its own law, found by a bounded search.
- Theorem 4 (rectangular knots suffice). On Mal'tsev algebras whose knots
  are rectangular by rectangularity: a failure between knots appears exactly
  when two knots sharing e induce partitions of e's range whose composition
  is total.
- Remark 5 (selectors). NAE is non-rectangular with no meeting variable,
  but it has a selector, so two copies sharing two variables form a hub. The
  Boolean knot {000, 010, 011, 101, 110} has neither a meeting variable nor
  a selector.
- Observation 6 (the diagonal derivation). For random knots on 3 variables
  over 2, 3 and 4 values that have neither direct case, the derived knot
  K'(x0, x1, x2) = exists h: K(x0, x0, h) and K(x1, x2, h), for some ordering
  of K's variables, has a direct case and forms a hub.
- Census agreement with MALTSEV-CONVERSE-20261020-001A-E001.

Controls, each of which must be rejected:
- 'no failure implies Mal'tsev' (law B);
- 'every knot is rectangular' (OR3);
- 'the direct cases cover every non-rectangular knot' (the Boolean knot
  {000, 010, 011, 101, 110}).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
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
CENSUS = ROOT / "artifacts" / "MALTSEV-CONVERSE-20261020-001A" / "MALTSEV-CONVERSE-20261020-001A-E001_converse_census"


# ------------------------------------------------------------------ circuits

def ranges(S, n):
    return [len({t[i] for t in S}) for i in range(n)]


def constrained(S, Y, rg):
    return len({tuple(t[i] for i in Y) for t in S}) < prod(rg[i] for i in Y)


def circuits(S, n):
    rg = ranges(S, n)
    found = []
    for size in range(2, n + 1):
        for Y in combinations(range(n), size):
            if not any(set(C) <= set(Y) for C in found) and constrained(S, Y, rg):
                found.append(Y)
    return found, rg


def failure(S, n, knots_only=False):
    found, rg = circuits(S, n)
    for C1, C2 in combinations(found, 2):
        if knots_only and min(len(C1), len(C2)) < 3:
            continue
        for e in sorted(set(C1) & set(C2)):
            if not constrained(S, tuple(sorted((set(C1) | set(C2)) - {e})), rg):
                return C1, C2, e
    return None


def is_knot(K, n):
    found, rg = circuits(K, n)
    return n >= 3 and all(r >= 2 for r in rg) and found == [tuple(range(n))]


def fibres(K, n, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return g


def rectangular(K, n):
    for e in range(n):
        fs = [frozenset(f) for f in fibres(K, n, e).values()]
        if any(a != b and a & b for a in fs for b in fs):
            return False
    return True


def meeting_variable(K, n):
    for e in range(n):
        fs = list(fibres(K, n, e).values())
        if all(a & b for a in fs for b in fs):
            return e
    return None


def find_selector(K, n):
    for e in range(n):
        g = fibres(K, n, e)
        for s in range(n):
            if s == e:
                continue
            pos = s if s < e else s - 1
            groups = {}
            for rest, f in g.items():
                groups.setdefault(rest[pos], []).append(f)
            if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                return s, e
    return None


def join(K1, n1, K2, n2, shared):
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
    return S, n1 + len(fresh), tuple(range(n1)), tuple(sorted(pos[b] for b in range(n2)))


def hub_fails(K1, n1, K2, n2, shared, eliminated):
    S, N, C1, C2 = join(K1, n1, K2, n2, shared)
    found, rg = circuits(S, N)
    return C1 in found and C2 in found and not constrained(S, tuple(sorted((set(C1) | set(C2)) - {eliminated})), rg)


def build(Rs, copies, n_total, visible, q):
    out = set()
    for a in product(range(q), repeat=n_total):
        if all(tuple(a[v] for v in c) in Rs[kind] for kind, c in copies):
            out.add(tuple(a[v] for v in visible))
    return out


def maltsev_on(R, values):
    """Exhaustive search for a Mal'tsev operation on `values` preserving R (all of whose entries lie in `values`)."""
    vals = sorted(values)
    free = [(x, y, z) for x in vals for y in vals for z in vals if x != y and y != z]
    R = [tuple(t) for t in R]
    Rs = set(R)
    k = len(R[0])
    m = {}
    for x in vals:
        for y in vals:
            m[(x, x, y)] = y
            m[(y, x, x)] = y
    trip = [tuple((a[i], b[i], c[i]) for i in range(k)) for a in R for b in R for c in R]

    def ok():
        return all(not all(key in m for key in keys) or tuple(m[key] for key in keys) in Rs for keys in trip)

    def go(i):
        if i == len(free):
            return True
        for v in vals:
            m[free[i]] = v
            if ok() and go(i + 1):
                return True
        del m[free[i]]
        return False

    return ok() and go(0)


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261020)

    parity = {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}
    leq = {(2, 2), (2, 3), (3, 3)}
    iso = {(2, 2), (3, 3), (3, 4), (4, 3)}
    prop1 = {}
    for name, other, q, level in (("A: parity beside x<=y", leq, 4, "knots"), ("B: parity beside an isolated value", iso, 5, "all")):
        Rs = {"p": parity, "o": other}
        row = {"systems": 0, "split_ok": 0, "with_knots": 0, "knot_failures": 0, "tie_failures": 0, "any_failures": 0}
        for _ in range(900):
            n = rng.randint(3, 5)
            hidden = rng.randint(0, 1)
            nt = n + hidden
            copies = []
            for _ in range(rng.randint(1, 4)):
                if rng.random() < 0.55:
                    copies.append(("p", tuple(rng.randrange(nt) for _ in range(3))))
                else:
                    copies.append(("o", tuple(rng.randrange(nt) for _ in range(2))))
            S = build(Rs, copies, nt, list(range(n)), q)
            if not S:
                continue
            row["systems"] += 1
            pvars = {v for kind, c in copies if kind == "p" for v in c}
            ovars = {v for kind, c in copies if kind == "o" for v in c}
            row["split_ok"] += not (pvars & ovars)
            found, _ = circuits(S, n)
            row["with_knots"] += any(len(C) >= 3 for C in found)
            row["knot_failures"] += failure(S, n, knots_only=True) is not None
            f = failure(S, n)
            row["any_failures"] += f is not None
            row["tie_failures"] += f is not None and failure(S, n, knots_only=True) is None
        row["second_relation_has_maltsev_on_its_range"] = maltsev_on(other, {v for t in other for v in t})
        prop1[name] = row
        ok = row["split_ok"] == row["systems"] and row["with_knots"] > 0 and row["knot_failures"] == 0 and \
            not row["second_relation_has_maltsev_on_its_range"]
        ok = ok and (row["tie_failures"] > 0 if level == "knots" else row["any_failures"] == 0)
        if not ok:
            failures.append(f"Proposition 1 {name}")
    checks["proposition_1_naive_converse_fails"] = prop1

    # Lemma 2: direct hubs
    lem2 = {"knots": 0, "meeting": 0, "meeting_hub": 0, "selector": 0, "selector_hub": 0}
    pool = []
    for mask in range(1, 255):
        K = {t for i, t in enumerate(product((0, 1), repeat=3)) if mask >> i & 1}
        if is_knot(K, 3):
            pool.append((K, 3))
    for _ in range(1500):
        q = 3
        n = rng.choice([3, 3, 4])
        K = {t for t in product(range(q), repeat=n) if rng.random() < rng.uniform(0.6, 0.95)}
        if is_knot(K, n):
            pool.append((K, n))
    for K, n in pool:
        lem2["knots"] += 1
        e = meeting_variable(K, n)
        if e is not None:
            lem2["meeting"] += 1
            lem2["meeting_hub"] += hub_fails(K, n, K, n, [(e, e)], e)
        sel = find_selector(K, n)
        if sel is not None and e is None:
            s, e2 = sel
            lem2["selector"] += 1
            lem2["selector_hub"] += hub_fails(K, n, K, n, [(e2, e2), (s, s)], e2)
    checks["lemma_2_direct_hubs"] = lem2
    if lem2["meeting_hub"] != lem2["meeting"] or lem2["selector_hub"] != lem2["selector"] or not lem2["meeting"]:
        failures.append("Lemma 2")

    # Theorem 3: two-valued knots
    thm3 = {"affine_knots_3": 0, "affine_knots_4": 0, "single_parities": 0, "nonaffine_knots_3": 0, "with_knot_hub": 0}

    def affine(R):
        R = list(R)
        return all(tuple(a ^ b ^ c for a, b, c in zip(t1, t2, t3)) in set(R) for t1 in R for t2 in R for t3 in R)

    for n in (3, 4):
        for mask in range(1, (1 << (1 << n)) - 1):
            K = {t for i, t in enumerate(product((0, 1), repeat=n)) if mask >> i & 1}
            if len(K) != (1 << (n - 1)) or not affine(K):
                continue
            if not is_knot(K, n):
                continue
            thm3[f"affine_knots_{n}"] += 1
            thm3["single_parities"] += K in ({t for t in product((0, 1), repeat=n) if sum(t) % 2 == 0},
                                            {t for t in product((0, 1), repeat=n) if sum(t) % 2 == 1})
    for K, n in pool:
        if n != 3 or any(v not in (0, 1) for t in K for v in t) or affine(K):
            continue
        thm3["nonaffine_knots_3"] += 1
        found = False
        knots = [K]
        tuples = list(product(range(5), repeat=3))
        for t1, t2 in combinations(tuples, 2):
            if found or len(knots) > 12:
                break
            for nv in (3, 4):
                S = {a[:nv] for a in product((0, 1), repeat=5)
                     if tuple(a[v] for v in t1) in K and tuple(a[v] for v in t2) in K}
                if S and is_knot(S, nv) and S not in knots:
                    knots.append(S)
        for K1 in knots:
            n1 = len(next(iter(K1)))
            for K2 in knots:
                n2 = len(next(iter(K2)))
                if found:
                    break
                for e1 in range(n1):
                    for e2 in range(n2):
                        if not found and hub_fails(K1, n1, K2, n2, [(e1, e2)], e1):
                            found = True
                        for s1 in range(n1):
                            for s2 in range(n2):
                                if found or s1 == e1 or s2 == e2:
                                    continue
                                if hub_fails(K1, n1, K2, n2, [(e1, e2), (s1, s2)], e1):
                                    found = True
        thm3["with_knot_hub"] += found
    checks["theorem_3_two_values"] = thm3
    if thm3["single_parities"] != thm3["affine_knots_3"] + thm3["affine_knots_4"] or \
            thm3["with_knot_hub"] != thm3["nonaffine_knots_3"] or not thm3["nonaffine_knots_3"]:
        failures.append("Theorem 3")

    # Theorem 4: rectangular knots suffice (Mal'tsev algebras)
    def heap_coset(gens, op, inv, n):
        t0 = gens[0]
        hgens = [tuple(op(a, inv(b)) for a, b in zip(t, t0)) for t in gens[1:]]
        e = tuple(op(x, inv(x)) for x in t0)
        H = {e}
        frontier = [e]
        while frontier:
            new = []
            for h in frontier:
                for g in hgens:
                    x = tuple(op(a, b) for a, b in zip(h, g))
                    if x not in H:
                        H.add(x)
                        new.append(x)
            frontier = new
        return {tuple(op(a, b) for a, b in zip(h, t0)) for h in H}

    groups = {"Z2xZ2": (lambda a, b: a ^ b, lambda a: a, 4), "Z4": (lambda a, b: (a + b) % 4, lambda a: (-a) % 4, 4),
              "Z3": (lambda a, b: (a + b) % 3, lambda a: (-a) % 3, 3), "Z6": (lambda a, b: (a + b) % 6, lambda a: (-a) % 6, 6)}
    thm4 = {}
    for name, (op, inv, q) in groups.items():
        row = {"systems": 0, "all_knots_rectangular": 0, "failures": 0, "failures_with_total_pair": 0,
               "total_pairs": 0, "total_pairs_fail_when_joined_alone": 0}
        for _ in range(120 if q <= 4 else 50):
            n = 4
            gens = [tuple(rng.randrange(q) for _ in range(n)) for _ in range(rng.randint(2, 4))]
            S = heap_coset(gens, op, inv, n)
            if len(S) == q ** n:
                continue
            found, rg = circuits(S, n)
            knots = [C for C in found if len(C) >= 3]
            if not knots:
                continue
            row["systems"] += 1
            projs = {C: {tuple(t[i] for i in C) for t in S} for C in knots}
            row["all_knots_rectangular"] += all(rectangular(projs[C], len(C)) for C in knots)
            total_here = False
            for C1, C2 in combinations(knots, 2):
                for e in set(C1) & set(C2):
                    parts = []
                    for C in (C1, C2):
                        g = fibres(projs[C], len(C), C.index(e))
                        parts.append({frozenset(f) for f in g.values()})
                    De = {t[e] for t in S}
                    comp = {(x, z) for P in parts[0] for Q in parts[1] if P & Q for x in P for z in Q}
                    if len(comp) == len(De) ** 2:
                        total_here = True
                        row["total_pairs"] += 1
                        row["total_pairs_fail_when_joined_alone"] += hub_fails(
                            projs[C1], len(C1), projs[C2], len(C2), [(C1.index(e), C2.index(e))], C1.index(e))
            if failure(S, n, knots_only=True) is not None:
                row["failures"] += 1
                row["failures_with_total_pair"] += total_here
        thm4[name] = row
        if row["all_knots_rectangular"] != row["systems"] or row["failures_with_total_pair"] != row["failures"] or \
                row["total_pairs_fail_when_joined_alone"] != row["total_pairs"]:
            failures.append(f"Theorem 4 on {name}")
    H1, H2 = {0, 1}, {0, 2}
    K1 = {(x, y, e) for x, y, e in product(range(4), repeat=3) if x ^ y ^ e in H1}
    K2 = {(z, w, e) for z, w, e in product(range(4), repeat=3) if z ^ w ^ e in H2}
    thm4["two_congruence_knot_hub_Z2xZ2"] = is_knot(K1, 3) and is_knot(K2, 3) and hub_fails(K1, 3, K2, 3, [(2, 2)], 2)
    checks["theorem_4_rectangular_knots_suffice"] = thm4
    if not thm4["two_congruence_knot_hub_Z2xZ2"]:
        failures.append("Theorem 4 knot-level construction")

    # Remark 5: NAE has a selector; knots with neither direct case exist and reach a hub through the diagonal derivation
    nae = {t for t in product((0, 1), repeat=3) if len(set(t)) > 1}
    sel = find_selector(nae, 3)
    rem5 = {"nae_is_knot": is_knot(nae, 3), "nae_rectangular": rectangular(nae, 3),
            "nae_meeting_variable": meeting_variable(nae, 3), "nae_selector": list(sel) if sel else None,
            "nae_selector_hub": sel is not None and hub_fails(nae, 3, nae, 3, [(sel[1], sel[1]), (sel[0], sel[0])], sel[1])}
    neither = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}
    rem5["boolean_neither_knot"] = {"is_knot": is_knot(neither, 3), "rectangular": rectangular(neither, 3),
                                    "meeting_variable": meeting_variable(neither, 3),
                                    "selector": find_selector(neither, 3)}
    checks["remark_5_selectors"] = rem5
    if not (rem5["nae_is_knot"] and not rem5["nae_rectangular"] and rem5["nae_meeting_variable"] is None
            and rem5["nae_selector_hub"] and rem5["boolean_neither_knot"]["is_knot"]
            and not rem5["boolean_neither_knot"]["rectangular"] and rem5["boolean_neither_knot"]["meeting_variable"] is None
            and rem5["boolean_neither_knot"]["selector"] is None):
        failures.append("Remark 5")

    # Observation 6: the diagonal derivation K'(x0, x1, x2) = exists h: K(x0, x0, h) and K(x1, x2, h)
    perms = ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))

    def diagonal(K, q):
        return {(a, b, c) for a, b, c in product(range(q), repeat=3)
                if any((a, a, h) in K and (b, c, h) in K for h in range(q))}

    obs6 = {}
    for q in (2, 3, 4):
        row = {"neither_knots": 0, "resolved_by_diagonal": 0}
        tries = 0
        targets = [neither] if q == 2 else []
        while len(targets) < (20 if q < 4 else 12) and tries < 300000:
            tries += 1
            K = {t for t in product(range(q), repeat=3) if rng.random() < rng.uniform(0.45, 0.97)}
            if is_knot(K, 3) and not rectangular(K, 3) and meeting_variable(K, 3) is None and find_selector(K, 3) is None:
                targets.append(K)
        for K in targets:
            row["neither_knots"] += 1
            ok = False
            for pm in perms:
                Kp = {tuple(t[pm[i]] for i in range(3)) for t in K}
                Dk = diagonal(Kp, q)
                if is_knot(Dk, 3):
                    mv = meeting_variable(Dk, 3)
                    sl = find_selector(Dk, 3)
                    if mv is not None and hub_fails(Dk, 3, Dk, 3, [(mv, mv)], mv):
                        ok = True
                    elif sl is not None and hub_fails(Dk, 3, Dk, 3, [(sl[1], sl[1]), (sl[0], sl[0])], sl[1]):
                        ok = True
                if ok:
                    break
            row["resolved_by_diagonal"] += ok
        obs6[str(q)] = row
        if row["resolved_by_diagonal"] != row["neither_knots"] or not row["neither_knots"]:
            failures.append(f"Observation 6 on {q} values")
    checks["observation_6_diagonal_derivation"] = obs6

    # census agreement
    census = {}
    if (CENSUS / "result.json").exists():
        res = json.loads((CENSUS / "result.json").read_text())
        rows = [json.loads(line) for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines()]
        census["predictions"] = res["predictions"]
        census["laws_with_knots"] = sum(bool(r["knots"]) for r in rows)
        census["laws_with_knots_and_no_knot_failure"] = sum(bool(r["knots"]) and not r["knot_failure"] for r in rows)
        census["nonrectangular_knots_by_mechanism"] = res["summary"]["nonrectangular_knots"]
        if census["laws_with_knots_and_no_knot_failure"] != 0 or not all(res["predictions"].values()):
            failures.append("census agreement")
    checks["census_agreement"] = census

    controls["no_failure_implies_maltsev"] = {"law_B_any_failures": prop1["B: parity beside an isolated value"]["any_failures"],
                                              "law_B_maltsev": prop1["B: parity beside an isolated value"]["second_relation_has_maltsev_on_its_range"],
                                              "rejected": prop1["B: parity beside an isolated value"]["any_failures"] == 0}
    or3 = set(product((0, 1), repeat=3)) - {(0, 0, 0)}
    controls["every_knot_rectangular"] = {"OR3_knot": is_knot(or3, 3), "OR3_rectangular": rectangular(or3, 3),
                                          "rejected": is_knot(or3, 3) and not rectangular(or3, 3)}
    bn = rem5["boolean_neither_knot"]
    controls["direct_cases_cover_every_nonrectangular_knot"] = {"knot": "000 010 011 101 110", "meeting": bn["meeting_variable"],
                                                               "selector": bn["selector"],
                                                               "rejected": bn["meeting_variable"] is None and bn["selector"] is None}
    for name, control in controls.items():
        if not control["rejected"]:
            failures.append(f"control not rejected: {name}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
