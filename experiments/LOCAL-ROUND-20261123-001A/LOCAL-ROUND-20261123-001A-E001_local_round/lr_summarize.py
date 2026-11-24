"""Verdicts for P1-P14, the comparison with the numbers disclosed before the freeze, and the replays.

    python -B lr_summarize.py      # reads runs/*.json, writes summary.json, summary.md and listings/*.json
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lr_configs as K  # noqa: E402
import lr_core as C  # noqa: E402
import lr_laws as L  # noqa: E402
import lr_reference as RF  # noqa: E402
from lr_run import OUT as RUNS, slug  # noqa: E402
from lr_run_all import configs  # noqa: E402
from lr_search import Runner  # noqa: E402

ART = RUNS.parent
LIST = ART / 'listings'


def load(cid):
    p = RUNS / (slug(cid) + '.json')
    if p.exists():
        return json.loads(p.read_text())
    p = RUNS / (slug(cid) + '.json.gz')
    if p.exists():
        with gzip.open(p, 'rt') as fh:
            return json.load(fh)
    return None


def kinds(run):
    """Outcome per kind of order: dict kind -> (n match, n mismatch, n underbuild) and every-order facts."""
    eo = run['every_order']
    o = eo.get('orders', {})
    return {
        'every': {'finished': eo.get('finished'), 'least': eo.get('least_n'), 'keys': eo.get('keys'),
                  'depth': eo.get('searched_to_births'), 'mismatch_orders': int(o.get('mismatch', '0')),
                  'underbuild_orders': int(o.get('underbuild', '0')), 'match_orders': int(o.get('match', '0')),
                  'stopped': eo.get('stopped'), 'seconds': eo.get('seconds'), 'mismatch_edges': eo.get('mismatch_edges')},
        'sampled': run['sampled']['counts'],
        'xlast': run['xlast']['counts']}


def differs(run):
    k = kinds(run)
    e = k['every']
    return (e['least'] is not None or e['underbuild_orders'] > 0 or e['mismatch_orders'] > 0
            or k['sampled']['mismatch'] + k['sampled']['underbuild'] > 0
            or k['xlast']['mismatch'] + k['xlast']['underbuild'] > 0)


def mismatches(run):
    k = kinds(run)
    return (k['every']['least'] is not None or k['sampled']['mismatch'] > 0 or k['xlast']['mismatch'] > 0)


def short(run):
    """One line: every order, sampled, x-last."""
    if run is None:
        return 'not run'
    k = kinds(run)
    e = k['every']
    s = 'every order: '
    if e['least'] is not None:
        s += 'least %d (exact)' % e['least']
        if e['finished']:
            s += ', finished'
        else:
            s += ', search unfinished at %d births' % e['depth']
    elif e['finished']:
        if e['underbuild_orders'] and not e['match_orders']:
            s += 'every order underbuilds'
        elif e['underbuild_orders']:
            s += 'no mismatch; %d underbuilding orders' % e['underbuild_orders']
        else:
            s += 'every order matches'
        s += ' (%s keys, to %d births)' % (format(e['keys'], ','), e['depth'])
    else:
        s += 'no mismatch to %d births (%s keys, unfinished: %s)' % (e['depth'], format(e['keys'], ','), e['stopped'])
    sm, xl = k['sampled'], k['xlast']
    s += '; sampled %d match, %d mismatch, %d underbuild of %d' % (sm['match'], sm['mismatch'], sm['underbuild'],
                                                                    sum(sm.values()))
    s += '; x-last %d/%d/%d of %d' % (xl['match'], xl['mismatch'], xl['underbuild'], sum(xl.values()))
    ld = run.get('least_differing_order')
    if ld and e['least'] is None:
        s += '; least found %d' % ld['births']
    return s


def first_n(run, kind, n):
    """Counts over the first n seeds (sampled), for comparison with a disclosed count over seeds 0..n-1."""
    outs = run[kind]['orders'][:n]
    c = defaultdict(int)
    for o in outs:
        c[o['outcome']] += 1
    return dict(c)


# ============================================================================== replays of named orders

def replay(start, fam, r, law, order, name):
    ref = RF.RefData(C.start_stars(start), *fam, r)
    run = Runner(ref, L.make_law(ref, law))
    rows = run.listing([tuple(B) for B in order])
    out = {'name': name, 'start': start, 'law_family': list(fam), 'cutoff': r, 'law': law,
           'order_images': [list(B) for B in order], 'listing': rows}
    last = rows[-1] if rows else None
    out['ends'] = ('mismatch at birth %d' % last['birth']) if last and 'birth' in last and \
        last.get('matches_reference_knot') is None and last.get('allowed', True) else \
        ('not allowed at birth %d' % last['birth'] if last and last.get('allowed') is False else 'no mismatch')
    LIST.mkdir(parents=True, exist_ok=True)
    (LIST / (slug(name) + '.json')).write_text(json.dumps(out, indent=1, default=str) + '\n')
    return out


def named_replays():
    R3W = K.R3W
    res = []
    j = ['(0,1)', '(0,4)', '(0,7)', '(1,2)', '(1,5)', '(2,3)', '(2,6)', '(3,4)', '(4,5)', '(5,6)', '(6,7)']
    start_joins = [tuple(int(c) for c in s.strip('()').split(',')) for s in j]
    # reference ids of the round-1 knots of the cycle of eight: joins 19..29 in that order, offshoots 30 (of 3), 31 (of 7)
    res.append(replay('C8X3', R3W, 1, 'R2', start_joins + [(3,), (22, 23)],
                      'C8X3 R2: every start birth but member 7s offshoot, then the join of knots 22 and 23'))
    res.append(replay('C8X3', R3W, 1, 'R2', start_joins + [(7,), (19, 23)],
                      'C8X3 R2: the advisors order (every start birth but member 3s offshoot, then the join of 19 and 23)'))
    res.append(replay('C8X3', R3W, 1, 'R1', [(0, 1), (0, 4), (0, 7), (1, 2), (1, 5), (19,), (19,)],
                      'C8X3 R1: (0,1) (0,4) (0,7) (1,2) (1,5), then two offshoots of knot 19'))
    res.append(replay('D2(4,3)', R3W, 1, 'R1', [(0,), (0, 1), (0, 3), (1,), (1, 2), (8,), (8,)],
                      'D2(4,3) R1: (0,) (0,1) (0,3) (1,) (1,2), then two offshoots of knot 9'))
    res.append(replay('SCC', R3W, 1, 'R3', [(0,), (0,)], 'SCC R3: two offshoots of knot 0'))
    # R3 on the cycle of eight in the order of the R2 counterexample, for contrast
    res.append(replay('C8X3', R3W, 1, 'R3', start_joins + [(3,), (22, 23)],
                      'C8X3 R3: the R2 counterexample order (expected: the 13th birth is not allowed)'))
    res[1]['trace'] = trace_advisor_order(start_joins)
    (LIST / (slug(res[1]['name']) + '.json')).write_text(json.dumps(res[1], indent=1, default=str) + '\n')
    return res


def trace_advisor_order(start_joins):
    """The advisor's account of R2 on the cycle of eight, traced: after every start birth but member 3's offshoot,
    the brood's roster at birth read by the join of members 0 and 1, with the roster in which each member acts."""
    ref = RF.RefData(C.start_stars('C8X3'), *K.R3W, 1)
    law = L.BroodLaw(ref, 'R2')
    I = ref.start_mask
    for G in start_joins + [(7,)]:
        I |= 1 << ref.by_par[G][0]
    st = L.State(ref, I, 0)
    B, P = law.brood_of(st, ref.by_par[(0, 1)][0])
    pl = law.brood_plan(st, B, P)
    name = {}
    for x in L.bits(B):
        name[x] = 'join of members %s' % (ref.par[x],) if len(ref.par[x]) > 1 else 'offshoot of member %d' % ref.par[x][0]
    return {'brood': {str(x): name[x] for x in L.bits(B)},
            'member 3 still a member': bool((st.mem >> 3) & 1),
            'weaned': {str(x): st.weaned(x) for x in L.bits(B)},
            'roster in which each acts (0 = the brood roster itself, k = its k-th waiters roster)':
                {name[x]: pl.acting_level.get(x) for x in L.bits(B)},
            'planned joins': [[name[g] for g in G] + ['f=%d' % f] for G, f in sorted(pl.joins.items())],
            'join (19, 23) planned': (19, 23) in pl.joins}


