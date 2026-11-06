#!/usr/bin/env python3
"""Independent check of FREEZING-KNOTS-20261020-001A-E001. It imports no producer code.

- Tree values: p_L and Psi(p_L) are recomputed in exact rational arithmetic for
  every measured (q, d, L).
- Star nativity on explicit broadcast trees: random broadcast colourings of the
  tree to depth L + 2 around a centre. Each star member is tested by exhaustive
  search on its ball, with distance L + 1 fixed. The estimate is compared with
  the producer's exact star value.
- Stored balls are re-solved by exhaustive search, and their verdicts compared.
- Relation study: every stored witness colouring is checked to be proper and to
  match its triple. Every missing triple is re-proved unrealizable with this
  file's own solver. The fractions are recomputed.
- Summary fractions and prediction flags are recomputed from the raw rows.
"""

from __future__ import annotations

import gzip
import json
import random
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import comb, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "FREEZING-KNOTS-20261020-001A" / HERE.name


def cover_exact(p, need, k, total):
    return sum(Fraction((-1) ** j * comb(need, j)) * (1 - Fraction(j) * p / total) ** k for j in range(need + 1))


def exact_values(q, d, L):
    p = Fraction(1)
    for _ in range(L):
        p = cover_exact(p, q - 1, d - 1, q - 1)
    return p, cover_exact(p, q - 1, d, q - 1)


def arc_consistent(domains, nbrs):
    """AC-3 for the inequality constraints on edges; returns False if a domain empties. Mutates domains."""
    queue = [(u, w) for u in domains for w in nbrs[u] if w in domains]
    while queue:
        u, w = queue.pop()
        if len(domains[w]) == 1:
            (c,) = tuple(domains[w])
            if c in domains[u]:
                domains[u] = domains[u] - {c}
                if not domains[u]:
                    return False
                queue.extend((x, u) for x in nbrs[u] if x in domains and x != w)
    return True


def satisfiable(domains, nbrs):
    domains = dict(domains)
    if not arc_consistent(domains, nbrs):
        return False
    open_vars = [u for u in domains if len(domains[u]) > 1]
    if not open_vars:
        return True
    u = min(open_vars, key=lambda x: (len(domains[x]), str(x)))
    for c in sorted(domains[u]):
        trial = dict(domains)
        trial[u] = frozenset({c})
        if satisfiable(trial, nbrs):
            return True
    return False


def can_recolour(nbrs, colour, centre, free, fixed_colours, q):
    """Is there a proper colouring of `free` (with fixed_colours on the rest) giving `centre` a new colour?"""
    domains = {u: frozenset({c}) for u, c in fixed_colours.items()}
    for u in free:
        domains[u] = frozenset(c for c in range(q) if not (u == centre and c == colour[centre]))
    return satisfiable(domains, nbrs)


