"""Collect the census, search and reduction results of THIRD-HOLDER-20261123-001B-E001, write every distinct structure with
a hidden excess as a list of knots, pick the smallest in each class by the frozen order (knots first, then extra holders),
and verify it by full enumeration of its four finished structures.

usage: report.py
"""
import json, os, time
import numpy as np
from fractions import Fraction
import common as c

t0 = time.time()
A = c.ART
def J(f): return json.load(open(f'{A}/{f}'))
def exists(f): return os.path.exists(f'{A}/{f}')

# ---- tables of what was searched -----------------------------------------------------------------------------------------
rows = []
def census_row(label, cls, cut, sides_tag, pair_file, kind):
    s = J(pair_file)
    meta = J(f'sides_{sides_tag}.json')
    nstruct = meta['stats'][-1]['structures'] if 'stats' in meta else meta.get('structures')
    r = dict(label=label, cls=cls, shared=cut, sides=sides_tag, labelled_structures=nstruct, side_tables=s.get('exact_tables', [None])[0],
             projective_tables=s.get('projective_tables', [None])[0], ordered_pairs=s.get('ordered_pairs') or s.get('ordered_pairs_projective'),
             kind=kind, file=pair_file)
    if pair_file.startswith('pairs_'):
        r.update(hidden_ordered_pairs=s.get('hidden_ordered_pairs', s.get('pairs_hidden')), pairs_scored=s.get('candidate_pairs', s.get('pairs_combined')),
                 unique_scored=s.get('unique_M'), excess_old_tables=s.get('n_hidden_gt2', 0), max_hidden=s.get('max_score_hidden_exact'),
                 reach2=s.get('n_hidden_reach2'))
    else:
        r.update(orbit_reps=s['orbit_reps'][0], pairs_scored=s['pairs'], hidden_among_scored=s['pairs_hidden'],
                 unique_hidden_scored=s['unique_hidden_M_sum_over_runs'], excess_old_tables=s['n_excess_old_tables'],
                 max_hidden=s['max_hidden_score_exact'], reach2=s['near2_distinct'])
    rows.append(r)
    return s

CENSUS = [('census, two holders (row G)', 'L', 1, 'L_c1_k3_i3_h2', 'pairs_L_c1_k3_i3_h2__L_c1_k3_i3_h2_full_summary.json', 'every ordered pair'),
          ('census, two holders (row G)', 'L', 2, 'L_c2_k3_i3_h2', 'pairs_L_c2_k3_i3_h2__L_c2_k3_i3_h2_full_summary.json', 'every ordered pair'),
          ('census <= 3 knots', 'L', 1, 'L_c1_k3_i3_h3', 'pairs_L_c1_k3_i3_h3__L_c1_k3_i3_h3_full_summary.json', 'every ordered pair'),
          ('census <= 3 knots', 'L', 2, 'L_c2_k3_i3_h3', 'pairs_L_c2_k3_i3_h3__L_c2_k3_i3_h3_full_summary.json', 'every ordered pair'),
          ('census <= 3 knots', 'S', 1, 'S_c1_k3_i3_h3', 'pairs_S_c1_k3_i3_h3__S_c1_k3_i3_h3_lemma_summary.json', 'reduction, hidden pairs counted'),
          ('census <= 3 knots', 'S', 2, 'S_c2_k3_i3_h3', 'pairs_S_c2_k3_i3_h3__S_c2_k3_i3_h3_lemma_summary.json', 'reduction, hidden pairs counted'),
          ('census <= 4 knots', 'L', 1, 'L_c1_k4_i5_h3', 'pairs_L_c1_k4_i5_h3__L_c1_k4_i5_h3_lemma_summary.json', 'reduction, hidden pairs counted'),
          ('census <= 4 knots', 'L', 2, 'L_c2_k4_i5_h3', 'pc_L_c2_k4_i5_h3__L_c2_k4_i5_h3_lemma_summary.json', 'reduction (rank 3)'),
          ('census <= 4 knots', 'S', 1, 'S_c1_k4_i5_h3', 'pairs_S_c1_k4_i5_h3__S_c1_k4_i5_h3_lemma_summary.json', 'reduction, hidden pairs counted'),
          ('census <= 4 knots', 'S', 2, 'S_c2_k4_i5_h3', 'pc_S_c2_k4_i5_h3__S_c2_k4_i5_h3_lemma_summary.json', 'reduction (rank 3)'),
          ('census <= 5 knots', 'L', 2, 'L_c2_k5_i5_h3', 'pc_L_c2_k5_i5_h3__L_c2_k5_i5_h3_lemma_summary.json', 'reduction (rank 3)'),
          ('seeded search, pool', 'L', 1, 'search_L_c1', 'pc_search_L_c1__search_L_c1_full_summary.json', 'every ordered pair'),
          ('seeded search, pool', 'L', 2, 'search_L_c2', 'pc_search_L_c2__search_L_c2_full_summary.json', 'every ordered pair'),
          ('seeded search, pool', 'S', 1, 'search_S_c1', 'pc_search_S_c1__search_S_c1_full_summary.json', 'every ordered pair'),
          ('seeded search, pool', 'S', 2, 'search_S_c2', 'pc_search_S_c2__search_S_c2_full_summary.json', 'every ordered pair'),
          ('extension: every distinct table of the draws', 'L', 2, 'search_L_c2_all', 'pc_search_L_c2_all__search_L_c2_all_lemma_summary.json', 'reduction (rank 3)'),
          ('extension: every distinct table of the draws', 'S', 2, 'search_S_c2_all', 'pc_search_S_c2_all__search_S_c2_all_lemma_summary.json', 'reduction (rank 3)')]

