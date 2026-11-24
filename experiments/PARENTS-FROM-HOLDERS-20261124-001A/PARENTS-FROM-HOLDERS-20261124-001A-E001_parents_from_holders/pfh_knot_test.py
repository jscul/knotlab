"""The knot test of P2 (pre-registration, "Populations"): every knot of each final P2 structure under parity by both
methods of the reference engine (ranks and cut), and under not-all-equal where the structure has at most 600 knots.

    python -B pfh_knot_test.py          # writes artifacts/.../knot_tests.json

The reference engine's own functions are used unchanged: parity_knot_test (both methods, with their agreement) and
nae_knot_test (a SAT solver for each of the 2^|S| assignments of each knot).
"""
from __future__ import annotations

import json
import resource
import time

import pfh_common as PC
import pfh_pop as PP

E = PC.E


def main():
    lim = 8 << 30
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    PC.check_frozen()
    t0 = time.time()
    rows = []
    for start, fam, rc in PC.gate_pairs():
        S0, rounds, events = PP.p2_lineage(start, fam, rc)
        S = rounds[-1]
        t1 = time.time()
        par = E.parity_knot_test(S)
        row = {'start': start, 'law': PC.LAW_NAMES[fam], 'round': S.round, 'knots': S.n_knots,
               'parity': {'all_pass': par['all_pass'], 'rank_fail': len(par['rank_fail']),
                          'cut_fail': len(par['cut_fail']), 'methods_disagree': len(par['disagree']),
                          'rank_H': par['rank_H'],
                          'rank_fail_knots': par['rank_fail'][:50], 'cut_fail_knots': par['cut_fail'][:50]},
               'parity_seconds': round(time.time() - t1, 2)}
        if S.n_knots <= 600:
            t2 = time.time()
            nae = E.nae_knot_test(S)
            row['nae'] = {'all_pass': nae['all_pass'], 'fail': len(nae['fail']), 'fail_knots': nae['fail'][:50],
                          'sat_calls': nae['sat_calls']}
            row['nae_seconds'] = round(time.time() - t2, 2)
        else:
            row['nae'] = 'not run: more than 600 knots (as registered)'
        rows.append(row)
        print(start, PC.LAW_SHORT[fam], 'round', S.round, 'knots', S.n_knots, 'parity all pass', par['all_pass'],
              'disagree', len(par['disagree']), 'nae', row['nae'] if isinstance(row['nae'], str) else row['nae']['all_pass'],
              flush=True)
    out = {'rows': rows, 'seconds': round(time.time() - t0, 1),
           'parity_all_pass_every_structure': all(r['parity']['all_pass'] for r in rows),
           'parity_methods_agree_every_knot': all(r['parity']['methods_disagree'] == 0 for r in rows),
           'nae_tested': sum(1 for r in rows if isinstance(r['nae'], dict)),
           'nae_all_pass_where_tested': all(r['nae']['all_pass'] for r in rows if isinstance(r['nae'], dict))}
    PC.write_json(PC.OUT / 'knot_tests.json', out)
    print('done', out['seconds'], 's')


if __name__ == '__main__':
    main()
