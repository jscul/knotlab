"""Unit tests of the new readings, on structures and starts built by hand.  usage: python -B test_mc.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P
RES = {}


def check(name, cond, detail=None):
    RES[name] = {'ok': bool(cond), 'detail': None if cond else repr(detail)[:500]}
    print('%-78s %s' % (name, 'ok' if cond else 'FAIL'), '' if cond else repr(detail)[:300])


def t_ties():
    # the record's value at three loose places: {v,p,q},{p,q,c1},{p,q,c2}: parity ties v, c1, c2
    S = pm.from_stars([[0, 1, 2], [1, 2, 3], [1, 2, 4]])
    T = mc.ties_parity(S)
    check('ties: parity, one value at three loose places', T.tied(0, 3) and T.tied(0, 4), T.classes)
    br = mc.ties_brute(S, 'parity')
    check('ties: parity equals brute force', {frozenset(c) for c in T.classes} == br['classes'], (T.classes, br))
    Tn = mc.ties_nae(S)
    check('ties: the same knots tie nothing under not-all-equal', not Tn.classes, Tn.classes)
    # Fano piece: ties 2, 4, 5 under not-all-equal (signs checked against brute force)
    F = pm.from_stars([[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 3, 5], [1, 4, 6], [2, 3, 6]])
    Tf = mc.ties_nae(F)
    brf = mc.ties_brute(F, 'nae')
    check('ties: Fano piece under not-all-equal equals brute force',
          {frozenset(c) for c in Tf.classes} == brf['classes'] and [2, 4, 5] in Tf.classes, (Tf.classes, brf))
    # a frozen distinction under parity: two knots on the same three places force nothing; {0,1},{0,1,2} freezes 2
    G = pm.from_stars([[0, 1, 2], [0, 1, 2, 3]])
    Tg = mc.ties_parity(G)
    check('ties: parity frozen distinction', 3 in Tg.frozen, (Tg.frozen, Tg.classes))


def t_descent():
    d = mc.design('ystart-three-222')
    law = mc.make_law('COPY-LAW(OFFSHOOT)', 'MET', 'NEWEST', 'parity')
    A = mc.grow(d, law)
    S = A.snap[6]
    desc = mc.descent_map(S, d.X, d.Y, 0)
    check('descent: start knots other than X and Y are from neither', desc[0] == 'neither' and desc[3] == 'neither')
    check('descent: X and Y members', desc[1] == 'X only' and desc[4] == 'Y only')
    # every knot made after s with a parent in X and its descendants is descended from X (or both)
    xd = P.side_of(S, d.X, 0)
    ok = all((desc[u] in ('X only', 'both')) == (u in xd) for u in range(S.n_knots) if S.made[u] > 0)
    check('descent: X and its descendants', ok)
    # the P6 case: 52 and 53, makers descended from X only, tied to 16
    T = mc.ties_parity(S)
    check('descent: P6 makers of 52, 53 from X only, tied to 16',
          desc[S.holders[52][0]] == 'X only' and desc[S.holders[53][0]] == 'X only' and T.tied(52, 16)
          and T.tied(53, 16))


def t_renamings():
    for name in ('made-3', 'ystart-three-222'):
        d0 = mc.design(name)
        S0 = d0.start()
        for rn in mc.renamings_for(name):
            S1 = mc.design(name, renaming=rn).start()
            same_struct = [sorted(len(S0.holders[d]) for d in P_) for P_ in S0.places] == \
                [sorted(len(S1.holders[d]) for d in P_) for P_ in S1.places]
            check('renaming %s of %s keeps knots, places and holders' % (rn, name), same_struct)
        S_n1 = mc.design(name, renaming='n1').start()
        labs = sorted({l for k in d0.stars for l in k})
        check('renaming n1 of %s: names reversed' % name, S_n1.labels == list(reversed(labs)), S_n1.labels)
    S = mc.design('ystart-three-222', renaming='n2').start()
    check('renaming n2: e named first', S.labels[0] == -1, S.labels[:3])
    S = mc.design('made-3', renaming='n3').start()
    # n3 on made-h puts X's labels (1, 2) after Y's (3, 4, 5): knot 0 holds names 0, 4, 5
    check('renaming n3 on made-3: X\'s labels after Y\'s', sorted(S.places[0]) == [0, 4, 5], S.places)
    S = mc.design('made-3', renaming='n4').start()
    m = mc.STARTS['renamings']['made-3']['n4']
    want = sorted(sorted(m[str(l)] for l in k) for k in mc.STARTS['designs']['made-3']['stars'])
    got = sorted(sorted(S.labels[x] for x in k) for k in S.places)
    check('renaming n4 on made-3 as listed', got == want, (got, want))


def t_same_and_built():
    law = mc.make_law('COPY-LAW(RETIRE)', None, 'OLDEST', 'parity')
    A = pm.Run(pm.from_stars([[0, 1, 2], [0, 3, 4]]), law, rounds=3)
    v = P.RunView(A)
    ref = mc.Reference(A.snap[1], v.roster(1), [4, 5], 1)
    R3 = v.roster(3)
    S3 = A.snap[3]
    n_same = sum(1 for p in R3.parts if mc.same_as(ref, R3, p))
    check('form: two-knot start, retiring, round 3: four parts the same as Y', n_same == 4, n_same)
    made = [u for u in range(S3.n_knots) if S3.made[u] > 1]
    r = mc.find_renamings(ref.built, S3, made, mode='count')
    check('built: counting mode finds four renamings of Y\'s knots', r['n'] == 4, r)
    r2 = mc.find_renamings(ref.built, S3, made, mode='two')
    check('built: two renamings with no common knot are found', r2['disjoint_pair'] is not None, r2)
    br = mc.renamings_brute(ref.built, S3, made)
    check('built: search equals every injective map', {frozenset(x) for x in r['sets']} == br, (r['sets'], br))


def t_paired():
    d = mc.design('made-3')
    law = mc.make_law('CAP-3(OFFSHOOT)', 'MET', 'OLDEST', 'parity')
    A = mc.grow(d, law)
    S1 = A.snap[1]
    B = P.bar_part(S1, d.Y)
    check('B(i): every usable loose distinction of Y\'s members barred',
          all(not B.usable(u) for u in d.Y) and all(B.usable(u) == S1.usable(u) for u in d.X))
    BX = P.bar_part(S1, d.X)
    check('B_X: every usable loose distinction of X\'s members barred', all(not BX.usable(u) for u in d.X))
    v = P.RunView(A)
    M = P.masked_run(v, 1, d.X, d.Y, 'XY')
    ok = True
    for rec in M.records[1:]:
        xd = P.side_of(M.snap[rec['round']], d.X, 1)
        yd = P.side_of(M.snap[rec['round']], d.Y, 1)
        for g in rec['groups']:
            if any(u in xd for u in g) and any(u in yd for u in g):
                ok = False
    check('M: no group holds a member of each side', ok)
    a = mc.alone('made-3', 'X alone').start()
    check('X alone: the shared distinction 0 barred', a.barred[0] and a.usable(0) == [1, 2], a.usable(0))


def main():
    for f in (t_ties, t_descent, t_renamings, t_same_and_built, t_paired):
        f()
    RES['_all_ok'] = all(v['ok'] for k, v in RES.items() if not k.startswith('_'))
    C.write_json('test_mc.json', RES)
    print('ALL OK' if RES['_all_ok'] else 'SOME FAIL')


if __name__ == '__main__':
    main()
