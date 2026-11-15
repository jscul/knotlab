#!/usr/bin/env python3
"""Check one identified middle by path enumeration, simultaneous truth and strict CNF."""

import argparse
import json
import runpy
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
        / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def arcs(r, join=None):
    edges = []
    for stage in range(r):
        for branch in range(2):
            middle = stage * 2 + branch
            if join is not None and middle == join[1]:
                middle = join[0]
            node = r + 1 + middle
            edges.extend(((stage, node), (node, stage + 1)))
    return edges


def simple_paths(r, edges):
    next_edges = defaultdict(list)
    for i, (s, t) in enumerate(edges):
        next_edges[s].append((t, 1 << i))
    found = set()

    def visit(node, visited, path):
        if node == r:
            found.add(path)
            return
        for target, bit in next_edges[node]:
            if target not in visited:
                visit(target, visited | {target}, path | bit)
    visit(0, {0}, 0)
    return found


def block_counts(r, d, choices):
    """Each live edge group has one realization, an inactive group has choices-1."""
    active_stage = 2 * choices**2 - 1
    if d == 0:
        return 2 * (choices - 1)**2 * active_stage**(r - 1)
    live_at_one_end = choices**2 + choices - 1
    extra = choices**6 * (choices**4)**(d - 1) - live_at_one_end**2 * active_stage**(d - 1)
    return active_stage**(r - d - 1) * extra


def path_counts(r, d):
    if d == 0:
        return 2**r, 0, 2**r
    return 3 * 2**(r - 2), 2**(r - 2), 2**(r - d - 1)


def larger_path_counts(r):
    old = simple_paths(r, arcs(r))
    totals = {}
    for join in combinations(range(2 * r), 2):
        d = join[1] // 2 - join[0] // 2
        paths = simple_paths(r, arcs(r, join))
        require((len(paths & old), len(old - paths), len(paths - old)) == path_counts(r, d),
                "a larger route family disagrees with the counting proof")
        require(totals.setdefault(str(d), len(paths)) == len(paths), "path counts depend on position")
    return {"layouts": r * (2 * r - 1), "paths_per_layout_by_gap": totals}


