"""Count ticket A's saved observations without importing its readers."""

import argparse
import ast
from collections import Counter
import gzip
from itertools import combinations, islice
import json
from pathlib import Path


TICKET = "MADE-COPIER-20261125-001A"
ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_made_copier"
REGISTERED = ROOT / "research" / TICKET
MADE = [f"made-{size}" for size in range(3, 7)]
START = [f"ystart-{kind}" for kind in ("one-2", "one-3", "two-23", "two-33", "three-222")]


def load(name, limit=None):
    path = DATA / name
    if path.suffix == ".json":
        with path.open() as source:
            return json.load(source)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as source:
        return [json.loads(line) for line in islice(source, limit)]


def direct_counts(run_rows):
    counts = Counter()
    course = Counter()
    take_and_course = Counter()
    found = {"values": [], "form": [], "built": [], "Y only values": [], "Y returns": [], "Y returns with X barred": []}
    stopped = Counter()
    capacities = Counter()
    tests = Counter()
    replacements = Counter()
    census = Counter()
    confirmed_families = Counter()
    for row in run_rows:
        job = row["job"]
        law = row["law"]
        knot_law = job["knot_law"]
        for name, run in row["designs"].items():
            if "per_round" not in run:
                counts["missing runs"] += 1
                continue
            family = "made" if name.startswith("made-") else "present at round 0"
            control = name not in MADE + START
            assert len(run["per_round"]) == run["rounds"] - (1 if family == "made" else 0)
            counts["all"] += 1
            counts[knot_law] += 1
            tests[knot_law] += run["knot_tests_A"]["verdicts"]
            tests[f"{knot_law} failing"] += run["knot_tests_A"]["n_fails"]
            tests[f"{knot_law} method disagreements"] += run["knot_tests_A"]["n_disagree"]
            for entries in run["knot_tests_cmp"].values():
                tests[knot_law] += entries["verdicts"]
                tests[f"{knot_law} failing"] += entries["n_fails"]
                tests[f"{knot_law} method disagreements"] += entries["n_disagree"]
            stopped[f"run A through round {run['rounds']}"] += 1
            stopped[f"owner's comparisons through round {run['T']}"] += 1
            capacities["runs with an eligible place of Y"] += bool(run["eligible_Y"])
            capacities["runs with at least one part of Y's form containing a made member"] += any(
                step["form"]["n"] for step in run["per_round"]
            )
            capacities["runs reaching round 6"] += run["rounds"] == 6
            if job["take"] == "MET" and job["base"].startswith(("COPY-LAW", "CAP-3")) and not control and knot_law == "parity":
                capacities["formal values runs"] += 1
            if job["take"] == "MET" and job["base"].startswith(("FBP", "CAP-3")) and name in MADE + [START[0], START[1], START[-1]]:
                capacities["formal form runs in the retained classes"] += 1
            for step in run["per_round"]:
                for case in step["values_Y"]:
                    if case["made_by_X"]:
                        found["values"].append({"design": name, "law": law, "t": step["t"], "case": case})
                if step["form"]["by_descent"].get("X only", 0) >= 2:
                    found["form"].append({"design": name, "law": law, "t": step["t"], "meeting": run["meeting_round"],
                                          "comparison": run["B(i)"]["form"], "X alone": run.get("X_alone")})
                if step["built_n"] or step["built_bound"]:
                    found["built"].append({"design": name, "law": law, "t": step["t"], "n": step["built_n"], "bound": step["built_bound"]})
                if knot_law == "nae":
                    counts["not-all-equal rounds checked"] += 1
                    counts["not-all-equal rounds with made ties"] += bool(step["made_tied"])
            if any(case["by_Y_only"] for case in run["values"]["cases"]):
                found["Y only values"].append((name, law, run["B_X"]["values"]["Y_own_some"]))
            if run["form"]["Y_returning_some"]:
                found["Y returns"].append((name, law))
            if run["B_X"]["form"]["Y_returning_some"]:
                found["Y returns with X barred"].append((name, law))
            if job["base"].startswith(("CAP-3", "FBP")) and name != "made-2-exchanged":
                for target, sequence in run["parts_same_as_member"].items():
                    if name.startswith("made-") != target.startswith("made-"):
                        continue
                    census[f"{knot_law}, {target}, runs read"] += 1
                    census[f"{knot_law}, {target}, any descent"] += any(map(bool, sequence))
                    census[f"{knot_law}, {target}, X only"] += any(step.get("X only", 0) for step in sequence)
            for role in ("X", "Y"):
                reading = run[f"{role}_course"]
                if reading["differs"] is not None:
                    course[f"{role}, differs"] += 1
                if reading.get("confirmed") == "through a meeting":
                    course[f"{role}, through a meeting"] += 1
                    take_and_course[f"{role}, {run[f'takes_vs_{role}_course']}"] += 1
                    confirmed_families[f"{role}, {name}, {job['base']}"] += 1
            for reading in ("reading_ii", "reading_ii_reverse"):
                if run[reading]["holds"]:
                    course[reading] += 1
                    course[f"{reading}: through a meeting"] += run[reading]["through a meeting"]
            for reading in ("reading_iii", "reading_iii_reverse"):
                course[reading] += run.get(reading, False)
            counts["PO1 relation projection differences"] += any(
                step["at_t"] != step["at_last"] for step in run["PO1"]["rows"]
            )
            counts["PO1 loose distinctions taken without an X parent"] += run["PO1"]["loose_taken_by_other"]
            if knot_law == "nae":
                counts["PO1 not-all-equal runs with truncated projections"] += any(
                    step["cut_to_12"] for step in run["PO1"]["rows"]
                )
        for family, names in (("made", MADE), ("present at round 0", START)):
            for left, right in combinations(names, 2):
                first, second = row["designs"][left], row["designs"][right]
                if "rounds" not in first or "rounds" not in second:
                    continue
                pair = "|".join(sorted((left, right)))
                replacements[f"{family} pairs"] += 1
                replacements[f"{family}, trace difference"] += row["fourth_mark"][pair] is not None
                common = min(first["rounds"], second["rounds"]) - (family == "made")
                targets = [name for name in names if name in first["parts_same_as_member"] and name in second["parts_same_as_member"]]
                replacements[f"{family}, parts by descent difference"] += any(
                    first["parts_same_as_member"][name][:common] != second["parts_same_as_member"][name][:common]
                    for name in targets
                )
    return {"counts": counts, "exposure": capacities, "stops": stopped, "positive readings": found, "course": course,
            "takes and course": take_and_course, "through a meeting by design and base law": confirmed_families,
            "knot verdicts": tests, "replacements": replacements, "form census": census}


