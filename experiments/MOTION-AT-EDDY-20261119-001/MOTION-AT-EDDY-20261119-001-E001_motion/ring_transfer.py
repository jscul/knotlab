"""Reconstruct and check a shortest local parity transfer between two closed rings."""
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import json

from motion_stage import load_marks, load_stage

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[2]/'artifacts'/HERE.parent.name/HERE.name


def paths(graph, start):
    parent={start:None}
    pending=deque([start])
    while pending:
        u=pending.popleft()
        for v in sorted(graph[u]-parent.keys()):
            parent[v]=u
            pending.append(v)
    def path(target):
        p=[target]
        while p[-1]!=start: p.append(parent[p[-1]])
        return list(reversed(p))
    return {k:path(k) for k in graph}


def transfer(name):
    raw=load_stage(name,0)
    stage=load_stage(name)
    rings=load_marks(name)['ring_edges']
    original={e for e,owners in raw.owners.items() if len(owners)==2}
    turns={frozenset(q&original):q for q in stage.ordinary_quads()}
    graph={e:set() for e in original}
    for legs in turns:
        u,v=legs;graph[u].add(v);graph[v].add(u)
    target=tuple(sorted(set(rings[0])|set(rings[1])))
    routes={i:paths(graph,i) for i in target}

    @lru_cache(maxsize=None)
    def matching(remaining):
        if not remaining:return 0,()
        first,*rest=remaining
        options=[]
        for other in rest:
            r=tuple(v for v in rest if v!=other)
            cost,pairs=matching(r)
            options.append((cost+len(routes[first][other])-1,((first,other),)+pairs))
        return min(options)

    distance,pairs=matching(target)
    used=set()
    for i,j in pairs:
        path=routes[i][j]
        for u,v in zip(path,path[1:]):
            used.symmetric_difference_update({turns[frozenset([u,v])]})
    assert len(used)==distance
    events=[set(q) for q in sorted(used,key=lambda q:sorted(q))]
    current=set(rings[0])
    private=defaultdict(list)
    old_holders=len(raw.stars)
    for q in events:
        current.symmetric_difference_update(q)
        for b in q-original:
            a,c=sorted(stage.owners[b])
            assert a<old_holders<=c
            private[a].append((b,c))
    for holder,row in sorted(private.items()):
        assert len(row)%2==0
        for (x,c),(y,d) in zip(row[::2],row[1::2],strict=True):
            assert c!=d
            ex=min(set(stage.stars[c])&stage.loose)
            ey=min(set(stage.stars[d])&stage.loose)
            change={x,y,ex,ey}
            assert len(change)==4 and change in stage.minimum_response(x).supports
            events.append(change)
            current.symmetric_difference_update(change)
    assert current==set(rings[1]) and len(events)==2*distance
    state=set(rings[0]);max_loose=0
    for change in events:
        assert stage.allowed_change(change)
        state.symmetric_difference_update(change)
        assert stage.allowed_change(state)
        max_loose=max(max_loose,len(state&stage.loose))
    return {'minimum_events':len(events),'least_ordinary_wedges':distance,
            'starting_support':rings[0],'final_support':rings[1],
            'max_loose_in_constructed_sequence':max_loose,'four_bit_events':[sorted(q) for q in events]}


def main():
    result={k:transfer(k) for k in ['T4','T8','T81']}
    assert [v['minimum_events'] for v in result.values()]==[18,26,50]
    (DATA/'ring_transfer.json').write_text(json.dumps(result,indent=2)+'\n')
    print({k:v['minimum_events'] for k,v in result.items()})


if __name__=='__main__':main()
