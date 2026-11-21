"""Independent state and parent-step checks for the frozen acyclic comparisons."""
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, product
import json


def prufer_tree(word):
    n = len(word) + 2
    degree = Counter(word)
    edges = []
    for x in word:
        leaf = next(i for i in range(n) if degree[i] == 0)
        edges.append((x, leaf))
        degree[leaf] = -1
        degree[x] -= 1
    edges.append(tuple(i for i in range(n) if degree[i] == 0))
    return edges


def neighbors(n, edges):
    adj = [set() for _ in range(n)]
    for i,j in edges:
        adj[i].add(j)
        adj[j].add(i)
    return adj


def routes(adj, start):
    paths = {start:(start,)}
    todo = deque([start])
    while todo:
        cut = todo.popleft()
        for nxt in adj[cut]:
            if nxt not in paths:
                paths[nxt] = paths[cut]+(nxt,)
                todo.append(nxt)
    return paths


def tree_groups(adj, live, rule):
    groups = set()
    for witness, others in enumerate(adj):
        for a,b in combinations(sorted(others & live),2):
            family = (a,b,witness) if rule=='W' and witness in live else (a,b)
            groups.add(tuple(sorted(family)))
    if rule=='D':
        for x in live:
            for y in adj[x] & live:
                groups.add(tuple(sorted((x,y))))
    return groups


def steps(adj, live, rule):
    groups = tree_groups(adj,live,rule)
    pairs = {pair for h in groups for pair in combinations(h,2)}
    return neighbors(len(adj),pairs)


def verify_trees(maximum):
    output = []
    for n in range(2,maximum+1):
        count = Counter()
        for seq in product(range(n),repeat=n-2):
            count['labelled_trees'] += 1
            physical = neighbors(n,prufer_tree(seq))
            paths = [routes(physical,i) for i in range(n)]
            can_spend = [i for i,ns in enumerate(physical) if len(ns)>=3]
            for spent_n in range(len(can_spend)+1):
                for spent in combinations(can_spend,spent_n):
                    live = set(range(n))-set(spent)
                    count['lawful_live_patterns'] += 1
                    ordinary = steps(physical,live,'O')
                    with_direct = steps(physical,live,'D')
                    with_witness = steps(physical,live,'W')
                    for i in sorted(live):
                        actual = routes(ordinary,i)
                        direct = routes(with_direct,i)
                        witnessed = routes(with_witness,i)
                        for j in sorted(live):
                            if i>=j:
                                continue
                            count['pairs'] += 1
                            path = paths[i][j]
                            d = len(path)-1
                            possible = d%2==0 and set(path[::2]) <= live
                            assert (j in actual) == possible
                            if possible:
                                assert len(actual[j])-1 == d//2
                                count['ordinary_finite'] += 1
                            if not spent:
                                assert len(direct[j])-1==(d+1)//2
                                if n>=3:
                                    assert len(witnessed[j])-1==(d+1)//2
        output.append(dict(n=n,**count))
    return output


def frozen_example(with_spent):
    edges=[(i,i+1) for i in range(4)]
    if with_spent:
        for center in (1,2,3):
            for j in range(4):
                edges.append((center, 5+4*(center-1)+j))
    n=max(max(pair) for pair in edges)+1
    adj=neighbors(n,edges)
    free=[6-len(group) for group in adj]
    live={v for v,l in enumerate(free) if l}
    comparisons={}
    for rule in ('O','D','W'):
        groups=tree_groups(adj,live,rule)
        charge=Counter(v for g in groups for v in g)
        assert all(charge[x] <= free[x] for x in live)
        parents=sorted(groups)+[(v,) for v in sorted(live) for _ in range(free[v]-charge[v])]
        ar=steps(adj,live,rule)
        r=routes(ar,0)
        comparisons[rule]=dict(coinput_steps=len(r[4])-1 if 4 in r else None,
                               first_births=len(parents),surplus=sum(free)-sum(charge.values()))
    return dict(holders=n,groups=comparisons,
                endpoint_disagreement=str((1-Fraction(-1,31)**5)/2))


def literal_words(arities):
    interface=list(range(len(arities)-1))
    next_name=len(interface)
    holders=[]
    marks=[]
    for j,a in enumerate(arities):
        h=[k for k in interface if k==j-1 or k==j]
        extra=list(range(next_name,next_name+a-len(h)))
        next_name+=len(extra)
        h+=extra
        holders.append(tuple(h))
        marks.append(extra[0])
    masks=[sum(1<<x for x in h) for h in holders]
    u,v=marks[0],marks[-1]
    cnt=[0,0]
    for w in range(1<<next_name):
        if all(w&m not in (0,m) for m in masks):
            cnt[((w>>u)^(w>>v))&1]+=1
    C=Fraction(1)
    for a in arities:
        C*=Fraction(-1,2**(a-1)-1)
    assert Fraction(cnt[1],sum(cnt))==(1-C)/2
    return dict(arities=arities,allowed=sum(cnt),unequal=cnt[1],fraction=str((1-C)/2))


if __name__=='__main__':
    print(json.dumps(dict(all_tree_comparisons=verify_trees(6),
                          same_state_readings=[frozen_example(False),frozen_example(True)],
                          literal_trees=[literal_words(a) for a in
                                         [(3,3),(3,3,3),(3,4,3),(3,4,5),(4,3,3,4),
                                          (3,7,3),(3,3,4,3,3)]]),indent=2))
