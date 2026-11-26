"""Test whether the frozen offsets add information to simpler readings of the same births."""

import argparse
import gzip
import json
import math
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import islice
from pathlib import Path


STUDY = Path(__file__).resolve().parents[1]
READINGS = ("without parent descriptions", "with parent descriptions")
COARSE = ("total", "join or offshoot", "parent count", "fresh distinctions", "places")


def differences(counts):
    return [b - a for a, b in zip(counts, counts[1:])]


def measure(rounds, dimension):
    """The last nonzero Dth difference ends at the earliest unrestricted cut.

    If it ends at round j, round j-D is the last round outside the eventual
    polynomial, and j-D+1 is the first round in the final polynomial sequence.
    """
    by_kind = defaultdict(lambda: [0] * len(rounds))
    for i, row in enumerate(rounds):
        for kind, count in row.items():
            by_kind[kind][i] = count
    last = 0
    for counts in by_kind.values():
        for _ in range(dimension):
            counts = differences(counts)
        last = max(last, max((dimension + i + 1 for i, c in enumerate(counts) if c), default=0))
    first = last - dimension + 1 if last else 1
    return {"cut": max(3, dimension, last), "first round in final polynomial sequence": first}


def last_fall(counts):
    return max((t for t, (a, b) in enumerate(zip(counts, counts[1:]), 2) if b < a), default=1)


def first_trough(counts):
    """First strict fall followed by an equal or greater count in the next round."""
    return next((t for t, (a, b, c) in enumerate(zip(counts, counts[1:], counts[2:]), 2)
                 if a > b <= c), None)


def read(row):
    counts = tuple(r["n"] for r in row["rows"])
    if len(counts) != 24 or not row["kind"].startswith("dim "):
        return None
    dimension = int(row["kind"].split()[1])
    records = {key: [] for key in (*COARSE, *READINGS)}
    records["total"] = [{"all births": n} for n in counts]
    for r in row["rows"]:
        fine = {repr(kind): n for kind, n in r["sig1"]}
        without = {}
        pieces = [Counter() for _ in range(4)]
        for kind, n in r["sig0"]:
            without[tuple(kind)] = n
            for c, value in zip(pieces, kind):
                c[value] += n
        for key, c in zip(COARSE[1:], pieces):
            records[key].append(c)
        assert sum(without.values()) == sum(fine.values()) == r["n"]
        records[READINGS[0]].append(without)
        records[READINGS[1]].append(fine)
    views = {key: measure(v, dimension) for key, v in records.items()}
    for view, offset in zip(READINGS, (3, 5)):
        v = records[view]
        seen = set()
        for t, kinds in enumerate(v, 1):
            if kinds.keys() - seen:
                views[view]["last first appearance of a kind"] = t
                seen.update(kinds)
        cut = views[view]["cut"]
        views[view]["late"] = cut > row["M"] + offset + 2
        views[view]["checkable"] = cut <= min(24 - dimension, len(counts) - 2)
    return {"index": row["index"], "D": dimension, "M": row["M"], "T": last_fall(counts),
            "counts": counts, "first count": counts[0],
            "first view": tuple(sorted(records[READINGS[0]][0].items())), "views": views}


def hist(values):
    return dict(sorted(Counter(values).items()))


def example(s):
    return {key: s[key] for key in ("index", "D", "M", "T", "counts")} | {
        "cuts": {name: v["cut"] for name, v in s["views"].items()}}


def permutation(starts, strata, view, offset):
    """Exact reassignment of T among selected starts, equally over permutations in each group."""
    groups = defaultdict(list)
    for s in starts:
        groups[tuple(s[key] for key in strata)].append(s)
    matches = Fraction()
    within = Fraction()
    all_match = Fraction(1)
    for group in groups.values():
        n = len(group)
        values = Counter(s["T"] for s in group)
        pred = Counter(s["views"][view]["cut"] - offset for s in group)
        matches += Fraction(sum(cnt * values[k] for k, cnt in pred.items()), n)
        within += Fraction(sum(c * d for k, c in pred.items() for t, d in values.items() if k <= t), n)
        all_match *= (Fraction(math.prod(math.factorial(i) for i in values.values()), math.factorial(n))
                      if pred == values else 0)
    return {"groups": len(groups), "mean exact matches": str(matches), "mean combined passes among late": str(within),
            "fraction of permutations matching all selected cuts": str(all_match)}


def different_cuts(starts, view, identical_counts):
    groups = defaultdict(list)
    for s in starts:
        key = (s["D"], s["M"], s["T"], s["counts"] if identical_counts else s["counts"][0])
        groups[key].append(s)
    mixed = [g for g in groups.values() if len({s["views"][view]["cut"] for s in g}) > 1]
    ordered = [sorted(g, key=lambda s: (s["views"][view]["cut"], s["index"])) for g in mixed]
    ordered.sort(key=lambda g: (-(g[-1]["views"][view]["cut"] - g[0]["views"][view]["cut"]), g[0]["index"]))
    return {"groups": len(groups), "groups with different cuts": len(mixed),
            "starts in those groups": sum(map(len, mixed)),
            "witness pair with widest difference": [example(s) for s in (ordered[0][0], ordered[0][-1])] if mixed else []}


