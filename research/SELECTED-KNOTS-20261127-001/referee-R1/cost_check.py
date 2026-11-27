"""Independent replay of ordinary parity growth, family costs and shortest changes.

Only published starts and comparison data are read. A pilot uses the same
algorithms, caps and resource limit as the complete check. Run from any directory.
"""

import argparse
import hashlib
import json
import random
import resource
import time
from collections import Counter, deque
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
OLD = RESEARCH / 'BUILT-BINDING-20261126-001'
FROZEN_LAST = 4
LATER_LAST = 7
CAP = 512


def read_lines(path):
    with path.open() as records:
        for line in records:
            yield json.loads(line)


def reach(adjacency, origins):
    distance = [-1] * len(adjacency)
    queue = list(origins)
    for u in queue:
        distance[u] = 0
    for u in queue:
        for v in adjacency[u]:
            if distance[v] == -1:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def supports(n, shared, loose):
    rows = [[] for _ in range(n)]
    x = 0
    for a, b, count in shared:
        for _ in range(count):
            rows[a].append(x)
            rows[b].append(x)
            x += 1
    for k, count in enumerate(loose):
        rows[k].extend(range(x, x + count))
        x += count
    return rows


def labelled_starts(n, count, seed, probability, maximum):
    rng = random.Random(seed)
    possible = list(combinations(range(n), 2))
    seen = 0
    while seen < count:
        pairs = [pair for pair in possible if rng.random() < probability]
        weighted = [(a, b, rng.choice((1, 2))) for a, b in pairs]
        loose = [rng.choice((0, 1, 2)) for _ in range(n)]
        if sum(loose) + sum(x[2] for x in weighted) > maximum:
            continue
        degree = loose.copy()
        adj = [[] for _ in range(n)]
        for u, v, k in weighted:
            degree[u] += k
            degree[v] += k
            adj[u].append(v)
            adj[v].append(u)
        if min(degree) >= 3 and -1 not in reach(adj, [0]):
            yield supports(n, weighted, loose)
            seen += 1


def rings(count, size, attach, link):
    rows = [[] for _ in range(count * size)]
    name = 0

    def add(*holders):
        nonlocal name
        for k in holders:
            rows[k].append(name)
        name += 1

    for first in range(0, len(rows), size):
        for i in range(size):
            add(first + i, first + (i + 1) % size)
    for i in range(len(rows)):
        add(i)
        add(i)
    ports = [0] * count
    for a, b in combinations(range(count), 2):
        left, right = len(rows), len(rows) + 1
        rows.extend([[], []])
        for ring, outside in [(a, left), (b, right)]:
            loc = ports[ring]
            ports[ring] += 1
            positions = (loc, loc + 2) if attach == 'split' else (2 * loc, 2 * loc)
            for pos in positions:
                add(ring * size + pos % size, outside)
        add(left, right)
        if link == 'double':
            add(left, right)
        else:
            previous = left
            for _ in range(3):
                middle = len(rows)
                rows.append([])
                add(previous, middle)
                add(previous, middle)
                previous = middle
            add(previous, right)
            add(previous, right)
    return rows


def fourteen():
    # Three four-knot rings between two common knots, two loose distinctions
    # on opposite holders of each ring. Distinction names are free to permute.
    shared = []
    for first in (0, 4, 8):
        shared.extend((first + j, first + (j + 1) % 4, 1) for j in range(4))
        shared.extend([(first, 12, 1), (first + 2, 13, 1)])
    shared.append((12, 13, 1))
    return supports(14, shared, [0, 2, 0, 2] * 3 + [0, 0])


