"""Recount the recorded pulses and trace the strike, the payments, and a refund.

Only the shared round engine is used for growth. The paired comparisons,
interventions, and the check of the joins owed to the new offshoot are
implemented here. `--smoke` reads one case per start and mark round using the
same replay horizons as the full run.
"""

import argparse
from collections import Counter, defaultdict
from gzip import open as gzip_open
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENGINE = (
    ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
    / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"
)
sys.path.insert(0, str(ENGINE))
import eng


READINGS = ("name", "sig0", "sig1")
LAW = eng.Law("ORD", "CANCEL-WAIT", None, "nae")
CHAIN_STARTS = {"two-touching", "chain3"}
BARE_RINGS = {"ring5-bare", "ring7-bare"}
KNOT_LIMIT = 20_000


def ring(length, loose):
    return [
        [(knot - 1) % length, knot, *range(length + knot * loose, length + (knot + 1) * loose)]
        for knot in range(length)
    ]


STARTS = {
    "two-touching": [[0, 1, 2], [0, 3, 4]],
    "chain3": [[0, 1, 2], [1, 3, 4], [3, 5, 6]],
    "ring5-bare": ring(5, 2),
    "ring7-bare": ring(7, 2),
    "ring5-eddy": ring(5, 3),
    "generator7": [
        [0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14],
        [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22],
        [5, 8, 23, 24],
    ],
}


def records():
    panels = defaultdict(dict)
    with gzip_open(HERE.parent / "runs.jsonl.gz", "rt") as source:
        for line in source:
            row = json.loads(line)
            if row.get("change") in {"made", "pulse"} and row["knot law"] == "nae":
                panels[row["start"], row["round"]][row["change"]] = row
    return panels


def index_cases(panel):
    pulse, mark = panel["pulse"], panel["made"]
    assert len(pulse["marks"]) == pulse["marked"] == mark["marked"]
    assert pulse["base counts"] == mark["base counts"]
    by_knot = {case["knot"]: case for case in mark["marks"]}
    assert set(by_knot) == {case["knot"] for case in pulse["marks"]}
    return [(case, by_knot[case["knot"]]) for case in pulse["marks"]]


def damage(pair):
    return sum(pair)


