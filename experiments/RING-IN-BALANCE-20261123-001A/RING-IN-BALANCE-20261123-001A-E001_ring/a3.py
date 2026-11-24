"""Run A3: Ring(5, 3) and Ring(7, 3) under the two and the three added rules with the not-all-equal knot law: births
compared with the same laws under parity at every round through 12; the not-all-equal knot test (SAT, every
assignment of every knot's places) at rounds 0 to 6.  Evidence for P7.  Writes a3.json."""
import time

from common import E, log, resources, write

R_BIRTHS = 12
R_TEST = 6


def comparable(rec):
    return {'groups': rec['groups'], 'short': rec['short'], 'cancelled': rec['cancelled'],
            'waiting': rec['waiting'], 'closing': rec['closing'],
            'births': [(b['id'], tuple(b['parents']), tuple(b['taken']), b['kind'], b['D'], b['f'], b['usable'],
                        b['barred']) for b in rec['births']]}


def main():
    out = {'runs': {}}
    for lname, law in (('two', E.TWO_ADDED), ('three', E.THREE_ADDED)):
        for n in (5, 7):
            nae_rows = []
            tsec = [0.0]

            def hook(S, r, rec, before):
                if r <= R_TEST:
                    t0 = time.time()
                    res = E.nae_knot_test(S)
                    tsec[0] += time.time() - t0
                    nae_rows.append({'round': r, 'n_knots': S.n_knots, 'n_fail': len(res['fail']),
                                     'fail': res['fail'][:20], 'sat_calls': res['sat_calls']})
            nae_law = law.replace(knot_law='nae')
            rn = E.Run(E.ring(n, 3), nae_law, R_BIRTHS, hook=hook)
            rp = E.Run(E.ring(n, 3), law, R_BIRTHS)
            per_round = []
            for a, b in zip(rn.records, rp.records):
                per_round.append({'round': a['round'], 'births_nae': a['n_births'], 'births_parity': b['n_births'],
                                  'equal': comparable(a) == comparable(b), 'closing_nae': a['closing'],
                                  'closing_parity': b['closing']})
            key = 'Ring(%d,3)|%s' % (n, lname)
            same_rosters = all(rn.cache.same(x, None, y, None) for x, y in zip(rn.rosters, rp.rosters))
            out['runs'][key] = {
                'summary_nae': rn.summary(), 'summary_parity': rp.summary(), 'per_round': per_round,
                'births_equal_every_round': all(x['equal'] for x in per_round) and len(rn.records) == len(rp.records),
                'rosters_same_every_round': same_rosters,
                'closing_ever': any(x['closing_nae'] or x['closing_parity'] for x in per_round),
                'nae_test': nae_rows, 'nae_all_pass': all(x['n_fail'] == 0 for x in nae_rows),
                'nae_knots_checked': sum(x['n_knots'] for x in nae_rows),
                'sat_calls': sum(x['sat_calls'] for x in nae_rows), 'nae_seconds': round(tsec[0], 1)}
            v = out['runs'][key]
            log(key, 'births equal', v['births_equal_every_round'], 'closing', v['closing_ever'], 'NAE pass',
                v['nae_all_pass'], 'knots checked', v['nae_knots_checked'], 'SAT calls', v['sat_calls'])
    out['resources'] = resources()
    write('a3.json', out)


if __name__ == '__main__':
    main()
