"""Recount the source census by Boolean truth tables and reconstruct its order."""

import argparse
from collections import Counter, defaultdict
from functools import cache, reduce
from hashlib import sha256
from itertools import combinations, islice, permutations, product
import json
from operator import and_, or_, xor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
START_ARCHIVE = ROOT / 'research/FORBID-EDITS-20261126-001/starts.json'
RESULT_ARCHIVE = HERE.parent / 'census.jsonl'
OUTPUT = HERE / 'source_census.json'


@cache
def archived_inputs():
    return tuple((size, tuple(map(tuple, meetings)), tuple(loose))
                 for size, meetings, loose in json.loads(START_ARCHIVE.read_text()))


def numbered_supports(size, meetings, loose_counts):
    supports = [[] for _ in range(size)]
    next_name = 0
    for a, b, count in meetings:
        shared = range(next_name, next_name + count)
        supports[a].extend(shared)
        supports[b].extend(shared)
        next_name += count
    for support, count in zip(supports, loose_counts, strict=True):
        support.extend(range(next_name, next_name + count))
        next_name += count
    return tuple(map(tuple, supports))


@cache
def load_starts():
    """The recorded knot supports in the zero-based order used by the output."""
    return tuple(numbered_supports(*entry) for entry in archived_inputs())


def one_meeting_component(size, occupied):
    groups = [1 << knot for knot in range(size)]
    for a, b in occupied:
        joined = groups[a] | groups[b]
        for knot in range(size):
            if joined & (1 << knot):
                groups[knot] = joined
    return groups[0].bit_count() == size


def reconstructed_inputs(size):
    """Visit first admitted presentations in the source's enumeration order."""
    pairs = tuple(combinations(range(size), 2))
    renamings = tuple(permutations(range(size)))
    seen_meeting_patterns = set()
    for occupied_count in range(size - 1, len(pairs) + 1):
        for occupied in combinations(pairs, occupied_count):
            if not one_meeting_component(size, occupied):
                continue
            for copies in product((1, 2), repeat=occupied_count):
                shared = sum(copies)
                if shared > 12:
                    continue
                meetings = tuple((a, b, count) for (a, b), count in
                                 zip(occupied, copies, strict=True))
                if meetings in seen_meeting_patterns:
                    continue

                renamed = defaultdict(list)
                for names in renamings:
                    presentation = tuple(sorted((min(names[a], names[b]),
                                                 max(names[a], names[b]), count)
                                                for a, b, count in meetings))
                    renamed[presentation].append(names)
                seen_meeting_patterns.update(renamed)
                first = min(renamed)
                maps_to_first = [tuple(names.index(i) for i in range(size))
                                 for names in renamed[first]]

                held = [0] * size
                for a, b, count in meetings:
                    held[a] += count
                    held[b] += count
                loose_options = [range(max(0, 3 - degree), 3) for degree in held]
                seen_loose = set()
                for loose in product(*loose_options):
                    if shared + sum(loose) > 12:
                        continue
                    canonical = min(tuple(loose[old] for old in old_names)
                                    for old_names in maps_to_first)
                    if canonical not in seen_loose:
                        seen_loose.add(canonical)
                        yield size, first, canonical


