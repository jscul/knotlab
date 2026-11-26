"""Read the missing parity test both on the stored stage's structure and on parity growth."""
import argparse
import json
import time
from collections import Counter
from itertools import product
import hashlib
import os
import random
import subprocess
import sys

from taking_tables import HERE, stream
from regrow_engine import Growth

LAWS = ("L0","L1","L3","L6","L7")


def restricted_dimension(masks, star, initial_rank):
    # dim {row combinations supported in star} = rank(M) - rank(M outside star).
    return initial_rank - rank(x & ~star for x in masks)


def rank(rows):
    pivots={}
    for x in rows:
        while x:
            i=x.bit_length()
            if i not in pivots:
                pivots[i]=x
                break
            x ^= pivots[i]
    return len(pivots)


def passing(g, crosscheck=False):
    # Append the outside as a holder of every loose distinction. Its parity
    # equation is the sum of the knot equations, so adds no constraint.
    outside=len(g.places)
    incidence=[set() for _ in range(outside+1)]
    for hs in g.holders.values():
        u=hs[0]
        v=hs[1] if len(hs)==2 else outside
        incidence[u].add(v)
        incidence[v].add(u)
    bad=[]
    masks=[sum(1<<d for d in star) for star in g.places]
    full_rank=rank(masks) if crosscheck else None
    for u,ns in enumerate(incidence[:-1]):
        neighbor=next(iter(ns))
        pending=[neighbor]
        visited={u,neighbor}
        for parent in pending:
            for v in incidence[parent] - visited:
                visited.add(v)
                pending.append(v)
        # Each remaining connected component imposes one even rule on
        # the places of u leading to it. One such rule gives full parity.
        ok=ns<=visited
        if crosscheck:
            assert (restricted_dimension(masks,masks[u],full_rank)==1)==ok
        if not ok:
            bad.append(u)
    return bad


def closing_arity(census,limit):
    named=json.loads((HERE.parent.with_name(HERE.parent.name+"A")/"named_starts.json").read_text())["named_starts"]
    counts=Counter()
    examples=[]
    for row in stream("run3",limit):
        end=row["parity_closing_round"]
        if end is None:
            continue
        start=row["start"]
        stars=census[int(start.split(":")[1])]["stars"] if start.startswith("census:") else named[start]
        growth=Growth(stars,row["law"],"parity")
        for _ in range(end):
            growth.step()
        n=len(growth.places)
        assert n==row["parity"]["structure_knots"]
        nstart=len(stars)
        seed=f"KWR|{start}|{row['law']}|parity|knot-test"
        rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(),"big"))
        selected=(set(range(n)) if n-nstart<=200 else
                  set(range(nstart))|set(rng.sample(range(nstart,n),200)))
        assert len(selected)==row["parity"]["tested"]
        counts["closing runs"]+=1
        counts["closing places "+str(len(growth.places[-1]))]+=1
        if len(growth.places[-1])<3:
            counts["under three places in sample"]+=int(n-1 in selected)
            examples.append({"start":start,"law":row["law"],"round":end,
                             "arity":len(growth.places[-1]),"selected":n-1 in selected})
    return {"counts":counts,"cases":examples}


def verify_first(w):
    # Project the entire even system by listing the allowed states.
    places=w["places"]
    u=w["failing knots"][0]
    sources=sorted(places[u])
    names=[f"d{d}" for d in sources]
    masks=[sum(1<<d for d in s) for s in places]
    n=max(d for s in places for d in s)+1
    states=[x for x in range(1<<n) if all((x&m).bit_count()%2==0 for m in masks)]
    projection={tuple((x>>d)&1 for d in sources) for x in states}
    clauses=[" ".join("~"+name if bit else name for name,bit in zip(names,row))
             for row in product((0,1), repeat=len(sources)) if row not in projection]
    checked=subprocess.run([sys.executable,"-B","-m","knotlab","check","--cnf","; ".join(clauses),
                            "--loops",*names[:-1],"--contact",names[-1],"--json"],cwd=HERE.parents[2],
                            env={**os.environ,"PYTHONPATH":"tools"},text=True,capture_output=True)
    w["allowed assignments"]=len(states)
    w["projected rows"]=sorted(projection)
    w["canonical check"]=json.loads(checked.stdout)
    assert not w["canonical check"]["is_knot"]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit",type=int)
    args=parser.parse_args()
    census=json.loads((HERE.parent.with_name(HERE.parent.name+"A")/"census_starts.json").read_text())
    result={}
    start=time.perf_counter()
    for law in LAWS:
        counters={reading:Counter() for reading in ("recorded structure","regrown under parity")}
        witnesses={}
        for raw in stream("run5_"+law,args.limit):
            idx=raw["index"]
            stars=census[idx]["stars"]
            stored={s["round"]:s for s in raw["stages"]}
            for reading,knot_law in (("recorded structure","nae"),("regrown under parity","parity")):
                g=Growth(stars, law=law, knot_law=knot_law)
                counts=counters[reading]
                rows_with_failure=0
                for t in range(1,5 if len(stars)<5 else 4):
                    births=g.step()
                    if not births:
                        if knot_law=="nae":
                            assert t not in stored
                        break
                    shared=sum(len(s)==2 for s in g.holders.values())
                    if knot_law=="nae":
                        s=stored[t]
                        assert (s["members"],s["shared"],s["knots"],s["distinctions"])==(
                            len(g.members),shared,len(g.places),len(g.holders))
                    if len(g.members)>30 or shared>50:
                        counts["above cap"]+=1
                        continue
                    counts["stages"]+=1
                    counts["knot at stage"]+=len(g.places)
                    do_rank=idx<223
                    bad=passing(g,crosscheck=do_rank)
                    short=[u for u,s in enumerate(g.places) if len(s)<3]
                    counts["below canonical arity"]+=len(short)
                    counts["below arity and deficient projection"]+=len(set(short)&set(bad))
                    counts["compared with independent ranks"]+=len(g.places) if do_rank else 0
                    counts["failing knot at stage"]+=len(bad)
                    counts["failing starts at stage"]+=sum(u<len(stars) for u in bad)
                    counts["stages with a failing knot"]+=bool(bad)
                    rows_with_failure+=bool(bad)
                    if bad and reading not in witnesses:
                        witnesses[reading]={"census index":idx,"start":stars,"round":t,"failing knots":bad,
                                            "places":list(g.places)}
                counts["runs with a failing knot"]+=bool(rows_with_failure)
        for w in witnesses.values():
            verify_first(w)
        result[law]={"counts":counters,"first witnesses":witnesses}
    result["run3 closings"]=closing_arity(census,args.limit)
    print("elapsed",round(time.perf_counter()-start,3))
    if args.limit is None:
        (HERE/"stage_parity.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    main()
