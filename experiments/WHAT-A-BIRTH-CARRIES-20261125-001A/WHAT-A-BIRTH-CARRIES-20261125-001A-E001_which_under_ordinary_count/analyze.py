"""Verdicts of WHAT-A-BIRTH-CARRIES-20261125-001A-E001: the cells, the per-pair counts, the predictions Q0 to Q7, the
checks of S1 to S5, the knot test; writes summary.json and summary.md."""
import sys

sys.dont_write_bytecode = True

import gzip
import json
import os
from collections import Counter, defaultdict

import common
from common import log
import wbc

PREF = (2, 3, 4)
LAWS = (('OLDEST', 'nae'), ('OLDEST', 'parity'), ('NEWEST', 'nae'), ('NEWEST', 'parity'))
KL = {'nae': 'not-all-equal', 'parity': 'parity'}
TAKE = {'OLDEST': 'take-the-oldest', 'NEWEST': 'take-the-newest'}


def load_json(name):
    p = common.out_path(name)
    if not os.path.exists(p):
        return None
    with (gzip.open if name.endswith('.gz') else open)(p, 'rt') as f:
        return json.load(f)


def jl(name):
    """Every complete line of a JSON-lines file; a gzip stream cut off by a stopped run is read up to its last whole
    line (deviations 28)."""
    p = common.out_path(name)
    if not os.path.exists(p):
        return []
    out = []
    try:
        with (gzip.open if name.endswith('.gz') else open)(p, 'rt') as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    break
    except EOFError:
        pass
    return out


def index_from_runs(name):
    """The run index, rebuilt from the per-run records (written only when a run ends normally otherwise), keeping
    only jobs with every one of their 2^h records, their pairs and their reading at fixed h and ν."""
    recs = jl(name + '_runs.jsonl.gz')
    by_job = defaultdict(list)
    for rec in recs:
        lawd = rec['law']
        key = (lawd['ration'], lawd['treatment'], lawd['take'], lawd['choice'], lawd['knot_law'])
        by_job[(key, rec['h'], rec['nu'])].append(rec)
    hands = {(tuple(x['key']), x['h'], x['nu']) for x in jl(name + '_handed.jsonl.gz')}
    index = []
    complete = set()
    for (key, h, nu), rs in by_job.items():
        if len(rs) != 2 ** h or (key, h, nu) not in hands:
            continue
        complete.add((key, h, nu))
        for rec in rs:
            index.append({'key': list(key), 'h': rec['h'], 'nu': rec['nu'], 'a': rec['a'], 'usable': rec['usable'],
                          'rounds_read': rec['rounds_read'], 'stop': rec['stop'],
                          'guard': rec['guard'] and rec['guard']['what'], 'gc': rec['global_class'],
                          'meet': rec['meet_round'], 'meet_how': rec['meet_how'],
                          'link': [(x['class'], x['is_X_start'], x['is_Y_start'], x['holds_e'])
                                   for x in rec['linking'] or []],
                          's4': rec['s4'], 'short': rec['short_after1'], 'implied': rec['implied_rounds'],
                          'kt': rec['knot_test'], 'fp': rec['fingerprint'], 'sec': rec['seconds'],
                          'knots': rec['knots']})
    return index, complete


def gc(r, R):
    v = r['gc'].get(str(R), r['gc'].get(R))
    return v


# ------------------------------------------------------------------------------------------------------ cells
def cells_of(index, key_filter):
    cells = defaultdict(list)
    for r in index:
        k = tuple(r['key'])
        if not key_filter(k):
            continue
        cells[(k, r['h'], r['a'])].append(r)
    return cells


def cell_rounds(runs):
    return min(r['rounds_read'] for r in runs)


def cset(runs, R):
    return {gc(r, R) for r in runs if r['rounds_read'] >= R}


