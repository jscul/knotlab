"""On the six positive census additions, change one part of the cap and match the marked descent."""
import argparse
import json
from time import process_time

from archive import HERE
from growth import Growth, first_hearing
from starts import build_pair


def cap_with(which):
    def fresh(kind, p, d, o):
        ordinary = max(1,3-p,d)
        if which == "offshoot" and kind == "offshoot":
            return max(3-p,1,min(p+1,ordinary))
        if which == "join" and (kind,p,d) == ("join",3,4):
            return 4
        return min(ordinary,3)
    return fresh


def run(limit):
    hits = [row for row in json.loads((HERE/"allocation_census.json").read_text())["rows"] if row["hearings"]]
    result = []
    begin = process_time()
    for rec in hits[:limit]:
        roots = build_pair(*rec["pair"])
        cap = Growth(*roots,law="CAP-3").run(12,1500)
        for key,law in [("cap","CAP-3"), ("offshoot",cap_with("offshoot")), ("join",cap_with("join")),
                        ("places","PLACES")]:
            g = Growth(*roots, law=law).run(12,1500)
            for hit in rec["hearings"]:
                t = hit["after"]
                source = next(m for m in cap.mark_candidates(t,True) if m.knot == hit["marked"])
                matches = [m for linked in (True,False) for m in g.mark_candidates(t,linked) if m.descent==source.descent]
                assert len(matches)==1
                m = matches[0]
                h = g.fork(t)
                h.mark(m.knot)
                h.run(12,1500)
                result.append({"pair":rec["pair"], "after":t,"law":key, "descent":m.descent,"marked":m.knot,
                               "sharings":m.sharings, "heard":first_hearing(g,h,t),
                               "end":min(len(g.rounds),len(h.rounds))})
    return {"controls":result, "cpu_seconds":round(process_time()-begin,3)}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("pairs", type=int)
    args=parser.parse_args()
    print(json.dumps(run(args.pairs)))
