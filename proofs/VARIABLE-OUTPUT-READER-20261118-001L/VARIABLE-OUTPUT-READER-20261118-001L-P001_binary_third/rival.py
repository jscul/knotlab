"""Targeted frontier control for a third unary three-fresh addition."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import chain, product
import json

from frontier import J, OLD, NOT_YET


MAX_SITES = 16


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
        return (9 if self.used else 7) - self.loose


def transitions(state, allowed):
    for group in allowed:
        if len(group) >= 2:
            yield group, 2
        if not state.used and len(group) == 1:
            yield group, 3


def next_state(state, group, h):
    prior = state.shrinks if h == 3 else state.prior_shrinks
    return State(prior, J.step(state.front, group, h))


def allowed(state):
    return tuple(OLD.possible_parents(state.front))


def literal(state, ancestry, roots):
    trace = []
    current = state
    while ancestry[current] is not None:
        previous, group, h = ancestry[current]
        trace.append((previous, current, group, h))
        current = previous
    rows = roots[current]
    special = None
    for previous, following, group, h in reversed(trace):
        front, names, loose = J.literal_snapshot(rows)
        assert front == previous.front
        assert group in OLD.verify_literal_moves(rows, front, names, loose)
        if h == 3:
            assert special is None and len(group) == 1
            special = len(rows)
        rows = J.advance(rows, tuple(names[i] for i in group), h)
        assert J.literal_snapshot(rows)[0] == following.front
    front, names, loose = J.literal_snapshot(rows)
    legal = OLD.verify_literal_moves(rows, front, names, loose)
    menu = tuple(sorted(tuple(sorted(bits)) for group in legal if len(group) == 3
                        for bits in product(*(loose[names[i]] for i in group))))
    assert state.used == (special is not None)
    assert state.shrinks == sum(len(row) == 5 for row in rows)
    return {
        "width": 1 + max(chain.from_iterable(rows)),
        "junction_supports": rows, "unary_third_site": special, "legal_triples": menu,
        "loose_bits": tuple(sorted(chain.from_iterable(loose.values()))),
    }


def bounded():
    roots = {State(NOT_YET, J.literal_snapshot(rows)[0]): rows for rows in J.initial_histories()}
    ancestry = dict.fromkeys(roots)
    depth = dict.fromkeys(roots, 3)
    queue = deque(roots)
    stats = defaultdict(Counter)
    grades = {}
    first_positive = {}
    examined_edges = 0
    while queue:
        state = queue.popleft()
        sites = depth[state]
        choices = allowed(state)
        n = sum(len(group) == 3 for group in choices)
        tag = (state.prior_shrinks, state.shrinks)
        stats[tag].update(states=1, positive=int(n > 0))
        if n and tag not in first_positive:
            first_positive[tag] = state
        if state.used and state.shrinks >= 4:
            witness = literal(state, ancestry, roots)
            assert bool(witness["legal_triples"]) == bool(n)
            grades[state] = witness
        if sites == MAX_SITES:
            continue
        for group, h in transitions(state, choices):
            examined_edges += 1
            following = next_state(state, group, h)
            if following not in ancestry:
                ancestry[following] = (state, group, h)
                depth[following] = sites + 1
                queue.append(following)
    return roots, ancestry, stats, grades, first_positive, examined_edges


def low_descendants(seeds, ancestry, roots):
    known = set(seeds)
    queue = list(seeds)
    examined = 0
    positive = []
    for state in queue:
        choices = allowed(state)
        if any(len(group) == 3 for group in choices):
            positive.append(literal(state, ancestry, roots))
        for group, h in transitions(state, choices):
            examined += 1
            following = next_state(state, group, h)
            if following in known:
                continue
            known.add(following)
            queue.append(following)
            if following not in ancestry:
                ancestry[following] = (state, group, h)
    return {"states": len(known), "transitions": examined, "positive_histories": positive}


def run():
    roots, ancestry, stats, grades, positive, edges = bounded()
    first_positive = [
        {"shrinks_before_unary_third": prior, "total_shrinks": total, **literal(state, ancestry, roots)}
        for (prior, total), state in sorted(positive.items()) if prior != NOT_YET and total >= 3
    ]
    result = {
        "bounded_ordinary_site_limit": MAX_SITES,
        "associated_width_limit_after_third_three_fresh_birth": 2 * MAX_SITES + 4,
        "bounded_states": len(ancestry), "bounded_transitions": edges,
        "distribution": [
            {"shrinks_before_unary_third": None if prior == NOT_YET else prior, "total_shrinks": total, **values}
            for (prior, total), values in sorted(stats.items())
        ],
        "first_positive_with_at_least_three_shrinks": first_positive,
        "literal_replays_at_or_above_four_shrinks": len(grades),
        "closed_descendants_of_the_bounded_four_or_more_shrink_records": low_descendants(grades, ancestry, roots),
    }
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
