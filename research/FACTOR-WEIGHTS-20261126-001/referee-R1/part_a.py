"""Rebuild the countings by exhaustive stage populations and exact rank tests."""

import argparse
import json
import random
import resource
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import prod
from pathlib import Path
from time import perf_counter


CENSUS = Path(__file__).resolve().parents[2] / 'FORBID-EDITS-20261126-001' / 'starts.json'
SEED, SAMPLE, CAP, ROUNDS = 20261129, 300, 14, 2
ARMS = ('ordinary', 'one_fewer', 'arity_floor')
WAITING_ARMS = (('parity', 'CAP-3'), ('nae', 'CAP-3'), ('nae', 'REC-ONE-FEWER'))


def start_knots(row):
    count, shared, loose = row
    knots = [[] for _ in range(count)]
    name = 0
    for left, right, multiplicity in shared:
        names = range(name, name + multiplicity)
        knots[left].extend(names)
        knots[right].extend(names)
        name += multiplicity
    for knot, size in zip(knots, loose, strict=True):
        knot.extend(range(name, name + size))
        name += size
    return tuple(map(tuple, knots))


def holdings(knots):
    holders = defaultdict(list)
    for knot, places in enumerate(knots):
        for place in places:
            holders[place].append(knot)
    return holders


def loose_roster(holders):
    loose = defaultdict(list)
    for place, knots in sorted(holders.items()):
        if len(knots) == 1:
            loose[knots[0]].append(place)
    return loose


def maximal_sets(joinable, chosen, candidates, excluded):
    if not candidates and not excluded:
        yield chosen
        return
    pivot = max(candidates | excluded, key=lambda i: len(joinable[i] & candidates))
    for member in candidates - joinable[pivot]:
        yield from maximal_sets(
            joinable, chosen | {member}, candidates & joinable[member], excluded & joinable[member]
        )
        candidates.remove(member)
        excluded.add(member)


def groups(holders, members):
    met = defaultdict(set)
    for owners in holders.values():
        for member in owners:
            if member in members:
                for other in owners:
                    if other != member:
                        met[other].add(member)
    met_sets = {frozenset(group) for group in met.values() if len(group) >= 2}
    pairs = {pair for group in met_sets for pair in combinations(sorted(group), 2)}
    joinable = {member: set() for member in members}
    for left, right in pairs:
        joinable[left].add(right)
        joinable[right].add(left)
    big = sorted(
        tuple(sorted(chosen))
        for chosen in maximal_sets(joinable, set(), set(members), set())
        if len(chosen) >= 3 and not any(chosen <= group for group in met_sets)
    )
    covered = {pair for chosen in big for pair in combinations(chosen, 2)}
    return big + sorted(pairs - covered)


def bits(places, index):
    return sum(1 << index[d] for d in places)


def allows(law, state, mask):
    values = state & mask
    return values.bit_count() % 2 == 0 if law == 'parity' else values != 0 and values != mask


@lru_cache(maxsize=32)
def population(knots, law):
    names = tuple(sorted(holdings(knots)))
    index = {name: position for position, name in enumerate(names)}
    states = range(1 << len(names))
    for places in knots:
        mask = bits(places, index)
        states = [state for state in states if allows(law, state, mask)]
    return names, states


def grow_round(knots, law, arm):
    holders = holdings(knots)
    loose = loose_roster(holders)
    if not loose:
        return (), (), 'closed'
    waiting = arm not in ARMS
    proposals = groups(holders, loose)
    demand = Counter(parent for group in proposals for parent in group)
    short = {knot for knot, places in loose.items() if demand[knot] > len(places)}
    if short and not waiting:
        return (), (), 'stalled'
    parents = [group for group in proposals if not short.intersection(group)]
    used = Counter(parent for group in parents for parent in group)
    for knot in sorted(set(loose) - short):
        parents.extend([(knot,)] * (len(loose[knot]) - used[knot]))
    if not parents:
        return (), tuple(sorted(short)), 'jammed'
    payments = {knot: iter(places) for knot, places in loose.items()}
    taken = tuple(tuple(sorted(next(payments[parent]) for parent in group)) for group in parents)
    newborn = set(range(len(knots), len(knots) + len(taken)))
    after_payment = holdings(knots + taken)
    demand = Counter(knot for group in groups(after_payment, newborn | short) for knot in group)
    names, old_states = population(knots, law)
    index = {name: position for position, name in enumerate(names)}
    next_name = max(names) + 1
    births = []
    for knot, inputs in zip(sorted(newborn), taken, strict=True):
        mask = bits(inputs, index)
        implied = (law == 'parity' or not waiting) and all(
            allows(law, state, mask) for state in old_states
        )
        floor = max(0, 3 - len(inputs))
        if waiting:
            ordinary = max(demand[knot], floor, 1)
            if implied:
                fresh = 0
            elif arm == 'CAP-3':
                fresh = min(ordinary, 3)
            else:
                fresh = max(floor, ordinary - 1)
            advance = fresh
        else:
            ordinary = demand[knot] if implied else max(demand[knot], floor, 1)
            fresh = ordinary
            if arm == 'one_fewer':
                fresh = min(ordinary, max(floor, ordinary - 1))
            elif arm == 'arity_floor':
                fresh = min(ordinary, floor)
            advance = ordinary
        births.append((inputs, tuple(range(next_name, next_name + fresh))))
        next_name += advance
    return tuple(births), tuple(sorted(short)), 'funded'


