"""Direct words and ordinary rosters for the live alias and loose-row controls."""
from fractions import Fraction
from itertools import combinations
import json
import numpy as np
from target import OUTPUT, advance, words, roster, conditional_table, reading

def allowed(rows):
    signs=words(rows)
    return {sum((int(v)<0)<<i for i,v in enumerate(row)) for row in signs}

def small():
    closed=((0,1,2,3),(0,4,5,6),(1,4,5,7),(2,3,6,7))
    perm=[0,6,2,3,4,5,1,7]
    other=tuple(tuple(sorted(perm[x] for x in row)) for row in closed)
    source_left=(*closed,(8,9,10))
    source_right=(*other,(8,9,10))
    _,left,_=advance(source_left,'nae')
    _,right,_=advance(source_right,'nae')
    s,t=words(left),words(right)
    assert s.shape==t.shape==(24948,17)
    assert np.array_equal(s.T@s,t.T@t)
    full_left=set(map(int,((s<0)@(1<<np.arange(17)))))
    full_right=set(map(int,((t<0)@(1<<np.arange(17)))))
    L=roster(left,'nae');R=roster(right,'nae')
    assert L==R
    diff=full_left-full_right
    # Smallest higher marginal (complement symmetry gives equality through 3).
    separation=None
    for cols in combinations(range(17),4):
        a,b=s[:,cols],t[:,cols]
        countA=int(np.all(a==1,axis=1).sum());countB=int(np.all(b==1,axis=1).sum())
        if countA!=countB:
            separation=(cols,countA,countB)
            break
    assert separation
    repeated=((0,1,2,3,4),(1,2,5),(3,4,6),(5,6,7))
    x=words(repeated)
    v=x.T@x
    local=[];necessary=[]
    full=set(map(int,((x<0)@(1<<np.arange(8)))))
    for i,H in enumerate(repeated):
        projection={tuple(w[j] for j in H) for w in x}
        assert len(projection)==(1<<len(H))-2
        removed=tuple(row for j,row in enumerate(repeated) if i!=j)
        n=8
        # Keep the same physical carrier even if removing H makes a name free.
        mask=[sum(1<<j for j in row) for row in removed]
        removed_states={w for w in range(1<<n) if all(w&h not in (0,h) for h in mask)}
        necessary.append(len(removed_states-full))
        assert necessary[-1]>0
        local.append(len(projection))
    minimum=min(v[0,j] for j in range(1,8))
    tied=[j for j in range(1,8) if v[0,j]==minimum]
    assert tied==[1,2,3,4,7]
    result=dict(seventeen=dict(sources=[source_left,source_right],new_stages=[left,right],complete_word_counts=[len(full_left),len(full_right)],
                 intersection=len(full_left&full_right),left_only=len(diff),right_only=len(full_right-full_left),
                 first_left_only_word=min(diff),first_right_only_word=min(full_right-full_left),all_equal_rates=136,
                 birth_profile=L['parent_supports_and_fresh'],new_word_extension_factor=27,least_separating_order=4,
                 first_all_zero_reading=dict(places=separation[0],left_count=separation[1],right_count=separation[2])),
            repeated_tie=dict(holders=repeated,uniform_words=len(x),local_projection_sizes=local,extra_words_upon_single_erasure=necessary,
                loose_index=0,its_true_holder=repeated[0],row_minimizers=tied,uniform_signed_minimum=str(Fraction(int(minimum),len(x)))))
    # Independently list the first two cuts of the ternary founder, whose
    # nonconstant second-extension counts distinguish the two weightings.
    base=((0,1,2),)
    _,step1,_=advance(base,'nae')
    _,step2,_=advance(step1,'nae')
    one,two=words(step1),words(step2)
    n=one.shape[1]
    values=1<<np.arange(n)
    index=(two[:,:n]<0)@values
    from collections import Counter
    completions=Counter(map(int,index))
    from math import lcm
    common=lcm(*completions.values())
    fresh_rows=step2[len(step1):]
    check_counts={}
    for label in ('uniform','inherited'):
        obs=conditional_table(one,fresh_rows,np.ones(len(one),dtype=np.int64),label)[0]
        mass=np.array([1 if label=='uniform' else common//completions[i] for i in index],dtype=np.int64)
        signed=two.T@(mass[:,None]*two)
        denom=int(mass.sum())
        assert reading(obs)==[Fraction(denom-int(signed[i,j]),2*denom) for i,j in combinations(range(two.shape[1]),2)]
        check_counts[label]=len(reading(obs))
    result['literal_recursive_ternary']=dict(old_states=len(one),new_states=len(two),pairs_checked=check_counts,
        previous_word_extension_histogram=dict(Counter(completions.values())))
    (OUTPUT/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['seventeen']['intersection'],result['seventeen']['birth_profile'],separation,len(x),tied)
if __name__=='__main__':small()
