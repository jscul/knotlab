"""Every prediction's verdict, the rates of cases with their zero bounds by stratum under each weighting of starts, the
knot tests, the renaming checks and the reported counts, from the result files: summary.json and summary.md."""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402

RUNS = {'R1a': ('parity', 'MET', 'T1', 3344), 'R1b': ('parity', 'STEPS-1', 'T1', 2000),
        'R1c': ('nae', 'MET', 'T1', 1000), 'R1d': ('nae', 'STEPS-1', 'T1', 120), 'R2': ('parity', 'both', 'T2', 500)}
CLAIMED = mcc.CLAIMED
REPORTED = mcc.REPORTED
READINGS = CLAIMED + REPORTED
COPY_OFF = 'FLOOR1/CANCEL-OFFSHOOT'


def lawkey(law):
    p = law.split('/')
    return '/'.join([p[0], p[1], p[3]])


def load(name):
    p = study.out_path(name)
    return json.load(open(p)) if os.path.exists(p) else None


def run_summary(run, conf_keys, full_key=False):
    rows = study.read_jsonl('%s.jsonl.gz' % run)
    if not rows:
        return None
    C = mcc.census()
    W = {i: s['labelled'] for i, s in enumerate(C)}
    size = {i: s['n'] for i, s in enumerate(C)}
    per = defaultdict(lambda: {'growths': Counter(), 'errors': Counter(), 'pair': Counter(), 'w': defaultdict(list),
                               'case': defaultdict(Counter), 'pass100': defaultdict(Counter),
                               'onehist': defaultdict(Counter), 'confirmed': defaultdict(Counter),
                               'case_nofail': defaultdict(Counter), 'pass100_nofail': defaultdict(Counter),
                               'growths_nofail': Counter(), 'wcase': defaultdict(lambda: defaultdict(float)),
                               'wpass': defaultdict(lambda: defaultdict(float)), 'wsum': defaultdict(float),
                               'wsum_nofail': defaultdict(float),
                               'wcase_nofail': defaultdict(lambda: defaultdict(float)),
                               'wpass_nofail': defaultdict(lambda: defaultdict(float)),
                               'stops': Counter(), 'kt_verdicts': 0, 'kt_fails': 0, 'kt_disagree': 0,
                               'growths_failing': 0, 'fail_classes': Counter(), 'more8': 0, 'removed': 0,
                               'pairs': 0, 'met_pairs': 0, 'unmet_pairs': 0, 'unmet_read': Counter(),
                               'met_read': Counter(), 'twice_growths': 0, 'twice_forms': set(),
                               'again_same_growth': 0, 'cases_list': [], 'nae_tie_classes': 0,
                               'nae_made_tie_classes': 0, 'nae_growths_checked': 0, 'max_holders': 0})
    total = Counter()
    for r in rows:
        lk = ('/'.join(r['law'].split('/')[:5]) + ('' if 'part' not in r else ' [%s]' % r['part'])) if full_key \
            else lawkey(r['law'])
        d = per[lk]
        idx = r['index']
        st = size[idx]
        if 'error' in r:
            d['errors'][st] += 1
            total['errors'] += 1
            total['not read: ' + r['error']] += 1
            continue
        total['growths'] += 1
        d['growths'][st] += 1
        d['w'][st].append(W[idx])
        d['wsum'][st] += W[idx]
        kt = r.get('knot_test', {})
        failing = bool(kt.get('n_fails'))
        if not failing:
            d['growths_nofail'][st] += 1
            d['wsum_nofail'][st] += W[idx]
        d['kt_verdicts'] += kt.get('verdicts', 0)
        d['kt_fails'] += kt.get('n_fails', 0)
        d['kt_disagree'] += kt.get('disagree', 0)
        d['growths_failing'] += int(failing)
        for f in kt.get('fails', []):
            d['fail_classes'][(f['kind'], min(f['parents'], 3), f['took'], f['implied'], f['made'])] += 1
        d['stops'][(r['stop'] or 'none (rounds or roster ended)') if r['stop'] != 'guard'
                   else 'guard: %s' % r['guard']['what']] += 1
        n_all = sum(v[1] for v in r['pair_rounds'].values())
        if n_all > 0:
            d['pair'][st] += 1
        d['more8'] += len(r['more_than_eight'])
        d['removed'] += r['removed']
        for p in r['pairs']:
            d['pairs'] += 1
            if p['meet'] is None:
                d['unmet_pairs'] += 1
                for g in READINGS:
                    if g in p['first']:
                        d['unmet_read'][g] += 1
            else:
                d['met_pairs'] += 1
                for g in READINGS:
                    if g in p['after']:
                        d['met_read'][g] += 1
        bf = r.get('by_form') or []
        tw = set()
        for x in bf:
            if x:
                tw.update(x['twice'])
        if tw:
            d['twice_growths'] += 1
            d['twice_forms'].update(tw)
        if 'nae_last_round_ties' in r:
            d['nae_growths_checked'] += 1
            d['nae_tie_classes'] += r['nae_last_round_ties']['classes']
            d['nae_made_tie_classes'] += r['nae_last_round_ties']['classes_with_a_made_distinction']
        got = defaultdict(set)
        xforms = Counter()
        for c in r['cases']:
            g = c['reading']
            got['case'].add(g)
            xforms[(c['xform']['key'], g)] += 1
            fs = c.get('first_stage', {})
            if fs.get('passes_at_100'):
                got['pass'].add(g)
            if fs.get('one_history'):
                got['onehist'].add(g)
            key = (run, idx, r['law'], c['s'], tuple(c['X']), tuple(c['Y']), g)
            if key in conf_keys:
                got['conf'].add(g)
            d['cases_list'].append({'start': r['start'], 'law': r['law'], 's': c['s'], 'X': c['X'], 'Y': c['Y'],
                                    'reading': g, 'meet': c['meet'], 'round_met': c['round_met'],
                                    'xform': c['xform']['key'], 'yform': c['yform']['key'],
                                    'y_loose_max': c['y_loose_max'],
                                    'q100': [c['rates100']['q1'], c['rates100']['q0'], c['rates100']['qY']]
                                    if 'rates100' in c else None,
                                    'p100': [fs.get('p_vs_Ybarred'), fs.get('p_vs_Yown')],
                                    'passes_at_100': fs.get('passes_at_100'), 'one_history': fs.get('one_history'),
                                    'growth_has_failing_knot': failing, 'made': c['made_questions'].get('made'),
                                    'y_made': c['made_questions'].get('Y made')})
        if any(v >= 2 for v in xforms.values()):
            d['again_same_growth'] += 1
        for k in ('case', 'pass', 'onehist', 'conf'):
            if got[k] & set(CLAIMED):
                got[k].add('claimed')
        for g in got['case']:
            d['case'][g][st] += 1
            d['wcase'][g][st] += W[idx]
            if not failing:
                d['case_nofail'][g][st] += 1
                d['wcase_nofail'][g][st] += W[idx]
        for g in got['pass']:
            d['pass100'][g][st] += 1
            d['wpass'][g][st] += W[idx]
            if not failing:
                d['pass100_nofail'][g][st] += 1
                d['wpass_nofail'][g][st] += W[idx]
        for g in got['onehist']:
            d['onehist'][g][st] += 1
        for g in got['conf']:
            d['confirmed'][g][st] += 1
        for k in ('case', 'pass', 'conf'):
            if got[k] & set(CLAIMED):
                total['growths with a claimed %s' % k] += 1
    out = {'growths read': total['growths'], 'growths not read (memory cap)': total['errors'],
           'not read, by reason': {k[10:]: v for k, v in total.items() if k.startswith('not read: ')}, 'laws': {}}
    for lk, d in sorted(per.items()):
        L = {'growths': dict(d['growths']), 'not read (memory)': dict(d['errors']),
             'with a pair in rounds 1 to 4': dict(d['pair']),
             'share with a pair': {st: round(d['pair'][st] / d['growths'][st], 4) for st in d['growths']},
             'stops': dict(d['stops']), 'knot test': {'verdicts': d['kt_verdicts'], 'failing knots': d['kt_fails'],
                                                      'growths with a failing knot': d['growths_failing'],
                                                      'method disagreements': d['kt_disagree'],
                                                      'classes (kind, parents (3 = 3+), took, implied, round)':
                                                          [[list(k), v] for k, v in sorted(d['fail_classes'].items())]},
             'rounds with more than eight pairs': d['more8'], 'ordered pairs removed by wholly apart': d['removed'],
             'pairs read': d['pairs'], 'met pairs': d['met_pairs'], 'unmet pairs': d['unmet_pairs'],
             'readings on met pairs after the meeting': dict(d['met_read']),
             'readings on unmet pairs (any round)': dict(d['unmet_read']),
             'growths with a form left twice': d['twice_growths'], 'forms left twice': len(d['twice_forms']),
             'growths with one X form in two or more cases': d['again_same_growth'],
             'cases': d['cases_list']}
        if d['nae_growths_checked']:
            L['not-all-equal ties at the last round'] = {'growths': d['nae_growths_checked'],
                                                         'tie classes': d['nae_tie_classes'],
                                                         'classes with a made distinction':
                                                             d['nae_made_tie_classes']}
        rates = {}
        for g in ('claimed',) + READINGS:
            rg = {}
            for st in sorted(d['growths']) + ['all']:
                sts = sorted(d['growths']) if st == 'all' else [st]
                N = sum(d['growths'][x] for x in sts)
                Nn = sum(d['growths_nofail'][x] for x in sts)
                ws = sum(d['wsum'][x] for x in sts)
                wsn = sum(d['wsum_nofail'][x] for x in sts)
                allw = [w for x in sts for w in d['w'][x]]
                factor = max(allw) / (ws / N) if N else None
                row = {'N': N, 'N_no_failing_knot': Nn,
                       'case': sum(d['case'][g][x] for x in sts),
                       'passes_at_100': sum(d['pass100'][g][x] for x in sts),
                       'one_history': sum(d['onehist'][g][x] for x in sts),
                       'confirmed': sum(d['confirmed'][g][x] for x in sts),
                       'case_no_failing_knot': sum(d['case_nofail'][g][x] for x in sts),
                       'passes_at_100_no_failing_knot': sum(d['pass100_nofail'][g][x] for x in sts),
                       'census': {'case': sum(d['case'][g][x] for x in sts) / N if N else None,
                                  'passes_at_100': sum(d['pass100'][g][x] for x in sts) / N if N else None,
                                  'confirmed': sum(d['confirmed'][g][x] for x in sts) / N if N else None,
                                  'zero_bound': min(1.0, 3 / N) if N else None},
                       'labelled': {'case': sum(d['wcase'][g][x] for x in sts) / ws if ws else None,
                                    'passes_at_100': sum(d['wpass'][g][x] for x in sts) / ws if ws else None,
                                    'zero_bound': min(1.0, 3 / N * factor) if N else None,
                                    'max w / mean w': factor},
                       'no failing knot': {
                           'census': {'case': sum(d['case_nofail'][g][x] for x in sts) / Nn if Nn else None,
                                      'passes_at_100': sum(d['pass100_nofail'][g][x] for x in sts) / Nn if Nn
                                      else None},
                           'labelled': {'case': sum(d['wcase_nofail'][g][x] for x in sts) / wsn if wsn else None,
                                        'passes_at_100': sum(d['wpass_nofail'][g][x] for x in sts) / wsn if wsn
                                        else None}}}
                rg[str(st)] = row
            rates[g] = rg
        L['rates'] = rates
        out['laws'][lk] = L
    return out


