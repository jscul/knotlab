"""Rebuild the ordinary not-all-equal whole-growth division control.

The ordered census is an input. Growth, allowed states, and determinants are
computed independently. The wider 14-distinction filter checks the antecedent
factoring study and distinguishes the starting width from the finishing width.
"""

import argparse
from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from time import perf_counter


CENSUS = Path(__file__).resolve().parents[2] / "FORBID-EDITS-20261126-001" / "starts.json"
SEED = 20261129
SAMPLE_SIZE = 300
NARROW_CAP = 9
WIDER_CAP = 14
ROUND_LIMIT = 2


def start_scopes(record):
    count, shares, loose = record
    scopes = [[] for _ in range(count)]
    free = 0
    for a, b, multiplicity in shares:
        names = list(range(free, free + multiplicity))
        scopes[a].extend(names)
        scopes[b].extend(names)
        free += multiplicity
    for scope, multiplicity in zip(scopes, loose, strict=True):
        scope.extend(range(free, free + multiplicity))
        free += multiplicity
    return tuple(map(tuple, scopes)), free


def birth_groups(neighbors, live):
    pairs = {pair for pair in combinations(live, 2) if neighbors[pair[0]] & neighbors[pair[1]]}
    valid = []

    def visit(prefix, remaining):
        if len(prefix) >= 3 and not set.intersection(*(neighbors[i] for i in prefix)):
            valid.append(prefix)
        for position, chosen in enumerate(remaining):
            next_remaining = tuple(i for i in remaining[position + 1:] if (chosen, i) in pairs)
            visit(prefix + (chosen,), next_remaining)

    visit((), tuple(i for i in live if any(i in pair for pair in pairs)))
    members = [frozenset(group) for group in valid]
    maximal = [group for group, member in zip(valid, members, strict=True) if not any(member < other for other in members)]
    covered_pairs = {pair for group in maximal for pair in combinations(group, 2)}
    return sorted(maximal) + sorted(pairs - covered_pairs)


def bit_mask(scope):
    return sum(1 << d for d in scope)


def possible_with_zeroes(scopes):
    """Return a test for an allowed state with the specified distinctions zero.

    Complement symmetry also answers the corresponding all-one query.
    """
    masks = tuple(map(bit_mask, scopes))

    @cache
    def satisfiable(zero, one):
        branches = []
        for scope in masks:
            need_zero, need_one = not (scope & zero), not (scope & one)
            if not (need_zero or need_one):
                continue
            choices = scope & ~(zero | one)
            if not choices:
                return False
            if need_zero:
                branches.append((choices.bit_count(), choices, False))
            if need_one:
                branches.append((choices.bit_count(), choices, True))
        if not branches:
            return True
        _, choices, value = min(branches)
        while choices:
            bit = choices & -choices
            choices ^= bit
            new_zero, new_one = (zero, one | bit) if value else (zero | bit, one)
            if satisfiable(new_zero, new_one):
                return True
        return False

    return lambda scope: satisfiable(bit_mask(scope), 0)


def next_round(scopes, width):
    owners = defaultdict(list)
    for holder, scope in enumerate(scopes):
        for distinction in scope:
            owners[distinction].append(holder)
    neighbors = [set() for _ in scopes]
    for holding in owners.values():
        if len(holding) == 2:
            a, b = holding
            neighbors[a].add(b)
            neighbors[b].add(a)
        else:
            assert len(holding) == 1
    loose = {i: [d for d in scope if len(owners[d]) == 1] for i, scope in enumerate(scopes)}
    live = tuple(i for i, names in loose.items() if names)
    if not live:
        return scopes, width, "closed"

    groups = birth_groups(neighbors, live)
    group_uses = Counter(i for group in groups for i in group)
    if any(group_uses[i] > len(loose[i]) for i in live):
        return scopes, width, "stalled"
    inputs = [tuple(loose[i].pop(0) for i in group) for group in groups]
    for i in live:
        groups.extend((i,) for _ in loose[i])
        inputs.extend((d,) for d in loose[i])

    # Provisional births meet a common prior holder exactly when their
    # parent sets intersect. This gives the next round's demand before topping up.
    demands = Counter(i for group in birth_groups(list(map(set, groups)), tuple(range(len(groups)))) for i in group)
    if_all_zero = possible_with_zeroes(scopes)
    births = []
    for i, taken in enumerate(inputs):
        demand = demands[i]
        with_floor = max(demand, 1, 3 - len(taken))
        fresh_count = with_floor if with_floor == demand or if_all_zero(taken) else demand
        births.append(taken + tuple(range(width, width + fresh_count)))
        width += fresh_count
    return scopes + tuple(births), width, "funded"


def allowed_states(scopes, width):
    masks = tuple(map(bit_mask, scopes))
    return [word for word in range(1 << width) if all(0 < (word & scope) < scope for scope in masks)]


def values(state, distinctions):
    return [(state >> d) & 1 for d in distinctions]


