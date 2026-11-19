"""An exact four-name reading in the 21-index split-hub core."""

import argparse
import json
from itertools import combinations
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "constructive_four.json"


def core():
    n = 21
    graph = nx.Graph()
    middle = sorted(combinations(range(n), 2))
    hub = {}
    for i in range(n):
        for step in range(1, 11):
            hub[tuple(sorted((i, (i + step) % n)))] = "dark" if step <= 5 else "light"
    for mid in middle:
        for u in (*mid, hub[mid]):
            graph.add_edge(mid, u)
    return graph, middle, hub


def check():
    graph, mids, hub = core()
    first, second = (2, 8), (8, 9)
    assert (hub[first], hub[second], hub[(3, 8)]) == ("light", "dark", "dark")
    marks = [("light", first), (8, first), (8, second), (9, second)]
    side = {"dark", 2}
    for w in mids:
        if len(set(graph[w]) & side) >= 2:
            side.add(w)
    side.update((first, second))
    assert all((u in side) != (v in side) for u, v in marks)
    assert nx.is_connected(graph.subgraph(side)) and nx.is_connected(graph.subgraph(set(graph) - side))
    length = len(list(nx.edge_boundary(graph, side)))
    assert length == 117
    # Each qualifying bond can be oriented this way; the two positive marked
    # middle vertices would otherwise be isolated. A cut minimum is a lower bound.
    force_in = ["dark", 2, first, second]
    force_out = ["light", 8, 9]
    flowgraph = nx.DiGraph()
    for u, v in graph.edges:
        flowgraph.add_edge(u, v, capacity=1)
        flowgraph.add_edge(v, u, capacity=1)
    for v in force_in:
        flowgraph.add_edge("SOURCE", v, capacity=graph.number_of_edges() + 1)
    for v in force_out:
        flowgraph.add_edge(v, "SINK", capacity=graph.number_of_edges() + 1)
    lower, _ = nx.minimum_cut(flowgraph, "SOURCE", "SINK")
    assert lower == length
    # In the image, all neighbors of the second positive middle are forced negative.
    assert set(graph[second]) == {"dark", 8, 9}
    return {
        "core_vertices": graph.number_of_nodes(), "core_names": graph.number_of_edges(),
        "permutation": [2, 3],
        "marks": [["spoke", 2, 8], ["index", 8, 2, 8], ["index", 8, 8, 9], ["index", 9, 8, 9]],
        "projection_after_changing_indices": {"first_mid": [3, 8], "second_mid": [8, 9]},
        "connected_upper_bound": length, "forced_partition_flow_lower_bound": lower,
        "four_name_minimum": length, "image_four_name_minimum": None,
        "before_implantation_attachment_edge_crossed": (0 in side) != ((0, 1) in side),
        "positive_index_vertices": sorted(v for v in side if isinstance(v, int)),
        "positive_hub": "dark", "positive_middle_vertices": [list(w) for w in mids if w in side],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.dumps(check(), indent=2) + "\n"
    if args.check:
        if OUT.read_text() != data:
            raise SystemExit("Saved four-mark certificate differs.")
    else:
        OUT.write_text(data)
    print("Four-name minimum 117, image absent.")


if __name__ == "__main__":
    main()
