"""Replay three boundary reductions and grade their related scalar tables."""

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from random import Random
import json
import sys


PROOFS = Path(__file__).resolve().parents[2]
I = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001I"
     / "VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction" / "fixtures.py")
SPEC = spec_from_file_location("seven_to_six_predecessor", I)
prior = module_from_spec(SPEC)
SPEC.loader.exec_module(prior)
literal, exact = prior.literal, prior.isometries
bits, mask = literal.bits, literal.mask


SEED = (("0", (0, 1, 2)),)
PLANS = (
    ("nine_sites", ((0,), (0,), (1, 2), (0, 3), (1, 2), (1, 4), (2, 4), (5, 6, 7)),
     (3, 3, 2, 2, 2, 2, 2, 2)),
    ("three_repeated_pairs", ((0,), (0,), (1, 2), (1, 2), (1, 2), (3, 4), (4, 5), (3, 5), (6, 7, 8)),
     (3, 3, 2, 2, 2, 2, 2, 2, 2)),
    ("two_caps_and_bridge", ((0,), (0,), (0,), (1, 2), (1, 3), (2, 3), (2, 3),
                            (4, 5, 6), (4, 5, 7), (8, 9), (6, 7, 10)),
     (3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2)),
)
CONNECTED = (((3, 5), (8, 9), (6, 10), (10,), (9, 11), (9, 12), (11, 12)), (3, 2, 3, 3, 2, 2, 2))


def attach(history, parents, h):
    users, ordinary = literal.incidence(history)
    parents = tuple(map(str, parents))
    assert literal.legal(parents, ordinary)
    operands = tuple(min(bit for bit, holders in users.items() if holders == [site]) for site in parents)
    return named_step(history, operands, h, len(users))


def named_step(history, operands, h, width):
    return (*history, (str(len(history)), (*operands, *range(width, width + h))))


def grow(history, groups, counts):
    for group, count in zip(groups, counts, strict=True):
        history = attach(history, group, count)
    return history


def replay(history):
    events = literal.replay(history)
    seen = ()
    rows = []
    for site, support in history:
        current = events[site]
        _, neighbors = literal.incidence(seen)
        parents = current["parents"]
        witnesses = [sorted(neighbors[a] & neighbors[b]) for a, b in combinations(parents, 2)]
        universal = sorted(set.intersection(*(neighbors[i] for i in parents))) if len(parents) == 3 else []
        assert all(witnesses) and not universal
        seen = (*seen, (site, support))
        owners, _ = literal.incidence(seen)
        loose = sorted(bit for bit, holders in owners.items() if len(holders) == 1)
        rows.append({"site": site, **current, "earlier_pair_witnesses": witnesses,
                     "common_neighbor_of_three": universal, "frontier": loose})
    return rows


def measure(history, independent=False):
    holders, adjacent = literal.incidence(history)
    width = len(holders)
    assert set(holders) == set(range(width))
    assert sum(len(row) == 3 for _, row in history) == 1
    assert all(len(row) >= 3 for _, row in history)
    bonds = literal.wired_bonds(history, holders)
    table = {}
    for support in sorted(bonds, key=lambda support: (support.bit_count(), support)):
        for pair in combinations(bits(support), 2):
            table.setdefault(pair, support.bit_count())
        if len(table) == width * (width - 1) // 2:
            break
    assert len(table) == width * (width - 1) // 2
    if independent:
        dual = prior.span(mask(row) for _, row in history)
        linear_table, _ = prior.pair_minima(dual, tuple(combinations(range(width), 2)))
        assert linear_table == table
    return table, bonds, frozenset(literal.direct_triples(holders, adjacent))


