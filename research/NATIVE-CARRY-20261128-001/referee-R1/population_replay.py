"""Recount whole-choice sets in the four fixed populations without a subset cut.

Only start decoding, sampling, and growth come from the archived engine. The
published population and birth rows are read after the independent calculations
for comparison. The census-type roster is the original census input.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ROOT = RESEARCH.parent
ENGINE = RESEARCH / "FORBID-EDITS-20261126-001"
BIRTH_STUDY = RESEARCH / "LOCAL-COMMUTE-20261127-001"
CENSUS_TYPES = (ROOT / "artifacts/FOUR-READINGS-20261120-001A"
                / "FOUR-READINGS-20261120-001A-E001_signed_rules/census.json")
POPULATIONS = ("census starts", "census types", "extension", "second sample")
FOUR = "four mutually meeting knots"
FIVE = "K_{2,3}"

sys.path.insert(0, str(ENGINE))
from forbid import extension, grown, sampled, supports_of


@dataclass(frozen=True)
class Cell:
    distinctions: tuple[int, int]
    knots: int
    cross_pairs: tuple[tuple[int, int], ...]
    signature: int
    odd: int


def pattern_cells(holders, pair_bit):
    """Make each cell once, with its direct commutation and word-sorting charges."""
    cells = []
    for left, right in combinations(range(len(holders)), 2):
        first, second = holders[left], holders[right]
        if len(set(first + second)) != 4:
            continue
        pairs = tuple(tuple(sorted(pair)) for pair in product(first, second))
        signature = sum(pair_bit[pair] for pair in pairs)
        odd = sum(a > b for a, b in product(first, second)) % 2
        cells.append(Cell((left, right), sum(1 << k for k in first + second), pairs, signature, odd))
    return cells


def all_signatures(n, cells, sign_bit):
    """Binary subset transform over four-holder groups, including multiplicities.

    The low bits are the pair parities and the sign. Each used group gets a
    separate high bit so a nonempty collection with all-low-zero survives.
    Before step k, a mask sums precisely the groups obtainable by erasing
    only processed bits. Step k adds the groups obtained by also erasing k.
    """
    subtotals = [0] * (1 << n)
    groups = {}
    for cell in cells:
        if cell.knots not in groups:
            groups[cell.knots] = sign_bit << (1 + len(groups))
            subtotals[cell.knots] ^= groups[cell.knots]
        subtotals[cell.knots] ^= cell.signature | (sign_bit if cell.odd else 0)
    for k in range(n):
        half = 1 << k
        for target_start in range(half, len(subtotals), 2 * half):
            for target in range(target_start, target_start + half):
                subtotals[target] ^= subtotals[target - half]
    return subtotals


def knots_of(mask):
    return [k for k in range(mask.bit_length()) if mask & (1 << k)]


def count_formula(knots, meetings, left, right):
    left_other = {k: meetings.get((left, k), 0) for k in knots if k not in (left, right)}
    right_other = {k: meetings.get((right, k), 0) for k in left_other}
    return (sum(left_other.values()) * sum(right_other.values())
            - sum(left_other[k] * right_other[k] for k in left_other))


def check_formula(knots, holders, cells):
    """Compare the multiplication rule with explicit cross-pair counts."""
    meetings = Counter(holders)
    meetings.update((right, left) for left, right in holders)
    counts = Counter(pair for cell in cells for pair in cell.cross_pairs)
    for a, b in combinations(knots, 2):
        assert counts[a, b] == count_formula(knots, meetings, a, b), (knots, holders, a, b)
    return counts


def interleaving(order, holders, cells):
    position = {k: i for i, k in enumerate(order)}
    ends = {d: sorted(position[k] for k in holders[d])
            for d in {d for cell in cells for d in cell.distinctions}}
    crossings = 0
    for cell in cells:
        left, right = cell.distinctions
        a, b = ends[left]
        c, d = ends[right]
        crossings += (a < c < b) != (a < d < b)
    return crossings % 2


def describe_whole_set(mask, holders, cells, odd, birth_allowed, rng):
    knots = knots_of(mask)
    included = [cell for cell in cells if cell.knots & mask == cell.knots]
    internal = [ends for ends in holders if all(mask & (1 << k) for k in ends)]
    counts = check_formula(knots, internal, included)
    assert included and not any(c % 2 for c in counts.values())
    assert interleaving(knots, holders, included) == odd
    for i in range(len(knots) - 1):
        adjacent = knots.copy()
        adjacent[i:i + 2] = reversed(adjacent[i:i + 2])
        assert interleaving(adjacent, holders, included) == odd
    for _ in range(2):
        assert interleaving(rng.sample(knots, len(knots)), holders, included) == odd

    used_ids = {d for cell in included for d in cell.distinctions}
    used = Counter(holders[d] for d in used_ids)
    kind = "other"
    if len(used_ids) == len(used) == 6:
        degrees = Counter(k for pair in used for k in pair)
        if sorted(degrees.get(k, 0) for k in knots) == [3, 3, 3, 3]:
            kind = FOUR
        elif sorted(degrees.get(k, 0) for k in knots) == [2, 2, 2, 3, 3]:
            high = tuple(sorted(k for k in knots if degrees[k] == 3))
            if high not in used:
                kind = FIVE
    result = {"set": knots, "knots": len(knots), "sign": odd, "cells": len(included),
              "max coverage": max(counts.values()), "covered twice": all(v == 2 for v in counts.values()),
              "doubled": any(v > 1 for v in used.values()), "kind": kind,
              "inert distinctions": len(internal) - len(used_ids)}
    if birth_allowed is not None:
        result["birth-forbidden cells"] = sum(c.distinctions not in birth_allowed for c in included)
    return result


def odd_choice(cells):
    """An odd commuting choice is a dependency of cell columns with odd charge."""
    pivots = {}
    odd_attainable = False
    for cell in cells:
        vector, cost = cell.signature, cell.odd
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (vector, cost)
                break
            old, old_cost = pivots[pivot]
            vector ^= old
            cost ^= old_cost
        else:
            odd_attainable |= bool(cost)
    return odd_attainable, len(cells) - len(pivots)


def birth_verdicts(holders, knot_births, cells):
    """Recreate the birth rule using only the holders present when it decides."""
    dates = [tuple(knot_births[k] for k in ends) for ends in holders]
    allowed = set()
    for cell in cells:
        i, j = cell.distinctions
        decision = max(dates[i][0], dates[j][0])
        if any(dates[d][1] <= decision for d in (i, j)):
            allowed.add(cell.distinctions)
    birth_cells = [cell for cell in cells if cell.distinctions in allowed]
    birth_odd, birth_dimension = odd_choice(birth_cells)
    whole_odd, whole_dimension = odd_choice(cells)
    natural_mask = 0
    for cell in birth_cells:
        natural_mask ^= cell.signature
    natural_sign = None
    if not natural_mask:
        natural_sign = sum(cell.odd for cell in birth_cells) % 2
    return allowed, {"birth choices attain odd": birth_odd, "birth choices: free directions": birth_dimension,
                     "whole choices attain odd": whole_odd, "whole choices: free directions": whole_dimension,
                     "locally decidable pairs": len(allowed), "unheld pairs": len(cells),
                     "natural rule closing sign": natural_sign}


def witness(mask, holders, cells, odd, minima, birth_allowed, rng):
    result = describe_whole_set(mask, holders, cells, odd, birth_allowed, rng)
    result["minimal subsets"] = [knots_of(m) for m in minima if m & mask == m]
    result["distinctions and holders"] = [(d, ends) for d, ends in enumerate(holders)
                                          if all(mask & (1 << k) for k in ends)]
    result["failing pairs"] = [c.distinctions for c in cells if c.knots & mask == c.knots]
    if birth_allowed is not None:
        result["unavailable at birth"] = [pair for pair in result["failing pairs"] if pair not in birth_allowed]
    return result


def recount(n, holders, dates, rng):
    knots = range(n)
    holders = [tuple(sorted(ends)) for ends in holders]
    assert all(len(ends) == len(set(ends)) == 2 for ends in holders)
    pair_bit = {pair: 1 << at for at, pair in enumerate(combinations(knots, 2))}
    sign_bit = 1 << len(pair_bit)
    cells = pattern_cells(holders, pair_bit)
    check_formula(knots, holders, cells)
    allowed, birth = birth_verdicts(holders, dates, cells) if dates else (None, {})
    signatures = all_signatures(n, cells, sign_bit)
    whole_sizes = {"even": Counter(), "odd": Counter()}
    minimal = []
    minimal_masks = []
    odd_birth_forbidden = 0
    odd_nonminimal = 0
    smallest_odd_nonminimal = None
    smallest_birth_forbidden_odd = None
    whole_closure_sign = None
    banned = set() if allowed is None else {cell.knots for cell in cells if cell.distinctions not in allowed}
    for mask, signature in enumerate(signatures):
        if signature < 2 * sign_bit or signature & (sign_bit - 1):
            continue
        sign = int(bool(signature & sign_bit))
        size = mask.bit_count()
        whole_sizes["odd" if sign else "even"][size] += 1
        # Every proper subset has an earlier numeric mask; any nonminimal
        # set contains a minimal one, irrespective of either set's sign.
        nonminimal = any(mask & m == m for m in minimal_masks)
        if nonminimal:
            if sign:
                odd_nonminimal += 1
                if smallest_odd_nonminimal is None or size < smallest_odd_nonminimal.bit_count():
                    smallest_odd_nonminimal = mask
        else:
            minimal_masks.append(mask)
            minimal.append(describe_whole_set(mask, holders, cells, sign, allowed, rng))
        if sign and any(mask & group == group for group in banned):
            odd_birth_forbidden += 1
            if smallest_birth_forbidden_odd is None or size < smallest_birth_forbidden_odd.bit_count():
                smallest_birth_forbidden_odd = mask
        if mask == len(signatures) - 1:
            whole_closure_sign = sign
            if nonminimal:
                describe_whole_set(mask, holders, cells, sign, allowed, rng)

    row = {"knots": n, "distinctions": len(holders), "subsets checked": len(signatures),
           "whole-choice sets by sign and size": whole_sizes, "whole closure sign": whole_closure_sign,
           "minimal sets": sorted(minimal, key=lambda item: (item["knots"], item["set"])),
           "odd nonminimal sets": odd_nonminimal}
    if allowed is not None:
        row.update(birth)
        row["odd whole-choice sets including a birth-forbidden cell"] = odd_birth_forbidden
        if smallest_birth_forbidden_odd is not None:
            row["smallest birth-forbidden odd example"] = witness(
                smallest_birth_forbidden_odd, holders, cells, 1, minimal_masks, allowed, rng)
    if smallest_odd_nonminimal is not None and not any(item["sign"] for item in minimal):
        row["smallest odd example with no odd minimal set in the closure"] = witness(
            smallest_odd_nonminimal, holders, cells, 1, minimal_masks, allowed, rng)
    return row


def growth(start, rounds, cap):
    supports = supports_of(start)
    knot_births = [0] * len(supports)
    for round_no in range(rounds + 1):
        holders = defaultdict(list)
        for k, distinctions in enumerate(supports):
            for d in distinctions:
                holders[d].append(k)
        if all(len(ends) == 2 for ends in holders.values()):
            if round_no:
                return [tuple(holders[d]) for d in sorted(holders)], knot_births, round_no
            return None
        if round_no == rounds:
            return None
        after, status, _ = grown(supports, "parity", "ordinary")
        if status == "stalled" or len(after) > cap:
            return None
        assert status == "funded" and tuple(after[:len(supports)]) == tuple(supports)
        knot_births.extend([round_no + 1] * (len(after) - len(supports)))
        supports = after


def starts_roster():
    return json.loads((ENGINE / "starts.json").read_text())


def read_growth(pop, starts, rounds, cap, rng):
    rows = []
    for start_index, start in enumerate(starts):
        closure = growth(start, rounds, cap)
        if closure is None:
            continue
        holders, dates, round_no = closure
        row = recount(len(dates), holders, dates, rng)
        rows.append({"population": pop, "index": len(rows), "start index": start_index,
                     "rounds": round_no, "start knots": start[0], **row})
    return rows


def read_types(rng):
    roster = json.loads(CENSUS_TYPES.read_text())
    rows = []
    for index, item in enumerate(roster):
        holders = item["sharing"]
        n = max(max(pair) for pair in holders) + 1
        assert set(k for pair in holders for k in pair) == set(range(n))
        rows.append({"population": "census types", "index": index, "type": index,
                     **recount(n, holders, None, rng)})
    return rows


def compare_population(rows):
    """Compare every previously reported subset and row field after recounting."""
    with gzip.open(STUDY / "rows.jsonl.gz", "rt") as stream:
        old_rows = {(r["population"], r["index"]): r for r in map(json.loads, stream)}
    differences = []
    fields = ("knots", "distinctions", "start index", "rounds", "start knots", "type", "birth choices attain odd")
    checked_sets = 0
    for new in rows:
        key = (new["population"], new["index"])
        old = old_rows.pop(key, None)
        if old is None:
            differences.append([*key, "row missing from published output"])
            continue
        for field in fields:
            if field not in old:
                continue
            if new.get(field) != old[field]:
                differences.append([*key, field, old[field], new.get(field)])
        if (new["whole closure sign"] is not None) != old["whole closure a carrier"]:
            differences.append([*key, "whole-closure membership"])
        if new["whole closure sign"] != old["whole closure sign"]:
            differences.append([*key, "whole-closure sign", old["whole closure sign"], new["whole closure sign"]])
        old_sets = {tuple(s["set"]): s for s in old["minimal carriers"]}
        new_sets = {tuple(s["set"]): s for s in new["minimal sets"] if s["knots"] <= old["subsets up to"]}
        if old_sets.keys() != new_sets.keys():
            differences.append([*key, "minimal sets", sorted(old_sets.keys() - new_sets.keys()),
                                sorted(new_sets.keys() - old_sets.keys())])
        for k in old_sets.keys() & new_sets.keys():
            checked_sets += 1
            for field in new_sets[k].keys() & old_sets[k].keys():
                if old_sets[k][field] != new_sets[k][field]:
                    differences.append([*key, k, field, old_sets[k][field], new_sets[k][field]])
            if not (old_sets[k]["order independent"] and old_sets[k]["formula agrees"]):
                differences.append([*key, k, "reported gate failure"])
    differences.extend([*key, "row missing from recount"] for key in sorted(old_rows))
    return {"rows checked": len(rows), "minimal sets compared within the published limit": checked_sets,
            "differences": differences}


def compare_birth(rows):
    """Compare the exact birth and whole linear-system verdicts with the birth study."""
    with (BIRTH_STUDY / "results.jsonl").open() as stream:
        old = {r["start"]: r for r in map(json.loads, stream) if "closing round" in r and r["rounds"] > 0}
    differences = []
    for row in rows:
        start = row["start index"]
        prior = old.pop(start, None)
        if prior is None:
            differences.append([start, "row missing from birth study"])
            continue
        for field in ("closing round", "knots", "birth choices attain odd", "birth choices: free directions",
                      "whole choices attain odd", "whole choices: free directions", "locally decidable pairs",
                      "unheld pairs", "natural rule closing sign"):
            if field == "natural rule closing sign":
                # The archive uses words, and omits the sign if no state is kept.
                value = {None: None, 0: "even", 1: "odd"}[row[field]]
            else:
                value = row["rounds" if field == "closing round" else field]
            if value != prior.get(field):
                differences.append([start, field, prior.get(field), value])
    differences.extend([start, "row missing from recount"] for start in sorted(old))
    return {"rows checked": len(rows), "differences": differences}


def summarize_population(rows):
    all_counts = {"even": Counter(), "odd": Counter()}
    minimal_counts = {"even": Counter(), "odd": Counter()}
    odd_rows = []
    odd_minimal_rows = []
    extra_minimal = []
    for row in rows:
        for word in all_counts:
            all_counts[word].update(row["whole-choice sets by sign and size"][word])
        if row["whole-choice sets by sign and size"]["odd"]:
            odd_rows.append(row)
        if any(item["sign"] for item in row["minimal sets"]):
            odd_minimal_rows.append(row)
        for item in row["minimal sets"]:
            sign = "odd" if item["sign"] else "even"
            label = f'{item["kind"]}; {item["knots"]} knots; {item["cells"]} cells'
            minimal_counts[sign][label] += 1
            if row["knots"] > 12 and item["knots"] > 8:
                extra_minimal.append({"start index": row["start index"], **item})
    return {"rows": len(rows), "total subsets checked": sum(r["subsets checked"] for r in rows),
            "knot counts": Counter(r["knots"] for r in rows),
            "whole-choice sets by sign and size": all_counts,
            "total whole-choice sets by sign": {sign: counts.total() for sign, counts in all_counts.items()},
            "whole closure is a set": sum(r["whole closure sign"] is not None for r in rows),
            "whole closure is an odd set": sum(r["whole closure sign"] == 1 for r in rows),
            "rows with a whole-choice set": sum(bool(r["minimal sets"]) for r in rows),
            "rows with an even whole-choice set": sum(bool(r["whole-choice sets by sign and size"]["even"]) for r in rows),
            "rows with an even minimal set": sum(any(not s["sign"] for s in r["minimal sets"]) for r in rows),
            "rows with an odd whole-choice set": len(odd_rows),
            "rows with an odd minimal set": len(odd_minimal_rows),
            "rows with odd nonminimal sets": sum(bool(r["odd nonminimal sets"]) for r in rows),
            "rows with odd sets but no odd minimal set": [r.get("start index", r["index"]) for r in odd_rows
                                                           if not any(s["sign"] for s in r["minimal sets"])],
            "minimal set counts by sign and kind": minimal_counts,
            "rows above twelve knots": [{"start index": r["start index"], "knots": r["knots"],
                                         "subsets checked": r["subsets checked"],
                                         "whole-choice sets by sign and size": r["whole-choice sets by sign and size"]}
                                        for r in rows if r["knots"] > 12],
            "new minimal sets at rows above twelve knots": extra_minimal}


def summarize_census(rows):
    rounds = {}
    for round_no in sorted({r["rounds"] for r in rows}):
        group = [r for r in rows if r["rounds"] == round_no]
        rounds[round_no] = {
            "rows": len(group),
            "whole closure is a set": sum(r["whole closure sign"] is not None for r in group),
            "whole closure is an odd set": sum(r["whole closure sign"] == 1 for r in group),
            "natural birth rule keeps a state": sum(r["natural rule closing sign"] is not None for r in group),
            "natural birth rule closes odd": sum(r["natural rule closing sign"] == 1 for r in group),
            "birth and whole candidate lists coincide": sum(r["locally decidable pairs"] == r["unheld pairs"]
                                                            for r in group),
            "birth choices attain odd": sum(r["birth choices attain odd"] for r in group),
            "whole choices attain odd": sum(r["whole choices attain odd"] for r in group),
            "rows with odd whole-choice sets": sum(bool(r["whole-choice sets by sign and size"]["odd"]) for r in group),
            "rows with odd minimal sets": sum(any(s["sign"] for s in r["minimal sets"]) for r in group),
            "odd whole-choice sets forbidden at birth": sum(r["odd whole-choice sets including a birth-forbidden cell"]
                                                            for r in group),
            "rows with odd whole-choice sets forbidden at birth": [r["start index"] for r in group
                                                                    if r["odd whole-choice sets including a birth-forbidden cell"]],
            "whole choices attain odd and birth choices never attain odd": [r["start index"] for r in group
                if r["whole choices attain odd"] and not r["birth choices attain odd"]],
        }
    birth_odd_without_minimal = [r for r in rows if r["birth choices attain odd"]
                                 and not any(s["sign"] for s in r["minimal sets"])]
    return {"by closing round": rounds,
            "rows attaining odd through birth choices without odd minimal sets": len(birth_odd_without_minimal),
            "of those, rows with odd whole-choice sets": [r["start index"] for r in birth_odd_without_minimal
                                                          if r["whole-choice sets by sign and size"]["odd"]],
            "of those, rows with odd whole-choice sets eligible at birth": [r["start index"] for r in birth_odd_without_minimal
                if r["whole-choice sets by sign and size"]["odd"].total()
                > r["odd whole-choice sets including a birth-forbidden cell"]],
            "rows with odd whole-choice sets where birth choices never attain odd": [r["start index"] for r in rows
                if r["whole-choice sets by sign and size"]["odd"] and not r["birth choices attain odd"]]}


def compare_literal_subsets(n, holders, result):
    """Check the packed calculation against literal omission on small patterns."""
    signs = {"even": Counter(), "odd": Counter()}
    valid = []
    for count in range(n + 1):
        for subset in combinations(range(n), count):
            internal = [tuple(sorted(pair)) for pair in holders if set(pair) <= set(subset)]
            pairs = [(a, b) for a, b in combinations(internal, 2) if not set(a) & set(b)]
            coverage = Counter(frozenset(p) for a, b in pairs for p in product(a, b))
            if not pairs or any(t % 2 for t in coverage.values()):
                continue
            odd = sum(a < c < b < d or c < a < d < b for (a, b), (c, d) in pairs) % 2
            signs["odd" if odd else "even"][count] += 1
            valid.append((frozenset(subset), odd))
    minimal = {tuple(sorted(subset)): odd for subset, odd in valid
               if not any(prior < subset for prior, _ in valid)}
    assert signs == result["whole-choice sets by sign and size"]
    assert minimal == {tuple(item["set"]): item["sign"] for item in result["minimal sets"]}


def pilot(rng):
    """Measure growth on roster prefixes and subset enumeration at increasing sizes."""
    starts = starts_roster()
    for index in (17, 21, 5088):
        holders, dates, round_no = growth(starts[index], 4, 40)
        result = recount(len(dates), holders, dates, rng)
        compare_literal_subsets(len(dates), holders, result)
        print(json.dumps({"census start index": index, "rounds": round_no, **result}), flush=True)
    begin = perf_counter()
    grown_start_count = sum(growth(start, 4, 40) is not None for start in starts[:120])
    print(f"120 census starts gave {grown_start_count} closures in {perf_counter() - begin:.3f} s", flush=True)
    for n in (6, 7, 8):
        begin = perf_counter()
        sample = sampled(n, 100, 20261200 + n)
        sampled_seconds = perf_counter() - begin
        begin = perf_counter()
        closures = sum(growth(start, 10, 3000) is not None for start in sample)
        print(f"{n}-knot starts: 100 sampled in {sampled_seconds:.3f} s; "
              f"{closures} closures in {perf_counter() - begin:.3f} s", flush=True)
    for n in (8, 13, 17):
        holders = [tuple(sorted((k, (k + offset) % n))) for k in range(n) for offset in (1, 2)]
        begin = perf_counter()
        result = recount(n, holders, None, rng)
        print(f"{n} knots: {result['subsets checked']} subsets in {perf_counter() - begin:.3f} s", flush=True)
        if n == 8:
            compare_literal_subsets(n, holders, result)
    print(f"peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.1f} MiB", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    rng = random.Random(46123)
    if args.pilot:
        pilot(rng)
        return
    started = perf_counter()
    result = {}
    population_counts = {}
    timings = {}
    for name in POPULATIONS:
        stage = perf_counter()
        if name == "census starts":
            result[name] = read_growth(name, starts_roster(), 4, 40, rng)
        elif name == "census types":
            result[name] = read_types(rng)
        elif name == "extension":
            result[name] = read_growth(name, extension(), 10, 3000, rng)
        else:
            second = (start for n in (6, 7, 8) for start in sampled(n, 10000, 20261200 + n))
            result[name] = read_growth(name, second, 10, 3000, rng)
        counts = summarize_population(result[name])
        population_counts[name] = counts
        timings[name] = round(perf_counter() - stage, 3)
        print(f"{name}: {counts['rows']} rows in {timings[name]} s; "
              f"odd whole-choice sets at {counts['rows with an odd whole-choice set']} rows, "
              f"odd minimal sets at {counts['rows with an odd minimal set']} rows; "
              f"even whole-choice sets at {counts['rows with an even whole-choice set']} rows, "
              f"even minimal sets at {counts['rows with an even minimal set']} rows", flush=True)

    all_rows = [row for name in POPULATIONS for row in result[name]]
    census = result["census starts"]
    summary = {"weighting": "One vote per census start, census type, or sample draw for row counts. "
                           "One vote per subset of labelled knots in each row for set counts.",
               "populations": population_counts,
               "census birth comparisons": summarize_census(census),
               "published population comparison": compare_population(all_rows),
               "published birth comparison": compare_birth(census),
               "seconds by population": timings, "seconds total": round(perf_counter() - started, 3),
               "peak MiB": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}
    (HERE / "population_counts.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (HERE / "population_rows.jsonl.gz").open("wb") as stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as archive:
            for row in all_rows:
                archive.write((json.dumps(row, separators=(",", ":")) + "\n").encode())
    print(f"{len(all_rows)} rows in {summary['seconds total']} s; peak {summary['peak MiB']} MiB", flush=True)


if __name__ == "__main__":
    main()