def compare_cells(ca, cb):
    Rst = min(cell_rounds(ca), cell_rounds(cb), 4)
    if Rst < 2:
        return {'prefix': Rst, 'verdict': 'undecided',
                'undecided_runs': sum(1 for r in ca + cb if r['rounds_read'] < 2)}
    by = {}
    for R in range(2, Rst + 1):
        A, B = cset(ca, R), cset(cb, R)
        by[R] = {'disjoint': not (A & B), 'shared': len(A & B), 'nA': len(A), 'nB': len(B)}
    return {'prefix': Rst, 'verdict': 'disjoint' if by[Rst]['disjoint'] else 'not disjoint', 'by_prefix': by}


def pair_stats(pairs, Rst):
    out = Counter()
    cls = Counter()
    fdk = Counter()
    gap = Counter()
    fcd = Counter()
    fvd = Counter()
    links = Counter()
    for p in pairs:
        out['pairs'] += 1
        mA, mB = p['mA'], p['mB']
        if mA is not None and mB is not None:
            out['both_meet'] += 1
            if mA == mB:
                out['same_round'] += 1
            else:
                gap[mB - mA] += 1
        else:
            out['no_meeting_in_one'] += 1
        if p['same_meeting']:
            out['same_meeting'] += 1
        ce = {int(k): v for k, v in p['course_equal'].items()}
        differ = (Rst in ce and not ce[Rst])
        if differ:
            out['courses_differ'] += 1
            f = min(R for R, v in ce.items() if not v)
            fcd[f] += 1
        fd = p['fd']
        if fd is not None and fd['round'] <= Rst:
            if differ:
                cls[fd['class']] += 1
                fdk[(fd['round'], fd['kind'], 'J' if p['fd_is_J_demand'] else '')] += 1
                fvd[fd['round']] += 1
            else:
                out['values_differ_courses_equal'] += 1
        elif differ:
            cls['no difference in the values'] += 1
        r9 = (mA is not None and mA == mB and differ and fd is not None and fd['round'] <= Rst and
              fd['class'] == 'through the meeting')
        if r9:
            out['r9_pair_ok'] += 1
        links[tuple(p['linkA'])] += 1
    return {'counts': dict(out), 'attribution': dict(cls), 'first_entry': {repr(k): v for k, v in fdk.items()},
            'meeting_gaps': dict(gap), 'first_course_difference_round': dict(fcd),
            'first_values_difference_round': dict(fvd), 'linking_A': {repr(k): v for k, v in links.items()}}


