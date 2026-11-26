"""Independently count the saved settling observations with exact differences."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import islice, pairwise, zip_longest
import json
from math import comb
from pathlib import Path


STUDY = Path(__file__).resolve().parents[1]
READINGS = {"sig0": (5, 3), "sig1": (7, 5)}
HORIZON = 24


def freeze(value):
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


def differences(values):
    return [right - left for left, right in pairwise(values)]


def classify(totals, end):
    if end.startswith(("stalls", "closes")):
        word, _, _, round_text = end.split()
        assert int(round_text) == len(totals) + 1
        return word
    if len(totals) >= 10:
        tail = totals[-8:]
        for dimension in range(1, 5):
            if tail[0] > 0 and len(set(tail)) == 1:
                return f"dim {dimension}"
            tail = differences(tail)
        rates = [Fraction(b, a) for a, b in pairwise(totals[-5:])]
        if min(rates) > Fraction(105, 100) and max(rates) - min(rates) < Fraction(1, 100):
            return f"rate {float(rates[-1]):.2f}"
    return "unread"


def read_records(law, pilot):
    with gzip.open(STUDY / f"grown_fresh_{law}.jsonl.gz", "rt") as source:
        for record in map(json.loads, islice(source, pilot)):
            assert record["knot law"] == law
            yield record


def decode(record):
    totals = []
    readings = {reading: [] for reading in READINGS}
    for row in record["rows"]:
        totals.append(row["n"])
        assert row["n"] > 0
        for reading in READINGS:
            counts = {freeze(kind): count for kind, count in row[reading]}
            assert len(counts) == len(row[reading])
            assert sum(counts.values()) == row["n"]
            assert all(count > 0 for count in counts.values())
            readings[reading].append(counts)
        projection = Counter()
        for (kind, parents), count in readings["sig1"][-1].items():
            assert kind[1] == len(parents)
            projection[kind] += count
        assert projection == readings["sig0"][-1]
    assert record["knots"] == len(record["stars"]) + sum(totals)
    if record["end"] == "bound":
        assert record["knots"] > 30000 >= record["knots"] - totals[-1]
    if record["end"] == "rounds":
        assert len(totals) == HORIZON
    places = [set(knot) for knot in record["stars"]]
    occurrences = Counter(item for knot in places for item in knot)
    loose = [sum(occurrences[item] == 1 for item in knot) for knot in places]
    assert loose == record["loose"]
    shared = [sum(bool(knot & other) and loose[j] > 0
                  for j, other in enumerate(places) if i != j)
              for i, knot in enumerate(places)]
    fresh = max((kind[2] for kind in readings["sig0"][0]), default=0) if totals else 0
    assert max(max(shared), fresh) == record["M"]
    return totals, readings


def series_of(reading):
    kinds = sorted(set().union(*reading))
    return {kind: [row.get(kind, 0) for row in reading] for kind in kinds}


def final_difference_failure(values, degree_test):
    checked = values
    for _ in range(degree_test):
        checked = differences(checked)
    return max((round_n for round_n, diff in enumerate(checked, degree_test + 1) if diff), default=0)


def predict(series, dimension, cut, last_round):
    """Use Newton's integer formula starting at the first fitting round."""
    first_round = cut - dimension + 1
    predictions = [dict() for _ in range(last_round - cut)]
    polynomials = Counter()
    zero_polynomials = 0
    for kind, values in series.items():
        fitting_values = values[first_round - 1:cut]
        coefficients = []
        while fitting_values:
            coefficients.append(fitting_values[0])
            fitting_values = differences(fitting_values)
        degrees = [degree for degree, coefficient in enumerate(coefficients) if coefficient]
        if degrees:
            polynomials[max(degrees)] += 1
        else:
            zero_polynomials += 1
        for round_n, counts in enumerate(predictions, cut + 1):
            count = sum(coefficient * comb(round_n - first_round, degree)
                        for degree, coefficient in enumerate(coefficients) if coefficient)
            if count:
                counts[kind] = count
    return predictions, polynomials, zero_polynomials


def inspect_forecast(counters, name, series, dimension, cut, horizon, index, examples):
    if cut < dimension or cut >= horizon:
        counters[name]["no forward check"] += 1
        return
    predictions, _, _ = predict(series, dimension, cut, horizon)
    counters[name]["forward check"] += 1
    has_negative = False
    for round_n, counts in enumerate(predictions, cut + 1):
        negatives = {kind: count for kind, count in counts.items() if count < 0}
        if negatives:
            has_negative = True
            counters[name]["negative rounds"] += 1
            counters[name]["negative kind counts"] += len(negatives)
            if name not in examples:
                kind = min(negatives, key=negatives.get)
                examples[name] = {
                    "index": index, "D": dimension, "cut": cut, "round": round_n,
                    "kind": kind, "fitted count": negatives[kind],
                    "observed count": series[kind][round_n - 1],
                    "fit counts": series[kind][cut - dimension:cut],
                }
    counters[name]["negative start readings"] += has_negative


