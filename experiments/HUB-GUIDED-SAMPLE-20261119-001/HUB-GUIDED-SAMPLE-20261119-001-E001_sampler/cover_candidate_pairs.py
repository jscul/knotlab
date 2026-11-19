"""Exhaust a finite roster's candidate pairs using literal unheld covering-group certificates."""
import argparse
import hashlib
import json
from pathlib import Path
from group_profile import Stage, members,pack


def solve(stage):
    n=stage.n
    closure=[stage.hood(s) if s else 1<<u for u,s in enumerate(stage.at)]
    holders=[sum(1<<b for b in s) for s in stage.at]
    left=[closed & ~((1<<(u+1))-1) for u,closed in enumerate(closure)]
    candidate=sum(x.bit_count() for x in left)
    def witness(common,h):
        if not h:return []
        outsider=common
        shortest=None
        for b in members(h):
            extra=common & ~stage.blocks[b]
            if not extra:return None
            outsider &= ~stage.blocks[b]
            if shortest is None or extra.bit_count()<shortest.bit_count():shortest=extra
        if outsider:return [(outsider & -outsider).bit_length()-1]
        for w in members(shortest):
            suffix=witness(common & closure[w],h & holders[w])
            if suffix is not None:return [w,*suffix]
        return None
    pairs=[];num=0;digest=hashlib.sha256()
    for u in range(n):
        while left[u]:
            bit=left[u] & -left[u]
            v=bit.bit_length()-1
            complete=witness(closure[u]&closure[v],holders[u]&holders[v])
            if complete is None:
                pairs.append((u,v))
                left[u]^=bit
                continue
            initial=[u,v,*complete]
            common=stage.full
            holding=(1<<len(stage.blocks))-1
            for w in initial:
                common &= closure[w]
                holding &= holders[w]
            group=pack(initial,n)
            assert common & group==group and not holding
            possible=common & ~group
            while possible:
                first=possible & -possible
                w=first.bit_length()-1
                group |= first
                possible &= closure[w] ^ first
            # These complete groups need not be enumerated globally. Each
            # individually witnesses every pair it covers. Check the witness.
            mask=stage.full
            for w in members(group):
                mask &= closure[w]
                left[w] &= ~group
            assert mask==group
            digest.update(group.to_bytes((n+7)//8,'little'))
            num+=1
    return dict(live=n,inspected_candidate_pairs=candidate,residual_pairs=len(pairs),pairs=pairs,
                unheld_covering_groups=num,ordered_bitset_sha256=digest.hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();row=solve(Stage(a.stage));a.out.write_text(json.dumps(row,indent=1)+'\n')
    print(row['inspected_candidate_pairs'],row['unheld_covering_groups'],row['residual_pairs'],flush=True)
