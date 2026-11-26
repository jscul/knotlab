"""Recount the recorded pair comparisons with exact multiset and polynomial arithmetic."""

import argparse
from collections import Counter, defaultdict
from functools import cache, lru_cache
import gzip
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
from time import perf_counter


DIRECTORY = Path(__file__).resolve().parent
READINGS = ("sig0", "sig1")
BOUNDS = (12, 14)
CUT = 14


def json_lines(name):
    with gzip.open(DIRECTORY.parent / name, "rt") as source:
        yield from map(json.loads, source)


def tuple_key(value):
    return tuple(map(tuple_key, value)) if isinstance(value, list) else value


def start_key(record):
    return record["n knots"], record["index"]


class Rows:
    def __init__(self):
        self.indices = {}
        self.items = []
        self.counts = []
        self.negative_keys = []
        self.totals = []

    def intern(self, counts):
        items = tuple(sorted((key, n) for key, n in counts.items() if n))
        index = self.indices.get(items)
        if index is None:
            index = len(self.items)
            self.indices[items] = index
            self.items.append(items)
            self.counts.append(dict(items))
            self.negative_keys.append(tuple(key for key, n in items if n < 0))
            self.totals.append(sum(n for _, n in items))
        return index

    @lru_cache(maxsize=65536)
    def orders(self, i, j):
        """Two inclusion bits, the published and union-key signed versions, and support inclusion."""
        a, b = self.counts[i], self.counts[j]
        left = all(b.get(key, 0) >= n for key, n in self.items[i])
        right = all(a.get(key, 0) >= n for key, n in self.items[j])
        published = left + 2 * right
        union = (left and all(key in a for key in self.negative_keys[j])) + 2 * (
            right and all(key in b for key in self.negative_keys[i])
        )
        supports = a.keys() <= b.keys() or b.keys() <= a.keys()
        return published, union, supports

    @lru_cache(maxsize=32768)
    def observed(self, a, b):
        last = min(len(a), len(b))
        first = dict.fromkeys(("nested", "exact", "fixed orientation", "support only", "equal totals"), 1)
        orientation = 3
        for r in range(last - 1, -1, -1):
            i, j = a[r], b[r]
            order, _, support = self.orders(i, j)
            orientation &= order
            for metric, holds in zip(first, (order, order == 3, orientation, support, self.totals[i] == self.totals[j])):
                if not holds and first[metric] == 1:
                    first[metric] = r + 2 if r + 1 < last else None
            if all(value != 1 for value in first.values()):
                break
        return first

    @lru_cache(maxsize=32768)
    def nested_suffix(self, a, b, signed_union=False):
        last = min(len(a), len(b))
        for r in range(last - 1, -1, -1):
            published, union, _ = self.orders(a[r], b[r])
            if not (union if signed_union else published):
                return r + 2 if r + 1 < last else None
        return 1

    @cache
    def fitted(self, view, dimension, cutoff):
        if len(view) <= cutoff:
            return view
        window = [self.counts[i] for i in view[cutoff - dimension:cutoff]]
        coefficients = {}
        for key in set().union(*window):
            values = [row.get(key, 0) for row in window]
            differences = []
            while values:
                differences.append(values[0])
                values = [b - a for a, b in zip(values, values[1:])]
            coefficients[key] = differences
        after = list(view[:cutoff])
        for r in range(cutoff + 1, len(view) + 1):
            offset = r - cutoff + dimension - 1
            weights = [comb(offset, order) for order in range(dimension)]
            after.append(self.intern({
                key: sum(c * w for c, w in zip(differences, weights))
                for key, differences in coefficients.items()
            }))
        return tuple(after)

    @cache
    def clipped(self, view):
        return tuple(self.intern({key: n for key, n in self.items[i] if n > 0})
                     if self.negative_keys[i] else i for i in view)

    @cache
    def first_negative(self, view):
        return next((r for r, i in enumerate(view, 1) if self.negative_keys[i]), None)

    @lru_cache(maxsize=32768)
    def totals_reverse(self, a, b):
        differences = [self.totals[i] - self.totals[j] for i, j in zip(a, b)]
        return min(differences) < 0 < max(differences)


