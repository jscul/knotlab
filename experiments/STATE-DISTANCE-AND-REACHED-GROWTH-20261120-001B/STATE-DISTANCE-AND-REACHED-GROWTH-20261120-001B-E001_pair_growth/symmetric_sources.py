"""Enumerate every 28-name holding invariant under the visible named symmetries."""
from collections import Counter
from functools import cache
from fractions import Fraction
from itertools import combinations, permutations, product
from math import prod
import json
from target import OUTPUT
from inherited_inversion import matrix
from census_rate_tables import nae_table


def moves(rows):
    first=rows[1:5]
    live=rows[5:]
    pairs=list(combinations(range(4),2))
    position={pair:k for k,pair in enumerate(pairs)}
    output=[]
    for perm in permutations(range(4)):
        points=list(perm)+[None]*24
        for k,(i,j) in enumerate(pairs):
            ij=tuple(sorted((perm[i],perm[j])))
            t=position[ij]
            new=live[t]; old=live[k]
            for x,a in zip((i,j),old[:2],strict=True):
                points[a]=next(b for b in new[:2] if b in first[perm[x]])
            for x,y in zip(old[2:],new[2:],strict=True): points[x]=y
        output.append(points)
    return output


def images(n,perms):
    table=[tuple(0 for _ in perms)]
    for bits in range(1,(1<<n)):
        rest=bits & (bits-1)
        ix=(bits-rest).bit_length()-1
        table.append(tuple(t | 1<<p[ix] for t,p in zip(table[rest],perms,strict=True)))
    return table


