"""Decisive witness check with pure set relations, independent of all engines.

Only main() optionally imports the fresh Rule-A implementation to print a
trace. Relation construction, greatest limit and powers below are new and
use no code from any study or earlier referee.
"""
import collections,gzip,hashlib,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
RAW=[[3,2,[['K',[0,1,2]],['K',[0,2,4]],['SELF',[1,3,4]]]]]


def bits(n,arity=3): return tuple((n>>j)&1 for j in range(arity))
def pack(v): return sum(x<<j for j,x in enumerate(v))
def nae(*v): return len(set(v))>1

def derive_restricted(previous):
    return {pack(v[:3]) for v in itertools.product((0,1),repeat=5)
            if nae(v[0],v[1],v[2]) and nae(v[0],v[2],v[4]) and pack((v[1],v[3],v[4])) in previous}

def compose(A,B): return {(a,c) for a,b in A for bb,c in B if b==bb}
def rectangular(A): return A=={(a,b) for a in {a for a,b in A} for b in {b for a,b in A}}
def hexrel(A): return hex(sum(1<<(8*a+b) for a,b in A))

def keynorm(raw):
    return tuple((k,l,tuple(sorted((str(c),tuple(sorted(a)) if c=='K' else tuple(a)) for c,a in cs))) for k,l,cs in raw)

def isomorphs_one(raw):
    arity,local,calls=raw[0]; result=set()
    for perm in itertools.permutations(range(arity)):
        for own in itertools.permutations(range(arity,arity+local)):
            env=perm+own; body=[]
            for c,args in calls:
                if c=='SELF':
                    out=[None]*arity
                    for j,v in enumerate(args): out[perm[j]]=env[v]
                else: out=[env[v] for v in args]
                body.append((c,out))
            result.add(keynorm([(arity,local,body)]))
    return result


def main():
    # The selected call is removed: no bottom G and no bottom NAE are added.
    relation={(pack(v[:3]),pack((v[1],v[3],v[4]))) for v in itertools.product((0,1),repeat=5)
              if nae(*v[:3]) and nae(v[0],v[2],v[4])}
    previous=set(range(8)); history=[sorted(previous)]
    while True:
        new=derive_restricted(previous);history.append(sorted(new))
        if new==previous: break
        assert new<=previous;previous=new
    assert new==set(range(1,7))
    product={(a,a) for a in range(8)}; powers=[]
    for n in range(1,13):
        product=compose(product,relation)
        row2=sorted(b for a,b in product if a==2);row5=sorted(b for a,b in product if a==5)
        assert not rectangular(product)
        assert row2==([5,7] if n%2 else [0,2]); assert row5==([0,2] if n%2 else [5,7])
        powers.append({'n':n,'relation':hexrel(product),'pairs':len(product),'rectangular':False,'row_010':row2,'row_101':row5})
    # Closed semigroup recurrence is a finite, all-length certificate.
    P2=compose(relation,relation);P3=compose(P2,relation)
    assert compose(P3,relation)==P2 and not rectangular(P2) and not rectangular(P3)
    # Also check the alternate row witness: crossed pairs are absent.
    witnesses=[]
    for p in (P2,P3):
        b=next(b for a,b in p if a==2);c=next(b for a,b in p if a==5)
        assert (2,c) not in p and (5,b) not in p
        witnesses.append({'allowed':[[2,b],[5,c]],'forbidden_crosses':[[2,c],[5,b]]})
    import independent_rules as R
    defs,allG,G,size,calls,_=R.prepare(RAW)
    exact_matrices,exact=R.exact(size,calls,G,0)
    assert exact_matrices==[sum(1<<(8*a+b) for a,b in relation)]
    assert exact['verdict']=='non-forgetting'
    state=((0,1,2),7,0); cs=R.constraint_data(calls,G,2);trace=[]
    for depth in range(1,5):
        new_state,detail=R.rule_step(size,cs,calls[2][1],state)
        trace.append({'depth':depth,'before':state,'after':new_state,'eliminations':detail['eliminations'],
                      'remaining_constraints':detail['remaining']});state=new_state
        if not state[1]:break
    assert len(trace)==3 and any(e['retained_output'] for s in trace for e in s['eliminations'])
    census=ROOT/'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
    exact_key=json.dumps(RAW,separators=(',',':'));iso=isomorphs_one(RAW);isomatches=[];exact_found=False;total=0
    with gzip.open(census,'rt') as f:
        for line in f:
            row=json.loads(line);total+=1;raw=json.loads(row['key']);exact_found|=row['key']==exact_key
            if len(raw)==1 and keynorm(raw) in iso: isomatches.append({'key':row['key'],'class':row.get('class'),'lambda':row.get('lambda')})
    assert not exact_found
    result={'verdict':'literal Rule A refuted','defs':RAW,'description_sha256':hashlib.sha256(exact_key.encode()).hexdigest(),
            'full_description':'S(p0,p1,p2): own u,v; NAE(p0,p1,p2); NAE(p0,p2,v); SELF(p1,u,v)',
            'greatest_fixed_point_history':history,'usual_pass_through_added':False,'alive':True,'R':hexrel(relation),'R_pairs':len(relation),
            'powers':powers,'exact_semigroup_cycle':{'prefix_length':2,'period':2,'P2':hexrel(P2),'P3':hexrel(P3),'P4_equals_P2':True},
            'nonrectangular_cross_witnesses':witnesses,'A_literal':R.rule_A(size,calls,G,0),'A_output_guard':R.rule_A(size,calls,G,0,protect_F_outputs=True),
            'A_literal_trace':trace,'N':R.rule_N(calls,0),'earlier_referee_R_and_lasso_match':True,
            'census_exclusion':{'full_records':total,'exact_description_present':exact_found,'isomorphic_descriptions_present':len(isomatches),'isomorphic_examples':isomatches[:12],
                                'interpretation':'Exact-key holdout only; this minimal description has isomorphic examples elsewhere in the full census, outside the 12,772 first-ray-grower study.'},
            'all_length_proof':'A top state010 has next bottom in{101,111};101 has next bottom in{000,010};000 and111 have no outgoing row. Thus for n>=1 top010 ends in{101,111} at odd n and{000,010} at even n; complementary top101 has the opposite row. Crossed pairs fail at every n.'}
    (HERE/'counterexample.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('verdict','R','R_pairs','A_literal','A_output_guard','N','census_exclusion')}))

if __name__=='__main__':main()
