"""Rebuild unchanged parity births and verify the pre-round shortage read."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import signal
import sys
from time import perf_counter, process_time


HERE = Path(__file__).resolve().parent
SEED = 2026112602
MEMORY = 3 * 1024**3
GUARD_MULT = 4
KNOT_BOUND = 1500
sys.path.insert(0, str(HERE.parent))
import shortage

eng = shortage.eng

# The eight-knot positive start in the first referee's witness.
CONTROL = [
    [10, 4, 5], [11, 6, 7], [2, 4, 5, 6, 7], [2, 0, 3, 8],
    [2, 1, 9], [0, 1, 3], [8, 12, 13], [9, 14, 15],
]


def mask(places):
    return sum(1 << distinction for distinction in places)


def reduce_row(pivots, row):
    """Eliminate by least distinction, independently of the engine's basis."""
    while row:
        pivot = row & -row
        if pivot not in pivots:
            break
        row ^= pivots[pivot]
    return row


def extend_basis(pivots, places):
    row = reduce_row(pivots, mask(places))
    if row:
        pivots[row & -row] = row


def is_implied(starting_pivots, fresh_rows, start_count, row):
    """Undo the old births from the latest fresh distinctions down to the start."""
    while row.bit_length() > start_count:
        fresh, birth_row = fresh_rows[row.bit_length() - 1 - start_count]
        if row & fresh != fresh:
            return False
        row ^= birth_row
    return reduce_row(starting_pivots, row) == 0


def projected_rank(places, retained):
    """Rank of the old row space supported entirely on the retained inputs."""
    all_rows, outside_rows = {}, {}
    for support in places:
        row = mask(support)
        for pivots, part in ((all_rows, row), (outside_rows, row & ~retained)):
            reduced = reduce_row(pivots, part)
            if reduced:
                pivots[reduced & -reduced] = reduced
    return len(all_rows) - len(outside_rows)


def meets(places, holders, u):
    return {v for d in places[u] for v in holders[d] if v != u}


def has_partner(state, member, roster):
    """Every joinable pair lies in at least one group of the demand roster."""
    return any((meets(state.places, state.holders, mediator) - {member}) & roster
               for mediator in meets(state.places, state.holders, member))


def direct_groups(state, roster):
    """Exhaust the subsets on small controls, without the engine's roster builder."""
    mediator_sets = [meets(state.places, state.holders, u) & roster
                     for u in range(state.n_knots)]
    pairs = {pair for pair in combinations(sorted(roster), 2)
             if any(set(pair) <= served for served in mediator_sets)}
    independent_maxima = []
    larger_maxima = []
    for size in range(len(roster), 2, -1):
        for group in combinations(sorted(roster), size):
            members = set(group)
            if any(members <= maximal for maximal in larger_maxima):
                continue
            if not all(pair in pairs for pair in combinations(group, 2)):
                continue
            larger_maxima.append(members)
            if all(not members <= served for served in mediator_sets):
                independent_maxima.append(group)
    covered = {pair for group in independent_maxima for pair in combinations(group, 2)}
    return sorted(independent_maxima) + sorted(pairs - covered)


def direct_roster(state):
    loose = {u: sum(len(state.holders[d]) == 1 and not state.barred[d] for d in places)
             for u, places in enumerate(state.places)}
    live = {u for u, holding in loose.items() if holding}
    groups = direct_groups(state, live)
    owed = Counter(u for group in groups for u in group)
    return groups, sorted(u for u in live if owed[u] > loose[u]), owed, loose


def joined_start(a, b):
    """Build the specified three meetings in order, preserving take precedence."""
    stars = [list(knot) for knot in shortage.bench.STARS[a]]
    left = shortage.bench.SITE[a]
    next_distinction = 1 + max(d for knot in stars for d in knot)
    if b != 'stub':
        right = len(stars) + shortage.bench.SITE[b]
        stars.extend([next_distinction + d for d in knot] for knot in shortage.bench.STARS[b])
        next_distinction = 1 + max(d for knot in stars for d in knot)
    for meeting in range(3):
        if meeting < 2 or b == 'stub':
            destination = len(stars)
            stars.append([])
        else:
            destination = right
        d = next_distinction
        stars.append([d, d + 1, d + 2])
        stars[left] += [d, d + 3]
        stars[destination] += [d + 1, d + 2, d + 4]
        next_distinction += 5
        left = destination
    return stars


