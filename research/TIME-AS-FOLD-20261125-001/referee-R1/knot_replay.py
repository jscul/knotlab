"""Rebuild selected growths and project their parity relations onto tested places."""

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from operator import xor
from functools import reduce

import networkx as nx

from knot_counts import HERE, REPO, GROWTH_FILES, key, rows


STARTS = json.loads((REPO / 'research/TIME-AS-FOLD-20261125-001A/starts.json').read_text())['named']


def parity_sum(values):
    return reduce(xor, values, 0)


def span(rows):
    basis = {}
    for row in rows:
        while row and row.bit_length() in basis:
            row ^= basis[row.bit_length()]
        if row:
            basis[row.bit_length()] = row
    return basis


def start_forms(places, distinctions):
    equations = span(parity_sum(1 << d for d in part) for part in places)
    forms = []
    parameters = 0
    for d in range(distinctions):
        if d + 1 not in equations:
            forms.append(1 << parameters)
            parameters += 1
        else:
            row = equations[d + 1] ^ (1 << d)
            forms.append(parity_sum(value for e, value in enumerate(forms) if (row >> e) & 1))
    return tuple(forms), parameters


def stars_for(name):
    if name in STARTS:
        return tuple(tuple(places) for places in STARTS[name])
    match = re.fullmatch(r'atlas (\d+) loose ([\d,]+)', name)
    atlas, loose = match.groups()
    loose = [int(h) for h in loose.split(',')]
    shared = sorted(tuple(sorted(pair)) for pair in nx.graph_atlas_g()[int(atlas)].edges)
    places = [[] for h in loose]
    for d, (left, right) in enumerate(shared):
        places[left].append(d)
        places[right].append(d)
    fresh = len(shared)
    for a, h in enumerate(loose):
        places[a].extend(range(fresh, fresh + h))
        fresh += h
    return tuple(map(tuple, places))


@dataclass(frozen=True)
class Growth:
    places: tuple
    parents: tuple
    born: tuple
    barred: frozenset
    forms: tuple
    parameters: int

    @classmethod
    def start(cls, places, parity):
        distinctions = 1 + max(d for part in places for d in part)
        forms, parameters = start_forms(places, distinctions) if parity else ((), 0)
        return cls(places, ((),) * len(places), (0,) * len(places), frozenset(), forms, parameters)


def holdings(places):
    held_by = defaultdict(list)
    for u, part in enumerate(places):
        for d in part:
            held_by[d].append(u)
    return held_by


def members(held_by, barred):
    loose = defaultdict(list)
    for d, owners in held_by.items():
        if len(owners) == 1 and d not in barred:
            loose[owners[0]].append(d)
    return {u: sorted(ds) for u, ds in loose.items()}


class Guard(Exception):
    pass


def group_structure(holds, loose, count, masked=None, guard=True):
    met = [set() for _ in range(count)]
    active = set(loose)
    incidence = 0
    for holders in holds.values():
        current = active.intersection(holders)
        if len(holders) < 2 or not current:
            continue
        incidence += len(current) * (len(holders) - 1)
        if guard and incidence > 2_000_000:
            raise Guard
        for u in holders:
            met[u].update(current - {u})
    joined = nx.Graph()
    joined.add_nodes_from(sorted(active))
    for neighbors in {frozenset(neighbors) for neighbors in met if len(neighbors) >= 2}:
        for u, v in combinations(sorted(neighbors), 2):
            if masked and ((u in masked[0] and v in masked[1]) or (u in masked[1] and v in masked[0])):
                continue
            joined.add_edge(u, v)
            if guard and joined.number_of_edges() > 20_000:
                raise Guard
    return met, joined


def birth_groups(met, joined):
    big = []
    for index, clique in enumerate(nx.find_cliques(joined), 1):
        if index > 200_000:
            raise Guard
        if len(clique) >= 3 and not any(set(clique) <= neighbors for neighbors in met):
            big.append(tuple(sorted(clique)))
    pairs_in_big = {pair for group in big for pair in combinations(group, 2)}
    pairs = {tuple(sorted(pair)) for pair in joined.edges} - pairs_in_big
    if len(big) + len(pairs) > 20_000:
        raise Guard
    return sorted(big) + sorted(pairs)


def ancestors(parents, u, distance, inclusive):
    level = {u}
    prior = set()
    for _ in range(distance):
        level = {p for a in level for p in parents[a]}
        prior.update(level)
    return prior if inclusive else level


