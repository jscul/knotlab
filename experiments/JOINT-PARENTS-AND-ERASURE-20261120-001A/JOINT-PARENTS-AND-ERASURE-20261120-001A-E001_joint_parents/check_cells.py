"""Compare ordinary maximal witnessed groups and grants with the proposed mixed rank model."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import networkx as nx

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
RANK_LIMIT = 9


def groups(labels, blocks):
    g=nx.Graph()
    g.add_nodes_from(labels)
    for block in blocks:
        g.add_edges_from(combinations(block,2))
    higher=[frozenset(c) for c in nx.find_cliques(g)
            if len(c)>=3 and not any(set(c)<=b for b in blocks)]
    return higher+[frozenset(p) for p in g.edges if not any(set(p)<=c for c in higher)]


def prepare(modes):
    real=set(range(7))
    gates=[frozenset((0,1,2)),frozenset((3,4,5))]
    normal=[frozenset((1,3)),frozenset((0,6))]
    split=[a for a,m in zip(gates,modes) if m=="S"]
    blocks=normal.copy()
    blocks.extend(c for g,m in zip(gates,modes) for c in ([g] if m=="C" else map(frozenset,combinations(g,2))))
    h={a:max(2,sum(len(b)-1 for b in normal+gates if a in b)) for a in real}
    original=groups(real,blocks)
    demand=Counter(x for group in original for x in group)
    g=nx.Graph()
    for b in normal+gates:
        g.add_edges_from(combinations(b,2))
    nxt=7
    for a in sorted(real):
        for _ in range(h[a]-demand[a]):
            root=nxt
            nxt+=1
            g.add_edge(a,root)
            for _ in range(max(0,3-h[a])):
                last=root
                for _ in range(RANK_LIMIT+2):
                    g.add_edge(last,nxt)
                    last=nxt
                    nxt+=1
    return real,g,split,blocks,h


def run(modes):
    real,g,split,initial_blocks,initial_h=prepare(modes)
    def rank(s):
        return len(s)-sum(t<=s for t in split)
    def extensions(s):
        result=set()
        for x in s:
            for y in g[x]:
                if y in s:
                    continue
                t=s|{y}
                for cell in split:
                    if len(cell&t)>=2:
                        t=t|cell
                if rank(t)==rank(s)+1:
                    result.add(frozenset(t))
        return result
    current=[frozenset({x}) for x in sorted(real)]
    h=[initial_h[x] for x in sorted(real)]
    blocks=initial_blocks
    rows=[]
    for n in range(1,RANK_LIMIT+1):
        nextgroups=groups(range(len(current)),blocks)
        spent=Counter(i for q in nextgroups for i in q)
        assert all(spent[i]<=h[i] for i in range(len(h)))
        candidates=nextgroups+[frozenset({i}) for i in range(len(h)) for _ in range(h[i]-spent[i])]
        nextblocks=[{k for k,q in enumerate(candidates) if i in q} for i in range(len(current))]
        forecast=groups(range(len(candidates)),nextblocks)
        future_demand=Counter(i for q in forecast for i in q)
        next_h=[max(1,3-len(q),future_demand[i]) for i,q in enumerate(candidates)]
        supers=defaultdict(set)
        for i,s in enumerate(current):
            for t in extensions(s):
                supers[t].add(i)
        by_parents=defaultdict(list)
        for t,ps in supers.items():
            by_parents[frozenset(ps)].append(t)
        next_cur=[]
        for i,ps in enumerate(candidates):
            assert by_parents[ps],(n,modes,ps)
            t=by_parents[ps].pop()
            assert next_h[i]==len(extensions(t)),(n,modes,t,ps,next_h[i],len(extensions(t)))
            next_cur.append(t)
        assert all(not ts for ts in by_parents.values())
        rows.append({"new_rank":n+1,"current":len(current),"new":len(next_cur),"parent_arities":dict(sorted(Counter(map(len,candidates)).items())),
                     "fresh_distribution":dict(sorted(Counter(next_h).items()))})
        current,h,blocks=next_cur,next_h,nextblocks
    return rows


def main():
    cases={"".join(m):run(m) for m in product("CS",repeat=2)}
    data={"kind":"Complete small examples of the ordinary parent and price theorem; no frequency inference.",
          "two_cycles":"Three donors on each side of a single joining pair, plus one spare-bearing terminal.",
          "laws":"Nonclosing ordinary end under parity and not-all-equal","cases":cases}
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/"cell_check.json"
    p.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("Complete new births:",sum(row["new"] for rr in cases.values() for row in rr))
    print(sha256(p.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
