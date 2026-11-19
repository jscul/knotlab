"""Independent literal, archived and roster controls for the growth probe."""

import argparse
from collections import Counter
import gzip
from itertools import combinations
import json
from pathlib import Path
import sys

from probe_growth import bits, follow, initial_roster, sizes_by_round, start_metrics
from probe_job import ROOT, SOURCE, census_starts, read_results


ARTIFACTS = ROOT / "artifacts"
ROSTERS = "WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered"
VERIFY = "GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"
EXTEND = "EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"
FAST = "JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins"
sys.path[:0] = [str(ROOT / "proofs" / ROSTERS), str(ROOT / "experiments" / VERIFY), str(ROOT / "experiments" / EXTEND),
                str(ROOT / "experiments" / FAST)]
import fastlib  # noqa: E402
import rosterlib  # noqa: E402
from verify import Arrangement, round_replay, start_audit  # noqa: E402
from extend import C, grow1  # noqa: E402


def raw_stars(sizes, meetings):
    result = [[] for _ in sizes]
    for name, (u,v) in enumerate(meetings):
        result[u].append(name)
        result[v].append(name)
    name = len(meetings)
    for j, row in enumerate(result):
        count = sizes[j] - len(row)
        row.extend(range(name, name+count))
        name += count
    return result


def literal_check(sizes, links, report, through):
    fastlib.install(C.S.F)
    try:
        return _literal_check(sizes, links, report, through)
    finally:
        fastlib.uninstall(C.S.F)


def _literal_check(sizes, links, report, through):
    previous = Arrangement.parse(raw_stars(sizes, links))
    gate = start_audit(previous)
    observations = []
    stage_counts = list(sizes_by_round(start_metrics(sizes, links), report["rows"]))
    for age in range(1, through+1):
        after = Arrangement.parse([sorted(row) for row in grow1(previous.stars)])
        rows = round_replay(previous, after)
        hist = sorted((p,f,count) for (p,f),count in Counter((len(row["taken"]), len(row["fresh"])) for row in rows).items())
        assert hist == list(map(tuple, report["rows"][age-1]["birth_histogram"]))
        exhausted = max((len(row) for j,row in enumerate(after.stars) if j not in after.live), default=0)
        current = [len(after.stars), len(after.labels), max(map(len, after.stars)), exhausted]
        assert current == stage_counts[age]
        observations.append({"age": age, "stage_sizes": current, "literal_births": hist})
        previous = after
    return {"start_gate": gate, "through_age": through, "observations": observations}


def independent_roster(start, history, through):
    opn, blocks = start
    ordinary = rosterlib.keys_by_round(opn, [frozenset(bits(k)) for k in blocks], through)
    wanted = [sorted((tuple(entry[:2]), entry[2]) for entry in row["birth_histogram"])
              for row in history["rows"][:through]]
    if len(wanted) < through and history["end"] in {"closed", "demand_stall"}:
        wanted.append("closed" if history["end"] == "closed" else "stall")
    assert ordinary == wanted, (len(opn), ordinary[:4], wanted[:4])
    return len(wanted)


