"""Recount opportunities to observe different second forms and the every-round check."""
import gzip
import json
import sys
import time
from collections import Counter, defaultdict
from itertools import islice
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ID = "MADE-COPIER-20261125-001"
ART = next((ROOT / "artifacts" / (ID + "C")).iterdir())
RUNS = ("R1a", "R1b", "R1c", "R1d", "R2", "R5", "R6")
STAGES = ("read apart", "met", "initial form case", "confirmed")

def rows(name, limit):
    with gzip.open(ART / (name + ".jsonl.gz"), "rt") as inp:
        for line in islice(inp, limit):
            yield json.loads(line)

def id_pair(row, pair):
    return (row["seed"], pair["s"], tuple(pair["X"]), tuple(pair["Y"]))

def opportunities(limit=None):
    positive = set()
    for filename in ("R3.json", "Rcond.json"):
        for cell in json.loads((ART / filename).read_text())["cases"]:
            if cell["reading"] == "form" and cell["confirmation"]["confirmed"]:
                positive.add(id_pair(cell, cell))
    counts, size_events, verified, seen = Counter(), Counter(), set(), set()
    by_form = defaultdict(lambda: {stage: Counter() for stage in STAGES})
    examples = {}
    for source in RUNS:
        for row in rows(source, limit):
            counts[source + " rows"] += 1
            if "error" in row or row["weighting"] != "T1" or row["knot_test"]["n_fails"]:
                continue
            for p in row["pairs"]:
                key = id_pair(row, p)
                if key in seen or p["same_form"]:
                    continue
                seen.add(key)
                x = (row["law"], p["xform"])
                g = p["yform"]
                tally = by_form[x]
                tally["read apart"][g] += 1
                if p["meet"] is None:
                    continue
                tally["met"][g] += 1
                if "form" not in p["after"]:
                    continue
                tally["initial form case"][g] += 1
                if key not in positive:
                    continue
                verified.add(key)
                tally["confirmed"][g] += 1
                size_events[(p["s"],p["meet"],p["after"]["form"],len(p["Y"]),g)] += 1
                examples[key] = (p["s"], p["meet"], p["after"]["form"], g)
    if limit is None:
        assert positive == verified
    exposed = []
    for (law, f), tally in sorted(by_form.items()):
        if tally["confirmed"]:
            exposed.append(dict(law=law, first_form=f, **tally))
    each_stage = {}
    for stage in STAGES:
        each_stage[stage] = {
            "law and first form with any": sum(bool(t[stage]) for t in by_form.values()),
            "law and first form with at least two distinct partners": sum(len(t[stage]) >= 2 for t in by_form.values()),
            "among the positive groups with at least two distinct partners": sum(len(t[stage]) >= 2 for t in exposed),
            "total unique ordered pairs at this stage": sum(sum(t[stage].values()) for t in by_form.values()),
        }
    for t in exposed:
        positive_g = set(t["confirmed"])
        t["other forms by stage"] = {stage: len(set(t[stage]) - positive_g) for stage in STAGES}
    r9 = Counter()
    for row in rows("R9",limit):
        r9["rows"] += 1
        if "error" in row:
            r9["unread"] += 1
            continue
        early = {f["knot"]: f for f in row["every_round_fails"]}
        late = set(row["last_round_fails"])
        r9["birth classifications"] += len(early)
        r9["failed growths"] += bool(early)
        r9["verdicts"] += row["verdicts"]
        r9["method disagreements"] += row["disagree"]
        r9["only one of every-round and last-round"] += len(set(early) ^ late)
        r9["first failed after birth"] += sum(f["made"] != f["first_failing_round"] for f in early.values())
        r9["failures of joins"] += sum(f["kind"] == "join" for f in early.values())
        r9["growths using the reduced check"] += bool(row["reduced_rounds"])
    return {"unit": "Distinct ordered pairs at one read round in the named-law, take-by-take, readable growths with no failing knot. Second form differs from first. Repeat appearances in the all-pairs reading counted once. A form key is the stored invariant and hash. The confirmed targets have only one or two members.",
            "rows_scanned": counts, "opportunities_by_stage": each_stage,
            "positive_law_and_first_form_groups": exposed,
            "positive_read_meeting_output_rounds_and_second_forms": [list(k)+[v] for k,v in sorted(size_events.items())],
            "every_round_vs_last_round": r9}

if __name__ == "__main__":
    test = "--pilot" in sys.argv
    t = time.monotonic()
    result = opportunities(50 if test else None)
    if test:
        print("50 rows per file", round(time.monotonic()-t,3), "seconds")
    else:
        (HERE / "c_opportunities.json").write_text(json.dumps(result,indent=2) + "\n")
        print(json.dumps(result["opportunities_by_stage"],indent=2))
