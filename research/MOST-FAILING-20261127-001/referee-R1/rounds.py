"""Check all round-by-round maxima on the later odd-attainable closures.

Use the earlier independent growth and check construction in core.py. Starting
with every new pair failing, a local maximum omits the fewest pairs needed to
meet the current parity checks. Breadth-first search gives that minimum:
repeating any column on a shortest XOR path would cancel two moves and produce
a shorter path. Enumerate minimum omissions in increasing column index, then
count their contributions to the later checks and the closing sign. Prefixes
with the same contributions have exactly the same future options.

Run from the repository root. A limited run leaves the output file alone.
"""

import argparse
import json
import resource
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache, reduce
from itertools import chain, combinations
from operator import xor
from pathlib import Path
from time import monotonic


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / "LOCAL-COMMUTE-20261127-001"
sys.path.insert(0, str(PRIOR / "referee-R1"))
from core import basis, closing_cost, commutation, history, read_starts, remainder


LABELS = "ascending distinction labels"
REVERSE_LABELS = "descending distinction labels"
KNOTS = "first occurrence in census knot order"
REVERSE_KNOTS = "first occurrence with knots reversed within each round"
POLICIES = (LABELS, REVERSE_LABELS, KNOTS, REVERSE_KNOTS)


@dataclass(frozen=True)
class Round:
    pairs: tuple
    rank: int
    columns: tuple
    priorities: tuple


@dataclass
class Extensions:
    count: int
    # For each policy, the pair (omission priority, chosen failing pairs mask).
    choices: list


@dataclass
class Prefixes:
    count: int
    example: tuple


def appearances(state, order):
    distinctions = dict.fromkeys(chain.from_iterable(state.knots[i] for i in order))
    return {distinction: index for index, distinction in enumerate(distinctions)}


def priorities(pairs, first_appearance, reversed_appearance):
    def by_appearance(pair, labels):
        return tuple(sorted(labels[d] for d in pair))

    rankings = (
        pairs,
        reversed(pairs),
        sorted(pairs, key=lambda pair: by_appearance(pair, first_appearance)),
        sorted(pairs, key=lambda pair: by_appearance(pair, reversed_appearance)),
    )
    result = []
    for ranking in rankings:
        weights = {pair: 1 << (len(pairs) - 1 - index) for index, pair in enumerate(ranking)}
        result.append(tuple(weights[pair] for pair in pairs))
    return tuple(result)


def independent_checks(states, final_rows):
    """Keep one check for each pivot in the new columns of a growth round."""
    earlier_basis = {}
    grouped = []
    old_width = 0
    old_knots = 0
    # The full rows are supplied in the order of pairs of knots in the closure.
    by_round = [[] for _ in states]
    knot_round = states[-1].knot_round
    for (first, second), row in zip(combinations(range(len(knot_round)), 2), final_rows, strict=True):
        by_round[knot_round[second]].append(row)
    for state, round_rows in zip(states, by_round, strict=True):
        width = old_width + len(state.new_birth_pairs)
        new_mask = (1 << width) - (1 << old_width)
        pivots = {}
        keep = []
        for row in round_rows:
            assert row >> width == 0
            reduced = remainder(row, pivots)
            new_part = reduced & new_mask
            if new_part:
                pivot = (new_part & -new_part).bit_length() - 1
                pivots[pivot] = reduced
                keep.append(row)
            else:
                # The dropped check follows from already tested checks.
                # Thus every allowed prefix has a full set of extensions.
                assert remainder(reduced, earlier_basis) == 0
        grouped.append(tuple(keep))
        earlier_basis = basis(chain(earlier_basis.values(), keep))
        assert len(round_rows) == sum(range(old_knots, len(state.knots)))
        old_knots = len(state.knots)
        old_width = width
    return grouped


