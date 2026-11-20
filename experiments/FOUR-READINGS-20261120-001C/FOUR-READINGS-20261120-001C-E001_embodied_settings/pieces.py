"""Construct all frozen two-reader assemblies; multiply their exact extension counts."""
from fractions import Fraction
from itertools import combinations, permutations, product
from collections import defaultdict
import gzip
import json
import sys
from observables import OUTPUT, PRIOR, WORDS, freeze, measure, put, prior_score_check
sys.path.insert(0,str(PRIOR))
import run as prior

NAMES = ("chain2","chain3","four")
BITS = (0,1)


def local_allowed(values,law):
    return sum(values)%2==0 if law=="parity" else bool(sum(values)) and sum(values)<len(values)


def piece(name,x,y,next_distinction):
    if name=="four":
        rows=[[x],[y],[],[]]
        for i,j in combinations(range(4),2):
            if (i,j)!=(0,1):
                shared=next(next_distinction)
                rows[i].append(shared)
                rows[j].append(shared)
        return rows
    size=int(name[-1])
    turns = [x] + [next(next_distinction) for _ in range(size-1)] + [y]
    return [[turns[i], turns[i+1], next(next_distinction)] for i in range(size)]


def signature(name,law):
    rows=piece(name,0,1,iter(range(2,20)))
    n=1+max(max(s) for s in rows)
    return [[sum(all(local_allowed([w[i] for i in row],law) for row in rows)
                 for other in product(BITS,repeat=n-2) for w in [(x,y)+other]) for y in BITS] for x in BITS]

def patterns():
    for k in range(4):
        for ls in combinations(range(3),k):
            for rs in permutations(range(3),k):
                for kinds in product(NAMES, repeat=k):
                    yield tuple(zip(ls,rs,kinds))


def assemble(extra,pattern):
    new=iter(range(6,100))
    rows=[list(range(3))+[next(new) for _ in range(extra[0])],
          list(range(3,6))+[next(new) for _ in range(extra[1])]]
    for x,y,kind in pattern:
        rows.extend(piece(kind,x,y+3,new))
    return tuple(tuple(sorted(row)) for row in rows)


def counts(extra,pattern,law,signatures):
    def local_factor(triple,unit):
        return sum(local_allowed(triple+spares,law) for spares in product(BITS,repeat=unit))
    raw=[]
    for w in WORDS:
        n=local_factor(w[:3],extra[0])*local_factor(w[3:],extra[1])
        for a,b,kind in pattern:
            n*=signatures[law][kind][w[a]][w[3+b]]
        raw.append(n)
    return raw


def update_peak(peaks,label,val,index):
    if label not in peaks or Fraction(val)>Fraction(peaks[label]["score"]):
        peaks[label]={"score":val,"first_index":index,"ties":1}
    elif Fraction(val)==Fraction(peaks[label]["score"]):
        peaks[label]["ties"]+=1


def main():
    freeze()
    signatures={law:{kind:signature(kind,law) for kind in NAMES+("chain1",)} for law in ("nae","parity")}
    details, summaries = [], {}
    for law in ("nae","parity"):
        summary={"tested":0,"lawful":0,"unlawful":0,"fully_populated":0,"full_hidden":0,"I_over_2_with_hidden":0,
                 "II_over_2_with_hidden":0,"I_over_2_any":0,"II_over_2_any":0,"peaks":{}}
        summaries[law]=summary
        for extra in product(range(3),repeat=2):
            for pattern in patterns():
                supports=assemble(extra,pattern)
                certificate=prior.certify(supports,law)
                raw=counts(extra,pattern,law,signatures)
                summary["tested"]+=1
                index=len(details)
                row={"law":law,"extra":extra,"pieces":pattern,"raw":raw,
                     "lawful":all(gate["eligible"] for gate in certificate)}
                details.append(row)
                if not row["lawful"]:
                    summary["unlawful"]+=1
                    continue
                summary["lawful"]+=1
                e=measure(raw)
                f=measure(raw,False)
                for read in ("I","II"):
                    ext=f[read]["maximum"]
                    assert Fraction(ext)<=2
                    row[read]={"embodied":None,"external":ext}
                    update_peak(summary["peaks"],"external_"+read,ext,index)
                if e["full_hidden"] is None: continue
                summary["fully_populated"]+=1
                summary["full_hidden"]+=int(e["full_hidden"])
                row.update({"hidden":e["full_hidden"],"tv":e["full_pair_tv"],"masses":e["masses"]})
                for read in ("I","II"):
                    score=e[read]["maximum"]
                    ext=f[read]["maximum"]
                    assert Fraction(ext)<=2
                    if law=="nae":
                        assert raw==raw[::-1] and Fraction(score) <= (4 if read=="I" else 2)
                        if read=="I": assert Fraction(score)<4
                    update_peak(summary["peaks"],"all_"+read,score,index)
                    if e["full_hidden"]:
                        update_peak(summary["peaks"],"hidden_"+read,score,index)
                    summary[read+"_over_2_any"]+=int(Fraction(score)>2)
                    summary[read+"_over_2_with_hidden"]+=int(e["full_hidden"] and Fraction(score)>2)
                    row[read]={"embodied":score,"external":ext}
        assert summary["tested"]==9*352
    # Independently contract actual displayed supports for every reported maximum.
    checked=set()
    for law,summ in summaries.items():
        for peak in summ["peaks"].values():
            i=peak["first_index"]
            if i in checked: continue
            checked.add(i)
            row=details[i]
            supports=assemble(row["extra"],row["pieces"])
            actual=prior.CountStage(supports,supports,law).histogram(tuple(range(6)),"U")[0]
            assert actual==row["raw"]
            assert prior_score_check(actual,{"embodied":measure(actual),"external":measure(actual,False)})
    # One direct ternary contains both marked terminals, and fails separation by definition.
    direct=assemble((1,1),((0,0,"chain1"),))
    from readings import shortest_steps,step_neighborhoods
    assert shortest_steps((0,1,2),(3,4,5),step_neighborhoods(direct)[0])==1
    put("piece_summary.json",{"transfer":signatures,"laws":summaries,"checked_maximum_examples":sorted(checked),
                              "direct_control_cross_steps":1})
    (OUTPUT/"piece_tables.json.gz").write_bytes(gzip.compress(json.dumps(details,separators=(",",":")).encode(),mtime=0))
    for law,obj in summaries.items():
        print(law,obj["tested"],obj["lawful"],obj["full_hidden"],obj["peaks"])
if __name__=="__main__":
    main()
