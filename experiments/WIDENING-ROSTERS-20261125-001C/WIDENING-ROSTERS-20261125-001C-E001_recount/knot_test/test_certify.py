"""Targeted controls for the exact whole-stage certificate."""

from collections import Counter
from itertools import product
import random
import unittest

from canonical import canonical_check
from canonical_wide import wide_check
from certify import History, Stage, birth_projections, certify_history, whole_stage
from projection import Projection, own_relation


def as_history(*rounds):
    supports = []
    stages = []
    for births in rounds:
        supports.extend(tuple(sorted(support)) for support in births)
        distinctions = {d for support in supports for d in support}
        assert distinctions == set(range(len(distinctions)))
        stages.append(Stage(len(supports), len(distinctions)))
    return History(supports, stages)


def brute(history, t, law):
    stage = history.stages[t]
    supports = history.supports[:stage.knots]
    allowed = [set() for _ in supports]
    for row in product((0, 1), repeat=stage.distinctions):
        parts = [tuple(row[d] for d in support) for support in supports]
        valid = (
            all(sum(part) % 2 == 0 for part in parts) if law == "parity"
            else all(len(set(part)) == 2 for part in parts)
        )
        if valid:
            for u, part in enumerate(parts):
                allowed[u].add(sum(bit << i for i, bit in enumerate(part)))
    return allowed


class ExactProjectionControls(unittest.TestCase):
    def assert_exact(self, history, law):
        stable, _ = birth_projections(history, law, Counter())
        for t, stage in enumerate(history.stages):
            reference = brute(history, t, law)
            computed = whole_stage(history, t, law, range(stage.knots), Counter())
            for u, projection in computed.items():
                actual = {word for word in range(1 << projection.width) if projection.allows(word)}
                self.assertEqual(actual, reference[u], (t, u, law, history))
                if stable is not None:
                    self.assertTrue(projection.same_relation(stable[u]))
        return certify_history(history, law)

    def test_no_loose_distinction_off_the_target_and_odd_cycle(self):
        # Each of the three remaining knots has two free distinctions and
        # one fixed place. A single equal pair repairs alternation.
        h = as_history([(0, 1, 2), (0, 3, 5), (1, 3, 4), (2, 4, 5)])
        for law in ("nae", "parity"):
            result = self.assert_exact(h, law)
            self.assertEqual(result["stages"][0]["passed"], 4)

    def test_terminal_cut_and_preservation_under_implied_closing(self):
        h = as_history([(0, 1, 2), (3, 4, 5)], [(0, 1, 2, 3, 4, 5)])
        result = self.assert_exact(h, "parity")
        self.assertEqual(result["evidence"]["implied_closing_births"], 1)
        self.assertEqual(result["stages"][1]["failed"], 1)
        self.assertEqual(result["failure_details"][0]["projection"]["data"], (7, 56))

    def test_invalid_closing_restricts_only_the_later_stage(self):
        h = as_history([(0, 1, 2), (3, 4, 5)], [(0, 1, 2, 3)])
        result = self.assert_exact(h, "parity")
        self.assertEqual(result["birth_method_fallback"]["reason"], "unproved_old_extension")
        self.assertEqual([stage["failed"] for stage in result["stages"]], [0, 2])

    def test_nae_extra_exclusions_can_leave_k2_true(self):
        h = as_history([(0, 1, 2, 3), (0, 1, 4), (2, 3, 4)])
        result = self.assert_exact(h, "nae")
        stronger = [r for r in result["stages"][0]["relations"] if r["projection"]["width"] == 4][0]
        self.assertEqual(stronger["allowed_count"], 12)
        self.assertTrue(stronger["loss_on_erasure"])

    def test_nae_extra_exclusions_can_make_k2_false(self):
        h = as_history([(0, 1, 2, 3, 4), (0, 1, 5), (2, 3, 5)])
        result = self.assert_exact(h, "nae")
        failed = result["failure_details"][0]
        self.assertTrue(failed["binding"] and failed["coexistence"])
        self.assertFalse(failed["loss_on_erasure"])

    def test_all_pins_and_fresh_nae_fallback(self):
        h = as_history([(0, 1, 2)], [(0, 1, 2, 3)])
        result = self.assert_exact(h, "nae")
        self.assertEqual(result["evidence"]["saturated_nae_sat_targets"], 1)
        self.assertEqual(result["stages"][1]["failed"], 1)

    def test_many_holders_fallback(self):
        h = as_history([(0, 1, 2), (0, 3, 4)], [(0, 5, 6)])
        for law in ("nae", "parity"):
            result = self.assert_exact(h, law)
            self.assertEqual(result["birth_method_fallback"]["reason"], "input_not_sole_use_loose")

    def test_small_whole_systems_against_exhaustion(self):
        rng = random.Random(15)
        for _ in range(100):
            rows = [set(rng.sample(range(8), rng.randrange(3, 6))) for _ in range(4)]
            packed = {d: i for i, d in enumerate(sorted(set.union(*rows)))}
            h = as_history([tuple(map(packed.__getitem__, row)) for row in rows])
            for law in ("nae", "parity"):
                self.assert_exact(h, law)

    def test_canonical_cli_on_actual_positive_and_negative_relations(self):
        controls = [
            own_relation(4, "nae"), own_relation(4, "parity"),
            Projection(3, "table"), Projection(3, "table", tuple(range(8))),
        ]
        for law in ("nae", "parity"):
            self.assertTrue(canonical_check(own_relation(4, law))["is_knot"])
        h = as_history([(0, 1, 2), (3, 4, 5)], [(0, 1, 2, 3, 4, 5)])
        projection = whole_stage(h, 1, "parity", [2], Counter())[2]
        self.assertFalse(canonical_check(projection)["is_knot"])
        controls.append(projection)
        h = as_history([(0, 1, 2, 3, 4), (0, 1, 5), (2, 3, 5)])
        projection = whole_stage(h, 0, "nae", [0], Counter())[0]
        self.assertFalse(canonical_check(projection)["is_knot"])
        controls.append(projection)
        for projection in controls:
            self.assertEqual(canonical_check(projection), wide_check(projection))


if __name__ == "__main__":
    unittest.main()
