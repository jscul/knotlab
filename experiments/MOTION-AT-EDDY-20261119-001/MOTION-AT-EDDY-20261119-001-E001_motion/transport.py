"""A pulse rule on ordinary four-distinction parity responses."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random

import networkx as nx

from motion_stage import INPUTS, MotionStage, ROOT, STAGES, load_marks, load_stage


CASES = ("B", "R0", "R1", "R2", "J0", "J1", "J2", "T4", "T8", "C1",
         "B81", "J81", "T81", "R31")
TICKET = "MOTION-AT-EDDY-20261119-001"
OUTPUT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_motion") / "transport.json"


@dataclass(frozen=True)
class Arrival:
    entry: int
    response: frozenset[int]


class PulseRule:
    """Only identity within and between nearby responses enters the rule."""

    def __init__(self, responses):
        self.incident = defaultdict(list)
        for response in responses:
            for bit in response:
                self.incident[bit].append(response)

    @cache
    def contacts(self, current):
        return frozenset(
            Arrival(bit, response)
            for bit in current
            for response in self.incident[bit]
            if len(response & current) == 1
        )

    def exits(self, state):
        return frozenset(
            contact for contact in self.contacts(state.response)
            if contact.entry != state.entry
        )


def follow(state, exits):
    """The unique-exit pulse. Repeating the full state certifies periodicity."""
    history = []
    seen = {}
    while state not in seen:
        seen[state] = len(history)
        history.append(state)
        choices = exits[state]
        if len(choices) != 1:
            reason = "end" if not choices else "tie"
            return history, {"kind": reason, "exit_count": len(choices)}
        state, = choices
    return history, {"kind": "periodic", "cycle_start": seen[state],
                     "period": len(history) - seen[state]}


def wave(source, exits):
    """Exact least arrival times of passive fan-out records, with all ties kept."""
    reached = {source: 0}
    fifo = deque([source])
    while fifo:
        state = fifo.popleft()
        for child in exits[state]:
            if child not in reached:
                reached[child] = reached[state] + 1
                fifo.append(child)
    return reached


def closure(source, exits, rng=None):
    """Close an arrival set with a stack or with randomly chosen pending records."""
    active = {source}
    pending = [source]
    while pending:
        state = pending.pop() if rng is None else pending.pop(rng.randrange(len(pending)))
        new = exits[state] - active
        active.update(new)
        pending.extend(new)
    return active


def windows(history, stop):
    if stop["kind"] == "periodic":
        start, period = stop["cycle_start"], stop["period"]
        history = history + [history[start + offset % period] for offset in range(2)]
    return zip(history, history[1:], history[2:])


def landmark_observer(distances, markers):
    @cache
    def pairs_on(responses):
        initial, middle, end = (distances[response] for response in responses)
        closer = [a for a in markers if initial[a] > middle[a] > end[a]]
        farther = [a for a in markers if initial[a] < middle[a] < end[a]]
        return {tuple(sorted((a, b))) for a in closer for b in farther}

    return pairs_on


def landmark_shifts(history, stop, distances, pairs, frozen_pairs, pairs_on):
    translated = set()
    registered = set()
    checks = 0
    witness = None
    first_window_passes = 0
    for step, states in enumerate(windows(history, stop)):
        checks += 1
        moved = pairs_on(tuple(s.response for s in states))
        translated.update(moved)
        if step == 0:
            first_window_passes = len(moved)
        registered.update(frozen_pairs & moved)
        if moved and witness is None:
            a, b = min(moved)
            da = tuple(distances[s.response][a] for s in states)
            db = tuple(distances[s.response][b] for s in states)
            witness = {"update": step, "landmarks": (a, b), "readings": (da, db)}
    return {
        "windows": checks,
        "landmark_pairs_with_two_advances_by_separation": dict(Counter(
            pairs[pair] for pair in translated
        )),
        "landmark_pairs_with_two_immediate_advances": first_window_passes,
        "registered_pairs_with_two_advances": sorted(registered),
        "first_witness": witness,
    }


def response_regions(responses, marks):
    """The evaluator may use source roles. Routing takes none of these."""
    by_bit = {bit: "path" for bit in marks["anchors"]}
    for copy, row in enumerate(marks["ring_edges"], 1):
        by_bit.update({bit: f"ring{copy}" for bit in row})
    if marks.get("cut_appendage"):
        by_bit.update({bit: "cut" for bit in marks["source_shared"] - by_bit.keys()})
    assert by_bit.keys() == marks["source_shared"]
    regions = {}
    for response in responses:
        support = response & by_bit.keys()
        if len(support) != 2:
            regions[response] = "no_source_wedge"
        else:
            regions[response] = "+".join(sorted({by_bit[bit] for bit in support}))
    return regions


def wave_record(reached, exits, regions):
    first = {}
    for state, time in reached.items():
        role = regions[state.response]
        first[role] = min(first.get(role, time), time)
    return {"arrival_count": len(reached), "last_new_arrival_at": max(reached.values()),
            "first_update_by_region": first,
            "reachable_branch_states": sum(len(exits[state]) > 1 for state in reached)}


def holder_geometry(stage, responses, previous_internal, source_marks):
    """Keep source landmarks out of the routing and read true ordinary holder steps."""
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stage.stars)))
    graph.add_edges_from(row for row in stage.owners.values() if len(row) == 2)
    steps = dict(nx.all_pairs_shortest_path_length(graph))
    source = nx.Graph()
    source.add_nodes_from(source_marks)
    source.add_edges_from(stage.owners[bit] for bit in previous_internal)
    source_steps = dict(nx.all_pairs_shortest_path_length(source))
    assert all(source_steps[a][b] == steps[a][b] for a, b in combinations(source_marks, 2))
    centres = {}
    inferred_wedges = Counter()
    for response in responses:
        pair = previous_internal & response
        a, b = tuple(pair)
        centre, = set(stage.owners[a]) & set(stage.owners[b])
        centres[response] = centre
        inferred_wedges[centre, frozenset(pair)] += 1
        # The decoration is the marked arrival distinction within an ordinary
        # four-response. Its four holders each touch exactly two changed names.
        degree = Counter(j for bit in response for j in stage.owners[bit])
        assert len(degree) == 4 and all(count == 2 for count in degree.values())
    assert inferred_wedges == Counter(
        (j, frozenset(pair)) for j in source_marks
        for pair in combinations(previous_internal.intersection(stage.stars[j]), 2)
    )
    return centres, steps


def link_speeds(exits, centres, steps, near):
    """All directed causal links, including alternatives kept only in the fan."""
    strict = Counter()
    fan = Counter()
    for state, choices in exits.items():
        for advance in choices:
            speed = steps[centres[state.response]][centres[advance.response]]
            reach = max(min(near[b][a] for a in state.response) for b in advance.response)
            assert speed <= 1 and reach <= 2
            link = (speed, reach)
            fan[link] += 1
            if len(choices) == 1:
                strict[link] += 1

    def encode(counts):
        return [{"centre_steps": centre, "new_distinction_reach": reach, "links": count}
                for (centre, reach), count in sorted(counts.items())]

    return {"strict": encode(strict), "fan": encode(fan), "physical_toggle_size": 6,
            "four_change_events_to_replace_one_response": 2}


def transfer_counts(runs, roles):
    """A pure launch has both of its prepared responses in the same named part."""
    result = {}
    pure = {role for role in roles if "+" not in role and role != "no_source_wedge"}
    for role in sorted(pure):
        launched = [run for run in runs if run["launch_regions"] == (role, role)]
        others = pure - {role}
        fan = Counter("+".join(sorted(others.intersection(run["fan"]["first_update_by_region"])))
                      for run in launched)
        result[role] = {
            "ordered_launches": len(launched),
            "strict_reaches_another_pure_part": sum(
                bool(others.intersection(run["strict_region_visits"])) for run in launched
            ),
            "fan_other_parts_and_launch_counts": dict(fan),
        }
    return result


def recoding_check(stage, responses, rule, states, seed):
    """Recompute the responses and each transition after two independent renamings."""
    rng = Random(seed)
    names = rng.sample(range(100003, 200003), len(stage.owners))
    change = dict(zip(stage.owners, names, strict=True))

    def recode(support):
        return frozenset(change[bit] for bit in support)

    def recode_state(state):
        return Arrival(change[state.entry], recode(state.response))

    stars = [list(recode(row)) for row in stage.stars]
    for row in stars:
        rng.shuffle(row)
    rng.shuffle(stars)
    new_stage = MotionStage(stars)
    new_responses = new_stage.ordinary_quads()
    assert set(new_responses) == {recode(c) for c in responses}
    new_rule = PulseRule(new_responses)
    for state in states:
        assert new_rule.exits(recode_state(state)) == {
            recode_state(s) for s in rule.exits(state)
        }
    return len(states)


def reflected_incidence(stage, current, first, second):
    """Find a literal stabilizer of current exchanging the two proposed exits."""
    def decorated(low, high):
        graph = nx.Graph()
        bins = defaultdict(list)
        for bit, holders in stage.owners.items():
            color = (bit in current, bit in low, bit in high)
            bins[holders, color].append(bit)
        loose = defaultdict(Counter)
        shared = defaultdict(Counter)
        for (holders, mark), bits in bins.items():
            if len(holders) == 1:
                loose[holders[0]][mark] += len(bits)
            else:
                shared[holders][mark] += len(bits)
        graph.add_nodes_from((j, {"color": dict(loose[j])}) for j in range(len(stage.stars)))
        graph.add_edges_from((*holders, {"color": dict(colors)})
                             for holders, colors in shared.items())
        return graph, bins

    source, source_bits = decorated(first, second)
    target, target_bits = decorated(second, first)
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        source, target, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b)
    mapping = next(matcher.isomorphisms_iter(), None)
    if mapping is None:
        return None
    names = {}
    for (holders, color), bits in source_bits.items():
        moved = tuple(sorted(mapping[j] for j in holders))
        names.update(zip(bits, target_bits[moved, color], strict=True))
    assert set(names) == set(names.values()) == set(stage.owners)
    assert all({names[bit] for bit in row} == set(stage.stars[mapping[j]])
               for j, row in enumerate(stage.stars))
    assert {names[bit] for bit in current} == current
    assert {names[bit] for bit in first} == second
    assert {names[bit] for bit in second} == first
    return {"holders": mapping, "distinctions": names}


def initial_direction_control(case, stage, rule, responses):
    if case not in {"B", "R0"}:
        return []
    witnesses = []
    for index, current in enumerate(responses):
        contacts = sorted(rule.contacts(current), key=lambda s: tuple(sorted(s.response)))
        if len(contacts) != 2:
            continue
        first, second = (contact.response for contact in contacts)
        reflection = reflected_incidence(stage, current, first, second)
        if reflection:
            witnesses.append({"fixed_response": index,
                              "exchanged_responses": [responses.index(first), responses.index(second)],
                              **reflection})
    return witnesses


def score(case, stage, marks):
    responses = stage.ordinary_quads()
    indices = {response: index for index, response in enumerate(responses)}
    assert len(indices) == len(responses)
    rule = PulseRule(responses)
    neighbor_distances = {}
    source_shared = sorted(marks["source_shared"])
    for bit in set(source_shared).union(*responses):
        neighbor_distances[bit] = stage.distances_from([bit])

    # Independently evaluate the adjacency formula and literal parity supports.
    for response in responses:
        assert len(response) == 4 and not response & stage.loose
        assert stage.allowed_change(response)
        assert all(neighbor_distances[a][b] <= 2 for a in response for b in response)
        expected = set()
        for other in responses:
            shared = response & other
            if len(shared) == 1:
                entry, = shared
                expected.add(Arrival(entry, other))
                assert stage.allowed_change(response ^ other)
        assert rule.contacts(response) == expected

    # Names and landmarks enter only this evaluation, after the rule is built.
    live_holders = {stage.owners[bit][0] for bit in stage.loose}
    previous_internal = {bit for bit, holders in stage.owners.items()
                         if len(holders) == 2 and not live_holders.intersection(holders)}
    assert previous_internal == marks["source_shared"]
    assert all(any(stage.minimum_response(bit).minimum_size == 4
                   for bit in response & previous_internal) for response in responses)
    regions = response_regions(responses, marks)
    pairs = {(a, b): neighbor_distances[a][b] for a, b in combinations(source_shared, 2)}
    registered_pairs = {tuple(sorted(pair)) for pair in
                        (marks["path_landmarks"], *marks["ring_landmarks"]) if pair}
    assert registered_pairs <= pairs.keys()
    distances = {r: {bit: min(neighbor_distances[e][bit] for e in r)
                     for bit in source_shared} for r in responses}
    pairs_on = landmark_observer(distances, source_shared)

    source_holders = tuple(range(len(marks["source_stars"])))
    centres, holder_steps = holder_geometry(stage, responses, previous_internal, source_holders)
    centre_distances = {r: holder_steps[centres[r]] for r in responses}
    junction_pairs = {(a, b): holder_steps[a][b] for a, b in combinations(source_holders, 2)}
    path = marks["background"]
    path_ends = tuple(sorted((path[0], path[-1]))) if path else ()
    ring_pairs = [tuple(sorted((ring[1], ring[3]))) for ring in marks["rings"]]
    registered_junctions = (set([path_ends]) if path_ends else set()) | set(ring_pairs)
    pairs_on_junctions = landmark_observer(centre_distances, source_holders)

    oriented = [(r, state) for r in responses for state in rule.contacts(r)]
    oriented.sort(key=lambda item: (indices[item[0]], indices[item[1].response]))
    exits = {state: rule.exits(state) for _, state in oriented}
    speeds = link_speeds(exits, centres, holder_steps, neighbor_distances)
    no_entry_control = Counter()
    for response in responses:
        contacts = rule.contacts(response)
        if len(contacts) == 1:
            step, = contacts
            outcome = "period_two" if len(rule.contacts(step.response)) == 1 else "one_update"
        else:
            outcome = "halt"
        no_entry_control[outcome] += 1

    def encoded(state):
        return (state.entry, indices[state.response])

    def encoded_order(states):
        return sorted((encoded(state) for state in states), key=lambda pair: (pair[1], pair[0]))

    runs = []
    rng = Random(372193)
    endpoint_launches = []
    if path:
        endpoint_launches = [(path[1], path[2]), (path[-2], path[-3])]
    endpoint_traces = []
    for prior, launch in oriented:
        history, stop = follow(launch, exits)
        if stop["kind"] != "periodic":
            stop["exits"] = encoded_order(exits[history[-1]])
        readings = landmark_shifts(history, stop, distances, pairs, registered_pairs, pairs_on)
        junction_readings = landmark_shifts(history, stop, centre_distances, junction_pairs,
                                           registered_junctions, pairs_on_junctions)
        reached = wave(launch, exits)
        assert closure(launch, exits) == closure(launch, exits, rng) == reached.keys()
        home = centres[launch.response]
        for state, depth in reached.items():
            assert holder_steps[home][centres[state.response]] <= depth
        fan = wave_record(reached, exits, regions)
        runs.append({"preceding_response": indices[prior], "launch": encoded(launch),
                     "launch_regions": (regions[prior], regions[launch.response]),
                     "history": [encoded(state) for state in history],
                     "stop": stop, "landmarks": readings,
                     "junction_landmarks": junction_readings,
                     "strict_region_visits": sorted({regions[s.response] for s in history}),
                     "same_incoming_contacts_excluded_at_launch": sum(
                         contact.entry == launch.entry for contact in rule.contacts(launch.response)),
                     "fan": fan})
        start = (centres[prior], home)
        if start in endpoint_launches and regions[prior] == regions[launch.response] == "path":
            endpoint_traces.append({"launch_index": len(runs) - 1, "source_centres": start,
                                    "centre_history": [centres[s.response] for s in history],
                                    "endpoint_readings": [tuple(centre_distances[s.response][a]
                                                                for a in path_ends) for s in history],
                                    "stop": stop, "fan": fan})
    assert len(endpoint_traces) == len(endpoint_launches)
    shorter = {width: {"fully_ordinary": sum(not support & stage.loose for support in supports),
                       "using_loose_distinctions": sum(bool(support & stage.loose) for support in supports)}
               for width, supports in stage.short_circuits.items() if width < 4}
    assert responses and all(row["fully_ordinary"] == 0 for row in shorter.values())

    return {
        "junction_count": len(stage.stars), "distinction_count": len(stage.owners),
        "responses": [sorted(row) for row in responses],
        "response_regions": [regions[row] for row in responses],
        "response_centres": [centres[row] for row in responses],
        "contact_counts": dict(Counter(len(rule.contacts(row)) for row in responses)),
        "port_counts": dict(Counter(len({c.entry for c in rule.contacts(row)}) for row in responses)),
        "ordinary_quads_excluded_by_minimum_test": sum(not r & stage.loose
                                                        for r in stage.short_circuits[4]) - len(responses),
        "smaller_minimal_changes": shorter,
        "source_wedge_count": len(responses) - list(regions.values()).count("no_source_wedge"),
        "launch_count": len(oriented), "distinct_arrivals": len(exits),
        "queue_order_comparisons": 2 * len(oriented),
        "exit_counts": dict(Counter(map(len, exits.values()))),
        "strict_outcomes": dict(Counter(run["stop"]["kind"] for run in runs)),
        "periods": dict(Counter(run["stop"]["period"] for run in runs
                                if run["stop"]["kind"] == "periodic")),
        "memoryless_from_current_response": dict(no_entry_control),
        "memoryless_reflections": initial_direction_control(case, stage, rule, responses),
        "registered_landmark_pairs": sorted(registered_pairs),
        "landmark_pairs_by_separation": dict(Counter(pairs.values())),
        "landmark_shifts_in_some_window": sum(run["landmarks"]["first_witness"] is not None
                                              for run in runs),
        "landmark_shifts_on_registered_pairs": sum(bool(run["landmarks"]["registered_pairs_with_two_advances"])
                                                    for run in runs),
        "registered_junction_landmarks": sorted(registered_junctions),
        "junction_landmark_pairs_by_separation": dict(Counter(junction_pairs.values())),
        "junction_landmark_shifts_in_some_window": sum(run["junction_landmarks"]["first_witness"] is not None
                                                       for run in runs),
        "junction_landmark_shifts_on_registered_pairs": sum(
            bool(run["junction_landmarks"]["registered_pairs_with_two_advances"]) for run in runs),
        "speed_and_reach": speeds,
        "path_endpoint_launches": endpoint_traces,
        "pure_part_transfer": transfer_counts(runs, set(regions.values())),
        "recoded_arrivals_checked": sum(recoding_check(stage, responses, rule, exits, seed)
                                       for seed in (11329, 77981, 362297)),
        "launches": runs,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = {"stage_input_sha256": sha256(STAGES.read_bytes()).hexdigest(),
              "extra_input_sha256": sha256(INPUTS.read_bytes()).hexdigest(),
              "age": 1, "ordinary_shortest_responses": True, "intersection_size": 1,
              "renaming_seeds": [11329, 77981, 362297], "cases": {}}
    for case in CASES:
        result["cases"][case] = row = score(case, load_stage(case), load_marks(case))
        print(case, row["launch_count"], row["strict_outcomes"], row["periods"], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    tmp.replace(args.output)


if __name__ == "__main__":
    main()