def tree_star_estimate(q, d, L, samples, rng):
    native = 0
    for _ in range(samples):
        colour = {0: rng.randrange(q)}
        parent = {0: None}
        depth = {0: 0}
        nbrs = defaultdict(list)
        frontier = [0]
        nxt_id = 1
        for level in range(1, L + 3):
            new = []
            for u in frontier:
                kids = d if u == 0 else d - 1
                for _ in range(kids):
                    v = nxt_id
                    nxt_id += 1
                    colour[v] = rng.choice([c for c in range(q) if c != colour[u]])
                    parent[v] = u
                    depth[v] = level
                    nbrs[u].append(v)
                    nbrs[v].append(u)
                    new.append(v)
            frontier = new
        members = nbrs[0][:q]
        ok_all = True
        for a in members:
            dist = {a: 0}
            queue = [a]
            for u in queue:
                if dist[u] == L + 1:
                    continue
                for w in nbrs[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        queue.append(w)
            free = [u for u, k in dist.items() if k <= L]
            fixed = {u: colour[u] for u, k in dist.items() if k == L + 1}
            if not can_recolour(nbrs, colour, a, free, fixed, q):
                ok_all = False
                break
        native += ok_all
    return native / samples


def solve_ball(rec, q):
    n = len(rec["dist"])
    nbrs = defaultdict(list)
    for a, b in rec["edges"]:
        nbrs[a].append(b)
        nbrs[b].append(a)
    L = rec["L"]
    free = [u for u in range(n) if rec["dist"][u] <= L]
    fixed = {u: rec["colour"][u] for u in range(n) if rec["dist"][u] == L + 1}
    colour = {u: rec["colour"][u] for u in range(n)}
    return can_recolour(nbrs, colour, 0, free, fixed, q)


def colourable(n, adj, fixed):
    """Own solver: arc consistency at every node, branching on the smallest open domain."""
    nbrs = {u: list(adj[u]) for u in range(n)}
    for u, c in fixed.items():
        if any(fixed.get(w) == c for w in nbrs[u]):
            return False
    domains = {u: frozenset({fixed[u]}) if u in fixed else frozenset(range(3)) for u in range(n)}
    return satisfiable(domains, nbrs)


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    report = {}

    exact_ok = 0
    for key, row in result["local"].items():
        p, psi = exact_values(row["q"], row["d"], row["L"])
        if abs(float(psi) - row["psi"]) > 1e-9:
            problems.append(f"psi mismatch at {key}")
        else:
            exact_ok += 1
    report["psi_exact_matches"] = exact_ok

    rng = random.Random(7)
    estimates = {}
    for q, d, L, samples in ((3, 3, 1, 400), (3, 4, 1, 400), (3, 4, 2, 400), (3, 5, 1, 400), (3, 6, 1, 400), (4, 9, 1, 300)):
        est = tree_star_estimate(q, d, L, samples, rng)
        target = result["local"][f"q{q}_d{d}_L{L}"]["star_exact"]
        tol = 4 * sqrt(max(target * (1 - target), 1e-6) / samples) + 0.01
        estimates[f"q{q}_d{d}_L{L}"] = {"estimate": est, "exact": target, "within": abs(est - target) <= tol}
        if abs(est - target) > tol:
            problems.append(f"star exact value disagrees with explicit trees at q{q}_d{d}_L{L}")
    report["star_tree_estimates"] = estimates

    with gzip.open(ART / "balls.json.gz", "rt") as fh:
        balls = json.load(fh)
    agree = sum(solve_ball(rec, rec["q"]) == (not rec["verdict_frozen"]) for rec in balls)
    report["balls_resolved"] = {"balls": len(balls), "agree": agree}
    if agree != len(balls):
        problems.append("a stored ball verdict disagrees with exhaustive search")

    with gzip.open(ART / "relation.json.gz", "rt") as fh:
        graphs = json.load(fh)
    not_distinct = {"".join(map(str, t)) for t in product(range(3), repeat=3) if len(set(t)) < 3}
    witnesses_ok = unrealizable_ok = 0
    fractions = defaultdict(lambda: [0, 0])
    for g in graphs:
        n, adj = g["n"], g["adj"]
        for star in g["stars"]:
            a, b, c = star["star"]
            realized = set(star["realized"])
            for t, wit in star["witnesses"].items():
                proper = all(wit[u] != wit[w] for u in range(n) for w in adj[u])
                matches = [wit[a], wit[b], wit[c]] == [int(x) for x in t]
                witnesses_ok += proper and matches
                if not (proper and matches):
                    problems.append("a witness colouring is improper or does not match its triple")
            for t in product(range(3), repeat=3):
                key = "".join(map(str, t))
                if key in realized:
                    continue
                if colourable(n, adj, {a: t[0], b: t[1], c: t[2]}):
                    problems.append(f"triple {key} is realizable in graph d{g['d']} n{n} g{g['g']}")
                else:
                    unrealizable_ok += 1
            fractions[(g["d"], n)][0] += 1
            fractions[(g["d"], n)][1] += realized == not_distinct
    rel = {f"d{d}_n{n}": c[1] / c[0] for (d, n), c in sorted(fractions.items())}
    report["relation"] = {"witnesses_verified": witnesses_ok, "unrealizable_reproved": unrealizable_ok, "fractions": rel}
    if any(abs(rel[k] - result["relation_knot_fraction"][k]) > 1e-12 for k in rel):
        problems.append("relation fractions differ from result.json")

    local_rows = [r for r in rows if r["kind"] == "local"]
    for r in local_rows:
        key = f"q{r['q']}_d{r['d']}_L{r['L']}"
        stored = result["local"][key]
        if r["vertex_frozen"] / r["vertex_tree_like"] != stored["frozen_fraction"]:
            problems.append(f"frozen fraction mismatch at {key}")

    def tol(v, n):
        return max(0.03, 3 * sqrt(max(v * (1 - v), 1e-12) / max(n, 1)))

    p1 = all(abs(r["frozen_fraction"] - r["psi"]) <= tol(r["psi"], r["vertex_tree_like"]) for r in result["local"].values())
    p2 = all(abs(r["native_fraction"] - r["star_exact"]) <= tol(r["star_exact"], r["star_tree_like"])
             for r in result["local"].values() if r["star_tree_like"] >= 100)
    p4 = all(rel[f"d3_n{n}"] >= 0.8 and rel[f"d7_n{n}"] <= 0.5 for n in (24, 36))
    report["predictions_recomputed"] = {"P1": p1, "P2": p2, "P4": p4}
    if (p1, p2, p4) != (result["predictions"]["P1"], result["predictions"]["P2"], result["predictions"]["P4"]):
        problems.append("prediction flags differ from result.json")

    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
