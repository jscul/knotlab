"""A depth-three reward tree with receipts and fitted tests held in ternary words."""

from __future__ import annotations

from collections import defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path


# This immutable predecessor supplies both the window sensor and the holding law.
HOLDING_SOURCE = (Path(__file__).resolve().parents[2] / "PIXEL-LETTERS-20261122-001"
                  / "PIXEL-LETTERS-20261122-001-E001_letters" / "learner.py")
_spec = spec_from_file_location("relative_pixel_holding", HOLDING_SOURCE)
_holding = module_from_spec(_spec)
_spec.loader.exec_module(_holding)

OPEN_RELATIONS = _holding.OPEN_RELATIONS
TRAINING_LIMIT = 64
DEPTH_LIMIT = 3
MEMORY_SCHEMA = "pixel-knot-tree-v1"
SIDE = _holding.SIDE
PIXELS = SIDE ** 2
FEATURE_COUNTS = {"position": PIXELS, "window": _holding.PATTERN_COUNT}

# Packed words are 4*mark + 2*dock + read. Each register is least-significant first.
_TRIPLES = tuple(product((0, 1), repeat=3))
_RECEIPT_WIDTH = 2 + PIXELS  # occupied, rewarded action, raw row-major bitmap
_TREE_START = 1 + TRAINING_LIMIT * _RECEIPT_WIDTH
_TAG_WIDTH = 2
_FEATURE_WIDTH = (PIXELS - 1).bit_length()
_THRESHOLD_WIDTH = _holding.WINDOW_COUNT.bit_length()
_NODE_WIDTH = _TAG_WIDTH + _FEATURE_WIDTH + _THRESHOLD_WIDTH
_NODE_COUNT = (1 << (DEPTH_LIMIT + 1)) - 1
HOLDING_COUNT = _TREE_START + _NODE_COUNT * _NODE_WIDTH
_BRANCH = 3


def _bitmap(pixels):
    bits = tuple(pixels)
    if len(bits) != PIXELS or any(type(bit) not in (int, bool) or bit not in (0, 1) for bit in bits):
        raise ValueError("Expected 64 row-major bits")
    return bits


def features(pixels, sensor) -> tuple[int, ...]:
    """Read padded anonymous window counts or the same occupied offsets from row/column minima."""
    if type(sensor) is not str or sensor not in FEATURE_COUNTS:
        raise ValueError("Expected position or window sensor")
    if sensor == "window":
        return _holding.pattern_counts(pixels)
    occupied = [divmod(index, SIDE) for index, bit in enumerate(_bitmap(pixels)) if bit]
    relative = [0] * PIXELS
    if occupied:
        first_row = min(row for row, _ in occupied)
        first_col = min(col for _, col in occupied)
        for row, col in occupied:
            relative[(row - first_row) * SIDE + col - first_col] = 1
    return tuple(relative)


def _best_split(rows):
    count = len(rows)
    ones = sum(action for _, action in rows)
    if ones in (0, count):
        return None

    best = None
    best_numerator, best_denominator = 0, 1
    for index in range(len(rows[0][0])):
        buckets = defaultdict(lambda: [0, 0])
        for vector, action in rows:
            bucket = buckets[vector[index]]
            bucket[0] += 1
            bucket[1] += action
        left_count = left_ones = 0
        for threshold, (size, positive) in sorted(buckets.items()):
            left_count += size
            left_ones += positive
            right_count = count - left_count
            if not right_count:
                break
            # Weighted Gini decrease is this ratio multiplied by 2/count**2.
            numerator = (left_count * ones - count * left_ones) ** 2
            denominator = left_count * right_count
            if numerator * best_denominator > best_numerator * denominator:
                best_numerator, best_denominator = numerator, denominator
                best = (index, threshold)
    return best


def _fit_tree(rows, depth=0):
    split = _best_split(rows) if depth < DEPTH_LIMIT else None
    if split is None:
        return {"vote": int(2 * sum(action for _, action in rows) > len(rows))}
    index, threshold = split
    left, right = [], []
    for row in rows:
        (left if row[0][index] <= threshold else right).append(row)
    return {"feature": index, "threshold": threshold,
            "left": _fit_tree(left, depth + 1), "right": _fit_tree(right, depth + 1)}


def _packed(triple):
    mark, dock, read = triple
    return 4 * mark + 2 * dock + read


