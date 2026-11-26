"""Recount the three follow-up archives without using their analysis code."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice, product
import json
from pathlib import Path
import re

from posthoc_structures import Seed, candidate_forms, group_ids, pairs_within


HERE = Path(__file__).resolve().parent
LATER = HERE.parent / 'checks/what_decides_the_class'
REGISTERED = HERE.parent.with_name(HERE.parent.name + 'A')
RUNS = next((HERE.parents[2] / 'artifacts' / REGISTERED.name).glob('*-E001*'))
FAMILIES = ('every_seed', 'registered_family', 'swap_family')
GROUPS = ('all', 'no taking rule', 'no taking rule; retire or offshoot', 'no taking rule; wait',
          'take of a sole candidate', 'held-out first seeds K-O', 'first seeds A-J')


def records(file):
    with gzip.open(file, 'rt') as source:
        yield from map(json.loads, source)


def key(spec):
    take = {'sole': 'MET-SOLE', 'MET-SOLE': 'MET-SOLE', 'none': 'none', None: 'none'}[spec['take']]
    return (spec['ration'], spec['treatment'], take, spec['first'])


def choose2(n):
    return n * (n - 1) // 2


def partitions_match(left, right):
    """Each label induces the same set of seed pairs, regardless of its name."""
    return len(set(zip(left, right))) == len(set(left)) == len(set(right))


def tally(groups, classes):
    together = sum(choose2(len(g)) for g in groups)
    same_class = sum(choose2(n) for g in groups
                     for n in Counter(classes[i] for i in g).values())
    return {'values': len(groups), 'pairs sharing it': together, 'of those told apart': together - same_class}


def first_difference(row, i, j):
    return next((r for r, labels in enumerate(row['class by round'], 1) if labels[i] != labels[j]), 'never')


def raw_registered(accepted, all_seeds):
    """Recover run-level FF 5, FF 5b and FF 11 readings also used by the registration."""
    source_names = {entry['name']: Seed.from_knots(entry).signature()
                    for family in all_seeds['second'].values() for entry in family}
    archive = defaultdict(dict)
    for runset in ('R1', 'R2', 'R3'):
        for file in sorted(RUNS.glob(f'runs_{runset}_*.jsonl.gz')):
            for run in records(file):
                study = key(run)
                if study not in accepted:
                    continue
                name = None if run['second'] is None else source_names[run['second']]
                # Each stored kind has its multiplicity last. Discard the own-descent
                # flag for mixed births after selecting entries not in the own descent.
                mixed = tuple(tuple(sorted(tuple(entry[:5] + entry[6:]) for entry in turn
                                           if not entry[5])) for turn in run['wider'])
                own = tuple(tuple(sorted(map(tuple, turn))) for turn in run['make'])
                result = (own, tuple(run['sec_only']), tuple(run['n_both']), mixed)
                assert all(len(series) == run['rounds_read'] for series in result)
                assert all(sum(entry[-1] for entry in turn) == count
                           for turn, count in zip(mixed, result[2]))
                previous = archive[study].get(name)
                if previous:
                    common = min(len(previous[0]), len(own))
                    assert all(a[:common] == b[:common] for a, b in zip(previous, result))
                if previous is None or len(previous[0]) < len(own):
                    archive[study][name] = result
    return archive


def load_roster(names, all_seeds):
    by_name = {entry['name']: Seed.from_knots(entry)
               for family in all_seeds['second'].values() for entry in family}
    seeds = [Seed.from_name(name) for name in names]
    for name, seed in zip(names, seeds):
        if name in by_name:
            assert seed == by_name[name], name
    profiles = [seed.profiles() for seed in seeds]
    groups = {profile: group_ids([p[profile] for p in profiles]) for profile in profiles[0]}
    return seeds, groups


def combined(accepted, rows):
    first = 'KLMNO' if accepted else 'ABCDEFGHIJ'
    return [row for row in rows if row['first'] in first]


def row_groups(rows):
    no_take = [r for r in rows if r['spec']['take'] is None]
    return dict(zip(GROUPS, (rows, no_take, [r for r in no_take if r['spec']['treatment'] != 'CANCEL-WAIT'],
                             [r for r in no_take if r['spec']['treatment'] == 'CANCEL-WAIT'],
                             [r for r in rows if r['spec']['take']], combined(True, rows), combined(False, rows))))


def sum_table(rows, profile_names):
    profiles = {}
    for name in profile_names:
        cells = [r['profiles'][name] for r in rows]
        profiles[name.split(':')[0]] = {
            'decides': sum(c['of those told apart'] == 0 for c in cells),
            'sharing': sum(c['pairs sharing it'] for c in cells),
            'told apart': sum(c['of those told apart'] for c in cells),
            'studies without a sharing pair': sum(c['pairs sharing it'] == 0 for c in cells)}
    return {'studies': len(rows), 'all pairs': sum(r['pairs'] for r in rows),
            'all told apart': sum(r['pairs told apart'] for r in rows), 'profiles': profiles}


def compare_printed(file, summary):
    headings, cells = 0, 0
    for line in file.read_text().splitlines():
        if line.startswith('== '):
            match = re.fullmatch(r'== (.*?) \| ([\d,]+) studies \| pairs ([\d,]+) \| told apart ([\d,]+)', line)
            group, *numbers = match.groups()
            expected = summary[group]
            assert list(map(lambda n: int(n.replace(',', '')), numbers)) == [
                expected['studies'], expected['all pairs'], expected['all told apart']], group
            headings += 1
        elif line.startswith('  ') and ':' in line:
            label = line.strip().split(':')[0]
            match = re.search(r'(\d+) of\s+(\d+) \|\s*([\d,]+) sharing \|\s*([\d,]+) apart \|\s*([\d.]+)%', line)
            if match is None:
                continue
            decides, studies, shared, apart = (int(n.replace(',', '')) for n in match.groups()[:4])
            expected_cell = expected['profiles'][label]
            assert (decides, studies, shared, apart) == (expected_cell['decides'], expected['studies'],
                    expected_cell['sharing'], expected_cell['told apart']), (group, label)
            assert match.group(5) == f'{(100 * apart/shared if shared else 0):.1f}', (group, label)
            cells += 1
    assert (headings, cells) == (len(GROUPS), len(GROUPS) * 16)
    return {'group headings compared': headings, 'profiles compared over all groups': cells}


def pair_timing(rows, pairs, names, detailed=True):
    observed, by_treatment = set(), defaultdict(list)
    per_law = defaultdict(set)
    for row in rows:
        rates = Counter()
        law = (row['spec']['take'] or 'none', row['spec']['treatment'])
        for i, j in pairs:
            r = first_difference(row, i, j)
            rates[str(r)] += 1
            if r != 'never':
                observed.add((names[i], names[j]))
                per_law[law].add((i, j))
        by_treatment[law].append((rates, row))
    strata = {}
    for key_, studies in sorted(by_treatment.items()):
        counts = sum((c for c, _ in studies), Counter())
        positives = [r for c, r in studies if c['never'] != len(pairs)]
        strata['/'.join(key_)] = {'studies': len(studies), 'opportunities': len(pairs) * len(studies),
                                   'studies with a difference': len(positives), 'first difference by round': counts,
                                   'distinct pairs told apart at least once': len(per_law[key_]),
                                   'common round': dict(Counter(r['R*'] for _, r in studies))}
        if detailed:
            strata['/'.join(key_)]['positive study settings'] = [key(r['spec']) for r in positives]
    return {'distinct pairs per study': len(pairs), 'distinct pairs told apart at least once': len(observed),
            'by law': strata}


def check_registered_overlap(rows, seeds, raw, family):
    signatures = [s.signature() for s in seeds]
    held = [s.held_triple() for s in seeds]
    summaries = []
    for row in rows:
        reference = raw[key(row['spec'])]
        common = row['R*']
        ids = [i for i, sign in enumerate(signatures) if sign in reference and len(reference[sign][0]) >= common]
        if not ids:
            continue
        series = [reference[signatures[i]] for i in ids]
        for r, labels in enumerate(row['class by round'], 1):
            assert partitions_match([labels[i] for i in ids], [s[0][:r] for s in series]), (key(row['spec']), r)
        final = [row['class by round'][-1][i] for i in ids]
        values = {'counts 1': [(held[i], s[1][:common]) for i, s in zip(ids, series)],
                  'shared 1': [(held[i], s[2][:common]) for i, s in zip(ids, series)],
                  'shared 2': [(held[i], s[3][:common]) for i, s in zip(ids, series)],
                  'shared 3': [s[3][:common] for s in series]}
        cells = {k: tally(group_ids(v), final) for k, v in values.items()}
        reported = {k.split(':')[0]: v for k, v in row['profiles'].items()}
        for label, cell in cells.items():
            if family == 'registered_family':
                assert len(ids) == len(seeds) and cell == reported[label], (key(row['spec']), label)
            else:
                assert all(cell[k] <= reported[label][k] for k in cell), (key(row['spec']), label)
        summaries.append((len(ids), common, cells['counts 1']))
    return {'studies compared': len(summaries), 'seed runs compared': sum(n for n, _, _ in summaries),
            'round-level partitions compared': sum(r for _, r, _ in summaries),
            'matched seeds per study': dict(Counter(n for n, _, _ in summaries)),
            'registered-profile counterexamples on the overlap': sum(c['of those told apart'] for _, _, c in summaries),
            'studies with an independent registered-profile counterexample from the overlap':
                sum(c['of those told apart'] > 0 for _, _, c in summaries)}


def compare_same_first_seeds(every, registered, raw):
    """Compare the 60-seed and 345-seed studies at the same first seeds and rounds."""
    old = {key(row['spec']): row for row in registered}
    size = len(registered[0]['names'])
    finished = [(row, old[key(row['spec'])]) for row in every if key(row['spec']) in old]
    counts, fits, fits_same_round = Counter(), Counter(), Counter()
    seeds = {name: Seed.from_name(name) for row in registered for name in row['names']}
    held_and_form = {name: (s.held_triple(), s.signature()) for name, s in seeds.items()}
    for larger, smaller in finished:
        positions = {name: i for i, name in enumerate(larger['names'])}
        ids = [positions[name] for name in smaller['names']]
        a, b = larger['R*'], smaller['R*']
        assert a <= b
        for longer, shorter in zip(larger['class by round'], smaller['class by round']):
            assert partitions_match([longer[i] for i in ids], shorter)
        chart_key = (a, b)
        counts[str(chart_key)] += 1
        a_fits, b_fits = (next(v['of those told apart'] == 0 for k, v in row['profiles'].items()
                               if k.startswith('counts 1:')) for row in (larger, smaller))
        fits[str((a_fits, b_fits))] += 1
        same_round_profiles = [(held, raw[key(smaller['spec'])][form][1][:a])
                               for held, form in (held_and_form[name] for name in smaller['names'])]
        labels = [larger['class by round'][-1][i] for i in ids]
        b_fits_at_a = tally(group_ids(same_round_profiles), labels)['of those told apart'] == 0
        fits_same_round[str((a_fits, b_fits_at_a))] += 1
    return {'matched studies': len(finished), 'same forms checked per common round': size,
            'class partitions matched through all shared rounds': len(finished),
            'common rounds as (345, 60)': counts, 'profile decides as (345, 60) at each family’s own horizon': fits,
            'profile decides as (345, 60) at the same horizon': fits_same_round}


def audit_family(family, rows, failed, all_seeds, raw, full):
    names = rows[0]['names']
    seeds, groups = load_roster(names, all_seeds)
    table = {label: sum_table(cells, rows[0]['profiles']) for label, cells in row_groups(rows).items()}
    matches = Counter()
    for row in rows:
        assert row['names'] == names
        expected = {name.split(':')[0]: value for name, value in row['profiles'].items()}
        course = row['class by round']
        assert len(course) == row['R*'] and all(len(c) == len(names) for c in course)
        for before, after in zip(course, course[1:]):
            assert len(set(zip(before, after))) == len(set(after))
        labels = course[-1]
        assert len(set(labels)) == row['classes']
        assert row['pairs'] == choose2(len(labels))
        assert row['pairs told apart'] == row['pairs'] - sum(choose2(c) for c in Counter(labels).values())
        for label, group in groups.items():
            assert tally(group, labels) == expected[label], (key(row['spec']), label)
            matches[label] += 1
    counts = [(row, next(c for k, c in row['profiles'].items() if k.startswith('counts 1:'))) for row in rows]
    fits = [(row, c) for row, c in counts if not c['of those told apart']]
    assert all(len(raw[key(row['spec'])][None][0]) >= row['R*'] for row in rows)
    output = {'completed': len(rows), 'unfinished': [{'study': key(r['spec']), 'return code': r['returncode']}
                                                     for r in failed],
              'common rounds': dict(Counter(r['R*'] for r in rows)),
              'bare starts independently recorded through the common round': len(rows),
              'distinct forms': len(groups['reach all']), 'study groups': table,
              'static profiles rebuilt and compared in this many studies': matches,
              'registered profile': {'distinct values per study: min and max':
                                        [min(c['values'] for _, c in counts), max(c['values'] for _, c in counts)],
                                     'deciding studies': len(fits),
                                     'all unordered pairs across deciding studies': sum(row['pairs'] for row, _ in fits),
                                     'pairs sharing in deciding studies': sum(c['pairs sharing it'] for _, c in fits),
                                     'deciding studies with no opportunity': sum(c['pairs sharing it'] == 0 for _, c in fits)}}
    if family == 'every_seed':
        output['registered profile']['deciding settings'] = [
            {'study': key(row['spec']), 'classes': row['classes'], **c} for row, c in fits]
        old = {Seed.from_knots(s).signature() for k in ('mixed', 'chains', 'second') for s in all_seeds['second'][k]}
        new = candidate_forms() - old
        assert {s.signature() for s in seeds} == old | new
        fresh = {Seed.from_knots(s).signature() for s in all_seeds['second']['fresh']}
        assert len(fresh) == 60 and fresh <= new
        output['roster'] = {'pre-freeze distinct forms': len(old), 'newly listed forms': len(new),
                            'earlier held-out forms included': len(fresh),
                            'knot counts': dict(Counter(len(s.loose) for s in seeds)),
                            'farthest knot by holder steps': dict(Counter(max(s.steps()) for s in seeds)),
                            'all-step profiles': len(groups['layers all']),
                            'full distinct forms': len(groups['reach all']),
                            'far knots without a loose distinction': sum(l == 0 and d >= 3 for s in seeds
                                                                        for l, d in zip(s.loose, s.steps()))}
        unplaced = pairs_within(groups['knots'])
        unplaced_stats = pair_timing(rows, unplaced, names, detailed=False)
        unplaced_stats['pairs with the same counts at every step'] = sum(
            seeds[i].by_steps() == seeds[j].by_steps() for i, j in unplaced)
        unplaced_stats['pairs with a different partner arrangement after forgetting every loose count'] = sum(
            seeds[i].signature(ignore_loose_after=-1) != seeds[j].signature(ignore_loose_after=-1) for i, j in unplaced)
        output['pairs without steps'] = unplaced_stats
        for depth in (2, 3):
            p = pairs_within(groups[f'reach {depth}'])
            stats = pair_timing(rows, p, names, detailed=False)
            same_beyond = [(i, j) for i, j in p if seeds[i].signature(ignore_loose_after=depth)
                           == seeds[j].signature(ignore_loose_after=depth)]
            different_beyond = [pair for pair in p if pair not in same_beyond]
            stats['differ only in loose counts farther out'] = len(same_beyond)
            stats['differ also in full partner arrangement or length'] = [(names[i], names[j]) for i, j in different_beyond]
            by_length = {same: [(i, j) for i, j in p if (len(seeds[i].loose) == len(seeds[j].loose)) == same]
                         for same in (True, False)}
            stats['same length'] = pair_timing(rows, by_length[True], names, detailed=False)
            stats['different lengths'] = pair_timing(rows, by_length[False], names, detailed=False)
            output[f'pairs agreeing to {depth} steps'] = stats
    if family != 'swap_family':
        output['registered run records at this study horizon'] = check_registered_overlap(rows, seeds, raw, family)
        if family == 'registered_family':
            forms = [None, *(s.signature() for s in seeds)]
            for row in rows:
                source = raw[key(row['spec'])]
                assert row['R*'] == min(9, *(len(source[form][0]) for form in forms))
            output['common rounds reconstructed from the bare start and all 60 second seeds'] = len(rows)
        if full:
            output['comparison with printed table'] = compare_printed(LATER / f'tables_{family}.txt', table)
    else:
        assert len(seeds) == len(groups['reach all']) == 54
        assert len(groups['layers all']) == 27 and all(len(g) == 2 for g in groups['layers all'])
        for i, j in pairs_within(groups['layers all']):
            a, b = seeds[i], seeds[j]
            assert a.held == b.held == 2 and a.loose[1:4] == b.loose[1:4]
            assert (a.loose[0], a.loose[-1]) == (b.loose[-1], b.loose[0])
        output['pairs swapping the two ends'] = pair_timing(rows, pairs_within(groups['layers all']), names)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--studies-per-family', type=int, help='Prefix used for timing at the same configuration')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    all_seeds = json.loads((REGISTERED / 'seeds.json').read_text())
    inputs = {}
    for family in FAMILIES:
        rows = list(islice(records(LATER / f'{family}.jsonl.gz'), args.studies_per_family))
        specs = [key(r['spec']) for r in rows]
        assert len(set(specs)) == len(specs)
        if args.studies_per_family is None:
            grid = product(('FLOOR1', 'CAP-3', 'ORD'), ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'),
                           ('none', 'MET-SOLE'), 'KLMNO' if family == 'registered_family' else 'ABCDEFGHIJKLMNO')
            assert set(specs) == set(grid)
        inputs[family] = ([r for r in rows if 'profiles' in r], [r for r in rows if 'profiles' not in r])
    accepted = {key(r['spec']) for f in FAMILIES for r in inputs[f][0]}
    raw = raw_registered(accepted, all_seeds)
    result = {family: audit_family(family, *inputs[family], all_seeds, raw, args.studies_per_family is None)
              for family in FAMILIES}
    result['matched original and expanded studies'] = compare_same_first_seeds(
        inputs['every_seed'][0], inputs['registered_family'][0], raw)
    result['how to read the counts'] = [
        'Every completed row contributes; the three unfinished rows supply settings only.',
        'Static profiles are rebuilt from second seeds and counted against the round partitions. All sixteen profiles are also aggregated from the archived study tallies.',
        'The registered run records contain the birth signatures and counts of second-only births. These give a separate check of the registered profile at each reported common round.',
        'An opportunity to test a profile means an unordered pair sharing it. A pair recurring under different laws or first seeds contributes once in each study.'
    ]
    content = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(content)
    else:
        for family in FAMILIES:
            counts = result[family]
            print(family, counts['completed'], counts['registered profile'])


if __name__ == '__main__':
    main()