def analyse_class(label, index, pairs, handed, laws, hs, treatment='CANCEL-RETIRE'):
    res = {'cells': [], 'follows_h': [], 'handed': [], 'distinct_courses': [], 'r9': {}, 'not_run': [],
           'numberings_run': {}}
    NU = {3: 120, 4: 210}
    pairs_by = defaultdict(list)
    for p in pairs:
        pairs_by[(tuple(p['key']), p['h'], p['a'], p['b'])].append(p)
    hand_by = defaultdict(list)
    for x in handed:
        hand_by[(tuple(x['key']), x['h'])].append(x)
    for ch, kl in laws:
        key = ('ORD', treatment, 'MET', ch, kl)
        cells = cells_of(index, lambda k: k == key)
        r9_h = {}
        for h in hs:
            okab = []
            nus = {r['nu'] for a in range(h + 1) for r in cells.get((key, h, a), [])}
            res['numberings_run']['%s/%s/h=%d' % (ch, kl, h)] = [len(nus), NU[h]]
            if not nus:
                res['not_run'].append({'take': ch, 'knot_law': kl, 'h': h})
                r9_h[h] = None
                continue
            for a in range(h + 1):
                for b in range(a + 1, h + 1):
                    ca, cb = cells[(key, h, a)], cells[(key, h, b)]
                    cmp_ = compare_cells(ca, cb)
                    ps = pair_stats(pairs_by[(key, h, a, b)], cmp_['prefix'])
                    kt_ok = all(r['kt']['n_fail'] == 0 for r in ca + cb)
                    row = {'numberings_run': len(nus), 'numberings': NU[h],
                           'take': ch, 'knot_law': kl, 'h': h, 'a': a, 'b': b, 'M_a': wbc.M_formula(h, a),
                           'M_b': wbc.M_formula(h, b), 'compare': cmp_, 'pairs': ps, 'knots_pass': kt_ok}
                    res['cells'].append(row)
                    n = ps['counts'].get('pairs', 0)
                    if a >= 1 and cmp_['verdict'] == 'disjoint' and ps['counts'].get('r9_pair_ok', 0) == n and kt_ok:
                        okab.append((a, b))
            r9_h[h] = okab
            # handed in one value / composed (RD 4.4), at the prefix every run of cells 1..h reached
            Rh = min(min(cell_rounds(cells[(key, h, a)]) for a in range(1, h + 1)), 4)
            verdicts = Counter()
            first = Counter()
            extra = Counter()
            ncls = Counter()
            for x in hand_by[(key, h)]:
                v = x['handed'].get(str(Rh), x['handed'].get(Rh))
                if v is None:
                    verdicts['not read at the prefix'] += 1
                    continue
                verdicts[v['verdict']] += 1
                ncls[v['n_classes']] += 1
                if v['verdict'] == 'handed in one value':
                    fi = v['first_inducing']
                    first[(fi['round'], fi['step'], fi['pos_kind'], fi.get('is_J'))] += 1
                    extra['J_demand_r2_induces'] += v['J_demand_r2_induces']
                    extra['demand_alone_induces'] += v['demand_alone_induces']
                    extra['first_is_count'] += v['first_is_count']
            union = set()
            for a in range(1, h + 1):
                union |= cset(cells[(key, h, a)], Rh)
            res['handed'].append({'numberings_run': len(nus), 'numberings': NU[h],
                                  'take': ch, 'knot_law': kl, 'h': h, 'prefix': Rh, 'verdicts': dict(verdicts),
                                  'first_inducing': {repr(k): v for k, v in first.items()}, 'extra': dict(extra),
                                  'classes_of_P': dict(ncls)})
            res['distinct_courses'].append({'numberings_run': len(nus), 'numberings': NU[h],
                                            'take': ch, 'knot_law': kl, 'h': h, 'prefix': Rh,
                                            'distinct': len(union)})
        res['r9'][(ch, kl)] = {'h3': r9_h.get(3), 'h4': r9_h.get(4),
                               'holds': None if (r9_h.get(3) is None or r9_h.get(4) is None)
                               else (bool(r9_h.get(3)) and bool(r9_h.get(4)))}
        if 3 in hs and 4 in hs and cells.get((key, 3, 0)) and cells.get((key, 4, 0)):
            for a in range(0, 4):
                cmp_ = compare_cells(cells[(key, 3, a)], cells[(key, 4, a)])
                res['follows_h'].append({'take': ch, 'knot_law': kl, 'a': a, 'compare': cmp_})
    res['r9'] = {repr(k): v for k, v in res['r9'].items()}
    return res


