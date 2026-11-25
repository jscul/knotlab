"""R0, the gate (PC, "Runs", order 1): the census list against starts_c.json; the order; the round-0 ties under
not-all-equal; the drafter's 96 cases of cases_c.json at the scratch's bounds (6 rounds, 300 knots) and pair rule, with
their counts of 20 continuations with Y and with X barred; its two values comparisons at sample indices 1,000 to 1,999
with their masked counts.  Writes gate_R0.json (and gate_R0_cases.jsonl, one row per regrown growth)."""
import argparse
import multiprocessing as mp
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from mcc import K, mc, pm  # noqa: E402
from study import log  # noqa: E402

SCRATCH_ROUNDS, SCRATCH_KNOTS = 6, 300


def spec_of_case(c):
    return mcc.Spec(c['ration'], c['treatment'], 'MET', c['knot_law'])


def census_checks():
    out = {}
    C = mcc.rebuild_census()
    F = mcc.STARTS_C['starts']
    out['n'] = len(C)
    out['ids_and_order_equal'] = [a['id'] for a in C] == [b['id'] for b in F]
    out['labelled_equal'] = all(a['labelled'] == b['labelled'] for a, b in zip(C, F))
    out['counts'] = dict(Counter(a['n'] for a in C))
    lab = Counter()
    for a in C:
        lab[a['n']] += a['labelled']
    out['labelled_totals'] = dict(lab)
    # set aside: a start knot fails the parity knot test at round 0; under not-all-equal every start knot passes
    flags = []
    nae_fail = []
    for a in C:
        S = pm.from_stars(a['stars'])
        pt = K.parity_test(S)
        flags.append(bool(pt['fail']))
        if pt['disagree']:
            out.setdefault('parity_method_disagree', []).append(a['id'])
        if pt['fail']:
            d = K.nae_direct(S, S.knots())
            if not all(d.values()):
                nae_fail.append(a['id'])
    out['set_aside_equal'] = flags == [b['set_aside_parity'] for b in F]
    out['set_aside'] = sum(flags)
    out['set_aside_by_size'] = dict(Counter(a['n'] for a, f in zip(C, flags) if f))
    out['set_aside_nae_failing'] = nae_fail
    lab2 = Counter()
    for a, f in zip(C, flags):
        if not f:
            lab2[a['n']] += a['labelled']
    out['labelled_totals_parity'] = dict(lab2)
    out['largest_labelled'] = max(a['labelled'] for a in C)
    # the order
    o = mcc.order()
    out['order_equal'] = [C[i]['id'] for i in o] == mcc.STARTS_C['registered_samples']['order']['ids']
    out['parity_list'] = len(mcc.run_order('parity'))
    five = [C[i]['id'] for i in o if C[i]['n'] == 5][:300]
    out['R5_five_equal'] = five == mcc.STARTS_C['registered_samples']['R5 five-knot starts']
    out['pass'] = bool(out['ids_and_order_equal'] and out['labelled_equal'] and out['set_aside_equal']
                       and out['order_equal'] and not nae_fail and out['parity_list'] == 3344
                       and out['R5_five_equal'])
    return out


def nae_ties_job(idx):
    C = mcc.census()
    S = pm.from_stars(C[idx]['stars'])
    T = mc.ties_nae(S, seed=idx)
    return idx, len(T.classes), len(T.frozen), T.unsat


# ------------------------------------------------------------------------------------------- the 96 cases replayed
def replay_growth(key):
    """Regrow one growth of the scratch at its bounds and pair rule; list its cases of form, from both, values both
    from X and ticket A's values reading (and of the form reading without "Y's form not X's form"); for each listed
    case, 20 continuations with Y and with X barred, the X-barred event read both as DC 4.2's Y's own and as two parts
    of Y's form of any descent (dev 35)."""
    gen, sid, ration, treatment, knot_law, i = key
    spec = mcc.Spec(ration, treatment, 'MET', knot_law)
    st = mcc.start_by_id(sid)
    assert mcc.base_seed(sid, spec, i) == gen
    row = study.analyse_growth(st['stars'], spec, sid, i, rounds=SCRATCH_ROUNDS, knot_bound=SCRATCH_KNOTS,
                               pair_rule='scratch', first=False, kt=False, by_form=False,
                               case_readings=('form', 'both', 'vX', 'vA', 'formany_X'))
    listed = [c for c in mcc.CASES_C['cases'] if c['generator'] == gen]
    g = mcc.Growth(st['stars'], spec, sid, i, SCRATCH_ROUNDS, SCRATCH_KNOTS, pair_rule='scratch')
    out = {'key': list(key), 'rounds': row['rounds'], 'stop': row['stop'], 'n_pairs': row['n_pairs'],
           'more_than_eight': row['more_than_eight'], 'cases_found': [], 'listed': []}
    for c in row['cases']:
        out['cases_found'].append({k: c[k] for k in ('s', 'X', 'Y', 'reading', 'meet', 'round_met',
                                                      'round_met_any')})
    for c in listed:
        X, Y, s = tuple(c['X']), tuple(c['Y']), c['s']
        ref = g.ref(s, X, Y)
        rd = {'form': 'form', 'values': 'vA'}[c['reading']]
        if rd == 'form' and ref.same_form:
            rd = 'formany_X'
        cnt = Counter()
        for k in ('BY', 'BX'):
            for j in range(20):
                Gc, _ = g.continuation(k, s, X, Y, j)
                r = mcc.read_pairs(Gc.snaps, Gc.records, Gc.R, [ref], need_form=(rd != 'vA') or k == 'BX',
                                   need_values=(rd == 'vA'))[0]
                if k == 'BY':
                    cnt['BY'] += int(rd in r.first)
                else:
                    cnt['BX'] += int(mcc.YOWN[rd] in r.first)
                    cnt['BX_any_descent'] += int('yform_any' in r.first)
        out['listed'].append({'s': s, 'X': list(X), 'Y': list(Y), 'reading': rd, 'same_form': ref.same_form,
                              'Y_barred_met_of_20': cnt['BY'], 'X_barred_Y_own_of_20': cnt['BX'],
                              'X_barred_two_of_Y_form_any_descent_of_20': cnt['BX_any_descent']})
    return out