def replay(stars, law, rounds, direct=False):
    state = eng.from_stars(stars)
    guard = eng.Guard(GUARD_MULT)
    parity = law.knot_law == 'parity'
    start_count = state.n_distinctions
    starting_pivots = {}
    fresh_rows = []
    for places in state.places:
        extend_basis(starting_pivots, places)

    result = []
    for round_ in range(1, rounds + 1):
        if direct:
            groups, short, owe, loose = direct_roster(state)
        rec = eng.play_round(state, law, guard)
        if direct:
            assert rec['groups'] == groups and rec['short'] == short
            assert rec['owe'] == owe and all(loose[u] == rec['h'][u] for u in rec['members'])
        made_short = [u for u in rec['short'] if state.made[u] > 0]
        births = rec['births']
        implied = []
        demand_members = {u for u, _, _ in rec['persisting']} | {b['id'] for b in births}
        if direct and births:
            demand = direct_groups(state, demand_members)
            assert rec['demand'].groups == demand
        new_fresh_rows = []
        for birth in births:
            inputs = mask(birth['inputs'])
            assert birth['implied'] == (parity and is_implied(starting_pivots, fresh_rows, start_count, inputs))
            if birth['implied']:
                assert birth['f'] == 0
                assert bool(birth['D']) == has_partner(state, birth['id'], demand_members)
                event = {k: birth[k] for k in ('id', 'parents', 'kind', 'inputs', 'D', 'f')}
                if birth['D']:
                    event['projected rank'] = projected_rank(state.places[:births[0]['id']], inputs)
                    assert event['projected rank'] >= 1
                implied.append(event)
            else:
                assert birth['f'] >= birth['D'] and birth['f'] > 0
                fresh = mask(birth['fresh'])
                new_fresh_rows.extend([(fresh, fresh | inputs)] * birth['f'])
        fresh_rows.extend(new_fresh_rows)
        assert len(fresh_rows) == state.n_distinctions - start_count
        row = {'round': round_, 'births': len(births), 'implied': implied, 'made short': made_short}
        if direct:
            row.update({'start short': [u for u in rec['short'] if state.made[u] == 0],
                        'live groups': rec['groups'], 'live holdings and owing': {
                            u: [rec['h'][u], rec['owe'].get(u, 0)] for u in rec['members']},
                        'demand groups': rec['demand'].groups if births else []})
        result.append(row)
    return result, state


def archive():
    with gzip.open(HERE.parent / 'parity_runs.jsonl.gz', 'rt') as stream:
        rows = [row for row in map(json.loads, stream) if 'law' in row]
    assert len({(row['A'], row['B'], *row['law']) for row in rows}) == len(rows) == 3221
    assert all(row['knot law'] == 'parity' for row in rows)
    return rows


def seeded_cases(rows):
    """Draw one record per nonempty law, sender and ending stratum."""
    groups = defaultdict(list)
    for row in rows:
        groups[(*row['law'], row['B'], row['ended'])].append(row)
    randomizer = random.Random(SEED)
    return [(randomizer.choice(groups[stratum]), len(groups[stratum]))
            for stratum in sorted(groups, key=repr)]


def replay_row(row, prefix=None):
    a, b = row['A'], row['B']
    ration, take, choice = row['law']
    law = eng.Law(ration, 'CANCEL-WAIT', take, 'parity', choice)
    stars = joined_start(a, b)
    assert stars == shortage.bench.build(a, b, 3, None, 'meeting')[0]
    requested = row['rounds'] if prefix is None else min(row['rounds'], prefix)
    observed, state = replay(stars, law, requested)
    assert [len(r['made short']) for r in observed] == row['made short'][:requested]
    terminal = None
    if requested == row['rounds']:
        assert (state.n_knots > KNOT_BOUND) == (row['ended'] == 'knots')
        terminal = {'direct roster read': False, 'made short': []}
        # With no made shortage in the previous live roster, every older made knot spent.
        # With no owed implied birth, dropping the zero-funded births deletes only
        # isolated demand members. The other newborns can pay the unchanged demand.
        if observed and (observed[-1]['made short'] or any(e['D'] for e in observed[-1]['implied'])):
            roster = eng.build_roster(state, eng.live_members(state), 'terminal', eng.Guard(1000))
            owing = Counter(u for group in roster.groups for u in group)
            terminal = {'direct roster read': True, 'made short': [u for u in roster.members
                        if state.made[u] and owing[u] > roster.h[u]]}
    return {**{k: row[k] for k in ('A', 'B', 'law', 'rounds', 'ended')},
            'round reads': observed, 'last knot count': state.n_knots, 'terminal roster': terminal}


