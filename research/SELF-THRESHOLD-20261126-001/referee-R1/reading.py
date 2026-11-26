"""Repeat two already published far additions under laws that fully specify the disputed allocation."""
import argparse
from collections import Counter
import json
from time import process_time

from growth import Growth, first_hearing
from starts import build_pair


def funding(which):
    if which == "minimum":
        return lambda kind,p,d,o: max(1, 3-p)
    if which == "any-join-four":
        return lambda kind,p,d,o: 3 if kind == "join" and d == 4 else max(1,3-p,d)
    if which == "only-four":
        return lambda kind,p,d,o: 3 if kind == "join" and d == 4 and p == 3 else max(1, 3-p, d)
    if which in ("fund-five", "give-five-three"):
        def change_five(kind, p, d, o):
            if kind == "join" and d == 5:
                return 5 if which == "fund-five" else 3
            return min(4, max(1, 3-p, d))
        return change_five
    if which == "restore-given-three":
        return lambda kind,p,d,o: 4 if (kind,p,d)==("join",3,4) else min(3,max(1,3-p,d))
    return which


def count(turns):
    totals = Counter()
    first_high = None
    for i, row in enumerate(turns, 1):
        for b in row.births:
            totals["births"] += 1
            if b.kind == "join" and b.D == 4:
                totals[f"join_owed_four_given_{b.f}"] += 1
            if b.D >= 5:
                totals["owed_at_least_five"] += 1
                if first_high is None:
                    first_high = {"round":i,"birth":b.knot,"kind":b.kind,"p":b.p,"D":b.D,"f":b.f}
    return {"counts":dict(totals),"first_high":first_high}


def run(test, law, number):
    t = process_time()
    if test == "cap-four":
        pair = ("tri:222@0", "n4:g13:2331@3")
        rounds, bound = 14, 6000
    elif test == "minimum":
        pair = ("n4:g15:2123@0", "g1:3@0")
        rounds, bound = 12, 1500
    else:
        pair = ("tri:122@0", "n4:g13:2331@3")
        rounds, bound = 14, 6000
    g = Growth(*build_pair(*pair), law=funding(law)).run(rounds, bound)
    options = g.mark_candidates(3,True)
    result = []
    for m in options[:number]:
        h = g.fork(3)
        h.mark(m.knot)
        h.run(rounds, bound)
        hit = first_hearing(g,h,3)
        end = min(len(g.rounds),len(h.rounds))
        prefix = hit-1 if hit is not None else end
        out = {"mark":m.knot,"descent":str(m.descent),"sharings":m.sharings,
               "heard":hit,"end":end, "baseline_before":count(g.rounds[:prefix]),
               "changed_before":count(h.rounds[:prefix]),
               "through_common_end":[count(v.rounds[:end]) for v in (g,h)]}
        if hit is not None:
            out["own_counts"] = [len(v.rounds[hit-1].receiver_signature) for v in (g,h)]
            out["next_births"] = [len(v.rounds[hit].births) if hit<len(v.rounds) else None for v in (g,h)]
        result.append(out)
    return {"test":test,"pair":pair,"law":law,"round_limit":rounds,"knot_limit":bound,
            "eligible_linked":len(options),"marks":result,"cpu_seconds":round(process_time()-t,3)}


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("test",choices=["cap-four","minimum","cap-three"])
    arg.add_argument("law")
    arg.add_argument("number",type=int)
    opts = arg.parse_args()
    print(json.dumps(run(opts.test,opts.law,opts.number)))