def certificate(table, history):
    width = max(max(pair) for pair in table) + 1
    visible = {pair: value if value <= 6 else None for pair, value in table.items()}
    known, residual, allowed, rounds = prior.force_from_table(visible, width, 6)
    physical = prior.span(mask(row) for _, row in history)
    if residual:
        matches, full, audit = prior.all_compatible_spaces(table, width, known, residual, allowed)
        assert known <= physical and physical in matches and physical in full
    else:
        assert known == physical
        matches = full = [physical]
        audit = {"rank_ceiling": 1 + (width - 3) // 2, "initial_unforced_cosets": 0,
                 "spaces_tested_by_rank": {len(history): 1}}
    return {"forced_rank_from_K6": prior.rank(known), "unresolved_short_bonds": len(residual),
            "spaces_matching_K6": len(matches), "spaces_matching_full_table": len(full),
            "force_rounds": [(result["rank_before"], result["viable_bonds"], len(result["forces"]))
                             for result in rounds], **audit}


def matrix(table, cutoff=None):
    width = max(max(pair) for pair in table) + 1
    return tuple(tuple(0 if a == b else truncated(table[tuple(sorted((a, b)))], cutoff)
                       for b in range(width)) for a in range(width))


def truncated(value, cutoff):
    return value if cutoff is None else min(value, cutoff + 1)


def lift_group(matrix_rows, menu):
    q = exact.Quotient.make(matrix_rows)
    order, _, generators = q.automorphisms()
    defects = []
    for image in generators:
        assert exact.disagreement(matrix_rows, matrix_rows, image) is None
        illegal = next((triple for triple in sorted(menu) if tuple(sorted(image[i] for i in triple)) not in menu), None)
        if illegal is not None and not defects:
            defects.append({"legal": illegal, "forbidden": tuple(sorted(image[i] for i in illegal)), "permutation": image})
    return q, {"order": order, "generators_graded": len(generators), "opposing": defects}


def reconstructions(history, bonds, required):
    pool = sorted(word for word in bonds if word.bit_count() <= 6)
    seed, = (word for word in pool if word.bit_count() == 3)
    pool = [word for word in pool if word == seed or (word & seed).bit_count() <= 1]
    first = frozenset((seed,))
    queue = [first]
    recorded = {first: (seed,)}
    complete = []
    marked_partial = []
    for state in queue:
        if required in state:
            marked_partial.append(recorded[state])
        if len(state) == len(history):
            complete.append(state)
            continue
        partial = tuple((str(word), bits(word)) for word in sorted(state))
        holders, adjacent = literal.incidence(partial)
        for word in pool:
            if word in state:
                continue
            old = tuple(bit for bit in bits(word) if bit in holders)
            if word.bit_count() - len(old) not in (2, 3) or any(len(holders[bit]) != 1 for bit in old):
                continue
            if not literal.legal(tuple(holders[bit][0] for bit in old), adjacent):
                continue
            launched = state | {word}
            if launched not in recorded:
                queue.append(launched)
                recorded[launched] = (*recorded[state], word)
    original = frozenset(mask(row) for _, row in history)
    assert original in complete
    return {"possible_stars_after_seed_filter": len(pool), "reachable_prefix_sets": len(queue),
            "complete_support_sets": [[bits(word) for word in sorted(state)] for state in complete],
            "complete_sets_with_boundary_as_star": sum(required in state for state in complete),
            "prefix_histories_with_boundary_as_star": [[bits(word) for word in row] for row in marked_partial]}


def measured_record(history, table, bonds, menu, full_certificate=None):
    width = max(max(pair) for pair in table) + 1
    _, automorphisms = lift_group(matrix(table), menu)
    return {"width": width, "sites": len(history), "history": replay(history), "bond_count": len(bonds),
            "exact_legal_triples": sorted(menu), "K_histogram": dict(sorted(Counter(table.values()).items())),
            "K_upper_triangle": [table[pair] for pair in combinations(range(width), 2)],
            "full_table_automorphisms": automorphisms,
            "table_only_certificate": full_certificate if full_certificate else certificate(table, history)}


def relabel_control(history, table, menu):
    width = max(max(pair) for pair in table) + 1
    image = list(range(width))
    Random(917 + width).shuffle(image)

    def mapped(group):
        return tuple(sorted(image[bit] for bit in group))

    renamed = tuple((site, mapped(row)) for site, row in history)
    literal.replay(renamed)
    other, _, other_menu = measure(renamed)
    assert all(other[mapped(pair)] == value for pair, value in table.items())
    assert other_menu == {mapped(group) for group in menu}
    return {"permutation": image, "all_pair_entries_checked": len(other), "triple_menu_preserved": True}


