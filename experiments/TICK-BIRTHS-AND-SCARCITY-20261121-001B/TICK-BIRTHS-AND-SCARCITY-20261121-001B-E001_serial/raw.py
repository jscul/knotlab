"""Read the registered marked turn through actual inputs under current-stage serial growth."""
from collections import Counter, defaultdict, deque
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name, relative):
    spec = spec_from_file_location(name, ROOT / relative)
    loaded = module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


rings = module("b262_historical_rings", "experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/"
               "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.py")
raw = module("b262_historical_serial", "experiments/ROUND-FREE-20261119-001B/"
             "ROUND-FREE-20261119-001B-E001_serial/serial.py")
physical = rings.fixture()
SOURCES = {"alone": None, "same_continuation": 3, "other_continuation": 2}


def ordinary_roles(host, law):
    source, _ = rings.attached_ring(8, (0,), host)
    physical.certify_source(source, law)
    _, clean = rings.attached_ring(8, (0,))
    winding = clean[0]
    names = rings.collect_model_labels(winding)
    roles = {}
    levels = {}
    stages = {}
    targets = {}
    current = source
    for age in range(1, 11):
        _, births, _ = physical.literal_turn(current, law)
        by_parents = {tuple(sorted(b.parents)): b for b in births}
        assert len(by_parents) == len(births)
        new = {}
        for shape in rings.model_cohort(winding, age + 1):
            previous = tuple(sorted(names[c] for c in rings.model_parents(winding, shape)))
            birth = by_parents[previous]
            new[shape] = birth.knot
            roles[birth.knot] = (previous, len(birth.fresh))
            levels[birth.knot] = age
            if rings.impulse(shape):
                assert age not in targets and len(previous) == 2
                targets[age] = birth.knot
        if age in (6, 10):
            stages[age] = current
        current += tuple(b.support for b in births)
        names = new
    assert set(targets) == {6, 10}
    return source, roles, levels, stages, targets


@lru_cache(maxsize=96)
def facts(stars, nsource):
    p = raw.S.from_junctions(stars)
    loose = {j: tuple(p.loose(j)) for j in range(len(stars)) if p.loose(j)}
    children = defaultdict(set)
    ancestry = [set([j]) for j in range(nsource)]
    by_parents = defaultdict(list)
    for child in range(nsource, len(stars)):
        ps = tuple(sorted({holder for slot in stars[child] for holder in p.owner[slot] if holder < child}))
        assert ps
        ancestry.append(set.union(*(ancestry[j] for j in ps)))
        by_parents[ps].append(child)
        for j in ps:
            children[j].add(child)
    multi, unary, _ = raw.moves(p, children)
    _, ordinary, openings = physical.incidence(stars)
    assert loose == {j: tuple(ds) for j, ds in openings.items()}
    blocks, candidates = physical.witnessed_end(ordinary, openings)
    external = physical.multi_groups(blocks, candidates)
    independent = {g for g in external if not set.intersection(*(children[j] for j in g))}
    uses = Counter(j for g in independent for j in g)
    assert set(multi) == independent
    assert set(unary) == {(j,) for j, ds in openings.items() if len(ds) > uses[j]}
    return p, loose, children, ancestry, by_parents, tuple(sorted(multi)), tuple(sorted(unary))


def pool(multi, unary, policy):
    return multi if policy == "joins_first" and multi else multi + unary


