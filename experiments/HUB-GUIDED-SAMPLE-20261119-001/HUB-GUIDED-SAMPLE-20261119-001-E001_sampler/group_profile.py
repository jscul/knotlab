"""Profile block covering and witnessed partner replacements of an actual joining group."""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from random import Random
from statistics import median


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def pack(vertices, n):
    out = bytearray((n+7)//8)
    for u in vertices:
        out[u//8] |= 1 << (u % 8)
    return int.from_bytes(out, "little")


class Stage:
    def __init__(self, path):
        with path.open() as f:
            self.n, num_blocks = map(int, f.readline().split())
            self.blocks = []
            self.at = [[] for _ in range(self.n)]
            for i, line in enumerate(f):
                vertices = list(map(int, line.split()))
                self.blocks.append(pack(vertices, self.n))
                for v in vertices:
                    self.at[v].append(i)
            assert len(self.blocks) == num_blocks
        self.at = list(map(tuple, self.at))
        self.full = (1 << self.n)-1
        self.signature_class = Counter(self.at)

    @lru_cache(maxsize=4096)
    def hood(self, signature):
        union = 0
        for block in signature:
            union |= self.blocks[block]
        return union

    def covers(self, g, sites):
        k = g.bit_count()
        hits = [((mask & g).bit_count(), i) for i,mask in enumerate(self.blocks)]
        n1, b1 = max(hits)
        touching = sum(h > 0 for h,_ in hits)
        sharing = sum(h >= 2 for h,_ in hits)
        if n1 == k:
            return n1, touching, sharing, [[b1]]
        for h,b in sorted(hits,reverse=True):
            if 2*h < k:
                break
            rem = g & ~self.blocks[b]
            first = (rem & -rem).bit_length()-1
            for second in self.at[first]:
                if not rem & ~self.blocks[second]:
                    return n1, touching, sharing, [[b,second]]
        return n1, touching, sharing, []

    def partners(self, sites):
        # Equal block memberships give equal closed neighborhoods for nonisolated
        # junctions, hence a potential alternative misses all copies or none.
        active = Counter(self.at[v] for v in sites)
        zero, one = self.full, 0
        for sig,count in active.items():
            closed = self.hood(sig)
            one &= closed
            if count == 1:
                one |= zero & ~closed
            zero &= closed
        choices = []
        for u in sites:
            sig = self.at[u]
            if active[sig] == 1:
                choices_u = one & ~self.hood(sig)
                if choices_u:
                    choices.append((choices_u.bit_count(),u,choices_u))
        # An outside junction can replace exactly one member of this group.
        # Mutually compatible replacements with distinct missing members
        # exhibit literal partner pairs and give independent binary choices.
        pool = self.full
        pairs = []
        for _,u,choices_u in sorted(choices):
            candidates = choices_u & pool
            if candidates:
                first = (candidates & -candidates).bit_length()-1
                pairs.append((u,first))
                pool &= self.hood(self.at[first])
        return len(choices), pairs

    def profile(self, sites, details=False):
        assert len(sites) >= 3 and len(set(sites)) == len(sites)
        g = pack(sites,self.n)
        largest, touching, sharing, double = self.covers(g,sites)
        upper, pairs = self.partners(sites)
        row = dict(size=len(sites),largest_single=largest,blocks_touched=touching,
                   blocks_holding_two=sharing,cover_up_to_two=double[0] if double else None,
                   partner_lower=len(pairs),partner_upper=upper)
        if details:
            row['witness_pairs'] = pairs
        return row


def summary(rows):
    n = len(rows)
    if not rows:
        return {'groups':0}
    def quant(key):
        values = sorted(key(x) for x in rows)
        return [values[0],median(values),values[-1]]
    return dict(groups=n, size=quant(lambda x:x['size']),
                single_block_share=quant(lambda x:x['largest_single']/x['size']),
                cover_one=sum(x['cover_up_to_two'] is not None and len(x['cover_up_to_two'])==1 for x in rows),
                cover_two=sum(x['cover_up_to_two'] is not None and len(x['cover_up_to_two'])==2 for x in rows),
                cover_at_least_three=sum(x['cover_up_to_two'] is None for x in rows),
                touched=quant(lambda x:x['blocks_touched']),
                share_with_witnessed_replacements=quant(lambda x:x['partner_lower']/x['size']),
                share_with_possible_replacements=quant(lambda x:x['partner_upper']/x['size']),
                definitely_near=sum(4*x['partner_lower'] >= 3*x['size'] for x in rows),
                definitely_outside_near=sum(4*x['partner_upper'] < 3*x['size'] for x in rows),
                some_partner_pair=sum(x['partner_lower']>0 for x in rows),
                independent_pair_count=quant(lambda x:x['partner_lower']))


def past(directory, seed, age, limit=384):
    name = f'start-{seed:02}'
    source = Stage(directory/f'{name}-age{age-1:02}.txt')
    with gzip.open(directory/f'{name}-age{age:02}.parents.json.gz','rt') as f:
        groups = json.load(f)
    ids = [i for i,g in enumerate(groups) if len(g)>=3]
    rng = Random(683291000+seed)
    picked = ids if seed == 3 or len(ids)<=limit else sorted(rng.sample(ids,limit))
    profiles = [source.profile(groups[i]) for i in picked]
    # All ranks at start-03 and uniform sampling without replacement elsewhere.
    size_hist = Counter(map(len,groups))
    maximum = max(range(len(groups)),key=lambda i:len(groups[i]))
    one = source.profile(groups[maximum],details=True) if len(groups[maximum])>=3 else None
    source.hood.cache_clear()
    return dict(start=name, age=age, predecessor_sites=source.n, all_births=len(groups),
                exact_sizes=dict(sorted(size_hist.items())),all_large=len(ids),sample=len(picked),
                uniform_large=summary(profiles),size_at_least_eight=summary([r for r in profiles if r['size']>=8]),
                first_largest=dict(rank=maximum,profile=one))


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--case',nargs=2,type=int,required=True)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    data=past(a.directory,*a.case)
    a.out.write_text(json.dumps(data,indent=1)+'\n')
    print(a.out,data['all_large'],data['uniform_large'],flush=True)


if __name__=='__main__':
    run()
