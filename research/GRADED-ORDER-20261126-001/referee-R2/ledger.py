"""Audit saved comparisons by sample, start and law without running growth."""

import argparse
import ast
from collections import Counter, defaultdict
import inspect
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys


STUDY = Path(__file__).resolve().parents[1]
FRESH = ('fresh7_treeplus', 'fresh7_grow')
HELD = ('held_treeplus', 'held_grow', 'held8_treeplus')
SAMPLES = (*FRESH, *HELD, 'replays')
LAWS = ('nae', 'parity')


def records(file, limit=None):
    with (STUDY / file).open() as stream:
        for line, raw in enumerate(stream, 1):
            if limit is not None and line > limit:
                break
            yield line, json.loads(raw)


def indexed(file, limit=None, keys=('draw', 'name')):
    rows = {}
    for line, row in records(file, limit):
        id_parts = tuple(row.get(key) for key in keys)
        assert any(part is not None for part in id_parts), (file, line)
        assert id_parts not in rows, (file, line, id_parts)
        rows[id_parts] = row
    return rows


def shape(stars):
    """Exact renaming key for starts whose distinctions each have at most two holders."""
    owners = defaultdict(list)
    for knot, distinctions in enumerate(stars):
        assert len(distinctions) == len(set(distinctions))
        for distinction in distinctions:
            owners[distinction].append(knot)
    assert all(len(knots) <= 2 for knots in owners.values()), stars
    shared = Counter(tuple(knots) for knots in owners.values() if len(knots) == 2)
    sizes = [len(distinctions) for distinctions in stars]
    groups = defaultdict(list)
    for knot, size in enumerate(sizes):
        partners = sorted((sizes[other], shared[tuple(sorted((knot, other)))])
                          for other in range(len(sizes)) if other != knot)
        groups[size, tuple(partners)].append(knot)
    orders = product(*(permutations(groups[key]) for key in sorted(groups)))
    return tuple(sorted(sizes)), min(
        tuple(shared[tuple(sorted((a, b)))] for a, b in combinations(sum(order, ()), 2))
        for order in orders
    )


def flags(row):
    return row['split pair'], row['cells share two']


def reference(sample, identity):
    if sample != 'replays':
        return identity[0]
    return next(f'replays.jsonl line {line}' for line, row in records('replays.jsonl')
                if row['name'] == identity[1])


def emit(label, counts):
    print(label)
    for key, count in sorted(counts.items(), key=lambda item: repr(item[0])):
        print(' ', count, key)