def cases(roster, pilot):
    if roster == 'census':
        catalogue = json.loads((RESEARCH / 'FORBID-EDITS-20261126-001/starts.json').read_text())
        selected = random.Random(20261215).sample(range(len(catalogue)), 1000)
        for i in selected[:12 if pilot else None]:
            yield 'census %d' % i, supports(*catalogue[i])
    elif roster in ('heldout', 'sampled', 'larger sampled'):
        if roster == 'heldout':
            config = [(n, 300, 20261206 + n, 1 / 3, 18) for n in (6, 7, 8)]
        elif roster == 'sampled':
            config = [(n, 100, 20261212 + n, 1 / 3, 30) for n in (9, 10, 11, 12)]
        else:
            config = [(n, 48, 1601127 + n, 3 / (n - 1), 3 * n + 2) for n in (13, 16, 20)]
        for n, total, seed, chance, maximum in config:
            prefix = min(3, total) if pilot else total
            for i, rows in enumerate(labelled_starts(n, prefix, seed, chance, maximum)):
                name = 'held out' if roster == 'heldout' else roster
                yield '%s %d-%d' % (name, n, i), rows
    else:
        sizes = product((3, 4), (4, 5, 6, 7), ('split', 'paired'), ('double', 'detour'))
        if roster == 'larger built':
            sizes = product((5, 6), (4, 5), ('split',), ('double',))
        for count, size, attach, link in sizes:
            if pilot and not (size == 4 and attach == 'split' and link == 'double'):
                continue
            yield f'{count} rings of {size}, {attach}, {link}', rings(count, size, attach, link)
        if roster == 'built':
            yield 'the 14-knot start', fourteen()


class Stage:
    def __init__(self, rows):
        self.rows = rows
        n = len(rows)
        self.owners = [[] for _ in range(1 + max(x for row in rows for x in row))]
        for k, row in enumerate(rows):
            for x in row:
                self.owners[x].append(k)
        self.near = [set() for _ in range(n)]
        self.loose = [[] for _ in range(n)]
        for x, holders in enumerate(self.owners):
            if len(holders) == 2:
                a, b = holders
                assert a != b
                self.near[a].add(b)
                self.near[b].add(a)
            else:
                assert len(holders) == 1
                self.loose[holders[0]].append(x)

    def live(self):
        return [i for i, loose in enumerate(self.loose) if loose]


def candidate_lists(near, live):
    live = set(live)
    adjacent = {u: set() for u in live}
    for meeting in near:
        for u, v in combinations(meeting & live, 2):
            adjacent[u].add(v)
            adjacent[v].add(u)
    return adjacent


def groups(near, live):
    adjacent = candidate_lists(near, live)
    larger = []

    def visit(chosen, pending, done):
        if not pending:
            if not done and len(chosen) > 2 and not set.intersection(*(near[u] for u in chosen)):
                larger.append(tuple(sorted(chosen)))
            return
        pivot = max(pending | done, key=lambda v: len(adjacent[v] & pending))
        for v in sorted(pending - adjacent[pivot]):
            visit(chosen + [v], pending & adjacent[v], done & adjacent[v])
            pending.remove(v)
            done.add(v)

    visit([], set(adjacent), set())
    covered = {pair for large in larger for pair in combinations(large, 2)}
    small = [(u, v) for u, vs in adjacent.items() for v in vs if u < v and (u, v) not in covered]
    return sorted(larger) + sorted(small)


def starting_families(stage):
    adjacent = candidate_lists(stage.near, stage.live())
    left = set(adjacent)
    labels = [-1] * len(stage.rows)
    parts = []
    while left:
        seed = min(left)
        left.remove(seed)
        members = [seed]
        for u in members:
            following = adjacent[u] & left
            members.extend(following)
            left.difference_update(following)
        for u in members:
            labels[u] = len(parts)
        parts.append(sorted(members))
    return parts, labels


