"""Rebuild recorded starts and parity growth without the study's engine or readers."""

from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, islice, permutations, product
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
LAYERS_REFEREE = RESEARCH / 'LAYERS-20261126-001' / 'referee-R1'
ARMS = ('ordinary', 'one_fewer', 'arity_floor')


def names_of(word):
    while word:
        least = word & -word
        yield least.bit_length() - 1
        word ^= least


def row_mask(row):
    return sum(1 << name for name in row)


def span(words):
    pivots = {}
    for word in words:
        while word:
            lead = word.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = word
                break
            word ^= pivots[lead]
    return pivots


def member(word, pivots):
    while word:
        previous = pivots.get(word.bit_length() - 1)
        if previous is None:
            return False
        word ^= previous
    return True


def members(basis):
    words = [0]
    for word in basis:
        words.extend(word ^ prior for prior in tuple(words))
    return words


def nullspace(conditions, columns):
    """Kernel basis given homogeneous equations and an explicit list of distinction names."""
    pivots = span(conditions)
    order = sorted(pivots)
    for free in columns:
        if free not in pivots:
            word = 1 << free
            for lead in order:
                if (word & pivots[lead]).bit_count() % 2:
                    word |= 1 << lead
            yield word


def holders(supports):
    owner = defaultdict(list)
    for knot, row in enumerate(supports):
        if len(set(row)) != len(row):
            raise ValueError(f'Repeated distinction in knot {knot}')
        for distinction in row:
            owner[distinction].append(knot)
    if any(len(knots) > 2 for knots in owner.values()):
        raise ValueError('A distinction has more than two holders')
    return {distinction: tuple(knots) for distinction, knots in owner.items()}


def connected(size, meetings):
    reached = 1
    while True:
        previous = reached
        for first, second, _ in meetings:
            pair = (1 << first) | (1 << second)
            if pair & reached:
                reached |= pair
        if reached == previous:
            return reached.bit_count() == size


def input_rows(meetings, loose):
    supports = [[] for _ in loose]
    distinction = 0
    for first, second, multiplicity in meetings:
        for _ in range(multiplicity):
            supports[first].append(distinction)
            supports[second].append(distinction)
            distinction += 1
    for row, count in zip(supports, loose, strict=True):
        row.extend(range(distinction, distinction + count))
        distinction += count
    return tuple(map(tuple, supports))


def census(size):
    """Each start once up to renaming, in the census's recorded order."""
    pairs = tuple(combinations(range(size), 2))
    pair_number = {pair: i for i, pair in enumerate(pairs)}
    relabelings = [
        (order, tuple(pair_number[tuple(sorted((order[a], order[b])))] for a, b in pairs))
        for order in permutations(range(size))
    ]

    def as_meetings(counts):
        return tuple((*pair, count) for pair, count in zip(pairs, counts, strict=True) if count)

    seen = set()
    for width in range(size - 1, len(pairs) + 1):
        for where in combinations(range(len(pairs)), width):
            if not connected(size, tuple((*pairs[i], 1) for i in where)):
                continue
            for values in product((1, 2), repeat=width):
                total_shared = sum(values)
                if total_shared > 12:
                    continue
                word = [0] * len(pairs)
                for i, count in zip(where, values, strict=True):
                    word[i] = count
                if tuple(word) in seen:
                    continue
                orbit = defaultdict(list)
                for order, indexes in relabelings:
                    renamed = tuple(word[i] for i in indexes)
                    orbit[renamed].append(order)
                seen.update(orbit)
                original_meetings = as_meetings(word)
                least = min(orbit, key=as_meetings)
                meeting_key = as_meetings(least)
                degree = [0] * size
                for a, b, count in original_meetings:
                    degree[a] += count
                    degree[b] += count
                loose_seen = set()
                for loose in product(*(range(max(0, 3 - count), 3) for count in degree)):
                    if total_shared + sum(loose) > 12:
                        continue
                    loose_key = min(tuple(loose[i] for i in order) for order in orbit[least])
                    if loose_key not in loose_seen:
                        loose_seen.add(loose_key)
                        yield meeting_key, loose_key


def sampled(size, count, seed, p_meet=1 / 3, max_distinctions=18):
    """Labelled, independently accepted samples with replacement under the recorded weighting."""
    rng = Random(seed)
    pairs = tuple(combinations(range(size), 2))
    accepted = 0
    while accepted < count:
        selected = [pair for pair in pairs if rng.random() < p_meet]
        meetings = tuple((a, b, rng.randrange(1, 3)) for a, b in selected)
        loose = tuple(rng.randrange(3) for _ in range(size))
        if sum(loose) + sum(count for _, _, count in meetings) > max_distinctions:
            continue
        arities = list(loose)
        for first, second, multiplicity in meetings:
            arities[first] += multiplicity
            arities[second] += multiplicity
        if min(arities) < 3 or not connected(size, meetings):
            continue
        accepted += 1
        yield meetings, loose


@cache
def heldout(size):
    return tuple(input_rows(*start) for start in sampled(size, 300, 20261206 + size))


def built_start(ring_count, connections):
    center = 4 * ring_count
    meetings = [(first + position, first + (position + 1) % 4, 1)
                for first in range(0, center, 4) for position in range(4)]
    meetings.extend((knot, center, 1) for knot in connections)
    held = [set() for _ in range(center + 1)]
    for first, second, _ in meetings:
        held[first].add(second)
        held[second].add(first)
    for row in held:
        row.discard(center)
    needs = Counter(knot for group in demand(held) for knot in group)
    return input_rows(meetings, [max(2, needs[knot]) for knot in range(center)] + [0])


