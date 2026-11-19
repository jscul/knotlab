"""Add certified disjoint populations from two complete counts and a projection."""
import argparse
import json
from pathlib import Path

from structure_export import physical_sites
from structure_receipts import receipt
from structure_sectors import common, masks_and_neighbors
from structure_union import context, irreducible, project, read_blocks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",type=Path)
    parser.add_argument("artifacts",type=Path)
    parser.add_argument("--k",type=int,default=180)
    args=parser.parse_args()
    folder,art=args.folder,args.artifacts
    n,blocks=read_blocks(folder/'start-03-age08.txt')
    masks,ngh=masks_and_neighbors(n,blocks)
    left,right,physical=context(blocks,3,31)
    selected=list(irreducible(physical))[:args.k]
    cols,_,rows=project(physical,left,selected)
    sites=physical_sites(blocks,3,31,left,right,physical,cols)
    induced=sum(1<<v for v,_,_ in sites)
    universal=masks[3]&masks[31]
    world=(1<<n)-1
    assert (universal&~induced)==0
    held=[]
    for i,mask in enumerate(masks):
        if universal&~mask==0 and common(mask,world,ngh)==mask:
            trace=mask&induced
            if common(trace,induced,ngh)==trace:
                held.append(trace)
    cnf=f'structure_3_31_{args.k}.cnf'
    answers=[receipt(folder,f'structure_3_31_{args.k}.log',cnf,'d4'),
             receipt(folder,f'structure_ganak_3_31_{args.k}.log',cnf,'ganak')]
    total=answers[0]["count"]
    assert total==answers[1]["count"]
    projection=dict(hubs=[3,31],columns=args.k,physical_sites=len(sites),raw_count=total,
                    distinct_held_traces=len(set(held)),unheld_lower=total-len(set(held)),receipts=answers)
    previous=json.loads((art/'structure_sectors.json').read_text())
    complete=[row for row in previous["rows"] if "large_global_groups_lower" in row]
    keep={(35,0),(13,4),(3,31)}
    pairs=[w for w in previous["disjointness_certificates"] if tuple(w["first_hubs"]) in keep
           and tuple(w["second_hubs"]) in keep]
    assert len(pairs)==3
    two=sum(row["large_global_groups_lower"] for row in complete)
    extra=json.loads((art/'literal_residual03.json').read_text())['residual_count']
    assert extra==1241
    report=dict(projection=projection,first_two_complete_populations_unheld_lower=two,
                disjointness_certificates=pairs,large_groups_lower=two+projection["unheld_lower"],
                residual_pairs=extra,offshoots=1,
                all_births_lower=two+projection["unheld_lower"]+extra+1)
    (art/'structure_bound.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if isinstance(v,int)})
    print({k:v for k,v in projection.items() if k!='receipts'})

if __name__=="__main__":
    main()
