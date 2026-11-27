"""Check source attribution, the same readings before opening, and all knot-test roles."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from functools import reduce
from io import StringIO
from itertools import combinations, product
import json
from operator import and_
from pathlib import Path
import sys

from other_upper import (CROSS, GROUPS, HERE, allowed, cells, counts, equality, mixed,
                         three_words_missing)


def grouping_components(knots, keep):
    parts = []
    unseen = set(keep)
    while unseen:
        part = {unseen.pop()}
        todo = list(part)
        while todo:
            i = todo.pop()
            neighbours = {j for j in unseen if set(knots[i]).intersection(knots[j])}
            part.update(neighbours)
            unseen.difference_update(neighbours)
            todo.extend(neighbours)
        parts.append(sorted(part))
    return sorted(parts)


def audit_source(record):
    w = record["witness"]
    knots = w["knots"]
    carriers = w["lower_agreement_carriers"]
    full, raw, laws, ok = allowed(19, knots)
    lower = [equality(c, raw, full) for c in carriers]
    upper = [equality(g, lower, full) for g in GROUPS]
    with_one_omitted = [reduce(and_, laws[:i] + laws[i + 1:], full) for i in range(len(laws))]
    required = [i for i, n in enumerate(w["upper_000_after_each_source_law_deletion"]) if n]
    six_suffice = reduce(and_, [laws[i] for i in required], full)
    source_37 = {i for i, c in enumerate(w["source_counts_by_six_lower_readings"]) if c}
    abstract_37 = {i for i, word in enumerate(product((0, 1), repeat=6))
                   if all(any(word[j] == 0 for j in tri) for tri in CROSS)}
    assert source_37 == abstract_37
    assert {i for i, c in enumerate(counts(six_suffice, lower)) if c} == abstract_37
    assert three_words_missing(counts(six_suffice, upper)) == ("000",)
    assert len(required) == 6
    pairs = grouping_components(knots, required)
    assert sorted(map(len, pairs)) == [2, 2, 2]
    shared = {tuple(p): next(iter(set(knots[p[0]]) & set(knots[p[1]]))) for p in pairs}
    own_shared = []
    partner_shared = []
    for a, b in GROUPS:
        common, = set(carriers[a]) & set(carriers[b])
        other_places = {frozenset(set(carriers[j]) - {common}) for j in (a, b)}
        matched, = [s for p, s in shared.items()
                    if other_places == {frozenset(set(knots[i]) - {s}) for i in p}]
        own_shared.append(matched)
        partner_shared.append(common)
    assert len(set(own_shared)) == 3 and set(own_shared) == set(partner_shared)
    assert all(a != b for a, b in zip(own_shared, partner_shared))
    lower_needed = []
    lower_present = []
    for tri, sufficient in zip(CROSS, w["each_lower_bond_source_three_sufficient_to_exclude_111"]):
        forbidden = reduce(and_, (lower[i] for i in tri), full)
        three_laws = reduce(and_, [laws[i] for i in sufficient], full)
        assert not three_laws & forbidden
        needed = [i for i, pred in enumerate(with_one_omitted) if pred & forbidden]
        assert needed == sufficient
        assert sorted(map(len, grouping_components(knots, needed))) == [1, 1, 1]
        assert {x for i in tri for x in carriers[i]} == {x for i in needed for x in knots[i]}
        lower_needed.append(needed)
        lower_present.append([i for i, cell in enumerate(cells(ok, [lower[j] for j in tri])) if cell])
    assert lower_present == [list(range(7))] * 8
    return {"unique_minimal_source_set_for_upper_000": required,
            "its_components_under_sharing_raw_distinctions": pairs,
            "shared_distinction_of_own_source_pair_for_each_upper_comparison": own_shared,
            "shared_distinction_taken_from_another_pair_in_each_comparison": partner_shared,
            "number_of_lower_bonds_with_unique_disconnected_three_law_source_set_covering_their_carriers":
                len(lower_needed),
            "source_and_eight_lower_clauses_allow_identical_six_reading_words": True,
            "six_source_laws_and_whole_stage_allow_identical_six_reading_words": True}


def audit_before(record):
    w = record["witness"]
    label = record["cut_in_lexicographic_labels"]
    old = lambda a: sorted({label if x == 18 else x for x in a})
    knots = [old(c) for c in w["knots"]]
    carriers = [old(c) for c in w["lower_agreement_carriers"]]
    full, raw, laws, ok = allowed(18, knots)
    lower = [equality(c, raw, full) for c in carriers]
    upper = [equality(group, lower, full) for group in GROUPS]
    outer = [set().union(*(carriers[j] for j in g)) for g in GROUPS]
    pairs_disjoint = all(a.isdisjoint(b) for a, b in combinations(outer, 2))
    unique = len({tuple(c) for c in carriers}) == 6
    raw_pairs_free = all(min(counts(ok, [lower[j] for j in g])) > 0 for g in GROUPS)
    lower_eligible = []
    for tri in CROSS:
        a, b, c = [set(carriers[i]) for i in tri]
        lower_eligible.append(a.isdisjoint(b) and a.isdisjoint(c) and b.isdisjoint(c))
    strict_checks = [min((ok & ~raw[j] & (ok >> (1 << j)) &
                          (bit ^ (bit >> (1 << j)))).bit_count() for j in c) > 0
                     for c, bit in zip(carriers, lower)]
    tri_images = [three_words_missing(counts(ok, [lower[i] for i in tri])) for tri in CROSS]
    fix_source = [cells(ok, [raw[i] for i in k]) for k in knots]
    fix_lower = [cells(ok, [lower[i] for i in tri]) for tri in CROSS]
    unread_lower = min(mixed(part, value) for part in fix_source for value in lower)
    unread_upper = min(mixed(part, value) for part in fix_lower for value in upper)
    upper_image = counts(ok, upper)
    lost = reduce(and_, (full ^ value for value in upper), full)
    necessary = [i for i in range(len(knots)) if reduce(and_, laws[:i] + laws[i + 1:], lost)]
    checks = {
        "six_distinct_carriers_with_two_or_three_members": unique and all(2 <= len(c) <= 3 for c in carriers),
        "each_member_can_change_the_reading_by_flipping_alone": all(strict_checks),
        "each_lower_pair_admits_four_values": raw_pairs_free,
        "three_upper_carriers_pairwise_disjoint_in_raw_support": pairs_disjoint,
        "all_eight_lower_bonds_have_pairwise_disjoint_raw_carriers": all(lower_eligible),
        "all_eight_lower_triples_miss_exactly_111": tri_images == [("111",)] * 8,
        "upper_image_misses_exactly_000": three_words_missing(upper_image) == ("000",),
        "every_lower_reading_unread_at_any_source_knot": unread_lower > 0,
        "every_upper_reading_unread_at_any_lower_bond": unread_upper > 0,
    }
    return {"unchanged_named_reading_passes_after_reidentifying_the_cut": all(checks.values()),
            "checks": checks, "upper_word_counts": upper_image,
            "lower_words": sum(bool(cell) for cell in cells(ok, lower)),
            "unique_source_law_deletions_that_restore_000": necessary}


def canonical():
    sys.path.insert(0, str(HERE.parents[2] / "tools"))
    from knotlab.cli import main

    def roles(cnf, names, aux):
        results = []
        for contact in names:
            loops = [k for k in names if k != contact]
            stream = StringIO()
            with redirect_stdout(stream):
                code = main(["check", "--cnf", cnf, "--loops", *loops, "--contact", contact,
                             "--witnesses", *aux, "--json"])
            assert code == 0
            r = json.loads(stream.getvalue())
            results.append({"contact": contact, "allowed": r["allowed"], "is_knot": r["is_knot"]})
        return results

    six = ("A0", "A1", "B0", "B1", "C0", "C1")
    three = ("P", "Q", "R")
    four = []
    for g, u in zip(GROUPS, three):
        group = [six[i] for i in g] + [u]
        for a, b, c in product((0, 1), repeat=3):
            if (a == b) != c:
                four.append(" ".join(("~" if x else "") + y for x, y in zip((a, b, c), group)))
    eight = [" ".join("~" + six[i] for i in tri) for tri in CROSS]
    cnf = "; ".join(eight + four)
    tests = {"common_single_lower_clause": roles("~P ~Q ~R", three, []),
             "upper_from_the_eight_verified_lower_bonds": roles(cnf, three, six),
             "upper_clause_after_one_lower_bond_is_erased": roles("; ".join(eight[1:] + four), three, six)}
    assert all(r["is_knot"] and len(r["allowed"]) == 7 for key in list(tests)[:2] for r in tests[key])
    assert all(not r["is_knot"] and len(r["allowed"]) == 8
               for r in tests["upper_clause_after_one_lower_bond_is_erased"])
    return {"upper_cnf": cnf, "roles": tests}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=HERE / "other_registered.json")
    p.add_argument("--limit", type=int, default=49)
    p.add_argument("--out", type=Path)
    opts = p.parse_args()
    rows = []
    tally = Counter()
    for rec in json.loads(opts.input.read_text())[:opts.limit]:
        before = audit_before(rec)
        on_cut = audit_source(rec)
        needed_cut = len(set(rec["cut_knots"]) & set(on_cut["unique_minimal_source_set_for_upper_000"]))
        tally[f"needed_cut_knots_{needed_cut}"] += 1
        if before["unchanged_named_reading_passes_after_reidentifying_the_cut"]:
            tally["same_witness_before_and_after"] += 1
            tally[f"same_witness_before_and_after_needs_{needed_cut}_cut_knots"] += 1
        for check, yes in before["checks"].items():
            tally["before_" + check] += int(yes)
        rows.append({"registered_position": rec["registered_position"],
                     "on_cut": on_cut, "before_cut": before})
    output = {"registered_cuts": len(rows), "summary": tally, "canonical_checks": canonical(), "rows": rows}
    print(json.dumps({"registered_cuts": len(rows), "summary": tally}))
    if opts.out:
        opts.out.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
