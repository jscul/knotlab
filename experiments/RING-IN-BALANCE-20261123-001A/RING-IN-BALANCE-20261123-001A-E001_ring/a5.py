"""Run A5: Ring(n, a), n = 5, 7, a = 2, 4, 5, under the two added rules (12 rounds) and the three added rules (20
rounds), cut off past 6,000 knots.  Evidence for P9 (a = 2); a = 4, 5 reported.  Writes a5.json."""
from common import E, log, resources, write

CAP = 6000


def p9(run, n):
    r1 = run.rosters[1]
    rows = []
    for t in range(1, run.rounds_done + 1):
        ros = run.rosters[t]
        rows.append({'t': t, 'same_as_round_1': run.cache.same(r1, None, ros, None), 'members': len(ros.members),
                     'parts': len(ros.parts), 'h': sorted(set(ros.h[u] for u in ros.members)),
                     'k': sorted(set(ros.k[u] for u in ros.members))})
    shape_ok = len(r1.members) == n and len(r1.parts) == 1 and all(r1.h[u] == 2 and r1.k[u] == 0 for u in r1.members)
    return {'shape_after_round_1_ok': shape_ok, 'all_same_as_round_1': all(r['same_as_round_1'] for r in rows),
            'ok': shape_ok and all(r['same_as_round_1'] for r in rows), 'bad_rows': [r for r in rows
                                                                                   if not r['same_as_round_1']][:5]}


def main():
    out = {'runs': {}, 'P9': {}}
    for lname, law, R in (('two', E.TWO_ADDED, 12), ('three', E.THREE_ADDED, 20)):
        for n in (5, 7):
            for a in (2, 4, 5):
                run = E.Run(E.ring(n, a), law, R, knot_cap=CAP)
                key = 'Ring(%d,%d)|%s' % (n, a, lname)
                rets = run.find_returns()
                out['runs'][key] = {'summary': run.summary(), 'balance': run.balance_summary(4),
                                    'returns': [{k: r[k] for k in ('s', 't', 'period', 'part_size', 'n_off',
                                                                   'off_sizes')} for r in rets[:20]],
                                    'n_returns': len(rets),
                                    'trace': [{k: row[k] for k in ('round', 'members', 'parts', 'births', 'h', 'k')
                                               if k in row} for row in run.trace()]}
                if a == 2:
                    out['P9'][key] = p9(run, n)
                log(key, run.summary()['kind'], 'rounds', run.rounds_done, 'knots', run.S.n_knots,
                    'cut' if run.cut_off else '', out['P9'][key]['ok'] if a == 2 else '')
    out['resources'] = resources()
    write('a5.json', out)


if __name__ == '__main__':
    main()
