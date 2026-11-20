"""Candidate B: one anonymous ordinary minimum-four update per event."""
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from motion_stage import MotionStage, load_marks, load_stage, support_neighbors


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
PHASES = ((0, 1, 4), (0, 1, 2, 4), (0, 1, 2, 4, 5), (0, 1, 2, 5))
TOGGLES = (2, 5, 4, 0)
RADIUS = 6
NARROW = ("B", "R0", "R1", "R2", "J0", "J1", "J2", "T4", "T8", "C1")
LONG = ("R31", "B81", "J81", "T81")


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def mask(names):
    return sum(1 << x for x in names)


def step_ball(graph, center, radius):
    distance = {center: 0}
    pending = [center]
    for u in pending:
        if distance[u] == radius:
            continue
        for v in graph[u]:
            if v not in distance:
                distance[v] = distance[u] + 1
                pending.append(v)
    return set(pending)


def rooted_orientations(graph, center, radius):
    ball = step_ball(graph, center, radius)
    neighbors = {u: tuple(v for v in graph[u] if v in ball) for u in ball}
    if any(len(row) > 2 for row in neighbors.values()):
        return ball, (), "branch"
    if sum(map(len, neighbors.values())) != 2*(len(ball)-1):
        return ball, (), "cycle"
    points = {0: center}
    for sign, start in zip((1,-1), neighbors[center]):
        previous, current, offset = center, start, sign
        while True:
            points[offset] = current
            onward = [v for v in neighbors[current] if v != previous]
            if not onward:
                break
            previous, current, offset = current, onward[0], offset + sign
    assert len(points) == len(ball)
    return ball, (points, {-k:v for k,v in points.items()}), None


class PathGuard:
    def __init__(self, graph, radius=RADIUS):
        self.candidates = []
        self.rejected = Counter()
        self.root_failure = []
        for root in range(len(graph)):
            ball, embeddings, failure = rooted_orientations(graph, root, radius)
            if failure:
                self.rejected[failure] += 1
            self.root_failure.append(failure)
            mark = mask(ball)
            allowed = set()
            for points in embeddings:
                for phase, target in zip(PHASES, TOGGLES, strict=True):
                    required = [u-target for u in phase]
                    if all(u in points for u in required):
                        allowed.add(mask(points[u] for u in required))
            self.candidates.append((mark, allowed))

    def fire(self, occupied, inconsistent=0):
        return tuple(root for root,(window, accepted) in enumerate(self.candidates)
                     if not window & inconsistent and (occupied & window) in accepted)


class Board:
    def __init__(self, stage):
        self.stage = stage
        self.responses = stage.ordinary_quads(pinned_loose=True)
        assert self.responses == stage.ordinary_quads()
        self.supports = tuple(mask(response) for response in self.responses)
        self.places = [set(holder for e in support for holder in stage.owners[e]) for support in self.responses]
        live = {stage.owners[e][0] for e in stage.loose}
        private = []
        for i,response in enumerate(self.responses):
            assert len(self.places[i]) == 4 and stage.allowed_change(response)
            corner, = self.places[i] & live
            names = sorted(e for e in response if corner in stage.owners[e])
            assert len(names) == 2
            other = set(response)-set(names)
            assert all(corner not in stage.owners[e] for e in other)
            private.append(mask(names))
        self.private = tuple(private)
        occurrences = Counter(e for support in self.responses for e in support)
        assert all(occurrences[e] == 1 for part in self.private for e in bits(part))
        assert all(len(a & b) <= 1 for a,b in combinations(self.responses,2))
        self.graph = support_neighbors(self.responses)
        self.guard = PathGuard(self.graph)

    def decode(self, state):
        observed, inconsistent = 0,0
        for q, pair in enumerate(self.private):
            value = state & pair
            if value == pair:
                observed |= 1 << q
            elif value:
                inconsistent |= 1 << q
        return observed, inconsistent

    def encode(self, occupied):
        state = 0
        for q in bits(occupied):
            state ^= self.supports[q]
        assert self.decode(state) == (occupied, 0)
        return state

    def actions(self, state):
        return self.guard.fire(*self.decode(state))

    def motion_axis(self, vertices, closed=False):
        centers = range(len(vertices)) if closed else range(1,len(vertices)-1)
        n = len(vertices)
        axis = []
        for i in centers:
            triple = {vertices[(i-1)%n], vertices[i], vertices[(i+1)%n]}
            slot, = (q for q,row in enumerate(self.places) if triple <= row)
            axis.append(slot)
        assert len(set(axis)) == len(axis)
        assert all(b in self.graph[a] for a,b in zip(axis,axis[1:]))
        assert not closed or axis[0] in self.graph[axis[-1]]
        return axis


