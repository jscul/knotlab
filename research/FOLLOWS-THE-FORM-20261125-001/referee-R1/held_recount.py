"""Recount FF 5–7, FF 9 and FF 11 from the individual held-out run records."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = 'FOLLOWS-THE-FORM-20261125-001A'
RUNS = ROOT / 'artifacts' / TICKET / (TICKET + '-E001_place_fixed_form_changed')
SEEDS = ROOT / 'research' / TICKET / 'seeds.json'
TAKING = ('none', 'sole')
RATIONS = ('FLOOR1', 'CAP-3', 'ORD')
TREATMENTS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
AFTER_FIRST_ROUND = (
    'pairs', 'told apart at R*', 'first told apart in round 2 or later',
    'of those, the wider record of round 1 the same',
    'in round 3 or later with the wider records the same through round 2',
)


def round_records(raw, fields):
    records = []
    for births in raw:
        assert all(len(birth) == fields + 1 and birth[-1] > 0 for birth in births)
        counts = {tuple(birth[:-1]): birth[-1] for birth in births}
        assert len(counts) == len(births)
        records.append(tuple(sorted(counts.items())))
    return tuple(records)


@dataclass(frozen=True)
class Run:
    own: tuple
    wider: tuple
    second_only: tuple
    stop: str | None
    knots: int

    @classmethod
    def from_row(cls, row):
        own = round_records(row['make'], 5)
        wider = round_records(row['wider'], 6)
        second_only = tuple(row['sec_only'])
        assert len(own) == len(wider) == len(second_only) == row['rounds_read']
        for round_index, (own_births, wider_births) in enumerate(zip(own, wider)):
            assert dict(own_births) == {birth[:5]: count for birth, count in wider_births if birth[5]}
            own_count = sum(count for _, count in own_births)
            wider_count = sum(count for _, count in wider_births)
            assert own_count == row['n_own'][round_index]
            assert wider_count == row['n_of_first'][round_index]
            assert wider_count - own_count == row['n_both'][round_index]
        return cls(own, wider, second_only, row['stop'], row['knots'])


def read_runs(runset, family, knot_law, forms, smoke):
    linked = runset != 'R2u'
    studies = defaultdict(dict)
    shards = range(1 if smoke else 8)
    for index in shards:
        with gzip.open(RUNS / f'runs_{runset}_{index}of8.jsonl.gz', 'rt') as stream:
            for line in stream:
                row = json.loads(line)
                assert (row['runset'], row['family'], row['knot_law'], row['linked']) == (
                    runset, family, knot_law, linked)
                study = (row['first'], row['take'], row['ration'], row['treatment'])
                name = row['second']
                assert name not in studies[study]
                studies[study][name] = Run.from_row(row)
    if not smoke:
        assert set(studies) == set(product('KLMNO', TAKING, RATIONS, TREATMENTS))
        for study, runs in studies.items():
            assert set(runs) == {*forms, None}, study
    return studies


def seed_holdings(seed):
    knots = [set(knot) for knot in seed['knots']]
    holders = Counter(distinction for knot in knots for distinction in knot)
    loose = [sum(holders[d] == 1 for d in knot) for knot in knots]
    partners = [{j for j, other in enumerate(knots) if j != i and knot & other}
                for i, knot in enumerate(knots)]
    return knots, loose, partners


def held_knot(seed):
    knots, loose, partners = seed_holdings(seed)
    at = seed['at']
    return len(knots[at]) + 1, loose[at], len(partners[at])


def chain_counts(seed):
    knots, loose, partners = seed_holdings(seed)
    assert sum(map(len, partners)) == 2 * (len(knots) - 1)
    read = [seed['at']]
    while remaining := partners[read[-1]] - set(read):
        next_knot, = remaining
        read.append(next_knot)
    assert len(read) == len(knots)
    counts = tuple(loose[i] for i in read)
    assert set(counts) <= {2, 3}
    return counts


def chain_pairs(forms):
    counts = {name: chain_counts(seed) for name, seed in forms.items()}
    assert len(set(counts.values())) == 62
    for a, b in combinations(counts, 2):
        shorter, longer = sorted((counts[a], counts[b]), key=len)
        n = len(shorter)
        if len(longer) == n:
            changed = [i for i, (x, y) in enumerate(zip(shorter, longer)) if x != y]
            if len(changed) == 1:
                yield (a, b), f'depth {changed[0]}'
        elif len(longer) == n + 1 and longer[:n] == shorter:
            yield (a, b), f'{n} against {n + 1} knots'


def seed_class(knots, held):
    by_distinction = defaultdict(set)
    for knot_index, knot in enumerate(knots):
        for distinction in knot:
            by_distinction[distinction].add(knot_index)
    other_knots = (i for i in range(len(knots)) if i != held)
    representations = []
    for order in permutations(other_knots):
        ranks = {i: rank for rank, i in enumerate((held, *order))}
        renamed = (tuple(sorted(ranks[i] for i in holders)) for holders in by_distinction.values())
        representations.append(tuple(sorted(renamed)))
    return min(representations)


def seed_candidates(n, partners, held_knots):
    for loose, held in product(product(range(4), repeat=n), held_knots):
        knots = [[] for _ in range(n)]
        for distinction, (a, b) in enumerate(partners):
            knots[a].append(distinction)
            knots[b].append(distinction)
        next_distinction = len(partners)
        for knot, count in zip(knots, loose):
            knot.extend(range(next_distinction, next_distinction + count))
            next_distinction += count
        if all(len(knot) + (i == held) >= 3 for i, knot in enumerate(knots)):
            yield seed_class(knots, held)


def seed_check(seeds):
    second = {family: [seed_class(s['knots'], s['at']) for s in forms] for family, forms in seeds['second'].items()}
    seen_second = set(second['mixed'] + second['second'] + second['chains'])
    first = {name: seed_class(s['knots'], s['site']) for name, s in seeds['first'].items()}
    seen_first = {first[name] for name in 'ABCDEFGHIJ'}
    fresh_first = {first[name] for name in 'KLMNO'}

    # Reconstruct the candidate order. Chains, then three-partner seeds, then rings. Within each kind,
    # order by the number of knots, loose counts and held-knot index, and keep the first representative.
    pool = []
    for n in range(1, 5):
        pool.extend(seed_candidates(n, [(i, i + 1) for i in range(n - 1)], range(n)))
    pool.extend(seed_candidates(4, [(0, i) for i in range(1, 4)], (0, 1)))
    for n in (3, 4):
        pool.extend(seed_candidates(n, [(i, (i + 1) % n) for i in range(n)], (0,)))
    pool = list(dict.fromkeys(seed for seed in pool if seed not in seen_second))
    indices = sorted(Random(seeds['seed of the sample']).sample(range(len(pool)), 60))
    return {
        'candidate classes': len(pool),
        'distinct second seeds by family': {name: len(set(forms)) for name, forms in second.items()},
        'fresh second classes also seen': len(set(second['fresh']) & seen_second),
        'distinct fresh and seen first classes': [len(fresh_first), len(seen_first)],
        'fresh first classes also seen': len(fresh_first & seen_first),
        'seeded draw agrees in listed order': [pool[i] for i in indices] == second['fresh'],
    }


def fate(run, horizon):
    if horizon < 4:
        return 'not read'
    x, y, z = (sum(count for _, count in births) for births in run.own[horizon - 3:horizon])
    if x == y == z == 0:
        return ('ends, taken up' if any(run.wider[horizon - 3:horizon]) else 'ends, no births')
    if x == y == z:
        return 'steady'
    if x < y < z:
        return 'grows'
    if x > y > z:
        return 'shrinks'
    return 'other'


def partition(observations):
    groups = defaultdict(list)
    for name, observed in observations.items():
        groups[observed].append(name)
    return set(frozenset(names) for names in groups.values())


def first_difference(a, b):
    return next((i for i, (left, right) in enumerate(zip(a, b), 1) if left != right), None)


def count_profiles(profiles, classes):
    counts = Counter({
        'profile values': len(set(profiles.values())),
        'same profile': 0,
        'same profile and different classes': 0,
        'different profiles and same class': 0,
    })
    for a, b in combinations(profiles, 2):
        if profiles[a] == profiles[b]:
            counts['same profile'] += 1
            counts['same profile and different classes'] += classes[a] != classes[b]
        elif classes[a] == classes[b]:
            counts['different profiles and same class'] += 1
    return dict(counts)


def pair_counts(forms, horizon, latest):
    counts = Counter(dict.fromkeys((
        *AFTER_FIRST_ROUND,
        'read through round 2 and the wider record of round 1 the same',
        'read through round 3 and the wider records through round 2 the same',
        'first told apart after R*',
    ), 0))
    first_told = Counter()
    for a, b in combinations(forms.values(), 2):
        counts['pairs'] += 1
        shared = min(len(a.own), len(b.own))
        earliest = first_difference(a.own, b.own)
        first_told[str(earliest) if earliest is not None else
                   'never' if shared == latest else 'not read further'] += 1
        matched_one = shared >= 2 and a.wider[:1] == b.wider[:1]
        matched_two = shared >= 3 and a.wider[:2] == b.wider[:2]
        counts['read through round 2 and the wider record of round 1 the same'] += matched_one
        counts['read through round 3 and the wider records through round 2 the same'] += matched_two
        if earliest is not None:
            counts['told apart at R*'] += earliest <= horizon
            counts['first told apart after R*'] += earliest > horizon
            counts['first told apart in round 2 or later'] += earliest >= 2
            counts['of those, the wider record of round 1 the same'] += earliest >= 2 and matched_one
            counts['in round 3 or later with the wider records the same through round 2'] += (
                earliest >= 3 and matched_two)
    return dict(counts), dict(first_told)


def read_study(study, runs, held_knots):
    horizon = min(len(run.own) for run in runs.values())
    latest = max(len(run.own) for run in runs.values())
    bare = runs[None]
    forms = {name: run for name, run in runs.items() if name is not None}
    classes = {name: run.own[:horizon] for name, run in forms.items()}
    wider_classes = {run.wider[:horizon] for run in forms.values()}
    pairs, first_told = pair_counts(forms, horizon, latest)
    held = {name: held_knots[name] for name in forms}
    second_only = {name: run.second_only[:horizon] for name, run in forms.items()}
    fates = Counter(fate(run, horizon) for run in forms.values())
    fates_for_prediction = {'ends' if value.startswith('ends') else value for value in fates}
    return {
        'study': list(study),
        'R*': horizon,
        'L': latest,
        'forms': len(forms),
        'classes': len(partition(classes)),
        'wider classes': len(wider_classes),
        'forms in the bare class': sum(c == bare.own[:horizon] for c in classes.values()),
        'forms failing the bare comparison through their common rounds': sum(
            first_difference(run.own, bare.own) is not None for run in forms.values()),
        'forms with fewer rounds read than the bare start': sum(
            len(run.own) < len(bare.own) for run in forms.values()),
        'forms with more rounds read than the bare start': sum(
            len(run.own) > len(bare.own) for run in forms.values()),
        'stops for forms with fewer rounds than the bare start': dict(Counter(
            run.stop or 'round cap' for run in forms.values() if len(run.own) < len(bare.own))),
        'fates': dict(fates),
        'fates for PN5': sorted(fates_for_prediction & {'ends', 'steady', 'grows'}),
        'pairs': pairs,
        'first told apart': first_told,
        'profiles': {
            'the held knot': count_profiles(held, classes),
            "the second seed's births by round": count_profiles(second_only, classes),
            'both': count_profiles({name: (held[name], second_only[name]) for name in forms}, classes),
        },
    }


def sum_counts(rows):
    combined = Counter()
    for row in rows:
        combined.update(row)
    return dict(combined)


def row_totals(studies):
    grouped = defaultdict(list)
    for study in studies:
        _, take, _, treatment = study['study']
        grouped[f'{take}, {treatment}'].append(study)
    return {row: {
        'first told apart': sum_counts(s['first told apart'] for s in group),
        'pairs': sum_counts(s['pairs'] for s in group),
        'fates': sum_counts(s['fates'] for s in group),
        'R*': dict(Counter(str(s['R*']) for s in group)),
    } for row, group in grouped.items()}


def profile_totals(studies):
    totals = {}
    for profile in studies[0]['profiles']:
        totals[profile] = {}
        for agrees in (False, True):
            selected = [study for study in studies if
                        (study['profiles'][profile]['same profile and different classes'] == 0) == agrees]
            counts = [study['profiles'][profile] for study in selected]
            totals[profile]['function' if agrees else 'not a function'] = {
                'studies': len(selected),
                'pair denominator': sum(s['pairs']['pairs'] for s in selected),
                'same profile': sum(c['same profile'] for c in counts),
                'same profile and different classes': sum(c['same profile and different classes'] for c in counts),
                'different profiles and same class': sum(c['different profiles and same class'] for c in counts),
                'studies with no pair sharing the profile': sum(c['same profile'] == 0 for c in counts),
                'profile values range': ([min(c['profile values'] for c in counts),
                                          max(c['profile values'] for c in counts)] if counts else None),
            }
    return totals


def tallied_tables(family, studies, rows, profiles):
    own_counts = Counter(str(s['classes']) for s in studies)
    wider_counts = Counter(str(s['wider classes']) for s in studies)
    wider_against = Counter('more' if s['wider classes'] > s['classes'] else
                            'less' if s['wider classes'] < s['classes'] else 'equal' for s in studies)
    return {
        f'first told apart, {family}': {row: data['first told apart'] for row, data in rows.items()},
        'after the first round': {family: {row: {name: data['pairs'][name] for name in AFTER_FIRST_ROUND}
                                          for row, data in rows.items()}},
        'fates on the window': {family: {row: data['fates'] for row, data in rows.items()}},
        'the count profile (studies in which the class is a function of it)': {family: {
            **{name: data['function']['studies'] for name, data in profiles.items()}, 'studies': len(studies)}},
        'R*': {family: {row: data['R*'] for row, data in rows.items()}},
        'wider record against own descent (studies)': {family: dict(wider_against)},
        'classes among the forms (studies by number)': {family: dict(own_counts)},
        'classes by the wider record (studies by number)': {family: dict(wider_counts)},
        'bare start a class of its own (studies)': {family: [
            sum(s['forms in the bare class'] == 0 for s in studies), len(studies)]},
        "every form in the bare start's class (studies)": {family: [
            sum(s['forms in the bare class'] == s['forms'] for s in studies), len(studies)]},
    }


def differences(a, b, path=()):
    if isinstance(a, dict) and isinstance(b, dict):
        return [d for key in sorted(a.keys() | b.keys()) for d in differences(a.get(key), b.get(key), (*path, key))]
    return [[list(path), a, b]] if a != b else []


def runset_summary(runset, family, studies, forms, raw_studies):
    rows = row_totals(studies)
    profiles = profile_totals(studies)
    tables = tallied_tables(family, studies, rows, profiles)
    published = json.loads((RUNS / f'tables_{runset}.json').read_text())
    depth = None
    if runset == 'R3':
        depth = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for (a, b), bin_name in chain_pairs(forms):
            for study in studies:
                key = tuple(study['study'])
                by_name = raw_studies[key]
                same = by_name[a].own[:study['R*']] == by_name[b].own[:study['R*']]
                cell = depth[', '.join(key[1:])][bin_name]
                cell[0] += not same
                cell[1] += 1
        tables['depth, chains, first seeds K to O together (told apart / pairs)'] = depth
    return {
        'runs': sum(s['forms'] + 1 for s in studies),
        'studies': len(studies),
        'classes among the forms (studies by number)': dict(Counter(s['classes'] for s in studies)),
        'pair rows': rows,
        'profiles': profiles,
        'forms failing the bare comparison through their common rounds': sum(
            s['forms failing the bare comparison through their common rounds'] for s in studies),
        'forms with fewer rounds read than the bare start': sum(
            s['forms with fewer rounds read than the bare start'] for s in studies),
        'forms with more rounds read than the bare start': sum(
            s['forms with more rounds read than the bare start'] for s in studies),
        'stops for forms with fewer rounds than the bare start': sum_counts(
            s['stops for forms with fewer rounds than the bare start'] for s in studies),
        'studies with a fate read': sum(s['R*'] >= 4 for s in studies),
        'published table differences': differences(tables, published),
        'depth': depth,
        'study counts': studies,
    }


def prediction_summary(output):
    held, unlinked, chains, parity = (output[label] for label in ('R2', 'R2u', 'R3', 'R4'))
    predictions = {}
    predictions['CU'] = sum(s['forms in the bare class'] == s['forms'] for s in unlinked['study counts'])
    predictions['S1'] = sum(s['forms in the bare class'] == 0 for s in held['study counts'])
    predictions['S2'] = sum(s['classes'] >= 2 for s in held['study counts'])
    predictions['S3'] = {name: data['1 against 2 knots'] for name, data in chains['depth'].items()}
    predictions['PN2'] = sum(s['classes'] >= 3 for s in held['study counts'])
    predictions['PN3'] = {name: data['pairs']['of those, the wider record of round 1 the same']
                          for name, data in held['pair rows'].items() if not name.endswith('WAIT')}
    predictions['PN4'] = {name: [data['pairs']['told apart at R*'], data['pairs']['pairs']]
                          for name, data in held['pair rows'].items()}
    predictions['PN5'] = sum(len(s['fates for PN5']) >= 2 for s in held['study counts'])
    predictions['PN6'] = sum(s['classes'] >= 3 for s in parity['study counts'])
    predictions['PN7'] = {profile: held['profiles'][profile]['not a function']['studies']
                          for profile in ('the held knot', 'both')}
    ceilings = {'depth 2': Fraction(1, 10), 'depth 3': Fraction(1, 10), 'depth 4': Fraction(1, 10),
                '3 against 4 knots': Fraction(3, 10), '4 against 5 knots': Fraction(15, 100)}
    pd1 = {'above the ceiling': [], 'at the ceiling': []}
    for law, cells in chains['depth'].items():
        if not law.startswith('none, '):
            continue
        for name, ceiling in ceilings.items():
            apart, pairs = cells[name]
            share = Fraction(apart, pairs)
            if share >= ceiling:
                relation = 'at the ceiling' if share == ceiling else 'above the ceiling'
                pd1[relation].append([law, name, [apart, pairs]])
    predictions['PD1'] = pd1
    predictions['PD2'] = {law: data['4 against 5 knots'] for law, data in chains['depth'].items()
                          if law.startswith('sole, ORD, ') or law == 'sole, CAP-3, CANCEL-WAIT'}
    return predictions


def both_starts_at_one_horizon(linked, unlinked):
    counts = Counter()
    for key, linked_runs in linked.items():
        unlinked_runs = unlinked[key]
        linked_horizon = min(len(run.own) for run in linked_runs.values())
        unlinked_horizon = min(len(run.own) for run in unlinked_runs.values())
        both_horizon = min(linked_horizon, unlinked_horizon)
        counts['common study horizon shorter than the linked horizon'] += both_horizon < linked_horizon
        for name, runs in [('linked', linked_runs), ('unlinked', unlinked_runs)]:
            observations = [run.own[:both_horizon] for form, run in runs.items() if form is not None]
            counts[f'{name} studies with at least two classes'] += len(set(observations)) >= 2
            counts[f'{name} studies with at least three classes'] += len(set(observations)) >= 3
            counts[f'{name} pairs told apart'] += sum(a != b for a, b in combinations(observations, 2))
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', help='time one shard and one partial study')
    args = parser.parse_args()
    seeds = json.loads(SEEDS.read_text())
    result = {'seed counts and split': seed_check(seeds)}
    linked = {}
    for runset, family, knot_law in [('R2', 'fresh', 'nae'), ('R2u', 'fresh', 'nae'),
                                    ('R3', 'chains', 'nae'), ('R4', 'fresh', 'parity')]:
        forms = {s['name']: s for s in seeds['second'][family]}
        held_knots = {name: held_knot(seed) for name, seed in forms.items()}
        studies = read_runs(runset, family, knot_law, forms, args.smoke)
        if args.smoke:
            first_study = next(iter(studies))
            print(runset, sum(map(len, studies.values())),
                  read_study(first_study, studies[first_study], held_knots)['pairs']['pairs'])
            continue
        if runset == 'R2':
            linked = studies
        if runset == 'R2u':
            result['bare runs with equal full records across R2 and R2u'] = sum(
                linked[key][None] == study[None] for key, study in studies.items())
            result['linked and unlinked at one common study horizon'] = both_starts_at_one_horizon(linked, studies)
        if runset == 'R4':
            different_runs = 0
            different_partitions = 0
            for key, parity in studies.items():
                nae = linked[key]
                different_runs += sum(parity[name] != nae[name] for name in parity)
                r_parity = min(len(x.own) for x in parity.values())
                r_nae = min(len(x.own) for x in nae.values())
                different_partitions += partition({name: run.own[:r_parity] for name, run in parity.items()}) != (
                    partition({name: run.own[:r_nae] for name, run in nae.items()}))
            result['knot law comparison'] = {'different run records': different_runs,
                                             'different own-descent study partitions': different_partitions}
        by_study = [read_study(key, study, held_knots) for key, study in sorted(studies.items())]
        result[runset] = runset_summary(runset, family, by_study, forms, studies)
    if not args.smoke:
        result['prediction counts'] = prediction_summary(result)
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
