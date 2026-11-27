"""Verify the labelled two-base certificate by listing every subset of each rank."""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def subsets(xs, n):
    return (frozenset(t) for t in combinations(xs,n))


def every_family(parents):
    candidates = []
    valid = []
    for n in range(2,len(parents)+1):
        for part in subsets(parents,n):
            if all(parents[a] & parents[b] for a,b in combinations(part,2)):
                if n==2:
                    candidates.append(part)
                elif not set.intersection(*(parents[a] for a in part)):
                    valid.append(part)
    groups = [f for f in valid if not any(f < other for other in valid)]
    return set(groups + [f for f in candidates if not any(f <= g for g in groups)])


def check(doc):
    rows = doc['labelled_ranks']
    stars = doc['stars']
    groups = [set() for _ in stars]
    for i,j in combinations(range(len(stars)),2):
        if set(stars[i]) & set(stars[j]):
            groups[i].add(j)
            groups[j].add(i)
    multiplicity = Counter(d for s in stars for d in s)
    assert max(multiplicity.values()) == 2 and min(map(len, stars)) >= 3
    opening = [sum(multiplicity[d]==1 for d in s) for s in stars]
    live = [i for i,n in enumerate(opening) if n]
    assert [opening[i] for i in live] == [3,3,1,1,2,2]
    id0 = {next(iter(obj['points'])):name for name,obj in rows[0].items()}
    assert set(id0)==set(live)
    first = every_family({id0[i]:groups[i] for i in live})
    actual = Counter(frozenset(v['parents']) for v in rows[1].values())
    expected = Counter(first)
    for i in live:
        excess = opening[i] - sum(id0[i] in g for g in first)
        if excess:
            expected[frozenset([id0[i]])] = excess
    assert expected==actual
    parents = {k:set(v['parents']) for row in rows for k,v in row.items()}
    pts = {k:set(v['points']) for row in rows for k,v in row.items()}
    bases = sorted({q for row in rows[1:2] for v in row.values() for q in v['points'] if q<0})
    assert len(bases)==2
    for k,obj in rows[1].items():
        start_points = {i for i in live if id0[i] in parents[k]}
        if len(parents[k])>1:
            assert pts[k]==start_points
        else:
            i, = start_points
            assert len(pts[k]-start_points)==1 and opening[i]==2
    n2 = []
    n3 = []
    n1 = []
    for r in range(1,len(rows)-1):
        row = rows[r]
        next_row = rows[r+1]
        assert Counter(every_family({x:parents[x] for x in row})) == Counter(frozenset(parents[z]) for z in next_row)
        assert all(pts[z]==set.union(*(pts[x] for x in parents[z])) for z in next_row)
        for x,y in combinations(row,2):
            for a,b in combinations(parents[x]&parents[y],2):
                if any(pts[z] & set(bases) for z in parents[a]&parents[b]):
                    n1.append([x,y,a,b])
        for k in range(1,len(bases)+1):
            for b in subsets(bases,k):
                marked = {x:{p for p in parents[x] if b<=pts[p]} for x in row if b<=pts[x]}
                for q in every_family(marked):
                    if len(q)>=3 and not any(q<=parents[z] for z in next_row):
                        n3.append([sorted(q),sorted(b)])
                for z in next_row:
                    for x,y in combinations(parents[z],2):
                        if b<=pts[x]&pts[y] and not any(b<=pts[u] for u in parents[x]&parents[y]):
                            n2.append([z,sorted(b)])
    assert n1==[] and n2==[['8.1',[-2,-1]]] and n3==[]
    assert doc['order_first_difference']==10
    assert len(doc['proposed_parent_families_only'])==1 and len(doc['round_rule_families_only'])==2
    for result in doc['ordinary'].values():
        assert result['comparison']==['views',9,'rounds']
        assert result['sig0_difference_at_first']=={'predicted_only':[[3,2,2]],'ordinary_only':[[3,3,2]]}
    print('All rank rosters and supports verified by subsets. N1 holds, N2 fails only at the top on both bases, N3 holds.')


if __name__=='__main__':
    check(json.loads((HERE/'witness.json').read_text())['two_bases'])
