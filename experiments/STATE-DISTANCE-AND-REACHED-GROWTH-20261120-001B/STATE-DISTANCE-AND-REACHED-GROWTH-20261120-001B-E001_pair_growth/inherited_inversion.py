"""Exact age-free checks for the recursively weighted 28-name table."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from math import lcm
import json

from target import OUTPUT, advance, roster, width
from census_rate_tables import nae_table


def matrix(rates, n):
    result=[[Fraction(i==j) for j in range(n)] for i in range(n)]
    for (i,j),r in zip(combinations(range(n),2),rates,strict=True):
        result[i][j] = result[j][i] = 1-2*Fraction(r)
    return result


def min_names(row, allowed, u):
    lower=min(row[v] for v in allowed if v!=u)
    return sorted(v for v in allowed if v!=u and row[v]==lower)


def cycle_types():
    # The four J witnesses have residual degree two, with no self-meeting.
    a,b,c,d=range(4)
    for omit in (((a,b),(c,d)),((a,c),(b,d)),((a,d),(b,c))):
        rest=[pair for pair in combinations(range(4),2) if pair not in omit]
        yield tuple(rest)
        yield tuple(v for pair in omit for v in (pair,pair))


def test():
    data=json.loads((OUTPUT/'target.json').read_text())
    c=matrix(data['inherited']['fractions'],28)
    orig, *remaining = map(tuple,data['observed_holders'])
    old=remaining[:4]
    now=remaining[4:]
    twos={tuple(h[-2:]) for h in now}
    allnames=set(range(28))
    # All twelve middle rows have only two minimizers. All four root decoys
    # have a strictly smaller subset with the full monochrome probability.
    bad_roots=[]
    for i,H in enumerate(old):
        M=min_names(c[i],allnames,i)
        triple=H[1:]
        mono=(1+sum(c[a][b] for a,b in combinations(triple,2)))/4
        assert len(M)==6 and set(triple)<set(M) and mono==-c[i][M[0]]
        bad_roots.append([i,M,list(triple),str(mono)])
    assert all(len(min_names(c[i],allnames,i))==2 for i in range(4,16))
    assert all(min_names(c[f],allnames,f)==sorted(set(h)-{f}) for h in now for f in h[-2:])
    assert data['inherited']['forced_ternaries']==0
    # If a sibling v were old, the other two inputs a,b remain visible at
    # the preceding cut; arity three and the positive ternary projection
    # already exclude its proposed previous row.
    for a,b,f,g in now:
        assert set(min_names(c[f],allnames,f))=={a,b,g}
        assert set(min_names(c[g],allnames,g))=={a,b,f}
    tested=0
    maps=[]
    for mask in range(1,1<<6):
        hs=[h for k,h in enumerate(now) if mask>>k&1]
        hidden={v for h in hs for v in h[2:]}
        avail=allnames-hidden
        for h in hs:
            for x in h[:2]:
                K=next(row for row in old if x in row)
                assert min_names(c[x],avail,x)==sorted(set(K)-{x})
                tested+=1
        maps.append([mask,len(hs)])
    # Choose the representative with absent pairs (0,1) and (2,3). The six
    # reduced witness types cover the others by the four underlying indices.
    missing=(0,5)
    sel=[now[k] for k in range(6) if k not in missing]
    avail=sorted(allnames-{u for h in sel for u in h[2:]})
    old_entries=[(1-c[i][j])/2 for i,j in combinations(avail,2)]
    denom=lcm(*(r.denominator for r in old_entries))
    old_multiset=Counter(old_entries)
    tested_types=[]
    # In circular order H0,H1,H2,H3 allocate two of the four J-H places
    # as loose at each H and assign the other two to its two adjacent J's.
    H=[(4*i,4*i+1,4*i+2,4*i+3) for i in range(4)]
    for pattern in cycle_types():
        W=[[4*i+3,4*((i+1)%4)+2] for i in range(4)]
        for v,(a,b) in enumerate(pattern,16):
            W[a].append(v);W[b].append(v)
        rows=tuple(map(tuple,H+W))
        total,counts,_=nae_table(rows,())
        counts=Counter(Fraction(x,total) for x in counts.values())
        reduced={u:k for k,u in enumerate(sorted({u for row in W for u in row}))}
        older=tuple(tuple(reduced[x] for x in row) for row in W)
        _,_,candidate=advance(older,'nae')
        count_two=sum(len(p)==2 for p,f in candidate)
        assert count_two in (0,2)
        assert old_multiset!=counts
        tested_types.append(dict(residual_meetings=pattern,source_words=total,compatible_denominator=(total%denom==0),uniform_multiset_matches=False,actual_antecedent_binary_births=count_two,antecedent_next_counts=len(candidate)))
    result=dict(root_decoys=bad_roots,subset_tests=63,spent_input_minimizer_checks=tested,all_forced_former_holders=True,
                width20_target_rate_denominator=denom,cycle_candidate_types=tested_types,unreached_competitors='inherited stage weights require a supplied history')
    (OUTPUT/'inherited_inversion.json').write_text(json.dumps(result,indent=2)+'\n')
    print(denom, tested, [(x['source_words'],x['actual_antecedent_binary_births']) for x in tested_types])

if __name__=='__main__':
    test()
