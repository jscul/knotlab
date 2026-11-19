"""Grade positive triple menus after the alternate third three-fresh births.

The same quotient and its proof in closure.md apply when the marked holder
is omitted and the one additional three-fresh birth instead uses one or
two parents. Breadth-first search covers both initial shapes. The witness
is replayed independently using the predecessor's literal parent check.
"""

from collections import Counter, defaultdict, deque
from itertools import chain
import argparse
import json

from closure import J, OLD, RULE, actual_triples, encode


INITIAL = {(False, J.literal_snapshot(rows)[0]): rows for rows in J.initial_histories()}


def transitions(used, allowed, extra_parents):
    for parents in allowed:
        if len(parents) >= 2:
            yield parents, 2
        if not used and len(parents) == extra_parents:
            yield parents, 3


def literal_witness(target, ancestry):
    itinerary = []
    state = target
    while ancestry[state] is not None:
        parent, group, outputs = ancestry[state]
        itinerary.append((state, group, outputs))
        state = parent
    rows = INITIAL[state]
    extra_site = None
    extra_group = ()
    shrinks_before = 0
    for child, group, outputs in reversed(itinerary):
        frontier, names, loose = J.literal_snapshot(rows)
        assert frontier == state[1]
        allowed = OLD.verify_literal_moves(rows, frontier, names, loose)
        assert group in allowed
        if outputs == 3:
            assert extra_site is None
            extra_site = len(rows)
            extra_group = tuple(names[i] for i in group)
            shrinks_before = 7 - sum(frontier.loose)
        rows = J.advance(rows, tuple(names[i] for i in group), outputs)
        assert J.literal_snapshot(rows)[0] == child[1]
        state = child
    assert extra_site is not None and state == target
    menu = tuple(sorted(actual_triples(rows)))
    assert menu
    boundary = tuple(sorted(chain.from_iterable(J.literal_snapshot(rows)[2].values())))
    assert RULE.legal_local_move(dict(enumerate(rows)), menu[0], OLD.FRESH_FOR_PARENT_TEST)
    return {**encode(rows, extra_site, menu[0]), "extra_parents": extra_group,
            "shrinks_before_extra": shrinks_before,
            "shrinks_after_extra": sum(len(scope) == 5 for i, scope in enumerate(rows) if i != extra_site)
                                    - shrinks_before,
            "true_loose_bits": boundary, "all_legal_triples": menu}


def census(extra_parents, threshold, stop_after_witness):
    queue = deque(INITIAL)
    previous = dict.fromkeys(INITIAL)
    stages = dict.fromkeys(INITIAL, 3)
    statistics = defaultdict(Counter)
    first = {}
    checked_transitions = 0
    fixed_point = True
    while queue:
        state = queue.popleft()
        used, frontier = state
        sites = stages[state]
        loose = sum(frontier.loose)
        shrinks = 7 + ((3 - extra_parents) if used else 0) - loose
        assert shrinks >= 0
        allowed = tuple(OLD.possible_parents(frontier))
        triples = sum(len(parents) == 3 for parents in allowed)
        counts = statistics[used, shrinks]
        counts.update(states=1, states_with_legal_triples=bool(triples), legal_holder_triples=triples)
        if used and triples and shrinks not in first:
            first[shrinks] = state
            if stop_after_witness and shrinks >= threshold:
                fixed_point = False
                break
        for parents, outputs in transitions(used, allowed, extra_parents):
            checked_transitions += 1
            next_step = (used or outputs == 3), J.step(frontier, parents, outputs)
            if next_step in previous:
                continue
            previous[next_step] = state, parents, outputs
            stages[next_step] = sites + 1
            queue.append(next_step)
    eligible = [state for shrinks, state in first.items() if shrinks >= threshold]
    witness = None
    if eligible:
        state = min(eligible, key=stages.__getitem__)
        witness = literal_witness(state, previous)
        assert witness["site_count"] == stages[state]
        assert witness["shrinks_before_extra"] + witness["shrinks_after_extra"] >= threshold
        assert witness["width"] == 2 * witness["site_count"] + 4
    return {
        "third_three_fresh_parent_count": extra_parents, "shrink_threshold": threshold,
        "closed_fixed_point": fixed_point, "states_discovered": len(previous),
        "states_processed": sum(c["states"] for c in statistics.values()), "transitions_generated": checked_transitions,
        "first_positive_state_at_or_above_threshold": witness,
        "first_positive_width_by_exact_shrink_count": {
            s: 2 * stages[state] + 4 for s, state in sorted(first.items())
        },
        "distribution": [
            {"third_three_fresh_birth_has_occurred": used, "shrinks": shrinks,
             "loose_bits": 7 + ((3 - extra_parents) if used else 0) - shrinks, **values}
            for (used, shrinks), values in sorted(statistics.items())
        ],
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--shortest", action="store_true", help="stop each branch on its first qualifying positive state")
    args = cli.parse_args()
    cases = {"binary_third": census(2, 2, args.shortest),
             "unary_third": census(1, 3, args.shortest)}
    print(json.dumps(cases, indent=2))


if __name__ == "__main__":
    main()
