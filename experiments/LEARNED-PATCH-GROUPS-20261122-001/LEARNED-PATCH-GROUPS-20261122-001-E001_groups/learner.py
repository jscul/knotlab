"""Fit an exact committee of histogram partitions and retain it in ternary holdings."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from math import gcd
from pathlib import Path


_PREDECESSOR = (Path(__file__).resolve().parents[2] / "PIXEL-LETTERS-20261122-001"
                / "PIXEL-LETTERS-20261122-001-E001_letters" / "learner.py")
_spec = spec_from_file_location("checked_pixel_holding", _PREDECESSOR)
_holding = module_from_spec(_spec)
_spec.loader.exec_module(_holding)

pattern_counts = _holding.pattern_counts
OPEN_RELATIONS = _holding.OPEN_RELATIONS
PATTERN_COUNT = _holding.PATTERN_COUNT
WINDOW_COUNT = _holding.WINDOW_COUNT
TRAINING_LIMIT = 64
PARTITION_COUNT = (1 << (PATTERN_COUNT - 1)) - 1
MEMORY_SCHEMA = "pixel-knot-partitions-v1"

# One byte encodes each independent holding as 4*mark + 2*dock + read.
# The fixed address order is phase, receipts, class counts, class totals, then
# one flag for each mask 1..32767. Each mask denotes the side excluding bin 15.
_TRIPLES = tuple(product((0, 1), repeat=3))
_COUNT_WIDTH = WINDOW_COUNT.bit_length()
_RECEIPT_WIDTH = 2 + PATTERN_COUNT * _COUNT_WIDTH  # occupied, earned action, 16 counts
_STATS_START = 1 + TRAINING_LIMIT * _RECEIPT_WIDTH
_CLASS_COUNT_WIDTH = TRAINING_LIMIT.bit_length()
_TOTAL_WIDTH = (TRAINING_LIMIT * WINDOW_COUNT).bit_length()
_CLASS_TOTALS_START = _STATS_START + 2 * _CLASS_COUNT_WIDTH
_FLAGS_START = _CLASS_TOTALS_START + 2 * PATTERN_COUNT * _TOTAL_WIDTH
HOLDING_COUNT = _FLAGS_START + PARTITION_COUNT


def _packed(triple):
    mark, dock, read = triple
    return 4 * mark + 2 * dock + read


def _smaller_side(mask):
    members = mask.bit_count()
    return min(members, PATTERN_COUNT - members)


def _fit_masks(classes):
    """Maximize exact mean separation over within-class variance, retaining all ties."""
    n0, n1 = map(len, classes)
    if not n0 or not n1:
        return [], 0, 1
    columns = [list(zip(*rows, strict=True)) for rows in classes]
    current = [[0] * n0, [0] * n1]
    previous_mask = 0
    selected = []
    best_numerator, best_denominator = 0, 1
    best_size = PATTERN_COUNT

    for index in range(1, PARTITION_COUNT + 1):
        # Gray order changes one anonymous bin at a time. It visits each mask once.
        mask = index ^ (index >> 1)
        changed = mask ^ previous_mask
        previous_mask = mask
        column = changed.bit_length() - 1
        sign = 1 if mask & changed else -1
        for action in (0, 1):
            current[action] = [total + sign * count for total, count in
                               zip(current[action], columns[action][column], strict=True)]

        s0, s1 = map(sum, current)
        numerator = (n1 * s0 - n0 * s1) ** 2
        if not numerator:
            continue
        q0, q1 = (sum(value * value for value in group) for group in current)
        denominator = (n0 * q0 - s0 * s0) * n1 ** 2 + (n1 * q1 - s1 * s1) * n0 ** 2
        # A nonzero numerator over zero ties with all other infinite ranks.
        rank_change = numerator * best_denominator - best_numerator * denominator
        if rank_change < 0:
            continue
        size = _smaller_side(mask)
        if rank_change > 0 or size < best_size:
            best_numerator, best_denominator = numerator, denominator
            best_size = size
            selected = [mask]
        elif size == best_size:
            selected.append(mask)

    divisor = gcd(best_numerator, best_denominator)
    return sorted(selected), best_numerator // divisor, best_denominator // divisor


def _rule_vote(mask, histogram, class_counts, class_totals):
    observed = sum0 = sum1 = 0
    while mask:
        low = mask & -mask
        index = low.bit_length() - 1
        mask ^= low
        observed += histogram[index]
        sum0 += class_totals[0][index]
        sum1 += class_totals[1][index]
    n0, n1 = class_counts
    left = n1 * abs(n0 * observed - sum0)
    right = n0 * abs(n1 * observed - sum1)
    return None if left == right else int(right < left)


def _check_export(memory):
    if (type(memory) is not dict or set(memory) != {"schema", "law", "training_limit", "words"}
            or memory["schema"] != MEMORY_SCHEMA):
        raise ValueError("Invalid partition memory schema")


class KnotLearner:
    """Training updates and deployment keep their state only in addressed holdings."""

    __slots__ = ("_law", "_zero", "_words")

    def __init__(self, law, *, training_limit=TRAINING_LIMIT):
        if type(law) is not str or law not in OPEN_RELATIONS:
            raise ValueError("Expected parity or nae law")
        if type(training_limit) is not int or training_limit != TRAINING_LIMIT:
            raise ValueError("Partition learner has capacity for exactly 64 presentations")
        self._law = law
        self._zero = _packed(_holding._admit_word(law, *_holding._MARK_DOCK_PAIRS[law][0]))
        self._words = self._neutral(HOLDING_COUNT)

    def _neutral(self, size):
        return bytes([self._zero]) * size

    def _read(self, words, address, width=1):
        register = tuple(_TRIPLES[code] for code in words[address:address + width])
        return _holding._read_register(self._law, register)

    def _write(self, words, address, width, value):
        prior = tuple(_TRIPLES[code] for code in words[address:address + width])
        offered = _holding._write_register(self._law, prior, value)
        words[address:address + width] = bytes(map(_packed, offered))

    def _seen(self, words):
        earned = [0, 0]
        for address in range(1, _STATS_START, _RECEIPT_WIDTH):
            if not self._read(words, address):
                break
            earned[self._read(words, address + 1)] += 1
        return earned

    def learn(self, pixels, guessed, correct):
        if (type(guessed) not in (int, bool) or guessed not in (0, 1)
                or type(correct) not in (int, bool) or correct not in (0, 1)):
            raise ValueError("Guess and correctness must be bits")
        source = self._words
        if self._read(source, 0):
            raise ValueError("The fitted selection is locked for deployment")
        histogram = pattern_counts(pixels)
        earned = self._seen(source)
        if guessed != int(earned[1] > earned[0]):
            raise ValueError("Feedback must refer to the learner's current guess")
        learned = sum(earned)
        if learned == TRAINING_LIMIT:
            raise ValueError("Training limit reached")

        action = int(guessed) if correct else 1 - guessed
        address = 1 + learned * _RECEIPT_WIDTH
        words = bytearray(source)
        self._write(words, address, 1, 1)
        self._write(words, address + 1, 1, action)
        for index, count in enumerate(histogram):
            self._write(words, address + 2 + index * _COUNT_WIDTH, _COUNT_WIDTH, count)
        self._words = bytes(words)

    def _receipt_histogram(self, words, address):
        return tuple(self._read(words, address + 2 + index * _COUNT_WIDTH, _COUNT_WIDTH)
                     for index in range(PATTERN_COUNT))

    def _receipt_classes(self, words):
        classes = [[], []]
        for address in range(1, _STATS_START, _RECEIPT_WIDTH):
            if not self._read(words, address):
                break
            classes[self._read(words, address + 1)].append(self._receipt_histogram(words, address))
        return classes

    def finalize(self):
        """Fit once from held receipts, erase their holdings, and return an audit reading."""
        source = self._words
        if self._read(source, 0):
            raise ValueError("The fitted selection is already locked")
        classes = self._receipt_classes(source)
        class_counts = list(map(len, classes))
        if not sum(class_counts):
            raise ValueError("No earned receipt to finalize")
        masks, numerator, denominator = _fit_masks(classes)
        totals = [[sum(row[index] for row in rows) for index in range(PATTERN_COUNT)] for rows in classes]
        words = bytearray(self._neutral(HOLDING_COUNT))
        self._write(words, 0, 1, 1)
        for action in (0, 1):
            self._write(words, _STATS_START + action * _CLASS_COUNT_WIDTH, _CLASS_COUNT_WIDTH,
                        class_counts[action])
            address = _CLASS_TOTALS_START + action * PATTERN_COUNT * _TOTAL_WIDTH
            for index, total in enumerate(totals[action]):
                self._write(words, address + index * _TOTAL_WIDTH, _TOTAL_WIDTH, total)
        self._set_flags(words, masks)
        self._words = bytes(words)
        return {**self.selection(), "rank_numerator": numerator, "rank_denominator": denominator,
                "partitions_scored": PARTITION_COUNT if all(class_counts) else 0}

    def _set_flags(self, words, masks):
        # All flag addresses have the same independent local law. Admit the two
        # offered transitions once, then apply them in bulk at those addresses.
        mark = bytearray(self._neutral(1))
        self._write(mark, 0, 1, 1)
        words[_FLAGS_START:] = self._neutral(PARTITION_COUNT)
        for mask in masks:
            words[_FLAGS_START + mask - 1] = mark[0]

    def _active_masks(self, words):
        flags = words[_FLAGS_START:]
        # Check every distinct held word against the same forcing operation.
        active = [code for code in set(flags) if self._read(bytes([code]), 0)]
        if not active:
            return []
        marker = bytes(active)
        masks = []
        address = flags.find(marker)
        while address >= 0:
            masks.append(address + 1)
            address = flags.find(marker, address + 1)
        return masks

    def _selection(self, words):
        counts = [self._read(words, _STATS_START + action * _CLASS_COUNT_WIDTH, _CLASS_COUNT_WIDTH)
                  for action in (0, 1)]
        totals = [[self._read(words, _CLASS_TOTALS_START + (action * PATTERN_COUNT + index) * _TOTAL_WIDTH,
                              _TOTAL_WIDTH) for index in range(PATTERN_COUNT)] for action in (0, 1)]
        masks = self._active_masks(words)
        return {"masks": masks, "smaller_side_cardinality": _smaller_side(masks[0]) if masks else None,
                "class_counts": counts, "class_totals": totals}

    def selection(self):
        words = self._words
        if not self._read(words, 0):
            raise ValueError("Finalize the acquired receipts before reading the selection")
        return self._selection(words)

    def explain(self, pixels, *, detail=False):
        histogram = pattern_counts(pixels)
        words = self._words
        if not self._read(words, 0):
            votes = self._seen(words)
            return {"phase": "acquisition", "counts": list(histogram), "guess": int(votes[1] > votes[0]),
                    "votes": votes, "abstentions": 0, **({"rule_votes": []} if detail else {})}
        fitting = self._selection(words)
        rule_votes = [_rule_vote(mask, histogram, fitting["class_counts"], fitting["class_totals"])
                      for mask in fitting["masks"]]
        votes = [rule_votes.count(0), rule_votes.count(1)]
        return {"phase": "deployment", "counts": list(histogram), "guess": int(votes[1] > votes[0]),
                "votes": votes, "abstentions": rule_votes.count(None),
                **({"rule_votes": rule_votes} if detail else {})}

    def predict(self, pixels):
        return self.explain(pixels)["guess"]

    def erase_selection(self):
        self.selection()
        words = bytearray(self._words)
        self._set_flags(words, ())
        self._words = bytes(words)

    def use_all_same_size(self):
        size = self.selection()["smaller_side_cardinality"]
        if size is None:
            return
        words = bytearray(self._words)
        self._set_flags(words, (mask for mask in range(1, PARTITION_COUNT + 1) if _smaller_side(mask) == size))
        self._words = bytes(words)

    def swap_actions(self):
        """Exchange the two class names in the held state under the same law."""
        source = self._words
        words = bytearray(source)
        if self._read(source, 0):
            for address, width in ((_STATS_START, _CLASS_COUNT_WIDTH),
                                   (_CLASS_TOTALS_START, PATTERN_COUNT * _TOTAL_WIDTH)):
                center = address + width
                end = center + width
                words[address:end] = source[center:end] + source[address:center]
        else:
            for index in range(sum(self._seen(source))):
                address = 2 + index * _RECEIPT_WIDTH
                self._write(words, address, 1, 1 - self._read(source, address))
        self._validate_words(words)
        self._words = bytes(words)

    def export_memory(self):
        return {"schema": MEMORY_SCHEMA, "law": self._law, "training_limit": TRAINING_LIMIT,
                "words": self._words.hex()}

    @classmethod
    def from_memory(cls, memory):
        _check_export(memory)
        receiver = cls(memory["law"], training_limit=memory["training_limit"])
        receiver.restore_memory(memory)
        return receiver

    def restore_memory(self, memory):
        _check_export(memory)
        if (memory["law"] != self._law or type(memory["training_limit"]) is not int
                or memory["training_limit"] != TRAINING_LIMIT):
            raise ValueError("Memory law and capacity must match the receiver")
        raw = memory["words"]
        if type(raw) is not str or len(raw) != 2 * HOLDING_COUNT:
            raise ValueError("Invalid packed holding roster")
        words = bytes.fromhex(raw)
        if words.hex() != raw:
            raise ValueError("Invalid packed holding encoding")
        self._validate_words(words)
        self._words = words

    def _validate_words(self, words):
        for code in set(words):
            if code >= len(_TRIPLES):
                raise ValueError("Packed holding is outside the three-bit roster")
            self._read(bytes([code]), 0)

        if self._read(words, 0):
            if words[1:_STATS_START] != self._neutral(_STATS_START - 1):
                raise ValueError("Deployment requires erased acquisition words")
            fitted = self._selection(words)
            counts, totals = fitted["class_counts"], fitted["class_totals"]
            if not 1 <= sum(counts) <= TRAINING_LIMIT or any(
                    sum(row) != count * WINDOW_COUNT for count, row in zip(counts, totals, strict=True)):
                raise ValueError("Class totals disagree with the bounded presentation counts")
            if fitted["masks"] and (not all(counts) or any(
                    _smaller_side(mask) != fitted["smaller_side_cardinality"] for mask in fitted["masks"])):
                raise ValueError("Active partition family has inconsistent support or cardinality")
            return

        used = sum(self._seen(words))
        unused_address = 1 + used * _RECEIPT_WIDTH
        if words[unused_address:] != self._neutral(HOLDING_COUNT - unused_address):
            raise ValueError("Acquisition state contains unexpected later holdings")
        for address in range(1, unused_address, _RECEIPT_WIDTH):
            if sum(self._receipt_histogram(words, address)) != WINDOW_COUNT:
                raise ValueError("Occupied receipt does not represent a whole histogram")

    def clear_memory(self):
        outgoing = self.export_memory()
        self._words = self._neutral(HOLDING_COUNT)
        return outgoing

    def prepare_holding(self, address, word):
        """Diagnostic access to one actual holding under the full law."""
        if type(address) is not int or not 0 <= address < HOLDING_COUNT:
            raise ValueError("Invalid holding address")
        if len(word) != 3 or any(type(bit) is not int or bit not in (0, 1) for bit in word):
            raise ValueError("Expected a complete three-bit holding")
        admitted = _holding._admit_holding(self._law, *word)
        words = bytearray(self._words)
        words[address] = _packed(admitted)
        self._words = bytes(words)
