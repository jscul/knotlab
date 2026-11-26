"""Reconstruct each pair forecast from the saved birth counts and frozen cuts."""

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import gzip
from itertools import combinations, islice, pairwise
import json
from math import comb
from pathlib import Path
import resource
import time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PRIOR = STUDY.parent / "LOOK-ALIKE-20261126-001"
READINGS = {"sig0": 5, "sig1": 7}
COMPARISONS = {"archived sparse": 1, "signed with absent kinds zero": 2, "negative counts replaced by zero": 4}


def immutable(value):
    return tuple(map(immutable, value)) if isinstance(value, list) else value


def dimension(totals):
    if len(totals) < 10:
        return None
    differences = totals[-8:]
    for d in range(1, 5):
        if differences[0] > 0 and len(set(differences)) == 1:
            return d
        differences = [b - a for a, b in pairwise(differences)]
    return None


def bound_input(start):
    knots = [set(holding) for holding in start["stars"]]
    frequency = Counter(distinction for knot in knots for distinction in knot)
    live = [knot for knot in knots if any(frequency[d] == 1 for d in knot)]
    neighbours = max(sum(knot is not other and bool(knot & other) for other in live) for knot in knots)
    first_row = start["rows"][0]["sig0"] if start["rows"] else ()
    fresh = max((label[2] for label, _ in first_row), default=0)
    return max(neighbours, fresh)


def settling(rows, d):
    # A cut works exactly when all later Dth differences vanish for every kind.
    k = max(d, 3)
    for label in set().union(*rows):
        differences = [row.get(label, 0) for row in rows]
        for _ in range(d):
            differences = [b - a for a, b in pairwise(differences)]
        k = max(k, max((i for i, value in enumerate(differences, d + 1) if value), default=0))
    return k if k <= len(rows) - 2 else None


def forecast(rows, d, cut):
    if len(rows) <= cut + 1:
        return ()
    # The Newton basis evaluates every coefficient using only integers.
    window = rows[cut - d:cut]
    result = rows[:cut] + [{} for _ in rows[cut:]]
    for label in set().union(*window):
        differences = [row.get(label, 0) for row in window]
        coefficients = []
        while differences:
            coefficients.append(differences[0])
            differences = [b - a for a, b in pairwise(differences)]
        for offset, row in enumerate(result[cut:], d):
            count = sum(comb(offset, order) * value for order, value in enumerate(coefficients))
            if count:
                row[label] = count
    return result


class RoundCounts:
    def __init__(self):
        self.ids = {}
        self.counts = []
        self.compare = lru_cache(maxsize=65_536)(self._compare)

    def intern(self, rows):
        ids = []
        for row in rows:
            key = frozenset(row.items())
            if key not in self.ids:
                self.ids[key] = len(self.counts)
                self.counts.append(row)
            ids.append(self.ids[key])
        return tuple(ids)

    def nested(self, a, b, comparison):
        if a == b:
            return True
        left, right = (a, b) if a < b else (b, a)
        return bool(self.compare(left, right) & comparison)

    def _compare(self, left, right):
        a, b = self.counts[left], self.counts[right]
        a_larger = any(count > b.get(label, 0) for label, count in a.items())
        b_larger = any(count > a.get(label, 0) for label, count in b.items())
        result = int(not (a_larger and b_larger))
        keys = a.keys() | b.keys()
        diff = [a.get(k, 0) - b.get(k, 0) for k in keys]
        if min(diff) >= 0 or max(diff) <= 0:
            result |= 2
        diff = [max(a.get(k, 0), 0) - max(b.get(k, 0), 0) for k in keys]
        if min(diff) >= 0 or max(diff) <= 0:
            result |= 4
        return result

    def onset(self, a, b, n, comparison):
        for i in range(n - 1, -1, -1):
            if not self.nested(a[i], b[i], comparison):
                return i + 2 if i < n - 1 else None
        return 1


@dataclass
class View:
    observed: tuple
    projected: tuple
    cut: int
    k: int | None
    first_mismatch: int
    first_negative: int
    dimension_at_cut: int | None

    @property
    def late(self):
        return self.k is None or self.k > self.cut


@dataclass
class Start:
    index: int
    knots: list
    dimension: int
    n: int
    m: int
    views: dict


