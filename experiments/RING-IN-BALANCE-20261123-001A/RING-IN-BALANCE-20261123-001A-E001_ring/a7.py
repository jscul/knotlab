"""Run A7: Ring(5, 3) and Ring(7, 3) under (CAP-k, CANCEL-WAIT), k = 3..7, through 2k + 8 rounds, cut off past
20,000 knots.  Evidence for P11: some part of n members with k usable loose distinctions each returns every two
rounds giving parts off.  Writes a7.json."""
from common import E, log, resources, write

CAP = 20000


def p11(run, n, k):
    R = run.rounds_done
    rets = {(r['s'], tuple(r['part'])): r for r in run.find_returns()}
    found = []
    for s in range(0, R - 1):
        ros = run.rosters[s]
        for P in ros.parts:
            if len(P) != n or any(ros.h[u] != k for u in P):
                continue
            r = rets.get((s, P))
            if r is None or r['t'] != s + 2 or r['n_off'] == 0:
                continue
            # follow the chain every two rounds
            chain = [{'s': s, 't': r['t'], 'n_off': r['n_off'], 'off_sizes': r['off_sizes']}]
            cur, t = tuple(r['same_part']), r['t']
            while t + 2 <= R:
                r2 = rets.get((t, cur))
                if r2 is None or r2['t'] != t + 2 or r2['n_off'] == 0:
                    break
                chain.append({'s': t, 't': r2['t'], 'n_off': r2['n_off'], 'off_sizes': r2['off_sizes']})
                cur, t = tuple(r2['same_part']), r2['t']
            to_end = t + 2 > R
            found.append({'s': s, 'chain_length': len(chain), 'chain_to_end_of_run': to_end,
                          'chain': chain[:3], 'part_k': sorted(set(ros.k[u] for u in P))})
        if found:
            break
    best = found[0] if found else None
    return {'found': bool(found), 'first': best,
            'ok': bool(found) and any(f['chain_to_end_of_run'] for f in found)}


def main():
    out = {'runs': {}, 'P11': {}}
    for n in (5, 7):
        for k in range(3, 8):
            law = E.Law('CAP-%d' % k, 'CANCEL-WAIT')
            R = 2 * k + 8
            run = E.Run(E.ring(n, 3), law, R, knot_cap=CAP)
            key = 'Ring(%d,3)|CAP-%d' % (n, k)
            rets = run.find_returns()
            out['runs'][key] = {'summary': run.summary(), 'R': R, 'n_returns': len(rets),
                                'returns': [{kk: r[kk] for kk in ('s', 't', 'period', 'part_size', 'n_off',
                                                                  'off_sizes')} for r in rets[:20]],
                                'trace': [{kk: row[kk] for kk in ('round', 'members', 'parts', 'births', 'n_knots')
                                           if kk in row} for row in run.trace()]}
            out['P11'][key] = p11(run, n, k)
            log(key, run.summary()['kind'], 'rounds', run.rounds_done, '/', R, 'knots', run.S.n_knots,
                'cut' if run.cut_off else '', 'P11', out['P11'][key]['ok'], out['P11'][key]['first'])
    out['resources'] = resources()
    write('a7.json', out)


if __name__ == '__main__':
    main()
