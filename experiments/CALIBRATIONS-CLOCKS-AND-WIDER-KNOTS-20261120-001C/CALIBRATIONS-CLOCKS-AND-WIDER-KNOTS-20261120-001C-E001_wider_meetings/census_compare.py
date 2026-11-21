"""Compare funded stages across widths, holding types and observational ages."""

from collections import Counter, defaultdict
from functools import cache
import gzip
from itertools import combinations
import json
from math import factorial, prod

from census_exact_rates import components, owners
from census_rate_tables import as_tuple, group_width
from census_stages import OUTPUT, mask_of, reduced
from census_incidence import automorphisms, incidence_family, matching
from census_rates import pair_symmetries
from census_reached import inverse, named_rows, state_transport
from model import spanned


def special_component(rows):
    names = {x for row in rows for x in row}
    return (len(rows) == 4 and len(names) == 6 and all(len(row) == 3 for row in rows)
            and all(len(set(a) & set(b)) == 1 for a, b in combinations(rows, 2)))


def name_supports(rows, movement=None):
    return tuple(tuple(row if movement is None else (movement[i] for i in row)) for row in rows)


def named_nae_state(rows):
    parts = []
    for component, names in components(rows):
        factors = tuple(tuple(sorted(rows[i])) for i in component)
        if special_component(factors):
            family = (*factors, *(tuple(x for x in names if x not in row) for row in factors))
        else:
            family = factors
        parts.append(tuple(sorted(family)))
    return tuple(sorted(parts))


def parity_generators(n, equations):
    blocks = defaultdict(list)
    for color, names in group_width(n, equations):
        blocks[color].append(names)
        for a, b in zip(names, names[1:]):
            move = list(range(n))
            move[a], move[b] = b, a
            yield tuple(move)
    for group in blocks.values():
        for left, right in zip(group, group[1:]):
            move = list(range(n))
            for a, b in zip(left, right, strict=True):
                move[a], move[b] = b, a
            yield tuple(move)


def name_permutation(mask, move):
    transformed = 0
    while mask:
        bit = mask & -mask
        transformed |= 1 << move[bit.bit_length() - 1]
        mask ^= bit
    return transformed


def moved_by_parity_table(n, basis):
    for move in parity_generators(n, basis):
        if any(not spanned(name_permutation(row, move), basis) for row in basis):
            return move
    return None


def physical_family(rows):
    holdings = Counter(owners(rows).values())
    masks = tuple(mask_of(s) for s, n in holdings.items() for _ in range(n))
    multiplicity = prod(factorial(n) for n in holdings.values())
    duplicates = prod(factorial(n) for n in Counter(map(frozenset, rows)).values())
    return incidence_family(len(rows), masks), multiplicity, duplicates


