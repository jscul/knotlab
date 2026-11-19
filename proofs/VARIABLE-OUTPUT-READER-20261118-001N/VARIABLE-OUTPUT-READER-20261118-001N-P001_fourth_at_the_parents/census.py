"""Exact tables, literal triple menus, and junction roles for four three-output joins."""

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
L = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001L" / "VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third"
SPEC = spec_from_file_location("fourth_output_predecessor", L / "census.py")
old = module_from_spec(SPEC)
sys.modules[SPEC.name] = old
SPEC.loader.exec_module(old)
checker, literal, algebra, exact = old.checker, old.literal, old.algebra, old.exact
mask, bits = old.mask, old.bits


def next_layer(layer):
    buckets = defaultdict(list)
    seen = set()
    for owner in layer:
        actions = [(group, 2) for group in owner.groups((2, 3))]
        if owner.extra < 2:
            actions.extend((group, 3) for group in owner.groups((1, 2, 3)))
        for group, h in actions:
            grown = replace(owner.grow(group, h), extra=owner.extra + (h == 3))
            key = grown.extra, grown.neighbors, grown.loose
            if key in seen:
                continue
            seen.add(key)
            color = old.color_incidence(grown)
            bucket = buckets[grown.extra, color.invariant]
            if not any(next(exact.isometries(earlier, color), None) is not None for earlier, _ in bucket):
                bucket.append((color, grown))
    return tuple(shape for bucket in buckets.values() for _, shape in bucket)


def dense(record, cutoff):
    width = record.fixture.width
    rows = [[0] * width for _ in range(width)]
    for (a, b), k in zip(old.pairs(width), record.entries, strict=True):
        rows[a][b] = rows[b][a] = k if cutoff is None else min(k, cutoff + 1)
    return tuple(map(tuple, rows))


def word_image(word, image):
    return mask(image[i] for i in bits(word))


def fourth(record):
    return tuple(i for i, (_, h) in enumerate(record.fixture.actions, 1) if h == 3)[-1]


def literal_record(record):
    rows = checker.replay(record.history)
    roles = [(len(row["operands"]), len(row["fresh"])) for row in rows]
    assert roles[:3] == [(0, 3), (1, 3), (1, 3)]
    assert sum(h == 3 for _, h in roles[1:]) == 4
    assert all(h == 3 or h == 2 and p >= 2 for p, h in roles[3:])
    i = fourth(record)
    return {"supports": [row["support"] for row in rows],
            "fourth_three_fresh_site": i, "fourth_move": rows[i], "moves": roles}


def mark_status(record, mark):
    owners, neighbors = literal.incidence(record.history)
    if any(len(owners[i]) > 1 for i in mark):
        return {"verdict": "shared_input", "shared_distinctions": [i for i in mark if len(owners[i]) > 1]}
    holders = tuple(owners[i][0] for i in mark)
    if len(set(holders)) != 3:
        return {"verdict": "repeated_holder", "holders": holders}
    pair_witnesses = [sorted(neighbors[a] & neighbors[b], key=int) for a, b in combinations(holders, 2)]
    all_common = sorted(set.intersection(*(neighbors[i] for i in holders)), key=int)
    verdict = "legal"
    if not all(pair_witnesses):
        verdict = "missing_pair_witness"
    elif all_common:
        verdict = "common_witness_of_all_three"
    return {"verdict": verdict, "holders": holders, "pair_witnesses": pair_witnesses, "common_witnesses": all_common}


def same_block(neighbors, first, second):
    if first == second:
        return True
    for excluded in neighbors.keys() - {first, second}:
        queue = [first]
        seen = {first, excluded}
        for site in queue:
            successors = neighbors[site] - seen
            seen.update(successors)
            queue.extend(successors)
        if second not in seen:
            return False
    return True


def roles(record, site):
    _, neighbors = literal.incidence(record.history)
    by_role = defaultdict(list)
    for mark in sorted(bits(word) for word in record.menu):
        status = mark_status(record, mark)
        assert status["verdict"] == "legal"
        parents = status["holders"]
        held = site in parents
        witness = any(site in pair for pair in status["pair_witnesses"])
        adjacent = bool(set(parents) & neighbors[site])
        if held:
            by_role["holder"].append(mark)
        if witness:
            by_role["pair_witness"].append(mark)
        if not (held or witness):
            if adjacent:
                by_role["adjacent_only"].append(mark)
            if all(same_block(neighbors, site, i) for i in parents):
                by_role["in_marked_block_without_direct_role"].append(mark)
    return dict(by_role)


