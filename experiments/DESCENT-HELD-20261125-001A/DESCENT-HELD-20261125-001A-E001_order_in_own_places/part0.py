"""Part 0: the checks (pre-registration, "The run", part 0 (a)-(g)).  Writes part0.json.  Readings: deviations 1-22.

python -B part0.py [--procs P]
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import Counter

from dh_common import (lr_core, knots, STARTS_JSON, HAND, ROOT, write, log, n_procs, load_avg)
import dh_engine as E

NAMED = list(STARTS_JSON['starts'].keys())
STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}


# ------------------------------------------------------------------------------------------------ (a) the gate
def gate_pair(args):
    start, ration, treatment, release = args
    stars = lr_core.start_stars(start)
    L = E.Law('gate', ration, treatment, release)
    A = lr_core.Str(stars)
    S = E.Struct(stars)
    rows = []
    ok = True
    first_diff = None
    while S.round < 8:
        ra = lr_core.own_round(A, ration, treatment, release)
        rb = E.do_round(S, L, None, 'parity')
        same = (A.places == S.places and A.holders == S.holders and A.barred == S.barred
                and list(A.parents) == list(S.parents) and ra['births'] == rb['births'])
        rows.append({'round': rb['round'], 'births': rb['births'], 'own_round_births': ra['births'],
                     'knots': len(S.places), 'equal_names': same})
        if not same:
            ok = False
            if first_diff is None:
                first_diff = rb['round']
        if rb['stalled'] or (rb['births'] == 0 and rb['newly_barred'] == 0) or len(S.places) > 3000:
            break
    return {'start': start, 'law': [ration, treatment, release], 'rounds': len(rows), 'pass': ok,
            'first_difference': first_diff, 'rows': rows}


def part_a(pool):
    g = json.load(open(os.path.join(ROOT, 'artifacts', 'LOCAL-ROUND-20261123-001A',
                                    'LOCAL-ROUND-20261123-001A-E001_local_round', 'gate.json')))
    jobs = [(p['start'], p['law'][0], p['law'][1], 'RELEASE') for p in g['pairs']]
    res = pool.map(gate_pair, jobs)
    # extra (labelled so): HOLD against own_round(release='HOLD') for the rations own_round has
    extra_jobs = []
    for start in ('TWO-KNOT', 'THREE-KNOT', 'Ring(5,3)', 'D2(4,3)', 'GEN7', 'SCC'):
        for ration, treatment in (('RATION-3', 'CANCEL-WAIT'), ('FLOOR1', 'CANCEL-RETIRE'),
                                  ('FLOOR1', 'CANCEL-OFFSHOOT'), ('ORD', 'CANCEL-WAIT')):
            extra_jobs.append((start, ration, treatment, 'HOLD'))
    extra = pool.map(gate_pair, extra_jobs)
    return {'pairs': res, 'n_pairs': len(res), 'pass': all(r['pass'] for r in res),
            'structures_compared': sum(r['rounds'] for r in res),
            'extra_HOLD_against_own_round': {'pairs': extra, 'pass': all(r['pass'] for r in extra),
                                             'note': 'extra, not registered: own_round(release="HOLD") as the reference'}}


# ------------------------------------------------------------------------------------------------ hand cases
def knot_row(S, x):
    return {'knot': x, 'parents': list(S.parents[x]), 'parents_parent_steps': [S.ps[y] for y in S.parents[x]],
            'parent_steps': S.ps[x], 'places': len(S.places[x]), 'p': S.p[x], 'F': S.F[x], 's': S.s[x],
            'barred_at_birth': S.z[x]}


def compare_rounds(S, recs, expected):
    out = []
    ok = True
    for er in expected:
        r = next((q for q in recs if q['round'] == er['round']), None)
        got = [knot_row(S, x) for x in r['new']] if r else []
        same_births = got == er['new_knots']
        same_wait = (sorted(r['waited']) if r else None) == sorted(er['short_members_that_waited'])
        if not (same_births and same_wait):
            ok = False
        diffs = []
        if not same_births:
            for a, b in itertools.zip_longest(got, er['new_knots']):
                if a != b:
                    diffs.append({'got': a, 'expected': b})
        out.append({'round': er['round'], 'births': len(got), 'expected_births': len(er['new_knots']),
                    'births_equal': same_births, 'waited': r['waited'] if r else None,
                    'waited_equal': same_wait, 'differences': diffs[:6]})
    return ok, out


FORM_KEY = {'base': None, 'NEXT3-PLACES (usable)': 'PU', 'NEXT3-PLACES (barred)': 'PB', 'NEXT3-BARRED': 'BB'}


def law_from_text(t):
    parts = t.split('/')
    return E.Law(t, parts[0], parts[1], parts[2] if len(parts) > 2 else 'RELEASE', 'FILLERS' in parts)


def part_b():
    out = {}
    h = HAND['H1_two_knot']
    L = law_from_text(h['base'])
    res = {}
    for fname, exp in h['forms'].items():
        form = FORM_KEY[fname]
        S, recs, end = E.grow(h['stars'], L, form, 'parity', R=len(exp))
        ok, rows = compare_rounds(S, recs, exp)
        res[fname] = {'pass': ok, 'rounds': rows, 'births_by_round': [r['births'] for r in recs]}
    out['H1'] = {'stars': h['stars'], 'law': h['base'], 'forms': res, 'pass': all(v['pass'] for v in res.values())}
    # T, the cycle of three
    T = HAND['T_triangle_closing']['stars']
    tres = []
    tok = True
    for L in (E.LAW['F1O'], E.LAW['ORD'], E.Law('FLOOR0', 'FLOOR0', 'CANCEL-OFFSHOOT')):
        for form in E.FORMS:
            for swap in (False, True):
                S, recs, end = E.grow(T, L, form, 'parity', R=1 if swap else 8, closing_swap=swap)
                x = 3
                row = {'law': L.text(), 'form': E.FORM_NAMES[form], 'closing_reading': 'swap' if swap else 'registered',
                       'rounds': len(recs), 'end': end, 'closing_flag': S.closing[x], 'parents': list(S.parents[x]),
                       'places': len(S.places[x]), 'F': S.F[x], 'FB': S.FB[x], 's': S.s[x], 'z': S.z[x],
                       'hyp_s': S.hyp_s[x]}
                pr = E.place_rule(S, form, t=1)
                row['place_rule_t1'] = pr['by_kind']
                own_side_wrong = sum(1 for (d, a, b, k) in pr['wrong_list'] if a == x and k == 'parent')
                parent_side_wrong = sum(1 for (d, a, b, k) in pr['wrong_list'] if b == x)
                row['closing_knot_places_to_parents_wrong_own_side'] = own_side_wrong
                row['parents_places_to_closing_knot_wrong'] = parent_side_wrong
                pt = knots.parity_test(E.KS(S, 1))
                row['parity_test_t1_fail'] = pt['fail']
                row['parity_methods_disagree'] = pt['disagree']
                if not swap:
                    kap = [S.kappa(u, form) % 3 for u in range(4)]
                    row['counts_after'] = kap
                    expect = (S.closing[x] and len(S.places) == 4 and all(len(P) == 3 for P in S.places)
                              and len(set(kap)) == 1 and own_side_wrong == 3 and parent_side_wrong == 0
                              and S.F[x] == 0 and S.s[x] == 0 and end == 'stopped' and pt['fail'] == []
                              and not pt['disagree'])
                else:
                    if L.ration == 'FLOOR0':
                        want_F, want_s = 0, 1
                    else:
                        want_F, want_s = 1, (1 if form == 'BB' else 0)
                    expect = (S.closing[x] and S.F[x] == want_F and S.s[x] == want_s and x in pt['fail']
                              and not pt['disagree'])
                row['as_stated'] = bool(expect)
                tok = tok and expect
                tres.append(row)
    out['T'] = {'stars': T, 'rows': tres, 'pass': tok}
    return out


# ------------------------------------------------------------------------------------------------ (c) planted error
def run_conditions(S, recs, form, knot_law='parity'):
    ds = E.descent_summary(S, recs)
    return {'a': E.condition_a(S, form), 'bprime': not ds['bprime_fails'], 'c': E.condition_c(S, form),
            'd': E.condition_d(S) if knot_law == 'parity' else True}


def planted(args):
    start, lname, form = args
    L = E.LAW[lname]
    S, recs, end = E.grow(STARS[start], L, form, 'parity', R=8, N=3000)
    cond = run_conditions(S, recs, form)
    r2 = next((r for r in recs if r['round'] == 2), None)
    if not r2 or not r2['new']:
        return {'start': start, 'law': lname, 'form': form, 'skipped': 'no birth in round 2', 'pass': True}
    x = r2['new'][0]
    V0 = E.place_verdict_map(S, form)
    d_new = len(S.holders)
    S.holders.append([x]); S.barred.append(True); S.bround.append(S.round); S.dround.append(S.round)
    S.places[x].append(d_new); S.b[x] += 1
    V1 = E.place_verdict_map(S, form)
    changed = {k for k in V0 if V0[k][1] != V1[k][1]}
    pred = set()
    for k in V0:
        d, a, b = k
        if a == x and b in S.parents[x]:
            pred.add(k)                     # x's places to its parents, x's side
        elif b == x and a in S.parents[x]:
            pred.add(k)                     # the parents' places to x
        elif b == x and x in S.parents[a]:
            pred.add(k)                     # x's children's places to x
    all_hold = all(cond.values())
    became_wrong = None
    if all_hold:
        became_wrong = all((V0[k][1] == (V0[k][0] == 'parent')) and (V1[k][1] != (V1[k][0] == 'parent'))
                           for k in changed)
    # deviations 28: the place rule's own arithmetic.  With delta = kappa(other) - kappa(x) before the error, adding 1 to
    # kappa(x) changes the verdict at x's place iff delta = 0 or -1 (mod 3), at the other holder's place iff delta = +-1.
    kap = [S.kappa(u, form) for u in range(len(S.places))]
    kap[x] -= 1                                   # before the error
    formula = set()
    for k in V0:
        d, a, b = k
        if a == x:
            dl = (kap[b] - kap[x]) % 3
            if dl in (0, 2):
                formula.add(k)
        elif b == x:
            dl = (kap[a] - kap[x]) % 3
            if dl in (1, 2):
                formula.add(k)
    ok_literal = changed == pred and (became_wrong is not False)
    ok_conditional = (not all_hold) or (changed == pred and became_wrong)
    return {'start': start, 'law': lname, 'form': form, 'x': x, 'changed': len(changed), 'predicted': len(pred),
            'equal': changed == pred, 'conditions': cond, 'became_wrong_where_conditions_hold': became_wrong,
            'children_of_x': len(S.kids[x]), 'pass': ok_literal, 'pass_where_conditions_hold': ok_conditional,
            'changed_equals_formula': changed == formula,
            'extra_changed': sorted(map(list, changed - pred))[:5], 'missing': sorted(map(list, pred - changed))[:5]}


def part_c(pool):
    jobs = [(s, L.name, f) for s in NAMED for L in E.BASES for f in ('PB', 'BB')]
    res = pool.map(planted, jobs)
    return {'runs': res, 'n': len(res), 'pass': all(r['pass'] for r in res),
            'pass_as_worded_on': sum(1 for r in res if r['pass']),
            'fail_as_worded': [[r['start'], r['law'], r['form'], r['conditions']] for r in res if not r['pass']],
            'pass_where_conditions_hold': all(r.get('pass_where_conditions_hold', True) for r in res),
            'changed_equals_formula_on': sum(1 for r in res if r.get('changed_equals_formula', True)),
            'skipped': sum(1 for r in res if 'skipped' in r),
            'runs_where_all_four_conditions_hold': sum(1 for r in res if 'conditions' in r and all(r['conditions'].values()))}


# ------------------------------------------------------------------------------------------------ (d) holding runs
def part_d():
    g = json.load(open(os.path.join(ROOT, 'artifacts', 'LEAST-RECORD-20261124-001A',
                                    'LEAST-RECORD-20261124-001A-E001_least_record', 'generations.json')))
    rows = []
    for r in g['P3']:
        L = E.LAW[r['law_short']]
        stars = lr_core.start_stars(r['start'])
        S, recs, end = E.grow(stars, L, None, 'parity', R=6, N=3000)
        mine = [q['births'] for q in recs]
        theirs = [e['births'] for e in r['events']]
        ds = E.descent_summary(S, recs)
        rows.append({'law': r['law_short'], 'start': r['start'], 'births_by_round': mine, 'recorded': theirs,
                     'equal': mine == theirs, 'knots': len(S.places), 'recorded_knots': r['knots'],
                     'counted': ds['counted'], 'greatest_difference': ds['greatest'], 'end': end})
    return {'runs': rows, 'pass': all(x['equal'] and not x['counted'] for x in rows),
            'equal': sum(x['equal'] for x in rows), 'no_unequal_parents': sum(not x['counted'] for x in rows)}


# ------------------------------------------------------------------------------------------------ (e) witnesses
def part_e(census_stars):
    out = {}
    ok_all = True
    for key in ('W1_waiting', 'W2_holding', 'W2b_holding_retiring'):
        h = HAND[key]
        L = law_from_text(h['law'])
        S, recs, end = E.grow(h['stars'], L, None, 'parity', R=len(h['rounds']))
        ok, rows = compare_rounds(S, recs, h['rounds'])
        idx_ok = census_stars[h['census_index']] == h['stars']
        unequal = [{'round': S.born[x], 'knot': x, 'parents': list(S.parents[x]),
                    'parents_parent_steps': [S.ps[y] for y in S.parents[x]]}
                   for x in range(len(S.places)) if S.born[x] and len({S.ps[y] for y in S.parents[x]}) > 1]
        out[key] = {'stars': h['stars'], 'law': h['law'], 'census_index': h['census_index'],
                    'census_index_gives_these_stars': idx_ok, 'pass': ok and idx_ok, 'rounds': rows,
                    'births_with_parents_at_different_parent_steps': unequal, 'stated': h['the_birth']}
        ok_all = ok_all and ok and idx_ok
    out['pass'] = ok_all
    return out


# ------------------------------------------------------------------------------------------------ (f) shortness
def independent_short(S, L):
    """From the structure alone: members by usable loose places, met sets, groups, owing, short."""
    hold = {}
    for u in range(len(S.places)):
        h = sum(1 for d in S.places[u] if len(S.holders[d]) == 1 and not S.barred[d])
        if h:
            hold[u] = h
    acc = {}
    for d, hs in enumerate(S.holders):
        if len(hs) == 2:
            a, b = hs
            if b in hold:
                acc.setdefault(a, set()).add(b)
            if a in hold:
                acc.setdefault(b, set()).add(a)
    fam = {frozenset(v) for v in acc.values() if len(v) >= 2}
    groups = lr_core.compute_groups(sorted(hold), fam)
    owe = Counter(u for g in groups for u in g)
    short = sorted(u for u in hold if owe[u] > hold[u])
    loose_all = {u: sum(1 for d in S.places[u] if len(S.holders[d]) == 1) for u in hold}
    short_all = sorted(u for u in hold if owe[u] > loose_all[u])
    with_barred = [u for u in hold if loose_all[u] > hold[u]]
    return short, short_all, with_barred


def shortness(args):
    start, lname, form = args
    L = E.LAW[lname]
    S = E.Struct(STARS[start])
    rounds = 0
    mism = 0
    differs = 0
    members_with_barred = 0
    while S.round < 8 and len(S.places) <= 3000:
        sh, sh_all, wb = independent_short(S, L)
        members_with_barred += len(wb)
        if sh != sh_all:
            differs += 1
        rec = E.do_round(S, L, form, 'parity')
        rounds += 1
        if rec['short'] != sh:
            mism += 1
        if rec['stalled'] or (rec['births'] == 0 and rec['newly_barred'] == 0):
            break
    # the deliberately wrong engine: shortness on every loose place
    S1, r1, _ = E.grow(STARS[start], L, form, 'parity', R=8, N=3000)
    try:
        S2, r2, _ = E.grow(STARS[start], L, form, 'parity', R=8, N=3000, all_loose_short=True)
        wrong_engine_differs = [q['births'] for q in r1] != [q['births'] for q in r2] or S1.parents != S2.parents
    except IndexError:
        wrong_engine_differs = True      # the wrong engine has a member pay from places it does not have
    return {'start': start, 'law': lname, 'form': form, 'rounds': rounds, 'mismatches': mism,
            'rounds_where_all_loose_reading_gives_another_short_set': differs,
            'member_rounds_holding_barred_places': members_with_barred,
            'all_loose_engine_gives_other_births': wrong_engine_differs}


def part_f(pool):
    jobs = [(s, L.name, f) for s in NAMED for L in E.BASES for f in ('PU', 'PB', 'BB')]
    res = pool.map(shortness, jobs)
    return {'runs': res, 'n': len(res), 'pass': all(r['mismatches'] == 0 for r in res),
            'member_rounds_holding_barred_places': sum(r['member_rounds_holding_barred_places'] for r in res),
            'rounds_where_all_loose_reading_differs': sum(r['rounds_where_all_loose_reading_gives_another_short_set']
                                                          for r in res),
            'runs_where_all_loose_engine_gives_other_births': sum(r['all_loose_engine_gives_other_births'] for r in res)}


# ------------------------------------------------------------------------------------------------ (g) numberings
NUMBERING_BASES = ['R3W', 'F1O', 'F1R', 'ORD', 'C3W']       # deviations 18


def renumber(stars, knot_order, newlab):
    return [sorted(newlab[d] for d in stars[k]) for k in knot_order]


def numbering_job(args):
    start, chunk = args
    stars = STARS[start]
    refs = {}
    for ln in NUMBERING_BASES:
        for form in E.FORMS:
            S, recs, end = E.grow(stars, E.LAW[ln], form, 'parity', R=4, N=10 ** 9)
            refs[(ln, form)] = (E.snapshot_stars(S, S.round), [q['births'] for q in recs])
    runs = 0
    diffs = []
    for knot_order, perm in chunk:
        labels = sorted({d for s in stars for d in s})
        newlab = {labels[i]: perm[i] for i in range(len(labels))}
        st = renumber(stars, knot_order, newlab)
        for ln in NUMBERING_BASES:
            for form in E.FORMS:
                S, recs, end = E.grow(st, E.LAW[ln], form, 'parity', R=4, N=10 ** 9)
                (rs, rb), rbirths = refs[(ln, form)]
                ss, sb = E.snapshot_stars(S, S.round)
                runs += 1
                same = [q['births'] for q in recs] == rbirths and E.isomorphic(ss, sb, rs, rb)
                if not same:
                    diffs.append({'knots': list(knot_order), 'perm': list(perm), 'law': ln, 'form': form})
    return {'start': start, 'runs': runs, 'differences': diffs}


def part_g(pool):
    jobs = []
    for start in ('LONE-THREE', 'LONE-FOUR', 'TWO-KNOT', 'TRIANGLE'):
        stars = STARS[start]
        m = len({d for s in stars for d in s})
        assert m <= 6
        allnum = [(ko, perm) for ko in itertools.permutations(range(len(stars)))
                  for perm in itertools.permutations(range(m))]
        step = max(1, len(allnum) // 24)
        for i in range(0, len(allnum), step):
            jobs.append((start, allnum[i:i + step]))
    res = pool.map(numbering_job, jobs)
    by = {}
    for r in res:
        b = by.setdefault(r['start'], {'runs': 0, 'differences': []})
        b['runs'] += r['runs']
        b['differences'] += r['differences']
    return {'by_start': by, 'runs': sum(b['runs'] for b in by.values()),
            'differences': sum(len(b['differences']) for b in by.values()),
            'bases': NUMBERING_BASES, 'rounds': 4, 'test': 'exact isomorphism of knots and distinctions with marks, '
                                                            'and births by round',
            'pass': all(not b['differences'] for b in by.values())}


def main():
    import multiprocessing as mp
    procs = n_procs()
    if '--procs' in sys.argv:
        procs = min(procs, int(sys.argv[sys.argv.index('--procs') + 1]))
    log('part 0, load %.1f, %d processes' % (load_avg(), procs))
    from dh_census import census_stars
    cs = census_stars()
    out = {'part': 0, 'load_at_start': load_avg(), 'processes': procs}
    t0 = time.time()
    with mp.Pool(procs) as pool:
        t = time.time(); out['a_gate'] = part_a(pool); out['a_gate']['seconds'] = round(time.time() - t, 1)
        log('a', out['a_gate']['pass'], out['a_gate']['extra_HOLD_against_own_round']['pass'])
        t = time.time(); out['b_hand_cases'] = part_b(); out['b_hand_cases']['seconds'] = round(time.time() - t, 1)
        log('b', out['b_hand_cases']['H1']['pass'], out['b_hand_cases']['T']['pass'])
        t = time.time(); out['c_planted_error'] = part_c(pool); out['c_planted_error']['seconds'] = round(time.time() - t, 1)
        log('c', out['c_planted_error']['pass'])
        t = time.time(); out['d_holding_runs'] = part_d(); out['d_holding_runs']['seconds'] = round(time.time() - t, 1)
        log('d', out['d_holding_runs']['pass'])
        t = time.time(); out['e_witnesses'] = part_e(cs); out['e_witnesses']['seconds'] = round(time.time() - t, 1)
        log('e', out['e_witnesses']['pass'])
        t = time.time(); out['f_shortness'] = part_f(pool); out['f_shortness']['seconds'] = round(time.time() - t, 1)
        log('f', out['f_shortness']['pass'])
        t = time.time(); out['g_numberings'] = part_g(pool); out['g_numberings']['seconds'] = round(time.time() - t, 1)
        log('g', out['g_numberings']['pass'], out['g_numberings']['runs'])
    others = all(out[k]['pass'] for k in ('a_gate', 'd_holding_runs', 'e_witnesses', 'f_shortness',
                                          'g_numberings')) and \
        out['b_hand_cases']['H1']['pass'] and out['b_hand_cases']['T']['pass']
    out['pass'] = others and out['c_planted_error']['pass']
    out['pass_every_check_but_c_as_worded'] = others
    out['c_where_conditions_hold_and_formula'] = (out['c_planted_error']['pass_where_conditions_hold'] and
                                                 out['c_planted_error']['changed_equals_formula_on'] ==
                                                 out['c_planted_error']['n'])
    out['seconds'] = round(time.time() - t0, 1)
    write('part0.json', out)
    log('part 0 pass', out['pass'], out['seconds'])


if __name__ == '__main__':
    main()
