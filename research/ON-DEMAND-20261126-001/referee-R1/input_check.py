"""Check the original place count and holder information needed by a cut roster."""

import argparse
import json
from pathlib import Path
import resource
import time

from growth import Roster, grow
from weighted_example import build

HERE = Path(__file__).resolve().parent


def views(roster, reader):
    first, second = grow(roster, 1, "nae").views(reader, 1)[0]
    return [[list(item) for item in sorted(count.items())] for count in (first, second)]


def run(pilot):
    variants = []
    for n_shared in (1, 2):
        pairs = [(0, 1)] * n_shared
        roster = Roster.from_graph([2 + n_shared] * 2, pairs)
        variants.append({"shared": n_shared, "loose": roster.loose, "places": roster.places,
                         "maximal_blocks": [sorted(b) for b in roster.blocks],
                         "reader_piece": sorted(roster.within(0, 2)), "views": views(roster, 0)})
    assert variants[0]["views"][0] == variants[1]["views"][0]
    assert variants[0]["views"][1] != variants[1]["views"][1]

    pairs, names, neighbours, places, loose = build()
    region = set("RVABC")
    cut = lambda holders: {h: sorted(neighbours[h] & region) for h in holders
                           if len(neighbours[h] & region) >= 2}
    correct = cut(names)
    discarded = cut(region)
    assert set(correct) == {"U", "W"} and not discarded
    numbering = {v: i for i, v in enumerate(names)}
    labels = {v: len(names) - 1 - i for v, i in numbering.items()}
    all_orders = [numbering] if pilot else [numbering, labels]
    results = []
    for order in all_orders:
        roster = Roster.from_graph({order[v]: places[v] for v in names}, [(order[a], order[b]) for a, b in pairs])
        reader = order["R"]
        full = grow(roster, 1, "nae")
        partial = grow(roster.restrict(roster.within(reader, 2)), 1, "nae")
        assert full.end == "rounds" and partial.end == "stall"
        results.append({"whole": sum(full.views(reader)[0][0].values()), "restricted": len(partial.rows)})
    return {"two_connected_starts": variants, "25_knot_cut": sorted(region),
            "cut_blocks_if_all_holders_are_read": correct, "cut_blocks_if_only_kept_holders_are_read": discarded,
            "example_under_original_and_reversed_numbering": results}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (600 << 20, 600 << 20))
    start = time.monotonic()
    data = run(args.pilot)
    data["elapsed_seconds"] = round(time.monotonic() - start, 4)
    output = HERE / ("input_check_pilot.json" if args.pilot else "input_check.json")
    output.write_text(json.dumps(data, indent=2) + "\n")
