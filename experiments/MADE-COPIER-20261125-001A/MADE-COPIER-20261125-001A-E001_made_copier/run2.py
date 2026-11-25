"""Run 2 (and run 3's pair arm, see run3.py): per law (a base law, MET or STEPS-1, a rule, a knot law), every design:
run A, B(i), B_X, M, M', M_Y (= M), M'_Y, X alone, Y alone; the three readings by descent at every round; the parts the
same as each member of the class (condition 2, the parts by descent, the census); the fourth mark on the replacement
runs; the owner's arm (D 7.1 to 7.7, 7.10); PO1; the knot tests.

usage: python -B run2.py [--procs 6] [--only substring]
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
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def course(runA, runB, pat, s, T):
    """FD 5.2, 5.5: the pattern's trace in two runs through round T: first differing round, way, demand line."""
    a = [r for r in P.trace(runA, pat, s, min(T, runA.rounds_done)) if r['t'] <= T]
    b = [r for r in P.trace(runB, pat, s, min(T, runB.rounds_done)) if r['t'] <= T]
    d, way, dem, n = P.first_difference(a, b)
    return {'differs': d, 'way': way, 'demand_line': dem, 'rounds_compared': n}, a, b


def same_course(runA, runB, pat, s, T):
    a = [r for r in P.trace(runA, pat, s, min(T, runA.rounds_done)) if r['t'] <= T]
    b = [r for r in P.trace(runB, pat, s, min(T, runB.rounds_done)) if r['t'] <= T]
    return P.first_difference(a, b)[0] is None


def fa_trace(run, pat, s, T):
    tr = [r for r in P.trace(run, pat, s, min(T, run.rounds_done)) if r['t'] <= T]
    return P.first_appearance(tr)


def fa_diff(t1, t2, s):
    n = min(len(t1), len(t2))
    for i in range(n):
        if t1[i] != t2[i]:
            return s + 1 + i
    return None


def class_of(name):
    if name.startswith('made') or name == 'made-2-exchanged':
        return mc.CLASS_MADE
    return mc.CLASS_START


def run_design(d, law, kl, A=None):
    """Run A and its references."""
    A = A or mc.grow(d, law)
    view = P.RunView(A)
    s = d.s
    if A.rounds_done < s:
        return A, view, None
    ref = mc.Reference(A.snap[s], view.roster(s), d.Y, s, X=d.X)
    return A, view, ref


