"""Replay the funded parity births and the registered order and contraction controls."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from math import prod
from pathlib import Path
from runpy import run_path


ROOT = Path(__file__).resolve().parents[3]
GROWN_TICKET = "GROWN-OPPOSITE-READS-20261125-001"
SERIAL_TICKET = "FRESH-DEMAND-20261120-001A"


def archives():
    previous = ROOT / "artifacts" / GROWN_TICKET / f"{GROWN_TICKET}-E001_grown_preparations"
    _, advance, record = run_path(str(previous / "check.py"))["archives"]()
    path = ROOT / "experiments" / SERIAL_TICKET / f"{SERIAL_TICKET}-E001_orders"
    serial = run_path(str(path / "serial_orders.py"))
    return advance, record, serial


def parity(word):
    return word.bit_count() % 2


def mask(names):
    return sum(1 << name for name in names)


def ownership(rows):
    owners = defaultdict(list)
    for i, row in enumerate(rows):
        for distinction in row:
            owners[distinction].append(i)
    assert all(len(holders) in (1, 2) for holders in owners.values())
    return owners


def echelon(words):
    pivots = {}
    for word in words:
        while word:
            top = word.bit_length() - 1
            if top not in pivots:
                pivots[top] = word
                break
            word ^= pivots[top]
    return pivots


def allowed_basis(rows):
    equations = tuple(map(mask, rows))
    pivots = echelon(equations)
    basis = []
    for free in sorted(set(ownership(rows)) - pivots.keys()):
        word = 1 << free
        for pivot in sorted(pivots):
            if parity(word & pivots[pivot]):
                word |= 1 << pivot
        assert all(not parity(word & row) for row in equations)
        basis.append(word)
    return basis


def exact_projection(basis, panel):
    def project(word):
        return sum(((word >> m) & 1) << i for i, m in enumerate(panel))

    projected = echelon(map(project, basis))
    support = [0]
    for word in projected.values():
        support += [value ^ word for value in support]
    counts = [0] * (1 << len(panel))
    for value in support:
        counts[value] = 1 << (len(basis) - len(projected))
    return {"panel": panel, "counts_little_endian": counts}


def extension_receipt(before, after):
    old_basis, new_basis = allowed_basis(before), allowed_basis(after)
    old_mask = mask(ownership(before))
    projected = echelon(word & old_mask for word in new_basis)
    assert len(projected) == len(old_basis)
    assert all(not parity(word & row) for word in projected.values()
               for row in map(mask, before))
    return {
        "old_state_count": 1 << len(old_basis),
        "new_state_count": 1 << len(new_basis),
        "full_old_words_retained": 1 << len(projected),
        "constant_extension_count": 1 << (len(new_basis) - len(projected)),
        "old_holder_rows_retained": set(map(frozenset, before)) <= set(map(frozenset, after)),
    }


def cycles(size, private):
    return tuple(tuple(sorted(((i - 1) % size, i,
                               *range(size + i * private, size + (i + 1) * private))))
                 for i in range(size))


def added_births(source, event, grown):
    owners = ownership(source)
    old_basis, new_basis = allowed_basis(source), allowed_basis(grown)
    births = []
    for new in event["new"]:
        row = tuple(new["places"])
        inherited = tuple(m for m in row if m in owners)
        fresh = tuple(m for m in row if m not in owners)
        assert len(fresh) == new["fresh"] and len(inherited) == new["parents"]
        assert all(len(owners[m]) == 1 for m in inherited)
        parents = sorted(owners[m][0] for m in inherited)
        assert parents == new["parent_names"] and len(set(parents)) == len(parents)
        distinct_meetings = []
        if len(parents) == 2:
            triple = [source[i] for i in parents] + [row]
            shared = [set(a) & set(b) for a, b in combinations(triple, 2)]
            if all(len(s) == 1 for s in shared) and len(set.union(*shared)) == 3:
                distinct_meetings = sorted(set.union(*shared))
        input_table = exact_projection(old_basis, inherited)["counts_little_endian"]
        child_table = exact_projection(new_basis, inherited + fresh)["counts_little_endian"]
        input_fibres = [sum(1 for y in range(1 << len(fresh))
                            if child_table[x | (y << len(inherited))])
                        for x in range(1 << len(inherited))]
        assert [bool(v) for v in input_fibres] == [bool(v) for v in input_table]
        assert set(input_fibres) <= {0, 1 << max(0, len(fresh) - 1)}
        assert all(bool(count) == (not parity(word)) for word, count in enumerate(child_table))
        births.append({
            "holder": new["holder"], "parents": parents, "inherited": inherited, "fresh": fresh,
            "arity": len(row), "lookahead_demand": new["demand"],
            "eligible_three_copy_incidence_at_newborn": distinct_meetings,
            "old_inherited_projection_counts": input_table,
            "child_joint_inherited_and_fresh_projection_counts": child_table,
            "number_of_legal_fresh_words_by_inherited_word": input_fibres,
        })
    return births


def reserved_order(source, births):
    rows = source
    old = ownership(source)
    openings = {m for m, holders in old.items() if len(holders) == 1}
    available = set(old)
    counts = []
    for birth in births:
        inherited, fresh = birth["inherited"], birth["fresh"]
        assert set(inherited) <= openings and not available.intersection(fresh)
        openings.difference_update(inherited)
        available.update(fresh)
        following = rows + (inherited + fresh,)
        counts.append(extension_receipt(rows, following)["constant_extension_count"])
        rows = following
    assert not openings
    return rows, counts


def exchange_loose_distinctions(source, selected=None):
    owners = ownership(source)
    changed = []
    for index, row in enumerate(source):
        loose = [m for m in row if len(owners[m]) == 1]
        if selected is not None and index not in selected:
            changed.append(row)
        else:
            swap = dict(zip(loose, reversed(loose)))
            changed.append(tuple(swap.get(m, m) for m in row))
    return tuple(changed)


def verify_alignment(source, baseline, alternate_source, alternate, first_rows, second_rows):
    original_owners, new_owners = ownership(source), ownership(alternate_source)
    labels = {frozenset(row): i for i, row in enumerate(source)}
    parent_names = {i: labels[frozenset(row)] for i, row in enumerate(alternate_source)}

    def batches(births, parent_of):
        groups = defaultdict(list)
        for birth in births:
            names = tuple(sorted(parent_of.get(i, i) for i in birth["parents"]))
            groups[names, len(birth["fresh"]), birth["lookahead_demand"]].append(birth)
        return groups

    first, second = batches(baseline, {}), batches(alternate, parent_names)
    assert first.keys() == second.keys()
    renaming = {m: m for m, holders in new_owners.items() if len(holders) == 2}
    for key, births in first.items():
        left = sorted(births, key=lambda birth: birth["inherited"])
        right = sorted(second[key], key=lambda birth: birth["inherited"])
        for a, b in zip(left, right, strict=True):
            old_by_parent = {original_owners[m][0]: m for m in a["inherited"]}
            for m in b["inherited"]:
                renaming[m] = old_by_parent[parent_names[new_owners[m][0]]]
            renaming.update(zip(b["fresh"], a["fresh"], strict=True))
            assert sorted(a["number_of_legal_fresh_words_by_inherited_word"]) == sorted(
                b["number_of_legal_fresh_words_by_inherited_word"]
            )
    assert len(renaming) == len(set(renaming.values())) == len(ownership(first_rows))
    assert {frozenset(renaming[m] for m in row) for row in second_rows} == {
        frozenset(row) for row in first_rows
    }
    return {m: renamed for m, renamed in renaming.items() if m != renamed}


def ordinary_case(source, advance):
    event, grown = advance(source, "parity")
    grown = tuple(map(tuple, grown))
    assert tuple(map(set, grown[:len(source)])) == tuple(map(set, source))
    births = added_births(source, event, grown)
    variation = {}
    for name, original in (
        ("initial_presentation", source),
        ("reversed_holders", tuple(reversed(source))),
        ("exchanged_equivalent_loose_distinctions", exchange_loose_distinctions(source)),
    ):
        if original == source and name != "initial_presentation":
            continue
        if name == "initial_presentation":
            compared, rows = births, grown
        else:
            output, following = advance(original, "parity")
            assert output["status"] == event["status"]
            rows = tuple(map(tuple, following))
            compared = added_births(original, output, rows)
            assert extension_receipt(original, rows) == extension_receipt(source, grown)
        forward, fw = reserved_order(original, compared)
        backwards, bw = reserved_order(original, reversed(compared))
        assert set(map(frozenset, forward)) == set(map(frozenset, backwards)) == set(
            map(frozenset, rows)
        )
        variation[name] = {
            "ordered_reserved_payments": [birth["inherited"] for birth in compared],
            "forward_extension_counts_by_write": fw,
            "reverse_extension_counts_by_write": bw,
            "nonidentity_distinction_correspondence_back_to_baseline": verify_alignment(
                source, births, original, compared, grown, rows
            ),
        }
    return {
        "source_holdings": source, "grown_holdings": grown, "status": event["status"],
        "births": births, "arity_histogram": Counter(b["arity"] for b in births),
        "join_count": sum(len(b["parents"]) >= 2 for b in births),
        "exact_two_parent_join_count": sum(len(b["parents"]) == 2 for b in births),
        "full_transition": extension_receipt(source, grown),
        "reserved_order_and_representation_cross": variation,
    }


def signed(copies, word, law):
    coefficients = []
    for local in copies:
        weight = sum((word >> distinction) & 1 for distinction in local)
        coefficients.append(0 if weight % 2 else (-1 if weight and law == "T-" else 1))
    return prod(coefficients)


def exterior_contraction(rows, extra_ordinary_rows=()):
    owners = ownership(rows)
    assert {m for row in extra_ordinary_rows for m in row} <= owners.keys()
    outside = tuple(sorted(m for m, holders in owners.items() if len(holders) == 1))
    inside = tuple(sorted(owners.keys() - set(outside)))
    table = []
    for physical in range(1 << len(outside)):
        output = sum(1 << distinction for i, distinction in enumerate(outside) if physical & (1 << i))
        positive, phased, fillings = 0, 0, []
        for bits in range(1 << len(inside)):
            hidden = sum(1 << distinction for i, distinction in enumerate(inside) if bits & (1 << i))
            word = output | hidden
            if any(parity(word & mask(row)) for row in extra_ordinary_rows):
                continue
            if signed(rows, word, "T+"):
                fillings.append(bits)
                positive += 1
                phased += signed(rows, word, "T-")
        table.append({"positive_completion_count": positive, "T_minus_sum": phased,
                      "distinct_ordinary_internal_fillings_little_endian": fillings})
    return outside, inside, table


def contraction_controls(ternary, doubled_pair):
    pre, post = ternary["source_holdings"], ternary["grown_holdings"]
    outside, inside, table = exterior_contraction(pre)
    before = exact_projection(allowed_basis(pre), outside)["counts_little_endian"]
    after = exact_projection(allowed_basis(post), outside)["counts_little_endian"]
    assert before == after == [row["positive_completion_count"] for row in table]
    assert [row["T_minus_sum"] for row in table] == [0] * 8
    assert tuple(ternary["births"][0]["inherited"]) == outside
    assert not ternary["births"][0]["fresh"] and ternary["status"] == "closed"
    assert all(not parity(word) for word, count in enumerate(after) if count)
    _, _, after_table = exterior_contraction(pre, post[len(pre):])
    assert after_table == table
    four_outside, four_inside, four = exterior_contraction(cycles(4, 1))
    assert sum(row["T_minus_sum"] != 0 for row in four) == 8
    pair_outside, pair_inside, pair = exterior_contraction(doubled_pair["source_holdings"])
    assert [row["T_minus_sum"] for row in pair] == [2, 0, 0, 2]
    assert [row["positive_completion_count"] for row in pair] == [2, 0, 0, 2]
    return {
        "exact_three_copy": {
            "exterior": outside, "retained_internal": inside, "exterior_table": table,
            "same_signed_table_after_ordinary_birth": after_table,
            "ordinary_before_exterior_counts": before, "ordinary_after_exterior_counts": after,
        },
        "offline_four_copy": {"exterior": four_outside, "internal": four_inside, "table": four},
        "offline_doubled_pair": {"exterior": pair_outside, "internal": pair_inside, "table": pair},
    }


def four_place_exterior(case):
    source, grown = case["source_holdings"], case["grown_holdings"]
    owners = ownership(source)
    pairs = [tuple(m for m in row if len(owners[m]) == 1) for row in source]
    exterior = tuple(m for pair in pairs for m in pair)
    old = exact_projection(allowed_basis(source), exterior)
    new = exact_projection(allowed_basis(grown), exterior)
    join, = [birth for birth in case["births"] if len(birth["parents"]) == 3]
    assert set(join["inherited"]) < set(exterior) and len(exterior) == 6
    paid_positions = [exterior.index(distinction) for distinction in join["inherited"]]
    xor_counts = [0] * 8
    paid_and_xor_counts = [[0] * 8 for _ in range(8)]
    for word, count in enumerate(old["counts_little_endian"]):
        projected = sum(parity((word >> (2 * i)) & 3) << i for i in range(3))
        paid = sum(((word >> position) & 1) << i for i, position in enumerate(paid_positions))
        xor_counts[projected] += count
        paid_and_xor_counts[paid][projected] += count
    assert xor_counts == [16 if not parity(w) else 0 for w in range(8)]
    assert all(row == [2 if not parity(w) else 0 for w in range(8)]
               for row in paid_and_xor_counts)
    return {"physical_exterior_before": old, "physical_exterior_after": new,
            "private_pair_xor_counts_before": xor_counts,
            "count_by_paid_word_then_private_pair_xor_word": paid_and_xor_counts,
            "actual_three_parent_join": join}


def unary_signed_lift(single):
    source = single["source_holdings"]
    grown = single["grown_holdings"]
    width = len(ownership(grown))
    old_mask = mask(ownership(source))
    extension_counts = Counter()
    retained_signs = {"T+": Counter(), "T-": Counter()}
    for full in range(1 << width):
        if any(parity(full & mask(row)) for row in grown):
            continue
        old = full & old_mask
        extension_counts[old] += 1
        for law, counts in retained_signs.items():
            counts[old] += signed(source, old, law)
    assert extension_counts == {0: 8, 3: 8, 5: 8, 6: 8}
    assert retained_signs["T+"] == extension_counts
    assert retained_signs["T-"] == {0: 8, 3: -8, 5: -8, 6: -8}
    return {"extensions_by_old_word_mask": extension_counts,
            "sum_of_supplied_old_decoration_over_lifts": retained_signs}


def serial_history(source, schedule, archive):
    stage = archive.S.from_junctions(source)
    children = defaultdict(set)
    rows = source
    events = []
    for parents in schedule:
        joins, unary, live = archive.moves(stage, children)
        assert parents in joins + unary
        openings = {m for holder in live for m in stage.loose(holder)}
        spent = tuple(stage.loose(parent)[0] for parent in parents)
        implied = set(spent) == openings
        assert implied == (len(echelon(map(mask, rows))) ==
                           len(echelon([*map(mask, rows), mask(spent)])))
        child = archive.new_junction(stage, spent)
        for parent in parents:
            children[parent].add(child)
        provisional = [i for i in range(len(stage.bits_of)) if stage.loose(i) or i == child]
        groups = [tuple(sorted(group)) for group in stage.groups_among(provisional) if child in group]
        amount = 0 if implied and not groups else max(len(groups), 3 - len(spent), 1)
        fresh = tuple(range(stage.nbits, stage.nbits + amount))
        for distinction in fresh:
            stage.bits_of[child].append(distinction)
            stage.owner[distinction] = [child]
        stage.nbits += amount
        stage.fresh[child] = amount
        following = rows + (spent + fresh,)
        events.append({"eligible_joins": joins, "eligible_unary": unary, "parents": parents,
                       "consumed": spent, "fresh": fresh, "demand_groups": groups,
                       "transition": extension_receipt(rows, following)})
        rows = following
    return rows, events


def serial_controls(independent, serial):
    processed = {}
    archive = serial["archived"]
    for label, order in (("left_first", ((0,), (3,))), ("right_first", ((3,), (0,)))):
        end, events = serial_history(independent["source_holdings"], order, archive)
        births_by_payment = {event["consumed"][0]: event["fresh"] for event in events}
        raw_after = independent["grown_holdings"]
        reference_by_payment = {birth["inherited"][0]: birth["fresh"]
                                for birth in independent["births"]}
        names = {m: m for m in ownership(independent["source_holdings"])}
        for payment, fresh in births_by_payment.items():
            names.update(zip(fresh, reference_by_payment[payment], strict=True))
        assert {frozenset(names[m] for m in row) for row in end} == set(map(frozenset, raw_after))
        processed[label] = events

    spent = serial["source"](9, 2, False)
    target = serial["TARGET"]
    early = (target,)
    delayed = tuple((parent,) for parent in target) + early
    later_with_exchanged_payments = exchange_loose_distinctions(spent, set(target))
    variants = {}
    for label, fixture, schedule in (
        ("pair_first", spent, early),
        ("unaries_then_pair", spent, delayed),
        ("unaries_then_same_literal_pair_payments", later_with_exchanged_payments, delayed),
    ):
        _, events = serial_history(fixture, schedule, archive)
        current = fixture
        for parents, event in zip(schedule, events):
            assert parents in serial["all_choices"](current, False)
            current, archived = serial["apply_move"](current, parents, "parity")
            assert archived["consumed"] == event["consumed"]
            assert archived["fresh_count"] == len(event["fresh"])
        variants[label] = events
    immediate, later = variants["pair_first"][-1], variants["unaries_then_same_literal_pair_payments"][-1]
    assert immediate["consumed"] == later["consumed"]
    assert (len(immediate["fresh"]), len(later["fresh"])) == (1, 2)
    return {"independent_unary_orders": processed, "archived_spent_witness_orders": variants}


def determinant_controls():
    def det(u, v, phased):
        matrix = ((u, -v if phased else v), (-v if phased else v, -u if phased else u))
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    rows = {}
    for u, v in ((1, 0), (1, 1), (1, -1)):
        a, b = det(u, v, False), det(u, v, True)
        assert (a, b) == (u*u - v*v, -u*u - v*v)
        rows[f"{u},{v}"] = [a, b]
    return rows


def results():
    advance, archive, serial = archives()
    names = {f"four_place_cycle_{n}": cycles(n, 2) for n in (3, 5, 7)}
    names.update({
        "exact_three_ternary_cycle": ((0, 2, 3), (0, 1, 4), (1, 2, 5)),
        "single_ternary": ((0, 1, 2),),
        "doubled_pair": ((0, 1, 2), (0, 1, 3)),
        "independent_two_end": ((0, 1, 5), (0, 1, 2), (2, 3, 4), (3, 4, 6)),
    })
    cases = {name: ordinary_case(source, advance) for name, source in names.items()}
    five = cases["four_place_cycle_5"]
    assert list(map(list, five["source_holdings"])) == archive["stages"]["0"]["stars"]
    assert list(map(list, five["grown_holdings"])) == archive["stages"]["1"]["stars"]
    ternary = cases["exact_three_ternary_cycle"]
    closed, no_growth = advance(ternary["grown_holdings"], "parity")
    assert closed["status"] == "already closed" and no_growth is None
    stalled, no_growth = advance(cycles(5, 1), "parity")
    assert stalled["status"] == "stall" and no_growth is None
    return {
        "production_cases": cases,
        "five_knot_archive_fixture": "R0",
        "four_place_three_cycle_exterior": four_place_exterior(cases["four_place_cycle_3"]),
        "signed_contraction_controls": contraction_controls(ternary, cases["doubled_pair"]),
        "determinant_controls_T_plus_then_T_minus": determinant_controls(),
        "unary_counterexample": cases["single_ternary"]["births"][0],
        "unary_preservation_of_both_supplied_decorations": unary_signed_lift(cases["single_ternary"]),
        "two_parent_counterexample": five["births"][0],
        "serial_controls": serial_controls(cases["independent_two_end"], serial),
        "no_event_controls": {"closed_ternary_cycle": closed, "underfunded_five_cycle": stalled},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the saved exact receipt")
    args = parser.parse_args()
    content = json.dumps(results(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if Path(__file__).with_name("results.json").read_text(encoding="utf-8") != content:
            raise SystemExit("results.json differs from the replay")
        print("results.json matches the exact replay")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
