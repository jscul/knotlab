"""Run 4: the two small starts, 16 rounds, cut off past 20,000 knots, under
  (a) the rations ORD, CAP-2, CAP-3, RATION-2 and RATION-3 with the three treatments;
  (b) each of the nine laws with NO-OFFSHOOT (the three with CANCEL-OFFSHOOT under reading C8-b only);
  (c) each of the nine laws with FILLERS;
  (d) each of the nine laws with HOLD.
For each run: its kind, whether a part copies itself (which: members, h, period), N(t).  P7 (a, b), P8 (RATION-3),
P9 (HOLD with FLOOR0, recurrences from round 8 on), P10 (FILLERS).  deviations.md C7-C11.  Writes run4.json."""
import time

from cpcommon import (E, N_series, RATIONS3, SMALL_STARTS, TREATMENTS3, copy_returns, copying_summary, is_two_knot_part,
                      law_literal, log, part_detail, resources, write)

R = 16
CAP = 20000
P9_RECS = {'CANCEL-RETIRE': ('N(n) = 2 N(n-3) + 2 N(n-4)', lambda N, n: 2 * N[n - 3] + 2 * N[n - 4]),
           'CANCEL-OFFSHOOT': ('N(n) = 3 N(n-3) + 2 N(n-4)', lambda N, n: 3 * N[n - 3] + 2 * N[n - 4]),
           'CANCEL-WAIT': ('N(n) = 2 N(n-3)', lambda N, n: 2 * N[n - 3])}


def law_list():
    out = []
    for r in ('ORD', 'CAP-2', 'CAP-3', 'RATION-2', 'RATION-3'):
        for t in TREATMENTS3:
            out.append(('a', E.Law(r, t), 'engine'))
    for r in RATIONS3:
        for t in TREATMENTS3:
            out.append(('b', law_literal(r, t, no_offshoot=True),
                        'C8-b (constructor bypassed)' if t == 'CANCEL-OFFSHOOT' else 'engine'))
    for r in RATIONS3:
        for t in TREATMENTS3:
            out.append(('c', E.Law(r, t, fillers=True), 'engine'))
    for r in RATIONS3:
        for t in TREATMENTS3:
            out.append(('d', E.Law(r, t, release='HOLD'), 'engine'))
    return out


def p8_check(run, crs):
    found = []
    five_copies = []
    for r in crs:
        if len(r['part']) != 5:
            continue
        ros = run.rosters[r['s']]
        P = r['part']
        ms = [M for M in ros.maxsets if next(iter(M)) in set(P)]
        sizes = sorted(len(M) for M in ms)
        hs = sorted(ros.h[u] for u in P)
        five_copies.append({'s': r['s'], 't': r['t'], 'period': r['period'], 'h': hs, 'metset_sizes': sizes})
        three = [M for M in ms if len(M) == 3]
        hub = [u for u in P if sum(1 for M in three if u in M) >= 2]
        if r['period'] == 1 and hs == [3] * 5 and hub:
            d = part_detail(run, r['s'], P)
            d.update({'t': r['t'], 'hub_member': hub, 'k': sorted(ros.k[u] for u in P),
                      'exactly_two_sets_of_three_sharing_one': (sizes == [3, 3] and
                                                                len(set(three[0]) & set(three[1])) == 1),
                      'n_off': r['n_off'], 'n_same_off': len(r['same_off']),
                      'copy_detail': part_detail(run, r['t'], r['off_parts'][r['same_off'][0]]),
                      'returned_as_detail': part_detail(run, r['t'], r['same_part'])})
            found.append(d)
    return {'ok': bool(found), 'n_found': len(found), 'first': found[0] if found else None,
            'first_s': found[0]['round'] if found else None,
            'five_member_copies': five_copies[:10], 'n_five_member_copies': len(five_copies)}


def p9_check(run, N, crs):
    two_copy = [r for r in crs if is_two_knot_part(run.rosters[r['s']], run.rosters[r['s']].parts.index(tuple(r['part'])))]
    name, f = P9_RECS[run.law.treatment]
    Ra = run.rounds_done
    rows = []
    for n in range(8, Ra + 1):
        rows.append({'n': n, 'N(n)': N[n], 'expected': f(N, n), 'ok': N[n] == f(N, n)})
    # the earliest n0 >= 4 from which the recurrence holds through the last round
    n0 = None
    for m in range(4, Ra + 1):
        if all(N[n] == f(N, n) for n in range(m, Ra + 1)):
            n0 = m
            break
    return {'recurrence': name, 'rows': rows, 'ok': bool(rows) and all(x['ok'] for x in rows),
            'failures': [x for x in rows if not x['ok']], 'holds_from_n': n0,
            'two_knot_part_copies_itself': bool(two_copy), 'n_two_knot_copies': len(two_copy),
            'two_knot_copy_periods': sorted({r['period'] for r in two_copy}),
            'first_two_knot_copy': ({'s': two_copy[0]['s'], 't': two_copy[0]['t'], 'part': two_copy[0]['part'],
                                     'n_off': two_copy[0]['n_off']} if two_copy else None)}


