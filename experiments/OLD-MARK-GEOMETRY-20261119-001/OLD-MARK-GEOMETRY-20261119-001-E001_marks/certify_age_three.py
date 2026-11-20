"""Certify the two longer comparisons at age three using an older quiet shore."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path

from certify import OUTPUT, Wired, frozen_source, min_fill, pair


def run(earlier):
    old, marks, ring, digest, step = frozen_source()
    payload = earlier.read_bytes()
    baseline = json.loads(payload)
    assert baseline["parity_source_sha256"] == digest and baseline["old_path_marks"] == marks
    assert baseline["action_table"] == ["P", "V"]
    previous = {tuple(row["path_positions"]): row for row in baseline["ages"]["2"]["pairs"]}
    stages, graphs = {}, {}
    for name, occupied in (("quiet", ()), ("loaded", ring)):
        stars = old
        for age in range(1, 4):
            frame = step(stars, occupied, ("P", "V"), caps={"junctions": 6000, "distinctions": 32000})
            assert frame["status"] == "extend"
            stars, occupied = frame["stars"], frame["occupied"]
            literal = sha256(json.dumps(stars, separators=(",", ":")).encode()).hexdigest()
            if age == 2:
                assert literal == baseline["ages"]["2"]["stages"][name]["literal_stars_sha256"]
        graph = graphs[name] = Wired(stars)
        stages[name] = {"knots": graph.outside, "distinctions": len(graph.ends),
                        "literal_stars_sha256": literal}
    decomposition = min_fill(graphs["loaded"])
    stages["loaded"]["largest_bag_including_exterior"] = max(len(b.names) for b in decomposition)
    budget = 500000
    rows = []
    for i, j in ((0, 15), (2, 5)):
        e, f = marks[i], marks[j]
        bound = previous[i, j]["quiet"]
        earlier_best = min((item for item in bound["orientations"] if item["status"] == "exact"),
                           key=lambda item: item["cost"])
        carried = graphs["quiet"].witness(sum(1 << knot for knot in earlier_best["shore"]))
        assert carried == {k: earlier_best[k] for k in carried}
        assert {e, f} <= set(carried["crossing_distinctions"])
        loaded = pair(graphs["loaded"], decomposition, e, f, budget)
        assert loaded["status"] == "exact"
        gap = loaded["bond_distance"] - (carried["cost"] - 1)
        assert gap == 2
        rows.append({"path_positions": [i, j], "loaded": loaded, "quiet_connected_witness": carried,
                     "quiet_distance_upper_bound": carried["cost"] - 1, "delta_lower_bound": gap})
    return {"source": "J1", "age": 3, "work_limit_per_orientation": budget, "stages": stages,
            "earlier_panel_sha256": sha256(payload).hexdigest(), "pairs": rows}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--earlier", type=Path, default=OUTPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT.with_name("certify_age_three.json"))
    args = parser.parse_args()
    result = run(args.earlier)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
