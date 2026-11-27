"""Audit the committed freeze, pilot, and reported evidence without loading study code."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess


ROOT = Path(__file__).resolve().parents[3]
STUDY = Path("research/RING-BOND-20261127-001")
CONSULTATION = "bda2216350"
FREEZE = "8df7206b94"
REGISTER = "d259996363"
RESULTS = "f027d7d3e9"
INDEX = "8ea02d94ec"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *map(str, args)])


def blob(revision, path):
    return git("show", f"{revision}:{path}")


def archive_paths(revision, path):
    return git("ls-tree", "-r", "--name-only", revision, path).decode().splitlines()


def sha256(contents):
    return hashlib.sha256(contents).hexdigest()


def pilot_summary(contents):
    records = [json.loads(line) for line in contents.splitlines()]
    stages = [
        record[round_name]
        for record in records
        for round_name in ("round 0", "round 1")
        if isinstance(record[round_name], dict)
    ]
    return {
        "rows": len(records),
        "starts": [record["start"] for record in records],
        "round_0_with_bond": sum(bool(record["round 0"]["bonds"]) for record in records),
        "round_1_funded": sum(isinstance(record["round 1"], dict) for record in records),
        "round_1_with_birth_in_holders": sum(
            bool(record["round 1"]["with a birth among the holders"])
            for record in records
            if isinstance(record["round 1"], dict)
        ),
        "stages_with_shape_totals": sum("by shape and missing count" in stage for stage in stages),
        "shape_missing_counts_present": sorted(
            {shape for stage in stages for shape in stage.get("by shape and missing count", {})}
        ),
    }


def start_indices(revision, path):
    records = [json.loads(line) for line in blob(revision, path).splitlines()]
    return [int(record["start"].split()[-1]) for record in records if "start" in record]


def sample_audit(pilots):
    census = Path("research/NAE-LAYER-20261127-001/census.jsonl")
    population = start_indices(FREEZE, census)
    assert population == list(range(len(population)))
    pilot = set(random.Random(1).sample(population, 10))
    declared = sorted(random.Random(20261127).sample(sorted(set(population) - pilot), 1000))
    nae_chunks = [
        start_indices(RESULTS, STUDY / f"out/census_nae_{i}.jsonl") for i in range(6)
    ]
    parity_chunks = [
        start_indices(RESULTS, STUDY / f"out/census_parity_{i}.jsonl") for i in range(8)
    ]
    read_five = start_indices(RESULTS, STUDY / "out/census_nae_m5.jsonl")
    checked_parity_pilot = set(pilots["chk.jsonl"]["starts"]) | set(pilots["par10_m4.jsonl"]["starts"])
    return {
        "archive_population": len(population),
        "pilot_indices": sorted(pilot),
        "parity_pilot_archived_indices": sorted(int(start.split()[-1]) for start in checked_parity_pilot),
        "nae_chunk_sizes": list(map(len, nae_chunks)),
        "nae_matches_frozen_roster": all(chunk == declared[i::6] for i, chunk in enumerate(nae_chunks)),
        "parity_chunk_sizes": list(map(len, parity_chunks)),
        "parity_matches_separate_chunk_prefixes": all(
            chunk == declared[i::8][:len(chunk)] for i, chunk in enumerate(parity_chunks)
        ),
        "cap_five_matches_every_tenth": read_five == declared[::10],
        "cap_five_matches_first_hundred": read_five == declared[:100],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    manifest = blob(FREEZE, STUDY / "frozen.sha256").decode().splitlines()
    digests = {}
    for entry in manifest[:1] if args.pilot else manifest:
        expected, path = entry.split(maxsplit=1)
        digests[path] = {
            "recorded": expected,
            "freeze": sha256(blob(FREEZE, path)),
            "results": sha256(blob(RESULTS, path)),
        }
        assert digests[path]["freeze"] == expected, path

    pilot_paths = archive_paths(FREEZE, STUDY / "pilot")
    pilots = {
        Path(path).name: pilot_summary(blob(FREEZE, path))
        for path in (pilot_paths[:1] if args.pilot else pilot_paths)
    }
    report = {"digests": digests, "prefreeze_pilot": pilots}
    if not args.pilot:
        report["commits_in_order"] = [
            git("show", "-s", "--format=%H %cI", revision).decode().strip()
            for revision in (CONSULTATION, FREEZE, REGISTER, RESULTS, INDEX)
        ]
        report["result_paths_before_freeze"] = archive_paths(FREEZE, STUDY / "out")
        report["result_paths_at_close"] = archive_paths(RESULTS, STUDY / "out")
        report["post_paths_at_close"] = archive_paths(RESULTS, STUDY / "post")
        report["changed_frozen_paths"] = [
            path for path, entry in digests.items() if entry["results"] != entry["recorded"]
        ]
        report["sample_audit"] = sample_audit(pilots)
        ring_output = json.loads(blob(RESULTS, STUDY / "out/ring.json"))
        of_interest = ("readings", "clause", "contact", "is_knot")
        report["archived_knot_checker_rows"] = [
            {field: row[field] for field in of_interest}
            for row in ring_output["checker"]
        ]
    result = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.write_text(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
