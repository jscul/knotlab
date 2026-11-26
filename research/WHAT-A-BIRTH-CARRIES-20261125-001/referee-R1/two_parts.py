"""Recount the first probe and inspect the growth records on explicit examples."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
from itertools import combinations
import json
from pathlib import Path

from b_growth import Law, bar, grow


HOME = Path(__file__).resolve().parents[1]
ROOT = HOME.parents[1]
PROBE = HOME / "checks" / "two_by_two"
TICKET_B = "WHAT-A-BIRTH-CARRIES-20261125-001B"
RING = "Ring(5,3)"
FULL_RUN = ("PARENT-OWING", "CANCEL-OFFSHOOT", "MET-SOLE", "nae")


def rows(name):
    with gzip.open(PROBE / (name + ".jsonl.gz"), "rt") as source:
        for line in source:
            yield json.loads(line)


def triple(row, unordered_partners=False):
    x, y1, y2 = (tuple(row[key]) for key in ("X", "Y1", "Y2"))
    if unordered_partners and y2 < y1:
        y1, y2 = y2, y1
    return row["s"], x, y1, y2


def count_courses(name):
    outcomes = defaultdict(Counter)
    common = defaultdict(set)
    complications = Counter()
    for row in rows(name):
        if "error" in row:
            complications["failed runs"] += 1
            complications[f"failure code {row['returncode']}"] += 1
            continue
        key = "/".join(row["spec"][k] for k in ("ration", "treatment", "knot_law"))
        out = outcomes[key]
        out["completed runs"] += 1
        out["runs through requested horizon"] += row["rounds_read"] == row["spec"].get("rounds", 7)
        by_round = Counter(t["s"] for t in row["triples"])
        for s, n in by_round.items():
            if n == 400:
                complications[f"400-case limit: {row['start']}, s={s}"] += 1
        for t in row["triples"]:
            baseline, bar_first, bar_second, bar_both = t["classes"]
            out["triples"] += 1
            if len(set(t["classes"])) == 1:
                out["same course"] += 1
                if t["last"] <= max(t["meets"]):
                    complications[f"no post-meeting comparison: {row['start']}"] += 1
                continue
            out["different courses"] += 1
            common[row["start"]].add(triple(t, unordered_partners=True))
            if bar_first != bar_second:
                out["single bars differ"] += 1
            elif len({baseline, bar_first, bar_both}) == 3:
                out["three classes by number barred"] += 1
                assert t["kind"] == "a count"
            symmetry = t.get("renaming exchanging Y1 and Y2 fixing X", "unread")
            out[f"exchange: {symmetry}"] += 1
            out[f"meeting rounds: {t['meets']}"] += 1
            out[f"first difference rounds: {t['first differs']}"] += 1
            out[f"last compared round: {t['last']}"] += 1
            m = t.get("m", {})
            out[f"reported m: {m.get('m')}"] += 1
            entries = m.get("entries", [])
            if entries:
                out[f"first saved witness (round, step): {entries[0][:2]}"] += 1
            if any(step in (4, 5, 6, 7) for _, step, _ in entries):
                out["saved witness is at a birth"] += 1
    return {
        "by ration, treatment and knot law": outcomes,
        "run limits and short comparisons": complications,
        "distinct responsive triples by start across laws": {k: len(v) for k, v in common.items()},
    }


def count_scan(name):
    outcomes = defaultdict(Counter)
    distinct_tests = defaultdict(set)
    failures = Counter()
    for row in rows(name):
        if "error" in row:
            failures[str(row["returncode"])] += 1
            continue
        key = "/".join(row["spec"][k] for k in ("ration", "treatment", "knot_law"))
        out = outcomes[key]
        out["completed runs"] += 1
        out["four-run tests"] += len(row["tests"])
        for t in row["tests"]:
            distinct_tests[row["spec"]["start"]].add(triple(t, unordered_partners=True))
            out["different courses in four-run tests"] += len(set(t["classes"])) > 1
        for selection in row["by_s"]:
            out["first parts with two or more partners"] += selection["X with two or more partners"]
            out.update(dict(selection["pairs"]))
            for size, n in selection["partners per X"]:
                out[f"first parts with {size} partners"] += n
    return {
        "by ration, treatment and knot law": outcomes,
        "failures by return code": failures,
        "distinct tests by start across laws": {k: len(v) for k, v in distinct_tests.items()},
    }


def count_first_meetings():
    outcomes = defaultdict(Counter)
    for row in rows("births_explore"):
        out = outcomes[row["spec"]["s"]]
        out["attempted selections"] += 1
        if "parts" not in row:
            out["selections too short to read"] += 1
            continue
        out["selections read"] += 1
        out["selections with multiple parts"] += row["parts"] > 1
        counts = dict(row["first meetings by round and made-only"])
        out["selections with a first meeting"] += bool(counts)
        out.update(counts)
        out["delayed candidate triples"] += row["candidate triples"]
        out["four-run tests"] += len(row["tests"])
    return outcomes


def count_later_lineage():
    out = Counter()
    for row in rows("lineage"):
        out["attempted starts"] += 1
        if "meetings in round 7" not in row:
            out["starts too short to read"] += 1
            continue
        out["starts read"] += 1
        counts = dict(row["meetings in round 7"])
        out["meeting-positive starts"] += bool(counts)
        out.update(counts)
    return out


@lru_cache(maxsize=None)
def start_holders(name):
    if name.startswith("census:"):
        path = ROOT / "research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json"
        return json.loads(path.read_text())[int(name.split(":")[1])]["stars"]
    data = json.loads((ROOT / "research" / TICKET_B / "starts.json").read_text())
    return data["extra"]["stars"] if name == data["extra"]["name"] else data["stars"][name]


def labels(run, s, parts):
    knots = run.states[-1].knots
    result = [0] * len(knots)
    for i, members in enumerate(parts):
        for u in members:
            result[u] = 1 << i
    for u, knot in enumerate(knots):
        if knot.made > s:
            for p in knot.parents:
                result[u] |= result[p]
    return result


def event_profile(run, s, parts):
    bits = labels(run, s, parts)
    out = {}
    for r, step in run.steps.items():
        if r <= s:
            continue
        kinds = {}
        for label, groups in (
            ("group", step.groups),
            ("demand group", step.demand_groups),
        ):
            witnesses = []
            for g in groups:
                tags = {bits[u] & 3 for u in g}
                if 3 in tags or (1 in tags and 2 in tags):
                    witnesses.append({"members": g, "descent tags": sorted(tags)})
            if witnesses:
                kinds[label] = {
                    "all witnesses": len(witnesses),
                    "witnesses with both separate descents": sum(
                        {1, 2}.issubset(w["descent tags"]) for w in witnesses
                    ),
                    "first witness": witnesses[0],
                }
        takes = []
        for b in step.births.values():
            tag = 0
            for p in b.parents:
                tag |= bits[p] & 3
            for d in b.takes:
                for u in sorted(run.states[r - 1].holders[d]):
                    source = bits[u] & 3
                    if (tag & 1 and source & 2) or (tag & 2 and source & 1):
                        takes.append((b.knot, d, u, tag, source))
        if takes:
            kinds["take"] = {
                "all witnesses": len(takes),
                "witnesses with both separate descents": sum(
                    {1, 2} == {b, u} for _, _, _, b, u in takes
                ),
                "first witness": takes[0],
            }
        if kinds:
            out[r] = kinds
    return out


def own_births(run, s, parts):
    bits = labels(run, s, parts)
    observations = {}
    for r, step in run.steps.items():
        if r <= s:
            continue
        rd = []
        for b in step.births.values():
            if bits[b.knot] != 1:
                continue
            groups = [g for g in step.demand_groups if b.knot in g]
            assert len(groups) == b.demand
            tagged = sorted({u for g in groups for u in g if u != b.knot and bits[u] & 6})
            rd.append({
                "knot": b.knot,
                "kind": b.kind,
                "parents": b.parents,
                "places": len(run.states[-1].knots[b.knot].places),
                "demand count": len(groups),
                "partners from barred or unbarred second parts": tagged,
                "parent owing": b.owing,
                "fresh distinctions": len(b.fresh),
            })
        observations[r] = rd
    return observations


def own_signature(run, s, x):
    bits = labels(run, s, [x])
    knots = run.states[-1].knots
    return [
        sorted(Counter(len(knot.places) for u, knot in enumerate(knots) if knot.made == r and bits[u]).items())
        for r in range(s + 1, run.states[-1].number + 1)
    ]


def replay_example():
    row = next(r for r in rows("main") if r["start"] == RING and r["law"].startswith("PARENT-OWING/") and r["spec"]["knot_law"] == "nae")
    t = row["triples"][0]
    s, x, y1, y2 = triple(t)
    law = Law(*FULL_RUN)
    baseline = grow(start_holders(RING), law, rounds=7)
    assert baseline.states[-1].number == row["rounds_read"] and len(baseline.states[-1].knots) == row["knots"]
    assert all(p in baseline.steps[s + 1].roster.parts for p in [x, y1, y2])
    bars = [(), y1, y2, y1 + y2]
    runs = [baseline] + [bar(baseline, s, blocked, law, rounds=7) for blocked in bars[1:]]
    observations = [own_births(r, s, [x, y1, y2]) for r in runs]
    joins = [[b for b in observation[5] if b["kind"] == "join"] for observation in observations]
    assert all(len(j) == 1 for j in joins)
    demand_vector = [j[0]["demand count"] for j in joins]
    assert (demand_vector[1] == demand_vector[2] and len(set(demand_vector)) == 3)
    sizes = [
        {r: sorted(Counter(b["places"] for b in rd).items()) for r, rd in observation.items()}
        for observation in observations
    ]
    first_differences = [
        next((r for r in sorted(sizes[0]) if sizes[0][r] != v[r]), None) for v in sizes[1:]
    ]
    assert first_differences == t["first differs"]
    repeat = event_profile(baseline, s, [x, y1])
    assert repeat[5]["demand group"]["witnesses with both separate descents"] == 1
    assert repeat[6]["group"]["witnesses with both separate descents"] == 1
    same_group = tuple(repeat[6]["group"]["first witness"]["members"])
    repeat_join_born = any(b.parents == same_group for b in baseline.steps[6].births.values())
    assert not repeat_join_born
    return {
        "start": RING,
        "structure at start": start_holders(RING),
        "law": FULL_RUN,
        "saved row": t,
        "bar order": [list(bar) for bar in bars],
        "births with X descent but neither second-part descent": observations,
        "round 5 demand vector": demand_vector,
        "round by round first-part birth sizes": sizes,
        "X and Y1 events by round in baseline": repeat,
        "round 6 X and Y1 group produces a join": repeat_join_born,
    }


def replay_waiting_example():
    row = next(
        r for r in rows("scan_laws")
        if r.get("start") == RING and r["spec"]["ration"] == "FLOOR1" and r.get("tests")
    )
    t = row["tests"][0]
    s, x, y1, y2 = triple(t)
    law = Law("FLOOR1", "CANCEL-WAIT", "MET-SOLE", "nae")
    run = grow(start_holders(RING), law, rounds=7)
    assert all(p in run.steps[s + 1].roster.parts for p in [x, y1, y2])
    knots = run.states[-1].knots
    ancestors = []
    for knot in knots:
        ancestors.append(set(knot.parents).union(*(ancestors[p] for p in knot.parents)))
    results = {}
    for name, y in (("Y1", y1), ("Y2", y2)):
        events = event_profile(run, s, [x, y])
        first = min(events)
        assert first == 5
        bits = labels(run, s, [x, y])
        step = run.steps[first]
        links = set()
        for roster in (step.roster, step.demand_roster):
            for knot, met in roster.met_sets.items():
                tags = {bits[u] for u in met}
                if (3 in tags or {1, 2}.issubset(tags)) and knots[knot].made < first:
                    links.add(knot)
        assert "take" not in events[first]
        assert links and all(knots[knot].made > 0 for knot in links)
        shared = set.intersection(*(ancestors[u] for u in x + y))
        assert not shared
        results[name] = {
            "events by round": events,
            "first meeting linking knots and their birth rounds": sorted(
                (knot, knots[knot].made) for knot in links
            ),
            "ancestors of every member of both parts": sorted(shared),
        }
    return {"law": vars(law), "start": RING, "saved row": t, "findings by second part": results}


def replay_three_partner_prefix(limit):
    """Use strict partner lists from the saved triple roster and a narrower course signature."""
    starts = (RING, "Ring(5,3)+1", "Ring(5,3)+1+2")
    output = {}
    for row in rows("main"):
        name = row["start"]
        if name not in starts or row["spec"]["knot_law"] != "nae" or row["spec"]["ration"] != "PARENT-OWING":
            continue
        law = Law(*FULL_RUN)
        baseline = grow(start_holders(name), law, rounds=7)
        parts = defaultdict(set)
        for t in row["triples"]:
            s, x, y1, y2 = triple(t)
            parts[(s, x)].update((y1, y2))
        out = Counter()
        for (s, x), partners in sorted(parts.items()):
            if len(partners) < 3:
                continue
            first_three = sorted(partners)[:3]
            sigs = defaultdict(set)
            for n in range(4):
                for subset in combinations(first_three, n):
                    blocked = [u for p in subset for u in p]
                    run = baseline if not blocked else bar(baseline, s, blocked, law, rounds=7)
                    sigs[n].add(tuple(tuple(counts) for counts in own_signature(run, s, x)))
            same_within = all(len(signatures) == 1 for signatures in sigs.values())
            distinct = len(set.union(*sigs.values()))
            out["first parts tested"] += 1
            out["four distinct signatures, each constant by count"] += same_within and distinct == 4
            if out["first parts tested"] == limit:
                break
        output[name] = out
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="profile one first part per explicit start")
    args = parser.parse_args()
    report = {
        "method": {
            "recounts": "Independent reductions of saved rows. Course classes and saved renaming and m verdicts were read as supplied.",
            "example": "Growth uses b_growth.py, the independent reconstruction of ticket B's growth. Counts, descent, demand entries and event witnesses are read directly from its records.",
            "three partners": "Prefix of first parts with at least three recorded partners under the owing ration with short knots offshooting and the not-all-equal law. Bar each subset of the first three parts. Compare the round-wise place-count multiset of X descendants.",
        },
        "courses": {name: count_courses(name) for name in ("main", "census_small", "planted")},
        "symmetry scans": {name: count_scan(name) for name in ("scan_small", "scan_laws", "scan_later")},
        "first meetings": count_first_meetings(),
        "later lineage": count_later_lineage(),
        "example replay": replay_example(),
        "waiting example replay": replay_waiting_example(),
        "three-partner recount": replay_three_partner_prefix(1 if args.smoke else 12),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
