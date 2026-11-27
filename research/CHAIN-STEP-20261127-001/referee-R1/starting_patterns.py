"""Check whether the carried class was already present before growth."""
import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
from time import perf_counter

from recount import load_census, supports_of, census_index, archive_records

HERE = Path(__file__).resolve().parent


def columns(n):
    full = (1 << (1 << n))-1
    return full, [full ^ (full // ((1 << (1 << i))+1)) for i in range(n)]


def pairs_only(supports, full, variables):
    allowed = full
    for support in supports:
        z = o = full
        for x in support:
            z &= ~variables[x]
            o &= variables[x]
        allowed &= ~(z|o)
    records = []
    for a,b in combinations(range(len(variables)),2):
        if any(a in k and b in k for k in supports):
            continue
        one = allowed & ~(variables[a] ^ variables[b])
        zero = allowed ^ one
        if one and zero:
            records.append(((1 << a)|(1 << b),zero,one))
    absent = []
    for i,(a,a0,a1) in enumerate(records):
        for j in range(i):
            b,b0,b1 = records[j]
            if a&b:
                continue
            cells = [x&y for x,y in product((a0,a1),(b0,b1))]
            for k in range(j):
                c,c0,c1 = records[k]
                if (a|b)&c:
                    continue
                miss = [2*t+bit for t,cell in enumerate(cells) for bit,cz in enumerate((c0,c1)) if not cell&cz]
                if len(miss)==1:
                    # Overcounting eligible bonds cannot miss a candidate.
                    absent.append((a,b,c,miss[0]))
    return absent


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    begin=perf_counter()
    pool=load_census()
    selected={census_index(r) for chunk in archive_records() for r in chunk}
    if args.pilot:
        indices=sorted(Random(2391).sample(range(len(pool)),32))
    else:
        indices=range(len(pool))
    full,variables=columns(12)
    stat={b:Counter() for b in ('all','sample')}
    witnesses=[]
    for i in indices:
        supports=supports_of(pool[i])
        n=len(set().union(*supports))
        assert n<=12
        bonds = [] if n<12 else pairs_only(supports,full,variables)
        for bucket in ('all','sample') if i in selected else ('all',):
            stat[bucket]['starts']+=1
            stat[bucket]['twelve_distinctions']+=n==12
            stat[bucket]['eligible_single_word_lower_triples_upper_bound']+=len(bonds)
            stat[bucket]['starts_with_any_candidate']+=bool(bonds)
        if bonds:
            witnesses.append({'entry':i,'candidate_lower_bonds':bonds})
    result={'weightings':stat,'candidates':witnesses,'seconds':perf_counter()-begin,
            'method':'At most twelve distinctions. Six disjoint carriers need twelve and every carrier is a pair. Exclude source-knot-readable pairs by containment. Count all remaining disjoint triples missing exactly one word, retaining every possible sign. No locality assumption is needed to use zero as an obstruction.'}
    path=HERE/('starting_pilot.json' if args.pilot else 'starting_patterns.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(stat, result['seconds'])

if __name__=='__main__':
    main()
