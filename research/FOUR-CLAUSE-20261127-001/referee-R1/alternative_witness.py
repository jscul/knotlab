"""Check each additional held-out certificate by full source-state enumeration."""

import argparse
from collections import Counter
import gzip
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

import numpy as np

from alternative_read import (HERE, SOURCES, WORDS, advance, canonical, joins, lower_indices, masks_to_triples,
                              packed, supports_of, upper)


def agree(states,m):
    part=states&m
    return (part==0)|(part==m)


def word_code(cols):
    x=np.zeros(len(cols[0]),dtype=np.uint8)
    for col in cols:x=(x<<1)|col
    return x


def all_cells(whole, cols):
    result=[whole]
    for col in cols:result=[child for cell in result for child in (cell&~col,cell&col)]
    return result


def canonical_check(present):
    absent=[w for w in product((0,1),repeat=3) if ''.join(map(str,w)) not in present]
    cnf='; '.join(' '.join(('~' if b else '')+j for b,j in zip(word,'ABC')) for word in absent)
    repo=HERE.parents[2]
    proc=subprocess.run([sys.executable,'-B','-m','knotlab','check','--cnf',cnf,
                         '--loops','A','B','--contact','C','--json'],capture_output=True,text=True,
                        check=True,env=dict(os.environ,PYTHONPATH=str(repo/'tools')))
    verdict=json.loads(proc.stdout)
    assert verdict['is_knot'] and verdict['allowed']==present
    return {'cnf of the projected relation':cnf,'canonical test':verdict}


def renamings_426(laws,initial,certificates):
    width=1+max(max(s) for s in laws)
    generators=(((15,16),),((9,10),(13,15),(14,16)))
    mappings=[]
    for interchanges in generators:
        mapping=list(range(width))
        for x,y in interchanges:mapping[x],mapping[y]=y,x
        for stage in (initial,advance(initial).supports,laws):
            assert {frozenset(k) for k in stage}=={frozenset(mapping[i] for i in k) for k in stage}
        mappings.append(mapping)
    reached={certificates[0]}; todo=[certificates[0]]
    while todo:
        row=todo.pop()
        for mapping in mappings:
            moved=[(sum(1<<mapping[i] for i in range(width) if (v>>1)&(1<<i))<<1)|(v&1) for v in row[:6]]
            actual=canonical((*moved,row[-1]))
            if actual not in reached:reached.add(actual);todo.append(actual)
    assert reached==set(certificates)
    return {'raw distinction swaps preserving each successive stage':generators,
            'distinct certificates reached from the first':len(reached)}


