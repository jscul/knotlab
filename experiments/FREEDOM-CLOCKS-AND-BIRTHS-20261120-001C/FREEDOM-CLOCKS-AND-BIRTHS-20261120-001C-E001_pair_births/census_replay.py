"""Independent counting, source allocation, state-matching and continuation controls."""

from collections import Counter, defaultdict, deque
from fractions import Fraction
import gzip
from itertools import combinations
import json
from math import factorial, prod
import sys

import networkx as nx

from census_incidence import automorphisms, incidence_family, matching
from census_rates import quotient
from census_reached import OUTPUT, ROOT, named_rows
from model import parity_counts


sys.path.insert(0, str(ROOT / 'experiments/ORDINARY-DYNAMICS-20261120-001A'
                       / 'ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'))
from end_operator import from_stars, step


def width(rows):
    return max(max(s) for s in rows) + 1


def masks(rows):
    return tuple(sum(1 << i for i in r) for r in rows)


def locally_allows(word, support, law):
    bits = word & support
    return bits.bit_count() % 2 == 0 if law == 'parity' else bits not in (0, support)


def literal_counts(rows, law):
    n = width(rows)
    forms = masks(rows)
    allowed = [word for word in range(1 << n) if all(locally_allows(word, row, law) for row in forms)]
    return len(allowed), {pair: sum(((word >> pair[0]) ^ (word >> pair[1])) & 1 for word in allowed)
                          for pair in combinations(range(n), 2)}


def check_source(rows, law, n):
    seen = Counter(i for row in rows for i in row)
    assert set(seen) == set(range(n)) and all(c in (1, 2) for c in seen.values())
    assert all(len(row) >= 3 and len(row) == len(set(row)) for row in rows)
    allowed = set()
    erasures = set()
    supports = masks(rows)
    for word in range(1 << n):
        failed = [i for i, row in enumerate(supports) if not locally_allows(word, row, law)]
        if not failed:
            allowed.add(word)
        if len(failed) == 1:
            erasures.add(failed[0])
    assert erasures == set(range(len(rows)))
    for row in supports:
        assert {w & row for w in allowed} == {w for w in range(1 << n)
                                              if w & row == w and locally_allows(w, row, law)}


def whole_dual(rows):
    seen = {0}
    for mask in masks(rows):
        seen |= {word ^ mask for word in seen}
    return seen


def parity_read(rows):
    n = width(rows)
    dual = whole_dual(rows)
    assert len(dual).bit_count() == 1
    total = 1 << (n - (len(dual).bit_length() - 1))
    return total, {(i, j): 0 if (1 << i) ^ (1 << j) in dual else total // 2
                   for i, j in combinations(range(n), 2)}


