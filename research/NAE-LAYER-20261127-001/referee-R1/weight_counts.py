"""Exact counts under the equal weighting of every allowed assignment."""

import argparse
from fractions import Fraction
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
import resource
from time import perf_counter

from growth_rule import advance, loose


def bitmask(places):
    return sum(1 << place for place in places)


def counts(laws, readers, *, width=None, stop_word=None):
    laws = tuple(bitmask(law) for law in laws)
    readers = tuple(bitmask(group) for group in readers)
    if width is None:
        width = max(laws + readers).bit_length()
    rows = [0] * (1 << len(readers))
    stop = (1 << width) if stop_word is None else min(stop_word, 1 << width)
    for word in range(stop):
        if all(0 < (word & law) < law for law in laws):
            output = 0
            for mask in readers:
                output = 2 * output + ((word & mask).bit_count() % 2)
            rows[output] += 1
    return rows


def marginal(rows, kept):
    width = (len(rows) - 1).bit_length()
    result = [0] * (1 << len(kept))
    for index, count in enumerate(rows):
        output = 0
        for position in kept:
            output = 2 * output + ((index >> (width - position - 1)) & 1)
        result[output] += count
    return result


def summary(rows):
    width = (len(rows) - 1).bit_length()
    n = sum(rows)
    separate = [marginal(rows, [i]) for i in range(width)]
    independent = all(
        count * n ** (width - 1) == prod(separate[i][v] for i, v in enumerate(word))
        for count, word in zip(rows, product(range(2), repeat=width), strict=True)
    )
    even = prod(count for i, count in enumerate(rows) if i.bit_count() % 2 == 0)
    odd = prod(count for i, count in enumerate(rows) if i.bit_count() % 2)
    return {
        "counts_in_lexicographic_order": rows,
        "allowed_assignments": n,
        "support_size": sum(v > 0 for v in rows),
        "marginals": separate,
        "independent": independent,
        "even_over_odd_product": str(Fraction(even, odd)) if odd else None,
    }


def power_set_indices(n):
    return (c for size in range(n + 1) for c in combinations(range(n), size))


def ring(n):
    return tuple((i, (i + 1) % n, n + i) for i in range(n))


def ring_test(n):
    laws = ring(n)
    readers = [(n + i, n + i + 1) for i in range(0, n, 2)]
    full = counts(laws, readers)
    subsets = {}
    for retained in power_set_indices(n):
        reading = summary(counts([laws[i] for i in retained], readers, width=2 * n))
        subsets[" ".join(map(str, retained))] = reading
    proper = [reading for key, reading in subsets.items() if len(key.split()) < n]
    assert all(reading["independent"] for reading in proper)
    assert not summary(full)["independent"]
    return {
        "source_knots": laws,
        "readers_on_loose_distinctions": readers,
        "source": summary(full),
        "all_proper_reader_marginals": {
            str(kept): summary(marginal(full, kept))
            for kept in power_set_indices(len(readers))
            if 0 < len(kept) < len(readers)
        },
        "law_subsets_with_unlisted_distinctions_left_free": subsets,
        "independent_proper_law_subsets": sum(row["independent"] for row in proper),
    }


def eight_knot_check(pilot=False):
    laws = ring(8)
    readers = tuple((8 + i, 9 + i) for i in range(0, 8, 2))
    last = 1024 if pilot else None
    rows = counts(laws, readers, stop_word=last)
    cut = counts(laws[1:], readers, width=16, stop_word=last)
    if pilot:
        return {"states_visited_per_roster": last, "allowed": [sum(rows), sum(cut)]}
    predicted = [5 ** (4 - i.bit_count()) * 4 ** i.bit_count() + (i == 0) for i in range(16)]
    assert rows == predicted and summary(cut)["independent"]
    return {"knots": laws, "readers": readers, "truth_table": summary(rows),
            "transfer_formula_counts": predicted, "first_law_removed": summary(cut)}


def ring_growth(n, pilot=False):
    laws = ring(n)
    readers = [(n + i, n + i + 1) for i in range(0, n, 2)]
    result = []
    stage = laws
    for distance in range(3):
        old = counts(stage, readers)
        movable = loose(stage)
        entry = {"round": distance, "laws": stage, "old_readers": summary(old),
                 "current_loose": movable}
        if len(movable) == 2:
            entry["two_current_loose"] = summary(counts(stage, [(i,) for i in movable]))
        if len(movable) == 4 and distance == 2:
            entry["one_fresh_distinction_from_each_offshoot"] = summary(
                counts(stage, [(movable[0],), (movable[2],)]))
            entry["both_fresh_distinctions_from_each_offshoot"] = summary(
                counts(stage, [movable[:2], movable[2:]]))
        if distance and not pilot:
            entry["delete_one_law"] = [
                summary(counts(stage[:i] + stage[i + 1:], readers,
                               width=1 + max(v for law in stage for v in law)))
                for i in range(len(stage))
            ]
        result.append(entry)
        if distance < 2:
            following = advance(stage)
            assert following.status == "funded"
            stage = following.supports
    newborns = (tuple(range(n, 2*n, 2)) + (2*n,), tuple(range(n+1, 2*n, 2)) + (2*n+1,))
    assert result[1]["laws"] == laws + newborns
    assert result[2]["laws"] == result[1]["laws"] + (
        (2*n, 2*n+2, 2*n+3), (2*n+1, 2*n+4, 2*n+5))
    return result


