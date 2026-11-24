"""Row G of THIRD-HOLDER-20261123-001B, and the two starting structures.

Part 1 (holder bound two): the census listings and pairings of ticket REVIEW-LEADS-20261123-001C are reproduced: 596 and
3,018 side tables for sides of at most 3 knots, and a largest hidden score of exactly 2 (read from the summaries written by
sides.py and pairs.py --mode full; the commands are in results_draft.md).
Part 2: 100 drawn pairs that use a third holder (25 from each of class L and S with one and two shared distinctions, sides of
at most 4 knots): every word of the four finished structures is enumerated (no side-table shortcut) and the joint record
counts are compared with F_a^T (T_A T_B^T) F_b; the stored structure of each side is re-enumerated directly and compared with
the listed table; the exact evaluation of the brute-force tables (hiding, score) is compared with the evaluation of M.
Part 3: the lemma used by pairs.py --mode lemma agrees with --mode full on every class where both were run (hidden pairs,
largest hidden score, old tables above 2).
Part 4: the 18-knot structure and the pencil 9-knot structure, by full enumeration of the four finished structures.
"""
import sys, json, time
import numpy as np
from fractions import Fraction
import common as c, structures as st

t0 = time.time()
out = {}
ok_all = True
def say(*a): print(*a, flush=True)

# ---- part 1 ------------------------------------------------------------------------------------------------------------
p1 = {}
for cut, want in ((1, 596), (2, 3018)):
    meta = json.load(open(f'{c.ART}/sides_L_c{cut}_k3_i3_h2.json'))
    n = meta['stats'][-1]['tables']
    sm = json.load(open(f'{c.ART}/pairs_L_c{cut}_k3_i3_h2__L_c{cut}_k3_i3_h2_full_summary.json'))
    good = (n == want) and sm['max_score_hidden_exact'] == '2' and sm['n_hidden_gt2'] == 0
    p1[f'cut{cut}'] = dict(tables=n, expected_tables=want, hidden_pairs=sm['pairs_hidden'], max_hidden=sm['max_score_hidden_exact'],
                           above2=sm['n_hidden_gt2'], ok=bool(good))
    ok_all &= good
    say('part 1', cut, p1[f'cut{cut}'])
out['part1_two_holders'] = p1

# ---- part 2 ------------------------------------------------------------------------------------------------------------
rng = np.random.default_rng(20261123)
p2 = dict(pairs=0, joint_mismatch=0, table_mismatch=0, eval_mismatch=0, by_pool={})
for cls in ('L', 'S'):
    for cut in (1, 2):
        tag = f'{cls}_c{cut}_k4_i5_h3'
        d = np.load(f'{c.ART}/sides_{tag}.npz')
        T = d['T'].astype(np.int64); ex = d['extra']; kn = d['knots']; S = d['structs']
        third = np.nonzero((ex > 0) & d['nonempty'])[0]; anyt = np.nonzero(d['nonempty'])[0]
        done = 0; tries = 0
        while done < 25:
            tries += 1
            i = int(rng.choice(third)); j = int(rng.choice(third if done % 2 == 0 else anyt))
            if rng.random() < 0.5: i, j = j, i
            M = T[i] @ T[j].T
            if M.sum() == 0: continue
            names = [f's{q + 1}' for q in range(cut)]
            kA = c.side_struct(S[i], kn[i], cut, 'A', names); kB = c.side_struct(S[j], kn[j], cut, 'B', names)
            # stored structures make the listed tables
            tA = c.side_table(kA, c.OBS['A'], names); tB = c.side_table(kB, c.OBS['B'], names)
            if not (np.array_equal(tA, T[i]) and np.array_equal(tB, T[j])): p2['table_mismatch'] += 1
            meas = c.structure_measures(kA, kB)
            assert meas['extra_holders'] > 0 and meas['cls'] in (cls, 'L')
            fc = c.full_check(kA, kB)
            if not fc['agrees_with_side_tables']: p2['joint_mismatch'] += 1
            hA, hB = c.exact_hidden(M)
            sc = c.exact_best(M, slack=1e-9)[0]
            if (hA and hB) != fc['hidden'] or sc != fc['score']: p2['eval_mismatch'] += 1
            done += 1; p2['pairs'] += 1
        p2['by_pool'][tag] = dict(pairs=done, draws=tries)
        say('part 2', tag, p2['by_pool'][tag], {k: p2[k] for k in ('joint_mismatch', 'table_mismatch', 'eval_mismatch')})
good2 = p2['pairs'] == 100 and p2['joint_mismatch'] == 0 and p2['table_mismatch'] == 0 and p2['eval_mismatch'] == 0
p2['ok'] = bool(good2); ok_all &= good2
out['part2_brute_force_third_holder'] = p2

