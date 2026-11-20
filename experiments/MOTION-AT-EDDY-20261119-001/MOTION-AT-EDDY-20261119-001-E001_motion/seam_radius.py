"""Find every possible through exit under a rooted neighbourhood symmetry."""

import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def exits_at_radius(source, seam, incoming, through, radius):
    vertices = nx.single_source_shortest_path_length(source, seam, cutoff=radius)
    ball = source.subgraph(vertices).copy()
    for v in ball:
        ball.nodes[v]["role"] = "root" if v == seam else "incoming" if v == incoming else ""
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        ball, ball, node_match=lambda x, y: x["role"] == y["role"]
    )
    return sorted({p[through] for p in matcher.isomorphisms_iter()})


def main():
    cases = json.loads((HERE / "holdout.json").read_text())["cases"]
    result = {}
    for case in cases:
        graph = nx.Graph(case["meetings"])
        path = case["roles"]["background"]
        rows = []
        for i in (28, 54):
            for sign in (-1, 1):
                seen = [exits_at_radius(graph, path[i], path[i-sign], path[i+sign], r)
                        for r in (1, 2)]
                expected = 3 if case["id"] == "first_cut85" and i == 28 else 1
                assert [len(s) for s in seen] == [3, expected]
                rows.append(dict(seam=path[i], incoming=path[i-sign], through=path[i+sign],
                                 images_at_radius_one=seen[0], images_at_radius_two=seen[1]))
        result[case["id"]] = rows
    (DATA / "seam_radius.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
