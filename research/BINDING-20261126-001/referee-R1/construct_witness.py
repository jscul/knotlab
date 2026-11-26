"""Build three named rings; check all their values, shortest changes and local reads.

No growth or reading code is imported. Only the canonical knot checker is called.
Use --pilot for a timed subset of the same preparations and dimensions as the full run.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache, reduce
from itertools import combinations
import json
import operator
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def bits(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def bitmask(indices):
    return sum(1 << i for i in indices)


def parity(word):
    return word.bit_count() % 2


def basis(words):
    pivots = {}
    for word in words:
        while word and word.bit_length() in pivots:
            word ^= pivots[word.bit_length()]
        if word:
            pivots[word.bit_length()] = word
    return list(pivots.values())


def kernel(rows, width):
    """Column elimination with input tags yields an independent allowed-change basis."""
    seen = {}
    free = []
    for col in range(width):
        syndrome = bitmask(j for j, row in enumerate(rows) if row & (1 << col))
        change = 1 << col
        while syndrome and syndrome.bit_length() in seen:
            old_syndrome, old_change = seen[syndrome.bit_length()]
            syndrome ^= old_syndrome
            change ^= old_change
        if syndrome:
            seen[syndrome.bit_length()] = syndrome, change
        else:
            free.append(change)
    return free


def image(changes, carriers):
    values = {0}
    for change in changes:
        value = bitmask(i for i, carrier in enumerate(carriers) if parity(change & carrier))
        if value not in values:
            values.update([value ^ old for old in values])
    return tuple(sorted(values))


def as_strings(values, width):
    return [''.join(str((value >> j) & 1) for j in range(width)) for value in values]


@cache
def canonical(width, values):
    """Pass the actual projected states to knotlab using one clause per excluded state."""
    names = [f'p{j}' for j in range(width)]
    clauses = [' '.join(('~' if state & (1 << j) else '') + name
                        for j, name in enumerate(names))
               for state in range(1 << width) if state not in values]
    command = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', '; '.join(clauses),
               '--loops', *names[:-1], '--contact', names[-1], '--json']
    report = json.loads(subprocess.check_output(command, cwd=ROOT,
                        env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')}, text=True))
    assert sorted(report['allowed']) == sorted(as_strings(values, width))
    return {key: report[key] for key in ('binding', 'loss_on_erasure', 'coexistence', 'is_knot')}


def build(ring_size, loose):
    """Ring i has positions j in cyclic order. Its parity uses only these named links."""
    rows, names, ring_starts = [], [], []

    def knot(name):
        names.append(name)
        rows.append([])
        return len(rows) - 1

    registered = []

    def distinction(*knots):
        number = len(registered)
        registered.append(knots)
        for holder in knots:
            rows[holder].append(number)
        return number

    rings, carriers = [], []
    for i in range(3):
        ring = [knot(f'ring {i + 1}, position {j}') for j in range(ring_size)]
        rings.append(ring)
        ring_starts.append(ring[0])
        carriers.append(bitmask(distinction(ring[j], ring[(j + 1) % ring_size])
                                for j in range(ring_size)))

    odd_knots = []
    for j in range(ring_size):
        members = [ring[j] for ring in rings]
        if j % 2:
            odd_knots.extend(members)
            for k in range(2):
                other = knot(f'odd {j}, common knot {k + 1}')
                odd_knots.append(other)
                for member in members:
                    distinction(member, other)
        else:
            attached = [knot(f'even {j}, ring {i + 1} attachment') for i in range(3)]
            for member, other in zip(members, attached):
                distinction(member, other)
                distinction(member, other)
            for left, right in combinations(attached, 2):
                distinction(left, right)

    for i, number in enumerate(loose):
        for _ in range(number):
            distinction(ring_starts[i])
    return rows, names, carriers, odd_knots


def holders(rows):
    owners = defaultdict(list)
    for i, row in enumerate(rows):
        assert len(set(row)) == len(row)
        for d in row:
            owners[d].append(i)
    assert set(owners) == set(range(len(owners)))
    assert all(len(pair) in (1, 2) for pair in owners.values())
    return owners


def first_round(rows, names):
    """Ordinary growth on this family, whose live knots have no common neighbour.

    Every initial loose distinction gets its own offspring. With at most two loose
    in any holder here, each offspring has at most one partner at the next round.
    The one-input birth needs two fresh distinctions to give three places.
    """
    owners = holders(rows)
    adjacent = [set() for _ in rows]
    loose = [[] for _ in rows]
    for d, pair in owners.items():
        if len(pair) == 2:
            a, b = pair
            adjacent[a].add(b)
            adjacent[b].add(a)
        else:
            loose[pair[0]].append(d)
    live = [j for j in range(len(rows)) if loose[j]]
    assert max((len(items) for items in loose), default=0) <= 2
    assert all(not adjacent[j] & adjacent[k] for j, k in combinations(live, 2))
    new_rows, new_names = list(rows), list(names)
    births = []
    n = len(owners)
    for parent in live:
        for old in loose[parent]:
            new_rows.append([old, n, n + 1])
            new_names.append(f'offspring of {names[parent]}, from {old}')
            births.append({'parent': parent, 'input': old, 'fresh': [n, n + 1]})
            n += 2
    return new_rows, new_names, births


def links_of(rows):
    owners = holders(rows)
    outside = len(rows)
    links = [[] for _ in range(outside + 1)]
    ends = []
    for d in range(len(owners)):
        pair = owners[d]
        left, right = (pair + [outside])[:2]
        links[left].append((right, d))
        links[right].append((left, d))
        ends.append((left, right))
    return links, ends


def moves(rows):
    """A shortest change through d consists of d and a shortest alternate holder path."""
    links, ends = links_of(rows)
    all_changes = set()
    lengths = []
    for restricted, (start, goal) in enumerate(ends):
        dist = {start: 0}
        parents = defaultdict(list)
        pending = deque([start])
        while pending:
            first = pending.popleft()
            if goal in dist and dist[first] >= dist[goal]:
                break
            length = dist[first] + 1
            for second, name in links[first]:
                if name == restricted:
                    continue
                if second not in dist:
                    dist[second] = length
                    pending.append(second)
                if dist[second] == length:
                    parents[second].append((first, name))
        if goal not in dist:
            lengths.append(None)
            continue
        lengths.append(1 + dist[goal])

        def collect(end, change):
            if end == start:
                all_changes.add(change)
            else:
                for pred, d in parents[end]:
                    collect(pred, change | (1 << d))

        collect(goal, 1 << restricted)
    return sorted(all_changes), lengths


def compare_by_size(rows, lengths, all_shortest):
    """Independent enumeration of simple cycles up to the longest measured minimum."""
    links, _ = links_of(rows)
    limit = max(5, max(size for size in lengths if size is not None))
    via_size = set()
    up_to_five = set()
    for start in range(len(links)):
        def visit(current, used, change):
            for nxt, d in links[current]:
                if change & (1 << d) or nxt < start:
                    continue
                new_change = change | (1 << d)
                if nxt == start:
                    size = new_change.bit_count()
                    if size <= 5:
                        up_to_five.add(new_change)
                    if any(lengths[k] == size for k in bits(new_change)):
                        via_size.add(new_change)
                elif nxt not in used and new_change.bit_count() < limit:
                    visit(nxt, used | {nxt}, new_change)
        visit(start, {start}, 0)
    assert via_size == set(all_shortest)
    return up_to_five


def one_cycle(carrier, rows):
    owners = holders(rows)
    links = defaultdict(list)
    for d in bits(carrier):
        if len(owners[d]) != 2:
            return False
        left, right = owners[d]
        links[left].append(right)
        links[right].append(left)
    connected = {next(iter(links))}
    pending = list(connected)
    for knot in pending:
        for other in links[knot]:
            if other not in connected:
                pending.append(other)
                connected.add(other)
    return connected == set(links) and all(len(neighbors) == 2 for neighbors in links.values())


def analyze(rows, carriers, odd_knots, pilot, *, cycle_carriers=True):
    checks = [bitmask(row) for row in rows]
    width = len(holders(rows))
    allowed = kernel(checks, width)
    minimum, lengths = moves(rows)
    small = compare_by_size(rows, lengths, minimum)
    assert all(all(not parity(change & row) for row in checks) for change in minimum)
    joint = image(allowed, carriers)
    combined = reduce(operator.xor, carriers)
    closed_cycles = sum(one_cycle(carrier, rows) for carrier in carriers)
    if cycle_carriers:
        assert closed_cycles == len(carriers)
    assert all(not left & right for left, right in combinations(carriers, 2))
    assert reduce(operator.xor, [checks[k] for k in odd_knots]) == combined
    assert all(not parity(combined & row) for row in checks)
    no_loose = all(len(owners) == 2 for d, owners in holders(rows).items() if combined & (1 << d))
    if cycle_carriers:
        assert no_loose
    joint_rel = canonical(3, joint)

    local_zero, knot_projections = Counter(), Counter()
    chosen = list(range(len(rows))) if not pilot else list(range(0, len(rows), 7))
    examples = {}
    for k in chosen:
        row = rows[k]
        locked = kernel(checks + [1 << d for d in row], width)
        restricted = image(locked, carriers)
        local_zero[','.join(as_strings(restricted, 3))] += 1
        singletons = [1 << d for d in row]
        own = image(allowed, singletons)
        verdict = canonical(len(row), own)
        knot_projections[f"{len(row)} places, {len(own)} values, K1-K3 {verdict['is_knot']}"] += 1
        if restricted != joint or not verdict['is_knot']:
            examples[str(k)] = {'label values at local zero': as_strings(restricted, 3),
                                'own projected values': as_strings(own, len(row))}

    return {
        'knots': len(rows), 'distinctions': width, 'allowed rank': len(allowed),
        'ranks of shortest changes and classes': [len(basis(minimum)), len(allowed) - len(basis(minimum))],
        'distinct shortest changes, both enumerations': len(minimum),
        'minimum size through each distinction, counts': dict(sorted(Counter(lengths).items())),
        'values of the three parities on allowed states': as_strings(joint, 3),
        'canonical check of the joint values': joint_rel,
        'attained parity changes using shortest moves': as_strings(image(minimum, carriers), 3),
        'attained parity changes using all moves of size at most five': as_strings(image(small, carriers), 3),
        'simple changes of size at most five': len(small),
        'distinct shortest changes altering each named parity': [
            sum(parity(change & carrier) for change in minimum) for carrier in carriers],
        'joint values with one knot fixed at zero, counted by knot': dict(local_zero),
        'canonical checks on actual projections of tested knots': dict(knot_projections),
        'single-knot exceptions': examples,
        'disjoint simple cycles verified': closed_cycles,
        'their union sums the designated laws': True,
        'their union has no loose distinction': no_loose,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))
    then = perf_counter()
    results = {}
    for label, size, loose in [
        ('Three six-knot rings, one loose at position zero in each', 6, [1, 1, 1]),
        ('Loose funding doubled in the same holders', 6, [2, 2, 2]),
        ('Shorter four-knot rings, one loose in each', 4, [1, 1, 1]),
        ('Longer eight-knot rings, one loose in each', 8, [1, 1, 1]),
    ]:
        rows, names, carriers, selected = build(size, loose)
        new_rows, new_names, births = first_round(rows, names)
        before = analyze(rows, carriers, selected, args.pilot)
        after = analyze(new_rows, carriers, selected, args.pilot)
        results[label] = {
            'ring labels chosen before growth, distinction numbers': [list(bits(c)) for c in carriers],
            'original knot names': names, 'original laws, distinction numbers': rows,
            'source knots whose laws sum to the three named rings': selected,
            'ordinary births': births, 'joint law inherited from source': True,
            'source': before, 'first ordinary round': after,
        }
        assert len(new_names) == len(new_rows)
        assert before['values of the three parities on allowed states'] == after['values of the three parities on allowed states']
    output = {'pilot samples every seventh local knot at both stages of every preparation': args.pilot,
              'elapsed seconds': perf_counter() - then, 'preparations': results}
    target = 'construct_pilot.json' if args.pilot else 'construct_witness.json'
    (OUT / target).write_text(json.dumps(output, indent=2) + '\n')
    for label, record in results.items():
        print(label, [(r['knots'], r['distinct shortest changes altering each named parity'],
                       r['joint values with one knot fixed at zero, counted by knot'])
                      for r in (record['source'], record['first ordinary round'])])
    print(f"Elapsed {output['elapsed seconds']:.3f} seconds")


if __name__ == '__main__':
    main()
