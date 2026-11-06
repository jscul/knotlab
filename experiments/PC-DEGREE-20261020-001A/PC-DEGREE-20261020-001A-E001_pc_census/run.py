#!/usr/bin/env python3
"""PC-DEGREE-20261020-001A-E001: exact polynomial calculus degree of Tseitin formulas against carving width.

For each roster graph and an odd charge, computes the least degree d at which polynomial calculus refutes the
Tseitin system (outside characteristic 2), in four settings, by the signed closure described in contract.json:
union-find with signs over monomials of degree at most d, where the members of a component that may be
multiplied by y_e are translated together. Also computes the exact carving width by subset dynamic programming.

Writes raw_rows.jsonl, result.json and run_output.txt under artifacts/PC-DEGREE-20261020-001A/<this directory>.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "PC-DEGREE-20261020-001A" / HERE.name
ROSTER = ROOT / ("artifacts/CUTWIDTH-DEPTH-20261020-001A/CUTWIDTH-DEPTH-20261020-001A-E001_monotone_census/"
                 "raw_rows.jsonl")
ROSTER_SHA256 = "d465a0a23a3e4f56b9cdae43a8bc6945005a29bfebcb9738fab7e9c4ac150f36"
SEED = 20261021


def popcount(x: int) -> int:
    return bin(x).count("1")


class Graph:
    def __init__(self, edges):
        self.edges = [tuple(e) for e in edges]
        self.n = 1 + max(max(e) for e in self.edges)
        self.m = len(self.edges)
        self.star = [0] * self.n
        self.nbr = [0] * self.n
        for i, (a, b) in enumerate(self.edges):
            self.star[a] |= 1 << i
            self.star[b] |= 1 << i
            self.nbr[a] |= 1 << b
            self.nbr[b] |= 1 << a
        self.deg = [popcount(s) for s in self.star]
        self.maxdeg = max(self.deg)


# ---------------------------------------------------------------- the signed closure

def refutes(g: Graph, d: int, axioms: str, convention: str, charge) -> bool:
    """Does polynomial calculus of degree d refute the system?

    axioms: "balanced" | "standard" | "clause"; convention: "R" (reduced) | "S" (standard).
    """
    need = {"balanced": max((x + 1) // 2 for x in g.deg), "standard": g.maxdeg, "clause": g.maxdeg}[axioms]
    if need > d:
        return False
    parent, sign, members, bad = {}, {}, {}, set()

    def find(a):
        path = []
        while parent.get(a, a) != a:
            path.append(a)
            a = parent[a]
        acc = 1
        for node in reversed(path):
            acc *= sign[node]
            sign[node], parent[node] = acc, a
        return a, (sign[path[0]] if path else 1)

    def relate(a, b, s):
        """Record value(b) = s * value(a); return True if the closure grew."""
        ra, sa = find(a)
        rb, sb = find(b)
        if ra == rb:
            if sb != s * sa and ra not in bad:
                bad.add(ra)
                members.setdefault(ra, [ra])
                return True
            return False
        ma, mb = members.get(ra, [ra]), members.get(rb, [rb])
        if len(ma) < len(mb):
            ra, rb, sa, sb, ma, mb = rb, ra, sb, sa, mb, ma
        parent[rb], sign[rb] = ra, sb * s * sa
        members[ra] = ma + mb if ra not in members else (members[ra].extend(mb) or members[ra])
        members.pop(rb, None)
        if rb in bad:
            bad.discard(rb)
            bad.add(ra)
        return True

    def mark_bad(a):
        ra, _ = find(a)
        if ra in bad:
            return False
        bad.add(ra)
        members.setdefault(ra, [ra])
        return True

    for v in range(g.n):
        E, s = g.star[v], (-1) ** charge[v]
        if axioms == "balanced":
            bits = [i for i in range(g.m) if E >> i & 1]
            A = sum(1 << i for i in bits[:(len(bits) + 1) // 2])
            relate(A, E ^ A, s)
        elif axioms == "standard":
            relate(0, E, s)
        else:
            sub = E
            while True:
                relate(sub, E ^ sub, s)
                if sub == 0:
                    break
                sub = (sub - 1) & E
    changed = True
    while changed:
        changed = False
        for r in list(members):
            if r not in members:
                continue
            M = list(members[r])
            isbad = r in bad
            if not isbad and len(M) < 2:
                continue
            phi = None if isbad else {A: find(A)[1] for A in M}
            low = [A for A in M if popcount(A) <= d - 1]
            top = [A for A in M if popcount(A) == d] if convention == "R" else []
            for e in range(g.m):
                bit = 1 << e
                elig = low + [A for A in top if A & bit] if top else low
                if not elig:
                    continue
                if isbad:
                    for A in elig:
                        changed |= mark_bad(A ^ bit)
                elif len(elig) >= 2:
                    A0 = elig[0]
                    p0 = phi[A0]
                    for A in elig[1:]:
                        changed |= relate(A0 ^ bit, A ^ bit, p0 * phi[A])
        if find(0)[0] in bad:
            return True
    return find(0)[0] in bad


def least_degree(g, axioms, convention, charge, start, stop):
    for d in range(start, stop + 1):
        if refutes(g, d, axioms, convention, charge):
            return d
    return None


# ---------------------------------------------------------------- carving width

def cut_table(g: Graph):
    cut = [0] * (1 << g.n)
    for S in range(1, 1 << g.n):
        v = (S & -S).bit_length() - 1
        R = S ^ (1 << v)
        cut[S] = cut[R] + g.deg[v] - 2 * popcount(g.nbr[v] & R)
    return cut


def carving_width(g: Graph) -> int:
    cut = cut_table(g)
    full = (1 << g.n) - 1
    big = 10 ** 9
    best_below = [big] * (1 << g.n)        # least possible width of a rooted carving of S, edge above S included
    for v in range(g.n):
        best_below[1 << v] = cut[1 << v]
    for S in sorted(range(1, full + 1), key=popcount):
        if popcount(S) < 2:
            continue
        low = S & -S
        best = big
        sub = (S - 1) & S
        while sub:
            if sub & low:
                val = best_below[sub] if best_below[sub] > best_below[S ^ sub] else best_below[S ^ sub]
                if val < best:
                    best = val
            sub = (sub - 1) & S
        best_below[S] = cut[S] if cut[S] > best else best
    return min(max(best_below[S], best_below[full ^ S]) for S in range(1, full) if S & 1)


# ---------------------------------------------------------------- rosters

def connected(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, todo = {0}, [0]
    while todo:
        for y in adj[todo.pop()] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == n


def held_out(rng):
    out = []
    for n in (7, 8, 9, 10, 11):
        count = 0
        while count < 60:
            p = rng.uniform(0.25, 0.45)
            edges = [(a, b) for a, b in combinations(range(n), 2) if rng.random() < p]
            if len(edges) <= 18 and edges and connected(n, edges) and 1 + max(max(e) for e in edges) == n:
                out.append(("held-out", n, edges))
                count += 1
    return out


def named():
    def complete(n):
        return [(a, b) for a, b in combinations(range(n), 2)]

    def bipartite(p, q):
        return [(a, p + b) for a in range(p) for b in range(q)]

    grid = [(r * 4 + c, r * 4 + c + 1) for r in range(3) for c in range(3)] + \
           [(r * 4 + c, (r + 1) * 4 + c) for r in range(2) for c in range(4)]
    heawood = [(i, (i + 1) % 14) for i in range(14)] + [(i, (i + 5) % 14) for i in range(0, 14, 2)]
    mk = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 8) for i in range(8)] + \
         [(8 + i, 8 + (i + 3) % 8) for i in range(8)]
    q4 = [(a, a ^ (1 << i)) for a in range(16) for i in range(4) if a < a ^ (1 << i)]
    graphs = {"K44": bipartite(4, 4), "K45": bipartite(4, 5), "K55": bipartite(5, 5), "K6": complete(6),
              "K7": complete(7), "grid3x4": grid, "heawood": heawood, "moebius-kantor": mk, "Q4": q4}
    return [("named:" + name, None, sorted(tuple(sorted(e)) for e in edges)) for name, edges in graphs.items()]


# ---------------------------------------------------------------- main

def main() -> int:
    started = time.time()
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    lines = []

    def log(message):
        print(message, flush=True)
        lines.append(message)

    digest = hashlib.sha256(ROSTER.read_bytes()).hexdigest()
    if digest != ROSTER_SHA256:
        log(f"roster digest mismatch: {digest}")
        return 2
    roster = []
    for line in ROSTER.read_text().splitlines():
        row = json.loads(line)
        if row.get("part") != "graph":
            continue
        if row["family"] in ("cubic", "small") or len(row["edges"]) <= 18:
            roster.append(("pilot:" + row["family"], row["vertices"], [tuple(e) for e in row["edges"]]))
    rng = random.Random(SEED)
    roster += held_out(rng)
    roster += named()
    log(f"[{time.time() - started:.0f}s] roster: {len(roster)} graphs")

    rows = []
    for index, (group, _, edges) in enumerate(roster):
        g = Graph(edges)
        charge = [1] + [0] * (g.n - 1)
        cvw = carving_width(g)
        lo, hi = (cvw + 1) // 2, cvw // 2 + 1
        start_bal = max(1, max((x + 1) // 2 for x in g.deg))
        bal = least_degree(g, "balanced", "R", charge, start_bal, cvw + 2)
        base = max(g.maxdeg, bal) if bal is not None else None
        rstd = least_degree(g, "standard", "R", charge, g.maxdeg, max(g.maxdeg, hi) + 1)
        cap = (base if base is not None else max(g.maxdeg, hi)) + 2
        sc = least_degree(g, "clause", "S", charge, g.maxdeg, cap)
        sb = least_degree(g, "standard", "S", charge, g.maxdeg, cap)
        row = {"group": group, "n": g.n, "m": g.m, "maxdegree": g.maxdeg, "edges": [list(e) for e in edges],
               "cvw": cvw, "PC_bal": bal, "PC_Rstd": rstd, "PC_SC": sc, "PC_SB": sb}
        row["P1"] = bal is not None and lo <= bal <= hi
        row["P2"] = bal is not None and rstd == max(g.maxdeg, bal)
        row["P3"] = base is not None and sc is not None and sb is not None and base <= sc <= base + 1 and \
            base <= sb <= base + 1
        if group in ("pilot:small",) or (group == "pilot:cubic" and g.n <= 10):
            last = [0] * (g.n - 1) + [1]
            three = [1, 1, 1] + [0] * (g.n - 3)
            even = [1, 1] + [0] * (g.n - 2)
            alt1 = least_degree(g, "balanced", "R", last, start_bal, cvw + 2)
            alt3 = least_degree(g, "balanced", "R", three, start_bal, cvw + 2)
            row["PC_bal_charge_last"], row["PC_bal_charge_three"] = alt1, alt3
            row["P4"] = alt1 == bal and alt3 == bal
            row["control_even_charge_refuted"] = least_degree(g, "balanced", "R", even, start_bal, hi + 1) is not None
        rows.append(row)
        if group.startswith("named") or index % 200 == 0:
            log(f"[{time.time() - started:.0f}s] {index:4d} {group:16s} n={g.n:2d} m={g.m:2d} D={g.maxdeg} "
                f"cvw={cvw} PC_bal={bal} PC_Rstd={rstd} PC_SC={sc} PC_SB={sb}")
        if time.time() - started > 5400:
            log("budget exhausted")
            break

    def holds(key):
        relevant = [r for r in rows if key in r]
        return all(r[key] for r in relevant), len(relevant), [r["group"] + ":" + str(r["edges"]) for r in relevant
                                                               if not r[key]][:5]

    even_rows = [r for r in rows if r["cvw"] % 2 == 0 and r["PC_bal"] is not None]
    ends = {"lower": sum(1 for r in even_rows if r["PC_bal"] == r["cvw"] // 2),
            "upper": sum(1 for r in even_rows if r["PC_bal"] == r["cvw"] // 2 + 1)}
    predictions = {}
    for key in ("P1", "P2", "P3", "P4"):
        ok, count, failures = holds(key)
        predictions[key] = {"holds": ok, "graphs": count, "first_failures": failures}
    predictions["P5"] = {"holds": ends["lower"] > 0 and ends["upper"] > 0, "even_width_graphs": len(even_rows),
                         "ends": ends}
    controls = {
        "even_charge_never_refuted": not any(r.get("control_even_charge_refuted") for r in rows),
        "exactness_fails_somewhere": ends["upper"] > 0,
    }
    by_group = {}
    for r in rows:
        key = r["group"].split(":")[0] if not r["group"].startswith("pilot") else r["group"]
        by_group[key] = by_group.get(key, 0) + 1
    histogram = {}
    for r in even_rows:
        k = f"cvw={r['cvw']}:PC_bal={r['PC_bal']}"
        histogram[k] = histogram.get(k, 0) + 1
    named_rows = {r["group"]: {k: r[k] for k in ("n", "m", "maxdegree", "cvw", "PC_bal", "PC_Rstd", "PC_SC", "PC_SB")}
                  for r in rows if r["group"].startswith("named")}
    result = {
        "experiment_id": "PC-DEGREE-20261020-001A-E001",
        "status": "complete" if len(rows) == len(roster) else "budget-exhausted",
        "graphs": len(rows),
        "groups": by_group,
        "predictions": predictions,
        "controls": controls,
        "even_width_histogram": dict(sorted(histogram.items())),
        "named": named_rows,
        "signal": all(p["holds"] for p in predictions.values()) and all(controls.values()),
        "wall_seconds": round(time.time() - started),
    }
    with open(ARTIFACT / "raw_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    (ARTIFACT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    log(json.dumps({k: result[k] for k in ("status", "graphs", "signal")}))
    log(json.dumps(predictions, sort_keys=True))
    log(json.dumps(controls, sort_keys=True))
    (ARTIFACT / "run_output.txt").write_text("\n".join(lines) + "\n")
    return 0 if result["signal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
