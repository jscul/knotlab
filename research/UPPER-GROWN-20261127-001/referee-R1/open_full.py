"""Search all allowed carriers before and after the constructed growth, and on selected splits."""

import argparse
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter

import networkx as nx

from census_recount import Search, names
from open_cuts import graph_rows
from open_witness import CARRIERS, START, advance


HERE = Path(__file__).resolve().parent


def census(search, knots):
    began = perf_counter()
    with search.finite_bonds(knots) as (bonds, count, diagnostics):
        boxes, pairs = search.boxes(bonds, count)
    return {'knots': knots, **diagnostics, 'bonds': count, 'qualifying_first_pairs': pairs,
            'box_count': len(boxes),
            'boxes': [[[names(r >> 1), r & 1] for r in box] for box in boxes],
            'elapsed_seconds': round(perf_counter() - began, 6)}


def orbits(knots):
    endpoints = [tuple(i for i, k in enumerate(knots) if x in k) for x in range(18)]
    graph = nx.Graph(endpoints)
    actions = list(nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
    todo = set(range(18))
    out = []
    while todo:
        x = min(todo)
        a, b = endpoints[x]
        equivalent = sorted({endpoints.index(tuple(sorted((move[a], move[b])))) for move in actions})
        out.append(equivalent)
        todo.difference_update(equivalent)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--witness', action='store_true')
    parser.add_argument('--orbits', type=int, default=0)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    before = perf_counter()
    sources = graph_rows()
    grouped = [orbits(row[2]) for row in sources]
    ordered = [(rank, cuts[rank], source) for rank in range(max(map(len, grouped)))
               for source, cuts in zip(sources, grouped, strict=True) if rank < len(cuts)]
    result = {'stored_parent_systems': len(sources), 'all_inequivalent_splits': len(ordered),
              'all_split_choices': sum(len(o) for _, o, _ in ordered), 'orbits_examined': 0,
              'choice_order': 'One split per system on each pass. On each system visit its still unseen '
                              'distinction of smallest recorded integer. Marked shared distinctions related by '
                              'a relabeling of the closed source give isomorphic splits.', 'splits': []}
    with TemporaryDirectory(prefix='open-scratch-', dir=HERE) as scratch:
        compiled = Path(scratch) / 'search.so'
        subprocess.run(['g++', '-std=c++20', '-O3', '-march=native', '-fPIC', '-shared',
                        str(HERE / 'census_search.cpp'), '-o', str(compiled)], check=True,
                       env=dict(os.environ, TMPDIR=scratch))
        search = Search(compiled)
        if args.witness:
            before_growing = census(search, START)
            after_growing = census(search, advance(START).supports)
            planted = {tuple(sorted((tuple(sorted(CARRIERS[i])), tuple(sorted(CARRIERS[i + 1]))))) for i in (0, 2, 4)}
            assert any({tuple(sorted((tuple(box[i][0]), tuple(box[i+1][0])))) for i in (0, 2, 4)} == planted
                    for box in after_growing['boxes'])
            result['complete_constructed_start_and_grown_stage'] = [before_growing, after_growing]
        for index, group, row in ordered[:args.orbits]:
            file, line, knots = row[:3]
            split = min(group)
            last = max(i for i, k in enumerate(knots) if split in k)
            changed = tuple(tuple(18 if x == split and i == last else x for x in k) for i, k in enumerate(knots))
            details = census(search, changed)
            result['splits'].append({'file': file, 'line': line, 'orbit_index': index,
                                     'equivalent_splits': group, 'new_end_at_knot': last, **details})
    result['orbits_examined'] = len(result['splits'])
    result['labelled_splits_covered'] = sum(len(row['equivalent_splits']) for row in result['splits'])
    result['positive_orbits'] = sum(row['box_count'] > 0 for row in result['splits'])
    result['positive_labelled_splits'] = sum(len(row['equivalent_splits']) for row in result['splits'] if row['box_count'])
    result['elapsed_seconds'] = round(perf_counter() - before, 6)
    args.out.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print({k:v for k,v in result.items() if k not in ('splits','complete_constructed_start_and_grown_stage','choice_order')})
    times = [r['elapsed_seconds'] for r in result['splits']]
    print('split_seconds_min_max', (min(times), max(times)) if times else (),
          'witness_start_and_grown_stage',
          [(r['bonds'], r['box_count'], r['elapsed_seconds'])
           for r in result.get('complete_constructed_start_and_grown_stage', [])])


if __name__ == '__main__':
    main()
