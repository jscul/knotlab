"""Part 6: the classification of the 1,200 construction orders (PR part 6; TD 8.1; R 29-30)."""
from __future__ import annotations

import sys
import time
from collections import Counter
from fractions import Fraction as Fr
from multiprocessing import Pool

import orders
import tc


def main():
    T0 = time.time()
    tc.cap_memory()
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    jobs = []
    for lst in ('eleven_registered_400', 'eleven_new_400', 'smallest_gain_400'):
        for i, o in enumerate(orders.ORD[lst]['orders']):
            jobs.append((lst, i, o))
    with Pool(nproc) as pool:
        rows = list(pool.imap(orders.evaluate_order, jobs, chunksize=10))
    summ = {}
    for lst in ('eleven_registered_400', 'eleven_new_400', 'smallest_gain_400'):
        rs = [r for r in rows if r['list'] == lst]
        inc = [r for r in rs if r['in class']]
        out = [r for r in rs if not r['in class']]
        above_h = [r for r in out if Fr(r['score_all']) > 2 and r['hidden']]
        above_nh = [r for r in out if Fr(r['score_all']) > 2 and not r['hidden']]
        at2_h = [r for r in out if Fr(r['score_all']) == 2 and r['hidden']]
        rest = [r for r in out if r not in above_h and r not in above_nh and r not in at2_h]
        summ[lst] = {
            'orders': len(rs), 'in the class': len(inc),
            'in the class: at 2 and hidden': sum(1 for r in inc if r['verdict'].startswith('in the class, at 2')),
            'in the class: not (C5 fails)': [r['index'] for r in inc if not r['verdict'].startswith('in the class, at 2')],
            'in the class: losing weight at some knot': sum(1 for r in inc if r['any weight lost']),
            'in the class: losing weight equally across the setting pairs': sum(
                1 for r in inc if r['weight lost equally across the setting pairs']),
            'outside: at 2, hidden': len(at2_h), 'outside: above 2, hidden': len(above_h),
            'outside: above 2, not hidden': len(above_nh), 'outside: other': [(r['index'], r['score_all'], r['hidden'])
                                                                              for r in rest],
            'outside: largest score': max((Fr(r['score_all']) for r in out), default=None),
            'outside: largest score, at orders': [r['index'] for r in out if out and Fr(r['score_all']) == max(
                Fr(x['score_all']) for x in out)],
            'outside: score values': {str(k): v for k, v in Counter((r['score_all'], r['hidden']) for r in out).most_common()},
            'in the class: score values': {str(k): v for k, v in Counter((r['score_all'], r['hidden']) for r in inc).most_common()},
        }
    p4 = all(r['verdict'].startswith('in the class, at 2') for r in rows if r['in class'])
    res = {'part': 6, 'summary': summ, 'P4 holds': p4,
           'P4 holds on the registered 400': all(r['verdict'].startswith('in the class, at 2') for r in rows
                                                 if r['in class'] and r['list'] == 'eleven_registered_400'),
           'rows': rows, 'wall_s': round(time.time() - T0, 1), 'processes': nproc}
    tc.dump('part6_orders.json', res)
    for k, v in summ.items():
        print(k, {kk: (tc.fstr(vv) if isinstance(vv, Fr) else vv) for kk, vv in v.items() if kk not in ('outside: score values',)})
    print('P4', p4, 'wall', res['wall_s'])


if __name__ == '__main__':
    main()
