#!/usr/bin/env python3
"""Check of NATIVE-APPROX-20261024-001D-P001 (standard library only, seed 20261024).

A place of a knot is two-way when the knot's excluded tuples take both values there, and one-way otherwise. A native tree without pins
has knots joined by edges, one root edge and boundary leaves; every knot has its parent edge in some place. Its width is the largest
minus the smallest probability that the root edge is 1 over all boundary values.
Checks:
- census: exactly 14 knots have three two-way places (the four excluding an antipodal pair, the eight excluding three tuples, the two
  parity knots), including the six open knots; the other 20 (eight single clauses, twelve excluding a pair at distance two) have a
  one-way place;
- exact integer counting on trees agrees with brute-force enumeration on random small trees and boundaries, for all 34 knots;
- if: for each two-way knot, on 150 random irregular trees of depth up to 10, the inductive construction gives boundary values that
  force the root edge to 0 and others that force it to 1 (exact counts: the other value has count 0, this one a positive count);
  brute force confirms it on the trees with at most seven knots;
- only if: for each one-way place (excluded tuples all take value u there), on random trees whose root edge sits there, every hard
  boundary (exhaustively, depth up to 3) and random soft boundaries (depth up to 8) give P(root edge = u) <= 1/2;
- consistency with ticket C (its bound rows): without pins, every tree of every depth had width 1 for the two-way knots tested, and
  the one-way controls had median width below 1e-6 at depth 16.
Controls: the construction is refused at every one-way place for its forbidden value; for a relation with three two-way places that
violates K2 (excluded 000, 001, 110, 111), the construction produces boundaries with no consistent assignment at all, so K2 is used.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CUBE = list(itertools.product((0, 1), repeat=3))
C_ROWS = ROOT / "artifacts/NATIVE-APPROX-20261024-001C/NATIVE-APPROX-20261024-001C-E001_tree_decay/rows.jsonl"


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def excluded(R):
    return [t for t in CUBE if t not in R]


def label(R):
    return ",".join("".join(map(str, t)) for t in excluded(R))


def two_way(R, s):
    return len({t[s] for t in excluded(R)}) == 2


def family(R):
    Z = excluded(R)
    if len(Z) == 1:
        return "single clause"
    if len(Z) == 2:
        return "antipodal pair" if sum(a != b for a, b in zip(*Z)) == 3 else "pair at distance two"
    return {3: "three excluded", 4: "parity"}[len(Z)]


def is_open(R):
    return len(excluded(R)) == 3 and not all(tuple(t[p] for p in perm) in R for t in R for perm in itertools.permutations(range(3)))


def random_tree(rng, max_depth, p_leaf, root_slot=None, level=0):
    """('knot', parent slot, child, child) or ('leaf',); children fill the other two places in increasing order"""
    s = rng.randrange(3) if root_slot is None else root_slot
    kids = []
    for _ in range(2):
        if level + 1 == max_depth or rng.random() < p_leaf:
            kids.append(("leaf",))
        else:
            kids.append(random_tree(rng, max_depth, p_leaf, None, level + 1))
    return ("knot", s, kids[0], kids[1])


def n_knots(tree):
    return 0 if tree[0] == "leaf" else 1 + n_knots(tree[2]) + n_knots(tree[3])


def n_leaves(tree):
    return 1 if tree[0] == "leaf" else n_leaves(tree[2]) + n_leaves(tree[3])


def place_tuple(s, v, a, b):
    t = [0, 0, 0]
    o = [k for k in range(3) if k != s]
    t[s], t[o[0]], t[o[1]] = v, a, b
    return tuple(t)


def force(tree, R, v):
    """boundary values (depth-first order) forcing the parent edge to v, by the inductive construction, or None"""
    if tree[0] == "leaf":
        return [v]
    _, s, c1, c2 = tree
    for t in excluded(R):
        if t[s] == 1 - v:
            o = [k for k in range(3) if k != s]
            left, right = force(c1, R, t[o[0]]), force(c2, R, t[o[1]])
            if left is None or right is None:
                return None
            return left + right
    return None


def counts(tree, R, leaves, weights=False):
    """exact counts (Z0, Z1) of consistent assignments with the parent edge 0 or 1; leaves is an iterator of boundary values
    (or of probabilities of 1, if weights)"""
    if tree[0] == "leaf":
        x = next(leaves)
        return (1 - x, x) if weights else ((1, 0) if x == 0 else (0, 1))
    _, s, c1, c2 = tree
    A, B = counts(c1, R, leaves, weights), counts(c2, R, leaves, weights)
    Z = [0, 0]
    for v, a, b in itertools.product((0, 1), repeat=3):
        if place_tuple(s, v, a, b) in R:
            Z[v] += A[a] * B[b]
    return tuple(Z)


def brute(tree, R, leaves):
    """the same counts by enumerating every assignment of the tree's edges (root edge first)"""
    knots_, counter = [], {"edge": 1, "leaf": 0}

    def visit(t, pe):
        _, s, c1, c2 = t
        refs = []
        for c in (c1, c2):
            if c[0] == "leaf":
                refs.append(("leaf", counter["leaf"]))
                counter["leaf"] += 1
            else:
                e = counter["edge"]
                counter["edge"] += 1
                refs.append(("edge", e))
                visit(c, e)
        knots_.append((s, pe, refs))
    visit(tree, 0)
    Z = [0, 0]
    for edges in itertools.product((0, 1), repeat=counter["edge"]):
        ok = all(place_tuple(s, edges[pe], *[(edges[i] if kind == "edge" else leaves[i]) for kind, i in refs]) in R
                 for s, pe, refs in knots_)
        Z[edges[0]] += ok
    return tuple(Z)


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    K = knots()
    two = [R for R in K if all(two_way(R, s) for s in range(3))]
    one = [R for R in K if R not in two]
    census = {"knots": len(K), "two-way forcing knots": len(two),
              "families of the two-way knots": dict(sorted({f: sum(family(R) == f for R in two) for f in {family(R) for R in two}}.items())),
              "families of the one-way knots": dict(sorted({f: sum(family(R) == f for R in one) for f in {family(R) for R in one}}.items())),
              "the six open knots are two-way": sum(is_open(R) for R in two) == 6 and sum(is_open(R) for R in K) == 6}

    # exact counting = brute force
    agree = 0
    for R in K:
        for _ in range(6):
            tree = random_tree(rng, 3, 0.3)
            leaves = [rng.randint(0, 1) for _ in range(n_leaves(tree))]
            agree += counts(tree, R, iter(leaves)) == brute(tree, R, leaves)
    counting = {"trees": 6 * len(K), "exact counts equal brute force": agree}

    # if
    forced = brute_forced = trees_if = 0
    all_forced = True
    for R in two:
        for i in range(150):
            tree = random_tree(rng, rng.randint(1, 10), rng.choice([0.0, 0.2, 0.4]))
            trees_if += 1
            for v in (0, 1):
                leaves = force(tree, R, v)
                ok = leaves is not None
                if ok:
                    Z = counts(tree, R, iter(leaves))
                    ok = Z[1 - v] == 0 and Z[v] > 0
                    if ok and n_knots(tree) <= 7:
                        Zb = brute(tree, R, leaves)
                        ok = Zb[1 - v] == 0 and Zb[v] > 0
                        brute_forced += ok
                forced += ok
                all_forced &= ok
    if_part = {"trees": trees_if, "root values forced": forced, "of which also by brute force": brute_forced,
               "every root value forced on every tree": all_forced and forced == 2 * trees_if}

    # only if
    only_ok, hard_cases, soft_cases = True, 0, 0
    for R in one:
        for s in range(3):
            if two_way(R, s):
                continue
            u = excluded(R)[0][s]
            for i in range(12):
                tree = random_tree(rng, rng.randint(1, 3), 0.3, root_slot=s)
                for leaves in itertools.product((0, 1), repeat=n_leaves(tree)):
                    Z = counts(tree, R, iter(leaves))
                    only_ok &= 2 * Z[u] <= Z[0] + Z[1]
                    hard_cases += 1
            for i in range(12):
                tree = random_tree(rng, rng.randint(4, 8), 0.3, root_slot=s)
                ws = [Fraction(rng.randint(0, 8), 8) for _ in range(n_leaves(tree))]
                Z = counts(tree, R, iter(ws), weights=True)
                only_ok &= 2 * Z[u] <= Z[0] + Z[1]
                soft_cases += 1
    only_if = {"hard boundaries checked": hard_cases, "soft boundaries checked": soft_cases,
               "P(root edge = u) <= 1/2 at every one-way root place": only_ok}

    # consistency with ticket C
    rows = [json.loads(line) for line in C_ROWS.read_text().splitlines()]
    by_label = {label(R): R for R in K}
    c_two = all(min(r["widths"]) == 1.0 for r in rows if r["q"] == 0.0 and by_label[r["knot"]] in two)
    c_one = all(r["median"] < 1e-6 for r in rows if r["q"] == 0.0 and r["L"] == 16 and by_label[r["knot"]] in one)
    consistency = {"C: two-way knots kept width 1 on every tree without pins": c_two,
                   "C: one-way controls fell below 1e-6 at depth 16 without pins": c_one,
                   "C knots two-way / one-way": [len({r["knot"] for r in rows if by_label[r["knot"]] in two}),
                                                  len({r["knot"] for r in rows if by_label[r["knot"]] in one})]}

    # controls
    refused = all(force(("knot", s, ("leaf",), ("leaf",)), R, excluded(R)[0][s]) is None
                  for R in one for s in range(3) if not two_way(R, s))
    bad = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 0, 1), (1, 1, 0), (1, 1, 1)})
    k2_needed = all(two_way(bad, s) for s in range(3)) and any(
        (lambda tr: (lambda lv: lv is not None and sum(counts(tr, bad, iter(lv))) == 0)(force(tr, bad, 0)))(random_tree(rng, 3, 0.0))
        for _ in range(20))
    controls = {"the construction is refused at every one-way place for its forbidden value": refused,
                "without K2 the construction can leave no consistent assignment": k2_needed}

    ok = (census["two-way forcing knots"] == 14
          and census["families of the two-way knots"] == {"antipodal pair": 4, "parity": 2, "three excluded": 8}
          and census["families of the one-way knots"] == {"pair at distance two": 12, "single clause": 8}
          and census["the six open knots are two-way"] and counting["exact counts equal brute force"] == counting["trees"]
          and if_part["every root value forced on every tree"] and if_part["of which also by brute force"] > 0
          and only_if["P(root edge = u) <= 1/2 at every one-way root place"] and c_two and c_one and all(controls.values()))
    result["checks"] = {"census": census, "exact counting": counting, "if": if_part, "only if": only_if, "ticket C": consistency}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
