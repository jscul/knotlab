"""Final parse, evidence-invariant and provenance checks; no study-code access."""
from __future__ import annotations
import ast
import collections
import datetime
import hashlib
import json
import re
from pathlib import Path

ROOT=Path('/home/jscul/p-vs-np-contact-first')
HERE=ROOT/'research/TOP-INFO-20261114-001/referee-R1/codex'
PREEXISTING={'brief_codex.md','codex_last_message.md'}
PROHIBITED=('experiments/TOP-INFO-20261114-001A/',
            'proofs/TOP-INFO-20261114-001Z/')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((HERE/name).read_text())


def verify_bond(record):
    assert record['is_bond'] and record['living']
    support=record['support']
    assert len(set(support))==len(support)
    assert 0<len(record['allowed'])<2**len(support)
    assert record['endpoints_valid'] and record['every_single_deletion_full']
    assert all(d['full'] and len(d['allowed'])==2**(len(support)-1)
               for d in record['deletions'])


def source_maps(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ('sources','inputs_sha256','helpers') and isinstance(v,dict):
                yield v
            yield from source_maps(v)
    elif isinstance(obj,list):
        for v in obj:
            yield from source_maps(v)


def main():
    files=[p for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in PREEXISTING
           and p.name!='referee_validation.json']
    syntax=[]; json_files=[]; jsonl_files=[]; sources={}; changed_sources=[]
    parsed={}
    bond_checks=0
    for p in files:
        if p.suffix=='.py':
            ast.parse(p.read_text(),filename=str(p))
            compile(p.read_text(),str(p),'exec')  # no bytecode or imports
            syntax.append(p.name)
        elif p.suffix=='.json':
            obj=json.loads(p.read_text()); parsed[p.name]=obj
            json_files.append(p.name)
        elif p.suffix=='.jsonl':
            obj=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
            parsed[p.name]=obj; jsonl_files.append({'file':p.name,'records':len(obj)})
        else:
            continue
        if p.name in parsed:
            for source in source_maps(parsed[p.name]):
                for name,expected in source.items():
                    if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):
                        continue
                    q=Path(name)
                    if not q.is_absolute(): q=ROOT/q
                    relative=str(q.relative_to(ROOT))
                    assert not (q.suffix=='.py' and relative.startswith(PROHIBITED)),relative
                    # Only declared sources are read, never guessed study files.
                    if q.exists():
                        actual=digest(q)
                        sources[relative]={'expected':expected,'actual':actual}
                        if actual!=expected:
                            changed_sources.append(relative)
            if p.name.startswith('middle_') and p.suffix=='.jsonl':
                for r in parsed[p.name]:
                    for k in ('verification','endpoint_only_verification'):
                        if k in r:
                            verify_bond(r[k]);bond_checks+=1
                    if isinstance(r.get('bond'),dict) and 'verification' in r['bond']:
                        verify_bond(r['bond']['verification']);bond_checks+=1

    counts=load('counts_results.json')
    assert counts['historical_counts']=={
        'strict_complete_row':{'bounded':5072,'growing':632,'undecided':85},
        'advertised_primary_path_admission':{'bounded':5074,'growing':632,'undecided':83},
        'all_valid_primary_certificates':{'bounded':5076,'growing':632,'undecided':81}}
    assert counts['new_final_counts']=={'bounded':5085,'growing':632,'undecided':72}
    assert sum(counts['new_final_counts'].values())==5789
    assert sum(counts['new_final_weights'].values())==5853
    assert counts['advertised_split']['groups']['unavailable']['families']==2
    assert counts['comparison_with_earlier_referee_R_flags']['compared']==5717
    assert not counts['comparison_with_earlier_referee_R_flags']['mismatches']
    assert not counts['plain_vs_bond_disagreements_in_supplied_flags']
    assert len(counts['order_not_pinned'])==15

    pinning=load('pinning_window_results_summary.json')
    assert pinning['pinning']['families']==757
    assert not pinning['pinning']['T1_violations']
    assert len(pinning['pinning']['T2_failures'])==15
    assert len(pinning['new_two_block_bounds'])==9
    assert all(x['maximum']==4 and x['wrapper'] for x in pinning['new_two_block_bounds'])
    assert pinning['all_runtime_code_hashes_identical']

    local=load('localisation_checks.json')
    assert local['script_sha256']==digest(HERE/'localisation_checks.py')
    assert not local['prohibited_study_python_opened_or_imported']
    synthetic=local['synthetic_cnf']
    assert synthetic['target_depth']>synthetic['H']
    assert synthetic['side_descent']>synthetic['side_bound']
    assert synthetic['far_support_is_least'] and synthetic['near_support_is_least']

    middle=load('middle_summary.json')
    assert middle['families']==65 and middle['completed_record_cells']==192
    assert middle['global_exact_size_three_cells']==159
    joined=middle['additional_prefix_minima_from_completed_lower_exclusion_and_alternative_witness']
    assert middle['finite_prefix_exact_size_four_cells']+len(joined)==27
    assert len(middle['missing_cells'])==3
    primary=[r for name,obj in parsed.items() if name.startswith('middle_panel') and name.endswith('.jsonl') for r in obj]
    primary+=parsed['middle_remaining_small.jsonl']
    oldhash=digest(HERE/'middle_bonds_soft_timeout.py')
    newhash=digest(HERE/'middle_bonds.py')
    assert all(r['script_sha256'] in (oldhash,newhash) for r in primary)
    assert load('middle_solver_controls.json')['timeout_is_exception_not_UNSAT']

    report=(HERE/'codex_report.md').read_text()
    assert report.startswith('Verdict: **Confirmed with fixes.**')
    assert all(f'## {i}.' in report for i in range(1,6))
    for target in re.findall(r'\]\(([^)]+)\)',report):
        assert (HERE/target).exists(),target
    assert not changed_sources,changed_sources
    now=datetime.datetime.now(datetime.timezone.utc)
    result={
        'verdict':'pass','finished_at_utc':now.isoformat(),
        'scope':'TOP-INFO-20261114-001 independent referee; outputs only in the assigned directory',
        'scientific_validation':'V2 fresh TOP mathematical recomputation using explicitly permitted earlier referee engines; V1 finite localisation controls; not external replication',
        'python_syntax_checked':syntax,'parsed_json':json_files,'parsed_jsonl':jsonl_files,
        'stored_complete_bond_certificates_rechecked':bond_checks,
        'all_declared_sources_unchanged':not changed_sources,'sources':sources,
        'runtime_source_versions':{'middle_bonds_soft_timeout.py':oldhash,'middle_bonds.py':newhash},
        'forbidden_study_python_opened_or_imported':False,
        'network_used':False,'git_mutation_or_publication':False,
        'resource_limits':{'max_solver_processes_across_lanes':3,'peak_imposed_parallel_address_space_GiB':9,
             'command_limit_minutes':15,'total_task_limit_minutes':75,
             'incomplete_cells_preserved':True,'owned_solver_sessions_interrupted':2},
        'files_written':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files},
        'preexisting_files_preserved':sorted(PREEXISTING)}
    (HERE/'referee_validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'verdict':result['verdict'],'python_files':len(syntax),
        'JSON_files':len(json_files),'JSONL_files':len(jsonl_files),
        'stored_bond_certificates':bond_checks,'files_written':len(files)+1,
        'final_counts':counts['new_final_counts'],'finished_at_utc':result['finished_at_utc']},indent=2))


if __name__=='__main__':
    main()
