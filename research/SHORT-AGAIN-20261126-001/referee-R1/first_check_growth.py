"""Regrow first-checkpoint cases without importing either producing program."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
from time import monotonic

from first_check_counts import OFFSHOOT, RATIONS, RETIRE, WAIT, fresh, last_round, rows


SEED = 20261126
OWN_A, OWN_B, LINK, SPENT = 1, 2, 4, 8
ROLE = {OWN_A: 'A', OWN_B: 'B', LINK: 'link', SPENT: 'spent'}
NAMED_STARTS = {
    'ring': ((4, 0, 5, 6, 7), (0, 1, 8, 9, 10), (1, 2, 11, 12, 13),
             (2, 3, 14, 15, 16), (3, 4, 17, 18, 19)),
    'copier': ((0, 1, 2), (0, 3, 4)),
    'source': ((0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14), (6, 7, 15, 16, 17),
               (2, 3, 4, 6, 18, 19, 20), (7, 8, 21, 22), (5, 8, 23, 24)),
}
CENSUS_SHARED = {1: (), 3: ((0, 1),), 6: ((0, 1), (0, 2)), 7: ((0, 1), (0, 2), (1, 2))}


def pattern(label):
    if label in NAMED_STARTS:
        return NAMED_STARTS[label], 0
    code, site = label.split('@')
    meeting, loose = code.split(':')
    knots = [[] for _ in loose]
    shared = CENSUS_SHARED[int(meeting[1:])]
    for d, holders in enumerate(shared):
        for holder in holders:
            knots[holder].append(d)
    d = len(shared)
    for knot, h in zip(knots, map(int, loose)):
        knot.extend(range(d, d + h))
        d += h
    return knots, int(site)


def census_starts():
    declared = []
    for meeting, shared in CENSUS_SHARED.items():
        n = max((max(pair) + 1 for pair in shared), default=1)
        degree = Counter(x for pair in shared for x in pair)
        symmetry = [p for p in permutations(range(n)) if {tuple(sorted(p[q] for q in pair)) for pair in shared} == set(shared)]
        for loose in product(range(4), repeat=n):
            if not any(loose) or any(degree[k] + loose[k] < 3 for k in range(n)):
                continue
            if min(tuple(loose[k] for k in p) for p in symmetry) != loose:
                continue
            keeping = [p for p in symmetry if tuple(loose[k] for k in p) == loose]
            for k in range(n):
                if min(p[k] for p in keeping) == k:
                    declared.append(f'g{meeting}:' + ''.join(map(str, loose)) + f'@{k}')
    return declared


class Names:
    """Equality of birth names by exact parent identities, without hashes."""

    def __init__(self):
        self.by_description = {}

    def get(self, description):
        if description not in self.by_description:
            self.by_description[description] = len(self.by_description)
        return self.by_description[description]


@dataclass
class Knot:
    name: int
    origin: int
    places: int
    usable: int
    meets: set


def make_start(a, b, d, join, names, change=None, alternate_a=None, alternate_b=None):
    """The two join constructions, plus a start, a link knot or a stub."""
    places = []
    origins = []
    next_distinction = 0
    side_sites = {}

    def add_knot(origin, distinctions=()):
        k = len(places)
        places.append(list(distinctions))
        origins.append(origin)
        return k

    def put(label, origin, alternate):
        nonlocal next_distinction
        knots, site = pattern(label)
        first = len(places)
        for p in knots:
            add_knot(origin, (next_distinction + x for x in p))
        next_distinction += 1 + max(x for p in knots for x in p)
        side_sites[origin] = first + (site if alternate is None else alternate)

    def connect(left, right):
        nonlocal next_distinction
        x = next_distinction
        if join == 'share':
            places[left].append(x)
            places[right].append(x)
            next_distinction += 1
        else:
            add_knot(SPENT, (x, x + 1, x + 2))
            places[left].extend((x, x + 3))
            places[right].extend((x + 1, x + 2, x + 4))
            next_distinction += 5

    def pad(k):
        nonlocal next_distinction
        while len(places[k]) < 3:
            places[k].append(next_distinction)
            next_distinction += 1

    for label, origin, alternate in ((a, OWN_A, alternate_a), (b, OWN_B, alternate_b)):
        if label not in ('stub', None):
            put(label, origin, alternate)
    if b is not None:
        if a == 'stub':
            side_sites[OWN_A] = add_knot(OWN_A)
        end = side_sites[OWN_A]
        link_knots = []
        for _ in range(d - 1):
            q = add_knot(LINK)
            connect(end, q)
            link_knots.append(q)
            end = q
        if b == 'stub':
            side_sites[OWN_B] = add_knot(OWN_B)
        connect(end, side_sites[OWN_B])
        for q in link_knots:
            pad(q)
        for label, origin in ((a, OWN_A), (b, OWN_B)):
            if label == 'stub':
                pad(side_sites[origin])

    held_by = defaultdict(list)
    for k, distinctions in enumerate(places):
        for x in distinctions:
            held_by[x].append(k)
    ordinals = Counter()
    state = []
    for k, (origin, distinctions) in enumerate(zip(origins, places)):
        neighbors = {u for x in distinctions for u in held_by[x] if u != k}
        assert all(1 <= len(held_by[x]) <= 2 for x in distinctions)
        h = sum(len(held_by[x]) == 1 for x in distinctions)
        label = names.get((ROLE[origin], ordinals[origin]))
        ordinals[origin] += 1
        state.append(Knot(label, origin, len(distinctions), h, neighbors))
    if change is not None:
        origin, member, delta, barred = change
        k = side_sites[origin] if member is None else [k for k, o in enumerate(origins) if o == origin][member]
        state[k].usable += delta
        state[k].places += 0 if barred else delta
        if state[k].usable < 0 or state[k].places < 3:
            raise ValueError('Change would leave an invalid start.')
    return state


def maximal_cliques(adj):
    def visit(chosen, available, examined):
        if not available and not examined:
            yield frozenset(chosen)
            return
        pivot = max(available | examined, key=lambda v: len(adj[v] & available))
        for v in sorted(available - adj[pivot]):
            yield from visit(chosen | {v}, available & adj[v], examined & adj[v])
            available.remove(v)
            examined.add(v)

    yield from visit(set(), set(adj), set())


def groups(state, live):
    met_by = defaultdict(set)
    for u in live:
        for v in state[u].meets:
            met_by[v].add(u)
    witnesses = {frozenset(members) for members in met_by.values() if len(members) > 1}
    joinable = defaultdict(set)
    witnessed_by = defaultdict(set)
    for met in witnesses:
        for member in met:
            joinable[member].update(met - {member})
            witnessed_by[member].add(met)
    higher = [tuple(sorted(q)) for q in maximal_cliques(joinable)
              if len(q) >= 3 and all(not q <= met for met in witnessed_by[min(q)])]
    covered = {p for q in higher for p in combinations(q, 2)}
    pairs = sorted((u, v) for u, neighbors in joinable.items() for v in neighbors if u < v and (u, v) not in covered)
    return sorted(higher) + pairs


def grant(ration, p, demand):
    if ration.startswith('CAP-'):
        return min(int(ration[4:]), max(3 - p, 1, demand))
    if ration == 'RECORDED-ONE-FEWER':
        return max(3 - p, 0, max(3 - p, 1, demand) - 1)
    return fresh(ration, p, demand)


def owner(origin):
    if origin == OWN_A:
        return 'own A'
    if origin == OWN_B:
        return 'own B'
    if origin & 3 == 3:
        return 'joint'
    return 'link side'


def take_round(state, ration, treatment, names):
    live = [u for u, knot in enumerate(state) if knot.usable]
    current = groups(state, live)
    owing = Counter(u for group in current for u in group)
    short = {u for u in live if owing[u] > state[u].usable}
    kept = [group for group in current if short.isdisjoint(group)]
    paid = Counter(u for group in kept for u in group)
    unpaid = {u: state[u].usable - paid[u] for u in live}
    own = {tag: {'members': 0, 'joined': 0, 'kept': 0, 'joined to the other': 0, 'births': []}
           for tag in (OWN_A, OWN_B)}
    cancelled = {OWN_A: [], OWN_B: []}
    for u in live:
        if state[u].origin in own:
            own[state[u].origin]['members'] += 1
    for g in current:
        for tag, other in ((OWN_A, OWN_B), (OWN_B, OWN_A)):
            if any(state[u].origin == tag for u in g):
                if not short.isdisjoint(g):
                    cancelled[tag].append(tuple(sorted(state[u].name for u in g)))
                crosses = any(state[u].origin != tag for u in g)
                own[tag]['joined'] += crosses
                own[tag]['kept'] += crosses and short.isdisjoint(g)
                own[tag]['joined to the other'] += any(state[u].origin & other for u in g)

    born = kept + [(u,) for u in live if u not in short or treatment == OFFSHOOT for _ in range(unpaid[u])]
    first_birth = len(state)
    occurrence = Counter()
    for q, parents in enumerate(born, first_birth):
        origin = 0
        for u in parents:
            origin |= state[u].origin
            state[u].meets.add(q)
        description = tuple(sorted(state[u].name for u in parents))
        label = names.get((description, occurrence[description]))
        occurrence[description] += 1
        state.append(Knot(label, origin, len(parents), 0, set(parents)))

    waiting = short if treatment == WAIT else set()
    for u in live:
        if u not in waiting:
            state[u].usable = 0
    next_owing = Counter(u for g in groups(state, waiting | set(range(first_birth, len(state)))) for u in g) if born else {}
    demand = Counter()
    joint = []
    any_a = []
    for q in range(first_birth, len(state)):
        child = state[q]
        p = child.places
        d = next_owing.get(q, 0)
        child.usable = grant(ration, p, d)
        child.places += child.usable
        birth = (child.name, child.usable, child.places)
        demand[(owner(child.origin), 'join' if p > 1 else 'offshoot', p, d)] += 1
        if child.origin in own:
            own[child.origin]['births'].append(birth)
        if child.origin & 3 == 3:
            joint.append(birth)
        if child.origin & OWN_A:
            any_a.append(birth)
    return {'knots': len(state), 'short': len(short), 'short_ids': sorted(short), 'birth_total': len(born),
            'own': own, 'cancelled': cancelled, 'joint': joint, 'any_A_ancestor': any_a, 'demand': demand}


def grow(state, ration, treatment, names, rounds, bound):
    result = []
    for _ in range(rounds):
        result.append(take_round(state, ration, treatment, names))
        if len(state) > bound:
            break
    return result


def first_difference(baseline, changed, field):
    return next((i for i, (a, b) in enumerate(zip(baseline, changed), 1) if field(a) != field(b)), None)


def own_births(row, origin=OWN_A):
    return row['own'][origin]['births']


def comparison(baseline, changed, origin=OWN_A):
    return {
        'rounds': min(len(baseline), len(changed)),
        'own': first_difference(baseline, changed, lambda r: set(own_births(r, origin))),
        'own_count': first_difference(baseline, changed, lambda r: len(own_births(r, origin))),
        'any_A_ancestor': first_difference(baseline, changed, lambda r: set(r['any_A_ancestor'])),
        'joint': first_difference(baseline, changed, lambda r: set(r['joint'])),
        'groups': first_difference(baseline, changed, lambda r: {g for g in r['cancelled'][origin]}),
    }


def reaches(row):
    a, b, d = row['A'], row['B'], row['d']
    ration, treatment = row['law']
    names = Names()
    baseline = grow(make_start(a, b, d, 'meeting', names), ration, treatment, names, 16, 3000)
    assert baseline[-1]['knots'] == row['knots']
    observed = {
        'short': [r['short'] for r in baseline],
        'kept': [r['own'][OWN_A]['kept'] for r in baseline],
        'own births': [len(own_births(r)) for r in baseline],
        'joint births': [len(r['joint']) for r in baseline],
    }
    for field, series in observed.items():
        assert series == row[field], (a, b, d, ration, treatment, field, series, row[field])
    if 'demand' in row:
        demand = sum((r['demand'] for r in baseline), Counter())
        assert demand == {tuple(k): n for k, n in row['demand']}
    alone = grow(make_start(a, None, 1, 'meeting', names), ration, treatment, names, 16, 3000)
    assert row['alone'] == {'rounds': len(alone), 'knots': alone[-1]['knots'], 'own births, last round': len(own_births(alone[-1]))}
    compares = {}
    for change, expected in row['changes'].items():
        if change in ('two', 'less'):
            descriptor = (OWN_B, None, 2 if change == 'two' else -1, False)
        else:
            is_link = change.startswith('L')
            descriptor = (LINK if is_link else OWN_B, int(change[1:]) - is_link, 1, False)
        altered = grow(make_start(a, b, d, 'meeting', names, descriptor), ration, treatment, names, 16, 3000)
        compared = comparison(baseline, altered)
        assert all(value == compared[key] for key, value in expected.items()), (a, b, d, ration, treatment, change, expected, compared)
        compares[change] = compared
    return {'case': (a, b, d, ration, treatment), 'baseline_rounds': len(baseline), 'changes': compares}


def mark_roll(row):
    a, b, d = row['A'], row['B'], row['d']
    ration, treatment = row['law']
    names = Names()
    state = make_start(a, b, d, 'meeting', names)
    head = grow(state, ration, treatment, names, 5, 3000)
    before_six = len(state)
    head += grow(state, ration, treatment, names, 1, 3000)
    assert len(state) == row['knots at round 6']
    marks = [q for q in range(before_six, len(state)) if state[q].origin != OWN_A]
    lengths = {q: 0 for q, k in enumerate(state) if k.origin == OWN_A}
    live = list(lengths)
    for q in live:
        for u in state[q].meets:
            if u not in lengths:
                lengths[u] = lengths[q] + 1
                live.append(u)

    def continue_growth(mark=None):
        fork = [Knot(k.name, k.origin, k.places, k.usable, set(k.meets)) for k in state]
        if mark is not None:
            fork[mark].usable += 1
            fork[mark].places += 1
        return head + grow(fork, ration, treatment, names, 10, 3000)

    baseline = continue_growth()
    assert len(baseline) == row['rounds']
    recount = []
    differences = []
    for mark in marks:
        grown = continue_growth(mark)
        compared = comparison(baseline, grown)
        differences.append(compared)
        recount.append([owner(state[mark].origin), lengths.get(mark), compared['own'], compared['rounds'],
                        sum(bool(y['short']) and not x['short'] for x, y in zip(baseline[6:], grown[6:]))])
    assert recount == row['marks'], ((a, b, d, ration, treatment), recount, row['marks'])
    return {'case': (a, b, d, ration, treatment), 'baseline_rounds': len(baseline), 'marks': recount,
            'own_counts_differ': sum(d['own_count'] is not None for d in differences),
            'any_A_ancestor_differs': sum(d['any_A_ancestor'] is not None for d in differences)}


def made_row(row, census):
    a, b = row['A'], row['B']
    d, join = row.get('steps', 1), row['join']
    ration, treatment = row['law'][:2]
    horizon, bound = (10, 1500) if census else (12, 3000)
    names = Names()

    def simulate(left, right, kd=d, mark=None):
        return grow(make_start(left, right, kd, join, names, mark), ration, treatment, names, horizon, bound)

    baseline = simulate(a, b)
    n = len(baseline)
    assert row['knots'] == baseline[-1]['knots']
    fields = ('rounds', 'short', 'joint') if census else ('rounds read', 'short members by round', 'joint descent, births by round')
    assert [row[k] for k in fields] == [n, [r['short'] for r in baseline], [len(r['joint']) for r in baseline]]
    by_read = {}
    for tag, other, mark_count, stub_pair in ((OWN_A, OWN_B, len(pattern(b)[0]), (a, 'stub')),
                                              (OWN_B, OWN_A, len(pattern(a)[0]), ('stub', b))):
        k = ROLE[tag]
        read = row['reads'][k]
        kept = [r['own'][tag]['kept'] for r in baseline]
        if census:
            assert read['last kept'] == last_round(kept)
        else:
            assert read['kept by round'] == kept
            for field in ('members', 'births', 'joined', 'joined to the other'):
                series = [r['own'][tag][field] for r in baseline]
                if field == 'births':
                    series = list(map(len, series))
                column = f'own {field} by round' if field in ('members', 'births') else f'{field} by round'
                assert read[column] == series, ((a, b, d, join, ration, treatment), k, column, read[column], series)
        stub = comparison(baseline, simulate(*stub_pair), tag)
        stub_key = 'stub' if census else 'own making differs from with a stub, first round'
        assert read[stub_key] == stub['own']
        if not census:
            assert read['rounds compared with the stub'] == stub['rounds']
        checks = []
        for i in range(mark_count):
            marked = simulate(a, b, mark=(other, i, 1, False))
            compared = comparison(baseline, marked, tag)
            expected = [compared['own'], compared['joint']]
            if census:
                assert read['marks'][i] == expected, ((a, b, d, join, ration, treatment), k, i, expected, read['marks'][i])
            else:
                observed = read['mark at a start knot of the other'][str(i)]
                assert observed['rounds compared'] == compared['rounds']
                assert [observed['own making first differs'], observed['joint descent first differs']] == expected
            checks.append(compared)
        by_read[k] = checks
    return {'case': (a, b, d, join, ration, treatment), 'baseline_rounds': n, 'marks': by_read}


def short_start_audit(selected):
    result = Counter(cases=len(selected))
    examples = []
    for row in selected:
        names = Names()
        state = make_start(row['A'], row['B'], row['d'], 'meeting', names)
        n_start = len(state)
        baseline = grow(state, 'ODD-FEWER', WAIT, names, 16, 3000)
        assert [r['short'] for r in baseline] == row['short']
        assert [r['own'][OWN_A]['kept'] for r in baseline] == row['kept']
        by_round = [set(r['short_ids']) for r in baseline]
        if any(q < n_start for group in by_round for q in group):
            result['cases_with_any_start_knot_short'] += 1
        if by_round[-1]:
            result['cases_with_short_in_last_round'] += 1
            waiting_since_two = set.intersection(*by_round[1:])
            first_births = set(range(n_start, baseline[0]['knots']))
            if waiting_since_two & first_births:
                result['cases_with_round_1_birth_short_in_all_rounds_2_through_16'] += 1
            if len(examples) < 2:
                examples.append({'case': [row['A'], row['B'], row['d']], 'start_knots': n_start,
                                 'knots_after_round_1': baseline[0]['knots'],
                                 'short_knot_indices_each_round': [sorted(ids) for ids in by_round]})
    return {'counts': dict(result), 'examples': examples}


def control(row):
    a, b, ration = row['A'], row['B'], row['ration']
    names = Names()

    def look(change=None):
        return grow(make_start(a, b, 3, 'meeting', names, change), ration, WAIT, names, 16, 3000)

    baseline = look()
    tested = {'source_or_other_knots': [comparison(baseline, look((OWN_B, j, 1, False))) for j in range(len(pattern(b)[0]))],
              'links': [comparison(baseline, look((LINK, j, 1, False))) for j in range(2)],
              'two_more': comparison(baseline, look((OWN_B, None, 2, False))),
              'one_fewer': comparison(baseline, look((OWN_B, None, -1, False)))}
    assert len(baseline) == row['rounds'] and baseline[-1]['knots'] == row['knots']
    assert sorted(v['own'] for v in tested['source_or_other_knots'] if v['own']) == row['B marks heard']
    assert len(tested['source_or_other_knots']) == row['of']
    assert [v['own'] for v in tested['links']] == row['link marks']
    assert tested['one_fewer']['own'] == row['less'] and tested['two_more']['own'] == row['two']
    return {'case': (a, b, 3, ration, WAIT), 'baseline_rounds': len(baseline), 'changes': tested}


def swapped():
    """The same two generators, with single changes to the join, site, ration or sign."""
    configs = [
        ('meeting', 'JOIN-FEWER', 'source', None),
        ('share', 'JOIN-FEWER', 'source', None),
        ('meeting', 'JOIN-FEWER', 'source', 5),
        ('meeting', 'JOIN-FEWER', 'stub', None),
        ('meeting', 'RECORDED-ONE-FEWER', 'source', None),
        ('meeting', 'CAP-5', 'source', None),
    ]
    result = []
    for join, ration, sender, site in configs:
        names = Names()

        def follow(change=None):
            state = make_start('source', sender, 3, join, names, change, alternate_b=site)
            return grow(state, ration, WAIT, names, 16, 3000)

        baseline = follow()
        if sender == 'stub':
            changes = [('L2+1', (LINK, 1, 1, False)), ('B+1', (OWN_B, None, 1, False))]
        else:
            changes = [('L2+1', (LINK, 1, 1, False)), ('B+1', (OWN_B, None, 1, False)),
                       ('B−1', (OWN_B, None, -1, False)), ('Bbar1', (OWN_B, None, -1, True))]
        counts = {}
        for label, change in changes:
            changed = follow(change)
            counts[label] = comparison(baseline, changed)
        result.append({'join': join, 'ration': ration, 'sender': sender, 'sender_site': site or 0,
                       'baseline_rounds': len(baseline), 'baseline_own_births': [len(own_births(r)) for r in baseline],
                       'comparisons': counts})
    return result


def ninth_meeting_step(bound, pilot=False):
    result = {}
    rations = ('JOIN-FEWER',) if pilot else ('JOIN-FEWER', 'ONE-FEWER')
    for ration in rations:
        names = Names()

        def follow(change=None):
            state = make_start('source', 'source', 9, 'meeting', names, change)
            return grow(state, ration, WAIT, names, 16, bound)

        baseline = follow()
        changes = {'B0+1': (OWN_B, 0, 1, False), 'B5+1': (OWN_B, 5, 1, False), 'L8+1': (LINK, 7, 1, False)}
        result[ration] = {}
        for label in ('B0+1',) if pilot else changes:
            change = changes[label]
            changed = follow(change)
            result[ration][label] = {**comparison(baseline, changed), 'knots_in_last_changed_round': changed[-1]['knots']}
    result['knot_bound'] = bound
    return result


def sample_by(rows_in, key, rng, size=1):
    by_key = defaultdict(list)
    for row in rows_in:
        by_key[key(row)].append(row)
    return [row for key in sorted(by_key) for row in rng.sample(by_key[key], min(len(by_key[key]), size))]


def make_plan():
    rng = random.Random(SEED)
    reach_rows = rows('reach_runs')
    far_rows = rows('far')
    marks = rows('made_mark')
    bench = [r for r in rows('made_bench') if 'reads' in r]
    census = rows('made_census')
    control_rows = rows('receivers')
    plan = {
        'reach': sample_by(reach_rows, lambda r: tuple(r['law']), rng),
        'far': sample_by(far_rows, lambda r: tuple(r['law']), rng),
        'made_marks': sample_by(marks, lambda r: (r['law'][0], r['law'][1], r['d']), rng),
        'bench': sample_by([r for r in bench if r['A'] == r['B'] == 'copier'], lambda r: r['join'], rng),
        'census': sample_by(census, lambda r: (r['join'], *r['law']), rng),
        'controls': control_rows,
        'odd_wait_short_starts': [r for r in reach_rows if r['law'] == ['ODD-FEWER', WAIT]],
    }
    plan['reach'].extend(r for r in reach_rows if r['d'] == 2 and r['A'] == r['B'] == 'g7:112@0' and
                         r['law'] in (['ONE-FEWER', WAIT], ['JOIN-FEWER', WAIT], ['THIRD-FEWER', WAIT]) and r not in plan['reach'])
    plan['bench'].extend(r for r in bench if r['A'] == r['B'] == 'source' and r['join'] == 'meeting' and r['law'][1] == WAIT
                         and (r['steps'] == 2 and r['law'][0] in ('ONE-FEWER', 'JOIN-FEWER', 'BUSY-FEWER')
                              or r['steps'] == 3 and r['law'][0] in ('ONE-FEWER', 'JOIN-FEWER')))
    plan['census'].extend(r for r in census if r['join'] == 'share' and r['law'] == ['BUSY-FEWER', WAIT] and
                           r['A'] in ('g7:112@0', 'g7:113@0') and r['B'] == 'g7:113@2' and r not in plan['census'])
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--part', choices=('reach', 'far', 'made_marks', 'bench', 'census', 'controls', 'odd_wait_short_starts',
                                           'swaps', 'ninth_meeting_step'))
    parser.add_argument('--ninth-bound', type=int, default=3000, help='Knot bound for the extra ninth meeting step only.')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    plan = make_plan()
    archive_roster = {r[k]: r[p] for r in rows('made_census') for k, p in (('i', 'A'), ('j', 'B'))}
    assert census_starts() == [archive_roster[i] for i in range(44)]
    runners = {
        'reach': reaches, 'far': reaches, 'made_marks': mark_roll,
        'bench': lambda r: made_row(r, census=False), 'census': lambda r: made_row(r, census=True), 'controls': control,
    }
    parts = [args.part] if args.part else [*plan, 'swaps', 'ninth_meeting_step']
    report = {'sample_seed': SEED, 'sited_census_starts': len(archive_roster), 'timings_seconds': {}}
    for part in parts:
        start = monotonic()
        if part in runners:
            chosen = plan[part][:1] if args.pilot else plan[part]
            report[part] = [runners[part](r) for r in chosen]
        elif part == 'odd_wait_short_starts':
            report[part] = short_start_audit(plan[part][:1] if args.pilot else plan[part])
        elif part == 'swaps':
            report[part] = swapped()
        elif part == 'ninth_meeting_step':
            report[part] = ninth_meeting_step(args.ninth_bound, args.pilot)
        report['timings_seconds'][part] = round(monotonic() - start, 3)
        print(f'Finished {part} in {report["timings_seconds"][part]:.3f} s', flush=True)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
