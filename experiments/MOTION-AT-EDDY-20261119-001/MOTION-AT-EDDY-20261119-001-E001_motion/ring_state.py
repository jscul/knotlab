"""Least changes capable of writing a closed state on a selected original ring."""

from itertools import combinations
from pathlib import Path
import json

from motion_stage import load_stage, load_marks

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2]/'artifacts'/HERE.parent.name/HERE.name


def vector(support):
    return sum(1<<i for i in support)


class Span:
    def __init__(self, generators):
        self.rows={}
        self.orig = generators
        for i,generator in enumerate(generators):
            x,receipt=self.reduce(vector(generator),1<<i)
            if x:self.rows[x.bit_length()-1]=(x,receipt)

    def reduce(self,x,receipt=0):
        while x and (row:=self.rows.get(x.bit_length()-1)):
            x ^= row[0]
            receipt ^= row[1]
        return x,receipt

    def representation(self,target):
        x,word=self.reduce(vector(target))
        if x:return None
        used=[i for i in range(len(self.orig)) if word>>i & 1]
        outcome=set()
        for i in used:outcome.symmetric_difference_update(self.orig[i])
        assert outcome==set(target)
        return [sorted(self.orig[i]) for i in used]


def score(name):
    stage=load_stage(name); raw=load_stage(name,0)
    marks=load_marks(name)
    ring_edges=marks['ring_edges']
    raw_shared={b for b,owners in raw.owners.items() if len(owners)==2}
    ordinary=set(stage.ordinary_quads())
    all_short=set()
    for bit in stage.owners:
        result=stage.minimum_response(bit)
        assert result.minimum_size in (2,4) and result.listed_all_supports
        all_short.update(map(frozenset,result.supports))
    fours={q for q in all_short if len(q)==4}
    assert all(len(q & raw_shared) in (0,2) for q in all_short)
    tiers={}
    for mode,gen in [('ordinary4',ordinary),('all_min4',fours),('all_min2_and_4',all_short)]:
        span=Span(sorted(gen,key=lambda x:(len(x),sorted(x))))
        targets={}
        for n in range(1,len(ring_edges)+1):
            for ids in combinations(range(len(ring_edges)),n):
                target=set().union(*(set(ring_edges[j]) for j in ids))
                assert stage.allowed_change(target)
                if mode=='ordinary4':assert span.representation(target) is None
                targets[','.join(str(j+1) for j in ids)]=span.representation(target)
        tiers[mode]=dict(generators=len(gen),rank=len(span.rows),targets=targets)
    return tiers


def main():
    names=['B','R0','R1','R2','J0','J1','J2','T4','T8','C1','B81','J81','T81','R31']
    rows={k:score(k) for k in names}
    (DATA/'ring_state.json').write_text(json.dumps(rows,indent=2)+'\n')
    for k in ['J1','T4','T8','T81','R31']:
        print(k,{m:{target:(None if rep is None else len(rep)) for target,rep in result['targets'].items()}
                 for m,result in rows[k].items()})


if __name__=='__main__':main()
