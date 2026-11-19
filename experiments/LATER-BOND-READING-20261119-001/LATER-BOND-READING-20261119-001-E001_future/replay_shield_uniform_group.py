"""Audit the full compact 224-stage pointwise-live stabilizer by exact readings."""

import argparse
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations
import json
from math import comb, factorial, prod
import sys

from replay_shield_uniform import (EXTEND_ROUND, ROOT, Fixture, Minimum, actual_growth, branch_certificates,
                                  connected_shores, image_key, optimized_production_round)
from replay_shield import follow
from verify import connected, indices, linear_basis, reduce_word


def local_edges(stage, fixture, arms):
    ends, _, outer = stage.holder_graph()
    templates = {}
    for j, arm in arms.items():
        nodes = [fixture.i + j, *arm["old_sites"], *arm["children_age_one"], outer]
        rank = {node: i for i, node in enumerate(nodes)}
        graph = [(tuple(sorted((rank[u], rank[v]))), name) for name, (u, v) in ends.items() if u in rank and v in rank]
        graph.sort()
        templates[j] = tuple(ends for ends, _ in graph), [name for _, name in graph]
    return templates


def local_bonds(topology):
    size = max(v for edge in topology for v in edge) + 1
    adj = [0] * size
    incident = [0] * size
    for j, (u, v) in enumerate(topology):
        adj[u] |= 1 << v
        adj[v] |= 1 << u
        incident[u] |= 1 << j
        incident[v] |= 1 << j
    adj[0] |= 1 << (size - 1)
    adj[-1] |= 1
    full = (1 << size) - 1
    cut = shore = 0
    parts = [[], []]
    for step in range(1, 1 << (size - 1)):
        bit = step & -step
        shore ^= bit
        cut ^= incident[bit.bit_length() - 1]
        if connected(shore, adj) and connected(full ^ shore, adj):
            k = cut.bit_count()
            parts[shore & 1].append((cut, shore, k, k))
    return [Minimum(part, topology, 1) for part in parts], [len(p) for p in parts]


class FullMinima:
    def __init__(self, f, stage, arms):
        core = [keys for keys, *rest in f.edges]
        self.branch_slot = {j: core.index(("branch", j)) for j in arms}
        self.compressed_bonds = connected_shores(f)
        self.host = Minimum(self.compressed_bonds, core, 1)
        templates = local_edges(stage, f, arms)
        decks = {graph: local_bonds(graph) for graph in {g for g, _ in templates.values()}}
        self.local_decks = {j: decks[g][0] for j, (g, _) in templates.items()}
        self.local_bonds = {j: decks[g][1] for j, (g, _) in templates.items()}
        self.names = {x: (None, k) for k, key in enumerate(core) if key in f.physical for x in f.physical[key]}
        self.names.update({name: (j, k) for j, (_, names) in templates.items() for k, name in enumerate(names)})
        assert set(self.names) == set(stage.labels)
        self.branch_capacity = f.m

    @cache
    def host_K(self, marks):
        return self.host.mark(marks)[0]

    @cache
    def local_K(self, branch, marks, separate):
        return self.local_decks[branch][int(separate)].mark(marks)[0]

    @cache
    def query(self, marks):
        host = set()
        branches = defaultdict(set)
        for x in marks:
            j, k = self.names[x]
            if j is None:
                host.add(k)
            else:
                branches[j].add(k)
        if not host and len(branches) == 1:
            j, local = next(iter(branches.items()))
            names = tuple(sorted(local))
            together, apart = self.local_K(j, names, False), self.local_K(j, names, True)
            external = self.host_K((self.branch_slot[j],))
            connected_cost = None if external is None or apart is None else external + apart - self.branch_capacity
            return min((v for v in (together, connected_cost) if v is not None), default=None)

        extra = 0
        for j, names in branches.items():
            k = self.local_K(j, tuple(sorted(names)), True)
            if k is None:
                return None
            host.add(self.branch_slot[j])
            extra += k - self.branch_capacity
        k = self.host_K(tuple(sorted(host)))
        return None if k is None else k + extra


def pair_classes(stage, deck):
    fixed = set().union(*(stage.stars[j] for j in stage.live))
    by_holders = defaultdict(list)
    for x in stage.labels:
        if x not in fixed:
            by_holders[tuple(stage.owners[x])].append(x)
    columns = list(by_holders.values())
    blocks = defaultdict(list)
    for column in columns:
        x = column[0]
        signature = tuple(deck.query((x, y)) for y in sorted(fixed))
        blocks[signature].append(column)
    return fixed, list(blocks.values())


def host_names(fixture, arms):
    return [arms[key[-1]].get("fixed_minimum_probe", arms[key[-1]]["literal_capacity_routes"][0][-1])
            if key[0] == "branch" else fixture.physical[key][0]
            for key, *_ in fixture.edges]


