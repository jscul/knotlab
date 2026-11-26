"""Recount both post-close records and test the effect of sampling a finite roster.

All inputs are saved records. The finite sum model and controls use only the
standard library. The model checks the proposed description independently of
the archived matching search. It does not regrow any start.
"""

import argparse
import gzip
import json
import re
import resource
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, islice
from math import comb
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parent.parent
ARCHIVE = ROOT / "artifacts" / (STUDY.name + "A")
RAW = ARCHIVE / (STUDY.name + "A-E001_knots_within_reach")
PROBE = STUDY / "checks/roster_probe"
LAWS = {
    "L0": "ordinary count",
    "L1": "cap of three with waiting",
    "L6": "cap of three with retiring",
    "L7": "cap of three with offshoots",
    "L9": "uncapped retiring",
    "L11": "cap of four with retiring",
}
ENVELOPE = "greatest count at each r (first 30)"
HIST = "neighbours within one step, by count of members"


def lines(path, limit=None):
    with gzip.open(path, "rt") as stream:
        for row in islice(stream, limit):
            yield json.loads(row)


def load(path):
    return json.loads(path.read_text())


def roster_tables(row):
    for key in ("at_T", "at_2T"):
        entry = row.get(key)
        if isinstance(entry, dict) and isinstance(entry.get("P"), dict):
            yield key, entry["round"], entry["P"]
    for key, value in row.items():
        if re.fullmatch(r"P_\d+", key) and isinstance(value, dict):
            yield key, row[key + "_round"], value


def formula(neighbours, r):
    if neighbours == 6:
        return 3 * r * (r + 1) + 1
    if neighbours == 12:
        return (2 * r + 1) * (5 * r * (r + 1) + 3) // 3
    if neighbours == 13:
        return 12 * r * r + 2 if r else 1
    if neighbours == 22:
        return 48 * r * (r - 1) + 24 if r >= 2 else (1, 23)[r]
    raise ValueError(neighbours)


def prefix(values, neighbours):
    return next((r - 1 for r, n in enumerate(values) if n != formula(neighbours, r)), len(values) - 1)


def square_bound(counts, first, last):
    ratios = [Fraction(counts[i], i * i) for i in range(first, last + 1)]
    return max(ratios) <= 2 * min(ratios)