# ------------------------------------------------------------------------------------------ S1, S3, S4, S5 checks
def s_checks(index, label):
    out = {'runs': 0, 's4_ok': 0, 's4_fail': [], 'short': Counter(), 'short_examples': [],
           'meet2_a_ge_1': 0, 'a_ge_1': 0, 'meet_not2': [], 'q2_fail': []}
    for r in index:
        out['runs'] += 1
        s4 = r['s4']
        if s4 is None:
            continue
        k = tuple(r['key'])
        if s4['all_ok']:
            out['s4_ok'] += 1
        else:
            out['s4_fail'].append({'key': k, 'h': r['h'], 'nu': r['nu'], 'usable': r['usable'], 's4': s4})
        if r['a'] >= 1:
            out['a_ge_1'] += 1
            ok2 = s4.get('J_found') and s4.get('takes_e') and s4.get('D_ok') and s4.get('f_ok') and \
                s4.get('places_ok')
            if not ok2:
                out['q2_fail'].append({'key': k, 'h': r['h'], 'nu': r['nu'], 'usable': r['usable']})
            if r['meet'] == 2:
                out['meet2_a_ge_1'] += 1
            else:
                out['meet_not2'].append({'key': k, 'h': r['h'], 'nu': r['nu'], 'usable': r['usable'],
                                         'meet': r['meet']})
        if r['a'] >= 1 and r['meet'] is not None:
            L = r['link']
            ys = any(x[2] and x[3] for x in L)
            xs = any(x[1] for x in L)
            others = [x for x in L if not (x[1] or x[2])]
            ytook = (s4.get('y_births_take_e') or 0) > 0
            ok = ys and (xs == ytook) and not others and all(x[0].startswith('start knot') for x in L)
            out.setdefault('link_ok', 0)
            out.setdefault('link_fail', [])
            out.setdefault('link_classes', Counter())
            out['link_ok'] += ok
            if not ok and len(out['link_fail']) < 10:
                out['link_fail'].append({'key': k, 'h': r['h'], 'nu': r['nu'], 'usable': r['usable'], 'link': L,
                                         'y_births_take_e': s4.get('y_births_take_e')})
            out['link_classes'][repr(sorted(set(x[0] for x in L)))] += 1
        for t, u, made, after_implied in r['short']:
            out['short'][(k[4], after_implied)] += 1
            if len(out['short_examples']) < 10:
                out['short_examples'].append({'key': k, 'h': r['h'], 'nu': r['nu'], 'usable': r['usable'],
                                              'round': t, 'knot': u, 'made': made, 'after_implied': after_implied})
    out['short'] = {repr(k): v for k, v in out['short'].items()}
    if 'link_classes' in out:
        out['link_classes'] = dict(out['link_classes'])
    out['s4_fail'] = out['s4_fail'][:20]
    out['meet_not2'] = out['meet_not2'][:20]
    out['q2_fail'] = out['q2_fail'][:20]
    return out


