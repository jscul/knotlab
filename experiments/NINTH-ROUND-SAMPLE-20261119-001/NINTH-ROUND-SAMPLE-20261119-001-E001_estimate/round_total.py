"""Verify the identity for the full next round and the specified complementary pairs."""
import json
from pathlib import Path
import sys
from decimal import Decimal, ROUND_CEILING

from parts import read_stage
from residual import covering_test


def main():
    base=Path(sys.argv[1])
    here=Path(__file__).resolve().parent
    out=here.parents[2]/"artifacts"/here.parent.name/here.name
    def get(name):
        return json.loads((out/name).read_text())
    n, blocks, masks, adj=read_stage(base/"age8.txt")
    allpts=(1<<n)-1
    held=[]
    for b,mask in zip(blocks,masks):
        common=allpts^mask
        for x in b:
            common &= adj[x]
            if not common:
                held.append(mask)
                break
    assert not any(a==0 for a in adj) and len(held)==203
    parents=json.loads((base/"parents8.json").read_text())
    singles=[i for i,p in enumerate(parents) if len(p)==1]
    assert len(singles)==1 and adj[singles[0]].bit_count()==1
    # An individual with only one parent has every neighbor in that same block.
    # Its only candidate pair is residual, so demand is one; two loose yield one offshoot.
    small=json.loads((base/"exact-pairs-8-0-160.json").read_text())
    test=covering_test(n,blocks,masks,adj)
    pairs=list(map(tuple,small["residual"]))
    only=(adj[singles[0]]&-adj[singles[0]]).bit_length()-1
    pairs.append(tuple(sorted((only,singles[0]))))
    pairs=set(pairs)
    assert all(((adj[x]>>y)&1) and not test(x,y) for x,y in pairs)
    partner=get("precision_rectangle.json")
    sz=partner["k"]
    marked=partner["pairs"]
    assert len(marked)==sz and len({x for pair in marked for x in pair})==2*sz
    for i,(a,b) in enumerate(marked):
        assert not ((adj[a]>>b)&1)
        for c,d in marked[:i]:
            assert all((adj[x]>>y)&1 for x in (a,b) for y in (c,d))
    # In a held maximal block at most one endpoint of each pair occurs. Count exactly
    # which transversal signatures this block can contain, rather than subtracting all 203.
    signatures={tuple(a if mask & (1<<a) else b for a,b in marked)
                for mask in held if all(mask & ((1<<a)|(1<<b)) for a,b in marked)}
    minimum_big=(1<<sz)-len(signatures)
    lo_raw=Decimal(get("estimate_heldout.json")["lower_limit_99pct"])
    lo=int(lo_raw.to_integral_value(rounding=ROUND_CEILING))-len(held)+len(pairs)+1
    result=dict(junctions=n,held_maximal_blocks=len(held),lone=0,offshoots=1,
                sole_one_parent_junction=singles[0],sole_neighbor=only,
                audited_residual_pairs=sorted(pairs),residual_pairs_lower=len(pairs),
                partnered_pairs=sz,held_transversal_signatures=len(signatures),
                unheld_groups_proved_at_least=minimum_big,next_births_proved_at_least=minimum_big+len(pairs)+1,
                next_births_one_sided_99pct_lower=lo,
                residual_pairs_uniform_999_interval=get("residual8.json")["interval"],
                age_seven_exact_control=28099-91+56+1)
    assert result["age_seven_exact_control"]==28065
    (out/"round_total.json").write_text(json.dumps(result,indent=2)+"\n")
    print({k:v for k,v in result.items() if k!="audited_residual_pairs"})

if __name__=="__main__":
    main()