def beyond_note():
    rows = study.read_jsonl('R1d_beyond_quarter.jsonl.gz')
    out = {'growths': len(rows), 'note': "R1d's growths of starts 30 to 119 written before R1d was stopped (dev 55): "
                                         'not part of the size run; in no rate, bound, family or verdict', 'cases': []}
    for r in rows:
        for c in r.get('cases', []):
            out['cases'].append({'start': r['start'], 'law': r['law'], 'reading': c['reading'], 's': c['s'],
                                 'X': c['X'], 'Y': c['Y'], 'q100': [c['rates100']['q1'], c['rates100']['q0'],
                                                                    c['rates100']['qY']],
                                 'passes_at_100': c['first_stage']['passes_at_100'], 'counted': False})
    out['passing at 100 (not counted)'] = [c for c in out['cases'] if c['passes_at_100']]
    return out


def fmt_pct(x, nd=2):
    return '—' if x is None else ('%.*f%%' % (nd, 100 * x))


def main():
    S = {'engine_hashes': mcc.engine_hashes(), 'engine_hashes_equal': mcc.engine_hashes() == mcc.ENGINE_SHA}
    S['R0'] = load('gate_R0.json')
    S['R0b'] = load('controls_R0b.json')
    S['tests'] = load('test_mcc.json')
    R3 = load('R3.json')
    conf_keys = set()
    if R3:
        for c in R3['cases']:
            if c['confirmation']['confirmed']:
                conf_keys.add((c['run'], c['index'], c['law'], c['s'], tuple(c['X']), tuple(c['Y']), c['reading']))
    S['R3'] = R3 and {k: R3[k] for k in ('runs read', 'm', "m'", 'level_claimed', 'level_reported')}
    S['R3_cases'] = R3 and [{k: c[k] for k in ('run', 'start', 'law', 's', 'X', 'Y', 'reading', 'family',
                                               'rates100', 'rates1000', 'confirmation', 'made_questions',
                                               'growth_has_failing_knot')} for c in R3['cases']]
    runs = {}
    for run in RUNS:
        rs = run_summary(run, conf_keys)
        if rs is not None:
            runs[run] = rs
    S['runs'] = runs
    RC = load('Rcond.json')
    cond_keys = set()
    if RC:
        for c in RC['cases']:
            if c['confirmation']['confirmed']:
                cond_keys.add((c['run'], c['index'], c['law'], c['s'], tuple(c['X']), tuple(c['Y']), c['reading']))
    S['Rcond'] = RC and {k: RC[k] for k in ('runs read', 'm', "m'", 'level_claimed', 'level_reported', 'family of')}
    S['Rcond_cases'] = RC and [{k: c[k] for k in ('run', 'start', 'law', 's', 'X', 'Y', 'reading', 'family',
                                                 'rates100', 'rates1000', 'confirmation', 'made_questions',
                                                 'growth_has_failing_knot')} for c in RC['cases']]
    S['cond_runs'] = {}
    for run in ('R5', 'R6'):
        rs = run_summary(run, cond_keys, full_key=True)
        if rs is not None:
            S['cond_runs'][run] = rs
    S['R1d beyond its quarter (not counted)'] = beyond_note()
    S['R7'] = load('R7.json')
    if S['R7']:
        S['R7'] = {k: v for k, v in S['R7'].items() if k != 'rows'}
    S['R8'] = load('R8.json')
    if S['R8']:
        for k in ('starts read', 'starts read, not set aside'):
            if k in S['R8']:
                S['R8'][k] = {kk: vv for kk, vv in S['R8'][k].items() if kk != 'tests'} | {
                    'rejected tests': [t for t in S['R8'][k]['tests'] if t['rejected']]}
    S['R9'] = load('R9.json')
    S['run_times'] = load('run_times.json')
    S['predictions'] = predictions(S)
    S['not_run'] = not_run(S)
    study.write_json('summary.json', S)
    write_md(S)


