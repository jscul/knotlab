"""Check every negative pair directly, then repeat the exhaustive coverage after a reversal."""
import argparse
import json
from pathlib import Path
import subprocess
from group_profile import Stage,members


def verify(source,receipt,engine,work):
    stage=Stage(source)
    d=json.loads(receipt.read_text())
    target={tuple(pair) for pair in d['residual_pairs']}
    def covered(candidates,held):
        if not held:return True
        rest=candidates
        candidates_by_block=[]
        for b in held:
            choices=candidates&~stage.blocks[b]
            if not choices:return False
            candidates_by_block.append(choices)
            rest &= ~stage.blocks[b]
        if rest:return True
        split=min(candidates_by_block,key=int.bit_count)
        return any(covered(candidates&stage.hood(stage.at[u]),held.intersection(stage.at[u]))
                   for u in members(split))
    for u,v in target:
        held=set(stage.at[u]).intersection(stage.at[v])
        assert held and not covered(stage.hood(stage.at[u])&stage.hood(stage.at[v]),held)
    reverse=work/(source.stem+'.reverse.txt')
    with reverse.open('w') as f:
        print(stage.n,len(stage.blocks),file=f)
        for block in reversed(stage.blocks):
            print(*(stage.n-1-v for v in members(block)),file=f)
    proc=subprocess.run([str(engine),str(reverse)],text=True,capture_output=True,check=True)
    row=json.loads(proc.stdout)
    assert {(stage.n-1-v,stage.n-1-u) for u,v in row['residual_pairs']}==target
    assert row['candidate_pairs']==d['candidate_pairs']
    return dict(candidate_pairs=d['candidate_pairs'],individual_negative_pairs=len(target),
                covering_groups_original=d['covering_groups'],covering_groups_reversed=row['covering_groups'],
                row_and_block_order_reversed=True,full_residual_sets_matched=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('receipt',type=Path);ap.add_argument('engine',type=Path)
    ap.add_argument('work',type=Path);ap.add_argument('out',type=Path)
    args=ap.parse_args();result=verify(args.source,args.receipt,args.engine,args.work)
    args.out.write_text(json.dumps(result,indent=1)+'\n');print(result)
