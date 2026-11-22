"""Independent physical replay of ordinary grants and the two registered rivals."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
import gzip
from hashlib import sha256
from inspect import getsourcefile, getsourcelines, signature
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys
from types import MappingProxyType

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAWS = ("parity", "nae")
ARMS = ("ordinary", "one_fewer", "arity_floor")
LIMIT = 8
WORD_CAP = 16
SOURCES = MappingProxyType({
    "isolated_three": ((0, 1, 2),),
    "isolated_four": ((0, 1, 2, 3),),
    "four_exhausted": ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8)),
    "four_spare": ((0, 1, 2, 9), (0, 3, 4), (1, 5, 6), (2, 7, 8)),
    "receiver_three": ((0, 1, 3, 4), (0, 1, 2, 5), (2, 6, 7)),
})


def experiment(scope, name):
    return ROOT / "experiments" / scope / (scope + "-E001_" + name)


FORBIDDING = experiment("FORBIDDING-JOIN-20261120-001B", "free_readings")
ORDINARY = experiment("ORDINARY-DYNAMICS-20261120-001A", "ordinary")
NAE = experiment("NAE-GROWTH-20261119-001B", "nae")
CALIBRATIONS = experiment("CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B", "receivers")


@cache
def archives():
    sys.path.insert(0, str(NAE))
    sys.path.insert(0, str(FORBIDDING))
    sys.path.insert(0, str(ORDINARY))
    sys.path.insert(0, str(ROOT / "tools"))
    import naelib
    import rival_growth
    import end_operator
    from closing_projection import literal_stars

    assert tuple(rival_growth.ARMS) == ARMS
    assert tuple(literal_stars(False)[0]) == SOURCES["four_exhausted"]
    assert tuple(literal_stars(True)[0]) == SOURCES["four_spare"]
    return naelib, rival_growth, end_operator


def incidence(stars):
    owners = defaultdict(list)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stars)))
    for holder, row in enumerate(stars):
        assert len(set(row)) == len(row)
        for name in row:
            owners[name].append(holder)
    for holders in owners.values():
        assert 1 <= len(holders) <= 2
        if len(holders) == 2:
            graph.add_edge(*holders)
    loose = {k: tuple(d for d in row if len(owners[d]) == 1) for k, row in enumerate(stars)}
    return owners, graph, {k: row for k, row in loose.items() if row}


def candidate_groups(blocks, points):
    candidate = nx.Graph()
    candidate.add_nodes_from(points)
    for block in blocks.values():
        candidate.add_edges_from(combinations(sorted(block), 2))
    cliques = [tuple(sorted(g)) for g in nx.find_cliques(candidate) if len(g) >= 2]
    held = {g: tuple(k for k, row in sorted(blocks.items()) if set(g).issubset(row)) for g in cliques}
    big = tuple(sorted(g for g in cliques if len(g) >= 3 and not held[g]))
    covered = {pair for group in big for pair in combinations(group, 2)}
    binary = tuple(sorted(tuple(sorted(e)) for e in candidate.edges if tuple(sorted(e)) not in covered))
    return big + binary, candidate, held


def proposal(stars):
    owners, shared, loose = incidence(stars)
    blocks = {k: row for k in shared if len(row := set(shared[k]).intersection(loose)) >= 2}
    multi, candidate, maximal = candidate_groups(blocks, loose)
    used = Counter(k for row in multi for k in row)
    shortages = tuple((k, used[k] - len(loose[k])) for k in loose if used[k] > len(loose[k]))
    groups = ()
    demands = ()
    status = "closed" if not loose else "stalled" if shortages else "funded"
    if status == "funded":
        groups = multi + tuple((k,) for k in loose for _ in range(len(loose[k]) - used[k]))
        child_lists = defaultdict(set)
        for i, parents in enumerate(groups):
            for k in parents:
                child_lists[k].add(i)
        next_groups, _, _ = candidate_groups(child_lists, range(len(groups)))
        next_uses = Counter(i for row in next_groups for i in row)
        demands = tuple(next_uses[i] for i in range(len(groups)))
    public = {
        "live_and_loose_names": loose,
        "witnessed_sets": {k: sorted(row) for k, row in blocks.items()},
        "candidate_pairs": sorted(tuple(sorted(row)) for row in candidate.edges),
        "maximal_candidate_sets": [{"members": row, "common_witnesses": maximal[row]} for row in sorted(maximal)],
        "multiple_groups": multi, "all_groups_if_funded": groups,
        "multiple_charges": {k: used[k] for k in loose}, "shortages": shortages,
        "status": status, "lookahead_demands": demands,
    }
    return public, owners


def legal(word, width, law):
    return word.bit_count() % 2 == 0 if law == "parity" else word not in (0, (1 << width) - 1)


@cache
def allowed_local(width, law):
    return tuple(word for word in range(1 << width) if legal(word, width, law))


def new_solver(stars, law):
    solver = Minisat22()
    for star in stars:
        if law == "nae":
            for sign in (1, -1):
                solver.add_clause([sign * (d + 1) for d in star])
        else:
            for word in range(1 << len(star)):
                if not legal(word, len(star), law):
                    solver.add_clause([-(d + 1) if (word >> i) & 1 else d + 1 for i, d in enumerate(star)])
    return solver


def exact_projection(solver, names):
    return tuple(word for word in range(1 << len(names))
                 if solver.solve(assumptions=[(d + 1) if word & (1 << i) else -(d + 1) for i, d in enumerate(names)]))


def knot_checks(words, width):
    count = len(words)
    dropped = [len({word & ~(1 << i) for word in words}) for i in range(width)]
    return {"K1_constrained": count < (1 << width),
            "K2_every_single_omission_full": all(n == 1 << (width - 1) for n in dropped),
            "K3_nonempty": count > 0, "one_name_omission_counts": dropped}


@cache
def canonical_local(width, law):
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    names = tuple(map(str, range(width)))
    canonical = allowed_local(width, law)
    assert width >= 3
    rows = frozenset(tuple(bool(word & (1 << i)) for i in range(width)) for word in canonical)
    assert check_knot(Relation(names, rows), names[:-1], names[-1]).is_knot
    return len(rows)


def compact_allowed(stars, law, names):
    name_bit = {d: 1 << i for i, d in enumerate(names)}
    masks = [sum(name_bit[d] for d in row) for row in stars]
    if law == "parity":
        return tuple(word for word in range(1 << len(names))
                     if all((word & mask).bit_count() % 2 == 0 for mask in masks))
    return tuple(word for word in range(1 << len(names))
                 if all((word & mask) not in (0, mask) for mask in masks))


def extension_count(word, paid, count, law):
    if law == "parity":
        return (1 << (count - 1)) if count else int((word & paid).bit_count() % 2 == 0)
    if word & paid not in (0, paid):
        return 1 << count
    return (1 << count) - 1


@cache
def old_word_checks(stars, grown, births, law):
    names = tuple(sorted({d for row in stars for d in row}))
    unfresh = [row for row in births if not row[2] and not row[3]]
    result = {"scope": names, "all_old_words_extend": not unfresh,
              "zero_fresh_nonimplied_holders": [row[0] for row in unfresh]}
    if len(names) > WORD_CAP:
        evidence = {}
        if unfresh:
            holder, inputs, _, _ = unfresh[0]
            with new_solver(stars, law) as before, new_solver(grown, law) as after:
                word = next(w for w in exact_projection(before, inputs) if not legal(w, len(inputs), law))
                pins = [(d + 1) if word & (1 << i) else -(d + 1) for i, d in enumerate(inputs)]
                assert before.solve(assumptions=pins)
                values = {d - 1 for d in before.get_model() if d > 0}
                assert not after.solve(assumptions=[(d + 1) if d in values else -(d + 1) for d in names])
                rejected = sum(1 << i for i, d in enumerate(names) if d in values)
                first_failed = [k for k, row, _, _ in unfresh
                                if not legal(sum((d in values) << i for i, d in enumerate(row)), len(row), law)]
                assert holder in first_failed and after.solve()
                surviving = {d - 1 for d in after.get_model() if d > 0}
                evidence = {"one_rejected_old_word": rejected, "rejection_witnesses": first_failed,
                            "one_surviving_old_word": sum(
                                1 << i for i, d in enumerate(names) if d in surviving)}
        return result | evidence | {"enumerated": False, "allowed_old_count": None, "surviving_old_count": None,
                                    "expanded_count": None, "rejected_old_words": None}

    ways = compact_allowed(stars, law, names)
    bit = {d: 1 << i for i, d in enumerate(names)}
    masks = [(holder, sum(bit[d] for d in inputs), grant) for holder, inputs, grant, _ in births]
    rejected = []
    surviving = 0
    expanded = 0
    for word in ways:
        count = 1
        for _, mask, grant in masks:
            count *= extension_count(word, mask, grant, law)
        surviving += count > 0
        expanded += count
        if not count:
            rejected.append(word)
    assert ways and surviving
    assert (surviving == len(ways)) == result["all_old_words_extend"]
    rejected_set = set(rejected)
    sample = rejected[:1] + [next(w for w in ways if w not in rejected_set)]
    witness_rows = []
    with new_solver(grown, law) as solver:
        witness_words = ways if len(names) <= 15 and unfresh else sample
        possible = set()
        for word in witness_words:
            pins = [(d + 1) if word & bit[d] else -(d + 1) for d in names]
            if solver.solve(assumptions=pins):
                possible.add(word)
                if word in sample:
                    witness_rows.append({"old_word": word, "one_extended_assignment_ones":
                                         sorted(x - 1 for x in solver.get_model() if x > 0)})
        assert possible == set(witness_words).difference(rejected_set)
    first_failed = []
    if rejected:
        first_failed = [k for k, mask, grant in masks if not extension_count(rejected[0], mask, grant, law)]
    return result | {"enumerated": True, "allowed_old_count": len(ways), "surviving_old_count": surviving,
                     "expanded_count": expanded, "rejected_old_words": rejected,
                     "first_rejected_word_failed_new_holders": first_failed, "extension_witnesses": witness_rows}


@cache
def support_projections(stars, law):
    report = []
    with new_solver(stars, law) as solver:
        assert solver.solve()
        for k, names in enumerate(stars):
            words = exact_projection(solver, names)
            report.append({"holder": k, "scope": names, "allowed": words,
                           "whole_canonical_relation": words == allowed_local(len(names), law),
                           **knot_checks(words, len(names))})
            if len(names) >= 3:
                assert canonical_local(len(names), law) == len(allowed_local(len(names), law))
    return report


@cache
def advance(stars, law, arm):
    engine, rival, compact = archives()
    plan, owners = proposal(stars)
    reached, archived = rival.grow(stars, law, arm, engine)
    assert plan["status"] == archived["status"]
    assert dict(plan["shortages"]) == archived.get("shortages", {})
    if nx.is_connected(incidence(stars)[1]):
        literal = compact.step(compact.from_stars(stars), law, max_births=1024)
        assert {"stalled": "stall", "funded": "extend", "closed": "closed"}[plan["status"]] == literal.status
        assert literal.shortages == plan["shortages"]
    else:
        literal = None

    method = {"rule": arm, "status": plan["status"], "stars_before": stars, "proposal": plan,
              "shortages": plan["shortages"], "births": [], "stars_after": stars}
    if reached is None:
        return stars, method | {"old_words": old_word_checks(stars, stars, (), law),
                                "next_funding": {"status": plan["status"], "shortages": plan["shortages"]}}
    births = []
    payment = {k: iter(row) for k, row in plan["live_and_loose_names"].items()}
    with new_solver(stars, law) as solver:
        for i, (old, expected, demand) in enumerate(zip(
                archived["births"], plan["all_groups_if_funded"], plan["lookahead_demands"], strict=True)):
            holder = len(stars) + i
            assert old["knot"] == holder
            paid = tuple((k, next(payment[k])) for k in expected)
            inputs = tuple(d for _, d in paid)
            assert all(owners[d] == [k] for k, d in paid)
            assert dict(paid) == {owners[d][0]: d for d in old["inputs"]}
            assert expected == old["parents"] and demand == old["D"]
            words = exact_projection(solver, inputs)
            implied = all(legal(word, len(inputs), law) for word in words)
            assert implied == old["old_inputs_already_imply_law"]
            q = demand if implied else max(demand, 3 - len(expected), 1)
            floor = max(0, 3 - len(expected))
            grant = q if arm == "ordinary" else min(q, max(floor, q - 1) if arm == "one_fewer" else floor)
            assert (q, grant) == (old["q"], old["f"])
            if literal is not None:
                assert (expected, demand, q, implied) == (literal.parents[i], literal.demand[i],
                                                         literal.fresh[i], literal.implied)
            start = max(owners) + 1 if not births else birth_end
            expected_fresh = tuple(range(start, start + q))
            birth_end = start + q
            assert expected_fresh == old["ordinary_fresh"]
            assert old["fresh"] == expected_fresh[:grant]
            births.append({"holder": holder, "parents": expected, "paid": paid, "consumed_names": inputs,
                           "fresh_names": old["fresh"], "ordinary_fresh_names": expected_fresh,
                           "demand": demand, "ordinary_grant": q, "grant": grant, "implied": implied,
                           "input_projection": words, "input_forgetting_tests": knot_checks(words, len(inputs))})
    assert all(next(row, None) is None for row in payment.values())
    assert reached == stars + tuple(tuple(sorted(b["consumed_names"])) + b["fresh_names"] for b in births)
    new_names = [d for b in births for d in b["fresh_names"]]
    assert len(set(new_names)) == len(new_names) and not set(new_names).intersection(owners)
    after, _ = proposal(reached)
    kept = tuple((b["holder"], b["consumed_names"], b["grant"], b["implied"]) for b in births)
    assert after["status"] == archived["following_funding"]["status"].replace("ready", "funded")
    assert dict(after["shortages"]) == archived["following_funding"]["shortages"]
    return reached, method | {
        "stars_after": reached, "births": births, "old_words": old_word_checks(stars, reached, kept, law),
        "next_funding": {"status": after["status"], "shortages": after["shortages"],
                         "live_and_loose_names": after["live_and_loose_names"],
                         "multiple_groups": after["multiple_groups"]},
    }


def replay_history(stars, law, policy, first_cuts=()):
    known = list(first_cuts)
    for age in range(len(known) + 1, LIMIT + 1):
        stars, cut = advance(stars, law, policy)
        known.append({"age": age, **cut})
        if cut["status"] != "funded":
            break
    return known


def recipient_descendants(keeper, cuts):
    if keeper is None:
        return []
    descendants = {keeper["holder"]}
    output = []
    for cut in cuts:
        if all(b["holder"] != keeper["holder"] for b in cut["births"]) and not output:
            continue
        if output:
            descendants = {b["holder"] for b in cut["births"] if descendants.intersection(b["parents"])}
        living = [b["holder"] for b in cut["births"] if b["grant"] and b["holder"] in descendants]
        other = [b["holder"] for b in cut["births"] if b["grant"] and b["holder"] not in descendants]
        output.append({"age": cut["age"], "status": cut["status"], "new_inclusive_members": sorted(descendants),
                       "continuing_new_members": living, "other_continuing_new_members": other})
    return output


def paid_by_name(cut, scope):
    observed = set(scope)
    return [(b["holder"], k, d) for b in cut["births"] for k, d in b["paid"] if d in observed]


def isolated_bindings(stars, cuts):
    first = {row["consumed_names"][0]: row for row in cuts[0]["births"]}
    old = tuple(stars[0])
    assert len(first) == len(old) and set(first) == set(old)
    xs = tuple(first[u] for u in old)
    idx = {row["holder"]: i for i, row in enumerate(xs)}
    second = {}
    for b in cuts[1]["births"]:
        assert len(b["parents"]) == 2 and set(b["parents"]).issubset(idx)
        i, j = sorted(idx[k] for k in b["parents"])
        second[i, j] = b

    pairs = {}
    for (i, j), b in sorted(second.items()):
        paid = dict(b["paid"])
        pairs[f"B{i}{j}"] = {
            **b, "i": i, "j": j, "x_ij": paid[xs[i]["holder"]], "x_ji": paid[xs[j]["holder"]],
            "y": b["fresh_names"],
        }
    all_round_three = []
    b_side = {b["holder"]: ij for ij, b in second.items()}
    if second and len(cuts) >= 3:
        for b in cuts[2]["births"]:
            if len(b["parents"]) == 3 and set(b["parents"]).issubset(b_side):
                all_round_three.append({**b,
                    "paid_b_labels": [f"B{i}{j}" for i, j in (b_side[k] for k in b["parents"])],
                    "y_paid_from_each_b": {f"B{i}{j}": d for k, d in b["paid"] for i, j in (b_side[k],)},
                })

    keeper = None
    if len(old) == 4:
        designated = {"B12", "B13", "B23"}
        keeper = next((row for row in all_round_three if set(row["paid_b_labels"]) == designated), None)
    else:
        keeper = pairs.get("B01")

    first_focal = xs[0]
    focal_names = first_focal["consumed_names"] + first_focal["fresh_names"]
    focal_history = [{"age": 0, "status": "original", "paid_u_0_holders": [0],
                      "focal_fresh_name_holders": {}, "still_loose_focal_fresh": [],
                      "simultaneous_payments_using_focal_names": [],
                      "next_payments_using_focal_names": paid_by_name(cuts[0], focal_names)}]
    for cut in cuts:
        owned = incidence(cut["stars_after"])[0]
        next_cut = cuts[cut["age"]] if cut["age"] < len(cuts) else None
        record = {"age": cut["age"], "status": cut["status"],
                  "paid_u_0_holders": owned[old[0]],
                  "focal_fresh_name_holders": {d: owned[d] for d in first_focal["fresh_names"]},
                  "still_loose_focal_fresh": [d for d in first_focal["fresh_names"] if len(owned[d]) == 1],
                  "simultaneous_payments_using_focal_names": paid_by_name(cut, focal_names),
                  "next_payments_using_focal_names": [] if next_cut is None else paid_by_name(next_cut, focal_names)}
        focal_history.append(record)

    return {"original_u_names": old, "first_children": {f"F{i}": row for i, row in enumerate(xs)},
            "pair_children": pairs, "ternary_children": all_round_three,
            "selected_keeper": keeper, "keeper_descendants": recipient_descendants(keeper, cuts),
            "focal_access": focal_history, "archived_J_physical_names": [row["fresh_names"][0] for row in xs[:2]]
            if len(old) == 3 else [],
            "same_cut_earlier_paid_names_of_sibling_only_triple": sorted(
                d for key in ("B12", "B13", "B23") for d in pairs[key]["consumed_names"]) if len(old) == 4 and pairs else []}


def focal_recodings(history):
    """Transport all four sibling origins through their complete ordinary finite history."""
    physical = history["physical_bindings"]
    first_layer = physical["first_children"]
    cuts = history["cuts"]
    source_names = physical["original_u_names"]
    transports = []
    for shift in range(4):
        holders = {0: 0}
        transport = {d: source_names[(i + shift) % 4] for i, d in enumerate(source_names)}
        for cut in cuts:
            grouped = defaultdict(list)
            for b in cut["births"]:
                grouped[b["parents"]].append(b)
            for parents, group in grouped.items():
                target_parents = tuple(sorted(holders[k] for k in parents))
                choices = list(grouped[target_parents])
                assert len(group) == len(choices)
                for old in group:
                    fixed_paid = {holders[k]: transport[d] for k, d in old["paid"] if d in transport}
                    new = next(candidate for candidate in choices
                               if fixed_paid.items() <= dict(candidate["paid"]).items())
                    choices.remove(new)
                    holders[old["holder"]] = new["holder"]
                    assert (old["demand"], old["grant"], old["implied"]) == (new["demand"], new["grant"], new["implied"])
                    target_paid = dict(new["paid"])
                    for k, d in old["paid"]:
                        target = target_paid[holders[k]]
                        assert d not in transport or transport[d] == target
                        transport[d] = target
        final = cuts[-1]["stars_after"]
        for old, new in holders.items():
            unmapped = set(final[old]).difference(transport)
            remaining = set(final[new]).difference(transport[d] for d in final[old] if d in transport)
            transport.update(zip(sorted(unmapped), sorted(remaining), strict=True))
        assert len(set(transport.values())) == len(transport)
        assert len(set(holders.values())) == len(final)
        for old, new in holders.items():
            assert {transport[d] for d in final[old]} == set(final[new])
        focal = first_layer["F0"]["holder"]
        assert holders[focal] == first_layer[f"F{shift}"]["holder"]
        transports.append({"image_of_F0": holders[focal], "image_original_index": shift,
                           "holder_transport": sorted(holders.items()), "name_transport": sorted(transport.items())})
    return transports


def archived_pair_control(hist):
    first = hist["physical_bindings"]["first_children"]
    keeper = hist["physical_bindings"]["selected_keeper"]
    current = hist["cuts"][0]["stars_after"]
    old_names = tuple(sorted(incidence(current)[0]))
    assigned = tuple(first[f"F{i}"]["fresh_names"][0] for i in (0, 1))
    assert assigned == keeper["consumed_names"]
    alternatives = []
    for offered in product(*(first[f"F{i}"]["fresh_names"] for i in (0, 1))):
        changed = sum(d in keeper["consumed_names"] for d in offered)
        alternatives.append({"changed_fresh_names": offered, "keeper_paid_names_changed": changed,
                             "required_parity_change_of_keeper_fresh_value": changed % 2})
    word_support = (0, 1, *assigned)
    other = sum(1 << old_names.index(d) for d in word_support)
    assert all(w in compact_allowed(current, "parity", old_names) for w in (0, other))
    return {"archived_placement": assigned, "focal_binary": keeper, "literal_options": alternatives,
            "fixed_presentation_two_legal_old_words": {"scope": old_names, "words": [0, other],
                                                        "different_names": word_support},
            "keeper_parity_table": allowed_local(3, "parity")}


def closing_bindings(cuts):
    core = [b for b in cuts[0]["births"] if len(b["parents"]) == 2]
    spare = next((b for b in cuts[0]["births"] if b["parents"] == (0,)), None)
    parent_ids = {b["holder"] for b in core}
    keeper, = (b for b in cuts[1]["births"] if set(b["parents"]) == parent_ids)
    return {"first_leaf_pairs": core, "spare_child": spare, "triple_child": keeper,
            "other_simultaneous_births": [b for b in cuts[1]["births"] if b["holder"] != keeper["holder"]],
            "triple_descendants": recipient_descendants(keeper, cuts)}


def receiver_bindings(stars, cuts):
    owners, shared, _ = incidence(stars)
    double_name_pair, = (pair for pair, n in Counter(tuple(v) for v in owners.values() if len(v) == 2).items() if n == 2)
    a, = (k for k in double_name_pair if shared.degree(k) == 1)
    w, = (k for k in double_name_pair if k != a)
    c, = set(shared[w]) - {a}
    pure, receiver = a, c
    out = []
    for cut in cuts:
        targets = (pure, receiver)
        neighbors = [other for pair in cut["proposal"]["candidate_pairs"] if pure in pair
                    for other in pair if other != pure]
        assert neighbors == [receiver]
        if cut["status"] != "funded":
            out.append({"age": cut["age"], "status": cut["status"], "prior_pure": pure, "prior_receiver": receiver,
                        "target_parent_set": tuple(sorted(targets)), "shortages": cut["shortages"]})
            break
        child, = (b for b in cut["births"] if set(b["parents"]) == set(targets))
        new_pure, = (b for b in cut["births"] if b["parents"] == (pure,))
        out.append({"age": cut["age"], "status": cut["status"], "prior_pure": pure, "prior_receiver": receiver,
                    "body": child, "pure_successor": new_pure, "outside_paid_name": dict(child["paid"])[pure]})
        pure, receiver = new_pure["holder"], child["holder"]
    return {"original_roles": {"A": a, "W": w, "C": c}, "receipts": out}


def raw_history(case, stars, cuts):
    if case.startswith("isolated_"):
        physical = isolated_bindings(stars, cuts)
    elif case.startswith("four_"):
        physical = closing_bindings(cuts)
    else:
        physical = receiver_bindings(stars, cuts)
    totals = [len(cut["births"]) for cut in cuts if cut["status"] == "funded"]
    return {"cuts": cuts, "physical_bindings": physical, "paid_birth_counts": totals,
            "terminal_status": cuts[-1]["status"] if cuts[-1]["status"] != "funded" else cuts[-1]["next_funding"]["status"],
            "last_paid_age": len(totals)}


def recode(cuts, law, seed):
    """Re-run the policies anonymously and check the coherent prior name allocation."""
    engine, rival, _ = archives()
    final = cuts[-1]["stars_after"]
    names = sorted(incidence(final)[0])
    rng = Random(seed)
    word_names = dict(zip(names, rng.sample(range(len(names) + 100, 4 * len(names) + 100), len(names)), strict=True))
    perm = list(range(len(final)))
    rng.shuffle(perm)
    position = {holder: i for i, holder in enumerate(perm)}
    compared = 0
    for cut in cuts:
        order = sorted(range(len(cut["stars_before"])), key=position.__getitem__)
        index = {holder: i for i, holder in enumerate(order)}
        source = tuple(tuple(word_names[d] for d in cut["stars_before"][k]) for k in order)
        forecast, owners = proposal(source)
        _, archive = rival.grow(source, law, cut["rule"], engine)
        assert forecast["status"] == cut["status"] == archive["status"]
        assert {order[k]: n for k, n in forecast["shortages"]} == dict(cut["shortages"])
        got = Counter((tuple(sorted(order[k] for k in b["parents"])), b["D"], b["q"], b["f"],
                       b["old_inputs_already_imply_law"]) for b in archive.get("births", ()))
        want = Counter((b["parents"], b["demand"], b["ordinary_grant"], b["grant"], b["implied"]) for b in cut["births"])
        assert got == want
        with new_solver(source, law) as prior:
            for b in cut["births"]:
                encoded_names = tuple(word_names[d] for d in b["consumed_names"])
                assert tuple(owners[d][0] for d in encoded_names) == tuple(index[k] for k in b["parents"])
                assert all(len(owners[d]) == 1 for d in encoded_names)
                assert exact_projection(prior, encoded_names) == b["input_projection"]
        transformed_after = tuple(tuple(word_names[d] for d in row) for row in cut["stars_after"])
        new_owners = incidence(transformed_after)[0]
        for b in cut["births"]:
            assert all(new_owners[word_names[d]] == [k, b["holder"]] for k, d in b["paid"])
            assert all(new_owners[word_names[d]] == [b["holder"]] for d in b["fresh_names"])
        compared += len(cut["births"])
    return {"seed": seed, "renamed_to_original_holder": perm, "original_to_renamed_name": sorted(word_names.items()),
            "replayed_paid_births": compared}


def assemble(case, index, recodings):
    stars = SOURCES[case]
    laws = {}
    for law_index, law in enumerate(LAWS):
        source_legality = support_projections(stars, law)
        assert all(row["whole_canonical_relation"] for row in source_legality)
        pol = {policy: replay_history(stars, law, policy) for policy in ARMS}
        for prefix, age in (("ordinary_first", 1), ("ordinary_second", 2)):
            if age > 1 and case != "isolated_four":
                continue
            reference = pol["ordinary"][:age]
            for policy in ARMS[1:]:
                pol[f"{prefix}__{policy}"] = replay_history(reference[-1]["stars_after"], law, policy, reference)
        histories = {}
        for j, (key, cuts) in enumerate(pol.items()):
            history = raw_history(case, stars, cuts)
            history["support_projections_at_first_two_reached_cuts"] = {
                row["age"]: support_projections(row["stars_after"], law) for row in cuts[:2] if row["status"] == "funded"}
            seeds = tuple(202611222601 + i * 10000 + index * 1000 + law_index * 100 + j
                          for i in range(4 if case == "isolated_four" and key == "ordinary" else 2))
            history["coherent_recodings"] = [recode(cuts, law, seed) for seed in seeds] if recodings else []
            histories[key] = history
        laws[law] = {"original_support_projections": source_legality, "histories": histories}
        if case == "isolated_four":
            laws[law]["actual_focal_role_transports"] = focal_recodings(histories["ordinary"])
        if case == "isolated_three" and law == "parity":
            laws[law]["archived_pair_control"] = archived_pair_control(histories["ordinary"])
    return {"original_stars": stars, "laws": laws}


def operator_sources():
    legacy, rival, compact = archives()
    functions = [
        (legacy.F.Presentation.step, "Holding incidence, present roster, full charges, simultaneous commit and lookahead."),
        (legacy.F.Presentation.loose, "One-holder names in the past physical stars."),
        (legacy.J.fastlib.groups_among, "Candidate groups from common physical witnesses."),
        (legacy.S.gf2, "Row-span implication on the entire old parity relation."),
        (legacy.nae_rule, "Failure of both uniform assignments as existence questions on the entire old not-all-equal relation."),
        (legacy.F.fewest, "Uses its planned demand, parent count and implication flag."),
        (compact.step, "Complete connected parity exhaustion and structural funding."),
        (rival.cut, "Grant cap from ordinary grant and parent count."),
        (rival.grow, "Ordinary scratch roster, tracked names and a new funding test from actual truncated holdings."),
    ]
    paths = []
    for function, observation in functions:
        first = getsourcelines(function)[1]
        paths.append({"symbol": function.__qualname__, "source": str(Path(getsourcefile(function)).relative_to(ROOT)),
                      "line": first, "arguments": str(signature(function)), "policy_input": observation})
    return paths


def input_hashes():
    receipt = HERE / "advisor_receipt.json"
    approved = next(item for item in json.loads(receipt.read_bytes())["records"] if item["verdict"] == "approved")
    design = HERE / "preregistration.md"
    assert sha256(design.read_bytes()).hexdigest() == approved["sha256"]
    legacy, _, _ = archives()
    dependencies = [
        Path(__file__), receipt, design, ROOT / approved["candidate_path"], FORBIDDING / "rival_growth.py",
        ORDINARY / "end_operator.py", ORDINARY / "closing_projection.py", CALIBRATIONS / "controls.py",
        Path(legacy.__file__), Path(legacy.J.__file__), Path(legacy.J.fastlib.__file__),
        Path(legacy.S.__file__), Path(legacy.F.__file__),
        ROOT / "research/SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001A/controls.py",
        ROOT / "research/NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001A/physical.py",
    ]
    return {str(path.resolve().relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in dependencies}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "native.json.gz")
    args = parser.parse_args()
    bound = input_hashes()
    cases = {case: assemble(case, i, recodings=True) for i, case in enumerate(SOURCES)}
    record = {"schema": "b256-native-v1", "cases": cases, "last_attempted_age": LIMIT,
              "complete_old_word_name_cap": WORD_CAP, "source_hashes_sha256": bound,
              "operator_sources": operator_sources()}
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    scratch = args.output.with_suffix(".tmp")
    scratch.write_bytes(gzip.compress(payload, mtime=0))
    scratch.replace(args.output)
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
