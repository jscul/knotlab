"""Compare determination at a defining clause with determination at other stage bonds."""
import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys
from subprocess import check_output
from time import perf_counter

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH/'NAE-LAYER-20261127-001/referee-R1'))
from growth_rule import advance, supports_of

CENSUS = RESEARCH/'FORBID-EDITS-20261126-001/starts.json'
SIX = ((2,8,10),(7,13),(0,1,5),(9,12,14),(3,4,11),(6,15,16))


def pack(bits):
    return int.from_bytes(np.packbits(bits,bitorder='little').tobytes(),'little')


def carrier(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def mask(c):
    return sum(1<<x for x in c)


def cells(allowed, predicates):
    result = [allowed]
    for val in predicates:
        result = [part for prev in result for part in (prev & ~val, prev & val)]
    return result


def projections(words, coords):
    return {tuple(w[i] for i in coords) for w in words}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--all-bonds',action='store_true',help='Request every lower bond from the independent full census')
    args=parser.parse_args()
    begin=perf_counter()
    original=supports_of(json.loads(CENSUS.read_text())[5260])
    supports=advance(advance(original).supports).supports
    n=1+max(max(k) for k in supports)
    states=np.arange(1<<n,dtype=np.uint32)
    for k in supports:
        m=mask(k)
        states=states[((states & m)!=m) & ((states & m)!=0)]
    allowed=(1<<len(states))-1
    # A knot fixes a reading exactly when each occupied local state has only one reading value.
    def local(k, bits):
        return len(np.unique((states & mask(k))*2+bits)) == len(np.unique(states & mask(k)))
    cols={}
    reads_by={}
    for size in (2,3):
        for c in combinations(range(n),size):
            m=mask(c)
            eq=((states & m)==0)|((states & m)==m)
            cols[m]=pack(eq)
            reads_by[m]=[j for j,k in enumerate(supports) if local(k,eq)]
    c6=tuple(mask(c) for c in SIX)
    four=[]
    for ijk in combinations(range(6),3):
        images=cells(allowed,[cols[c6[i]] for i in ijk])
        if sum(map(bool,images))==7:
            missing=images.index(0)
            four.append((ijk,tuple((missing>>(2-j))&1 for j in range(3))))
    named=[(ijk,w) for ijk,w in four if w==(1,1,1)]
    # Find the pair partition from the occurrence lists. Keep the rank of each carrier as printed.
    found=[]
    for group in combinations(named,4):
        triples=[set(ijk) for ijk,_ in group]
        if any(sum(i in t for t in triples)!=2 for i in range(6)):continue
        if any(len(a&b)!=1 for a,b in combinations(triples,2)):continue
        pairs=[(i,j) for i,j in combinations(range(6),2) if all(not {i,j}<=t for t in triples)]
        if len(pairs)==3:found.append(pairs)
    assert len(found)==1,found
    pairs=found[0]
    assert not any(reads_by[c] for c in c6)
    pred={}
    for idx,(i,j) in enumerate(pairs):
        a,b=cols[c6[i]],cols[c6[j]]
        pred[idx,'both']=a & b
        pred[idx,'either']=a | b
    counts=Counter()
    examples={}
    def record(carr,missing):
        assert all(not reads_by[m] for m in carr)
        parts=cells(allowed,[cols[c] for c in carr])
        assert sum(1<<i for i,cell in enumerate(parts) if not cell)==missing
        for key,u in pred.items():
            if all(not (cell & u and cell & ~u) for cell in parts):
                counts[key]+=1
                if key not in examples:
                    examples[key]={'determining_bond':[carrier(m) for m in carr],
                                   'missing':[format(w,'03b') for w in range(8) if missing&(1<<w)],
                                   'upper_true_on':[format(w,'03b') for w in range(8) if parts[w]&u]}
    if args.all_bonds:
        answer=json.loads(check_output([HERE/'read_engine','2',*[str(mask(k)) for k in supports]]))
        assert len(answer['all_bonds'])==answer['bonds']
        for a,b,c,miss in answer['all_bonds']:
            record((a,b,c),miss)
            counts['examined']+=1
            if args.pilot and counts['examined']>=100:break
    else:
        for idx,(i,j) in enumerate(pairs):
            if args.pilot and idx>0:break
            a,b=c6[i],c6[j]
            for m,derived in reads_by.items():
                if derived or m & (a|b):continue
                carr=(a,b,m)
                pp=cells(allowed,[cols[c] for c in carr])
                words=[tuple(int(y) for y in format(w,'03b')) for w,x in enumerate(pp) if x]
                if len(words)>=8 or any(len(projections(words,ij))!=4 for ij in combinations(range(3),2)):continue
                record(carr,sum(1<<w for w,x in enumerate(pp) if not x))
                counts['examined']+=1
    data={'stage':'second round of census entry 5260','source_states':len(states),'source_knots':supports,
          'weighting':'one count per distinct lower bond, once for each upper reading it determines',
          'mode':'all stage bonds supplied by independent recount' if args.all_bonds else 'all eligible third carriers for each of the three named pairs',
          'pilot':args.pilot,'pairs':[[carrier(c6[i]),carrier(c6[j])] for i,j in pairs],'tested_bonds':counts['examined'],
          'both_and_either':[{'pair':key[0],'reading':key[1],'determined_at':counts[key],'first_example':examples.get(key)}
                             for key in pred], 'seconds':round(perf_counter()-begin,3)}
    kind='all' if args.all_bonds else 'paired'
    label='pilot' if args.pilot else 'counts'
    out=HERE/f'locality_{kind}_{label}.json'
    out.write_text(json.dumps(data,indent=2)+'\n')
    print(out.name,data['tested_bonds'],[(p['pair'],p['reading'],p['determined_at']) for p in data['both_and_either']],data['seconds'])

if __name__=='__main__':
    main()
