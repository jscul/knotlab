"""Small exhaustive state/subset oracle for the fresh direct SAT search."""
import itertools
import json
import random
import time
from pathlib import Path
from direct_bonds import DirectSearch, unfold, usual_and_limit

OUT=Path(__file__).resolve().parent


def oracle(clauses,n,roots,targets):
    states=[s for s in range(1<<n)
            if all(any(bool(s>>(abs(l)-1)&1)==(l>0) for l in c) for c in clauses)]
    if not states:return None
    def full(vs):
        return len({sum(((s>>v)&1)<<j for j,v in enumerate(vs)) for s in states})==1<<len(vs)
    for k in range(2,n+1):
        for vs in itertools.combinations(range(n),k):
            if not set(vs)&roots or not set(vs)&targets:continue
            if not full(vs) and all(full(tuple(w for w in vs if w!=v)) for v in vs):return k
    return None


def main():
    t0=time.monotonic();rng=random.Random(5190241);rows=[]
    for case in range(45):
        n=5+case%4;clauses=[]
        for _ in range(1+case%9):
            a=rng.sample(range(1,n+1),3)
            clauses.extend([a,[-x for x in a]])
        if case%7==0:clauses.extend([[1,-2],[-1,2]])
        roots={0};targets={n-1}
        expected=oracle(clauses,n,roots,targets)
        # These NAE fixtures are satisfiable unless their complete state
        # list is empty; only compare nonempty systems.
        satisfiable=any(all(any(bool(s>>(abs(l)-1)&1)==(l>0) for l in c)
                            for c in clauses) for s in range(1<<n))
        if not satisfiable:continue
        search=DirectSearch(clauses,n,roots,targets,30,[set(range(n))])
        try:actual=search.run(max_size=n,seeds=10)['minimum']
        finally:search.close()
        assert actual==expected,(case,actual,expected)
        rows.append({'case':case,'n':n,'clauses':clauses,'oracle':expected,'direct_sat':actual})
    # A finite helper before recursive entry must remain part of main at
    # depth zero. Its locals must not be relabelled as depth-one targets.
    raw=[[3,1,[['K',[0,1,3]]]],
         [3,1,[['K',[0,1,3]],['SELF',[1,3,0]]]],
         [3,0,[[0,[0,1,2]],[1,[0,1,2]]]]]
    defs,G=usual_and_limit(raw)
    _,_,_,targets,copies,_=unfold(defs,G,2,1)
    helper=[c for c in copies if c['definition']==0 and c['address']==['D0']][0]
    entry=[c for c in copies if c['definition']==1 and c['address']==['D1']][0]
    assert helper['depth']==0 and not(set(helper['own'])&targets)
    assert entry['depth']==1 and set(entry['own']).issubset(targets)
    # Independently check the relation lane's explicit NAE wrapper witness
    # by full-copy SAT rather than port products or its local enumerator.
    control=json.loads((OUT/'relations_audit.json').read_text())['controls']['wrapper_boundary_counterexample']
    defs,G=usual_and_limit(control['NAE_description'])
    clauses,n,roots,targets,copies,_=unfold(defs,G,5,4)
    c2=[c for c in copies if c['definition']==1 and c['depth']==2][0]
    c4=[c for c in copies if c['definition']==1 and c['depth']==4][0]
    witness=(1,c2['own'][2],c4['own'][3])
    search=DirectSearch(clauses,n,roots,targets,30)
    try:
        assert not search.shatters(witness)
        assert all(search.shatters(set(witness)-{v}) for v in witness)
        assert witness[0] in roots and witness[-1] in targets
        forbidden=[]
        for state in range(8):
            if not search.solve([(v+1) if state>>j&1 else -(v+1) for j,v in enumerate(witness)]):
                forbidden.append(state)
        assert forbidden==[0,7]
    finally:search.close()
    # The sample stratum has a choice of calls. Duplicating the SELF call
    # retains G=TOP and the same observed path witness; unmarked sibling
    # subtrees add no port restriction. Check that variant directly too.
    branch_raw=json.loads(json.dumps(control['NAE_description']))
    branch_raw[1][2].append(['SELF',[1,3,4]])
    defs,branch_G=usual_and_limit(branch_raw)
    assert all(branch_G[1])
    branch_cnf,branch_n,branch_roots,branch_targets,branch_copies,_=unfold(defs,branch_G,5,4)
    b2=[c for c in branch_copies if c['definition']==1 and c['address']==['D0',2]][0]
    b4=[c for c in branch_copies if c['definition']==1 and c['address']==['D0',2,2,2]][0]
    branch_witness=(1,b2['own'][2],b4['own'][3])
    search=DirectSearch(branch_cnf,branch_n,branch_roots,branch_targets,30)
    try:
        assert not search.shatters(branch_witness)
        assert all(search.shatters(set(branch_witness)-{v}) for v in branch_witness)
        branch_forbidden=[]
        for state in range(8):
            if not search.solve([(v+1) if state>>j&1 else -(v+1)
                                 for j,v in enumerate(branch_witness)]):
                branch_forbidden.append(state)
        assert branch_forbidden==[0,7]
    finally:search.close()
    result={'controls':rows,'all_match':True,'count':len(rows),
            'helper_entry_depth_control':{'helper':helper,'entry':entry,'passed':True},
            'wrapper_counterexample_direct_sat':{'variables':n,'witness':witness,
                                                 'forbidden_states':forbidden,'passed':True},
            'two_call_wrapper_counterexample':{'raw':branch_raw,'variables':branch_n,
                                               'witness':branch_witness,'G_S_is_TOP':True,
                                               'forbidden_states':branch_forbidden,'passed':True},
            'seconds':time.monotonic()-t0}
    (OUT/'direct_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='controls'}))


if __name__=='__main__':main()
