"""Unit checks of this study's additions, on structures built by hand (run: python -B test_gch.py).  The earlier
study's checks are in test_lr.py and must still pass on these modules."""
import lr_core as C
import lr_laws as L
import lr_reference as RF
from lr_search import Runner
from gch_configs import CAP3W, CAP3WF, CAP3H, R3H, F1OH


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print('ok  ', msg)


def ref_of(start, fam, r):
    return RF.RefData(C.start_stars(start), fam[0], fam[1], r, release=fam[2], fillers=fam[3])


def test_cap_demand():
    # D2(4,3) start roster: member i's births are two joins and one offshoot, one met set of three per member
    ref = ref_of('D2(4,3)', CAP3W, 1)
    law = L.make_law(ref, 'R3')
    pl = law.start_plan()
    d = sorted((len(G), D, f, u) for G, D, f, u, depth in pl.detail)
    check(d == [(1, 2, 2, 2)] * 4 + [(2, 4, 3, 3)] * 4,
          'cap: an offshoot has D = 2 and f = min(max(2, 2, 1), 3) = 2; a join D = 4 and f = 3')
    check(C.fresh_ration('CAP-3', 1, 0) == 2 and C.fresh_ration('CAP-3', 3, 0) == 1 and
          C.fresh_ration('CAP-3', 2, 7) == 3, 'cap: f = min(max(D, 3 - p, 1), 3)')
    # the demand of a birth counts only the births of its own reading
    hold = {0: 2, 1: 2, 2: 2}
    fam = [frozenset((0, 1)), frozenset((1, 2))]
    pl = C.read_plan(hold, fam, 'CAP-3', 'CANCEL-WAIT')
    Ds = {G: D for G, D, f, u, depth in pl.detail}
    # births J01, J12, O0, O2; met sets of the births: {J01, O0} (parent 0), {J01, J12} (1), {J12, O2} (2)
    check(Ds == {(0, 1): 2, (1, 2): 2, (0,): 1, (2,): 1},
          'cap: D among one reading\'s births (each parent\'s births form one met set): joins 2, offshoots 1')


def test_fillers_h0():
    ref = ref_of('D2(4,3)', CAP3WF, 3)
    # round-2 offshoots of the round-1 offshoots: f = 2, D = 1, so one usable and one barred at birth
    r2 = [x for x in range(ref.N) if ref.born[x] == 2]
    check(r2 and all(ref.fresh[x] == 2 and ref.barred0[x] == 1 and ref.h0[x] == 1 and ref.loose0[x] == 2 for x in r2),
          'fillers: h0 = places less parents less places barred at birth (2 - 1 = 1); both loose')
    I = 0
    for x in range(ref.N):
        if ref.born[x] <= 2:
            I |= 1 << x
    st = L.State(ref, I, 0)
    check(all(st.use.get(x) == 1 for x in r2) and st.loose >= 2 * len(r2),
          'fillers: a barred filler is loose but not usable')
    law = L.make_law(ref, 'R3')
    B, P = law.brood_of(st, r2[0])
    pl = law.brood_plan(st, B, P)
    check(all(h == 1 for (G, f, u), h in [((G, f, u), 1) for (G, f, u) in pl.births]),
          'fillers: the brood of round-2 offshoots is read with holdings h0 = 1')


def test_stayers_and_idle():
    # a - b - c, holdings 1, 1, 2, met sets {a,b}, {b,c}: b is short and waits; a and c stay
    hold = {'a': 1, 'b': 1, 'c': 2}
    fam = [frozenset('ab'), frozenset('bc')]
    pl = C.read_plan(hold, fam, 'RATION-3', 'CANCEL-WAIT', release='HOLD')
    check(dict(pl.births) == {(('c',), 3, 3): 1}, 'HOLD: c makes holding less all its groups = 1 offshoot; a makes none')
    check(pl.stayers['a'] == [(0, 1), (1, 1)] and pl.stayers['c'] == [(0, 1), (1, 1)],
          'HOLD: a and c are stayers, each keeping one, in the first reading and again in the second')
    check(pl.waited['b'] == [0, 1] and all(pl.status[u] == 'idle' for u in 'abc'),
          'waiters and stayers roster: b waits again, nothing is planned, so the part is idle (not all-short)')
    pl2 = C.read_plan(hold, fam, 'RATION-3', 'CANCEL-WAIT', release='RELEASE')
    check(dict(pl2.births) == {(('a',), 3, 3): 1, (('b',), 3, 3): 1, (('c',), 3, 3): 2} and
          pl2.acting_level['b'] == 1 and pl2.status['b'] == 'acts',
          'RELEASE on the same roster: a and c release everything; b waits, then alone in the waiters roster acts')
    # the cap with holding on D2(4,3): the round-1 brood is idle in its first reading
    ref = ref_of('D2(4,3)', CAP3H, 1)
    I = 0
    for x in range(ref.N):
        if ref.born[x] <= 1:
            I |= 1 << x
    st = L.State(ref, I, 0)
    law = L.make_law(ref, 'R3')
    B, P = law.brood_of(st, 8)
    pl = law.brood_plan(st, B, P)
    offs = [x for x in L.bits(B) if len(ref.par[x]) == 1]
    check(not pl.births and all(pl.status[x] == 'idle' for x in L.bits(B)) and
          all(pl.stayers[o] == [(0, 2)] for o in offs),
          'cap with holding: joins wait, offshoots keep 2 and plan nothing: the part is idle at once')
    # R3H: round-1 offshoots stay (keep 2, make 1) and the part is idle in the second reading
    ref = ref_of('D2(4,3)', R3H, 2)
    st = L.State(ref, I, 0)
    law = L.make_law(ref, 'R3')
    B, P = law.brood_of(st, 8)
    pl = law.brood_plan(st, B, P)
    offs = [x for x in L.bits(B) if len(ref.par[x]) == 1]
    check(all(pl.member_births[o] == {((o,), 3, 3): 1} and pl.stayers[o] == [(0, 2), (1, 2)] for o in offs) and
          all(pl.status[x] == 'idle' for x in L.bits(B)),
          'R3H: each round-1 offshoot makes one offshoot, keeps two for its cancelled joins, and its part goes idle')


