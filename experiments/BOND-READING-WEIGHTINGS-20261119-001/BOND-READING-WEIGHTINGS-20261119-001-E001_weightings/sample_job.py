"""Shared-runner job and deterministic export for the frozen sampling frame."""

import argparse
from collections import Counter
import gzip
import hashlib
import io
from itertools import groupby
import json
from pathlib import Path
import platform
import sys
from tempfile import NamedTemporaryFile

import sample_stages as study


def cases():
    # Each block crosses the three weightings with all sizes, including the smoke.
    for replicate in range(study.REPLICATES):
        for weighting in study.WEIGHTINGS:
            for m in study.SIZES:
                yield f"{weighting}-{m}-{replicate:02d}", [weighting, m, replicate]


def run(case_id, payload):
    return study.run_draw(*payload)


def tally(rows, payload, cell):
    start, *stages, end = rows
    assert start["kind"] == "start" and end["kind"] == "terminal"
    assert all([row[k] for k in ("weighting", "m", "replicate")] == payload for row in rows)
    assert start["J"] == payload[1] and start["age"] == 0
    assert end["observed_stages"] == end["age"] == len(stages)
    assert start["gate"]["census_open_legal"] == (end["outcome"] != "invalid_start")
    assert start["next_round"]["status"] != "stalled" or end["outcome"] == "first_round_stall"
    assert end["outcome"] != "completed" or (len(stages) == study.MAX_AGE and stages[-1]["can_grow"])
    assert end["outcome"] != "closed" or stages[-1]["closed"]
    if end["outcome"] == "expansion_cap":
        attempted = end["attempted_size"]
        assert end["attempted_age"] == end["age"] + 1
        assert attempted["J_lower"] > study.JUNCTION_CAP or attempted["n_lower"] > study.DISTINCTION_CAP
        assert (stages[-1] if stages else start)["can_grow"]

    cell["draws"] += 1
    cell["outcomes"][end["outcome"]] += 1
    for age, row in enumerate(stages, 1):
        assert row["kind"] == "stage" and row["age"] == age
        assert row["J"] <= study.JUNCTION_CAP and row["n"] <= study.DISTINCTION_CAP
        assert row["J"] == len(row["stars"]) and row["n"] == len({b for star in row["stars"] for b in star})
        assert row["can_grow"] == (row["next_round"]["status"] == "available")
        assert row["closed"] == (not row["loose_distinctions"])
        assert row["can_grow"] or age == len(stages)
        cell["observed_by_age"][age] += 1
        cell["terminal_stages_by_age"][age] += not row["can_grow"]


def new_cell():
    return {"draws": 0, "outcomes": Counter(), "observed_by_age": Counter(),
            "terminal_stages_by_age": Counter()}


