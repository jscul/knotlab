"""Replay finite points of the fixed-route split-holder construction."""

import argparse
import json
from pathlib import Path
import sys

from lower import EXTEND_ROUND, ROOT
from lower_probe import core, explicit_scheme, grow_graft


def measures(order, routes, compact=False):
    anchors = order - 1 if compact else order + 1
    weak_bound = anchors * (routes + 2) + 2 if compact else (anchors - 2) * order + routes + 3
    weight = weak_bound // (routes - 2 * (order - 1)) + 1
    width = 2 * (anchors + 1) + routes * (2 * weight + anchors) + 5
    junctions = routes + anchors + 6
    return junctions, width, weight


def certificate(order, routes, compact=False):
    anchors = order - 1 if compact else order + 1
    junctions, width, weight = measures(order, routes, compact)
    weak_bound = anchors * (routes + 2) + 2 if compact else (anchors - 2) * order + routes + 3
    cheap_bound = 2 * (order - 1) * weight + weak_bound
    split_bound = routes * weight
    assert cheap_bound < split_bound
    assert weight == 1 or cheap_bound - 2 * (order - 1) >= routes * (weight - 1)
    sites, links, classes, type_map, unit = core(routes, anchors, dense=True)
    geometry = sites, links, type_map, unit
    weights = [(1, 1, 1, weight)[c] for c in classes]
    stages, names, phi = grow_graft(geometry, weights)
    assert (len(stages[1].stars), len(stages[1].labels)) == (junctions, width)
    exposure = explicit_scheme(geometry, names, phi, stages)
    assert len(exposure["old_mark"]) == anchors + 2
    assert exposure["image_K"] == split_bound + anchors + 1
    return {"fixed_routes": routes, "weak_anchors": anchors, "route_bundle_size": weight,
            "strict_shared_bond_bound": cheap_bound, "hub_separating_lower_bound": split_bound,
            "sizes_by_age": [(len(z.stars), len(z.labels)) for z in stages],
            "map": sorted(phi.items()), "discrepancy": exposure,
            "support_history": [[sorted(row) for row in z.stars] for z in stages]}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--through", type=int, default=8)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    results = []
    for order in range(3, args.through + 1):
        least_j = 2 * order - 1
        least_n = min(range(least_j, 8 * order), key=lambda s: measures(order, s)[1::-1])
        results.append({"preserved_order": order, "least_junctions_in_formula": certificate(order, least_j, compact=True),
                        "smallest_route_count_with_extra_anchors": certificate(order, least_j),
                        "least_width_in_panel": certificate(order, least_n),
                        "width_panel_routes": [least_j, 8 * order - 1]})
    args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
