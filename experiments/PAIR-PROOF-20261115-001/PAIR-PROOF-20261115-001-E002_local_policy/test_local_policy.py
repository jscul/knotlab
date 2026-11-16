"""Synthetic edits and independent scalar truth checks; no experiment fixtures."""

import json
import unittest

import local_policy as policy


def counted_bits(m, rotation=0):
    """Return parity and the second bit of a signed input count.

    Every triple has four joint residuals. Changing an inverter switches the
    sign of one input while keeping the same exact width. Four corners of any
    pair exhibit three distinct sums, but the successful three-corner masks
    depend on the relative signs.
    """
    gates = []

    def nand(a, b):
        gates.append([a, b])
        return m + 1 + len(gates)

    def conjunction(a, b):
        c = nand(a, b)
        return nand(c, c)

    def exclusive(a, b):
        c = nand(a, b)
        return nand(nand(a, c), nand(b, c))

    axes = list(range(m))
    axes = axes[rotation:] + axes[:rotation]
    flips = []
    corrected = []
    for axis in axes[:2]:
        inverse = nand(axis, axis)
        corrected.append(nand(inverse, m + 1))
        flips.append(dict(gate=corrected[-1], pin=0, to=axis))
    parity = carry = m
    for x in corrected + axes[2:]:
        carry = exclusive(carry, conjunction(parity, x))
        parity = exclusive(parity, x)
    return dict(n=m, upstream_count=0, gates=gates, frontier=list(range(m)),
                outputs=[parity, carry], pieces=[]), flips


def quartets(m, pair, mask, base):
    i, j = pair
    assert 0 <= i < j < m and base >> m == 0
    assert not (base & ((1 << i) | (1 << j)))
    assert mask in (7, 11, 13, 14, 15)
    return [base | (1 << i if k & 1 else 0) | (1 << j if k & 2 else 0)
            for k in range(4) if mask & (1 << k)]


class LocalPolicy(unittest.TestCase):
    def test_paid_update_freeze_and_transfer(self):
        cases = []
        for r in range(3):
            original, edits = counted_bits(8, r)
            cases.append(dict(original, edits=edits))
        duplicate_parent = dict(cases[0], edits=cases[0]["edits"][:1])
        model, receipt = policy.fit(cases + [duplicate_parent], (0, 1, 2, 4))
        self.assertEqual(receipt["trained_parents"], 3)
        self.assertEqual(receipt["training_width_counts"], {"2": 7})
        self.assertGreater(receipt["selected_two_bit_units"], 0)
        self.assertGreater(receipt["label_unique_current_rows"], 0)
        self.assertEqual(len(receipt["candidates"]), 36)
        self.assertTrue(all(0 <= slot < len(policy.CORNERS)
                            for r in model["recipes"] for slot in (r[1], r[4])))
        original, edits = counted_bits(9, 4)
        model = json.loads(json.dumps(model))
        actions = policy.propose(model, original, edits[0])
        self.assertTrue(actions)
        self.assertEqual(actions, policy.propose(model, original, edits[0]))
        successes = 0
        for i, j, base, mask in actions:
            rows = quartets(9, (i, j), mask, base)
            # First signed input was flipped by the current edit.
            successes += len({(row ^ (1 << 4)).bit_count() % 4 for row in rows}) >= 3
        self.assertGreater(successes, 0)
        engine = policy._train_engine()
        parent = engine._engine.Parent(original)
        selected, work = engine.select_only(parent.edit(edits[0]), "advice", advice=actions)
        exact, _ = engine.select_only(parent.edit(edits[0]), "no-proof")
        self.assertEqual((selected["width"], selected["triple"]),
                         (exact["width"], exact["triple"]))
        self.assertGreater(work["proof_avoided_exact_groups"], 0)

    def test_no_examples_and_no_private_fields(self):
        model, _ = policy.fit([])
        original, edits = counted_bits(7, 1)
        self.assertEqual([], policy.propose(model, original, edits[0]))
        self.assertEqual(policy.fixed_actions(original, edits[1]),
                         policy.fixed_actions(json.loads(json.dumps(original)), edits[1]))
        with self.assertRaises(ValueError):
            policy.propose(model, dict(original, id="secret"), edits[0])
        with self.assertRaises(ValueError):
            policy.fixed_actions(original, dict(edits[0], future={}))
        single, _ = policy.fit([dict(original, edits=edits[:1])], (0, 2))
        self.assertEqual(single["plan"], "none")

    def test_bounded_graph_reads_and_radius(self):
        original, edits = counted_bits(8, 3)
        gate = len(original["gates"]) + original["n"] + 1
        edit = {"gate": gate, "pin": 1, "to": 2}
        small = policy._view(original, edit, 0)
        large = policy._view(original, edit, 4)
        self.assertEqual(small.visits, 3)
        self.assertGreater(large.visits, small.visits)
        changed = dict(original, gates=[row[:] for row in original["gates"]])
        changed["gates"][0] = [original["n"], original["n"]]
        self.assertEqual(small, policy._view(changed, edit, 0))
        self.assertEqual(large, policy._view(changed, edit, 4))
        for r in (0, 1, 2, 4):
            view = policy._view(original, edit, r)
            self.assertLessEqual(view.visits, 3 * ((1 << (r + 1)) - 1))
            self.assertEqual(sum(row[5] for row in view.pairs), view.balanced)
            self.assertEqual(sum(row[6] for row in view.pairs), view.balanced)

    def test_gate_polarity_and_corner_falsification(self):
        # t=x XOR d; compare AND-vs-OR consumers at fixed d=0.
        for operate, good_z, working in ((lambda t, y, z: t & y & z, 1, {11, 14, 15}),
                                          (lambda t, y, z: t | y | z, 0, {7, 13, 15})):
            results = {}
            for z in (0, 1):
                code = 0
                for k in range(4):
                    x, y = k & 1, k >> 1
                    code |= ((x << 1) | operate(x, y, z)) << (2 * k)
                results[z] = {mask for mask in policy.CORNERS if policy._certificate(code, mask)}
            self.assertEqual(results[1 - good_z], set())
            self.assertEqual(results[good_z], working)


if __name__ == "__main__":
    unittest.main()
