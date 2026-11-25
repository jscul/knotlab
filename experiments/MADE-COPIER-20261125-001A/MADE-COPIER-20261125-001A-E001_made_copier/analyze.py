"""Every prediction's verdict, with its numbers, from the run outputs; writes summary.json (report.py writes summary.md).

usage: python -B analyze.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

FAMS = [('made-3 to made-6', mc.CLASS_MADE), ('Y present from round 0, five members', mc.CLASS_START),
        ('made-2 and the same start with names exchanged', ['made-2', 'made-2-exchanged']),
        ('two-22', ['ystart-two-22'])]
GROUPS = ('COPY-LAW', 'CAP-3', 'FBP')
CONTROLS = ('made-2', 'made-2-exchanged', 'ystart-two-22')


def bl(base):
    """'COPY-LAW(OFFSHOOT)' -> 'COPY-LAW(CANCEL-OFFSHOOT)', as P names it."""
    nm, t = base.split('(')
    return '%s(CANCEL-%s' % (nm, t)


def group(base):
    return base.split('(')[0]


def lawname(j):
    return '%s, %s(%s), %s' % (bl(j['base']), j['take'], j['choice'], 'parity' if j['knot_law'] == 'parity'
                               else 'not-all-equal')


def load(name):
    p = C.out_path(name)
    if not os.path.exists(p):
        return None
    if name.endswith('.json'):
        return json.load(open(p))
    return C.read_jsonl(name)


def verdict(ok):
    return 'holds' if ok else 'fails'


# ------------------------------------------------------------------------------------------------------- the gate
def gate(S):
    fold, ties, same = load('gate_fold.json'), load('gate_ties.json'), load('gate_same.json')
    ctr, rec, third = load('gate_controls.json'), load('gate_record.json'), load('gate_third.json')
    tests = load('test_mc.json')
    ok0 = (not fold['mismatches'] and fold['runs'] == 384 and ties['n_mismatches'] == 0 and
           ties['counts']['structures parity'] == 600 and ties['counts']['structures nae'] == 600 and
           same['n_mismatches'] == 0)
    S['P0'] = {'verdict': verdict(ok0), 'numbers': {
        'runs equal to the fold engine': '%d of %d' % (fold['runs'] - len(fold['mismatches']), fold['runs']),
        'drawn structures, ties against every assignment': '600 under each knot law, %d mismatches' %
        ties['n_mismatches'], 'tie classes found (parity, not-all-equal)': [ties['counts']['classes parity'],
                                                                          ties['counts']['classes nae']],
        'frozen (parity)': ties['counts']['frozen parity'],
        'sameness and renamings against brute force': same['counts'], 'mismatches': same['n_mismatches'],
        'placed positives': same['positives'], 'unit tests of the readings': '%d of %d pass' % (
            sum(1 for k, v in tests.items() if not k.startswith('_') and v['ok']),
            sum(1 for k in tests if not k.startswith('_')))}}
    S['P14'] = {'verdict': ctr['P14'], 'numbers': {'two-knot start, no taking rule, rounds 2 to 7':
                                                   ctr['two-knot'], 'placed by hand': ctr['placed']}}
    S['P4'] = {'verdict': rec['P4'], 'numbers': {'checks': rec['checks'], 'parity counts': rec['parity']['counts'],
                                                 'not-all-equal counts': rec['nae']['counts']}}
    rows = third['rows']
    no_tie = all(not r[k]['classes'] and not r[k]['frozen'] and not r[k]['unsat'] for r in rows
                 for k in ('parity', 'nae'))
    S['_third'] = {'starts': len(rows), 'no tie or frozen distinction under either knot law': no_tie,
                   'e has three holders in all': third['e has three holders in all']}


# -------------------------------------------------------------------------------------------------------- run 1
def run1(S):
    R = load('run1.jsonl.gz') or []
    S['_run1'] = {'runs': len(R), 'errors': [r for r in R if 'error' in r][:3]}
    bad, exc = [], defaultdict(Counter)
    for r in R:
        if 'error' in r or r['base'].split('(')[0] != 'COPY-LAW' or r['take'] not in ('MET', 'STEPS-1', 'STEPS-2'):
            continue
        bad += [dict(b, law=r['law'], start=r['start']) for b in r['fresh_bad']]
        for k, v in r['fresh_exceptions'].items():
            exc[r['take']][k] += v
    n1 = sum(1 for r in R if 'error' not in r and r['base'].startswith('COPY-LAW') and
             r['take'] in ('MET', 'STEPS-1', 'STEPS-2'))
    S['P1'] = {'verdict': verdict(not bad), 'numbers': {
        'runs read (COPY-LAW(t); MET, STEPS-1, STEPS-2; four rules; both knot laws; three starts)': n1,
        'births with another count': len(bad), 'first of them': bad[:5],
        'the allowed exceptions, births (kind | fresh count)': {k: dict(v) for k, v in exc.items()}}}
    # P3
    counts = mc.STARTS['counts for P3']['counts']
    viol, early, cmp_ = [], Counter(), []
    for r in R:
        if 'error' in r:
            continue
        g = group(r['base'])
        if g == 'FBP':
            continue
        if r['take'] in ('Q', 'MET', 'STEPS-1', 'STEPS-2'):
            for t, n in enumerate(r['N']):
                if t >= 3 and n:
                    viol.append({'law': r['law'], 'start': r['start'], 't': t, 'N': n})
                if t < 3 and n:
                    early[(r['start'], r['take'], t, n)] += 1
        elif r['take'] is None:
            key = '%s|%s-%s' % (r['start'], 'FLOOR1' if g == 'COPY-LAW' else 'CAP3', r['base'].split('(')[1][:-1])
            want = counts[key][:len(r['N'])]
            cmp_.append({'start': r['start'], 'base': bl(r['base']), 'knot law': r['knot_law'], 'N': r['N'],
                         'starts.json': counts[key], 'equal': r['N'] == want, 'rounds': r['rounds']})
    eq_par = all(c['equal'] for c in cmp_ if c['knot law'] == 'parity')
    S['P3'] = {'verdict': verdict(not viol and eq_par), 'numbers': {
        'parts the same as the two-knot part after a round t >= 3 under a taking rule': len(viol),
        'first of them': viol[:5],
        'parts after rounds 0 to 2 under a taking rule (start, rule, round, count: runs)':
            {'%s|%s|t=%d|N=%d' % k: v for k, v in sorted(early.items())},
        'no taking rule, parity, equal to starts.json': '%d of %d' % (
            sum(c['equal'] for c in cmp_ if c['knot law'] == 'parity'),
            sum(1 for c in cmp_ if c['knot law'] == 'parity')),
        'no taking rule, not-all-equal, equal to starts.json (reported)': '%d of %d' % (
            sum(c['equal'] for c in cmp_ if c['knot law'] == 'nae'), sum(1 for c in cmp_ if c['knot law'] == 'nae')),
        'unequal': [c for c in cmp_ if not c['equal']][:6]}}
    fbp = [(r['start'], r['take'], r['choice'], r['knot_law'], [t for t, n in enumerate(r['N']) if n and t >= 3])
           for r in R if 'error' not in r and group(r['base']) == 'FBP' and r['take'] and
           any(n and t >= 3 for t, n in enumerate(r['N']))]
    S['_run1']['FBP(t) runs with a part the same as the two-knot part after a round >= 3 (reported)'] = {
        'runs': len(fbp), 'of': sum(1 for r in R if 'error' not in r and group(r['base']) == 'FBP' and r['take']),
        'first': fbp[:6]}
    return R


# ---------------------------------------------------------------------------------------------- knot tests (P10)
def kt_rows(R1, R2, R3, R5):
    """(run, label, knot law, brief) for every knot test of runs 1 to 5."""
    out = []
    for r in R1:
        if 'error' not in r:
            out.append((1, '%s %s' % (r['start'], r['law']), r['knot_law'], r['knot_tests']))
    for r in R2:
        kl = r['job']['knot_law']
        for name, d in r.get('designs', {}).items():
            if 'knot_tests_A' not in d:
                continue
            out.append((2, '%s %s run A' % (name, r['law']), kl, d['knot_tests_A']))
            for k, v in d['knot_tests_cmp'].items():
                out.append((2, '%s %s %s' % (name, r['law'], k), kl, v))
            for k in ('X_alone', 'Y_alone'):
                if k in d:
                    out.append((2, '%s %s %s' % (name, r['law'], k), kl, d[k]['knot_tests']))
    for r in R3:
        if 'knot_tests_A' in r:
            out.append((3, '%s %s run A' % (r['job']['start'], r.get('law')), r['job']['knot_law'],
                        r['knot_tests_A']))
            for p_ in r.get('pairs', []):
                for k, v in p_.get('knot_tests_cmp', {}).items():
                    out.append((3, '%s %s pair %s %s' % (r['job']['start'], r.get('law'), p_['X'], k),
                                r['job']['knot_law'], v))
    return out


def p10(S, R1, R2, R3, R4, R4rep, R5):
    rows = kt_rows(R1, R2, R3, R5)
    nae_fail = [(r, l, b['n_fails']) for r, l, kl, b in rows if kl == 'nae' and b['n_fails']]
    par = [(r, l, b) for r, l, kl, b in rows if kl == 'parity' and b['n_fails']]
    kinds = Counter()
    unsure = []
    for r, l, b in par:
        if 'fail_kinds' in b:
            kinds.update(b['fail_kinds'])
        else:
            kinds.update(Counter(f['kind'] for f in b['fails']))
            if b['n_fails'] > len(b['fails']):
                unsure.append(l)
    disagree = sum(b['n_disagree'] for _, _, _, b in rows)
    verdicts = Counter()
    for r, l, kl, b in rows:
        verdicts[kl] += b['verdicts']
    # run 4: every replayed list and every history with two tested at every round
    r4_fail = sum(1 for x in R4rep['rows'] if not x['every knot passes'])
    r4_hist = sum(r['counts'].get('histories with two of a place of Y made by X', 0) for r in R4 if 'counts' in r)
    r4_pass = sum(r['counts'].get('  of them, every knot passing', 0) for r in R4 if 'counts' in r)
    # run 5
    r5 = {'nae fails': 0, 'parity fails': 0, 'runs': 0}
    for src in R5:
        for x in src:
            for row in _r5_rows(x):
                if row.get('knot_fails') is None:
                    continue
                r5['runs'] += 1
                if row['knot_fails']:
                    r5['parity fails' if row.get('kl') == 'parity' else 'nae fails'] += 1
    rf = load('run4_fails.json')
    r4k = Counter()
    r4kinds = Counter()
    r4same = None
    if rf:
        r4same = True
        by = {r['design']: r for r in R4 if r.get('base') == 'COPY-LAW(OFFSHOOT)' and r.get('knot_law') == 'parity'}
        for x in rf['rows']:
            for k, v in x['counts'].items():
                r4k[k] += v
            r4kinds.update(x['kinds of failing knots by (kind, inputs, fresh)'])
            want = by.get(x['design'], {}).get('counts', {}).get('histories with two of a place of Y made by X', 0)
            if x['counts'].get('histories with two of a place of Y made by X', 0) != want:
                r4same = False
    ok = (not nae_fail and set(kinds) <= {'join'} and not disagree and not unsure and
          all(k.startswith('join') for k in r4kinds) and not r4k.get('disagreements'))
    S['P10'] = {'verdict': verdict(ok), 'numbers': {
        'knot tests read in runs 1 to 3 (verdicts, parity / not-all-equal)': [verdicts['parity'], verdicts['nae']],
        'tests with a failing knot under not-all-equal': len(nae_fail),
        'tests with a failing knot under parity': len(par), 'failing knots by kind (parity)': dict(kinds),
        'parity failures (first 8)': [{'run': r, 'where': l, 'fails': b['fails'][:4], 'n': b['n_fails']}
                                      for r, l, b in par[:8]],
        'method disagreements': disagree, 'tests with more failures than listed (kind not read)': unsure,
        'run 4: replayed lists with a failing knot': r4_fail,
        'run 4: histories with two of a place of Y made by X / of them every knot passing': [r4_hist, r4_pass],
        'run 5: runs read / with a failing knot (parity, not-all-equal)': [r5['runs'], r5['parity fails'],
                                                                            r5['nae fails']],
        'run 4, drawn again (dev 50): counts': dict(r4k), 'run 4: failing knots by kind, inputs and fresh count':
            dict(r4kinds), 'run 4 drawn again gives run 4\'s histories with two': r4same}}


def _r5_rows(x):
    """Rows of run 5 outputs with 'knot_fails' and the knot law."""
    out = []
    if 'swaps' in x and 'case' in x:
        for k, v in x['swaps'].items():
            if isinstance(v, dict) and 'knot_fails' in v:
                out.append(dict(knot_fails=v['knot_fails'], kl='parity' if '/parity' in v.get('law', '') else 'nae'))
    if 'designs' in x:
        for v in x['designs'].values():
            if 'knot_fails' in v:
                out.append(dict(knot_fails=v['knot_fails'], kl=x['job']['knot_law']))
    if 'rows' in x and 'job' in x:
        kl = x['job'].get('knot_law', 'parity')
        for r in x['rows']:
            for k in ('with Z', 'Z barred'):
                if isinstance(r.get(k), dict) and 'knot_fails' in r[k]:
                    out.append(dict(knot_fails=r[k]['knot_fails'], kl=kl))
    if 'swaps' in x and 'index' in x:
        for v in x['swaps'].values():
            if 'knot_fails' in v:
                out.append(dict(knot_fails=v['knot_fails'], kl='parity' if '/parity' in v['law'] else 'nae'))
    return out


# -------------------------------------------------------------------------------------------------- P2 (run 6)
def p2(S, R1, R2, R3, R4, R5, R6):
    n, bad = Counter(), []
    for r in R1:
        if 'error' not in r and r['knot_law'] == 'nae':
            n['run 1'] += 1
            if r['ties_made']['n_classes_with_made']:
                bad.append(('run 1', r['law'], r['start']))
    for r in R2:
        if r['job']['knot_law'] != 'nae':
            continue
        for name, d in r.get('designs', {}).items():
            if 'per_round' in d:
                n['run 2, run A, every round'] += 1
                if any(x['made_tied'] for x in d['per_round']):
                    bad.append(('run 2', r['law'], name))
    for r in R6:
        for name, row in (r.get('rows') or {}).items() if isinstance(r.get('rows'), dict) else []:
            for k, v in row.items():
                n['run 6 (run 2: every run, last round)'] += 1
                if v['n']:
                    bad.append(('run 6', r['law'], name, k, v['classes'][:2]))
        if isinstance(r.get('rows'), list):
            for row in r['rows']:
                for k, v in row.items():
                    if isinstance(v, dict) and 'n' in v:
                        n['run 6 (run 3: comparison runs of every pair, last round)'] += 1
                        if v['n']:
                            bad.append(('run 6', r['law'], row['X'], k))
    for r in R3:
        if r['job']['knot_law'] == 'nae' and 'ties_made' in r:
            n['run 3, run A, last round'] += 1
            if r['ties_made']:
                bad.append(('run 3', r.get('law'), r['job']['start']))
    for r in R4:
        if r.get('knot_law') == 'nae':
            n['run 4, histories'] += r['counts'].get('histories', 0)
            if r['counts'].get('histories with a tie class (not-all-equal)'):
                bad.append(('run 4', r['law'], r['counts']['histories with a tie class (not-all-equal)']))
    for src in R5:
        for x in src:
            for t in _nae_ties(x):
                n['run 5'] += 1
                if t['n']:
                    bad.append(('run 5', t))
    third = S['_third']
    ok = not bad and third['no tie or frozen distinction under either knot law'] and third['starts'] == 60
    S['P2'] = {'verdict': verdict(ok), 'numbers': {'not-all-equal runs and histories read': dict(n),
                                                   'with a tie class containing a made distinction': len(bad),
                                                   'first of them': bad[:6], 'the third-pattern starts': third}}


def _nae_ties(x):
    out = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'nae_made_ties' and v is not None:
                    out.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(x)
    return out


# -------------------------------------------------------------------------------------------------------- run 2
def run2_rows(R2):
    """(job, design, row) for every design of every law of run 2."""
    out = []
    for r in R2:
        for name, d in r.get('designs', {}).items():
            out.append((r['job'], name, d, r))
    return out


def cases2(rows):
    out = []
    for j, name, d, r in rows:
        for reading, key in (('values', 'Y_by_X_some'), ('form', 'two_by_X_some'), ('built', 'two_by_X_some')):
            if d.get(reading, {}).get(key):
                out.append((j, name, d, reading))
    return out


def p5_p6(S, rows):
    ck = load('check_p5.json')
    built = [(lawname(j), name) for j, name, d, r in rows if group(j['base']) == 'COPY-LAW' and
             d.get('built', {}).get('any_renaming_some')]
    n_built = sum(1 for j, name, d, r in rows if group(j['base']) == 'COPY-LAW' and 'built' in d)
    S['P5'] = {'verdict': verdict(ck is not None and ck['P5 first clause'] == 'holds' and not built),
               'numbers': {'parts the same as a member of the class with a member made after round s':
                           ck and ck['parts read'], 'of them with a made member that is not an offshoot of a start knot':
                           ck and ck['parts failing'], 'parts by design, member and taking rule':
                           ck and ck['parts by design, member and taking rule'],
                           'runs A under COPY-LAW(t) read for renamings of Y\'s knots': n_built,
                           'with a renaming among the made knots': len(built)}}
    vals = [(j, name, d) for j, name, d, r in rows if d.get('values', {}).get('Y_by_X_some')]
    main = [(j, name, d) for j, name, d in vals if name != 'made-2-exchanged']
    want = [x for x in main if x[1] == 'ystart-three-222' and x[0]['base'] == 'COPY-LAW(OFFSHOOT)' and
            x[0]['take'] == 'MET' and x[0]['choice'] == 'NEWEST' and x[0]['knot_law'] == 'parity']
    ok = len(main) == 1 and len(want) == 1
    det = None
    if want:
        d = want[0][2]
        c = next(c for c in d['values']['cases'] if c['made_by_X'])
        det = {'two': c['two'], 'v': c['v'], 'descents': c['descents'], 'round': c['t'],
               'holders of v after round 0 and at the round seen': [None, c['holders_v_t']],
               'v a place of a member of Y': True, 'every knot passes': d['knot_tests_A']['n_fails'] == 0,
               'B(i)': d['B(i)']['values']['cases'][:1], 'B_X has two by Y only': d['B_X']['values']['Y_own_some'],
               'two users': d.get('two_users')}
        ok = ok and sorted(c['two']) == [52, 53] and c['v'] == 16 and c['descents'] == ['X only', 'X only']
    S['P6'] = {'verdict': verdict(ok), 'numbers': {
        'runs with two of a place of Y made by X (stated rules; made-2 to made-6 and the six designs with Y present '
        'from round 0)': ['%s: %s' % (name, lawname(j)) for j, name, d in main],
        'made-2-exchanged (reported)': ['%s' % lawname(j) for j, name, d in vals if name == 'made-2-exchanged'],
        'the case': det, 'runs read': sum(1 for j, name, d, r in rows if 'values' in d)}}
    return want


# ------------------------------------------------------------------------------------------------- P7 (run 5)
def p7(S, R5c):
    row = next((x for x in R5c if x['case']['design'] == 'ystart-three-222' and x['case']['reading'] == 'values'
                and x['case']['base'] == 'COPY-LAW(OFFSHOOT)' and x['case']['choice'] == 'NEWEST'), None)
    if row is None:
        for k in ('P7a', 'P7b', 'P7c', 'P7d'):
            S[k] = {'verdict': 'not read', 'numbers': {}}
        return
    sw = row['swaps']
    sv = {k: (v['survives'], v['round']) for k, v in sw.items()}
    S['P7a'] = {'verdict': verdict(sw['demand before the takes']['survives'] and sw['HOLD']['survives']),
                'numbers': {k: sv[k] for k in ('demand before the takes', 'HOLD')}}
    rules = [k for k in sw if k.startswith('rule ')]
    S['P7b'] = {'verdict': verdict(not any(sw[k]['survives'] for k in rules)), 'numbers': {k: sv[k] for k in rules}}
    rn = [k for k in sw if k.startswith('renaming ')]
    S['P7c'] = {'verdict': verdict(not any(sw[k]['survives'] for k in rn)), 'numbers': {k: sv[k] for k in rn}}
    oth = [k for k in sw if k.startswith('base law') or k.startswith('STEPS-1') or k in (
        'order of births reversed', 'knot law')]
    S['P7d'] = {'verdict': 'reported', 'numbers': {k: sv[k] for k in oth},
                'note': 'seen: lost under each'}


# ------------------------------------------------------------------------------------------- P8, P9, PO8 (run 4)
def run4(S, R4, R4rep):
    S['P8a'] = {'verdict': R4rep['P8a'], 'numbers': {
        'lists': R4rep['lists'], 'give the two': sum(r['gives the two'] for r in R4rep['rows']),
        'every knot passing': sum(r['every knot passes'] for r in R4rep['rows']),
        'two seen earlier than the listed round': [r['index'] for r in R4rep['rows'] if r['two seen earlier at']],
        'holders of v as listed': sum(r['holders of v'] == r['listed holders of v'] for r in R4rep['rows']),
        'found by the full basis as listed': sum(sorted(r['found by the full basis']) == sorted(r['listed two'])
                                                 for r in R4rep['rows'])}}
    tab, p9, guard = {}, {}, {}
    for r in R4:
        if 'counts' not in r:
            continue
        key = '%s | %s | %s' % (r['design'], bl(r['base']), r['knot_law'])
        c = r['counts']
        tab[key] = {'mode': r['mode'], 'histories': c.get('histories'),
                    'with two of a place of Y made by X': c.get('histories with two of a place of Y made by X', 0),
                    'of them every knot passing': c.get('  of them, every knot passing', 0),
                    'stopped by the guard': c.get('stopped by the guard', 0)}
        if r['base'] == 'COPY-LAW(OFFSHOOT)' and r['knot_law'] == 'parity':
            p9[r['design']] = {k[len('histories with two: '):]: v for k, v in c.items()
                               if k.startswith('histories with two: ')}
            p9[r['design']]['histories'] = c.get('histories')
    pooled = Counter()
    for v in p9.values():
        for k, n in v.items():
            if k != 'histories':
                pooled[k] += n
    S['P8b'] = {'verdict': 'reported', 'numbers': tab,
                'note': 'seen: under COPY-LAW(CANCEL-OFFSHOOT) every design, in 5,000 draws: made-3 4, made-4 34, '
                        'made-5 30, made-6 25; one-2 26, one-3 10, two-23 13, two-33 11, three-222 4; made-2 57, two-22 '
                        '23; none under CAP-3(t); CAP-3(CANCEL-OFFSHOOT) on made-4, made-5, made-6 mostly stopped '
                        'by the guard (4,867, 5,000 and 5,000 of 5,000)'}
    S['P9'] = {'verdict': 'reported', 'numbers': {'per design': p9, 'pooled': dict(pooled)}}
    po8 = {}
    every_ok = True
    for r in R4:
        if r.get('design') != 'made-2' or 'states_made2' not in r:
            continue
        st = {}
        for k, v in r['states_made2'].items():
            a, b = eval(k)
            st[(a, b)] = v
        exch = {(b, a): v for (a, b), v in st.items()}
        same = st == exch
        po8['%s | %s' % (bl(r['base']), r['knot_law'])] = {
            'mode': r['mode'], 'counts': {'%s / %s' % k: v for k, v in sorted(st.items())},
            'unchanged when X and Y are exchanged': same}
        if r['mode'] == 'every history' and not same:
            every_ok = False
    S['PO8'] = {'verdict': verdict(every_ok), 'numbers': po8}


# ------------------------------------------------------------------------------------------------- C, CF, POA
def renaming_survival(R5c):
    out = {}
    for x in R5c:
        c = x['case']
        key = (c['design'], c['base'], c['take'], c['choice'], c['knot_law'], c['reading'])
        regs = {k[len('renaming '):]: v['survives'] for k, v in x.get('swaps', {}).items()
                if k.startswith('renaming ')}
        out[key] = {'every registered renaming': x.get('survives every registered renaming'), 'by renaming': regs,
                    'swaps': {k: v['survives'] for k, v in x.get('swaps', {}).items()}}
    return out


def census(rows):
    """P13: runs of the form arm's laws under parity with a part the same as the member's Y (any descent; and one with
    every member descended from X only), in the runs of the member's family, its control included."""
    cen = {}
    for fam, members, designs in (('made', mc.CLASS_MADE, mc.DESIGNS_MADE),
                                  ('ystart', mc.CLASS_START, mc.DESIGNS_YSTART)):
        n_runs = 0
        anyp, xonly = Counter(), Counter()
        for j, name, d, r in rows:
            if (name not in designs or group(j['base']) not in ('CAP-3', 'FBP') or j['knot_law'] != 'parity'
                    or 'parts_same_as_member' not in d):
                continue
            n_runs += 1
            for m in members:
                per = d['parts_same_as_member'].get(m, [])
                if any(sum(c.values()) for c in per):
                    anyp[m] += 1
                if any(c.get('X only', 0) for c in per):
                    xonly[m] += 1
        cen[fam] = {'runs': n_runs, 'members made': {m: anyp[m] for m in members},
                    'by descent from X only': {m: xonly[m] for m in members}}
    # not-all-equal against parity, run by run
    by = {}
    for j, name, d, r in rows:
        if group(j['base']) in ('CAP-3', 'FBP') and 'parts_same_as_member' in d and name in (
                mc.DESIGNS_MADE + mc.DESIGNS_YSTART):
            by[(name, j['base'], j['take'], j['choice'], j['knot_law'])] = (d['parts_same_as_member'],
                                                                           d['form'])
    pairs = [(k, by[k], by.get(k[:4] + ('parity',))) for k in by if k[4] == 'nae']
    eq = sum(1 for k, a, b in pairs if b is not None and a == b)
    cen['not-all-equal equal to parity, run by run'] = '%d of %d' % (eq, len(pairs))
    return cen


