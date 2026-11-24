"""SETTING-AS-REREAD-20261123-001A-E001: the report.  Reads the JSON files written by both_settings.py, applies the
"Fails when" column of the frozen note literally (deviations A15), and writes summary.json and tables.md (every table of
(a) to (f) in full) to the artifact folder.  Computes nothing new from words; reads only this study's outputs.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / 'artifacts' / HERE.parent.name / HERE.name


def load(name):
    return json.loads((ART / name).read_text())


def yn(b):
    return 'yes' if b else 'no'


def main():
    st, gd, mn, ee, ff = (load('selftest.json'), load('g_draws.json'), load('main.json'), load('e.json'),
                          load('f_000-512.json'))
    V = {}
    T = []   # markdown lines

    # ---------------- row G ----------------
    c = gd['counts']
    g1 = (c['funded'] == 280 and c['engine_equals_recorded'] == 280 and not gd['mismatches']
          and all(c[k] == 280 for k in ('planner_off_equals_end_operator_round1', 'planner_off_equals_qgrowth_round1',
                                        'planner_QO_equals_qgrowth_round1', 'planner_QN_equals_qgrowth_round1')))
    g2 = mn['g2']['all_agree'] and len(mn['g2']['rows']) == 9
    V['G'] = dict(holds=bool(g1 and g2), draws=c, scorer_rows=len(mn['g2']['rows']), scorer_all_agree=mn['g2']['all_agree'])

    # ---------------- P1 ----------------
    a = mn['a']
    births_ok = (a['n_births'] == 2 and a['one_parent_births'] == 2
                 and all(ch['fresh'] == [1, 1] for ch in a['choices']))
    opts_ok = all(len(b['options']) == 3 for b in a['births'])
    main_pair = [r for r in mn['b'] if r['pair_A'] == ['x2', 'x3'] and r['pair_B'] == ['y2', 'y3']][0]
    mp_ok = (all(v == 144 for v in main_pair['words'].values()) and main_pair['hidden']['both']
             and F(main_pair['score_i']) == F(20, 9))
    others = [r for r in mn['b'] if r is not main_pair]
    oth_ok = len(others) == 8 and all(r['hidden']['both'] and F(r['score_i']) in (F(19, 9), F(37, 18)) for r in others)
    V['P1'] = dict(holds=bool(births_ok and opts_ok and mp_ok and oth_ok), births=births_ok, options=opts_ok,
                   main_pair=mp_ok, other_eight=oth_ok)

    # ---------------- P2 ----------------
    fx = mn['c']['fixed']
    refs = [k for k in fx if not k.startswith('old structure')]
    fixed_ok = all(F(fx[k][s]) <= 2 for k in refs for s in ('score_i', 'score_ii', 'score_iii'))
    not_alice = all(mn['c']['s1s2_same_for_alice_choice_given_bob'].values())
    on_bob_some = not all(mn['c']['s1s2_same_for_bob_choice_given_alice'].values())
    on_bob_every = not any(mn['c']['s1s2_same_for_bob_choice_given_alice'].values())
    V['P2'] = dict(holds=bool(fixed_ok and not_alice and on_bob_some), fixed_scores_at_most_2=fixed_ok,
                   s1s2_not_on_alice=not_alice, s1s2_on_bob_for_some_alice_choice=on_bob_some,
                   s1s2_on_bob_for_every_alice_choice=on_bob_every)

    # ---------------- P3, P4, P5 ----------------
    V['P3'] = dict(holds=bool(mn['d']['all_nine_hidden']), largest_subtest_score_i=mn['d']['largest_score_i'])
    V['P4'] = dict(holds=not ee['strict_hidden_excess'], strict_met=ee['strict_met'],
                   strict_hidden_excess=ee['strict_hidden_excess'], beside_loose_met=ee['loose_met'],
                   beside_loose_hidden_excess=ee['loose_hidden_excess'], beside_two_one_parent_met=ee['two_one_parent_met'],
                   beside_two_one_parent_hidden_excess=ee['two_one_parent_hidden_excess'])
    V['P5'] = dict(holds=F(main_pair['score_iii']) == F(main_pair['score_i']), score_i=main_pair['score_i'],
                   score_iii=main_pair['score_iii'])

    # ---------------- (f) classes ----------------
    rows = ff['rows']
    # parity knots in order: 0 A0, 1 even(x2,h1,h2), 2 odd(x3,h1,h2), 3 B0, 4 t-m, 5 s1-m, 6 y2-k, 7 y3-k, 8 s2-k
    cls = defaultdict(Counter)
    for r in rows:
        alpha = r['laws'][1] != r['laws'][2]     # x2 + x3 forced to 1 (x2 and x3 differ)
        beta = r['laws'][6] != r['laws'][7]      # y2 + y3 forced to 1
        out = (r['status'], r.get('hidden_A'), r.get('hidden_B'), r.get('score_i'), r.get('score_ii'), r.get('score_iii'))
        cls[(alpha, beta)][out] += 1
    f_summary = dict(n=len(rows), no_word=sum(1 for r in rows if r['status'] != 'ok'),
                     hidden_excess_i=sum(1 for r in rows if r.get('hidden_excess')),
                     hidden_excess_ii=sum(1 for r in rows if r.get('hidden_excess_ii')),
                     hidden_excess_iii=sum(1 for r in rows if r.get('hidden_excess_iii')),
                     outcomes=Counter((r.get('hidden'), r.get('score_i')) for r in rows),
                     classes={f'x2!=x3:{al} y2!=y3:{be}': {str(k): v for k, v in cnt.items()} for (al, be), cnt in cls.items()})
    f_summary['outcomes'] = {str(k): v for k, v in f_summary['outcomes'].items()}

    # ================= tables =================
    T.append('### Row G')
    T.append('')
    T.append('| check | compared | equal |')
    T.append('| --- | --- | --- |')
    T.append(f"| QGrowth, re-reading off, against the recorded driver lib.grow (stars, knots per stage, outcome; 12 rounds, 5,000 knots) | {c['funded']} funded draws ({', '.join(f'arm {k}: {v}' for k, v in gd['funded_per_arm'].items())}), {c['rounds_compared']} rounds | {c['engine_equals_recorded']} |")
    T.append(f"| this study's planner, re-reading off, against end_operator.step, round 1 (status, parents, fresh, demand) | {c['funded']} | {c['planner_off_equals_end_operator_round1']} |")
    T.append(f"| this study's planner against QGrowth, round 1, re-reading off / on with convention O / on with convention N | {c['funded']} each | {c['planner_off_equals_qgrowth_round1']} / {c['planner_QO_equals_qgrowth_round1']} / {c['planner_QN_equals_qgrowth_round1']} (re-reading births at round 1: {c['reread_births_round1_O']} under O, {c['reread_births_round1_N']} under N) |")
    T.append('')
    T.append('| Alice pair | Bob pair | recorded scorer, score | this study, score (ii) | recorded scorer, hidden | this study, hidden | agree |')
    T.append('| --- | --- | --- | --- | --- | --- | --- |')
    for r in mn['g2']['rows']:
        T.append(f"| {', '.join(r['pair_A'])} | {', '.join(r['pair_B'])} | {r['scorer_score']:.12f} | {r['mine_score_ii']} | {yn(r['scorer_hidden'])} | {yn(r['mine_hidden'])} | {yn(r['agree'])} |")
    T.append('')
    T.append(f"Self-test of the scoring code (objects that are not this study's): {st['random_tables']} drawn tables of one- and two-bit records, score (i) merged = unmerged = every function on both sides, score (ii) = every parity on both sides with and without the constant; {st['random_tables_8']} drawn three-bit tables, merged = unmerged; a non-local box gives 4; the recorded scorer's own four-type example gives {st['scorer_example_score_ii']} by score (ii), as `evaluate(M)` does, and {st['scorer_example_score_i']} by score (i).")
    T.append('')

    T.append('### (a) Round 1 of rule Q on the 11-knot structure')
    T.append('')
    T.append(f"Live knots (knot: openings): {a['live_knots']} (knot 0 = even(x1,x2,x3,c), knot 5 = even(y1,y2,y3,t)); groups of two or more live knots: {a['groups'] or 'none'}; births: {a['n_births']}, of which one-parent: {a['one_parent_births']}.")
    T.append('')
    T.append('| birth | parent | loose distinction taken | options (shared distinctions of the parent) |')
    T.append('| --- | --- | --- | --- |')
    for b in a['births']:
        T.append(f"| {b['index']} | {b['parent_knots'][0]} | {b['loose_taken']} | {', '.join(b['options'])} |")
    T.append('')
    T.append('| choice (Alice, Bob) | birth on x1 takes | birth on y1 takes | lookahead demand | fresh distinctions | QGrowth = this planner |')
    T.append('| --- | --- | --- | --- | --- | --- |')
    for ch in a['choices']:
        T.append(f"| {ch['choice']['0']}, {ch['choice']['1']} | {', '.join(ch['inputs'][0])} | {', '.join(ch['inputs'][1])} | {ch['demand'][0]}, {ch['demand'][1]} | {ch['fresh'][0]}, {ch['fresh'][1]} | {yn(ch['engines_equal'])} |")
    T.append('')
    T.append(f"Convention O (smallest number, deviations A2) would take {', '.join(a['convention_O_takes'])}; convention N {', '.join(a['convention_N_takes'])}. Old structure: {mn['old_words']} allowed words over 16 distinctions.")
    T.append('')
    T.append('| stage-1 structure (Alice, Bob) | newborns | allowed words | completions per old word (completions: old words) |')
    T.append('| --- | --- | --- | --- |')
    for k, v in sorted(mn['stage1'].items()):
        T.append(f"| {k.replace('|', ', ')} | {'; '.join(v['knots'])} | {v['words']} | {', '.join(f'{a_}: {b_}' for a_, b_ in sorted(v['completions'].items()))} |")
    T.append('')

    def score_row(r, extra=''):
        if r['status'] != 'ok':
            return f"| {extra}{', '.join(r['pair_A'])} | {', '.join(r['pair_B'])} | {', '.join(str(v) for v in r['words'].values())} | {r['status']} | | | | | |"
        h = r['hidden']
        return (f"| {extra}{', '.join(r['pair_A'])} | {', '.join(r['pair_B'])} | {', '.join(str(r['words'][k]) for k in ('00', '01', '10', '11'))} | "
                f"{yn(h['A']['hidden'])} ({h['A']['largest_change']}) | {yn(h['B']['hidden'])} ({h['B']['largest_change']}) | "
                f"{r['score_i']} | {r['score_ii']} ({r['score_ii_with_constant']}) | {r['score_iii']} | {yn(r['hidden_excess'])} |")
    HDR = ('| Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | '
           'Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |')
    SEP = '| --- | --- | --- | --- | --- | --- | --- | --- | --- |'
    T.append('### (b) All nine pairs of option pairs')
    T.append('')
    T.append(HDR)
    T.append(SEP)
    for r in mn['b']:
        T.append(score_row(r))
    T.append('')
    d1 = main_pair['score_i_detail']
    T.append(f"For (x2, x3) against (y2, y3) the value 20/9 is reached with the minus sign on E({d1['placement'][0]},{d1['placement'][1]}); the four correlations are {', '.join(f'E({k[0]},{k[1]}) = {v}' for k, v in sorted(d1['E'].items()))}; response functions found by enumerating {'Bob' if d1['enumerated'] == 'B' else 'Alice'} ({d1['merged']} merged generators per setting), re-evaluated in fractions; the unmerged enumeration of Alice's functions gives {main_pair['score_i_brute']}.")
    T.append('')

    cc = mn['c']
    T.append('### (c) The pair (x2, x3) against (y2, y3): what depends on the far choice')
    T.append('')
    T.append('| choice (Alice, Bob) | P(s1 s2 = 00) | 01 | 10 | 11 |')
    T.append('| --- | --- | --- | --- | --- |')
    for k, v in cc['s1s2'].items():
        T.append(f"| {k.replace('|', ', ')} | {v['00']} | {v['01']} | {v['10']} | {v['11']} |")
    T.append('')
    T.append(f"(s1, s2) the same under Alice's two choices, for Bob's choice y2 / y3: {yn(cc['s1s2_same_for_alice_choice_given_bob']['y2'])} / {yn(cc['s1s2_same_for_alice_choice_given_bob']['y3'])}. The same under Bob's two choices, for Alice's choice x2 / x3: {yn(cc['s1s2_same_for_bob_choice_given_alice']['x2'])} / {yn(cc['s1s2_same_for_bob_choice_given_alice']['x3'])}.")
    T.append('')
    T.append('| observer | distinctions | own choice | unchanged by the far choice | change (total variation) |')
    T.append('| --- | --- | --- | --- | --- |')
    for key, label in (('own_distinctions', 'held by its own knots, with its fresh one'),
                       ('own_without_s1_s2', 'the same without s1 and s2 (beside, deviations B4)')):
        for who in ('A', 'B'):
            o = cc[key][who]
            for ch, v in o['per_own_choice'].items():
                T.append(f"| {'Alice' if who == 'A' else 'Bob'} | {label}: {' '.join(o['names'])} | {ch} | {yn(v['same'])} | {v['change']} |")
    T.append('')
    T.append('Old words\' distribution held fixed (deviations A11): reference weight of an old word = its number of completions in the reference structure, divided equally among its completions under each choice.')
    T.append('')
    T.append('| reference | weighted totals (00, 01, 10, 11; weights x4) | Alice hidden | Bob hidden | score (i) | score (ii) (with the constant) | score (iii) |')
    T.append('| --- | --- | --- | --- | --- | --- | --- |')
    for k, r in fx.items():
        h = r['hidden']
        T.append(f"| {k.replace('|', ', ')} | {', '.join(str(r['words'][x]) for x in ('00', '01', '10', '11'))} | {yn(h['A']['hidden'])} | {yn(h['B']['hidden'])} | {r['score_i']} | {r['score_ii']} ({r['score_ii_with_constant']}) | {r['score_iii']} |")
    T.append('')

    dd = mn['d']
    T.append('### (d) Three options each')
    T.append('')
    T.append('| Alice choice | Bob choice | allowed words | Alice\'s five-value record the same for all three of Bob\'s choices | Bob\'s the same for all three of Alice\'s |')
    T.append('| --- | --- | --- | --- | --- |')
    for k, v in dd['per_choice'].items():
        a_, b_ = k.split('|')
        T.append(f"| {a_} | {b_} | {dd['words'][k]} | {yn(v['alice_same_for_every_far_choice'])} | {yn(v['bob_same_for_every_far_choice'])} |")
    T.append('')
    T.append('Two-by-two sub-tests on the five-value records (x1, x2, x3, c, zA) and (y1, y2, y3, t, zB):')
    T.append('')
    T.append(HDR)
    T.append(SEP)
    for r in dd['subtests']:
        T.append(score_row(r))
    T.append('')
    T.append(f"Largest score (i) over the nine sub-tests: {dd['largest_score_i']} (over the hidden ones: {dd['largest_score_i_hidden_subtests']}).")
    T.append('')

    T.append('### (e) One or two knots left out (66 structures)')
    T.append('')
    T.append('Knots: 0 even(x1,x2,x3,c), 1 nae(c,x2,s1), 2 nae(c,x3,s2), 3 even(x2,h1,h2), 4 odd(x3,h1,h2), 5 even(y1,y2,y3,t), 6 even(t,m1,m2), 7 even(s1,m1,m2), 8 even(y2,k1,k2), 9 odd(y3,k1,k2), 10 odd(s2,k1,k2).')
    T.append('')
    T.append('| left out | round 1 | births (parent knots: taken distinctions; fresh) | options on x1 / y1 | strict (judged) | two one-parent, joint allowed (beside) | loose (beside) | hidden excess | largest hidden score (i) | engines agree |')
    T.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in ee['rows']:
        if r['status'] == 'extend':
            r1 = r['round1']
            bs = '; '.join(f"{'+'.join(map(str, p))}: {' '.join(ins)} ({f})" for p, ins, f in
                           zip(r1['parents_original'], r1['inputs'], r1['fresh']))
            ops = f"{', '.join(r['options_x1'] or ['-'])} / {', '.join(r['options_y1'] or ['-'])}"
        elif r['status'] == 'stall':
            bs = 'shortage: ' + '; '.join(f'knot {k} short by {x}' for k, x in r['round1']['shortages'])
            ops = ''
        else:
            bs, ops = '', ''
        he = '' if 'hidden_excess' not in r else yn(r['hidden_excess'])
        T.append(f"| {', '.join(map(str, r['removed']))} | {r['status']} | {bs} | {ops} | {yn(r['strict'])} | {yn(r['two_one_parent'])} | {yn(r['loose'])} | {he} | {r.get('largest_hidden_score_i', '')} | {yn(r.get('engines_equal_every_choice', True)) if r['status'] != 'x1 or y1 held by no knot' else ''} |")
    T.append('')
    for r in ee['rows']:
        if not r['loose']:
            continue
        tag = 'strict reading (judged)' if r['strict'] else 'loose reading only (beside, not judged)'
        T.append(f"(e) without knots {', '.join(map(str, r['removed']))} ({'; '.join(r['removed_knots'])}), {tag}; tables: {r['tables_made']}:")
        T.append('')
        T.append(HDR.replace('| Alice pair', '| other births\' choices | Alice pair'))
        T.append(SEP + ' --- |')
        for t in r['b']:
            oc = ', '.join(f'birth {k}: {v}' for k, v in t['other_choice'].items()) or '-'
            T.append(score_row(t, extra=f'{oc} | '))
        T.append('')

    T.append('### (f) Every even/odd assignment of the nine parity knots (pair (x2, x3) against (y2, y3))')
    T.append('')
    T.append(f"Assignments: {f_summary['n']}; with no allowed word in some stage-1 structure: {f_summary['no_word']}; with a hidden excess by score (i): {f_summary['hidden_excess_i']} (by (ii): {f_summary['hidden_excess_ii']}, by (iii): {f_summary['hidden_excess_iii']}). The note's structure is assignment {ff['original_assignment']}.")
    T.append('')
    T.append('| x2 and x3 forced to differ (laws of even(x2,h1,h2), odd(x3,h1,h2) differ) | y2 and y3 forced to differ (laws of even(y2,k1,k2), odd(y3,k1,k2) differ) | assignments | Alice hidden | Bob hidden | score (i) | score (ii) | score (iii) |')
    T.append('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for (al, be), cnt in sorted(cls.items(), reverse=True):
        for (status, ha, hb, s1, s2, s3), n in sorted(cnt.items(), key=lambda kv: -kv[1]):
            T.append(f"| {yn(al)} | {yn(be)} | {n} | {yn(ha)} | {yn(hb)} | {s1} | {s2} | {s3} |")
    T.append('')
    T.append('Every assignment (laws in the order of deviations A14, e = even, o = odd; allowed words of the four stage-1 structures x2y2, x2y3, x3y2, x3y3; Alice hidden; Bob hidden; scores (i), (ii), (iii); hidden excess):')
    T.append('')
    T.append('```text')
    for r in rows:
        laws = ''.join(l[0] for l in r['laws'])
        w = '/'.join(str(r['words'][k]) for k in ('00', '01', '10', '11'))
        if r['status'] != 'ok':
            T.append(f"{r['assignment']:3d} {laws} {w} no word")
            continue
        T.append(f"{r['assignment']:3d} {laws} {w} A:{'h' if r['hidden_A'] else '-'} B:{'h' if r['hidden_B'] else '-'} "
                 f"{r['score_i']} {r['score_ii']} {r['score_iii']} {'EXCESS' if r['hidden_excess'] else ''}{' (note)' if r['original'] else ''}")
    T.append('```')
    T.append('')

    summary = dict(verdicts=V, f=f_summary, inputs=mn['inputs'],
                   runs=(ART / 'logs' / 'runs.log').read_text().splitlines())
    (ART / 'summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + '\n')
    (ART / 'tables.md').write_text('\n'.join(T) + '\n')
    print(json.dumps({k: v['holds'] for k, v in V.items()}))
    print(json.dumps(f_summary['classes'], indent=0))


if __name__ == '__main__':
    main()