def record_views(record, rows):
    views = [[], []]
    for data in record["rows"]:
        multisets = []
        for s, reading in enumerate(READINGS):
            signatures = {tuple_key(key): n for key, n in data[reading]}
            assert len(signatures) == len(data[reading])
            assert all(isinstance(n, int) and n > 0 for n in signatures.values())
            assert sum(signatures.values()) == data["n"]
            views[s].append(rows.intern(signatures))
            multisets.append(signatures)
        projected = Counter()
        for (signature, parents), n in multisets[1].items():
            assert len(parents) == signature[1]
            projected[signature] += n
        assert projected == multisets[0]
    sig0_start = Counter(("start", 0, 0, len(knot)) for knot in record["stars"])
    initial = (rows.intern(sig0_start), rows.intern({(key, ()): n for key, n in sig0_start.items()}))
    return tuple(map(tuple, views)), initial


def literal_check(record_a, record_b, reading):
    """Expand multiplicities, match each copy, and try each suffix from its beginning."""
    def expanded(record):
        initial = [("start", 0, 0, len(knot)) for knot in record["stars"]]
        yield sorted(initial if reading == "sig0" else [(kind, ()) for kind in initial])
        for row in record["rows"]:
            yield sorted(tuple_key(key) for key, count in row[reading] for _ in range(count))

    def included(left, right):
        remaining = iter(right)
        for wanted in left:
            if not any(wanted == candidate for candidate in remaining):
                return False
        return True

    flags = [(included(a, b), included(b, a)) for a, b in zip(expanded(record_a), expanded(record_b))]
    start = next((r for r in range(1, len(flags)) if all(map(any, flags[r:]))), None)
    exact = next((r for r in range(1, len(flags)) if all(map(all, flags[r:]))), None)
    from_zero = next((r for r in range(len(flags)) if all(map(any, flags[r:]))), None)
    exact_from_zero = next((r for r in range(len(flags)) if all(map(all, flags[r:]))), None)
    fixed = next((r for r in range(1, len(flags))
                  if any(all(direction) for direction in zip(*flags[r:]))), None)
    return [start, exact, len(flags) - 1], from_zero, exact_from_zero, fixed, flags


def suffix_band(first):
    if first is None:
        return "never"
    return "by round 8" if first <= 8 else "later"


def dimension_at_cutoff(record):
    rounds = record["rows"]
    if len(rounds) < CUT:
        return "shorter than round 14"
    values = [row["n"] for row in rounds[CUT - 8:CUT]]
    for dimension in range(1, 5):
        if len(set(values)) == 1 and values[0] > 0:
            return f"dim {dimension}"
        values = [b - a for a, b in zip(values, values[1:])]
    return "no dimension at round 14"


def increment(table, *fields):
    table[" / ".join(map(str, fields))] += 1


