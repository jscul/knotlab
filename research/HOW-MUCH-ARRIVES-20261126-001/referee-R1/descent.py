"""Replay ordinary marks and moves from lesson 8.1 and the frozen round definitions.

Sources: INTUITIONS.md 8.1, RING-IN-BALANCE definitions steps 1–7,
PARTS-MEET-AGAIN definitions 2.1, and the study note's three readings.
This implementation uses no growth, reading, or analysis modules from the studies.
"""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import gzip
from itertools import combinations, permutations, product
import json
from pathlib import Path


STUDY = Path(__file__).resolve().parent.parent
STARTS = {
    'two-touching': ((0, 1, 2), (0, 3, 4)),
    'chain3': ((0, 1, 2), (1, 3, 4), (3, 5, 6)),
}
READINGS = ('name', 'sig0', 'sig1')


def cliques(extend, remaining, excluded, neighbours):
    """Enumerate maximal sets in the pairwise joinability relation."""
    if not remaining and not excluded:
        yield frozenset(extend)
        return
    pivot = max(remaining | excluded, key=lambda u: len(remaining & neighbours[u]))
    for u in sorted(remaining - neighbours[pivot]):
        yield from cliques(extend | {u}, remaining & neighbours[u], excluded & neighbours[u], neighbours)
        remaining.remove(u)
        excluded.add(u)


def groups(holders, live):
    """A join group as in the frozen ordinary definition and its pair fallback."""
    met = {frozenset(held & live) for held in holders}
    met = {members for members in met if len(members) > 1}
    neighbours = {u: set() for u in live}
    pairs = {pair for members in met for pair in combinations(sorted(members), 2)}
    for u, v in pairs:
        neighbours[u].add(v)
        neighbours[v].add(u)
    large = [group for group in cliques(set(), set(live), set(), neighbours)
             if len(group) > 2 and not any(group <= members for members in met)]
    covered = {pair for group in large for pair in combinations(sorted(group), 2)}
    return sorted(tuple(sorted(group)) for group in large) + sorted(pairs - covered)


class Symbols(dict):
    def symbol(self, key):
        return self.setdefault(key, len(self))


@dataclass
class Knot:
    name: tuple
    sig0: tuple
    sig1: tuple
    origins: frozenset
    plain_index: int
    typed_index: int


@dataclass
class Frame:
    births: list
    holder_steps: dict


def holder_steps(holders, start):
    distance = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in holders[u]:
            if v not in distance:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def start_knots(start, change=None, at=None, repeat_meeting=None):
    knots = [list(places) for places in STARTS[start]]
    next_distinction = 1 + max(d for places in knots for d in places)
    if repeat_meeting is not None:
        a, b = repeat_meeting
        assert set(knots[a]) & set(knots[b])
        knots[a].append(next_distinction)
        knots[b].append(next_distinction)
        next_distinction += 1
    if change == 'mark':
        knots[at].append(next_distinction)
    if change == 'move':
        donor, receiver = at
        count = Counter(d for places in knots for d in places)
        distinction = next(d for d in reversed(knots[donor]) if count[d] == 1)
        knots[donor].remove(distinction)
        knots[receiver].append(distinction)
    return knots


