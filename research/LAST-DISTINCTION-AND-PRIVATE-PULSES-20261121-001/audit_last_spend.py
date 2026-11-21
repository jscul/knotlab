"""Independent certificate checks for the physical last-distinction comparison."""
from collections import defaultdict
from itertools import permutations, product
from pathlib import Path
import json
import sys

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'research' / 'TICK-BIRTHS-AND-SCARCITY-20261121-001'))
BASE = "TICK-BIRTHS-AND-SCARCITY-20261121-001B"
BASE_ARCHIVE = ROOT / "artifacts" / BASE / (BASE + "-E001_serial")


def ancestry(parents, tip):
    """The full paid ancestry, with original identities and the observed tip anchored."""
    result = nx.DiGraph()
    pending = [tip]
    while pending:
        here = pending.pop()
        if here in result and "anchor" in result.nodes[here]:
            continue
        tag = ("original", here) if here not in parents else ("child", here == tip)
        result.add_node(here, anchor=tag)
        for parent in parents.get(here, ()):
            result.add_edge(parent, here)
            pending.append(parent)
    return result


def reference_turn():
    case = json.loads((BASE_ARCHIVE / "receipt.json").read_bytes())["laws"]["parity"]["bare"]
    parents = {event["knot"]: event["parents"]
               for depth in range(1, 7) for event in case["depths"][str(depth)]["events"]}
    root = case["tick_windows"]["6"]["tick"]
    graph = ancestry(parents, root)
    return graph, [v for v in nx.topological_sort(graph)], root


def exact_turns(reference, writes):
    match = lambda a, b: a["anchor"] == b["anchor"]
    hits = []
    for tip in writes:
        observed = ancestry(writes, tip)
        if len(observed) == len(reference) and DiGraphMatcher(
                reference, observed, node_match=match).is_isomorphic():
            hits.append(tip)
    return hits


def future_bound(reference, roles, writes, loose):
    """Overapproximate every later realization, even incompatible choices on different parents.

    An existing child is considered whenever its true parents can match the old
    roles. A hypothetical new child may even use parents that have yet to be
    born. We only remove an option when a fixed parent is empty, a fixed
    multipart group has already been used together, or a required role is
    impossible. Thus an empty result excludes every future realization.
    """
    by_arity = defaultdict(list)
    paid = {}
    for child, inputs in writes.items():
        paid[child] = frozenset(inputs)
        by_arity[len(inputs)].append(child)
    actual, future = {}, {}
    for role in roles:
        prs = tuple(reference.predecessors(role))
        if not prs:
            actual[role], future[role] = {role}, False
            continue
        actual[role] = {child for child in by_arity[len(prs)]
                        if any(all(point in actual[parent] for parent, point in zip(prs, order))
                               for order in permutations(paid[child]))}
        alternatives = [[*actual[parent], *([None] if future[parent] else [])] for parent in prs]
        can_be_born = False
        for choice in product(*alternatives):
            pinned = {x for x in choice if x is not None}
            if len(pinned) != sum(x is not None for x in choice):
                continue
            if any(not loose.get(x) for x in pinned):
                continue
            if len(prs) > 1 and None not in choice and any(pinned <= p for p in paid.values()):
                continue
            can_be_born = True
            break
        future[role] = can_be_born
    return actual, future


def held_loose(holdings):
    owners = defaultdict(list)
    for holder, names in enumerate(holdings):
        for name in names:
            owners[name].append(holder)
    assert all(len(ids) <= 2 and len(set(ids)) == len(ids) for ids in owners.values())
    loose = defaultdict(set)
    for name, ids in owners.items():
        if len(ids) == 1:
            loose[ids[0]].add(name)
    return loose


def input_words(holdings, inputs, law):
    """Count old-state projections onto the actual paid distinctions before a birth."""
    names = {n: i + 1 for i, n in enumerate(sorted(set().union(*map(set, holdings))))}
    if law == "parity":
        rows = [sum(1 << names[n] for n in h) for h in holdings]
        outside = ~sum(1 << names[n] for n in inputs)

        def rank(eq):
            pivots = {}
            for v in eq:
                while v:
                    i = v.bit_length()
                    if i not in pivots:
                        pivots[i] = v
                        break
                    v ^= pivots[i]
            return len(pivots)
        num_constraints = rank(rows) - rank(v & outside for v in rows)
        return 1 << (len(inputs) - num_constraints)
    if law != "nae":
        raise ValueError(law)
    from pysat.solvers import Solver
    clauses = [[sign * names[n] for n in h] for h in holdings for sign in (1, -1)]
    with Solver(bootstrap_with=clauses) as solver:
        return sum(solver.solve(assumptions=[sign * names[n] for sign, n in zip(word, inputs)])
                   for word in product((-1, 1), repeat=len(inputs)))


