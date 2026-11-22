"""Independent replay of the enrolled fresh-mark supports and exact rates."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import product
import json
from math import comb, prod
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
SOURCE = "TWO-SENDS-AND-GROWN-KEEPERS-20261122-001A"
ARCHIVE = ROOT / "artifacts" / SOURCE / (SOURCE + "-E001_two_sends") / "ordinary.json"
DESIGN = ROOT / "research" / HERE.parent.name / "design_candidate.md"
PINNED = {
    DATA / "growth.json.gz": "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    DATA / "supports.json.gz": "35d55ff7594316542c0ee003ea4c0de1c82eda207c66b82a54961b1befccbf80",
    DATA / "whole_words.json.gz": "d652b46212ed4fdd3ad344596ce9a6c1b2cc2be3327cb8fbac6a765226c2f290",
    ARCHIVE: "c58ffc91241edb3bc797dc0a7b63bcaaa7f23d88ec9fd352ac558dabc3678d0e",
    DESIGN: "400924e945474db498557639dfd2b0dcaf726e8dd85b32a077d240a64d741f14",
}
LAWS = ("parity", "nae")
ROUTES = ("intact", "interrupted", "sham")
SIDES = ("00", "01", "10", "11")
TARGETS = {"C": 162, "D": 163, "R": 294, "J": 292}
A, B, SPARE = 510, 563, 677


def held_names(names):
    return sum(1 << name for name in names)


def sample(word, names):
    return "".join("1" if word & (1 << name) else "0" for name in names)


def valid(law, ones, width):
    if law == "parity":
        return ones % 2 == 0
    assert law == "nae"
    return 0 < ones < width


def decode(word):
    value = int(word, 16)
    assert value >= 0
    return value


def check_word(law, word, masks, domain):
    assert word & ~domain == 0
    assert all(valid(law, (word & mark_mask).bit_count(), width) for mark_mask, width in masks)


def snapshot_owners(stars):
    owners = defaultdict(set)
    for holder, row in enumerate(stars):
        assert len(set(row)) == len(row) >= 3
        for name in row:
            owners[name].add(holder)
    assert all(len(row) in (1, 2) for row in owners.values())
    return owners


class Ledger:
    def __init__(self, grown, law, route):
        self.law = law
        self.original = tuple(map(tuple, grown["original_stars"]))
        self.stars = self.original
        self.stages = [self.stars]
        self.owners = [snapshot_owners(self.stars)]
        self.births = {}
        self.when = {}
        self.fresh_payer = {}
        condition = grown["cases"][route][law]
        for age, cut in enumerate(condition["cuts"], 1):
            self.add_cut(cut, age)
        assert len(self.stages) == 4 and len(self.stars) == 647
        self.constraints = tuple((held_names(row), len(row)) for row in self.stars)
        self.domain = held_names(self.owners[-1])
        self.clock = {target: self.finish(holder) for target, holder in TARGETS.items()}
        for target, holder in TARGETS.items():
            receipt = condition["receivers"][target]
            assert receipt["holder"] == holder
            assert list(self.stars[holder]) == receipt["holding"]
            assert self.clock[target] == receipt["local_clock"]
            assert self.births[holder]["fresh_names"] == receipt["fresh_names"]
            assert self.births[holder]["consumed_names"] == receipt["inherited_names"]

    def add_cut(self, cut, age):
        assert cut["age"] == age and cut["status"] == "extend" and cut["old_assignments_extend"]
        before = self.owners[-1]
        available = {name for name, holders in before.items() if len(holders) == 1}
        assert cut["total_loose_inputs"] == len(available)
        minted = set()
        children = []
        use_count = Counter()
        for record in cut["births"]:
            h, parents, paid, fresh = (record[k] for k in ("holder", "parents", "consumed_names", "fresh_names"))
            assert h == len(self.stars) + len(children)
            assert len(parents) == len(set(parents)) and parents
            for name, payer in zip(paid, parents, strict=True):
                assert before[name] == {payer} and self.when.get(payer, 0) == age - 1
                available.remove(name)
                use_count[str(payer)] += 1
            assert len(fresh) == record["grant"] == max(1, 3 - len(paid), record["demand"])
            for name in fresh:
                assert name not in self.fresh_payer and name not in before
                self.fresh_payer[name] = h
                minted.add(name)
            # Every conditional kernel is positive and normalized for every
            # possible prior tuple, including genuine three-contributor births.
            for paid_ones in range(len(paid) + 1):
                mass = sum(comb(len(fresh), n) for n in range(len(fresh) + 1)
                           if valid(self.law, paid_ones + n, len(paid) + len(fresh)))
                self.check_conditional_normalizer(mass, paid_ones, len(paid), len(fresh))
            self.births[h] = record
            self.when[h] = age
            children.append(tuple(paid + fresh))
        assert not available and dict(use_count) == cut["paid_count_by_donor"]
        self.stars += tuple(children)
        self.stages.append(self.stars)
        reached = snapshot_owners(self.stars)
        assert {name for name, holders in reached.items() if len(holders) == 1} == minted
        self.owners.append(reached)

    def check_conditional_normalizer(self, mass, ones, paid, length):
        count = (1 << (length - 1)) if self.law == "parity" else (1 << length) - int(ones in (0, paid))
        assert mass == count and mass > 0
        assert mass * Fraction(1, count) == 1

    def finish(self, holder):
        when = self.when[holder]
        fresh = self.births[holder]["fresh_names"]
        assert fresh and all(self.owners[when][name] == {holder} for name in fresh)
        numbering = {}
        clocks = [[None] * len(fresh)]
        for stage in self.owners[when + 1:]:
            result = []
            for mark in fresh:
                others = stage[mark] - {holder}
                peer = next(iter(others), None)
                result.append(None if peer is None else numbering.setdefault(peer, len(numbering)))
            if result != clocks[-1]:
                clocks.append(result)
            if all(peer is not None for peer in result):
                break
        assert len(clocks) == 2 and all(peer is not None for peer in clocks[-1])
        return clocks

    def fresh_options(self, holder, inputs):
        birth = self.births[holder]
        width = len(birth["fresh_names"])
        count = sum(inputs)
        arity = len(inputs) + width
        return tuple(values for values in product((0, 1), repeat=width)
                     if valid(self.law, count + sum(values), arity))

    def projected_kernel(self, holder, original_word):
        """Marginalize each actual payer once before joining the paid inputs."""
        birth = self.births[holder]
        input_names = birth["consumed_names"]
        by_payer = defaultdict(list)
        fixed = {}
        for name, parent in zip(input_names, birth["parents"], strict=True):
            if name in self.fresh_payer:
                assert self.fresh_payer[name] == parent and self.when[parent] == 1
                by_payer[parent].append(name)
            else:
                fixed[name] = int(original_word >> name & 1)
        tables = []
        for parent, names in by_payer.items():
            p = self.births[parent]
            fresh = p["fresh_names"]
            wanted = [fresh.index(name) for name in names]
            allocations = self.fresh_options(parent, [int(original_word >> d & 1) for d in p["consumed_names"]])
            histogram = Counter(tuple(draw[i] for i in wanted) for draw in allocations)
            tables.append([(dict(zip(names, vals, strict=True)), Fraction(n, len(allocations)))
                           for vals, n in histogram.items()])
        result = Counter()
        for draws in product(*tables):
            inputs = fixed | {name: bit for paid, _ in draws for name, bit in paid.items()}
            chance = prod((weight for _, weight in draws), start=Fraction(1))
            draws_at_receiver = self.fresh_options(holder, tuple(inputs[d] for d in input_names))
            for observed in draws_at_receiver:
                result["".join(map(str, observed))] += chance / len(draws_at_receiver)
        assert sum(result.values()) == 1 and all(value > 0 for value in result.values())
        return dict(result)


def old_pairs(growth, supports, witness, earlier):
    source = tuple(map(tuple, growth["original_stars"]))
    old_names = sorted(snapshot_owners(source))
    assert old_names == growth["original_name_order"]
    slots = held_names(old_names)
    rows = tuple((held_names(row), len(row)) for row in source)
    expected = {f"{law}-{side}" for law in LAWS for side in SIDES}
    assert supports["background_inputs"].keys() == witness["old_words"].keys() == expected
    pairs = {}
    for law, side in product(LAWS, SIDES):
        archived = earlier["ordinary_preconsumption_private_swap"][law]["original_and_first_cut_witness"]
        archive = archived["common_initial_word"]
        assert archived["original_name_order"] == old_names and growth["common_original_words"][law] == archive
        archive_word = held_names(name for name, bit in zip(old_names, archive, strict=True) if bit == "1")
        label = f"{law}-{side}"
        spec = witness["old_words"][label]
        old = decode(spec["common_before"])
        pair = tuple(map(decode, spec["sender_idle_and_swap"]))
        assert pair == (old, old ^ held_names((A, B)))
        assert side != "00" or old == archive_word
        assert sample(old, (A, B)) == "01" and sample(old, (515, 555)) == side
        assert sample(old, (518, 523)) == "00" and sample(old, (SPARE,)) == sample(archive_word, (SPARE,))
        assert supports["background_inputs"][label] == {
            "P_paid": "00",
            "old_changed_vs_archive": [d for d in old_names if (old ^ archive_word) >> d & 1],
            "old_fixed_in_both_offers": spec["common_before"],
            "realizable": True, "side": side, "spare": sample(old, (SPARE,)),
        }
        for word in pair:
            check_word(law, word, rows, slots)
        pairs[law, side] = pair
    assert all(snapshot_owners(source)[d] == {80} for d in (A, B, SPARE))
    return slots, pairs


def support_comparison(left, right):
    return {"counts": [len(left), len(right)], "common": sorted(left & right),
            "exclusive_idle": sorted(left - right), "exclusive_swap": sorted(right - left),
            "union_size": len(left | right), "zero_error": not (left & right)}


def audit_projections(supports, ledgers, old):
    labels = tuple(TARGETS)
    expected = set(product(LAWS, ROUTES, SIDES, labels))
    rows = {(r["law"], r["route"], r["side"], r["target"]): r for r in supports["projections"]}
    assert rows.keys() == expected and len(rows) == len(supports["projections"]) == 96
    unions = defaultdict(lambda: [set(), set()])
    reads = {}
    for (law, route, side, label), submitted in rows.items():
        ledger, holder = ledgers[law, route], TARGETS[label]
        fresh = ledger.births[holder]["fresh_names"]
        assert submitted["fresh_slots"] == fresh
        assert all(ledger.fresh_payer[d] == holder for d in fresh)
        assert not set(fresh) & set(ledger.births[holder]["consumed_names"])
        assert supports["reader_local_clock"][law][route][label] == ledger.clock[label]
        kernels = [ledger.projected_kernel(holder, word) for word in old[law, side]]
        a, b = list(map(set, kernels))
        assert submitted["support"] == support_comparison(a, b)
        assert submitted["individual"] == [
            support_comparison({w[i] for w in a}, {w[i] for w in b}) for i in range(len(fresh))
        ]
        tv = sum(abs(kernels[0].get(w, 0) - kernels[1].get(w, 0)) for w in a | b) / 2
        accuracy = sum(max(kernels[0].get(w, 0), kernels[1].get(w, 0)) for w in a | b) / 2
        assert accuracy == (1 + tv) / 2 and submitted["cancelled_later_birth_weight"]
        weighted = submitted["weighted"]
        for j, arm in enumerate(("idle", "swap")):
            assert {word: Fraction(mass) for word, mass in weighted[arm].items()} == kernels[j]
            unions[law, route, label][j].update(kernels[j])
        assert (Fraction(weighted["total_variation"]), Fraction(weighted["equal_prior_optimal_accuracy"])) == (tv, accuracy)
        assert support_comparison({w[::-1] for w in a}, {w[::-1] for w in b})["counts"] == [len(a), len(b)]
        reads[law, route, side, label] = (a, b, tv, accuracy)
    pooled = {(x["law"], x["route"], x["target"]): x["support"] for x in supports["unknown_reference_union"]}
    assert len(pooled) == len(supports["unknown_reference_union"]) == 24
    assert pooled == {key: support_comparison(*pair) for key, pair in unions.items()}
    return reads, pooled


def coupling(ledger, pair, record, old_domain):
    a, b = pair
    pinned = ledger.stars[TARGETS["R"]]
    assert sample(a, pinned) == sample(b, pinned)
    altered = a ^ b
    changed_fresh = altered & ~old_domain
    corrected = sorted(d for d in ledger.fresh_payer if changed_fresh & (1 << d))
    assert record["only_changed_fresh"] == corrected
    assert record["equal_entire_fresh"] == (not corrected)
    if ledger.law == "nae":
        assert corrected == [] and record["joint_second_payment"] is None
        return
    # Keeping every fresh value is impossible in parity when exactly one paid
    # value changes at each of two distinct first-cut holders.
    recipients = {h for h, birth in ledger.births.items() if ledger.when[h] == 1
                  and len(set(birth["consumed_names"]) & {A, B}) == 1}
    assert len(recipients) == len(corrected) == 2
    assert recipients == {ledger.fresh_payer[d] for d in corrected}
    joint = record["joint_second_payment"]
    assert ledger.when[joint] == 2 and set(ledger.births[joint]["parents"]) == recipients
    assert set(ledger.births[joint]["consumed_names"]) == set(corrected)
    assert not (set(corrected) & set(pinned))


def verify_recoding(ledger, pair):
    names = list(range(ledger.domain.bit_length()))
    holders = list(range(len(ledger.stars)))
    rng = Random(202611220307)
    rng.shuffle(names)
    rng.shuffle(holders)
    reached = [None] * len(holders)
    for i, row in enumerate(ledger.stars):
        reached[holders[i]] = tuple(names[d] for d in row)
    domain = held_names(snapshot_owners(reached))
    masks = tuple((held_names(row), len(row)) for row in reached)
    for word in pair:
        transported = held_names(names[n] for n in range(len(names)) if word >> n & 1)
        check_word(ledger.law, transported, masks, domain)
        for h in TARGETS.values():
            fresh = ledger.births[h]["fresh_names"]
            for ordering in (fresh, fresh[::-1]):
                assert sample(word, ordering) == sample(transported, [names[d] for d in ordering])


def verify_witnesses(witness, supports, ledgers, reads, old_domain, old):
    extensions = {}
    for row in witness["whole_extensions"]:
        key = row["law"], row["route"], row["side"], row["target"], row["fresh_value"]
        assert key not in extensions
        extensions[key] = row
    assert extensions.keys() == {(*key, reading) for key, (a, b, _, _) in reads.items() for reading in a | b}
    checked = Counter()
    coupled = Counter()
    recoded = set()
    for (law, route, side, label, word), record in extensions.items():
        ledger = ledgers[law, route]
        supports_a, supports_b, _, _ = reads[law, route, side, label]
        assert record["same_prestate"] == f"{law}-{side}"
        options = record["complete_reached"]
        assert len(options) == 2
        pair = []
        for selected, raw in enumerate(options):
            expect = word in (supports_a, supports_b)[selected]
            assert (raw is not None) == expect
            if raw is not None:
                actual = decode(raw)
                check_word(law, actual, ledger.constraints, ledger.domain)
                assert actual & old_domain == old[law, side][selected]
                assert sample(actual, ledger.births[TARGETS[label]]["fresh_names"]) == word
                checked[law] += 1
                pair.append(actual)
        if label == "R":
            assert len(pair) == 2 and record["coupling"] is not None
            coupling(ledger, pair, record["coupling"], old_domain)
            coupled[law] += 1
            if side == "00" and word == "000":
                verify_recoding(ledger, pair)
                recoded.add((law, route))
        else:
            assert record["coupling"] is None
    assert dict(checked) == supports["whole_extensions_verified_per_law"]
    assert recoded == {(r["law"], r["route"]) for r in supports["recodings"]} == set(product(LAWS, ROUTES))
    return len(extensions), dict(checked), dict(coupled)


def confirm_controls(ledgers, reads, pooled, old):
    primary = {}
    count = Counter()
    for law, side in product(LAWS, SIDES):
        for target in TARGETS:
            assert reads[law, "intact", side, target] == reads[law, "sham", side, target]
        for route in ROUTES:
            frame = ledgers[law, route]
            p = frame.births[165]
            assert p["consumed_names"] == [518, 523] and p["fresh_names"] == [957, 958]
            assert frame.projected_kernel(165, old[law, side][0]) == frame.projected_kernel(165, old[law, side][1])
            assert frame.births[294]["parents"] == [162, 165]
            assert frame.stars[294] == (949, 957, 1754, 1755, 1756)
            assert frame.clock["R"] == [[None, None, None], [0, 1, 2]]
            assert frame.births[292]["consumed_names"] == [947, 950]
            controls = {}
            for target in TARGETS:
                a, b, tv, accuracy = reads[law, route, side, target]
                count[law] += not bool(a & b)
                if law == "parity":
                    expected = target == "D" or (target == "C" and route != "interrupted")
                    assert bool(a & b) != expected
                    assert tv == int(expected)
                else:
                    assert a & b
                if target == "R":
                    assert len(a) == len(b) == len(a & b) == 8
                    assert tv == (Fraction(5, 784) if law == "nae" and route != "interrupted" else 0)
                controls[target] = {"shared_words": len(a & b), "tv": str(tv), "accuracy": str(accuracy)}
            if side == "00":
                primary[f"{law}-{route}"] = controls
    assert all(not row["zero_error"] for row in pooled.values())
    assert dict(count) == {"parity": 20, "nae": 0}
    assert primary["nae-interrupted"]["J"]["tv"] == "31/5488"
    return primary, dict(count)


def audit():
    blobs = {path: path.read_bytes() for path in PINNED}
    assert {path: sha256(data).hexdigest() for path, data in blobs.items()} == PINNED
    grown, support, witness = (json.loads(gzip.decompress(blobs[DATA / name]))
                              for name in ("growth.json.gz", "supports.json.gz", "whole_words.json.gz"))
    frames = {(law, route): Ledger(grown, law, route) for law, route in product(LAWS, ROUTES)}
    for law in LAWS:
        base, interrupted, sham = (frames[law, route] for route in ROUTES)
        assert base.stages == sham.stages and base.births == sham.births
        assert [i for i, (x, y) in enumerate(zip(base.stars, interrupted.stars, strict=True)) if x != y] == [162, 164]
        assert [base.owners[-1][d] for d in (A, B, SPARE)] == [{80, 162}, {80, 163}, {80, 164}]
        assert [interrupted.owners[-1][d] for d in (A, B, SPARE)] == [{80, 164}, {80, 163}, {80, 162}]
        row = support["laws"][law]
        expected = ["".join(map(str, word)) for word in product((0, 1), repeat=3) if valid(law, sum(word), 3)]
        assert row["allowed"] == expected and row["K1_K2_K3"]
        assert all(len({word[:i] + word[i + 1:] for word in expected}) == 4 for i in range(3))
    old_domain, old = old_pairs(grown, support, witness, json.loads(blobs[ARCHIVE]))
    reads, pooled = audit_projections(support, frames, old)
    witness_rows, whole, coupled = verify_witnesses(witness, support, frames, reads, old_domain, old)
    primary, distinguished = confirm_controls(frames, reads, pooled, old)
    return {
        "passed": True,
        "audit_class": "V1 independently authored same-task replay",
        "input_sha256": {str(path.relative_to(ROOT)): digest for path, digest in PINNED.items()},
        "paired_cells": len(reads),
        "unknown_reference_pools": len(pooled),
        "whole_witness_rows": witness_rows,
        "whole_assignments_checked": whole,
        "shared_R_records_with_matched_whole_witnesses": coupled,
        "zero_error_cells_under_fixed_reference": distinguished,
        "primary_00_results_from_recomputed_kernel": primary,
        "whole_holding_count": len(frames["parity", "intact"].stars),
        "witness_replay_checks": [
            "Every reached holding and actual paid name, including triple payments",
            "Same complete early word per paired action and only the enrolled old exchange",
            "Own fresh positions and anonymous positive FINISH, with hidden inputs conserved",
            "Common whole fresh assignment in not-all-equal and two actual hidden compensation marks in parity",
            "One global recoding and local reversal for the saved representative in each law and route",
        ],
    }


if __name__ == "__main__":
    output = DATA / "verification.json"
    output.write_text(json.dumps(audit(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(sha256(output.read_bytes()).hexdigest(), output)
