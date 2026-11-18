"""Check the necessary scalar condition for a split of the exterior.

If S is a proper subset of the loose distinctions, moving those exterior
incidences to one new site leaves its complementary wired graph connected.
Thus S is itself a bond in the split system. Every pair in S must already
have bond distance at most |S|-1 if the scalar table is to remain the same.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from math import prod
from pathlib import Path
import json

import networkx as nx

import check_continuation as continuation


ARITIES = (3, 4, 5, 6)
CHECKS = ("same_color_holder_sets", "all_literal_subsets", "proper_holder_sets", "proper_literal_subsets",
          "proper_holder_sets_hitting_a_legal_triple", "proper_literal_subsets_hitting_a_legal_triple",
          "passes_pair_minimum_bound", "literal_subsets_passing_pair_minimum_bound")


def empty_counts():
    return {arity: Counter(dict.fromkeys(CHECKS, 0)) for arity in ARITIES}


def unrestricted_minima(checks):
    """An off-law split can create a unary or binary constraint."""
    dual = [0]
    for check in checks:
        word = sum(1 << bit for bit in check)
        dual.extend([row ^ word for row in dual])
    assert len(dual) == len(set(dual))
    minimal = []
    for word in sorted(dual[1:], key=lambda row: (row.bit_count(), row)):
        if not any(word & other == other for other in minimal):
            minimal.append(word)
    return frozenset(minimal)


def measure(case, gluing):
    stars = tuple(case.fixture.checks().values())
    gluing.replay(stars)
    source = gluing.minimal_dual(stars)
    target = unrestricted_minima((*stars, case.operands))
    assert sum(1 << i for i in case.operands) in target
    original = gluing.scalar_table(source, case.width)
    split = gluing.scalar_table((word for word in target if word.bit_count() >= 3), case.width)
    before, after = (table[case.pair] for table in (original, split))
    assert before == case.distance and before > len(case.operands) - 1 >= after
    return {"family": case.family, "history": case.fixture.history, "width": case.width,
            "original_junctions_in_birth_order": stars, "selected_loose_bits": case.operands,
            "pair_failing_the_bound": case.pair, "distance_before": before, "distance_after": after,
            "smallest_constraint_after_off_law_split": min(word.bit_count() for word in target),
            "legal_triple_hit": case.hit, "candidate_distance_bound": len(case.operands) - 1}


class Closest:
    def __init__(self, family, fixture, width, operands, pair, distance, hit):
        self.family = family
        self.fixture = fixture
        self.width = width
        self.operands = operands
        self.pair = pair
        self.distance = distance
        self.hit = hit


def prefer(collection, arity, case):
    if arity not in collection or case.distance < collection[arity].distance:
        collection[arity] = case


def main():
    root = Path(__file__).resolve().parents[3]
    source, _, gluing = (continuation.load(root, path, digest) for path, digest in continuation.SOURCES)
    scout, _, rules = source.inherited()
    population = continuation.families(scout, rules)
    by_family = {}
    closest = {}
    closest_that_hit = {}
    for name, fixtures in population.items():
        counts = empty_counts()
        by_family[name] = {"fixtures": len(fixtures), "by_new_junction_arity": counts}
        for fixture in fixtures:
            stars = tuple(fixture.checks().values())
            holders, _ = gluing.incidence(stars)
            loose = defaultdict(list)
            for bit, sites in holders.items():
                if len(sites) == 1:
                    loose[sites[0]].append(bit)
            loose_count = sum(map(len, loose.values()))
            colors = nx.bipartite.color(fixture.meeting_graph())
            groups = [sorted(i for i in loose if colors[i] == color) for color in (0, 1)]
            if max(map(len, groups)) < min(ARITIES):
                continue
            menu = sorted(tuple(sorted(move)) for move in scout.actual_menu(rules, fixture.checks()) if len(move) == 3)
            live_parents = {holders[bit][0] for move in menu for bit in move}
            table = gluing.scalar_table(continuation.cut_supports(gluing, stars), len(holders))
            for arity in ARITIES:
                data = counts[arity]
                for group in groups:
                    for parents in combinations(group, arity):
                        # Loose distinctions of the same holder exchange by
                        # exact incidence symmetries. One choice per holder
                        # represents the product of the loose multiplicities.
                        multiplicity = prod(len(loose[parent]) for parent in parents)
                        data["same_color_holder_sets"] += 1
                        data["all_literal_subsets"] += multiplicity
                        if arity == loose_count:
                            continue
                        data["proper_holder_sets"] += 1
                        data["proper_literal_subsets"] += multiplicity
                        operands = tuple(sorted(min(loose[parent]) for parent in parents))
                        hit = next((move for move in menu if set(operands).intersection(move)), None)
                        assert bool(hit) == bool(live_parents.intersection(parents))
                        if hit:
                            data["proper_holder_sets_hitting_a_legal_triple"] += 1
                            data["proper_literal_subsets_hitting_a_legal_triple"] += multiplicity

                        pair = max(combinations(operands, 2), key=table.__getitem__)
                        distance = table[pair]
                        case = Closest(name, fixture, len(holders), operands, pair, distance, hit)
                        prefer(closest, arity, case)
                        if hit:
                            prefer(closest_that_hit, arity, case)
                        if distance <= arity - 1:
                            data["passes_pair_minimum_bound"] += 1
                            data["literal_subsets_passing_pair_minimum_bound"] += multiplicity

    totals = empty_counts()
    for family in by_family.values():
        for arity, counts in family["by_new_junction_arity"].items():
            totals[arity].update(counts)
    assert sum(part["fixtures"] for part in by_family.values()) == 849
    assert all(counts["passes_pair_minimum_bound"] == 0 for counts in totals.values())
    print(json.dumps({
        "source_continuation_checker_sha256": sha256(Path(continuation.__file__).read_bytes()).hexdigest(),
        "fixtures": 849, "by_family": by_family, "totals_by_new_junction_arity": totals,
        "closest_candidates_direct_dual_check": {k: measure(case, gluing) for k, case in closest.items()},
        "closest_triple_hitting_candidates_direct_dual_check": {k: measure(case, gluing)
                                                                for k, case in closest_that_hit.items()},
        "candidates_requiring_refactored_order_test": sum(row["passes_pair_minimum_bound"] for row in totals.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
