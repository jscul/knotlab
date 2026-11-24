"""Run B1: D2(n, 3) and DW(n, 3), n = 3 to 12, and Ring(n, 3), n = 3 to 16, under the ordinary law, the two added rules
and the three added rules, R = 12, cut off past 6,000 knots; the parity knot test (both methods) and the not-all-equal
knot test on every start.  Evidence for G (knot test of the starts, D2 = DW, ordinary-law checks), P1, and B3/P3
(every return giving parts off, with which members waited).  Writes b1.json."""
from bref import E, LAWS3, has_waiting, log, ordinary_checks, resources, run_record, write

R = 12
CAP = 6000


def chain(run, s0, Y0, n_expected):
    """The chain of least returns from part Y0 after round s0, two rounds at a time (deviations.md B3)."""
    rets = {(r['s'], tuple(r['part'])): r for r in run.find_returns()}
    cur, s, steps = tuple(sorted(Y0)), s0, []
    while s + 2 <= run.rounds_done:
        r = rets.get((s, cur))
        if r is None or r['t'] != s + 2:
            steps.append({'s': s, 'returns_at_s_plus_2': False,
                          'least_t': (r['t'] if r is not None else None)})
            break
        steps.append({'s': s, 't': r['t'], 'n_off': r['n_off'], 'off_sizes': r['off_sizes'],
                      'returns_at_s_plus_2': True, 'part_size': r['part_size']})
        cur, s = tuple(r['same_part']), r['t']
    good = [x for x in steps if x['returns_at_s_plus_2']]
    want_steps = (run.rounds_done - s0) // 2
    full = len(good) == want_steps and all(x['n_off'] == n_expected for x in good)
    return {'s0': s0, 'steps': steps, 'n_steps': len(good), 'steps_wanted': want_steps,
            'n_offs': sorted({x['n_off'] for x in good}), 'full_chain_n_off': full}


def same_labelled(r1, r2):
    """Exact sufficient test of sameness: the identity renaming carries h, k and the inclusion-maximal met sets of one
    roster onto the other (D2 and DW number their knots alike, so their births get the same numbers)."""
    return (r1.members == r2.members and all(r1.h[u] == r2.h[u] and r1.k[u] == r2.k[u] for u in r1.members)
            and sorted(sorted(M) for M in r1.maxsets) == sorted(sorted(M) for M in r2.maxsets))


def trace(run):
    return [[t, len(ros.members), len(ros.parts)] for t, ros in enumerate(run.rosters)]


def main():
    starts = []
    for n in range(3, 13):
        starts.append(('D2', n, E.d2(n, 3)))
        starts.append(('DW', n, E.dw(n, 3)))
    for n in range(3, 17):
        starts.append(('Ring', n, E.ring(n, 3)))
    out = {'knot_tests': {}, 'runs': {}, 'P1': {}, 'same_D2_DW': {}, 'ordinary': {}}
    runs = {}
    for fam, n, S in starts:
        name = '%s(%d,3)' % (fam, n)
        par = E.parity_knot_test(S)
        nae = E.nae_knot_test(S)
        out['knot_tests'][name] = {'parity_all_pass': par['all_pass'], 'rank_fail': par['rank_fail'],
                                   'cut_fail': par['cut_fail'], 'disagree': par['disagree'],
                                   'nae_all_pass': nae['all_pass'], 'nae_fail': nae['fail'],
                                   'nae_sat_calls': nae['sat_calls'], 'n_knots': S.n_knots}
        for lname, law in LAWS3:
            run = E.Run(S, law, R, knot_cap=CAP)
            key = '%s|%s' % (name, lname)
            rec = run_record(run, keep_all_off=True)
            rec.update({'start': name, 'family': fam, 'n': n, 'law': lname, 'law_name': law.name(),
                        'waiting_law': has_waiting(law), 'trace': trace(run)})
            if lname == 'ordinary':
                oc = ordinary_checks(run)
                c, at = run.max_descendant_parts()
                oc['max_parts_from_one_part'] = c
                oc['ok_strong'] = oc['ok'] and c <= 1
                out['ordinary'][key] = oc
            if fam in ('D2', 'DW'):
                ros0 = run.rosters[0]
                p1 = {'start_parts': len(ros0.parts), 'start_past_start': ros0.past_start}
                if len(ros0.parts) == 1:
                    p1['even_chain'] = chain(run, 0, ros0.parts[0], n)
                if run.rounds_done >= 1 and len(run.rosters[1].parts) == 1:
                    p1['odd_chain'] = chain(run, 1, run.rosters[1].parts[0], n)
                out['P1'][key] = p1
            out['runs'][key] = rec
            if fam in ('D2', 'DW'):
                runs[(fam, n, lname)] = run
            log(key, rec['kind'], 'rounds', rec['rounds_done'], 'knots', rec['knots'],
                'off-returns', rec['n_off_returns'], 'cut' if rec['cut_off'] else '')
        if fam == 'DW':
            for lname, _ in LAWS3:
                a, b = runs[('D2', n, lname)], runs[('DW', n, lname)]
                rows = []
                for t in range(max(a.rounds_done, b.rounds_done) + 1):
                    if t > a.rounds_done or t > b.rounds_done:
                        rows.append([t, None])
                        continue
                    if same_labelled(a.rosters[t], b.rosters[t]):
                        rows.append([t, True, 'labelled identity'])
                    else:
                        rows.append([t, E.same_rosters(a.rosters[t], b.rosters[t]), 'VF2'])
                out['same_D2_DW']['%d|%s' % (n, lname)] = {
                    'rounds': [a.rounds_done, b.rounds_done], 'knots': [a.S.n_knots, b.S.n_knots],
                    'all_same': all(x[1] is True for x in rows), 'rows': rows}
                del runs[('D2', n, lname)], runs[('DW', n, lname)]
    out['resources'] = resources()
    write('b1.json', out)


if __name__ == '__main__':
    main()
