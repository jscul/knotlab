"""Unit tests on structures built by hand.  usage: python -B test_engine.py  (writes test_engine.json)"""
import sys

import common as C
import knots as K
import paired as P
import pm

RES = {}


def check(name, cond, detail=None):
    RES[name] = {'ok': bool(cond), 'detail': detail}
    print('%-70s %s' % (name, 'ok' if cond else 'FAIL'), '' if cond else detail)


def law(**kw):
    return pm.Law(**kw)


def t_meeting_three_holders():
    # distinction 0 held by knots 0, 1, 2; each holds two loose ones; knot 3 dead meeting 1 and 2 through 5, 6
    S = pm.from_stars([[0, 1, 2], [0, 3, 4, 5], [0, 6, 7, 8], [5, 8]])
    R = pm.roster_of(S, law())
    check('three holders: members', R.members == (0, 1, 2), R.members)
    # met sets: knot 0 meets 1, 2 -> {1,2}; knot 1 meets 0, 2, 3 -> {0,2}; knot 2 -> {0,1}; knot 3 -> {1,2}
    ms = sorted(sorted(M) for M in R.maxsets)
    check('three holders: a knot is not in its own met set', ms == [[0, 1], [0, 2], [1, 2]], ms)
    check('three holders: one part', R.parts == [(0, 1, 2)], R.parts)
    # groups: the triangle {0,1,2} is in no single met set -> one group of three
    check('three holders: one group of three', R.groups == [(0, 1, 2)], R.groups)


def t_classes():
    # two parts that share nothing, and two parts that share a distinction (two members holding a common one, not
    # joinable because no met set contains both)
    S = pm.from_stars([[0, 1, 2], [0, 3, 4], [5, 6, 7], [5, 8, 9], [10, 11, 12]])
    # knots 0 and 1 meet directly (distinction 0) and are not joinable (no common knot): two parts, one class
    R = pm.roster_of(S, law())
    cls = pm.roster_classes(R)
    check('classes: parts', R.parts == [(0,), (1,), (2,), (3,), (4,)], R.parts)
    check('classes: 0~1 and 2~3 linked, 4 alone', cls[0] == cls[1] and cls[2] == cls[3] and len(set(cls)) == 3, cls)


def t_trace_renaming():
    # the smallest case: X's trace in A and in B(i) agree through round 3 (other new knots and distinctions renamed)
    L = law(ration='FLOOR1', treatment='CANCEL-RETIRE', take='STEPS-2', choice='OLDEST')
    A = pm.Run(pm.start('three-knot'), L)
    v = P.RunView(A)
    B1 = P.run_from(v, 2, P.bar_part(A.snap[2], [8, 9]))
    ta, tb = P.trace(A, [6, 7], 2), P.trace(B1, [6, 7], 2)
    check('trace: equal at round 3 although names differ', P.course_key(ta[0]) == P.course_key(tb[0]),
          (ta[0]['births'], tb[0]['births']))
    check('trace: differs at round 4', P.course_key(ta[1]) != P.course_key(tb[1]))
    names_a = [b[0] for b in ta[0]['births']]
    check('trace: X births renamed in order', names_a == [('n', 0), ('n', 1), ('n', 2)], names_a)


def t_b2_defined():
    L = law(ration='FLOOR1', treatment='CANCEL-RETIRE', take='STEPS-2', choice='OLDEST')
    A = pm.Run(pm.start('three-knot'), L)
    T = P.remove_part(A.snap[2], [8, 9], 2)
    check('B(ii): defined for the smallest case', T is not None)
    if T is not None:
        check('B(ii): taken distinctions return loose and barred', all(len(T.holders[d]) == 1 and T.barred[d]
                                                                      for d in (11, 12)),
              [(d, T.holders[d], T.barred[d]) for d in (11, 12)])
        T.check()
    # not defined: Y = {12,...} after round 3, 12 holds distinction 0 with four holders
    T2 = P.remove_part(A.snap[3], [14, 15], 3)
    check('B(ii): not defined when a taken distinction has more than one other holder', T2 is None)


def t_mask():
    L = law(ration='FLOOR1', treatment='CANCEL-RETIRE', take='STEPS-2', choice='OLDEST')
    A = pm.Run(pm.start('three-knot'), L)
    v = P.RunView(A)
    M = P.masked_run(v, 2, [6, 7], [8, 9], 'XY')
    g4 = M.records[3]['groups']
    check('mask: no group across X and Y at round 4', g4 == [[10, 12, 13], [11, 14, 15]], g4)
    M2 = P.masked_run(v, 2, [6, 7], [8, 9], 'ISO')
    check('isolating mask: the same here', M2.records[3]['groups'] == [[10, 12, 13], [11, 14, 15]])


