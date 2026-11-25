"""Unit tests of the rules of BD2 2 on structures built by hand (brief, item 1).

  python -B test_rules.py
"""
import sys

sys.dont_write_bytecode = True

import common
import eng


def births_of(rec, parent):
    return [b for b in rec['births'] if b['kind'] == 'offshoot' and b['parents'] == (parent,)]


def t_sole_against_two():
    """MET-SOLE: P's offshoot has one candidate (distinction 1, held by W and Z) and takes it; with a second
    candidate (2) it takes nothing.  The join (P, Z) has no candidate (W's shared distinctions are held by its
    parents)."""
    law = eng.Law('FLOOR1', 'CANCEL-RETIRE', 'MET-SOLE', 'nae')
    # P = 0, W = 1, Z = 2
    one = [[0, 10, 11], [0, 1, 5], [1, 6, 7]]
    run = eng.run_stars(one, law, rounds=1)
    rec = run.recs[0]
    (bP,) = births_of(rec, 0)
    assert [c[0] for c in bP['cands']] == [1] and bP['takes'] == [1], bP
    assert bP['cands'][0][1] == (1,), 'supplier is W'
    (bj,) = [b for b in rec['births'] if b['kind'] == 'join']
    assert bj['parents'] == (0, 2) and bj['cands'] == [] and bj['takes'] == []
    two = [[0, 10, 11], [0, 1, 2, 5], [1, 2, 6, 7]]
    run = eng.run_stars(two, law, rounds=1)
    (bP,) = births_of(run.recs[0], 0)
    assert [c[0] for c in bP['cands']] == [1, 2] and bP['takes'] == [], bP
    # the gate's MET(OLDEST) takes the oldest of the two
    run = eng.run_stars(two, eng.Law('FLOOR1', 'CANCEL-RETIRE', 'MET', 'nae', 'OLDEST'), rounds=1)
    (bP,) = births_of(run.recs[0], 0)
    assert bP['takes'] == [1]
    return 'ok'


def t_steps_sole():
    """STEPS1-SOLE and STEPS2-SOLE on a structure with a written record: the candidates are the eligible
    distinctions of the knots one (two) parent steps above the parent, not held by the parent."""
    S = eng.from_stars([[0, 1, 2], [1, 3], [0, 4, 5]])     # g = 0, q = 1 (holds 1 with g), p = 2 (holds 0 with g)
    S.parents[2] = (0,)
    law = eng.Law('FLOOR1', 'CANCEL-RETIRE', 'STEPS1-SOLE', 'nae')
    b = {'kind': 'offshoot', 'parents': (2,), 'loose': [4]}
    c = eng.candidates(S, law, b, None)
    assert [x[0] for x in c] == [1] and c[0][1] == (0,), c      # 0 is held by p; 1 is g's other shared one
    S2 = eng.from_stars([[0, 1, 2, 6], [1, 3, 6], [0, 4, 5]])
    S2.parents[2] = (0,)
    c = eng.candidates(S2, law, b, None)
    assert [x[0] for x in c] == [1, 6], c                        # two candidates: a sole-candidate take takes none
    law2 = eng.Law('FLOOR1', 'CANCEL-RETIRE', 'STEPS2-SOLE', 'nae')
    assert eng.candidates(S, law2, b, None) == []                # no knot two steps above
    return 'ok'


def t_owing_before_cancel():
    """PARENT-OWING: the owing is counted before any group is cancelled.  Ring(5,3) under FLOOR1/CANCEL-OFFSHOOT:
    in round 2 the joins of round 1 hold one usable distinction and owe 4; every group holding one is cancelled,
    and each makes one offshoot, which receives max(2, 4) = 4."""
    st = common.load('starts.json')['stars']
    law = eng.Law('PARENT-OWING', 'CANCEL-OFFSHOOT', 'MET-SOLE', 'nae')
    run = eng.run_stars(st['Ring(5,3)'], law, rounds=2)
    rec = run.recs[1]
    for u in range(5, 10):
        assert rec['owe'][u] == 4 and u in rec['short'], (u, rec['owe'].get(u))
        (b,) = births_of(rec, u)
        assert b['o'] == 4 and b['f'] == 4, b
    assert not [g for g in rec['groups'] if g not in rec['cancelled']]
    # the same under the caps: min(max(2, 4), 3) = 3 and min(max(2, 4), 4) = 4
    for r, want in (('PARENT-OWING-CAP3', 3), ('PARENT-OWING-CAP4', 4)):
        run = eng.run_stars(st['Ring(5,3)'], eng.Law(r, 'CANCEL-OFFSHOOT', 'MET-SOLE', 'nae'), rounds=2)
        (b,) = births_of(run.recs[1], 5)
        assert b['f'] == want, (r, b['f'])
    # joins receive as FLOOR1
    assert all(b['f'] == max(3 - b['p'], 1) for b in rec['births'] if b['kind'] == 'join')
    return 'ok'


