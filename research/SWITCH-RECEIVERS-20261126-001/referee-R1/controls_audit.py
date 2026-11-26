"""Recount rule, intervention, long-run, and sender records without producer imports."""

import argparse
from collections import Counter, defaultdict
from gzip import open as gzip_open
from hashlib import sha256
from itertools import combinations, islice, product
import json
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
RECORD = HERE.parent
PREDECESSOR = RECORD.parent / "SHORT-AGAIN-20261126-001" / "switch_runs.jsonl.gz"
ONE_KNOT = "g1:3@0"
TWO_KNOT = "g3:22@0"
MIDDLE_SITE = "g6:122@0"
SWITCH_RECEIVER = "g7:122@0"
STUB = "stub"
SENDERS = (ONE_KNOT, TWO_KNOT, MIDDLE_SITE, SWITCH_RECEIVER, STUB)
INPUTS = ("rule_runs.jsonl.gz", "controls_runs.jsonl.gz", "senders_runs.jsonl.gz", "reflect.json", "receivers_runs.jsonl.gz")


def rows(filename, limit=None):
    with gzip_open(RECORD / filename, "rt") as stream:
        return [json.loads(line) for line in islice(stream, limit)]


def first_change(first, second):
    return next((r for r, (a, b) in enumerate(zip(first, second), 1) if a != b), None)


def departure(trace):
    return first_change(trace, range(3, len(trace) + 3))


def alternating_short_after(trace, first):
    if first is None or len(trace) <= first:
        return None
    return all(bool(value) == (offset % 2 == 1) for offset, value in enumerate(trace[first:], 1))


def comparison(row):
    runs = row["by sender"]
    assert set(runs) == set(SENDERS)
    births = {sender: runs[sender]["own births"] for sender in SENDERS}
    short = {sender: runs[sender]["A short"] for sender in SENDERS}
    horizon = {sender: len(births[sender]) for sender in SENDERS}
    assert all(horizon[s] == len(short[s]) == runs[s]["rounds"] for s in SENDERS)
    common = min(horizon.values())
    by_prefix = defaultdict(list)
    for sender, sequence in births.items():
        by_prefix[tuple(sequence[:common])].append(sender)
    classes = list(by_prefix.values())
    first_pair = {pair: first_change(births[pair[0]], births[pair[1]]) for pair in combinations(SENDERS, 2)}
    first = min((r for r in first_pair.values() if r is not None), default=None)
    first_common = min((r for r in first_pair.values() if r is not None and r <= common), default=None)
    own_short_before = None if first is None else any(any(sequence[: first - 1]) for sequence in short.values())
    assert row["first differs"] == first_common
    assert row["rounds compared"] == common
    assert {frozenset(group) for group in row["classes"]} == {frozenset(group) for group in classes}
    if first == first_common:
        assert row["own short before"] == own_short_before
    against_stub = {}
    for sender in SENDERS:
        changed = first_change(births[sender], births[STUB])
        prefix = min(horizon[sender], horizon[STUB])
        short_before = None if changed is None else any(short[sender][: changed - 1] + short[STUB][: changed - 1])
        assert changed == runs[sender]["differs from the stub"]
        assert prefix == runs[sender]["rounds with the stub"]
        against_stub[sender] = {
            "first": changed,
            "rounds": prefix,
            "short_before": short_before,
            "short_rounds": [r for r, total in enumerate(short[sender], 1) if total],
            "alternate_short_to_stop": alternating_short_after(short[sender], changed),
        }
    return {
        "receiver": row["A"], "cap": row["cap"], "steps": row["d"],
        "all_sender_common_rounds": common, "first_all_sender_common": first_common,
        "first_on_any_pair": first, "classes_all_sender_common": classes,
        "any_own_short_before_first": own_short_before,
        "switch": first is not None and first > 2 * row["d"] and not own_short_before,
        "sender_full_rounds": horizon,
        "stub_comparisons": against_stub,
        "first_after_all_sender_common": [
            {"senders": list(pair), "first": changed}
            for pair, changed in first_pair.items() if changed is not None and changed > common
        ],
    }


def rule_reading(records):
    classes = [comparison(row) for row in records if row["reading"] == "classes"]
    swaps = [row for row in records if row["reading"] == "swap"]
    class_keys = {(r["receiver"], r["cap"], r["steps"]) for r in classes}
    expected = {(f"tri:{loose}22@0", cap, steps) for loose in range(1, 6)
                for cap in range(max(3, loose + 1), loose + 4) for steps in (2, 3)}
    assert len(class_keys) == len(classes) and class_keys == expected
    assert len(swaps) == 30
    by_cap = {}
    for cap in range(3, 8):
        matching = sorted((r for r in swaps if r["cap"] == cap), key=lambda r: r["t0"])
        assert [r["t0"] for r in matching] == list(range(6))
        assert {r["A"] for r in matching} == {f"tri:{cap - 2}22@0"}
        by_cap[cap] = [{"after_round": r["t0"], "first_own_birth_difference_reported": r["heard"],
                        "common_rounds": r["rounds"]} for r in matching]
    return {"classes": classes, "swaps_aggregate_only": by_cap}


