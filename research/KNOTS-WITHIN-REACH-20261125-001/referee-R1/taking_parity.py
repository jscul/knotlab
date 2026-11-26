"""Recheck final parity projections and arities with the earlier shared growth engine."""
import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

from taking_tables import HERE, stream
from stage_parity import rank

ROOT=HERE.parents[2]
TICKET=ROOT/"research"/(HERE.parent.name+"A")
GROWTH=next((ROOT/"experiments").glob("PARTS-MEET-AGAIN-20261124-001A/*/pm.py"))
sys.path.insert(0,str(GROWTH.parent))
import pm


def generator(*keys):
    code="|".join(("KWR",*keys))
    return random.Random(int.from_bytes(hashlib.sha256(code.encode()).digest(),"big"))


def signatures(places):
    # Express each column's value on all solutions in terms of the free bits.
    rows={}
    for star in places:
        x=sum(1<<d for d in star)
        while x:
            i=x.bit_length()-1
            if i not in rows:
                rows[i]=x^(1<<i)
                break
            x^=rows[i]|(1<<i)
    sig=[]
    for i in range(1+max(max(s) for s in places)):
        if i not in rows:
            sig.append(1<<i)
            continue
        rest,mask=rows[i],0
        while rest:
            b=rest & -rest
            mask ^=sig[b.bit_length()-1]
            rest-=b
        sig.append(mask)
    return sig


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args()
    census=json.loads((TICKET/"census_starts.json").read_text())
    named=json.loads((TICKET/"named_starts.json").read_text())["named_starts"]
    totals=Counter()
    examples=[]
    start=time.perf_counter()
    pm.GUARD.update({k:10*v for k,v in pm.GUARD.items()})
    for row in stream("run4",None):
        if row["knot_law"]!="parity":
            continue
        if args.pilot and row["start"] not in ("Ring(5,3)","census:5","census:60"):
            continue
        law=row["law"]
        num=int(law[1:])
        base="CAP-3" if num in (1,2,3,4,9) else "FLOOR1"
        take="CARRY" if num>=9 else ("Q","MET","STEPS-1","STEPS-2")[(num-1)%4]
        law_obj=pm.Law(ration=base,knot_law="parity",take=take)
        label=row["start"]
        stars=census[int(label.split(":")[1])]["stars"] if label.startswith("census:") else named[label]
        state=pm.from_stars(stars)
        rng=generator(label,law,"parity",row["seed"])
        ctx={"chooser":lambda _,candidates: rng.choice(candidates)} if num<=8 else {}
        for k in range(row["rounds_done"]):
            pm.round_step(state,law_obj,ctx)
            assert len(state.places)==row["knots_per_round"][k+1]
        n=len(state.places)
        early=row["knots_per_round"][min(row["rounds_done"],25)]
        sample=list(range(early,n))
        if len(sample)>100:
            sample=generator(label,law,"parity","later-knots").sample(sample,100)
        chosen=list(range(early))+sample
        sig=signatures(state.places)
        failed,short=set(),set()
        for u in chosen:
            star=state.places[u]
            if rank(sig[d] for d in star)!=len(star)-1:
                failed.add(u)
            if len(star)<3:
                short.add(u)
        assert failed=={f["knot"] for f in row["knot_test"]["fails"]}
        assert len(chosen)==row["knot_test"]["tested"]
        totals.update({"runs":1,"tested":len(chosen),"deficient projection":len(failed),
                       "below arity":len(short),"below arity only":len(short-failed),
                       "below arity and deficient projection":len(short&failed),"fails or below arity":len(short|failed)})
        if short-failed and len(examples)<6:
            u=min(short-failed)
            examples.append([label,law,row["seed"],u,state.places[u],state.made[u]])
    print("seconds",round(time.perf_counter()-start,3),dict(totals))
    if not args.pilot:
        (HERE/"taking_parity.json").write_text(json.dumps({"shared growth file":str(GROWTH.relative_to(ROOT)),
            "shared growth sha256":hashlib.sha256(GROWTH.read_bytes()).hexdigest(),"counts":totals,
            "examples below arity only":examples},indent=2)+"\n")


if __name__=="__main__":
    main()