def copier(S, rows, R5c, R5f):
    surv = renaming_survival(R5c)
    cen = census(rows)
    form_class = {'made': [m for m in mc.CLASS_MADE if cen['made']['members made'][m]],
                  'ystart': [m for m in mc.CLASS_START if cen['ystart']['members made'][m]]}
    dropped = [m for m in mc.CLASS_START if not cen['ystart']['members made'][m]] + \
        [m for m in mc.CLASS_MADE if not cen['made']['members made'][m]]
    ok13 = (set(form_class['made']) == set(mc.CLASS_MADE) and
            set(form_class['ystart']) == {'ystart-one-2', 'ystart-one-3', 'ystart-three-222'})
    S['P13'] = {'verdict': verdict(ok13), 'numbers': cen, 'the form classes': form_class, 'dropped': dropped,
                'note': 'seen: made family (240 runs) made-3 47, made-4 13, made-5 6, made-6 11; Y present from '
                        'round 0 (288 runs) one-2 31, one-3 1, three-222 38, two-23 0, two-33 0; from X only: 46, 13, '
                        '6, 11; 2, 0, 3; not-all-equal equal to parity in 528 of 528'}
    by = {(j['base'], j['take'], j['choice'], j['knot_law'], name): d for j, name, d, r in rows}
    # C(r, b): values, MET, parity, b in COPY-LAW(t), CAP-3(t)
    C_tab = {}
    for fam, members in (('X made', mc.CLASS_MADE), ('X a start pattern', mc.CLASS_START)):
        for b in mc.BASES_COPY + mc.BASES_CAP3:
            for r_ in mc.RULES:
                before, after = [], []
                for m in members:
                    d = by.get((b, 'MET', r_, 'parity', m))
                    if d and d.get('values', {}).get('Y_by_X_some'):
                        before.append(m)
                        sv = surv.get((m, b, 'MET', r_, 'parity', 'values'))
                        if sv and sv['every registered renaming']:
                            after.append(m)
                C_tab['%s | %s | MET(%s)' % (fam, bl(b), r_)] = {'members with two before the renamings': before,
                                                                 'surviving every registered renaming': after,
                                                                 'of': len(members)}
    holdsC = [k for k, v in C_tab.items() if len(v['surviving every registered renaming']) == v['of']]
    S['P11'] = {'verdict': verdict(not holdsC), 'numbers': {
        'C(r, b) holds for': holdsC,
        'with a member before the renamings': {k: v['members with two before the renamings'] for k, v in
                                               C_tab.items() if v['members with two before the renamings']},
        'with a member after the renamings': {k: v['surviving every registered renaming'] for k, v in
                                              C_tab.items() if v['surviving every registered renaming']},
        'laws and rules read': len(C_tab)},
        'note': 'seen: for X a start pattern, C(NEWEST, COPY-LAW(CANCEL-OFFSHOOT)) holds for 1 of 5 members before '
                'the renamings and for none after; every other rule and base law 0; X made 0 of 4'}
    # CF(r, b): form, MET, b in CAP-3(t), FBP(t); and STEPS-1 reported
    CF_tab, cases_form = {}, []
    for fam, key in (('X made', 'made'), ('X a start pattern', 'ystart')):
        members = form_class[key]
        for take in ('MET', 'STEPS-1'):
            for b in mc.BASES_CAP3 + mc.BASES_FBP:
                for r_ in mc.RULES:
                    for kl in ('parity', 'nae'):
                        two, full = [], []
                        for m in members:
                            d = by.get((b, take, r_, kl, m))
                            if not d or not d.get('form', {}).get('two_by_X_some'):
                                continue
                            two.append(m)
                            # condition 2: fewer than two of every other member after every round read, and the run
                            # with that member has two of it made by X
                            c2a = all(sum(c.values()) < 2 for o in members if o != m
                                      for c in d['parts_same_as_member'].get(o, []))
                            c2b = all((by.get((b, take, r_, kl, o)) or {}).get('form', {}).get('two_by_X_some')
                                      for o in members if o != m)
                            sv = surv.get((m, b, take, r_, kl, 'form'))
                            xa = d.get('X_alone', {}).get('parts_same_as_Y', [])
                            x_own = any(c.get('X only', 0) >= 2 for c in xa)
                            cases_form.append({'design': m, 'law': '%s, %s(%s), %s' % (bl(b), take, r_, kl),
                                               'round': d['form']['two_by_X_some'],
                                               'condition 2, fewer than two of every other member': c2a,
                                               'condition 2, every other member has two in its own run': c2b,
                                               'passes the registered renamings': sv and
                                               sv['every registered renaming'],
                                               'renamings': sv and sv['by renaming'],
                                               'X alone has two of Y (X\'s own course)': x_own,
                                               'B(i) has two': bool(d['B(i)']['form'].get('two_by_X_some')),
                                               'X\'s course with Y barred first differs at': d['X_course']['differs'],
                                               'X alone first differs at': d.get('X_alone', {}).get(
                                                   'X course differs from X alone at'),
                                               'in the run with each other member, the most parts the same as this Y':
                                               {o: max([sum(c.values()) for c in (by.get((b, take, r_, kl, o)) or {}).get(
                                                   'parts_same_as_member', {}).get(m, [])] or [0])
                                                for o in members if o != m},
                                               'parts the same as each other member, by round':
                                               {o: d['parts_same_as_member'].get(o) for o in members if o != m}})
                            if c2a and c2b and sv and sv['every registered renaming']:
                                full.append(m)
                        CF_tab['%s | %s | %s(%s) | %s' % (fam, bl(b), take, r_, kl)] = {
                            'two before the renamings': two, 'a copier for': full, 'of': len(members)}
    holdsCF = [k for k, v in CF_tab.items() if '| MET(' in k and v['of'] and len(v['a copier for']) == v['of']]
    S['P12'] = {'verdict': verdict(not holdsCF), 'numbers': {
        'CF(r, b) holds for (MET)': holdsCF,
        'laws with two parts the same as Y made by X only (MET)': {k: v['two before the renamings'] for k, v in
                                                                   CF_tab.items() if v['two before the renamings']
                                                                   and '| MET(' in k},
        'under STEPS-1 (reported)': {k: v['two before the renamings'] for k, v in CF_tab.items()
                                     if v['two before the renamings'] and '| STEPS-1(' in k},
        'the cases': cases_form},
        'note': 'seen: one case under MET, made-4, FBP(CANCEL-OFFSHOOT), MET(BY-COUNT) (each knot law): there with '
                'this Y and not in X alone, a copier for no other member, lost under renaming (survives n4, lost '
                'under n1 and n3); under STEPS-1 two cases that are X\'s own course'}
    # POA (i)
    some = [k for k, v in C_tab.items() if v['surviving every registered renaming']] + \
        [k for k, v in CF_tab.items() if v['a copier for'] and '| MET(' in k]
    whole = holdsC + holdsCF
    if whole:
        outcome = 'a copier for a whole registered class: overturned for that class'
    elif some:
        outcome = 'a copier for some members of the class and not all'
    else:
        outcome = 'no copier at all'
    S['POA'] = {'verdict': 'only supported' if not whole else 'overturned', 'numbers': {
        '(i)': outcome, 'a copier for some members (law and rule: members)': {k: (
            C_tab.get(k, {}).get('surviving every registered renaming') or CF_tab.get(k, {}).get('a copier for'))
            for k in some}},
        'note': 'seen: (i) no copier at all; readings (ii) to (iv) are PO5, PO6, PO9, PO10, never called support for '
                'his second sentence'}
    return form_class, cases_form


