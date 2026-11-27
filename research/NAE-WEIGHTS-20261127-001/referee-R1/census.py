"""Recount the two weightings from the census and audit the W2 eligibility rules."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import prod
from pathlib import Path
from time import perf_counter

from growth import round_completion_weights


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
STARTS = RESEARCH / 'FORBID-EDITS-20261126-001' / 'starts.json'
CENSUS_ROWS = RESEARCH / 'NAE-LAYER-20261127-001' / 'census.jsonl'
REPORTED = HERE.parent / 'weights.json'
OUTPUT = HERE / 'census.json'
EQUAL = 'equal'
COMPLETIONS = 'completions'
DISJOINT = 'disjoint held unions'
TERM_DISJOINT = 'overlapping held unions, disjoint selected distinctions'
TERM_SHARED = 'overlapping held unions, shared selected distinctions'


def one_component(knots, neighbors):
    remaining = set(knots)
    pending = [remaining.pop()]
    while pending:
        next_knots = neighbors[pending.pop()] & remaining
        remaining.difference_update(next_knots)
        pending.extend(next_knots)
    return not remaining


def canonical_tree_roster():
    """Rebuild the eligible set without depending on the order in the archive."""
    roster = set()
    for size in (3, 4, 5):
        labels = tuple(range(size))
        renamings = tuple(permutations(labels))
        for pairs in combinations(combinations(labels, 2), size - 1):
            neighbors = [set() for _ in labels]
            for a, b in pairs:
                neighbors[a].add(b)
                neighbors[b].add(a)
            if not one_component(labels, neighbors):
                continue
            loose_options = [range(max(0, 3 - len(group)), 3) for group in neighbors]
            for loose in product(*loose_options):
                if len(pairs) + sum(loose) > 12:
                    continue
                presentations = (
                    (tuple(sorted((min(names[a], names[b]), max(names[a], names[b]), 1)
                                  for a, b in pairs)), tuple(loose[names.index(k)] for k in labels))
                    for names in renamings
                )
                meetings, canonical_loose = min(presentations)
                roster.add((size, meetings, canonical_loose))
    return roster


def source_rows():
    """Reconstruct all meeting patterns and join the source's numbered rows."""
    inputs = json.loads(STARTS.read_text())
    source_rows = [json.loads(line) for line in CENSUS_ROWS.read_text().splitlines()]
    assert source_rows.pop()['tally']['starts'] == len(inputs)
    entries = []
    shapes = Counter()
    tree_keys = set()
    for index, ((size, meetings, loose), recorded) in enumerate(zip(inputs, source_rows, strict=True)):
        assert 3 <= size <= 5 and len(loose) == size
        assert all(count in (0, 1, 2) for count in loose)
        assert recorded['start'] == f'census {index}' and recorded['loose'] == sum(loose)
        supports = [[] for _ in range(size)]
        neighbors = [set() for _ in range(size)]
        next_name = 0
        for a, b, copies in meetings:
            assert 0 <= a < b < size and copies in (1, 2) and b not in neighbors[a]
            neighbors[a].add(b)
            neighbors[b].add(a)
            shared = range(next_name, next_name + copies)
            supports[a].extend(shared)
            supports[b].extend(shared)
            next_name += copies
        for knot, count in enumerate(loose):
            supports[knot].extend(range(next_name, next_name + count))
            next_name += count
        assert next_name <= 12 and min(map(len, supports)) >= 3
        assert one_component(range(size), neighbors)
        doubled = any(copies == 2 for _, _, copies in meetings)
        ring = len(meetings) >= size
        tree = not (doubled or ring)
        assert tree == recorded['tree-shaped'], (index, tree, recorded)
        shapes[size, ring, doubled] += 1
        if tree:
            key = (size, tuple(map(tuple, meetings)), tuple(loose))
            assert key not in tree_keys
            tree_keys.add(key)
            entries.append((index, tuple(map(tuple, supports)), neighbors))

    regenerated = canonical_tree_roster()
    assert tree_keys == regenerated, (tree_keys - regenerated, regenerated - tree_keys)
    return entries, {
        'reconstructed rows': len(inputs),
        'source tree eligibility or row identity mismatches': 0,
        'independently regenerated eligible tree roster': len(regenerated),
        'scope by meeting pattern': [
            {'knots': size, 'ring of at least three knots': ring,
             'doubled meeting': doubled, 'starts': count}
            for (size, ring, doubled), count in sorted(shapes.items())
        ],
        'source sha256': {str(path.relative_to(RESEARCH.parent)): sha256(path.read_bytes()).hexdigest()
                          for path in (STARTS, CENSUS_ROWS, REPORTED)},
    }


