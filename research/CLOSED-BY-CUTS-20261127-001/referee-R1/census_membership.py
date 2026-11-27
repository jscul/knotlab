"""Generate the finite starting class and check each archived representative up to renaming."""
import argparse
from collections import Counter
from itertools import combinations, permutations, product
import json
from time import perf_counter

from growth_replay import ARCHIVE, HERE


def generate(n):
    pairs = list(combinations(range(n),2))
    moves = []
    for perm in permutations(range(n)):
        edge_order = tuple(pairs.index(tuple(sorted((perm[a],perm[b])))) for a,b in pairs)
        moves.append((perm,edge_order))

    # First partition shared multiplicities by renaming alone. For each representative
    # only its own renamings can further identify two assignments of loose counts.
    shared_classes = {}
    keys = set()
    for shared in product(range(3),repeat=len(pairs)):
        used=sum(shared)
        if used>12 or shared in shared_classes:
            continue
        neighbours=[set() for _ in range(n)]
        arities=[0]*n
        for (a,b),m in zip(pairs,shared):
            if m:
                arities[a]+=m
                arities[b]+=m
                neighbours[a].add(b)
                neighbours[b].add(a)
        seen={0}
        for _ in range(n-1):
            seen.update(set().union(*(neighbours[i] for i in seen)))
        if len(seen)!=n:
            continue

        to_rep={}
        sym=[]
        for perm,order in moves:
            renamed=tuple(shared[i] for i in order)
            inverse=tuple(perm.index(i) for i in range(n))
            to_rep[renamed]=inverse
            if renamed==shared:
                sym.append(perm)
        for member,perm in to_rep.items():
            shared_classes[member]=(shared,perm,sym)
        lower=[max(0,3-a) for a in arities]
        for loose in product(*(range(k,3) for k in lower)):
            if used+sum(loose)<=12:
                canonical=min(tuple(loose[i] for i in perm) for perm in sym)
                keys.add((shared,canonical))

    def key(meetings,loose):
        counts={(a,b):m for a,b,m in meetings}
        representative,perm,sym=shared_classes[tuple(counts.get(pair,0) for pair in pairs)]
        renamed=tuple(loose[i] for i in perm)
        return representative,min(tuple(renamed[i] for i in order) for order in sym)
    return keys,key


def main(pilot):
    archive=json.loads(ARCHIVE.read_text())
    result={}
    for n in (3,4) if pilot else (3,4,5):
        expected,key=generate(n)
        recorded=Counter(key(m,l) for k,m,l in archive if k==n)
        entry=dict(constructed=len(expected),archive_rows=sum(recorded.values()),
                   duplicates=sum(i-1 for i in recorded.values()),missing=len(expected-set(recorded)),
                   outside=len(set(recorded)-expected))
        assert not any(entry[k] for k in ('duplicates','missing','outside'))
        result[n]=entry
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    result=main(args.pilot)
    if not args.pilot:
        (HERE/'census_membership.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result,round(perf_counter()-t,4))
