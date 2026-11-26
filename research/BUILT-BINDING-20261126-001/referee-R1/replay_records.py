"""Recount the premise, origin and closing archives and replay their growth."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from replay_growth import CENSUS, grow, items, read_census, verify_census
from replay_span import new_span, origin_check


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent
ROSTERS = ("census", "heldout", "built", "sampled", "small built")
READINGS = ("SHORT", "UPTO5")
FROZEN_SPAN_SIZE = 400
GROWTH_SIZE = 20_000
READ_FIELDS = ("dim Z_new", "rank of pairs and loops of four", "inside Z_new")


def read_archive(filename):
    path = ARCHIVE / filename
    data = path.read_bytes()
    rows = [json.loads(line) for line in data.splitlines()]
    by_start = {row["start"]: row for row in rows[:-1]}
    assert len(by_start) == len(rows) - 1
    return by_start, rows[-1], sha256(data).hexdigest()


def archive_premises(rows):
    breaks = Counter()
    stages = Counter()
    spans = Counter()
    ends = Counter()
    first_ends = Counter()
    by_round = defaultdict(Counter)
    for start in rows.values():
        for row in start["rounds"]:
            if "end" in row:
                ends[row["end"]] += 1
                if row["round"] == 1:
                    first_ends[row["end"]] += 1
                continue
            detail = by_round[row["round"]]
            stages["funded rounds"] += 1
            detail["funded rounds"] += 1
            breaks.update(row["premises broken"])
            if row["premises broken"]:
                stages["distinct rounds with a broken premise"] += 1
                detail["distinct rounds with a broken premise"] += 1
            if "span" in row:
                span = row["span"]
                spans["checks"] += 1
                detail["span checks"] += 1
                if span["dim Z_new"] == span["rank of pairs and loops of four"] and span["inside Z_new"]:
                    spans["equal and inside"] += 1
                if span["dim Z_new"]:
                    spans["positive dimension"] += 1
            else:
                spans["not run above span cap"] += 1
                detail["span not run above cap"] += 1
    summary = {
        "premises": {"rounds read": stages["funded rounds"], **breaks},
        "span": {"stages": spans["checks"], "equal": spans["equal and inside"]},
    }
    return summary, {
        "starts": len(rows), "premise rounds": stages, "premise failures by reason": breaks,
        "span": spans, "all ends": ends, "first-round ends": first_ends, "by round": by_round,
    }


def archive_origin(rows):
    ends = Counter()
    checks = Counter()
    by_round = defaultdict(Counter)
    for start in rows.values():
        for row in start["rounds"]:
            if "end" in row:
                ends[row["end"]] += 1
                continue
            checks["stages read"] += 1
            by_round[row["round"]]["stages read"] += 1
            if row["dim Z_new"]:
                checks["positive dimension"] += 1
                by_round[row["round"]]["positive dimension"] += 1
            for method in READINGS:
                checks[f"{method} failures"] += not row[method]
    summary = {
        "stages read": checks["stages read"],
        "stages where some class fact depends on values the start does not fix": {
            method: checks[f"{method} failures"] for method in READINGS
        },
    }
    return summary, {"starts": len(rows), "checks": checks, "ends": ends, "by round": by_round}


def closing_stats(rows):
    tallies = Counter()
    ends = Counter()
    by_round = defaultdict(Counter)
    for start in rows:
        law = start["law"]
        for birth in start["births"]:
            if "end" in birth:
                ends[birth["end"]] += 1
                continue
            by_round[birth["round"]]["births"] += 1
            if birth["takes all"]:
                by_round[birth["round"]]["takes all"] += 1
            if birth["implied"]:
                by_round[birth["round"]]["implied"] += 1
            if not birth["f"]:
                by_round[birth["round"]]["zero fresh"] += 1
            key = (
                law, "implied" if birth["implied"] else "not implied",
                "takes every loose distinction of its structure" if birth["takes all"] else "leaves some",
                "fresh 0" if birth["f"] == 0 else "fresh > 0",
            )
            tallies[key] += 1
    return {"tally": [[list(key), value] for key, value in sorted(tallies.items())]}, {
        "births": sum(tallies.values()), "ends": ends, "by round": by_round,
    }


def read_section(filename, section):
    rows, footer, checksum = read_archive(filename)
    if section == "premises":
        summary, stats = archive_premises(rows)
    elif section == "origin":
        summary, stats = archive_origin(rows)
    else:
        summary, stats = closing_stats(rows.values())
        stats["starts"] = len(rows)
    assert footer == summary, (filename, footer, summary)
    return rows, {"file": filename, "sha256": checksum, "footer matches rows": True, **stats}


def choose_pilot(starts, archives):
    """Include both endpoint rows and a funded row for each supplied start size."""
    hold = {starts[0][0], starts[-1][0]}
    chosen = {}
    for name, start in starts:
        section = archives.get("premises", {}).get(name, {}).get("rounds", [])
        if not section:
            section = archives.get("closing", {}).get(name, {}).get("births", [])
        if section and "end" not in section[0]:
            chosen.setdefault(len(start), name)
        if len(starts) == 32 and "4 rings of 6" in name:
            hold.add(name)
    hold.update(chosen.values())
    return [(key, state) for key, state in starts if key in hold]


def compare_rows(comparisons, part, name, expected, actual):
    result = comparisons[part]
    result["trajectories compared"] += 1
    result["archived records compared"] += len(expected)
    result["replayed records compared"] += len(actual)
    if expected == actual:
        result["matched trajectories"] += 1
    else:
        result["mismatched trajectories"] += 1
        if "examples" not in result:
            result["examples"] = []
        if len(result["examples"]) < 3:
            first = next(i for i in range(max(len(expected), len(actual)))
                         if expected[i:i+1] != actual[i:i+1])
            result["examples"].append({
                "start": name, "position": first,
                "archived": expected[first:first+1], "replayed": actual[first:first+1],
            })


def replay(starts, law, arm, archives, pilot):
    if pilot:
        starts = choose_pilot(starts, archives)
    for part in archives:
        assert {name for name, _ in starts} <= archives[part].keys()
        if not pilot:
            assert len(starts) == len(archives[part])
    rounds = 6 if "premises" in archives else 3
    totals = Counter()
    by_round = defaultdict(Counter)
    first_ends = Counter()
    all_ends = Counter()
    zeros = Counter()
    checks = {part: Counter() for part in archives}
    origin_dimensions = {method: Counter() for method in READINGS}
    literal = []
    beyond = []
    closure_rows = []
    size_groups = defaultdict(Counter)
    for name, start in starts:
        size_groups[len(start)]["starts"] += 1
        old = {name for knot in start for name in knot}
        age = [0] * len(start)
        previous = start
        rec = {part: [] for part in checks}
        active_origin = "origin" in archives
        if any(len(knot) > 3 for knot in start):
            totals["starts with a knot of more than three places"] += 1
        for round_no in range(1, rounds + 1):
            status, stage, births, bad = grow(previous, law, arm)
            if status != "funded":
                all_ends[status] += 1
                if round_no == 1:
                    first_ends[status] += 1
                    size_groups[len(start)][f"first-round {status}"] += 1
                end = {"round": round_no, "end": status}
                if "premises" in rec:
                    rec["premises"].append(end)
                if "closing" in rec and round_no <= 3:
                    rec["closing"].append(end)
                if active_origin and round_no <= 3:
                    rec["origin"].append(end)
                break
            distinct = len({name for knot in stage for name in knot})
            before = len(age)
            age.extend([round_no] * len(births))
            assert len(stage) == len(age) == before + len(births)
            totals["funded rounds"] += 1
            totals["funded births"] += len(births)
            size_groups[len(start)]["funded rounds"] += 1
            size_groups[len(start)]["funded births"] += len(births)
            totals["maximum distinctions"] = max(totals["maximum distinctions"], distinct)
            stats = by_round[round_no]
            stats["funded rounds"] += 1
            stats["funded births"] += len(births)
            if bad:
                stats["distinct rounds with a broken premise"] += 1
                totals["distinct rounds with a broken premise"] += 1
            for birth in births:
                if not birth.fresh:
                    tag = "implied" if birth.implied else "adds an equation"
                    zeros[tag] += 1
                    zeros[f"{tag}, {len(birth.parents)} inputs"] += 1
                if law == "parity" and birth.implied != birth.takes_all:
                    totals["parity closing criterion failures"] += 1

            if "premises" in rec:
                row = {"round": round_no, "premises broken": bad}
                span = new_span(stage, old, age)
                dim = span["dim Z_new"]
                ok = dim == span["rank of pairs and loops of four"] and span["inside Z_new"]
                all_ok = (dim == span["rank of all pairs and four-distinction changes"]
                          and span["inside Z_new"])
                stats["positive new-only dimension"] += bool(dim)
                stats["chronological span equal and inside"] += ok
                stats["any two or four span equal and inside"] += all_ok
                stats["generators verified shortest in full stage"] += span["shortest in the full stage"]
                if distinct > FROZEN_SPAN_SIZE:
                    if not ok or not all_ok or not span["shortest in the full stage"]:
                        totals["additional span failures"] += 1
                    beyond.append({"start": name, "round": round_no, "distinctions": distinct, **span})
                else:
                    row["span"] = {key: span[key] for key in READ_FIELDS}
                    stats["within archived span cap"] += 1
                    stats["positive new-only dimension within archived span cap"] += bool(dim)
                rec["premises"].append(row)

            if active_origin and round_no <= 3:
                if distinct > FROZEN_SPAN_SIZE:
                    rec["origin"].append({"round": round_no, "end": "not read"})
                    active_origin = False
                else:
                    literal_here = len(literal) < 4 and distinct <= 13
                    origin = origin_check(stage, old, literal_here)
                    if literal_here:
                        literal.append({"start": name, "round": round_no, "distinctions": distinct})
                    dimensions = origin.pop("class dimension")
                    for method, dim in dimensions.items():
                        origin_dimensions[method][dim] += 1
                        stats[f"{method}: origin stages with class facts"] += bool(dim)
                        stats[f"{method}: origin stages with class facts and positive new-only dimension"] += (
                            bool(dim) and bool(origin["dim Z_new"])
                        )
                    rec["origin"].append({"round": round_no, **origin})

            if "closing" in rec and round_no <= 3:
                for birth in births:
                    rec["closing"].append({
                        "round": round_no, "parents": list(birth.parents), "p": len(birth.inputs),
                        "f": len(birth.fresh), "implied": birth.implied, "takes all": birth.takes_all,
                    })

            previous = stage
            if distinct > GROWTH_SIZE:
                totals["growth size stops"] += 1
                rec["premises"].append({"round": round_no, "end": "size cap"})
                break

        for part, source in archives.items():
            field = "births" if part == "closing" else "rounds"
            compare_rows(checks, part, name, source[name][field], rec[part])
        if "closing" in rec:
            closure_rows.append({"law": law, "births": rec["closing"]})

    return {
        "starts": len(starts), "labelled distinct starts": len({start for _, start in starts}),
        "overall": totals, "by start size": size_groups, "by round": by_round,
        "first-round ends": first_ends, "all ends": all_ends, "zero-fresh births": zeros,
        "origin class dimensions": origin_dimensions if "origin" in checks else {},
        "literal origin checks": literal, "stages beyond the archived span cap": beyond,
        "closing tally": closing_stats(closure_rows)[0]["tally"] if closure_rows else [],
        "archive comparison": checks,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", action="store_true")
    cli.add_argument("--output", type=Path)
    cli.add_argument("--roster", choices=ROSTERS, action="append")
    args = cli.parse_args()
    start = perf_counter()
    census = read_census()
    result = {
        "roster": {
            "census file": str(CENSUS.relative_to(CENSUS.parents[2])),
            "census sha256": sha256(CENSUS.read_bytes()).hexdigest(),
            "held-out weighting": "Independent pair meeting with probability 1/3, multiplicity one or two equally, "
                                  "loose count zero, one or two equally, conditional on connectivity, at least three "
                                  "places at every knot and at most 18 distinctions. Labelled draws with replacement.",
            "held-out parameters": {"sizes": [6, 7, 8], "accepted per size": 300, "seed plus size": 20261206},
            "larger sample parameters": {"sizes": [9, 10, 11, 12], "accepted per size": 100,
                                          "seed plus size": 20261212, "maximum distinctions": 30},
        },
        "archive cap for span and origin": FROZEN_SPAN_SIZE,
        "archive cap for premise growth": GROWTH_SIZE,
        "unarchived premise arms": {"one fewer and arity floor": ["heldout", "built", "sampled"]},
        "pilot": args.pilot,
        "cases": {},
    }
    if not args.roster or "census" in args.roster:
        census_time = perf_counter()
        result["roster"]["independent census coverage"] = verify_census(census)
        result["roster"]["census verification seconds"] = round(perf_counter() - census_time, 3)
    for roster in args.roster or ROSTERS:
        variants = [("parity", "ordinary")]
        if roster == "census":
            variants.extend([("parity", "one_fewer"), ("parity", "arity_floor")])
        if roster in ("census", "heldout", "small built"):
            variants.append(("nae", "ordinary"))
        roster_starts = list(items(roster, census))
        for law, arm in variants:
            basename = "built" if roster == "small built" else roster
            case = f"{roster}, {law}, {arm}"
            sections = {}
            if law == "parity" and roster != "small built":
                suffix = "" if arm == "ordinary" else f"_{arm}"
                sections["premises"] = f"frozen_premises_{basename}{suffix}.jsonl"
            if roster in ("census", "heldout", "small built") and arm == "ordinary":
                sections["closing"] = f"closing_{basename}_{law}.jsonl"
                if law == "parity":
                    sections["origin"] = f"origin_{basename}.jsonl"
            read_at = perf_counter()
            archives, recounts = {}, {}
            for part, filename in sections.items():
                archives[part], recounts[part] = read_section(filename, part)
            replay_at = perf_counter()
            checked = replay(roster_starts, law, arm, archives, args.pilot)
            case_stats = {
                "recount": recounts, "replay": checked,
                "recount seconds": round(replay_at - read_at, 3),
                "replay seconds": round(perf_counter() - replay_at, 3),
            }
            result["cases"][case] = case_stats
            print(case, checked["starts"], checked["overall"]["funded rounds"],
                  case_stats["replay seconds"],
                  {part: counts["mismatched trajectories"] for part, counts in checked["archive comparison"].items()},
                  flush=True)
    result["total seconds"] = round(perf_counter() - start, 3)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        for case, values in result["cases"].items():
            for part, detail in values["replay"]["archive comparison"].items():
                if detail["mismatched trajectories"]:
                    print(case, part, detail["examples"])


if __name__ == "__main__":
    main()
