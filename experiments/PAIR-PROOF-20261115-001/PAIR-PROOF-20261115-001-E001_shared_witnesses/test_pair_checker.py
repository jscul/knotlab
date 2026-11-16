"""Synthetic proof reuse, exact fallback, current-data and profiling checks."""

from copy import deepcopy
from itertools import combinations
from pathlib import Path
import random
import sys

from pair_checker import HistoricalChecker, PairChecker

ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = ROOT / "experiments/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits"
JOINT = ROOT / "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
sys.path[:0] = [str(PREVIOUS), str(JOINT)]
from joint_solver import JointSolver
from wire_return import attach_physical


class NANDs:
    def __init__(self, m):
        self.m, self.gates = m, []

    def nand(self, a, b):
        self.gates.append([a, b])
        return self.m + 1 + len(self.gates)

    def xor(self, a, b):
        h = self.nand(a, b)
        return self.nand(self.nand(a, h), self.nand(b, h))


def fixture():
    m, n = 5, 7
    stage = NANDs(m)
    u = stage.xor(stage.xor(0, 1), 4)
    v = stage.xor(stage.xor(2, 3), 4)
    h = stage.nand(u, v)
    output0 = stage.nand(h, h)
    output1 = stage.nand(stage.nand(u, u), stage.nand(v, v))
    frontier = [10, 1, 2, 3, 4]
    gates = [[0, 5], [9, 6]]
    wires = frontier + [n, n + 1]
    for a, b in stage.gates:
        gates.append([wires[a], wires[b]])
        wires.append(n + 1 + len(gates))
    return dict(id="synthetic-pair-parent", n=n, upstream_count=2, frontier=frontier,
                gates=gates, outputs=[wires[output0], wires[output1]], pieces=[])


def scalar_tables(case):
    n, m = case["n"], len(case["frontier"])
    seen = {}
    for assignment in range(1 << n):
        values = [*((assignment >> i) & 1 for i in range(n)), 0, 1]
        for a, b in case["gates"]:
            values.append(1 ^ (values[a] & values[b]))
        row = sum(values[wire] << i for i, wire in enumerate(case["frontier"]))
        outputs = tuple(values[wire] for wire in case["outputs"])
        assert row not in seen or seen[row] == outputs
        seen[row] = outputs
    assert len(seen) == 1 << m
    return tuple(sum(seen[row][output] << row for row in range(1 << m)) for output in range(2))


def classes(m, outputs, group):
    outside = [i for i in range(m) if i not in group]
    columns = set()
    for local in range(8):
        base = sum(((local >> j) & 1) << axis for j, axis in enumerate(group))
        column = []
        for rest in range(1 << len(outside)):
            row = base | sum(((rest >> j) & 1) << axis for j, axis in enumerate(outside))
            column.append(tuple((table >> row) & 1 for table in outputs))
        columns.add(tuple(column))
    return len(columns)


def labels(outputs, a, b, base=0):
    return [tuple((table >> (base | ((corner & 1) << a) | ((corner >> 1) << b))) & 1
                  for table in outputs) for corner in range(4)]


def history_for(outputs, m):
    proofs, faces = [], []
    for a, b in combinations(range(m), 2):
        values = labels(outputs, a, b)
        chosen, seen = 0, set()
        for corner, value in enumerate(values):
            if value not in seen and len(seen) < 3:
                chosen |= 1 << corner
                seen.add(value)
        face = [0, chosen] if len(seen) >= 3 else None
        faces.append(face)
        if face is not None:
            proofs.append([a, b, *face])
    return dict(schema=1, m=m, strategy="scalar", tables=list(outputs), proofs=proofs, faces=faces)


def rejected(fn, text):
    try:
        fn()
    except ValueError as error:
        assert text in str(error), str(error)
    else:
        raise AssertionError("invalid witness was accepted")