def replay(start, n_rounds, symbols, change=None, at=None, reverse=False, repeat_meeting=None):
    """Use the holder relation and loose counts, with initial start labels fixed.

    Every input here is a distinction with one holder and is assigned once.
    It therefore links the birth to its supplying parent and to no other
    knot. Two distinctions shared by the same start knots count once for
    meetings and twice for places. The reverse control renumbers knots and
    reverses birth order.
    """
    knots = start_knots(start, change, at, repeat_meeting)
    seed_labels = list(range(len(knots)))
    if reverse:
        seed_labels.reverse()
    labels = {seed: u for u, seed in enumerate(seed_labels)}
    by_distinction = defaultdict(list)
    for seed, places in enumerate(knots):
        assert len(places) == len(set(places))
        for d in places:
            by_distinction[d].append(labels[seed])
    loose = Counter()
    holders = [set() for _ in seed_labels]
    for owners in by_distinction.values():
        assert 1 <= len(owners) <= 2
        if len(owners) == 1:
            loose[owners[0]] += 1
        else:
            a, b = owners
            holders[a].add(b)
            holders[b].add(a)
    all_knots = []
    for seed in seed_labels:
        places = len(knots[seed])
        signature = ('start', 0, 0, places)
        token = symbols.symbol(('start', seed))
        typed = symbols.symbol(('typed start', seed, places))
        all_knots.append(Knot((token, 0, places), signature, (), frozenset([seed]), token, typed))
    assert len(holder_steps(holders, 0)) == len(holders)
    frames = []
    for _ in range(n_rounds):
        join_groups = groups(holders, set(loose))
        owed = Counter(u for group in join_groups for u in group)
        assert all(owed[u] <= count for u, count in loose.items()), 'unexpected short knot'
        planned = [('join', parents) for parents in join_groups]
        planned.extend(('offshoot', (u,)) for u in sorted(loose) for _ in range(loose[u] - owed[u]))
        assert planned, 'unexpected closure'
        assert max(len(parents) for _, parents in planned) < sum(loose.values()), 'possible parity closing'
        if reverse:
            planned.reverse()
        used = Counter(u for _, parents in planned for u in parents)
        assert used == loose
        first = len(all_knots)
        newborns = range(first, first + len(planned))
        # Every old loose distinction is now spent. Read demand with all new knots live.
        for u, (_, parents) in zip(newborns, planned):
            holders.append(set(parents))
            for p in parents:
                holders[p].add(u)
        demand = Counter(u for group in groups(holders, set(newborns)) for u in group)
        seen = Counter()
        loose = {}
        for u, (kind, parents) in zip(newborns, planned):
            fresh = max(1, 3 - len(parents), demand[u])
            places = fresh + len(parents)
            loose[u] = fresh
            inputs = [all_knots[p] for p in parents]
            input_names = tuple(sorted(x.name[0] for x in inputs))
            key = (kind, input_names)
            ordinal = seen[key]
            seen[key] += 1
            token = symbols.symbol(('bench', key, ordinal))
            sig0 = (kind, len(parents), fresh, places)
            sig1 = sig0 + (tuple(sorted(x.sig0 for x in inputs)),)
            origins = frozenset.union(*(x.origins for x in inputs))
            plain = symbols.symbol(('unindexed', kind, tuple(sorted(x.plain_index for x in inputs))))
            typed = symbols.symbol(('typed', sig0, tuple(sorted(x.typed_index for x in inputs))))
            all_knots.append(Knot((token, fresh, places), sig0, sig1, origins, plain, typed))
        steps_to_births = {}
        for seed, root in labels.items():
            distance = holder_steps(holders, root)
            steps_to_births[seed] = [distance[u] for u in newborns]
        frames.append(Frame(all_knots[first:], steps_to_births))
    return frames


def unmatched(base, changed, reading):
    base_counts = Counter(getattr(knot, reading) for knot in base)
    changed_counts = Counter(getattr(knot, reading) for knot in changed)
    return [sum((changed_counts - base_counts).values()), sum((base_counts - changed_counts).values())]


def measure(base, changed, seeds, focus, round_number):
    original, altered = base.births, changed.births
    row = {'round': round_number, 'n': len(original), "n'": len(altered),
           'desc': sum(bool(knot.origins & seeds) for knot in altered)}
    row.update({reading: unmatched(original, altered, reading) for reading in READINGS})
    row['count_difference'] = abs(len(original) - len(altered))
    origin_counts = defaultdict(lambda: [[], []])
    for side, births in enumerate((original, altered)):
        for knot in births:
            origin_counts[tuple(sorted(knot.origins))][side].append(knot)
    # [base, changed, bench damage] in each exact set of start ancestors.
    row['start_ancestors'] = {','.join(map(str, origins)): [len(a), len(b), sum(unmatched(a, b, 'name'))]
                              for origins, (a, b) in sorted(origin_counts.items())}
    if focus is not None:
        shells = defaultdict(lambda: [[], []])
        for side, frame in enumerate((base, changed)):
            for knot, steps in zip(frame.births, frame.holder_steps[focus]):
                shells[steps][side].append(knot)
        # [base, changed, bench damage, sig0 damage, sig1 damage, unindexed damage, typed damage].
        row['shells'] = {str(steps): [len(a), len(b)] + [sum(unmatched(a, b, reading)) for reading in
                         (*READINGS, 'plain_index', 'typed_index')] for steps, (a, b) in sorted(shells.items())}
    return row


