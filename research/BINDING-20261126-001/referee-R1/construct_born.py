"""A forced relation on three disjoint cycles made entirely of new distinctions.

Three ordinary five-knot rings grow in a single connected start. Their own
distinctly named loose distinctions become closed cycles at the following
round. This program generates all births from the support lists, without the
author's engine, and checks what happens when each indispensable law is lifted.
"""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from functools import reduce
import operator
import resource
from time import perf_counter

from construct_witness import (
    OUT, analyze, as_strings, basis, bitmask, bits, canonical, compare_by_size, holders,
    image, kernel, moves, one_cycle,
)


def start(style):
    rows = [[] for _ in range(15)]
    labels = [f'ring {r + 1}, position {j}' for r in range(3) for j in range(5)]
    next_name = 0

    def knot(name):
        rows.append([])
        labels.append(name)
        return len(rows) - 1

    def share(*among):
        nonlocal next_name
        for k in among:
            rows[k].append(next_name)
        next_name += 1
        return next_name - 1

    rings = [list(range(i * 5, (i + 1) * 5)) for i in range(3)]
    for ring in rings:
        for i, k in enumerate(ring):
            share(k, ring[(i + 1) % 5])
    loose = []
    for ring in rings:
        loose.append(bitmask(share(p) for p in ring for _ in range(2)))

    incidences = Counter()
    for r, s in combinations(range(3), 2):
        description = f'between rings {r + 1} and {s + 1}'
        left, right = knot(f'{description}, first attachment'), knot(f'{description}, second attachment')
        for i, side in ((r, left), (s, right)):
            port = incidences[i]
            incidences[i] += 1
            if style == 'paired':
                p = rings[i][2 * port]
                share(p, side)
                share(p, side)
            else:
                # Already joinable within the original ring via the knot between them.
                share(rings[i][port], side)
                share(rings[i][port + 2], side)
        share(left, right)
        if style == 'detour':
            previous = left
            for h in range(3):
                place = knot(f'{description}, extra knot {h + 1}')
                share(previous, place)
                share(previous, place)
                previous = place
            share(previous, right)
            share(previous, right)
        else:
            share(left, right)
    return rows, labels, loose


def pair_round(rows):
    owners = holders(rows)
    waiting = defaultdict(list)
    neighbors = [set() for _ in rows]
    for d, who in owners.items():
        if len(who) == 1:
            waiting[who[0]].append(d)
        else:
            left, right = who
            neighbors[left].add(right)
            neighbors[right].add(left)
    available = set(waiting)

    def parents_from(families):
        pairs = sorted(set().union(*(set(combinations(sorted(family), 2)) for family in families)))
        # No pair belongs to a triple of pairwise eligible parents in this family.
        paired = defaultdict(set)
        for a, b in pairs:
            paired[a].add(b)
            paired[b].add(a)
        assert all(not paired[a] & paired[b] for a, b in pairs)
        return pairs

    groups = parents_from([family & available for family in neighbors])
    demand = Counter(p for pair in groups for p in pair)
    assert set(demand) == available
    assert all(demand[p] == len(waiting[p]) == 2 for p in available)
    children = defaultdict(set)
    inputs = []
    for b, pair in enumerate(groups):
        inputs.append([waiting[p].pop(0) for p in pair])
        for p in pair:
            children[p].add(b)
    needed = Counter(b for pair in parents_from(children.values()) for b in pair)
    assert all(needed[b] == 2 for b in range(len(groups)))
    new = list(rows)
    next_name = len(owners)
    births = []
    for b, pair in enumerate(groups):
        # Two inputs, two required fresh. This passes both three places and the
        # free parity-extension gate, whether or not the old inputs were implied.
        fresh = list(range(next_name, next_name + needed[b]))
        next_name += len(fresh)
        births.append({'parents': list(pair), 'inputs': inputs[b], 'fresh': fresh})
        new.append(inputs[b] + fresh)
    return new, births


def new_carriers(previous, births):
    """Use the three original pieces as names only; each birth must have its own two inputs in one piece."""
    out = [0, 0, 0]
    covered = [0, 0, 0]
    contributors = [[], [], []]
    for b, birth in enumerate(births):
        inputs = bitmask(birth['inputs'])
        owner, = [i for i, word in enumerate(previous) if inputs & word == inputs]
        covered[owner] |= inputs
        assert not out[owner] & bitmask(birth['fresh'])
        out[owner] |= bitmask(birth['fresh'])
        contributors[owner].append(b)
    assert covered == previous
    assert all(len(group) == 5 for group in contributors)
    return out, contributors


