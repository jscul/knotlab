"""Recount finite kind labels and polynomial settling in the two raw growth archives."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys
from time import monotonic


HERE = Path(__file__).resolve().parent
READINGS = {"sig0": 12, "sig1": 14}
CUT = 14


def differences(values):
    return [b - a for a, b in zip(values, values[1:])]


def ratios(counts):
    return [Fraction(b, a) for a, b in zip(counts[-5:], counts[-4:])]


def kind(counts, end, highest=4):
    if end.startswith("stalls"):
        return "stalls"
    if end.startswith("closes"):
        return "closes"
    if len(counts) >= 8:
        last = counts[-8:]
        for dimension in range(1, highest + 1):
            if last[0] > 0 and len(set(last)) == 1:
                return f"dim {dimension}"
            last = differences(last)
    if len(counts) >= 5:
        last = ratios(counts)
        if min(last) > Fraction(21, 20) and max(last) - min(last) < Fraction(1, 100):
            return f"rate {float(last[-1]):.2f}"
    return "unread"


def knot_data(stars):
    holders = Counter(d for knot in stars for d in knot)
    loose = [sum(holders[d] == 1 for d in knot) for knot in stars]
    shares = [set() for _ in stars]
    for i, j in combinations(range(len(stars)), 2):
        if not stars[i].isdisjoint(stars[j]):
            shares[i].add(j)
            shares[j].add(i)
    live = {i for i, n in enumerate(loose) if n}
    most = max(len(group & live) for group in shares)
    return loose, shares, most if most >= 2 else 0


def key(item, reading):
    if reading == "sig0":
        return tuple(item)
    birth, parents = item
    return tuple(birth), tuple(tuple(parent) for parent in parents)


def series(rows, reading):
    data = defaultdict(lambda: [0] * len(rows))
    for t, row in enumerate(rows):
        assert sum(number for _, number in row[reading]) == row["n"]
        for item, number in row[reading]:
            values = data[key(item, reading)]
            assert number > 0 and values[t] == 0
            values[t] = number
    return list(data.values())


def last_violation(values, dimension):
    # A fit through the D observations ending at K predicts each subsequent
    # observation exactly iff every D-th difference ending after K is zero.
    for _ in range(dimension):
        values = differences(values)
    return max((t for t, value in enumerate(values, dimension + 1) if value), default=dimension)


def forecast_errors(values, dimension, cutoff):
    # Newton's forward formula, in integer arithmetic at integer rounds.
    observed = values[cutoff - dimension:cutoff]
    coefficients = []
    while observed:
        coefficients.append(observed[0])
        observed = differences(observed)
    bad = set()
    for t in range(cutoff + 1, len(values) + 1):
        offset = t - (cutoff - dimension + 1)
        predicted = sum(comb(offset, j) * c for j, c in enumerate(coefficients))
        if predicted != values[t - 1]:
            bad.add(t)
    return bad


def late_degree(values, dimension):
    tail = values[-dimension:]
    degree = -1
    while any(tail):
        degree += 1
        tail = differences(tail)
    return degree


def summarize_settling(rows, reading, dimension):
    values = series(rows, reading)
    least = max(last_violation(v, dimension) for v in values)
    bounds = {READINGS[reading], CUT}
    errors = {b: sorted(set().union(*(forecast_errors(v, dimension, b) for v in values))) for b in bounds}
    assert all(bool(failed) == (least > b) for b, failed in errors.items())
    degrees = {late_degree(v, dimension) for v in values}
    assert max(degrees) == dimension - 1
    return least, errors, sorted(degrees)


def table(counts, columns):
    return [dict(zip(columns, items), count=n) for items, n in sorted(counts.items())]


def tally(scope, *fields):
    return Counter(tuple(record[name] for name in fields) for record in scope)


def pair_count(counts):
    return sum(comb(number, 2) for number in counts.values())


def pair_eligibility(scope):
    full = Counter(x["kind"] for x in scope if x["kind"].startswith("dim"))
    early = Counter(x["at14"] for x in scope if x["at14"].startswith("dim"))
    common = Counter((x["kind"], x["at14"]) for x in scope
                     if x["kind"].startswith("dim") and x["at14"].startswith("dim"))
    both = pair_count(common)
    return {"same dimension at last read": pair_count(full), "same dimension at 14": pair_count(early),
            "eligible both ways": both, "newly eligible at 14": pair_count(early) - both,
            "lost at 14": pair_count(full) - both}


def check_quartic_restart(raw, loose, shares):
    # Every pair shares a neighbour and no knot is its own neighbour. The
    # sole maximal group contains all five knots. One loose distinction on
    # each remains for one offshoot. Compute their next groups from parents.
    assert loose == [2] * 5 and all(shares[i] & shares[j] for i, j in combinations(range(5), 2))
    parents = [set(range(5))] + [{i} for i in range(5)]
    pairs = [(i, j) for i, j in combinations(range(6), 2) if parents[i] & parents[j]]
    assert pairs == [(0, k) for k in range(1, 6)]
    assert all(len(parents[i] & parents[j]) == 1 for i, j in pairs)
    demand = Counter(i for pair in pairs for i in pair)
    fresh = [max(demand[i], 3 - len(group), 1) for i, group in enumerate(parents)]
    assert fresh == [5, 2, 2, 2, 2, 2]
    births = Counter({tuple(item): count for item, count in raw["rows"][0]["sig0"]})
    assert births == Counter({("join", 5, 5, 10): 1, ("offshoot", 1, 2, 3): 5})
    return {"round_one_loose": fresh, "round_two_groups": pairs,
            "round_one_loose_beyond_round_two_demand": [n - demand[i] for i, n in enumerate(fresh)]}


def raw_record(raw, limit):
    rows = raw["rows"]
    counts = [r["n"] for r in rows]
    label = kind(counts, raw["end"])
    assert label == raw["kind"], (raw["index"], label, raw["kind"])
    assert len(counts) <= limit and sum(counts, raw["n knots"]) == raw["knots"]
    if raw["end"] == "bound":
        assert raw["knots"] > 30000 >= raw["knots"] - counts[-1]
    if raw["end"] == "rounds":
        assert len(rows) == limit
    stars = [set(knot) for knot in raw["stars"]]
    loose, shares, block = knot_data(stars)
    assert loose == raw["loose"]
    early_end = raw["end"] if len(rows) < CUT else "rounds"
    short_dim_labels = 0
    contradicted = []
    for horizon in range(10, len(counts)):
        prefix = kind(counts[:horizon], "rounds")
        if prefix.startswith("dim"):
            short_dim_labels += 1
            wrong = forecast_errors(counts, int(prefix[-1]), horizon)
            if wrong:
                contradicted.append([horizon, prefix, min(wrong)])
    out = {"size": len(stars), "index": raw["index"], "kind": label, "at14": kind(counts[:CUT], early_end),
           "end": raw["end"], "read": len(rows), "knots": raw["knots"], "initial_block": block,
           "dimension_labelled_prefixes": short_dim_labels, "contradicted_prefixes": contradicted}
    dimension = int(label[-1]) if label.startswith("dim") else None
    if label == "unread" or label.startswith("rate"):
        r = ratios(counts)
        out["non_dimension_detail"] = {
            "index": raw["index"], "meetings": [[i, j] for i, adj in enumerate(shares) for j in sorted(adj) if i < j],
            "loose": loose, "kind": label, "as_of_14": out["at14"], "end": raw["end"], "counts": counts,
            "last_four_ratios": [str(q) for q in r], "spread": round(float(max(r) - min(r)), 6),
            "kind_allowing_D5": kind(counts, raw["end"], highest=5),
            "equals_5_plus_binomial_t_plus_3_choose_4_at_every_read_round":
                all(value == 5 + comb(t + 3, 4) for t, value in enumerate(counts, 1))}
        if len(shares) == 5 and all(len(adj) == 2 for adj in shares):
            out["non_dimension_detail"]["leftovers_on_five_knot_ring"] = sum(loose) - 10
        if out["non_dimension_detail"]["kind_allowing_D5"] == "dim 5":
            out["non_dimension_detail"]["finite_settling_at_D5"] = {
                r: summarize_settling(rows, r, 5)[0] for r in READINGS}
            out["quartic_restart"] = check_quartic_restart(raw, loose, shares)
    if dimension is not None:
        for reading in READINGS:
            least, errors, degrees = summarize_settling(rows, reading, dimension)
            out[reading] = {"least": least, "errors": errors, "degrees": degrees}
        if any(out[r]["least"] > b for r, b in READINGS.items()):
            out["late_detail"] = {"size": len(stars), "index": raw["index"], "loose": loose,
                                  "meetings": [[i, j] for i, adj in enumerate(shares) for j in sorted(adj) if i < j],
                                  "counts": counts, "initial_block": block, "kind_at14": out["at14"],
                                  "settles": {r: out[r]["least"] for r in READINGS},
                                  "bad_forecast_rounds": {r: out[r]["errors"] for r in READINGS}}
            out["first_three_sig0"] = [row["sig0"] for row in rows[:3]]
            out["late_trajectory"] = {r: [tuple((key(item, r), count) for item, count in row[r])
                                          for row in rows] for r in READINGS}
    return out


def phase_table(scope, limit):
    dimensions = [x for x in scope if x["kind"].startswith("dim")]
    horizons = sorted({x["read"] for x in dimensions})
    pairs_through = {}
    for t in range(CUT + 1, limit + 1):
        counts = Counter(x["kind"] for x in dimensions if x["read"] >= t)
        pairs_through[t] = pair_count(counts)
    readings = {}
    late = [x for x in dimensions if "late_detail" in x]
    for r, bound in READINGS.items():
        ks = Counter((x["kind"], x[r]["least"]) for x in dimensions)
        blocks = defaultdict(list)
        for x in dimensions:
            blocks[x["initial_block"]].append(x[r]["least"])
        cutoffs = {}
        for cutoff in sorted({CUT, bound}):
            cutoffs[cutoff] = {
                "starts_with_wrong_forecasts": sum(bool(x[r]["errors"][cutoff]) for x in dimensions),
                "forecast_rounds_observed": sum(x["read"] - cutoff for x in dimensions),
                "start_rounds_with_wrong_forecasts": sum(len(x[r]["errors"][cutoff]) for x in dimensions)}
        readings[r] = {
            "least_K_by_kind": table(ks, ["kind", "K"]),
            "K_less_than_3": sum(x[r]["least"] < 3 for x in dimensions),
            "observed_rounds_after_least_K": {
                "minimum": min(x["read"] - x[r]["least"] for x in dimensions),
                "maximum": max(x["read"] - x[r]["least"] for x in dimensions)},
            "fixed_cutoffs": cutoffs,
            "starts_with_nonzero_late_signature_of_degree_strictly_below_D_minus_1":
                sum(any(0 <= d < int(x["kind"][-1]) - 1 for d in x[r]["degrees"]) for x in dimensions),
            "K_by_initial_block_size": {m: {"starts": len(ks), "minimum": min(ks), "maximum": max(ks)}
                                        for m, ks in sorted(blocks.items())},
            "tightest_additive_constant_for_this_phase":
                max(x[r]["least"] - x["initial_block"] for x in dimensions)}
    if late:
        late_agreement = {}
        for r in READINGS:
            histories = [x["late_trajectory"][r] for x in late]
            late_agreement[r] = {
                "distinct_complete_histories": len({tuple(v) for v in histories}),
                "first_round_all_late_starts_identical_thereafter": 1 + max(
                    (i + 1 for i, values in enumerate(zip(*histories)) if len(set(values)) > 1), default=0)}
        if late_agreement["sig0"]["distinct_complete_histories"] == 1:
            late_agreement["shared_first_three_rounds_sig0"] = late[0]["first_three_sig0"]
    else:
        late_agreement = {}
    failed_prefix = [x for x in scope if x["contradicted_prefixes"]]
    capped = [x for x in scope if x["end"] == "bound"]
    quartic = [x["non_dimension_detail"] for x in scope if "non_dimension_detail" in x
               and x["non_dimension_detail"]["kind_allowing_D5"] == "dim 5"]
    paired = [{"late_index": x["index"], "quartic_index": y["index"]} for x in late for y in quartic
              if x["late_detail"]["meetings"] == y["meetings"]]
    restarts = [x["quartic_restart"] for x in scope if "quartic_restart" in x]
    if restarts:
        assert all(state == restarts[0] for state in restarts)
        certificate = {
            "starts": len(restarts), "numbering": "The five-parent join is 0 and knots 1 to 5 are the offshoots born in the same round.",
            "common_next_groups_and_loose_counts": restarts[0],
            "formula": "5 + binomial(t + 3, 4) for round t >= 1",
            "argument": [
                "Restart at round one. Each group for the next round is one pair with one common neighbour. The loose counts meet every demand.",
                "The cluster identification applies. Each offshoot has one leftover and two loose distinctions, giving it one endless chain. The five-parent join has no leftover.",
                "Each original round t counts clusters of size t in this map. For a cluster containing the five-parent join, the five chain lengths are nonnegative and sum to t - 1. A cluster omitting the join must begin at one of the five offshoots and has one continuation to size t.",
                "This map has clusters of every size. Since it never closes, the parity and not-all-equal growths agree."
            ],
            "references": [
                "proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md, Theorem 6",
                "proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/proof.md, extended complex and rays",
                "research/NAE-GROWTH-20261119-001/nae_growth.md, growth under the two laws"
            ]}
    else:
        certificate = None
    return {
        "archive_rows": len(scope), "end_kind_and_rounds": table(tally(scope, "end", "kind", "read"), ["end", "kind", "rounds"]),
        "knots_at_first_excess_over_30000": [min(x["knots"] for x in capped), max(x["knots"] for x in capped)] if capped else [],
        "kind_as_read_at_14": table(tally(scope, "kind", "at14"), ["last_read", "through_14"]),
        "same_dimension_pair_eligibility": pair_eligibility(scope),
        "pairs_by_last_common_round": {h: pair_count(tally([x for x in dimensions if x["read"] >= h], "kind"))
                                       - pair_count(tally([x for x in dimensions if x["read"] > h], "kind"))
                                       for h in horizons},
        "pairs_observed_at_each_forecast_round": pairs_through,
        "prefix_dimension_check": {
            "prefixes_tested": "Every prefix from round 10 through the penultimate round with a dimension label.",
            "labelled_prefixes": sum(x["dimension_labelled_prefixes"] for x in scope),
            "prefixes_whose_total_count_fit_later_fails": sum(len(x["contradicted_prefixes"]) for x in failed_prefix),
            "starts_with_such_a_failure": len(failed_prefix),
            "first_five_start_examples": [{"size": x["size"], "index": x["index"], "last_kind": x["kind"],
                                           "prefix_label_first_wrong_round": x["contradicted_prefixes"]}
                                          for x in failed_prefix[:5]]},
        "settling": readings, "late_starts": [x["late_detail"] for x in late],
        "late_starts_sharing_histories": late_agreement,
        "late_and_quartic_with_identical_starting_meetings": paired,
        "quartic_cluster_count": certificate,
        "unread_and_rate_starts": [x["non_dimension_detail"] for x in scope if "non_dimension_detail" in x]}


def run(stride):
    phases = {}
    records = {}
    for phase, limit in [(1, 20), (2, 24)]:
        with gzip.open(HERE.parent / f"phase{phase}_grown.jsonl.gz", "rt") as archive:
            scope = [raw_record(json.loads(line), limit) for i, line in enumerate(archive) if i % stride == 0]
        records[phase] = scope
        phases[phase] = phase_table(scope, limit)
    block_transfer = {}
    for r in READINGS:
        constant = phases[1]["settling"][r]["tightest_additive_constant_for_this_phase"]
        missed = [x for x in records[2] if r in x and x[r]["least"] > x["initial_block"] + constant]
        second_constant = max(x[r]["least"] - 2 * x["initial_block"] for x in records[1] if r in x)
        block_transfer[r] = {"constant_fit_on_up_to_four_knots": constant, "five_knot_misses": len(missed),
                             "misses_by_initial_block_and_K": table(
                                 Counter((x["initial_block"], x[r]["least"]) for x in missed), ["block", "K"]),
                             "exploratory_K_at_most_twice_initial_block_plus_c": {
                                 "constant_fit_on_up_to_four_knots": second_constant,
                                 "five_knot_misses": sum(x[r]["least"] > 2 * x["initial_block"] + second_constant
                                                         for x in records[2] if r in x)}}
    return {"archive_stride": stride, "start_index": "Zero-based index within starts of that number of knots.",
            "K": "Least K >= D with a polynomial of degree at most D-1 per signature matching all later observations.",
            "initial_block": "Largest number of live starting knots sharing a common neighbour. Size 0 if no block has at least two knots.",
            "phases": phases, "posthoc_initial_block_bound": block_transfer}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stride", type=int, choices=(1, 16), default=1, help="Use 16 for the timing pilot.")
    args = parser.parse_args()
    start = monotonic()
    result = run(args.stride)
    if args.stride > 1:
        seconds = monotonic() - start
        result = {"stride": args.stride, "archive_rows": {p: v["archive_rows"] for p, v in result["phases"].items()},
                  "seconds": round(seconds, 3), "full_run_estimate_seconds": round(seconds * args.stride, 2)}
    json.dump(result, sys.stdout, indent=2)
    print()
    print(f"elapsed_seconds {monotonic() - start:.3f}", file=sys.stderr)
