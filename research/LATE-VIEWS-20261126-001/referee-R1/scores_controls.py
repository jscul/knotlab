"""Count where the three controls can disagree, and which fail there."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from scores import PANELS, STUDY, first_difference, inputs, keys_as_strings, read_rows


CONTROLS = ('without the relay', 'without the group cells', 'the not-all-equal predictor on parity growth')


def map_of_start(stars):
    """Recover cells, finite pieces, and the pair roster used when cells are removed."""
    knots = [set(star) for star in stars]
    links = {i: {j for j, other in enumerate(knots) if i != j and star & other} for i, star in enumerate(knots)}
    loose = {i: len(star - set().union(*(knots[j] for j in links[i]))) for i, star in enumerate(knots)}
    live = {i for i, n in loose.items() if n}
    blocks = {frozenset(v & live) for v in links.values() if len(v & live) >= 2}
    pairs = {frozenset(pair) for block in blocks for pair in combinations(block, 2)}
    # Test larger sets first so a clique extending a smaller set is already known.
    maximal_cliques = []
    for size in range(len(live), 2, -1):
        for members in combinations(sorted(live), size):
            group = frozenset(members)
            if any(group <= prior for prior in maximal_cliques):
                continue
            if all(frozenset(pair) in pairs for pair in combinations(members, 2)):
                maximal_cliques.append(group)
    cells = [cell for cell in maximal_cliques if not any(cell <= block for block in blocks)]
    actual_pairs = [pair for pair in pairs if not any(pair <= cell for cell in cells)]
    demand = Counter(i for group in cells + actual_pairs for i in group)
    growers = {i: set() for i in live}
    chains = {}
    next_point = len(stars)
    for i in sorted(live):
        assert loose[i] >= demand[i]
        for _ in range(loose[i] - demand[i]):
            growers[i].add(next_point)
            growers[next_point] = {i}
            chains[next_point] = max(0, 3 - loose[i])
            next_point += 1
    kept_blocks = [block for block in blocks if not any(block < other for other in blocks)
                   and not any(block <= cell for cell in cells)]
    for group in kept_blocks + cells:
        for i in group:
            growers[i].update(group - {i})
    remaining = set(growers)
    components = []
    while remaining:
        piece = {min(remaining)}
        while True:
            enlarged = piece.union(*(growers[i] for i in piece))
            if enlarged == piece:
                break
            piece = enlarged
        components.append(piece)
        remaining.difference_update(piece)
    finite_pieces = [piece for piece in components if not any(chains.get(i, 0) for i in piece)]
    relay_rounds = [len(piece) - sum(len(cell) - 2 for cell in cells if cell <= piece) - 1 for piece in finite_pieces]
    assert all(r >= 1 for r in relay_rounds)

    no_cells_first_round = Counter()
    for i in growers:
        for j in growers[i]:
            if i >= j or (i not in live and j not in live):
                continue
            members = {i, j}
            parents = len(members & live)
            fresh = len((growers[i] | growers[j]) - members) + chains.get(i, 0) + chains.get(j, 0)
            if members in finite_pieces:
                fresh += 1
            kind = 'join' if parents == 2 else 'offshoot'
            no_cells_first_round[kind, parents, fresh, parents + fresh] += 1
    return cells, relay_rounds, no_cells_first_round


def first_miss(actual, prediction, grown):
    mismatches = [first_difference(read, estimate, len(grown['rows']), grown['end'].startswith('closes'))
                  for read, estimate in zip(actual, prediction)]
    return min((i for i in mismatches if i is not None), default=None)


def controls(limit, confirm_all_rounds):
    if confirm_all_rounds:
        from map_predict import evaluate

    panels = {key: stem for key, stem in PANELS.items() if key[0] == 'uniform'}
    growth, predictions = inputs(panels, limit)
    opportunities, results = Counter(), Counter()
    records = []
    for key, grown in growth.items():
        panel, law, index = key
        base = predictions[key]
        if base['read'] != 'predicted':
            continue
        observed = read_rows(grown)
        predicted = read_rows(base)
        base_miss = first_miss(observed, predicted, grown)
        if law == 'nae':
            cells, relay_rounds, removal_first_round = map_of_start(grown['stars'])
            # Removing cells keeps the assembled map but discards the cell rules.
            # Each birth in round one now reads a pair or an offshoot. Original
            # large groups therefore force a difference whenever cells occur.
            cell_change = 1 if removal_first_round != predicted[0][0] else None
            assert bool(cells) == (cell_change is not None), key
            cell_miss = 1 if removal_first_round != observed[0][0] else base_miss
            if cells:
                assert cell_miss == 1, key
            # With a relay suppressed, the first difference removes its one
            # fresh distinction from the whole finite piece. All relays begin
            # that way, so synchronous first differences cannot cancel.
            relay_change = min((r for r in relay_rounds if r <= len(grown['rows'])), default=None)
            assert base_miss is None or relay_change is None or base_miss != relay_change, key
            relay_miss = min((r for r in (base_miss, relay_change) if r is not None), default=None)
            variants = [(CONTROLS[0], bool(relay_rounds), relay_change, relay_miss),
                        (CONTROLS[1], bool(cells), cell_change, cell_miss)]
            if confirm_all_rounds:
                for mode, variant in zip(('relay', 'cells'), variants):
                    changed = evaluate(grown['stars'], len(base['rows']), law, control=mode)
                    assert changed['read'] == 'predicted', key
                    all_rows = read_rows(changed)
                    assert (all_rows != predicted) == variant[1], (key, mode)
                    assert first_miss(predicted, all_rows, grown) == variant[2], (key, mode)
                    assert first_miss(observed, all_rows, grown) == variant[3], (key, mode)
        else:
            switched = read_rows(predictions[(panel, 'nae', index)])
            difference = first_miss(predicted, switched, grown)
            miss = first_miss(observed, switched, grown)
            variants = [(CONTROLS[2], predictions[(panel, 'nae', index)]['rows'] != base['rows'], difference, miss)]

        for control, changes, inside, miss in variants:
            opportunities[control, 'accepted'] += 1
            opportunities[control, 'changes over predicted horizon' if changes else 'unchanged over predicted horizon'] += 1
            opportunities[control, 'changes in the scored rounds' if inside else 'unchanged in the scored rounds'] += 1
            full = 'full differs' if base_miss else 'full agrees'
            variant = 'control differs' if miss else 'control agrees'
            results[control, 'differ' if miss else 'agree'] += 1
            opportunities[control, full, variant, 'changes' if inside else 'unchanged'] += 1
            records.append({'record': key, 'control': control, 'first change': inside,
                            'first control miss': miss, 'first full miss': base_miss})
    result = keys_as_strings(results)
    recorded = json.loads((STUDY / 'score.json').read_text())['P4']
    return {'prefix per law': limit, 'first differences confirmed by full ablation': confirm_all_rounds,
            'P4 fields': result, 'same as recorded P4': result == recorded if limit is None else None,
            'opportunities': keys_as_strings(opportunities), 'first changed or missed round': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--confirm-all-rounds', action='store_true')
    args = parser.parse_args()
    args.output.write_text(json.dumps(controls(args.limit, args.confirm_all_rounds), indent=2) + '\n')
