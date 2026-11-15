"""Replay the switch-to-clause identities, exact path count, and finite controls."""

import argparse
from itertools import product
import json
import os
from pathlib import Path
import random
import subprocess
import sys


def source(r):
    """Initial and final units, then four directed implications per stage."""
    nodes = list(range(1, r + 2))
    clauses = [(nodes[0],), (-nodes[-1],)]
    fresh = r + 2
    for left, right in zip(nodes, nodes[1:]):
        for middle in (fresh, fresh + 1):
            clauses.extend([(-left, middle), (-middle, right)])
        fresh += 2
    return clauses


def strict_groups(clauses):
    fresh = max(abs(lit) for row in clauses for lit in row) + 1
    groups = []
    for clause in clauses:
        pads = tuple(range(fresh, fresh + 3 - len(clause)))
        fresh += len(pads)
        groups.append([clause + tuple(s * v for s, v in zip(signs, pads))
                       for signs in product((-1, 1), repeat=len(pads))])
    return groups


def guarded_formula(groups):
    fresh = max(abs(lit) for group in groups for clause in group for lit in clause) + 1
    formula, group_masks, bit_variables = [], [], []
    for group in groups:
        mask = 0
        for clause in group:
            witnesses = tuple(range(fresh, fresh + 3))
            guards = tuple(range(fresh + 3, fresh + 6))
            fresh += 6
            formula.append(witnesses)
            formula.extend((-guard, -w, lit) for guard, w, lit in zip(guards, witnesses, clause))
            mask |= 7 << len(bit_variables)
            bit_variables.extend(guards)
        group_masks.append(mask)
    return formula, group_masks, bit_variables


def scan_unsat(live):
    if not all(live[:2]):
        return False
    for i in range(2, len(live), 4):
        a, b, c, d = live[i:i + 4]
        if not ((a and b) or (c and d)):
            return False
    return True


def route_masks(r, group_masks):
    for branches in product((0, 1), repeat=r):
        mask = group_masks[0] | group_masks[1]
        for stage, branch in enumerate(branches):
            first = 2 + 4 * stage + 2 * branch
            mask |= group_masks[first] | group_masks[first + 1]
        yield mask


def truth_table_census(r):
    """Classify all source-clause subsets by explicit simultaneous assignments."""
    clauses = source(r)
    width = max(abs(lit) for row in clauses for lit in row)
    assignments = range(1 << width)
    masks = []
    for clause in clauses:
        states = 0
        for bits in assignments:
            if any(bool(bits & (1 << (abs(lit) - 1))) == (lit > 0) for lit in clause):
                states |= 1 << bits
        masks.append(states)
    feasible = [0] * (1 << len(clauses))
    feasible[0] = (1 << (1 << width)) - 1
    minimal = set()
    for subset in range(1, len(feasible)):
        bit = subset & -subset
        feasible[subset] = feasible[subset ^ bit] & masks[bit.bit_length() - 1]
        live = [bool(subset & (1 << i)) for i in range(len(clauses))]
        assert bool(feasible[subset]) != scan_unsat(live)
        if not feasible[subset] and all(feasible[subset ^ (1 << i)] for i, on in enumerate(live) if on):
            minimal.add(subset)
    assert minimal == set(route_masks(r, [1 << i for i in range(len(clauses))]))
    return {"stage_count": r, "source_activations": len(feasible), "minimal": len(minimal)}


def zero_certificates(group_masks):
    """Minimal sets of zero bits that hit every candidate contradiction."""
    def bits(mask):
        while mask:
            bit = mask & -mask
            yield bit
            mask ^= bit

    certificates = set(bits(group_masks[0] | group_masks[1]))
    for i in range(2, len(group_masks), 4):
        a, b, c, d = group_masks[i:i + 4]
        certificates.update(x | y for x in bits(a | b) for y in bits(c | d))
    return certificates


def adversary_check(group_masks, orders):
    full = 0
    for block in group_masks:
        full |= block
    branches = []
    for i in range(2, len(group_masks), 4):
        a, b, c, d = group_masks[i:i + 4]
        branches.append((a | b, c | d))

    def unsat(mask):
        return scan_unsat([mask & block == block for block in group_masks])

    for order in orders:
        ones = zeros = 0
        for j in order:
            # With all unknowns zero or one, both decisions still occur.
            assert not unsat(ones) and unsat(full ^ zeros)
            bit = 1 << j
            seen = ones | zeros | bit
            first_finished = False
            for left, right in branches:
                own, other = (left, right) if left & bit else (right, left)
                if own & bit:
                    first_finished = seen & own == own and seen & other != other
                    break
            if first_finished:
                zeros |= bit
            else:
                ones |= bit
        assert ones | zeros == full and unsat(ones)


