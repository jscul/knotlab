"""Sample full legal groups by uniformly ranking maximal groups of a counted part."""
import argparse
import hashlib
import json
from pathlib import Path
from random import Random
from group_profile import Stage, pack, members, summary
from structure_rank import load, unrank


def full_group(stage, seed_group):
    group=pack(seed_group,stage.n)
    allowed=stage.full
    # Memoize signatures only. Intersection before the greedy extension is exact.
    for sig in set(stage.at[v] for v in seed_group):
        allowed &= stage.hood(sig)
    assert group & allowed == group
    outside=allowed & ~group
    outside_before=outside.bit_count()
    while outside:
        bit=outside & -outside
        v=bit.bit_length()-1
        group |= bit
        outside &= stage.hood(stage.at[v]) ^ bit
    literal=list(members(group))
    common=stage.full
    for sig in set(stage.at[v] for v in literal):
        common &= stage.hood(sig)
    assert common == group
    return literal,outside_before


def sample(blocks, recipe, reps=32):
    data=load(recipe)
    rng=Random(82902143)
    stage=Stage(blocks)
    H=pack((x[0] for x in data['sites']),stage.n)
    results=[]
    for _ in range(reps):
        rank=rng.randrange(data['count'])
        K=unrank(data,rank)
        g,eligible=full_group(stage,K)
        bits=pack(g,stage.n)
        assert bits & H == pack(K,stage.n)
        row=stage.profile(g)
        row.update(rank=rank,prefix_size=len(K),outside_common=eligible,
                   physical_sha256=hashlib.sha256(bits.to_bytes((stage.n+7)//8,'little')).hexdigest())
        results.append(row)
    return dict(seed=82902143,exact_inverse_weight=data['count'],samples=reps,
                weighting='Uniform over the injective greedy extensions of the maximal groups of the selected induced part.',
                notes='Lower partner count is witnessed. Upper counts group members each admitting any individually compatible replacement.',
                recipe_sha256=hashlib.sha256(recipe.read_bytes()).hexdigest(),rows=results,statistics=summary(results))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('blocks',type=Path)
    ap.add_argument('recipe',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    value=sample(args.blocks,args.recipe)
    args.output.write_text(json.dumps(value,indent=1)+'\n')
    print(value['statistics'],flush=True)
