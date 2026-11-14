"""Compute TOP's counts/predictions; missing runner cases remain pending."""
from __future__ import annotations
from collections import Counter,defaultdict
import argparse
import json
from pathlib import Path
import time
import top_data as data


def rate(rows, flags):
    yes=[r for r,f in zip(rows,flags) if f is True]
    unknown=[r for r,f in zip(rows,flags) if f is None]
    w=sum(r['weight'] for r in rows)
    return dict(families=len(rows),success=len(yes),share=len(yes)/len(rows) if rows else None,
                unknown=len(unknown),draw_weight=w,success_weight=sum(r['weight'] for r in yes),
                weight_share=sum(r['weight'] for r in yes)/w if w else None,
                unknown_weight=sum(r['weight'] for r in unknown),
                share_upper=(len(yes)+len(unknown))/len(rows) if rows else None,
                weight_share_upper=(sum(r['weight'] for r in yes)+sum(r['weight'] for r in unknown))/w if w else None)


def load_attempts(path):
    rows={}
    if path.exists():
        with path.open() as stream:
            for line in stream:
                x=json.loads(line);rows[x['case']]=x
    return rows


def verdict(failures,unknown):
    return 'fail' if failures else 'pending' if unknown else 'pass'


def summarize(out='census_run'):
    started=time.monotonic()
    cat=json.loads((data.HERE/'catalog.json').read_text())
    records=load_attempts(data.HERE/out/'results.jsonl')
    flags,two,forget={}, {}, {}
    failed_records=[]
    for case,rec in records.items():
        if rec['status']!='ok':
            failed_records.append(dict(case=case,status=rec['status'],error=rec.get('error')));continue
        r=rec['result'];kind=r['kind']
        (flags if kind=='flags' else two if kind=='two_block' else forget)[r['key']]=r
    families=[]
    for row in cat['rows']:
        key=row['key'];f=flags.get(key);t=two.get(key)
        item={k:row[k] for k in ('key','key_sha256','in_scope','stratum','weight','final_verdict','exception_family','R')}
        item['pinning']=f if f else dict(complete=False,pending=True,residues=[],
            plain_pinned=dict(some_residue=None,every_residue=None),bond_pinned=dict(some_residue=None,every_residue=None))
        item['two_block']=t if t else dict(complete=False,selected=key in cat['selected_two_block'],pending=key in cat['selected_two_block'])
        families.append(item)
    groups=defaultdict(list)
    for row in families:
        groups[('in' if row['in_scope'] else 'out',row['stratum'],row['final_verdict'])].append(row)
    tables=[]
    for (scope,stratum,final),rows in sorted(groups.items()):
        record=dict(scope=scope,stratum=stratum,final_verdict=final,families=len(rows),draw_weight=sum(r['weight'] for r in rows))
        for label,getter in [
            ('R_some',lambda r:r['R']['some_residue']),('R_every',lambda r:r['R']['every_residue']),
            ('plain_some',lambda r:r['pinning']['plain_pinned']['some_residue']),
            ('plain_every',lambda r:r['pinning']['plain_pinned']['every_residue']),
            ('bond_some',lambda r:r['pinning']['bond_pinned']['some_residue']),
            ('bond_every',lambda r:r['pinning']['bond_pinned']['every_residue'])]:
            record[label]=rate(rows,[getter(r) for r in rows])
        tables.append(record)
    residue_tables=[]
    for (scope,stratum,final),rows in sorted(groups.items()):
        for predicate in ('R_applies','plain_pinned','bond_pinned'):
            values=[(r,s[predicate]) for r in rows for s in r['pinning']['residues']]
            residue_tables.append(dict(scope=scope,stratum=stratum,final_verdict=final,predicate=predicate,
                **rate([r for r,f in values],[f for r,f in values]),
                complete_families=sum(r['pinning']['complete'] for r in rows),
                note='denominator counts Q residues; draw weight repeated once per residue'))
    R_residue_tables=[]
    for (scope,stratum,final),rows in sorted(groups.items()):
        values=[(r,s['applies']) for r in rows for s in r['R']['residues']]
        R_residue_tables.append(dict(scope=scope,stratum=stratum,final_verdict=final,
            **rate([r for r,f in values],[f for r,f in values]),
            note='READ carried-set residues, with compatible Q phases listed per family'))
    bounded_without_R=defaultdict(list)
    for row in families:
        residues=[]
        for r in row['R']['residues']:
            if r['applies'] is not False:continue
            bounded_Q=[q for q,u in zip(r['Q_residues'],r['U']) if isinstance(u,int)]
            if row['final_verdict'].startswith('bounded_') or bounded_Q:
                residues.append(dict(residue=r['residue'],s_mod_period=r['s_mod_period'],
                                     bounded_Q_residues=bounded_Q,U=r['U'],
                                     certificate=row['final_verdict'] if row['final_verdict'].startswith('bounded_') else 'partial_window_residues'))
        if residues:
            group='O' if row['stratum']=='O' else 'nine_exception_families' if row['exception_family'] else 'others'
            bounded_without_R[('in:' if row['in_scope'] else 'out:')+group].append(dict(
                key=row['key'],key_sha256=row['key_sha256'],weight=row['weight'],final_verdict=row['final_verdict'],residues=residues))
    growers=[r for r in families if r['final_verdict']=='growing']
    R_bad=[r['key'] for r in growers if r['R']['some_residue'] is True]
    R_unknown=[r['key'] for r in growers if r['R']['some_residue'] is None]
    bond_bad=[r['key'] for r in growers if r['pinning']['bond_pinned']['some_residue'] is True]
    bond_unknown=[r['key'] for r in growers if r['pinning']['bond_pinned']['some_residue'] is None]
    plain_bad=[r['key'] for r in growers if r['pinning']['plain_pinned']['some_residue'] is True]
    # Capped counts as not pinned in frozen T1; absent computations remain pending.
    T1_pending=[r['key'] for r in growers if r['pinning'].get('pending')]
    order=[r for r in families if r['in_scope'] and r['stratum']=='O']
    T2_bad=[r['key'] for r in order if not r['pinning'].get('pending') and r['pinning']['bond_pinned']['every_residue'] is not True]
    T2_pending=[r['key'] for r in order if r['pinning'].get('pending')]
    undecided=[r for r in families if r['in_scope'] and r['final_verdict']=='undecided']
    T3_good=[r['key'] for r in undecided if r['two_block'].get('complete') and all(isinstance(s['U2'],int) for s in r['two_block']['residues'])]
    T3_pending=[r['key'] for r in undecided if r['two_block'].get('pending')]
    T3_status='pass' if len(T3_good)>=10 else 'pending' if T3_pending else 'fail'
    upper_bad=[k for k,v in two.items() if v['one_block_gate']['passed'] is False]
    upper_unknown=[k for k in cat['selected_two_block'] if k not in two or two[k]['one_block_gate']['passed'] is None]
    forgetting_bad=[k for k,v in forget.items() if v['forgetting_gate']['passed'] is False]
    forgetting_unknown=[r['key'] for r in cat['forgetting_controls'] if r['key'] not in forget or forget[r['key']]['forgetting_gate']['passed'] is None]
    gates=dict(R=dict(status=verdict(R_bad,R_unknown),violations=R_bad,unknown=R_unknown),
        bond_pinning=dict(status=verdict(bond_bad,bond_unknown),violations=bond_bad,unknown=bond_unknown),
        upper_comparison=dict(status=verdict(upper_bad,upper_unknown),violations=upper_bad,unknown=upper_unknown),
        forgetting=dict(status=verdict(forgetting_bad,forgetting_unknown),violations=forgetting_bad,unknown=forgetting_unknown),
        brute_force=dict(status='skipped_ambiguity',question=cat['brute_selection_ambiguity'],families_selected=0))
    overall='fail' if any(g['status']=='fail' for g in gates.values()) else 'inconclusive' if any(g['status']!='pass' for g in gates.values()) else 'pass'
    hiding,possible_hiding=[],[]
    for row in families:
        if row['final_verdict']!='undecided':continue
        p,t=row['pinning'],row['two_block']
        g2=p.get('G2',{})
        if p.get('complete') and not g2.get('certified') and p['bond_pinned']['some_residue'] is False:
            target=dict(key=row['key'],in_scope=row['in_scope'],G2_complete=g2.get('complete'),G2_cap=g2.get('cap'),
                        no_bond_pinning=True,two_block_complete=t.get('complete'))
            if t.get('complete') and all(not isinstance(a['U2'],int) for a in t['residues']):hiding.append(target)
            elif not t.get('complete'):possible_hiding.append(target)
    expected=len(cat['rows'])+len(cat['selected_two_block'])+len(cat['forgetting_controls'])
    summary=dict(schema_version=1,scope_id='TOP-INFO-20261114-001A',complete=len(records)==expected and not failed_records,
        population=dict(families=len(families),in_scope=sum(r['in_scope'] for r in families),out_of_scope=sum(not r['in_scope'] for r in families),
                        final_counts=dict(Counter(('in:' if r['in_scope'] else 'out:')+r['final_verdict'] for r in families))),
        execution=dict(expected_cases=expected,finished_attempt_cases=len(records),flags=len(flags),two_block=len(two),forgetting=len(forget),
                       pending_cases=expected-len(records),failed_records=failed_records,run_directory=out),
        by_stratum_and_verdict=tables,Q_residue_cross_tabs=residue_tables,R_residue_cross_tabs=R_residue_tables,
        bounded_residues_without_R=dict(bounded_without_R),
        bounded_residues_without_R_counts={k:dict(families=len(v),weight=sum(x['weight'] for x in v),residues=sum(len(x['residues']) for x in v)) for k,v in bounded_without_R.items()},
        G=dict(status=overall,checks=gates),
        T1=dict(status=verdict(plain_bad,T1_pending),growers=len(growers),pinned_keys=plain_bad,pending_keys=T1_pending,
                capped_as_not_pinned=sum(not r['pinning']['complete'] and not r['pinning'].get('pending') for r in growers)),
        T2=dict(status=verdict(T2_bad,T2_pending),order_families=len(order),failure_keys=T2_bad,pending_keys=T2_pending),
        T3=dict(status=T3_status,threshold=10,undecided_in_scope=len(undecided),newly_bounded=len(T3_good),newly_bounded_keys=T3_good,pending_keys=T3_pending),
        hiding=dict(families=hiding,pending_two_block=possible_hiding,count=len(hiding),qualification='G2 not certified is the requested operational screen, not proof of a non-rectangular long product when G2 is capped; no two-block bond means none through size 6'),
        timings=dict(summary_seconds=time.monotonic()-started,
                     runner_case_seconds=sum((x.get('result') or {}).get('metrics',{}).get('seconds',0) for x in records.values()),
                     maximum_worker_rss_bytes=max(((x.get('result') or {}).get('metrics',{}).get('process_peak_rss_bytes',0) for x in records.values()),default=0)),
        ambiguities=[cat['brute_selection_ambiguity']],
        nonclaims=['Empirical computations do not discharge proof obligations.','No canonical test or definition changed.'])
    data.dump('results.json',dict(schema_version=1,scope_id='TOP-INFO-20261114-001A',complete=summary['complete'],families=families))
    data.dump('summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('population','execution','bounded_residues_without_R_counts','timings')},indent=2))
    print('G',overall,'T1',summary['T1']['status'],'T2',summary['T2']['status'],'T3',T3_status)
    write_report(summary)
    return summary




def write_report(summary):
    e=summary['execution'];pop=summary['population'];tim=summary['timings']
    root='experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex'
    lines=[
        '# Is reading the whole rule: census computation', '',
        'Scope: ticket `TOP-INFO-20261114-001A`, experiment `E001_rule_check`. All authored files and outputs stay in this CODEX directory. Source data and implementations are read in place. No Git command, publication, tracker change, external research, or definition change was performed.', '',
        '## Current result', '',
        'Check 1 is computed for the full supplied population from READ-RULE’s retained exact tie summaries, using the theorem’s existential quantifier. Checks 2–4 are implemented; the shared-runner smoke results below are partial and do not establish full census predictions. The full run is prepared and unlaunched for the thread.', '',
        f"Final population: {pop['in_scope']} in scope and {pop['out_of_scope']} out of scope. In scope, 5,067 are window-bounded, seven more have a bounded path-DP certificate, 632 are growing, and 83 are undecided. Out of scope, 129 are window-bounded and 46 undecided. This resolves READ-RULE’s earlier 90-versus-83 ambiguity by using the supplied final path certificates.", '',
        '## What was built', '',
        '- `top_data.py` reuses READ’s byte-offset index and streamed CARRY SHA-256 receipt, verifies file size/mtime, reads one original record at a time, and applies the seven path-DP bounded certificates. `catalog.json` stores metadata and selections, without copying source relations.',
        '- R uses “some repeating state in which the knot’s position is carried and the exception fails.” Existing `any_state_survives` flags supply the full check; `checks.py` also recomputes the flags from exact projections on each completed smoke family.',
        '- Plain pinning compares the exact joint projection count with the product of its two marginal counts. Bond-pinning searches shattered subsets on both sides, without the size-six restriction. Searching maximal shattered sides suffices for existence: extending a witnessing side preserves non-fullness of the union. It does not infer bond-pinning from plain correlation.',
        '- `two_block.py` retains all main-block distinctions in the transfer state and identity partition, treats word depth zero as the same copy when main is S, and uses whole-block contexts at each direct initial call. Later transfer composition is CARRY’s unchanged operation. Every candidate bond contains a main port and an end-own distinction; all proper one-variable deletions must be full.',
        '- `two_block_brute.py` independently unfolds the raw syntax through the target’s children and enumerates its exact CNF projection. It also checks independent bond minima and recovers CARRY’s original port-only projection. It is callable for any supplied family; it does not choose the unspecified official 30-family sample.',
        '- `job.py` and `summarize.py` preserve caps and missing cells, compute cross-tabs, both family and draw-weight shares, G and T1–T3, and the requested hiding screen. Full key/residue lists are in the JSON outputs.', '',
        '## Frozen execution and controls', '',
        'The full job has 5,964 pinning cases, 961 two-block cases (every 761 not-already-bounded family, plus the first 200 bounded families in sha256("TOP:" + key) order), and the first 100 certified-forgetting families in the same order: 7,025 cases. Both scope populations are included. Selection code is independently checked by `verify.py`.', '',
        'Use `.venv/bin/python -B`. The prepared runner has one worker, a 3 GB case ceiling and 5 GB total ceiling, retaining headroom below the requested approximate 8 GB total. The foreground runner uses a parent and one worker. Numerical libraries have one thread. Internal inherited limits are 585 seconds and 2,800,000,000 bytes per case; Q has the same 200,000 stored-state/2,000-level caps and bond size at most six. Independent unfolding retains CARRY’s caps of 15,000 variables, 100,000 clauses, 25,000 copies and 1,048,576 projection rows.', '',
        'Depth `s` in the code is CARRY’s word length; absolute copy depth is `s + wrapper`. The forgetting comparison is therefore `2 + floor(s/r)`, equivalently `2 + floor((absolute_depth-wrapper)/r)`. Overlapping eventual congruences and available finite prefix cells are compared for `U2 <= U` whenever both are finite. A finite repeating U2 is checked at a sufficiently late representative against the forgetting lower bound. `> 6` is an exhausted bounded search, not a finite bound or a growth proof.', '',
        'The independent pinning controls pass the advisor’s 26-state hiding example (plain pinned, no bond-pinning), full-product, opposite-pair and NAE controls, plus all 255 nonempty complement-closed relations on four distinctions against exhaustive minimal-support enumeration. See `controls.json`.', '',
        'Two implementation fixtures, a self-holding main and a wrapper with multiple direct entries, are recorded in `validation.json`; all 60 covered words through s=3 agree in their entire two-block projection, independent bond minimum and recovered old port-only projection. These fixtures validate implementation and do not fill the unselected official brute30 gate.', '',
        '## Computed counts', '',
        f"Runner records read from `{e['run_directory']}`: {e['finished_attempt_cases']} / {e['expected_cases']} cases ({e['flags']} pinning, {e['two_block']} two-block, {e['forgetting']} forgetting). Pending: {e['pending_cases']}. Failed runner records: {len(e['failed_records'])}.", '',
        '| Scope and stratum | Families bounded on a residue without R | Draw weight | Such residues |',
        '| --- | ---: | ---: | ---: |']
    for k,v in sorted(summary['bounded_residues_without_R_counts'].items()):
        lines.append(f"| {k} | {v['families']} | {v['weight']} | {v['residues']} |")
    lines += ['', 'The strata “O”, “nine exception families”, and “others” are disjoint. A family appears once per listed stratum, with every qualifying residue retained in `summary.json`. A partial window certificate is listed only for its bounded Q residues. READ’s carried-set residue period and the Q-window period are both retained, rather than silently identifying them.', '',
        '| Check | Status | Observed violations / failures | Remaining or unavailable |', '| --- | --- | ---: | ---: |']
    for name,g in summary['G']['checks'].items():
        lines.append(f"| G: {name} | {g['status']} | {len(g.get('violations',[]))} | {len(g.get('unknown',[])) if 'unknown' in g else 'official sample unspecified'} |")
    lines += ['',f"Overall G: **{summary['G']['status']}**. T1: **{summary['T1']['status']}**; T2: **{summary['T2']['status']}**; T3: **{summary['T3']['status']}** ({summary['T3']['newly_bounded']} of the 83 formerly undecided newly bounded on every residue; threshold 10). Missing runs are pending; actual caps count as prescribed in T1–T3.", '',
        f"Hiding screen completed matches: {summary['hiding']['count']}. Full lists and incomplete candidates are retained. G2 not certified is the requested operational criterion; when G2 is capped it does not prove a non-rectangular long product. Absence of a two-block bond refers to the search through size six.", '',
        '## Timings and validation', '',
        f"Recorded worker computation: {tim['runner_case_seconds']:.3f} seconds summed over the read runner records. Maximum recorded worker high-water RSS: {tim['maximum_worker_rss_bytes']:,} bytes. Final metadata/summary aggregation: {tim['summary_seconds']:.3f} seconds. Source-index provenance and its original streaming time are reused, not counted as new computation.", '',
        'The pinning controls took about 0.04 seconds; the two independent unfolding fixtures took about 26 seconds together. `validation.json` preserves actual timings and resource measurements. The per-case runner records retain timings, caps and memory measurements; `frozen_sources.json` binds local code and source machinery. A full job has more than ten minutes of census work and is deliberately left to the shared runner. The 20-case smoke is validation only, with its retained output available for inspection.', '',
        'Empirical checks do not discharge Theorem P′, the two-block bound, or localisation proof obligations. No mathematical theorem is inferred from an incomplete census.', '',
        '## Ambiguities', '',
        '1. **Which 30 census families and selection rule are intended for the separate brute-force gate?** The specification freezes SHA-256 ordering for the 200 bounded and 100 forgetting controls, but supplies no selection of the 30 brute families. No official sample is chosen. Only that official sample and its G component are skipped; the complete per-family independent comparison is implemented and two explicit engineering fixtures were checked.', '',
        'The prior R quantifier ambiguity is explicitly resolved by the user’s “some state” instruction. The old population discrepancy is resolved by the final path-DP certificates. READ’s conditional-product storage-cap ambiguity and undefined descriptive counterexample classifier do not affect this study. The user’s explicit `U2 <= U` comparison resolves the preregistration’s less precise “agrees” wording.', '',
        '## Thread launch commands', '',
        'The full service has not been launched and no run has been registered. From the repository root, after reviewing the retained smoke records:', '', '```sh',
        f'.venv/bin/python -B scripts/longrun.py resume --out {root}/census_run',
        f'.venv/bin/python -B scripts/longrun.py status --out {root}/census_run --json',
        f'.venv/bin/python -B scripts/longrun.py wait --out {root}/census_run',
        f'.venv/bin/python -B {root}/summarize.py --run census_run',
        f'.venv/bin/python -B {root}/verify.py', '```', '',
        'The thread handles any registration outside CODEX. Supplying the intended brute30 selection remains necessary before that official gate can be completed. Until then, even a successful full numerical run leaves G inconclusive.', '']
    (data.HERE/'REPORT.md').write_text('\n'.join(lines))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',default='census_run');a=p.parse_args();summarize(a.run)
