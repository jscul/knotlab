"""Independent finite check of polarity.json; never imports polarity.py.

Use integer bit states, terminal strongly connected components, backward
probability recursion and exhaustive raw continuations for the saved paths.
Only stdout is written. Run with python3 -B to avoid bytecode artifacts.
"""

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TICKET = "SIX-BIT-EVENT-20261111-001"
DEFAULT_RECORD = (ROOT / "artifacts" / TICKET /
                  f"{TICKET}-E001_raw_event" / "polarity.json")
PORTS = "abcxyz"
TRIPLES = ((0, 1, 2), (0, 4, 5), (3, 1, 5), (3, 4, 2))
RAW = tuple(range(8))
MIXED = tuple(range(1, 7))
TIMES = (0, 1, 2, 4, 8, 16, 32, 64, 128)


class CheckFailure(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def bit(state, index):
    return (state >> (5 - index)) & 1


def core_legal(state):
    return all(len({bit(state, i) for i in triple}) == 2 for triple in TRIPLES)


STATES = tuple(s for s in range(64) if core_legal(s))
REST = tuple(s for s in STATES if bit(s, 0) != bit(s, 3))


def label(state):
    return f"{state:06b}"


def labels(states):
    return [label(s) for s in sorted(states)]


def transition(state, port, raw, preference):
    candidate = state ^ (1 << (5 - port))
    if not core_legal(candidate):
        return state
    if port == 4:
        if preference == "one" and bit(candidate, 4) != 1:
            return state
        if preference == "opposite_a" and bit(candidate, 4) == bit(state, 0):
            return state
    for shift in (0, 1, 2):
        observed = (raw >> shift) & 1
        before = bit(state, 0) == bit(state, 3) == observed
        after = bit(candidate, 0) == bit(candidate, 3) == observed
        if after and not before:
            return state
    return candidate


def graph(words, preference):
    return {s: {transition(s, i, w, preference) for w in words for i in range(6)}
            for s in STATES}


def reachable(starts, edges):
    found = set(starts)
    while True:
        expanded = found | {t for s in found for t in edges[s]}
        if expanded == found:
            return found
        found = expanded


def terminal_components(edges):
    """Tarjan components followed by an independent outgoing-edge test."""
    indices, low, stack, on_stack, components = {}, {}, [], set(), []

    def visit(s):
        indices[s] = low[s] = len(indices)
        stack.append(s)
        on_stack.add(s)
        for t in edges[s]:
            if t not in indices:
                visit(t)
                low[s] = min(low[s], low[t])
            elif t in on_stack:
                low[s] = min(low[s], indices[t])
        if low[s] == indices[s]:
            component = set()
            while True:
                t = stack.pop()
                on_stack.remove(t)
                component.add(t)
                if t == s:
                    break
            components.append(component)

    for s in STATES:
        if s not in indices:
            visit(s)
    return [c for c in components if all(edges[s] <= c for s in c)]


def terminal_from(starts, edges, components):
    seen = reachable(starts, edges)
    return set().union(*(c for c in components if c & seen))


def stable_correct(edges, value):
    # Remove every state that can reach an incorrect reading, working backward.
    bad = {s for s in STATES if bit(s, 4) != value}
    while True:
        expanded = bad | {s for s in STATES if edges[s] & bad}
        if expanded == bad:
            return set(STATES) - bad
        bad = expanded


def stable_probabilities(raw, stable):
    # Backward recursion computes P_s(X_n in stable) simultaneously for all s.
    values = {s: Fraction(int(s in stable)) for s in STATES}
    saved = {}
    for n in range(max(TIMES) + 1):
        if n in TIMES:
            saved[n] = values.copy()
        values = {s: sum((values[transition(s, i, raw, "opposite_a")]
                          for i in range(6)), Fraction()) / 6 for s in STATES}
    return saved


def check_readings(record):
    mixed = graph(MIXED, "opposite_a")
    require(all(mixed[s] == {s} for s in REST), "a resting state moves on mixed input")
    constants = {w: graph((w,), "opposite_a") for w in (0, 7)}
    components = {w: terminal_components(constants[w]) for w in (0, 7)}
    probability_cells = 0
    for word, value in (("000", 0), ("111", 1)):
        raw = int(word, 2)
        data = record["prefer_y_opposite_a"][word]
        stable = stable_correct(graph((*MIXED, raw), "opposite_a"), value)
        require(labels(stable) == data["stable_correct_states"], f"{word}: stable set")
        terminal = terminal_from(STATES, constants[raw], components[raw])
        require(labels(terminal) == data["terminal_from_all_18"], f"{word}: global terminal set")
        require(len(components[raw]) == 1 and len(terminal) == 7,
                f"{word}: expected one seven-state terminal component")
        require({bit(s, 4) for s in terminal} == {value}, f"{word}: wrong terminal reading")
        require(set(data["starts"]) == set(labels(REST)), f"{word}: missing resting start")
        probabilities = stable_probabilities(raw, stable)
        for start in REST:
            saved = data["starts"][label(start)]
            first = terminal_from((start,), constants[raw], components[raw])
            require(labels(first) == saved["terminal_at_first_word"],
                    f"{word}/{label(start)}: terminal states")
            after_mixed = reachable(first, mixed)
            readings = sorted({str(bit(s, 4)) for s in after_mixed})
            require(readings == saved["readings_after_any_mixed_continuation"] == [str(value)],
                    f"{word}/{label(start)}: retained reading")
            opposite = 7 - raw
            second = terminal_from(after_mixed, constants[opposite], components[opposite])
            final = reachable(second, mixed)
            readings = sorted({str(bit(s, 4)) for s in final})
            require(readings == saved["readings_after_opposite_sustained_word_and_any_mixed"]
                    == [str(1 - value)], f"{word}/{label(start)}: overwritten reading")
            cells = saved["probability_already_stable_after_n_proposals"]
            require(set(cells) == {str(n) for n in TIMES}, "recorded exposure grid differs")
            for n in TIMES:
                require(Fraction(cells[str(n)]) == probabilities[n][start],
                        f"{word}/{label(start)}: probability at {n}")
                probability_cells += 1
    return probability_cells


def check_paths(record):
    certificate = record["one_way_pulse_certificate"]
    paths = certificate["port_paths"]
    starts = {label(s) for s in STATES if bit(s, 4) == 0}
    count = continuations = 0
    lengths = []
    require(set(paths) == {"000", "111"}, "path event words differ")
    for event, by_start in paths.items():
        require(set(by_start) == starts, "path start coverage differs")
        for start, path in by_start.items():
            require(isinstance(path, str) and 1 <= len(path) <= 4,
                    "missing or overly long port path")
            require(set(path) <= set(PORTS), "unknown port in path")
            for suffix in product(RAW, repeat=len(path) - 1):
                state = int(start, 2)
                for port, raw in zip(path, (int(event, 2), *suffix)):
                    state = transition(state, PORTS.index(port), raw, "one")
                    require(state in STATES, "path left the hard core")
                require(bit(state, 4) == 1,
                        f"failed path {event}/{start}/{path} with suffix {suffix}")
                continuations += 1
            lengths.append(len(path))
            count += 1
    worst = max(lengths)
    require(certificate["worst_path_length"] == worst, "wrong maximum path length")
    require(Fraction(certificate["uniform_probability_lower_bound"]) == Fraction(1, 6**worst),
            "wrong uniform probability bound")
    return count, continuations


def verify(record, plan):
    require(len(STATES) == 18 and len(REST) == 4, "core enumeration differs")
    require(record["state_order"] == PORTS, "state order differs")
    require(record["resting_states"] == labels(REST), "resting states differ")
    require(record["secondary_plan_sha256"] == hashlib.sha256(plan.read_bytes()).hexdigest(),
            "secondary plan hash differs")
    probability_cells = check_readings(record)
    path_count, continuation_count = check_paths(record)
    mutations = []
    changed = deepcopy(record)
    changed["prefer_y_opposite_a"]["000"]["starts"]["001101"][
        "readings_after_any_mixed_continuation"] = ["1"]
    try:
        check_readings(changed)
    except CheckFailure:
        mutations.append("incorrect retained reading rejected")
    changed = deepcopy(record)
    changed["one_way_pulse_certificate"]["port_paths"]["000"]["001101"] = "aczb"
    try:
        check_paths(changed)
    except CheckFailure:
        mutations.append("failed event path rejected")
    require(len(mutations) == 2, "a scientific mutation escaped rejection")
    return {
        "passed": True,
        "hard_core_states": len(STATES), "resting_states": len(REST), "raw_words": len(RAW),
        "closed_classes": {"000": {"states": 7, "y": 0}, "111": {"states": 7, "y": 1}},
        "sustained_orders_with_arbitrary_intervening_mixed_words": ["000 then 111", "111 then 000"],
        "probability_cells_checked": probability_cells,
        "maximum_recorded_exposure_checked": max(TIMES),
        "one_way_paths_checked": path_count,
        "exhaustive_raw_suffixes_checked": continuation_count,
        "scientific_mutations_rejected": mutations,
        "independence": "No producer import; integer states, Tarjan components, backward probabilities and exhaustive suffixes.",
        "limits": "Sustained input conclusions require independent full-support proposals. Finite exposure has misses. The supplied polarity rule overwrites the one-way event bit; y alone cannot distinguish no event from a matching initial polarity. This check covers the secondary analysis, not the primary experiment or upper-knot certificate.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--plan", type=Path, default=Path(__file__).with_name("secondary_plan.md"))
    args = parser.parse_args()
    try:
        record_bytes = args.record.read_bytes()
        report = verify(json.loads(record_bytes), args.plan)
        report["record_sha256"] = hashlib.sha256(record_bytes).hexdigest()
    except (CheckFailure, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"polarity verification failed: {exc}")
    print(json.dumps(report, indent=2, sort_keys=True))
