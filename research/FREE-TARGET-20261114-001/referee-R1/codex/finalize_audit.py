"""Recheck retained exact witnesses and bind the referee deliverables."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path
from direct_bonds import DirectSearch, usual_and_limit, unfold, load_cases, ROOT
from direct_summary import main as summarize

OUT=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    start=time.monotonic();summarize()
    summary=json.loads((OUT/'direct_summary.json').read_text())
    assert not summary['mismatches'],summary['mismatches']
    assert summary['families_with_exact_points']>=8
    assert sum(c['r']>=4 and any(p['status']=='exact' for p in c['points'])
               for c in summary['cases'])>=2
    # Check selection sizes against the completely independent flattened
    # bodies rather than accepting producer preparation metadata on trust.
    relations=json.loads((OUT/'relations_audit.json').read_text())
    assert relations['mismatches']==[]
    assert relations['summary']['finite_r']==43
    assert relations['summary']['relation_or_semigroup_mismatches']==0
    eligible=[f for f in relations['families'] if f['semigroup']['r'] is not None]
    eligible.sort(key=lambda f:(f['S_size'],f['n_defs'],f['semigroup']['r'],f['key']))
    assert [f['key'] for f in summary['cases']]==[f['key'] for f in eligible[:10]]
    independent={f['key']:f for f in eligible}
    checked=[]
    for family in summary['cases']:
        defs,G=usual_and_limit(json.loads(family['key']))
        fresh=independent[family['key']]
        assert (family['S'],family['main'],family['s_block_size'],family['r'])==(
            fresh['S'],fresh['main'],fresh['S_size'],fresh['semigroup']['r'])
        assert {str(i):sum(int(b)<<j for j,b in enumerate(g)) for i,g in G.items()}=={
            i:int(g,16) for i,g in fresh['G'].items()}
        for p in family['points']:
            if p['status']!='exact':continue
            cnf,n,roots,targets,copies,_=unfold(defs,G,p['s']+p['h'],p['s'])
            assert n==p['variables']
            support=tuple(p['witness'])
            assert len(set(support))==p['minimum']
            assert set(support)&roots and set(support)&targets
            search=DirectSearch(cnf,n,roots,targets,30)
            try:
                assert not search.shatters(support)
                assert all(search.shatters(set(support)-{v}) for v in support)
                forbidden=[]
                for state in range(1<<len(support)):
                    cube=[v+1 if state>>j&1 else -(v+1) for j,v in enumerate(support)]
                    if not search.solve(cube):forbidden.append(state)
                if p['forbidden_states'] is not None:
                    assert forbidden==p['forbidden_states']
            finally:search.close()
            assert p['minimum']>=p['claimed_lower_bound']
            assert p['minimum']>=p['justified_lower_bound']
            assert p['minimum']<=p['L_path']
            checked.append({'case':p['case'],'s':p['s'],'h':p['h'],
                            'size':len(support),'forbidden_states':forbidden,
                            'all_one_deleted_full':True})
    assert len(checked)==summary['exact_points']
    for p in summary['complete_halo_pairs']:
        assert p['h2']<=p['h1']
    direct_controls=json.loads((OUT/'direct_controls.json').read_text())
    direct_validation=json.loads((OUT/'direct_validation.json').read_text())
    assert direct_controls['nonminimal_mutant_rejected']
    assert all(r['cegar_agrees'] for r in direct_controls['cases'])
    assert direct_validation['all_match'] and direct_validation['count']==45
    assert direct_validation['wrapper_counterexample_direct_sat']['passed']
    # All artifacts must parse; all in-report local links must resolve.
    parsed=[]
    for p in sorted(OUT.glob('*.json')):
        if p.name=='run_manifest.json':continue
        json.loads(p.read_text());parsed.append(p.name)
    for p in sorted(OUT.glob('*.jsonl')):
        for line in p.read_text().splitlines():json.loads(line)
        parsed.append(p.name)
    report=OUT/'codex_report.md'
    links=re.findall(r'\]\(([^)]+)\)',report.read_text())
    for target in links:
        if '://' not in target:assert (OUT/target.split('#')[0]).exists(),target
    study=ROOT/'experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex'
    inputs=[ROOT/'research/FREE-TARGET-20261114-001'/name for name in
            ['free_target.md','preregistration.md','codex_spec.md','advisor_review_answer.md']]
    inputs += [study/name for name in ['population.json','gates.json','gate_relations.jsonl',
                                       'full/results.jsonl','full/summary.json']]
    inputs += list((ROOT/'experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample').glob('*.jsonl'))
    inputs += [ROOT/'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py',
               ROOT/'experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py',
               ROOT/'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz',
               ROOT/'experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz']
    # This guard concerns file contents, not paths mentioned in the spec.
    assert all(not(p.suffix=='.py' and study in p.parents) for p in inputs)
    input_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(inputs))}
    now=datetime.datetime.now(datetime.timezone.utc)
    initial=datetime.datetime(2026,11,14,0,19,57,tzinfo=datetime.timezone.utc)
    outputs=[p for p in OUT.iterdir() if p.is_file() and
             p.name not in ('brief_codex.md','codex_last_message.md','run_manifest.json')]
    manifest={'status':'PASS','review_kind':'V2, independently authored same-task AI audit',
              'started_at_utc':initial.isoformat(),'finished_at_utc':now.isoformat(),
              'elapsed_minutes':(now-initial).total_seconds()/60,
              'witnesses_rechecked':len(checked),'checks':checked,
              'smallest_block_selection_and_G_cross_checks':10,
              'parsed_artifacts':parsed,'report_links_checked':links,
              'input_sha256':input_hashes,'output_sha256':{p.name:sha(p) for p in sorted(outputs)},
              'read_restriction':'No producer Python under FREE-TARGET codex opened or imported.',
              'writes_restriction':'Only referee-R1/codex; no Git mutations or publication.',
              'execution_deviations':['resource_deviation.json','direct_budget_interrupt.json'],
              'validation_seconds':time.monotonic()-start}
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['status','witnesses_rechecked','elapsed_minutes','validation_seconds']}))


if __name__=='__main__':main()
