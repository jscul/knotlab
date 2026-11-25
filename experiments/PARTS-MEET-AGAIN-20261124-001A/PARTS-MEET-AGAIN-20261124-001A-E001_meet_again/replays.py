"""Birth-by-birth replays of the cases where this engine's result differs from a number disclosed under "Known before
the freeze" (pre-registration, "Disagreements"): parents, inputs, holders of each input at the start of the round,
fresh counts.  Writes replays.json.

usage: python -B replays.py
"""
import common as C
import knots as K
import paired as P
import pm
import special as SP


def carry_case(kl, carry_filter):
    law = SP.make_law('RING-LAW', 'CARRY', kl, 'Ring(5,3)', carry_filter=carry_filter)
    A = pm.Run(pm.start('Ring(5,3)'), law)
    lst = SP.listing(A, min(3, A.rounds_done))
    big = [b for b in A.records[1]['births'] if len(b['parents']) == 10]
    S = A.snap[A.rounds_done]
    out = {'law': law.name(), 'rounds': A.rounds_done, 'stop': A.stop, 'knots': S.n_knots, 'listing': lst}
    if big:
        b = big[0]
        u = b['id']
        out['join_of_ten'] = {'id': u, 'parents': b['parents'], 'loose_given': b['loose'], 'carried': b['rule_takes'],
                              'fresh': b['fresh'], 'places': len(A.snap[2].places[u])}
        if kl == 'nae':
            out['join_of_ten']['birth_method'] = K.birth_method(A.snap[1], A.snap[2], u)
            out['join_of_ten']['direct_at_round_2'] = K.nae_direct(A.snap[2], [u])[u] if \
                len(A.snap[2].places[u]) <= 22 else 'too many places for the direct test'
        else:
            out['join_of_ten']['parity_pass_round_2'] = K.parity_test(A.snap[2])['pass'][u]
    return out


def hold_q_case(st):
    law = SP.make_law('COPY-LAW(OFFSHOOT)', 'Q(NEWEST)', 'nae', st, release='HOLD')
    A = pm.Run(pm.start(st), law)
    v = P.RunView(A)
    ap = P.all_pairs_checks(v)
    return {'law': law.name(), 'start': st, 'came_apart': ap['came_apart_list'][:6],
            'listing': SP.listing(A, min(4, A.rounds_done)),
            'rosters': [{'t': t, 'parts': [list(p) for p in v.roster(t).parts]} for t in range(min(5, v.R + 1))]}


def a225_wait_case(X, Y):
    law = SP.make_law('COPY-LAW(WAIT)', 'none', 'nae', 'three-knot')
    A = pm.Run(pm.start('three-knot'), law)
    v = P.RunView(A)
    T, placed = SP.place_knot(A.snap[2], X, Y)
    A2 = P.run_from(v, 2, T)
    B2 = P.run_from(P.RunView(A2), 2, P.bar_part(T, Y))
    d = P.first_difference(P.trace(A2, X, 2), P.trace(B2, X, 2))
    return {'X': X, 'Y': Y, 'placed': placed, 'course_differs': d[0], 'way': d[1], 'demand_line': d[2],
            'with Y': SP.listing(A2, 5)[2:], 'Y barred': SP.listing(B2, 5)[2:]}


def main():
    out = {'carry': {}, 'hold_q_newest': {}, 'a225_wait': {}}
    out['a225_wait']['the two copies (used)'] = a225_wait_case([6, 7], [8, 9])
    out['a225_wait']['the first two parts (X the waiting join)'] = a225_wait_case([3], [6, 7])
    for kl in ('nae', 'parity'):
        for cf in (False, True):
            out['carry']['%s, %s' % (kl, 'oldest not already taken (alternative)' if cf else
                                     'skip a repeat (reading 10, used in the runs)')] = carry_case(kl, cf)
    for st in ('two-knot', 'Ring(5,3)'):
        out['hold_q_newest'][st] = hold_q_case(st)
    C.write_json('replays.json', out)
    for k, v in out['carry'].items():
        print('CARRY', k, v.get('join_of_ten', {}).get('places'), {kk: vv for kk, vv in v.get('join_of_ten', {}).items()
                                                                   if kk in ('birth_method', 'direct_at_round_2',
                                                                             'parity_pass_round_2')})
    for k, v in out['a225_wait'].items():
        print('A225 WAIT', k, v['course_differs'], v['way'], v['demand_line'])
    for k, v in out['hold_q_newest'].items():
        print('HOLD Q(NEWEST)', k, v['came_apart'][:3])


if __name__ == '__main__':
    main()
