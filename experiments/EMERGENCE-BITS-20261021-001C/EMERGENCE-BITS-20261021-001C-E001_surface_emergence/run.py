#!/usr/bin/env python3
"""Producer for EMERGENCE-BITS-20261021-001C-E001: emergence of not-all-equal worlds on surfaces at scale.

Confirmatory Monte Carlo over the roster frozen in contract.json. A not-all-equal relation NAE(h_u, x_e, h_v) sits on
every edge of a torus grid; the joints h are hidden and the spokes x are fair bits. For each torus the producer counts
the samples whose spokes extend to the joints and reports E = -log2 of the consistent fraction. Every square-torus
sample is judged twice: by limited backtracking on the not-all-equal tables, and by strongly connected components on
the recoloured form built directly from the spokes. Self-contained; imports nothing from the proofs.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import math
import random
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "EMERGENCE-BITS-20261021-001C" / HERE.name

sys.setrecursionlimit(10000)

NAE_TABLES = [((0, 1), (1, 1)), ((1, 1), (1, 0))]     # spoke 0 forbids (0,0); spoke 1 forbids (1,1)
PARITY_TABLES = [((1, 0), (0, 1)), ((0, 1), (1, 0))]


# ------------------------------------------------------------------ surfaces

def square_torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    edges = [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)]
    edges += [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]
    seam = [(i == a - 1) and a % 2 == 1 for i in range(a) for j in range(b)]
    seam += [(j == b - 1) and b % 2 == 1 for i in range(a) for j in range(b)]
    colour = [((v // b) + (v % b)) % 2 for v in range(a * b)]
    return a * b, edges, seam, colour


def triangular_torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    edges = []
    for i in range(a):
        for j in range(b):
            for di, dj in ((1, 0), (0, 1), (1, 1)):
                edges.append((idx(i, j), idx(i + di, j + dj)))
    seam = [False] * len(edges)          # every triangle is an odd face; no cut makes it bipartite
    return a * b, edges, seam, None


def brick_torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    edges, seam = [], []
    for i in range(a):
        for j in range(b):
            edges.append((idx(i, j), idx(i, j + 1)))
            seam.append(j == b - 1 and b % 2 == 1)
            if (i + j) % 2 == 0:
                edges.append((idx(i, j), idx(i + 1, j)))
                seam.append(i == a - 1 and a % 2 == 1)
    return a * b, edges, seam, None


def bipartite(nv, edges):
    adj = [[] for _ in range(nv)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    col = [None] * nv
    for s in range(nv):
        if col[s] is not None:
            continue
        col[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if col[w] is None:
                    col[w] = 1 - col[u]
                    stack.append(w)
                elif col[w] == col[u]:
                    return False
    return True


# ------------------------------------------------------------------ solver 1: limited backtracking on the tables

def consistent_tables(nv, edges, mats):
    adj = [[] for _ in range(nv)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k, 0))
        adj[v].append((u, k, 1))
    val = [None] * nv

    def propagate(start, a, val, changed):
        val[start] = a
        changed.append(start)
        stack = [start]
        while stack:
            u = stack.pop()
            for w, k, side in adj[u]:
                M = mats[k]
                if side == 0:
                    allowed = [c for c in (0, 1) if M[val[u]][c]]
                else:
                    allowed = [c for c in (0, 1) if M[c][val[u]]]
                if val[w] is None:
                    if not allowed:
                        return False
                    if len(allowed) == 1:
                        val[w] = allowed[0]
                        changed.append(w)
                        stack.append(w)
                elif val[w] not in allowed:
                    return False
        return True

    for v in range(nv):
        if val[v] is not None:
            continue
        ok = False
        for a in (0, 1):
            changed = []
            if propagate(v, a, val, changed):
                ok = True
                break
            for w in changed:
                val[w] = None
        if not ok:
            return False
    return all(mats[k][val[u]][val[v]] for k, (u, v) in enumerate(edges))


# ------------------------------------------------------------------ solver 2: components of the implication graph

def consistent_recoloured(nv, edges, seam, colour, x):
    """Build the recoloured two-literal instance directly from the spokes and decide it by strongly connected
    components. Literal 2v means tau_v = 1, literal 2v+1 means tau_v = 0."""
    n = 2 * nv
    succ = [[] for _ in range(n)]
    def clause(p, q):                     # p or q
        succ[p ^ 1].append(q)
        succ[q ^ 1].append(p)
    for (u, v), s, xe in zip(edges, seam, x):
        c = xe ^ colour[u]
        if not s:                         # colours differ: forbid tau_u = c, tau_v = 1 - c
            lit_u_not_c = 2 * u + (1 if c == 1 else 0)
            lit_v_c = 2 * v + (0 if c == 1 else 1)
            clause(lit_u_not_c, lit_v_c)
        else:                             # colours equal: forbid tau_u = tau_v = c
            lit_u = 2 * u + (1 if c == 1 else 0)
            lit_v = 2 * v + (1 if c == 1 else 0)
            clause(lit_u, lit_v)
    index = [-1] * n
    low = [0] * n
    on = [False] * n
    comp = [-1] * n
    stack, counter, ncomp = [], 0, 0
    for root in range(n):
        if index[root] != -1:
            continue
        work = [(root, 0)]
        while work:
            node, i = work.pop()
            if i == 0:
                index[node] = low[node] = counter
                counter += 1
                stack.append(node)
                on[node] = True
            recurse = False
            for j in range(i, len(succ[node])):
                w = succ[node][j]
                if index[w] == -1:
                    work.append((node, j + 1))
                    work.append((w, 0))
                    recurse = True
                    break
                elif on[w]:
                    low[node] = min(low[node], index[w])
            if recurse:
                continue
            if low[node] == index[node]:
                while True:
                    w = stack.pop()
                    on[w] = False
                    comp[w] = ncomp
                    if w == node:
                        break
                ncomp += 1
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
    return all(comp[2 * v] != comp[2 * v + 1] for v in range(nv))


def parity_criterion(nv, edges, x):
    """Spokes extend for parity links exactly when h_u xor h_v = x_e is solvable: breadth-first propagation."""
    adj = [[] for _ in range(nv)]
    for (u, v), xe in zip(edges, x):
        adj[u].append((v, xe))
        adj[v].append((u, xe))
    h = [None] * nv
    for s in range(nv):
        if h[s] is not None:
            continue
        h[s] = 0
        queue = [s]
        while queue:
            u = queue.pop()
            for w, xe in adj[u]:
                if h[w] is None:
                    h[w] = h[u] ^ xe
                    queue.append(w)
                elif h[w] != h[u] ^ xe:
                    return False
    return True


# ------------------------------------------------------------------ runs

def row(family, a, b, builder, samples, two_solvers):
    t0 = time.time()
    nv, edges, seam, colour = builder(a, b)
    rng = random.Random(f"{family}-{a}-{b}")
    good = agree = 0
    for _ in range(samples):
        x = [rng.randrange(2) for _ in edges]
        ok = consistent_tables(nv, edges, [NAE_TABLES[xe] for xe in x])
        good += ok
        if two_solvers:
            agree += ok == consistent_recoloured(nv, edges, seam, colour, x)
    cut = [e for e, s in zip(edges, seam) if not s]
    p = good / samples
    se_p = math.sqrt(p * (1 - p) / samples)
    E = -math.log2(p) if p > 0 else None
    se_E = se_p / (p * math.log(2)) if p > 0 else None
    return {"family": family, "a": a, "b": b, "vertices": nv, "edges": len(edges), "samples": samples,
            "consistent": good, "P": p, "se_P": se_p, "E": E, "se_E": se_E,
            "solvers_agree": agree if two_solvers else None, "bipartite": bipartite(nv, edges),
            "locally_bipartite": bipartite(nv, cut), "seconds": round(time.time() - t0, 2)}


def slope(rows):
    xs = [math.log2(r["a"]) for r in rows]
    ys = [r["E"] for r in rows]
    ws = [1 / r["se_E"] ** 2 for r in rows]
    W = sum(ws)
    xm = sum(w * x for w, x in zip(ws, xs)) / W
    ym = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - xm) ** 2 for w, x in zip(ws, xs))
    b = sum(w * (x - xm) * (y - ym) for w, x, y in zip(ws, xs, ys)) / sxx
    return b, math.sqrt(1 / sxx)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows, failures = [], []

    # controls first
    for a in (8, 16, 32):
        r = row("square_even_control", a, a, square_torus, 2000, True)
        rows.append(r)
        if r["consistent"] != r["samples"] or r["solvers_agree"] != r["samples"] or not r["bipartite"]:
            failures.append(f"square_even_control {a}")
    for a in (3, 5):
        nv, edges, seam, colour = square_torus(a, a)
        rng = random.Random(f"parity-{a}")
        agree = 0
        for _ in range(500):
            x = [rng.randrange(2) for _ in edges]
            agree += consistent_tables(nv, edges, [PARITY_TABLES[xe] for xe in x]) == parity_criterion(nv, edges, x)
        rows.append({"family": "parity_control", "a": a, "b": a, "samples": 500, "agree": agree})
        if agree != 500:
            failures.append(f"parity_control {a}")
    if failures:
        return finish(rows, failures, started, contract)

    for a in (9, 13, 17, 25, 33, 41):
        rows.append(row("square_odd", a, a, square_torus, 8000, True))
        print(rows[-1], flush=True)
    for a in (9, 13, 17, 25, 33):
        rows.append(row("square_odd_by_even", a, 2 * a, square_torus, 8000, True))
        print(rows[-1], flush=True)
    for a in (4, 8, 12, 16, 24):
        rows.append(row("honeycomb_odd", a, a + 1, brick_torus, 6000, False))
        print(rows[-1], flush=True)
    for a in (3, 4, 5):
        rows.append(row("triangular", a, a, triangular_torus, 20000, False))
        print(rows[-1], flush=True)
    for r in rows:
        fam = r["family"]
        if fam in ("square_odd", "square_odd_by_even"):
            if r["solvers_agree"] != r["samples"]:
                failures.append(f"solver disagreement {fam} {r['a']}")
            if r["bipartite"] or not r["locally_bipartite"]:
                failures.append(f"structure {fam} {r['a']}")
        if fam == "honeycomb_odd" and (r["bipartite"] or not r["locally_bipartite"]):
            failures.append(f"structure {fam} {r['a']}")
        if fam == "triangular" and r["locally_bipartite"]:
            failures.append(f"structure {fam} {r['a']}")
    return finish(rows, failures, started, contract)


def finish(rows, failures, started, contract):
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not failures, "control_failures": failures,
              "rows": len(rows)}
    if not failures:
        fams = {}
        for r in rows:
            fams.setdefault(r["family"], []).append(r)
        sq, sq2 = fams["square_odd"], fams["square_odd_by_even"]
        b1, s1 = slope(sq)
        b2, s2 = slope(sq2)
        floor_ok = all(r["E"] > 0.3 for r in sq + sq2)
        supported = abs(b1) <= 0.04 and abs(b2) <= 0.04 and floor_ok
        refuted = (abs(b1) > 0.04 + 3 * s1) or (abs(b2) > 0.04 + 3 * s2)
        hon = fams["honeycomb_odd"]
        vanish = hon[-1]["E"] < 0.01 and all(
            hon[k + 1]["E"] <= hon[k]["E"] + 3 * math.hypot(hon[k]["se_E"], hon[k + 1]["se_E"]) for k in range(len(hon) - 1))
        tri = fams["triangular"]
        extensive = all(tri[k + 1]["E"] > tri[k]["E"] for k in range(len(tri) - 1)) and \
            tri[-1]["E"] / tri[-1]["vertices"] >= 0.5 * tri[0]["E"] / tri[0]["vertices"]
        mean1 = sum(r["E"] for r in sq) / len(sq)
        mean2 = sum(r["E"] for r in sq2) / len(sq2)
        verdict = "supported" if supported and vanish and extensive else ("refuted" if refuted else "closed-null")
        result.update({
            "square_odd": {"E": [round(r["E"], 4) for r in sq], "se_E": [round(r["se_E"], 4) for r in sq],
                           "slope_per_doubling": b1, "slope_se": s1, "mean_E": mean1},
            "square_odd_by_even": {"E": [round(r["E"], 4) for r in sq2], "se_E": [round(r["se_E"], 4) for r in sq2],
                                   "slope_per_doubling": b2, "slope_se": s2, "mean_E": mean2},
            "honeycomb_odd": {"E": [round(r["E"], 4) for r in hon]},
            "triangular": {"E": [round(r["E"], 4) for r in tri],
                           "E_per_vertex": [round(r["E"] / r["vertices"], 4) for r in tri]},
            "H_scale": "supported" if supported else ("refuted" if refuted else "inconclusive"),
            "H_aspect": mean2 - mean1 >= 0.1, "H_vanish": vanish, "H_extensive": extensive, "verdict": verdict,
        })
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    (OUT / "raw_rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