# ============================================================================== reference facts cited by the pre-registration

def reference_facts():
    E = RF.E
    out = {}
    # groups of three or more in the rounds read by the reference, through round 6
    g3 = {}
    for (start, fam), cuts in sorted(K.gate_pairs().items()):
        S = E.from_stars(C.start_stars(start))
        law = RF.ref_law(*fam)
        rows = []
        for t in range(1, 7):
            S, rec = E.round_step(S, law)
            big = [g for g in rec['groups'] if len(g) >= 3]
            rows.append({'round': t, 'groups_3plus': len(big), 'largest': max((len(g) for g in rec['groups']), default=0)})
            if rec.get('stopped') or S.n_knots > 20000:
                break
        first = next((r['round'] for r in rows if r['groups_3plus']), None)
        g3['%s %s/%s' % (start, fam[0], fam[1])] = {'first_round_with_group_of_3plus': first, 'rows': rows}
    out['groups_of_three_in_reference_rounds_1_to_6'] = g3
    # the cycle of eight: the knot test, and shortness by round
    S = E.from_stars(C.start_stars('C8X3'))
    law = RF.ref_law(*K.R3W)
    kt = [E.parity_knot_test(S)['all_pass']]
    shorts = []
    for t in range(1, 6):
        S, rec = E.round_step(S, law)
        kt.append(E.parity_knot_test(S)['all_pass'])
        shorts.append({'round': t, 'births': rec['n_births'], 'short': rec['short']})
    out['C8X3_parity_knot_test_rounds_0_to_5'] = kt
    out['C8X3_short_by_round'] = shorts
    # extents of the round-1 brood (definitions, section 3), in the structure after round 1
    ext = {}
    for start in ('C8X3', 'D2(4,3)', 'D2(6,3)', 'D2(8,3)', 'D2(12,3)'):
        ref = RF.RefData(C.start_stars(start), *K.R3W, 1)
        I = 0
        for x in range(ref.N):
            if ref.born[x] <= 1:
                I |= 1 << x
        st = L.State(ref, I, 0)
        brood = [x for x in range(ref.N) if ref.born[x] == 1]
        parents = sorted({p for x in brood for p in ref.par[x]})
        targets = set(brood) | set(parents)

        def dist_from(x):
            d = {x: 0}
            fr = [x]
            while fr:
                nx = []
                for y in fr:
                    for z in L.bits(st.nbrs(y)):
                        if z not in d:
                            d[z] = d[y] + 1
                            nx.append(z)
                fr = nx
            return d
        per = {}
        for x in brood:
            d = dist_from(x)
            per[x] = max(d[t] for t in targets)
        e = {'greatest_extent': max(per.values()), 'least_extent': min(per.values())}
        if start == 'C8X3':
            j15 = ref.by_par[(1, 5)][0]
            e['extent_from_join_of_1_and_5'] = per[j15]
            e['join_of_1_and_5'] = j15
        ext[start] = e
    out['round1_brood_extents'] = ext
    return out


# ============================================================================== verdicts

def R(cid):
    """A run's result; where an extended search of the same run exists (`<id>__long`: the same search with a
    longer time budget, toward the registered key cap), that one is used and the registered line kept beside it."""
    x = load(cid + '__long')
    if x is not None:
        base = load(cid)
        x['_registered_line'] = short(base) if base else None
        return x
    return load(cid)


def long_runs():
    out = []
    for p in sorted(RUNS.glob('*__long.json')):
        x = json.loads(p.read_text())
        base_id = x['id'][:-len('__long')]
        base = load(base_id)
        e = x['every_order']
        out.append({'id': x['id'], 'command': x.get('command'), 'seconds_total': x['seconds'],
                    'peak_rss_mb': x['peak_rss_mb'], 'every_finished': e.get('finished'), 'stopped': e.get('stopped'),
                    'keys': e.get('keys'), 'searched_to_births': e.get('searched_to_births'),
                    'every_seconds': e.get('seconds'), 'line': short(x),
                    'registered_line': short(base) if base else None})
    return out


