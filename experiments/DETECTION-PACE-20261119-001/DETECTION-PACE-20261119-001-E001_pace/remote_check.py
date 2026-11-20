"""Read the remote growing end on the current stage, with history used only for checking."""
from collections import Counter
import json
import signal
from current import DATA, cases, distances, loads, padded, stages
from current_exterior import View, compare, expire


def observe(stage, seam, count):
    live_distance = distances(stage.neighbors,stage.open)
    assert set(live_distance)==set(range(len(stage.stars)))
    assert all(live_distance[v]==stage.age for v in range(count+1))
    rows={}
    for m in range(count):
        endpoints=stage.ends[m]
        reached=distances(stage.neighbors,endpoints)
        first=min(reached[u] for u in stage.open)
        assert first==stage.age
        observed={u for u in stage.open if reached[u]==first}
        ancestor_mask=sum(1<<u for u in endpoints)
        rebuilt={u for u in stage.open if stage.ancestors[u]&ancestor_mask}
        assert observed==rebuilt
        rows[m] = dict(sorted(Counter(stage.open[u] for u in observed).items()))
    return rows


def domains(q,l,marks,count,seam):
    result=[]
    for side in ("right","left"):
        for d in range(count-seam if side=="right" else seam):
            low,high=(seam+d,count) if side=="right" else (0,seam-d)
            anchor=low if side=="right" else high-1
            mask=((1<<(high+1))-1) ^ ((1<<low)-1)
            for which in ("some","every"):
                views=[]
                for frame in (q,l):
                    members={v for v,bits in enumerate(frame.ancestors)
                             if (bool(mask&bits) if which=="some" else (bits&~mask)==0)}
                    views.append(View(frame,members,{anchor},False,open_cuts=True))
                result.append([q.age,side,d,which,views[0].size,views[1].size,compare(*views)])
    return result


def run(spec,through,check_regions):
    count=len(spec["roles"]["anchors"])
    seam,=spec["roles"]["seams"]
    codes={}
    bank=[stages(spec,state,through,codes) for state in loads(spec).values()]
    result={"seam":seam,"marks":count,"frames":[],"regions":[]}
    for q,l in zip(*bank):
        qr=observe(q,seam,count)
        lr=observe(l,seam,count)
        marks=[]
        for m in range(count):
            d=(m-seam if m>=seam else seam-m-1)
            marks.append([m,d,qr[m],lr[m]])
        result["frames"].append({"age":q.age,"sizes":[[len(g.stars),len(g.ends)] for g in (q,l)],"probes":marks})
        if check_regions and q.age<=4:
            result["regions"].extend(domains(q,l,marks,count,seam))
    return result


def main():
    signal.signal(signal.SIGALRM,expire)
    sources={tag:cases()[tag] for tag in ("J1","P8","P16")}
    sources["long"]=padded("long",128,[16])
    data={"measure":"loose-degree histograms on nearest knots that have a loose distinction, from both actual holders of an old mark. Physical tails keep cut ports, without outside degrees.",
          "cases":{tag:run(source,8,tag in ("J1","P8")) for tag,source in sources.items()}}
    (DATA/"remote_check.json").write_text(json.dumps(data,separators=(",",":"))+"\n")
    print({tag:(len(v["frames"]),len(v["regions"])) for tag,v in data["cases"].items()})


if __name__=="__main__":
    main()