def audit(phase, prefix):
    rows = Rows()
    source = f"phase{phase}_grown.jsonl.gz"
    published = json.loads((DIRECTORY.parent / ("phase1_rule.json" if phase == 1 else "phase2.json")).read_text())
    groups = defaultdict(list)
    by_kind, settles, late, literal_bound_difference = Counter(), Counter(), [], []
    fit_differences, negative_fits, negative_examples = Counter(), Counter(), []
    read_lengths, phase_pair_counts = Counter(), Counter()
    early_dimensions = Counter()
    census_metadata = {}
    t0 = perf_counter()
    for raw in json_lines(source):
        kind = raw["kind"]
        early_dimensions[(kind, dimension_at_cutoff(raw))] += 1
        if not kind.startswith("dim "):
            continue
        dim = int(kind.removeprefix("dim "))
        key = start_key(raw)
        views, initial = record_views(raw, rows)
        n = len(raw["rows"])
        read_lengths[n] += 1
        by_kind[kind] += 1
        fits, fitting_rounds = [], []
        for s, reading in enumerate(READINGS):
            view = views[s]
            k, literal_k = None, None
            for r in range(dim, n):
                if rows.fitted(view, dim, r) == view:
                    if literal_k is None:
                        literal_k = r
                    if max(dim, 3) <= r <= n - 2:
                        k = r
                        break
            fitting_rounds.append(k)
            if literal_k != k:
                literal_bound_difference.append([*key, reading, literal_k, k])
            within = k is not None and k <= BOUNDS[s]
            increment(settles, kind, reading, "within bound" if within else "later" if k else "never")
            if not within:
                late.append([key[1], kind, reading, k, n])
            fit = rows.fitted(view, dim, CUT) if n > CUT else None
            fits.append(fit)
            if fit is not None and fit != view:
                increment(fit_differences, kind, reading, "starts")
                fit_differences[f"{kind} / {reading} / rounds"] += sum(a != b for a, b in zip(view, fit))
            if fit is not None and (bad := rows.first_negative(fit)) is not None:
                increment(negative_fits, kind, reading, "starts")
                negative_fits[f"{kind} / {reading} / rounds"] += sum(bool(rows.negative_keys[i]) for i in fit)
                if len(negative_examples) < 4:
                    negative_examples.append([key, reading, bad, rows.items[fit[bad - 1]]])
        ordinal = len(census_metadata)
        census_metadata[key] = {"order among dimensional starts": ordinal,
                                "loose distinctions": raw["loose"],
                                "places": [len(knot) for knot in raw["stars"]]}
        groups[kind].append((key, views, initial, tuple(fits), tuple(fitting_rounds)))

    # Restate pair weight and row labels before inspecting the original pair tables.
    groups = dict(sorted(groups.items()))
    number = sum(comb(len(group), 2) for group in groups.values())
    phase1_pair_file = {}
    if phase == 1:
        for record in json_lines("phase1_pairs.jsonl.gz"):
            key = tuple(record["a"]), tuple(record["b"])
            assert key not in phase1_pair_file
            phase1_pair_file[key] = record
    preparation_seconds = perf_counter() - t0
    tables, diagnostics, changes, horizons = Counter(), Counter(), Counter(), Counter()
    sample = {}
    bucket_fills = Counter()
    listed_misses, first_file_differences = [], []
    sample_numbers = set(random.Random(31170 + phase).sample(range(number), min(20, number)))
    negatives = set()
    rank = 0
    for kind, group in groups.items():
        for a, b in combinations(group, 2):
            if prefix is not None and phase_pair_counts[kind] == prefix:
                break
            key_a, observed_a, start_a, fit_a, ka = a
            key_b, observed_b, start_b, fit_b, kb = b
            key = key_a, key_b
            phase_pair_counts[kind] += 1
            common = min(len(observed_a[0]), len(observed_b[0]))
            increment(horizons, kind, common)
            pair_results = {}
            for s, reading in enumerate(READINGS):
                va, vb = observed_a[s], observed_b[s]
                first = rows.observed(va, vb)
                obs, exact = first["nested"], first["exact"]
                initial = rows.orders(start_a[s], start_b[s])[0]
                from_zero = 0 if obs == 1 and initial else obs
                exact_from_zero = 0 if exact == 1 and initial == 3 else exact
                bucket = "never" if obs is None else str(obs)
                increment(diagnostics, kind, reading, "observed round", bucket)
                for label, enabled in (
                    ("exact by the last round", exact is not None),
                    ("containment orientation has to switch", obs != first["fixed orientation"]),
                    ("count-free support gives a different round", obs != first["support only"]),
                    ("total-count nesting gives a different round", obs != 1),
                    ("equal totals give a different exact round", exact != first["equal totals"]),
                    ("initial read changes nested round to 0", from_zero == 0),
                    ("initial read changes exact round to 0", exact_from_zero == 0),
                    ("round-14 persistence gives a different round", rows.nested_suffix(va[:CUT], vb[:CUT]) != obs),
                    ("short pair below ten common rounds", common < 10),
                ):
                    if enabled:
                        increment(diagnostics, kind, reading, label)
                fa, fb = fit_a[s], fit_b[s]
                prediction = None
                invalid = False
                same_late = False
                paired_unsettled = sum(k is None or k > CUT for k in (ka[s], kb[s]))
                if common <= CUT or fa is None or fb is None:
                    increment(tables, kind, reading, "not predicted: too few rounds")
                else:
                    prediction = rows.nested_suffix(fa, fb)
                    is_miss = prediction != obs
                    increment(tables, kind, reading, "missed" if is_miss else "predicted")
                    increment(tables, kind, reading, "observed " + suffix_band(obs))
                    increment(diagnostics, kind, reading, f"{paired_unsettled} starts unsettled at round 14",
                              "missed" if is_miss else "predicted")
                    if is_miss:
                        listed_misses.append([key_a[1], key_b[1], reading, obs, prediction])
                        increment(changes, kind, reading, obs, prediction)
                    faults = [r for view in (fa, fb) if (r := rows.first_negative(view)) is not None]
                    invalid = bool(faults and min(faults) <= common)
                    if invalid:
                        negatives.add(key)
                        union = rows.nested_suffix(fa, fb, True)
                        clipped = rows.nested_suffix(rows.clipped(fa), rows.clipped(fb))
                        changed = union != prediction or clipped != prediction
                        for mode, alt in (("signed union", union), ("clamped", clipped)):
                            increment(negative_fits, kind, reading, mode, "pairs")
                            increment(negative_fits, kind, reading, mode, "matches" if alt == obs else "misses")
                            if alt != prediction:
                                increment(negative_fits, kind, reading, mode, "changes the predicted round")
                        increment(negative_fits, kind, reading, "invalid-fit abstention",
                                  "withdrawn matches" if not is_miss else "withdrawn misses")
                        if changed:
                            increment(negative_fits, kind, reading, "alternative changes a pair conclusion")
                if obs is not None and obs > 8:
                    max_k = max(ka[s] or common, kb[s] or common)
                    dim = int(kind.removeprefix("dim "))
                    if max_k + dim <= common + 1:
                        same_late = va[max_k - 1:max_k + dim - 1] == vb[max_k - 1:max_k + dim - 1]
                    increment(diagnostics, kind, reading, "after round 8",
                              "same fitted polynomials" if same_late else "different or unverified polynomials")
                    increment(diagnostics, kind, reading, "after round 8",
                              "both settled before agreement" if max_k < obs else "a view settles at or after agreement")
                    if dim == 2 and max_k < common:
                        same_slope = rows.totals[va[common - 1]] - rows.totals[va[common - 2]] == (
                            rows.totals[vb[common - 1]] - rows.totals[vb[common - 2]]
                        )
                        if same_slope:
                            increment(diagnostics, kind, reading, "after round 8", "equal settled total slopes")
                    no_reversal = not rows.totals_reverse(va, vb)
                    if no_reversal:
                        increment(diagnostics, kind, reading, "after round 8", "no reversal in total counts")
                else:
                    same_slope = no_reversal = False
                labelled = ("never" if obs is None else "round 1" if obs == 1 else "rounds 2 to 8" if obs <= 8
                            else "rounds 9 to 14" if obs <= 14 else "after round 14")
                for bucket in (labelled,
                               "orientation switch" if obs != first["fixed orientation"] else None,
                               "same fitted polynomials after round 8" if same_late else None,
                               "neither different settled total slopes nor total reversal after round 8"
                               if same_slope and no_reversal else None,
                               "prediction misses" if common > CUT and obs != prediction else None,
                               "record ended before phase limit" if common < (20 if phase == 1 else 24) else None,
                               "initial round changes the start" if from_zero == 0 else None,
                               "invalid polynomial fit" if invalid else None):
                    tag = kind, reading, bucket
                    if bucket and bucket_fills[tag] < 1:
                        bucket_fills[tag] += 1
                        sample.setdefault(key, set()).add(bucket)
                pair_results[reading] = ([obs, exact, common], from_zero, exact_from_zero,
                                         first["fixed orientation"], prediction)
            s0, s1 = (pair_results[s][0][0] for s in READINGS)
            assert s1 is None or s0 is not None and s0 <= s1
            if s1 is None and s0 is not None:
                increment(diagnostics, kind, "extra parent reading removes agreement")
            elif s1 is not None and s0 < s1:
                increment(diagnostics, kind, "extra parent reading delays agreement")
            if phase == 1:
                saved = phase1_pair_file.pop(key, {})
                actual = {"a": list(key_a), "b": list(key_b), "kind": kind,
                          **{reading: value[0] for reading, value in pair_results.items()}}
                if saved != actual:
                    first_file_differences.append([saved, actual])
            if key in sample or rank in sample_numbers:
                if rank in sample_numbers:
                    sample.setdefault(key, set()).add("seeded sample")
                sample[key] = (pair_results, sorted(sample[key]))
            rank += 1

    pair_seconds = perf_counter() - t0 - preparation_seconds
    lookup = {key for pair in sample for key in pair}
    raw_sample = {start_key(raw): raw for raw in json_lines(source) if start_key(raw) in lookup}
    witnesses = []
    for key, (results, reasons) in sample.items():
        key_a, key_b = key
        info = {"a": key_a, "b": key_b, "reasons sampled": reasons}
        info["birth totals by round, from round 1"] = {
            label: [row["n"] for row in raw_sample[start]["rows"]]
            for label, start in (("a", key_a), ("b", key_b))
        }
        for reading in READINGS:
            comparison, from_zero, exact_zero, fixed, flags = literal_check(raw_sample[key_a], raw_sample[key_b], reading)
            summary, zero, zero_exact, fixed_orientation, prediction = results[reading]
            assert (comparison, from_zero, exact_zero, fixed) == (summary, zero, zero_exact, fixed_orientation)
            info[reading] = {"nested, exact, last round": comparison, "nested with round 0": from_zero,
                             "exact with round 0": exact_zero, "fixed orientation": fixed,
                             "round-14 prediction": prediction,
                             "round-by-round inclusion bits, from round 0": [a + 2*b for a, b in flags]}
        info["kind"] = raw_sample[key_a]["kind"]
        witnesses.append(info)

    ranks = {key[1]: value["order among dimensional starts"] for key, value in census_metadata.items()}
    chunk_limits = Counter()
    published_miss_order = []
    if phase == 2:
        for miss in sorted(listed_misses, key=lambda m: (ranks[m[0]], ranks[m[1]], m[2])):
            chunk = ranks[miss[0]] // 25
            if chunk_limits[chunk] < 50:
                published_miss_order.append(miss)
                chunk_limits[chunk] += 1

    recomputed = {"starts of a dimension": sum(by_kind.values()), "by kind": dict(by_kind),
                  "settling": dict(settles), "unsettled or late": late, "pairs": dict(tables),
                  "misses (first 50 per chunk)": published_miss_order}
    checked = {name: actual == published[name] for name, actual in recomputed.items()}
    both_early = sum(comb(n, 2) for (kind, early), n in early_dimensions.items()
                     if kind.startswith("dim ") and early == kind)
    return {
        "phase": phase,
        "prefix per dimension": prefix,
        "pair weighting": "each unordered pair of dimensional census starts once, within dimension",
        "pair interpretation": "published suffix begins at round 1; direction may vary by round",
        "recomputed author table": recomputed,
        "table fields agree": checked,
        "recorded phase 1 pair file differences": first_file_differences,
        "recorded phase 1 pair file rows left unvisited": len(phase1_pair_file),
        "settling changes under the note's least supported K": literal_bound_difference,
        "counts by common last round": dict(horizons),
        "counts of starts by last round": dict(read_lengths),
        "dimension using the last eight rounds through round 14": {
            " / ".join(keys): n for keys, n in sorted(early_dimensions.items())
        },
        "pairs with both dimensions identified at round 14": both_early,
        "pairs relying on a dimension label absent at round 14 under the same test": number - both_early,
        "pairs checked": dict(phase_pair_counts),
        "pair diagnostics": dict(diagnostics),
        "pairs where observed and predicted rounds differ": dict(changes),
        "round-14 fitted view differences from observed": dict(fit_differences),
        "negative multiplicity diagnostics": dict(negative_fits),
        "pairs with invalid fits": len(negatives),
        "negative multiplicity examples": negative_examples,
        "sampled pair starts": {str(key): census_metadata[key] for key in sorted(lookup)},
        "pair sample seed": 31170 + phase,
        "independent literal expansion sample": witnesses,
        "preparation seconds": preparation_seconds,
        "pair comparison seconds": pair_seconds,
        "interned distinct round multisets": len(rows.items),
        "interpolation cache hits": rows.fitted.cache_info().hits,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int, help="take this many pairs from the start of each dimension")
    args = parser.parse_args()
    for phase in (1, 2):
        result = audit(phase, args.prefix)
        print(json.dumps({k: result[k] for k in (
            "phase", "pairs checked", "table fields agree", "pairs with invalid fits",
            "preparation seconds", "pair comparison seconds", "interned distinct round multisets")}), flush=True)
        if args.prefix is None:
            (DIRECTORY / f"pairs_audit_phase{phase}.json").write_text(json.dumps(result, indent=2) + "\n")
