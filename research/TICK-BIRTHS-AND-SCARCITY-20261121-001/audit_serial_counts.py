"""Independently count the funded eight-knot clock's completed birth cohorts.

Use the earlier identification of a birth with consecutive original occurrences
and a subset of their available additions. This checker counts by a generating
function, without reading a serial schedule or enumerating its individual births.

For each possible first original, count only the first four core lengths. Four
more original occurrences return to its phase and add w optional positions.
If z counts total size and u marks each option left unselected, these extensions
multiply by Q = z**4 * (u+z)**w. Then C = N + Q*C counts children, where N is
the polynomial for lengths one to four. Differentiating with respect to u at
one counts unselected options. Each such option and two extensions are funded.
Read size t+1 for parent age t. All counts refer to the built fixtures.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import comb


@dataclass(frozen=True)
class Source:
    marks: tuple[int, ...] = (0,)
    attached_at: int | None = None


SOURCES = {
    "bare": Source(),
    "same": Source(attached_at=3),
    "other": Source(attached_at=2),
    "supply": Source((0, 2, 4)),
}


def option_count(source: Source, first: int, length: int) -> int:
    roles = [(first + 2 * offset) % 8 for offset in range(length + 1)]
    spares = sum(source.marks.count(role) for role in roles[:-1])
    attached = source.attached_at
    gaps = 0 if attached is None else roles.count((attached + 1) % 8)
    return spares + gaps


def numerator(length: int, options: int, counts: list[int], unselected: list[int]):
    for selected in range(options + 1):
        size = length + selected
        if size < len(counts):
            ways = comb(options, selected)
            counts[size] += ways
            unselected[size] += (options - selected) * ways


def coefficients(source: Source, limit: int) -> tuple[list[int], list[int]]:
    """Return total births and loose distinctions at each complete size."""
    all_counts = [0] * (limit + 1)
    all_loose = [0] * (limit + 1)
    if source.attached_at is not None:
        all_counts[1], all_loose[1] = 1, 2
    for first in range(8):
        counts = [0] * (limit + 1)
        unselected = [0] * (limit + 1)
        for length in range(1, 5):
            numerator(length, option_count(source, first, length), counts, unselected)
        gained = option_count(source, first, 5) - option_count(source, first, 1)
        for size in range(1, limit + 1):
            for selected in range(gained + 1):
                previous = size - 4 - selected
                if previous < 1:
                    continue
                ways = comb(gained, selected)
                counts[size] += ways * counts[previous]
                unselected[size] += ways * (unselected[previous]
                                            + (gained - selected) * counts[previous])
            all_counts[size] += counts[size]
            all_loose[size] += 2 * counts[size] + unselected[size]
    return all_counts, all_loose


def tick_parent(source: Source, turn: int) -> tuple[int, int]:
    """Count all available slots and extensions containing the attached donor."""
    length = 4 * turn + 1
    pure = Source(source.marks)
    choices = option_count(source, 0, length)
    # Either actual tick parent has retained one marked option, at opposite ends.
    return 2 + choices - 1, choices - option_count(pure, 0, length)


def report(turns: int):
    print('source  turn  age  cohort_births  births_since_previous_cut  loose_at_cut  '
          'consumer_in_cohort  slots_per_tick_parent  consumer_siblings_per_parent')
    for name, source in SOURCES.items():
        limit = 4 * turns + 3
        births, loose = coefficients(source, limit)
        pure_births, _ = coefficients(Source(source.marks), limit)
        previous = 1  # omit the prepared knots
        for turn in range(1, turns + 1):
            size = 4 * turn + 3
            print(name, turn, size - 1, births[size], sum(births[previous + 1:size + 1]),
                  loose[size], births[size] - pure_births[size], *tick_parent(source, turn))
            previous = size


def matched_event_budget():
    """Bound the number of turns in every order at the same individual birth."""
    size = 7  # first recorded turn, six parent steps beyond the source
    counts, _ = coefficients(SOURCES["bare"], size)
    budget = sum(counts[2:])
    print(f'At individual birth {budget}, the first completed bare turn:')
    for name, source in SOURCES.items():
        counts, _ = coefficients(source, size + 4)
        before = sum(counts[2:size])
        through = before + counts[size]
        assert sum(counts[2:size + 4]) >= budget
        if through <= budget:
            guaranteed = 'one tick'
        elif budget <= before:
            guaranteed = 'zero ticks'
        else:
            guaranteed = 'ordering can matter within this group'
        print(f'{name}: first turn lies within births {before + 1}–{through}; {guaranteed}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--turns', type=int, default=4)
    opts = parser.parse_args()
    if opts.turns < 1:
        parser.error('give a positive number of turns')
    report(opts.turns)
    matched_event_budget()