def first_look(limit=None):
    readings = Counter()
    groups = defaultdict(list)
    labels = Counter()
    totals = Counter()
    extents = []
    candidate_sources = Counter()
    for row in lines(RAW / "run2.jsonl.gz", limit):
        for field, t, table in roster_tables(row):
            sources = table.get("counted_from", [])
            readings[f"{row['kind']} / {field}"] += len(sources)
            run = f"{row['start']} / {LAWS.get(row['law'], row['law'])} / round {t}"
            for origin in sources:
                counts = origin["P"]
                candidate_sources[run] += 1
                last = prefix(counts, 6)
                if last < 5:
                    continue
                groups[run].append(last)
                labels[origin["label"]] += 1
                extent = len(counts) - 1
                extents.append(extent)
                totals[f"matches under {LAWS[row['law']]}"] += 1
                totals["exact prefix contains at least ten values"] += last >= 9
                totals["can read r = 32"] += extent >= 32
                totals["would meet square bound on [4,32]"] += extent >= 32 and square_bound(counts, 4, 32)
                totals["would meet square bound on a final factor-eight range"] += any(
                    square_bound(counts, a, extent) for a in range(4, extent // 8 + 1)
                )
                totals["ever exceeds the polynomial after departing"] += any(
                    val > formula(6, r) for r, val in enumerate(counts[last + 1 :], start=last + 1)
                )
    comparison = {}
    for run, values in sorted(groups.items()):
        comparison[run] = {
            "sampled": candidate_sources[run], "matching": len(values), "last radii": sorted(values)
        }
    return {
        "all saved primary roster readings by row kind and field": readings,
        "stage and member samples": comparison,
        "matching observations": sum(map(len, groups.values())),
        "labels of matches": labels,
        "radii of farthest member among matches": [min(extents), max(extents)] if extents else [],
        "tests of matches": totals,
    }


def census_fast(limit=None):
    births = {}
    ordinary = 0
    for row in lines(RAW / "run1.jsonl.gz", limit):
        if row["law"] == "L0":
            ordinary += 1
            reading = row["births_reading"]
            if reading.get("verdict") == "POWER" and reading["j"] >= 2:
                births[row["start"]] = reading["j"]
    return ordinary, births


def roster_size(n, t):
    if n == 6:
        return comb(t + 1, 2) + 3
    if n == 12:
        return comb(t + 2, 3) + 4
    if n == 13:
        return 2 * t * (t - 1) + 4
    return 8 * t * (t - 3) + 27


def census_probe():
    rows = list(lines(PROBE / "probe_runs.jsonl.gz"))
    ordinary = {x["start"]: x for x in rows if x["law"] == "L0" and x["knot law"] == "nae"}
    family = {k: max(int(d) for d in v["stages"][0][HIST]) for k, v in ordinary.items()}
    start_count, fast = census_fast()
    published = set(load(PROBE / "fast_starts.json")["L0 fast"])
    count = Counter()
    split_cubic = Counter()
    parts = defaultdict(Counter)
    cohorts = defaultdict(list)
    ranges = defaultdict(dict)
    part_sizes = defaultdict(Counter)
    rounds2 = defaultdict(set)
    parity_match = {}
    whole_laws = {6: set(LAWS), 12: {"L0", "L9", "L11"}, 13: {"L0", "L9"}, 22: {"L0", "L9"}}
    for start, n in family.items():
        cohorts[n].append(int(start.split(":")[1]))
        rounds2[n].add(ordinary[start]["members per round"][2])
        fitted_from = 3 if n in (13, 22) else 1
        for t, m in enumerate(ordinary[start]["members per round"]):
            if t >= fitted_from:
                count["ordinary roster sizes checked against the family formula"] += 1
                count["ordinary roster size mismatches"] += m != roster_size(n, t)
    for x in rows:
        n, law = family[x["start"]], x["law"]
        if x["knot law"] == "parity":
            earlier = ordinary[x["start"]]
            stages = {st["round"]: st for st in earlier["stages"]}
            pairs = [(st, stages[st["round"]]) for st in x["stages"]]
            compared = (ENVELOPE, HIST, "members", "parts", "knots", "sources", "part sizes (largest 5)")
            parity_match[x["start"]] = {
                "number of members agrees at every reached round":
                    x["members per round"] == earlier["members per round"],
                "common saved stages": len(pairs),
                "saved summaries agree": all(a.get(k) == b.get(k) for a, b in pairs for k in compared),
            }
        for st in x["stages"]:
            t = st["round"]
            count["all stages"] += 1
            count["stages with sizes only"] += "sources" not in st
            if "sources" in st:
                censused = st["sources"] == st["of members in the part"]
                count["all members of largest part read" if censused else "sample of largest part read"] += 1
            whole = st["parts"] == 1
            parts[f"{n} other members within one step / {LAWS[law]} / {x['knot law']}"][str(st["parts"])] += 1
            count["whole or split disagrees with law table"] += whole != (law in whole_laws[n])
            if not whole:
                if n == 12:
                    split_cubic["split stages"] += 1
                    part_sizes[f"{LAWS[law]} / round {t}"][str(st["part sizes (largest 5)"])] += 1
                    if ENVELOPE in st:
                        split_cubic["stages with saved counts for the largest part"] += 1
                        size = st["part sizes (largest 5)"][0]
                        split_cubic["untruncated 2r+1 fails at a saved radius"] += any(
                            y != 2 * r + 1 for r, y in enumerate(st[ENVELOPE])
                        )
                        split_cubic["truncated formula mismatches"] += any(
                            y != min(2 * r + 1, size) for r, y in enumerate(st[ENVELOPE])
                        )
                continue
            expected = {6: (t - 1) // 3, 12: (t - 1) // 4, 13: (t - 2) // 3, 22: (t - 3) // 3}[n]
            last = prefix(st[ENVELOPE], n)
            count["one-part maxima checked"] += 1
            count["number of neighbours differs"] += max(map(int, st[HIST])) != n
            count["wrong exact prefix in one-part maximum"] += last != expected
            count["saved count exceeds polynomial after departing"] += any(
                y > formula(n, r) for r, y in enumerate(st[ENVELOPE])
            )
            if n == 6:
                expected_hist = {"1": 3, "3": 3, "4": 3*t - 6, "6": st["members"] - 3*t}
                count["six-neighbour degree histogram mismatches"] += expected_hist != st[HIST]
            if law == "L0" and x["knot law"] == "nae":
                ranges[n][t] = last
    return {
        "ordinary starts in registered first table": start_count,
        "starts with a fast births reading by exact degree": Counter(fast.values()),
        "selected cohort agrees in registered records, list and probe": set(ordinary) == set(fast) == published,
        "runs by law": Counter(f"{LAWS[x['law']]} / {x['knot law']}" for x in rows),
        "families identified by their ordinary one-step count, excluding the source": {
            k: sorted(v) for k, v in cohorts.items()
        },
        "round two members in the ordinary families": {k: sorted(v) for k, v in rounds2.items()},
        "last radius in the ordinary maximum by family and round": ranges,
        "stage counts": count, "part counts on saved stages": parts,
        "four-term family under cap three": split_cubic, "split part sizes": part_sizes,
        "parity comparison to ordinary not-all-equal": parity_match,
    }


def confirmation():
    second = load(PROBE / "confirm_second.json")
    knots = load(PROBE / "confirm_ktest.json")
    totals = Counter()
    for row in knots:
        for law in ("not-all-equal", "parity"):
            for field in ("tested", "failing", "methods disagreeing"):
                totals[f"{law} / {field}"] += row[law][field]
        totals["not-all-equal / untested in sample"] += row["not-all-equal"]["untested"]
        direct = row["not-all-equal"]["compared directly"]
        totals["not-all-equal / made knots also tested directly"] += direct
        totals["not-all-equal / runs comparing no made knot directly"] += direct == 0
        totals["parity / closures"] += row["parity"]["closing round"] is not None
    matching = load(PROBE / "model_check.json")
    return {
        "comparisons marked equal": sum(x["equal"] for x in second),
        "compared beyond numbers of knots and members": sum(x["every member read by the probe"] for x in second),
        "only numbers of knots and members compared": [
            [x["start"], x["round"]] for x in second if not x["every member read by the probe"]
        ],
        "knot-tested runs by law": Counter(LAWS[x["law"]] for x in knots),
        "knot sample": totals,
        "archived matching verdicts": Counter(str(x["the same up to renaming"]) for x in matching["matching"]),
        "larger starts with saved radius counts": [
            x["m"] for x in matching["touching starts"] if x["greatest count at each r"] is not None
        ],
    }


def sums(n, m):
    if m == 1:
        yield (n,)
        return
    for i in range(n + 1):
        for rest in sums(n - i, m - 1):
            yield (i, *rest)


def distances_from_sum(source, targets):
    """A move balances one excess against one deficit. An offshoot costs one extra step."""
    s = sum(source)
    hist = Counter(sum(max(a-b, 0) for a, b in zip(source, y)) for y in targets)
    hist.update(1 + s - a for a in source)
    return hist


def model_case(m, t, r):
    targets = list(sums(t - 1, m))
    types = Counter(tuple(sorted(p)) for p in targets)
    values = {}
    for p in types:
        dist = distances_from_sum(p, targets)
        values[p] = sum(n for d, n in dist.items() if d <= r)
    # From one offshoot first reach its concentrated sum, then use transfers.
    end = sum(y[0] >= t - r for y in targets) + 1 + (m-1) * (r >= t + 1)
    best = max(max(values.values()), end)
    winners = sum(n for p, n in types.items() if values[p] == best) + m * (end == best)
    next_count = max((val for val in [end, *values.values()] if val < best), default=None)
    result = {
        "m": m, "round": t, "radius": r, "members": len(targets) + m, "sum types by permutation": len(types),
        "true maximum": best, "maximizers": winners, "best count after excluding all maximizers": next_count,
        "count from an offshoot": end,
    }
    if (m, t, r) == (4, 30, 7):
        # Same finite roster, with every maximizing source in the omitted half.
        # Rotate its presentation by one position to exchange the two halves.
        below = sorted([values[tuple(sorted(p))] for p in targets if values[tuple(sorted(p))] < best] + [end] * m)
        half = result["members"] // 2
        first = below[-half:]
        second = below[:-half] + [best] * winners
        presented = [entry for pair in zip(first, second, strict=True) for entry in pair]
        result["stride-two maxima before and after one-position rotation"] = [
            max(presented[::2]), max(presented[1::2])
        ]
        result["stride-two sample size"] = half
    return result


def sum_model_records():
    published = load(PROBE / "model_check.json")
    matches = Counter()
    for row in published["matching"]:
        m, s = row["m"], row["round"] - 1
        members = comb(s + m - 1, m - 1) + m
        matches["archived stages with correct model size"] += row["members"] == members
        if "one-step pairs" in row:
            # Choose the positive entries and their values. Each positive
            # entry can supply one unit to m-1 other entries. Add the offshoots.
            transfer_degree_sum = sum(
                comb(m, k) * comb(s - 1, k - 1) * k * (m - 1) for k in range(1, min(s, m) + 1)
            )
            pairs = transfer_degree_sum // 2 + m
            matches["archived stages with correct model count of pairs"] += row["one-step pairs"] == pairs
    larger = []
    for row in published["touching starts"]:
        m, t = row["m"], row["rounds done"]
        q, k = divmod(t - 1, m)
        source = (q,) * (m - k) + (q + 1,) * k
        targets = list(sums(t - 1, m))
        hist = distances_from_sum(source, targets)
        cumulative = []
        total = 0
        for d in range(max(hist) + 1):
            total += hist[d]
            cumulative.append(total)
        archive = row["greatest count at each r"]
        n_by_round = [row["m"]] + [comb(j + m - 2, m - 1) + m for j in range(1, len(row["members per round"]))]
        larger.append({
            "m": m, "round": t, "early model sizes agree": n_by_round == row["members per round"],
            "terminal model size agrees": len(targets) + m == row["members"],
            "one-step maximum agrees": cumulative[1] - 1 == row["most within one step"],
            "balanced sum counts at radii zero through nine": cumulative[:10],
            "saved radius counts agree": cumulative[:len(archive)] == archive if archive is not None else None,
        })
    model_extensions = []
    for m, r in ((5, 4), (6, 2)):
        t = m * r + 1
        hist = distances_from_sum((r,) * m, sums(t - 1, m))
        model_extensions.append({
            "m": m, "round": t,
            "counts from equal terms": [sum(hist[i] for i in range(j + 1)) for j in range(r + 1)],
        })
    boundary = distances_from_sum((1, 1, 1), sums(3, 3))
    return {
        "saved isomorphism claims checked here by size and, where available, pair count": matches,
        "comparison of larger archived starts to direct counts of the described model": larger,
        "later rounds of the model only": model_extensions,
        "three-term round-four member reaches a member with only four neighbours at one step": {
            "source": [1, 1, 1], "reachable member": [2, 1, 0],
            "counts at radii zero through two": [sum(boundary[j] for j in range(i+1)) for i in range(3)],
        },
    }


def restricted_histograms(s, extras):
    """Enumerate the dense finite model by source type, retaining every target.

    The three unrestricted entries and the extra zero-or-one entries have
    fixed sum s. Distances count the units present at the source that must
    move. Each of the three additional offshoots costs one further step.
    """
    targets = {b: list(sums(s - b, 3)) for b in range(extras + 1)}
    for h, sources in targets.items():
        for origin in sorted({tuple(sorted(v)) for v in sources}):
            result = Counter()
            a, b, c = origin
            for h2, destinations in targets.items():
                costs = Counter(max(a-x, 0) + max(b-y, 0) + max(c-z, 0) for x, y, z in destinations)
                for overlap in range(max(0, h2 - extras + h), min(h, h2) + 1):
                    copies = comb(h, overlap) * comb(extras - h, h2 - overlap)
                    for d, n in costs.items():
                        result[d + h - overlap] += copies * n
            result.update(1 + s - a for a in origin)
            yield (origin, h), result


def model_maxima(n, t):
    s = t - 1
    if n in (13, 22):
        histograms = restricted_histograms(s, {13: 2, 22: 4}[n])
    else:
        m = {6: 3, 12: 4}[n]
        targets = list(sums(s, m))
        types = sorted({tuple(sorted(x)) for x in targets})
        histograms = ((x, distances_from_sum(x, targets)) for x in types)
    # Every positive-radius count from an offshoot is bounded by the count
    # from its only neighbour. At zero all origins tie.
    maxima = [0] * (t + 2)
    attaining = [set() for _ in maxima]
    for origin, hist in histograms:
        value = 0
        for r, best in enumerate(maxima):
            value += hist[r]
            if value > best:
                maxima[r] = value
                attaining[r] = {origin}
            elif value == best:
                attaining[r].add(origin)
    disjoint = next(([r, q] for q in range(1, len(maxima)) for r in range(1, q)
                     if not attaining[r] & attaining[q]), None)
    return maxima, bool(set.intersection(*attaining)), disjoint


def compare_saved_maxima():
    models = {}
    count = Counter()
    discrepancies = []
    for row in lines(PROBE / "probe_runs.jsonl.gz"):
        for stage in row["stages"]:
            if stage["parts"] != 1:
                continue
            n, t = max(map(int, stage[HIST])), stage["round"]
            if (n, t) not in models:
                models[n, t] = model_maxima(n, t)
            maxima, _, _ = models[n, t]
            actual = stage[ENVELOPE]
            missed = [r for r, v in enumerate(actual) if v != maxima[r]]
            full = stage["sources"] == stage["members"]
            weight = "all members" if full else "sample of members"
            count[f"compared / {weight}"] += 1
            count[f"all saved radii match / {weight}"] += not missed
            if missed:
                discrepancies.append({"start": row["start"], "law": LAWS[row["law"]], "knot law": row["knot law"],
                                      "round": t, "family neighbours": n, "source count": stage["sources"],
                                      "members": stage["members"], "differing counts": [
                                          {"r": r, "sample maximum": actual[r], "model maximum": maxima[r]}
                                          for r in missed
                                      ], "largest shortfall": max(maxima[r] - actual[r] for r in missed)})
    by_stage = {f"{n} neighbours, round {t}": {"one member realizes every maximum": all_r,
                                                "disjoint maximizing member types at radii": pair}
                for (n, t), (_, all_r, pair) in sorted(models.items())}
    return {"compared one-part records": count, "discrepancies": discrepancies,
            "finite models by stage": by_stage}


def dense_control(extra_places):
    """Construct the complete finite relation at round ten, then read each member literally."""
    s = 9
    points = [(*x, mask) for mask in range(1 << extra_places) for x in sums(s - mask.bit_count(), 3)]
    adj = [set() for _ in range(len(points) + 3)]
    for i, (a, b, c, h) in enumerate(points):
        for j in range(i):
            x, y, z, k = points[j]
            if abs(a-x) + abs(b-y) + abs(c-z) + (h^k).bit_count() == 2:
                adj[i].add(j)
                adj[j].add(i)
        if max(a, b, c) == s:
            end = len(points) + (a, b, c).index(s)
            adj[end].add(i)
            adj[i].add(end)
    counts = []
    for start in range(len(adj)):
        reached = {start}
        for _ in range(3):
            reached |= set().union(*(adj[u] for u in reached))
        counts.append((1 + len(adj[start]), len(reached)))
    r1 = max(i for i, _ in counts)
    r3 = max(j for _, j in counts)
    return {"round": 10, "members": len(adj), "extra zero-or-one places": extra_places,
            "r1 maximum": r1, "r3 maximum": r3, "maximizers at r1": sum(i == r1 for i, _ in counts),
            "maximizers at r3": sum(j == r3 for _, j in counts),
            "common maximizers at r1 and r3": counts.count((r1, r3))}


def aggregate_control():
    """Both six-element relations share every rooted count but have different one-step relations."""
    pairs = [(a,b) for a in range(3) for b in range(3,6)]
    other = list(combinations(range(3),2)) + list(combinations(range(3,6),2)) + [(a,a+3) for a in range(3)]
    out = []
    for connections in (pairs, other):
        adj = {u: set() for u in range(6)}
        for a, b in connections:
            adj[a].add(b)
            adj[b].add(a)
        rooted = []
        for u in adj:
            reached = {u}
            counts = [1]
            while len(reached) != 6:
                reached |= set().union(*(adj[a] for a in reached))
                counts.append(len(reached))
            rooted.append(counts)
        triples = sum(b in adj[a] and c in adj[a] and c in adj[b] for a,b,c in combinations(range(6), 3))
        out.append({"all rooted counts": rooted, "mutually adjacent triples": triples})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    cap = 1_750_000 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    if args.pilot:
        before = perf_counter()
        timing_raw = first_look(8)
        timing_births = census_fast(10)
        seconds_records = perf_counter() - before
        before = perf_counter()
        timed_model = model_case(4, 15, 3)
        dense = model_maxima(22, 10)
        print(json.dumps({"eight roster and ten birth rows, seconds": seconds_records,
                          "readings": sum(timing_raw["all saved primary roster readings by row kind and field"].values()),
                          "ordinary rows": timing_births[0], "model": timed_model,
                          "dense model, maximum at two": dense[0][2], "model seconds": perf_counter() - before}))
        return
    out = {"first look": first_look(), "probe": census_probe(), "checks": confirmation(), "finite model": sum_model_records(),
           "full saved radius sequences against finite models": compare_saved_maxima(),
           "literal origin check of the dense round-ten models": [dense_control(2), dense_control(4)],
           "four-term roster, stride-two sampling control": model_case(4, 30, 7),
           "two one-step relations with the same counts": aggregate_control()}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