def read_starts(path, counts):
    starts = []
    kinds = Counter()
    diagnostics = {r: Counter() for r in READINGS}
    negative_examples = {}
    with gzip.open(path, "rt") as stream:
        for x in map(json.loads, stream):
            m = bound_input(x)
            assert m == x["M"]
            totals = [row["n"] for row in x["rows"]]
            d = None if x["end"].startswith(("closes", "stalls")) else dimension(totals)
            assert (f"dim {d}" == x["kind"] if d else not x["kind"].startswith("dim"))
            kinds[x["kind"]] += 1
            if not d:
                continue
            n = len(totals)
            views = {}
            for reading, slack in READINGS.items():
                observed = [{immutable(label): count for label, count in row[reading]} for row in x["rows"]]
                assert all(len(counts) == len(row[reading]) and all(value > 0 for value in counts.values())
                           and sum(counts.values()) == row["n"] for counts, row in zip(observed, x["rows"]))
                k = settling(observed, d)
                cut = m + slack
                projected = forecast(observed, d, cut)
                first_change = next((i for i, (a, b) in enumerate(zip(observed, projected), 1) if a != b), n + 1)
                negative = [(i, label, count) for i, row in enumerate(projected, 1)
                            for label, count in row.items() if count < 0]
                if negative:
                    diagnostics[reading]["starts with negatives"] += 1
                    diagnostics[reading]["start-rounds with negatives"] += len({i for i, _, _ in negative})
                    diagnostics[reading]["negative birth-kind counts"] += len(negative)
                    least = min(negative, key=lambda hit: (hit[2], hit[0], hit[1]))
                    if least[2] < diagnostics[reading]["lowest extrapolated count"]:
                        diagnostics[reading]["lowest extrapolated count"] = least[2]
                        negative_examples[reading] = {
                            "start index": x["index"], "knots": x["stars"], "dimension": d, "cut": cut,
                            "settles": k, "round": least[0], "birth kind": least[1], "predicted count": least[2],
                            "observed count": observed[least[0] - 1].get(least[1], 0),
                            "fit counts": [row.get(least[1], 0) for row in observed[cut - d:cut]],
                        }
                view = View(counts.intern(observed), counts.intern(projected), cut, k, first_change,
                            negative[0][0] if negative else n + 1, dimension(totals[:cut]))
                if projected:
                    assert view.late == (first_change <= n)
                views[reading] = view
            starts.append(Start(x["index"], x["stars"], d, n, m, views))
    return starts, kinds, diagnostics, negative_examples


def prior_burst(starts):
    # Those starts exceeded the predecessor's fixed cut in both readings.
    burst = [s for s in starts if s.views["sig0"].k > 12 and s.views["sig1"].k > 14]
    saved = json.loads((PRIOR / "phase2.json").read_text())["unsettled or late"]
    assert {s.index for s in burst} == {row[0] for row in saved}
    assert len(burst) == 7
    assert all((s.dimension, s.m, s.views["sig0"].k, s.views["sig1"].k) == (2, 10, 14, 16) for s in burst)
    assert all(not view.late and view.first_mismatch > s.n for s in burst for view in s.views.values())
    return {s.index: s.knots for s in burst}