def literal_states(supports, bits):
    masks = [sum(bits[name] for name in support) for support in supports]
    return [word for word in range(1 << len(bits))
            if all(word & mask not in (0, mask) for mask in masks)]


def signed_sums(weights, width):
    """Walsh–Hadamard transform of integer masses by state word."""
    table = [weights.get(word, 0) for word in range(1 << width)]
    for place in range(width):
        offset = 1 << place
        for start in range(0, len(table), offset * 2):
            for left in range(start, start + offset):
                right = left + offset
                a, b = table[left], table[right]
                table[left], table[right] = a + b, a - b
    assert table[0] == sum(weights.values()) > 0
    assert all(value == 0 for term, value in enumerate(table) if term.bit_count() % 2)
    return table


def local_products(supports, names, bits):
    """Expand even products into terms on knots by tracing to one distinction."""
    holders = {name: [k for k, support in enumerate(supports) if name in support]
               for name in names}
    paths = {}
    zero = (0,) * len(supports)

    def visit(name, previous_knot, path):
        assert name not in paths
        paths[name] = path
        for knot in holders[name]:
            if knot == previous_knot:
                continue
            for next_name in supports[knot]:
                if next_name != name:
                    next_local = bits[name] | bits[next_name]
                    visit(next_name, knot, path[:knot] + (next_local,) + path[knot + 1:])

    visit(names[0], None, zero)
    assert len(paths) == len(names)
    products = [zero]
    for term in range(1, 1 << len(names)):
        lowest = term & -term
        path = paths[names[lowest.bit_length() - 1]]
        products.append(tuple(a ^ b for a, b in zip(products[term ^ lowest], path, strict=True)))
    return products


def knot_terms(knots, supports, bits, holders, neighbors):
    own = set(knots)
    names = sorted({name for knot in knots for name in supports[knot]})
    held = sum(bits[name] for name in names)
    exclusive = sum(bits[name] for name in names if holders[name] <= own)
    terms = [(tuple(subset), sum(bits[name] for name in subset), count)
             for count in range(2, len(names) + 1, 2) for subset in combinations(names, count)]
    return held, exclusive, terms, one_component(knots, neighbors)


def knot_partitions(size):
    """Enumerate each unordered pair once, retaining the recorded exception order."""
    result = []
    for placements in product((0, 1, 2), repeat=size):
        group_a = tuple(knot for knot, group in enumerate(placements) if group == 1)
        group_b = tuple(knot for knot, group in enumerate(placements) if group == 2)
        if group_a and group_b and group_a < group_b:
            result.append((group_a, group_b))
    return sorted(result, key=lambda pair: (len(pair[0]), pair[0], len(pair[1]), pair[1]))