def verdicts():
    V = {}
    # ---------------------------------------------------------------- P1
    a = [R('D2(4,3)-R3W__r1__R2'), R('D2(4,3)-R3W__r1__R3')]
    b = [R('D2(4,3)-R3W-r3__R2'), R('D2(4,3)-R3W-r3__R3')]
    fa = [x for x in a if x is None or differs(x)]
    fb = []
    for x in b:
        if x is None:
            fb.append(x)
            continue
        k = kinds(x)
        if k['sampled']['mismatch'] + k['sampled']['underbuild'] + k['xlast']['mismatch'] + k['xlast']['underbuild']:
            fb.append(x)
    eo_b = [kinds(x)['every'] for x in b if x]
    v = 'holds' if not fa and not fb else 'fails'
    if v == 'holds' and any(e['least'] is not None for e in eo_b):
        v = 'holds (every order through round 3, not part of P1, shows a mismatch)'
    V['P1'] = {'verdict': v, 'numbers': {'R2 r1': short(a[0]), 'R3 r1': short(a[1]),
                                         'R2 r3': short(b[0]), 'R3 r3': short(b[1])}}
    # ---------------------------------------------------------------- P2
    rows = {}
    bad = []
    unfinished = []
    for st, cid in (('D2(5,3)', 'D2(5,3)-R3W__r1__'), ('Ring(5,3)', 'Ring(5,3)-R3W__r1__')):
        for law in ('R2', 'R3'):
            x = R(cid + law)
            rows['%s %s' % (st, law)] = short(x)
            if x is None or differs(x):
                bad.append('%s %s' % (st, law))
            elif not kinds(x)['every']['finished']:
                unfinished.append('%s %s' % (st, law))
    V['P2'] = {'verdict': 'fails' if bad else ('holds in part' if unfinished else 'holds'),
               'differs': bad, 'every_order_unfinished': unfinished, 'numbers': rows}
    # ---------------------------------------------------------------- P3
    rows = {}
    bad = []
    for st in ('D2(4,3)', 'D2(5,3)', 'Ring(5,3)', 'C8X3'):
        x = R('%s-R3W__r1__R1' % st)
        if x is None:
            bad.append(st + ' not run')
            continue
        e = kinds(x)['every']
        ws = x.get('least_mismatches_waiter_surplus', [])
        rows[st] = {'least': e['least'], 'exact': e['least'] is not None,
                    'least_mismatches_all_waiter_surplus_offshoots': bool(ws) and all(ws),
                    'n_least_mismatch_edges_recorded': len(ws), 'line': short(x)}
        if e['least'] != 7 or not (ws and all(ws)):
            bad.append(st)
    V['P3'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}
    # ---------------------------------------------------------------- P4
    rows = {}
    bad = []
    for n, cid in ((4, 'D2(4,3)-R3W__r1__R3L'), (5, 'D2(5,3)-R3W__r1__R3L'), (6, 'D2(6,3)-R3W__r1__R3L')):
        x = R(cid)
        least = kinds(x)['every']['least'] if x else None
        exact = least is not None
        if x and least is None and x.get('least_differing_order'):
            least = x['least_differing_order']['births']
        rows['n=%d' % n] = {'predicted': 2 * n + 4, 'least': least, 'exact': exact, 'line': short(x)}
        if least != 2 * n + 4:
            bad.append(n)
    V['P4'] = {'verdict': 'fails' if bad else 'holds', 'fails_at_n': bad, 'numbers': rows}
    # ---------------------------------------------------------------- P5
    rows = {}
    bad = []
    unf = []
    for row, cuts in (('TWO-KNOT-F1R', (2, 3)), ('THREE-KNOT-F1R', (2, 3)), ('THREE-KNOT-F1O', (2, 3)),
                      ('TWO-KNOT-F1O', (2, 3))):
        for r in cuts:
            for law in ('R1', 'R2', 'R3'):
                x = R('%s__r%d__%s' % (row, r, law))
                key = '%s r%d %s' % (row, r, law)
                rows[key] = short(x)
                if x is None or differs(x):
                    bad.append(key)
                elif not kinds(x)['every']['finished']:
                    unf.append(key)
    extra = {}
    for row in ('TWO-KNOT-F1R', 'THREE-KNOT-F1R', 'THREE-KNOT-F1O', 'TWO-KNOT-F1O'):
        for law in ('R1', 'R2', 'R3'):
            extra['%s r4 %s' % (row, law)] = short(R('%s__r4__%s' % (row, law)))
    V['P5'] = {'verdict': 'fails' if bad else ('holds in part' if unf else 'holds'), 'differs': bad,
               'every_order_unfinished': unf, 'numbers': rows, 'cutoff_4_not_in_P5': extra}
    # ---------------------------------------------------------------- P6
    want = [('TWO-KNOT-F1R__r2__R3L', 3), ('TWO-KNOT-F1O__r2__R3L', 3), ('Ring(5,3)-R3W__r1__R3L', 3),
            ('THREE-KNOT-F1O__r2__R3L', 6), ('C8X3-R3W__r1__R3L', 17)]
    rows = {}
    bad = []
    for cid, n in want:
        x = R(cid)
        least = kinds(x)['every']['least'] if x else None
        rows[cid] = {'predicted': n, 'least': least, 'line': short(x)}
        if least != n:
            bad.append(cid)
    for r in (3, 4):
        for row in ('TWO-KNOT-F1R', 'TWO-KNOT-F1O', 'THREE-KNOT-F1O'):
            x = R('%s__r%d__R3L' % (row, r))
            rows['%s__r%d__R3L (other cutoff, reported)' % (row, r)] = short(x)
    x = R('THREE-KNOT-F1R__r2__R3L')
    rows['THREE-KNOT-F1R__r2__R3L (predicted: no difference)'] = short(x)
    if x is None or differs(x):
        bad.append('THREE-KNOT-F1R__r2__R3L')
    for r in (3, 4):
        rows['THREE-KNOT-F1R__r%d__R3L (reported)' % r] = short(R('THREE-KNOT-F1R__r%d__R3L' % r))
    V['P6'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}
    # ---------------------------------------------------------------- P7
    rows = {}
    bad = []
    unf = []
    closing = {}
    for row, r in (('D2(4,3)-ORD', 2), ('Ring(5,3)-ORD', 2), ('TWO-KNOT-ORD', 3), ('LONE-FOUR-ORD', 4)):
        for law in ('R1', 'R2', 'R3'):
            x = R('%s__r%d__%s' % (row, r, law))
            key = '%s r%d %s' % (row, r, law)
            rows[key] = short(x)
            if x is None or differs(x):
                bad.append(key)
            elif not kinds(x)['every']['finished']:
                unf.append(key)
            if x:
                cb = x['closing_bit']
                closing[key] = cb
                if cb['every_order_firings'] != cb['every_order_matched_received_none'] or \
                        cb['sampled_and_xlast_firings'] != cb['sampled_and_xlast_matched_received_none']:
                    bad.append(key + ' (closing bit)')
                if row == 'LONE-FOUR-ORD' and (cb['every_order_firings'] == 0 or cb['sampled_and_xlast_firings'] == 0):
                    bad.append(key + ' (closing bit never fired)')
    V['P7'] = {'verdict': 'fails' if bad else ('holds in part' if unf else 'holds'), 'differs': bad,
               'every_order_unfinished': unf, 'numbers': rows,
               'closing_bit': {k: {kk: v[kk] for kk in ('every_order_firings', 'every_order_matched_received_none',
                                                       'sampled_and_xlast_firings',
                                                       'sampled_and_xlast_matched_received_none',
                                                       'reference_closing_knots')} for k, v in closing.items()}}
    # ---------------------------------------------------------------- P8
    rows = {}
    bad = []
    for law in ('R1', 'R2', 'R3', 'R3L', 'R0'):
        x = R('SCC-R3W__r1__' + law)
        e = kinds(x)['every'] if x else {}
        rows[law] = {'least': e.get('least'), 'line': short(x)}
        if e.get('least') != 2:
            bad.append(law)
    x = R('SCC-R3W__r1__CONTROL')
    k = kinds(x) if x else None
    ctrl_ok = k is not None and k['every']['least'] is None and k['every']['match_orders'] == 0 and \
        k['every']['underbuild_orders'] > 0 and k['sampled']['mismatch'] == 0 and k['xlast']['mismatch'] == 0 and \
        k['sampled']['match'] == 0 and k['xlast']['match'] == 0
    rows['CONTROL'] = short(x)
    if not ctrl_ok:
        bad.append('CONTROL')
    V['P8'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}
    # ---------------------------------------------------------------- P9
    first = {}
    bad1 = []
    for row, r in (('D2(4,3)-R3W', 1), ('D2(5,3)-R3W', 1), ('Ring(5,3)-R3W', 1), ('Ring(5,3)-R3W', 2),
                   ('C8X3-R3W', 1), ('SCC-R3W', 1)):
        x = R('%s__r%d__CONTROL' % (row, r))
        first['%s r%d' % (row, r)] = short(x)
        if x is None:
            bad1.append(row)
            continue
        k = kinds(x)
        if k['every']['match_orders'] or k['every']['least'] is not None or k['sampled']['match'] or \
                k['xlast']['match'] or k['sampled']['mismatch'] or k['xlast']['mismatch']:
            bad1.append('%s r%d' % (row, r))
    second = {}
    bad2 = []
    unf2 = []
    for row, start, fam, cuts in K.TABLE:
        if fam == K.R3W:
            continue
        for r in cuts:
            x = R('%s__r%d__CONTROL' % (row, r))
            second['%s r%d' % (row, r)] = short(x)
            if x is None or differs(x):
                bad2.append('%s r%d' % (row, r))
            elif not kinds(x)['every']['finished']:
                unf2.append('%s r%d' % (row, r))
    v = 'fails' if bad2 else ('holds in part' if unf2 else 'holds')
    V['P9'] = {'verdict': v, 'first_half_check': 'holds' if not bad1 else 'fails on %s' % bad1,
               'second_half_differs': bad2, 'second_half_unfinished': unf2,
               'numbers': {'first half': first, 'second half': second}}
    # ---------------------------------------------------------------- P10
    rows = {}
    bad = []
    outside = []
    for row, start, fam, cuts in K.TABLE:
        for r in cuts:
            x = R('%s__r%d__R0' % (row, r))
            e = kinds(x)['every'] if x else {}
            rows['%s r%d' % (row, r)] = {'least': e.get('least'), 'line': short(x)}
            if x is None or not mismatches(x):
                bad.append('%s r%d' % (row, r))
            elif e.get('least') is None or not 1 <= e['least'] <= 3:
                outside.append('%s r%d' % (row, r))
    V['P10'] = {'verdict': 'fails' if bad else ('holds in part' if outside else 'holds'),
                'matches_on': bad, 'least_outside_1_to_3': outside, 'numbers': rows}
    # ---------------------------------------------------------------- P11
    td = {}
    bad = []
    for start in K.TD_STARTS:
        per_d = {}
        least = {'every': None, 'sampled': None, 'xlast': None, 'all kinds': None}
        for d in K.TD_DS:
            x = R('TD-%s__r1__T(%d)' % (start, d))
            if x is None:
                per_d[d] = 'not run'
                continue
            k = kinds(x)
            e = k['every']
            no_mm = {'every': e['least'] is None, 'sampled': k['sampled']['mismatch'] == 0,
                     'xlast': k['xlast']['mismatch'] == 0}
            no_mm['all kinds'] = all(no_mm.values())
            for kk, val in no_mm.items():
                if val and least[kk] is None:
                    least[kk] = d
            per_d[d] = {'line': short(x), 'no_mismatch': no_mm, 'every_finished': e['finished'],
                        'every_depth': e['depth'], 'every_least': e['least'],
                        'underbuild_any': e['underbuild_orders'] > 0 or k['sampled']['underbuild'] > 0 or
                        k['xlast']['underbuild'] > 0}
        td[start] = {'least_d_with_no_mismatch': least, 'per_d': per_d}
        if start.startswith('D2'):
            if least['all kinds'] != 4:
                bad.append('%s: least d %s' % (start, least['all kinds']))
        else:
            for d in (2, 3, 4, 5):
                pd = per_d.get(d)
                if isinstance(pd, dict) and pd['no_mismatch']['all kinds']:
                    bad.append('%s: d = %d has no mismatch' % (start, d))
    V['P11'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': td}
    # ---------------------------------------------------------------- P12
    rows = {}
    bad = []
    for row, r in (('D2(4,3)-ORD', 2), ('Ring(5,3)-ORD', 2), ('TWO-KNOT-ORD', 3), ('LONE-FOUR-ORD', 4)):
        for law in ('R1', 'R2', 'R3', 'R3L'):
            x = R('%s__r%d__%s' % (row, r, law))
            if x is None:
                continue
            seen = x['brood_roster_with_short_member']['seen']
            rows['%s r%d %s' % (row, r, law)] = seen
            if seen:
                bad.append('%s r%d %s' % (row, r, law))
    V['P12'] = {'verdict': 'fails' if bad else 'holds (a check)', 'fails_on': bad,
                'brood_roster_with_short_member_seen': rows}
    # ---------------------------------------------------------------- P13
    rows = {}
    for cid, start, fam, r, law, cap, budget in configs():
        if fam not in (K.F1R, K.F1O) or law not in ('R1', 'R2', 'R3', 'R3L', 'R0', 'CONTROL'):
            continue
        x = R(cid)
        if x is None:
            continue
        rows[cid] = {'group_of_three_or_more': x['group_of_three_or_more']['seen'],
                     'where': x['group_of_three_or_more']['first_where'], 'differs': differs(x),
                     'line': short(x) if law == 'R1' else None}
    with_big = sorted({cid.split('__')[0] for cid, v in rows.items() if v['group_of_three_or_more']})
    r1_there = {cid: v['line'] for cid, v in rows.items() if cid.endswith('__R1') and v['group_of_three_or_more']}
    V['P13'] = {'verdict': 'open (reported without a prediction)', 'rows_with_a_group_of_three': with_big,
                'R1_where_a_roster_read_has_a_group_of_three': r1_there, 'numbers': rows}
    # ---------------------------------------------------------------- P14
    x2 = R('C8X3-R3W__r1__R2')
    x3 = R('C8X3-R3W__r1__R3')
    e2 = kinds(x2)['every'] if x2 else {}
    bad = []
    if x2 is None or not mismatches(x2):
        bad.append('R2 matches in every order')
    if e2.get('least') != 13:
        bad.append('R2 least %s' % e2.get('least'))
    if x3 is None or differs(x3):
        bad.append('R3 differs')
    unf = x3 is not None and not kinds(x3)['every']['finished']
    V['P14'] = {'verdict': 'fails' if bad else ('holds in part' if unf else 'holds'), 'fails_on': bad,
                'R3_every_order_unfinished': unf, 'numbers': {'R2': short(x2), 'R3': short(x3)}}
    return V


# ============================================================================== disclosed numbers

DISCLOSED = {
    # (row, cutoff, law): (disclosed text, least n or 'match' or 'underbuild' for every order, or None)
    ('D2(4,3)-R3W', 1, 'R1'): ('differs: 67,353 keys, 1,332 mismatches; least 7', 7),
    ('D2(4,3)-R3W', 1, 'R2'): ('every order matches (65,803 keys)', 'match'),
    ('D2(4,3)-R3W', 1, 'R3'): ('every order matches (65,791 keys)', 'match'),
    ('D2(4,3)-R3W', 1, 'R3L'): ('differs: 32 mismatches; least 12', 12),
    ('D2(4,3)-R3W', 1, 'R0'): ('every order ends in a mismatch or underbuilds; least 3', 3),
    ('D2(4,3)-R3W', 1, 'CONTROL'): ('every order underbuilds, ending after 20 births', 'underbuild'),
    ('D2(5,3)-R3W', 1, 'R1'): ('least 7; 30 of 60 sampled and 19 of 20 x-last differ', 7),
    ('D2(5,3)-R3W', 1, 'R2'): ('60 of 60 sampled and 20 of 20 x-last match', None),
    ('D2(5,3)-R3W', 1, 'R3'): ('as R2', None),
    ('D2(5,3)-R3W', 1, 'R3L'): ('least 14; 60 of 60 sampled match', 14),
    ('D2(5,3)-R3W', 1, 'R0'): ('least 3', 3),
    ('D2(5,3)-R3W', 1, 'CONTROL'): ('60 of 60 underbuild', None),
    ('Ring(5,3)-R3W', 1, 'R1'): ('least 7; 15 of 40 sampled (round 2) and 7 of 15 x-last differ', 7),
    ('Ring(5,3)-R3W', 1, 'R2'): ('40 of 40 sampled (round 2) and 15 of 15 x-last match', None),
    ('Ring(5,3)-R3W', 1, 'R3'): ('as R2', None),
    ('Ring(5,3)-R3W', 1, 'R3L'): ('least 3; 39 of 40 differ', 3),
    ('Ring(5,3)-R3W', 1, 'R0'): ('least 2', 2),
    ('Ring(5,3)-R3W', 1, 'CONTROL'): ('40 of 40 underbuild', None),
    ('C8X3-R3W', 1, 'R1'): ('least 7', 7),
    ('C8X3-R3W', 1, 'R2'): ('least 13 (8,435 keys); 27 of 200 sampled and 2 of 32 x-last differ', 13),
    ('C8X3-R3W', 1, 'R3'): ('no mismatch in any order up to 18 births (318,780 keys, unfinished); 200 of 200 sampled and '
                            '32 of 32 x-last match', None),
    ('C8X3-R3W', 1, 'R3L'): ('least 17', 17),
    ('C8X3-R3W', 1, 'R0'): ('least 3', 3),
    ('C8X3-R3W', 1, 'CONTROL'): ('no mismatch in any order (8,206 keys); 200 of 200 underbuild', 'underbuild'),
    ('TWO-KNOT-F1R', 2, 'R1'): ('every order matches (517 keys)', 'match'),
    ('TWO-KNOT-F1R', 3, 'R1'): ('every order matches (17,403 keys)', 'match'),
    ('TWO-KNOT-F1R', 4, 'R1'): ('40 of 40 sampled', None),
    ('TWO-KNOT-F1R', 2, 'R2'): ('every order matches (357)', 'match'),
    ('TWO-KNOT-F1R', 3, 'R2'): ('every order matches (16,435)', 'match'),
    ('TWO-KNOT-F1R', 2, 'R3'): ('as R2', 'match'),
    ('TWO-KNOT-F1R', 3, 'R3'): ('as R2', 'match'),
    ('TWO-KNOT-F1R', 2, 'R3L'): ('differs: least 3; 26 of 40 differ', 3),
    ('TWO-KNOT-F1R', 2, 'R0'): ('least 2', 2),
    ('TWO-KNOT-F1R', 2, 'CONTROL'): ('every order matches (152)', 'match'),
    ('TWO-KNOT-F1R', 3, 'CONTROL'): ('every order matches (4,247)', 'match'),
    ('TWO-KNOT-F1O', 2, 'R1'): ('every order to round 2 (841)', 'match'),
    ('TWO-KNOT-F1O', 3, 'R1'): ('round 3: no mismatch in 95,621 keys, unfinished at 35 s', None),
    ('TWO-KNOT-F1O', 2, 'R2'): ('every order to round 2 (729)', 'match'),
    ('TWO-KNOT-F1O', 3, 'R2'): ('round 3: none in 90,554, unfinished', None),
    ('TWO-KNOT-F1O', 2, 'R3'): ('as R2', 'match'),
    ('TWO-KNOT-F1O', 3, 'R3'): ('as R2 (92,858, unfinished)', None),
    ('TWO-KNOT-F1O', 2, 'R3L'): ('least 3; 31 of 40 differ', 3),
    ('TWO-KNOT-F1O', 2, 'R0'): ('least 2', 2),
    ('TWO-KNOT-F1O', 3, 'CONTROL'): ('every order to round 3 matches (37,258 keys)', 'match'),
    ('THREE-KNOT-F1R', 2, 'R1'): ('every order matches (128)', 'match'),
    ('THREE-KNOT-F1R', 3, 'R1'): ('every order matches (528)', 'match'),
    ('THREE-KNOT-F1R', 2, 'R2'): ('every order matches (124)', 'match'),
    ('THREE-KNOT-F1R', 3, 'R2'): ('every order matches (364)', 'match'),
    ('THREE-KNOT-F1R', 2, 'R3'): ('as R2', 'match'),
    ('THREE-KNOT-F1R', 3, 'R3'): ('as R2', 'match'),
    ('THREE-KNOT-F1R', 2, 'R3L'): ('every order to round 2 matches (124)', 'match'),
    ('THREE-KNOT-F1R', 2, 'R0'): ('least 2 (a wrong retirement)', 2),
    ('THREE-KNOT-F1R', 2, 'CONTROL'): ('every order matches (79)', 'match'),
    ('THREE-KNOT-F1R', 3, 'CONTROL'): ('every order matches (159)', 'match'),
    ('THREE-KNOT-F1O', 2, 'R1'): ('every order matches (409)', 'match'),
    ('THREE-KNOT-F1O', 3, 'R1'): ('every order matches (9,260)', 'match'),
    ('THREE-KNOT-F1O', 2, 'R2'): ('every order matches (407)', 'match'),
    ('THREE-KNOT-F1O', 3, 'R2'): ('every order matches (8,026)', 'match'),
    ('THREE-KNOT-F1O', 2, 'R3'): ('as R2', 'match'),
    ('THREE-KNOT-F1O', 3, 'R3'): ('as R2', 'match'),
    ('THREE-KNOT-F1O', 2, 'R3L'): ('differs: least 6; 13 of 40 differ', 6),
    ('THREE-KNOT-F1O', 2, 'R0'): ('least 3', 3),
    ('THREE-KNOT-F1O', 2, 'CONTROL'): ('every order matches (216)', 'match'),
    ('THREE-KNOT-F1O', 3, 'CONTROL'): ('every order matches (2,807)', 'match'),
    ('TWO-KNOT-ORD', 3, 'R1'): ('every order matches (4,624)', 'match'),
    ('TWO-KNOT-ORD', 3, 'R2'): ('every order matches (3,364)', 'match'),
    ('TWO-KNOT-ORD', 3, 'R3'): ('every order matches (3,136)', 'match'),
    ('TWO-KNOT-ORD', 3, 'R0'): ('least 2', 2),
    ('TWO-KNOT-ORD', 3, 'CONTROL'): ('every order matches (1,350)', 'match'),
    ('LONE-FOUR-ORD', 4, 'R1'): ('every order matches (84)', 'match'),
    ('LONE-FOUR-ORD', 4, 'R2'): ('every order matches (84)', 'match'),
    ('LONE-FOUR-ORD', 4, 'R3'): ('every order matches (84)', 'match'),
    ('LONE-FOUR-ORD', 4, 'R0'): ('least 1', 1),
    ('LONE-FOUR-ORD', 4, 'CONTROL'): ('every order matches (84)', 'match'),
    ('D2(4,3)-ORD', 2, 'R1'): ('30 of 30', None),
    ('D2(4,3)-ORD', 2, 'R2'): ('30 of 30', None),
    ('D2(4,3)-ORD', 2, 'R3'): ('30 of 30', None),
    ('D2(4,3)-ORD', 2, 'R0'): ('30 of 30 differ; least 1', 1),
    ('D2(4,3)-ORD', 2, 'CONTROL'): ('30 of 30', None),
    ('Ring(5,3)-ORD', 2, 'R1'): ('30 of 30', None),
    ('Ring(5,3)-ORD', 2, 'R2'): ('30 of 30', None),
    ('Ring(5,3)-ORD', 2, 'R3'): ('30 of 30', None),
    ('Ring(5,3)-ORD', 2, 'R0'): ('30 of 30 differ; least 1', 1),
    ('Ring(5,3)-ORD', 2, 'CONTROL'): ('30 of 30', None),
    ('SCC-R3W', 1, 'R1'): ('least 2', 2),
    ('SCC-R3W', 1, 'R2'): ('least 2', 2),
    ('SCC-R3W', 1, 'R3'): ('least 2', 2),
    ('SCC-R3W', 1, 'R3L'): ('least 2', 2),
    ('SCC-R3W', 1, 'R0'): ('least 2', 2),
    ('SCC-R3W', 1, 'CONTROL'): ('underbuilds (216 keys)', 'underbuild'),
}

TD_DISCLOSED = {
    'D2(4,3)': {2: 7, 3: 10, 4: 'match', 5: 'match'},
    'D2(6,3)': {2: 11, 3: 11, 4: 'match', 5: 'match'},
    'D2(8,3)': {2: 14, 3: 17, 4: 'match', 5: 'match'},
    'D2(12,3)': {2: 24, 3: 25, 4: 'match', 5: 'match'},
    'C8X3': {2: 10, 3: 14, 4: 14, 5: 14, 6: 'match'},
}


def compare_disclosed():
    rows = []
    diffs = []
    for (row, r, law), (text, val) in DISCLOSED.items():
        x = R('%s__r%d__%s' % (row, r, law))
        mine = short(x)
        flag = None
        if x is not None and val is not None:
            e = kinds(x)['every']
            if isinstance(val, int):
                least = e['least']
                if least is None and x.get('least_differing_order'):
                    least = x['least_differing_order']['births']
                if least != val:
                    flag = 'least %s, disclosed %d' % (least, val)
            elif val == 'match':
                if differs(x):
                    flag = 'differs, disclosed every order matches'
            elif val == 'underbuild':
                if e['least'] is not None or e['match_orders']:
                    flag = 'not every order underbuilds'
        if x is not None and val is None:
            # verdict-level comparison of sampled statements
            k = kinds(x)
            if ('match' in text and 'differ' not in text and 'underbuild' not in text) and differs(x):
                flag = 'an order differs, disclosed: %s' % text
            if 'underbuild' in text and (k['sampled']['match'] or k['sampled']['mismatch']):
                flag = 'a sampled order does not underbuild'
        firstM = {}
        if x is not None:
            import re
            for m in re.finditer(r'(\d+) of (\d+)( sampled)?', text):
                M = int(m.group(2))
                if M <= 200 and 'x-last' not in text[m.end():m.end() + 8]:
                    firstM['sampled seeds 0-%d' % (M - 1)] = first_n(x, 'sampled', M)
            firstM['x-last'] = x['xlast']['counts']
        rows.append({'row': row, 'cutoff': r, 'law': law, 'disclosed': text, 'found': mine, 'difference': flag,
                     'found_over_disclosed_seed_ranges': firstM})
        if flag:
            diffs.append(rows[-1])
            if x is not None:
                LIST.mkdir(parents=True, exist_ok=True)
                (LIST / ('difference_%s.json' % slug('%s__r%d__%s' % (row, r, law)))).write_text(json.dumps(
                    {'run': '%s__r%d__%s' % (row, r, law), 'disclosed': text, 'difference': flag,
                     'least_differing_order': x.get('least_differing_order'),
                     'mismatching_sampled_orders': [o for o in x['sampled']['orders'] if o['outcome'] != 'match'][:5],
                     'mismatching_xlast_orders': [o for o in x['xlast']['orders'] if o['outcome'] != 'match'][:5]},
                    indent=1, default=str) + '\n')
    td = []
    for start, per in TD_DISCLOSED.items():
        for d, val in per.items():
            x = R('TD-%s__r1__T(%d)' % (start, d))
            mine = short(x)
            flag = None
            if x is not None:
                e = kinds(x)['every']
                least = e['least']
                if least is None and x.get('least_differing_order'):
                    least = x['least_differing_order']['births']
                if isinstance(val, int) and least != val:
                    flag = 'least %s, disclosed %d' % (least, val)
                if val == 'match' and mismatches(x):
                    flag = 'a mismatch, disclosed none'
            td.append({'start': start, 'd': d, 'disclosed': val, 'found': mine, 'difference': flag})
            if flag:
                diffs.append(td[-1])
                LIST.mkdir(parents=True, exist_ok=True)
                (LIST / ('difference_%s.json' % slug('TD-%s__r1__T(%d)' % (start, d)))).write_text(json.dumps(
                    {'run': 'TD-%s__r1__T(%d)' % (start, d), 'disclosed': val, 'difference': flag,
                     'least_differing_order': x.get('least_differing_order')}, indent=1, default=str) + '\n')
    # beyond the first table (sampled, with R1, R2 and R3 only)
    beyond = [('D2(4,3)-R3W-r3__R1', 'R1 differs in 20 of 40 sampled (least 9 found)', 9),
              ('D2(4,3)-R3W-r3__R2', 'R2 matches in 40 of 40 sampled', 'match-sampled'),
              ('D2(4,3)-R3W-r3__R3', 'R3 matches in 40 of 40 sampled', 'match-sampled')]
    for row in ('Ring(5,3)-F1R-r3', 'Ring(5,3)-F1O-r3', 'GEN7-F1R-r3', 'GEN7-F1O-r3'):
        for law in ('R1', 'R2', 'R3'):
            beyond.append(('%s__%s' % (row, law), 'matches in 40 of 40 sampled', 'match-sampled'))
    for cid, text, val in beyond:
        x = R(cid)
        flag = None
        if x is not None:
            k = kinds(x)
            if val == 'match-sampled' and (k['sampled']['mismatch'] + k['sampled']['underbuild']):
                flag = 'a sampled order differs'
            if isinstance(val, int):
                least = k['every']['least']
                if least != val:
                    flag = 'least %s (%s), disclosed %d found' % (least, 'exact' if least is not None else 'none', val)
        rows.append({'row': cid, 'cutoff': 3, 'law': cid.split('__')[1], 'disclosed': text, 'found': short(x),
                     'difference': flag,
                     'found_over_disclosed_seed_ranges': {'sampled seeds 0-39': first_n(x, 'sampled', 40)} if x else {}})
        if flag:
            diffs.append(rows[-1])
            LIST.mkdir(parents=True, exist_ok=True)
            (LIST / ('difference_%s.json' % slug(cid))).write_text(json.dumps(
                {'run': cid, 'disclosed': text, 'difference': flag,
                 'least_differing_order': x.get('least_differing_order'),
                 'least_found_in_sampled_orders': x['sampled'].get('least_found')}, indent=1, default=str) + '\n')
    return rows, td, diffs


# ============================================================================== long runs and the table of runs

def run_table():
    out = []
    for c in configs():
        cid = c[0]
        x = load(cid)          # the registered run; extended searches are listed separately
        if x is None:
            out.append({'id': cid, 'status': 'not run'})
            continue
        e = x['every_order']
        out.append({'id': cid, 'command': x.get('command'), 'seconds_total': x['seconds'],
                    'peak_rss_mb': x['peak_rss_mb'], 'every_finished': e.get('finished'), 'stopped': e.get('stopped'),
                    'keys': e.get('keys'), 'searched_to_births': e.get('searched_to_births'),
                    'least_n': e.get('least_n'), 'every_seconds': e.get('seconds'), 'line': short(x),
                    'births_within_r': x['reference']['births_within_r'], 'R': x['reference']['R']})
    return out


def write_md(V, facts, rows, td, diffs, table, replays):
    L_ = []
    a = L_.append
    a('# LOCAL-ROUND-20261123-001A-E001: summary')
    a('')
    a('Generated by `lr_summarize.py` from `runs/*.json`. "Every order": breadth-first over memo keys (LR section 4);')
    a('"sampled": seeds 0 to 199, a uniform choice among the allowed parent sets at each step; "x-last": one order per')
    a('knot that exists by round 1 of the reference, seed 0. Counts of sampled orders are counts under that uniform')
    a('choice only. Readings are in `deviations.md` of the experiment family.')
    a('')
    a('## Predictions')
    a('')
    a('| Prediction | Verdict | Numbers |')
    a('| --- | --- | --- |')
    for p in ['P%d' % i for i in range(1, 15)]:
        v = V[p]
        nums = v.get('numbers', {})
        if p == 'P11':
            txt = '; '.join('%s: least d with no mismatch %s (every order %s, sampled %s, x-last %s)' % (
                s, d['least_d_with_no_mismatch']['all kinds'], d['least_d_with_no_mismatch']['every'],
                d['least_d_with_no_mismatch']['sampled'], d['least_d_with_no_mismatch']['xlast'])
                for s, d in nums.items())
        elif p == 'P13':
            txt = 'rows with a roster read holding a group of three or more: %s; R1 there: %s' % (
                v['rows_with_a_group_of_three'], '; '.join('%s: %s' % kv for kv in v['R1_where_a_roster_read_has_a_group_of_three'].items()))
        elif p == 'P12':
            txt = 'brood roster at birth with a short member, in any ORD run: %s' % (
                'none' if not v['fails_on'] else v['fails_on'])
        else:
            parts = []
            for k, val in nums.items():
                if isinstance(val, dict):
                    if 'line' in val:
                        parts.append('%s: %s' % (k, val['line']))
                    else:
                        parts.append('%s: %s' % (k, '; '.join('%s: %s' % kv for kv in val.items())))
                else:
                    parts.append('%s: %s' % (k, val))
            txt = ' · '.join(parts)
        extra = ''
        for key in ('fails_on', 'differs', 'every_order_unfinished', 'fails_at_n', 'first_half_check',
                    'second_half_differs', 'second_half_unfinished', 'matches_on', 'least_outside_1_to_3'):
            if key in v and v[key]:
                extra += ' [%s: %s]' % (key.replace('_', ' '), v[key])
        a('| %s | %s%s | %s |' % (p, v['verdict'], extra, txt.replace('|', '/')))
    a('')
    a('## Differences from the numbers disclosed before the freeze')
    a('')
    if not diffs:
        a('None in least numbers of births or verdicts.')
    for d in diffs:
        a('- %s' % json.dumps(d, default=str))
    a('')
    a('## Counts of x-last orders that differ from the disclosed counts')
    a('')
    a('An x-last order is one order per knot, drawn with seed 0; the generator and the enumeration of allowed births')
    a('(deviations.md items 8 and 17) are this engine\'s, so the orders are not the prototype\'s. Each differing order')
    a('of mine is listed birth by birth in the file named.')
    a('')
    for t in xlast_listings():
        a('- `%s`: disclosed %s; mine %s; every mismatch a waiter\'s surplus offshoot: %s; `%s`.' % (
            t['run'], t['disclosed'], t['mine'], t['all_mismatches_are_waiter_surplus_offshoots'], t['listing_file']))
    a('')
    a('## Named orders replayed birth by birth (listings in `listings/`)')
    a('')
    for r in replays:
        a('- %s: %s.' % (r['name'], r['ends']))
    a('')
    a('## Every run')
    a('')
    a('| Run | R | births within r | result | every-order s | total s | peak MB |')
    a('| --- | --- | --- | --- | --- | --- | --- |')
    for t in table:
        if t.get('status') == 'not run':
            a('| %s | | | not run | | | |' % t['id'])
            continue
        a('| %s | %s | %s | %s | %s | %s | %s |' % (t['id'], t['R'], t['births_within_r'], t['line'],
                                                   t['every_seconds'], t['seconds_total'], t['peak_rss_mb']))
    a('')
    a('## Extended searches (the same search with a 1,500 s budget, toward the registered key cap)')
    a('')
    a('These ran longer than ten minutes, in the background; their results are used for the verdicts above.')
    a('')
    for t in long_runs():
        a('- `%s`: %s (registered run: %s); %s s, peak %s MB. Command: `%s`' % (
            t['id'], t['line'], t['registered_line'], t['seconds_total'], t['peak_rss_mb'], t['command']))
    a('')
    a('## Disclosed and found, every cell')
    a('')
    a('| Row | r | Law | Disclosed | Found |')
    a('| --- | --- | --- | --- | --- |')
    for r in rows:
        a('| %s | %s | %s | %s | %s |' % (r['row'], r['cutoff'], r['law'], r['disclosed'], r['found']))
    for r in td:
        a('| TD %s | 1 | T(%d) | %s | %s |' % (r['start'], r['d'], r['disclosed'], r['found']))
    a('')
    a('## Reference facts cited by the pre-registration')
    a('')
    a('- Knot test (parity, both methods) on the cycle of eight with three extra dead knots, start and rounds 1-5: %s.'
      % facts['C8X3_parity_knot_test_rounds_0_to_5'])
    a('- Its short members by round: %s.' % '; '.join('round %d: %d births, short %s' % (s['round'], s['births'], s['short'])
                                                     for s in facts['C8X3_short_by_round'][:4]))
    a('- Extents of the round-1 brood (after round 1): %s.' % json.dumps(facts['round1_brood_extents']))
    a('- First round with a group of three or more in the reference, rounds 1-6: %s.' % '; '.join(
        '%s: %s' % (k, v['first_round_with_group_of_3plus']) for k, v in facts['groups_of_three_in_reference_rounds_1_to_6'].items()))
    (ART / 'summary.md').write_text('\n'.join(L_) + '\n')


XLAST_COUNT_DIFFS = [
    # (run, disclosed x-last count): the disclosed count of x-last orders that differ, where mine is not equal
    ('D2(5,3)-R3W__r1__R1', '19 of 20 x-last differ'),
    ('Ring(5,3)-R3W__r1__R1', '7 of 15 x-last differ'),
    ('Ring(5,3)-R3W__r2__R1', '7 of 15 x-last differ'),
]


def xlast_listings():
    """Birth-by-birth listings of every x-last order of mine that differs, on the rows whose disclosed x-last count
    differs from mine (the pre-registration's rule for disagreements)."""
    out = []
    for cid, text in XLAST_COUNT_DIFFS:
        x = load(cid)
        if x is None:
            continue
        ref = RF.RefData(C.start_stars(x['start']), *x['law_family'], x['cutoff'])
        run = Runner(ref, L.make_law(ref, x['law']))
        orders = []
        for o in x['xlast']['orders']:
            if o['outcome'] == 'match':
                continue
            order = [tuple(e[1]) for e in o['events'] if e[0] == 'birth']
            orders.append({'x': o['x'], 'outcome': o['outcome'], 'births': o['births'],
                           'waiter_surplus_offshoot': o.get('waiter_surplus_offshoot'), 'listing': run.listing(order)})
        rec = {'run': cid, 'disclosed': text, 'mine': x['xlast']['counts'], 'differing_xlast_orders': orders}
        LIST.mkdir(parents=True, exist_ok=True)
        (LIST / ('xlast_%s.json' % slug(cid))).write_text(json.dumps(rec, indent=1, default=str) + '\n')
        out.append({'run': cid, 'disclosed': text, 'mine': x['xlast']['counts'],
                    'all_mismatches_are_waiter_surplus_offshoots': all(o['waiter_surplus_offshoot'] for o in orders
                                                                       if o['outcome'] == 'mismatch'),
                    'listing_file': 'listings/xlast_%s.json' % slug(cid)})
    return out


def main():
    V = verdicts()
    facts = reference_facts()
    rows, td, diffs = compare_disclosed()
    table = run_table()
    replays = named_replays()
    summ = {'predictions': V, 'differences_from_disclosed': diffs, 'disclosed_vs_found': rows, 'td_disclosed_vs_found': td,
            'reference_facts': facts, 'runs': table,
            'named_replays': [{'name': r['name'], 'ends': r['ends']} for r in replays],
            'extended_searches': long_runs(),
            'xlast_count_differences': xlast_listings(),
            'long_runs_over_600s': [t for t in table + long_runs() if t.get('seconds_total', 0) and t['seconds_total'] > 600]}
    summ['registered_runs_over_600s'] = [t['id'] for t in table if t.get('seconds_total', 0) > 600]
    gate = ART / 'gate.json'
    if gate.exists():
        g = json.loads(gate.read_text())
        summ['gate'] = {'pass': g['pass'], 'pairs': g['n_pairs'], 'structures': g['n_structures_compared'],
                        'controls': g['controls']}
    (ART / 'summary.json').write_text(json.dumps(summ, indent=1, default=str) + '\n')
    write_md(V, facts, rows, td, diffs, table, replays)
    for p, v in V.items():
        print(p, v['verdict'])
    print('differences from disclosed:', len(diffs))
    for d in diffs:
        print('  ', d)


if __name__ == '__main__':
    main()
