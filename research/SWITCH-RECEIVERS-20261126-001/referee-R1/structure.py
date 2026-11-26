"""Rebuild the six receivers, compare their birth records, and change the proposed rule's inputs.

Run with the repository's .venv/bin/python -B. All growth comes from the
independent growth.py in this directory. The compressed archive supplies
the names and counts against which the reruns are compared.
"""

from __future__ import annotations

import argparse
import gzip
import json
import resource
from collections import Counter, defaultdict
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from time import perf_counter

from growth import from_sharings, grow, mutual_three, start

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / "receivers_runs.jsonl.gz"
SENDERS = ("g1:3@0", "g3:22@0", "g6:122@0", "g7:122@0", "stub")
TWO = SENDERS[1]
THREE = "n3:g7:122@0"
MUTUAL = ((0, 1), (0, 2), (1, 2))


def first(left, right):
    """First difference on the rounds that both have."""
    return next((i for i, (a, b) in enumerate(zip(left, right), 1) if a != b), None)


def sharings(pattern):
    holders = defaultdict(list)
    for i, knot in enumerate(pattern.stars):
        for distinction in knot:
            holders[distinction].append(i)
    return sorted(pair for pair in holders.values() if len(pair) == 2)


def features(pattern, k):
    site, loose = pattern.site, pattern.loose
    members = {i for i, held in enumerate(loose) if held > 0}
    others = sorted(loose[i] for i in members if i != site)
    met_by = [set() for _ in loose]
    for i, j in sharings(pattern):
        if i in members:
            met_by[j].add(i)
        if j in members:
            met_by[i].add(j)
    whole = (len(members) >= 3 and not any(members <= group for group in met_by)
             and all(any({a, b} <= group for group in met_by) for a, b in combinations(members, 2)))
    mutual = len(loose) == 3 and len({tuple(pair) for pair in sharings(pattern)}) == 3
    others_two = len(loose) == 3 and all(n == 2 for i, n in enumerate(loose) if i != site)
    site_loose = loose[site] == k - 2
    return {
        "site has k places": len(pattern.stars[site]) == k,
        "site has k minus two loose": site_loose,
        "site holds two shared distinctions": len(pattern.stars[site]) - loose[site] == 2,
        "three knots each meet both others": mutual,
        "three knots and both others hold two loose": others_two,
        "three mutually meeting knots, both others hold two, site holds k minus two":
            mutual and others_two and site_loose,
        "all live members form one group, two nonsite members hold two loose, remaining nonsite live members hold one, site holds k minus two":
            whole and site_loose and others.count(2) == 2 and all(n in (1, 2) for n in others),
    }


