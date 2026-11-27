"""One completed ordinary round, identical allowed states, different family trees."""

import argparse
import hashlib
import json
import resource
from collections import Counter, defaultdict, deque
from itertools import combinations


ROOTS = (0, 5)
CHORDS = [(0, 2), (1, 5), (3, 7), (4, 8), (6, 9)]


def mask(names):
    return sum(1 << i for i in names)


def add_basis(pivots, word):
    while word:
        lead = word.bit_length() - 1
        if lead not in pivots:
            pivots[lead] = word
            return
        word ^= pivots[lead]


def legal_states(rows, limit):
    """Solve the displayed parity rows. Enumerate the choices of all free bits."""
    names = sorted(set().union(*rows.values()))
    pivots = {}
    for row in rows.values():
        add_basis(pivots, mask(row))
    generators = []
    for name in names:
        if name in pivots:
            continue
        word = 1 << name
        for lead in sorted(pivots):
            if (word & pivots[lead]).bit_count() % 2:
                word |= 1 << lead
        generators.append(word)
    count = 1 << len(generators)
    checked = min(limit, count) if limit is not None else count
    states = [0] * checked
    for index in range(1, checked):
        low = index & -index
        states[index] = states[index ^ low] ^ generators[low.bit_length() - 1]
    states.sort()
    supports = [mask(row) for row in rows.values()]
    assert len(set(states)) == checked
    assert all((word & row).bit_count() % 2 == 0 for word in states for row in supports)
    return states, count


def common_presentation():
    """The same final holders with two possible choices of the omitted even row."""
    base = [(i, (i + 1) % 10) for i in range(10)] + CHORDS
    final = defaultdict(set)
    inserts = {}
    next_holder = 10
    next_distinction = len(base)
    for root in ROOTS:
        inserts[root] = {}
        neighbors = sorted({b if a == root else a for a, b in base if root in (a, b)})
        for parent in neighbors:
            child = next_holder
            fresh = (next_distinction, next_distinction + 1)
            final[root].update(fresh)
            final[child].update(fresh)
            inserts[root][parent] = (child, fresh)
            next_holder += 1
            next_distinction += 2
    for name, (a, b) in enumerate(base):
        first = inserts[a][b][0] if a in ROOTS else a
        second = inserts[b][a][0] if b in ROOTS else b
        final[first].add(name)
        final[second].add(name)
    return dict(final), inserts


def incidences(rows):
    holder = defaultdict(list)
    for knot, row in rows.items():
        for name in row:
            holder[name].append(knot)
    shared = {knot: set() for knot in rows}
    loose = defaultdict(list)
    for name, knots in holder.items():
        if len(knots) == 1:
            loose[knots[0]].append(name)
        else:
            assert len(knots) == 2
            a, b = knots
            shared[a].add(b)
            shared[b].add(a)
    return shared, loose


def steps_from(source, adjacent):
    steps = {source: 0}
    pending = deque([source])
    while pending:
        current = pending.popleft()
        for other in adjacent[current] - steps.keys():
            steps[other] = steps[current] + 1
            pending.append(other)
    assert len(steps) == len(adjacent)
    return steps


def exact_round(start, insert, start_states, full):
    shared, loose = incidences(start)
    families = sorted(loose)
    assert len(families) == 3
    assert all(len(loose[knot]) == 1 for knot in families)
    assert all(not (shared[a] & shared[b]) for a, b in combinations(families, 2))
    previous = set().union(*start.values())
    grown = dict(start)
    for parent in families:
        child, fresh = insert[parent]
        old = loose[parent][0]
        if full:
            assert any(word & (1 << old) for word in start_states)
        # Zero candidate pairs, one unary birth per parent. The three births
        # have distinct parents, so their next-round group demand is zero.
        # Each input is open, so the three-place floor supplies two fresh bits.
        assert len(fresh) == max(0, 1, 3 - 1) and previous.isdisjoint(fresh)
        previous.update(fresh)
        grown[child] = {old, *fresh}
    assert set(families) == set(insert)
    after_shared, after_loose = incidences(grown)
    assert len(after_loose) == 3
    assert all(len(names) == 2 for names in after_loose.values())
    assert all(not (after_shared[a] & after_shared[b]) for a, b in combinations(after_loose, 2))
    return grown, families, loose, shared


def cluster_history(labels, costs):
    parts = [{i} for i in labels]
    levels = [{'threshold': 0, 'clusters': [[v] for v in labels]}]
    for weight in sorted(set(costs.values())):
        before = len(parts)
        for (i, j), cost in costs.items():
            if cost != weight:
                continue
            a = next(part for part in parts if i in part)
            b = next(part for part in parts if j in part)
            if a is not b:
                a.update(b)
                parts.remove(b)
        if len(parts) != before:
            levels.append({'threshold': weight, 'clusters': sorted(sorted(p) for p in parts)})
    return levels


