"""Reconstruct all powered moves from the frozen rules and submitted holdings."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
DESIGN = ROOT / "research" / HERE.parent.name
RAW_SHA = "cce06163980a9661d97f30847614398e6acdd26eb22b358f686eebc0e63f59df"
LAWS = ("parity", "nae")
CONDITIONS = ("intact", "interrupted", "read_disabled")
NAMINGS = ("original", "reverse", "shuffle")
BANKS = ("offer", "stage", "receipt", "memory", "donor_bundle")
ROLES = ("source", "witness", "receiver")
ONE = ("10010", "00110")
TWO = ("10010", "01010", "10001", "00101")


def unpack(value):
    number = int(value, 16)
    assert number >= 0
    return frozenset(i for i in range(number.bit_length()) if number & (1 << i))


def bits(ones, names):
    return "".join("1" if name in ones else "0" for name in names)


def allowed(count, width, law):
    return count % 2 == 0 if law == "parity" else 0 < count < width


def owners(stars):
    found = defaultdict(set)
    for holder, row in enumerate(stars):
        assert len(set(row)) == len(row) and len(row) >= 3
        for name in row:
            found[name].add(holder)
    assert all(len(row) in (1, 2) for row in found.values())
    return found


def reached_stages(original, board):
    stages = [original]
    assert len(board["cuts"]) == 2
    for age, cut in enumerate(board["cuts"], 1):
        assert cut["age"] == age and cut["status"] == "extend" and cut["old_assignments_extend"]
        incidence = owners(stages[-1])
        loose = {name for name, row in incidence.items() if len(row) == 1}
        fresh = set()
        births = []
        for birth in cut["births"]:
            paid, grant = birth["consumed_names"], birth["fresh_names"]
            assert birth["holder"] == len(stages[-1]) + len(births)
            assert len(set(birth["parents"])) == 2
            assert len(grant) == birth["grant"] == max(1, birth["demand"])
            assert birth["input_projection"] == [0, 1, 2, 3]
            for holder, name in zip(birth["parents"], paid, strict=True):
                assert incidence[name] == {holder}
                loose.remove(name)
            for name in grant:
                assert name not in incidence and name not in fresh
                fresh.add(name)
            births.append(paid + grant)
        assert not loose
        stages.append(stages[-1] + births)
    assert stages[-1][len(original):] == board["newborn_stars"]
    return stages


def check_interruption(before, after):
    old, new = [side["devices_in_c8_u8_order"] for side in (before, after)]
    assert before["source_p"] == after["source_p"] == old[0]["source"] == new[1]["source"]
    assert old[1]["source"] == new[0]["source"] != old[0]["source"]
    edit, = after["edits"]
    assert not before["edits"] and (edit["site"], edit["size"]) == (8, 9)
    expected = [set(row) for row in before["stars"]]
    for i in range(2):
        baseline, crossed, other = old[i], new[i], old[1 - i]
        for key in ("receiver", "witness", "receipt", "memory"):
            assert baseline[key] == crossed[key]
        for key in ("source", "offer", "stage", "donor_bundle"):
            assert crossed[key] == other[key]
        holder = baseline["witness"]
        expected[holder].difference_update(baseline["donor_bundle"])
        expected[holder].update(crossed["donor_bundle"])
    assert expected == list(map(set, after["stars"]))


def check_enrollment(stars, devices):
    for device, width in zip(devices, (12, 14), strict=True):
        s, w, r = (device[role] for role in ROLES)
        assert len(stars[w]) == width and set(stars[s]).isdisjoint(stars[r])
        donor = sorted(set(stars[s]) & set(stars[w]))
        incoming = sorted(set(stars[r]) & set(stars[w]))
        assert len(donor) == 9 and len(incoming) == width - 9
        assert donor == device["donor_bundle"] and donor[:3] == device["offer"]
        assert donor[3:5] == device["stage"] and incoming[:3] == device["receipt"]
        first, second = device["memory"]
        incidence = owners(stars)
        other, = incidence[first] - {r}
        assert other != w and incidence[first] == incidence[second] == {r, other}
        assert sorted(set(stars[r]) & set(stars[other]))[:2] == device["memory"]


def transported(board, stars, devices, initial, naming, reverse):
    hm, dm = (board["recodings"][naming][field] for field in (
        "old_holder_to_new", "old_distinction_to_new"
    ))
    expected_h = list(range(len(stars)))
    expected_d = list(range(max(name for row in stars for name in row) + 1))
    if naming == "reverse":
        expected_h.reverse()
        expected_d.reverse()
    elif naming == "shuffle":
        generator = Random(202611220305)
        generator.shuffle(expected_h)
        generator.shuffle(expected_d)
    assert hm == expected_h and dm == expected_d
    renamed_stars = [None] * len(stars)
    for original_id, row in enumerate(stars):
        renamed_stars[hm[original_id]] = tuple(dm[name] for name in row)
    moved = []
    for device in devices:
        mapped = {key: hm[device[key]] for key in ROLES}
        for key in BANKS:
            names = device[key][::-1] if reverse and key in ("offer", "receipt") else device[key]
            mapped[key] = tuple(dm[name] for name in names)
        moved.append(mapped)
    return renamed_stars, moved, frozenset(dm[x] for x in initial), hm


@dataclass(frozen=True)
class Rule:
    actor: int
    action: str
    sensing: tuple
    pattern: str
    swaps: tuple

    def enabled(self, word):
        return bits(word, self.sensing) == self.pattern

    def apply(self, word):
        changed = set(word)
        for a, b in self.swaps:
            if (a in word) != (b in word):
                changed.symmetric_difference_update((a, b))
        assert changed != word
        return frozenset(changed)


def relay_rules(device, conditional):
    sense = device["offer"] + device["stage"] + device["receipt"]
    first, middle, end = device["receipt"]
    relay = device["witness"]
    stage = device["stage"]
    yield Rule(relay, "issue_end", sense, "01010100", ((first, end), stage))
    if conditional:
        yield Rule(relay, "issue_mid", sense, "00110100", ((first, middle), stage))
        yield Rule(relay, "issue_end", sense, "00101100", ((first, end),))
    else:
        yield Rule(relay, "issue_end", sense, "00110100", ((first, end), stage))


def program(device, offer, conditional):
    start, middle, end = device["offer"]
    yield Rule(device["source"], "offer", device["offer"], "100",
               ((start, (middle, end)[offer - 1]),))
    yield from relay_rules(device, conditional)
    receipt = device["receipt"]
    yield Rule(device["receiver"], "acknowledge", receipt + device["memory"], "01010",
               ((receipt[0], receipt[1]), device["memory"]))


def check_local_rules(rules, stars):
    incidence = owners(stars)
    for rule in rules:
        assert len(rule.sensing) == len(rule.pattern) and len(set(rule.sensing)) == len(rule.sensing)
        assert set(rule.sensing) <= set(stars[rule.actor])
        marks = [name for pair in rule.swaps for name in pair]
        assert len(marks) == len(set(marks)) and set(marks) <= set(rule.sensing)
        for a, b in rule.swaps:
            assert incidence[a] == incidence[b] and rule.actor in incidence[a]


def capture_table(stars, device, law):
    holder = device["witness"]
    support = stars[holder]
    width = len(support)
    index = {name: i for i, name in enumerate(support)}
    forgetting = [set() for _ in support]
    matches = Counter()
    moves = []
    for conditional in (False, True):
        for rule in relay_rules(device, conditional):
            sense = sum(1 << index[name] for name in rule.sensing)
            required = sum(1 << index[name] for name, bit in zip(rule.sensing, rule.pattern, strict=True) if bit == "1")
            flipped = sum(1 << index[name] for pair in rule.swaps for name in pair)
            assert flipped & sense == flipped
            assert all(((required >> index[a]) ^ (required >> index[b])) & 1 for a, b in rule.swaps)
            moves.append((conditional, rule.action, sense, required, flipped))
    count = 0
    for word in range(1 << width):
        if not allowed(word.bit_count(), width, law):
            continue
        count += 1
        for i, readings in enumerate(forgetting):
            readings.add(word & ~(1 << i))
        for condition, action, sense, required, changed in moves:
            if word & sense == required:
                assert allowed((word ^ changed).bit_count(), width, law)
                matches[f"{condition}-{action}"] += 1
    projections = [len(readings) for readings in forgetting]
    assert 0 < count < 1 << width and projections == [1 << (width - 1)] * width
    return {"holder": holder, "arity": width, "possible": 1 << width, "allowed": count,
            "after_single_forgetting": projections, "enabled_moves_by_read": dict(matches)}


def receiver_prefix(stages, device, word):
    holder = device["receiver"]
    marks = stages[0][holder]
    trace = []
    for stage in stages:
        incidence = owners(stage)
        local = {}
        observed = [[local.setdefault(peer, len(local)) for peer in sorted(incidence[name] - {holder})]
                    for name in marks]
        sample = {"values": bits(word, marks), "coholders_at_each_own_mark": observed}
        if not trace or sample != trace[-1]:
            trace.append(sample)
    return trace


def independent_graph(stars, rules, initial, law):
    assert initial <= owners(stars).keys()
    check_local_rules(rules, stars)
    supports = tuple(map(frozenset, stars))
    graph = {}
    pending = [initial]
    while pending:
        state = pending.pop()
        if state in graph:
            continue
        assert all(allowed(len(state & row), len(row), law) for row in supports)
        arcs = [(rule, rule.apply(state)) for rule in rules if rule.enabled(state)]
        assert len(arcs) == len(set(arcs))
        graph[state] = arcs
        pending.extend(target for _, target in arcs)
    return graph


def edge_signature(actor, action, swaps, target):
    return actor, action, tuple(map(tuple, swaps)), target


def compare_graph(graph, submitted, initial):
    known = {}
    for node in submitted:
        state = initial ^ unpack(node["delta_from_initial"])
        assert state not in known
        edges = {edge_signature(edge["actor"], edge["action"], edge["swaps"],
                                initial ^ unpack(edge["after_delta"])) for edge in node["enabled"]}
        assert len(edges) == len(node["enabled"])
        known[state] = edges
    assert known.keys() == graph.keys(), "Missing or spurious reachable state"
    for state, branches in graph.items():
        expected = {edge_signature(rule.actor, rule.action, rule.swaps, target) for rule, target in branches}
        assert known[state] == expected, "Missing or spurious enabled move"


def paths(graph, current, seen=frozenset()):
    assert current not in seen, "A reachable cycle permits a nonterminating order"
    if not graph[current]:
        yield ()
    for rule, target in graph[current]:
        for suffix in paths(graph, target, seen | {current}):
            yield ((rule, target),) + suffix


def order_observation(initial, order, devices, source_p, selected):
    assert Counter(rule.actor for rule, _ in order if rule.action == "offer") == {
        device["source"]: 1 for device in devices
    }
    all_traces, incoming, acknowledgments = [], [], []
    for device in devices:
        observed = device["receipt"] + device["memory"]
        trace = [bits(initial, observed)]
        changed_by = []
        for rule, target in order:
            value = bits(target, observed)
            if value != trace[-1]:
                trace.append(value)
                changed_by.append(rule.actor)
        assert tuple(trace) in (ONE, TWO)
        assert sum(row[2] == "1" for row in trace) == 1 and trace[-1][2] == "1"
        actors = ([device["witness"]] if tuple(trace) == ONE
                  else [device["witness"], device["receiver"], device["witness"]])
        assert changed_by == actors
        expected_offer = selected if device["source"] == source_p else 1
        assert bits(order[-1][1], device["offer"]) == {1: "010", 2: "001"}[expected_offer]
        all_traces.append(trace)
        incoming.append(changed_by.count(device["witness"]))
        acknowledgments.append(changed_by.count(device["receiver"]))
    return all_traces, incoming, acknowledgments


def verify_cell(cell, starts, boards, words):
    law, mode, offer = (cell[key] for key in ("law", "condition", "offer"))
    crossed = int(mode == "interrupted")
    condition = mode != "read_disabled"
    orient = cell["reversed_bank"]
    key = f"{crossed}-{int(orient)}"
    assert cell["common_initial_before_name_transport"] == words[key]["complete_after_two_cuts"]
    assert (cell["receiver"], cell["other"]) == ("c8", "u8")
    raw = starts[crossed]
    stars, devices, initial, hm = transported(
        boards[crossed], raw["stars"] + boards[crossed]["newborn_stars"],
        raw["devices_in_c8_u8_order"], unpack(words[key]["complete_after_two_cuts"]), cell["naming"], orient,
    )
    source_p = hm[raw["source_p"]]
    rules = tuple(rule for device in devices
                  for rule in program(device, offer if device["source"] == source_p else 1, condition))
    graph = independent_graph(stars, rules, initial, law)
    compare_graph(graph, cell["all_order_state_graph"], initial)
    sampled = cell["one_complete_actual_order"]
    state = initial
    for action in sampled:
        rule, target = next((rule, target) for rule, target in graph[state] if {
            "actor": rule.actor, "action": rule.action, "physical_swaps": list(map(list, rule.swaps)),
            "sensed_marks": list(rule.sensing),
        } == action)
        state = target
    assert not graph[state]
    total = longest = 0
    expected = [1, 1]
    if condition:
        expected[crossed] = offer
    terminals = set()
    for order in paths(graph, initial):
        total += 1
        longest = max(longest, len(order))
        terminals.add(order[-1][1])
        traces, incoming, own = order_observation(initial, order, devices, source_p, offer)
        assert traces == cell["receiver_transcripts"]
        assert [trace[-1][:3] for trace in traces] == cell["final_receipt_bank"] == ["001", "001"]
        memory = [1 if trace[-1][3:] == "10" else 2 for trace in traces]
        history = [2 if any(row[:3] == "010" for row in trace[:-1]) else 1 for trace in traces]
        assert memory == cell["memory_decoded"] == history == cell["history_decoded"] == expected
        assert incoming == cell["incoming_changes"] and own == cell["own_acknowledgments"]
    assert len(terminals) == 1
    assert (total, len(graph), longest) == (cell["complete_orders"], cell["states"], cell["longest"])
    return total, sum(map(len, graph.values())), graph, initial


def rejection_controls(graph, initial, submitted):
    first = next(row for row in submitted if unpack(row["delta_from_initial"]) == frozenset())
    rest = [row for row in submitted if row is not first]
    a, b = first["enabled"]
    assert a["action"] == b["action"] == "offer"
    for replacement in ([a], [a, b, {**a, "action": "acknowledge"}]):
        try:
            compare_graph(graph, [{**first, "enabled": replacement}, *rest], initial)
        except AssertionError:
            continue
        raise AssertionError("An omitted or fabricated transition passed")


def audit():
    path = DATA / "sends.json.gz"
    content = path.read_bytes()
    assert sha256(content).hexdigest() == RAW_SHA
    raw = json.loads(gzip.decompress(content))
    summary = json.loads((DATA / "summary.json").read_bytes())
    assert summary["data_sha256"] == RAW_SHA
    assert raw["design"] == [sha256((DESIGN / name).read_bytes()).hexdigest()
                             for name in ("design_candidate.md", "design_revision.md")]
    for filename, digest in summary["source_code_sha256"].items():
        assert sha256((HERE / filename).read_bytes()).hexdigest() == digest
    starts = [raw["originals"][str(i)] for i in range(2)]
    check_interruption(*starts)
    for start in starts:
        check_enrollment(start["stars"], start["devices_in_c8_u8_order"])

    def identity(cell):
        return tuple(cell[x] for x in ("law", "condition", "offer", "naming", "reversed_bank"))

    submitted = {identity(cell): cell for cell in raw["all_physical_orders"]}
    expected = set(product(LAWS, CONDITIONS, (1, 2), NAMINGS, (False, True)))
    assert submitted.keys() == expected and len(raw["all_physical_orders"]) == len(expected)
    result = {}
    for law in LAWS:
        law_record, totals = raw["laws"][law], summary["laws"][law]
        boards = [law_record["boards"][str(i)] for i in range(2)]
        stages = [reached_stages(start["stars"], board) for start, board in zip(starts, boards, strict=True)]
        growth = [[len(b) - len(a) for a, b in zip(stage, stage[1:])] for stage in stages]
        assert growth == totals["growth"] == [[63, 131], [63, 131]]
        words = law_record["words"]
        captures = {}
        for orient in (False, True):
            pairs = [words[f"{i}-{int(orient)}"] for i in range(2)]
            common = unpack(pairs[0]["complete_original"])
            assert common == unpack(pairs[1]["complete_original"])
            references = []
            for i, item in enumerate(pairs):
                initial = unpack(item["complete_after_two_cuts"])
                _, devices, _, _ = transported(boards[i], stages[i][-1],
                    starts[i]["devices_in_c8_u8_order"], initial, "original", orient)
                assert initial & owners(starts[i]["stars"]).keys() == common
                assert all(allowed(len(initial.intersection(row)), len(row), law) for row in stages[i][-1])
                for device in devices:
                    assert bits(initial, device["offer"]) == bits(initial, device["receipt"]) == "100"
                    assert bits(initial, device["stage"]) == bits(initial, device["memory"]) == "10"
                assert bits(initial, devices[0]["donor_bundle"]) == bits(initial, devices[1]["donor_bundle"])
                prefixes = [receiver_prefix(stages[i], device, initial) for device in devices]
                assert prefixes == item["whole_receiver_local_prefixes"]
                references.append(prefixes)
                checked = [capture_table(stages[i][-1], device, law) for device in devices]
                assert checked == item["exhaustive_relay_checks"]
                trimmed = [{key: cap[key] for key in ("arity", "possible", "allowed")} for cap in checked]
                assert trimmed == totals["foreground_full_tables"][str(i)]
                captures[str(i)] = trimmed
            assert references[0] == references[1] and totals["identical_whole_receiver_prefixes"]
        counts = Counter()
        edges = cells = 0
        by_control = {}
        for mode, offer, naming, orient in product(CONDITIONS, (1, 2), NAMINGS, (False, True)):
            cell = submitted[law, mode, offer, naming, orient]
            count, edge_count, graph, initial = verify_cell(cell, starts, boards, words)
            if (mode, offer, naming, orient) == ("intact", 1, "original", False):
                rejection_controls(graph, initial, cell["all_order_state_graph"])
            counts[mode] += count
            edges += edge_count
            cells += 1
            subset = {key: cell[key] for key in ("states", "complete_orders", "receiver_transcripts",
                      "memory_decoded", "incoming_changes", "own_acknowledgments", "condition", "offer")}
            assert by_control.setdefault((mode, offer), subset) == subset
        assert cells == totals["registered_cells_with_recodings"] == 36
        assert dict(counts) == totals["orders_by_condition_with_recodings"]
        assert by_control == {(cell["condition"], cell["offer"]): cell for cell in totals["canonical_cells"]}
        result[law] = {"cells": cells, "edges": edges, "maximal_orders": dict(counts),
                       "full_captures": captures, "conditions": list(by_control.values())}
    return {
        "passed": True,
        "audit_class": "V1 independently authored same-task replay",
        "submitted_data_sha256": RAW_SHA,
        "summary_sha256": sha256((DATA / "summary.json").read_bytes()).hexdigest(),
        "legal_moves_checked": "Exact equality of every reached state's complete enabled successors.",
        "rejection_controls": ["Missing enabled move", "Fabricated enabled move"],
        "per_law": result,
    }


if __name__ == "__main__":
    result = audit()
    output = DATA / "verification.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(sha256(output.read_bytes()).hexdigest())
