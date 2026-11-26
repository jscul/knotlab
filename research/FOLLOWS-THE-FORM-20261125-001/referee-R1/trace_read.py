"""Extract two held-out pairs' literal births and reread their first two rounds."""

import argparse
import gzip
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "FOLLOWS-THE-FORM-20261125-001A"
GROWTH = "WHAT-A-BIRTH-CARRIES-20261125-001B"
CASES = [
    ("K", "CAP-3", "none", ("ring:1,2,1,2@0", "ring:1,2,1,3@0")),
    ("L", "FLOOR1", "sole", ("path:2,1,1,2@0", "path:1,2,1,2@0")),
]


def make_start(first, second):
    site = first["site"]
    link = 1 + max(d for knot in first["knots"] for d in knot)
    start = [knot.copy() for knot in first["knots"]]
    start[site].append(link)
    for i, knot in enumerate(second["knots"]):
        places = [d + link + 1 for d in knot]
        if i == second["at"]:
            places.append(link)
        start.append(places)
    return start, link


def partners(places):
    held = [set(knot) for knot in places]
    return [
        {v for v, other in enumerate(held) if v != u and own & other}
        for u, own in enumerate(held)
    ]


def groups_on(places, members):
    # These rosters are small enough to test every subset against the definition.
    met = [other & set(members) for other in partners(places)]
    pairs = {
        pair for pair in combinations(members, 2)
        if any(set(pair) <= common for common in met)
    }
    large = []
    for size in range(len(members), 2, -1):
        for choice in combinations(members, size):
            group = set(choice)
            if (all(pair in pairs for pair in combinations(choice, 2))
                    and not any(group <= common for common in met)
                    and not any(group <= larger for larger in large)):
                large.append(group)
    uncovered = [pair for pair in pairs if not any(set(pair) <= group for group in large)]
    return sorted([tuple(sorted(group)) for group in large] + uncovered)


def read_births(start, n_first, run, ration, take):
    # Read only parents and literal distinction lists for counting FF 5 and 5b.
    places = [knot.copy() for knot in start]
    origin = ["first"] * n_first + ["second"] * (len(start) - n_first)
    rounds = []
    barred = set()
    for t, rec in enumerate(run.recs, 1):
        old_partners = partners(places)
        old_count = Counter(d for knot in places for d in knot)
        usable = {u: {d for d in knot if old_count[d] == 1 and d not in barred}
                  for u, knot in enumerate(places)}
        members = sorted(u for u, ds in usable.items() if ds)
        groups = groups_on(places, members)
        short = [u for u in members if sum(u in g for g in groups) > len(usable[u])]
        assert short == sorted(rec["short"])
        assert groups == sorted(map(tuple, rec["groups"]))
        barred.update(d for u in short for d in usable[u])
        births = []
        own = Counter()
        wider = Counter()
        for b in rec["births"]:
            k = b["id"]
            parents = list(b["parents"])
            sources = {origin[p] for p in parents}
            origin.append(sources.pop() if len(sources) == 1 else "both")
            assert k == len(places)
            given = list(b["loose"])
            taken = list(b["takes"])
            fresh = list(b["fresh"])
            assert len(given) == len(parents)
            for d, parent in zip(given, parents):
                assert d in places[parent] and old_count[d] == 1
            possible = set()
            if take == "sole":
                common = set.intersection(*(old_partners[p] for p in parents))
                held_by_parent = set().union(*(places[p] for p in parents))
                possible = {
                    d for w in common for d in places[w]
                    if d not in held_by_parent and old_count[d] >= 2
                }
                assert taken == (sorted(possible) if len(possible) == 1 else [])
            else:
                assert not taken
            assert all(d not in old_count for d in fresh)
            places.append(given + taken + fresh)
            assert places[k] == run.snaps[t].places[k]
            kind = "j" if len(parents) >= 2 else "o"
            entry = (kind, len(parents), len(places[k]), len(fresh), len(taken))
            if origin[k] in ("first", "both"):
                wider[(*entry, int(origin[k] == "first"))] += 1
            if origin[k] == "first":
                own[entry] += 1
            births.append({
                "knot": k, "parents": parents, "given": given,
                "eligible_candidates": sorted(possible), "taken": taken,
                "fresh": fresh, "descent": origin[k],
                "demand": b["D"],
            })
        met = partners(places)
        # Both traces use retiring and release. Every old member retired or spent.
        demand_groups = groups_on(places, [b["knot"] for b in births])
        assert demand_groups == sorted(map(tuple, rec["demand"].groups if births else []))
        for b in births:
            demand = sum(b["knot"] in group for group in demand_groups)
            assert demand == b["demand"]
            p = len(b["given"]) + len(b["taken"])
            minimum = max(3 - p, 1)
            required = min(max(minimum, demand), 3) if ration == "CAP-3" else minimum
            assert len(b["fresh"]) == required
            if b["descent"] == "second":
                continue
            b["second_only_newborn_partners"] = [
                c["knot"] for c in births
                if c["descent"] == "second" and c["knot"] in met[b["knot"]]
            ]
        rounds.append({
            "round": t, "members": members, "groups": groups,
            "short": short, "newly_barred": sorted(d for u in short for d in usable[u]),
            "births": births, "demand_groups": demand_groups,
            "own": [list(entry) + [count] for entry, count in sorted(own.items())],
            "wider": [list(entry) + [count] for entry, count in sorted(wider.items())],
        })
    return rounds