def analyse(d, law, kl, A, view, ref, refs, seed, ktA=None, alone_runs=True):
    """Everything for one design under one law, given run A and the references of the class members."""
    s, X, Y = d.s, d.X, d.Y
    row = {'design': d.name, 'rounds': A.rounds_done, 'stop': A.stop, 'guard': A.guard, 'knots': A.S.n_knots}
    if ref is None:
        row['note'] = 'run A ended before round s'
        return row, None
    rr = mc.readings_per_round(A, ref, X, Y, s, kl, seed=seed)
    row['values'] = mc.values_flags(rr)
    row['form'] = mc.form_flags(rr)
    row['built'] = mc.built_flags(rr)
    row['per_round'] = [{'t': r['t'], 'knots': r['knots'], 'form': r['form'], 'built_n': r['built']['n'],
                         'built_bound': r['built']['bound_hit'], 'built_pair': r['built'].get('disjoint_pair'),
                         'values_Y': r['values_Y'][:4], 'values_X': r['values_X'][:4], 'made_tied': r['made_tied'],
                         'made_tied_classes': r['made_tied_classes'][:3]} for r in rr['rows']]
    row['eligible_Y'] = rr['eligible_Y']
    row['ties_after_s'] = rr['ties_s']
    # parts the same as each member of the class, by descent, at each round (condition 2; D 5.3)
    cross = {}
    for yn, yref in refs.items():
        per = []
        for t in range(s + 1, A.rounds_done + 1):
            S_t = A.snap[t]
            desc = mc.descent_map(S_t, X, Y, s)
            parts = mc.form_reading(yref, S_t, view.roster(t), desc)
            per.append(dict(Counter(p['descent'] for p in parts)))
        cross[yn] = per
    row['parts_same_as_member'] = cross
    # the meeting round and the linking knots
    meet = P.one_part_again(view, s, X, Y)
    row['meeting_round'] = meet
    if meet is not None:
        lk = P.linking(view, meet, X, Y, s)
        row['link'] = {k: lk[k] for k in ('made_connected', 'start_connected', 'link_classes', 'links')}
    # paired runs
    S_s = A.snap[s]
    B1 = mc.run_from_state(A, s, P.bar_part(S_s, Y))
    BX = mc.run_from_state(A, s, P.bar_part(S_s, X))
    M = P.masked_run(view, s, X, Y, 'XY')
    M1 = P.masked_run(view, s, X, Y, 'ISO')          # M': Y and its descendants joinable with nothing
    MY1 = P.masked_run(view, s, Y, X, 'ISO')         # M'_Y: X and its descendants joinable with nothing
    runs = {'B(i)': B1, 'B_X': BX, 'M': M, "M'": M1, "M'_Y": MY1}
    row['comparison_rounds'] = {k: v.rounds_done for k, v in runs.items()}
    T = min(A.rounds_done, B1.rounds_done, BX.rounds_done, M.rounds_done)
    row['T'] = T
    # readings in B(i) (values: does it need Y's births?), B_X (Y handing on its own value), and form in both
    rb = mc.readings_per_round(B1, ref, X, Y, s, kl, built=False, seed=seed + 101)
    rx = mc.readings_per_round(BX, ref, X, Y, s, kl, built=False, seed=seed + 202)
    row['B(i)'] = {'values': mc.values_flags(rb), 'form': mc.form_flags(rb)}
    row['B_X'] = {'values': mc.values_flags(rx), 'form': mc.form_flags(rx)}
    # courses
    cx, _, _ = course(A, B1, X, s, T)
    if cx['differs'] is not None:
        cx['confirmed'] = ('through a meeting' if same_course(M, B1, X, s, T) else
                           'through a third part' if same_course(M1, B1, X, s, T) else 'unconfirmed')
    cy, _, _ = course(A, BX, Y, s, T)
    if cy['differs'] is not None:
        cy['confirmed'] = ('through a meeting' if same_course(M, BX, Y, s, T) else
                           'through a third part' if same_course(MY1, BX, Y, s, T) else 'unconfirmed')
    row['X_course'] = cx
    row['Y_course'] = cy
    tk = mc.takes_between(A, X, Y, s, T)
    row['takes'] = tk
    row['takes_vs_X_course'] = mc.relation(_first(tk['X takes from Y'], tk['Y takes from X']), cx['differs'])
    row['takes_vs_Y_course'] = mc.relation(_first(tk['X takes from Y'], tk['Y takes from X']), cy['differs'])
    # endings
    eA_X, eA_Y = mc.ending(A, X, s, T), mc.ending(A, Y, s, T)
    eB_X = mc.ending(B1, X, s, T)
    eM_X = mc.ending(M, X, s, T)
    eBX_Y = mc.ending(BX, Y, s, T)
    eM_Y = mc.ending(M, Y, s, T)
    row['endings'] = {'X in A': eA_X, 'Y in A': eA_Y, 'X in B(i)': eB_X, 'X in M': eM_X, 'Y in B_X': eBX_Y,
                      'Y in M_Y': eM_Y}
    ii = (eA_X['round_of_ending'] is not None and eB_X['round_of_ending'] is None and
          eA_Y.get('state') == 'makes a birth in round T')
    ii_rev = (eA_Y['round_of_ending'] is not None and eBX_Y['round_of_ending'] is None and
              eA_X.get('state') == 'makes a birth in round T')
    row['reading_ii'] = {'holds': ii, 'through a meeting': ii and eM_X['round_of_ending'] is None}
    row['reading_ii_reverse'] = {'holds': ii_rev, 'through a meeting': ii_rev and eM_Y['round_of_ending'] is None}
    # X alone, Y alone
    if alone_runs and d.name in mc.STARTS['alone']:
        xa = mc.alone(d.name, 'X alone')
        ya = mc.alone(d.name, 'Y alone')
        XA = mc.grow(xa, law)
        YA = mc.grow(ya, law)
        T3 = min(T, XA.rounds_done, YA.rounds_done)
        row['T_iii'] = T3
        tA = fa_trace(A, X, s, T3)
        tXA = fa_trace(XA, xa.X, xa.s, T3)
        x_alone_diff = fa_diff(tA, tXA, s)
        tAy = fa_trace(A, Y, s, T3)
        tYA = fa_trace(YA, ya.Y, ya.s, T3)
        y_alone_diff = fa_diff(tAy, tYA, s)
        row['X_alone'] = {'X course differs from X alone at': x_alone_diff, 'rounds': XA.rounds_done,
                          'knot_tests': mc.knot_tests_A(XA)}
        row['Y_alone'] = {'Y course differs from Y alone at': y_alone_diff, 'rounds': YA.rounds_done,
                          'knot_tests': mc.knot_tests_A(YA)}
        # values / form in X alone (X's own course: is there a part the same as Y, or two made distinctions?)
        vXA = P.RunView(XA)
        if XA.rounds_done >= xa.s:
            per = []
            for t in range(xa.s + 1, XA.rounds_done + 1):
                S_t = XA.snap[t]
                desc = mc.descent_map(S_t, xa.X, [], xa.s)
                parts = mc.form_reading(ref, S_t, vXA.roster(t), desc)
                per.append(dict(Counter(p['descent'] for p in parts)))
            row['X_alone']['parts_same_as_Y'] = per
        # reading (iii) and its reverse at T_iii
        cx3, _, _ = course(A, B1, X, s, T3)
        cx3_conf = cx3['differs'] is not None and same_course(M, B1, X, s, T3)
        cy3, _, _ = course(A, BX, Y, s, T3)
        cy3_conf = cy3['differs'] is not None and same_course(M, BX, Y, s, T3)
        eA_Y3 = mc.ending(A, Y, s, T3)
        eA_X3 = mc.ending(A, X, s, T3)
        iii = (cx3_conf and x_alone_diff is not None and cy3['differs'] is None and
               eA_Y3.get('state') == 'makes a birth in round T')
        iii_rev = (cy3_conf and y_alone_diff is not None and cx3['differs'] is None and
                   eA_X3.get('state') == 'makes a birth in round T')
        row['reading_iii'] = iii
        row['reading_iii_reverse'] = iii_rev
    # PO1 on run A
    row['PO1'] = mc.po1_check(A, X, s, kl)
    # knot tests
    ktA = ktA or mc.knot_tests_A(A)
    row['knot_tests_A'] = ktA
    fails = [f['knot'] for f in ktA['fails'] if f['round'] <= s]
    row['knot_tests_cmp'] = {k: mc.knot_tests_cmp(v, s, fails) for k, v in runs.items()}
    # the fourth mark: X's trace renamed by first appearance (compared across the replacement runs by the caller)
    fa = fa_trace(A, X, s, A.rounds_done)
    return row, fa