def verify_stream(path):
    """Check the entire exported stream against the original production implementation."""
    from networkx import from_prufer_sequence

    checker = study.load_source("weighting_verify", study.CHECKER)
    cell = new_cell()
    with gzip.open(path, "rt", encoding="ascii") as stream:
        rows = groupby(map(json.loads, stream), lambda row: (row["weighting"], row["m"], row["replicate"]))
        for (case_id, payload), (key, draw) in zip(cases(), rows, strict=True):
            assert list(key) == payload, case_id
            draw = list(draw)
            tally(draw, payload, cell)
            start, *stages, _ = draw
            weighting, m, replicate = key
            links, trace = study.draw_start(weighting, m, replicate)
            if "prufer_word" in trace:
                tree = from_prufer_sequence(trace["prufer_word"])
                assert sorted(tuple(sorted(pair)) for pair in tree.edges) == trace["tree_links"], case_id
            else:
                parents, naming = trace["insertion_parents"], trace["insertion_to_name"]
                assert sorted(naming) == list(range(m)) and len(parents) == m - 1, case_id
                assert all(0 <= p < child for child, p in enumerate(parents, 1)), case_id
                assert sorted(tuple(sorted((naming[p], naming[child])))
                              for child, p in enumerate(parents, 1)) == trace["tree_links"], case_id
            assert len(start["tree_links"]) == m - 1, case_id
            added = trace["added_links"]
            assert len(added) == ((m + 2) // 4 if weighting == "uniform_tree_plus_links" else 0), case_id
            assert not (set(added) & set(trace["tree_links"])), case_id

            expected = list(study.replay(m, links, fast=False))
            expected[0].update(trace)
            expected = [{"weighting": weighting, "m": m, "replicate": replicate, **row} for row in expected]
            assert draw == json.loads(json.dumps(expected)), case_id

            # The support of a junction is a bond when deleting that holder
            # leaves the augmented incidence graph connected.
            for row in stages:
                arrangement = checker.Arrangement.parse(row["stars"])
                _, adjacency, _ = arrangement.holder_graph()
                universe = (1 << len(adjacency)) - 1
                assert all(checker.connected(universe ^ (1 << u), adjacency)
                           for u in range(row["J"])), (case_id, row["age"])
    return {"draws": cell["draws"], "replayed_stages": sum(cell["observed_by_age"].values())}


def collect(run_dir, output):
    sys.path.insert(0, str(study.ROOT / "scripts"))
    from longrun import load_results

    expected = dict(cases())
    records = load_results(run_dir)
    if set(records) != set(expected):
        raise ValueError(f"missing case records: {sorted(expected.keys() - records.keys())}, "
                         f"unexpected case records: {sorted(records.keys() - expected.keys())}")
    failures = {case_id: row["status"] for case_id, row in records.items() if row["status"] != "ok"}
    if failures:
        raise ValueError(f"unresolved runner outcomes: {failures}")

    output.mkdir(parents=True, exist_ok=True)
    cells = {weighting: {m: new_cell() for m in study.SIZES} for weighting in study.WEIGHTINGS}
    row_count = largest_j = largest_n = 0
    stream_path = output / "sample_stages.jsonl.gz"
    with NamedTemporaryFile(dir=output, prefix="sample_stream_", delete=False) as raw:
        pending = Path(raw.name)
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="ascii", newline="\n") as stream:
                for case_id, payload in expected.items():
                    weighting, m, _ = payload
                    rows = records[case_id]["result"]
                    tally(rows, payload, cells[weighting][m])
                    for row in rows:
                        stream.write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")
                    row_count += len(rows)
                    largest_j = max(largest_j, *(row["J"] for row in rows[:-1]))
                    largest_n = max(largest_n, *(row["n"] for row in rows[:-1]))
    pending.replace(stream_path)

    outcomes, reached, terminal = Counter(), Counter(), Counter()
    for weighting_cells in cells.values():
        for cell in weighting_cells.values():
            assert cell["draws"] == study.REPLICATES == sum(cell["outcomes"].values())
            outcomes.update(cell["outcomes"])
            reached.update(cell["observed_by_age"])
            terminal.update(cell["terminal_stages_by_age"])
    assert row_count == 2 * len(expected) + sum(reached.values())

    run_config = json.loads((run_dir / "job.json").read_text())
    runner = {key: run_config[key] for key in ("workers", "case_timeout", "case_mem", "mem_max")}
    summary = {
        "frame": {"weightings": study.WEIGHTINGS, "start_junction_counts": study.SIZES,
                  "replicates_per_cell": study.REPLICATES, "base_seed": study.BASE_SEED,
                  "seed_key": "{base_seed}|{weighting}|{m}|{replicate}",
                  "seed_conversion": "ASCII SHA-256 interpreted as a big-endian integer",
                  "random_generator": "stdlib random.Random", "python_version": platform.python_version(),
                  "max_age": study.MAX_AGE, "junction_cap": study.JUNCTION_CAP,
                  "distinction_cap": study.DISTINCTION_CAP},
        "production_law": study.START_LAW, "production_cliques": study.CLIQUE_LAW,
        "independent_round_checker": study.CHECKER, "literal_controls": study.check_controls(),
        "runner": {"path": "scripts/longrun.py", "successful_records": len(records), **runner},
        "stream": {"file": stream_path.name, "sha256": hashlib.sha256(stream_path.read_bytes()).hexdigest(),
                   "rows": row_count},
        "draws": len(expected), "outcomes": outcomes, "observed_by_age": reached,
        "terminal_stages_by_age": terminal, "largest_J": largest_j, "largest_n": largest_n,
        "by_cell": cells,
    }
    with NamedTemporaryFile(mode="w", encoding="ascii", dir=output, prefix="sample_summary_",
                            delete=False) as stream:
        pending = Path(stream.name)
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    pending.replace(output / "sample_summary.json")
    return {k: summary[k] for k in ("draws", "outcomes", "observed_by_age", "terminal_stages_by_age",
                                   "largest_J", "largest_n", "stream")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("controls", help="replay the fixed construction and refusal fixtures")
    validator = sub.add_parser("verify", help="replay every draw in the final stream")
    validator.add_argument("--stream", type=Path, default=study.ARTIFACTS / "sample_stages.jsonl.gz")
    exporter = sub.add_parser("collect", help="export one complete shared-runner result set")
    exporter.add_argument("run_dir", type=Path)
    exporter.add_argument("--output", type=Path, default=study.ARTIFACTS)
    args = parser.parse_args()
    if args.command == "controls":
        result = study.check_controls()
    elif args.command == "verify":
        result = verify_stream(args.stream)
    else:
        result = collect(args.run_dir, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