def score_pairs(starts, counts, burst, limit):
    tallies = {r: {} for r in READINGS}
    onsets = {r: Counter() for r in READINGS}
    excluded = {r: Counter() for r in READINGS}
    archive_counts = Counter()
    archive_misses = []
    examples = {}
    pairs = ((a, b) for a, b in combinations(starts, 2) if a.dimension == b.dimension)
    for a, b in islice(pairs, limit):
        n = min(a.n, b.n)
        burst_count = (a.index in burst) + (b.index in burst)
        for reading in READINGS:
            va, vb = a.views[reading], b.views[reading]
            late = va.late + vb.late
            groups = ["all", f"{late} late"]
            if burst_count:
                groups.extend(["prior burst / all", f"prior burst / {burst_count} burst starts / {late} late"])
            rows = [tallies[reading].setdefault(group, Counter()) for group in groups]
            common = n - max(va.cut, vb.cut)
            if common < 2:
                for row in rows:
                    row["excluded"] += 1
                excluded[reading][f"dimension {a.dimension}, {common} common rounds past both cuts"] += 1
                archive_counts[f"{reading} / not testable: too few rounds past the cut"] += 1
                continue

            observed = counts.onset(va.observed, vb.observed, n, COMPARISONS["signed with absent kinds zero"])
            forecast_differs = min(va.first_mismatch, vb.first_mismatch) <= n
            negatives = min(va.first_negative, vb.first_negative) <= n
            outcomes = [counts.onset(va.projected, vb.projected, n, variant)
                        for variant in COMPARISONS.values()] if negatives else [
                            counts.onset(va.projected, vb.projected, n, COMPARISONS["signed with absent kinds zero"])
                        ] * len(COMPARISONS)
            sparse, signed, clipped = outcomes
            archived_miss = sparse != observed
            assert not archived_miss or forecast_differs
            archive_counts[f"{reading} / {'missed' if archived_miss else 'predicted'}"] += 1
            if archived_miss and len(archive_misses) < 200:
                archive_misses.append([a.index, b.index, reading, observed, sparse])
            onsets[reading][(observed, sparse, signed, clipped)] += 1

            updates = {"tested": 1, "wrong count within common rounds": forecast_differs,
                       "negative forecast in common rounds": negatives,
                       "archived sparse misses": archived_miss,
                       "signed with absent kinds zero misses": signed != observed,
                       "negative counts replaced by zero misses": clipped != observed,
                       "signed onset differs from archived": signed != sparse,
                       "clipped onset differs from archived": clipped != sparse,
                       "valid archived sparse misses": archived_miss and not negatives,
                       "invalid forecasts judged right in archive": negatives and not archived_miss,
                       "invalid forecasts judged wrong in archive": negatives and archived_miss,
                       "completed dimension unavailable or different at either cut":
                           va.dimension_at_cut != a.dimension or vb.dimension_at_cut != b.dimension}
            updates = {name: int(value) for name, value in updates.items()}
            for row in rows:
                row.update(updates)
            for label, alternative in (("signed", signed), ("clipped", clipped)):
                key = f"{reading} / {label} / {'changes verdict' if (alternative == observed) != (sparse == observed) else 'changes onset only'}"
                if sparse != alternative and key not in examples:
                    round_index = max(n if value is None else value - 1 for value in (sparse, alternative)) - 1
                    examples[key] = {"starts": [{"index": s.index, "knots": s.knots, "cut": v.cut, "settles": v.k}
                                                 for s, v in ((a, va), (b, vb))],
                                     "dimension": a.dimension, "common horizon": n,
                                     "onsets": dict(zip(("observed", *COMPARISONS), (observed, *outcomes))),
                                     "last round where the two onsets force different nesting": round_index + 1,
                                     "forecast counts in that round": [sorted(counts.counts[v.projected[round_index]].items())
                                                                        for v in (va, vb)]}
    return tallies, onsets, excluded, archive_counts, archive_misses, examples


def recount(path, output_key, limit):
    before = time.monotonic()
    counts = RoundCounts()
    starts, kinds, diagnostics, negative_examples = read_starts(path, counts)
    burst = prior_burst(starts) if output_key == "g5_nae" else {}
    prepared = time.monotonic()
    tallies, onsets, excluded, archive_counts, archive_misses, examples = score_pairs(starts, counts, burst, limit)
    compared = time.monotonic()
    comparison = {}
    if limit is None:
        saved = json.loads((STUDY / f"test_{output_key}.json").read_text())
        assert len(starts) == saved["starts of a dimension"]
        assert archive_counts == saved["pairs"], (output_key, archive_counts, saved["pairs"])
        assert archive_misses == saved["pair misses (first 200)"]
        comparison = {"all archived tallies agree": True, "archived miss records matched in order": len(archive_misses)}
    return {"start counts by kind": kinds, "horizons of dimension starts": Counter(s.n for s in starts),
            "counts by reading": tallies,
            "onset counts by reading": {r: [[*key, value] for key, value in table.items()] for r, table in onsets.items()},
            "excluded pairs by common rounds beyond the later cut": excluded, "archived totals": archive_counts,
            "archive comparison": comparison, "first archived misses": archive_misses,
            "negative forecast counts by reading": diagnostics, "lowest negative examples": negative_examples,
            "examples where a comparison convention changes a predicted onset": examples,
            "prior seven bursting starts by index and knot holdings": burst,
            "seconds to parse and fit": round(prepared - before, 3), "seconds to compare pairs": round(compared - prepared, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=int, metavar="PAIRS", help="prefix of same-dimension pairs in each run")
    args = parser.parse_args()
    answer = {"pilot pair cap per population": args.pilot,
              "onset columns": ["observed", *COMPARISONS, "pair count"], "populations": {}}
    for key in ("g5_nae", "g5_par", "g6_nae", "g6_par"):
        result = recount(STUDY / f"grown_{key}.jsonl.gz", key, args.pilot)
        answer["populations"][key] = result
        print(key, dict(result["archived totals"]), "pair comparison seconds", result["seconds to compare pairs"], flush=True)
    answer["peak resident KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    path = HERE / ("pairs_pilot.json" if args.pilot is not None else "pairs.json")
    path.write_text(json.dumps(answer, indent=1) + "\n")


if __name__ == "__main__":
    main()