def nae_read(rows):
    """Inclusion-exclusion using literal union-find on waived monochrome rules."""
    n = width(rows)
    all_names = tuple(range(n))
    same = Counter()
    total = 0
    for chosen in range(1 << len(rows)):
        parent = list(all_names)

        def find(i):
            while parent[i] != i:
                i = parent[i]
            return i

        for i, (first, *rest) in enumerate(rows):
            if chosen & (1 << i):
                root = find(first)
                for item in rest:
                    parent[find(item)] = root
        groups = defaultdict(list)
        for i in all_names:
            groups[find(i)].append(i)
        weight = (-1 if chosen.bit_count() % 2 else 1) * (1 << len(groups))
        total += weight
        for group in groups.values():
            for pair in combinations(group, 2):
                same[pair] += weight
    return total, {pair: (total - same[pair]) // 2 for pair in combinations(all_names, 2)}


def physical_holder_graph(rows):
    owners = defaultdict(list)
    for h, row in enumerate(rows):
        for name in row:
            owners[name].append(h)
    actual = Counter(tuple(group) for group in owners.values())
    graph = nx.Graph()
    graph.add_nodes_from((h, {'loose': actual[h,]}) for h in range(len(rows)))
    graph.add_edges_from((a, b, {'shares': size}) for group, size in actual.items() if len(group) == 2
                         for a, b in (group,))
    assert nx.is_connected(graph)
    return graph


def holder_match(a, b):
    return nx.is_isomorphic(a, b, node_match=lambda x, y: x['loose'] == y['loose'],
                            edge_match=lambda x, y: x['shares'] == y['shares'])


def weighted_orders(labels, weights):
    """Count exact automorphisms by extending partial name matches."""
    indices = range(len(labels))
    signatures = [(labels[i], tuple(sorted((labels[j], weights[i][j]) for j in indices if j != i)))
                  for i in indices]
    candidates = [tuple(j for j in indices if signatures[i] == signatures[j]) for i in indices]
    priority = sorted(indices, key=lambda i: len(candidates[i]))
    used = set()
    matching_points = {}

    def visit(depth):
        if depth == len(priority):
            return 1
        a = priority[depth]
        count = 0
        for b in candidates[a]:
            if b not in used and all(weights[a][old] == weights[b][new]
                                     for old, new in matching_points.items()):
                matching_points[a] = b
                used.add(b)
                count += visit(depth + 1)
                del matching_points[a]
                used.remove(b)
        return count

    return visit(0)


def holder_order(graph):
    nodes = tuple(graph)
    weights = [[graph[a][b]['shares'] if graph.has_edge(a, b) else 0 for b in nodes] for a in nodes]
    loose = tuple(graph.nodes[a]['loose'] for a in nodes)
    multiplicity = prod(factorial(i) for i in loose) * prod(factorial(q['shares']) for _, _, q in graph.edges.data())
    return multiplicity * weighted_orders(loose, weights)


def parity_state_match(a, b):
    return matching(a, b) is not None


def stage_status(turn):
    return 'births' if turn.status == 'extend' else turn.status


def materialize(rows, turn, reverse=False):
    owner_count = Counter(i for group in rows for i in group)
    inputs = [iter(sorted((i for i in group if owner_count[i] == 1), reverse=reverse)) for group in rows]
    at = width(rows)
    births = []
    for parents, fresh in zip(turn.parents, turn.fresh, strict=True):
        used = tuple(next(inputs[h]) for h in parents)
        newborn = used + tuple(range(at, at + fresh))
        births.append(newborn)
        at += fresh
    return (*rows, *births)


def allocation_witness(record, turn):
    original = tuple(map(tuple, record['source_rows']))
    recorded = tuple(map(tuple, record['stage_rows']))
    alternate = materialize(original, turn, reverse=True)
    pools = defaultdict(deque)
    for pair, row in zip(zip(turn.parents, turn.fresh, strict=True), alternate[len(original):], strict=True):
        pools[pair].append(row)
    recode = {}
    for (parents, fresh), row in zip(record['first_births'], recorded[len(original):], strict=True):
        recode.update(zip(row, pools[tuple(parents), fresh].popleft(), strict=True))
    order = tuple(recode.get(i, i) for i in range(record['stage_width']))
    assert len(set(order)) == len(order)
    assert named_rows(recorded, order) == named_rows(alternate)
    return alternate


def same_rate_table(n, left, right):
    a, p = left
    b, q = right
    return all(p[key] * b == q[key] * a for key in combinations(range(n), 2))


def as_tuple(value):
    return tuple(map(as_tuple, value)) if isinstance(value, list) else value


def check_key_order(table_key, order, matrix):
    size, groups, between = table_key
    assert sorted(order) == list(range(size))
    which = [i for i, (n, _, _) in enumerate(groups) for _ in range(n)]
    inter = dict(zip(combinations(range(len(groups)), 2), between, strict=True))
    for i, j in combinations(range(size), 2):
        a, b = which[i], which[j]
        expected = groups[a][1:] if a == b else inter[a, b]
        assert matrix[order[i]][order[j]] == expected


def replay(law, records):
    tested = Counter()
    families = defaultdict(dict)
    rate_classes = defaultdict(dict)
    for item in records:
        old = tuple(map(tuple, item['source_rows']))
        check_source(old, law, item['source_width'])
        assert item['labelled_source_multiplicity'] * holder_order(physical_holder_graph(old)) == factorial(item['source_width'])
        first = step(from_stars(old), law, max_births=1024)
        assert stage_status(first) == item['first_status']
        tested[item['first_status']] += 1
        if first.status != 'extend':
            continue
        assert Counter(zip(first.parents, first.fresh, strict=True)) == Counter((tuple(p), f) for p, f in item['first_births'])
        alternate = allocation_witness(item, first)
        second = step(from_stars(alternate), law, max_births=1024)
        assert stage_status(second) == item['next_status'] and len(second.parents) == item['next_birth_count']

        rows = tuple(map(tuple, item['stage_rows']))
        n = item['stage_width']
        analytic = nae_read(rows) if law == 'nae' else parity_read(rows)
        assert analytic == (item['total_words'], dict(zip(combinations(range(n), 2), item['pair_counts'], strict=True)))
        if n <= 12:
            assert analytic == literal_counts(rows, law)
            tested['full_word_replays'] += 1
        total, disagree = analytic
        table_key = as_tuple(item['table_key'])
        pairs = {k: Fraction(v, total) for k, v in disagree.items()}
        matrix = [[None] * n for _ in range(n)]
        for (i, j), value in pairs.items():
            matrix[i][j] = matrix[j][i] = (value.numerator, value.denominator)
        check_key_order(table_key, item['table_order'], matrix)
        classes, colors, reduced_weights, graph = quotient(matrix)
        table_invariant = (n, tuple(sorted(Counter(pairs.values()).items())))
        for key, other in rate_classes[table_invariant].items():
            assert nx.vf2pp_is_isomorphic(other, graph, node_label='kind') == (key == table_key)
        rate_classes[table_invariant].setdefault(table_key, graph)
        assert sum(col[0] for col in colors) == n and len(classes) == len(colors)
        twin_product = prod(factorial(len(c)) for c in classes)
        assert weighted_orders(colors, reduced_weights) * twin_product == item['table_automorphisms']
        physical = physical_holder_graph(rows)
        assert holder_order(physical) == item['physical_automorphisms']
        if law == 'nae':
            family = physical
            comparator = holder_match
        else:
            family = incidence_family(n, tuple(sorted(whole_dual(rows) - {0})))
            comparator = parity_state_match
        state_type = item['state_type_within_table']
        for code, other in families[table_key].items():
            assert comparator(family, other) == (code == state_type)
        if state_type not in families[table_key] and law == 'parity':
            assert automorphisms(family) == item['state_automorphisms']
        families[table_key].setdefault(state_type, family)
        tested['independent_count_replays'] += 1
    return {'checks': tested, 'rate_table_types': sum(map(len, rate_classes.values())),
            'state_types': sum(map(len, families.values()))}


def later_counts(left, right, law):
    left = tuple(map(tuple, left))
    right = tuple(map(tuple, right))
    states = [left, right]
    results = []
    stopped = [False, False]
    for cut in range(2, 6):
        record = {'cut': cut, 'arms': []}
        for i, rows in enumerate(states):
            if stopped[i]:
                previous = results[-1]['arms'][i]
                record['arms'].append(previous)
                continue
            turn = step(from_stars(rows), law, max_births=1024)
            if turn.status == 'cap':
                stopped[i] = True
                record['arms'].append({'status': 'cap', 'planned_births_lower': turn.planned_births_lower,
                                       'width': width(rows)})
                continue
            if turn.status == 'extend':
                states[i] = materialize(rows, turn)
            record['arms'].append({'status': stage_status(turn), 'births': len(turn.parents),
                                   'next_width': width(states[i])})
        if not any(stopped):
            n, m = map(width, states)
            if n != m:
                record['later_tables_equal_up_to_renaming'] = False
            elif law == 'parity' and n <= 128:
                (_, a), (_, b) = map(parity_counts, states)
                # Parity tables have just equality rates zero and all other rates one half.
                record['later_tables_equal_up_to_renaming'] = sorted(Counter(i for p, k in a.items() if k == 0
                                                                           for i in p).values()) == sorted(
                    Counter(i for p, k in b.items() if k == 0 for i in p).values())
        results.append(record)
        if all(stopped) or all(x['status'] in ('closed', 'stall') for x in record['arms']):
            break
    return results


def parity_controls(summary):
    out = {}
    for name, case in summary['minima'].items():
        left, right = (arm['reached_rows_in_common_names'] for arm in case['arms'])
        n = width(left)
        left_counts, right_counts = parity_read(left), parity_read(right)
        assert same_rate_table(n, left_counts, right_counts)
        differences = whole_dual(left) ^ whole_dual(right)
        check = min(differences, key=lambda mask: (mask.bit_count(), mask), default=None)
        matched = {'same_full_named_states': not differences,
                   'least_separating_full_marginal_order': check.bit_count() if check else None,
                   'least_separating_support_marginal_order': check.bit_count() if check else None,
                   'separating_check': [i for i in range(n) if check and check & (1 << i)],
                   'check_holds_in_left': check in whole_dual(left) if check else None}
        if check:
            projected = []
            for arm in (left, right):
                rules = masks(arm)
                local = Counter(w & check for w in range(1 << n)
                                if all(locally_allows(w, rule, 'parity') for rule in rules))
                projected.append(dict(sorted(local.items())))
            assert set(projected[0]) != set(projected[1])
            matched['literal_local_word_counts'] = projected
        if name in ('different_next_birth_counts', 'same_states_different_next_birth_counts', 'different_next_status'):
            matched['trace'] = later_counts(left, right, 'parity')
        out[name] = matched
    return out


def closed_nae_control():
    rows = ((0, 1, 2, 3), (0, 4, 5, 6), (1, 4, 5, 7), (2, 3, 6, 7))
    other = named_rows(rows, (0, 6, 2, 3, 4, 5, 1, 7))
    left, right = masks(rows), masks(other)
    assert literal_counts(rows, 'nae') == literal_counts(other, 'nae')
    only_left = next(w for w in range(256) if all(locally_allows(w, s, 'nae') for s in left)
                     and any(not locally_allows(w, s, 'nae') for s in right))
    assert step(from_stars(rows), 'nae').status == step(from_stars(other), 'nae').status == 'closed'
    return {'rows': [rows, other], 'word_only_in_left': only_left, 'state_count_each': 154,
            'first_status_each': 'closed'}


def main():
    with gzip.open(OUTPUT / 'census_cases.json.gz', 'rt') as data:
        records = json.load(data)
    summary = json.loads((OUTPUT / 'census_summary.json').read_text())
    receipt = {}
    for law, population in records.items():
        receipt[law] = replay(law, population)
        print(law, receipt[law], flush=True)
    receipt['ordinary_parity_controls'] = parity_controls(summary['parity'])
    receipt['closed_nae_control'] = closed_nae_control()
    (OUTPUT / 'census_verification.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
