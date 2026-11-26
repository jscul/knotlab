"""Count reading orders of fixed ordinary-growth birth-parent histories."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations, permutations
import json
from math import factorial, prod
from pathlib import Path
import resource
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fold

CENSUS = HERE.parents[1] / "FORBID-EDITS-20261126-001" / "starts.json"
MAX_BIRTHS = 20
BRUTE_FORCE_MAX = 8
PAIRED_MAX_IDEALS = 150_000
PAIRED_MAX_SECOND_CANDIDATES = 2_000_000


class PairedCountBudgetExceeded(Exception):
    pass


def sample_starts():
    for places in (3, 4):
        yield f"lone {places}-place knot", (tuple(range(places)),)
    for shared in (1, 2):
        for first in range(3 - shared, 4):
            for second in range(first, 4):
                start = fold.forbid.supports_of((2, ((0, 1, shared),), (first, second)))
                name = f"two knots, {shared} shared and {first}/{second} loose distinctions"
                yield name, start
    for index, start in enumerate(json.loads(CENSUS.read_text())):
        knots, meetings, loose = start
        if knots != 3 or (index >= 4 and not 1 <= sum(loose) <= 2):
            continue
        name = f"three-knot census start {index}, shared counts {[m for _, _, m in meetings]}, loose counts {loose}"
        yield name, fold.forbid.supports_of(start)


def birth_order(number_of_knots, starts, parent_pairs):
    parents = [set() for _ in range(number_of_knots)]
    children = [set() for _ in parents]
    for child, parent in parent_pairs:
        assert parent < child and child not in starts
        parents[child].add(parent)
        children[parent].add(child)
    births = sorted(set(range(number_of_knots)) - starts)
    assert all(parents[birth] for birth in births)
    predecessors = {}
    successors = {}
    for birth in births:
        direct = parents[birth] - starts
        predecessors[birth] = direct.union(*(predecessors[parent] for parent in direct))
    for birth in reversed(births):
        direct = children[birth]
        successors[birth] = direct.union(*(successors[child] for child in direct))
    return births, predecessors, successors, parents, children


def parity_counts(births, predecessors):
    bit = {birth: 1 << index for index, birth in enumerate(births)}
    prerequisites = [sum(bit[p] for p in predecessors[birth]) for birth in births]
    full = (1 << len(births)) - 1

    @cache
    def completions(ideal):
        if ideal == full:
            return 1, 0
        even = odd = 0
        pending = full ^ ideal
        while pending:
            next_bit = pending & -pending
            pending ^= next_bit
            if prerequisites[next_bit.bit_length() - 1] & ~ideal:
                continue
            next_even, next_odd = completions(ideal | next_bit)
            if (ideal >> next_bit.bit_length()).bit_count() % 2:
                next_even, next_odd = next_odd, next_even
            even += next_even
            odd += next_odd
        return even, odd

    result = completions(0)
    completions.cache_clear()
    return result


def brute_count(births, required_pairs):
    even = odd = 0
    for order in permutations(births):
        position = {birth: index for index, birth in enumerate(order)}
        if any(position[parent] > position[child] for child, parent in required_pairs):
            continue
        inversions = sum(first > second for first, second in combinations(order, 2))
        if inversions % 2:
            odd += 1
        else:
            even += 1
    return even, odd


def paired_imbalance(births, predecessors, successors):
    """Cancel by exchanging the first incomparable pair of consecutive positions."""
    bit = {birth: 1 << index for index, birth in enumerate(births)}
    prerequisites = [sum(bit[p] for p in predecessors[birth]) for birth in births]
    following = [sum(bit[s] for s in successors[birth]) for birth in births]
    full = (1 << len(births)) - 1
    visited = candidates_checked = 0

    @cache
    def contributions(ideal):
        nonlocal visited, candidates_checked
        visited += 1
        if visited > PAIRED_MAX_IDEALS:
            raise PairedCountBudgetExceeded("ideal budget reached")
        unplaced = full ^ ideal
        if not unplaced:
            return 1
        if unplaced.bit_count() == 1:
            inversions = (ideal >> unplaced.bit_length()).bit_count()
            return -1 if inversions % 2 else 1

        signed = 0
        first_choices = unplaced
        while first_choices:
            first = first_choices & -first_choices
            first_choices ^= first
            first_index = first.bit_length() - 1
            if prerequisites[first_index] & ~ideal:
                continue
            with_first = ideal | first
            first_inversions = (ideal >> first.bit_length()).bit_count()
            second_choices = following[first_index] & unplaced
            while second_choices:
                candidates_checked += 1
                if candidates_checked > PAIRED_MAX_SECOND_CANDIDATES:
                    raise PairedCountBudgetExceeded("second-birth candidate budget reached")
                second = second_choices & -second_choices
                second_choices ^= second
                if prerequisites[second.bit_length() - 1] & ~with_first:
                    continue
                inversions = first_inversions + (with_first >> second.bit_length()).bit_count()
                signed_next = contributions(with_first | second)
                signed += -signed_next if inversions % 2 else signed_next
        return signed

    try:
        return contributions(0), visited, candidates_checked
    finally:
        contributions.cache_clear()


def keeps_distinction_holdings(pair, holders, barred):
    first, second = pair
    swap = {first: second, second: first}
    original = Counter((distinction in barred, frozenset(knots))
                       for distinction, knots in holders.items())
    swapped = Counter((distinction in barred, frozenset(swap.get(k, k) for k in knots))
                      for distinction, knots in holders.items())
    return original == swapped


def parent_guard_witness(births, predecessors, parents, children):
    for birth in births:
        for parent in sorted(parents[birth]):
            for grandparent in sorted(parents[parent]):
                unfinished = children[grandparent] - predecessors[birth] - {birth}
                if unfinished:
                    return {
                        "birth": birth,
                        "parent": parent,
                        "parent_of_parent": grandparent,
                        "unfinished_child": min(unfinished),
                        "ideal": sorted(predecessors[birth]),
                    }
    return None


def measure(stage, barred, reading, widths):
    starts, parent_pairs = reading
    births, predecessors, successors, parents, children = birth_order(len(stage), starts, parent_pairs)
    twins = [(a, b) for a, b in combinations(births, 2)
             if predecessors[a] == predecessors[b] and successors[a] == successors[b]]
    fixed_start = [(a, b) for a, b in twins if parents[a] == parents[b] and children[a] == children[b]]
    holders = fold.forbid.holders(stage)
    fixed_start_and_holdings = [pair for pair in fixed_start
                                if keeps_distinction_holdings(pair, holders, barred)]
    round_orders = prod(factorial(width) for width in widths)
    round_imbalance = int(round_orders == 1)
    result = {
        "birth_count": len(births),
        "round_widths": list(widths),
        "parent_pairs_child_first": sorted(parent_pairs),
        "strict_order_twins": twins,
        "fixed_start_parent_record_twins": fixed_start,
        "fixed_start_parent_record_and_final_holdings_twins": fixed_start_and_holdings,
        "guard_R1_excluded_parent_order_witness": parent_guard_witness(births, predecessors, parents, children),
        "complete_round_sensitivity": {"orders": round_orders, "imbalance": round_imbalance},
        "brute_force_checked": False,
    }
    try:
        signed, visited, checked = paired_imbalance(births, predecessors, successors)
        result["paired_count_work"] = {"ideals": visited, "second_birth_candidates": checked}
    except PairedCountBudgetExceeded as error:
        signed = None
        result["paired_count_not_run_to_completion"] = str(error)
    if len(births) > MAX_BIRTHS:
        result["counts_not_run"] = f"more than {MAX_BIRTHS} births"
        if signed is not None:
            assert not twins or signed == 0
            result.update(imbalance=signed, imbalance_method="consecutive comparable pairs")
        elif twins:
            result.update(imbalance=0, imbalance_method="transposition of order twins")
        else:
            result["imbalance_not_run"] = "paired count reached its budget"
        return result
    even, odd = parity_counts(births, predecessors)
    if len(births) <= BRUTE_FORCE_MAX:
        direct_pairs = [(child, parent) for child, parent in parent_pairs if parent not in starts]
        assert (even, odd) == brute_count(births, direct_pairs)
        result["brute_force_checked"] = True
    assert not twins or even == odd
    assert signed is None or signed == even - odd
    result.update(even=even, odd=odd, imbalance=even - odd, imbalance_method="separate even and odd counts")
    return result


def control_checks():
    # A twin pair, a three-birth chain with a singleton, and two two-birth chains.
    controls = [
        (range(2), [], (1, 1)),
        (range(4), [(1, 0), (2, 1)], (2, 2)),
        (range(4), [(1, 0), (3, 2)], (4, 2)),
    ]
    for births, pairs, expected in controls:
        predecessors = {birth: {p for node, p in pairs if node == birth} for birth in births}
        assert parity_counts(births, predecessors) == expected
        assert brute_count(births, pairs) == expected


def run(rounds, smoke):
    records = []
    starts = list(sample_starts())
    if smoke:
        starts = [starts[i] for i in (0, 1, 2, 11, 15)]
    for engine in ("fold", "canonical"):
        fold.ENGINE = engine
        for law in ("nae", "parity"):
            for name, supports in starts:
                history = []
                widths = []
                preceding_knots = len(supports)
                for index, stage, barred, reading in fold.grow(supports, law, rounds):
                    widths.append(len(stage) - preceding_knots)
                    assert widths[-1] > 0
                    row = measure(stage, barred, reading, widths)
                    row["round"] = index
                    history.append(row)
                    preceding_knots = len(stage)
                records.append({
                    "start": name,
                    "start_supports": supports,
                    "engine": engine,
                    "law": law,
                    "end": "round cutoff" if len(history) == rounds else "growth iterator stopped",
                    "histories": history,
                })
    return records


def summarize(records):
    histories = [history for record in records for history in record["histories"]]
    signed = [row for row in histories if "imbalance" in row]
    no_twins = [row for row in signed if not row["strict_order_twins"]]
    return {
        "runs": len(records),
        "runs_without_a_birth": sum(not record["histories"] for record in records),
        "growth_iterator_stops": sum(record["end"] == "growth iterator stopped" for record in records),
        "nonempty_histories": len(histories),
        "histories_with_separate_even_and_odd_counts": sum("even" in row for row in histories),
        "histories_with_separate_counts_not_run": sum("counts_not_run" in row for row in histories),
        "histories_with_computed_imbalance": len(signed),
        "histories_with_imbalance_not_run": len(histories) - len(signed),
        "histories_with_paired_count_cross_check": sum(
            "even" in row and "paired_count_work" in row for row in histories),
        "histories_with_brute_force_check": sum(row["brute_force_checked"] for row in histories),
        "histories_with_order_twins": sum(bool(row["strict_order_twins"]) for row in histories),
        "histories_with_fixed_start_parent_record_twins": sum(
            bool(row["fixed_start_parent_record_twins"]) for row in histories),
        "histories_with_fixed_start_parent_record_and_final_holdings_twins": sum(
            bool(row["fixed_start_parent_record_and_final_holdings_twins"]) for row in histories),
        "histories_with_a_parent_order_excluded_by_R1": sum(
            bool(row["guard_R1_excluded_parent_order_witness"]) for row in histories),
        "twin_free_counted_imbalance_frequency": dict(sorted(Counter(row["imbalance"] for row in no_twins).items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    started_at = perf_counter()
    control_checks()
    records = run(args.rounds, args.smoke)
    summary = summarize(records)
    canonical = [record for record in records if record["engine"] == "canonical"]
    replay = [record for record in records if record["engine"] == "fold"]
    engines_agree = [{k: v for k, v in r.items() if k != "engine"} for r in canonical] == [
        {k: v for k, v in r.items() if k != "engine"} for r in replay]
    result = {
        "command": ".venv/bin/python -B " + " ".join(sys.argv),
        "weighting": "One count per nonempty (start, engine, law, completed round) with all four combinations counted separately. Each order of a fixed history has equal magnitude; its weight is its permutation sign.",
        "sample": "Lone three- and four-place knots, all two-knot starts with one or two shared distinctions and up to three loose distinctions per knot allowing at least three places each, the first four recorded three-knot census starts, and all recorded three-knot census starts with one or two loose distinctions in total.",
        "history": "Fixed parent record from ordinary growth. The order is the transitive closure on births after excluding the existing start knots. The sign reference is increasing birth label.",
        "twins": "The swap alone preserves the strict birth order exactly when both strict predecessor and successor sets agree. The stronger columns additionally fix each start knot and preserve direct parent pairs, and then preserve final distinction holdings up to recoding that also preserves barring.",
        "complete_round_sensitivity": "Requires every birth of an earlier round to precede every birth of a later round. Neither count enumerates one-birth-at-a-time guarded schedules.",
        "round_bound": args.rounds,
        "count_birth_bound": MAX_BIRTHS,
        "brute_force_birth_bound": BRUTE_FORCE_MAX,
        "paired_count_limits_per_history": {
            "ideals": PAIRED_MAX_IDEALS,
            "second_birth_candidates": PAIRED_MAX_SECOND_CANDIDATES,
        },
        "summary": summary,
        "engines_agree": engines_agree,
        "summary_one_engine_per_start_and_law": {
            law: summarize([r for r in canonical if r["law"] == law]) for law in ("nae", "parity")
        } if engines_agree else None,
        "measurement_before_serialization": {
            "wall_seconds": perf_counter() - started_at,
            "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "runs": records,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
