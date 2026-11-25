"""Run 6 (P2): under not-all-equal, every tie class containing a made distinction, in every run of runs 2 and 3
(run A and every comparison run, regrown as those runs grow them).  Runs 1, 3 (run A), 4 and 5 read their own ties
(run1.jsonl.gz 'ties_made', run3.jsonl.gz 'ties_made', run4.jsonl 'histories with a tie class', run 5's
'nae_made_ties').  By S1 a tie among the distinctions existing after a round is the same after every later round, so
each run is read at its last round.

usage: python -B run6.py [--procs 4]
"""
import argparse
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run1  # noqa: E402
import run2  # noqa: E402
import run3  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def made_ties(run):
    nd0 = run.snap[0].n_distinctions
    T = mc.ties(run.snap[run.rounds_done], 'nae')
    cl = [c for c in T.classes if any(x >= nd0 for x in c)]
    return {'n': len(cl), 'classes': cl[:4], 'unsat': T.unsat, 'rounds': run.rounds_done}


def comparison_runs(A, view, X, Y, s):
    S_s = A.snap[s]
    return {'B(i)': mc.run_from_state(A, s, P.bar_part(S_s, Y)), 'B_X': mc.run_from_state(A, s, P.bar_part(S_s, X)),
            'M': P.masked_run(view, s, X, Y, 'XY'), "M'": P.masked_run(view, s, X, Y, 'ISO'),
            "M'_Y": P.masked_run(view, s, Y, X, 'ISO')}


def do2(job):
    C.cap_memory(6)
    t0 = time.time()
    out = {'run': 2, 'job': job, 'rows': {}}
    try:
        law = mc.make_law(job['base'], job['take'], job['choice'], 'nae')
        out['law'] = law.name()
        for name in mc.RUN2_DESIGNS:
            d = mc.design(name)
            A = mc.grow(d, law)
            row = {'A': made_ties(A)}
            if A.rounds_done >= d.s:
                view = P.RunView(A)
                for k, r in comparison_runs(A, view, d.X, d.Y, d.s).items():
                    row[k] = made_ties(r)
            if name in mc.STARTS['alone']:
                row['X alone'] = made_ties(mc.grow(mc.alone(name, 'X alone'), law))
                row['Y alone'] = made_ties(mc.grow(mc.alone(name, 'Y alone'), law))
            out['rows'][name] = row
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def do3(job):
    C.cap_memory(6)
    t0 = time.time()
    out = {'run': 3, 'job': job, 'rows': []}
    try:
        law = mc.make_law(job['base'], job['take'], job['choice'], 'nae')
        out['law'] = law.name()
        A = mc.grow(pm.from_stars(run3.pair_starts()[job['start']]), law, rounds=7)
        view = P.RunView(A)
        for p_ in run3.find_pairs(A, view, run1.two_knot_ref()):
            row = {'s': p_['s'], 'X': p_['X'], 'Y': p_['Y']}
            for k, r in comparison_runs(A, view, p_['X'], p_['Y'], p_['s']).items():
                row[k] = made_ties(r)
            out['rows'].append(row)
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    C.cap_memory(7)
    js = [(do2, j) for j in run2.jobs() if j['knot_law'] == 'nae']
    js += [(do3, r['job']) for r in C.read_jsonl('run3.jsonl.gz') if r['job']['knot_law'] == 'nae' and r.get('pairs')]
    C.log('run 6:', len(js), 'jobs')
    out = C.JsonLines('run6.jsonl.gz')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = [ex.submit(fn, j) for fn, j in js]
        for i, f in enumerate(as_completed(futs)):
            r = f.result()
            out.write(r)
            if 'error' in r or (i + 1) % 10 == 0 or i + 1 == len(js):
                C.log(i + 1, '/', len(js), r.get('law'), r.get('seconds'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