def grow(stage, labels):
    live = stage.live()
    if not live:
        return None, labels, 'closed', []
    planned = groups(stage.near, live)
    uses = Counter(k for group in planned for k in group)
    if any(uses[k] > len(stage.loose[k]) for k in live):
        return None, labels, 'stalled', []
    for k in live:
        planned.extend([(k,)] * (len(stage.loose[k]) - uses[k]))
    loose = [deque(xs) for xs in stage.loose]
    rows = [row.copy() for row in stage.rows]
    adjacency = [vs.copy() for vs in stage.near]
    base = len(rows)
    next_labels = labels.copy()
    for parents in planned:
        family = {labels[k] for k in parents}
        assert len(family) == 1 and -1 not in family
        next_labels.append(family.pop())
        k = len(rows)
        for p in parents:
            adjacency[p].add(k)
        adjacency.append(set(parents))
        rows.append([loose[p].popleft() for p in parents])
    demand = Counter(k for g in groups(adjacency, range(base, len(rows))) for k in g)
    next_name = len(stage.owners)
    births = []
    for i, parents in enumerate(planned, base):
        inputs = len(rows[i])
        # In a connected start the only nonempty parity relation on loose
        # distinctions alone includes them all. Every loose input is spent.
        implied = len(planned) == 1
        fresh = demand[i] if implied else max(demand[i], 1, 3 - inputs)
        rows[i].extend(range(next_name, next_name + fresh))
        next_name += fresh
        births.append((list(parents), inputs, fresh, implied))
    return Stage(rows), next_labels, 'funded', births


def mask(names):
    return sum(1 << x for x in names)


def family_supports(stage, labels, m):
    names = [0] * m
    for k in stage.live():
        assert labels[k] >= 0
        names[labels[k]] |= mask(stage.loose[k])
    return names


def stage_costs(stage, labels, m, do_short):
    n = len(stage.rows)
    live_by_family = [[] for _ in range(m)]
    augmented = [s.copy() for s in stage.near] + [set() for _ in range(m)]
    for k in stage.live():
        i = labels[k]
        live_by_family[i].append(k)
        augmented[k].add(n + i)
        augmented[n + i].add(k)
    assert all(live_by_family)
    direct, exact = {}, {}
    for i in range(m - 1):
        ordinary_steps = reach(stage.near, live_by_family[i])
        family_steps = reach(augmented, [n + i])
        for j in range(i + 1, m):
            direct[i, j] = 2 + min(ordinary_steps[k] for k in live_by_family[j])
            exact[i, j] = family_steps[n + j]
    changed = shortest_changes(stage, labels) if do_short else None
    return live_by_family, direct, exact, changed


def shortest_changes(stage, labels):
    # Through each distinguished occurrence, consider every shortest alternate
    # route between its holders, preserving all attainable tied family parities.
    outside = len(stage.rows)
    adjacency = [[] for _ in range(outside + 1)]
    connections = []
    for e, owners in enumerate(stage.owners):
        u = owners[0]
        v = owners[1] if len(owners) == 2 else outside
        tag = (1 << labels[u]) if v == outside else 0
        connections.append((u, v, tag))
        adjacency[u].append((v, e, tag))
        adjacency[v].append((u, e, tag))
    changed = set()
    for blocked, (source, dest, tag) in enumerate(connections):
        seen = {source}
        front = {source: {0}}
        while front:
            following = {}
            for u, parities in front.items():
                for v, e, delta in adjacency[u]:
                    if v in seen or e == blocked:
                        continue
                    values = following.setdefault(v, set())
                    if delta:
                        values.update(p ^ delta for p in parities)
                    else:
                        values.update(parities)
            if dest in following:
                changed.update(p ^ tag for p in following[dest])
                break
            seen.update(following)
            front = following
    return sorted(changed - {0})


def chain_costs(m, direct):
    d = [[0] * m for _ in range(m)]
    for (i, j), value in direct.items():
        d[i][j] = d[j][i] = value
    for middle in range(m):
        for i, row in enumerate(d):
            for j in range(i):
                through = row[middle] + d[middle][j]
                if through < row[j]:
                    row[j] = d[j][i] = through
    return {(i, j): d[i][j] for i in range(m) for j in range(i + 1, m)}


def costs_by_syndrome(m, exact):
    # Match all odd bookkeeping holders. Odd holders can be paired along
    # trails of any change; adding shortest pair changes realizes the minimum.
    best = {0: 0}
    for p in range(1, 1 << m):
        if p.bit_count() % 2:
            continue
        a = (p & -p).bit_length() - 1
        best[p] = min(exact[a, b] + best[p ^ (1 << a) ^ (1 << b)]
                      for b in range(a + 1, m) if p & (1 << b))
    return best


