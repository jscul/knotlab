"""Check the first reached not-all-equal types and their exact disagreement tables."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations
import json
from math import comb, lcm, prod
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts"
ARCHIVE = (
    ARTIFACTS / "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C"
    / "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C-E001_pair_births"
)
RECORDED = (
    ARTIFACTS / "TWO-COUNTINGS-20261125-001A"
    / "TWO-COUNTINGS-20261125-001A-E001_two_countings/part5_p9.json"
)


def mask(names):
    return sum(1 << name for name in names)


def allows(state, places):
    return (state & places) not in (0, places)


def ordinary_groups(live, witnessed):
    joinable = {pair for members in witnessed for pair in combinations(sorted(members), 2)}
    largest = []
    for size in range(len(live), 2, -1):
        for trial in combinations(sorted(live), size):
            group = frozenset(trial)
            if any(group <= previous for previous in largest) or any(group <= s for s in witnessed):
                continue
            if all(pair in joinable for pair in combinations(trial, 2)):
                largest.append(group)
    return largest + [
        frozenset(pair) for pair in sorted(joinable)
        if not any(set(pair) <= group for group in largest)
    ]


def ordinary_step(rows):
    row_sets = [set(row) for row in rows]
    holders = Counter(name for row in row_sets for name in row)
    loose = {i: sum(holders[name] == 1 for name in row) for i, row in enumerate(row_sets)}
    live = {i for i, count in loose.items() if count}
    if not live:
        return "closed", []
    witnessed = [{i for i in live if i != j and row_sets[i] & row} for j, row in enumerate(row_sets)]
    groups = ordinary_groups(live, witnessed)
    owing = Counter(i for group in groups for i in group)
    if any(owing[i] > loose[i] for i in live):
        return "stall", []
    parents = groups + [frozenset({i}) for i in sorted(live) for _ in range(loose[i] - owing[i])]
    return "births", parents


def check_growth(row, source, newborns, next_groups):
    status, parents = ordinary_step(source)
    assert status == row["first_status"] == "births"
    assert len(parents) == row["first_birth_count"] == len(newborns)
    child_rosters = [{c for c, p in enumerate(parents) if i in p} for i in range(len(source))]
    demand = Counter(c for group in ordinary_groups(range(len(parents)), child_rosters) for c in group)
    expected = Counter((p, max(demand[c], 3 - len(p), 1)) for c, p in enumerate(parents))
    stage_groups = Counter()
    for old, fresh in newborns:
        parent_sets = [{i for i, source_row in enumerate(source) if name in source_row} for name in old]
        assert all(len(parents_at_name) == 1 for parents_at_name in parent_sets)
        group = frozenset().union(*parent_sets)
        assert len(group) == len(old)
        stage_groups[group, len(fresh)] += 1
    assert expected == stage_groups == Counter((frozenset(p), f) for p, f in row["first_births"])
    status, next_parents = next_groups
    assert status == row["next_status"]
    assert len(next_parents) == row["next_birth_count"]
    assert Counter(next_parents) == Counter(frozenset(p) for p, _ in row["next_births"])


def check_source(source, source_width, source_states, connected):
    holders = Counter(name for places in source for name in places)
    assert set(holders) == set(range(source_width))
    assert set(holders.values()) <= {1, 2}
    assert all(len(places) >= 3 and len(set(places)) == len(places) for places in source)
    reached = {0}
    while True:
        older = reached.copy()
        names = {name for i in reached for name in source[i]}
        reached.update(i for i, row in enumerate(source) if names.intersection(row))
        if reached == older:
            break
    assert (len(reached) == len(source)) == connected

    masks = [mask(row) for row in source]
    for i, places in enumerate(masks):
        # Compare the allowed projections with the full local rule, and
        # require a state that the rule excludes but the other rules allow.
        actual = {o & places for o in source_states}
        intended = {o & places for o in range(1 << source_width) if allows(o, places)}
        assert actual == intended
        assert any(
            not allows(o, places) and all(allows(o, other) for j, other in enumerate(masks) if j != i)
            for o in range(1 << source_width)
        )


def exact_tables(source_states, newborns, width):
    # Completion count and one-place counts in a newborn are obtained by
    # deleting the single forbidden assignment when its old places agree.
    owner = {v: i for i, (_, fresh) in enumerate(newborns) for v in fresh}
    source_masks = [mask(old) for old, _ in newborns]
    fresh_counts = [len(fresh) for _, fresh in newborns]
    owner_by_name = [owner.get(v) for v in range(width)]
    pairs = list(combinations(range(width), 2))
    conditional = []
    for state in source_states:
        old_values = [state & places for places in source_masks]
        sizes = [(1 << f) - int(val in (0, places)) for f, val, places
                 in zip(fresh_counts, old_values, source_masks, strict=True)]
        ones = [(1 << (f - 1)) - int(val == places) for f, val, places
                in zip(fresh_counts, old_values, source_masks, strict=True)]
        conditional.append((state, sizes, ones, prod(sizes)))

    common = lcm(*(total for _, _, _, total in conditional))
    start = [0] * len(pairs)
    finish = [0] * len(pairs)
    total_words = 0
    for state, sizes, ones, total in conditional:
        total_words += total
        multiplier = common // total
        individual = [(1, (state >> v) & 1) if i is None else (sizes[i], ones[i])
                      for v, i in enumerate(owner_by_name)]
        for k, (i, j) in enumerate(pairs):
            group = owner_by_name[i]
            if group is not None and group == owner_by_name[j]:
                # The single excluded word, if present, agrees on both places.
                different = (total // sizes[group]) * (1 << (fresh_counts[group] - 1))
            else:
                di, oi = individual[i]
                dj, oj = individual[j]
                different = (total // (di * dj)) * (oi * (dj - oj) + oj * (di - oi))
            start[k] += different * multiplier
            finish[k] += different
    start_rates = tuple(Fraction(count, common * len(source_states)) for count in start)
    return start_rates, total_words, finish


def enumerate_small(stage_rows, source_width, width):
    complete = np.arange(1 << width, dtype=np.int64)
    for places in stage_rows:
        restricted = complete & mask(places)
        complete = complete[(restricted != 0) & (restricted != mask(places))]
    prefixes = complete & ((1 << source_width) - 1)
    sizes = np.bincount(prefixes)
    common = lcm(*(int(v) for v in np.unique(sizes[sizes > 0])))
    denominator = common * np.count_nonzero(sizes)
    assert denominator < 2**61
    weights = common // sizes[prefixes]
    bits = (complete[:, None] >> np.arange(width)) & 1
    marginal = weights @ bits
    both = bits.T @ (weights[:, None] * bits)
    return tuple(Fraction(int(marginal[i] + marginal[j] - 2 * both[i, j]), int(denominator))
                 for i, j in combinations(range(width), 2))


def read_case(scope, index, row):
    source_width = row["source_width"]
    stage_width = row["stage_width"]
    source = row["source_rows"]
    stage = row["stage_rows"]
    assert stage[:len(source)] == source
    newborns = [
        ([v for v in places if v < source_width], [v for v in places if v >= source_width])
        for places in stage[len(source):]
    ]
    assert all(old and fresh for old, fresh in newborns)
    assert sorted(v for _, fresh in newborns for v in fresh) == list(range(source_width, stage_width))
    source_masks = [mask(places) for places in source]
    source_states = [s for s in range(1 << source_width) if all(allows(s, m) for m in source_masks)]
    assert source_states
    check_source(source, source_width, source_states, scope == "connected")
    next_groups = ordinary_step(stage)
    check_growth(row, source, newborns, next_groups)
    start_rates, total, finish_counts = exact_tables(source_states, newborns, stage_width)
    assert total == row["total_words"]
    assert finish_counts == row["pair_counts"]
    direct = stage_width <= 20
    if direct:
        assert start_rates == enumerate_small(stage, source_width, stage_width)
    return {
        "scope": scope,
        "index": index,
        "source_rows": source,
        "stage_width": stage_width,
        "first_birth_count": len(newborns),
        "next_status": next_groups[0],
        "next_birth_count": len(next_groups[1]),
        "source states": len(source_states),
        "start table": start_rates,
        "finish table": tuple(Fraction(count, total) for count in finish_counts),
        "finish total": total,
        "full assignment enumeration": direct,
    }


def matrix(width, table):
    weights = [[None] * width for _ in range(width)]
    for (i, j), rate in zip(combinations(range(width), 2), table, strict=True):
        weights[i][j] = weights[j][i] = rate
    return weights


def equivalent(width, a, b):
    left, right = matrix(width, a), matrix(width, b)
    left_profiles = [tuple(sorted(rate for rate in row if rate is not None)) for row in left]
    right_profiles = [tuple(sorted(rate for rate in row if rate is not None)) for row in right]
    if Counter(left_profiles) != Counter(right_profiles):
        return False
    initial_domains = [{i for i in range(width) if left_profiles[u] == right_profiles[i]}
                       for u in range(width)]

    def extend(domains):
        if not domains:
            return True
        u = min(domains, key=lambda a: len(domains[a]))
        for v in sorted(domains[u]):
            rest = {
                x: {y for y in ds if y != v and left[u][x] == right[v][y]}
                for x, ds in domains.items() if x != u
            }
            if all(rest.values()) and extend(rest):
                return True
        return False

    return extend(dict(enumerate(initial_domains)))


def compare_tables(rows, field):
    named = defaultdict(list)
    by_width = defaultdict(list)
    histogram = defaultdict(list)
    totals = defaultdict(list)
    row_sums = set()
    labels = []
    for row in rows:
        width, table = row["stage_width"], row[field]
        label = (row["scope"], row["index"])
        outcome = (row["next_status"], row["next_birth_count"])
        labels.append(label)
        named[width, table].append(label)
        by_width[width].append(outcome)
        histogram[width, tuple(sorted(table))].append((label, table))
        totals[width, sum(table)].append((label, outcome))
        sums = [sum(rate for rate in row if rate is not None) for row in matrix(width, table)]
        row_sums.add((width, tuple(sorted(sums))))
    groups_sharing_named = [group for group in named.values() if len(group) > 1]
    groups_sharing_permuted = []
    iso_calls = 0
    conflicts = []
    outcomes = {(row["scope"], row["index"]): (row["next_status"], row["next_birth_count"])
                for row in rows}
    for (width, _), candidates in histogram.items():
        if len(candidates) <= 1:
            continue
        groups = []
        for label, table in candidates:
            for representative, group in groups:
                iso_calls += 1
                if equivalent(width, table, representative):
                    group.append(label)
                    break
            else:
                groups.append((table, [label]))
        for _, group in groups:
            if len(group) > 1:
                groups_sharing_permuted.append(group)
                if len({outcomes[label] for label in group}) > 1:
                    conflicts.append(group)

    width_count = sum(comb(len(group), 2) for group in by_width.values())
    width_contested_count = sum(
        comb(len(group), 2) - sum(comb(n, 2) for n in Counter(group).values()) for group in by_width.values()
    )
    equal_totals = [
        {"width": width, "sum of rates": str(total), "types and next outcomes": group}
        for (width, total), group in totals.items() if len(group) > 1
    ]
    return {
        "all distinct type pairs": comb(len(labels), 2),
        "same reached width pairs": width_count,
        "same reached width with different next outcomes, pairs": width_contested_count,
        "reached widths": len(by_width),
        "reached widths with several next outcomes": sorted(
            width for width, group in by_width.items() if len(set(group)) > 1
        ),
        "distinct rate sums at their widths": len(totals),
        "groups sharing reached width and sum of rates": equal_totals,
        "same-width equal-sum groups with different outcomes": sum(
            len({outcome for _, outcome in group["types and next outcomes"]}) > 1
            for group in equal_totals
        ),
        "distinct multisets of row sums at their widths": len(row_sums),
        "distinct rate multisets at their widths": len(histogram),
        "exact renaming comparisons after rate-multiset checks": iso_calls,
        "groups sharing a named table": groups_sharing_named,
        "groups sharing a table under renaming": groups_sharing_permuted,
        "same-table pairs under renaming": sum(comb(len(group), 2) for group in groups_sharing_permuted),
        "distinct tables under renaming": len(labels) - sum(len(group) - 1 for group in groups_sharing_permuted),
        "same-table conflicts in next outcome": conflicts,
    }


def comparison_controls():
    pairs = tuple(combinations(range(6), 2))
    a = tuple(Fraction(1, 3) if (j - i) in (1, 5) else Fraction(2, 3) for i, j in pairs)
    b = tuple(Fraction(1, 3) if i // 3 == j // 3 else Fraction(2, 3) for i, j in pairs)
    perm = (2, 0, 4, 1, 5, 3)
    weights = matrix(6, a)
    renamed = tuple(weights[perm[i]][perm[j]] for i, j in pairs)
    assert a != renamed and equivalent(6, a, renamed)
    assert sorted(a) == sorted(b) and not equivalent(6, a, b)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    timing = parser.add_mutually_exclusive_group()
    timing.add_argument("--limit", type=int, help="check this many types of each scope")
    timing.add_argument("--timing-sample", action="store_true", help="check the smallest, widest and largest enumerated types")
    parser.add_argument("--output", type=Path, default=HERE / "types.json")
    args = parser.parse_args()
    with gzip.open(ARCHIVE / "census_cases.json.gz", "rt") as stream:
        connected = [r for r in json.load(stream)["nae"] if r["first_status"] == "births"]
    disconnected = json.loads((ARCHIVE / "disconnected.json").read_text())["nae"]["cases"]
    recorded = {(r["scope"], r["index"]): r for r in json.loads(RECORDED.read_text())["rows"]}
    comparison_controls()
    rows = []
    differences = []
    for scope, cases in (("connected", connected), ("disconnected", disconnected)):
        selected = list(enumerate(cases))[:args.limit]
        if args.timing_sample:
            selected = sorted({
                0,
                max(range(len(cases)), key=lambda i: cases[i]["stage_width"]),
                max((i for i in range(len(cases)) if cases[i]["stage_width"] <= 20),
                    key=lambda i: cases[i]["total_words"]),
            })
            selected = [(index, cases[index]) for index in selected]
        for index, case in selected:
            row = read_case(scope, index, case)
            reference = recorded[scope, index]
            for key, value in row.items():
                if key not in reference:
                    continue
                if key == "start table":
                    value = [str(rate) for rate in value]
                if value != reference[key]:
                    differences.append([scope, index, key])
            rows.append(row)
    changes = [(row["scope"], row["index"]) for row in rows if row["start table"] != row["finish table"]]
    changes_after_renaming = [
        (row["scope"], row["index"]) for row in rows
        if sorted(row["start table"]) != sorted(row["finish table"])
        or not equivalent(row["stage_width"], row["start table"], row["finish table"])
    ]
    result = {
        "types": len(rows),
        "connected": sum(row["scope"] == "connected" for row in rows),
        "disconnected": sum(row["scope"] == "disconnected" for row in rows),
        "ordinary first births and next birth counts checked": len(rows),
        "archive finish counts compared": len(rows),
        "start tables compared with full assignment enumeration": sum(row["full assignment enumeration"] for row in rows),
        "disagreements with recorded start tables and row fields": differences,
        "types whose named pair tables change between countings": len(changes),
        "types whose pair tables change between countings under renaming": len(changes_after_renaming),
        "unchanged named pair tables": [[row["scope"], row["index"]] for row in rows
                                         if (row["scope"], row["index"]) not in changes],
        "next outcome counts": {str(key): value for key, value in Counter(
            (row["next_status"], row["next_birth_count"]) for row in rows
        ).items()},
        "start": compare_tables(rows, "start table"),
        "finish": compare_tables(rows, "finish table"),
        "rows": rows,
    }
    args.output.write_text(json.dumps(result, default=str, indent=2) + "\n")
    print(f"{len(rows)} types, {len(differences)} differences from recorded rows")
    if differences:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