def sample_audit(samples, limit, prior):
    tally = Counter()
    joint = {}
    held_coverage = Counter()
    for sample, starts in samples.items():
        if sample != 'replays':
            emit(sample + ' (first stratum, route flag, split flag, cell flag)', Counter(
                (start['strata'][0], start['route cycle'], *flags(start))
                for start in starts.values()
            ))
        for law in LAWS:
            suffix = f'{sample}_{law}.jsonl'
            grown = indexed('grown_' + suffix, limit)
            after = indexed('nodesg_' + suffix, limit)
            before = indexed('nodes_' + suffix, limit) if sample not in HELD else {}
            graded = indexed('scored_' + suffix, limit) if sample not in HELD else {}
            assert starts.keys() == grown.keys() == after.keys(), (sample, law)
            if sample not in HELD:
                assert starts.keys() == before.keys() == graded.keys(), (sample, law)
            by_flag = Counter()
            coverage = Counter()
            changes = Counter()
            for identity, start in starts.items():
                g, result = grown[identity], after[identity]
                assert g['stars'] == start['stars'] and g['knot law'] == result['law'] == law
                assert all(g.get(key) == value for key, value in start.items())
                observed = len(g['rows'])
                end = g['end']
                if end.startswith('closes'):
                    assert int(end.rsplit(' ', 1)[1]) == observed + 1
                else:
                    assert (end == 'rounds') == (observed == 24)
                assert all(r['n'] > 0 for r in g['rows'])
                for r in g['rows']:
                    assert sum(c for _, c in r['sig0']) == sum(c for _, c in r['sig1']) == r['n']
                row = graded.get(identity)
                if row is not None:
                    rebuild = prior[sample, law, identity[0] if identity[0] is not None else identity[1]]
                    assert rebuild['observed'] == observed and rebuild['end'] == end
                    assert rebuild['first'] == [row['first differing round']] * 2
                    assert (rebuild['split'], rebuild['cells']) == flags(row)
                    assert rebuild['route'] == row['route cycle']
                graded_first = result.get('graded order') if row is None else row['first differing round']
                if 'error' in result:
                    assert 'node reading' not in result
                    node_first = result['error']
                    print('predictor error', sample, law, reference(sample, identity), end, observed, node_first)
                else:
                    assert result['rounds read'] == observed
                    assert 'node reading' in result and 'graded order' in result
                    for first in (result['node reading'], result['graded order']):
                        if isinstance(first, int):
                            assert 1 <= first <= (24 if end.startswith('closes') else observed)
                            if first > observed:
                                print('difference against predicted emptiness', sample, law, identity, first, observed)
                    node_first = result['node reading']
                    assert graded_first == result['graded order']
                flag_pair = flags(start if sample != 'replays' else row)
                if 'error' not in result:
                    assert flag_pair == flags(result), (sample, identity, law)
                if row is not None and sample != 'replays':
                    assert flags(row) == flag_pair and row['route cycle'] == start['route cycle']
                if isinstance(node_first, int):
                    print('node miss', sample, law, reference(sample, identity), node_first, observed, end)
                if sample in HELD:
                    held_coverage[law, 'closure' if end.startswith('closes') else end] += 1
                if sample != 'replays':
                    tag = 'flagged' if any(flag_pair) else 'neither'
                    tally[sample, law, tag, 'graded differs' if graded_first is not None else 'graded agrees',
                          f'node differs@{node_first}' if node_first is not None else 'node agrees'] += 1
                by_flag[flag_pair, graded_first, node_first] += 1
                coverage[any(flag_pair), end] += 1
                joint[sample, identity, law] = (graded_first, node_first, observed, end)
                if identity in before and 'error' not in before[identity]:
                    previous = before[identity]['node reading']
                    if previous != node_first:
                        changes[flag_pair, previous, node_first] += 1
            emit(f'{sample} {law} ((split flag, cell flag), first graded, first node)', by_flag)
            emit(f'{sample} {law} (flagged, end)', coverage)
            emit(f'{sample} {law} (flags, first node before group-based rank one, after)', changes)
    emit('held comparison coverage', held_coverage)
    if limit is None:
        saved = Counter()
        for line in (STUDY / 'held_tally.txt').read_text().splitlines()[:14]:
            count, key = line.split(' ', maxsplit=1)
            saved[ast.literal_eval(key)] = int(count)
        assert saved == Counter({key: n for key, n in tally.items() if key[0] in HELD})
    return joint


def witnesses(limit):
    starts = {}
    for name in ('obstruction', 'small'):
        _, row = next(records(f'referee-R1/{name}_nae.jsonl'))
        starts[name] = row['stars']
    for _, row in records('referee-R1/challenge_anchor.jsonl'):
        starts[f'challenge anchor {row["case"]}'] = row['stars']
    data = indexed('witness_nodes.jsonl', limit, keys=('witness', 'law'))
    if limit is None:
        assert data.keys() == {(name, law) for name in starts for law in LAWS}
    for (name, law), row in data.items():
        print('witness', name, len(starts[name]), law, row['rounds grown'], row['end'],
              row['graded order'], row['node reading'])
    return starts


def overlaps_and_prior(samples, witnesses_by_name, limit):
    classes = defaultdict(list)
    for sample, starts in samples.items():
        for identity, start in starts.items():
            classes[shape(start['stars'])].append((sample, identity))
    eight_knot_prior = {key for key in classes if len(key[0]) == 8}
    print('retained fresh and held renaming repetitions', [rows for rows in classes.values() if len(rows) > 1])
    blind = list(records('referee-R1/fresh_rows.jsonl', limit))
    blind_shapes = {shape(row['stars']) for _, row in blind}
    print('earlier blind rows / distinct / repeats with current eight-knot records',
          len(blind), len(blind_shapes), len(blind_shapes & eight_knot_prior))
    emit('earlier blind flagged outcomes', Counter(
        (law, bool(row['flags']['missing']), bool(row['flags']['overlap']),
         tuple(item['round'] for item in row[law]['misses'].values()), row[law]['observed'], row[law]['end'])
        for _, row in blind for law in LAWS
    ))
    emit('later twin-marked sample categories', Counter(
        row['twins'] for _, row in records('twins7_treeplus.jsonl', limit)
    ))
    result = json.loads((STUDY.parent / 'LATE-VIEWS-20261126-001/posthoc.json').read_text())
    emit('earlier fitted and tested law comparisons', Counter({
        ending: sum(n for key, n in result['tally'].items() if key.endswith(' / ' + ending))
        for ending in ('agree', 'differ')
    }))
    assert len(result['still differ']) == sum(n for key, n in result['tally'].items() if key.endswith(' / differ'))
    print('constructed witness start records', len(witnesses_by_name))