def _first(a, b):
    xs = [x for x in (a, b) if x is not None]
    return min(xs) if xs else None


def two_users(d, law, kl, case):
    """D 3.3: whether the two are later taken by different births (run A to 8 rounds)."""
    A8 = mc.grow(d, law, rounds=8)
    t0, two = case['t'], case['two']
    takers = {x: [] for x in two}
    for rec in A8.records[t0:]:
        for b in rec['births']:
            for x in two:
                if x in b['inputs']:
                    takers[x].append((rec['round'], b['id']))
    a, b = two[0], two[1]
    diff = bool(takers[a] and takers[b] and {i for _, i in takers[a]} != {i for _, i in takers[b]})
    tie_last = None
    if A8.rounds_done >= 8:
        T8 = mc.ties(A8.snap[8], kl)
        tie_last = T8.tied(a, case['v']) and T8.tied(b, case['v'])
    return {'takers': {str(k): v[:8] for k, v in takers.items()}, 'taken by different births': diff,
            'still tied at round 8': tie_last, 'rounds': A8.rounds_done}


def do_job(job):
    C.cap_memory(job.get('mem', 6))
    t0 = time.time()
    out = {'job': job, 'designs': {}}
    try:
        kl = job['knot_law']
        law = mc.make_law(job['base'], job['take'], job['choice'], kl)
        out['law'] = law.name()
        designs = job.get('designs') or mc.RUN2_DESIGNS
        runs = {}
        for name in designs:
            d = mc.design(name, renaming=job.get('renaming'))
            runs[name] = (d,) + run_design(d, law, kl)
        # references of the class members (each from its own run A under this law)
        refs_made = {n: runs[n][3] for n in mc.CLASS_MADE if n in runs and runs[n][3] is not None}
        refs_start = {n: runs[n][3] for n in mc.CLASS_START if n in runs and runs[n][3] is not None}
        fas = {}
        for i, name in enumerate(designs):
            d, A, view, ref = runs[name]
            refs = refs_made if (name.startswith('made')) else refs_start
            row, fa = analyse(d, law, kl, A, view, ref, refs, seed=1000 * i)
            if row.get('values', {}).get('Y_by_X_some'):
                case = next(c for c in row['values']['cases'] if c['made_by_X'])
                row['two_users'] = two_users(d, law, kl, case)
            out['designs'][name] = row
            fas[name] = fa
        # the fourth mark on the replacement runs: same X, law, rule and naming; Y against Y'
        fm = {}
        for fam in (mc.CLASS_MADE, mc.CLASS_START):
            for a in fam:
                for b in fam:
                    if a < b and fas.get(a) is not None and fas.get(b) is not None:
                        s = runs[a][0].s
                        fm['%s|%s' % (a, b)] = fa_diff(fas[a], fas[b], s)
        out['fourth_mark'] = fm
    except Exception as e:
        out['error'] = repr(e)
        out['trace'] = traceback.format_exc()
    out['seconds'] = round(time.time() - t0, 1)
    out['peak_mb'] = C.peak_mb()
    return out