def prepare(states):
    final = states[-1]
    pairs = tuple(chain.from_iterable(state.new_birth_pairs for state in states))
    assert set(pairs) == set(final.birth_pairs) and len(pairs) == len(set(pairs))
    rows = tuple(commutation(final, pairs))
    cost = closing_cost(final, pairs)
    pivots = basis(rows)
    if not remainder(cost, pivots):
        return None

    order = tuple(range(len(final.knots)))
    reverse_within_round = tuple(
        knot for state in states for knot in reversed(order) if final.knot_round[knot] == state.round
    )
    for (first, second), row in zip(combinations(order, 2), rows, strict=True):
        rest = tuple(knot for knot in order if knot not in (first, second))
        before = closing_cost(final, pairs, (first, second) + rest)
        after = closing_cost(final, pairs, (second, first) + rest)
        assert before ^ after == row
        assert remainder(cost ^ before, pivots) == 0
    assert remainder(cost ^ closing_cost(final, pairs, reverse_within_round), pivots) == 0

    checks = independent_checks(states, rows)
    tracked = tuple(chain.from_iterable(checks)) + (cost,)
    tracked_basis = basis(tracked[:-1])
    assert len(tracked_basis) == len(pivots)
    assert all(remainder(row, tracked_basis) == 0 for row in rows)
    first_appearance = appearances(final, order)
    reversed_appearance = appearances(final, reverse_within_round)
    rounds = []
    row_offset = 0
    column_offset = 0
    for state, local_checks in zip(states, checks, strict=True):
        new_pairs = state.new_birth_pairs
        columns = tuple(
            sum(((row >> bit) & 1) << index for index, row in enumerate(tracked[row_offset:]))
            for bit in range(column_offset, column_offset + len(new_pairs))
        )
        rounds.append(Round(new_pairs, len(local_checks), columns,
                            priorities(new_pairs, first_appearance, reversed_appearance)))
        row_offset += len(local_checks)
        column_offset += len(new_pairs)
    return rounds, pairs, order, reverse_within_round, len(rows)


def shortest_distances(rank, columns, targets):
    distances = [-1] * (1 << rank)
    distances[0] = 0
    pending = set(targets) - {0}
    queue = deque([0])
    generators = tuple(sorted(set(columns) - {0}))
    while pending:
        # Every target is reachable by the surjectivity check in independent_checks.
        current = queue.popleft()
        next_distance = distances[current] + 1
        for column in generators:
            reached = current ^ column
            if distances[reached] < 0:
                distances[reached] = next_distance
                queue.append(reached)
                pending.discard(reached)
    return distances


def shortest_omissions(columns, rank, distances, target):
    """Yield each minimum omission mask and its contribution to later checks and sign."""
    current_mask = (1 << rank) - 1
    candidates = tuple((column & current_mask, column >> rank) for column in columns)

    def visit(remaining, first, omissions, later):
        distance = distances[remaining]
        if distance == 0:
            yield omissions, later
            return
        for index in range(first, len(candidates) - distance + 1):
            current, next_later = candidates[index]
            if distances[remaining ^ current] == distance - 1:
                yield from visit(remaining ^ current, index + 1, omissions | (1 << index), later ^ next_later)

    yield from visit(target, 0, 0, 0)


def omission_priorities(omissions, priorities_by_policy):
    scores = [0] * len(priorities_by_policy)
    rest = omissions
    while rest:
        bit = rest & -rest
        index = bit.bit_length() - 1
        for policy, priorities in enumerate(priorities_by_policy):
            scores[policy] |= priorities[index]
        rest ^= bit
    return scores


