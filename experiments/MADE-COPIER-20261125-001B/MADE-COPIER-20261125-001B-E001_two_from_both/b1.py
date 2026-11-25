"""Runs B1 and B2 (arm 1, no taking rule): one job per base law, knot law and release, on the 256 starts (B1), the 87
starts of the other-member swap (B2) or the 256 under HOLD (B2).  For every start: run A, B_X, B(i); for every kind: X
alone and Y alone; the per-law class (its forms as Y with every X and start's meeting).  Per round: the parts by form
and descent, the roster (for PB13's R3), whether the knots descended from Y only (X only) have ended; at the round of a
case and the first round with two, DB 3.5's reports; the knot tests.

usage: python -B b1.py [--procs 4] [--set main|other|hold] [--only substring]
"""
import argparse
import json
import os
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P


def read_run(run, X, Y, s, law, forms, keep_parts=False):
    """Per round t = s+1..: counts of parts by form (any descent) and by (form, descent); the roster as a multiset of
    forms; whether X-only and Y-only knots have ended; rounds whose roster met the guard."""
    rows = []
    for t in range(s + 1, run.rounds_done + 1):
        S = run.snap[t]
        R = mcb.roster_or_none(S, law)
        row = {'t': t, 'knots': S.n_knots - len(S.removed)}
        if R is None:
            row['not read'] = True
            rows.append(row)
            continue
        if X is not None or Y is not None:
            desc, xo, yo = mcb.side_sets(S, X or [], Y or [], s)
        else:
            desc, xo, yo = {}, set(), set()
        parts = mcb.read_parts(S, R, desc, forms)
        row['counts'] = dict(Counter(c for c, _, _, _ in parts))
        row['by_descent'] = [[c, k, n] for (c, k), n in sorted(Counter((c, k) for c, k, _, _ in parts).items())]
        row['roster'] = sorted(Counter(c for c, _, _, _ in parts).items())
        mem = mcb.members_now(S)
        row['Y only ended'] = not (yo & mem) if Y else None
        row['X only ended'] = not (xo & mem) if X else None
        row['members'] = len(mem)
        if keep_parts:
            row['_parts'] = parts
        rows.append(row)
    return rows


def count_of(rows, cid, t):
    for r in rows:
        if r['t'] == t:
            if r.get('not read'):
                return None
            return r['counts'].get(cid, 0)
    return 'not reached'


def case_details(A, X, Y, law, forms, rows, t, yform, xform, kind_forms):
    row = next(r for r in rows if r['t'] == t)
    parts = row['_parts']
    both_y = [p for p in parts if p[0] == yform and p[1] == 'both']
    others = [p for p in parts if not (p[0] == yform and p[1] == 'both')]
    S = A.snap[t]
    desc, xo, yo = mcb.side_sets(S, X, Y, 0)
    cls = Counter()
    for c, k, _, _ in others:
        for kn, f in kind_forms.items():
            if c == f:
                cls['%s|%s' % (kn, k)] += 1
    return {'t': t, 'parts the same as Y, from both': len(both_y), 'exactly two': len(both_y) == 2,
            'other parts': len(others), 'class forms among the other parts (kind|descent)': dict(cls),
            'how the knots descended from Y only ended': mcb.how_ended(A, yo, t),
            'knots descended from X only ended': row['X only ended'],
            'X returns (a part of X\'s form, every member from X only)': any(c == xform and k == 'X only'
                                                                          for c, k, _, _ in parts),
            'a part of X\'s form descended from both': any(c == xform and k == 'both' for c, k, _, _ in parts),
            'parts of Y\'s form, mixed': sum(1 for c, k, _, _ in parts if c == yform and k == 'mixed'),
            'first joint births': mcb.first_joint_births(A, X, Y, 0, t)}


def strip(rows):
    return [{k: v for k, v in r.items() if not k.startswith('_')} for r in rows]


def knot_brief(run, full=True):
    return mc.knot_tests_A(run) if full else None


