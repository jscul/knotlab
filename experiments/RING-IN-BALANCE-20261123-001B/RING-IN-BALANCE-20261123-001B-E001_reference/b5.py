"""Run B5: the seven-knot generator under the ordinary law, R = 9, cut off past 20,000 knots.  For every knot made in
rounds 1 to R: f >= (t + 9)/5 (the record's bound, deviations.md B9), and the table of rounds by (p, f).  Evidence for
P7 and G (ordinary-law checks).  Writes b5.json."""
from b4 import pf_table
from bref import E, log, ordinary_checks, resources, write

R = 9
CAP = 20000


def main():
    S0 = E.generator7()
    run = E.Run(S0, E.ORDINARY, R, knot_cap=CAP)
    S = run.S
    fails = []
    by_round = {}
    for x in range(S.n_knots):
        t = S.made[x]
        if t < 1:
            continue
        f = len(S.fresh[x])
        b = by_round.setdefault(t, {'knots': 0, 'min_f': f, 'bound': (t + 9) / 5})
        b['knots'] += 1
        b['min_f'] = min(b['min_f'], f)
        if 5 * f < t + 9:
            fails.append({'id': x, 'round': t, 'p': len(S.parents[x]), 'f': f, 'bound': (t + 9) / 5})
    for b in by_round.values():
        b['ok'] = b['min_f'] >= b['bound']
    out = {'rounds_done': run.rounds_done, 'cut_off': run.cut_off, 'knots': S.n_knots, 'kind': run.kind(),
           'births': [r['n_births'] for r in run.records], 'fresh': [r['fresh_total'] for r in run.records],
           'bound_by_round': {str(k): v for k, v in sorted(by_round.items())},
           'n_fail': len(fails), 'fails_first': fails[:20],
           'fails_by_round': {str(t): sum(1 for x in fails if x['round'] == t) for t in sorted({x['round'] for x in fails})},
           'P7_ok': not fails, 'pf_table': pf_table(run, run.rounds_done), 'ordinary': ordinary_checks(run),
           'start_parity_pass': E.parity_knot_test(S0)['all_pass']}
    out['resources'] = resources()
    log('generator', out['kind'], 'rounds', out['rounds_done'], 'knots', out['knots'], 'P7', out['P7_ok'],
        'fails', out['n_fail'], out['fails_by_round'])
    write('b5.json', out)


if __name__ == '__main__':
    main()
