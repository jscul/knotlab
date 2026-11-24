"""Unit checks of the pieces on structures built by hand (run: python -B test_lr.py)."""
import lr_core as C
import lr_laws as L
import lr_reference as RF
from lr_search import Runner


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print('ok  ', msg)


def test_groups():
    # 4-cycle of met sets: four pairs
    fam = [frozenset(p) for p in ((0, 1), (1, 2), (2, 3), (3, 0))]
    check(C.compute_groups(range(4), fam) == [(0, 1), (0, 3), (1, 2), (2, 3)], 'groups of a 4-cycle are its pairs')
    # one met set of three: three pairs, no big group (contained in a single met set)
    check(C.compute_groups(range(3), [frozenset((0, 1, 2))]) == [(0, 1), (0, 2), (1, 2)],
          'a triangle inside one met set gives three pairs')
    # three pairwise met sets: one group of three
    fam = [frozenset(p) for p in ((0, 1), (1, 2), (0, 2))]
    check(C.compute_groups(range(3), fam) == [(0, 1, 2)], 'a triangle of three met sets is one group of three')
    # the start-clause counterexample, round 2: K4 of four members over three met sets of three
    fam = [frozenset(s) for s in ((0, 1, 2), (0, 1, 3), (0, 2, 3))]
    check(C.compute_groups(range(4), fam) == [(0, 1, 2, 3)], 'K4 not in one met set is one group of four')


def test_plans():
    # start-clause counterexample start roster: knot 0 short (3 groups, 2 holdings) waits, then reads alone
    hold = {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}
    fam = [frozenset(s) for s in ((1, 2, 3), (0, 4), (0, 5), (0, 6))]
    pl = C.read_plan(hold, fam, 'RATION-3', 'CANCEL-WAIT')
    check(pl.offs.get(0) == [2, 3] and pl.acting_level[0] == 1,
          'waiters recursion: knot 0 waits, then reads a roster of itself alone: two offshoots')
    check(set(pl.joins) == {(1, 2), (1, 3), (2, 3)} and all(pl.offs[u] == [2, 3] for u in (4, 5, 6)),
          'start-clause counterexample: three joins and two offshoots of each of knots 4-6')
    # the control: no recursion, the waiter is given nothing
    pl0 = C.read_plan(hold, fam, 'RATION-3', 'CANCEL-WAIT', recursion=False)
    check(0 not in pl0.offs and pl0.status[0] == 'waits', 'without the recursion the waiter makes nothing')
    # all-short: a 4-cycle with holdings 1
    pl = C.read_plan({u: 1 for u in range(4)}, [frozenset(p) for p in ((0, 1), (1, 2), (2, 3), (3, 0))],
                     'RATION-3', 'CANCEL-WAIT')
    check(all(pl.status[u] == 'allshort' for u in range(4)) and not pl.joins and not pl.offs,
          'a part all of whose members are short is all-short and makes nothing')
    # ORD on the lone four-place knot: four offshoots, each D = 3
    pl = C.read_plan({0: 4}, [], 'ORD', 'STALL')
    check(pl.offs[0] == [4, 3], 'ORD: four offshoots of the lone knot, each with D = 3, f = 3')
    # STALL
    pl = C.read_plan({u: 1 for u in range(4)}, [frozenset(p) for p in ((0, 1), (1, 2), (2, 3), (3, 0))],
                     'ORD', 'STALL')
    check(pl.stalled and not pl.joins, 'STALL: a short member stalls the plan')
    # RETIRE and OFFSHOOT
    pl = C.read_plan({0: 1, 1: 2, 2: 2}, [frozenset((0, 1)), frozenset((0, 2))], 'FLOOR1', 'CANCEL-RETIRE')
    check(pl.status[0] == 'retires' and pl.offs[1] == [2, 2] and not pl.joins,
          'CANCEL-RETIRE: the short member retires, its groups are cancelled, the others release')
    pl = C.read_plan({0: 1, 1: 2, 2: 2}, [frozenset((0, 1)), frozenset((0, 2))], 'FLOOR1', 'CANCEL-OFFSHOOT')
    check(pl.offs[0] == [1, 2], 'CANCEL-OFFSHOOT: the short member makes an offshoot from each holding')