def grow(start, law, arm):
    stages, rounds, waiting = [start], [], []
    for _ in range(ROUNDS):
        births, short, status = grow_round(stages[-1], law, arm)
        if not births:
            return stages, rounds, waiting, status
        stages.append(stages[-1] + tuple(inputs + fresh for inputs, fresh in births))
        rounds.append(births)
        waiting.append(short)
        if len(holdings(stages[-1])) > CAP:
            return stages, rounds, waiting, 'over cap'
    return stages, rounds, waiting, 'round cap'


def exact_countings(stages, rounds, law):
    populations = [population(stage, law) for stage in stages]
    names, final_states = populations[-1]
    start_count = len(populations[0][1])
    projected = []
    factor_checks, zero_fresh = 0, 0
    for (old_names, old_states), (new_names, new_states), births in zip(
        populations[:-1], populations[1:], rounds, strict=True
    ):
        assert new_names[:len(old_names)] == old_names
        old_mask = (1 << len(old_names)) - 1
        completed = Counter(state & old_mask for state in new_states)
        projected.append((completed, old_mask))
        fresh_names = [d for _, fresh in births for d in fresh]
        assert sorted(fresh_names) == list(new_names[len(old_names):])
        old_index = {name: position for position, name in enumerate(old_names)}
        private = [(bits(inputs, old_index), len(fresh)) for inputs, fresh in births]
        zero_fresh += sum(fresh == 0 for _, fresh in private)
        for state in old_states:
            factors = []
            for mask, fresh in private:
                if fresh == 0:
                    factors.append(int(allows(law, state, mask)))
                elif law == 'parity':
                    factors.append(1 << (fresh - 1))
                else:
                    assert mask
                    factors.append((1 << fresh) - ((state & mask) in (0, mask)))
            assert completed[state] == prod(factors)
            factor_checks += 1
    stage_weights = [0] * (1 << len(names))
    one_stage_weights = stage_weights.copy()
    initial_mask = projected[0][1]
    total_completions = Counter(state & initial_mask for state in final_states)
    for state in final_states:
        stage_weights[state] = prod(completions[state & mask] for completions, mask in projected)
        one_stage_weights[state] = total_completions[state & initial_mask]
    # Denominators omit only constants common to the entire weighting.
    retained = sum(Fraction(count, denominator) for denominator, count in
                   Counter(stage_weights[state] for state in final_states).items()) / start_count
    return names, final_states, stage_weights, one_stage_weights, retained, factor_checks, zero_fresh


