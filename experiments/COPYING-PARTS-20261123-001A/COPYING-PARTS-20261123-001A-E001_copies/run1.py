"""Run 1: the two small starts and Ring(5, 3) under the nine laws (FLOOR0, FLOOR1, ONE-FEWER x CANCEL-RETIRE,
CANCEL-OFFSHOOT, CANCEL-WAIT; RELEASE; parity), 24 rounds, cut off past 20,000 knots (A-D9; deviations.md C2).
N(t) after every round; every return of a two-knot part with the parts that came apart; the recurrences of P1-P3
(deviations.md C3); P1's returns.  Writes run1.json."""
import time

from cpcommon import (E, N_series, RUN1_STARTS, copying_summary, copy_returns, is_two_knot_part, log, nine_laws,
                      part_shape, resources, shape_key, two_knot_parts, write)

R = 24
CAP = 20000

RECS = {
    'P1': ('CANCEL-RETIRE', 0, lambda N, t: 2 * N[t]),
    'P2': ('CANCEL-OFFSHOOT', 1, lambda N, t: 2 * N[t] + N[t - 1]),
    'P3': ('CANCEL-WAIT', 2, lambda N, t: 2 * N[t] + N[t - 2]),
}


def knots_by_round(run, start_knots):
    return [start_knots] + [rec['n_knots'] for rec in run.records]


def last_round_under(knots, cap):
    good = [t for t, k in enumerate(knots) if k <= cap]
    return max(good)


def check_recurrence(N, lo_offset, f, Rlast):
    t0 = next((t for t, x in enumerate(N) if x > 0), None)
    if t0 is None:
        return {'t0': None, 'checked': [], 'ok': False, 'why': 'no two-knot part'}
    lo = t0 + lo_offset
    rows = []
    for t in range(lo, Rlast - 2 + 1):
        exp = f(N, t)
        rows.append({'t': t, 'N(t+2)': N[t + 2], 'expected': exp, 'ok': N[t + 2] == exp})
    fails = [r for r in rows if not r['ok']]
    return {'t0': t0, 't_range': [lo, Rlast - 2], 'n_checked': len(rows), 'ok': bool(rows) and not fails,
            'failures': fails[:10]}


def two_knot_returns(run, Rlast):
    """Every two-knot part Y after every round s: its return (A-D6), with what came apart (deviations.md C3)."""
    rets = {(r['s'], tuple(r['part'])): r for r in run.find_returns()}
    agg = {}
    first_full = {}
    n_parts = n_checkable = 0
    p1_fail = []
    unreturned = []
    for s in range(0, run.rounds_done + 1):
        ros = run.rosters[s]
        for i in two_knot_parts(ros):
            n_parts += 1
            Y = ros.parts[i]
            r = rets.get((s, Y))
            checkable = s + 2 <= Rlast
            n_checkable += int(checkable)
            if r is None:
                if checkable:
                    unreturned.append({'s': s, 'part': list(Y)})
                continue
            if r['t'] > Rlast:
                continue
            rt = run.rosters[r['t']]
            offs = [tuple(P) for P in r['off_parts']]
            same = [run.cache.same(ros, Y, rt, P) for P in offs]
            off_desc = sorted(shape_key(part_shape(rt, P)) + (' [same as Y]' if sm else '')
                              for P, sm in zip(offs, same))
            key = 'period %d | %d off | %s' % (r['period'], len(offs), ' + '.join(off_desc))
            a = agg.setdefault(key, {'count': 0, 'first_s': s})
            a['count'] += 1
            if key not in first_full:
                first_full[key] = {'s': s, 't': r['t'], 'part': list(Y), 'same_part': r['same_part'],
                                   'off_parts': [list(P) for P in offs], 'off_same_as_Y': same}
            if checkable and not (r['t'] == s + 2 and len(offs) == 1 and all(same)):
                p1_fail.append({'s': s, 'part': list(Y), 't': r['t'], 'n_off': len(offs), 'off': off_desc})
    return {'n_two_knot_parts': n_parts, 'n_checkable_s_le_R_minus_2': n_checkable,
            'unreturned_checkable': unreturned[:10], 'n_unreturned_checkable': len(unreturned),
            'kinds': [dict(v, kind=k, example=first_full[k]) for k, v in sorted(agg.items())],
            'p1_pattern_failures': p1_fail[:10], 'n_p1_pattern_failures': len(p1_fail),
            'p1_pattern_ok': n_checkable > 0 and not p1_fail and not unreturned}


def main():
    out = {'R': R, 'cap': CAP, 'runs': {}, 'P1': {}, 'P2': {}, 'P3': {}, 'recurrences_all_rations': {}}
    for sname, mk in RUN1_STARTS:
        for law in nine_laws():
            t_start = time.time()
            S0 = mk()
            run = E.Run(S0, law, R, knot_cap=CAP)
            t_grow = time.time() - t_start
            N = N_series(run)
            knots = knots_by_round(run, S0.n_knots)
            Ra = run.rounds_done
            Rb = last_round_under(knots, CAP)
            t1 = time.time()
            tk = {'C2-a': two_knot_returns(run, Ra)}
            if Rb != Ra:
                tk['C2-b'] = two_knot_returns(run, Rb)
            crs = copy_returns(run)
            t_ret = time.time() - t1
            key = '%s|%s' % (sname, law.name())
            rec = {'start': sname, 'law': law.to_dict(), 'rounds_done': Ra, 'cut_off': run.cut_off,
                   'last_round_under_cap': Rb, 'N': N, 'knots': knots,
                   'members': [len(r.members) for r in run.rosters], 'parts': [len(r.parts) for r in run.rosters],
                   'births': [r['n_births'] for r in run.records],
                   'kind': run.kind(), 'first_event': run.first_event(), 'n_returns': len(run.find_returns()),
                   'mixed_parts': len(getattr(run, 'mixed_parts', [])),
                   'two_knot_returns': tk, 'copying': copying_summary(run, crs),
                   'seconds': {'grow': round(t_grow, 1), 'returns': round(t_ret, 1)}}
            out['runs'][key] = rec
            # recurrences: the registered one for this treatment, under every ration (registered for FLOOR0 only)
            for p, (tr, off, f) in RECS.items():
                if law.treatment != tr:
                    continue
                res = {'C2-a': check_recurrence(N, off, f, Ra), 'C2-b': check_recurrence(N, off, f, Rb)}
                out['recurrences_all_rations'][key] = {'prediction': p, **res}
                if law.ration == 'FLOOR0':
                    out[p][sname] = res
                    if p == 'P1':
                        out['P1'][sname]['returns'] = {k: {kk: v[kk] for kk in (
                            'n_two_knot_parts', 'n_checkable_s_le_R_minus_2', 'n_unreturned_checkable',
                            'n_p1_pattern_failures', 'p1_pattern_ok', 'p1_pattern_failures')}
                            for k, v in tk.items()}
            log(key, 'rounds', Ra, '(under cap %d)' % Rb, 'knots', run.S.n_knots, 'kind', rec['kind'],
                'N', N, 'returns %.1fs' % t_ret)
    out['resources'] = resources()
    write('run1.json', out)


if __name__ == '__main__':
    main()
