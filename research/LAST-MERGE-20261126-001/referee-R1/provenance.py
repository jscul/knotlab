"""Check the actual freeze, dated object searches, and the files carrying the public wording."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
STUDY = OUT.parent.relative_to(ROOT)
FIT = "research/SETTLE-BOUND-20261126-001"
READER = "research/LOOK-ALIKE-20261126-001"
FREEZE = "4efff45d0a"
RESULT = "4707b8880b"
FIT_REF = "368facf6be"
SEARCHES = (
    "last fall in births",
    "settling round largest block",
    "local reader settled view",
    "binomial burst two chains",
    "live neighbour reduction",
)


def command(args, data=None):
    return subprocess.run(args, cwd=ROOT, input=data, capture_output=True, check=False)


def git(*args):
    result = command(["git", *map(str, args)])
    result.check_returncode()
    return result.stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit(pilot):
    started = time.perf_counter()
    note = str(STUDY / "README.md")
    frozen = git("show", f"{FREEZE}:{note}")
    reported = git("show", f"{RESULT}:{note}")
    tracked = [line.decode() for line in git("ls-tree", "-r", "--name-only", FREEZE, STUDY).splitlines()]
    scripts = [str(STUDY / "sample.py"), f"{FIT}/bound.py", f"{READER}/alike.py",
               f"{READER}/phase2.py", *[str(p.relative_to(ROOT)) for pattern in
               ("experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/*/eng.py",
                "experiments/COPYING-PARTS-20261123-001A/*/cpcensus.py") for p in ROOT.glob(pattern)]]
    stable = {}
    for path in scripts:
        blobs = [git("show", f"{rev}:{path}") for rev in (FREEZE, RESULT)]
        stable[path] = {"same_at_freeze_results_and_review": blobs[0] == blobs[1] == (ROOT / path).read_bytes(),
                        "sha256_at_freeze": digest(blobs[0])}
    cli = [sys.executable, "-B", "scripts/track.py"]
    gates = {}
    for label, path, data in (("freeze", "/dev/stdin", frozen), ("current note", note, None)):
        p = command([*cli, "objects-gate", path], data)
        gates[label] = {"exit": p.returncode, "message": (p.stdout + p.stderr).decode().strip()}
    searches = {}
    for query in SEARCHES[:1] if pilot else SEARCHES:
        flags = ["--until", "2026-11-26", "--exclude", STUDY.name, "--limit", "5", "--json"]
        p = command([*cli, "objects", query, *flags])
        p.check_returncode()
        hits = json.loads(p.stdout)
        searches[query] = {
            "flags": flags, "index": [r["id"] for r in hits["index"]],
            "unindexed": [r["id"] for r in hits["other_epics"]],
        }
    return {
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "freeze": FREEZE, "results": RESULT, "earlier_settling_referee": FIT_REF,
        "freeze_is_ancestor_of_earlier_referee": command(["git", "merge-base", "--is-ancestor", FREEZE, FIT_REF]).returncode == 0,
        "earlier_referee_is_ancestor_of_results": command(["git", "merge-base", "--is-ancestor", FIT_REF, RESULT]).returncode == 0,
        "committed_at": {rev: git("show", "-s", "--format=%cI", rev).decode().strip() for rev in (FREEZE, FIT_REF, RESULT)},
        "study_files_at_freeze": tracked,
        "freeze_is_byte_for_byte_prefix_of_results": reported.startswith(frozen),
        "results_are_current_note": reported == (ROOT / note).read_bytes(),
        "first_commit_containing_scoring_script": git("log", "--no-renames", "-1", "--diff-filter=A", "--format=%h", RESULT, "--", STUDY / "merge_test.py").decode().strip(),
        "separate_registration_or_deviations_paths": [p for p in git("ls-tree", "-r", "--name-only", RESULT, STUDY).decode().splitlines()
                                                     if any(term in p.lower() for term in ["deviat", "contract", "prereg", "pre-reg"])],
        "sampling_growth_and_reading_code": stable, "prior_work_gates": gates,
        "prior_work_searches_from_present_index": searches,
        "earlier_credit": [
            f"{READER}/README.md (phase 2, seven five-knot starts; round 11 burst ending, cuts 14 and 16)",
            f"{FIT}/referee-R1/report.md (item 5, offsets for all 47 earlier late starts and 794 of 815 with a fall)",
        ],
    }


if __name__ == "__main__":
    opts = argparse.ArgumentParser(description=__doc__)
    opts.add_argument("--pilot", action="store_true")
    args = opts.parse_args()
    result = audit(args.pilot)
    path = OUT / ("provenance_pilot.json" if args.pilot else "provenance.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path.name, result["elapsed_seconds"], result["prior_work_gates"])