def partnered_presentation(n):
    live = 2*n
    roster = [edge for edge in combinations(range(live), 2) if edge[0]//2 != edge[1]//2]
    hubs = list(range(live, live+len(roster)))
    # The closed holders form a cycle, so no holder is an articulation.
    meetings = [tuple(sorted((u, v))) for u,v in zip(hubs, hubs[1:]+hubs[:1], strict=True)]
    meetings += [(u,h) for h,edge in zip(hubs, roster, strict=True) for u in edge]
    sizes = [2*(n-1) + (1 << (n-1))] * live + [4] * len(hubs)
    return sizes, sorted(meetings)


def paired_controls():
    material = {}
    for n, stop in [(2, 10), (3, 3)]:
        sizes, links = partnered_presentation(n)
        start = initial_roster(sizes, links)
        official = rosterlib.roster_of(sizes, links)
        assert tuple(official[0]) == start[0]
        report = follow(start, depth=stop)
        independent_roster(start, report, stop)
        literal = literal_check(sizes, links, report, stop)
        assert literal["start_gate"]["census_open_legal"]
        populations = [2*n, 1 << n]
        if n == 3:
            while len(populations) <= 4:
                populations.append((1 << (populations[-1]//2))-populations[-2])
        for age, row in enumerate(report["rows"], 1):
            if n == 2:
                assert row["birth_histogram"] == [[2,2,4]]
                continue
            parents = populations[age-1]//2
            fresh = (1 << (populations[age]//2-1))-parents
            assert row["birth_histogram"] == [[parents,fresh,populations[age]]]
        extra = {}
        if n == 3:
            following = (1 << (populations[4]//2))-populations[3]
            extra = {"symbolic_round4": {"births": populations[4], "parents": populations[3]//2,
                                        "loose": (1 << (populations[4]//2-1))-populations[3]//2,
                                        "size": 1 << (populations[4]//2-1)},
                     "symbolic_round5": {"births": following, "parents": populations[4]//2,
                                        "size": f"2^{(following//2-1)}"}}
        material[f"partnered_{n}"] = {"initial_sizes": sizes, "initial_meetings": links, "growth": report,
                                       "literal": literal, **extra}
    return material


def merge_controls():
    data = read_results(ROOT / "runs/merge-burst/results.jsonl")
    material = {}
    for key in ("start-00", "start-04"):
        source = data[key]["result"]
        sizes = source["start"]["sizes"]
        links = [tuple(i) for i in source["start"]["edges"]]
        exact = follow(initial_roster(sizes, links), depth=24, birth_limit=16000, clique_limit=800000)
        sizes_per_age = list(sizes_by_round(start_metrics(sizes, links), exact["rows"]))
        for archived, measured in zip(source["follow"]["rounds"], exact["rows"]):
            assert (archived["count"], archived["group"]) == (measured["births"], measured["maximum_parent_count"])
            assert archived["junctions"] == sizes_per_age[archived["t"]][0]
        block = exact.get("single_block")
        assert block is not None and block["population"] == (9 if key == "start-00" else 781)
        at_age = block["at_age"]
        assert at_age == len(source["follow"]["rounds"])
        literal = literal_check(sizes, links, exact, min(4, at_age))
        material[key] = {"start_sizes": sizes, "start_meetings": links, "growth": exact,
                         "literal_prefix": literal, "sizes_through_truncation": sizes_per_age,
                         "exact_at_closure": [sizes_per_age[at_age][0] + block["all_later_births"],
                                              sizes_per_age[at_age][1] + block["all_later_fresh"],
                                              max(sizes_per_age[at_age][2], block["population"])]}
    return material


def archived_census_checks(artifact):
    with gzip.open(artifact, "rt") as handle:
        data = json.load(handle)
    starts = census_starts()
    by_key = {(tuple(row["key"][0]), tuple(row["key"][1])): row for shard in read_results(SOURCE).values()
              for row in shard["result"]["arrangements"]}
    stats = Counter()
    for row in data:
        start, hist = row["roster"], row["history"]
        masks = tuple(sum(1 << j for j in part) for part in start[1])
        independent_roster((tuple(start[0]), masks), hist, 6)
        stats["exact_roster_prefixes"] += 1
        for index, *_ in row["members"]:
            prior = by_key[starts[index]]
            stop = hist["last_complete_age"]
            prior_end = prior["outcome"]
            if prior_end in {"closed", "stall"} and prior["rounds"] <= stop:
                assert hist["end"] == ("closed" if prior_end == "closed" else "demand_stall")
                assert stop == prior["rounds"], (index, stop, prior)
                stats["archive_natural_terminal"] += 1
            recent = prior["last"]
            start_age = prior["rounds"] - len(recent) + 1
            for age in range(max(1,start_age), min(prior["rounds"], stop)+1):
                assert hist["rows"][age-1]["births"] == recent[age-start_age], (index, age, prior)
                stats["archive_tail_round_counts"] += 1
    return dict(stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--census", type=Path)
    parser.add_argument("--subset", choices=["paired", "merge", "archive", "all"], default="all")
    args = parser.parse_args()
    result = {}
    if args.subset in {"paired", "all"}:
        result.update(paired=paired_controls())
    if args.subset in {"merge", "all"}:
        result.update(merge=merge_controls())
    if args.subset in {"archive", "all"} and args.census:
        result.update(census_replay=archived_census_checks(args.census))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
