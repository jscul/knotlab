"""Enumerate the small unary-third family and grade its marked scalar tables."""

from collections import Counter, defaultdict
from dataclasses import replace
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess
import sys


PROOFS = Path(__file__).resolve().parents[2]
PRIOR = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001L" / "VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third"
SPEC = spec_from_file_location("unary_predecessor", PRIOR / "census.py")
old = module_from_spec(SPEC)
sys.modules[SPEC.name] = old
SPEC.loader.exec_module(old)
checker, literal, algebra, exact = old.checker, old.literal, old.algebra, old.exact
bits, mask = old.bits, old.mask


def shrinks(shape):
    return 7 + 2 * shape.extra - sum(shape.loose)


def next_layer(layer):
    buckets = defaultdict(list)
    literal_keys = set()
    for owner in layer:
        moves = [(g, 2) for g in owner.groups((2, 3))]
        if not owner.extra:
            moves.extend((g, 3) for g in owner.groups((1,)))
        for group, h in moves:
            shape = replace(owner.grow(group, h), extra=owner.extra or h == 3)
            key = shape.extra, shape.neighbors, shape.loose
            if key in literal_keys:
                continue
            literal_keys.add(key)
            color = old.color_incidence(shape)
            bucket = buckets[shape.extra, color.invariant]
            if not any(next(exact.isometries(previous, color), None) is not None for previous, _ in bucket):
                bucket.append((color, shape))
    return tuple(shape for bucket in buckets.values() for _, shape in bucket)


def table_of(record):
    return dict(zip(old.pairs(record.fixture.width), record.entries, strict=True))


def quotient_of(matrix):
    table = exact.Quotient.make(matrix)
    colors = replace(table.colored, invariant=(hash(table.colored.invariant),))
    return replace(table, colored=colors)


def cases_on_a_table(records, cutoff):
    buckets = defaultdict(list)
    counts = Counter(tables=len(records))
    witnesses = {}

    def grade(left, right, left_matrix, right_matrix, permutation, place):
        assert exact.disagreement(left_matrix, right_matrix, permutation) is None
        different_menu = old.transport(left.menu, permutation) != right.menu
        different_stars = old.transport(left.stars, permutation) != right.stars
        if different_menu:
            counts[f"{place}_opposing_menus"] += 1
            witnesses.setdefault("opposing_menus", (left, right.history, permutation))
        if different_stars:
            live = bool(left.menu or right.menu)
            name = "different_supports_live" if live else "different_supports_empty"
            counts[f"{place}_{name}"] += 1
            witnesses.setdefault(name, (left, right.history, permutation))

    for record in records:
        matrix = record.matrix(cutoff)
        q = quotient_of(matrix)
        bucket = buckets[q.colored.invariant]
        _, _, generators = q.automorphisms()
        counts["self_generators"] += len(generators)
        for image in generators:
            grade(record, record, matrix, matrix, image, "self")
        for other, other_matrix, other_q in bucket:
            counts["cross_candidates"] += 1
            found = next(exact.isometries(q.colored, other_q.colored), None)
            if found is not None:
                counts["cross_exact_lifts"] += 1
                grade(record, other, matrix, other_matrix, q.lift(other_q, found), "cross")
        bucket.append((record, matrix, q))
    return dict(counts), witnesses


def named_witness(case, cutoff):
    record, rival, permutation = case
    out = old.witness(*case, cutoff=cutoff)
    mapped = algebra.span(old.transport(record.stars, permutation))
    rival_space = algebra.span(mask(row) for _, row in rival)
    out["same_equation_space_under_the_map"] = mapped == rival_space
    out["self_isometry"] = record.history == rival
    return out


def forced_space(record):
    source = table_of(record)
    visible = {pair: value if value <= 5 else None for pair, value in source.items()}
    known, remaining, _, rounds = algebra.force_from_table(visible, record.fixture.width, 5)
    physical = algebra.span(record.stars)
    assert known <= physical and algebra.rank(physical) == record.fixture.sites
    return algebra.rank(known), len(remaining), rounds


def large_five_shores(history):
    supports = [mask(row) for _, row in history]
    span = [0]
    result = []
    for selected in range(1, 1 << len(supports)):
        first = selected & -selected
        word = span[selected ^ first] ^ supports[first.bit_length() - 1]
        span.append(word)
        if selected.bit_count() >= 3 and word.bit_count() == 5:
            result.append((bits(selected), bits(word)))
    return result