def do_start(key, S0, X, Y, law, base, forms, alone, kind_forms, info):
    A = mcb.grow(S0, law, base)
    rows = read_run(A, X, Y, 0, law, forms, keep_parts=True)
    BX = mc.run_from_state(A, 0, P.bar_part(A.snap[0], X))
    BI = mc.run_from_state(A, 0, P.bar_part(A.snap[0], Y))
    rbx = read_run(BX, X, Y, 0, law, forms)
    rbi = read_run(BI, X, Y, 0, law, forms)
    ky, kx = info['Y kind'], info['X kind']
    yform = alone[('Y', ky)]['form']
    xform = alone[('X', kx)]['form']
    T = min(A.rounds_done, BX.rounds_done, alone[('Y', ky)]['rounds'], alone[('X', kx)]['rounds'])
    per = []
    first_two, case_t = None, None
    for r in rows:
        if r.get('not read'):
            per.append({'t': r['t'], 'not read': True})
            continue
        nb = sum(n for c, k, n in r['by_descent'] if c == yform and k == 'both')
        nm = sum(n for c, k, n in r['by_descent'] if c == yform and k == 'mixed')
        nall = r['counts'].get(yform, 0)
        per.append({'t': r['t'], 'Y form from both': nb, 'Y form mixed': nm, 'Y form any': nall,
                    'Y only ended': r['Y only ended'], 'X only ended': r['X only ended']})
        if nb >= 2 and first_two is None:
            first_two = r['t']
        if nb >= 2 and r['Y only ended'] and case_t is None:
            case_t = r['t']
    out = dict(info, key=key, rounds=A.rounds_done, stop=A.stop, guard=A.guard, T=T, per_round=per,
               first_two=first_two, case_round=case_t,
               B_X={'rounds': BX.rounds_done, 'Y form': [count_of(rbx, yform, t) for t in range(1, T + 1)]},
               B_i={'rounds': BI.rounds_done, 'Y form': [count_of(rbi, yform, t) for t in range(1, BI.rounds_done + 1)]},
               closing_round=next((rec['round'] for rec in A.records if rec['closing']), None))
    out['counts'] = [r.get('counts') for r in rows]
    out['roster'] = [r.get('roster') for r in rows]
    out['both forms'] = [sorted([c, n] for c, k, n in r['by_descent'] if k == 'both') if not r.get('not read') else None
                         for r in rows]
    for t in sorted({x for x in (first_two, case_t) if x is not None}):
        out.setdefault('details', {})[str(t)] = case_details(A, X, Y, law, forms, rows, t, yform, xform, kind_forms)
    # the knot tests: run A at every round; the comparison runs at their last round
    kt = mc.knot_tests_A(A)
    fails0 = [f['knot'] for f in kt['fails'] if f['round'] == 0]
    out['knot_tests'] = {'A': kt, 'B_X': mc.knot_tests_cmp(BX, 0, fails0), 'B(i)': mc.knot_tests_cmp(BI, 0, fails0)}
    return out


def do_job(job):
    cb.cap_memory(job.get('mem', 7))
    t0 = time.time()
    base, kl, release, which = job['base'], job['knot_law'], job['release'], job['set']
    law = mcb.law1(base, kl, release)
    forms = mcb.Forms()
    out = {'job': job, 'law': law.name(), 'alone': {}, 'starts': {}, 'perlaw': []}
    try:
        alone = {}
        for kind in mcb.KINDS8:
            for which_ in ('X', 'Y'):
                S0, mem = mcb.alone_b(kind, which_ + ' alone')
                R0 = pm.roster_of(S0.copy(), law)
                part = next(p for p in R0.parts if set(mem) <= set(p))
                assert set(part) == set(mem), (kind, which_, part, mem)
                form = forms.classify(R0, part)
                run = mcb.grow(S0, law, base)
                rows = read_run(run, mem if which_ == 'X' else None, mem if which_ == 'Y' else None, 0, law, forms)
                alone[(which_, kind)] = {'form': form, 'rounds': run.rounds_done, 'rows': rows}
                out['alone']['%s alone|%s' % (which_, kind)] = {
                    'form': form, 'rounds': run.rounds_done, 'stop': run.stop, 'guard': run.guard,
                    'per_round_own_form': [r.get('counts', {}).get(form, 0) if not r.get('not read') else None
                                           for r in rows],
                    'counts': [r.get('counts') for r in rows], 'roster': [r.get('roster') for r in rows],
                    'knot_tests': mc.knot_tests_A(run)}
        kind_forms = {k: alone[('Y', k)]['form'] for k in mcb.KINDS8}
        # the starts
        keys = starts_of(which)
        for key in keys:
            S0, X, Y = mcb.start_b(key)
            kx, rest = key.split(' + ')
            ky, way = rest.split(' / ')
            info = {'X kind': kx, 'Y kind': ky, 'way': way}
            out['starts'][key] = do_start(key, S0, X, Y, law, base, forms, alone, kind_forms, info)
        # the per-law class (B1 only)
        if which == 'main':
            out['perlaw'] = perlaw(base, law, forms, alone, kind_forms)
        out['forms'] = forms.desc
        out['kind_forms'] = kind_forms
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    out['peak_mb'] = cb.peak_mb()
    return out


