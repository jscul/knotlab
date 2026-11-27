"""Read selected archived relations by exact finite enumeration."""

import argparse
from collections import Counter, defaultdict
from functools import cached_property
from itertools import combinations, product
import json

from growth_audit import RESEARCH, STARTS, UPPER, advance, ordinary_stages, rows, scan_stage, start_number, supports_of


RING_RECORDS = RESEARCH / "RING-BOND-20261127-001" / "referee-R1"
PAIR_WORDS = set(product((0, 1), repeat=2))
TRIPLE_WORDS = set(product((0, 1), repeat=3))


def intersection(bitsets):
    first, *rest = bitsets
    for bits in rest:
        first &= bits
    return first


def words(allowed, distinctions):
    cells = {(): allowed}
    for truth in distinctions:
        later = {}
        for word, assignments in cells.items():
            for value, part in enumerate((assignments & ~truth, assignments & truth)):
                if part:
                    later[word + (value,)] = part
        cells = later
    return cells


def named(cells):
    return {"".join(map(str, word)): bits.bit_count() for word, bits in sorted(cells.items())}


def free_pairs(image):
    return all({(word[i], word[j]) for word in image} == PAIR_WORDS for i, j in combinations(range(3), 2))


class Stage:
    def __init__(self, supports):
        self.supports = supports
        self.count = len({name for row in supports for name in row})
        assert set(range(self.count)) == {name for row in supports for name in row}
        all_states = (1 << (1 << self.count)) - 1
        self.ones = tuple((all_states // (1 + (1 << (1 << x)))) << (1 << x) for x in range(self.count))
        self.zeros = tuple(all_states ^ ones for ones in self.ones)
        self.laws = tuple(all_states ^ self.agreement(row) for row in self.supports)
        self.allowed = intersection(self.laws)

    def agreement(self, carrier):
        return intersection(self.ones[x] for x in carrier) | intersection(self.zeros[x] for x in carrier)

    @cached_property
    def fixing_cells(self):
        return tuple(tuple(words(self.allowed, [self.ones[x] for x in knot]).values()) for knot in self.supports)

    @cached_property
    def single_flips(self):
        return tuple(self.allowed & zeros & (self.allowed >> (1 << x)) for x, zeros in enumerate(self.zeros))

    def unread(self, carrier, truth):
        switches = set()
        for x in carrier:
            if self.single_flips[x] & (truth ^ (truth >> (1 << x))):
                switches.add(x)
        for knot, fixes in zip(self.supports, self.fixing_cells, strict=True):
            if switches.difference(knot):
                continue
            if not any((fix & truth) and (fix & ~truth) for fix in fixes):
                return False
        return True


def exact_pair_clauses(stage):
    """Find every one-word bond using three pair carriers."""
    carriers = []
    states = []
    for carrier in combinations(range(stage.count), 2):
        truth = stage.agreement(carrier)
        if stage.unread(carrier, truth):
            carriers.append(sum(1 << x for x in carrier))
            states.append((stage.allowed & ~truth, stage.allowed & truth))
    free = defaultdict(dict)
    for left, right in combinations(range(len(carriers)), 2):
        if carriers[left] & carriers[right]:
            continue
        cells = tuple(x & y for x, y in product(states[left], states[right]))
        if all(cells):
            free[left][right] = cells
    clauses = set()
    for left, partners in free.items():
        for middle, cells in partners.items():
            for right in partners.keys() & free.get(middle, {}).keys():
                missing = [code for code, (cell, value) in enumerate(product(cells, states[right])) if not cell & value]
                if len(missing) == 1:
                    code = missing[0]
                    clauses.add((2 * left + (code >> 2), 2 * middle + ((code >> 1) & 1), 2 * right + (code & 1)))
    return carriers, clauses


def boxes_from_clauses(carriers, clauses):
    alternatives = defaultdict(set)
    for clause in clauses:
        for member in clause:
            alternatives[tuple(x for x in clause if x != member)].add(member)
    boxes = set()
    for a, b, c in clauses:
        original = carriers[a // 2] | carriers[b // 2] | carriers[c // 2]
        for other_a in alternatives[b, c]:
            mask_a = carriers[other_a // 2]
            if other_a <= a or original & mask_a:
                continue
            for other_b in alternatives[a, c]:
                mask_b = carriers[other_b // 2]
                if other_b <= b or (original | mask_a) & mask_b:
                    continue
                for other_c in alternatives[a, b]:
                    if other_c <= c or (original | mask_a | mask_b) & carriers[other_c // 2]:
                        continue
                    groups = (a, other_a), (b, other_b), (c, other_c)
                    if all(tuple(sorted(word)) in clauses for word in product(*groups)):
                        boxes.add(groups)
    return boxes


def pair_only_census(limit):
    starts = json.loads(STARTS.read_text())
    counts = defaultdict(Counter)
    examined = 0
    detailed = []
    for path in sorted((UPPER / "out").glob("census_*.jsonl")):
        for record in rows(path):
            number = start_number(record)
            if not any(row["distinctions"] == 12 for row in record["rounds"]):
                continue
            reconstructed, _ = ordinary_stages(supports_of(starts[number]))
            for turn, (row, supports) in enumerate(zip(record["rounds"], reconstructed, strict=True)):
                if row["distinctions"] != 12 or (limit is not None and examined >= limit):
                    continue
                examined += 1
                stage = Stage(supports)
                carriers, clauses = exact_pair_clauses(stage)
                boxes = boxes_from_clauses(carriers, clauses)
                assert len(clauses) <= row["bonds"]
                for scope in ("all", f"round {turn}"):
                    tally = counts[scope]
                    tally["stages"] += 1
                    tally["stages with eight or more exact eligible clauses"] += len(clauses) >= 8
                    tally["exact eligible clauses"] += len(clauses)
                    tally["stages with boxes"] += bool(boxes)
                    tally["boxes"] += len(boxes)
                if boxes:
                    detailed.append({"start": number, "round": turn, "supports": supports, "boxes": sorted(boxes)})
    return {"counts": counts, "positive rows": detailed}


def replay(supports, groups, missing):
    stage = Stage(supports)
    carriers = sum(groups, [])
    truths = [stage.agreement(carrier) for carrier in carriers]
    assert all(stage.unread(carrier, truth) for carrier, truth in zip(carriers, truths, strict=True))
    signed = [2 * index + value for index, value in enumerate(missing)]
    signed_products = set(product(signed[:2], signed[2:4], signed[4:]))
    lower_image = words(stage.allowed, truths)
    lower_clauses = []
    for clause in combinations(range(6), 3):
        if any(set(carriers[i]) & set(carriers[j]) for i, j in combinations(clause, 2)):
            continue
        image = {tuple(word[x] for x in clause) for word in lower_image}
        if len(image) == 7 and free_pairs(image):
            lack, = TRIPLE_WORDS.difference(image)
            lower_clauses.append(tuple(2 * index + value for index, value in zip(clause, lack, strict=True)))
    assert set(lower_clauses) == signed_products

    # Checking the pattern extractor on the same eight signed clauses does not
    # depend on n=12, where all six carriers are pairs.
    masks = [sum(1 << x for x in carrier) for carrier in carriers]
    full_box = bool(boxes_from_clauses(masks, signed_products))
    assert full_box == (len(set().union(*map(set, carriers))) == sum(map(len, carriers)))

    e = [~(x ^ y) if a == b else x ^ y for x, y, a, b in zip(
        truths[::2], truths[1::2], missing[::2], missing[1::2], strict=True)]
    image = words(stage.allowed, e)
    assert len(image) == 7 and free_pairs(image)
    upper_missing, = TRIPLE_WORDS.difference(image)
    deletion = {}
    for k in range(len(supports)):
        removed = words(intersection(law for i, law in enumerate(stage.laws) if k != i), e)
        deletion[k] = removed.get(upper_missing, 0).bit_count()
    return {"supports": supports, "loose distinctions": scan_stage(supports)["loose distinctions"],
            "agreement carriers": groups, "disjoint lower carriers": full_box,
            "lower clauses": len(lower_clauses), "lower word counts": named(lower_image),
            "upper word counts": named(image), "absent upper word": "".join(map(str, upper_missing)),
            "restored assignments after deletion of each law": deletion}


def earlier_witnesses():
    closed = json.loads((RING_RECORDS / "layer_witness.json").read_text())
    carriers = closed["lower_carriers_in_A0_A1_B0_B1_C0_C1_order"]
    closed_replay = replay(tuple(map(tuple, closed["source_knots_not_all_equal"])),
                          [carriers[i:i + 2] for i in range(0, 6, 2)], [1] * 6)
    assert sum(closed_replay["upper word counts"].values()) == closed["allowed_source_states"] == 7570
    assert len(closed_replay["lower word counts"]) == 37
    assert all(closed_replay["restored assignments after deletion of each law"].values())

    earlier_ring = json.loads((RING_RECORDS / "layer_ring_search.json").read_text())
    deletions = json.loads((RING_RECORDS / "ring_upper_deletions.json").read_text())
    start = ((0, 1, 3), (1, 2, 4), (0, 2, 5))
    supports = start
    for i in range(3):
        step = advance(supports)
        assert step.status == "funded", i
        supports = step.supports
    ring = earlier_ring["round_3_overlap"]
    assert supports == tuple(map(tuple, ring["stage"])) == tuple(map(tuple, deletions["stage"]))
    witness = ring["witness"]
    ring_replay = replay(supports, witness["six_lower_carriers_grouped_into_upper_pairs"],
                         witness["signed_values_in_the_eight_forbidden_words"])
    assert not ring_replay["disjoint lower carriers"]
    assert len(ring_replay["lower word counts"]) == 25
    assert ring_replay["upper word counts"] == deletions["upper counts"]
    assert list(ring_replay["restored assignments after deletion of each law"].values()) == deletions["restored 000 after deleting each source law"]
    return {"closed disjoint witness": closed_replay, "open ordinary grown ring": ring_replay}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    print(json.dumps({"all recorded 12-distinction stages": pair_only_census(args.limit),
                      "earlier witnesses": earlier_witnesses()}, indent=2))


if __name__ == "__main__":
    main()