def static_audit(samples, joint):
    """Rebuild core rosters from the study's static operations, with a separate twin scan."""
    sys.path.insert(0, str(STUDY))
    import order

    checked = Counter()
    for sample, starts in samples.items():
        for identity, row in starts.items():
            if any(isinstance(joint[sample, identity, law][1], str) for law in LAWS):
                continue
            law = LAWS[0]
            source = order.late.Map(row['stars'], law)
            assert source.cls == 'in' and all(tree for _, tree, _ in source.pieces)
            order.NodePiece.round1_groups = order.late.round1(*order.late.sizes_edges(row['stars']))[4]
            ranks = set()
            for points, _, _ in source.pieces:
                core = order.NodePiece(points, source.adj, source.chains, lambda v: v < source.n,
                                       None, lambda v: 1, source.cells)
                groups = Counter()
                for birth, parents in core.core_parents.items():
                    for c, d in combinations(sorted(parents), 2):
                        groups[(core.sizes_of[birth] - 1, c, d)] += 1
                for (rank, c, d), count in groups.items():
                    common = core.core_parents[c] & core.core_parents[d]
                    if count >= 2 and any(source.chains.get(v, 0)
                                          for grandparent in common for v in core.points_of[grandparent]):
                        ranks.add(rank)
            checked['completed starts'] += 1
            if ranks:
                checked['starts with the twin condition'] += 1
                print('twins with a chain at a common grandparent', sample, reference(sample, identity), sorted(ranks),
                      [joint[sample, identity, law][1] for law in LAWS])
            if sample in FRESH:
                # check_start deliberately starts at rank 1 and skips the last rank.
                rank_checks = order.check_start(row['stars'], law)
                first = min((rank for rank, equal in rank_checks if not equal), default=None)
                checked['first static difference', flags(row), first] += 1
    emit('static audit', checked)


def relay_variants(samples, limit):
    """Test relay choices on the saved not-all-equal growth."""
    import order

    source = inspect.getsource(order.predict_nodes)
    terminal_filter = ' and not P.children[n]'
    unique_check = "        if relay and len(tops) != 1: return None, 'not one last birth holding the whole piece'\n"
    assert source.count(terminal_filter) == source.count(unique_check) == 1
    alternatives = {
        'one terminal whole-piece node': source,
        'all whole-piece nodes': source.replace(terminal_filter, '').replace(unique_check, ''),
        'all terminal whole-piece nodes': source.replace(unique_check, ''),
        'one whole-piece node, omit relay when multiple': source.replace(terminal_filter, '').replace(
            unique_check, '        if len(tops) != 1: tops = []\n'),
        'all latest-rank whole-piece nodes': source.replace(terminal_filter, '').replace(
            unique_check, '        if tops:\n'
                          '            latest = max(P.sizes_of[n] for n in tops)\n'
                          '            tops = [n for n in tops if P.sizes_of[n] == latest]\n'),
    }
    predictors = {}
    for name, variant in alternatives.items():
        context = dict(vars(order))
        exec(variant, context)
        predictors[name] = context['predict_nodes']
    outcomes = Counter()
    for sample in FRESH:
        for identity, grown in indexed(f'grown_{sample}_nae.jsonl', limit).items():
            assert identity in samples[sample]
            for groups in (False, True):
                for name, predict in predictors.items():
                    prediction, why = predict(grown['stars'], 24, 'nae', groups)
                    first = order.score.compare(prediction, grown) if prediction is not None else why
                    outcomes[name, sample, groups, first] += 1
    emit('relay variants (choice, sample, group-based rank one, first difference)', outcomes)


def main(limit):
    samples = {sample: indexed(sample + '.jsonl', limit) for sample in SAMPLES}
    prior = indexed('referee-R1/record_audit.jsonl', keys=('source', 'law', 'sample'))
    joint = sample_audit(samples, limit, prior)
    overlaps_and_prior(samples, witnesses(limit), limit)
    static_audit(samples, joint)
    relay_variants(samples, limit)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='Read this many initial rows per sample and law for timing.')
    main(parser.parse_args().limit)
