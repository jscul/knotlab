"""Classify exact lower-arity readings of the archived six-junction witness."""

from collections import Counter, defaultdict
from functools import cache
from itertools import combinations
from math import factorial, prod
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
ARCHIVED_CASE = Path("GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached")
sys.path.insert(0, str(ROOT / "experiments" / ARCHIVED_CASE))
from verify import exact_table, find_matching, lineage, mismatches, pair_key, reading, round_domains  # noqa: E402


def bond_readings(arrangement):
    """Take all nonempty support-minimal XORs of the given parity rows."""
    span = {0}
    for row in arrangement.masks:
        span |= {word ^ row for word in span}
    tables = [{args: None for args in combinations(arrangement.labels, arity)} for arity in (1, 2, 3)]
    bonds = []
    for word in sorted(span - {0}, key=int.bit_count):
        if any(bond & word == bond for bond in bonds):
            continue
        bonds.append(word)
        support = [x for x in arrangement.labels if word & arrangement.label_bits[x]]
        for arity, table in enumerate(tables, 1):
            for args in combinations(support, arity):
                if table[args] is None:
                    table[args] = len(support) - 1
    return tables, bonds, span


def all_mappings(labels, table, fixed):
    """List all full pair-table automorphisms fixing the specified labels."""
    signatures = {x: (Counter(table[pair_key(x, y)] for y in labels if x != y),
                      tuple(table[pair_key(x, y)] for y in sorted(fixed)))
                  for x in labels if x not in fixed}
    domains = {x: {y for y in signatures if signatures[x] == signatures[y]} for x in signatures}
    permuted = {x: x for x in fixed}
    unused = set(signatures)

    def search():
        if not unused:
            yield dict(permuted)
            return
        options = {}
        for x in domains.keys() - permuted.keys():
            options[x] = [y for y in sorted(domains[x] & unused) if all(
                table[pair_key(x, u)] == table[pair_key(y, v)] for u, v in permuted.items())]
        x = min(options, key=lambda item: (len(options[item]), item))
        for y in options[x]:
            permuted[x] = y
            unused.remove(y)
            yield from search()
            unused.add(y)
            del permuted[x]

    yield from search()


def extension_checks(a, successor, records, table, phi):
    fixed = {x: y for x, y in phi.items() if x not in a.loose}
    if mismatches(table, table, fixed):
        return False, False, False
    fresh = set(successor.labels) - set(a.labels)
    strict = {x: {phi[x]} if x in phi else fresh for x in successor.labels}
    exact = find_matching(table, table, strict, phi) is not None
    loose_of = defaultdict(set)
    for x, j in a.loose.items():
        loose_of[j].add(x)
    repair = {x: loose_of[a.loose[x]] if x in a.loose else strict[x] for x in successor.labels}
    repaired = exact or find_matching(table, table, repair, fixed) is not None
    by_round, membership = round_domains(records, records, {j: j for j in a.live}, repair)
    round_match = repaired and find_matching(table, table, by_round, fixed, *membership) is not None
    return exact, repaired, round_match


def minimum_cover(entries, failures):
    """Find the fewest individual triple queries that cover every failure."""
    by_mask = {}
    for triple, mask in entries.items():
        mask &= failures
        if mask:
            by_mask.setdefault(mask, triple)
    masks = [m for m in by_mask if not any(m != n and m & n == m for n in by_mask)]
    choices = {1 << i: [m for m in masks if m & (1 << i)]
               for i in range(failures.bit_length()) if failures & (1 << i)}
    if any(not options for options in choices.values()):
        return None

    @cache
    def cover(todo):
        if not todo:
            return ()
        bit = min((bit for bit in choices if todo & bit), key=lambda bit: len(choices[bit]))
        return min((tuple(sorted((by_mask[m], *cover(todo & ~m)))) for m in choices[bit]),
                   key=lambda solution: (len(solution), solution))

    return cover(failures)


def union(masks):
    combined = 0
    for mask in masks:
        combined |= mask
    return combined


