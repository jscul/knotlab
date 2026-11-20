"""Check two state-only recovery certificates and the eight-name pair-table collision."""
from collections import Counter
from itertools import combinations, permutations
from functools import lru_cache
import gzip
import json

from controls import OUT, allowed, deletions, growth, lawful, mask_of, next_stage
from model import literal_counts


@lru_cache(maxsize=None)
def violates_mask(n,support):
    pattern=mask_of(support)
    return sum(1<<w for w in range(1<<n) if w & pattern in (0,pattern))


def state_certificates(n,packed):
    words=[w for w in range(1<<n) if packed>>w & 1]
    # Candidate extraction uses only the support width upper bound supplied by
    # the number of names; the physical presentation is unavailable here.
    rows=displayed_candidates(n,words)
    candidate_masks=[violates_mask(n,row) for row in rows]
    all_words=(1<<(1<<n))-1
    violated=0
    twice=0
    for mask in candidate_masks:
        twice |= violated & mask
        violated |= mask
    assert all_words ^ violated == packed
    only=violated & ~twice
    mandatory=[row for row,mask in zip(rows,candidate_masks) if mask & only]
    cover=0
    for row in mandatory:cover|=violates_mask(n,row)
    one_flip=set()
    for w in range(1<<n):
        if not packed>>w & 1:
            fixes=tuple(i for i in range(n) if packed>>(w ^ 1<<i) & 1)
            if fixes in rows:one_flip.add(fixes)
    assert one_flip <= set(mandatory)
    flip_cover=0
    for row in one_flip:flip_cover |= violates_mask(n,row)
    return cover==violated,flip_cover==violated


def displayed_candidates(n,words):
    rows=[]
    for size in range(3,n+1):
        for support in combinations(range(n),size):
            form=mask_of(support)
            local={w & form for w in words}
            if 0 not in local and form not in local and len(local)==(1<<size)-2:
                rows.append(support)
    return tuple(rows)


def residual_certificate(rows):
    # Remove one complete support and ensure every other holder keeps at
    # least two positions in a component other than an isolated odd cycle.
    for i,row in enumerate(rows):
        removed=set(row)
        remaining={j:set(other)-removed for j,other in enumerate(rows) if i!=j}
        if any(len(x)<2 for x in remaining.values()):
            return False
        pending=set(remaining)
        while pending:
            start=pending.pop()
            stack=[start]
            component=[start]
            while stack:
                j=stack.pop()
                reached={k for k in pending if remaining[j]&remaining[k]}
                stack.extend(reached)
                component.extend(reached)
                pending-=reached
            if len(component)%2==1 and all(len(remaining[k])==2 for k in component):
                counts=Counter(x for k in component for x in remaining[k])
                if all(c==2 for c in counts.values()):
                    return False
    return True


def preserved_class(rows):
    holders=[set(row) for row in rows]
    if any(len(a-b)<2 or len(b-a)<2 for a,b in combinations(holders,2)):
        return False
    return not any(a&b and a&c and b&c for a,b,c in combinations(holders,3))


def physical_samples():
    panels=json.loads((OUT/'samples.json').read_text())['draws']
    summary={}
    for name,sources in panels.items():
        q=Counter()
        for row in sources:
            seed=tuple(map(tuple,row['rows']))
            strong=preserved_class(seed)
            q['sources']+=1
            q['class_sources']+=strong
            if strong:
                assert residual_certificate(seed)
            status,after,_=next_stage(seed,'nae')
            if status=='births':
                q['funded']+=1
                if strong:
                    assert preserved_class(after) and residual_certificate(after)
                    q['class_funded_and_preserved']+=1
        summary[name]=dict(q)
    return summary


def eight_names():
    a=((0,1,2,3),(0,4,5,6),(1,4,5,7),(2,3,6,7))
    p=(0,6,2,3,4,5,1,7)
    b=tuple(sorted(tuple(sorted(p[i] for i in r)) for r in a))
    u,v=(allowed(rows,'nae') for rows in (a,b))
    n,d=literal_counts(u,8)
    assert (n,d)==literal_counts(v,8) and u!=v
    table_symmetries=0
    state_symmetries=0
    words=set(u)
    for perm in permutations(range(8)):
        if any(d[tuple(sorted((perm[i],perm[j])))]!=count for (i,j),count in d.items()):
            continue
        table_symmetries+=1
        if all(mask_of(perm[k] for k in range(8) if word>>k&1) in words for word in words):
            state_symmetries+=1
    assert (table_symmetries,state_symmetries)==(64,32)
    for rows in (a,b):
        assert lawful(rows,'nae') and all(deletions(rows,'nae')[0]) and growth(rows,'nae')==('closed',())
    return {'rows':[a,b],'permutation':p,'solutions_each':n,'one_word_only_in_first':min(set(u)-set(v)),
            'one_word_only_in_second':min(set(v)-set(u)),'asymmetric_difference_counts':[len(set(u)-set(v)),len(set(v)-set(u))],
            'D_lexicographic':list(d.values()),'table_and_state_symmetries':[table_symmetries,state_symmetries],'both_sources':'lawful, irredundant, already closed'}


def main():
    with gzip.open(OUT/'census_cases.json.gz','rt') as f:
        all_sizes=json.load(f)
    results={}
    for ns,laws in all_sizes.items():
        n=int(ns)
        counters=Counter()
        failures=[]
        for case in laws['nae']:
            mandatory,flips=state_certificates(n,int(case['state_words_hex'],16))
            physical=case['presentations'][0]['supports']
            structural=residual_certificate(physical)
            assert not structural or flips
            if mandatory:
                assert case['named_presentations_per_state']==1
            for label,success in [('mandatory',mandatory),('one_flip',flips),('residual',structural)]:
                counters[label+'_orbits']+=int(success)
                counters[label+'_named_states']+=case['named_states_in_orbit']*success
            if not mandatory:
                failures.append({'one_representative':physical,'count_named':case['named_states_in_orbit'],
                                 'named_presentations_per_state':case['named_presentations_per_state']})
        results[ns]={'state_orbits':len(laws['nae']),'covered':dict(counters),'unresolved_by_mandatory':failures}
    (OUT/'certificates.json').write_text(json.dumps({'widths':results,'eight_names':eight_names(),'preserved_class_samples':physical_samples()},indent=2)+'\n')
    print([(n,v['state_orbits'],v['covered']['mandatory_orbits'],
            v['covered']['one_flip_orbits'],v['covered']['residual_orbits']) for n,v in results.items()])


if __name__=='__main__':
    main()
