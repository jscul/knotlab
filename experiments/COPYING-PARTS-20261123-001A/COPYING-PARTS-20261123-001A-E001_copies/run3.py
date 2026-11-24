"""Run 3: Ring(5, 3) under the nine laws, 12 rounds: the parity knot test by both methods for every knot at rounds 0
to 12, the extension test for every round, the fresh count of every birth; every birth with no fresh distinction
(round, parents, demand) and every failing knot with the round it first fails (deviations.md C6).  Evidence for P6.
Writes run3.json."""
from collections import Counter

from cpcommon import E, log, nine_laws, resources, write

R = 12


class ParityHook:
    def __init__(self):
        self.rows = []
        self.fail_rounds = {}       # knot -> rounds at which it fails (either method)

    def __call__(self, S, r, rec, before):
        res = E.parity_knot_test(S)
        failing = sorted(set(res['rank_fail']) | set(res['cut_fail']))
        for u in failing:
            self.fail_rounds.setdefault(u, []).append(r)
        row = {'round': r, 'n_knots': S.n_knots, 'n_rank_fail': len(res['rank_fail']),
               'n_cut_fail': len(res['cut_fail']), 'n_disagree': len(res['disagree']), 'disagree': res['disagree'],
               'all_pass': res['all_pass'], 'failing': failing[:50]}
        if r >= 1:
            ext = E.extension_test_parity(before, S)
            row['extends'] = ext['extends']
            row['ext_dims'] = [ext['dim_before'], ext['dim_restricted']]
            row['closing'] = rec['closing']
        self.rows.append(row)


def main():
    out = {'R': R, 'runs': {}}
    for law in nine_laws():
        key = 'Ring(5,3)|%s' % law.name()
        ph = ParityHook()
        run = E.Run(E.ring(5, 3), law, R, hook=ph, hook_needs_before=True)
        S = run.S
        zero = [{'round': rec['round'], 'id': b['id'], 'kind': b['kind'], 'parents': b['parents'], 'D': b['D']}
                for rec in run.records for b in rec['births'] if b['f'] == 0]
        zero_rounds = sorted({z['round'] for z in zero})
        fresh_hist = {}
        for rec in run.records:
            c = Counter((len(b['parents']), b['D'], b['f']) for b in rec['births'])
            fresh_hist[rec['round']] = [[p, D, f, n] for (p, D, f), n in sorted(c.items())]
        failing = []
        for u, rs in sorted(ph.fail_rounds.items()):
            first = rs[0]
            failing.append({'id': u, 'made': S.made[u], 'kind': ('start' if not S.parents[u] else
                                                               ('join' if len(S.parents[u]) >= 2 else 'offshoot')),
                            'parents': list(S.parents[u]), 'fresh': len(S.fresh[u]), 'first_fail': first,
                            'fail_rounds': rs, 'fails_every_round_from_first': rs == list(range(first, R + 1)),
                            'zero_fresh_birth_in_first_fail_round': first in zero_rounds})
        round1_joins = [u for u in range(S.n_knots) if S.made[u] == 1 and len(S.parents[u]) >= 2]
        r1 = {}
        for u in round1_joins:
            rs = ph.fail_rounds.get(u, [])
            r1[u] = {'fail_rounds': rs, 'passes_rounds_1_to_3': not any(x <= 3 for x in rs),
                     'fails_every_round_4_to_12': all(x in rs for x in range(4, R + 1))}
        v = {'law': law.to_dict(), 'rounds_done': run.rounds_done, 'knots_by_round': [r['n_knots'] for r in ph.rows],
             'kind': run.kind(), 'rows': ph.rows,
             'all_knots_pass': all(r['all_pass'] for r in ph.rows),
             'methods_agree': all(r['n_disagree'] == 0 for r in ph.rows),
             'all_rounds_extend': all(r.get('extends', True) for r in ph.rows),
             'first_non_extending_round': next((r['round'] for r in ph.rows if r.get('extends') is False), None),
             'closing_rounds': [r['round'] for r in ph.rows if r.get('closing')],
             'zero_fresh_births': zero, 'n_zero_fresh_births': len(zero), 'zero_fresh_rounds': zero_rounds,
             'fresh_histogram_by_round_p_D_f_count': fresh_hist,
             'failing_knots': failing, 'n_failing_knots': len(failing),
             'first_failing_round': min((f['first_fail'] for f in failing), default=None),
             'every_failure_in_a_zero_fresh_round': all(f['zero_fresh_birth_in_first_fail_round'] for f in failing),
             'round1_joins': r1,
             'round1_joins_fail_from_4': bool(r1) and all(x['passes_rounds_1_to_3'] and x['fails_every_round_4_to_12']
                                                          for x in r1.values()),
             'failing_other_than_round1_joins': [f for f in failing if f['id'] not in r1]}
        out['runs'][key] = v
        log(key, 'knots', S.n_knots, 'all pass', v['all_knots_pass'], 'agree', v['methods_agree'], 'extend',
            v['all_rounds_extend'], 'f=0 births', len(zero), 'in rounds', zero_rounds, 'failing knots', len(failing),
            'first fail', v['first_failing_round'], 'failures in f=0 rounds', v['every_failure_in_a_zero_fresh_round'],
            'round-1 joins fail from 4', v['round1_joins_fail_from_4'])
    rr = out['runs']

    def g(r, t):
        return rr['Ring(5,3)|%s' % E.Law(r, t).name()]
    p6 = {}
    for r in ('FLOOR0', 'FLOOR1'):
        for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            p6['%s|%s all pass' % (r, t)] = g(r, t)['all_knots_pass'] and g(r, t)['methods_agree']
    for t in ('CANCEL-RETIRE', 'CANCEL-WAIT'):
        p6['ONE-FEWER|%s all pass' % t] = g('ONE-FEWER', t)['all_knots_pass'] and g('ONE-FEWER', t)['methods_agree']
    p6['ONE-FEWER|CANCEL-OFFSHOOT round-1 joins fail from round 4'] = g('ONE-FEWER', 'CANCEL-OFFSHOOT')[
        'round1_joins_fail_from_4']
    p6['every failing knot first fails in a round with a birth with f = 0 (nine laws)'] = all(
        v['every_failure_in_a_zero_fresh_round'] for v in rr.values())
    out['P6'] = p6
    out['P6_pass'] = all(p6.values())
    out['resources'] = resources()
    log('P6', p6, out['P6_pass'])
    write('run3.json', out)


if __name__ == '__main__':
    main()
