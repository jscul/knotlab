"""Allow a carrier to have different excluded signs in different lower clauses."""

import argparse
from collections import Counter
from contextlib import contextmanager
import ctypes
from functools import cache
import gzip
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from time import perf_counter

import numpy as np

from alternative_read import CODE, HERE, SOURCES, Source, WORDS, masks_to_triples, pairings


SLOTS = tuple(combinations(range(6),3))
TABLE = {(t,words):sum(1<<i for i,w in enumerate(WORDS) if tuple(w[j] for j in t)==words)
         for t in SLOTS for words in product((0,1), repeat=3)}
ALL = (1<<64)-1


@contextmanager
def mixed_sets():
    with NamedTemporaryFile(prefix='alternative_mixed_',suffix='.so',dir=HERE) as handle:
        subprocess.run(['g++','-std=c++17','-O3','-fPIC','-shared',str(HERE/'alternative_mixed.cpp'),
                        '-o',handle.name],check=True,env=dict(os.environ,TMPDIR=str(HERE)))
        lib=ctypes.CDLL(handle.name)
        ptr=ctypes.c_void_p
        for key,res,args in [('find',ptr,[ctypes.POINTER(CODE),ctypes.c_size_t]),('size',ctypes.c_size_t,[ptr]),
                             ('sets',ctypes.POINTER(CODE*6),[ptr]),('counts',ctypes.POINTER(ctypes.c_uint64),[ptr]),
                             ('release',None,[ptr])]:
            fn=getattr(lib,'mixed_'+key)
            fn.restype=res
            fn.argtypes=args
        def find(data):
            arr=np.asarray(data,dtype=np.uint32,order='C')
            r=lib.mixed_find(arr.ctypes.data_as(ctypes.POINTER(CODE)),len(data))
            try:
                sets=lib.mixed_sets(r)
                return list(lib.mixed_counts(r)[:3]),[tuple(sets[j]) for j in range(lib.mixed_size(r))]
            finally:
                lib.mixed_release(r)
        yield find


@cache
def eligible_roles(places):
    found=[]
    for pairs in pairings(set(range(6))):
        if all(all(len(set(t).intersection(p))==1 for p in pairs) for t in places):
            for bidx,both in enumerate(pairs):
                b,c=pairs[:bidx]+pairs[bidx+1:]
                found.append((both,b,c))
    return found


@cache
def target(pairs,signs):
    a,b,c=pairs
    def test(w):
        return all(w[i]==signs[i] for i in a) and any(w[i]==signs[i] for i in b) and any(w[i]==signs[i] for i in c)
    return sum(1<<i for i,w in enumerate(WORDS) if test(w))


@cache
def extensions(quad):
    places=tuple(t for t,word in quad)
    signs=[set() for _ in range(6)]
    for t,word in quad:
        for i,bit in zip(t,word): signs[i].add(bit)
    if not all(signs) or max(map(len,signs))<2:
        return ()
    tables=[TABLE[item] for item in quad]
    excluded=tables[0]|tables[1]|tables[2]|tables[3]
    result=[]
    for roles in eligible_roles(places):
        a,b,c=roles
        if any(len(signs[i])!=1 for i in a): continue
        signs_a=[next(iter(signs[i])) for i in a]
        for others in product((0,1),repeat=4):
            sig=[0]*6
            for i,v in zip((*a,*b,*c),(*signs_a,*others)):sig[i]=v
            sig=tuple(sig)
            upper111=target(roles,sig)
            if upper111 & ~excluded:continue
            # The four lower clauses must each be needed, as a virtual test.
            assert all(upper111 & cell & ~(tables[(j+1)%4]|tables[(j+2)%4]|tables[(j+3)%4])
                       for j,cell in enumerate(tables))
            result.append((roles,sig))
    return tuple(result)


def signed_rules(data):
    result={}
    for triple in data:
        lits=tuple(sorted(triple))
        supp=tuple(x>>1 for x in lits)
        assert supp not in result
        result[supp]=tuple(x&1 for x in lits)
    return result


def inferred(six,rules):
    local=[(t,rules[s]) for t in SLOTS if (s:=tuple(six[i] for i in t)) in rules]
    results=[]
    for quad in combinations(local,4):
        for roles,signs in extensions(quad):
            order=sum(roles,())
            grouped=tuple((six[i]<<1)|signs[i] for i in order)
            indices=tuple(tuple(order.index(i) for i in clause) for clause,_ in quad)
            lower=tuple((ix,tuple(r)) for ix,(_,r) in zip(indices,quad))
            results.append((grouped,lower))
    return results


