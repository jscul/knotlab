"""Independently audit the changed three-mark bonds by pinned integer cuts."""

from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

import networkx as nx

from common_bonds import INFINITY, OUTPUT, Wiring, by_flows, recoding_control
from bond_later import PinFlow
import side_sources


def check_cut(stars, marks, witness, cost):
    holders = defaultdict(list)
    for knot, support in enumerate(stars):
        for distinction in support:
            holders[distinction].append(knot)
    outside = len(stars)
    edges = {d: tuple(ends if len(ends) == 2 else [ends[0], outside]) for d, ends in holders.items()}
    graph = nx.Graph(edges.values())
    inside = set(witness["knots"])
    assert outside not in inside
    assert nx.is_connected(graph.subgraph(inside)) and nx.is_connected(graph.subgraph(set(graph) - inside))
    crossing = {d for d, (a, b) in edges.items() if (a in inside) != (b in inside)}
    assert crossing == set(witness["distinctions"]) and len(crossing) == cost
    assert set(marks) <= crossing


def profile(spec, early, through, limit):
    roles = spec["roles"]
    start = roles["seams"][0]
    indices = [(start, start + 1, start + 2), (start + 1, start + 2, start + 3)]
    marks = [tuple(roles["anchors"][i] for i in q) for q in indices]
    lookup = [early["query_indices"].index(list(group)) for group in indices]
    result = {}
    for arm, occupied in side_sources.loads(spec).items():
        iterator = side_sources.generate(spec, occupied, min(through, side_sources.AGES[spec["id"]]),
                                         side_sources.CAPS)
        known = [None] * len(marks)
        scans = {}
        while True:
            try:
                age, frame = next(iterator)
            except StopIteration as stop:
                result[arm] = {"frames": scans, "termination": stop.value}
                break
            if not age:
                continue
            wire = Wiring(frame["stars"])
            flow = PinFlow(wire)
            records = []
            for i, query in enumerate(marks):
                low, high, optimum, work, cap = by_flows(flow, query, known[i], limit)
                if optimum is None:
                    witness = None
                else:
                    witness = wire.witness(optimum, query, high)
                    check_cut(frame["stars"], query, witness, high)
                    known[i] = optimum
                if age <= 2:
                    expected = early["activity_traces"][arm]["frames"][str(age)]["readings"][lookup[i]][0]
                    assert low == high == expected
                if age == 1:
                    assert low == high != INFINITY
                    recoding_control(wire, query, high)
                records.append({"bounds": [low, high], "witness": witness,
                                "integer_flow_relaxations": work, "cap": cap})
            scans[str(age)] = {"knots": wire.n, "distinctions": len(wire.edge), "reads": records}
            print(spec["id"], arm, age, [record["bounds"] for record in records], flush=True)
    return {"indices": indices, "physical_distinctions": marks, "arms": result}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=12)
    parser.add_argument("--flows", type=int, default=1000)
    parser.add_argument("--early", type=Path, default=OUTPUT / "common_bonds_translated_age_two.json")
    parser.add_argument("--out", type=Path, default=OUTPUT / "common_bonds_witnesses.json")
    args = parser.parse_args()
    raw = args.early.read_bytes()
    control = json.loads(raw)["cases"]
    result = {}
    for key in ("T4", "PT4"):
        result[key] = profile(side_sources.cases()[key], control[key], args.through, args.flows)
    args.out.write_text(json.dumps({"schema": 1, "unit": "physical bond size",
                                    "early_sha256": sha256(raw).hexdigest(), "max_age": args.through,
                                    "flow_limit_per_query": args.flows,
                                    "age_one_recoding": "all sixteen triple-arm readings",
                                    "cases": result}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
