"""Reconstruct component and sign tests from the named rows of each funded cut.

For an actual connected closure let C be its set of all-even named words.
An operator at distinction e sends |w> to (-1)^(w[e]+g[e]) |w+t[e]>.
All entries of t and g, including every repeated meeting, are solved directly
from the local involution, commutation and product requirements. A separate
checker composes the resulting maps on the original named carrier.
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
import time


HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.name
HISTORY = (
    HERE.parents[2] / "artifacts" / TICKET / (TICKET + "-E001_closures")
    / "panels_histories.json.gz"
)
PANEL_NAMES = ("T", "E", "M", "S")
SEED = 20261126


def bits(indices):
    value = 0
    for index in indices:
        value |= 1 << index
    return value


def set_indices(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def xor_masks(masks):
    value = 0
    for mask in masks:
        value ^= mask
    return value


def basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            index = vector.bit_length() - 1
            if index not in pivots:
                pivots[index] = vector
                break
            vector ^= pivots[index]
    return pivots


def in_span(vector, pivots):
    while vector:
        i = vector.bit_length() - 1
        if i not in pivots:
            return False
        vector ^= pivots[i]
    return True


def scalar_counts(row_masks, name_count, odd_rows=()):
    odd_rows = set(odd_rows)
    augmented = basis(
        (row << 1) | (i in odd_rows) for i, row in enumerate(row_masks)
    )
    # A pivot at the constant column represents 0 = 1.
    rank = len(augmented) - (0 in augmented)
    return {
        "rank": rank, "augmented_rank": len(augmented), "names": name_count,
        "words": 0 if 0 in augmented else 1 << (name_count - rank),
    }


def solve_binary(equations):
    echelon = basis((left << 1) | right for left, right in equations)
    if 0 in echelon:
        return None
    solution = 0
    for pivot, augmented in sorted(echelon.items()):
        left = augmented >> 1
        if ((left & solution).bit_count() & 1) != (augmented & 1):
            solution |= 1 << (pivot - 1)
    return solution


@dataclass(frozen=True)
class Part:
    holders: tuple
    names: tuple
    loose: tuple

    def as_dict(self):
        return {k: list(getattr(self, k)) for k in ("holders", "names", "loose")}


def components(rows):
    owners = defaultdict(list)
    neighbors = [set() for _ in rows]
    for holder, row in enumerate(rows):
        assert row and len(row) == len(set(row))
        for name in row:
            owners[name].append(holder)
    for holders in owners.values():
        assert 1 <= len(holders) <= 2
        if len(holders) == 2:
            a, b = holders
            neighbors[a].add(b)
            neighbors[b].add(a)
    unseen = set(range(len(rows)))
    result = []
    while unseen:
        reached = set()
        pending = [min(unseen)]
        while pending:
            a = pending.pop()
            if a in unseen:
                unseen.remove(a)
                reached.add(a)
                pending.extend(neighbors[a])
        names = sorted({name for i in reached for name in rows[i]})
        loose = tuple(name for name in names if len(owners[name]) == 1)
        result.append(Part(tuple(sorted(reached)), tuple(names), loose))
    return result


def physical_equations(local_rows, n, odd_holder):
    # t[e][f] toggles physical distinction f when operator e acts.
    def shift(e, f):
        return 1 << (n * e + f)

    def sign(e):
        return 1 << (n * n + e)

    for e in range(n):
        yield shift(e, e), 0
        for row in local_rows:
            # Each individual shift preserves C. Each holder's net shift is zero.
            yield xor_masks(shift(e, f) for f in row), 0
            yield xor_masks(shift(f, e) for f in row), 0
    for i, row in enumerate(local_rows):
        local_phase = xor_masks(sign(e) for e in row)
        for left, right in combinations(row, 2):
            yield shift(left, right) ^ shift(right, left), 0
            # Rightmost operator acts first.
            local_phase ^= shift(right, left)
        yield local_phase, int(i == odd_holder)


def signed_words(rows, names, odd_holder):
    index_of = {name: i for i, name in enumerate(names)}
    local_rows = [[index_of[name] for name in row] for row in rows]
    n = len(names)
    assignment = solve_binary(physical_equations(local_rows, n, odd_holder))
    if assignment is None:
        return None
    n_mask = (1 << n) - 1
    shifts = [(assignment >> (e * n)) & n_mask for e in range(n)]
    phases = (assignment >> (n * n)) & n_mask
    return {"physical_name_order": list(names), "shift_masks": shifts, "sign_mask": phases}


def expand_reading(reading):
    names = reading["physical_name_order"]
    signs = reading["sign_mask"]
    return {
        name: (bits(names[j] for j in set_indices(shift)), (signs >> i) & 1)
        for i, (name, shift) in enumerate(zip(names, reading["shift_masks"], strict=True))
    }


def check_signed_words(rows, odd_holders, operators):
    """Check an exact operator identity on all words by composing affine signs."""
    masks = list(map(bits, rows))
    names = {name for row in rows for name in row}
    assert names == operators.keys()
    for name, (shift, _) in operators.items():
        assert not (shift >> name) & 1
        assert all((row & shift).bit_count() % 2 == 0 for row in masks)
    for holder, row in enumerate(rows):
        for a, b in combinations(row, 2):
            assert ((operators[a][0] >> b) ^ (operators[b][0] >> a)) & 1 == 0
        translation = 0
        constant = 0
        for name in reversed(row):
            shift, sign = operators[name]
            constant ^= ((translation >> name) & 1) ^ sign
            translation ^= shift
        # The w-dependent exponent is the parity of the original holder in C.
        assert translation == 0 and constant == (holder in odd_holders)


def audit_closed_part(rows, older_rows, part, parent_part, archive_row=None):
    new_holders = set(part.holders) - set(parent_part.holders)
    assert len(new_holders) == 1
    (terminal,) = new_holders
    assert terminal >= len(older_rows)
    closing = rows[terminal]
    assert set(closing) == set(parent_part.loose)
    assert parent_part.names == part.names
    assert xor_masks(bits(older_rows[i]) for i in parent_part.holders) == bits(closing)
    local_rows = [rows[i] for i in part.holders]
    local_masks = list(map(bits, local_rows))
    index = part.holders.index(terminal)
    even = scalar_counts(local_masks, len(part.names))
    odd = scalar_counts(local_masks, len(part.names), [index])
    assert even["rank"] == len(part.holders) - 1 and not odd["words"]
    deleted = []
    paired = []
    for holder in range(len(local_rows)):
        remaining = local_masks[:holder] + local_masks[holder + 1:]
        changed = [] if holder == index else [index - (holder < index)]
        assert scalar_counts(remaining, len(part.names), changed)["words"] == even["words"]
        deleted.append(part.holders[holder])
        if holder != index:
            assert scalar_counts(local_masks, len(part.names), [index, holder]) == even
            paired.append(part.holders[holder])
    reading = signed_words(local_rows, part.names, index)
    if reading is not None:
        check_signed_words(local_rows, {index}, expand_reading(reading))
    if archive_row is not None:
        assert archive_row["holder"] == terminal and not archive_row["fresh"]
        assert set(archive_row["inputs"]) == set(closing)
        assert archive_row["component_holders"] == list(part.holders)
        assert archive_row["component_names"] == list(part.names)
        assert archive_row["old_component_holders"] == list(parent_part.holders)
        assert archive_row["old_component_loose"] == list(parent_part.loose)
        assert archive_row["all_even_scalar"] == even and archive_row["single_odd_scalar"] == odd
        assert archive_row["operator_positive"] == (reading is not None)
    return {
        "terminal_holder": terminal, "holder_ids": list(part.holders),
        "older_holders": list(parent_part.holders), "closing_inputs": list(closing),
        "name_count": len(part.names), "ordinary_even_words": even["words"],
        "ordinary_single_odd_words": odd["words"],
        "each_single_rule_deleted_restores_even_count": len(deleted),
        "each_additional_old_sign_flip_restores_even_count": len(paired),
        "signed_permutation": reading,
    }


def audit_births(older_rows, rows, births, law):
    assert rows[:len(older_rows)] == older_rows
    assert [b["holder"] for b in births] == list(range(len(older_rows), len(rows)))
    owners = defaultdict(list)
    for i, row in enumerate(older_rows):
        for name in row:
            owners[name].append(i)
    old_masks = list(map(bits, older_rows))
    old_space = basis(old_masks)
    fresh_this_cut = set()
    positive_grants = 0
    for birth in births:
        row = rows[birth["holder"]]
        inputs = set(row) & owners.keys()
        fresh = set(row) - inputs
        assert set(row) == set(birth["support"])
        assert inputs == set(birth["inputs"]) and fresh == set(birth["new_names"])
        assert birth["fresh"] == len(fresh)
        assert inputs and all(len(owners[name]) == 1 for name in inputs)
        assert set(birth["parents"]) == {owners[name][0] for name in inputs}
        assert len(inputs) == len(birth["parents"])
        assert fresh.isdisjoint(fresh_this_cut)
        fresh_this_cut.update(fresh)
        positive_grants += bool(fresh)
        if law == "parity":
            implied = in_span(bits(inputs), old_space)
            assert implied == (not fresh)
            certificate = birth["old_span_rows"]
            assert (certificate is not None) == implied
            if certificate is not None:
                assert xor_masks(old_masks[i] for i in certificate) == bits(inputs)
        else:
            assert fresh
    if law == "parity":
        new_masks = list(map(bits, rows))
        even_old = scalar_counts(old_masks, len(owners))["words"]
        even_new = scalar_counts(new_masks, len(owners) + len(fresh_this_cut))["words"]
        # For a fixed old word, each row with f > 0 has exactly 2^(f-1)
        # extensions, and every zero-fresh row is already implied.
        exponent = len(fresh_this_cut) - positive_grants
        assert even_new == even_old * (1 << exponent)
    return positive_grants


def signed_union(rows, parts, closed, archive_union):
    keys = [part for part in parts if not part.loose]
    terminals = [closed[part.holders]["terminal_holder"] for part in keys]
    row_masks = list(map(bits, rows))
    all_names = [name for part in parts for name in part.names]
    assert len(set(all_names)) == len(all_names)
    if archive_union is not None:
        assert archive_union["ordered_terminal_holders"] == terminals
        archived = {
            tuple(s["signs_by_closing_holder"]): s for s in archive_union["scenarios"]
        }
        assert len(archived) == 1 << len(keys)
    outcomes = []
    for signs in product((0, 1), repeat=len(keys)):
        odd = {t for t, sign in zip(terminals, signs, strict=True) if sign}
        scalar = scalar_counts(row_masks, len(all_names), odd)
        per_part = []
        words_product = 1
        readings = {}
        failed_odd = []
        for part in parts:
            local_rows = [row_masks[i] for i in part.holders]
            odd_local = [i for i, h in enumerate(part.holders) if h in odd]
            part_scalar = scalar_counts(local_rows, len(part.names), odd_local)
            words_product *= part_scalar["words"]
            part_admits = True
            if odd_local:
                assert len(odd_local) == 1 and not part.loose
                reading = closed[part.holders]["signed_permutation"]
                if reading is None:
                    part_admits = False
                    failed_odd.append(part.holders[odd_local[0]])
                else:
                    readings.update(expand_reading(reading))
            else:
                readings.update((name, (0, 0)) for name in part.names)
            per_part.append({
                "holders": list(part.holders), "loose": list(part.loose),
                "operator_admits": part_admits, "scalar": part_scalar,
                "scalar_admits": bool(part_scalar["words"]),
            })
        assert words_product == scalar["words"]
        admits = not failed_odd
        if admits:
            # Includes the entire still-growing part and every older closed part.
            check_signed_words(rows, odd, readings)
        if archive_union is not None:
            stored = archived[signs]
            assert set(stored["odd_holders"]) == odd
            assert stored["scalar"] == scalar and stored["scalar_admits"] == bool(scalar["words"])
            assert stored["operator_admits"] == admits
            assert stored["components"] == per_part
        outcomes.append({
            "signs": list(signs), "odd_holders": sorted(odd), "scalar": scalar,
            "operator_admits": admits, "failed_odd_component_terminals": failed_odd,
        })
    return {"terminals": terminals, "scenarios": outcomes}


def signed_deletions(rows, parts, terminal, odd_holders):
    row_masks = list(map(bits, rows))
    names = {name for row in rows for name in row}
    focus = next(part for part in parts if terminal in part.holders)
    outcomes = {"inside_designated_component": {}, "outside_designated_component": {}}
    for removed in range(len(rows)):
        reduced = row_masks[:removed] + row_masks[removed + 1:]
        new_odd = [i - (removed < i) for i in odd_holders if i != removed]
        count = scalar_counts(reduced, len(names), new_odd)["words"]
        key = "inside_designated_component" if removed in focus.holders else "outside_designated_component"
        outcomes[key].setdefault(str(count), []).append(removed)
    return {
        "odd_holders": sorted(odd_holders),
        "complete_ordinary_words": scalar_counts(row_masks, len(names), odd_holders)["words"],
        "words_at_all_physical_names_after_removing_each_rule": outcomes,
    }


def inspect_draw(item, original_archive):
    draw_summary = {}
    for law in ("parity", "nae"):
        history = item["laws"][law]
        older_rows = item["source_rows"]
        before = components(older_rows)
        assert all(part.loose for part in before)
        closed = {}
        cut_results = []
        for cut in history["cuts"]:
            rows = cut["after_rows"]
            after = components(rows)
            assert [part.as_dict() for part in after] == cut["components"]
            positive = audit_births(older_rows, rows, cut["births"], law)
            assert positive == cut["positive_grants"]
            present_closed = {part.holders for part in after if not part.loose}
            assert closed.keys() <= present_closed
            archive_rows = {r["holder"]: r for r in cut["new_closing_components"]}
            closures = []
            for part in after:
                if part.loose or part.holders in closed:
                    continue
                assert law == "parity"
                parents = [p for p in before if set(p.holders) & set(part.holders)]
                assert len(parents) == 1 and parents[0].loose
                delta = set(part.holders) - set(parents[0].holders)
                assert len(delta) == 1
                (holder,) = delta
                archived = archive_rows.pop(holder)
                checked = audit_closed_part(
                    rows, older_rows, part, parents[0], archived if original_archive else None
                )
                assert checked["holder_ids"] == archived["component_holders"]
                assert list(part.names) == archived["component_names"]
                closed[part.holders] = checked
                closures.append(checked)
            assert not archive_rows and len(closures) == len(cut["births"]) - positive
            whole = len(closed) == len(after)
            assert whole == cut["whole_closed"]
            cut_result = {
                "age": cut["age"], "component_count": len(after),
                "already_closed": len(closed) - len(closures), "funded_births": len(cut["births"]),
                "positive_grants": positive, "whole_closed": whole, "closures": closures,
            }
            if law == "parity" and (item["panel"], item["draw"], cut["age"]) == ("T", 2, 1):
                birth = next(b for b in cut["births"] if 17 in b["new_names"])
                holder, name = birth["holder"], 17
                row_masks = list(map(bits, rows))
                name_count = sum(len(p.names) for p in after)
                assert {i for i, row in enumerate(rows) if name in row} == {holder}
                even = scalar_counts(row_masks, name_count)
                odd = scalar_counts(row_masks, name_count, {holder})
                assert even == odd
                cut_result["fresh_sign_control"] = {
                    "holder": holder, "support": sorted(rows[holder]), "flipped_fresh_name": name,
                    "whole_words_per_sign": even["words"],
                    "all_zero_witnesses_only_even": True, "singleton_one_witnesses_only_odd": True,
                }
            if closed:
                archive_union = cut.get("union_signs")
                if original_archive:
                    assert (archive_union is not None) == (item["panel"] == "M")
                cut_result["whole_signs"] = signed_union(rows, after, closed, archive_union)
                if item["panel"] == "M" and item["draw"] == 1 and len(closures) == 2:
                    first, second = cut_result["whole_signs"]["terminals"]
                    cut_result["rule_deletion_controls"] = [
                        signed_deletions(rows, after, first, odd_set)
                        for odd_set in ({first}, {first, second})
                    ]
                if item["panel"] == "S" and item["draw"] == 2 and closures:
                    (terminal,) = cut_result["whole_signs"]["terminals"]
                    name = min(rows[terminal])
                    changed = {holder for holder, row in enumerate(rows) if name in row}
                    assert len(changed) == 2 and terminal in changed
                    count = scalar_counts(list(map(bits, rows)), len(after[0].names), changed)
                    assert count["words"] == closures[0]["ordinary_even_words"]
                    cut_result["changed_older_sign_control"] = {
                        "odd_holders": sorted(changed), "whole_words": count["words"],
                        "one_supporting_word_has_ones_only_at": [name],
                    }
            cut_results.append(cut_result)
            older_rows, before = rows, after
        draw_summary[law] = cut_results
    return {"panel": item["panel"], "draw": item["draw"], "laws": draw_summary}


def summarize(records):
    groups = defaultdict(Counter)
    scenarios = Counter()
    double_sign_tables = Counter()
    rank_sizes = Counter()
    for draw in records:
        for law, cuts in draw["laws"].items():
            counts = groups[draw["panel"] + " " + law]
            counts["draws"] += 1
            for cut in cuts:
                n = len(cut["closures"])
                counts["funded_cuts"] += 1
                counts["funded_births"] += cut["funded_births"]
                counts["positive_grants"] += cut["positive_grants"]
                counts["newly_closed"] += n
                counts["double_closing_cuts"] += (n == 2)
                counts["whole_closing_cuts"] += cut["whole_closed"]
                for closed in cut["closures"]:
                    admits = closed["signed_permutation"] is not None
                    counts["single_odd_operator_positive"] += admits
                    counts["single_odd_operator_negative"] += not admits
                    counts["single_odd_ordinary_empty"] += not closed["ordinary_single_odd_words"]
                    counts["individual_old_sign_twists_tested"] += closed["each_additional_old_sign_flip_restores_even_count"]
                    counts["one_rule_deletions_tested"] += closed["each_single_rule_deleted_restores_even_count"]
                    rank_sizes[f"{len(closed['holder_ids'])} knots, {closed['name_count']} distinctions, odd operator {admits}"] += 1
                if "whole_signs" in cut:
                    admissions = []
                    for case in cut["whole_signs"]["scenarios"]:
                        counts["full_union_scenarios"] += 1
                        counts["full_union_operator_checks_positive"] += case["operator_admits"]
                        counts["full_union_ordinary_positive"] += bool(case["scalar"]["words"])
                        admissions.append(str(int(case["operator_admits"])))
                        if len(cut["whole_signs"]["terminals"]) == 2:
                            signs = "".join(map(str, case["signs"]))
                            position = "two new" if n == 2 else "one new" if n else "both older"
                            key = f"{position}, signs {signs}, ordinary {bool(case['scalar']['words'])}, operator {case['operator_admits']}"
                            scenarios[key] += 1
                    if n == 2:
                        double_sign_tables["".join(admissions)] += 1
    return {
        "draws": len(records), "panels_and_laws": dict(groups),
        "structural_sizes": dict(sorted(rank_sizes.items())),
        "double_cut_operator_outcomes_for_00_01_10_11": dict(sorted(double_sign_tables.items())),
        "whole_signs_with_two_closed_components": dict(sorted(scenarios.items())),
    }


def seeded_ids():
    rng = random.Random(SEED)
    result = set()
    for panel, size, k in zip(PANEL_NAMES, (256, 128, 128, 32), (32, 16, 16, 8), strict=True):
        result.update((panel, i) for i in rng.sample(range(1, size + 1), k))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("archive", "forward"), required=True)
    parser.add_argument("--selection", choices=("pilot", "seeded", "all"), required=True)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--details", type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    cap_bytes = 1_750_000 * 1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if soft == resource.RLIM_INFINITY or soft > cap_bytes:
        resource.setrlimit(resource.RLIMIT_AS, (cap_bytes, hard))
    source_is_archive = args.source == "archive"
    if source_is_archive:
        with gzip.open(HISTORY, "rt") as file:
            draws = json.load(file)
        assert all(
            sorted(d["draw"] for d in draws if d["panel"] == p) == list(range(1, n + 1))
            for p, n in zip(PANEL_NAMES, (256, 128, 128, 32), strict=True)
        )
    else:
        with (HERE / "growth_replay.json").open() as file:
            draws = json.load(file)["histories"]
    seeded = seeded_ids()
    pilot = {("T", 2), ("T", 57), ("T", 201), ("E", 8), ("M", 1), ("M", 11), ("S", 2)}
    filter_set = {"pilot": pilot, "seeded": seeded, "all": None}[args.selection]
    selected = [d for d in draws if filter_set is None or (d["panel"], d["draw"]) in filter_set]
    assert filter_set is None or len(selected) == len(filter_set)
    selected.sort(key=lambda d: (PANEL_NAMES.index(d["panel"]), d["draw"]))
    evidence = []
    for draw in selected:
        try:
            evidence.append(inspect_draw(draw, source_is_archive))
        except Exception as error:
            raise RuntimeError(f"{draw['panel']} draw {draw['draw']}") from error
    selected_seeded = [d for d in evidence if (d["panel"], d["draw"]) in seeded]
    result = {
        "source": args.source, "selection": args.selection, "seed": SEED,
        "summary": summarize(evidence), "seeded_summary": summarize(selected_seeded),
        "additional_named_draws": [(d["panel"], d["draw"]) for d in selected if (d["panel"], d["draw"]) not in seeded] if not source_is_archive else [],
        "elapsed_seconds_before_writing": round(time.perf_counter() - start, 5),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "address_space_limit_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
    }
    if args.summary:
        args.summary.write_text(json.dumps(result, indent=2) + "\n")
    if args.details:
        data = json.dumps(evidence, separators=(",", ":")).encode()
        args.details.write_bytes(gzip.compress(data, compresslevel=6, mtime=0))
    print(json.dumps({k: result[k] for k in (
        "source", "selection", "elapsed_seconds_before_writing", "peak_rss_kib",
    )} | {"draws": len(evidence)}))


if __name__ == "__main__":
    main()