def renaming_counts(swap_rows, form_rows, numberings):
    case_results = []
    for row in swap_rows:
        case = row["case"]
        case_results.append({"case": case, "original repeats": row["as run"]["survives"],
                             "renamings": {kind: read["survives"] for kind, read in row["swaps"].items()
                                           if kind.startswith("renaming ")},
                             "other surviving swaps": [kind for kind, read in row["swaps"].items()
                                                      if not kind.startswith("renaming ") and read["survives"]]})
    keys = {}
    for row in form_rows:
        job = row["job"]
        key = tuple(job[field] for field in ("base", "take", "choice", "knot_law", "swap"))
        keys[key] = row
    form = Counter()
    for row in keys.values():
        swap = row["job"]["swap"]
        for name, result in row.get("designs", {}).items():
            if "form" not in result:
                form[f"{swap}, unread"] += 1
                continue
            form[f"{swap}, runs"] += 1
            form[f"{swap}, guard"] += bool(result.get("guard"))
            if result["form"]["two_by_X_some"]:
                form[f"{swap}, two for {name}"] += 1
    wider = [
        {"case": row["case"], "count": len(row["numberings"]),
         "passes by first round": Counter(r["round"] for r in row["numberings"] if r["passes"])}
        for row in numberings["rows"]
    ]
    return {"case swaps": case_results, "form arm checks": form, "post-freeze numbering checks": wider,
            "form arm rows": len(form_rows), "form arm unique settings": len(keys)}


def drawn_counts(history_rows, saved_failures, replay, take_lists):
    counts = Counter()
    by_design = {}
    symmetry = []
    for row in history_rows:
        record = row["counts"]
        counts["histories"] += record["histories"]
        counts[f"histories, {row['knot_law']}"] += record["histories"]
        for key, value in record.items():
            if "with two" in key or "passing" in key or "guard" in key:
                counts[key] += value
        if row["base"] == "COPY-LAW(OFFSHOOT)" and row["knot_law"] == "parity":
            by_design[row["design"]] = record
        if row["design"] == "made-2":
            states = {ast.literal_eval(k): v for k, v in row["states_made2"].items()}
            symmetry.append({"knot law": row["knot_law"], "base law": row["base"], "mode": row["mode"],
                             "histories": sum(states.values()), "symmetric": all(
                                 value == states.get((pair[1], pair[0]), 0) for pair, value in states.items())})
    expected = take_lists if isinstance(take_lists, list) else next(x for x in take_lists.values() if isinstance(x, list))
    assert len(expected) == len(replay["rows"])
    return {"all aggregate counts": counts, "copy ration with offshoots and parity by design": by_design,
            "replayed take-list records": len(replay["rows"]),
            "saved positive lists passing": sum(row["every knot passes"] and row["gives the two"] for row in replay["rows"]),
            "saved draw knot test counts": sum((Counter(row["counts"]) for row in saved_failures["rows"]), Counter()),
            "made-2 symmetry": symmetry}