def notes(source, group, lower, upper, present, pair_free, restored):
    counts=[]
    for places,missing in lower:
        masks=[source.value(group[i]|1) for i in places]
        row=[0,0,0]
        observed=[]
        for raw in product((0,1),repeat=3):
            cell=source.legal
            for v,b in zip(masks,raw): cell &= v if b else ~v
            if not cell:continue
            observed.append(raw)
            for j,v in enumerate(upper):row[j]+=bool(cell&v and cell&~v)
        assert len(observed)==7 and missing not in observed
        counts.append(row)
    passed = pair_free and all(all(row) for row in counts)
    return passed,{'carriers A0,A1,B0,B1,C0,C1':masks_to_triples([i>>1 for i in group]),
                   'agreement values counted as true':[i&1 for i in group],
                   'four lower triples by carrier index, with the missing agreement word':lower,
                   'upper words':present,'free in pairs':pair_free,
                   'lower-cell counts with each upper reading varying':counts,
                   'allowed source states':source.allowed,'source laws':source.supports,
                   'source laws before growth':source.original,'111 states restored on each single-law deletion':restored}


def controls(find):
    chosen=tuple(3<<(2*i) for i in range(6))
    # A lower clause in this fixture uses the other C reading with an opposite
    # sign in place of its usual positive choice. All four still cover 111.
    directions = (((0,2,4),(1,1,1)),((1,2,5),(1,1,1)),((1,3,5),(1,1,0)),((0,3,5),(1,1,1)))
    data=[[chosen[i]*2+s for i,s in zip(t,w)] for t,w in directions]
    assert find(data)[1]==[chosen]
    rules=signed_rules(data)
    found=inferred(chosen,rules)
    assert any(tuple((m<<1)|1 for m in chosen)==group for group,lower in found)
    for omit in range(4):assert not find(data[:omit]+data[omit+1:])[1]
    return {'planted mixed-sign family processed':True,'single lower deletions losing that family':4,
            'all qualifying oriented upper readings on that fixture':len(found)}


def read_stage(raw,find,archive):
    data=raw['clauses']; start=int(str(raw.get('start',raw.get('census_entry'))).split()[-1]); rn=raw['round']
    counts,sets=find(data)
    rules=signed_rules(data) if sets else {}
    found=[]
    for six in sets:found.extend(inferred(six,rules))
    covers=[]; successes=set(); born=set(); examples={}; all7=0
    if found:source=Source(archive[start],rn)
    for group,lower in found:
        up,present,free,restored=source.upper_properties(group)
        valid,detail=notes(source,group,lower,up,present,free,restored)
        covers.append(valid)
        if valid:
            successes.add(group)
            if any(restored[source.original:]):born.add(group)
            all7+=len(present)==7
        tag='birth-essential step' if valid and any(restored[source.original:]) else 'step' if valid else 'failed reading'
        examples.setdefault(tag,detail)
    return {'start':start,'round':rn,'signed clauses':len(data),'four and five carrier sets extended':counts[:2],
            'six-carrier checks, with repeats':counts[2],'candidate six-carrier sets':len(sets),
            'oriented four-clause certificates':len(found),'certificates passing':sum(covers),
            'passing certificates with seven upper words':all7,'unique upper reading triples passing':len(successes),
            'unique upper reading triples passing and needing a birth':len(born),'examples':examples}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--limit',type=int)
    args=p.parse_args()
    archive=json.loads(SOURCES.read_text()); begin=perf_counter(); rows=[]
    with mixed_sets() as find:
        checks=controls(find)
        with gzip.open(args.input,'rt') as file:
            for line in file:
                if args.limit is not None and len(rows)>=args.limit:break
                since=perf_counter(); row=read_stage(json.loads(line),find,archive)
                row['seconds']=round(perf_counter()-since,6); rows.append(row)
    numbers=Counter()
    for row in rows:
        numbers.update({k:v for k,v in row.items() if isinstance(v,int) and k not in ('start','round')})
    rep={'scope':'Four single-word lower clauses with at least one shared carrier whose forbidden value differs between clauses. '
                'All six raw carriers disjoint. Upper signed readings use both for one pair, either for the other two. '
                'The four clauses alone must force the missing upper 111.',
         'stages':len(rows),'totals':dict(numbers),'distinct starts with a step needing a birth':
             sorted({r['start'] for r in rows if r['unique upper reading triples passing and needing a birth']}),
         'controls':checks,'seconds':round(perf_counter()-begin,4),'rows':rows}
    args.output.write_text(json.dumps(rep,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in rep.items() if k!='rows'}))


if __name__=='__main__':main()
