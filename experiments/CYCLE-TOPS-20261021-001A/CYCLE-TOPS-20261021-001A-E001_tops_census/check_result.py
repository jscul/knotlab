#!/usr/bin/env python3
"""Independent check of CYCLE-TOPS-20261021-001A-E001. It imports no producer code.

- Every recorded elimination failure is re-verified by brute-force enumeration of its system.
- Every recorded operation table is re-verified as a polymorphism of every relation of its law, with its conditions
  modulo the recorded tops on the recorded ranges.
- Every certificate is re-verified: each coarser proper equivalence of a certified top is listed with its own
  enumeration and must carry a witness from the recorded pool, whose tables are re-verified as polymorphisms.
- The hidden-circuit, tie, knot and dressed counts are replicated on 400 fresh systems per surviving law, drawn with a
  different generator and analysed with this file's own code and the recorded tops.
- For the disjoint unions: the whole-domain top is equality and some relation is not rectangular, so no operation is
  exactly Mal'tsev on the whole domain.
- The prediction and control flags are recomputed from the rows.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "CYCLE-TOPS-20261021-001A" / HERE.name


def roster():
    Z3 = {t for t in product(range(3), repeat=3) if (t[0] + t[1] + t[2]) % 3 == 0}
    g = (0, 1, 2, 2)
    lift = {t for t in product(range(4), repeat=3) if (g[t[0]] + g[t[1]] + g[t[2]]) % 3 == 0}
    cube = list(product((2, 3), repeat=3))
    classes = {}
    for bits in range(256):
        X = frozenset(c for i, c in enumerate(cube) if bits & (1 << i))
        images = []
        for p in permutations(range(3)):
            for flip in (0, 1):
                images.append(tuple(sorted(tuple(t[p[j]] if not flip else 5 - t[p[j]] for j in range(3)) for t in X)))
        classes.setdefault(min(images), X)
    out = {}
    for key in classes:  # each class is named and built by its least image, as the producer does
        out["L-{" + ",".join("".join(str(x) for x in t) for t in key) + "}"] = (4, [lift - set(key)], "block removal")
    nt = {t for t in product((0, 1), repeat=3) if t.count(1) != 2}
    K6 = {(2 * u[0] + w[0], 2 * u[1] + w[1], 2 * u[2] + w[2]) for u in Z3 for w in nt}
    for a in (0, 1):
        gm = lambda x, a=a: a if x == 6 else x
        out[f"K6 lift at {a}"] = (7, [{t for t in product(range(7), repeat=3) if tuple(map(gm, t)) in K6} - {(a, a, a)}], "K6 lift")
    par = {t for t in product((0, 1), repeat=3) if t.count(1) % 2 == 0}
    out["parity + J"] = (5, [par, {(2, 2), (3, 3), (3, 4), (4, 3)}], "disjoint union")
    out["K4 + Z3"] = (7, [lift - {(2, 2, 2)}, {(a + 4, b + 4, c + 4) for a, b, c in Z3}], "disjoint union")
    out["Z6"] = (6, [{t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}], "control")
    out["neither-knot"] = (2, [{(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}], "control")
    out["parity"] = (2, [par], "control")
    out["Z3"] = (3, [Z3], "control")
    return out, Z3


def all_solutions(D, n, rels, cons):
    return [a for a in product(range(D), repeat=n) if all(tuple(a[v] for v in vs) in rels[ri] for ri, vs in cons)]


def analyse(S, n, sizes=None):
    """free(Y) for every nonempty Y, relative to the given range sizes (default: the observed ranges)."""
    rng_sizes = sizes or [len({s[v] for s in S}) for v in range(n)]
    free = {}
    for Y in (Y for k in range(1, n + 1) for Y in combinations(range(n), k)):
        need = 1
        for v in Y:
            need *= rng_sizes[v]
        free[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return free


def minimal_constrained(free):
    return [Y for Y in free if len(Y) >= 2 and not free[Y] and all(free[tuple(u for u in Y if u != w)] for w in Y)]


def is_pol(F, rels):
    for R in rels:
        Rl = list(R)
        k = len(Rl[0])
        for a in Rl:
            for b in Rl:
                for c in Rl:
                    if tuple(F[(a[i], b[i], c[i])] for i in range(k)) not in R:
                        return False
    return True


def set_partitions(xs):
    if not xs:
        yield []
        return
    for p in set_partitions(xs[1:]):
        yield [[xs[0]]] + p
        for i in range(len(p)):
            yield p[:i] + [[xs[0]] + p[i]] + p[i + 1:]


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = {}
    for line in (ART / "raw_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        rows[r["law"]] = r
    L, Z3 = roster()
    problems, report = [], {}
    if set(rows) != set(L):
        problems.append("roster differs")

    # failures
    fails = {}
    for name, r in rows.items():
        if not r["failure"]:
            continue
        D, rels, _ = L[name]
        f = r["failure"]
        n, cons = f["n"], [(ri, tuple(vs)) for ri, vs in f["constraints"]]
        S = all_solutions(D, n, rels, cons)
        fr = analyse(S, n)
        a, b, e = tuple(f["circuits_and_shared"][0]), tuple(f["circuits_and_shared"][1]), f["circuits_and_shared"][2]
        cs = minimal_constrained(fr)
        ok = a in cs and b in cs and e in a and e in b and fr[tuple(sorted((set(a) | set(b)) - {e}))]
        fails[name] = ok
        if not ok:
            problems.append(f"failure of {name} does not verify")
    report["failures_verified"] = sum(fails.values())

    # survivors: tables, certificates, replication
    rep = {}
    for name, r in rows.items():
        if r["failure"]:
            continue
        D, rels, family = L[name]
        args = list(product(range(D), repeat=3))
        tops = {tuple(int(x) for x in k.split(",")): [list(b) for b in v] for k, v in r["tops"].items()}
        cls = {B: {x: i for i, b in enumerate(tops[B]) for x in b} for B in tops}
        info = {}
        for which, rk in (("table_knot_ranges", "knot_ranges"), ("table_all_ranges", "ranges")):
            if r[which] is None:
                continue
            F = dict(zip(args, r[which]))
            good = is_pol(F, rels)
            for B in (tuple(b) for b in r[rk]):
                c = cls[B]
                good = good and all(c[F[(x, y, y)]] == c[x] and c[F[(x, x, y)]] == c[y] for x in B for y in B)
            info[which] = good
            if not good:
                problems.append(f"{name}: {which} does not verify")
        pool = [dict(zip(args, t)) for t in r["pool"]]
        pool_ok = {}
        for key, ok in r["certified"].items():
            if not ok:
                continue
            B = tuple(int(x) for x in key.split(","))
            blocks = tops[B]
            wit = {tuple(sorted(tuple(sorted(b)) for b in w["equivalence"])): w for w in r["certificates"][key]}
            for p in set_partitions(list(range(len(blocks)))):
                if not 1 < len(p) < len(blocks):
                    continue
                E = sorted(sorted(x for i in part for x in blocks[i]) for part in p)
                w = wit.get(tuple(tuple(b) for b in E))
                if w is None:
                    problems.append(f"{name}: no certificate for {E} on {key}")
                    continue
                i = w["pool_index"]
                if i not in pool_ok:
                    pool_ok[i] = is_pol(pool[i], rels)
                cE = {x: j for j, b in enumerate(E) for x in b}
                (x1, y1), (x2, y2), (x3, y3) = w["pairs"]
                inE = cE[x1] == cE[y1] and cE[x2] == cE[y2] and cE[x3] == cE[y3]
                broken = cE[pool[i][(x1, x2, x3)]] != cE[pool[i][(y1, y2, y3)]]
                if not (pool_ok[i] and inE and broken):
                    problems.append(f"{name}: certificate for {E} on {key} does not verify")
        info["certificates"] = "verified"

        # replication on fresh systems
        g = random.Random(f"check-{name}")
        hidden = ties = bij = knots = functional = dressed = kept = 0
        nmax = 5 if D <= 5 else 4
        tries = 0
        while kept < 400 and tries < 4000:
            tries += 1
            n = g.randint(2, nmax)
            cons = []
            for _ in range(g.randint(1, 4)):
                ri = g.randrange(len(rels))
                arity = len(next(iter(rels[ri])))
                cons.append((ri, tuple(g.randrange(n) for _ in range(arity))))
            S = all_solutions(D, n, rels, cons)
            if not S:
                continue
            fr = analyse(S, n)
            if minimal_constrained(fr) and any(
                    fr[tuple(sorted((set(a) | set(b)) - {e}))]
                    for a, b in combinations(minimal_constrained(fr), 2) for e in set(a) & set(b)):
                problems.append(f"{name}: replication found an elimination failure")
                break
            ranges = [tuple(sorted({s[v] for s in S})) for v in range(n)]
            if any(B not in tops for B in ranges):
                continue
            kept += 1
            T = {tuple(cls[ranges[v]][s[v]] for v in range(n)) for s in S}
            sizes = [len(tops[ranges[v]]) for v in range(n)]
            frT = analyse(list(T), n, sizes)
            hidden += frT != fr
            certified = lambda v: r["certified"].get(",".join(map(str, ranges[v])), True)
            for C in minimal_constrained(fr):
                img = {tuple(t[v] for v in C) for t in T}
                if len(C) == 2:
                    if certified(C[0]) and certified(C[1]):
                        ties += 1
                        u, v = C
                        bij += sizes[u] == sizes[v] == len(img) == len({p[0] for p in img}) == len({p[1] for p in img})
                else:
                    knots += 1
                    fun = True
                    for i in range(len(C)):
                        fib = {}
                        for t in img:
                            fib.setdefault(t[:i] + t[i + 1:], set()).add(t[i])
                        fun = fun and all(len(x) == 1 for x in fib.values())
                    functional += fun
            if family in ("block removal", "K6 lift"):
                S3 = all_solutions(3, n, [Z3], [(0, vs) for _, vs in cons])
                dressed += analyse(S3, n) == fr
        if kept < 100:
            problems.append(f"{name}: only {kept} fresh systems replicated")
        info.update({"replicated_systems": kept, "hidden": hidden, "ties": ties, "ties_bijective": bij, "knots": knots,
                     "knots_functional": functional, "dressed": dressed if family in ("block removal", "K6 lift") else None})
        rep[name] = info

    # unions: whole-domain top is equality and some relation is not rectangular
    unions = {}
    for name in ("parity + J", "K4 + Z3"):
        r = rows[name]
        D, rels, _ = L[name]
        key = ",".join(map(str, range(D)))
        eq = r["tops"][key] == [[x] for x in range(D)] and r["certified"][key]
        nonrect = False
        for R in rels:
            k = len(next(iter(R)))
            for e in range(k):
                fib = {}
                for t in R:
                    fib.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
                fs = list(fib.values())
                nonrect = nonrect or any(a != b and a & b for a in fs for b in fs)
        unions[name] = eq and nonrect
        if not unions[name]:
            problems.append(f"{name}: the reason for no exact Mal'tsev operation does not verify")
    report["unions_reason"] = unions

    # flags
    surv = [n for n, r in rows.items() if not r["failure"] and r["family"] != "control"]
    blocks = sorted(n for n, r in rows.items() if r["family"] == "block removal" and not r["failure"])
    flags = {
        "H1": blocks == sorted(["L-{}", "L-{222}", "L-{223}", "L-{223,232}", "L-{223,232,322}"])
        and all(not rows[n]["failure"] for n in ("K6 lift at 0", "K6 lift at 1", "parity + J", "K4 + Z3"))
        and all(rows[n]["dressed_systems"] == rows[n]["kept_systems"] for n in surv if rows[n]["dressed_systems"] is not None)
        and all(rep[n]["dressed"] == rep[n]["replicated_systems"] for n in surv if rep[n]["dressed"] is not None),
        "H2": all(rows[n]["hidden_systems"] == 0 and rep[n]["hidden"] == 0 for n in surv),
        "H3": all(rows[n]["ties_bijective"] == rows[n]["ties"] for n in surv if all(rows[n]["certified"].values()))
        and all(rep[n]["ties_bijective"] == rep[n]["ties"] for n in surv),
        "H4": all(rows[n]["knots_functional"] == rows[n]["knots"] and rep[n]["knots_functional"] == rep[n]["knots"] for n in surv),
        "H5": all(rows[n]["maltsev_knot_ranges"] == "found" and rep[n].get("table_knot_ranges") for n in surv),
        "H6": all(rows[n]["maltsev_all_ranges"] == "none" and unions[n] for n in ("parity + J", "K4 + Z3"))
        and all(rows[n]["maltsev_all_ranges"] == "found" and rep[n].get("table_all_ranges")
                for n in surv if rows[n]["family"] != "disjoint union"),
    }
    for h, v in flags.items():
        if v != result["predictions"][h]:
            problems.append(f"{h}: recorded {result['predictions'][h]}, recomputed {v}")
    report["flags"] = flags
    report["replication"] = rep

    # Z6 control recomputed
    D, rels, _ = L["Z6"]
    mod3 = {(s[0], s[1]) for s in all_solutions(6, 3, rels, [(0, (0, 0, 2)), (0, (1, 1, 2))])}
    mod2 = {(s[0], s[1]) for s in all_solutions(6, 3, rels, [(0, (2, 2, 2)), (0, (0, 1, 2))])}
    c1 = (bool(rows["Z6"]["failure"]) and fails.get("Z6", False)
          and mod3 == {(x, y) for x in range(6) for y in range(6) if (x - y) % 3 == 0}
          and mod2 == {(x, y) for x in range(6) for y in range(6) if (x - y) % 2 == 0}
          and len({(x % 2, y % 2) for x, y in mod3}) == 4)
    controls = {"C1_Z6": c1, "C2_neither_knot_fails": fails.get("neither-knot", False),
                "C3_parity_Z3": all(n in rep and rep[n].get("table_all_ranges") for n in ("parity", "Z3")),
                "C4_union_tops": all(unions.values())}
    for c, v in controls.items():
        if v != result["controls"][c]:
            problems.append(f"{c}: recorded {result['controls'][c]}, recomputed {v}")
    report["controls"] = controls

    status = "passed: every failure, table, certificate and flag agrees, and the replication agrees (V1, exploratory evidence only)" \
        if not problems else "failed"
    text = json.dumps(report, indent=1, sort_keys=True, default=str) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text[-3000:])
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