def literal_states(stage, first, best):
    # Enumerate actual allowed states from the homogeneous parity equations.
    # This control keeps the original loose supports even after growth.
    columns = len(stage.owners)
    rows = [mask(row) for row in stage.rows]
    pivots = {}
    for r in rows:
        while r:
            pivot = r.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = r
                break
            r ^= pivots[pivot]
    free = sorted(set(range(columns)) - set(pivots))
    if len(free) > 14:
        return 0
    states = [0]
    for f in free:
        word = 1 << f
        for p, r in sorted(pivots.items()):
            word |= ((word & r).bit_count() & 1) << p
        states += [old ^ word for old in states]
    got = {}
    for word in states:
        syndrome = sum((((word & f).bit_count() & 1) << i) for i, f in enumerate(first))
        got[syndrome] = min(got.get(syndrome, columns + 1), word.bit_count())
    assert got == best, (got, best)
    return len(states)


def cluster_dimension(m, direct, k):
    adj = [[] for _ in range(m)]
    for (a, b), w in direct.items():
        if w <= k:
            adj[a].append(b)
            adj[b].append(a)
    unvisited = set(range(m))
    count = 0
    while unvisited:
        distances = reach(adj, [min(unvisited)])
        unvisited.difference_update(i for i, d in enumerate(distances) if d >= 0)
        count += 1
    return count - 1


def all_cuts(stage, family_live, direct, exact, best):
    m = len(family_live)
    all_costs = {}
    for s in range(1, (1 << m) - 1, 2):  # one of each pair of complementary sums
        inside = [u for i, holders in enumerate(family_live) if s & (1 << i) for u in holders]
        outside = [u for i, holders in enumerate(family_live) if not s & (1 << i) for u in holders]
        from_inside = reach(stage.near, inside)
        w = 2 + min(from_inside[u] for u in outside)
        crossing = [ij for ij in direct if ((s >> ij[0]) ^ (s >> ij[1])) & 1]
        assert w == min(exact[ij] for ij in crossing) == min(direct[ij] for ij in crossing)
        all_costs[s] = w
    # A large number of families is inexpensive for holder searches, but
    # quadratic enumeration of all even syndromes versus all cuts is optional.
    if m <= 8:
        for s, w in all_costs.items():
            assert w == min(v for p, v in best.items() if (s & p).bit_count() % 2)
    return all_costs


def compare_shortest_levels(kept, all_costs, out, name, t, parts, d0, changed, original_range, n):
    # Every threshold level is represented at one of the distinct costs, or at
    # zero. Sums have unique coefficient masks after requiring family 0 in S.
    # The cap-free single-linkage hierarchy is used; no level is selected in advance.
    levels = {k: sorted(s for s, w in all_costs.items() if w > k)
              for k in sorted({0, *all_costs.values()})}
    if not kept:
        outcome = 'no nonconstant sum kept'
    elif len(kept) == len(all_costs):
        outcome = 'every nonconstant sum kept'
    elif any(kept == subset for subset in levels.values()):
        outcome = 'proper nonzero space equals a level'
    else:
        outcome = 'proper nonzero space equals no level'
        if 'example' not in out['shortest vs threshold']:
            out['shortest vs threshold']['example'] = {
                'start': name, 'knots at start': n, 'round': t, 'starting family holders': parts,
                'starting holder steps': {f'{a}-{b}': d for (a, b), d in d0.items()},
                'family signatures of shortest changes': changed, 'kept coefficient masks': kept,
                'masks at all threshold levels (stage scale)': levels}
    table = 'recorded family range' if original_range else 'extra family count on frozen stage'
    out['shortest vs threshold'][table][outcome] += 1


