"""Focused synthetic checks for interface inference, physical sharing and counters."""

import random
from itertools import combinations

from checker import JointChecker
from joint_solver import DEFAULT_ENTRY, PINS, JointSolver, _Physical


def packed(n, fn):
    return sum(int(fn(tuple((row >> i) & 1 for i in range(n)))) << row for row in range(1 << n))


def scalar_minimum(n, targets):
    all_rows = range(1 << n)
    shared = [axis for axis in range(n)
              if all(any(((t >> row) ^ (t >> (row ^ (1 << axis)))) & 1 for row in all_rows)
                     for t in targets)]
    best = None
    for group in combinations(shared, 3):
        outside = [axis for axis in range(n) if axis not in group]
        residuals = set()
        for local in range(8):
            offset = sum(((local >> i) & 1) << g for i, g in enumerate(group))
            columns = []
            for z in range(1 << len(outside)):
                row = offset | sum(((z >> i) & 1) << axis for i, axis in enumerate(outside))
                columns.append(tuple((t >> row) & 1 for t in targets))
            residuals.add(tuple(columns))
        candidate = ((len(residuals) - 1).bit_length(), group, len(residuals))
        if best is None or candidate < best:
            best = candidate
    return best


def check():
    rng = random.Random(412493)
    checked = 0
    widths, class_counts = set(), set()
    for n in (3, 4, 6, 7):
        engines = [JointSolver(n, arm) for arm in ("primitive", "named", "flat")]
        checker = JointChecker(n)
        cases = [(rng.getrandbits(1 << n), rng.getrandbits(1 << n)) for _ in range(14)]
        cases.append((0, 0))
        for order in ((0, 1, 2), (2, 0, 1), (1, 2, 0)):
            group = (0, n // 2, n - 1)
            x, y, z = (group[i] for i in order)
            other = [g for g in range(n) if g not in group]
            def h(s):
                return s[x] ^ (s[y] & s[z])
            cases.append((packed(n, lambda s: h(s) ^ (s[other[0]] if other else 0)),
                          packed(n, lambda s: h(s) | (s[other[-1]] if other else 0))))
        for targets in cases:
            expected = scalar_minimum(n, targets)
            returned = [e.solve(targets) for e in engines]
            for answer in returned:
                if expected is None:
                    assert answer["status"] == "no_eligible_triple"
                    continue
                assert (answer["width"], tuple(answer["triple"]), answer["class_count"]) == expected
                receipt = checker.verify(targets, answer)
                assert receipt["active_gates"] == len(answer["circuit"]["gates"])
                assert receipt["shared_gates"] == answer["shared_gates"]
                assert receipt["shared_summary_wires"] == answer["shared_summary_wires"]
                w = answer["work"]
                assert w["fold_group_hypotheses"] == w["fold_group_rejections"] + w["fold_group_hits"]
                assert w["group_trials"] == w["group_incumbents"] + w["group_failures"]
                widths.add(answer["width"])
                class_counts.add(answer["class_count"])
                checked += 1
            assert returned[1]["circuit"] == returned[2]["circuit"]
            assert returned[1]["fold_uses"] == returned[2]["fold_uses"]
        repeated = engines[1].solve(cases[-1])
        assert repeated["work"]["group_cache_hits"] == 1 and repeated["work"]["group_trials"] == 0
        assert repeated["fold_uses"] == repeated["shared_summary_wires"] == 1
    assert widths == {1, 2, 3} and {2, 3, 4, 8} <= class_counts

    engine = JointSolver(6)
    for arity in (1, 2, 3, 4, 5, 6):
        mask = (1 << (1 << arity)) - 1
        tables = range(mask + 1) if arity <= 3 else (rng.getrandbits(1 << arity) for _ in range(60))
        for table in tables:
            physical = _Physical(engine)
            end = physical.build(engine._recipe(arity, table), tuple(range(arity)))
            assert physical.values[end] & mask == table

    alternate = {"truth": PINS[0] & (PINS[1] ^ PINS[2]),
                 "expr": ("AND", ("input", 0), ("XOR", ("input", 1), ("input", 2)))}
    h = packed(5, lambda x: x[4] & (x[2] ^ x[1]))
    a, b = (packed(5, lambda x: x[0]), packed(5, lambda x: x[3]))
    ans = JointSolver(5, "flat", alternate).solve(h ^ a, h | b)
    assert ans["fold_uses"] == 1
    JointChecker(5).verify((h ^ a, h | b), ans)
    try:
        JointSolver(5, "named", DEFAULT_ENTRY, {"gates": [[0, 1]], "output": 5})
    except ValueError:
        pass
    else:
        raise AssertionError("wrong physical binding accepted")
    return checked


if __name__ == "__main__":
    print(f"{check()} synthetic joint programs and all primitive truth masks through three inputs passed.")
