"""Independent finite parity and serialization checks for the feedback table."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import factorial, prod
from pathlib import Path
from random import Random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "independent.json"
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.knots import check_knot
from knotlab.relations import Relation


PATH = (frozenset((0, 2, 3)), frozenset((0, 1, 6)), frozenset((1, 4, 5)))
MIXED = frozenset((0, 1, 2, 4))
TABLES = tuple(product("PV+-", repeat=2))


def cycle(length, loose):
    return tuple(frozenset(((j - 1) % length, j, *range(length + loose * j,
                                                     length + loose * (j + 1))))
                 for j in range(length))


def incidence(stars):
    owners = defaultdict(list)
    for knot, row in enumerate(stars):
        for bit in row:
            owners[bit].append(knot)
    ordinary = {j: set() for j in range(len(stars))}
    loose = defaultdict(list)
    for bit, row in owners.items():
        if len(row) == 1:
            loose[row[0]].append(bit)
        else:
            u, v = row
            ordinary[u].add(v)
            ordinary[v].add(u)
    return ordinary, dict(loose)


def multis(neighbors):
    """Find candidate cliques and test their common witnesses independently."""
    graph = nx.Graph()
    graph.add_nodes_from(neighbors)
    graph.add_edges_from((a, b) for a, b in combinations(neighbors, 2)
                         if neighbors[a] & neighbors[b])
    eligible = [tuple(sorted(row)) for row in nx.find_cliques(graph)
                if len(row) >= 3 and not set.intersection(*(neighbors[v] for v in row))]
    covered = {pair for row in eligible for pair in combinations(row, 2)}
    eligible.extend(tuple(sorted(pair)) for pair in graph.edges if tuple(sorted(pair)) not in covered)
    return tuple(sorted(eligible))


@dataclass(frozen=True)
class Birth:
    parents: tuple[int, ...]
    fresh: int
    demand: int
    action: str


@dataclass(frozen=True)
class Plan:
    proposals: tuple[tuple[int, ...], ...]
    refused: tuple[tuple[int, ...], ...]
    births: tuple[Birth, ...]
    shortages: tuple[tuple[int, int], ...]


def plan(stars, occupied, table, read="support"):
    ordinary, loose = incidence(stars)
    offered = multis({j: ordinary[j] for j in loose})

    def action(group):
        if read == "support":
            hot = any(occupied & stars[j] for j in group)
        elif read == "loose":
            hot = any(occupied.intersection(loose[j]) for j in group)
        else:
            assert read == "parity"
            hot = any(len(occupied & stars[j]) % 2 for j in group)
        return table[hot]

    refused = tuple(group for group in offered if action(group) == "V")
    roster = [group for group in offered if group not in refused]
    demand = Counter(j for group in roster for j in group)
    shortages = tuple(sorted((j, demand[j] - len(bits)) for j, bits in loose.items()
                             if demand[j] > len(bits)))
    if shortages:
        return Plan(offered, refused, (), shortages)
    roster.extend((j,) for j, bits in sorted(loose.items()) for _ in range(len(bits) - demand[j]))
    future = Counter(i for group in multis({i: set(row) for i, row in enumerate(roster)})
                     for i in group)
    closing = len(roster) == 1 and len(roster[0]) == sum(map(len, loose.values()))
    births = []
    for i, group in enumerate(roster):
        choice = action(group)
        floor = max(1, 3 - len(group))
        shift = {"+": 1, "-": -1}.get(choice, 0)
        count = 0 if closing else max(floor, max(floor, future[i]) + shift)
        births.append(Birth(group, count, future[i], choice))
    return Plan(offered, refused, tuple(births), ())


def bindings(stars, births):
    _, loose = incidence(stars)
    orders = [list(permutations(sorted(loose[parent]))) for parent in sorted(loose)]
    for chosen in product(*orders):
        pools = {parent: iter(row) for parent, row in zip(sorted(loose), chosen, strict=True)}
        yield tuple(tuple(next(pools[parent]) for parent in b.parents) for b in births)


@cache
def parity_basis(stars):
    # Triangular elimination with the highest occupied bit as pivot.
    bits = tuple(sorted(set().union(*stars)))
    index = {bit: i for i, bit in enumerate(bits)}
    pivots = {}
    for row in stars:
        mask = sum(1 << index[bit] for bit in row)
        while mask:
            k = mask.bit_length() - 1
            if k not in pivots:
                pivots[k] = mask
                break
            mask ^= pivots[k]
    basis = []
    for free in sorted(set(range(len(bits))) - pivots.keys()):
        mask = 1 << free
        for pivot, row in sorted(pivots.items()):
            if (mask & row).bit_count() % 2:
                mask |= 1 << pivot
        basis.append(frozenset(bit for i, bit in enumerate(bits) if mask & (1 << i)))
    return tuple(basis)


def projection(basis, marks):
    states = {frozenset()}
    for delta in basis:
        projected = delta & marks
        states.update(row ^ projected for row in tuple(states))
    return states


def all_old_states(stars):
    names = sorted(set().union(*stars))
    # Direct truth table is an independent check on linear elimination.
    direct = {frozenset(bit for bit, on in zip(names, values, strict=True) if on)
              for values in product((0, 1), repeat=len(names))}
    direct = {row for row in direct if all(len(row & s) % 2 == 0 for s in stars)}
    assert direct == projection(parity_basis(stars), set(names))
    return tuple(sorted(direct, key=lambda row: tuple(sorted(row))))


@cache
def qualify(old, following):
    old_bits = set().union(*old)
    before, after = parity_basis(old), parity_basis(following)
    assert projection(after, old_bits) == projection(before, old_bits)
    return tuple(projected_knot(after, row).is_knot for row in following[len(old):])


def projected_knot(basis, row):
    bits = sorted(row)
    names = tuple(map(str, bits))
    states = frozenset(tuple(bit in values for bit in bits) for values in projection(basis, row))
    return check_knot(Relation(names, states), names[:-1], names[-1])


@cache
def minimum_options(width, odd):
    allowed = [bits for k in range(width + 1) if k % 2 == odd
               for bits in combinations(range(width), k)]
    assert allowed
    minimum = min(map(len, allowed))
    return tuple(bits for bits in allowed if len(bits) == minimum)


def realize(stars, occupied, births, inputs, ordering):
    next_name = max(set().union(*stars)) + 1
    remaining = set().union(*map(set, incidence(stars)[1].values()))
    rows = []
    marked = set(occupied)
    for i in ordering:
        used = frozenset(inputs[i])
        width = births[i].fresh
        assert used <= remaining
        remaining -= used
        fresh = range(next_name, next_name + width)
        next_name += width
        chosen = minimum_options(width, len(used & occupied) % 2)[0]
        row = used.union(fresh)
        marked.update(fresh[j] for j in chosen)
        assert len(row & marked) % 2 == 0
        rows.append(row)
    assert not remaining
    return stars + tuple(rows), frozenset(marked)


def old_fixed_key(old, stars, occupied):
    names = set().union(*old)
    return tuple(sorted((tuple(sorted(row & names)), len(row - names), len((row - names) & occupied))
                        for row in stars[len(old):]))


def graph(stars, marked=None, old=None):
    g = nx.Graph()
    old_bits = set().union(*old) if old is not None else set()
    old_count = len(old) if old is not None else 0
    for j, row in enumerate(stars):
        g.add_node(("K", j), color=("K", j < old_count))
        for bit in row:
            g.add_node(("D", bit), color=("D", bit in old_bits, marked is not None and bit in marked))
            g.add_edge(("K", j), ("D", bit))
    return g


def shape_classes(realizations, colored, old=None):
    samples = []
    for stars, values in realizations:
        current = graph(stars, values if colored else None, old=old)
        if not any(nx.is_isomorphic(current, peer, node_match=lambda a, b: a == b) for peer in samples):
            samples.append(current)
    return len(samples)


def frame(stars, occupied, table, *, all_orders):
    work = plan(stars, occupied, table)
    assert not work.shortages and work.births
    old_bits = set().union(*stars)
    fixed = set()
    realizations = []
    lift_count = labeled_schedules = num_bindings = 0
    lit_details = []
    for inputs in bindings(stars, work.births):
        num_bindings += 1
        initial_order = tuple(range(len(inputs)))
        stars_out, values_out = realize(stars, occupied, work.births, inputs, initial_order)
        assert all(qualify(stars, stars_out))
        expected = old_fixed_key(stars, stars_out, values_out)
        fixed.add(expected)
        realizations.append((stars_out, values_out))
        choices = [len(minimum_options(b.fresh, len(occupied.intersection(taken)) % 2))
                   for b, taken in zip(work.births, inputs, strict=True)]
        lift_count += prod(choices)
        if all_orders:
            for order in permutations(initial_order):
                again, marked = realize(stars, occupied, work.births, inputs, order)
                # All other minimum lifts are within each child's private fresh permutation group.
                assert old_fixed_key(stars, again, marked) == expected
                assert marked & old_bits == occupied
                labeled_schedules += 1
        lit_details.append((inputs, expected, len(values_out - old_bits)))
    assert labeled_schedules == (num_bindings * factorial(len(work.births)) if all_orders else 0)
    assert shape_classes(realizations, False) == 1
    colored_classes = shape_classes(realizations, True, old=stars)
    assert colored_classes == shape_classes(realizations, True)
    return {
        "old_ones": sorted(occupied), "bindings": num_bindings,
        "labeled_birth_orders": labeled_schedules,
        "minimum_lifts_with_bindings": lift_count,
        "serial_realizations_including_lifts": lift_count * factorial(len(work.births)) if all_orders else 0,
        "full_colored_classes": colored_classes, "pointwise_old_colored_classes": len(fixed),
        "pointwise_old_uncolored_classes": len({
            tuple((row, width) for row, width, _ in key) for key in fixed
        }),
        "new_knots": len(work.births), "new_bits": sum(b.fresh for b in work.births),
        "fresh_activity": sorted({mass for _, _, mass in lit_details}),
        "literal_bindings": lit_details,
    }


def path_recoding():
    rng = Random(8243)
    return (2, 0, 1), dict(zip(range(7), rng.sample(range(31, 103), 7), strict=True))


def recoding_control(rows, before, states):
    row_order, moved = path_recoding()
    inverse = {new: old for old, new in moved.items()}
    renamed = tuple(frozenset(moved[e] for e in rows[j]) for j in row_order)
    checked = 0
    for table, occupancy_rows in before.items():
        for occupied, expected in zip(states, occupancy_rows, strict=True):
            result = frame(renamed, frozenset(moved[e] for e in occupied), tuple(table), all_orders=False)
            def remap(key):
                return tuple(sorted((tuple(sorted(inverse[e] for e in inputs)), width, weight)
                                    for inputs, width, weight in key))
            assert {remap(detail[1]) for detail in result["literal_bindings"]} == {
                detail[1] for detail in expected["literal_bindings"]
            }
            assert result["full_colored_classes"] == expected["full_colored_classes"]
            checked += 1
    return {"frames": checked, "old_distinction_permutation": moved, "old_knot_order": row_order}


def path_checks():
    states = all_old_states(PATH)
    assert all(qualify((), PATH))
    found = {"".join(table): [frame(PATH, occupied, table, all_orders=True) for occupied in states]
             for table in TABLES}
    assert len(states) == 16 and MIXED in states
    abstract = [k for k, rows in found.items() if all(row["full_colored_classes"] == 1 for row in rows)]
    literal = [k for k, rows in found.items() if all(row["pointwise_old_colored_classes"] == 1 for row in rows)]
    assert set(abstract) == {t + "V" for t in "PV+-"} and literal == ["VV"]
    for table, cases in found.items():
        sample = cases[states.index(MIXED)]
        assert sample["fresh_activity"] == ([2] if table[1] == "V" else [0, 2])
        if table[0] != "V":
            assert cases[0]["pointwise_old_uncolored_classes"] > 1
    return {
        "source_stars": [sorted(row) for row in PATH], "mixed_old_ones": sorted(MIXED),
        "allowed_inputs": len(states), "all_tables": len(found),
        "fully_colored_confluent_tables": abstract, "pointwise_old_confluent_tables": literal,
        "recoding": recoding_control(PATH, found, states),
        "total_birth_orders": sum(row["labeled_birth_orders"] for rows in found.values() for row in rows),
        "total_order_and_min_lift_choices": sum(row["serial_realizations_including_lifts"]
                                                for rows in found.values() for row in rows),
        "frames": found,
    }


def select(stars, occupied, table):
    work = plan(stars, occupied, table)
    assert not work.shortages
    taken = next(bindings(stars, work.births))
    out, lifted = realize(stars, occupied, work.births, taken, tuple(range(len(taken))))
    assert all(qualify(stars, out))
    return work, out, lifted


def ring_controls():
    stars = cycle(5, 2)
    assert all(qualify((), stars))
    quiet = frozenset()
    ring = frozenset(range(5))
    assert all(len(ring & row) == 2 for row in stars)
    p, cold, _ = select(stars, quiet, ("P", "+"))
    q, hot, same_lift = select(stars, ring, ("P", "+"))
    # Toggling the old shared ring is still allowed on the cold successor.
    assert all(len(row & ring) % 2 == 0 for row in cold)
    assert same_lift == ring
    assert shape_classes(((cold, ring), (hot, ring)), False) == 2
    assert plan(cold, quiet, ("P", "+")) == plan(cold, ring, ("P", "+"))
    assert plan(stars, quiet, ("P", "+"), read="loose") == plan(
        stars, ring, ("P", "+"), read="loose")
    assert plan(stars, quiet, ("P", "+"), read="parity") == plan(
        stars, ring, ("P", "+"), read="parity")
    action_counts = {}
    for action in "PV+-":
        now, _, values = select(stars, ring, ("P", action))
        assert values == ring
        action_counts[action] = [len(now.births), sum(b.fresh for b in now.births)]
    assert action_counts == {"P": [5, 10], "V": [10, 20], "+": [5, 15], "-": [5, 5]}
    _, pinched, _ = select(stars, ring, ("P", "-"))
    stalled = plan(pinched, ring, ("P", "-"))
    rescued = plan(pinched, ring, ("V", "-"))
    assert len(stalled.shortages) == 5 and all(d == 1 for _, d in stalled.shortages)
    assert not rescued.shortages and len(rescued.refused) == len(rescued.births) == 5
    return {"old_shared_ring": sorted(ring), "hot_action_births_and_new_distinctions": action_counts,
            "flip_after_birth": {"new_knots": len(p.births), "width": len(set().union(*cold))},
            "flip_before_birth": {"new_knots": len(q.births), "width": len(set().union(*hot))},
            "same_old_state_and_zero_fresh": True, "late_ring_null": True,
            "shortages_after_minus": stalled.shortages, "vetoed_to_restore_funding": rescued.refused,
            "spent_loose_reads_quiet": True, "total_parity_reads_quiet": True}


def closing_control():
    stars = cycle(3, 1)
    assert all(qualify((), stars))
    old_states = all_old_states(stars)
    checked = 0
    for table in TABLES:
        for state in old_states:
            work, _, _ = select(stars, state, table)
            if not work.refused:
                assert len(work.births) == 1 and work.births[0].fresh == 0
                checked += 1
    extra = stars + (frozenset((3, 4, 5, 6)),)
    assert qualify(stars, extra) == (False,)
    assert projection(parity_basis(extra), {6}) == {frozenset()}
    flags = projected_knot(parity_basis(extra), extra[-1])
    assert flags.binding and not flags.loss_on_erasure and flags.coexistence
    return {"old_stars": [sorted(row) for row in stars], "old_states": len(old_states),
            "closing_frames": checked, "forcible_extra_bit_fails_K2": True,
            "forcible_extra_bit_preserves_old_marginal": True}


def port_and_lift_controls():
    # This optional slot reader leaves the original complete structural law in place.
    base = plan(PATH, MIXED, ("P", "P"))
    routes = []
    for state in (MIXED, MIXED ^ {2, 3}):
        only, = [inputs for inputs in bindings(PATH, base.births)
                 if all(set(bits) <= state for b, bits in zip(base.births, inputs, strict=True)
                        if len(b.parents) > 1)]
        end, marked = realize(PATH, state, base.births, only, range(len(only)))
        routes.append((end, marked))
    assert old_fixed_key(PATH, *routes[0]) != old_fixed_key(PATH, *routes[1])
    assert shape_classes(routes, True) == 1

    odd = frozenset((0, 2, 6))
    assert all(len(odd & row) % 2 == 0 for row in PATH)
    use = next(bindings(PATH, base.births))
    stars, lift = realize(PATH, odd, base.births, use, range(len(use)))
    child, = [row for row in stars[len(PATH):] if 6 in row]
    fresh = child - {6}
    assert len(fresh) == 2 and len(fresh & lift) == 1
    swap = lift ^ fresh
    assert all(len(row & swap) % 2 == 0 for row in stars)
    assert old_fixed_key(PATH, stars, lift) == old_fixed_key(PATH, stars, swap)
    return {
        "optional_occupied_first_A104_router": {
            "two_old_frames": [sorted(marked & set(range(7))) for _, marked in routes],
            "endpoints_with_old_identity": [old_fixed_key(PATH, *route) for route in routes],
            "same_unlabelled_colored_incidence": True,
        },
        "odd_input_two_fresh": {"old_frame": sorted(odd), "fixed_input": 6, "fresh_pair": sorted(fresh),
                                "first_lift": sorted(lift & fresh), "second_lift": sorted(swap & fresh),
                                "literal_symmetric_choice_impossible": True},
    }


def late_frames():
    old = cycle(5, 2)
    ring = frozenset(range(5))
    first, handover, _ = select(old, frozenset(), ("P", "P"))
    selected = next(i for i, b in enumerate(first.births) if b.parents == (1, 4))
    used = handover[len(old) + selected].intersection(range(15))
    pulse = frozenset((0, 4)) | used
    assert len(pulse) == 4 and all(len(row & pulse) % 2 == 0 for row in handover)
    _, loose = incidence(handover)
    assert sum(bool(pulse & handover[j]) for j in loose) == 1
    return handover, ring, pulse


def late_control():
    stars, ring, pulse = late_frames()
    differences = {}
    for table in TABLES:
        base, cold, _ = select(stars, frozenset(), table)
        assert plan(stars, ring, table) == base
        loaded, hot, marks = select(stars, pulse, table)
        assert marks == pulse and all(len(row & pulse) % 2 == 0 for row in cold)
        profile = [(len(p.births), len(set().union(*stage)))
                   for p, stage in ((base, cold), (loaded, hot))]
        assert (profile[0] != profile[1]) == (table[0] != table[1])
        differences["".join(table)] = profile
    return {"raw_ring_in_all_tables": "same plan once its original knots are exhausted",
            "four_response": sorted(pulse), "live_knots_active": 1, "quiet_then_active": differences}


def production_replay():
    from growth import grow, plan_round, realize_round

    def shape_key(births):
        return Counter((b.parents, b.fresh, b.demand, b.action) for b in births)

    def compare_plan(stars, occupied, table):
        direct = plan(stars, occupied, table)
        actual = plan_round(stars, occupied, table)
        if direct.shortages:
            assert actual.status == "stall" and dict(direct.shortages) == actual.details["shortages"]
            return actual
        assert actual.status == "extend"
        assert shape_key(direct.births) == shape_key(actual.births)
        offered = actual.details["candidate_groups"]
        assert direct.proposals == tuple(sorted(tuple(d["parents"]) for d in offered))
        assert direct.refused == tuple(sorted(tuple(d["parents"]) for d in offered if d["action"] == "V"))
        return actual

    def checked_realization(old, occupied, actual, given, order, chooser, expected):
        observed = realize_round(actual, allocation=given, birth_order=order, choose_fresh=chooser)
        literal = tuple(map(frozenset, observed["stars"]))
        marked = frozenset(observed["occupied"])
        assert literal[:len(old)] == old
        assert marked.intersection(set.union(set(), *old)) == occupied
        assert all(len(row & marked) % 2 == 0 for row in literal)
        assert old_fixed_key(old, literal, marked) == expected

    path_frames = orders = lift_realizations = recoded_plans = 0
    row_order, moved = path_recoding()
    renamed = tuple(frozenset(moved[e] for e in PATH[j]) for j in row_order)
    for occupied, table in product(all_old_states(PATH), TABLES):
        actual = compare_plan(PATH, occupied, table)
        path_frames += 1
        recoded_state = frozenset(moved[e] for e in occupied)
        recoded = compare_plan(renamed, recoded_state, table)
        assert shape_key(actual.births) == Counter(
            (tuple(sorted(row_order[p] for p in b.parents)), b.fresh, b.demand, b.action)
            for b in recoded.births
        )
        recoded_plans += 1
        for given in bindings(PATH, actual.births):
            enumeration = tuple(range(len(given)))
            representative = realize(PATH, occupied, actual.births, given, enumeration)
            expected = old_fixed_key(PATH, *representative)
            for order in permutations(enumeration):
                checked_realization(PATH, occupied, actual, given, order,
                                    lambda fresh: fresh[-1], expected)
                orders += 1
            odd_widths = [b.fresh for b, used in zip(actual.births, given, strict=True)
                          if len(occupied.intersection(used)) % 2]
            for positions in product(*(range(width) for width in odd_widths)):
                choice = iter(positions)
                checked_realization(PATH, occupied, actual, given, enumeration,
                                    lambda fresh: fresh[next(choice)], expected)
                assert next(choice, None) is None
                lift_realizations += 1

    extra_inputs = [(cycle(3, 1), state) for state in all_old_states(cycle(3, 1))]
    extra_inputs += [(cycle(5, 2), frozenset()), (cycle(5, 2), frozenset(range(5)))]
    handover, ring, pulse = late_frames()
    extra_inputs += [(handover, occupied) for occupied in (frozenset(), ring, pulse)]
    for (stars, occupied), table in product(extra_inputs, TABLES):
        compare_plan(stars, occupied, table)
    own_ring = cycle(5, 2)
    load = frozenset(range(5))
    _, pinch, _ = select(own_ring, load, ("P", "-"))
    assert compare_plan(pinch, load, ("P", "-")).status == "stall"
    assert compare_plan(pinch, load, ("V", "-")).status == "extend"

    # The same literal stage and frame are handed in with unrelated reported ages.
    ages = (0, 17)
    next_frames = []
    for age in ages:
        archive = grow(handover, pulse, ("P", "V"), rounds=1, start_age=age)["stages"]
        next_frames.append({k: v for k, v in archive[str(age + 1)].items() if k != "age"})
    assert next_frames[0] == next_frames[1]
    return {"path_frames": path_frames, "recoded_plans": recoded_plans,
            "additional_plan_frames": len(extra_inputs) * len(TABLES) + 2,
            "reference_birth_orders_replayed": orders, "minimum_lifts_replayed": lift_realizations,
            "same_present_input_at_age_labels": ages}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = {"validation": "V2-independent-reimplementation-or-kernel",
              "freeze": "2d6cd3f340c1238836174f88dcc205c0e90abc45",
              "definition_digest": sha256((ROOT / "research" / HERE.parent.name
                                            / "definitions.md").read_bytes()).hexdigest(),
              "path": path_checks(), "ring": ring_controls(), "closing": closing_control(),
              "port_and_lift": port_and_lift_controls(), "present_state": late_control(),
              "production_replay": production_replay()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(args.output)
    path = result["path"]
    for key in ("fully_colored_confluent_tables", "pointwise_old_confluent_tables",
                "total_birth_orders", "total_order_and_min_lift_choices"):
        print(key, path[key])
    print(result["ring"], result["closing"], result["production_replay"])


if __name__ == "__main__":
    main()