def check_w2(supports, bits, neighbors, tables, routed):
    holders = {name: {k for k, support in enumerate(supports) if name in support}
               for name in bits}
    partitions = knot_partitions(len(supports))
    groups = {group: knot_terms(group, supports, bits, holders, neighbors)
              for pair in partitions for group in pair}
    across = {weighting: defaultdict(Counter) for weighting in tables}
    connected_counts = {weighting: defaultdict(Counter) for weighting in tables}
    unique_pairs = {weighting: defaultdict(set) for weighting in tables}
    exceptions = {weighting: [] for weighting in tables}
    first_failures = {weighting: {} for weighting in tables}
    scopes = Counter()
    route_cases = Counter()
    connected_controls = {weighting: Counter() for weighting in tables}

    for group_a, group_b in partitions:
        held_a, only_a, terms_a, connected_a = groups[group_a]
        held_b, only_b, terms_b, connected_b = groups[group_b]
        unions_disjoint = not held_a & held_b
        carrier_status = 'disjoint held unions' if unions_disjoint else 'overlapping held unions'
        connectedness = 'both connected' if connected_a and connected_b else 'at least one disconnected'
        scopes[carrier_status, connectedness, 'carrier pairs'] += 1
        if only_a.bit_count() >= 2 and only_b.bit_count() >= 2:
            scopes[carrier_status, connectedness, 'carrier pairs with two exclusive distinctions each'] += 1

        for names_a, term_a, count_a in terms_a:
            for names_b, term_b, count_b in terms_b:
                domain = DISJOINT if unions_disjoint else TERM_SHARED if term_a & term_b else TERM_DISJOINT
                location = 'inside' if not (term_a & ~only_a or term_b & ~only_b) else 'exposed'
                sizes = tuple(sorted((count_a, count_b)))
                key = domain, sizes, location
                frozen_cell = domain == DISJOINT and sizes == (2, 2)
                joint = term_a ^ term_b
                jointly_used = tuple(sorted((a ^ b).bit_count()
                                            for a, b in zip(routed[term_a], routed[term_b], strict=True)
                                            if a and b))
                for weighting, table in tables.items():
                    mass = table[0]
                    independent = table[joint] * mass == table[term_a] * table[term_b]
                    counts = across[weighting][key]
                    counts['comparisons'] += 1
                    counts['independent'] += independent
                    counts['identical products'] += term_a == term_b
                    counts['products using at least one of the same knots'] += bool(jointly_used)
                    if connected_a and connected_b:
                        connected_controls[weighting]['comparisons'] += 1
                        connected_controls[weighting]['independent'] += independent
                    if weighting == EQUAL:
                        assert independent == (not jointly_used), (supports, group_a, group_b, names_a, names_b)
                        if frozen_cell and jointly_used:
                            route_cases[location, connectedness, jointly_used] += 1
                    if frozen_cell:
                        unique_pairs[weighting][location].add(tuple(sorted((term_a, term_b))))
                        connected_counts[weighting][location, connectedness]['comparisons'] += 1
                        connected_counts[weighting][location, connectedness]['independent'] += independent
                    if independent:
                        continue
                    limited = frozen_cell and len(exceptions[weighting]) < 5
                    if limited or key not in first_failures[weighting]:
                        exact = str(Fraction(table[joint], mass))
                        separate = str(Fraction(table[term_a] * table[term_b], mass * mass))
                        if limited:
                            exceptions[weighting].append((supports, names_a, names_b, exact, separate))
                        first_failures[weighting].setdefault(key, {
                            'knot sets': (group_a, group_b), 'term distinctions': (names_a, names_b),
                            'joint mean': exact, 'product of separate means': separate,
                            'joint product sizes at jointly used knots': jointly_used,
                        })

    return (across, connected_counts, unique_pairs, exceptions, first_failures,
            scopes, route_cases, connected_controls)


def analyze(index, supports, neighbors):
    names = sorted({name for support in supports for name in support})
    bits = {name: 1 << i for i, name in enumerate(names)}
    states = literal_states(supports, bits)
    equal_weights = dict.fromkeys(states, 1)
    completion_weights = round_completion_weights(supports, names, states)
    if completion_weights is not None:
        assert equal_weights.keys() == completion_weights.keys() and min(completion_weights.values()) > 0

    weights = {EQUAL: equal_weights}
    if completion_weights is not None:
        weights[COMPLETIONS] = completion_weights
    tables = {weighting: signed_sums(masses, len(names)) for weighting, masses in weights.items()}
    controls = (bits[names[0]] | bits[names[-1]], (1 << len(names)) - 1)
    for weighting, masses in weights.items():
        for term in controls:
            direct = sum((-1) ** (word & term).bit_count() * mass for word, mass in masses.items())
            assert tables[weighting][term] == direct
    routed = local_products(supports, names, bits)
    factors = [2 ** (len(support) - 1) - 1 for support in supports]
    equal = tables[EQUAL]
    assert equal[0] == 2 * prod(factors)
    for term, local in enumerate(routed):
        if term.bit_count() % 2:
            continue
        visited = [divisor for divisor, part in zip(factors, local, strict=True) if part]
        assert equal[term] * prod(visited) == (-1) ** len(visited) * equal[0]

    w1 = {weighting: defaultdict(Counter) for weighting in tables}
    w1_exceptions = {weighting: [] for weighting in tables}
    for x, y in combinations(names, 2):
        mask = bits[x] | bits[y]
        visited = [divisor for divisor, part in zip(factors, routed[mask], strict=True) if part]
        length = len(visited)
        assert all(not part or part.bit_count() == 2 for part in routed[mask])
        predicted = Fraction((-1) ** length, prod(visited))
        for weighting, table in tables.items():
            exact = Fraction(table[mask], table[0])
            agrees = exact == predicted
            w1[weighting][length]['comparisons'] += 1
            w1[weighting][length]['matched'] += agrees
            if agrees and weighting == COMPLETIONS:
                w1[weighting][length].setdefault('matching distinctions', []).append((x, y))
            if not agrees and len(w1_exceptions[weighting]) < 5:
                w1_exceptions[weighting].append((supports, x, y, str(exact), str(predicted)))

    w2 = check_w2(supports, bits, neighbors, tables, routed)
    return {
        'start': index, 'supports': supports, 'places per knot': list(map(len, supports)),
        'distinctions': len(names), 'source states': len(states),
        'weighted masses': {weighting: table[0] for weighting, table in tables.items()},
        'different integer masses': {weighting: len(set(masses.values())) for weighting, masses in weights.items()},
        'equal even moments checked by local products': len(equal) // 2,
    }, w1, w1_exceptions, w2


