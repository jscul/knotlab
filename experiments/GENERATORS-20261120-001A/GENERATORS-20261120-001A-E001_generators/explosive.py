"""Complete and present-state serial growth on the sixteen archived jump-selected sources."""

from collections import Counter, defaultdict, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "explosive.json"
AUDIT = ROOT / "artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json"
SCREEN = ROOT / "artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/starts_screen.json"
EXPERIMENTS = ROOT / "experiments"
SCAFFOLDS = EXPERIMENTS / "SERIAL-REPAIRS-20261120-001A/SERIAL-REPAIRS-20261120-001A-E001_repairs/scaffolds.py"
SERIAL = EXPERIMENTS / "ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/serial.py"
LAWS = ("parity", "nae")
MAX_ROUNDS, MAX_KNOTS, MAX_DISTINCTIONS, MAX_ACTIONS = 4, 512, 4096, 24


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_gate(controls, literal, stars, recorded_parity):
    ranks = controls.parity_profile(stars)
    p_failed = [i for i, rank in enumerate(ranks) if rank != 1 or len(stars[i]) < 3]
    assert (not p_failed) == recorded_parity
    failures, strengthened = [], []
    with literal.nae_solver(stars) as solver:
        assert solver.solve()
        for i, support in enumerate(stars):
            words = literal.sat_patterns(solver, support)
            if words == controls.declared_patterns(len(support), "nae"):
                continue
            lacks = [
                d for j, d in enumerate(support)
                if len({word[:j] + word[j + 1:] for word in words}) != 1 << (len(support) - 1)
            ]
            row = {"knot": i, "local_rows": len(words), "missing_proper_projections": lacks}
            (failures if lacks or len(support) < 3 else strengthened).append(row)
    return {
        "parity": {"lawful": not p_failed, "fails_at": p_failed, "literal_projection_ranks": ranks},
        "nae": {"lawful": not failures, "fails_at": failures, "strengthened_local_law": strengthened},
    }


def components(graph):
    remaining = set(graph)
    parts = []
    while remaining:
        start = min(remaining)
        part = {start}
        todo = [start]
        for v in todo:
            more = graph[v] - part
            part.update(more)
            todo.extend(more)
        remaining.difference_update(part)
        parts.append(tuple(sorted(part)))
    return parts


def witness_graph(ordinary, live, *, witness_holders=None):
    graph = {v: set() for v in live}
    witnesses = range(len(ordinary)) if witness_holders is None else witness_holders
    for witness in witnesses:
        for a, b in combinations(sorted(ordinary[witness] & live), 2):
            graph[a].add(b)
            graph[b].add(a)
    return graph


def component_read(operator, literal, stars, end):
    graph = operator.neighbors(end)
    ordinary = literal.holder_graph(stars)
    assert graph == witness_graph(ordinary, end.opens.keys())
    witnessed = components(graph)
    combined = {v: row | (ordinary[v] & end.opens.keys()) for v, row in graph.items()}
    separate = components(combined)
    return witnessed, separate


def changes(before, after, label):
    holder = {v: i for i, part in enumerate(before) for v in part}
    from_parts = [{holder[p] for v in part for p in label[v]} for part in after]
    outputs = Counter(p for source_ids in from_parts for p in source_ids)
    return {
        "merge": [i for i, labels in enumerate(from_parts) if len(labels) > 1],
        "split": sorted(p for p, count in outputs.items() if count > 1),
        "disappear": sorted(set(range(len(before))) - outputs.keys()),
        "from_parts": [sorted(labels) for labels in from_parts],
    }