# ------------------------------------------------------------------------------------------------ the owner's arm
def arm(S, rows):
    tab = {}
    allrow = Counter()
    ways, ways_m = Counter(), Counter()
    tk_x, tk_y, tk_x_nc = Counter(), Counter(), Counter()
    unconf, unconf_take = 0, 0
    Tdist = Counter()
    members_left = 0
    ii, iirev, iii, iiirev = [], [], [], []
    x_alone = Counter()
    for fam, designs in FAMS:
        for g in GROUPS:
            c = Counter()
            for j, name, d, r in rows:
                if name not in designs or group(j['base']) != g or 'X_course' not in d:
                    continue
                c['runs'] += 1
                cx, cy = d['X_course'], d['Y_course']
                if cx['differs'] is not None:
                    c['X differs'] += 1
                    c['X differs (meeting)'] += cx.get('confirmed') == 'through a meeting'
                if cy['differs'] is not None:
                    c['Y differs'] += 1
                    c['Y differs (meeting)'] += cy.get('confirmed') == 'through a meeting'
                tk = d['takes']
                c['X takes from Y'] += tk['X takes from Y'] is not None
                c['Y takes from X'] += tk['Y takes from X'] is not None
                e = d['endings']
                c['X ended, not with Y barred'] += (e['X in A']['round_of_ending'] is not None and
                                                    e['X in B(i)']['round_of_ending'] is None)
                c['Y ended, not with X barred'] += (e['Y in A']['round_of_ending'] is not None and
                                                    e['Y in B_X']['round_of_ending'] is None)
                c['(ii)'] += d['reading_ii']['holds']
                c['(ii) reverse'] += d['reading_ii_reverse']['holds']
                c['(iii)'] += bool(d.get('reading_iii'))
                c['(iii) reverse'] += bool(d.get('reading_iii_reverse'))
                c['Waits'] += (e['X in A'].get('state') == 'every member left waits' or
                               e['Y in A'].get('state') == 'every member left waits')
            tab['%s | %s' % (fam, g)] = dict(c)
            allrow.update(c)
    for j, name, d, r in rows:
        if 'X_course' not in d:
            continue
        Tdist[d['T']] += 1
        cx, cy = d['X_course'], d['Y_course']
        e = d['endings']
        members_left += sum(1 for k in ('X in A', 'Y in A') if e[k].get('state') == 'members left, no birth')
        if cx['differs'] is not None:
            ways[cx['way']] += 1
            if cx.get('confirmed') == 'through a meeting':
                ways_m[cx['way']] += 1
                tk_x[d['takes_vs_X_course']] += 1
                if name not in CONTROLS:
                    tk_x_nc[d['takes_vs_X_course']] += 1
            elif cx.get('confirmed') == 'unconfirmed':
                unconf += 1
                t1 = _first(d['takes']['X takes from Y'], d['takes']['Y takes from X'])
                if t1 is not None and t1 <= cx['differs']:
                    unconf_take += 1
        if cy['differs'] is not None and cy.get('confirmed') == 'through a meeting':
            tk_y[d['takes_vs_Y_course']] += 1
        lab = '%s: %s' % (name, lawname(j))
        if d['reading_ii']['holds']:
            ii.append({'run': lab, 'T': d['T'], 'through a meeting': d['reading_ii']['through a meeting'],
                       'X ends (A, B(i), M)': [e['X in A']['round_of_ending'], e['X in B(i)']['round_of_ending'],
                                               e['X in M']['round_of_ending']], 'X course': cx, 'Y course': cy,
                       'takes': d['takes']})
        if d['reading_ii_reverse']['holds']:
            iirev.append({'run': lab, 'T': d['T'], 'through a meeting': d['reading_ii_reverse']['through a meeting'],
                          'Y ends (A, B_X, M_Y)': [e['Y in A']['round_of_ending'], e['Y in B_X']['round_of_ending'],
                                                   e['Y in M_Y']['round_of_ending']], 'takes': d['takes']})
        if d.get('reading_iii'):
            iii.append(lab)
        if d.get('reading_iii_reverse'):
            iiirev.append(lab)
        if 'X_alone' in d:
            fam = 'made-3 to made-6' if name in mc.CLASS_MADE else (
                'made-2 runs' if name in ('made-2', 'made-2-exchanged') else 'Y present from round 0')
            x_alone[(j['take'], fam, 'runs')] += 1
            x_alone[(j['take'], fam, 'differs')] += d['X_alone']['X course differs from X alone at'] is not None
    S['PO3'] = {'verdict': None, 'numbers': {'table': tab, 'all': dict(allrow), 'ways of X\'s differences': dict(ways),
                                             'of them through a meeting': dict(ways_m), 'T': dict(Tdist)}}
    S['PO4'] = {'verdict': None, 'numbers': {'X\'s differences through a meeting': dict(tk_x),
                                             'without the controls': dict(tk_x_nc),
                                             'Y\'s differences through a meeting': dict(tk_y),
                                             'X\'s unconfirmed differences': unconf,
                                             'of them with a take from the other at or before': unconf_take,
                                             'pattern-runs with members left and no birth in round T, not waiting':
                                             members_left}}
    S['PO5'] = {'verdict': None, 'numbers': ii}
    S['PO6'] = {'verdict': None, 'numbers': iirev}
    S['PO9'] = {'verdict': 'reported', 'numbers': {'(iii)': len(iii), '(iii) reverse': len(iiirev),
                                                   '(iii) runs': iii, '(iii) reverse runs': iiirev},
                'note': 'seen: 70 runs and 8 (owner\'s arm C.3)'}
    S['P18'] = {'verdict': 'reported', 'numbers': {'%s | %s' % (a, b): '%d of %d' % (
        x_alone[(a, b, 'differs')], x_alone[(a, b, 'runs')]) for a, b, k in x_alone if k == 'runs'},
        'note': 'seen: differs in every MET run; under STEPS-1 in 216 of 432 made runs (144 of 288 of made-3 to '
                'made-6, 72 of 144 of the made-2 runs) and none with Y present from round 0'}
    # PO3 verdict against the disclosed table
    want = {('made-3 to made-6', 'COPY-LAW'): (24, 24), ('made-3 to made-6', 'CAP-3'): (96, 96),
            ('made-3 to made-6', 'FBP'): (72, 72),
            ('Y present from round 0, five members', 'COPY-LAW'): (10, 0),
            ('Y present from round 0, five members', 'CAP-3'): (120, 90),
            ('Y present from round 0, five members', 'FBP'): (108, 78),
            ('made-2 and the same start with names exchanged', 'COPY-LAW'): (28, 24),
            ('made-2 and the same start with names exchanged', 'CAP-3'): (72, 72),
            ('made-2 and the same start with names exchanged', 'FBP'): (72, 68),
            ('two-22', 'COPY-LAW'): (2, 0), ('two-22', 'CAP-3'): (24, 18), ('two-22', 'FBP'): (24, 18)}
    diffs = []
    for (fam, g), (a, b) in want.items():
        c = tab['%s | %s' % (fam, g)]
        if (c.get('X differs', 0), c.get('X differs (meeting)', 0)) != (a, b):
            diffs.append({'row': '%s | %s' % (fam, g), 'disclosed': [a, b],
                          'here': [c.get('X differs', 0), c.get('X differs (meeting)', 0)]})
    tot = (allrow['X differs'], allrow['X differs (meeting)'], allrow['Y differs'], allrow['Y differs (meeting)'])
    if tot != (652, 560, 457, 357):
        diffs.append({'row': 'all', 'disclosed': [652, 560, 457, 357], 'here': list(tot)})
    per_base = {}
    for g in GROUPS:
        per_base[g] = sum(1 for j, name, d, r in rows if group(j['base']) == g and name != 'made-2-exchanged'
                          and 'X_course' in d and d['X_course']['differs'] is not None)
    S['PO3']['numbers']['X differs per base law, without made-2-exchanged (version 2\'s P15: 50, 276, 240 of 528)'] = \
        per_base
    if [per_base[g] for g in GROUPS] != [50, 276, 240]:
        diffs.append({'row': 'per base law without made-2-exchanged', 'disclosed': [50, 276, 240],
                      'here': [per_base[g] for g in GROUPS]})
    S['PO3']['verdict'] = verdict(not diffs)
    S['PO3']['differences from the disclosure'] = diffs
    w4x = {'no take': 370, 'same round': 60, 'after': 126, 'strictly before': 4}
    w4y = {'no take': 240, 'same round': 40, 'after': 62, 'strictly before': 15}
    d4 = []
    if {k: tk_x.get(k, 0) for k in w4x} != w4x:
        d4.append({'X': {k: tk_x.get(k, 0) for k in w4x}, 'disclosed': w4x})
    if {k: tk_y.get(k, 0) for k in w4y} != w4y:
        d4.append({'Y': {k: tk_y.get(k, 0) for k in w4y}, 'disclosed': w4y})
    S['PO4']['verdict'] = verdict(not d4)
    S['PO4']['differences from the disclosure'] = d4
    # PO5, PO6
    w5 = {('made-4', 'CAP-3(OFFSHOOT)', 'MET', 'BY-COUNT', 'parity'), ('ystart-two-22', 'CAP-3(RETIRE)', 'MET',
                                                                       'IN-TURN', 'parity'),
          ('ystart-two-22', 'CAP-3(RETIRE)', 'MET', 'IN-TURN', 'nae')}
    got5 = {(name, j['base'], j['take'], j['choice'], j['knot_law']) for j, name, d, r in rows
            if d.get('reading_ii', {}).get('holds')}
    S['PO5']['verdict'] = verdict(got5 == w5)
    S['PO5']['differences from the disclosure'] = {'here, not disclosed': sorted(got5 - w5),
                                                   'disclosed, not here': sorted(w5 - got5)}
    w6 = set()
    for kl in ('parity', 'nae'):
        w6 |= {('made-3', 'CAP-3(RETIRE)', 'MET', 'NEWEST', kl), ('made-3', 'CAP-3(RETIRE)', 'MET', 'BY-COUNT', kl),
               ('ystart-three-222', 'CAP-3(RETIRE)', 'MET', 'OLDEST', kl),
               ('ystart-three-222', 'CAP-3(RETIRE)', 'MET', 'IN-TURN', kl)}
    w6.add(('ystart-one-2', 'COPY-LAW(OFFSHOOT)', 'MET', 'NEWEST', 'parity'))
    got6 = {(name, j['base'], j['take'], j['choice'], j['knot_law']) for j, name, d, r in rows
            if d.get('reading_ii_reverse', {}).get('holds')}
    meet6 = all(x['through a meeting'] for x in iirev)
    S['PO6']['verdict'] = verdict(got6 == w6 and meet6)
    S['PO6']['differences from the disclosure'] = {'here, not disclosed': sorted(got6 - w6),
                                                   'disclosed, not here': sorted(w6 - got6),
                                                   'all through a meeting': meet6}
    # PO7: the controls with Y the same as X
    same_end, one_way = Counter(), []
    for j, name, d, r in rows:
        if name not in ('made-2', 'made-2-exchanged') or 'endings' not in d:
            continue
        e = d['endings']
        same_end[(name, e['X in A']['round_of_ending'] == e['Y in A']['round_of_ending'])] += 1
        tk = d['takes']
        a, b = tk['X takes from Y'] is not None, tk['Y takes from X'] is not None
        if a != b:
            one_way.append((name, j['base'], j['take'], j['choice'], j['knot_law'],
                            'X from Y' if a else 'Y from X'))
    want7 = set()
    for name in ('made-2', 'made-2-exchanged'):
        for kl in ('parity', 'nae'):
            for b in ('COPY-LAW(OFFSHOOT)', 'CAP-3(OFFSHOOT)', 'FBP(OFFSHOOT)'):
                want7.add((name, b, 'MET', 'NEWEST', kl, 'X from Y'))
            want7.add((name, 'FBP(OFFSHOOT)', 'MET', 'BY-COUNT', kl, 'Y from X'))
    ok7 = all(k[1] for k in same_end) and set(one_way) == want7
    S['PO7'] = {'verdict': verdict(ok7), 'numbers': {
        'X and Y end in the same round (design, same: runs)': {'%s|%s' % k: v for k, v in same_end.items()},
        'takes in one direction only': sorted(one_way),
        'here, not disclosed': sorted(set(one_way) - want7), 'disclosed, not here': sorted(want7 - set(one_way))}}


