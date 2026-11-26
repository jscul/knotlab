"""Rebuild the read-set tables from the earlier raw census holder lists.

On a basis word x, distinction i toggles i and gives a minus sign for each
unheld pair (j, i) with j < i present in x. Each distinction is an involution
with the prescribed R signs. Project the zero basis word onto the common
signed knot eigenspace, and recover each read set's outcome probabilities
from its moments by an exact inverse Walsh transform. Separately, form each
candidate law directly by counting swaps and cancelling repeated distinctions.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter


CENSUS = Path(
    "artifacts/FOUR-READINGS-20261120-001A/"
    "FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
)


def distinctions(mask):
    return tuple(i for i in range(mask.bit_length()) if mask & (1 << i))


def subsets(mask):
    yield 0
    part = mask
    while part:
        yield part
        part = (part - 1) & mask


def all_reads(compatible, candidates, read=0):
    yield read
    while candidates:
        next_bit = candidates & -candidates
        candidates ^= next_bit
        new_candidates = candidates & compatible[next_bit.bit_length() - 1]
        yield from all_reads(compatible, new_candidates, read | next_bit)


def act(word, basis, lower_unheld):
    sign = 1
    for i in reversed(word):
        if (basis & lower_unheld[i]).bit_count() % 2:
            sign = -sign
        basis ^= 1 << i
    return basis, sign


def act_on_state(word, state, lower_unheld):
    moved = {}
    for basis, coefficient in state.items():
        target, sign = act(word, basis, lower_unheld)
        moved[target] = coefficient * sign
    return moved


def project(word, sign, state, lower_unheld):
    moved = act_on_state(word, state, lower_unheld)
    result = state.copy()
    for basis, coefficient in moved.items():
        result[basis] = result.get(basis, 0) + sign * coefficient
    return {basis: coefficient for basis, coefficient in result.items() if coefficient}


def joint_state(knots, signs, lower_unheld):
    state = {0: 1}
    for knot, sign in zip(knots, signs, strict=True):
        state = project(knot, sign, state, lower_unheld)
    return state


def moment(word, state, norm_squared, lower_unheld):
    moved = act_on_state(word, state, lower_unheld)
    inner_product = sum(state.get(basis, 0) * coef for basis, coef in moved.items())
    value, remainder = divmod(inner_product, norm_squared)
    assert remainder == 0 and value in (-1, 0, 1)
    return value


def compute_product_laws(knots, signs, holders):
    signed_laws = set()
    gf2_laws = set()
    for count in range(len(knots) + 1):
        for chosen in combinations(range(len(knots)), count):
            word = tuple(i for k in chosen for i in knots[k])
            repeats = Counter(word)
            support = sum(1 << i for i, times in repeats.items() if times % 2)
            swaps = sum(i > j and holders[i].isdisjoint(holders[j])
                        for i, j in combinations(word, 2))
            sign = (-1) ** sum(signs[k] == -1 for k in chosen)
            gf2_laws.add((support, sign))
            signed_laws.add((support, sign * (-1) ** swaps))
    return signed_laws, gf2_laws


def restricted(laws, read):
    return [(support, sign) for support, sign in laws if support & read == support]


def parity(support, outcome):
    return (-1) ** ((support & outcome).bit_count() % 2)


def allowed_words(laws, outcomes):
    return {outcome for outcome in outcomes
            if all(parity(support, outcome) == sign for support, sign in laws)}


def cut_knots(knot_count, holders):
    result = []
    for removed in range(knot_count):
        remaining = set(range(knot_count)) - {removed}
        connected = {min(remaining)}
        while True:
            added = set().union(*(pair for pair in holders
                                 if removed not in pair and pair & connected))
            if added <= connected:
                break
            connected.update(added)
        if connected != remaining:
            result.append(removed)
    return result


def show_laws(laws):
    return [{"distinctions": distinctions(support), "sign": sign}
            for support, sign in sorted(laws)]


def check_type(type_number, row, examples):
    holders = tuple(frozenset(pair) for pair in row["sharing"])
    assert len(holders) == row["m"] == len(set(holders))
    assert all(len(pair) == 2 for pair in holders)
    knots = tuple(tuple(i for i, pair in enumerate(holders) if k in pair)
                  for k in range(row["n"]))
    assert sorted(map(len, knots)) == sorted(row["arities"])
    compatible = tuple(sum(1 << j for j, pair in enumerate(holders) if i != j and holder & pair)
                       for i, holder in enumerate(holders))
    lower_unheld = tuple(sum(1 << j for j in range(i) if holders[i].isdisjoint(holders[j]))
                         for i in range(len(holders)))
    if any(act(k + l, 0, lower_unheld) != act(l + k, 0, lower_unheld)
           for k, l in combinations(knots, 2)):
        return None

    full_word = tuple(i for knot in knots for i in knot)
    full_support, closing_sign = act(full_word, 0, lower_unheld)
    assert full_support == 0
    signs = (1,) * (len(knots) - 1) + (closing_sign,)
    state = joint_state(knots, signs, lower_unheld)
    assert state
    assert not joint_state(knots, signs[:-1] + (-closing_sign,), lower_unheld)
    norm_squared = sum(coef * coef for coef in state.values())
    for knot, sign in zip(knots, signs, strict=True):
        assert moment(knot, state, norm_squared, lower_unheld) == sign

    signed_laws, gf2_laws = compute_product_laws(knots, signs, holders)
    gf2_nonzero = [(support, sign) for support, sign in gf2_laws if support]
    knot_laws = [(sum(1 << i for i in knot), sign)
                 for knot, sign in zip(knots, signs, strict=True)]
    knot_supports = {support for support, _ in knot_laws}
    reads = sorted(all_reads(compatible, (1 << len(holders)) - 1),
                   key=lambda read: (read.bit_count(), read))
    assert len(reads) == len(set(reads))
    read_parities = {read: moment(distinctions(read), state, norm_squared, lower_unheld)
                     for read in reads}
    maximal_reads = sum(all(read | (1 << i) not in read_parities
                            for i in range(len(holders)) if not read & (1 << i))
                        for read in reads)
    assert maximal_reads > 0

    cuts = cut_knots(row["n"], holders)
    cut_supports = {knot_laws[k][0] for k in cuts}
    counts = {"nonempty": Counter(), "empty": Counter()}
    knot_reads_contradicted = 0
    for read in reads:
        tally = counts["nonempty" if read else "empty"]
        tally["read_sets"] += 1
        outcomes = tuple(subsets(read))
        laws = [(support, read_parities[support]) for support in outcomes if read_parities[support]]
        numerators = {outcome: sum(sign * parity(support, outcome) for support, sign in laws)
                      for outcome in outcomes}
        assert min(numerators.values()) >= 0 and sum(numerators.values()) == len(outcomes)
        reference = {outcome for outcome, numerator in numerators.items() if numerator}
        assert len({numerators[outcome] for outcome in reference}) == 1

        candidates = {
            "signed_products": restricted(signed_laws, read),
            "closed_part": restricted(knot_laws, read),
            "gf2_nonzero_support": restricted(gf2_nonzero, read),
            "gf2_with_identity": restricted(gf2_laws, read),
        }
        for name, candidate in candidates.items():
            predicted = allowed_words(candidate, outcomes)
            if predicted == reference:
                tally[f"{name}_agreement"] += 1
            elif not predicted:
                tally[f"{name}_contradiction"] += 1
            else:
                tally[f"{name}_mismatch"] += 1
                if len(predicted) == len(reference):
                    tally[f"{name}_mismatch_same_word_count"] += 1
                if predicted.isdisjoint(reference):
                    tally[f"{name}_mismatch_disjoint"] += 1

        if not allowed_words(candidates["gf2_nonzero_support"], outcomes):
            knot_reads_contradicted += read in knot_supports
            if "gf2_contradiction" not in examples:
                examples["gf2_contradiction"] = {
                    "type": type_number,
                    "holder_lists": row["sharing"],
                    "closing_sign": closing_sign,
                    "read_distinctions": distinctions(read),
                    "state_laws": show_laws(laws),
                    "gf2_laws": show_laws(candidates["gf2_with_identity"]),
                }
        if read in cut_supports:
            examples["cut_knot_read"] = {
                "type": type_number,
                "holder_lists": row["sharing"],
                "read_distinctions": distinctions(read),
                "allowed_words": {name: len(allowed_words(candidate, outcomes))
                                  for name, candidate in candidates.items()} | {"state": len(reference)},
                "state_laws": show_laws(laws),
                "closed_part_laws": show_laws(candidates["closed_part"]),
                "gf2_laws": show_laws(candidates["gf2_nonzero_support"]),
            }

    if len(knots) == 5 and len(holders) == 10:
        # These extra projectors commute with the knot projections.
        extra = (0,)
        assert all(act(knot + extra, 0, lower_unheld) == act(extra + knot, 0, lower_unheld)
                   for knot in knots)
        other_moments = []
        for sign in (-1, 1):
            modified = project(extra, sign, state, lower_unheld)
            norm = sum(coef * coef for coef in modified.values())
            assert norm > 0
            assert all(moment(knot, modified, norm, lower_unheld) == required
                       for knot, required in zip(knots, signs, strict=True))
            other_moments.append(moment(extra, modified, norm, lower_unheld))
        examples["different_states_with_the_same_knot_signs"] = {
            "type": type_number,
            "read_distinction": extra[0],
            "counting_state_moment": read_parities[1],
            "other_moments": other_moments,
        }

    summary = {
        "type": type_number,
        "atlas": row["atlas"],
        "knots": len(knots),
        "distinctions": len(holders),
        "closing_sign": closing_sign,
        "cut_knots": cuts,
        "maximal_reads": maximal_reads,
        "nonempty_reads": counts["nonempty"]["read_sets"],
        "closed_part_mismatches": counts["nonempty"]["closed_part_mismatch"],
        "gf2_nonzero_support_mismatches": counts["nonempty"]["gf2_nonzero_support_mismatch"],
        "gf2_nonzero_support_contradictions": counts["nonempty"]["gf2_nonzero_support_contradiction"],
        "knot_reads_contradicted": knot_reads_contradicted,
    }
    return summary, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Process a prefix of the raw census rows.")
    args = parser.parse_args()
    start = perf_counter()
    census_bytes = (Path(__file__).resolve().parents[3] / CENSUS).read_bytes()
    data = json.loads(census_bytes)[:args.limit]
    examples = {}
    all_counts = {"empty": Counter(), "nonempty": Counter()}
    rows = []
    for type_number, row in enumerate(data):
        result = check_type(type_number, row, examples)
        if result is None:
            continue
        summary, counts = result
        rows.append(summary)
        for scope in all_counts:
            all_counts[scope].update(counts[scope])
    output = {
        "input": str(CENSUS),
        "input_sha256": hashlib.sha256(census_bytes).hexdigest(),
        "census_types_read": len(data),
        "commuting_types": len(rows),
        "commuting_odd_types": sum(row["closing_sign"] == -1 for row in rows),
        "commuting_even_types": sum(row["closing_sign"] == 1 for row in rows),
        "maximal_reads": sum(row["maximal_reads"] for row in rows),
        "counts": all_counts,
        "examples": examples,
        "rows": rows,
        "wall_seconds": round(perf_counter() - start, 6),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