def placed(axis, first, phase=PHASES[0], backward=False, circular=False):
    positions = [first + (-x if backward else x) for x in phase]
    if circular:
        positions = [p % len(axis) for p in positions]
    if min(positions) < 0 or max(positions) >= len(axis):
        return None
    return mask(axis[p] for p in positions)


def holder_steps(stage, holder):
    distances = {holder: 0}
    queue = [holder]
    for u in queue:
        for v in stage.bundles[u]:
            if v != stage.outside and v not in distances:
                distances[v] = distances[u]+1
                queue.append(v)
    return distances


def journey(board, axis, start, maximum, landmarks=(), holders=(), circular=False, backward=False):
    occupied = placed(axis, start, backward=backward, circular=circular)
    assert occupied is not None
    original = board.encode(occupied)
    state = original
    references = [board.stage.distances_from([bit]) for bit in landmarks]
    holder_references = [holder_steps(board.stage, holder) for holder in holders]
    completed = []
    ticks = []
    intermediate = []
    finish = "cap"
    refusal = None

    def position(event):
        support = list(bits(state))
        touched = {v for e in support for v in board.stage.owners[e]}
        return {"event": event, "support": support,
                "landmark_distinction_steps": [min(metric[e] for e in support) for metric in references],
                "landmark_holder_steps": [min(metric[v] for v in touched) for metric in holder_references]}

    for event in range(maximum+1):
        macro, phase = divmod(event, 4)
        origin = start + (-macro if backward else macro)
        expected = placed(axis,origin,PHASES[phase],backward=backward,circular=circular)
        if occupied != expected:
            finish = "phase_shape_break"
            break
        if phase == 0:
            completed.append(position(event))
        intended = origin + (-TOGGLES[phase] if backward else TOGGLES[phase])
        if circular:
            intended %= len(axis)
        available = board.actions(state)
        if len(available) != 1:
            finish = "refused" if not available else "choice"
            if finish == "refused":
                refusal = "boundary" if not 0 <= intended < len(axis) else board.guard.root_failure[axis[intended]] or "window_match"
            break
        if event == maximum:
            break
        q, = available
        assert 0 <= intended < len(axis) and q == axis[intended]
        state ^= board.supports[q]
        occupied ^= 1 << q
        assert board.decode(state) == (occupied,0) and board.stage.allowed_change(bits(state))
        ticks.append(q)
        intermediate.append({"event": event+1, "changed_distinctions": list(bits(board.supports[q])),
                             "resulting_support": list(bits(state))})
        if circular and state == original:
            finish = "returns_to_initial_state"
            completed.append(position(event+1))
            assert (event+1) % 4 == 0 and len({tuple(p["support"]) for p in completed[:-1]}) == (event+1)//4
            break
    return {"events_executed": len(ticks), "actual_toggles": ticks, "stop": finish,
            "refusal_reason": refusal, "holder_landmarks": list(holders), "distinction_landmarks": list(landmarks),
            "atomic_states": intermediate,
            "complete_motif_locations": completed, "last_actions": list(board.actions(state)),
            "last_occupancy": list(bits(occupied))}


