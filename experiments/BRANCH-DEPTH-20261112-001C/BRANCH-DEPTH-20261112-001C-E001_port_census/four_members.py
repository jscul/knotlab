"""For residuals, try the target's parent and combine independently periodic witnesses."""
from collections import Counter
from math import lcm
import gzip
import json

from census import OUT, SOURCE, allowed_local_words
from endpoints import orbit


def value(info, n):
    seq=info["certificates"]
    return seq[n] if n<len(seq) else seq[info["start"]+(n-info["start"])%info["period"]]


def outcome(infos):
    # A parent-window certificate at depth n corresponds to target depth n+1.
    start=max(1,max(info["start"]+offset for info,offset in infos))
    period=lcm(*(info["period"] for info,_ in infos))
    valid=lambda s:any(value(info,s-offset) for info,offset in infos)
    pre=all(valid(s) for s in range(1,start))
    cyc=[bool(valid(s)) for s in range(start,start+period)]
    if all(cyc):
        return "every_positive_depth" if pre else "eventually_every_depth"
    return "some_periodic_depths" if any(cyc) else "no_eventual_certificate"


def main():
    path=lambda n: OUT/n
    tables=json.loads(path("port_tables.json").read_text())
    triples={(r["file"],r["line"]):r for r in json.loads(path("endpoint_tables.json").read_text())["rows"]}
    data=[]
    for filename in tables["source_files"]:
        included={r["line"]:r for r in tables["rows"] if r["file"]==filename and
                  r["rectangular"] is None and triples[filename,r["line"]]["classification"]!="every_positive_depth"}
        for line,text in enumerate(gzip.open(SOURCE/filename,"rt"),1):
            if line not in included:
                continue
            definition=json.loads(text)["defs"][0]
            tab=included[line]
            allowed, words, _,_=allowed_local_words(definition)
            parent=orbit(definition,allowed,words,tab["transition"],branches=((0,),),sizes=(4,),target_index=1)
            info=[(triples[filename,line],0),(parent,1)]
            target_quads=None
            if outcome(info)!="every_positive_depth":
                children=[()]+[(i,) for i in range(tab["children"])]
                target_quads=orbit(definition,allowed,words,tab["transition"],branches=children,sizes=(4,))
                info.append((target_quads,0))
            data.append(dict(file=filename,line=line,parent=parent,target=target_quads,classification=outcome(info)))
    totals=dict(Counter(r["classification"] for r in data))
    path("four_members.json").write_text(json.dumps(dict(totals=totals,rows=data),separators=(",",":"))+"\n")
    print(json.dumps(totals,indent=2))


if __name__ == "__main__":
    main()
