"""Literal parity changes and directed motion on the two archived bare rings."""
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "motion.json"
MOTION = "MOTION-AT-EDDY-20261119-001"
LAW = "MOTION-LAW-20261119-001"
MOTION_DIR = ROOT / "experiments" / MOTION / (MOTION + "-E001_motion")
LAW_DIR = ROOT / "experiments" / LAW / (LAW + "-E001_rules")
sys.path[:0] = [str(MOTION_DIR), str(LAW_DIR)]
import motion_stage


def mask(names):
    return sum(1 << bit for bit in names)


def bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def basis(words):
    pivots = {}
    for word in words:
        while word and (top := word.bit_length() - 1) in pivots:
            word ^= pivots[top]
        if word:
            pivots[word.bit_length() - 1] = word
    return tuple(pivots[k] for k in sorted(pivots))


def all_words(independent):
    reached = [0]
    for word in independent:
        reached += [x ^ word for x in reached]
    return set(reached)


def paths(graph, start, omit=None):
    """Distance and the complete tied list of shortest predecessors."""
    distance, previous, queue = {start: 0}, defaultdict(list), [start]
    for u in queue:
        for v, mark in graph[u]:
            if mark == omit:
                continue
            if v not in distance:
                distance[v] = distance[u] + 1
                queue.append(v)
            if distance[v] == distance[u] + 1:
                previous[v].append((u, mark))
    return distance, previous


def path_masks(previous, at, start):
    if at == start:
        yield 0
    else:
        for u, mark in previous[at]:
            for before in path_masks(previous, u, start):
                yield before | 1 << mark


def ring_generators(stage, pinned):
    names = [e for e in stage.owners if not pinned or e not in stage.loose]
    graph, forest = defaultdict(list), defaultdict(list)
    fundamental = []
    for e in names:
        u, v = stage.ends[e]
        distance, previous = paths(forest, u)
        if v in distance:
            path, = path_masks(previous, v, u)
            fundamental.append(path | 1 << e)
        else:
            forest[u].append((v, e))
            forest[v].append((u, e))
        graph[u].append((v, e))
        graph[v].append((u, e))
    shortest = set()
    sizes = Counter()
    for e, (u, v) in stage.ends.items():
        old = stage.minimum_response(e, pinned_loose=pinned)
        if e not in names:
            assert old.minimum_size is None
            continue
        distance, previous = paths(graph, u, omit=e)
        tied = {p | 1 << e for p in path_masks(previous, v, u)} if v in distance else set()
        length = distance[v] + 1 if v in distance else None
        assert (old.minimum_size, old.count) == (length, len(tied))
        if old.listed_all_supports:
            assert tied == {mask(ch) for ch in old.supports}
        shortest.update(tied)
        sizes[str(length)] += 1
    assert len(basis(fundamental)) == len(fundamental)
    return names, fundamental, shortest, dict(sizes)


def is_circuit(stage, word):
    if not word:
        return False
    degrees = Counter()
    neighbors = defaultdict(set)
    for e in bits(word):
        u, v = stage.ends[e]
        degrees.update((u, v))
        if degrees[u] > 2 or degrees[v] > 2:
            return False
        neighbors[u].add(v)
        neighbors[v].add(u)
    if any(n != 2 for n in degrees.values()):
        return False
    todo = [next(iter(degrees))]
    seen = set(todo)
    for u in todo:
        for v in neighbors[u] - seen:
            seen.add(v)
            todo.append(v)
    return len(seen) == len(degrees)


@cache
def knot_check(width, allowed):
    fields = [f"a{i}" for i in range(width)]
    cnf = ";".join(" ".join(("~" if word >> i & 1 else "") + name for i, name in enumerate(fields))
                   for word in range(1 << width) if word not in allowed)
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", *fields[:-1], "--contact", fields[-1], "--json"]
    report = json.loads(subprocess.check_output(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}))
    return {k: report[k] for k in ("binding", "loss_on_erasure", "coexistence", "is_knot")}


