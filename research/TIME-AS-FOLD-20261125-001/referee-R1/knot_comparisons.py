"""Rebuild comparisons for the positive readings and the predicted failure source."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import product

import networkx as nx
from pysat.solvers import Solver

from knot_counts import GROWTH_FILES, key, predicted_case, rows
from knot_replay import closure, group_structure, grow, holdings, members, parity_failures, relation


def nae_clauses(places):
    return [[sign * (d + 1) for d in places] for sign in (1, -1)]


def has_every_word(solver, places):
    if not places:
        return solver.solve()
    literals = [d + 1 for d in places]
    return all(solver.solve(assumptions=[literals[0], *[-d if bit else d
                                                   for d, bit in zip(literals[1:], word)]])
               for word in product((0, 1), repeat=len(places) - 1))


def nae_failures(growth, after):
    failures = []
    prefix = growth[0]
    holders = holdings(prefix.places)
    with Solver(bootstrap_with=[clause for places in prefix.places for clause in nae_clauses(places)]) as solver:
        if after == 0:
            for u, places in enumerate(prefix.places):
                passes = all(has_every_word(solver, tuple(d for d in places if d != forgotten))
                             for forgotten in places)
                if not passes:
                    failures.append(u)
        for state in growth[1:]:
            first = len(prefix.places)
            for u in range(first, len(state.places)):
                places = state.places[u]
                inputs = tuple(d for d in places if d in holders)
                assert len(places) > len(inputs)
                # Every old input word must be possible, since forgetting one fresh place otherwise leaves a constraint.
                if not has_every_word(solver, inputs):
                    failures.append(u)
            for u in range(first, len(state.places)):
                for clause in nae_clauses(state.places[u]):
                    solver.add_clause(clause)
            prefix = state
            holders = holdings(state.places)
    return failures


def parts(state):
    holders = holdings(state.places)
    roster = members(holders, state.barred)
    met, joined = group_structure(holders, roster, len(state.places), guard=False)
    signatures = {}
    for part in nx.connected_components(joined):
        signature = nx.Graph()
        for u in part:
            blocked = sum(d in state.barred and len(holders[d]) == 1 for d in state.places[u])
            signature.add_node(u, type=('member', len(roster[u]), blocked))
        sets = {frozenset(neighbors) for neighbors in met if neighbors <= part and len(neighbors) >= 2}
        for i, group in enumerate(group for group in sets if not any(group < other for other in sets)):
            signature.add_node(('met', i), type=('met',))
            signature.add_edges_from((u, ('met', i)) for u in group)
        signatures[tuple(sorted(part))] = signature
    return signatures


def own_birth_counts(state, first, x, y, after):
    x = closure(state.parents, x, first)
    y = closure(state.parents, y, first)
    own = Counter()
    joint = 0
    for u in range(after, len(state.parents)):
        parents = state.parents[u]
        if x.intersection(parents):
            if y.intersection(parents):
                joint += 1
            else:
                own[state.born[u]] += 1
    return dict(own), joint


def check_run(config, a, t, expected, bar=(), mask=None):
    last_round = expected.get('rounds')
    target_round = last_round + 1 if expected.get('stop') == 'guard' else last_round
    period_states, fresh, stop = grow(config, through=target_round, start=a[t], start_t=t, bar=bar,
                                      mask_roots=mask)
    reached = t + len(period_states) - 1
    if last_round is not None:
        assert reached == last_round and stop == expected['stop'], (config, t, reached, stop, expected)
    law = config[-1]
    state = period_states[-1]
    first = len(a[t].places)
    failed = parity_failures(state, first) if law == 'parity' else nae_failures(period_states, first)
    failure_relations = [{'knot': u, 'relation': relation(state.places, state.places[u])} for u in failed] if law == 'parity' else []
    return state, {'last_round': reached, 'stop': stop, 'new_knots': len(fresh),
                   'new_joins': sum(len(p) >= 2 for p in state.parents[first:]),
                   'implied_births': fresh.count(0),
                   'under_three_places': [u for u in range(first, len(state.places)) if len(state.places[u]) < 3],
                   'failing_knots': failed, 'failure_relations': failure_relations}


def tick_parts(a, series, row, comparison):
    tick = comparison['t_bar']
    ticks = {series['t0']: tuple(series['P0'])}
    ticks.update({t[0]: tuple(t[1]) for t in series['ticks']})
    current = ticks[tick]
    preceding_t = tick - row['period']
    past = ticks[preceding_t]
    past_count = len(a[preceding_t].places)
    now = a[tick]
    came_from_past = closure(now.parents, past, past_count)
    if not isinstance(comparison.get("B'"), dict) and not isinstance(comparison.get('Ball'), dict):
        return current, (), ()
    past_shape = parts(a[preceding_t])[past]
    qualifying = []
    given_off = []
    for part, shape in parts(now).items():
        if not came_from_past.intersection(part):
            continue
        if set(part) <= came_from_past and any(u >= past_count for u in part) and nx.is_isomorphic(
                shape, past_shape, node_match=lambda left, right: left['type'] == right['type']):
            qualifying.extend(part)
        else:
            given_off.extend(part)
    assert set(current) <= set(qualifying)
    return current, tuple(sorted(given_off)), tuple(sorted(qualifying))


def compare(config, tests, source):
    a, fresh, stop = grow(config)
    assert stop == source['stop']
    assert [len(state.places) for state in a] == [r[-1] for r in source['per_round']]
    law = config[-1]
    original_failures = parity_failures(a[-1]) if law == 'parity' else nae_failures(a, 0)
    series_at = {(s['t0'], tuple(s['P0'])): s for s in source['nopast_series']}
    comparisons = {}
    totals = Counter()

    def cached(label, tick, expected, bar=(), mask=None):
        descriptor = (label, tick, bar, mask)
        totals[label] += 1
        if descriptor not in comparisons:
            state, result = check_run(config, a, tick, expected, bar, mask)
            comparisons[descriptor] = state, {'type': label, 'after': tick, 'bar': bar, 'mask': mask, **result}
        return comparisons[descriptor][0]

    for test in tests:
        series = series_at[test['t0'], tuple(test['P0'])]
        if expected := test.get('X_barred'):
            cached('X barred', test['t_j'], expected, tuple(test['X']))
        for bar in test['bars']:
            if not isinstance(bar.get('B'), dict):
                continue
            tick = bar['t_bar']
            now = a[tick]
            count = len(now.places)
            first = len(a[test['t_j']].places)
            current, given_off, qualifying = tick_parts(a, series, test, bar)
            side_x = closure(now.parents, test['X'], first)
            assert len(side_x.intersection(current)) == bar['X_desc_in_barred_part']
            barred = tuple(u for u in current if u not in side_x)
            b = cached('B', tick, bar['B'], barred)
            expected = {int(t): n for t, n in bar['own_B_after_bar_by_round'].items()}
            assert own_birth_counts(b, first, test['X'], test['P_j'], count) == (expected, bar['joint_B_after_bar'])
            if isinstance(bar.get("B'"), dict):
                cached("B'", tick, bar["B'"], tuple(u for u in given_off if u not in side_x))
            if isinstance(bar.get('Ball'), dict):
                cached('Ball', tick, bar['Ball'], tuple(u for u in qualifying if u not in side_x))
            if isinstance(bar.get('M'), dict):
                cached('M', tick, bar['M'], mask=(tuple(sorted(side_x)), current, count))
    return {'configuration': config, 'tests': len(tests), 'original_failures': original_failures,
            'original_under_three_places': [u for u, places in enumerate(a[-1].places) if len(places) < 3],
            'comparison_references': totals, 'comparisons': [result for _, result in comparisons.values()]}


def main(limit):
    selected = defaultdict(list)
    for row in rows('run4'):
        run = key(row)
        if row.get('verdict_C_iii') == 'holds' or predicted_case(run) and 'X' in row:
            selected[run].append(row)
    if limit is not None:
        selected = dict(list(selected.items())[:limit])
    records = {key(row): row for name in GROWTH_FILES for row in rows(name) if key(row) in selected}
    return [compare(run, tests, records[run]) for run, tests in selected.items()]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int)
    print(json.dumps(main(parser.parse_args().limit), indent=2))