def tree_claim():
    laws = ((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 8))
    # Distinctions 1, 3, 5, 7 are loose on four successive knots.
    interleaved = ((1, 5), (3, 7))
    connected = ((1, 3), (5, 7))
    data = {name: summary(counts(laws, readers)) for name, readers in (
        ("interleaved", interleaved), ("connected", connected))}
    rows = data["interleaved"]["counts_in_lexicographic_order"]
    n = sum(rows)
    mean = lambda vector: str(Fraction(vector[0] - vector[1], sum(vector)))
    data["interleaved_sign_means"] = [mean(marginal(rows, [i])) for i in (0, 1)]
    data["interleaved_product_mean"] = str(Fraction(rows[0] - rows[1] - rows[2] + rows[3], n))
    data.update({"knots": laws, "interleaved_supports": interleaved, "connected_supports": connected})
    return data


def even_expansion(laws, read_places):
    # Under the uniform count on all words an odd occurrence sums to zero.
    factors = []
    for law in laws:
        denominator = 2 ** (len(law) - 1) - 1
        choices = [(0, Fraction(1))]
        for size in range(2, len(law) + 1, 2):
            choices.extend((bitmask(group), Fraction(-1, denominator))
                           for group in combinations(law, size))
        factors.append(choices)
    desired = bitmask(read_places)
    totals = {0: Fraction(), desired: Fraction()}
    for chosen in product(*factors):
        remaining = 0
        for support, _ in chosen:
            remaining ^= support
        if remaining in totals:
            totals[remaining] += prod(weight for _, weight in chosen)
    return totals[desired], totals[0]


def weighted_pairs():
    cases = {
        "four_adjacent_shared": (ring(4), (0, 1)),
        "three_adjacent_shared": (ring(3), (0, 1)),
        "four_adjacent_shared_remote_edit": (
            tuple(law + (8,) if i == 2 else law for i, law in enumerate(ring(4))), (0, 1)),
        "two_loose_at_one_knot_on_a_ring": (((0, 1, 3, 4), (1, 2, 5), (2, 0, 6)), (3, 4)),
    }
    result = {}
    for name, (laws, pair) in cases.items():
        observed = counts(laws, [pair])
        signed = Fraction(observed[0] - observed[1], sum(observed))
        numerator, denominator = even_expansion(laws, pair)
        assert signed == numerator / denominator
        result[name] = {"knots": laws, "read_distinctions": pair, "even_odd_counts": observed,
                        "signed_mean": str(signed), "expansion_numerator": str(numerator),
                        "expansion_denominator": str(denominator)}
    main = ring(4)
    shared, private = tuple(range(4)), tuple(range(4, 8))
    result["ring_four_parities"] = {
        "all_shared": counts(main, [shared]), "all_loose": counts(main, [private]),
        "after_one_deletion_shared": counts(main[1:], [shared], width=8),
        "after_one_deletion_loose": counts(main[1:], [private], width=8),
        "shared_and_loose": counts(main, [shared, private])}
    return result


def unread(laws, readers):
    outcomes = []
    width = 1 + max(v for law in laws for v in law)
    for carrier in readers:
        knot_reads = []
        for i, law in enumerate(laws):
            blocks = counts(laws, [*((p,) for p in law), carrier], width=width)
            possible = [blocks[j:j + 2] for j in range(0, len(blocks), 2) if sum(blocks[j:j + 2])]
            knot_reads.append({"knot": i, "realized_local_patterns": len(possible),
                               "allow_both_reader_values": sum(all(row) for row in possible)})
        outcomes.append(knot_reads)
    return outcomes


def independent_three():
    # Each allowed three-place word supplies one pair of fair, correlated signs.
    laws = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    readers = ((0, 7), (3, 1), (6, 4))
    observed = counts(laws, readers)
    return {"knots": laws, "readers": readers, "source": summary(observed),
            "pairs": [summary(marginal(observed, pair)) for pair in combinations(range(3), 2)],
            "every_proper_law_subset": {
                str(kept): summary(counts([laws[i] for i in kept], readers, width=9))
                for kept in power_set_indices(3) if len(kept) < 3}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = perf_counter()
    if args.pilot:
        # The same readers and full configurations as the main run, each on
        # one member of its test roster.
        four = ring_test(4)
        six = ring(6)
        six_counts = counts(six, [(6, 7), (8, 9), (10, 11)])
        timed_growth = [ring_growth(n, pilot=True) for n in (4, 6)]
        result = {"four_state_count": four["source"]["allowed_assignments"],
                  "six_state_count": sum(six_counts),
                  "growth_rounds_per_ring": [len(stages) for stages in timed_growth],
                  "eight_knot_prefix": eight_knot_check(pilot=True)}
    else:
        four = ring_test(4)
        six = ring_test(6)
        for row in (four, six):
            row["any_single_knot_reads_carriers"] = unread(row["source_knots"], row["readers_on_loose_distinctions"])
        result = {"four_ring": four, "six_ring": six, "four_ring_growth": ring_growth(4),
                  "six_ring_growth": ring_growth(6), "eight_ring": eight_knot_check(),
                  "four_knot_chain": tree_claim(), "spin_expansion": weighted_pairs(),
                  "three_independent_knots_control": independent_three()}
    result["seconds"] = perf_counter() - started
    result["peak_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result["memory_limit_bytes"] = resource.getrlimit(resource.RLIMIT_AS)[0]
    data = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
