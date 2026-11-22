"""Rewarded 2-by-2 bitmap histograms stored as prepared ternary words."""

from __future__ import annotations

from itertools import product
from types import MappingProxyType


SIDE = 8
PATTERN_COUNT = 16
WINDOW_COUNT = (SIDE + 1) ** 2
MEMORY_SCHEMA = "pixel-knot-histograms-v1"

Word = tuple[int, int, int]
Register = tuple[Word, ...]
Bank = tuple[Register, ...]

_ALL_WORDS = tuple(product((0, 1), repeat=3))
OPEN_RELATIONS = MappingProxyType({
    "parity": frozenset(word for word in _ALL_WORDS if sum(word) % 2 == 0),
    "nae": frozenset(word for word in _ALL_WORDS if 0 < sum(word) < 3),
})
# Bit 0, then bit 1. Each pair must force the read distinction in the full law.
# The third distinction is derived by admission and held as part of the word.
_MARK_DOCK_PAIRS = {"parity": ((1, 1), (0, 1)), "nae": ((1, 1), (0, 0))}


def pattern_counts(pixels) -> tuple[int, ...]:
    """Count all ordered four-bit words after one zero-padding on each side."""
    bits = tuple(pixels)
    if len(bits) != SIDE ** 2 or any(type(bit) not in (int, bool) or bit not in (0, 1)
                                     for bit in bits):
        raise ValueError("Expected 64 row-major bits")
    padding = (0,) * (SIDE + 2)
    rows = [padding]
    rows.extend((0, *bits[start:start + SIDE], 0) for start in range(0, len(bits), SIDE))
    rows.append(padding)
    counts = [0] * PATTERN_COUNT
    for upper, lower in zip(rows[:-1], rows[1:], strict=True):
        for column in range(SIDE + 1):
            word = 8 * upper[column] + 4 * upper[column + 1] + 2 * lower[column] + lower[column + 1]
            counts[word] += 1
    return tuple(counts)


def _complete_read(relation: frozenset[Word], mark: int, dock: int) -> int:
    zero = (mark, dock, 0) in relation
    one = (mark, dock, 1) in relation
    if zero == one:
        raise ValueError("The offered mark and dock do not force one read")
    return int(one)


def _admit_holding(law: str, mark: int, dock: int, read: int | None = None) -> Word:
    """Admit a full word, or complete a pair only when the law forces its read."""
    relation = OPEN_RELATIONS[law]
    if read is None:
        read = _complete_read(relation, mark, dock)
    word = (mark, dock, read)
    if word not in relation:
        raise ValueError("The offered holding is outside its law")
    return word


def _admit_word(law: str, mark: int, dock: int) -> Word:
    """Write the offered pair and retain only its unique lawful completion."""
    word = _admit_holding(law, mark, dock)
    if (mark, dock) not in _MARK_DOCK_PAIRS[law]:
        raise ValueError("The offered mark and dock are outside the prepared alternatives")
    return word


def _read_register(law: str, words: Register) -> int:
    value = 0
    for position, word in enumerate(words):
        admitted = _admit_word(law, word[0], word[1])
        if word != admitted:
            raise ValueError("The held read distinction disagrees with its lawful completion")
        value += admitted[2] << position
    return value


def _write_register(law: str, words: Register, value: int) -> Register:
    if value < 0 or value.bit_length() > len(words):
        raise ValueError("Count exceeds register capacity")
    next_words = []
    for position, word in enumerate(words):
        offered = _MARK_DOCK_PAIRS[law][(value >> position) & 1]
        next_words.append(word if word[:2] == offered else _admit_word(law, *offered))
    return tuple(next_words)


def _read_action(histogram: tuple[int, ...], counts: tuple[int, ...]) -> dict:
    total = sum(counts)
    row_count, remainder = divmod(total, WINDOW_COUNT)
    if remainder:
        raise ValueError("Memory total is inconsistent with a whole presentation count")
    differences = None
    numerator = None
    denominator = None
    if row_count:
        differences = [row_count * seen - stored
                       for seen, stored in zip(histogram, counts, strict=True)]
        numerator = sum(difference ** 2 for difference in differences)
        denominator = row_count ** 2
    return {
        "total": total,
        "row_count": row_count,
        "distance_numerator": numerator,
        "distance_denominator": denominator,
        "per_word_differences": differences,
    }


def _closest_action(actions: list[dict]) -> int:
    left, right = actions
    if left["row_count"] == 0:
        return int(right["row_count"] > 0)
    if right["row_count"] == 0:
        return 0
    return int(right["distance_numerator"] * left["distance_denominator"]
               < left["distance_numerator"] * right["distance_denominator"])


def _check_export(memory: dict) -> None:
    if (type(memory) is not dict or set(memory) != {"schema", "law", "training_limit", "words"}
            or memory["schema"] != MEMORY_SCHEMA):
        raise ValueError("Invalid knot memory schema")


