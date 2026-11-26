"""Regrow every reported Ticket C confirmation from its registered start.

The confirmation records identify cases for replay and provide comparison
targets. They do not supply any of the replayed holdings or birth records.
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from gzip import open as gzip_open
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from random import Random

import networkx as nx

from c_growth import (
    Law,
    descend,
    failing_knots,
    form,
    groups,
    grow,
    initial_state,
    roster,
    same_form,
)


ROOT = Path(__file__).resolve().parents[3]
TICKET = "MADE-COPIER-20261125-001C"
ARTIFACTS = ROOT / "artifacts" / TICKET / (TICKET + "-E001_copier_by_sampling")
STARTS = ROOT / "research" / TICKET / "starts_c.json"


def pairs_at(state, seed, every_pair):
    read = roster(state)
    part_of = {name: part for part in read.parts for name in part}
    part_classes = nx.Graph()
    part_classes.add_nodes_from(read.parts)
    for holders in state.holders:
        parts = {part_of[name] for name in holders if name in part_of}
        part_classes.add_edges_from(combinations(parts, 2))
    class_of = {part: i for i, group in enumerate(nx.connected_components(part_classes)) for part in group}
    pairs = [
        (x, y) for x in read.parts if all(state.knots[name].made for name in x)
        for y in read.parts if class_of[x] != class_of[y]
    ]
    if len(pairs) > 8 and not every_pair:
        pairs = Random(f"{seed}|P|{state.round}").sample(pairs, 8)
    return sorted(pairs)


def met_parts(read, labels):
    return [
        part for part in read.parts
        if any(labels[name] & 1 for name in part) and any(labels[name] & 2 for name in part)
    ]


def qualifying_parts(state, read, labels, y_form, s):
    return [
        part for part in read.parts
        if all(labels[name] == 1 for name in part)
        and any(state.knots[name].made > s for name in part)
        and same_form(y_form, form(read, part))
    ]


def birth_record(state, name):
    knot = state.knots[name]
    return {
        "knot": name, "birth_round": knot.made, "kind": knot.kind, "parents": knot.parents,
        "places": knot.places, "takes": knot.takes, "extra_take": knot.extra_take,
        "fresh": knot.fresh,
    }


def form_record(state, read, part):
    graph = form(read, part)
    return {
        "members": [
            birth_record(state, name) | {
                "usable_loose": read.usable[name],
                "barred_loose": read.barred_loose.get(name, ()),
            } for name in part
        ],
        "maximal_met_sets": sorted(
            tuple(sorted(graph[node])) for node, data in graph.nodes(data=True)
            if data["label"] == ("met set",)
        ),
    }


def ancestors(state, name):
    result = set()
    to_check = list(state.knots[name].parents)
    while to_check:
        parent = to_check.pop()
        if parent not in result:
            result.add(parent)
            to_check.extend(state.knots[parent].parents)
    return result


def support_record(state, read, labels):
    supports = []
    restricted = [nx.Graph(), nx.Graph()]
    for graph in restricted:
        graph.add_nodes_from(read.usable)
    for common, members in sorted(read.met_sets.items()):
        made = state.knots[common].made > 0
        restricted[made].add_edges_from(combinations(members, 2))
        connections = []
        has_ancestral_connection = False
        for first in sorted(members):
            if not labels[first] & 1:
                continue
            for second in sorted(members - {first}):
                if not labels[second] & 2:
                    continue
                common_places = set(state.knots[common].places)
                connections.append({
                    "X_member": birth_record(state, first),
                    "Y_member": birth_record(state, second),
                    "shared_with_X_member": sorted(common_places.intersection(state.knots[first].places)),
                    "shared_with_Y_member": sorted(common_places.intersection(state.knots[second].places)),
                })
                if common in ancestors(state, first) & ancestors(state, second):
                    has_ancestral_connection = True
        if connections:
            supports.append({
                "common_knot": birth_record(state, common),
                "met_members": sorted(members),
                "first_connection": connections[0],
                "connection_count": len(connections),
                "ancestor_of_both_members_in_some_connection": has_ancestral_connection,
            })
    connection = {
        kind: any(any(labels[name] & 1 for name in part) and any(labels[name] & 2 for name in part)
                  for part in nx.connected_components(graph))
        for kind, graph in zip(("start_knots_only", "made_knots_only"), restricted)
    }
    return connection | {"common_knots_with_direct_connections": supports}


def run_case(case, start, source):
    seed, law = case["seed"], Law.from_record(case["law"])
    x, y, s = tuple(case["X"]), tuple(case["Y"]), case["s"]
    states, stop = grow(initial_state(start), law, seed)
    after_s = states[s]
    read_s = roster(after_s)
    x_form, y_form = form(read_s, x), form(read_s, y)
    assert not same_form(x_form, y_form)
    assert (x, y) in pairs_at(after_s, seed, every_pair=case["run"] == "R6")
    raw_pair = next(p for p in source["pairs"] if p["X"] == list(x) and p["Y"] == list(y) and p["s"] == s)
    meeting = first = first_after = None
    for state in states[s+1:]:
        labels = descend(state, x, y, s)
        read = roster(state)
        together = met_parts(read, labels)
        if meeting is None and together:
            meeting = state.round
            support = support_record(state, read, labels)
        matches = qualifying_parts(state, read, labels, y_form, s)
        if len(matches) >= 2 and first is None:
            first = state.round
        if len(matches) >= 2 and meeting is not None and first_after is None:
            first_after = state.round
            reading = [form_record(state, read, part) for part in matches]
    failed = failing_knots(states[-1], law)
    assert (len(states[-1].knots), states[-1].round, stop) == (source["knots"], source["rounds"], source["stop"])
    assert (meeting, first, first_after) == (raw_pair["meet"], raw_pair["first"]["form"], raw_pair["after"]["form"])
    assert not failed and not case["growth_has_failing_knot"]
    direct = support["common_knots_with_direct_connections"]
    assert any(row["common_knot"]["birth_round"] == 0 for row in direct)
    assert support["made_knots_only"] == case["made_questions"]["meeting through made knots"]
    assert all(after_s.knots[name].made > 0 for name in x+y)
    return {
        "run": case["run"], "start": case["start"], "seed": seed, "law": case["law"], "X": x, "Y": y,
        "pair_round": s, "meeting_round": meeting, "first_form_round": first, "first_form_at_or_after_meeting": first_after,
        "registered_pair_reselected": True, "K1_K2_K3_failures": failed, "final_knot_count": len(states[-1].knots),
        "X_form": form_record(after_s, read_s, x), "Y_form": form_record(after_s, read_s, y),
        "qualifying_X_only_parts": reading, "first_meeting_support": support,
    }, x_form, y_form


def branch_record(states, x, y, s, y_form, masked):
    timeline = []
    for state in states[1:]:
        read = roster(state)
        labels = descend(state, x, y, s)
        matches = qualifying_parts(state, read, labels, y_form, s)
        row = {
            "round": state.round,
            "one_part": met_parts(read, labels),
            "qualifying_X_only_parts": [form_record(state, read, part) for part in matches],
        }
        if state.round <= 4:
            read_for_growth = roster(state, mask_labels=labels) if masked else read
            offered = groups(read_for_growth)
            owes = Counter(name for group in offered for name in group)
            row.update({
                "births": [birth_record(state, name) | {"descent": labels[name]} for name, knot in enumerate(state.knots)
                           if knot.made == state.round],
                "short_before_next_round": sorted(name for name, n in owes.items() if n > len(read.usable[name])),
                "groups_before_next_round": offered,
                "live_usable_loose_counts": {name: len(loose) for name, loose in sorted(read.usable.items())},
                "barred_distinctions": sorted(state.barred),
                "retired_knots": sorted(state.retired),
            })
        timeline.append(row)
    return timeline


def hand_check(case, start):
    law = Law.from_record(case["law"])
    seed, s = case["seed"], case["s"]
    x, y = tuple(case["X"]), tuple(case["Y"])
    states, _ = grow(initial_state(start), law, seed)
    y_form = form(roster(states[s]), y)
    checks = {}
    for check in ("same seed to expose the changed round", "registered stage 2 index 110"):
        arms = {}
        for kind, barred, mask, fully in (
            ("BN", (), False, False), ("BY", y, False, False),
            ("BM", (), True, False), ("BT", (), True, True),
        ):
            branch_seed = seed if check.startswith("same seed") else f"{seed}|{kind}|{s}|110"
            branch, stop = grow(states[s], law, branch_seed, x=x, y=y, barred=barred,
                                mask=mask, fully_masked=fully)
            trace = branch_record(branch, x, y, s, y_form, masked=mask)
            index = next((row["round"] for row in trace if row["one_part"]), None)
            arms[kind] = {
                "seed": branch_seed, "stop": stop, "meeting_round": index,
                "two_X_only_parts_at": [row["round"] for row in trace if len(row["qualifying_X_only_parts"]) >= 2],
                "rounds": trace,
            }
        assert arms["BN"]["two_X_only_parts_at"] and arms["BN"]["meeting_round"] is not None
        assert all(not arms[kind]["two_X_only_parts_at"] for kind in ("BY", "BM", "BT"))
        checks[check] = arms
    diagnostic = checks["same seed to expose the changed round"]
    assert diagnostic["BT"]["meeting_round"] is not None
    assert diagnostic["BN"]["rounds"][0]["births"] == diagnostic["BM"]["rounds"][0]["births"]
    assert diagnostic["BN"]["rounds"][0]["short_before_next_round"] == [6, 7, 8, 11, 12]
    assert not diagnostic["BM"]["rounds"][0]["short_before_next_round"]
    return checks


def read_growth_records(cases):
    needed = defaultdict(set)
    for case in cases:
        needed[case["run"]].add(case["seed"])
    rows = {}
    for run, seeds in needed.items():
        with gzip_open(ARTIFACTS / f"{run}.jsonl.gz", "rt") as stream:
            for line in stream:
                record = loads(line)
                seed = record.get("seed")
                if seed in seeds:
                    rows[run, seed] = record
                    seeds.remove(seed)
                    if not seeds:
                        break
        assert not seeds, (run, seeds)
    return rows


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--first", type=int, help="time a prefix of the confirmation list")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    starts = {row["id"]: row for row in loads(STARTS.read_text())["starts"]}
    cases = [
        case for name in ("R3", "Rcond")
        for case in loads((ARTIFACTS / f"{name}.json").read_text())["confirmed_claimed"]
    ]
    if args.first is not None:
        cases = cases[:args.first]
    sources = read_growth_records(cases)
    records = []
    form_classes = defaultdict(list)
    for case in cases:
        record, x_form, y_form = run_case(case, starts[case["start"]], sources[case["run"], case["seed"]])
        records.append(record)
        classes = form_classes[case["law"]]
        found = next((entry for entry in classes if same_form(entry[0], x_form)), None)
        if found is None:
            classes.append((x_form, [y_form]))
        elif not any(same_form(known, y_form) for known in found[1]):
            found[1].append(y_form)
    summary = {
        "confirmed_cases_regrown": len(records),
        "distinct_growths_regrown": len({record["seed"] for record in records}),
        "distinct_starts_regrown": len({record["start"] for record in records}),
        "cases_with_start_only_connection": sum(record["first_meeting_support"]["start_knots_only"] for record in records),
        "cases_with_made_only_connection": sum(record["first_meeting_support"]["made_knots_only"] for record in records),
        "first_pattern_forms_with_multiple_Y_forms": sum(
            len(y_forms) > 1 for classes in form_classes.values() for _, y_forms in classes
        ),
        "first_pattern_forms_by_law": {
            law: [len(y_forms) for _, y_forms in classes] for law, classes in form_classes.items()
        },
    }
    output = summary | {"records": records}
    if args.first is None:
        selected = next(case for case in cases if case["start"] == "n3-g6-223")
        output["hand_check"] = hand_check(selected, starts[selected["start"]])
        assert len(records) == 17
        assert summary["cases_with_start_only_connection"] == 17
        assert summary["cases_with_made_only_connection"] == 2
        assert summary["first_pattern_forms_with_multiple_Y_forms"] == 0
    if args.output:
        args.output.write_text(dumps(output, indent=2, sort_keys=True) + "\n")
    print(dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