def local_relations(stage, generators):
    kinds = Counter()
    for row in stage.stars:
        projections = basis(sum(((w >> e) & 1) << j for j, e in enumerate(row)) for w in generators)
        kinds[len(row), tuple(sorted(all_words(projections)))] += 1
    return [dict(arity=n, words=list(allowed), occurrences=count, **knot_check(n, allowed))
            for (n, allowed), count in sorted(kinds.items())]


def ring_trial(stage, length, age, pinned, rim):
    names, fundamental, shortest, marked_lengths = ring_generators(stage, pinned)
    stars = list(map(mask, stage.stars))
    constraints = [s & mask(names) for s in stars]
    full_rank = len(names) - len(basis(constraints))
    assert full_rank == len(fundamental)
    assert all(is_circuit(stage, w) and stage.allowed_change(bits(w)) for w in fundamental)
    assert all(is_circuit(stage, w) and stage.allowed_change(bits(w)) for w in shortest)
    ordinary = {mask(q) for q in stage.ordinary_quads(pinned_loose=pinned)}
    short_rank, ordinary_rank = len(basis(shortest)), len(basis(ordinary))
    ring_hits = len(basis([*shortest, rim])) == short_rank
    assert stage.allowed_change(bits(rim))
    # A nonzero difference is tested on several assignment-basis vectors, including an illegal one.
    words = {0, rim, 1 << min(stage.owners)}
    reads = [1 << i for i in stage.owners] + stars
    tested, odd = 0, 0
    for change in shortest:
        for read in reads:
            anti = (read & change).bit_count() % 2
            odd += anti
            for word in words:
                left = ((word ^ change) & read).bit_count() % 2
                right = (word & read).bit_count() % 2
                assert (left ^ right) == anti
            tested += 1
    row = dict(knots=len(stage.stars), distinctions=len(stage.owners), loose=len(stage.loose),
               ring=length, age=age, loose_pinned=pinned, marked_minimum_sizes=marked_lengths,
               allowed_change_rank=full_rank, allowed_assignments=1 << full_rank,
               shortest_generators=len(shortest), shortest_rank=short_rank,
               shortest_counts_by_size=dict(sorted(Counter(w.bit_count() for w in shortest).items())),
               shortest_fixed_weighting_dimension=1 << (full_rank - short_rank),
               ordinary_four_count=len(ordinary), ordinary_four_rank=ordinary_rank,
               ordinary_fixed_weighting_dimension=1 << (full_rank - ordinary_rank),
               all_circuit_rank=full_rank, all_circuit_fixed_weighting_dimension=1,
               original_ring_in_shortest_span=ring_hits, original_ring=list(bits(rim)),
               odd_original_overlap_in_shortest=sum((w & rim).bit_count() % 2 for w in shortest),
               mark_or_knot_read_change_pairs=tested, odd_exchange_pairs=odd,
               assignment_basis_checks=tested * len(words), projected_knots=local_relations(stage, fundamental))
    if full_rank <= 16:
        states = all_words(fundamental)
        assert all(all((w & s).bit_count() % 2 == 0 for s in stars) for w in states)
        exhaustive_odd = sum(sum((t & read).bit_count() % 2 for t in states) for read in reads)
        predicted_odd = (len(states) // 2) * sum(any((g & r).bit_count() % 2 for g in fundamental)
                                                   for r in reads)
        assert exhaustive_odd == predicted_odd
        circuits = [w for w in states if is_circuit(stage, w)]
        assert len(basis(circuits)) == full_rank and shortest <= set(circuits)
        remaining, sizes = states.copy(), []
        moves = all_words(basis(shortest))
        while remaining:
            x = min(remaining)
            orbit = {x ^ t for t in moves}
            assert orbit <= remaining
            sizes.append(len(orbit))
            remaining -= orbit
        row.update(enumerated_allowed_states=len(states), all_circuit_count=len(circuits),
                   orbit_sizes=sorted(sizes), all_translation_read_pairs=len(states) * len(reads),
                   odd_pairs_over_all_translations=exhaustive_odd)
    else:
        row.update(all_translation_read_pairs=(1 << full_rank) * len(reads),
                   odd_pairs_over_all_translations=(1 << (full_rank - 1)) *
                   sum(any((g & r).bit_count() % 2 for g in fundamental) for r in reads))
    if age == 1:
        assert not ring_hits and all((w & rim).bit_count() % 2 == 0 for w in shortest)
        assert short_rank + 1 == full_rank
    else:
        assert ring_hits and short_rank == full_rank
    return row


