#!/usr/bin/env python3
"""Check shared half-clause padding through literal models and guarded strict CNF."""

import argparse
import json
import os
import random
import runpy
import subprocess
import sys
from collections import Counter
from functools import cache
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
        / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(test, message):
    if not test:
        raise ValueError(message)


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def partitions(n, word=(0,)):
    if len(word) == n:
        yield word
        return
    for v in range(max(word) + 2):
        yield from partitions(n, word + (v,))


def short_names(word):
    labels = {v: i for i, v in enumerate(dict.fromkeys(word))}
    return tuple(labels[v] for v in word)


@cache
def local_minima(word):
    obstructions = {15, 240}  # all four signed halves on one branch
    for pad in set(word[:2]) & set(word[2:]):
        for a_sign in (0, 1):
            mask = 0
            for e, p in enumerate(word):
                signs = 3 if p != pad else 1 << (a_sign if e < 2 else 1 - a_sign)
                mask |= signs << (2 * e)
            obstructions.add(mask)
    return frozenset(obstructions)


def blocked_settings(word, choices):
    count = 2 * choices**4 - 1
    for p in set(word[:2]) & set(word[2:]):
        a, b = word[:2].count(p), word[2:].count(p)
        count += 2 * (choices**a - 1) * (choices**b - 1)
    return count


