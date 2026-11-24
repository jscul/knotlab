"""Report: every number of the draft result, from the outputs of q_sources.py, q_draws.py, q_census.py and q_rowg.py,
written to summary.json in the artifacts folder.  Reads only this study's outputs (and, for names, the census parts'
structures through qcen).  The smallest gain of each arm is rebuilt from its history and written out in full.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qcen  # noqa: E402

qlaw, cs, bc = qcen.qlaw, qcen.cs, qcen.bc
ART = qlaw.ART
PREREG = qlaw.ROOT / 'research/ONE-PARENT-REREAD-20261123-001A/preregistration.md'


def jl(pattern):
    return [l for f in sorted(ART.glob(pattern)) for l in qlaw.load(f)]


def gate(name):
    p = ART / f'{name}.json'
    return json.loads(p.read_text()) if p.exists() else None


def gates(prefix):
    return {p.stem: json.loads(p.read_text()) for p in sorted(ART.glob(f'{prefix}*.json'))}


def add_counts(ds):
    c = Counter()
    for d in ds:
        c.update(d.get('counts', {}))
    return dict(c)


def frac(x):
    return None if x is None else Fraction(x)


# ======================================================================================================================
def report_sources():
    rows = qlaw.load(ART / 'sources.jsonl')
    out = {}
    for r in rows:
        key = r['source']
        rule = 'ordinary' if r['rule'] == 'ordinary' else 'Q' + r['conv']
        out.setdefault(key, {})[rule] = {k: r.get(k) for k in (
            'outcome', 'rounds', 'n_at', 'births', 'one_parent_births', 'reread_births', 'rounds_with_reread', 'holders_at',
            'max_holders', 'growth_kind', 'growth_kind_births', 'first_failing_step', 'fresh_lower_bound',
            'stall_shortages', 'reread_fresh', 'zero_fresh', 'stars_sha256')}
    for key, d in out.items():
        for rule in ('QO', 'QN'):
            d[rule]['knots_per_stage_equal_ordinary'] = d[rule]['n_at'] == d['ordinary']['n_at']
            d[rule]['stars_equal_ordinary'] = d[rule]['stars_sha256'] == d['ordinary']['stars_sha256']
    return out


def alive(outcome, strict):
    return outcome == 'horizon' if strict else outcome in ('horizon', 'cap')


def report_draws():
    out = {}
    for law in ('nae', 'parity'):
        rows = jl(f'draws_{law}_arm*.jsonl')
        d = dict(funded=len(rows))
        for rule in ('ordinary', 'QO', 'QN'):
            hs = [r[rule] for r in rows]
            e = dict(outcome=dict(Counter(h['outcome'] for h in hs)),
                     growth_kind=dict(Counter(h['growth_kind'] for h in hs)),
                     growth_kind_births=dict(Counter(h['growth_kind_births'] for h in hs)),
                     first_failing_step=dict(Counter(str(h['first_failing_step']) for h in hs)),
                     births_per_round_total=[sum(h['births'][t] for h in hs if len(h['births']) > t) for t in range(12)],
                     histories_with_round=[sum(1 for h in hs if len(h['births']) > t) for t in range(12)],
                     max_holders=dict(Counter(h['max_holders'] for h in hs)),
                     holders_by_stage_max=[max((h['holders_at'][t] for h in hs if len(h['holders_at']) > t), default=None)
                                           for t in range(13)],
                     holders_by_stage_hist=[dict(Counter(h['holders_at'][t] for h in hs if len(h['holders_at']) > t))
                                            for t in range(13)])
            if rule == 'ordinary':
                e['one_parent_births_per_round_total'] = [sum(h['one_parent_births'][t] for h in hs
                                                              if len(h['one_parent_births']) > t) for t in range(12)]
                e['draws_with_one_parent_birth_after_round_1'] = sum(1 for h in hs if any(h['one_parent_births'][1:]))
            else:
                e['reread_births_per_round_total'] = [sum(h['reread_births'][t] for h in hs if len(h['reread_births']) > t)
                                                      for t in range(12)]
                e['draws_with_reread_after_round_1'] = sum(1 for h in hs if any(h['reread_births'][1:]))
                e['draws_with_reread'] = sum(1 for h in hs if any(h['reread_births']))
                e['zero_fresh_births'] = sum(sum(h['zero_fresh']) for h in hs)
                e['fresh_lower_bound_histories'] = sum(1 for h in hs if any(h['fresh_lower_bound']))
                e['stalls'] = [dict(arm=r['arm'], draw=r['draw'], shortages=r[rule]['stall_shortages'],
                                    n_at=r[rule]['n_at']) for r in rows if r[rule]['outcome'] == 'stall']
                e['births_per_round_equal_ordinary'] = sum(1 for r in rows if r[rule]['births'] == r['ordinary']['births'])
                e['knots_per_stage_equal_ordinary'] = sum(1 for r in rows if r[rule]['n_at'] == r['ordinary']['n_at'])
                e['stars_equal_ordinary'] = sum(1 for r in rows if r[rule]['stars_sha256'] is not None
                                                and r[rule]['n_at'] == r['ordinary']['n_at']
                                                and r[rule]['births'] == r['ordinary']['births']
                                                and not any(r[rule]['reread_births']))
                # P5 pieces
                e['draws_reaching_8_holders_by_round_12'] = sum(1 for h in hs if max(h['holders_at'][:13]) >= 8)
                e['draws_holders_grow_after_round_3'] = [
                    dict(arm=r['arm'], draw=r['draw'], holders_at=r[rule]['holders_at']) for r in rows
                    if len(r[rule]['holders_at']) > 4 and max(r[rule]['holders_at'][4:]) > r[rule]['holders_at'][3]]
                e['n_draws_holders_grow_after_round_3'] = len(e['draws_holders_grow_after_round_3'])
                # P6 pieces, both readings
                for strict in (False, True):
                    tag = 'strict' if strict else 'primary'
                    base = [r for r in rows if alive(r['ordinary']['outcome'], strict)]
                    lost = [dict(arm=r['arm'], draw=r['draw'], ordinary=r['ordinary']['outcome'], Q=r[rule]['outcome'],
                                 Q_n_at=r[rule]['n_at'], Q_births=r[rule]['births'], Q_reread=r[rule]['reread_births'])
                            for r in base if not alive(r[rule]['outcome'], strict)]
                    e[f'P6_{tag}'] = dict(alive_ordinary=len(base), alive_Q=len(base) - len(lost), not_alive_Q=len(lost),
                                          not_alive_by_outcome=dict(Counter(x['Q'] for x in lost)), cases=lost[:40])
                    rev = [dict(arm=r['arm'], draw=r['draw'], ordinary=r['ordinary']['outcome'], Q=r[rule]['outcome'])
                           for r in rows if not alive(r['ordinary']['outcome'], strict) and alive(r[rule]['outcome'], strict)]
                    e[f'P6_{tag}']['alive_Q_not_ordinary'] = len(rev)
                e['outcome_pairs'] = dict(Counter(f"{r['ordinary']['outcome']}->{r[rule]['outcome']}" for r in rows))
            d[rule] = e
        out[law] = d
    # pooled P5 / P6 verdict inputs
    p5 = dict(O_draws_reaching_8=sum(out[l]['QO']['draws_reaching_8_holders_by_round_12'] for l in out),
              N_draws_grow_after_3=sum(out[l]['QN']['n_draws_holders_grow_after_round_3'] for l in out))
    p5['fails'] = p5['O_draws_reaching_8'] == 0 or p5['N_draws_grow_after_3'] > 0
    p6 = {}
    for tag in ('primary', 'strict'):
        nl = sum(out[l][r][f'P6_{tag}']['not_alive_Q'] for l in out for r in ('QO', 'QN'))
        p6[tag] = dict(not_alive_Q_histories=nl, fails=nl > 0)
    return out, p5, p6


# ======================================================================================================================
def report_census():
    parts = jl('census_parts_c_*.jsonl.gz')
    hist = jl('census_hist_c_*.jsonl.gz')
    gains = jl('census_gains_c_*.jsonl.gz')
    pop = qcen.population()
    lift = sorted(qcen.liftable_parts())
    assert len(parts) == len(pop) == 5761 and {p['si'] for p in parts} == set(pop)
    out = dict(parts=len(parts), stalled_counted=len(qcen.stalled_two_holder()),
               no_round=sum(1 for p in parts if p['D0'] > qcen.DMAX))
    out['growing_parts'] = out['parts'] - out['no_round']
    grow_parts = [p for p in parts if p['D0'] <= qcen.DMAX]
    out['choice_mode'] = dict(Counter(p['choice_record']['mode'] for p in grow_parts))
    out['choice_total_hist'] = dict(sorted(Counter(p['choice_record']['total'] for p in grow_parts).items()))
    out['choice_total_max'] = max(p['choice_record']['total'] for p in grow_parts)
    out['parts_with_reread_at_round_1'] = sum(1 for p in grow_parts if p['choice_record']['sizes'])
    out['histories'] = dict(total=len(hist), by_kind=dict(Counter(h['kind'] for h in hist)),
                            grown=sum(1 for h in hist if len(h['n_at']) >= 2),
                            distinct_per_part_total=sum(p['distinct_histories'] for p in parts),
                            law_mode=dict(Counter(h['law_mode'] for h in hist)),
                            outcome=dict(Counter(h['outcome'] for h in hist)),
                            stalls=[dict(si=h['si'], kind=h['kind'], j=h['j'], stall=h['stall']) for h in hist
                                    if h['outcome'] == 'stall'],
                            rounds=dict(Counter(len(h['n_at']) - 1 for h in hist)),
                            max_holders=dict(Counter(max(h['holders_at']) for h in hist)))
    # histories with every choice and every assignment enumerated (by part)
    full_parts = set()
    for p in grow_parts:
        hs = [h for h in hist if h['si'] == p['si']]
        if p['choice_record']['mode'] == 'all' and all(h['law_mode'] == 'all' for h in hs):
            full_parts.add(p['si'])
    out['parts_fully_enumerated'] = len(full_parts)
    out['parts_partly_drawn'] = len(grow_parts) - len(full_parts)
    out['histories_fully_enumerated_assignments'] = sum(1 for h in hist if h['law_mode'] == 'all')
    out['histories_from_drawn_choices'] = sum(1 for h in hist if h['kind'] == 'choice' and h['choice_mode'] == 'drawn')
    out['tables'] = dict(uniform=sum(len(h['uniform']) for h in hist),
                         mixed=sum(s['tables'] for h in hist for s in h['stages']),
                         mixed_effective=sum(s['effective'] for h in hist for s in h['stages']),
                         grown_stages=sum(len(h['stages']) for h in hist))
    out['support_changes'] = dict(mixed=sum(s['support_changes'] for h in hist for s in h['stages']),
                                  uniform=sum(u['support_changed'] for h in hist for u in h['uniform']))
    out['round1_reread_births'] = sum(h['births'][0]['reread'] for h in hist if h['births'])
    out['round1_births'] = sum(h['births'][0]['n'] for h in hist if h['births'])
    out['reread_births_by_round'] = [sum(h['births'][t]['reread'] for h in hist if len(h['births']) > t) for t in range(3)]
    out['births_by_round'] = [sum(h['births'][t]['n'] for h in hist if len(h['births']) > t) for t in range(3)]
    out['reread_fresh_by_round'] = [dict(sum((Counter(h['births'][t]['reread_fresh']) for h in hist
                                              if len(h['births']) > t), Counter())) for t in range(3)]
    out['round1_sibling_class'] = dict(Counter(h['births'][0]['siblings'] for h in hist if h['births']))
    # best hidden scores where nothing gains
    best = {}
    for arm in ('uniform', 'mixed'):
        vals = []
        for h in hist:
            if arm == 'uniform':
                for u in h['uniform']:
                    if u['eval'][0] and u['eval'][1] and u['eval'][3] is not None:
                        vals.append(Fraction(u['eval'][3]))
            else:
                for s in h['stages']:
                    if s['best_hidden_exact'] is not None:
                        vals.append(Fraction(s['best_hidden_exact']))
        best[arm] = str(max(vals)) if vals else None
    out['best_hidden_exact_any_stage'] = best
    stage0 = {p['si']: p['stage0_eval'] for p in parts}
    out['parts_hidden_at_exactly_2_stage0'] = sum(1 for p in parts if p['stage0_eval'][0] and p['stage0_eval'][1]
                                                  and p['stage0_eval'][3] == '2')
    out['liftable_in_population'] = sum(1 for si in lift if si in set(pop))
    # ---- gains ----
    G = {}
    for arm in ('uniform', 'mixed'):
        gs = [g for g in gains if g['arm'] == arm]
        e = dict(tables=len(gs), parts=sorted({g['si'] for g in gs}),
                 histories=len({(g['si'], g['kind'], g['j']) for g in gs}),
                 by_round=dict(Counter(g['t'] for g in gs)),
                 by_kind=dict(Counter(g['kind'] for g in gs)),
                 by_kind_round=dict(Counter(f"{g['kind']}_t{g['t']}" for g in gs)),
                 by_round1_siblings=dict(Counter(g['siblings'][0] for g in gs)),
                 by_siblings=dict(Counter('/'.join(g['siblings']) for g in gs)),
                 by_reread_laws=dict(Counter(','.join(sorted(r['law'] for r in g['reread'])) for g in gs)),
                 by_reread_fresh=dict(Counter(','.join(str(r['fresh']) for r in sorted(g['reread'], key=lambda r: (
                     r['round'], r['birth']))) for g in gs)),
                 by_nae_reread_fresh=dict(Counter(','.join(sorted(str(r['fresh']) for r in g['reread'] if r['law'] == 'nae'))
                                                  for g in gs)),
                 by_multi_input_nae=dict(Counter(sum(1 for m in g['multi_input'] if m['law'] == 'nae') for g in gs)),
                 scores=dict(Counter(g['eval'][3] for g in gs)),
                 drawn_choice=sum(1 for g in gs if g['kind'] == 'choice' and
                                  next(h for h in hist if h['si'] == g['si'] and h['kind'] == 'choice' and h['j'] == g['j'])[
                                      'choice_mode'] == 'drawn'))
        e['n_parts'] = len(e['parts'])
        e['parts_liftable'] = sorted(set(e['parts']) & set(lift))
        e['parts_other'] = sorted(set(e['parts']) - set(lift))
        e['parts_round1'] = sorted({g['si'] for g in gs if g['t'] == 1})
        e['liftable_without_round1_gain'] = sorted(set(lift) - set(e['parts_round1']))
        e['stage0_of_gaining_parts'] = dict(Counter(f"hidden={stage0[si][0] and stage0[si][1]},exact={stage0[si][3]}"
                                                    for si in e['parts']))
        st1 = [g for g in gs if g['t'] == 1]
        e['stage1'] = dict(tables=len(st1), control_computed=sum('control' in g for g in st1),
                           control_lost=sum(1 for g in st1 if 'control' in g and not g['control']['excess']),
                           control_kept=[dict(si=g['si'], kind=g['kind'], j=g['j'], laws=g['laws'])
                                         for g in st1 if 'control' in g and g['control']['excess']][:20])
        conv1 = [g for g in st1 if g['kind'] in ('O', 'N')]
        e['stage1_conventions'] = dict(tables=len(conv1), parts=sorted({g['si'] for g in conv1}))
        same1 = [g for g in st1 if g['kind'] == 'choice' and g['siblings'][0] == 'same']
        e['stage1_choice_all_same'] = dict(tables=len(same1), parts=sorted({g['si'] for g in same1}))
        diff1 = [g for g in st1 if g['siblings'][0] == 'different']
        e['stage1_different'] = dict(tables=len(diff1), parts=sorted({g['si'] for g in diff1}))
        # per part, per round
        e['per_part'] = {str(si): dict(Counter(f"{g['kind']}_t{g['t']}" for g in gs if g['si'] == si)) for si in e['parts']}
        e['per_part_detail'] = {str(si): dict(
            tid=next(g['tid'] for g in gs if g['si'] == si),
            scores_by_stage={str(t): dict(Counter(g['eval'][3] for g in gs if g['si'] == si and g['t'] == t)) for t in (1, 2, 3)},
            histories=sorted({f"{g['kind']}{g['j']}" for g in gs if g['si'] == si}),
            round1_choices=sorted({str(g['choice_dict']) for g in gs if g['si'] == si}))
            for si in e['parts']}
        # new gains: a gain at stage t whose assignment prefix is a gain at no earlier stage of the same history
        gain_keys = {(g['si'], g['kind'], g['j'], g['t'], g['laws']) for g in gs}
        nb_at = {}
        for h in hist:
            if h['si'] in {g['si'] for g in gs}:
                nb_at[(h['si'], h['kind'], h['j'])] = [n - h['n_at'][0] for n in h['n_at']]
        new = []
        for g in gs:
            nbs = nb_at[(g['si'], g['kind'], g['j'])]
            if not any((g['si'], g['kind'], g['j'], tt, g['laws'][:nbs[tt]]) in gain_keys for tt in range(1, g['t'])):
                new.append(g)
        e['new_gains_by_stage'] = dict(Counter(g['t'] for g in new))
        e['new_gains_later_stages'] = dict(Counter(
            f"t{g['t']} | {g['siblings'][0]} | {','.join(r['law'] + '@r' + str(r['round']) for r in sorted(g['reread'], key=lambda r: (r['round'], r['birth'])))}"
            f" | multi-input nae {sum(1 for m in g['multi_input'] if m['law'] == 'nae')} | {g['eval'][3]}" for g in new if g['t'] > 1))
        e['new_gains_later_parts'] = len({g['si'] for g in new if g['t'] > 1})
        # cross tables by stage: (round-1 sibling class, laws of the re-reading births, score), and by kind
        e['by_stage'] = {}
        for t in (1, 2, 3):
            gt = [g for g in gs if g['t'] == t]
            e['by_stage'][str(t)] = dict(
                tables=len(gt), parts=len({g['si'] for g in gt}),
                by_kind=dict(Counter(g['kind'] for g in gt)),
                siblings_laws_score=dict(Counter(f"{g['siblings'][0]} | {','.join(r['law'] for r in sorted(g['reread'], key=lambda r: (r['round'], r['birth'])))}"
                                                 f" | {g['eval'][3]}" for g in gt)),
                reread_fresh=dict(Counter(','.join(str(r['fresh']) for r in g['reread']) for g in gt)),
                nae_reread=dict(Counter(sum(1 for r in g['reread'] if r['law'] == 'nae') for g in gt)),
                nae_multi_input=dict(Counter(sum(1 for m in g['multi_input'] if m['law'] == 'nae') for g in gt)),
                scores=dict(Counter(g['eval'][3] for g in gt)))
        G[arm] = e
    out['gains'] = G
    # ---- predictions ----
    U, Mx = G['uniform'], G['mixed']
    P = {}
    P['P1'] = dict(uniform_round1_gain_tables=U['stage1']['tables'], parts=U['parts_round1'],
                   fails=U['stage1']['tables'] == 0)
    P['P2'] = dict(uniform_round1_gain_tables_conventions=U['stage1_conventions']['tables'],
                   parts=U['stage1_conventions']['parts'], fails=U['stage1_conventions']['tables'] > 0,
                   beside_choice_histories_all_same=U['stage1_choice_all_same'])
    bad3 = [si for arm in ('uniform', 'mixed') for si in G[arm]['parts']
            if not (stage0[si][0] and stage0[si][1] and stage0[si][3] == '2')]
    P['P3'] = dict(gaining_parts=sorted(set(U['parts']) | set(Mx['parts'])), not_hidden_at_2=sorted(set(bad3)),
                   fails=bool(bad3))
    P['P4'] = dict(liftable=len(lift), liftable_with_round1_gain=len(set(lift) & set(Mx['parts_round1'])),
                   liftable_without=Mx['liftable_without_round1_gain'], other_parts_gaining=Mx['parts_other'],
                   fails=bool(Mx['liftable_without_round1_gain']) or bool(Mx['parts_other']))
    out['predictions'] = P
    # ---- smallest gain of each arm ----
    out['smallest'] = {}
    for arm in ('uniform', 'mixed'):
        gs = [g for g in gains if g['arm'] == arm]
        if not gs:
            out['smallest'][arm] = None
            continue
        g = min(gs, key=lambda g: (g['knots_n'], g['D'], Fraction(g['eval'][3]), g['pos'], g['kind'], g['j'], g['laws']))
        out['smallest'][arm] = smallest_in_full(g)
    return out


def smallest_in_full(g):
    h, ix, ch, (stars, laws, names, obs) = qcen.history_by_key(g['si'], g['kind'], g['j'])
    nf = len(stars)
    t = g['t']
    n = h['n_at'][t]
    row = np.array([int(c) for c in g['laws']], dtype=np.int8)[None, :]
    laws_all = list(laws) + [qcen.CH3[int(v)] for v in row[0]]
    T = bc.stage_tables(h['stars'], laws, nf, n, row, obs, choices=qcen.CH3)[0]
    ev = cs.Eval()
    e = ev.run(T[None, :])[0]
    T0 = bc.stage_tables(stars, laws, nf, nf, np.zeros((1, 0), np.int8), obs, choices=qcen.CH3)[0]
    e0 = ev.run(T0[None, :])[0]
    holders = Counter(d for s in stars for d in s)
    births = []
    for rt in range(t):
        for i, b in enumerate(h['births'][rt]):
            k = nf + sum(len(x) for x in h['births'][:rt]) + i
            births.append(dict(round=rt + 1, index=i, parents=[qcen.knots_text([h['stars'][p]], [laws_all[p]], names)[0]
                                                               for p in b['parents']],
                               took=[qcen.name_of(names, d) for d in b['inputs']],
                               shared=(qcen.name_of(names, b['shared']) if b['reread'] else None),
                               fresh=[qcen.name_of(names, d) for d in h['stars'][k][len(b['inputs']):]],
                               law=laws_all[k], knot=qcen.knots_text([h['stars'][k]], [laws_all[k]], names)[0]))
    knots = qcen.named_knots(h['stars'][:n], laws_all[:n], names)
    fc = cs.full_check(knots)
    Jt = cs.joint_from_table(T)
    out = dict(arm=g['arm'], si=g['si'], tid=g['tid'], mask=g['mask'], kind=g['kind'], j=g['j'], choice=g['choice'],
               choice_dict=g['choice_dict'], t=t, knots_n=n, D=h['D_at'][t], laws=g['laws'],
               start=qcen.knots_text(stars, laws, names),
               start_holders=dict(loose=[names[d] for d in range(len(names)) if holders[d] == 1],
                                  shared=[names[d] for d in range(len(names)) if holders[d] >= 2]),
               stage0=dict(hidden=bool(e0[0] and e0[1]), exact=cs.frac(e0[3]), float=e0[2]),
               births=births, stage_knots=qcen.knots_text(h['stars'][:n], laws_all[:n], names),
               table=[int(v) for v in T], eval=dict(hidden_A=e[0], hidden_B=e[1], float=e[2], exact=cs.frac(e[3])),
               full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']), change=str(fc['change']),
                                     words=fc['words'], distinctions_finished=fc['distinctions_finished'],
                                     joint_equals_table=all(np.array_equal(fc['J'][k], Jt[k]) for k in Jt)),
               control=g.get('control', {}).get('eval'), control_excess=g.get('control', {}).get('excess'))
    if t == 1:
        cst = qcen.control_stars(h, n, nf)
        Tc = bc.stage_tables(cst, laws, nf, n, row, obs, choices=qcen.CH3)[0]
        ec = ev.run(Tc[None, :])[0]
        fcc = cs.full_check(qcen.named_knots(cst, laws_all[:n], names))
        out['control_full_enumeration'] = dict(hidden=fcc['hidden'], score=str(fcc['score']),
                                               table_eval=[ec[0], ec[1], ec[2], cs.frac(ec[3])],
                                               knots=qcen.knots_text(cst, laws_all[:n], names))
    return out


# ======================================================================================================================
def report_gates():
    g = {}
    off = gates('gate_off_')
    g['off'] = dict(runs=len(off), ok=all(v['ok'] for v in off.values()),
                    by_run={k: dict(counts=v['counts'], mismatches=len(v['mismatches'])) for k, v in off.items()})
    for name in ('parts500', 'reduction', 'addedknot', 'verify', 'stages'):
        runs = {k: v for k, v in gates(f'gate_{name}').items()}
        if runs:
            g[name] = dict(runs=len(runs), ok=all(v['ok'] for v in runs.values()), counts=add_counts(runs.values()),
                           failures=sum(len(v.get('failures', [])) for v in runs.values()))
    for name in ('extension', 'scorer', 'stalled'):
        v = gate(f'gate_{name}')
        if v is not None:
            g[name] = {k: v[k] for k in v if k not in ('rows',)}
    return g


def report_extra():
    """Numbers read after the results (deviations B): the known values on the ten parts, where the parts that do not
    gain stay, holder growth in (b), the operator test's first failing step ordinary -> Q, and one closing case."""
    X = {}
    hist = jl('census_hist_c_*.jsonl.gz')
    parts = {p['si']: p for p in jl('census_parts_c_*.jsonl.gz')}
    lift = qcen.liftable_parts()
    ten = {si for si in lift if 135 <= lift[si]['tid'] <= 144}
    ev = cs.Eval()
    uni, par, fresh = Counter(), Counter(), Counter()
    for h in hist:
        if h['si'] not in lift or h['kind'] != 'choice':
            continue
        key = 'ten' if h['si'] in ten else 'other17'
        u = h['uniform'][0]['eval']
        uni[f"{key} | hidden={u[0] and u[1]} | {u[3]}"] += 1
        fresh[f"{key} | {h['births'][0]['n']} births | fresh {h['births'][0]['reread_fresh']}"] += 1
        hh, ix, ch, (stars, laws, names, obs) = qcen.history_by_key(h['si'], 'choice', h['j'])
        nf = len(stars)
        rows = np.array([[a, b] for a in (0, 1) for b in (0, 1)], dtype=np.int8)
        for e in ev.run(bc.stage_tables(hh['stars'], laws, nf, hh['n_at'][1], rows, obs, choices=qcen.CH3)):
            par[f"{key} | hidden={e[0] and e[1]} | {cs.frac(e[3])}"] += 1
    X['liftable_choice_histories_stage1'] = dict(uniform_both_nae=dict(uni), both_parity=dict(par),
                                                 round1=dict(fresh))
    at2 = {si for si, p in parts.items() if p['stage0_eval'][0] and p['stage0_eval'][1] and p['stage0_eval'][3] == '2'}
    best_ex, best_f, best_u = {}, {}, {}
    for h in hist:
        for s in h['stages']:
            if s['best_hidden_exact'] is not None:
                best_ex[h['si']] = max(best_ex.get(h['si'], Fraction(0)), Fraction(s['best_hidden_exact']))
            if s['best_hidden_float'] is not None:
                best_f[h['si']] = max(best_f.get(h['si'], 0.0), s['best_hidden_float'])
        for u in h['uniform']:
            if u['eval'][0] and u['eval'][1]:
                best_u[h['si']] = max(best_u.get(h['si'], 0.0), u['eval'][2])
    other_at2 = sorted(at2 - set(lift))
    below = [si for si in parts if si not in at2]
    X['parts_at_2_not_liftable'] = dict(n=len(other_at2), grow=sum(parts[si]['D0'] <= qcen.DMAX for si in other_at2),
                                        best_exact_at_grown_stages=dict(Counter(str(best_ex.get(si)) for si in other_at2)),
                                        targets=dict(sorted(Counter(parts[si]['tid'] for si in other_at2).items())))
    X['parts_below_2_or_not_hidden'] = dict(
        n=len(below), largest_hidden_float_mixed=max(best_f.get(si, 0.0) for si in below),
        largest_hidden_float_uniform=max(best_u.get(si, 0.0) for si in below),
        largest_hidden_float_stage0=max((parts[si]['stage0_eval'][2] or 0.0) for si in below
                                        if parts[si]['stage0_eval'][0] and parts[si]['stage0_eval'][1]),
        any_exact_computed=sum(1 for si in below if si in best_ex))
    X['stage0_classes'] = dict(Counter(f"hidden={p['stage0_eval'][0] and p['stage0_eval'][1]} exact={p['stage0_eval'][3]}"
                                       for p in parts.values()))
    hb = {}
    for law in ('nae', 'parity'):
        R = jl(f'draws_{law}_arm*.jsonl')
        for rule in ('QO', 'QN'):
            H = [r[rule]['holders_at'] for r in R]
            hb[f'{law}_{rule}'] = dict(
                grow_after_round_1=sum(1 for h in H if len(h) > 2 and max(h[2:]) > h[1]),
                H_last_stage=dict(sorted(Counter(h[-1] for h in H).items())),
                H_stage1=dict(sorted(Counter(h[1] for h in H if len(h) > 1).items())),
                one_more_holder_each_round_9_to_12=sum(1 for h in H if len(h) == 13
                                                       and all(h[t + 1] - h[t] == 1 for t in range(8, 12))))
        hb[f'{law}_first_failing_step_ordinary_to_QO'] = dict(Counter(
            f"{r['ordinary']['first_failing_step']}->{r['QO']['first_failing_step']}" for r in R))
        hb[f'{law}_first_failing_step_ordinary_to_QN'] = dict(Counter(
            f"{r['ordinary']['first_failing_step']}->{r['QN']['first_failing_step']}" for r in R))
    X['b_holders'] = hb
    dr = next(d for d in qlaw.lib.p3_draws() if d['arm'] == 3 and d['draw'] == 17)
    case = dict(arm=3, draw=17, stars=[list(s) for s in dr['stars']])
    for conv in ('O', 'N'):
        g = qlaw.run_ab(dr['stars'], 'parity', conv, True)
        case['Q' + conv] = dict(outcome=g.outcome, n_at=g.n_at, newborns=[list(s) for s in g.stars[len(dr['stars']):]],
                                zero_fresh=[x['zero_fresh'] for x in g.rounds])
    h = qlaw.lib.grow(dr['stars'], 'parity', qlaw.HORIZON, qlaw.CAP)
    case['ordinary'] = dict(outcome=h['outcome'], n_at=h['n_at'], first_newborns=[list(s) for s in h['stars'][5:9]])
    X['closing_case'] = case
    X['contracted_tables'] = sum(p['cache_tables'] for p in parts.values())
    X['controls'] = dict(Counter(f"{g['arm']} | hidden={g['control']['eval'][0] and g['control']['eval'][1]} | "
                                 f"{g['control']['eval'][3]}" for g in jl('census_gains_c_*.jsonl.gz') if 'control' in g))
    X['other_at2_uniform_evals'] = dict(Counter(f"hidden={u['eval'][0] and u['eval'][1]} | {u['eval'][3]}"
                                                for h in hist if h['si'] in set(other_at2) for u in h['uniform']))
    X['other_at2_law_modes'] = dict(Counter(h['law_mode'] for h in hist if h['si'] in set(other_at2)))
    bnd = {}
    for law in ('nae', 'parity'):
        R = jl(f'draws_{law}_arm*.jsonl')
        for rule in ('QO', 'QN'):
            bnd[f'{law}_{rule}'] = dict(sorted(Counter(r[rule]['births'][-1] for r in R if r[rule]['growth_kind'] == 'bounded'
                                                       and r[rule]['outcome'] == 'horizon').items()))
    X['bounded_draws_births_in_round_12'] = bnd
    R = jl('draws_parity_arm*.jsonl')
    X['parity_draws_without_reread'] = {rule: dict(n=sum(1 for r in R if not any(r[rule]['reread_births'])), ends=dict(Counter(
        f"{r[rule]['outcome']} at round {r[rule]['rounds']}" for r in R if not any(r[rule]['reread_births']))))
        for rule in ('QO', 'QN')}
    src = qlaw.lib.recorded_sources()
    rr_d = {}
    for name in ('archive_start-00', 'archive_start-04'):
        for conv in ('O', 'N'):
            g = qlaw.QGrowth(src[name], 'nae', conv)
            per = []
            while g.outcome is None and len(g.rounds) < qlaw.HORIZON:
                r = g.plan(max_births=qlaw.CAP - len(g.stars))
                if r.status != 'extend':
                    break
                per.append([int(row[-1]) for row, prow in zip(r.inputs, r.paid) if any(prow)])
                g.apply(r)
            rr_d[f'{name}_{conv}'] = dict(reread_distinctions_per_round=per, births=g.births_per_round(),
                                          holders_at=g.holders_at)
    X['a_archive_reread_distinctions'] = rr_d
    # the new stage-3 gains: part 3072 under O, laws even, even, even, not-all-equal against the stage-1 tables
    h, ix, ch, (stars, laws, names, obs) = qcen.history_by_key(3072, 'O', 0)
    nf = len(stars)
    T1 = {lw: bc.stage_tables(h['stars'], laws, nf, h['n_at'][1], np.array([lw], dtype=np.int8), obs,
                              choices=qcen.CH3)[0] for lw in ((0, 2), (2, 0))}
    tie = {}
    for lw in ((0, 0, 0, 2), (1, 0, 0, 2), (0, 1, 0, 2), (0, 0, 1, 2), (1, 1, 1, 2)):
        T3 = bc.stage_tables(h['stars'], laws, nf, h['n_at'][3], np.array([lw], dtype=np.int8), obs, choices=qcen.CH3)[0]
        e = ev.run(np.array([int(v) for v in T3])[None, :])[0]
        tie[''.join(map(str, lw))] = dict(score=cs.frac(e[3]), hidden=bool(e[0] and e[1]),
                                          proportional_to_stage1_second_sibling_nae=bool(bc.proportional(T3, T1[(0, 2)])),
                                          proportional_to_stage1_first_sibling_nae=bool(bc.proportional(T3, T1[(2, 0)])))
    X['stage3_tie_part3072_O'] = dict(births=[[dict(inputs=[qcen.name_of(names, d) for d in b['inputs']], fresh=b['fresh'],
                                                    reread=b['reread']) for b in rd] for rd in h['births']], laws=tie)
    return X


