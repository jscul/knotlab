"""Synthetic-only checks; no saved study panels, labels or timing outcomes."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pair_solver as solver


class Build:
    def __init__(self, n):
        self.n, self.gates = n, []

    def nand(self, a, b):
        self.gates.append([a, b])
        return self.n + 1 + len(self.gates)

    def inv(self, a):
        return self.nand(a, a)

    def land(self, a, b):
        return self.inv(self.nand(a, b))

    def lor(self, a, b):
        return self.nand(self.inv(a), self.inv(b))

    def xor(self, a, b):
        h = self.nand(a, b)
        return self.nand(self.nand(a, h), self.nand(b, h))

    def truth(self, truth):
        terms = []
        for row in range(1 << self.n):
            if not (truth >> row) & 1:
                continue
            pins = [j if (row >> j) & 1 else self.inv(j) for j in range(self.n)]
            term = pins[0]
            for pin in pins[1:]:
                term = self.land(term, pin)
            terms.append(term)
        if not terms:
            return self.n
        result = terms[0]
        for term in terms[1:]:
            result = self.lor(result, term)
        return result

    def parent(self, outputs):
        return solver._engine.Parent(dict(n=self.n, upstream_count=0, gates=self.gates,
                                          frontier=list(range(self.n)), outputs=outputs, pieces=[]))


def class_count(tables, n, group):
    outside = [j for j in range(n) if j not in group]
    columns = set()
    for local in range(8):
        column = []
        for rest in range(1 << len(outside)):
            row = (sum(((local >> k) & 1) << j for k, j in enumerate(group))
                   + sum(((rest >> k) & 1) << j for k, j in enumerate(outside)))
            column.append(tuple((table >> row) & 1 for table in tables))
        columns.add(tuple(column))
    return len(columns)


def verify(state, answer):
    n = state.m
    full = (1 << (1 << n)) - 1
    values = [sum(((row >> j) & 1) << row for row in range(1 << n)) for j in range(n)] + [0, full]
    supports = [1 << j for j in range(n)] + [0, 0]
    gates = answer["circuit"]["gates"]
    for a, b in gates:
        assert 0 <= a < len(values) and 0 <= b < len(values)
        values.append(full ^ (values[a] & values[b]))
        supports.append(supports[a] | supports[b])
    assert tuple(values[w] for w in answer["circuit"]["outputs"]) == state.tables
    group_mask = sum(1 << j for j in answer["triple"])
    assert all(not supports[w] & ~group_mask for w in answer["summary_wires"])
    pending, seen = list(answer["circuit"]["outputs"]), set(answer["summary_wires"])
    while pending:
        wire = pending.pop()
        if wire in seen:
            continue
        seen.add(wire)
        assert not (wire < n and group_mask & (1 << wire)), "group-to-output bypass"
        if wire >= n + 2:
            pending.extend(gates[wire - n - 2])
    semantic = []
    for truth in state.tables:
        semantic.append({j for j in range(n) if any(((truth >> row) ^ (truth >> (row ^ (1 << j)))) & 1
                                                    for row in range(1 << n))})
    groups = list(combinations(sorted(semantic[0] & semantic[1]), 3))
    assert answer["width"] == min((class_count(state.tables, n, group) - 1).bit_length() for group in groups)
    assert answer["class_count"] == class_count(state.tables, n, answer["triple"])
    for i, j, base, mask in answer.get("pair_proofs", ()):
        assert i < j and not base & ((1 << i) | (1 << j))
        rows = (base, base | (1 << i), base | (1 << j), base | (1 << i) | (1 << j))
        assert len({tuple((truth >> row) & 1 for truth in state.tables)
                    for k, row in enumerate(rows) if (mask >> k) & 1}) == 3


def fixtures():
    b = Build(4)
    p = b.xor(b.xor(0, 1), 2)
    yield "one", b.parent([b.xor(p, 3), b.land(p, 3)]), (0, 1, 2)
    b = Build(4)
    p, q = b.xor(b.xor(0, 1), 2), b.lor(b.lor(0, 1), 2)
    yield "wider-seed", b.parent([b.xor(p, 3), b.xor(q, 3)]), (0, 1, 3)
    b = Build(4)
    e = b.truth(sum(1 << row for row in range(16) if row.bit_count() == 1))
    yield "failed-probes-tie", b.parent([e, e]), (0, 1, 2)
    b = Build(4)
    yield "width-three", b.parent([b.truth(0xca35), b.truth(0x8b16)]), (0, 1, 2)


class SyntheticChecks(unittest.TestCase):
    def test_every_mode_exact_physical_and_minimum(self):
        for name, parent, hint in fixtures():
            history, acquisition = solver.prepare_history(parent)
            scalar, _ = solver.prepare_history(parent, strategy="scalar")
            self.assertEqual(history["faces"], scalar["faces"])
            self.assertEqual(acquisition["old_acquisition_pairs"], 6)
            for mode in solver.MODES:
                with self.subTest(fixture=name, mode=mode):
                    state = parent.edit(None)
                    answer, work = solver.solve(state, mode, history, history["proofs"], hint)
                    verify(state, answer)
                    self.assertGreater(work["minimum_selection_cpu_ns"], 0)
                    self.assertNotIn("pair_audit", answer)
                    if name == "one":
                        self.assertEqual(answer["width"], 1)
                        self.assertFalse(work.get("face_tests", 0))
                    elif name == "width-three":
                        self.assertEqual(answer["width"], 3)
                        self.assertFalse(work.get("face_tests", 0))
                    elif name == "wider-seed":
                        self.assertEqual(tuple(answer["triple"]), (0, 1, 2))
                        self.assertGreater(work["wider_exact_alternatives"], 0)
                    else:
                        self.assertEqual(answer["width"], 2)
                        self.assertEqual(tuple(answer["triple"]), hint)
                        self.assertFalse(answer["pair_proofs"])

    def test_frozen_physical_core_and_compact_control(self):
        for name, parent, hint in fixtures():
            answer, _ = solver.solve(parent.edit(None), hint=hint)
            reference, _ = solver._ordinary.ordinary_exact(parent.edit(None), hint)
            self.assertEqual(answer["circuit"], reference["circuit"], name)
            answer, _ = solver.solve(parent.edit(None))
            compact, _ = solver._compact.compact(parent.edit(None))
            self.assertEqual(answer["circuit"], compact["circuit"], name)

    def test_same_three_can_fail_while_new_three_at_same_four_succeeds(self):
        # Original corner colors0,1,2,2; current colors0,1,1,2.
        old = (0b0010, 0b1100)
        current = (0b0110, 0b1000)
        old_rows = solver._Rows(old, Counter())
        self.assertEqual(old_rows.test(0, 1, 0, 15), 7)
        work = Counter()
        rows = solver._Rows(current, work)
        self.assertEqual(rows.test(0, 1, 0, 7), 0)
        self.assertEqual(rows.test(0, 1, 0, 15), 11)
        self.assertEqual((work["query_row_requests"], work["query_unique_rows"], work["query_reused_rows"]), (7, 4, 3))

    def test_bulk_and_scalar_advice_and_edit_isolation(self):
        _, parent, _ = next(f for f in fixtures() if f[0] == "wider-seed")
        history, _ = solver.prepare_history(parent)
        counts = []
        for _ in range(2):
            state = parent.edit(None)
            answer, work = solver.solve(state, "advice", advice=history["proofs"], hint=(0, 1, 2), audit=True)
            verify(state, answer)
            self.assertIn("pair_audit", answer)
            self.assertEqual(work["proof_avoided_exact_groups"], 3)
            self.assertEqual(work.get("compact_exact_alternatives", 0), 0)
            counts.append((work.get("query_row_requests", 0), work.get("query_unique_rows", 0)))
        self.assertEqual(counts[0], counts[1])
        state = parent.edit(None)
        answer, work = solver.solve(state, "advice", advice=[], hint=(0, 1, 2))
        verify(state, answer)
        self.assertEqual(work.get("face_tests", 0), 0)
        self.assertEqual(work["compact_exact_alternatives"], 3)
        with self.assertRaises(ValueError):
            solver.solve(parent.edit(None), "advice", advice=[[0, 1, 1]], hint=(0, 1, 2))


if __name__ == "__main__":
    unittest.main()