def owner_extra(edge_rows, third_rows):
    changes = Counter()
    for row in edge_rows:
        ration = row["base"].split("(")[0]
        changes[f"{ration}, all runs"] += 1
        changes[f"{ration}, read"] += row["read"]
        changes[f"{ration}, relation changes"] += bool(row.get("change"))
        if row.get("by births descended from Y only"):
            changes[f"{ration}, Y only"] += 1
            changes[f"{ration}, Y only with a failing knot"] += row["knot test at the round of the change"]["n_fails"] > 0
            changes[f"Y only, {row['design']}, {row['knot_law']}, {row['take']}"] += 1
    third = Counter()
    for row in third_rows:
        for result in row["rows"]:
            kind = row["job"]["kind"]
            third[f"{kind}, trials"] += 1
            if "(iv) holds" not in result:
                third[f"{kind}, list does not apply"] += 1
                third[f"{kind}, inaccessible result but Z barred two of Y"] += bool(result["Z barred"]["two of Y at"])
                continue
            third[f"{kind}, reading (iv) holds"] += result["(iv) holds"]
            third[f"{kind}, (b) with Z barred two of Y"] += result["(b) with Z barred, two of Y"]
    return {"weaker rations": changes, "third pattern": third}


def other_runs(run_one, run_three, more_nae):
    counts = Counter()
    control_counts = json.loads((REGISTERED / "starts.json").read_text())["counts for P3"]["counts"]
    for row in run_one:
        counts["run 1"] += 1
        if row["take"] in ("MET", "STEPS-1", "STEPS-2") and row["base"].startswith("COPY-LAW"):
            counts["P1 runs"] += 1
            counts["P1 other fresh counts"] += len(row["fresh_bad"])
        if row["take"] in ("Q", "MET", "STEPS-1", "STEPS-2") and not row["base"].startswith("FBP"):
            counts["P3 runs with a taking rule"] += 1
            counts["P3 such runs with a part after round 2"] += any(row["N"][3:])
        if row["take"] in ("", "none", "NONE", None, "base"):
            family, treatment = row["base"].rstrip(")").split("(")
            if family in ("COPY-LAW", "CAP-3"):
                ration = {"COPY-LAW": "FLOOR1", "CAP-3": "CAP3"}[family]
                counts[f"P3 no take {row['knot_law']}"] += 1
                counts[f"P3 no take mismatches {row['knot_law']}"] += row["N"] != control_counts[f"{row['start']}|{ration}-{treatment}"]
        for test in ("n_fails", "n_disagree", "verdicts"):
            counts[f"run 1 {row['knot_law']} {test}"] += row["knot_tests"][test]
        if row["knot_law"] == "nae":
            counts["run 1 not-all-equal tie classes with made distinctions"] += row["ties_made"]["n_classes_with_made"]
    for row in run_three:
        counts["run 3"] += 1
        for test in ("n_fails", "n_disagree", "verdicts"):
            counts[f"run 3 {row['job']['knot_law']} {test}"] += row["knot_tests_A"][test]
        for pair in row.get("pairs", []):
            counts["run 3 pairs"] += 1
            counts["run 3 pairs with an eligible place of Y"] += bool(pair["eligible_Y"])
            counts["run 3 pair values cases"] += bool(pair["values"]["Y_by_X_some"])
            counts["run 3 pair form cases"] += bool(pair["form"]["two_by_X_some"])
            counts["run 3 pair built matches"] += bool(pair["built"]["any_renaming_some"])
            counts["run 3 PO1 disagreements"] += not pair["PO1"]["same"]
            if row["job"]["knot_law"] == "nae":
                counts["run 3 recorded rounds with a made tie under not-all-equal"] += sum(
                    step["made_tied"] > 0 for step in pair["per_round"]
                )
            for entry in pair["knot_tests_cmp"].values():
                for test in ("n_fails", "n_disagree", "verdicts"):
                    counts[f"run 3 {row['job']['knot_law']} {test}"] += entry[test]
    for row in more_nae:
        runs = row["rows"].values() if isinstance(row["rows"], dict) else row["rows"]
        for run in runs:
            for result in run.values():
                if isinstance(result, dict) and "classes" in result:
                    counts[f"run 6 readings from run {row['run']}"] += 1
                    counts[f"run 6 unsatisfiable from run {row['run']}"] += result["unsat"]
                    counts[f"run 6 ties from run {row['run']}"] += result["n"]
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="read a timed prefix of each JSONL file")
    args = parser.parse_args()
    limit = args.limit
    result = {
        "prefix per JSONL file": limit,
        "stated rules": direct_counts(load("run2.jsonl.gz", limit)),
        "renamings": renaming_counts(load("run5_cases.jsonl", limit), load("run5_form.jsonl.gz", limit),
                                    load("run7_numberings.json")),
        "every-choice counts retained by the study": drawn_counts(
            load("run4.jsonl", limit), load("run4_fails.json"), load("run4_replay.json"),
            json.loads((REGISTERED / "take_lists.json").read_text())),
        "other runs": other_runs(load("run1.jsonl.gz", limit), load("run3.jsonl.gz", limit),
                                 load("run6.jsonl.gz", limit)),
        "owner's arm": owner_extra(load("runO.jsonl.gz", limit), load("run5_iv.jsonl", limit)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