def rival_competitors(prefix):
    """Compare all literal two-output binary and triple choices at the event prefix."""
    holders, adjacent = literal.incidence(prefix)
    width = len(holders)
    loose = sorted(bit for bit, users in holders.items() if len(users) == 1)
    candidates = []
    by_p = Counter()
    forced_ranks = Counter()
    for p in (2, 3):
        for group in combinations(loose, p):
            if not literal.legal(tuple(holders[bit][0] for bit in group), adjacent):
                continue
            grown = named_step(prefix, group, 2, width)
            literal.replay(grown)
            table, _, menu = measure(grown)
            cert = certificate(table, grown)
            mat = matrix(table)
            quotient, autos = lift_group(mat, menu)
            by_p[p] += 1
            forced_ranks[cert["forced_rank_from_K6"], cert["spaces_matching_full_table"]] += 1
            candidates.append((group, table, menu, mat, quotient, autos))

    tally = Counter(pairs=0, identical_named_full_tables=0, different_named_menus=0,
                    exact_full_isometries_between_distinct_choices=0, opposing_pairs=0)
    first = differing = None
    for a, b in combinations(candidates, 2):
        og, table, menu, mat, qa, _ = a
        qg, table2, menu2, mat2, qb, autos = b
        tally["pairs"] += 1
        tally["identical_named_full_tables"] += table == table2
        tally["different_named_menus"] += menu != menu2
        initial = next(exact.isometries(qa.colored, qb.colored), None)
        if initial is None:
            continue
        image = qa.lift(qb, initial)
        assert exact.disagreement(mat, mat2, image) is None
        tally["exact_full_isometries_between_distinct_choices"] += 1
        transported = {tuple(sorted(image[i] for i in mark)) for mark in menu}
        if transported != menu2:
            tally["opposing_pairs"] += 1
            if first is None:
                first = {"operands": (og, qg), "permutation": image,
                         "transported_menus": (sorted(transported), sorted(menu2))}
        elif autos["opposing"]:
            tally["opposing_pairs"] += 1
            if first is None:
                first = {"operands": (og, qg), "isometry": image, "target_self_opposition": autos["opposing"]}
        elif len(og) == len(qg) == 2 and menu != menu2 and differing is None:
            differing = {"operands": (og, qg), "permutation": image,
                         "named_menus": (sorted(menu), sorted(menu2))}
    return {"choices_by_parent_count": dict(by_p), "counts_by_forced_rank_and_full_spaces": [
                (rank, spaces, count) for (rank, spaces), count in sorted(forced_ranks.items())],
            "self_conflicts": [{"operands": row[0], **row[-1]} for row in candidates if row[-1]["opposing"]],
            **dict(tally), "first_full_opposition": first,
            "first_isometric_binary_pair_with_different_named_menu": differing}


def one_isometry(left, right, cutoff=None):
    original, rival = matrix(left, cutoff), matrix(right, cutoff)
    qa, qb = exact.Quotient.make(original), exact.Quotient.make(rival)
    possible = next(exact.isometries(qa.colored, qb.colored), None)
    mapped = None if possible is None else qa.lift(qb, possible)
    if mapped is not None:
        assert exact.disagreement(original, rival, mapped) is None
    return mapped


def difference(left, right):
    changed = [(pair, left[pair], right[pair]) for pair in left if left[pair] != right[pair]]
    changed.sort(key=lambda entry: (min(entry[1:]), entry[0]))
    mapped = one_isometry(left, right)
    return {"changed_named_pairs": len(changed),
            "first_named_cutoff_difference": min(changed[0][1:]) if changed else None,
            "isometry_through_cutoff": {k: one_isometry(left, right, k) for k in (3, 4, 5, 6)},
            "full_isometry_exists": mapped is not None, "one_full_isometry": mapped, "first_differences": changed[:8]}