@lru_cache(maxsize=160)
def apply(stars, nsource, parents, law):
    p, loose, _, ancestry, _, multi, unary = facts(stars, nsource)
    assert parents in multi + unary
    inputs = tuple(loose[j][0] for j in parents)
    assert all(p.owner[d] == [j] for j, d in zip(parents, inputs, strict=True))
    assert set(inputs) < {d for ds in loose.values() for d in ds}
    # A GF(2) reduction or SAT test checks every assignment on exactly these old inputs.
    if law == "parity":
        for size in range(1, len(inputs) + 1):
            assert all(p._reduce(p._mask(selection)) for selection in combinations(inputs, size))
    else:
        with Minisat22() as solver:
            for star in stars:
                physical.nae_add(solver, star)
            for assignment in range(1 << len(inputs)):
                signed = [(x + 1) * (1 if assignment >> i & 1 else -1) for i, x in enumerate(inputs)]
                assert solver.solve(assumptions=signed)

    child = len(stars)
    provisional = raw.S.from_junctions(stars + (inputs,))
    still_live = {j for j in loose if provisional.loose(j)} | {child}
    demand_sets = tuple(sorted(tuple(sorted(group)) for group in provisional.groups_among(still_live)
                               if child in group))
    demand = len(demand_sets)
    nfresh = raw.F.fewest(provisional, [{"d": demand, "p": len(parents), "implied": False}], None)[0]
    assert nfresh == max(1, 3-len(inputs), demand)
    fresh = tuple(range(p.nbits, p.nbits + nfresh))
    physical.canonical_relation(law, nfresh + len(inputs))
    assert all(d not in p.owner for d in fresh)
    row = {
        "child": child, "parents": parents, "eligible_slots_at_parents": [loose[j] for j in parents],
        "consumed_slots": inputs, "fresh": fresh, "current_demand": demand_sets,
        "source_ancestry_of_parents": [tuple(sorted(ancestry[j])) for j in parents],
        "pre_total_loose": sum(map(len, loose.values())),
        "post_total_loose": sum(map(len, loose.values())) - len(inputs) + nfresh,
        "old_input_tuples_tested": 1 << len(inputs)
    }
    return stars + (inputs + fresh,), row


def needed_roles(target, roles):
    ids = {target}
    pending = [target]
    while pending:
        for parent in roles[pending.pop()][0]:
            if parent in roles and parent not in ids:
                ids.add(parent)
                pending.append(parent)
    return sorted(ids)


def realizations(stars, nsource, target, roles, needed):
    """Enumerate injective matches of the specified ancestor roles to physical births."""
    by_parents = facts(stars, nsource)[4]
    maps = [{i: i for i in range(nsource)}]
    for role in needed:
        extensions = []
        for mapping in maps:
            demanded = tuple(sorted(mapping[p] for p in roles[role][0]))
            for made in by_parents.get(demanded, []):
                if made not in mapping.values():
                    extensions.append({**mapping, role: made})
        maps = extensions
        if not maps:
            break
    return [m[target] for m in maps]


def write_measure(stars, nsource, selected, law, target, policy):
    _, loose, _, ancestry, _, multi, unary = facts(stars, nsource)
    admitted = pool(multi, unary, policy)
    assert selected in admitted
    after, detail = apply(stars, nsource, selected, law)
    return after, {
        **detail, "target_admitted_before": target in admitted, "pool_size": len(admitted),
        "also_passes_joins_first": selected in pool(multi, unary, "joins_first"),
        "target_donor_slots_before": [loose.get(j, ()) for j in target],
        "target_donor_slots_after": [tuple(d for d in loose.get(j, ()) if d not in detail["consumed_slots"])
                                     for j in target],
        "consumer": nsource == 9 and any(8 in ancestry[j] for j in selected),
    }


def irreversible(stars, nsource, target):
    _, loose, children, _, _, _, _ = facts(stars, nsource)
    zero = [j for j in target if not loose.get(j)]
    joined = sorted(set.intersection(*(children[j] for j in target)))
    if zero or joined:
        return {"exhausted_target_donors": zero, "earlier_children_using_both": joined}
    return None


def witness_search(start, nsource, target, law, policy, variant):
    q = deque([(start, (), frozenset(), False)])
    expansions = Counter()
    states_made = 0
    while q and sum(expansions.values()) < 200:
        stars, path, prior_competitors, used_bridge = q.popleft()
        if len(path) >= 4:
            continue
        expansions[len(path)] += 1
        _, _, _, ancestry, _, multi, unary = facts(stars, nsource)
        allowed = []
        for g in pool(multi, unary, policy):
            overlaps = sum(j in target for j in g)
            consumer = nsource == 9 and any(8 in ancestry[j] for j in g)
            bridge = not overlaps and not used_bridge and bool(prior_competitors.intersection(g))
            if g == target:
                continue
            if variant == "consumer_donor_only":
                if not (overlaps and consumer):
                    continue
            elif not (overlaps or bridge):
                continue
            allowed.append((not consumer, -overlaps, g, bridge))
        for _, negative_overlap, g, bridge in sorted(allowed):
            after, step = write_measure(stars, nsource, g, law, target, policy)
            states_made += 1
            cert = irreversible(after, nsource, target)
            trace = path + (step,)
            if cert:
                return {"status": "permanent_loss", "certificate": cert, "trace": trace,
                        "expanded_by_prefix_length": dict(expansions), "children_checked": states_made}
            if len(trace) < 4:
                added = prior_competitors | {len(stars)} if negative_overlap else prior_competitors
                q.append((after, trace, added, used_bridge or bridge))
    return {"status": "censored_at_200" if q else "no_certificate_in_registered_prefixes",
            "expanded_by_prefix_length": dict(expansions), "children_checked": states_made}


