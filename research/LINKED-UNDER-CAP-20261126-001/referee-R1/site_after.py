"""Place a second addition at the original far site just after a recorded first hearing."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from time import perf_counter

from growth import RECEIVER, build_pair, far_members, first_own_difference, grow, perturb, roster

HERE = Path(__file__).resolve().parent


def read(r):
    t = r["changes"][0]["heard"]
    pair = build_pair(r["A"],r["B"])
    cap = int(r["law"][-1])
    # Keep the first hearing and read one more complete round, even for cases
    # where the changed growth first crossed its old knot bound at the hearing.
    w = grow(pair,cap,rounds=t+1,bound=65000)
    u, _ = far_members(w.states[3],True)[0]
    h = perturb(w,3,u)
    first, _ = first_own_difference(w,h,3)
    assert first == t and u == r["changes"][0]["knot"]
    v = pair.far_site
    both = perturb(h,t,v)
    edited = both.edits[t]
    classes = roster(edited).class_of
    owns = {classes[k] for k in edited.members if edited.knots[k].roles==RECEIVER}
    h2,end = first_own_difference(h,both,t)
    return dict(cap=cap,receiver=r["A"],far=r["B"],first_knot=u,second_round=t,far_site=v,
                second_usable_before=len(h.states[t].usable(v)),site_in_receiver_class_after=classes[v] in owns,
                common_round=end,second_hearing=h2)


def run(pilot):
    rows=[]
    for name in ("caps36","receivers"):
        with gzip.open(HERE.parent/f"again_linked_runs_{name}.jsonl.gz","rt") as f:
            rows.extend(r for r in map(json.loads,f) if r["changes"][0]["heard"] is not None)
    if pilot:
        cases={}
        for r in rows:
            cases.setdefault((r["law"],r["A"].startswith("tri")),r)
        rows=list(cases.values())
    start=perf_counter()
    cases=[read(r) for r in rows]
    summary=dict(total=len(cases),far_sites_already_live=sum(bool(c["second_usable_before"]) for c in cases),
                 now_in_receiver_class=sum(c["site_in_receiver_class_after"] for c in cases),
                 next_round_hearings=sum(c["second_hearing"] is not None for c in cases),
                 by_first_hearing_round=Counter(c["second_round"] for c in cases))
    if not pilot:
        (HERE/"site_after.json").write_text(json.dumps(dict(summary=summary,cases=cases),indent=2)+"\n")
    print(f"{summary} in {perf_counter()-start:.2f} seconds",flush=True)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot",action="store_true")
    run(p.parse_args().pilot)
