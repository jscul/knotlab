"""Exhaust all marked single cuts and all double cuts of two named closed sources."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
import json
from pathlib import Path
import subprocess
from time import perf_counter

import networkx as nx

from opening_witness import HERE, split_source


def holders(supports):
    return [tuple(i for i, k in enumerate(supports) if x in k) for x in range(18)]


def grouped_cuts(supports, number):
    ends = holders(supports)
    assert all(len(pair) == 2 for pair in ends)
    graph = nx.Graph(ends)
    numbers = {frozenset(pair): i for i, pair in enumerate(ends)}
    moves = [[numbers[frozenset((renaming[u], renaming[v]))] for u, v in ends]
             for renaming in nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter()]
    remaining = set(combinations(range(18), number))
    orbits = []
    while remaining:
        least = min(remaining)
        orbit = {tuple(sorted(move[i] for i in least)) for move in moves}
        assert orbit <= remaining and least in orbit
        orbits.append(tuple(sorted(orbit)))
        remaining -= orbit
    return orbits


def source_positions(rows):
    witness = json.loads((HERE.parents[1] / "RING-BOND-20261127-001" / "referee-R1" /
                          "layer_witness.json").read_text())["source_knots_not_all_equal"]
    graph = nx.Graph(holders(witness))
    original = [r["position"] for r in rows if nx.is_isomorphic(graph, nx.Graph(holders(r["closed_supports"])))]
    alternate = [r["position"] for r in rows if r["closed_file"] == "cubic_12_3.jsonl" and r["line"] == 1]
    assert len(original) == len(alternate) == 1
    return {"original_twelve_knot_witness": original[0], "alternative_one_cut_witness": alternate[0]}


def jobs_for(rows, options, scope):
    jobs = []
    for row in rows:
        sizes = ([] if scope == "double" else [1]) + (
            [2] if scope != "single" and row["position"] in options.values() else [])
        for n in sizes:
            orbits = grouped_cuts(row["closed_supports"], n)
            reference = row["inequivalent_single_cuts" if n == 1 else "inequivalent_double_cuts"]
            assert len(orbits) == reference
            for orbit in orbits:
                jobs.append((row, orbit))
    return jobs


def evaluate(job, binary):
    row, orbit = job
    chosen = orbit[0]
    supports = split_source(row["closed_supports"], chosen)
    masks = [sum(1 << x for x in k) for k in supports]
    text = " ".join(map(str, [18 + len(chosen), len(supports)] + masks)) + "\n"
    raw = subprocess.run([binary], input=text, text=True, capture_output=True, check=True)
    data = json.loads(raw.stdout)
    assert len(data["loose_distinctions"]) == 2 * len(chosen)
    if len(chosen) == 1 and (row["seeded_link"],) in orbit:
        assert (row["cut_bonds"], row["cut_boxes"]) == (data["bonds"], len(data["boxes"]))
    return {"source_position": row["position"], "source_file": row["closed_file"], "source_line": row["line"],
            "equivalent_labelled_cuts": orbit, **data}


def summarize(records):
    groups = defaultdict(list)
    for row in records:
        n = len(row["equivalent_labelled_cuts"][0])
        groups[("all" if n == 1 else row["source_position"], n)].append(row)
    out = []
    for (source, n), rows in groups.items():
        dist_classes = Counter()
        dist_marked = Counter()
        for r in rows:
            count = len(r["boxes"])
            dist_classes[count] += 1
            dist_marked[count] += len(r["equivalent_labelled_cuts"])
        out.append({
            "number_cut": n, "source_position": source, "sources_checked": len({r["source_position"] for r in rows}),
            "cut_orbits": len(rows), "labelled_cuts": sum(dist_marked.values()),
            "positive_cut_orbits": len(rows) - dist_classes[0],
            "positive_labelled_cuts": sum(dist_marked.values()) - dist_marked[0],
            "sources_with_a_positive": sorted({r["source_position"] for r in rows if r["boxes"]}),
            "box_counts_across_cut_orbits": dict(sorted(dist_classes.items())),
            "box_counts_across_labelled_cuts": dict(sorted(dist_marked.items())),
            "boxes_counted_per_labelled_cut": sum(x * c for x, c in dist_marked.items()),
            "box_incidences_counting_one_representative_per_cut_orbit": sum(x * c for x, c in dist_classes.items()),
            "range_of_bond_counts": [min(r["bonds"] for r in rows), max(r["bonds"] for r in rows)],
            "total_engine_seconds": round(sum(r["seconds"] for r in rows), 3),
        })
    return out


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, default=HERE / "recount_engine")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2, choices=(1, 2))
    parser.add_argument("--scope", choices=("all", "single", "double"), default="all")
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start = perf_counter()
    archive = json.loads((HERE / "archive_counts.json").read_text())
    rows = archive["rows"]
    options = source_positions(rows)
    jobs = jobs_for(rows, options, args.scope)
    totals = Counter(len(orbit[0]) for _, orbit in jobs)
    if args.pilot:
        single, double = ([j for j in jobs if len(j[1][0]) == n] for n in (1, 2))
        singles = [x for x in single if x[0]["position"] == options["alternative_one_cut_witness"]]
        jobs = singles[:2] + [j for pos in options.values() for j in [x for x in double if x[0]["position"] == pos][:2]]
    with ThreadPoolExecutor(args.workers) as pool:
        records = list(pool.map(lambda j: evaluate(j, args.engine.resolve()), jobs))
    out = {"coverage": ("first two representatives on the indicated sources for timing" if args.pilot else
                        "every marked cut in the specified populations, up to a renaming of its source"),
           "two_cut_source_positions": options, "planned_counts_by_number_cut": totals, "workers": args.workers,
           "elapsed_seconds": round(perf_counter() - start, 4), "summaries": summarize(records), "records": records}
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "records"}), flush=True)


if __name__ == "__main__":
    main()
