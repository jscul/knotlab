"""Run 3, the arm of parts that came apart (D 4.8): on the pair starts, for each s from 0 to 4, every part X the same as
the two-knot part and every other part Y not the same as X, wholly apart, that are one part again or one part for the
first time by round 7; COPY-LAW(t), CAP-3(t); STEPS-2, MET, STEPS-1 with four rules; both knot laws; 7 rounds.  Readings
as run 2 without the replacement runs, X alone, Y alone and reading (iii).

usage: python -B run3.py [--procs 4] [--renaming n1|n4] [--only substring]
"""
import argparse
import json
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

pm, K, P = mc.pm, mc.K, mc.P


def pair_starts():
    out = dict(mc.STARTS['fold study starts'])
    out.update(mc.STARTS['pair starts, besides those'])
    return out


def renamed_stars(stars, name, renaming):
    if renaming in (None, 'n1'):
        return stars
    if name in mc.STARTS['renamings'] and renaming in mc.STARTS['renamings'][name]:
        m = mc.STARTS['renamings'][name][renaming]
    elif renaming == 'n4':
        m = mc.n4_map(stars, name)
    else:
        raise ValueError((name, renaming))
    return [[m[str(l)] for l in k] for k in stars]


def find_pairs(A, view, twoknot_ref, rounds=7):
    """D 4.8: (s, X, Y) with X the same as the two-knot part, Y another part not the same as X, wholly apart, one part
    again or one part for the first time by round 7."""
    pairs = []
    for s in range(0, min(4, A.rounds_done - 1) + 1):
        R = view.roster(s)
        cls = pm.roster_classes(R)
        same = [mc.same_as(twoknot_ref, R, p_) for p_ in R.parts]
        for i, Xp in enumerate(R.parts):
            if not same[i]:
                continue
            for j, Yp in enumerate(R.parts):
                if j == i or same[j] or cls[i] == cls[j]:
                    continue
                t = P.one_part_again(view, s, list(Xp), list(Yp))
                if t is not None and t <= rounds:
                    pairs.append({'s': s, 'X': list(Xp), 'Y': list(Yp), 'meeting_round': t,
                                  'came_apart': P.came_apart(view, s, list(Xp), list(Yp))})
    return pairs


def do_job(job):
    C.cap_memory(job.get('mem', 6))
    t0 = time.time()
    out = {'job': job, 'pairs': []}
    try:
        kl = job['knot_law']
        law = mc.make_law(job['base'], job['take'], job['choice'], kl)
        out['law'] = law.name()
        stars = renamed_stars(pair_starts()[job['start']], job['start'], job.get('renaming'))
        S0 = pm.from_stars(stars, reverse_names=(job.get('renaming') == 'n1'))
        A = mc.grow(S0, law, rounds=7)
        view = P.RunView(A)
        out.update({'rounds': A.rounds_done, 'stop': A.stop, 'guard': A.guard, 'knots': A.S.n_knots})
        pairs = find_pairs(A, view, run1.two_knot_ref())
        out['n_pairs'] = len(pairs)
        ktA = mc.knot_tests_A(A)
        out['knot_tests_A'] = ktA
        if kl == 'nae':
            T = mc.ties(A.S, 'nae')
            nd0 = A.snap[0].n_distinctions
            out['ties_made'] = sum(1 for c in T.classes if any(d >= nd0 for d in c))
        for k, p_ in enumerate(pairs):
            d = mc.Design('pair|%s|s=%d|X=%s|Y=%s' % (job['start'], p_['s'], p_['X'], p_['Y']), stars, p_['X'],
                          p_['Y'], p_['s'], family='pair', renaming=job.get('renaming'))
            ref = mc.Reference(A.snap[p_['s']], view.roster(p_['s']), p_['Y'], p_['s'], X=p_['X'])
            row, _ = run2.analyse(d, law, kl, A, view, ref, {}, seed=7000 + k, ktA=ktA, alone_runs=False)
            row.update({'s': p_['s'], 'X': p_['X'], 'Y': p_['Y'], 'came_apart': p_['came_apart']})
            row.pop('knot_tests_A', None)
            out['pairs'].append(row)
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    return out


def jobs(renaming=None):
    js = []
    for st in pair_starts():
        for base in mc.BASES_COPY + mc.BASES_CAP3:
            for take in ('STEPS-2', 'MET', 'STEPS-1'):
                for ch in mc.RULES:
                    for kl in ('nae', 'parity'):
                        js.append({'start': st, 'base': base, 'take': take, 'choice': ch, 'knot_law': kl,
                                   'renaming': renaming})
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--mem', type=float, default=6)
    ap.add_argument('--renaming', default=None)
    ap.add_argument('--only', default=None)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    js = jobs(args.renaming)
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    for j in js:
        j['mem'] = args.mem
    name = args.out or ('run3.jsonl.gz' if not args.renaming else 'run3_%s.jsonl.gz' % args.renaming)
    C.log('run 3:', len(js), 'runs')
    out = C.JsonLines(name)
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for i, f in enumerate(as_completed([ex.submit(do_job, j) for j in js])):
            r = f.result()
            out.write(r)
            if 'error' in r or (i + 1) % 100 == 0 or r.get('seconds', 0) > 120:
                C.log(i + 1, '/', len(js), r.get('law'), r['job']['start'], r.get('n_pairs'), r.get('seconds'),
                      r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