def query_summary(table, maps, good, bad, fixed_probes, target_index):
    rejects = {}
    for args, value in table.items():
        rejects[args] = sum(1 << i for i, phi in enumerate(maps)
                            if table[tuple(sorted(phi[x] for x in args))] != value)
    by_probe = {z: union(mask for args, mask in rejects.items() if z in args) for z in fixed_probes}
    all_rejected = union(rejects.values())
    published_triple = (0, 1, 15)

    def counts(mask):
        return {"failures_detected": (mask & bad).bit_count(), "extenders_rejected": (mask & good).bit_count()}

    def exact(mask):
        return mask == bad

    def cover_summary(allowed):
        queries = minimum_cover(allowed, bad)
        return None if queries is None else {"count": len(queries), "example": queries}

    best = (max((mask & bad).bit_count() for mask in rejects.values()),
            min((mask & good).bit_count() for mask in rejects.values() if mask & bad == bad)
            if any(mask & bad == bad for mask in rejects.values()) else None)
    return {"all_triples": counts(all_rejected),
            "published_triple": {**counts(rejects[published_triple]),
                                 "detects_published_swap": bool(rejects[published_triple] & (1 << target_index))},
            "max_failures_detected_by_one_triple": best[0],
            "fewest_extenders_rejected_by_a_complete_single_triple": best[1],
            "single_triples_detecting_every_failure": [q for q, mask in rejects.items() if mask & bad == bad],
            "single_triples_exactly_classifying": [q for q, mask in rejects.items() if exact(mask)],
            "one_fixed_probe_with_all_pair_completions": {z: counts(mask) for z, mask in by_probe.items()},
            "fixed_probes_exactly_classifying": [z for z, mask in by_probe.items() if exact(mask)],
            "fewest_detection_queries": cover_summary(rejects),
            "fewest_exact_queries": cover_summary({q: mask for q, mask in rejects.items() if not mask & good}),
            "failures_preserving_all_triples": [i for i in range(len(maps)) if bad & (1 << i) and not all_rejected & (1 << i)],
            "extenders_violating_some_triple": [i for i in range(len(maps)) if good & (1 << i) and all_rejected & (1 << i)]}


