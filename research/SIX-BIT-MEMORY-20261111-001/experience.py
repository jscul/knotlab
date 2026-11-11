"""Exact response of the six distinctions after exposure to either rule set."""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


PORTS = "abcxyz"
RULES = ("abc", "ayz", "xbz", "xyc")
STATES = tuple("".join(bits) for bits in product("01", repeat=6))


def allowed(rules):
    return {
        state for state in STATES
        if all(len({state[PORTS.index(port)] for port in rule}) > 1 for rule in rules)
    }


def outcomes(state, allowed_states):
    """One outcome for each equiprobable attempt, including rejected flips."""
    result = []
    for index, bit in enumerate(state):
        proposed = state[:index] + ("0" if bit == "1" else "1") + state[index + 1:]
        result.append(proposed if proposed in allowed_states else state)
    return result


def equal_weight_response(starts, evaluation):
    counts = Counter(after[3:] for state in starts for after in outcomes(state, evaluation))
    return {word: str(Fraction(count, 6 * len(starts))) for word, count in sorted(counts.items())}


def covering_walk(start, allowed_states):
    """Return a possible finite history visiting every legal state, back to start."""
    visited = {start}
    walk = [start]

    def visit(current):
        for after in outcomes(current, allowed_states):
            if after in visited:
                continue
            visited.add(after)
            walk.append(after)
            visit(after)
            walk.append(current)

    visit(start)
    if visited != allowed_states:
        raise ValueError("A covering history requires one connected set of states")
    return walk


def compare_experiences():
    original = allowed(RULES)
    relaxed = allowed(RULES[1:])
    free = set(STATES)
    # The proposal matrix is symmetric, counting blocked moves as staying put.
    # Check the incoming column sums, so uniform really is stationary in each case.
    for law in (original, relaxed):
        incoming = Counter(after for state in law for after in outcomes(state, law))
        if any(incoming[state] != 6 for state in law):
            raise ValueError("Uniform preparation is not stationary")

    common_cues = sorted({state[3:] for state in original} & {state[3:] for state in relaxed})
    comparisons = {}
    for cue in common_cues:
        panel = {}
        for name, preparation in (("four_knots", original), ("without_abc", relaxed)):
            starts = sorted(s for s in preparation if s[3:] == cue)
            panel[name] = {
                "equiprobable_abc": [s[:3] for s in starts],
                "next_xyz_with_abc_removed": equal_weight_response(starts, relaxed),
                "next_xyz_free": equal_weight_response(starts, free),
            }
        comparisons[cue] = panel

    free_rows = {}
    for cue in sorted({s[3:] for s in free}):
        rows = [equal_weight_response([s], free) for s in sorted(free) if s[3:] == cue]
        if any(row != rows[0] for row in rows[1:]):
            raise ValueError("Hidden state affects the free visible response")
        free_rows[cue] = rows[0]

    start = min(original & relaxed)
    paths = [covering_walk(start, states) for states in (original, relaxed)]
    horizon = max(map(len, paths))
    for walk, states in zip(paths, (original, relaxed)):
        spare = horizon - len(walk)
        if spare % 2:
            raise ValueError("Cannot equalize the histories by legal out-and-back moves")
        neighbor = next(s for s in outcomes(start, states) if s != start)
        walk.extend([neighbor, start] * (spare // 2))
        if set(walk) != states or walk[-1] != start or any(
            after not in outcomes(before, states) for before, after in zip(walk, walk[1:])
        ):
            raise ValueError("Invalid exhaustive history")

    return {
        "ports": PORTS,
        "shared_full_states": len(original & relaxed),
        "preparation_sizes": [len(original), len(relaxed)],
        "matched_visible_cues": comparisons,
        "free_visible_kernel_for_every_hidden_state": free_rows,
        "complete_histories": {
            "four_knots": paths[0],
            "without_abc": paths[1],
            "moves_each": horizon - 1,
            "common_start_and_end": start,
            "visible_words_in_order_of_first_visit": [
                list(dict.fromkeys(s[3:] for s in walk)) for walk in paths
            ],
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(compare_experiences(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