def local_checks():
    total = 0
    for values in product((False, True), repeat=3):
        for guards in product((False, True), repeat=3):
            allowed = any(any(w) and all(not e or not v or x for e, v, x in zip(guards, w, values))
                          for w in product((False, True), repeat=3))
            assert allowed == (not all(guards) or any(values))
            total += 1
    for width in (1, 2):
        pad_patterns = list(product((0, 1), repeat=3 - width))
        for bits in range(1 << len(pad_patterns)):
            active = {word for i, word in enumerate(pad_patterns) if bits & (1 << i)}
            for original_satisfied in (False, True):
                extension = any(all(original_satisfied or pad != excluded for excluded in active)
                                for pad in pad_patterns)
                assert extension == (original_satisfied or bits != (1 << len(pad_patterns)) - 1)
                total += 1
    return total


def canonical_check(allowed):
    # Serialize the computed allowed table on this four-guard restriction.
    missing = set(product((0, 1), repeat=4)) - set(allowed)
    names = ("g1", "g2", "g3", "g4")
    cnf = ";".join(" ".join(("~" if v else "") + name for name, v in zip(names, row))
                   for row in sorted(missing))
    root = Path(__file__).resolve().parents[3]
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
            "--loops", *names[:3], "--contact", names[-1], "--json"]
    process = subprocess.run(args, cwd=root, env={**os.environ, "PYTHONPATH": str(root / "tools")},
                             text=True, capture_output=True, check=True)
    data = json.loads(process.stdout)
    assert data["erasure"] == "forgetting" and data["is_knot"] and len(data["allowed"]) == 15
    return len(data["allowed"])


def raw_sat_test():
    from pysat.solvers import Solver

    tested = 0
    rng = random.Random(41)
    for r in (1, 2, 4, 8):
        formula, blocks, guards = guarded_formula(strict_groups(source(r)))
        full = (1 << len(guards)) - 1
        routes = list(route_masks(r, blocks))
        with Solver(name="g3", bootstrap_with=formula) as solver:
            def check(mask):
                assumptions = [v if (mask >> j) & 1 else -v for j, v in enumerate(guards)]
                observed = solver.solve(assumptions=assumptions)
                expected = not scan_unsat([mask & block == block for block in blocks])
                assert observed == expected
                return observed

            examples = {0, full, *routes}
            examples.update(rng.getrandbits(len(guards)) for _ in range(32))
            for _ in range(64):
                mask = full
                for block in blocks:
                    if rng.randrange(4) == 0:
                        choices = [i for i in range(len(guards)) if block & (1 << i)]
                        mask &= ~(1 << rng.choice(choices))
                examples.add(mask)
            for mask in examples:
                check(mask)
            tested += len(examples)
            for mask in (routes[0], routes[-1]):
                for j in range(len(guards)):
                    if mask & (1 << j):
                        assert check(mask ^ (1 << j))
                        tested += 1
            if r == 1:
                mask = routes[0]
                chosen = [j for j in range(len(guards)) if mask & (1 << j)][:4]
                base = mask & ~sum(1 << j for j in chosen)
                allowed = [bits for bits in product((0, 1), repeat=4)
                           if check(base | sum(bit << j for bit, j in zip(bits, chosen)))]
                canonical_check(allowed)
                tested += 16
    return tested


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--with-solver", action="store_true")
    args = p.parse_args()
    census = [truth_table_census(i) for i in (1, 2, 3)]
    r = 8
    _, blocks, guards = guarded_formula(strict_groups(source(r)))
    routes = set(route_masks(r, blocks))
    common = (1 << len(guards)) - 1
    for mask in routes:
        common &= mask
    assert len(routes) == 2**r and {m.bit_count() for m in routes} == {12*r + 24}
    assert common.bit_count() == 24 and len(guards) == 24*r + 24
    rng = random.Random(73)
    order = list(range(len(guards)))
    orders = [order, list(reversed(order))] + [rng.sample(order, len(order)) for _ in range(8)]
    adversary_check(blocks, orders)
    sample = next(iter(routes))
    blockers = zero_certificates(blocks)
    assert len(blockers) == 24 + 144*r
    for zeros in blockers:
        assert all(zeros & route for route in routes)
        for j in range(len(guards)):
            if zeros & (1 << j):
                assert any(not ((zeros ^ (1 << j)) & route) for route in routes)
    for j in range(len(guards)):
        if sample & (1 << j):
            changed = sample ^ (1 << j)
            assert not scan_unsat([changed & block == block for block in blocks])
    # Dropping even one switch can break a complete route; neither counting
    # live endpoints nor merging the two branches into one tests reachability.
    assert scan_unsat([sample & block == block for block in blocks])
    edge = next(block for block in blocks[2:] if sample & block == block)
    broken = sample ^ (edge & -edge)
    assert not scan_unsat([broken & block == block for block in blocks])
    allowed = [bits for bits in product((0, 1), repeat=4) if not all(bits)]
    result = {"status": "passed", "local_cases": local_checks(), "source_censuses": census,
              "r8": {"obstructions": len(routes), "guards_each": 12*r + 24,
                     "guards_common": common.bit_count(), "guards_total": len(guards),
                     "minimal_zero_certificates": len(blockers), "sensitive_bits": sample.bit_count(),
                     "full_depth_orders_checked": len(orders)},
              "four_guard_restriction_allowed": canonical_check(allowed)}
    if args.with_solver:
        result["original_cnf_SAT_checks"] = raw_sat_test()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