def optimal_extensions(current, earlier_targets):
    width = len(current.pairs)
    all_failing = (1 << width) - 1
    current_mask = (1 << current.rank) - 1
    all_effects = reduce(xor, current.columns, 0)
    all_current = all_effects & current_mask
    all_later = all_effects >> current.rank
    targets = {prefix: prefix ^ all_current for prefix in earlier_targets}
    distances = shortest_distances(current.rank, [c & current_mask for c in current.columns], targets.values())
    result = {}
    for prefix, target in targets.items():
        groups = {}
        for omissions, later in shortest_omissions(current.columns, current.rank, distances, target):
            word = all_failing ^ omissions
            contribution = later ^ all_later
            choices = [(score, word) for score in omission_priorities(omissions, current.priorities)]
            if contribution in groups:
                group = groups[contribution]
                group.count += 1
                group.choices = [min(a, b) for a, b in zip(group.choices, choices, strict=True)]
            else:
                groups[contribution] = Extensions(1, choices)
        assert groups
        result[prefix] = (width - distances[target], groups)
    return result


def explore(rounds):
    prefixes = {(0, ()): Prefixes(1, ())}
    policies = [(0, ()) for _ in POLICIES]
    prefix_counts = []
    for current in rounds:
        mask = (1 << current.rank) - 1
        local = optimal_extensions(current, sorted({effect & mask for effect, _ in prefixes}))
        advanced = {}
        for (effect, weights), prefix in prefixes.items():
            weight, groups = local[effect & mask]
            for contribution, extensions in groups.items():
                signature = ((effect >> current.rank) ^ contribution, weights + (weight,))
                count = prefix.count * extensions.count
                if signature in advanced:
                    advanced[signature].count += count
                else:
                    advanced[signature] = Prefixes(count, prefix.example + (extensions.choices[0][1],))
        for index, (effect, path) in enumerate(policies):
            _, groups = local[effect & mask]
            _, word, contribution = min((*entry.choices[index], change) for change, entry in groups.items())
            policies[index] = ((effect >> current.rank) ^ contribution, path + (word,))
        prefixes = advanced
        prefix_counts.append(sum(entry.count for entry in prefixes.values()))
    assert all(sign in (0, 1) for sign, _ in prefixes)
    return prefixes, policies, prefix_counts


def sign_name(bit):
    return "odd" if bit else "even"


def selected_pairs(pairs, word):
    assert 0 <= word < 1 << len(pairs)
    return tuple(pair for index, pair in enumerate(pairs) if word & (1 << index))


def check_path(states, rounds, pairs, path, expected, orders):
    """Check certificates against the direct commutation equations and product."""
    width = 0
    word = 0
    for state, current, chosen in zip(states, rounds, path, strict=True):
        assert 0 <= chosen < 1 << len(current.pairs)
        word |= chosen << width
        width += len(current.pairs)
        assert all((row & word).bit_count() % 2 == 0 for row in commutation(state, pairs[:width]))
    assert all((closing_cost(states[-1], pairs, order) & word).bit_count() % 2 == expected for order in orders)
    return {"sign": sign_name(expected), "round weights": [word.bit_count() for word in path],
            "round masks": list(path)}


def describe(states, rounds, choices, orders):
    return {
        "knots by growth round": [
            [knot for index, knot in enumerate(state.knots) if state.knot_round[index] == state.round]
            for state in states
        ],
        "decision pairs by round": [current.pairs for current in rounds],
        "knot orders": orders,
        "choices": {
            name: {
                "sign under both knot orders": record["sign"],
                "round weights": record["round weights"],
                "omitted pairs by round": [
                    selected_pairs(current.pairs, ((1 << len(current.pairs)) - 1) ^ word)
                    for current, word in zip(rounds, record["round masks"], strict=True)
                ],
            } for name, record in choices.items()
        },
    }


def census_rows(path):
    with path.open() as source:
        yield from map(json.loads, source)


