"""Swap senders against the three mutually sharing knots under the nominal cap."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import time

from growth import grow, mutual_three, start


HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent.parent / "SHORT-AGAIN-20261126-001"
SEED = 20261126
PER_STRATUM = 6
ROUNDS = 16
BOUND = 3000
PANEL_TWO = "g3:22@0"
ORDER = [(cap, d) for d in (3, 2) for cap in (6, 7, 3, 4, 5)]


def archived_rows(path):
    with gzip.open(path, "rt") as stream:
        yield from map(json.loads, stream)


def loose_at_site(name):
    if name == "stub":
        return None
    pattern = start(name)
    return pattern.loose[pattern.site]


def senders():
    prior_rows = archived_rows(PREDECESSOR / "switch_runs.jsonl.gz")
    prior = sorted({row["B"] for row in prior_rows
                    if row["A"] == "g7:122@0" and row["d"] == 3
                    and row["law"] == ["CAP-3", "CANCEL-WAIT"]
                    and row["join"] == "meeting"})
    receiver_rows = archived_rows(HERE.parent / "receivers_runs.jsonl.gz")
    four_knot_ids = sorted({row["A"] for row in receiver_rows if row["A"].startswith("n4:")})
    strata = defaultdict(list)
    for name in four_knot_ids:
        strata[loose_at_site(name)].append(name)

    assert len(prior) == 48
    assert {loose: len(names) for loose, names in strata.items()} == {0: 59, 1: 144, 2: 198, 3: 198}
    rng = random.Random(SEED)
    sample = {loose: sorted(rng.sample(strata[loose], PER_STRATUM)) for loose in sorted(strata)}
    return prior, strata, sample


def first_difference(left, right, attribute):
    return next((i for i, (a, b) in enumerate(zip(left, right), 1)
                 if getattr(a, attribute) != getattr(b, attribute)), None)


def comparison(left, right):
    first_count = first_difference(left, right, "own_births")
    first_signature = first_difference(left, right, "own_signature")
    return {
        "rounds_compared": min(len(left), len(right)),
        "first_count_difference": first_count,
        "first_signature_difference": first_signature,
        "own_short_before_signature_difference": (
            any(row.own_short for row in left[:first_signature - 1])
            or any(row.own_short for row in right[:first_signature - 1])
        ) if first_signature is not None else None,
    }


def grow_case(cap, d, sender, mark_after=None, rounds=ROUNDS):
    receiver = mutual_three(cap - 2)
    return grow(receiver, sender, d, f"CAP-{cap}", rounds=rounds, bound=BOUND,
                join="meeting", mark_after=mark_after)


def growth_record(rows):
    return {
        "rounds_completed": len(rows),
        "last_knot_count": rows[-1].knots if rows else None,
        "own_births": [row.own_births for row in rows],
        "own_short": [row.own_short for row in rows],
        "sender_site_owed_and_held": [row.sender_site_owed_and_held for row in rows],
    }


def summarize(rows, target):
    counts = defaultdict(Counter)
    for row in rows:
        measured = row["against_stub"]
        loose = row["site_loose_before_meeting"]
        stratum = f"{row['source']}/{loose if loose is not None else 'stub'}"
        counts[stratum]["senders"] += 1
        for name in ("first_count_difference", "first_signature_difference"):
            first = measured[name]
            if measured["rounds_compared"] < target:
                counts[stratum][f"{name}/censored_before_{target}"] += 1
            elif first == target:
                counts[stratum][f"{name}/at_{target}"] += 1
            elif first is None:
                counts[stratum][f"{name}/none_in_prefix"] += 1
            else:
                counts[stratum][f"{name}/{first}"] += 1
        if row["against_panel_two"]["rounds_compared"] >= target:
            first_vs_panel_two = row["against_panel_two"]["first_signature_difference"]
            if first_vs_panel_two is None or first_vs_panel_two > target:
                counts[stratum][f"same_signature_as_panel_two_through_{target}"] += 1
        if (measured["first_signature_difference"] == target
                and measured["own_short_before_signature_difference"] is False):
            counts[stratum][f"switch_against_stub_at_{target}"] += 1
    return {key: dict(count) for key, count in sorted(counts.items())}


def sender_swaps(cap, d, prior, sample):
    started = time.monotonic()
    stub = grow_case(cap, d, "stub")
    panel_two = grow_case(cap, d, PANEL_TWO)
    baselines = {"stub": stub, PANEL_TWO: panel_two}
    rows = []
    for source, sender in [("prior", name) for name in prior] + [("four-knot sample", name) for name in sample]:
        growth = baselines[sender] if sender in baselines else grow_case(cap, d, sender)
        rows.append({
            "sender": sender,
            "source": source,
            "site_loose_before_meeting": loose_at_site(sender),
            "against_stub": comparison(growth, stub),
            "against_panel_two": comparison(growth, panel_two),
            **growth_record(growth),
        })
    target = 2 * d + 1
    return {"cap": cap, "d": d, "target_round": target, "rows": rows,
            "summary": summarize(rows, target), "seconds": round(time.monotonic() - started, 4)}


def interventions(sample):
    """Give one more loose distinction to selected sites after round t0."""
    d = 3
    selected = ["g7:122@0", "g7:122@1", *(sample[loose][0] for loose in (0, 1, 2, 3))]
    rows = []
    for cap in (6, 7):
        stub = grow_case(cap, d, "stub")
        for sender in selected:
            baseline = grow_case(cap, d, sender)
            comparison_to_stub = comparison(baseline, stub)
            for mark_after in (0, d - 1, d, d + 1, 8):
                marked = grow_case(cap, d, sender, mark_after)
                rows.append({
                    "cap": cap,
                    "d": d,
                    "sender": sender,
                    "site_loose_before_meeting": loose_at_site(sender),
                    "mark_after": mark_after,
                    "mark_acted_in_completed_round": len(marked) > mark_after,
                    "unmarked_against_stub": comparison_to_stub,
                    "marked_against_unmarked": comparison(marked, baseline),
                    "marked_against_stub": comparison(marked, stub),
                    **growth_record(marked),
                })
    return rows


def pilot(sample):
    for cap in (6, 7, 3):
        for d in (3, 2):
            for sender in ("stub", PANEL_TWO, "g7:122@0", sample[2][0], sample[3][0]):
                started = time.monotonic()
                rows = grow_case(cap, d, sender)
                print(json.dumps({"cap": cap, "d": d, "sender": sender,
                                  "seconds": round(time.monotonic() - started, 4), **growth_record(rows)}))
    for cap in (6, 7):
        for mark_after in (2, 3, 8):
            started = time.monotonic()
            sender = sample[2][0]
            rows = grow_case(cap, 3, sender, mark_after)
            print(json.dumps({"cap": cap, "d": 3, "sender": sender, "mark_after": mark_after,
                              "seconds": round(time.monotonic() - started, 4), **growth_record(rows)}))


def archive_replay(cells):
    """Compare independent growth traces to archived count and short traces."""
    published = Counter()
    mismatches = []
    archived_nominal = {
        (row["cap"], row["d"]): row["by sender"]
        for row in archived_rows(HERE.parent / "rule_runs.jsonl.gz")
        if row["reading"] == "classes" and int(row["A"].split(":")[1][0]) == row["cap"] - 2
    }
    archived_prior = {
        (row["d"], row["B"]): row
        for row in archived_rows(PREDECESSOR / "switch_runs.jsonl.gz")
        if row["A"] == "g7:122@0" and row["law"] == ["CAP-3", "CANCEL-WAIT"]
        and row["join"] == "meeting" and row["d"] in (2, 3)
    }
    for cell in cells:
        cap, d = cell["cap"], cell["d"]
        for row in cell["rows"]:
            sender = row["sender"]
            candidates = {"nominal rule archive": archived_nominal[(cap, d)].get(sender)}
            if cap == 3:
                candidates["prior sender archive"] = archived_prior.get((d, sender))
            for source, archive in candidates.items():
                if archive is None:
                    continue
                published[source] += 1
                if (row["own_births"] != archive["own births"] or row["own_short"] != archive["A short"]
                        or row["last_knot_count"] != archive["knots"]):
                    mismatches.append({"source": source, "cap": cap, "d": d, "sender": sender})
    return {"traces_compared": dict(published), "mismatches": mismatches}


def four_knot_census(cap, strata, sample, trial=False):
    """Read all four-knot sites exactly through the claimed reading round."""
    d, target = 3, 7
    started = time.monotonic()
    stub = grow_case(cap, d, "stub", rounds=target)
    panel_two = grow_case(cap, d, PANEL_TWO, rounds=target)
    source = sample if trial else strata
    rows = []
    for sites in source.values():
        for sender in sites:
            growth = grow_case(cap, d, sender, rounds=target)
            pattern = start(sender)
            sharings = [[a, b] for a, b in combinations(range(len(pattern.stars)), 2)
                        if set(pattern.stars[a]).intersection(pattern.stars[b])]
            rows.append({"sender": sender, "source": "four-knot census",
                         "site": pattern.site, "loose_counts": pattern.loose,
                         "site_loose_before_meeting": pattern.loose[pattern.site],
                         "sharings": sharings, "against_stub": comparison(growth, stub),
                         "against_panel_two": comparison(growth, panel_two), **growth_record(growth)})
    return {"cap": cap, "d": d, "target_round": target, "round_limit": target,
            "rows": rows, "summary": summarize(rows, target),
            "seconds": round(time.monotonic() - started, 4),
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def run(prior, strata, sample):
    started = time.monotonic()
    flattened_sample = [name for group in sample.values() for name in group]
    cells = []
    for cap, d in ORDER:
        cell = sender_swaps(cap, d, prior, flattened_sample)
        cells.append(cell)
        totals = Counter()
        for row in cell["rows"]:
            comparison = row["against_stub"]
            if comparison["rounds_compared"] < cell["target_round"]:
                status = "censored before target"
            elif comparison["first_signature_difference"] == cell["target_round"]:
                status = "first signature difference at target"
            else:
                status = "no first signature difference at target"
            totals[(str(row["site_loose_before_meeting"]), status)] += 1
        print(f"cap {cap}, d {d}, {cell['seconds']} seconds, {dict(sorted(totals.items()))}", flush=True)
    intervention_rows = interventions(sample)
    return {
        "question": "Does the nominated receiver distinguish a two-loose site at round 2d + 1 under the nominal cap?",
        "receiver": "Three mutually sharing knots, loose counts (cap - 2, 2, 2), sited at the first knot.",
        "join": "Meeting through d - 1 link knots, short knots wait.",
        "round_limit": ROUNDS,
        "knot_bound": BOUND,
        "sample_seed": SEED,
        "four_knot_sample_weighting": "Uniform without replacement within each initial site loose-count stratum.",
        "four_knot_strata": {loose: len(names) for loose, names in sorted(strata.items())},
        "four_knot_sample": sample,
        "prior_roster": prior,
        "cells": cells,
        "interventions": intervention_rows,
        "archive_replay": archive_replay(cells),
        "seconds": round(time.monotonic() - started, 4),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--four-census-pilot", type=int, choices=(3, 6))
    mode.add_argument("--four-census", type=int, choices=(3, 6))
    args = parser.parse_args()
    prior, strata, sample = senders()
    output = HERE / "sender_swap.json"
    if args.pilot:
        pilot(sample)
    elif args.four_census_pilot:
        census = four_knot_census(args.four_census_pilot, strata, sample, trial=True)
        print(json.dumps({key: value for key, value in census.items() if key != "rows"}))
    elif args.four_census:
        result = json.loads(output.read_text())
        census = four_knot_census(args.four_census, strata, sample)
        results = result.setdefault("four_knot_sender_censuses", {})
        results[str(args.four_census)] = census
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({key: value for key, value in census.items() if key != "rows"}))
    else:
        result = run(prior, strata, sample)
        output.write_text(json.dumps(result, indent=2) + "\n")
