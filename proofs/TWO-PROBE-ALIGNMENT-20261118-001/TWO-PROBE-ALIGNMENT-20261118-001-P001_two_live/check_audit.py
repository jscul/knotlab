"""Check the two-probe prefix by excluding every reachable nonterminal cycle.

Uses separate full-projection and weighted-table implementations. A Boolean
cycle search and a finite enumeration with a hidden chooser check the game.
The actual physical state is retained across observations.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from math import factorial, perm, prod

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


GOAL = -1
OLD = tuple(range(8))
PORTS = (8, 9)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


@cache
def symmetries(rooted):
    result = set()
    for axes in permutations(range(3)):
        for flip in ((0,) if rooted else OLD):
            old = tuple(flip ^ sum(((i >> a) & 1) << b for b, a in enumerate(axes))
                        for i in OLD)
            for ports in (PORTS, PORTS[::-1]) if rooted else ((),):
                result.add(old + ports)
    return tuple(sorted(result))


def pair(x, y):
    return (x, y) if x <= y else (y, x)


def image(tests, names):
    return tuple(sorted(pair(names[a], names[b]) for a, b in tests))


class Physical:
    def __init__(self):
        self.states = []
        self.index = {}
        self.labeled_count = 0
        for rooted in (False, True):
            choices = tuple(combinations(range(10 if rooted else 8), 2))
            for count in range(3):
                for tests in combinations_with_replacement(choices, count):
                    self.labeled_count += 8 if rooted else 1
                    if (rooted, tests) in self.index:
                        continue
                    number = len(self.states)
                    self.states.append((rooted, tests))
                    for names in symmetries(rooted):
                        self.index[rooted, image(tests, names)] = number
        require(self.labeled_count == 9083, self.labeled_count)

    def at(self, rooted, tests):
        return self.index[rooted, tuple(sorted(tests))]


def allowed(rooted, tests):
    cuts = [sum(((i >> j) & 1) << i for i in OLD) for j in range(3)]
    rows = {0, 255, *cuts, *(255 ^ word for word in cuts)}
    width = 8
    if rooted:
        rows = {s | (u << 8) | ((u ^ (s & 1)) << 9)
                for s in rows for u in (0, 1)}
        width += 2
    for a, b in tests:
        old = rows
        rows = {s | p << width | q << (width + 1)
                for s in old for p, q in product((0, 1), repeat=2)
                if p != q or p == (s >> a & 1) == (s >> b & 1)}
        require({s & ((1 << width) - 1) for s in rows} == old, "probe projection")
        width += 2
    return rows, width


def distance_table(rows, width):
    # Grow only free supports, in increasing order of their highest coordinate.
    # Every possible minimal nonfree support has a free immediate predecessor.
    table = [[0 if i == j else width + 1 for j in range(width)] for i in range(width)]
    layer = {0}
    for size in range(1, min(width, len(rows).bit_length()) + 1):
        following = set()
        for prefix in layer:
            for last in range(prefix.bit_length(), width):
                mask = prefix | (1 << last)
                places = tuple(i for i in range(last + 1) if mask >> i & 1)
                if any(mask ^ (1 << i) not in layer for i in places):
                    continue
                if len({s & mask for s in rows}) == 1 << size:
                    following.add(mask)
                elif size >= 3:
                    for i, j in combinations(places, 2):
                        table[i][j] = table[j][i] = min(table[i][j], size - 1)
        layer = following
    return tuple(map(tuple, table))


def compress(values):
    index = {value: i for i, value in enumerate(sorted(set(values)))}
    return tuple(index[value] for value in values)


@dataclass(frozen=True)
class Quotient:
    sizes: tuple
    renamings: tuple


def observation(table, marks):
    n = len(table)
    cells = []
    for i in range(n):
        for cell in cells:
            a = cell[0]
            if marks[a] == marks[i] and all(table[a][j] == table[i][j]
                                          for j in range(n) if j not in (i, a)):
                cell.append(i)
                break
        else:
            cells.append([i])
    anchors = tuple(cell[0] for cell in cells)
    inner = tuple((len(c), marks[c[0]], table[c[0]][c[-1]]) for c in cells)
    weights = tuple(tuple(table[a][b] for b in anchors) for a in anchors)
    colors = compress(inner)
    while True:
        colored = compress(tuple((c, tuple(sorted((weights[i][j], colors[j])
                                for j in range(len(cells)) if j != i)))
                                 for i, c in enumerate(colors)))
        if colored == colors:
            break
        colors = colored
    groups = [[i for i, c in enumerate(colors) if c == k] for k in sorted(set(colors))]
    best, maps = None, []
    for order_parts in product(*(permutations(g) for g in groups)):
        order = sum(order_parts, ())
        key = (tuple(inner[i] for i in order),
               tuple(weights[i][j] for i, j in combinations(order, 2)))
        if best is None or key < best:
            best, maps = key, [order]
        elif key == best:
            maps.append(order)
    first = maps[0]
    block = {v: k for k, i in enumerate(first) for v in cells[i]}
    renamings = tuple(tuple(order.index(i) for i in first) for order in maps)
    return best, block, Quotient(tuple(len(cells[i]) for i in first), renamings)


SINGLE = ((0,),)
UNORDERED = ((0, 1), (1, 0))
REPLACE = tuple((*x, *(2 + i for i in y)) for x, y in product(UNORDERED, repeat=2))
TWO_TESTS = REPLACE + tuple((p[2], p[3], p[0], p[1]) for p in REPLACE)
ARGUMENT_ORDERS = {
    "root": SINGLE, "second": ((0, 1),), "probe": UNORDERED, "erase": UNORDERED,
    "replace": REPLACE, "clear": ((),), "drop_any": ((),), "replace_any": UNORDERED,
    "replace_all": UNORDERED,
    "configure_two": TWO_TESTS,
}


def signature(blocks, operands):
    # Equal arguments, possible between the two simultaneous queries, retain
    # their equality even if they belong to a large class of interchangeable IDs.
    return tuple((b, operands.index(a)) for b, a in zip(blocks, operands))


@cache
def action_class(quotient, operation, pattern):
    blocks, repeated = zip(*pattern) if pattern else ((), ())
    orders = ARGUMENT_ORDERS[operation]
    variants = set()
    for renaming in quotient.renamings:
        for p in orders:
            new_blocks = tuple(renaming[blocks[k]] for k in p)
            new_ids = tuple(repeated[k] for k in p)
            variants.add(signature(new_blocks, new_ids))
    uses = Counter(b for b, _ in set(pattern))
    assignments = prod(perm(quotient.sizes[b], count) for b, count in uses.items())
    equivalent_orders = len({tuple(repeated[k] for k in p) for p in orders})
    total = len(variants) * assignments
    require(total % equivalent_orders == 0, (operation, pattern))
    return (operation, min(variants)), total // equivalent_orders


def physical_moves(world, rooted, tests, extra):
    permanent = 10 if rooted else 8
    pool = tuple(combinations(range(permanent), 2))
    if rooted:
        for port in (0, *PORTS):
            for neighbor in (1, 2, 4):
                yield "second", (port, neighbor), {GOAL}
    else:
        for r in OLD:
            shifted = image(tests, tuple(i ^ r for i in OLD))
            yield "root", (r,), {world.at(True, shifted)}
    if len(tests) < 2:
        for probe in pool:
            yield "probe", probe, {world.at(rooted, (*tests, probe))}
    for i in range(len(tests)):
        endpoints = (permanent + 2 * i, permanent + 2 * i + 1)
        retained = tests[:i] + tests[i + 1:]
        yield "erase", endpoints, {world.at(rooted, retained)}
        for probe in pool:
            yield "replace", endpoints + probe, {world.at(rooted, (*retained, probe))}
    if tests and "clear" in extra:
        yield "clear", (), {world.at(rooted, ())}
    if tests and "arbitrary" in extra:
        after = [tests[:i] + tests[i + 1:] for i in range(len(tests))]
        yield "drop_any", (), {world.at(rooted, other) for other in after}
        for probe in pool:
            yield "replace_any", probe, {world.at(rooted, (*other, probe)) for other in after}
    if tests and "replace_all" in extra:
        for probe in pool:
            yield "replace_all", probe, {world.at(rooted, (probe,))}
    if "batch" in extra or ("initial_batch" in extra and not rooted and not tests):
        for x, y in combinations_with_replacement(pool, 2):
            yield "configure_two", x + y, {world.at(rooted, (x, y))}


def frame(world, tables, extras):
    observed = []
    agencies = []
    for (rooted, tests), table in zip(world.states, tables):
        key, named_block, quotient = observation(table, (0,) * len(table))
        observed.append(key)
        counts = Counter()
        next_states = defaultdict(set)
        sizes = {}
        for op, args, successors in physical_moves(world, rooted, tests, extras):
            key_action, orbit_size = action_class(quotient, op, signature(
                tuple(named_block[v] for v in args), args))
            counts[key_action] += 1
            next_states[key_action].update(successors)
            sizes[key_action] = orbit_size
        # A set of addressed legal commands may be a proper subset of its
        # scalar-table orbit. Omitted addresses are physical errors or bad joins.
        require(all(count <= sizes[k] for k, count in counts.items()), "orbit overcount")
        agencies.append({k: t for k, t in next_states.items() if counts[k] == sizes[k]})
    return compress(observed), agencies


def check_stabilizers(world, tables):
    """Count selected action orbits again by actually coloring their arguments."""
    checked = Counter()
    for (rooted, tests), table in zip(world.states, tables):
        original, blocks, graph = observation(table, (0,) * len(table))
        order = tuple(range(1, len(table), 2)) + tuple(reversed(range(0, len(table), 2)))
        shuffled = tuple(tuple(table[i][j] for j in order) for i in order)
        transported, other_blocks, other_graph = observation(shuffled, (0,) * len(table))
        require(transported == original, "relabelled scalar table")
        group_size = len(graph.renamings) * prod(factorial(n) for n in graph.sizes)
        representatives = {}
        for op, args, _ in physical_moves(world, rooted, tests, ()):
            representatives.setdefault(op, args)
        # Simultaneous operands may repeat either one or both actual middles.
        for args in ((0, 1, 2, 3), (0, 1, 1, 2), (0, 1, 0, 1)):
            representatives["configure_two", args] = args
        for label, args in representatives.items():
            op = label if isinstance(label, str) else label[0]
            annotated = {}
            stabilizer = None
            for ordered in {tuple(args[i] for i in permuted)
                            for permuted in ARGUMENT_ORDERS[op]}:
                marks = tuple(sum(1 << j for j, v in enumerate(ordered) if v == i)
                              for i in range(len(table)))
                key, _, colored = observation(table, marks)
                annotated[ordered] = key
                if ordered == args:
                    stabilizer = (len(colored.renamings)
                                  * prod(factorial(n) for n in colored.sizes))
            orderings_reached = sum(x == annotated[args] for x in annotated.values())
            key, formula = action_class(graph, op, signature(tuple(blocks[v] for v in args), args))
            moved = tuple(order.index(v) for v in args)
            require(action_class(other_graph, op, signature(tuple(other_blocks[v] for v in moved), moved))
                    == (key, formula), ("transport", rooted, tests, op))
            require(group_size == stabilizer * orderings_reached * formula,
                    ("stabilizer", rooted, tests, op, args))
            checked[op] += 1
    return dict(sorted(checked.items()))


def check_erasure(world):
    """Compare exact projected sets, including deletion of the older probe."""
    tested = 0
    for rooted, tests in world.states:
        rows, width = allowed(rooted, tests)
        for index in range(len(tests)):
            p = (10 if rooted else 8) + 2 * index
            remaining = tests[:index] + tests[index + 1:]
            projected = {(row & ((1 << p) - 1)) | ((row >> (p + 2)) << p)
                         for row in rows}
            smaller, target_width = allowed(rooted, remaining)
            require(target_width == width - 2 and projected == smaller,
                    ("erase", rooted, tests, index))
            tested += 1
    return tested


def hidden_ranks(edges):
    ranks = {GOAL: 0}
    while True:
        add = {s: 1 + min(max(ranks[t] for t in targets) for targets in legal.values()
                           if targets <= ranks.keys())
               for s, legal in enumerate(edges) if s not in ranks and
               any(targets <= ranks.keys() for targets in legal.values())}
        if not add:
            return ranks
        ranks.update(add)


def conditional_conflict(world, obs, agencies):
    """Exhaust just five shared decisions, granting hidden-state advice everywhere else.

    At a partial choice, the ordinary reachability attractor grants each
    undecided occurrence its own move. A winning witness that uses two
    different moves at one observation forces a case split. Every addressed
    orbit occurring in any winning policy is among those cases.
    """
    examples = [((1, 8),), ((1, 8), (1, 8)), ((1, 8), (1, 9)),
                ((1, 8), (2, 8)), ((1, 8), (2, 9))]
    required = {obs[world.at(True, tests)] for tests in examples}
    require(len(required) == len(examples), "five distinct observations")
    initial = world.at(False, ())
    optimistic = hidden_ranks(agencies)
    usable = [{a: t for a, t in moves.items() if s not in t and t <= optimistic.keys()}
              for s, moves in enumerate(agencies)]
    options = {}
    for color in required:
        positions = [s for s in range(len(obs)) if obs[s] == color]
        # Duplicates have identical physical successors everywhere this
        # observation occurs, including which occurrences cannot use the move.
        effects = {}
        for a in sorted({a for s in positions for a in usable[s]}):
            effect = tuple(frozenset(usable[s][a]) if a in usable[s] else None
                           for s in positions)
            effects.setdefault(effect, a)
        options[color] = tuple(effects.values())

    def solve(enforced):
        nodes, leaves = 0, 0

        def visit(fixed):
            nonlocal nodes, leaves
            nodes += 1
            eligible = [({fixed[o]: moves[fixed[o]]} if fixed[o] in moves else {})
                        if o in fixed else moves for o, moves in zip(obs, usable)]
            ranks = hidden_ranks(eligible)
            if initial not in ranks:
                leaves += 1
                return False
            steps, reached, pending = {}, set(), [initial]
            while pending:
                s = pending.pop()
                if s in reached:
                    continue
                reached.add(s)
                best = min((max(ranks[t] for t in targets), a, targets)
                           for a, targets in eligible[s].items() if targets <= ranks.keys())
                _, action, targets = best
                require(all(ranks[t] < ranks[s] for t in targets), "attractor witness")
                o = obs[s]
                if o in enforced:
                    if o in steps and steps[o] != action:
                        require(o not in fixed, "conflict on previously fixed action")
                        return any(visit({**fixed, o: a}) for a in options[o])
                    steps[o] = action
                pending.extend(sorted(targets - reached - {GOAL}))
            return True

        result = visit({})
        return {"uniformly_winning": result, "searched_prefixes": nodes,
                "leaves_lost_even_with_hidden_chooser": leaves}

    all_five = solve(required)
    if not all_five["uniformly_winning"]:
        leave_one_out = {o: solve(required - {o})["uniformly_winning"] for o in sorted(required)}
    else:
        leave_one_out = {}
    return {"representative_rooted_tests": examples, "all_five": all_five,
            "wins_if_one_shared_observation_is_relaxed": leave_one_out}


def cycle_model(initial, obs, agencies):
    """Require physical closure and rule out every reachable nonterminal cycle.

    The Boolean solver chooses a single action per observed table. Each arc
    of a reached chosen orbit must remain active. Any witness cycle forbids
    precisely its simultaneous arcs, regardless of which actions supply them.
    These cuts exclude no winning policy. There are finitely many such cycles.
    """
    ranks = hidden_ranks(agencies)
    answer = {"optimistic_initial_rank": ranks.get(initial),
              "optimistically_winning_types": len(ranks) - 1}
    if initial not in ranks:
        return {**answer, "uniform_policy": False}
    usable = {s: {action: targets for action, targets in agencies[s].items()
                  if s not in targets and targets <= ranks.keys()}
              for s in ranks if s != GOAL}
    reached = {initial}
    pending = [initial]
    while pending:
        s = pending.pop()
        for t in set().union(*usable[s].values()) - reached - {GOAL}:
            pending.append(t)
            reached.add(t)
    answer["types_reachable_after_optimistic_pruning"] = len(reached)

    variables = IDPool()
    active = {s: variables.id(("live", s)) for s in reached}
    actions = {(obs[s], a): variables.id(("action", obs[s], a))
               for s in reached for a in usable[s]}
    by_observation = defaultdict(list)
    for (o, _), var in actions.items():
        by_observation[o].append(var)
    with Solver(name="cadical195") as solver:
        solver.add_clause([active[initial]])
        for options in by_observation.values():
            if len(options) > 1:
                at_most_one = CardEnc.atmost(options, bound=1, vpool=variables,
                                             encoding=EncType.seqcounter)
                solver.append_formula(at_most_one.clauses)
        arcs = {(s, t): variables.id(("arc", s, t)) for s in reached
                for targets in usable[s].values() for t in targets if t != GOAL}
        adjacent = defaultdict(set)
        for (s, t), var in arcs.items():
            adjacent[s].add(t)
            solver.add_clause([-var, active[t]])
            if s < t and (t, s) in arcs:
                solver.add_clause([-var, -arcs[t, s]])
        # Exclude the length-three cycles eagerly as well.
        for s in sorted(reached):
            for t in sorted(adjacent[s]):
                if t > s:
                    for u in adjacent[t]:
                        if u > s and (u, s) in arcs:
                            solver.add_clause([-arcs[s, t], -arcs[t, u], -arcs[u, s]])
        for s in reached:
            o = obs[s]
            solver.add_clause([-active[s], *(actions[o, a] for a in usable[s])])
            for a, targets in usable[s].items():
                for t in targets - {GOAL}:
                    solver.add_clause([-active[s], -actions[o, a], arcs[s, t]])

        while solver.solve():
            model = {lit for lit in solver.get_model() if lit > 0}
            policy = {o: a for (o, a), var in actions.items() if var in model}
            stack, on_stack, seen, cycles = [], {}, set(), set()

            def visit(s):
                if s in on_stack:
                    cycles.add(tuple(stack[on_stack[s]:]))
                    return
                if s in seen:
                    return
                seen.add(s)
                on_stack[s] = len(stack)
                stack.append(s)
                for t in sorted(usable[s][policy[obs[s]]] - {GOAL}):
                    visit(t)
                stack.pop()
                del on_stack[s]

            visit(initial)
            if not cycles:
                return {**answer, "uniform_policy": True,
                        "all_reachable_winning_policy_ties_replayed": True}
            for cycle in sorted(cycles):
                pairs = zip(cycle, cycle[1:] + cycle[:1])
                solver.add_clause([-arcs[s, t] for s, t in pairs])
    return {**answer, "uniform_policy": False}


def simultaneous_policy(world, tables, obs, edges):
    # Each row prescribes an orbit on the scalar table of the given fixture.
    # The usable controller keys are the anonymous observations and patterns.
    prescriptions = [
        (False, (), "root", (0,)),
        (True, (), "configure_two", (0, 1, 0, 2)),
        (True, ((0, 1), (0, 2)), "second", (0, 1)),
        (True, ((0, 1), (0, 3)), "second", (0, 1)),
        (True, ((0, 1), (0, 6)), "second", (0, 1)),
        (True, ((0, 1), (0, 7)), "second", (0, 1)),
        (True, ((0, 3), (0, 5)), "second", (0, 1)),
        (True, ((0, 3), (0, 7)), "configure_two", (0, 1, 0, 2)),
    ]
    results = {}
    for horizontal in (False, True):
        decisions, rows = {}, []
        for rooted, tests, op, args in prescriptions:
            s = world.at(rooted, tests)
            require(world.states[s] == (rooted, tests), "physical witness naming")
            if horizontal and op == "second":
                args = (8, args[1])
            table = tables[s]
            _, cells, quotient = observation(table, (0,) * len(table))
            key, ties = action_class(quotient, op, signature(tuple(cells[v] for v in args), args))
            require(obs[s] not in decisions, "two prescriptions on the same anonymous table")
            require(key in edges[s], "unsafe action orbit")
            if horizontal and op == "second":
                horizontal_ties = [
                    operand for operation, operand, _ in physical_moves(world, rooted, tests, ())
                    if operation == op and operand[0] in PORTS and action_class(
                        quotient, op, signature(tuple(cells[v] for v in operand), operand))[0] == key
                ]
                require(len(horizontal_ties) == ties, "a tie can use the designated original")
            decisions[obs[s]] = key
            rows.append({"rooted": rooted, "tests": tests, "representative": [op, args],
                         "orbit_size": ties})
        levels, visited = {GOAL: 0}, set()

        def finish(s):
            if s in levels:
                return levels[s]
            require(s not in visited, "policy cycle")
            visited.add(s)
            move = decisions[obs[s]]
            levels[s] = 1 + max(finish(t) for t in edges[s][move])
            return levels[s]

        highest = finish(world.at(False, ()))
        require(highest == 4 and len(visited) == len(decisions), "policy depth or domain")
        results["horizontal" if horizontal else "via_root"] = {"longest_play": highest, "rows": rows}
    return {"uniform_policy": True, "optimistic_initial_rank": hidden_ranks(edges)[world.at(False, ())],
            "replayed_policies": results}


def run():
    world = Physical()
    tables = [distance_table(*allowed(*s)) for s in world.states]
    initial = world.at(False, ())
    record = {"named_physical_positions": world.labeled_count, "physical_types": len(world.states),
              "projected_erased_probe_laws": check_erasure(world),
              "point_and_set_stabilizer_checks": check_stabilizers(world, tables),
              "variants": {}}
    cases = {"addressed": (),
             "automatic_clear_either_or_all_and_replace_either": ("arbitrary", "clear"),
             "also_replace_all_with_one": ("arbitrary", "clear", "replace_all"),
             "initial_two_at_once": ("initial_batch",),
             "reconfigure_two_at_any_stage": ("batch",)}
    for name, extras in cases.items():
        obs, edges = frame(world, tables, extras)
        require(len(set(obs)) == 73 and len(world.states) == 225, "census changed")
        record["full_scalar_observations"] = len(set(obs))
        if name == "reconfigure_two_at_any_stage":
            report = simultaneous_policy(world, tables, obs, edges)
        else:
            report = cycle_model(initial, obs, edges)
        if name in ("addressed", "initial_two_at_once"):
            report["solver_free_five_table_certificate"] = conditional_conflict(world, obs, edges)
            certificate = report["solver_free_five_table_certificate"]
            require(not certificate["all_five"]["uniformly_winning"]
                    and all(certificate["wins_if_one_shared_observation_is_relaxed"].values()),
                    "conditional obstruction or positive relaxation failed")
        expected = name in ("also_replace_all_with_one", "reconfigure_two_at_any_stage")
        require(report["uniform_policy"] == expected, (name, report["uniform_policy"]))
        record["variants"][name] = report
    return record


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
