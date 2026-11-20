"""Secondary exact check of whether NAE pair counts and rates identify states in the census."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import factorial, prod
import gzip
import json
from pathlib import Path

from controls import OUT


def multiset_orders(labels):
    counts=Counter(labels)
    def visit(prefix):
        if len(prefix)==len(labels):
            yield tuple(prefix)
        else:
            for x in counts:
                if counts[x]:
                    counts[x]-=1
                    yield from visit((*prefix,x))
                    counts[x]+=1
    yield from visit(())


def canonical(n,weights):
    # A transposition preserving every weight can be quotiented before testing
    # permutations inside equal point profiles. Counting its factorial keeps
    # the full, named automorphism group.
    profiles=defaultdict(list)
    d=lambda i,j:weights[tuple(sorted((i,j)))]
    for i in range(n):
        profiles[tuple(sorted(d(i,j) for j in range(n) if j!=i))].append(i)
    group_orders=[]
    twin_factor=1
    for profile,indices in sorted(profiles.items()):
        classes=[]
        for i in indices:
            for bucket in classes:
                j=bucket[0]
                if all(d(i,k)==d(j,k) for k in range(n) if k not in (i,j)):
                    bucket.append(i)
                    break
            else:
                classes.append([i])
        twin_factor*=prod(factorial(len(c)) for c in classes)
        choices=[]
        for order in multiset_orders([k for k,c in enumerate(classes) for _ in c]):
            stacks=[iter(c) for c in classes]
            choices.append(tuple(next(stacks[k]) for k in order))
        group_orders.append(choices)
    best=None
    attain=0
    for parts in product(*group_orders):
        order=tuple(i for sub in parts for i in sub)
        image=tuple(d(i,j) for i,j in combinations(order,2))
        if best is None or image<best:
            best,attain=image,1
        elif image==best:
            attain+=1
    return best,attain*twin_factor


def main():
    with gzip.open(OUT/'census_cases.json.gz','rt') as f:
        book=json.load(f)
    result={}
    for key,by_law in book.items():
        n=int(key)
        pairs=tuple(combinations(range(n),2))
        measurements={mode:defaultdict(list) for mode in ('raw','rate')}
        for case in by_law['nae']:
            packed=int(case['state_words_hex'],16)
            words=[s for s in range(1<<n) if packed>>s & 1]
            d={(i,j):sum((x>>i ^ x>>j)&1 for x in words) for i,j in pairs}
            signature,aut=canonical(n,d)
            assert aut%case['state_automorphisms']==0
            for mode,label in [('raw',signature),('rate',tuple(Fraction(z,len(words)) for z in signature))]:
                measurements[mode][label].append((case,aut))
        out={}
        for mode,groups in measurements.items():
            number_tables = sum(factorial(n)//cases[0][1] for cases in groups.values())
            bad_named,ambiguous_orbits,largest,bad_example=0,0,1,None
            for sig,cases in groups.items():
                count=sum(aut//c['state_automorphisms'] for c,aut in cases)
                if count>1:
                    bad_named+=factorial(n)//cases[0][1]
                    ambiguous_orbits+=1
                    if bad_example is None:
                        c,aut=cases[0]
                        bad_example={'one_named_representative':c['presentations'][0]['supports'],
                                     'same_named_table_states':count,'state_orbits_in_table_orbit':len(cases),
                                     'table_automorphisms':aut,'state_automorphisms':c['state_automorphisms']}
                largest=max(largest,count)
            out[mode]={'distinct_named_tables':number_tables,'table_orbits':len(groups),
                       'ambiguous_named_tables_for_states':bad_named,'ambiguous_table_orbits_for_named_states':ambiguous_orbits,
                       'table_orbits_with_nonisomorphic_states':sum(len(cases)>1 for cases in groups.values()),
                       'max_distinct_named_states_per_named_table':largest,'first_example':bad_example}
        result[key]=out
    (OUT/'pair_readings.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{m:s['ambiguous_named_tables_for_states'] for m,s in v.items()} for k,v in result.items()}))


if __name__=='__main__':
    main()
