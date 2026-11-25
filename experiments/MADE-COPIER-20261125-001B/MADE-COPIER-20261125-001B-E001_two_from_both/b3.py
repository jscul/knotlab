"""Run B3 (arm 2, MET): ticket A's designs (their own s) and the 256 starts, under MET with CAP-3(t) and FBP(t) and the
four stated rules, and MET under COPY-LAW(t) as the check row (PB6); both knot laws.  Readings as B1 (DB 3, with DB 3.0
on ticket A's designs); every case under every renaming registered for its design.

usage: python -B b3.py [--procs 4] [--only substring]
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
import b1  # noqa: E402
import cb  # noqa: E402
import mcb  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P
A_DESIGNS = mc.RUN2_DESIGNS
EXCHANGED_ALONE = {'X alone': {'stars': [[0, 3, 4]], 'barred': [0], 'X': [1, 2], 's': 1},
                   'Y alone': {'stars': [[0, 1, 2]], 'barred': [0], 'Y': [1, 2], 's': 1}}


def a_alone(name, which):
    a = mc.STARTS['alone'].get(name) or EXCHANGED_ALONE
    a = a[which] if name in mc.STARTS['alone'] else EXCHANGED_ALONE[which]
    S = mc.build_start(a['stars'], None, a['barred'])
    return S, list(a['X'] if which == 'X alone' else a['Y']), a['s']


def a_class(name):
    return mc.CLASS_MADE if name.startswith('made') else mc.CLASS_START


def a_control(name):
    return 'made-2' if name.startswith('made') else 'ystart-two-22'


def form_after(S0, mem, s, law, base, forms):
    """The form of the part a pattern's members form after round s of its alone run (DB 3.0, 3.3)."""
    run = mcb.grow(S0, law, base)
    if run.rounds_done < s:
        return None, run
    R = pm.roster_of(run.snap[s].copy(), law)
    part = next((p for p in R.parts if set(mem) <= set(p)), None)
    if part is None or set(part) != set(mem):
        return None, run
    return forms.classify(R, part), run


def read_case(A, X, Y, s, law, forms, yform, upto):
    first_two, case_t, per = None, None, []
    rows = b1.read_run(A, X, Y, s, law, forms, keep_parts=True)
    for r in rows:
        if r['t'] > upto:
            break
        if r.get('not read'):
            per.append({'t': r['t'], 'not read': True})
            continue
        nb = sum(n for c, k, n in r['by_descent'] if c == yform and k == 'both')
        per.append({'t': r['t'], 'Y form from both': nb, 'Y form any': r['counts'].get(yform, 0),
                    'Y form mixed': sum(n for c, k, n in r['by_descent'] if c == yform and k == 'mixed'),
                    'Y only ended': r['Y only ended']})
        if nb >= 2 and first_two is None:
            first_two = r['t']
        if nb >= 2 and r['Y only ended'] and case_t is None:
            case_t = r['t']
    return rows, per, first_two, case_t


def counts_series(run, s, law, forms, cid):
    out = []
    for t in range(s + 1, run.rounds_done + 1):
        R = mcb.roster_or_none(run.snap[t], law)
        out.append(None if R is None else sum(1 for p in R.parts if forms.classify(R, p) == cid))
    return out


def both_class_forms(rows, class_forms):
    """PB6: parts of a class form descended from both, at any round."""
    n = 0
    for r in rows:
        if r.get('not read'):
            continue
        n += sum(k_n for c, k, k_n in r['by_descent'] if c in class_forms and k == 'both')
    return n


def do_design(name, law, base, forms, cache, renaming=None):
    d = mc.design(name, renaming=renaming)
    s = d.s
    A = mcb.grow(d.start(), law, base)
    if ('Y', name) not in cache:
        SY, my, sy = a_alone(name, 'Y alone')
        yf, ry = form_after(SY, my, sy, law, base, forms)
        SX, mx, sx = a_alone(name, 'X alone')
        xf, rx = form_after(SX, mx, sx, law, base, forms)
        cache[('Y', name)] = (yf, ry, sy)
        cache[('X', name)] = (xf, rx, sx)
    yf, ry, sy = cache[('Y', name)]
    xf, rx, sx = cache[('X', name)]
    out = {'design': name, 'renaming': renaming, 's': s, 'rounds': A.rounds_done, 'stop': A.stop, 'guard': A.guard,
           'Y form': yf}
    if yf is None or A.rounds_done < s:
        out['note'] = 'Y\'s form not read'
        return out, A
    BX = mc.run_from_state(A, s, P.bar_part(A.snap[s], d.X))
    T = min(A.rounds_done, BX.rounds_done, ry.rounds_done, rx.rounds_done)
    rows, per, ft, ct = read_case(A, d.X, d.Y, s, law, forms, yf, T)
    out.update({'T': T, 'per_round': per, 'first_two': ft, 'case_round': ct,
                '(a) B_X': counts_series(BX, s, law, forms, yf)[:T - s],
                '(b) Y alone': counts_series(ry, sy, law, forms, yf)[:T - s],
                '(d) X alone': counts_series(rx, sx, law, forms, yf)[:T - s],
                'counts': [r.get('counts') for r in rows],
                'both forms': [sorted([c, n] for c, k, n in r['by_descent'] if k == 'both') if not r.get('not read')
                               else None for r in rows]})
    out['knot_tests'] = mc.knot_tests_A(A)
    return out, A


