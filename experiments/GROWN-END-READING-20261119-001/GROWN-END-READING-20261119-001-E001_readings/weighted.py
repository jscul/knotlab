"""Test every one-or-two multiplicity assignment to the seven-start shared names."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
from hashlib import sha256
from itertools import combinations
import json
from math import factorial, prod
from operator import xor
from pathlib import Path
import sys

import numpy as np

from named import MEET_ONCE_RUN, ROOT, all_mappings, bond_readings, changed
from verify import Arrangement, connected, exact_table, find_matching, indices, pair_key, round_replay, start_audit


SOURCE = ROOT / "artifacts" / MEET_ONCE_RUN / "two_histories.json"
EXTEND_ROUND = Path("EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend")
NO_BOND = 255


def skeleton():
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    from extend import grow1

    source = json.loads(SOURCE.read_text())["seven_at_round_one"]["stages"]
    following = grow1([frozenset(row) for row in source[-1]])
    return [Arrangement.parse(rows) for rows in [*source, [sorted(row) for row in following]]]


def cut_bonds(stage):
    """Recover the skeleton's bonds by connected shores, counted once per cut."""
    _, neighbors, _ = stage.holder_graph()
    half = 1 << (len(neighbors) - 1)
    full = (half << 1) - 1
    return {reduce(xor, (stage.masks[j] for j in indices(shore)), 0)
            for shore in range(1, half) if connected(shore, neighbors) and connected(full ^ shore, neighbors)}


class WeightedReadings:
    def __init__(self, stage, bonds, doubled, arity):
        self.index = {query: i for i, query in enumerate(query for k in range(1, arity + 1)
                                                        for query in combinations(stage.labels, k))}
        width = 1 << len(doubled)
        self.sizes = np.full((width, len(self.index)), NO_BOND, dtype=np.uint8)
        overlap = np.array([x.bit_count() for x in range(width)], dtype=np.uint8)
        weights = np.arange(width)
        optional = {x: 1 << i for i, x in enumerate(doubled)}
        for bond in bonds:
            names = [stage.labels[i] for i in indices(bond)]
            shared = sum(optional.get(x, 0) for x in names)
            columns = [self.index[q] for k in range(1, arity + 1) for q in combinations(names, k)]
            costs = len(names) + overlap[weights & shared]
            self.sizes[:, columns] = np.minimum(self.sizes[:, columns], costs[:, None])

    def table(self, labels, originals, weights, arity):
        row = self.sizes[weights]
        return {args: int(row[self.index[tuple(sorted({originals.get(x, x) for x in args}))]])
                for args in combinations(labels, arity)}


def twin_classes(stage, fixed):
    by_holders = defaultdict(list)
    for x in stage.labels:
        if x not in fixed:
            by_holders[tuple(stage.owners[x])].append(x)
    return list(by_holders.values())


def triple_representatives(labels, pairs, triples, fixed, classes):
    """Exhaust the pair-and-triple stabilizer modulo source parallel columns."""
    fixed = tuple(sorted(fixed))
    fixed_pairs = list(combinations(fixed, 2))
    movable = set(labels) - set(fixed)
    allies = {x: [y for y in members if x != y] for members in classes for x in members}
    signatures = {}
    for x in movable:
        signatures[x] = (tuple(pairs[pair_key(x, y)] for y in fixed),
                         tuple(triples[tuple(sorted((x, u, v)))] for u, v in fixed_pairs),
                         Counter(pairs[pair_key(x, y)] for y in labels if x != y))
    domains = {x: {y for y in movable if signatures[x] == signatures[y]} for x in movable}
    assigned = {x: x for x in fixed}
    used = set()
    extra = []

    def fits(x, y):
        if any(u in assigned and (u < x) != (assigned[u] < y) for u in allies[x]):
            return False
        for u in extra:
            v = assigned[u]
            if pairs[pair_key(x, u)] != pairs[pair_key(y, v)]:
                return False
            for t in fixed:
                if triples[tuple(sorted((x, u, t)))] != triples[tuple(sorted((y, v, t)))]:
                    return False
        return all(triples[tuple(sorted((x, u, t)))] == triples[tuple(sorted((y, assigned[u], assigned[t])))]
                   for u, t in combinations(extra, 2))

    def extend():
        if len(used) == len(movable):
            yield dict(assigned)
            return
        options = {x: sorted(y for y in domains[x] - used if fits(x, y)) for x in movable - assigned.keys()}
        x = min(options, key=lambda x: (len(options[x]), x))
        for y in options[x]:
            assigned[x] = y
            used.add(y)
            extra.append(x)
            yield from extend()
            extra.pop()
            used.remove(y)
            del assigned[x]

    yield from extend()


def equations_kept(stage, phi):
    from verify import linear_basis, reduce_word

    span = linear_basis(stage.masks)
    return all(reduce_word(sum(stage.label_bits[phi[x]] for x in row), span) == 0 for row in stage.stars)


def flips_kept(stage, phi):
    owned = {x: tuple(holders) for x, holders in stage.owners.items()}
    return all((owned[x] == owned[y]) == (owned[phi[x]] == owned[phi[y]]) for x, y in combinations(stage.labels, 2))


def literal_extension(stage, successor, next_pairs, phi):
    bad_old = next(changed({q: d for q, d in next_pairs.items() if set(q) <= stage.owners.keys()}, phi), None)
    if bad_old is not None:
        return None, bad_old
    fresh = set(successor.labels) - set(stage.labels)
    domains = {x: {phi[x]} if x in phi else fresh for x in successor.labels}
    extension = find_matching(next_pairs, next_pairs, domains, phi)
    return None if extension is None else sorted(extension.items()), None