def control_reading(records, rule):
    by_kind = defaultdict(list)
    for row in records:
        by_kind[row["reading"]].append(row)
    receiver_set = sorted({r["A"] for r in by_kind["both"]})
    assert len(receiver_set) == len(by_kind["both"]) == 6
    swaps = by_kind["swap"]
    long_runs = by_kind["long"]
    assert len(swaps) == 162 and {(r["A"], r["B"], r["t0"]) for r in swaps} == set(
        product(receiver_set, (ONE_KNOT, TWO_KNOT, STUB), range(9))
    )
    assert len(long_runs) == 30 and {(r["A"], r["B"]) for r in long_runs} == set(product(receiver_set, SENDERS))
    swap_cells = defaultdict(dict)
    for pair in product((ONE_KNOT, TWO_KNOT, STUB), range(9)):
        sender, t0 = pair
        matching = [r for r in swaps if (r["B"], r["t0"]) == pair]
        swap_cells[sender][t0] = {
            "count_by_first_difference_reported": dict(Counter(str(r["heard"]) for r in matching)),
            "count_by_common_rounds": dict(Counter(r["rounds"] for r in matching)),
        }
    by_sender = {}
    for sender in SENDERS:
        matching = [r for r in long_runs if r["B"] == sender]
        for row in matching:
            assert len(row["own births"]) == len(row["A short"]) == row["rounds"]
            assert (row["rounds"] == 22 and row["knots"] <= 6000) or (row["rounds"] < 22 and row["knots"] > 6000)
        sequences = defaultdict(list)
        for row in matching:
            sequences[tuple(row["own births"]), tuple(row["A short"])].append(row["A"])
        by_sender[sender] = {
            "count_by_rounds": dict(Counter(r["rounds"] for r in matching)),
            "knots_at_stop_by_receiver": {r["A"]: r["knots"] for r in matching},
            "sequences": [{"receivers": receivers, "own_births": births, "own_short": short,
                           "first_leaves_r_plus_two": departure(births),
                           "alternate_short_to_stop": alternating_short_after(short, departure(births))}
                          for (births, short), receivers in sequences.items()],
        }
    both = []
    for row in by_kind["both"]:
        ends = {end: departure(row[f"own births {end}"]) for end in ("A", "B")}
        assert all(ends[end] == row[f"{end} leaves first way"] for end in ends)
        both.append({"receiver": row["A"], "other_end": row["A"], "first_leaves_r_plus_two": ends,
                     "equal_own_birth_counts_all_read_rounds": row["own births A"] == row["own births B"],
                     "read_rounds": len(row["own births A"])})
    rule_swaps = rule["swaps_aggregate_only"]
    caps_with_full_horizon = [cap for cap, checks in rule_swaps.items() if all(r["common_rounds"] == 16 for r in checks)]
    return {"swaps_aggregate_only": swap_cells, "long_by_sender": by_sender, "both_ends": both,
            "rule_swaps_caps_with_16_common_rounds": caps_with_full_horizon,
            "long_runs_reaching_round_22": sum(r["rounds"] == 22 for r in long_runs),
            "cap3_switchers_short_counts": switching_short_counts(receiver_set)}


def switching_short_counts(receiver_set):
    by_steps = defaultdict(dict)
    with gzip_open(RECORD / "receivers_runs.jsonl.gz", "rt") as stream:
        for row in (json.loads(line) for line in stream):
            if row["law"] == "CAP-3" and row["A"] in receiver_set:
                checked = comparison(dict(row, cap=3))
                by_steps[row["d"]][row["A"]] = checked["stub_comparisons"]
    assert set(by_steps) == {2, 3, 4, 5}
    for receivers in by_steps.values():
        assert set(receivers) == set(receiver_set)
    return by_steps


