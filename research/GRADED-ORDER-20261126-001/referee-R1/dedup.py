"""Check the two seven-knot samples and replay their selection without growing."""

import argparse
import importlib.util
import itertools
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY))
import graded

SETTINGS = {
    'tree+': (40_000, 40, 'fresh7_treeplus.jsonl'),
    'grow': (200_000, 60, 'fresh7_grow.jsonl'),
}


def exact_key(sizes, pairs):
    """Canonical place sizes and shared-distinction counts across all renamings."""
    n = len(sizes)
    multiplicity = [[0] * n for _ in sizes]
    for a, b in pairs:
        multiplicity[a][b] += 1
        multiplicity[b][a] += 1
    groups = defaultdict(list)
    for a in range(n):
        shared_counts = tuple(sorted((sizes[b], count) for b, count in
                                     enumerate(multiplicity[a]) if count))
        groups[(sizes[a], shared_counts)].append(a)
    signatures = sorted(groups)
    arrangements = itertools.product(*(itertools.permutations(groups[s]) for s in signatures))
    positions = list(itertools.combinations(range(n), 2))
    orders = (tuple(itertools.chain.from_iterable(parts)) for parts in arrangements)
    least = min(tuple(multiplicity[order[a]][order[b]] for a, b in positions) for order in orders)
    return tuple(s[0] for s in signatures for _ in groups[s]), least


def inspect_lists():
    classes = defaultdict(list)
    rows = {}
    for kind, (_, _, name) in SETTINGS.items():
        rows[kind] = [json.loads(line) for line in (STUDY / name).read_text().splitlines()]
        for row in rows[kind]:
            sizes, pairs = graded.late.sizes_edges(row['stars'])
            assert row['weighting'] == kind
            assert (sizes, pairs) == (row['sizes'], sorted(map(tuple, row['edges'])))
            classes[exact_key(sizes, pairs)].append({
                'weighting': kind, 'draw': row['draw'], 'split pair': row['split pair'],
                'route cycle': row['route cycle'], 'cells share two': row['cells share two'],
            })
    print(json.dumps({
        'list rows': {kind: len(rs) for kind, rs in rows.items()},
        'within list renaming classes': {
            kind: sum(any(item['weighting'] == kind for item in cl) for cl in classes.values())
            for kind in rows
        },
        'combined renaming classes': len(classes),
        'overlapping or repeated classes': [cl for cl in classes.values() if len(cl) > 1],
    }), flush=True)
    return rows


def replay(kind, rows, sample, prefix):
    original_draws, quota, _ = SETTINGS[kind]
    draws = min(original_draws, prefix) if prefix is not None else original_draws
    started = time.process_time()
    rng = random.Random(graded.SEED)
    tally = Counter()
    by_hash = defaultdict(dict)
    original_kept = defaultdict(list)
    exact_kept = defaultdict(list)
    exact_seen = set()
    hash_seen = {}
    eligible_keys = {}
    metadata = {row['draw']: row for row in rows}
    colliding_starts = {}
    rejects_before_quota = {}
    for i in range(draws):
        sizes, pairs = sample(kind, 7, rng)
        stars = graded.stars_of(sizes, pairs)
        if i in metadata:
            row = metadata[i]
            assert (sizes, [list(p) for p in pairs], stars) == (row['sizes'], row['edges'], row['stars']), (kind, i)
        model = graded.late.Map(stars)
        if model.cls != 'in':
            tally[model.cls] += 1
            continue
        if not all(tree for _, tree, _ in model.pieces):
            tally['a piece with a cycle'] += 1
            continue
        strata = graded.rare(model)
        if not strata:
            tally['accepted, no rare stratum'] += 1
            continue
        tally['eligible'] += 1
        cycle = graded.route_cycle(model)
        bucket = (strata[0], cycle)
        tally[str(bucket)] += 1
        exact = exact_key(sizes, pairs)
        digest = graded.canon(sizes, pairs)
        assert eligible_keys.setdefault(exact, (digest, bucket)) == (digest, bucket), (kind, i)
        by_hash[digest].setdefault(exact, i)
        if len(original_kept[bucket]) < quota:
            if digest not in hash_seen:
                original_kept[bucket].append(i)
                hash_seen[digest] = (exact, i)
            elif hash_seen[digest][0] != exact:
                rejects_before_quota.setdefault(exact, (hash_seen[digest][1], i, bucket))
                colliding_starts[i] = (sizes, pairs)
        if len(exact_kept[bucket]) < quota and exact not in exact_seen:
            exact_kept[bucket].append(i)
            exact_seen.add(exact)
        if i in metadata:
            assert (strata, cycle, graded.split_pair(stars), graded.cells_share_two(model), len(model.chains)) == (
                row['strata'], row['route cycle'], row['split pair'], row['cells share two'], row['pendant points'],
            ), (kind, i)

    original_ids = [i for b in sorted(original_kept, key=str) for i in original_kept[b]]
    assert original_ids == [r['draw'] for r in rows if r['draw'] < draws], kind
    exact_ids = {i for kept in exact_kept.values() for i in kept}
    original_id_set = set(original_ids)
    print(json.dumps({
        'weighting': kind,
        'draws': draws,
        'tally': dict(tally),
        'eligible renaming classes': len(eligible_keys),
        'eligible hash classes': len(by_hash),
        'collision classes, representative draws': [
            list(matches.values()) for matches in by_hash.values() if len(matches) > 1
        ],
        'collision rejections with room, blocker and blocked draws': list(rejects_before_quota.values()),
        'exact kept per bucket': {str(b): len(ids) for b, ids in exact_kept.items()},
        'hash kept per bucket': {str(b): len(ids) for b, ids in original_kept.items()},
        'stored rows reproduced': len(original_ids),
        'lost by replacing hash': sorted(original_id_set - exact_ids),
        'added by replacing hash': sorted(exact_ids - original_id_set),
        'added colliding starts': [
            (i, *colliding_starts[i]) for i in sorted(exact_ids - original_id_set) if i in colliding_starts
        ],
        'CPU seconds': round(time.process_time() - started, 3),
    }), flush=True)
    return eligible_keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=int, help='maximum draws per weighting for timing')
    args = parser.parse_args()
    rows = inspect_lists()
    path = (STUDY.parents[1] / 'experiments/WEIGHTINGS-20261119-001B'
            / 'WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
    spec = importlib.util.spec_from_file_location('weightlib', path)
    weightlib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(weightlib)
    tree = replay('tree+', rows['tree+'], weightlib.sample, args.prefix)
    grow = replay('grow', rows['grow'], weightlib.sample, args.prefix)
    print(json.dumps({
        'eligible classes across both streams': len(tree.keys() | grow.keys()),
        'eligible classes present under both weightings': len(tree.keys() & grow.keys()),
    }))


if __name__ == '__main__':
    main()