def main():
    out = {'R': R, 'cap': CAP, 'runs': {}}
    for sname, mk in SMALL_STARTS:
        for grp, law, how in law_list():
            t0 = time.time()
            run = E.Run(mk(), law, R, knot_cap=CAP)
            N = N_series(run)
            crs = copy_returns(run)
            key = '%s|%s' % (sname, law.name())
            members = [len(r.members) for r in run.rosters]
            v = {'start': sname, 'group': grp, 'law': law.to_dict(), 'law_built_by': how,
                 'rounds_done': run.rounds_done, 'cut_off': run.cut_off,
                 'knots': [mk().n_knots] + [rec['n_knots'] for rec in run.records], 'members': members,
                 'parts': [len(r.parts) for r in run.rosters], 'N': N, 'kind': run.kind(),
                 'first_event': run.first_event(), 'n_returns': len(run.find_returns()),
                 'mixed_parts': len(getattr(run, 'mixed_parts', [])), 'copying': copying_summary(run, crs),
                 'stopped_round': next((rec['round'] for rec in run.records if rec['stopped']), None)}
            if law.ration == 'RATION-3' and grp == 'a':
                v['P8'] = p8_check(run, crs)
            if grp == 'd' and law.ration == 'FLOOR0':
                v['P9'] = p9_check(run, N, crs)
            if grp == 'c':
                v['P10'] = {'members_after_round_4_onwards': members[4:], 'ok': all(m == 0 for m in members[4:])}
            v['seconds'] = round(time.time() - t0, 1)
            out['runs'][key] = v
            log(key, '[%s]' % grp, 'rounds', run.rounds_done, 'knots', run.S.n_knots, 'kind', v['kind'], 'copies',
                v['copying']['copies'], [(k['shape']['n'], k['shape']['h'], k['period']) for k in
                                         v['copying']['kinds']][:4], 'N', N, '%.1fs' % v['seconds'])
    rr = out['runs']
    p7a = {k: v['copying']['copies'] for k, v in rr.items()
           if v['group'] == 'a' and v['law']['ration'] in ('ORD', 'CAP-2', 'CAP-3', 'RATION-2')}
    p7b_engine = {k: v['copying']['copies'] for k, v in rr.items() if v['group'] == 'b' and v['law_built_by'] == 'engine'}
    p7b_literal = {k: v['copying']['copies'] for k, v in rr.items() if v['group'] == 'b'}
    out['P7'] = {'rations_copying': [k for k, c in p7a.items() if c],
                 'no_offshoot_copying_C8a': [k for k, c in p7b_engine.items() if c],
                 'no_offshoot_copying_C8b': [k for k, c in p7b_literal.items() if c],
                 'n_runs_C8a': len(p7a) + len(p7b_engine), 'n_runs_C8b': len(p7a) + len(p7b_literal)}
    out['P7']['pass_C8a'] = not out['P7']['rations_copying'] and not out['P7']['no_offshoot_copying_C8a']
    out['P7']['pass_C8b'] = not out['P7']['rations_copying'] and not out['P7']['no_offshoot_copying_C8b']
    out['P8'] = {k: v['P8']['ok'] for k, v in rr.items() if 'P8' in v}
    out['P8_pass'] = len(out['P8']) == 6 and all(out['P8'].values())
    out['P9'] = {k: {'copies': v['P9']['two_knot_part_copies_itself'], 'recurrence_ok': v['P9']['ok'],
                     'holds_from_n': v['P9']['holds_from_n'], 'failures': v['P9']['failures']}
                 for k, v in rr.items() if 'P9' in v}
    out['P9_pass'] = len(out['P9']) == 6 and all(x['copies'] and x['recurrence_ok'] for x in out['P9'].values())
    out['P10'] = {k: {'ok': v['P10']['ok'], 'stopped_round': v['stopped_round']} for k, v in rr.items() if 'P10' in v}
    out['P10_pass'] = len(out['P10']) == 18 and all(x['ok'] for x in out['P10'].values())
    out['resources'] = resources()
    log('P7', out['P7'])
    log('P8', out['P8'], out['P8_pass'])
    log('P9', out['P9'], out['P9_pass'])
    log('P10', out['P10_pass'])
    write('run4.json', out)


if __name__ == '__main__':
    main()
