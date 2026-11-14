"""Fresh Rule A/N from preregistration stage 2; permitted referee exact engine.

No FORGET-RULE experiment Python is read or imported.  Rule A's implementation
below was written from the prose, before any held-out comparison.  All call
relations and exact graph decisions use the earlier permitted referee engine.
"""
from __future__ import annotations
import os
for _v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_v]='1'
import collections, hashlib, importlib.util, itertools, json, resource, time
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
ENGINE=ROOT/'research/CENSUS-FORGET-20261114-001/referee-R1/codex/sample_audit.py'
_spec=importlib.util.spec_from_file_location('permitted_referee_engine',ENGINE)
E=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E)


def canonical(defs):
    return json.dumps(defs,separators=(',',':'))


def full_pairs(allowed):
    return all(len({E.project(v,[j for j in range(3) if j!=drop]) for v in allowed})==4
               for drop in range(3))


def constraint_data(calls,G,chosen):
    """Remove the continuation; full relations impose no constraint at all."""
    constraints=[]
    for j,(callee,args) in enumerate(calls):
        if j==chosen: continue
        allowed=set(range(1,7)) if callee=='K' else G[callee]
        if len(allowed)==8: continue
        constraints.append((tuple(args),full_pairs(allowed)))
    return constraints


class Union:
    def __init__(self,n): self.p=list(range(n))
    def root(self,x):
        while x!=self.p[x]:
            self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def join(self,a,b):
        a,b=self.root(a),self.root(b)
        if a!=b: self.p[b]=a


def rule_step(size,constraints,args,state,free_peeling=True,protect_F_outputs=False):
    sigma,marked,F=state
    remaining=list(constraints)
    protected=set(args)
    removed=0; free_removed=0; eliminations=[]
    # The first three distinctions are ports. Own distinctions not retained
    # at the lower boundary, and ports untouched from above, can be eliminated.
    while True:
        degree=collections.Counter(v for vs,_ in remaining for v in vs)
        peel=None
        for idx,(vs,pair_full) in enumerate(remaining):
            if not pair_full: continue
            for v in vs:
                eligible=(v>=3 and v not in protected) or (v<3 and free_peeling and ((F>>v)&1) and (not protect_F_outputs or v not in protected))
                # Literal stage-2 rule allows a port in F even when retained
                # among the chosen call arguments. The repair protects it.
                if degree[v]==1 and eligible:
                    peel=(idx,v); break
            if peel: break
        if peel is None: break
        idx,v=peel; old=remaining.pop(idx); eliminations.append({"constraint":old[0],"via":v,"retained_output":v in protected}); removed+=1; free_removed+=v<3
    u=Union(size)
    for a in range(3):
        for b in range(a):
            if sigma[a]==sigma[b]: u.join(a,b)
    for vs,_ in remaining:
        for v in vs[1:]: u.join(vs[0],v)
    roots=[u.root(v) for v in args]
    names={}; new_sigma=tuple(names.setdefault(r,len(names)) for r in roots)
    marked_roots={u.root(j) for j in range(3) if (marked>>j)&1}
    new_marked=sum((r in marked_roots)<<j for j,r in enumerate(roots))
    touched={v for vs,_ in remaining for v in vs}
    # A carried upper port keeps its prior touch. An own distinction has no
    # incidence above the current block. Top boundary ports start nonfree.
    new_F=sum((v not in touched and (v>=3 or (F>>v)&1))<<j for j,v in enumerate(args))
    result=(new_sigma,new_marked,new_F)
    assert all(not ((new_F>>j)&1) or (not ((new_marked>>j)&1) and new_sigma.count(new_sigma[j])==1)
               for j in range(3))
    return result, {'peeled':removed,'F_peeled':free_removed,'remaining':remaining,'eliminations':eliminations}


def rule_A(size,calls,G,S,free_peeling=True,start=None,protect_F_outputs=False):
    selected=[j for j,(c,_) in enumerate(calls) if c==S]
    constraints=[constraint_data(calls,G,j) for j in selected]
    arguments=[calls[j][1] for j in selected]
    initial=start or ((0,1,2),7,0)
    queue=collections.deque([initial]); states={initial:0}; graph={}; stats=collections.Counter()
    while queue:
        state=queue.popleft(); targets=[]
        if not state[1]: continue
        for cs,args in zip(constraints,arguments):
            nxt,detail=rule_step(size,cs,args,state,free_peeling,protect_F_outputs)
            stats['steps']+=1; stats['peelings']+=detail['peeled']; stats['F_peelings']+=detail['F_peeled']
            targets.append(nxt)
            if nxt[1] and nxt not in states:
                states[nxt]=len(states); queue.append(nxt)
        graph[state]=targets
    active={}; closed={}; stack=[]; labels=[]; cycle=None
    def visit(state):
        nonlocal cycle
        active[state]=len(stack); stack.append(state); longest=0
        for i,nxt in enumerate(graph[state]):
            if not nxt[1]: continue
            if nxt in active:
                k=active[nxt]; cycle={'prefix':labels[:k],'cycle':labels[k:]+[i]}; return None
            if nxt not in closed:
                labels.append(i); value=visit(nxt); labels.pop()
                if value is None: return None
            longest=max(longest,1+closed[nxt])
        closed[state]=longest; stack.pop(); active.pop(state); return longest
    value=visit(initial)
    return {'certified':value is not None,'bound':value+1 if value is not None else None,
            'live_states':len(graph),'cycle':cycle,**stats}


