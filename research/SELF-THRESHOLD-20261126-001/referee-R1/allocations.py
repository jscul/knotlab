"""Find the first departure from the cap anywhere in each preparation, including silent additions.

On a common history the fresh count is the only changing rule. Therefore a
different prescription witnesses departure, and the absence of one through
the entire history proves equality there by induction over rounds.
"""
import argparse
from collections import Counter
import json
from time import process_time

from archive import panel, hearings, normalized
from growth import Growth, first_hearing
from starts import build_pair


def first_split(turns, start, other):
    for i,row in enumerate(turns[start:],start+1):
        split = Counter()
        for b in row.births:
            if other == "HALF":
                if b.D < 5:
                    continue
                alt = (b.D+1)//2+1
            else:
                alt = max(3-b.p,1,min(b.p+1,b.D))
            if alt != b.f:
                split[b.kind,b.p,b.D,b.f,alt] += 1
        if split:
            return {"round":i, "types":[[*k,n] for k,n in sorted(split.items())]}
    return None


def scan(name, limit):
    begin = process_time()
    pairs = panel(name)
    result = []
    for pair, laws in list(sorted(pairs.items()))[:limit]:
        r = laws["CAP-3"]
        positive = bool(hearings(r))
        eq = normalized(r)==normalized(laws["HALF"])
        rounds,bound = (24,6000) if name == "linked" else (12,1500)
        g = Growth(*build_pair(*pair), law="CAP-3").run(rounds,bound)
        base = first_split(g.rounds,0,"HALF")
        any_split = base is not None
        out = {"pair":pair,"equal_summary":eq,"baseline":base,"additions_checked":0,
               "first_changed_split":None,"hearings":[]}
        t0s = [3,5,8] if name=="linked" else [1,2,3]
        index = 0
        for t in t0s:
            if t>=len(g.rounds) or g.linked(t) is None:
                continue
            for linked, cap in ((True,5),(False,2)):
                for m in g.mark_candidates(t,linked)[:cap]:
                    saved=r["changes"][index]
                    index += 1
                    assert (t,linked,m.sharings)==(saved["t0"],saved["linked"],saved["sharings"])
                    if any_split and not positive:
                        continue
                    h = g.fork(t)
                    h.mark(m.knot)
                    h.run(rounds,bound)
                    hit = first_hearing(g,h,t)
                    assert hit==saved["heard"] and min(len(g.rounds),len(h.rounds))==saved["rounds"]
                    out["additions_checked"] += 1
                    split = first_split(h.rounds,t,"HALF")
                    if split:
                        any_split = True
                        if out["first_changed_split"] is None:
                            out["first_changed_split"] = {"after":t,"marked":m.knot,"heard":hit,**split}
                    if hit is not None:
                        out["hearings"].append({"after":t,"marked":m.knot,"heard":hit,
                            "births_in_changed_growth":sum(len(row.births) for row in h.rounds),
                            "half_split_on_changed_history":first_split(h.rounds,0,"HALF"),
                            "places_split_through_hearing":first_split(h.rounds[:hit],0,"PLACES")})
        assert index == len(r["changes"])
        out["any_half_split"]=any_split
        result.append(out)
    return {"panel":name,"rows":result,"cpu_seconds":round(process_time()-begin,3)}


def later_growth(limit):
    begin = process_time()
    result = []
    for pair, laws in sorted(panel("linked").items()):
        cut = [c for c in laws["HALF"]["changes"] if c["heard"] and c["rounds"] == c["heard"]]
        if not cut:
            continue
        g = Growth(*build_pair(*pair), law="HALF").run(24, 6000)
        for c in cut:
            t = c["t0"]
            # Resolve by the stored within-round candidate order, including ties in sharings.
            peers = [v for v in laws["HALF"]["changes"] if v["t0"] == t and v["linked"] == c["linked"]]
            m = g.mark_candidates(t,c["linked"])[peers.index(c)]
            h = g.fork(t).mark(m.knot).run(24,6000)
            assert first_hearing(g,h,t) == len(h.rounds) == c["heard"] == 23
            extended = h.fork(23).run(24,6000)
            result.append({"pair":pair, "after":t, "marked":m.knot,"hearing":c["heard"],
                           "next_births":[len(v.rounds[23].births) for v in (g,extended)]})
            if len(result) == limit:
                return {"rows":result,"cpu_seconds":round(process_time()-begin,3)}
    return {"rows":result,"cpu_seconds":round(process_time()-begin,3)}


if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("panel",choices=["linked","census","later"])
    arg.add_argument("limit",type=int)
    opts=arg.parse_args()
    print(json.dumps(later_growth(opts.limit) if opts.panel=="later" else scan(opts.panel, opts.limit)))
