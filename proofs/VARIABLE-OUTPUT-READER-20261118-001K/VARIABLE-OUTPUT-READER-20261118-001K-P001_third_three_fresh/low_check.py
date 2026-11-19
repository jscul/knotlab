"""Replay the two-shrink minimum-cut proof on two shortest sources and two disjoint binary continuations of each."""

from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def mask(labels):
    return sum(1 << label for label in labels)


def positions(word):
    while word:
        low_bit = word & -word
        yield low_bit.bit_length() - 1
        word ^= low_bit


def cliques(neighbors, available, remaining, chosen=0):
    if remaining == 0:
        yield chosen
        return
    while available.bit_count() >= remaining:
        bit = available & -available
        available ^= bit
        allowed = available & neighbors[bit.bit_length() - 1]
        yield from cliques(neighbors, allowed, remaining - 1, chosen | bit)


def verify(source, prior_shrinks):
    rows = source['junction_supports']
    stars = [mask(row) for row in rows]
    width = source['width']
    high = source['exceptional_site']
    caps = [i for i, row in enumerate(rows) if len(row) == 5]
    assert len(caps) == 2 and len(rows[high]) == 6
    pins = mask((0, *caps))
    shore = cut = 0
    short = []
    pinned = {}
    for index in range(1, 1 << len(stars)):
        bit = index & -index
        shore ^= bit
        cut ^= stars[bit.bit_length() - 1]
        size = cut.bit_count()
        if size <= 6:
            short.append((shore, cut))
        if shore & pins == pins:
            assert size >= 5
            if size == 5:
                pinned[shore] = cut
        elif shore.bit_count() >= 3:
            assert size >= 6
    assert all((a & b) in pinned and (a | b) in pinned for a, b in combinations(pinned, 2))

    high_inputs = set(rows[high]) & set().union(*(set(row) for row in rows[:high]))
    high_outputs = set(rows[high]) - high_inputs
    assert len(high_inputs) == len(high_outputs) == 3
    for i, j in product(high_inputs, high_outputs):
        pair = mask((i, j))
        assert [cut for _, cut in short if cut & pair == pair] == [stars[high]]

    low_fives = {cut for shore, cut in short if not shore & (1 << high) and cut.bit_count() == 5}
    neighbors = [0] * width
    for _, cut in short:
        if cut.bit_count() <= 5:
            for i in positions(cut):
                neighbors[i] |= cut ^ (1 << i)
    common = [star for star in stars if star.bit_count() <= 4]
    adjacent = [(a, b) for a, b in combinations(common, 2) if a & b]
    cap_inputs = set()
    for c in caps:
        cap_inputs.update(set(rows[c]) & set().union(*(set(row) for row in rows[:c])))
    tested = outside = viable = 0
    for candidate in cliques(neighbors, (1 << width) - 1, 5):
        tested += 1
        if candidate in low_fives:
            continue
        outside += 1
        if any((star & candidate).bit_count() > 1 for star in common):
            continue
        if any((candidate & a) and (candidate & b) for a, b in adjacent):
            continue
        if any((candidate & stars[c]).bit_count() > 2 for c in caps):
            continue
        viable += 1
        assert not candidate & mask(cap_inputs)
        assert candidate in pinned.values()
    return {
        'prior_shrinks': prior_shrinks,
        'width': width,
        'ordinary_sites': len(rows),
        'nonempty_shores_checked': (1 << len(stars)) - 1,
        'five_bit_minimum_shores': len(pinned),
        'incomparable_pairs_of_minimum_shores': sum(a & b not in (a, b) for a, b in combinations(pinned, 2)),
        'five_element_table_cliques': tested,
        'five_element_table_cliques_outside_low_span': outside,
        'remaining_possible_five_stars_outside_low_span': viable,
        'remaining_possible_five_stars_outside_true_space': 0,
        'unique_high_cross_witnesses': 9,
    }


def two_disjoint_joins(source):
    rows = [set(row) for row in source['junction_supports']]
    adjacent = [{j for j, other in enumerate(rows) if i != j and row & other}
                for i, row in enumerate(rows)]
    holders = {x: next(i for i, row in enumerate(rows) if x in row) for x in source['loose_bits']}
    moves = [(x, y) for x, y in combinations(sorted(holders), 2)
             if holders[x] != holders[y] and adjacent[holders[x]] & adjacent[holders[y]]]
    first, second = next((a, b) for a, b in combinations(moves, 2)
                         if {holders[x] for x in a}.isdisjoint(holders[y] for y in b))
    width = source['width']
    extra = [[*first, width, width + 1], [*second, width + 2, width + 3]]
    return {**source, 'width': width + 4, 'junction_supports': [*source['junction_supports'], *extra]}, extra


def main():
    data = (HERE / 'closure.json').read_bytes()
    histories = json.loads(data)['shortest_post_exception_histories']
    results = []
    for item in histories:
        if item['prior_shrinks'] + item['subsequent_shrinks'] != 2:
            continue
        source = item['first_history']
        results.append(verify(source, item['prior_shrinks']))
        extended, extra = two_disjoint_joins(source)
        control = verify(extended, item['prior_shrinks'])
        assert control['incomparable_pairs_of_minimum_shores'] >= 1
        results.append({**control, 'additional_rows': extra})
    assert sorted(item['width'] for item in results) == [38, 42, 42, 46]
    print(json.dumps({'source_sha256': sha256(data).hexdigest(), 'controls': results}, indent=2))


if __name__ == '__main__':
    main()