def test_d2_after_round1():
    ref = RF.RefData(C.start_stars('D2(4,3)'), 'RATION-3', 'CANCEL-WAIT', 1)
    I = ref.start_mask | sum(1 << x for x in range(8, 16))       # the start and its eight round-1 births
    st = L.State(ref, I, 0)
    check([ref.h0[u] for u in range(8)] == [3, 3, 3, 3, 0, 0, 0, 0], 'h0 of start knots: 3 for members, 0 dead')
    check(all(ref.h0[x] == 3 for x in range(8, 16)), 'h0 of round-1 knots: places less parents = 3')
    check(st.mem == sum(1 << x for x in range(8, 16)), 'members after round 1: the eight new knots')
    check(all(st.weaned(x) for x in range(8, 16)), 'every round-1 knot is weaned (the start members are dead)')
    law = L.BroodLaw(ref, 'R3')
    B, P = law.brood_of(st, 8)
    check(B == sum(1 << x for x in range(8, 16)) and P == 0b1111, 'the brood of a round-1 join is all eight')
    pl = law.brood_plan(st, B, P)
    joins = [x for x in range(8, 16) if len(ref.par[x]) == 2]
    offs = [x for x in range(8, 16) if len(ref.par[x]) == 1]
    check(all(pl.acting_level[j] == 1 for j in joins) and all(pl.acting_level[o] == 0 for o in offs),
          'joins wait once, offshoots act in the first roster')
    check(len(pl.joins) == 4 and all(pl.offs[j] == [1, 3] for j in joins) and all(pl.offs[o] == [3, 3] for o in offs),
          'plan: four joins of joins, one offshoot per join, three per offshoot')
    o = offs[0]
    c = ref.by_par[(o,)][0]
    st2 = L.State(ref, I | (1 << c), 0)
    rem = dict(law.remaining(pl, st2))
    check(rem[(o,)] == 3 and len(ref.by_par[(o,)]) == 3, 'made births are subtracted by parent set')
    cnt = sum(1 for G, f in law.remaining(pl, st2) if G == (o,))
    # remaining() lists a member's offshoots once while any remain; the number left is planned less made
    made = (ref.by_par_mask[(o,)] & st2.I).bit_count()
    check(pl.offs[o][0] - made == 2 and cnt == 1, 'two offshoots of that knot remain after one is made')
    check(not st2.weaned(c), 'the new offshoot is not weaned while its parent still holds a usable distinction')
    # R1 guard: a join of the joins is allowed (its parents are weaned); R3 too (brood all-weaned)
    A1 = dict(L.BroodLaw(ref, 'R1').allowed(st2))
    A3 = dict(law.allowed(st2))
    check(set(A1) == set(A3), 'after one offshoot of an offshoot, R1 and R3 allow the same births')


def test_c8x3_recursion():
    ref = RF.RefData(C.start_stars('C8X3'), 'RATION-3', 'CANCEL-WAIT', 1)
    I = ref.start_mask | sum(1 << x for x in range(19, 32))
    st = L.State(ref, I, 0)
    law = L.BroodLaw(ref, 'R3')
    B, P = law.brood_of(st, 19)
    pl = law.brood_plan(st, B, P)
    lv = {x: pl.acting_level.get(x) for x in range(19, 32)}
    j15 = ref.by_par[(1, 5)][0]
    check(lv[j15] == 3 and pl.offs[j15] == [3, 3], 'the join of members 1 and 5 waits three times, then 3 offshoots')
    check(sum(1 for x in lv if lv[x] == 2) == 6 and sum(1 for x in lv if lv[x] == 1) == 4,
          'of the 11 joins, 4 act after one wait and 6 after two')


def test_closing():
    ref = RF.RefData(C.start_stars('LONE-FOUR'), 'ORD', 'STALL', 4)
    run = Runner(ref, L.make_law(ref, 'R3'))
    o = run.run_order(lambda A: A[0])
    check(o['outcome'] == 'match' and len(o['closing']) == 1 and o['closing'][0]['matched_received_none'],
          'lone four-place knot under (ORD, STALL): the closing bit fires once, at the reference closing birth')


if __name__ == '__main__':
    test_groups()
    test_plans()
    test_d2_after_round1()
    test_c8x3_recursion()
    test_closing()
    print('all unit checks passed')