def test_has_given():
    ref = ref_of('D2(4,3)', R3H, 2)
    I = 0
    for x in range(ref.N):
        if ref.born[x] <= 2:
            I |= 1 << x
    st = L.State(ref, I, 0)
    o0 = ref.by_par[(0,)][0]
    c0 = ref.by_par[(o0,)][0]
    r3 = L.make_law(ref, 'R3')
    r3p = L.make_law(ref, "R3'")
    check((st.mem >> o0) & 1 and not st.weaned(c0), 'the staying offshoot is still a member: its child is not weaned')
    check(r3p.has_given(st, o0, {}), "has given: o0's brood parents gave, its one offshoot is made, its part is idle")
    a3 = {G for G, f, u in r3.allowed3(st)}
    a3p = {G for G, f, u in r3p.allowed3(st)}
    check((c0,) not in a3 and (c0,) in a3p, "R3 never lets the stayer's child act; R3' does")
    # before o0's child is made, o0 has not given (a planned birth is missing)
    st2 = L.State(ref, I & ~(1 << c0), 0)
    w = r3p.why_not_given(st2, o0)
    check(not r3p.has_given(st2, o0, {}) and w['why'] == 'a birth planned for it is not made',
          'has given fails while a birth planned for the stayer is not made')
    # under RELEASE, R3' is R3
    refw = ref_of('D2(4,3)', CAP3W, 1)
    I1 = 0
    for x in range(refw.N):
        if refw.born[x] <= 2:
            I1 |= 1 << x
    stw = L.State(refw, I1, 0)
    check(sorted(L.make_law(refw, 'R3').allowed3(stw)) == sorted(L.make_law(refw, "R3'").allowed3(stw)),
          "under RELEASE R3' allows what R3 allows")


def test_match_earliest_round():
    found = None
    for start in ('TWO-KNOT', 'THREE-KNOT', 'D2(4,3)'):
        for fam in (R3H, F1OH):
            ref = ref_of(start, fam, 4 if start != 'D2(4,3)' else 3)
            for k, xs in ref.by_pfb.items():
                if len({ref.born[x] for x in xs}) > 1:
                    found = (ref, k, xs)
                    break
            if found:
                break
        if found:
            break
    check(found is not None, 'some parent has children of one kind (parents, f, barred) born in two rounds')
    ref, k, xs = found
    check(xs == sorted(xs, key=lambda x: (ref.born[x], x)), 'candidates ordered by round of birth, then number')
    # a birth of that kind is matched to the earliest-born candidate not yet an image, even when a later-born one
    # has a smaller number
    I = 0
    for x in range(ref.N):
        if x not in xs and all(ref.born[p] <= ref.born[xs[0]] for p in ref.par[x]) and ref.born[x] < ref.born[xs[0]]:
            I |= 1 << x
    I |= ref.start_mask
    for p in k[0]:
        I |= 1 << p
    run = Runner(ref, L.make_law(ref, 'R3'))
    st = L.State(ref, I, 0)
    c, cl, f, u = run.birth(st, k[0], k[1], k[1] - k[2])
    check(c == xs[0] and ref.born[c] == min(ref.born[x] for x in xs), 'the match by earliest round picks %d' % c)


if __name__ == '__main__':
    test_cap_demand()
    test_fillers_h0()
    test_stayers_and_idle()
    test_has_given()
    test_match_earliest_round()
    print('all unit checks passed')