def rank_screen(records, witnesses):
    ranks = Counter()
    cuts = Counter()
    for record in records:
        t = shrinks(record.fixture)
        if t <= 1:
            continue
        forced, remaining, _ = forced_space(record)
        ranks[(t, bool(record.menu), forced, remaining)] += 1
        large = large_five_shores(record.history)
        cuts[(t, bool(record.menu), len(large))] += 1
        if large:
            key = "first_large_five_with_live_menu" if record.menu else "first_large_five_with_empty_menu"
            if key not in witnesses:
                table, bonds, menu = checker.measure(record.history, independent=True)
                assert record.entries == tuple(table[pair] for pair in old.pairs(record.fixture.width))
                assert all(mask(word) in bonds for _, word in large)
                trace = checker.replay(record.history)
                special = next(i for i, row in enumerate(trace[3:], 3) if len(row["fresh"]) == 3)
                witnesses[key] = {"width": record.fixture.width, "history": old.summary(record.history),
                                  "legal_triples": sorted(menu), "forced_rank": forced, "short_shores": large,
                                  "third_unary_index": special, "all_pair_entries": record.entries}
        if forced < record.fixture.sites and "first_rank_deficit" not in witnesses:
            witnesses["first_rank_deficit"] = {"width": record.fixture.width,
                                              "history": old.summary(record.history), "has_triple": bool(record.menu),
                                              "forced_rank": forced, "remaining_short_bonds": remaining,
                                              "large_five_shores": large, "all_pair_entries": record.entries}
    return {"rank_group_columns": ["shrinks", "has_legal_triple", "forced_rank", "unresolved_short_bonds", "types"],
            "rank_group_counts": [(*row, n) for row, n in sorted(ranks.items())],
            "large_five_group_columns": ["shrinks", "has_legal_triple", "number_of_large_five_shores", "types"],
            "large_five_group_counts": [(*row, n) for row, n in sorted(cuts.items())]}


def direct_literal_controls(records):
    # This arm expands the raw row supports through the lower witness width.
    deck = [(checker.grow(checker.SEED, ((0,), (i,)), (3, 3)), False) for i in (0, 1)]
    for _ in range(6):
        grown = []
        for history, used_extra in deck:
            holders, adjacent = literal.incidence(history)
            loose = defaultdict(list)
            for bit, sites in holders.items():
                if len(sites) == 1:
                    loose[sites[0]].append(bit)
            for p, h in ((2, 2), (3, 2)) if used_extra else ((2, 2), (3, 2), (1, 3)):
                for parents in combinations(sorted(loose), p):
                    if literal.legal(parents, adjacent):
                        operands = tuple(min(loose[parent]) for parent in parents)
                        grown.append((checker.named_step(history, operands, h, len(holders)), used_extra or h == 3))
        deck = grown

    indexed = defaultdict(list)
    for i, record in enumerate(records):
        color = old.color_incidence(record.fixture)
        indexed[color.invariant].append((i, color))
        known, _, menu = checker.measure(record.history, independent=True)
        assert record.entries == tuple(known[pair] for pair in old.pairs(22))
        assert record.menu == frozenset(map(mask, menu))
    reached = set()
    count = 0
    for history, used_extra in deck:
        if used_extra:
            count += 1
            owners, adjacent = literal.incidence(history)
            names = tuple(site for site, _ in history)
            graph = tuple(mask(i for i, other in enumerate(names) if other in adjacent[site]) for site in names)
            loose = tuple(sum(group == [site] for group in owners.values()) for site in names)
            color = old.color_incidence(old.Fixture(graph, loose, True, ()))
            match, = (i for i, q in indexed[color.invariant] if next(exact.isometries(q, color), None) is not None)
            reached.add(match)
    assert reached == set(range(len(records)))
    return {"literal_histories_at_width_22": count, "types_reached": len(reached),
            "independent_pair_entries": len(records) * len(old.pairs(22))}


def append_unary_control():
    j = old.previous.load_source("frontier.json")["sharp_distance_four"]
    start = old.previous.named(j["junction_supports"])
    extra = checker.named_step(start, (23,), 3, 25)
    trace = checker.replay(extra)
    assert [(len(row["operands"]), len(row["fresh"])) for row in trace[3:] if len(row["fresh"]) == 3] == [(1, 3)]
    table, _, menu = checker.measure(extra, independent=True)
    witness = old.previous.transposition(table, menu, 28, (19, 20), (12, 20, 21))
    assert witness["changed_entries"]["D3"] == 0 and witness["changed_entries"]["D4"] == 8
    return {"history": old.summary(extra), "legal_triples": sorted(menu), **witness}


