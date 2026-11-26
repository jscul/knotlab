"""Extend a paired sample of the original round-seven placements to their benchmark."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import random
from time import perf_counter

from growth import _advance, build_pair, edit_state, far_members, grow, perturb

HERE = Path(__file__).resolve().parent
SEED = 261107
BOUND = 65000
LAST = 21


def read_arm(state, cap):
    readings = []
    sizes = []
    for _ in range(state.round,LAST):
        state, row = _advance(state,cap)
        readings.append(row.own_births)
        sizes.append(len(state.knots))
        if sizes[-1] > BOUND:
            break
    return readings, sizes


def trial(r):
    cap = int(r["law"][-1])
    w = grow(build_pair(r["A"],r["B"]),cap,rounds=3)
    u = far_members(w.states[3],True)[0][0]
    g = perturb(w,3,u,rounds=7)
    v, s = far_members(g.states[7],True)[0]
    assert (u,v,s) == (r["changes"][0]["knot"],r["changes"][1]["knot"],13)
    a, n = read_arm(g.states[7],cap)
    b, m = read_arm(edit_state(g.states[7],v),cap)
    common = 7 + min(len(a),len(b))
    h = next((i for i,(x,y) in enumerate(zip(a,b),8) if x!=y),None)
    old = min(next((t for t,k in enumerate(counts,8) if k>10000),LAST) for counts in (n,m))
    assert old == min(LAST,r["changes"][1]["rounds"])
    return dict(cap=cap,receiver=r["A"],far=r["B"],first_knot=u,second_knot=v,sharings=s,
                old_common_through=old,new_common_through=common,second_hearing=h,
                sizes_from_8_first=n,sizes_from_8_both=m,
                receiver_counts_from_8_first=[len(x) for x in a],receiver_counts_from_8_both=[len(x) for x in b])


def run(pilot):
    with gzip.open(HERE.parent/"again_linked_runs_caps36.jsonl.gz","rt") as f:
        rs = [r for r in map(json.loads,f) if "knot" in r["changes"][1]]
    by_far = defaultdict(dict)
    for r in rs:
        by_far[r["B"]][r["law"]] = r
    choices = sorted(f for f,v in by_far.items() if len(v)==4)
    selected = random.Random(SEED).sample(choices,2)
    rows = []
    for far in selected[:1] if pilot else selected:
        for cap in (4,5,6):
            start = perf_counter()
            row = trial(by_far[far][f"CAP-{cap}"])
            print(f"{far}, cap {cap}, through {row['new_common_through']} in {perf_counter()-start:.2f} s",flush=True)
            rows.append(row)
    if not pilot:
        (HERE/"extend_second.json").write_text(json.dumps(dict(seed=SEED,far_ends=selected,frame=len(choices),
             weighting="Two far ends uniformly without replacement from common round-seven targets, paired across caps.",
             last=LAST,bound=BOUND,cases=rows),indent=2)+"\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot",action="store_true")
    run(p.parse_args().pilot)