def main():
    S = dict(preregistration_sha256=qlaw.sha256(PREREG), rlaw_sha256=qlaw.sha256(qlaw.A_EXP / 'rlaw.py'),
             reused_sha256={p: qlaw.sha256(qlaw.ROOT / p) for p in (
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/rlaw.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/words.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/cstudy.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/arm1.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/gates.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/common.py',
                 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/verify_excess.py',
                 'experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test/lib.py',
                 'experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py',
                 'docs/prompts/missed_leads_checks/finished_weighting_chsh.py')})
    S['a_sources'] = report_sources()
    S['b_draws'], S['P5'], S['P6'] = report_draws()
    S['c_census'] = report_census()
    S['G'] = report_gates()
    S['extra'] = report_extra()
    # stalls of rule Q anywhere (G: no knot born under rule Q is ever short)
    st = []
    for src, d in S['a_sources'].items():
        for rule in ('QO', 'QN'):
            if d[rule]['outcome'] == 'stall':
                st.append(('a', src, rule, d[rule]['stall_shortages']))
    for law in ('nae', 'parity'):
        for rule in ('QO', 'QN'):
            for x in S['b_draws'][law][rule]['stalls']:
                st.append(('b', law, rule, x))
    st += [('c', x) for x in S['c_census']['histories']['stalls']]
    S['G']['born_short'] = dict(stalls=st, n=len(st))
    (ART / 'summary.json').write_text(json.dumps(S, indent=1, default=str) + '\n')
    print(json.dumps(dict(P=S['c_census']['predictions'], P5=S['P5'], P6=S['P6']), default=str)[:4000])


if __name__ == '__main__':
    main()