def rings():
    rows = []
    for case, length in (("R0", 5), ("R31", 31)):
        record = motion_stage.load_case_record(case)
        rim = mask(record["input"]["roles"]["ring_edges"][0])
        for age in (0, 1):
            stage = motion_stage.MotionStage(record["stages"][str(age)]["stars"])
            for pinned in (False, True):
                rows.append(ring_trial(stage, length, age, pinned, rim))
    return rows



def directed_guard():
    import b_updates
    stage = motion_stage.load_stage("R31", 1)
    board = b_updates.Board(stage)
    axis = board.motion_axis(motion_stage.load_marks("R31")["rings"][0], closed=True)
    orbits, witness = [], None
    for reflected in (False, True):
        initial = board.encode(b_updates.placed(axis, 0, backward=reflected, circular=True))
        state, successors = initial, {}
        while state not in successors:
            assert stage.allowed_change(bits(state))
            event, = board.actions(state)
            after = state ^ board.supports[event]
            successors[state] = after
            if witness is None:
                assert event not in board.actions(after)
                witness = dict(enabled_state=list(bits(state)), image_and_disabled_state=list(bits(after)),
                               named_event=list(bits(board.supports[event])),
                               enabled_events_at_image=list(board.actions(after)))
            assert len(successors) <= 124
            state = after
        assert state == initial and set(successors) == set(successors.values()) and len(successors) == 124
        orbits.append(len(successors))
    return dict(permitted_fixed_event="injective on the states enabling that event by XOR cancellation",
                idling_when_disabled_is_injective=False, idling_collision=witness,
                unique_successor_is_permutation_on_each_registered_orbit=orbits)


def allowed_words(stars, law):
    size = max(max(row) for row in stars) + 1
    star_masks = list(map(mask, stars))
    if law == "parity":
        return {x for x in range(1 << size) if all((x & s).bit_count() % 2 == 0 for s in star_masks)}
    return {x for x in range(1 << size) if all(0 < (x & s).bit_count() < s.bit_count() for s in star_masks)}


def distribution_after(allowed, update):
    targets = {x: mask(update(frozenset(bits(x)))) for x in allowed}
    return targets, dict(allowed=len(allowed), distinct_images=len(set(targets.values())),
                         allowed_images=sum(y in allowed for y in targets.values()),
                         changed=sum(x != y for x, y in targets.items()),
                         inverse_on_allowed=all(targets.get(y) == x for x, y in targets.items()),
                         whole_uniform_fixed=set(targets.values()) == allowed)


def ties(allowed, a, b, width):
    am, bm = mask(a), mask(b)
    hidden = ((1 << width) - 1) ^ (am | bm)
    rows = defaultdict(set)
    for x in allowed:
        rows[x & hidden].add((x & am, x & bm))
    products = sum(len(r) == len({x for x, _ in r}) * len({y for _, y in r}) for r in rows.values())
    supported = sorted(x | y for x in all_words([1 << j for j in a]) if x
                       for y in all_words([1 << j for j in b]) if y)
    reads = [r for r in supported if all((x & r).bit_count() % 2 == 0 for x in allowed)]
    shifts = [t for t in supported if all(x ^ t in allowed for x in allowed)]
    pairs = [(r, t) for r in reads for t in shifts
             if (r & t & am).bit_count() % 2 and (r & t & bm).bit_count() % 2]
    return dict(readers=[a, b], unread=list(bits(hidden)), unread_assignments=len(rows),
                product_support_conditional_cells=products, fixed_anticommuting_pairs=len(pairs),
                witness=None if not pairs else dict(joint_read=list(bits(pairs[0][0])),
                                                    joint_change=list(bits(pairs[0][1]))))