def perlaw(base, law, forms, alone, kind_forms):
    rows_out = []
    fl = mcb.STB['per-law class'][mcb.LAW_KEY[base]]
    for i, f in enumerate(fl):
        ystars = f['part (labels from 100)']
        nmem = len(f['members h'])
        yinfo = {'members': nmem, 'first member': f['first member'], 'first dead knot': f['first dead knot'],
                 'other member': f['first member']}
        # Y alone: the part with e barred
        SA = mcb.build(ystars, [1000])
        ymem = list(range(1, 1 + nmem))
        R0 = pm.roster_of(SA.copy(), law)
        part = next(p for p in R0.parts if set(ymem) <= set(p))
        yform = forms.classify(R0, part)
        ra = mcb.grow(SA, law, base)
        rya = read_run(ra, None, ymem, 0, law, forms)
        key_y = 'per-law %d' % i
        alone[('Y', key_y)] = {'form': yform, 'rounds': ra.rounds_done, 'rows': rya}
        rec = {'index': i, 'members h': f['members h'], 'maximal met sets': f['maximal met sets'], 'form': yform,
               'Y alone': {'rounds': ra.rounds_done, 'own form': [r.get('counts', {}).get(yform, 0)
                                                                  if not r.get('not read') else None for r in rya],
                           'roster': [r.get('roster') for r in rya], 'knot_tests': mc.knot_tests_A(ra)},
               'starts': {}}
        for kx in mcb.KINDS8:
            xp = mcb.STB['parts'][kx]
            xinfo = {'members': xp['members'], 'first member': xp['first member'], 'first dead knot':
                     xp['first dead knot'], 'other member': xp['other member']}
            for way in mcb.WAYS:
                stars, X, Y = mcb.way_start(xp['X (labels from 0)'], xinfo, ystars, yinfo, way)
                S0 = mcb.build(stars)
                info = {'X kind': kx, 'Y kind': key_y, 'way': way}
                r = do_start('%s + %s / %s' % (kx, key_y, way), S0, X, Y, law, base, forms, alone, kind_forms, info)
                rec['starts']['%s / %s' % (kx, way)] = r
        rows_out.append(rec)
    return rows_out


def starts_of(which):
    ks = list(mcb.STB['starts'].keys())
    if which in ('main', 'hold'):
        return [k for k in ks if 'other' not in k.split(' / ')[1]]
    return [k for k in ks if 'other' in k.split(' / ')[1]]


def jobs(which):
    js = []
    for base in mcb.BASES6:
        for kl in ('nae', 'parity'):
            js.append({'base': base, 'knot_law': kl, 'release': 'HOLD' if which == 'hold' else 'RELEASE',
                       'set': which})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--set', default='main', choices=('main', 'other', 'hold'))
    ap.add_argument('--only', default=None)
    ap.add_argument('--mem', type=float, default=7)
    args = ap.parse_args()
    js = jobs(args.set)
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    for j in js:
        j['mem'] = args.mem
    name = {'main': 'b1.jsonl.gz', 'other': 'b2_other.jsonl.gz', 'hold': 'b2_hold.jsonl.gz'}[args.set]
    cb.log('run %s:' % name, len(js), 'jobs')
    out = cb.JsonLines(name)
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = {ex.submit(do_job, j): j for j in js}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:
                r = {'job': futs[f], 'error': repr(e)}
            out.write(r)
            cb.log(r.get('law'), r.get('seconds'), r.get('peak_mb'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
