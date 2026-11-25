"""Runs 1, 3 and 7 of the pre-registration ("Runs (frozen)"): every start, base law and law, both knot laws, run A
with its per-round readings, the paired test on the pairs of definitions section 5 item 8, and the knot tests.

usage: python -B runs.py run1|run3|run7 [--procs 8] [--mem 6]
Writes run<k>.jsonl.gz (one line per run A) to the artifact folder.
"""
import argparse
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

import common as C
import paired as P
import pm

T3 = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
TSHORT = {'CANCEL-RETIRE': 'RETIRE', 'CANCEL-OFFSHOOT': 'OFFSHOOT', 'CANCEL-WAIT': 'WAIT'}


def base_pairs():
    """The 21 base-law and start pairs of runs 1 and 3."""
    out = []
    for st in pm.RING_STARTS:
        out.append(('RING-LAW', dict(ration='CAP-3', treatment='CANCEL-WAIT'), st))
    for t in T3:
        for st in pm.COPIER_STARTS:
            out.append(('COPY-LAW(%s)' % TSHORT[t], dict(ration='FLOOR1', treatment=t), st))
    for t in T3:
        for st in pm.COPIER_STARTS:
            out.append(('CAP-3(%s)' % TSHORT[t], dict(ration='CAP-3', treatment=t), st))
    return out


def laws_run1(base, st):
    """none; Q(OLDEST, NEWEST, IN-TURN, BY-COUNT); SHORT-TAKES(OLDEST, NEWEST); the late start of Q(O, N), SHORT-TAKES(O, N)."""
    s0 = pm.LATE_S0[st]
    out = [('none', dict())]
    for c in ('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT'):
        out.append(('Q(%s)' % c, dict(take='Q', choice=c)))
    for c in ('OLDEST', 'NEWEST'):
        out.append(('SHORT-TAKES(%s)' % c, dict(treatment='SHORT-TAKES', choice=c)))
    for c in ('OLDEST', 'NEWEST'):
        out.append(('late Q(%s)' % c, dict(take='Q', choice=c, late=s0)))
    for c in ('OLDEST', 'NEWEST'):
        out.append(('late SHORT-TAKES(%s)' % c, dict(treatment='SHORT-TAKES', choice=c, late=s0,
                                                    base_treatment=base['treatment'])))
    return out


def laws_run3(base, st):
    out = [('RECORD-2', dict(joinable='RECORD-2')), ('RECORD-3', dict(joinable='RECORD-3')),
           ('ALL-JOINABLE', dict(joinable='ALL')), ('CARRY', dict(take='CARRY'))]
    for rule in ('MET', 'STEPS-1', 'STEPS-2', 'UP-TO-2'):
        for c in ('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT'):
            out.append(('%s(%s)' % (rule, c), dict(take=rule, choice=c)))
    out.append(('FIRST(PARTS)(OLDEST)', dict(take='FIRST', choice='OLDEST')))
    return out


def jobs_for(which):
    jobs = []
    if which in ('run1', 'run3'):
        for bname, bkw, st in base_pairs():
            lf = laws_run1 if which == 'run1' else laws_run3
            for lname, lkw in lf(bkw, st):
                for kl in ('nae', 'parity'):
                    kw = dict(bkw)
                    kw.update(lkw)
                    jobs.append({'run': which, 'base': bname, 'start': st, 'law_name': lname, 'knot_law': kl,
                                 'kw': kw, 'every_pair': False})
    elif which == 'carry-alt':
        # supplementary (deviations item 37): CARRY under the other reading of "a take never repeats"
        for bname, bkw, st in base_pairs():
            for kl in ('nae', 'parity'):
                kw = dict(bkw)
                kw.update(dict(take='CARRY', carry_filter=True))
                jobs.append({'run': which, 'base': bname, 'start': st, 'law_name': 'CARRY(oldest not taken)',
                             'knot_law': kl, 'kw': kw, 'every_pair': False})
    elif which == 'run7':
        bases = [('COPY-LAW(%s)+HOLD' % TSHORT[t], dict(ration='FLOOR1', treatment=t, release='HOLD')) for t in T3]
        bases.append(('RING-LAW+HOLD', dict(ration='CAP-3', treatment='CANCEL-WAIT', release='HOLD')))
        for bname, bkw in bases:
            for st in ('two-knot', 'three-knot', 'Ring(5,3)'):
                for lname, lkw in (('none', {}), ('Q(OLDEST)', dict(take='Q', choice='OLDEST')),
                                   ('Q(NEWEST)', dict(take='Q', choice='NEWEST')),
                                   ('STEPS-2(OLDEST)', dict(take='STEPS-2', choice='OLDEST'))):
                    for kl in ('nae', 'parity'):
                        kw = dict(bkw)
                        kw.update(lkw)
                        jobs.append({'run': which, 'base': bname, 'start': st, 'law_name': lname, 'knot_law': kl,
                                     'kw': kw, 'every_pair': True})
    return jobs


def do_job(job, mem):
    C.cap_memory(mem)
    t0 = time.time()
    try:
        law = pm.Law(knot_law=job['knot_law'], **job['kw'])
        out, view = P.analyse_run(job['start'], law, rev=job.get('rev', False), every_pair=job['every_pair'])
        out.update({k: job[k] for k in ('run', 'base', 'law_name', 'knot_law')})
        out['seconds'] = round(time.time() - t0, 2)
        out['peak_mb'] = C.peak_mb()
        return out
    except MemoryError:
        return {'error': 'MemoryError', **{k: job[k] for k in ('run', 'base', 'start', 'law_name', 'knot_law')},
                'seconds': round(time.time() - t0, 2)}
    except Exception as e:  # reported, never hidden
        return {'error': repr(e), 'trace': traceback.format_exc(),
                **{k: job[k] for k in ('run', 'base', 'start', 'law_name', 'knot_law')},
                'seconds': round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('which', choices=('run1', 'run3', 'run7', 'carry-alt'))
    ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--mem', type=float, default=6)
    ap.add_argument('--only', default=None, help='substring filter on base/start/law (development)')
    args = ap.parse_args()
    jobs = jobs_for(args.which)
    if args.only:
        jobs = [j for j in jobs if args.only in '%s|%s|%s|%s' % (j['base'], j['start'], j['law_name'], j['knot_law'])]
    C.log(args.which, len(jobs), 'runs')
    out = C.JsonLines('%s.jsonl.gz' % args.which if not args.only else 'dev_%s.jsonl.gz' % args.which)
    done = 0
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = {ex.submit(do_job, j, args.mem): j for j in jobs}
        for f in as_completed(futs):
            r = f.result()
            out.write(r)
            done += 1
            if 'error' in r or done % 50 == 0 or r.get('seconds', 0) > 60:
                C.log(done, '/', len(jobs), r.get('base'), r.get('start'), r.get('law_name'), r.get('knot_law'),
                      r.get('seconds'), r.get('error', ''))
    out.close()
    C.log('done', args.which)


if __name__ == '__main__':
    main()
