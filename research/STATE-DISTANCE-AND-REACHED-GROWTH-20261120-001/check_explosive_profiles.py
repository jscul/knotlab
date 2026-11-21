"""Recompute each next parent holding and fresh grant in the two-weight explosive census."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
EPIC = Path(__file__).resolve().parent.name
FAMILY = ROOT / 'artifacts' / (EPIC+'B') / (EPIC+'B-E001_pair_growth')
sys.path.insert(0,str(ROOT/'research'/'CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001'))
from check_reached_births import maximal, signed_pair_multiset


def group_roster(live, witnesses):
    around = {i:set() for i in live}
    pairs = set()
    for w in witnesses:
        for i,j in combinations(sorted(w),2):
            around[i].add(j)
            around[j].add(i)
            pairs.add((i,j))
    large = [tuple(sorted(c)) for c in maximal(around,set(),set(live),set())
             if len(c)>=3 and not any(c<=w for w in witnesses)]
    for g in large:
        pairs.difference_update(combinations(g,2))
    return sorted([*large,*pairs])


def parent_prices(rows, law):
    held = defaultdict(list)
    for i,h in enumerate(rows):
        for x in h:
            held[x].append(i)
    free = defaultdict(list)
    incident = defaultdict(set)
    for x,owners in held.items():
        if len(owners)==1:
            free[owners[0]].append(x)
        else:
            a,b=owners
            incident[a].add(b)
            incident[b].add(a)
    live=set(free)
    parents=group_roster(live,[v & live for v in incident.values()])
    used=Counter(i for g in parents for i in g)
    if any(used[i]>len(free[i]) for i in live):
        return [],'stall'
    if not live:
        return [],'closed'
    for i in sorted(live):
        parents.extend([(i,)]*(len(free[i])-used[i]))
    future=defaultdict(set)
    for i,ps in enumerate(parents):
        for k in ps:
            future[k].add(i)
    demand=Counter(i for g in group_roster(range(len(parents)),list(future.values())) for i in g)
    basis={}
    def reduce_word(word):
        for b in sorted(basis,reverse=True):
            if word & (1<<b):
                word ^= basis[b]
        return word
    if law=='parity':
        for h in rows:
            w=reduce_word(sum(1<<x for x in h))
            if w:
                basis[w.bit_length()-1]=w
    openings={i:iter(sorted(free[i])) for i in free}
    result=[]
    for j,g in enumerate(parents):
        inputs=sum(1<<next(openings[i]) for i in g)
        price=max(1,3-len(g),demand[j])
        if law=='parity' and reduce_word(inputs)==0:
            assert demand[j]==0
            price=0
        result.append((tuple(sorted(tuple(sorted(rows[i])) for i in g)),price))
    return sorted(result),'births'


def run():
    def read(name):
        return json.loads(gzip.decompress((FAMILY/name).read_bytes()))
    stages=read('explosive_stages.json.gz')
    readings=read('explosive_rates.json.gz')['reads']
    result={}
    for law, pop in stages.items():
        verified={}
        compared=0
        for source in pop['sources']:
            for stage in source['stages']:
                rebuilt,status=parent_prices(stage['rows'],law)
                original=sorted((tuple(sorted(tuple(sorted(p)) for p in ps)),q) for ps,q in stage['profile'])
                assert rebuilt==original and status==stage['next_status']
                verified[source['id'],stage['age']]=tuple(rebuilt)
                compared+=len(rebuilt)
        reports={}
        for weight in ['uniform','inherited']:
            tables=defaultdict(set)
            for r in readings[law]:
                data=r['weights'][weight]
                sizes = Counter((len(ps),q) for ps,q in verified[r['source_id'],r['age']])
                key=signed_pair_multiset(data['counts'],data['total'])
                tables[key].add(tuple(sorted(sizes.items())))
            reports[weight]=dict(rate_multisets=len(tables),
                                 multisets_with_different_price_or_parent_arities=sum(len(v)>1 for v in tables.values()),
                                 multisets_with_different_birth_counts=sum(len({sum(n for pair,n in t) for t in v})>1 for v in tables.values()))
        result[law]=dict(reached_physical_stages=len(verified),individual_parent_and_price_rows=compared,
                         fully_measured_rate_tables=len(readings[law]),by_weight=reports)
    return result


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
