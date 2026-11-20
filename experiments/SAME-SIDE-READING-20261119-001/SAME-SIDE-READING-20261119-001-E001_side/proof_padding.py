"""Check the ordinary range theorem on a path satisfying its explicit sufficient padding."""
from pathlib import Path
import json

from moving_count import adjacency, shells
from side_sources import CAPS, generate, loads, padded

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[2]/"artifacts"/HERE.parent.name/HERE.name


def main():
    seam=12
    size=128
    source=padded("long-proof",size,[seam])
    arms={}
    for arm,state in loads(source).items():
        out={}; arms[arm]=out
        gen=generate(source,state,max_age=9,caps=CAPS)
        while True:
            try:
                age,stage=next(gen)
            except StopIteration as ex:
                out["stop"]=ex.value
                break
            if age<3:
                continue
            k=age-1
            assert size>=seam+10*k+24
            hh,nn=adjacency(stage["stars"])
            obs=[]
            for m in (2,3,4):
                marks=list(range(seam+2*k,seam+2*k+m))
                dist=shells({v for b in marks for v in hh[b]},nn,k+1)
                counts=[sum(d<=j for d in dist.values()) for j in range(k+2)]
                expected=(k+2)*(m+2*k+3)+(6 if arm=="0" else 4)
                assert counts[-1]==expected
                obs.append({"marks":marks,"knots_by_odd_radius":counts})
            out[str(k)]={"age":age,"absolute_counts":obs,"size":[len(nn),len(hh)]}
    complete=sorted(set(arms["0"]) & set(arms["1"])-{"stop"})
    for k in complete:
        for quiet,loaded in zip(arms["0"][k]["absolute_counts"],arms["1"][k]["absolute_counts"],strict=True):
            q=quiet["knots_by_odd_radius"];l=loaded["knots_by_odd_radius"]
            assert q[:-1]==l[:-1] and q[-1]-l[-1]==2
    record={"original_path_marks":size,"seam":seam,"minimum_right_reach":"10k+24",
            "arms":arms,"matched_k":list(map(int,complete))}
    (DATA/"proof_padding.json").write_text(json.dumps(record,separators=(",",":"))+"\n")
    print(complete,{a:b["stop"]["status"] for a,b in arms.items()})


if __name__=="__main__":
    main()
