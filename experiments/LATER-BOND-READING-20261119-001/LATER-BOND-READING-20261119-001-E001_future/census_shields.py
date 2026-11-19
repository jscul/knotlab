"""Exact weighted split-hub sweep and literal growth replay for the shield family."""

from argparse import ArgumentParser
from collections import Counter
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path
import json
import sys

from census_interfaces import ROOT, PRIOR, VERIFY, load, literal_start, branch_membership, separating_cut, separating_cost


SHIELDS = range(1, 4)
ANCHORS = range(1, 5)
ARM = range(1, 9)
BRANCH = (2, 3)
FOCUSED = (range(1, 5), range(1, 9), range(1, 9), range(2, 19))
SITE_CAP = 328


@cache
def geometry(anchors, shields):
    """Return bundle endpoints and the involution interchanging two mids."""
    v = 6
    first_shield = v + anchors
    outside = first_shield + 2 * shields
    # Fixed hubs 0,1, ordinary mids 2–5, and distinguished anchor v.
    edges, types = [], []

    def add(a, b, kind):
        edges.append((a, b))
        types.append(kind)

    for mid in range(2, 6):
        add((mid - 2) // 2, mid, "arm")
        for anchor in range(v, first_shield):
            add(mid, anchor, "arm" if anchor == v else "unit")
    ports = list(range(first_shield, outside))
    for j, site in enumerate(ports):
        add(j // shields, site, "hub")
        for anchor in range(v, first_shield):
            add(site, anchor, "unit")
    ordinary = len(edges)
    for site in ports:
        add(site, outside, "branch")
    labels = {frozenset(e): i for i, e in enumerate(edges)}
    image = list(range(len(edges)))
    for i, (a, b) in enumerate(edges):
        if a == 2 and b >= v:
            image[i] = labels[frozenset((4, b))]
        elif a == 4 and b >= v:
            image[i] = labels[frozenset((2, b))]
    x = labels[frozenset((0, 2))]
    y = labels[frozenset((1, 4))]
    image[x], image[y] = y, x
    assert all(image[image[i]] == i and types[image[i]] == types[i] for i in range(len(edges)))
    return {"ordinary_sites": outside, "edges": edges, "types": types, "image": image, "ports": ports,
            "ordinary_bundles": ordinary, "selected_pair": (x, labels[frozenset((0, 3))])}


def members(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def connected(side, adjacent):
    pending = seen = side & -side
    while pending:
        bit = pending & -pending
        pending ^= bit
        new = adjacent[bit.bit_length() - 1] & side & ~seen
        pending |= new
        seen |= new
    return seen == side


def symmetry_groups(anchors, shields):
    first = 6 + anchors
    return (tuple(range(7, first)), tuple(range(first, first + shields)),
            tuple(range(first + shields, first + 2 * shields)))


def representatives(anchors, shields, order):
    # A comparison moving anything must mark an ordinary arm or spoke.
    # Up to order - 1 other marks can select shield sites of each color.
    symmetry = symmetry_groups(anchors, shields)
    selected = (order, order - 1, order - 1)
    return tuple(group[count:] for group, count in zip(symmetry, selected, strict=True))


@cache
def bonds_for(anchors, shields, order=3, quotient=True):
    core = geometry(anchors, shields)
    n = core["ordinary_sites"] + 1
    adjacent, stars = [0] * n, [0] * n
    kind_masks = dict.fromkeys(("unit", "arm", "hub", "branch"), 0)
    for j, ((a, b), kind) in enumerate(zip(core["edges"], core["types"], strict=True)):
        adjacent[a] |= 1 << b
        adjacent[b] |= 1 << a
        stars[a] |= 1 << j
        stars[b] |= 1 << j
        kind_masks[kind] |= 1 << j
    total = (1 << n) - 1
    if not all(connected(total ^ (1 << j), adjacent) for j in range(n)):
        return ()
    tails = representatives(anchors, shields, order) if quotient else ()
    unfixed = {u for group in tails for u in group}
    heads = [u for u in range(n - 1) if u not in unfixed]
    tail_options = []
    for group in tails:
        options = [(0, 0)]
        for u in group:
            side, cut = options[-1]
            options.append((side | (1 << u), cut ^ stars[u]))
        tail_options.append(options)
    completions = [(sum(side for side, _ in groups), xor_cuts(groups)) for groups in product(*tail_options)]
    side = cut = 0
    out = []
    for step in range(1 << len(heads)):
        if step:
            changed = heads[(step & -step).bit_length() - 1]
            side ^= 1 << changed
            cut ^= stars[changed]
        for extra_side, extra_cut in completions:
            full_side = side | extra_side
            if full_side and connected(full_side, adjacent) and connected(total ^ full_side, adjacent):
                word = cut ^ extra_cut
                counts = tuple((word & mask).bit_count() for mask in kind_masks.values())
                out.append((word, counts, full_side))
    return tuple(out)


def xor_cuts(sides):
    word = 0
    for _, cut in sides:
        word ^= cut
    return word


def cost(bond, arm, hub, branch):
    _, (u, a, h, b), _ = bond
    return u + arm * a + hub * h + branch * b


def weight_data(core, bonds, arm, hub, branch, labels):
    ordered = sorted((cost(b, arm, hub, branch), b[0], b[2]) for b in bonds)
    observed = sum(1 << b for b in labels)
    occurrences = [bytearray((len(ordered) + 7) // 8) for _ in core["edges"]]
    for j, (_, cut, _) in enumerate(ordered):
        for b in members(cut & observed):
            occurrences[b][j >> 3] |= 1 << (j & 7)
    return ordered, tuple(int.from_bytes(b, "little") for b in occurrences)


def minimum(data, marks):
    ordered, columns = data
    options = columns[marks[0]]
    for b in marks[1:]:
        options &= columns[b]
    return ordered[(options & -options).bit_length() - 1] if options else (None, 0, 0)


def direct_minimum(bonds, marks, arm, hub, branch):
    word = sum(1 << b for b in marks)
    return min(((cost(b, arm, hub, branch), b[0], b[2]) for b in bonds if b[0] & word == word),
               default=(None, 0, 0))


def difference(data, image, size, labels=None):
    tested = 0
    for marks in combinations(range(len(image)) if labels is None else labels, size):
        transported = tuple(sorted(image[b] for b in marks))
        if marks >= transported:
            continue
        tested += 1
        left, right = minimum(data, marks), minimum(data, transported)
        if left[0] != right[0]:
            return {"marks": marks, "image": transported, "cardinalities": [left[0], right[0]],
                    "bonds": [list(members(left[1])), list(members(right[1]))], "ordinary_shores": [left[2], right[2]]}, tested
    return None, tested


def mark_pool(core, anchors, shields, order):
    omitted = {u for group in representatives(anchors, shields, order) for u in group}
    return [b for b, edge in enumerate(core["edges"]) if omitted.isdisjoint(edge)]


def signatures(bonds, marks):
    mask = sum(1 << b for b in marks)
    return {counts for word, counts, _ in bonds if word & mask == mask}


def scalar(values, arm, branch, next_branch):
    return min((u + arm * a + branch * h + next_branch * b for u, a, h, b in values), default=None)


def legal(core, arm, branch):
    arity = Counter()
    for edge, kind in zip(core["edges"], core["types"], strict=True):
        count = {"unit": 1, "arm": arm, "hub": branch, "branch": branch}[kind]
        for holder in edge:
            arity[holder] += count
    return min(arity.values()) >= 3


def current_sites(core, shields, branch):
    sizes = {2: 7, 3: 6}
    return core["ordinary_sites"] + 2 * shields * sizes.get(branch, 2 * branch + 1)


def scan(anchor_values=ANCHORS, shield_values=SHIELDS, arm_values=ARM, branch_values=BRANCH, site_cap=328):
    totals = Counter()
    hits = []
    for i, s in product(anchor_values, shield_values):
        core = geometry(i, s)
        bonds = bonds_for(i, s)
        if not bonds:
            continue
        totals["attachment_geometries"] += 1
        p = core["selected_pair"]
        q = tuple(sorted(core["image"][b] for b in p))
        a, b = p
        lookup = {frozenset(e): j for j, e in enumerate(core["edges"])}
        port = core["ports"]
        first_hub = lookup[frozenset((0, port[0]))]
        fixed_pairs = [p, (a, first_hub)]
        fixed_triples = [(a, b, first_hub)]
        if s >= 2:
            second_hub = lookup[frozenset((0, port[1]))]
            fixed_triples.append((a, first_hub, second_hub))
        seed = [(marks, signatures(bonds, marks), signatures(bonds, (core["image"][v] for v in marks)))
                for marks in (*fixed_pairs, *fixed_triples)]
        pool = mark_pool(core, i, s, 3)
        for arm, branch in product(arm_values, branch_values):
            totals["parameter_choices"] += 1
            if current_sites(core, s, branch) > site_cap:
                totals["outside_current_size_cap"] += 1
                continue
            if not legal(core, arm, branch):
                continue
            totals["admissible_starts"] += 1
            if scalar(seed[0][1], arm, branch, 1) == scalar(seed[0][2], arm, branch, 1):
                continue
            totals["future_named_old_pair_changes"] += 1
            cheap = next((len(marks) for marks, left, right in seed
                          if scalar(left, arm, branch, branch) != scalar(right, arm, branch, branch)), None)
            if cheap:
                totals[f"rejected_by_fixed_order_{cheap}_probe"] += 1
                continue
            present = weight_data(core, bonds, arm, branch, branch, pool)
            comparisons = {}
            for size in (1, 2, 3):
                failure, comparisons[size] = difference(present, core["image"], size, pool)
                if failure:
                    totals[f"rejected_at_order_{size}"] += 1
                    break
            else:
                totals["current_triple_preservers"] += 1
                before, after = (direct_minimum(bonds, x, arm, branch, 1) for x in (p, q))
                positive = [minimum(present, x) for x in (p, q)]
                hit = {"anchors": i, "shields_per_hub": s, "arm_multiplicity": arm, "branch_kind": branch,
                       "current_cut_representatives": len(bonds), "current_comparisons_by_order": comparisons,
                       "current_pair_cardinalities": [x[0] for x in positive],
                       "current_pair_shores": [x[2] for x in positive],
                       "later_pair": {"marks": p, "image": q, "cardinalities": [before[0], after[0]],
                                      "ordinary_shores": [before[2], after[2]],
                                      "bonds": [list(members(before[1])), list(members(after[1]))]}}
                hits.append(hit)
        bonds_for.cache_clear()
    return totals, hits


def middle_image(core, permutation):
    moved = dict(zip(range(2, 6), permutation, strict=True))
    bundles = {frozenset(edge): b for b, edge in enumerate(core["edges"])}
    result = []
    for u, v in core["edges"]:
        if u < 2 and v in moved:
            v = moved[v]
            u = (v - 2) // 2
        else:
            u, v = moved.get(u, u), moved.get(v, v)
        result.append(bundles[frozenset((u, v))])
    return result


def order_four_check(hit):
    i, s, arm, branch = (hit[key] for key in ("anchors", "shields_per_hub", "arm_multiplicity", "branch_kind"))
    core = geometry(i, s)
    pool = mark_pool(core, i, s, 4)
    measurement = weight_data(core, bonds_for(i, s, 4), arm, branch, branch, pool)
    mismatch, checked = difference(measurement, core["image"], 4, pool)
    # The two within-color swaps are physical automorphisms. Together with
    # the current three-way cross-color swap they generate S4. Their group
    # has three double cosets in S4: within, whole-color swap, and mixed.
    within = [p for p in permutations(range(2, 6)) if set(p[:2]) == {2, 3}]
    whole = (4, 5, 2, 3)
    cross = (4, 3, 2, 5)
    assert middle_image(core, cross) == core["image"] and mismatch is not None
    whole_image = middle_image(core, whole)
    other, whole_checked = difference(measurement, whole_image, 4, pool)
    all_order_three = list(permutations(range(2, 6)))
    cosets = []
    for p in ((2, 3, 4, 5), whole, cross):
        images = {tuple(a[p[b[j] - 2] - 2] for j in range(4)) for a, b in product(within, repeat=2)}
        cosets.append(images)
    assert [len(group) for group in cosets] == [4, 4, 16] and len(set.union(*cosets)) == 24
    order_four = sorted(cosets[0] if other is not None else cosets[0] | cosets[1])
    return {"first_difference": mismatch, "entries_checked": checked,
            "whole_color_exchange": {"middle_image": whole, "first_difference": other, "entries_checked": whole_checked},
            "middle_group": {"domain": [2, 3, 4, 5], "through_three": all_order_three, "through_four": order_four,
                             "double_coset_sizes": [len(group) for group in cosets]}}


def direct_check(hit):
    """Repeat the smallest witness with every shore and every marking present."""
    i, s, arm, branch = (hit[key] for key in ("anchors", "shields_per_hub", "arm_multiplicity", "branch_kind"))
    core = geometry(i, s)
    bonds = bonds_for(i, s, quotient=False)
    all_names = range(len(core["edges"]))
    current = weight_data(core, bonds, arm, branch, branch, all_names)
    counts = []
    for r in (1, 2, 3):
        mismatch, checked = difference(current, core["image"], r)
        assert mismatch is None
        counts.append(checked)
    pair = hit["later_pair"]
    later = [direct_minimum(bonds, names, arm, branch, 1)[0] for names in (pair["marks"], pair["image"])]
    assert later == pair["cardinalities"]
    fourth = hit["order_four"]["first_difference"]
    assert fourth and [minimum(current, names)[0] for names in (fourth["marks"], fourth["image"])] == fourth["cardinalities"]
    whole = hit["order_four"]["whole_color_exchange"]["first_difference"]
    if whole:
        assert [minimum(current, names)[0] for names in (whole["marks"], whole["image"])] == whole["cardinalities"]
    return {"ordinary_shores_examined": (1 << core["ordinary_sites"]) - 1, "connected_cuts": len(bonds),
            "comparisons_by_order_1_2_3": counts, "later_cardinalities": later,
            "current_fourth_cardinalities": fourth["cardinalities"]}


def physical_start(hit):
    core = geometry(hit["anchors"], hit["shields_per_hub"])
    arm, branch = hit["arm_multiplicity"], hit["branch_kind"]
    linear = {"unit": 1, "arm": arm, "hub": branch}
    edges, copies = [], []
    for edge, kind in zip(core["edges"], core["types"], strict=True):
        if kind == "branch":
            break
        copies.append(tuple(range(len(edges), len(edges) + linear[kind])))
        edges.extend([edge] * linear[kind])
    fixture = {"edges": edges, "ordinary_junctions": core["ordinary_sites"], "ports": core["ports"]}
    if branch < 4:
        start = literal_start(fixture, [branch] * len(core["ports"]))
    else:
        start = [[] for _ in range(core["ordinary_sites"])]
        label = 0

        def add(*sites):
            nonlocal label
            for site in sites:
                start[site].append(label)
            label += 1

        for edge in edges:
            add(*edge)
        for hub in fixture["ports"]:
            first = len(start)
            live = range(first, first + branch)
            u, v, special = first + 1, first + 2, first + branch
            start.extend([] for _ in range(branch + 1))
            for i, site in enumerate(live):
                add(hub, site)
                if i >= 3:
                    add(site, u if i % 2 else v)
                for _ in range(2 if i else branch - 1):
                    add(site)
            add(u, v)
            add(u, special)
            add(v, special)
            add(special)
    movable = tuple(p for i in range(len(copies)) for p in copies[core["image"][i]])
    return fixture, start, copies, movable


def literal_replay(hit):
    verify = load(VERIFY / "verify.py", "shield_verify")
    prior = load(PRIOR / "census.py", "prior_census")
    law = prior.production_law()
    fixture, start, copies, movable = physical_start(hit)
    state = law.from_junctions(start)
    stages = [verify.Arrangement.parse(start)]
    for _ in range(3):
        record = state.step(law.gf2(law.F.fewest), None)
        assert record is not None and record["new"] and state.implied_mismatch == 0
        stage = verify.Arrangement.parse([sorted(row) for row in state.bits_of])
        verify.round_replay(stages[-1], stage)
        stages.append(stage)
    assert all(verify.start_audit(stage)["census_open_legal"] for stage in stages)
    branch = hit["branch_kind"]
    diagnostics = []
    for age, stage in enumerate(stages):
        ends, _, outside = stage.holder_graph()
        membership = branch_membership(stage, fixture)
        capacities = [separating_cost([edge for edge in ends.values() if membership[hub].intersection(edge)], hub, outside)
                      for hub in fixture["ports"]]
        assert set(capacities) == {branch if age < 2 else 1}
        image = movable + tuple(range(len(movable), len(stage.labels)))
        assert all(image[b] == b for s in stage.live for b in stage.stars[s])
        basis = verify.linear_basis(stage.masks)
        changed = tuple(sorted(image[b] for b in stage.stars[0]))
        word = sum(stage.label_bits[b] for b in changed)
        assert verify.reduce_word(word, basis)
        owner_classes = {}
        for b, holder in stage.owners.items():
            owner_classes.setdefault(tuple(holder), set()).add(b)
        same_holders = {frozenset(names) for names in owner_classes.values()}
        assert {frozenset(image[b] for b in names) for names in same_holders} == same_holders
        diagnostics.append({"age": age, "junctions": len(stage.stars), "distinctions": len(stage.labels),
                            "terminal_capacities": capacities, "largest_arity": max(map(len, stage.stars)),
                            "changed_h0_support": changed})
    core = geometry(hit["anchors"], hit["shields_per_hub"])
    bundle_of = {frozenset(e): j for j, e in enumerate(core["edges"][:len(copies)])}
    cycle = [copies[bundle_of[frozenset(pair)]][0] for pair in ((0, 2), (2, 6), (6, 3), (3, 0))]
    for age, stage in enumerate(stages):
        assert all(len(set(cycle).intersection(row)) % 2 == 0 for row in stage.stars)
        assert len(set(cycle).intersection(diagnostics[age]["changed_h0_support"])) == 1

    later = hit["later_pair"]
    selected = [[copies[i][0] for i in marks] for marks in (later["marks"], later["image"])]
    lifts = []
    for age, shores, costs in ((1, hit["current_pair_shores"], hit["current_pair_cardinalities"]),
                               (2, later["ordinary_shores"], later["cardinalities"])):
        stage = stages[age]
        row = [lift_bond(stage, fixture, shore, verify) for shore in shores]
        assert [len(word) for word in row] == costs
        assert all(set(marks) <= set(word) for marks, word in zip(selected, row, strict=True))
        lifts.append({"age": age, "literal_minimizing_bonds": row})
    fourth = hit["order_four"]["first_difference"]
    physical_fourth = None
    if fourth and max(fourth["marks"] + fourth["image"]) < len(copies):
        marks = [[copies[i][0] for i in terms] for terms in (fourth["marks"], fourth["image"])]
        words = [None if k is None else lift_bond(stages[1], fixture, side, verify)
                 for k, side in zip(fourth["cardinalities"], fourth["ordinary_shores"], strict=True)]
        assert [None if word is None else len(word) for word in words] == fourth["cardinalities"]
        assert all(word is None or set(terms) <= set(word) for terms, word in zip(marks, words, strict=True))
        physical_fourth = {"markings": marks, "cardinalities": fourth["cardinalities"], "literal_minimizing_bonds": words}
    return {"core_bundles": copies, "physical_permutation_of_core_prefix": movable,
            "compressed_core": core,
            "literal_stages": [[sorted(s) for s in stage.stars] for stage in stages], "checks": diagnostics,
            "named_physical_old_pair": selected[0], "image_of_physical_old_pair": selected[1],
            "allowed_difference_witness": cycle, "selected_pair_bond_lifts": lifts, "physical_fourth": physical_fourth}


def lift_bond(stage, fixture, core_shore, verify):
    ends, adjacent, outside = stage.holder_graph()
    branches = branch_membership(stage, fixture)
    inside = set(members(core_shore))
    for hub in inside.copy().intersection(branches):
        sites = branches[hub]
        related = [edge for edge in ends.values() if sites.intersection(edge)]
        _, branch_shore = separating_cut(related, hub, outside)
        inside.update(branch_shore)
    mask = sum(1 << v for v in inside)
    assert verify.connected(mask, adjacent) and verify.connected(((1 << len(adjacent)) - 1) ^ mask, adjacent)
    return sorted(b for b, (a, c) in ends.items() if (a in inside) != (c in inside))


def cases():
    for i, s in product(*FOCUSED[:2]):
        yield f"anchors{i}-shields{s}", [i, s]


def run(case_id, payload):
    i, s = payload
    totals, hits = scan([i], [s], *FOCUSED[2:], site_cap=SITE_CAP)
    return {"counts": totals, "hits": hits}


def one_anchor_check():
    checks = []
    for s in FOCUSED[1]:
        core = geometry(1, s)
        a = core["selected_pair"][0]
        z = core["ports"][0]
        bundles = {frozenset(edge): b for b, edge in enumerate(core["edges"])}
        marks = (a, bundles[frozenset((0, z))], bundles[frozenset((z, 6))])
        transported = tuple(sorted(core["image"][b] for b in marks))
        bonds = bonds_for(1, s)
        assert not signatures(bonds, marks)
        constructive_shore = sum(1 << v for v in (0, 2, 3, 4, 6))
        witness = next(cut for cut, _, shore in bonds if shore == constructive_shore)
        assert all(witness & (1 << b) for b in transported)
        checks.append({"shields_per_hub": s, "old_triple": marks, "image": transported,
                       "old_triple_has_no_bond": True, "image_shore": list(members(constructive_shore))})
        bonds_for.cache_clear()
    return checks


def evidence(path):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results
    shards = load_results(path)
    assert set(shards) == {name for name, _ in cases()} and all(value["status"] == "ok" for value in shards.values())
    anchors, shields, arms, branches = FOCUSED
    totals, hits = Counter(), []
    for name, _ in cases():
        row = shards[name]["result"]
        totals.update(row["counts"])
        hits.extend(row["hits"])
    assert totals["parameter_choices"] == len(anchors) * len(shields) * len(arms) * len(branches)
    small, small_hits = scan()
    assert not small_hits
    for hit in hits:
        fixture, start, _, _ = physical_start(hit)
        hit["starting_size"] = [len(start), max(b for row in start for b in row) + 1]
        branch_count = len(fixture["ports"])
        branch = hit["branch_kind"]
        hit["current_size"] = [len(start) + branch_count * branch, hit["starting_size"][1] + branch_count * branch]
    hits.sort(key=lambda h: (h["current_size"], h["starting_size"], h["arm_multiplicity"], h["branch_kind"]))
    if hits:
        hits[0]["order_four"] = order_four_check(hits[0])
    return {"freeze": "9d6a0f5b8", "bounds": {"anchors": list(anchors), "shields_per_hub": list(shields),
                                              "arm_multiplicities": list(arms), "branch_kinds": list(branches),
                                              "marked_current_site_cap": SITE_CAP},
            "counts": totals, "small_rectangle_counts": small, "all_hits": hits,
            "least_by_current_size": literal_replay(hits[0]) if hits else None,
            "least_witness_without_quotient": direct_check(hits[0]) if hits else None,
            "one_anchor_checks": one_anchor_check()}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    print(json.dumps(evidence(parser.parse_args().run), indent=2))