def choose_mark(left, right, image):
    right_menu = right.menu
    for word in sorted(left.menu):
        mapped = word_image(word, image)
        if mapped not in right_menu:
            return bits(word), bits(mapped)
    inverse = exact.inverse(image)
    for word in sorted(right_menu):
        preimage = word_image(word, inverse)
        if preimage not in left.menu:
            return bits(preimage), bits(word)
    return None


def automorphisms(quotient):
    if len(set(quotient.colored.colors)) != len(quotient.blocks):
        return quotient.automorphisms()[2]
    identity = list(range(sum(map(len, quotient.blocks))))
    swaps = []
    for block in quotient.blocks:
        for right in block[1:]:
            left = block[0]
            permutation = identity.copy()
            permutation[left], permutation[right] = right, left
            swaps.append(tuple(permutation))
    return swaps


def orbit(word, generators, width):
    seed = tuple(range(width))
    queue = [word]
    transport = {word: seed}
    for item in queue:
        for move in generators:
            image = word_image(item, move)
            if image not in transport:
                transport[image] = tuple(move[i] for i in transport[item])
                queue.append(image)
    return transport


def moved_images(left, right, to_right, generators, totals, witnesses):
    width = left.fixture.width
    target_code = algebra.span(right.stars)
    for site, support in left.history:
        word = mask(support)
        options = orbit(word, generators, width)
        lost = [(word_image(image, to_right), p) for image, p in options.items()
                if word_image(image, to_right) not in right.stars]
        if not lost:
            continue
        affected = roles(left, site)
        site_is_fourth = int(site) == fourth(left)
        for image, from_left in lost:
            stays = image in target_code
            totals["moved_support_images"] += 1
            totals["retained_as_equation" if stays else "lost_equation"] += 1
            totals["source_and_target_both_empty"] += not (left.menu or right.menu)
            totals["from_fourth_junction"] += site_is_fourth
            if not affected:
                totals["no_recorded_marked_role"] += 1
            for key in affected:
                totals[key] += 1
            direct = "holder" in affected or "pair_witness" in affected
            kind = "full_direct_moved_support" if direct else "full_moved_support"
            if kind not in witnesses:
                image_map = tuple(to_right[i] for i in from_left)
                witnesses[kind] = (left, right, image_map, site, support, bits(image), stays, affected)


def screen(records, cutoff, moved, examples):
    counts = Counter(tables=len(records))
    buckets = defaultdict(list)
    has_menu_defect = set()

    def measure_map(left, right, image, label, mat_left, mat_right):
        changes_menu = old.transport(left.menu, image) != right.menu
        changes_stars = old.transport(left.stars, image) != right.stars
        if changes_menu or changes_stars:
            assert exact.disagreement(mat_left, mat_right, image) is None
        if changes_menu:
            counts[f"{label}_opposing_menus"] += 1
            key = "D4" if cutoff == 5 else "D5" if cutoff == 6 else "full"
            examples.setdefault(key, (left, right, image))
            _, wrong = choose_mark(left, right, image)
            if mask(wrong) in right.menu:
                source_mark = choose_mark(left, right, image)[0]
                wrong_status = mark_status(left, source_mark)
            else:
                wrong_status = mark_status(right, wrong)
            counts[f"opposition_to_{wrong_status['verdict']}"] += 1
        counts[f"{label}_moves_supports"] += changes_stars
        return changes_menu, changes_stars

    for position, record in enumerate(records):
        matrix = dense(record, cutoff)
        q = exact.Quotient.make(matrix)
        generators = automorphisms(q)
        counts["self_generators"] += len(generators)
        different = False
        for image in generators:
            bad_menu, bad_stars = measure_map(record, record, image, "self", matrix, matrix)
            different |= bad_stars
            if bad_menu:
                has_menu_defect.add(position)
        if cutoff is None and different:
            moved_images(record, record, tuple(range(record.fixture.width)), generators, moved, examples)
        key = hash(q.colored.invariant)
        for index in buckets[key]:
            other = records[index]
            other_matrix = dense(other, cutoff)
            other_q = exact.Quotient.make(other_matrix)
            counts["cross_candidates"] += 1
            found = next(exact.isometries(q.colored, other_q.colored), None)
            if found is None:
                continue
            image = q.lift(other_q, found)
            assert exact.disagreement(matrix, other_matrix, image) is None
            counts["cross_isometric_pairs"] += 1
            opposing, _ = measure_map(record, other, image, "cross", matrix, other_matrix)
            if opposing or position in has_menu_defect or index in has_menu_defect:
                counts["cross_pairs_with_an_opposing_map"] += 1
            if cutoff is None:
                moved_images(record, other, image, generators, moved, examples)
                moved_images(other, record, exact.inverse(image), automorphisms(other_q), moved, examples)
        buckets[key].append(position)
    return {key: value for key, value in counts.items() if value}