def candidates(growth, held_by, parent_group, rule):
    if rule is None:
        return []
    parents = parent_group
    places = growth.places
    prohibited = {d for u in parents for d in places[u]}
    if len(parents) > 1:
        if rule not in ('MET', 'MET:join'):
            return []
        meetings = [{v for d in places[u] for v in held_by[d] if v != u} for u in parents]
        sources = set.intersection(*meetings)
    elif rule == 'MET:join':
        return []
    elif rule == 'Q':
        sources = set(parents)
        prohibited.clear()
    elif rule in ('MET', 'MET:offshoot'):
        u = parents[0]
        sources = {v for d in places[u] for v in held_by[d] if v != u}
    else:
        config = re.fullmatch(r'(STEPS|UP-TO)-(\d+)(?::(join|offshoot))?', rule)
        family, depth, parent_kind = config.groups()
        u = parents[0]
        n = len(growth.parents[u])
        if parent_kind == 'join' and n < 2 or parent_kind == 'offshoot' and n != 1:
            return []
        sources = ancestors(growth.parents, u, int(depth), family == 'UP-TO')
    return sorted({d for u in sources for d in places[u] if len(held_by[d]) >= 2 and d not in prohibited})


def closure(parents, roots, start):
    result = set(roots)
    for u in range(start, len(parents)):
        if result.intersection(parents[u]):
            result.add(u)
    return result


def expand(growth, config, t, mask=None):
    group, _, base, rule, choice, law = config
    held_by = holdings(growth.places)
    old_count = len(growth.places)
    current = members(held_by, growth.barred)
    met, joined = group_structure(held_by, current, old_count, mask)
    groups = birth_groups(met, joined)
    owing = Counter(u for parent_group in groups for u in parent_group)
    short = {u for u, ds in current.items() if owing[u] > len(ds)}
    raw_births = [(parents, 0) for parents in groups if not short.intersection(parents)]
    used = Counter(u for parents, _ in raw_births for u in parents)
    barred = set(growth.barred)
    for u, ds in sorted(current.items()):
        if u not in short or base.endswith('(OFFSHOOT)'):
            raw_births.extend(((u,), index) for index in range(len(ds) - used[u]))
        elif base.endswith('(RETIRE)'):
            barred.update(ds)
    if len(raw_births) > 20_000:
        raise Guard

    input_groups = []
    demand_places = list(growth.places)
    cursor = Counter()
    for parents, offshoot_number in raw_births:
        inputs = tuple(current[u][cursor[u]] for u in parents)
        cursor.update(parents)
        possible = candidates(growth, held_by, parents, rule)
        taken = ()
        if possible:
            if choice == 'NEWEST':
                selected = len(possible) - 1
            elif choice == 'BY-COUNT':
                selected = len(growth.places[parents[0]]) % len(possible)
            elif choice == 'IN-TURN':
                selected = offshoot_number % len(possible)
            else:
                assert choice == 'OLDEST'
                selected = 0
            taken = (possible[selected],)
        input_groups.append(inputs + taken)
        demand_places.append(inputs if group == 'dbt' else inputs + taken)

    demand_holders = holdings(demand_places)
    demand_roster = {u: True for u, ds in members(demand_holders, barred).items() if u < old_count}
    demand_roster.update({u: True for u in range(old_count, len(demand_places))})
    if mask:
        parents_now = growth.parents + tuple(parents for parents, _ in raw_births)
        mask = tuple(closure(parents_now, side, old_count) for side in mask)
    met, joined = group_structure(demand_holders, demand_roster, len(demand_places), mask)
    demand = Counter(u for group in birth_groups(met, joined) for u in group)

    forms = list(growth.forms)
    parameters = growth.parameters
    next_distinction = len(held_by)
    complete = []
    fresh_counts = []
    for u, (inputs, (parents, _)) in enumerate(zip(input_groups, raw_births), old_count):
        p = len(parents) if group == 'fbp' else len(inputs)
        fresh = max(3 - p, 1)
        if law == 'parity' and parity_sum(growth.forms[d] for d in inputs) == 0:
            fresh = 0
        elif not base.startswith('COPY-LAW'):
            fresh = min(max(fresh, demand[u]), 3)
        additions = tuple(range(next_distinction, next_distinction + fresh))
        if base.endswith('+FILLERS'):
            barred.update(additions[min(fresh, demand[u]):])
        next_distinction += fresh
        if next_distinction > 400_000:
            raise Guard
        complete.append(inputs + additions)
        fresh_counts.append(fresh)
        if law == 'parity' and fresh:
            free = [1 << param for param in range(parameters, parameters + fresh - 1)]
            parameters += fresh - 1
            forms.extend(free + [parity_sum([forms[d] for d in inputs] + free)])
    next_growth = Growth(growth.places + tuple(complete), growth.parents + tuple(p for p, _ in raw_births),
                         growth.born + (t,) * len(complete), frozenset(barred), tuple(forms), parameters)
    return next_growth, tuple(fresh_counts)