def _first(a, b):
    xs = [x for x in (a, b) if x is not None]
    return min(xs) if xs else None


# -------------------------------------------------------------------------------------------- P16, P17, P19, PO1
def misc2(S, rows, cases_form):
    # P17: the fourth mark on the renamed trace; and on the parts by descent
    fm = Counter()
    for r in {id(x[3]): x[3] for x in rows}.values():
        j = r['job']
        for pair, v in r.get('fourth_mark', {}).items():
            fam = 'made' if pair.startswith('made') else 'start'
            fm[(fam, 'all', 'pairs')] += 1
            fm[(fam, 'all', 'differ')] += v is not None
            if j['take'] == 'MET':
                fm[(fam, group(j['base']), 'pairs')] += 1
                fm[(fam, group(j['base']), 'differ')] += v is not None
    pd = Counter()
    by = defaultdict(dict)
    for j, name, d, r in rows:
        if 'parts_same_as_member' in d:
            by[(j['base'], j['take'], j['choice'], j['knot_law'])][name] = d['parts_same_as_member']
    for law, ds in by.items():
        for fam, members in (('made', mc.CLASS_MADE), ('start', mc.CLASS_START)):
            for a in members:
                for b in members:
                    if a < b and a in ds and b in ds:
                        pd[(fam, 'pairs')] += 1
                        pa, pb = ds[a], ds[b]
                        n = min(len(next(iter(pa.values()), [])), len(next(iter(pb.values()), [])))
                        diff = any(pa[m][:n] != pb[m][:n] for m in members if m in pa and m in pb)
                        pd[(fam, 'differ')] += diff
    S['P17'] = {'verdict': 'reported', 'numbers': {
        'on the renamed trace': {'%s | %s' % (f, g): '%d of %d' % (fm[(f, g, 'differ')], fm[(f, g, 'pairs')])
                                 for f, g, k in fm if k == 'pairs'},
        'on the parts by descent': {f: '%d of %d' % (pd[(f, 'differ')], pd[(f, 'pairs')]) for f in ('made', 'start')}},
        'note': 'seen on the trace: 164 of 864 made-X pairs, 203 of 1,440 start-X pairs; under MET, CAP-3(t) 56 of '
                '144 and 116 of 240, FBP(t) 22 of 144 and 76 of 240, COPY-LAW(t) 6 of 144 and 11 of 240'}
    # P16: form cases by X only meeting condition 2 show the fourth mark on the parts by descent
    p16 = [c for c in cases_form if c['condition 2, fewer than two of every other member'] and
           c['condition 2, every other member has two in its own run']]
    S['P16'] = {'verdict': 'holds' if not p16 else 'see cases', 'numbers': {
        'form cases made by X only meeting condition 2': len(p16), 'cases': p16},
        'note': 'true by definition (B3); with no case meeting condition 2 there is nothing to check'}
    # P19
    own, own_bx, ret, ret_bx = [], [], [], []
    for j, name, d, r in rows:
        if 'values' not in d:
            continue
        lab = '%s: %s' % (name, lawname(j))
        if d['values'].get('Y_own_some'):
            own.append(lab)
        if d['B_X']['values'].get('Y_own_some'):
            own_bx.append(lab)
        if d['form'].get('Y_returning_some'):
            ret.append(lab)
        if d['B_X']['form'].get('Y_returning_some'):
            ret_bx.append(lab)
    S['P19'] = {'verdict': 'reported', 'numbers': {
        'Y handing on its own value, run A': own, 'with X barred': own_bx, 'the same runs': sorted(own) == sorted(own_bx),
        'Y returning (form), run A': len(ret), 'with X barred': len(ret_bx), 'Y returning runs (first 10)': ret[:10]},
        'note': 'seen: 9 parity runs, the same with X barred'}
    # PO1
    n, bad = 0, []
    for j, name, d, r in rows:
        if 'PO1' in d:
            n += 1
            if not d['PO1']['same'] or d['PO1']['loose_taken_by_other']:
                bad.append(('%s: %s' % (name, lawname(j)), d['PO1']['same'], d['PO1']['loose_taken_by_other']))
    S['PO1'] = {'verdict': verdict(not bad), 'numbers': {'runs A read (run 2)': n, 'failing': bad[:10]}}


