"""Collect the results of REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001 into summary.json (counts, verdict inputs, the
smallest finds written out in full).  Reads the outputs of build_targets.py, gates.py, sign_check.py, grow_t1.py (both
versions), verify_excess.py, t2.py, verify_t2.py and seven_reasons.py (.jsonl or .jsonl.gz).
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import glob
import gzip
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

A = c.ART


def jl(pattern):
    out = []
    for f in sorted(glob.glob(str(A / pattern)) + glob.glob(str(A / (pattern + '.gz')))):
        op = gzip.open if f.endswith('.gz') else open
        with op(f, 'rt') as fh:
            out += [json.loads(l) for l in fh]
    return out


S = {}
S['build'] = json.loads((A / 'build_summary.json').read_text())
g = json.loads((A / 'gates.json').read_text())
S['gates'] = {k: ({kk: vv for kk, vv in v.items() if kk != 'failures'} if isinstance(v, dict) else v) for k, v in g.items()}
sc = json.loads((A / 'sign_check.json').read_text())
S['sign_check'] = {k: v for k, v in sc.items() if k not in ('brute_force_confirmation',)}
S['sign_check']['brute_force_confirmation'] = sc.get('brute_force_confirmation')
targets = {t['tid']: t for t in json.loads((A / 'targets.json').read_text())}

for tag in ('c2', 'c3'):
    L = jl(f't1_{tag}_[0-9]*.jsonl')
    H = jl(f't1_hits_{tag}_*.jsonl')
    st = [s for r in L for s in r['stages']]
    grown = [s for s in st if s['t'] >= 1]
    newh = [r for r in L if not r['stage0_excess'] and any(s['new_excess'] for s in r['stages'])]
    reach = [r for r in L if not r['stages'][0]['proportional'] and any(s['proportional'] for s in r['stages'][1:])]
    V = jl(f'verify_excess_{tag}_*.jsonl')
    Vexc = [v for v in V if isinstance(v.get('full_enumeration'), dict)]
    Vnot = [v for v in V if isinstance(v.get('full_enumeration'), str)]
    # rows not enumerated because they were done in a later run: drop the "not run" note if the same row was enumerated
    done = {(v['si'], v['t'], tuple(v['newborn_laws'])) for v in Vexc}
    Vnot = [v for v in Vnot if (v['si'], v['t'], tuple(v['newborn_laws'])) not in done]
    same = {(v['si'], v['t'], tuple(v['newborn_laws'])) for v in V if v.get('same_structure_as_target')}
    same_hist = {v['si'] for v in V if v.get('same_structure_as_target')}
    best_grown_new = max(((s['best_hidden_float'], s['best_hidden_exact'], r['si']) for r in L if not r['stage0_excess']
                          for s in r['stages'] if s['t'] >= 1 and s['best_hidden_float'] is not None), default=None)
    best_grown_any = max(((s['best_hidden_float'], s['best_hidden_exact'], r['si']) for r in L
                          for s in r['stages'] if s['t'] >= 1 and s['best_hidden_float'] is not None), default=None)
    smallest = min(((r['n_at'][s['t']], s['D'], r['si'], r['tid'], r['mask'], s['t']) for r in newh for s in r['stages']
                    if s['new_excess']), default=None)
    seven = [r for r in L if 'seven' in targets[r['tid']]['tags']]
    S[f't1_{tag}'] = dict(
        histories=len(L), stages=len(st), grown_stages=len(grown), tables=sum(s['tables'] for s in st),
        grown_tables=sum(s['tables'] for s in grown), modes=dict(Counter(r['mode'] for r in L)),
        outcomes=dict(Counter(r['outcome'] for r in L)), newborns_max=max(r['newborns'] for r in L),
        histories_with_growth=sum(1 for r in L if len(r['n_at']) > 1),
        support_shrinks=sum(r['support_shrinks'] for r in L), support_changes=sum(r['support_changes'] for r in L),
        starts_support_equal_to_target=sum(1 for r in L if r['stages'][0]['support_equal']),
        stage_tables_support_equal=sum(s['support_equal'] for s in st),
        proportional_tables=sum(s['proportional'] for s in st),
        proportional_tables_grown=sum(s['proportional'] for s in grown),
        starts_already_proportional=sum(1 for r in L if r['stages'][0]['proportional']),
        histories_reaching_only_by_growth=len(reach), targets_reached_only_by_growth=len({r['tid'] for r in reach}),
        reaching_histories_start_without_excess=sum(1 for r in reach if not r['stage0_excess']),
        grown_stages_that_are_the_target=len(same), histories_growing_the_target_itself=len(same_hist),
        targets_grown_exactly=len({v['tid'] for v in V if v.get('same_structure_as_target')}),
        starts_with_excess=sum(1 for r in L if r['stage0_excess']),
        excess_tables=sum(s['excess'] for s in st),
        grown_tables_from_excess_starts=sum(s['tables'] for r in L if r['stage0_excess'] for s in r['stages'] if s['t'] >= 1),
        grown_excess_tables_from_excess_starts=sum(s['excess'] for r in L if r['stage0_excess'] for s in r['stages'] if s['t'] >= 1),
        new_excess_tables=sum(s['new_excess'] for s in st), histories_with_new_excess=len(newh),
        targets_with_new_excess=len({r['tid'] for r in newh}), smallest_new_excess=smallest,
        best_hidden_grown_from_starts_without_excess=best_grown_new, best_hidden_grown_any=best_grown_any,
        verified_by_full_enumeration=len(Vexc),
        verified_all_hidden_excess=all(v['full_enumeration']['hidden'] and Fraction(v['full_enumeration']['score']) > 2 for v in Vexc),
        verified_all_agree=all(v['full_enumeration']['joint_equals_table'] and v['full_enumeration']['score_equals_contraction']
                               for v in Vexc),
        separate_enumeration_checked=sum(1 for v in Vexc if 'separate_enumeration_equal' in v),
        separate_enumeration_equal=sum(1 for v in Vexc if v.get('separate_enumeration_equal')),
        not_enumerated=Counter(v['D'] for v in Vnot), verified_D=Counter(v['D'] for v in Vexc),
        new_excess_by_score=dict(Counter(v['full_enumeration']['score'] for v in Vexc)),
        seven_knot_starts=len(seven), seven_knot_support_equal=sum(1 for r in seven if r['stages'][0]['support_equal']),
        seven_knot_any_excess=sum(1 for r in seven if any(s['excess'] for s in r['stages'])),
        seven_knot_best_hidden=max((s['best_hidden_float'] for r in seven for s in r['stages'] if s['best_hidden_float'] is not None),
                                   default=None))
    # the smallest new excess in full
    if smallest:
        si, t = smallest[2], smallest[5]
        rows = [v for v in Vexc if v['si'] == si and v['t'] == t]
        r = [x for x in L if x['si'] == si][0]
        S[f't1_{tag}']['smallest_new_excess_in_full'] = dict(
            target=targets[r['tid']]['knots'], target_score=targets[r['tid']]['recorded_score'],
            start=[k for k in rows[0]['knots'][:r['founders']]] if rows else None, n_at=r['n_at'], D_at=r['D_at'],
            births=r['births'], stage=t, stages=r['stages'], rows=rows)

for tag in ('c2', 'c3'):
    tg = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(A / f't2_targets_{tag}_*.json')))]
    dr = json.loads((A / f't2_draws_{tag}_0-1000000.json').read_text())
    keys = ('stages', 'distinct_structures', 'stages_with_a_tie', 'stages_with_two_disjoint_ties',
            'stages_with_two_ties_no_common_knot', 'choices_tested', 'choices_ordered', 'hidden', 'excess', 'sym_checked',
            'sym_equal', 'closing_stages')
    bt = Counter()
    for d in tg:
        bt.update(d['by_t'])
    vt = json.loads((A / f'verify_t2_{tag}.json').read_text())
    best = max(((d['best_hidden'], d['best_hidden_exact']) for d in tg if d['best_hidden'] is not None), default=None)
    S[f't2_{tag}'] = dict(targets={k: sum(d.get(k, 0) for d in tg) for k in keys}, targets_by_t=dict(bt),
                          draws={k: dr.get(k) for k in keys + ('draws', 'funded', 'by_t', 'closing_implied_constant',
                                                               'parity_rule_same_as_nae', 'parity_rule_compared')},
                          best_hidden=best, verify={k: v for k, v in vt.items() if k != 'rows'})
S['seven_reasons'] = {k: v for k, v in json.loads((A / 'seven_reasons.json').read_text()).items()}
(A / 'summary.json').write_text(json.dumps(S, indent=1, default=str))
print(json.dumps({k: v for k, v in S.items() if k not in ('seven_reasons',)}, indent=1, default=str)[:20000])
