"""Literal ring-state exchange, symmetry, and all-outcome cleanup checks."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import cached_property
from hashlib import sha256
from itertools import combinations, product
import json
from math import factorial, prod
from pathlib import Path
from random import Random
import sys
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = "MOTION-AT-EDDY-20261119-001"
PRIOR_FAMILY = PRIOR + "-E001_motion"
sys.path.insert(0, str(ROOT / "experiments" / PRIOR / PRIOR_FAMILY))
from motion_stage import MotionStage, load_marks, load_stage


OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "exchange.json"
CASES = ("T4", "T8", "T81")
GROUP_LIMIT = 100_000
T4_OUTCOME_LIMIT = 20_000


def support_key(support):
    return tuple(sorted(support))


def xor_all(rows):
    result = set()
    for row in rows:
        result.symmetric_difference_update(row)
    return frozenset(result)


def push(support, names):
    return frozenset(names[bit] for bit in support)


def shortest_paths(adjacency, first):
    distance = {first: 0}
    predecessor = {}
    pending = deque([first])
    while pending:
        at = pending.popleft()
        for other in adjacency[at]:
            if other not in distance:
                distance[other] = distance[at] + 1
                predecessor[other] = at
                pending.append(other)
    return distance, predecessor


class Exchange:
    """Anonymous size-two incidence and all primitive minimum changes."""

    def __init__(self, stage):
        self.stage = stage
        self.loose_at = {v: frozenset(row) & stage.loose for v, row in enumerate(stage.stars)}
        self.young = {v for v, names in self.loose_at.items() if names}
        self.old = set(range(len(stage.stars))) - self.young
        self.raw = frozenset(bit for bit, ends in stage.owners.items()
                             if len(ends) == 2 and set(ends) <= self.old)
        self.rooms = {v: {} for v in self.old}
        self.inputs_at = {v: {} for v in self.old}
        self.child_of = {}
        self.child_inputs = {v: set() for v in self.young}
        for bit, ends in stage.owners.items():
            if bit in self.raw:
                u, v = ends
                assert v not in self.rooms[u]
                self.rooms[u][v] = self.rooms[v][u] = bit
            elif len(ends) == 2:
                a, = set(ends) & self.old
                b, = set(ends) & self.young
                assert b not in self.inputs_at[a]
                self.inputs_at[a][b] = bit
                self.child_of[bit] = b
                self.child_inputs[b].add(bit)
        assert all(len(self.child_inputs[v]) in (1, 2) and len(self.loose_at[v]) >= 2 for v in self.young)
        self.quads = {row & self.raw: row for row in stage.ordinary_quads()}
        assert len(self.quads) == len(stage.ordinary_quads()) and all(len(k) == 2 for k in self.quads)
        self.private = {row: row - self.raw for row in self.quads.values()}
        assert set().union(*self.private.values()) == {
            bit for v, names in self.child_inputs.items() if len(names) == 2 for bit in names
        }

    @cached_property
    def events(self):
        two = {frozenset(pair) for row in self.loose_at.values() for pair in combinations(row, 2)}
        exposed = set()
        for row in self.inputs_at.values():
            for (u, a), (v, b) in combinations(row.items(), 2):
                exposed.update(frozenset((a, b, x, y)) for x, y in product(self.loose_at[u], self.loose_at[v]))
        ordinary = set(self.quads.values())
        direct = set()
        for bit in self.stage.owners:
            minima = self.stage.minimum_response(bit)
            assert minima.minimum_size in (2, 4) and minima.listed_all_supports
            direct.update(minima.supports)
        assert direct == two | exposed | ordinary
        return {"ordinary_four": tuple(sorted(ordinary, key=support_key)),
                "exterior_four": tuple(sorted(exposed, key=support_key)),
                "loose_two": tuple(sorted(two, key=support_key))}

    def exterior_cleanups(self, relative):
        choices = {}
        for v in self.young:
            active = self.loose_at[v] & relative
            choices[v] = (active or self.loose_at[v]) if len(active) <= 1 else ()
        result = set()
        for row in self.inputs_at.values():
            current = [(v, bit) for v, bit in row.items() if bit in relative]
            for (u, a), (v, b) in combinations(current, 2):
                result.update(frozenset((a, b, x, y)) for x, y in product(choices[u], choices[v]))
        return result

    def colored_holder_maps(self, state):
        """Complete automorphisms of weighted holder incidence with the state fixed."""
        n = len(self.stage.stars)
        edges = [defaultdict(Counter) for _ in range(n)]
        for bit, ends in self.stage.owners.items():
            if len(ends) == 2:
                u, v = ends
                color = int(bit in state)
                edges[u][v][color] += 1
                edges[v][u][color] += 1
        graph = [{v: (count[0], count[1]) for v, count in row.items()} for row in edges]
        colors = [(len(self.loose_at[v] - state), len(self.loose_at[v] & state)) for v in range(n)]
        while True:
            signature = [(colors[u], tuple(sorted((mark, colors[v]) for v, mark in graph[u].items())))
                         for u in range(n)]
            palette = {key: i for i, key in enumerate(sorted(set(signature)))}
            refined = [palette[key] for key in signature]
            if len(palette) == len(set(colors)):
                colors = refined
                break
            colors = refined
        classes = defaultdict(list)
        for v, c in enumerate(colors):
            classes[c].append(v)
        chosen = {group[0]: group[0] for group in classes.values() if len(group) == 1}
        remaining = set(range(n)) - chosen.keys()
        used = set(chosen.values())
        visits = 0
        found = []

        def recurse():
            nonlocal visits
            visits += 1
            if visits > GROUP_LIMIT:
                raise RuntimeError("holder automorphism check exceeded its exact search cap")
            if not remaining:
                found.append(tuple(chosen[v] for v in range(n)))
                return
            options = []
            for u in remaining:
                possible = [v for v in classes[colors[u]] if v not in used and all(
                    graph[u].get(p) == graph[v].get(q) for p, q in chosen.items()
                )]
                if not possible:
                    return
                options.append((len(possible), u, possible))
            _, u, possible = min(options)
            remaining.remove(u)
            for v in possible:
                chosen[u] = v
                used.add(v)
                recurse()
                used.remove(v)
                del chosen[u]
            remaining.add(u)

        recurse()
        assert found and all(all({mapping[v]: w for v, w in graph[u].items()} == graph[mapping[u]]
                                 for u in range(n)) for mapping in found)
        return found, visits

    def stabilizer(self, state, *, record_swaps=False):
        classes = defaultdict(list)
        for bit, holders in self.stage.owners.items():
            classes[holders, bit in state].append(bit)
        holder_maps, visits = self.colored_holder_maps(state)
        lifts = []
        for holders in holder_maps:
            lifted = {}
            for (ends, value), names in classes.items():
                goal = classes[tuple(sorted(holders[v] for v in ends)), value]
                lifted.update(zip(sorted(names), sorted(goal), strict=True))
            assert push(state, lifted) == state
            assert all(push(row, lifted) == frozenset(self.stage.stars[holders[v]])
                       for v, row in enumerate(self.stage.stars))
            lifts.append(lifted)
        class_of = {bit: tuple(sorted(names)) for names in classes.values() for bit in names}
        swaps = {}
        for v in sorted(self.young):
            parts = [sorted(self.loose_at[v] - state), sorted(self.loose_at[v] & state)]
            all_swaps = [list(pair) for fiber in parts for pair in combinations(fiber, 2)]
            assert all(self.stage.owners[a] == self.stage.owners[b] == (v,)
                       and (a in state) == (b in state) for a, b in all_swaps)
            swaps[str(v)] = {"zero": parts[0], "one": parts[1],
                             **({"swaps": all_swaps} if record_swaps else {}),
                             "swap_count": len(all_swaps)}
        def orbit_key(event):
            count = Counter(class_of[d] for d in event)
            return tuple(sorted(count.items()))
        receipt = {"holder_automorphisms": len(holder_maps), "search_visits": visits,
                   "literal_stabilizer_order": len(holder_maps) * prod(factorial(len(n)) for n in classes.values()),
                   "sibling_transpositions": sum(row["swap_count"] for row in swaps.values())}
        if record_swaps:
            receipt["children"] = swaps
            receipt["holder_maps"] = holder_maps
        return orbit_key, lifts, receipt

    def event_orbits(self, state, *, record_swaps=False):
        key, lifts, receipt = self.stabilizer(state, record_swaps=record_swaps)
        catalogs = {}
        for label, events in self.events.items():
            sibling = defaultdict(list)
            for event in events:
                sibling[key(event)].append(event)
            full_hist = Counter()
            fixed = set()
            done = set()
            for cls, group in sibling.items():
                if cls in done:
                    continue
                orbit = {key(push(group[0], lift)) for lift in lifts}
                done |= orbit
                size = sum(len(sibling[c]) for c in orbit)
                full_hist[size] += 1
                if size == 1:
                    fixed.add(group[0])
            catalogs[label] = fixed
            receipt[label] = {"events": len(events), "full_orbit_sizes": dict(sorted(full_hist.items())),
                              "individually_fixed": len(fixed)}
            if record_swaps:
                receipt[label]["fixed_supports"] = sorted(map(support_key, fixed))
        return catalogs, receipt

    @cached_property
    def path(self):
        end0, end1 = sorted(v for v in self.old if len(self.rooms[v]) == 1)
        _, parents = shortest_paths(self.rooms, end0)
        route = [end1]
        while route[-1] != end0:
            route.append(parents[route[-1]])
        return tuple(reversed(route))

    def ring(self, seam, path):
        """Read the orientation with the surplus offshoot closest to its first leg."""
        legs = sorted(set(self.rooms[seam]) - set(path))
        assert len(legs) == 2
        rotations = []
        for leg in legs:
            order = [seam, leg]
            while True:
                following, = set(self.rooms[order[-1]]) - {order[-2]}
                if following == seam:
                    break
                order.append(following)
            assert len(order) == 5
            spare, = (i for i, v in enumerate(order[1:], 1)
                      if any(len(self.child_inputs[h]) == 1 for h in self.inputs_at[v]))
            names = tuple(self.rooms[u][v] for u, v in zip(order, order[1:] + order[:1], strict=True))
            rotations.append((spare, names))
        assert rotations[0][0] != rotations[1][0]
        return min(rotations)[1]

    @cached_property
    def orientations(self):
        choices = []
        for path in (self.path, self.path[::-1]):
            starts = [i for i, v in enumerate(path) if len(self.rooms[v]) == 4]
            seam, far = starts
            r0, r1 = [self.ring(path[k], path) for k in starts]
            along = [self.rooms[u][v] for u, v in zip(path, path[1:])]
            axis = [None] + [self.quads[frozenset(pair)] for pair in zip(along, along[1:])]
            arrival = xor_all(axis[k] for k in (seam - 3, seam - 2, seam + 1))
            crossing = (r0[0], *along[seam:far], r1[0])
            matched = [*zip(crossing, crossing[1:]), (r0[1], r0[2]), (r0[3], r0[4]),
                       (r1[1], r1[2]), (r1[3], r1[4])]
            program = frozenset(self.quads[frozenset(pair)] for pair in matched)
            assert len(program) == far - seam + 5
            assert xor_all(q & self.raw for q in program) == frozenset(r0 + r1)
            assert len(arrival) == 10
            choices.append({"path": path, "seams": (seam, far), "rings": (r0, r1), "axis": axis,
                            "pulse": arrival, "program": program})
        return tuple(choices)

    def read_arrival(self, state):
        detected = []
        for direction in self.orientations:
            seam, _ = direction["seams"]
            outside = direction["axis"][1:seam]
            active = [i for i, q in enumerate(outside, 1) if self.private[q] <= state]
            if active == [seam - 3, seam - 2] and all(
                not (state & self.private[q]) or self.private[q] <= state for q in outside
            ):
                detected.append(direction)
        return detected[0] if len(detected) == 1 else None

    def eligible(self, state):
        """A relation using the arrival side and a structurally determined program."""
        direction = self.read_arrival(state)
        if direction is None:
            return set()
        relative = state ^ direction["pulse"]
        start, end = map(frozenset, direction["rings"])
        program = direction["program"]
        past = relative & self.raw
        if past == end:
            return self.exterior_cleanups(relative)
        if relative & self.stage.loose:
            return set()
        fired = {q for q in program if self.private[q] <= relative}
        if relative != xor_all([start, *fired]):
            return set()
        return program - fired

    def staged_program(self, direction):
        plan = tuple(sorted(direction["program"], key=support_key))
        pairs = {}
        for v, row in self.inputs_at.items():
            names = frozenset(row.values()) & set().union(*(self.private[q] for q in plan))
            if names:
                assert len(names) == 2
                pairs[v] = names
        assert len(plan) == len(pairs)
        quad_for = {bit: q for q in plan for bit in self.private[q]}
        done_basis = Span((q & self.raw for q in plan), self.stage.owners)
        assert len(done_basis.basis) == len(plan)
        return plan, pairs, quad_for, done_basis

    def eligible_interleaved(self, state, prepared):
        direction = self.read_arrival(state)
        if direction is None:
            return set()
        plan, pairs, quad_for, basis = prepared[direction["path"]]
        relative = state ^ direction["pulse"]
        z = (relative & self.raw) ^ frozenset(direction["rings"][0])
        decoded = basis.combination(z)
        if decoded is None or relative - self.raw - self.stage.loose - set(quad_for):
            return set()
        fired = {q for i, q in enumerate(plan) if decoded >> i & 1}
        swept = set()
        active_cleanup = set()
        for v, pair in pairs.items():
            flags = {(bit in relative) ^ (quad_for[bit] in fired) for bit in pair}
            if len(flags) != 1:
                return set()
            ready = all(quad_for[b] in fired for b in pair)
            if True in flags:
                if not ready:
                    return set()
                swept.add(v)
            elif ready:
                active_cleanup.add(pair)
        active_loose = Counter(self.child_of[bit] for v in swept for bit in pairs[v])
        if any(len(relative & self.loose_at[v]) != active_loose[v] % 2 for v in self.young):
            return set()
        cleaners = {row for row in self.exterior_cleanups(relative)
                    if row - self.stage.loose in active_cleanup}
        return (set(plan) - fired) | cleaners


class Span:
    def __init__(self, generators, coordinates):
        self.names = {bit: 1 << i for i, bit in enumerate(coordinates)}
        self.generators = tuple(generators)
        self.basis = {}
        for i, row in enumerate(self.generators):
            value, used = self.reduce(self.pack(row))
            if value:
                self.basis[value.bit_length() - 1] = value, used ^ (1 << i)

    def pack(self, support):
        return sum(self.names[bit] for bit in support)

    def reduce(self, value):
        used = 0
        for bit, (row, source) in sorted(self.basis.items(), reverse=True):
            if value >> bit & 1:
                value ^= row
                used ^= source
        return value, used

    def combination(self, support):
        residue, sources = self.reduce(self.pack(support))
        return sources if not residue else None

    def separating_support(self, target):
        residue, _ = self.reduce(self.pack(target))
        if not residue:
            return None
        test = residue & -residue
        witness = frozenset(bit for bit, unit in self.names.items() if self.reduce(unit)[0] & test)
        assert all(len(witness & row) % 2 == 0 for row in self.generators)
        assert len(witness & target) % 2 == 1
        return sorted(witness)


def atomic_orbits(exchange, direction):
    """XOR each entire orbit of the initial sibling group, a permissive subgroup test."""
    atoms = set()
    histogram = {}
    for category, rows in exchange.events.items():
        groups = defaultdict(list)
        for support in rows:
            loose_counts = Counter(exchange.stage.owners[b][0] for b in support & exchange.stage.loose)
            groups[(support - exchange.stage.loose, tuple(sorted(loose_counts.items())))].append(support)
        sizes = Counter()
        for (shared, composition), group in groups.items():
            physical = xor_all(group)
            if category == "loose_two":
                ((v, count),) = composition
                assert count == 2
                k = len(exchange.loose_at[v])
                expected = exchange.loose_at[v] if k % 2 == 0 else frozenset()
                assert len(group) == k * (k - 1) // 2 and expected == physical
            elif category == "exterior_four":
                (u, count_u), (v, count_v) = composition
                assert count_u == count_v == 1
                k, ell = len(exchange.loose_at[u]), len(exchange.loose_at[v])
                expected = (shared if k * ell % 2 else frozenset())
                expected |= exchange.loose_at[u] if ell % 2 else frozenset()
                expected |= exchange.loose_at[v] if k % 2 else frozenset()
                assert len(group) == k * ell and expected == physical
            else:
                assert not composition and len(group) == 1 and physical == shared
            assert exchange.stage.allowed_change(physical)
            if physical:
                atoms.add(physical)
            sizes[len(physical)] += 1
        histogram[category] = dict(sorted(sizes.items()))
    target = frozenset(direction["rings"][0] + direction["rings"][1])
    table = Span(sorted(atoms, key=support_key), exchange.stage.owners)
    return {"orbit_xor_weight_histograms": histogram, "atomic_span_rank": len(table.basis),
            "target_in_span": table.combination(target) is not None,
            "separating_parity_functional": table.separating_support(target)}


def mismatch(exchange, state):
    return frozenset(v for v in exchange.young if len(exchange.child_inputs[v] & state) % 2)


def closed_residue(exchange, state):
    if state & exchange.stage.loose:
        return None
    return (state ^ xor_all(q for q, private in exchange.private.items() if private <= state)) & exchange.raw


def replay(exchange, direction, *, interleave, keep_trace=False):
    reference = direction["pulse"]
    start, target = (reference ^ frozenset(ring) for ring in direction["rings"])
    state = start
    expected = 2 * len(direction["program"])
    phase = []
    history = []
    toggled = set()
    first_open = None
    prepared = {d["path"]: exchange.staged_program(d) for d in exchange.orientations}
    for _ in range(expected):
        available = (exchange.eligible_interleaved(state, prepared)
                     if interleave else exchange.eligible(state))
        assert available
        external = [q for q in available if q & exchange.stage.loose]
        # This ordering is only a witness, outside the enabled-event relation.
        move = max(external or available, key=support_key)
        event_identity = move - exchange.stage.loose
        assert event_identity not in toggled and len(move) == 4
        toggled.add(event_identity)
        before = state
        state ^= move
        phase.append("exterior" if external else "ordinary")
        assert exchange.stage.allowed_change(state)
        assert len(state & exchange.raw) % 2 == len(start & exchange.raw) % 2
        prior_mismatch = mismatch(exchange, state)
        prior_residue = closed_residue(exchange, state)
        prior_loose = state & exchange.stage.loose
        assert all(mismatch(exchange, state ^ q) == prior_mismatch
                   and closed_residue(exchange, state ^ q) == prior_residue
                   and (state ^ q) & exchange.stage.loose == prior_loose
                   for q in exchange.private)
        if keep_trace and first_open is None:
            fixed, total = exchange.event_orbits(before)
            picked = move in fixed["exterior_four" if external else "ordinary_four"]
            history.append({"move_index": len(phase), "move_is_fixed": picked,
                            "holder_automorphisms": total["holder_automorphisms"],
                            "sibling_transpositions": total["sibling_transpositions"],
                            "fixed_two_events": total["loose_two"]["individually_fixed"],
                            "fixed_exterior_events": total["exterior_four"]["individually_fixed"]})
            if state & exchange.stage.loose:
                first_open = state
        if keep_trace:
            # The actual selected support, not the pulse or ring name, identifies an event.
            assert move in exchange.events["exterior_four" if external else "ordinary_four"]
    final_menu = (exchange.eligible_interleaved(state, prepared) if interleave else exchange.eligible(state))
    assert not final_menu and state == target
    assert phase.count("ordinary") == phase.count("exterior") == expected // 2
    return {"events": expected, "order": phase, "start": sorted(start), "target": sorted(target),
            "first_open_support": sorted(first_open) if first_open is not None else None,
            "pinned_prefix_stabilizers": history}


def independent_trace(exchange, direction):
    """Concrete shortest witness with a different least orientation from the archive."""
    source, final = map(frozenset, direction["rings"])
    distance = min(min(exchange.stage.distances_from([bit])[x] for x in final) for bit in source)
    d = direction["seams"][1] - direction["seams"][0]
    n = len(direction["program"])
    # This bound is for co-knotted steps on original distinctions. At size two any
    # two-parent child's two edges can be replaced by a two-meeting original path.
    assert distance == d + 1 and n == distance + 4
    pulse = direction["pulse"]
    state = source ^ pulse
    moves = list(sorted(direction["program"], key=support_key, reverse=True))
    for event in moves:
        state ^= event
        assert exchange.stage.allowed_change(state)
    tail = []
    while eligible := exchange.eligible(state):
        event = min(eligible, key=support_key)
        assert event in exchange.events["exterior_four"]
        state ^= event
        assert exchange.stage.allowed_change(state)
        tail.append(event)
    assert state == final ^ pulse and len(moves) == len(tail) == n
    return {"old_inter_ring_co_knotted_steps": distance, "minimum_wedges": n,
            "minimum_events": 2 * n, "literal_minimizing_events": [sorted(q) for q in moves + tail]}


def fair_census(exchange, direction, *, interleave):
    """Exhaust all T4 reachable quotient states and grade every physical outcome."""
    prepared = {d["path"]: exchange.staged_program(d) for d in exchange.orientations}
    plan, pairs, quad_for, _ = prepared[direction["path"]]
    start, end = map(frozenset, direction["rings"])
    pulse = direction["pulse"]
    all_active = (1 << len(plan)) - 1
    event_index = {q: i for i, q in enumerate(plan)}
    old = tuple(sorted(pairs))
    pair_index = {pairs[v]: i for i, v in enumerate(old)}
    prereq = [sum(1 << event_index[quad_for[b]] for b in pairs[v]) for v in old]
    assert all(value.bit_count() == 2 for value in prereq)

    def signature(state):
        return (state - exchange.stage.loose,
                tuple(len(exchange.loose_at[v] & state) for v in sorted(exchange.young)))

    def representative(w, e):
        fired = [q for i, q in enumerate(plan) if w >> i & 1]
        swept = [pairs[v] for i, v in enumerate(old) if e >> i & 1]
        private_changes = frozenset(b for row in swept for b in row)
        loose_counts = Counter(exchange.child_of[b] for b in private_changes)
        extras = frozenset(min(exchange.loose_at[v]) for v, k in loose_counts.items() if k % 2)
        return xor_all([start, pulse, private_changes, extras, *fired])

    agenda = [(0, 0)]
    seen = set(agenda)
    enablings = slots = maximum = ties = terminal = 0
    for w, e in agenda:
        if len(seen) > T4_OUTCOME_LIMIT:
            raise RuntimeError("fair right-hand-side catalogue exceeded its finite limit")
        state = representative(w, e)
        assert exchange.stage.allowed_change(state) and exchange.read_arrival(state) == direction
        allowed = (exchange.eligible_interleaved(state, prepared)
                   if interleave else exchange.eligible(state))
        if not allowed:
            terminal += 1
            assert (w, e) == (all_active, all_active) and state == end ^ pulse
        expected = {(w | (1 << i), e) for i in range(len(plan)) if not w >> i & 1}
        if interleave or w == all_active:
            expected |= {(w, e | (1 << i)) for i, required in enumerate(prereq)
                         if w & required == required and not e >> i & 1}
        after = Counter()
        for event in allowed:
            if event in event_index:
                i = event_index[event]
                assert not w >> i & 1
                following = (w | (1 << i), e)
            else:
                i = pair_index[event - exchange.stage.loose]
                assert not e >> i & 1
                following = (w, e | (1 << i))
            output = state ^ event
            assert exchange.stage.allowed_change(output)
            assert signature(output) == signature(representative(*following))
            assert sum(x.bit_count() for x in following) == w.bit_count() + e.bit_count() + 1
            after[following] += 1
        assert set(after) == expected
        for following in after:
            if following not in seen:
                seen.add(following)
                agenda.append(following)
        enablings += len(allowed)
        slots += len(after)
        maximum = max(maximum, len(allowed))
        ties += any(n > 1 for n in after.values())
    assert terminal == 1
    return {"sibling_quotient_states": len(seen), "quotient_transitions": slots,
            "literal_outcomes_per_representative_summed": enablings, "max_simultaneously_enabled": maximum,
            "quotient_states_with_tied_literal_outcomes": ties, "terminal_states": terminal,
            "terminal_support": sorted(end ^ pulse), "each_path_events": 2 * len(plan)}


def rename_check(exchange, direction, witness, first_open):
    old_start, old_target = (direction["pulse"] ^ frozenset(ring) for ring in direction["rings"])
    stages = {}
    for state in (old_start, first_open):
        fixed, receipt = exchange.event_orbits(state)
        stages[state] = fixed, receipt
    for seed in (181, 271):
        rng = Random(seed)
        names = list(exchange.stage.owners)
        replacement = [13 + 3 * i for i in range(len(names))]
        rng.shuffle(replacement)
        mapping = dict(zip(names, replacement, strict=True))
        holder_order = list(range(len(exchange.stage.stars)))
        rng.shuffle(holder_order)
        renamed = Exchange(MotionStage([[mapping[d] for d in exchange.stage.stars[v]] for v in holder_order]))
        current = push(old_start, mapping)
        oriented = renamed.read_arrival(current)
        assert oriented and oriented["pulse"] == push(direction["pulse"], mapping)
        assert set(oriented["program"]) == {push(q, mapping) for q in direction["program"]}
        assert frozenset(oriented["rings"][1]) == push(direction["rings"][1], mapping)
        for state, (fixed, receipt) in stages.items():
            transported, alternative = renamed.event_orbits(push(state, mapping))
            assert all({push(q, mapping) for q in rows} == transported[key] for key, rows in fixed.items())
            assert all(alternative[key] == receipt[key] for key in
                       ("sibling_transpositions", "holder_automorphisms", "literal_stabilizer_order"))
        left = old_start
        for change in map(frozenset, witness["literal_minimizing_events"]):
            assert {push(q, mapping) for q in exchange.eligible(left)} == renamed.eligible(current)
            assert renamed.stage.allowed_change(current)
            current ^= push(change, mapping)
            left ^= change
        assert left == old_target and current == push(old_target, mapping)
    return {"seeds": [181, 271], "all_menus_transported_at_every_witness_state": True,
            "exact_fixed_event_sets_transported_before_and_after_opening": True}


def approach_long_path(exchange, direction):
    from composed_motion import PairedReader, co_knotted_pairs

    reader = PairedReader(co_knotted_pairs(exchange.stage.stars))
    holder_names = {frozenset(row): i for i, row in enumerate(reader.rule.stars)}
    path = [holder_names[frozenset(exchange.stage.stars[v])] for v in direction["path"]]
    lookup = {i: reader.sites[frozenset(path[i - 1:i + 2])] for i in range(1, len(path) - 1)}
    launch = reader.encode(lookup[i] for i in (1, 2, 5))
    ring = sum(1 << b for b in direction["rings"][0])
    goal_packet = sum(1 << b for b in direction["pulse"])
    assert not (launch & ring) and launch.bit_count() == 10
    current = launch ^ ring
    shifts = direction["seams"][0] - 4
    for _ in range(4 * shifts):
        successor = reader.next_state(current)
        assert successor is not None and (current ^ successor).bit_count() == 4
        current = successor
    assert current == goal_packet ^ ring
    # A separately invoked predecessor rule resumes from the certified terminal.
    new_ring = sum(1 << b for b in direction["rings"][1])
    current = goal_packet ^ new_ring
    for _ in range(8):
        successor = reader.next_state(current)
        assert successor is not None and (current ^ successor).bit_count() == 4
        current = successor
    release_centers = [direction["seams"][0] + i for i in (-1, 0, 3)]
    assert current == reader.encode(lookup[i] for i in release_centers) ^ new_ring
    return {"completed_translations": shifts, "ordinary_events": 4 * shifts,
            "launch_centers": [1, 2, 5],
            "arrival_centers": [direction["seams"][0] + i for i in (-3, -2, 1)],
            "exact_frozen_arrival_with_first_ring_intact": True,
            "separate_predecessor_wave_reader": True,
            "separate_release": {"ordinary_events": 8, "completed_translations": 2,
                                 "centers": release_centers, "second_ring_intact": True}}


def measurement(case, d):
    model = Exchange(load_stage(case))
    marks = load_marks(case)
    direction, = (x for x in model.orientations if list(x["path"]) == marks["background"])
    assert direction["seams"] == tuple(marks["seams"])
    assert tuple(map(set, direction["rings"])) == tuple(map(set, marks["ring_edges"]))
    assert direction["seams"][1] - direction["seams"][0] == d
    pulse = direction["pulse"]
    start = pulse ^ frozenset(direction["rings"][0])
    assert len(start) == 15 and not start & model.stage.loose
    fixed, group = model.event_orbits(start, record_swaps=True)
    assert not fixed["exterior_four"]
    assert fixed["loose_two"] == {bits for bits in model.loose_at.values() if len(bits) == 2}
    for event in fixed["loose_two"]:
        after = start ^ event
        assert model.stage.allowed_change(after) and after & model.stage.loose
        assert all(not after & bits or bits <= after for bits in model.loose_at.values())
    # All events are perpetually parity-allowed, so doubling each event forms a fair loop.
    old_witness = independent_trace(model, direction)
    goal = pulse ^ frozenset(direction["rings"][1])
    moves = [q for category in model.events.values() for q in category]
    assert all(start ^ q != goal and model.stage.allowed_change(start ^ q) for q in moves)
    staged = replay(model, direction, interleave=False, keep_trace=True)
    interleaved = replay(model, direction, interleave=True)
    assert not staged["pinned_prefix_stabilizers"][-1]["move_is_fixed"]
    assert all(not r["fixed_exterior_events"] for r in staged["pinned_prefix_stabilizers"])
    assert interleaved["order"].index("exterior") < max(
        i for i, tag in enumerate(interleaved["order"]) if tag == "ordinary")
    first_open = frozenset(staged["first_open_support"])
    _, open_group = model.event_orbits(first_open)
    atoms = atomic_orbits(model, direction)
    assert not atoms["target_in_span"]
    checks = rename_check(model, direction, old_witness, first_open)
    result = {
        "literal_knots": len(model.stage.stars), "literal_distinctions": len(model.stage.owners),
        "loose_counts_by_child": dict(sorted(Counter(len(model.loose_at[v]) for v in model.young).items())),
        "pulse": sorted(pulse), "ring_distance_in_source_knot_steps": d,
        "eligible_events": {key: [sorted(q) for q in events] for key, events in model.events.items()},
        "initial_state_stabilizer": group, "first_open_state_stabilizer": open_group,
        "all_fixed_single_loose_two_successors_keep_siblings_equal": len(fixed["loose_two"]),
        "minimal_trace": old_witness, "target_gated_trace": staged, "interleaved_trace": interleaved,
        "unguarded_fair_loop": {"events_per_repeat": 2 * len(moves), "target_visited": False},
        "atomic_sibling_orbits": atoms, "renaming": checks,
    }
    if case == "T4":
        result["exact_target_gated_fair_census"] = fair_census(model, direction, interleave=False)
        result["exact_interleaved_fair_census"] = fair_census(model, direction, interleave=True)
    if case == "T81":
        result["external_approach"] = approach_long_path(model, direction)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--case", choices=CASES)
    args = parser.parse_args()
    contract = HERE / "inputs.json"
    config = json.loads(contract.read_text())
    assert config["arrival_offset"] == [-3, -2, 1]
    assert tuple(case for case, _ in config["exchange"]) == CASES
    result = {"input_sha256": sha256(contract.read_bytes()).hexdigest(),
              "caps": {"holder_isomorphism_nodes": GROUP_LIMIT, "T4_sibling_states": T4_OUTCOME_LIMIT},
              "cases": {case: measurement(case, d) for case, d in config["exchange"]
                        if args.case is None or args.case == case}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.output.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(result, stream, separators=(",", ":"))
            print(file=stream)
            stream.flush()
            temporary.replace(args.output)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