class KnotLearner:
    """Only the held words change between presentations."""

    __slots__ = ("_law", "_training_limit", "_width", "_words")

    def __init__(self, law: str, *, training_limit: int = 64):
        if type(law) is not str or law not in OPEN_RELATIONS:
            raise ValueError("Expected parity or nae law")
        if type(training_limit) is not int or training_limit < 1:
            raise ValueError("Expected a positive training limit")
        self._law = law
        self._training_limit = training_limit
        self._width = (training_limit * WINDOW_COUNT).bit_length()
        self._words = self._blank_words()

    def _blank_words(self) -> tuple[Bank, Bank]:
        blank = _admit_word(self._law, *_MARK_DOCK_PAIRS[self._law][0])
        bank = tuple((blank,) * self._width for _ in range(PATTERN_COUNT))
        # A distinction's identity is its action, word, bit position and role.
        return bank, bank

    def _read_counts(self, words: tuple[Bank, Bank]) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(_read_register(self._law, register) for register in bank) for bank in words)

    def _explain_counts(self, histogram: tuple[int, ...], counts: tuple[tuple[int, ...], ...]) -> dict:
        actions = [_read_action(histogram, bank) for bank in counts]
        return {"counts": list(histogram), "actions": actions, "guess": _closest_action(actions)}

    def explain(self, pixels) -> dict:
        """Read exact squared differences to the two mean histograms."""
        return self._explain_counts(pattern_counts(pixels), self._read_counts(self._words))

    def predict(self, pixels) -> int:
        return self.explain(pixels)["guess"]

    def learn(self, pixels, guessed: int, correct: bool) -> None:
        if (type(guessed) not in (int, bool) or guessed not in (0, 1)
                or type(correct) not in (int, bool) or correct not in (0, 1)):
            raise ValueError("Guess and correctness must be bits")
        histogram = pattern_counts(pixels)
        counts = self._read_counts(self._words)
        reading = self._explain_counts(histogram, counts)
        if guessed != reading["guess"]:
            raise ValueError("Feedback must refer to the learner's current guess")
        if sum(action["row_count"] for action in reading["actions"]) >= self._training_limit:
            raise ValueError("Training limit reached")
        rewarded = int(guessed) if correct else 1 - guessed
        updated = tuple(_write_register(self._law, register, count + increment)
                        for register, count, increment in zip(self._words[rewarded], counts[rewarded],
                                                              histogram, strict=True))
        self._words = (updated, self._words[1]) if rewarded == 0 else (self._words[0], updated)

    def export_memory(self) -> dict:
        """Export physical words in action, pattern and least-significant-bit order."""
        return {
            "schema": MEMORY_SCHEMA,
            "law": self._law,
            "training_limit": self._training_limit,
            "words": [["".join(str(bit) for word in register for bit in word) for register in bank]
                      for bank in self._words],
        }

    @classmethod
    def from_memory(cls, memory: dict) -> KnotLearner:
        _check_export(memory)
        learner = cls(memory["law"], training_limit=memory["training_limit"])
        learner.restore_memory(memory)
        return learner

    def restore_memory(self, memory: dict) -> None:
        """Admit a complete same-law donor through the mark and dock of each word."""
        _check_export(memory)
        if (memory["law"] != self._law or type(memory["training_limit"]) is not int
                or memory["training_limit"] != self._training_limit):
            raise ValueError("Memory law and training limit must match the recipient")
        banks = memory["words"]
        if (type(banks) is not list or len(banks) != 2
                or any(type(bank) is not list or len(bank) != PATTERN_COUNT for bank in banks)):
            raise ValueError("Expected 16 words for each of two actions")
        prepared = tuple(tuple(self._load_register(raw) for raw in bank) for bank in banks)
        counts = self._read_counts(prepared)
        totals = [sum(bank) for bank in counts]
        if any(total % WINDOW_COUNT for total in totals) or sum(totals) > self._training_limit * WINDOW_COUNT:
            raise ValueError("Memory totals are inconsistent with the bounded presentation count")
        for bank, total in zip(counts, totals, strict=True):
            marked = [sum(count for pattern, count in enumerate(bank) if pattern & position)
                      for position in (8, 4, 2, 1)]
            if len(set(marked)) != 1 or marked[0] > (total // WINDOW_COUNT) * SIDE ** 2:
                raise ValueError("Memory counts are inconsistent with padded bitmap marginals")
        self._words = prepared

    def _load_register(self, raw: str) -> Register:
        if type(raw) is not str or len(raw) != 3 * self._width or set(raw) - {"0", "1"}:
            raise ValueError("Malformed physical count word")
        words = []
        for position in range(0, len(raw), 3):
            mark, dock, read = (int(bit) for bit in raw[position:position + 3])
            admitted = _admit_word(self._law, mark, dock)
            if admitted[2] != read:
                raise ValueError("The donor's read distinction disagrees with its lawful completion")
            words.append(admitted)
        return tuple(words)

    def prepare_holding(self, action: int, pattern: int, position: int, word: Word) -> None:
        """Diagnostic preparation of one addressed holding under its open law."""
        address = (action, pattern, position)
        bounds = (2, PATTERN_COUNT, self._width)
        if any(type(index) is not int or not 0 <= index < bound
               for index, bound in zip(address, bounds, strict=True)):
            raise ValueError("Invalid holding address")
        if len(word) != 3 or any(type(bit) is not int or bit not in (0, 1) for bit in word):
            raise ValueError("Expected a complete three-bit holding")
        admitted = _admit_holding(self._law, *word)
        banks = list(self._words)
        bank = list(banks[action])
        register = list(bank[pattern])
        register[position] = admitted
        bank[pattern] = tuple(register)
        banks[action] = tuple(bank)
        self._words = tuple(banks)

    def clear_memory(self) -> dict:
        """Replace the held words with the lawful neutral preparation."""
        outgoing = self.export_memory()
        self._words = self._blank_words()
        return outgoing