def comparison(starts, view, offset):
    check = [s for s in starts if s["views"][view]["checkable"]]
    late = [s for s in check if s["views"][view]["late"]]
    out = {"checkable": len(check), "late": len(late), "late details": [example(s) for s in late]}
    for name, group in (
            ("all", check), ("all with a strict fall", [s for s in check if s["T"] > 1]),
            ("all without a strict fall", [s for s in check if s["T"] == 1]), ("late only", late)):
        def delta(key):
            return hist(s["views"][view]["cut"] - s["views"][key]["cut"] for s in group)
        out[name] = {
            "size": len(group),
            "dimensions": hist(s["D"] for s in group),
            "K minus T": hist(s["views"][view]["cut"] - s["T"] for s in group),
            "K minus M": hist(s["views"][view]["cut"] - s["M"] for s in group),
            "first round in final polynomial sequence minus T":
                hist(s["views"][view]["first round in final polynomial sequence"] - s["T"] for s in group),
            "K minus cut for simpler readings": {key: delta(key) for key in COARSE},
            "K minus last first appearance of a kind":
                hist(s["views"][view]["cut"] - s["views"][view]["last first appearance of a kind"] for s in group),
            "K equals first global minimum round plus offset":
                sum(s["views"][view]["cut"] == s["counts"].index(min(s["counts"])) + 1 + offset for s in group),
            "K equals the first trough round plus offset":
                sum(s["views"][view]["cut"] - offset == first_trough(s["counts"]) for s in group),
            "T exceeds M plus two": sum(s["T"] > s["M"] + 2 for s in group),
            "bound strictly below largest checkable cut":
                sum(max(s["T"] + offset, s["M"] + offset + 2) < min(22, 24 - s["D"]) for s in group)}
    out["late inputs"] = {
        "T": hist(s["T"] for s in late),
        "T minus M minus two": hist(s["T"] - s["M"] - 2 for s in late),
        "births in round T": hist(s["counts"][s["T"] - 1] for s in late),
        "distinct count sequences": len({s["counts"] for s in late}),
        "late selections permitting an earlier checkable cut inside the combined bound":
            sum(s["T"] + offset > s["M"] + offset + 3 for s in late),
        "T reassigned among all late starts": permutation(late, [], view, offset),
        "T reassigned among late starts of the same dimension and M": permutation(late, ["D", "M"], view, offset),
        "T reassigned among late starts with the same D, M and first count":
            permutation(late, ["D", "M", "first count"], view, offset),
        "T reassigned among late starts with the same D, M and first view without parent descriptions":
            permutation(late, ["D", "M", "first view"], view, offset),
    }
    out["same D, M, T and first count"] = different_cuts(check, view, False)
    out["same D, M, T and every count"] = different_cuts(check, view, True)
    over = [s for s in check if s["views"][view]["cut"] > s["T"] + offset]
    out["largest miss for T alone"] = (example(max(over, key=lambda s: s["views"][view]["cut"] - s["T"]))
                                       if over else None)
    out["strict falls with K above T plus offset"] = [example(s) for s in over if s["T"] > 1]
    return out


def arithmetic_control(j, h, fall=6):
    counts = [4] * (fall - 1) + list(range(2, 27 - fall))
    coarse, fine = [], []
    for r, n in enumerate(counts, 1):
        b = 1 + (r == j)
        coarse.append({"A": n - b, "B": b})
        fine.append({"A1": n - b - (r == h), "A2": int(r == h), "B1": b})
    for n, c, f in zip(counts, coarse, fine):
        assert sum(c.values()) == sum(f.values()) == n
        assert c["A"] == f["A1"] + f["A2"] and c["B"] == f["B1"] and min(f.values()) >= 0
    t, m, d = last_fall(counts), 3, 2
    return {"M": m, "T": t, "D": d, "counts": counts, "round of extra B": j, "round of different A description": h,
            "cuts": [measure(v, d) for v in (coarse, fine)],
            "bounds": [max(m + gap + 2, t + gap) for gap in (3, 5)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="archive rows per law, in saved order")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    began = time.perf_counter()
    out = {"archive prefix per law": args.limit,
           "index": "Position of the six-knot start in the census up to renaming.",
           "method": "Exact integer differences by kind. The earliest cut permits at least two subsequent saved rounds. "
                     "First round in the final polynomial sequence is the beginning of agreement with the final fit. "
                     "All comparisons here use the completed runs. The reassignment gives equal weight to each permutation of observed T in its group.",
           "arithmetic controls": {"scope": "Abstract birth counts with a refinement by descriptions, with no claim of realizable growth.",
                                   "pass": arithmetic_control(7, 9), "break both predictions": arithmetic_control(8, 10),
                                   "break only the equality": arithmetic_control(7, 9, fall=7)}}
    for law in ("nae", "parity"):
        starts = []
        with gzip.open(STUDY / f"grown_fresh_{law}.jsonl.gz", "rt") as f:
            for raw in islice(f, args.limit):
                s = read(json.loads(raw))
                if s is not None:
                    starts.append(s)
        out[law] = {v: comparison(starts, v, off) for v, off in zip(READINGS, (3, 5))}
        both = [s for s in starts if all(s["views"][v]["checkable"] for v in READINGS)]
        late = [s for s in both if s["views"][READINGS[0]]["late"] or s["views"][READINGS[1]]["late"]]
        out[law]["parent reading minus reading without parent descriptions"] = {
            name: hist(s["views"][READINGS[1]]["cut"] - s["views"][READINGS[0]]["cut"] for s in group)
            for name, group in [("both checkable", both), ("late in either", late)]}
    out["elapsed seconds"] = round(time.perf_counter() - began, 4)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(f"{args.output.name}: {out['elapsed seconds']} seconds")


if __name__ == "__main__":
    main()
