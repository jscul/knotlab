"""Check funded continuation and ending controls at the level of literal parent sets."""
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/PARTNER-RETRACT-20261119-001'))
from retraction_check import positive_realization, rosterlib

TICKET = 'GROWTH-CONTINUES-20261119-001'
OUT = ROOT / 'artifacts' / TICKET / (TICKET + '-E001_checks')


def subset_tail(m):
    """Compare the exact groups with the inclusion rule at every layer."""
    rows = []
    universe = frozenset(range(m))
    for k in range(1, m):
        layer = list(map(frozenset, combinations(range(m), k)))
        index = {item: j for j, item in enumerate(layer)}
        blocks = [
            frozenset(j for j, item in enumerate(layer) if parent <= item)
            for parent in map(frozenset, combinations(range(m), k - 1))
        ]
        groups = rosterlib.groups_of(index.values(), blocks)
        expected = {
            frozenset(index[top - {v}] for v in top)
            for top in map(frozenset, combinations(range(m), k + 1))
        }
        assert set(groups) == expected
        counts = Counter(v for group in groups for v in group)
        assert all(counts[v] == m - k for v in index.values())
        if k >= 4:
            graph = rosterlib.candidate_graph(index.values(), blocks)
            for group in groups:
                assert max(len(group & block) for block in blocks) == 2
                covered_pairs = {pair for block in blocks for pair in combinations(sorted(group & block), 2)}
                assert len(covered_pairs) == len(group) * (len(group) - 1) // 2
                assert all(len(group.intersection(graph[v])) <= 2 for v in set(graph) - group)
        rows.append({'k': k, 'live': len(layer), 'births': len(groups),
                     'new_parents': k + 1, 'individual_replacements': 0 if k >= 4 else None})
    return rows


def copied_partners(n=3, copies=2):
    """Every allowed group has no individual replacement at this reached stage."""
    roster = list(product(range(n), range(2), range(copies)))
    def adjacent(i, j):
        a, b, _ = roster[i]
        c, d, _ = roster[j]
        return i != j and (a != c or b == d)

    points = range(len(roster))
    blocks = {frozenset((i, j)) for i, j in combinations(points, 2) if adjacent(i, j)}
    opens = [2 ** (n - 1)] * len(roster)
    groups = sorted(rosterlib.groups_of(points, blocks), key=lambda g: tuple(sorted(g)))
    assert len(groups) == 2 ** n and all(len(g) == n * copies for g in groups)
    assert all(sum(not adjacent(u, v) for v in g) == copies
               for g in groups for u in set(points) - g)
    counts = Counter(v for g in groups for v in g)
    assert [counts[v] for v in points] == opens
    complement = {i: roster.index((a, 1-b, t)) for i, (a, b, t) in enumerate(roster)}
    assert all(not adjacent(v, complement[v]) for v in points)
    assert {frozenset(complement[v] for v in b) for b in blocks} == blocks
    new_blocks = rosterlib.maximal_blocks({i for i, g in enumerate(groups) if v in g} for v in points)
    assert len(new_blocks) == 2 * n
    assert all(sum(u.isdisjoint(v) for v in groups) == 1 for u in groups)
    new_groups = rosterlib.groups_of(range(len(groups)), new_blocks)
    assert len(new_groups) == 2 ** (2 ** (n-1)) - 2*n
    history = positive_realization(blocks, opens)
    return {'partner_pairs': n, 'copies_per_side': copies, 'parents_per_group': n*copies,
            'old_blocks_per_group': (n*copies + 1)//2, 'individual_replacements': 0,
            'legal_groups': len(groups), 'following_births': len(new_groups),
            'literal_reached_stage': history}


def complete_control():
    points = range(7)
    opens = [1]*7
    blocks = [frozenset(pair) for pair in combinations(points, 2)]
    rows = list(rosterlib.grow(opens, blocks, 3))
    assert [r['count'] for r in rows if 'count' in r] == [1]
    assert rows[-1]['end'] == 'closed'
    # Two live junctions can continue on a single pair as well as close.
    def two(opens):
        return list(rosterlib.grow(opens, [frozenset((0, 1))], 6))
    assert [r['count'] for r in two([2, 1]) if 'count' in r] == [2]*6
    assert [r['count'] for r in two([1, 1]) if 'count' in r] == [1]
    return {'unheld_complete_on_seven': rows, 'two_points_supplies_2_1': 'six rounds of two',
            'two_points_supplies_1_1': 'one closing birth'}


def main():
    output = {'single_block_layers': {m: subset_tail(m) for m in range(3, 10)},
              'complete_controls': complete_control(), 'copied_partners': copied_partners()}
    (OUT / 'local_controls.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()

