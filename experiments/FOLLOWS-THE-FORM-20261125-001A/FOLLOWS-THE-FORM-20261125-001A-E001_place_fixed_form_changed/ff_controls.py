"""Run R5, the controls, of FOLLOWS-THE-FORM-20261125-001A-E001: renumbering (FF 10) and the knot test.

  python -B ff_controls.py time                         # times a few jobs of each kind
  python -B ff_controls.py run --chunk i/8 [--kt-half]  # a chunk of the 1,200 jobs; writes controls_<i>of8.jsonl.gz
  python -B ff_controls.py summary                      # controls.json

Samples and renumberings as deviations 3 and 4.  The knot test is ticket B's routine as its read.py calls it for a
full test: knots.test_run(run.snaps, run.law) (deviations 23).
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import random
import time

import ff_core as C
import ff_read as FR

if C.FOLD_DIR not in sys.path:
    sys.path.append(C.FOLD_DIR)
import knots  # noqa: E402  (ticket B's knot-test routine, from the fold folder, unchanged, read-only)
import eng  # noqa: E402


def samples():
    R2 = C.runset_runs('R2')
    R4 = C.runset_runs('R4')
    rng2 = random.Random(2)
    s_none = rng2.sample([r for r in R2 if r['take'] is None], 100)
    s_take = rng2.sample([r for r in R2 if r['take'] is not None], 100)
    rng7 = random.Random(7)
    s_r4 = rng7.sample(R4, 100)
    rng6 = random.Random(6)
    k_r2 = rng6.sample(R2, 200)
    k_r4 = rng6.sample(R4, 100)
    return s_none + s_take + s_r4, k_r2 + k_r4


def renumberings(ren_sample):
    """[(j, run, stars, first_knots, second_knots)] for j = 1, 2, 3 (seeds 3, 4, 5), deviations 4."""
    jobs = []
    for j, seed in ((1, 3), (2, 4), (3, 5)):
        rng = random.Random(seed)
        for r in ren_sample:
            stars, n_first, n_second = C.start_of(r)
            names = sorted({d for k in stars for d in k})
            perm = list(names)
            rng.shuffle(perm)
            to = dict(zip(names, perm))
            st = [[to[d] for d in k] for k in stars]
            for k in st:
                rng.shuffle(k)
            order = list(range(len(st)))
            rng.shuffle(order)
            st = [st[o] for o in order]
            fk = [pos for pos, o in enumerate(order) if o < n_first]
            sk = [pos for pos, o in enumerate(order) if n_first <= o < n_first + n_second]
            jobs.append({'kind': 'renumber', 'j': j, 'seed': seed, 'run': r, 'stars': st, 'first_knots': fk,
                         'second_knots': sk, 'n_first': n_first, 'n_second': n_second})
    return jobs


def all_jobs(kt_half=False):
    ren, kt = samples()
    jobs = renumberings(ren)
    kts = [{'kind': 'knot test', 'run': r} for r in kt]
    if kt_half:      # the registered cut: R5's knot test to half (a prefix of each sample)
        kts = kts[:100] + kts[200:250]
    return jobs + kts


def do_job(job):
    r = job['run']
    t0 = time.time()
    law = eng.Law(ration=r['ration'], treatment=r['treatment'], take=r['take'], knot_law=r['knot_law'])
    if job['kind'] == 'renumber':
        run = eng.Run(law, stars=job['stars'], rounds=C.rounds_for(r['family']), knot_bound=3000)
        rec = C.read_run(run, job['n_first'], job['n_second'], job['first_knots'], job['second_knots'])
        out = {'kind': 'renumber', 'j': job['j'], 'seed': job['seed'], 'key': C.run_key(r),
               'rounds_read': rec['rounds_read'], 'stop': rec['stop'], 'make': rec['make'], 'wider': rec['wider'],
               'sec_only': rec['sec_only'], 'knots': rec['knots']}
    else:
        run, _, _ = C.grow(r)
        kt = knots.test_run(run.snaps, run.law)
        out = {'kind': 'knot test', 'key': C.run_key(r), 'knot_law': r['knot_law'], 'rounds_read': run.rounds_read,
               'knots': run.S.n_knots, 'verdicts': kt['verdicts'], 'n_fail': len(kt['fails']),
               'fails': kt['fails'][:10], 'n_disagree': len(kt['disagree']), 'disagree': kt['disagree'][:5],
               'n_untested': len(kt['untested']), 'birth_vs_direct': kt['birth_vs_direct']}
    out['sec'] = round(time.time() - t0, 3)
    return out


def assignment(jobs, n):
    """Which process does which job (scheduling only, no effect on any result): renumbering jobs by index modulo n;
    knot-test jobs longest first to the least loaded process, the size predicted by the original run's final knot
    count times its rounds read (from the R2/R4 records)."""
    size = {}
    for rs in ('R2', 'R4'):
        for r in FR.load_runs(rs):
            size[C.run_key(dict(r, take=None if r['take'] == 'none' else 'MET-SOLE'))] = r['knots'] * r['rounds_read']
    who = {}
    load = [0] * n
    kts = []
    for k, job in enumerate(jobs):
        if job['kind'] == 'renumber':
            who[k] = k % n
        else:
            kts.append((size[C.run_key(job['run'])], k))
    for s, k in sorted(kts, key=lambda x: (-x[0], x[1])):
        p = min(range(n), key=lambda q: (load[q], q))
        who[k] = p
        load[p] += s
    return who


def run_chunk(chunk, kt_half):
    i, n = (int(x) for x in chunk.split('/'))
    C.cap_memory(6)
    jobs = all_jobs(kt_half)
    who = assignment(jobs, n)
    out = C.JsonLines(C.out_path('controls_%dof%d.jsonl.gz' % (i, n)))
    t0 = time.time()
    for k, job in enumerate(jobs):
        if who[k] != i:
            continue
        row = do_job(job)
        row['job'] = k
        out.write(row)
    out.close()
    C.log('controls chunk', chunk, 'done', '%.1fs' % (time.time() - t0))


HALF = set(range(900, 1000)) | set(range(1100, 1150))     # the registered cut (deviations 35)


def read_partial(path):
    """The finished lines of a gzip file that may have been cut off (a stopped process)."""
    import gzip
    import os
    out = []
    if not os.path.exists(path):
        return out
    try:
        with gzip.open(path, 'rt') as f:
            for line in f:
                if line.endswith('\n') and line.strip():
                    out.append(json.loads(line))
    except (EOFError, OSError):
        pass
    return out


def all_rows():
    import glob
    rows = []
    for p in sorted(glob.glob(C.out_path('controls_*of*.jsonl.gz'))):
        rows += read_partial(p)
    by = {}
    for x in rows:
        by.setdefault(x['job'], x)          # a job finished twice is counted once
    return [by[k] for k in sorted(by)]


def run_rest(part, exclude, deadline):
    """The jobs of the half not yet finished (deviations 35), other than `exclude`, longest first to the least loaded
    of n processes; no job is started after the deadline (epoch seconds)."""
    i, n = (int(x) for x in part.split('/'))
    C.cap_memory(6)
    jobs = all_jobs()
    done = {x['job'] for x in all_rows()}
    left = [k for k in sorted(HALF) if k not in done and k not in exclude]
    size = {}
    for rs in ('R2', 'R4'):
        for r in FR.load_runs(rs):
            size[C.run_key(dict(r, take=None if r['take'] == 'none' else 'MET-SOLE'))] = r['knots'] * r['rounds_read']
    load = [0] * n
    mine = []
    for k in sorted(left, key=lambda k: (-size[C.run_key(jobs[k]['run'])], k)):
        p = min(range(n), key=lambda q: (load[q], q))
        load[p] += size[C.run_key(jobs[k]['run'])]
        if p == i:
            mine.append(k)
    out = C.JsonLines(C.out_path('controls_rest_%dof%d.jsonl.gz' % (i, n)))
    t0 = time.time()
    for k in mine:
        if time.time() > deadline:
            C.log('deadline: job', k, 'not started')
            continue
        row = do_job(jobs[k])
        row['job'] = k
        out.write(row)
    out.close()
    C.log('rest part', part, 'jobs', mine, 'done', '%.1fs' % (time.time() - t0))


def summary(n=8):
    rows = all_rows()
    orig = {}
    for rs in ('R2', 'R4'):
        for r in FR.load_runs(rs):
            orig[C.run_key(dict(r, take=None if r['take'] == 'none' else 'MET-SOLE'))] = r
    ren = [x for x in rows if x['kind'] == 'renumber']
    kt_all = [x for x in rows if x['kind'] == 'knot test']
    kt = [x for x in kt_all if x['job'] in HALF]            # the registered row after the cut (deviations 35)
    kt_out = [x for x in kt_all if x['job'] not in HALF]
    jobs = all_jobs()
    done = {x['job'] for x in rows}
    not_run_half = [k for k in sorted(HALF) if k not in done]
    not_run_out = [k for k in range(900, 1200) if k not in HALF and k not in done]
    not_run_ren = [k for k in range(900) if k not in done]
    bad = []
    n_make = n_all = 0
    for x in ren:
        o = orig[x['key']]
        same_make = x['make'] == o['make'] and x['rounds_read'] == o['rounds_read'] and x['stop'] == o['stop']
        same_all = same_make and x['wider'] == o['wider'] and x['sec_only'] == o['sec_only']
        n_make += same_make
        n_all += same_all
        if not same_make:
            bad.append({'key': x['key'], 'j': x['j'], 'rounds_read': [o['rounds_read'], x['rounds_read']],
                        'stop': [o['stop'], x['stop']]})
    by_group = {}
    for x in ren:
        g = 'R4' if x['key'].startswith('R4|') else ('R2, the take' if '|MET-SOLE|' in x['key'] else
                                                       'R2, no taking rule')
        by_group.setdefault(g, [0, 0])
        o = orig[x['key']]
        by_group[g][0] += x['make'] == o['make'] and x['rounds_read'] == o['rounds_read'] and x['stop'] == o['stop']
        by_group[g][1] += 1
    kt_nae = [x for x in kt if x['knot_law'] == 'nae']
    kt_par = [x for x in kt if x['knot_law'] == 'parity']
    res = {
        'renumbering': {'renumbered runs': len(ren), 'make the same (and rounds read, stop)': n_make,
                        'wider record and second-only births the same too': n_all, 'by group': by_group,
                        'first differing': bad[:1], 'differing': len(bad)},
        'knot test': {
            'nae': {'runs': len(kt_nae), 'verdicts': sum(x['verdicts'] for x in kt_nae),
                    'failing knots': sum(x['n_fail'] for x in kt_nae),
                    'disagreements': sum(x['n_disagree'] for x in kt_nae),
                    'untested': sum(x['n_untested'] for x in kt_nae),
                    'first failing': next((x for x in kt_nae if x['n_fail']), None)},
            'parity': {'runs': len(kt_par), 'verdicts': sum(x['verdicts'] for x in kt_par),
                       'failing knots': sum(x['n_fail'] for x in kt_par),
                       'runs with a failing knot': sum(1 for x in kt_par if x['n_fail']),
                       'disagreements': sum(x['n_disagree'] for x in kt_par),
                       'first failing': next((x for x in kt_par if x['n_fail']), None)},
        },
        'seconds': {'renumber': round(sum(x['sec'] for x in ren), 1),
                    'knot test': round(sum(x['sec'] for x in kt_all), 1)},
        'cut': {'registered half': 'jobs 900-999 (first 100 of the 200 R2 runs) and 1100-1149 (first 50 of the 100 '
                                   'R4 runs), deviations 35',
                'renumbering jobs not run': not_run_ren,
                'knot tests of the half not run': [{'job': k, 'run': C.run_key(jobs[k]['run'])} for k in not_run_half],
                'knot tests outside the half not run': len(not_run_out)},
        'knot test outside the half (reported apart, not the registered row)': {
            'runs': len(kt_out), 'nae runs': sum(1 for x in kt_out if x['knot_law'] == 'nae'),
            'nae verdicts': sum(x['verdicts'] for x in kt_out if x['knot_law'] == 'nae'),
            'nae failing knots': sum(x['n_fail'] for x in kt_out if x['knot_law'] == 'nae'),
            'parity runs': sum(1 for x in kt_out if x['knot_law'] == 'parity'),
            'parity verdicts': sum(x['verdicts'] for x in kt_out if x['knot_law'] == 'parity'),
            'parity failing knots': sum(x['n_fail'] for x in kt_out if x['knot_law'] == 'parity'),
            'parity runs with a failing knot': sum(1 for x in kt_out if x['knot_law'] == 'parity' and x['n_fail'])},
    }
    with open(C.out_path('controls.json'), 'w') as f:
        json.dump(res, f, indent=1, sort_keys=True)
    C.log(json.dumps(res)[:1500])
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('time', 'run', 'summary', 'rest'))
    ap.add_argument('--chunk', default='0/1')
    ap.add_argument('--kt-half', action='store_true')
    ap.add_argument('--exclude', default='')
    ap.add_argument('--deadline', type=float, default=0)
    a = ap.parse_args()
    C.check_frozen()
    if a.what == 'run':
        run_chunk(a.chunk, a.kt_half)
    elif a.what == 'rest':
        run_rest(a.chunk, {int(x) for x in a.exclude.split(',') if x}, a.deadline)
    elif a.what == 'summary':
        summary()
    else:
        C.cap_memory(6)
        jobs = all_jobs()
        ren = [j for j in jobs if j['kind'] == 'renumber']
        kts = [j for j in jobs if j['kind'] == 'knot test']
        for label, js in (('renumber', ren[::30]), ('knot test', kts[::25])):
            t0 = time.time()
            worst = 0
            for job in js:
                t1 = time.time()
                do_job(job)
                worst = max(worst, time.time() - t1)
            dt = (time.time() - t0) / len(js)
            C.log('%s: %d jobs timed, %.2f s a job, slowest %.1f s; all %d jobs %.1f min of one process'
                  % (label, len(js), dt, worst, len([j for j in jobs if j['kind'] == label]),
                     dt * len([j for j in jobs if j['kind'] == label]) / 60))
