#!/usr/bin/env python3
"""Producer for GALLAI-KNOTS-20261020-001A-E001 (exploratory; see contract.json).

For q = 3 and 4 and every connected witness graph W on at most 6 vertices, up
to isomorphism, attach q - deg(v) pendant leaves to each vertex. Compute the
composite relation: the leaf colourings from whose lists W is colourable. Test
K1-K3 against the prediction "a knot exactly when W is a Gallai tree".

Writes artifacts/GALLAI-KNOTS-20261020-001A/<this folder>/:
result.json, raw_rows.jsonl and run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import json
import sys
import time
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "GALLAI-KNOTS-20261020-001A" / HERE.name
CAPS = {3: 9, 4: 7}
LOG = []


def log(msg):
    line = f"[{time.time() - START:.0f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ graphs up to isomorphism

def connected(k, edges):
    if k == 1:
        return True
    adj = {v: set() for v in range(k)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == k


def canonical(k, edges):
    deg = [0] * k
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    classes = {}
    for v in range(k):
        classes.setdefault(deg[v], []).append(v)
    order = [classes[d] for d in sorted(classes)]
    best = None
    for perms in product(*[list(permutations(c)) for c in order]):
        flat = [v for p in perms for v in p]
        pos = {v: i for i, v in enumerate(flat)}
        key = tuple(sorted(tuple(sorted((pos[a], pos[b]))) for a, b in edges))
        if best is None or key < best:
            best = key
    return best


def all_graphs(max_k):
    out = []
    for k in range(1, max_k + 1):
        pairs = list(combinations(range(k), 2))
        seen = set()
        for mask in range(1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
            if not connected(k, edges):
                continue
            key = canonical(k, edges)
            if key not in seen:
                seen.add(key)
                out.append((k, list(key)))
    return out


# ------------------------------------------------------------------ blocks and the Gallai test

def blocks(k, edges):
    """Biconnected components (as edge lists) by Tarjan's algorithm."""
    adj = {v: [] for v in range(k)}
    for i, (a, b) in enumerate(edges):
        adj[a].append((b, i))
        adj[b].append((a, i))
    disc, low, timer, stack, out = {}, {}, [0], [], []

    def dfs(u, parent_edge):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for w, i in adj[u]:
            if i == parent_edge:
                continue
            if w not in disc:
                stack.append(i)
                dfs(w, i)
                low[u] = min(low[u], low[w])
                if low[w] >= disc[u]:
                    comp = []
                    while True:
                        e = stack.pop()
                        comp.append(edges[e])
                        if e == i:
                            break
                    out.append(comp)
            elif disc[w] < disc[u]:
                stack.append(i)
                low[u] = min(low[u], disc[w])

    for v in range(k):
        if v not in disc:
            dfs(v, None)
    return out


def block_type(comp):
    verts = {v for e in comp for v in e}
    m, e = len(verts), len(comp)
    if e == m * (m - 1) // 2:
        return f"K{m}"
    deg = {}
    for a, b in comp:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    if e == m and all(d == 2 for d in deg.values()):
        return f"C{m}"
    return "other"


def gallai(k, edges, accept_even_cycles=False):
    types = [block_type(c) for c in blocks(k, edges)]
    ok = all(t.startswith("K") or (t.startswith("C") and (int(t[1:]) % 2 == 1 or accept_even_cycles)) for t in types)
    return ok, sorted(types)


# ------------------------------------------------------------------ the composite relation

def composite(k, edges, q, leaves_at):
    nbrs = [set() for _ in range(k)]
    for a, b in edges:
        nbrs[a].add(b)
        nbrs[b].add(a)

    @lru_cache(maxsize=None)
    def colourable(lists):
        order = sorted(range(k), key=lambda v: len(lists[v]))
        assign = {}

        def go(i):
            if i == k:
                return True
            v = order[i]
            for c in lists[v]:
                if all(assign.get(w) != c for w in nbrs[v]):
                    assign[v] = c
                    if go(i + 1):
                        return True
                    del assign[v]
            return False

        return go(0)

    owners = [v for v in range(k) for _ in range(leaves_at[v])]
    rel = set()
    for t in product(range(q), repeat=len(owners)):
        lists = [set(range(q)) for _ in range(k)]
        for v, c in zip(owners, t):
            lists[v].discard(c)
        if colourable(tuple(frozenset(s) for s in lists)):
            rel.add(t)
    return rel, owners