def key(record):
    at = record['at']
    return record['start'], record['change'], tuple(at) if isinstance(at, list) else at


def read_records(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as source:
        return [json.loads(line) for line in source]


def verdict(rows, reading):
    damage = [sum(row[reading]) for row in rows]
    counts = [row['n'] + row["n'"] for row in rows]
    half = len(rows) // 2
    if all(x == 0 for x in damage[half:]):
        return 'dies out'
    if all(n > 0 and 20 * x >= 19 * n for x, n in zip(damage[-4:], counts[-4:])):
        return 'takes over'
    if counts[-1] <= counts[half]:
        return 'bounded' if damage[-1] <= damage[half] else 'grows'
    if damage[-1] <= damage[half] and 2 * counts[-1] >= 3 * counts[half]:
        return 'weakens'
    return 'holds'


def plateau(values):
    start = next((idx + 2 for idx in reversed(range(len(values) - 1)) if values[idx] != values[-1]), 1)
    return [start, values[-1]]


def summarize_case(case):
    rows = case['rounds']
    case['plateaus [first round, damage]'] = {r: plateau([sum(row[r]) for row in rows]) for r in READINGS}
    case['first round of count-only tail'] = {}
    for reading in ('sig0', 'sig1'):
        count_only = [sum(row[reading]) == row['count_difference'] for row in rows]
        case['first round of count-only tail'][reading] = plateau(count_only)[0] if count_only[-1] else None
    if len(rows) >= 8:
        case['verdicts'] = {r: verdict(rows, r) for r in READINGS}


def start_knot_tests(knots):
    """Project whole-start states onto each knot's places under each knot law."""
    assert min(map(len, knots)) >= 3
    assert set(Counter(d for places in knots for d in places).values()) <= {1, 2}
    distinctions = sorted({d for places in knots for d in places})
    checks = {}
    for law in ('nae', 'parity'):
        def allows(row):
            return len(set(row)) == 2 if law == 'nae' else sum(row) % 2 == 0

        full = []
        for bits in product((0, 1), repeat=len(distinctions)):
            values = dict(zip(distinctions, bits))
            projected = [tuple(values[d] for d in places) for places in knots]
            if all(allows(row) for row in projected):
                full.append(projected)
        counts = []
        for i, places in enumerate(knots):
            rows = {projected[i] for projected in full}
            allowed_by_one_rule = {row for row in product((0, 1), repeat=len(places)) if allows(row)}
            assert rows == allowed_by_one_rule
            assert 0 < len(rows) < 2 ** len(places)
            assert all(len({row[:j] + row[j + 1:] for row in rows}) == 2 ** (len(places) - 1)
                       for j in range(len(places)))
            counts.append(len(rows))
        checks[law] = {'whole start allowed states': len(full), 'allowed states on each knot': counts}
    return checks


def repaired_moves(rounds, cases):
    """Give the donor a second shared distinction in both arms of each pair."""
    comparison = []
    for case in cases:
        start, at = case['start'], case['at']
        if case['change'] != 'move' or (start == 'chain3' and set(at) != {0, 2}):
            continue
        donor, recipient = at
        neighbour = recipient if start == 'two-touching' else 1
        meeting = (donor, neighbour)
        padded_base = start_knots(start, repeat_meeting=meeting)
        padded_changed = start_knots(start, 'move', at, meeting)
        symbols = Symbols()
        base = replay(start, rounds, symbols, repeat_meeting=meeting)
        changed = replay(start, rounds, symbols, 'move', at, repeat_meeting=meeting)
        rows = []
        for t, (a, b, original) in enumerate(zip(base, changed, case['rounds']), 1):
            row = measure(a, b, set(at), donor, t)
            fields = ('n', "n'", 'name', 'sig0', 'desc', 'start_ancestors')
            if t > 1:
                fields += ('sig1',)
            assert all(row[field] == original[field] for field in fields), (start, at, t)
            shell_fields = 5 if t > 1 else 4
            assert {s: v[:shell_fields] for s, v in row['shells'].items()} == {
                s: v[:shell_fields] for s, v in original['shells'].items()}, (start, at, t)
            rows.append(row)
        repaired = {
            'start': start, 'change': 'move', 'at': at,
            'repeated meeting': meeting,
            'start distinctions': {'base': padded_base, 'changed': padded_changed},
            'start knot tests': {'base': start_knot_tests(padded_base), 'changed': start_knot_tests(padded_changed)},
            'rounds': rows,
        }
        summarize_case(repaired)
        comparison.append(repaired)
    return comparison


def audit(rounds):
    original = defaultdict(list)
    for record in read_records(STUDY / 'runs.jsonl.gz'):
        if record.get('start') in STARTS and record.get('change') in ('mark', 'move'):
            original[key(record)].append(record)
    longer = {key(record): record for record in read_records(STUDY / 'longer.jsonl')}
    control = json.loads((STUDY / 'control.json').read_text())
    named_shells = {key(record): record for record in control['by name, shell by shell']}
    checks = Counter()
    cases = []
    for start in STARTS:
        symbols = Symbols()
        base = replay(start, rounds, symbols)
        sites = range(len(STARTS[start]))
        changes = [('mark', u) for u in sites] + [('move', pair) for pair in permutations(sites, 2)]
        for change, at in changes:
            case_key = (start, change, at)
            focus = at if change == 'mark' else at[0]
            seeds = {at} if change == 'mark' else set(at)
            altered = replay(start, rounds, symbols, change, at)
            relabelled = replay(start, rounds, symbols, change, at, reverse=True)
            rows = []
            for t, (a, b, r) in enumerate(zip(base, altered, relabelled), 1):
                row = measure(a, b, seeds, focus, t)
                reverse_row = measure(a, r, seeds, focus, t)
                assert row == reverse_row, (case_key, t, 'relabelled')
                checks['relabelled case rounds'] += 1
                rows.append(row)
            assert {record['knot law'] for record in original[case_key]} == {'nae', 'parity'}
            for record in original[case_key]:
                for row, expected in zip(rows, record['rows']):
                    assert all(row[k] == value for k, value in expected.items() if k != 'shells'), (case_key, row, expected)
                    if 'shells' in expected:
                        assert {s: fields[:2] + [fields[4]] for s, fields in row['shells'].items()} == expected['shells']
                    checks[f"raw {record['knot law']} case rounds"] += 1
                assert [row['n'] for row in rows[:16]] == record['base counts'][:rounds]
                if rounds >= 16:
                    assert {r: verdict(rows[:16], r) for r in READINGS} == record['verdicts']
            if expected := longer.get(case_key):
                assert [sum(row['sig1']) for row in rows] == expected['sig1 damage by round'][:rounds]
                assert [sum(row['name']) for row in rows] == expected['name damage by round'][:rounds]
                assert [row['n'] + row["n'"] for row in rows] == expected["n + n'"][:rounds]
                checks['extension case rounds'] += rounds
                if rounds == 32:
                    assert {r: verdict(rows, r) for r in READINGS} == expected['verdicts']
                    assert {s: fields[:2] + [fields[4]] for s, fields in rows[-1]['shells'].items()} == expected['last shells']
            if rounds == 32 and (expected := named_shells.get(case_key)):
                assert {s: fields[:3] for s, fields in rows[-1]['shells'].items()} == expected["shells by name [G, G', damage]"]
                checks['round 32 recorded name shell cases'] += 1
            case = {'start': start, 'change': change, 'at': at, 'rounds': rows}
            summarize_case(case)
            cases.append(case)

    # A symmetric mark on the opposite knot gives the same unlabelled structure.
    # Fixed start names report damage even for this paired reflection.
    symbols = Symbols()
    left = replay('two-touching', rounds, symbols, 'mark', 0)
    right = replay('two-touching', rounds, symbols, 'mark', 1)
    reflection = [{reading: sum(unmatched(a.births, b.births, reading)) for reading in READINGS}
                  for a, b in zip(left, right)]
    assert all(row['sig0'] == row['sig1'] == 0 and row['name'] > 0 for row in reflection)
    return {
        'rounds': rounds,
        'checks': dict(checks),
        'shell fields': ['base births', 'changed births', 'name damage', 'sig0 damage', 'sig1 damage',
                         'name damage without equal-sibling ordinal', 'structural descent damage including ancestors’ places'],
        'controls': {'opposite marks of two touching knots, fixed start names': reflection},
        'cases': cases,
        'moves with three or more places at every start knot': repaired_moves(rounds, cases),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, choices=range(1, 33), default=32)
    args = parser.parse_args()
    print(json.dumps(audit(args.rounds), ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