def replay(eng, first_name, ration, take, second_name, seed_file):
    first = seed_file["first"][first_name]
    second = next(s for s in seed_file["second"]["fresh"] if s["name"] == second_name)
    start, link = make_start(first, second)
    law = eng.Law(ration, "CANCEL-RETIRE", "MET-SOLE" if take == "sole" else None, "nae")
    historical = eng.run_stars(start, law, rounds=2, knot_bound=3000)
    assert historical.rounds_read == 2
    return {
        "first": first_name, "second": second_name, "knot_law": "nae",
        "ration": ration, "treatment": "CANCEL-RETIRE", "take": take,
        "start": start, "link": link, "first_seed_size": len(first["knots"]),
        "rounds": read_births(start, len(first["knots"]), historical, ration, take),
    }


def compare_shards(runs):
    pending = {(r["first"], r["ration"], r["take"], r["second"]): r for r in runs}
    for p in sorted((ROOT / "artifacts" / TICKET).glob("*/runs_R2_*.jsonl.gz")):
        with gzip.open(p, "rt") as fd:
            for line in fd:
                row = json.loads(line)
                key = (row["first"], row["ration"], row["take"], row["second"])
                if key not in pending or row["treatment"] != "CANCEL-RETIRE":
                    continue
                run = pending.pop(key)
                assert row["linked"] and row["knot_law"] == "nae"
                for t, rec in enumerate(run["rounds"]):
                    assert row["make"][t] == rec["own"]
                    assert row["wider"][t] == rec["wider"]
                run["archived_shard"] = p.name
    assert not pending, pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time-first", action="store_true",
                        help="time the first two-round trace of each law")
    args = parser.parse_args()
    seed_file = json.loads((ROOT / "research" / TICKET / "seeds.json").read_text())
    sys.path.insert(0, str(next((ROOT / "experiments" / GROWTH).glob("*/eng.py")).parent))
    import eng

    pairs = []
    for first_name, ration, take, names in CASES:
        t0 = time.perf_counter()
        runs = [
            replay(eng, first_name, ration, take, name, seed_file)
            for name in (names[:1] if args.time_first else names)
        ]
        if args.time_first:
            print(f"{ration}, {take}, one two-round trace: {time.perf_counter()-t0:.4f} seconds")
        else:
            left, right = (r["rounds"] for r in runs)
            assert left[0]["wider"] == right[0]["wider"]
            assert left[0]["own"] == right[0]["own"] and left[1]["own"] != right[1]["own"]
            pairs.append(runs)
    if not args.time_first:
        compare_shards([run for pair in pairs for run in pair])
        (HERE / "trace_births.json").write_text(json.dumps(pairs, indent=1) + "\n")
        print("Four runs agree with the stored own and wider outputs for both rounds.")


if __name__ == "__main__":
    main()