@cache
def truth_tables(width):
    """A truth table has bit s set when the statement holds in assignment s."""
    full = (1 << (1 << width)) - 1
    by_name = []
    for name in range(width):
        stride = 1 << name
        zeros = ((1 << stride) - 1) * (full // ((1 << (2 * stride)) - 1))
        by_name.append((zeros, full ^ zeros))
    return full, tuple(by_name)


def state_tables(supports, width):
    full, by_name = truth_tables(width)
    nae = parity = full
    for support in supports:
        ones = [by_name[name][1] for name in support]
        same = reduce(and_, ones) | (full ^ reduce(or_, ones))
        nae &= full ^ same
        parity &= full ^ reduce(xor, ones)
    return nae, parity


def assignment_numbers(table):
    while table:
        lowest = table & -table
        yield lowest.bit_length() - 1
        table ^= lowest


def component_count(allowed, by_name):
    count = 0
    remaining = allowed
    while remaining:
        reached = remaining & -remaining
        while True:
            before = reached
            for name, (zeros, ones) in enumerate(by_name):
                stride = 1 << name
                one_change = ((reached & zeros) << stride) | ((reached & ones) >> stride)
                reached |= remaining & one_change
            if reached == before:
                break
        remaining ^= reached
        count += 1
    return count


def pair_is_free(allowed, by_name, a, b):
    return all(allowed & a_value & b_value
               for a_value, b_value in product(by_name[a], by_name[b]))


def project(table, hidden, by_name):
    for name in hidden:
        zeros, ones = by_name[name]
        table = (table & zeros) | ((table & ones) >> (1 << name))
    return table


def meeting_category(size, meetings):
    ring = len(meetings) >= size
    doubled = any(count == 2 for _, _, count in meetings)
    if ring and doubled:
        return 'ring and doubled meeting'
    if ring:
        return 'ring without doubled meeting'
    if doubled:
        return 'doubled meeting without longer ring'
    return 'tree-shaped'


def alternating_missing(supports, meetings, loose):
    """Independently predict the two absent patterns on the tree's loose distinctions."""
    colors = {0: 0}
    pending = list(meetings)
    while pending:
        a, b, _ = pending.pop(0)
        if a in colors:
            colors[b] = 1 - colors[a]
        elif b in colors:
            colors[a] = 1 - colors[b]
        else:
            pending.append((a, b, 1))
    loose_names = set(loose)
    first = sum(1 << d for knot, row in enumerate(supports) if colors[knot]
                for d in row if d in loose_names)
    opposite = first ^ sum(1 << d for d in loose)
    return (1 << first) | (1 << opposite)


def literal_control(supports, width):
    """Scalar enumeration checks the truth-table construction on small starts."""
    nae = parity = 0
    for state in range(1 << width):
        ones = [sum((state >> d) & 1 for d in row) for row in supports]
        if all(0 < number < len(row) for number, row in zip(ones, supports, strict=True)):
            nae |= 1 << state
        if all(number % 2 == 0 for number in ones):
            parity |= 1 << state
    return nae, parity


def measure(entry, supports):
    size, meetings, loose_counts = entry
    shared = sum(count for _, _, count in meetings)
    width = shared + sum(loose_counts)
    loose = range(shared, width)
    full, by_name = truth_tables(width)
    nae, parity = state_tables(supports, width)
    hidden = range(shared)
    loose_nae = project(nae, hidden, by_name)
    loose_parity = project(parity, hidden, by_name)
    loose_universe = project(full, hidden, by_name)
    odd = reduce(xor, (by_name[d][1] for d in loose), 0)

    pairs, tied = Counter(), Counter()
    co_knotted = {pair for support in supports for pair in combinations(support, 2)}
    for a, b in combinations(range(width), 2):
        kind = ('shared + shared', 'loose + shared', 'loose + loose')[(a >= shared) + (b >= shared)]
        occurrence = 'co-knotted' if (a, b) in co_knotted else 'without common knot'
        incidence = f'{kind}, {occurrence}'
        pairs[incidence] += 1
        if not pair_is_free(nae, by_name, a, b):
            tied[incidence] += 1

    return {
        'width': width,
        'loose': tuple(loose),
        'category': meeting_category(size, meetings),
        'arity_profile': tuple(sorted(map(len, supports))),
        'states': (nae, parity),
        'NAE components': component_count(nae, by_name),
        'NAE loose projection': loose_nae,
        'loose universe': loose_universe,
        'parity loose projection': loose_parity,
        'parity projection is exactly even': loose_parity == loose_universe & ~odd,
        'pair incidence': pairs,
        'restricted pairs': tied,
    }


def select_pilot(archive):
    """Include both ends of every knot-count and distinction-count cell."""
    by_size = defaultdict(list)
    for rank, (size, meetings, loose) in enumerate(archive):
        width = sum(copies for _, _, copies in meetings) + sum(loose)
        by_size[size, width].append(rank)
    return sorted({ranks[index] for ranks in by_size.values() for index in (0, -1)})


def verify_output(archive, raw, ranks):
    totals = Counter()
    factors = defaultdict(Counter)
    incidence, restricted_pairs = Counter(), Counter()
    grown_rosters = Counter()
    source_state_ranges = defaultdict(list)
    tree_cases, grown_ranks, mismatches = [], [], []
    for i in ranks:
        entry = archive[i]
        size, meetings, _ = entry
        supports = load_starts()[i]
        checked = measure(entry, supports)
        row = raw[i]
        width = checked['width']
        loose = checked['loose']
        m = len(loose)
        category = checked['category']
        tree = category == 'tree-shaped'
        c1 = checked['NAE components'] == 1
        c2 = not checked['restricted pairs']
        patterns = checked['NAE loose projection'].bit_count()
        predicted = 2 ** m - (2 if tree else 0)
        even = checked['parity loose projection'].bit_count() if m else None
        exact = {
            'start': f'census {i}', 'C1': c1, 'C2': c2, 'loose': m, 'tree-shaped': tree,
            'C3 patterns': patterns, 'C3 predicted': predicted, "C3' parity patterns": even,
        }
        for field, value in exact.items():
            if row.get(field) != value or field not in row:
                mismatches.append({'source_rank': i, 'field': field,
                                   'recorded': row.get(field), 'recomputed': value})

        totals['starts'] += 1
        totals['C1 fails'] += not c1
        totals['C1 starts with more than one allowed state'] += checked['states'][0].bit_count() > 1
        totals['C2 fails'] += not c2
        totals['C3 fails on starts with loose distinctions'] += bool(m) and patterns != predicted
        totals['C3 zero-loose projections with one pattern'] += not m and patterns == 1
        totals['C3 positive-loose starts'] += bool(m)
        totals['C3 tree-shaped starts'] += tree
        totals['C3 other positive-loose starts'] += bool(m) and not tree
        totals['C3 other starts with at least three loose distinctions'] += m >= 3 and not tree
        totals['C3 candidate loose words, summed over positive-loose starts'] += 2 ** m if m else 0
        totals['C3 missing loose words, summed over positive-loose starts'] += 2 ** m - patterns if m else 0
        totals["C3' fails on starts with loose distinctions"] += bool(m) and even != 2 ** (m - 1)
        totals["C3' projections equal the even loose words"] += checked['parity projection is exactly even']
        totals['checked against literal enumeration'] += width <= 8
        if width <= 8 and checked['states'] != literal_control(supports, width):
            raise ValueError(f'Scalar and truth-table states differ on census source rank {i}')
        incidence.update(checked['pair incidence'])
        restricted_pairs.update(checked['restricted pairs'])
        for law, states in zip(('not-all-equal', 'parity'), checked['states'], strict=True):
            source_state_ranges[law].append(states.bit_count())

        grown = row.get('C4 after one round')
        record_grown = grown is not None
        if record_grown:
            occurred, possible = grown
            if possible < 1 or possible & (possible - 1) or not 0 <= occurred <= possible:
                raise ValueError(f'Malformed C4 on census source rank {i}: {grown}')
            grown_ranks.append(i)
            grown_rosters[possible.bit_length() - 1] += 1
            totals['C4 recorded'] += 1
            totals['C4 recorded failures'] += occurred != possible
            totals['C4 recorded after a tree-shaped start'] += tree
            totals['C4 possible loose words across recorded stages'] += possible

        for factor, level in (('knots', size), ('distinctions', width), ('loose distinctions', m),
                              ('meeting category', category),
                              ('knot arities', 'all three-place' if max(checked['arity_profile']) == 3
                               else 'includes a knot with at least four places')):
            group = factors[factor, level]
            group['starts'] += 1
            group['tree-shaped'] += tree
            group['starts with loose distinctions'] += bool(m)
            group['starts with at least three loose distinctions'] += m >= 3
            group['distinction pairs checked'] += sum(checked['pair incidence'].values())
            group['C4 recorded'] += record_grown

        if tree:
            missing = checked['loose universe'] ^ checked['NAE loose projection']
            alternates = missing == alternating_missing(supports, meetings, loose)
            totals['tree-shaped starts with exactly the alternating patterns missing'] += alternates
            tree_cases.append({'census_source_rank': i, 'knot_supports': supports, 'loose': loose,
                               'missing_words': [''.join(str((state >> name) & 1) for name in loose)
                                                 for state in assignment_numbers(missing)],
                               'alternating_by_holder': alternates, 'C4 recorded': record_grown})

    return {
        'totals': dict(totals),
        'raw_start_field_mismatches': mismatches,
        'source_state_counts': {law: {'total': sum(counts), 'min': min(counts), 'max': max(counts)}
                                for law, counts in source_state_ranges.items()},
        'source_pair_totals': {'checked': sum(incidence.values()), 'restricted': sum(restricted_pairs.values())},
        'source_pair_incidence': {key: {'candidates': count, 'restricted': restricted_pairs[key]}
                                  for key, count in sorted(incidence.items())},
        'by_source_factor': {factor: {level: dict(counts) for (kind, level), counts in factors.items()
                                      if kind == factor}
                             for factor in sorted({kind for kind, _ in factors})},
        'tree_shaped_sources': tree_cases,
        'C4_recorded_selection': {
            'evidence': 'Selection and denominators from the recorded fields. Growth is checked separately.',
            'first_census_source_rank': min(grown_ranks, default=None),
            'last_census_source_rank': max(grown_ranks, default=None),
            'sources_without_C4_through_last_rank': max(grown_ranks, default=-1) + 1 - len(grown_ranks),
            'sources_after_last_rank': len(archive) - 1 - max(grown_ranks, default=-1),
            'stages_by_new_loose_count': dict(sorted(grown_rosters.items())),
            'stages_with_at_least_three_loose_distinctions': sum(count for m, count in grown_rosters.items() if m >= 3),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='time short matching census and source checks')
    args = parser.parse_args()
    archive = archived_inputs()
    with RESULT_ARCHIVE.open() as handle:
        *raw, original_tally = (json.loads(line) for line in handle)
    if len(raw) != len(archive):
        raise ValueError(f'{len(raw)} result rows for {len(archive)} archived starts')

    rebuilt_count = 0
    for size in (3, 4, 5):
        archived_size = [entry for entry in archive if entry[0] == size]
        rebuilt = reconstructed_inputs(size)
        if args.pilot:
            rebuilt = islice(rebuilt, 12)
            archived_size = archived_size[:12]
        for rank, (found, expected) in enumerate(zip(rebuilt, archived_size, strict=True)):
            if found != expected:
                raise ValueError(f'Order mismatch on the size-{size} census at local rank {rank}')
            rebuilt_count += 1
    if sorted(archive, key=lambda entry: entry[0]) != list(archive):
        raise ValueError('The archive does not group sizes in the recorded order')

    _, small_truth = truth_tables(3)
    two_tied = (1 << 0) | (1 << 7)
    if component_count(two_tied, small_truth) != 2 or pair_is_free(two_tied, small_truth, 0, 1):
        raise ValueError('Readers did not detect the disconnected, tied negative control')

    ranks = select_pilot(archive) if args.pilot else range(len(archive))
    result = verify_output(archive, raw, ranks)
    totals = result['totals']
    if args.pilot:
        print(json.dumps({'independently_ordered_starts': rebuilt_count, **totals}, indent=2))
        if result['raw_start_field_mismatches']:
            raise SystemExit('Pilot found a recorded field discrepancy')
        return

    recomputed_tally = {
        'starts': totals['starts'], 'C1 fails': totals['C1 fails'], 'C2 fails': totals['C2 fails'],
        'C3 fails': totals['C3 fails on starts with loose distinctions'],
        "C3' fails": totals["C3' fails on starts with loose distinctions"],
        'C4 read': totals['C4 recorded'], 'C4 fails': totals['C4 recorded failures'],
    }
    result['inputs'] = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                        for path in (START_ARCHIVE, RESULT_ARCHIVE)}
    result['census_generation'] = {
        'limits': 'Connected starts of three to five knots with at most twelve distinctions, '
                  'at least three places per knot, at most two loose distinctions per knot, '
                  'and one or two shared distinctions per meeting pair.',
        'order': 'First admissible source enumerations in knot count, occupied-pair count, '
                 'lexical occupied pairs, multiplicities and loose counts. The reported '
                 'start is the least renaming by its meeting list and then loose counts. '
                 'Shared distinction names precede loose names.',
        'exact_order_comparisons': rebuilt_count,
        'raw_source_records': len(raw),
    }
    result['controls'] = {
        'truth_tables': 'Literal state enumeration for both laws on every source with up to eight distinctions.',
        'C1 and C2': 'A supplied three-distinction relation with only 000 and 111 has '
                     'two single-change classes and a tied pair. Both readers detected the failure.',
        'C3 independent opportunities': 'With at least three loose distinctions a missing word can '
                                        'survive the every-pair-free check. With two or fewer, '
                                        'pair freedom, complement symmetry or nonemptiness suffice.',
    }
    result['raw_tally'] = original_tally['tally']
    result['recomputed_tally'] = recomputed_tally
    result['raw_tally_matched'] = original_tally == {'tally': recomputed_tally}
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'independently_ordered_starts': rebuilt_count, **totals}, indent=2))
    if result['raw_start_field_mismatches'] or not result['raw_tally_matched']:
        raise SystemExit('The recount found recorded discrepancies')


if __name__ == '__main__':
    main()
