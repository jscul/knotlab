"""Four-arm and fixed-amount evaluations of the old-mark, below-attachment reading."""
from collections import Counter, defaultdict
from pathlib import Path
import json

from moving_count import adjacency, shells
from side_sources import CAPS, cases, generate, loads, padded

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def observers(spec):
    seams = spec["roles"]["seams"]
    n = len(spec["roles"]["anchors"])
    for donor, seam, direction in ((0,seams[0],-1),(len(seams)-1,seams[-1],1)):
        for k in range(2,5):
            for m in (2,3,4):
                ms = sorted(seam+2*k+u if direction==1 else seam-1-2*k-u for u in range(m))
                if 0 <= ms[0] and ms[-1] < n:
                    yield donor, k, ms


def readings(spec, state):
    obs=list(observers(spec))
    out = {}
    for age,frame in generate(spec,state,max_age=max(k+1 for _,k,_ in obs), caps=CAPS):
        mapping,nb=adjacency(frame["stars"])
        for donor,k,ms in obs:
            if age==k+1:
                roots = {h for m in ms for h in mapping[m]}
                size = len(shells(roots,nb,k+1))
                out[(donor,k,tuple(ms))]=size
    return out


def dose(spec):
    masks = {}
    phys = []
    ring = spec["roles"]["rings"][0]
    for arm,state in loads(spec).items():
        hot = tuple(sorted({v for m in state for v in spec["meetings"][m]}))
        if hot not in masks:
            masks[hot] = readings(spec,state)
        phys.append((arm,state,hot))
    rows=[]
    for donor,k,marks in sorted(masks[()]):
        key=(donor,k,marks)
        quiet=masks[()][key]
        by_weight=defaultdict(Counter)
        by_hot=defaultdict(Counter)
        for arm,state,hot in phys:
            if key in masks[hot]:
                delta=masks[hot][key]-quiet
                by_weight[len(state)][delta]+=1
                by_hot["".join("1" if r in hot else "0" for r in ring)][delta]+=1
        rows.append({"donor":donor,"k":k,"marks":marks,"quiet":quiet,"radius":2*k+3,
                     "by_weight":by_weight,"by_hot":by_hot})
    return rows


def factorial(spec):
    arms=[readings(spec,st) for st in loads(spec).values()]
    shared=set.intersection(*(set(row) for row in arms))
    return [{"donor":key[0],"k":key[1],"marks":key[2],"radius":2*key[1]+3,
             "four_counts":[a[key] for a in arms],"interaction":arms[3][key]-arms[2][key]-arms[1][key]+arms[0][key]}
            for key in sorted(shared)]


def main():
    named=cases()
    counts={tag:dose(named[tag]) for tag in ("J1x2","PX4")}
    doubles=dict((tag,named[tag]) for tag in ("T4","PT4","PT8"))
    # T8 has no pair at these offsets on either outer portion; no query exists.
    for gap in (4,8):
        tag=f"W{gap}"
        doubles[tag]=padded(tag,64,[32-gap,32])
    multi={tag:factorial(spec) for tag,spec in doubles.items()}
    result={"unit":"physical old pairs/triples/quads. Each legal load occurs once",
            "dose":counts,"two_rings":multi}
    (DATA/"moving_loads.json").write_text(json.dumps(result,separators=(",",":"))+"\n")
    for tag,rows in counts.items():
        r=next(row for row in rows if row["k"]==2 and len(row["marks"])==2)
        print(tag,"one per physical assignment at k=2:",r["by_weight"])
    for tag,rows in multi.items():
        print(tag,len(rows),"four-arm interactions",dict(Counter(r["interaction"] for r in rows)))


if __name__=="__main__":
    main()

