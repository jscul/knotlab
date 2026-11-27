"""Compare the whole-stage reducer with direct enumeration on small two-holder systems."""

import argparse
from itertools import combinations
import json
from time import perf_counter

from other_bonds_determination import HERE, Stage, agreed, ids, mask_of


SYSTEMS = (
    ((0, 1, 2), (2, 3, 4), (4, 5, 6)),
    ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 6, 7), (4, 5, 6, 7)),
    ((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)),
    ((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 8)),
)


def truth_table(supports):
    n = 1 + max(map(max, supports))
    laws = tuple(map(mask_of, supports))
    states = [s for s in range(1 << n) if all(not agreed(s, law) for law in laws)]
    universe = (1 << len(states)) - 1
    carriers = sorted(c for size in (2, 3) for c in combinations(range(n), size))
    masks = {c: mask_of(c) for c in carriers}
    equal = {c: sum(1 << j for j, s in enumerate(states) if agreed(s, m)) for c, m in masks.items()}
    partitions = []
    for law in laws:
        classes = {}
        for j, state in enumerate(states):
            key = state & law
            classes[key] = classes.get(key, 0) | (1 << j)
        partitions.append(list(classes.values()))
    ordinary = [c for c in carriers if all(any(cell & equal[c] and cell & ~equal[c] for cell in cells)
                                           for cells in partitions)]
    tested = 0
    bonds = []
    for a, b, c in combinations(ordinary, 3):
        if masks[a] & masks[b] or (masks[a] | masks[b]) & masks[c]:
            continue
        tested += 1
        cells = [universe]
        for g in (a, b, c):
            cells = [part for cell in cells for part in (cell & ~equal[g], cell & equal[g])]
        present = {w for w, cell in enumerate(cells) if cell}
        if len(present) < 8 and all(len({w & m for w in present}) == 4 for m in (3, 5, 6)):
            bonds.append(((a, b, c), cells))
    return states, carriers, masks, equal, ordinary, tested, bonds


def check_system(supports):
    states, carriers, masks, equal, ordinary, tested, bonds = truth_table(supports)
    index = {s: j for j, s in enumerate(states)}
    found = {}
    mixed_queries = admissible_queries = 0
    for a, b in combinations(ordinary, 2):
        if masks[a] & masks[b]:
            continue
        domain = masks[a] | masks[b]
        for both in (False, True):
            u = (equal[a] & equal[b]) if both else (equal[a] | equal[b])
            changes = {d for d in ids(domain) if any(
                (v := index.get(s ^ (1 << d))) is not None and ((u >> j) ^ (u >> v)) & 1
                for j, s in enumerate(states)
            )}
            if len(changes) != domain.bit_count():
                continue
            admissible_queries += 1
            actual = [g for g, cells in bonds if all(not (cell & u and cell & ~u) for cell in cells)]
            mixed = [g for g in actual if all(masks[c] & domain for c in g)]
            alternative = [g for g in actual if not {a, b}.issubset(g) and g not in mixed]
            if mixed:
                mixed_queries += 1
            category = 'three touching carriers' if mixed else 'different pair of touching carriers' if alternative else (
                'two named carriers' if actual else 'no determining bond')
            if category not in found:
                found[category] = ((a, b), both, u, changes, actual, mixed)
    report = []
    stage = Stage(supports)
    for category, (pair, both, upper, changes, actual, mixed) in found.items():
        result = stage.reducer(pair, both)
        assert changes == set(result['mandatory'])
        stable = set()
        for c in carriers:
            if not changes.intersection(c):
                continue
            partition = {}
            for j, s in enumerate(states):
                key = (s & ~masks[c], agreed(s, masks[c]))
                u = (upper >> j) & 1
                if key in partition and partition[key] != u:
                    break
                partition[key] = u
            else:
                stable.add(c)
        assert stable == set(result['surviving_groups'])
        assert set(mixed) == {r['groups'] for r in result['determining_three_touching_bonds']}
        actual_double = {tuple(c for c in g if changes.intersection(c)) for g in actual if g not in mixed}
        assert actual_double <= set(result['two_touching_groups'])
        report.append({'query_kind': category, 'pair': pair, 'both': both,
                       'directly_checked_carriers_containing_a_mandatory_distinction': sum(bool(changes.intersection(c)) for c in carriers),
                       'direct_and_reduced_surviving_carriers': len(stable),
                       'directly_determining_stage_bonds': len(actual),
                       'direct_and_reduced_determining_bonds_with_three_touching_carriers': len(mixed),
                       'first_determining_example': actual[0] if actual else None})
    stage.solver.delete()
    return {'source_knots': supports, 'allowed_states': len(states), 'nonlocal_agreement_carriers': len(ordinary),
            'disjoint_triples_of_nonlocal_carriers': tested, 'all_genuine_bonds': len(bonds),
            'direct_upper_queries_with_all_raw_distinctions_mandatory': admissible_queries,
            'queries_determined_at_a_bond_with_three_touching_carriers': mixed_queries, 'comparisons': report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    before = perf_counter()
    rows = [check_system(s) for s in (SYSTEMS[:1] if args.pilot else SYSTEMS)]
    result = {'scope': 'Direct all-assignment, all-carrier, all-bond controls on the specified finite systems.',
              'cases': rows, 'seconds': round(perf_counter() - before, 3)}
    kind = 'pilot' if args.pilot else 'all'
    (HERE / f'other_bonds_controls_{kind}.json').write_text(json.dumps(result, indent=2) + '\n')
    print([(len(r['source_knots']), r['all_genuine_bonds'], [c['query_kind'] for c in r['comparisons']]) for r in rows],
          result['seconds'])


if __name__ == '__main__':
    main()
