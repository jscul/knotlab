"""Check the local exchange, full-order signs and two readings on a small ordinary history."""

import argparse
import json
import sys
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fold


# The two five-place knots share distinction 12. Each meets two three-place
# knots, each of which has one loose distinction to give.
START = ((0, 1, 2), (3, 4, 5), (0, 1, 3, 4, 12),
         (6, 7, 8), (9, 10, 11), (6, 7, 9, 10, 12))


def order_signs(prerequisites):
    counts = {1: 0, -1: 0}
    for order in permutations(sorted(prerequisites)):
        position = {b: i for i, b in enumerate(order)}
        if any(position[p] > position[b] for b, ps in prerequisites.items() for p in ps):
            continue
        inversions = sum(a > b for i, a in enumerate(order) for b in order[i + 1:])
        counts[(-1) ** inversions] += 1
    return counts


def verify_exchange(stage):
    # Simultaneously exchange the two copies, fixing their shared distinction.
    # Derive the distinction permutation from the holder lists, keeping
    # parallel shared distinctions and loose distinctions as distinct names.
    knot_swap = [3, 4, 5, 0, 1, 2, 7, 6, 9, 8][:len(stage)]
    holders = {}
    for k, places in enumerate(stage):
        for d in places:
            holders.setdefault(d, []).append(k)
    by_holders = {}
    for d, ks in holders.items():
        by_holders.setdefault(tuple(ks), []).append(d)
    rename = {}
    for ks, names in by_holders.items():
        image = tuple(sorted(knot_swap[k] for k in ks))
        rename.update(zip(sorted(names), sorted(by_holders[image]), strict=True))
    for k, places in enumerate(stage):
        assert {rename[d] for d in places} == set(stage[knot_swap[k]])
    return knot_swap


def main(rounds):
    previous = START
    result = []
    for r, stage, barred, (start, parent) in fold.grow(START, 'nae', rounds):
        assert not barred
        parents = {k: {p for c, p in parent if c == k} for k in range(len(start), len(stage))}
        prec = {k: ps - start for k, ps in parents.items()}
        swap = verify_exchange(stage)
        assert {(swap[c], swap[p]) for c, p in parent} == parent
        assert len(start) == 6 and len(stage) == 6 + 2 * r
        counts = order_signs(prec)
        row = dict(round=r, parents={k: sorted(ps) for k, ps in parents.items()},
                   even=counts[1], odd=counts[-1])
        if r == 1:
            assert counts == {1: 1, -1: 1}
        else:
            assert prec == {6: set(), 7: set(), 8: {6}, 9: {7}}
            assert counts == {1: 2, -1: 4}
            [(_, rebuilt, _, (later_start, later_parents))] = fold.grow(previous, 'nae', 1)
            assert rebuilt == stage and len(later_start) == 8
            row['alternative_start_size'] = len(later_start)
            later_births = set(range(len(rebuilt))) - later_start
            later_prec = {b: {p for c, p in later_parents if c == b} - later_start for b in later_births}
            later_counts = order_signs(later_prec)
            assert later_counts == {1: 1, -1: 1}
            row['alternative_start_even_odd'] = [later_counts[1], later_counts[-1]]

            # Swapping the two fresh distinctions of the same last birth fixes
            # the complete start and all knots, and is odd on all distinctions.
            loose = [d for d in stage[8] if all(d not in places for k, places
                                                in enumerate(stage) if k != 8)]
            assert len(loose) == 2
            exchange = dict(zip(loose, reversed(loose)))
            assert all({exchange.get(d, d) for d in places} == set(places) for places in stage)
            assert not set(loose).intersection(d for places in START for d in places)
            row['loose_distinction_transposition'] = loose

            def sign_before(ideal):
                nonmaximal = {p for k in ideal for p in prec[k]}
                return (-1) ** len(ideal - nonmaximal)

            ideal = {6}
            extend_first = sign_before(ideal) * sign_before(ideal | {8})
            start_other = sign_before(ideal) * sign_before(ideal | {7})
            assert extend_first * start_other == -1
            row['maximal_count_exchange'] = [extend_first, start_other]
        result.append(row)
        previous = stage
    assert len(result) == rounds
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, choices=(1, 2), required=True)
    main(parser.parse_args().rounds)