def audit_start(name, rows, roster, frozen, earlier, closing, out, digest):
    stages = Stage(rows)
    parts, labels = starting_families(stages)
    m = len(parts)
    counts = out['counts']
    counts['starts'] += 1
    if frozen:
        assert frozen['families'] == m and earlier['families'] == m and earlier['knots'] == len(rows)
    if m < 2:
        counts['starts below two families'] += 1
        if frozen:
            assert not frozen['rounds']
        return
    counts['starts at least two families'] += 1
    first = family_supports(stages, labels, m)
    by_family = first.copy()
    d0 = None
    frozen_rows = {r['round']: r for r in frozen['rounds']} if frozen else {}
    earlier_rows = {r['round']: r for r in earlier['rounds']} if earlier else {}
    births_by_t = {} if closing is None else closing
    for t in range(LATER_LAST + 1):
        if t:
            next_stage, labels, status, births = grow(stages, labels)
            if t in births_by_t:
                archived = births_by_t[t]
                actual = births if status == 'funded' else status
                assert actual == archived, (name, t, actual, archived)
                counts['archived birth logs compared'] += 1
                counts['archived birth entries compared'] += len(births)
            if status != 'funded':
                if t in frozen_rows:
                    assert frozen_rows[t]['end'] == status
                    counts['frozen stop reasons matched'] += 1
                out['endings'][f'round {t}, {status}'] += 1
                break
            for i in range(len(stages.rows), len(next_stage.rows)):
                by_family[labels[i]] ^= mask(next_stage.rows[i])
            stages = next_stage
        nd = len(stages.owners)
        assert family_supports(stages, labels, m) == by_family
        original = frozen_rows.get(t)
        if original and 'end' in original:
            assert original['end'] == 'not read' and nd > 300
            counts['frozen stop reasons matched'] += 1
            original = None
        if nd > CAP:
            out['endings'][f'round {t}, over {CAP} distinctions'] += 1
            break
        key = 'frozen rows' if original else 'extra rows'
        record = out[key]
        record['stages'] += 1
        record['max distinctions'] = max(record['max distinctions'], nd)
        record['max families'] = max(record['max families'], m)
        record['max knots'] = max(record['max knots'], len(stages.rows))
        out['stages by round'][t] += 1
        check_shortest = bool(original)
        family_live, direct, exact, changed = stage_costs(stages, labels, m, check_shortest)
        if t == 0:
            d0 = {ij: v - 2 for ij, v in direct.items()}
            if frozen:
                assert {f'{a}-{b}': v for (a, b), v in d0.items()} == frozen['distances']
        predicted = {ij: v + 2 + 2 * t for ij, v in d0.items()}
        assert direct == predicted and exact == chain_costs(m, predicted), (name, t, direct, exact)
        failures = [[a, b, d0[a, b], w] for (a, b), w in exact.items() if w != predicted[a, b]]
        if original:
            assert failures == original['SK1 failures'], (name, t, failures, original)
        if failures:
            out['pair exceptions'].append({'start': name, 'knots at start': len(rows), 'round': t,
                                           'family holders': parts, 'rows': failures})
        record['pair comparisons'] += len(exact)
        record['maximum exact pair cost'] = max(record['maximum exact pair cost'], max(exact.values()))
        record['round zero pair comparisons' if t == 0 else 'positive round pair comparisons'] += len(exact)
        record['direct pair prediction failures'] += len(failures)
        record['chain pair prediction failures'] += 0
        best = costs_by_syndrome(m, exact)
        record['even signatures with four or more flips'] += sum(p.bit_count() >= 4 for p in best)
        if any(p.bit_count() >= 4 for p in best):
            record['stages admitting four or more flips'] += 1
        all_costs = all_cuts(stages, family_live, direct, exact, best)
        record['maximum set cost'] = max(record['maximum set cost'], max(all_costs.values()))
        record['all complementary set pairs'] += len(all_costs)
        record['unrestricted set vs all even signatures'] += len(all_costs) if m <= 8 else 0
        if 4 <= m <= 8:
            multi = [(p, cost) for p, cost in best.items() if p.bit_count() >= 4]
            for s, w in all_costs.items():
                options = [cost for p, cost in multi if (s & p).bit_count() % 2]
                if options:
                    margin = min(options) - w
                    record['sets also flippable by at least four families'] += 1
                    record['minimum margin to a four-or-more-family change'] = min(
                        record.get('minimum margin to a four-or-more-family change', margin), margin)
                    assert margin > 0
        if original and m <= 6:
            assert not original['SK2 failures']
            record['set costs on announced range'] += len(all_costs)
            record['rows on announced set range'] += 1
        if t in earlier_rows and 'least flips' in earlier_rows[t]:
            def with_first(s):
                return s if s & 1 else ((1 << m) - 1) ^ s
            assert [all_costs[with_first(1 << i)] for i in range(m)] == earlier_rows[t]['least flips']
            record['earlier individual minima compared'] += m
        if changed is not None:
            short_masks = sorted(s for s in all_costs if all((s & p).bit_count() % 2 == 0 for p in changed))
            if m <= 6:
                assert len(short_masks) == original['shortest reading: kept sums'], (name, t, short_masks, original)
                record['shortest reading rows compared'] += 1
                record['shortest reading rows with kept sums'] += bool(short_masks)
            if t > 0:
                compare_shortest_levels(short_masks, all_costs, out, name, t, parts, d0, changed, m <= 6, len(rows))
        # Independently calculate every integer threshold on this finite stage,
        # including both sides of every change and the frozen 8 and 12 scales.
        for k in range(max(12, max(direct.values())) + 2):
            kept = sum(x > k for x in all_costs.values())
            dim = cluster_dimension(m, predicted, k)
            assert kept == (1 << dim) - 1, (name, t, k, kept, dim)
            record['integer thresholds checked'] += 1
            if original and m <= 6 and k in (8, 12):
                assert original[f'SK3 k={k}'] == {'kept sums': kept, 'dimension': dim, 'predicted': dim}
                record['frozen scale comparisons'] += 1
        group = f'{roster}: {m} families, round {t}'
        if out['literal cases by family count and round'][group] < 2 and nd <= 50:
            nstates = literal_states(stages, first, best)
            if nstates:
                out['literal cases by family count and round'][group] += 1
                counts['literal state checks'] += 1
                counts['allowed states enumerated'] += nstates
                counts['literal syndromes compared'] += len(best)
                counts['literal syndromes with at least four flips'] += sum(p.bit_count() >= 4 for p in best)
        checksum = [name, t, len(stages.rows), nd, sorted(exact.items()), sorted(all_costs.items()), changed]
        digest.update((json.dumps(checksum, separators=(',', ':')) + '\n').encode())
    else:
        out['endings'][f'read through round {LATER_LAST}'] += 1