def controls():
    result = {}
    for knot_law, take in [('parity', 'MET'), ('nae', 'MET'), ('parity', None)]:
        law = eng.Law('ORD', 'CANCEL-WAIT', take, knot_law, 'OLDEST' if take else None)
        rounds, _ = replay(CONTROL, law, 2, direct=True)
        original = shortage.ring_line.Growth(CONTROL, ['control'] * len(CONTROL), law)
        original.run(1, KNOT_BOUND)
        cut_read = shortage.made_short(original)
        original.run(2, KNOT_BOUND)
        full_read = shortage.made_short(original)
        assert full_read == [len(row['made short']) for row in rounds]
        result[f'{knot_law}/{take or "no take"}'] = {
            'round reads': rounds, 'published reader at one round': cut_read,
            'published reader at two rounds': full_read}
    parity = result['parity/MET']['round reads']
    assert parity[0]['implied'] == [{'id': 8, 'parents': (0, 1), 'kind': 'join',
                                     'inputs': [10, 11, 2], 'D': 1, 'f': 0, 'projected rank': 1}]
    assert parity[1]['made short'] == [9, 10, 11, 12]
    assert all(parity[1]['live holdings and owing'][u] == [1, 3] for u in range(9, 13))
    assert all(not row['implied'] and not row['made short']
               for key, control in result.items() if key != 'parity/MET' for row in control['round reads'])
    return result


def counts(rows):
    totals = defaultdict(Counter)
    for row in rows:
        take = '/'.join(field for field in row['law'] if field)
        reads = row['round reads']
        implied = [event for r in reads for event in r['implied']]
        totals[take].update({'records': 1, 'rounds': len(reads),
                             'births': sum(r['births'] for r in reads),
                             'implied': len(implied), 'implied with demand': sum(e['D'] > 0 for e in implied),
                             'owed, projected rank one': sum(e.get('projected rank') == 1 for e in implied),
                             'owed, projected rank greater than one': sum(e.get('projected rank', 0) > 1 for e in implied),
                             'made short': sum(len(r['made short']) for r in reads)})
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('control', 'pilot', 'prefix', 'sample', 'complete'))
    parser.add_argument('--rounds', type=int, default=2)
    parser.add_argument('--skip', type=int, default=0)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--cpu-seconds', type=int)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.skip < 0 or args.limit is not None and args.limit <= 0:
        parser.error('--skip must be nonnegative and --limit positive')
    if args.mode != 'complete' and (args.skip or args.limit is not None):
        parser.error('--skip and --limit apply to complete mode')
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
    started, cpu_started = perf_counter(), process_time()
    result = {'mode': args.mode, 'memory limit bytes': MEMORY, 'guard multiplier': GUARD_MULT}
    if args.cpu_seconds is not None:
        resource.setrlimit(resource.RLIMIT_CPU, (args.cpu_seconds, args.cpu_seconds + 5))
        result['cpu seconds limit'] = args.cpu_seconds

        def budget_reached(_signal, _frame):
            raise TimeoutError('CPU limit reached')

        signal.signal(signal.SIGXCPU, budget_reached)

    def checkpoint():
        result['seconds'] = round(perf_counter() - started, 4)
        result['cpu seconds'] = round(process_time() - cpu_started, 4)
        result['peak resident KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if args.output:
            temporary = args.output.with_name(args.output.stem + '_writing.json')
            temporary.write_text(json.dumps(result, separators=(',', ':')) + '\n')
            temporary.replace(args.output)

    if args.mode == 'control':
        result['controls'] = controls()
    else:
        shortage.receivers.register()
        source = archive()
        result['archive records'] = len(source)
        if args.mode == 'pilot':
            # Spread the timed feasibility run across take and stopping settings.
            sample = seeded_cases(source)
            chosen = {}
            for row, weight in sample:
                chosen.setdefault((*row['law'], row['ended']), (row, weight))
            source = list(chosen.values())
        elif args.mode == 'sample':
            source = seeded_cases(source)
            result['sampling seed'] = SEED
            result['sampling unit'] = 'one uniformly drawn record per nonempty take, sender and ending stratum'
        else:
            source = [(row, None) for row in source]
            if args.mode == 'complete':
                random.Random(SEED).shuffle(source)
                result['order seed'] = SEED
                end = len(source) if args.limit is None else min(len(source), args.skip + args.limit)
                source = source[args.skip:end]
                result['requested range'] = [args.skip, end]
        rows = []
        try:
            for row, stratum_size in source:
                start = perf_counter()
                rebuilt = replay_row(row, args.rounds if args.mode == 'prefix' else None)
                if stratum_size is not None:
                    rebuilt['stratum size'] = stratum_size
                rebuilt['seconds'] = round(perf_counter() - start, 5)
                rows.append(rebuilt)
                if args.mode == 'complete' and args.output and len(rows) % 64 == 0:
                    result.update({'counts by law': counts(rows), 'records': rows, 'status': 'in progress'})
                    checkpoint()
        except TimeoutError:
            result['status'] = 'CPU limit reached'
        else:
            result['status'] = 'completed'
        result.update({'counts by law': counts(rows), 'records': rows})
    checkpoint()
    if args.output:
        print(args.output, result['seconds'], result['peak resident KiB'])
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    main()
