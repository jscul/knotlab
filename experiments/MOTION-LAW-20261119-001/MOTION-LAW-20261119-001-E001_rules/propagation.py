"""Reach, clockless scattering, and synchronous controls on a literal response chain."""

from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from functools import cache
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = "MOTION-AT-EDDY-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / PREDECESSOR / f"{PREDECESSOR}-E001_motion"))
from b_updates import Board, bits, mask
from motion_stage import load_stage


WORDS = {1: (0, 1, 3), 2: (0, 1, 2, 4)}
MEETING_WORD = tuple(range(7))
CLEARANCE = 3
MEETING_GAP = 5
READ_RADIUS = 14
MAX_STATES = 20_000
RADII = (1, 2, 4, 8)


class PhysicalChain:
    def __init__(self):
        self.board = Board(load_stage("B81"))
        graph = self.board.graph
        end, _ = [i for i, row in enumerate(graph) if len(row) == 1]
        axis = [end]
        previous = None
        while len(axis) < len(graph):
            following, = set(graph[axis[-1]]) - {previous}
            previous = axis[-1]
            axis.append(following)
        if len(set(axis)) != 79 or graph[axis[-1]] != (axis[-2],):
            raise ValueError("registered fixture must be the 79 ordinary responses on a path")
        self.axis = tuple(axis)
        self.length = len(axis)

    @cache
    def literal(self, positions):
        occupied = mask(self.axis[i] for i in positions)
        physical = frozenset(bits(self.board.encode(occupied)))
        if not self.board.stage.allowed_change(physical) or physical & self.board.stage.loose:
            raise AssertionError("state escaped the literal closed response code")
        return physical


def components(occupied):
    groups = []
    for at in sorted(occupied):
        if not groups or at - groups[-1][-1] >= CLEARANCE:
            groups.append([])
        groups[-1].append(at)
    return tuple(tuple(group) for group in groups)


def normalize(group):
    return tuple(at - group[0] for at in group)


def reflected(group):
    return tuple(group[0] + group[-1] - at for at in reversed(group))


@dataclass(frozen=True)
class Packet:
    cells: tuple
    stride: int
    heading: int

    @property
    def head(self):
        return self.cells[-1] if self.heading == 1 else self.cells[0]


def decode(group):
    word = normalize(group)
    for stride, pattern in WORDS.items():
        if word == pattern:
            return Packet(group, stride, 1)
        if word == reflected(pattern):
            return Packet(group, stride, -1)
    return None


@dataclass(frozen=True)
class Event:
    kind: str
    root_twice: int
    before: tuple
    after: tuple
    stride: int = 0

    def changed(self):
        return frozenset(self.before) ^ frozenset(self.after)

    def apply(self, state):
        return state ^ self.changed()


def meeting(kind, root_twice, left, right):
    return Event(kind, root_twice, left.cells + right.cells,
                 reflected(left.cells) + reflected(right.cells))


def enabled(occupied, length, direct=False):
    groups = components(occupied)
    kinds = tuple(normalize(group) == MEETING_WORD for group in groups)
    packets = tuple(decode(group) for group in groups)
    events = []
    for i, packet in enumerate(packets):
        if packet:
            limit = length - 1 - packet.head if packet.heading == 1 else packet.head
            ahead = i + packet.heading
            if 0 <= ahead < len(groups):
                target = groups[ahead][0 if packet.heading == 1 else -1]
                gap = MEETING_GAP if kinds[ahead] else CLEARANCE
                limit = min(limit, abs(target - packet.head) - gap)
            distance = min(packet.stride, limit)
            if distance > 0:
                out = tuple(at + packet.heading * distance for at in packet.cells)
                events.append(Event("travel", 2 * packet.head, packet.cells, out, packet.stride))
        if kinds[i] and 0 < i < len(groups) - 1:
            left, right = packets[i - 1], packets[i + 1]
            a, b = groups[i][0], groups[i][-1]
            if (left and right and left.heading == 1 and right.heading == -1
                    and a - left.head == right.head - b == MEETING_GAP):
                events.append(meeting("marked_scatter", a + b, left, right))
    if direct:
        for left, right in zip(packets, packets[1:]):
            if (left and right and left.heading == 1 and right.heading == -1
                    and right.head - left.head == CLEARANCE):
                events.append(meeting("direct_scatter", left.head + right.head, left, right))
    return tuple(events)


def reflect_event(event, length):
    return Event(event.kind, 2 * (length - 1) - event.root_twice,
                 tuple(length - 1 - j for j in reversed(event.before)),
                 tuple(length - 1 - j for j in reversed(event.after)), event.stride)


def event_record(event, chain):
    changes = event.changed()
    return asdict(event) | {
        "response_toggles": sorted(changes),
        "physical_changes": sorted(chain.literal(changes)),
        "centre_shift": abs(event.after[0] - event.before[0]) if event.kind == "travel" else 0,
    }