# ---- part 3 ------------------------------------------------------------------------------------------------------------
p3 = {}
import glob, os
for f in sorted(glob.glob(f'{c.ART}/pairs_*_full_summary.json')):
    sf = json.load(open(f)); fl = f.replace('_full_summary', '_lemma_summary')
    if not os.path.exists(fl): continue
    sl = json.load(open(fl))
    if sf.get('rows', [0, None])[0] != 0 or sf['rows'][1] != sf['projective_tables'][0]: continue
    mf = Fraction(sf['max_score_hidden_exact']) if sf.get('max_score_hidden_exact') else None
    ml = Fraction(sl['max_score_hidden_exact']) if sl.get('max_score_hidden_exact') else None
    # the lemma scores only the pairs it cannot exclude, so its largest value equals the full one when that exceeds 2,
    # and is at most 2 otherwise
    max_ok = (ml == mf) if (mf is not None and mf > 2) else (ml is None or ml <= 2)
    good = (sf['pairs_hidden'] == sl['hidden_ordered_pairs'] and max_ok and sf['n_hidden_gt2'] == sl.get('n_hidden_gt2', 0))
    # every excess old table of the full run is among those of the lemma run (canonical scores and sizes)
    ef = sorted((e['score'], e['knots'], e['extra_holders']) for e in sf.get('excess', []))
    el = sorted((e['score'], e['knots'], e['extra_holders']) for e in sl.get('excess', []))
    good &= (ef == el)
    p3[os.path.basename(f)] = dict(hidden_full=sf['pairs_hidden'], hidden_lemma=sl['hidden_ordered_pairs'], max_full=sf['max_score_hidden_exact'],
                                   max_lemma=sl.get('max_score_hidden_exact'), above2_full=sf['n_hidden_gt2'], above2_lemma=sl.get('n_hidden_gt2', 0), ok=bool(good))
    ok_all &= good
    say('part 3', os.path.basename(f), p3[os.path.basename(f)])
out['part3_lemma_vs_full'] = p3

# ---- part 3b: compiled pairing, reduction against every ordered pair, on classes with and without an excess ----------------
p3b = {}
for nm in ('mixS', 'search_L_c2', 'search_S_c2'):
    sl = json.load(open(f'{c.ART}/pc_{nm}__{nm}_lemma_summary.json')); sf = json.load(open(f'{c.ART}/pc_{nm}__{nm}_full_summary.json'))
    el = {json.dumps(e['M']): (e['score'], e['knots'], e['extra_holders']) for e in sl['excess']}
    ef = {json.dumps(e['M']): (e['score'], e['knots'], e['extra_holders']) for e in sf['excess']}
    good = (el == ef)
    p3b[nm] = dict(excess_full=len(ef), excess_lemma=len(el), same_old_tables_scores_and_sizes=bool(good),
                   pairs_full=sf['pairs'], pairs_lemma=sl['pairs'], max_full=sf['max_hidden_score_exact'], max_lemma=sl['max_hidden_score_exact'])
    ok_all &= good
    say('part 3b', nm, p3b[nm])
out['part3b_compiled_lemma_vs_full'] = p3b

# ---- part 2b: the seeded side generator's tables against direct enumeration ----------------------------------------------
p2b = dict(checked=0, mismatches=0)
for cls in ('L', 'S'):
    for cut in (1, 2):
        d = np.load(f'{c.ART}/sides_search_{cls}_c{cut}.npz')
        for t in np.random.default_rng(7).choice(len(d['T']), 50, replace=False):
            names = [f's{q + 1}' for q in range(cut)]
            kA = c.side_struct(d['structs'][t], d['knots'][t], cut, 'A', names)
            meas_h = c.holders(kA)
            assert all(1 <= meas_h[o] <= (1 if cls == 'L' else 2) for o in c.OBS['A']) and all(meas_h[s_] == 1 for s_ in names)
            assert all(1 <= v <= 3 for k_, v in meas_h.items() if k_.startswith('Ah')) and int(d['knots'][t]) <= 9
            p2b['checked'] += 1
            p2b['mismatches'] += not np.array_equal(c.side_table(kA, c.OBS['A'], names), d['T'][t])
p2b['ok'] = p2b['mismatches'] == 0; ok_all &= p2b['ok']
say('part 2b', p2b)
out['part2b_search_tables'] = p2b

# ---- part 4 ------------------------------------------------------------------------------------------------------------
p4 = {}
for name, (kA, kB, cls) in st.STARTS.items():
    t1 = time.time()
    fc = c.full_check(kA, kB)
    meas = c.structure_measures(kA, kB)
    M, TA, TB, sh = c.old_table(kA, kB)
    p4[name] = dict(knots=c.fmt_knots(kA) + c.fmt_knots(kB), measures=meas, hidden=fc['hidden'], hidden_A=fc['hidden_A'], hidden_B=fc['hidden_B'],
                    score=str(fc['score']), score_float=float(fc['score']), change=str(fc['change']), agrees_with_side_tables=fc['agrees_with_side_tables'],
                    old_words=fc['old_words'], finished_words=fc['words_finished'], finished_distinctions=fc['distinctions_finished'],
                    shared=sh, T_A=TA.tolist(), T_B=TB.tolist(), control=float(c.score_batch_c(M[None], control=True)[0]),
                    seconds=round(time.time() - t1, 1))
    say('part 4', name, {k: v for k, v in p4[name].items() if k not in ('T_A', 'T_B', 'knots')})
out['part4_starts'] = p4
g18 = p4['eighteen']['hidden'] and p4['eighteen']['score'] == '20/9' and p4['eighteen']['agrees_with_side_tables']
out['eighteen_reproduces_20_9_hidden'] = bool(g18)
out['P4_pencil_20_9_hidden'] = bool(p4['pencil']['hidden'] and p4['pencil']['score'] == '20/9')
out['row_G_pass'] = bool(ok_all)
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(f'{c.ART}/gates.json', 'w'), indent=1, default=str)
say('ROW G:', 'PASS' if ok_all else 'FAIL', '| 18-knot 20/9 hidden:', g18, '| P4 pencil 20/9 hidden:', out['P4_pencil_20_9_hidden'])
