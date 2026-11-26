"""Replay the reported reader comparisons from the start holdings under both laws.

From the repository root:
  .venv/bin/python -B research/ON-DEMAND-20261126-001/referee-R1/replay.py pilot
  .venv/bin/python -B research/ON-DEMAND-20261126-001/referee-R1/replay.py sample
"""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import resource
import time

from growth import grow, joins
from replay_inputs import HORIZONS, cases, census_archive


HERE = Path(__file__).resolve().parent
CAP = 3000
MEMORY = 3 << 30
SEED = 871926
H1 = "H1 within t + 1 steps agrees"
SMALL = "within t steps agrees"
ENDINGS = "region ends where H1 differs"
PROV = "births of the region not in the full growth, of all the region's births, at round t"
NEED = "births needed, of all births, through round t"
CAPPED = "region growths stopped at the cap, not read"


def selected(pop, all_cases, mode):
    eligible = [c for c in all_cases if "laws" in c.record]
    growing = [c for c in eligible if c.record["laws"]["nae"]["end"] != "stall"]
    parity_miss = [c for c in growing if c.record["laws"]["parity"][ENDINGS]
                   or any(r[2] is False or isinstance(r[2], list) and not all(r[2])
                          for r in c.record["laws"]["parity"]["H2"])]
    if mode == "pilot":
        # Fixed pilot including the same caps, laws, horizons and random draws as the sample.
        fixed = {"tree40": {0, 2}, "treeplus25": {0, 7}, "census6": {42518, 14733, 50090}}
        return [c for c in eligible if c.index in fixed[pop]]
    rng = random.Random(f"{SEED}:{pop}")
    sample = rng.sample(growing, 12 if pop != "census6" else 28)
    fewer_steps_miss = [c for c in growing if not all(c.record["laws"]["nae"][SMALL].values())]
    keep = {c.index for c in sample + parity_miss + fewer_steps_miss}
    keep.update(c.index for c in eligible if c.record["laws"]["nae"]["end"] == "stall")
    return [c for c in eligible if c.index in keep]


def detail(full, restricted, reader, t, region, catalogue, fullnames):
    whole = full.views(reader, t)
    part = restricted.views(reader, t)
    first = next(i + 1 for i in range(t) if whole[i] != part[i])
    cutoff = len(restricted.rows)
    event = {}
    if restricted.end == "closed" and cutoff:
        born = restricted.rows[-1]
        terminal = born[0]
        old_fresh = ([b.fresh for b in restricted.rows[-2]] if cutoff > 1
                     else [region.loose[k] for k in restricted.start])
        old_total = sum(old_fresh)
        taken = len(terminal.parents)
        region_names = restricted.names(catalogue)
        name, = region_names[-1]
        full_row = full.rows[cutoff - 1] if len(full.rows) >= cutoff else ()
        # For a full birth, identify the corresponding recursively named parent multiset,
        # and then recover its fresh count separately. Names intentionally omit fresh counts.
        old = [-k - 1 for k in full.start]
        desc = []
        for row in full.rows[:cutoff]:
            current = [(catalogue[tuple(sorted(old[p] for p in b.parents))], b.fresh) for b in row]
            old = [key for key, _ in current]
            desc = current
        event = {
            "round": cutoff,
            "total loose beforehand": old_total,
            "terminal parents": taken,
            "terminal kind": terminal.description[0],
            "terminal fresh": terminal.fresh,
            "single birth takes every loose distinction": len(born) == 1 and old_total == taken,
            "full births at that round": len(full_row),
            "full fresh counts at matching parent descent":
                sorted(f for key, f in desc if key == name) if full_row else [],
            "full birth count at matching parent descent": fullnames[cutoff - 1][name],
            "full implied at that round":
                full.end == "closed" and len(full.rows) == cutoff and bool(full_row)
                and len(full_row) == 1 and full_row[0].fresh == 0,
        }
    return {
        "reader": reader, "comparison horizon": t,
        "live start knots in region": sorted(region.loose), "first different round": first,
        "first reading differs there": whole[first - 1][0] != part[first - 1][0],
        "reading with parents differs there": whole[first - 1][1] != part[first - 1][1],
        "region end": restricted.end, "full end at study horizon": full.end,
        "terminal birth": event,
    }


def check_predecessor(full, record):
    views = full.views()
    compared = min(len(views), len(record["rows"]))
    for i, ((first, second), row) in enumerate(zip(views, record["rows"]), 1):
        saved_first = Counter({tuple(desc): count for desc, count in row["sig0"]})
        saved_second = Counter({(tuple(desc), tuple(map(tuple, parents))): count
                                for (desc, parents), count in row["sig1"]})
        if first != saved_first or second != saved_second:
            raise AssertionError(("earlier whole reading", record["index"], i))
    if len(views) < len(record["rows"]) and full.end in ("closed", "stall"):
        raise AssertionError(("extra births in earlier archive", record["index"]))
    return compared


