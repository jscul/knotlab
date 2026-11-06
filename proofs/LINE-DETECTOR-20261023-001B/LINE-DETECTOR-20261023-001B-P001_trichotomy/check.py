#!/usr/bin/env python3
"""Check of LINE-DETECTOR-20261023-001B-P001 (standard library only).

- Lemma 1 (clauses): every two-literal tiling placement is the conjunction of the two-literal clauses it implies, and on every edge
  of the triangular lattice the clauses from its up and down triangles have the same type. Controls: no three-place tiling
  placement is such a conjunction; the local two-literal placements with clashing types have an odd contractible closed walk.
- Lemma 2 (parity): for every two-literal tiling placement on the 3 x 3, 3 x 4 and 4 x 4 tori and every twist, the value change of
  the implication arcs around each fundamental cycle of the clause graph equals, mod 2, the twist relative to a fitting twist
  evaluated on the cycle's class.
- Theorem 3 (trichotomy), on sampled configurations of all 24 two-literal tiling placements on 3 x 3 and 3 x 4 in every twist: the
  classes among (1,0), (0,1), (1,1), (1,-1), (1,2), (2,1), (1,-2), (2,-1) whose cylinders contradict (own two-literal solver on
  strips of 30 periods and cyclic covers of at most 24 sheets) are none, one, or every odd class; and the cause is as the proof
  says: every odd class exactly when a contradicting cluster has rank two, one class c exactly when every cluster lies along c.
- Proposition 4 (three-place counterexamples): for three explicit configurations on 3 x 3 (placements 54, 62 and 111) the
  pattern among eight classes is certified both ways with an own search (a strip of up to 36 periods with no assignment, or a
  cyclic cover with an assignment that is then verified clause by clause) and is selective.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSES = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]
UPO, DNO = ((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))
PAIRS = [(0, 1), (1, 2), (0, 2)]
UPDIR = {(0, 1): "h", (1, 2): "v", (0, 2): "d"}
DNDIR = {(0, 1): "v", (1, 2): "h", (0, 2): "d"}
SEED = 20261023
EXAMPLES = [  # (placement, L, M, twist, configuration, classes contradicting among the eight plus two longer ones)
    (54, 3, 3, (0, 1), 91, [(1, 0), (1, 1), (1, -1), (1, 2), (1, -2), (3, -1), (3, 1)]),
    (62, 3, 3, (0, 1), 27, [(1, 0), (1, 1), (1, -1), (1, 2), (1, -2), (3, -1), (3, 1)]),
    (111, 3, 3, (0, 0), 681, [(1, 0), (0, 1), (1, 2), (2, 1), (1, -2), (3, 2)]),
]


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def triangles(L, M):
    return [[(i + a, j + b) for a, b in offs] for j in range(M) for i in range(L) for offs in (UPO, DNO)]


def vid(p, L, M):
    return (p[1] % M) * L + p[0] % L


def deck(p, L, M):
    return (p[0] // L, p[1] // M)


def gauge(p, q, L, M):
    d = deck(p, L, M)
    return (q[0] * d[0] + q[1] * d[1]) & 1


# ------------------------------------------------------------------ Lemma 1

def implied_clauses(R):
    """(k1, k2, b1, b2): no pattern of R has places k1, k2 equal to b1, b2."""
    return [(k1, k2, b1, b2) for k1, k2 in PAIRS for b1 in (0, 1) for b2 in (0, 1)
            if not any((R >> p & 1) and ((p >> k1) & 1) == b1 and ((p >> k2) & 1) == b2 for p in range(8))]


def conjunction(cl):
    return sum(1 << p for p in range(8) if all(not (((p >> k1) & 1) == b1 and ((p >> k2) & 1) == b2) for k1, k2, b1, b2 in cl))


def types_consistent(cl):
    seen = {}
    for k1, k2, b1, b2 in cl:
        s = int(b1 == b2)
        for dirmap in (UPDIR, DNDIR):
            if seen.setdefault(dirmap[(k1, k2)], s) != s:
                return False
    return True


# ------------------------------------------------------------------ two-literal worlds

def fitting(R, L, M):
    U = R & comp(R)
    tris = triangles(L, M)
    V = L * M
    by_last = [[] for _ in range(V)]
    out = []
    for q in TWISTS:
        by_last = [[] for _ in range(V)]
        for P in tris:
            vs = [vid(p, L, M) for p in P]
            by_last[max(vs)].append((vs, [gauge(p, q, L, M) for p in P]))
        h = [0] * V

        def go(v):
            if v == V:
                return True
            for b in (0, 1):
                h[v] = b
                if all(U >> sum((h[vs[k]] ^ g[k]) << k for k in range(3)) & 1 for vs, g in by_last[v]) and go(v + 1):
                    return True
            return False

        if go(0):
            out.append(q)
    return out


def edge_clauses(R, L, M, q, x, layout=None):
    """Two-literal clauses of the world: (u, a, w, b, d) meaning not (h_u = a and h_w = b), with d the deck displacement u -> w.
    layout: optional list of (triangle index, corner nodes) of a cover or strip; corners are then nodes instead of vertices."""
    tris = triangles(L, M)
    out = []
    items = layout if layout is not None else [(f, [vid(p, L, M) for p in P]) for f, P in enumerate(tris)]
    for f, nodes in items:
        P = tris[f]
        rel = comp(R) if x >> f & 1 else R
        g = [gauge(p, q, L, M) for p in P]
        for k1, k2, b1, b2 in implied_clauses(rel):
            d = tuple(a - b for a, b in zip(deck(P[k2], L, M), deck(P[k1], L, M)))
            out.append((nodes[k1], b1 ^ g[k1], nodes[k2], b2 ^ g[k2], d))
    return out


def scc(adj):
    n = len(adj)
    index, low, comp_id, onstack, stack = [-1] * n, [0] * n, [-1] * n, [False] * n, []
    counter = ncomp = 0
    for s in range(n):
        if index[s] != -1:
            continue
        work = [(s, 0)]
        index[s] = low[s] = counter
        counter += 1
        stack.append(s)
        onstack[s] = True
        while work:
            v, i = work[-1]
            if i < len(adj[v]):
                work[-1] = (v, i + 1)
                w = adj[v][i]
                if index[w] == -1:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    onstack[w] = True
                    work.append((w, 0))
                elif onstack[w]:
                    low[v] = min(low[v], index[w])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    while True:
                        w = stack.pop()
                        onstack[w] = False
                        comp_id[w] = ncomp
                        if w == v:
                            break
                    ncomp += 1
    return comp_id


def implication(n, clauses):
    adj = [[] for _ in range(2 * n)]
    for u, a, w, b, _d in clauses:
        adj[2 * u + a].append(2 * w + 1 - b)
        adj[2 * w + b].append(2 * u + 1 - a)
    return adj


def two_lit_unsat(n, clauses):
    cid = scc(implication(n, clauses))
    return any(cid[2 * v] == cid[2 * v + 1] for v in range(n))


def complement_basis(c):
    for u0 in range(-4, 5):
        for u1 in range(-4, 5):
            if c[0] * u1 - c[1] * u0 == 1:
                return (u0, u1)
    raise ValueError(c)


def layout_of(L, M, c, sheets, cyclic):
    tris = triangles(L, M)
    nodes, out = {}, []
    for f, P in enumerate(tris):
        corners = []
        for p in P:
            d = deck(p, L, M)
            corners.append((vid(p, L, M), c[0] * d[1] - c[1] * d[0]))
        for m in range(sheets):
            out.append((f, [nodes.setdefault((v, (t + m) % sheets if cyclic else t + m), len(nodes)) for v, t in corners]))
    return len(nodes), out


def cylinder_two_lit(R, L, M, q, x, c):
    n, lay = layout_of(L, M, c, 30, False)
    if two_lit_unsat(n, edge_clauses(R, L, M, q, x, lay)):
        return True
    for k in range(1, 25):
        n, lay = layout_of(L, M, c, k, True)
        if not two_lit_unsat(n, edge_clauses(R, L, M, q, x, lay)):
            return False
    return None


def clusters(R, L, M, q, x):
    """(torus contradicts, [(rank of the cluster's period lattice, cluster's direction or None, contains a contradiction)])."""
    V = L * M
    cl = edge_clauses(R, L, M, q, x)
    cid = scc(implication(V, cl))
    bad = {cid[2 * v] for v in range(V) if cid[2 * v] == cid[2 * v + 1]}
    nbr = {}
    for u, a, w, b, d in cl:
        if cid[2 * u + a] == cid[2 * w + 1 - b]:
            nbr.setdefault(u, []).append((w, d))
            nbr.setdefault(w, []).append((u, (-d[0], -d[1])))
    seen, out = {}, []
    for s0 in nbr:
        if s0 in seen:
            continue
        seen[s0] = (0, 0)
        stack, members, classes = [s0], [s0], []
        while stack:
            u = stack.pop()
            for w, d in nbr[u]:
                pw = (seen[u][0] + d[0], seen[u][1] + d[1])
                if w not in seen:
                    seen[w] = pw
                    stack.append(w)
                    members.append(w)
                elif pw != seen[w]:
                    classes.append((pw[0] - seen[w][0], pw[1] - seen[w][1]))
        nz = [g for g in classes if g != (0, 0)]
        rank = 0 if not nz else (1 if all(nz[0][0] * g[1] - nz[0][1] * g[0] == 0 for g in nz) else 2)
        out.append((rank, nz[0] if rank == 1 else None, any(cid[2 * v] in bad for v in members)))
    return bool(bad), out


def parallel(a, b):
    return a[0] * b[1] - a[1] * b[0] == 0


def parity_checks(R, L, M):
    """Lemma 2: value changes around fundamental cycles of the clause graph equal the relative twist on their classes."""
    fit = fitting(R, L, M)
    good = total = 0
    for q in TWISTS:
        cl = edge_clauses(R, L, M, q, 0)
        # value change along clause (u, a, w, b): arc (h_u = a) -> (h_w = 1 - b) changes the value by a + 1 + b
        pot, par = {}, {}
        adj = {}
        for u, a, w, b, d in cl:
            ch = (a + 1 + b) & 1
            adj.setdefault(u, []).append((w, ch, d))
            adj.setdefault(w, []).append((u, ch, (-d[0], -d[1])))
        for s0 in adj:
            if s0 in pot:
                continue
            pot[s0] = (0, (0, 0))
            stack = [s0]
            while stack:
                u = stack.pop()
                for w, ch, d in adj[u]:
                    pw = (pot[u][0] ^ ch, (pot[u][1][0] + d[0], pot[u][1][1] + d[1]))
                    if w not in pot:
                        pot[w] = pw
                        stack.append(w)
                    else:
                        g = (pw[1][0] - pot[w][1][0], pw[1][1] - pot[w][1][1])
                        change = pw[0] ^ pot[w][0]
                        total += 1
                        good += all(change == (((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1) for f in fit)
    return good, total


def trichotomy_checks(rng, placements):
    out = {"configurations": 0, "contradicting": 0, "patterns follow the trichotomy": 0, "cause matches": 0,
           "all odd classes (rank two)": 0, "one class": 0, "none of the eight": 0, "undetermined": 0}
    for R in placements:
        for L, M in ((3, 3), (3, 4)):
            fit = fitting(R, L, M)
            for q in TWISTS:
                odd = [g for g in CLASSES if fit and all(((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1 for f in fit)]
                for _ in range(3):
                    x = rng.randrange(1 << (2 * L * M))
                    out["configurations"] += 1
                    contradicts, cls = clusters(R, L, M, q, x)
                    if not contradicts:
                        continue
                    out["contradicting"] += 1
                    st = [cylinder_two_lit(R, L, M, q, x, c) for c in CLASSES]
                    if None in st:
                        out["undetermined"] += 1
                        continue
                    S = [c for c, s in zip(CLASSES, st) if s]
                    follows = (not S) or len(S) == 1 or set(S) == set(odd)
                    out["patterns follow the trichotomy"] += follows
                    rank2 = any(r == 2 and b for r, _d, b in cls)
                    dirs = {d for r, d, b in cls if r == 1}
                    if set(S) == set(odd) and len(odd) > 1:
                        out["all odd classes (rank two)"] += 1
                        out["cause matches"] += rank2
                    elif len(S) == 1:
                        out["one class"] += 1
                        out["cause matches"] += (not rank2) and all(parallel(d, S[0]) for d in dirs)
                    else:
                        out["none of the eight"] += 1
                        out["cause matches"] += (not rank2) and all(not any(parallel(d, c) for c in CLASSES) for d in dirs if d)
    return out


# ------------------------------------------------------------------ three-place certificates

def cnf(R, L, M, q, x, c, sheets, cyclic):
    n, lay = layout_of(L, M, c, sheets, cyclic)
    tris = triangles(L, M)
    out = []
    for f, nodes in lay:
        P = tris[f]
        rel = comp(R) if x >> f & 1 else R
        g = [gauge(p, q, L, M) for p in P]
        for pat in range(8):
            if not rel >> pat & 1:
                out.append([(-(nodes[k] + 1) if ((pat >> k) & 1) ^ g[k] else nodes[k] + 1) for k in range(3)])
    return n, out


def dpll(n, clauses):
    """An assignment (list of 0/1) or None, by depth-first search with unit propagation."""
    occ = [[] for _ in range(2 * n + 2)]
    for i, cl in enumerate(clauses):
        for lit in cl:
            occ[lit if lit > 0 else n - lit].append(i)
    val = [-1] * (n + 1)

    def lit_val(lit):
        v = val[abs(lit)]
        return -1 if v < 0 else (v if lit > 0 else 1 - v)

    def propagate(trail, start):
        i = start
        while i < len(trail):
            var = trail[i]
            neg = -var if val[var] == 1 else var          # the literal that just became false
            for ci in occ[neg if neg > 0 else n - neg]:
                free, sat = [], False
                for lit in clauses[ci]:
                    lv = lit_val(lit)
                    if lv == 1:
                        sat = True
                        break
                    if lv < 0:
                        free.append(lit)
                if sat:
                    continue
                if not free:
                    return False
                if len(free) == 1:
                    lit = free[0]
                    val[abs(lit)] = 1 if lit > 0 else 0
                    trail.append(abs(lit))
            i += 1
        return True

    def solve(trail):
        start = len(trail)
        var = next((v for v in range(1, n + 1) if val[v] < 0), None)
        if var is None:
            return True
        for b in (0, 1):
            val[var] = b
            trail.append(var)
            if propagate(trail, len(trail) - 1) and solve(trail):
                return True
            while len(trail) > start:
                val[trail.pop()] = -1
        return False

    if not solve([]):
        return None
    return [val[v] for v in range(1, n + 1)]


def verify(clauses, assignment):
    return all(any((assignment[abs(l) - 1] == 1) == (l > 0) for l in cl) for cl in clauses)


def certify(R, L, M, q, x, c):
    """True: a strip of 12, 24 or 36 periods has no assignment; False: a cyclic cover of at most 12 sheets has a verified one."""
    for k in range(1, 13):
        n, cl = cnf(R, L, M, q, x, c, k, True)
        a = dpll(n, cl)
        if a is not None:
            return False if verify(cl, a) else None
    for periods in (12, 24, 36):
        n, cl = cnf(R, L, M, q, x, c, periods, False)
        if dpll(n, cl) is None:
            return True
    return None


def main() -> int:
    rng = random.Random(SEED)
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    pair_tiling = [r["R"] for r in census if r["kind"] == "pair" and r["class"] == "TILING"]
    three_tiling = [r["R"] for r in census if r["kind"] == "three" and r["class"] == "TILING"]
    pair_local = [r["R"] for r in census if r["kind"] == "pair" and r["class"] == "LOCAL"]
    result = {"schema_version": 3}
    manifest = json.loads((HERE / "manifest.json").read_text())
    result.update({"artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
                   "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
                   "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
                   "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]})
    checks, controls = {}, {}
    # Lemma 1
    checks["Lemma 1"] = {
        "two-literal tiling placements": len(pair_tiling),
        "equal to the conjunction of their two-literal clauses": sum(conjunction(implied_clauses(R)) == R for R in pair_tiling),
        "edge clauses of one type": sum(types_consistent(implied_clauses(R)) for R in pair_tiling)}
    controls["three-place tiling placements that are conjunctions of two-literal clauses (must be 0)"] = sum(
        conjunction(implied_clauses(R)) == R for R in three_tiling)
    # control: local two-literal placements with clashing edge types have an odd contractible closed walk (the parity lemma needs the tiling)
    clash = [R for R in pair_local if not types_consistent(implied_clauses(R))]
    odd_contractible = 0
    for R in clash:
        good, total = parity_checks_any(R)
        odd_contractible += good
    controls["local two-literal placements with clashing edge types"] = len(clash)
    controls["of them with an odd contractible closed walk"] = odd_contractible
    # Lemma 2
    lemma2 = {"placement-torus pairs": 0, "fundamental cycles": 0, "value change equals the relative twist": 0}
    for R in pair_tiling:
        for L, M in ((3, 3), (3, 4), (4, 4)):
            good, total = parity_checks(R, L, M)
            lemma2["placement-torus pairs"] += 1
            lemma2["fundamental cycles"] += total
            lemma2["value change equals the relative twist"] += good
    checks["Lemma 2"] = lemma2
    print("lemmas checked", flush=True)
    # Theorem 3
    checks["Theorem 3 on sampled configurations"] = trichotomy_checks(rng, pair_tiling)
    print("trichotomy checked", flush=True)
    # Proposition 4
    prop = []
    for R, L, M, q, x, classes in EXAMPLES:
        fit = fitting(R, L, M)
        st = {c: certify(R, L, M, q, x, c) for c in classes}
        odd = [c for c in classes if all(((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1 for f in fit)]
        S = [c for c in classes if st[c]]
        prop.append({"placement": R, "torus": f"{L}x{M}", "twist": f"{q[0]}{q[1]}", "configuration": x,
                     "contradicts along": [list(c) for c in S], "has assignments along (odd)": [list(c) for c in odd if st[c] is False],
                     "undetermined": [list(c) for c in classes if st[c] is None],
                     "selective": len(S) >= 2 and any(st[c] is False for c in odd)})
    checks["Proposition 4"] = prop
    t3 = checks["Theorem 3 on sampled configurations"]
    ok = (checks["Lemma 1"]["equal to the conjunction of their two-literal clauses"] == checks["Lemma 1"]["edge clauses of one type"] == len(pair_tiling) == 24
          and lemma2["value change equals the relative twist"] == lemma2["fundamental cycles"] > 0
          and t3["undetermined"] == 0 and t3["patterns follow the trichotomy"] == t3["contradicting"] > 0
          and t3["cause matches"] == t3["contradicting"] and t3["all odd classes (rank two)"] > 0 and t3["one class"] > 0
          and all(p["selective"] and not p["undetermined"] for p in prop)
          and controls["three-place tiling placements that are conjunctions of two-literal clauses (must be 0)"] == 0
          and controls["of them with an odd contractible closed walk"] == controls["local two-literal placements with clashing edge types"] > 0)
    result["checks"], result["controls"] = checks, controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": checks, "controls": controls}, indent=1))
    return 0 if ok else 1


def parity_checks_any(R):
    """1 if some contractible closed walk of the clause graph of R on the 3 x 3 torus has odd value change, else 0."""
    for q in TWISTS:
        cl = edge_clauses(R, 3, 3, q, 0)
        adj = {}
        for u, a, w, b, d in cl:
            ch = (a + 1 + b) & 1
            adj.setdefault(u, []).append((w, ch, d))
            adj.setdefault(w, []).append((u, ch, (-d[0], -d[1])))
        pot = {}
        for s0 in adj:
            if s0 in pot:
                continue
            pot[s0] = (0, (0, 0))
            stack = [s0]
            while stack:
                u = stack.pop()
                for w, ch, d in adj[u]:
                    pw = (pot[u][0] ^ ch, (pot[u][1][0] + d[0], pot[u][1][1] + d[1]))
                    if w not in pot:
                        pot[w] = pw
                        stack.append(w)
                    elif pw[1] == pot[w][1] and pw[0] != pot[w][0]:
                        return 1, 1
    return 0, 1


if __name__ == "__main__":
    raise SystemExit(main())
