"""Check fused and delayed transfer on the frozen parity-growth fixtures."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import comb, perm, prod
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = "STATE-FEEDS-GROWTH-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / PREDECESSOR / f"{PREDECESSOR}-E001_feedback"))
import growth


TABLE = ("P", "V")
MODES = ("minimum", "exact_two", "any_pair")
CAPS = {"junctions": 6000, "distinctions": 32000}


def allowed(stars, occupied):
    return all(len(set(row) & occupied) % 2 == 0 for row in stars)


def permits_pair(fresh_count, mode):
    return (mode == "exact_two" and fresh_count == 2) or (mode == "any_pair" and fresh_count >= 2)


def lift_options(birth, old_values, mode):
    """The local family on actual fresh siblings; no choice by name is required."""
    fresh = birth["fresh"]
    if sum(d in old_values for _, d in birth["spent"]) % 2:
        return tuple((d,) for d in fresh)
    if birth["active"] and len(birth["parents"]) == 1 and permits_pair(len(fresh), mode):
        return tuple(combinations(fresh, 2))
    return ((),)


def realize(plan, mode, *, allocation=None, birth_order=None, pick=None):
    """Realize a funded roster, then select one representative of each local lift."""
    if mode not in MODES:
        raise ValueError(f"unknown lift {mode}")
    frame = growth.realize_round(plan, allocation=allocation, birth_order=birth_order)
    assert frame["status"] == "extend", frame
    values = set(plan.occupied)
    deposits, passed = {}, {}
    named_lifts = 1
    for birth in frame["births"]:
        options = lift_options(birth, plan.occupied, mode)
        chosen = options[0] if pick is None else pick(birth, options)
        if chosen not in options:
            raise ValueError("representative must be a permitted lift")
        named_lifts *= len(options)
        values.update(chosen)
        if len(chosen) == 2:
            deposits[birth["knot"]] = chosen
        elif len(chosen) == 1:
            passed[birth["knot"]] = chosen
    assert allowed(frame["stars"], values)
    assert values & plan.stage.names == plan.occupied
    return {**frame, "occupied": sorted(values), "new_occupied": sorted(values - plan.occupied),
            "deposits": deposits, "passed": passed, "named_lifts_per_fixed_allocation": named_lifts}


def round_plan(stars, occupied):
    plan = growth.plan_round(stars, occupied, TABLE, caps=CAPS)
    assert plan.status == "extend", plan.details
    return plan


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            i = row.bit_length() - 1
            if i not in basis:
                basis[i] = row
                break
            row ^= basis[i]
    return len(basis)


def check_projections(before, after):
    """Eliminate off-support columns to check the actual projections."""
    rows = [sum(1 << d for d in s) for s in after["stars"]]
    r = rank(rows)
    assert r == after["equation_rank"]
    old = 0
    for mask in rows[:len(before)]:
        old |= mask
    assert r - rank(row & ~old for row in rows) == rank(rows[:len(before)])
    assert all(r - rank(row & ~support for row in rows) == 1 for support in rows)
    return len(rows)


def transport(left, right, old_names):
    """Complete a common old renaming by matching consumed roles and fresh colors."""
    names = dict(old_names)
    lut = {frozenset(d for _, d in row["spent"]): row for row in right["births"]}
    left_values, right_values = set(left["occupied"]), set(right["occupied"])
    child_map = {}
    for birth in left["births"]:
        other = lut[frozenset(names[d] for _, d in birth["spent"])]
        child_map[birth["knot"]] = other["knot"]
        assert birth["demand"] == other["demand"]
        for value in (False, True):
            src = [d for d in birth["fresh"] if (d in left_values) == value]
            dst = [d for d in other["fresh"] if (d in right_values) == value]
            names.update(zip(src, dst, strict=True))
    assert len(set(names.values())) == len(names) == left["distinction_count"] == right["distinction_count"]
    assert {frozenset(names[d] for d in row) for row in left["stars"]} == set(map(frozenset, right["stars"]))
    assert {names[d] for d in left_values} == right_values
    return child_map


def ordering(plan, frame, mode):
    demand = Counter(v for b in plan.births if len(b.parents) > 1 for v in b.parents)
    hot = set(plan.details["hot_live_parents"])
    assert hot.isdisjoint(demand)
    classes = prod(perm(len(ds), demand[v]) for v, ds in plan.stage.loose.items())
    renamed = {d: d for d in plan.stage.names}
    reversed_ports = {d: e for row in plan.stage.loose.values() for d, e in zip(row, reversed(row), strict=True)}
    for v, row in plan.stage.loose.items():
        if v not in hot:
            renamed.update((d, reversed_ports[d]) for d in row)
    assignment = growth.literal_allocation(plan)
    reversed_frame = realize(plan, mode, allocation=[tuple(reversed_ports[d] for d in ds) for ds in assignment],
                             birth_order=reversed(range(len(assignment))), pick=lambda _b, opts: opts[-1])
    transport(frame, reversed_frame, renamed)
    assert frame["named_lifts_per_fixed_allocation"] == reversed_frame["named_lifts_per_fixed_allocation"]
    report = {"old_colored_outcomes": 1, "fixed_all_old_distinctions_outcomes": classes,
              "named_lifts_per_fixed_allocation": frame["named_lifts_per_fixed_allocation"],
              "serializations_of_fixed_plan": perm(len(assignment)), "reverse_replay_matches": True}
    for v, row in plan.stage.loose.items():
        if not demand[v] or len(row) < 2:
            continue
        i, slot = next((i, b.parents.index(v)) for i, b in enumerate(plan.births)
                       if len(b.parents) > 1 and v in b.parents)
        a = assignment[i][slot]
        b = next(d for d in row if d != a)
        changed = [tuple(b if d == a else a if d == b else d for d in ds) for ds in assignment]
        other = realize(plan, mode, allocation=changed)
        old_supports = lambda f: {frozenset(d for _, d in r["spent"]) for r in f["births"]}
        assert old_supports(frame) != old_supports(other)
        swap = {d: d for d in plan.stage.names} | {a: b, b: a}
        transport(frame, other, swap)
        report["fixed_name_witness"] = {"parent": v, "old_swap": [a, b], "original_multi_input": assignment[i],
                                        "changed_multi_input": changed[i]}
        break
    assert (classes > 1) == ("fixed_name_witness" in report)
    return report


def recoding(plan, frame, mode, seed):
    rng = Random(seed)
    old = sorted(plan.stage.names)
    names = [7 * i + 11 for i in range(len(old))]
    rng.shuffle(names)
    by_name = dict(zip(old, names, strict=True))
    indices = list(range(len(plan.stage.stars)))
    rng.shuffle(indices)
    reply = round_plan([[by_name[d] for d in plan.stage.stars[v]] for v in indices],
                       {by_name[d] for d in plan.occupied})
    renamed_index = {v: i for i, v in enumerate(indices)}
    spent = defaultdict(list)
    for birth in frame["births"]:
        group = tuple(sorted(renamed_index[v] for v in birth["parents"]))
        moved = {renamed_index[v]: by_name[d] for v, d in birth["spent"]}
        spent[group].append(tuple(moved[v] for v in group))
    allocation = [spent[b.parents].pop() for b in reply.births]
    assert all(not rows for rows in spent.values())
    other = realize(reply, mode, allocation=allocation, birth_order=reversed(range(len(allocation))),
                    pick=lambda _birth, opts: opts[-1])
    transport(frame, other, by_name)


def groups(frame, vetoed):
    return {tuple(row["parents"]) for row in frame["candidate_groups"] if (row["action"] == "V") == vetoed}


def counts(before, frame):
    return {"knots": len(frame["born"]), "distinctions": frame["distinction_count"] - before["distinction_count"],
            "occupied_new": frame["new_occupied"], "new_pairs": frame["deposits"], "passed_singletons": frame["passed"],
            "retained_groups": sorted(groups(frame, False)), "vetoed_groups": sorted(groups(frame, True))}


def compare_second(first, without, mode):
    with_pairs = set(first["occupied"])
    actual = frozenset(d for ds in first["deposits"].values() for d in ds)
    assert with_pairs ^ without == actual and allowed(first["stars"], without)
    erased_plan, live_plan = (round_plan(first["stars"], values) for values in (without, with_pairs))
    erased, grown = (realize(plan, mode) for plan in (erased_plan, live_plan))
    assert not erased["hot_live_parents"] and set(grown["hot_live_parents"]) == set(first["deposits"])
    removed = {g for g in groups(erased, False) if not set(g).isdisjoint(first["deposits"])}
    assert groups(grown, True) == removed and not groups(erased, True)
    delta = len(grown["born"]) - len(erased["born"])
    assert delta == sum(len(g) - 1 for g in removed)
    siblings = Counter(b["parents"][0] for b in first["births"] if b["knot"] in first["deposits"])
    if mode == "any_pair":
        assert delta == sum(comb(j, 2) for j in siblings.values())
    assert set(grown["spent_occupied"]) == actual
    passing = [b for b in grown["births"] if any(d in actual for _, d in b["spent"])]
    assert all(len(b["parents"]) == 1 and b["knot"] in grown["passed"] for b in passing)
    assert len(passing) == len(actual)
    for seed in (376, 817):
        recoding(live_plan, grown, mode, seed)
    return {"kept": counts(first, grown), "erased": counts(first, erased),
            "birth_delta": delta, "distinction_delta": grown["distinction_count"] - erased["distinction_count"],
            "paid_signal_ports_passed_individually": len(passing),
            "erased_assignment_allowed": True,
            "kept_ordering": ordering(live_plan, grown, mode), "erased_ordering": ordering(erased_plan, erased, mode),
            "full_renamings_checked": 2,
            "projection_checks": [check_projections(first["stars"], r) for r in (erased, grown)]}


def far_reader(first, without):
    initial = round_plan(first["stars"], without)
    stage = initial.stage
    active = {j for j, row in enumerate(stage.stars) if not without.isdisjoint(row)}
    near = {j for j in stage.loose if j in active or not active.isdisjoint(stage.neighbors[j])}
    actions = {tuple(q["parents"]): "V" if not near.isdisjoint(q["parents"]) else "P"
               for q in initial.details["candidate_groups"]}
    actions.update({(j,): "P" for j in stage.loose})
    wide = growth.plan_round(stage.stars, without, TABLE, caps=CAPS, recorded_actions=actions)
    frame = realize(wide, "minimum")
    erased = realize(initial, "minimum")
    assert not frame["new_occupied"] and not erased["new_occupied"]
    return {"hot_at_own_or_one_neighbor": sorted(near), "growth": counts(first, frame),
            "birth_delta": len(frame["born"]) - len(erased["born"])}


def pending_at_handover(stars, occupied, mode):
    """Test a current holder and its unique shared-input holder for pending transfer."""
    holders = defaultdict(list)
    for v, row in enumerate(stars):
        for d in row:
            holders[d].append(v)
    pending = set()
    for v, row in enumerate(stars):
        shared = [d for d in row if len(holders[d]) == 2]
        fresh = set(row) - set(shared)
        if len(shared) == 1 and permits_pair(len(fresh), mode) and occupied.isdisjoint(fresh):
            d, = shared
            other, = set(holders[d]) - {v}
            if d not in occupied and not occupied.isdisjoint(stars[other]):
                pending.add(v)
    return pending


def one_pair(first, without):
    cold = realize(round_plan(first["stars"], without), "minimum")
    v, pair = next((v, pair) for v, pair in first["deposits"].items()
                   if any(v in group for group in groups(cold, False)))
    assert all(not allowed(first["stars"], without | {d}) for d in pair)
    assert allowed(first["stars"], without) and allowed(first["stars"], without | set(pair))
    changed = realize(round_plan(first["stars"], without | set(pair)), "minimum")
    assert changed["hot_live_parents"] == [v] and groups(changed, True)
    return {"child": v, "support": first["stars"][v], "pair": pair,
            "allowed_write_counts_tested": {0: True, 1: False, 2: True},
            "second_births_without_pair": len(cold["born"]), "second_births_with_only_pair": len(changed["born"]),
            "groups_refused": sorted(groups(changed, True))}


def delayed_bad_order(first, without):
    pending = first["deposits"]
    state = set(without)
    remaining = set(pending)
    for v, pair in reversed(tuple(pending.items())):
        assert pending_at_handover(first["stars"], state, "exact_two") == remaining
        state.update(pair)
        remaining.remove(v)
        assert allowed(first["stars"], state)
    assert state == set(first["occupied"])
    assert not pending_at_handover(first["stars"], state, "exact_two")
    early = realize(round_plan(first["stars"], state), "minimum")
    late = realize(round_plan(first["stars"], without), "minimum")
    keeper = {d: v for v, row in late["consumed"].items() for _, d in row}
    blocked = []
    for v, pair in pending.items():
        u, w = (keeper[d] for d in pair)
        assert u != w and not allowed(late["stars"], set(late["occupied"]) ^ set(pair))
        blocked.append({"initial_child": v, "pending_pair": pair, "distinct_consumers": [u, w]})
    assert len(early["born"]) > len(late["born"])
    return {"early_pair_then_growth": len(early["born"]), "growth_before_any_pair": len(late["born"]),
            "pending_pairs_disabled_after_consumption": blocked,
            "readiness_checks_during_all_deposits": len(pending) + 1}


def total_bare_write(plan, first):
    n = len(plan.stage.stars)
    # The frozen bare source gives ring meetings first and then two loose distinctions per original knot.
    rotation = {d: (d + 1) % n for d in range(n)}
    for v in range(n):
        rotation.update(zip(plan.stage.loose[v], plan.stage.loose[(v + 1) % n], strict=True))
    swap = {d: d for d in plan.stage.names}
    a, b = plan.stage.loose[0]
    swap.update({a: b, b: a})
    cold = realize(plan, "minimum")
    generators = [transport(cold, cold, action) for action in (rotation, swap)]
    seen = {cold["born"][0]}
    while (more := {p[v] for p in generators for v in seen} - seen):
        seen.update(more)
    assert seen == set(cold["born"]) == set(first["deposits"])
    assert all(len(row) == 2 for row in cold["fresh"].values())
    return {"transitive_orbit_of_unary_children": len(seen), "minimum_nonzero_equivariant_total_writes": 2 * len(seen),
            "local_even_nonzero_writes": 2, "generators_on_children": generators}


def tiny_lifts():
    """All serial orders and each minimum or pair lift on two small hot-unary starts."""
    results = {}
    for n in (3, 4):
        plan = round_plan((tuple(range(n)),), {0, 1})
        for mode in MODES:
            reference = realize(plan, mode)
            identity = {d: d for d in plan.stage.names}
            orders = tuple(permutations(range(n)))
            for order, ports in product(orders, repeat=2):
                other = realize(plan, mode, allocation=[(d,) for d in ports], birth_order=order,
                                pick=lambda _b, opts: opts[-1])
                transport(reference, other, identity)
            portfolios = [lift_options(b, plan.occupied, mode) for b in reference["births"]]
            for choices in product(*portfolios):
                chosen = iter(choices)
                other = realize(plan, mode, pick=lambda _b, _opt: next(chosen))
                transport(reference, other, identity)
            for birth, opts in zip(reference["births"], portfolios, strict=True):
                assert len(opts) == comb(len(birth["fresh"]), len(opts[0]))
                assert all(len(opt) % 2 == sum(d in plan.occupied for _, d in birth["spent"]) % 2 for opt in opts)
            results[f"{n}/{mode}"] = {"serializations_checked": len(orders), "old_input_allocations_checked": len(orders),
                                      "allocation_order_combinations_checked": len(orders) ** 2,
                                      "named_lifts_checked": prod(map(len, portfolios)),
                                      "pointwise_old_colored_outcomes": 1}
    return results


def continued_bare(stars, occupied):
    reports = {}
    for mode in MODES:
        trace = []
        stage, values = stars, occupied
        for age in range(1, 7):
            frame = realize(round_plan(stage, values), mode)
            expected = len(stars) * (age + 1 if mode == "minimum" else 2 ** age)
            assert len(frame["born"]) == expected
            assert len(set(frame["new_occupied"])) == sum(map(len, frame["passed"].values())) + 2 * len(frame["deposits"])
            assert all(len(ds) == 2 for ds in frame["fresh"].values())
            trace.append({"age": age, "births": len(frame["born"]), "total_knots": frame["junction_count"],
                          "deposited_pairs": len(frame["deposits"]), "passed_singletons": len(frame["passed"]),
                          "new_occupied": len(frame["new_occupied"])})
            stage, values = frame["stars"], frame["occupied"]
        reports[mode] = trace
    return reports


def fixture(spec):
    stars = growth.predecessor().source_stars(spec)
    ring, = map(frozenset, spec["roles"]["ring_edges"])
    report = {"original_ring": sorted(ring), "source_knots": len(stars), "preparations": {}}
    for preparation, state in (("quiet", frozenset()), ("ring_loaded", ring)):
        plan = round_plan(stars, state)
        assert not any(set(row) & state for row in plan.stage.loose.values())
        ordinary = realize(plan, "minimum")
        incidence = {k: ordinary[k] for k in ("stars", "fresh", "parent_sets", "consumed")}
        arms = {}
        for mode in MODES:
            first = realize(plan, mode)
            assert all(first[k] == value for k, value in incidence.items())
            assert set(first["occupied"]) & plan.stage.names == state
            old_values = set(first["occupied"]) - {d for ds in first["deposits"].values() for d in ds}
            assert old_values == state == set(ordinary["occupied"])
            eligible = [b for b in first["births"] if b["active"] and len(b["parents"]) == 1]
            if mode == "any_pair":
                assert {b["knot"] for b in eligible} == set(first["deposits"])
            if mode != "minimum":
                assert pending_at_handover(first["stars"], old_values, mode) == set(first["deposits"])
                assert not pending_at_handover(first["stars"], set(first["occupied"]), mode)
            arms[mode] = {"first_occupied": first["occupied"], "first_deposits": first["deposits"],
                          "hot_unary_eligible_by_fresh_count": dict(Counter(len(b["fresh"]) for b in eligible)),
                          "first_ordering": ordering(plan, first, mode),
                          "second": compare_second(first, frozenset(old_values), mode)}
            if not state:
                assert not first["deposits"] and not arms[mode]["second"]["birth_delta"]
            elif mode == "exact_two" and spec["id"] in ("R0", "J1"):
                report["one_pair_witness"] = one_pair(first, state)
            if state and mode == "exact_two" and spec["id"] == "R0":
                report["delayed_bad_order"] = delayed_bad_order(first, state)
                report["equivariant_total_write"] = total_bare_write(plan, first)
        far = far_reader(ordinary, state)
        broad = arms["any_pair"]["second"]["kept"]
        assert set(far["hot_at_own_or_one_neighbor"]) == set(arms["any_pair"]["first_deposits"])
        for measure in ("knots", "distinctions", "retained_groups", "vetoed_groups"):
            assert far["growth"][measure] == broad[measure]
        report["preparations"][preparation] = {
            "original_assignment": sorted(state), "incidence": incidence,
            "first_projection_checks": check_projections(stars, ordinary), "modes": arms,
            "radius_one_holder_control": {**far, "matches_any_pair_structural_reading": True},
        }
    if spec["id"] == "R0":
        report["six_completed_layers"] = continued_bare(stars, ring)
    return report


def main():
    config = json.loads((HERE / "inputs.json").read_text())
    source = (ROOT / config["source"]).read_bytes()
    assert sha256(source).hexdigest() == config["sha256"]
    specs = {row["id"]: row for row in json.loads(source)["cases"]}
    report = {"source_sha256": config["sha256"], "caps": CAPS, "fixtures": {tag: fixture(specs[tag]) for tag in config["cases"]},
              "tiny_hot_unary_controls": tiny_lifts()}
    print(json.dumps(report, separators=(",", ":")))


if __name__ == "__main__":
    main()