def load_closing(roster, chosen):
    lookup = {}
    if roster not in ('census', 'heldout'):
        return lookup
    for item in read_lines(OLD / f'closing_{roster}_parity.jsonl'):
        if item.get('start') not in chosen:
            continue
        by = {}
        for b in item['births']:
            if 'end' in b:
                by[b['round']] = b['end']
            else:
                by.setdefault(b['round'], []).append((b['parents'], b['p'], b['f'], b['implied']))
        lookup[item['start']] = by
    return lookup


def chain_crosscheck():
    checked = []
    for example in json.loads((HERE / 'pair_shortcut.json').read_text()):
        stage = Stage(example['start'])
        families, labels = starting_families(stage)
        assert len(families) == 3
        frozen_supports = family_supports(stage, labels, 3)
        outer = [frozen_supports.index(mask(s)) for s in example['outer family supports']]
        middle = frozen_supports.index(mask(example['middle family support']))
        for item in example['stages']:
            t = item['round']
            if t:
                stage, labels, status, _ = grow(stage, labels)
                assert status == 'funded'
            _, direct, exact, _ = stage_costs(stage, labels, 3, False)
            end = tuple(sorted(outer))
            assert direct[end] == item['predicted outer pair'] and exact[end] == item['measured outer pair']
            assert len(stage.owners) == item['distinctions'] and len(stage.rows) == item['knots']
            assert all(exact[tuple(sorted((i, middle)))] == item['either outer with middle'] for i in outer)
            # The independent reconstruction allocates names in the frozen
            # order. Inspect the supplied witness on its original supports.
            word = mask(item['outer pair witness'])
            assert all((word & mask(r)).bit_count() % 2 == 0 for r in stage.rows)
            assert all((word & s).bit_count() % 2 == (i in outer) for i, s in enumerate(frozen_supports))
            assert word.bit_count() == exact[end]
            checked.append([len(example['start']), t, len(stage.owners), direct[end], exact[end]])
    return checked


