#!/usr/bin/env python3
"""Census for CYCLE-TOPS-20261021-001A-E001 (contract.json).

For every law in the roster:
- elimination on random systems; the first failure is recorded with its system;
- for laws without a failure:
  - candidate tops: on each range found, the transitive closure of the proper reflexive relations observed (two-variable
    projections between variables sharing that range, and the fibre-sharing relation of every circuit at each of its
    variables). A candidate is certified when every coarser proper equivalence is broken by a polymorphism of a pool;
  - hidden circuits: each sampled system against its image modulo the candidate tops;
  - top images of ties (bijective?) and of knots (functional at every variable, or overlapping somewhere?);
  - a ternary polymorphism Mal'tsev modulo the candidate tops on the knot ranges found, and on all ranges found;
  - for block removals and lifts of K6: the same systems over the Z3 law have the same constrained sets.
- controls: Z6 and the Boolean neither-knot fail; parity and the Z3 law have Mal'tsev polymorphisms; for Z6 the
  observed proper reflexive relations close up to the total relation and blurring by x = y mod 2 hides a circuit.

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, permutations, product
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "CYCLE-TOPS-20261021-001A" / HERE.name
CAP = 300
SEED = 20261021


# ------------------------------------------------------------------ laws

M3 = sorted(t for t in product(range(3), repeat=3) if sum(t) % 3 == 0)
G = (0, 1, 2, 2)
LIFT = sorted(t for t in product(range(4), repeat=3) if tuple(G[x] for x in t) in set(M3))
BLOCK = sorted(product((2, 3), repeat=3))


def block_classes():
    """One removal per class of subsets of the (2,2,2)-block under coordinate permutations and swapping 2 and 3."""
    def canon(X):
        best = None
        for p in permutations(range(3)):
            for sw in (False, True):
                Y = tuple(sorted(tuple((5 - t[p[i]]) if sw else t[p[i]] for i in range(3)) for t in X))
                best = Y if best is None or Y < best else best
        return best
    reps = {}
    for mask in range(256):
        X = tuple(b for i, b in enumerate(BLOCK) if mask >> i & 1)
        reps.setdefault(canon(X), X)
    return sorted(reps, key=lambda X: (len(X), X))


def laws():
    out = {}
    for X in block_classes():
        name = "L-{" + ",".join("".join(map(str, t)) for t in X) + "}"
        out[name] = {"D": 4, "rels": [sorted(set(LIFT) - set(X))], "family": "block removal", "removed": X,
                     "image": list(G)}
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    for a in (0, 1):
        g7 = list(range(6)) + [a]
        R = {t for t in product(range(7), repeat=3) if tuple(g7[x] for x in t) in K6} - {(a, a, a)}
        out[f"K6 lift at {a}"] = {"D": 7, "rels": [sorted(R)], "family": "K6 lift", "image": [g7[x] // 2 for x in range(7)]}
    P3 = sorted(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0)
    J = [(2, 2), (3, 3), (3, 4), (4, 3)]
    out["parity + J"] = {"D": 5, "rels": [P3, J], "family": "disjoint union"}
    K4 = sorted(set(LIFT) - {(2, 2, 2)})
    out["K4 + Z3"] = {"D": 7, "rels": [K4, sorted(tuple(x + 4 for x in t) for t in M3)], "family": "disjoint union"}
    out["Z6"] = {"D": 6, "rels": [sorted(t for t in product(range(6), repeat=3) if sum(t) % 6 == 0)], "family": "control"}
    out["neither-knot"] = {"D": 2, "rels": [[(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]], "family": "control"}
    out["parity"] = {"D": 2, "rels": [P3], "family": "control"}
    out["Z3"] = {"D": 3, "rels": [M3], "family": "control"}
    return out


LAWS = laws()


def budget(D):
    """(systems, largest number of variables)"""
    return {2: (2000, 7), 3: (2000, 6), 4: (6000, 7), 5: (2000, 6), 6: (3000, 5), 7: (1000, 5)}[D]


# ------------------------------------------------------------------ systems

def solve(rels, D, n, cons):
    """All solutions of a system; cons is a list of (relation index, variable tuple)."""
    order = []
    for _, vs in cons:
        for v in vs:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    by_last = {}
    sets = [set(R) for R in rels]
    for ri, vs in cons:
        by_last.setdefault(max(pos[v] for v in vs), []).append((sets[ri], vs))
    out, a = [], [0] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in range(D):
            a[v] = x
            if all(tuple(a[u] for u in vs) in R for R, vs in by_last.get(i, ())):
                go(i + 1)
    go(0)
    return out


def free_sets(S, n):
    ranges = [frozenset(s[i] for s in S) for i in range(n)]
    fr = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            full = 1
            for v in Y:
                full *= len(ranges[v])
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == full
    return fr, ranges


def circuits(fr):
    return [Y for Y, f in fr.items() if len(Y) > 1 and not f and all(fr[tuple(x for x in Y if x != w)] for w in Y)]


def elimination_failure(fr, cs):
    for a, b in combinations(cs, 2):
        for e in set(a) & set(b):
            if fr[tuple(sorted((set(a) | set(b)) - {e}))]:
                return [list(a), list(b), e]
    return None


def random_system(rng, law, n):
    cons = []
    for _ in range(rng.randint(1, 5)):
        ri = rng.randrange(len(law["rels"]))
        cons.append((ri, tuple(rng.randrange(n) for _ in range(len(law["rels"][ri][0])))))
    return cons


def fibres(S, C, e):
    out = {}
    for s in S:
        out.setdefault(tuple(s[v] for v in C if v != e), set()).add(s[e])
    return list(out.values())


# ------------------------------------------------------------------ equivalences

def closure(B, pairs):
    """Partition of B generated by the given pairs (union-find)."""
    parent = {x: x for x in B}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for x, y in pairs:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx
    blocks = {}
    for x in B:
        blocks.setdefault(find(x), set()).add(x)
    return sorted(sorted(b) for b in blocks.values())


def partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


def coarser(blocks):
    """Equivalences strictly coarser than the partition `blocks` and not total, as lists of merged blocks."""
    out = []
    for p in partitions(list(range(len(blocks)))):
        if 1 < len(p) < len(blocks):
            out.append([sorted(x for i in part for x in blocks[i]) for part in p])
    return out


def breaks(F, blocks):
    """A witness that the ternary table F does not preserve the equivalence given by blocks, or None."""
    cls = {x: i for i, b in enumerate(blocks) for x in b}
    pairs = sorted(((x, y) for b in blocks for x in b for y in b), key=lambda p: p[0] == p[1])
    for p, q, r in product(pairs, repeat=3):
        if cls[F[(p[0], q[0], r[0])]] != cls[F[(p[1], q[1], r[1])]]:
            return [list(p), list(q), list(r)]
    return None


# ------------------------------------------------------------------ solver over operation tables

class Solver:
    """Ternary operations on {0..D-1} preserving every relation of a law, under unary restrictions."""

    def __init__(self, D, rels):
        self.D, self.rels = D, [[tuple(t) for t in R] for R in rels]
        self.args = list(product(range(D), repeat=3))
        self.idx = {a: i for i, a in enumerate(self.args)}
        self.dom0 = [set(range(D)) for _ in self.args]
        self.cons, self.by_var = [], {}
        seen = set()
        for ri, R in enumerate(self.rels):
            for ts in product(R, repeat=3):
                sc = (ri, tuple(self.idx[tuple(t[i] for t in ts)] for i in range(len(R[0]))))
                if sc not in seen:
                    seen.add(sc)
                    self.cons.append(sc)
        for ci, (_, sc) in enumerate(self.cons):
            for v in set(sc):
                self.by_var.setdefault(v, []).append(ci)

    def restrict(self, args, values):
        self.dom0[self.idx[args]] &= set(values)

    def _revise(self, dom, ci):
        ri, sc = self.cons[ci]
        support = {v: set() for v in set(sc)}
        for t in self.rels[ri]:
            seen, good = {}, True
            for v, x in zip(sc, t):
                if x not in dom[v] or seen.get(v, x) != x:
                    good = False
                    break
                seen[v] = x
            if good:
                for v, x in seen.items():
                    support[v].add(x)
        changed = []
        for v, s in support.items():
            if s != dom[v]:
                if not s:
                    return None
                dom[v] = s
                changed.append(v)
        return changed

    def _propagate(self, dom, queue):
        queue, inq = list(queue), set(queue)
        while queue:
            ci = queue.pop()
            inq.discard(ci)
            ch = self._revise(dom, ci)
            if ch is None:
                return False
            for v in ch:
                for cj in self.by_var.get(v, ()):
                    if cj not in inq:
                        inq.add(cj)
                        queue.append(cj)
        return True

    def solve(self, cap=CAP, rng=None):
        t0 = time.time()
        dom = [set(d) for d in self.dom0]
        if any(not d for d in dom) or not self._propagate(dom, range(len(self.cons))):
            return None

        def go(dom):
            if time.time() - t0 > cap:
                raise TimeoutError
            free = [v for v, d in enumerate(dom) if len(d) > 1]
            if not free:
                return dom
            v = min(free, key=lambda u: (len(dom[u]), -len(self.by_var.get(u, ()))))
            vals = sorted(dom[v])
            if rng is not None:
                rng.shuffle(vals)
            for x in vals:
                d2 = [set(s) for s in dom]
                d2[v] = {x}
                if self._propagate(d2, self.by_var.get(v, ())):
                    r = go(d2)
                    if r is not None:
                        return r
            return None
        r = go(dom)
        return None if r is None else {a: next(iter(r[i])) for a, i in self.idx.items()}


def maltsev_modulo(law, tops, ranges, cap=CAP):
    """A ternary polymorphism F with F(x,y,y) ~ x and F(x,x,y) ~ y modulo the top of every listed range."""
    S = Solver(law["D"], law["rels"])
    for B in ranges:
        cls = {x: b for b in tops[B] for x in b}
        for x in B:
            for y in B:
                S.restrict((x, y, y), cls[x])
                S.restrict((x, x, y), cls[y])
    try:
        return "found", S.solve(cap)
    except TimeoutError:
        return "timeout", None


def pool(law, extra, rng, count=6):
    """Polymorphisms for certifying tops: argument permutations of the given tables and of random solutions."""
    S = Solver(law["D"], law["rels"])
    found = list(extra)
    tries = 0
    while len(found) < len(extra) + count and tries < 2 * count:
        tries += 1
        S.dom0 = [set(range(law["D"])) for _ in S.args]
        for _ in range(rng.randint(1, 6)):
            S.restrict(rng.choice(S.args), [rng.randrange(law["D"])])
        try:
            r = S.solve(10, rng)
        except TimeoutError:
            r = None
        if r is not None:
            found.append(r)
    out = []
    for F in found:
        for p in permutations(range(3)):
            out.append({a: F[tuple(a[p[i]] for i in range(3))] for a in F})
    return out


# ------------------------------------------------------------------ one law

def census(name):
    law = LAWS[name]
    D, rels = law["D"], law["rels"]
    rng = random.Random(f"{SEED}-{name}")
    N, nmax = budget(D)
    row = {"law": name, "family": law["family"], "D": D, "systems": 0, "failure": None}
    kept, ranges, knot_ranges, refl = [], {frozenset(range(D))}, set(), {}
    t0 = time.time()
    for _ in range(N):
        n = rng.randint(2, nmax)
        cons = random_system(rng, law, n)
        S = solve(rels, D, n, cons)
        if not S:
            continue
        row["systems"] += 1
        fr, rg = free_sets(S, n)
        cs = circuits(fr)
        f = elimination_failure(fr, cs)
        if f:
            row["failure"] = {"n": n, "constraints": [[ri, list(vs)] for ri, vs in cons], "circuits_and_shared": f}
            break
        kept.append((n, cons))
        ranges.update(rg)
        for u, v in combinations(range(n), 2):
            if rg[u] == rg[v] and len(rg[u]) > 1:
                P = {(s[u], s[v]) for s in S}
                if all((x, x) in P for x in rg[u]) and len(P) < len(rg[u]) ** 2:
                    refl.setdefault(rg[u], set()).update(P | {(y, x) for x, y in P})
        for C in cs:
            if len(C) >= 3:
                knot_ranges.update(rg[v] for v in C)
            for e in C:
                lam = {(x, y) for F in fibres(S, C, e) for x in F for y in F}
                if len(lam) < len(rg[e]) ** 2:
                    refl.setdefault(rg[e], set()).update(lam)
    row["seconds_sampling"] = round(time.time() - t0, 1)
    if name == "Z6":
        row["control"] = z6_control(law, rng)
    if row["failure"]:
        return row

    tops = {B: closure(sorted(B), refl.get(B, ())) for B in ranges}
    row["ranges"] = sorted(sorted(B) for B in ranges)
    row["knot_ranges"] = sorted(sorted(B) for B in knot_ranges)
    row["tops"] = {",".join(map(str, sorted(B))): tops[B] for B in ranges}
    row["collapsed"] = sorted(sorted(B) for B in ranges if len(B) > 1 and len(tops[B]) == 1)

    # Mal'tsev modulo the tops: knot ranges, then all ranges
    t1 = time.time()
    st_k, F_k = maltsev_modulo(law, tops, sorted(knot_ranges, key=sorted))
    st_a, F_a = maltsev_modulo(law, tops, sorted(ranges, key=sorted))
    row["maltsev_knot_ranges"] = st_k if F_k is not None or st_k == "timeout" else "none"
    row["maltsev_all_ranges"] = st_a if F_a is not None or st_a == "timeout" else "none"
    row["table_knot_ranges"] = [F_k[a] for a in sorted(F_k)] if F_k else None
    row["table_all_ranges"] = [F_a[a] for a in sorted(F_a)] if F_a else None
    row["seconds_maltsev"] = round(time.time() - t1, 1)

    # certify the candidate tops
    P = pool(law, [F for F in (F_k, F_a) if F], rng)
    cert, witnesses = {}, {}
    for B in ranges:
        if len(B) < 2:
            continue
        key = ",".join(map(str, sorted(B)))
        ok, wit = True, []
        for E in coarser(tops[B]):
            w = None
            for i, F in enumerate(P):
                w = breaks(F, E)
                if w:
                    wit.append({"equivalence": E, "pool_index": i, "pairs": w})
                    break
            if w is None:
                ok = False
        cert[key], witnesses[key] = ok, wit
    row["certified"] = cert
    row["certificates"] = witnesses
    row["pool"] = [[F[a] for a in sorted(F)] for F in P]

    # second pass: hidden circuits, tie and knot top images, dressed
    cls_of = {B: {x: i for i, b in enumerate(tops[B]) for x in b} for B in ranges}
    hidden = ties = ties_bij = ties_cert = knots = knots_fun = knots_over = knots_neither = 0
    dressed = 0
    examples = {}
    for n, cons in kept:
        S = solve(rels, D, n, cons)
        fr, rg = free_sets(S, n)
        cs = circuits(fr)
        top = [cls_of[rg[v]] for v in range(n)]
        T = {tuple(top[v][s[v]] for v in range(n)) for s in S}
        ntop = [len(tops[rg[v]]) for v in range(n)]
        frT = {}
        for Y in fr:
            full = 1
            for v in Y:
                full *= ntop[v]
            frT[Y] = len({tuple(t[v] for v in Y) for t in T}) == full
        if frT != fr:
            hidden += 1
            examples.setdefault("hidden", {"n": n, "constraints": [[ri, list(vs)] for ri, vs in cons]})
        for C in cs:
            img = {tuple(t[v] for v in C) for t in T}
            if len(C) == 2:
                ties += 1
                u, v = C
                certified = all(cert.get(",".join(map(str, sorted(rg[w]))), True) for w in C)
                ties_cert += certified
                bij = ntop[u] == ntop[v] == len(img) and len({a for a, _ in img}) == len({b for _, b in img}) == len(img)
                ties_bij += bij
                if not bij and certified:
                    examples.setdefault("tie", {"n": n, "constraints": [[ri, list(vs)] for ri, vs in cons], "tie": list(C)})
            else:
                knots += 1
                kinds = []
                for i, e in enumerate(C):
                    fib = {}
                    for t in img:
                        fib.setdefault(t[:i] + t[i + 1:], set()).add(t[i])
                    if all(len(F) == 1 for F in fib.values()):
                        kinds.append("functional")
                    elif len({(x, y) for F in fib.values() for x in F for y in F}) == ntop[e] ** 2:
                        kinds.append("overlapping")
                    else:
                        kinds.append("neither")
                knots_fun += all(k == "functional" for k in kinds)
                knots_over += "overlapping" in kinds
                knots_neither += "neither" in kinds
                if "functional" not in kinds or "neither" in kinds:
                    examples.setdefault("knot", {"n": n, "constraints": [[ri, list(vs)] for ri, vs in cons], "knot": list(C),
                                                 "kinds": kinds})
        if "image" in law:
            S3 = solve([M3], 3, n, [(0, vs) for _, vs in cons])
            fr3, _ = free_sets(S3, n)
            dressed += fr3 == fr
    row.update({"hidden_systems": hidden, "ties": ties, "ties_bijective": ties_bij, "ties_certified": ties_cert,
                "knots": knots, "knots_functional": knots_fun, "knots_overlapping": knots_over,
                "knots_neither": knots_neither, "dressed_systems": dressed if "image" in law else None,
                "kept_systems": len(kept), "examples": examples, "seconds": round(time.time() - t0, 1)})
    return row


def z6_control(law, rng):
    """Without composition like cycles the conclusions fail.
    - x = y mod 3 is exists z: R(x,x,z) and R(y,y,z); x = y mod 2 is exists z: R(z,z,z) and R(x,y,z). Both are
      proper and reflexive, and they join to the total relation.
    - The mod-3 system, with z hidden, ties x and y over full ranges; blurring both by x = y mod 2 leaves them free."""
    D, rels = law["D"], law["rels"]
    mod3 = {(s[0], s[1]) for s in solve(rels, D, 3, [(0, (0, 0, 2)), (0, (1, 1, 2))])}
    mod2 = {(s[0], s[1]) for s in solve(rels, D, 3, [(0, (2, 2, 2)), (0, (0, 1, 2))])}
    blur = {(x % 2, y % 2) for x, y in mod3}
    return {"mod3": mod3 == {(x, y) for x in range(6) for y in range(6) if (x - y) % 3 == 0},
            "mod2": mod2 == {(x, y) for x in range(6) for y in range(6) if (x - y) % 2 == 0},
            "join_total": len(closure(list(range(6)), mod3 | mod2)) == 1,
            "tie_constrained": len(mod3) < 36, "mod2_blur_hides_tie": len(blur) == 4}


# ------------------------------------------------------------------ main

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    names = list(LAWS)
    with Pool(min(22, len(names))) as p:
        rows = p.map(census, names)
    by = {r["law"]: r for r in rows}
    lines = []
    for r in rows:
        if r["failure"]:
            lines.append(f"{r['law']}: failure after {r['systems']} systems")
        else:
            lines.append(f"{r['law']}: no failure in {r['systems']} systems; knot ranges {r['knot_ranges']}; "
                         f"Mal'tsev knot/all {r['maltsev_knot_ranges']}/{r['maltsev_all_ranges']}; hidden "
                         f"{r['hidden_systems']}; ties {r['ties_bijective']}/{r['ties']}; knots functional "
                         f"{r['knots_functional']}/{r['knots']}; certified {r['certified']}")
    blocks = [r for r in rows if r["family"] == "block removal"]
    surv_blocks = sorted(r["law"] for r in blocks if not r["failure"])
    expected_blocks = sorted(["L-{}", "L-{222}", "L-{223}", "L-{223,232}", "L-{223,232,322}"])
    survivors = [r for r in rows if not r["failure"] and r["family"] != "control"]
    lifts = [by["K6 lift at 0"], by["K6 lift at 1"]]
    unions = [by["parity + J"], by["K4 + Z3"]]
    dressed_ok = all(r["dressed_systems"] == r["kept_systems"] for r in survivors if r["dressed_systems"] is not None)
    predictions = {
        "H1": surv_blocks == expected_blocks and all(not r["failure"] for r in lifts + unions) and dressed_ok,
        "H2": all(r["hidden_systems"] == 0 for r in survivors),
        "H3": all(r["ties_bijective"] == r["ties"] for r in survivors if all(r["certified"].values())),
        "H4": all(r["knots_functional"] == r["knots"] for r in survivors),
        "H5": all(r["maltsev_knot_ranges"] == "found" for r in survivors),
        "H6": all(r["maltsev_all_ranges"] == "none" for r in unions)
        and all(r["maltsev_all_ranges"] == "found" for r in survivors if r["family"] != "disjoint union"),
    }
    z6 = by["Z6"].get("control", {})
    controls = {
        "C1_Z6": bool(by["Z6"]["failure"]) and all(z6.get(k) is True for k in
                                                   ("mod3", "mod2", "join_total", "tie_constrained", "mod2_blur_hides_tie")),
        "C2_neither_knot_fails": bool(by["neither-knot"]["failure"]),
        "C3_parity_Z3": all(not by[x]["failure"] and by[x]["maltsev_all_ranges"] == "found" for x in ("parity", "Z3")),
        "C4_union_tops": all(r["tops"][",".join(map(str, range(r["D"])))] == [[x] for x in range(r["D"])]
                             and r["certified"][",".join(map(str, range(r["D"])))] for r in unions),
    }
    result = {"experiment": "CYCLE-TOPS-20261021-001A-E001", "laws": len(rows), "block_survivors": surv_blocks,
              "predictions": predictions, "controls": controls,
              "signal": all(predictions.values()) and all(controls.values()), "seconds": round(time.time() - t0, 1)}
    with (OUT / "raw_rows.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=list) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    text = "\n".join(lines) + "\n" + json.dumps(result, indent=1, sort_keys=True) + "\n"
    (OUT / "run_output.txt").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