def two_method_record(history):
    table, _, menu = checker.measure(history, independent=True)
    owners, neighbors = literal.incidence(history)
    width = len(owners)
    loose = tuple(sum(groups == [site] for groups in owners.values()) for site, _ in history)
    ordinary = tuple(mask(map(int, neighbors[site])) for site, _ in history)
    trace = checker.replay(history)
    actions = tuple((tuple(map(int, row["parents"])), len(row["fresh"])) for row in trace[1:])
    fixture = old.Fixture(ordinary, loose, 2, actions)
    assert width == fixture.width
    return old.Observation(fixture, tuple(table[pair] for pair in old.pairs(width)), history,
                           frozenset(mask(row) for _, row in history), frozenset(map(mask, menu)))


def rank_certificate(record):
    width = record.fixture.width
    table = dict(zip(old.pairs(width), record.entries, strict=True))
    result = []
    for cutoff in (5, 6):
        observe = {pair: k if k <= cutoff else None for pair, k in table.items()}
        known, remaining, _, _ = algebra.force_from_table(observe, width, cutoff)
        assert known <= algebra.span(record.stars)
        rank = algebra.rank(known)
        result.append({"D_cutoff": cutoff - 1, "forced_rank": rank, "unresolved_short_bonds": len(remaining),
                       "forces_every_matching_rival_equation_space": rank == record.fixture.sites})
    return {"rival_rank_ceiling_after_J_exclusion": record.fixture.sites, "short_rank_checks": result}


def rank_sweep(records):
    """Find an actual unique short witness for each independent source star."""
    totals = Counter()
    first_deficit = None
    for record in records:
        width = record.fixture.width
        exact_entries = dense(record, None)
        closed = [[1 << i for i in range(width)] for _ in range(7)]
        for (i, j), size in zip(old.pairs(width), record.entries, strict=True):
            for limit in range(size, 7):
                closed[limit][i] |= 1 << j
                closed[limit][j] |= 1 << i
        forced_sizes = []
        for star in record.stars:
            size = star.bit_count()
            if any(exact_entries[a][b] == size and closed[size][a] & closed[size][b] == star
                   for a, b in combinations(bits(star), 2)):
                forced_sizes.append(size)
        low = sum(size <= 5 for size in forced_sizes)
        high = len(forced_sizes)
        totals["all_star_equations_forced_at_D4"] += low == record.fixture.sites
        totals["all_star_equations_forced_at_D5"] += high == record.fixture.sites
        totals["sources"] += 1
        if high == record.fixture.sites:
            totals["arbitrary_rival_spaces_forced_at_D5"] += 1
            continue
        result = rank_certificate(record)["short_rank_checks"][-1]
        totals["refined_rank_checks"] += 1
        totals["arbitrary_rival_spaces_forced_at_D5"] += result["forced_rank"] == record.fixture.sites
        if first_deficit is None and result["forced_rank"] < record.fixture.sites:
            first_deficit = {"width": width, "replay": literal_record(record), **result}
    return {**totals, "first_deficit": first_deficit}


def roles_on_one_map(left, right, image):
    target = algebra.span(right.stars)
    result = []
    for site, row in left.history:
        projected = word_image(mask(row), image)
        if projected in right.stars:
            continue
        result.append({"site": int(site), "support": row, "image": bits(projected),
                       "kept_as_parity_equation": projected in target,
                       "is_fourth_three_fresh_site": int(site) == fourth(left), "roles": roles(left, site)})
    return result


