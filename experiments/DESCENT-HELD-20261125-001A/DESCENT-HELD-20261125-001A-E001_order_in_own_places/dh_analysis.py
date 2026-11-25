"""Reading one run: arm R (base law) and arm W (a count form).  Shared by parts 1, 4, 5 and 8.  Deviations 6-14, 23."""
from __future__ import annotations

import dh_engine as E


def fives_pred(vx, vy):
    return (vx - vy) % 5 in (1, 2)


def first_wrong_round(S, wrong_list_all):
    """Round at which each wrong place first exists (the later of its two holders' births)."""
    if not wrong_list_all:
        return None
    return min(max(S.born[x], S.born[y]) for (d, x, y, k) in wrong_list_all)


def m2_first_failing(S, recs):
    """DH 5.3, deviations 23: first round with a new knot x and a parent y with n(x) != n(y) + 1 (mod 3) ('some'), and
    the other reading (for every parent)."""
    some = None
    every = None
    for r in recs:
        for x in r['new']:
            nx_ = len(S.places[x])
            bad = [((nx_ - len(S.places[y])) % 3) != 1 for y in S.parents[x]]
            if any(bad) and some is None:
                some = r['round']
            if all(bad) and every is None:
                every = r['round']
        if some is not None and every is not None:
            break
    return some, every


def analyze_base(S, recs, end, with_place=True):
    ds = E.descent_summary(S, recs)
    lq = E.lq_condition_fails(S, recs)
    row = {
        'rounds': E.rounds_changed(recs), 'rounds_run': len(recs), 'knots': len(S.places), 'end': end,
        'births': [r['births'] for r in recs],
        'counted': ds['counted'], 'counted_first_round': ds['counted_first_round'],
        'bprime_fails': ds['bprime_fails'], 'bprime_first_round': ds['bprime_first_round'],
        'greatest': ds['greatest'], 'greatest_by_round': ds['greatest_by_round'], 'max_ps': ds['max_ps'],
        'lq_fails_rounds': lq, 'first_no_birth_round': E.first_no_birth_round(recs),
        'closing_births': sum(1 for r in recs if r['closing']),
    }
    if with_place:
        st5 = [v % 5 for v in S.ps]
        f5 = E.place_rule(S, None, stamp=st5, pred=fives_pred, keep_wrong=10 ** 9)
        row['fives_right_on'] = f5['wrong'] == 0
        row['fives_first_wrong_round'] = first_wrong_round(S, f5['wrong_list'])
        st3 = [v % 3 for v in S.ps]
        f3 = E.place_rule(S, None, stamp=st3, pred=lambda a, b: (a - b) % 3 == 1, keep_wrong=0)
        row['three_stamp_right_on'] = f3['wrong'] == 0
        pr = E.place_rule(S, None, keep_wrong=0)
        row['places_count_rule_by_kind'] = pr['by_kind']
    m2s, m2e = m2_first_failing(S, recs)
    row['m2_fail_round_some'] = m2s
    row['m2_fail_round_every'] = m2e
    return row


def alt_stop(row):
    """The stopping swap (deviations 6): the registered run cut at its first round with no birth."""
    r0 = row['first_no_birth_round']

    def before(v):
        return v is not None and (r0 is None or v < r0)
    g = 0
    for k, v in row['greatest_by_round'].items():
        if r0 is None or int(k) < r0:
            g = max(g, v)
    return {'counted': before(row['counted_first_round']), 'bprime_fails': before(row['bprime_first_round']),
            'greatest': g, 'lq_fails': any(before(v) for v in row['lq_fails_rounds']),
            'fives_right_on': not before(row.get('fives_first_wrong_round'))}