def t_branch_cache():
    # a branch must not reuse levels computed in another branch for knots that differ between them
    L = law(ration='FLOOR1', treatment='CANCEL-RETIRE', take='STEPS-2', choice='OLDEST')
    A = pm.Run(pm.start('three-knot'), L)
    v = P.RunView(A)
    M = P.masked_run(v, 2, [6, 7], [8, 9], 'XY')
    B1 = P.run_from(v, 2, P.bar_part(A.snap[2], [8, 9]))
    check('levels: masked run equals B(i) on X (no stale cache)',
          P.first_difference(P.trace(M, [6, 7], 2), P.trace(B1, [6, 7], 2))[0] is None)


def t_knot_tests():
    S = pm.from_stars([['a', 'b', 'l1', 'l2', 'l3'], ['a', 'b', 'e', 'f', 'g'], ['e', 'f', 'g']])
    pt = K.parity_test(S)
    bp, _ = K.brute(S, 'parity')
    check('parity: planted failing knot, both methods and brute agree',
          not pt['disagree'] and all(pt['pass'][u] == bp[u] for u in bp) and not bp[0], (pt, bp))
    T = pm.from_stars([[0, 1, 4], [0, 1, 2, 3], [2, 3, 4]])
    d = K.nae_direct(T, T.knots())
    bn, _ = K.brute(T, 'nae')
    check('nae: direct equals brute on a small case', d == bn, (d, bn))
    # birth method: a birth taking two places of a three-place knot fails
    S0 = pm.from_stars([[0, 1, 2]])
    S1 = S0.copy()
    S1.places.append([0, 1, 3])
    S1.parents.append(())
    S1.made.append(1)
    S1.kind.append('drawn')
    S1.holders[0].append(1)
    S1.holders[1].append(1)
    S1.holders.append([1])
    S1.barred.append(False)
    S1.round = 1
    b = K.birth_method(S0, S1, 1)
    dd = K.nae_direct(S1, [1])[1]
    check('birth method: two places of a 3-place knot are jointly free', b is True and dd is True, (b, dd))
    S2 = S0.copy()
    S2.places.append([0, 1, 2, 3])
    S2.parents.append(())
    S2.made.append(1)
    S2.kind.append('drawn')
    for x in (0, 1, 2):
        S2.holders[x].append(1)
    S2.holders.append([1])
    S2.barred.append(False)
    b2 = K.birth_method(S0, S2, 1)
    d2 = K.nae_direct(S2, [1])[1]
    check('birth method: all three places of a knot are not jointly free', b2 is False and d2 is False, (b2, d2))


def t_closing():
    # two knots joined: a birth taking every loose distinction of a connected two-holder structure is implied
    S = pm.from_stars([[0, 1, 2], [0, 3, 4]])
    v = 0
    for d in (1, 2, 3, 4):
        v |= 1 << d
    check('IMPLIED: every loose distinction of a connected structure is implied', pm.span_contains(S.span, v))
    check('IMPLIED: a part of them is not', not pm.span_contains(S.span, (1 << 1) | (1 << 3)))


def t_short_takes():
    # Ring(5,3) under SHORT-TAKES with the earlier laws' ration: nobody is short in round 1
    L = law(ration='FLOOR1', treatment='SHORT-TAKES', choice='OLDEST')
    r = pm.Run(pm.start('three-knot'), L, rounds=2)
    rec = r.records[1]
    j = [b for b in rec['births'] if b['kind'] == 'join']
    check('SHORT-TAKES: the round-1 join is short in round 2 and takes a shared distinction',
          rec['short'] == [3] and any(b['given_shared'] for b in j), rec)


def t_names_reversed():
    S = pm.start('three-knot', reverse_names=True)
    check('names reversed: knot 0 holds 4..7', sorted(S.places[0]) == [4, 5, 6, 7], S.places)
    check('names reversed: knot 2 holds 0, 1, 4, 5', sorted(S.places[2]) == [0, 1, 4, 5], S.places)


def t_order_reversed():
    L = law(ration='FLOOR1', treatment='CANCEL-RETIRE', order_reversed=True)
    r = pm.Run(pm.start('three-knot'), L, rounds=1)
    b = r.records[0]['births']
    check('order reversed: offshoots named first, the join last', [x['kind'] for x in b] == ['offshoot', 'offshoot',
                                                                                          'join'], b)
    # knot 2's offshoot comes first and takes 2's smallest usable distinction (6); the join takes 7 and 5
    check('order reversed: hand-out reversed', b[0]['inputs'] == [6] and sorted(b[2]['inputs']) == [5, 7], b)


def main():
    for f in (t_meeting_three_holders, t_classes, t_trace_renaming, t_b2_defined, t_mask, t_branch_cache,
              t_knot_tests, t_closing, t_short_takes, t_names_reversed, t_order_reversed):
        f()
    RES['_all_ok'] = all(v['ok'] for k, v in RES.items() if not k.startswith('_'))
    C.write_json('test_engine.json', RES)
    print('ALL OK' if RES['_all_ok'] else 'SOME FAIL')
    return 0 if RES['_all_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