def extended_senders(records):
    roster = {r["B"] for r in records}
    assert len(roster) == 48 and len(records) == 192
    assert {(r["law"], r["d"], r["B"]) for r in records} == set(product(("CAP-4", "CAP-5"), (2, 3), roster))
    baseline = {(r["law"], r["d"]): r["own births"] for r in records if r["B"] == STUB}
    results = {}
    for law, steps in product(("CAP-4", "CAP-5"), (2, 3)):
        matching = [r for r in records if (r["law"], r["d"]) == (law, steps)]
        cap = int(law[-1])
        prediction = (cap - 1) * steps + (cap - 2)
        entries = {}
        for r in matching:
            births = r["own births"]
            short = r["A short"]
            assert len(births) == len(short) == r["rounds"]
            changed = departure(births)
            assert changed == r["leaves first way"] == first_change(births, baseline[law, steps])
            entries[r["B"]] = {"first": changed, "rounds": r["rounds"],
                               "own_short_before": None if changed is None else any(short[: changed - 1]),
                               "own_short_rounds": [n for n, count in enumerate(short, 1) if count]}
        results[f"{law} d={steps}"] = {
            "advisor_predicted_round": prediction,
            "count_by_first": dict(Counter(str(r["first"]) for r in entries.values())),
            "count_by_last_round": dict(Counter(r["rounds"] for r in entries.values())),
            "reaching_predicted_round": sum(r["rounds"] >= prediction for r in entries.values()),
            "censored_before_predicted_round_without_a_difference": [
                s for s, r in entries.items() if r["rounds"] < prediction and r["first"] is None
            ],
            "by_sender": entries,
        }
    return roster, results


def reflection_reading(records, roster):
    assert len(records) == 48 and {r["B"] for r in records} == roster
    with gzip_open(PREDECESSOR, "rt") as stream:
        predecessor = [r for r in (json.loads(line) for line in stream)
                       if (r["A"], r["join"], r["law"], r["d"]) ==
                       (SWITCH_RECEIVER, "meeting", ["CAP-3", "CANCEL-WAIT"], 3)]
    assert len(predecessor) == len(roster) and {r["B"] for r in predecessor} == roster
    by_name = {r["B"]: r for r in predecessor}
    by_slack = defaultdict(list)
    by_loose = defaultdict(list)
    separately_named_loose = {"ring": "3", "copier": "2", "source": "3", STUB: "stub"}
    for row in records:
        times = row["site: round and owe less holds while a member"]
        assert len(times) == 1 and times[0][0] == 1
        slack = -times[0][1]
        sender = row["B"]
        if sender.startswith("g"):
            profile, site = sender.split(":")[1].split("@")
            loose = profile[int(site)]
        else:
            loose = separately_named_loose[sender]
        assert row["switch round"] == departure(by_name[sender]["own births"])
        by_slack[slack].append(row)
        by_loose[loose].append(row)
    return {
        "stored_site_member_rounds": 1,
        "count_by_switch_round_for_each_slack": {slack: dict(Counter(str(r["switch round"]) for r in rs))
                                                 for slack, rs in by_slack.items()},
        "count_by_switch_round_for_each_pre_join_loose_count": {
            loose: dict(Counter(str(r["switch round"]) for r in rs)) for loose, rs in by_loose.items()
        },
        "two_knot_sender_duplicate_name": "copier",
        "all_reported_switches": {r["B"]: r["switch round"] for r in records if r["switch round"] is not None},
        "no_negative_slack": all(slack >= 0 for slack in by_slack),
        "all_departures_match_predecessor_birth_counts": True,
        "start_site_control_cases_in_predecessor": {
            sender: [c for c in by_name[sender]["changes"] if c["at"] in ("B0", "bB0")]
            for sender in SENDERS
        },
    }


def mark_reading(unmarked, marked, after, stub=None):
    def first(field):
        return first_change([getattr(r, field) for r in unmarked], [getattr(r, field) for r in marked])

    time_of_mark = marked[after]
    assert time_of_mark.sender_site_owed_and_held is not None
    # Owing zero excludes groups through the site's neighbours. With zero live
    # neighbours it also has no old member for its fresh offshoot to join by
    # meeting through the site. Future births share only with their parents.
    detached = (time_of_mark.sender_site_owed_and_held == (0, 1)
                and time_of_mark.sender_site_live_neighbours == 0
                and unmarked[after].sender_site_owed_and_held is None)
    reading = {
        "after_round": after, "acts_in_round": after + 1,
        "rounds_in_common": min(len(unmarked), len(marked)),
        "first_receiver_own_signature_difference": first("own_signature"),
        "first_receiver_own_birth_count_difference": first("own_births"),
        "first_receiver_inclusive_birth_count_difference": first("receiver_inclusive_births"),
        "first_sender_own_signature_difference": first("sender_signature"),
        "first_whole_knot_count_difference": first("knots"),
        "marked_original_site_first_three_owed_and_held": [r.sender_site_owed_and_held for r in marked[after:after + 3]],
        "marked_original_site_live_neighbours": time_of_mark.sender_site_live_neighbours,
        "marked_site_starts_a_detached_part": detached,
    }
    if stub is not None:
        reading["marked_first_signature_difference_from_unmarked_stub"] = first_change(
            [r.own_signature for r in marked], [r.own_signature for r in stub]
        )
        reading["rounds_in_common_with_unmarked_stub"] = min(len(marked), len(stub))
    if detached:
        assert reading["first_receiver_own_signature_difference"] is None
        assert reading["first_sender_own_signature_difference"] == after + 1
    return reading