def predicted_wrong_c(S, t):
    """P6, the general rule for (c) under NEXT3-BARRED: the predicted wrong places after round t."""
    K = S.k_at[t]
    rr, ret = S.retired_round, S.ret
    delta = [(ret[u] if rr[u] is not None and rr[u] <= t else 0) % 3 for u in range(K)]
    out = set()
    for d in range(S.m_at[t]):
        h = S.holders[d]
        if len(h) < 2 or h[0] >= K or h[1] >= K:
            continue
        a, c = h
        for x, y in ((a, c), (c, a)):
            kind = E.place_kind(S, x, y)
            e = (delta[y] - delta[x]) % 3
            if (kind == 'parent' and e != 0) or (kind == 'child' and e == 1) or (kind == 'start' and e == 2):
                out.add((d, x, y))
    return out


def analyze_armw(S, recs, end, form, knot_law, L, keep_wrong=20):
    ds = E.descent_summary(S, recs)
    a = E.condition_a(S, form)
    c = E.condition_c(S, form)
    d = E.condition_d(S) if knot_law == 'parity' else True
    bprime = not ds['bprime_fails']
    retired = any(S.ret)
    every_round = form == 'BB' and retired
    rounds_checked = list(range(0, S.round + 1)) if every_round else [S.round]
    right_on = True
    first_wrong = None
    p6_ok = None
    p6_rows = []
    for t in rounds_checked:
        pr_t = E.place_rule(S, form, t=t, keep_wrong=10 ** 9 if (form == 'BB' and L.treatment == 'CANCEL-RETIRE')
                            else 0)
        if pr_t['wrong']:
            right_on = False
            if first_wrong is None:
                first_wrong = t
        if form == 'BB' and L.treatment == 'CANCEL-RETIRE' and a and bprime and d:
            actual = {(dd, x, y) for (dd, x, y, k) in pr_t['wrong_list']}
            pred = predicted_wrong_c(S, t)
            ok = actual == pred
            p6_rows.append({'round': t, 'wrong': len(actual), 'predicted': len(pred), 'equal': ok})
            p6_ok = ok if p6_ok is None else (p6_ok and ok)
    pr = E.place_rule(S, form, keep_wrong=keep_wrong)
    counted3 = [x for x in range(len(S.places)) if S.differ[x]]
    bp_births = [x for x in range(len(S.places)) if S.born[x] and len({S.ps[y] % 3 for y in S.parents[x]}) > 1]
    row = {
        'rounds': E.rounds_changed(recs), 'rounds_run': len(recs), 'knots': len(S.places), 'end': end,
        'births': [r['births'] for r in recs],
        'a': a, 'bprime': bprime, 'b': not ds['counted'], 'c': c, 'd': d,
        'greatest': ds['greatest'], 'bprime_first_round': ds['bprime_first_round'],
        'bprime_first_births': ds['bprime_first_births'][:20],
        'place_rule_last_by_kind': pr['by_kind'], 'wrong_last': pr['wrong'], 'wrong_examples': pr['wrong_list'],
        'right_on_every_structure': right_on, 'first_round_with_a_wrong_place': first_wrong,
        'every_round_checked': every_round,
        'counted_step3': len(counted3), 'bprime_births': len(bp_births),
        'counted_step3_equals_bprime_births': set(counted3) == set(bp_births),
        'closing_births': sum(1 for x in range(len(S.places)) if S.closing[x]),
        'closing_hyp_s': [S.hyp_s[x] for x in range(len(S.places)) if S.closing[x]],
        'retired_knots': sum(1 for v in S.ret if v),
        's_positive': sum(1 for x in range(len(S.places)) if S.born[x] and S.s[x] > 0),
        'new_knots': sum(1 for x in range(len(S.places)) if S.born[x]),
        's_sum': sum(S.s[x] for x in range(len(S.places)) if S.born[x]),
    }
    # the predictions' judgements on this run
    row['P3'] = (right_on if (a and bprime and c and d) else None)
    if a and c and d and not bprime:
        first_counted = all(S.differ[x] for x in ds['bprime_first_births'])
        row['P4'] = (not right_on) and first_counted
        row['P4_first_births_counted'] = first_counted
    else:
        row['P4'] = None
    if form in ('PU', 'PB') and not a:
        row['P5'] = pr['by_kind']['start'][1] > 0
    else:
        row['P5'] = None
    row['P6'] = p6_ok
    row['P6_rows'] = p6_rows
    return row