def direct(start,rn,clauses,covers,local_limit):
    initial=supports_of(json.loads(SOURCES.read_text())[start]); laws=initial
    for _ in range(rn):laws=advance(laws).supports
    n=1+max(max(k) for k in laws); states=np.arange(1<<n,dtype=np.uint32)
    violated=np.zeros(len(states),dtype=np.uint32)
    for i,k in enumerate(laws):violated|=agree(states,sum(1<<j for j in k)).astype(np.uint32)<<i
    valid=states[violated==0]; whole=(1<<len(valid))-1
    masks={t>>1 for clause in clauses for t in clause}
    by_mask={m:packed(agree(valid,m)) for m in masks}
    records=[]
    for group in covers:
        literals=group[:6];f=group[-1]; locations=lower_indices(f)
        pred=[agree(states,v>>1)==(v&1) for v in literals]
        ut=(pred[0]&pred[1],pred[2]|pred[3],pred[4]|pred[5]); uppercode=word_code(ut)
        observed=np.bincount(uppercode[violated==0],minlength=8).tolist()
        present=[f'{j:03b}' for j,count in enumerate(observed) if count]
        canonical=canonical_check(present)
        lookup=word_code(pred); six_counts=np.bincount(lookup[violated==0],minlength=64)
        source_words={WORDS[i] for i,num in enumerate(six_counts) if num}
        virtual={w for w in WORDS if not any(all(w[j] for j in loc) for loc in locations)}
        assert source_words<=virtual
        abstract=[]; named_mixes=[]
        for i,t in enumerate(locations):
            missing={w for w in product((0,1),repeat=3) if w not in {tuple(s[j] for j in t) for s in source_words}}
            assert missing=={(1,1,1)}
            cells=[[s for s in source_words if tuple(s[j] for j in t)==w] for w in product((0,1),repeat=3)]
            mixed=[sum(len({upper(s)[k] for s in cell})==2 for cell in cells) for k in range(3)]
            assert min(mixed)>0
            named_mixes.append(mixed)
            after=[w for w in WORDS if upper(w)==(1,1,1) and
                   not any(j!=i and all(w[k] for k in loc) for j,loc in enumerate(locations))]
            assert after
            abstract.append([''.join(map(str,w)) for w in after])
        stage_restored=[int(np.sum((violated==(1<<i))&(uppercode==7))) for i in range(len(laws))]
        ucols=[packed(bit[violated==0]) for bit in ut]
        names=[v>>1 for v in literals]
        local=[Counter() for _ in range(3)]; fixed=[set() for _ in range(3)]
        defining={tuple(sorted(names[i] for i in loc)) for loc in locations}
        chosen=set()
        for clause in clauses[:local_limit]:
            raw=tuple(sorted(v>>1 for v in clause)); fixing=all_cells(whole,[by_mask[m] for m in raw]);
            if raw in defining:chosen.add(raw)
            for i,uv in enumerate(ucols):
                determines=not any((group&uv) and (group&~uv) for group in fixing)
                if determines:
                    assert raw not in defining
                    members=set(names[2*i:2*i+2])
                    local[i]['any']+=1
                    local[i]['contains both constituents']+=members.issubset(raw)
                    local[i]['contains one constituent']+=len(members.intersection(raw))==1
                    local[i]['contains neither constituent']+=members.isdisjoint(raw)
                    fixed[i].add(raw)
        two_needed=[]
        for p in range(3):
            # Essential input on the actual six-word relation: hold the other
            # five signed readings still and flip this one across two words.
            here=[]
            for j in range(2*p,2*p+2):
                adjacent=sum(w[j]==0 and w[:j]+(1,)+w[j+1:] in source_words and
                             upper(w)[p]!=upper(w[:j]+(1,)+w[j+1:])[p] for w in source_words)
                here.append(adjacent)
            two_needed.append(here)
        records.append({'carriers A0,A1,B0,B1,C0,C1':masks_to_triples([v>>1 for v in literals]),
                        'agreement values counted as true':[v&1 for v in literals],
                        'A index for B,C choices 00,01,10,11':[(f>>j)&1 for j in range(4)],
                        'signed six words attained':sorted(''.join(map(str,w)) for w in source_words),
                        'six words allowed by only the four lower clauses':len(virtual),
                        'extra six words allowed by only the four lower clauses':len(virtual-source_words),
                        'source states per upper word, 000 to 111':observed,'upper relation':canonical,
                        'defining lower cells with both values of each upper reading':named_mixes,
                        'upper 111 states restored by each single source-law deletion':stage_restored,
                        'abstract 111 witnesses on the four single lower-clause deletions':abstract,
                        'six-word pairs proving constituent essentiality at fixed other five':two_needed,
                        'stage lower bonds inspected':len(clauses[:local_limit]),
                        'the four defining lower bonds found in that inspection':len(chosen),
                        'any stage lower bond determining each upper reading':[dict(q) for q in local],
                        'example for each upper reading, with zero if none':[
                            masks_to_triples(min(s)) if s else 0 for s in fixed]})
    result={'census entry':start,'round':rn,'source laws':laws,'start laws':len(initial),
            'source assignments tested':len(states),'source assignments allowed':len(valid),'records':records}
    if start==426 and rn==2 and len(covers)==4:
        result['renamings']=renamings_426(laws,initial,covers)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--start',type=int,default=426);p.add_argument('--round',type=int,default=2)
    p.add_argument('--limit',type=int);p.add_argument('--covers',type=int);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();begin=perf_counter()
    with gzip.open(args.input,'rt') as stream:
        for line in stream:
            row=json.loads(line)
            source_id=row.get('start',row.get('census_entry'))
            if int(str(source_id).split()[-1])==args.start and row['round']==args.round:break
        else:raise ValueError('Stage missing')
    with joins() as find:covers,_=find(row['clauses'])
    rep=direct(args.start,args.round,row['clauses'],covers[:args.covers],args.limit)
    rep['seconds']=round(perf_counter()-begin,5);args.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(rep['census entry'],rep['round'],len(rep['records']),rep['seconds'])


if __name__=='__main__':main()