def first_outside_bound(reference, roles):
    """Count every possible prefix set, including those raw funding might forbid."""
    written = [r for r in roles if reference.in_degree(r)]
    index = {r: i for i, r in enumerate(written)}
    required = [sum(1 << index[p] for p in reference.predecessors(r) if p in index)
                for r in written]
    uses = {i: sum(1 << index[r] for r in reference.successors(i)) for i in (2, 4)}
    assert all(x.bit_count() == 2 for x in uses.values())
    seen, todo = {0}, [0]
    while todo:
        prefix = todo.pop()
        for i, earlier in enumerate(required):
            child = 1 << i
            if prefix & earlier != earlier or prefix & child:
                continue
            extended = prefix | child
            if extended not in seen:
                seen.add(extended)
                todo.append(extended)
    minima = {}
    for donor, rec in uses.items():
        outstanding = [(3 - (prefix & rec).bit_count(), (rec & ~prefix).bit_count())
                       for prefix in seen if rec & ~prefix]
        assert min(left - debt for left, debt in outstanding) == 1
        minima[donor] = min(left for left, _ in outstanding)
    return len(seen), minima


def current_groups(holdings, writes):
    from audit_serial_traces import sharing, raw_groups
    _, neighbors, loose = sharing(holdings)
    live = {j for j, names in enumerate(loose) if names}
    paid = [set(v) for v in writes.values()]
    groups = {g for g in raw_groups(neighbors, live) if not any(g <= a for a in paid)}
    return groups, loose


def write_group(holdings, parents, loose):
    from audit_serial_traces import sharing, raw_groups
    from collections import Counter
    used = [min(loose[k]) for k in parents]
    tip = len(holdings)
    interim = holdings + [used]
    _, touching, remaining = sharing(interim)
    live = {j for j, names in enumerate(remaining) if names} | {tip}
    uses = Counter(j for g in raw_groups(touching, live) for j in g)
    budget = max(uses[tip], 3-len(used), 1)
    first = max(max(h) for h in holdings) + 1
    return holdings + [used + list(range(first, first + budget))]


def disjoint_suffixes(reference, roles, tip, holdings, writes, disjoint):
    """Exhaust only still-needed clock births after the alternate outside spend."""
    allowed, loose = current_groups(holdings, writes)
    assert frozenset(disjoint) in allowed
    new = len(holdings)
    holdings = write_group(holdings, disjoint, loose)
    writes = {**writes, new: list(disjoint)}
    realized, _ = future_bound(reference, roles, writes, held_loose(holdings))
    assert all(len(a) <= 1 for a in realized.values())
    mapping = {role: next(iter(ids)) for role, ids in realized.items() if ids}
    missing = [role for role in roles if role not in mapping]
    stats = {"admitted_prefixes": 0, "terminal_misses": 0, "full_suffixes": 0, "first_complete": None}

    def visit(current, built, paid, suffix):
        stats["admitted_prefixes"] += 1
        if tip in built:
            assert exact_turns(reference, paid) == [built[tip]]
            stats["full_suffixes"] += 1
            if stats["first_complete"] is None:
                stats["first_complete"] = suffix
            return
        options, loose_now = current_groups(current, paid)
        followed = False
        for role in missing:
            if role in built:
                continue
            earlier = tuple(reference.predecessors(role))
            if any(p not in built for p in earlier):
                continue
            group = sorted(built[p] for p in earlier)
            assert len(group) >= 2
            if frozenset(group) not in options:
                continue
            followed = True
            child = len(current)
            result = write_group(current, group, loose_now)
            visit(result, {**built, role: child}, {**paid, child: group}, suffix + [group])
        if not followed:
            stats["terminal_misses"] += 1
    visit(holdings, mapping, writes, [])
    return stats