def removed_laws(stage, carriers, source_end, first_end, pilot):
    rows = [bitmask(r) for r in stage]
    width = len(holders(stage))
    unique = len(basis(rows)) == len(rows)
    assert unique
    grouped = defaultdict(Counter)
    for i in range(0, len(rows), 7 if pilot else 1):
        wanted = 'from the start' if i < source_end else 'first-round birth' if i < first_end else 'second-round birth'
        allowed = kernel(rows[:i] + rows[i + 1:], width)
        grouped[wanted][','.join(as_strings(image(allowed, carriers), 3))] += 1
    without_first = rows[:source_end] + rows[first_end:]
    return {'all stage laws independent as distinction supports': unique,
            'joint values when every first-round law is removed':
                as_strings(image(kernel(without_first, width), carriers), 3),
            'joint values after removing one law, counted by its origin': dict(grouped)}


def nonminimal_split(stage, previous, following, first_stage_zero, contributors):
    """Two independently named branches, each read on two disjoint growth rounds."""
    named = [previous[0], following[0], previous[1], following[1]]
    laws = [bitmask(row) for row in stage]
    selected = [first_stage_zero + k for group in contributors[:2] for k in group]
    union = reduce(operator.xor, named)
    assert all(one_cycle(word, stage) for word in named)
    assert all(not a & b for a, b in combinations(named, 2))
    assert union == reduce(operator.xor, [laws[k] for k in selected])
    assert all((word & union).bit_count() % 2 == 0 for word in laws)
    all_shortest, _ = moves(stage)
    assert image(all_shortest, named) == (0,)
    width = len(holders(stage))
    joint = image(kernel(laws, width), named)
    assert len(joint) == 4 and not canonical(4, joint)['loss_on_erasure']
    projections = {}
    for subset_size in range(1, 5):
        for subset in combinations(range(4), subset_size):
            projection = tuple(sorted({bitmask(k for k, j in enumerate(subset) if value & (1 << j))
                                       for value in joint}))
            projections[','.join(str(k) for k in subset)] = as_strings(projection, subset_size)
    return {'named supports in order, distinction numbers': [list(bits(w)) for w in named],
            'all four cycles disjoint and shortest-move invariant': True,
            'single-knot unreadability follows separately from the verified two three-parity families': True,
            'union is the sum of these first-round laws, absolute knot numbers': selected,
            'values on every subset of carriers': projections,
            'canonical check on the four actual values': canonical(4, joint),
            'joint interpretation': 'The two parities of each branch agree. The two branches take all four pairs.'}


def raw_carrier_ranks(state, carriers):
    free = kernel([bitmask(row) for row in state], len(holders(state)))
    readings = {}
    for size in range(1, len(carriers) + 1):
        for combo in combinations(range(len(carriers)), size):
            keep = reduce(operator.or_, (carriers[i] for i in combo))
            rank = len(basis(change & keep for change in free))
            readings[','.join(str(i + 1) for i in combo)] = {
                'number of distinctions': keep.bit_count(), 'rank of their allowed states': rank,
                'number of their allowed states': 2**rank,
            }
    return readings


def isolate_rings(original, one, two, born, old_carriers, new_carriers, pilot):
    """Release the omitted holders. Keep the actual supports of every retained knot."""
    descriptions = {}
    owners = holders(original)
    for keep_attachments in (True, False):
        summaries = []
        joint = {0}
        for r, carrier in enumerate(new_carriers):
            source_knots = set(range(5 * r, 5 * (r + 1)))
            selected = set(source_knots)
            if keep_attachments:
                selected.update(k for p in source_knots for d in original[p] for k in owners[d])
            selected.update(len(original) + k for k, birth in enumerate(one[len(original):])
                            if bitmask(birth) & old_carriers[r])
            selected.update(len(one) + k for k, birth in enumerate(born)
                            if bitmask(birth['inputs']) & carrier)
            names = sorted({d for k in selected for d in two[k]})
            renumber = {old: i for i, old in enumerate(names)}
            rows = [[renumber[d] for d in two[k]] for k in sorted(selected)]
            c = bitmask(renumber[d] for d in bits(carrier))
            checks = [bitmask(row) for row in rows]
            allowed = kernel(checks, len(names))
            smallest, sizes = moves(rows)
            capped = compare_by_size(rows, sizes, smallest)
            values = image(allowed, [c])
            joint = {v | (extra << r) for v in joint for extra in values}
            locals_read = 0
            for row in rows[::7 if pilot else 1]:
                restricted = kernel(checks + [1 << d for d in row], len(names))
                locals_read += len(image(restricted, [c])) == 1
            assert one_cycle(c, rows)
            summaries.append({'ring': r + 1, 'retained knot numbers': sorted(selected),
                              'knots': len(rows), 'distinctions': len(names),
                              'values of the ring parity': list(values),
                              'projections onto the ten carrier distinctions, number of values':
                                  len(image(allowed, [1 << d for d in bits(c)])),
                              'changes of ring parity admitted by shortest moves': list(image(smallest, [c])),
                              'changes of ring parity admitted by all moves of size at most five': list(image(capped, [c])),
                              'tested single knots that determine the parity': locals_read})
        title = ('Each source ring with its two original attachment knots and its two rounds of births'
                 if keep_attachments else 'Each source ring with its two rounds of births, omitting both attachment knots')
        descriptions[title] = {'individual preparations': summaries,
                               'joint image of the three independent preparations':
                                   as_strings(sorted(joint), 3),
                               'canonical test on those three values': canonical(3, tuple(sorted(joint)))}
    return descriptions