def registered_checks():
    """S3 on the registered numbering (ν = 0, made-h as written), S5 on it under OLDEST, and the disclosed sweep of
    the registered numbering at a = h (Y_3 to Y_6) and at a = 0."""
    reg = {}
    for rec in jl('run1_runs.jsonl.gz') + jl('run1r_runs.jsonl.gz'):
        if rec['nu'] != 0:
            continue
        reg[(rec['law']['choice'], rec['law']['knot_law'], rec['h'], tuple(rec['usable']))] = rec
    R2 = load_json('run2.json.gz')
    for rec in (R2['runs'] if R2 else []):
        reg[(rec['law']['choice'], rec['law']['knot_law'], rec['h'], tuple(rec['usable']))] = rec
    s3 = []
    s5 = []
    for (ch, kl, h, us), rec in sorted(reg.items()):
        if h not in (3, 4):
            continue
        a = len(us)
        s4 = rec['s4']
        ok_members = all(hu == h - 1 and ow == a - 1 and not sh for _, hu, ow, sh in s4['y_members'])
        ok_jo = all(j == a - 1 and o == h - a for j, o in s4['y_joins_offshoots'])
        M = wbc.M_formula(h, a)
        s3.append({'take': ch, 'knot_law': kl, 'h': h, 'usable': list(us), 'members_hold_owe_ok': ok_members,
                   'joins_offshoots_ok': ok_jo, 'every_birth_takes_e': s4['every_birth_takes_e'],
                   'x_births_D': s4['x_births_D'], 'x_births_D_ok': all(d == 2 + M for d in s4['x_births_D']),
                   'M': M})
    for kl in ('nae', 'parity'):
        for h in (3, 4):
            A = reg.get(('OLDEST', kl, h, tuple(range(3, 3 + h - 1))))
            B = reg.get(('OLDEST', kl, h, tuple(range(3, 3 + h))))
            if not A or not B:
                continue
            nA, nB = A['s4']['n_births_r2'], B['s4']['n_births_r2']
            r3A = A['round_summaries'].get('3', [])
            r3B = B['round_summaries'].get('3', [])
            joinsA = [x for x in r3A if x[0] == 'join']
            joinsB = [x for x in r3B if x[0] == 'join']
            take1 = all(x[2] == [1] for x in joinsA + joinsB)
            DA = sorted({x[3] for x in joinsA})
            DB = sorted({x[3] for x in joinsB})
            same3 = None
            if 3 in [int(k) for k in A['courses']] and 3 in [int(k) for k in B['courses']]:
                same3 = wbc.same_course(A['courses']['3'], B['courses']['3'])
            same2 = wbc.same_course(A['courses']['2'], B['courses']['2'])
            s5.append({'knot_law': kl, 'h': h, 'births_r2': [nA, nB], 'expected': 3 + wbc.M_formula(h, h),
                       'round3_joins_take_1': take1, 'round3_join_D': [DA, DB],
                       'x_round_births': [A['x_round_births'], B['x_round_births']],
                       'course_equal_r2': same2, 'course_equal_r3': same3})
    sweep = []
    for ch in ('OLDEST', 'NEWEST'):
        for kl in ('nae', 'parity'):
            full = [(h, reg.get((ch, kl, h, tuple(range(3, 3 + h))))) for h in (3, 4, 5, 6)]
            for i in range(4):
                for j in range(i + 1, 4):
                    (ha, A), (hb, B) = full[i], full[j]
                    if not A or not B:
                        continue
                    last = min(A['rounds_read'], B['rounds_read'], 4)
                    eq = {R: wbc.same_course(A['courses'][str(R)], B['courses'][str(R)])
                          for R in range(2, last + 1)}
                    sweep.append({'take': ch, 'knot_law': kl, 'a': 'h', 'hA': ha, 'hB': hb, 'course_equal': eq,
                                  'first_difference': min([R for R, v in eq.items() if not v], default=None)})
            A, B = reg.get((ch, kl, 3, ())), reg.get((ch, kl, 4, ()))
            if A and B:
                last = min(A['rounds_read'], B['rounds_read'], 4)
                eq = {R: wbc.same_course(A['courses'][str(R)], B['courses'][str(R)]) for R in range(2, last + 1)}
                sweep.append({'take': ch, 'knot_law': kl, 'a': 0, 'hA': 3, 'hB': 4, 'course_equal': eq,
                              'first_difference': min([R for R, v in eq.items() if not v], default=None)})
    return {'S3': s3, 'S5': s5, 'sweep': sweep}