def count_record(counts):
    return dict(counts, failed=counts['comparisons'] - counts['independent'])


def summarize(results):
    rows = []
    scope = defaultdict(Counter)
    w1_summary = defaultdict(Counter)
    w2_summary = defaultdict(Counter)
    route_summary = defaultdict(Counter)
    connection_summary = defaultdict(Counter)
    connected_controls_summary = defaultdict(Counter)
    distinct_summary = Counter()
    first = {}
    raw = {'tree-shaped census starts': len(results)}
    for weighting in (EQUAL, COMPLETIONS):
        raw[weighting] = {'W1': Counter(), 'W1 exceptions': [], 'W2': Counter(), 'W2 exceptions': []}

    for row, w1, w1_exceptions, w2_result in results:
        (across, connected_counts, unique_pairs, exceptions, first_failures,
         scopes, route_cases, connected_controls) = w2_result
        places = 'three places only' if max(row['places per knot']) == 3 else 'at least one knot with four or more places'
        row['place group'] = places
        row['carrier sets'] = [{'held unions': unions, 'connectedness': connected, 'count kind': kind, 'count': count}
                               for (unions, connected, kind), count in sorted(scopes.items())]
        scope[places].update(scopes)
        if COMPLETIONS not in w1:
            raw[COMPLETIONS]['W1']['not grown'] += 1
        row['W1 by knots on route'] = w1
        row['W2 for disjoint held unions and two-by-two products'] = {}
        for weighting, by_length in w1.items():
            for length, counts in by_length.items():
                w1_summary[weighting, length].update({k: counts[k] for k in ('comparisons', 'matched')})
                raw[weighting]['W1']['pairs'] += counts['comparisons']
                raw[weighting]['W1']['equal to the route product'] += counts['matched']
            old = raw[weighting]['W1 exceptions']
            old.extend(w1_exceptions[weighting][:5 - len(old)])

            row_frozen = {}
            for (domain, sizes, location), counts in across[weighting].items():
                key = weighting, places, domain, sizes, location
                total = w2_summary[key]
                total.update(counts)
                total['starts with comparisons'] += counts['comparisons'] > 0
                total['starts with failures'] += counts['independent'] < counts['comparisons']
                if counts['independent'] < counts['comparisons']:
                    first.setdefault(key, {'start': row['start'], 'supports': row['supports'],
                                           **first_failures[weighting][domain, sizes, location]})
                if domain == DISJOINT and sizes == (2, 2):
                    raw[weighting]['W2']['pairs of functions'] += counts['comparisons']
                    raw[weighting]['W2']['independent'] += counts['independent']
                    distinct = len(unique_pairs[weighting][location])
                    total['distinct product pairs within starts'] += distinct
                    row_frozen[location] = dict(count_record(counts), distinct_pairs=distinct)
            row['W2 for disjoint held unions and two-by-two products'][weighting] = row_frozen
            all_unique = set().union(*unique_pairs[weighting].values())
            row_frozen['distinct product pairs regardless of carrier'] = len(all_unique)
            distinct_summary[weighting] += len(all_unique)
            connected_controls_summary[weighting].update(connected_controls[weighting])
            for (location, connectedness), counts in connected_counts[weighting].items():
                summary = connection_summary[weighting, places, location, connectedness]
                summary.update(counts)
                summary['starts with comparisons'] += 1
                summary['starts with failures'] += counts['independent'] < counts['comparisons']
            old = raw[weighting]['W2 exceptions']
            old.extend(exceptions[weighting][:5 - len(old)])

        for (location, connectedness, joint_sizes), count in route_cases.items():
            stats = route_summary[places, location, connectedness, joint_sizes]
            stats['failures'] += count
            stats['starts with failures'] += 1
        rows.append(row)

    return {
        'weightings and raw census fields': raw,
        'W1 by number of knots on the route': [
            {'weighting': weighting, 'knots on route': length, **counts}
            for (weighting, length), counts in sorted(w1_summary.items())
        ],
        'W2 eligibility and thresholds': [
            {'weighting': weighting, 'place group': places, 'domain': domain,
             'product sizes': sizes, 'location': location, **count_record(counts)}
            for (weighting, places, domain, sizes, location), counts in sorted(w2_summary.items())
        ],
        'W2 recorded scope by connection within knot sets': [
            {'weighting': weighting, 'place group': places, 'location': location,
             'connection within knot sets': connectedness, **count_record(counts)}
            for (weighting, places, location, connectedness), counts in sorted(connection_summary.items())
        ],
        'W2 both knot sets connected, all product sizes and held unions': {
            weighting: count_record(counts) for weighting, counts in connected_controls_summary.items()
        },
        'W2 distinct product pairs in the recorded test, summed across starts': distinct_summary,
        'Equal W2 failures at jointly used knots, recorded scope': [
            {'place group': places, 'location': location, 'connection within knot sets': connectedness,
             'joint product sizes at jointly used knots': joint_sizes, **counts}
            for (places, location, connectedness, joint_sizes), counts in sorted(route_summary.items())
        ],
        'W2 first failure per eligibility cell': [
            {'weighting': weighting, 'place group': places, 'domain': domain,
             'product sizes': sizes, 'location': location, **example}
            for (weighting, places, domain, sizes, location), example in sorted(first.items())
        ],
        'carrier pair scopes by place count': [
            {'place group': places, 'held unions': unions, 'connectedness': connected,
             'count kind': kind, 'count': count}
            for places, scopes in sorted(scope.items())
            for (unions, connected, kind), count in sorted(scopes.items())
        ],
        'tree rows': rows,
    }


