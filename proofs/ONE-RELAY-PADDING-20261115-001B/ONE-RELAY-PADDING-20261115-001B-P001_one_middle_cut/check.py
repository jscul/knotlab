"""Construct strict witnesses and independently check the two sharing operations."""

import importlib.util
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
BASE = (ROOT / "proofs/SIGNED-KNOT-OVERLAP-20261114-001C"
        / "SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/check.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def switches(edge_slots, endpoints=(True, True)):
    raw = bytearray()
    for on in endpoints:
        raw.extend([int(on)] * 12)
    # In the original generator the negative padding slot precedes the positive.
    for selected in edge_slots:
        for side in range(2):
            raw.extend([(selected >> side) & 1] * 3)
    return raw


def requirements(pad_names, raw):
    results = []
    for e, pad in enumerate(pad_names):
        start = 24 + 6 * e
        negative = all(raw[start:start + 3])
        positive = all(raw[start + 3:start + 6])
        if positive and negative:
            results.append(None)
        elif positive:
            results.append(pad + 1)
        elif negative:
            results.append(-(pad + 1))
        else:
            results.append(0)
    return results


class Demands:
    def __init__(self, number):
        self.counts = [[0, 0] for _ in range(number)]
        self.bad = 0

    def change(self, literal, amount):
        if literal is None:
            self.bad += amount
        elif literal:
            values = self.counts[abs(literal) - 1]
            was_conflict = all(values)
            values[int(literal > 0)] += amount
            self.bad += int(all(values)) - int(was_conflict)


def solve(shared, pad_names, raw):
    r = len(shared) // 2
    p = max(pad_names) + 1
    if not all(raw[:12]) or not all(raw[12:24]):
        value = int(all(raw[:12]))
        return [value] * (r + 1), [value] * (2 * r), [0] * p
    demand = requirements(pad_names, raw)
    for relay in (1, 0):
        base = Demands(p)
        order = reversed(range(r)) if relay else range(r)
        for cut in order:
            ordinary = []
            for position in (2 * cut, 2 * cut + 1):
                if shared[position]:
                    base.change(demand[2 * position + relay], 1)
                else:
                    ordinary.append(position)
            if base.bad:
                continue
            for halves in product((0, 1), repeat=len(ordinary)):
                selected = [demand[2 * index + half] for index, half in zip(ordinary, halves)]
                for literal in selected:
                    base.change(literal, 1)
                if not base.bad:
                    x = [int(i <= cut) for i in range(r + 1)]
                    mids = [relay if special else int(i // 2 < cut)
                            for i, special in enumerate(shared)]
                    for i, half in zip(ordinary, halves):
                        mids[i] = half
                    return x, mids, [int(count[1] > 0) for count in base.counts]
                for literal in selected:
                    base.change(literal, -1)
    return None


def source_ok(pad_names, raw, x, mids, pads):
    if (all(raw[:12]) and not x[0]) or (all(raw[12:24]) and x[-1]):
        return False
    for e, pad in enumerate(pad_names):
        position, half = divmod(e, 2)
        stage = position // 2
        left, right = (mids[position], x[stage + 1]) if half else (x[stage], mids[position])
        if left and not right:
            start = 24 + 6 * e
            # A true pad falsifies its negative literal, and conversely.
            falsified = start if pads[pad] else start + 3
            if all(raw[falsified:falsified + 3]):
                return False
    return True


def brute(shared, pad_names, raw):
    r = len(shared) // 2
    keys = ["J" if special else i for i, special in enumerate(shared)]
    names = list(dict.fromkeys(keys))
    for x in product((0, 1), repeat=r + 1):
        if (all(raw[:12]) and not x[0]) or (all(raw[12:24]) and x[-1]):
            continue
        for values in product((0, 1), repeat=len(names)):
            assigned = dict(zip(names, values))
            mids = [assigned[key] for key in keys]
            for pads in product((0, 1), repeat=max(pad_names) + 1):
                if source_ok(pad_names, raw, x, mids, pads):
                    return True
    return False


def partitions(n, initial=(0,)):
    if len(initial) == n:
        yield initial
    else:
        for j in range(max(initial) + 2):
            yield from partitions(n, (*initial, j))


def base_module():
    spec = importlib.util.spec_from_file_location("guarded_routes", BASE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StrictInstance:
    def __init__(self, old, shared, pad_names):
        self.shared = shared
        self.pad_names = pad_names
        r = len(shared) // 2
        groups = old.strict_groups(old.source(r))
        formula, _, self.guards = old.guarded_formula(groups)
        self.middle_ids = list(range(r + 2, 3 * r + 2))
        self.pad_ids = {}
        rename = {}
        if any(shared):
            relay_id = self.middle_ids[shared.index(True)]
            rename.update({v: relay_id for i, v in enumerate(self.middle_ids) if shared[i]})
        for e, name in enumerate(pad_names):
            v = abs(groups[e + 2][0][-1])
            self.pad_ids.setdefault(name, v)
            rename[v] = self.pad_ids[name]
        self.middle_ids = [rename.get(v, v) for v in self.middle_ids]

        def renamed(clause):
            return tuple((1 if lit > 0 else -1) * rename.get(abs(lit), abs(lit)) for lit in clause)

        self.formula = [renamed(c) for c in formula]
        self.slots = [renamed(c) for group in groups for c in group]
        self.endpoint_pads = [tuple(map(abs, group[0][1:])) for group in groups[:2]]
        require(all(len(set(map(abs, c))) == 3 for c in self.formula), "strict clause lost arity")

    def witness(self, raw, solution):
        x, mids, pads = solution
        env = dict(zip(range(1, len(x) + 1), x))
        for v, value in zip(self.middle_ids, mids):
            require(v not in env or env[v] == value, "inconsistent identified middle in witness")
            env[v] = value
        for name, var in self.pad_ids.items():
            env[var] = pads[name]
        env.update(zip(self.guards, raw))

        def holds(lit):
            return bool(env[abs(lit)]) == (lit > 0)

        for unit, private in enumerate(self.endpoint_pads):
            for values in product((0, 1), repeat=2):
                env.update(zip(private, values))
                if all(not all(raw[3*i:3*i + 3]) or any(map(holds, self.slots[i]))
                       for i in range(4 * unit, 4 * unit + 4)):
                    break
            else:
                raise AssertionError("endpoint padding cannot extend the returned source model")
        for i, literals in enumerate(self.slots):
            ws = self.formula[4 * i]
            chosen = next((j for j, lit in enumerate(literals) if not raw[3 * i + j] or holds(lit)), None)
            require(chosen is not None, "active strict slot has no witness")
            env.update((w, int(j == chosen)) for j, w in enumerate(ws))
        require(all(abs(lit) in env for c in self.formula for lit in c), "partial strict assignment")
        require(all(any(map(holds, c)) for c in self.formula), "full strict assignment violates a clause")
        require(all(env[v] == b for v, b in zip(self.guards, raw)), "witness changed a supplied switch")
        return env


def check_solution(shared, pads, raw, answer):
    if answer is not None:
        x, mids, values = answer
        require(len({m for m, special in zip(mids, shared) if special}) <= 1, "middle split")
        require(source_ok(pads, raw, x, mids, values), "returned source assignment is invalid")
        require(all(a >= b for a, b in zip(x, x[1:])), "returned boundaries are not normalized")


def check_small(old):
    count = witnesses = 0
    for shared in ((False, False), (True, True)):
        for pads in partitions(4):
            strict = StrictInstance(old, shared, pads)
            for selected in product(range(4), repeat=4):
                raw = switches(selected)
                answer = solve(shared, pads, raw)
                require((answer is not None) == brute(shared, pads, raw), "exhaustive one-stage decisions")
                check_solution(shared, pads, raw, answer)
                if answer:
                    strict.witness(raw, answer)
                    witnesses += 1
                count += 1
    return count, witnesses


def example(split_middle=False, split_pad=False):
    shared = (not split_middle, False, not split_middle, False)
    pads = [0, 1, 2, 3, 4, 5 if split_pad else 1, 6, 7]
    # D|z is the positive slot (2); D|~z is the negative slot (1).
    raw = switches([3, 2, 0, 0, 0, 1, 3, 3])
    return shared, pads, raw


def check_example(old):
    shared, pads, raw = example()
    strict = StrictInstance(old, shared, pads)
    require(sum(raw) == 48 and solve(shared, pads, raw) is None and not brute(shared, pads, raw),
            "the 48-switch obstruction is feasible")
    coordinate_witnesses = 0
    for i, selected in enumerate(raw):
        if selected:
            reduced = raw.copy()
            reduced[i] = 0
            answer = solve(shared, pads, reduced)
            require(answer is not None, "one of the 48 switches was redundant")
            strict.witness(reduced, answer)
            coordinate_witnesses += 1
    for split_j, split_z in ((True, False), (False, True), (True, True)):
        sh, ps, same_input = example(split_j, split_z)
        require(same_input == raw, "split changed switch assignments")
        answer = solve(sh, ps, same_input)
        require(answer is not None, "splitting an identity failed to restore SAT")
        StrictInstance(old, sh, ps).witness(raw, answer)
    return coordinate_witnesses


def check_cut_orientation(old):
    shared = (True, False) * 3
    pads = (0,) * 12
    strict = StrictInstance(old, shared, pads)
    unnormalized_x = [1, 0, 1, 0]
    # J=1 requires old x2=true, so the last true boundary is needed.
    # J=0 requires old x1=false, so the first false boundary is needed.
    for relay, required, expected in [(1, (0, 5), [1, 1, 1, 0]), (0, (4, 9), [1, 0, 0, 0])]:
        selected = [3 if e in required else 0 for e in range(12)]
        raw = switches(selected)
        original = (unnormalized_x, [relay, 0] * 3, [0])
        strict.witness(raw, original)
        normalized = solve(shared, pads, raw)
        require(normalized is not None and normalized[0] == expected and normalized[1][0] == relay,
                "wrong direction for normalized cuts")
        strict.witness(raw, normalized)
    return 2


def check_all_two_stage_slots():
    shared, _, _ = example()
    # The same two positions share z as in the 48-switch example, with all
    # other pads distinct. Enumerate actual source/pad assignments first.
    pads = (0, 1, 2, 3, 4, 1, 5, 6)
    forbidden_masks = set()
    for x1, relay, b1, b2 in product((0, 1), repeat=4):
        x, mids = (1, x1, 0), (relay, b1, relay, b2)
        false_edges = []
        for position, middle in enumerate(mids):
            stage = position // 2
            if x[stage] and not middle:
                false_edges.append(2 * position)
            if middle and not x[stage + 1]:
                false_edges.append(2 * position + 1)
        for z in product((0, 1), repeat=7):
            forbidden_masks.add(sum(1 << (2 * e + (1 - z[pads[e]])) for e in false_edges))
    count = 1 << 16
    full = (1 << count) - 1
    allows_off = []
    for i in range(16):
        size = 1 << i
        repeats = full // ((1 << (2 * size)) - 1)
        allows_off.append(((1 << size) - 1) * repeats)
    feasible = 0
    for bad in forbidden_masks:
        accepted = full
        for i in range(16):
            if bad >> i & 1:
                accepted &= allows_off[i]
        feasible |= accepted
    direct = feasible.to_bytes(count // 8, "little")
    for active in range(count):
        raw = switches([(active >> (2 * e)) & 3 for e in range(8)])
        answer = solve(shared, pads, raw)
        expected = bool(direct[active >> 3] >> (active & 7) & 1)
        require((answer is not None) == expected, "two-stage exhaustive slot mismatch")
        check_solution(shared, pads, raw, answer)
    return count


def check_more(old):
    rng = random.Random(3903)
    tested = built = 0
    for r, samples in ((2, 130), (3, 36)):
        for _ in range(samples):
            shared = tuple(bool(rng.randrange(2)) for _ in range(2 * r))
            pads = tuple(rng.randrange(3) for _ in range(4 * r))
            selected = [rng.choice((0, 1, 1, 2, 2, 3, 3)) for _ in range(4 * r)]
            raw = switches(selected)
            for i in range(24, len(raw), 3):
                if raw[i] == 0:
                    incomplete = rng.randrange(7)
                    raw[i:i + 3] = bytes((incomplete >> j) & 1 for j in range(3))
            if rng.randrange(4) == 0:
                raw[rng.randrange(24)] = 0
            answer = solve(shared, pads, raw)
            require((answer is not None) == brute(shared, pads, raw), "interstage pad truth-table mismatch")
            check_solution(shared, pads, raw, answer)
            if answer:
                StrictInstance(old, shared, pads).witness(raw, answer)
                built += 1
            tested += 1
    # There is only one feasible cut, far from the end; many later occurrences
    # demand the same positive pad, and the ordinary cut demands another false.
    r, cut = 4096, 1365
    shared = (True, False) * r
    pads = (1, 0, 1, 1) * r
    selected = []
    for stage in range(r):
        selected.extend((3, 3 if stage < cut else 2, 1 if stage == cut else 3, 3))
    raw = switches(selected)
    answer = solve(shared, pads, raw)
    require(answer is not None and sum(answer[0]) == cut + 1 and answer[1][0] == 1,
            "repeated-pad cut at large size")
    check_solution(shared, pads, raw, answer)
    return tested, built, r


def raw_oracle():
    from pysat.solvers import Solver

    old = base_module()
    tested = 0
    for split_j, split_z in product((False, True), repeat=2):
        shared, pads, raw = example(split_j, split_z)
        strict = StrictInstance(old, shared, pads)
        with Solver(name="g3", bootstrap_with=strict.formula) as solver:
            cases = [raw]
            if not split_j and not split_z:
                for j, on in enumerate(raw):
                    if on:
                        reduced = raw.copy()
                        reduced[j] = 0
                        cases.append(reduced)
            for data in cases:
                pins = [v if on else -v for v, on in zip(strict.guards, data)]
                actual = solver.solve(assumptions=pins)
                require(actual == (solve(shared, pads, data) is not None), "raw SAT solver mismatch")
                tested += 1
            if not split_j and not split_z:
                chosen = (2, 24, 33, 60)
                require(all(raw[i] for i in chosen), "slice contains a switch outside the obstruction")
                allowed = []
                for row in product((0, 1), repeat=4):
                    restricted = raw.copy()
                    for j, value in zip(chosen, row):
                        restricted[j] = value
                    assumption = [v if on else -v for v, on in zip(strict.guards, restricted)]
                    if solver.solve(assumptions=assumption):
                        allowed.append(row)
                    tested += 1
                require(old.canonical_check(allowed) == 15, "canonical four-switch slice")
    rng = random.Random(438)
    for r in (1, 2, 4, 9):
        shared = tuple(i % 3 != 1 for i in range(2 * r))
        pads = tuple(rng.randrange(3) for _ in range(4 * r))
        strict = StrictInstance(old, shared, pads)
        with Solver(name="g3", bootstrap_with=strict.formula) as solver:
            for _ in range(45):
                raw = switches([rng.choice((0, 1, 2, 3, 3)) for _ in range(4 * r)])
                if rng.randrange(5) == 0:
                    raw[rng.randrange(24)] = 0
                answer = solve(shared, pads, raw)
                pins = [v if on else -v for v, on in zip(strict.guards, raw)]
                require(solver.solve(assumptions=pins) == (answer is not None), "raw larger solver mismatch")
                if answer:
                    strict.witness(raw, answer)
                tested += 1
    return tested


def installed_oracle():
    if importlib.util.find_spec("pysat") is not None:
        return raw_oracle()
    python = ROOT / ".venv/bin/python"
    probe = "import importlib.util,sys; sys.exit(importlib.util.find_spec('pysat') is None)"
    if python.is_file() and subprocess.run([str(python), "-B", "-c", probe]).returncode == 0:
        return int(subprocess.check_output([str(python), "-B", __file__, "--raw"], text=True))
    return 0


def main():
    old = base_module()
    cases, witnesses = check_small(old)
    essential = check_example(old)
    orientations = check_cut_orientation(old)
    two_stage_census = check_all_two_stage_slots()
    larger, more_witnesses, size = check_more(old)
    return {
        "status": "passed",
        "exhaustive_one_stage_switch_and_alias_cases": cases,
        "one_stage_full_strict_witnesses": witnesses,
        "two_and_three_stage_truth_table_cases": larger,
        "exhaustive_two_stage_activations_on_interaction_wiring": two_stage_census,
        "two_and_three_stage_full_strict_witnesses": more_witnesses,
        "essential_switches_in_joint_example": essential,
        "identity_splitting_controls_restoring_sat": 3,
        "nonmonotone_models_normalized_in_the_forced_direction": orientations,
        "stages_in_repeated_pad_stress_case": size,
        "raw_strict_sat_oracle_cases": installed_oracle(),
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--raw"]:
        print(raw_oracle())
    else:
        print(json.dumps(main(), indent=2, sort_keys=True))