def main():
    common.check_frozen()
    S = {'gate': {}, 'N': {}, 'P': {}, 'run1': {}, 'run1b': {}, 'run2': {}}
    # ---- run G
    eng = []
    for i in range(4):
        eng += jl('G_engine_%d_of_4.jsonl' % i)
    rest = load_json('G_rest.json')
    S['gate'] = {'engine_runs': len(eng), 'engine_equal': sum(r['equal'] for r in eng),
                 'engine_differ': [r for r in eng if not r['equal']],
                 'engine_stops': dict(Counter('%s/%s' % (r['stop'], r['guard'] and r['guard'][1]) for r in eng)),
                 'listing_equal': rest['gate_listing']['equal'], 'listing_lines': rest['gate_listing']['lines_compared'],
                 'listing_runs_registered_bounds': rest['gate_listing']['registered_bounds_runs'],
                 'records': [(r['name'], r['equal'], r['got']) for r in rest['attribution_records']],
                 'symmetric_identical': sum(r['identical'] for r in rest['symmetric_pairs']),
                 'symmetric_pairs': len(rest['symmetric_pairs'])}
    q0 = (S['gate']['engine_runs'] == 648 and S['gate']['engine_equal'] == 648 and S['gate']['listing_equal'] and
          all(x[1] for x in S['gate']['records']) and S['gate']['symmetric_identical'] == 100)
    # ---- N
    idxN = load_json('runN_index.json.gz') or []
    nres = {}
    for kl in ('nae', 'parity'):
        rs = [r for r in idxN if r['key'][4] == kl]
        if not rs:
            continue
        Rn = min(min(r['rounds_read'] for r in rs), 4)
        by = {R: len({gc(r, R) for r in rs if r['rounds_read'] >= R}) for R in PREF if R <= Rn}
        nres[kl] = {'runs': len(rs), 'prefix': Rn, 'courses_by_prefix': by,
                    'meetings': sum(1 for r in rs if r['meet'] is not None),
                    'stops': dict(Counter('%s/%s/%d' % (r['stop'], r['guard'], r['rounds_read']) for r in rs)),
                    'implied_runs': sum(1 for r in rs if r['implied']),
                    'knot_fail': sum(r['kt']['n_fail'] for r in rs)}
    S['N'] = nres
    q5 = bool(nres) and all(all(v == 1 for v in x['courses_by_prefix'].values()) for x in nres.values())
    # ---- P
    P = load_json('runP.json.gz')
    if P:
        S['P'] = {'comparisons': P['comparisons'],
                  'runs': [{'h': r['h'], 'a': r['a'], 'law': r['law_name'], 'rounds_read': r['rounds_read'],
                            'stop': r['stop'], 'guard': r['guard'], 'knot_fail': r['knot_test']['n_fail'],
                            'meet': r['meet_round'], 'x_round_births': r['x_round_births']} for r in P['runs']]}
    q6 = bool(P) and all(c['criterion']['passes'] for c in P['comparisons'])
    # ---- run 1
    idx1 = load_json('run1_index.json.gz')
    if idx1 is None:
        idx1, done1 = index_from_runs('run1')
    else:
        done1 = {(tuple(r['key']), r['h'], r['nu']) for r in idx1}
    pairs1 = [p for p in jl('run1_pairs.jsonl.gz') if (tuple(p['key']), p['h'], p['nu']) in done1]
    hand1 = [x for x in jl('run1_handed.jsonl.gz') if (tuple(x['key']), x['h'], x['nu']) in done1]
    # the second part of run 1 (deviations 32): take-the-newest under parity only, its own course classes
    idx1r = load_json('run1r_index.json.gz')
    if idx1r is None:
        idx1r, done1r = index_from_runs('run1r')
    else:
        done1r = {(tuple(r['key']), r['h'], r['nu']) for r in idx1r}
    assert not (done1 & done1r)
    idx1 = idx1 + idx1r
    pairs1 += [p for p in jl('run1r_pairs.jsonl.gz') if (tuple(p['key']), p['h'], p['nu']) in done1r]
    hand1 += [x for x in jl('run1r_handed.jsonl.gz') if (tuple(x['key']), x['h'], x['nu']) in done1r]
    done1 = done1 | done1r
    S['run1_second_part_runs'] = len(idx1r)
    S['run1_jobs'] = {repr(k): v for k, v in Counter((key[3], key[4], h) for key, h, nu in done1).items()}
    if idx1:
        S['run1'] = analyse_class('1', idx1, pairs1, hand1, LAWS, (3, 4))
        S['run1']['checks'] = s_checks(idx1, '1')
        S['run1']['runs'] = len(idx1)
        S['run1']['stops'] = dict(Counter('%s/%s/%s/%d' % (r['key'][3], r['key'][4], r['guard'], r['rounds_read'])
                                          for r in idx1))
        S['run1']['knot_test'] = {'verdicts': sum(r['kt']['verdicts'] for r in idx1),
                                  'fails': sum(r['kt']['n_fail'] for r in idx1),
                                  'disagree': sum(r['kt']['n_disagree'] for r in idx1),
                                  'untested': sum(r['kt']['n_untested'] for r in idx1)}
        secs = defaultdict(list)
        for r in idx1:
            secs[(r['key'][3], r['key'][4])].append(r['sec'])
        S['run1']['seconds_per_run'] = {'%s/%s' % k: [round(min(v), 3), round(sorted(v)[len(v) // 2], 3),
                                                      round(max(v), 3), round(sum(v), 1)] for k, v in secs.items()}
    # ---- run 1b
    idx1b = load_json('run1b_index.json.gz') or []
    if idx1b:
        pairs1b = jl('run1b_pairs.jsonl.gz')
        hand1b = jl('run1b_handed.jsonl.gz')
        S['run1b'] = {}
        for tr in ('CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            sub = [r for r in idx1b if r['key'][1] == tr]
            S['run1b'][tr] = analyse_class('1b', sub, [p for p in pairs1b if p['key'][1] == tr],
                                           [x for x in hand1b if x['key'][1] == tr], LAWS, (3,), treatment=tr)
            S['run1b'][tr]['checks'] = s_checks(sub, '1b')
        fp1 = {(r['key'][3], r['key'][4], r['h'], r['nu'], tuple(r['usable'])): r['fp'] for r in idx1}
        eq = Counter()
        for r in idx1b:
            k = (r['key'][3], r['key'][4], r['h'], r['nu'], tuple(r['usable']))
            v = fp1.get(k)
            eq[(r['key'][1], r['key'][3], r['key'][4],
                'no run-1 counterpart (not run)' if v is None else v == r['fp'])] += 1
        S['run1b']['equal_to_run1'] = {repr(k): v for k, v in eq.items()}
        S['run1b']['knot_test'] = {'verdicts': sum(r['kt']['verdicts'] for r in idx1b),
                                   'fails': sum(r['kt']['n_fail'] for r in idx1b)}
    # ---- run 2
    R2 = load_json('run2.json.gz')
    if R2:
        S['run2'] = {'comparisons': R2['comparisons'],
                     'runs': [{'h': r['h'], 'a': r['a'], 'law': r['law_name'], 'rounds_read': r['rounds_read'],
                               'stop': r['stop'], 'guard': r['guard'], 'knot_fail': r['knot_test']['n_fail'],
                               'meet': r['meet_round'], 's4': r['s4'], 'short': r['short_after1'],
                               'seconds': r['seconds']} for r in R2['runs']]}
    if idx1:
        S['registered'] = registered_checks()
        # per numbering: the (h - 1, h) clause of Q3 and the classes of P (RD 4.4, 4.7)
        per_nu = []
        rmin = {}
        for r in idx1:
            if r['a'] >= 1:
                k2 = (tuple(r['key']), r['h'])
                rmin[k2] = min(rmin.get(k2, 99), r['rounds_read'])
        for x in hand1:
            key = tuple(x['key'])
            h = x['h']
            Rh = min(rmin[(key, h)], 4)
            v = x['handed'].get(str(Rh))
            if v is None:
                per_nu.append({'key': key, 'h': h, 'nu': x['nu'], 'prefix': Rh, 'verdict': 'not read'})
                continue
            top_equal = None
            if v['verdict'] != 'no difference':
                cl = [c for c in v['P'] if (h in c) or (h - 1 in c)]
                top_equal = len(cl) == 1 and cl[0].count(h) == 1 and cl[0].count(h - 1) == h
            else:
                top_equal = True
            per_nu.append({'key': key, 'h': h, 'nu': x['nu'], 'prefix': Rh, 'verdict': v['verdict'],
                           'n_classes': v['n_classes'], 'P': v['P'], 'top_equal': top_equal,
                           'J_demand_r2_induces': v.get('J_demand_r2_induces'),
                           'first_inducing': v.get('first_inducing'),
                           'demand_alone_induces': v.get('demand_alone_induces')})
        S['run1']['per_nu'] = per_nu
    common.write_json('summary_raw.json', {'S': S, 'q0': q0, 'q5': q5, 'q6': q6})
    log('Q0', q0, 'Q5', q5, 'Q6', q6)


if __name__ == '__main__':
    main()
