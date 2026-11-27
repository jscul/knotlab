"""Complete the parity construction using only genuine four-place knots."""

import argparse
from itertools import combinations,islice,product
import json

from arity_construct import LOWER,adequate,replay


def candidates():
    positive=[i for i in range(16) if (i>>1).bit_count()%2==0]
    negative=[i for i in range(16) if (i>>1).bit_count()%2]
    for left,right in product(combinations(positive,4),combinations(negative,4)):
        if 0 not in left: continue
        for a,b in product(left,right):
            yield list(left+right+(a,b)),[(left.index(a),8),(4+right.index(b),9)]


def search(limit):
    directions=[sum(1<<j for j,r in enumerate(LOWER) if i in r) for i in range(9)]
    counted=0
    for locations,extra in islice(candidates(),limit):
        counted+=1
        choices=[]
        for d in directions:
            meets=[(a,b) for a,b in combinations(range(10),2) if locations[a]^locations[b]==d]
            choices.append([(p,q) for p,q in combinations(meets,2) if len(set(p+q))==4])
        order=sorted(range(9),key=lambda k:len(choices[k]))
        if not choices[order[0]]: continue
        remaining=[4]*10
        for a,b in extra:
            remaining[a]-=1
            remaining[b]-=1
        picked=[None]*9
        def visit(j):
            if j==len(order):
                pairs=[p for two in picked for p in two]+extra
                cuts=[sum(1<<i for i,meet in enumerate(pairs) if v in meet) for v in range(10)]
                if adequate(cuts): return pairs
                return None
            k=order[j]
            for pair in choices[k]:
                ends=pair[0]+pair[1]
                if any(remaining[v]<=0 for v in ends): continue
                for v in ends: remaining[v]-=1
                picked[k]=pair
                found=visit(j+1)
                if found: return found
                for v in ends: remaining[v]+=1
            return None
        found=visit(0)
        if found: return {'sets_challenged':counted,'labels':locations,'meetings':found}
    return {'sets_challenged':counted,'meetings':None}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--limit',type=int)
    p.add_argument('--prefix',type=int,default=2**20)
    args=p.parse_args()
    result=search(args.limit)
    if result['meetings']:
        result['replay']=replay(result['meetings'],args.prefix)
    print(json.dumps(result,indent=2))