def po1_run3(S, R3):
    n, bad = 0, []
    for r in R3:
        for p_ in r.get('pairs', []):
            if 'PO1' in p_:
                n += 1
                if not p_['PO1']['same'] or p_['PO1']['loose_taken_by_other']:
                    bad.append((r['job'], p_['X'], p_['Y']))
    S['PO1']['numbers']['pairs read (run 3)'] = n
    S['PO1']['numbers']['failing (run 3)'] = bad[:10]
    if bad:
        S['PO1']['verdict'] = 'fails'


# ------------------------------------------------------------------------------------------------------- run O
def po2(S, RO):
    read = [r for r in RO if r.get('read')]
    ch = [r for r in read if r.get('change')]
    byy = [r for r in ch if r.get('by births descended from Y only')]
    fl0 = [r for r in read if r['base'].startswith('FLOOR0')]
    one = [r for r in read if r['base'].startswith('ONE-FEWER')]
    pass_ = [r for r in byy if r['knot test at the round of the change']['n_fails'] == 0]
    S['PO2'] = {'verdict': verdict(not pass_), 'numbers': {
        'runs': len(RO), 'read': len(read), 'errors': sum(1 for r in RO if 'error' in r),
        'changed under FLOOR0': '%d of %d' % (sum(1 for r in fl0 if r.get('change')), len(fl0)),
        'changed under ONE-FEWER': '%d of %d' % (sum(1 for r in one if r.get('change')), len(one)),
        'changed, parity / not-all-equal': [sum(1 for r in ch if r['knot_law'] == 'parity'),
                                            sum(1 for r in ch if r['knot_law'] == 'nae')],
        'by births descended from Y only': len(byy),
        'of them by ration': dict(Counter(r['base'].split('(')[0] for r in byy)),
        'of them by knot law and taking rule': dict(Counter('%s %s' % (r['knot_law'], r['take']) for r in byy)),
        'of them by design': dict(Counter(r['design'] for r in byy)),
        'of them with every knot passing at that round': len(pass_),
        'not-all-equal tie classes with a made distinction (runs with one)': sum(
            1 for r in read if any(r.get('tie classes with a made distinction, per round') or []))},
        'note': 'seen: 1,034 read; 190 of 528 under FLOOR0, 74 of 506 under ONE-FEWER (174 parity, 90 '
                'not-all-equal); by births descended from Y only in 68 (34 each ration), all parity and STEPS-1: '
                'made-3 12, ystart-one-2 14, ystart-one-3 18, ystart-three-222 24; every one with a failing knot'}


