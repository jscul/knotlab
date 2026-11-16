"""Which root questions leave room to establish two live uses of a cheap sector?"""
from collections import Counter
from functools import cache
import json

import solver


ROWS = solver.old.evaluator_sets((1, 6), 1)
R, P = ROWS['left'], ROWS['right']
HALVES = [solver.old.equation_points(q, 1) for q in range(512)]
UNREACHABLE = 99


@cache
def fixed(cell):
    while cell:
        after = solver.old.hull(cell & R) & solver.old.hull(cell & P)
        if after == cell:
            break
        cell = after
    return cell


@cache
def cheap_close(cell):
    """Exact through two charges, with all larger costs rounded down to three."""
    rich, plain = cell & R, cell & P
    if not rich or not plain:
        return 1
    if not (solver.old.hull(rich) & plain) or not (solver.old.hull(plain) & rich):
        return 2
    return 3


def prefix(premise, conclusion):
    guard = solver.old.equation_points(*premise)
    literal = solver.old.equation_points(*conclusion)

    def live(cell):
        return bool(fixed(cell) & ~literal and fixed(cell & literal))

    @cache
    def overhead(cell, budget):
        if not (cell & ~guard):
            return 0 if live(cell) else UNREACHABLE
        f = fixed(cell)
        if budget == 0 or not (f & guard & literal and f & guard & ~literal):
            return UNREACHABLE
        best = UNREACHABLE
        for rows in (R, P):
            after = solver.old.hull(cell & rows)
            if after != cell:
                best = min(best, 1 + overhead(after, budget-1))
        if budget >= 2 and live(cell & guard):
            best = min(best, 1 + cheap_close(cell & ~guard))
        if budget == 3:
            # For any other query the continuing affine half is still outside the guard.
            # Its remaining expense is >=1, so its sibling must close for exactly one check.
            for mask in HALVES[1:]:
                a = cell & mask
                b = cell ^ a
                if not a or not b:
                    continue
                for keep, drop in ((a,b),(b,a)):
                    if keep & ~guard and (not (drop & R) or not (drop & P)):
                        best = min(best, 2 + overhead(keep, 1))
        return best if best <= budget else UNREACHABLE

    distribution = Counter()
    feasible = []
    for query in range(1, 512):
        if query == premise[0]:
            # One whole answer lies outside the premise, so it can have no live citation.
            continue
        pos = HALVES[query]
        low = overhead(solver.ALL ^ pos, 3)
        high = overhead(pos, 3)
        key = tuple(sorted((min(4, low), min(4, high))))
        distribution[key] += 1
        if low + high <= 4:
            feasible.append(query)
    assert sum(distribution.values()) == 510 and not feasible
    return {'first_questions_checked': 511, 'premise_question_excluded': 1,
            'paired_overhead_histogram_four_means_above_three':
                {f'{a},{b}': n for (a,b),n in sorted(distribution.items())},
            'root_questions_surviving_22_units': feasible}


def audit():
    outputs = {}
    forbidden = ((2,0,132,0), (2,0,148,0), (6,0,128,1), (22,0,128,1))
    for a, c, b, d in forbidden:
        for g, s, l, t in ((a,c,b,1^d), (b,d,a,1^c), (a^b,c^d,a,1^c)):
            label = f'{g}={s} implies {l}={t}'
            outputs[label] = prefix((g,s), (l,t))
    assert len(outputs) == 12
    return outputs


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
