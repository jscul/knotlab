"""Check the marked-incidence shore construction on every pattern through arity five."""

import argparse
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "constructive_arity.json"


def component(seed, adjacency):
    seen = pending = 1 << seed
    while pending:
        point = pending & -pending
        pending ^= point
        new = adjacency[point.bit_length() - 1] & ~seen
        seen |= new
        pending |= new
    return seen


def certify(order):
    # 0 is the merged hub. At most order middles carry marks. Use a spare to
    # connect positive anchors and a second spare to witness the negative shore.
    outer = (1 << order) - 1
    middles = ((1 << (order + 2)) - 1) << order
    all_points = outer | middles
    marks = [(u, v) for u in range(order) for v in range(order, 2 * order)]
    counts = []
    for size in range(1, order + 1):
        checked = singleton = max_outer = max_middles = 0
        for picked in itertools.combinations(marks, size):
            adjacency = [0] * (2 * order)
            active_middles = 0
            for u, v in picked:
                adjacency[u] |= 1 << v
                adjacency[v] |= 1 << u
                active_middles |= 1 << v
            hub = component(0, adjacency)
            candidates = outer & ~hub
            if not candidates:
                assert active_middles.bit_count() == 1
                positive = active_middles
                singleton += 1
            else:
                anchor = (candidates & -candidates).bit_length() - 1
                chosen = component(anchor, adjacency)
                positive = (chosen & outer) | (active_middles & ~chosen)
                if not positive & middles and positive.bit_count() > 1:
                    positive |= 1 << (2 * order)
            for side in (positive, all_points ^ positive):
                # Connectedness in a complete bipartite graph, including singletons.
                assert side.bit_count() == 1 or (side & outer and side & middles)
            assert all(((positive >> u) ^ (positive >> v)) & 1 for u, v in picked)
            assert not (positive & 1)
            max_outer = max(max_outer, (positive & outer).bit_count())
            max_middles = max(max_middles, (positive & middles).bit_count())
            checked += 1
        assert max_outer <= order - 1 and max_middles <= order + 1
        counts.append({"arity": size, "patterns": checked, "forced_single_middle": singleton,
                       "max_positive_anchors": max_outer, "max_positive_middles": max_middles})
    anchors = order - 1
    shields = 4 * (order + 2)
    test = shields * order
    price = 8 * shields
    middle_count = 2 * shields + 4
    bound = (4 * test + 2 * shields + (anchors - 1) * middle_count
             + 4 * (2 * test + anchors - 1) + (order + 1) * (2 * price + anchors))
    assert shields * price - bound == 7 * order ** 2 + 208 * order + 417
    assert 2 * test + shields * (anchors + 1) == 3 * test < 4 * test
    return {"r": order, "I": anchors, "s": shields, "L": test, "M": price,
            "present_upper": bound, "separating_lower": shields * price,
            "next_original_pair_upper": 3 * test, "next_image_pair_lower": 4 * test,
            "reached_junctions": anchors + 6 + 4 * shields + 4 * shields * price,
            "patterns": counts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = {
        "scope": "All subsets through r marks in the folded incidence graph on r outer vertices and r eligible middles for 2 <= r <= 5. Every pattern of at most r marks uses at most r middles. The size-independent argument is in constructive-proof.md.",
        "cases": [certify(r) for r in range(2, 6)],
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.check:
        if OUT.read_text() != encoded:
            raise SystemExit("saved component replay differs")
    else:
        OUT.write_text(encoded)
    print("All marked-incidence shore patterns through arity five passed.")
