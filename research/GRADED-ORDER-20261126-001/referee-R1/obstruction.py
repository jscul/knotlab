"""Two flag-clear starts: test the growth identification and the proposed order lemma."""
import argparse
from collections import Counter
from itertools import combinations
import json
import resource
import sys
import time
from fresh import HERE, alike, late, view

sys.path.insert(0, str(HERE.parent))
import graded


def from_pairs(n, pairs, loose):
    stars = [[] for _ in range(n)]
    for d,(a,b) in enumerate(pairs):
        stars[a].append(d)
        stars[b].append(d)
    d = len(pairs)
    for a,k in enumerate(loose):
        stars[a].extend(range(d,d+k))
        d += k
    return stars


def triples_start():
    triples = sorted({tuple(sorted((x-1, y-1, (x ^ y)-1))) for x,y in combinations(range(1,8),2)})
    pairs = [(14,a) for a in range(7)]
    w = 15
    for i,group in enumerate(triples):
        for a in group:
            pairs.extend([(a,w),(7+i,w)])
            w += 1
    pairs.extend((v, 15+(v-14)%21) for v in range(15,36))
    return from_pairs(36,pairs,[3]*7+[1]*7+[0]*22)


def four_cells_start():
    a,b,c,d,e,f = range(6)
    p,q,r,s = range(6,10)
    middle,x,y,z = range(10,14)
    pairs = [(middle,i) for i in range(6)]
    pairs.extend([(a,c),(a,e),(b,f),(p,c),(q,e),(r,f),(s,a),(s,b)])
    for w, group in [(x,(p,b,c)), (y,(q,d,e)), (z,(r,d,f))]:
        pairs.extend((w,i) for i in group)
    return from_pairs(14,pairs,[3]*6+[1]*4+[0]*4)


def test(which, laws):
    if which == 'triples':
        stars = triples_start()
    elif which == 'four-cells':
        stars = four_cells_start()
    else:
        stars = from_pairs(5,[(0,i) for i in range(1,5)],[0,3,3,3,3])
    m = late.Map(stars)
    print(json.dumps(dict(stars=stars, cells=list(map(sorted,m.cells)), pieces=m.pieces, cls=m.cls)))
    sets = {}
    ids, _, _ = m.pieces[0]
    for n in range(1,len(ids)+1):
        for group in combinations(ids,n):
            s = frozenset(group)
            if any(1<len(s & g)<len(g) for g in m.cells):
                continue
            seen = set()
            stack = [next(iter(s))]
            while stack:
                v = stack.pop()
                if v not in seen:
                    seen.add(v)
                    stack.extend((m.adj[v] & s)-seen)
            if s==seen:
                sets[s]=len(s)-1-sum(len(g)-2 for g in m.cells if g<=s)
    parents, actual_rank = {}, {}
    for s in sets:
        maximal = []
        for t in reversed(sets):
            if t < s and not any(t < u for u in maximal):
                maximal.append(t)
        parents[s] = set(maximal)
        heights = {actual_rank[t]+1 for t in maximal} or {0}
        assert len(heights) == 1
        actual_rank[s] = heights.pop()
    split = any(actual_rank[s]>=2 and any(not parents[a] & parents[b] for a,b in combinations(pp,2))
                for s,pp in parents.items())
    print(json.dumps(dict(valid_by_computed_rank=dict(sorted(Counter(sets.values()).items())),
                          valid_by_inclusion_rank=dict(sorted(Counter(actual_rank.values()).items())),
                          split_using_inclusion_rank=split,
                          valid_by_cardinality=dict(sorted(Counter(map(len,sets)).items())))))
    for law in laws:
        rounds = 4 if which=='one-block' else 2
        assert m.cls == 'in' and all(tree for _,tree,_ in m.pieces)
        assert not graded.split_pair(stars,law) and not graded.cells_share_two(m) and not graded.route_cycle(m)
        p, reason = late.predict(stars,rounds,law,general=True)
        g = alike.grow(stars,rounds=rounds,bound=2200,knot_law=law)
        for reading in ['sig0','sig1']:
            if which=='one-block':
                assert all(view(a,reading)==view(b,reading) for a,b in zip(p,g['rows']))
                assert not any(row['n'] for row in p[len(g['rows']):])
            else:
                assert view(p[0],reading)!=view(g['rows'][0],reading)
        print(json.dumps(dict(law=law,predicted=p,grown=g,why=reason,split_pair=False,cells_share_two=False)))


if __name__=='__main__':
    args=argparse.ArgumentParser()
    args.add_argument('which',choices=['triples','four-cells','one-block'])
    args.add_argument('laws',nargs='+',choices=['nae','parity'])
    opt=args.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(3 << 30, 3 << 30))
    start=time.monotonic()
    test(opt.which,opt.laws)
    print(f'{time.monotonic()-start:.4f} seconds',file=sys.stderr)