def cold(source, roles, levels, goal, law, policy, tie):
    needed = needed_roles(goal, roles)
    mapping = {j: j for j in range(len(source))}
    current = source
    trace = []
    missing = []
    while goal not in mapping:
        _, _, _, _, _, multi, unary = facts(current, len(source))
        admitted = pool(multi, unary, policy)
        choices = []
        for role in needed:
            if role in mapping or not all(p in mapping for p in roles[role][0]):
                continue
            parents = tuple(sorted(mapping[p] for p in roles[role][0]))
            if parents in admitted:
                choices.append((levels[role], parents, role))
        if not choices:
            for role in needed:
                if role not in mapping and all(j in mapping for j in roles[role][0]):
                    ps = tuple(sorted(mapping[j] for j in roles[role][0]))
                    missing.append({"ordinary_role": role, "actual_parents": ps,
                                    "unrestricted_admits": ps in multi + unary})
            break
        latest = max(t for t, _, _ in choices)
        pick = min if tie == "ascending" else max
        _, selected, role = pick(a for a in choices if a[0] == latest)
        later, step = apply(current, len(source), selected, law)
        trace.append({**step, "reference_role": role, "reference_parent_depth": levels[role],
                      "reference_fresh": roles[role][1], "also_passes_joins_first":
                      selected in pool(multi, unary, "joins_first")})
        mapping[role] = len(current)
        current = later
    matched = realizations(current, len(source), goal, roles, needed)
    status = "unique_firing" if len(matched) == 1 else "ambiguous" if matched else "ancestry_strategy_stalled"
    divergence = next((i for i,r in enumerate(trace,1) if len(r["fresh"]) != r["reference_fresh"]), None)
    return {"status": status, "full_realizations": matched, "needed_nonoriginal_roles": len(needed),
            "made_nonoriginal_roles": len(mapping)-len(source), "first_changed_fresh_at_event": divergence,
            "blocked_ordinary_roles_whose_parents_exist": missing, "trace": trace}


def study(host, law):
    source, roles, levels, stages, target_roles = ordinary_roles(host, law)
    ns = len(source)
    results = {"source": source, "warm": {}, "cold": {}}
    for age in (6, 10):
        goal = target_roles[age]
        needed = needed_roles(goal, roles)
        parents, normal_fresh = roles[goal]
        start = stages[age]
        for p in parents:
            assert realizations(start, ns, p, roles, needed_roles(p, roles)) == [p]
        warm = {"tick_id_in_ordinary_roster": goal, "physical_target_parents": parents,
                "target_role_ancestry_size": len(needed), "normal_fresh": normal_fresh, "policies": {}}
        for policy in ("unrestricted", "joins_first"):
            _, loose, _, _, _, multi, unary = facts(start, ns)
            admitted = pool(multi, unary, policy)
            assert parents in admitted
            next_state, step = write_measure(start, ns, parents, law, parents, policy)
            assert realizations(next_state, ns, goal, roles, needed) == [len(start)]
            cell = {"initial_loose_at_tick_parents": [loose[p] for p in parents], "immediate_unique_firing": step}
            for v in ("consumer_donor_only", "any_donor_plus_one_intervening"):
                earlier = results["warm"].get("6",{}).get("policies",{}).get(policy,{}).get(v,{})
                if age == 6 or earlier.get("status") == "permanent_loss":
                    cell[v] = witness_search(start, ns, parents, law, policy, v)
            warm["policies"][policy] = cell
        results["warm"][str(age)] = warm
    for policy in ("unrestricted", "joins_first"):
        results["cold"][policy] = {tie: cold(source, roles, levels, target_roles[6], law, policy, tie)
                                   for tie in ("ascending", "descending")}
    return results


def main():
    output = {"observation": "Marked structural roles are resolved using chronological physical input holders.",
              "sources": {}}
    for name, host in SOURCES.items():
        output["sources"][name] = {law: study(host, law) for law in ("parity", "nae")}
    print(json.dumps(output, separators=(",",":"), sort_keys=True))


if __name__ == "__main__":
    main()
