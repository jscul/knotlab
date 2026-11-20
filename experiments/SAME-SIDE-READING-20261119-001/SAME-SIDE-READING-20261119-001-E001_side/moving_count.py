"""Independently read the fixed old marks without using ancestry to find their ball."""
from collections import Counter, defaultdict, deque
from itertools import accumulate
import json
from pathlib import Path
from random import Random

from side_sources import AGES, CAPS, cases, generate, growth, loads, padded

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def adjacency(stars):
    holders = defaultdict(list)
    for v, support in enumerate(stars):
        for mark in support:
            holders[mark].append(v)
    neighbors = [set() for _ in stars]
    for ends in holders.values():
        if len(ends) == 2:
            u, v = ends
            neighbors[u].add(v)
            neighbors[v].add(u)
    return holders, neighbors


def shells(starts, neighbors, limit):
    distances = dict.fromkeys(starts, 0)
    todo = deque(distances)
    while todo:
        v = todo.popleft()
        depth = distances[v]
        if depth == limit:
            continue
        for u in neighbors[v]:
            if u not in distances:
                distances[u] = depth+1
                todo.append(u)
    return distances


def read(frame, marks, k, ancestry, ages, allowed, mappings):
    holders, neighbors = mappings
    endpoints = {v for mark in marks for v in holders[mark]}
    assert all(len(holders[m]) == 2 for m in marks)
    # An old shared mark has only its original holders. A knot at holder
    # distance j from these holders is precisely 2j+1 physical hops away.
    dist = shells(endpoints, neighbors, k+1)
    shell = Counter(dist.values())
    pure = Counter(ages[v] for v in dist if ancestry[v] & ~allowed)
    return {"knots":len(dist),"by_radius_odd":list(accumulate(shell[j] for j in range(k+2))),
            "with_ancestry_outside_side":sum(pure.values()),"outside_by_age":dict(sorted(pure.items())),
            "by_birth_layer":dict(sorted(Counter(ages[v] for v in dist).items()))}


def measure(spec, end_at):
    seam, = spec["roles"]["seams"]
    count = len(spec["roles"]["anchors"])
    queries = []
    for k in range(2,9):
        for m in (2,3,4):
            for direction in (1,-1):
                ms = tuple(sorted(seam+2*k+u if direction==1 else seam-1-2*k-u for u in range(m)))
                if ms[0] < 0 or ms[-1] >= count:
                    continue
                margin = count-1-ms[-1] if direction==1 else ms[0]
                allowed = sum(1<<i for i in range(count+1) if direction*(i-seam)>0)
                queries.append((k,m,direction,ms,margin,allowed))
    index={}; stages={}
    for arm,state in loads(spec).items():
        ancestry=[]; ages=[]
        rows = index[arm] = {}
        stages[arm]={}
        gen = generate(spec,state,max_age=end_at,caps=CAPS)
        while True:
            try:
                age, frame = next(gen)
            except StopIteration as ex:
                stages[arm]["stop"]=ex.value
                break
            if not age:
                ancestry[:] = [1<<v for v in range(len(spec["sizes"]))]
                ages[:] = [0]*len(ancestry)
            else:
                for v in frame["born"]:
                    assert v == len(ancestry)
                    origins=0
                    for parent in frame["parent_sets"][v]:
                        origins |= ancestry[parent]
                    ancestry.append(origins)
                    ages.append(age)
            mapping=adjacency(frame["stars"])
            stages[arm][age]=[len(frame["stars"]),len(mapping[0])]
            for k,m,d,ms,margin,allowed in queries:
                if age > k+2:
                    continue
                rows.setdefault((k,m,d),{})[age]=read(frame,ms,k,ancestry,ages,allowed,mapping)
    comparisons=[]
    for k,m,d,ms,margin,allowed in queries:
        arms=[index[a][k,m,d] for a in ("0","1")]
        pair={}
        for age in sorted(arms[0].keys() & arms[1].keys()):
            q,l = [arm[age] for arm in arms]
            pair[age]={"quiet":q,"loaded":l,"delta":l["knots"]-q["knots"],
                       "delta_by_radius_odd":[y-x for x,y in zip(q["by_radius_odd"],l["by_radius_odd"],strict=True)]}
        comparisons.append({"k":k,"marks":ms,"side":d,"margin":margin,"generous":margin>=2*(k+2),
                            "offset":2*k,"radius":2*k+3,"old_ring_hops":4*k+1,
                            "prediction_age":k+1,"comparisons":pair})
    return {"stages":stages,"comparisons":comparisons}


def rename_check():
    spec=cases()["P4"]
    original=growth.predecessor().source_stars(spec)
    seed=Random(275989)
    order=list(range(len(original)));seed.shuffle(order)
    names=sorted({b for row in original for b in row});perm=names.copy();seed.shuffle(perm)
    recoding=dict(zip(names,perm,strict=True))
    mapped={b:i for i,b in enumerate(order)}
    new=[[recoding[b] for b in original[i]] for i in order]
    marks=[12,13,14]
    results={}
    for arm,state in loads(spec).items():
        checks=[]
        for trace,mark,ring in ((growth.grow(original,state,("P","V"),rounds=3,caps=CAPS),marks,8),
                                (growth.grow(new,{recoding[b] for b in state},("P","V"),rounds=3,caps=CAPS),
                                 [recoding[b] for b in marks],mapped[8])):
            hh,nn=adjacency(trace["stages"]["3"]["stars"])
            counts=shells({k for b in mark for k in hh[b]},nn,5)
            checks.append((sum(x<=3 for x in counts.values()),1+2*counts[ring]))
        assert checks[0]==checks[1]
        results[arm]=checks
    return results


def main():
    all_cases=dict(cases())
    all_cases["W"]=padded("W",64,[32])
    record={"unit":"ordinary incidence hops; one physical knot per union","cases":{},
            "renaming_old_holders_and_distinctions":rename_check()}
    for name in ("J1","P4","P8","P16","W"):
        rec=measure(all_cases[name],min(10,AGES.get(name,10)))
        record["cases"][name]=rec
        got=[(r["k"], r["comparisons"][r["prediction_age"]]["delta"]) for r in rec["comparisons"]
             if r["generous"] and r["prediction_age"] in r["comparisons"]]
        print(name,len(rec["comparisons"]),dict(Counter(got)),flush=True)
    (DATA/"moving_count.json").write_text(json.dumps(record,separators=(",",":"))+"\n")


if __name__ == "__main__":
    main()

