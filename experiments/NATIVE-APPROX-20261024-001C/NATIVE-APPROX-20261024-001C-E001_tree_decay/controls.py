#!/usr/bin/env python3
"""Control (i) of NATIVE-APPROX-20261024-001C-E001, run before the producer; writes controls.json next to the rows.

On 50 random native trees of depth at most 3 per knot (half with pin probability 0.2), the interval propagation of run.py equals brute
force: every 0/1 assignment of the boundary leaves, and for each the exact probability that the root edge is 1, by enumerating every
assignment of the internal edges and the root edge with fractions. The smallest and largest of these must match run.envelope to 1e-9.

    python3 -B controls.py
"""

from __future__ import annotations

import itertools
import json
import random
from fractions import Fraction

import run


def flatten(tree):
    """knots as (slot, child refs); a child ref is ('edge', k), ('pin', v) or ('leaf', j); the root edge is edge 0"""
    knots, counter = [], {"edge": 1, "leaf": 0}

    def visit(t, parent_edge):
        _, s, c1, c2 = t
        refs = []
        for c in (c1, c2):
            if c[0] == "pin":
                refs.append(("pin", c[1]))
            elif c[0] == "leaf":
                refs.append(("leaf", counter["leaf"]))
                counter["leaf"] += 1
            else:
                e = counter["edge"]
                counter["edge"] += 1
                refs.append(("edge", e))
                visit(c, e)
        knots.append((s, parent_edge, refs))
    visit(tree, 0)
    return knots, counter["edge"], counter["leaf"]


def brute_range(R, tree):
    knots, n_edges, n_leaves = flatten(tree)
    probs = []
    for leaves in itertools.product((0, 1), repeat=n_leaves):
        z = [0, 0]
        for edges in itertools.product((0, 1), repeat=n_edges):
            ok = True
            for s, pe, refs in knots:
                o = [k for k in range(3) if k != s]
                t = [0, 0, 0]
                t[s] = edges[pe]
                for place, ref in zip(o, refs):
                    t[place] = edges[ref[1]] if ref[0] == "edge" else ref[1] if ref[0] == "pin" else leaves[ref[1]]
                if tuple(t) not in R:
                    ok = False
                    break
            if ok:
                z[edges[0]] += 1
        probs.append(Fraction(z[1], z[0] + z[1]))
    return min(probs), max(probs), n_leaves


def main() -> int:
    run.OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261024)
    agree, trees, with_leaves = True, 0, 0
    for label in run.KNOTS:
        R = run.relation(label)
        maps = [run.node_map(R, s) for s in range(3)]
        for i in range(50):
            L = rng.randint(1, 3)
            q = 0.2 if i % 2 else 0.0
            tree = run.draw_tree(rng, L, q)
            lo, hi, _ = run.envelope(tree, maps)
            blo, bhi, n_leaves = brute_range(R, tree)
            agree &= abs(lo - float(blo)) < 1e-9 and abs(hi - float(bhi)) < 1e-9
            trees += 1
            with_leaves += n_leaves > 0
    controls = {"interval propagation equals brute force on 50 trees of depth at most 3 per knot": agree and with_leaves > 0}
    (run.OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
    print(json.dumps(controls, indent=1), "trees:", trees, "with boundary leaves:", with_leaves)
    return 0 if all(controls.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