def finite_schedule(guard, initial, cap):
    history = {initial: None}
    queue = [initial]
    terminals = []
    branches = 0
    for state in queue:
        choices = guard.fire(state)
        if not choices:
            terminals.append(state)
        branches += int(len(choices) > 1)
        for q in choices:
            next_state = state ^ (1 << q)
            if next_state not in history:
                if len(history) == cap:
                    return {"complete": False, "states": len(history), "branch_states": branches}
                history[next_state] = state,q
                queue.append(next_state)

    def trace(state):
        route = []
        while history[state] is not None:
            state,event = history[state]
            route.append(event)
        return route[::-1]

    return {"complete": True, "states": len(history), "branch_states": branches,
            "terminal_observations": [{"occupancy": list(bits(s)), "route": trace(s)} for s in terminals]}


def reverse_word(word, length):
    image = 0
    for _ in range(length):
        image = (image << 1) | (word & 1)
        word >>= 1
    return image


def orbit(word):
    return min(word, reverse_word(word,word.bit_length()))


def local_sweep(radius, width=8, peak=5, period=8, visit_cap=1_000_000):
    """All unique-enabled reflected local rules in the bounded chiral state roster."""
    words = [x for x in range(1,1 << width,2) if x.bit_count() <= peak and x != reverse_word(x,x.bit_length())]
    nodes = set(words)
    transitions = {}
    local_width = 2*radius+1
    for word in words:
        seen = defaultdict(list)
        for q in range(-radius,word.bit_length()+radius):
            left = q-radius
            local = (word >> left if left >=0 else word << -left) & ((1<<local_width)-1)
            if local:
                seen[min(local,reverse_word(local,local_width))].append(q)
        differing = mask(seen)
        transitions[word] = []
        for action, indices in seen.items():
            if len(indices) != 1:
                continue
            q, = indices
            displacement = min(0,q)
            changed = (word << -displacement) ^ (1 << (q-displacement))
            lead = next(bits(changed))
            changed >>= lead
            if changed in nodes:
                transitions[word].append((q,changed,displacement+lead,1<<action,differing ^ (1<<action)))

    visits = 0
    best = None
    minimal_period = None

    for ceiling in range(2,period+1,2):
        def scan(start, word, position, used, on, off, route):
            nonlocal visits, best
            if visits >= visit_cap:
                return
            visits += 1
            for q, changed, offset, enabled, disabled in transitions[word]:
                if enabled & off or disabled & on:
                    continue
                next_position = position + offset
                following = route + [(word,position,q)]
                if changed == start and next_position:
                    receipt = (len(following),max(w.bit_length() for w,_,_ in following),
                               max(w.bit_count() for w,_,_ in following),-abs(next_position))
                    if best is None or receipt < best[0]:
                        best = (receipt, following, next_position, on|enabled, off|disabled)
                elif len(following) < ceiling and orbit(changed) not in used:
                    scan(start,changed,next_position,used | {orbit(changed)},on|enabled,off|disabled,following)

        for start in words:
            if start == orbit(start):
                scan(start,start,0,{orbit(start)},0,0,[])
        if best is not None:
            minimal_period = ceiling
            break
        if visits >= visit_cap:
            break
    witness = None
    if best is not None:
        _,trace,shift,on,off = best
        witness = {"period": len(trace), "steps": [{"occupied": list(bits(w)), "origin": o, "toggle": q} for w,o,q in trace],
                   "translation": shift, "required_word_classes": list(bits(on)), "forbidden_word_classes": list(bits(off))}
    return {"radius": radius, "span_bound": width, "peak_occupied_bound": peak, "period_bound": period,
            "completed_visit_budget": visits < visit_cap, "visits": visits, "chiral_states": len(words),
            "first_completed_period_with_witness": minimal_period, "witness": witness}