def recover_columns(blocks, deck, host_representatives):
    """Use at most two invariant probes to distinguish all unlike ambiguous columns."""
    ambiguous = [block for block in blocks if len(block) > 1]
    unpinned = {deck.names[column[0]][1] for b in ambiguous for column in b}
    probes = [i for i in range(len(host_representatives)) if i not in unpinned]
    evidence = []
    for block in ambiguous:
        if max(map(len, block)) == 1:
            continue
        assert all(deck.names[column[0]][0] is None for column in block)
        for a_col, b_col in combinations(block, 2):
            a, b = (deck.names[col[0]][1] for col in (a_col, b_col))
            best = None
            for k in (1, 2):
                for z in combinations(probes, k):
                    triple = deck.host_K(tuple(sorted((a, b, *z))))
                    singles = tuple(deck.host_K(tuple(sorted((p, *z)))) for p in (a, b))
                    if singles != (triple, triple):
                        best = {"probes": [host_representatives[p] for p in z], "joined": triple, "individuals": singles}
                        break
                if best is not None:
                    break
            evidence.append({"columns": (a_col, b_col), "distinguishing_reading": best})
    return evidence


def pair_candidates(blocks, fixed, deck):
    movable = {column[0]: column for block in blocks if len(block) > 1 for column in block}
    pinned = sorted(fixed | {block[0][0] for block in blocks if len(block) == 1})
    signatures = {x: tuple(deck.query((x, y)) for y in pinned) for x in movable}
    domains = {column[0]: {candidate[0] for candidate in block if len(candidate) == len(column)
                          and signatures[column[0]] == signatures[candidate[0]]}
               for block in blocks if len(block) > 1 for column in block}

    def unwind(assigned):
        if len(assigned) == len(movable):
            yield {x: y for a, b in assigned.items() for x, y in zip(movable[a], movable[b])}
            return
        options = {}
        for x in movable.keys() - assigned.keys():
            options[x] = [y for y in sorted(domains[x] - set(assigned.values())) if all(
                deck.query(tuple(sorted((x, p)))) == deck.query(tuple(sorted((y, q)))) for p, q in assigned.items())]
        x = min(options, key=lambda i: (len(options[i]), i))
        for y in options[x]:
            assigned[x] = y
            yield from unwind(assigned)
            del assigned[x]

    yield from unwind({})


def rank_check(stage, permutation):
    basis = linear_basis(stage.masks)
    return all(reduce_word(sum(stage.label_bits[permutation.get(x, x)] for x in row), basis) == 0 for row in stage.stars)


def whole_group_check(stage, fixture, arms, deck, fixed, blocks):
    representatives = host_names(fixture, arms)
    column_recovery = recover_columns(blocks, deck, representatives)
    maps = list(pair_candidates(blocks, fixed, deck))
    # Exact triplet and quartet checks may use the compressed names because the branch interiors are fixed.
    equiv = []
    remaining = {}
    inverse = {x: j for j, x in enumerate(representatives)}
    for i, permutation in enumerate(maps):
        witness = {"map": sorted((x, y) for x, y in permutation.items() if x != y),
                   "preserves_equations": rank_check(stage, permutation)}
        equiv.append(witness)
        if not witness["preserves_equations"]:
            remaining[i] = {p: inverse[permutation.get(x, x)] for p, x in enumerate(representatives)
                            if permutation.get(x, x) != x}
    # Only selected root/branch probe distinctions are needed to realize a compressed query in the literal system.
    by_order = {}
    for size in (1, 2, 3, 4):
        for query in combinations(range(len(representatives)), size):
            if not remaining:
                break
            if not any(p in marking for marking in remaining.values() for p in query):
                continue
            old = deck.host_K(query)
            for i, marking in list(remaining.items()):
                changed = tuple(sorted(marking.get(p, p) for p in query))
                if changed != query and old != (new := deck.host_K(changed)):
                    equiv[i]["first_mismatch"] = {"arity": size, "source": [representatives[p] for p in query],
                                                 "image": [representatives[p] for p in changed], "K": [old, new]}
                    del remaining[i]
        by_order[size] = sum(w["preserves_equations"] or w.get("first_mismatch", {}).get("arity", float("inf")) > size
                            for w in equiv)
    all_columns = all(row["distinguishing_reading"] is not None for row in column_recovery)
    max_arity = (max((2 + len(row["distinguishing_reading"]["probes"]) for row in column_recovery), default=2)
                 if all_columns else None)
    return {"maximum_arity_for_holder_column_recognition_without_flip": max_arity,
            "column_recovery": column_recovery, "quotient_candidates_checked": len(maps),
            "equal_holder_column_permutation_factor": prod(factorial(len(column)) for b in blocks for column in b),
            "candidates_by_arity": by_order, "non_equation_preservers_after_four": len(remaining),
            "maps": equiv}


