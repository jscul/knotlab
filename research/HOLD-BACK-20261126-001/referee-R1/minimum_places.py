"""Does a ceiling given by the minimum number of places at this birth reproduce the cap?

Before running, fix T=p+L where L=max(3-p,1), and f=max(L,min(D,T)).
Use the four linked pairs in threshold_plan.md, in its predeclared order.
Compare to the archived cap and count actual fresh-count differences on each
unchanged and marked history, omitting the shared prefix of each marked run.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
from time import perf_counter

from archive import records
from growth import grow, Law, link_membership, perturb, sharing_counts

STUDY = Path(__file__).resolve().parents[1]
LOCAL = Law(lambda b: max(b.floor, min(b.demand, len(b.inputs) + b.floor)))


def minimum_ceiling(p, d):
    return p + max(3 - p, 1)


def classify(rows, ceiling):
    bins = Counter()
    for row in rows:
        bins.update(row.counts)
    table = Counter()
    for (p, d, f), n in bins.items():
        cap = min(3, max(d, 3 - p, 1))
        table["decisions"] += n
        table["different fresh count from cap"] += n * (f != cap)
        table["ceiling differs from three"] += n * (ceiling(p, d) != 3)
        table["bound below demand"] += n * (f < d)
    return table


def check(cap, *, law=LOCAL, ceiling=minimum_ceiling, rounds=24, bound=6000, edits_after=(3, 5, 8)):
    w = grow(cap["A"], cap["B"], law, rounds=rounds, bound=bound)
    base = classify(w.rows, ceiling)
    extra = Counter()
    edits = []
    lk = [link_membership(s) for s in w.states[1:]]
    for t in edits_after:
        if t >= len(w.rows) or lk[t-1][0] is None:
            continue
        mem = lk[t-1][1]
        dist = sharing_counts(w.states[t])
        for linked, n in [(True, 5), (False, 2)]:
            eligible = sorted((u for u in mem if mem[u] == linked), key=lambda u:(dist.get(u, float("inf")), u))
            for u in eligible[:n]:
                x = perturb(w, t, u)
                marked_counts = classify(x.rows[t:], ceiling)
                extra.update(marked_counts)
                m = min(len(x.rows), len(w.rows))
                heard = next((j+1 for j in range(t, m) if w.rows[j].own_births != x.rows[j].own_births), None)
                passed = None
                if heard is not None:
                    passed = any(r.births for r in x.rows[heard:m]) and any(r.births for r in w.rows[heard:m])
                edits.append(dict(t0=t, member=u, linked=linked, sharings=dist.get(u),
                                  heard=heard, rounds=m, both_grow_later=passed,
                                  changed_allocations=marked_counts["different fresh count from cap"]))
    def key(c):
        return tuple(c[k] for k in ["t0", "linked", "sharings", "heard", "rounds"])
    return dict(receiver=cap["A"], far=cap["B"], baseline=base, marked_tails=extra, changes=edits,
                matches_cap_on_reported_edits=[key(c) for c in edits] == [key(c) for c in cap["changes"]],
                matches_cap_on_baseline=(w.stop == cap["ended"] and
                    [r.births for r in w.rows] == cap["births"] and
                    [r.made_short for r in w.rows] == cap["made short"] and
                    [s for s, mem in lk] == cap["linked"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    caps = {r["B"]: r for r in records(STUDY / "linked_runs.jsonl.gz") if r["law"][0] == "CAP-3"}
    names = random.Random(2026112603).sample(sorted(caps), 4)
    for name in names[args.skip:args.skip + args.limit]:
        start = perf_counter()
        result = check(caps[name])
        result["seconds"] = round(perf_counter() - start, 3)
        print(json.dumps(result), flush=True)
