"""Part 4: the named starts (P3-P7, P12, P13).  14 starts x 11 bases x (base + 3 forms) x 2 knot laws, 8 rounds or
3,000 knots.  Writes part4.json.

python -B part4.py
"""
from __future__ import annotations

import time

from dh_common import STARTS_JSON, write, log, n_procs, load_avg
import dh_engine as E
import dh_analysis as A

NAMED = list(STARTS_JSON['starts'].keys())
STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}


def parents_by_round(S, recs):
    return [[list(S.parents[x]) for x in r['new']] for r in recs]


def job(args):
    start, ln, kl = args
    L = E.LAW[ln]
    out = {'start': start, 'law': ln, 'knot_law': kl, 'forms': {}}
    Sb, rb, eb = E.grow(STARS[start], L, None, kl, R=8, N=3000)
    base_row = A.analyze_base(Sb, rb, eb)
    base_row['place_rule_last_by_kind (places count, nothing written)'] = base_row.pop('places_count_rule_by_kind')
    out['forms']['base'] = base_row
    pb = parents_by_round(Sb, rb)
    closing_round = next((r['round'] for r in rb if r['closing']), None)
    base_last = len(rb)
    for form in E.FORMS:
        S, recs, end = E.grow(STARS[start], L, form, kl, R=8, N=3000)
        row = A.analyze_armw(S, recs, end, form, kl, L, keep_wrong=10)
        pf = parents_by_round(S, recs)
        both = min(len(pb), len(pf))
        row['same_births (DH 6.2)'] = pb[:both] == pf[:both]
        row['same_rounds_and_end'] = (len(pb) == len(pf) and eb == end)
        if form in ('PB', 'BB'):
            through = closing_round if (kl == 'parity' and closing_round is not None) else base_last
            same = pb[:through] == pf[:through] and len(pf) >= through
            row['P7'] = same
            row['P7_through_round'] = through
            row['base_closes_at'] = closing_round
            row['goes_on_after_base_closes'] = (closing_round is not None and
                                                any(r['births'] for r in recs[closing_round:]))
        else:
            row['P12_against_base'] = {'births_base': [r['births'] for r in rb], 'births': row['births'],
                                       'knots_base': len(Sb.places), 'knots': len(S.places),
                                       'end_base': eb, 'end': end}
        row['cost'] = {'share_s_positive': (row['s_positive'] / row['new_knots']) if row['new_knots'] else None,
                       'mean_s': (row['s_sum'] / row['new_knots']) if row['new_knots'] else None}
        out['forms'][form] = row
    return out


def main():
    import multiprocessing as mp
    procs = n_procs()
    log('part 4, load %.1f, %d processes' % (load_avg(), procs))
    t0 = time.time()
    jobs = [(s, L.name, kl) for s in NAMED for L in E.BASES for kl in ('parity', 'nae')]
    with mp.Pool(procs) as pool:
        res = pool.map(job, jobs, chunksize=1)
    out = {'part': 4, 'load_at_start': load_avg(), 'processes': procs, 'runs': res, 'n_runs': 4 * len(res),
           'seconds': round(time.time() - t0, 1)}
    write('part4.json', out)
    log('part 4 written', out['seconds'])


if __name__ == '__main__':
    main()