class HybridFixture(Fixture):
    def __init__(self, anchors=2, shields=6, hub=3, special=3, shield=8, capacity=8):
        super().__init__(anchors, shields, hub, capacity, True, anchor_hot=special, shield_weight=shield)
        self.parameters = (anchors, shields, hub, special, shield, capacity)
        self.edges = [(k, u, v, weight, weight if k[0] == "branch" and k[-1] >= 4 + self.s else next_)
                      for k, u, v, weight, next_ in self.edges]

    def branch(self, pole):
        if pole - self.i < 4 + self.s:
            return super().branch(pole)
        u = self.site()
        entries = [self.wire(pole, u) for _ in range(self.m)]
        self.loose(u, self.m)
        return {"old_sites": [u], "stable_ports": entries}


def hybrid_certificates(fixture, stages, records):
    start, current, successor = stages
    old, next_ = records
    current_ends, _, current_outer = current.holder_graph()
    next_ends, _, next_outer = successor.holder_graph()
    result = {}
    for j, arm in fixture.arms.items():
        initial = set(arm["old_sites"])
        now = [(u, row) for u, row in enumerate(old, len(start.stars)) if row["taken"].keys() <= initial]
        sites = [u for u, _ in now]
        assert len(sites) == fixture.m
        later = {frozenset(row["taken"]): (v, row) for v, row in enumerate(next_, len(current.stars))
                 if row["taken"].keys() <= set(sites)}
        if ports := arm.get("stable_ports"):
            (holder,) = initial
            paths = [(entry, row["taken"][holder], row["fresh"][0]) for entry, (_, row) in zip(ports, now)]
            probe = paths[0][1]
            assert len(later) == comb(fixture.m, 2)
            next_routes = []
            for i, path in enumerate(paths):
                _, row = later[frozenset((sites[i], sites[(i + 1) % len(sites)]))]
                next_routes.append((*path[:2], row["taken"][sites[i]], row["fresh"][0]))
            assert all(follow(next_ends, fixture.i + j, r) == next_outer for r in next_routes)
            assert len({x for r in next_routes for x in r}) == sum(map(len, next_routes))
        else:
            by_parents = {frozenset(row["taken"]): row for _, row in now}
            paths = []
            for parents, holder, prefix in arm["original_route_plan"]:
                row = by_parents[frozenset(parents)]
                (fresh,) = row["fresh"]
                paths.append((*prefix, row["taken"][holder], fresh))
            assert len(later) == 1
            (single,) = later.values()
            (_tip,) = single[1]["fresh"]
            probe = paths[0][-1]
        assert all(follow(current_ends, fixture.i + j, r) == current_outer for r in paths)
        assert len({x for r in paths for x in r}) == sum(map(len, paths))
        result[j] = {"old_sites": arm["old_sites"], "children_age_one": sites,
                     "children_age_two": [v for v, _ in later.values()], "literal_capacity_routes": paths,
                     "fixed_minimum_probe": probe, "stable": bool(ports)}
    return result


def hybrid_lift(f, stage, arms, shore, age, branch_marks=()):
    endpoints, neighbors, exterior = stage.holder_graph()
    ordinary = {j for j in indices(shore) if j != f.outside}
    exterior_inside = bool(shore >> f.outside & 1)
    if exterior_inside:
        ordinary.add(exterior)
    for j, arm in arms.items():
        mid_inside = f.i + j in ordinary
        if arm["stable"]:
            former_parent_inside = (mid_inside if age == 1 and j in branch_marks else exterior_inside)
            descendants_inside = exterior_inside
        else:
            former_parent_inside = descendants_inside = mid_inside
        if former_parent_inside:
            ordinary.update(arm["old_sites"])
        if descendants_inside:
            ordinary.update(arm["children_age_one"])
            if age == 2:
                ordinary.update(arm["children_age_two"])
    mask = sum(1 << j for j in ordinary)
    total = (1 << len(neighbors)) - 1
    assert connected(mask, neighbors) and connected(total ^ mask, neighbors)
    support = sorted(x for x, (u, v) in endpoints.items() if (u in ordinary) != (v in ordinary))
    return {"shore": sorted(ordinary), "bond": support}


