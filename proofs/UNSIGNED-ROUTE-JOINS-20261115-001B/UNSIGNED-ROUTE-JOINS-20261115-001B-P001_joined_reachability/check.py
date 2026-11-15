"""Test positive middle-name identifications on the committed strict-switch encoding."""

import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PREDECESSOR = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
               / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def predecessor():
    spec = importlib.util.spec_from_file_location("unjoined_two_routes", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def partitions(length, initial=(0,)):
    if len(initial) == length:
        yield initial
    else:
        for label in range(max(initial) + 2):
            yield from partitions(length, (*initial, label))


def edges(labels):
    stages = len(labels) // 2
    result = []
    for pos, label in enumerate(labels):
        stage = pos // 2
        middle = stages + 1 + label
        result.extend([(stage, middle), (middle, stage + 1)])
    return result


def reach(occurrences, live, target):
    adjacency = {}
    for i, (u, v) in enumerate(occurrences):
        if (live >> i) & 1:
            adjacency.setdefault(u, []).append(v)
    reached, pending = {0}, [0]
    while pending:
        for v in adjacency.get(pending.pop(), ()):
            if v not in reached:
                reached.add(v)
                pending.append(v)
    return target in reached


def simple_paths(occurrences, target):
    paths = set()

    def visit(u, seen, mask):
        if u == target:
            paths.add(mask)
            return
        for i, (left, right) in enumerate(occurrences):
            if left == u and right not in seen:
                visit(right, seen | {right}, mask | (1 << i))

    visit(0, {0}, 0)
    return paths


class ActivationTables:
    """One bit-table position for each assignment to the implication activations."""

    def __init__(self, r):
        self.r = r
        self.number = 1 << (4 * r)
        self.full = (1 << self.number) - 1
        self.on = []
        for i in range(4 * r):
            run = 1 << i
            repeat = self.full // ((1 << (2 * run)) - 1)
            self.on.append((((1 << run) - 1) << run) * repeat)
        self.old_scan = self.full
        self.stage_patterns = []
        for start in range(0, 4 * r, 4):
            a, b, c, d = self.on[start:start + 4]
            self.old_scan &= (a & b) | (c & d)
            patterns = []
            for value in range(16):
                accepted = self.full
                for j in range(4):
                    on = self.on[start + j]
                    accepted &= on if value >> j & 1 else ~on
                patterns.append(accepted)
            self.stage_patterns.append(patterns)

    def truth_by_assignments(self, occurrences):
        width = max(max(pair) for pair in occurrences) + 1
        feasible = 0
        for x in range(1 << width):
            if not (x & 1) or x >> self.r & 1:
                continue
            permitted = self.full
            for i, (u, v) in enumerate(occurrences):
                if x >> u & 1 and not (x >> v & 1):
                    permitted &= ~self.on[i]
            feasible |= permitted
        return self.full ^ feasible

    def truth_by_reachability(self, occurrences):
        reached = [0] * (1 + max(max(pair) for pair in occurrences))
        reached[0] = self.full
        while True:
            previous = reached.copy()
            for i, (u, v) in enumerate(occurrences):
                reached[v] |= reached[u] & self.on[i]
            if previous == reached:
                return reached[self.r]

    def product_of_stage_projections(self, lookup):
        product_table = self.full
        for i, patterns in enumerate(self.stage_patterns):
            full_except_one = (self.number - 1) ^ (15 << (4 * i))
            available = 0
            for value, pattern in enumerate(patterns):
                if lookup(full_except_one | (value << (4 * i))):
                    available |= pattern
            product_table &= available
        return product_table


def audit_partition(labels, tables, audit_residuals=True):
    r = len(labels) // 2
    arcs = edges(labels)
    truth = tables.truth_by_assignments(arcs)
    require(truth == tables.truth_by_reachability(arcs), "reachability disagrees with Boolean models")
    require(tables.old_scan & ~truth == 0, "a complete old route disappeared")
    require((truth == tables.old_scan) == (len(set(labels)) == len(labels)),
            "wrong classification for preserving the old scan")
    packed = truth.to_bytes((tables.number + 7) // 8, "little")

    def unsat(mask):
        return (packed[mask >> 3] >> (mask & 7)) & 1

    minimal = set()
    for mask in range(tables.number):
        if not unsat(mask):
            continue
        bits = mask
        while bits:
            bit = bits & -bits
            if unsat(mask ^ bit):
                break
            bits ^= bit
        else:
            minimal.add(mask)
    paths = simple_paths(arcs, r)
    require(paths == minimal, "occurrence paths differ from minimal contradictions")
    one_bit = tables.product_of_stage_projections(unsat) == truth
    widths = []
    if audit_residuals:
        for cut in range(1, r):
            first = 1 << (4 * cut)
            residuals = set()
            for prefix in range(first):
                row = sum(unsat(prefix | (suffix * first)) << suffix
                          for suffix in range(tables.number // first))
                residuals.add(row)
            widths.append(len(residuals))
            early_mask = first - 1
            splices_work = all(unsat((p & early_mask) | (q & ~early_mask)) for p in paths for q in paths)
            require(0 in residuals and splices_work == (len(residuals) <= 2),
                    "cut splicing disagrees with the direct residual census")
        require(one_bit == all(w <= 2 for w in widths), "one-bit scan differs from stage conjunction")
    return one_bit, widths, len(paths)


def strict_instance(old, labels):
    """Identify only original middles, after constructing the untouched guarded CNF."""
    r = len(labels) // 2
    formula, blocks, guards = old.guarded_formula(old.strict_groups(old.source(r)))
    renamed = {r + 2 + j: r + 2 + labels.index(name) for j, name in enumerate(labels)}
    renamed_formula = [tuple((1 if lit > 0 else -1) * renamed.get(abs(lit), abs(lit))
                             for lit in clause) for clause in formula]
    require(all(len(set(map(abs, clause))) == 3 for clause in renamed_formula), "strict arity")
    return renamed_formula, blocks, guards


def raw_solver():
    from pysat.solvers import Solver

    old = predecessor()
    cases = [
        ((0, 0), (0, 3)),
        ((0, 1, 0, 2), (0, 5)),
        ((0, 1, 0, 2, 2, 1), (0, 3, 5, 6, 9, 10)),
        ((0, 1, 2, 3, 4, 5, 6, 7, 8, 0), (0, 19)),
    ]
    tested, raw_max_stages = 0, 0
    for labels, selected in cases:
        r = len(labels) // 2
        formula, blocks, guards = strict_instance(old, labels)
        live = sum(1 << i for i in selected)
        route = blocks[0] | blocks[1]
        for i in selected:
            route |= blocks[i + 2]
        require(route.bit_count() == 24 + 6 * len(selected), "private groups were merged")
        arcs = edges(labels)
        with Solver(name="g3", bootstrap_with=formula) as solver:
            def check(mask):
                nonlocal tested
                values = [mask & block == block for block in blocks]
                active = sum(int(on) << j for j, on in enumerate(values[2:]))
                expected = not (values[0] and values[1] and reach(arcs, active, r))
                pins = [v if mask >> j & 1 else -v for j, v in enumerate(guards)]
                observed = solver.solve(assumptions=pins)
                require(observed == expected, "strict guarded CNF disagrees with reachability")
                tested += 1
                return observed

            require(not check(route), "claimed live bypass is satisfiable")
            require(not old.scan_unsat([True, True, *(bool(live >> i & 1) for i in range(4 * r))]),
                    "wrong scan already saw the bypass")
            for j in range(len(guards)):
                if route >> j & 1:
                    require(check(route ^ (1 << j)), "the raw obstruction has a redundant switch")
            if r == 3:
                require(len(simple_paths([arcs[i] for i in selected], r)) == 1,
                        "the backward witness has an alternate route")
                successor = dict(arcs[i] for i in selected)
                chain = [0]
                while chain[-1] in successor:
                    chain.append(successor[chain[-1]])
                    require(len(chain) <= len(selected) + 1, "unexpected cycle in backward example")
                require([v for v in chain if v <= r] == [0, 2, 1, 3],
                        "the sole raw path did not require a backward boundary step")
                allowed = []
                chosen = [j for j in range(len(guards)) if route >> j & 1][:4]
                base = route & ~sum(1 << j for j in chosen)
                for bits in product((0, 1), repeat=4):
                    if check(base | sum(bit << j for bit, j in zip(bits, chosen))):
                        allowed.append(bits)
                old.canonical_check(allowed)
        raw_max_stages = max(raw_max_stages, r)
    tied_guards_tested = 0
    formula, blocks, guards = strict_instance(old, (0, 1))
    with Solver(name="g3", bootstrap_with=formula) as solver:
        # In the first case B's route image is properly contained in A's.
        # The second case makes the two original route images equal.
        for aliases, wanted in [((0, 0, 1, 2, 1, 1), {3}), ((0, 0, 1, 2, 1, 2), {7})]:
            contradictory = set()
            for input_mask in range(8):
                expanded = 0
                for group, label in zip(blocks, aliases):
                    if input_mask >> label & 1:
                        expanded |= group
                switches = [v if expanded >> j & 1 else -v for j, v in enumerate(guards)]
                actual = not solver.solve(assumptions=switches)
                require(actual == old.scan_unsat([expanded & block == block for block in blocks]),
                        "identifying only public guards broke the stage scan")
                if actual:
                    contradictory.add(input_mask)
                tied_guards_tested += 1
            minimal = {m for m in contradictory if all((m ^ (1 << i)) not in contradictory
                       for i in range(3) if m >> i & 1)}
            require(minimal == wanted, "guard alias images were not minimized")
    return {"raw_strict_solver_cases": len(cases), "raw_strict_switch_vectors": tested,
            "raw_guard_alias_inputs": tied_guards_tested, "largest_raw_strict_stage_count": raw_max_stages}


def run_raw_with_installed_solver():
    if importlib.util.find_spec("pysat") is not None:
        return raw_solver()
    python = ROOT / ".venv/bin/python"
    if python.is_file():
        check = "import importlib.util,sys; sys.exit(importlib.util.find_spec('pysat') is None)"
        if subprocess.run([str(python), "-B", "-c", check]).returncode == 0:
            return json.loads(subprocess.check_output([str(python), "-B", __file__, "--raw"], text=True))
    return {"raw_strict_solver_cases": 0, "raw_strict_switch_vectors": 0,
            "raw_guard_alias_inputs": 0, "largest_raw_strict_stage_count": 0}


def main():
    counts, models, one_bit_counts = [], 0, []
    for r in (1, 2, 3):
        tables = ActivationTables(r)
        count = one = old_correct = 0
        for labels in partitions(2 * r):
            is_one_bit, _, _ = audit_partition(labels, tables)
            count += 1
            one += is_one_bit
            old_correct += len(set(labels)) == len(labels)
        require(old_correct == 1, "the original scan has extra all-input survivors")
        counts.append(count)
        one_bit_counts.append(one)
        models += count * tables.number
    require(counts == [2, 15, 203], "not all small partitions were visited")
    two = ActivationTables(2)
    require(audit_partition((0, 1, 0, 2), two)[1] == [4], "four distinguishable residuals")
    require(audit_partition((0, 0, 0, 0), two)[1] == [2], "all-middle-equal one-bit control")
    require(audit_partition((0, 0), ActivationTables(1))[2] == 4, "parallel occurrences collapsed")
    larger = (0, 1, 0, 2, 2, 1, 3, 4)
    audit_partition(larger, ActivationTables(4), audit_residuals=False)
    result = {
        "status": "passed",
        "middle_partitions_exhausted_through_three_stages": sum(counts),
        "source_edge_activations_exhausted_through_three_stages": models,
        "all_one_bit_partitions_r1": one_bit_counts[0],
        "all_one_bit_partitions_r2": one_bit_counts[1],
        "all_one_bit_partitions_r3": one_bit_counts[2],
        "four_stage_edge_activations": 65536,
        "two_stage_single_interstage_join_residuals": 4,
        "two_stage_all_middle_equal_residuals": 2,
    }
    return {**result, **run_raw_with_installed_solver()}


if __name__ == "__main__":
    report = raw_solver() if sys.argv[1:] == ["--raw"] else main()
    print(json.dumps(report, indent=2, sort_keys=True))