def t_offshoot_that_takes():
    """PARENT-OWING: an offshoot that takes (p = 2) still receives max(2, o); FLOOR1 would give 1."""
    law = eng.Law('PARENT-OWING', 'CANCEL-RETIRE', 'MET-SOLE', 'nae')
    run = eng.run_stars([[0, 10, 11], [0, 1, 5], [1, 6, 7]], law, rounds=1)
    (bP,) = births_of(run.recs[0], 0)
    assert bP['takes'] == [1] and bP['p'] == 2 and bP['o'] == 1 and bP['f'] == 2, bP
    run = eng.run_stars([[0, 10, 11], [0, 1, 5], [1, 6, 7]], eng.Law('FLOOR1', 'CANCEL-RETIRE', 'MET-SOLE', 'nae'),
                        rounds=1)
    (bP,) = births_of(run.recs[0], 0)
    assert bP['p'] == 2 and bP['f'] == 1
    # the controls: PARENT-OWING-PLAIN gives max(o, 3 - p, 1) = 1 here; PARENT-OWING-1 max(1, o) = 1
    for r, want in (('PARENT-OWING-PLAIN', 1), ('PARENT-OWING-1', 1), ('OFFSHOOT-TWO', 2), ('OFFSHOOT-THREE', 3),
                    ('MOD2', 3)):
        run = eng.run_stars([[0, 10, 11], [0, 1, 5], [1, 6, 7]], eng.Law(r, 'CANCEL-RETIRE', 'MET-SOLE', 'nae'),
                            rounds=1)
        (bP,) = births_of(run.recs[0], 0)
        assert bP['f'] == want, (r, bP['f'])
    return 'ok'


def t_short_by_keeper():
    """SHORT-BY: u holds 3 and owes 4; its groups are cancelled; it makes min(3, 1) = 1 offshoot from its first
    usable distinction and keeps 2; it stays in the demand roster with what it keeps; in the next round it is a
    member with h = 2, its shortness read afresh (it owes nothing) and it makes 2 offshoots."""
    # u = 0 with a1..a4 = 1..4 and loose 10, 11, 12; dead w_i = 1..4 holding a_i and b_i = 5..8; v_i = 5..8
    stars = [[1, 2, 3, 4, 10, 11, 12], [1, 5], [2, 6], [3, 7], [4, 8],
             [5, 20, 21, 22], [6, 23, 24, 25], [7, 26, 27, 28], [8, 29, 30, 31]]
    S0 = eng.from_stars(stars)
    law = eng.Law('FLOOR1', 'SHORT-BY', 'MET-SOLE', 'nae')
    run = eng.run_stars(stars, law, rounds=2)
    r1, r2 = run.recs
    assert r1['owe'][0] == 4 and 0 in r1['short'] and r1['act'][0] == 'short-by 1 keep 2', r1['act'][0]
    assert all(g in r1['cancelled'] for g in r1['groups'] if 0 in g)
    (b,) = births_of(r1, 0)
    assert b['loose'] == [S0.usable(0)[0]]
    assert r1['kept_by'][0] == S0.usable(0)[1:]
    assert (0, 2, 0) in r1['persisting']
    assert 0 in r1['demand'].members
    assert 0 in r2['members'] and r2['h'][0] == 2 and 0 not in r2['short'] and r2['act'][0] == 'none'
    assert len(births_of(r2, 0)) == 2
    # with o - h >= h it is CANCEL-OFFSHOOT: u holds 1 and owes 4
    stars2 = [[1, 2, 3, 4, 10]] + stars[1:]
    run = eng.run_stars(stars2, law, rounds=1)
    assert run.recs[0]['act'][0] == 'short-by 1 keep 0'
    return 'ok'


def t_j_each_part():
    """J-EACH-PART: an offshoot takes every eligible distinction held by a member of another part."""
    st = common.load('starts.json')['stars']
    law = eng.Law('FLOOR1', 'CANCEL-WAIT', 'J-EACH-PART', 'nae')
    run = eng.run_stars(st['two-knot'], law, rounds=2)
    r2 = run.recs[1]
    R = r2['roster']
    for b in r2['births']:
        if b['kind'] != 'offshoot':
            continue
        p = b['parents'][0]
        want = sorted({d for w in R.members if R.part_of[w] != R.part_of[p]
                       for d in run.snaps[1].places[w] if len(run.snaps[1].holders[d]) >= 2})
        assert sorted(b['takes']) == want, (b, want)
    return 'ok'


if __name__ == '__main__':
    for f in (t_sole_against_two, t_steps_sole, t_owing_before_cancel, t_offshoot_that_takes, t_short_by_keeper,
              t_j_each_part):
        print(f.__name__, f())