@lru_cache(maxsize=CAP)
def zero_value_masks(width):
    all_states = (1 << (1 << width)) - 1
    return tuple(
        (all_states // ((1 << (2 << position)) - 1)) * ((1 << (1 << position)) - 1)
        for position in range(width)
    )


def canonical_knots(names, states):
    """Enumerate every minimally constrained projection of three or more distinctions."""
    if not states:
        return ()
    width = len(names)
    byte_support = bytearray(((1 << width) + 7) // 8)
    for state in states:
        byte_support[state // 8] |= 1 << (state % 8)
    full = bytearray(1 << width)
    zeros = zero_value_masks(width)

    def project(places, allowed, drop_below):
        full[places] = allowed.bit_count() == 1 << places.bit_count()
        for j in range(drop_below):
            # Project by taking either value of j and storing that state with j = 0.
            smaller = (allowed | (allowed >> (1 << j))) & zeros[j]
            project(places ^ (1 << j), smaller, j)

    project((1 << width) - 1, int.from_bytes(byte_support, 'little'), width)
    result = []
    for subset, complete in enumerate(full):
        if complete or subset.bit_count() < 3:
            continue
        places = tuple(j for j in range(width) if subset & (1 << j))
        if all(full[subset ^ (1 << j)] for j in places):
            result.append(tuple(names[j] for j in places))
    return tuple(result)


def rank_tests(scopes, names, states, start_weight, one_stage):
    held = {pair for places in scopes for pair in combinations(sorted(places), 2)}
    other_assignments = support_tables = pairs = 0
    failures = [0, 0, 0]
    witnesses = {}
    full_mask = (1 << len(names)) - 1
    for (i, left), (j, right) in combinations(enumerate(names), 2):
        if (left, right) in held:
            continue
        pairs += 1
        other_assignments += 1 << (len(names) - 2)
        first, second = 1 << i, 1 << j
        other_mask = full_mask ^ first ^ second
        occupied = {state & other_mask for state in states}
        support_tables += len(occupied)
        for rest in occupied:
            i00, i01, i10, i11 = rest, rest | second, rest | first, rest | first | second
            d00, d01, d10, d11 = (start_weight[i00], start_weight[i01], start_weight[i10], start_weight[i11])
            diagonal, off_diagonal = d00 * d11, d01 * d10
            s00, s01, s10, s11 = (one_stage[i00], one_stage[i01], one_stage[i10], one_stage[i11])
            violations = (bool(diagonal) != bool(off_diagonal), diagonal != off_diagonal, s00 * s11 != s01 * s10)
            if any(violations):
                for k, violation in enumerate(violations):
                    if not violation:
                        continue
                    failures[k] += 1
                    if k in witnesses:
                        continue
                    witnesses[k] = {
                        'pair': [left, right],
                        'other values': {name: (rest >> k) & 1 for k, name in enumerate(names) if k not in (i, j)},
                        'whole-stage denominators in 00, 01, 10, 11 order': [s00, s01, s10, s11],
                        'rounds-as-stages denominators in the same order': [d00, d01, d10, d11],
                    }
    return pairs, other_assignments, support_tables, failures, witnesses


def run(prefix, use_canonical_knots=False):
    before = perf_counter()
    census = json.loads(CENSUS.read_text())
    picks = random.Random(SEED).sample(range(len(census)), SAMPLE)[:prefix]
    rows = {}
    for law, arm in [(law, arm) for law in ('parity', 'nae') for arm in ARMS] + list(WAITING_ARMS):
        started = perf_counter()
        tallies, timings = Counter(), Counter()
        control_failures, counting_failures, first_loss = [], [], None
        for index in picks:
            phase = perf_counter()
            stages, rounds, waiting, status = grow(start_knots(census[index]), law, arm)
            timings['growth'] += perf_counter() - phase
            if status == 'over cap' or not rounds:
                tallies['over cap' if status == 'over cap' else f'no round: {status}'] += 1
                continue
            tallies['growth histories'] += 1
            tallies['one round' if len(rounds) == 1 else 'two rounds'] += 1
            tallies['histories with a waiting member'] += any(waiting)
            phase = perf_counter()
            names, states, start_w, one_w, retained, checked, zero_fresh = exact_countings(stages, rounds, law)
            timings['weightings'] += perf_counter() - phase
            tallies['histories with zero-fresh rules'] += zero_fresh > 0
            tallies['histories losing weight'] += retained < 1
            tallies['histories with empty support'] += not states
            tallies['old states checked against product of private completions'] += checked
            if retained < 1 and first_loss is None:
                first_loss = {'census index': index, 'start rules': stages[0], 'births': rounds,
                              'waiting members': waiting, 'retained weight': str(retained)}
            tested_scopes = stages[-1]
            if use_canonical_knots:
                phase = perf_counter()
                tested_scopes = canonical_knots(names, states)
                timings['canonical knot check'] += perf_counter() - phase
                tallies['subsets of named distinctions classified'] += 1 << len(names)
                tallies['canonical knots across histories'] += len(tested_scopes)
            phase = perf_counter()
            pairs, total, tested, failed, witnesses = rank_tests(tested_scopes, names, states, start_w, one_w)
            timings['rank tests'] += perf_counter() - phase
            tallies['pairs'] += pairs
            tallies['all tables per weighting'] += total
            tallies['tables with at least one allowed state per weighting'] += tested
            tallies['all-zero tables per weighting'] += total - tested
            for label, count in zip(('finish', 'start', 'one stage'), failed, strict=True):
                tallies[f'{label} failures'] += count
                tallies[f'{label} histories with failures'] += count > 0
            if 2 in witnesses:
                control_failures.append({'census index': index, 'start rules': stages[0], 'births': rounds,
                                         'failures': failed[2], 'first table': witnesses[2]})
            if failed[0] or failed[1]:
                counting_failures.append({'census index': index, 'start rules': stages[0], 'births': rounds,
                                          'finish failures': failed[0], 'start failures': failed[1],
                                          'first table by weighting': {k: w for k, w in witnesses.items() if k != 2},
                                          'tested knots': tested_scopes})
        rows[f'{law} / {arm}'] = {'counts': dict(tallies), 'phase seconds': dict(timings),
                                'elapsed seconds': perf_counter() - started,
                                'control failures': control_failures, 'first loss': first_loss,
                                'counting failures': counting_failures}
    return {'census length': len(census), 'seed': SEED, 'census indices': picks, 'round cap': ROUNDS,
            'distinction cap': CAP, 'pair classification': 'canonical knots' if use_canonical_knots else 'listed rules',
            'rows': rows, 'elapsed seconds': perf_counter() - before,
            'peak resident KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=int, default=SAMPLE, choices=range(1, SAMPLE + 1), metavar='COUNT')
    parser.add_argument('--canonical-knots', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.prefix, args.canonical_knots), indent=2))