def run(pilot):
    answer = {}
    for roster in ('census', 'heldout', 'sampled', 'built', 'larger sampled', 'larger built'):
        begin = time.perf_counter()
        source = list(cases(roster, pilot))
        selected = {name for name, _ in source}
        assert len(source) == len(selected)
        current, earlier = {}, {}
        if not roster.startswith('larger'):
            current = {r['start']: r for r in read_lines(STUDY / f'frozen_{roster}.jsonl')}
            earlier = {r['start']: r for r in read_lines(RESEARCH / 'THIRD-LAYER-20261126-001' / f'frozen_{roster}.jsonl')}
            assert selected <= set(current) and (pilot or set(current) == selected)
        archived = load_closing(roster, selected)
        out = {k: Counter() for k in ['counts', 'frozen rows', 'extra rows', 'stages by round', 'endings',
                                     'literal cases by family count and round']}
        out['pair exceptions'] = []
        out['shortest vs threshold'] = {'recorded family range': Counter(), 'extra family count on frozen stage': Counter()}
        digest = hashlib.sha256()
        load_time = time.perf_counter() - begin
        for name, rows in source:
            audit_start(name, rows, roster, current.get(name), earlier.get(name), archived.get(name), out, digest)
        out['elapsed seconds'] = round(time.perf_counter() - begin, 3)
        out['load seconds'] = round(load_time, 3)
        out['row checksum'] = digest.hexdigest()
        out['literal cases by family count and round'] = {k: v for k, v in out['literal cases by family count and round'].items() if v}
        answer[roster] = out
        print(roster, out['counts']['starts'], out['frozen rows']['stages'], out['extra rows']['stages'],
              out['elapsed seconds'], 's', flush=True)
    answer['independent chain certificate replay'] = chain_crosscheck()
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='run the shorter prefix, print timing only')
    args = parser.parse_args()
    cap = 2560 * 1024**2
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    before = time.perf_counter()
    pilot = run(True)
    partial_seconds = round(time.perf_counter() - before, 3)
    print('pilot', partial_seconds, 's', flush=True)
    if args.pilot:
        return
    before = time.perf_counter()
    results = run(False)
    records = {'methods': {'growth': 'Reconstructed groups, funding, complete rounds and ancestry. No shared engine.',
                          'pair': 'Route between distinct bookkeeping holders, one per family, on the independently grown stage.',
                          'set': 'Merged loose distinctions into two groups, then searched between them. Compared the optimum with the actual crossing pair costs, with the direct costs, and through eight families with all even syndromes.',
                          'shortest': 'For each distinction, compared all tied shortest alternate holder routes, keeping all attainable family parities.',
                          'literal': 'First two stages per roster, family count and round with at most 50 distinctions and at most 14 free variables. Enumerated every state and minimized separately on each exact starting family signature.',
                          'late': 'All starts with two or more families through round seven until stalled, closed or above 512 distinctions. Frozen cells have their original 300-distinction bound.',
                          'larger built': 'Five and six rings of four and five knots with split attachments and double links, one start per combination.',
                          'larger sampled': '48 accepted labelled starts at each of 13, 16 and 20 knots, seeds 1601127 plus size. Each knot pair meets with chance 3/(size-1), multiplicity uniformly one or two, loose counts uniformly zero to two. Accept connected starts with at least three distinctions per knot and at most 3*size+2 distinctions. Sampling with replacement.',
                          'cut enumeration': 'One representative of each complementary pair of nonconstant family sums; first family included.',
                          'checksum': 'Each JSON line contains start label, round, knots, distinctions, sorted exact pair and cut optima and all family signatures flipped by shortest changes when read.'},
               'pilot seconds': partial_seconds,
               'pilot strata seconds': {k: v['elapsed seconds'] for k, v in pilot.items() if isinstance(v, dict)},
               'full seconds': round(time.perf_counter() - before, 3),
               'process address limit MiB': 2560, 'processes': 1,
               'peak resident KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'runs': results}
    (HERE / 'cost_check.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    main()