def masks_control():
    road = [tuple(v for v in (u-1,u+1) if 0 <= v < 31) for u in range(31)]
    guard = PathGuard(road)
    pattern = mask(9+x for x in PHASES[0])
    for j,delta in enumerate(TOGGLES):
        assert guard.fire(pattern) == (9+delta,)
        pattern ^= 1 << (9+delta)
        assert pattern == mask(9+x for x in (PHASES[j+1] if j < 3 else (1,2,5)))
    assert guard.fire(0) == ()


def same_orbit_radii():
    out = []
    for radius in range(1,7):
        width = 2*radius+1
        enabled, disabled = set(), set()
        reasons = []
        for j,(phase,root) in enumerate(zip(PHASES,TOGGLES,strict=True)):
            words = defaultdict(list)
            for q in range(min(phase)-radius,max(phase)+radius+1):
                value = mask(p-q+radius for p in phase if abs(p-q) <= radius)
                words[min(value,reverse_word(value,width))].append(q)
            key = next((value for value,where in words.items() if root in where),0)
            if not key or len(words[key]) != 1:
                reasons.append({"phase": j, "collisions": words.get(key, []), "desired_root": root})
            enabled.add(key)
            disabled.update(set(words)-{key})
        road = [tuple(v for v in (u-1,u+1) if 0 <= v < 31) for u in range(31)]
        guard = PathGuard(road,radius)
        literal = [list(guard.fire(mask(10+p for p in phase))) for phase in PHASES]
        out.append({"radius":radius, "some_word_rule_realizes_same_orbit": not reasons and not enabled & disabled,
                    "chosen_word_classes": sorted(enabled), "conflicting_classes": sorted(enabled & disabled),
                    "nonunique_roots_by_phase": reasons, "full_template_possible": literal == [[10+q] for q in TOGGLES],
                    "full_template_fires_by_phase": literal})
    return out


def overlap_family_checks(board, axis):
    source = axis[6]
    singleton = 1 << source
    adjacent = singleton | (1 << axis[7])
    model = placed(axis,5)
    assert model is not None

    def overlap(occ):
        physical = board.encode(occ)
        return [(support & physical).bit_count() for support in board.supports]

    def successors(occ, active_counts):
        return tuple(q for q,value in enumerate(overlap(occ)) if value in active_counts)

    def wave(start, budget, active_counts):
        states = {start}
        for _ in range(budget):
            states = {state ^ (1<<q) for state in states for q in successors(state,active_counts)}
        return states

    out = []
    for rule in range(32):
        counts = set(bits(rule))
        one = successors(singleton,counts)
        two = wave(singleton,2,counts)
        phase = model
        can, forced = True,True
        for offset in TOGGLES:
            q = axis[5+offset]
            choices = successors(phase,counts)
            can &= q in choices
            forced &= choices == (q,)
            phase ^= 1 << q
        assert phase == placed(axis,6)
        outputs = wave(model,4,counts)
        out.append({"enabled_overlap_counts": sorted(counts), "quiet_empty_state": not successors(0,counts),
                    "singleton_first_choices": list(one), "adjacent_pair_first_choices": list(successors(adjacent,counts)),
                    "single_can_shift_left_in_two": 1 << axis[5] in two,
                    "single_can_shift_right_in_two": 1 << axis[7] in two,
                    "single_can_return_in_two": singleton in two,
                    "pulse_canonical_phase_route_admitted": can, "pulse_canonical_phase_route_forced": forced,
                    "pulse_shift_left_in_four": placed(axis,4) in outputs,
                    "pulse_shift_right_in_four": placed(axis,6) in outputs,
                    "pulse_return_in_four": model in outputs,
                    "count_of_exact_four_event_endpoints": len(outputs),
                    "pulse_only_four_event_endpoint_is_right_shift": outputs == {placed(axis,6)}})
    return out