def analyse(data):
    a, successor, records, history = lineage(data["a"])
    assert history["rounds"]
    (unary, pairs, triples), bonds, span = bond_readings(a)
    (_, next_pairs, _), next_bonds, _ = bond_readings(successor)
    assert exact_table(a, 100_000)[0] == pairs and exact_table(successor, 100_000)[0] == next_pairs
    fixed_live = set().union(*(a.stars[j] for j in a.live))
    maps = sorted(all_mappings(a.labels, pairs, fixed_live), key=lambda phi: tuple(phi[x] for x in a.labels))
    assert len({tuple(phi[x] for x in a.labels) for phi in maps}) == len(maps)
    fixed_distance_classes = defaultdict(list)
    for x in a.labels:
        if x not in fixed_live:
            signature = tuple(pairs[pair_key(x, y)] for y in sorted(fixed_live))
            fixed_distance_classes[signature].append(x)
    classes = sorted(fixed_distance_classes.values())
    signature_upper_bound = prod(factorial(len(group)) for group in classes)
    assert len(maps) == signature_upper_bound
    fixed_probes = [x for x in a.labels if all(phi[x] == x for phi in maps)]
    extends = []
    for phi in maps:
        assert reading(a, a, phi)[1]["keeps_reading"]
        checks = extension_checks(a, successor, records, next_pairs, phi)
        carries = all(sum(a.label_bits[phi[x]] for x in row) in span for row in a.stars)
        extends.append((*checks, carries))
    exact_mask = sum(1 << i for i, (exact, _, _, _) in enumerate(extends) if exact)
    repair_mask = sum(1 << i for i, (_, repair, _, _) in enumerate(extends) if repair)
    round_mask = sum(1 << i for i, (_, _, matches, _) in enumerate(extends) if matches)
    failures = ((1 << len(maps)) - 1) ^ exact_mask
    specified = next(i for i, phi in enumerate(maps) if phi[0] == 2 and phi[2] == 0
                     and all(phi[x] == x for x in a.labels if x not in (0, 2)))
    assert triples[0, 1, 15] == 3 and triples[1, 2, 15] is None
    group = [{"images": [phi[x] for x in a.labels], "extends": exact,
              "extends_with_loose_repair": repaired, "extends_with_round_supports": rounds,
              "carries_equations": eq} for phi, (exact, repaired, rounds, eq) in zip(maps, extends)]
    eq_maps = [phi for phi, (_, _, _, carries) in zip(maps, extends) if carries]
    eq_orbits = {frozenset(phi[x] for phi in eq_maps) for x in a.labels}
    all_moves_in_eq_orbits = all(any(x in orbit and phi[x] in orbit for orbit in eq_orbits)
                                  for phi in maps for x in a.labels)
    central = range(4)
    columns = {x: sum(1 << i for i, bond in enumerate(bonds) if bond & a.label_bits[x]) for x in central}
    common = {pair: (columns[pair[0]] & columns[pair[1]]).bit_count() for pair in combinations(central, 2)}
    assert all({phi[x] for x in central} == set(central) for phi in maps)
    pair_readout = {}
    for name, passes in (("same_bond_occurrence_column", lambda x, y: columns[x] == columns[y]),
                           ("more_than_one_shared_bond", lambda x, y: common[pair_key(x, y)] > 1)):
        accepted = sum(1 << i for i, phi in enumerate(maps) if passes(phi[0], phi[1]) == passes(0, 1))
        pair_readout[name] = {"source_0_1": passes(0, 1), "image_2_1": passes(2, 1),
                              "accepts_exactly_the_extenders": accepted == exact_mask,
                              "failures_detected": (failures & ~accepted).bit_count(),
                              "extenders_rejected": (exact_mask & ~accepted).bit_count()}
    same_equation_subgroup = {i for i, row in enumerate(group) if row["carries_equations"]} == {
        i for i, row in enumerate(group) if row["extends"]}

    return {"current_labels": a.labels, "fixed_live_support_labels": sorted(fixed_live),
            "globally_fixed_probes": fixed_probes, "published_swap_index": specified,
            "automorphisms": group, "exact_extenders": exact_mask.bit_count(),
            "upper_bound_from_distance_to_fixed_supports": signature_upper_bound,
            "classes_by_distance_to_fixed_supports": classes,
            "loose_repaired_extenders": repair_mask.bit_count(), "round_support_extenders": round_mask.bit_count(),
            "same_exact_and_repaired_subsets": exact_mask == repair_mask,
            "same_exact_and_round_support_subsets": exact_mask == round_mask,
            "same_extenders_and_equation_preservers": same_equation_subgroup,
            "max_arity_two_numeric_rejects": sum(any(unary[x,] != unary[phi[x],] for x in a.labels) for phi in maps),
            "equation_span_preserving_subgroup_orbits": sorted(sorted(orbit) for orbit in eq_orbits),
            "all_tested_moves_within_equation_preserving_orbits": all_moves_in_eq_orbits,
            "pair_bond_occurrence": {"common_bonds": [[*p, n] for p, n in common.items()], **pair_readout},
            "published_triple_least_distance": {"source": triples[0, 1, 15], "image": triples[1, 2, 15]},
            "current_bonds": len(bonds), "next_bonds": len(next_bonds),
            "three_way": query_summary(triples, maps, exact_mask, failures, fixed_probes, specified),
            "binary_any_bond": query_summary({args: val is not None for args, val in triples.items()}, maps,
                                             exact_mask, failures, fixed_probes, specified)}


def main():
    path = ROOT / "artifacts" / ARCHIVED_CASE / "construct_6.json"
    print(json.dumps(analyse(json.loads(path.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
