"""Close the one-shrink distance-five reader on exact terminal cut records."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import argparse
import json
import sys

import closure


LIVE_SIZE = 7
LIVE_MASK = (1 << LIVE_SIZE) - 1
RETIRED = 7
NO_LOW_HOLDER = 8
NO_HIGH = -1


def indices(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def mask(bits):
    return sum(1 << bit for bit in bits)


@dataclass(frozen=True, slots=True)
class Arc:
    following: closure.State
    parents: tuple
    outputs: int
    keep: tuple
    maps: tuple
    budget: int


def make_arc(state, parents, outputs, following):
    old = state.frontier
    newborn = len(old.loose)
    loose = tuple(count - (i in parents) for i, count in enumerate(old.loose))
    adjacent = tuple(word | ((1 << newborn) if i in parents else 0)
                     for i, word in enumerate(old.adjacent))
    retired = (*old.retired, *(adjacent[i] for i, count in enumerate(loose) if count == 0))
    retained = (*tuple(i for i, count in enumerate(loose) if count), newborn)
    raw = closure.OLD.Frontier((*loose, outputs), (*adjacent, mask(parents)), retired).restrict(retained)
    high = newborn if outputs == 3 else state.high_holder
    old_mark = retained.index(high) if high in retained else closure.NO_LIVE_MARKER
    front, mark, order = closure.canonical(raw, old_mark)
    assert (front, mark) == (following.frontier, following.high_holder)
    keep = tuple(retained[i] for i in order)
    maps = tuple(mask(i for i, j in enumerate(keep) if word & (1 << j))
                 for word in range(1 << (newborn + 1)))
    return Arc(following, parents, outputs, keep, maps, 7 - following.shrinks)


def relevant_frontiers():
    initials, reps, arcs, _, _ = closure.explore()
    targets = {state for state in arcs if state.prior_shrinks != closure.NOT_YET and state.shrinks == 1
               and any(len(group) == 3 for group, _, _ in arcs[state])}
    back = defaultdict(set)
    for state, choices in arcs.items():
        for _, _, dest in choices:
            back[dest].add(state)
    retained = set(targets)
    queue = list(sorted(targets))
    for state in queue:
        for predecessor in sorted(back[state] - retained):
            retained.add(predecessor)
            queue.append(predecessor)
    actions = {state: tuple(make_arc(state, group, h, nxt) for group, h, nxt in arcs[state]
                            if nxt in retained) for state in sorted(retained)}
    entries = [reps[state][0] for state in initials.values() if state in retained]
    return entries, actions, targets


def packed_record(live, high, weight):
    return ((high << LIVE_SIZE | live) << 3) | weight


def unpack(record):
    return (record >> 3 & LIVE_MASK), record >> (3 + LIVE_SIZE), record & 7


def literal_layout(rows, live, high_bits, high_site):
    holders, adjacent = closure.RULE.incidence(dict(enumerate(rows)))
    colors = {live[0]: 0}
    queue = [live[0]]
    for site in queue:
        for other in sorted(adjacent[site]):
            side = 1 ^ colors[site]
            if other in colors:
                assert colors[other] == side
            else:
                colors[other] = side
                queue.append(other)
    current_color = mask(i for i, site in enumerate(live) if colors[site])
    high_color = colors[high_site] if high_site is not None else NO_HIGH
    positions = {site: i for i, site in enumerate(live)}
    status = []
    for bit in high_bits:
        other = set(holders[bit]) - {high_site}
        status.append(positions.get(next(iter(other)), RETIRED) if other else NO_LOW_HOLDER)
    return current_color, high_color, tuple(status)


def literal_cuts(rows, live, high_bits, budget):
    supports = [mask(row) for row in rows]
    words = [0]
    least = {}
    for subset in range(1 << len(rows)):
        if subset:
            bit = subset & -subset
            words.append(words[subset ^ bit] ^ supports[bit.bit_length() - 1])
        word = words[subset]
        weight = word.bit_count()
        if weight <= budget:
            flags = mask(i for i, bit in enumerate(high_bits) if word & (1 << bit))
            membership = mask(i for i, site in enumerate(live) if subset & (1 << site))
            key = packed_record(membership, flags, 0)
            least[key] = min(weight, least.get(key, 8))
    return tuple(sorted(key | weight for key, weight in least.items()))


def starter(rows):
    state, live, _ = closure.snapshot(rows, closure.NOT_YET, None)
    colors, high_color, status = literal_layout(rows, live, (), None)
    cuts = literal_cuts(rows, live, (), 7)
    return state, colors, high_color, status, cuts


def advance(node, arc):
    base, colors, high_color, status, cuts = node
    n = len(base.frontier.loose)
    new_bit = 1 << n
    taken = mask(arc.parents)
    parent_color = (colors >> arc.parents[0]) & 1
    assert colors & taken in (0, taken)
    birth = arc.outputs == 3
    consumes_high = base.high_holder in arc.parents
    move_high_flag = 0
    moved_status = ()
    new_index = arc.keep.index(n)
    next_colors = arc.maps[colors | (new_bit if not parent_color else 0)]
    next_high_color = high_color if not birth else 1 ^ parent_color
    flip = next_colors & 1
    if flip:
        next_colors ^= (1 << len(arc.keep)) - 1
        if next_high_color != NO_HIGH:
            next_high_color ^= 1
    mapped_holder = {i: j for j, i in enumerate(arc.keep)}
    if birth:
        moved_status = (*tuple(mapped_holder.get(i, RETIRED) for i in arc.parents),
                        NO_LOW_HOLDER, NO_LOW_HOLDER, NO_LOW_HOLDER)
    elif status:
        moved_status = tuple(mapped_holder.get(i, RETIRED) if i < RETIRED else i for i in status)
        if consumes_high:
            slot = status.index(NO_LOW_HOLDER)
            moved_status = (*moved_status[:slot], new_index, *moved_status[slot + 1:])
            move_high_flag = 1 << slot

    least = {}
    larger = len(arc.parents) + arc.outputs
    for record in cuts:
        live, high, weight = unpack(record)
        new_weight = weight + larger - 2 * (live & taken).bit_count()
        if birth:
            high = mask(j for j, i in enumerate(arc.parents) if live & (1 << i))
            selected_flags = high ^ 63
        else:
            selected_flags = high ^ move_high_flag
        if weight <= arc.budget:
            key = packed_record(arc.maps[live], high, 0)
            least[key] = min(weight, least.get(key, 8))
        if new_weight <= arc.budget:
            key = packed_record(arc.maps[live | new_bit], selected_flags, 0)
            least[key] = min(new_weight, least.get(key, 8))
    return arc.following, next_colors, next_high_color, moved_status, tuple(sorted(key | w for key, w in least.items()))


def candidate_assignments(node):
    base, colors, high_color, status, cuts = node
    mandatory = mask(i for i, holder in enumerate(status) if holder == NO_LOW_HOLDER)
    roles = defaultdict(list)
    for bit, holder in enumerate(status):
        if holder != NO_LOW_HOLDER:
            role = holder if holder < RETIRED else RETIRED + bit
            roles[role].append(bit)
    labels = 6
    low_loose = {}
    for holder, count in enumerate(base.frontier.loose):
        if holder != base.high_holder:
            assigned = tuple(range(labels, labels + count))
            labels += count
            roles[holder].extend(assigned)
            low_loose[holder] = mask(assigned)
        else:
            assert count == mandatory.bit_count()
    near = [0] * labels
    for record in cuts:
        membership, support, _ = unpack(record)
        for i in indices(membership):
            support |= low_loose.get(i, 0)
        for edge in indices(support):
            near[edge] |= support ^ (1 << edge)

    def clique(word):
        return all(word & ~near[i] == (1 << i) for i in indices(word))

    assignments = []
    k = 6 - mandatory.bit_count()
    ground = (1 << labels) - 1
    for color in (0, 1):
        distinct = [bits for holder, bits in sorted(roles.items())
                    if (1 ^ high_color if holder >= RETIRED else colors >> holder & 1) == color]
        for holders in combinations(distinct, k):
            for columns in product(*holders):
                selected = mask(columns)
                high = mandatory | selected
                exterior = ground ^ selected
                if clique(high) and clique(exterior):
                    assignments.append(high)
    assert len(assignments) == len(set(assignments)) and 63 in assignments
    return sorted(assignments)


def recover(node, previous):
    trail = []
    while previous[node][0] is not None:
        node, arc = previous[node]
        trail.append(arc)
    rows = previous[node][1]
    _, live, _ = closure.snapshot(rows, closure.NOT_YET, None)
    high = None
    high_bits = ()
    for arc in reversed(trail):
        parent_sites = tuple(live[i] for i in arc.parents)
        cooked = closure.J.advance(rows, parent_sites, arc.outputs)
        if arc.outputs == 3:
            high = len(rows)
            high_bits = cooked[-1]
        live = tuple((*live, len(rows))[i] for i in arc.keep)
        rows = cooked
    return rows, live, high, high_bits


def named_supports(choices, live, loose, high, high_bits):
    names = (*high_bits, *(bit for site in live if site != high for bit in sorted(loose[site])))
    return sorted(tuple(sorted(names[i] for i in indices(choice))) for choice in choices)


def literal_candidates(rows, high):
    """Measure the terminal pairs and test complete assignments on the original names."""
    owners, _ = closure.RULE.incidence(dict(enumerate(rows)))
    low = {bit: set(sites) - {high} for bit, sites in owners.items()}
    ground = {bit for bit, sites in low.items() if not sites}
    dangling = {bit for bit, sites in low.items() if len(sites) == 1}
    terminal_mask = mask(ground | dangling)

    space = {0}
    colors = []
    first_user = {}
    for i, row in enumerate(rows):
        parents = {first_user[bit] for bit in row if bit in first_user}
        sides = {colors[parent] for parent in parents}
        assert len(sides) <= 1
        colors.append(1 ^ sides.pop() if sides else 0)
        for bit in row:
            first_user.setdefault(bit, i)
        check = mask(row)
        space |= {old ^ check for old in space}
    near = {pair for word in space if word.bit_count() <= 6
            for pair in combinations(indices(word & terminal_mask), 2)}

    alternatives = []
    for taken in combinations(sorted(dangling), 6 - len(ground)):
        holders = {next(iter(low[bit])) for bit in taken}
        if len(holders) != len(taken) or len({colors[i] for i in holders}) != 1:
            continue
        assigned = sorted(ground | set(taken))
        exterior = sorted(ground | (dangling - set(taken)))
        if all(pair in near for word in (assigned, exterior) for pair in combinations(word, 2)):
            alternatives.append(tuple(assigned))
    return sorted(alternatives)


def test_replay(node, previous):
    rows, live, high, high_bits = recover(node, previous)
    base, colors, high_color, status, cuts = node
    assert (colors, high_color, status) == literal_layout(rows, live, high_bits, high)
    assert cuts == literal_cuts(rows, live, high_bits, 7 - base.shrinks)
    holders, _ = closure.RULE.incidence(dict(enumerate(rows)))
    loose = closure.RULE.loose_ports(holders)
    named = named_supports(candidate_assignments(node), live, loose, high, high_bits)
    assert named == literal_candidates(rows, high)
    return rows, high_bits, named


def empty_menu_control():
    rows = ((0, 1, 2), (0, 3, 4, 5), (1, 6, 7, 8), (3, 6, 9, 10), (4, 7, 11, 12),
            (9, 11, 13, 14), (5, 13, 15, 16), (2, 15, 17, 18), (8, 17, 19, 20), (18, 14, 21, 22),
            (10, 16, 19, 23, 24, 25), (12, 20, 21, 26, 27))
    high = 10
    state, live, loose = closure.snapshot(rows, 0, high)
    high_bits = rows[high]
    roles = literal_layout(rows, live, high_bits, high)
    cuts = literal_cuts(rows, live, high_bits, 6)
    choices = named_supports(candidate_assignments((state, *roles, cuts)), live, loose, high, high_bits)
    assert choices == literal_candidates(rows, high) and len(choices) == 4
    assert not closure.actual_triples(rows)
    return {"supports": rows, "possible_high_supports": choices, "legal_triples": []}


def run(limit):
    starters, arcs, targets = relevant_frontiers()
    initial = {starter(rows): (None, rows) for rows in starters}
    previous = initial.copy()
    queue = deque(initial)
    identifiers = {node: i for i, node in enumerate(initial)}
    frontier_ids = {base: i for i, base in enumerate(arcs)}
    digest = sha256()
    checked_states = Counter()
    checked_arcs = 0
    positive_by_role = Counter()
    sizes = Counter()
    replays = []
    covered = set()
    aliases = set()
    while queue:
        node = queue.popleft()
        base, colors, high_color, status, cuts = node
        phase = base.prior_shrinks != closure.NOT_YET, base.shrinks
        checked_states[phase] += 1
        sizes[len(cuts)] += 1
        if base in targets:
            allowed = candidate_assignments(node)
            covered.add(base)
            signature = base.prior_shrinks, status.count(NO_LOW_HOLDER)
            positive_by_role[signature] += 1
            if len(allowed) > 1:
                rows, high, named = test_replay(node, previous)
                return {"closed": False, "filter_counterexample": {"supports": rows, "high_bits": high,
                                                                      "possible_high_supports": named,
                                                                      "frontier": base.description()},
                        "states_examined": sum(checked_states.values()), "states_reached": len(previous)}
            if signature not in aliases:
                rows, high, named = test_replay(node, previous)
                replays.append({"prior_shrinks": signature[0], "loose_high_bits": signature[1], "supports": rows,
                                "high_bits": high, "terminal_cuts": len(cuts), "possible_high_supports": named})
                aliases.add(signature)
        successors = []
        for arc in arcs[base]:
            next_node = advance(node, arc)
            checked_arcs += 1
            if next_node not in previous:
                previous[next_node] = (node, arc)
                identifiers[next_node] = len(identifiers)
                queue.append(next_node)
            successors.append(identifiers[next_node])
        rec = (frontier_ids[base], colors, high_color, status, cuts, successors)
        digest.update(json.dumps(rec, separators=(",", ":")).encode() + b"\n")
        if not sum(checked_states.values()) % 20000:
            print(f"Visited {sum(checked_states.values())} and found {len(previous)} states.", file=sys.stderr, flush=True)
        if limit and len(previous) >= limit:
            return {"closed": False, "state_limit": limit, "states_examined": sum(checked_states.values()),
                    "states_reached": len(previous), "positive_records_tested": sum(positive_by_role.values())}
    assert covered == targets
    return {"closed": True, "base_records": len(arcs), "base_positive_records": len(targets),
            "augmented_records": len(previous), "transition_checks": checked_arcs,
            "positive_records_tested": sum(positive_by_role.values()),
            "all_positive_records_unique_high_support": True,
            "positive_records_by_prior_shrinks_and_loose_high": [(*role, count) for role, count in sorted(positive_by_role.items())],
            "records_by_phase": [(int(high), shrinks, count) for (high, shrinks), count in sorted(checked_states.items())],
            "record_sizes": sorted(sizes.items()), "fixed_point_sha256": digest.hexdigest(),
            "literal_cut_controls": replays, "empty_menu_control": empty_menu_control()}


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--state-limit", type=int, default=0)
    print(json.dumps(run(args.parse_args().state_limit), indent=2))
