"""Every prediction of PB with its verdict and numbers: summary.json.  usage: python -B analyze_b.py"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402

KINDS = mcb.KINDS8
PB4_A_IS_B = lambda way, ky: way.startswith(('W1', 'W2', 'W3')) or ky not in ('pairs-3', 'pairs-4')  # noqa: E731


def load(name):
    p = cb.out_path(name)
    if not os.path.exists(p):
        return None
    return json.load(open(p)) if name.endswith('.json') else cb.read_jsonl(name)


def verdict(ok):
    return 'holds' if ok else 'fails'


def series_ok(xs):
    """Fewer than two at every round read; rounds not read are reported apart."""
    read = [x for x in xs if isinstance(x, int)]
    return all(x < 2 for x in read), sum(1 for x in xs if not isinstance(x, int))


def cnt(counts_row, cid):
    if counts_row is None:
        return None
    return counts_row.get(str(cid), 0)


def cb1(job, st, alone, yform, xkind, ykind, way, base, upto6=False):
    """CB-1 for one start (DB 4.1), with its failed clauses (DB 4.4)."""
    T = st['T'] if not upto6 else min(st['T'], 6)
    a = st['B_X']['Y form'][:T]
    b = alone['Y alone|' + ykind]['per_round_own_form'][:T] if ('Y alone|' + ykind) in alone else \
        st['_Y alone own'][:T]
    d = [cnt(r, yform) for r in alone['X alone|' + xkind]['counts'][:T]]
    oka, na = series_ok(a)
    okb, nb = series_ok(b)
    okd, nd = series_ok(d)
    ft = st['first_two'] if (st['first_two'] or 99) <= T else None
    ct = st['case_round'] if (st['case_round'] or 99) <= T else None
    later = (st['case_round'] or 0) > T or (st['first_two'] or 0) > T
    failed = []
    if ft is None:
        failed.append('no round with two')
    elif ct is None:
        failed.append('the knots descended from Y only not ended')
    if not oka:
        failed.append('(a)')
    if not okb:
        failed.append('(b)')
    if not okd:
        failed.append('(d)')
    holds = ct is not None and oka and okb and okd
    a_is_b = PB4_A_IS_B(way, ykind)
    allowed = {'(b)', '(d)'} | ({'(a)'} if a_is_b else set())
    on_b_alone = (not holds) and '(b)' in failed and set(failed) <= allowed
    if holds:
        kind = 'holds'
    elif base.startswith('COPY-LAW') and ykind in mcb.SETTLED4_EXCLUDED:
        kind = 'by argument (Settled 4)'
    else:
        kind = 'by census'
    return {'holds': holds, 'failure': None if holds else kind, 'failed clauses': failed,
            'on (b) alone': on_b_alone, 'T': T, 'first two': ft, 'case round': ct,
            'undecided past round T': bool(later and ct is None), 'rounds not read': na + nb + nd}


def arm1(rows, label, fallback=None, fallback_cb1=None):
    """CB-1, CB-2, PB10, PB11, PB13, PB14, PB15, PB7, PB18 from B1 or B2 rows."""
    res = {'jobs': len(rows), 'errors': [r['job'] for r in rows if 'error' in r]}
    cb1_rows = []
    cb2_rows = []
    pb7 = Counter()
    pb7_bad = []
    pb13 = []
    pb15 = []
    knots = Counter()
    knot_fail_rows = []
    for r in rows:
        if 'error' in r:
            continue
        job = r['job']
        base, kl = job['base'], job['knot_law']
        alone, kf = r['alone'], r['kind_forms']
        forms = r['forms']
        # knot tests
        for nm, a in alone.items():
            kt = a['knot_tests']
            knots['alone runs'] += 1
            knots['verdicts'] += kt['verdicts']
            if kt['n_fails']:
                knot_fail_rows.append({'law': r['law'], 'run': nm, 'fails': kt['fails'][:4]})
        alone_rosters = {}
        for nm, a in alone.items():
            for i, ro in enumerate(a['roster']):
                if ro is not None:
                    alone_rosters.setdefault(json.dumps(ro), '%s after round %d' % (nm, i + 1))
        for pl in r.get('perlaw') or []:
            for i, ro in enumerate(pl['Y alone']['roster']):
                if ro is not None:
                    alone_rosters.setdefault(json.dumps(ro), 'per-law form %d alone after round %d' % (pl['index'], i + 1))
        starts = r['starts']
        for key, st in starts.items():
            kx, ky, way = st['X kind'], st['Y kind'], st['way']
            for nm, kt in st['knot_tests'].items():
                knots['runs'] += 1
                knots['verdicts'] += kt['verdicts']
                knots['disagree'] += kt['n_disagree']
                if kt['n_fails']:
                    fl = kt['fails']
                    knot_fail_rows.append({'law': r['law'], 'run': key + ' ' + nm, 'n': kt['n_fails'],
                                           'fails': fl[:4]})
                    knots['tests with a failing knot'] += 1
                    knots['of them only start knots at round 0'] += all(f['made'] == 0 and f['round'] == 0
                                                                         for f in fl)
            yform = kf[ky]
            c = cb1(job, st, alone, yform, kx, ky, way, base)
            c6 = cb1(job, st, alone, yform, kx, ky, way, base, upto6=True)
            row = {'law': r['law'], 'base': base, 'knot law': kl, 'start': key, 'X': kx, 'Y': ky, 'way': way,
                   'control': kx == ky, **c, 'within 6 rounds': {k: c6[k] for k in ('first two', 'case round',
                                                                                     'failed clauses', 'holds')},
                   'details': st.get('details'),
                   'max Y form from both': max([p.get('Y form from both', 0) for p in st['per_round']] or [0]),
                   'mixed Y form (rounds)': sum(1 for p in st['per_round'] if p.get('Y form mixed')),
                   'mixed Y form within 6 rounds (rounds)': sum(1 for p in st['per_round'] if p.get('Y form mixed')
                                                                and p['t'] <= 6),
                   'rounds': st['rounds'], 'stop': st['stop'], 'closing round': st['closing_round']}
            cb1_rows.append(row)
            # PB7: (a) against (b)
            T = st['T']
            a = st['B_X']['Y form'][:T]
            b = alone['Y alone|' + ky]['per_round_own_form'][:T]
            eq = a == b
            grp = 'W4, Y pairs-3 or pairs-4' if (way.startswith('W4') and ky in ('pairs-3', 'pairs-4')) else (
                'W4, other Y' if way.startswith('W4') else 'W1 to W3')
            pb7[(grp, 'runs')] += 1
            pb7[(grp, 'equal')] += eq
            if not eq and grp != 'W4, Y pairs-3 or pairs-4':
                pb7_bad.append(key + ' ' + r['law'])
            # PB13: the forms from both, per round
            lst = [tuple(tuple(x) for x in (row_ or [])) for row_ in st['both forms']]
            pb13.append({'law': r['law'], 'base': base, 'kl': kl, 'X': kx, 'Y': ky, 'way': way, 'list': lst,
                         'R3': next(((i + 1, alone_rosters[json.dumps(ro)]) for i, ro in enumerate(st['roster'])
                                     if ro is not None and json.dumps(ro) in alone_rosters), None),
                         'forms': forms})
        # CB-2 per X, way
        by = defaultdict(dict)
        for row in cb1_rows:
            if row['law'] == r['law']:
                by[(row['X'], row['way'])][row['Y']] = row
        for (kx, way), ys in by.items():
            members = [k for k in KINDS if k != kx]
            if fallback_cb1 is not None:
                # deviations 10: a member with no listed start for the other-member swap is read on the main way
                for ky in members:
                    if ky not in ys:
                        fr = fallback_cb1.get((r['law'], kx, way.replace('-other', ''), ky))
                        if fr is not None:
                            ys[ky] = fr
            cs = {}
            for ky in members:
                yform = kf[ky]
                okc = True
                for ky2 in members:
                    if ky2 == ky:
                        continue
                    k2 = '%s + %s / %s' % (kx, ky2, way)
                    pool = starts
                    if k2 not in starts:
                        k2 = '%s + %s / %s' % (kx, ky2, way.replace('-other', ''))
                        if k2 not in starts:
                            pool = (fallback or {}).get(r['law'], {})
                    st2 = pool[k2]
                    T2 = min(ys[ky]['T'], st2['rounds'])
                    xs = [cnt(x, yform) for x in st2['counts'][:T2]]
                    okc = okc and series_ok(xs)[0]
                cs[ky] = okc
            good = [ky for ky in members if ys.get(ky, {}).get('holds') and cs[ky]]
            cb2_rows.append({'law': r['law'], 'base': base, 'knot law': kl, 'X': kx, 'way': way,
                             'holds': len(good) == len(members), 'members with CB-1 and (c)': good,
                             'failure': None if len(good) == len(members) else (
                                 'by argument (Settled 4)' if base.startswith('COPY-LAW') else 'by census'),
                             'members failing CB-1': {ky: ys[ky]['failed clauses'] for ky in members
                                                      if not ys.get(ky, {}).get('holds')},
                             'members failing (c)': [ky for ky in members if not cs[ky]]})
        # PB15: the per-law class
        for pl in r.get('perlaw') or []:
            for k2, st in pl['starts'].items():
                kx, way = k2.split(' / ')
                st['_Y alone own'] = pl['Y alone']['own form']
                c = cb1(job, st, {**alone}, pl['form'], kx, 'per-law %d' % pl['index'], way, 'per-law')
                pb15.append({'law': r['law'], 'form': mcb.form_text(forms[pl['form']]), 'X': kx, 'way': way, **c})
    res['CB-1'] = cb1_rows
    res['CB-2'] = cb2_rows
    res['PB7'] = {'%s|%s' % k: v for k, v in pb7.items()}
    res['PB7 unequal where (a) is (b)'] = pb7_bad[:20]
    res['PB13'] = pb13
    res['PB15'] = pb15
    res['knots'] = dict(knots)
    res['knot failures'] = knot_fail_rows[:30]
    res['n knot failure rows'] = len(knot_fail_rows)
    return res


def pb13_summary(pb13):
    """R1, R2 per X, law, way, knot law; forms present twice."""
    groups = defaultdict(list)
    for x in pb13:
        groups[(x['law'], x['X'], x['way'])].append(x)
    out = []
    twice = defaultdict(set)
    for (law, kx, way), xs in groups.items():
        forms = xs[0]['forms']
        lists = {x['Y']: x['list'] for x in xs}
        r1 = len({tuple(v) for v in lists.values()})
        seen_by = defaultdict(set)
        for ky, lst in lists.items():
            for rnd in lst:
                for cid, n in rnd:
                    seen_by[cid].add(ky)
                    if n >= 2:
                        twice[law.split('/')[0] + '/' + law.split('/')[1]].add(mcb.form_text(forms[cid]))
        r2 = {mcb.form_text(forms[c]): sorted(v) for c, v in seen_by.items() if len(v) == 1}
        out.append({'law': law, 'X': kx, 'way': way, 'R1': r1, 'R2': r2,
                    'R3': {x['Y']: x['R3'] for x in xs}})
    return out, {k: sorted(v) for k, v in twice.items()}


def main():
    S = {}
    tests = load('test_mcb.json')
    S['_tests'] = {'all ok': tests and tests.get('_all_ok'), 'n': tests and len(tests) - 1}
    # ---------------------------------------------------------------- PB1 (B4)
    b4 = load('b4.jsonl.gz') or []
    no_take = [x for r in b4 if not r['job']['take'] for x in r.get('rows', [])]
    met = [x for r in b4 if r['job']['take'] for x in r.get('rows', [])]
    reg8 = lambda x: not x['renaming'].startswith(('two usable', 'knot order reversed'))  # noqa: E731
    S['PB1'] = {'verdict': verdict(no_take and all(x['verdict'] != 'differs' for x in no_take)), 'numbers': {
        'renamed runs, no taking rule (RELEASE and HOLD, six base laws, both knot laws)': len(no_take),
        'of them a renaming at every round, built and verified': sum(
            1 for x in no_take if x['verdict'] == 'a renaming at every round'),
        'of them the same with some round found by search': sum(1 for x in no_take if x['by search']),
        'of them differing': sum(1 for x in no_take if x['verdict'] == 'differs'),
        'rounds compared': sum(x['rounds compared'] for x in no_take),
        'the eight renamings of version 1 / the two further': [sum(1 for x in no_take if reg8(x)),
                                                              sum(1 for x in no_take if not reg8(x))],
        'MET control, renamed runs (the eight renamings)': sum(1 for x in met if reg8(x)),
        'of them differing': sum(1 for x in met if reg8(x) and x['verdict'] == 'differs'),
        'MET control, all ten renamings: runs / differing': [len(met), sum(1 for x in met if x['verdict'] ==
                                                                          'differs')],
        'errors': [r['job'] for r in b4 if 'error' in r]},
        'seen': 'no taking rule: none differs; MET control: 1,860 of 3,456 renamed runs differ (replication)'}
    # ---------------------------------------------------------------- PB2, PB3, PB4, PB8, PB5 (B5)
    b5 = load('b5.jsonl.gz') or []
    f1 = [r['PB2'] for r in b5 if r.get('PB2')]
    S['PB2'] = {'verdict': verdict(f1 and all(x['identical'] == x['pairs'] for x in f1)), 'numbers': {
        'pairs': sum(x['pairs'] for x in f1), 'identical at every round': sum(x['identical'] for x in f1)},
        'seen': '1,536 pairs identical'}
    st3 = Counter()
    confl = []
    for r in b5:
        if 'PB3' not in r:
            continue
        rel = r['job']['release']
        for kl, v in r['PB3'].items():
            for k in ('steps', 'repeats', 'closing steps', 'distinct', 'n_conflicts',
                      'closing steps leaving a member'):
                st3[(rel, k)] += v.get(k, 0)
            confl += [dict(c, law=r['law'], kl=kl) for c in v['conflicts']]
    noclose_conf = [c for c in confl if not c['closing']]
    S['PB3'] = {'verdict': verdict(not [c for c in noclose_conf if 'RELEASE' in c['law']]) +
                (' (under HOLD: %s)' % ('no conflict' if not [c for c in noclose_conf if 'HOLD' in c['law']]
                                         else 'conflicts')),
                'numbers': {'%s|%s' % k: v for k, v in sorted(st3.items())}, 'conflicts (first 10)': confl[:10],
                'seen': '55,244 steps over RELEASE and HOLD; 27,734 distinct; 27,510 repeats; no conflict; 174 '
                        'steps close'}
    # PB4: round-0 partitions
    pb4 = {}
    if b5:
        r0 = b5[0]['round0']
        part_u, part_m = defaultdict(list), defaultdict(list)
        for k, v in r0.items():
            part_u[json.dumps(v['roster'])].append(k)
            part_m[json.dumps(v['marked'])].append(k)
        mine_u = {frozenset(v) for v in part_u.values()}
        mine_m = {frozenset(v) for v in part_m.values()}
        th_u, th_m = defaultdict(list), defaultdict(list)
        for k, v in mcb.ROSB['starts'].items():
            th_u[v['roster']].append(k)
            th_m[v['marked roster']].append(k)
        alone0 = b5[0]['alone round0']
        same_alone = {}
        for k, v in r0.items():
            same_alone[k] = sorted(kind for kind, ro in alone0.items() if ro == v['roster'])
        sa_eq = sum(1 for k in r0 if same_alone[k] == sorted(mcb.ROSB['starts'][k]['same as alone']))
        n_alone = Counter()
        for k, v in same_alone.items():
            for kind in v:
                n_alone[kind] += 1
        per_law = []
        for r in b5:
            for kl, v in r.get('PB4 per law', {}).items():
                per_law.append((r['law'], kl, v['classes'], v['classes whose starts differ']))
        pb4 = {'unmarked classes': len(mine_u), 'marked classes': len(mine_m),
               'the same partition as rosters_b.json (unmarked, marked)': [mine_u == {frozenset(v) for v in
                                                                                     th_u.values()},
                                                                          mine_m == {frozenset(v) for v in
                                                                                     th_m.values()}],
               '"same as alone" as listed': '%d of %d' % (sa_eq, len(r0)),
               'starts with the roster of an alone start, by kind': dict(n_alone),
               'classes x laws x knot laws read': sum(x[2] for x in per_law),
               'of them classes of two or more starts, RELEASE / HOLD (seen 636)': [
                   sum(len(r.get('PB4 per law', {})) * sum(1 for c in Counter(
                       json.dumps(v['marked']) for v in r['round0'].values()).values() if c >= 2)
                       for r in b5 if r['job']['release'] == rel) for rel in ('RELEASE', 'HOLD')],
               'of them with starts that differ at some round': sum(x[3] for x in per_law)}
        ok4 = pb4['the same partition as rosters_b.json (unmarked, marked)'] == [True, True] and \
            pb4['of them with starts that differ at some round'] == 0
        S['PB4'] = {'verdict': verdict(ok4), 'numbers': pb4,
                    'seen': '78 and 189 classes; 29 starts with an alone start\'s roster (two-23 8, pairs-4 5, '
                            'two-22 4, pairs-3 4, three-222 4, two-33 4); 636 classes of starts sharing a marked '
                            'roster, a law and a knot law agree'}
    pb8 = [r['PB8'] for r in b5 if r.get('PB8') and r['job']['release'] == 'RELEASE']
    pb8h = [r['PB8'] for r in b5 if r.get('PB8') and r['job']['release'] == 'HOLD']
    close = Counter()
    for r in b5:
        if r.get('PB8') and r['job']['release'] == 'RELEASE':
            close[r['job']['ration']] += len(r['PB8']['closing_runs'])
    S['PB8'] = {'verdict': verdict(pb8 and all(x['identical up to the first closing'] == x['pairs'] for x in pb8)),
                'numbers': {'pairs (RELEASE)': sum(x['pairs'] for x in pb8),
                            'identical up to the first closing': sum(x['identical up to the first closing']
                                                                     for x in pb8),
                            'parity runs that close (RELEASE), by ration': dict(close),
                            'under HOLD (reported): pairs, identical': [sum(x['pairs'] for x in pb8h), sum(
                                x['identical up to the first closing'] for x in pb8h)]},
                'seen': '1,536 pairs identical up to the first closing; 87 parity runs close (COPY-LAW 12, CAP-3 75)'}
    pb5 = Counter()
    for r in b5:
        if r.get('PB5'):
            for k, v in r['PB5'].items():
                pb5['%s|%s' % (r['job']['release'], k)] += v
    bad5 = {k: v for k, v in pb5.items() if ('three or more' in k or 'not offshoots' in k or 'made parts of the form'
                                             in k or 'not offshoots of one start knot' in k) and v}
    S['PB5'] = {'verdict': verdict(pb5 and not bad5), 'numbers': dict(pb5), 'failing counts': bad5}
    # ---------------------------------------------------------------- BG
    bg = load('bg.json')
    if bg:
        wc = bg['PB16 worked case']
        S['PB16'] = {'verdict': verdict(bg['PB16 controls']['all equal'] and wc[
            'under not-all-equal, run A from both equals three-222 alone, round by round'] and
            wc['under not-all-equal, at rounds 4, 6, 8'] == [1, 2, 4] and
            wc['under parity, the round-2 join of three parents closes and leaves nothing']),
            'numbers': {'controls': {k: [v['counts'], v['equal']] for k, v in bg['PB16 controls']['rows'].items()},
                        'worked case, not-all-equal, rounds 4, 6, 8': wc['under not-all-equal, at rounds 4, 6, 8'],
                        'worked case, equal to three-222 alone round by round': wc[
                            'under not-all-equal, run A from both equals three-222 alone, round by round'],
                        'worked case, parity: round-2 join of three parents closes, nothing left': wc[
                            'under parity, the round-2 join of three parents closes and leaves nothing'],
                        'worked case, round-0 roster the same as three-222 alone\'s': [
                            wc[k]['round-0 roster the same as three-222 alone\'s'] for k in ('nae', 'parity')]}}
        S['PB17'] = {'verdict': bg['PB17']['PB17'], 'numbers': {k: v for k, v in bg['PB17'].items() if k != 'PB17'},
                     'seen': 'X only in 86 pairs of a run and a round, Y only in 150; never from both, never mixed'}
    # ---------------------------------------------------------------- arm 1
    b1 = load('b1.jsonl.gz') or []
    A1 = arm1(b1, 'B1')
    S['_arm1'] = {k: v for k, v in A1.items() if k not in ('CB-1', 'PB13', 'PB15')}
    rows = A1['CB-1']
    copy_ = [x for x in rows if x['base'].startswith('COPY-LAW') and not x['control']]
    cap_ = [x for x in rows if x['base'].startswith('CAP-3') and not x['control']]
    two = [x for x in rows if x['first two'] and not x['control']]
    two6 = [x for x in rows if x['within 6 rounds']['first two'] and not x['control']]

    def clause_counts(xs):
        c = Counter()
        for x in xs:
            for f in x['failed clauses']:
                c[f] += 1
        return dict(c)
    und = [x for x in rows if x['Y'] == 'one-2' and x['base'] == 'COPY-LAW(RETIRE)']
    S['PB10'] = {'verdict': verdict(not any(x['holds'] for x in copy_) and not any(
        x['holds'] for x in und)), 'numbers': {
        'pairs read under COPY-LAW(t) (X other than Y)': len(copy_),
        'CB-1 holds': sum(x['holds'] for x in copy_),
        'failures by argument (Settled 4)': sum(1 for x in copy_ if x['failure'] == 'by argument (Settled 4)'),
        'failures by census': sum(1 for x in copy_ if x['failure'] == 'by census'),
        'of them on (b) alone': sum(1 for x in copy_ if x['failure'] == 'by census' and x['on (b) alone']),
        'runs with two parts the same as Y, each from both (X other than Y), through round 8': len(
            [x for x in two if x['base'].startswith('COPY-LAW')]),
        'the same within 6 rounds': len([x for x in two6 if x['base'].startswith('COPY-LAW')]),
        'by Y and treatment, within 6 rounds': dict(Counter('%s %s' % (x['Y'], x['base']) for x in two6
                                                            if x['base'].startswith('COPY-LAW'))),
        'by Y and treatment, through round 8': dict(Counter('%s %s' % (x['Y'], x['base']) for x in two
                                                            if x['base'].startswith('COPY-LAW'))),
        'the clauses that failed in those runs (through round 8)': clause_counts(
            [x for x in two if x['base'].startswith('COPY-LAW')]),
        'the clauses that failed in those runs (within 6 rounds)': clause_counts(
            [{'failed clauses': x['within 6 rounds']['failed clauses']} for x in two6
             if x['base'].startswith('COPY-LAW')]),
        'the undecided case (Y one-2, COPY-LAW(CANCEL-RETIRE)): runs, with a round t, with one such part at most': [
            len(und), sum(1 for x in und if x['case round']),
            sum(1 for x in und if x['max Y form from both'] == 1)],
        'the undecided case, the runs with one such part': ['%s %s %s' % (x['X'], x['way'], x['knot law'])
                                                            for x in und if x['max Y form from both'] == 1]},
        'seen': '36 runs with two (6 rounds): two-22 28 (offshoots 24, retiring 2, waiting 2), one-2 8 (offshoots); '
                '(a) and (b) fail in all 36, (d) in 28; the undecided case: at most one such part, in 6 of 64 runs'}
    two_cap = [x for x in two if x['base'].startswith('CAP-3')]
    S['PB11'] = {'verdict': verdict(not any(x['holds'] for x in cap_) and not [
        c for c in A1['CB-2'] if c['base'].startswith('CAP-3') and c['holds']]), 'numbers': {
        'pairs read under CAP-3(t) (X other than Y)': len(cap_), 'CB-1 holds': sum(x['holds'] for x in cap_),
        'runs with two parts the same as Y each from both (X other than Y)': len(two_cap),
        'of them': ['%s + %s / %s %s %s t=%s' % (x['X'], x['Y'], x['way'], x['base'], x['knot law'], x['first two'])
                    for x in two_cap][:20],
        'failures by census, by clause': clause_counts(cap_),
        'CB-2 holds (X, law, way)': sum(1 for c in A1['CB-2'] if c['base'].startswith('CAP-3') and c['holds']),
        'runs with a part of Y\'s form of mixed descent, pairs of a run and a round (within 6 rounds), by treatment':
            dict(Counter(x['base'] for x in cap_ for _ in range(x['mixed Y form within 6 rounds (rounds)'])))},
        'seen': 'no two parts the same as Y each from both, X other than Y; mixed in 44 pairs of a run and a round '
                '(waiting 36, retiring 4, offshoots 4)'}
    cb2 = A1['CB-2']
    S['PB9'] = {'verdict': verdict(not any(c['holds'] for c in cb2 if c['base'].startswith('COPY-LAW'))),
                'numbers': {'X and start\'s meetings under COPY-LAW(t), both knot laws': sum(
                    1 for c in cb2 if c['base'].startswith('COPY-LAW')), 'CB-2 holds': sum(
                    1 for c in cb2 if c['base'].startswith('COPY-LAW') and c['holds'])}}
    S['PB7'] = {'verdict': verdict(not A1['PB7 unequal where (a) is (b)']), 'numbers': A1['PB7'],
                'unequal where (a) is (b)': A1['PB7 unequal where (a) is (b)'],
                'seen': 'equal in every run under W1 to W3; under W4 equal except Y pairs-3 (48 runs) or pairs-4 (16)'}
    p13, twice = pb13_summary(A1['PB13'])
    copy13 = [x for x in p13 if x['law'].startswith('FLOOR1')]
    r2_copy = [x for x in copy13 if x['R2']]
    S['PB13'] = {'verdict': None, 'numbers': {
        'X, law, way and knot law read': len(p13),
        'under COPY-LAW: R1 > 1 in': sum(1 for x in copy13 if x['R1'] > 1), 'of': len(copy13),
        'under COPY-LAW: R2 not empty in': len(r2_copy), 'R2 examples': [x['R2'] for x in r2_copy[:5]],
        'forms present twice from both, by law': twice,
        'under CAP-3: R1 values': dict(Counter(x['R1'] for x in p13 if x['law'].startswith('CAP-3'))),
        'under CAP-3: R2 not empty in': sum(1 for x in p13 if x['law'].startswith('CAP-3') and x['R2']),
        'R3, the first round after which run A\'s roster is an alone run\'s (counts of starts with one)': dict(
            Counter(x['law'].split('/')[0] + ' ' + ('yes' if any(v for v in x['R3'].values()) else 'no')
                    for x in p13))}}
    copy_twice = set()
    for k, v in twice.items():
        if k.startswith('FLOOR1'):
            copy_twice |= set(v)
    S['PB13']['numbers']['forms present twice under COPY-LAW'] = sorted(copy_twice)
    S['PB13']['verdict'] = verdict(not r2_copy and len(copy_twice) <= 3)
    def pb14(xs, upto):
        c = Counter()
        how = Counter()
        for x in xs:
            ft = x['first two'] if upto is None else x['within 6 rounds']['first two']
            if not ft or not x.get('details') or str(ft) not in x['details']:
                continue
            d = x['details'][str(ft)]
            c['runs'] += 1
            c['exactly two'] += d['exactly two']
            c['no other part'] += d['other parts'] == 0
            c['the knots descended from Y only ended'] += bool(x['per_round_y_ended'].get(str(ft))) if x.get(
                'per_round_y_ended') else 0
            c['the knots descended from X only ended'] += bool(d['knots descended from X only ended'])
            c['X returns'] += bool(d["X returns (a part of X's form, every member from X only)"])
            c['a part of X\'s form descended from both'] += bool(d["a part of X's form descended from both"])
            for k, v in d['how the knots descended from Y only ended'].items():
                how[k] += v
        return dict(c), dict(how)
    for x in rows:
        x['per_round_y_ended'] = {}
    for r in b1:
        if 'error' in r:
            continue
        for key, st in r['starts'].items():
            pass
    yend = {}
    for r in b1:
        if 'error' in r:
            continue
        for key, st in r['starts'].items():
            yend[(r['law'], key)] = {str(p['t']): p.get('Y only ended') for p in st['per_round']}
    for x in rows:
        x['per_round_y_ended'] = yend.get((x['law'], x['start']), {})
    S['PB14'] = {'verdict': 'reported', 'numbers': {
        'at the first round with two, the runs with two within 6 rounds (X other than Y)': pb14(two6, 6),
        'the same through round 8': pb14(two, None),
        'the runs with two (X other than Y), first 60': [
            {'start': x['start'], 'law': x['law'], 'first two': x['first two'], 'case round': x['case round'],
             'details': x['details']} for x in two][:60]}}
    S['PB15'] = {'verdict': 'reported', 'numbers': {
        'per-law class starts read': len(A1['PB15']), 'CB-1 holds': sum(x['holds'] for x in A1['PB15']),
        'with two parts the same as Y each from both': sum(1 for x in A1['PB15'] if x['first two']),
        'failures by clause': clause_counts(A1['PB15']),
        'forms per law': dict(Counter(x['law'] for x in A1['PB15']))}}
    S['PB18'] = {'verdict': None, 'numbers': {'arm 1': A1['knots'], 'failures (first 30)': A1['knot failures']}}
    # ---------------------------------------------------------------- B2
    for nm, fn in (('other', 'b2_other.jsonl.gz'), ('hold', 'b2_hold.jsonl.gz')):
        rr = load(fn) or []
        if not rr:
            continue
        fb = {r['law']: r['starts'] for r in b1 if 'error' not in r}
        fbc = {(x['law'], x['X'], x['way'], x['Y']): x for x in rows}
        A2 = arm1(rr, 'B2 ' + nm, fallback=fb, fallback_cb1=fbc if nm == 'other' else None)
        xs = [x for x in A2['CB-1'] if not x['control']]
        S['_B2 ' + nm] = {'jobs': A2['jobs'], 'errors': A2['errors'], 'pairs': len(xs),
                          'CB-1 holds': sum(x['holds'] for x in xs),
                          'runs with two from both': ['%s %s t=%s' % (x['start'], x['law'], x['first two'])
                                                      for x in xs if x['first two']][:40],
                          'n runs with two from both': sum(1 for x in xs if x['first two']),
                          'clauses': clause_counts([x for x in xs if x['first two']]),
                          'CB-2 holds': sum(1 for c in A2['CB-2'] if c['holds']), 'knots': A2['knots'],
                          'PB7': A2['PB7']}
    # ---------------------------------------------------------------- B3
    b3 = []
    seen3 = set()
    for nm in ('b3.jsonl.gz', 'b3_small.jsonl.gz', 'b3_cut.jsonl.gz',
               'b3_cut2.jsonl.gz'):          # deviations 31, 32, 33: four parts
        for r in (load(nm) or []):
            k = json.dumps({x: r['job'][x] for x in ('base', 'choice', 'knot_law')}, sort_keys=True)
            if k not in seen3 and 'error' not in r:
                seen3.add(k)
                b3.append(r)
    S['_b3 jobs written'] = len(b3)
    S['_b3 the cut (dev 32): starts of DB 2 read per job'] = {
        r['law']: [r.get('starts read', len(r['starts'])), r.get('starts not run', 0), r.get('first start not run')]
        for r in b3}
    S['_b3 the fourth part (dev 33), per job'] = {r['law']: {
        k: r.get(k) for k in ('form tests undecided (deviations 33)', 'undecided tests by members of the part',
                              'parts classed by invariants and hash alone (deviations 33)', 'largest form read (members)',
                              'seconds', 'starts read', 'starts not run', 'first start not run')}
        for r in b3 if 'parts classed by invariants and hash alone (deviations 33)' in r}
    S['_b3 jobs not run'] = sorted('%s, MET(%s), %s' % (j['base'], j['choice'], j['knot_law'])
                                   for j in __import__('b3').jobs()
                                   if json.dumps({x: j[x] for x in ('base', 'choice', 'knot_law')},
                                                 sort_keys=True) not in seen3)
    A2 = arm2(b3)
    S['_arm2'] = A2
    # deviations 27 (added after the freeze): wider numberings, only for cases of arm 2 passing their registered renamings
    S['_post-freeze numberings (dev 27)'] = {
        'cases of arm 2 found': len(A2['cases']),
        'runs of arm 2 with two parts the same as Y each descended from both': len(A2['two from both']),
        'numberings run': 0 if not A2['cases'] else 'cases found: the registered renamings and numberings are to be run',
        'note': ('no case of arm 2, so no case passes its registered renamings and nothing was run (dev 24, 27)'
                 if not A2['cases'] else 'see the post-freeze file')}
    cb.write_json('post_freeze_numberings.json', S['_post-freeze numberings (dev 27)'])
    if b3:
        S['PB6'] = {'verdict': verdict(A2['PB6'].get('class-form parts from both', 0) == 0), 'numbers': A2['PB6']}
        cut_jobs = [r['law'] for r in b3 if r.get('starts not run')]
        n_read = sum(r.get('starts read', len(r['starts'])) for r in b3)
        n_not = sum(r.get('starts not run', 0) or 0 for r in b3)
        v12 = verdict(not A2['cases'])
        if cut_jobs and v12 == 'holds':
            v12 = 'holds on what was run (cut, deviations 32: %d starts of DB 2 not run in %d jobs)' % (n_not,
                                                                                                      len(cut_jobs))
        S['PB12'] = {'verdict': v12, 'numbers': {
            'jobs': A2['jobs'], 'errors': A2['errors'], 'cases (CB-1 under MET, X other than Y)': A2['cases'],
            'ticket A\'s designs read, per job': 12, 'starts of DB 2 read / not run (all jobs)': [n_read, n_not],
            'jobs cut (some starts not run)': cut_jobs,
            'jobs not run': S['_b3 jobs not run'],
            'runs with two parts the same as Y each from both (first 20)': A2['two from both'][:20],
            'n runs with two from both': len(A2['two from both'])},
            'seen': 'none on ticket A\'s designs, none on the starts under MET with CAP-3(t)'}
    ka = A1['knots']
    kinds = A2.get('knot fail kinds (parity)', {}) if b3 else {}
    S['PB18'] = {'verdict': verdict(not A1['n knot failure rows'] and all(k == 'join' for k in kinds) and
                                    not (A2.get('knots', {}).get('not-all-equal fails'))),
                 'numbers': {'arm 1 (B1): runs tested, verdicts, failing knots, disagreements': [
                     ka.get('runs'), ka.get('verdicts'), A1['n knot failure rows'], ka.get('disagree')],
                     'arm 2 (B3)': A2.get('knots'), 'arm 2, parity failing knots by kind': kinds},
                 'seen': 'none in 3,072 runs of arm 1; under MET knots fail only at joins under parity'}
    nb = [c for c in cb2 if not c['holds']]
    some = [c for c in cb2 if c['members with CB-1 and (c)'] and not c['holds']]
    S['PBA'] = {'verdict': 'only supported' if not any(c['holds'] for c in cb2) else 'overturned', 'numbers': {
        'CB-2 read (X, law, start\'s meeting, knot law), arm 1': len(cb2), 'CB-2 holds': sum(c['holds'] for c in cb2),
        'failures by argument (COPY-LAW, Settled 4)': sum(1 for c in nb if c['failure'].startswith('by argument')),
        'failures by census (CAP-3)': sum(1 for c in nb if c['failure'] == 'by census'),
        'some members and not all (DB 4.3)': len(some),
        'CB-1 failures by census not on (b) alone, arm 1 (bear on his first sentence)': sum(
            1 for x in rows if x['failure'] == 'by census' and not x['on (b) alone'] and not x['control']),
        'CB-1 failures on (b) alone': sum(1 for x in rows if x['failure'] == 'by census' and x['on (b) alone']
                                          and not x['control']),
        'CB-1 failures by argument': sum(1 for x in rows if x['failure'] and x['failure'].startswith('by argument')
                                         and not x['control'])}}
    p3 = S.get('PB3', {}).get('numbers', {})
    stp = sum(v for k, v in p3.items() if k.endswith('|steps'))
    dis = sum(v for k, v in p3.items() if k.endswith('|distinct'))
    rep = sum(v for k, v in p3.items() if k.endswith('|repeats'))
    cl = sum(v for k, v in p3.items() if k.endswith('|closing steps'))
    mix = S.get('PB11', {}).get('numbers', {}).get(
        'runs with a part of Y\'s form of mixed descent, pairs of a run and a round (within 6 rounds), by treatment', {})
    p17 = S.get('PB17', {}).get('numbers', {}).get('parts by descent (without made-2-exchanged)', {})
    S['_disagreements'] = [
        '## Differences from the disclosed numbers, and what the replays show (`replays_b.json`)', '',
        '1. **PB3\'s counts** (a check; its verdict holds, no conflict, %d steps that close, as seen 174): steps %d, '
        'distinct keys %d, repeats %d; seen 55,244, 27,734 and 27,510. Every run of B5 reaches its last round here '
        '(2,048 steps per COPY-LAW(t) job and knot law, 2,560 per CAP-3(t) one, listed), so the 52 steps fewer there would '
        'be runs ending earlier in the prototype; not reproduced here, and no verdict depends on it.' % (cl, stp, dis, rep),
        '2. **PB11\'s parts of Y\'s form of mixed descent** within 6 rounds, X other than Y: %s pairs of a run and a '
        'round (waiting %s, retiring %s, offshoots %s), and 8 more in the controls under waiting; seen 44 (36, 4, 4). '
        'Every one is listed with its members, h, k, parents and descents; the retiring and offshoot counts agree, '
        'waiting has 4 fewer than seen (and 4 more with the controls). Not reproduced either way; a reported count.' % (
            sum(mix.values()), mix.get('CAP-3(WAIT)'), mix.get('CAP-3(RETIRE)'), mix.get('CAP-3(OFFSHOOT)')),
        '3. **PB17**: in ticket A\'s run 2 file (without made-2-exchanged), parts the same as the run\'s own Y: '
        'X only %s, Y only %s; seen 86 and 150. The 2 more from X only are made-6 under CAP-3(t) with MET, where that '
        'design\'s Y has members holding three (ticket A\'s disagreement 2); never from both, never mixed: PB17 holds.' % (
            p17.get('X only'), p17.get('Y only')),
        '4. **"On (b) alone"** (DB 4.4): the claim reads the 36 failures of CB-1 seen as on (b) alone. Under DB 4.4\'s '
        'list of clauses, 22 of the 36 (within 6 rounds) also fail "the knots descended from Y only not ended" by round '
        '6, so 14 are on (b) alone there; through round 8, 22 of the 100 runs with two. The clauses (a), (b) and (d) '
        'agree with the disclosure exactly (36, 36, 28).', '']
    cb.write_json('summary.json', S)
    for k in sorted(S):
        if not k.startswith('_'):
            print(k, S[k].get('verdict'))


def arm2(rows):
    out = {'jobs': len(rows), 'errors': [r['job'] for r in rows if 'error' in r], 'cases': [], 'two from both': [],
           'PB6': Counter(), 'knots': Counter(), 'knot fail kinds (parity)': Counter()}
    for r in rows:
        if 'error' in r:
            continue
        base = r['job']['base']
        check_row = base.startswith('COPY-LAW')
        kf = r['kind_forms']
        cf = set(str(v) for v in r['class forms'].values() if v is not None)
        for name, d in r['designs'].items():
            if 'per_round' not in d:
                continue
            if d['first_two']:
                out['two from both'].append('%s %s t=%s' % (name, r['law'], d['first_two']))
            okab = all(series_ok(d[k])[0] for k in ('(a) B_X', '(b) Y alone', '(d) X alone'))
            if d['case_round'] and okab and not name.startswith('made-2') and name != 'ystart-two-22':
                out['cases'].append({'design': name, 'law': r['law'], 'round': d['case_round']})
            if check_row:
                out['PB6']['designs read'] += 1
                out['PB6']['class-form parts from both'] += sum(n for row in d['both forms'] if row
                                                                for c, n in row if str(c) in cf)
            kt = d['knot_tests']
            out['knots']['verdicts'] += kt['verdicts']
            out['knots']['fails'] += kt['n_fails']
            out['knots']['disagree'] += kt['n_disagree']
            if r['job']['knot_law'] == 'parity':
                out['knot fail kinds (parity)'].update(kt.get('fail_kinds') or Counter(f['kind'] for f in kt['fails']))
            elif kt['n_fails']:
                out['knots']['not-all-equal fails'] += kt['n_fails']
        for key, st in r['starts'].items():
            if st['first_two'] and st['X kind'] != st['Y kind']:
                out['two from both'].append('%s %s t=%s' % (key, r['law'], st['first_two']))
            if check_row:
                out['PB6']['starts read'] += 1
                out['PB6']['class-form parts from both'] += st.get('class forms from both', 0)
            kt = st['knot_tests']['A']
            out['knots']['verdicts'] += kt['verdicts']
            out['knots']['fails'] += kt['n_fails']
            if r['job']['knot_law'] == 'parity':
                out['knot fail kinds (parity)'].update(kt.get('fail_kinds') or Counter(f['kind'] for f in kt['fails']))
            elif kt['n_fails']:
                out['knots']['not-all-equal fails'] += kt['n_fails']
            if st['case_round'] and st['X kind'] != st['Y kind'] and st['case_round'] <= st['T']:
                al = r['alone']
                yf = str(kf[st['Y kind']])
                T = st['T']
                a = st['B_X']['Y form'][:T]
                b = [(c or {}).get(yf, 0) if c is not None else None for c in al['Y alone|' + st['Y kind']]['counts'][:T]]
                d = [(c or {}).get(yf, 0) if c is not None else None for c in al['X alone|' + st['X kind']]['counts'][:T]]
                if series_ok(a)[0] and series_ok(b)[0] and series_ok(d)[0]:
                    out['cases'].append({'start': key, 'law': r['law'], 'round': st['case_round']})
                else:
                    out['round t, failing (a), (b) or (d)'] = out.get('round t, failing (a), (b) or (d)', 0) + 1
    out['PB6'] = dict(out['PB6'])
    out['knots'] = dict(out['knots'])
    out['knot fail kinds (parity)'] = dict(out['knot fail kinds (parity)'])
    return out


if __name__ == '__main__':
    main()
