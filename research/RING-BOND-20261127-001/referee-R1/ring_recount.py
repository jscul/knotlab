"""Exact agreement images on the three-knot ring and its ordinary growth."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from pathlib import Path
import sys

import numpy as np


STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY.parent / "NAE-LAYER-20261127-001" / "referee-R1"))
from growth_rule import advance


SOURCE = ((0, 1, 3), (1, 2, 4), (0, 2, 5))
WORDS = tuple(product((0, 1), repeat=3))
WORD_NAMES = tuple("".join(map(str, word)) for word in WORDS)


@cache
def rings_with_births(max_round=5):
    stages = [SOURCE]
    births = []
    for _ in range(max_round):
        grown = advance(stages[-1])
        if grown.status != "funded":
            break
        stages.append(grown.supports)
        births.append(grown.births)
    return tuple(stages), tuple(births)


def ring_stages(max_round=5):
    return rings_with_births(max_round)[0]


def bitset(bits):
    return int.from_bytes(np.packbits(bits, bitorder="little").tobytes(), "little")


@dataclass(frozen=True)
class Reading:
    carrier: tuple[int, ...]
    used: tuple[int, ...]
    offsets: tuple[int, ...]
    label: str


@dataclass(frozen=True)
class Bond:
    readings: tuple[Reading, ...]
    missing: tuple[str, ...]
    essential: tuple[int, ...]

    def carrier_image(self):
        order = sorted(range(3), key=lambda i: self.readings[i].carrier)
        carriers = tuple(self.readings[i].carrier for i in order)
        missing = tuple(sorted("".join(word[i] for i in order) for word in self.missing))
        return carriers, missing


class Stage:
    def __init__(self, supports, *, law="nae"):
        self.supports = supports
        self.names = tuple(sorted(set().union(*map(set, supports))))
        self.positions = {x: i for i, x in enumerate(self.names)}
        self.law = law
        # Fix the smallest distinction to zero. The other half is its
        # global complement. Parity is complement invariant only at even arity.
        self.complement = law == "nae" or all(len(knot) % 2 == 0 for knot in supports)
        values = np.arange(1 << (len(self.names) - self.complement), dtype=np.uint32)
        if self.complement:
            values <<= 1
        violations = np.zeros(values.size, dtype=np.uint8)
        culprit = np.full(values.size, -1, dtype=np.int16)
        for index, knot in enumerate(supports):
            mask = self.mask(knot)
            restricted = values & mask
            if law == "nae":
                bad = (restricted == 0) | (restricted == mask)
            elif law == "parity":
                bad = np.zeros(values.size, dtype=bool)
                for x in knot:
                    bad ^= ((values >> self.positions[x]) & 1).astype(bool)
            else:
                raise ValueError(law)
            violations += bad
            culprit[bad] = index
        keep = violations <= 1
        self.values = values[keep]
        self.culprit = culprit[keep]
        self.allowed = self.culprit == -1
        self.allowed_values = self.values[self.allowed]
        self.allowed_bitset = bitset(self.allowed)
        self.deletions = tuple(bitset(self.culprit == i) for i in range(len(supports)))
        self.all_rows = (1 << len(self.values)) - 1
        self.normalized_knot_states = tuple(self.group_codes(knot) for knot in supports)

    def mask(self, carrier):
        return sum(1 << self.positions[x] for x in carrier)

    def group_codes(self, distinctions):
        """Index each local pattern, identifying global complements when admitted."""
        restricted = self.allowed_values & self.mask(distinctions)
        code = np.zeros(restricted.size, dtype=np.int16)
        if self.complement:
            reference = restricted >> self.positions[distinctions[0]]
            distinctions = distinctions[1:]
        else:
            reference = 0
        for i, x in enumerate(distinctions):
            code |= (((restricted >> self.positions[x]) ^ reference) & 1).astype(np.int16) << i
        return code

    def reading_values(self, reading, values):
        first, *rest = reading.used
        differences = (values >> self.positions[first]) ^ reading.offsets[0]
        truth = np.ones(values.size, dtype=bool)
        for x, offset in zip(rest, reading.offsets[1:], strict=True):
            truth &= ((differences ^ (values >> self.positions[x]) ^ offset) & 1) == 0
        return truth

    @staticmethod
    def has_two_readings_at_one_pattern(codes, truth):
        yes = np.bincount(codes[truth], minlength=1 + int(codes.max()))
        no = np.bincount(codes[~truth], minlength=len(yes))
        return (yes.astype(bool) & no.astype(bool)).any()

    def unread(self, allowed_truth):
        return all(self.has_two_readings_at_one_pattern(codes, allowed_truth)
                   for codes in self.normalized_knot_states)

    def redundant_places(self, reading):
        truth = self.reading_values(reading, self.allowed_values)
        return tuple(x for x in reading.carrier if not self.has_two_readings_at_one_pattern(
            self.group_codes(tuple(y for y in reading.carrier if y != x)), truth))

    def determined_at(self, reading):
        truth = self.reading_values(reading, self.allowed_values)
        holders = []
        for i, codes in enumerate(self.normalized_knot_states):
            yes = set(codes[truth])
            no = set(codes[~truth])
            if yes.isdisjoint(no):
                holders.append(i)
        return tuple(holders)

    def candidate_readings(self, sizes, forms, include_readable):
        for size in sizes:
            for carrier in combinations(self.names, size):
                if forms == "flip" and size == 3:
                    variants = tuple(((0, p, p ^ q), f"{p}{q}") for p, q in product((0, 1), repeat=2))
                else:
                    variants = (((0,) * size, "="),)
                used = carrier[:3] if forms == "padded" else carrier
                for offsets, label in variants:
                    reading = Reading(carrier, used, offsets[:len(used)], label)
                    values = self.reading_values(reading, self.allowed_values)
                    if values.any() and not values.all():
                        unread = self.unread(values)
                        if unread or include_readable:
                            yield reading, values, unread

    def missing(self, readings):
        positive = [bitset(self.reading_values(r, self.allowed_values)) for r in readings]
        all_allowed = (1 << len(self.allowed_values)) - 1
        signs = [(value ^ all_allowed, value) for value in positive]
        return tuple(name for word, name in zip(WORDS, WORD_NAMES, strict=True)
                     if not signs[0][word[0]] & signs[1][word[1]] & signs[2][word[2]])


def all_pair_images(left, right):
    return all(a & b for a in left for b in right)


def scan(stage, *, sizes=(2, 3), forms="agree", include_readable=False, prefix=None):
    """Screen by witnessed states, then decide remaining cells with exact integer masks.

    A witness may establish presence only. Unobserved cells go to the exhaustive
    check, so the witness selection affects performance and leaves the image exact.
    """
    cohort = list(stage.candidate_readings(sizes, forms, include_readable))
    counters = Counter({"nonconstant readings in scan": len(cohort)})
    if len(cohort) < 3:
        return [], counters
    readings, values, unread = zip(*cohort, strict=True)
    counters["unread readings in scan"] = sum(unread)
    count = len(readings)
    supports = np.array([stage.mask(r.carrier) for r in readings], dtype=np.uint32)
    pairs = np.triu((supports[:, None] & supports[None, :]) == 0, 1)
    exact = tuple((bitset(~v), bitset(v)) for v in values)
    for a, b in np.argwhere(pairs):
        if not all_pair_images(exact[a], exact[b]):
            pairs[a, b] = False

    block_size = min(384, len(stage.allowed_values))
    witness_rows = np.random.default_rng(19483).choice(len(stage.allowed_values), block_size, replace=False)
    packed = np.zeros((2, count, (block_size + 63) // 64), dtype=np.uint64)
    for i, row in enumerate(values):
        for block, start in enumerate(range(0, block_size, 64)):
            selected = row[witness_rows[start:start + 64]]
            packed[0, i, block] = bitset(~selected)
            packed[1, i, block] = bitset(selected)

    kept_signs = {}

    def deletion_signs(i):
        if i not in kept_signs:
            yes = bitset(stage.reading_values(readings[i], stage.values))
            kept_signs[i] = (stage.all_rows ^ yes, yes)
        return kept_signs[i]

    bonds = []
    for a in range(count if prefix is None else min(prefix, count)):
        possible = np.flatnonzero(pairs[a])
        left_positions, right_positions = np.nonzero(pairs[np.ix_(possible, possible)])
        if left_positions.size == 0:
            continue
        left, right = possible[left_positions], possible[right_positions]
        counters["pair-free disjoint triples"] += len(left)
        missing = {}
        for code, (x, y, z) in enumerate(WORDS):
            remaining = np.arange(len(left))
            for block in range(packed.shape[2]):
                matches = packed[x, a, block] & packed[y, left[remaining], block] & packed[z, right[remaining], block]
                remaining = remaining[matches == 0]
                if len(remaining) == 0:
                    break
            head = exact[a][x]
            for index in remaining:
                b, c = left[index], right[index]
                if not head & exact[b][y] & exact[c][z]:
                    missing.setdefault(int(index), []).append(code)

        for index, missing_codes in sorted(missing.items()):
            b, c = left[index], right[index]
            if not (unread[a] and unread[b] and unread[c]):
                counters["excluded only for readability"] += 1
                continue
            signs = [deletion_signs(i) for i in (a, b, c)]
            restored = 0
            for code in missing_codes:
                x, y, z = WORDS[code]
                restored |= signs[0][x] & signs[1][y] & signs[2][z]
            assert not (restored & stage.allowed_bitset)
            essential = tuple(i for i, deleted in enumerate(stage.deletions) if restored & deleted)
            bonds.append(Bond((readings[a], readings[b], readings[c]),
                              tuple(WORD_NAMES[code] for code in missing_codes), essential))
    return bonds, counters


def find_bonds(supports):
    """Return the exact bond images in lexicographic carrier order."""
    bonds, _ = scan(Stage(supports))
    return dict(bond.carrier_image() for bond in bonds)


def connected(holders, supports):
    reached = {holders[0]} if holders else set()
    while True:
        known = set().union(*(set(supports[i]) for i in reached))
        next_reached = reached | {i for i in holders if known.intersection(supports[i])}
        if next_reached == reached:
            return len(reached) == len(holders)
        reached = next_reached


def candidates_by_holders(supports, cap=4, per_size=None):
    candidate = {}
    alternatives = defaultdict(list)
    for size in range(1, min(cap, len(supports)) + 1):
        visited = 0
        for holders in combinations(range(len(supports)), size):
            if not connected(holders, supports):
                continue
            if per_size is not None and visited >= per_size:
                break
            visited += 1
            bonds, _ = scan(Stage(tuple(supports[i] for i in holders)))
            for bond in bonds:
                if len(bond.essential) != size:
                    continue
                key, image = bond.carrier_image()
                alternatives[key].append((image, holders))
                candidate.setdefault(key, (image, holders))
    return candidate, alternatives