def read_archive():
    by_cap = defaultdict(list)
    switch_features = defaultdict(list)
    cap_three = {}
    t = perf_counter()
    with gzip.open(ARCHIVE, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            receiver, law, d = row["A"], row["law"], row["d"]
            if law == "CAP-3" and receiver.startswith(("n3:g7:", "n4:g17:", "n4:g18:")):
                cap_three[receiver, d] = row
            if d != 3 or law not in ("CAP-3", "CAP-4", "CAP-5") or not receiver.startswith("n"):
                continue
            byr = row["by sender"]
            k = int(law[4:])
            watched = 2 * d + 1
            if min(run["rounds"] for run in byr.values()) < watched:
                by_cap[k].append((receiver, None, None))
                continue
            reported = {name: run["differs from the stub"] for name, run in byr.items()}
            common = min(run["rounds"] for run in byr.values())
            first_seen = min((r for r in reported.values() if r is not None and r <= common), default=None)
            pattern = start(receiver)
            if first_seen and first_seen > 2 * d and not any(
                    any(run["A short"][:first_seen - 1]) for run in byr.values()):
                switch_features[k].append({"receiver": receiver, "first": first_seen,
                                           "site loose": pattern.loose[pattern.site],
                                           "site places": len(pattern.stars[pattern.site])})
            first_two_only = (reported[TWO] == watched
                              and all(r is None or r > watched for s, r in reported.items() if s != TWO)
                              and not any(any(run["A short"][:watched - 1]) for run in byr.values()))
            by_cap[k].append((receiver, first_two_only, features(pattern, k)))
    six = sorted(name for name, positive, _ in by_cap[3] if positive)
    if THREE not in six:
        raise ValueError("Expected the earlier three-knot receiver in the rebuilt roster.")
    output = {}
    for k, rows in sorted(by_cap.items()):
        cap_output = {}
        for family, selected in (("all simple census starts", rows),
                                 ("three mutually meeting knots",
                                  [r for r in rows if r[0].startswith("n3:g7:")])):
            eligible = [r for r in selected if r[1] is not None]
            tests = {}
            for description in eligible[0][2]:
                c = Counter((actual, flags[description]) for _, actual, flags in eligible)
                tests[description] = dict(matches_positive=c[True, True], misses_positive=c[True, False],
                                          matches_negative=c[False, False], selects_negative=c[False, True])
            cap_output[family] = {"cases": len(selected), "reached round seven with five senders": len(eligible),
                                  "round-seven two-loose-only cases": [a for a, passed, _ in eligible if passed],
                                  "feature contrasts": tests}
        cap_output["all receivers that switched on the five-way common prefix"] = switch_features[k]
        output[k] = cap_output
    return six, {(a, d): cap_three[a, d] for a in six for d in range(2, 6)}, output, perf_counter() - t


def growth_panel(receiver, d, law, join="meeting"):
    return {sender: grow(receiver, sender, d, law, join=join) for sender in SENDERS}


def first_round(rows):
    return sorted((sorted(p.ordinal for p in name.parents), fresh, places)
                  for name, fresh, places in rows[0].own_signature)


def after_first(rows, names):
    """Match the initial join and the two offshoots. Keep every later birth record in full."""
    initial = rows[0].own_signature
    joined = [n for n, _, _ in initial if len(n.parents) >= 3]
    offshoots = sorted((n for n, _, _ in initial if len(n.parents) == 1),
                       key=lambda n: n.parents[0].ordinal)
    if len(initial) != 3 or len(joined) != 1 or len(offshoots) != 2:
        raise ValueError("The first round does not have the three proposed own births.")
    known = dict(zip([joined[0], *offshoots], (0, 1, 2)))

    def name_of(birth):
        if birth not in known:
            if not birth.parents:
                raise ValueError("A later own birth uses a start knot directly.")
            key = (tuple(sorted(name_of(p) for p in birth.parents)), birth.ordinal)
            known[birth] = names.setdefault(key, len(names) + 3)
        return known[birth]

    return [tuple(sorted((name_of(n), f, places) for n, f, places in row.own_signature))
            for row in rows[1:]]


def compare_six(six, archived):
    answer = []
    first_making = {}
    for d in range(2, 6):
        for sender in SENDERS:
            names = {}
            template = grow(THREE, sender, d, "CAP-3")
            expected = after_first(template, names)
            for receiver in six:
                rows = template if receiver == THREE else grow(receiver, sender, d, "CAP-3")
                raw = archived[receiver, d]["by sender"][sender]
                counts = [x.own_births for x in rows]
                shorts = [x.own_short for x in rows]
                row_check = {"receiver": receiver, "d": d, "sender": sender, "rounds": len(rows),
                             "three-knot rounds": len(template),
                             "archive rounds, own counts, shorts, final knots match":
                             (len(rows), counts, shorts, rows[-1].knots) ==
                             (raw["rounds"], raw["own births"], raw["A short"], raw["knots"]),
                             "first different own count": first(counts, [r.own_births for r in template]),
                             "first different own short count": first(shorts, [r.own_short for r in template]),
                             "first different named birth record":
                             first([r.own_signature for r in rows], [r.own_signature for r in template]),
                             "first different round after matching the first three births":
                             first(after_first(rows, names), expected),
                             "whole-growth knot count exceeds the smaller start by":
                             sorted({r.knots - b.knots for r, b in zip(rows, template)})}
                folded = row_check["first different round after matching the first three births"]
                if folded is not None:
                    row_check["first different round after matching the first three births"] = folded + 1
                answer.append(row_check)
                profile = first_round(rows)
                if receiver in first_making and profile != first_making[receiver]["births"]:
                    raise ValueError("The first own births depend on the sender or join length.")
                p = start(receiver)
                first_making[receiver] = {"loose in start order": p.loose, "site": p.site,
                                          "pairs sharing one distinction": sharings(p), "births": profile}
    return {"first own births as [start parent indices, fresh, places]": first_making,
            "cross-receiver and archive comparisons": answer}


def readings(panel):
    result = {}
    for field in ("own_signature", "own_births", "receiver_inclusive_births"):
        seen = {s: [getattr(r, field) for r in rows] for s, rows in panel.items()}
        firsts = {s: first(tr, seen["stub"]) for s, tr in seen.items()}
        all_pairs = [first(seen[a], seen[b]) for a, b in combinations(SENDERS, 2)]
        finite = [r for r in all_pairs if r is not None]
        r = min(finite) if finite else None
        result[field] = {"first between any pair": r, "first against stub": firsts,
                         "some strictly own knot was short before first difference":
                         None if r is None else any(any(z.own_short for z in rows[:r-1]) for rows in panel.values())}
    result["rounds"] = {s: len(rows) for s, rows in panel.items()}
    result["any-receiver-ancestor births in round four"] = {
        s: rows[3].receiver_inclusive_births if len(rows) >= 4 else None for s, rows in panel.items()}
    return result


def interventions():
    output = []
    duplication = (*MUTUAL, (0, 1))
    for d in (2, 3):
        for a in (3, 4):
            groups = {}
            for spelling, shares in (("one sharing per pair", MUTUAL), ("two sharings of the site and first partner", duplication)):
                rec = from_sharings((a, 2, 2), shares)
                panel = growth_panel(rec, d, "CAP-6")
                groups[spelling] = panel
                output.append({"d": d, "law": "CAP-6", "join": "meeting", "changed": spelling,
                               "loose": rec.loose, "site": rec.site, "site places": len(rec.stars[rec.site]),
                               "reading": readings(panel)})
            plain, doubled = groups.values()
            # Rows contain both ends' complete birth readings, shorts, the whole knot count and sender-site owing.
            output[-1]["every rebuilt round equals its singly shared control"] = all(
                plain[s] == doubled[s] for s in SENDERS)
    for k, a in ((3, 1), (6, 4)):
        rec = mutual_three(a)
        changes = [("baseline", rec, f"CAP-{k}", "meeting"),
                   ("new site", replace(rec, site=1), f"CAP-{k}", "meeting"),
                   ("new join", rec, f"CAP-{k}", "share")]
        if k == 3:
            changes.extend([("ordinary count", rec, "ORD", "meeting"),
                            ("record's one fewer", rec, "REC-ONE-FEWER", "meeting")])
        for changed, p, law, join in changes:
            output.append({"d": 3, "law": law, "join": join, "changed": changed, "loose": p.loose,
                           "site": p.site, "site places": len(p.stars[p.site]),
                           "reading": readings(growth_panel(p, 3, law, join))})
    return output


def pilot():
    """Time one sender at the actual full-run horizon for each kind of configuration."""
    cases = [(start(THREE), d, "CAP-3", "meeting") for d in range(2, 6)]
    cases.append((start("g18:1122@0"), 5, "CAP-3", "meeting"))
    for d in (2, 3):
        for a in (3, 4):
            for shares in (MUTUAL, (*MUTUAL, (0, 1))):
                cases.append((from_sharings((a, 2, 2), shares), d, "CAP-6", "meeting"))
    for a in (1, 4):
        p = mutual_three(a)
        cases.extend([(replace(p, site=1), 3, f"CAP-{a+2}", "meeting"),
                      (p, 3, f"CAP-{a+2}", "share")])
    cases.extend([(mutual_three(1), 3, law, "meeting") for law in ("ORD", "REC-ONE-FEWER")])
    records = []
    for rec, d, law, join in cases:
        started = perf_counter()
        rows = grow(rec, TWO, d, law, join=join)
        records.append({"loose": rec.loose, "site": rec.site, "site places": len(rec.stars[rec.site]),
                        "d": d, "law": law, "join": join, "seconds": round(perf_counter() - started, 5),
                        "rounds": len(rows), "final knots": rows[-1].knots})
    t = perf_counter()
    with gzip.open(ARCHIVE, "rt") as stream:
        for _ in range(20):
            json.loads(next(stream))
    return {"one sender per configuration": records, "twenty archive rows seconds": round(perf_counter() - t, 5),
            "projected 200 growths at slowest pilot seconds": round(200 * max(r["seconds"] for r in records), 2)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2_400_000_000, 2_400_000_000))
    t = perf_counter()
    timing = pilot()
    if args.pilot:
        print(json.dumps(timing, indent=2))
        return
    six, archive, contrasts, load_seconds = read_archive()
    t_growth = perf_counter()
    sources = compare_six(six, archive)
    six_seconds = perf_counter() - t_growth
    t_growth = perf_counter()
    swaps = interventions()
    result = {
        "limits": {"rounds": 16, "knots checked after each round": 3000,
                   "processes": 1, "address space bytes": 2_400_000_000},
        "sender keys": dict(zip(SENDERS, ("one knot, site holds three loose", "two knots, site holds two loose",
                                          "three in a path, middle site holds one loose",
                                          "three mutually sharing knots, site holds one loose", "stub"))),
        "target for feature contrasts": (
            "At d=3 every sender reached round 7. The two-knot sender first differs from the stub "
            "in round 7, all other senders agree with the stub through round 7, and no own receiver "
            "knot was short in rounds 1 to 6. Round against the stub is the archived making of own births."),
        "scope of contrasts": "One case per archived sited simple start, three bench patterns excluded.",
        "why the four-knot counts agree": (
            "All four knots pay the same first own join. The additional one-loose knot spends its "
            "only distinction there and has no other child. Each of the two knots holding two "
            "loose makes one offshoot. The site also pays the meeting with the line. After the "
            "round all receiver start knots are spent. The additional parent meets only one live "
            "child, so contributes no met set of two or more live children. The three first own "
            "births can be paired by their roles. Their later birth records are compared under "
            "this pairing, retaining parents, ordinal among equal births, fresh count and places."),
        "why duplicate sharing has no effect on the observed growth": (
            "The added distinction already has both holders. It adds one to their place counts "
            "but changes neither their usable loose counts nor whom they meet. Groups depend on "
            "sets of members meeting a common knot. Each kept birth takes only loose distinctions "
            "and receives fresh ones from its number of parents and next demand. The correspondence "
            "of loose counts and meetings therefore continues after a round under these laws. "
            "The two fresh starts test this consequence of the definitions."),
        "feature contrasts at d=3": contrasts,
        "six under cap three": sources,
        "changed inputs": swaps,
        "pilot": timing,
        "seconds": {"read archive and compare features": round(load_seconds, 4),
                    "six across all five senders and four link lengths": round(six_seconds, 4),
                    "change inputs": round(perf_counter() - t_growth, 4),
                    "entire check": round(perf_counter() - t, 4)},
        "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    output = HERE / "structure.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"file": output.name, "receivers": len(six), "cross comparisons": len(sources[
        "cross-receiver and archive comparisons"]), "input panels": len(swaps), "seconds": result["seconds"]}))


if __name__ == "__main__":
    main()