def verify_hybrid_swap(f, stages, arms, deck, fixed):
    names = [key for key, *_ in f.edges]
    index = {key: i for i, key in enumerate(names)}
    images = [index[image_key(key)] for key in names]
    local_names = host_names(f, arms)
    assert {local_names[i] for i, k in enumerate(names) if k[0] == "branch"} <= fixed
    mapping = {x: y for key, entries in f.physical.items() for x, y in zip(entries, f.physical[image_key(key)])}
    assert all(mapping.get(x, x) == x for x in fixed)
    flips = defaultdict(set)
    for x, owners in stages[1].owners.items():
        flips[tuple(owners)].add(x)
    groups = {frozenset(c) for c in flips.values()}
    assert {frozenset(mapping.get(x, x) for x in c) for c in groups} == groups

    first = None
    coverage = {}
    for size in (1, 2, 3, 4):
        changes = 0
        for marks in combinations(range(len(names)), size):
            image = tuple(sorted(images[p] for p in marks))
            if marks >= image:
                continue
            if (before := deck.host_K(marks)) != (after := deck.host_K(image)):
                if first is None:
                    first = {"arity": size, "query": [local_names[p] for p in marks],
                             "image": [local_names[p] for p in image], "K": [before, after]}
                    for side, set_, value in (("source", marks, before), ("target", image, after)):
                        if value is not None:
                            _, shore = deck.host.mark(set_)
                            branch_marks = [names[p][-1] for p in set_ if names[p][0] == "branch"]
                            witness = hybrid_lift(f, stages[1], arms, shore, 1, branch_marks)
                            assert len(witness["bond"]) == value and {local_names[p] for p in set_} <= set(witness["bond"])
                            first[side] = witness
                changes += 1
        assert size == 4 or not changes
        coverage[size] = {"queries": comb(len(names), size), "differing_orbits": changes}

    pair = tuple(sorted(index[key] for key in (("spoke", 0), ("spoke", 1))))
    pair_image = tuple(sorted(images[p] for p in pair))
    next_deck = Minimum(deck.compressed_bonds, names, 2)
    next_sizes = []
    for marks in (pair, pair_image):
        size, shore = next_deck.mark(marks)
        witness = hybrid_lift(f, stages[2], arms, shore, 2)
        assert len(witness["bond"]) == size and {local_names[p] for p in marks} <= set(witness["bond"])
        next_sizes.append({"K": size, "literal_marks": [local_names[p] for p in marks], **witness})
    companion = []
    if f.i == 2:
        same_color = tuple(sorted(index[q] for q in (("anchor", 0, 1), ("spoke", 1), ("anchor", 1, 0), ("spoke", 0))))
        for marks in (same_color, tuple(sorted(images[p] for p in same_color))):
            size, shore = deck.host.mark(marks)
            literal = [local_names[p] for p in marks]
            record = {"K": size, "literal_marks": literal}
            if size is not None:
                witness = hybrid_lift(f, stages[1], arms, shore, 1)
                assert len(witness["bond"]) == size and set(literal) <= set(witness["bond"])
                record.update(witness)
            companion.append(record)
    return {"coverage": coverage, "first_discriminating_mark_set": first,
            "companion_quartet": companion,
            "current_marked_pair": [deck.host_K(p) for p in (pair, pair_image)], "next_marked_pair": next_sizes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hybrid", action="store_true")
    parser.add_argument("--hybrid-params", nargs=6, type=int, metavar=("I", "s", "H", "V", "W", "M"))
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    import extend as law

    hybrid = args.hybrid or args.hybrid_params is not None
    f = HybridFixture(*(args.hybrid_params or ())) if hybrid else Fixture(2, 6, 3, 8, True)
    stages, steps = actual_growth(f.archive_supports(), lambda stars: optimized_production_round(stars, law))
    arms = (hybrid_certificates if hybrid else branch_certificates)(f, stages, steps)
    current = stages[1]
    deck = FullMinima(f, current, arms)
    fixed, blocks = pair_classes(current, deck)
    ambiguous = [block for block in blocks if len(block) > 1]
    traits = Counter(tuple(sorted({str(deck.names[column[0]][0]) for column in block})) for block in ambiguous)
    core_only = set(traits) <= {("None",)}
    counts = whole_group_check(current, f, arms, deck, fixed, blocks) if core_only else None
    print(json.dumps({"parameters": f.parameters if hybrid else (2, 6, 3, 3, 8, 8),
                      "stage_sizes": [(len(a.stars), len(a.labels)) for a in stages],
                      "literal_start": [sorted(row) for row in stages[0].stars],
                      "literal_round_additions": [[sorted(row) for row in b.stars[len(a.stars):]] for a, b in zip(stages, stages[1:])],
                      "branch_certificates": arms,
                      "direct_swap": verify_hybrid_swap(f, stages, arms, deck, fixed) if args.hybrid_params else None,
                      "fixed_names": len(fixed), "movable_class_blocks": len(blocks),
                      "movable_column_classes": sum(map(len, blocks)), "local_bonds": deck.local_bonds,
                      "ambiguous_blocks": ambiguous, "ambiguous_block_sizes": dict(Counter(map(len, ambiguous))),
                      "traits": [[tag, value] for tag, value in traits.items()], "full_group": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
