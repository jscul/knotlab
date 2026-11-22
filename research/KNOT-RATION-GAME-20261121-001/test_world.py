"""Check physical links, payments, and local projections in game worlds."""

import sys
import unittest
from collections import defaultdict

from world import ROOT, sample_world, source_key


sys.path.insert(0, str(ROOT / "experiments/GENERATORS-20261120-001A/"
                       "GENERATORS-20261120-001A-E001_generators"))
from fixtures import certify_source, from_stars, step  # noqa: E402


CLOSING_SEED = int.from_bytes(b"ordinary-world:closure", "big") + 9
LAWS = ("parity", "nae")


class WorldTests(unittest.TestCase):
    def test_reset_and_source_pairing(self):
        keys = set()
        for seed in range(32):
            parity = sample_world(seed, "parity")
            nae = sample_world(seed, "nae")
            self.assertEqual(parity, sample_world(seed, "parity"))
            self.assertEqual(nae, sample_world(seed, "nae"))
            self.assertEqual(parity.stages[0], nae.stages[0])
            self.assertEqual(parity.source_key, source_key(seed))
            self.assertEqual(parity.source_key, nae.source_key)
            keys.add(parity.source_key)
        self.assertGreater(len(keys), 1)

    def test_physical_replay(self):
        for seed in (0, 1, 3, 17, 21, CLOSING_SEED):
            for law in LAWS:
                with self.subTest(seed=seed, law=law):
                    self.check_replay(sample_world(seed, law))

    def check_replay(self, world):
        for stage in world.stages:
            owners = defaultdict(list)
            for holder, names in enumerate(stage.holdings):
                for name in names:
                    owners[name].append(holder)
            for holder, names in enumerate(stage.holdings):
                linked = {(name, other) for name in names for other in owners[name] if other != holder}
                loose = {name for name in names if owners[name] == [holder]}
                self.assertEqual(set(stage.links[holder]), linked)
                self.assertEqual(set(stage.loose[holder]), loose)
                self.assertTrue(all(len(owners[name]) in (1, 2) for name in names))

        current = world.stages[0]
        for attempt in world.attempts:
            plan = step(from_stars(current.holdings), world.law)
            if plan.status != "extend":
                self.assertEqual(attempt.status, plan.status)
                self.assertEqual(attempt.shortages, plan.shortages)
                self.assertEqual(attempt.stage, current.formation)
                self.assertEqual(attempt.births, ())
                break
            self.assertEqual(attempt.status, "born")
            following = world.stages[attempt.stage]
            self.assertEqual(following.holdings[:len(current.holdings)], current.holdings)
            self.assertEqual(tuple(b.holder for b in attempt.births), following.born)
            self.assertEqual(tuple(tuple(parent for parent, _ in b.payments) for b in attempt.births),
                             plan.parents)
            self.assertEqual(tuple(len(b.grants) for b in attempt.births), plan.fresh)
            self.assertEqual(tuple(b.demand for b in attempt.births), plan.demand)
            payments = sorted((h, n) for b in attempt.births for h, n in b.payments)
            self.assertEqual(payments, sorted((h, n) for h, names in enumerate(current.loose) for n in names))
            for birth in attempt.births:
                names = tuple(name for _, name in birth.payments) + birth.grants
                self.assertEqual(following.holdings[birth.holder], names)
                self.assertEqual(tuple(sorted(birth.grants)), following.loose[birth.holder])
            current = following

    def test_closure_and_stall(self):
        for law in LAWS:
            world = sample_world(0, law)
            self.assertEqual(world.stop, "stall")
            self.assertEqual(len(world.stages), 1)
            self.assertTrue(world.attempts[0].shortages)

        parity = sample_world(CLOSING_SEED, "parity")
        nae = sample_world(CLOSING_SEED, "nae")
        self.assertEqual(parity.stop, "closed")
        self.assertEqual(parity.attempts[1].births[0].grants, ())
        self.assertEqual(parity.attempts[2].status, "closed")
        self.assertEqual(nae.attempts[1].births[0].payments, parity.attempts[1].births[0].payments)
        self.assertEqual(len(nae.attempts[1].births[0].grants), 1)
        self.assertEqual(nae.attempts[2].status, "born")

    def test_projected_laws_on_accumulated_holdings(self):
        for seed in (0, 1, CLOSING_SEED):
            for law in LAWS:
                with self.subTest(seed=seed, law=law):
                    certify_source(sample_world(seed, law).stages[-1].holdings, law)


if __name__ == "__main__":
    unittest.main()