def compare_cases(rows):
    """Every listed case against the regrown one; each difference with its class (dev 35, 36)."""
    listed = mcc.CASES_C['cases']
    found = {}
    counts = {}
    for r in rows:
        gen = r['key'][0]
        for c in r['cases_found']:
            found[(gen, c['s'], tuple(c['X']), tuple(c['Y']), c['reading'])] = c
        for c in r['listed']:
            counts[(gen, c['s'], tuple(c['X']), tuple(c['Y']))] = c
    want = {}
    listing = []
    for idx, c in enumerate(listed):
        k4 = (c['generator'], c['s'], tuple(c['X']), tuple(c['Y']))
        n = counts[k4]
        rd = n['reading']
        want[k4 + (rd,)] = idx
        f = found.get(k4 + (rd,))
        row = {'index': idx, 'start': c['start'], 'law': '%s/%s/%s' % (c['ration'], c['treatment'], c['knot_law']),
               'reading listed': c['reading'], 'reading here': rd, 'same_form': n['same_form'],
               'listed': {k: c[k] for k in ('s', 'meeting_round', 'round_met', 'Y_barred_met_of_20',
                                            'X_barred_Y_own_of_20')},
               'here': {'found': f is not None, 'meeting_round': f and f['meet'], 'round_met': f and f['round_met'],
                        'Y_barred_met_of_20': n['Y_barred_met_of_20'],
                        'X_barred_Y_own_of_20': n['X_barred_Y_own_of_20'],
                        'X_barred_two_of_Y_form_any_descent_of_20': n['X_barred_two_of_Y_form_any_descent_of_20']},
               'differences': []}
        if f is None:
            row['differences'].append('not found')
        else:
            if f['meet'] != c['meeting_round']:
                row['differences'].append('meeting round')
            if f['round_met'] != c['round_met']:
                row['differences'].append('round met')
        if n['Y_barred_met_of_20'] != c['Y_barred_met_of_20']:
            row['differences'].append('Y barred, of 20')
        if n['X_barred_Y_own_of_20'] != c['X_barred_Y_own_of_20']:
            if n['X_barred_two_of_Y_form_any_descent_of_20'] == c['X_barred_Y_own_of_20'] and rd != 'vA':
                row['differences'].append("X barred, of 20: equal to two parts of Y's form of any descent (dev 35)")
            else:
                row['differences'].append('X barred, of 20')
        if c['reading'] == 'form' and n['same_form']:
            row['differences'].append("listed as form, but Y's form is X's form: equal under the form reading "
                                      "without that condition (dev 36)")
        listing.append(row)
    extra = [dict(zip(('generator', 's', 'X', 'Y', 'reading'), k)) for k in found
             if k[:4] + (k[4],) not in want and k[4] != 'formany_X']
    unexplained = [r for r in listing if any(not (d.startswith("X barred, of 20: equal") or
                                                  d.startswith('listed as form')) for d in r['differences'])]
    return listing, extra, unexplained


# --------------------------------------------------------------------------------------- the values comparisons
def values_case(ordinal):
    """cases_c.json's values_case_index counts the values cases (0 to 3), not the cases list (dev 37)."""
    vals = [i for i, c in enumerate(mcc.CASES_C['cases']) if c['reading'] == 'values']
    return vals[ordinal]


