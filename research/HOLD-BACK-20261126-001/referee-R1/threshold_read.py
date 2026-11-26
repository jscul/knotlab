"""Validate the raw birth decisions and compare the repeated cap with its archive."""

import gzip
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
rows = [json.loads(line) for path in ["threshold_pilot.jsonl", "threshold_sample.jsonl"]
        for line in (HERE / path).read_text().splitlines()]
with gzip.open(HERE.parent / "linked_runs.jsonl.gz", "rt") as f:
    original = {r["B"]: r for line in f if (r := json.loads(line))["law"][0] == "CAP-3"}


def count_decisions(entries, per_round):
    tally = Counter()
    different = 0
    for kind, received, demand, role, local, cap, count in entries:
        floor = max(1, 3 - received)
        funded = max(floor, demand)
        assert local == min(funded, max(floor, received + 1))
        assert cap == min(funded, 3)
        tally[kind, received, demand, local, cap] += count
        different += (local != cap) * count
    assert sum(tally.values()) == sum(total for total, diffs in per_round)
    assert different == sum(diffs for total, diffs in per_round)
    return tally


def overlaps(tally):
    return {"agree": sum(n for key, n in tally.items() if key[-1] == key[-2]),
            "differ": sum(n for key, n in tally.items() if key[-1] != key[-2]),
            "different_inputs": [[*key, count] for key, count in sorted(tally.items()) if key[-1] != key[-2]]}


def first_disagreement(decisions):
    return next((i for i, (_, different) in enumerate(decisions, 1) if different), None)


totals = {}
by_pair = []
archived_errors = []
for r in rows:
    identifier = r["far"]
    arms = r["arms"]
    archived = original[identifier]
    cap = arms["cap"]
    cap_events = [(c["after"], c["linked"], c["sharings"], c["heard"], c["common_horizon"])
                  for c in cap["changes"]]
    archived_events = [(c["t0"], c["linked"], c["sharings"], c["heard"], c["rounds"])
                       for c in archived["changes"]]
    if cap_events != archived_events:
        archived_errors.append([identifier, "changes", cap_events, archived_events])
    if cap["linked"] != archived["linked"] or cap["base_births"] != archived["births"]:
        archived_errors.append([identifier, "unchanged linked or births"])
    for c, a in zip(cap["changes"], archived["changes"]):
        births = cap["base_births"][:c["after"]] + [n for n, d in c["suffix_decisions_by_round"]]
        if c["heard"] is not None and births != a["births with"]:
            archived_errors.append([identifier, "marked births on hearing", c["after"], c["knot"]])
    pair = {"far": identifier, "cpu_seconds": r["cpu_seconds"]}
    shared_names = []
    for mode, arm in arms.items():
        aggregate = totals.setdefault(mode, {"base": Counter(), "suffix": Counter(), "hearing": Counter(),
                                             "horizon": Counter(), "marks": 0, "tested_pairs": 0,
                                             "linked_after_3": 0, "continued": 0, "late": 0,
                                             "continued_common": 0, "linked_every_round": 0,
                                             "fully_funded_base": 0, "held_back_in_suffix": Counter(),
                                             "first_difference_after_mark": Counter(),
                                             "difference_before_hearing": Counter(),
                                             "different_marked_growths": 0,
                                             "different_marked_growths_heard": 0})
        base = count_decisions(arm["base_overlap"], arm["base_decisions_by_round"])
        assert arm["base_births"] == [n for n, d in arm["base_decisions_by_round"]]
        aggregate["base"].update(base)
        aggregate["fully_funded_base"] += sum(n for (k, p, d, a, b), n in base.items()
                                              if (a if mode == "local" else b) >= d)
        aggregate["tested_pairs"] += 1
        aggregate["linked_after_3"] += arm["linked"][2] is True
        aggregate["linked_every_round"] += all(value is True for value in arm["linked"])
        changes = arm["changes"]
        aggregate["marks"] += len(changes)
        joint = []
        events = {}
        for c in changes:
            suffix = count_decisions(c["marked_suffix_overlap"], c["suffix_decisions_by_round"])
            aggregate["suffix"].update(suffix)
            for (kind, p, d, local_f, cap_f), n in suffix.items():
                if (local_f if mode == "local" else cap_f) < d:
                    aggregate["held_back_in_suffix"][f"{kind} p={p} D={d}"] += n
            delay = first_disagreement(c["suffix_decisions_by_round"])
            if delay is not None:
                aggregate["different_marked_growths"] += 1
                aggregate["first_difference_after_mark"][delay] += 1
                if c["heard"] is not None:
                    aggregate["different_marked_growths_heard"] += 1
                    aggregate["difference_before_hearing"][c["heard"] - (c["after"] + delay)] += 1
            horizon = min(arm["base_horizon"], c["marked_horizon"])
            assert horizon == c["common_horizon"] and horizon > c["after"]
            aggregate["horizon"][horizon] += 1
            here = (c["after"], c["name"])
            assert here not in events
            events[here] = c["heard"]
            if c["heard"] is not None:
                t = c["heard"]
                assert c["after"] < t <= horizon and (c["added_in_marked"] or c["missing_from_marked"])
                assert c["later_births"][0] == sum(arm["base_births"][t:])
                assert c["later_births_common"][0] == sum(arm["base_births"][t:horizon])
                aggregate["hearing"][t] += 1
                aggregate["late"] += t > 6
                aggregate["continued"] += bool(min(c["later_births"]))
                aggregate["continued_common"] += bool(min(c["later_births_common"]))
                joint.append([c["after"], c["linked"], c["sharings"], t])
        shared_names.append(events)
        diffs = first_disagreement(arm["base_decisions_by_round"])
        pair[mode] = {"marks": len(events), "heard": joint,
                      "base_first_rule_difference": diffs, "base_overlap": overlaps(base),
                      "linked_at_marks": [arm["linked"][t-1] for t in (3, 5, 8) if t <= arm["base_horizon"]]}
    first, second = shared_names
    common = first.keys() & second.keys()
    pair["matched_descent"] = {"marks": len(common), "identical_first_hearing": sum(first[k] == second[k] for k in common),
                              "cap_only_heard": sum(first[k] is None and second[k] is not None for k in common),
                              "local_only_heard": sum(first[k] is not None and second[k] is None for k in common)}
    by_pair.append(pair)

for mode in totals:
    for key in ("base", "suffix"):
        totals[mode][key] = overlaps(totals[mode][key])
print(json.dumps({"archive_mismatches": archived_errors, "totals": totals, "pairs": by_pair}, indent=2))
