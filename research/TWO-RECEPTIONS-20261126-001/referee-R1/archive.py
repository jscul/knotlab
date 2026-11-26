"""Recount the immutable rows without running growth."""
import argparse
import gzip
import json
import resource
from collections import Counter, defaultdict
from itertools import islice
from pathlib import Path
from time import perf_counter

resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
HERE = Path(__file__).resolve().parent


def load(name, limit):
    with gzip.open(HERE.parent / name, "rt") as stream:
        return list(map(json.loads, islice(stream, limit)))


def recount(limit):
    a = load("two_runs.jsonl.gz", limit)
    b = load("shortage_runs.jsonl.gz", limit)
    second_keys = {(r["A"], r["B"], r["law"], tuple(r["first"]), r["t"], tuple(r["second"]))
                   for r in a if "second" in r}
    by_first = defaultdict(Counter)
    for r in a:
        if "second" in r:
            by_first[str(r["first"][0])].update([r["kind"]])
    groups = defaultdict(Counter)
    pairs_by_receiver = defaultdict(Counter)
    linked_receivers = defaultdict(set)
    receivers = set()
    keys = set()
    hits = []
    for r in b:
        if "law" not in r:
            continue
        receivers.add(r["A"])
        law = "/".join(s for s in r["law"] if s)
        key = (r["A"], r["B"], law)
        assert key not in keys
        keys.add(key)
        summary = groups[law]
        pairs_by_receiver[law][r["A"]] += 1
        summary["pairs"] += 1
        summary["with made short"] += any(r["made short"])
        summary["short observations"] += sum(r["made short"])
        summary[r["ended"]] += 1
        for c in r["changes"]:
            if c["linked"]:
                linked_receivers[law].add(r["A"])
            linked = "linked" if c["linked"] else "unlinked"
            summary[linked] += 1
            if c["heard"] is not None:
                summary["heard " + linked] += 1
                summary["heard in round " + str(c["heard"])] += 1
                summary["heard at sharings " + str(c["sharings"])] += 1
                if r["law"][0] != "ORD":
                    hits.append({"law":law,"A":r["A"],"B":r["B"], **c})
    for law, by_receiver in pairs_by_receiver.items():
        groups[law]["receivers represented"] = len(by_receiver)
        groups[law]["receivers with five senders"] = sum(n == 5 for n in by_receiver.values())
        groups[law]["receivers with linked placements"] = len(linked_receivers[law])
    settings = Counter((r["law"], r["first"][0], r["r1"]) for r in a)
    censored = Counter(r["law"] for r in a if "second" in r and
                       r["rounds"] < r["t"] + r["second"][1] + 1)
    return {"second changes":len(second_keys), "second rows":len(a),
            "unique pair and cap keys":len({(r["A"],r["B"],r["law"]) for r in a}),
            "first histories":len({(r["A"],r["B"],r["law"],r["first"][1]) for r in a}),
            "by first":dict(by_first), "rounds by first and cap":sorted([*k,n] for k,n in settings.items()),
            "common endpoints":dict(Counter(r["rounds"] for r in a if "second" in r)),
            "cancellations by first sharings":dict(Counter(r["first"][2] for r in a if r.get("kind") == "cancels")),
            "ending before setting round plus sharings plus one":dict(censored),
            "cancelling settings":sorted({(r["t"],r["second"][1],r["r1"],r["r2"]) for r in a if r.get("kind")=="cancels"}),
            "census keys":len(keys), "receivers represented":len(receivers), "census by law":dict(groups),
            "incomplete jobs":[r for r in b if "not run" in r], "hearings under reduced rations":hits}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    start = perf_counter()
    result = recount(25 if args.pilot else None)
    print(json.dumps({**result, "seconds":round(perf_counter()-start,4)}, indent=2))