def permutations():
    import permutation_controls as old
    small = [[0, 1, 2], [0, 3, 4, 5]]
    central = [[0, 1, 2, 3], [0, 4, 5, 6, 7], [1, 8, 9, 10, 11]]
    result = {}
    for law in ("parity", "nae"):
        allowed = allowed_words(small, law)
        pools = old.local_pools(small)
        targets, swap = distribution_after(allowed, lambda x: old.apply(x, {4}, pools))
        assert swap["inverse_on_allowed"] and swap["whole_uniform_fixed"]
        separated = ties(allowed, [1, 2], [3, 4, 5], 6)
        split = ties(allowed, [1], [0, 2], 6)
        assert separated == ties(set(targets.values()), [1, 2], [3, 4, 5], 6)
        assert split == ties(set(targets.values()), [1], [0, 2], 6)
        assert separated["fixed_anticommuting_pairs"] == 0
        assert separated["product_support_conditional_cells"] == separated["unread_assignments"]
        if law == "parity":
            assert split["fixed_anticommuting_pairs"] > 0
        states = allowed_words(central, law)
        guarded = old.guarded_pools(central, 5)
        outgoing, toggle = distribution_after(states, lambda x: old.guarded_change(x, guarded))
        bad = next(((x, y) for x, y in sorted(outgoing.items()) if y not in states), None)
        toggle["outside_example"] = None if bad is None else [list(bits(x)) for x in bad]
        assert (toggle["inverse_on_allowed"], bad is None) == (law == "parity", law == "parity")
        for star_list, physical, report in ((small, allowed, swap), (central, states, toggle)):
            report["old_knot_checks"] = []
            for names in star_list:
                projected = tuple(sorted({sum(((x >> e) & 1) << j for j, e in enumerate(names))
                                          for x in physical}))
                checked = knot_check(len(names), projected)
                assert checked["is_knot"]
                report["old_knot_checks"].append(dict(places=names, allowed_words=len(projected), **checked))
        result[law] = dict(two_loose_swap=swap, shared_value_guarded_toggle=toggle,
                           split_reader_test=split, separate_reader_test=separated)
    return dict(swap_source=small, guarded_toggle_source=central, laws=result)


def terminal_graph(model, initial):
    queue, depth, incoming = [initial], {initial: 0}, Counter()
    stopped, translations = [], set()
    for state in queue:
        assert model.stage.allowed_change(state)
        menu = model.enabled(state)
        if not menu:
            stopped.append(state)
        for event in menu:
            after = state ^ event
            translations.add(event)
            incoming[after] += 1
            if after not in depth:
                depth[after] = depth[state] + 1
                queue.append(after)
            assert depth[after] == depth[state] + 1
        assert len(queue) <= 20000
    for event in translations:
        assert model.stage.allowed_change(event)
    summary = dict(states=len(depth), transitions=sum(incoming.values()), distinct_named_events=len(translations),
                   states_with_multiple_predecessors=sum(n > 1 for n in incoming.values()),
                   terminal_depths=[depth[s] for s in stopped], terminals=[sorted(s) for s in stopped])
    return stopped, summary


