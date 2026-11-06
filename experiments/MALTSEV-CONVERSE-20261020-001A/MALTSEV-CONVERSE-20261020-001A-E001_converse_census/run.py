#!/usr/bin/env python3
"""Producer for MALTSEV-CONVERSE-20261020-001A-E001 (exploratory; see contract.json).

Circuits are taken relative to each variable's range: a set is constrained
when its projection is smaller than the product of its variables' ranges.
Knots are circuits with at least 3 variables. A knot is rectangular at a
variable when its fibres over that variable are pairwise equal or disjoint.

For each law (one relation), this records:
- whether a Mal'tsev polymorphism exists;
- the knots found in small systems and whether each is rectangular;
- failures of elimination between knots (hubs of two pool knots sharing one
  or two variables) and between ties (the binary pp-closure).

Writes artifacts/MALTSEV-CONVERSE-20261020-001A/<this folder>/:
result.json, raw_rows.jsonl and run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "MALTSEV-CONVERSE-20261020-001A" / HERE.name
LOG = []
START = time.time()


def log(msg):
    line = f"[{time.time() - START:.0f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ circuits relative to ranges

def range_sizes(S, n):
    return [len({t[i] for t in S}) for i in range(n)]


def is_constrained(S, Y, sizes):
    full = 1
    for i in Y:
        full *= sizes[i]
    return len({tuple(t[i] for i in Y) for t in S}) < full


def circuits(S, n):
    sizes = range_sizes(S, n)
    found = []
    for size in range(2, n + 1):
        for Y in combinations(range(n), size):
            if not any(set(C) <= set(Y) for C in found) and is_constrained(S, Y, sizes):
                found.append(Y)
    return found, sizes


def failure(S, n, knots_only=False):
    found, sizes = circuits(S, n)
    for C1, C2 in combinations(found, 2):
        if knots_only and min(len(C1), len(C2)) < 3:
            continue
        for e in sorted(set(C1) & set(C2)):
            if not is_constrained(S, tuple(sorted((set(C1) | set(C2)) - {e})), sizes):
                return [list(C1), list(C2), e]
    return None


def system(R, copies, n_total, n_vis, q):
    out = set()
    for a in product(range(q), repeat=n_total):
        if all(tuple(a[v] for v in c) in R for c in copies):
            out.add(a[:n_vis])
    return out


def is_knot(S, n):
    if n < 3 or not S:
        return False
    found, sizes = circuits(S, n)
    return found == [tuple(range(n))] and all(s >= 2 for s in sizes)


def fibres(K, n, e):
    by_rest = {}
    for t in K:
        by_rest.setdefault(tuple(v for i, v in enumerate(t) if i != e), set()).add(t[e])
    return by_rest


def rectangular_at(K, n, e):
    fs = [frozenset(f) for f in fibres(K, n, e).values()]
    return all(a == b or not (a & b) for a in fs for b in fs)


def pairwise_meeting_at(K, n, e):
    fs = list({frozenset(f) for f in fibres(K, n, e).values()})
    return all(a & b for a in fs for b in fs)


def selector(K, n):
    """A pair (s, e) such that for each value of s the fibres over e pairwise meet."""
    for e in range(n):
        for s in range(n):
            if s == e:
                continue
            groups = {}
            for rest, f in fibres(K, n, e).items():
                full_index = [i for i in range(n) if i != e]
                sval = rest[full_index.index(s)]
                groups.setdefault(sval, set()).add(frozenset(f))
            if all(all(a & b for a in g for b in g) for g in groups.values()):
                return [s, e]
    return None


# ------------------------------------------------------------------ knots and hubs

def knot_pool(R, k, q, cap=6):
    pool = {}
    for n_total in range(3, 5):
        tuples = list(product(range(n_total), repeat=k))
        for n_vis in range(3, n_total + 1):
            for m in (1, 2, 3) if k == 2 else (1, 2):
                for copies in combinations(tuples, m):
                    if not set(range(n_vis)) <= set(v for t in copies for v in t):
                        continue
                    S = system(R, copies, n_total, n_vis, q)
                    if is_knot(S, n_vis):
                        key = (n_vis, frozenset(S))
                        if key not in pool:
                            pool[key] = {"copies": [list(t) for t in copies], "n_total": n_total, "n_vis": n_vis}
                    if len(pool) >= 4 * cap:
                        break
    items = sorted(pool.items(), key=lambda kv: (kv[0][0], len(kv[0][1]), sorted(kv[0][1])))
    return items[:cap]


def hub_failure(pool):
    """Fibre criterion: sharing one variable (e) or two (s and e); verified by building the join."""
    for (k1, d1), (k2, d2) in product(pool, repeat=2):
        n1, K1 = k1
        n2, K2 = k2
        for e1 in range(n1):
            for e2 in range(n2):
                f1, f2 = fibres(K1, n1, e1), fibres(K2, n2, e2)
                if all(a & b for a in f1.values() for b in f2.values()):
                    if verify_join(K1, n1, K2, n2, [(e1, e2)], e1):
                        return {"knot1": d1, "knot2": d2, "shared": [[e1, e2]], "eliminated": e1}
                for s1 in range(n1):
                    for s2 in range(n2):
                        if s1 == e1 or s2 == e2:
                            continue
                        idx1 = [i for i in range(n1) if i != e1]
                        idx2 = [i for i in range(n2) if i != e2]
                        g1, g2 = {}, {}
                        for rest, f in f1.items():
                            g1.setdefault(rest[idx1.index(s1)], []).append(f)
                        for rest, f in f2.items():
                            g2.setdefault(rest[idx2.index(s2)], []).append(f)
                        if set(g1) != set(g2):
                            continue
                        if all(a & b for sv in g1 for a in g1[sv] for b in g2[sv]):
                            if verify_join(K1, n1, K2, n2, [(e1, e2), (s1, s2)], e1):
                                return {"knot1": d1, "knot2": d2, "shared": [[e1, e2], [s1, s2]], "eliminated": e1}
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


def verify_join(K1, n1, K2, n2, shared, eliminated):
    S, N, C1, C2 = join(K1, n1, K2, n2, shared)
    found, sizes = circuits(S, N)
    return C1 in found and C2 in found and not is_constrained(S, tuple(sorted((set(C1) | set(C2)) - {eliminated})), sizes)


PAIRS3 = [(x, y) for x in range(3) for y in range(3)]


def to_mask(rel):
    return sum(1 << (3 * x + y) for x, y in rel)


def from_mask(mask):
    return {(x, y) for x, y in PAIRS3 if mask >> (3 * x + y) & 1}


COMP3 = None
CONV3 = None


def tables3():
    global COMP3, CONV3
    if COMP3 is None:
        rels = [from_mask(m) for m in range(512)]
        CONV3 = [to_mask({(y, x) for x, y in r}) for r in rels]
        COMP3 = [[to_mask({(x, z) for (x, y) in A for (y2, z) in B if y == y2}) for B in rels] for A in rels]
    return COMP3, CONV3


def binary_closure(R2s, q, cap=600):
    if q == 3:
        comp, conv = tables3()
        rels = [to_mask(R) for R in R2s] + [to_mask({(x, x) for x in range(3)})]
        deriv = [("base", i) for i in range(len(R2s))] + [("eq",)]
        seen = {r: i for i, r in enumerate(rels)}
        i = 0
        while i < len(rels) and len(rels) < cap:
            for j in range(i + 1):
                A, B = rels[i], rels[j]
                for C, d in ((conv[A], ("conv", i)), (comp[A][B], ("comp", i, j)), (comp[B][A], ("comp", j, i)),
                             (A & B, ("and", i, j))):
                    if C and C not in seen:
                        seen[C] = len(rels)
                        rels.append(C)
                        deriv.append(d)
            i += 1
        return [frozenset(from_mask(r)) for r in rels], deriv
    rels = [frozenset(R) for R in R2s] + [frozenset((x, x) for x in range(q))]
    deriv = [("base", i) for i in range(len(R2s))] + [("eq",)]
    seen = {r: i for i, r in enumerate(rels)}
    i = 0
    while i < len(rels) and len(rels) < cap:
        for j in range(i + 1):
            A, B = rels[i], rels[j]
            for C, d in ((frozenset((y, x) for x, y in A), ("conv", i)),
                         (frozenset((x, z) for (x, y) in A for (y2, z) in B if y == y2), ("comp", i, j)),
                         (frozenset((x, z) for (x, y) in B for (y2, z) in A if y == y2), ("comp", j, i)),
                         (A & B, ("and", i, j))):
                if C and C not in seen:
                    seen[C] = len(rels)
                    rels.append(C)
                    deriv.append(d)
        i += 1
    return rels, deriv


def tie_hub(rels):
    info = []
    for T in rels:
        l, r = frozenset(x for x, _ in T), frozenset(y for _, y in T)
        info.append((l, r, len(T) == len(l) * len(r)))
    for i, T1 in enumerate(rels):
        l1, r1, full1 = info[i]
        if full1:
            continue
        for j, T2 in enumerate(rels):
            l2, r2, full2 = info[j]
            if l2 != r1 or full2:
                continue
            C = {(x, z) for (x, y) in T1 for (y2, z) in T2 if y == y2}
            if len(C) == len(l1) * len(r2):
                return i, j
    return None


def binary_projections(R, k):
    out = []
    for i, j in combinations(range(k), 2):
        out.append({(t[i], t[j]) for t in R})
    return out


# ------------------------------------------------------------------ Mal'tsev search

def has_maltsev(relations, q):
    """Exact search for m with m(x,x,y) = m(y,x,x) = y preserving every relation; only entries met by some column matter."""
    m = {}
    for x in range(q):
        for y in range(q):
            m[(x, x, y)] = y
            m[(y, x, x)] = y
    checks = []
    for R in relations:
        R = list(R)
        Rs = set(R)
        k = len(R[0])
        for a in R:
            for b in R:
                for c in R:
                    checks.append((tuple((a[i], b[i], c[i]) for i in range(k)), Rs))
    by_entry = {}
    for idx, (keys, _) in enumerate(checks):
        for key in set(keys):
            if key not in m:
                by_entry.setdefault(key, []).append(idx)
    for keys, Rs in checks:
        if all(key in m for key in keys) and tuple(m[key] for key in keys) not in Rs:
            return False
    entries = sorted(by_entry, key=lambda e: -len(by_entry[e]))

    def consistent(entry):
        for idx in by_entry[entry]:
            keys, Rs = checks[idx]
            if all(key in m for key in keys) and tuple(m[key] for key in keys) not in Rs:
                return False
        return True

    def go(i):
        if i == len(entries):
            return True
        for v in range(q):
            m[entries[i]] = v
            if consistent(entries[i]) and go(i + 1):
                return True
        del m[entries[i]]
        return False

    return go(0)


# ------------------------------------------------------------------ operations on three elements

def random_maltsev(rng, q):
    t = {}
    for x, y, z in product(range(q), repeat=3):
        t[(x, y, z)] = z if x == y else (x if y == z else rng.randrange(q))
    return lambda x, y, z: t[(x, y, z)]


def random_majority(rng, q):
    t = {}
    for x, y, z in product(range(q), repeat=3):
        if x == y or x == z:
            t[(x, y, z)] = x
        elif y == z:
            t[(x, y, z)] = y
        else:
            t[(x, y, z)] = rng.randrange(q)
    return lambda x, y, z: t[(x, y, z)]


def semilattices(q):
    out = []
    for vals in product(range(q), repeat=q * q):
        f = {(x, y): vals[x * q + y] for x in range(q) for y in range(q)}
        if all(f[(x, x)] == x for x in range(q)) and all(f[(x, y)] == f[(y, x)] for x in range(q) for y in range(q)) and \
                all(f[(f[(x, y)], z)] == f[(x, f[(y, z)])] for x in range(q) for y in range(q) for z in range(q)):
            out.append(f)
    return out


def rps():
    beats = {(0, 1): 0, (1, 2): 1, (2, 0): 2}
    f = {}
    for x in range(3):
        for y in range(3):
            f[(x, y)] = x if x == y else beats.get((x, y), beats.get((y, x)))
    return f


def random_conservative(rng, q):
    t = {k: rng.choice(k) for k in product(range(q), repeat=3)}
    return lambda x, y, z: t[(x, y, z)]


def random_idempotent(rng, q):
    t = {k: (k[0] if len(set(k)) == 1 else rng.randrange(q)) for k in product(range(q), repeat=3)}
    return lambda x, y, z: t[(x, y, z)]


def generate(gens, ops, n):
    S = set(gens)
    frontier = set(gens)
    while frontier:
        new = set()
        items = list(S)
        for arity, f in ops:
            for args in product(items, repeat=arity):
                if not any(a in frontier for a in args):
                    continue
                t = tuple(f(*cols) for cols in zip(*args))
                if t not in S:
                    new.add(t)
        S |= new
        frontier = new
    return S


# ------------------------------------------------------------------ analysis of one law

def analyse(R, k, q, label):
    R = set(map(tuple, R))
    row = {"label": label, "k": k, "q": q, "relation": sorted(R), "maltsev": has_maltsev([R], q)}
    pool = knot_pool(R, k, q)
    row["knots"] = []
    for (n, K), d in pool:
        rect = all(rectangular_at(K, n, e) for e in range(n))
        mech = None
        if not rect:
            meeting = [e for e in range(n) if pairwise_meeting_at(K, n, e)]
            sel = selector(K, n)
            mech = "pairwise meeting" if meeting else ("selector" if sel else "neither")
        row["knots"].append({"definition": d, "arity": n, "size": len(K), "rectangular": rect, "mechanism": mech})
    row["knot_failure"] = hub_failure(pool) if pool else None
    rels, deriv = binary_closure(binary_projections(R, k) if k > 2 else [R], q)
    th = tie_hub(rels)
    row["tie_failure"] = {"T1": th[0], "T2": th[1], "derivations": deriv[:max(th) + 1],
                          "bases": [sorted(b) for b in (binary_projections(R, k) if k > 2 else [R])]} if th else None
    row["any_failure"] = bool(row["knot_failure"] or row["tie_failure"])
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261020)
    q = 3
    rows = []
    ops = []
    for i in range(5):
        ops.append((f"maltsev {i}", [(3, random_maltsev(rng, q))]))
    for i in range(5):
        ops.append((f"majority {i}", [(3, random_majority(rng, q))]))
    for i, f in enumerate(semilattices(q)):
        ops.append((f"semilattice {i}", [(2, (lambda f: lambda x, y: f[(x, y)])(f))]))
    r = rps()
    ops.append(("rock-paper-scissors", [(2, lambda x, y: r[(x, y)])]))
    for i in range(5):
        ops.append((f"conservative {i}", [(3, random_conservative(rng, q))]))
    for i in range(5):
        ops.append((f"idempotent {i}", [(3, random_idempotent(rng, q))]))
    for name, op in ops:
        for k in (2, 3):
            for _ in range(10):
                gens = [tuple(rng.randrange(q) for _ in range(k)) for _ in range(rng.randint(2, 4))]
                R = generate(gens, op, k)
                if len(R) == q ** k:
                    continue
                rows.append({**analyse(R, k, q, name), "part": "structured"})
        log(f"{name} done")
    for mask in range(1, 2 ** 9 - 1):
        R = {t for i, t in enumerate(product(range(q), repeat=2)) if mask >> i & 1}
        rows.append({**analyse(R, 2, q, "binary"), "part": "binary"})
    log("binary relations done")

    # disjoint unions
    parity = {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}
    implication = {(2, 2), (2, 3), (3, 3)}
    iso = {(2, 2), (3, 3), (3, 4), (4, 3)}
    unions = []
    for name, other, Q in (("parity beside implication", implication, 4), ("parity beside an isolated value", iso, 5)):
        maltsev = has_maltsev([parity, other], Q)
        union = {"name": name, "domain": Q, "maltsev": maltsev}
        pool = knot_pool(parity, 3, Q)
        union["knots_found"] = len(pool)
        union["knot_failure_within_parity"] = hub_failure(pool) is not None
        rels, _ = binary_closure([other], Q)
        union["tie_failure_within_other"] = tie_hub(rels) is not None
        mixed = 0
        for _ in range(60):
            n = rng.randint(3, 5)
            copies = []
            for _ in range(rng.randint(2, 4)):
                if rng.random() < 0.5:
                    copies.append(("p", tuple(rng.randrange(n) for _ in range(3))))
                else:
                    copies.append(("o", tuple(rng.randrange(n) for _ in range(2))))
            S = set()
            for a in product(range(Q), repeat=n):
                if all((tuple(a[v] for v in c) in (parity if kind == "p" else other)) for kind, c in copies):
                    S.add(a)
            if S and failure(S, n, knots_only=True):
                mixed += 1
        union["mixed_systems_knot_failures"] = mixed
        unions.append(union)
    log("disjoint unions done")

    structured = [r for r in rows if r["part"] == "structured"]
    binary = [r for r in rows if r["part"] == "binary"]
    allrows = structured + binary
    m1 = not any(r["any_failure"] for r in allrows if r["maltsev"])
    m2 = all(all(kn["rectangular"] for kn in r["knots"]) for r in allrows if not r["knot_failure"])
    m3 = (unions[0]["knots_found"] > 0 and not unions[0]["maltsev"] and not unions[0]["knot_failure_within_parity"]
          and unions[0]["tie_failure_within_other"] and unions[0]["mixed_systems_knot_failures"] == 0
          and unions[1]["knots_found"] > 0 and not unions[1]["maltsev"] and not unions[1]["knot_failure_within_parity"]
          and not unions[1]["tie_failure_within_other"] and unions[1]["mixed_systems_knot_failures"] == 0)
    nonrect = [kn for r in allrows for kn in r["knots"] if not kn["rectangular"]]
    m4 = all(kn["mechanism"] in ("pairwise meeting", "selector") for kn in nonrect)
    colour = next(r for r in binary if sorted(map(tuple, r["relation"])) == sorted((x, y) for x in range(3) for y in range(3) if x != y))
    controls = {
        "C1_colouring_has_knot_failure": bool(colour["knot_failure"]),
        "C2_no_failure_implies_maltsev_rejected": any(not r["any_failure"] and not r["maltsev"] for r in allrows),
        "C3_all_knots_rectangular_rejected": len(nonrect) > 0,
    }
    by_label = {}
    for r in structured:
        key = r["label"].split(" ")[0]
        s = by_label.setdefault(key, {"relations": 0, "maltsev": 0, "with_knots": 0, "knot_failure": 0, "any_failure": 0,
                                      "nonrectangular_knots": 0})
        s["relations"] += 1
        s["maltsev"] += r["maltsev"]
        s["with_knots"] += bool(r["knots"])
        s["knot_failure"] += bool(r["knot_failure"])
        s["any_failure"] += r["any_failure"]
        s["nonrectangular_knots"] += sum(not kn["rectangular"] for kn in r["knots"])
    summary = {
        "structured": by_label,
        "binary": {"relations": len(binary), "maltsev": sum(r["maltsev"] for r in binary),
                   "with_knots": sum(bool(r["knots"]) for r in binary),
                   "knot_failure": sum(bool(r["knot_failure"]) for r in binary),
                   "any_failure": sum(r["any_failure"] for r in binary)},
        "nonrectangular_knots": {"total": len(nonrect),
                                 "pairwise_meeting": sum(kn["mechanism"] == "pairwise meeting" for kn in nonrect),
                                 "selector": sum(kn["mechanism"] == "selector" for kn in nonrect),
                                 "neither": sum(kn["mechanism"] == "neither" for kn in nonrect)},
        "non_maltsev_without_any_failure": sum(not r["any_failure"] and not r["maltsev"] for r in allrows),
        "non_maltsev_with_knots_without_knot_failure": sum(bool(r["knots"]) and not r["knot_failure"] and not r["maltsev"]
                                                            for r in allrows),
        "disjoint_unions": unions,
    }
    result = {"experiment_id": "MALTSEV-CONVERSE-20261020-001A-E001", "evidence_stage": "exploratory", "summary": summary,
              "predictions": {"M1": m1, "M2": m2, "M3": m3, "M4": m4}, "controls": controls,
              "signal": m1 and m2 and m3 and m4, "wall_seconds": round(time.time() - START, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, default=list) + "\n")
    log(f"summary {json.dumps(summary)}")
    log(f"predictions {result['predictions']} controls {controls} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