def candidate_orbits(rows):
    maps=moves(rows)
    old=images(16,maps)
    # For each fresh pair equality amounts to taking neither, either one, or both.
    fresh_groups=[]
    for counts in product(range(3),repeat=6):
        singleton=sum(v==1 for v in counts)
        if singleton>3: continue  # its 2^4 pointwise swaps already exceed 56/4.
        tup=tuple(v for k,a in enumerate(counts) for v in rows[5+k][2:2+a])
        bits=sum(1<<v for v in tup)
        all_copies=tuple(sum(1<<p[v] for v in tup) for p in maps)
        fresh_groups.append((sum(counts),singleton,bits,all_copies))
    found={}
    for fixed,old_images in enumerate(old):
        if fixed!=min(old_images): continue
        r0=(fixed&15).bit_count()
        r1=fixed.bit_count()-r0
        old_order=len(set(old_images))
        for r2,t,fb,fbperm in fresh_groups:
            q=r0+r1+r2
            if q<4: continue
            twice=1<<t
            limit=min(56//q,*[2*n//r for n,r in zip((4,12,12),(r0,r1,r2)) if r])
            if twice*old_order>limit:continue
            unique=set()
            for a,b in zip(old_images,fbperm,strict=True):
                unique.add(a|b)
                if len(unique)*twice>limit:break
            else:
                s=len(unique)*twice
                counts=(s*r0//4,s*r1//12,s*r2//12)
                assert all(k*n==s*r for k,n,r in zip(counts,(4,12,12),(r0,r1,r2),strict=True))
                key=min(unique)
                if key in found:continue
                physical=set()
                for rep in unique:
                    singles=[i for i in range(6) if (rep>>(16+2*i)&3)==1]
                    for flips in range(1<<len(singles)):
                        mask=rep
                        for k,i in enumerate(singles):
                            if flips>>k&1:mask^=3<<(16+2*i)
                        physical.add(mask)
                assert len(physical)==s
                found[key]=(counts,tuple(sorted(physical)))
    return list(found.values()),maps



def index_orbits(rows, even=False):
    group=moves(rows)
    if even: group=[p for p in group if sum(p[i]>p[j] for i,j in combinations(range(4),2))%2==0]
    old_images=images(16,group)
    later=images(12,[[p[v]-16 for v in range(16,28)] for p in group])
    found={}
    for old,oi in enumerate(old_images):
        if old!=min(oi):continue
        root=(old&15).bit_count()
        mid=old.bit_count()-root
        order=len(set(oi))
        if order>14 or order*root>8 or order*mid>24:continue
        for newer,ni in enumerate(later):
            a=(newer & 0x555).bit_count(); b=newer.bit_count()-a
            q=root+mid+a+b
            if q<4:continue
            orbit_size=max(order,len(set(ni)))
            kinds=(4,12,6,6); uses=(root,mid,a,b)
            if any(orbit_size*m>2*n for m,n in zip(uses,kinds)):continue
            orb=tuple(sorted({x|(y<<16) for x,y in zip(oi,ni,strict=True)}))
            if old|(newer<<16)!=orb[0] and orb[0] in found:continue
            m=len(orb)
            if any(m*v>2*n for v,n in zip(uses,kinds)):continue
            degrees=tuple(m*v//n for v,n in zip(uses,kinds))
            assert all(m*v==u*n for v,n,u in zip(uses,kinds,degrees))
            found[orb[0]]=degrees,orb
    return list(found.values()),group

def covers(orbits):
    # Every orbit occupies at least one of the six available per-name degree units.
    def visit(first, deg, selected):
        if min(deg)>0:yield deg,selected
        for j in range(first,len(orbits)):
            cost,_=orbits[j]
            new=tuple(x+y for x,y in zip(deg,cost))
            if max(new)<=2:
                yield from visit(j+1,new,selected+(j,))
    return visit(0,(0,)*len(orbits[0][0]),())


def count_words(rows):
    # Inclusion-exclusion. A family of constant rows contributes one binary
    # choice per connected component of its common-name constraints.
    total=0
    free=28
    def count(ix,sign,groups):
        nonlocal total
        if ix==len(rows):
            total+=sign*(1<<(free-sum(v.bit_count()-1 for v in groups)))
            return
        count(ix+1,sign,groups)
        merged=rows[ix]; rest=[]
        for group in groups:
            if merged & group: merged|=group
            else:rest.append(group)
        count(ix+1,-sign,(*rest,merged))
    count(0,1,())
    return total


def run(mode):
    data=json.loads((OUTPUT/'target.json').read_text());stage=data['observed_holders']
    cs=matrix(data['uniform']['fractions'],28)
    denom=data['uniform']['lcm_individual_triple_word_denominator']
    orbits,perms=candidate_orbits(stage) if mode=="full" else index_orbits(stage, mode=="even")
    # The full table need only be invariant under the tested subgroup.
    for g in perms:
        assert all(cs[x][y]==cs[g[x]][g[y]] for x,y in combinations(range(28),2))
    for h in stage[5:]:
        a,b=h[2:]
        assert all(cs[a][x]==cs[b][x] for x in range(28) if x not in (a,b))
    atlas=list(covers(orbits))
    valid=[]
    types=Counter()
    retained=0
    total_subset_ops=0
    for deg,selection in atlas:
        forms=tuple(m for k in selection for m in orbits[k][1])
        types[len(forms)]+=1
        # Subsets or repeated rows cannot coexist in an essential cover.
        if any((a & b) in (a,b) for a,b in combinations(forms,2)):continue
        retained+=1
        total_subset_ops+=1<<len(forms)
        n=count_words(forms)
        if n%denom==0:
            valid.append((n,forms))
    expected={sum(1<<y for y in row) for row in stage}
    after_count=list(valid)
    valid=[]
    denominator=0
    checks=[]
    for n,forms in after_count:
        rows=tuple(tuple(i for i in range(28) if m>>i&1) for m in forms)
        denominator,counts,_=nae_table(rows,())
        assert denominator==n
        failed=sum(Fraction(counts[i,j],n)!=(1-cs[i][j])/2 for i,j in combinations(range(28),2))
        checks.append(dict(holders=rows,different_named_pair_entries=failed))
        if failed==0:valid.append((n,forms))
    assert len(valid)==1 and set(valid[0][1])==expected
    report=dict(named_action_order={"full":1536,"indices":24,"even":12}[mode],candidate_orbits=len(orbits),cover_count=len(atlas),cover_sizes=types,
        incomparable_covers=retained,after_count_only=len(after_count),checks_after_count=checks,number_of_inclusion_exclusion_terms=total_subset_ops,triple_atom_denominator=denom,
        survivors=[dict(allowed_words=n,holders=[[i for i in range(28) if m>>i&1] for m in forms]) for n,forms in valid],
        qualifier={'full':'All 24 permutations of the four indices and six independent sibling exchanges.', 'indices':'Only the 24 index permutations, fixing the choice of sibling tokens.', 'even':'Only the 12 even index permutations, fixing the choice of sibling tokens.'}[mode]+' No age or live status assumed.')
    (OUTPUT/('symmetric_sources'+('' if mode=='full' else '_'+mode)+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(len(orbits),len(atlas),retained,total_subset_ops,len(valid))

if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else 'full')
