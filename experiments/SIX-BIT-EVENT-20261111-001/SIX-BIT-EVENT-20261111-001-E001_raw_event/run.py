"""Exact local-update, pulse, settling and readout analysis of the raw input.

The scorer enumerates the fixed six-bit core. A raw word changes atomically;
it does not overwrite any core value. Each proposal chooses one of the six
core bits uniformly. The kernel evaluates individual constraints and never
classifies the raw word as an event.
"""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from time import perf_counter


CORE_NAMES = "abcxyz"
RAW_NAMES = "uvw"
READ = CORE_NAMES.index("y")
HARD = ((0, 1, 2), (0, 4, 5), (3, 1, 5), (3, 4, 2))
HORIZONS = (0, 1, 2, 4, 8, 16, 32, 64, 128)
NEUTRAL = (0, 0, 1)


def bit(state, port):
    return (state >> (5 - port)) & 1


def word(state):
    return f"{state:06b}"


def raw_word(raw):
    return "".join(map(str, raw))


def nae(values):
    return len(set(values)) > 1


STATES = tuple(s for s in range(64) if all(nae(bit(s, p) for p in knot) for knot in HARD))
INDEX = {state: i for i, state in enumerate(STATES)}
RAW_WORDS = tuple(product((0, 1), repeat=3))
CLEAR = tuple(s for s in STATES if bit(s, 0) != bit(s, 3) and bit(s, READ) == 0)
LOADED = tuple(s for s in STATES if bit(s, 0) != bit(s, 3) and bit(s, READ) == 1)


def violations(state, raw, couplings):
    """Identity of each violated raw attachment under this same raw word."""
    return frozenset(
        position
        for position, (input_port, negated) in enumerate(couplings)
        if not nae((raw[input_port] ^ negated, bit(state, 0), bit(state, 3)))
    )


def kernel(raw, couplings, one_way):
    """Integer multiplicities out of six; rejected proposals are self-loops."""
    rows = []
    for state in STATES:
        before = violations(state, raw, couplings)
        counts = {}
        for port in range(6):
            candidate = state ^ (1 << (5 - port))
            accepted = (
                candidate in INDEX
                and not (one_way and port == READ and bit(state, READ) == 1)
                and violations(candidate, raw, couplings) <= before
            )
            target = INDEX[candidate if accepted else state]
            counts[target] = counts.get(target, 0) + 1
        assert sum(counts.values()) == 6
        rows.append(counts)
    return tuple(rows)


def components(rows):
    """Strong components by mutual reachability, sufficient for 18 states."""
    reaches = []
    for start in range(len(rows)):
        found = {start}
        pending = [start]
        while pending:
            for target in rows[pending.pop()]:
                if target not in found:
                    found.add(target)
                    pending.append(target)
        reaches.append(found)
    remaining = set(range(len(rows)))
    parts = []
    while remaining:
        first = min(remaining)
        part = {target for target in reaches[first] if first in reaches[target]}
        parts.append(part)
        remaining.difference_update(part)
    return parts


