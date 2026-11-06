#!/usr/bin/env python3
"""Census for MALTSEV-CONDITIONS-20261021-001A-E001 (contract.json).

Parts:
- Hagemann-Mitschke searches for K4, L223 and L233 (H1, H2);
- exhaustive Hagemann-Mitschke and Day chains in the two-element clones these laws and the shadow K6 restrict to
  (H2, H3), and in the eight Boolean dressings (H5);
- polymorphisms Mal'tsev modulo the tops (H4), with the derived equivalences;
- controls.

    python3 -B run.py
"""

from __future__ import annotations

import json
import sys
import time
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "MALTSEV-CONDITIONS-20261021-001A" / HERE.name
CAP = 600


# ------------------------------------------------------------------ solver over operation tables

class Solver:
    """Find operation tables (ops: name -> arity) on {0..D-1} preserving rel, under unary restrictions and equalities."""

    def __init__(self, D, rel, ops):
        self.D, self.rel, self.ops = D, [tuple(t) for t in rel], ops
        self.k = len(self.rel[0])
        self.idx = {}
        for name, ar in ops.items():
            for args in product(range(D), repeat=ar):
                self.idx[(name, args)] = len(self.idx)
        self.parent = list(range(len(self.idx)))
        self.dom = [set(range(D)) for _ in range(len(self.idx))]

    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def equal(self, e1, e2):
        a, b = self.find(self.idx[e1]), self.find(self.idx[e2])
        if a != b:
            self.parent[b] = a
            self.dom[a] &= self.dom[b]

    def restrict(self, e, values):
        self.dom[self.find(self.idx[e])] &= set(values)

    def _build(self):
        roots = sorted({self.find(i) for i in range(len(self.idx))})
        self.vdom = {r: set(self.dom[r]) for r in roots}
        scopes = set()
        for name, ar in self.ops.items():
            for ts in product(self.rel, repeat=ar):
                scopes.add(tuple(self.find(self.idx[(name, tuple(t[i] for t in ts))]) for i in range(self.k)))
        self.cons = list(scopes)
        self.by_var = {}
        for ci, sc in enumerate(self.cons):
            for v in set(sc):
                self.by_var.setdefault(v, []).append(ci)

    def _revise(self, dom, ci):
        sc = self.cons[ci]
        support = {v: set() for v in set(sc)}
        for t in self.rel:
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

    def solve(self, cap=CAP):
        self._build()
        t0 = time.time()
        dom = {v: set(d) for v, d in self.vdom.items()}
        if any(not d for d in dom.values()) or not self._propagate(dom, range(len(self.cons))):
            return None

        def go(dom):
            if time.time() - t0 > cap:
                raise TimeoutError
            free = [v for v, d in dom.items() if len(d) > 1]
            if not free:
                return dom
            v = min(free, key=lambda u: (len(dom[u]), -len(self.by_var.get(u, ()))))
            for x in sorted(dom[v]):
                d2 = {u: set(s) for u, s in dom.items()}
                d2[v] = {x}
                if self._propagate(d2, self.by_var.get(v, ())):
                    r = go(d2)
                    if r is not None:
                        return r
            return None

        r = go(dom)
        if r is None:
            return None
        return {name: [next(iter(r[self.find(self.idx[(name, args)])])) for args in product(range(self.D), repeat=ar)]
                for name, ar in self.ops.items()}


def hm(D, rel, n, cap=CAP):
    S = Solver(D, rel, {f"p{i}": 3 for i in range(1, n)})
    for x in range(D):
        for y in range(D):
            S.restrict(("p1", (x, y, y)), [x])
            S.restrict((f"p{n-1}", (x, x, y)), [y])
            for i in range(1, n - 1):
                S.equal((f"p{i}", (x, x, y)), (f"p{i+1}", (x, y, y)))
    try:
        return "found", S.solve(cap)
    except TimeoutError:
        return "timeout", None


def maltsev_on_tops(D, rel, classes, cap=CAP):
    """classes: list of (range, partition dict x -> allowed values) pairs; F must be Mal'tsev modulo each partition on its range."""
    S = Solver(D, rel, {"F": 3})
    for rng, cls in classes:
        for x in rng:
            for y in rng:
                S.restrict(("F", (x, y, y)), cls[x])
                S.restrict(("F", (x, x, y)), cls[y])
    try:
        return "found", S.solve(cap)
    except TimeoutError:
        return "timeout", None


# ------------------------------------------------------------------ two-element clones and chains

def two_element_pols(rel, ar):
    args = list(product((0, 1), repeat=ar))
    rl = list(rel)
    k = len(rl[0])
    out = []
    for tab in product((0, 1), repeat=2 ** ar):
        f = dict(zip(args, tab))
        if all(tuple(f[tuple(ts[j][i] for j in range(ar))] for i in range(k)) in rel for ts in product(rl, repeat=ar)):
            out.append(f)
    return out