def check():
    from audit_serial_traces import reproduce
    file, = (ROOT / "artifacts" / (HERE.name + "A")).glob("*/witness.json")
    data = json.loads(file.read_bytes())
    alternatives = json.loads(file.with_name("counterfactuals.json").read_bytes())["laws"]
    reference, roles, tip = reference_turn()
    ideals, lower = first_outside_bound(reference, roles)
    assert all(k == 2 for k in lower.values())
    projected = writes_checked = 0
    examples = 0
    disjoint = None
    for naming in ("witnesses", "reversed_source_names"):
        for law, case in data[naming].items():
            source = case["source"]
            common, prefix_map = list(source), {}
            for e in case["common"]:
                combinations_tested = input_words(common, e["consumed_slots"], law)
                assert combinations_tested == 1 << len(e["parents"])
                projected += combinations_tested
                common = reproduce(common, len(source), e, "unrestricted")
                prefix_map[e["child"]] = e["parents"]
                writes_checked += 1
            x = case["fork"]["slot"]
            donor = case["fork"]["donor"]
            assert held_loose(common)[donor] == {x}
            actions = [case["control"][0], case["treatment"][0]]
            assert all(x in a["consumed_slots"] and a["also_passes_joins_first"] for a in actions)
            control_group, outside_group = (set(a["parents"]) for a in actions)
            assert control_group == {4, 6} and outside_group == {4, len(source) - 1}
            assert any(set(reference.predecessors(r)) == control_group for r in roles)
            assert not any(control_group <= set(o) for o in prefix_map.values())
            for key in ("control", "treatment"):
                holders, writes = common, dict(prefix_map)
                for e in case[key]:
                    nr = input_words(holders, e["consumed_slots"], law)
                    assert nr == 1 << len(e["parents"])
                    projected += nr
                    holders = reproduce(holders, len(source), e, "unrestricted")
                    writes[e["child"]] = e["parents"]
                    writes_checked += 1
                possible, later = future_bound(reference, roles, writes, held_loose(holders))
                if key == "control":
                    assert exact_turns(reference, writes) == case["control_marked_realization"]
                    assert len(possible[tip]) == 1
                else:
                    assert not possible[tip] and not later[tip]
                    assert not held_loose(holders)[donor]
                    assert not any(control_group <= set(o) for o in writes.values())
            assert input_words([[0, 1]], [0, 1], law) == 2
            if naming == "witnesses":
                other = alternatives[law]["one_fewer_shared_preparatory_write"]
                assert other["outside"]["parents"] == case["treatment"][0]["parents"]
                context = alternatives[law]["matched_event_budget"]
                tracks = (
                    (case["common"][:-1], [other["outside"]] + other["follow"], 1),
                    (case["common"] + case["treatment"], context["additional_physical_loss_arm_writes"], 0),
                )
                for earlier, later, expected in tracks:
                    holders, edges = list(source), {}
                    for index, e in enumerate(earlier + later):
                        free = held_loose(holders)
                        if expected and index == len(earlier):
                            assert x in e["consumed_slots"] and len(free[donor]) == 2
                        if expected and index == len(earlier)+1:
                            assert len(free[donor]) == 1 and x not in free[donor]
                        nr = input_words(holders, e["consumed_slots"], law)
                        assert nr == 1 << len(e["parents"])
                        event = {**e, "eligible_slots_at_parents": [sorted(free[p]) for p in e["parents"]]}
                        holders = reproduce(holders, len(source), event, "unrestricted")
                        edges[e["child"]] = e["parents"]
                        projected += nr
                        writes_checked += 1
                    assert len(edges) == 21 and len(exact_turns(reference, edges)) == expected
                other, = case["controls"]["disjoint"]["eligible_equal_cost_groups"]
                assert donor not in other
                other_result = disjoint_suffixes(reference, roles, tip, common, prefix_map, other)
                if disjoint is None:
                    disjoint = other_result
                assert disjoint == other_result
            examples += 1
    print(f"{examples} law and naming checks, {writes_checked} physical writes, "
          f"{projected} old input words. Turn fired at event 21 or became impossible at 10.")
    print(f"{ideals} downward-closed subsets of the 20 required writes. "
          f"Each original accessible on the first outside spend had at least two slots if still needed.")
    print("After the disjoint outside spend, outstanding-clock-only suffixes:", json.dumps(disjoint))


if __name__ == "__main__":
    check()