def proper_five_controls():
    """Retain the complete old five-bit bond and vary the holder of the added unary site."""
    archive = old.previous.load_source("frontier.json")["closure"]["first_histories_by_shrinking_joins"]
    prefix = old.previous.named(archive["2"])
    holders, adjacent = literal.incidence(prefix)
    assert len(holders) == 27 and not literal.direct_triples(holders, adjacent)
    loose = defaultdict(list)
    for bit, sites in sorted(holders.items()):
        if len(sites) == 1:
            loose[sites[0]].append(bit)
    boundary = tuple(sorted(bit for group in loose.values() for bit in group))
    cases = []
    tables = []
    for bit in sorted(min(group) for group in loose.values()):
        history = checker.named_step(prefix, (bit,), 3, 27)
        replay = old.summary(history)
        assert replay["third_three_fresh_parent_count"] == 1
        table, bonds, menu = checker.measure(history, independent=True)
        assert large_five_shores(history) == [(tuple(range(len(prefix))), boundary)]
        assert mask(boundary) in bonds and not menu
        visible = {pair: k if k <= 5 else None for pair, k in table.items()}
        known, residual, _, _ = algebra.force_from_table(visible, 30, 5)
        physical = frozenset(mask(row) for _, row in history)
        assert known == algebra.span(physical) and not residual
        realized, audit = old.previous.physical_realizations(known)
        rival, = realized
        assert frozenset(mask(row) for _, row in rival) == physical
        cases.append({"third_unary_input": bit, "history": replay, "legal_triples": [],
                      "forced_rank": algebra.rank(known), "unresolved_short_bonds": len(residual),
                      "arbitrary_rival_support_search": audit,
                      "K_upper_triangle": [table[pair] for pair in old.pairs(30)]})
        tables.append((bit, table))
    comparisons = [{"third_unary_inputs": (left, right),
                    "D4_isometry": checker.one_isometry(a, b, 5),
                    "full_isometry": checker.one_isometry(a, b)}
                   for (left, a), (right, b) in combinations(tables, 2)]
    return {"width": 30, "proper_shore": tuple(range(len(prefix))), "boundary": boundary,
            "each_full_table_pairs": len(old.pairs(30)), "placements": cases, "comparisons": comparisons}


def run(max_width, engine):
    stages = []
    witnesses = {}
    layer = old.starters()
    for sites in range(4, (max_width - 4) // 2 + 1):
        layer = next_layer(layer)
        sources = [shape for shape in layer if shape.extra]
        records = old.measured(sources, engine)
        width = 2 * sites + 4
        by_type = Counter((shrinks(rec.fixture), bool(rec.menu)) for rec in records)
        row = {"width": width, "physical_types": len(records),
               "types_by_shrinks_and_legal_triple": [(*shape, n) for shape, n in sorted(by_type.items())]}
        if "first_positive" not in witnesses:
            positive = next((record for record in records if record.menu), None)
            if positive:
                table, _, menu = checker.measure(positive.history, independent=True)
                assert positive.entries == tuple(table[pair] for pair in old.pairs(width))
                witnesses["first_positive"] = {"width": width, "history": old.summary(positive.history),
                                               "legal_triples": sorted(menu)}
        if "first_D3_opposition" not in witnesses and any(rec.menu for rec in records):
            row["D3"], found, self_map, _ = old.table_screen(records, 4, False)
            if found:
                witnesses["first_D3_opposition"] = named_witness(found, 4)
            if self_map and self_map != found:
                witnesses["first_D3_self_opposition"] = named_witness(self_map, 4)
        for mode, cutoff in (("D4", 5), ("full", None)):
            row[mode], examples = cases_on_a_table(records, cutoff)
            for name, example in examples.items():
                key = f"first_{mode}_{name}"
                if key not in witnesses:
                    witnesses[key] = named_witness(example, cutoff)
        row["rank_and_geometry"] = rank_screen(records, witnesses)
        if width == 22:
            row["independent_literal_validation"] = direct_literal_controls(records)
        stages.append(row)
        print(f"width {width}: {len(records)} types", file=sys.stderr, flush=True)
    return {"freeze": "60507e63e", "maximum_census_width": max_width, "stages": stages, "witnesses": witnesses,
            "unary_append_J_control": append_unary_control(), "proper_five_control": proper_five_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=28)
    args = parser.parse_args()
    if not 22 <= args.width <= 28 or args.width % 2:
        parser.error("width must be even and between 22 and 28")
    with TemporaryDirectory(prefix="unary-third-census-") as tmp:
        engine = Path(tmp) / "measure"
        subprocess.run(["c++", "-std=c++20", "-O2", "-D_GLIBCXX_ASSERTIONS", "-pthread",
                        PRIOR / "census.cpp", "-o", engine], check=True)
        result = run(args.width, engine)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