# ------------------------------------------------------------------------------------------------- run 5 extras
def po10(S, R5iv):
    stated = [x for x in R5iv if x['job'].get('kind') == 'stated']
    lists = [x for x in R5iv if x['job'].get('kind') == 'take list']
    st_rows = []
    for x in stated:
        for r in x['rows']:
            st_rows.append({'case': '%s: %s' % (x['job']['design'], lawname(x['job'])), 'Z': r['Z'],
                            'where': r['where'], '(iv) holds': r.get('(iv) holds'),
                            'with Z: two of Y at': r['with Z']['two of Y at'],
                            'with Z: two of Z at': r['with Z']['two of Z at'],
                            'Z barred: two of Y at': r['Z barred']['two of Y at'],
                            'Z barred: two of Z at': r['Z barred']['two of Z at'],
                            'Z in round T': r.get('Z in the run with Z'),
                            'knot fails': [r['with Z']['knot_fails'], r['Z barred']['knot_fails']]})
    c = Counter()
    for x in lists:
        for r in x['rows']:
            c['runs with Z'] += 1
            ap = r['the list does not apply from round']
            if ap['with Z'] is not None:
                c['with Z: does not apply'] += 1
                c['with Z: does not apply from round %d' % ap['with Z']] += 1
            if ap['Z barred'] is not None:
                c['Z barred: does not apply'] += 1
            if 'with Z' in r:
                c['with Z, applies: two of Y remain'] += bool(r['with Z']['two of Y at'])
                c['with Z, applies'] += 1
            if 'Z barred' in r:
                c['Z barred, applies'] += 1
                c['Z barred: two of Y'] += bool(r['Z barred']['two of Y at'])
            if r.get('(iv) holds') is not None:
                c['(iv) read'] += 1
                c['(iv) holds'] += bool(r['(iv) holds'])
                c['Z makes a birth in round T'] += bool(r['(d) Z makes a birth in round T'])
            for k in ('with Z', 'Z barred'):
                if isinstance(r.get(k), dict) and r[k].get('knot_fails'):
                    c['runs with a failing knot'] += 1
    S['PO10'] = {'verdict': 'reported', 'numbers': {'the stated-rule cases': st_rows,
                                                    'the take-list cases': dict(c),
                                                    'lists read': len(lists)},
                 'note': 'seen: on the stated-rule case (iv) holds for each of the 5 kinds of Z named before Y and '
                         'for none named after; on the 18 take-list cases for none, the list not applying in 26 of '
                         '180 runs'}


