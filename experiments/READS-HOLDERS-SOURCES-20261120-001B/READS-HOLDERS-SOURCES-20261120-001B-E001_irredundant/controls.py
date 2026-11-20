"""Exact erasures and ordinary first-stage controls for irredundant presentations."""
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys

from pysat.solvers import Solver
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT/'artifacts'/HERE.parent.name/HERE.name
OLD = ROOT/'experiments/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth'
sys.path.insert(0,str(OLD))
from model import (accepts, allowed, bits, build, growth, mask_of, nae_lawful, ownership,
                   parity_local, reduced, width)
from pair_tables import archive_switch, seven


def deletions(rows,law):
    """Separate global and local tests, leaving the full original set of names."""
    n = width(rows)
    if law=='parity':
        forms = tuple(map(mask_of,rows))
        full = len(reduced(forms))
        global_essential, local_essential = [],[]
        for i,h in enumerate(forms):
            rest = forms[:i]+forms[i+1:]
            old_rank = len(reduced(rest))
            old_local_rank = old_rank-len(reduced(x & ~h for x in rest))
            full_local_rank = full-len(reduced(x & ~h for x in forms))
            global_essential.append(old_rank<full)
            local_essential.append(old_local_rank<full_local_rank)
        return global_essential,local_essential
    # Every wrapper j>n disables the two clauses defining one physical rule.
    # Compute whole-word feasibility after assigning a single violated rule,
    # and separately query the erased relation's local all-zero/all-one words.
    clauses = []
    for i,row in enumerate(rows):
        positive = [x+1 for x in row]
        gate = n+i+1
        clauses += [[gate,*positive],[gate,*[-x for x in positive]]]
    whole, local = [],[]
    with Solver(name='g3',bootstrap_with=clauses) as sat:
        for i,row in enumerate(rows):
            gated = [(1 if i==j else -1)*(n+j+1) for j in range(len(rows))]
            positive = [x+1 for x in row]
            defect = sat.solve(assumptions=[*gated,*positive])
            if defect:
                x = mask_of(j-1 for j in sat.get_model() if 0<j<=n)
                assert all(accepts((other,),x,'nae')==(i!=k) for k,other in enumerate(rows))
            whole.append(defect)
            try_zero = sat.solve(assumptions=[*gated,*[-v for v in positive]])
            try_one  = sat.solve(assumptions=[*gated,*positive])
            assert try_zero==try_one
            local.append(try_zero or try_one)
    return whole,local


def lawful(rows,law):
    return min(map(len,rows))>=3 and (all(i==1 for i in parity_local(rows)) if law=='parity' else nae_lawful(rows))


def next_stage(rows,law):
    status,births = growth(rows,law)
    if status!='births' or len(births)>256:
        return ('cap' if len(births)>256 else status),rows,births
    owner = ownership(rows)
    loose = {h:iter(sorted(x for x in r if len(owner[x])==1)) for h,r in enumerate(rows)}
    next_name = width(rows)
    extra = []
    for parents,price in births:
        extra.append(tuple(next(loose[h]) for h in parents)+tuple(range(next_name,next_name+price)))
        next_name += price
    return status,(*rows,*extra),births


def tree_source(rng,plus):
    n = rng.randrange(4,9)
    word = [rng.randrange(n) for _ in range(n-2)]
    occurrences = Counter(word)
    pairs = []
    for x in word:
        leaf = next(i for i in range(n) if occurrences[i]==0)
        pairs.append(tuple(sorted((leaf,x))))
        occurrences[leaf]=-1
        occurrences[x]-=1
    pairs.append(tuple(i for i in range(n) if occurrences[i]==0))
    if plus:
        pairs.append(rng.choice(sorted(set(combinations(range(n),2))-set(pairs))))
    degree = Counter(u for p in pairs for u in p)
    private = [max(0,3-degree[i])+int(rng.randrange(4)==0) for i in range(n)]
    return build(pairs,private)


def explosive_source(rng):
    joins = [(i,(i+1)%5) for i in range(5) for _ in range(1+rng.randrange(2))]
    return build(joins,[3]*5)


def unique_private(rows):
    counts = Counter(x for r in rows for x in r)
    return all(any(counts[x]==1 for x in row) for row in rows)


def stage(rows,law):
    valid = lawful(rows,law)
    global_,local = deletions(rows,law)
    assert global_==local
    return {'lawful':valid,'holders':len(rows),'names':width(rows),'all_essential':all(global_),
            'implied_holders':[i for i,v in enumerate(global_) if not v],
            'each_holder_has_private':unique_private(rows)}


def interval(k,n):
    if not n:
        return None
    return [0. if not k else float(beta.ppf(.025,k,n-k+1)),
            1. if k==n else float(beta.ppf(.975,k+1,n-k))]


