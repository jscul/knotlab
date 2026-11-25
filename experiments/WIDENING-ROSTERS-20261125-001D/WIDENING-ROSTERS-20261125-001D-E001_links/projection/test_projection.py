"""Literal truth controls and provenance checks for the link projections."""

from itertools import combinations, product
import random
import unittest

from job import parse_rounds, project_events, rows_with_masks, split_arm_rows, verify_events
from stage import NaeProjection, ParityProjection
from truth import canonical_receipt, classify


def project(rules, law, variables):
    solver_type = NaeProjection if law == "nae" else ParityProjection
    with solver_type() as solver:
        solver.add(rules)
        return solver.project(variables)


def brute(rules, law, variables):
    n = max(max(rule) for rule in rules) + 1
    projected = 0
    for values in product(range(2), repeat=n):
        parts = [tuple(values[d] for d in rule) for rule in rules]
        if law == "nae":
            ready = all(len(set(row)) == 2 for row in parts)
        else:
            ready = all(sum(row) % 2 == 0 for row in parts)
        if ready:
            projected |= 1 << sum(values[d] << i for i, d in enumerate(reversed(variables)))
    return projected


class ProjectionControls(unittest.TestCase):
    def test_full_stage_parity_contact_table(self):
        initial = [(0, 2, 3), (1, 2, 4)]
        stage = [*initial, (2, 3, 4)]
        self.assertEqual(project(initial, "parity", (0, 1)), 15)
        self.assertEqual(project(stage, "parity", (0, 1, 2)), 0x69)
        self.assertEqual(classify(0x69)["category"], "knot")

    def test_full_stage_nae_contact_table(self):
        stage = [(0, 2, 3), (1, 2, 4), (0, 1, 2)]
        self.assertEqual(project(stage, "nae", (0, 1, 2)), 0x7E)
        self.assertEqual(classify(0x7E)["category"], "knot")

    def test_proper_hub_with_only_a_shared_identity(self):
        # Each four-rule gadget forces its own endpoint opposite the same c.
        a_arm = [(0, 2, 3), (0, 2, 4), (0, 2, 5), (3, 4, 5)]
        b_arm = [(1, 2, 6), (1, 2, 7), (1, 2, 8), (6, 7, 8)]
        both_arms = [*a_arm, *b_arm, (2, 9, 10)]
        mask = project(both_arms, "nae", (0, 1, 2))
        self.assertEqual(mask, 0x42)
        row = classify(mask)
        self.assertEqual(row["arm_product_mask"], mask)
        self.assertEqual(row["category"], "proper_hub")
        self.assertFalse(row["loss_on_erasure"])
        only_a = [*a_arm, (1, 2, 6), (2, 7, 8)]
        self.assertEqual(classify(project(only_a, "nae", (0, 1, 2)))["category"], "one_sided")

    def test_free_and_empty_controls(self):
        loose_completions = [(0, 2, 3), (1, 2, 4), (2, 5, 6)]
        for law in ("nae", "parity"):
            self.assertEqual(project(loose_completions, law, (0, 1, 2)), 255)
        empty = list(combinations(range(5), 3))
        self.assertEqual(project(empty, "nae", (0, 1, 2)), 0)
        self.assertEqual(classify(255)["category"], "full")
        self.assertEqual(classify(0)["category"], "empty")
        self.assertEqual(classify(0x55)["constant_roles"], ["c"])
        self.assertEqual(classify(0x55)["category"], "other")

    def test_stock_cli_exact_mask(self):
        for mask in (0, 0x42, 0x55, 0x69, 0x7E, 255):
            self.assertEqual(canonical_receipt(mask)["classification"], classify(mask))

    def test_small_whole_stages_against_brute_force(self):
        rng = random.Random(43)
        for _ in range(100):
            rules = [(0, 1, 2, 3, 4, 5, 6)]
            rules.extend(tuple(rng.sample(range(7), rng.randrange(3, 6))) for _ in range(4))
            for law in ("nae", "parity"):
                for width in (2, 3):
                    visible = tuple(rng.sample(range(7), width))
                    self.assertEqual(project(rules, law, visible), brute(rules, law, visible))

    def test_full_stage_and_prior_masks_keep_their_distinct_prefixes(self):
        rounds, supports = parse_rounds([
            {"round": 0, "knots": 2, "distinctions": 5, "supports": [[0, 2, 3], [1, 2, 4]]},
            {"round": 1, "knots": 3, "distinctions": 5, "supports": [[2, 3, 4]]},
        ])
        events = [{
            "s": 0, "t": 1, "X": [0], "Y": [1], "meeting_types": ["met"],
            "routes": [{
                "route": "met", "w": 2, "u": 0, "v": 1,
                "contacts": [2], "x_arms": [2, 3], "y_arms": [2, 4], "a": [0, 3], "b": [1, 4],
            }],
        }]
        events = verify_events(events, rounds, supports, [0])
        current, prior, work = project_events(rounds, events, "parity")
        rows = list(rows_with_masks("example", "parity", rounds, events, current, prior))
        self.assertEqual(rows[0], ("example", "parity", 0, [0], [1], 1, "met", 2, 0, 1, 2, 0, 1, 0x69, 15))
        self.assertEqual(work["unique_triples"], 4)
        self.assertEqual(work["unique_prior_pairs"], 4)
        self.assertFalse(list(split_arm_rows("example", "parity", events)))
        events[0]["routes"][0]["contacts"] = [3]
        with self.assertRaisesRegex(ValueError, "absent at one endpoint"):
            verify_events(events, rounds, supports, [0])

    def test_split_arms_produce_an_incidence_record_without_a_mask(self):
        rounds, supports = parse_rounds([
            {"round": 0, "knots": 2, "distinctions": 6, "supports": [[0, 1, 2], [3, 4, 5]]},
            {"round": 1, "knots": 3, "distinctions": 7, "supports": [[2, 3, 6]]},
        ])
        events = [{
            "s": 0, "t": 1, "X": [0], "Y": [1], "meeting_types": ["demand"],
            "routes": [{
                "route": "demand", "w": 2, "u": 0, "v": 1,
                "contacts": [], "x_arms": [2], "y_arms": [3], "a": [0, 1, 2], "b": [3, 4, 5],
            }],
        }]
        events = verify_events(events, rounds, supports, [0])
        current, prior, work = project_events(rounds, events, "nae")
        self.assertFalse(list(rows_with_masks("example", "nae", rounds, events, current, prior)))
        self.assertEqual(work["projection_calls"], 0)
        self.assertEqual(list(split_arm_rows("example", "nae", events)), [
            ("example", "nae", 0, [0], [1], 1, "demand", 2, 0, 1, [2], [3]),
        ])


if __name__ == "__main__":
    unittest.main()