found = []          # every excess structure: (source, knots_A, knots_B, score, measures)
for label, cls, cut, stag, pf, kind in CENSUS:
    if not exists(pf):
        rows.append(dict(label=label, cls=cls, shared=cut, sides=stag, missing=pf)); continue
    s = census_row(label, cls, cut, stag, pf, kind)
    if pf.startswith('pc_'):
        d = np.load(f'{A}/sides_{stag}.npz')
        for e in s['excess']:
            if 'rep_A' not in e: continue
            kA = c.side_struct(d['structs'][e['rep_A']], d['knots'][e['rep_A']], cut, 'A')
            kB = c.side_struct(d['structs'][e['rep_B']], d['knots'][e['rep_B']], cut, 'B')
            found.append(dict(source=label, sides=stag, knots_A=c.fmt_knots(kA), knots_B=c.fmt_knots(kB), score=e['score'],
                              pairs_giving_it=e['pairs'], M=e['M'], measures=c.structure_measures(kA, kB)))

red = J('reduce_verified.json')
for start, r in red.items():
    for f in r['distinct_finals']:
        kA = c.parse_knots(f['knots_A']); kB = c.parse_knots(f['knots_B'])
        found.append(dict(source=f'reduction from {start} ({r["orders"]} orders)', sides=None, knots_A=f['knots_A'], knots_B=f['knots_B'],
                          score=f['full_enumeration']['score'], pairs_giving_it=None, M=None, measures=c.structure_measures(kA, kB)))

def size(f): return (f['measures']['knots'], f['measures']['extra_holders'])
out = dict(rows=rows, n_found=len(found))
for cls in ('L', 'S'):
    inc = [f for f in found if f['measures']['cls'] == 'L' or (cls == 'S' and f['measures']['cls'] == 'S')]
    if not inc:
        out[f'class_{cls}'] = dict(found=0); continue
    inc.sort(key=lambda f: (size(f), -float(Fraction(f['score']))))
    best = inc[0]
    kA = c.parse_knots(best['knots_A']); kB = c.parse_knots(best['knots_B'])
    fc = c.full_check(kA, kB)
    best_v = dict(best, full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']), change=str(fc['change']),
                                              agrees_with_side_tables=fc['agrees_with_side_tables'], finished_words=fc['words_finished'],
                                              finished_distinctions=fc['distinctions_finished'], old_words=fc['old_words']))
    by_k = {}
    for f in inc:
        k = f['measures']['knots']
        by_k[k] = min(by_k.get(k, 99), f['measures']['extra_holders'])
    min_extra = min(f['measures']['extra_holders'] for f in inc)
    at_min_extra = min((f for f in inc if f['measures']['extra_holders'] == min_extra), key=lambda f: (f['measures']['knots'], -float(Fraction(f['score']))))
    bound3 = [f for f in inc if f['measures']['max_holders'] <= 3]
    strict = [f for f in inc if f['measures']['cls'] == cls]
    out[f'class_{cls}'] = dict(found=len(inc), found_strictly_in_class=len(strict), smallest=best_v,
                               smallest_extra_holders_at_any_knots=dict(extra_holders=min_extra, knots=at_min_extra['measures']['knots'],
                                                                        knots_A=at_min_extra['knots_A'], knots_B=at_min_extra['knots_B'], score=at_min_extra['score']),
                               fewest_extra_holders_by_knots={str(k): v for k, v in sorted(by_k.items())},
                               with_no_distinction_held_more_than_three_times=len(bound3),
                               largest_score=max((f['score'] for f in inc), key=lambda s: Fraction(s)))
    # several smallest, for the note
    out[f'class_{cls}']['ten_smallest'] = [dict(knots=f['measures']['knots'], extra=f['measures']['extra_holders'], score=f['score'],
                                                knots_A=f['knots_A'], knots_B=f['knots_B'], source=f['source']) for f in inc[:10]]
    print(cls, 'found', len(inc), 'smallest', size(best), best['score'], 'full enumeration', fc['hidden'], fc['score'], fc['agrees_with_side_tables'])
out['largest_hidden_score_found'] = max((f['score'] for f in found), key=lambda s: Fraction(s)) if found else None
json.dump(out, open(f'{A}/report.json', 'w'), indent=1, default=str)
json.dump(found, open(f'{A}/structures_found.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1, default=str)[:6000])
print(f'done {time.time() - t0:.0f}s')