def audit_reading(record, totals, reading, rows, dimension, data):
    index, horizon, size = record["index"], len(totals), record["M"]
    strict_falls = [round_n for round_n, jump in enumerate(differences(totals), 2) if jump < 0]
    trough = max(strict_falls, default=1)
    size_offset, trough_offset = READINGS[reading]
    size_cut, trough_cut = size + size_offset, trough + trough_offset
    bound = max(size_cut, trough_cut)
    series = series_of(rows)
    latest_failure = max(final_difference_failure(values, dimension) for values in series.values())
    latest_total_failure = final_difference_failure(totals, dimension)
    floor = max(3, dimension)
    # The Dth difference whose last round is K + 1 is the first tested after the fit.
    fit_cut = max(floor, latest_failure)
    cut = fit_cut if fit_cut <= horizon - 2 else None
    actual_horizon_checkable = cut is not None and cut <= horizon - dimension

    if cut is not None:
        predicted, degrees, zeros = predict(series, dimension, cut, horizon + 1)
        assert predicted[:-1] == rows[cut:]
        assert all(count > 0 for row in predicted[:-1] for count in row.values())
        data["polynomial degree"].update(degrees)
        data["zero polynomials"] += zeros
        data["settled forecasts negative at next unsaved round"] += any(x < 0 for x in predicted[-1].values())

    reasons = []
    if cut is None:
        reasons.append("K unavailable")
    elif cut > HORIZON - dimension:
        reasons.append("K exceeds 24 minus D")
    if horizon < HORIZON:
        reasons.append("fewer than 24 saved rounds")
    result = {"index": index, "D": dimension, "end": record["end"], "last round": horizon,
              "M": size, "T": trough, "K": cut, "strict falls": len(strict_falls),
              "latest nonzero Dth difference": latest_failure,
              "latest nonzero Dth difference in total": latest_total_failure,
              "censor reasons": reasons, "checkable relative to saved horizon": actual_horizon_checkable}
    data["K counts"][str(cut)] += 1
    data["T counts"][trough] += 1
    data["horizons"][horizon][record["kind"]] += 1
    data["strict fall counts"][len(strict_falls)] += 1
    if cut is not None and cut > trough and cut > floor:
        data["K after T and floor"][record["kind"]] += 1
    if cut is not None and fit_cut > floor and latest_failure > latest_total_failure:
        data["last failure cancels in total"][record["kind"]] += 1
    for name, trial in (("M cutoff", size_cut), ("T cutoff", trough_cut), ("combined cutoff", bound)):
        inspect_forecast(data["forecasts"], name, series, dimension, trial, horizon, index, data["negative examples"])

    if cut is not None:
        result.update({"M cutoff": size_cut, "T cutoff": trough_cut,
                       "point holds if late": cut <= size_cut or cut == trough_cut,
                       "bound holds": cut <= bound, "slack": bound - cut})
    if reasons:
        data["censored"].append(result)
        data["cells"][record["kind"]]["censored"] += 1
        data["tally"]["censored"] += 1
        return result

    cell = data["cells"][record["kind"]]
    cell["checkable"] += 1
    assert actual_horizon_checkable
    assert cut is not None
    data["post-cut compared rounds"][horizon - cut] += 1
    data["final horizon bound"]["at or beyond last saved round" if bound >= horizon else "before last saved round"] += 1
    data["offset K minus T"]["strict fall" if strict_falls else "none"][cut - trough] += 1
    data["offset K minus T"]["late" if cut > size_cut else "within M cutoff"][cut - trough] += 1
    data["larger cutoff"]["M" if size_cut > trough_cut else "T" if trough_cut > size_cut else "tied"] += 1
    if cut > trough_cut:
        data["T-only bound fails"]["strict fall" if strict_falls else "none"] += 1
        if strict_falls and "example: strict fall yet T-only bound fails" not in data:
            data["example: strict fall yet T-only bound fails"] = {**result, "birth counts": totals}
    if cut > size_cut:
        data["late"].append({**result, "birth counts": totals})
        cell["late"] += 1
        ok = cut == trough_cut
        tally_key = f"late: K = T + {trough_offset}" if ok else "late: point law broken"
        data["tally"][tally_key] += 1
        cell[tally_key] += 1
        if not ok:
            data["breaks"].append([index, reading, "point", size, trough, cut])
    if cut <= bound:
        data["tally"]["within the combined bound"] += 1
        data["slack"][bound - cut] += 1
        cell["within the combined bound"] += 1
    else:
        data["tally"]["combined bound broken"] += 1
        cell["combined bound broken"] += 1
        data["breaks"].append([index, reading, "bound", size, trough, cut])
    return result


def new_reading_summary():
    return {
        "K counts": Counter(), "T counts": Counter(), "horizons": defaultdict(Counter),
        "strict fall counts": Counter(), "K after T and floor": Counter(),
        "last failure cancels in total": Counter(), "polynomial degree": Counter(),
        "zero polynomials": 0, "settled forecasts negative at next unsaved round": 0,
        "forecasts": defaultdict(Counter), "negative examples": {},
        "censored": [], "cells": defaultdict(Counter), "tally": Counter(),
        "post-cut compared rounds": Counter(), "final horizon bound": Counter(),
        "offset K minus T": defaultdict(Counter), "larger cutoff": Counter(),
        "T-only bound fails": Counter(), "late": [], "breaks": [], "slack": Counter(),
    }