def jobs(renaming=None, designs=None, extra=None):
    js = []
    for base in mc.NINE:
        for take in ('MET', 'STEPS-1'):
            for ch in mc.RULES:
                for kl in ('nae', 'parity'):
                    j = {'base': base, 'take': take, 'choice': ch, 'knot_law': kl, 'renaming': renaming}
                    if designs:
                        j['designs'] = designs
                    js.append(j)
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--mem', type=float, default=6)
    ap.add_argument('--only', default=None)
    ap.add_argument('--out', default='run2.jsonl.gz')
    ap.add_argument('--append', action='store_true', help='skip the laws already in the output and append')
    args = ap.parse_args()
    js = jobs()
    if args.append:
        done = {json.dumps({k: r['job'][k] for k in ('base', 'take', 'choice', 'knot_law')}, sort_keys=True)
                for r in C.read_jsonl(args.out) if 'error' not in r}
        js = [j for j in js if json.dumps({k: j[k] for k in ('base', 'take', 'choice', 'knot_law')},
                                          sort_keys=True) not in done]
    if args.only:
        js = [j for j in js if all(x in json.dumps(j) for x in args.only.split(','))]
    for j in js:
        j['mem'] = args.mem
    C.log('run 2:', len(js), 'laws')
    out = C.JsonLines(args.out, mode='a' if args.append else 'w')
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        futs = [ex.submit(do_job, j) for j in js]
        for i, f in enumerate(as_completed(futs)):
            r = f.result()
            out.write(r)
            C.log(i + 1, '/', len(js), r.get('law'), r.get('seconds'), r.get('error', ''))
    out.close()


if __name__ == '__main__':
    main()
