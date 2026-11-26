"""Replay the archived gate with the pinned historical engines and a fresh check of each take."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import json
from pathlib import Path
import sys
from time import perf_counter

from growth_engine import build_start

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.with_name(HERE.parent.name + "A")
CONTRACT = json.loads(next((ROOT / "experiments" / TICKET.name).glob("*/contract.json")).read_text())
sys.path.insert(0, str((ROOT / CONTRACT["growth_engine"]).parent))
sys.path.insert(0, str((ROOT / CONTRACT["second_growth_engine"]).parent))
import eng
import pm


def audit_takes(snapshot, births):
    holders = defaultdict(set)
    for knot, distinctions in enumerate(snapshot.places):
        for d in distinctions:
            holders[d].add(knot)

    @lru_cache(maxsize=None)
    def partners(knot):
        return set.union(*(holders[d] for d in snapshot.places[knot])) - {knot}

    @lru_cache(maxsize=None)
    def sole(parents):
        sources = set.intersection(*(partners(k) for k in parents))
        already = {d for k in parents for d in snapshot.places[k]}
        eligible = {d for k in sources for d in snapshot.places[k] if d not in already and len(holders[d]) >= 2}
        return eligible if len(eligible) == 1 else set()

    count = 0
    for birth in births:
        expect = sole(tuple(birth["parents"]))
        assert sorted(expect) == sorted(birth["takes"])
        count += len(expect)
    return count


def replay(row, first, families):
    dataset, knot_law, family, name, take, ration, treatment, other, linked = row["key"].split("|")
    assert dataset in {"R1", "R2"} and knot_law == "nae" and linked == "True"
    seed = None if other == "None" else families[family][other]
    start, _ = build_start(first[name], seed)
    rounds = 10 if family == "chains" else 9
    take = None if take == "None" else take
    law = eng.Law(ration, treatment, take, knot_law)
    run = eng.Run(law, stars=start, rounds=rounds, knot_bound=3000)
    assert (run.rounds_read, run.stop, run.S.n_knots) == (row["rounds_read"], row["stop"], row["knots"])
    if take:
        assert take == "MET-SOLE"
        births = sum(len(r["births"]) for r in run.recs)
        took = sum(audit_takes(s, r["births"]) for s, r in zip(run.snaps, run.recs))
        assert (births, took) == (row["births"], row["takes"])
        return Counter(sole_runs=1, births_checked=births, takes=took)
    previous = pm.Run(pm.from_stars(start), pm.Law(ration=ration, treatment=treatment, release="RELEASE",
                      knot_law=knot_law, closing="IMPLIED", take=None), rounds=rounds, knot_bound=3000)
    assert (previous.stop, previous.rounds_done) == (run.stop, run.rounds_read)
    def guard_at(result):
        return (result.guard["round"], result.guard["what"]) if result.guard else None
    assert guard_at(previous) == guard_at(run)
    assert len(previous.snap) == len(run.snaps) == row["rounds_compared"]
    assert not any(b["takes"] for r in run.recs for b in r["births"])
    for left, right in zip(previous.snap, run.snaps):
        assert left.places == right.places
        assert tuple(map(tuple, left.parents)) == tuple(map(tuple, right.parents))
        assert (left.made, left.kind, left.barred) == (right.made, right.kind, right.barred)
    return Counter(no_take_runs=1, snapshots_including_starts=len(run.snaps))


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true", help="first three sampled runs and the slowest archived case")
    args = p.parse_args()
    source = json.loads((TICKET / "seeds.json").read_text())
    seeds = {family: {s["name"]: s for s in entries} for family, entries in source["second"].items()}
    rows = []
    for path in (ROOT / "artifacts" / TICKET.name).glob("*/gate_*.jsonl.gz"):
        with gzip.open(path, "rt") as f:
            rows.extend(map(json.loads, f))
    rows.sort(key=lambda r: r["sample_index"])
    assert [r["sample_index"] for r in rows] == list(range(400))
    if args.pilot:
        rows = rows[:3] + [max(rows, key=lambda r: r["sec"])]
    start = perf_counter()
    counts = Counter()
    for row in rows:
        counts.update(replay(row, source["first"], seeds))
    print(dict(counts), f"{perf_counter()-start:.2f} s", flush=True)
    if not args.pilot:
        (HERE / "gate_replay_counts.json").write_text(json.dumps(counts, indent=2) + "\n")


if __name__ == "__main__":
    main()
