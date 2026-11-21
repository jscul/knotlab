"""Recover presentations from literal allowed words only, with an independent census comparison."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
import json

from pair_repairs import OUT, read_cases


def positions(mask):
    while mask:
        bit=mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


@lru_cache(maxsize=None)
def zero_bit(n,i):
    return sum(1<<w for w in range(1<<n) if not w & 1<<i)


@lru_cache(maxsize=None)
def violated(n,h):
    return sum(1<<w for w in range(1<<n) if (w&h) in (0,h))


class AllowedReader:
    def __init__(self,n,s):
        self.n=n
        self.s=s
        self.words=tuple(positions(s))
        self.neighbours=[1<<i for i in range(n)]
        self.same_holders=[1<<i for i in range(n)]
        for i,j in combinations(range(n),2):
            di,dj=1<<i,1<<j
            z=zero_bit(n,i)&zero_bit(n,j)
            s01,s10,s11=s>>di,s>>dj,s>>(di+dj)
            if z & ~s & s01 & s10 & s11:
                self.neighbours[i] |= dj
                self.neighbours[j] |= di
            if not z & (s|s01|s10|s11) & ~(s01&s10):
                self.same_holders[i] |= dj
                self.same_holders[j] |= di

    def exact(self,h):
        if h.bit_count()<3 or self.s&violated(self.n,h):
            return False
        return len({x&h for x in self.words})==(1<<h.bit_count())-2

    def propagate(self,h):
        if not self.exact(h):
            return None
        pending=[h]
        seen={h}
        while pending:
            holder=pending.pop()
            for x in positions(holder):
                outside=self.neighbours[x]&~holder
                if not outside:
                    continue
                other=outside|self.same_holders[x]
                if other in seen:
                    continue
                if not self.exact(other):
                    return None
                seen.add(other)
                pending.append(other)
        all_seen=0
        for row in seen:
            all_seen |= row
        if all_seen != (1<<self.n)-1:
            return None
        # Verify that every named incidence and every word is accounted for.
        for x in range(self.n):
            incident=[k for k in seen if k & (1<<x)]
            if len(incident) not in (1,2):
                return None
            whole=0
            for k in incident:
                whole |= k
            if whole != self.neighbours[x]:
                return None
        v=0
        for h in seen:
            v |= violated(self.n,h)
        if v^self.s != (1<<(1<<self.n))-1 or v&self.s:
            return None
        return tuple(sorted(seen))

    def mixed_slice(self,i,j):
        rest=[k for k in range(self.n) if k not in (i,j)]
        words=[sum((w>>k & 1)<<a for a,k in enumerate(rest)) for w in self.words if not w & (1<<i) and w & (1<<j)]
        return rest,AllowedReader(len(rest),sum(1<<w for w in words))

    def recover(self):
        for hood in self.neighbours:
            if self.exact(hood):
                result=self.propagate(hood)
                assert result is not None
                return 'loose', {result}
        for i,twins in enumerate(self.same_holders):
            if twins.bit_count()>1:
                j=next(j for j in positions(twins) if i!=j)
                rest,residual=self.mixed_slice(i,j)
                seed=next(hood for hood in residual.neighbours if residual.exact(hood))
                native=sum(1<<rest[k] for k in positions(seed))
                result=self.propagate(native)
                assert result is not None
                return 'closed_repeated',{result}
        # In a closed simple start every holder is a maximal pairwise co-held
        # set: no distinct name outside a star can meet all its >=3 marks.
        clique_seeds=[]
        for h in range(1<<self.n):
            if h.bit_count()<3:
                continue
            members=tuple(positions(h))
            common=(1<<self.n)-1
            for i in members:
                common &= self.neighbours[i]
            if common == h and self.exact(h):
                clique_seeds.append(h)
        candidates={value for h in clique_seeds if (value:=self.propagate(h)) is not None}
        assert candidates
        return 'closed_simple',candidates


def main():
    report={}
    for n,cases in read_cases().items():
        strata=Counter()
        for c in cases:
            s=int(c['state_words_hex'],16)
            reader=AllowedReader(n,s)
            arm,families=reader.recover()
            expected=c['named_presentations_per_state']
            assert len(families)==expected
            literal=tuple(sorted(sum(1<<i for i in row) for row in c['presentations'][0]['supports']))
            assert literal in families
            strata[arm]+=1
            if len(families)>1:
                assert n==6 and len(families)==2
                strata['two_named_families']+=1
        report[str(n)]=strata
    (OUT/'state_reconstruction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
