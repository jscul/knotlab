"""Classify the two addressed source marks before and after ordinary payment."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "source.json.gz"
B305 = "TWO-SENDS-AND-GROWN-KEEPERS-20261122-001A"
B307 = "HIDDEN-SENDER-MARKS-20261122-001A"
ORDINARY = ROOT / "artifacts" / B305 / (B305 + "-E001_two_sends") / "ordinary.json"
PRIOR = ROOT / "artifacts" / B307 / (B307 + "-E001_hidden_sends")
GROWTH = PRIOR / "growth.json.gz"
WORDS = PRIOR / "whole_words.json.gz"
PINNED = {
    ORDINARY: "c58ffc91241edb3bc797dc0a7b63bcaaa7f23d88ec9fd352ac558dabc3678d0e",
    GROWTH: "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    WORDS: "d652b46212ed4fdd3ad344596ce9a6c1b2cc2be3327cb8fbac6a765226c2f290",
}
LAWS = ("parity", "nae")
ROUTES = ("intact", "interrupted", "sham")
SIDES = ("00", "01", "10", "11")
A, B, SPARE = 510, 563, 677
SENDER, RECEIVER = 80, 294
SWAP = (1 << A) | (1 << B)
BANDS = ("E", "P", "B", "F")


def load(path=OUTPUT):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def bitmask(names):
    return sum(1 << name for name in names)


def read(word, names):
    return "".join(str(word >> name & 1) for name in names)


def legal(law, width, ones):
    if law == "parity":
        return ones % 2 == 0
    assert law == "nae"
    return 0 < ones < width


def incidence(stars):
    owners = defaultdict(list)
    for holder, names in enumerate(stars):
        assert len(names) == len(set(names)) >= 3
        for name in names:
            owners[name].append(holder)
    assert all(len(row) in (1, 2) for row in owners.values())
    return owners


def coholder_clock(holder, marks, stages):
    slots = {}
    samples = []
    for owners in stages:
        partners = []
        for name in marks:
            assert holder in owners[name]
            other = [peer for peer in owners[name] if peer != holder]
            partners.append(None if not other else slots.setdefault(other[0], len(slots)))
        if not samples or samples[-1] != partners:
            samples.append(partners)
    return samples


class PhysicalReplay:
    def __init__(self, growth, law, route):
        self.law = law
        self.route = route
        self.original = tuple(map(tuple, growth["original_stars"]))
        self.cuts = growth["cases"][route][law]["cuts"]
        self.stars = self.original
        self.stages = [self.stars]
        self.owners = [incidence(self.stars)]
        self.births = {}
        for age, cut in enumerate(self.cuts, 1):
            self.add_cut(cut, age)
        assert [len(c["births"]) for c in self.cuts] == [63, 131, 339]
        self.constraints = [(len(row), bitmask(row)) for row in self.stars]
        self.original_domain = bitmask(self.owners[0])
        self.domain = bitmask(self.owners[-1])
        self.sender_bank = self.original[SENDER]
        self.sender_clock = coholder_clock(SENDER, self.sender_bank, self.owners)
        assert len(self.sender_clock) == 2
        self.carriers = tuple(next(h for h in self.owners[1][d] if h != SENDER) for d in (A, B))
        expected_a = 164 if route == "interrupted" else 162
        assert self.carriers == (expected_a, 163)
        for d, child in zip((A, B), self.carriers, strict=True):
            assert self.owners[0][d] == [SENDER]
            assert all(owners[d] == [SENDER, child] for owners in self.owners[1:])
        assert all(len(stage[d]) == 2 for d in self.sender_bank for stage in self.owners[1:])
        self.r_bank = self.stars[RECEIVER]
        r = self.births[RECEIVER]
        assert r["parents"] == [162, 165] and r["consumed_names"] == [949, 957]
        self.r_view = r["fresh_names"]
        assert self.r_bank == (949, 957, 1754, 1755, 1756) and not set(self.r_bank) & {A, B}
        self.r_clock = coholder_clock(RECEIVER, self.r_view, self.owners[2:])
        assert self.r_clock == growth["cases"][route][law]["receivers"]["R"]["local_clock"]
        assert self.r_clock == [[None, None, None], [0, 1, 2]]
        assert all(len(self.owners[-1][d]) == 2 for d in self.r_bank)

    def add_cut(self, layer, age):
        assert layer["age"] == age and layer["status"] == "extend" and layer["old_assignments_extend"]
        before = self.owners[-1]
        unspent = {d for d, donors in before.items() if len(donors) == 1}
        assert len(unspent) == layer["total_loose_inputs"]
        new_names = set()
        after = []
        for receipt in layer["births"]:
            holder, parents, inputs, fresh = (receipt[k] for k in ("holder", "parents", "consumed_names", "fresh_names"))
            assert holder == len(self.stars) + len(after)
            assert parents and len(parents) == len(set(parents))
            assert len(fresh) == receipt["grant"] == max(1, 3 - len(parents), receipt["demand"])
            assert not ({A, B} & set(inputs)) or age == 1
            for d, donor in zip(inputs, parents, strict=True):
                assert before[d] == [donor]
                unspent.remove(d)
            for d in fresh:
                assert d not in before and d not in new_names
                new_names.add(d)
            self.births[holder] = receipt
            after.append(tuple(inputs + fresh))
        assert not unspent
        self.stars += tuple(after)
        reached = incidence(self.stars)
        assert {d for d, donors in reached.items() if len(donors) == 1} == new_names
        self.stages.append(self.stars)
        self.owners.append(reached)

    def violated(self, word, age):
        assert word >= 0
        return [i for i, (width, mask) in enumerate(self.constraints[:len(self.stages[age])])
                if not legal(self.law, width, (word & mask).bit_count())]

    def full_state(self, old_word, assignments):
        assert old_word & ~self.original_domain == 0
        word = old_word
        for layer in self.cuts:
            for newborn in layer["births"]:
                paid = newborn["consumed_names"]
                names = newborn["fresh_names"]
                active = read(word, paid).count("1")
                bank = assignments.get(newborn["holder"])
                width = len(paid) + len(names)
                if bank is None:
                    # The fresh names on each new row are distinct and nonempty.
                    bank = ("0" if legal(self.law, width, active) else "1") + "0" * (len(names) - 1)
                assert len(bank) == len(names) and legal(self.law, width, active + bank.count("1"))
                assert word & bitmask(names) == 0
                word |= bitmask(d for d, bit in zip(names, bank, strict=True) if bit == "1")
        assert word & ~self.domain == 0 and not self.violated(word, 3)
        return word

    def allocation(self, mark, holder, old):
        birth = self.births[holder]
        paid = birth["consumed_names"]
        fresh = birth["fresh_names"]
        assert mark in paid and ((A if mark == B else B) not in paid)
        before = read(old, paid)
        requested = read(old ^ SWAP, paid)
        width = len(paid) + len(fresh)
        result = []
        for word in product("01", repeat=len(fresh)):
            bank = "".join(word)
            if not legal(self.law, width, (before + bank).count("1")):
                continue
            valid = legal(self.law, width, (requested + bank).count("1"))
            remainder = read(old, [d for d in paid if d != mark]) + bank
            assert valid == (self.law == "nae" and len(set(remainder)) == 2)
            result.append((bank, valid))
        return result

    def complete_witness(self, old, banks, blockers):
        before = self.full_state(old, dict(zip(self.carriers, banks, strict=True)))
        request = before ^ SWAP
        assert request & self.original_domain == old ^ SWAP
        assert not self.violated(request, 0)
        for age in (1, 2, 3):
            # Restrict to the actual names present when the repeat was offered.
            domain = bitmask(self.owners[age])
            actual = before & domain
            trial = request & domain
            assert not self.violated(actual, age)
            assert self.violated(trial, age) == list(blockers)
            assert trial ^ SWAP == actual
        assert read(before, self.r_bank) == read(request, self.r_bank)
        return {
            "whole_cut_three_before": hex(before),
            "whole_cut_three_requested": hex(request),
            "whole_cut_three_committed": hex(before if blockers else request),
            "blocking_holders": list(blockers),
            "pointwise_inverse_admitted": not blockers,
            "pre_request_sender_bank": read(before, self.sender_bank),
            "r_fresh_word_before_and_after": read(before, self.r_view),
        }

    def census(self, side, first, old):
        addressed = list(zip((A, B), self.carriers, strict=True))
        options = [self.allocation(mark, child, old) for mark, child in addressed]
        tested = len(options[0]) * len(options[1])
        counts = Counter()
        representatives = {}
        allocations = []
        for left, right in product(*options):
            banks = left[0], right[0]
            blockers = tuple(sorted(h for h, option in zip(self.carriers, (left, right), strict=True) if not option[1]))
            counts[bool(blockers)] += 1
            allocations.append({"carrier_fresh_words": banks, "swap_admitted": not blockers,
                                "blocking_holders": list(blockers)})
            if blockers not in representatives:
                representatives[blockers] = self.complete_witness(old, banks, blockers)
        admitted, refused = counts[False], counts[True]
        assert admitted + refused == tested and tested > 0
        assert not admitted or self.law == "nae"
        same_source_disagreement = bool(admitted and refused)
        if same_source_disagreement:
            assert len({record["pre_request_sender_bank"] for record in representatives.values()}) == 1
            assert any(w["blocking_holders"] for w in representatives.values()) and () in representatives
        return {
            "law": self.law, "route": self.route, "side": side, "first_action": first,
            "first_action_net_old_word": hex(old), "first_action_net_source_bits": read(old, (A, B)),
            "carriers_in_a_b_order": [{
                "mark": mark, "holder": h, "paid_names": self.births[h]["consumed_names"],
                "paid_before_repeat": read(old, self.births[h]["consumed_names"]),
                "fresh_names": self.births[h]["fresh_names"],
            } for mark, h in addressed],
            "admission_bands_checked": list(BANDS[1:]),
            "idle_always_admitted": True,
            "strict_swap_admitted_in_late_bands": False,
            "allocations": allocations,
            "allocation_counts": {"tested": tested, "pointwise_admitted": admitted, "pointwise_refused": refused},
            "pointwise_admission_probability": str(Fraction(admitted, tested)),
            "same_sender_bank_with_opposite_admission": same_source_disagreement,
            "witnesses_by_actual_blocking_set": list(representatives.values()),
        }


def reproduce_old_words(growth, archived, prior):
    source = tuple(map(tuple, growth["original_stars"]))
    names = sorted(incidence(source))
    assert names == growth["original_name_order"]
    assert prior["old_words"].keys() == {f"{law}-{side}" for law, side in product(LAWS, SIDES)}
    output = {}
    for law in LAWS:
        original = archived["ordinary_preconsumption_private_swap"][law]["original_and_first_cut_witness"]
        assert original["original_name_order"] == names
        assert original["common_initial_word"] == growth["common_original_words"][law]
        early = bitmask(d for d, b in zip(names, original["common_initial_word"], strict=True) if b == "1")
        for side in SIDES:
            raw = prior["old_words"][f"{law}-{side}"]
            common = int(raw["common_before"], 16)
            offered = tuple(int(value, 16) for value in raw["sender_idle_and_swap"])
            assert common & ~bitmask(names) == 0 and (side != "00" or common == early)
            assert read(common, (A, B)) == "01" and read(common, (515, 555)) == side
            assert read(common, (518, 523)) == "00" and read(common, (SPARE,)) == read(early, (SPARE,))
            assert offered == (common, common ^ SWAP)
            output[law, side] = offered
    return output


def early_orders(replay, common):
    words = {}
    for requests in ("II", "IT", "TI", "TT"):
        active = common
        recollect = [read(active, (A, B))]
        for action in requests:
            if action == "T":
                assert read(active, (A, B)) in ("01", "10")
                new = active ^ SWAP
                assert new != active and not replay.violated(new, 0)
                active = new
            recollect.append(read(active, (A, B)))
        words[requests] = {"initial_and_two_requested_pairs": recollect, "net_old_word": hex(active)}
    assert words["II"]["net_old_word"] == words["TT"]["net_old_word"] == hex(common)
    return words


def build():
    blobs = {path: path.read_bytes() for path in PINNED}
    assert {path: sha256(blob).hexdigest() for path, blob in blobs.items()} == PINNED
    growth = json.loads(gzip.decompress(blobs[GROWTH]))
    source = reproduce_old_words(growth, json.loads(blobs[ORDINARY]), json.loads(gzip.decompress(blobs[WORDS])))
    replays = {(law, route): PhysicalReplay(growth, law, route) for law, route in product(LAWS, ROUTES)}
    cells = []
    preparations = {}
    for law in LAWS:
        intact, diverted, sham = (replays[law, route] for route in ROUTES)
        assert intact.stars == sham.stars and intact.cuts == sham.cuts
        assert [i for i, rows in enumerate(zip(intact.stars, diverted.stars, strict=True)) if rows[0] != rows[1]] == [162, 164]
        assert intact.cuts[1:] == diverted.cuts[1:]
        for side in SIDES:
            common, swapped = source[law, side]
            assert not intact.violated(common, 0) and not intact.violated(swapped, 0)
            preparations[f"{law}-{side}"] = early_orders(intact, common)
        for route in ROUTES:
            replay = replays[law, route]
            assert replay.r_bank == intact.r_bank and replay.r_clock == intact.r_clock
            for side in SIDES:
                for first, old in zip(("idle", "swap"), source[law, side], strict=True):
                    cells.append(replay.census(side, first, old))
    assert len(cells) == 48
    for law, route in product(LAWS, ROUTES):
        matching = [cell for cell in cells if cell["law"] == law and cell["route"] == route]
        assert any(cell["allocation_counts"]["pointwise_refused"] for cell in matching)
    return {
        "schema": "b308-repeat-source-lawfulness-v1",
        "input_sha256": {str(path.relative_to(ROOT)): expected for path, expected in PINNED.items()},
        "addresses": [A, B],
        "sender_bank": list(replays["parity", "intact"].sender_bank),
        "ownership_and_observations": {
            route: {
                "scorer_owner_sets_by_cut": [{str(d): row[d] for d in (A, B, SPARE)}
                                             for row in replays["parity", route].owners],
                "sender_anonymous_incidence_samples": replays["parity", route].sender_clock,
                "r_holding": replays["parity", route].r_bank,
                "r_positive_finish_clock": replays["parity", route].r_clock,
            } for route in ROUTES
        },
        "before_payment_ordered_words": preparations,
        "structural_rule": (
            "The two loose marks have the same sole holder S0 before payment, so a nonidentity "
            "transposition preserves every old row. Once the atomic payment assigns each mark to a "
            "different child, its owner set differs from the other mark's set. Neither mark can be paid again."
        ),
        "pointwise_rule": (
            "After payment the repeat changes one bit at each of two persistent children. Parity refuses "
            "every unequal pair. Not-all-equal accepts if both children already have unequal values "
            "among their unaffected marks. These affected rows and all of their values other than the "
            "two sender marks persist. Acceptance is unchanged by later ordinary cuts, and any "
            "accepted transposition has an accepted inverse."
        ),
        "local_finish_rule": (
            "R sees a private fresh bank at birth and a single positive batch of new coholders. "
            "Its full holding is then shared. A repeat on the two fixed sender marks is disjoint from "
            "R. Further ordinary funding cannot add another coholder or change R's values."
        ),
        "cells": cells,
    }


if __name__ == "__main__":
    payload = json.dumps(build(), sort_keys=True, separators=(",", ":")).encode()
    OUTPUT.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    print(sha256(OUTPUT.read_bytes()).hexdigest(), OUTPUT)