def count_paths(graph, start):
    indegrees = Counter(child for edges in graph.values() for child in edges)
    queue = deque([start])
    ways = {start: 1}
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for child in graph[node]:
            ways[child] = ways.get(child, 0) + ways[node]
            indegrees[child] -= 1
            if indegrees[child] == 0:
                queue.append(child)
    if visited != len(graph):
        raise AssertionError("a reachable cycle would invalidate terminal-history counting")
    return sum(ways[node] for node, edges in graph.items() if not edges)


def enumerate_histories(name, initial, chain, direct=False):
    @cache
    def actions(positions):
        return enabled(positions, chain.length, direct)

    queue = deque([initial])
    graph = {}
    histories = {initial: ((), (), ())}
    history_split = None
    square_split = None
    meeting_events = set()
    diamond_count = 0
    costs = Counter()
    physical = chain.literal(initial)
    while queue:
        state = queue.popleft()
        current = actions(state)
        graph[state] = []
        for first, second in combinations(current, 2):
            one = first.apply(state)
            two = second.apply(state)
            if second in actions(one) and first in actions(two):
                assert first.apply(two) == second.apply(one)
                diamond_count += 1
            elif square_split is None:
                square_split = {"occupied": sorted(state), "first": event_record(first, chain),
                                "second": event_record(second, chain)}
        mirror = frozenset(chain.length - 1 - at for at in state)
        assert {reflect_event(event, chain.length) for event in current} == set(actions(mirror))
        for event in current:
            # Restrict what is occupied, while leaving the actual path endpoints in place.
            window = frozenset(at for at in state if abs(2 * at - event.root_twice) <= 2 * READ_RADIUS)
            assert event in actions(window)
            after = event.apply(state)
            changes = chain.literal(event.changed())
            assert chain.literal(state) ^ chain.literal(after) == changes
            costs[event.kind, event.stride, len(event.changed()), len(changes)] += 1
            if not event.stride:
                meeting_events.add(event)
            graph[state].append(after)
            projected = list(histories[state])
            arm = event.stride - 1 if event.stride else 2
            projected[arm] += (event,)
            history = tuple(projected)
            if after not in histories:
                histories[after] = history
                if len(histories) > MAX_STATES:
                    raise ValueError(f"{name} exceeded {MAX_STATES} reachable states")
                queue.append(after)
            elif histories[after] != history and history_split is None:
                history_split = {
                    "same_occupied_state": sorted(after),
                    "first_meetings": [asdict(e) for e in histories[after][2]],
                    "other_meetings": [asdict(e) for e in history[2]],
                    "first_travel_counts": list(map(len, histories[after][:2])),
                    "other_travel_counts": list(map(len, history[:2])),
                }
    terminal = sorted((state for state, nxt in graph.items() if not nxt), key=lambda state: tuple(sorted(state)))
    # Use one event history as a literal replay. Every interleaving is counted separately.
    witness = terminal[len(terminal) // 2]
    return {
        "case": name, "initial": sorted(initial), "initial_physical_changes_from_zero": sorted(physical),
        "reachable_states": len(graph), "arcs": sum(map(len, graph.values())),
        "complete_schedules": count_paths(graph, initial), "commuting_event_pairs": diamond_count,
        "square_failure": square_split, "projected_history_failure": history_split,
        "literal_reflection_covariant": True, "enabled_events_retained_by_radius_14": True,
        "terminal_states": [sorted(state) for state in terminal],
        "joined_event_roots_twice": sorted({e.root_twice for e in meeting_events}),
        "joined_event_details": [event_record(e, chain) for e in sorted(meeting_events, key=lambda e: e.before)],
        "one_terminal_replay_by_packet_and_meeting": [
            [event_record(event, chain) for event in history] for history in histories[witness]
        ],
        "costs": [{"event": kind, "stride": stride, "changed_responses": positions,
                   "changed_physical_distinctions": distinctions, "observed_arcs": count}
                  for (kind, stride, positions, distinctions), count in sorted(costs.items())],
    }


def scattering_controls(chain):
    left = frozenset({10, 11, 13})
    right = frozenset({65, 67, 68, 69})
    marker = frozenset(range(36, 43))
    paired = left | right
    marked = paired | marker
    mirrored = frozenset(chain.length - 1 - at for at in marked)
    specs = (
        ("both_with_visible_meeting", marked, False),
        ("both_with_visible_meeting_reflected", mirrored, False),
        ("stride_one_alone_with_visible_meeting", left | marker, False),
        ("stride_two_alone_with_visible_meeting", right | marker, False),
        ("both_with_no_meeting_mark", paired, False),
        ("both_with_unmarked_direct_scatter_variant", paired, True),
    )
    return {"marker": sorted(marker), "marker_physical_support": sorted(chain.literal(marker)),
            "packet_words": WORDS, "ordinary_gap": CLEARANCE, "marked_meeting_gap": MEETING_GAP,
            "read_radius_in_response_steps": READ_RADIUS, "reachable_states_cap": MAX_STATES,
            "cases": [enumerate_histories(name, initial, chain, direct) for name, initial, direct in specs]}


def expanded(positions, radius, length):
    return {j for at in positions for j in range(max(0, at - radius), min(length, at + radius + 1))}


def flood(seed, radius, chain, reverse):
    state = frozenset(seed)
    chronology = []
    while eligible := expanded(state, radius, chain.length) - state:
        target = (max if reverse else min)(eligible)
        change = chain.literal(frozenset({target}))
        assert len(change) == 4
        after = state | {target}
        assert chain.literal(state) ^ chain.literal(after) == change
        state = after
        chronology.append(target)
    return state, chronology


def scalar_additive(current, radius, length):
    return frozenset(at - radius for at in current if at >= radius) ^ frozenset(
        at + radius for at in current if at + radius < length
    )


def additive_site(current, index, radius):
    new = ((index - radius in current) != (index + radius in current))
    return current ^ {index} if new != (index in current) else current


def two_streams(seed, radius, level):
    """Ordered channels supplied only for comparison with the scalar frame reader."""
    return frozenset({seed + (level - 3) * radius}), frozenset({seed - (level - 3) * radius})


def record_state(state, chain):
    return {"responses": sorted(state), "physical_changes_from_zero": sorted(chain.literal(state))}


def scalar_controls(radius, chain):
    centre = chain.length // 2
    initial = frozenset({centre})
    levels = [initial]
    for level in range(1, 5):
        successor = scalar_additive(levels[-1], radius, chain.length)
        assert min(successor) == centre - radius * level and max(successor) == centre + radius * level
        levels.append(successor)
    assert levels[4] == {centre - 4 * radius, centre + 4 * radius}

    i, j = centre, centre + radius
    ij = additive_site(additive_site(initial, i, radius), j, radius)
    ji = additive_site(additive_site(initial, j, radius), i, radius)
    assert not ij and ji == {i, j}

    past_positive, past_negative = two_streams(centre, radius, -1)
    now_positive, now_negative = two_streams(centre, radius, 0)
    previous = past_positive ^ past_negative
    current = now_positive ^ now_negative
    frame_rows = []
    for depth in range(7):
        left, right = two_streams(centre, radius, depth)
        assert current == left ^ right
        image = scalar_additive(current, radius, chain.length)
        following = previous ^ image
        assert following ^ image == previous
        frame_rows.append({"frame_index": depth, "previous": record_state(previous, chain),
                           "current": record_state(current, chain),
                           "supplied_positive_stream": sorted(left), "supplied_negative_stream": sorted(right),
                           "physical_changes_to_next_frame": sorted(chain.literal(current ^ following))})
        previous, current = current, following
    assert not frame_rows[3]["current"]["responses"] and frame_rows[4]["current"]["responses"]
    return {
        "synchronous_scalar": [
            record_state(state, chain) | {
                "logical_tick": i, "primitive_response_toggles_to_next": len(state ^ levels[i + 1]),
                "physical_changes_to_next": len(chain.literal(state ^ levels[i + 1])),
            } if i + 1 < len(levels) else record_state(state, chain) | {"logical_tick": i}
            for i, state in enumerate(levels)
        ],
        "asynchronous_site_attempts": {"sites": [i, j], "first_then_second": sorted(ij),
                                       "second_then_first": sorted(ji),
                                       "physical_first_then_second": sorted(chain.literal(ij)),
                                       "physical_second_then_first": sorted(chain.literal(ji))},
        "reversible_two_ordered_frames": frame_rows,
    }


def propagation_controls(chain):
    centre = chain.length // 2
    rows = []
    for r in RADII:
        up, chronology_up = flood({centre}, r, chain, reverse=False)
        down, chronology_down = flood({centre}, r, chain, reverse=True)
        assert up == down == frozenset(range(chain.length))
        ranked = [frozenset({centre})]
        for depth in range(1, 5):
            ranked.append(frozenset(expanded(ranked[-1], r, chain.length)))
            assert min(ranked[-1]) == centre - r * depth and max(ranked[-1]) == centre + r * depth
        seed_pair = {centre - 3*r, centre + 3*r}
        pair, _ = flood(seed_pair, r, chain, reverse=False)
        assert pair == up
        rows.append({
            "radius_in_response_steps": r,
            "monotone_flood": {"causal_rank_rulers": [[min(x), max(x)] for x in ranked],
                               "terminal": record_state(up, chain), "primitive_weight": 4,
                               "left_biased_order": chronology_up, "right_biased_order": chronology_down,
                               "different_orders": chronology_up != chronology_down,
                               "two_seed_run_also_fills_chain": True},
        } | scalar_controls(r, chain))
    return rows


def main():
    chain = PhysicalChain()
    print(json.dumps({
        "freeze": "011396144", "fixture": "B81", "cluster_size": 2, "ordinary_responses": chain.length,
        "literal_response_supports": [sorted(chain.literal(frozenset({i}))) for i in range(chain.length)],
        "scattering": scattering_controls(chain),
        "propagation_and_additive_comparisons": propagation_controls(chain),
    }, indent=2))


if __name__ == "__main__":
    main()
