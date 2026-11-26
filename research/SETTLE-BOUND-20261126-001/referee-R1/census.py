"""Check the census order, the recorded selection and the earlier parity census."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import comb
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from time import monotonic

from networkx.generators.atlas import graph_atlas_g


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PREDECESSOR = STUDY.parent / 'LOOK-ALIKE-20261126-001'
BALANCE = (STUDY.parents[1] / 'artifacts' / 'RING-IN-BALANCE-20261123-001B'
           / 'RING-IN-BALANCE-20261123-001B-E001_reference' / 'census')
SEED = 20261126
SLACK = {'sig0': 5, 'sig1': 7}
BALANCE_BLOCK = 200


def reach(neighbours, first, allowed):
    visited = first
    while True:
        extended = visited
        for knot, related in enumerate(neighbours):
            if visited & (1 << knot):
                extended |= related & allowed
        if extended == visited:
            return visited
        visited = extended


def meetings(knots, pairs):
    masks = [0] * knots
    for first, second in pairs:
        masks[first] |= 1 << second
        masks[second] |= 1 << first
    return masks


def enumerate_starts(knots, atlas, pilot):
    beginning = monotonic()
    possible = list(combinations(range(knots), 2))
    pair_bit = {pair: 1 << index for index, pair in enumerate(possible)}
    perms = list(permutations(range(knots)))
    all_knots = (1 << knots) - 1
    atlas_cases = []
    for index, graph in enumerate(atlas):
        if len(graph) != knots:
            continue
        pairs = tuple(sorted(tuple(sorted(pair)) for pair in graph.edges))
        neighbours = meetings(knots, pairs)
        if reach(neighbours, 1, all_knots) == all_knots:
            atlas_cases.append((index, pairs, neighbours))

    roster, atlas_pairs = [], {}
    numbered = set()
    no_loose = []
    selected = atlas_cases[:8] if pilot else atlas_cases
    for index, pairs, neighbours in selected:
        atlas_pairs[index] = pairs
        base = sum(pair_bit[pair] for pair in pairs)
        aliases = set()
        symmetries = []
        for order in perms:
            image = sum(pair_bit[tuple(sorted((order[a], order[b])))] for a, b in pairs)
            aliases.add(image)
            if image == base:
                symmetries.append(order)
        assert not (numbered & aliases), (knots, index)
        numbered.update(aliases)
        domains = [range(max(0, 3 - count.bit_count()), 4) for count in neighbours]
        seen = set()
        for loose in product(*domains):
            if loose in seen:
                continue
            if not any(loose):
                no_loose.append(index)
                continue
            seen.update(tuple(loose[i] for i in order) for order in symmetries)
            roster.append((index, loose))

    mask_count = 1 << len(possible)
    numbered_check = set()
    checked = range(min(mask_count, 4096) if pilot else mask_count)
    for mask in checked:
        pairs = [pair for index, pair in enumerate(possible) if mask & (1 << index)]
        if reach(meetings(knots, pairs), 1, all_knots) == all_knots:
            numbered_check.add(mask)
    if not pilot:
        assert numbered_check == numbered, knots
    stats = {'atlas_patterns_enumerated': len(selected), 'atlas_patterns_available': len(atlas_cases),
             'numbered_patterns_checked': len(checked), 'numbered_patterns_available': mask_count,
             'connected_numbered_patterns_among_check': len(numbered_check),
             'starts': len(roster), 'excluded_without_loose_distinctions': no_loose,
             'with_dead_knot': sum(0 in loose for _, loose in roster),
             'seconds': round(monotonic() - beginning, 4)}
    return roster, atlas_pairs, stats


def holdings(pairs, loose):
    stars = [[] for _ in loose]
    for distinction, (first, second) in enumerate(pairs):
        stars[first].append(distinction)
        stars[second].append(distinction)
    distinction = len(pairs)
    for knot, count in enumerate(loose):
        stars[knot].extend(range(distinction, distinction + count))
        distinction += count
    return stars


def dimension(counts, greatest_dimension):
    differences = counts[-8:]
    for value in range(1, greatest_dimension + 1):
        if len(set(differences)) == 1 and differences[0] > 0:
            return value
        differences = [b - a for a, b in zip(differences, differences[1:])]
    return None


def kind(counts, ending):
    if ending.startswith(('stalls', 'closes')):
        return ending.split()[0]
    if len(counts) < 10:
        return 'unread'
    label = dimension(counts, 4)
    if label is not None:
        return f'dim {label}'
    ratios = [Fraction(b, a) for a, b in zip(counts[-5:], counts[-4:])]
    if min(ratios) > Fraction(105, 100) and max(ratios) - min(ratios) < Fraction(1, 100):
        return f'rate {float(ratios[-1]):.2f}'
    return 'unread'


def fingerprint(value):
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def read_archive(path, stride=1):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as source:
        for position, line in enumerate(source):
            if position % stride == 0:
                yield position, json.loads(line)


def endings(record, counts, knots, horizon):
    ending = record['end']
    total = knots + sum(counts)
    assert all(count > 0 for count in counts) and record['knots'] == total, record['index']
    assert len(counts) <= horizon, record['index']
    if ending == 'bound':
        assert total > 30000 >= total - counts[-1], record['index']
    else:
        assert total <= 30000, record['index']
    if ending.startswith(('stalls ', 'closes ')):
        assert ending in {f'stalls at round {len(counts) + 1}',
                          f'closes at round {len(counts) + 1}'}, record['index']
        assert len(counts) < horizon, record['index']
    elif ending == 'rounds':
        assert len(counts) == horizon, record['index']
    else:
        assert ending in {'bound', 'guard'}, record['index']
    return ending.split()[0]


def select_archive(knots, law, census, pairs, order, pilot):
    beginning = monotonic()
    path = STUDY / f'grown_g{knots}_{law}.jsonl.gz'
    total_counts, kinds_at_stop, endpoints = (Counter() for _ in range(3))
    dimensions_past_four = defaultdict(list)
    records = {}
    for position, entry in read_archive(path, 64 if pilot else 1):
        index = entry['index']
        assert entry['n knots'] == knots and entry['knot law'] == ('parity' if law == 'par' else 'nae')
        assert index not in records, (path.name, index)
        if not pilot:
            graph, loose = census[index]
            assert index == order[position], (path.name, position, index, order[position])
            assert (graph, list(loose)) == (entry['graph'], entry['loose']), index
            assert holdings(pairs[graph], loose) == entry['stars'], index
        counts = [row['n'] for row in entry['rows']]
        stop = endings(entry, counts, knots, 24)
        label = kind(counts, entry['end'])
        assert label == entry['kind'], (path.name, index, label, entry['kind'])
        total_counts[label] += 1
        kinds_at_stop[stop, label] += 1
        endpoints[stop, len(counts)] += 1
        if label == 'unread' and len(counts) >= 10:
            higher = dimension(counts, 6)
            if higher is not None:
                dimensions_past_four[higher].append(index)
        cuts = {reading: entry['M'] + slack for reading, slack in SLACK.items()}
        trace = (fingerprint((entry['rows'], entry['end'], entry['knots']))
                 if (knots, law) == (5, 'nae') else None)
        records[index] = {'kind': label, 'end': stop, 'n': len(counts),
                          'cut': cuts, 'trace': trace}

    stats = {'records_read': len(records), 'kinds': dict(total_counts),
             'kinds_by_run_ending': joined(kinds_at_stop),
             'endings_by_number_of_saved_rounds': joined(endpoints),
             'unread_passing_higher_count_dimension_screen': dict(dimensions_past_four),
             'seconds': round(monotonic() - beginning, 4)}
    if not pilot:
        assert len(records) == len(order), path.name
        stats['order_and_holdings_match_expected_roster'] = True
        selected = {index: row for index, row in records.items() if row['kind'].startswith('dim ')}
        published = json.loads((STUDY / f'test_g{knots}_{law}.json').read_text())
        assert len(selected) == published['starts of a dimension'], path.name
        assert Counter(row['kind'] for row in selected.values()) == published['kinds'], path.name
        stats.update(selection(selected, published))
    return records, stats


def joined(counts):
    return {' / '.join(map(str, key)): value for key, value in sorted(counts.items())}


def selection(selected, published):
    beginning = monotonic()
    dimensions = defaultdict(list)
    for index, record in selected.items():
        dimensions[record['kind']].append((index, record))
    stats = {'dimension_starts': len(selected), 'dimension_denominator_matches_table': True,
             'all_same_dimension_pairs': sum(comb(len(xs), 2) for xs in dimensions.values()), 'readings': {}}
    for reading in SLACK:
        eligible, too_short = 0, 0
        affected = set()
        for ids in dimensions.values():
            for (aid, a), (bid, b) in combinations(ids, 2):
                if min(a['n'], b['n']) - max(a['cut'][reading], b['cut'][reading]) < 2:
                    too_short += 1
                    affected.update((aid, bid))
                    continue
                eligible += 1
        table = published['pairs']
        assert too_short == table.get(f'{reading} / not testable: too few rounds past the cut', 0)
        assert eligible == sum(table.get(f'{reading} / {key}', 0) for key in ('predicted', 'missed'))
        stats['readings'][reading] = {
            'pair_eligible': eligible, 'pair_too_short': too_short,
            'lacks_two_rounds_after_own_cut': sorted(
                index for index, row in selected.items() if row['n'] - row['cut'][reading] < 2
            ),
            'distinct_starts_in_too_short_pairs': len(affected),
        }
    stats['selection_seconds'] = round(monotonic() - beginning, 4)
    return stats


def look_alike_overlap(archives, pilot):
    beginning = monotonic()
    phase1 = Counter()
    for _, entry in read_archive(PREDECESSOR / 'phase1_grown.jsonl.gz', 8 if pilot else 1):
        counts = [row['n'] for row in entry['rows']]
        endings(entry, counts, entry['n knots'], 20)
        phase1[kind(counts, entry['end'])] += 1
    phase2 = archives[5, 'nae']
    matching = set()
    for _, entry in read_archive(PREDECESSOR / 'phase2_grown.jsonl.gz', 64 if pilot else 1):
        index = entry['index']
        if index not in phase2:
            continue
        assert phase2[index]['trace'] == fingerprint((entry['rows'], entry['end'], entry['knots'])), index
        matching.add(index)
    if not pilot:
        assert matching == phase2.keys()
    return {'phase_1_kinds': dict(phase1), 'phase_2_matching_five_knot_nae_traces': len(matching),
            'seconds': round(monotonic() - beginning, 4)}


def prior_balance_census(censuses, selected_orders, archives, pilot):
    beginning = monotonic()
    index_by_start = {n: {start: i for i, start in enumerate(censuses[n])} for n in (5, 6)}
    encountered = {5: set(), 6: set()}
    previous = {5: Counter(), 6: Counter()}
    previous_in_current = {5: Counter(), 6: Counter()}
    previous_in_current_by_kind = {5: Counter(), 6: Counter()}
    former_set_asides = {5: [], 6: []}
    selected = {n: set(selected_orders[n]) for n in (5, 6)}
    files = (BALANCE / 'results.jsonl.gz', BALANCE / 'extra_blocks.jsonl')
    for path in files:
        for _, block in read_archive(path):
            if block['status'] != 'ok' or block['case'][1] not in '56':
                continue
            n = int(block['case'][1])
            if pilot and block['case'] != f'n{n}-b0000':
                continue
            assert block['result']['rounds'] == 10 and block['result']['cap'] == 1500
            offset = BALANCE_BLOCK * block['result']['block']
            if block.get('start_range'):
                offset += block['start_range'][0]
            for expected, row in enumerate(block['result']['starts'], offset):
                start = (row['g'], tuple(row['loose']))
                if pilot and start not in index_by_start[n]:
                    continue
                index = index_by_start[n][start]
                assert index == expected and index not in encountered[n], (n, index, expected)
                encountered[n].add(index)
                assert row['set_aside'] != row['kt']['pass'], (n, index)
                if row['set_aside']:
                    state = 'set aside at initial parity knot test'
                elif row['laws']['ordinary'].get('not_completed'):
                    state = 'ordinary parity run incomplete'
                else:
                    state = 'ordinary parity run completed'
                previous[n][state] += 1
                if index in selected[n]:
                    previous_in_current[n][state] += 1
                    if row['set_aside']:
                        former_set_asides[n].append(index)
                    for law in ('nae', 'par'):
                        row_now = archives[n, law].get(index)
                        if row_now is not None:
                            previous_in_current_by_kind[n][state, law, row_now['kind']] += 1
    result = {}
    for n in (5, 6):
        flagged_late = {}
        if not pilot:
            assert len(encountered[n]) == len(censuses[n]), n
            earlier = set(former_set_asides[n])
            for law in ('nae', 'par'):
                table = json.loads((STUDY / f'test_g{n}_{law}.json').read_text())
                late = {row[0] for row in table['bound misses'] if row[4] is not None}
                flagged_late[law] = sorted(earlier & late)
        result[n] = {'earlier_roster': dict(previous[n]),
                     'earlier_status_of_current_study_starts': dict(previous_in_current[n]),
                     'earlier_status_of_current_starts_by_law_and_kind': joined(previous_in_current_by_kind[n]),
                     'earlier_set_asides_in_current_study': sorted(former_set_asides[n]),
                     'earlier_set_asides_among_reported_late_starts': flagged_late}
    return {'sizes': result, 'seconds': round(monotonic() - beginning, 4)}


def main(pilot):
    beginning = monotonic()
    atlas = graph_atlas_g()
    rosters, pairs, generation = {}, {}, {}
    for n in (5, 6):
        rosters[n], pairs[n], generation[n] = enumerate_starts(n, atlas, pilot)
    six = Random(SEED).sample(range(len(rosters[6])), min(1000, len(rosters[6])) if pilot else 1000)
    orders = {5: range(len(rosters[5])), 6: six}
    archives, stats = {}, {}
    for n in (5, 6):
        for law in ('nae', 'par'):
            records, run = select_archive(n, law, rosters[n], pairs[n], orders[n], pilot)
            archives[n, law], stats[f'g{n}_{law}'] = records, run
    law_transfers = {}
    if not pilot:
        for n in (5, 6):
            left, right = archives[n, 'nae'], archives[n, 'par']
            assert left.keys() == right.keys(), n
            law_transfers[n] = {
                'kinds_under_not_all_equal_then_parity': joined(Counter(
                    (x['kind'], right[i]['kind']) for i, x in left.items()
                )),
                'endings_under_not_all_equal_then_parity': joined(Counter(
                    (x['end'], right[i]['end']) for i, x in left.items()
                )),
            }
    result = {
        'scope': 'timing only' if pilot else 'census, archive selection and prior census overlap',
        'shared_input': 'The graph atlas supplies the order and numbering. Coverage, renaming, loose counts, '
                        'sampling and archive checks are implemented here. Prior parity flags are read from the earlier '
                        'archive. Pair eligibility uses recorded M.',
        'census': generation,
        'six_knot_seed': SEED,
        'runs': stats,
        'law_transfers': law_transfers,
        'look_alike_overlap': look_alike_overlap(archives, pilot),
        'earlier_balance_census': prior_balance_census(rosters, orders, archives, pilot),
        'seconds': round(monotonic() - beginning, 4),
        'peak_rss_kib': getrusage(RUSAGE_SELF).ru_maxrss,
    }
    if not pilot:
        result['six_knot_census_order_sha256'] = fingerprint(rosters[6])
        result['six_knot_sample_indices_in_order'] = six
        result['six_knot_sample_identity_order_sha256'] = fingerprint([rosters[6][i] for i in six])
        result['six_knot_sample_not_grown'] = len(rosters[6]) - len(six)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    output = main(args.pilot)
    path = HERE / ('census_pilot.json' if args.pilot else 'census.json')
    path.write_text(json.dumps(output, indent=2) + '\n')
    print(path.name, output['seconds'], output['peak_rss_kib'])
