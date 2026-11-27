"""Test the earlier minimal-constraint reading and deletion/insertion controls."""
import argparse
import json
import time
from collections import Counter
from functools import cache

from census_tools import HERE, roster


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


@cache
def variables(n):
    universe = (1 << (1 << n)) - 1
    ones = tuple(universe // ((1 << (1 << j)) + 1) << (1 << j) for j in range(n))
    return universe, ones


@cache
def monochrome(n, row):
    universe, bits = variables(n)
    all_zero = all_one = universe
    for i in members(row):
        all_one &= bits[i]
        all_zero &= universe ^ bits[i]
    return all_zero | all_one


def read(rows):
    n = max(rows).bit_length()
    universe, bits = variables(n)
    excluded = [monochrome(n, r) for r in rows]
    states = universe
    for violation in excluded:
        states &= ~violation
    # Positions s index states; after taking all subsets, positions t index
    # supports that can all be one. Complementing a state preserves the law.
    possible = states
    for j, b in enumerate(bits):
        possible |= (possible & b) >> (1 << j)
    entailed = universe ^ possible
    minimal = entailed
    for j, b in enumerate(bits):
        minimal &= ~((entailed & ~b) << (1 << j))
    loose = 0
    actual = 0
    for r in rows:
        loose ^= r
        actual |= 1 << r
    redundant = 0
    for i, orig in enumerate(excluded):
        extra = orig
        for j, other in enumerate(excluded):
            if j != i:
                extra &= ~other
        redundant += extra == 0
    # An insertion fits remaining holding capacity iff all its places are loose.
    additions = [m for m in members(minimal) if (m & ~loose) == 0 and m.bit_count() >= 3]
    checked = None
    if additions:
        t = min(additions)
        assert t not in rows and not (states & monochrome(n, t))
        checked = dict(added=list(members(t)), knots=[list(members(r)) for r in rows],
                       marked_before=list(members(loose)), marked_after=list(members(loose ^ t)),
                       states=states.bit_count())
    return dict(starts=1, saturated=int(minimal == actual),
                irredundant=int(not redundant),
                all_original_supports_minimal=int((minimal & actual) == actual),
                has_implied_pair=int(any(m.bit_count() == 2 for m in members(minimal))),
                admits_an_unmarked_single_insertion=int(bool(additions))), checked


def run(indices):
    starts = roster()
    results = {}
    examples = {}
    for i in indices:
        row, witness = read(starts[i])
        for bucket in (['all', 'frozen prefix'] if i < 1194 else ['all', 'after prefix']):
            results.setdefault(bucket, Counter()).update(row)
            if witness and bucket not in examples:
                examples[bucket] = dict(census_index=i, **witness)
    return dict(reading="All inclusion-minimal implied not-all-equal supports; "
                "one extra distinct knot of at least three places using loose distinctions only.",
                counts=results, first_insertion=examples)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    begin = time.monotonic()
    result = run(range(0, 7075, 101) if args.pilot else range(7075))
    result["elapsed_seconds"] = round(time.monotonic() - begin, 3)
    if args.pilot:
        print(json.dumps(result["counts"]), result["elapsed_seconds"])
    else:
        (HERE / "unmarked_counts.json").write_text(json.dumps(result, indent=2) + "\n")
