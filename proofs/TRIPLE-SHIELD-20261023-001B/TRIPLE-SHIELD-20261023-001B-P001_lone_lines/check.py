#!/usr/bin/env python3
"""Check of TRIPLE-SHIELD-20261023-001B-P001 (standard library only).

- Theorem 1 (cylinders and fitting twists): for every tiling placement on the 3 x 3, 3 x 4 and 4 x 3 tori and every fitting
  twist q_f (found by backtracking for a doubly allowed assignment h_f), and for every class c and twist q with (q - q_f)(c) = 0,
  the gauge G on a strip of 12 periods of the cylinder along c is solved explicitly (union-find with parity) and h_f + G is
  doubly allowed on every strip triangle in twist q. Control: when (q - q_f)(c) = 1 no such gauge exists on a strip closed
  around c.
- Theorem 5 and Lemma 3 (lone lines are line events in orientation worlds): for placements 63, 119, 187 and 207 on the four tori, own
  implication graphs give the strong components, the cyclic edges, the clusters and their period lattices, hence the line event
  L(c) (every cluster's periods in Zc, some nonzero). The cylinder events are certified by an own two-literal solver: a cylinder
  contradicts when a strip of 24 periods does, and does not when a cyclic cover of at most 16 sheets has an assignment. On random
  configurations and on configurations selected by the cluster computation (line events and rank-two contradictions), lone_c
  equals L(c) for each class, and every rank-two contradiction makes exactly two of the three cylinders contradict.
- Exhaustive counts on 3 x 3: for placements 63 and 207, the number of configurations in L(c) for each twist and class equals the
  lone-line count recorded in rows.jsonl of TRIPLE-SHIELD-20261023-001A-E001.
- Controls (each must be rejected): the cylinder event without the lone condition differs from L(c) on some configuration;
  a twist odd on c admits no gauge (Theorem 1's hypothesis); a rank-one contradiction along c leaves a cylinder along an odd
  class without a contradiction (Lemma 3 needs rank two).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
ROWS = ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs/rows.jsonl"
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSES = [(1, 0), (0, 1), (1, 1)]
UPO = ((0, 0), (1, 0), (1, 1))
DNO = ((0, 0), (0, 1), (1, 1))
ORIENTATION = (63, 119, 187, 207)
STRIP, COVERS = 24, 16
SEED = 20261023


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


def sheet(d, c):
    """t in d = s c + t u for the basis {c, u} of the deck lattice."""
    u = {(1, 0): (0, 1), (0, 1): (1, 0), (1, 1): (0, 1)}[c]
    det = c[0] * u[1] - c[1] * u[0]
    return (c[0] * d[1] - c[1] * d[0]) // det


def lifted(L, M, c, sheets, cyclic):
    """Lifted triangles (base index, corner vertices) of the cover along c (cyclic) or of a strip of the cylinder along c."""
    out = []
    for f, P in enumerate(triangles(L, M)):
        corners = [(vid(p, L, M), sheet(deck(p, L, M), c)) for p in P]
        for m in range(sheets):
            out.append((f, [(v, (t + m) % sheets if cyclic else t + m) for v, t in corners]))
    return out


# ------------------------------------------------------------------ Theorem 1

def doubly_allowed(R, L, M, q):
    """A hidden assignment whose gauged pattern lies in R and in its complement on every triangle, by backtracking."""
    U = R & comp(R)
    tris = triangles(L, M)
    V = L * M
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

    return list(h) if go(0) else None


def solve_gauge(L, M, c, q, qf, sheets):
    """G on the strip with G(corner k) + G(corner 0) = t_q - t_qf at every corner, closed around c; None if inconsistent."""
    parent, par = {}, {}

    def find(a):
        p = 0
        while parent[a] != a:
            p ^= par[a]
            a = parent[a]
        return a, p

    tris = triangles(L, M)
    for f, corners in lifted(L, M, c, sheets, False):
        P = tris[f]
        for node in corners:
            if node not in parent:
                parent[node], par[node] = node, 0
        for k in (1, 2):
            d = gauge(P[k], q, L, M) ^ gauge(P[k], qf, L, M) ^ gauge(P[0], q, L, M) ^ gauge(P[0], qf, L, M)
            (ra, pa), (rb, pb) = find(corners[0]), find(corners[k])
            if ra == rb:
                if pa ^ pb != d:
                    return None
            else:
                parent[rb], par[rb] = ra, pa ^ pb ^ d
    # close the strip around c: a vertex at sheet t is the same vertex of the cylinder at every lift along c, so the strip
    # already contains the loops around c; inconsistency there is the obstruction
    return {node: find(node)[1] for node in parent}


def theorem1_checks():
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    tiling = [r["R"] for r in census if r["class"] == "TILING"]
    out = Counter()
    for L, M in ((3, 3), (3, 4), (4, 3)):
        tris = triangles(L, M)
        for R in tiling:
            U = R & comp(R)
            for qf in TWISTS:
                hf = doubly_allowed(R, L, M, qf)
                if hf is None:
                    continue
                out["fitting (placement, torus, twist)"] += 1
                for c in CLASSES:
                    for q in TWISTS:
                        odd = (((q[0] ^ qf[0]) * c[0] + (q[1] ^ qf[1]) * c[1]) & 1)
                        G = solve_gauge(L, M, c, q, qf, 12)
                        if odd:
                            out["odd twists: no gauge exists (control)"] += G is None
                            out["odd twists tested"] += 1
                            continue
                        out["even twists tested"] += 1
                        if G is None:
                            continue
                        ok = True
                        for f, corners in lifted(L, M, c, 12, False):
                            P = tris[f]
                            pat = sum((hf[corners[k][0]] ^ G[corners[k]] ^ gauge(P[k], q, L, M)) << k for k in range(3))
                            ok &= bool(U >> pat & 1)
                        out["even twists: h_f + G doubly allowed on the whole strip"] += ok
    return dict(out)


# ------------------------------------------------------------------ two-literal worlds

def clause_of(rel, g):
    """The single two-literal clause equivalent to a gauged relation of an orientation placement: ((k1, b1), (k2, b2)) meaning
    h at corner k1 differs from b1, or h at corner k2 differs from b2."""
    bad = [p for p in range(8) if not rel >> p & 1]
    dep = [k for k in range(3) if (bad[0] >> k & 1) == (bad[1] >> k & 1)]
    assert len(bad) == 2 and len(dep) == 2
    return tuple((k, ((bad[0] >> k) & 1) ^ g[k]) for k in dep)


def implication(nverts, clauses):
    """Arcs between literals 2v + b (meaning h_v = b): clause (u != a or w != c) gives (u = a) -> (w = 1 - c) and
    (w = c) -> (u = 1 - a)."""
    adj = [[] for _ in range(2 * nverts)]
    for (u, a), (w, cc) in clauses:
        adj[2 * u + a].append(2 * w + (1 - cc))
        adj[2 * w + cc].append(2 * u + (1 - a))
    return adj


def scc(adj):
    """Strongly connected component ids (iterative Tarjan)."""
    n = len(adj)
    index, low, comp_id, onstack, stack = [-1] * n, [0] * n, [-1] * n, [False] * n, []
    counter, ncomp = 0, 0
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


def unsat(nverts, clauses):
    cid = scc(implication(nverts, clauses))
    return any(cid[2 * v] == cid[2 * v + 1] for v in range(nverts))


def world_clauses(R, L, M, q, x, layout, index):
    """Clauses of the lifted world: layout from lifted() or the torus; index maps lifted vertices to 0..n-1."""
    tris = triangles(L, M)
    out = []
    for f, corners in layout:
        P = tris[f]
        rel = comp(R) if x >> f & 1 else R
        (k1, b1), (k2, b2) = clause_of(rel, [gauge(p, q, L, M) for p in P])
        out.append(((index[corners[k1]], b1), (index[corners[k2]], b2)))
    return out


def cylinder_status(R, L, M, q, x, c):
    """True if the cylinder along c contradicts, False if not, None if neither certificate is found."""
    layout = lifted(L, M, c, STRIP, False)
    index = {}
    for _f, corners in layout:
        for node in corners:
            index.setdefault(node, len(index))
    if unsat(len(index), world_clauses(R, L, M, q, x, layout, index)):
        return True
    for k in range(1, COVERS + 1):
        layout = lifted(L, M, c, k, True)
        index = {}
        for _f, corners in layout:
            for node in corners:
                index.setdefault(node, len(index))
        if not unsat(len(index), world_clauses(R, L, M, q, x, layout, index)):
            return False
    return None


def line_structure(R, L, M, q, x):
    """(torus contradicts, list of clusters as (period classes, contains a contradiction))."""
    tris = triangles(L, M)
    V = L * M
    clauses, edges = [], []
    for f, P in enumerate(tris):
        rel = comp(R) if x >> f & 1 else R
        (k1, b1), (k2, b2) = clause_of(rel, [gauge(p, q, L, M) for p in P])
        u, w = vid(P[k1], L, M), vid(P[k2], L, M)
        d = tuple(a - b for a, b in zip(deck(P[k2], L, M), deck(P[k1], L, M)))
        clauses.append(((u, b1), (w, b2)))
        edges.append((u, w, d))
    adj = implication(V, clauses)
    cid = scc(adj)
    bad_comp = {cid[2 * v] for v in range(V) if cid[2 * v] == cid[2 * v + 1]}
    cyclic = [e for e, ((u, a), (w, cc)) in enumerate(clauses) if cid[2 * u + a] == cid[2 * w + (1 - cc)]]
    # clusters of cyclic edges with potentials
    nbr = {}
    for e in cyclic:
        u, w, d = edges[e]
        nbr.setdefault(u, []).append((w, d))
        nbr.setdefault(w, []).append((u, (-d[0], -d[1])))
    seen, clusters = {}, []
    for s in nbr:
        if s in seen:
            continue
        seen[s] = (0, 0)
        stack, members, classes = [s], [s], []
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
        contradicts = any(cid[2 * v] in bad_comp for v in members)
        clusters.append((classes, contradicts))
    return bool(bad_comp), clusters


def rank_of(classes):
    nz = [g for g in classes if g != (0, 0)]
    if not nz:
        return 0
    g0 = nz[0]
    return 1 if all(g0[0] * g[1] - g0[1] * g[0] == 0 for g in nz) else 2


def line_event(clusters, c):
    """L(c) of the shielding theorem: some cluster contradicts, every cluster's periods lie in Zc and some period is nonzero.
    (A contradiction needs a period of odd twist, so this is empty when the twist is even on c, where L(c) is not defined.)"""
    return (any(b for _cl, b in clusters)
            and all(all(g[0] * c[1] - g[1] * c[0] == 0 for g in cl) for cl, _b in clusters)
            and any(any(g != (0, 0) for g in cl) for cl, _b in clusters))


def theorem2_checks(rng):
    out = Counter()
    controls = Counter()
    for R in ORIENTATION:
        for L, M in ((3, 3), (3, 4), (4, 3), (4, 4)):
            for q in TWISTS:
                total = 1 << (2 * L * M)
                picks = [rng.randrange(total) for _ in range(12)]
                wanted = {"line": 4, "rank two": 3}
                for _ in range(3000):
                    if not any(wanted.values()):
                        break
                    x = rng.randrange(total)
                    _u, clusters = line_structure(R, L, M, q, x)
                    if wanted["line"] and any(line_event(clusters, c) for c in CLASSES):
                        wanted["line"] -= 1
                        picks.append(x)
                    elif wanted["rank two"] and any(b and rank_of(cl) == 2 for cl, b in clusters):
                        wanted["rank two"] -= 1
                        picks.append(x)
                for x in picks:
                    contradicts, clusters = line_structure(R, L, M, q, x)
                    out["configurations"] += 1
                    if not contradicts:
                        out["no contradiction (torus has an assignment, so every cylinder has one)"] += 1
                        continue
                    status = [cylinder_status(R, L, M, q, x, c) for c in CLASSES]
                    if None in status:
                        out["undetermined"] += 1
                        continue
                    out["contradicting configurations certified"] += 1
                    for i, c in enumerate(CLASSES):
                        lone = status[i] and sum(status) == 1
                        out["lone_c equals L(c)"] += lone == line_event(clusters, c)
                        out["class comparisons"] += 1
                        if status[i] != line_event(clusters, c):
                            controls["cylinder event without the lone condition differs from L(c)"] += 1
                    r2 = any(b and rank_of(cl) == 2 for cl, b in clusters)
                    if r2:
                        out["rank-two contradictions"] += 1
                        out["rank two: exactly two cylinders contradict"] += sum(status) == 2
                    elif sum(status) == 1:
                        controls["rank-one contradiction leaves a cylinder along an odd class free"] += 1
    return dict(out), dict(controls)


def exhaustive_3x3():
    rows = [json.loads(l) for l in ROWS.read_text().splitlines() if l.strip()]
    rec = {(r["L"], r["M"], r["R"]): r for r in rows}
    out = Counter()
    for R in (63, 207):
        for q in TWISTS:
            n = Counter()
            for x in range(1 << 18):
                contradicts, clusters = line_structure(R, 3, 3, q, x)
                if contradicts:
                    for i, c in enumerate(CLASSES):
                        n[i] += line_event(clusters, c)
            recorded = rec[(3, 3, R)]["counts"][f"{q[0]}{q[1]}"]["lone"]
            out["(placement, twist) pairs"] += 1
            out["L(c) counts equal the recorded lone counts"] += [n[0], n[1], n[2]] == recorded
    return dict(out)


def main() -> int:
    rng = random.Random(SEED)
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"], "checks": {}}
    t1 = theorem1_checks()
    t2, controls = theorem2_checks(rng)
    ex = exhaustive_3x3()
    result["checks"]["Theorem 1 on the 3 x 3, 3 x 4 and 4 x 3 tori"] = t1
    result["checks"]["Theorem 5 and Lemma 3 on sampled configurations of the orientation worlds"] = t2
    result["checks"]["Exhaustive line-event counts on 3 x 3 against the recorded lone counts"] = ex
    controls["odd twist: no gauge (Theorem 1's hypothesis is needed)"] = t1.get("odd twists: no gauge exists (control)", 0)
    result["controls"] = controls
    ok = (t1["even twists: h_f + G doubly allowed on the whole strip"] == t1["even twists tested"] > 0
          and t1["odd twists: no gauge exists (control)"] == t1["odd twists tested"] > 0
          and t2.get("undetermined", 0) == 0 and t2["lone_c equals L(c)"] == t2["class comparisons"] > 0
          and t2["rank two: exactly two cylinders contradict"] == t2["rank-two contradictions"] > 0
          and t2["no contradiction (torus has an assignment, so every cylinder has one)"]
          == t2["configurations"] - t2["contradicting configurations certified"]
          and ex["L(c) counts equal the recorded lone counts"] == ex["(placement, twist) pairs"] == 8
          and all(v > 0 for v in controls.values()) and len(controls) == 3)
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({k: result[k] for k in ("status", "checks", "controls")}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
