"""Filter candidate pairs by witnessed triples, then certify every surviving pair exactly."""
from collections import Counter
import json
from pathlib import Path
import random
import sys

from parts import members, read_stage
from residual import covering_test


def main():
    base=Path(sys.argv[1])
    age=int(sys.argv[2])
    start,stop=map(int,sys.argv[3:5])
    n, blocks, masks, adj=read_stage(base/f"age{age}.txt")
    limit=min(n,stop)
    owner=[0]*n
    for k,b in enumerate(blocks):
        for x in b:
            owner[x] |= 1<<k
    check=covering_test(n,blocks,masks,adj)
    order=list(range(n))
    random.Random(20261119094).shuffle(order)
    stats=Counter()
    residual=[]
    for x in range(start,limit):
        rem=adj[x] & ~((1<<(x+1))-1)
        if not rem:
            continue
        stats["original"]+=rem.bit_count()
        for z in order[:min(128,n)]:
            hh=owner[x]&owner[z]
            if not hh or x==z:
                continue
            if rem.bit_count()<6:
                break
            eligible=rem & adj[z]
            if not eligible:
                continue
            for h in members(hh):
                eligible &= ~masks[h]
                if not eligible:
                    break
            rem ^= eligible
        stats["recursive_tests"]+=rem.bit_count()
        for y in members(rem):
            if not check(x,y):
                residual.append((x,y))
    output=dict(age=age,start=start,stop=limit,counts=dict(stats),residual=residual)
    dest=base/f"exact-pairs-{age}-{start}-{limit}.json"
    dest.write_text(json.dumps(output)+"\n")
    print(start,limit,stats,len(residual),flush=True)

if __name__=="__main__":
    main()

