"""Rebuild the parity readings and recount a1, a2 and a3 from the frozen witness definitions."""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import reduce
from itertools import combinations, islice
import json
from operator import or_, xor
from pathlib import Path
import resource
from time import perf_counter

from knotlab.knots import check_knot
from knotlab.relations import Relation


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PREVIOUS_WITNESS = (
    STUDY.parent / "SELECTED-KNOTS-20261127-001" / "referee-R1" / "natural_places.json"
)


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def bit_mask(indices_):
    return reduce(or_, (1 << index for index in indices_), 0)


def xor_sum(values):
    return reduce(xor, values, 0)


def reachable(adjacency, first):
    reached = {first}
    pending = [first]
    while pending:
        for other in adjacency[pending.pop()] - reached:
            reached.add(other)
            pending.append(other)
    return reached


class LawSpan:
    """Binary elimination retaining the source law indices of each row."""

    def __init__(self, rows):
        self.pivots = {}
        for index, row in enumerate(rows):
            remainder, used = self.reduce(row)
            if remainder:
                self.pivots[remainder.bit_length() - 1] = remainder, used ^ (1 << index)

    def reduce(self, row):
        used = 0
        remainder = 0
        while row:
            leading = row.bit_length() - 1
            if leading in self.pivots:
                pivot, source = self.pivots[leading]
                row ^= pivot
                used ^= source
            else:
                bit = 1 << leading
                row ^= bit
                remainder |= bit
        return remainder, used

    def sources(self, row):
        remainder, used = self.reduce(row)
        return None if remainder else used


@dataclass(frozen=True)
class RingWitness:
    sizes: tuple
    laws: tuple
    generation: tuple
    carriers: tuple
    start_families: tuple
    stages: tuple


def start_laws(sizes):
    laws = [0] * sum(sizes)
    distinction = 0

    def share(*holders):
        nonlocal distinction
        bit = 1 << distinction
        for holder in holders:
            laws[holder] |= bit
        distinction += 1
        return bit

    rings = []
    first = 0
    for size in sizes:
        ring = tuple(range(first, first + size))
        rings.append(ring)
        for left, right in zip(ring, ring[1:] + ring[:1]):
            share(left, right)
        first += size

    ring_loose = tuple(reduce(or_, (share(holder) for holder in ring for _ in range(2)))
                       for ring in rings)
    ports = [0] * len(rings)
    for left, right in combinations(range(len(rings)), 2):
        pair = []
        for index in (left, right):
            holder = len(laws)
            laws.append(0)
            pair.append(holder)
            ring = rings[index]
            share(holder, ring[ports[index] % len(ring)])
            share(holder, ring[(ports[index] + 2) % len(ring)])
            ports[index] += 1
        share(*pair)
        share(*pair)

    return tuple(laws), distinction, ring_loose


def loose_and_candidates(laws):
    holders = defaultdict(list)
    for knot, law in enumerate(laws):
        for distinction in indices(law):
            holders[distinction].append(knot)

    neighbours = [set() for _ in laws]
    loose = defaultdict(deque)
    for distinction, knots in sorted(holders.items()):
        if len(knots) == 1:
            loose[knots[0]].append(distinction)
        else:
            assert len(knots) == 2
            left, right = knots
            neighbours[left].add(right)
            neighbours[right].add(left)

    pairs = set()
    for adjacent in neighbours:
        pairs.update(combinations(sorted(adjacent & loose.keys()), 2))
    candidates = {knot: set() for knot in loose}
    for left, right in pairs:
        candidates[left].add(right)
        candidates[right].add(left)
    # A group of three or more would contain three mutually eligible knots.
    assert all(not (candidates[left] & candidates[right]) for left, right in pairs)
    assert all(len(loose[knot]) == 2 and len(others) <= 2 for knot, others in candidates.items())
    return loose, candidates, sorted(pairs)