def run5_extra(S, R5c, R5c3, R5l, R5f):
    S['_run5'] = {}
    rows = []
    for x in R5c:
        c = x['case']
        rows.append({'case': '%s, %s: %s' % (c['design'], c['reading'], lawname(c)), 'control': c['control'],
                     'as run': x.get('as run', {}).get('survives'),
                     'passes the registered renamings': x.get('survives every registered renaming'),
                     'swaps survived': [k for k, v in x['swaps'].items() if v['survives']],
                     'swaps lost': [k for k, v in x['swaps'].items() if not v['survives']], 'error': x.get('error')})
    S['_run5']['cases of run 2'] = rows
    S['_run5']['cases of run 3'] = [{'case': x['case'], 'swaps': {k: v['survives'] for k, v in x['swaps'].items()}}
                                    for x in R5c3]
    lt = Counter()
    lrows = []
    for x in R5l:
        for k, v in x['swaps'].items():
            kk = k if not k.startswith('base law') else 'base law ' + group(k[len('base law '):])
            lt[(kk, 'swaps')] += 1
            lt[(kk, 'does not apply')] += v['the list does not apply from round'] is not None
            lt[(kk, 'survives')] += bool(v.get('survives'))
        lrows.append({'index': x['index'], 'design': x['design'], 'identity': x.get('identity'),
                      'survives': [k for k, v in x['swaps'].items() if v.get('survives')], 'error': x.get('error')})
    S['_run5']['take lists'] = {'by swap': {'%s | %s' % k: v for k, v in sorted(lt.items())},
                                'lists': lrows,
                                'identity translation gives the list\'s run': sum(
                                    1 for x in R5l if (x.get('identity') or {}).get('same structures'))}
    # the form arm's swaps
    ft = defaultdict(Counter)
    fcases = []
    guard = 0
    for x in R5f:
        sw = x['job']['swap']
        for name, d in x.get('designs', {}).items():
            if 'form' not in d:
                continue
            ft[sw]['runs'] += 1
            guard += bool(d.get('guard'))
            ft[sw]['runs with a round not read (roster met the guard)'] += bool(d.get('rounds not read'))
            if d['form'].get('two_by_X_some'):
                ft[sw]['runs with two parts the same as Y, made by X only'] += 1
                fcases.append({'swap': sw, 'design': name, 'law': x['law'], 'round': d['form']['two_by_X_some'],
                               'control': name in CONTROLS})
    S['_run5']['form arm'] = {'by swap': {k: dict(v) for k, v in ft.items()}, 'cases': fcases,
                              'runs stopped by the guard': guard}


# --------------------------------------------------------------------------------------------------- verdicts
NUMBERINGS = {}


