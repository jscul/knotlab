"""Rebuild every recorded tower row and recount opportunities under both readings."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
from random import Random

import growth
from exchange import renaming
from tower_readings import readings


STUDY = Path(__file__).resolve().parents[1]
LAYERS = STUDY.parent / "LAYERS-20261126-001"
ROUND_LIMIT = 3
DISTINCTION_LIMIT = 400
READINGS = ("SHORT", "UPTO5")


def json_lines(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream]


def source_rosters():
    census = growth.census()
    heldout = growth.heldout()
    draw = sorted(Random(20261208).sample(range(len(census)), 400))
    census_multi = [row["index"] for row in json_lines(LAYERS / "frozen_census.jsonl")
                    if row.get("classes", 0) >= 4]
    heldout_multi = [tuple(map(int, row["index"].split("-")))
                     for row in json_lines(LAYERS / "frozen_heldout.jsonl")
                     if row.get("classes", 0) >= 4]
    extra_sources = []
    canonical = STUDY.parent / "TWO-CLASS-SIGN-20261126-001" / "census_canonical.jsonl.gz"
    with gzip.open(canonical, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            index = int(row["structure"].split()[-1])
            source = row.get("start")
            if isinstance(source, dict) and source["loose free"]["classes"] >= 4 and index not in census_multi:
                extra_sources.append(index)
    multi = {f"census {i} (after one round)": census[i] for i in census_multi}
    multi.update({f"census {i} (start)": census[i] for i in extra_sources})
    multi.update({f"held out {n}-{i}": heldout[n, i] for n, i in heldout_multi})
    rosters = {"census": {f"census {i}": census[i] for i in draw}, "multi": multi, "rings": growth.joined()}
    details = {
        "census draws": draw,
        "census multiclass after a grown round": census_multi,
        "additional census multiclass sources": extra_sources,
        "held-out multiclass after a grown round": heldout_multi,
        "census indices appearing in both the draw and the multiclass roster": sorted(
            set(draw) & (set(census_multi) | set(extra_sources))
        ),
        "built roster": list(rosters["rings"]),
    }
    literal_cases = {f"census {i} (after one round)" for i in census_multi}
    literal_cases.update(f"held out {n}-{i}" for n, i in heldout_multi)
    return rosters, details, literal_cases


def size(stage):
    return len(set().union(*stage))


def digest(stage):
    return hashlib.sha256(json.dumps([sorted(knot) for knot in stage]).encode()).hexdigest()


def source_aliases(rosters):
    buckets = defaultdict(list)
    duplicates = {}
    for group, roster in rosters.items():
        for case, stage in roster.items():
            name = f"{group} / {case}"
            holders = Counter(distinction for knot in stage for distinction in knot)
            signature = tuple(sorted((len(knot), sum(holders[d] == 1 for d in knot)) for knot in stage))
            for previous, previous_stage in buckets[signature]:
                if renaming(stage, previous_stage) is not None:
                    duplicates[name] = previous
                    break
            else:
                buckets[signature].append((name, stage))
    return duplicates


def replay(start, literal_first=False, report_individual=True):
    rounds = []
    details = []
    stage = start
    for number in range(1, ROUND_LIMIT + 1):
        stage, status, _ = growth.advance(stage)
        if status != "funded":
            rounds.append({"round": number, "end": status})
            break
        count = size(stage)
        if count > DISTINCTION_LIMIT:
            rounds.append({"round": number, "end": f"not read: {count} distinctions"})
            break
        data, extra = readings(stage, literal=number == 1 and literal_first, report_individual=report_individual)
        rounds.append({"round": number, **data})
        details.append({"round": number, "knots": len(stage), "distinctions": count, **extra})
    return rounds, details


def prior_controls():
    folder = LAYERS / "referee-R1"
    joint = json.loads((folder / "joint_check.json").read_text())
    two_rings = json.loads((folder / "moves_certificates.json").read_text())
    controls = {
        "two four-knot rings with single meetings to the ninth knot": joint["source"]["supports"],
        "two four-knot rings with double meetings to the ninth knot": two_rings["joining_two_four_knot_rings"]["source"],
        "two five-knot rings joined by one shared distinction and with reduced loose supply":
            two_rings["joining_two_five_knot_rings"]["source"],
    }
    out = {}
    for name, supports in controls.items():
        source = tuple(map(frozenset, supports))
        first, first_extra = readings(source)
        rounds, details = replay(source)
        out[name] = {
            "source": {"knots": len(source), "distinctions": size(source), **first},
            "source diagnostics": first_extra,
            "grown rounds": rounds,
            "diagnostics": details,
        }
    return out


def parallel_control():
    source = (frozenset({0, 1, 2, 3, 4}), frozenset({0, 1, 2, 3, 5}))
    profile, details = readings(source, literal=True)
    expected = {"allowed assignments": 16, "bounded nonzero changes": 15,
                "bounded changes outside the simple generators": 5}
    if details["literal"] != expected or details["maximum shortest ties through one distinction"] != 4:
        raise AssertionError("the four parallel shared distinctions give a different count")
    return {"supports": [sorted(knot) for knot in source], "profile": profile, **details}


def counts_for_round(records, number):
    statuses = Counter()
    class_counts = {key: Counter() for key in READINGS}
    whole_counts = {key: Counter() for key in READINGS}
    opportunities = {key: [] for key in (*READINGS, "both")}
    presence = Counter()
    unreadable = {key: {} for key in READINGS}
    changed_class_rank = Counter()
    for name, (rounds, extras) in records.items():
        if number > len(rounds):
            statuses["not reached"] += 1
            continue
        row = rounds[number - 1]
        if "end" in row:
            statuses[row["end"].split(":")[0]] += 1
            continue
        statuses["read"] += 1
        for key in READINGS:
            class_counts[key][row[key]["classes"]] += 1
            whole_counts[key][row[key]["whole-held"]] += 1
            if row[key]["classes"] >= 4:
                opportunities[key].append(name)
            diagnostic = extras[number - 1][key]
            if diagnostic.get("individually unreadable rank", 0) >= 2:
                unreadable[key][name] = {
                    **row[key],
                    "individually unreadable rank": diagnostic["individually unreadable rank"],
                    "individually unreadable labels": diagnostic["individually unreadable labels"],
                }
        if all(row[key]["classes"] >= 4 for key in READINGS):
            opportunities["both"].append(name)
        pair = tuple(int(row[key]["whole-held"] > 0) for key in READINGS)
        presence[f"{pair[0]} / {pair[1]}"] += 1
        delta = row["UPTO5"]["labels"] - row["SHORT"]["labels"]
        trend = "higher" if delta > 0 else "lower" if delta < 0 else "equal"
        changed_class_rank[trend] += 1
    return {
        "status": dict(statuses),
        "class counts": {key: dict(value) for key, value in class_counts.items()},
        "whole-held counts": {key: dict(value) for key, value in whole_counts.items()},
        "opportunities for two whole-held labels": {
            key: {"count": len(value), "starts": value} for key, value in opportunities.items()
        },
        "presence of a whole-held label, SHORT / UPTO5": dict(presence),
        "UPTO5 label rank relative to SHORT": dict(changed_class_rank),
        "two independent individually unreadable labels": unreadable,
    }


def score_tally(group, records):
    tally = Counter()
    for rounds, _ in records.values():
        for row in rounds:
            prefix = f"{group} / round {row['round']} / "
            if "end" in row:
                tally[prefix + row["end"].split(":")[0]] += 1
                continue
            for key in READINGS:
                tally[f"{prefix}{key} / whole-held {row[key]['whole-held']}"] += 1
    return tally


def run(pilot):
    rosters, selection, literal_cases = source_rosters()
    out = {"pilot": pilot, "selection": selection, "groups": {}, "archive differences": []}
    observed = {}
    checked_rosters = {}
    all_tally = Counter()
    maximum_ties = 0
    all_literals = []
    for name, roster in rosters.items():
        archive = json_lines(STUDY / f"tower_{name}.jsonl")
        raw_names = [row["start"] for row in archive]
        if list(roster) != raw_names:
            out["archive differences"].append({
                "group": name, "expected names": list(roster), "archived names": raw_names,
            })
        by_name = {row["start"]: row for row in archive}
        if pilot:
            picks = {
                "census": ("census 0",),
                "multi": ("held out 7-239",),
                "rings": ("one ring of 7", "two rings of 5 sharing a knot"),
            }[name]
            roster = {case: roster[case] for case in picks}
        checked_rosters[name] = roster
        records = {}
        source_data = {}
        for case, source in roster.items():
            rounds, details = replay(source, literal_first=case in literal_cases)
            independent = {"start": case, "knots": len(source), "rounds": rounds}
            if independent != by_name.get(case):
                out["archive differences"].append({"group": name, "made": independent, "recorded": by_name.get(case)})
            records[case] = rounds, details
            for row in details:
                maximum_ties = max(maximum_ties, row["maximum shortest ties through one distinction"])
                if "literal" in row:
                    all_literals.append({"case": case, **row["literal"]})
            if name == "multi":
                before, _ = readings(source)
                source_data[case] = {"source digest": digest(source), "classes at round zero": {
                    key: before[key]["classes"] for key in READINGS
                }}
        observed[name] = records
        group = {
            "rows": len(roster),
            "source roster digest": digest(tuple(knot for source in roster.values() for knot in source)),
            "rounds": {number: counts_for_round(records, number) for number in range(1, ROUND_LIMIT + 1)},
            "ends": {case: rounds[-1] for case, (rounds, _) in records.items() if "end" in rounds[-1]},
        }
        if source_data:
            group["source diagnostics"] = source_data
            group["frozen 16 by round"] = {
                number: counts_for_round({case: records[case] for case in records if case in literal_cases}, number)
                for number in range(1, ROUND_LIMIT + 1)
            }
        if name == "rings":
            group["built profiles"] = {case: rounds for case, (rounds, _) in records.items()}
        out["groups"][name] = group
        all_tally.update(score_tally(name, records))
    if not pilot:
        score = json.loads((STUDY / "score.json").read_text())
        out["matches published score table"] = all_tally == score["tower"]
    combined = {f"{name} / {case}": report for name, records in observed.items() for case, report in records.items()}
    duplicates = source_aliases(checked_rosters)
    unique = {name: report for name, report in combined.items() if name not in duplicates}
    for duplicate, original in duplicates.items():
        if combined[duplicate][0] != combined[original][0]:
            out["archive differences"].append({
                "renamed source": [duplicate, original],
                "different round results": [combined[duplicate][0], combined[original][0]],
            })
    out["starts up to renaming"] = {"count": len(unique), "aliases": duplicates}
    out["all sample rows by round"] = {number: counts_for_round(combined, number)
                                        for number in range(1, ROUND_LIMIT + 1)}
    out["all starts up to renaming by round"] = {number: counts_for_round(unique, number)
                                                 for number in range(1, ROUND_LIMIT + 1)}
    out["maximum shortest ties through one distinction across archive"] = maximum_ties
    out["literal controls on the selected grown multiclass preparations"] = {
        "preparations": len(all_literals),
        "allowed assignments": sum(row["allowed assignments"] for row in all_literals),
        "preparations with bounded changes outside the simple generators": sum(
            row["bounded changes outside the simple generators"] > 0 for row in all_literals
        ),
        "details": all_literals,
    }
    out["parallel shared distinction control"] = parallel_control()
    out["earlier referee witness controls"] = prior_controls()
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.pilot)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({"rows": sum(group["rows"] for group in result["groups"].values()),
           "archive differences": len(result["archive differences"]),
           "matches published score table": result.get("matches published score table")})
    return bool(result["archive differences"] or result.get("matches published score table") is False)


if __name__ == "__main__":
    raise SystemExit(main())
