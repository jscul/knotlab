"""Close the binary-third family by the exact loose-holder transition."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from importlib import util
from itertools import chain, product
import json
from math import prod
from pathlib import Path
import sys


PROOFS = Path(__file__).resolve().parents[2]
PREVIOUS = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001J" / "VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six"
K_FILE = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001K" / "VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh/alternate.json"
FROZEN = {
    PREVIOUS / "frontier.py": "ef602d7b51ed1c5e3bcdf738ce3cd291bba6143e985d7feb4ac088edbec85773",
    PREVIOUS / "frontier.json": "84624e514dd16a36a177c8730e426d188c0ad6e5cac91b17a66aab555fed5605",
    K_FILE: "c0b13cd00b9ffc4540654525614f99d78fc3bb51fc3f0ef14112a3438f283649",
}
NOT_YET = -1


def verified(path):
    content = path.read_bytes()
    assert sha256(content).hexdigest() == FROZEN[path]
    return content


verified(PREVIOUS / "frontier.py")
spec = util.spec_from_file_location("binary_third_parent_frontier", PREVIOUS / "frontier.py")
J = util.module_from_spec(spec)
sys.modules[spec.name] = J
spec.loader.exec_module(J)
OLD = J.old
RULE = OLD.original_rule()


@dataclass(frozen=True, order=True)
class State:
    prior_shrinks: int
    front: OLD.Frontier

    @property
    def used(self):
        return self.prior_shrinks != NOT_YET

    @property
    def loose(self):
        return sum(self.front.loose)

    @property
    def shrinks(self):
        return (8 if self.used else 7) - self.loose

    def roster(self):
        return (self.front.loose, self.front.adjacent, self.front.retired)


def options(state, allowed):
    moves = []
    for group in allowed:
        if len(group) >= 2:
            moves.append((group, 2))
        if not state.used and len(group) == 2:
            moves.append((group, 3))
    return tuple(moves)


def memo_states():
    queue = deque()
    reps = {}
    initials = {}
    for label, rows in zip(("siblings", "chain"), J.initial_histories(), strict=True):
        state = State(NOT_YET, J.literal_snapshot(rows)[0])
        initials[label] = state
        reps[state] = rows, None
        queue.append(state)
    arcs = {}
    roster = {}
    while queue:
        state = queue.popleft()
        rows, special = reps[state]
        same, names, loose = J.literal_snapshot(rows)
        assert same == state.front
        width = 1 + max(chain.from_iterable(rows))
        assert width == 2 * len(rows) + 3 + state.used
        assert state.shrinks == sum(len(row) == 5 for row in rows) - state.used
        assert state.used == (special is not None)
        allowed = tuple(sorted(OLD.verify_literal_moves(rows, state.front, names, loose)))
        roster[state] = allowed
        nxt = []
        for parents, outputs in options(state, allowed):
            prior = state.shrinks if outputs == 3 else state.prior_shrinks
            following = State(prior, J.step(state.front, parents, outputs))
            nxt.append((parents, outputs, following))
            if following not in reps:
                advanced = J.advance(rows, tuple(names[i] for i in parents), outputs)
                new_special = len(rows) if outputs == 3 else special
                reps[following] = advanced, new_special
                queue.append(following)
        arcs[state] = tuple(nxt)
    return initials, reps, arcs, roster


def bits_for_groups(groups, names, loose):
    return tuple(sorted(tuple(sorted(bits)) for group in groups
                        for bits in product(*(loose[names[i]] for i in group))))


def describe(state, reps, roster):
    rows, special = reps[state]
    form, names, loose = J.literal_snapshot(rows)
    assert form == state.front
    allowed = roster[state]
    return {
        "width": 1 + max(chain.from_iterable(rows)), "site_count": len(rows),
        "junction_supports": rows, "binary_three_fresh_site": special,
        "prior_shrinks": None if not state.used else state.prior_shrinks,
        "total_shrinks": state.shrinks, "frontier": state.roster(),
        "live_holders_and_loose_bits": tuple((site, tuple(sorted(loose[site]))) for site in names),
        "legal_triples": bits_for_groups((ps for ps in allowed if len(ps) == 3), names, loose),
    }


def summaries(reps, arcs, roster):
    counts = defaultdict(Counter)
    first = {}
    positives = {}
    for state, allowed in roster.items():
        tag = state.prior_shrinks, state.shrinks
        first.setdefault(tag, state)
        triples = tuple(p for p in allowed if len(p) == 3)
        n = sum(prod(state.front.loose[i] for i in p) for p in triples)
        counts[tag].update(states=1, transitions=len(arcs[state]), states_with_a_legal_triple=int(bool(triples)),
                           legal_three_holder_groups=len(triples),
                           named_triple_choices_on_representatives=n)
        if triples:
            positives.setdefault(tag, state)
    rows = []
    for (prior, total), counts_by_group in sorted(counts.items()):
        tag = prior, total
        rows.append({
            "shrinks_before_special": None if prior == NOT_YET else prior, "total_shrinks": total,
            "loose_bits": (7 if prior == NOT_YET else 8) - total, **counts_by_group,
            "shortest_width": 2 * len(reps[first[tag]][0]) + 3 + (prior != NOT_YET),
            "shortest_positive_history": None if tag not in positives else describe(positives[tag], reps, roster),
        })
    return rows, first, positives


def complementary(front, left, allowed):
    spare = tuple(n - (i in left) for i, n in enumerate(front.loose))
    if any(n not in (0, 1) for n in spare):
        return None
    other = tuple(i for i, n in enumerate(spare) if n)
    return other if other in allowed else None


def complement_details(state, group, other, h, reps):
    rows, _ = reps[state]
    _, names, loose = J.literal_snapshot(rows)
    selected = {i: min(loose[names[i]]) for i in group}
    left = tuple(sorted(selected.values()))
    right = tuple(sorted(min(b for b in loose[names[i]] if b != selected.get(i)) for i in other))
    assert not set(left) & set(right)
    assert set(left) | set(right) == set(chain.from_iterable(loose.values()))
    assert RULE.legal_local_move(dict(enumerate(rows)), left, OLD.FRESH_FOR_PARENT_TEST)
    assert RULE.legal_local_move(dict(enumerate(rows)), right, OLD.FRESH_FOR_PARENT_TEST)
    return {"width_before_join": len(set(chain.from_iterable(rows))), "junction_supports": rows,
            "first_inputs": left, "second_inputs": right, "first_parent_count": len(group),
            "second_parent_count": len(other), "first_outputs": h, "same_distinct_holders": group == other}


def covers(reps, arcs, roster):
    stats = defaultdict(Counter)
    first = {}
    for state, links in arcs.items():
        for group, h, _ in links:
            if not state.used and h != 3:
                continue
            tag = state.prior_shrinks, state.loose, len(group), h
            entry = stats[tag]
            entry["moves"] += 1
            other = complementary(state.front, group, roster[state])
            if other is None:
                continue
            entry["moves_with_a_complement"] += 1
            entry["named_source_choices_with_complement"] += prod(state.front.loose[i] for i in group)
            entry["complement_uses_same_holders"] += group == other
            if tag not in first:
                first[tag] = complement_details(state, group, other, h, reps)
    return [
        {"shrinks_before_special": None if prior == NOT_YET else prior,
         "loose_bits": loose, "source_parent_count": size, "outputs": h,
         **{label: result[label] for label in ("moves", "moves_with_a_complement",
                                              "named_source_choices_with_complement", "complement_uses_same_holders")},
         "shortest_example": first.get((prior, loose, size, h))}
        for (prior, loose, size, h), result in sorted(stats.items())
    ]


def terminal_records(reps, arcs, roster):
    controls = []
    for state, allowed in roster.items():
        if not state.used or state.loose > 5:
            continue
        positive = any(len(group) == 3 for group in allowed)
        if not positive and state.loose != 4:
            continue
        item = describe(state, reps, roster)
        rows, _ = reps[state]
        _, names, loose = J.literal_snapshot(rows)
        continuations = []
        for parents, h, following in arcs[state]:
            chosen = tuple(min(loose[names[i]]) for i in parents)
            continuations.append({
                "representative_inputs": tuple(sorted(chosen)), "fresh_count": h,
                "target_frontier": following.roster(), "returns_to_same_frontier": following == state,
                "target_has_legal_triple": any(len(group) == 3 for group in roster[following]),
            })
        controls.append({
            **item, "legal_binary_input_sets": bits_for_groups((p for p in allowed if len(p) == 2), names, loose),
            "continuations": continuations, "minimum_positive_binary_return_length": shortest_return(state, arcs)
            if positive else None,
        })
    return controls


def shortest_return(start, arcs):
    queue = deque((following, 1) for parents, h, following in arcs[start] if len(parents) == 2 and h == 2)
    seen = {state for state, _ in queue}
    while queue:
        state, steps = queue.popleft()
        if state == start:
            return steps
        for parents, h, following in arcs[state]:
            if len(parents) == 2 and h == 2 and following not in seen:
                seen.add(following)
                queue.append((following, steps + 1))
    return None


def reverse_binary_trim(target, arcs):
    predecessors = defaultdict(set)
    for source, choices in arcs.items():
        if not source.used or source.shrinks != target.shrinks:
            continue
        for parents, h, following in choices:
            if len(parents) == 2 and h == 2:
                predecessors[following].add(source)
    queue = [target]
    reached = {target}
    for state in queue:
        for previous in sorted(predecessors[state] - reached):
            reached.add(previous)
            queue.append(previous)
    order = sorted(reached)
    numbered = {state: i for i, state in enumerate(order)}
    return {
        "target_index": numbered[target],
        "states_from_which_target_is_binary_reachable": [
            {"shrinks_before_special": state.prior_shrinks, "frontier": state.roster()} for state in order
        ],
        "binary_transitions_within_those_states": [
            (numbered[state], parents, numbered[following]) for state in order for parents, h, following in arcs[state]
            if len(parents) == 2 and h == 2 and following in numbered
        ],
    }


def connected(neighbors, side):
    start = min(side)
    reached = {start}
    queue = [start]
    for i in queue:
        for j in neighbors[i] & (side - reached):
            reached.add(j)
            queue.append(j)
    return reached == side


def five_cut(rows, shore):
    users, _ = RULE.incidence(dict(enumerate(rows)))
    exterior = len(rows)
    neighbors = [set() for _ in range(exterior + 1)]
    cut = []
    incoming = []
    for bit, owners in sorted(users.items()):
        a, b = (owners[0], exterior) if len(owners) == 1 else sorted(owners)
        neighbors[a].add(b)
        neighbors[b].add(a)
        if (a in shore) != (b in shore):
            cut.append(bit)
            if b in shore:
                incoming.append(bit)
    assert len(cut) == 5
    assert connected(neighbors, shore) and connected(neighbors, set(range(exterior + 1)) - shore)
    return {"shore_sites": tuple(sorted(shore)), "cut_bits": cut, "incoming": incoming,
            "bond_from_two_connected_shores": True}


def digest(arcs):
    numbered = {state: i for i, state in enumerate(sorted(arcs))}
    rows = [(state.prior_shrinks, state.roster(),
             [(group, h, numbered[following]) for group, h, following in arcs[state]]) for state in sorted(arcs)]
    return sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def before_control(arcs):
    states = sorted(state for state in arcs if not state.used)
    numbered = {state: i for i, state in enumerate(states)}
    rows = [[state.roster(), [(group, numbered[following]) for group, h, following in arcs[state] if h == 2]]
            for state in states]
    checksum = sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    old = json.loads(verified(PREVIOUS / "frontier.json"))["closure"]
    assert checksum == old["fixed_point_sha256"]
    return {"same_fixed_point_sha256_as_J": checksum, "states": len(states),
            "moves_with_two_outputs": sum(len(row[1]) for row in rows)}


def reach(initial, arcs):
    reached = {initial}
    queue = [initial]
    for state in queue:
        for _, _, following in arcs[state]:
            if following not in reached:
                reached.add(following)
                queue.append(following)
    return reached


def run():
    initials, reps, arcs, roster = memo_states()
    stats, earliest, positives = summaries(reps, arcs, roster)
    after_three = positives[0, 3]
    after_two_late_birth = positives[2, 2]
    a, _ = reps[after_three]
    b, special = reps[after_two_late_birth]
    previous_shortest = json.loads(verified(K_FILE))["binary_third"]["first_positive_state_at_or_above_threshold"]
    actual_shortest = min(2 * len(reps[state][0]) + 4 for (prior, shrinks), state in positives.items()
                          if prior != NOT_YET and shrinks >= 2)
    assert actual_shortest == previous_shortest["width"]
    sources = {label: reach(initial, arcs) for label, initial in initials.items()}
    assert set.union(*sources.values()) == set(arcs)
    return {
        "dependency_sha256": {str(path.relative_to(PROOFS)): checksum for path, checksum in FROZEN.items()},
        "closed_records": len(arcs), "transitions": sum(map(len, arcs.values())),
        "literal_representatives_validated": len(reps),
        "fixed_point_sha256": digest(arcs), "before_special_control": before_control(arcs),
        "records_by_initial_shape": {tag: len(group) for tag, group in sources.items()},
        "records_reached_from_both_shapes": len(set.intersection(*sources.values())),
        "distribution": stats, "min_loose_bits": min(state.loose for state in arcs if state.used),
        "max_total_shrinks_by_shrinks_before_special": {
            prior: max(state.shrinks for state in arcs if state.prior_shrinks == prior)
            for prior in sorted({prior for prior, _ in earliest} - {NOT_YET})
        },
        "terminal_controls_at_five_or_four_loose": terminal_records(reps, arcs, roster),
        "reverse_binary_trim_at_the_positive_three_shrink_state": reverse_binary_trim(after_three, arcs),
        "complementary_moves": covers(reps, arcs, roster),
        "positive_bond_size_five_controls": {
            "whole": {"source": describe(after_three, reps, roster),
                      "cut": five_cut(a, set(range(len(a))))},
            "proper": {"source": describe(after_two_late_birth, reps, roster),
                       "cut": five_cut(b, set(range(special)))},
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
