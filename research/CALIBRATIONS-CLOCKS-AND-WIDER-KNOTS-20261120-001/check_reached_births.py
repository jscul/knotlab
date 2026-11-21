"""Recount funded births and compare the multiset of measured pair rates independently."""
from collections import Counter, defaultdict
from itertools import combinations
from math import gcd
from pathlib import Path
import gzip
import json

from check_wider_pairs import TruthColumns

EPIC = Path(__file__).resolve().parent.name
DATA = Path(__file__).resolve().parents[2] / 'artifacts' / (EPIC+'C') / (EPIC+'C-E001_wider_meetings')


def read(name):
    with gzip.open(DATA / name, 'rt') as stream:
        return json.load(stream)


def maximal(candidates, chosen, unused, excluded):
    """Enumerate maximal sets of pairwise witnessed live holders."""
    if not unused and not excluded:
        yield chosen
        return
    possible=unused|excluded
    pivot=max(possible,key=lambda p:len(unused & candidates[p]))
    for i in sorted(unused-candidates[pivot]):
        yield from maximal(candidates,chosen|{i},unused & candidates[i],excluded & candidates[i])
        unused.remove(i)
        excluded.add(i)


def next_count(stage):
    held_by=defaultdict(list)
    for holder,row in enumerate(stage['rows']):
        for mark in row:
            held_by[mark].append(holder)
    loose=Counter(holders[0] for holders in held_by.values() if len(holders)==1)
    if not loose:
        return 'closed',0
    live=set(loose)
    named_neighbors=defaultdict(set)
    for holders in held_by.values():
        if len(holders)==2:
            a,b=holders
            if b in live:named_neighbors[a].add(b)
            if a in live:named_neighbors[b].add(a)
    witnesses=list(named_neighbors.values())
    candidates={u:set() for u in live}
    pairs=set()
    for witness in witnesses:
        for a,b in combinations(sorted(witness),2):
            candidates[a].add(b)
            candidates[b].add(a)
            pairs.add((a,b))
    groups=[]
    for group in maximal(candidates,set(),set(live),set()):
        if len(group)>=3 and not any(group<=w for w in witnesses):
            groups.append(group)
            pairs.difference_update(combinations(sorted(group),2))
    groups.extend(pairs)
    demand=Counter(v for group in groups for v in group)
    if any(demand[v]>loose[v] for v in live):
        return 'stall',0
    return 'births',len(groups)+sum(loose[v]-demand[v] for v in live)


def signed_pair_multiset(values, denominator):
    histogram=Counter(values)
    entries=[]
    for value,count in histogram.items():
        divisor=gcd(value,denominator)
        entries.append((value//divisor,denominator//divisor,count))
    return tuple(sorted(entries))


def parity_classes(rows,width):
    """Two bits always agree exactly when their residues modulo the row space agree."""
    basis={}
    def reduce_word(word):
        for bit in sorted(basis,reverse=True):
            if word & (1 << bit):word ^= basis[bit]
        return word
    for row in rows:
        word=reduce_word(sum(1 << x for x in row))
        if word:basis[word.bit_length()-1]=word
    same=Counter(reduce_word(1 << i) for i in range(width))
    return tuple(sorted(same.values())),1 << (width-len(basis))


def main():
    sources=read('census_stages.json.gz')
    rates=read('census_rate_tables.json.gz')
    cache={}
    summary={}
    for law in ('nae','parity'):
        decisions=defaultdict(set)
        actual=defaultdict(int)
        parity_inputs=defaultdict(list)
        literal=numerators=0
        for r in rates[law]['records']:
            start=sources[law][r['source_index']]
            s=next(s for s in start['stages'] if s['age']==r['age'])
            birth=next_count(s)
            assert birth==(s['next_status'],s['next_birth_count'])
            actual[birth[0]]+=1
            size=r['allowed_states']
            width=s['width']
            if law=='parity':
                key,number=parity_classes(s['rows'],width)
                assert number==size
                decisions[key].add(birth)
                parity_inputs[key].append((start['source_width'],len(start['source_rows']),s['age'],birth[1]))
                continue
            counts=r['disagreement_counts']
            assert len(counts)==width*(width-1)//2
            key=(width,signed_pair_multiset(counts,size))
            decisions[key].add(birth)
            if width<=16:
                if width not in cache:cache[width]=TruthColumns(width)
                truth=cache[width];support=truth.all
                for row in s['rows']:support &= truth.allowed(row)
                assert support.bit_count()==size
                replay=[(support & mask).bit_count() for mask in truth.pairs.values()]
                assert replay==counts
                literal+=1
                numerators+=len(counts)
        summary[law]={"independent_next_outcomes":actual,"literal_word_replays":literal,
                      "literal_named_pair_numerators":numerators}
        if law=='nae':
            summary[law].update(pair_multisets=len(decisions),multisets_with_distinct_births=sum(len(x)>1 for x in decisions.values()))
        else:
            best=None
            for key,group in parity_inputs.items():
                for left,right in combinations(group,2):
                    if left[3]==right[3]:continue
                    rank=(max(left[0],right[0]),sum(key),left[1]+right[1],left[2]+right[2])
                    candidate=(rank,tuple(sorted((left[3],right[3]))))
                    if best is None or candidate<best:best=candidate
            summary[law].update(pair_table_types=len(decisions),
                                types_with_distinct_births=sum(len({b[1] for b in group})>1 for group in decisions.values()),
                                minimum_ambiguity=best)
    return summary


if __name__=='__main__':
    print(json.dumps(main(),indent=2))