def hm_chain(P3):
    B = (0, 1)
    start = [i for i, f in enumerate(P3) if all(f[(x, y, y)] == x for x in B for y in B)]
    end = {i for i, f in enumerate(P3) if all(f[(x, x, y)] == y for x in B for y in B)}
    seen, stack = set(start), list(start)
    while stack:
        i = stack.pop()
        if i in end:
            return True
        for j, g in enumerate(P3):
            if j not in seen and all(P3[i][(x, x, y)] == g[(x, y, y)] for x in B for y in B):
                seen.add(j)
                stack.append(j)
    return False


def day_chain(P4):
    B = (0, 1)
    ok = [i for i, f in enumerate(P4) if all(f[(x, y, y, x)] == x for x in B for y in B)]
    first = [i for i in ok if all(P4[i][a] == a[0] for a in P4[i])]
    last = {i for i in ok if all(P4[i][a] == a[3] for a in P4[i])}
    seen = {(i, 0) for i in first}
    stack = list(seen)
    while stack:
        i, par = stack.pop()
        if i in last:
            return True
        for j in ok:
            if par == 0:
                same = all(P4[i][(x, x, u, u)] == P4[j][(x, x, u, u)] for x in B for u in B)
            else:
                same = all(P4[i][(x, y, y, u)] == P4[j][(x, y, y, u)] for x in B for y in B for u in B)
            if same and (j, 1 - par) not in seen:
                seen.add((j, 1 - par))
                stack.append((j, 1 - par))
    return False


def chains(rel):
    P3, P4 = two_element_pols(rel, 3), two_element_pols(rel, 4)
    return {"ternary_polymorphisms": len(P3), "quaternary_polymorphisms": len(P4), "hm_chain": hm_chain(P3),
            "day_chain": day_chain(P4)}


# ------------------------------------------------------------------ derived equivalences

def solve_sys(R, D, n, cons):
    out = []
    for a in product(range(D), repeat=n):
        if all(tuple(a[v] for v in c) in R for c in cons):
            out.append(a)
    return out


def derived_equivalences(R, D, k):
    """Equivalences with full ranges among projections onto (0,1) of systems of one or two copies on k+1 variables."""
    n = k + 1
    scopes = list(product(range(n), repeat=k))
    eqs = set()
    for c1 in scopes:
        for c2 in [None] + scopes:
            cons = [c1] + ([c2] if c2 else [])
            S = solve_sys(R, D, n, cons)
            E = frozenset((t[0], t[1]) for t in S)
            if {a for a, _ in E} != set(range(D)):
                continue
            if all((a, a) in E for a in range(D)) and all((b, a) in E for a, b in E) and \
                    all((a, d) in E for a, b in E for c, d in E if b == c):
                eqs.add(E)
    proper = [E for E in eqs if len(E) < D * D]
    return proper


def classes_of(E, D):
    return {x: sorted(y for y in range(D) if (x, y) in E) for x in range(D)}