def closed_and_renamed_benchmark(board, axis):
    two = 1 << axis[5]
    shifted = 1 << axis[6]
    pair_moves = [[axis[5],axis[6]],[axis[6],axis[5]]]
    assert (board.encode(two) ^ board.encode(shifted)).bit_count() == 6
    assert all((board.encode(two) ^ board.encode(shifted)) != event for event in board.supports)
    # All literal closed states on the background path are in the pure response code.
    ordinary = set(board.stage.owners)-board.stage.loose
    connected = holder_steps(board.stage,0)
    assert len(connected) == len(board.stage.stars)
    assert len(ordinary)-len(connected)+1 == len(board.responses)
    minimum = None
    minimums = Counter()
    for occupancy in range(1,1 << len(axis)):
        support = occupancy >> next(bits(occupancy))
        if support == reverse_word(support,support.bit_length()):
            continue
        state = board.encode(mask(axis[i] for i in bits(occupancy)))
        record = (state.bit_count(),occupancy.bit_count())
        minimum = min(minimum,record) if minimum else record
        minimums[record[1]] += 1
    assert minimum == (10,3)

    labels = sorted(board.stage.owners)
    renamed = {e: j+100 for j,e in enumerate(reversed(labels))}
    reflex = Board(MotionStage([[renamed[e] for e in row[::-1]] for row in board.stage.stars[::-1]]))
    by_support = {support:i for i,support in enumerate(reflex.responses)}
    slots = {q: by_support[frozenset(renamed[e] for e in source)] for q,source in enumerate(board.responses)}

    checked = 0
    for occupancy in range(1 << len(axis)):
        expected = tuple(sorted(slots[q] for q in board.guard.fire(occupancy)))
        renamed_occupied = mask(slots[q] for q in bits(occupancy))
        assert reflex.actions(reflex.encode(renamed_occupied)) == expected
        checked += 1
    occupied = placed(axis,5)
    state = board.encode(occupied)
    assert board.actions(state) and not board.actions(state ^ state) and board.stage.allowed_change(bits(state))
    return {"single_response_translation_changed_bits": 6, "minimal_atomic_sequences": pair_moves,
            "intermediate_states": [[],list(bits(board.encode(two|shifted)))],
            "closed_state_count": 1 << len(axis), "minimum_chiral_physical_support": minimum[0],
            "minimum_initial_occupied_slots": minimum[1], "label_covariant_closed_states": checked,
            "chiral_states_by_active_count": dict(minimums),
            "reference_forgotten_control": {"allowed_shift_maps_nonquiescent_seed_to_quiescence": True,
                                             "original_enabled": list(board.actions(state)), "shifted_enabled": []}}


def exhaustive_closed_control():
    stars = [[] for _ in range(10)]
    for e,(u,v) in enumerate([(i,i+1) for i in range(5)] + [(i,6+i) for i in range(4)] + [(i+2,6+i) for i in range(4)]):
        stars[u].append(e)
        stars[v].append(e)
    for i in range(4):
        stars[6+i].extend((13+2*i,14+2*i))
    board = Board(MotionStage(stars))
    ordinary = sorted(set(board.stage.owners)-board.stage.loose)
    states = {mask(e for j,e in enumerate(ordinary) if k>>j&1) for k in range(1 << len(ordinary))}
    allowed = {p for p in states if board.stage.allowed_change(bits(p))}
    generated = {board.encode(j) for j in range(1 << len(board.responses))}
    assert allowed == generated
    return {"subset_trials": len(states), "literal_allowed_states": len(allowed), "quad_count": len(board.responses)}


