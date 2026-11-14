"""Reconcile independent lanes without rerunning their scientific checks."""
import ast
import collections
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE/name).read_text())


def jsonl(name):
    path=HERE/name
    return list(map(json.loads,path.read_text().splitlines())) if path.exists() else []


def main():
    plan=read('sample_plan.json')
    main_rows=jsonl('optimality_results.jsonl')
    cells={}
    disagreements=[]
    def accept(case,N,s,value,source,key=None):
        index=(case,N,s)
        if index in cells and cells[index]['L']!=value:
            disagreements.append({'case':case,'key':key,'N':N,'s':s,
                                  'previous':cells[index],'new_L':value,'new_source':source})
        cells[index]={'case':case,'N':N,'s':s,'L':value,'source':source}
    for r in main_rows:
        if r['result']['exact']:
            accept(r['case'],r['N'],r['s'],r['result']['L'],'optimality_results.jsonl',r['key'])
    direct=read('outcomes/direct_pair_audit.json')
    for case in direct['cases']:
        for q in case['queries']:
            if q.get('exact'):
                # For these explicit upper/lower checks exact_profile is
                # numeric only where all support-minimality checks passed.
                value=q['upper_bound']
                assert isinstance(value,int) and q['lower_bound']==value
                accept(case['case'],9,q['s'],value,'outcomes/direct_pair_audit.json',case['key'])
    sample_summary=[]
    for e in plan['sample']:
        verified=[]
        for s,study in enumerate(e['study'],1):
            cell=cells.get((e['case'],9,s))
            verified.append(cell['L'] if cell else 'unresolved')
            if cell and study!='undecided' and cell['L']!=study:
                disagreements.append({'case':e['case'],'key':e['key'],'N':9,'s':s,
                                      'study_L':study,'fresh':cell})
        sample_summary.append({'case':e['case'],'stratum':e['stratum'],'study':e['study'],
                               'verified':verified,'all_four_exact':'unresolved' not in verified})
    depth_rows=jsonl('cert_audit/depth_results.jsonl')+jsonl('depth_retries.jsonl')
    benchmark=HERE/'acceleration_benchmark.json'
    if benchmark.exists():
        depth_rows.append(read('acceleration_benchmark.json'))
    depth={}
    for r in depth_rows:
        index=(r['case'],r['N'],r['s'])
        previous=depth.get(index)
        if previous and previous['result']['exact']:
            if r['result']['exact'] and previous['result']['L']!=r['result']['L']:
                disagreements.append({'depth_first':previous,'depth_second':r})
            continue
        depth[index]=r
    depth_summary=[]
    for r in depth.values():
        depth_summary.append({'case':r['case'],'stratum':r['stratum'],'N':r['N'],'s':r['s'],
                              'study_N9':r['study_N9'],'fresh':r['result']['L'],
                              'exact':r['result']['exact'],'reason':r['result'].get('reason')})
    # A support block excludes the subset itself as well as its supersets.
    # Check explicitly that no recorded blocked subset could itself be a
    # crossing bond. This is also implied by cardinality-first exhaustion.
    checked_blocks=0
    block_violations=[]
    for r in main_rows+depth_rows:
        for support in r['result'].get('stats',{}).get('blocked_supports',[]):
            member_levels={(v+1).bit_length()-1 for v in support}
            checked_blocks+=1
            if 3 in member_levels and 3+r['s'] in member_levels:
                block_violations.append({'case':r['case'],'N':r['N'],'s':r['s'],'support':support})
    summary={'verdict':'Confirmed with fixes','sample_plan_sha256':hashlib.sha256((HERE/'sample_plan.json').read_bytes()).hexdigest(),
             'N9':{'descriptions':len(plan['sample']),'requested_cells':4*len(plan['sample']),
                   'exact_cells':sum((e['case'],9,s) in cells for e in plan['sample'] for s in range(1,5)),
                   'exact_full_profiles':sum(r['all_four_exact'] for r in sample_summary),
                   'profiles':sample_summary},
             'depth':{'unique_cells':len(depth_summary),'exact_cells':sum(r['exact'] for r in depth_summary),
                      'matching_N9':sum(r['exact'] and r['fresh']==r['study_N9'] for r in depth_summary),
                      'rows':sorted(depth_summary,key=lambda r:(r['stratum'],r['case'],r['N'],r['s']))},
             'numeric_disagreements':disagreements,
             'nonminimal_block_audit':{'recorded_blocks_checked':checked_blocks,
                                       'blocked_subsets_meeting_both_levels':block_violations},
             'lower_bound_limitations':'Exhaustion SAT queries are replayable computational evidence; no LRAT proof of the optimized master UNSAT is retained.',
             'substantive_corrections':['Universal N-monotonicity refuted in actual alive description family',
                                        'Q3 universal found-support membership false:26 cells,16descriptions',
                                        'Compatibility bounds tighten Q0-Q2; Q1/Q2 not falsified, not established',
                                        'Original dead-union retention not hash-bound; three fresh weighted-dead proofs rechecked'],
             'lane_sources':{'brute':'brute_audit/summary.json','outcomes':'outcomes/independent_summary.json',
                             'certificates':'cert_audit/summary.json','search_controls':'cert_audit/search_review_controls.json',
                             'dead_sample':'dead_recomputation.json'}}
    (HERE/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    validation={'python_sources_parsed':[],'json_parsed':0,'jsonl_records_parsed':0,'files':[]}
    for p in sorted(HERE.rglob('*')):
        if not p.is_file() or p.name in ['brief_codex.md','codex_last_message.md','validation_manifest.json']:
            continue
        if p.suffix=='.py':
            ast.parse(p.read_text(),filename=str(p))
            validation['python_sources_parsed'].append(str(p.relative_to(HERE)))
        elif p.suffix=='.json':
            json.loads(p.read_text())
            validation['json_parsed']+=1
        elif p.suffix=='.jsonl':
            validation['jsonl_records_parsed']+=len([json.loads(l) for l in p.read_text().splitlines() if l.strip()])
        raw=p.read_bytes()
        validation['files'].append({'path':str(p.relative_to(HERE)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (HERE/'validation_manifest.json').write_text(json.dumps(validation,indent=2)+'\n')
    assert not disagreements, 'Independent numeric disagreements must be investigated and reported in full'
    assert not block_violations, 'A blocked subset itself needs a crossing-bond safety justification'
    print(json.dumps({'N9_exact_cells':summary['N9']['exact_cells'],'N9_profiles':summary['N9']['exact_full_profiles'],
                      'depth_unique_cells':len(depth_summary),'depth_exact':summary['depth']['exact_cells'],
                      'json_files':validation['json_parsed'],'python_files':len(validation['python_sources_parsed'])}))


if __name__=='__main__':
    main()