def _check_export(memory):
    if (type(memory) is not dict or set(memory) != {"schema", "law", "sensor", "training_limit", "words"}
            or memory["schema"] != MEMORY_SCHEMA or type(memory["training_limit"]) is not int
            or memory["training_limit"] != TRAINING_LIMIT):
        raise ValueError("Invalid fitted tree memory schema")


class KnotTree:
    """Use either input sensor with the same fitted tree and holding operations."""

    __slots__ = ("_law", "_sensor", "_zero", "_words")

    def __init__(self, law, sensor):
        if type(law) is not str or law not in OPEN_RELATIONS:
            raise ValueError("Expected parity or nae law")
        if type(sensor) is not str or sensor not in FEATURE_COUNTS:
            raise ValueError("Expected position or window sensor")
        self._law = law
        self._sensor = sensor
        self._zero = _packed(_holding._admit_word(law, *_holding._MARK_DOCK_PAIRS[law][0]))
        self._words = self._neutral(HOLDING_COUNT)

    def _neutral(self, count):
        return bytes([self._zero]) * count

    def _read(self, words, address, width=1):
        register = tuple(_TRIPLES[code] for code in words[address:address + width])
        return _holding._read_register(self._law, register)

    def _write(self, words, address, width, value):
        register = tuple(_TRIPLES[code] for code in words[address:address + width])
        offered = _holding._write_register(self._law, register, value)
        words[address:address + width] = bytes(map(_packed, offered))

    def _earned(self, words):
        counts = [0, 0]
        for address in range(1, _TREE_START, _RECEIPT_WIDTH):
            if not self._read(words, address):
                break
            counts[self._read(words, address + 1)] += 1
        return counts

    def learn(self, pixels, guessed, correct):
        if (type(guessed) not in (int, bool) or guessed not in (0, 1)
                or type(correct) not in (int, bool) or correct not in (0, 1)):
            raise ValueError("Guess and correctness must be bits")
        source = self._words
        if self._read(source, 0):
            raise ValueError("The fitted tree is locked for deployment")
        bits = _bitmap(pixels)
        counts = self._earned(source)
        if guessed != int(counts[1] > counts[0]):
            raise ValueError("Feedback must refer to the reader's current guess")
        accepted = sum(counts)
        if accepted == TRAINING_LIMIT:
            raise ValueError("Training limit reached")
        address = 1 + accepted * _RECEIPT_WIDTH
        words = bytearray(source)
        self._write(words, address, 1, 1)
        self._write(words, address + 1, 1, int(guessed) if correct else 1 - guessed)
        self._write(words, address + 2, PIXELS, sum(bit << index for index, bit in enumerate(bits)))
        self._words = bytes(words)

    def finalize(self):
        """Fit once using only the marked receipts, then clear them before deployment."""
        source = self._words
        if self._read(source, 0):
            raise ValueError("The fitted tree is already locked")
        if sum(self._earned(source)) != TRAINING_LIMIT:
            raise ValueError("Finalize requires exactly 64 rewarded presentations")
        training = []
        for address in range(1, _TREE_START, _RECEIPT_WIDTH):
            bitmap = self._read(source, address + 2, PIXELS)
            bits = tuple((bitmap >> index) & 1 for index in range(PIXELS))
            training.append((features(bits, self._sensor), self._read(source, address + 1)))
        tree = _fit_tree(training)
        words = bytearray(self._neutral(HOLDING_COUNT))
        self._write(words, 0, 1, 1)
        self._write_tree(words, 0, tree)
        self._words = bytes(words)
        return self.describe()

    def _write_tree(self, words, index, tree):
        address = _TREE_START + index * _NODE_WIDTH
        if "vote" in tree:
            self._write(words, address, _TAG_WIDTH, tree["vote"] + 1)
            return
        self._write(words, address, _TAG_WIDTH, _BRANCH)
        self._write(words, address + _TAG_WIDTH, _FEATURE_WIDTH, tree["feature"])
        self._write(words, address + _TAG_WIDTH + _FEATURE_WIDTH, _THRESHOLD_WIDTH, tree["threshold"])
        self._write_tree(words, 2 * index + 1, tree["left"])
        self._write_tree(words, 2 * index + 2, tree["right"])

    def _node(self, words, index, depth):
        address = _TREE_START + index * _NODE_WIDTH
        tag = self._read(words, address, _TAG_WIDTH)
        feature = self._read(words, address + _TAG_WIDTH, _FEATURE_WIDTH)
        threshold = self._read(words, address + _TAG_WIDTH + _FEATURE_WIDTH, _THRESHOLD_WIDTH)
        if not tag:
            raise ValueError("A reachable tree holding is vacant")
        if tag != _BRANCH and (feature or threshold):
            raise ValueError("A terminal holding contains a split test")
        if tag == _BRANCH:
            maximum = 1 if self._sensor == "position" else _holding.WINDOW_COUNT
            if depth >= DEPTH_LIMIT or feature >= FEATURE_COUNTS[self._sensor] or threshold >= maximum:
                raise ValueError("Stored split exceeds the registered tree or sensor bounds")
        return tag, feature, threshold

    def _describe_tree(self, words):
        visited = set()

        def descend(index, depth):
            visited.add(index)
            tag, feature, threshold = self._node(words, index, depth)
            if tag != _BRANCH:
                return {"vote": tag - 1}
            return {"feature": feature, "threshold": threshold,
                    "left": descend(2 * index + 1, depth + 1), "right": descend(2 * index + 2, depth + 1)}

        tree = descend(0, 0)
        for index in range(_NODE_COUNT):
            address = _TREE_START + index * _NODE_WIDTH
            if index not in visited and words[address:address + _NODE_WIDTH] != self._neutral(_NODE_WIDTH):
                raise ValueError("Unreachable tree holdings are occupied")
        return tree

    def describe(self):
        words = self._words
        if not self._read(words, 0):
            raise ValueError("Finalize receipts before reading tree tests")
        return self._describe_tree(words)

    def explain(self, pixels):
        vector = features(pixels, self._sensor)
        words = self._words
        path = []
        if not self._read(words, 0):
            counts = self._earned(words)
            return {"guess": int(counts[1] > counts[0]), "features": list(vector), "path": path}
        index, depth = 0, 0
        while True:
            tag, feature, threshold = self._node(words, index, depth)
            if tag != _BRANCH:
                return {"guess": tag - 1, "features": list(vector), "path": path}
            value = vector[feature]
            go_left = value <= threshold
            path.append({"feature": feature, "threshold": threshold, "value": value,
                         "branch": "left" if go_left else "right"})
            index = 2 * index + (1 if go_left else 2)
            depth += 1

    def predict(self, pixels):
        return self.explain(pixels)["guess"]

    def export_memory(self):
        return {"schema": MEMORY_SCHEMA, "law": self._law, "sensor": self._sensor,
                "training_limit": TRAINING_LIMIT, "words": self._words.hex()}

    @classmethod
    def from_memory(cls, memory):
        _check_export(memory)
        reader = cls(memory["law"], memory["sensor"])
        reader.restore_memory(memory)
        return reader

    def restore_memory(self, memory):
        _check_export(memory)
        if (memory["law"], memory["sensor"]) != (self._law, self._sensor):
            raise ValueError("Memory law and sensor must match the reader")
        raw = memory["words"]
        if type(raw) is not str or len(raw) != 2 * HOLDING_COUNT:
            raise ValueError("Invalid packed holding roster")
        words = bytes.fromhex(raw)
        if words.hex() != raw:
            raise ValueError("Invalid packed holding encoding")
        for code in set(words):
            if code >= len(_TRIPLES):
                raise ValueError("Packed holding is outside the three-bit roster")
            self._read(bytes([code]), 0)
        if self._read(words, 0):
            if words[1:_TREE_START] != self._neutral(_TREE_START - 1):
                raise ValueError("A deployed tree must have erased all receipt holdings")
            self._describe_tree(words)
        else:
            first_unoccupied = 1 + sum(self._earned(words)) * _RECEIPT_WIDTH
            if words[first_unoccupied:] != self._neutral(HOLDING_COUNT - first_unoccupied):
                raise ValueError("Acquisition state contains unexpected later holdings")
        self._words = words

    def clear_memory(self):
        outgoing = self.export_memory()
        self._words = self._neutral(HOLDING_COUNT)
        return outgoing

    def prepare_holding(self, address, word):
        """Offer a complete word at one diagnostic address under the full law."""
        if type(address) is not int or not 0 <= address < HOLDING_COUNT:
            raise ValueError("Invalid holding address")
        if len(word) != 3 or any(type(bit) is not int or bit not in (0, 1) for bit in word):
            raise ValueError("Expected a complete three-bit holding")
        admitted = _holding._admit_holding(self._law, *word)
        words = bytearray(self._words)
        words[address] = _packed(admitted)
        self._words = bytes(words)