def score_case(tag):
    board = Board(load_stage(tag))
    role = load_marks(tag)
    background = role["background"]
    measurements = []
    if background:
        axis = board.motion_axis(background)
        holder_landmarks = (background[0],background[-2])
        center = 8 if len(background) > 30 else 2
        positions = [("background_forward",center,False),("background_reflected",len(axis)-center-1,True)]
        for seam in role["seams"]:
            j = background.index(seam)-1
            if j-14 >= 0:
                positions.append((f"approach_seam_{seam}",j-14,False))
            if j+10 < len(axis)-5:
                positions.append((f"depart_seam_{seam}",j+10,False))
        for label,index,reverse in positions:
            max_events = 4*(len(axis)+1) if tag in ("B","B81") else 84 if len(axis)>30 else 24
            readings = journey(board, axis, index, max_events,
                               role["path_landmarks"], holder_landmarks, backward=reverse)
            measurements.append({"fixture": label, "initial_axis_position": index, **readings})
        if tag == "B81":
            collisions = []
            for separation in (8,10,12,14,16):
                left = placed(axis,20)
                right = placed(axis,20+separation+4,backward=True)
                assert not left & right
                recorded = finite_schedule(board.guard,left|right,20_000)
                for stop in recorded.get("terminal_observations", []):
                    endpoint = left | right
                    for q in stop["route"]:
                        assert q in board.guard.fire(endpoint)
                        endpoint ^= 1 << q
                    assert endpoint == mask(stop["occupancy"]) and not board.guard.fire(endpoint)
                    stop["literal_terminal_support"] = list(bits(board.encode(endpoint)))
                collisions.append({"separation": separation, **recorded})
            measurements.append({"fixture": "opposing_pulses", "censuses": collisions})
            well_separated = placed(axis,20) | placed(axis,64,backward=True)
            p,q = board.guard.fire(well_separated)
            assert (1<<p) ^ (1<<q) == (1<<q) ^ (1<<p)
            assert q in board.guard.fire(well_separated ^ (1<<p))
            assert p in board.guard.fire(well_separated ^ (1<<q))
            measurements.append({"fixture": "well_separated_first_fires", "both_orders": [[p,q],[q,p]],
                                 "same_two_event_state": True})
    for i, ring in enumerate(role["rings"]):
        axis = board.motion_axis(ring,closed=True)
        if len(ring) == 31:
            for reverse in (False,True):
                readings = journey(board,axis,0,124,role["ring_landmarks"][i],(ring[1],ring[3]),
                                   circular=True,backward=reverse)
                measurements.append({"fixture": f"ring_{i}_full_return", "reflected": reverse, **readings})
        else:
            ring_mask = mask(axis)
            on_ring = 0
            all_roots = 0
            for local in range(1 << len(axis)):
                occ = mask(axis[j] for j in range(len(axis)) if local>>j&1)
                available = board.guard.fire(occ)
                on_ring += any(ring_mask >> q & 1 for q in available)
                all_roots += bool(available)
            measurements.append({"fixture": f"ring_{i}_small_closed_controls", "pure_states": 1 << len(axis),
                                 "states_enabling_any_fire": all_roots, "states_enabling_ring_fire": on_ring})
    return {"response_count": len(board.responses), "guard_refusal_types": dict(board.guard.rejected), "tests": measurements}


def main():
    masks_control()
    actual = Board(load_stage("B"))
    axis = actual.motion_axis(load_marks("B")["background"])
    payload = {"source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "control": exhaustive_closed_control(), "template_radius": RADIUS,
               "phase_templates": [{"occupied": phase, "toggle": action} for phase,action in zip(PHASES,TOGGLES)],
               "background_closed_benchmarks": closed_and_renamed_benchmark(actual,axis),
               "all_overlap_count_rules": overlap_family_checks(actual,axis),
               "same_four_phase_orbit_by_radius": same_orbit_radii(),
               "radius_search": [local_sweep(r) for r in (1,2,3)],
               "cases": {tag: score_case(tag) for tag in NARROW+LONG}}
    (ARTIFACTS / "b_updates.json").write_text(json.dumps(payload,separators=(",", ":")) + "\n")
    print({r["radius"]: (r["completed_visit_budget"],r["first_completed_period_with_witness"]) for r in payload["radius_search"]})
    for tag,case in payload["cases"].items():
        print(tag,case["response_count"],[(x["fixture"],x.get("events_executed"),x.get("stop")) for x in case["tests"]])


if __name__ == "__main__":
    main()
