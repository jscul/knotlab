"""Search a complete, finite family of carried readings on one actual birth.

Use the first ordinary round of the three-knot ring with one loose
distinction per knot. Search partitions of the seven resulting distinctions
into three carriers of sizes two, two and three. Each reading uses all of
its places and is unchanged by simultaneous complementation. Complementing
an output only renames its two values, so keep one choice in each such pair.
"""

import argparse
import json
import time
from itertools import combinations, product
from pathlib import Path

from growth_rule import advance


def project(state, support):
    return sum(((state >> variable) & 1) << place for place, variable in enumerate(support))


def partitions(count):
    names = tuple(range(count))
    for three in combinations(names, 3):
        others = sorted(set(names) - set(three))
        for mate in others[1:]:
            first = (others[0], mate)
            second = tuple(x for x in others if x not in first)
            yield (first, second, three)


def tables(size):
    """For each complementary pair use the smaller member as its name."""
    values = 1 << size
    last = values - 1
    for bits in range(1, 1 << (values // 2), 2):
        truth = tuple((bits >> min(state, state ^ last)) & 1 for state in range(values))
        if all(any(truth[s] != truth[s ^ (1 << k)] for s in range(values)) for k in range(size)):
            yield truth


def state_mask(test, size):
    return sum(1 << state for state in range(size) if test(state))


def signatures(yes, universe):
    return [
        (yes[0] if a else universe ^ yes[0])
        & (yes[1] if b else universe ^ yes[1])
        & (yes[2] if c else universe ^ yes[2])
        for a, b, c in product(range(2), repeat=3)
    ]


def cell_count(mask):
    return mask.bit_count()


def joint_knot(patterns):
    if len(patterns) in (0, 8):
        return False
    return all(len({word[:i] + word[i + 1:] for word in patterns}) == 4 for i in range(3))


def run(limit):
    started = time.monotonic()
    source = [(0, 1, 3), (1, 2, 4), (2, 0, 5)]
    grown = advance(source)
    assert grown.status == "funded" and len(grown.births) == 1
    supports = grown.supports
    size = 1 << (max(x for knot in supports for x in knot) + 1)
    assert size == 128
    everything = (1 << size) - 1
    masks = [state_mask(lambda s: 0 < project(s, k) < (1 << len(k)) - 1, size) for k in supports]
    active = everything
    for mask in masks:
        active &= mask
    deletion = [everything for _ in supports]
    for i in range(len(supports)):
        for j, mask in enumerate(masks):
            if i != j:
                deletion[i] &= mask
    fibres = [[state_mask(lambda s: project(s, k) == local, size) & active
               for local in range(1 << len(k))] for k in supports]
    words = tuple(product(range(2), repeat=3))
    counts = dict(partitions=0, readings=0, knots=0, each_law_essential=0,
                  full_after_each_deletion=0, individually_unread=0, full_after_some_fix_of_each_knot=0)
    best = None
    best_score = None
    for carriers in partitions(7):
        if limit is not None and counts["partitions"] >= limit:
            break
        counts["partitions"] += 1
        for readings in product(*(tables(len(c)) for c in carriers)):
            counts["readings"] += 1
            yes = [state_mask(lambda s: reading[project(s, carrier)], size)
                   for carrier, reading in zip(carriers, readings)]
            parts = signatures(yes, everything)
            observed = tuple(w for w, mask in zip(words, parts) if mask & active)
            if not joint_knot(observed):
                continue
            counts["knots"] += 1
            after_deletion = [sum(bool(d & mask) for mask in parts) for d in deletion]
            if not all(n > len(observed) for n in after_deletion):
                continue
            counts["each_law_essential"] += 1
            if after_deletion != [8] * len(deletion):
                continue
            counts["full_after_each_deletion"] += 1
            unreadable = all(any(f & y and f & (everything ^ y) for f in family)
                             for family in fibres for y in yes)
            if not unreadable:
                continue
            counts["individually_unread"] += 1
            full = [[i for i, f in enumerate(family)
                     if sum(bool(f & mask) for mask in parts) == len(observed)] for family in fibres]
            if all(full):
                counts["full_after_some_fix_of_each_knot"] += 1
            score = (sum(bool(f) for f in full), min(map(len, full)), sum(map(len, full)), len(observed))
            if best_score is None or score > best_score:
                best_score = score
                best = {
                    "carriers": carriers, "readings_in_little_endian_order": readings, "words": observed,
                    "states_per_word": [cell_count(active & m) for m in parts],
                    "words_after_removing_each_law": after_deletion,
                    "local_states_retaining_all_words_in_little_endian_order": full,
                }
    return {"source": source, "stage": supports, "stage_states": cell_count(active), "counts": counts,
            "best": best, "seconds": time.monotonic() - started}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-partitions", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.limit_partitions)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
