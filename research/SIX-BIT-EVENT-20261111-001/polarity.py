"""Analyze alternative local preferences and certify paths through short input pulses."""

import argparse
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from itertools import product
from pathlib import Path


PORTS = "abcxyz"
TRIPLES = ("abc", "ayz", "xbz", "xyc")
WORDS = tuple("".join(bits) for bits in product("01", repeat=3))
MIXED = tuple(w for w in WORDS if len(set(w)) == 2)
STATES = tuple(
    "".join(bits) for bits in product("01", repeat=6)
    if all(len({bits[PORTS.index(p)] for p in triple}) == 2 for triple in TRIPLES)
)
REST = tuple(s for s in STATES if s[0] != s[3])
TIMES = (0, 1, 2, 4, 8, 16, 32, 64, 128)


def steps(state, raw, preference):
    out = []
    for i, port in enumerate(PORTS):
        new = state[:i] + ("1" if state[i] == "0" else "0") + state[i + 1:]
        allowed = new in STATES
        if port == "y":
            preferred = "1" if preference == "one" else ("1" if state[0] == "0" else "0")
            allowed = allowed and new[i] == preferred
        for sample in raw:
            was_violated = state[0] == state[3] == sample
            would_violate = new[0] == new[3] == sample
            if would_violate and not was_violated:
                allowed = False
        out.append(new if allowed else state)
    return tuple(out)


def closure(starts, successors):
    found = set(starts)
    pending = list(starts)
    while pending:
        state = pending.pop()
        for nxt in successors[state]:
            if nxt not in found:
                found.add(nxt)
                pending.append(nxt)
    return found


def terminal_states(starts, successors):
    """In this finite full-support process, find states in reachable closed classes."""
    reached = closure(starts, successors)
    future = {s: closure([s], successors) for s in reached}
    return {s for s in reached if all(s in future[t] for t in future[s])}


def unions(kernels, words):
    return {s: {t for w in words for t in kernels[w][s]} for s in STATES}


def retained_chance(start, kernel, stable):
    counts = {start: 1}
    snapshots = {}
    for tick in range(max(TIMES) + 1):
        if tick in TIMES:
            captured = sum(n for s, n in counts.items() if s in stable)
            snapshots[tick] = str(Fraction(captured, 6**tick))
        if tick < max(TIMES):
            next_counts = Counter()
            for s, n in counts.items():
                for t in kernel[s]:
                    next_counts[t] += n
            counts = next_counts
    return snapshots


def last_value(kernels):
    mixed_transitions = unions(kernels, MIXED)
    report = {}
    for value in "01":
        word = value * 3
        same_or_mixed = unions(kernels, (*MIXED, word))
        stable = {s for s in STATES if all(t[4] == value for t in closure([s], same_or_mixed))}
        first = {}
        for s in REST:
            terminal = terminal_states([s], kernels[word])
            after = closure(terminal, mixed_transitions)
            opposite = ("1" if value == "0" else "0") * 3
            next_terminal = terminal_states(after, kernels[opposite])
            after_opposite = closure(next_terminal, mixed_transitions)
            first[s] = {
                "terminal_at_first_word": sorted(terminal),
                "readings_after_any_mixed_continuation": sorted({t[4] for t in after}),
                "readings_after_opposite_sustained_word_and_any_mixed": sorted({t[4] for t in after_opposite}),
                "probability_already_stable_after_n_proposals": retained_chance(s, kernels[word], stable),
            }
        report[word] = {
            "stable_correct_states": sorted(stable),
            "terminal_from_all_18": sorted(terminal_states(STATES, kernels[word])),
            "starts": first,
        }
    return report


def robust_path(start, event, kernels):
    """One proposal at the event, then the same path works under every later letter."""
    pending = deque((t, [i]) for i, t in enumerate(kernels[event][start]))
    visited = set()
    while pending:
        state, path = pending.popleft()
        if state[4] == "1":
            return "".join(PORTS[i] for i in path)
        if state in visited:
            continue
        visited.add(state)
        for i in range(len(PORTS)):
            targets = {kernels[w][state][i] for w in WORDS}
            if len(targets) == 1:
                nxt = targets.pop()
                if nxt != state:
                    pending.append((nxt, path + [i]))
    return None


def analyze():
    def kernels(mode):
        return {w: {s: steps(s, w, mode) for s in STATES} for w in WORDS}

    constant = kernels("one")
    paths = {w: {s: robust_path(s, w, constant) for s in STATES if s[4] == "0"}
             for w in ("000", "111")}
    routes = [path for by_state in paths.values() for path in by_state.values()]
    length = max(map(len, routes)) if all(path is not None for path in routes) else None
    return {
        "secondary_plan_sha256": hashlib.sha256(Path(__file__).with_name("secondary_plan.md").read_bytes()).hexdigest(),
        "state_order": PORTS, "resting_states": REST,
        "one_way_pulse_certificate": {
            "port_paths": paths, "worst_path_length": length,
            "uniform_probability_lower_bound": str(Fraction(1, 6**length)) if length is not None else None,
        },
        "prefer_y_opposite_a": last_value(kernels("opposite_a")),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(analyze(), indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(output)
    else:
        print(output, end="")
