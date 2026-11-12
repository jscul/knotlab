"""Independent finite check of the autonomous source, memory and live reader.

This checker imports neither integration producer nor polarity implementation.
It reconstructs every offered one-site change from the stated local rules.
The source artifact is read; mutations are made only in memory.
"""

from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "artifacts/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/source.json"
NAMES = "abcxyz"
KNOTS = ((0, 1, 2), (0, 4, 5), (3, 1, 5), (3, 4, 2))
ALL_SIX = tuple(product((0, 1), repeat=6))


def nae(values):
    values = tuple(values)
    return any(value != values[0] for value in values[1:])


def hard_legal(bits, deleted=False):
    return all(nae(bits[i] for i in knot) for knot in (KNOTS[1:] if deleted else KNOTS))


def bridge_failures(state):
    return {
        raw_port
        for raw_port in (3, 4, 5)
        if not nae((state[raw_port], state[6], state[9]))
    }


def offered(state, port, deleted):
    """Offer any of the 14 sites; source changes do not consult its reader."""
    assert 0 <= port < 14
    trial = state[:port] + (1 - state[port],) + state[port + 1 :]
    if port < 6:
        return trial if hard_legal(trial[:6], deleted) else state
    if port < 12:
        if port == 10 and state[port] == 1:
            return state
        if not hard_legal(trial[6:12]):
            return state
        if not bridge_failures(trial) <= bridge_failures(state):
            return state
        if not nae((trial[10], trial[12], trial[13])):
            return state
        return trial
    return trial if nae((trial[10], trial[12], trial[13])) else state


def render(state):
    return ["".join(map(str, state[:6])), "".join(map(str, state[6:12])), "".join(map(str, state[12:]))]


def parse(value):
    assert isinstance(value, list) and len(value) == 3
    assert all(isinstance(part, str) and len(part) == size and set(part) <= {"0", "1"} for part, size in zip(value, (6, 6, 2)))
    return tuple(int(bit) for part in value for bit in part)


def closed_components(graph):
    """Iterative Kosaraju; no producer SCC or reachability code is reused."""
    order = []
    seen = set()
    for start in graph:
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, iter(graph[start]))]
        while stack:
            state, targets = stack[-1]
            try:
                target = next(targets)
            except StopIteration:
                stack.pop()
                order.append(state)
                continue
            if target not in seen:
                seen.add(target)
                stack.append((target, iter(graph[target])))
    reverse = {state: set() for state in graph}
    for state, targets in graph.items():
        for target in targets:
            reverse[target].add(state)
    assigned = set()
    closed = []
    for start in reversed(order):
        if start in assigned:
            continue
        part = {start}
        assigned.add(start)
        pending = [start]
        while pending:
            for previous in reverse[pending.pop()]:
                if previous not in assigned:
                    assigned.add(previous)
                    part.add(previous)
                    pending.append(previous)
        if all(target in part for state in part for target in graph[state]):
            closed.append(part)
    return closed, reverse


def enumerate_model(deleted):
    sources = tuple(bits for bits in ALL_SIX if hard_legal(bits, deleted))
    memories = tuple(bits for bits in ALL_SIX if hard_legal(bits) and bits[0] != bits[3] and bits[4] == 0)
    starts = {
        source + memory + upper
        for source in sources
        for memory in memories
        for upper in product((0, 1), repeat=2)
        if nae((memory[4], *upper))
    }
    found = set(starts)
    pending = deque(starts)
    graph = {}
    while pending:
        state = pending.popleft()
        targets = {offered(state, port, deleted) for port in range(14)}
        graph[state] = targets
        for target in targets:
            assert hard_legal(target[:6], deleted)
            assert hard_legal(target[6:12])
            assert nae((target[10], target[12], target[13]))
            if target not in found:
                found.add(target)
                pending.append(target)
    closed, reverse = closed_components(graph)

    def hitting(predicate):
        targets = {state for state in found if predicate(state)}
        can_hit = set(targets)
        pending = list(targets)
        while pending:
            for previous in reverse[pending.pop()]:
                if previous not in can_hit:
                    can_hit.add(previous)
                    pending.append(previous)
        # All starts were included in the forward search. Every reached state
        # can reach a target iff the finite positive-probability chain hits it
        # almost surely from every start.
        return {
            "reachable_target_states": len(targets),
            "reachable_states_without_a_path_to_target": len(found - can_hit),
            "hit_with_probability_one_from_all_starts": not (found - can_hit),
        }

    summary = {
        "source_states": len(sources),
        "initial_states": len(starts),
        "reachable_joint_states": len(found),
        "equal_words_reachable": sorted({"".join(map(str, state[3:6])) for state in found if state[3:6] in ((0, 0, 0), (1, 1, 1))}),
        "upper_pairs_reachable": sorted({"".join(map(str, state[12:14])) for state in found}),
        "written_can_fall_back_to_zero": any(state[10] and not target[10] for state, targets in graph.items() for target in targets),
        "hitting": {
            "stored_bit_is_one": hitting(lambda state: state[10] == 1),
            "upper_pair_is_00": hitting(lambda state: state[12:14] == (0, 0)),
        },
    }
    classes = [
        {
            "size": len(part),
            "memory_y_values": sorted({state[10] for state in part}),
            "raw_words": sorted({"".join(map(str, state[3:6])) for state in part}),
            "upper_pairs": sorted({"".join(map(str, state[12:14])) for state in part}),
        }
        for part in closed
    ]
    classes.sort(key=lambda row: (row["size"], row["memory_y_values"], row["raw_words"], row["upper_pairs"]))
    return {"summary": summary, "closed_classes": classes, "starts": starts, "graph": graph}


