"""Physical one-contact comparison and fixed-map checks of delayed encounters."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "experiments" / "GENERATORS-20261120-001A"
sys.path.insert(0, str(next(PRIOR.glob("*_generators"))))
from periodic import (A as NEUTRAL, H_ARCS, P, canonical, contact, frame,
                      name_frames, windows)
from small_periodic import definition, rotate_factors, swapped
from boundaries import law_gate, ownership, recode, source, stage_size, write_layer
from end_operator import from_stars, neighbors

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "matched.json"


def seam_start(a, b, joined):
    paths = [[f"l{i}" for i in range(a+1)], [f"r{i}" for i in range(b+1)]]
    bonds = []
    for path in paths:
        for x,y in zip(path,path[1:]):
            witness = "w"+x+y
            bonds.extend([(x,witness),(y,witness),(y,witness)])
    # Existing spent holders connect the two full structures in both cases.
    v,w = paths[0][-1],paths[1][0]
    bonds.extend([(v,"z"),(v,"z"),("z","y"),("y",w),("y",w)])
    labels = sorted({x for pair in bonds for x in pair})
    ids = {v:i for i,v in enumerate(labels)}
    initial = source(len(ids), [(ids[x],ids[y]) for x,y in bonds],
                     [2 if x in paths[0]+paths[1] else 0 for x in labels])
    if joined:
        bit=max(ownership(initial))+1
        for v in ("z",w):
            initial[ids[v]] += (bit,)
    return initial,ids[paths[0][0]],ids[paths[1][-1]]


def read_end(stars):
    ids=sorted(stars)
    end=from_stars([stars[i] for i in ids])
    graph=nx.Graph()
    adj=neighbors(end)
    graph.add_nodes_from(ids[i] for i in adj)
    graph.add_edges_from((ids[i],ids[j]) for i in adj for j in adj[i])
    opens={ids[i]:h for i,h in end.opens.items()}
    return graph,opens


def min_distance(graph, first, second):
    if not first or not second:
        return None
    distances=nx.multi_source_dijkstra_path_length(graph,first,weight=None)
    return min((distances[u] for u in second if u in distances),default=None)


def seam(a,b,joined,law):
    stars,left,right=seam_start(a,b,joined)
    assert law_gate(stars,law,{})
    d=a+b+1
    out=[]
    for m in range(2,d+5):
        before=stars
        stars=write_layer(before,law)
        holders=ownership(before)
        incoming={v:{holders[bit][0] for bit in row if bit in holders}
                  for v,row in stars.items() if v not in before}
        if m==2:
            la={v for v,ps in incoming.items() if ps=={left}}
            lb={v for v,ps in incoming.items() if ps=={right}}
            ia,ib=set(la),set(lb)
        else:
            ia={v for v,ps in incoming.items() if ps & ia}
            ib={v for v,ps in incoming.items() if ps & ib}
            la={v for v,ps in incoming.items() if ps<=la}
            lb={v for v,ps in incoming.items() if ps<=lb}
        assert len(la)==len(lb)==1
        g,h=read_end(stars)
        g2,h2=read_end(recode(stars,28000+m)[0])
        view=lambda g,h: sorted((len(c),sorted((g.degree[v],h[v]) for v in c))
                                for c in nx.connected_components(g))
        assert view(g,h)==view(g2,h2)
        assert all(g.degree[v]==1 and h[v]==2 for v in la|lb)
        assert len(ia)==len(ib)==m-1
        assert sum(h[u] for u in ia)==sum(h[u] for u in ib)==2*(m-1)
        d_pure=min_distance(g,la,lb)
        d_inc=min_distance(g,ia,ib)
        d_one=min_distance(g,la,ib)
        assert d_inc==(max(0,d+3-m) if joined else None)
        assert d_pure==(d+m-1 if joined else None)
        assert d_one==(d+1 if joined else None)
        assert len(ia&ib)==(max(0,m-d-2) if joined else 0)
        obs=view(g,h)
        out.append(dict(size=m,holdings=stage_size(stars),live=len(g),
                        witnessed_part_sizes=[row[0] for row in obs],
                        pure_separation=d_pure,pure_A_to_inclusive_B=d_one,
                        inclusive_separation=d_inc,inclusive_per_party=len(ia),
                        joint_descendants=len(ia&ib),fresh_of_A_descendants=sum(h[u] for u in ia)))
    return out


def delay(n):
    (first,second),k,_=definition(n)
    second=swapped(second)
    lo,hi=1,k
    while hi-lo>1:
        mid=(hi+lo)//2
        if rotate_factors(first,mid)&rotate_factors(second,mid):
            lo=mid
        else:
            hi=mid
    assert lo==10 and hi==11
    suffixes = {}
    for w in windows(first,k):
        for x in (w,w[::-1]):
            suffixes[x[-lo:]]=x
    for w in windows(second,k):
        for x in (w,w[::-1]):
            if x[:lo] in suffixes:
                start=suffixes[x[:lo]]
                word=start+x[lo:]
                assert word[:k]==start and word[-k:]==x
                assert canonical(start) in rotate_factors(first,k)
                assert canonical(x) in rotate_factors(second,k)
                # Each local turn must switch the physical witness (not just its name).
                seven=source(7,[(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6),(0,1)],
                             (3,0,3,3,3,2,2))
                graph=contact(seven)
                witness=[]
                for a,b in zip(word,word[1:]):
                    (witness_id,)=nx.common_neighbors(graph,a,b)
                    witness.append(witness_id)
                assert all(a!=b for a,b in zip(witness,witness[1:]))
                assert len(word)==2*k-lo
                return dict(n=n,release=k,periods=[len(first),len(second)],max_overlap=lo,
                            steps_to_first_joint=k-lo,first_joint_size=len(word),
                            shared_interval=list(x[:lo]))
    raise AssertionError("longest common interval did not give a mixed descendant")


def alter_staggered(stars,names):
    altered=stars.copy()
    i=H_ARCS.index(("b2","s"))
    w=names.index(f"w{i}")
    b=names.index("b2")
    (bit,)=set(altered[w]) & set(altered[b])
    altered[b]=tuple(t for t in altered[b] if t!=bit)
    owners=ownership(altered)
    assert owners[bit]==[w] and stage_size(stars)==stage_size(altered)
    return altered,w


def staggered_physical(law,off):
    names,original=frame("meeting")
    altered,lone=alter_staggered(original,names)
    stars=altered if off else original
    assert law_gate(stars,law,{})
    orig=stars
    g,h=read_end(stars)
    core=nx.Graph(H_ARCS)
    if off:
        core.remove_edge("s","b2")
        assert g.degree[lone]==0 and h[lone]==1
    assert {frozenset((names[a],names[b])) for a,b in g.edges}=={frozenset(e) for e in core.edges}
    counter=[]
    for m in range(1,5):
        for current in (stars,recode(stars,44000+m)[0]):
            maps,parents=name_frames(names,orig,current)
            assert len(maps)==1
            mp=maps[0]
            seqs=windows(NEUTRAL+P[0]+NEUTRAL+P[1],m)
            def find(seq):
                if len(seq)==1:
                    return mp[seq[0]]
                ps=frozenset([find(seq[1:]),find(seq[:-1])])
                assert len(ps)==2 and len(parents[ps])==1
                return parents[ps][0]
            for seq in seqs:
                v=find(seq)
                expected=2+sum(nx.Graph(H_ARCS).degree[x]-2 for x in seq)
                actual=len(current[v])-2 if m>1 else h[names.index(seq[0])]
                assert expected==actual
        counter.append(stage_size(stars))
        if m<4:
            stars=write_layer(stars,law)
    return counter


def staggered_words(n):
    a,b=(NEUTRAL*n+P[0]+NEUTRAL*n+P[j] for j in (1,2))
    p=len(b)
    common=set(windows(a,p-1))&set(windows(b,p-1))
    assert len(common)==1
    I=common.pop()
    core=nx.Graph(H_ARCS)
    changed=core.copy()
    changed.remove_edge("s","b2")
    changed.add_edges_from([("s","spare"),("b2","out")])
    degree=lambda g,seq: 2+sum(g.degree[x]-2 for x in seq)
    cases=[]
    for q in [p+1,2*p,4*p]:
        for m in [q,q+1,q+5]:
            (active,)= [s for s in windows(a,m) if s[-(p-1):]==I]
            joint=active+("b2",)
            other=active[1:]+("b2",)
            seed=I+("b2",)
            assert seed in windows(b,p) and other[-p:]==joint[-p:]==seed
            assert active in windows(a,m) and other not in windows(b,m)
            assert all(core.has_edge(x,y) for x,y in zip(joint,joint[1:]))
            assert all(x!=z for x,z in zip(joint,joint[2:]))
            assert not changed.has_edge(active[-1],"b2") and changed.has_edge(active[-1],"spare")
            replace=active+("spare",)
            assert degree(core,active)==degree(changed,active)
            assert degree(core,joint)==degree(changed,replace)+1
            # Each outside neighbor in the tree is an actual child. Summing
            # its loose count costs delta(C) + degree(new point) - 2.
            def children(g,seq):
                main=degree(g,seq)
                return [main+g.degree[y]-2 for i,x in enumerate(seq) for y in g[x]
                        if y not in seq[max(0,i-1):i]+seq[i+1:i+2]]
            on,off=children(core,active),children(changed,active)
            assert len(on)==len(off)==degree(core,active)
            assert sum(on)-sum(off)==active.count("s")
            cases.append(dict(release_A=q,size_A=m,older_release_B=p,
                              direct_children_each=len(on),fresh_A=degree(core,active),
                              fresh_joint_on=degree(core,joint),fresh_substitute_off=degree(changed,replace),
                              total_fresh_on=sum(on),total_fresh_off=sum(off)))
    return cases


def main():
    ap=ArgumentParser();ap.add_argument("--out",type=Path,default=OUT)
    path=ap.parse_args().out
    result={"seam":{f"{a},{b}":{law:{arm:seam(a,b,arm=="joined",law) for arm in ("apart","joined")}
                         for law in ("parity","nae")} for a,b in [(2,2),(2,4),(3,5)]},
            "generator_delay":[delay(n) for n in [2,4,6,8]],
            "staggered_physical":{law:{arm:staggered_physical(law,arm=="off") for arm in ("on","off")}
                                  for law in ("parity","nae")},
            "staggered_words":{str(n):staggered_words(n) for n in [1,2,4]}}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    main()
