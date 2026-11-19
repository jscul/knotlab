"""Apply the complete fewest-count rule twice to three simple diamond starts."""

import argparse
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREVIOUS = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_extend")))
import extend as law


# The four diamond vertices are s,t,a,b (0,1,2,3). The distinctions 0 through
# 4 on them are sa,sb,ta,tb,ab, in that order.
STARTS = {
    7: [
        [0, 1, 5, 6, 7], [2, 3, 14, 15], [0, 2, 4], [1, 3, 4],
        [5, 8, 9], [6, 10, 11], [7, 12, 13],
    ],
    8: [
        [0, 1, 5, 6, 7], [2, 3, 16, 17], [0, 2, 4], [1, 3, 4],
        [5, 8, 9, 12, 13], [6, 8, 10, 14], [10, 11, 15], [7, 9, 11],
    ],
    10: [
        [0, 1, 5, 6, 13, 14], [2, 3, 11, 12], [0, 2, 4], [1, 3, 4],
        [5, 7, 8], [6, 7, 9], [8, 10, 15], [9, 10, 16], [11, 17, 18], [12, 19, 20],
    ],
}


def swap(x):
    return {0: 2, 2: 0}.get(x, x)


def exterior_cut(stars):
    graph = nx.Graph()
    for name, u, v in law.L.graph_of(stars)[1]:
        if name >= 5:
            capacity = graph.get_edge_data(u, v, {}).get("capacity", 0)
            graph.add_edge(u, v, capacity=capacity + 1)
    return nx.minimum_cut_value(graph, 0, 1)


def check_table(stars):
    table, labels = law.L.table(stars)
    differences = []
    for pair, d in table.items():
        image = tuple(sorted(swap(x) for x in pair))
        if d != table[image]:
            differences.append({"pair": list(pair), "image": list(image),
                                "distance": d, "image_distance": table[image]})
    assert all(isinstance(d, int) for d in table.values())
    return {"junctions": len(stars), "width": len(labels), "compared_pairs": len(table),
            "exterior_min_cut": exterior_cut(stars), "differences": differences,
            "distance_0_1": table[0, 1], "distance_1_2": table[1, 2]}


def additions(earlier, later):
    own = law.L.owners(earlier)
    result = []
    for j, support in enumerate(later[len(earlier):], len(earlier)):
        used = sorted(support & own.keys())
        assert all(len(own[x]) == 1 for x in used)
        result.append({"junction": j, "parents": sorted(own[x][0] for x in used),
                       "taken": used, "fresh": sorted(support - own.keys())})
    return result


def replay(size):
    start = list(map(frozenset, STARTS[size]))
    current = law.grow1(start)
    successor = law.grow1(current)
    stages = {"start": start, "current": current, "next": successor}
    assert all(law.L.max_shared(stars) == 1 for stars in stages.values())
    bonds = {frozenset(cut) for cut in law.L.bonds(start)}
    assert all(len(star) >= 3 and star in bonds for star in start)
    assert all(len(cut) > 1 for cut in bonds)
    owners = law.L.owners(current)
    perm = {x: swap(x) for x in sorted(owners)}
    reading = law.reading(current)
    live_sites, loose, common = reading
    assert all(len(owners[x]) == 2 for x in range(5))
    assert all(all(swap(x) == x for x in current[u]) for u in live_sites)
    assert law.keeps_reading(perm, current, current, reading, reading) == {u: u for u in live_sites}
    comparisons = {name: check_table(stars) for name, stars in stages.items()}
    assert not comparisons["current"]["differences"]
    assert comparisons["current"]["exterior_min_cut"] == 2
    assert comparisons["next"]["exterior_min_cut"] == 1
    assert [row["pair"] for row in comparisons["next"]["differences"]] == [
        [0, 1], [0, 3], [1, 2], [2, 3]]
    assert (comparisons["next"]["distance_0_1"], comparisons["next"]["distance_1_2"]) == (2, 3)
    case = {"a": {key: [sorted(s) for s in stars] for key, stars in stages.items()},
            "permutation": [list(item) for item in perm.items()]}
    report = {"certificate": f"construct_{size}.json", "tables": comparisons,
              "rounds": [additions(start, current), additions(current, successor)],
              "current_live": live_sites, "current_loose": {str(u): sorted(loose[u]) for u in live_sites},
              "current_common_neighbor_sets_of_size_at_least_two": sorted(sorted(g) for g in common),
              "all_current_live_supports_fixed_pointwise": True,
              "max_ordinary_meeting_multiplicity_at_all_stages": 1}
    return case, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare saved files without writing")
    args = parser.parse_args()
    files, reports = {}, {}
    for n in STARTS:
        files[f"construct_{n}.json"], reports[str(n)] = replay(n)
    files["construct_results.json"] = reports
    for name, body in files.items():
        path = OUT / name
        content = json.dumps(body, indent=2) + "\n"
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f"Record differs: {path}")
        else:
            path.write_text(content)
    print("Seven-, eight- and ten-junction certificates pass both complete-round replays and all pair comparisons.")


if __name__ == "__main__":
    main()
