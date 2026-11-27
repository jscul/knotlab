"""Reverse the funded round when possible and test individual source-law deletions on split boxes."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from time import perf_counter

from open_cuts import Source
from open_witness import advance

HERE = Path(__file__).resolve().parent


def predecessor(knots):
    owners = defaultdict(list)
    for i, knot in enumerate(knots):
        for x in knot:
            owners[x].append(i)
    loose = {x for x, ks in owners.items() if len(ks) == 1}
    new = sorted({owners[x][0] for x in loose})
    old = sorted(set(range(len(knots))) - set(new))
    if not new or not old:
        return None
    desired = defaultdict(list)
    for b in new:
        if any(x not in loose and set(owners[x]) <= set(new) for x in knots[b]):
            return None
        parents = tuple(sorted(old.index(i) for x in knots[b] if x not in loose
                               for i in owners[x] if i != b))
        if not parents or len(set(parents)) != len(parents):
            return None
        desired[parents].append(b)
    before = [knots[i] for i in old]
    growth = advance(before)
    if growth.status != 'funded' or Counter(b.parents for b in growth.births) != Counter(
            {p: len(group) for p, group in desired.items()}):
        return None
    order = []
    for b in growth.births:
        original = desired[b.parents].pop(0)
        if len(b.fresh) != len(set(knots[original]) & loose):
            return None
        order.append(original)
    # A loose distinction's identity can be matched to the input that the
    # recorded round takes. This explicitly constructs an admissible parent
    # ordering where a parent has more than one available input.
    before = [tuple(sorted(k, key=lambda x: next((i for i, b in enumerate(order) if x in knots[b]), -1)))
              for k in before]
    replay = advance(before)
    assert replay.status == 'funded'
    fresh_names = {}
    for current, original in zip(replay.births, order, strict=True):
        for x, y in zip(current.fresh, sorted(set(knots[original]) & loose), strict=True):
            fresh_names[x] = y
        assert {fresh_names.get(x, x) for x in replay.supports[current.knot]} == set(knots[original])
    return {'earlier_knots': before, 'new_law_indices_in_original': order,
            'parents_in_earlier_order': [x.parents for x in replay.births]}


def upper_literal(stage, pool, left, right, first_sign, second_sign):
    a, b = sorted((stage.reading(tuple(left)), stage.reading(tuple(right))))
    if (a, b) not in pool:
        upper = stage.allocate()
        for u, v in product((False, True), repeat=2):
            stage.solver.add_clause([a if not u else -a, b if not v else -b, upper if u != v else -upper])
        pool[a, b] = upper
    return pool[a, b] * (1 if first_sign == second_sign else -1)


def read(row):
    supports = row['knots']
    stop = supports
    history = []
    while (previous := predecessor(stop)) is not None:
        history.append(previous)
        stop = previous['earlier_knots']
    stage = Source(supports)
    upper_pairs = {}
    boxes = []
    for box in row['boxes']:
        groups = [upper_literal(stage, upper_pairs, box[i][0], box[i+1][0], box[i][1], box[i+1][1]) for i in (0, 2, 4)]
        missing = []
        missing_literals = []
        for word in product((0, 1), repeat=3):
            signed = [lit * (1 if b else -1) for lit, b in zip(groups, word, strict=True)]
            if not stage.permits(signed):
                missing.append(''.join(map(str, word)))
                missing_literals.append(signed)
        assert '111' in missing
        needed = [[i for i in range(len(supports)) if stage.permits(lits, drop=i)] for lits in missing_literals]
        boxes.append({'carriers_and_signs': box, 'upper_missing': missing, 'source_laws_needed_for_each_word': needed})
    stage.solver.delete()
    return {'file': row['file'], 'line': row['line'], 'equivalent_splits': row['equivalent_splits'],
            'ordinary_predecessors_newest_first': history, 'boxes': boxes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    started = perf_counter()
    whole = json.loads(args.input.read_text())
    chosen = [r for r in whole['splits'] if r['box_count']]
    if 'complete_constructed_start_and_grown_stage' in whole:
        grown = whole['complete_constructed_start_and_grown_stage'][1]
        witness = read(dict(grown, file='chosen start', line=None, equivalent_splits=[0]))
    else:
        witness = None
    results = [read(r) for r in chosen[:args.limit]]
    summary = Counter()
    depths = Counter()
    for result in results:
        n = len(result['equivalent_splits'])
        history = result['ordinary_predecessors_newest_first']
        if history:
            summary['labelled split choices with any exact predecessor'] += n
            depths[len(history)] += n
        for box in result['boxes']:
            summary['box instances across labelled split choices'] += n
            full = len(box['upper_missing']) == 1 and len(box['source_laws_needed_for_each_word'][0]) == 12
            summary['one upper word missing, all twelve laws needed'] += n * full
            if history:
                new = set(history[0]['new_law_indices_in_original'])
                target = set(box['source_laws_needed_for_each_word'][box['upper_missing'].index('111')])
                summary['box instances that need both births'] += n * (new <= target)
    result = {'positive_split_classes_in_input': len(chosen), 'positive_split_classes_examined': len(results),
              'constructed_growth': witness, 'all_positive_split_checks': results, 'totals': dict(summary),
              'rounds_recoverable_by_labelled_split_choice': dict(depths),
              'elapsed_seconds': round(perf_counter() - started, 6)}
    args.out.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print('positive classes', len(results), 'totals', dict(summary), 'depths', dict(depths), 'seconds', result['elapsed_seconds'])


if __name__ == '__main__':
    main()