def checked_maps(stage, pairs, triples, fixed, classes, crosscheck):
    representatives = list(triple_representatives(stage.labels, pairs, triples, fixed, classes))
    n = prod(factorial(len(c)) for c in classes)
    for phi in representatives:
        assert next(changed(pairs, phi), None) is None and next(changed(triples, phi), None) is None
    if crosscheck:
        full = [phi for phi in all_mappings(stage.labels, pairs, fixed) if next(changed(triples, phi), None) is None]
        assert len(full) == len(representatives) * n
        assert sum(flips_kept(stage, phi) for phi in full) == sum(flips_kept(stage, phi) for phi in representatives) * n
    return representatives, n


def weighted_copy(stage, chosen, copies):
    return Arrangement.parse([sorted(row | {copies[x] for x in row & chosen}) for row in stage.stars])


def stage_result(age, stages, pair_tri, third_pair, mask, originals, crosscheck):
    stage, successor = stages[age:age + 2]
    fixed = set().union(*(stage.stars[j] for j in stage.live))
    pairs = pair_tri[age].table(stage.labels, originals, mask, 2)
    triples = pair_tri[age].table(stage.labels, originals, mask, 3)
    if crosscheck:
        literal, _bonds, _span = bond_readings(stage)
        for reading, plain in ((pairs, literal[1]), (triples, literal[2])):
            assert all(size == (NO_BOND if plain[q] is None else plain[q] + 1) for q, size in reading.items())
    reps, weight = checked_maps(stage, pairs, triples, fixed, twin_classes(stage, fixed), crosscheck)
    kept = Counter()
    exceptions = []
    next_pairs = None
    for phi in reps:
        equation = equations_kept(stage, phi)
        flip = flips_kept(stage, phi)
        kept["triple"] += 1
        kept["both"] += flip
        kept["triple_equation"] += equation
        kept["both_equation"] += flip and equation
        if equation:
            # Claim B*: the same permutation, with every fresh name fixed, transports every row after the round.
            assert all(phi[x] == x for x in stage.loose)
            kept["triple_extend"] += 1
            kept["both_extend"] += flip
            continue
        if next_pairs is None:
            reading = pair_tri[age + 1] if age == 1 else third_pair()
            next_pairs = reading.table(successor.labels, originals, mask, 2)
            if crosscheck:
                literal, _, _ = exact_table(successor, 5_000_000)
                assert all(next_pairs[q] == (NO_BOND if d is None else d + 1) for q, d in literal.items())
        extension, fails_on_old = literal_extension(stage, successor, next_pairs, phi)
        kept["triple_extend"] += extension is not None
        kept["both_extend"] += flip and extension is not None
        exceptions.append({"permutation": sorted(phi.items()), "also_preserves_flip": flip,
                           "extension": extension, "old_pair_break_in_bond_sizes": fails_on_old})
    result = {"age": age, "width": len(stage.labels), "unweighted_representatives": dict(kept),
              "source_parallel_factor": weight, "full_group_counts": {k: n * weight for k, n in kept.items()},
              "non_equation_representatives": exceptions, "independent_full_group_check": crosscheck}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weight", type=int, action="append", help="checked multiplicity mask, default all")
    parser.add_argument("--ages", nargs="+", type=int, choices=(1, 2), default=[1, 2])
    args = parser.parse_args()
    unweighted = skeleton()
    shared = [x for x in unweighted[0].labels if len(unweighted[0].owners[x]) == 2]
    assert len(shared) == 8
    copies = {x: max(unweighted[-1].labels) + 1 + i for i, x in enumerate(shared)}
    originals = {copy: original for original, copy in copies.items()}
    tables = {}
    skeleton_counts = {}
    for age in (1, 2):
        stage = unweighted[age]
        bonds = cut_bonds(stage)
        assert bonds == set(bond_readings(stage)[1])
        tables[age] = WeightedReadings(stage, bonds, shared, 3)
        skeleton_counts[age] = len(bonds)
    third = None

    def third_pair():
        nonlocal third
        if third is None:
            bonds = cut_bonds(unweighted[3])
            skeleton_counts[3] = len(bonds)
            third = WeightedReadings(unweighted[3], bonds, shared, 2)
        return third

    rows = []
    for mask in args.weight if args.weight is not None else range(1 << len(shared)):
        assert 0 <= mask < 1 << len(shared)
        chosen = {shared[i] for i in indices(mask)}
        stages = [weighted_copy(stage, chosen, copies) for stage in unweighted]
        assert start_audit(stages[0])["census_open_legal"]
        for previous, following in zip(stages, stages[1:]):
            round_replay(previous, following)
        results = [stage_result(age, stages, tables, third_pair, mask, originals, mask in (0, 1, 255))
                   for age in args.ages]
        rows.append({"mask": mask, "doubled": sorted(chosen), "results": results})
    totals = {age: dict(sum((Counter(row["full_group_counts"]) for case in rows for row in case["results"]
                            if row["age"] == age), Counter())) for age in args.ages}
    output = {"source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
              "original_shared_names": shared, "possible_starts": 1 << len(shared), "copy_labels": copies,
              "skeleton_rounds": [[sorted(row) for row in stage.stars] for stage in unweighted],
              "skeleton_bond_counts": skeleton_counts, "group_totals": totals, "starts": rows}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