@cache
def bit_columns(n):
    full = (1 << (1 << n)) - 1
    ones = []
    for i in range(n):
        step = 1 << i
        ones.append((full // ((1 << step) + 1)) << step)
    return full, ones


@cache
def original_failures(r):
    # Enumerate all literal assignments of stage and middle names with both
    # endpoint units active. True implications impose no condition on any pad.
    pairs = [(u, v) for k in range(r) for i in range(2)
             for u, v in ((k, r + 1 + 2 * k + i), (r + 1 + 2 * k + i, k + 1))]
    failed = set()
    for vals in product((False, True), repeat=3 * r - 1):
        bits = (True,) + vals[:r - 1] + (False,) + vals[r - 1:]
        failed.add(sum(1 << i for i, (u, v) in enumerate(pairs) if bits[u] and not bits[v]))
    # A strict superset of failed original implications forbids at least as
    # many half activations for every fixed pad assignment.
    return tuple(tuple(members(d)) for d in failed if not any(e != d and e & d == e for e in failed))


def permitted_halves(layout):
    r = len(layout) // 4
    all_halves = (1 << (8 * r)) - 1
    allowed = set()
    for failed in original_failures(r):
        names = sorted({layout[e] for e in failed})
        for values in product((0, 1), repeat=len(names)):
            valuation = dict(zip(names, values))
            live = all_halves
            for e in failed:
                # Half 0 displays the negative pad, half 1 the positive pad.
                false_half = 1 - valuation[layout[e]]
                live ^= 1 << (2 * e + false_half)
            allowed.add(live)
    return allowed


def literal_bad(layout):
    full, ones = bit_columns(2 * len(layout))
    feasible = sum(1 << mask for mask in permitted_halves(layout))
    for i, column in enumerate(ones):
        feasible |= (feasible & column) >> (1 << i)
    return full ^ feasible


def exact_minima(bad, n):
    full, ones = bit_columns(n)
    nonminimal = 0
    for i, column in enumerate(ones):
        nonminimal |= (bad & (full ^ column)) << (1 << i)
    return set(members(bad & ~nonminimal))


def local_values():
    out = {}
    tables = {}
    for layout in partitions(4):
        bad = literal_bad(layout)
        minima = local_minima(layout)
        require(exact_minima(bad, 8) == minima, "literal one-stage minima differ")
        weights = Counter(3 * mask.bit_count() for mask in minima)
        raw = sum(7**(8 - mask.bit_count()) for mask in members(bad))
        require(bad.bit_count() == blocked_settings(layout, 2) and raw == blocked_settings(layout, 8),
                "literal failed settings differ from the closed count")
        name = "".join(map(str, layout))
        out[name] = {"supports_by_guard_count": dict(sorted(weights.items())),
                     "blocked_half_masks": bad.bit_count(), "blocked_raw_stage_masks": raw}
        tables[layout] = bad
    return tables, out


@cache
def product_table(left, right):
    return sum(left << (256 * hi) for hi in members(right))


def two_stage_census(tables):
    tested = 0
    sizes = Counter()
    cross_stage = 0
    for layout in partitions(8):
        left, right = short_names(layout[:4]), short_names(layout[4:])
        actual = literal_bad(layout)
        require(actual == product_table(tables[left], tables[right]), "a cross-stage identification changed feasibility")
        prediction = {a | (b << 8) for a in local_minima(left) for b in local_minima(right)}
        require(exact_minima(actual, 16) == prediction, "two-stage minimal supports fail to factor")
        sizes[len(prediction)] += 1
        cross_stage += bool(set(layout[:4]) & set(layout[4:]))
        tested += 1
    return {"layouts": tested, "with_cross_stage_reuse": cross_stage, "complete_half_masks": tested * 65536,
            "layouts_by_number_of_minimal_supports": dict(sorted(sizes.items()))}


def raw_formula(base, layout):
    r = len(layout) // 4
    groups = base["strict_groups"](base["source"](r))
    cnf, _, guards = base["guarded_formula"](groups)
    original = [abs(g[0][-1]) for g in groups[2:]]
    labels = short_names(layout)
    rename = dict(zip(original, (original[k] for k in labels)))
    result = [tuple((1 if lit > 0 else -1) * rename.get(abs(lit), abs(lit)) for lit in clause)
              for clause in cnf]
    require(len(guards) == 24 + 24 * r and all(len({abs(v) for v in row}) == 3 for row in result),
            "guard identity or strict arity lost during pad identification")
    return result, guards


def raw_mask(halves, r, almost=False):
    mask = (1 << 24) - 1
    for h in range(8 * r):
        group = 7 if halves & (1 << h) else 0
        if not group and almost:
            group = 7 ^ (1 << ((h + halves.bit_count()) % 3))
        mask |= group << (24 + 3 * h)
    return mask


def holds(solver, guards, mask):
    return solver.solve(assumptions=[v if mask & (1 << i) else -v for i, v in enumerate(guards)])


def canonical_check(observed, names):
    absent = set(product((0, 1), repeat=len(names))) - set(observed)
    require(absent == {(1,) * len(names)}, "observed raw restriction missed a different assignment")
    cnf = ";".join(" ".join(("~" if b else "") + name for name, b in zip(names, row)) for row in sorted(absent))
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
           "--loops", *names[:-1], "--contact", names[-1], "--json"]
    out = subprocess.run(cmd, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                         capture_output=True, text=True, check=True)
    data = json.loads(out.stdout)
    require(data["is_knot"] and data["erasure"] == "forgetting" and len(data["allowed"]) == len(observed),
            "canonical forgetting test failed on literal table")
    return {"loops": names[:-1], "contact": names[-1], "allowed": len(observed), "is_knot": data["is_knot"]}


def raw_checks():
    from pysat.solvers import Solver

    base = runpy.run_path(str(BASE))
    counts = Counter()
    knot = []
    named_drop_control = {}
    rng = random.Random(85014)
    only_between = (0, 1, 2, 3, 4, 5, 6, 7, 0, 8, 9, 10)
    larger = [(0, 1, 0, 2, 3, 1, 2, 3), (0, 1, 2, 3) * 3, (0,) * 12,
              (0, 1, 0, 1, 1, 2, 1, 3, 2, 0, 0, 2), only_between, (0, 1, 0, 1, 0, 0, 0, 0) * 3]
    for layout in [*partitions(4), *larger]:
        r = len(layout) // 4
        formula, guards = raw_formula(base, layout)
        stages = [local_minima(short_names(layout[i:i + 4])) for i in range(0, len(layout), 4)]
        with Solver(name="g3", bootstrap_with=formula) as solver:
            half_vectors = range(256) if r == 1 else [rng.getrandbits(8 * r) for _ in range(128)]
            for mask in half_vectors:
                contradiction = all(any(((mask >> (8 * k)) & p) == p for p in stage)
                                    for k, stage in enumerate(stages))
                for almost in (False, True):
                    require(holds(solver, guards, raw_mask(mask, r, almost)) != contradiction,
                            "guarded strict CNF disagrees on a complete vector")
                    counts["complete_guard_vectors"] += 1
            candidates = product(*map(sorted, stages)) if r <= 2 else [tuple(max(s) for s in stages)]
            for selected in candidates:
                mask = raw_mask(sum(m << (8 * k) for k, m in enumerate(selected)), r)
                require(not holds(solver, guards, mask), "claimed minimal support was satisfiable")
                for i in members(mask):
                    require(holds(solver, guards, mask ^ (1 << i)), "a single switch deletion left a contradiction")
                    counts["single_switch_deletions"] += 1
                counts["minimal_guard_supports"] += 1
            if layout == (0, 0, 0, 0):
                half_example = 90  # Both positive A halves and both negative B halves.
                common = raw_mask(half_example, 1)
                require(not holds(solver, guards, common), "shared-pad negative control became feasible")
                fresh, independent = raw_formula(base, (0, 1, 2, 3))
                with Solver(name="g3", bootstrap_with=fresh) as other:
                    require(holds(other, independent, common), "wrong fresh-pad interpretation failed to separate")
                selected = [24 + 3 * h for h in members(half_example)]
                for w in (3, 4):
                    active = selected[:w]
                    fixed = common ^ sum(1 << i for i in active)
                    allowed = [row for row in product((0, 1), repeat=w)
                               if holds(solver, guards, fixed | sum(b << i for b, i in zip(row, active)))]
                    item = canonical_check(allowed, ["AinPlus", "AoutPlus", "BinMinus", "BoutMinus"][:w])
                    knot.append({**item, "free_guard_indices": active})
            if layout == only_between:
                # Stage 1 has A-in positive, A-out complete. Stage 3 has
                # A-in negative, A-out complete. Only the A-in pad is reused.
                halves = 14 | (255 << 8) | (13 << 16)
                mask = raw_mask(halves, 3)
                fixed = [v if mask & (1 << i) else -v for i, v in enumerate(guards)]
                # The actual source numbering is x_0=1, x_1=2, x_2=3, x_3=4.
                controls = {"guards_only": [], "first_descent": [-2], "last_descent": [3],
                            "both_prescribed_descents": [-2, 3]}
                named_drop_control = {name: solver.solve(assumptions=fixed + pins)
                                      for name, pins in controls.items()}
                require(named_drop_control == {"guards_only": True, "first_descent": True,
                        "last_descent": True, "both_prescribed_descents": False},
                        "two forced descents on one shared pad failed to separate the projections")
    require(len(knot) == 2, "missing visible-switch restrictions")
    require(named_drop_control, "missing three-stage named-variables control")
    return {"solver_tests": dict(sorted(counts.items())), "fresh_vs_shared": {"half_mask": 90,
            "raw_support_size": 36, "fresh_sat": True, "shared_sat": False}, "visible_guard_restrictions": knot,
            "pinning_two_descents": named_drop_control}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("checks.json"))
    args = parser.parse_args()
    if args.raw:
        print(json.dumps(raw_checks()))
        return
    tables, local = local_values()
    global_counts = two_stage_census(tables)
    raw = subprocess.run([str(ROOT / ".venv/bin/python"), "-B", str(Path(__file__).resolve()), "--raw"],
                         check=True, capture_output=True, text=True)
    result = {"local_partitions": local, "local_half_masks": len(local) * 256,
              "two_stages": global_counts, "raw_cnf": json.loads(raw.stdout)}
    # Normalize integer histogram keys to the interchange representation.
    result = json.loads(json.dumps(result))
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(json.loads(args.expected.read_text()) == result, "reference data differ from recalculated evidence")
        print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