def sample():
    rng=Random(20261120293)
    summaries,draws={},{}
    for panel in ('tree','tree_plus_one','explosive_five'):
        sample=[]
        for i in range(128):
            rows = explosive_source(rng) if panel=='explosive_five' else tree_source(rng,panel=='tree_plus_one')
            one = {'rows':rows}
            for law in ('nae','parity'):
                start = stage(rows,law)
                status,after,births = next_stage(rows,law) if start['lawful'] else ('ineligible',rows,())
                one[law]={'source':start,'growth':status,'births':len(births)}
                if status=='births':
                    one[law]['next']=stage(after,law)
            sample.append(one)
        draws[panel]=sample
        for law in ('nae','parity'):
            records=[r[law] for r in sample]
            good=[r for r in records if r['source']['lawful']]
            fresh=[r['next'] for r in good if r['growth']=='births']
            initial=sum(r['source']['all_essential'] for r in good)
            summaries[panel+'_'+law]={
                'draws':len(records),'lawful_sources':len(good),'irredundant_sources':initial,
                'irredundant_source_share_95_exact':interval(initial,len(good)),
                'sources_each_holder_private':sum(r['source']['each_holder_has_private'] for r in good),
                'growth_status':dict(Counter(r['growth'] for r in good)),
                'first_stages':len(fresh),'lawful_first_stages':sum(t['lawful'] for t in fresh),
                'irredundant_lawful_first_stages':sum(t['lawful'] and t['all_essential'] for t in fresh),
                'ratio_on_funded':interval(sum(t['all_essential'] for t in fresh),len(fresh)),
                'first_stages_each_holder_private':sum(t['each_holder_has_private'] for t in fresh)}
    return {'seed':20261120293,'summary':summaries,'draws':draws}


def candidate_sets(rows,words=None):
    n=width(rows)
    words=allowed(rows,'nae') if words is None else words
    seen=[]
    for s in range(1,1<<n):
        if s.bit_count()<3:
            continue
        projected={s & w for w in words}
        if len(projected)==(1<<s.bit_count())-2 and 0 not in projected and s not in projected:
            seen.append(tuple(bits(s)))
    return tuple(seen)


def force(rows):
    words=allowed(rows,'nae')
    candidates=candidate_sets(rows,words)
    need,_=deletions(candidates,'nae')
    mandatory=tuple(h for i,h in enumerate(candidates) if need[i])
    universe=range(1<<width(rows))
    reconstruct=tuple(x for x in universe if accepts(mandatory,x,'nae'))==words
    fixable=set()
    for x in set(universe)-set(words):
        repair=tuple(i for i in range(width(rows)) if x^1<<i in words)
        if repair in candidates:
            fixable.add(repair)
    assert fixable<=set(mandatory)
    return {'candidates':candidates,'mandatory':mandatory,'same_relation':reconstruct,
            'holders_recovered_by_single_flip':sorted(fixable)}


def literal_erasure(rows):
    n=width(rows)
    result={}
    for law in ('nae','parity'):
        old=set(allowed(rows,law))
        global_,local=deletions(rows,law)
        counts=[]
        for i,r in enumerate(rows):
            rest=rows[:i]+rows[i+1:]
            new={x for x in range(1<<n) if accepts(rest,x,law)}
            proj=lambda words:{mask_of(r)&x for x in words}
            assert global_[i]==(new!=old) and local[i]==(proj(old)!=proj(new))
            counts.append([len(new),len(proj(old)),len(proj(new))])
        result[law]={'solutions':len(old),'deletion_total_before_after_projections':counts,
                     'lawful':lawful(rows,law),'implied':[i for i,e in enumerate(global_) if not e],
                     'growth':growth(rows,law)}
    return result


def controls():
    # The complement permutation of pair names maps each set of incident
    # pairs to the triple of pairs avoiding a fixed original name.
    edges=tuple(combinations(range(4),2))
    star=tuple(tuple(i for i,p in enumerate(edges) if u in p) for u in range(4))
    other=tuple(tuple(i for i,p in enumerate(edges) if u not in p) for u in range(4))
    assert allowed(star,'nae')==allowed(other,'nae')
    nonminimal=((0,1,2),(3,4,5),(0,3,6),(1,2,4,5,6))
    sharpened=(*nonminimal[:3],(1,2,4,5))
    assert allowed(nonminimal,'nae')==allowed(sharpened,'nae')
    root=((0,1,2),)
    out={'six_named':{'both':[literal_erasure(z) for z in (star,other)],'forced':force(star),'rows':[star,other]},
         'older_seven':{'both':[literal_erasure(z) for z in (nonminimal,sharpened)],'rows':[nonminimal,sharpened]}}
    for law in ('nae','parity'):
        rows=root
        states=[]
        for age in range(4):
            detail=stage(rows,law)
            if age==1 and law=='nae': detail['from_all_candidates']=force(rows)
            states.append(detail)
            if age!=3:
                status,rows,_=next_stage(rows,law)
                assert status=='births'
        out['root_to_third_'+law]=states
    for name,source in [('switch',archive_switch),('displacement',seven)]:
        a,b,_,_=source()
        out[name]=[{'parity_essential':all(deletions(z,'parity')[0]),
                    'nae_essential':all(deletions(z,'nae')[0]),'width':width(z)} for z in (a,b)]
    # Uniform rates on an unrestricted triple vs a single four-place rule.
    control={}
    for n in (3,4):
        full=list(range(1<<n))
        words=allowed((tuple(range(n)),),'nae')
        control[n]={'solutions':[len(full),len(words)],
                    'pair_count':[sum((s&1)!=(s>>1&1) for s in w) for w in (full,words)]}
    out['single_support_vs_free']=control
    return out


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'controls.json').write_text(json.dumps(controls(),indent=2)+'\n')
    panel=sample()
    (OUT/'samples.json').write_text(json.dumps(panel,separators=(',',':'))+'\n')
    print(json.dumps(panel['summary']))


if __name__=='__main__':
    main()
