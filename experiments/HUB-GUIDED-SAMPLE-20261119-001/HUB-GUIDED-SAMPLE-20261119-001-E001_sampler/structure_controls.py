"""Validate two-hub counts on all three-by-three contexts and the preceding actual stage."""
import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from structure_compile import compiled
from structure_sectors import common, masks_and_neighbors
from structure_union import bits, context, project, read_blocks, simple_union, transposed


def maximal_sets(neighborhoods):
    n=len(neighborhoods)
    adj=[q & ~(1<<i) for i,q in enumerate(neighborhoods)]
    def visit(pos, available, excluded):
        if not available:
            if not excluded:
                yield pos
            return
        pivot=max(bits(available|excluded),key=lambda v:(adj[v]&available).bit_count())
        to_try=available & ~adj[pivot]
        for v in bits(to_try):
            b=1<<v
            yield from visit(pos|b,available&adj[v],excluded&adj[v])
            available^=b
            excluded|=b
    return list(visit(0,(1<<n)-1,0))


def literal_size_three():
    for graph in range(512):
        cells=[(graph>>(3*i))&7 for i in range(3)]
        closed=[7|((7^x)<<3) for x in cells]
        cross=transposed(dict(enumerate(cells)),list(range(3)))
        closed.extend((7<<3)|(7^cross[j]) for j in range(3))
        brute=set()
        for group in range(1<<6):
            if common(group,(1<<6)-1,closed)==group:
                brute.add(group)
        coords,_,rows=project(cross,list(range(3)))
        e,root=compiled(rows,len(coords),10000)
        physical=set()
        for i in range(e.counts[root]):
            omitted=e.decode(root,i)
            left=7
            for j,v in enumerate(coords):
                if not omitted&(1<<j):
                    left &= ~cross[v]
            right=sum(1<<j for j in range(3) if not (cross[j] & left))
            physical.add(left|(right<<3))
        assert physical==brute
    return 512


def previous(path, next_parents):
    n,blocks=read_blocks(path)
    masks,ngh=masks_and_neighbors(n,blocks)
    if next_parents:
        actual=json.loads(next_parents.read_text())
        ordered=sorted({v for row in actual for v in row})
        assert len(ordered)==n and len(actual)==28065
        index={v:i for i,v in enumerate(ordered)}
        maximal={sum(1<<index[v] for v in row) for row in actual if len(row)>=3}
        world=(1<<n)-1
        maximal.update(m for m in masks if common(m,world,ngh)==m)
        maximal.update(1<<i for i,m in enumerate(ngh) if m==1<<i)
        assert all(common(m,world,ngh)==m for m in maximal)
    else:
        maximal=maximal_sets(ngh)
    assert len(maximal)==28099 and n==386
    order=sorted(range(len(blocks)),key=lambda i:(-len(blocks[i]),i))[:15]
    selected=[]
    differences=0
    zeros=0
    for a,b in combinations(order,2):
        closed=masks[a]&masks[b]
        if not closed:
            continue
        domain=common(closed,(1<<n)-1,ngh)
        union=masks[a]|masks[b]
        left,_,physical=context(blocks,a,b)
        cols,_,rows=project(physical,left)
        norm=len(simple_union(rows))
        full=sum((closed&m)==closed for m in maximal)
        assert norm<=full
        if domain==union:
            assert norm==full
            zeros+=1
        if full>norm:
            differences+=1
        selected.append(dict(hubs=[a,b],common=closed.bit_count(),union=union.bit_count(),
                             outside=(domain^union).bit_count(),two_hub_count=norm,
                             enumerated_global_sector_count=full))
    return dict(stage_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),stage_sites=n,
                source_of_global_groups="Actual next-round parent rows plus globally maximal held blocks and isolates" if next_parents else "Literal global clique traversal",
                maximal_sets_exhausted=len(maximal),pair_comparisons=len(selected),
                closed_sectors=zeros,strict_lower_cases=differences,rows=selected)


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("previous_stage",type=Path)
    ap.add_argument("output",type=Path)
    ap.add_argument("--next-parents",type=Path)
    args=ap.parse_args()
    result=dict(literal_three_by_three=literal_size_three(),previous=previous(args.previous_stage,args.next_parents))
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print({k:v for k,v in result["previous"].items() if k!="rows"})
