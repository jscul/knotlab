"""Check scalar triple symmetries on targeted continuations of the hub switch."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
from pathlib import Path
import json
import sys

import networkx as nx


WIDTH18 = "proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/"
WIDTH20 = "proofs/VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/"
SOURCES = (
    (WIDTH18 + "check_width.py", "dc1bdeaea873653d027b07dcad78f0735716bce7604f2bb62a179da1bbd6d163"),
    (WIDTH18 + "check_classes.py", "8dd0ddaa58aa6e6f8ba1ec20fbe87b0b1c31cb090e93849fb271c8243dcb2472"),
    (WIDTH20 + "check_gluing.py", "6ce8aa70d9ec7ead98da8a4bfd0c891a935dc0cc2fb4effa3bad3e885f653335"),
)
CUBE_PARENTS = ((0,), (0,), (0,), (1, 2), (1, 3), (2, 3), (4, 5, 6))


def load(root, relative, digest):
    source = root / relative
    assert sha256(source.read_bytes()).hexdigest() == digest
    spec = spec_from_file_location("continuation_" + source.stem, source)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build(scout, rules, parents, counts, initial=None):
    fixture = initial if initial is not None else scout.Fixture((), (3,), ())
    for group, count in zip(parents, counts, strict=True):
        assert group in {option for option, _ in scout.legal_parent_sets(rules, fixture.checks())}
        fixture = fixture.successor(group, count)
    return fixture


def unique_shapes(scout, fixtures):
    buckets = defaultdict(list)
    for fixture in fixtures:
        graph = fixture.meeting_graph()
        invariant = tuple(sorted((graph.degree(i), n) for i, n in enumerate(fixture.loose_counts)))
        if not any(nx.is_isomorphic(graph, previous, node_match=scout.same_attributes)
                   for _, previous in buckets[invariant]):
            buckets[invariant].append((fixture, graph))
    return tuple(fixture for bucket in buckets.values() for fixture, _ in bucket)


def families(scout, rules):
    cubes = unique_shapes(scout, (build(scout, rules, CUBE_PARENTS, counts)
                                for counts in product((2, 3), repeat=7)))
    first, _ = scout.advance(rules, cubes, (2, 3))
    exact = tuple(build(scout, rules, CUBE_PARENTS, (2,) * 6 + (last,)) for last in (2, 3))
    exact_first, _ = scout.advance(rules, exact, (2, 3))
    exact_second, _ = scout.advance(rules, exact_first, (2, 3))
    triple_second = tuple(fixture.successor(parents, count)
                          for fixture in first
                          for parents, _ in scout.legal_parent_sets(rules, fixture.checks())
                          if len(parents) == 3 for count in (2, 3))
    second = unique_shapes(scout, (*exact_second, *triple_second))
    positive_tail = build(scout, rules, ((7,), (7,), (7,), (8, 9), (8, 10), (9, 10)),
                          (2,) * 6, initial=exact[-1])
    return {"closed_cube": cubes, "first_join_all_output_profiles": tuple(first),
            "second_join_from_exact_switch_or_three_parent": second,
            "exterior_triple_control": (positive_tail,)}


def bits(word):
    while word:
        first = word & -word
        yield first.bit_length() - 1
        word ^= first


def reached(rows, universe):
    seen = pending = universe & -universe
    while pending:
        first = pending & -pending
        new = rows[first.bit_length() - 1] & universe & ~seen
        seen |= new
        pending = (pending ^ first) | new
    return seen


def components(rows, mask):
    result = []
    while mask:
        found = reached(rows, mask)
        result.append(found)
        mask ^= found
    return tuple(result)


def cut_supports(gluing, checks):
    """Ordinary parity cuts, independently filtered for two connected sides."""
    holders, _ = gluing.incidence(checks)
    outside = len(checks)
    adjacency = [0] * (outside + 1)
    for ends in holders.values():
        a, b = (*ends, outside)[:2]
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    all_vertices = (1 << (outside + 1)) - 1
    span = [0]
    for check in checks:
        word = sum(1 << bit for bit in check)
        span += [word ^ prior for prior in span]
    assert len(set(span)) == 1 << outside
    return frozenset(word for side, word in enumerate(span) if side and reached(adjacency, side) == side
                     and reached(adjacency, all_vertices ^ side) == all_vertices ^ side)


def dense(table, width):
    matrix = [[0] * width for _ in range(width)]
    for (a, b), d in table.items():
        assert d is not None
        matrix[a][b] = matrix[b][a] = d
    return tuple(map(tuple, matrix))


def separator_components(matrix, checks):
    width = len(matrix)
    all_bits = (1 << width) - 1
    shared_star = [0] * width
    for check in checks:
        word = sum(1 << bit for bit in check)
        for bit in check:
            shared_star[bit] |= word ^ (1 << bit)
    calculated = {}
    mismatches = []
    for t in range(width):
        active = all_bits ^ (1 << t)
        links = [0] * width
        for x, y in combinations(bits(active), 2):
            if matrix[x][y] + 1 != matrix[x][t] + matrix[t][y]:
                links[x] |= 1 << y
                links[y] |= 1 << x
        scalar = components(links, active)
        physical = components(shared_star, active)
        if len(scalar) > 1:
            calculated[t] = scalar
        if scalar != physical:
            mismatches.append({"bit": t, "scalar_components": [list(bits(s)) for s in scalar],
                               "physical_components": [list(bits(s)) for s in physical]})
    return calculated, mismatches


def retain(width, separators, triple):
    active = (1 << width) - 1
    marks = sum(1 << bit for bit in triple)
    for t, pieces in separators.items():
        if marks & (1 << t):
            return 0
        piece = next((piece for piece in pieces if marks & piece == marks), 0)
        if not piece:
            return 0
        active &= piece | (1 << t)
    return active


@dataclass
class Record:
    family: str
    fixture: object
    matrix: tuple
    legal: frozenset
    separators: dict
    pieces: dict = field(default_factory=dict)

    def description(self, marked=None):
        return {"family": self.family, "history": self.fixture.history, "checks": self.fixture.checks(),
                "marked": sorted(marked) if marked is not None else None, "width": len(self.matrix)}

    def restricted(self, api, remaining):
        if remaining not in self.pieces:
            names = tuple(bits(remaining))
            cropped = tuple(tuple(self.matrix[a][b] for b in names) for a in names)
            self.pieces[remaining] = names, cropped, api.Quotient.make(cropped)
        return self.pieces[remaining]


def exact_switch_control(root, gluing, scout, rules):
    data = json.loads((root / WIDTH18 / "classes.json").read_text())["full_table_self_conflicts"][0]
    left = tuple(map(tuple, data["stars"]))
    mapping = tuple(data["same_states_different_menu"]["bit_permutation"])
    right = tuple(tuple(mapping[i] for i in scope) for scope in left)
    gluing.replay(left)
    gluing.replay(right)
    assert gluing.minimal_dual(left) == gluing.minimal_dual(right)
    shared_loose = set.intersection(*({i for i, owners in gluing.incidence(side)[0].items() if len(owners) == 1}
                                     for side in (left, right)))
    assert shared_loose == {15, 16, 17}
    checks = list(left)
    for bit, outputs in zip(sorted(shared_loose), ((18, 19), (20, 21), (22, 23)), strict=True):
        checks.append((bit, *outputs))
    common = (*right, *checks[len(left):])
    gluing.replay(tuple(checks))
    gluing.replay(common)
    assert gluing.minimal_dual(tuple(checks)) == gluing.minimal_dual(common)
    for side in (checks, common):
        assert not any(len(action) == 3 for action in scout.actual_menu(rules, dict(enumerate(side))))
    return {"initial_width": 18, "common_bits": sorted(shared_loose), "common_unary_joins": 3,
            "same_full_state_relation_before_and_after": True, "legal_triples_after": [0, 0]}


def mismatch(api, first, second, mapping):
    wrong = first.legal - api.transported(second.legal, api.inverse(mapping))
    if not wrong:
        first, second, mapping = second, first, api.inverse(mapping)
        wrong = first.legal - api.transported(second.legal, api.inverse(mapping))
    mark = min(wrong, key=lambda action: tuple(sorted(action)))
    return {"left": first.description(mark), "right": second.description({mapping[bit] for bit in mark}),
            "full_permutation": mapping,
            "full_pairs_compared": len(first.matrix) * (len(first.matrix) - 1) // 2}


def review_full(api, gluing, scout, rules, population):
    records = []
    buckets = defaultdict(list)
    by_family = {}
    first_conflict = first_separator_mismatch = None
    measures = Counter()
    for label, fixtures in population.items():
        counts = by_family[label] = Counter()
        for fixture in fixtures:
            checks = tuple(fixture.checks().values())
            width = len(fixture.meetings) + sum(fixture.loose_counts)
            support = cut_supports(gluing, checks)
            if not counts["fixtures"]:
                assert support == gluing.minimal_dual(checks)
            matrix = dense(gluing.scalar_table(support, width), width)
            menu = scout.actual_menu(rules, fixture.checks())
            legal = frozenset(action for action in menu if len(action) == 3)
            separators, bad_cuts = separator_components(matrix, checks)
            rec = Record(label, fixture, matrix, legal, separators)
            records.append(rec)
            counts["fixtures"] += 1
            counts["with_legal_triples"] += bool(legal)
            counts["legal_triples"] += len(legal)
            counts["tested_distinction_deletions"] += width
            counts["scalar_separator_discrepancies"] += len(bad_cuts)
            if bad_cuts and first_separator_mismatch is None:
                first_separator_mismatch = {"fixture": rec.description(), **bad_cuts[0]}
                print("CONTINUATION_SEPARATOR_MISMATCH " + json.dumps(first_separator_mismatch),
                      file=sys.stderr, flush=True)

            quotient = api.Quotient.make(matrix)
            loose = {next(iter(action)) for action in menu if len(action) == 1}
            mixed = [set(block) for block in quotient.blocks if set(block) & loose and set(block) - loose]
            counts["fixtures_with_loose_shared_distance_twins"] += bool(mixed)
            counts["fixtures_with_a_legal_triple_and_loose_shared_twins"] += bool(mixed and legal)
            active_bits = set().union(*legal)
            counts["legal_inputs_with_a_shared_distance_twin"] += len(active_bits & set().union(*mixed))
            group_order, _, generators = quotient.automorphisms()
            counts["full_automorphisms"] += group_order
            counts["generators_graded"] += len(generators)
            counts.setdefault("triple_changing_generators", 0)
            for mapping in generators:
                assert api.disagreement(matrix, matrix, mapping) is None
                if api.transported(legal, mapping) != legal:
                    counts["triple_changing_generators"] += 1
                    if first_conflict is None:
                        first_conflict = mismatch(api, rec, rec, mapping)
                        print("FULL_TRIPLE_CONFLICT " + json.dumps(first_conflict), file=sys.stderr, flush=True)

            bucket = buckets[quotient.colored.invariant]
            seen_table = False
            for prior, earlier in bucket:
                measures["cross_fixture_quotient_checks"] += 1
                iso = next(api.isometries(quotient.colored, earlier.colored), None)
                if iso is not None:
                    seen_table = True
                    mapping = quotient.lift(earlier, iso)
                    assert api.disagreement(matrix, prior.matrix, mapping) is None
                    measures["cross_fixture_full_coincidences"] += 1
                    if api.transported(legal, mapping) != prior.legal and first_conflict is None:
                        first_conflict = mismatch(api, rec, prior, mapping)
                        print("FULL_TRIPLE_CONFLICT " + json.dumps(first_conflict), file=sys.stderr, flush=True)
                    # Keep each distinct menu to check all new members. Any
                    # other isometry differs by one of the tested self-maps.
            measures["full_table_classes"] += not seen_table
            bucket.append((rec, quotient))
    measures.setdefault("cross_fixture_quotient_checks", 0)
    measures.setdefault("cross_fixture_full_coincidences", 0)
    return records, by_family, measures, first_conflict, first_separator_mismatch


def internal(matrix, marks):
    a, b, c = marks
    return matrix[a][b], matrix[a][c], matrix[b][c]


def rows_key(matrix, marks, distances):
    return min(tuple(sorted((matrix[a][j], matrix[b][j], matrix[c][j])
                            for j in range(len(matrix)) if j not in marks))
               for a, b, c in permutations(marks) if internal(matrix, (a, b, c)) == distances)


def marked_partition(api, matrix, quotient, marks):
    colors = tuple((len(block), matrix[block[0]][block[1]] if len(block) > 1 else 0,
                    sum(bit in marks for bit in block)) for block in quotient.blocks)
    return api.ColoredMatrix.make(quotient.colored.matrix, colors)


def marked_lift(source, target, smarks, tmarks, quotient_map):
    result = [-1] * sum(map(len, source.blocks))
    for x, y in enumerate(quotient_map):
        old = sorted(source.blocks[x], key=lambda bit: (bit not in smarks, bit))
        new = sorted(target.blocks[y], key=lambda bit: (bit not in tmarks, bit))
        for a, b in zip(old, new, strict=True):
            result[a] = b
    return result


def rows_control(gluing, older, old_names, old_marks, old_matrix, rec, names, marks, matrix, distances, feature):
    def ordered_columns(table, chosen):
        for order in permutations(chosen):
            if internal(table, order) != distances:
                continue
            outside = sorted((tuple(table[bit][j] for bit in order), j)
                             for j in range(len(table)) if j not in chosen)
            if tuple(column for column, _ in outside) == feature:
                return (*order, *(j for _, j in outside))
        raise AssertionError("Missing matched three-row order")

    old_order, new_order = ordered_columns(old_matrix, old_marks), ordered_columns(matrix, marks)
    differences = [{"left_pair": sorted((old_names[old_order[i]], old_names[old_order[j]])),
                    "right_pair": sorted((names[new_order[i]], names[new_order[j]])),
                    "distances": [old_matrix[old_order[i]][old_order[j]], matrix[new_order[i]][new_order[j]]]}
                   for i, j in combinations(range(len(old_order)), 2)
                   if old_matrix[old_order[i]][old_order[j]] != matrix[new_order[i]][new_order[j]]]
    assert differences
    descriptions = []
    for case, current_names, marked, retained in ((older, old_names, old_marks, old_matrix),
                                                    (rec, names, marks, matrix)):
        checks = tuple(case.fixture.checks().values())
        steps = gluing.replay(checks)
        assert tuple((tuple(s["parents"]), len(s["fresh"])) for s in steps[1:]) == case.fixture.history
        assert dense(gluing.scalar_table(gluing.minimal_dual(checks), len(case.matrix)), len(case.matrix)) == case.matrix
        triple = frozenset(current_names[i] for i in marked)
        holders, adjacency = gluing.incidence(checks)
        allowed = (all(len(holders[bit]) == 1 for bit in triple)
                   and gluing.legal_parents([holders[bit][0] for bit in triple], adjacency))
        assert allowed == (triple in case.legal)
        descriptions.append({**case.description(triple), "legal": allowed, "retained_bits": current_names,
                             "full_entries_at_distance_four": sum(case.matrix[a][b] == 4
                                                                   for a, b in combinations(range(len(case.matrix)), 2)),
                             "retained_entries_at_distance_four": sum(retained[a][b] == 4
                                                                       for a, b in combinations(range(len(retained)), 2))})
    assert descriptions[0]["legal"] and not descriptions[1]["legal"]
    return {"left": descriptions[0], "right": descriptions[1], "same_arrangement": older is rec,
            "retained_row_preserving_map": [(old_names[i], names[j]) for i, j in zip(old_order, new_order, strict=True)],
            "differing_retained_pairs_under_that_map": len(differences),
            "retained_differences": sorted(differences, key=lambda pair: pair["left_pair"])}


def review_retained(api, gluing, records):
    keys = defaultdict(dict)
    stats = Counter()
    first = decoy = None
    for rec in records:
        for triple in sorted(rec.legal, key=lambda action: tuple(sorted(action))):
            remaining = retain(len(rec.matrix), rec.separators, triple)
            if not remaining:
                stats["legal_triples_rejected_at_a_reported_cut"] += 1
                continue
            names, matrix, quotient = rec.restricted(api, remaining)
            marks = tuple(sorted(names.index(bit) for bit in triple))
            distances = tuple(sorted(internal(matrix, marks)))
            signature = rows_key(matrix, marks, distances)
            color = marked_partition(api, matrix, quotient, marks)
            keys[len(names), distances].setdefault(signature, []).append((rec, names, marks, matrix, quotient, color))
            stats["legal_triples_bank"] += 1
    internal_shapes = {distances for _, distances in keys}
    for rec in records:
        for triple in combinations(range(len(rec.matrix)), 3):
            stats["candidate_triples"] += 1
            distances = tuple(sorted(internal(rec.matrix, triple)))
            if distances not in internal_shapes or frozenset(triple) in rec.legal:
                continue
            remaining = retain(len(rec.matrix), rec.separators, triple)
            bucket = keys.get((remaining.bit_count(), distances))
            if not bucket:
                continue
            names, matrix, quotient = rec.restricted(api, remaining)
            marks = tuple(sorted(names.index(bit) for bit in triple))
            signature = rows_key(matrix, marks, distances)
            matching = bucket.get(signature, ())
            if not matching:
                continue
            color = marked_partition(api, matrix, quotient, marks)
            stats["forbidden_choices_matching_legal_retained_rows"] += 1
            for older, old_names, old_marks, old_matrix, old_quotient, old_color in matching:
                iso = next(api.isometries(old_color, color), None)
                if iso is None:
                    continue
                mapping = marked_lift(old_quotient, quotient, old_marks, marks, iso)
                assert {mapping[bit] for bit in old_marks} == set(marks)
                assert api.disagreement(old_matrix, matrix, mapping) is None
                stats["forbidden_choices_matching_a_legal_retained_table"] += 1
                if first is None:
                    first = {"legal": older.description(old_names[bit] for bit in old_marks),
                             "forbidden": rec.description(triple), "retained_width": len(names),
                             "retained_distinction_map": [(name, names[mapping[i]]) for i, name in enumerate(old_names)]}
                    print("RETAINED_TRIPLE_CONFLICT " + json.dumps(first), file=sys.stderr, flush=True)
                break
            else:
                if decoy is None:
                    older, old_names, old_marks, old_matrix, _, _ = matching[0]
                    decoy = rows_control(gluing, older, old_names, old_marks, old_matrix, rec, names, marks,
                                         matrix, distances, signature)
    stats.setdefault("forbidden_choices_matching_a_legal_retained_table", 0)
    stats.setdefault("legal_triples_rejected_at_a_reported_cut", 0)
    return stats, first, decoy


def legal_input(gluing, checks, operands):
    holders, adjacency = gluing.incidence(checks)
    return (all(len(holders[bit]) == 1 for bit in operands)
            and gluing.legal_parents([holders[bit][0] for bit in operands], adjacency))


def independent_marked_check(matrix, left, right):
    """Compare literal weighted graphs, without the twin-quotient matcher."""
    def graph(marks):
        result = nx.Graph()
        for i, row in enumerate(matrix):
            profile = tuple(sorted(Counter((j in marks, value) for j, value in enumerate(row) if j != i).items()))
            result.add_node(i, color=(i in marks, profile))
        result.add_weighted_edges_from((i, j, matrix[i][j]) for i, j in combinations(range(len(matrix)), 2))
        return result

    return nx.is_isomorphic(graph(left), graph(right), node_match=lambda a, b: a == b,
                            edge_match=lambda a, b: a == b)


def follow_rows_control(api, gluing, decoy):
    assert decoy["same_arrangement"]
    checks = tuple(decoy["left"]["checks"].values())
    left, right = (tuple(decoy[side]["marked"]) for side in ("left", "right"))
    width = decoy["left"]["width"]
    mapping = dict(decoy["retained_row_preserving_map"])
    affected = {bit for witness in decoy["retained_differences"]
                for named in ("left_pair", "right_pair") for bit in witness[named]}
    original = dense(gluing.scalar_table(gluing.minimal_dual(checks), width), width)
    assert not independent_marked_check(original, left, right)
    def shell_count(marked):
        a, b = min(combinations(marked, 2), key=lambda pair: original[pair[0]][pair[1]])
        c, = set(marked) - {a, b}
        pairs = [pair for pair in combinations((i for i in range(width) if i not in marked), 2)
                 if original[pair[0]][pair[1]] == 5 and sorted(original[c][i] for i in pair) == [6, 7]]
        return {"mark_opposite_shortest_pair": c, "pairs": pairs}

    shell = [shell_count(left), shell_count(right)]
    assert [len(side["pairs"]) for side in shell] == [5, 0]
    assert all(min(original[i][j], 5) == min(original[mapping[i]][mapping[j]], 5)
               for i, j in combinations(range(width), 2))

    layer = [(checks, ())]
    per_depth = []
    offshoots = []
    banks = (defaultdict(list), defaultdict(list))
    for depth in (1, 2):
        seen = Counter(cross_history_exact_candidates=0, histories_with_both_marks_still_loose=0)
        future = []
        for before, history in layer:
            holders, adjacency = gluing.incidence(before)
            loose = [bit for bit, sites in sorted(holders.items()) if len(sites) == 1]
            implicated = affected | (set(history[-1][1]) if history else set())
            for size in (1, 2, 3):
                for operands in combinations(loose, size):
                    if not set(operands) & implicated or not gluing.legal_parents(
                            [holders[bit][0] for bit in operands], adjacency):
                        continue
                    for count in (2, 3):
                        fresh = tuple(range(len(holders), len(holders) + count))
                        next_checks = (*before, (*operands, *fresh))
                        if not legal_input(gluing, next_checks, left) or legal_input(gluing, next_checks, right):
                            seen["moves_discarded_after_marked_verdicts"] += 1
                            continue
                        path = (*history, (operands, fresh))
                        future.append((next_checks, path))
                        seen["opposed_histories"] += 1
                        gluing.replay(next_checks)
                        next_holders = gluing.incidence(next_checks)[0]
                        seen["histories_with_both_marks_still_loose"] += all(
                            len(next_holders[bit]) == 1 for bit in (*left, *right)
                        )
                        n = len(holders) + count
                        matrix = dense(gluing.scalar_table(cut_supports(gluing, next_checks), n), n)
                        quotient = api.Quotient.make(matrix)
                        colored = [marked_partition(api, matrix, quotient, mark) for mark in (left, right)]
                        if next(api.isometries(*colored), None) is not None:
                            raise AssertionError(("full marked conflict", path))
                        for polarity, (marked, table) in enumerate(zip((left, right), colored, strict=True)):
                            for other, other_path in banks[1 - polarity][table.invariant]:
                                seen["cross_history_exact_candidates"] += 1
                                if next(api.isometries(table, other), None) is not None:
                                    raise AssertionError(("full cross-history marked conflict", path, other_path, marked))
                            banks[polarity][table.invariant].append((table, path))
                        bad = sum(matrix[i][j] != matrix[mapping[i]][mapping[j]]
                                  for i, j in combinations(range(width), 2))
                        if seen["opposed_histories"] == 1 or bad < seen["least_old_disagreements_under_original_map"]:
                            seen["least_old_disagreements_under_original_map"] = bad
                        seen["most_old_disagreements_under_original_map"] = max(
                            seen["most_old_disagreements_under_original_map"], bad
                        )
                        if depth == 1 and len(operands) == 1 and mapping[operands[0]] == operands[0] and len(offshoots) < 2:
                            assert all(matrix[i][j] == original[i][j] for i, j in combinations(range(width), 2))
                            extension = (*tuple(mapping[i] for i in range(width)), *fresh)
                            assert all(matrix[i][j] == matrix[extension[i]][extension[j]]
                                       for i, j in combinations(range(n), 2) if i in left or j in left)
                            separators, mismatches = separator_components(matrix, next_checks)
                            assert not mismatches and all(retain(n, separators, mark) == (1 << width) - 1
                                                          for mark in (left, right))
                            offshoots.append({"history": path, "width": n, "retained_width": width})
        per_depth.append(dict(seen))
        layer = future
    return {"distance_five_links_between_shells_six_and_seven": shell,
            "entire_marked_table_matches_when_capped_through_four": True,
            "old_distinctions_in_the_changed_pairs": sorted(affected),
            "independent_complete_marked_isometry_exists": False,
            "continuations_at_depth_one_then_two": per_depth, "fixed_tip_offshoot_controls": offshoots,
            "full_marked_conflicts_in_scoped_continuations": 0}


def main():
    root = Path(__file__).resolve().parents[3]
    population_source, api, gluing = (load(root, path, digest) for path, digest in SOURCES)
    scout, _, rules = population_source.inherited()
    control = exact_switch_control(root, gluing, scout, rules)
    records, by_family, tests, full, separator = review_full(api, gluing, scout, rules, families(scout, rules))
    retained_counts, retained, decoy = review_retained(api, gluing, records)
    followup = follow_rows_control(api, gluing, decoy) if decoy is not None else None
    print(json.dumps({"sources": dict(SOURCES), "by_targeted_family": by_family,
                      "common_continuation_control": control, "exact_cross_fixture_checks": tests,
                      "first_full_conflict": full, "first_scalar_separator_discrepancy": separator,
                      "retained_marked_checks": retained_counts, "first_retained_conflict": retained,
                      "matched_retained_rows_control": decoy,
                      "same_arrangement_followup": followup,
                      "full_targeted_fixtures": len(records)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
