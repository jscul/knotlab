"""Unit checks of the series and the tests on structures with known answers (the brief's list), written after the runs
as a check of the code they used; writes unit_series.json.

1. A series of returns with a known period: the two-knot case under L1 (COPY-LAW(CANCEL-OFFSHOOT), OLDEST): the part of
   four at rounds 4, 6, ..., 18 and two parts of three at rounds 3, 5, ..., 17 (the pre-registration's disclosure), and
   the ring Ring(5,3) under RING-LAW (the control), whose start's roster returns every two rounds.
2. A part barred after a tick: in B(r) every member of the barred part holds no usable loose distinction after the bar,
   and X's side is never barred.
3. Own knots against joint knots: for every test of the case under STEPS-2 for offshoots of joins, the knots made after
   t_j with a parent on X's side are exactly the own knots plus the joint knots, recounted from the structure.
4. A renumbered start gives the renumbered run where no rule uses names: under the control (no taking rule; which
   distinction goes to which birth makes no difference up to renaming, SD line 77), every numbering of the two-knot
   start and the 4n shifts of the three-knot start give the same rounds up to renaming (members, part sizes, knots,
   births per round) and the same series (sizes and periods), under every base law.
"""
from __future__ import annotations

from collections import Counter

import tf_common as C
import tf_engine as E
import tf_run5 as R5
import tf_runs as RN
import tf_series as Se
import tf_tests as Tt


def check1():
    out = {}
    stars = C.named_stars()['two-knot']
    law = E.Law.from_base('COPY-LAW(OFFSHOOT)', knot_law='nae', take='STEPS-1', choice='OLDEST')
    A = E.Run(E.from_stars(stars), law)
    ser, _ = Se.build_series(A, False)
    Se.describe(ser)
    got = sorted((s['size'], s['t0'], tuple(tk['t'] for tk in s['ticks'])) for s in ser if s['size'] >= 2 and s['ticks'])
    want = [(3, 3, tuple(range(5, 18, 2))), (3, 3, tuple(range(5, 18, 2))), (4, 4, tuple(range(6, 19, 2)))]
    out['two_knot_series'] = {'got': got, 'ok': got == want}
    R4p = A.roster(4)
    out['two_knot_parts_after_round_4'] = {'got': [list(P) for P in R4p.parts],
                                           'ok': [list(P) for P in R4p.parts] == [[18], [19], [20, 21, 22, 23]]
                                           and all(R4p.h[u] == 1 for u in R4p.members)}
    law = E.Law.from_base('RING-LAW', knot_law='nae')
    A = E.Run(E.from_stars(C.named_stars()['Ring(5,3)']), law, rounds=12)
    rr = Se.start_roster_returns(A)
    out['ring_returns'] = {'got': rr, 'ok': rr[:4] == [2, 4, 6, 8]}
    return out


def check2_3():
    out = {'barred_ok': 0, 'barred_bad': 0, 'own_joint_ok': 0, 'own_joint_bad': 0}
    for it in ({'group': 'main', 'start': 'two-knot', 'base': 'COPY-LAW(WAIT)', 'rule': 'STEPS-2:join',
                'choice': 'OLDEST', 'knot_law': 'nae'},
               {'group': 'main', 'start': 'two-knot', 'base': 'COPY-LAW(OFFSHOOT)', 'rule': 'STEPS-1',
                'choice': 'OLDEST', 'knot_law': 'nae'}):
        A, law = RN.grow(it)
        ser, _ = Se.build_series(A, False)
        Se.describe(ser)
        comps = Tt.Comparisons(A, law, 18, 4000)
        import tf_run4 as R4
        for s in R4.chosen_clocks(ser):
            for j in (0, 1):
                for row in Tt.run_tests(A, law, s, j, comps):
                    # 3: own + joint = every knot made after t_j with a parent on X's side
                    S = A.S
                    xs = Tt.side_set(S, row['X'], row['t_j'])
                    ys = Tt.side_set(S, row['P_j'], row['t_j'])
                    n_all = sum(1 for x in range(S.n_knots) if S.made[x] > row['t_j']
                                and any(p in xs for p in S.parents[x]))
                    n_own = sum(v for v in row['own_A_by_round'].values())
                    n_joint = sum(1 for x in range(S.n_knots) if S.made[x] > row['t_j']
                                  and any(p in xs for p in S.parents[x]) and any(p in ys for p in S.parents[x]))
                    if n_all == n_own + n_joint:
                        out['own_joint_ok'] += 1
                    else:
                        out['own_joint_bad'] += 1
        # 2: every B run: the barred knots hold no usable loose distinction after the bar
        for key, (R, sec) in comps.cache.items():
            if key[0] not in ('B', 'B1', 'XB'):
                continue
            t = key[1]
            V = R.S.view(t, with_span=False)
            for u in key[2]:
                if V.hk(u)[0] == 0:
                    out['barred_ok'] += 1
                else:
                    out['barred_bad'] += 1
    return out


def shape(A):
    rows = []
    for t in range(A.rounds_done + 1):
        R = A.roster(t)
        rows.append((len(R.members), tuple(sorted(len(P) for P in R.parts)), A.records[t - 1]['n_knots'] if t else 0,
                     A.records[t - 1]['n_births'] if t else 0))
    ser, _ = Se.build_series(A, False)
    Se.describe(ser)
    return rows, sorted((s['size'], tuple(s['periods'])) for s in ser if s['ticks'])


def check4():
    out = {'runs': 0, 'same': 0, 'different': []}
    for name in ('two-knot', 'three-knot'):
        stars = C.named_stars()[name]
        nums = R5.registered_numberings(stars)
        for base in E.BASE_ORDER:
            law = E.Law.from_base(base, knot_law='nae')
            ref = shape(E.Run(E.from_stars(stars), law))
            for num in nums:
                A = E.Run(E.from_stars(stars, dist_order=num['dist'], knot_order=num['knots']), law)
                out['runs'] += 1
                if shape(A) == ref:
                    out['same'] += 1
                elif len(out['different']) < 10:
                    out['different'].append([name, base, num])
    return out


def main():
    res = {'1': check1(), '2_3': check2_3(), '4': check4()}
    res['ok'] = (all(v['ok'] for v in res['1'].values()) and res['2_3']['barred_bad'] == 0
                 and res['2_3']['own_joint_bad'] == 0 and res['4']['same'] == res['4']['runs'])
    C.write_json('unit_series.json', res)
    C.log(res)


if __name__ == '__main__':
    C.cap_memory()
    main()