def laws_of_run(S, run):
    return S['runs'].get(run, {}).get('laws', {})


def predictions(S):
    P = []
    R = S['runs']

    def add(n, text, verdict, numbers):
        P.append({'#': n, 'prediction': text, 'verdict': verdict, 'numbers': numbers})

    # PC1
    rows, bad, nr = [], [], []
    for run, kl in (('R1a', 'parity'), ('R1c', 'nae')):
        if run not in R:
            nr.append(run)
            continue
        for lk, L in laws_of_run(S, run).items():
            for st, sh in L['share with a pair'].items():
                rows.append([run, lk, st, sh])
                st = int(st)
                if lk.startswith(COPY_OFF + '/'):
                    lo, hi = (0.20, 0.55) if st == 5 else (0.25, 0.65)
                    if not (lo <= sh <= hi):
                        bad.append([run, lk, st, sh])
                elif sh > 0.10:
                    bad.append([run, lk, st, sh])
    add('PC1', 'Under MET, at most 10% of growths with a pair (20 laws, each knot law and start size); '
               'COPY-LAW(CANCEL-OFFSHOOT) 20%-55% (five knots), 25%-65% (three, four)',
        'not run' if len(nr) == 2 else ('holds' if not bad else 'fails') + (' (not run: %s)' % nr if nr else ''),
        {'outside': bad, 'COPY-LAW(CANCEL-OFFSHOOT)': [x for x in rows if x[1].startswith(COPY_OFF + '/')],
         'largest other': sorted([x for x in rows if not x[1].startswith(COPY_OFF + '/')], key=lambda x: -x[3])[:6]})
    # PC2
    bad, rows, nr = [], [], []
    for run in ('R1b', 'R1d'):
        if run not in R:
            nr.append(run)
            continue
        for lk, L in laws_of_run(S, run).items():
            N = sum(L['growths'].get(st, 0) for st in (3, 4))
            k = sum(L['with a pair in rounds 1 to 4'].get(st, 0) for st in (3, 4))
            sh = k / N if N else None
            rows.append([run, lk, k, N, sh])
            if sh is not None and sh < 0.20:
                bad.append([run, lk, k, N, sh])
    add('PC2', 'Under STEPS-1, at least 20% of growths with a pair on the starts of three and four knots, each law',
        'not run' if len(nr) == 2 else ('holds' if not bad else 'fails') + (' (not run: %s)' % nr if nr else ''),
        {'below 20%': bad, 'smallest': sorted([x for x in rows if x[4] is not None], key=lambda x: x[4])[:6]})
    # PC3, PC4, PC5
    R3 = S.get('R3')
    main_read = [r for r in ('R1a', 'R1b', 'R1c', 'R1d', 'R2') if r in R]
    conf = [c for c in (S.get('R3_cases') or []) if c['family'] == 'claimed' and c['confirmation']['confirmed']]
    conf_ok = [c for c in conf if not c['growth_has_failing_knot']]
    if R3 is None:
        v3 = 'not run (R3 not run)'
    else:
        v3 = 'holds' if not conf_ok else 'fails'
    add('PC3', 'No confirmed case of a claimed reading in the main runs (CC-1 not found)', v3,
        {'main runs read': main_read, 'm (claimed cases passing at 100)': R3 and R3['m'],
         'confirmed': len(conf), 'confirmed in growths with no failing knot': len(conf_ok)})
    # DC 5.1: a candidate, under one law and knot law, is one form F of made pattern with confirmed cases for at least
    # two second-pattern forms G other than F
    xf = {}
    for run in R:
        for lk, L in laws_of_run(S, run).items():
            for c in L['cases']:
                xf[(run, c['start'], c['law'], c['s'], tuple(c['X']), tuple(c['Y']), c['reading'])] = c
    by_f = defaultdict(set)
    for c in conf_ok:
        cc = xf.get((c['run'], c['start'], c['law'], c['s'], tuple(c['X']), tuple(c['Y']), c['reading']))
        if cc and cc['xform'] != cc['yform']:
            by_f[(c['law'], cc['xform'])].add(cc['yform'])
    cands = {'%s | F %s' % k: sorted(v) for k, v in by_f.items() if len(v) >= 2}
    add('PC4', 'No candidate seen again (CC-2 not found)',
        'not run (R3 not run)' if R3 is None else ('holds (no candidate: no form F of made pattern has confirmed '
                                                   'cases for two second-pattern forms; stage 2 not triggered)'
                                                   if not cands else 'candidate found: stage 2 (R4) triggered'),
        {'forms F with confirmed cases, and their second-pattern forms G':
            {'%s | F %s' % k: sorted(v) for k, v in by_f.items()}, 'candidates': cands})
    conf_met_form = [c for c in conf if c['reading'] == 'form' and '/MET/' in c['law']]
    add('PC5', 'Under MET, no form case is confirmed', 'not run' if R3 is None else
        ('holds' if not conf_met_form else 'fails'), {'confirmed MET form cases': len(conf_met_form)})
    # PC6
    byl = defaultdict(Counter)
    for run in main_read:
        for lk, L in laws_of_run(S, run).items():
            for c in L['cases']:
                if c['reading'] in ('form', 'both'):
                    byl[lk][c['y_loose_max']] += 1
    argued = ['FLOOR1/%s/%s' % (t, tk) for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT') for tk in ('MET', 'STEPS-1')]
    bad = {k: dict(v) for k, v in byl.items() if k in argued and any(x > 1 for x in v)}
    wait = {k: dict(v) for k, v in byl.items() if k.startswith('FLOOR1/CANCEL-WAIT/')}
    add('PC6', "COPY-LAW(RETIRE, OFFSHOOT) with MET and STEPS-1: every member of Y in a form or from-both case holds at "
               "most one loose distinction (CANCEL-WAIT checked)", 'holds' if not bad else 'fails',
        {'argued laws, by most loose of a member of Y': {k: dict(v) for k, v in byl.items() if k in argued},
         'CANCEL-WAIT (check)': wait, 'violations': bad})
    # PC7
    nae = []
    for run in ('R1c', 'R1d'):
        for lk, L in laws_of_run(S, run).items():
            t = L.get('not-all-equal ties at the last round')
            if t:
                nae.append([run, lk, t['growths'], t['tie classes'], t['classes with a made distinction']])
    bad = [x for x in nae if x[4] > 0]
    add('PC7', 'Under not-all-equal no values reading is met',
        'not run' if not nae else ('holds' if not bad else 'fails'),
        {'growths checked': sum(x[2] for x in nae), 'tie classes at the last round': sum(x[3] for x in nae),
         'with a made distinction': sum(x[4] for x in nae)})
    # PC8
    both = []
    for run in main_read:
        for lk, L in laws_of_run(S, run).items():
            for c in L['cases']:
                if c['reading'] == 'both':
                    both.append([run, c['start'], c['law'], c['q100'], c['passes_at_100']])
    add('PC8', 'From both: no case passes at 100', 'holds' if not any(x[4] for x in both) else 'fails',
        {'from-both cases': len(both), 'passing': [x for x in both if x[4]][:10]})
    # PC9
    va = []
    for run in main_read:
        if RUNS[run][0] != 'parity':
            continue
        for lk, L in laws_of_run(S, run).items():
            for c in L['cases']:
                if c['reading'] == 'vA':
                    va.append([run, lk, c['law'], c['q100'], c['passes_at_100']])
    va_off = [x for x in va if x[1].startswith(COPY_OFF + '/')]
    va_pass = [x for x in va_off if x[4]]
    confA = [c for c in (S.get('R3_cases') or []) if c['reading'] == 'vA' and c['confirmation']['confirmed']]
    joining = [c for c in confA if c['confirmation'].get('way') == 'through joining']
    v9 = 'holds' if (va_pass and not joining) else 'fails'
    add('PC9', "Ticket A's values reading: under COPY-LAW(CANCEL-OFFSHOOT), parity, some cases pass at 100; a "
               "confirmed one, if any, is through takes", v9,
        {'cases under COPY-LAW(CANCEL-OFFSHOOT), parity': len(va_off), 'passing at 100': len(va_pass),
         'all vA cases (parity)': len(va), 'confirmed (its own family)': len(confA),
         'ways': [c['confirmation'].get('way') for c in confA]})
    # PC10, PC11, PC12
    r7 = S.get('R7')
    add('PC10', 'R7: the distributions are equal in every check', 'not run' if not r7 else
        ('holds' if r7['all_equal'] == r7['checks'] else 'fails'),
        r7 and {'checks': r7['checks'], 'all equal': r7['all_equal'], 'single history': r7['single_history'],
                'by label': r7['by_label']})
    r8 = S.get('R8')
    add('PC11', 'R8: no rejection (each law and renaming at 0.05/210; pooled at 0.05/5)', 'not run' if not r8 else
        ('holds' if r8['starts read']['rejections'] == 0 and r8['starts read']['pooled_rejections'] == 0 else 'fails'),
        r8 and {k: {'starts': r8[k].get('starts'), 'rejections': r8[k]['rejections'],
                    'pooled rejections': r8[k]['pooled_rejections'], 'smallest p': r8[k]['smallest p'],
                    'pooled': r8[k]['pooled']} for k in ('starts read', 'starts read, not set aside')})
    if 'R2' in R and 'R1a' in R and 'R1b' in R:
        first500 = set(mcc.run_order('parity')[:500])
        cnt = Counter()
        for run in ('R1a', 'R1b', 'R2'):
            for r in study.read_jsonl('%s.jsonl.gz' % run):
                if 'error' in r or r['index'] not in first500:
                    continue
                cnt[(run, 'n')] += 1
                cnt[(run, 'pair')] += int(sum(v[1] for v in r['pair_rounds'].values()) > 0)
        t1 = cnt[('R1a', 'pair')] + cnt[('R1b', 'pair')]
        t2 = cnt[('R2', 'pair')]
        add('PC12', 'R2: fewer growths with a pair under the holder weighting than take by take (first 500, 42 laws)',
            'holds' if t2 < t1 else 'fails', {'take by take (R1a + R1b)': [t1, cnt[('R1a', 'n')] + cnt[('R1b', 'n')]],
                                              'holder (R2)': [t2, cnt[('R2', 'n')]]})
    else:
        add('PC12', 'R2: fewer growths with a pair under the holder weighting', 'not run', {})
    trig = bool(conf_ok)
    rcc = S.get('Rcond_cases')

    def cond_verdict(run):
        if not trig:
            return 'not run (no confirmed case: not triggered)', {}
        if run not in S.get('cond_runs', {}):
            return 'not run (triggered)', {}
        if rcc is None:
            return 'not decided (confirmation of the conditional family not run)', {}
        mine = [c for c in rcc if c['run'] == run and c['family'] == 'claimed']
        confd = [c for c in mine if c['confirmation']['confirmed'] and not c['growth_has_failing_knot']]
        cs = S['cond_runs'][run]
        nums = {'growths read': cs['growths read'], 'not read': cs['not read, by reason'],
                'claimed cases passing the first stage': len(mine), 'confirmed': len(confd),
                'm_c (the conditional family)': S['Rcond']['m'],
                'confirmed cases': [(c['start'], c['law'], c['reading'], c['s'], c['rates1000']['q1'],
                                     c['rates1000']['q0'], c['rates1000']['qY'], c['rates1000']['qM'],
                                     c['rates1000']['qT'], c['confirmation'].get('way')) for c in confd]}
        return ('holds' if not confd else 'fails'), nums
    v, nums = cond_verdict('R5')
    add('PC13', 'R5, if run: no confirmed case under HOLD or STEPS-2, in the conditional family', v, nums)
    # PC14
    nae_fail = sum(L['knot test']['failing knots'] for run in ('R1c', 'R1d') for L in laws_of_run(S, run).values())
    par = Counter()
    for run in ('R1a', 'R1b', 'R2'):
        for lk, L in laws_of_run(S, run).items():
            for k, v in L['knot test']['classes (kind, parents (3 = 3+), took, implied, round)']:
                par[k[0]] += v
    r9 = S.get('R9')
    missed = r9['totals'].get('missed_by_last_round', 0) if r9 else None
    after = r9['totals'].get('failing_after_its_round', 0) if r9 else None
    ok = (nae_fail == 0) and par.get('join', 0) > 0 and sum(v for k, v in par.items() if k != 'join') == 0 and \
        (missed == 0 if r9 else True) and (after == 0 if r9 else True)
    add('PC14', 'Under not-all-equal no knot fails; under parity joins fail in the round they are made; R9 finds no '
                'failure the last-round test misses', ('holds' if ok else 'fails') + ('' if r9 else ' (R9 not run)'),
        {'not-all-equal failing knots': nae_fail, 'parity failing knots by kind': dict(par),
         'R9': r9 and r9['totals']})
    v, nums = cond_verdict('R6')
    add('PC15', 'R6, if run: no confirmed case with every pair either', v, nums)
    r0b = S.get('R0b')
    add('PC16', 'R0b: machinery passes at 100 and 1,000; planted arm 1 passes and is confirmed, arms 2 and 3 do '
                'not pass; no negative control is confirmed', 'not run' if not r0b else
        ('holds' if r0b['pass'] else 'fails'), r0b and {c['name']: c['pass'] for c in r0b['controls']})
    add('PC17', 'Reported, no prediction', 'reported', {})
    return P


def not_run(S):
    out = []
    times = S.get('run_times') or {}
    for run, (kl, tk, w, size) in RUNS.items():
        if run not in S['runs']:
            out.append('%s: not run.' % run)
            continue
        sz = (times.get(run) or {}).get('starts')
        if sz is not None and sz < size:
            out.append('%s: run on the first %d of its %d registered starts (a registered prefix); the rest not run.'
                       % (run, sz, size))
    for run, size in (('R8', 219), ('R9', None), ('R7', None)):
        t = times.get(run) or {}
        if t.get('starts') is not None and size and t['starts'] < size:
            out.append('%s: run on the first %d of its %d registered starts; the rest not run.' % (run, t['starts'], size))
    conf_ok = [c for c in (S.get('R3_cases') or []) if c['family'] == 'claimed' and c['confirmation']['confirmed']
               and not c['growth_has_failing_knot']]
    if not conf_ok:
        n8 = sum(r['rounds with more than eight pairs'] for rs in S['runs'].values() for r in rs['laws'].values())
        out.append('Not run: HOLD, STEPS-2, every pair. The negative is under RELEASE, MET and STEPS-1, with at most '
                   'eight pairs read a round; %d rounds had more. The drafter\'s scratch on the starts of three and four '
                   'knots (unreviewed, 6 rounds) saw no case met more often with Y under those swaps.' % n8)
        out.append('R4 (stage 2), R5 and R6: not run (no confirmed case of a claimed reading; no candidate).')
    else:
        for run in ('R5', 'R6'):
            if run not in S.get('cond_runs', {}):
                out.append('%s: triggered by %d confirmed cases of a claimed reading; not run.' % (run, len(conf_ok)))
            else:
                nr = S['cond_runs'][run]['not read, by reason']
                if nr:
                    out.append('%s: growths not read: %s (never a negative).' % (run, nr))
                t = (S.get('run_times') or {}).get(run) or {}
                if t.get('starts') is not None and t.get('registered starts') and t['starts'] < t['registered starts']:
                    out.append('%s: run on the first %d of its %d starts; the rest not run.' % (run, t['starts'],
                                                                                           t['registered starts']))
        out.append('R4 (stage 2): not triggered (no candidate, DC 5.1).')
    return out


def write_md(S):
    L = []
    w = L.append
    w('# MADE-COPIER-20261125-001C-E001: a copier by sampling, results')
    w('')
    w('Generated by `summarize.py` from the result files of this folder. Words are the frozen texts\'. Every rate names its '
      'weighting. "Not run" is never a negative. COPY-LAW(t) is the fold study\'s name for (FLOOR1, t, RELEASE), not a '
      'law of copying.')
    w('')
    w('## Predictions')
    w('')
    w('| # | Prediction | Verdict | Numbers |')
    w('| --- | --- | --- | --- |')
    for p in S['predictions']:
        num = json.dumps(p['numbers'], default=str)
        if len(num) > 400:
            num = num[:400] + ' ... (summary.json)'
        w('| %s | %s | %s | %s |' % (p['#'], p['prediction'], p['verdict'], num.replace('|', '/')))
    w('')
    w('## The main runs')
    w('')
    w('| Run | Starts run / registered | Wall minutes | Growths read | Not read (memory cap) | Growths with a pair | '
      'Growths with a case (claimed) | ... passing at 100 | ... confirmed |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    times = S.get('run_times') or {}
    for run, rs in S['runs'].items():
        cases = sum(r['rates']['claimed']['all']['case'] for r in rs['laws'].values())
        p100 = sum(r['rates']['claimed']['all']['passes_at_100'] for r in rs['laws'].values())
        conf = sum(r['rates']['claimed']['all']['confirmed'] for r in rs['laws'].values())
        pair = sum(sum(r['with a pair in rounds 1 to 4'].values()) for r in rs['laws'].values())
        t = times.get(run) or {}
        w('| %s | %s / %s | %s | %d | %d | %d | %d | %d | %d |' % (
            run, t.get('starts', '?'), RUNS[run][3], t.get('wall minutes', '?'), rs['growths read'],
            rs['growths not read (memory cap)'], pair, cases, p100, conf))
    w('')
    w('Cases are counted by growth and reading (a growth holding a case of a reading counts once for it).')
    w('')
    w('## Zero bounds, each law separately, at 0.95')
    w('')
    w('The bounded event (DC 4.5): a growth holding a case of a claimed reading (form, from both, values both from X) '
      'that passes at 100; where some pass and none is confirmed, a confirmed case. N: growths read (one a start, '
      'sample index 0). Census weighting: 3/N; labelled weighting: 3/N times max w / mean w over the starts read.')
    w('')
    w('| Run | Law | N (3/4/5 knots) | Cases | Pass at 100 | Confirmed | Census: all, 3, 4, 5 knots | Labelled: all |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for run, rs in S['runs'].items():
        for lk, r in rs['laws'].items():
            rr = r['rates']['claimed']
            ns = '/'.join(str(rr.get(st, {}).get('N', 0)) for st in ('3', '4', '5'))
            cb = ', '.join(fmt_pct(rr[st]['census']['zero_bound']) if st in rr else '—' for st in ('all', '3', '4', '5'))
            w('| %s | %s | %s | %d | %d | %d | %s | %s |' % (run, lk, ns, rr['all']['case'], rr['all']['passes_at_100'],
                                                       rr['all']['confirmed'], cb,
                                                       fmt_pct(rr['all']['labelled']['zero_bound'])))
    w('')
    w('## Cases that pass at 100 (first stage) and their confirmation (R3)')
    w('')
    if S.get('R3'):
        w('m (claimed readings) = %s; m\' (reported readings) = %s; runs read: %s.' % (S['R3']['m'], S['R3']["m'"],
                                                                                    S['R3']['runs read']))
        w('')
        w('| Run | Start | Law | Reading | s | At 100: q1, q0, qY | At 1,000: q1, q0, qY, qM, qT | Confirmed | Way |')
        w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
        for c in S['R3_cases']:
            a1, b1 = c['rates100'], c['rates1000']
            w('| %s | %s | %s | %s | %d | %s, %s, %s | %s, %s, %s, %s, %s | %s | %s |' % (
                c['run'], c['start'], c['law'], c['reading'], c['s'], a1['q1'], a1['q0'], a1['qY'], b1['q1'], b1['q0'],
                b1['qY'], b1['qM'], b1['qT'], c['confirmation']['confirmed'], c['confirmation'].get('way', '—')))
    else:
        w('R3 not run.')
    w('')
    w('## The conditional runs (R5, R6) and their family')
    w('')
    if S.get('cond_runs'):
        w('| Run | Law (and part) | Growths read | Not read | With a pair | Cases (claimed) | Passing the first stage | '
          'Confirmed |')
        w('| --- | --- | --- | --- | --- | --- | --- | --- |')
        for run, rs in S['cond_runs'].items():
            for lk, r in rs['laws'].items():
                rr = r['rates']['claimed']['all']
                w('| %s | %s | %d | %d | %d | %d | %d | %d |' % (run, lk, rr['N'], sum(r['not read (memory)'].values()),
                                                           sum(r['with a pair in rounds 1 to 4'].values()), rr['case'],
                                                           rr['passes_at_100'], rr['confirmed']))
        w('')
    if S.get('Rcond'):
        w('The conditional family: m_c = %s (claimed readings), level %s; reported readings m_c\' = %s.' % (
            S['Rcond']['m'], S['Rcond']['level_claimed'], S['Rcond']["m'"]))
        w('')
        w('| Run | Start | Law | Reading | s | First stage: q1, q0, qY | At 1,000: q1, q0, qY, qM, qT | Confirmed | Way |')
        w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
        for c in S['Rcond_cases']:
            a1, b1 = c['rates100'], c['rates1000']
            w('| %s | %s | %s | %s | %d | %s, %s, %s | %s, %s, %s, %s, %s | %s | %s |' % (
                c['run'], c['start'], c['law'], c['reading'], c['s'], a1['q1'], a1['q0'], a1['qY'], b1['q1'], b1['q0'],
                b1['qY'], b1['qM'], b1['qT'], c['confirmation']['confirmed'], c['confirmation'].get('way', '—')))
        w('')
    bn = S.get('R1d beyond its quarter (not counted)')
    if bn:
        w('**Not counted:** %s. Its %d growths hold %d cases; passing at 100 there, not counted: %s.' % (
            bn['note'], bn['growths'], len(bn['cases']),
            '; '.join('%s under %s, %s, s = %d (q1, q0, qY = %s)' % (c['start'], c['law'], c['reading'], c['s'],
                                                                     ', '.join(map(str, c['q100'])))
                      for c in bn['passing at 100 (not counted)']) or 'none'))
        w('')
    w('## Knot tests (DC 8)')
    w('')
    w('| Run | Law | Verdicts | Failing knots | Growths with a failing knot | Classes (kind, parents, took, implied, round): n |')
    w('| --- | --- | --- | --- | --- | --- |')
    for run, rs in S['runs'].items():
        for lk, r in rs['laws'].items():
            kt = r['knot test']
            if kt['failing knots'] or lk.startswith('FLOOR1/CANCEL-OFFSHOOT'):
                cl = '; '.join('%s: %d' % ('/'.join(map(str, k)), v) for k, v in
                               kt['classes (kind, parents (3 = 3+), took, implied, round)'][:6])
                w('| %s | %s | %d | %d | %d | %s |' % (run, lk, kt['verdicts'], kt['failing knots'],
                                                      kt['growths with a failing knot'], cl))
    w('')
    if S.get('R9'):
        w('R9 (every knot at every round, R1a\'s and R1b\'s growths of the starts of three and four knots): %s.' %
          json.dumps(S['R9']['totals']))
        w('')
    w('## The renaming checks')
    w('')
    if S.get('R7'):
        r7 = S['R7']
        w('R7: %d checks, %d with every renaming equal, %d with a single history (no check of takes); by label: %s.' %
          (r7['checks'], r7['all_equal'], r7['single_history'], json.dumps(r7['by_label'])))
    else:
        w('R7: not run.')
    w('')
    if S.get('R8'):
        for k in ('starts read', 'starts read, not set aside'):
            x = S['R8'][k]
            w('R8 (%s: %s): %d of 210 tests rejected at 0.05/210 (smallest p %.3g); pooled, %d of 5 rejected at '
              '0.05/5.' % (k, x.get('starts'), x['rejections'], x['smallest p'], x['pooled_rejections']))
    else:
        w('R8: not run.')
    w('')
    w('## The gate and the controls')
    w('')
    if S.get('R0'):
        w('R0: %s (census, order, set-aside flags and weights equal; round-0 ties: %s; the 96 cases: %s, difference '
          'classes %s; the two values comparisons: %s).' % (
              'passed' if S['R0']['pass'] else 'differences', S['R0']['nae_round0_ties']['pass'],
              S['R0']['cases']['pass'], json.dumps(S['R0']['cases']['difference classes']),
              S['R0']['values_comparisons']['pass']))
    if S.get('R0b'):
        w('')
        w('R0b: %s.' % ('passed' if S['R0b']['pass'] else 'a control failed'))
        w('')
        w('| Control | Must | Passed |')
        w('| --- | --- | --- |')
        for c in S['R0b']['controls']:
            w('| %s | %s | %s |' % (c['name'], c.get('must', 'pass at 100 and at 1,000'), c['pass']))
    w('')
    w('## Not run')
    w('')
    for line in S.get('not_run', []):
        w('- ' + line)
    w('')
    open(study.out_path('summary.md'), 'w').write('\n'.join(L) + '\n')
    study.log('wrote summary.md')


if __name__ == '__main__':
    main()