def rule_N(calls,S):
    successors=[set() for _ in range(3)]
    for callee,args in calls:
        if callee==S:
            for k,v in enumerate(args):
                if v<3: successors[v].add(k)
    reach=[set(x) for x in successors]
    for _ in range(3):
        reach=[set(x)|set().union(*(reach[v] for v in x)) for x in reach]
    return {'cyclic':any(j in reach[j] for j in range(3)),
            'arcs':[[a,b] for a,x in enumerate(successors) for b in sorted(x)]}


@lru_cache(maxsize=30000)
def _assignment_mask(size,args,allowed_mask):
    return sum(1<<v for v in range(1<<size) if (allowed_mask>>E.project(v,args))&1)


def limit_fast(defs):
    """Independent finite bitset evaluation from raw-language semantics."""
    types=E.self_types(defs); prev={i:255 for i in types}; history=[]
    while True:
        relations=[]
        for i,(arity,local,calls) in enumerate(defs):
            size=arity+local; possible=(1<<(1<<size))-1
            for callee,args in calls:
                allowed=126 if callee=='K' else prev[i] if callee=='SELF' else relations[callee]
                possible &= _assignment_mask(size,tuple(args),allowed)
                if not possible: break
            answer=0
            while possible:
                bit=possible&-possible; answer|=1<<((bit.bit_length()-1)&((1<<arity)-1)); possible^=bit
            relations.append(answer)
        curr={i:relations[i] for i in types}; history.append(curr)
        assert all(curr[i]&prev[i]==curr[i] for i in types)
        if curr==prev:
            return [{v for v in range(1<<defs[i][0]) if (r>>v)&1} for i,r in enumerate(relations)], {
                i:{v for v in range(8) if (r>>v)&1} for i,r in curr.items()},history
        prev=curr


def prepare(raw,S=None):
    defs=E.usual(raw); all_G,G,history=limit_fast(defs)
    S=len(defs)-1 if S is None else S
    size,calls=E.flatten(defs,S)
    return defs,all_G,G,size,calls,history


def exact(size,calls,G,S,max_states=250000):
    selected=[j for j,(c,_) in enumerate(calls) if c==S]
    matrices=[E.derive_R(size,calls,G,j)[0] for j in selected]
    return matrices,E.graph_decision(matrices,max_states=max_states)


def examine(raw,S=None,exact_all=True):
    defs,all_G,G,size,calls,history=prepare(raw,S)
    S=len(defs)-1 if S is None else S
    a=rule_A(size,calls,G,S); n=rule_N(calls,S)
    matrices,decision=exact(size,calls,G,S) if exact_all or a['certified'] else ([],None)
    return {'defs':raw,'S':S,'alive':bool(all_G[-1]),'G':{str(i):hex(E.mask(r)) for i,r in G.items()},
            'size':size,'calls':calls,'A':a,'N':n,'R_i':list(map(hex,matrices)),'exact':decision}


def controls():
    # Entire q=2 relation algebra plus graph/orbit checks are inherited from
    # the permitted referee and explicitly rerun as controls.
    algebra=E.controls()
    fixtures=[]
    for name,raw,wantA,wantN,r in [
        ('empty_block_fresh_args',[[3,3,[['SELF',[3,4,5]]]]],True,False,1),
        ('identity',[[3,0,[['SELF',[0,1,2]]]]],False,True,None),
        ('identity_shift_two',[[3,2,[['SELF',[1,3,4]]]]],True,False,2),
        ('degree_one_peel',[[3,4,[['K',[0,3,6]],['SELF',[3,4,5]]]]],True,False,1),
        ('F_peel_at_second_layer',[[3,3,[['K',[0,1,3]],['SELF',[3,4,5]]]]],True,False,2),
    ]:
        z=examine(raw); assert z['A']['certified']==wantA and z['N']['cyclic']==wantN and z['exact']['r']==r,(name,z)
        if name=='F_peel_at_second_layer': assert z['A']['F_peelings']>0
        fixtures.append({'name':name,**z})
    gadget=json.loads((ROOT/'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.json').read_text())
    z=examine(gadget['defs']); assert not z['A']['certified'] and not z['N']['cyclic'] and z['exact']['r'] is None
    assert int(gadget['R'][0],16)==int(z['R_i'][0],16)
    fixtures.append({'name':'climb_back_inequality_gadget','beyond_LOCAL_CAP':True,**z})
    return {'algebra':algebra,'fixtures':fixtures,'passed':True}

if __name__=='__main__':
    result=controls(); (HERE/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'fixtures':len(result['fixtures'])}))