def run(style, pilot):
    original, names, source_loose = start(style)
    one, births_one = pair_round(original)
    two, births_two = pair_round(one)
    three, births_three = pair_round(two)
    first_loose, contributors = new_carriers(source_loose, births_one)
    second_loose, _ = new_carriers(first_loose, births_two)
    third_loose, _ = new_carriers(second_loose, births_three)
    assert all(x.bit_count() == 10 for triple in (source_loose, first_loose, second_loose, third_loose) for x in triple)
    assert all(c >= len(holders(original)) for word in first_loose for c in bits(word))
    assert all(not (a & b) for a in source_loose for b in first_loose)
    for r, group in enumerate(contributors):
        law_sum = reduce(operator.xor, [bitmask(one[len(original) + b]) for b in group])
        assert source_loose[r] ^ first_loose[r] == law_sum
    source_sel = list(range(len(original)))
    first_sel = list(range(len(one)))
    second_sel = list(range(len(two)))
    records = {}
    for title, state, carriers, forced_by, cyc in [
        ('Source, loose distinctions of each original ring', original, source_loose, source_sel, False),
        ('First round, same source distinctions now cycles', one, source_loose, source_sel, True),
        ('First round, fresh distinctions of each group still loose', one, first_loose, first_sel, False),
        ('Second round, cycles entirely on distinctions made in the first', two, first_loose, first_sel, True),
        ('Third round, same cycles kept', three, first_loose, first_sel, True),
        ('Third round, cycles entirely on distinctions made in the second', three, second_loose, second_sel, True),
    ]:
        records[title] = analyze(state, carriers, forced_by, pilot, cycle_carriers=cyc)
    mid = records['Second round, cycles entirely on distinctions made in the first']
    assert mid['distinct shortest changes altering each named parity'] == [0, 0, 0]
    assert mid['canonical check of the joint values']['is_knot']
    assert not mid['single-knot exceptions']
    assert not any(row['single-knot exceptions'] for row in records.values())
    return {
        'original knots, in support order': names, 'source supports': original,
        'first ordinary births': births_one, 'second ordinary births': births_two,
        'third ordinary births': births_three,
        'ring-wise source-loose supports': [list(bits(w)) for w in source_loose],
        'ring-wise supports born in the first round': [list(bits(w)) for w in first_loose],
        'ring-wise supports born in the second round': [list(bits(w)) for w in second_loose],
        'raw joint states on each union of round-two carrier supports': raw_carrier_ranks(two, first_loose),
        'five first-round laws identifying each new parity with its own old representative': contributors,
        'second-round laws that force the joint relation':
                {'all original laws': len(original), 'all first-round laws': len(births_one),
                 'second-round laws needed': 0},
        'source laws cannot span the new supports (every distinction on them is fresh at round one)': True,
        'deleting laws of the second-round system': removed_laws(two, first_loose, len(original), len(one), pilot),
        'nonminimal split inside the same connected stage':
            nonminimal_split(two, source_loose, first_loose, len(original), contributors),
        'isolated preparations, omitted knots release their held distinctions':
            isolate_rings(original, one, two, births_two, source_loose, first_loose, pilot),
        'readings': records,
    }


def k2_control():
    """Two independent positive preparations, with all six carriers included."""
    triple = [0, 3, 5, 6]
    joint = tuple(sorted(a | (b << 3) for a in triple for b in triple))
    assert all(value.bit_count() % 2 == 0 for value in joint)
    return {'two independent copies of a checked positive ring triple':
            {'joint values': as_strings(joint, 6), 'number of values': len(joint),
             'canonical check on all six carriers': canonical(6, joint)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))
    then = perf_counter()
    variants = {
        'detour': 'Three five-knot rings with a direct shared distinction and a four-step alternative between each pair of attachments',
        'separate': 'Three five-knot rings with each attachment shared separately with two ring knots, and two direct distinctions between attachments',
        'paired': 'Three five-knot rings with three successive double meetings between each pair of rings',
    }
    preparations = {}
    for style, description in variants.items():
        record = run(style, args.pilot)
        preparations[description] = record
        print(style, [r['distinct shortest changes altering each named parity'] for r in record['readings'].values()])
    output = {'pilot samples every seventh knot at each stage, including the one-law removal': args.pilot,
              'preparations': preparations, 'missing minimality control': k2_control(),
              'elapsed seconds': perf_counter() - then}
    target = 'construct_born_pilot.json' if args.pilot else 'construct_born.json'
    (OUT / target).write_text(json.dumps(output, indent=2) + '\n')
    print(f"Elapsed {output['elapsed seconds']:.3f} seconds")


if __name__ == '__main__':
    main()
