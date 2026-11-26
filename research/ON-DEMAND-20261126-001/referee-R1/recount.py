"""Recount the frozen comparison records without importing the producer or scorer."""

import argparse
import json
import statistics
from collections import Counter
from fractions import Fraction
from itertools import islice
from pathlib import Path


STUDY = Path(__file__).resolve().parent.parent
HORIZONS = {"tree40": 8, "treeplus25": 7, "census6": 10}
POPULATION_SIZES = {"tree40": 60, "treeplus25": 60, "census6": 400}
H1 = "H1 within t + 1 steps agrees"
SHORT = "within t steps agrees"
ENDS = "region ends where H1 differs"
PROVISIONAL = "births of the region not in the full growth, of all the region's births, at round t"
NEEDED = "births needed, of all births, through round t"
CAPS = "region growths stopped at the cap, not read"
CAP = 3000


def unique_keys(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), pairs
    return result


def records(path, limit):
    with path.open() as stream:
        return [json.loads(line, object_pairs_hook=unique_keys) for line in islice(stream, limit)]


def rounds(mapping):
    return {int(t): value for t, value in mapping.items()}


def region_kind(row, radius):
    if radius < row["eccentricity"]:
        return "omits knots inside reader piece"
    if row["live in the reader piece"] < row["live"]:
        return "whole reader piece, omits other knots"
    return "whole roster"


def omitted_bounds(row, radius):
    """One shortest route to a farthest knot bounds each side of the cut."""
    eccentricity = row["eccentricity"]
    outside = row["live"] - row["live in the reader piece"]
    if radius >= eccentricity:
        return outside, outside
    return outside + eccentricity - radius, row["live"] - radius - 1