def grow(config, through=None, start=None, start_t=0, bar=(), mask_roots=None):
    group, name, _, rule, _, law = config
    if start is None:
        start = Growth.start(stars_for(name), law == 'parity')
    if bar:
        current = members(holdings(start.places), start.barred)
        barred = start.barred | {d for u in bar for d in current.get(u, [])}
        start = Growth(start.places, start.parents, start.born, barred, start.forms, start.parameters)
    growth = [start]
    fresh = []
    stop = None
    default_rounds = 2 * int(rule[6:]) + 4 if group == 'ladder' else 18
    knot_bound = 6000 if group == 'ladder' else 4000
    for t in range(start_t + 1, (default_rounds if through is None else through) + 1):
        old = growth[-1]
        mask = None
        if mask_roots:
            left, right, start_count = mask_roots
            mask = (closure(old.parents, left, start_count), closure(old.parents, right, start_count))
        try:
            added, new_fresh = expand(old, config, t, mask)
        except Guard:
            stop = 'guard'
            break
        growth.append(added)
        fresh.extend(new_fresh)
        if len(added.places) > knot_bound:
            stop = 'knots'
            break
    return growth, fresh, stop


def equations_on(whole, selected):
    """Eliminate every distinction outside selected before reading the induced equations."""
    selected_mask = parity_sum(1 << d for d in selected)
    outside_pivots = {}
    supported = []
    for part in whole:
        row = parity_sum(1 << d for d in part)
        while outside := row & ~selected_mask:
            high = outside.bit_length()
            if high not in outside_pivots:
                outside_pivots[high] = row
                break
            row ^= outside_pivots[high]
        else:
            supported.append(row)
    return tuple(span(supported).values())


def relation(whole, selected):
    equations = equations_on(whole, selected)
    reduced = [set(d for d in selected if (row >> d) & 1) for row in equations]
    # A linear combination omitting a place remains a constraint on forgetting it.
    # For two or more independent equations, at least one nonzero combination omits any specified place.
    obstructed = [d for d in selected if len(reduced) > 1 or reduced and d not in reduced[0]]
    out = {'places': list(selected), 'even_on': [sorted(row) for row in reduced],
           'allowed_count': 1 << (len(selected) - len(reduced)), 'K1': bool(reduced),
           'K2': not obstructed, 'K3': True, 'forgetting_still_constrained': obstructed}
    if len(selected) <= 6:
        projected = [sum(1 << i for i, d in enumerate(selected) if d in row) for row in reduced]
        out['allowed_words'] = [format(word, f'0{len(selected)}b')[::-1] for word in range(1 << len(selected))
                                if not any((word & row).bit_count() % 2 for row in projected)]
    return out


def parity_failures(state, after=0):
    return [u for u, places in enumerate(state.places) if u >= after
            and len(span(state.forms[d] for d in places)) != len(places) - 1]


def named_replays(limit, records):
    source_failures = json.loads((HERE / 'knot_counts.json').read_text())['run_a']['failure_rows']
    by_run = defaultdict(list)
    for failure in source_failures:
        by_run[tuple(failure['configuration'])].append(failure)
    if limit is not None:
        by_run = dict(sorted(by_run.items(), key=lambda entry: entry[0][0] != 'main')[:limit])
    found = []
    controls = []
    for config, expected in by_run.items():
        states, fresh, stop = grow(config)
        state = states[-1]
        source = records[config]
        assert stop == source['stop'] and len(states) == len(source['per_round']), config
        assert [len(s.places) for s in states] == [r[-1] for r in source['per_round']], config
        failed = parity_failures(state)
        assert failed == sorted(f['knot'] for f in expected), (config, failed)
        for failure in expected:
            u = failure['knot']
            made = state.born[u]
            assert made == failure['made'] and len(state.parents[u]) == failure['parents'], (config, u)
            assert len(state.places[u]) == failure['places'], (config, u)
            born = states[made]
            support = relation(born.places, born.places[u])
            assert support == relation(state.places, state.places[u])
            assert support['K1'] and not support['K2'] and support['K3']
            found.append({'configuration': config, 'knot': u, 'made': made, 'parents': list(state.parents[u]),
                          'fresh': fresh[u - len(states[0].places)], 'relation': support})
            if len(state.places[u]) <= 6 and not controls:
                parent = state.parents[u][0]
                passed = relation(born.places, born.places[parent])
                assert passed['K1'] and passed['K2'] and passed['K3']
                controls.append({'configuration': config, 'knot': parent, 'at_round': made, 'relation': passed})
    return {'failed_runs': len(by_run), 'failed_knots': found, 'nearest_passing_parent': controls}


def main(args):
    run_counts = json.loads((HERE / 'knot_counts.json').read_text())
    fails = {tuple(f['configuration']) for f in run_counts['run_a']['failure_rows']}
    records = {key(row): row for name in GROWTH_FILES for row in rows(name) if key(row) in fails}
    return named_replays(args.limit, records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int)
    print(json.dumps(main(parser.parse_args()), indent=2))
