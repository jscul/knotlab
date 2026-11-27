"""Audit saved starts, draw order, and equality under renaming.

Run from the repository with .venv/bin/python -B. The draw prefix applies
separately to each weighting. The audit writes JSON to standard output.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from itertools import combinations
import json
from math import comb, exp
from pathlib import Path
from random import Random
from time import process_time

from core import read_map

HERE = Path(__file__).resolve().parent.parent
LATE = HERE.parent / 'LATE-VIEWS-20261126-001'
GRADED = HERE.parent / 'GRADED-ORDER-20261126-001'
SAMPLES = {
    'cyc6_uniform': 'cyc6_uniform.jsonl',
    'cyc7_treeplus': 'cyc7_treeplus.jsonl',
    'cyc7_grow': 'cyc7_grow.jsonl',
    'twin9': 'twin9_draw.jsonl',
    'twin8': 'twin8_draw.jsonl',
}
TWIN_NAMES = {'twin9': 'W1 tree+ nine knots', 'twin8': 'W2 tree+s50 eight knots'}
PRIOR = {
    LATE: ('held_out_nae.jsonl.gz', 'grown_grow7_nae.jsonl.gz', 'stratified.jsonl',
           'handbuilt.jsonl', 'horizon.jsonl'),
    GRADED: ('fresh7_treeplus.jsonl', 'fresh7_grow.jsonl', 'held_treeplus.jsonl',
             'held_grow.jsonl', 'held8_treeplus.jsonl', 'replays.jsonl',
             'twins7_treeplus.jsonl', 'referee-R1/fresh_rows.jsonl',
             'referee-R1/small_nae.jsonl', 'referee-R1/obstruction_nae.jsonl',
             'referee-R1/challenge_anchor.jsonl', 'referee-R2/draws.jsonl'),
}
CAP = 5000
PAIRS = 250_000
CORE_WORK = 2_000_000


def rows(path):
    reader = gzip.open if path.suffix == '.gz' else open
    with reader(path, 'rt') as source:
        yield from map(json.loads, source)


def draw_id(row):
    return row.get('draw', row.get('index'))


def start_of(sizes, pairs):
    stars = [[] for _ in sizes]
    for distinction, (a, b) in enumerate(pairs):
        stars[a].append(distinction)
        stars[b].append(distinction)
    distinction = len(pairs)
    for star, size in zip(stars, sizes, strict=True):
        loose = size - len(star)
        assert loose >= 0
        star.extend(range(distinction, distinction + loose))
        distinction += loose
    return stars


def holders(stars):
    owners = defaultdict(list)
    for k, star in enumerate(stars):
        assert len(star) == len(set(star))
        for distinction in star:
            owners[distinction].append(k)
    return owners.values()


@dataclass
class Pattern:
    colors: tuple
    mult: list
    signature: tuple


def pattern(stars):
    """Encode a colored multigraph from the incidence of shared distinctions."""
    sizes = list(map(len, stars))
    mult = [[0] * len(sizes) for _ in sizes]
    loose = [0] * len(sizes)
    for owner in holders(stars):
        assert 1 <= len(owner) <= 2
        if len(owner) == 1:
            loose[owner[0]] += 1
        else:
            a, b = owner
            mult[a][b] += 1
            mult[b][a] += 1
    colors = tuple((loose[k], tuple(sorted((sizes[j], m) for j, m in enumerate(line) if m)))
                   for k, line in enumerate(mult))
    return Pattern(colors, mult, tuple(sorted(colors)))


def renaming(a, b):
    """Return an exact bijection of knots or None. The signature only screens."""
    if a.signature != b.signature:
        return None
    candidates = [[j for j, right in enumerate(b.colors) if right == left]
                  for left in a.colors]
    ordering = sorted(range(len(candidates)), key=lambda i: (len(candidates[i]), -sum(a.mult[i])))
    assigned = {}

    def visit(depth, available):
        if depth == len(ordering):
            return dict(sorted(assigned.items()))
        k = ordering[depth]
        for j in candidates[k]:
            if j in available and all(a.mult[k][q] == b.mult[j][r] for q, r in assigned.items()):
                assigned[k] = j
                result = visit(depth + 1, available - {j})
                if result is not None:
                    return result
                del assigned[k]
        return None

    return visit(0, set(ordering))


class Index:
    def __init__(self):
        self.buckets = defaultdict(list)

    def matches(self, source):
        for target, record in self.buckets.get(source.signature, ()):
            mapping = renaming(source, target)
            if mapping is not None:
                yield record, list(mapping.values())

    def add(self, source, record):
        self.buckets[source.signature].append((source, record))


def replay_construction(families, opens):
    """Read the earlier seeded construction from its saved families and loose counts."""
    n = len(opens)
    pairs = [(k, n + j) for j, family in enumerate(families) for k in family]
    pairs.extend((n + j, n + j + 1) for j in range(len(families) - 1))
    count = n + len(families)
    if len(families) == 1:
        pairs.extend([(n, n + 1)] * 3)
        count += 1
    sizes = list(opens) + [0] * (count - n)
    for a, b in pairs:
        sizes[a] += 1
        sizes[b] += 1
    for j, family in enumerate(families):
        k = family[0]
        while sizes[n + j] < 3:
            pairs.append((k, n + j))
            sizes[k] += 1
            sizes[n + j] += 1
    for k in range(n):
        j = next(n + j for j, family in enumerate(families) if k in family)
        while sizes[k] < 3:
            pairs.append((k, j))
            sizes[k] += 1
            sizes[j] += 1
    while len(sizes) < 8:
        pairs.extend([(n, len(sizes))] * 3)
        sizes[n] += 3
        sizes.append(3)
    return start_of(sizes, pairs)


def earlier_records():
    index = Index()
    for directory, filenames in PRIOR.items():
        for name in filenames:
            for line, row in enumerate(rows(directory / name), 1):
                stars = row.get('stars')
                if stars is None and name == 'referee-R2/draws.jsonl':
                    stars = replay_construction(row['families'], row['opens'])
                    assert len(stars) == row['knots']
                if stars is not None:
                    reference = {'file': f'{directory.name}/{name}', 'line': line,
                                 'id': draw_id(row), 'name': row.get('name')}
                    index.add(pattern(stars), reference)
    return index


def compare_samples(samples, prior):
    index = Index()
    within = defaultdict(list)
    across = []
    predecessors = []
    for name, sample in samples.items():
        for line, row in enumerate(sample, 1):
            mark = [name, line, draw_id(row)]
            shape = pattern(row['stars'])
            for other, mapping in index.matches(shape):
                if name == other[0]:
                    within[name].append([mark, other, mapping])
                else:
                    across.append([mark, other, mapping])
            index.add(shape, mark)
            for other, mapping in prior.matches(shape):
                predecessors.append([mark, other, mapping])
    return {'within': within, 'across': across, 'earlier': predecessors}


def evidence_joins(samples):
    strata = {}
    with (HERE / 'strata.txt').open() as source:
        for line in source:
            if line.startswith('{'):
                x = json.loads(line)
                strata[x['file'], x['line']] = x
    scores = {x: list(rows(HERE / name)) for x, name in
              ((False, 'scores.jsonl'), (True, 'scores2.jsonl'))}
    report = {}
    for name, sample in samples.items():
        label = SAMPLES[name]
        by_id = {draw_id(row): row for row in sample}
        assert len(by_id) == len(sample)
        for law in ('nae', 'parity'):
            grew = list(rows(HERE / f'grown_{name}_{law}.jsonl.gz'))
            predicted = list(rows(HERE / f'nodes_{name}_{law}.jsonl'))
            selected = [x for x in scores[name in TWIN_NAMES] if x['law'] == law and
                        (x['weighting'] == TWIN_NAMES[name] if name in TWIN_NAMES else x['file'] == label)]
            scored = {draw_id(row): row for row in selected}
            n = len(sample)
            assert len(grew) == len(predicted) == len(selected) == len(scored) == n
            assert {draw_id(row) for row in grew} == by_id.keys() == scored.keys()
            mismatch = []
            anonymous = 0
            for position, (growth, prediction) in enumerate(zip(grew, predicted, strict=True), 1):
                identity = draw_id(growth)
                row = by_id[identity]
                score = scored[identity]
                assert all(growth.get(field) == value for field, value in row.items())
                assert growth['knot law'] == prediction['law'] == score['law'] == law
                if prediction['draw'] is None:
                    anonymous += 1
                elif prediction['draw'] != identity:
                    mismatch.append(identity)
                if 'rounds read' in prediction:
                    assert prediction['rounds read'] == len(growth['rows']) == score['rounds read']
                if name in TWIN_NAMES:
                    assert score['bucket'] == row['twins']
                else:
                    entry = strata[label, score['line']]
                    assert entry['draw'] == identity and entry['twins'] == score['twins']
                    assert sample[score['line'] - 1] == row
            report[f'{name}/{law}'] = {'rows': n, 'prediction_rows_without_start_id': anonymous,
                                      'prediction_key_mismatches': mismatch,
                                      'growth_order_matches_saved_start_order': [
                                          draw_id(g) for g in grew] == list(by_id),
                                      'endings': Counter(g['end'].split(' at round')[0] for g in grew),
                                      'time_limits': [draw_id(g) for g in grew
                                                      if g['end'] == 'not run (time limit)']}
    return report


def uniform_reuse(saved):
    """Replay the three seeded draws over the documented atlas census index range."""
    remaining = list(range(82_656))
    for seed, number in ((20261126, 1000), (20261127, 2000)):
        selected = set(Random(seed).sample(remaining, number))
        remaining = [i for i in remaining if i not in selected]
    expected = Random(20261128).sample(remaining, 2000)
    result = {}
    for law in ('nae', 'parity'):
        source = list(rows(LATE / f'held_out_{law}.jsonl.gz'))
        selected = []
        for row in source:
            mapped = read_map(row['stars'])
            if mapped.status == 'in' and any(p.cycle for p in mapped.pieces):
                selected.append(row)
        assert expected == [x['index'] for x in source]
        assert saved == [{k: row[k] for k in ('index', 'stars')} for row in selected]
        assert selected == list(rows(HERE / f'grown_cyc6_uniform_{law}.jsonl.gz'))
        result[law] = {'matching_seeded_indices': len(source),
                       'matching_selected_starts_and_growth_rows': len(selected)}
    return result


def earlier_grow_reuse(sample):
    report = {}
    for law in ('nae', 'parity'):
        previous = {row['index']: row for row in rows(LATE / f'grown_grow7_{law}.jsonl.gz')}
        current = {row['draw']: row for row in rows(HERE / f'grown_cyc7_grow_{law}.jsonl.gz')}
        reused = sorted({row['draw'] for row in sample} & previous.keys())
        for i in reused:
            for field in ('stars', 'sizes', 'edges', 'rows', 'end', 'knots', 'knot law', 'kind'):
                assert current[i][field] == previous[i][field]
        report[law] = reused
    return report


def grow_weight(n, rng):
    sizes = [rng.choice((3, 4, 5))]
    free = sizes.copy()
    pairs = []
    for k in range(1, n):
        size = rng.choice((3, 4, 5))
        sizes.append(size)
        free.append(size)
        available = [i for i in range(k) if free[i] > 0]
        if not available:
            return grow_weight(n, rng)
        links = 2 if rng.random() < 1 / 3 else 1
        for _ in range(min(links, len(available))):
            j = rng.choices(available, weights=[free[i] for i in available])[0]
            available.remove(j)
            pairs.append((j, k))
            free[j] -= 1
            free[k] -= 1
    return sizes, pairs


def tree_weight(n, rng, scaffold):
    code = [rng.randrange(n) for _ in range(n - 2)]
    degree = [1 + code.count(k) for k in range(n)]
    pairs = []
    for k in code:
        leaf = degree.index(1)
        pairs.append(tuple(sorted((k, leaf))))
        degree[leaf] -= 1
        degree[k] -= 1
    pairs.append(tuple(k for k, d in enumerate(degree) if d))
    candidates = [pair for pair in combinations(range(n), 2) if pair not in pairs]
    product = 1
    extras = 0
    while (product := product * rng.random()) > exp(-1):
        extras += 1
    pairs.extend(rng.sample(candidates, min(extras, len(candidates))))
    shared = Counter(k for pair in pairs for k in pair)
    all_live = start_of([shared[k] + 1 for k in range(n)], pairs)
    demand = Counter(k for piece in read_map(all_live).pieces for group in piece.groups for k in group)
    sizes = [max(3, shared[k] + demand[k]) for k in range(n)]
    if scaffold:
        sizes = [size + (rng.random() < 0.5) for size in sizes]
    return sizes, pairs


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class CoreWorkLimit(Exception):
    pass


def maximal_families(neighbours, work_limit):
    """Enumerate maximal cliques, including the common-parent and singleton cases."""
    pending = [(0, (1 << len(neighbours)) - 1, 0)]
    work = 0
    while pending:
        chosen, possible, excluded = pending.pop()
        if not (possible or excluded):
            yield chosen
        if not possible:
            continue
        if possible.bit_count() >= 8 and all(
            possible & ~neighbours[k] == 1 << k for k in bits(possible)
        ):
            if not any(possible & ~neighbours[k] == 0 for k in bits(excluded)):
                yield chosen | possible
            continue
        pivot_set = possible | excluded
        work += pivot_set.bit_count()
        if work > work_limit:
            raise CoreWorkLimit
        pivot = max(bits(pivot_set), key=lambda k: (possible & neighbours[k]).bit_count())
        for k in bits(possible & ~neighbours[pivot]):
            bit = 1 << k
            pending.append((chosen | bit, possible & neighbours[k], excluded & neighbours[k]))
            possible ^= bit
            excluded |= bit


def next_families(layer, parents, budget, pair_cap, work_limit):
    holders = defaultdict(int)
    for i, birth in enumerate(layer):
        for parent in parents[birth]:
            holders[parent] |= 1 << i
    blocks = set(holders.values())
    if pair_cap is not None and sum(comb(mask.bit_count(), 2) for mask in holders.values()) > pair_cap:
        return None, 'pair cap'
    adjacent = [0] * len(layer)
    for block in blocks:
        for i in bits(block):
            adjacent[i] |= block ^ (1 << i)
    if len(layer) >= 80 and budget >= 0:
        # Distinct maximal families in any induced restriction extend to
        # distinct maximal families in the whole. A small restriction can
        # certify the count stop without building the larger search.
        sample_rng = Random(1417)
        for count in (40, 60, 80):
            selected = sorted(sample_rng.sample(range(len(layer)), count))
            sampled = [sum(1 << j for j, k in enumerate(selected) if adjacent[i] & (1 << k))
                       for i in selected]
            try:
                if any(k > budget for k, _ in enumerate(maximal_families(sampled, work_limit), 1)):
                    return None, 'maximal families cap'
            except CoreWorkLimit:
                pass
    covered = [0] * len(layer)
    groups = []
    for count, group in enumerate(maximal_families(adjacent, work_limit), 1):
        if count > budget:
            return None, 'maximal families cap'
        if group.bit_count() >= 3 and group not in blocks:
            groups.append(group)
            for i in bits(group):
                covered[i] |= group
    for i, other in enumerate(adjacent):
        uncovered = other & ~covered[i] & ~((1 << (i + 1)) - 1)
        if len(groups) + uncovered.bit_count() > budget:
            return None, 'core births cap'
        groups.extend((1 << i) | (1 << j) for j in bits(uncovered))
    return [tuple(layer[i] for i in bits(group)) for group in groups], None


def twin_bucket(mapped, pair_cap, work_limit=CORE_WORK):
    any_twin = False
    any_chained = False
    for piece in mapped.pieces:
        born_to = {i: () for i in piece.live}
        has_base = dict.fromkeys(piece.live, False)
        conditions = [(tuple(g), False) for g in piece.groups]
        conditions.extend(((parent,), pendant in piece.chains) for pendant, parent in piece.attachments.items())
        identity = max(piece.live) + 1
        first_round = True
        while conditions:
            layer = []
            for parents, based in conditions:
                born_to[identity] = parents
                has_base[identity] = based or any(has_base[p] for p in parents)
                layer.append(identity)
                identity += 1
            budget = CAP - len(born_to)
            try:
                result, cap = next_families(layer, born_to, budget, pair_cap, work_limit)
            except CoreWorkLimit:
                return 'work limit'
            if cap:
                return cap
            # The frozen bucket convention skips first-round births. In later
            # rounds an uncovered parent pair cannot be twins of another birth.
            if not first_round and not any_chained:
                pair_seen = set()
                for parents, _ in conditions:
                    if len(parents) >= 3:
                        for a, b in combinations(parents, 2):
                            if (a, b) in pair_seen:
                                any_twin = True
                                if any(has_base[g] for g in set(born_to[a]).intersection(born_to[b])):
                                    any_chained = True
                            pair_seen.add((a, b))
            first_round = False
            conditions = [(group, False) for group in result]
    if any_chained:
        return 'twins, chained'
    twin = 'twins, not chained' if any_twin else 'no twins'
    return twin + (', with chains' if any(p.chains for p in mapped.pieces) else ', no chains')


def cap_for_draw_1990(sample):
    selected = next(row for row in sample if row['draw'] == 1990)
    mapped = read_map(selected['stars'])
    return {'draw': 1990, 'knots': len(selected['stars']), 'weighting': selected['weighting'],
            'without_pair_cap': twin_bucket(mapped, None), 'with_pair_cap': twin_bucket(mapped, PAIRS)}


def replay_draws(name, sample, prior, prefix):
    settings = {'cyc7_treeplus': ('tree+', 7, 20_000, 20261129),
                'cyc7_grow': ('grow', 7, 200_000, 20261129),
                'twin9': ('tree+', 9, 20_000, 20261130),
                'twin8': ('tree+s50', 8, 6_000, 20261131)}
    kind, n, draws, seed = settings[name]
    rng = Random(seed)
    stop = draws if prefix is None else min(draws, prefix)
    targets = {row['draw']: row for row in sample if row['draw'] < stop}
    twin = name in TWIN_NAMES
    kept = defaultdict(list)
    accepted = Counter()
    distinct = Counter()
    new = Counter()
    unmatched = {}
    wrong_buckets = {}
    indexed = Index()
    repeated = {}
    earlier_exclusions = {}
    suspect = []
    per = 40 if twin else 50
    pair_cap = None if name == 'twin8' else PAIRS
    for i in range(stop):
        sizes, pairs = grow_weight(n, rng) if kind == 'grow' else tree_weight(n, rng, kind == 'tree+s50')
        stars = start_of(sizes, pairs)
        target = targets.get(i)
        if target is not None:
            assert target['sizes'] == sizes and target['edges'] == [list(p) for p in pairs], (name, i)
            assert target['stars'] == stars and target['weighting'] == kind, (name, i)
        mapped = read_map(stars)
        cycles = [piece for piece in mapped.pieces if piece.cycle]
        if mapped.status != 'in' or twin == bool(cycles):
            accepted['rejected by map' if mapped.status != 'in' else 'wrong cycle eligibility'] += 1
            assert target is None
            continue
        shape = pattern(stars)
        previous = next(indexed.matches(shape), None)
        if previous is not None:
            (key, first_draw), _ = previous
            accepted[key] += 1
            if target is not None:
                repeated[i] = first_draw
            continue
        if twin:
            key = twin_bucket(mapped, pair_cap)
        else:
            key = str((len(cycles), any(piece.chains for piece in cycles)))
        single = {'pair cap', 'maximal families cap', 'core births cap', 'work limit'}
        indexed.add(shape, (key, i))
        accepted[key] += 1
        distinct[key] += 1
        prior_match = next(prior.matches(shape), None) if twin else None
        old = prior_match is not None
        if old:
            earlier_exclusions[i] = [key, *prior_match]
        if not old:
            new[key] += 1
        if target is not None:
            expected = target['twins'] if twin else str(
                (target['pieces with a cycle'], target['chains on a cycle piece']))
            if key != expected or old:
                wrong_buckets[i] = [key, expected, old]
        if key == 'work limit':
            suspect.append(i)
        if not old and key not in single and len(kept[key]) < per:
            kept[key].append(i)
            if target is None:
                unmatched[i] = key
    simulated = {i for selections in kept.values() for i in selections}
    return {'weighting': kind, 'knots': n, 'draws_run': stop, 'declared_draws': draws,
            'seed': seed, 'matching_saved_raw_draws': len(targets), 'pair_cap': pair_cap if twin else None,
            'raw_counts': accepted, 'exact_distinct_counts': distinct, 'exact_new_counts': new,
            'earlier_exclusions': earlier_exclusions,
            'retained': {key: len(draws) for key, draws in kept.items()},
            'retention_differences': {'replay_only': unmatched,
                                      'saved_only': sorted(targets.keys() - simulated),
                                      'saved_repeats': repeated, 'saved_bucket_differences': wrong_buckets},
            'work_limited_first_draws': suspect}


def check_renaming():
    first = [[0, 1, 2, 3], [0, 1, 4], [2, 5, 6]]
    second = [[50, 20, 60], [40, 10, 30], [30, 10, 20, 70]]
    assert renaming(pattern(first), pattern(second)) == {0: 2, 1: 1, 2: 0}
    cycle = start_of([3] * 6, [(a, (a + 1) % 6) for a in range(6)])
    split = start_of([3] * 6, [(a, 3 * (a // 3) + ((a + 1) % 3)) for a in range(6)])
    assert pattern(cycle).signature == pattern(split).signature
    assert renaming(pattern(cycle), pattern(split)) is None


def refine_scaffold_replay(output, limit, work_limit):
    baseline = output['generator_replays']['twin8']
    wanted = baseline['work_limited_first_draws'][:limit]
    if not wanted:
        return
    rng = Random(baseline['seed'])
    outcomes = {}
    t = process_time()
    for i in range(wanted[-1] + 1):
        sizes, pairs = tree_weight(baseline['knots'], rng, True)
        if i in wanted:
            outcomes[i] = twin_bucket(read_map(start_of(sizes, pairs)), None, work_limit)
    output['W2_cap_refinement'] = {'cpu_seconds': round(process_time() - t, 3),
                                   'work_limit': work_limit, 'rechecked_draws': outcomes,
                                   'other_work_limited_draws_not_rechecked': [
                                       i for i in baseline['work_limited_first_draws'] if i not in outcomes]}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--draw-prefix', type=int)
    cli.add_argument('--refine-scaffold', type=Path)
    cli.add_argument('--refine-prefix', type=int)
    cli.add_argument('--refine-work', type=int, default=5_000_000)
    args = cli.parse_args()
    if args.refine_scaffold:
        output = json.loads(args.refine_scaffold.read_text())
        refine_scaffold_replay(output, args.refine_prefix, args.refine_work)
        print(json.dumps(output, indent=2, sort_keys=True))
        return
    check_renaming()
    started = process_time()
    prior = earlier_records()
    samples = {name: list(rows(HERE / file)) for name, file in SAMPLES.items()}
    output = {'earlier_rows': Counter(record['file'] for entries in prior.buckets.values()
                                      for _, record in entries),
              'sample_rows': {name: len(sample) for name, sample in samples.items()},
              'record_joins': evidence_joins(samples),
              'sample_comparisons': compare_samples(samples, prior),
              'uniform_reuse': uniform_reuse(samples['cyc6_uniform']),
              'grow_reuse': earlier_grow_reuse(samples['cyc7_grow']),
              'W2_draw_1990_cap_control': cap_for_draw_1990(samples['twin8']),
              'retained_twin_buckets': {name: Counter(r['twins'] for r in samples[name])
                                        for name in TWIN_NAMES},
              'W1_saved_tally': next(rows(HERE / 'part3' / 'W1_tree+_9_seed20261130.json')),
              'part3_saved_tallies': sorted(p.name for p in (HERE / 'part3').glob('*.json'))}
    output['artifact_cpu_seconds'] = round(process_time() - started, 3)
    output['audit_caps'] = {'maximal_family_work_per_search': CORE_WORK,
                            'core_count': CAP, 'parent_sharing_pairs': PAIRS}
    output['generator_replays'] = {}
    for name in ('cyc7_treeplus', 'cyc7_grow', 'twin9', 'twin8'):
        started = process_time()
        output['generator_replays'][name] = replay_draws(name, samples[name], prior, args.draw_prefix)
        output['generator_replays'][name]['cpu_seconds'] = round(process_time() - started, 3)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