def knot(rel, n, q):
    full = q ** n
    if not rel or len(rel) == full:
        return False
    return all(len({r[:i] + r[i + 1:] for r in rel}) == q ** (n - 1) for i in range(n))


def excluded_type(rel, n, q):
    excl = [t for t in product(range(q), repeat=n) if t not in rel]
    if not excl:
        return "none", 0
    if all(len(set(t)) == 1 for t in excl) and len(excl) == q:
        return "all-equal", len(excl)
    if n == q and set(excl) == {t for t in product(range(q), repeat=n) if len(set(t)) == q}:
        return "all-colours", len(excl)
    return "other", len(excl)


def main():
    global START
    START = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    graphs = all_graphs(6)
    log(f"connected graphs on <= 6 vertices up to isomorphism: {len(graphs)}")
    rows = []
    for q in (3, 4):
        for k, edges in graphs:
            deg = [0] * k
            for a, b in edges:
                deg[a] += 1
                deg[b] += 1
            dmax = max(deg)
            if dmax <= q:
                regime = "within"
            elif dmax == q + 1:
                regime = "outside"
            else:
                continue
            leaves_at = [max(q - d, 0) for d in deg]
            n = sum(leaves_at)
            if n == 0 or n > CAPS[q]:
                rows.append({"q": q, "k": k, "edges": edges, "regime": regime, "leaves": n, "skipped": True})
                continue
            rel, owners = composite(k, edges, q, leaves_at)
            is_gallai, types = gallai(k, edges)
            wrong_gallai, _ = gallai(k, edges, accept_even_cycles=True)
            etype, nexcl = excluded_type(rel, n, q)
            rows.append({"q": q, "k": k, "edges": edges, "degrees": deg, "regime": regime, "leaves": n,
                         "allowed": len(rel), "excluded": nexcl, "excluded_type": etype, "knot": knot(rel, n, q),
                         "gallai": is_gallai, "blocks": types, "wrong_gallai": wrong_gallai, "skipped": False})
        log(f"q={q} done")
    done = [r for r in rows if not r["skipped"]]
    within = [r for r in done if r["regime"] == "within"]
    outside = [r for r in done if r["regime"] == "outside"]
    p1 = all(r["knot"] == r["gallai"] for r in within)
    p2 = all(r["excluded"] == 0 for r in within if not r["gallai"])

    def single_block(r, name):
        return r["blocks"] == [name]

    p3_cases = []
    for r in within:
        if r["k"] == 1:
            p3_cases.append(r["excluded_type"] == "all-colours")
        if single_block(r, f"K{r['q']}") or (r["q"] == 3 and len(r["blocks"]) == 1 and r["blocks"][0].startswith("C")
                                              and int(r["blocks"][0][1:]) % 2 == 1):
            p3_cases.append(r["excluded_type"] == "all-equal")
    p3 = bool(p3_cases) and all(p3_cases)
    p4 = any(r["knot"] for r in outside)
    c1 = all(not r["knot"] for r in within if r["blocks"] in (["C4"], ["C6"]))
    c2_disagree = sum(r["wrong_gallai"] != r["knot"] for r in within)
    summary = {}
    for q in (3, 4):
        w = [r for r in within if r["q"] == q]
        o = [r for r in outside if r["q"] == q]
        summary[str(q)] = {"within_cases": len(w), "within_knots": sum(r["knot"] for r in w),
                           "within_gallai": sum(r["gallai"] for r in w),
                           "outside_cases": len(o), "outside_knots": sum(r["knot"] for r in o),
                           "skipped": sum(1 for r in rows if r["q"] == q and r["skipped"])}
    outside_knots = [{"q": r["q"], "edges": r["edges"], "blocks": r["blocks"], "degrees": r["degrees"],
                      "excluded": r["excluded"]} for r in outside if r["knot"]][:12]
    result = {
        "experiment_id": "GALLAI-KNOTS-20261020-001A-E001", "evidence_stage": "exploratory",
        "graphs": len(graphs), "summary": summary, "outside_knot_examples": outside_knots,
        "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4},
        "controls": {"C1_even_cycles_no_knot": c1, "C2_wrong_gallai_disagreements": c2_disagree,
                     "C2_rejected": c2_disagree > 0},
        "signal": p1 and p2 and p3,
        "wall_seconds": round(time.time() - START, 1),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    log(f"summary {summary}")
    log(f"predictions {result['predictions']} controls {result['controls']} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
