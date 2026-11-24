"""Run A6: Ring(n, 3), n = 5, 7, 9, under (CAP-3, CANCEL-WAIT with HOLD), 12 rounds.  Evidence for P10.
Writes a6.json."""
from common import E, log, resources, write

LAW = E.Law('CAP-3', 'CANCEL-WAIT', 'HOLD')
R = 12


def main():
    out = {'runs': {}}
    for n in (5, 7, 9):
        run = E.Run(E.ring(n, 3), LAW, R, knot_cap=6000)
        rets = run.find_returns()
        off = [r for r in rets if r['n_off'] > 0]
        waited2 = run.records[1]['waiting'] if run.rounds_done >= 2 else []
        later = []
        for rec in run.records[2:]:
            sh = set(rec['short'])
            later.append({'round': rec['round'], 'all_waited2_short': all(u in sh for u in waited2),
                          'n_short': len(rec['short']), 'births': rec['n_births'], 'jammed': rec['jammed'],
                          'held': len(rec['held'])})
        key = 'Ring(%d,3)' % n
        out['runs'][key] = {
            'summary': run.summary(), 'waited_in_round_2': waited2,
            'rounds_after_2': later,
            'waited2_short_every_later_round': bool(waited2) and all(x['all_waited2_short'] for x in later),
            'has_return_giving_parts_off': bool(off), 'n_returns': len(rets),
            'returns': [{k: r[k] for k in ('s', 't', 'period', 'part_size', 'n_off', 'off_sizes')} for r in rets[:12]],
            'trace': run.trace(),
            'records_round_1_2': [{k: rec[k] for k in ('round', 'short', 'waiting', 'held', 'n_joins', 'n_offshoots',
                                                       'jammed')} for rec in run.records[:3]]}
        v = out['runs'][key]
        v['ok'] = v['waited2_short_every_later_round'] and not v['has_return_giving_parts_off']
        log(key, run.summary()['kind'], 'waited2 short later', v['waited2_short_every_later_round'],
            'return with parts off', v['has_return_giving_parts_off'])
    out['resources'] = resources()
    write('a6.json', out)


if __name__ == '__main__':
    main()
