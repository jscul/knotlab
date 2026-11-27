"""Rebuild Part 3 samples and measure the effect of its two count limits."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
import math
from pathlib import Path
import random
import resource
import time

import networkx as nx

from core import Birth, Piece, _add_rank, _group_masks, _indices, build_core, read_map


STUDY = Path(__file__).resolve().parent.parent
OVER = 'unending core (over the cap of core births)'
TIMEOUT = 'not run (time limit)'
OUTSIDE = ('a piece with a cycle', 'not accepted')
LIVE_START_BUDGET = 5000
PARENT_PAIR_BUDGET = 250000


def weighted_start(kind, n, rng):
    if kind == 'grow':
        while True:
            sizes = [rng.choice((3, 4, 5))]
            loose = sizes[:]
            sharing = []
            for k in range(1, n):
                sizes.append(rng.choice((3, 4, 5)))
                loose.append(sizes[-1])
                if not any(loose[:k]):
                    break
                links = 2 if rng.random() < 1 / 3 else 1
                eligible = [i for i in range(k) if loose[i]]
                for _ in range(min(links, len(eligible))):
                    i = rng.choices(eligible, weights=[loose[a] for a in eligible])[0]
                    sharing.append((i, k))
                    eligible.remove(i)
                    loose[i] -= 1
                    loose[k] -= 1
            else:
                return sizes, sharing

    code = [rng.randrange(n) for _ in range(n - 2)]
    remaining = Counter(code)
    available = set(range(n))
    sharing = []
    for k in code:
        leaf = min(i for i in available if not remaining[i])
        sharing.append(tuple(sorted((leaf, k))))
        available.remove(leaf)
        remaining[k] -= 1
    sharing.append(tuple(sorted(available)))
    missing = [pair for pair in combinations(range(n), 2) if pair not in sharing]
    factors = 0
    product = rng.random()
    while product > math.exp(-1):
        factors += 1
        product *= rng.random()
    sharing.extend(rng.sample(missing, min(len(missing), factors)))

    neighbours = [0] * n
    for a, b in sharing:
        neighbours[a] |= 1 << b
        neighbours[b] |= 1 << a
    demand = Counter(i for group in _group_masks(n, neighbours, 100000, 2000000)
                     for i in _indices(group))
    sizes = [max(3, mask.bit_count() + demand[i]) for i, mask in enumerate(neighbours)]
    if kind == 'tree+s50':
        sizes = [size + int(rng.random() < 0.5) for size in sizes]
    return sizes, sharing


def stars_of(sizes, sharing):
    stars = [[] for _ in sizes]
    for distinction, (a, b) in enumerate(sharing):
        stars[a].append(distinction)
        stars[b].append(distinction)
    distinction = len(sharing)
    for star, size in zip(stars, sizes):
        end = distinction + size - len(star)
        star.extend(range(distinction, end))
        distinction = end
    return stars


def sample_key(sizes, sharing):
    graph = nx.Graph()
    graph.add_nodes_from((i, {'p': str(size)}) for i, size in enumerate(sizes))
    counts = Counter(tuple(sorted(pair)) for pair in sharing)
    graph.add_edges_from((a, b, {'m': str(m)}) for (a, b), m in counts.items())
    key = nx.weisfeiler_lehman_graph_hash(graph, node_attr='p', edge_attr='m', iterations=4)
    return key, graph


def maximal_candidates(neighbours):
    """Every maximal set of pairwise candidates, including singleton sets."""
    pending = [(0, (1 << len(neighbours)) - 1, 0)]
    while pending:
        chosen, remaining, excluded = pending.pop()
        if all(not remaining & ~(neighbours[i] | (1 << i)) for i in _indices(remaining)):
            if not any(remaining & ~neighbours[i] == 0 for i in _indices(excluded)):
                yield chosen | remaining
            continue
        pivot = max(_indices(remaining | excluded), key=lambda i: (neighbours[i] & remaining).bit_count())
        for i in _indices(remaining & ~neighbours[pivot]):
            bit = 1 << i
            adjacent = neighbours[i]
            pending.append((chosen | bit, remaining & adjacent, excluded & adjacent))
            remaining ^= bit
            excluded |= bit


def round_groups(parents, remaining, pair_budget):
    masks = defaultdict(int)
    for i, row in enumerate(parents):
        for p in row:
            masks[p] |= 1 << i
    pair_count = sum(math.comb(mask.bit_count(), 2) for mask in masks.values())
    detail = {'parent-pair incidences': pair_count}
    if pair_count > pair_budget:
        return (), 'parent-pair cap', detail

    neighbours = [0] * len(parents)
    for mask in masks.values():
        for i in _indices(mask):
            neighbours[i] |= mask
    for i in range(len(neighbours)):
        neighbours[i] &= ~(1 << i)

    groups = []
    covered = [0] * len(parents)
    for listed, candidate in enumerate(maximal_candidates(neighbours), 1):
        if listed > remaining:
            detail['maximal candidates lower bound'] = listed
            return (), 'maximal-candidate cap', detail
        if candidate.bit_count() >= 3:
            first = next(_indices(candidate))
            if all(candidate & ~masks[p] for p in parents[first]):
                groups.append(candidate)
                for i in _indices(candidate):
                    covered[i] |= candidate
    detail['maximal candidates'] = listed

    uncovered = [mask & ~covered[i] & ~((1 << (i + 1)) - 1)
                 for i, mask in enumerate(neighbours)]
    detail['next births'] = len(groups) + sum(mask.bit_count() for mask in uncovered)
    if detail['next births'] > remaining:
        return (), 'birth cap', detail
    for i, later in enumerate(uncovered):
        groups.extend((1 << i) | (1 << j) for j in _indices(later))
    return groups, None, detail


def twin_present(piece, rank):
    seen = set()
    for i in piece.ranks[rank]:
        parents = piece.nodes[i].parents
        if len(parents) >= 3:
            pairs = set(combinations(sorted(parents), 2))
            if seen & pairs:
                return True
            seen.update(pairs)
    return False


def guarded_piece(start, start_size, birth_budget, pair_budget):
    piece = Piece(start.points, start.chains, start.cycle)
    piece.nodes = {k: Birth(1, (), frozenset((k,))) for k in start.live}
    piece.ranks[1] = start.live
    seeds = [(group, frozenset(group)) for group in start.groups]
    seeds.extend(((k,), frozenset((k, p))) for p, k in start.attachments.items())
    rank = 2
    next_id = _add_rank(piece, rank, start_size, seeds)
    any_twins = False
    while True:
        current = piece.ranks[rank]
        remaining = birth_budget - len(piece.nodes)
        groups, stop, detail = round_groups([piece.nodes[i].parents for i in current], remaining, pair_budget)
        if stop or not groups:
            record = {'stop': stop or 'finished', 'cap checked at rank': rank,
                      'current node count': len(piece.nodes), 'counts by rank': list(map(len, piece.ranks.values())),
                      **detail}
            return piece, any_twins, record
        births = []
        for group in groups:
            parents = tuple(current[i] for i in _indices(group))
            births.append((parents, frozenset().union(*(piece.nodes[p].points for p in parents))))
        rank += 1
        next_id = _add_rank(piece, rank, next_id, births)
        any_twins = any_twins or twin_present(piece, rank)


def classify(mapped, birth_budget, pair_budget):
    # The reported classification first tests admissibility under not-all-equal.
    if mapped.status != 'in':
        return OUTSIDE[1], None
    if any(piece.cycle for piece in mapped.pieces):
        return OUTSIDE[0], None
    built = []
    for start in mapped.pieces:
        piece, twins, record = guarded_piece(start, len(mapped.sizes), birth_budget, pair_budget)
        if record['stop'] != 'finished':
            return OVER, record
        built.append((piece, twins))
    if any(piece.twin for piece, _ in built):
        return 'twins, chained', None
    presence = 'twins, not chained' if any(twins for _, twins in built) else 'no twins'
    chains = 'with chains' if any(piece.chains for piece, _ in built) else 'no chains'
    return f'{presence}, {chains}', None


def exact_match(graph, other):
    return nx.is_isomorphic(graph, other, node_match=lambda a, b: a['p'] == b['p'],
                            edge_match=lambda a, b: a['m'] == b['m'])


def replay(path, args):
    start_cpu = time.process_time()
    stored = json.loads(path.read_text())
    kind, n, seed, draws = (stored[k] for k in ('weighting', 'knots', 'seed', 'draws'))
    sample_count = min(args.limit or draws, draws)
    repeat, distinct = Counter(), Counter()
    comparison_repeat, comparison_distinct = Counter(), Counter()
    cases, cap_examples = {}, {}
    duplicates, merged = set(), []
    retained = {}
    if path.name.startswith('W1'):
        for line in (STUDY / 'twin9_draw.jsonl').read_text().splitlines():
            row = json.loads(line)
            retained[row['draw']] = row
    checked_retained = 0
    reconstructed_kept = defaultdict(list)
    rng = random.Random(seed)
    for draw in range(sample_count):
        sizes, sharing = weighted_start(kind, n, rng)
        stars = stars_of(sizes, sharing)
        mapped = read_map(stars)
        if mapped.status != 'in' or any(piece.cycle for piece in mapped.pieces):
            category, _ = classify(mapped, args.birth_budget, args.pair_budget)
            repeat[category] += 1
            continue
        key, graph = sample_key(sizes, sharing)
        if key not in cases:
            case_cpu = time.process_time()
            category, detail = classify(mapped, args.birth_budget, args.pair_budget)
            if detail:
                cap_examples[key] = {'first sample index': draw, 'repeat indices': [],
                                     'sizes': sizes, 'shared distinctions by knot pair': sharing,
                                     'stars': stars, 'first limit reached': detail,
                                     'classification cpu seconds': round(time.process_time() - case_cpu, 4)}
            compare_stop = False
            if args.compare_birth_budget:
                comparison, _ = classify(mapped, args.compare_birth_budget, args.pair_budget)
                compare_stop = comparison == OVER
                comparison_distinct[category] += int(compare_stop)
            cases[key] = category, graph, compare_stop
            distinct[category] += 1
            if category != OVER and len(reconstructed_kept[category]) < 40:
                reconstructed_kept[category].append(draw)
        else:
            category, original, compare_stop = cases[key]
            labelled = key, tuple(sizes), tuple(sorted(sharing))
            if args.verify_keys and labelled not in duplicates:
                duplicates.add(labelled)
                if not exact_match(graph, original):
                    merged.append(draw)
        if key in cap_examples:
            cap_examples[key]['repeat indices'].append(draw)
        repeat[category] += 1
        comparison_repeat[category] += int(compare_stop)
        if draw in retained:
            row = retained[draw]
            assert row['sizes'] == sizes and row['edges'] == list(map(list, sharing)) and row['stars'] == stars
            assert row['twins'] == category, (draw, row['twins'], category)
            checked_retained += 1

    cap_reasons = Counter(row['first limit reached']['stop'] for row in cap_examples.values())
    cap_reasons_repeats = Counter()
    for row in cap_examples.values():
        cap_reasons_repeats[row['first limit reached']['stop']] += len(row['repeat indices'])
    stored_distinct = Counter(stored['distinct accepted tree-piece starts drawn (new)'])
    stored_repeats = Counter(stored['accepted draws with repeats'])
    result = {'samples rebuilt': sample_count, 'stored totals': stored,
              'stored denominator with repeats': sum(v for k, v in stored_repeats.items() if k not in OUTSIDE),
              'stored distinct denominator': sum(stored_distinct.values()), 'rebuilt totals with repeats': repeat,
              'rebuilt distinct totals': distinct, 'reasons for stopping distinct starts': cap_reasons,
              'reasons for stopping samples with repeats': cap_reasons_repeats,
              'cap examples': list(cap_examples.values()), 'stored W1 samples checked': checked_retained,
              'nonisomorphic samples merged by the key': merged,
              'same-key patterns compared': len(duplicates),
              'cpu seconds': round(time.process_time() - start_cpu, 4)}
    if args.compare_birth_budget:
        result['comparison cap'] = {
            'cumulative node budget': args.compare_birth_budget,
            'parent-pair incidence budget': args.pair_budget,
            'cap hits with repeats': sum(comparison_repeat.values()),
            'distinct cap hits': sum(comparison_distinct.values()),
            'with repeats that finish under baseline guard': sum(v for k, v in comparison_repeat.items() if k != OVER),
            'distinct that finish under baseline guard': sum(v for k, v in comparison_distinct.items() if k != OVER),
        }
    if sample_count == draws:
        result['rebuilt minus stored with repeats'] = difference(repeat, stored_repeats)
        result['rebuilt minus stored distinct'] = difference(distinct, stored_distinct)
        if retained:
            expected = {draw for ids in reconstructed_kept.values() for draw in ids}
            result['W1 retained list differences'] = {'study only': sorted(retained.keys() - expected),
                                                      'replay only': sorted(expected - retained.keys())}
    return result


def difference(left, right):
    return {k: left[k] - right[k] for k in sorted(left.keys() | right.keys()) if left[k] != right[k]}


def relaxed(row, args):
    begin = time.process_time()
    result = build_core(row['stars'], max_rank=args.rank, max_births=args.relax, group_work=args.group_work)
    pieces = [{'stop': piece.stop, 'live start knots': len(piece.ranks[1]), 'births': piece.birth_count,
               'counts by rank': list(map(len, piece.ranks.values())),
               'first chained-twin rank': piece.twin_rank} for piece in result.pieces]
    return {'first sample index': row.get('first sample index'), 'pieces': pieces,
            'cpu seconds': round(time.process_time() - begin, 4)}


def common_parent_completion(piece):
    """A full rank sharing one parent starts the nonempty subset recurrence."""
    before = len(piece.ranks[1])
    for rank in sorted(piece.ranks.keys() - {1}):
        current = piece.ranks[rank]
        parent_rows = [set(piece.nodes[i].parents) for i in current]
        common = set.intersection(*parent_rows)
        if len(current) >= 2 and common:
            return {'rank': rank, 'common parent': min(common), 'parent lists':
                    {i: sorted(piece.nodes[i].parents) for i in current},
                    'total nodes including live start knots': before + (1 << len(current)) - 1,
                    'terminal rank': rank + len(current) - 1}
        before += len(current)
    return None


def period_certificate(piece):
    states = defaultdict(list)
    for rank in sorted(piece.ranks.keys() - {1}):
        current = piece.ranks[rank]
        previous = piece.ranks[rank - 1]
        if len(current) + len(previous) > 64:
            continue
        state = nx.Graph()
        state.add_nodes_from((i, {'role': 'current'}) for i in current)
        state.add_nodes_from((i, {'role': 'previous'}) for i in previous)
        state.add_edges_from((i, p) for i in current for p in piece.nodes[i].parents)
        signature = (len(current), len(previous), tuple(sorted(state.degree(i) for i in current)),
                     tuple(sorted(state.degree(i) for i in previous)))
        for earlier, old in states[signature]:
            match = nx.algorithms.isomorphism.GraphMatcher(
                old, state, node_match=lambda a, b: a['role'] == b['role'])
            if match.is_isomorphic():
                return {'matched ranks': [earlier, rank], 'renaming': match.mapping,
                        'parent lists by rank': {
                            r: {i: sorted(piece.nodes[i].parents) for i in piece.ranks[r]}
                            for r in (earlier, rank)},
                        'birth counts in one period': [len(piece.ranks[r]) for r in range(earlier, rank)]}
        states[signature].append((rank, state))
    return None


def certify(row, args):
    start_cpu = time.process_time()
    core = build_core(row['stars'], max_rank=args.rank, max_births=args.birth_budget, group_work=args.group_work)
    pieces = []
    for piece in core.pieces:
        exact = None
        if piece.finished:
            exact = {'total nodes including live start knots': len(piece.nodes),
                     'terminal rank': max(piece.ranks), 'counts by rank': [len(ids) for ids in piece.ranks.values()]}
        completion = exact or common_parent_completion(piece)
        period = period_certificate(piece) if not completion else None
        pieces.append({'independent stop': piece.stop, 'direct finish': exact,
                       'finite completion': completion, 'period certificate': period})
    return {'first sample index': row['first sample index'], 'pieces': pieces,
            'cpu seconds': round(time.process_time() - start_cpu, 4)}


def check_without_pair_guard(rows, args):
    rows = [row for row in rows if row['first limit reached']['stop'] == 'parent-pair cap']
    rows.sort(key=lambda row: row['first limit reached']['parent-pair incidences'])
    examined = []
    for row in rows:
        mapped = read_map(row['stars'])
        if any(piece.chains for piece in mapped.pieces):
            continue
        start_cpu = time.process_time()
        core = build_core(row['stars'], max_rank=args.birth_budget + 1,
                          max_births=args.birth_budget, group_work=args.group_work)
        record = {'first sample index': row['first sample index'], 'repeat sample indices': row['repeat indices'],
                  'parent-pair incidences': row['first limit reached']['parent-pair incidences'],
                  'independent stops': [piece.stop for piece in core.pieces],
                  'nodes by piece including live starts': [len(piece.nodes) for piece in core.pieces]}
        if all(piece.finished and len(piece.nodes) <= args.birth_budget for piece in core.pieces):
            category, _ = classify(mapped, args.birth_budget, math.inf)
            record['category without the pair guard'] = category
            record['counts by rank and piece'] = [list(map(len, piece.ranks.values())) for piece in core.pieces]
        record['cpu seconds'] = round(time.process_time() - start_cpu, 4)
        examined.append(record)
        if (record.get('category without the pair guard') == 'twins, not chained, no chains'
                or len(examined) == args.relax_prefix):
            break
    return examined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files', nargs='+')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--verify-keys', action='store_true')
    parser.add_argument('--birth-budget', type=int, default=LIVE_START_BUDGET)
    parser.add_argument('--pair-budget', type=int, default=PARENT_PAIR_BUDGET)
    parser.add_argument('--compare-birth-budget', type=int)
    parser.add_argument('--relax', type=int, default=0)
    parser.add_argument('--rank', type=int, default=64)
    parser.add_argument('--group-work', type=int, default=2000000)
    parser.add_argument('--relax-prefix', type=int)
    parser.add_argument('--read-replay', type=Path)
    parser.add_argument('--certify', action='store_true')
    parser.add_argument('--drop-pair-cap', action='store_true')
    parser.add_argument('--sample-indices', type=int, nargs='+')
    parser.add_argument('--compact', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    limit = 2_500_000_000
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    start = time.process_time()
    if args.read_replay:
        result = json.loads(args.read_replay.read_text())
        source = result['sample replay']
    else:
        part = STUDY / 'part3'
        files = [part / name for name in args.files] if args.files else sorted(part.glob('*.json'))
        source = {path.name: replay(path, args) for path in files}
        result = {'sample replay': source}
    selected = {
        name: [row for row in cell['cap examples'] if not args.sample_indices
               or row['first sample index'] in args.sample_indices][:args.relax_prefix]
        for name, cell in source.items() if (not args.files or name in args.files)}
    if args.certify:
        result['certificates'] = {name: [certify(row, args) for row in rows] for name, rows in selected.items()}
    if args.drop_pair_cap:
        result['pair guard removal'] = {name: check_without_pair_guard(cell['cap examples'], args)
                                        for name, cell in source.items() if (not args.files or name in args.files)}
    if args.relax:
        result['relaxed settings'] = {'rank limit': args.rank, 'new births limit': args.relax,
                                      'group search work limit': args.group_work}
        result['relaxed sample replay'] = {
            name: [relaxed(row, args) for row in rows] for name, rows in selected.items()}
        stars = [list(range(16)), [0, 1, 2]]
        fixed = {'stars': stars, 'first limit reached': classify(read_map(stars), args.birth_budget,
                                                                  args.pair_budget)[1]}
        result['finite control'] = {**fixed, **relaxed(fixed, args)}
    execution = 'supplemental execution' if args.read_replay else 'execution'
    result[execution] = {'cpu seconds': round(time.process_time() - start, 4),
                         'peak resident memory KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.compact:
        for cell in source.values():
            del cell['cap examples'], cell['stored totals']
    content = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(content + '\n')
    else:
        print(content)


if __name__ == '__main__':
    main()
