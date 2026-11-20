"""Check physical parents from anonymous holdings and periodic releases from the fixed map."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(next((ROOT / "experiments" / "READ-ORIGIN-20261120-001A").glob("*_origins"))))
from boundaries import law_gate, ownership, recode, source, stage_size, write_layer
from end_operator import from_stars, neighbors, proposals, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "periodic.json"
A = ("v", "r1", "r2", "r3")
P = [("v", "s", "b" + str(j), "t") for j in range(3)]
CA = ("u", "a3", "a1", "v", "a2")
CB = ("u", "b3", "b1", "v", "b2")
C_ARCS = [("u", "v"), ("u","a1"), ("a1","a2"), ("a2","a3"), ("a3","v"),
          ("u","b1"), ("b1","b2"), ("b2","b3"), ("b3","v")]
C_DOUBLE = [("u","a1"), ("a2","a3"), ("v","b3"), ("b1","b2"), ("u","b1")]
H_ARCS = list(zip(A, A[1:] + A[:1])) + [
    ("v","s"), ("t","v"), ("s","b0"), ("t","b0"), ("s","b1"), ("b1","t"),
    ("t","b2"), ("b2","s")]


def frame(kind):
    if kind == "compact":
        links = C_ARCS + C_DOUBLE
        old = nx.Graph(C_ARCS)
        opens = {p: sum(old.degree[q]-1 for q in old[p]) for p in old}
    else:
        arcs = [edge for edge in H_ARCS if kind == "meeting" or "b2" not in edge]
        links = []
        opens = Counter()
        for i, (p, q) in enumerate(arcs):
            w = f"w{i}"
            links.extend([(p,w), (q,w), (q,w)])
            opens.update([p,q])
    names = sorted({s for edge in links for s in edge})
    idx = {p:i for i,p in enumerate(names)}
    stars = source(len(names), [(idx[p],idx[q]) for p,q in links], [opens.get(p,0) for p in names])
    return names, stars


def contact(stars):
    graph = nx.Graph()
    graph.add_nodes_from(stars)
    shared = Counter(tuple(sorted(owners)) for owners in ownership(stars).values() if len(owners)==2)
    for (a,b), weight in shared.items():
        graph.add_edge(a,b,weight=weight)
    return graph


def name_frames(names, original, stars):
    physical = contact(stars)
    origins = {p for a,b,w in physical.edges(data="weight") if w>=2 for p in (a,b)}
    current = physical.subgraph(origins).copy()
    orig = contact(original)
    for p in current:
        current.nodes[p]["arity"] = len(stars[p])
    for p in orig:
        orig.nodes[p]["arity"] = len(original[p])
    match = nx.algorithms.isomorphism.GraphMatcher(orig, current,
        node_match=lambda a,b:a["arity"]==b["arity"], edge_match=lambda a,b:a["weight"]==b["weight"])
    maps = list(match.isomorphisms_iter())
    assert maps
    rs = nx.multi_source_dijkstra_path_length(physical, origins, weight=None)
    parents = defaultdict(list)
    for child, distance in rs.items():
        if distance:
            ps = frozenset(p for p in physical[child] if rs[p]+1==distance)
            parents[ps].append(child)
    return [{label:mp[i] for i,label in enumerate(names)} for mp in maps], parents


def windows(word, size):
    stream = word * (1 + (size+len(word)-1)//len(word))
    return [stream[i:i+size] for i in range(len(word))]


def canonical(seq):
    return min(seq, seq[::-1])


def compact_source(seq):
    positions = [i for i,q in enumerate(seq) if q == "b1"]
    for j,a in enumerate(positions):
        for b in positions[j+1:]:
            width = b-a
            for i in range(max(0,b-2*width+1), min(a,len(seq)-2*width)+1):
                if seq[i:i+width] == seq[i+width:i+2*width]:
                    return False
    return True


def meeting_source(seq):
    marked = [i for i,q in enumerate(seq) if q in {"b0","b1","b2"}]
    for j,a in enumerate(marked):
        for b in marked[j+1:]:
            s=b-a
            if max(0,b-2*s+1) <= min(a,len(seq)-2*s):
                return False
    return True


def check_physical(kind,law):
    names, original = frame(kind)
    assert law_gate(original,law,{})
    end = from_stars(list(original.values()))
    adj = neighbors(end)
    groups = list(proposals(end))
    assert all(len(t)==2 for t in groups)
    assert all(len(adj[p])==slots for p,slots in end.opens.items())
    G = contact(original)
    shared_block = {}
    for p,q in groups:
        witnesses = list(nx.common_neighbors(G,p,q))
        assert len(witnesses)==1
        label=frozenset((names[p],names[q]))
        shared_block[label]=(witnesses[0],len(set(G[witnesses[0]]) & end.opens.keys()))
    degrees={names[p]:len(adj[p]) for p in adj}
    words=[CA+CB,CA*2+CB] if kind=="compact" else [A+P[0]+A+P[j] for j in (1,2) if P[j][2] in names]
    seed=20261120721
    stars=original
    stage=[]
    # Each size is a whole physical stage. Numbers beyond the last are checked
    # as particular intervals under the separately proved map identification.
    for size in range(1,5):
        decodings=[]
        for presentation in [stars,recode(stars,seed+size)[0]]:
            maps,parents=name_frames(names,original,presentation)
            all_counts=[]
            for mp in maps:
                if kind=="compact":
                    assert len({m["b1"] for m in maps})==1
                cache={}
                def find(seq):
                    if seq not in cache:
                        if len(seq)==1:
                            cache[seq]=mp[seq[0]]
                        else:
                            pair=frozenset((find(seq[:-1]),find(seq[1:])))
                            assert len(pair)==2 and len(parents[pair])==1, (kind,seq,pair)
                            cache[seq]=parents[pair][0]
                    return cache[seq]
                checks=0
                for word in words:
                    for seq in windows(word,size):
                        b=[shared_block[frozenset(pair)] for pair in zip(seq[:-1],seq[1:])]
                        assert all(v[0]!=w[0] for v,w in zip(b,b[1:]))
                        fresh=sum(degrees[q] for q in seq)-sum(w for _,w in b)
                        actual=len(presentation[find(seq)])-2 if size>1 else end.opens[names.index(seq[0])]
                        assert actual==fresh, (kind,seq,actual,fresh)
                        checks+=1
                all_counts.append(checks)
            decodings.append([len(maps),min(all_counts)])
        assert decodings[0]==decodings[1]
        stage.append(dict(size=size,holdings=stage_size(stars),origin_isomorphisms=decodings[0][0],
                          phase_words_checked_per_isomorphism_and_encoding=decodings[0][1]))
        if size<4:
            plan=step(from_stars([stars[i] for i in sorted(stars)]),law,max_births=350)
            assert plan.status=="extend"
            stars=write_layer(stars,law)
    return stage


def symbolic():
    full=nx.Graph(H_ARCS)
    reduced=full.copy()
    reduced.remove_node("b2")
    separated=reduced.copy()
    separated.add_edge("b1","extra")
    degrees=lambda seq,g:2+sum(g.degree[q]-2 for q in seq)
    single=[]; pairs=[]
    for n in range(1,9):
        word=CA*n+CB
        k=2*len(word)
        assert all(map(compact_source,windows(word,k-1))) and not any(map(compact_source,windows(word,k)))
        assert all(len({canonical(w) for w in windows(word,h)})==len(word) for h in range(k,k+4))
        single.append(dict(n=n,period=len(word),release_size=k,phases=len(word)))
        w1,w2=(A*n+P[0]+A*n+P[j] for j in (1,2))
        k=len(w1)
        for w in [w1,w2]:
            assert all(map(meeting_source,windows(w,k-1))) and not any(map(meeting_source,windows(w,k)))
            for h in range(k,k+4):
                rows={canonical(x) for x in windows(w,h)}
                assert len(rows)==k
                if h>k:
                    before={canonical(x) for x in windows(w,h-1)}
                    assert all(canonical(x[:-1]) in before and canonical(x[1:]) in before for x in rows)
        for h in range(k,k+4):
            assert not ({canonical(x) for x in windows(w1,h)} & {canonical(x) for x in windows(w2,h)})
        overlap=set(windows(w1,k-1)) & set(windows(w2,k-1))
        assert len(overlap)==1
        common=overlap.pop()
        left=("b1",)+common
        right=common+("b2",)
        mixed=left+("b2",)
        assert left in windows(w1,k) and right in windows(w2,k)
        assert left==mixed[:-1] and right==mixed[1:]
        assert all(full.has_edge(p,q) for p,q in zip(mixed,mixed[1:]))
        assert all(p!=r for p,r in zip(mixed,mixed[2:]))
        costs=[degrees(left,g) for g in (full,reduced,separated)]
        assert costs[0]-costs[1]==4 and costs[0]-costs[2]==3
        pairs.append(dict(n=n,period=k,first_mixed_size=k+1,phases_each=k,
                          common_oriented_predecessors=1,full_reduced_separate_fresh=costs))
    return dict(emitters=single,encounters=pairs)


def main():
    arg=ArgumentParser();arg.add_argument("--out",type=Path,default=OUT);dest=arg.parse_args().out
    result={"physical":{kind:{law:check_physical(kind,law) for law in ("parity","nae")}
                        for kind in ("compact","meeting","reduced")},"fixed_map":symbolic()}
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    main()

