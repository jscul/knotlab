"""Widen genuine not-all-equal knots and replay the chosen readings directly."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import numpy as np


HERE=Path(__file__).resolve().parent
OPEN=json.loads((HERE/'open_witness.json').read_text())
OLD=json.loads((HERE.parent.parent/'RING-BOND-20261127-001'/'referee-R1'/'layer_witness.json').read_text())
CROSS=list(product((0,1),(2,3),(4,5)))


def agreement(states, places):
    mask=sum(1<<p for p in places)
    return ((states & mask)==0) | ((states & mask)==mask)


def upper_table():
    words=np.arange(64,dtype=np.uint8)
    return ((words^(words>>1))&1) | (((words>>2)^(words>>3))&1)<<1 | (((words>>4)^(words>>5))&1)<<2


class Replay:
    def __init__(self, rows, carriers, prefix):
        self.rows=rows
        self.carriers=carriers
        total=1<<(1+max(max(r) for r in rows))
        self.states=np.arange(min(prefix,total) if prefix else total,dtype=np.uint32)
        self.lower=np.zeros(len(self.states),dtype=np.uint8)
        for i,c in enumerate(carriers):
            self.lower|=agreement(self.states,c).astype(np.uint8)<<i
        self.upper=upper_table()[self.lower]
        self.banned=((self.lower&3)!=0)&((self.lower&12)!=0)&((self.lower&48)!=0)
        self.original=self.violations(rows)

    def violations(self, rows):
        bad=np.zeros(len(self.states),dtype=np.uint16)
        for i,r in enumerate(rows):
            bad|=agreement(self.states,r).astype(np.uint16)<<i
        return bad

    def check(self,rows,bad=None):
        if bad is None: bad=self.violations(rows)
        allowed=bad==0
        if np.any(allowed & self.banned): return None
        lower_counts=np.bincount(self.lower[allowed],minlength=64)
        words=np.flatnonzero(lower_counts)
        missing=[]
        for triple in CROSS:
            proj=sum(((words>>v)&1)<<j for j,v in enumerate(triple))
            missing.append(sorted(set(range(8))-set(proj.tolist())))
        if any(w!=[7] for w in missing): return None
        upper_counts=np.bincount(self.upper[allowed],minlength=8)
        if np.flatnonzero(upper_counts).tolist()!=list(range(7)): return None
        abstract_words=np.arange(64)
        fails=np.zeros(64,dtype=np.uint16)
        for i,t in enumerate(CROSS):
            all_one=sum(1<<v for v in t)
            fails|=((abstract_words&all_one)==all_one).astype(np.uint16)<<i
        upper_mixed=[]
        for source_words in (words,abstract_words[fails==0]):
            fixes=[]
            for t in CROSS:
                projection=sum(((source_words>>v)&1)<<j for j,v in enumerate(t))
                by_reading=[]
                for i in range(3):
                    values=(upper_table()[source_words]>>i)&1
                    tally=np.bincount(2*projection+values,minlength=16).reshape(8,2)
                    by_reading.append(int(np.sum(np.all(tally>0,axis=1))))
                fixes.append(by_reading)
            if min(min(row) for row in fixes)==0: return None
            upper_mixed.append(fixes)
        st=self.states[allowed]
        lower=self.lower[allowed]
        mixed=[]
        for row in rows:
            fix=sum(((st>>x)&1)<<i for i,x in enumerate(row))
            counts=[]
            for k in range(6):
                both=np.bincount(2*fix+((lower>>k)&1),minlength=2<<(len(row))).reshape(-1,2)
                counts.append(int(np.sum(np.all(both>0,axis=1))))
            mixed.append(counts)
        if min(min(row) for row in mixed)==0: return None
        flips=[]
        for idx,c in enumerate(self.carriers):
            count=[]
            for p in c:
                flipped=st^(1<<p)
                valid=flipped<len(allowed)
                changed=flipped[valid]
                count.append(int(np.count_nonzero(allowed[changed] &
                    (((lower[valid]^self.lower[changed])>>idx)&1).astype(bool))))
            flips.append(count)
        assert min(min(row) for row in flips)>0
        patches=[int(np.count_nonzero((self.upper==7)&(bad==1<<i))) for i in range(len(rows))]
        degrees=Counter(v for r in rows for v in r)
        return {
            'source_supports':rows,'carriers':self.carriers,'counted_assignments':len(self.states),
            'source_states':int(allowed.sum()),'lower_words':len(words),
            'source_states_by_lower_word':{format(int(w),'06b')[::-1]:int(lower_counts[w]) for w in words},
            'lower_words_missing_in_A_B_C_order':missing,'upper_counts_by_binary_index':upper_counts.tolist(),
            'knot_fixes_with_both_reading_values':mixed,'single_change_count_by_carrier_place':flips,
            'source_states_restoring_upper_111_when_each_law_dropped':patches,
            'lower_triple_fixes_leaving_both_upper_values_on_stage_and_on_abstract_clauses':upper_mixed,
            'restored_upper_111_six_reading_words_on_each_lower_clause_deletion':[
                abstract_words[(upper_table()==7)&(fails==1<<i)].tolist() for i in range(8)],
            'counts_of_distinctions_by_holder_count':dict(sorted(Counter(degrees.values()).items())),
        }


def augmented(prefix,limit):
    rows=OPEN['grown_supports']
    source=Replay(rows,OPEN['six_disjoint_carriers'],prefix)
    deltas={}
    for v in (17,18):
        for i,r in enumerate(rows):
            if v not in r:
                relieved=agreement(source.states,r)&~agreement(source.states,r+[v])
                deltas[v,i]=relieved.astype(np.uint16)<<i
    tested=0
    accepted=[]
    first=None
    for i,j in product(range(len(rows)),repeat=2):
        if i==j or (17,i) not in deltas or (18,j) not in deltas: continue
        if limit and tested==limit: break
        tested+=1
        bad=source.original ^ deltas[17,i] ^ deltas[18,j]
        if np.any((bad==0)&source.banned): continue
        new=[r+[17] if k==i else r+[18] if k==j else r for k,r in enumerate(rows)]
        detail=source.check(new,bad)
        if detail:
            patches=detail['source_states_restoring_upper_111_when_each_law_dropped']
            accepted.append({'four_place_knots':[i,j],'every_law_needed':all(patches)})
            if first is None: first=detail
    return {'tested_two_distinct_widenings':tested,'boxes':accepted,'first':first}


def uniform(prefix):
    rows=OLD['source_knots_not_all_equal']
    carriers=OLD['lower_carriers_in_A0_A1_B0_B1_C0_C1_order']
    new=[]
    for r in rows:
        small=next(c for c in carriers if len(set(c)&set(r))==1)
        new.append(r+[next(x for x in small if x not in r)])
    return Replay(new,carriers,prefix).check(new)


def caps(prefix):
    rows=OPEN['grown_supports']
    result=[]
    for fresh in ([19,20],[19,20,21]):
        new=rows+[[x]+fresh for x in (17,18)]
        result.append(Replay(new,OPEN['six_disjoint_carriers'],prefix).check(new))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--prefix',type=int)
    p.add_argument('--limit',type=int)
    p.add_argument('--part',choices=['widen','uniform','cap'],required=True)
    args=p.parse_args()
    if args.part=='widen': result=augmented(args.prefix,args.limit)
    elif args.part=='cap': result=caps(args.prefix)
    else: result=uniform(args.prefix)
    print(json.dumps(result,indent=2))