def h2_checks(row, record, h1, cap_events, counts, score, failures):
    admission = None
    random_kept = 0
    for t, extra, agrees in record["H2"]:
        assert 1 <= t <= record["rounds read"], (row, t)
        base_kind = region_kind(row, t + 1)
        lo, hi = omitted_bounds(row, t + 1)
        if isinstance(extra, int):
            assert 0 <= extra <= hi and isinstance(agrees, bool), (row, t, extra)
            random_kept += 1
            if extra == 0:
                kind = "repeats H1 roster"
                assert agrees == h1[t], (row, t)
            elif extra == hi:
                kind = "whole roster forced by size"
                assert agrees, (row, t)
            elif base_kind != "omits knots inside reader piece":
                kind = "adds other pieces only, proper subset"
            elif extra > row["live"] - row["live in the reader piece"]:
                kind = "adds inside reader piece, proper subset" if extra < lo else "adds inside reader piece, may be whole roster"
            else:
                kind = "membership of additions unrecorded"
            counts[f"random / {kind}"] += 1
            score["agree" if agrees else "differ"] += 1
            if not agrees:
                failures.append([row["index"], t, "random", extra, extra == 0])
        else:
            assert extra == "admitted in three steps" and admission is None, row
            admission = t
            assert 1 + (t in h1) <= len(agrees) <= 2 + (t in h1), row
            assert all(isinstance(x, bool) for x in agrees) and agrees[-1], row
            counts["ordered reruns with readable t"] += 1
            counts[f"ordered reruns / {base_kind}"] += 1
            counts["ordered / final full roster"] += 1
            if t in h1:
                assert agrees[0] == h1[t], row
                counts["ordered / first repeats H1 roster"] += 1
                if not agrees[0]:
                    failures.append([row["index"], t, "first", 0, True])
            middle_read = len(agrees) == 2 + (t in h1)
            assert cap_events["H2 admitted", t] == 2 - (t in h1) - middle_read, row
            if middle_read:
                if hi < 2:
                    kind = "repeats H1 roster"
                    assert agrees[-2] == h1[t], row
                elif lo < 2:
                    kind = "may repeat H1 roster"
                elif base_kind != "omits knots inside reader piece":
                    kind = "adds other pieces only"
                elif lo // 2 > row["live"] - row["live in the reader piece"]:
                    kind = "adds inside reader piece"
                else:
                    kind = "adds knots, membership unrecorded"
                counts[f"ordered / middle {kind}"] += 1
                if not agrees[-2]:
                    failures.append([row["index"], t, "middle", lo // 2 if lo == hi else None, hi < 2])
            score.update("agree" if good else "differ" for good in agrees)
    random_capped = sum(n for (kind, _), n in cap_events.items() if kind == "H2")
    assert random_kept + random_capped <= 3, row
    if record["end"] != "cap":
        assert admission is not None and random_kept + random_capped == 3, row
    counts["random comparisons omitted at full cap"] += 3 - random_kept - random_capped
    counts["random comparisons omitted at region cap"] += random_capped
    counts["ordered comparisons omitted at full cap"] += 3 * (admission is None)
    counts["ordered comparisons omitted at region cap"] += sum(
        n for (kind, _), n in cap_events.items() if kind == "H2 admitted"
    )


def audit_population(population, rows, summary, saved):
    tally, births, shares, h1_failures = saved
    horizon = HORIZONS[population]
    assert len({row["index"] for row in rows}) == len(rows), population
    for row in rows:
        assert row["population"] == population, row
        assert isinstance(row["seconds"], (int, float)) and row["seconds"] >= 0, row
        if "not read" in row:
            assert population == "treeplus25" and row["not read"] in {"time", "memory"}, row
            tally[f"{population} / start not read / {row['not read']}"] += 1
            summary["starts not read"].append([row["index"], row["not read"]])
    readable = [row for row in rows if "not read" not in row]
    for law in ("nae", "parity"):
        full_ends, stalls, coverage, h2 = Counter(), Counter(), Counter(), Counter()
        h2_outcomes, h1_outcomes, short_outcomes = Counter(), Counter(), Counter()
        h2_failures, h1_starts, short_failures, ratios = [], [], [], []
        provisional_rounds = Counter()
        total_provisional = total_region_births = 0
        prefix = f"{population} / {law}"
        for row in readable:
            assert set(row["laws"]) == {"nae", "parity"}, row
            assert 0 <= row["eccentricity"] < row["live in the reader piece"] <= row["live"], row
            a = row["laws"][law]
            n = a["rounds read"]
            end = a["end"]
            assert end in {"rounds", "closed", "stall", "cap"}, row
            full_ends[end] += 1
            assert 0 <= n < horizon if end == "cap" else n == horizon, (row, law)
            if end == "stall":
                step = a["least steps whose knots stall"]
                if step is None:
                    assert row["live in the reader piece"] < row["live"], row
                    stalls["beyond the reader piece"] += 1
                else:
                    assert 1 <= step <= row["eccentricity"], row
                    stalls[f"seen within {step} steps"] += 1
                continue

            coverage["starts with full-growth comparisons"] += 1
            coverage["full-growth rounds omitted by cap"] += horizon - n
            scheduled = set(range(1, n + 1))
            h1, short, ends, provisional, needed = (rounds(a[key]) for key in (H1, SHORT, ENDS, PROVISIONAL, NEEDED))
            cap_events = Counter(map(tuple, a.get(CAPS, [])))
            assert all(t in scheduled and kind in {"H1", "H2", "H2 admitted"} for kind, t in cap_events), row
            assert scheduled - set(h1) == {t for kind, t in cap_events if kind == "H1"}, row
            assert set(short) <= set(h1) == set(provisional) == set(needed) <= scheduled, row
            assert all(isinstance(v, bool) for v in [*h1.values(), *short.values()]), row
            assert set(ends) == {t for t, agrees in h1.items() if not agrees}, row

            coverage["H1 t + 1 omitted by region cap"] += n - len(h1)
            coverage["H1 t omitted by region cap after t + 1 read"] += len(h1) - len(short)
            coverage["H1 t skipped when t + 1 capped"] += n - len(h1)
            prev_needed = prev_full = prev_t = 0
            failure_rounds = []
            for t in sorted(h1):
                good = h1[t]
                tag = "agree" if good else "differ"
                h1_outcomes[tag] += 1
                kind = region_kind(row, t + 1)
                coverage[f"H1 t + 1 / {kind} / {tag}"] += 1
                region_only, region_total = provisional[t]
                needed_total, full_total = needed[t]
                assert all(type(x) is int for x in (region_only, region_total, needed_total, full_total)), row
                assert 0 <= region_only <= region_total and 0 < needed_total <= full_total, row
                assert prev_needed <= needed_total and prev_full <= full_total <= prev_full + CAP * (t - prev_t), row
                coverage["numeric pairs checked"] += 2
                if t == prev_t + 1:
                    full_births = full_total - prev_full
                    assert region_total - region_only <= full_births, row
                    if kind == "whole roster":
                        assert (region_only, region_total) == (0, full_births) and good, row
                    if full_births == 0:
                        assert end == "closed" and needed_total == prev_needed, row
                        coverage["H1 t + 1 compared through padded full round"] += 1
                if population == "treeplus25":
                    assert region_total <= CAP, row
                if region_only:
                    provisional_rounds[kind] += 1
                total_provisional += region_only
                total_region_births += region_total
                if not good:
                    h1_failures.append([population, row["index"], law, row["reader"], t, ends[t]])
                    coverage[f"H1 terminal label on differing prefix / {ends[t]}"] += 1
                    coverage["H1 differs with birth at t" if region_total else "H1 differs after its last birth"] += 1
                    failure_rounds.append([t, ends[t], region_only, region_total, full_total - prev_full if t == prev_t + 1 else None])
                if t in short:
                    short_tag = "agree" if short[t] else "differ"
                    short_outcomes[short_tag] += 1
                    short_kind = region_kind(row, t)
                    coverage[f"H1 t / {short_kind} / {short_tag}"] += 1
                    if short_kind == "whole roster":
                        assert short[t], row
                    if not short[t]:
                        short_failures.append([row["index"], t, good, short_kind])
                prev_needed, prev_full, prev_t = needed_total, full_total, t

            if failure_rounds:
                first_false_t = failure_rounds[0][0]
                stable_piece = first_false_t + 1 >= row["eccentricity"]
                h1_starts.append({
                    "index": row["index"], "reader": row["reader"], "eccentricity": row["eccentricity"],
                    "live": row["live"], "piece": row["live in the reader piece"], "full end": end,
                    "first tested false has a complete reader piece": stable_piece,
                    "last true from the same roster": max(
                        (t for t in h1 if h1[t] and stable_piece and t + 1 >= row["eccentricity"]), default=None
                    ),
                    "rounds [t, region end, region-only names, region births, full births]": failure_rounds,
                })
            if needed:
                t = max(needed)
                need, all_births = needed[t]
                ratios.append((Fraction(need, all_births), row["index"], t, need, all_births))
                coverage["shares cut short by a region cap"] += t != n
            h2_checks(row, a, h1, cap_events, h2, h2_outcomes, h2_failures)

        for label, count in stalls.items():
            tally[f"{prefix} / stalls in round 1 / {label}"] = count
        for label, results in (("H1 (reader, round)", h1_outcomes), ("within t steps", short_outcomes),
                               ("H2 regions and admission steps", h2_outcomes)):
            for outcome, count in results.items():
                tally[f"{prefix} / {label} / {outcome}"] = count
        for key, count in coverage.items():
            if key.startswith("H1 terminal label on differing prefix / "):
                tally[f"{prefix} / H1 differs, region growth ends / {key.rsplit(' / ', 1)[1]}"] = count
        tally[f"{prefix} / starts read"] = coverage["starts with full-growth comparisons"]
        births[f"{prefix} / all"] = total_region_births
        births[f"{prefix} / provisional"] = total_provisional
        numeric = [float(entry[0]) for entry in ratios]
        if numeric:
            shares[prefix] = {"median": statistics.median(numeric), "least": min(numeric), "starts": len(numeric)}
        summary[law] = {
            "full ends": full_ends, "stall distances": stalls, "coverage": coverage,
            "H1 outcomes": h1_outcomes, "t-step outcomes": short_outcomes, "H2 outcomes": h2_outcomes,
            "H2 opportunities": h2,
            "H2 failed comparisons [index, t, stage, extras, same as H1]": h2_failures,
            "H1 false prefixes by start": h1_starts, "t-step false prefixes [index, t, H1 agree, region]": short_failures,
            "provisional births": {"region-only": total_provisional, "all region": total_region_births,
                                   "rounds with any by region": provisional_rounds},
            "share at last archived t": {"n": len(ratios), "all births needed": sum(x[0] == 1 for x in ratios),
                                         "median (exact)": str(statistics.median(r[0] for r in ratios)) if ratios else None,
                                         "upper middle recorded as median": sorted(numeric)[len(numeric) // 2] if numeric else None,
                                         "least [index, t, needed, all]": min(ratios)[1:] if ratios else None},
        }


def compare_score(actual, expected):
    if isinstance(expected, dict) and isinstance(actual, dict):
        errors = {}
        for key in sorted(actual.keys() | expected.keys()):
            difference = compare_score(actual.get(key), expected.get(key))
            if difference:
                errors[key] = difference
        return errors
    return {} if actual == expected else {"recounted": actual, "stored": expected}


def comparable_payload(row):
    """Exclude the elapsed time and the empty cap field added by the rerun."""
    copy = {k: v for k, v in row.items() if k not in {"seconds", "laws"}}
    copy["laws"] = {
        law: {key: value for key, value in cell.items() if key != CAPS or value}
        for law, cell in row["laws"].items()
    }
    return copy


def audit(limit=None):
    sample = {p: records(STUDY / f"results_{p}.jsonl", limit) for p in HORIZONS}
    if limit is None:
        assert {p: len(rows) for p, rows in sample.items()} == POPULATION_SIZES
        for p in ("tree40", "treeplus25"):
            assert [row["index"] for row in sample[p]] == list(range(POPULATION_SIZES[p])), p
    first = records(STUDY / "results_treeplus25_first_run.jsonl", limit)
    if limit is None:
        assert [row["index"] for row in first] == list(range(14))
    first_differences = [a["index"] for a, b in zip(first, sample["treeplus25"]) if comparable_payload(a) != comparable_payload(b)]
    summaries = {p: {"archive rows": len(rows), "starts not read": []} for p, rows in sample.items()}
    tally, births, shares, h1_failures = Counter(), {}, {}, []
    for p, rows in sample.items():
        audit_population(p, rows, summaries[p], (tally, births, shares, h1_failures))
    recomputed = {"tally": tally, "provisional births": births,
                  "share of births the view rests on, at the last round read": shares, "H1 differs": h1_failures}
    score = json.loads((STUDY / "score.json").read_text(), object_pairs_hook=unique_keys)
    return {
        "pilot maximum rows per archive": limit,
        "populations": summaries,
        "first run versus capped rerun": {"rows compared": len(first), "differing indices": first_differences},
        "saved score differences": None if limit is not None else compare_score(recomputed, score),
        "recounted score": recomputed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Read only this many rows of each archive for a pilot.")
    args = parser.parse_args()
    print(json.dumps(audit(args.limit), indent=2, sort_keys=True))
