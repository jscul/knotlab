"""Compare three finite families of mixed-fresh serial parity arrangements.

The observations are complete tables of minimum bond sizes K, or the same
tables with values above a cutoff coalesced. The marker is only membership
in an unordered triple. Holder identities and chronological names are used
to generate legal histories and grade moves.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

import networkx as nx


HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1]
G = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh"
D = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse"
FROZEN = {
    G / "six_check.json": "21b673034abf89e7db4f800c2bc850a6ba313d2af77d37644cb8460b096c7fbc",
    D / "active_part.json": "48a711f1fa5b6eca0aa05d47eba9011bb129af985f29f8fd3ea959981ee09ed3",
    D / "check_span_controls.py": "ece53f8c0aa3f71c6be5984de374992d11c15bd3f4a20e9ff979d4c57e7cd6a2",
}
MARK = (9, 11, 13)
FIRST_CUTOFF = 5
INFINITY = 255


def verified(path):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == FROZEN[path], path
    return data


@cache
def dependencies():
    path = D / "check_span_controls.py"
    verified(path)
    spec = importlib.util.spec_from_file_location("high_cross_span", path)
    span = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = span
    spec.loader.exec_module(span)
    scout, rules = span.scout_and_rules()
    return span, scout, rules, span.controls(), span.load("check_classes.py")


@dataclass(frozen=True)
class Presentation:
    prefix: str
    supports: tuple[tuple[int, ...], ...]
    width: int
    additions: tuple[tuple[tuple[int, ...], int], ...] = ()

    @property
    def checks(self):
        return dict(enumerate(self.supports))

    @property
    def high(self):
        return tuple(i for i, scope in enumerate(self.supports) if len(scope) >= 5)

    @property
    def masks(self):
        return tuple(sum(1 << bit for bit in scope) for scope in self.supports)

    def child(self, consumed, count):
        fresh = tuple(range(self.width, self.width + count))
        return Presentation(self.prefix, (*self.supports, (*consumed, *fresh)),
                            self.width + count, (*self.additions, (consumed, count)))

    def describe(self):
        history = replay(self)
        return {"prefix": self.prefix, "width": self.width, "junctions": len(history),
                "new_moves": self.additions, "history": history}


@dataclass(frozen=True)
class Measured:
    case: Presentation
    rows: tuple[bytes, ...]


def replay(case):
    _, scout, rules, _, _ = dependencies()
    present = {}
    names = set()
    events = []
    for site, scope in enumerate(case.supports):
        assert len(scope) == len(set(scope))
        consumed = tuple(bit for bit in scope if bit in names)
        fresh = tuple(bit for bit in scope if bit not in names)
        if present:
            assert len(fresh) in (2, 3)
            assert rules.legal_local_move(present, consumed, scout.FRESH_FOR_PARENT_TEST)
        else:
            assert len(fresh) == 3
        users, _ = rules.incidence(present)
        parents = tuple(users[bit][0] for bit in consumed)
        events.append({"site": site, "consumed": consumed, "fresh": fresh, "parents": parents})
        present[site] = scope
        names.update(fresh)
    assert names == set(range(case.width))
    return events


def triple_allowed(case, triple):
    _, scout, rules, _, _ = dependencies()
    return rules.legal_local_move(case.checks, triple, scout.FRESH_FOR_PARENT_TEST)


def triple_menu(case):
    _, scout, rules, _, _ = dependencies()
    return frozenset(triple for triple in scout.actual_menu(rules, case.checks) if len(triple) == 3)


def next_cases(case, reserve=(), high_only=False):
    _, scout, rules, _, _ = dependencies()
    for _, options in scout.legal_parent_sets(rules, case.checks):
        choices = tuple(tuple(bit for bit in sorted(bits) if bit not in reserve) for bits in options)
        if any(not bits for bits in choices):
            continue
        # Other available names at each holder are exchanged by a physical
        # isomorphism fixing the reserved names. Its extension fixes new names.
        consumed = tuple(bits[0] for bits in choices)
        assert rules.legal_local_move(case.checks, consumed, scout.FRESH_FOR_PARENT_TEST)
        for count in (2, 3):
            if not high_only or len(consumed) + count >= 5:
                yield case.child(consumed, count)


def dense(width, upper):
    rows = [bytearray(width) for _ in range(width)]
    for (a, b), value in zip(combinations(range(width), 2), upper, strict=True):
        rows[a][b] = rows[b][a] = value
    return tuple(map(bytes, rows))


def upper(rows):
    return bytes(rows[a][b] for a, b in combinations(range(len(rows)), 2))


def cut(rows, cutoff):
    if cutoff is None:
        return rows
    translate = bytes(min(k, cutoff + 1) for k in range(256))
    return tuple(row.translate(translate) for row in rows)


def measure(binary, cases):
    payload = "".join(" ".join(map(str, (case.width, len(case.supports), *case.masks))) + "\n"
                      for case in cases)
    measured = subprocess.run([binary], input=payload, text=True, capture_output=True, check=True)
    return tuple(Measured(case, dense(case.width, bytes.fromhex(line)))
                 for case, line in zip(cases, measured.stdout.splitlines(), strict=True))


def span_control(sample):
    span, scout, _, _, _ = dependencies()
    words = scout.parity_span(sample.case.checks)
    distances = span.measure_every_pair(words, sample.case.width)
    agreement = all(sample.rows[a][b] == (INFINITY if value == INFINITY else value + 1)
                    for a, row in enumerate(distances)
                    for b, value in enumerate(row) if a < b)
    assert agreement, sample.case
    return len(upper(sample.rows))


def prefix_pairs():
    data = json.loads(verified(G / "six_check.json"))
    cases = []
    for item in data["cases"]:
        first, second = (item[key] for key in ("source", "rival"))
        width = item["width"]
        cases.append(tuple(
            (Presentation(item["case"] + "/" + key, tuple(tuple(event["support"]) for event in side["history"]),
                          width), side["pair_minimum_upper_triangle"], side["exact_legal_triples"])
            for key, side in (("source", first), ("rival", second))
        ))
    return cases


def cap_baseline():
    data = json.loads(verified(D / "active_part.json"))["completions"][0]
    return (Presentation("active_part_completion_0", tuple(map(tuple, data["junction_supports"])),
                         data["width"]), data["true_triples"])


@cache
def physical(case):
    _, _, rules, _, classes = dependencies()
    users, neighbors = rules.incidence(case.checks)
    size = len(case.supports)
    counts = Counter(sites[0] for sites in users.values() if len(sites) == 1)
    adjacency = tuple(tuple(int(j in neighbors[i]) for j in range(size)) for i in range(size))
    return classes.ColoredMatrix.make(adjacency, tuple(counts[i] for i in range(size)))


def physically_same(left, right):
    *_, classes = dependencies()
    if len(left.supports) != len(right.supports):
        return False
    return next(classes.isometries(physical(left), physical(right)), None) is not None


@cache
def marked_part(case, triple):
    graph = nx.Graph()
    width = case.width
    for i, support in enumerate(case.supports):
        graph.add_edges_from((width + i, bit) for bit in support)
    retained = set(graph)
    marked = set(triple)
    for cut_bit in sorted(v for v in nx.articulation_points(graph) if v < width):
        if cut_bit in marked:
            return {"status": "mark_is_separator", "separator": cut_bit}
        side = nx.node_connected_component(graph.subgraph(set(graph) - {cut_bit}), triple[0])
        if not marked <= side:
            return {"status": "mark_spans_separator", "separator": cut_bit}
        retained &= side | {cut_bit}
    return {"status": "retained", "high_sites": case.high,
            "retained_high_sites": tuple(site for site in case.high if width + site in retained)}


def mark_incidence(case, triple):
    _, _, rules, _, _ = dependencies()
    users, neighbors = rules.incidence(case.checks)
    holders = tuple(tuple(users[bit]) for bit in triple)
    result = {"holders_by_mark": holders}
    if any(len(sites) != 1 for sites in holders):
        return result
    parents = tuple(sites[0] for sites in holders)
    return {**result,
            "pairwise_common_neighbors": tuple(tuple(sorted(neighbors[a] & neighbors[b]))
                                               for a, b in combinations(parents, 2)),
            "neighbors_common_to_all_three": tuple(sorted(set.intersection(*(neighbors[i] for i in parents))))}


def witness(left, right, cutoff, left_marks, right_marks, mapping):
    _, _, _, exact, _ = dependencies()
    exact.verify_map(cut(left.rows, cutoff), cut(right.rows, cutoff), left_marks, right_marks, mapping)
    assert not physically_same(left.case, right.case)
    assert triple_allowed(left.case, left_marks) and not triple_allowed(right.case, right_marks)
    changed = tuple((a, b) for a, b in combinations(range(left.case.width), 2)
                    if left.rows[a][b] != right.rows[mapping[a]][mapping[b]])
    result = {
        "kept_K_through": cutoff, "width": left.case.width, "bijection_left_to_right": mapping,
        "checked_upper_triangle_entries": len(upper(left.rows)),
        "full_entries_different_under_map": len(changed),
        "independent_span_entries_checked": [span_control(left), span_control(right)],
    }
    if changed:
        a, b = changed[0]
        result["first_full_difference"] = {"left_pair": [a, b], "right_pair": [mapping[a], mapping[b]],
                                           "left_K": left.rows[a][b], "right_K": right.rows[mapping[a]][mapping[b]]}
        next_cutoff = cutoff + 1
        left_count = upper(left.rows).count(next_cutoff)
        right_count = upper(right.rows).count(next_cutoff)
        assert exact.exact_map(cut(left.rows, next_cutoff), cut(right.rows, next_cutoff),
                               left_marks, right_marks) is None
        result["next_cutoff_rejection"] = {"kept_K_through": next_cutoff,
                                            "pairs_at_next_value": [left_count, right_count],
                                            "marked_isometry_exists": False}
    for tag, fixture, marks, verdict in (("left", left, left_marks, True), ("right", right, right_marks, False)):
        result[tag] = {**fixture.case.describe(), "mark": marks, "allowed": verdict,
                       "marked_part": marked_part(fixture.case, marks),
                       "mark_incidence_for_grading": mark_incidence(fixture.case, marks),
                       "full_upper_triangle_K_hex": upper(fixture.rows).hex()}
    return result


def branch(case, anchor):
    width = case.width
    return (case.child((anchor,), 2).child((width,), 2).child((width + 1,), 2)
            .child((width + 2, width + 4), 3))


def anchored_control(binary, examples):
    outcomes = []
    for pair in examples:
        old = tuple(archive[0] for archive in pair)
        width = old[0].width
        anchor = width - 1
        extended = tuple(branch(side, anchor) for side in old)
        for side in extended:
            replay(side)
        graft_scopes = extended[0].supports[-4:]
        names = (anchor, *range(width, width + 9))
        translate = {bit: i for i, bit in enumerate(names)}
        graft = Presentation("branch_alone_for_measurement",
                             tuple(tuple(translate[b] for b in scope) for scope in graft_scopes), len(names))
        assert set(translate) & set(range(width)) == {anchor}
        old_first, old_second, left, right, graft_measure = measure(binary, (*old, *extended, graft))
        for before, after in zip((old_first, old_second), (left, right), strict=True):
            for a, b in combinations(range(after.case.width), 2):
                if b < width:
                    expected = before.rows[a][b]
                elif a in translate:
                    expected = graft_measure.rows[translate[a]][translate[b]]
                else:
                    expected = before.rows[a][anchor] + graft_measure.rows[0][translate[b]] - 2
                assert after.rows[a][b] == expected, (before.case.prefix, a, b)
        identity = tuple(range(left.case.width))
        result = witness(left, right, FIRST_CUTOFF, MARK, MARK, identity)
        assert result["full_entries_different_under_map"] > 0
        assert not result["left"]["marked_part"]["retained_high_sites"]
        assert len(result["right"]["marked_part"]["retained_high_sites"]) == 1
        result["separator_distinction"] = anchor
        result["branch_distinctions_except_separator"] = names[1:]
        result["first_branch_site"] = len(old[0].supports), len(old[1].supports)
        result["two_sided_gluing_formula_entries_checked"] = 2 * len(upper(left.rows))
        outcomes.append(result)
    return outcomes


def local_roster(examples):
    eligible = ([], [])
    counts = {}
    for pair in examples:
        for side, (initial, _, _) in enumerate(pair):
            verdict = side == 0
            assert triple_allowed(initial, MARK) == verdict
            tiers = [(initial,)]
            info = counts[initial.prefix] = []
            for depth in range(3):
                tier = tiers[depth]
                # Expand every representative even if the current verdict
                # differs. Endpoint filtering uses only the actual verdict.
                selected = [case for case in tier if case.high and triple_allowed(case, MARK) == verdict]
                eligible[side].extend(selected)
                info.append({"additions": depth, "paths": len(tier), "eligible": len(selected),
                             "eligible_by_width": dict(sorted(Counter(case.width for case in selected).items())),
                             "eligible_with_high_in_marked_part": sum(
                                 bool(marked_part(case, MARK).get("retained_high_sites")) for case in selected
                             )})
                if depth < 2:
                    tiers.append(tuple(child for case in tier for child in next_cases(case, reserve=MARK)))
    return tuple(eligible[0]), tuple(eligible[1]), counts


def marked_signature(rows, mark):
    histograms = tuple(bytes(sorted(row)) for row in rows)
    internal = tuple(sorted(rows[a][b] for a, b in combinations(mark, 2)))
    return tuple(sorted(histograms)), tuple(sorted(histograms[i] for i in mark)), internal


def local_grade(left, right):
    _, _, _, exact, _ = dependencies()
    left_by_width, right_by_width = (Counter(sample.case.width for sample in side) for side in (left, right))
    width_pairs = {w: left_by_width[w] * right_by_width[w] for w in sorted(left_by_width.keys() & right_by_width)}
    active = tuple(tuple(bool(marked_part(sample.case, MARK).get("retained_high_sites")) for sample in side)
                   for side in (left, right))
    prior = None
    reports = {}
    best = None
    highest = FIRST_CUTOFF - 1
    max_finite = max((max((k for k in upper(item.rows) if k != INFINITY), default=0)
                      for item in (*left, *right)), default=0)
    for cutoff in (*range(FIRST_CUTOFF, max(FIRST_CUTOFF, max_finite) + 1), None):
        left_rows = tuple(cut(sample.rows, cutoff) for sample in left)
        right_rows = tuple(cut(sample.rows, cutoff) for sample in right)
        left_stamps = tuple(marked_signature(rows, MARK) for rows in left_rows)
        right_stamps = tuple(marked_signature(rows, MARK) for rows in right_rows)
        if prior is None:
            buckets = defaultdict(list)
            for j, stamp in enumerate(right_stamps):
                buckets[stamp].append(j)
            potential = ((i, j) for i, stamp in enumerate(left_stamps) for j in buckets[stamp])
            entering = sum(width_pairs.values())
        else:
            entering = len(prior)
            potential = ((i, j) for i, j in prior if left_stamps[i] == right_stamps[j])
        following = []
        matched_widths = Counter()
        both_active_widths = Counter()
        matched_prefixes = Counter()
        trials = physical_duplicates = 0
        first = None
        for i, j in potential:
            trials += 1
            mapping = exact.exact_map(left_rows[i], right_rows[j], MARK, MARK)
            if mapping is None:
                continue
            if physically_same(left[i].case, right[j].case):
                physical_duplicates += 1
                continue
            following.append((i, j))
            width = left[i].case.width
            matched_widths[width] += 1
            if active[0][i] and active[1][j]:
                both_active_widths[width] += 1
            matched_prefixes[(left[i].case.prefix, right[j].case.prefix)] += 1
            if first is None:
                first = (i, j, mapping)
        reports["full" if cutoff is None else str(cutoff)] = {
            "entering_path_pairs": entering, "exact_marked_comparisons": trials,
            "isometric_but_physically_identical": physical_duplicates,
            "opposing_cross_pairs_by_width": dict(sorted(matched_widths.items())),
            "opposing_cross_pairs_with_high_in_both_marked_parts_by_width": dict(sorted(both_active_widths.items())),
            "opposing_cross_pairs_by_prefix": {
                f"{a} versus {b}": n for (a, b), n in sorted(matched_prefixes.items())
            },
        }
        if first is not None:
            if cutoff is not None:
                highest = cutoff
            best = (cutoff, *first)
        prior = following
        if not prior and cutoff is not None:
            reports["full"] = {"opposing_cross_pairs_by_width": {}, "excluded_by_cutoff": cutoff}
            break
    return {"equal_width_path_pairs": width_pairs, "by_cutoff": reports,
            "largest_opposing_capped_K": highest if best is not None else None,
            "full_opposing_collision": best is not None and best[0] is None,
            "witness": None if best is None else witness(
                left[best[1]], right[best[2]], best[0], MARK, MARK, best[3]
            )}


def distinct_cap_placements(initial):
    roster = []
    raw = Counter()
    for candidate in next_cases(initial, high_only=True):
        width = candidate.width
        raw[width] += 1
        if not any(physically_same(candidate, prior) for prior in roster if prior.width == width):
            roster.append(candidate)
    return tuple(roster), dict(sorted(raw.items()))


def inverse(mapping):
    return tuple(mapping.index(i) for i in range(len(mapping)))


def cap_conflict(classes, left_quotient, right_quotient, left_menu, right_menu, block_map):
    mapping = left_quotient.lift(right_quotient, block_map)
    if classes.transported(left_menu, mapping) == right_menu:
        # The remaining maps differ by a left automorphism. Checking its
        # generators suffices to decide invariance of the entire menu.
        _, _, generators = left_quotient.automorphisms()
        changer = next((g for g in generators if classes.transported(left_menu, g) != left_menu), None)
        if changer is None:
            return None
        mapping = tuple(mapping[changer[i]] for i in range(len(mapping)))
    image = classes.transported(left_menu, mapping)
    assert image != right_menu
    if image - right_menu:
        right_mark = min(tuple(sorted(triple)) for triple in image - right_menu)
        backwards = inverse(mapping)
        left_mark = tuple(sorted(backwards[i] for i in right_mark))
        return False, left_mark, right_mark, mapping
    right_mark = min(tuple(sorted(triple)) for triple in right_menu - image)
    backwards = inverse(mapping)
    return True, right_mark, tuple(sorted(backwards[i] for i in right_mark)), backwards


def cap_grade(roster):
    *_, classes = dependencies()
    menus = tuple(triple_menu(item.case) for item in roster)
    pairs = [(i, j) for i, j in combinations(range(len(roster)), 2)
             if roster[i].case.width == roster[j].case.width]
    pair_count = Counter(roster[i].case.width for i, _ in pairs)
    reports = {}
    best = None
    max_finite = max((max((k for k in upper(item.rows) if k != INFINITY), default=0)
                      for item in roster), default=0)
    for cutoff in (*range(3, max_finite + 1), None):
        quotients = tuple(classes.Quotient.make(cut(sample.rows, cutoff)) for sample in roster)
        following = []
        isometric = Counter()
        opposite = Counter()
        invariant_pass = 0
        for i, j in pairs:
            left, right = quotients[i], quotients[j]
            if left.colored.invariant != right.colored.invariant:
                continue
            invariant_pass += 1
            block = next(classes.isometries(left.colored, right.colored), None)
            if block is None:
                continue
            following.append((i, j))
            isometric[roster[i].case.width] += 1
            conflict = cap_conflict(classes, left, right, menus[i], menus[j], block)
            if conflict is not None:
                width = roster[i].case.width
                opposite[width] += 1
                if best is None or best[0] != cutoff:
                    inverted, a, b, mapping = conflict
                    best = cutoff, (j if inverted else i), (i if inverted else j), a, b, mapping
        reports["full" if cutoff is None else str(cutoff)] = {
            "entering_pairs": len(pairs), "exact_isometry_comparisons": invariant_pass,
            "isometric_pairs_by_width": dict(sorted(isometric.items())),
            "opposing_pairs_by_width": dict(sorted(opposite.items())),
        }
        pairs = following
        if not pairs and cutoff is not None:
            reports["full"] = {"isometric_pairs_by_width": {}, "opposing_pairs_by_width": {},
                               "excluded_by_cutoff": cutoff}
            break
    return {"distinct_placements_by_width": dict(sorted(Counter(item.case.width for item in roster).items())),
            "placements_with_legal_triples_by_width": dict(sorted(Counter(
                item.case.width for item, menu in zip(roster, menus, strict=True) if menu
            ).items())),
            "equal_width_type_pairs": dict(sorted(pair_count.items())), "by_cutoff": reports,
            "largest_opposing_capped_K": best[0] if best is not None else None,
            "full_opposing_collision": best is not None and best[0] is None,
            "witness": None if best is None else witness(
                roster[best[1]], roster[best[2]], best[0], best[3], best[4], best[5]
            )}


def relabel_control(sample, chosen):
    _, _, _, exact, _ = dependencies()
    images = list(range(sample.case.width))
    Random(612018).shuffle(images)
    names = inverse(tuple(images))
    right_rows = tuple(bytes(sample.rows[a][b] for b in names) for a in names)
    right_marks = tuple(sorted(images[i] for i in chosen))
    found = exact.exact_map(sample.rows, right_rows, chosen, right_marks)
    assert found is not None
    exact.verify_map(sample.rows, right_rows, chosen, right_marks, found)
    return {"seed": 612018, "entries_checked": len(upper(sample.rows)),
            "old_marks": chosen, "new_marks": right_marks, "known_bijection": images,
            "checked_bijection": found}


def run(binary):
    examples = prefix_pairs()
    baseline, baseline_triples = cap_baseline()
    frozen = [part for pair in examples for part in pair]
    fixtures = tuple(case for case, _, _ in frozen)
    controls = {}
    for sample, (_, archived, menu) in zip(measure(binary, fixtures), frozen, strict=True):
        replay(sample.case)
        assert upper(sample.rows) == bytes(archived)
        assert triple_menu(sample.case) == frozenset(map(frozenset, menu))
        controls[sample.case.prefix] = {"archived_entries_checked": len(archived),
                                       "independent_span_entries_checked": span_control(sample)}
    (base_sample,) = measure(binary, (baseline,))
    replay(baseline)
    assert triple_menu(baseline) == frozenset(map(frozenset, baseline_triples))
    assert len(baseline_triples) == 8
    controls[baseline.prefix] = {"actual_legal_triples": len(baseline_triples),
                                 "independent_span_entries_checked": span_control(base_sample)}
    controls["arbitrary_full_relabeling"] = relabel_control(base_sample, tuple(baseline_triples[0]))
    grafted = anchored_control(binary, examples)
    left, right, local_counts = local_roster(examples)
    print(f"Marked local path endpoints meeting the filters: {len(left)} / {len(right)}", file=sys.stderr)
    local_results = local_grade(measure(binary, left), measure(binary, right))
    cap_placements, raw = distinct_cap_placements(baseline)
    print(f"Distinct high-cap placements: {len(cap_placements)}", file=sys.stderr)
    for case in cap_placements:
        replay(case)
    cap_results = cap_grade(measure(binary, cap_placements))
    cap_results["raw_placements_by_width"] = raw
    return {
        "entry_encoding": "K = D + 1, lexicographic upper triangle, hexadecimal ff denotes infinity",
        "cutoff_rule": "Coalesce K strictly greater than L at L+1",
        "sources": {str(path.relative_to(PROOFS)): digest for path, digest in FROZEN.items()},
        "controls": controls,
        "fixed_single_distinction_branch": grafted,
        "two_serial_additions_per_side": {"generation": local_counts, **local_results},
        "one_high_cap_on_active_prefix": cap_results,
    }


def main():
    with TemporaryDirectory(prefix="high-cross-") as scratch:
        binary = str(Path(scratch) / "cross_search")
        subprocess.run(["c++", "-std=c++20", "-O3", "-Wall", "-Wextra", "-Wpedantic",
                        str(HERE / "cross_search.cpp"), "-o", binary], check=True)
        print(json.dumps(run(binary), indent=2))


if __name__ == "__main__":
    main()
