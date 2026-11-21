"""Independently check named source realizations, sign ranks and certificates."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product

from job import write
from panels_sources import COUNTS, OUT, seed_for
from panels_summary import read


def low_rank(vectors):
    basis = {}
    for n in vectors:
        while n:
            least = n & -n
            if least not in basis:
                basis[least] = n
                break
            n ^= basis[least]
    return len(basis)


def literal_rank(rows, holders, odd):
    active = {x for h in holders for x in rows[h]}
    # The lowest position is the sign in this independent reduction.
    base = tuple(sum(2 << x for x in rows[h]) for h in holders)
    coefficient = low_rank(base)
    augmented = low_rank(r | int(h in odd) for h, r in zip(holders, base, strict=True))
    return dict(names=len(active), rank=coefficient, augmented_rank=augmented,
                words=1 << (len(active) - coefficient) if coefficient == augmented else 0)


def prufer(word):
    rest = set(range(len(word) + 2))
    count = Counter(word)
    edges = []
    for h in word:
        chosen = min(k for k in rest if not count[k])
        rest.remove(chosen)
        count[h] -= 1
        edges.append(tuple(sorted((chosen, h))))
    return sorted((*edges, tuple(sorted(rest))))


def check_source(source):
    panel = source['panel']
    assert source['seed_sha256'] == seed_for(panel)
    rows = [set(h) for h in source['before_permutation']]
    p = source['source_name_permutation']
    d = source['source_holder_order_to_original']
    assert source['source_rows'] == [sorted(p[x] for x in rows[j]) for j in d]
    degrees = Counter(x for row in rows for x in row)
    loose = [sum(degrees[x] == 1 for x in row) for row in rows]
    meet = {(a, b): len(rows[a] & rows[b]) for a, b in combinations(range(len(rows)), 2) if rows[a] & rows[b]}
    if panel == 'T':
        predicted = prufer(source['prufer'])
        assert meet == dict.fromkeys(predicted, 1)
        active = Counter(a for pair in predicted for a in pair)
        assert loose == [max(0, 3 - active[h]) + s for h, s in enumerate(source['extra_private'])]
    elif panel in ('M', 'E'):
        amounts, private = source['indexed_ring']
        assert meet == {tuple(sorted((i, (i + 1) % 5))): amounts[i] for i in range(5)}
        expected = private + source.get('companion_arities', [])
        assert loose == expected
    else:
        assert set(meet) == set(combinations(range(4), 2)) and set(meet.values()) <= {1, 2}
        assert loose == [1] * 4


def check_certificate(rows, event):
    holders = set(event['component_holders'])
    shared = {(a, b): set(rows[a]).intersection(rows[b]) for a, b in combinations(sorted(holders), 2)
              if set(rows[a]).intersection(rows[b])}

    def meet(a, b):
        return tuple(sorted((a, b))) in shared

    p = event['certificate']
    if p['kind'] == 'planar_rotation':
        rotation = dict(p['rotation'])
        assert set(rotation) == holders and not event['operator_positive']
        todo = {(a, b) for a, b in product(holders, repeat=2) if a != b and meet(a, b)}
        assert todo == {(a, b) for a, choices in rotation.items() for b in choices}
        faces = 0
        while todo:
            start = current = min(todo)
            while current in todo:
                a, b = current
                todo.remove(current)
                neighbors = rotation[b]
                current = b, neighbors[(neighbors.index(a) + 1) % len(neighbors)]
            assert current == start
            faces += 1
        assert faces == p['face_count'] and len(holders) - len(shared) + faces == 2
        return 'verified_planar_rotation'
    assert event['operator_positive']
    groups = {a: set(g) for a, g in p['groups']}
    assert set().union(*groups.values()) <= holders
    assert sum(map(len, groups.values())) == len(set().union(*groups.values()))
    for start, chosen in groups.items():
        stack = [start]
        for a in stack:
            stack.extend(b for b in sorted(chosen) if b not in stack and meet(a, b))
        assert set(stack) == chosen
    required = list(combinations(p['anchor_parts'][0], 2)) if p['kind'] == 'five_all_pairs' else list(product(*p['anchor_parts']))
    assert len(required) in (9, 10)
    for a, b in required:
        assert any(meet(u, v) for u, v in product(groups[a], groups[b]))
    for path in p['paths']:
        for a, b, name in zip(path['holders'], path['holders'][1:], path['named_meetings']):
            assert name in shared[tuple(sorted((a, b)))]
    return 'verified_connected_groups'


def checked_case(source, results):
    check_source(source)
    results['named_source_replays'] += 1
    for law, history in source['laws'].items():
        assert history['founder']['lawful'] and history['founder']['essential']
        results['source_lawfulness_checks'] += 1
        before = source['source_rows']
        previous_closed = set()
        for cut in history['cuts']:
            after = cut['after_rows']
            assert after[:len(before)] == before
            births = cut['births']
            assert [b['support'] for b in births] == after[len(before):]
            found = {tuple(c['holders']) for c in cut['components'] if not c['loose']}
            new = {tuple(e['component_holders']) for e in cut['new_closing_components']}
            assert new == found - previous_closed and previous_closed <= found
            for e in cut['new_closing_components']:
                want = Counter(x for i in e['old_span_rows'] for x in before[i])
                assert sorted(x for x, count in want.items() if count % 2) == e['inputs']
                assert literal_rank(after, e['component_holders'], ()) == e['all_even_scalar']
                assert literal_rank(after, e['component_holders'], (e['holder'],)) == e['single_odd_scalar']
                results[check_certificate(after, e)] += 1
            if 'union_signs' in cut:
                s = cut['union_signs']
                assert len(s['scenarios']) == 1 << len(s['ordered_terminal_holders'])
                for r in s['scenarios']:
                    assert literal_rank(after, range(len(after)), r['odd_holders']) == r['scalar']
                    for c in r['components']:
                        assert literal_rank(after, c['holders'], r['odd_holders']) == c['scalar']
                    results['M_joint_signs'] += 1
                    if len(new) == 2:
                        results['M_simultaneous_joint_signs'] += 1
            results[f'{law}_funded_physical_replays'] += 1
            before, previous_closed = after, found


def main():
    draws = read(OUT / 'panels_histories.json.gz')
    assert Counter(row['panel'] for row in draws) == COUNTS
    counts = Counter()
    for source in draws:
        checked_case(source, counts)
    receipts = ('panels_histories.json.gz', 'panels_summary.json', 'panels_witnesses.json')
    write('panels_audit.json', {'passed': counts, 'sha256': {name: sha256((OUT / name).read_bytes()).hexdigest() for name in receipts}})
    print(counts, flush=True)


if __name__ == '__main__':
    main()
