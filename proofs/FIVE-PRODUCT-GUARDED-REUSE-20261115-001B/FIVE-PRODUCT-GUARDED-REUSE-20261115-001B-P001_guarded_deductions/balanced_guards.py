"""Test literal reuse of one terminal guard across two whole alternating-input cases."""
from itertools import combinations
import json


def span(points):
    if not points:
        return set()
    anchor = next(iter(points))
    offsets = {0}
    for point in points:
        offset = point ^ anchor
        if offset not in offsets:
            offsets |= {old ^ offset for old in offsets}
    return {anchor ^ d for d in offsets}


def close(cell, positive, negative):
    while cell:
        new = span(positive & cell) & span(negative & cell)
        if new == cell:
            break
        cell = new
    return cell


def bits(value):
    return value.bit_count() % 2


def replay():
    # Representatives use the first four mask bits; adding the total clears the fifth.
    planes = {tuple(sorted((first, second, first ^ second)))
              for first, second in combinations(range(1, 16), 2)}
    cases = [{row for row in range(512)
              if ((row & 1) | ((row >> 1) & 2) | ((row >> 2) & 4)) == a}
             for a in range(8)]
    both = [span(u | v) for u, v in combinations(cases, 2)]
    closed, live = 0, 0
    retained = set()
    for first, second, _ in sorted(planes):
        pos, neg = set(), set()
        for x in range(64):
            prods = x & (x >> 1) & 31
            q = bits(prods)
            pos.add(x | (q << 6) | (bits(prods & first) << 7) | (bits(prods & second) << 8))
            neg.update(x | ((1 ^ q) << 6) | (z << 7) for z in range(4))
        for case in cases:
            assert not close(case, pos, neg)
            closed += 1
        for case in both:
            fixed = close(case, pos, neg)
            assert fixed, (first, second)
            retained.add(len(fixed))
            live += 1
    assert len(planes) == 35 and closed == 280 and live == 980
    return {"single_case_closures": closed, "two_case_guards_still_live": live,
            "sizes_of_saturated_live_cells": sorted(retained)}


if __name__ == "__main__":
    print(json.dumps(replay(),sort_keys=True))
