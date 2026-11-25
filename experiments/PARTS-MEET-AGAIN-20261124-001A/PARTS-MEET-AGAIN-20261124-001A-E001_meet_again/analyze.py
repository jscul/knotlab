"""Verdicts of P0 to P18 from the outputs of runs G and 1 to 7; writes summary.json and summary.md.

usage: python -B analyze.py
"""
import glob
import gzip
import json
import os
from collections import Counter, defaultdict

import common as C

OUT = C.OUT


def jl(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return []
    op = gzip.open if p.endswith('.gz') else open
    with op(p, 'rt') as f:
        return [json.loads(x) for x in f if x.strip()]


def js(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


ARM_A = lambda n: n.startswith('Q(') or n.startswith('SHORT-TAKES') or n.startswith('late ')


def kind(p):
    return 'came apart' if p['came_apart'] else 'first time'


def rule_of(name):
    if name.startswith('late '):
        name = name[5:]
    return name.split('(')[0]


def choice_of(name):
    if '(' in name:
        return name.split('(')[-1].rstrip(')')
    return None


def ration_group(base):
    return 'CAP-3 swap' if base.startswith('CAP-3') else 'base laws'


# ------------------------------------------------------------------------------------------------------ cost vector
INF = 99


def cost(law_name):
    """D 3.3's table: (holder steps, record steps, whole roster, what supplies the choice)."""
    r = rule_of(law_name)
    c = choice_of(law_name)
    sup = {'OLDEST': 'names', 'NEWEST': 'names', 'IN-TURN': 'order of births', 'BY-COUNT': 'structure',
           'BY-RECEIVED': 'record'}.get(c, 'none')
    if r in ('Q', 'SHORT-TAKES'):
        return (1, 0, 0, sup)
    if r == 'CARRY':
        return (1, 1, 0, 'names')
    if r == 'MET':
        return (2, 0, 0, sup)
    if r in ('STEPS-1', 'STEPS-2', 'UP-TO-2'):
        k = int(r[-1])
        return (k + 1, k, 0, sup)
    if r == 'FIRST':
        return (INF, INF, 1, sup)
    if r in ('RECORD-2', 'RECORD-3'):
        return (0, int(r[-1]), 0, 'none')
    if r == 'ALL-JOINABLE':
        return (0, 0, 1, 'none')
    if r == 'none':
        return (0, 0, 0, 'none')
    raise ValueError(law_name)


def leq(a, b, with_choice=True):
    if any(x > y for x, y in zip(a[:3], b[:3])):
        return False
    if with_choice and a[3] != b[3]:
        return False
    return True


def minimal(laws, with_choice=True):
    cs = {l: cost(l) for l in laws}
    out = []
    key = (lambda c: c) if with_choice else (lambda c: c[:3])
    for l in laws:
        if not any(m != l and leq(cs[m], cs[l], with_choice) and key(cs[m]) != key(cs[l]) for m in laws):
            out.append(l)
    return sorted(out)


# -------------------------------------------------------------------------------------------------------- the gate
def gate():
    ring = [js(os.path.basename(p)) for p in sorted(glob.glob(os.path.join(OUT, 'gate_ring_summary_*.json')))]
    rq = [js(os.path.basename(p)) for p in sorted(glob.glob(os.path.join(OUT, 'gate_rq_summary_*.json')))]
    reg_rows = []
    for p in sorted(glob.glob(os.path.join(OUT, 'gate_ring_*of6*.jsonl'))):
        reg_rows += jl(os.path.basename(p))
    # registered runs: chunk 4 registered file + the registered rows of the other chunks (chunk 4 full file holds
    # the same registered rows again and the extras)
    seen = {}
    for r in reg_rows:
        key = (r['start'], r['names_reversed'], r['law'], r['knot_law'])
        seen[key] = r
    rows = list(seen.values())
    reg = [r for r in rows if r['registered']]
    ext = [r for r in rows if not r['registered']]
    g = {'ring_runs_registered': len(reg), 'ring_runs_extra': len(ext),
         'ring_rounds_compared': sum(r['rounds_compared'] for r in rows),
         'ring_mismatches': sum(1 for r in rows if r['mismatch']),
         'implied_vs_literal_runs': sum(1 for r in rows if 'implied_equals_literal' in r),
         'implied_vs_literal_mismatch': sum(1 for r in rows if r.get('implied_equals_literal') is False),
         'G_knot_verdicts': sum(r['knot_tests']['verdicts'] for r in rows),
         'G_knot_fails': sum(r['knot_tests']['n_fails'] for r in rows),
         'G_fail_laws': sorted({(r['law'], r['knot_law']) for r in rows if r['knot_tests']['n_fails']}),
         'G_method_disagreements': sum(r['knot_tests']['n_disagree'] for r in rows),
         'G_birth_vs_direct': sum(r['knot_tests']['birth_vs_direct'] for r in rows),
         'G_untested': sum(len(r['knot_tests']['untested']) for r in rows),
         'G_stops': Counter(str(r['stop']) for r in rows)}
    rqrows = []
    for p in sorted(glob.glob(os.path.join(OUT, 'gate_rq_*of3.jsonl'))):
        rqrows += jl(os.path.basename(p))
    g.update({'rq_runs': len(rqrows), 'rq_rounds_compared': sum(r['rounds_compared'] for r in rqrows),
              'rq_mismatches': sum(1 for r in rqrows if r['mismatch']),
              'rq_their_outcomes': Counter(r.get('their_outcome') for r in rqrows),
              'rq_my_stops': Counter(str(r.get('stop')) for r in rqrows)})
    b = js('gate_brute_summary.json')
    bb = js('gate_birth_summary.json')
    g['brute'] = b
    g['birth'] = bb
    ok = (g['ring_mismatches'] == 0 and g['implied_vs_literal_mismatch'] == 0 and g['rq_mismatches'] == 0 and
          b and b['mismatch_ranks'] == 0 and b['mismatch_kernel'] == 0 and b['mismatch_nae'] == 0 and
          bb and bb['mismatch_direct'] == 0 and bb['mismatch_brute'] == 0 and g['G_method_disagreements'] == 0)
    g['P0'] = 'holds' if ok else 'fails'
    return g


# ------------------------------------------------------------------------------------------------- runs 1 and 3
def pairs_table(rows):
    """Aggregates per law name over the rows (both knot laws)."""
    agg = defaultdict(lambda: Counter())
    for r in rows:
        if 'pairs' not in r:
            continue
        L = r['law_name']
        a = agg[L]
        a['runs'] += 1
        for p in r['pairs']:
            k = kind(p)
            a['pairs ' + k] += 1
            if p['one_part_again'] is not None:
                a['one part again ' + k] += 1
            if p['joint_birth'] is not None:
                a['joint birth ' + k] += 1
            if p['course_differs'] is not None:
                a['course differs ' + k] += 1
                if p.get('confirmed'):
                    a['confirmed ' + k] += 1
                a['verdict %s: %s' % (k, p.get('verdict'))] += 1
        ca = sum(1 for p in r['pairs'] if p['came_apart'])
        if ca:
            a['runs with pairs that came apart'] += 1
    return {k: dict(v) for k, v in agg.items()}


def marks_list(rows, run_label):
    out = []
    for r in rows:
        for p in r.get('pairs', []):
            if p['course_differs'] is None:
                continue
            out.append({'run': run_label, 'base': r['base'], 'start': r['start'], 'law_name': r['law_name'],
                        'knot_law': r['knot_law'], 'kind': kind(p), 's': p['s'], 'X': p['X'], 'Y': p['Y'],
                        'wholly_apart': p['wholly_apart'], 'one_part_again': p['one_part_again'],
                        'joint_birth': p['joint_birth'], 'course_differs': p['course_differs'], 'way': p['way'],
                        'demand_line': p['demand_line'], 'confirmed': p.get('confirmed'), 'verdict': p.get('verdict'),
                        'b2': p.get('b2'), 'link_classes': (p.get('link') or {}).get('link_classes')})
    return out



def s1(p):
    return p['s'] >= 1


def verdicts(S, r1, r3, r7, r2, r4, r5, r6, rca):
    V = {}
    armA = [r for r in r1 if ARM_A(r['law_name'])]
    carry = [r for r in r3 if r['law_name'] == 'CARRY']
    # ---------------------------------------------------------------- P0
    V['P0'] = {'verdict': S['gate']['P0'], 'numbers': {k: S['gate'][k] for k in (
        'ring_runs_registered', 'ring_runs_extra', 'ring_rounds_compared', 'ring_mismatches', 'implied_vs_literal_runs',
        'implied_vs_literal_mismatch', 'rq_runs', 'rq_rounds_compared', 'rq_mismatches', 'G_birth_vs_direct',
        'G_method_disagreements', 'G_knot_verdicts', 'G_knot_fails')},
        'brute': S['gate']['brute'], 'birth': S['gate']['birth']}
    # ---------------------------------------------------------------- P1
    bad = []
    for r in armA + carry + [x for x in rca]:
        ap = r['all_pairs']
        if ap['one_part_again'] or ap['joint_birth']:
            bad.append({k: r[k] for k in ('base', 'start', 'law_name', 'knot_law')} | {'opa': ap['one_part_again'],
                                                                                        'jb': ap['joint_birth']})
    r2bad = [x['id'] for x in r2 if 'stats' in x and x['rule'] in ('Q', 'SHORT-TAKES') and
             (x['stats']['one_part_again'] or x['stats']['joint_births'])]
    V['P1'] = {'verdict': 'holds' if not bad and not r2bad else 'fails',
               'numbers': {'runs checked (run 1 arm A, CARRY of run 3, CARRY other reading)': len(armA) + len(carry) +
                           len(rca), 'violations': bad[:10], 'run 2 enumerations checked': len(r2),
                           'run 2 histories': sum(x['stats']['histories'] for x in r2 if 'stats' in x),
                           'run 2 violations': r2bad}}
    # ---------------------------------------------------------------- P2
    other = []
    n_nae = n_par = 0
    for r in armA:
        for p in r['pairs']:
            if not s1(p):
                continue
            if r['knot_law'] == 'nae':
                n_nae += 1
                if p['course_differs'] is not None:
                    other.append((r['base'], r['start'], r['law_name'], 'nae', p['s'], p['way']))
            else:
                n_par += 1
                if p['course_differs'] is not None and p['way'] != 'a round-wide trigger':
                    other.append((r['base'], r['start'], r['law_name'], 'parity', p['s'], p['way']))
    par_trig = sum(1 for r in armA if r['knot_law'] == 'parity' for p in r['pairs'] if s1(p) and
                   p['course_differs'] is not None)
    s0 = Counter((r['law_name'], r['knot_law'], p['way']) for r in armA for p in r['pairs'] if p['s'] == 0 and
                 p['course_differs'] is not None)
    V['P2'] = {'verdict': 'holds' if not other else 'fails',
               'numbers': {'pairs at s >= 1, not-all-equal': n_nae, 'pairs at s >= 1, parity': n_par,
                           'parity marks (all by a round-wide trigger if holds)': par_trig, 'other ways': other[:10],
                           "the two-knot start's own pair at s = 0 (not wholly apart; outside argument 4)":
                               {str(k): v for k, v in s0.items()}}}
    # ---------------------------------------------------------------- P3
    r1q = [r for r in r1 if r['law_name'] in ('Q(OLDEST)', 'Q(NEWEST)', 'Q(IN-TURN)', 'Q(BY-COUNT)',
                                               'SHORT-TAKES(OLDEST)', 'SHORT-TAKES(NEWEST)')]
    ret = [(r['base'], r['start'], r['law_name'], r['knot_law'], r['ring_returns']) for r in r1q
           if r['start'] in ('Ring(5,3)', 'Ring(7,3)', 'D2(5,3)') and r.get('ring_returns')]
    ctrl = [(r['base'], r['start'], r['knot_law'], r.get('ring_returns')) for r in r1 if r['law_name'] == 'none' and
            r['start'] in ('Ring(5,3)', 'Ring(7,3)', 'D2(5,3)')]
    n2 = []
    for r in r1q:
        if not r['base'].startswith('COPY-LAW'):
            continue
        for row in r['per_round']:
            if row['t'] >= 1 and row['N2']:
                ok = (row['t'] == 1 and row['N2'] == 2 and r['start'] == 'two-knot' and
                      r['law_name'].startswith('SHORT-TAKES'))
                if not ok:
                    n2.append((r['base'], r['start'], r['law_name'], r['knot_law'], row['t'], row['N2']))
    exc = [(r['base'], r['law_name'], r['knot_law'], [row['N2'] for row in r['per_round']]) for r in r1q if
           r['base'].startswith('COPY-LAW') and r['start'] == 'two-knot' and r['law_name'].startswith('SHORT')]
    V['P3'] = {'verdict': 'holds' if not ret and not n2 else 'fails',
               'numbers': {'ring returns under arm A from round 1': ret, 'control, no taking rule (rounds of return)':
                           ctrl, 'two-knot parts after round 1 other than the exception': n2,
                           'the exception (N(t), t = 0..)': exc}}
    # ---------------------------------------------------------------- P5
    p5 = {}
    for L in ('late Q(OLDEST)', 'late Q(NEWEST)', 'late SHORT-TAKES(OLDEST)', 'late SHORT-TAKES(NEWEST)'):
        rr = [r for r in r1 if r['law_name'] == L]
        ca = [p for r in rr for p in r['pairs'] if s1(p) and p['came_apart']]
        p5[L] = {'pairs that came apart': len(ca), 'one part again': sum(1 for p in ca if p['one_part_again']),
                 'all-pairs check, one part again': sum(len(r['all_pairs']['one_part_again']) for r in rr)}
    V['P5'] = {'verdict': 'holds' if all(v['pairs that came apart'] >= 300 and not v['one part again'] and
                                         not v['all-pairs check, one part again'] for v in p5.values()) else 'fails',
               'numbers': p5}
    # ---------------------------------------------------------------- P6
    p6 = {}
    for L in ('RECORD-2', 'RECORD-3'):
        rr = [r for r in r3 if r['law_name'] == L]
        ca = [p for r in rr for p in r['pairs'] if s1(p) and p['came_apart']]
        p6[L] = {'pairs that came apart': len(ca), 'one part again': sum(1 for p in ca if p['one_part_again']),
                 'all-pairs check (any wholly apart pair), one part again':
                     sum(len(r['all_pairs']['one_part_again']) for r in rr)}
    for L, rr in (('ALL-JOINABLE', [r for r in r3 if r['law_name'] == 'ALL-JOINABLE']), ('CARRY', carry),
                  ('CARRY (other reading)', rca)):
        mx = max(row['classes'] for r in rr for row in r['per_round'])
        p6[L] = {'largest number of classes at any round': mx,
                 'runs with two or more classes at some round': sum(1 for r in rr if any(
                     row['classes'] >= 2 for row in r['per_round']))}
    V['P6'] = {'verdict': 'holds' if all(p6[L]['one part again'] == 0 for L in ('RECORD-2', 'RECORD-3')) and
               all(p6[L]['largest number of classes at any round'] <= 1 for L in ('ALL-JOINABLE', 'CARRY'))
               else 'fails', 'numbers': p6}
    # ---------------------------------------------------------------- P11 cost order
    p11 = {}
    for kind_ in ('came apart', 'first time'):
        laws_all = defaultdict(set)
        for r in r1 + r3:
            if r['knot_law'] not in ('nae', 'parity'):
                continue
            for p in r['pairs']:
                if s1(p) and kind(p) == kind_ and p['course_differs'] is not None and p.get('confirmed') and \
                        p.get('verdict') in ('through a knot the growth made', 'through a start knot'):
                    laws_all[ration_group(r['base'])].add(r['law_name'])
                    laws_all['pooled'].add(r['law_name'])
        p11[kind_] = {}
        for grp, ls in sorted(laws_all.items()):
            ls = sorted(ls)
            p11[kind_][grp] = {'laws with the mark': ls,
                               'minimal, three components (holder, record, whole roster)': minimal(ls, False),
                               'minimal, four components (choice supplier compared by equality)': minimal(ls, True)}
    want_ca = {'base laws': ['STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)'], 'CAP-3 swap': ['MET(BY-COUNT)', 'MET(NEWEST)']}
    hold3 = all(p11['came apart'].get(g, {}).get('minimal, three components (holder, record, whole roster)') == w
                for g, w in want_ca.items())
    hold4 = all(p11['came apart'].get(g, {}).get('minimal, four components (choice supplier compared by equality)')
                == w for g, w in want_ca.items())
    ft = p11['first time']
    ft_ok3 = ft.get('base laws', {}).get('minimal, three components (holder, record, whole roster)') == \
        ['MET(BY-COUNT)'] and set(ft.get('CAP-3 swap', {}).get(
            'minimal, three components (holder, record, whole roster)', [])) == {'MET(OLDEST)', 'MET(NEWEST)',
                                                                                'MET(IN-TURN)', 'MET(BY-COUNT)'}
    forbidden = [l for l in p11['came apart'].get('pooled', {}).get('laws with the mark', [])
                 if ARM_A(l) or l in ('RECORD-2', 'RECORD-3', 'ALL-JOINABLE', 'CARRY')]
    V['P11'] = {'verdict': ('holds under the three-component reading per ration group; ' +
                            ('holds' if hold4 else 'fails') + ' under the four-component reading')
                if hold3 and ft_ok3 and not forbidden else 'fails',
                'numbers': p11, 'arm A, RECORD, ALL-JOINABLE or CARRY with the mark': forbidden,
                'cost table': {l: cost(l) for l in sorted({r['law_name'] for r in r1 + r3})}}
    # ---------------------------------------------------------------- P12 (run 5)
    p12 = {}
    for kind_ in ('came apart', 'first time'):
        rs = [r for r in r5 if r['case']['kind'] == kind_]
        van = Counter()
        for r in rs:
            for k, v in r['swaps'].items():
                if v.get('applies') and not v['survives']:
                    van[k] += 1
        p12[kind_] = {'cases': len(rs), 'vanish under': dict(van),
                      'survive every swap': [(r['case']['law_name'], r['case']['base'], r['case']['start'],
                                              r['case']['verdicts']) for r in rs if all(
                                                  v['survives'] for v in r['swaps'].values() if v.get('applies'))],
                      'survive the ration swap': [(r['case']['law_name'], r['case']['base'], r['case']['start'])
                                                  for r in rs if r['swaps']['ration']['survives']],
                      'vanish under the knot law': [(r['case']['law_name'], r['case']['base'], r['case']['start'])
                                                    for r in rs if not r['swaps']['knot law']['survives']],
                      'STEPS-2 cases surviving UP-TO-2': [(r['case']['law_name'], r['case']['base'],
                                                           r['case']['start']) for r in rs if
                                                          'STEPS-2' in r['case']['law_name'] and
                                                          r['swaps']['STEPS-k/UP-TO-k'].get('survives')]}
    ca, ftm = p12['came apart'], p12['first time']
    exc = [x for x in ftm['survive every swap']]
    ok = (not ca['survive the ration swap'] and not ca['STEPS-2 cases surviving UP-TO-2'] and
          not ca['vanish under the knot law'] and len(exc) == 1 and exc[0][0] == 'MET(BY-COUNT)' and
          exc[0][1] == 'COPY-LAW(OFFSHOOT)')
    V['P12'] = {'verdict': 'holds' if ok else 'fails', 'numbers': p12,
                'battery': [{'case': r['case'], 'survives': {k: v.get('survives') for k, v in r['swaps'].items()
                                                              if v.get('applies')}} for r in r5]}
    # ---------------------------------------------------------------- P16 (run 7)
    wait = [r for r in r7 if r['base'] == 'COPY-LAW(WAIT)+HOLD']
    nwa = [p for r in wait for p in r['pairs'] if s1(p) and not p['wholly_apart']]
    cd_wait = [(r['start'], r['law_name'], r['knot_law'], p['s']) for r in wait for p in r['pairs'] if s1(p) and
               p['course_differs'] is not None]
    q_hold = [r for r in r7 if r['law_name'].startswith('Q(')]
    q_apart = [(r['base'], r['start'], r['law_name'], r['knot_law'], r['all_pairs']['came_apart'])
               for r in q_hold if r['all_pairs']['came_apart']]
    cd_all = Counter((r['base'], r['law_name']) for r in r7 for p in r['pairs'] if s1(p) and
                     p['course_differs'] is not None)
    V['P16'] = {'verdict': 'holds' if nwa and all(p['one_part_again'] for p in nwa) and not cd_wait and not q_apart
                else 'fails',
                'numbers': {'COPY-LAW(WAIT)+HOLD: pairs not wholly apart': len(nwa),
                            'of them one part again': sum(1 for p in nwa if p['one_part_again']),
                            'COPY-LAW(WAIT)+HOLD: course differs': cd_wait,
                            'Q with HOLD: parts that come apart (runs)': q_apart,
                            'every HOLD-arm course-differs mark at s >= 1, by base and law': {str(k): v for k, v in
                                                                                             cd_all.items()},
                            'HOLD arm, the two-knot start s = 0 pair': [(r['base'], r['law_name'], r['knot_law'],
                                                                         p['one_part_again'], p['course_differs'])
                                                                        for r in r7 for p in r['pairs'] if p['s'] == 0]}}
    # ---------------------------------------------------------------- P17 joint births
    jb = Counter()
    for lab, rows in (('run1', r1), ('run3', r3), ('run7', r7)):
        for r in rows:
            for p in r['pairs']:
                if s1(p) and p['joint_birth'] is not None:
                    jb[(lab, kind(p), r['law_name'], r['base'])] += 1
    V['P17'] = {'verdict': 'reported (open)', 'numbers': {' | '.join(k): v for k, v in sorted(jb.items())},
                'arm A joint births at s >= 1': sum(v for k, v in jb.items() if ARM_A(k[2]))}
    # ---------------------------------------------------------------- P18 knots
    fails = []
    tot = Counter()
    for lab, rows in (('run1', r1), ('run3', r3), ('run7', r7), ('carry-alt (supplementary)', rca)):
        for r in rows:
            k = r['knot_tests']
            tot['verdicts'] += k['verdicts']
            tot['disagreements'] += k['n_disagree']
            tot['untested'] += k['n_untested']
            tot['birth vs direct compared'] += k['birth_vs_direct']
            for f in k['fails']:
                fails.append((lab, r['knot_law'], r['law_name'], r['base'], r['start'], f['kind'], f['parents'],
                              f['places'], f['made']))
            for p in r['pairs']:
                for key in ('kt_B1', 'kt_B2', 'kt_M', 'kt_M2'):
                    if key in p:
                        tot['comparison-run verdicts'] += p[key]['verdicts']
                        tot['disagreements'] += p[key]['n_disagree']
                        tot['untested'] += p[key]['n_untested']
                        for f in p[key]['fails']:
                            fails.append((lab + ' ' + key + ' s=%d' % p['s'], r['knot_law'], r['law_name'], r['base'],
                                          r['start'], f['kind'], f['parents'], f['places'], f['made']))
    for r in r2:
        if 'stats' in r:
            tot['run 2 verdicts'] += r['stats']['knot_verdicts']
            tot['disagreements'] += r['stats']['method_disagreements']
            tot['untested'] += r['stats']['untested']
            if r['stats']['knot_fails']:
                fails.append(('run2', r['knot_law'], r['id'], '', '', 'see examples', None, None, None))
    uniq = sorted(set(fails), key=str)
    reg = [f for f in uniq if not f[0].startswith('carry-alt')]
    nae_bad = [f for f in reg if f[1] == 'nae' and 'CARRY' not in f[2]]
    par_bad = [f for f in reg if f[1] == 'parity' and not (f[5] == 'join' and (f[6] or 0) >= 3) and
               'FLOOR0' not in str(f[2]) and 'ONE-FEWER' not in str(f[2])]
    sup = [list(f) for f in uniq if f[0].startswith('carry-alt')]
    V['P18'] = {'verdict': 'holds' if not nae_bad and not par_bad and tot['disagreements'] == 0 else 'fails',
                'numbers': dict(tot), 'failing knots (distinct rows)': [list(f) for f in uniq][:80],
                'not-all-equal failures outside CARRY': nae_bad, 'parity failures not at joins of 3+ parents': par_bad,
                'supplementary CARRY run (other reading), failures (not registered)': sup,
                'run 2 failure examples': [{'id': r['id'], 'examples': [e for e in r['examples'] if 'fail' in e['kind']]}
                                           for r in r2 if 'stats' in r and r['stats']['knot_fails']]}
    return V



def reruns():
    """P4 and P7: short reruns of named cases (deterministic), with their records."""
    import pm
    import paired as P
    out = {'P4': [], 'P7': {}}
    for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
        for kl in ('nae', 'parity'):
            for rule, ch in (('Q', 'OLDEST'), ('Q', 'NEWEST'), ('SHORT-TAKES', 'OLDEST'), ('SHORT-TAKES', 'NEWEST')):
                kw = dict(ration='FLOOR1', treatment=t, knot_law=kl, choice=ch)
                if rule == 'Q':
                    kw['take'] = 'Q'
                else:
                    kw['treatment'] = 'SHORT-TAKES'
                    kw['base_treatment'] = None
                law = pm.Law(**{k: v for k, v in kw.items() if k != 'base_treatment'})
                A = pm.Run(pm.start('three-knot'), law)
                v = P.RunView(A)
                parts = [len(v.roster(x).parts) for x in range(A.rounds_done + 1)]
                r2 = A.records[1]
                row = {'treatment': t, 'knot_law': kl, 'law': rule + '(' + ch + ')', 'parts_per_round': parts,
                       'round2_groups': r2['groups'], 'round2_short': r2['short']}
                if rule == 'Q':
                    row['ok'] = ([3, 4, 5] in r2['groups'] and all(n == 1 for n in parts))
                else:
                    js = [b for b in r2['births'] if b['kind'] == 'join' and 3 in b['parents']]
                    row['round2_joins_of_3'] = [(b['parents'], b['given_shared']) for b in js]
                    row['ok'] = (3 in r2['short'] and any(b['given_shared'] for b in js) and
                                 all(n == 1 for n in parts[:9]))
                out['P4'].append(row)
    for t in ('CANCEL-RETIRE', 'CANCEL-WAIT'):
        law = pm.Law('FLOOR1', t, take='MET', choice='OLDEST', knot_law='nae')
        A = pm.Run(pm.start('three-knot'), law)
        r1 = A.records[0]
        r2 = A.records[1]
        out['P7'][t] = {'round1': [(b['id'], b['kind'], b['parents'], b['inputs']) for b in r1['births']],
                        'round2': {'groups': r2['groups'], 'short': r2['short'], 'retired': r2['retired'],
                                   'waiting': r2['waiting'], 'births': r2['n_births'], 'jammed': r2['jammed'],
                                   'stopped': r2['stopped']},
                        'final_knots': A.S.n_knots}
    return out


def run4_verdicts(r4, r6, rr):
    V = {}
    by = defaultdict(list)
    for r in r4:
        if 'swap' in r:
            by[('swap', r['case'])].append(r)
        else:
            by[r['case']].append(r)

    def pair_of(r, s, X):
        for p in r['pairs']:
            if p['s'] == s and p['X'] == X:
                return p
    # P4, P7
    V['P4'] = {'verdict': 'holds' if all(x['ok'] for x in rr['P4']) else 'fails', 'numbers': rr['P4']}
    p7 = rr['P7']
    ok7 = (p7['CANCEL-RETIRE']['round1'] == [[3, 'join', [1, 2], [4, 6]], [4, 'offshoot', [1], [5, 2]],
                                              [5, 'offshoot', [2], [7, 0]]] or
           p7['CANCEL-RETIRE']['round1'] == [(3, 'join', [1, 2], [4, 6]), (4, 'offshoot', [1], [5, 2]),
                                              (5, 'offshoot', [2], [7, 0])])
    ok7 = ok7 and sorted(p7['CANCEL-RETIRE']['round2']['retired']) == [3, 4, 5] and \
        p7['CANCEL-RETIRE']['final_knots'] == 6 and p7['CANCEL-WAIT']['round2']['jammed']
    V['P7'] = {'verdict': 'holds' if ok7 else 'fails', 'numbers': p7}
    # P8
    rows = by['smallest case']
    res = {}
    ok8 = True
    for r in rows:
        p = pair_of(r, 2, [6, 7])
        L = r['listing']
        b3 = {b['id']: b for b in L[2]['births']}
        chk = {'one part again': p['one_part_again'], 'course differs B(i)': p['course_differs'],
               'course differs B(ii)': p['b2']['course_differs'] if isinstance(p['b2'], dict) else p['b2'],
               'demand line': p['demand_line'], 'way': p['way'], 'confirmed': p['confirmed'],
               'joint birth': p['joint_birth'], 'verdict': p['verdict'], 'link classes': (p['link'] or {}).get(
                   'link_classes'), 'knot fails through round 8': r['knot_tests']['n_fails'],
               'knot verdicts': r['knot_tests']['verdicts'],
               'round 1': [(b['id'], b['kind'], b['parents'], b['f']) for b in L[0]['births']],
               'round 2 parts': L[1]['parts'], 'round 2 retired': L[1]['retired'],
               'round 3 takes of 12..15': {u: b3[u]['rule_takes'] for u in (12, 13, 14, 15)},
               'round 4 retired': L[3]['retired'], 'round 4 births': [(b['id'], b['parents']) for b in L[3]['births']],
               'knots after round 5': r['per_round'][5]['knots']}
        good = (p['one_part_again'] == 3 and p['course_differs'] == 4 and chk['course differs B(ii)'] == 4 and
                p['demand_line'] == 3 and p['way'] == 'a group or owing' and p['confirmed'] == 'through a meeting'
                and p['joint_birth'] is None and p['verdict'] == 'through a start knot' and
                r['knot_tests']['n_fails'] == 0 and chk['knots after round 5'] == 20 and
                chk['round 3 takes of 12..15'] == {12: [0], 13: [0], 14: [2], 15: [2]} and
                sorted(L[3]['retired']) == [12, 13, 14, 15])
        ok8 = ok8 and good
        res[r['knot_law']] = chk
    V['P8'] = {'verdict': 'holds' if ok8 else 'fails', 'numbers': res}
    # P9, P10 swaps
    for key, label, stands, vanish, rev_verdict in (
            ('P9', 'smallest case', ['parity', 'order reversed', 'demand before the takes', 'fresh by parents', 'HOLD'],
             ['NEWEST', 'BY-COUNT', 'CAP-3', 'UP-TO-2'], 'through a knot the growth made'),
            ('P10', 'through the retired join', [], ['order reversed', 'CAP-3', 'UP-TO-2'], 'through a start knot')):
        sw = {r['swap']: r for r in by[('swap', label)]}
        out = {k: {'stands': v['stands'], 'verdicts': sorted({m['verdict'] for m in v['confirmed_came_apart']}),
                   'n_marks': len(v['confirmed_came_apart'])} for k, v in sw.items()}
        ok = all(sw[k]['stands'] for k in stands) and not any(sw[k]['stands'] for k in vanish) and \
            sw['names reversed']['stands'] and rev_verdict in out['names reversed']['verdicts']
        if key == 'P9':
            nr = sw['names reversed']['confirmed_came_apart']
            out['names reversed: linking knots'] = [m.get('link', {}).get('link_classes') for m in nr]
        if key == 'P10':
            r = by['through the retired join'][0]
            p = pair_of(r, 2, [6, 7])
            out['case'] = {'one part again': p['one_part_again'], 'course differs': p['course_differs'],
                           'verdict': p['verdict'], 'link classes': (p['link'] or {}).get('link_classes')}
            ok = ok and p['one_part_again'] == 3 and p['course_differs'] == 4 and \
                p['verdict'] == 'through a knot the growth made' and '3' in (p['link'] or {}).get('link_classes', {})
        V[key] = {'verdict': 'holds' if ok else 'fails', 'numbers': out}
    # P13
    sm = by['smallest case'][0]
    cn = [c for c in sm['choice_is_necessary'] if c['s'] == 2 and c['X'] == [6, 7]][0]['by_choice']
    a = {c: v['course_differs'] for c, v in cn.items()}
    ok_a = a['OLDEST'] and a['IN-TURN'] and not a['NEWEST'] and not a['BY-COUNT'] and not a['BY-RECEIVED']
    ring = by['P13 ring'][0]
    given = [t for t in ring['tests'] if t['Y_is_ring_part'] and not t['X_is_ring_part']]
    dep = [t for t in given if t['by_choice']['BY-COUNT']['course_differs'] or
           t['by_choice']['BY-RECEIVED']['course_differs']]
    ok_b = bool(dep) and all(not t['by_choice'][c]['course_differs'] for t in given for c in
                             ('OLDEST', 'NEWEST', 'IN-TURN'))
    V['P13'] = {'verdict': 'holds' if ok_a and ok_b else 'fails',
                'numbers': {'smallest case, first copy only': a,
                            'Ring(5,3) RING-LAW STEPS-2(OLDEST), X a given-off part, Y the ring part':
                                [{'s': t['s'], 'X': t['X'], 'by_choice': {c: v['course_differs'] for c, v in
                                                                         t['by_choice'].items()}} for t in given],
                            'other orientations (X the ring part or neither)': [
                                {'s': t['s'], 'X': t['X'], 'Y': t['Y'], 'by_choice': {
                                    c: v['course_differs'] for c, v in t['by_choice'].items()}}
                                for t in ring['tests'] if not (t['Y_is_ring_part'] and not t['X_is_ring_part'])]}}
    # P14
    w = []
    for lab in ('smallest case', 'through the retired join'):
        for r in by[lab]:
            for x in r.get('what_the_other_is', []):
                w.append({'case': lab, 'knot_law': r['knot_law'], 's': x['s'], 'X': x['X'], 'found': x.get('found'),
                          'X in the larger-founder run': x.get('X_variant'), 'course differs': x.get('course_differs'),
                          'rounds compared': x.get('rounds_compared')})
    sup = jl('run4_what_the_other_is.jsonl')
    ap = [x for x in sup if x.get('applicable')]
    V['P14'] = {'verdict': 'reported (open)', 'numbers': w,
                'supplement (every three-knot pair with a course-differs mark in runs 1 and 3)': {
                    'pairs': len(sup), 'applicable (Y from knot 2 only, X not from knot 2)': len(ap),
                    'laws of the applicable pairs': sorted({'%s / %s' % (x['base'], x['law_name']) for x in ap}),
                    'applicable pairs whose course differs with what the other is': [
                        (x['base'], x['law_name'], x['knot_law'], x['s'], x['X'], x.get('course_differs'))
                        for x in ap if x.get('course_differs')]}}
    # P15
    p15 = []
    ok15 = True
    for r in r6:
        row = {k: r.get(k) for k in ('start', 'base', 'knot_law', 'X', 'Y', 'wholly_apart', 'placed',
                                      'one_part_at_round_s_with_placed_knot', 'one_part_again', 'joint_birth',
                                      'course_differs_against_Y_barred', 'course_differs_against_no_placed_knot',
                                      'verdict')}
        row['placed knot short/retired/waiting'] = [(x['t'], x['short'], x['retired'], x['waiting'])
                                                    for x in r.get('placed_knot_record', [])][:3]
        row['knot tests'] = r.get('knot_tests')
        p15.append(row)
        cy = r['course_differs_against_Y_barred']['round']
        cn_ = r['course_differs_against_no_placed_knot']['round']
        if r['base'] == 'COPY-LAW(RETIRE)':
            ok15 = ok15 and r['one_part_at_round_s_with_placed_knot'] and cy is None and cn_ is None
        elif r['base'] == 'COPY-LAW(WAIT)':
            ok15 = ok15 and cy == 3
        else:
            ok15 = ok15 and cy is None and cn_ is not None
    V['P15'] = {'verdict': 'holds' if ok15 else 'fails', 'numbers': p15}
    return V


def main():
    S = {}
    S['gate'] = gate()
    r1 = jl('run1.jsonl.gz')
    r3 = jl('run3.jsonl.gz')
    r7 = jl('run7.jsonl.gz')
    r2 = [r for r in jl('run2.jsonl') + jl('run2b.jsonl') + jl('run2c.jsonl') + jl('run2_long.jsonl') if 'stats' in r]
    r4 = jl('run4.jsonl')
    r5 = jl('run5.jsonl')
    r6 = jl('run6.jsonl')
    rca = jl('carry-alt.jsonl.gz')
    S['errors'] = [{k: r.get(k) for k in ('run', 'base', 'start', 'law_name', 'knot_law', 'error')}
                   for r in r1 + r3 + r7 + rca if 'error' in r] + [r for r in r2 if 'error' in r]
    S['run1_pairs'] = pairs_table(r1)
    S['run3_pairs'] = pairs_table(r3)
    S['run7_pairs'] = pairs_table(r7)
    S['carry_alt_pairs'] = pairs_table(rca)
    S['marks'] = marks_list(r1, 'run1') + marks_list(r3, 'run3') + marks_list(r7, 'run7')
    S['verdicts'] = verdicts(S, r1, r3, r7, r2, r4, r5, r6, rca)
    S['reruns'] = reruns()
    S['verdicts'].update(run4_verdicts(r4, r6, S['reruns']))
    S['verdicts'] = {k: S['verdicts'][k] for k in sorted(S['verdicts'], key=lambda x: int(x[1:]))}
    S['holders'] = {}
    for r in r1 + r3 + rca:
        S['holders'][r['law_name']] = max(S['holders'].get(r['law_name'], 0), r['max_holders'])
    S['stops'] = Counter('%s %s' % (r.get('run'), r['stop']) for r in r1 + r3 + r7 + rca)
    S['run2'] = [{k: r.get(k) for k in ('id', 'mode', 'n_histories_counted', 'stats', 'seconds', 'error')} for r in r2]
    done = {r['id'] for r in r2 if 'stats' in r}
    import enum_choices as EC
    S['run2_not_finished'] = [c['id'] for c in EC.cases() if c['id'] not in done]
    prog = {}
    for x in jl('run2_progress.jsonl') + jl('run2_long_progress.jsonl'):
        if x['id'] not in done:
            prog[x['id']] = {'mode': x['mode'], 'histories_so_far': x['histories_so_far'], 'seconds': x['seconds'],
                             'one_part_again_so_far': x['stats_so_far']['one_part_again'],
                             'joint_births_so_far': x['stats_so_far']['joint_births'],
                             'knot_fails_so_far': x['stats_so_far']['knot_fails'],
                             'pairs_wholly_apart_so_far': x['stats_so_far']['pairs_wholly_apart']}
    S['run2_progress_of_unfinished'] = prog
    C.write_json('summary_core.json', S)
    return S


if __name__ == '__main__':
    S = main()
    for k, v in S['verdicts'].items():
        print(k, v['verdict'])
