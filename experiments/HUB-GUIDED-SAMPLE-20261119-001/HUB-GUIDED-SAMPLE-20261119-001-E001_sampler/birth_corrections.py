"""Count held maximal groups and sample residual pairs after an exact first stratum."""
import argparse
import gzip
import json
import math
from collections import Counter
from pathlib import Path
from random import Random

from group_profile import Stage, members


def correction(directory, stem, draws=256, batches=32, seed=202611199610, exhaustive=False):
    stage = Stage(directory/(stem+'.txt'))
    n = stage.n
    with gzip.open(directory/(stem+'.degrees.json.gz'),'rt') as f:
        degrees=json.load(f)
    with (directory/(stem+'.meta.json')).open() as f:
        meta=json.load(f)
    graph_rows=lambda v:stage.hood(stage.at[v])
    bsize=[b.bit_count() for b in stage.blocks]
    easy_sites=set()
    easy_at=Counter()
    for v,sig in enumerate(stage.at):
        for b in sig:
            if degrees[v]+1==bsize[b]:
                easy_sites.add(v)
                easy_at[b]+=1
                break
    easy=sum(c*(bsize[b]-1)-math.comb(c,2) for b,c in easy_at.items())
    total=meta['candidate_pairs']
    residual_frame=total-easy
    def is_held_block(b):
        block=stage.blocks[b]
        if b in easy_at:
            return True
        outside=stage.full ^ block
        inside=sorted(members(block),key=degrees.__getitem__)
        for j,u in enumerate(inside):
            if outside.bit_count()<len(inside)-j:
                return not any(block & ~graph_rows(v)==0 for v in members(outside))
            outside &= graph_rows(u)
            if not outside:
                return True
        return not outside
    held=sum(is_held_block(i) for i in range(len(stage.blocks)))
    law={}
    for sig in set(stage.at):
        law[sig]=sum(1<<b for b in sig)
    active=[v for v in range(n) if v not in easy_sites and degrees[v]]
    def extends(common, holders):
        # Search for any extension escaping all currently holding blocks.
        if not holders:
            return True
        outside_all=common
        shortest=None
        for b in members(holders):
            outside = common & ~stage.blocks[b]
            if not outside:
                return False
            outside_all &= ~stage.blocks[b]
            if shortest is None or outside.bit_count()<shortest.bit_count():
                shortest=outside
        if outside_all:
            return True
        return any(extends(common & graph_rows(w),holders & law[stage.at[w]]) for w in members(shortest))
    exact_residual=None
    if exhaustive:
        exact_residual=easy+sum(
            not extends(graph_rows(u)&graph_rows(v),law[stage.at[u]]&law[stage.at[v]])
            for i,u in enumerate(active) for v in active[i+1:] if law[stage.at[u]]&law[stage.at[v]])
    results=[]
    stage_number=int(stem[6:8])
    for i in range(batches):
        rng=Random(seed+10000*stage_number+i)
        hits=0
        if residual_frame:
            for _ in range(draws):
                while True:
                    u,v=rng.choice(active),rng.choice(active)
                    hold=law[stage.at[u]] & law[stage.at[v]]
                    if u != v and hold:
                        break
                hits+=not extends(graph_rows(u)&graph_rows(v),hold)
        results.append(hits)
    constant=meta['exact_offshoots']-meta['isolated']-held
    assert constant is not None and 0<=residual_frame<=total
    return dict(stage=stem,live=n,total_candidate_pairs=total,held=held,isolated=meta['isolated'],
                offshoots=meta['exact_offshoots'],raw_maximum_to_birth_term=constant,
                easy_residual_pairs=easy,nontrivial_candidate_pairs=residual_frame,exact_residual=exact_residual,
                samples_per_replicate=draws if residual_frame else 0,hits=results,base_seed=seed+10000*stage_number,
                weighting='Within this stage, independent uniform candidate pairs outside the exact stratum, with replacement.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory',type=Path)
    ap.add_argument('stem')
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    data=correction(args.directory,args.stem)
    args.output.write_text(json.dumps(data,indent=1)+'\n')
    print(data['stage'], data['held'],data['easy_residual_pairs'],sum(data['hits']),flush=True)