def do_job(job):
    cb.cap_memory(job.get('mem', 7))
    t0 = time.time()
    base, ch, kl = job['base'], job['choice'], job['knot_law']
    law = mc.make_law(base, 'MET', ch, kl)
    forms = mcb.Forms(seconds=job.get('iso_seconds'), hash_above=job.get('hash_above'))
    out = {'job': job, 'law': law.name(), 'designs': {}, 'starts': {}}
    try:
        cache = {}
        for name in A_DESIGNS:
            row, A = do_design(name, law, base, forms, cache)
            out['designs'][name] = row
        # class forms for PB6 and (c) on ticket A's designs
        out['class forms'] = {n: cache[('Y', n)][0] for n in A_DESIGNS if ('Y', n) in cache}
        # the 256 starts: as arm 1 (alone runs under this law)
        alone = {}
        for kind in mcb.KINDS8:
            for w in ('X', 'Y'):
                S0, mem = mcb.alone_b(kind, w + ' alone')
                R0 = pm.roster_of(S0.copy(), law)
                part = next(p for p in R0.parts if set(mem) <= set(p))
                f = forms.classify(R0, part)
                run = mcb.grow(S0, law, base)
                rows = b1.read_run(run, mem if w == 'X' else None, mem if w == 'Y' else None, 0, law, forms)
                alone[(w, kind)] = {'form': f, 'rounds': run.rounds_done, 'rows': rows}
        kind_forms = {k: alone[('Y', k)]['form'] for k in mcb.KINDS8}
        out['kind_forms'] = kind_forms
        out['alone'] = {'%s alone|%s' % k: {'form': v['form'], 'rounds': v['rounds'],
                                            'counts': [r.get('counts') for r in v['rows']]} for k, v in alone.items()}
        keys = b1.starts_of('main')
        budget = job.get('budget')
        t_start = time.time()
        import signal

        class _Budget(Exception):
            pass

        def _h(*a):
            raise _Budget()
        if budget:
            signal.signal(signal.SIGALRM, _h)
        not_run = []
        for i, key in enumerate(keys):
            if budget:
                left = budget - (time.time() - t_start)
                if left <= 0:
                    not_run = keys[i:]
                    break
                signal.alarm(max(1, int(left)))
            S0, X, Y = mcb.start_b(key)
            kx, rest = key.split(' + ')
            ky, way = rest.split(' / ')
            info = {'X kind': kx, 'Y kind': ky, 'way': way}
            try:
                r = b1.do_start(key, S0, X, Y, law, base, forms, alone, kind_forms, info)
            except _Budget:
                not_run = keys[i:]
                break
            finally:
                if budget:
                    signal.alarm(0)
            r['class forms from both'] = sum(n for row in r['both forms'] if row for c, n in row
                                             if c in set(kind_forms.values()))
            out['starts'][key] = r
        out['starts read'] = len(out['starts'])
        out['starts not run'] = len(not_run)
        out['first start not run'] = not_run[0] if not_run else None
        out['forms'] = forms.desc
        out['form tests undecided (deviations 33)'] = forms.undecided
        out['undecided tests by members of the part'] = {str(k): v for k, v in sorted(forms.undecided_sizes.items())}
        out['parts classed by invariants and hash alone (deviations 33)'] = forms.by_hash
        out['classes made so (deviations 33)'] = sorted(forms.by_hash_classes)
        out['largest form read (members)'] = max(
            [len(forms.desc[c]['hk']) for c in list(out.get('kind_forms', {}).values()) +
             list(out.get('class forms', {}).values()) if c is not None] or [0])
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    out['peak_mb'] = cb.peak_mb()
    return out


def jobs():
    js = []
    for base in mc.BASES_CAP3 + mc.BASES_FBP + mc.BASES_COPY:
        for ch in mc.RULES:
            for kl in ('nae', 'parity'):
                js.append({'base': base, 'choice': ch, 'knot_law': kl})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--only', default=None)
    ap.add_argument('--mem', type=float, default=7)
    ap.add_argument('--out', default='b3.jsonl.gz')
    ap.add_argument('--small', action='store_true', help='only the laws with retiring or waiting, and MET under COPY-LAW')
    ap.add_argument('--skip-done', default=None, help='comma-separated result files whose jobs are not run again')
    ap.add_argument('--budget', type=float, default=None, help='seconds for the starts of DB 2 in each job (a prefix)')
    ap.add_argument('--iso-seconds', type=float, default=None, help='limit on one exact form test (deviations 33)')
    ap.add_argument('--hash-above', type=int, default=None,
                    help='parts of more members are classed by invariants and hash alone (deviations 33)')
    args = ap.parse_args()
    js = jobs()
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    if args.small:
        js = [j for j in js if not j['base'] in ('FBP(OFFSHOOT)', 'CAP-3(OFFSHOOT)')]
    if args.skip_done:
        done = set()
        for nm in args.skip_done.split(','):
            for r in cb.read_jsonl(nm):
                if 'error' not in r:
                    done.add((r['job']['base'], r['job']['choice'], r['job']['knot_law']))
        js = [j for j in js if (j['base'], j['choice'], j['knot_law']) not in done]
    for j in js:
        j['budget'] = args.budget
        j['iso_seconds'] = args.iso_seconds
        j['hash_above'] = args.hash_above
    for j in js:
        j['mem'] = args.mem
    # the long laws first (deviations 30): FBP and CAP-3 with offshoots
    js.sort(key=lambda j: (not j['base'].startswith('FBP(OFF'), not j['base'].startswith('CAP-3(OFF')))
    cb.log('run B3:', len(js), 'jobs')
    out = cb.JsonLines(args.out)
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