def state_cluster_history(states):
    """A path of moves of weight at most k reaches their binary span from zero."""
    layers = defaultdict(list)
    for state in states:
        if state:
            layers[state.bit_count()].append(state)
    pivots = {}
    history = [{'threshold': 0, 'components': len(states), 'states_per_component': 1}]
    for weight, changes in sorted(layers.items()):
        old_rank = len(pivots)
        for change in changes:
            add_basis(pivots, change)
        if len(pivots) != old_rank:
            size = 1 << len(pivots)
            history.append({'threshold': weight, 'components': len(states) // size,
                            'states_per_component': size})
    assert history[-1]['components'] == 1
    return history


def local_projections(rows, states, complete):
    counts = Counter()
    for row in rows.values():
        support = mask(row)
        attained = {word & support for word in states}
        if complete:
            assert len(attained) == 1 << (len(row) - 1)
        counts[f'{len(row)} distinctions, {len(attained)} local states'] += 1
    return counts


def serialized_pairs(mapping):
    return {f'{a},{b}': v for (a, b), v in sorted(mapping.items())}


def evaluate(final, inserts, root, limit):
    target = {k: row for k, row in final.items() if k != root}
    new_holders = {child for child, _ in inserts[root].values()}
    start = {k: row for k, row in target.items() if k not in new_holders}
    source_states, source_count = legal_states(start, limit)
    grown, families, loose, shared = exact_round(start, inserts[root], source_states, limit is None)
    assert grown == target
    states, grown_count = legal_states(grown, limit)
    start_steps = {(a, b): steps_from(a, shared)[b] for a, b in combinations(families, 2)}
    original = {k: 1 << loose[k][0] for k in families}
    fresh = {k: mask(inserts[root][k][1]) for k in families}
    costs = {}
    tuples = Counter()
    for state in states:
        before = tuple(k for k in families if (state & original[k]).bit_count() % 2)
        after = tuple(k for k in families if (state & fresh[k]).bit_count() % 2)
        assert before == after
        tuples[before] += 1
        if len(after) == 2:
            costs[after] = min(costs.get(after, state.bit_count()), state.bit_count())
    if limit is None:
        assert set(tuples) == {(), *combinations(families, 2)}
        assert costs == {pair: d + 4 for pair, d in start_steps.items()}
    projections = {'start': local_projections(start, source_states, limit is None),
                   'round_one': local_projections(grown, states, limit is None)}
    history = cluster_history(families, costs)
    if limit is not None:
        return (dict(outside=root, source_states_checked=len(source_states),
                     round_one_states_checked=len(states), source_total=source_count,
                     round_one_total=grown_count, partial_family_levels=len(history)), states)
    return (dict(outside=root, start_knots=len(start), start_states=len(source_states),
                 round_one_knots=len(grown), round_one_states=len(states),
                 family_start_knots=families, start_loose={k: loose[k][0] for k in families},
                 births={parent: dict(child=child, fresh=list(new)) for parent, (child, new)
                         in inserts[root].items()},
                 start_distinctions=len(set().union(*start.values())),
                 round_one_distinctions=len(set().union(*grown.values())),
                 start_rows={k: sorted(row) for k, row in sorted(start.items())},
                 local_even_projections=projections,
                 start_steps=serialized_pairs(start_steps),
                 exact_two_fact_costs=serialized_pairs(costs),
                 states_per_family_tuple={str(k): v for k, v in tuples.items()},
                 family_single_linkage=history), states)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    cap = 1536 * 1024**2
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    final, inserts = common_presentation()
    cases, words = [], []
    for root in ROOTS:
        record, states = evaluate(final, inserts, root, 64 if args.pilot else None)
        cases.append(record)
        words.append(states)
    result = {'cycle': list(range(10)), 'additional_pairs': CHORDS, 'cases': cases}
    state_levels = state_cluster_history(words[0])
    if not args.pilot:
        assert words[0] == words[1] and len(words[0]) == 4096
        assert sorted(len(case['family_single_linkage']) for case in cases) == [2, 3]
        result['common_allowed_states'] = len(words[0])
        result['state_set_sha256'] = hashlib.sha256(
            b''.join(w.to_bytes(4, 'little') for w in words[0])
        ).hexdigest()
        result['single_linkage_of_allowed_states'] = state_levels
    else:
        result['partial_state_levels'] = len(state_levels)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
