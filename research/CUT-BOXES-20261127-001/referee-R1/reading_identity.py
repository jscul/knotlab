"""Match the two strict certificates and test when the chosen start first carries a box."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import time

import networkx as nx
from upper_check import TruthTable

HERE = Path(__file__).resolve().parent


def named_system(supports, carriers):
    graph = nx.Graph()
    def node(kind, index):
        token = (kind, index)
        graph.add_node(token, kind=kind)
        return token
    for i, knot in enumerate(supports):
        for d in knot:
            graph.add_edge(node("knot", i), node("distinction", d))
    for i, carrier in enumerate(carriers):
        graph.add_edge(node("pair", i // 2), node("carrier", i))
        for d in carrier:
            graph.add_edge(node("carrier", i), node("distinction", d))
    return graph


def matched_systems(left, right):
    isos = nx.isomorphism.GraphMatcher(left, right, node_match=lambda a, b: a["kind"] == b["kind"])
    mapping = next(isos.isomorphisms_iter(), None)
    if mapping is None:
        return None
    return {kind: [mapping[(kind, i)][1] for i in sorted(j for k, j in left if k == kind)]
            for kind in sorted({k for k, _ in left})}


def run_case(exe, knots):
    ids = sorted({d for s in knots for d in s})
    masks = [sum(1 << ids.index(d) for d in s) for s in knots]
    record = " ".join(map(str, [len(ids), len(masks), *masks])) + "\n"
    row = json.loads(subprocess.check_output([str(exe)], text=True, input=record))
    image_sizes = Counter()
    orbits = []
    if row["boxes"]:
        table = TruthTable(knots)
        named = named_system(knots, [])
        for i in range(len(knots)):
            named.nodes["knot", i]["cohort"] = i >= 10
        renamings = list(nx.isomorphism.GraphMatcher(named, named, node_match=lambda a, b: a == b).isomorphisms_iter())
        def comparison_key(box, p):
            return tuple(sorted(tuple(sorted((tuple(sorted(p["distinction", ids[d]][1] for d in c)), s)
                for c, s in pair)) for pair in box))
        seen = set()
        for box in row["boxes"]:
            orbit = frozenset(comparison_key(box, p) for p in renamings)
            if orbit not in seen:
                seen.add(orbit)
                orbits.append(len(orbit))
            carriers = [tuple(ids[i] for i in reading) for pair in box for reading, _ in pair]
            size = sum(bool(table.forbidden_states(tuple(zip(carriers, values)))) for values in product((0, 1), repeat=6))
            image_sizes[size] += 1
        table.equal.cache_clear()
    return {"birth_preserving_orbit_sizes": orbits, "six_word_counts_by_box": image_sizes, "knots": len(knots), "distinctions": len(ids), "bonds": row["bonds"], "boxes": len(row["boxes"]),
            "allowed": row["allowed_states"], "every_loose_read": row["boxes_reading_every_loose_distinction"],
            "every_place_used": row["boxes_with_every_carrier_place_used"], "seconds": row["seconds"]}


def compare(exe, limit):
    grown = json.loads((HERE / "witness_states.json").read_text())
    split = json.loads((HERE / "opening_witness.json").read_text())["checked"]["opened_new_box"]
    supports, carriers = grown["ten_start_laws_then_two_birth_laws"], grown["carriers"]
    mapping = matched_systems(named_system(supports, carriers), named_system(split["supports"], split["carriers"]))
    match_sources = matched_systems(named_system(supports, []), named_system(split["supports"], []))
    cases = {"start": supports[:-2], "first_birth_only": supports[:-1],
             "second_birth_only": supports[:-2] + supports[-1:], "actual_funded_round": supports}
    return {"growth_to_split_including_carrier_pairs": mapping, "growth_to_split_sources": match_sources,
            "readings": {name: run_case(exe, ks) for name, ks in list(cases.items())[:limit]}}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--engine", required=True, type=Path)
    p.add_argument("--limit", type=int, default=4)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    start = time.monotonic()
    out = compare(args.engine.resolve(), args.limit)
    out["elapsed_seconds"] = round(time.monotonic() - start, 4)
    if args.output:
        args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))