def switch_at_four():
    import sources
    import uniform_exchange as old
    spec, = (r for r in sources.cases() if r["id"] == "T4")
    model, donor, receiver, _ = old.named_fixture(spec)
    results = []
    for first, second in ((donor, receiver), (receiver, donor)):
        pulse = first.pulse
        initial, desired = old.origin_and_goal(first, second)
        off, empty = terminal_graph(model, pulse)
        on, loaded = terminal_graph(model, initial)
        frozen, already = terminal_graph(model, desired)
        assert off == [pulse] and on == [desired] and frozen == [desired]
        d, r = frozenset(first.ring), frozenset(second.ring)
        assert (initial ^ d) == (desired ^ r) == pulse and (initial ^ desired) == (d ^ r)
        # An additional coherent encoding writes the free end of a split three-place rule on a ring.
        # The archived endpoint map itself only supplies the two images of the basis words.
        encoded = [(a, b, pulse ^ (r if a ^ b else frozenset())) for a in (0, 1) for b in (0, 1)]
        local_mark = min(r)
        z_sum = sum((-1) ** (a ^ b ^ (local_mark in (word ^ pulse))) for a, b, word in encoded)
        coherent_x_sum = dephased_x_sum = 0
        for a, b, word in encoded:
            if (1 - a, b, word ^ r) in encoded:
                coherent_x_sum += 1
                dephased_x_sum += (a ^ b) == ((1 - a) ^ b)
        assert (z_sum, coherent_x_sum, dephased_x_sum) == (4, 4, 0)
        total_translation = []
        for x in (0, 1):
            for y in (0, 1):
                input_bits = pulse ^ (d if x else frozenset()) ^ (r if y else frozenset())
                out = input_bits ^ (initial ^ desired)
                assert out == pulse ^ (d if not x else frozenset()) ^ (r if not y else frozenset())
                total_translation.append(dict(input=[x, y], output=[1 - x, 1 - y]))
        results.append(dict(donor_ring=sorted(d), receiver_ring=sorted(r), returning_pulse=sorted(pulse),
                            unloaded=empty, loaded=loaded, preloaded_receiver=already,
                            every_intermediate_restored=(initial ^ desired) == (d ^ r),
                            prescribed_translation_truth_table=total_translation,
                            encoded_clean_receiver_images=[[0, 0], [0, 1]],
                            encoded_split_terms=len(encoded), encoded_reference_read=[0, 1],
                            reference_change=[0], receiver_read_mark=local_mark, receiver_change=sorted(r),
                            encoded_expectation_denominator=len(encoded),
                            coherent_joint_ZX_numerators=[z_sum, coherent_x_sum],
                            dephased_joint_ZX_numerators=[z_sum, dephased_x_sum],
                            complete_run_to_rest_injective=False))
    return dict(stage_knots=len(model.stage.stars), stage_distinctions=len(model.stage.owners), directions=results)


def phases():
    import permutation_controls as old
    stars = [[0, 1, 2], [0, 3, 4, 5]]
    pools = old.local_pools(stars)
    result = {}
    for law, flips in (("parity", [[1, 2]]), ("nae", [list(range(6)), [1, 2]])):
        allowed = allowed_words(stars, law)
        targets, _ = distribution_after(allowed, lambda x: old.apply(x, {4}, pools))
        weighted_transitions, chances = [], []
        for phase in (False, True):
            amp = {x: (-1 if phase and x & (1 << 1) else 1) if x in allowed else 0 for x in range(64)}
            denominator = 4 * len(allowed)
            for changes in flips:
                flip = mask(changes)
                masses = [sum((amp[x] + eig * amp[x ^ flip]) ** 2 for x in range(64)) for eig in (1, -1)]
                assert sum(masses) == denominator
                constant_change = all((x ^ flip) in allowed for x in allowed)
                if constant_change:
                    assert masses[0 if phase else 1] == 0
                chances.append(dict(phase_changed=phase, change=changes, constant_allowed_change=constant_change,
                                    sign_outcome_order=[1, -1], numerators=masses, denominator=denominator))
            weighted_transitions.append({(x, targets[x]): amp[x] ** 2 for x in allowed})
        assert weighted_transitions[0] == weighted_transitions[1]
        result[law] = dict(allowed_states=len(allowed), physical_transition_pairs=len(weighted_transitions[0]),
                           identical_ordinary_record_weights=True, supplied_change_read=chances)
    return dict(source=stars, phase_read=[1], laws=result)


def run():
    return {"rings": rings(), "directed_guard": directed_guard(), "permutations": permutations(),
            "restored_switch": switch_at_four(), "phase_test": phases()}


if __name__ == "__main__":
    if len(sys.argv) == 1:
        results = run()
    else:
        results = json.loads(OUT.read_text()) if OUT.is_file() else {}
        for part in sys.argv[1:]:
            if part == "rings":
                results["rings"] = rings()
            elif part == "maps":
                results.update(directed_guard=directed_guard(), permutations=permutations(),
                               restored_switch=switch_at_four())
            elif part == "phase":
                results["phase_test"] = phases()
            else:
                raise ValueError(part)
    OUT.write_text(json.dumps(results, indent=2) + "\n")