def compare_records(rebuilt, reported, path=()):
    if isinstance(rebuilt, dict) and isinstance(reported, dict):
        if rebuilt.keys() != reported.keys():
            yield path, sorted(rebuilt.keys()), sorted(reported.keys())
        for field in rebuilt.keys() & reported.keys():
            yield from compare_records(rebuilt[field], reported[field], (*path, field))
    elif isinstance(rebuilt, list) and isinstance(reported, list):
        if len(rebuilt) != len(reported):
            yield path, len(rebuilt), len(reported)
        for index, (left, right) in enumerate(zip(rebuilt, reported)):
            yield from compare_records(left, right, (*path, index))
    elif rebuilt != reported:
        yield path, rebuilt, reported


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    started = perf_counter()
    entries, scope = source_rows()
    if args.pilot:
        for size in (3, 4, 5):
            candidates = [entry for entry in entries if len(entry[1]) == size]
            entry = max(candidates, key=lambda item: sum(map(len, item[1])))
            run_start = perf_counter()
            row, _, _, _ = analyze(*entry)
            print(f"{row['start']} with {size} knots and {row['distinctions']} distinctions ran in "
                  f"{perf_counter() - run_start:.3f} s, with {len(candidates)} eligible starts of this size")
        print(f'Pilot including source checks: {perf_counter() - started:.3f} s')
        return

    report = summarize([analyze(*entry) for entry in entries])
    report['source scope'] = scope
    report['decision rules'] = {
        'W1': 'The exact mean equals the product of the knot factors on the unique route.',
        'W2': 'The joint signed sum times the mass equals the product of the two separate signed sums.',
        'inside': 'Each selected distinction has all of its holders in its own knot set.',
        'exposed': 'At least one selected distinction also has a holder outside its own knot set.',
        'W2 unit': 'A pair of products with its unordered pair of nonempty disjoint knot sets.',
        'constant term': 'A product of zero signs is identically one and independent under each weighting.',
        'exception records': 'The archive keeps the first five exceptions per test and weighting. '
                             'The denominator includes every tested pair.',
        'local product check': 'For each even product, collect the routes from its distinctions to one fixed distinction '
                               'and cancel repeated places at each knot in pairs. Under the equal weighting its mean '
                               'is the product of the local factors for knots with a nonempty remainder.',
        'joint sizes': 'At a knot used by both products, size zero records cancellation, size two a two-place product, '
                       'and size four a four-place product.',
    }
    rebuilt = json.loads(json.dumps(report['weightings and raw census fields']))
    reported = json.loads(REPORTED.read_text())
    archive_scope = {key: reported[key] for key in rebuilt}
    differences = list(compare_records(rebuilt, archive_scope))
    report['comparison with weights.json'] = {
        'census keys checked': list(rebuilt),
        'all nested fields and exception entries match': not differences,
        'differences': differences,
        'ring keys outside census comparison': sorted(reported.keys() - rebuilt.keys()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'comparison with weights.json': report['comparison with weights.json'],
                      'seconds including source checks': round(perf_counter() - started, 3)}, indent=2))
    if differences:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
