"""Exact integer classification by learned bipartitions of raw patch categories."""

from copy import deepcopy
from math import gcd
from operator import index


BIN_COUNT = 16
PATCH_COUNT = 81


def histogram(pixels):
    """Count all padded two-by-two words in row-major bit order."""
    pixels = tuple(map(index, pixels))
    if len(pixels) != 64 or any(pixel not in (0, 1) for pixel in pixels):
        raise ValueError("expected 64 binary pixels")

    border = (0,) * 10
    padded = [border]
    padded.extend((0, *pixels[offset:offset + 8], 0) for offset in range(0, 64, 8))
    padded.append(border)

    counts = [0] * BIN_COUNT
    for top, bottom in zip(padded, padded[1:]):
        for top_left, top_right, bottom_left, bottom_right in zip(
            top, top[1:], bottom, bottom[1:]
        ):
            word = (top_left << 3) | (top_right << 2) | (bottom_left << 1) | bottom_right
            counts[word] += 1
    return counts


def _checked_histogram(counts):
    counts = tuple(map(index, counts))
    if len(counts) != BIN_COUNT or min(counts) < 0 or sum(counts) != PATCH_COUNT:
        raise ValueError("expected 16 nonnegative bin counts summing to 81")
    return counts


def _bit(value):
    value = index(value)
    if value not in (0, 1):
        raise ValueError("expected a binary action or correctness bit")
    return value


def _subset_moments(columns):
    """Tabulate sums and sums of squares of the subset counts in mask order."""
    totals = [0]
    squares = [0]
    for position, column in enumerate(columns):
        total = sum(column)
        square = sum(value * value for value in column)

        # Adding this bin to a subset adds its own square and its cross terms.
        cross_terms = [0]
        for earlier_column in columns[:position]:
            cross_term = 2 * sum(a * b for a, b in zip(column, earlier_column))
            cross_terms += [prior_term + cross_term for prior_term in cross_terms]

        totals += [prior_total + total for prior_total in totals]
        squares += [
            prior_square + square + cross_term
            for prior_square, cross_term in zip(squares, cross_terms)
        ]
    return totals, squares


def _fit_classes(rows_by_class):
    columns = [list(zip(*rows)) for rows in rows_by_class]
    n0, n1 = map(len, rows_by_class)
    memory = {
        "class_totals": [n0, n1],
        "class_bin_totals": [
            [sum(column) for column in class_columns] if class_columns else [0] * BIN_COUNT
            for class_columns in columns
        ],
        "masks": [],
        "score": None,
        "smaller_side_size": None,
    }
    if not n0 or not n1:
        return memory

    # Each partition has a unique representative omitting the final bin.
    totals0, squares0 = _subset_moments(columns[0][:-1])
    totals1, squares1 = _subset_moments(columns[1][:-1])
    best_numerator, best_denominator = 0, 1
    best_size = BIN_COUNT
    best_masks = []
    for mask, (total0, square0, total1, square1) in enumerate(
        zip(totals0, squares0, totals1, squares1)
    ):
        separation = n0 * total1 - n1 * total0
        if separation == 0:
            continue

        # The shared denominator n0**2 * n1**2 cancels from the ratio.
        numerator = separation * separation
        denominator = (
            n1 * n1 * (n0 * square0 - total0 * total0)
            + n0 * n0 * (n1 * square1 - total1 * total1)
        )
        comparison = numerator * best_denominator - best_numerator * denominator
        cardinality = mask.bit_count()
        size = min(cardinality, BIN_COUNT - cardinality)
        if comparison > 0 or (comparison == 0 and size < best_size):
            best_numerator, best_denominator = numerator, denominator
            best_size = size
            best_masks = [mask]
        elif comparison == 0 and size == best_size:
            best_masks.append(mask)

    if best_masks:
        divisor = gcd(best_numerator, best_denominator)
        memory["masks"] = best_masks
        memory["score"] = [best_numerator // divisor, best_denominator // divisor]
        memory["smaller_side_size"] = best_size
    return memory


def fit_histograms(histograms, actions):
    """Fit on 16-bin histograms with one earned binary action per histogram.

    The returned memory is JSON-compatible. Masks omit bin 15, and the
    score is a reduced numerator and denominator with [1, 0] for infinity.
    """
    rows_by_class = [[], []]
    for counts, action in zip(histograms, actions, strict=True):
        rows_by_class[_bit(action)].append(_checked_histogram(counts))
    return _fit_classes(rows_by_class)


def explain_histogram(counts, memory):
    """Return each fitted partition's scalar and vote on one histogram."""
    counts = _checked_histogram(counts)
    n0, n1 = memory["class_totals"]
    bins0, bins1 = memory["class_bin_totals"]
    votes = [0, 0]
    abstentions = 0
    partitions = []
    for mask in memory["masks"]:
        bins = [position for position in range(BIN_COUNT - 1) if mask & (1 << position)]
        value = sum(counts[position] for position in bins)
        total0 = sum(bins0[position] for position in bins)
        total1 = sum(bins1[position] for position in bins)
        # The sign compares the squared distances from the two class means.
        signed_margin = (2 * n0 * n1 * value - n1 * total0 - n0 * total1) * (
            n0 * total1 - n1 * total0
        )
        vote = int(signed_margin > 0) if signed_margin else None
        if vote is None:
            abstentions += 1
        else:
            votes[vote] += 1
        partitions.append({"mask": mask, "count": value, "vote": vote})

    return {
        "action": int(votes[1] > votes[0]),
        "votes": votes,
        "abstentions": abstentions,
        "partitions": partitions,
    }


class NumericGroups:
    def __init__(self, training_limit=64):
        self.training_limit = index(training_limit)
        if self.training_limit < 0:
            raise ValueError("training limit must be nonnegative")
        self._rows = [[], []]
        self._memory = None

    def predict(self, pixels):
        return self.explain(pixels)["action"]

    def learn(self, pixels, guessed, correct):
        if self._memory is not None or sum(map(len, self._rows)) >= self.training_limit:
            raise RuntimeError("training is already complete")
        guessed = _bit(guessed)
        action = guessed if _bit(correct) else 1 - guessed
        self._rows[action].append(histogram(pixels))

    def finalize(self):
        if self._memory is not None:
            return
        if sum(map(len, self._rows)) != self.training_limit:
            raise RuntimeError("training is incomplete")
        self._memory = _fit_classes(self._rows)
        self._rows = None

    def export_memory(self):
        if self._memory is None:
            raise RuntimeError("fit has not been finalized")
        return deepcopy(self._memory)

    @classmethod
    def from_memory(cls, data):
        model = cls(training_limit=sum(data["class_totals"]))
        model._memory = deepcopy(data)
        model._rows = None
        return model

    def explain(self, pixels):
        if self._memory is not None:
            return explain_histogram(histogram(pixels), self._memory)
        n0, n1 = map(len, self._rows)
        return {"action": int(n1 > n0), "votes": [0, 0], "abstentions": 0, "partitions": []}

    def selection(self):
        return self.export_memory()
