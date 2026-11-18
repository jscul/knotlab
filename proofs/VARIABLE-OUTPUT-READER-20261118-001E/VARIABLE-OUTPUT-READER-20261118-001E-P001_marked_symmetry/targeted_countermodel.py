"""Targeted tests of a three-parent cap on a genuinely live prefix."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[3]
D_ROOT = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse"
sys.path.insert(0, str(D_ROOT))
import check_ambiguity_continuation as ambiguity
import check_continuation as continuation


SEED = ((0, 1, 2),)
SEVEN = ((0,), (0,), (0,), (1, 2), (1, 3), (2, 3))
VARY = (2, 3)
MOTIFS = (
    ("repeated_two_parent_branch", (*SEVEN, (2, 3)), (VARY, (3,), (3,), *(VARY,) * 4),
     ((4, 5, 6), (4, 5, 7))),
    ("branch_through_a_new_shared_witness", (*SEVEN, (4, 5), (2, 7)),
     (VARY, (3,), VARY, VARY, (3,), VARY, VARY, VARY), ((4, 5, 6), (5, 6, 8))),
)


def adjoin(gluing, checks, parents, how_many):
    holders, adjacent = gluing.incidence(checks)
    assert gluing.legal_parents(parents, adjacent)
    consumed = tuple(min(bit for bit in checks[site] if holders[bit] == [site]) for site in parents)
    return (*checks, (*consumed, *range(len(holders), len(holders) + how_many))), consumed


def dual_words(checks):
    span = [0]
    for support in checks:
        word = sum(1 << bit for bit in support)
        span.extend([prior ^ word for prior in span])
    assert len(set(span)) == len(span)
    return span


def row_differences(matrix, loose, shared):
    return [(x, matrix[loose][x], matrix[shared][x]) for x in range(len(matrix)) if x not in (loose, shared)
            and matrix[loose][x] != matrix[shared][x]]


def named_triples(menu):
    return sorted(tuple(sorted(mark)) for mark in menu)


def d_control(api, gluing):
    raw = (D_ROOT / "active_part.json").read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == "48a711f1fa5b6eca0aa05d47eba9011bb129af985f29f8fd3ea959981ee09ed3"
    record = json.loads(raw)["completions"][0]
    checks = tuple(map(tuple, record["junction_supports"]))
    assert gluing.replay(checks) == record["history"]
    matrix = ambiguity.measure(gluing, checks)
    move = tuple(14 if x == 13 else 13 if x == 14 else x for x in range(32))
    legal = ambiguity.triples(gluing, checks)
    assert api.disagreement(matrix, matrix, move) is None and api.transported(legal, move) == legal
    assert not ambiguity.in_span(sum(1 << move[bit] for bit in record["true_parity_equation"]), checks)
    assert named_triples(legal) == list(map(tuple, record["true_triples"]))
    order, _, generators = api.Quotient.make(matrix).automorphisms()
    assert all(api.transported(legal, generator) == legal for generator in generators)

    size = {}
    for word in sorted(continuation.cut_supports(gluing, checks), key=lambda item: (item.bit_count(), item)):
        for triple in combinations(continuation.bits(word), 3):
            size.setdefault(triple, word.bit_count())
    shifted = [(triple, size.get(triple), size.get(tuple(sorted(move[i] for i in triple))))
               for triple in combinations(range(32), 3)
               if size.get(triple) != size.get(tuple(sorted(move[i] for i in triple)))]
    return {"source_sha256": digest, "pair_entries_invariant": 496, "legal_triples_fixed": named_triples(legal),
            "scalar_group_order": order, "modified_ternary_minimum_on_all_input_triples": len(shifted),
            "first_changed_ternary_minimum": shifted[0] if shifted else None}


def amplification_archive(scout, gluing):
    rank = json.loads((D_ROOT / "span_controls.json").read_text())
    roster = {case["case_id"]: case["source_history"]
              for case in rank["full_table_rank_one_extension_controls"]["individual_cases"]}
    prior = json.loads((D_ROOT / "live_twins.json").read_text())["per_source_transposition"]
    pairs = [(row["source"], row["tracked_loose"], row["tracked_shared"]) for row in prior]
    pairs.append(("width_20_type_12350", 14, 13))
    holds = Counter()
    for case, loose, shared in pairs:
        fixture = scout.Fixture((), (3,), ())
        for parents, count in roster[case]:
            fixture = fixture.successor(tuple(parents), count)
        holders, _ = gluing.incidence(tuple(fixture.checks().values()))
        assert len(holders[loose]) == 1 and len(holders[shared]) == 2
        u, = holders[loose]
        assert u in holders[shared]
        holds["shared_bit_born_at_loose_holder"] += holders[shared][0] == u
        holds["shared_input_at_holder_with_three_loose_bits"] += (holders[shared][1] == u and
                                                                   sum(v == [u] for v in holders.values()) == 3)
    return {"archived_scalar_transpositions_checked": len(pairs), **dict(holds)}


def witness(api, gluing, states, conflict):
    left, right = (states[conflict[side]] for side in ("left", "right"))
    perm = conflict["permutation"]
    menus = [ambiguity.triples(gluing, checks) for checks in (left, right)]
    illegal = menus[0] - api.transported(menus[1], api.inverse(perm))
    if not illegal:
        left, right = right, left
        menus.reverse()
        perm = api.inverse(perm)
        illegal = menus[0] - api.transported(menus[1], api.inverse(perm))
    mark = min((tuple(sorted(triple)) for triple in illegal))
    sides = []
    for checks in (left, right):
        steps = gluing.replay(checks)
        width = len(gluing.incidence(checks)[0])
        original = gluing.scalar_table(gluing.minimal_dual(checks), width)
        matrix = continuation.dense(original, width)
        assert matrix == ambiguity.measure(gluing, checks)
        sides.append((steps, matrix))
    assert api.disagreement(sides[0][1], sides[1][1], perm) is None
    return {"left_supports": left, "right_supports": right,
            "left_history": sides[0][0], "right_history": sides[1][0], "permutation": perm,
            "legal_marks": mark, "forbidden_marks": sorted(perm[i] for i in mark),
            "pair_entries_compared": len(perm) * (len(perm) - 1) // 2,
            "full_upper_triangle_left": [sides[0][1][i][j] for i, j in combinations(range(len(perm)), 2)],
            "mapped_full_upper_triangle_right": [sides[1][1][perm[i]][perm[j]]
                                                  for i, j in combinations(range(len(perm)), 2)]}


def cap_trials(api, gluing):
    measurements = []
    states = {}
    best = {}
    reports = {}
    for name, parents, output_patterns, caps in MOTIFS:
        counts = Counter()
        old_costs = Counter()
        widths = Counter()
        for fresh_pattern in product(*output_patterns):
            prefix = SEED
            for parents_here, count in zip(parents, fresh_pattern, strict=True):
                prefix, _ = adjoin(gluing, prefix, parents_here, count)
            old_triples = ambiguity.triples(gluing, prefix)
            span = dual_words(prefix)
            by_fresh = {}
            for cap, count in product(caps, (2, 3)):
                grown, inputs = adjoin(gluing, prefix, cap, count)
                gluing.replay(grown)
                table = ambiguity.measure(gluing, grown)
                holders, _ = gluing.incidence(grown)
                current = ambiguity.triples(gluing, grown)
                still_legal = current & old_triples
                assert still_legal
                union = set().union(*still_legal)
                all_legal = set().union(*current)
                old_input_mask = sum(1 << bit for bit in inputs)
                cap_fresh = set(grown[-1]) - set(inputs)
                observed = []
                for loose, shared in product(sorted(union), inputs):
                    if holders[loose][0] not in holders[shared]:
                        continue
                    counts["live_sibling_swaps"] += 1
                    cost = min((word ^ old_input_mask).bit_count() for word in span if word & (1 << loose))
                    assert cost >= 5
                    old_costs[cost] += 1
                    changed = row_differences(table, loose, shared)
                    assert all(table[shared][z] <= count + 2 < table[loose][z] for z in cap_fresh)
                    assert all(table[loose][z] + 1 >= count + cost for z in cap_fresh)
                    observed.append((len(changed), loose, shared, changed))
                assert observed
                closest = min(observed)
                if name not in best or closest[0] < best[name][0]:
                    best[name] = closest[0], grown, closest[1], closest[2], closest[3], current
                quotient = api.Quotient.make(table)
                loose_bits = {bit for bit, sites in holders.items() if len(sites) == 1}
                counts["exact_live_loose_shared_twins"] += sum(len(all_legal & set(block)) * len(set(block) - loose_bits)
                                                              for block in quotient.blocks)
                for u, star in enumerate(grown):
                    own = sorted(bit for bit in star if holders[bit] == [u])
                    if len(own) != 3:
                        continue
                    for bit in star:
                        if len(holders[bit]) == 2 and holders[bit][1] == u:
                            counts["three_loose_holder_input_swaps"] += 1
                            if not row_differences(table, own[0], bit):
                                counts["three_loose_holder_scalar_twins"] += 1
                                print("AMPLIFICATION_INPUT " + json.dumps([grown, own[0], bit]), file=sys.stderr, flush=True)

                widths[len(table)] += 1
                counts["with_live_triples"] += 1
                counts["legal_triples"] += len(current)
                key = (name, fresh_pattern, cap, count)
                measurements.append((key, table, current))
                states[key] = grown
                if count not in by_fresh:
                    by_fresh[count] = table, current
                else:
                    previous, previous_marks = by_fresh[count]
                    counts["alternate_caps_on_the_same_prefix"] += 1
                    counts["alternate_caps_with_identical_named_matrices"] += previous == table
                    counts["alternate_caps_changing_some_actual_triple"] += previous_marks != current
        counts.setdefault("three_loose_holder_scalar_twins", 0)
        reports[name] = {**dict(counts), "width_counts": dict(widths),
                         "least_prefix_word_size_after_symmetric_difference_with_cap_inputs": dict(old_costs)}
    classification = ambiguity.compare_complete(api, measurements)
    evidence = witness(api, gluing, states, classification["first_conflict"]) if classification["first_conflict"] else None
    if evidence is not None:
        print("FULL_TARGETED_CONFLICT " + json.dumps(evidence), file=sys.stderr, flush=True)
    return reports, classification, evidence, best


def repairs(api, gluing, best):
    reports = {}
    measurements = []
    states = {}
    for name, (_, checks, loose, shared, differences, marks) in best.items():
        cap = len(checks) - 1
        holders, _ = gluing.incidence(checks)
        implicated_sites = {site for bit in checks[cap] for site in holders[bit]}
        implicated = {bit for bit, sites in holders.items() if len(sites) == 1 and sites[0] in implicated_sites}
        layers = [(checks, ())]
        details = []
        for depth in (1, 2):
            following = []
            smallest = None
            repaired = 0
            for before, history in layers:
                width = len(gluing.incidence(before)[0])
                touched = implicated | (set(history[-1][1]) if history else set())
                for act, count in product(ambiguity.operands(gluing, before), (2, 3)):
                    if loose in act or not touched.intersection(act):
                        continue
                    fresh = tuple(range(width, width + count))
                    grown = (*before, (*act, *fresh))
                    available = ambiguity.triples(gluing, grown)
                    if not any(loose in triple for triple in available):
                        continue
                    history_here = (*history, (act, fresh))
                    following.append((grown, history_here))
                    matrix = ambiguity.measure(gluing, grown)
                    key = (name, history_here)
                    states[key] = grown
                    measurements.append((key, matrix, available))
                    changed = row_differences(matrix, loose, shared)
                    if smallest is None or len(changed) < smallest:
                        smallest = len(changed)
                    if not changed:
                        record = witness(api, gluing, {0: grown}, {"left": 0, "right": 0, "permutation": tuple(
                            shared if i == loose else loose if i == shared else i for i in range(width + count)
                        )})
                        print("LIVE_REPAIRED_CONFLICT " + json.dumps(record), file=sys.stderr, flush=True)
                        repaired += 1
            details.append({"moves": depth, "histories_retaining_a_live_input": len(following),
                            "smallest_number_of_differing_row_entries": smallest, "full_live_swaps": repaired})
            layers = following
        reports[name] = {"checks": checks, "history": gluing.replay(checks),
                         "live_loose": loose, "shared_cap_input": shared,
                         "row_differences_loose_then_shared": differences,
                         "live_triples": [triple for triple in named_triples(marks) if loose in triple],
                         "extra_joins_only_at_the_cap_its_parents_or_new_outputs": details}
    classification = ambiguity.compare_complete(api, measurements)
    evidence = witness(api, gluing, states, classification["first_conflict"]) if classification["first_conflict"] else None
    if evidence is not None:
        print("FULL_REPAIR_CONFLICT " + json.dumps(evidence), file=sys.stderr, flush=True)
    return reports, classification, evidence


def main():
    source, api, gluing = (continuation.load(ROOT, path, digest) for path, digest in continuation.SOURCES)
    scout, _, _ = source.inherited()
    control = d_control(api, gluing)
    archive = amplification_archive(scout, gluing)
    reports, classification, evidence, best = cap_trials(api, gluing)
    repairs_report, repair_classification, repair_evidence = repairs(api, gluing, best)
    print(json.dumps({"width_32_predecessor_control": control, "archived_amplification_inputs": archive,
                      "specified_cap_motifs": reports, "full_exact_isometries_on_cap_trials": classification,
                      "full_cap_counterexample": evidence, "targeted_repairs_of_two_closest_caps": repairs_report,
                      "full_exact_isometries_on_targeted_repairs": repair_classification,
                      "full_repair_counterexample": repair_evidence},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