def solve(matrix, right):
    """Exact Gauss-Jordan elimination with several right-hand sides."""
    n = len(matrix)
    if not n:
        return []
    augmented = [list(map(Fraction, row)) + list(map(Fraction, values)) for row, values in zip(matrix, right)]
    width = len(augmented[0])
    for column in range(n):
        pivot = next(row for row in range(column, n) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row != column and augmented[row][column]:
                factor = augmented[row][column]
                augmented[row] = [
                    augmented[row][j] - factor * augmented[column][j] for j in range(width)
                ]
    return [row[n:] for row in augmented]


def absorption(rows):
    """Closed classes, their uniform stationary readouts, and hitting laws."""
    closed = [part for part in components(rows) if all(target in part for state in part for target in rows[state])]
    closed.sort(key=min)
    class_of = {state: c for c, part in enumerate(closed) for state in part}
    transient = [state for state in range(len(rows)) if state not in class_of]
    transient_index = {state: i for i, state in enumerate(transient)}
    matrix = [[0] * len(transient) for _ in transient]
    right = [[0] * len(closed) for _ in transient]
    for state in transient:
        i = transient_index[state]
        matrix[i][i] = 6
        for target, count in rows[state].items():
            if target in class_of:
                right[i][class_of[target]] += count
            else:
                matrix[i][transient_index[target]] -= count
    solved = solve(matrix, right)
    probabilities = []
    for state in range(len(rows)):
        if state in class_of:
            probabilities.append(tuple(Fraction(int(c == class_of[state])) for c in range(len(closed))))
        else:
            probabilities.append(tuple(solved[transient_index[state]]))
    records = []
    averages = []
    for c, part in enumerate(closed):
        # A closed cycle preserves the violation set and cannot decrease the
        # one-way bit. Thus transitions inside each class are symmetric.
        assert all(rows[s].get(t, 0) == rows[t].get(s, 0) for s in part for t in part if s != t)
        average = Fraction(sum(bit(STATES[s], READ) for s in part), len(part))
        averages.append(average)
        records.append(
            {
                "class_id": c,
                "states": [word(STATES[s]) for s in sorted(part)],
                "read_values": sorted({bit(STATES[s], READ) for s in part}),
                "stationary_y1": str(average),
            }
        )
    for values in probabilities:
        assert sum(values) == 1 and all(value >= 0 for value in values)
    reward = [sum((p * averages[c] for c, p in enumerate(values)), Fraction()) for values in probabilities]
    return {"classes": records, "probabilities": probabilities, "reward": reward}


def class_distribution(counts, denominator, settled):
    return [
        sum((Fraction(counts[s], denominator) * settled["probabilities"][s][c] for s in range(len(STATES))), Fraction())
        for c in range(len(settled["classes"]))
    ]


def pulse(rows, neutral, initial):
    counts = [0] * len(STATES)
    counts[INDEX[initial]] = 1
    denominator = 1
    immediate = []
    later = []
    for horizon in range(max(HORIZONS) + 1):
        if horizon in HORIZONS:
            immediate.append(str(Fraction(sum(counts[s] for s in range(len(STATES)) if bit(STATES[s], READ)), denominator)))
            later.append(str(sum((Fraction(counts[s], denominator) * neutral["reward"][s] for s in range(len(STATES))), Fraction())))
        if horizon < max(HORIZONS):
            updated = [0] * len(STATES)
            for source, count in enumerate(counts):
                for target, multiplicity in rows[source].items():
                    updated[target] += count * multiplicity
            counts = updated
            denominator *= 6
    distribution = class_distribution(counts, denominator, neutral)
    support = [neutral["classes"][c] for c, p in enumerate(distribution) if p]
    return {
        "y1_immediate": immediate,
        "y1_after_neutral_limit": later,
        "pulse_state_support_at_last_horizon": [word(STATES[s]) for s, count in enumerate(counts) if count],
        "settled_classes_at_last_horizon": [
            {"class_id": c, "probability": str(p)} for c, p in enumerate(distribution) if p
        ],
        "settled_state_support_at_last_horizon": sorted({state for record in support for state in record["states"]}),
    }


def reachable_union(kernels, starts):
    found = {INDEX[state] for state in starts}
    pending = list(found)
    while pending:
        source = pending.pop()
        for rows in kernels:
            for target in rows[source]:
                if target not in found:
                    found.add(target)
                    pending.append(target)
    return sorted(found)


def sustained(rows, analysis):
    # Stop on first y=1 only in this external hitting-probability calculation.
    hitting_rows = tuple({s: 6} if bit(STATES[s], READ) else row for s, row in enumerate(rows))
    hitting = absorption(hitting_rows)
    result = []
    for initial in (*CLEAR, *LOADED):
        s = INDEX[initial]
        permanent = sum(
            (analysis["probabilities"][s][c] for c, record in enumerate(analysis["classes"]) if record["read_values"] == [1]),
            Fraction(),
        )
        result.append(
            {
                "initial": word(initial),
                "initial_kind": "clear" if initial in CLEAR else "loaded",
                "ever_y1_probability": str(hitting["reward"][s]),
                "limit_y1_probability": str(analysis["reward"][s]),
                "eventually_permanently_y1_probability": str(permanent),
                "terminal_class_probabilities": [
                    {"class_id": c, "probability": str(p)}
                    for c, p in enumerate(analysis["probabilities"][s]) if p
                ],
            }
        )
    return result


def variant_report(name, couplings):
    dynamics = []
    for one_way in (False, True):
        kernels = {raw: kernel(raw, couplings, one_way) for raw in RAW_WORDS}
        analyses = {raw: absorption(rows) for raw, rows in kernels.items()}
        neutral = analyses[NEUTRAL]
        mixed = [rows for raw, rows in kernels.items() if len(set(raw)) > 1]
        mixed_only = []
        for initial in CLEAR:
            reached = reachable_union(mixed, (initial,))
            mixed_only.append(
                {
                    "initial": word(initial),
                    "reachable_states": [word(STATES[s]) for s in reached],
                    "y1_reachable": any(bit(STATES[s], READ) for s in reached),
                }
            )
        all_after_loaded = reachable_union(list(kernels.values()), LOADED)
        pulses = []
        for raw, rows in kernels.items():
            for initial in (*CLEAR, *LOADED):
                pulses.append(
                    {
                        "raw": raw_word(raw),
                        "initial": word(initial),
                        "initial_kind": "clear" if initial in CLEAR else "loaded",
                        **pulse(rows, neutral, initial),
                    }
                )
        dynamics.append(
            {
                "name": "one_way_y" if one_way else "symmetric",
                "blocked_transition": "y:1->0" if one_way else None,
                "neutral_word": raw_word(NEUTRAL),
                "neutral_classes": neutral["classes"],
                "mixed_only": mixed_only,
                "loaded_retention_under_arbitrary_raw_sequences": {
                    "reachable_states": [word(STATES[s]) for s in all_after_loaded],
                    "y0_reachable": any(bit(STATES[s], READ) == 0 for s in all_after_loaded),
                },
                "sustained": [
                    {"raw": raw_word(raw), "closed_classes": analyses[raw]["classes"], "starts": sustained(rows, analyses[raw])}
                    for raw, rows in kernels.items()
                ],
                "pulses": pulses,
            }
        )
    return {
        "name": name,
        "couplings": [{"raw_port": RAW_NAMES[p], "negated": bool(sign), "core_ports": "ax"} for p, sign in couplings],
        "dynamics": dynamics,
    }


def shortest_path(rows, initial, predicate):
    first = INDEX[initial]
    previous = {first: None}
    pending = deque([first])
    target = None
    while pending:
        source = pending.popleft()
        if predicate(STATES[source]):
            target = source
            break
        for neighbor in rows[source]:
            if neighbor not in previous:
                previous[neighbor] = source
                pending.append(neighbor)
    if target is None:
        return None
    indices = []
    while target is not None:
        indices.append(target)
        target = previous[target]
    indices.reverse()
    steps = []
    for source, target in zip(indices, indices[1:]):
        difference = STATES[source] ^ STATES[target]
        port = next(p for p in range(6) if difference == 1 << (5 - p))
        steps.append({"flip": CORE_NAMES[port], "after": word(STATES[target])})
    return {"initial": word(initial), "steps": steps, "last": word(STATES[indices[-1]])}


def examples():
    couplings = ((0, 0), (1, 0), (2, 0))
    neutral_rows = kernel(NEUTRAL, couplings, True)
    result = []
    for raw in ((0, 0, 0), (1, 1, 1)):
        rows = kernel(raw, couplings, True)
        for initial in CLEAR:
            capture = shortest_path(rows, initial, lambda s: bit(s, READ) == 1)
            if capture is None:
                result.append({"raw": raw_word(raw), "initial": word(initial), "capture": None})
                continue
            captured = int(capture["last"], 2)
            settle = shortest_path(neutral_rows, captured, lambda s: not violations(s, NEUTRAL, couplings))
            result.append({"raw": raw_word(raw), "capture": capture, "common_neutral_settle": settle})
    return result


def upper_probe():
    return {
        "allowed_words_ypq": ["".join(map(str, values)) for values in product((0, 1), repeat=3) if nae(values)],
        "by_memory": [
            {
                "y": value,
                "allowed_queries_pq": ["".join(map(str, query)) for query in product((0, 1), repeat=2) if nae((value, *query))],
                "initial_pq": "01",
                "proposed_q": 0,
                "proposal_accepted": nae((value, 0, 0)),
                "resulting_pq": "00" if nae((value, 0, 0)) else "01",
            }
            for value in (0, 1)
        ],
        "severed": {
            "replacement": "independent h",
            "allowed_queries_after_forgetting_h": ["00", "01", "10", "11"],
            "matched_q_proposal_by_h": {str(value): nae((value, 0, 0)) for value in (0, 1)},
            "memory_y_has_no_incidence": True,
        },
    }


def run():
    started = perf_counter()
    base_couplings = ((0, 0), (1, 0), (2, 0))
    specifications = [("original", base_couplings)]
    specifications += [(f"remove_{RAW_NAMES[p]}", tuple(c for c in base_couplings if c[0] != p)) for p in range(3)]
    specifications += [(f"flip_{RAW_NAMES[p]}", tuple((q, int(q == p)) for q in range(3))) for p in range(3)]
    specifications.append(("uncoupled_raw", ()))
    variants = []
    first_signal = None
    for name, couplings in specifications:
        variants.append(variant_report(name, couplings))
        if first_signal is None:
            first_signal = perf_counter() - started
    here = Path(__file__).resolve().parent
    return {
        "schema_version": 1,
        "experiment_id": "SIX-BIT-EVENT-20261111-001-E001",
        "evidence_stage": "exploratory",
        "branch": "training",
        "core_order": CORE_NAMES,
        "raw_order": RAW_NAMES,
        "core_states": [word(s) for s in STATES],
        "starts": {"clear": [word(s) for s in CLEAR], "loaded": [word(s) for s in LOADED]},
        "horizons": list(HORIZONS),
        "probabilities": "Exact Fraction strings; each finite pulse uses 6^h equally likely proposal words.",
        "settling": "Raw changes atomically to 001; limit under that same indefinitely held word, without feedback or capture-based stopping.",
        "variants": variants,
        "coverage": {
            "variants": len(variants),
            "dynamics_per_variant": 2,
            "raw_words": len(RAW_WORDS),
            "initial_states": len(CLEAR) + len(LOADED),
            "pulse_rows": sum(len(d["pulses"]) for v in variants for d in v["dynamics"]),
            "horizons_per_pulse": len(HORIZONS),
        },
        "representative_paths": examples(),
        "upper_probe": upper_probe(),
        "runtime_seconds": {"first_original_report": first_signal, "total": perf_counter() - started},
        "contract_sha256": hashlib.sha256((here / "contract.json").read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "nonclaims": [
            "The sensor geometry, atomic raw source, clear preparation and update rule are supplied.",
            "The one-way preference is an added irreversible law, not formed by the four hard constraints.",
            "The finite pulse schedules are fixed in advance and do not wait for capture.",
            "A one-bit record and supplied downstream knot do not learn an arbitrary hidden rule or assemble their wiring.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="-", help="Destination JSON; '-' writes stdout. Existing files are preserved.")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, separators=(",", ":"), sort_keys=True) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        with Path(args.output).open("x", encoding="utf-8") as output:
            output.write(text)


if __name__ == "__main__":
    main()