def affine_solver(rows, offset, width):
    """List all maximum words by direct elimination and enumeration in one round."""
    @cache
    def solve(rhs):
        pivots = {}
        for index, row in enumerate(rows):
            equation = row >> offset
            parity = (rhs >> index) & 1
            while equation:
                pivot = equation.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = (equation, parity)
                    break
                previous, previous_parity = pivots[pivot]
                equation ^= previous
                parity ^= previous_parity
            if not equation:
                assert parity == 0

        def complete(word, homogeneous):
            for pivot, (equation, parity) in sorted(pivots.items()):
                if (word & equation).bit_count() % 2 != (0 if homogeneous else parity):
                    word |= 1 << pivot
            return word

        word = complete(0, False)
        directions = [complete(1 << index, True) for index in range(width) if index not in pivots]
        best = word.bit_count()
        choices = [word]
        for counter in range(1, 1 << len(directions)):
            word ^= directions[(counter & -counter).bit_length() - 1]
            weight = word.bit_count()
            if weight > best:
                best = weight
                choices = [word]
            elif weight == best:
                choices.append(word)
        return choices

    return solve


def interleaving_cost(state, pairs):
    positions = defaultdict(list)
    for index, distinction in enumerate(chain.from_iterable(state.knots)):
        positions[distinction].append(index)
    cost = 0
    for index, (left, right) in enumerate(pairs):
        a, b = positions[left]
        c, d = positions[right]
        if a < c < b < d or c < a < d < b:
            cost |= 1 << index
    return cost


def check_by_affine_enumeration(result):
    """Recount without syndrome search, merged prefixes or the cancellation check."""
    starts = read_starts()
    total = 0
    for record in result["rows"]:
        states = history(starts[record["census index"]]).states
        final = states[-1]
        pairs = tuple(chain.from_iterable(state.new_birth_pairs for state in states))
        order = tuple(range(len(final.knots)))
        reverse_order = tuple(
            knot for state in states for knot in reversed(order) if final.knot_round[knot] == state.round
        )
        labels = (appearances(final, order), appearances(final, reverse_order))
        prefixes = [(0, ())]
        policy_words = [0] * len(POLICIES)
        counts = []
        offset = 0
        for state in states:
            width = len(state.new_birth_pairs)
            rows = tuple(commutation(state, pairs[:offset + width]))
            solve = affine_solver(rows, offset, width)

            def rhs_of(prefix):
                return sum(((prefix & row).bit_count() % 2) << index for index, row in enumerate(rows))

            prefixes = [
                (prefix | (word << offset), weights + (word.bit_count(),))
                for prefix, weights in prefixes
                for word in solve(rhs_of(prefix))
            ]
            rankings = [range(width), reversed(range(width))]
            for mapping in labels:
                rankings.append(sorted(range(width),
                                       key=lambda index: sorted(mapping[d] for d in state.new_birth_pairs[index])))
            for index, ranking in enumerate(rankings):
                ordering = tuple(ranking)
                options = solve(rhs_of(policy_words[index]))
                word = max(options, key=lambda choice: tuple((choice >> j) & 1 for j in ordering))
                policy_words[index] |= word << offset
            offset += width
            counts.append(len(prefixes))

        cost = interleaving_cost(final, pairs)
        observed = Counter((sign_name((word & cost).bit_count() % 2), weights) for word, weights in prefixes)
        expected = {
            (sign, tuple(choice["round weights"])): choice["histories"]
            for sign, choices in record["exact histories by sign and weight profile"].items()
            for choice in choices
        }
        assert observed == expected, record["census index"]
        assert counts == record["maximum-weight prefixes through each round"], record["census index"]
        for name, observed_word in zip(POLICIES, policy_words, strict=True):
            offset = 0
            for width, expected_word in zip(record["decidable pairs per round"],
                                            record["tie-breaks preferring earlier failing pairs"][name]["round masks"],
                                            strict=True):
                assert (observed_word >> offset) & ((1 << width) - 1) == expected_word, record["census index"]
                offset += width
        total += len(prefixes)
    return total


