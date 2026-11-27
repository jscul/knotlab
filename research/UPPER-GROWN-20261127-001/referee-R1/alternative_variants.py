"""Interchange which outer member receives either incoming distinction in five carriers."""

import argparse
from collections import Counter
import json
from itertools import product

import alternative_growth as base


def setup(switches):
    # Group 0 supplies its old pair to B1 and its two fresh places to B0.
    # In every other group, two outgoing laws share the middle member.
    # Interchanging the two incoming occurrences preserves these facts.
    switches = (0, *switches)
    laws = []
    first = None
    for g, i, j in product(range(3), range(2), range(2)):
        double = 2*g + i
        single = 2*((g + 1) % 3) + j
        left = (3*double + j, 3*double + 1 + j)
        right = 3*single + 2*(i ^ switches[single])
        if (g, i, j) == (0, 0, 0):
            first = right
            continue
        laws.append(tuple(0 if x == 1 else x for x in (*left, right)))
    result = base.advance(tuple(laws))
    birth, = result.births
    assert result.status == "funded" and birth.inputs == (first,) and birth.fresh == (18, 19)
    return tuple(laws), result.supports, list(birth.parents)


def examine(switches):
    start, laws, parents = setup(switches)
    _, universe, _, obey, allowed, lower, upper = base.source_data(laws)
    joint = sorted(base.cells(allowed, lower))
    upper_image = sorted(base.cells(allowed, upper))
    with_birth_omitted = base.reduce(base.and_, obey[:-1], universe)
    missing = universe & ~upper[0] & ~upper[1] & ~upper[2]
    return {"switches": switches, "source_states": allowed.bit_count(), "joint_words": len(joint),
            "upper_words": upper_image, "restored_000_states_after_birth_deletion": (with_birth_omitted & missing).bit_count(),
            "parent": parents, "start": start, "birth": laws[-1]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=32)
    options = parser.parse_args()
    data = [examine(orient) for orient in list(product((0, 1), repeat=5))[:options.limit]]
    print(json.dumps({"variants": len(data), "joint_word_counts": dict(Counter(r["joint_words"] for r in data)),
                      "rows": data}, indent=2))