def determinants(scopes, initial_width, width):
    states = allowed_states(scopes, width)
    old_mask = (1 << initial_width) - 1
    completions = Counter(word & old_mask for word in states)
    denominators = {word: completions[word & old_mask] for word in states}
    together = {pair for scope in scopes for pair in combinations(sorted(scope), 2)}
    pairs = list(pair for pair in combinations(range(width), 2) if pair not in together)
    checked = failed = 0
    witness = None
    for a, b in pairs:
        a_mask, b_mask = 1 << a, 1 << b
        fixed_mask = ~(a_mask | b_mask)
        fixed_states = {word & fixed_mask for word in states}
        checked += len(fixed_states)
        for fixed in sorted(fixed_states):
            d00 = denominators.get(fixed, 0)
            d01 = denominators.get(fixed | b_mask, 0)
            d10 = denominators.get(fixed | a_mask, 0)
            d11 = denominators.get(fixed | a_mask | b_mask, 0)
            # Each positive entry is the reciprocal of its completion count.
            # Compare products of denominators, then handle absent entries.
            diagonal, off_diagonal = d00 * d11, d01 * d10
            if diagonal == off_diagonal:
                continue
            failed += 1
            if witness is None:
                rest = [d for d in range(width) if d not in (a, b)]
                witness = {
                    "read_distinctions": [a, b],
                    "fixed_distinctions": rest,
                    "fixed_values": values(fixed, rest),
                    "weight_table_before_normalization": [
                        [f"1/{d}" if d else "0" for d in row] for row in ((d00, d01), (d10, d11))
                    ],
                }
    return {
        "allowed_finish_states": len(states),
        "starting_words_with_completions": len(completions),
        "pairs_checked": len(pairs),
        "positive_mass_tables_checked": checked,
        "zero_tables_omitted": len(pairs) * (1 << (width - 2)) - checked,
        "nonzero_determinants": failed,
        "first_nonzero_determinant": witness,
    }


def summarize(rows, cap):
    retained = [row for row in rows if row["funded_rounds"] and row["finishing_distinctions"] <= cap]
    failures = [row for row in retained if row["nonzero_determinants"]]
    return {
        "cap_on_finishing_distinctions": cap,
        "starts_examined": len(rows),
        "excluded_no_funded_round": sum(not row["funded_rounds"] for row in rows),
        "excluded_over_cap_with_funded_round": sum(
            bool(row["funded_rounds"]) and row["finishing_distinctions"] > cap for row in rows
        ),
        "retained_and_determinant_checked": len(retained),
        "distinct_pairs_summed_over_retained_growths": sum(row["pairs_checked"] for row in retained),
        "positive_mass_tables_checked": sum(row["positive_mass_tables_checked"] for row in retained),
        "zero_tables_omitted": sum(row["zero_tables_omitted"] for row in retained),
        "nonzero_determinants": sum(row["nonzero_determinants"] for row in retained),
        "growths_with_nonzero_determinants": len(failures),
        "sample_indices_with_nonzero_determinants": [row["census_index"] for row in failures],
        "start_width_at_most_nine_with_nonzero_determinants": [
            row["census_index"] for row in failures if row["starting_distinctions"] <= NARROW_CAP
        ],
    }


def run(prefix):
    begun = perf_counter()
    source = CENSUS.read_bytes()
    census = json.loads(source)
    picks = Random(SEED).sample(range(len(census)), SAMPLE_SIZE)
    rows = []
    growth_wall = determinant_wall = 0.0
    for position, index in enumerate(picks[:prefix], start=1):
        step_started = perf_counter()
        initial, initial_width = start_scopes(census[index])
        scopes, width = initial, initial_width
        statuses, stage_widths = [], []
        for _ in range(ROUND_LIMIT):
            scopes, width, status = next_round(scopes, width)
            statuses.append(status)
            if status != "funded":
                break
            stage_widths.append(width)
        growth_wall += perf_counter() - step_started
        row = {
            "sample_position_one_based": position,
            "census_index": index,
            "starting_distinctions": initial_width,
            "funded_rounds": len(stage_widths),
            "round_attempt_statuses": statuses,
            "width_after_each_funded_round": stage_widths,
            "finishing_distinctions": width,
        }
        if stage_widths and width <= WIDER_CAP:
            step_started = perf_counter()
            row.update(determinants(scopes, initial_width, width))
            row.update({"start_scopes": initial, "finish_scopes": scopes})
            determinant_wall += perf_counter() - step_started
        rows.append(row)
    narrow = summarize(rows, NARROW_CAP)
    first_failure = next((row for row in rows if row["finishing_distinctions"] <= NARROW_CAP and row.get("nonzero_determinants")), None)
    return {
        "source": "research/FORBID-EDITS-20261126-001/starts.json",
        "source_sha256": sha256(source).hexdigest(),
        "census_size": len(census),
        "sample_seed": SEED,
        "full_sample_size": SAMPLE_SIZE,
        "sampled_without_replacement": True,
        "round_limit": ROUND_LIMIT,
        "law": "not-all-equal",
        "growth_arm": "ordinary",
        "primary_filter": narrow,
        "wider_filter_for_predecessor_check": summarize(rows, WIDER_CAP),
        "first_eligible_failure_in_sample_order": first_failure,
        "eligible_quantum_control_cases": int(first_failure is not None),
        "quantum_control_runs": 0,
        "elapsed_seconds": {
            "growth": round(growth_wall, 6),
            "determinants": round(determinant_wall, 6),
            "total": round(perf_counter() - begun, 6),
        },
        "peak_rss_kib": getrusage(RUSAGE_SELF).ru_maxrss,
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int, default=SAMPLE_SIZE)
    args = parser.parse_args()
    if not 1 <= args.prefix <= SAMPLE_SIZE:
        parser.error(f"--prefix must be between 1 and {SAMPLE_SIZE}")
    print(json.dumps(run(args.prefix), indent=2, sort_keys=True))