def event(name, history):
    prefix = history[:-1]
    trace = replay(history)
    before_front, after_front = trace[-2]["frontier"], trace[-1]["frontier"]
    assert len(before_front) == 7 and len(after_front) == 6
    assert min(len(row["frontier"]) for row in trace[2:-1]) >= 7
    old_table, old_bonds, old_menu = measure(prefix, True)
    new_table, new_bonds, new_menu = measure(history, True)
    assert tuple(sorted(trace[-1]["operands"])) in old_menu
    support = mask(after_front)
    parity = 0
    for _, row in history:
        parity ^= mask(row)
    assert parity == support and support in new_bonds
    law = certificate(new_table, history)
    reconstruction = reconstructions(history, new_bonds, support) if law["spaces_matching_full_table"] == 1 else None
    comparison = None
    if reconstruction and reconstruction["prefix_histories_with_boundary_as_star"]:
        states = reconstruction["prefix_histories_with_boundary_as_star"]
        actual = tuple((str(i), row) for i, row in enumerate(states[0]))
        alternate, bonds, menu = measure(actual, True)
        if len(alternate) == len(new_table):
            comparison = {"actual_six_site": measured_record(actual, alternate, bonds, menu),
                          "pairs_within_six_support": [(pair, new_table[pair], alternate[pair])
                                                       for pair in combinations(after_front, 2)],
                          "whole_table_comparison": difference(new_table, alternate)}
    print(f"{name}: width {len(literal.incidence(history)[0])}, menus {len(old_menu)}->{len(new_menu)}", file=sys.stderr, flush=True)
    return {"fixture": name, "before": measured_record(prefix, old_table, old_bonds, old_menu),
            "after": measured_record(history, new_table, new_bonds, new_menu, law),
            "six_distinction_bond": after_front, "same_code_physical_reconstructions": reconstruction,
            "actual_boundary_as_six_site_comparator": comparison,
            "renaming_control": relabel_control(history, new_table, new_menu),
            "competing_binary_and_triple_caps": rival_competitors(prefix)}


def retained_component(history, start):
    _, adjacency = literal.incidence(history)

    def reach(site, forbidden):
        queue = [site]
        seen = {site}
        for old in queue:
            for nxt in adjacency[old] - seen:
                if frozenset((old, nxt)) not in forbidden:
                    seen.add(nxt)
                    queue.append(nxt)
        return seen

    bridges = {frozenset((a, b)) for a in adjacency for b in adjacency[a] if a < b
               and b not in reach(a, {frozenset((a, b))})}
    return reach(start, bridges)


def connected_extension(core):
    history = grow(core, *CONNECTED)
    table, bonds, menu = measure(history)
    mark = (32, 34, 36)
    assert mark in menu
    original_boundary = mask(replay(core)[-1]["frontier"])
    assert original_boundary in bonds
    component = retained_component(history, "8")
    holders, _ = literal.incidence(history)
    assert all(set(holders[bit]) <= component for bit in mark)
    print("connected continuation: proper six-bond and nonempty menu at width 38", file=sys.stderr, flush=True)
    compare = []
    for parents in ((13, 14), (11, 12)):
        successor = attach(history, parents, 2)
        other_table, other_bonds, other_menu = measure(successor)
        compare.append((parents, successor, other_table, other_bonds, other_menu))
    assert len(compare[0][-1]) != len(compare[1][-1])
    result = {"physical": measured_record(history, table, bonds, menu), "legal_mark": mark,
              "proper_six_distinction_bond": bits(original_boundary), "original_shore_sites": len(core),
              "old_cap_and_mark_holders_in_retained_component": sorted(component, key=int),
              "renaming_control": relabel_control(history, table, menu),
              "two_binary_successors": [{"parent_sites": parents, **measured_record(h, tab, bs, perms)}
                                       for parents, h, tab, bs, perms in compare],
              "binary_successor_table_comparison": difference(compare[0][2], compare[1][2])}
    result["clipped_self_checks"] = {k: lift_group(matrix(table, k), menu)[1] for k in (4, 5, 6)}
    return result


def main():
    histories = [(name, grow(SEED, groups, widths)) for name, groups, widths in PLANS]
    results = [event(name, history) for name, history in histories]
    live = connected_extension(histories[0][1])
    print(json.dumps({"events": results, "connected_live_extension": live}, indent=2))


if __name__ == "__main__":
    main()