def start_items(group):
    if group == 'census':
        starts = (item for size in (3, 4, 5) for item in census(size))
        for i, start in enumerate(starts):
            yield f'census {i}', input_rows(*start)
    elif group == 'heldout':
        for size in (6, 7, 8):
            for i, supports in enumerate(heldout(size)):
                yield f'held out {size}-{i}', supports
    elif group == 'witnesses':
        yield 'referee built 0 (9 knots)', built_start(2, (0, 2, 4))
        yield 'referee built 17 (13 knots)', built_start(3, (0, 4, 8))
        yield 'referee built 20 (17 knots)', built_start(4, (0, 4, 8, 12))
        larger = sampled(10, 35, 61261236, 2.75 / 9, 30)
        yield 'referee sampled 10-34', input_rows(*next(islice(larger, 34, None)))
        yield 'held out 7-239', heldout(7)[239]
    else:
        raise ValueError(f'Unknown group {group!r}')


def demand(holds):
    """Groups of prospective parents, from the sets with one common holder."""
    common_holders = defaultdict(set)
    partners = defaultdict(int)
    for holder, members_at_holder in enumerate(holds):
        members_at_holder = sorted(members_at_holder)
        for member_at_holder in members_at_holder:
            common_holders[member_at_holder].add(holder)
        for first, second in combinations(members_at_holder, 2):
            partners[first] |= 1 << second
            partners[second] |= 1 << first

    large = []

    def maximal(group, remaining, inspected):
        if not remaining:
            if not inspected and len(group) >= 3 and not set.intersection(
                *(common_holders[knot] for knot in group)
            ):
                large.append(tuple(sorted(group)))
            return
        pivot = max(names_of(remaining | inspected), key=lambda knot: (partners[knot] & remaining).bit_count())
        for knot in names_of(remaining & ~partners[pivot]):
            together = partners[knot]
            maximal((*group, knot), remaining & together, inspected & together)
            remaining ^= 1 << knot
            inspected |= 1 << knot

    maximal((), row_mask(partners), 0)
    covered = {pair for group in large for pair in combinations(group, 2)}
    uncovered = [(a, b) for a, others in partners.items() for b in names_of(others)
                 if a < b and (a, b) not in covered]
    return sorted(large) + sorted(uncovered)


def grow(supports, arm='ordinary'):
    """One complete round, preserving the order in which the census allocates distinctions."""
    if arm not in ARMS:
        raise ValueError(f'Unknown fresh-count rule {arm!r}')
    supports = tuple(map(tuple, supports))
    owner = holders(supports)
    loose = [tuple(name for name in row if len(owner[name]) == 1) for row in supports]
    if not any(loose):
        return supports, 'closed'

    encounters = [set() for _ in supports]
    for knots in owner.values():
        if len(knots) == 2:
            a, b = knots
            if loose[a]:
                encounters[b].add(a)
            if loose[b]:
                encounters[a].add(b)
    groups = demand(encounters)
    needed = Counter(knot for group in groups for knot in group)
    if any(needed[knot] > len(names) for knot, names in enumerate(loose)):
        return supports, 'stalled'

    plan = groups + [(knot,) for knot, names in enumerate(loose) for _ in names[needed[knot]:]]
    still_loose = list(map(iter, loose))
    inputs = [tuple(sorted(next(still_loose[knot]) for knot in parents)) for parents in plan]
    assert sum(map(len, inputs)) == sum(map(len, loose))
    children = [set() for _ in supports]
    for child, parents in enumerate(plan):
        for parent in parents:
            children[parent].add(child)
    following_demand = Counter(child for group in demand(children) for child in group)

    laws = span(map(row_mask, supports))
    next_name = max(owner) + 1
    births = []
    for child, old_names in enumerate(inputs):
        fresh = following_demand[child]
        if not member(row_mask(old_names), laws):
            fresh = max(fresh, 3 - len(old_names), 1)
        floor = max(0, 3 - len(old_names))
        if arm == 'one_fewer':
            kept = min(fresh, max(floor, fresh - 1))
        elif arm == 'arity_floor':
            kept = min(fresh, floor)
        else:
            kept = fresh
        births.append(old_names + tuple(range(next_name, next_name + kept)))
        next_name += fresh
    return supports + tuple(births), 'funded'


def kernel_images(words, image):
    """Kernel of a linear map on the span of independent input words."""
    pivots = {}
    kernel = []
    for word in words:
        signature = image(word)
        while signature:
            lead = signature.bit_length() - 1
            previous = pivots.get(lead)
            if previous is None:
                pivots[lead] = signature, word
                break
            signature ^= previous[0]
            word ^= previous[1]
        else:
            kernel.append(word)
    return tuple(kernel)


def bicycle(supports):
    """Dimensions of allowed changes and law changes, then the basis with loose entries zero."""
    owner = holders(supports)
    laws = span(map(row_mask, supports))
    columns = {name: row_mask(knots) for name, knots in owner.items()}
    loose = row_mask(name for name, knots in owner.items() if len(knots) == 1)

    def syndrome(word):
        value = 0
        for name in names_of(word):
            value ^= columns[name]
        return value

    law_changes = kernel_images(laws.values(), syndrome)
    closed_law_changes = kernel_images(law_changes, lambda word: word & loose)
    return len(owner) - len(laws), len(law_changes), closed_law_changes


def projection_rank_loss(older, newer):
    """Extra independent equations after forgetting every distinction absent from older."""
    old_names = row_mask(holders(older))
    old_laws = span(map(row_mask, older))
    new_laws = span(map(row_mask, newer))
    new_only = span(word & ~old_names for word in new_laws.values())
    return len(new_laws) - len(new_only) - len(old_laws)