def census(panel):
    result = {
        "knots_made": panel["pulse"]["made"],
        "pulse_cases": len(panel["pulse"]["marks"]),
        "eligible_for_dies_out": 0,
        "final_round": Counter(),
        "case_stop": Counter(),
        "barred_distinctions": Counter(),
        "dies_out_by_reading": dict.fromkeys(READINGS, 0),
        "nonzero_in_every_round_of_final_half": dict.fromkeys(READINGS, 0),
        "pulse_vs_mark_smaller_equal_larger_damage_at_last_shared_round": {
            reading: Counter() for reading in READINGS
        },
        "pulse_vs_mark_different_birth_counts_at_last_shared_round": 0,
        "pulse_vs_mark_different_birth_counts_in_any_shared_round_after_strike": 0,
        "pulse_vs_mark_different_damage_in_any_shared_round_after_strike": dict.fromkeys(READINGS, 0),
    }
    for pulse, mark in index_cases(panel):
        rows = pulse["rows"]
        last = rows[-1]
        result["final_round"][last["round"]] += 1
        result["case_stop"][pulse["stop"] or "round_limit"] += 1
        result["barred_distinctions"][pulse["struck"]] += 1
        eligible = len(rows) >= 8
        result["eligible_for_dies_out"] += eligible
        pairs = list(zip(rows, mark["rows"]))
        first_pulse, first_mark = pairs[0]
        assert first_pulse == first_mark
        assert all(a["round"] == b["round"] and a["n"] == b["n"] for a, b in pairs)
        assert all(row["n"] == panel["pulse"]["base counts"][row["round"] - 1] for row in rows)
        pulse_last, mark_last = pairs[-1]
        result["pulse_vs_mark_different_birth_counts_at_last_shared_round"] += (
            pulse_last["n'"] != mark_last["n'"]
        )
        result["pulse_vs_mark_different_birth_counts_in_any_shared_round_after_strike"] += any(
            a["n'"] != b["n'"] for a, b in pairs[1:]
        )
        for reading in READINGS:
            tail = [damage(row[reading]) for row in rows[len(rows) // 2:]]
            dies = eligible and not any(tail)
            assert dies == (pulse["verdicts"][reading] == "dies out")
            result["dies_out_by_reading"][reading] += dies
            result["nonzero_in_every_round_of_final_half"][reading] += all(tail)
            last_pulse_damage, last_mark_damage = damage(pulse_last[reading]), damage(mark_last[reading])
            comparison = (
                "smaller" if last_pulse_damage < last_mark_damage else
                "larger" if last_pulse_damage > last_mark_damage else "equal"
            )
            result["pulse_vs_mark_smaller_equal_larger_damage_at_last_shared_round"][reading][comparison] += 1
            result["pulse_vs_mark_different_damage_in_any_shared_round_after_strike"][reading] += any(
                damage(a[reading]) != damage(b[reading]) for a, b in pairs[1:]
            )
    return result


class Replay:
    def __init__(self, stars, identities):
        self.state = eng.from_stars(stars)
        self.guard = eng.Guard(100)
        self.identities = identities
        self.names = list(range(len(stars)))
        self.local = [("start", 0, 0, len(knot)) for knot in stars]

    def fork(self):
        copy = object.__new__(Replay)
        copy.state = self.state.copy()
        copy.guard = eng.Guard(100)
        copy.identities = self.identities
        copy.names = self.names.copy()
        copy.local = self.local.copy()
        return copy

    def add_distinction(self, knot):
        added = self.state.n_distinctions
        self.state.places[knot].append(added)
        self.state.holders.append([knot])
        self.state.barred.append(False)
        self.state.maker.append(knot)
        kind, parents, fresh, places = self.local[knot]
        self.local[knot] = kind, parents, fresh, places + 1
        # The basis is not read in a round under not-all-equal.
        return added

    def advance(self):
        read = eng.play_round(self.state, LAW, self.guard)
        assert not read["short"]
        assert read["births"]
        readings = {key: Counter() for key in READINGS}
        same_parents = Counter()
        for birth in read["births"]:
            knot = birth["id"]
            assert knot == len(self.names) == len(self.local)
            parents = birth["parents"]
            kind = birth["kind"]
            origin = kind, tuple(sorted(self.names[parent] for parent in parents))
            name = self.identities.setdefault(
                (origin, same_parents[origin]), self.state.n_start + len(self.identities),
            )
            same_parents[origin] += 1
            signature = kind, len(parents), len(birth["fresh"]), len(self.state.places[knot])
            self.names.append(name)
            self.local.append(signature)
            readings["name"][name, *signature[2:]] += 1
            readings["sig0"][signature] += 1
            readings["sig1"][signature, tuple(sorted(self.local[parent] for parent in parents))] += 1
        return read, readings


def unmatched(reference, changed):
    differences = {}
    for reading in READINGS:
        base, test = reference[reading], changed[reading]
        matched = sum((base & test).values())
        differences[reading] = [sum(test.values()) - matched, sum(base.values()) - matched]
    return differences


def birth_key(birth):
    return birth["kind"], birth["parents"], birth["off_index"]


def strike_and_refund(baseline_births, marked, marked_round, target, added):
    base = {birth_key(birth): birth for birth in baseline_births}
    marked_births = {birth_key(birth): birth for birth in marked_round["births"]}
    assert set(base) < set(marked_births)
    extra_key, = set(marked_births) - set(base)
    extra = marked_births[extra_key]
    offshoot = extra["id"]
    assert extra["kind"] == "offshoot" and extra["parents"] == (target,)
    assert extra["inputs"] == [added]
    assert marked.state.holders[added] == [target, offshoot]
    assert not marked.state.usable(target)

    struck = marked.fork()
    barred = struck.state.usable(offshoot)
    assert barred == extra["fresh"] and barred
    for distinction in barred:
        struck.state.barred[distinction] = True

    refund = struck.fork()
    common, siblings = {}, []
    extra_payments = {}
    for key, before in base.items():
        after = marked_births[key]
        common[before["id"]] = after["id"]
        assert before["inputs"] == after["inputs"]
        is_sibling = target in after["parents"]
        assert after["D"] - before["D"] == int(is_sibling)
        for birth in (before, after):
            assert len(birth["fresh"]) == max(birth["D"], 3 - len(birth["parents"]), 1)
        if is_sibling:
            siblings.append({
                "knot": after["id"], "kind": after["kind"], "parents": after["parents"],
                "demand_without_and_with_mark": [before["D"], after["D"]],
                "fresh_without_and_with_mark": [before["f"], after["f"]],
            })
        surplus = after["fresh"][before["f"]:]
        if surplus:
            assert is_sibling and len(surplus) == 1
            extra_payments[after["id"]] = surplus[0]
        for distinction in surplus:
            refund.state.barred[distinction] = True

    expected = {tuple(sorted((offshoot, sibling["knot"]))) for sibling in siblings}
    assert expected == {group for group in marked_round["demand"].groups if offshoot in group}
    assert marked.state.usable(offshoot) and not struck.state.usable(offshoot)
    return struck, refund, common, extra_payments, expected, {
        "added_distinction": added,
        "new_offshoot": offshoot,
        "barred_distinctions": barred,
        "shared_with_marked_knot_after_strike": marked.state.holders[added],
        "joins_due_with_struck_offshoot": sorted(expected),
        "siblings_owed_to_join": siblings,
    }


def check_record(row, reference, changed, difference):
    assert row["n"] == sum(reference["sig0"].values())
    assert row["n'"] == sum(changed["sig0"].values())
    assert all(row[reading] == difference[reading] for reading in READINGS)


def trace_case(snap, base_counts, first_base, second_base, pulse_record, mark_record, stop_round):
    target = pulse_record["knot"]
    marked = snap.fork()
    added = marked.add_distinction(target)
    marked_round, first = marked.advance()
    first_round = marked.state.round
    struck, refund, common, payments, expected, opportunity = strike_and_refund(
        first_base, marked, marked_round, target, added,
    )
    next_base_keys = {
        (birth["kind"], tuple(sorted(common[parent] for parent in birth["parents"])), birth["off_index"])
        for birth in second_base
    }
    pulse_rows = {row["round"]: row for row in pulse_record["rows"]}
    mark_rows = {row["round"]: row for row in mark_record["rows"]}
    raw_checked = Counter()
    comparisons = []
    for current in range(first_round, stop_round + 1):
        reference = base_counts[current]
        if current == first_round:
            readings = {"mark": first, "pulse": first, "refund": first}
        else:
            readings = {}
            for label, replay in (("mark", marked), ("pulse", struck), ("refund", refund)):
                read, readings[label] = replay.advance()
                if current == first_round + 1:
                    offshoot = opportunity["new_offshoot"]
                    offered = {group for group in read["groups"] if offshoot in group}
                    made = {birth["parents"] for birth in read["births"] if offshoot in birth["parents"]}
                    if label == "mark":
                        assert offered == made == expected
                    else:
                        assert not offered and not made
                        actual = {birth_key(birth): birth for birth in read["births"]}
                        assert next_base_keys <= set(actual)
                        surplus_births = [actual[key] for key in set(actual) - next_base_keys]
                        if label == "pulse":
                            assert len(surplus_births) == len(payments)
                            assert {
                                (birth["parents"][0], birth["inputs"][0]) for birth in surplus_births
                                if birth["kind"] == "offshoot"
                            } == set(payments.items())
                            opportunity["offshoots_spending_advance_payments"] = [
                                {"id": birth["id"], "parent": birth["parents"][0], "input": birth["inputs"][0]}
                                for birth in sorted(surplus_births, key=lambda birth: birth["id"])
                            ]
                        else:
                            assert not surplus_births
        from_base = {label: unmatched(reference, reading) for label, reading in readings.items()}
        direct = unmatched(readings["mark"], readings["pulse"])
        for label, rows in (("mark", mark_rows), ("pulse", pulse_rows)):
            if current in rows:
                check_record(rows[current], reference, readings[label], from_base[label])
                raw_checked[label] += 1
        comparisons.append({
            "round": current, "base_births": sum(reference["sig0"].values()),
            "births": {label: sum(reading["sig0"].values()) for label, reading in readings.items()},
            "damage_from_base": {
                label: {reading: damage(pair) for reading, pair in difference.items()}
                for label, difference in from_base.items()
            },
            "damage_from_mark_to_pulse": {reading: damage(pair) for reading, pair in direct.items()},
        })
        if any(replay.state.n_knots > KNOT_LIMIT for replay in (marked, struck, refund)):
            break
    assert len(comparisons) >= 3
    assert len(opportunity["barred_distinctions"]) == pulse_record["struck"]
    assert all(row["damage_from_base"]["refund"]["sig0"] == 0 for row in comparisons[1:])
    assert all(row["damage_from_base"]["refund"]["name"] == 0 for row in comparisons[1:])
    assert all(row["damage_from_base"]["refund"]["sig1"] == 0 for row in comparisons[2:])
    later_positive = [
        row["damage_from_base"]["pulse"]["sig1"] > 0 for row in comparisons[2:]
    ]
    opportunity["made_when_left_unstruck"] = len(expected)
    opportunity["made_when_struck"] = 0
    return {
        "marked_knot": target,
        "opportunity": opportunity,
        "raw_rows_checked": dict(raw_checked),
        "replay_last_round": comparisons[-1]["round"],
        "pulse_vs_mark_nonzero_in_every_compared_round_after_the_strike": {
            reading: all(row["damage_from_mark_to_pulse"][reading] > 0 for row in comparisons[1:])
            for reading in READINGS
        },
        "pulse_vs_base_sig1_nonzero_from_third_round": all(later_positive),
        "rounds": comparisons[:3] + comparisons[max(3, len(comparisons) - 4):],
    }


def summaries(traces):
    totals = Counter()
    for case in traces:
        opportunity = case["opportunity"]
        paid = Counter()
        for sibling in opportunity["siblings_owed_to_join"]:
            before, after = sibling["fresh_without_and_with_mark"]
            totals[f"{sibling['kind']}_siblings_owed_to_join"] += 1
            if after > before:
                paid[sibling["kind"]] += after - before
                totals[f"{sibling['kind']}_siblings_received_extra"] += 1
        if paid:
            totals["cases_with_extra_payment"] += 1
        for kind in paid:
            totals[f"cases_with_extra_payment_to_{kind}"] += 1
        totals["joins_due_with_struck_offshoot"] += len(opportunity["joins_due_with_struck_offshoot"])
        totals["struck_distinctions"] += len(opportunity["barred_distinctions"])
        totals["cases_with_nonzero_sig1_from_third_round"] += case["pulse_vs_base_sig1_nonzero_from_third_round"]
        totals["cases_with_no_initial_join_opportunity"] += not opportunity["joins_due_with_struck_offshoot"]
    return dict(totals)


def requested_horizon(start, intervention_round, rank, pulse, mark):
    last_shared = min(pulse["rows"][-1]["round"], mark["rows"][-1]["round"])
    if start in CHAIN_STARTS:
        return 32
    if start in BARE_RINGS:
        return 24 if rank == 0 else last_shared
    if rank == 0:
        return min(last_shared, 10)
    return intervention_round + 4


def replay_panel(start, panels, smoke):
    cases_by_round = {s: index_cases(panels[start, s]) for s in (2, 4)}
    if smoke:
        cases_by_round = {s: cases[:1] for s, cases in cases_by_round.items()}
    baseline = Replay(STARTS[start], {})
    horizons = {
        s: [requested_horizon(start, s, i, *pair) for i, pair in enumerate(cases)]
        for s, cases in cases_by_round.items()
    }
    base_counts, base_births, snaps = {}, {}, {}
    recorded_counts = panels[start, 2]["pulse"]["base counts"]
    assert recorded_counts == panels[start, 4]["pulse"]["base counts"]
    for current in range(1, max(max(values) for values in horizons.values()) + 1):
        record, base_counts[current] = baseline.advance()
        actual = len(record["births"])
        if current <= len(recorded_counts):
            assert actual == recorded_counts[current - 1]
        if current in cases_by_round:
            snaps[current] = baseline.fork()
        if current - 1 in cases_by_round or current - 2 in cases_by_round:
            base_births[current] = record["births"]
    panels_out = {}
    for s, cases in cases_by_round.items():
        traces = [
            trace_case(snaps[s], base_counts, base_births[s + 1], base_births[s + 2], pulse, mark, horizon)
            for (pulse, mark), horizon in zip(cases, horizons[s])
        ]
        panels_out[str(s)] = {
            "census": census(panels[start, s]), "traces": traces, "trace_totals": summaries(traces),
        }
    return {
        "baseline_rounds_checked": min(len(base_counts), len(recorded_counts)),
        "baseline_birth_counts": [sum(row["sig0"].values()) for row in base_counts.values()],
        "round_marked": panels_out,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--start", choices=STARTS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    panels = records()
    starts = (args.start,) if args.start else STARTS
    replays = {start: replay_panel(start, panels, args.smoke) for start in starts}
    all_traces = [
        trace for replay in replays.values() for panel in replay["round_marked"].values()
        for trace in panel["traces"]
    ]
    result = {
        "growth": "Ordinary count, no taking, not-all-equal, with waiting available. No knot was short.",
        "refund": "Bar the same offshoot's fresh distinctions, plus exactly the extra fresh distinctions each sibling received.",
        "comparison_coverage": (
            "Recount every recorded case. Replay two touching knots and the three-knot row through round 32 and "
            "the bare rings through round 16, extending the first case per mark round per bare ring through round 24. "
            "On the eddy and the generator, replay through four rounds after the mark, extending the first case "
            "per mark round per start through round 10. Stop a replay after the first round above 20,000 knots."
        ),
        "trace_count": len(all_traces),
        "trace_horizons": Counter(trace["replay_last_round"] for trace in all_traces),
        "trace_totals": summaries(all_traces),
        "starts": replays,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({field: result[field] for field in ("trace_count", "trace_horizons", "trace_totals")}))


if __name__ == "__main__":
    main()
