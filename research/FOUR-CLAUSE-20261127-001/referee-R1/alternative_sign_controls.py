"""Check the sign-conflict search against all labeled minimal orientations on six bits."""

import argparse
from collections import Counter
from itertools import islice, product
import json
from pathlib import Path
from time import perf_counter

from alternative_read import BOUND, WORDS, upper
from alternative_signed import TABLE, inferred, mixed_sets, signed_rules


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--limit',type=int,default=4096)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); begin=perf_counter(); counts=Counter()
    six=tuple(3<<(2*i) for i in range(6))
    ua=tuple(2*m+1 for m in six)
    full_target=sum(1<<i for i,w in enumerate(WORDS) if upper(w)==(1,1,1))
    # A clause covering the singly true choices j,k can name either A. It
    # can test B_j true or its mate false, and make the same choice for C.
    choices=[tuple(((i,2+(j^fb),4+(k^fc)),(1,1-fb,1-fc))
                   for i,fb,fc in product((0,1),repeat=3)) for j,k in BOUND]
    with mixed_sets() as find:
        for quad in islice(product(*choices),args.limit):
            counts['orientations']+=1
            if len({t for t,_ in quad})<4 or len({i for t,_ in quad for i in t})<6:continue
            if all(len({b for t,w in quad for p,b in zip(t,w) if p==v})==1 for v in range(6)): continue
            counts['distinct supports, all six used, conflicting sign']+=1
            forbidden=0
            for clause in quad:forbidden|=TABLE[clause]
            expected=not bool(full_target&~forbidden)
            counts['force 111 absent in full truth table']+=expected
            if expected:
                legal=[w for i,w in enumerate(WORDS) if not(forbidden>>i)&1]
                counts['force 111 absent and all four lower projections have seven words']+=all(
                    len({tuple(w[i] for i in t) for w in legal})==7 for t,_ in quad)
            data=[[2*six[i]+s for i,s in zip(t,w)] for t,w in quad]
            _,sets=find(data)
            assert sets==[six]
            actual=any(group==ua for group,_ in inferred(six,signed_rules(data)))
            assert actual==expected
            counts['reviewed by independent full truth table and candidate search']+=1
    result={'counts':dict(counts),'seconds':round(perf_counter()-begin,5)}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(result)


if __name__=='__main__':main()
