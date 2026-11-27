"""Check the archived choice of systems, link numbering, cut weighting and evidence lineage."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import networkx as nx

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PREV = STUDY.parent / "UPPER-GROWN-20261127-001"
ROOT = STUDY.parents[1]


def jsonlines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def closed_examples():
    return [(path.name, n, row) for path in sorted((PREV / "out").glob("cubic_12_*.jsonl"))
            for n, row in enumerate(jsonlines(path), start=1)]


def exact_numberings(examples):
    remaining = {tuple(map(tuple, row["links"])) for _, _, row in examples}
    found = {}
    for seed in range(1012, 4012):
        graph = nx.random_regular_graph(3, 12, seed=seed)
        order = tuple(graph.edges())
        key = tuple(sorted(order))
        if key in remaining:
            found[key] = (seed, order, graph)
            remaining.remove(key)
            if not remaining:
                return found
    raise ValueError("Some archived labelled systems are missing from the seeded draws")


def orbits(graph, order, chosen):
    lookup = {frozenset(pair): n for n, pair in enumerate(order)}
    renamings = [[lookup[frozenset((p[a], p[b]))] for a, b in order]
                 for p in nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter()]
    def canonical(indices):
        return min(tuple(sorted(p[i] for i in indices)) for p in renamings)
    representative = [canonical([i]) for i in range(len(order))]
    double = {canonical(pair) for pair in combinations(range(len(order)), 2)}
    return {"inequivalent_single_cuts": len(set(representative)),
            "labelled_cuts_equivalent_to_seeded": representative.count(representative[chosen]),
            "inequivalent_double_cuts": len(double),
            "disconnecting_single_cuts": len(list(nx.bridges(graph)))}


def json_queries():
    result = []
    for q in ("box closed system cut link layer above", "eight lower bonds agreements upper grown ring",
              "ordinary growth fresh distinction projection onto earlier distinctions"):
        raw = subprocess.check_output([sys.executable, "-B", "scripts/track.py", "objects", q,
                                       "--until", "2026-11-27", "--limit", "8", "--json"], cwd=ROOT)
        result.append({"query": q, "first_eight_index_ids": [x["id"] for x in json.loads(raw)["index"]]})
    return result


def audit(limit):
    start = time.monotonic()
    closed = closed_examples()
    ordered = sorted((item for item in closed if item[2]["boxes"]), key=lambda item: item[2]["links"])
    by_position = {r["graph"]: r for f in (STUDY / "out").glob("cut_*.jsonl") for r in jsonlines(f)}
    assert len(by_position) == len(ordered)
    rows = ordered[:limit]
    numbered = exact_numberings(rows)
    out = []
    for position, (name, line, row) in enumerate(rows):
        key = tuple(map(tuple, row["links"]))
        seed, order, graph = numbered[key]
        cut = random.Random(20261129 + position).choice(list(range(18)))
        endpoints = sorted(order[cut])
        saved = by_position[position]
        assert (cut, endpoints, row["boxes"]) == (saved["cut distinction"], saved["knots at its ends"],
                                                    saved["boxes before"])
        knots = [[i for i, link in enumerate(order) if k in link] for k in range(12)]
        opened = [s.copy() for s in knots]
        opened[endpoints[1]][opened[endpoints[1]].index(cut)] = 18
        incidence = Counter(d for knot in opened for d in knot)
        assert Counter(incidence.values()) == {1: 2, 2: 17} and all(len(set(s)) == 3 for s in opened)
        out.append({"position": position, "closed_file": name, "line": line, "draw_seed": seed,
                    "closed_supports": knots, "seeded_link": cut, "holders": endpoints,
                    "closed_bonds": row["bonds"], "cut_bonds": saved["bonds"],
                    "closed_boxes": row["boxes"], "cut_boxes": saved["boxes"],
                    **orbits(graph, order, cut)})
    hashes = []
    for record in (STUDY / "frozen.sha256").read_text().splitlines():
        hexdigest, name = record.split()
        now = (ROOT / name).read_bytes()
        original = subprocess.check_output(["git", "show", "a14cb272a5:" + name], cwd=ROOT)
        assert sha256(now).hexdigest() == hexdigest and original == now
        hashes.append({"path": name, "sha256": hexdigest, "matches_freeze": True})
    directions = Counter(("more" if r["cut_bonds"] > r["closed_bonds"] else "equal"
                          if r["cut_bonds"] == r["closed_bonds"] else "fewer") for r in out)
    example_links = [tuple(sorted((i, (i + 1) % 12))) for i in range(12)] + [(i, i + 1) for i in range(0, 12, 2)]
    example = nx.MultiGraph(example_links)
    assert nx.is_connected(example) and set(dict(example.degree()).values()) == {3}
    assert len(set(example_links)) == 12 and len(example_links) == 18
    assert all(len({tuple(pair) for pair in r["links"]}) == 18 for _, _, r in closed)
    return {"closed_systems_in_archive": len(closed), "closed_systems_with_boxes": len(ordered),
            "archived_closed_boxes": sum(r["boxes"] for _, _, r in closed),
            "closed_boxes_with_upper_deletion_checks_in_archive": sum(r["boxes read"] for _, _, r in closed),
            "candidates_checked": len(out), "individual_links": 18 * len(out),
            "pairs_of_links": 153 * len(out),
            **{field: sum(r[field] for r in out) for field in ("inequivalent_single_cuts",
               "labelled_cuts_equivalent_to_seeded", "inequivalent_double_cuts", "disconnecting_single_cuts")},
            "bond_count_after_vs_before": directions, "frozen": hashes,
            "cut_study_has_post_directory": (STUDY / "post").is_dir(),
            "closed_example_outside_the_simple_census": {
                "distinct_pairs_of_holders": 12, "distinctions": 18,
                "holders_in_distinction_order": example_links, "connected": True, "places_per_knot": 3},
            "prior_objects": json_queries(), "rows": out, "elapsed_seconds": round(time.monotonic() - start, 4)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=49)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit(args.limit)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"rows", "frozen", "prior_objects"}}))
