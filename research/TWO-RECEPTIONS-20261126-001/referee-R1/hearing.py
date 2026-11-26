"""Rebuild the identified late hearings and matched changes of ration, sender and site."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import resource
from time import perf_counter

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3,) * 2)
import reception_growth as growth

HERE = Path(__file__).resolve().parent
PENDANT = "n4:g15:2123@0"
ONE, TWO = "g1:3@0", "g3:22@0"
RATIONS = ("FLOOR1", "PARENT-OWING", "PARENT-OWING-CAP3", "PARENT-OWING-CAP4",
           "OFFSHOOT-TWO", "PARENT-OWING-1", "PARENT-OWING-PLAIN", "ORD")


def census():
    with gzip.open(HERE.parent / "shortage_runs.jsonl.gz", "rt") as src:
        return {(r["A"], r["B"], tuple(r["law"])): r for line in src
                if "law" in (r := json.loads(line))}


def shortages(g):
    out = []
    starts = []
    for s in g.states[:-1]:
        roster = growth.eng.build_roster(s, growth.eng.live_members(s), "actual", growth.eng.Guard(4))
        owing = Counter(u for q in roster.groups for u in q)
        short = [u for u in roster.members if len(s.usable(u)) < owing[u]]
        out.append(sum(u >= s.n_start for u in short))
        starts.append(sum(u < s.n_start for u in short))
    return out, starts


def compare(r, rows):
    a, b, law, take = r
    before = perf_counter()
    pair = growth.build_pair(a, b)
    g = growth.grow(pair, growth.law_of(law, take), 12, 1500, mult=4)
    short, start_short = shortages(g)
    changes = []
    details = []
    links = [growth.link_status(g, t) for t in range(1, g.last_round + 1)]
    if g.last_round > 3 and links[2] is not None:
        for linked, limit in [(True, 5), (False, 2)]:
            for u, s in growth.far_members(g, 3, linked)[:limit]:
                h = growth.fork(g, 3, u)
                heard, common = growth.first_own_difference(g, h, 3)
                changes.append({"linked": linked, "sharings": s, "heard": heard, "rounds": common})
                item = {"target": u, "loose before": len(g.states[3].usable(u))}
                if heard is not None:
                    i = heard - 1
                    original, changed = g.own_births[i], h.own_births[i]
                    item["birth count original, changed"] = [len(original), len(changed)]
                    item["fresh totals original, changed"] = [sum(x[1] for x in original),sum(x[1] for x in changed)]
                    item["counts original"] = list(map(len, g.own_births[:common]))
                    item["counts changed"] = list(map(len, h.own_births[:common]))
                details.append(item)
    key = (a, b, (law, take, None))
    values = {"changes": changes, "rounds": g.last_round, "ended": g.stop, "made short": short, "linked": links}
    if key in rows:
        for k, v in values.items():
            assert rows[key][k] == v, (key, k, rows[key][k], v)
    return {"receiver": a, "sender": b, "ration": law, "take": take, "matches archived fields": key in rows,
            **values, "short start observations by round": start_short, "target details": details,
            "seconds": round(perf_counter() - before, 4)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["late", "cross"], required=True)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    if args.mode == "late":
        cases = [(PENDANT, b, law, None) for law in RATIONS for b in (ONE, TWO)]
        cases += [("n4:g15:2123@3", ONE, "FLOOR1", None)]
    else:
        cases = [("n4:g15:2330@3", TWO, "ORD", "J-EACH-PART"),
                 ("n4:g15:3133@1", "g7:122@0", "ORD", "J-EACH-PART")]
    begin = perf_counter()
    rows = census()
    results = [compare(c, rows) for c in (cases[:1] if args.pilot else cases)]
    print(json.dumps({"mode":args.mode, "results":results, "seconds":round(perf_counter()-begin, 4),
                      "peak KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, indent=2))