def audit(limit=None):
    starts = read_starts()
    candidates = [
        row for row in census_rows(PRIOR / "results.jsonl")
        if row["end"] == "closed" and row.get("closing round", 0) >= 2
    ]
    rows = {}
    witnesses = {}
    exchange_checks = 0
    for candidate in candidates[:limit]:
        index = candidate["start"]
        growth = history(starts[index])
        states = growth.states
        assert growth.end == "closed" and states[-1].round == candidate["closing round"]
        prepared = prepare(states)
        assert bool(prepared) == candidate["birth choices attain odd"]
        if prepared is None:
            continue
        rounds, pairs, order, reverse_order, checks = prepared
        exchange_checks += checks
        assert not rounds[-1].pairs and rounds[-1].rank == 0
        prefixes, policies, prefix_counts = explore(rounds)
        orders = (order, reverse_order)
        by_sign = defaultdict(list)
        for (sign, weights), result in sorted(prefixes.items()):
            witness = check_path(states, rounds, pairs, result.example, sign, orders)
            assert tuple(witness["round weights"]) == weights
            witness["histories"] = result.count
            by_sign[sign_name(sign)].append(witness)
        chosen = {
            name: check_path(states, rounds, pairs, path, sign, orders)
            for name, (sign, path) in zip(POLICIES, policies, strict=True)
        }
        rows[index] = {
            "census index": index,
            "closing round": states[-1].round,
            "decidable pairs per round": [len(current.pairs) for current in rounds],
            "independent new checks per round": [current.rank for current in rounds],
            "maximum-weight prefixes through each round": prefix_counts,
            "exact histories by sign and weight profile": dict(by_sign),
            "tie-breaks preferring earlier failing pairs": chosen,
        }
        cases = (
            ("different pair order changes the selected sign", LABELS, REVERSE_LABELS),
            ("different knot order changes the selected sign via first occurrence", KNOTS, REVERSE_KNOTS),
        )
        for name, first, second in cases:
            if name not in witnesses and chosen[first]["sign"] != chosen[second]["sign"]:
                witnesses[name] = {"census index": index,
                                   **describe(states, rounds, {key: chosen[key] for key in (first, second)}, orders)}
        if "round-by-round maxima permit both signs" not in witnesses and len(by_sign) == 2:
            # A sign witness need only attain the per-prefix local maxima.
            examples = {name: by_sign[name][0] for name in ("even", "odd")}
            witnesses["round-by-round maxima permit both signs"] = {
                "census index": index, **describe(states, rounds, examples, orders)
            }

    archived = {
        row["start"]: row for row in census_rows(HERE.parent / "results.jsonl")
        if row["closing round"] >= 2
    }
    if limit is not None:
        tested = {candidate["start"] for candidate in candidates[:limit]}
        archived = {index: row for index, row in archived.items() if index in tested}
    archived_counts = Counter()
    verdicts = Counter()
    archived_agree = certain_agree = possible_agree = forced_global = 0
    policy_counts = {name: Counter() for name in POLICIES}
    policy_agreements = Counter()
    policy_mismatches = {name: [] for name in POLICIES}
    whole_weight_comparison = Counter()
    forced_disagreements = []
    tie_dependent_agreements = []
    order_dependent_selections = []
    unsupported = []
    for index, row in rows.items():
        signs = row["exact histories by sign and weight profile"]
        verdicts["free" if len(signs) == 2 else f"forced {next(iter(signs))}"] += 1
        reference = archived.get(index, {})
        archived_sign = reference.get("round-by-round maximum closing sign")
        archived_counts[archived_sign or "absent"] += 1
        row["archived round-by-round sign"] = archived_sign
        row["archived sign is attainable under ties"] = archived_sign in signs
        if archived_sign not in signs:
            unsupported.append(index)
        global_verdict = reference.get("max principle")
        global_weight = reference.get("max weight")
        row["archived whole-closure maximum"] = {"weight": global_weight, "verdict": global_verdict}
        totals = sorted({sum(record["round weights"]) for profiles in signs.values() for record in profiles})
        row["possible round-by-round total weights"] = totals
        if global_weight is not None:
            assert totals[-1] <= global_weight
            if totals[-1] < global_weight:
                whole_weight_comparison["no history reaches the whole-closure maximum"] += 1
            elif len(totals) > 1:
                whole_weight_comparison["some histories reach the whole-closure maximum"] += 1
            else:
                whole_weight_comparison["all histories reach the whole-closure maximum"] += 1
        if global_verdict in ("forced odd", "forced even"):
            expected = global_verdict.split()[-1]
            forced_global += 1
            archived_agree += archived_sign == expected
            certain_agree += set(signs) == {expected}
            possible_agree += expected in signs
            if expected not in signs:
                forced_disagreements.append(index)
            elif len(signs) > 1:
                tie_dependent_agreements.append(index)
        else:
            expected = None
        choices = row["tie-breaks preferring earlier failing pairs"]
        if choices[KNOTS]["sign"] != choices[REVERSE_KNOTS]["sign"]:
            order_dependent_selections.append(index)
        for policy, record in choices.items():
            policy_counts[policy][record["sign"]] += 1
            policy_agreements[policy] += record["sign"] == expected
            if record["sign"] != archived_sign:
                policy_mismatches[policy].append(index)

    return {
        "scope": "Later grown closures in the earlier census, up to four rounds and 40 knots, with odd attainable.",
        "weighting": "One vote per census start. History counts give one to each complete set of pair decisions.",
        "later closure candidates examined": len(candidates[:limit]),
        "odd-attainable closures examined": len(rows),
        "complete round-by-round maximum histories across the examined closures":
            sum(row["maximum-weight prefixes through each round"][-1] for row in rows.values()),
        "closures by closing round": dict(Counter(row["closing round"] for row in rows.values())),
        "knot-pair exchange checks": exchange_checks,
        "every admissible prefix admits an extension": True,
        "closing rounds with no new decision pairs or independent new checks": len(rows),
        "archive comparison": {
            "archived sign counts": dict(archived_counts),
            "census indices in only one roster": sorted(rows.keys() ^ archived.keys()),
            "census indices with an unsupported archived sign": unsupported,
            "archived agreement with forced whole-closure maxima": [archived_agree, forced_global],
            "minimum and maximum agreement with forced whole-closure maxima over all ties":
                [certain_agree, possible_agree, forced_global],
            "census indices with unavoidable sign disagreement": forced_disagreements,
            "census indices with tie-dependent sign agreement": tie_dependent_agreements,
            "round-by-round weights compared with archived whole-closure maxima": dict(whole_weight_comparison),
            "archive limitation": "The archived round-by-round sign gives no chosen word or round weights.",
        },
        "verdicts over all sequentially maximum histories": dict(verdicts),
        "odd count range when ties are chosen independently for each start":
            [verdicts["forced odd"], verdicts["forced odd"] + verdicts["free"]],
        "counts for explicit deterministic tie-breaks": {name: dict(counts) for name, counts in policy_counts.items()},
        "agreement with forced whole-closure maxima for explicit deterministic tie-breaks":
            {name: [agreement, forced_global] for name, agreement in policy_agreements.items()},
        "census indices where explicit tie-breaks differ from the archived sign": policy_mismatches,
        "census indices where the first-occurrence tie-break changes sign when the knots are reordered":
            order_dependent_selections,
        "round mask interpretation":
            "The least significant bit is the first eligible pair that round, in ascending distinction-label order.",
        "witnesses": witnesses,
        "rows": list(rows.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="check only that many later candidates, without writing")
    parser.add_argument("--verify-affine", action="store_true",
                        help="independently enumerate affine choices to check counts, weights and tie policies")
    args = parser.parse_args()
    started = monotonic()
    result = audit(args.limit)
    if args.verify_affine:
        histories = check_by_affine_enumeration(result)
        print(f"Direct enumeration confirms {histories} complete histories and every recorded tie-policy word.")
    if args.limit is None:
        (HERE / "rounds.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in {"rows", "witnesses"}}, indent=2))
    print(f"Elapsed {monotonic() - started:.2f} s, peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KiB")


if __name__ == "__main__":
    main()
