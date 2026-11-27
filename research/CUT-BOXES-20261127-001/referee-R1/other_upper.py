"""Exhibit agreement readings on a registered cut using directly implied lower clauses."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
from itertools import combinations, product
import json
from operator import and_
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent.parent / "UPPER-GROWN-20261127-001"
GROUPS = ((0, 1), (2, 3), (4, 5))
CROSS = tuple(product(*GROUPS))


def read_cases():
    def rows(folder, pattern):
        return [json.loads(line) for path in sorted(folder.glob(pattern))
                for line in path.read_text().splitlines()]

    cut = sorted(rows(HERE.parent / "out", "cut_*.jsonl"), key=lambda row: row["graph"])
    closed = sorted((r for r in rows(PREVIOUS / "out", "cubic_12_*.jsonl") if r["boxes"]),
                    key=lambda row: row["links"])
    assert len(closed) == len(cut) == 49
    for index, (record, control) in enumerate(zip(cut, closed, strict=True)):
        assert index == record["graph"] and control["boxes"] == record["boxes before"]
        links = [tuple(pair) for pair in control["links"]]
        endpoints = tuple(record["knots at its ends"])
        links = sorted(tuple(sorted(pair)) for pair in links)
        cut_label = links.index(endpoints)
        knots = tuple(tuple(18 if link == cut_label and i == endpoints[1] else link
                            for link, pair in enumerate(links) if i in pair) for i in range(12))
        assert sorted(Counter(v for knot in knots for v in knot).values()) == [1, 1] + [2] * 17
        yield index, knots, endpoints, cut_label


def source_clauses(knots, limit):
    """Each of three laws enforces a difference around an odd cycle if all three readings are 1.

    The raw members of a reading are the pair of places in one source law and the
    single place from the preceding law. The pair and the single can share a member.
    """
    masks = [[(sum(1 << v for v in knot if v != one), 1 << one) for one in knot]
             for knot in knots]
    result = {}
    for triple in list(combinations(range(len(knots)), 3))[:limit]:
        i, j, k = triple
        for a, b, c in ((i, j, k), (i, k, j)):
            for (paired_a, single_a), (paired_b, single_b), (paired_c, single_c) in product(
                    masks[a], masks[b], masks[c]):
                x, y, z = paired_a | single_c, paired_b | single_a, paired_c | single_b
                if (x & y) or (x & z) or (y & z):
                    continue
                result.setdefault(tuple(sorted((x, y, z))), triple)
    return result


def linked_pairs(clauses):
    by_carrier = defaultdict(set)
    for x, y, z in clauses:
        by_carrier[x].add((y, z))
        by_carrier[y].add((x, z))
        by_carrier[z].add((x, y))
    return by_carrier


def groupings(by_carrier, pair_limit, total_overlap):
    """Fix a pair with shared members, then read cycles of four in its common partners."""
    keys = sorted(by_carrier)
    roots = ((x, y) for x, y in combinations(keys, 2) if x & y)
    for step, (first, second) in enumerate(roots):
        if step >= pair_limit:
            return
        overlap = (first & second).bit_count()
        if overlap > total_overlap:
            continue
        common = by_carrier[first] & by_carrier[second]
        if len(common) < 4:
            continue
        adjacent = defaultdict(set)
        for a, b in common:
            adjacent[a].add(b)
            adjacent[b].add(a)
        for a0, a1 in combinations(sorted(adjacent), 2):
            left = (a0 & a1).bit_count()
            if left + overlap > total_overlap:
                continue
            for b0, b1 in combinations(sorted(adjacent[a0] & adjacent[a1]), 2):
                if (b0, b1) < (a0, a1):
                    continue
                right = (b0 & b1).bit_count()
                if left + right + overlap != total_overlap:
                    continue
                if any(other < (first, second) and (other[0] & other[1])
                       for other in ((a0, a1), (b0, b1))):
                    continue
                yield (first, second, a0, a1, b0, b1)


def cols(n):
    size = 1 << n
    # Repeat each short 0/1 pattern in whole bytes before converting to a bit set.
    result = [int.from_bytes(bytes([pat]) * (size // 8), 'little') for pat in (170, 204, 240)]
    for i in range(3, n):
        block = 1 << (i - 3)
        result.append(int.from_bytes((bytes(block) + b'\xff' * block) * (size // (16 * block)),
                                     'little'))
    return (1 << size) - 1, result


def members(mask):
    return tuple(i for i in range(mask.bit_length()) if mask & (1 << i))


def equality(carrier, raw, full):
    first, *rest = carrier
    return reduce(and_, (full ^ (raw[first] ^ raw[j]) for j in rest), full)


def cells(ok, readings):
    words = [ok]
    for bit in readings:
        words = [part for w in words for part in (w & ~bit, w & bit)]
    return words


def counts(ok, readings):
    return [w.bit_count() for w in cells(ok, readings)]


def allowed(n, knots):
    full, raw = cols(n)
    laws = [full ^ equality(k, raw, full) for k in knots]
    return full, raw, laws, reduce(and_, laws, full)


def mixed(partitions, reading):
    return sum(bool(p & reading) and bool(p & ~reading) for p in partitions)


def three_words_missing(n):
    return tuple(format(i, "03b") for i, c in enumerate(n) if not c)


def describe(knots, names, which_three, raw_data):
    full, raw, laws, ok = raw_data
    carrier = [members(v) for v in names]
    raw_sets = [set(c) for c in carrier]
    assert all(raw_sets[a].isdisjoint(raw_sets[b])
               for g, h in combinations(GROUPS, 2) for a, b in product(g, h))
    lower = [equality(c, raw, full) for c in carrier]
    up = [full ^ (lower[a] ^ lower[b]) for a, b in GROUPS]
    physical = counts(ok, up)
    if three_words_missing(physical) != ("000",):
        return None
    if any(three_words_missing(counts(ok, [lower[i] for i in triple])) != ("111",)
           for triple in CROSS):
        return None
    if any(min(counts(ok, [lower[a], lower[b]])) == 0 for a, b in GROUPS):
        return None
    source_fixes = [cells(ok, [raw[i] for i in knot]) for knot in knots]
    unread_lower = [[mixed(fix, bit) for bit in lower] for fix in source_fixes]
    lower_fixes = [cells(ok, [lower[i] for i in triple]) for triple in CROSS]
    unread_upper = [[mixed(fix, bit) for bit in up] for fix in lower_fixes]
    if min(map(min, unread_lower + unread_upper)) == 0:
        return None
    flips = [[(ok & ~raw[i] & (ok >> (1 << i)) &
               (bit ^ (bit >> (1 << i)))).bit_count() for i in c]
             for c, bit in zip(carrier, lower)]
    if min(map(min, flips)) == 0:
        return None
    lost = reduce(and_, (full ^ u for u in up), full)
    restored = [(reduce(and_, laws[:i] + laws[i + 1:], lost)).bit_count()
                for i in range(len(laws))]
    abstract, lower_bits = cols(6)
    clauses = [abstract ^ reduce(and_, (lower_bits[i] for i in triple), abstract) for triple in CROSS]
    clause_j = reduce(and_, clauses, abstract)
    upper_bits = [equality(pair, lower_bits, abstract) for pair in GROUPS]
    abstract_upper = counts(clause_j, upper_bits)
    omit = [counts(reduce(and_, clauses[:i] + clauses[i + 1:], abstract), upper_bits)[0]
            for i in range(len(clauses))]
    assert omit == [1] * 8
    assert three_words_missing(abstract_upper) == ("000",)
    traces = [which_three[tuple(sorted(names[i] for i in triple))] for triple in CROSS]
    source_free = counts(full, up)
    assert min(source_free) > 0
    loose = [d for d, count in Counter(v for knot in knots for v in knot).items() if count == 1]
    return {
        "knots": knots, "loose_distinctions": sorted(loose),
        "lower_agreement_carriers": carrier,
        "raw_overlaps_within_upper_comparisons": [sorted(raw_sets[a] & raw_sets[b]) for a, b in GROUPS],
        "raw_overlaps_across_upper_comparisons": 0,
        "lower_bonds_in_order": CROSS,
        "each_lower_bond_source_three_sufficient_to_exclude_111": traces,
        "source_counts_by_each_lower_triple": [counts(ok, [lower[i] for i in tri]) for tri in CROSS],
        "lower_pair_counts_inside_each_upper_comparison": [counts(ok, [lower[i] for i in pair]) for pair in GROUPS],
        "recorded_source_states": ok.bit_count(), "source_counts_by_six_lower_readings": counts(ok, lower),
        "source_counts_by_upper_word": physical, "unconstrained_source_counts_by_upper_word": source_free,
        "upper_pair_projection_counts": [counts(ok, [up[i], up[j]]) for i, j in combinations(range(3), 2)],
        "upper_000_after_each_source_law_deletion": restored,
        "source_knot_fixes_allowing_both_values_of_each_lower_reading": unread_lower,
        "single_distinction_changes_flipping_each_lower_reading": flips,
        "lower_bond_fixes_allowing_both_values_of_each_upper_reading_on_source": unread_upper,
        "lower_bond_fixes_allowing_both_values_of_each_upper_reading_on_eight_bonds": [
            [mixed(cells(clause_j, [lower_bits[i] for i in triple]), bit) for bit in upper_bits] for triple in CROSS],
        "six_reading_words_allowed_by_eight_lower_bonds": clause_j.bit_count(),
        "eight_lower_bonds_counts_by_upper_word": abstract_upper,
        "upper_000_after_each_lower_bond_deletion_on_six_free_readings": omit,
    }


def search(index, knots, endpoints, label, subset, pair_limit, max_overlap):
    started = perf_counter()
    candidates = source_clauses(knots, subset)
    by_carrier = linked_pairs(candidates)
    raw_data = allowed(19, knots)
    tally = Counter()
    for overlap in range(1, max_overlap + 1):
        for names in groupings(by_carrier, pair_limit, overlap):
            tally[overlap] += 1
            found = describe(knots, names, candidates, raw_data)
            if found:
                return {"registered_position": index, "cut_knots": endpoints, "cut_in_lexicographic_labels": label,
                        "three_law_candidates": len(candidates), "groupings_tested": tally,
                        "seconds": round(perf_counter() - started, 4), "witness": found}
    return {"registered_position": index, "cut_knots": endpoints, "cut_in_lexicographic_labels": label,
            "three_law_candidates": len(candidates), "groupings_tested": tally, "witness": None,
            "seconds": round(perf_counter() - started, 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--count", default=1, type=int)
    parser.add_argument("--source-triples", type=int, default=220)
    parser.add_argument("--compared-pairs", type=int, default=1_000_000)
    parser.add_argument("--max-overlap", type=int, default=3)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows = []
    for case in list(read_cases())[args.start:args.start + args.count]:
        r = search(*case, args.source_triples, args.compared_pairs, args.max_overlap)
        rows.append(r)
        print(r["registered_position"], r["three_law_candidates"], dict(r["groupings_tested"]),
              bool(r["witness"]), r["seconds"], flush=True)
    if args.out:
        args.out.write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