def check():
    case = fixture()
    tables = scalar_tables(case)
    result = JointSolver(5).solve(tables)
    assert result["width"] == 2
    answer = attach_physical(case, result)
    baseline = HistoricalChecker(case).verify(None, answer)
    no_proof = PairChecker(case).verify(None, answer)
    assert no_proof["pair_no_proof_fast_path"]
    assert no_proof["alternative_exact_checks_actual"] == baseline["global_minimum_alternative_groups_checked"]
    assert no_proof["alternative_exact_checks_avoided"] == 0
    assert no_proof["minimum_phase_cpu_ns"] > 0
    assert no_proof["alternative_checks_cpu_ns"] > 0
    assert no_proof["stage_program_and_cut_cpu_ns"] > 0
    assert no_proof["optimistic_no_minimum_is_certified"] is False
    assert no_proof["minimum_phase_cpu_ns"] + no_proof["verification_remainder_cpu_ns"] == no_proof["verification_cpu_ns"]

    # One certificate licenses multiple triples; an exact duplicate is read
    # once.  The independent second face reuses two current raw observations.
    proofs = [[0, 2, 0], [0, 2, 0], [0, 3, 0]]
    supplied = dict(answer, pair_proofs=proofs)
    paid = PairChecker(case).verify(None, supplied)
    chosen = tuple(sorted(answer["triple"]))
    covered = sum(group != chosen and (set((0, 2)) <= set(group) or set((0, 3)) <= set(group))
                  for group in combinations(range(5), 3))
    assert paid["pair_proof_unique_certificates_checked"] == 2
    assert paid["pair_proof_successes"] == 2
    assert paid["pair_proof_duplicate_certificates"] == 1
    assert paid["pair_proof_row_requests"] == 8
    assert paid["pair_proof_raw_rows_read"] == paid["pair_proof_distinct_rows"] == 6
    assert paid["pair_proof_row_cache_hits"] == 2
    assert paid["alternative_exact_checks_avoided"] == covered >= 2
    assert paid["chosen_group_exact_checks"] == 1
    assert paid["alternative_exact_checks_actual"] + covered == baseline["global_minimum_alternative_groups_checked"]
    assert paid["minimum_phase_cpu_ns"] >= paid["alternative_checks_cpu_ns"] >= paid["pair_proof_verification_cpu_ns"]
    assert paid["pair_proof_coverage_unions"] == 2
    assert paid["global_minimum_alternative_groups_certified"] == baseline["global_minimum_alternative_groups_checked"]
    assert paid["optimistic_no_alternative_cpu_floor_ns"] + paid["alternative_checks_cpu_ns"] == paid["verification_cpu_ns"]

    three = PairChecker(case).verify(None, dict(answer, pair_proofs=[[0, 2, 0, 11]]))
    assert three["pair_proof_raw_rows_read"] == 3
    assert three["pair_proof_successes"] == 1
    failed = PairChecker(case).verify(None, dict(answer, pair_proofs=[[0, 2, 0, 7]]))
    assert failed["pair_proof_current_data_failures"] == 1
    assert failed.get("alternative_exact_checks_avoided", 0) == 0
    assert failed["alternative_exact_checks_actual"] == baseline["global_minimum_alternative_groups_checked"]
    # These two axes have identical influences, hence a stale claim of three
    # responses is false here.  It never licenses a minimum-check shortcut.
    stale = PairChecker(case).verify(None, dict(answer, pair_proofs=[[0, 1, 0]]))
    assert stale["pair_proof_current_data_failures"] == 1
    assert stale.get("alternative_exact_checks_avoided", 0) == 0

    original_history = history_for(tables, 5)
    verifier = PairChecker(case)
    historical = verifier.verify_history(original_history)
    assert historical["global_minimum_queries"] == 0
    assert historical["pair_proof_successes"] == len(original_history["proofs"])
    assert historical["pair_proof_output_bits_read"] == 2 * historical["pair_proof_raw_rows_read"]
    assert not verifier._certified_pairs and not verifier._proof_row_values
    bad = deepcopy(original_history)
    bad["tables"][0] ^= 1
    rejected(lambda: verifier.verify_history(bad), "does not match")
    bad = deepcopy(original_history)
    bad["proofs"].append([0, 1, 0, 7])
    bad["faces"][0] = [0, 7]
    rejected(lambda: verifier.verify_history(bad), "fails on the actual original")
    # History verification confers no current-proof authority.
    after_history = verifier.verify(None, dict(answer, pair_proofs=[[0, 1, 0]]))
    assert after_history["pair_proof_current_data_failures"] == 1

    # Exact fallback arithmetic is checked independently of every producer.
    rng = random.Random(40956)
    exact = PairChecker(case)
    for _ in range(24):
        random_tables = (rng.getrandbits(32), rng.getrandbits(32))
        exact._compact_joint = None
        for group in combinations(range(5), 3):
            actual = classes(5, random_tables, group)
            assert exact._compact_classes(random_tables, group, 2) == min(3, actual)
            assert exact._compact_classes(random_tables, group, 4) == min(5, actual)
    # A valid pair certificate cannot exclude a two-bit competitor to a
    # three-bit incumbent; those alternatives still receive full exact tests.
    width3 = None
    for _ in range(20):
        candidate = (rng.getrandbits(16), rng.getrandbits(16))
        returned = JointSolver(4).solve(candidate)
        if returned["width"] == 3:
            width3 = returned
            break
    assert width3 is not None
    case3 = dict(id="synthetic-width3", n=4, upstream_count=0, frontier=list(range(4)),
                 gates=width3["circuit"]["gates"], outputs=width3["circuit"]["outputs"], pieces=[])
    assert scalar_tables(case3) == candidate
    answer3 = attach_physical(case3, width3)
    wider = PairChecker(case3).verify(None, dict(answer3, pair_proofs=[[0, 1, 0]]))
    assert wider["width"] == 3
    assert wider.get("alternative_exact_checks_avoided", 0) == 0
    assert wider["alternative_exact_checks_actual"] == wider["global_minimum_alternative_groups_checked"]
    assert wider.get("pair_proof_raw_rows_read", 0) == 0
    damaged = deepcopy(supplied)
    damaged["physical"]["gates"][0] = [0, 0]
    rejected(lambda: PairChecker(case).verify(None, damaged), "unchanged prefix")
    geometry = {}
    for _ in range(2):
        receipt = PairChecker(case, geometry_cache=geometry).verify(None, supplied)
        assert receipt["exact"] and receipt["alternative_exact_checks_avoided"] == covered
    ordinary_fallback = PairChecker(case, exact_fallback="historical").verify(None, supplied)
    assert ordinary_fallback["alternative_exact_checks_avoided"] == covered
    untimed = PairChecker(case, profile=False).verify(None, supplied)
    assert untimed["exact"] and untimed["alternative_exact_checks_avoided"] == covered
    assert not untimed["phase_profile_enabled"]
    assert "optimistic_no_minimum_cpu_floor_ns" not in untimed
    return dict(certificates_checked=2, alternative_exact_checks_avoided=covered,
                shared_row_requests=8, distinct_raw_reads=6, exact_fallback_random_group_bounds=480,
                stale_and_failed_proofs="fell back", original_scope="verified", physical_guarantees="retained")


if __name__ == "__main__":
    print(check())