def identify_physical(rows, prior):
    family, n, duplicates = physical_family(rows)
    for pair in prior:
        if matching(pair[0], family) is not None:
            return pair[1:]
    order = automorphisms(family) * n
    assert order % duplicates == 0
    index = len(prior)
    prior.append((family, index, order // duplicates))
    return index, order // duplicates


@cache
def small_dual(n, basis):
    # Called only when multiple physical types need comparison and simple
    # invariants cannot decide them. Large ranks avoid whole-dual enumeration.
    if len(basis) > 13:
        return None
    vectors = {0}
    for check in basis:
        vectors |= {test ^ check for test in vectors}
    retained = []
    for check in sorted(vectors - {0}, key=lambda x: (x.bit_count(), x)):
        if not any(check & minimum == minimum for minimum in retained):
            retained.append(check)
    return incidence_family(n, tuple(retained))


@cache
def fixed_distinctions(basis, n):
    # The pair table already gives the weight-two family. Unary checks are
    # an independent distinction permutation invariant at all ranks.
    return sum(spanned(1 << i, basis) for i in range(n))


def state_equivalence(left, right, n):
    a, b = left['named_state'], right['named_state']
    if left['physical_type'] == right['physical_type'] or a == b:
        return True
    a, b = sorted((a, b))
    return compare_bases(n, a, b)


@cache
def compare_bases(n, a, b):
    if len(a) != len(b) or fixed_distinctions(a, n) != fixed_distinctions(b, n):
        return False
    l, r = small_dual(n, a), small_dual(n, b)
    return None if l is None or r is None else matching(l, r) is not None


def stages_by_group(records, measurements, law):
    groups = defaultdict(list)
    for item in measurements:
        source = records[item['source_index']]
        stage = source['stages'][item['age'] - 1]
        group_item = {**item, **stage, 'source_rows': source['source_rows'],
                      'source_width': source['source_width'], 'components': source['source_components'],
                      'labelled_source_multiplicity': source['labelled_source_multiplicity']}
        key = as_tuple(item['table_key']) if 'table_key' in item else ('unresolved', stage['width'], len(groups))
        groups[key].append(group_item)
    for key, items in groups.items():
        if 'table_key' not in items[0]:
            continue
        previous = []
        for item in items:
            rows = item['rows']
            item['physical_type'], physical_order = identify_physical(rows, previous)
            assert item['table_automorphisms'] % physical_order == 0
            move = inverse(item['table_order'])
            item['named_holding'] = named_rows(rows, move)
            item['internal_holding_alias'] = item['table_automorphisms'] > physical_order
            if law == 'nae':
                exceptional = sum(special_component([rows[h] for h in part]) for part, _ in components(rows))
                state_order = physical_order * (2 ** exceptional)
                assert item['table_automorphisms'] % state_order == 0
                item['named_state_variants'] = item['table_automorphisms'] // state_order
                item['internal_alias'] = item['table_automorphisms'] > state_order
                item['named_state'] = named_nae_state(name_supports(rows, move))
            else:
                n = item['width']
                equations = item['state_equations']
                alias = moved_by_parity_table(n, equations)
                item['internal_alias'] = alias is not None
                item['internal_transport'] = alias
                item['named_state'] = reduced(name_permutation(check, move) for check in equations)
    return groups


def metrics(items, law, cross_age=False):
    states = {v['named_state'] for v in items}
    holdings = {v['named_holding'] for v in items}
    outcome = {(s['next_status'], s['next_birth_count']) for s in items}
    birth_counts = {count for _, count in outcome}
    n = items[0]['width']
    seen = {}
    for item in items:
        seen.setdefault(item['physical_type'], item)
    signs = {}
    pending = False
    for i, j in combinations(seen, 2):
        comparable = False if law == 'nae' else state_equivalence(seen[i], seen[j], n)
        signs[tuple(sorted((i, j)))] = comparable
        pending |= comparable is None

    def eq(a, b):
        x, y = sorted((a['physical_type'], b['physical_type']))
        return True if x == y else signs[x, y]

    distinguished = []
    if not pending:
        for item in seen.values():
            if not any(eq(item, prior) for prior in distinguished):
                distinguished.append(item)

    if cross_age:
        comparisons = [(a, b) for a, b in combinations(items, 2) if a['age'] != b['age']]
        named = any(a['internal_alias'] or b['internal_alias'] or a['named_state'] != b['named_state']
                    for a, b in comparisons)
        different_types = any(eq(a, b) is False for a, b in comparisons)
        undecided = any(eq(a, b) is None for a, b in comparisons)
        births = any(a['next_birth_count'] != b['next_birth_count'] for a, b in comparisons)
        statuses = any((a['next_status'], a['next_birth_count']) != (b['next_status'], b['next_birth_count'])
                       for a, b in comparisons)
        holds = any(a['physical_type'] != b['physical_type'] for a, b in comparisons)
        named_holds = any(a['internal_holding_alias'] or b['internal_holding_alias']
                          or a['named_holding'] != b['named_holding'] for a, b in comparisons)
    else:
        named = len(states) > 1 or any(v['internal_alias'] for v in items)
        different_types = any(value is False for value in signs.values())
        undecided = pending
        births = len(birth_counts) > 1
        statuses = len(outcome) > 1
        holds = len(seen) > 1
        named_holds = len(holdings) > 1 or any(v['internal_holding_alias'] for v in items)
    return {'named_states_differ': named, 'state_types_differ': different_types,
            'state_types_unresolved': undecided, 'next_birth_counts_differ': births,
            'next_outcomes_differ': statuses, 'physical_types_differ': holds, 'named_holdings_differ': named_holds,
            'next_counts': sorted(birth_counts), 'physical_types': len(seen),
            'state_types': None if pending else len(distinguished)}


def summarize(groups, law, eligible, cross_age=False):
    totals = Counter(stage_records=0, weighted_source_records=0, table_types=0, named_tables=0,
                     named_states_differ=0, state_types_differ=0, next_birth_counts_differ=0,
                     next_outcomes_differ=0, physical_types_differ=0, named_holdings_differ=0,
                     state_types_unresolved=0, readings_unresolved=0, certified_state_types=0,
                     physical_types=0, source_age_cases_with_birth_ambiguity=0)
    stages_with_same_count, widths = 0, defaultdict(set)
    for members in groups.values():
        for v in filter(eligible, members):
            widths[v['width']].add(v['next_birth_count'])
    by_scope = Counter()
    exceptions = []
    for key, members in groups.items():
        people = [s for s in members if eligible(s)]
        if not people or cross_age and len({v['age'] for v in people}) < 2:
            continue
        totals['stage_records'] += len(people)
        totals['weighted_source_records'] += sum(v['labelled_source_multiplicity'] for v in people)
        by_scope.update((str(p['source_width']) + '/' + str(p['age']) + '/' + str(p['components']) for p in people))
        if 'table_key' not in people[0]:
            totals['readings_unresolved'] += len(people)
            stages_with_same_count += len(people) * (len(widths[people[0]['width']]) == 1)
            continue
        status = metrics(people, law, cross_age)
        named_tables = factorial(people[0]['width']) // people[0]['table_automorphisms']
        totals['table_types'] += 1
        totals['named_tables'] += named_tables
        totals['certified_state_types'] += status['state_types'] or 0
        totals['physical_types'] += status['physical_types']
        totals['source_age_cases_with_birth_ambiguity'] += len(people) * status['next_birth_counts_differ']
        for flag, passed in status.items():
            if isinstance(passed, bool) and passed:
                totals[flag] += 1
                totals['named_tables_' + flag] += named_tables
        if any(v is True for v in status.values()):
            exceptions.append({'table_key': key, **status,
                               'members': [(x['source_index'], x['age']) for x in people]})
    return dict(totals=totals, widths_with_one_next_count=sum(len(c) == 1 for c in widths.values()),
                unmeasured_stages_decided_by_width=stages_with_same_count, stages_by_source_age_components=by_scope,
                cases_with_alternatives=exceptions)


def summary_views(groups, law):
    predicates = {'first_through_8': lambda s: s['age'] == 1 and s['source_width'] <= 8,
                  'second_through_8': lambda s: s['age'] == 2,
                  'first_exactly_9': lambda s: s['age'] == 1 and s['source_width'] == 9,
                  'first_exactly_10': lambda s: s['age'] == 1 and s['source_width'] == 10,
                  'first_through_9': lambda s: s['age'] == 1 and s['source_width'] <= 9,
                  'first_through_10': lambda s: s['age'] == 1,
                  'both_ages_through_8': lambda s: s['source_width'] <= 8,
                  'both_ages_through_9': lambda s: s['source_width'] <= 9,
                  'both_ages_through_10': lambda s: True}
    summary = {label: summarize(groups, law, candidate) for label, candidate in predicates.items()}
    for bound in (8, 9, 10):
        summary[f'cross_age_through_{bound}'] = summarize(groups, law, lambda s: s['source_width'] <= bound,
                                                           cross_age=True)
    return summary


def minima(groups, law):
    result = {}

    def keep(test, key, a, b):
        rank = (max(a['source_width'], b['source_width']), a['width'],
                len(a['source_rows']) + len(b['source_rows']), a['age'] + b['age'])
        if test not in result or rank < result[test][0]:
            result[test] = (rank, key, a, b)

    for key, members in groups.items():
        if 'table_key' not in members[0]:
            continue
        for a in members:
            if a['internal_alias']:
                keep('different_named_states', key, a, a)
        for a, b in combinations(members, 2):
            if a['named_state'] != b['named_state']:
                keep('different_named_states', key, a, b)
            if a['physical_type'] != b['physical_type']:
                proven = law == 'nae' or state_equivalence(a, b, a['width']) is False
                if proven:
                    keep('different_state_types', key, a, b)
            if a['next_birth_count'] != b['next_birth_count']:
                keep('different_next_birth_counts', key, a, b)
                if a['age'] != b['age']:
                    keep('different_next_birth_counts_cross_age', key, a, b)
                if law == 'parity' and state_equivalence(a, b, a['width']) is True:
                    keep('same_states_different_births', key, a, b)
    return result


def minimum_payload(result, law):
    packed = {}
    for kind, (rank, key, left, right) in result.items():
        transforms = [inverse(s['table_order']) for s in (left, right)]
        if left is right:
            if law == 'parity':
                move = right['internal_transport']
            else:
                n = right['width']
                total = right['allowed_states']
                rates = dict(zip(combinations(range(n), 2), right['disagreement_counts'], strict=True))
                state = named_nae_state(right['rows'])
                move = next(p for p in pair_symmetries(n, total, rates)
                            if named_nae_state(name_supports(right['rows'], p)) != state)
            transforms[1] = tuple(transforms[1][i] for i in move)
        elif kind == 'same_states_different_births':
            to_compatible = lambda s: {'stage_rows': s['rows'], 'stage_width': s['width'], 'table_order': s['table_order']}
            transforms[1] = state_transport(to_compatible(left), to_compatible(right), 'parity')
        packed[kind] = {'rank': rank, 'table_key': key,
                        'arms': [{'source_width': s['source_width'], 'age': s['age'], 'source_rows': s['source_rows'],
                                  'stage_rows': named_rows(s['rows'], move), 'reached_name_transport': move,
                                  'allowed_states': s['allowed_states'], 'next_status': s['next_status'],
                                  'next_birth_count': s['next_birth_count']}
                                 for s, move in zip((left, right), transforms, strict=True)]}
    return packed


def main():
    with gzip.open(OUTPUT / 'census_stages.json.gz', 'rt') as file:
        all_stages = json.load(file)
    with gzip.open(OUTPUT / 'census_rate_tables.json.gz', 'rt') as file:
        rate_tables = json.load(file)
    output = {}
    for law, sources in all_stages.items():
        print(law, 'grouping reached states', flush=True)
        groups = stages_by_group(sources, rate_tables[law]['records'], law)
        views = summary_views(groups, law)
        minima_reached = minimum_payload(minima(groups, law), law)
        source_counts = Counter(f'{s["source_width"]}/{s["source_components"]}/{s["attempts"][0]}' for s in sources)
        output[law] = {'views': views, 'minima': minima_reached, 'source_types_by_status': source_counts}
        print(law, 'classes', [(key, list(report['totals'].items())[:2], report['totals']['table_types'],
                                report['totals']['named_states_differ'], report['totals']['next_birth_counts_differ'])
                               for key, report in views.items()], flush=True)
        print(law, 'minima', {key: group['rank'] for key, group in minima_reached.items()}, flush=True)
    (OUTPUT / 'census_summary.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