def new_law_summary():
    return {
        "kinds": Counter(), "ends by kind": defaultdict(Counter),
        "saved rounds": 0, "births": 0, "unread": [],
        "readings": {reading: new_reading_summary() for reading in READINGS},
        "reading overlap indices": {"late": [], "censored": []},
        "K with parents minus K without parents (finite K in both)": defaultdict(Counter),
    }


def audit_record(record, summary):
    totals, rows = decode(record)
    kind = classify(totals, record["end"])
    assert kind == record["kind"]
    summary["kinds"][kind] += 1
    summary["ends by kind"][kind][record["end"]] += 1
    summary["saved rounds"] += len(totals)
    summary["births"] += sum(totals)
    if kind == "unread":
        summary["unread"].append({"index": record["index"], "end": record["end"], "birth counts": totals})
    outcomes = {}
    if kind.startswith("dim "):
        for reading, details in summary["readings"].items():
            outcomes[reading] = audit_reading(record, totals, reading, rows[reading], int(kind[4:]), details)
        without_parents, with_parents = (outcomes[reading]["K"] for reading in READINGS)
        if with_parents is not None:
            assert without_parents is not None and without_parents <= with_parents
            summary["K with parents minus K without parents (finite K in both)"][kind][
                with_parents - without_parents] += 1
    return outcomes, totals, rows


def as_saved_result(summary):
    result = {"kinds": summary["kinds"], "tally": {}, "slack (bound minus K)": {}, "breaks": []}
    for reading, data in summary["readings"].items():
        result["tally"].update({f"{reading} / {key}": value for key, value in data["tally"].items()})
        result["slack (bound minus K)"][reading] = {str(key): value for key, value in data["slack"].items()}
        result["breaks"].extend(data["breaks"])
    return result


def compare_pair(nae, parity, left, right, summaries, cross):
    index = nae["index"]
    assert all(nae[key] == parity[key] for key in ("index", "graph", "loose", "stars"))
    label = f"{nae['kind']} / {parity['kind']}"
    cross["dimension and ending comparison"][label] += 1
    for name, first, second in zip(("totals", *READINGS), (left[1], *left[2].values()), (right[1], *right[2].values())):
        first_difference = next((i for i, (a, b) in enumerate(zip(first, second), 1) if a != b), None)
        if first_difference is None:
            relation = "identical" if len(first) == len(second) else "agree through shorter record"
        else:
            relation = f"first difference at {first_difference}"
        cross["law reading comparison"][label][name][relation] += 1
    if nae["M"] != parity["M"]:
        cross["M differs"][label] += 1
    flags = {"late": [], "censored": [], "checkable": []}
    for law, outcome in (("nae", left), ("parity", right)):
        for reading, result in outcome[0].items():
            name = f"{law} {reading}"
            if result["censor reasons"]:
                flags["censored"].append(name)
            else:
                flags["checkable"].append(name)
                if result["K"] > result["M cutoff"]:
                    flags["late"].append(name)
        for name in ("late", "censored"):
            if all(f"{law} {reading}" in flags[name] for reading in READINGS):
                summaries[law]["reading overlap indices"][name].append(index)
    for key, values in flags.items():
        if values:
            label = " / ".join(values)
            cross[f"{key} overlap"][label] += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=int, help="count only this many paired sample entries")
    args = parser.parse_args()
    laws = ("nae", "parity")
    summaries = {law: new_law_summary() for law in laws}
    cross = {name: Counter() for name in ("dimension and ending comparison", "M differs",
                                          "late overlap", "censored overlap", "checkable overlap")}
    cross["law reading comparison"] = defaultdict(lambda: defaultdict(Counter))
    indices = set()
    for nae, parity in zip_longest(*(read_records(law, args.pilot) for law in laws)):
        assert nae is not None and parity is not None
        assert nae["index"] not in indices
        indices.add(nae["index"])
        left = audit_record(nae, summaries["nae"])
        right = audit_record(parity, summaries["parity"])
        compare_pair(nae, parity, left, right, summaries, cross)
    validation = {}
    if args.pilot is None:
        for law, summary in summaries.items():
            expected = json.loads((STUDY / f"test_{law}.json").read_text())
            actual = as_saved_result(summary)
            validation[law] = {key: value == actual[key] for key, value in expected.items()}
            assert expected == actual, (law, expected, actual)
    output = {"paired census starts": len(indices), "laws": summaries, "comparison": cross,
              "all fields agree with saved test results": validation}
    path = Path(__file__).with_name("recount_pilot.json" if args.pilot is not None else "recount.json")
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"paired census starts": len(indices), "comparison": cross,
                      "all fields agree with saved test results": validation}, indent=2))


if __name__ == "__main__":
    main()
