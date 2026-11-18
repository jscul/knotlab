"""Shared-runner job for FIRST-KNOT-20261118-001B-E001: two first knots, small starts of several knots, and the floor control."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import startlib as S  # noqa: E402

F = S.F

SMALL = {
    'chain 3-3-3': [[0, 1, 2], [2, 3, 4], [4, 5, 6]],
    'chain 4-4-4': [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]],
    'chain 3-4-5': [[0, 1, 2], [2, 3, 4, 5], [5, 6, 7, 8, 9]],
    'chain 3-3-3-3': [[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 8]],
    'ring of three 3s': [[0, 1, 2], [2, 3, 4], [4, 5, 0]],
    'ring of four 3s': [[0, 1, 2], [2, 3, 4], [4, 5, 6], [6, 7, 0]],
    'ring of three 4s': [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 0]],
    'star of 3s': [[0, 1, 2], [0, 3, 4], [1, 5, 6], [2, 7, 8]],
    'star 4 with two 3s': [[0, 1, 2, 3], [0, 4, 5], [1, 6, 7]],
    'lone 3 and two touching 4s': [[0, 1, 2], [3, 4, 5, 6], [6, 7, 8, 9]],
    'presented 4: A and B': [[0, 1, 2], [2, 3, 4]],
    'presented 4: A and A+B': [[0, 1, 2], [0, 1, 3, 4]],
    'single 4': [[0, 1, 2, 3]],
}


def summary(P, outcome):
    return {'outcome': outcome, 'rounds': P.rounds, 'counts': P.counts_by_round(), 'offshoots': P.offshoots_by_round(),
            'junctions': len(P.bits_of), 'forced_bits': len(P.forced_bits())}


def relay(P, stars):
    """For each junction born with demand 0 and given one fresh distinction, is that distinction equal to a start-shared
    distinction on every allowed state?"""
    from collections import Counter
    cnt = Counter(x for S_ in stars for x in S_)
    shared0 = [x for x, k in cnt.items() if k == 2]
    out = []
    for j in range(len(stars), len(P.bits_of)):
        if P.demand_at_birth[j] == 0 and P.fresh[j] == 1:
            u = P.bits_of[j][-1]
            out.append(any(P._reduce(P._mask([u, h])) == 0 for h in shared0))
    return out


def cases():
    for a in range(3, 7):
        for b in range(a, 7):
            for s in (0, 1, 2):
                st = S.share(a, b, s)
                for c in range(2, 9):
                    yield f'uniform-{a}-{b}-s{s}-c{c}', {'part': 'uniform', 'stars': st, 'c': c}
                yield f'fewest-{a}-{b}-s{s}', {'part': 'fewest', 'stars': st, 'a': a, 'b': b, 's': s}
    for name, st in SMALL.items():
        yield f'small-{name}', {'part': 'small', 'stars': st}
        for c in range(2, 6):
            yield f'small-uniform-{name}-c{c}', {'part': 'uniform', 'stars': st, 'c': c}
    for m in (2, 4):
        for name, st in (('3-3 s1', S.share(3, 3, 1)), ('4-4 s1', S.share(4, 4, 1)), ('3-5 s1', S.share(3, 5, 1)),
                         ('ring of four 3s', SMALL['ring of four 3s'])):
            yield f'floor{m}-{name}', {'part': 'floor', 'stars': st, 'm': m}


def run(case_id, p):
    st = p['stars']
    if p['part'] == 'uniform':
        P, o = S.grow(st, F.uniform(p['c']), 9, max_junctions=6000)
        out = summary(P, o)
        out['stall_round'] = P.rounds + 1 if o == 'stall' else None
        out['open'] = S.open_counts(st)
        out['predicted'] = S.predicted_uniform(st, p['c'], P.rounds)
        out['in_scope'] = S.in_scope(st)
        return out
    if p['part'] in ('fewest', 'small'):
        P, o = S.grow(st, F.fewest, 30, max_junctions=6000)
        out = summary(P, o)
        out['open'] = S.open_counts(st)
        zero = [j for j in range(len(st), len(P.bits_of)) if P.demand_at_birth[j] == 0]
        out['demand0'] = len(zero)
        out['demand0_implied'] = sum(1 for j in zero if P.fresh[j] == 0)
        out['relay'] = relay(P, st)
        if p['part'] == 'fewest' and p['s'] == 1:
            la, lb = p['a'] - 1, p['b'] - 1
            out['predicted_counts'] = [2] + [S.predicted_fewest_piece(la, t) + S.predicted_fewest_piece(lb, t)
                                             for t in range(1, P.rounds + 1)]
        return out
    if p['part'] == 'floor':
        P, o = S.grow(st, S.fewest_floor(p['m']), 14, max_junctions=6000)
        return summary(P, o)
    raise ValueError(p['part'])
