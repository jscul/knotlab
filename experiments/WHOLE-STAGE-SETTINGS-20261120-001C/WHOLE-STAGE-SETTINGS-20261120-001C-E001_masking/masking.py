"""Exact pre-settings mixture of three ordinary two-terminal correspondences."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import product
from math import lcm, prod
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "masking.json"
BITS = (0, 1)
CELLS = tuple(product(BITS,repeat=2))
WORDS = tuple(product(BITS,repeat=3))
I, P, Q = (0,1,2), (1,0,2), (0,2,1)


def law_ok(law, word):
    return sum(word)%2 == 0 if law == "parity" else 0 < sum(word) < len(word)


def device(law, label, terminals, extra=None, grown=False):
    """Number of legal assignments at one end for a specified terminal triple.

    The five centre distinctions, private address distinctions and the two detector
    openings exhaust the side. An optional edit adds at the end of the chosen queue.
    """
    sizes = [1 if j == label else 2 for j in BITS]
    if extra is not None:
        sizes[extra] += 1
    mass = 0
    for word in product(BITS,repeat=7+sum(sizes)):
        centre = word[:5]
        v = 5+sizes[0]
        u = v+sizes[1]
        slots = (word[5:v],word[v:u],word[u:])
        rows = (centre,centre[:2]+slots[0],centre[2:4]+slots[1],centre[4:]+slots[2]+terminals)
        if not all(law_ok(law,support) for support in rows):
            continue
        multiplicity = 1
        if grown:
            assert sizes == [2,2]
            # Stable proposal order 01,02,12, taking one old slot per parent per proposal.
            old_pairs = ((slots[0][0],slots[1][0]),(slots[0][1],slots[2][0]),(slots[1][1],slots[2][1]))
            multiplicity = prod(sum(law_ok(law,pair+(b,)) for b in BITS) for pair in old_pairs)
        mass += multiplicity
    return mass


@cache
def site(law, label, extra=None, grown=False):
    return tuple(device(law,label,w,extra,grown) for w in WORDS)


def one_piece(law):
    return tuple(tuple(sum(law_ok(law,(a,*m)) and law_ok(law,(b,*m)) for m in CELLS)
                       for b in BITS) for a in BITS)


@cache
def transfer(law, permutation):
    weights = one_piece(law)
    return tuple(tuple(prod(weights[a[i]][b[permutation[i]]] for i in range(3)) for b in WORDS) for a in WORDS)


def layouts(r, s, mode, guards=2):
    p = P if r else I
    q = Q if s else I
    if mode == "commuting":
        q = P if s else I
    if mode == "identity":
        p,q = I,I
    middle = [q,p,q,p] if mode == "reversed" else [p,q,p,q]
    return tuple([I]*guards+middle+[I]*guards)


def matmul(a,b):
    right = tuple(zip(*b))
    return tuple(tuple(sum(x*y for x,y in zip(row,col)) for col in right) for row in a)


UNIT = tuple(tuple(int(i==j) for j in range(8)) for i in range(8))


@cache
def source(law, r, s, mode, weighting="prepared", x=None, y=None):
    maps = layouts(r,s,mode)
    matrices = [transfer(law,p) for p in maps]
    prefix = [UNIT]
    for matrix in matrices:
        prefix.append(matmul(prefix[-1],matrix))
    suffix = [UNIT]
    for matrix in reversed(matrices):
        suffix.append(matmul(matrix,suffix[-1]))
    suffix.reverse()
    grown = weighting=="uniform_final" and (r,s)==(x,y)
    # In the saturated preparation both edit addresses carry two old openings.
    # The same old preparation labels still control their two interior interchanges.
    left_deficit = None if mode == "saturated" else r
    right_deficit = None if mode == "saturated" else s
    aweights = site(law,left_deficit,None if weighting=="prepared" else x,grown)
    bweights = site(law,right_deficit,None if weighting=="prepared" else y,grown)
    joint = {(a,b):aweights[i]*prefix[-1][i][j]*bweights[j]
             for i,a in enumerate(WORDS) for j,b in enumerate(WORDS)}
    total = sum(joint.values())
    def left(j):
        return [sum(w*prefix[j][i][k] for i,w in enumerate(aweights)) for k in range(8)]
    def right(j):
        return [sum(w*suffix[j][k][i] for i,w in enumerate(bweights)) for k in range(8)]
    def cut(j):
        return {w:a*b for w,a,b in zip(WORDS,left(j),right(j))}
    def two(j):
        before,after = left(j),right(j+1)
        return {(a,b):before[i]*matrices[j][i][k]*after[k] for i,a in enumerate(WORDS) for k,b in enumerate(WORDS)}
    guards = (cut(1),cut(len(maps)-1))
    extra = (two(3),two(4)) if mode != "reversed" else (two(4),two(3))
    assert all(sum(d.values())==total for d in (*guards,*extra))
    return total,joint,guards,extra


def tv(a,b):
    return sum(abs(a[k]-b[k]) for k in a.keys()|b.keys())/2


def flags(r,s,x,y,gate):
    if gate=="independent_local":
        return r==x,s==y
    if gate=="terminal_only":
        return True,True
    return ((r,s)==(x,y),)*2


def make_table(law, mode="primary", gate="ordinary", masses=(1,1,1,1), weighting="prepared"):
    assert len(masses)==4 and sum(masses)>0
    contexts = {}
    for x,y in CELLS:
        binary = Counter()
        records = [{name:Counter() for name in ("selected","full_local","type_public","interior_test")}
                   for _ in BITS]
        represented_mass = {}
        for (r,s),w in zip(CELLS,masses):
            if not w:
                continue
            args = () if weighting=="prepared" else (weighting,x,y)
            total,joint,guard,extra = source(law,r,s,mode,*args)
            factor = Fraction(w,sum(masses)*total)
            represented_mass[f"{r}{s}"] = {"type_units":w,"complete_states":total}
            visible = flags(r,s,x,y,gate)
            for (a,b),n in joint.items():
                outputs = int(visible[0])*a[0],int(visible[1])*b[0]
                binary[outputs] += n*factor
                for k in BITS:
                    records[k]["selected"][outputs[k]] += n*factor
            for k,label in enumerate((r,s)):
                f = visible[k]
                for z,n in guard[k].items():
                    records[k]["full_local"][label,f,z] += n*factor
                    records[k]["type_public"][r,s,f,z] += n*factor
                for (z0,z1),n in extra[k].items():
                    records[k]["interior_test"][label,f,z0,z1] += n*factor
        assert sum(binary.values())==1
        if weighting=="prepared":
            totals = {t["complete_states"] for t in represented_mass.values()}
            assert len(totals)==1
            denominator = totals.pop()*sum(masses)
        else:
            denominator = sum(masses)*lcm(*(t["complete_states"] for t in represented_mass.values()))
        raw = [binary[ab]*denominator for ab in CELLS]
        assert all(n.denominator==1 for n in raw)
        contexts[x,y] = dict(outputs=[str(binary[ab]) for ab in CELLS],counts=list(map(int,raw)),
                              denominator=denominator,types=represented_mass,
                              correlation=sum((-1)**(a+b)*binary[a,b] for a,b in CELLS),records=records)
    E=[v["correlation"] for v in contexts.values()]
    variation={}
    for side,who in enumerate(("Alice","Bob")):
        variation[who]={}
        for name in ("selected","full_local","type_public","interior_test"):
            deltas=[]
            for own in BITS:
                c,d=((own,0),(own,1)) if side==0 else ((0,own),(1,own))
                deltas.append(str(tv(contexts[c]["records"][side][name],contexts[d]["records"][side][name])))
            variation[who][name]=deltas
    compact=[]
    for c in contexts.values():
        c.pop("records")
        c["correlation"]=str(c["correlation"])
        compact.append(c)
    return dict(contexts=compact,correlations=list(map(str,E)),signed_S=str(E[0]+E[1]+E[2]-E[3]),
                max_CHSH=str(max(sum(i*j for i,j in zip(v,E)) for v in product((-1,1),repeat=4) if v.count(-1)%2)),
                TV=variation)


def run():
    result={"settings":["00","01","10","11"],"outcomes":["00","01","10","11"],
            "guards":{"per_end":2,"local_region_complete_segments":1},
            "score_units":"Equal mass per named source type unless explicitly reweighted; integer cumulative denominators.",
            "full_local":"Exact sufficient histogram of own known type, local holder-gain status and three outside guard bits; all other recorded coordinates have an identical conditional law as proved in result.md.",
            "interior_test":"Joint of known local readiness, local gain, and the triples before and after the remote switch between the observer's two preparation switches; lower bound for full enlarged-region TV.",
            "control_semantics":{"terminal_only":"Read both terminals before growth; record flag set to constant for this comparison.",
            "independent_local":"Separate local funding controls the two detector flags.",
            "saturated":"Give both addresses two openings before the interventions; every round funds under the ordinary rule.",
            "uniform_edited_and_uniform_final":"Sensitivity on a single edited or final cut; its accessible marginals are single-cut marginals. No pre-settings trajectories are implicitly assigned."},
            "laws":{}}
    for law in ("parity","nae"):
        info={"one_piece":one_piece(law),"local_weights":{str(r):site(law,r) for r in BITS},
              "primary":make_table(law),"controls":{}}
        for mode in ("commuting","identity","reversed"):
            info["controls"][mode]=make_table(law,mode=mode)
        for gate in ("independent_local","terminal_only"):
            info["controls"][gate]=make_table(law,gate=gate)
        info["controls"]["saturated"] = make_table(law,mode="saturated",gate="terminal_only")
        info["controls"]["bob_label_one_three_quarters"]=make_table(law,masses=(1,3,1,3))
        info["controls"]["fixed_types"]={f"{r}{s}":make_table(law,masses=tuple(int(t==(r,s)) for t in CELLS)) for r,s in CELLS}
        for weighting in ("uniform_edited","uniform_final"):
            info["controls"][weighting]=make_table(law,weighting=weighting)
        info["endpoint_histograms"]={}
        for r,s in CELLS:
            total,joint,guards,extra=source(law,r,s,"primary")
            info["endpoint_histograms"][f"{r}{s}"]=dict(total=total,
                six_bit_weights=[joint[a,b] for a in WORDS for b in WORDS],
                cut_weights=[[cut[z] for z in WORDS] for cut in guards])
        result["laws"][law]=info
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,separators=(",",":"))+"\n")
    for law,d in result["laws"].items():
        r=d["primary"]
        print(law,r["correlations"],r["signed_S"],r["TV"])


if __name__=="__main__":
    run()
