"""Run 1 (P1, P3; P2 and P10 on its runs): the two-knot, three-knot and Ring(5, 3) starts; COPY-LAW(t), CAP-3(t),
FBP(t); no taking rule, Q, MET, STEPS-1, STEPS-2 with four rules; both knot laws; 8 rounds.  Per round: N(t), the parts
the same as the two-knot part; every birth's fresh count; the knot tests; under not-all-equal every tie class containing
a made distinction (run 6).

usage: python -B run1.py [--procs 4]
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

pm, K, P = mc.pm, mc.K, mc.P
STARTS1 = ['two-knot', 'three-knot', 'Ring(5,3)']


def two_knot_ref():
    law = mc.make_law('COPY-LAW(RETIRE)', None, 'OLDEST', 'parity')
    A = pm.Run(pm.from_stars([[0, 1, 2], [0, 3, 4]]), law, rounds=1)
    S1 = A.snap[1]
    R1 = pm.roster_of(S1.copy(), law)
    return mc.Reference(S1, R1, [2, 3], 1)


def jobs():
    out = []
    for st in STARTS1:
        for base in mc.NINE:
            for take in (None, 'Q', 'MET', 'STEPS-1', 'STEPS-2'):
                for ch in (mc.RULES if take else ('OLDEST',)):
                    for kl in ('nae', 'parity'):
                        out.append({'start': st, 'base': base, 'take': take, 'choice': ch if take else None,
                                    'knot_law': kl})
    return out


def do(job):
    C.cap_memory(6)
    t0 = time.time()
    try:
        law = mc.make_law(job['base'], job['take'], job['choice'] or 'OLDEST', job['knot_law'])
        stars = mc.STARTS['fold study starts'][job['start']]
        A = pm.Run(pm.from_stars(stars), law, rounds=8, knot_bound=mc.KNOT_BOUND)
        view = P.RunView(A)
        ref = two_knot_ref()
        N = []
        for t in range(A.rounds_done + 1):
            R = view.roster(t)
            N.append(sum(1 for part in R.parts if mc.same_as(ref, R, part)))
        # P1: fresh counts
        S = A.S
        exceptions = Counter_()
        bad = []
        for rec in A.records:
            for b in rec['births']:
                f = b['f']
                ps = b['parents']
                start_parent_offshoot = (b['kind'] == 'offshoot' and S.made[ps[0]] == 0)
                parents_all_start = (b['kind'] == 'offshoot' and all(S.made[g] == 0 for g in S.parents[ps[0]])
                                     and S.parents[ps[0]])
                ok = (f == 1) or (f == 0 and b['implied'])
                if not ok:
                    key = ('offshoot of a start knot' if start_parent_offshoot else
                           'offshoot of a knot whose parents are all start knots' if parents_all_start else
                           '%s with %d inputs' % (b['kind'], len(b['inputs'])))
                    exceptions[(key, f)] += 1
                    if not start_parent_offshoot and not (job['take'] == 'STEPS-2' and parents_all_start):
                        if len(bad) < 10:
                            bad.append({'round': rec['round'], 'id': b['id'], 'kind': b['kind'], 'parents': ps,
                                        'inputs': b['inputs'], 'f': f, 'implied': b['implied']})
        kt = mc.knot_tests_A(A)
        tie = None
        if job['knot_law'] == 'nae':
            T = mc.ties(A.S, 'nae')
            nd0 = A.snap[0].n_distinctions
            tie = {'classes_with_made': [c for c in T.classes if any(d >= nd0 for d in c)][:10],
                   'n_classes_with_made': sum(1 for c in T.classes if any(d >= nd0 for d in c)),
                   'unsat': T.unsat}
        return dict(job, law=law.name(), rounds=A.rounds_done, stop=A.stop, guard=A.guard, knots=A.S.n_knots,
                    N=N, fresh_exceptions={'%s|f=%d' % k: v for k, v in exceptions.items()}, fresh_bad=bad,
                    knot_tests=kt, ties_made=tie, seconds=round(time.time() - t0, 2))
    except Exception as e:
        return dict(job, error=repr(e), trace=traceback.format_exc())


def Counter_():
    from collections import Counter
    return Counter()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--append', action='store_true', help='skip the runs already in the output and append')
    args = ap.parse_args()
    js = jobs()
    key = ('start', 'base', 'take', 'choice', 'knot_law')
    if args.append:
        done = {tuple(r[k] for k in key) for r in C.read_jsonl('run1.jsonl.gz') if 'error' not in r}
        js = [j for j in js if tuple(j[k] for k in key) not in done]
    C.log('run 1:', len(js), 'runs')
    out = C.JsonLines('run1.jsonl.gz', mode='a' if args.append else 'w')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for i, f in enumerate(as_completed([ex.submit(do, j) for j in js])):
            r = f.result()
            out.write(r)
            if 'error' in r or (i + 1) % 100 == 0:
                C.log(i + 1, r.get('start'), r.get('base'), r.get('take'), r.get('choice'), r.get('knot_law'),
                      r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
