"""Certify global sector boundaries, old held groups, and disjoint extension populations."""
import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from structure_union import bits,read_blocks


def masks_and_neighbors(n,blocks):
    masks=[sum(1<<v for v in block) for block in blocks]
    owners=[[] for _ in range(n)]
    for i,block in enumerate(blocks):
        for v in block:
            owners[v].append(i)
    neighborhoods=[]
    for v,hubs in enumerate(owners):
        seen=1<<v
        for h in hubs:
            seen |= masks[h]
        neighborhoods.append(seen)
    return masks,neighborhoods


def common(vertices,world,neighborhoods):
    result=world
    for v in bits(vertices):
        result &= neighborhoods[v]
    return result


def certificate(n,blocks,items):
    all_sites=(1<<n)-1
    masks,neighborhoods=masks_and_neighbors(n,blocks)
    rows=[]
    universal=[]
    domains=[]
    for left,right,size in items:
        intersect=masks[left]&masks[right]
        two=masks[left]|masks[right]
        where=common(intersect,all_sites,neighborhoods)
        assert two & ~where==0
        traces=set()
        held=[]
        for j,old in enumerate(masks):
            if intersect & ~old:
                continue
            if common(old,all_sites,neighborhoods)!=old:
                continue
            trace=old&two
            if common(trace,two,neighborhoods)==trace:
                traces.add(trace)
                held.append(j)
        row=dict(hubs=[left,right],core_sites=intersect.bit_count(),union_sites=two.bit_count(),
                 common_neighborhood_size=where.bit_count(),extra_sites=(where^two).bit_count(),
                 globally_held_maximal_sets_containing_core_and_maximal_on_union=held,
                 distinct_held_traces_on_full_union=len(traces))
        # Direct checks of literal witnesses found by traversing the nonjoinability relation.
        obstructions={
            (35,0):[4626,7633,13,7855,1072,7101,15610],
            (4,362):[8992,3841,17489],
            (13,31):[7349,231,8746]}
        if (left,right) in obstructions:
            cycle=obstructions[left,right]
            assert len(cycle)%2==1 and len(cycle)==len(set(cycle))
            for v,w in zip(cycle,cycle[1:]+cycle[:1]):
                assert (where>>v)&1 and not (neighborhoods[v]>>w)&1
            row["odd_nonjoinability_cycle_in_joint_neighborhood"]=cycle
        if size is not None:
            row.update(full_union_count=size,large_global_groups_lower=size-len(traces))
        universal.append(intersect)
        domains.append(where)
        rows.append(row)
    disjoint=[]
    for i,j in combinations(range(len(rows)),2):
        candidates=universal[j]&~domains[i]
        if candidates:
            y=next(bits(candidates))
            x=next(bits(universal[i]&~neighborhoods[y]))
            assert not (neighborhoods[x]>>y)&1
            disjoint.append(dict(first_hubs=rows[i]["hubs"],second_hubs=rows[j]["hubs"],
                                 first_universal_site=x,second_universal_site=y))
    return rows,disjoint


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage",type=Path)
    ap.add_argument("--out",type=Path)
    ap.add_argument("--counts",type=Path)
    args=ap.parse_args()
    n,blocks=read_blocks(args.stage)
    counts=json.loads(args.counts.read_text()) if args.counts else []
    lookup={tuple(v["hubs"]):v["count"] for v in counts}
    ids=[(35,0),(13,4),(4,362),(13,31),(3,31)]
    items=[(i,j,lookup.get((i,j))) for i,j in ids]
    rows,pairs=certificate(n,blocks,items)
    report=dict(stage_sha256=hashlib.sha256(args.stage.read_bytes()).hexdigest(),
                rows=rows,disjointness_certificates=pairs)
    if args.out:
        args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