def check_traces(saved, model, deleted):
    traces = saved["matched_source_traces"]
    if not deleted:
        assert traces == {}
        return {}
    assert set(traces) == {"000", "111"}
    checked = {}
    for label, trace in traces.items():
        initial = parse(trace["start"])
        assert initial in model["starts"] and initial[10] == 0 and initial[12:] == (0, 1)
        state = initial
        raw_seen = {"".join(map(str, state[3:6]))}
        for step in trace["moves"]:
            port = step["proposal_index"]
            assert type(port) is int
            target = offered(state, port, deleted)
            assert target != state, "a recorded move was rejected"
            assert target == parse(step["after"]), "trace disagrees with local rules"
            assert target in model["graph"][state]
            state = target
            raw_seen.add("".join(map(str, state[3:6])))
        assert label in raw_seen
        assert ({"000", "111"} - {label}).isdisjoint(raw_seen), "history also saw the other equal word"
        assert state[:6] == initial[:6], "source did not return to its common state"
        assert state[10] == 1 and state[12:] == (0, 1)
        assert state == parse(trace["common_probe_from"])
        probe = offered(state, 13, deleted)
        assert probe != state and probe[12:] == (0, 0)
        assert probe == parse(trace["probe_after_proposing_q"])
        clear = state[:6] + initial[6:12] + (0, 1)
        assert clear == parse(trace["same_probe_from_clear_start"])
        assert offered(clear, 13, deleted) == clear
        checked[label] = {
            "accepted_history_moves": len(trace["moves"]),
            "raw_words_seen": sorted(raw_seen),
            "common_source": render(state)[0],
            "memory_before_probe": render(state)[1],
            "upper_before_probe": "01",
            "written_q_flip_accepts": True,
            "matched_clear_q_flip_rejects": True,
        }
    assert traces["000"]["start"] == traces["111"]["start"]
    return checked


def compare(saved, models):
    expected_order = [f"source.{name}" for name in NAMES] + [f"memory.{name}" for name in NAMES] + ["reader.p", "reader.q"]
    assert saved["proposal_order"] == expected_order
    checked = {}
    for key, deleted in (("original_source", False), ("source_without_abc", True)):
        model = models[deleted]
        for field, expected in model["summary"].items():
            assert saved[key][field] == expected, f"{key}.{field}: expected {expected!r}"
        checked[key] = check_traces(saved[key], model, deleted)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Saved source-integration JSON to check")
    args = parser.parse_args()
    started = perf_counter()
    saved_bytes = args.source.read_bytes()
    saved = json.loads(saved_bytes)
    models = {deleted: enumerate_model(deleted) for deleted in (False, True)}
    traces = compare(saved, models)
    mutations = []
    wrong_count = deepcopy(saved)
    wrong_count["source_without_abc"]["reachable_joint_states"] += 1
    wrong_trace = deepcopy(saved)
    move = wrong_trace["source_without_abc"]["matched_source_traces"]["000"]["moves"][0]
    move["proposal_index"] = (move["proposal_index"] + 1) % 14
    for name, corrupted in (("reachable_count", wrong_count), ("trace_proposal", wrong_trace)):
        try:
            compare(corrupted, models)
        except (AssertionError, KeyError, ValueError):
            mutations.append({"mutation": name, "rejected": True})
        else:
            raise AssertionError(f"checker accepted {name} mutation")
    report = {
        "status": "PASS",
        "independence": "Separate same-task implementation; no source.py or polarity.py import or code inspection.",
        "source_path": str(args.source.resolve()),
        "source_sha256": hashlib.sha256(saved_bytes).hexdigest(),
        "proposal_sites": 14,
        "models": {
            key: {**models[deleted]["summary"], "closed_classes": models[deleted]["closed_classes"]}
            for key, deleted in (("original_source", False), ("source_without_abc", True))
        },
        "exclusive_event_histories": traces["source_without_abc"],
        "mutations": mutations,
        "runtime_seconds": perf_counter() - started,
        "limits": [
            "The result concerns this finite source, prepared clear memories, live reader and supplied update laws.",
            "No unknown-rule learning, spontaneous wiring, physical time or unbounded hierarchy is established.",
            "Probability-one hitting uses independent uniform proposals; an adversary can indefinitely stall.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
