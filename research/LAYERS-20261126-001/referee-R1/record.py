"""Read the freeze, archived counts and the prior-work index without changing them."""
import gzip
import json
import resource
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
NOTE = str((STUDY / "README.md").relative_to(ROOT))
FREEZE, RESULT = "f2a940d3b8", "8fdd3c4edd"
SIGN = ROOT / "research/TWO-CLASS-SIGN-20261126-001"
QUERIES = [
    "shortest changes class old ring parity whole start single knot",
    "ordinary growth every old state extends fresh implied",
    "nesting by hand outer law classes of classes",
    "periodic parity two independent class labels shortest cycles",
]


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def prior():
    track = [sys.executable, "-B", "scripts/track.py"]
    gate = run(track + ["objects-gate", NOTE])
    searches = []
    for q in QUERIES:
        flags = ["--until", "2026-11-26", "--exclude", STUDY.name, "--limit", "5", "--json"]
        t = time.monotonic()
        rc, out, err = run(track + ["objects", q] + flags)
        assert not rc, err
        result = json.loads(out)
        before_freeze = {}
        for row in result["other_epics"]:
            ticket = "tickets/"+row["epic"]+".json"
            before_freeze[row["epic"]] = run(["git", "cat-file", "-e", FREEZE+":"+ticket])[0] == 0
        searches.append({"query": q, "ticket_present_at_freeze": before_freeze, "seconds": round(time.monotonic()-t, 4),
                         "curated_rows": [r["id"] for r in result["index"]],
                         "other_studies": [r["id"] for r in result["other_epics"]]})
    return {"gate": {"exit": gate[0], "message": gate[1] or gate[2]}, "searches": searches}


def frozen():
    note = run(["git", "show", FREEZE+":"+NOTE])[1]
    close = run(["git", "show", RESULT+":"+NOTE])[1]
    assert note and close.startswith(note+"\n")
    archived = (STUDY/"multi_class.json").read_text()
    before = json.loads(archived)
    tags = Counter((x["census index"], x["when"]) for x in before)
    score = json.loads((STUDY/"score.json").read_text())
    answer = {}
    failed = []
    flagged = []
    for group in ("census", "heldout"):
        with (STUDY/f"frozen_{group}.jsonl").open() as f:
            rows = [json.loads(line) for line in f]
        counts = Counter()
        for r in rows:
            if not r["grows"]:
                counts[r["end"]] += 1
                continue
            counts["grew"] += 1
            if r["in the conditions"]:
                passed = r["classes"] == r["predicted classes"] and r["each piece parity a label"]
                counts["rule holds" if passed else "rule fails"] += 1
                if not passed:
                    counts[f'fail with {r["classes"]} classes'] += 1
                    failed.append(["census" if group == "census" else "held out", r["index"],
                                   r["classes"], r["predicted classes"], r["each piece parity a label"]])
            else:
                counts[f'outside with {r["classes"]} classes'] += 1
            if r.get("labels read knot by knot") is False:
                flagged.append(["census" if group == "census" else "held out", r["index"], r["classes"]])
        answer[group] = dict(counts)
    assert failed == score["P1 breaks"] and flagged == score["candidate tower steps"]
    with gzip.open(SIGN/"census_canonical.jsonl.gz","rt") as f:
        old = [json.loads(line) for line in f]
    missing = [int(x["structure"].split()[-1]) for x in old
               if x["start"]["loose free"]["classes"] >= 4
               and (int(x["structure"].split()[-1]), "start") not in tags]
    return {"registered_note": NOTE, "freeze": FREEZE, "results": RESULT,
            "frozen_text_is_prefix_of_results_note": True, "score_matches_failure_and_candidate_lists": True,
            "scores": answer, "candidate_list": flagged, "early_reader_table": {"rows": len(before),
            "unique_row_stages": len(tags), "duplicated_grown_rows": [i for (i,k),v in tags.items() if v>1],
            "missing_source_rows": missing}}


if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    # Same command and settings on one query before the set of four.
    if "--pilot" in sys.argv:
        QUERIES[:] = QUERIES[:1]
    start = time.monotonic()
    rec = {"prior_work": prior(), "freeze_and_archive": frozen()}
    rec["seconds"] = round(time.monotonic()-start, 4)
    path = HERE / ("record_pilot.json" if "--pilot" in sys.argv else "record.json")
    path.write_text(json.dumps(rec, indent=2)+"\n")