def reading_delta(whole, part):
    return {"full only": sorted((k, v) for k, v in (whole - part).items()),
            "region only": sorted((k, v) for k, v in (part - whole).items())}


def compare_fewer_steps(case, full, region, restricted, t):
    reader = case.reader
    whole, part = full.views(reader, t), restricted.views(reader, t)
    first = next(i for i in range(t) if whole[i] != part[i])
    initial_groups = [g for g in joins(case.roster.loose, case.roster.blocks) if len(g) >= 3]
    cut = [g for g in initial_groups if region.intersection(g) and not region.issuperset(g)]
    candidates = []
    for g in initial_groups:
        inside = region.intersection(g)
        for x in case.roster.loose.keys() - region:
            sees = case.roster.neighbours[x] & inside
            if len(sees) >= 2:
                candidates.append({"full group": g, "outside knot": x, "joinable inside members": sorted(sees),
                                   "outside knot in this group": x in g})

    def coarser(view, places):
        rows = []
        for counts, _ in view:
            row = Counter()
            for desc, value in counts.items():
                row[tuple(desc[i] for i in places)] += value
            rows.append(row)
        return rows

    small = []
    for q in range(t):
        other = grow(case.roster.restrict(case.within(q)), t, "nae",
                     CAP if case.population == "treeplus25" else None)
        equal = None if other.end == "cap" else other.views(reader, t) == whole
        small.append({"steps": q, "end": other.end, "agrees": equal})
    comparison = {
        "start index": case.index, "population": case.population,
        "reader": reader, "round": t, "within t": sorted(region),
        "first different round": first + 1,
        "reader birth totals through t, full": [sum(a.values()) for a, _ in whole],
        "reader birth totals through t, region": [sum(a.values()) for a, _ in part],
        "counts by parents alone agree through t": coarser(whole, [1]) == coarser(part, [1]),
        "counts by fresh distinctions alone agree through t": coarser(whole, [2]) == coarser(part, [2]),
        "first reading differs there": whole[first][0] != part[first][0],
        "first-round-only reading agrees": whole[0] == part[0],
        "first reading at first difference": reading_delta(whole[first][0], part[first][0]),
        "reading including parents at first difference": reading_delta(whole[first][1], part[first][1]),
        "full first-round groups of three or more cut by this region": cut,
        "outside knots joinable to two or more inside members of a full group of three or more": candidates,
        "fewer steps": small,
    }
    if first == 0:
        for name, tr in (("full", full), ("region", restricted)):
            comparison[f"first reader births in {name}"] = sorted(
                (sorted(tr.start[p] for p in b.parents), b.fresh) for b in tr.rows[0]
                if b.ancestry >> reader & 1) if tr.rows else []
    return comparison