def bounded_plan(operator, end, law, room_knots, room_distinctions):
    if not end.opens:
        return {"stop": "closed"}
    try:
        multi = operator._proposals(end, room_knots)
    except operator._Cap:
        return {"stop": "current_group_cap", "next_knots_lower": room_knots + 1}
    used = Counter(p for row in multi for p in row)
    shortages = [(p, used[p] - h) for p, h in end.opens.items() if used[p] > h]
    if shortages:
        return {"stop": "stall", "shortages": shortages}
    parents = multi + tuple((p,) for p, h in end.opens.items() for _ in range(h - used[p]))
    if len(parents) > room_knots:
        return {"stop": "knot_cap", "next_knots": len(parents)}
    future = operator.End(dict.fromkeys(range(len(parents)), 1), operator._parent_blocks(parents))
    try:
        next_groups = operator._proposals(future, room_distinctions // 2)
    except operator._Cap:
        return {"stop": "lookahead_group_cap", "fresh_lower": 2 * (room_distinctions // 2 + 1)}
    count = Counter(i for row in next_groups for i in row)
    demand = tuple(count[i] for i in range(len(parents)))
    implied = law == "parity" and len(parents) == 1
    fresh = (0,) if implied else tuple(max(d, 3 - len(p), 1) for d, p in zip(demand, parents, strict=True))
    if sum(fresh) > room_distinctions:
        return {"stop": "distinction_cap", "fresh": sum(fresh), "next_knots": len(parents)}
    reference = operator.step(end, law)
    assert (reference.parents, reference.fresh, reference.demand, reference.implied) == (parents, fresh, demand, implied)
    return {"parents": parents, "fresh": fresh, "demand": demand, "implied": implied}


def loose_slots(literal, stars):
    available = defaultdict(deque)
    for d, row in sorted(literal.owners(stars).items()):
        if len(row) == 1:
            available[row[0]].append(d)
    return available


def allocate(literal, stars, plan):
    slots = loose_slots(literal, stars)
    fresh_name = len(literal.owners(stars))
    rows = []
    for group, n in zip(plan["parents"], plan["fresh"], strict=True):
        used = tuple(slots[v].popleft() for v in group)
        fresh = tuple(range(fresh_name, fresh_name + n))
        fresh_name += n
        rows.append((used, fresh))
    assert not any(slots.values())
    return rows


def replay_cohort(literal, stars, rows, order):
    """Replay fixed physical assignments. The result keeps its actual writing order."""
    coholders = Counter(d for row in stars for d in row)
    realized = list(stars)
    for i in order:
        inputs, fresh = rows[i]
        assert all(coholders[d] == 1 for d in inputs) and all(coholders[d] == 0 for d in fresh)
        assert len(inputs) + len(fresh) >= 2
        coholders.update((*inputs, *fresh))
        realized.append((*inputs, *fresh))
    assert sum(coholders.values()) == sum(map(len, realized))
    assert coholders == {d: len(row) for d, row in literal.owners(realized).items()}
    return tuple(realized)


def exact_local_control(controls, literal, stars, scope, law):
    measured = controls.patterns(literal, stars, scope, law)
    assert measured == controls.declared_patterns(len(scope), law)


def archive_turn(serial, stars, law, plan, expected):
    model = serial.S.from_junctions(stars)
    model.linalg = False
    def law_counts(p, info, rng):
        if law == "nae":
            info = [{**row, "implied": False} for row in info]
        return serial.F.fewest(p, info, rng)
    result = model.step(law_counts)
    assert result is not None and result["new"] == len(plan["parents"])
    assert tuple(map(tuple, model.bits_of)) == expected
    assert model.demand_at_birth[-len(plan["parents"]):] == list(plan["demand"])


def layer_summary(operator, literal, stars, parents=None):
    end = operator.from_stars(stars)
    witnessed, separate = component_read(operator, literal, stars, end)
    owners = literal.owners(stars)
    ordinary = literal.holder_graph(stars)
    erased_parts = components(witness_graph(ordinary, end.opens.keys(), witness_holders=end.opens))
    one_parent = []
    thin = []
    if parents is not None:
        assert all(parents[v] for v in end.opens)
        assert all(not (ordinary[v] & end.opens.keys()) for v in end.opens)
        assert len(erased_parts) == len(end.opens)
        graph = operator.neighbors(end)
        for v, h in end.opens.items():
            actual_old = {old for d in stars[v] for old in owners[d] if old != v}
            assert actual_old == set(parents[v])
            if len(actual_old) == 1:
                one_parent.append(v)
                if h == 2 and len(graph[v]) <= 1:
                    thin.append({"holder": v, "only_candidates": sorted(graph[v]), "opens": h})
    return {"knots": len(stars), "distinctions": len(owners), "live": len(end.opens),
            "component_sizes": list(map(len, witnessed)), "separate_part_sizes": list(map(len, separate)),
            "without_spent_witness_part_count": len(erased_parts),
            "opens": sum(end.opens.values()), "one_parent_live": one_parent, "thin_live": thin}


def whole(operator, literal, serial, controls, source, law, audit):
    stars = source
    ages = [{"age": 0, **layer_summary(operator, literal, stars)}]
    stop = {"stop": "four_round_limit"}
    first = None
    local_controls = 0
    for age in range(1, MAX_ROUNDS + 1):
        end = operator.from_stars(stars)
        before, _ = component_read(operator, literal, stars, end)
        plan = bounded_plan(operator, end, law, MAX_KNOTS - len(stars),
                            MAX_DISTINCTIONS - len(literal.owners(stars)))
        if "stop" in plan:
            stop = plan
            break
        if first is None:
            first = plan
        rows = allocate(literal, stars, plan)
        n = len(rows)
        left = replay_cohort(literal, stars, rows, range(n))
        right = replay_cohort(literal, stars, rows, reversed(range(n)))
        assert Counter(left) == Counter(right) and left[:len(stars)] == right[:len(stars)] == stars
        archive_turn(serial, stars, law, plan, left)
        if age == 1 and len(left[-1]) <= 8:
            exact_local_control(controls, literal, left, left[-1], law)
            local_controls += 1
        offset = len(stars)
        parents = {offset + i: p for i, p in enumerate(plan["parents"])}
        next_end = operator.from_stars(left)
        after, _ = component_read(operator, literal, left, next_end)
        transit = changes(before, after, parents)
        assert not transit["merge"] and not transit["split"]
        assert bool(transit["disappear"]) == plan["implied"]
        for v in ages[-1]["thin_live"]:
            parent = v["holder"]
            pure = [{"holder": offset + i, "fresh_count": plan["fresh"][i]}
                    for i, p in enumerate(plan["parents"]) if p == (parent,)]
            singleton = operator.step(operator.End({parent: v["opens"]}, ()), law)
            expected_pure = 1 if v["only_candidates"] else 2
            assert len(pure) == expected_pure and len(singleton.parents) == 2
            assert all(row["fresh_count"] == 2 for row in pure) and singleton.fresh == (2, 2)
            ages[-1].setdefault("thin_continuations", []).append(
                {"parent": parent, "all_own_children": pure, "alone_recomputed_fresh_counts": singleton.fresh}
            )
        summary = layer_summary(operator, literal, left, parents)
        max_parent = max(map(len, plan["parents"]))
        if age < len(audit["round_junction_counts"]):
            assert n == audit["round_junction_counts"][age]
            assert max_parent == audit["round_largest_groups"][age]
        ages.append({"age": age, "births": n, "largest_parent_set": max_parent,
                     "born_unaries": sum(len(p) == 1 for p in plan["parents"]),
                     "cohort_writes_equal": True, "component_change": transit, **summary})
        stars = left
        if plan["implied"]:
            stop = {"stop": "closed"}
            break
    return {"ages": ages, "stop": stop, "initial_plan": first,
            "exact_birth_projection_controls": local_controls}


def implemented_groups(operator, model, live):
    observed = operator.End(dict.fromkeys(live, 1), tuple(set(live).intersection(row) for row in model.nbr))
    return tuple(operator.proposals(observed))


def raw(controls, operator, literal, serial, source, law, first_plan, policy, order):
    model = serial.S.from_junctions(source)
    children = defaultdict(set)
    current = source
    events = []
    exact_inputs = 0
    first_difference = None
    planned = Counter(zip(first_plan["parents"], first_plan["fresh"], strict=True))
    remaining = planned.copy()
    monitor_first = True
    stop = {"stop": "24_action_limit"}
    for step in range(1, MAX_ACTIONS + 1):
        groups, unary, live = serial.moves(model, children)
        predicted = [
            g for g in implemented_groups(operator, model, live)
            if not set.intersection(*(children[p] for p in g))
        ]
        assert groups == predicted
        owes = Counter(p for g in groups for p in g)
        assert unary == [(p,) for p in live if len(model.loose(p)) > owes[p]]
        choices = groups if policy == "joins-first" and groups else groups + unary
        if not choices:
            stop = {"stop": "closed" if not live else "no_admitted_moves"}
            break
        parent = min(choices) if order == "low" else max(choices)
        if len(current) + 1 > MAX_KNOTS:
            stop = {"stop": "knot_cap"}
            break
        slots = tuple(model.loose(v)[0] for v in parent)
        spends_all = len(slots) == sum(len(model.loose(v)) for v in live)
        implied = law == "parity" and spends_all
        old_end = operator.from_stars(current)
        old_witness, old_separate = component_read(operator, literal, current, old_end)
        newborn = serial.new_junction(model, slots)
        relative_live = [i for i in range(len(model.bits_of)) if model.loose(i) or i == newborn]
        look = [tuple(sorted(g)) for g in model.groups_among(relative_live)]
        assert look == list(implemented_groups(operator, model, relative_live))
        demand = sum(newborn in g for g in look)
        assert not implied or demand == 0
        added = 0 if implied else max(demand, 3 - len(parent), 1)
        if model.nbits + added > MAX_DISTINCTIONS:
            stop = {"stop": "distinction_cap", "fresh": added}
            break
        input_projection_size = None
        if len(parent) <= 5:
            expected = controls.declared_patterns(len(parent), law) if implied else None
            projection = controls.patterns(literal, current, slots, law)
            assert projection == expected if implied else len(projection) == 1 << len(slots)
            input_projection_size = len(projection)
            exact_inputs += 1
        for p in parent:
            children[p].add(newborn)
        fresh = tuple(range(model.nbits, model.nbits + added))
        for bit in fresh:
            model.bits_of[newborn].append(bit)
            model.owner[bit] = [newborn]
            model.nbits += 1
        model.fresh[newborn] = added
        current = (*current, (*slots, *fresh))
        status = operator.from_stars(current)
        new_witness, new_separate = component_read(operator, literal, current, status)
        ancestry = {v: (v,) for v in status.opens if v != newborn}
        ancestry[newborn] = parent
        witness_changes = changes(old_witness, new_witness, ancestry)
        separate_changes = changes(old_separate, new_separate, ancestry)
        # Every pair of parents has a witness in the pre-action physical incidence.
        assert sum(not set(part).isdisjoint(parent) for part in old_witness) == 1
        assert not separate_changes["merge"]
        if monitor_first:
            if remaining[(parent, added)]:
                remaining[(parent, added)] -= 1
                if not any(remaining.values()):
                    monitor_first = False
            else:
                kind = ("fresh" if any(p == parent and left > 0 for (p, _), left in remaining.items())
                        else "parents")
                first_difference = {"step": step, "kind": kind, "parents": parent,
                                    "written_fresh": added,
                                    "pending_complete_fresh_for_parents": [
                                        f for (p, f), left in remaining.items() if p == parent and left > 0
                                    ]}
                monitor_first = False
        events.append({"step": step, "parents": parent, "spent": slots, "fresh": fresh, "demand": demand,
                       "knots": len(current), "distinctions": model.nbits,
                       "spends_all": spends_all, "implied": implied, "input_projection_size": input_projection_size,
                       "witness_sizes": list(map(len, new_witness)), "separate_sizes": list(map(len, new_separate)),
                       "witnessed_components_changed": witness_changes, "separate_parts_changed": separate_changes})
        if implied:
            stop = {"stop": "closed"}
            break
    return {"first_difference_from_planned_cohort": first_difference, "events": events, "stop": stop,
            "exact_input_projection_controls": exact_inputs,
            "literal_incidence_sha256": sha256(repr(current).encode()).hexdigest()}


def opposite_order_counts(cases, policy):
    first_differences = Counter()
    for row in cases:
        orders = row["present_serial"][policy]
        low, high = (orders[order]["events"] for order in ("low", "high"))
        at = next((a["step"] for a, b in zip(low, high) if a["distinctions"] != b["distinctions"]), None)
        first_differences[str(at) if at is not None else "equal_at_compared_steps"] += 1
    return dict(sorted(first_differences.items()))


def main():
    controls = load("old_projection_controls", SCAFFOLDS)
    literal = controls.load("literal_bond_utilities", controls.BOND / "scaffolds.py")
    operator = controls.load("complete_end_operator", controls.ORDINARY / "end_operator.py")
    serial = load("raw_serial_operator", SERIAL)
    sources_data = json.loads(AUDIT.read_text())["named_archive_starts"]
    screen_data = {row["case"]: row for row in json.loads(SCREEN.read_text())["starts"]}
    assert len(sources_data) == len(screen_data) == 16
    records = {}
    for case, data in sorted(sources_data.items()):
        stars = tuple(map(tuple, data["gate"]["literal_supports"]))
        q = source_gate(controls, literal, stars, data["gate"]["canonical"])
        record = {"original_identifier": data["identifier"], "source": stars, "source_gate": q,
                  "archived_offshoot_and_fate": {k: screen_data[case][k]
                                                for k in ("classification", "initial_two_open_offshoots")},
                  "laws": {}}
        for law in LAWS:
            if not q[law]["lawful"]:
                record["laws"][law] = {"status": "unlawful_source"}
                continue
            complete = whole(operator, literal, serial, controls, stars, law, data)
            assert complete["initial_plan"] is not None
            record["laws"][law] = {
                "status": "replayed",
                "complete": complete,
                "present_serial": {
                    policy: {order: raw(controls, operator, literal, serial, stars, law,
                                        complete["initial_plan"], policy, order)
                             for order in ("low", "high")}
                    for policy in ("any", "joins-first")
                },
            }
        records[case] = record
    summary = {}
    for law in LAWS:
        cases = [record["laws"][law] for record in records.values() if record["laws"][law]["status"] == "replayed"]
        serials = [run for row in cases for orders in row["present_serial"].values() for run in orders.values()]
        splits_then_merges = 0
        for run in serials:
            split = False
            for event in run["events"]:
                change = event["witnessed_components_changed"]
                if split and change["merge"]:
                    splits_then_merges += 1
                    break
                split = split or bool(change["split"])
        summary[law] = {
            "catalogued": len(records), "lawful_sources": len(cases),
            "complete_transitions": sum(len(x["complete"]["ages"]) - 1 for x in cases),
            "complete_stop_reasons": dict(Counter(x["complete"]["stop"]["stop"] for x in cases)),
            "raw_orders": len(serials), "raw_actions": sum(len(s["events"]) for s in serials),
            "raw_stop_reasons": dict(Counter(s["stop"]["stop"] for s in serials)),
            "raw_orders_diverging_from_first_cohort": sum(s["first_difference_from_planned_cohort"] is not None
                                                        for s in serials),
            "raw_orders_splitting_witness_components": sum(
                any(e["witnessed_components_changed"]["split"] for e in s["events"]) for s in serials),
            "raw_orders_merging_witness_components": sum(
                any(e["witnessed_components_changed"]["merge"] for e in s["events"]) for s in serials),
            "raw_orders_acquiring_a_separated_part": sum(
                any(e["separate_parts_changed"]["split"] for e in s["events"]) for s in serials),
            "raw_orders_splitting_then_merging_witness_components": splits_then_merges,
            "raw_opposite_orders_first_different_distinction_counts_by_policy": {
                policy: opposite_order_counts(cases, policy)
                for policy in ("any", "joins-first")
            },
            "raw_exact_input_projection_controls": sum(s["exact_input_projection_controls"] for s in serials),
        }
    result = {"design_freeze": "140ecfc78", "caps": {"complete_rounds": MAX_ROUNDS, "knots": MAX_KNOTS,
                                                    "distinctions": MAX_DISTINCTIONS, "raw_actions": MAX_ACTIONS},
              "weighting": "One per original archived cap-seven jump-selected draw, including equivalent descriptions.",
              "summary": summary, "catalogue": records}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=OUT.parent, delete=False) as out:
        temp = Path(out.name)
        json.dump(result, out, separators=(",", ":"))
        out.write("\n")
    temp.replace(OUT)


if __name__ == "__main__":
    main()
