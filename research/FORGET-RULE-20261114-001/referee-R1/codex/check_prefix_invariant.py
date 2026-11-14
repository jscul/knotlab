"""Compare Rule A's frontier memory to a whole-prefix graph, six layers deep."""
import collections,itertools,json,random,time
import independent_rules as R
from search_counterexamples import random_families,f_targeted
HERE=R.HERE


def verify(raw,word):
    defs,allG,G,size,calls,_=R.prepare(raw);S=len(defs)-1
    chosen=[j for j,(c,a) in enumerate(calls) if c==S]
    state=((0,1,2),7,0);frontier=[0,1,2];nv=3;global_constraints=[];steps=0;climbbacks=0
    for letter in word:
        select=chosen[letter];args=calls[select][1];cs=R.constraint_data(calls,G,select)
        env=frontier+list(range(nv,nv+size-3));nv+=size-3
        before=state
        state,detail=R.rule_step(size,cs,args,state,protect_F_outputs=True)
        # Install the actual constraints in a finite layered composite.
        global_constraints.extend([tuple(env[v] for v in vs) for vs,full in cs])
        next_frontier=[env[v] for v in args]
        for deletion in detail['eliminations']:
            v=env[deletion['via']];constraint=tuple(env[q] for q in deletion['constraint'])
            degree=sum(v in scope for scope in global_constraints)
            assert degree==1 and v not in next_frontier and v not in (0,1,2),(raw,word,before,deletion,degree)
            global_constraints.remove(constraint)
        # A separate full union over all retained prefix constraints. No
        # summary partitions are used in deriving the expected next state.
        neighbors=collections.defaultdict(set)
        for scope in global_constraints:
            for a,b in itertools.combinations(scope,2):neighbors[a].add(b);neighbors[b].add(a)
        components={};names=0
        for v in range(nv):
            if v in components:continue
            pending=[v];components[v]=names
            while pending:
                x=pending.pop()
                for y in neighbors[x]:
                    if y not in components:components[y]=names;pending.append(y)
            names+=1
        roots=[components[v] for v in next_frontier];renaming={};sigma=tuple(renaming.setdefault(v,len(renaming)) for v in roots)
        top_roots={components[j] for j in range(3)};marked=sum((v in top_roots)<<j for j,v in enumerate(roots))
        touched=set(itertools.chain.from_iterable(global_constraints));F=sum((v not in touched and v not in (0,1,2))<<j for j,v in enumerate(next_frontier))
        assert state==(sigma,marked,F),(raw,word,before,state,(sigma,marked,F))
        if any(before[0][j]==before[0][k] for j in range(3) for k in range(j)):
            climbbacks+=1
        frontier=next_frontier;steps+=1
    return steps,climbbacks


def run():
    start=time.monotonic();rng=random.Random(303031);families=0;words=0;steps=0;joined_prefix_steps=0;F_cases=0
    streams=itertools.chain(f_targeted(991111,1000),random_families(991112,1000))
    for kind,raw in streams:
        defs,allG,G,size,calls,_=R.prepare(raw);S=len(defs)-1;c=sum(c==S for c,a in calls)
        if not allG[-1]:continue
        A=R.rule_A(size,calls,G,S,protect_F_outputs=True);F_cases+=bool(A.get('F_peelings',0));families+=1
        for word in ([0]*6,[c-1]*6,[rng.randrange(c) for _ in range(6)]):
            s,j=verify(raw,word);steps+=s;joined_prefix_steps+=j;words+=1
    # The advisor's down-and-back inequality gadget is the named hard control.
    p=R.ROOT/'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.json'
    gadget=json.loads(p.read_text());s,j=verify(gadget['defs'],[0]*6);steps+=s;joined_prefix_steps+=j;words+=1
    result={'passed':True,'alive_random_families':families,'words':words,'prefix_steps':steps,'steps_with_nontrivial_upper_partition':joined_prefix_steps,
            'families_using_F_peeling':F_cases,'hard_climb_back_gadget_checked':True,'depth_per_word':6,'seconds':time.monotonic()-start}
    (HERE/'prefix_invariant.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':run()