def case_verdicts(rows, R5c):
    surv = renaming_survival(R5c)
    out = []
    for j, name, d, reading in cases2(rows):
        sv = surv.get((name, j['base'], j['take'], j['choice'], j['knot_law'], reading))
        if reading == 'values':
            c = next(c for c in d['values']['cases'] if c['made_by_X'])
            who = sorted(c['descents'])
            who = ('descended from X only' if who == ['X only', 'X only'] else
                   'from both' if 'both' in who else 'mixed: %s' % who)
        else:
            who = 'descended from X only'
        nb = NUMBERINGS.get((name, j['base'], j['take'], j['choice'], j['knot_law'], reading))
        if sv and sv['every registered renaming']:
            fixed = ('a stated rule whose case passes the registered renamings (%s); post-freeze (dev 51): %s' % (
                ', '.join(sorted(sv['by renaming'])), ('passes each of the %d numberings run' % nb['numberings run']
                                                       if nb and nb['passes'] == nb['numberings run'] else
                                                       'under a supplied numbering' if nb else
                                                       'not decided by the registered test')))
        else:
            fixed = 'a stated rule whose case is lost under some registered renaming' if sv else 'not read'
        link = d.get('link', {}) or {}
        lc = Counter(link.get('link_classes', {}).values()) if link else Counter()
        xfrom = 'X made by births' if name.startswith('made') else 'X a start pattern'
        made_link = bool(link.get('made_connected')) if link else None
        out.append({'case': '%s, %s: %s' % (name, reading, lawname(j)), 'control': name in CONTROLS,
                    'round': d[reading]['Y_by_X_some' if reading == 'values' else 'two_by_X_some'],
                    'who made the two': who, 'what fixed the takes': fixed,
                    'renamings': sv and sv['by renaming'],
                    'where X comes from': xfrom, 'meeting round': d.get('meeting_round'),
                    'linking knots (FD 5.7 classes: knots)': dict(lc),
                    'X and Y one part through made knots only': made_link,
                    'made': (who == 'descended from X only' and fixed.startswith('a stated rule whose case passes')
                             and xfrom == 'X made by births' and bool(made_link)),
                    'knot fails in run A': d['knot_tests_A']['n_fails'],
                    'B(i)': d['B(i)'][reading if reading != 'built' else 'form'],
                    'X alone': d.get('X_alone', {}).get('X course differs from X alone at')})
    return out


def main():
    S = {}
    gate(S)
    R1 = run1(S)
    R2 = load('run2.jsonl.gz') or []
    R3 = load('run3.jsonl.gz') or []
    R4 = load('run4.jsonl') or []
    R4rep = load('run4_replay.json')
    R5c = load('run5_cases.jsonl') or []
    R5c3 = load('run5_cases3.jsonl') or []
    R5l = load('run5_lists.jsonl') or []
    R5iv = load('run5_iv.jsonl') or []
    R5f_all = load('run5_form.jsonl.gz') or []
    keep = {}
    for r in R5f_all:                       # deviations 47: a rerun row replaces an error row of the same law
        k = json.dumps(r['job'], sort_keys=True)
        if k not in keep or 'error' in keep[k]:
            keep[k] = r
    R5f = list(keep.values())
    R6 = load('run6.jsonl.gz') or []
    RO = load('runO.jsonl.gz') or []
    # deviations 44: X alone and Y alone for made-2-exchanged
    ex = {tuple(r['job'][k] for k in ('base', 'take', 'choice', 'knot_law')): r
          for r in (load('run2_exchanged_alone.jsonl') or [])}
    for r in R2:
        e = ex.get(tuple(r['job'][k] for k in ('base', 'take', 'choice', 'knot_law')))
        if e and e['run A as in run 2']:
            for k in ('X_alone', 'Y_alone', 'T_iii', 'reading_iii', 'reading_iii_reverse'):
                r['designs']['made-2-exchanged'][k] = e[k]
    S['_exchanged_alone'] = {'laws': len(ex), 'run A as in run 2': sum(1 for e in ex.values()
                                                                        if e['run A as in run 2'])}
    rows = run2_rows(R2)
    S['_counts'] = {'run 1 runs': len(R1), 'run 2 laws': len(R2), 'run 2 design runs': len(rows),
                    'run 3 runs': len(R3), 'run 3 pairs': sum(len(r.get('pairs', [])) for r in R3),
                    'run 4 enumerations': len(R4), 'run 5 cases': len(R5c), 'run 5 run-3 cases': len(R5c3),
                    'run 5 take lists': len(R5l), 'run 5 (iv) jobs': len(R5iv), 'run 5 form arm laws': len(R5f),
                    'run 6 jobs': len(R6), 'run O runs': len(RO),
                    'errors': {'run 2': [r['job'] for r in R2 if 'error' in r],
                               'run 3': [r['job'] for r in R3 if 'error' in r],
                               'run 5': [x.get('case', x.get('job')) for src in (R5c, R5c3, R5l, R5iv, R5f)
                                         for x in src if 'error' in x],
                               'run 6': [r['job'] for r in R6 if 'error' in r],
                               'run O': [r for r in RO if 'error' in r][:3]}}
    p2(S, R1, R2, R3, R4, (R5c, R5c3, R5l, R5iv, R5f), R6)
    p5_p6(S, rows)
    p7(S, R5c)
    run4(S, R4, R4rep)
    p10(S, R1, R2, R3, R4, R4rep, (R5c, R5c3, R5l, R5iv, R5f))
    form_class, cases_form = copier(S, rows, R5c, R5f)
    arm(S, rows)
    misc2(S, rows, cases_form)
    po1_run3(S, R3)
    po2(S, RO)
    po10(S, R5iv)
    run5_extra(S, R5c, R5c3, R5l, R5f)
    r7 = load('run7_numberings.json')
    if r7:
        for x in r7['rows']:
            c = x['case']
            NUMBERINGS[(c['design'], c['base'], c['take'], c['choice'], c['knot_law'], c['reading'])] = x
        S['_post-freeze numberings (dev 51)'] = [{
            'case': '%s, %s: %s' % (x['case']['design'], x['case']['reading'], lawname(x['case'])),
            'numberings run': x['numberings run'],
            'distinct named starts (distinct up to the start\'s symmetries)': x[
                "distinct up to the start's symmetries (distinct named starts)"],
            'passes': x['passes'], 'verdict': x['verdict']} for x in r7['rows']]
    S['_cases'] = case_verdicts(rows, R5c)
    S['_built'] = {'runs A read': sum(1 for j, name, d, r in rows if 'built' in d),
                   'with a renaming of Y\'s knots among the made knots at some round': [
                       '%s: %s' % (name, lawname(j)) for j, name, d, r in rows
                       if d.get('built', {}).get('any_renaming_some')],
                   'with the search bound met': sum(1 for j, name, d, r in rows if d.get('built', {}).get('bound_hit'))}
    p20 = load('check_p20.json')
    if p20:
        c1 = p20["clause 1 (all three takes of round 3 take Y's fresh distinction 17)"]
        c2 = p20['clause 2 (three usable loose made distinctions of X, tied to three different start distinctions)']
        smallest = S['P6']['verdict'] == 'holds'
        S['P20'] = {'verdict': verdict(c1 and c2 and smallest), 'numbers': {
            'the smallest second pattern P6 fails on': 'ystart-one-2 (one member holding two), since P6 holds for '
            'ystart-three-222 only' if smallest else 'not read (P6 fails)', 'clause 1': c1, 'clause 2': c2,
            'start distinctions (names, labels)': p20['their start distinctions (names, labels)']}}
    # P10: run 2's runs A with a failing knot
    S['P10']['numbers']['run 2, runs A with a failing knot'] = [
        ('%s: %s' % (name, lawname(j)), d['knot_tests_A']['n_fails']) for j, name, d, r in rows
        if d.get('knot_tests_A', {}).get('n_fails')]
    S['_run3'] = {'runs': len(R3), 'pairs': sum(len(r.get('pairs', [])) for r in R3),
                  'pairs by start': dict(Counter(r['job']['start'] for r in R3 for _ in r.get('pairs', []))),
                  'cases': [{'start': r['job']['start'], 'law': r.get('law'), 's': p_['s'], 'X': p_['X'], 'Y': p_['Y'],
                             'values': p_['values'].get('Y_by_X_some'), 'form': p_['form'].get('two_by_X_some'),
                             'built': p_['built'].get('two_by_X_some')}
                            for r in R3 for p_ in r.get('pairs', [])
                            if p_['values'].get('Y_by_X_some') or p_['form'].get('two_by_X_some') or
                            p_['built'].get('two_by_X_some')],
                  'pairs with a made distinction of X tied to a place of Y (any)': sum(
                      1 for r in R3 for p_ in r.get('pairs', []) if any(
                          c['made_by_X'] for row in p_.get('per_round', []) for c in row.get('values_Y', []))),
                  'NAE tie classes with a made distinction (runs)': sum(1 for r in R3 if r.get('ties_made'))}
    C.write_json('summary.json', S)
    for k in sorted(k for k in S if not k.startswith('_')):
        print('%-6s %s' % (k, S[k]['verdict']))


if __name__ == '__main__':
    main()