def replay_law(case, law, archive):
    saved = case.record["laws"][law]
    horizon = HORIZONS[case.population]
    roster, reader = case.roster, case.reader
    full = grow(roster, horizon, law, CAP)
    n = len(full.rows) if full.end == "cap" else horizon
    score = Counter({"start-law replays": 1, "whole birth rounds": len(full.rows),
                     "whole births": sum(map(len, full.rows))})
    if archive is not None:
        score["earlier whole reading rounds compared"] = check_predecessor(full, archive[case.index])
    if full.end != saved["end"] or n != saved["rounds read"]:
        raise AssertionError(("full end", case.index, law, full.end, n, saved["end"]))
    if full.end == "stall":
        limit = max(case.steps.values())
        stop = next((s for s in range(limit + 1)
                     if grow(roster.restrict(case.within(s)), 1, law).end == "stall"), None)
        if stop != saved["least steps whose knots stall"]:
            raise AssertionError(("stall", case.index, law, stop))
        score["whole stalls"] += 1
        return score, [], []
    fullview = full.views(reader, n)
    catalogue = {}
    fullnames = full.names(catalogue) + [Counter() for _ in range(n - len(full.rows))]
    alld = defaultdict(list)
    for t in range(1, n + 1):
        alld[case.within(t)].append(t)
        alld[case.within(t + 1)].append(t)
    for t, region in case.h2 + case.admissions:
        if t <= n:
            alld[region].append(t)
    regions = {}
    names = {}
    for region, use in alld.items():
        if region == roster.loose.keys():
            trace = full
            names[region] = fullnames
        else:
            rcap = CAP if case.population == "treeplus25" else None
            trace = grow(roster.restrict(region), max(use), law, rcap)
        regions[region] = trace
        if trace is not full:
            score["distinct nonfull growths"] += 1
            score["distinct nonfull birth rounds"] += len(trace.rows)
            score["distinct nonfull births"] += sum(map(len, trace.rows))
    def available(region, t):
        trace = regions[region]
        return trace.end != "cap" or len(trace.rows) >= t

    observed = {H1: {}, SMALL: {}, ENDINGS: {}, PROV: {}, NEED: {}, "H2": [], CAPPED: []}
    differences = []
    smaller_steps = []

    def test(region, t, kind, index=None):
        trace = regions[region]
        ok = trace.views(reader, t) == fullview[:t]
        if not ok and kind in (H1, "H2"):
            # A cached trace may have run farther than the recorded comparison.
            trace_at = grow(roster.restrict(region), t, law,
                            CAP if case.population == "treeplus25" else None)
            cause = detail(full, trace_at, reader, t, roster.restrict(region), catalogue, fullnames)
            cause.update({"test": kind, "item": index, "law": law, "population": case.population,
                          "start index": case.index})
            differences.append(cause)
        score[kind + " comparisons"] += 1
        if not ok:
            score[kind + " differences"] += 1
        return ok

    for t in range(1, n + 1):
        within = case.within(t + 1)
        if not available(within, t):
            observed[CAPPED].append(["H1", t])
            continue
        key = str(t)
        observed[H1][key] = test(within, t, H1)
        if not observed[H1][key]:
            # Each recorded t is a fresh from-start run.
            observed[ENDINGS][key] = differences[-1]["region end"]
        if within not in names:
            names[within] = regions[within].names(catalogue)
        rownames = names[within][t - 1] if len(names[within]) >= t else Counter()
        observed[PROV][key] = [sum((rownames - fullnames[t - 1]).values()), sum(rownames.values())]
        nearer = case.within(t)
        if available(nearer, t):
            observed[SMALL][key] = test(nearer, t, SMALL)
            if law == "nae" and not observed[SMALL][key]:
                smaller_steps.append(compare_fewer_steps(case, full, nearer, regions[nearer], t))
        observed[NEED][key] = list(full.needed(reader, t))
    for i, (t, region) in enumerate(case.h2):
        if t > n:
            continue
        if not available(region, t):
            observed[CAPPED].append(["H2", t])
        else:
            ok = test(region, t, "H2", f"random {i + 1}")
            observed["H2"].append([t, len(region - case.within(t + 1)), ok])
    if case.admissions[0][0] <= n:
        oks = []
        for i, (t, region) in enumerate(case.admissions):
            if not available(region, t):
                observed[CAPPED].append(["H2 admitted", t])
            else:
                oks.append(test(region, t, "H2", f"admission {i + 1}"))
        observed["H2"].append([t, "admitted in three steps", oks])
    for k, value in observed.items():
        if value != saved.get(k, []):
            raise AssertionError(("archive drift", case.population, case.index, law, k, value, saved.get(k)))
    return score, differences, smaller_steps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("pilot", "sample"))
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
    overall = time.monotonic()
    scores, diffs, by_start, smaller = {}, [], {}, []
    for population in HORIZONS:
        records = list(cases(population))
        chosen = selected(population, records, args.mode)
        archives = {law: census_archive(law) if population == "census6" else None
                    for law in ("nae", "parity")}
        per_law = defaultdict(Counter)
        by_start[population] = []
        for c in chosen:
            began = time.monotonic()
            for law in ("nae", "parity"):
                score, differences, steps = replay_law(c, law, archives[law])
                per_law[law].update(score)
                diffs.extend(differences)
                smaller.extend(steps)
            by_start[population].append({"index": c.index, "seconds": round(time.monotonic() - began, 4)})
        scores[population] = per_law
    result = {"selection seed": SEED, "selection": (
        "Fixed pilot including a cap, a stall and a parity difference." if args.mode == "pilot" else
        "Per weighting, uniform sample of 12 completed growing tree or tree-plus starts or 28 growing census starts. "
        "Include all recorded parity misses, all 27 not-all-equal failures within t steps and all census stalls. "
        "Both laws on every selected start."),
        "growth": "Independent. The six-knot holdings are read from the earlier growth archives and the three "
                  "successive census draws reselected from integer indices. Tree and tree-plus starts, loose counts, "
                  "reader and all region draws are rebuilt from their weighting and seeds.",
        "memory limit bytes": MEMORY, "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "seconds": round(time.monotonic() - overall, 3),
        "checks": scores, "selected starts": by_start, "differing comparisons": diffs,
        "not-all-equal misses within t steps": smaller}
    (HERE / f"replay_{args.mode}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"by population": {p: len(v) for p, v in by_start.items()},
                      "seconds": result["seconds"], "differences": len(diffs), "peak KiB": result["peak resident KiB"]}))


if __name__ == "__main__":
    main()
