"""Independent exact reference for the anonymous-bin rule selection."""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from subsets import subset_projections


@dataclass(frozen=True)
class Group:
    members: tuple[int, ...]
    means: tuple[Fraction, Fraction]
    score: tuple[int, int]


def supplement(members, width):
    return tuple(column for column in range(width) if column not in members)


def mask_from_partition(members):
    eligible = set(range(15))
    membership = set(members)
    columns = eligible - membership if 15 in membership else membership
    return sum(1 << index for index in columns)


def group_roster(rows, labels):
    """Represent each complement-equivalent pair once and use integer moments."""
    width = len(rows[0])
    frequencies = Counter(zip(rows, labels, strict=True))
    patterns = tuple(frequencies)
    counts = [sum(count for (_, label), count in frequencies.items() if label == action) for action in (0, 1)]
    if not all(counts):
        raise ValueError("Calibration needs observations for both actions")

    for members, totals in subset_projections(tuple(pattern for pattern, _ in patterns)):
        # A fixed representative convention may change under recoding. Its
        # complement defines the same partition, score and votes.
        if not members or members[0] == 0:
            continue
        sums = [0, 0]
        squares = [0, 0]
        for key, projected in zip(patterns, totals, strict=True):
            action = key[1]
            multiplicity = frequencies[key]
            sums[action] += multiplicity * projected
            squares[action] += multiplicity * projected * projected

        left, right = counts
        a, b = sums
        difference = a * right - b * left
        if difference == 0:
            continue
        numerator = difference * difference
        denominator = (left * squares[0] - a * a) * right * right + (right * squares[1] - b * b) * left * left
        other = supplement(members, width)
        means = Fraction(a, left), Fraction(b, right)
        if (len(other), other) < (len(members), members):
            # Each projected count plus its complement sums to the same
            # total, so complementing reflects all projected means.
            total = sum(rows[0])
            means = total - means[0], total - means[1]
            members = other
        yield Group(members, means, (numerator, denominator))


def priority(group):
    numerator, denominator = group.score
    return denominator == 0, Fraction(numerator, denominator) if denominator else 0, -len(group.members)


def selected_groups(roster):
    if not roster:
        return []
    best = max(map(priority, roster))
    return [group for group in roster if priority(group) == best]


def committee(feature, groups):
    votes = Counter()
    for group in groups:
        count = sum(feature[index] for index in group.members)
        gap = abs(count - group.means[0]) - abs(count - group.means[1])
        choice = int(gap > 0) if gap else None
        votes[choice] += 1
    return int(votes[1] > votes[0]), votes
