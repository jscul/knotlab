"""Collect every number of the draft result (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001) into summary.json.

Reads arm 1's and arm 2's line files, the gate outputs (gates_*.json) and the full enumerations; writes summary.json and
prints the verdict inputs.  (Named report_c.py: ticket B's folder, on the import path, has a report.py.)
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import glob
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cstudy as cs  # noqa: E402

_sp = importlib.util.spec_from_file_location('gates_c', HERE / 'gates.py')
gates = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(gates)
bc = cs.bc


def F(x):
    return None if x is None else Fraction(x)


def load_json(name):
    p = cs.ART / name
    return json.loads(p.read_text()) if p.exists() else None


def main():
    S = cs.starts()
    Bl = cs.b_lines('c3')
    out = dict(rlaw_sha256=cs.rlaw_sha(), rlaw_sha256_at_freeze=cs.RLAW_SHA)

    # ------------------------------------------------------------------ arm 1
    L = gates.arm1_lines()
    G = gates.arm1_gains()
    a1 = {}
    stalled = Counter(cs.start_class(S[i]) for i in range(len(S)) if Bl[i]['outcome'] == 'stall')
    a1['stalled_starts'] = dict(stalled)
    a1['starts_in_lines'] = {c: len({l['si'] for l in L if l['cls'] == c}) for c in ('two', 'three')}
    conv = [l for l in L if l['kind'] in ('O', 'N')]
    oc = defaultdict(Counter)
    for l in conv:
        key = l['outcome'] if l['outcome'] != 'residual_stall' else f"residual_stall_round_{l['residual_round']}"
        oc[f"{l['cls']}_{l['kind']}"][key] += 1
    a1['convention_outcomes'] = {k: dict(v) for k, v in sorted(oc.items())}
    grew = defaultdict(set)
    for l in conv:
        if len(l['n_at']) >= 2:
            grew[(l['cls'], l['kind'])].add(l['si'])
    a1['grew_at_least_one_round'] = {f'{c}_{k}': len(grew[(c, k)]) for c in ('two', 'three') for k in ('O', 'N')}
    for c in ('two', 'three'):
        a1['grew_at_least_one_round'][f'{c}_either'] = len(grew[(c, 'O')] | grew[(c, 'N')])
        a1['grew_at_least_one_round'][f'{c}_both'] = len(grew[(c, 'O')] & grew[(c, 'N')])
    resid1 = {c: {k: sum(1 for l in conv if l['cls'] == c and l['kind'] == k and l['outcome'] == 'residual_stall'
                         and l['residual_round'] == 1) for k in ('O', 'N')} for c in ('two', 'three')}
    for c in ('two', 'three'):
        sO = {l['si'] for l in conv if l['cls'] == c and l['kind'] == 'O' and l['outcome'] == 'residual_stall'
              and l['residual_round'] == 1}
        sN = {l['si'] for l in conv if l['cls'] == c and l['kind'] == 'N' and l['outcome'] == 'residual_stall'
              and l['residual_round'] == 1}
        resid1[c]['both'] = len(sO & sN)
        resid1[c]['either'] = len(sO | sN)
    a1['residual_stalls_round_1'] = resid1
    a1['residual_stalls_later_rounds'] = sum(1 for l in L if l['outcome'] == 'residual_stall' and l['residual_round'] > 1)
    # choices of the two-holder starts
    crec = [l['choice_record'] for l in L if l['kind'] == 'O' and l['cls'] == 'two']
    a1['two_choice_modes'] = dict(Counter(r['mode'] for r in crec))
    a1['two_choice_totals_hist'] = {str(k): v for k, v in sorted(Counter(r['total'] for r in crec).items()) if k <= 64}
    a1['two_choice_totals_above_64'] = sum(1 for r in crec if r['total'] > 64)
    a1['two_choice_total_max'] = max(r['total'] for r in crec)
    a1['two_starts_where_O_choice_incomplete'] = sum(1 for r in crec if r['index_O'] is None)
    a1['two_starts_where_N_choice_incomplete'] = sum(1 for r in crec if r['index_N'] is None)
    a1['two_starts_no_allowed_choice'] = sum(1 for r in crec if r['total'] == 0)
    # among choice histories: residual stalls at round 1 cannot happen (a full choice pays every birth); outcomes
    a1['choice_history_outcomes'] = dict(Counter(l['outcome'] for l in L if l['kind'] in ('choice', 'choiceN')))
    a1['two_starts_some_choice_grows'] = len({l['si'] for l in L if l['kind'] in ('choice', 'choiceN')
                                             and len(l['n_at']) >= 2})
    a1['two_starts_some_history_grows'] = len({l['si'] for l in L if l['cls'] == 'two' and len(l['n_at']) >= 2})
    # histories
    hk = Counter()
    for l in L:
        full_choice = l['kind'] in ('O', 'N') or l['choice_mode'] == 'all'
        hk[(l['cls'], l['kind'], 'choices_' + ('all' if full_choice else 'drawn'), 'laws_' + l['law_mode'])] += 1
    a1['histories'] = {'|'.join(k): v for k, v in sorted(hk.items())}
    a1['histories_total'] = len(L)
    a1['histories_by_class'] = dict(Counter(l['cls'] for l in L))
    a1['histories_full'] = sum(1 for l in L if (l['kind'] in ('O', 'N') or l['choice_mode'] == 'all')
                               and l['law_mode'] == 'all')
    a1['histories_drawn_choice'] = sum(1 for l in L if l['kind'] in ('choice', 'choiceN') and l['choice_mode'] == 'drawn')
    a1['histories_drawn_assignments'] = sum(1 for l in L if l['law_mode'] == 'drawn')
    a1['histories_choiceN'] = sum(1 for l in L if l['kind'] == 'choiceN')
    a1['histories_with_a_round'] = dict(Counter(l['cls'] for l in L if len(l['n_at']) >= 2))
    # starts covered in full: every allowed round-1 choice grown (two-holder) and every assignment in every history
    per_start = defaultdict(list)
    for l in L:
        per_start[(l['cls'], l['si'])].append(l)
    cov = Counter()
    for (c, si), ls in per_start.items():
        chm = next(l['choice_mode'] for l in ls if l['kind'] == 'O')
        full = (c == 'three' or chm in ('all', 'none')) and all(l['law_mode'] == 'all' for l in ls)
        cov[(c, 'full' if full else 'partly_drawn')] += 1
    a1['starts_coverage'] = {f'{c}_{k}': v for (c, k), v in sorted(cov.items())}
    tab = Counter()
    for l in L:
        for s in l['stages']:
            tab[(l['cls'], 'all')] += s['tables']
            tab[(l['cls'], 'stages')] += 1
            if s['t'] >= 1:
                tab[(l['cls'], 'grown')] += s['tables']
                tab[(l['cls'], 'grown_stages')] += 1
                tab[(l['cls'], 'effective')] += s.get('effective', 0)
    a1['tables'] = {f'{c}_{k}': v for (c, k), v in sorted(tab.items())}
    a1['support_changes'] = sum(s['support_changes'] for l in L for s in l['stages'])
    a1['max_holders'] = {c: dict(sorted(Counter(l['max_holders'] for l in L if l['cls'] == c).items()))
                         for c in ('two', 'three')}
    pay = Counter()
    for l in L:
        for rd, b in enumerate(l['births']):
            pay[(l['cls'], f'round_{rd + 1}_paying_births')] += b[2]
            pay[(l['cls'], f'round_{rd + 1}_births')] += b[0]
            pay[(l['cls'], f'round_{rd + 1}_rounds_with_payment')] += b[2] > 0
            pay[(l['cls'], f'round_{rd + 1}_rounds')] += 1
    a1['payments'] = {f'{c}_{k}': v for (c, k), v in sorted(pay.items())}
    a1['stage0_excess_starts'] = dict(Counter(l['cls'] for l in L if l['kind'] == 'O' and l['stage0_excess']))
    # gains
    gl = [l for l in L if any(s['gains'] for s in l['stages'])]
    a1['gains_tables'] = {c: sum(s['gains'] for l in L if l['cls'] == c for s in l['stages']) for c in ('two', 'three')}
    a1['gains_through_payment_tables'] = {c: sum(s['gains_pay'] for l in L if l['cls'] == c for s in l['stages'])
                                          for c in ('two', 'three')}
    a1['gain_histories'] = [dict(si=l['si'], tid=l['tid'], mask=l['mask'], cls=l['cls'], kind=l['kind'], j=l['j'],
                                 n_at=l['n_at'], D_at=l['D_at'], outcome=l['outcome'], births=l['births'],
                                 max_holders=l['max_holders'], law_mode=l['law_mode'], choice_mode=l['choice_mode'],
                                 stage0=l['stage0_eval'],
                                 stages=[(s['t'], s['tables'], s['gains'], s['gains_pay'], s['best_hidden_exact'])
                                         for s in l['stages']]) for l in gl]
    a1['gain_starts'] = {c: len({l['si'] for l in gl if l['cls'] == c}) for c in ('two', 'three')}
    a1['gain_starts_through_payment'] = {c: len({l['si'] for l in gl if l['cls'] == c
                                                 and any(s['gains_pay'] for s in l['stages'])}) for c in ('two', 'three')}
    a1['gain_starts_not_through_payment_only'] = {c: len({l['si'] for l in gl if l['cls'] == c}
                                                         - {l['si'] for l in gl if l['cls'] == c
                                                            and any(s['gains_pay'] for s in l['stages'])})
                                                  for c in ('two', 'three')}
    a1['gain_histories_by_mode'] = dict(Counter(f"{l['cls']}|{l['kind']}|laws_{l['law_mode']}" for l in gl))
    a1['gain_scores_tables'] = dict(Counter(g['eval'][3] for g in G))
    a1['gains_written'] = len(G)
    # share beside ticket B
    gO = grew[('three', 'O')] | grew[('three', 'N')]
    gain3 = {l['si'] for l in gl if l['cls'] == 'three'}
    gain3p = {l['si'] for l in gl if l['cls'] == 'three' and any(s['gains_pay'] for s in l['stages'])}
    a1['three_share'] = dict(stalled=stalled['three'], grow_either=len(gO), gain=len(gain3), gain_through_payment=len(gain3p),
                             gain_and_grow=len(gain3 & gO),
                             ticket_B=dict(grew=7957, gained=34))
    # best hidden scores where no gain (two-holder)
    best2 = None
    bestf2 = None
    for l in L:
        if l['cls'] != 'two':
            continue
        for s in l['stages']:
            if s['t'] >= 1:
                if s['best_hidden_exact'] is not None and (best2 is None or F(s['best_hidden_exact']) > best2):
                    best2 = F(s['best_hidden_exact'])
                if s.get('best_hidden_float') is not None and (bestf2 is None or s['best_hidden_float'] > bestf2):
                    bestf2 = s['best_hidden_float']
    a1['two_best_hidden_grown_exact'] = cs.frac(best2)
    a1['two_best_hidden_grown_float'] = bestf2
    a1['two_stage0_hidden_exactly_2'] = sum(1 for l in L if l['cls'] == 'two' and l['kind'] == 'O'
                                            and l['stage0_eval'][3] == '2')
    # smallest gain in full
    if G:
        G.sort(key=lambda g: (g['knots_n'], g['D'], Fraction(g['eval'][3])))
        g = G[0]
        stars, laws, names, obs = cs.start_struct(g['si'])
        births = []
        for rd, row in enumerate(g['births']):
            for b in row:
                births.append(dict(round=rd + 1, parents=[cs.knots_text([stars[p]], [laws[p]], names)[0]
                                                          if p < len(stars) else f'newborn {p}' for p in b['parents']],
                                   inputs=[cs.name_of(names, d) for d in b['inputs']], paid=b['paid'],
                                   paying=b['paying'], fresh=b['fresh']))
        a1['smallest_gain'] = dict(si=g['si'], tid=g['tid'], mask=g['mask'], cls=g['cls'], kind=g['kind'], t=g['t'],
                                   start=cs.knots_text(stars, laws, names),
                                   start_loose=[names[d] for d in range(len(names))
                                                if sum(d in s for s in stars) == 1],
                                   start_holders={names[d]: sum(d in s for s in stars) for d in range(len(names))},
                                   stage_knots=g['knots'], newborn_laws=g['newborn_laws'], births=births,
                                   score=g['eval'][3], hidden=bool(g['eval'][0] and g['eval'][1]),
                                   through_payment=g['through_payment'], even_payers=g['even_payers_eval'],
                                   table=g['table'], D=g['D'], knots=g['knots_n'])
        same_stage = [x for x in G if x['si'] == g['si'] and x['kind'] == g['kind'] and x['t'] == g['t']]
        a1['smallest_gain']['same_stage_gain_laws'] = [x['newborn_laws'] for x in same_stage]
    # ------------------------------------------------------------------ arm 2
    L2 = gates.arm2_lines()
    a2 = dict(starts=len(L2), stalled_starts=sum(l['stalled'] for l in L2), sets=sum(l['sets'] for l in L2),
              hidden_sets=sum(l['hidden'] for l in L2), support_unchanged_all=all(l['support_unchanged'] for l in L2))
    by = defaultdict(lambda: [0, 0, 0])
    keys = ('size', 'shared', 'observers', 'origin_ordinary', 'origin_R', 'origin_anyplace')
    for l in L2:
        for row in l['counts']:
            k, v = row[:6], row[6:]
            for i, name in enumerate(keys):
                kk = (name, k[i])
                for j in range(3):
                    by[kk][j] += v[j]
            for j in range(3):
                by[('origin_pair', (k[3], k[4]))][j] += v[j]
                by[('size_shared', (k[0], k[1]))][j] += v[j]
    a2['by_class'] = {f'{a}={b}': dict(sets=v[0], hidden=v[1], gains=v[2]) for (a, b), v in sorted(by.items(), key=str)}
    a2['R_status'] = dict(Counter(l['origin']['R_status'] for l in L2))
    a2['R_not_decided_starts'] = sum(1 for l in L2 if l['n_R'] is None)
    a2['R_not_decided_sets'] = sum(l['sets'] for l in L2 if l['n_R'] is None)
    a2['ordinary_outcome'] = dict(Counter(l['origin'].get('ordinary_outcome') for l in L2))
    gs = [(l, g) for l in L2 for g in l['gains']]
    a2['gains'] = len(gs)
    a2['gain_starts'] = len({l['si'] for l, _ in gs})
    a2['gain_starts_list'] = [dict(si=l['si'], tid=l['tid'], mask=l['mask'], knots=l['knots'], D=l['D'], stalled=l['stalled'],
                                   gains=l['n_gains'], best=str(max(Fraction(g['score']) for g in l['gains'])),
                                   R_status=l['origin']['R_status'], ordinary_births=l['origin'].get('ordinary_births'))
                              for l in L2 if l['n_gains']]
    a2['gains_by'] = {}
    for name, f in (('size', lambda g: g['size']), ('shared', lambda g: g['shared']), ('observers', lambda g: g['obs_class']),
                    ('origin_ordinary', lambda g: g['origin_ordinary']), ('origin_R', lambda g: g['origin_R']),
                    ('origin_anyplace', lambda g: g['origin_anyplace']), ('known_shape', lambda g: g['known_shape']),
                    ('size_shared_observers', lambda g: f"{g['size']}|{g['shared']}|{g['obs_class']}"),
                    ('score', lambda g: g['score'])):
        a2['gains_by'][name] = {str(k): v for k, v in sorted(Counter(f(g) for _, g in gs).items(), key=lambda x: str(x[0]))}
    a2['gains_only_loose'] = sum(1 for _, g in gs if g['shared'] == 0)
    a2['gains_known_shape'] = sum(1 for _, g in gs if g['known_shape'])
    a2['gains_not_known_shape'] = sum(1 for _, g in gs if not g['known_shape'])
    a2['gains_made_by_ordinary_round1'] = sum(1 for _, g in gs if g['origin_ordinary'])
    a2['gains_made_by_R_round1'] = sum(1 for _, g in gs if g['origin_R'])
    a2['gains_R_not_decided'] = sum(1 for _, g in gs if g['origin_R'] is None)
    # loose observer distinction in every gain?
    a2['gains_with_a_loose_observer'] = sum(1 for l, g in gs if any(x in l['loose'] and x in cs.OBS for x in g['T']))
    a2['gain_T_loose_count'] = dict(Counter(sum(x in l['loose'] for x in g['T']) for l, g in gs))
    if gs:
        a2['least_T_size'] = min(g['size'] for _, g in gs)
        best = max(gs, key=lambda x: Fraction(x[1]['score']))
        a2['largest_score'] = dict(score=best[1]['score'], si=best[0]['si'], tid=best[0]['tid'], T=best[1]['T'],
                                   starts_with_it=sorted({l['si'] for l, g in gs if g['score'] == best[1]['score']}),
                                   gains_with_it=sum(1 for _, g in gs if g['score'] == best[1]['score']))
        sm = min(gs, key=lambda x: (x[0]['knots'], x[0]['D'], x[1]['size'], Fraction(x[1]['score']), x[0]['si']))
        l, g = sm
        ties = [(ll['si'], gg['T'], gg['score']) for ll, gg in gs if (ll['knots'], ll['D'], gg['size']) ==
                (l['knots'], l['D'], g['size'])]
        a2['smallest_gain'] = dict(si=l['si'], tid=l['tid'], mask=l['mask'], start=l['start_knots'], loose=l['loose'],
                                   shared=l['shared'], D=l['D'], knots=l['knots'], T=g['T'], score=g['score'],
                                   obs_class=g['obs_class'], origin_ordinary=g['origin_ordinary'], origin_R=g['origin_R'],
                                   table=g.get('table'), M=l['M'], ties=ties[:40], n_ties=len(ties))
        # stage-0 evaluation of the gain starts
    a2['best_hidden_float_no_gain_starts'] = max((l['best_hidden_float'] for l in L2 if not l['n_gains']
                                                  and l['best_hidden_float'] is not None), default=None)
    out['arm1'] = a1
    out['arm2'] = a2
    # ------------------------------------------------------------------ gates
    gt = {}
    for name in ('g1two', 'g1three', 'known', 'pairs', 'scorer'):
        j = load_json(f'gates_{name}.json')
        gt[name] = None if j is None else {k: v for k, v in j.items() if k in ('counts', 'ok', 'scores', 'n_failures',
                                                                              'failures', 'seconds')}
    st = [load_json(Path(p).name) for p in sorted(glob.glob(str(cs.ART / 'gates_stages_*.json')))]
    gt['stages'] = dict(runs=len(st), counts=sum((Counter(x['counts']) for x in st), Counter()),
                        ok=all(x['ok'] for x in st), failures=[f for x in st for f in x['failures']])
    vf = [load_json(Path(p).name) for p in sorted(glob.glob(str(cs.ART / 'gates_verify_*.json')))]
    gt['verify'] = dict(runs=len(vf), counts=sum((Counter(x['counts']) for x in vf), Counter()), ok=all(x['ok'] for x in vf))
    rows = [r for x in vf for r in x['rows']]
    gt['verify']['scores_arm1'] = dict(Counter(r['full_enumeration']['score'] for r in rows if r['arm'] == 'arm1'))
    gt['verify']['D_arm1'] = dict(Counter(r['D'] for r in rows if r['arm'] == 'arm1'))
    gt['verify']['all_hidden'] = all(r['full_enumeration']['hidden'] for r in rows)
    gt['verify']['all_scores_equal_table'] = all(r['full_enumeration']['score'] == r['score_table'] for r in rows)
    gt['verify']['joint_equals_table'] = dict(Counter(str(r['full_enumeration']['joint_equals_table']) for r in rows))
    if G:
        sg = out['arm1']['smallest_gain']
        hit = [r for r in rows if r['arm'] == 'arm1' and r['knots'] == sg['stage_knots']]
        out['arm1']['smallest_gain']['full_enumeration'] = hit[0]['full_enumeration'] if hit else None
    if gs:
        sg = out['arm2']['smallest_gain']
        hit = [r for r in rows if r['arm'] == 'arm2' and r['si'] == sg['si'] and r['T'] == sg['T']]
        out['arm2']['smallest_gain']['full_enumeration'] = hit[0]['full_enumeration'] if hit else None
        known = load_json('gates_known.json')
        out['arm2']['known_starts'] = None if known is None else [
            dict(si=r['si'], tid=r['tid'], score=r['score'], hidden=r['hidden'], stage0=r['stage0'],
                 enumeration=r['full_enumeration']) for r in known['rows']]
    out['gates'] = gt
    # ------------------------------------------------------------------ verdict inputs
    v = {}
    v['G'] = dict(g1two=gt['g1two'] and gt['g1two']['ok'], stages=gt['stages']['ok'], pairs=gt['pairs'] and gt['pairs']['ok'],
                  known=gt['known'] and gt['known']['ok'], support_arm1=a1['support_changes'] == 0,
                  support_arm2=a2['support_unchanged_all'])
    v['P1_two_holder_gains'] = a1['gains_tables']['two']
    v['P2_three_holder_gains_through_payment_starts'] = a1['gain_starts_through_payment']['three']
    v['P3_gains_with_T_only_loose'] = a2['gains_only_loose']
    v['P4_gains_not_known_shape'] = a2['gains_not_known_shape']
    out['verdict_inputs'] = v
    (cs.ART / 'summary.json').write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(v, default=str))


if __name__ == '__main__':
    main()
