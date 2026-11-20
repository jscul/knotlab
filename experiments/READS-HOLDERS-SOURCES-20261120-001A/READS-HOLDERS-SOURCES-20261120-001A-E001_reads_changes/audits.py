"""Cross-checks of the tied signs, NAE product mixture and fixed-size sampling intervals."""
from fractions import Fraction
from itertools import combinations
import json
from scipy.stats import beta
from operations import LAW, OUT, change, np, parity, probability_table, read, save, weighting
from tables import split,table,compare_old,canonical
from holdings import parity_ties


def interval(k,n,risk):
    return (0. if k==0 else float(beta.ppf(risk/2,k,n-k+1)),
            1. if k==n else float(beta.ppf(1-risk/2,k+1,n-k)))


def sampling_intervals():
    source=json.loads((OUT/"placements.json").read_text())
    out=[]
    for broad in [r for r in source["rates"] if r["n"]==0]:
        parts=[r for r in source["rates"] if r["n"] and all(r[k]==broad[k] for k in ("stratum","law","age")) and r["observed"]]
        bounds=[interval(r["two_or_more"],r["observed"],.05/len(parts)) for r in parts]
        n=sum(r["observed"] for r in parts)
        combined=[sum(r["observed"]*q[j] for r,q in zip(parts,bounds))/n for j in (0,1)]
        out.append(dict(stratum=broad["stratum"],law=broad["law"],age=broad["age"],numerator=broad["two_or_more"],denominator=n,
                        simultaneous_weighted_95=combined,weights=[[r["n"],r["observed"]] for r in parts]))
    return out


def alternate_checks():
    stars,a,b=split(2)
    a2=[(change(1),a[0][1]),(change(4),a[1][1])]
    alts={}
    for law in LAW:
        f=weighting(stars,law)
        alt=table(f,a2,b,solver=False)
        alts[law]=dict(score=alt["equal_at_shared"],same_full_table=(probability_table(alt["rows"])==probability_table(table(f,a,b,solver=False)["rows"])))
    c2=[[0,1,2],[0,1,3]];c1=[[0,1,2],[2,3,4]]
    orientations={}
    for name,holds in (("four",c2),("five",c1)):
        n=1+max(map(max,holds))
        hits=[]
        for k in range(1,n):
            for am in combinations(range(n),k):
                if not all(len(set(am)&set(row))==2 for row in holds):continue
                bm=sorted(set(range(n))-set(am))
                hits.append(dict(alice=am,bob=bm,rank=parity_ties(holds,am,bm)["ties"]))
        orientations[name]=hits
    # Use the two integer column vectors for b in its change basis; the common scale is sqrt(2).
    blocks=[]
    for c in (0,1):
        col=np.array([[int(not ((u^c)==c==b)) for b in (0,1)] for u in (0,1)],dtype=int)
        blocks.append(col @ np.array([[1,1],[1,-1]]))
    gram=sum(np.outer(m.flatten(),m.flatten()) for m in blocks)
    want=np.array([[2,0,4,0],[0,2,0,0],[4,0,8,0],[0,0,0,0]])
    assert np.array_equal(gram,want)
    from holdings import next_stage
    one=[[0,1,2]]
    _,stage=next_stage(one,"parity")
    a=[];b=[];chosen=[]
    for child in stage[1:3]:
        [old]=set(child)&set(one[0])
        fresh=sorted(set(child)-{old})
        a.append((change(fresh[0]),read(old,fresh[0])))
        b.append((change(fresh[1]),read(fresh[1])))
        chosen.append(dict(child=child,alice=[old,fresh[0]],bob=[fresh[1]]))
    sample=table(weighting(stage,"parity"),a,b,solver=False)
    embedded=dict(whole=stage,selected=chosen,score=sample["equal_at_shared"],full_comparison=compare_old(sample["rows"]))
    canonical_types={law:{n:canonical([list(range(n))],law)[0]["canonical"] for n in range(3,9)} for law in LAW}
    separate=[[0,1,2],[3,4,5]]
    f=weighting(separate,"parity")
    f*=np.array([1-2*((((x>>0)&(x>>3)&1)^((x>>1)&(x>>4)&1))) for x in range(64)],dtype=int)
    a=[(change(0,2),read(0)),(change(1,2),read(1))]
    b=[(read(3),change(3,5)),(read(4),change(4,5))]
    phase=table(f,a,b,solver=False)
    phase_control=dict(holdings=separate,extra_phase="(-1)^(x0*x3+x1*x4)",reversed_local_reads_on_b=True,
                       score=phase["equal_at_shared"],mismatches=compare_old(phase["rows"])["differences"])
    return dict(nonfactorizing_phase_control=phase_control,reached_split_subcollection=embedded,canonical_projected_law_types=canonical_types,alternate_alice_changes=alts,same_side_two_place_controls=orientations,
                nae_register_in_b_change_basis_numerators_over_12=gram.tolist(),
                alternate_law_exact_product_mixture=["5/6","1/6"])


def run():
    save("audits.json",dict(fixed_size_sampling_intervals=sampling_intervals(),checks=alternate_checks()))
