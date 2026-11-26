"""Extend the 28 far ends still linked when the original cap-seven runs stop."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from time import perf_counter

from growth import build_pair, far_members, first_own_difference, grow, link_status, perturb

HERE = Path(__file__).resolve().parent


def extend(far):
    w = grow(build_pair("tri:522@0", far), cap=7, rounds=16, bound=16000)
    u, s = far_members(w.states[3], True)[0]
    h = perturb(w, 3, u)
    heard, end = first_own_difference(w, h, 3)
    return dict(far=far, through_round_16=len(w.rows)>=16 and all(link_status(st) for st in w.states[1:17]),
                baseline_end=len(w.rows), baseline_knots=len(w.states[-1].knots),
                changed_end=len(h.rows), changed_knots=len(h.states[-1].knots),
                knot=u, sharings=s, hearing=heard, common_endpoint=end,
                birth_counts=None if heard is None else [len(g.rows[heard-1].own_births) for g in (w,h)])


def run(pilot):
    begin = perf_counter()
    with gzip.open(HERE.parent/"linked_runs.jsonl.gz", "rt") as f:
        labels = sorted(r["B"] for r in map(json.loads, f) if r["law"]=="CAP-7" and r["linked"][-1] is True)
    if pilot:
        labels = labels[:1]
    cases = [extend(b) for b in labels]
    counts = dict(entries=len(cases), linked_through_16=sum(c["through_round_16"] for c in cases),
                  hearings=Counter(str(c["hearing"]) for c in cases))
    if not pilot:
        (HERE/"extend_seven.json").write_text(json.dumps(dict(rounds=16,bound=16000,setting=3,counts=counts,cases=cases),indent=2)+"\n")
    print(f"{counts} in {perf_counter()-begin:.2f} seconds")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    run(p.parse_args().pilot)