def grow_rings(sizes, rounds):
    """Use the joining rule on the path and cycle components of these starts."""
    laws, next_distinction, ring_loose = start_laws(sizes)
    generation = [0] * len(laws)
    stages = [(len(laws), next_distinction)]
    _, candidates, _ = loose_and_candidates(laws)
    family_of = {}
    families = []
    for knot in sorted(candidates):
        if knot not in family_of:
            family = tuple(sorted(reachable(candidates, knot)))
            family_of.update(dict.fromkeys(family, len(families)))
            families.append(family)
    assert len(families) == 2 * len(sizes)
    assert tuple(len(family) for family in families) == tuple(size // 2 for size in sizes for _ in range(2))
    first_fresh = [0] * len(families)
    for round_ in range(1, rounds + 1):
        loose, candidates, pairs = loose_and_candidates(laws)
        plans = pairs + [(knot,) for knot in sorted(loose)
                         for _ in range(len(loose[knot]) - len(candidates[knot]))]
        children = defaultdict(list)
        for birth, parents in enumerate(plans):
            for parent in parents:
                children[parent].append(birth)
        assert all(len(children[parent]) == len(values) == 2 for parent, values in loose.items())
        next_pairs = {tuple(children[parent]) for parent in loose}
        next_demand = Counter(child for pair in next_pairs for child in pair)
        next_families = {}
        births = []
        for birth, parents in enumerate(plans):
            taken = bit_mask(loose[parent].popleft() for parent in parents)
            fresh_count = max(3 - len(parents), next_demand[birth])
            fresh = bit_mask(range(next_distinction, next_distinction + fresh_count))
            next_distinction += fresh_count
            family = family_of[parents[0]]
            assert all(family_of[parent] == family for parent in parents)
            next_families[len(laws) + birth] = family
            if round_ == 1:
                first_fresh[family] |= fresh
            births.append(taken | fresh)
        assert all(not values for values in loose.values())
        laws += tuple(births)
        generation.extend([round_] * len(births))
        family_of = next_families
        stages.append((len(laws), next_distinction))
    return RingWitness(sizes, laws, tuple(generation), tuple(first_fresh) + ring_loose,
                       tuple(families), tuple(stages))


def fact_names(rings):
    return tuple(f"{letter}{index}" for index in range(1, rings + 1) for letter in ("p", "q")) + tuple(
        f"R{index}" for index in range(1, rings + 1)
    )


def independent_fact_words(rings):
    family_count = 2 * rings
    return {families | bit_mask(family_count + ring for ring in range(rings)
                                if ((families >> (2 * ring)) & 3).bit_count() % 2)
            for families in range(1 << family_count) if families.bit_count() % 2 == 0}


def equations(words, places):
    return tuple(support for support in range(1, 1 << places)
                 if all((support & word).bit_count() % 2 == 0 for word in words))


def consequences(carriers, span):
    implied = {}
    for support in range(1, 1 << len(carriers)):
        carrier_sum = xor_sum(carriers[place] for place in indices(support))
        sources = span.sources(carrier_sum)
        if sources is not None:
            implied[support] = sources
    return implied


def project(words, places):
    return {tuple(bool(word & (1 << place)) for place in places) for word in words}


def readings(words, places):
    return sorted("".join(str(int(value)) for value in row) for row in project(words, places))


def constraints_on_distinctions(laws, distinctions):
    # The projection of law supports onto the unobserved distinctions has this kernel.
    return len(LawSpan(laws).pivots) - len(LawSpan(law & ~distinctions for law in laws).pivots)


def meeting_adjacency(basis):
    adjacency = [set() for _ in basis]
    for (left, first), (right, second) in combinations(enumerate(basis), 2):
        if first & second:
            adjacency[left].add(right)
            adjacency[right].add(left)
    return adjacency


def loose_facts(basis):
    return xor_sum(basis)


def counts_by_place(basis, place_count):
    return tuple(sum(bool(relation & (1 << place)) for relation in basis) for place in range(place_count))


def named_support(support, names):
    return tuple(names[index] for index in indices(support))


def named_basis(basis, names):
    return sorted(named_support(support, names) for support in basis)


def basis_census(rings, check_extra_presentations=False):
    names = fact_names(rings)
    words = independent_fact_words(rings)
    relations = equations(words, len(names))
    dimension = len(LawSpan(relations).pivots)
    minimal = tuple(support for support in relations
                    if not any(other != support and other & support == other for other in relations))
    if rings == 3:
        for support in relations:
            places = tuple(indices(support))
            labels = named_support(support, names)
            observed = Relation(labels, frozenset(project(words, places)))
            assert all(check_knot(observed, labels[:contact] + labels[contact + 1:], label).is_knot
                       == (support in minimal) for contact, label in enumerate(labels))

    bases = [basis for basis in combinations(relations, dimension) if len(LawSpan(basis).pivots) == dimension]
    two_holders = [basis for basis in bases if max(counts_by_place(basis, len(names))) <= 2]
    assert all(0 not in counts_by_place(basis, len(names)) for basis in bases)
    assert all(all(support in minimal for support in basis) for basis in two_holders)

    counted = Counter()
    loose_classes = defaultdict(list)
    for basis in two_holders:
        adjacency = meeting_adjacency(basis)
        connected = len(reachable(adjacency, 0)) == len(basis)
        assert connected
        counted["cycle"] += sum(map(len, adjacency)) // 2 >= len(adjacency)
        counted["one ring"] += all(len(others) == 2 for others in adjacency)
        loose_classes[loose_facts(basis)].append(basis)

    family_mask = (1 << (2 * rings)) - 1
    family_loose = [basis for basis in two_holders if loose_facts(basis) & family_mask == family_mask]
    census = {
        "fact order": names,
        "allowed words": len(words),
        "relation dimension": dimension,
        "nonzero equations": len(relations),
        "nonzero equations by places": dict(sorted(Counter(value.bit_count() for value in relations).items())),
        "minimal equations by places": dict(sorted(Counter(value.bit_count() for value in minimal).items())),
        "rank bases": len(bases),
        "bases with only minimal equations": sum(all(support in minimal for support in basis) for basis in bases),
        "bases with every fact held by at most two knots": len(two_holders),
        "such bases with a cycle": counted["cycle"],
        "such bases with one ring on all their knots": counted["one ring"],
        "such bases with all family facts held once": len(family_loose),
        "the one such basis": named_basis(family_loose[0], names),
        "distinct loose sets among holder-capped bases": len(loose_classes),
        "loose-set counts by number of bases": dict(sorted(Counter(map(len, loose_classes.values())).items())),
        "distinct completed systems": len({tuple(sorted((*basis, loose_facts(basis)))) for basis in two_holders}),
    }
    assert len(family_loose) == 1
    if check_extra_presentations:
        valid = []
        for size in range(dimension, len(minimal) + 1):
            for presentation in combinations(minimal, size):
                if max(counts_by_place(presentation, len(names))) <= 2 and len(LawSpan(presentation).pivots) == dimension:
                    valid.append(presentation)
        assert all(len(reachable(meeting_adjacency(item), 0)) == len(item) for item in valid)
        census["all presentations with the holder cap and no limit on knot count, by knot count"] = dict(
            sorted(Counter(map(len, valid)).items())
        )
        census["closed presentations with no loose facts"] = sum(loose_facts(item) == 0 for item in valid)
        census["holder-capped rank bases grouped by loose facts"] = [
            {"loose facts": named_support(loose, names), "bases": [named_basis(basis, names) for basis in grouped]}
            for loose, grouped in sorted(loose_classes.items())
        ]
        root = ((1 << rings) - 1) << (2 * rings)
        quadruples = tuple(root ^ ((1 << (2 * rings + ring)) | (3 << (2 * ring))) for ring in range(rings))
        earlier_loop = (root, *quadruples)
        assert tuple(sorted(earlier_loop)) in bases
        loop_counts = counts_by_place(earlier_loop, len(names))
        census["root and three quadruples"] = {
            "is a rank basis": True,
            "has only minimal equations": all(equation in minimal for equation in earlier_loop),
            "holders by fact": dict(zip(names, loop_counts)),
            "loose facts by holder count": tuple(name for name, count in zip(names, loop_counts) if count == 1),
            "can be completed by adding one knot to leave every fact with two holders": False,
        }
    return census, bases, minimal, two_holders


def check_deletions(witness, deletion_limit=None):
    ring_count = len(witness.sizes)
    names = fact_names(ring_count)
    word_count = 1 << len(names)
    expected = independent_fact_words(ring_count)
    laws = witness.laws
    span = LawSpan(laws)
    assert len(span.pivots) == len(laws)
    observed = consequences(witness.carriers, span)
    words = {word for word in range(word_count)
             if all((word & relation).bit_count() % 2 == 0 for relation in observed)}
    assert words == expected
    assert tuple(sorted(observed)) == equations(expected, len(names))

    quadruples = []
    for ring in range(ring_count):
        places = (2 * ring, 2 * ring + 1, *(2 * ring_count + other for other in range(ring_count) if other != ring))
        labels = tuple(names[place] for place in places)
        carriers = tuple(witness.carriers[place] for place in places)
        allowed = project(words, places)
        assert len(allowed) == 8
        assert all(check_knot(Relation(labels, frozenset(allowed)), labels[:i] + labels[i + 1:], label).is_knot
                   for i, label in enumerate(labels))
        support = bit_mask(places)
        sources = observed[support]
        sources_by_round = dict(sorted(Counter(witness.generation[index] for index in indices(sources)).items()))

        deletions = Counter()
        for row, round_ in islice(enumerate(witness.generation), deletion_limit):
            remaining = LawSpan(laws[:row] + laws[row + 1:])
            implied = consequences(carriers, remaining)
            assert implied.keys() in (set(), {15})
            freed = not implied
            assert freed == bool(sources & (1 << row))
            deletions[round_, "all sixteen" if freed else "eight even"] += 1
        quadruples.append({
            "places": labels,
            "allowed readings": readings(words, places),
            "independent constraints if reading their physical distinctions separately":
                constraints_on_distinctions(laws, reduce(or_, carriers)),
            "unique law sum by birth round": sources_by_round,
            "one-law deletions by birth round": [
                {"round": round_, "freed": deletions[round_, "all sixteen"],
                 "unchanged": deletions[round_, "eight even"]}
                for round_ in sorted(set(witness.generation))
            ],
        })
    return {"round": witness.generation[-1], "quadruples": quadruples,
            "start laws": witness.stages[0][0], "laws tested per quadruple": len(laws[:deletion_limit]),
            "nine fact words": readings(words, range(len(names)))}


def cost_by_equation(witness, relations):
    span = LawSpan(witness.laws)
    assert len(span.pivots) == len(witness.laws)
    costs = {}
    for equation in relations:
        carriers = tuple(witness.carriers[index] for index in indices(equation))
        source_mask = span.sources(xor_sum(carriers))
        assert source_mask is not None
        laws = tuple(witness.laws[index] for index in indices(source_mask))
        costs[equation] = {"places": len(carriers), "carrier distinctions": reduce(or_, carriers).bit_count(),
                           "laws": len(laws), "distinct distinctions in the laws": reduce(or_, laws).bit_count(),
                           "place occurrences in the laws": sum(law.bit_count() for law in laws)}
    return costs


def least_cost_bases(bases, costs, names, quad, tree):
    minima = {}
    for metric in costs[quad]:
        totals = {basis: sum(costs[equation][metric] for equation in basis) for basis in bases}
        minimum = min(totals.values())
        tied = [basis for basis, total in totals.items() if total == minimum]
        minima[metric] = {
            "minimum total": minimum,
            "tree total": totals[tree],
            "minimizing bases": len(tied),
            "minimizing bases containing the big-ring quadruple": sum(quad in basis for basis in tied),
            "one minimum basis": named_basis(tied[0], names),
        }
    return minima


def cost_readings(witness, bases, minimal, two_holders):
    names = fact_names(len(witness.sizes))
    relations = equations(independent_fact_words(len(witness.sizes)), len(names))
    costs = cost_by_equation(witness, relations)
    triple = (1 << 6) | 3
    quad = (1 << 7) | (1 << 8) | 3
    root = bit_mask(range(6, 9))
    triples = tuple((3 << (2 * ring)) | (1 << (6 + ring)) for ring in range(3))
    tree = tuple(sorted((root, *triples)))
    assert tree in two_holders
    physical_counts = {
        equation: constraints_on_distinctions(witness.laws, reduce(or_, (witness.carriers[i] for i in indices(equation))))
        for equation in (triple, quad)
    }
    return {
        "ring sizes": witness.sizes,
        "start families": witness.start_families,
        "knots and distinctions by round": witness.stages,
        "carrier sizes by fact": dict(zip(names, (carrier.bit_count() for carrier in witness.carriers))),
        "triple R1 p1 q1": costs[triple],
        "quadruple p1 q1 R2 R3": costs[quad],
        "independent constraints if reading their physical distinctions separately": {
            "triple": physical_counts[triple], "quadruple": physical_counts[quad]
        },
        "minimum totals across the full basis": {
            "all rank bases": least_cost_bases(bases, costs, names, quad, tree),
            "bases of knots": least_cost_bases([basis for basis in bases if all(rule in minimal for rule in basis)],
                                               costs, names, quad, tree),
            "bases with every fact held at most twice": least_cost_bases(two_holders, costs, names, quad, tree),
        },
    }


def compare_records(result, witness):
    raw = json.loads((STUDY / "checks_a.json").read_text())
    a1 = result["a1"]
    for calculated, original in (
        ("nonzero equations", "relations"), ("relation dimension", "dimension"), ("rank bases", "bases"),
        ("bases with every fact held by at most two knots", "every fact in at most two relations"),
        ("such bases with a cycle", "of those, relations meeting in a cycle"),
        ("such bases with one ring on all their knots", "of those, four relations meeting in one ring"),
        ("such bases with all family facts held once", "of those, six family facts each in exactly one relation"),
    ):
        assert a1[calculated] == raw["a1"][original]
    assert {frozenset(rule) for rule in a1["the one such basis"]} == {
        frozenset(rule) for rule in raw["a1"]["that basis"]
    }

    a2 = result["a2"]
    assert a2["round"] == raw["a2"]["round"] and a2["start laws"] == raw["a2"]["start laws"]
    for ring, (calculated, original) in enumerate(zip(a2["quadruples"], raw["a2"]["quadruples"], strict=True), 1):
        by_round = calculated["one-law deletions by birth round"]
        assert len(calculated["allowed readings"]) == original[f"quadruple of ring {ring}"]
        assert by_round[0]["freed"] == original["single removals freeing it"]["start"]
        assert sum(row["freed"] for row in by_round[1:]) == original["single removals freeing it"]["born"]

    a3 = result["a3"]
    for relation, original in (("triple R1 p1 q1", "triple R1 = p1 + q1"),
                               ("quadruple p1 q1 R2 R3", "quadruple p1 q1 R2 R3")):
        for measured, recorded in (("places", "places"), ("laws", "laws"),
                                   ("distinct distinctions in the laws", "distinctions")):
            assert a3[relation][measured] == raw["a3"][original][recorded]
    assert raw["a3"]["families of the big ring"] == sum(a[0] < a3["ring sizes"][0] for a in a3["start families"])

    prior = json.loads(PREVIOUS_WITNESS.read_text())["three_rings_of_four"]
    assert [list(family) for family in witness.start_families] == prior["start families"]
    assert [list(indices(carrier)) for carrier in witness.carriers] == prior["disjoint carriers as distinction numbers"]
    assert [list(stage) for stage in witness.stages] == prior["knots and distinctions through rounds"]
    assert a2["nine fact words"] == readings(prior["allowed words"], range(9))
    return {"all raw a1–a3 fields match": True,
            "earlier witness matches stage sizes, families, all nine carrier supports and allowed words": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time a prefix at the same witness sizes and resource limit")
    parser.add_argument("--output", type=Path, default=HERE / "layer_counts.json")
    arguments = parser.parse_args()
    limit = 2 * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    started = perf_counter()

    a1, bases, minimal, two_holders = basis_census(3, check_extra_presentations=True)
    deletion_witness = grow_rings((4, 4, 4), 5)
    a2 = check_deletions(deletion_witness, 12 if arguments.pilot else None)
    a2["knots and distinctions by round"] = deletion_witness.stages
    a2["nine disjoint carrier supports"] = dict(zip(fact_names(3), (list(indices(carrier)) for carrier in deletion_witness.carriers)))
    unequal_witness = grow_rings((10, 4, 4), 2)
    a3 = cost_readings(unequal_witness, bases, minimal, two_holders)
    result = {"a1": a1, "a2": a2, "a3": a3}
    if arguments.pilot:
        print(f"Pilot: {a1['rank bases']} bases, {a2['laws tested per quadruple']} of {len(deletion_witness.laws)} "
              f"single deletions per quadruple, {a3['knots and distinctions by round'][-1][0]} unequal-ring laws, "
              f"{perf_counter() - started:.3f} s")
        larger_relations = equations(independent_fact_words(4), 12)
        before_prefix = perf_counter()
        prefix = sum(len(LawSpan(basis).pivots) == 5 for basis in islice(combinations(larger_relations, 5), 5000))
        print(f"Four-ring pilot: {prefix} bases among the first 5,000 candidate sets, "
              f"{perf_counter() - before_prefix:.3f} s")
        return

    result["record comparisons"] = compare_records(result, deletion_witness)
    result["four-ring algebraic stress"] = basis_census(4)[0]
    result["carrier and law counts on nearby unequal rings"] = [
        {"ring sizes": sizes,
         "triple": counts["triple R1 p1 q1"], "quadruple": counts["quadruple p1 q1 R2 R3"]}
        for sizes in ((8, 4, 4), (12, 4, 4))
        for counts in (cost_readings(grow_rings(sizes, 2), bases, minimal, two_holders),)
    ]
    arguments.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Recount: all raw a1–a3 fields match; {perf_counter() - started:.3f} s")


if __name__ == "__main__":
    main()