def independent_mechanism(smoke=False):
    from growth import grow, start

    reflected = {r["B"]: r for r in json.loads((RECORD / "reflect.json").read_text())}
    roster = list(reflected) if not smoke else [TWO_KNOT]
    source = {}
    for sender in roster:
        trace = grow(SWITCH_RECEIVER, sender, 3, "CAP-3")
        activity = [[number, owe - held] for number, rnd in enumerate(trace, 1)
                    if (holdings := rnd.sender_site_owed_and_held) is not None
                    for owe, held in [holdings]]
        assert activity == reflected[sender]["site: round and owe less holds while a member"]
        first = departure([r.own_births for r in trace])
        assert first == reflected[sender]["switch round"]
        source[sender] = {"site_owed_held_live_neighbours": [list(r.sender_site_owed_and_held) + [r.sender_site_live_neighbours]
                                                            for r in trace if r.sender_site_owed_and_held is not None],
                          "receiver_first_leaves_r_plus_two": first, "rounds": len(trace)}
    assert start("copier") == start(TWO_KNOT)

    interventions = {}
    controls = {(r["B"], r["t0"]): r for r in rows(INPUTS[1])
                if r["reading"] == "swap" and r["A"] == "n3:g7:122@0"}
    stub = grow(SWITCH_RECEIVER, STUB, 3, "CAP-3")
    senders = (TWO_KNOT,) if smoke else (ONE_KNOT, TWO_KNOT, STUB)
    for sender in senders:
        unmarked = grow(SWITCH_RECEIVER, sender, 3, "CAP-3")
        interventions[sender] = []
        for after in ((2, 3) if smoke else range(9)):
            marked = grow(SWITCH_RECEIVER, sender, 3, "CAP-3", mark_after=after)
            reading = mark_reading(unmarked, marked, after, stub if sender == TWO_KNOT else None)
            archived = controls[sender, after]
            assert reading["first_receiver_own_signature_difference"] == archived["heard"]
            assert reading["rounds_in_common"] == archived["rounds"]
            interventions[sender].append(reading)

    cap_marks = {}
    for cap in ((7,) if smoke else range(3, 8)):
        receiver = f"tri:{cap - 2}22@0"
        law = f"CAP-{cap}"
        unmarked = grow(receiver, TWO_KNOT, 3, law)
        unmarked_stub = grow(receiver, STUB, 3, law)
        cap_marks[cap] = [mark_reading(unmarked, grow(receiver, TWO_KNOT, 3, law, mark_after=after), after,
                                      unmarked_stub)
                          for after in (2, 3)]
    return {"reflection_by_sender": source, "canonical_d3_cap3_marks": interventions,
            "rule_three_mutually_sharing_knots_d3_boundary": cap_marks}


def audit():
    rule = rule_reading(rows(INPUTS[0]))
    controls = control_reading(rows(INPUTS[1]), rule)
    roster, senders = extended_senders(rows(INPUTS[2]))
    reflection = reflection_reading(json.loads((RECORD / INPUTS[3]).read_text()), roster)
    return {"inputs_sha256": {name: sha256((RECORD / name).read_bytes()).hexdigest() for name in INPUTS},
            "predecessor_sha256": sha256(PREDECESSOR.read_bytes()).hexdigest(),
            "rule": rule, "controls": controls, "extended_senders": senders, "reflection": reflection,
            "independent_mechanism": independent_mechanism()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Time the raw decode and checks on a small sample")
    parser.add_argument("--mechanism-smoke", action="store_true", help="Time two marked rounds and the last cap")
    args = parser.parse_args()
    begin = perf_counter()
    assert first_change([3, 4], [3, 4, 5]) is None
    assert first_change([3, 10, 5], [3, 4, 5]) == 2
    assert departure([3, 4, 8]) == 3
    assert alternating_short_after([0, 0, 1, 0, 1], 2)
    assert not alternating_short_after([0, 0, 1, 0, 0], 2)
    assert alternating_short_after([0, 0], 2) is None
    if args.smoke:
        comparison(rows(INPUTS[0], 1)[0])
        assert rows(INPUTS[1], 1)[0]["rounds"] == 16
        assert departure(rows(INPUTS[2], 1)[0]["own births"]) is None
        assert len(rows(INPUTS[4], 1)[0]["by sender"]) == len(SENDERS)
        print(f"Raw recount smoke {perf_counter() - begin:.6f} seconds")
        return
    if args.mechanism_smoke:
        independent_mechanism(smoke=True)
        print(f"Independent growth smoke {perf_counter() - begin:.6f} seconds")
        return
    result = audit()
    (HERE / "controls_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Controls audit complete in {perf_counter() - begin:.6f} seconds")


if __name__ == "__main__":
    main()
