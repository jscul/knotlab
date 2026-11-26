"""Rebuild the three-reader fixture from the ordinary one-round growth rules.

Growth follows the proposal and pricing rules in
research/ORDINARY-DYNAMICS-20261120-001/end_operator.md. The part counts and
the three-reader target are obtained by separate exact calculations.
"""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product


def words(length):
    return product((0, 1), repeat=length)


def project(word, distinctions):
    return tuple(word[d] for d in distinctions)


def states(width, equations):
    return [word for word in words(width)
            if all(sum(project(word, knot)) % 2 == sign for knot, sign in equations)]


def groups(live, witnesses):
    candidate_pairs = {
        frozenset(pair) for witness in witnesses
        for pair in combinations(sorted(witness), 2)
    }
    unheld = [
        frozenset(group)
        for size in range(3, len(live) + 1)
        for group in combinations(live, size)
        if all(frozenset(pair) in candidate_pairs for pair in combinations(group, 2))
        and not any(set(group) <= witness for witness in witnesses)
    ]
    maximal = [group for group in unheld if not any(group < rival for rival in unheld)]
    uncovered = [pair for pair in candidate_pairs if not any(pair <= group for group in maximal)]
    return sorted(tuple(sorted(group)) for group in maximal) + sorted(
        tuple(sorted(pair)) for pair in uncovered
    )


def ordinary_round(founders, old_states, width):
    holdings = Counter(d for knot in founders for d in knot)
    loose = {i: [d for d in sorted(knot) if holdings[d] == 1]
             for i, knot in enumerate(founders)}
    live = [i for i, distinctions in loose.items() if distinctions]
    witnesses = [
        {u for u in live if u != i and knot & founders[u]}
        for i, knot in enumerate(founders)
    ]
    proposed = groups(live, witnesses)
    obligations = Counter(u for group in proposed for u in group)
    assert all(obligations[u] <= len(loose[u]) for u in live), "Round stalled"

    allocated = {u: iter(loose[u]) for u in live}
    funded = [(group, tuple(next(allocated[u]) for u in group)) for group in proposed]
    funded.extend(((u,), (d,)) for u in live for d in allocated[u])
    assert Counter(d for _, inputs in funded for d in inputs) == {
        d: 1 for d, count in holdings.items() if count == 1
    }

    prospective = range(len(funded))
    next_witnesses = [{i for i, (group, _) in enumerate(funded) if u in group} for u in live]
    next_groups = groups(prospective, next_witnesses)
    demand = Counter(i for group in next_groups for i in group)
    births = []
    for i, (parents, inputs) in enumerate(funded):
        possible_signs = {sum(project(word, inputs)) % 2 for word in old_states}
        grant = demand[i] if possible_signs == {0} else max(demand[i], 3 - len(parents), 1)
        fresh = tuple(range(width, width + grant))
        width += grant
        births.append({"parents": parents, "inputs": inputs, "next_demand": demand[i],
                       "old_input_signs": sorted(possible_signs), "fresh": fresh})

    return witnesses, proposed, births


def distribution(support):
    count = Counter(support)
    total = count.total()
    assert total > 0
    return {word: Fraction(n, total) for word, n in count.items()}


def closed_part(context, equations):
    read_names = set(context)
    included = [(tuple(context.index(d) for d in knot), sign)
                for knot, sign in equations if knot <= read_names]
    return distribution(states(len(context), included))


def mermin_probability(setting, answer):
    # Squared overlap with (|000> - |111>) / sqrt(2). Setting 0 is X,
    # setting 1 is Y, and answer a labels eigenvalue (-1)**a in both bases.
    exponent = (2 * sum(answer) - sum(setting)) % 4
    real, imag = ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent]
    return Fraction((1 - real) ** 2 + imag ** 2, 16)


def marginal(table, positions):
    result = Counter()
    for word, probability in table.items():
        result[project(word, positions)] += probability
    return result


