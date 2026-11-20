"""Fixed-radius tied exchange on the two-five-ring source family."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import product
from math import comb, prod
from pathlib import Path
from random import Random
import json

from sources import DATA, ReturnRule, cases, co_knotted_pairs, source_and_stage
from nearness import distances
from exchange import support_key, push, xor_all


OUT = DATA / "uniform_exchange.json"
ARM_LIMIT = 30
DYNAMIC_HOLDER_RADIUS = 8
STATIC_NEARNESS_RADIUS = 40
QUOTIENT_CAP = 20_000
ORDERS = (193, 347, 401, 683)


@dataclass(frozen=True)
class Attachment:
    center: int
    inward: int
    ring_knots: tuple[int, ...]
    ring: tuple[int, ...]
    entry: frozenset[int]
    completing: tuple[tuple[int, frozenset[int]], ...]
    common: int
    marker: frozenset[int]
    pulse: frozenset[int]
    outside_length: int


class UniformSwitch:
    """One local check at a time on a nearness-only holder reconstruction."""

    def __init__(self, rule, *, outside_guard=False):
        self.rule = rule
        self.stage = rule.stage
        self.graph = rule.graph
        self.outside_guard = outside_guard
        self.shared = {
            v: {w: self.stage.bundles[v][w][0] for w in row}
            for v, row in self.graph.items()
        }
        self.raw = frozenset(d for row in self.shared.values() for d in row.values())
        self.inputs = {
            v: {self.stage.bundles[v][w][0]: w for w in rule.full[v] - rule.source}
            for v in self.graph
        }
        self.loose = {v: frozenset(self.stage.stars[v]) & self.stage.loose
                      for v in set(rule.full) - rule.source}
        self.attachments = {v: self.attachment(v) for v, row in self.graph.items() if len(row) == 4}
        self.ring_knots = frozenset(v for item in self.attachments.values() for v in item.ring_knots)
        self.completing = {v: (item, event)
                          for item in self.attachments.values() for v, event in item.completing}
        self.cleanup_mark = {item.common: item for item in self.attachments.values()}
        correction = defaultdict(list)
        for item in self.attachments.values():
            around = self.old_ball(item.center, 4)
            for bit in item.pulse:
                assert {v for v in self.stage.owners[bit] if v in self.graph} <= around
                correction[bit].append(item)
            assert all(around & set(self.stage.owners[bit]) for bit in item.marker)
        self.correction = dict(correction)
        self.axial = {
            v: self.rule.packet((u, v, w))
            for v, row in self.graph.items() if len(row) == 2 and v not in self.ring_knots
            for u, w in (tuple(row),)
        }
        self.outside_strays = {
            v for v in self.axial if outside_guard and any(
                self.end_before_attachment(v, w) is not None for w in self.graph[v]
            )
        }
        self.max_dynamic_read = 0

    @cache
    def old_ball(self, center, radius):
        return frozenset(distances(self.graph, center, cap=radius))

    def follow(self, root, leg, budget):
        route = [root, leg]
        while len(route) - 1 < budget and len(self.graph[route[-1]]) == 2:
            if route[-1] == root:
                break
            w, = self.graph[route[-1]] - {route[-2]}
            route.append(w)
        return tuple(route)

    def end_before_attachment(self, root, leg):
        route = self.follow(root, leg, ARM_LIMIT)
        return route if len(self.graph[route[-1]]) == 1 else None

    def attachment(self, at):
        returning = [self.follow(at, leg, 5) for leg in self.graph[at]]
        returning = [path for path in returning if len(path) == 6 and path[-1] == at]
        assert len(returning) == 2 and returning[0] == returning[1][::-1]

        def spare(path):
            i, = (i for i, v in enumerate(path[1:-1], 1)
                  if any(len(self.rule.full[c]) == 1 for c in self.inputs[v].values()))
            return i

        a, b = map(spare, returning)
        assert {a, b} == {2, 3}
        ring = min(returning, key=spare)
        bits = tuple(self.shared[u][v] for u, v in zip(ring, ring[1:]))
        ring_legs = {ring[1], ring[-2]}
        other = self.graph[at] - ring_legs
        outside, = (route for leg in other if (route := self.end_before_attachment(at, leg)) is not None)
        assert 4 <= len(outside) - 1 <= ARM_LIMIT
        inward, = other - {outside[1]}
        inner = self.follow(at, inward, 2)
        assert len(inner) == 3
        first = self.rule.packet(outside[2:5])
        second = self.rule.packet(outside[1:4])
        lead = self.rule.packet(inner)
        marker = (first | second) - self.raw
        pulse = first ^ second ^ lead
        assert len(marker) == 4 and marker <= pulse and len(pulse) == 10
        entry = self.rule.packet((ring[1], at, inward))
        completing = ((ring[2], self.rule.packet(ring[1:4])),
                      (ring[4], self.rule.packet(ring[3:6])))
        return Attachment(at, inward, ring[:-1], bits, entry, completing, ring[3], marker, pulse,
                          len(outside) - 1)

    @cache
    def physical_steps(self, v):
        # For the observer's radius audit only, not for choosing a firing.
        return distances(self.rule.full, v, cap=DYNAMIC_HOLDER_RADIUS)

    def enabled_at(self, v, state, *, audit=False):
        observed = set()
        seen_markers = {}

        def bit(d):
            if audit:
                observed.add(d)
            return d in state

        def marked(item):
            if item.center not in seen_markers:
                seen_markers[item.center] = all(bit(d) for d in item.marker)
            return seen_markers[item.center]

        def relative(d):
            lit = bit(d)
            return lit ^ (sum(marked(item) for item in self.correction.get(d, ())) % 2 == 1)

        def ring_total(item):
            return sum(bit(d) for d in item.ring)

        def private_clear(label):
            return not any(relative(d) for d in label - self.raw)

        result = set()
        if (item := self.attachments.get(v)) is not None:
            lit = relative(self.shared[v][item.inward])
            raw = ring_total(item)
            if ((marked(item) and raw == 5 and not lit)
                    or (not marked(item) and raw == 0 and lit)):
                if private_clear(item.entry):
                    result.add(item.entry)
        elif v in self.completing:
            item, move = self.completing[v]
            selected = bit(item.ring[0])
            pair = sum(bit(d) for d in move & self.raw)
            if ((marked(item) and not selected and pair == 2)
                    or (not marked(item) and selected and pair == 0)):
                if private_clear(move):
                    result.add(move)
        elif v in self.axial and v not in self.outside_strays:
            move = self.axial[v]
            if sum(relative(d) for d in self.shared[v].values()) == 1 and private_clear(move):
                for neighbor in self.graph[v]:
                    gate = self.attachments.get(neighbor)
                    if gate is not None and gate.inward == v and marked(gate) and ring_total(gate):
                        break
                else:
                    result.add(move)

        active = [(d, child) for d, child in self.inputs[v].items() if relative(d)]
        if len(active) == 2:
            ((a, u), (b, w)) = active
            assert u != w
            loose_u = [d for d in self.loose[u] if bit(d)]
            loose_w = [d for d in self.loose[w] if bit(d)]
            item = self.cleanup_mark.get(v)
            donor_wait = item is not None and marked(item)
            seed = item is not None and not marked(item) and ring_total(item) == 5
            ready = bool(loose_u and loose_w) if donor_wait else seed or bool(loose_u or loose_w)
            if ready and len(loose_u) <= 1 and len(loose_w) <= 1:
                result.update(frozenset((a, b, x, y)) for x, y in product(
                    loose_u or self.loose[u], loose_w or self.loose[w]))

        if audit:
            near = self.physical_steps(v)
            assert all(any(u in near for u in self.stage.owners[d]) for d in observed)
            radius = max((min(near[u] for u in self.stage.owners[d] if u in near)
                          for d in observed), default=0)
            self.max_dynamic_read = max(self.max_dynamic_read, radius)
        return result

    def enabled(self, state, *, audit=False):
        """The harness visits all possible event centers. Each center reads its own guard."""
        return set().union(*(self.enabled_at(v, state, audit=audit) for v in self.graph))


def chosen_source(d, left, right):
    assert d >= 4 and 4 <= left <= ARM_LIMIT and 4 <= right <= ARM_LIMIT
    count = left + d + right + 1
    path = list(range(count))
    seams = [left, left + d]
    rings = [[at, *range(count + 4 * i, count + 4 * i + 4)] for i, at in enumerate(seams)]
    meetings = list(map(list, zip(path, path[1:])))
    anchors = list(range(len(meetings)))
    ring_edges = []
    for row in rings:
        first = len(meetings)
        meetings.extend([u, v] for u, v in zip(row, row[1:] + row[:1], strict=True))
        ring_edges.append(list(range(first, len(meetings))))
    background_spares = [0, 1, count - 2, count - 1]
    ring_spares = [[row[2]] for row in rings]
    loose_addition = set(background_spares) | {row[0] for row in ring_spares}
    adjacency = [set() for _ in range(count + 8)]
    for u, v in meetings:
        adjacency[u].add(v)
        adjacency[v].add(u)
    sizes = [len(row) + sum(len(adjacency[u]) - 1 for u in row) + (v in loose_addition)
             for v, row in enumerate(adjacency)]
    return {"id": f"d{d}-arms{left}-{right}", "sizes": sizes, "meetings": meetings,
            "roles": {"background": path, "rings": rings, "seams": seams, "ring_edges": ring_edges,
                      "anchors": anchors, "background_spares": background_spares, "ring_spares": ring_spares}}


def named_fixture(spec):
    literal, recovered = source_and_stage(spec)
    owners = {frozenset(row): u for u, row in enumerate(recovered.stars)}
    expected, other = (owners[frozenset(literal[u])] for u in spec["roles"]["seams"])
    model = UniformSwitch(recovered)
    source, final = model.attachments[expected], model.attachments[other]
    assert tuple(map(frozenset, spec["roles"]["ring_edges"])) == (frozenset(source.ring), frozenset(final.ring))
    path = [owners[frozenset(literal[u])] for u in spec["roles"]["background"]]
    s = spec["roles"]["background"].index(spec["roles"]["seams"][0])
    actual = xor_all(recovered.packet(path[i - 1:i + 2]) for i in (s - 3, s - 2, s + 1))
    assert actual == source.pulse
    return model, source, final, path


def minimum_event(model, event):
    assert len(event) == 4
    mark = min(event - model.stage.loose)
    assert event in model.stage.minimum_response(mark).supports


def origin_and_goal(donor, receiver):
    return donor.pulse ^ frozenset(donor.ring), donor.pulse ^ frozenset(receiver.ring)


def run_order(model, donor, receiver, separation, seed, *, audit=True, keep=False):
    state, goal = origin_and_goal(donor, receiver)
    assert model.stage.allowed_change(state)
    rng = Random(seed)
    expected = 2 * (separation + 5)
    moves = []
    states = [state]
    old_step = set()
    before_cleanup = None
    kinds = Counter()
    widths = Counter()
    for i in range(expected):
        available = sorted(model.enabled(state, audit=audit), key=support_key)
        assert available
        widths[len(available)] += 1
        event = available[rng.randrange(len(available))]
        minimum_event(model, event)
        key = event - model.stage.loose
        assert key not in old_step
        old_step.add(key)
        kind = "cleanup" if event & model.stage.loose else "ordinary"
        kinds[kind] += 1
        if kind == "cleanup" and before_cleanup is None:
            before_cleanup = i
        state ^= event
        assert model.stage.allowed_change(state)
        if keep:
            moves.append(event)
            states.append(state)
    assert state == goal and not model.enabled(state, audit=audit)
    assert kinds == {"ordinary": separation + 5, "cleanup": separation + 5}
    assert before_cleanup == separation + 5
    if keep:
        by_center = {v: model.enabled_at(v, states[-2]) for v in model.graph}
        assert by_center[donor.common] == {moves[-1]}
        assert all(not row for v, row in by_center.items() if v != donor.common)
    result = {"seed": seed, "elementary_events": expected, "ordinary": kinds["ordinary"],
              "cleanup": kinds["cleanup"], "menu_sizes": dict(sorted(widths.items())),
              "exact_target": sorted(state)}
    if keep:
        result["literal_steps"] = [sorted(row) for row in moves]
    return result, states, moves


def exhaustive(model, donor, receiver, separation):
    """Search the exact finite quotient by loose-sibling permutations."""
    start, goal = origin_and_goal(donor, receiver)
    expected = 2 * (separation + 5)

    def normalize(state):
        chosen = state - model.stage.loose
        return chosen | frozenset(
            bit for loose in model.loose.values() for bit in sorted(loose)[:len(loose & state)]
        )

    steps = {start: frozenset()}
    agenda = [start]
    outcomes = []
    transitions = literal = physical = tied = 0
    for state in agenda:
        if len(agenda) > QUOTIENT_CAP:
            raise RuntimeError("uniform exchange quotient exceeded its bound")
        neighbors = set()
        used = steps[state]
        moves = model.enabled(state, audit=True)
        for event in moves:
            minimum_event(model, event)
            key = event - model.stage.loose
            assert key not in used
            nxt = normalize(state ^ event)
            assert model.stage.allowed_change(nxt)
            history = used | {key}
            if nxt in steps:
                assert steps[nxt] == history
            else:
                steps[nxt] = history
                agenda.append(nxt)
            neighbors.add(nxt)
        literal += len(moves)
        tied += len(moves) > len(neighbors)
        transitions += len(neighbors)
        physical += prod(comb(len(loose), len(loose & state)) for loose in model.loose.values())
        if not moves:
            assert state == goal and len(used) == expected
            outcomes.append(state)
    assert outcomes == [goal]

    # Independently traverse the literal names to check the sibling quotient.
    physical_agenda = [start]
    physical_depth = {start: 0}
    physical_arcs = 0
    physical_terminals = []
    for state in physical_agenda:
        if len(physical_agenda) > physical:
            raise RuntimeError("literal traversal disagrees with the sibling orbit count")
        moves = model.enabled(state, audit=True)
        physical_arcs += len(moves)
        for event in moves:
            nxt = state ^ event
            depth = physical_depth[state] + 1
            if nxt not in physical_depth:
                physical_agenda.append(nxt)
                physical_depth[nxt] = depth
            assert physical_depth[nxt] == depth
            assert normalize(nxt) in steps and len(steps[normalize(nxt)]) == depth
        if not moves:
            physical_terminals.append((state, physical_depth[state]))
    assert len(physical_agenda) == physical
    assert physical_terminals == [(goal, expected)]
    return {"quotient_states": len(agenda), "quotient_transitions": transitions,
            "literal_menus_summed_over_representatives": literal,
            "physical_states_from_exact_sibling_orbit_sizes": physical,
            "direct_literal_states": len(physical_agenda), "direct_literal_transitions": physical_arcs,
            "quotient_states_with_tied_loose_choices": tied,
            "terminals": len(outcomes), "minimum_and_maximum_event_count": [expected, expected]}


def recoding_control(model, states, moves, seed):
    rng = Random(seed)
    names = list(model.stage.owners)
    recoded = [101 + 7 * i for i in range(len(names))]
    rng.shuffle(recoded)
    change = dict(zip(names, recoded, strict=True))
    scrambled = [[change[d] for d in row] for row in model.stage.stars]
    rng.shuffle(scrambled)
    for row in scrambled:
        rng.shuffle(row)
    check = UniformSwitch(ReturnRule(co_knotted_pairs(scrambled)), outside_guard=model.outside_guard)
    actual = push(states[0], change)
    for i, state in enumerate(states):
        assert push(state, change) == actual
        wanted = {push(event, change) for event in model.enabled(state)}
        assert check.enabled(actual, audit=True) == wanted
        if i < len(moves):
            minimum_event(check, push(moves[i], change))
            actual ^= push(moves[i], change)
        else:
            assert not wanted
    return {"seed": seed, "matched_menus": len(states), "max_observed_dynamic_holder_steps": check.max_dynamic_read}


def controls(model, donor, receiver, path, separation):
    quiet = frozenset()
    raw_donor = frozenset(donor.ring)
    raw_receiver = frozenset(receiver.ring)
    start, target = origin_and_goal(donor, receiver)
    fixtures = {
        "all_zero": quiet,
        "stored_first_ring_without_arrival": raw_donor,
        "stored_second_ring_without_arrival": raw_receiver,
        "arrival_without_stored_ring": donor.pulse,
        "proper_arrival_with_empty_receiver": start,
        "both_rings_loaded_with_arrival": start ^ raw_receiver,
        "terminal": target,
    }
    report = {}
    for key, row in fixtures.items():
        assert model.stage.allowed_change(row)
        menu = model.enabled(row, audit=True)
        report[key] = {"enabled": len(menu), "literal_supports": [sorted(q) for q in sorted(menu, key=support_key)]}
    assert all(report[key]["enabled"] == 0 for key in (
        "all_zero", "stored_first_ring_without_arrival", "stored_second_ring_without_arrival",
        "arrival_without_stored_ring", "terminal"))
    assert report["proper_arrival_with_empty_receiver"] == report["both_rings_loaded_with_arrival"]
    assert report["proper_arrival_with_empty_receiver"]["enabled"] == 1
    blocked = fixtures["both_rings_loaded_with_arrival"]
    for _ in range(separation + 2):
        menu = model.enabled(blocked, audit=True)
        assert menu and all(not (event & model.stage.loose) for event in menu)
        blocked ^= min(menu, key=support_key)
        assert model.stage.allowed_change(blocked)
    assert not model.enabled(blocked, audit=True)
    assert (blocked & raw_receiver) == raw_receiver and not (blocked & raw_donor)
    assert model.shared[receiver.center][receiver.inward] in blocked
    report["both_rings_loaded_with_arrival"].update(
        {"one_replay_stalls_after_events": separation + 2, "blocked_literal_state": sorted(blocked)})
    if donor.outside_length >= 7:
        stems = (1, 2, 5)
        fully_outside = xor_all(model.rule.packet(path[i - 1:i + 2]) for i in stems)
        assert len(fully_outside) == 10
        launch = fully_outside ^ raw_donor
        assert model.stage.allowed_change(launch)
        raw_menu = model.enabled(launch, audit=True)
        gated = UniformSwitch(model.rule, outside_guard=True)
        gate_menu = gated.enabled(launch, audit=True)
        report["independent_wholly_outside_launch"] = {
            "source_path_centers": stems,
            "base_guard_enabled": len(raw_menu),
            "exterior_end_exclusion_enabled": len(gate_menu),
            "base_guard_supports": [sorted(q) for q in sorted(raw_menu, key=support_key)],
        }
    return report


def measurement(spec, *, full_quotient=False):
    model, donor, receiver, path = named_fixture(spec)
    separation = spec["roles"]["seams"][1] - spec["roles"]["seams"][0]
    samples = []
    kept = None
    for i, seed in enumerate(ORDERS):
        row, states, moves = run_order(model, donor, receiver, separation, seed, keep=(i == 0))
        samples.append(row)
        if i == 0:
            kept = states, moves
    restricted = UniformSwitch(model.rule, outside_guard=True)
    other, _, _ = run_order(restricted, donor, receiver, separation, ORDERS[0])
    opposing, _, _ = run_order(model, receiver, donor, separation, ORDERS[-1])
    start, target = origin_and_goal(donor, receiver)
    near = co_knotted_pairs(model.stage.stars)
    seam_gap = min(distances(near, d)[e] for d in model.stage.stars[donor.center]
                   for e in model.stage.stars[receiver.center])
    report = {
        "source_arm_lengths": [donor.outside_length, receiver.outside_length],
        "separation_old_knot_steps": separation, "size_two_knots": len(model.stage.stars),
        "co_knotted_steps_between_seam_supports": seam_gap,
        "size_two_distinctions": len(model.stage.owners),
        "donor_pulse": sorted(donor.pulse), "initial": sorted(start), "target": sorted(target),
        "sampled_orders": samples, "outside_end_exclusion_replay": other, "reflected_arrival_replay": opposing,
        "controls": controls(model, donor, receiver, path, separation),
        "neighborhood_verification": [recoding_control(model, *kept, seed) for seed in (701, 911)],
        "max_observed_dynamic_full_holder_steps": model.max_dynamic_read,
    }
    if full_quotient:
        report["all_sibling_quotient_outcomes"] = exhaustive(model, donor, receiver, separation)
        report["max_observed_dynamic_full_holder_steps"] = model.max_dynamic_read
    return report


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--known-only", action="store_true")
    args = parser.parse_args()
    indexed = {row["id"]: row for row in cases()}
    known = [indexed[name] for name in ("T4", "T8", "T81")]
    fresh = [
        chosen_source(d, left, right)
        for d, left, right in ((31, 4, 30), (32, 30, 4), (47, 17, 23), (80, 4, 30), (97, 30, 4))
    ]
    rows = known if args.known_only else known + fresh
    record = {
        "abstraction": "All events use an anonymous current-state local reader. The harness visits event centers.",
        "caps": {
            "arm_limit_old_knot_steps": ARM_LIMIT,
            "proved_dynamic_full_holder_steps_to_at_least_one_holder_of_each_read_distinction": DYNAMIC_HOLDER_RADIUS,
            "conservative_full_co_knotted_step_radius_from_the_center_support": STATIC_NEARNESS_RADIUS,
            "T4_quotient_state_limit": QUOTIENT_CAP,
        },
        "case_specs": {r["id"]: r for r in ([] if args.known_only else fresh)},
        "cases": {r["id"]: measurement(r, full_quotient=(r["id"] == "T4")) for r in rows},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