def describe_comparison(left, right, image, cutoff):
    result = old.witness(left, right.history, image, cutoff=cutoff)
    result["source_replay"] = literal_record(left)
    result["right_replay"] = literal_record(right)
    result["same_equation_space"] = algebra.span(old.transport(left.stars, image)) == algebra.span(right.stars)
    result["moved_support_roles_under_the_map"] = roles_on_one_map(left, right, image)
    mark = result["marked_example"]
    if mark["left"] is not None:
        result["marked_examples_by_law"] = [mark_status(left, mark["left"]), mark_status(right, mark["right"])]
    result["unrestricted_rank_certificates"] = [rank_certificate(record) for record in (left, right)]
    return result


def planted_D4():
    old_rows = old.previous.load_source("frontier.json")["sharp_distance_four"]["junction_supports"]
    rows = list(map(tuple, old_rows))
    rows[5] = (*rows[5], 26)
    rows[-1] = (*rows[-1], 25)
    fixture = two_method_record(old.previous.named(rows))
    mapping = list(range(27))
    mapping[19], mapping[20] = 20, 19
    return describe_comparison(fixture, fixture, mapping, 5)


def run(last, engine):
    stages, examples = [], {}
    layer = old.starters()
    adjacent_example = None
    total_moved = Counter()
    positive_recheck = []
    for n in range(4, (last - 5) // 2 + 1):
        layer = next_layer(layer)
        complete = [shape for shape in layer if shape.extra == 2]
        if not complete:
            continue
        records = old.measured(complete, engine)
        width = 2 * n + 5
        first = records[0]
        direct = two_method_record(first.history)
        assert first.entries == direct.entries and first.menu == direct.menu
        literal_record(first)
        positive_recheck.append(width)
        if adjacent_example is None:
            for record in records:
                site = str(fourth(record))
                marks = roles(record, site).get("adjacent_only", [])
                if marks:
                    mark = marks[0]
                    adjacent_example = {"width": width, "replay": literal_record(record), "mark": mark,
                                        "law": mark_status(record, mark), "rank": rank_certificate(record)}
                    break
        summary = {"width": width, "source_types": len(records), "with_legal_triples": sum(bool(r.menu) for r in records),
                   "literal_legal_triples": sum(len(r.menu) for r in records)}
        moved = Counter()
        summary["full"] = screen(records, None, moved, examples)
        rank = rank_sweep(records)
        exact_at_five = rank["arbitrary_rival_spaces_forced_at_D5"] == len(records)
        # Equal equation spaces give the same untruncated table on these names.
        summary["D5"] = summary["full"].copy() if exact_at_five else screen(records, 6, moved, examples)
        summary["D4"] = screen(records, 5, moved, examples)
        summary["full_moved_roles"] = dict(moved)
        summary["unrestricted_D5_rank_screen"] = rank
        summary["D5_isometries_equal_full_isometries_from_rank"] = exact_at_five
        total_moved.update(moved)
        stages.append(summary)
        print(f"width {width}: {len(records)} source types; full moves {moved['moved_support_images']}", file=sys.stderr, flush=True)

    witnesses = {}
    for name, example in examples.items():
        left, right, image, *details = example
        cutoff = 5 if name == "D4" else 6 if name == "D5" else None
        result = describe_comparison(left, right, image, cutoff)
        if details:
            site, support, at_target, equation, affected = details
            result["moved_support_role"] = {"site": site, "old_support": support, "image": at_target,
                                             "retained_as_equation": equation, "role_by_mark": affected,
                                             "is_fourth_three_fresh_site": int(site) == fourth(left)}
        witnesses[name] = result
    return {"freeze": "35ab25cfb", "stages": stages, "literal_two_method_checks_at_widths": positive_recheck,
            "full_moved_support_totals": dict(total_moved), "fourth_adjacent_to_a_legal_holder": adjacent_example,
            "witnesses": witnesses, "planted_D4_control": planted_D4()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=27)
    arguments = parser.parse_args()
    if not 15 <= arguments.width <= 27 or arguments.width % 2 == 0:
        parser.error("width must be odd and between 15 and 27")
    with TemporaryDirectory(prefix="fourth-output-census-") as scratch:
        engine = Path(scratch) / "measure"
        subprocess.run(["c++", "-std=c++20", "-O2", "-pthread", L / "census.cpp", "-o", engine], check=True)
        result = run(arguments.width, engine)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
