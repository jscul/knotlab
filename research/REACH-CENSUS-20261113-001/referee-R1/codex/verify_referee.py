"""Compact integrity checks and third-method truth-enumeration controls.

Truth enumeration uses no DP, SAT queries, component factorisation, bit-complement
shortcut, or minimal-nonfree-set pruning. It evaluates the CNF on every assignment
and independently tests projections and their single-member deletions.
"""
import itertools
import json
import hashlib
import importlib.util
import resource
import time
from collections import Counter
import numpy as np
import fresh_recompute as R

def load(name):
    return [json.loads(x) for x in (R.HERE/name).read_text().splitlines()]

def exhaustive(p,depth,maximum):
    clauses,n,top,last,pool=p.cnf(depth)
    assert n<=12
    assignments=np.arange(1<<n,dtype=np.int64)
    allowed=np.ones(len(assignments),dtype=bool)
    for clause in clauses:
        holds=np.zeros(len(assignments),dtype=bool)
        for lit in clause:
            holds |= ((assignments>>(abs(lit)-1))&1)==(lit>0)
        allowed &= holds
    satisfying=assignments[allowed]
    assert len(satisfying)>0
    cache={}
    def free(W):
        if W not in cache:
            projection=np.zeros(len(satisfying),dtype=np.int64)
            for i,w in enumerate(W): projection |= ((satisfying>>w)&1)<<i
            cache[W]=len(np.unique(projection))==(1<<len(W))
        return cache[W]
    for size in range(1,maximum+1):
        for W in itertools.combinations(sorted(pool),size):
            if not top.intersection(W) or not last.intersection(W): continue
            if not free(W) and all(free(W[:i]+W[i+1:]) for i in range(size)):
                return dict(value=size,n=n,allowed_states=len(satisfying),projection_tests=len(cache))
    return dict(value=None,lower_bound=maximum+1,n=n,allowed_states=len(satisfying),projection_tests=len(cache))

def main():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    primary=load('fresh_primary.jsonl'); alternative=load('fresh_alternative.jsonl')
    certs=json.loads((R.HERE/'all131_positive_certificates.json').read_text())
    assert len(primary)==49 and all(r['status']=='done' and not r['errors'] for r in primary)
    assert all(not r['errors'] for r in alternative)
    assert len(certs)==131 and all(r['status']=='done' and r['certified'] for r in certs)
    assert Counter(r['uniform_cost_bound'] for r in certs)=={3:96,4:32,5:3}
    # Verify the stress-test keys really name distinct first-ray growers in the
    # one-definition limit-only domain, independently of its filename.
    stress=R.rows('alt_growing664_families.jsonl.gz')
    census={r['key']:r for r in R.rows('families.jsonl.gz')}
    assert len(stress)==len({r['key'] for r in stress})==224
    language=R.ROOT/'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py'
    spec=importlib.util.spec_from_file_location('allowed_input_language_verification',language)
    lang=importlib.util.module_from_spec(spec); spec.loader.exec_module(lang)
    for r in stress:
        first=census[r['key']]; defs=json.loads(r['key'])
        assert len(defs)==1 and first['class']=='grows' and first['complete'] and first['usual_limit_alive']
        assert not all(lang.depth_sequence(defs,lang.NAE)[0])
    stress_link=dict(unique_keys=224,all_in_primary_census=True,
                     all_complete_first_ray_growers=True,all_one_definition_limit_only=True)
    del census
    truth=[]
    # Six multi-definition examples with distinct block/entry situations, plus
    # two one-definition controls. Selection depends only on recorded structure.
    selected=[]
    for multi,count in [(True,6),(False,2)]:
        candidates=[r for r in primary if (r['structure']['n_defs']>1)==multi
                    and r['structure']['main_size']+r['structure']['s_size']-3<=12]
        selected += candidates[:count]
    for r in selected:
        p=R.Pattern(r['key'])
        for depth in [1,2,3]:
            n=p.main[1]+depth*(p.body[1]-3)
            if n>12: continue
            result=exhaustive(p,depth,min(5,r['dp_small'][depth-1]))
            expected=r['dp_small'][depth-1]
            result.update(key=r['key'],depth=depth,expected=expected)
            result['agrees']=result['value']==expected if result['value'] is not None else expected>=result['lower_bound']
            assert result['agrees']
            truth.append(result)
    def aggregate(a):
        sat=[s for r in a for s in r.get('direct_sat',[])]
        return dict(families=len(a),statuses=dict(Counter(r['status'] for r in a)),
                    classes=dict(Counter(r['reported']['class'] for r in a)),
                    multi_definition=sum(r['structure']['n_defs']>1 for r in a),
                    at_block_cap=sum(max(r['structure']['main_size'],r['structure']['s_size'])==12 for r in a),
                    max_ray_distinctions=max(s['n'] for s in sat),
                    direct_sat_cases=len(sat),direct_sat_exact=sum(s['status']=='exact' for s in sat),
                    direct_sat_lower_bound=sum(s['status']=='lower_bound' for s in sat),
                    direct_sat_disagreements=sum(not s['agreement'] for s in sat),
                    graph_depth_values=sum(len(r.get('class_recompute',{}).get('L_ray',[])) for r in a),
                    sum_seconds=sum(r['seconds'] for r in a),peak_rss_kib=max(r['peak_rss_kib'] for r in a))
    source_paths=[R.HERE/'fresh_recompute.py',R.HERE/'bounded_certificate.py',R.HERE/'verify_referee.py',
                  R.ROOT/'research/REACH-CENSUS-20261113-001/codex_spec.md',
                  R.ROOT/'research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py']
    source_paths += [language]+[R.DATA/name for name in ['families.jsonl.gz','alt_growing664_families.jsonl.gz','run_info.json']]
    result=dict(primary=aggregate(primary),alternative=aggregate(alternative),
                all131=dict(cases=len(certs),certified=sum(r['certified'] for r in certs),
                            bounds=dict(Counter(r['uniform_cost_bound'] for r in certs)),
                            peak_rss_kib=max(r['peak_rss_kib'] for r in certs),
                            sufficient_onset_range=[min(r['onset_depth'] for r in certs),max(r['onset_depth'] for r in certs)],
                            sum_seconds=sum(r['seconds'] for r in certs)),
                stress_test_key_link=stress_link,
                truth_enumeration_controls=truth,
                reused_code='only exact_eventual_bound from explicitly permitted prior referee',
                forbidden_implementation_accessed=False,
                input_and_source_sha256={str(p.relative_to(R.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
    R.save('verification_summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k in ['primary','alternative','all131']}))
    print('truth enumeration controls:',len(truth),'all agree')

if __name__=='__main__': main()