# ------------------------------------------------------------------ main

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    rows, summary = [], {}
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    g = (0, 1, 2, 2)
    L = {t for t in product(range(4), repeat=3) if tuple(g[x] for x in t) in M3}
    K4, L223, L233 = L - {(2, 2, 2)}, L - {(2, 2, 3)}, L - {(2, 3, 3)}
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    M4 = {t for t in product(range(2), repeat=4) if sum(t) % 2 == 0}
    K4x4 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M4 for w in M4 | {(1, 0, 0, 0)}}

    # H1, H2: Hagemann-Mitschke searches
    hm_rows = {}
    for name, R, ns in (("K4", K4, (2, 3)), ("L223", L223, (2, 3, 4, 5, 6)), ("L233", L233, (2, 3, 4, 5, 6))):
        res = {}
        for n in ns:
            t = time.time()
            status, w = hm(4, R, n)
            res[str(n)] = "found" if w else ("none" if status == "found" else "timeout")
            if w:
                rows.append({"part": "hm", "law": name, "n": n, "tables": w})
            print(f"HM {name} n={n}: {res[str(n)]} ({time.time()-t:.1f}s)", flush=True)
            if w:
                break
        hm_rows[name] = res
    summary["hagemann_mitschke"] = hm_rows

    # H2, H3: two-element restrictions
    blocks = {"K4 block (all but 000)": set(product((0, 1), repeat=3)) - {(0, 0, 0)},
              "L223 block (all but 001)": set(product((0, 1), repeat=3)) - {(0, 0, 1)},
              "L233 block (all but 011)": set(product((0, 1), repeat=3)) - {(0, 1, 1)},
              "K6 fibre (not exactly two ones)": not_two,
              "parity (control)": {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}}
    summary["two_element_chains"] = {}
    for name, R in blocks.items():
        c = chains(R)
        summary["two_element_chains"][name] = c
        rows.append({"part": "chains", "name": name, "relation": sorted(R), **c})
        print(f"chains {name}: {c}", flush=True)
    k6hm = {}
    for n in (2, 3):
        status, w = hm(6, K6, n)
        k6hm[str(n)] = "found" if w else ("none" if status == "found" else "timeout")
        print(f"HM K6 n={n}: {k6hm[str(n)]}", flush=True)
    summary["K6_hagemann_mitschke"] = k6hm

    # H4: Mal'tsev modulo the tops, with derived equivalences
    lift_cls = {0: [0], 1: [1], 2: [2, 3], 3: [2, 3]}
    exact013 = {x: [x] for x in (0, 1, 3)}
    shadow_cls = lambda D: {x: [2 * (x // 2), 2 * (x // 2) + 1] for x in range(D)}
    cases = {
        "K4": (4, K4, 3, [(range(4), lift_cls), ((0, 1, 3), exact013)], lift_cls),
        "L223": (4, L223, 3, [(range(4), lift_cls)], lift_cls),
        "L233": (4, L233, 3, [(range(4), lift_cls)], lift_cls),
        "K6": (6, K6, 3, [(range(6), shadow_cls(6))], shadow_cls(6)),
        "K4x4": (4, K4x4, 4, [(range(4), shadow_cls(4))], shadow_cls(4)),
    }
    summary["maltsev_on_tops"] = {}
    for name, (D, R, k, cls, top) in cases.items():
        t = time.time()
        proper = derived_equivalences(R, D, k)
        largest = max(proper, key=len) if proper else None
        top_matches = largest is not None and classes_of(largest, D) == {x: sorted(v) for x, v in top.items()}
        status, w = maltsev_on_tops(D, R, cls)
        res = {"found": w is not None, "status": status if w is None else "found", "derived_proper_equivalences": len(proper),
               "largest_is_top": top_matches, "seconds": round(time.time() - t, 1)}
        summary["maltsev_on_tops"][name] = res
        rows.append({"part": "tops", "law": name, "D": D, "relation": sorted(R), "classes": [[list(rg), {str(a): b for a, b in c.items()}] for rg, c in cls],
                     "table": w["F"] if w else None, "largest_derived": sorted(largest) if largest else None})
        print(f"Mal'tsev on tops {name}: {res}", flush=True)

    # H5: the eight Boolean dressings
    extra = [(0, 1, 1), (1, 0, 1), (1, 1, 0)]
    dress = {}
    for mask in range(8):
        K = set(not_two) | {extra[i] for i in range(3) if mask >> i & 1}
        c = chains(K)
        dress["".join(str(mask >> i & 1) for i in range(3))] = c
        rows.append({"part": "dressing", "added": [extra[i] for i in range(3) if mask >> i & 1], **c})
    summary["dressings"] = dress
    print(f"dressings: {dress}", flush=True)

    # controls
    Z6 = {t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}
    V4 = {(x, y, x ^ y) for x in range(4) for y in range(4)}
    NB = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}
    ctl = {}
    for name, D, R in (("Z6", 6, Z6), ("Z2xZ2", 4, V4), ("Boolean neither-knot", 2, NB)):
        status, w = hm(D, R, 2)
        ctl[name] = "found" if w else ("none" if status == "found" else "timeout")
        if w:
            rows.append({"part": "control", "law": name, "tables": w})
    summary["controls"] = ctl
    print(f"controls (Mal'tsev): {ctl}", flush=True)

    tc = summary["two_element_chains"]
    predictions = {
        "H1": hm_rows["K4"].get("2") == "none" and hm_rows["K4"].get("3") == "found",
        "H2": all(hm_rows[x].get(str(n)) == "none" for x in ("L223", "L233") for n in range(2, 7))
        and all(not tc[b]["hm_chain"] and not tc[b]["day_chain"] for b in ("L223 block (all but 001)", "L233 block (all but 011)")),
        "H3": not tc["K6 fibre (not exactly two ones)"]["hm_chain"] and not tc["K6 fibre (not exactly two ones)"]["day_chain"]
        and all(v == "none" for v in k6hm.values()),
        "H4": all(v["found"] and v["largest_is_top"] for v in summary["maltsev_on_tops"].values()),
        "H5": any(c["hm_chain"] and c["day_chain"] for c in dress.values()) and any(not c["hm_chain"] and not c["day_chain"] for c in dress.values()),
    }
    controls = {
        "C1_Z6_maltsev": {"passed": ctl["Z6"] == "found"},
        "C2_Z2xZ2_maltsev": {"passed": ctl["Z2xZ2"] == "found"},
        "C3_neither_knot_not_maltsev": {"passed": ctl["Boolean neither-knot"] == "none"},
        "C4_parity_chains": {"passed": tc["parity (control)"]["hm_chain"] and tc["parity (control)"]["day_chain"]},
    }
    result = {"schema_version": 1, "experiment_id": "MALTSEV-CONDITIONS-20261021-001A-E001", "status": "complete",
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
