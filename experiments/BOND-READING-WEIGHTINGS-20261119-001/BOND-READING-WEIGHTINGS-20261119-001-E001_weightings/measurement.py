"""Group equal reached stages without changing the multiplicity of any sample draw."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import warnings

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
KEY = "BOND-READING-WEIGHTINGS-20261119-001"
OUTPUT = ROOT / "artifacts" / KEY / (KEY + "-E001_weightings")
STREAM = OUTPUT / "sample_stages.jsonl.gz"
SHAPES = OUTPUT / "sample_shape_index.json"


def holder_graph(stars):
    outside = len(stars)
    holders = defaultdict(list)
    for vertex, row in enumerate(stars):
        for name in row:
            holders[name].append(vertex)
    graph = nx.Graph()
    graph.add_nodes_from(range(outside + 1))
    for vertices in holders.values():
        if len(vertices) == 1:
            vertices = [vertices[0], outside]
        u, v = vertices
        if graph.has_edge(u, v):
            graph[u][v]["weight"] += 1
        else:
            graph.add_edge(u, v, weight=1)
    for vertex in graph:
        graph.nodes[vertex]["color"] = str((vertex == outside, sorted(d["weight"] for d in graph[vertex].values())))
    return graph


def boundary_features(graph, outside):
    live = set(graph[outside])
    old = set(graph) - live - {outside}
    old_touching = {v for u in live for v in graph[u] if v in old}
    counts = []
    for group in nx.connected_components(graph.subgraph(old - old_touching)):
        boundary = {v for u in group for v in graph[u] if v in old_touching}
        counts.append(len(boundary))
    ordinary = graph.subgraph(set(graph) - {outside})
    return {"exhausted_touching_live": len(old_touching),
            "most_old_neighbors_one_live": max((len(set(graph[u]) & old) for u in live), default=0),
            "older_parts": len(counts), "largest_older_part_attachment": max(counts, default=0),
            "older_parts_with_three_or_more": sum(v >= 3 for v in counts),
            "movable_names": sum(d["weight"] for u,v,d in graph.edges(data=True) if u in old and v in old),
            "ordinary_tree": nx.is_tree(ordinary), "ordinary_single_meetings": all(
                d["weight"] == 1 for _,_,d in ordinary.edges(data=True))}


def prepare():
    links = defaultdict(list)
    graphs = []
    shapes = []
    members = Counter()
    with gzip.open(STREAM, "rt") as source:
        for line in source:
            row = json.loads(line)
            if row["kind"] != "stage":
                continue
            graph = holder_graph(row["stars"])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                fingerprint = nx.weisfeiler_lehman_graph_hash(graph, node_attr="color", edge_attr="weight", iterations=5)
            key = (row["J"], row["n"], row["can_grow"], fingerprint)
            representative = None
            for possible in links[key]:
                if nx.is_isomorphic(graph, graphs[possible],
                                    node_match=nx.algorithms.isomorphism.categorical_node_match("color", None),
                                    edge_match=nx.algorithms.isomorphism.categorical_edge_match("weight", None)):
                    representative = possible
                    break
            if representative is None:
                representative = len(graphs)
                graphs.append(graph)
                links[key].append(representative)
                shapes.append({"shape": representative, "can_grow": row["can_grow"], "J": row["J"],
                               "n": row["n"], "stars": row["stars"],
                               "boundary": boundary_features(graph, row["J"]), "observations": []})
            tag = (row["weighting"], row["m"], row["replicate"], row["age"])
            shapes[representative]["observations"].append(tag)
            members[tag] += 1
    assert all(v == 1 for v in members.values())
    SHAPES.write_text(json.dumps({"visits": len(members), "shape_count": len(shapes), "shapes": shapes},
                                separators=(",", ":")) + "\n")
    print(f"{len(members)} observations, {len(shapes)} isomorphism classes; all equivalent graphs directly matched.")


def cases():
    for record in json.loads(SHAPES.read_text())["shapes"]:
        yield str(record["shape"]), {x: record[x] for x in ["shape","can_grow","J","n","stars"]}


def run(case_id, payload):
    if not payload["can_grow"]:
        return {"shape": payload["shape"], "lo": 0, "hi": 0, "method": "strictly terminal"}
    from scale_reader import scale_order

    coarse = scale_order(payload["stars"], has_successor=True)
    lo, hi = coarse["lo"], coarse["hi"]
    answer = {"shape": payload["shape"], "coarse": coarse, "method": "pair certificate"}
    if lo != hi:
        from order_reader import read_order
        exact = read_order(payload["stars"])
        lo, hi = max(lo, exact["lo"]), min(hi, exact["hi"])
        assert lo <= hi, (case_id, coarse, exact)
        answer.update(exact_engine=exact, method="intersection of certified intervals")
    answer.update(lo=lo, hi=hi)
    return answer


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("action", choices=["prepare"])
    cli.parse_args()
    prepare()