def one_columns(n):
    """Bit i in a column denotes the ith edge activation."""
    full = (1 << (1 << n)) - 1
    cols = []
    for j in range(n):
        run = 1 << j
        cols.append((full // ((1 << run) + 1)) << run)
    return full, cols


def bitmap_members(bits):
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low


def impossible_assignments(r, edges, full, columns):
    # Enumerate all original truth assignments with the endpoints forced. For
    # each assignment, every subset of the implications it satisfies is feasible.
    free = sorted({v for edge in edges for v in edge} - {0, r})
    sat = 0
    for values in product((False, True), repeat=len(free)):
        assignment = {0: True, r: False, **dict(zip(free, values))}
        permitted = sum(1 << i for i, (s, t) in enumerate(edges) if not assignment[s] or assignment[t])
        sat |= 1 << permitted
    for j, active in enumerate(columns):
        sat |= (sat & active) >> (1 << j)
    return full ^ sat


def predicted_bitmap(paths, full, cols):
    answer = 0
    for path in paths:
        supersets = full
        for i in bitmap_members(path):
            supersets &= cols[i]
        answer |= supersets
    return answer


def finite_census(r):
    base_paths = simple_paths(r, arcs(r))
    full, cols = one_columns(4 * r)
    old_unsat = predicted_bitmap(base_paths, full, cols)
    by_gap = {}
    layout_count = Counter()
    for join in combinations(range(2 * r), 2):
        edges = arcs(r, join)
        paths = simple_paths(r, edges)
        d = join[1] // 2 - join[0] // 2
        kept, lost, added = len(paths & base_paths), len(base_paths - paths), len(paths - base_paths)
        require((kept, lost, added) == path_counts(r, d), "old and new path comparison failed")
        if d:
            require(all(len([p for p in paths - base_paths if p & mask == p]) == 1
                        for mask in base_paths - paths), "an old nonminimal path lacks its unique shortcut")
        truth = impossible_assignments(r, edges, full, cols)
        require(truth == predicted_bitmap(paths, full, cols), "actual implications disagree with paths")
        # For the other three endpoint settings a single assignment satisfies
        # the FULL set of arcs, so it witnesses every subset at that setting.
        for positive, negative, constant in ((0, 0, 0), (0, 1, 0), (1, 0, 1)):
            assignment = [constant] * (3 * r + 1)
            require((not positive or assignment[0]) and (not negative or not assignment[r])
                    and all(not assignment[s] or assignment[t] for s, t in edges),
                    "a released endpoint lacked the promised constant witness")
        nonminimal = 0
        for j, on in enumerate(cols):
            nonminimal |= ((truth & (full ^ on)) << (1 << j))
        require(set(bitmap_members(truth & ~nonminimal)) == paths, "truth-table minima changed")
        require(not (old_unsat & ~truth), "an old contradiction was lost")
        wrong = truth & ~old_unsat
        require(wrong.bit_count() == block_counts(r, d, 2), "source activation count changed")
        missed = Counter(mask.bit_count() for mask in bitmap_members(wrong))
        raw = sum(count * 63**(4 * r - weight) for weight, count in missed.items())
        require(raw == block_counts(r, d, 64), "raw-switch activation count changed")
        sizes = Counter(24 + 6 * mask.bit_count() for mask in paths)
        key = str(d)
        row = {"kept": kept, "old_nonminimal": lost, "new": added,
               "minimal_switch_supports_by_size": {str(k): v for k, v in sorted(sizes.items())},
               "wrong_source_activations": wrong.bit_count(), "wrong_raw_switch_vectors": raw}
        require(by_gap.setdefault(key, row) == row, "position or branch label changed a class count")
        layout_count[key] += 1
    layouts = sum(layout_count.values())
    return {"layouts": layouts, "layouts_by_gap": dict(sorted(layout_count.items())),
            "source_vectors": layouts * 2**(4 * r + 2),
            "both_endpoints_on_vectors": layouts * 2**(4 * r), "per_layout_by_gap": by_gap}


def renamed_cnf(base, r, join):
    formula, groups, switches = base["guarded_formula"](base["strict_groups"](base["source"](r)))
    first, second = (r + 2 + m for m in join)
    require(first not in switches and second not in switches, "a middle was mislabeled as a switch")
    result = [tuple((first if lit > 0 else -first) if abs(lit) == second else lit for lit in row)
              for row in formula]
    require(all(len({abs(lit) for lit in row}) == 3 for row in result), "a strict clause degenerated")
    return formula, result, groups, switches


def switch_mask(live, groups, almost=False):
    mask = 0
    for j, group in enumerate(groups):
        if live & (1 << j):
            mask |= group
        elif almost:
            first = (group & -group).bit_length() - 1
            missing = first + (live.bit_count() + j) % group.bit_count()
            mask |= group ^ (1 << missing)
    return mask


def raw_cnf_checks():
    from pysat.solvers import Solver

    base = runpy.run_path(str(BASE))
    results = Counter()
    earliest = None
    for r in (1, 2, 3, 4, 6):
        joins = combinations(range(2 * r), 2) if r <= 4 else ((0, 1), (0, 2), (0, 2 * r - 2))
        for join in joins:
            paths = simple_paths(r, arcs(r, join))
            old, formula, groups, switches = renamed_cnf(base, r, join)
            with Solver(name="g3", bootstrap_with=formula) as solver:
                def allowed(mask):
                    return solver.solve(assumptions=[v if mask & (1 << i) else -v
                                                     for i, v in enumerate(switches)])

                if r <= 2:
                    for live in range(1 << len(groups)):
                        predicted = not ((live & 3) == 3 and any((live >> 2) & p == p for p in paths))
                        for almost in (False, True):
                            require(allowed(switch_mask(live, groups, almost)) == predicted,
                                    "literal CNF disagrees at a source activation")
                            results["complete_source_activation_representatives"] += 1
                new_paths = paths - simple_paths(r, arcs(r))
                support = switch_mask(3 | (min(new_paths) << 2), groups)
                require(not allowed(support), "raw minimal obstruction became feasible")
                for bit in bitmap_members(support):
                    require(allowed(support ^ (1 << bit)), "deleting one switch failed to repair")
                results["minimal_supports_in_literal_cnf"] += 1
                results["single_switch_deletions"] += support.bit_count()
                if r == 1:
                    # The first numerical error mask uses a-out and b-in.
                    old_paths = simple_paths(r, arcs(r))
                    bad = [mask for mask in range(16) if any(mask & p == p for p in paths)
                           and not any(mask & p == p for p in old_paths)]
                    require(bad == [6, 9], "first same-stage error masks changed")
                    activation = 3 | (min(bad) << 2)
                    witness = switch_mask(activation, groups)
                    assumptions = [v if witness & (1 << i) else -v for i, v in enumerate(switches)]
                    with Solver(name="g3", bootstrap_with=old) as original:
                        require(original.solve(assumptions=assumptions) and not allowed(witness),
                                "the claimed first false answer failed on an actual strict CNF")
                    chosen = [next(bitmap_members(groups[k])) for k in bitmap_members(activation)]
                    fixed = witness ^ sum(1 << k for k in chosen)
                    rows = [bits for bits in product((0, 1), repeat=len(chosen))
                            if allowed(fixed | sum(b << k for b, k in zip(bits, chosen)))]
                    require(set(product((0, 1), repeat=4)) - set(rows) == {(1, 1, 1, 1)},
                            "the observed four-switch restriction had the wrong missing row")
                    earliest = {"stages": r, "live_source_mask": activation,
                                "switches": len(switches), "one_switch_indices": list(bitmap_members(witness)),
                                "four_switch_restriction_indices": chosen,
                                "four_switch_restriction_rows": base["canonical_check"](rows),
                                "unjoined_sat": True, "joined_sat": False}
    return {"tests": dict(sorted(results.items())), "first_counterexample": earliest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("checks.json"))
    args = parser.parse_args()
    if args.raw:
        print(json.dumps(raw_cnf_checks()))
        return
    census = {str(r): finite_census(r) for r in range(1, 5)}
    raw = subprocess.run([str(ROOT / ".venv/bin/python"), "-B", str(Path(__file__).resolve()), "--raw"],
                         text=True, capture_output=True, check=True)
    result = {"per_stage_count": census, "raw_cnf": json.loads(raw.stdout),
              "larger_path_counts": {str(r): larger_path_counts(r) for r in (5, 6, 7)},
              "layouts": sum(row["layouts"] for row in census.values()),
              "source_activation_vectors": sum(row["source_vectors"] for row in census.values())}
    if args.emit:
        print(json.dumps(result, indent=2))
        return
    require(json.loads(args.expected.read_text()) == result, "saved and recomputed counts disagree")
    print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