def values_job(args):
    ci, kind, lo, hi = args
    c = mcc.CASES_C['cases'][values_case(ci)]
    spec = spec_of_case(c)
    st = mcc.start_by_id(c['start'])
    g = mcc.Growth(st['stars'], spec, c['start'], c['sample'], SCRATCH_ROUNDS, SCRATCH_KNOTS, pair_rule='scratch')
    X, Y, s = tuple(c['X']), tuple(c['Y']), c['s']
    ref = g.ref(s, X, Y)
    cnt = Counter()
    for i in range(lo, hi):
        Gc, seed = g.continuation(kind, s, X, Y, i)
        r = mcc.read_pairs(Gc.snaps, Gc.records, Gc.R, [ref], need_form=False, need_values=True)[0]
        cnt['n'] += 1
        cnt['meet'] += int(r.meet is not None)
        for rd in ('vA', 'vX', 'Yown_val'):
            if rd in r.first:
                cnt[rd + '_any'] += 1
            if rd in r.first_after:
                cnt[rd + '_after'] += 1
    return ci, kind, dict(cnt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    a = ap.parse_args()
    out = {'engine_hashes': mcc.engine_hashes(), 'engine_hashes_equal': mcc.engine_hashes() == mcc.ENGINE_SHA,
           'guard': dict(pm.GUARD)}
    log('census')
    out['census'] = census_checks()
    log('census', out['census']['pass'])
    ctx = mp.get_context('fork')
    with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
        log('round-0 ties under not-all-equal')
        res = list(pool.imap_unordered(nae_ties_job, range(3376), chunksize=20))
        bad = [r for r in res if r[1] or r[2] or r[3]]
        out['nae_round0_ties'] = {'starts': len(res), 'with_a_tie_or_frozen_or_unsat': len(bad), 'list': bad[:20],
                                  'pass': not bad}
        log('ties', out['nae_round0_ties'])
        keys = sorted({(c['generator'], c['start'], c['ration'], c['treatment'], c['knot_law'], c['sample'])
                       for c in mcc.CASES_C['cases']})
        log('replaying', len(keys), 'growths')
        rows = list(pool.imap_unordered(replay_growth, keys, chunksize=1))
        w = study.JsonLines('gate_R0_cases.jsonl')
        for r in sorted(rows, key=lambda r: r['key']):
            w.write(r)
        w.close()
        listing, extra, unexplained = compare_cases(rows)
        study.write_json('gate_R0_case_listing.json', listing)
        out['cases'] = {'growths': len(rows), 'listed': len(mcc.CASES_C['cases']),
                        'found': sum(len(r['cases_found']) for r in rows),
                        'with a difference': [r['index'] for r in listing if r['differences']],
                        'difference classes': dict(Counter(d for r in listing for d in r['differences'])),
                        'unexplained': unexplained, 'cases found and not listed': extra,
                        'growths with more than eight pairs a round': [r['key'] for r in rows if r['more_than_eight']],
                        'pass': not unexplained and not extra}
        log('cases', out['cases']['difference classes'], len(unexplained), 'unexplained', len(extra), 'extra')
        jobs = []
        for vc in mcc.CASES_C['values_confirmations']:
            for kind in ('BN', 'BY', 'BX', 'BM'):
                for lo in range(1000, 2000, 100):
                    jobs.append((vc['values_case_index'], kind, lo, lo + 100))
        log('values comparisons', len(jobs), 'jobs')
        tot = defaultdict(Counter)
        for ci, kind, cnt in pool.imap_unordered(values_job, jobs, chunksize=1):
            tot[(ci, kind)].update(cnt)
    vrows = []
    for vc in mcc.CASES_C['values_confirmations']:
        ci = vc['values_case_index']
        assert mcc.CASES_C['cases'][values_case(ci)]['start'] == vc['start']
        here = {'nothing_barred_met_after_meeting': tot[(ci, 'BN')]['vA_after'],
                'Y_barred_met': tot[(ci, 'BY')]['vA_any'],
                'X_barred_Y_own': tot[(ci, 'BX')]['Yown_val_any'],
                'masked_met': tot[(ci, 'BM')]['vA_any'],
                'values_both_from_X_only': {'nothing barred after the meeting': tot[(ci, 'BN')]['vX_after'],
                                            'masked': tot[(ci, 'BM')]['vX_any']},
                'nothing_barred_met_at_any_round': tot[(ci, 'BN')]['vA_any'],
                'continuations': {k: tot[(ci, k)]['n'] for k in ('BN', 'BY', 'BX', 'BM')},
                'meetings': {k: tot[(ci, k)]['meet'] for k in ('BN', 'BY', 'BX', 'BM')}}
        listed = {k: vc[k] for k in ('nothing_barred_met_after_meeting', 'Y_barred_met', 'X_barred_Y_own',
                                     'masked_met', 'values_both_from_X_only', 'nothing_barred_met_at_any_round')}
        same = all(here[k] == listed[k] for k in listed)
        vrows.append({'case': ci, 'cases index': values_case(ci), 'start': vc['start'], 'listed': listed, 'here': here, 'equal': same})
    out['values_comparisons'] = {'rows': vrows, 'pass': all(r['equal'] for r in vrows)}
    out['pass'] = bool(out['engine_hashes_equal'] and out['census']['pass'] and out['nae_round0_ties']['pass']
                       and out['cases']['pass'] and out['values_comparisons']['pass'])
    study.write_json('gate_R0.json', out)
    log('GATE', 'PASS' if out['pass'] else 'DIFFERENCES', {k: out[k]['pass'] for k in ('census', 'nae_round0_ties',
                                                                                    'cases', 'values_comparisons')})


if __name__ == '__main__':
    main()
