"""Give a connected-cut upper bound and elementary route lower certificates."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path

import networkx as nx

from certify import OUTPUT, Wired, frozen_source, orientations


def contracted(graph, pins):
    sink = graph.outside
    source = min(j for j, color in pins.items() if color)
    representative = {j: source if pins.get(j) == 1 else sink if pins.get(j) == 0 else j
                      for j in graph.all_knots}
    capacities = Counter()
    for a, b in graph.ends.values():
        u, v = representative[a], representative[b]
        if u != v:
            capacities[tuple(sorted((u, v)))] += 1
    return capacities, representative, source, sink


def route_certificate(residual, source, sink, value):
    flow = nx.DiGraph()
    flow.add_nodes_from(residual)
    for a, b, row in residual.edges(data=True):
        if row["flow"] > 0:
            flow.add_edge(a, b, remaining=row["flow"])
    routes = []
    while value > 0:
        path = nx.shortest_path(flow, source, sink)
        width = min(value, *(flow[a][b]["remaining"] for a, b in pairwise(path)))
        routes.append((width, path))
        value -= width
        for a, b in pairwise(path):
            flow[a][b]["remaining"] -= width
            if flow[a][b]["remaining"] == 0:
                flow.remove_edge(a, b)
    return routes


def verify_lower(capacities, source, sink, routes):
    used = defaultdict(int)
    for width, route in routes:
        assert isinstance(width, int) and width > 0
        assert route[0] == source and route[-1] == sink and len(set(route)) == len(route)
        for u, v in pairwise(route):
            bundle = tuple(sorted((u, v)))
            used[bundle] += width
            assert used[bundle] <= capacities[bundle]
    return sum(width for width, _ in routes)


def exact_pair(graph, first, second):
    alternatives = []
    for pins in orientations(graph, first, second):
        capacities, representative, source, sink = contracted(graph, pins)
        g = nx.DiGraph()
        g.add_nodes_from(sorted(set(representative.values())))
        for (u, v), width in sorted(capacities.items()):
            g.add_edge(u, v, capacity=width)
            g.add_edge(v, u, capacity=width)
        residual = nx.algorithms.flow.preflow_push(g, source, sink)
        value = residual.graph["flow_value"]
        routes = route_certificate(residual, source, sink, value)
        # The route proof is checked against the physical multiplicities
        # without inspecting the optimizer's capacities or objective.
        assert verify_lower(capacities, source, sink, routes) == value
        optimum, (side, _) = nx.minimum_cut(g, source, sink)
        assert optimum == value
        inside = {j for j, rep in representative.items() if rep in side}
        connected = graph.connected(inside) and graph.connected(graph.all_knots - inside)
        row = {"pins": sorted(pins.items()), "lower_bound_cost": value, "route_weights_and_knots": routes}
        if connected:
            witness = graph.witness(sum(1 << j for j in inside))
            assert witness["cost"] == value and {first, second} <= set(witness["crossing_distinctions"])
            row["upper_witness"] = witness
        alternatives.append(row)
    lower = min(row["lower_bound_cost"] for row in alternatives)
    upper = min((row["upper_witness"]["cost"] for row in alternatives if "upper_witness" in row),
                default=None)
    assert lower == upper
    return {"marks": [first, second], "bond_distance": lower - 1, "cut_cost": lower,
            "orientations": alternatives}


def run(through):
    old, marks, ring, digest, step = frozen_source()
    arms = {"quiet": (old, ()), "loaded": (old, ring)}
    rows = {}
    for age in range(through + 1):
        row = {}
        for name, (stars, occupied) in tuple(arms.items()):
            graph = Wired(stars)
            exact = exact_pair(graph, marks[3], marks[4])
            exact.update(knots=graph.outside, distinctions=len(graph.ends),
                         literal_stars_sha256=sha256(json.dumps(stars, separators=(",", ":")).encode()).hexdigest())
            row[name] = exact
            if age < through:
                frame = step(stars, occupied, ("P", "V"), caps={"junctions": 6000, "distinctions": 32000})
                assert frame["status"] == "extend"
                arms[name] = (frame["stars"], frame["occupied"])
        assert row["quiet"]["bond_distance"] == 7 and row["loaded"]["bond_distance"] == (7 if age < 4 else 4)
        rows[age] = row
        print(age, row["quiet"]["bond_distance"], row["loaded"]["bond_distance"], flush=True)
    return {"source": "J1", "path_positions": [3, 4], "parity_source_sha256": digest, "ages": rows,
            "units": "cost counts physical distinctions; distance equals cost minus one"}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT.with_name("certify_flow.json"))
    parser.add_argument("--through", type=int, choices=range(7), default=6)
    args = parser.parse_args()
    result = run(args.through)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    tmp.replace(args.output)


if __name__ == "__main__":
    main()
