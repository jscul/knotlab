"""Compare the longer bond distances between fixed original distinctions."""
import argparse
import json
from itertools import combinations, product
from pathlib import Path
import subprocess
import tempfile

import growth
from specificity import DATA, WORLD
import world_bonds as bonds


def certified_bounds(stage, roots, binary):
    result, receipt = {}, []
    for block in stage.blocks:
        vertices, edges = stage.local_edges(block)
        index = {global_id: i for i, global_id in enumerate(block)}
        queries = sorted(i for key, i in index.items() if any(stage.bundle_of[r] == key for r in roots))
        if not queries:
            continue
        if binary is not None and vertices <= bonds.VERTEX_LIMIT and len(edges) <= bonds.BUNDLE_LIMIT:
            try:
                table = bonds.native_table(binary, vertices, edges, queries)
            except subprocess.TimeoutExpired:
                pass
            else:
                for q, row in table.items():
                    result[block[q]] = dict(zip(block, bonds.distance_values(row), strict=True))
                receipt.append({"vertices": vertices, "queries": len(queries), "method": "exact"})
                continue
        for q in queries:
            best = [bonds.UNKNOWN] * len(edges)
            for cap in range(6, 11):
                search = bonds.AnchoredCuts(vertices, edges)
                try:
                    values = search.through(q, cap)
                except bonds.SearchLimit:
                    break
                best = bonds.distance_values(values, cap)
            result[block[q]] = dict(zip(block, best, strict=True))
        receipt.append({"vertices": vertices, "queries": len(queries), "method": "capped anchored cuts"})
    return result, receipt


def verdict(a, b):
    def interval(x):
        if x == bonds.UNKNOWN:
            return 0, float("inf")
        if x == bonds.INFINITY:
            return (float("inf"),) * 2
        if isinstance(x, str):
            return int(x[1:]) + 1, float("inf")
        return x, x
    lo, hi = interval(a)
    new_lo, new_hi = interval(b)
    if hi < new_lo:
        return "longer"
    if new_hi < lo:
        return "shorter"
    return "equal" if lo == hi == new_lo == new_hi else "unresolved"


def main(*, try_full=False, out=None):
    bonds.PATH_STATES = 120000
    spec = next(x for x in json.loads((WORLD / "inputs.json").read_text())["cases"] if x["id"] == "J1")
    stars = growth.predecessor().source_stars(spec)
    path, ring = spec["roles"]["anchors"], spec["roles"]["ring_edges"][0]
    blank = growth.step(stars, (), ("P", "V"))["stars"]
    loaded = growth.step(stars, ring, ("P", "V"))["stars"]
    for occupied in ((), ring):
        assert growth.step(stars, occupied)["stars"] == blank
    groups = {"path_path": list(combinations(path, 2)), "ring_path": list(product(ring, path)),
              "ring_ring": list(combinations(ring, 2))}
    results, methods, counts = {}, {}, {}
    with tempfile.TemporaryDirectory() as build:
        binary = bonds.prepare_native(Path(build)) if try_full else None
        stages = [bonds.WiredStage(rows) for rows in (blank, loaded)]
        tables = []
        for tag, stage in zip(("quiet", "loaded"), stages, strict=True):
            table, methods[tag] = certified_bounds(stage, path + ring, binary)
            tables.append(table)
        for group, pairs in groups.items():
            results[group] = []
            tally = {"equal": 0, "shorter": 0, "longer": 0, "unresolved": 0}
            for a, b in pairs:
                values = [table[s.bundle_of[a]].get(s.bundle_of[b], bonds.INFINITY)
                          for s, table in zip(stages, tables, strict=True)]
                outcome = verdict(*values)
                tally[outcome] += 1
                results[group].append([a, b, *values, outcome])
            counts[group] = tally
    output = {"unit": "bond size minus one", "ages": [1], "source": "J1", "counts": counts,
              "quiet_and_both_pass_controls_identical": True, "methods": methods,
              "pair_fields": ["first", "second", "quiet", "loaded", "result"], "pairs": results}
    (out or DATA / "original_marks.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--try-full", action="store_true",
                        help="try the predeclared full solver first, with its per-block cutoff")
    parser.add_argument("--out", type=Path, help="output file for an independent replay")
    options = parser.parse_args()
    main(try_full=options.try_full, out=options.out)