def check_overlaps(tables):
    pair_counts = Counter()
    equalities = 0
    for (left, left_table), (right, right_table) in combinations(tables.items(), 2):
        shared = sorted(set(left) & set(right))
        left_marginal = marginal(left_table, [left.index(d) for d in shared])
        right_marginal = marginal(right_table, [right.index(d) for d in shared])
        for word in words(len(shared)):
            assert left_marginal[word] == right_marginal[word], (left, right, word)
            equalities += 1
        pair_counts[len(shared)] += 1
    return pair_counts, equalities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-limit", type=int, choices=(2, 8), default=8)
    args = parser.parse_args()

    founders = tuple(map(frozenset, ((0, 1, 2), (1, 3, 4), (3, 0, 5))))
    holdings = Counter(d for knot in founders for d in knot)
    names = sorted(holdings)
    width = len(names)
    assert names == list(range(width))
    older_equations = [(knot, 0) for knot in founders]
    older_states = states(width, older_equations)
    witnesses, proposed, births = ordinary_round(founders, older_states, width)
    assert len(births) == 1
    (birth,) = births
    assert birth["inputs"] == (2, 4, 5) and not birth["fresh"] and birth["next_demand"] == 0
    assert birth["old_input_signs"] == [0]

    closing = frozenset(birth["inputs"])
    roster = founders + (closing,)
    assert Counter(d for knot in roster for d in knot) == dict.fromkeys(names, 2)
    assert all(len(a & b) == 1 for a, b in combinations(roster, 2))
    readers = [tuple(sorted(pair, key=holdings.__getitem__)) for pair in combinations(names, 2)
               if not any(set(pair) <= knot for knot in roster)]
    assert sorted(d for pair in readers for d in pair) == names
    assert all(holdings[x] == 1 and holdings[y] == 2 for x, y in readers)
    print(json.dumps({"growth": {"founders": [sorted(knot) for knot in founders],
                                  "witnesses": [sorted(witness) for witness in witnesses],
                                  "groups": proposed, "funded_births": births,
                                  "older_states": len(older_states), "readers_X_then_Y": readers}}))

    contexts = [(setting, tuple(pair[choice] for pair, choice in zip(readers, setting)))
                for setting in list(words(len(readers)))[:args.context_limit]]
    for closing_sign in (0, 1):
        equations = older_equations + [(closing, closing_sign)]
        whole = states(width, equations)
        assert whole == ([] if closing_sign else older_states)
        if whole:
            for knot in roster:
                assert len({project(word, sorted(knot)) for word in whole}) == 4
                for pair in combinations(sorted(knot), 2):
                    assert len({project(word, pair) for word in whole}) == 4

        tables = {}
        cells = Counter()
        controls = []
        target_mismatches = 0
        for setting, context in contexts:
            actual = closed_part(context, equations)
            tables[context] = actual
            assert sum(actual.values()) == 1
            whole_marginal = distribution(project(word, context) for word in whole) if whole else {}
            differences = 0
            for answer in words(len(context)):
                probability = actual.get(answer, Fraction(0))
                target = mermin_probability(setting, answer)
                differences += probability != target
                expected = target if closing_sign else whole_marginal.get(answer, Fraction(0))
                assert probability == expected, (closing_sign, setting, answer)
                cells[str(probability)] += 1

            support = frozenset(context)
            assert differences == (8 if closing_sign == 0 and support == closing else 0)
            target_mismatches += differences
            if support in roster:
                own_sign = dict(equations)[support]
                others = [(knot, sign) for knot, sign in equations if knot != support]
                other_words = states(width, others)
                projected = {project(word, context) for word in other_words}
                assert projected == {word for word in words(len(context))
                                     if sum(word) % 2 == own_sign ^ closing_sign}
                controls.append({"context": context, "own_sign": own_sign,
                                 "other_sign": own_sign ^ closing_sign,
                                 "other_states": len(other_words), "projected_words": len(projected)})

            print(json.dumps({"closing_sign": closing_sign, "setting": setting, "read": context,
                              "probabilities": {"".join(map(str, word)): str(actual.get(word, 0))
                                                for word in words(len(context))}}))

        overlap_pairs, overlap_equalities = check_overlaps(tables)
        print(json.dumps({"closing_sign": closing_sign, "whole_states": len(whole),
                          "zero_state_allowed": (0,) * width in whole,
                          "probabilities_checked": sum(cells.values()), "probability_counts": cells,
                          "mermin_target_mismatches": target_mismatches,
                          "overlap_pairs_by_size": overlap_pairs,
                          "overlap_equalities": overlap_equalities, "erasure_controls": controls}))


if __name__ == "__main__":
    main()
