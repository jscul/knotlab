"""Replay cheapest growth from the archived starts and check both readings.

Join selection follows Lemma R in REDUCE-BLOCKS and fresh counts follow the
two implication tests in NAE-GROWTH. The archive supplies the start and the
comparison record. No study implementation is imported. The optional longer
replay overrides the knot cap for a sensitivity check on shortened records.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
import gzip
from itertools import chain, combinations, permutations
import json
from pathlib import Path
from random import Random
import resource
from time import perf_counter


STUDY = Path(__file__).resolve().parents[1]
LAWS = ('nae', 'parity')
ROUND_LIMIT = 24
KNOT_CAP = 30_000
SEED = 901127


@dataclass
class Replay:
    rows: list
    end: str
    knots: int
    M: int
    live_neighbour_max: int
    first_fresh_max: int
    all_live_joins: list
    all_loose_births: list
    name_checks: dict


def incidence(stars):
    """Return who meets each starting knot, and each knot's loose count."""
    holders = defaultdict(set)
    for name, distinctions in enumerate(stars):
        if len(distinctions) < 3 or len(distinctions) != len(set(distinctions)):
            raise ValueError(f'invalid knot holdings: {distinctions}')
        for distinction in distinctions:
            holders[distinction].add(name)

    witnesses = [set() for _ in stars]
    loose = [0] * len(stars)
    for names in holders.values():
        if len(names) == 1:
            (name,) = names
            loose[name] += 1
        elif len(names) == 2:
            first, second = names
            witnesses[first].add(second)
            witnesses[second].add(first)
        else:
            raise ValueError(f'distinction held by more than two knots: {names}')

    reached = {0}
    remaining = [0]
    while remaining:
        new = witnesses[remaining.pop()] - reached
        reached.update(new)
        remaining.extend(new)
    if len(reached) != len(stars):
        raise ValueError('the implication shortcut requires a connected start')
    return witnesses, loose


def maximal_pairwise_groups(partners):
    """Enumerate maximal sets whose pairs all have a witness (Bron–Kerbosch)."""
    def visit(group, candidates, excluded):
        if not candidates:
            if not excluded:
                yield group
            return
        pivot = max(chain(candidates, excluded), key=lambda name: len(candidates & partners[name]))
        for name in candidates - partners[pivot]:
            others = partners[name]
            yield from visit(group + (name,), candidates & others, excluded & others)
            candidates.remove(name)
            excluded.add(name)

    yield from visit((), set(partners), set())


def joins(witnesses):
    """Every uncovered pair and every maximal group with no common witness."""
    rosters = defaultdict(list)
    for name, its_witnesses in enumerate(witnesses):
        for witness in its_witnesses:
            rosters[witness].append(name)
    partners = defaultdict(set)
    for roster in rosters.values():
        for first, second in combinations(roster, 2):
            partners[first].add(second)
            partners[second].add(first)

    groups = []
    for group in maximal_pairwise_groups(partners):
        # If a maximal group has a common witness, every subset does too.
        if len(group) >= 3 and not set.intersection(*(set(witnesses[name]) for name in group)):
            groups.append(tuple(sorted(group)))

    covered = {pair for group in groups for pair in combinations(group, 2)}
    groups.extend(
        (first, second)
        for first, others in partners.items()
        for second in others
        if first < second and (first, second) not in covered
    )
    return sorted(groups)


def direct_start_joins(witnesses):
    """Check the join definition by listing every subset of six start names."""
    live = [name for name, preceding in enumerate(witnesses) if preceding]
    pairs = [pair for pair in combinations(live, 2) if witnesses[pair[0]] & witnesses[pair[1]]]
    pair_set = set(pairs)
    valid = []
    for size in range(3, len(live) + 1):
        for names in combinations(live, size):
            if all(pair in pair_set for pair in combinations(names, 2)):
                if not set.intersection(*(witnesses[name] for name in names)):
                    valid.append(frozenset(names))
    maximal = [group for group in valid if not any(group < other for other in valid)]
    return sorted([tuple(sorted(group)) for group in maximal]
                  + [pair for pair in pairs if not any(set(pair) <= group for group in maximal)])


def demands(groups, count):
    result = [0] * count
    for group in groups:
        for name in group:
            result[name] += 1
    return result


def birth_plan(groups, loose):
    spent = demands(groups, len(loose))
    if any(demand > budget for demand, budget in zip(spent, loose, strict=True)):
        return None
    parents = list(groups)
    for name, (budget, demand) in enumerate(zip(loose, spent, strict=True)):
        parents.extend([(name,)] * (budget - demand))
    return parents


def first_plan_key(stars):
    """Canonical named first-round plan with the starting loose counts.

    A plan keeps one roster per birth occurrence, even when rosters coincide.
    Equal keys give a bijection of live starting knots and of the births with
    their parent names, and give equal first-round demand and fresh counts
    under one law. Later grouping reads those preceding parent rosters, so
    the bijection extends round by round. Across laws this also requires that
    the replay never takes all loose distinctions in one birth. The starting
    descriptions may differ and are read separately for round 1.
    """
    witnesses, loose = incidence(stars)
    live = [name for name, count in enumerate(loose) if count]
    living_witnesses = [ws if loose[name] else () for name, ws in enumerate(witnesses)]
    groups = joins(living_witnesses)
    parents = birth_plan(groups, loose)
    if not parents:
        raise ValueError('cannot extend a start with no births in round 1')
    relabellings = []
    for order in permutations(live):
        rename = {name: n for n, name in enumerate(order)}
        starting_counts = tuple(loose[name] for name in order)
        named_rosters = tuple(sorted(tuple(sorted(rename[parent] for parent in roster)) for roster in parents))
        relabellings.append((starting_counts, named_rosters))
    return len(stars), min(relabellings)


def reuse_after_first_round(source, stars, law):
    first = grow(stars, law, stop_at_round=1, knot_cap=None)
    # The first sig1 depends on start descriptions. Its sig0 is already
    # determined by the named plan and must match across this reuse.
    if dict(freeze(first.rows[0]['sig0'])) != dict(freeze(source.rows[0]['sig0'])):
        raise ValueError('first descriptions differ for identical first plans')
    return replace(source, rows=first.rows + source.rows[1:], M=first.M,
                   live_neighbour_max=first.live_neighbour_max, first_fresh_max=first.first_fresh_max,
                   name_checks={**source.name_checks, **first.name_checks})


def read_births(descriptions, parents, earlier_descriptions, check_names):
    """Count birth descriptions and the same descriptions with parent multisets."""
    with_parents = Counter()
    representative = {}
    name_witness = None
    equal_parent_descriptions = 0
    for name, (own, roster) in enumerate(zip(descriptions, parents, strict=True)):
        parent_descriptions = tuple(sorted(earlier_descriptions[parent] for parent in roster))
        reading = (own, parent_descriptions)
        with_parents[reading] += 1
        if check_names:
            if len(set(parent_descriptions)) < len(roster):
                equal_parent_descriptions += 1
            earlier_name, earlier_roster = representative.setdefault(reading, (name, roster))
            if name_witness is None and earlier_roster != roster:
                name_witness = {'reading': reading, 'birth names': [earlier_name, name],
                                'parent names': [earlier_roster, roster]}
    row = {'n': len(parents), 'sig0': sorted(Counter(descriptions).items()),
           'sig1': sorted(with_parents.items())}
    name_check = {'births with equally described distinct parents': equal_parent_descriptions,
                  'two different parent rosters with one reading': name_witness}
    return row, name_check


def grow(stars, law, *, stop_at_round=ROUND_LIMIT, knot_cap=KNOT_CAP, checkpoints=()):
    witnesses, loose = incidence(stars)
    initial_rosters = Counter(witness for name, its_witnesses in enumerate(witnesses)
                              if loose[name] for witness in its_witnesses)
    live_neighbour_max = max(initial_rosters.values(), default=0)
    eligible = [its_witnesses if loose[name] else () for name, its_witnesses in enumerate(witnesses)]
    current_joins = joins(eligible)
    descriptions = [('start', 0, 0, len(distinctions)) for distinctions in stars]
    knots = len(stars)
    rows = []
    first_fresh_max = 0
    all_live_joins = []
    all_loose_births = []
    name_checks = {}
    end = 'rounds'

    for round_number in range(1, stop_at_round + 1):
        parents = birth_plan(current_joins, loose)
        if parents is None:
            end = f'stalls at round {round_number}'
            break
        if not parents:
            end = f'closes at round {round_number}'
            break

        live = sum(budget > 0 for budget in loose)
        if any(len(roster) == live for roster in current_joins):
            all_live_joins.append(round_number)
        takes_all = len(parents) == 1 and len(parents[0]) == sum(loose)
        if takes_all:
            all_loose_births.append(round_number)

        # Every new knot is live except the implied sole parity birth. Its
        # next-round demand is already zero because there are no partners.
        next_joins = joins(parents)
        next_demand = demands(next_joins, len(parents))
        next_loose = [demand if law == 'parity' and takes_all else max(demand, 3 - len(roster), 1)
                      for roster, demand in zip(parents, next_demand, strict=True)]
        if round_number == 1:
            first_fresh_max = max(next_loose)
        next_descriptions = [('join' if len(roster) > 1 else 'offshoot', len(roster), fresh, len(roster) + fresh)
                             for roster, fresh in zip(parents, next_loose, strict=True)]
        knots += len(parents)
        crosses_cap = knot_cap is not None and knots > knot_cap
        check_names = round_number in checkpoints or crosses_cap or round_number == stop_at_round
        row, name_check = read_births(next_descriptions, parents, descriptions, check_names)
        rows.append(row)
        if check_names:
            name_checks[round_number] = name_check
        if crosses_cap:
            end = 'bound'
            break
        descriptions = next_descriptions
        loose = next_loose
        current_joins = next_joins

    return Replay(rows, end, knots, max(live_neighbour_max, first_fresh_max),
                  live_neighbour_max, first_fresh_max, all_live_joins, all_loose_births, name_checks)


def freeze(value):
    """Make a JSON reading hashable while preserving multiplicity and order."""
    if isinstance(value, (list, tuple)):
        return tuple(map(freeze, value))
    return value


def compare_rounds(actual, expected):
    """The order in which reading kinds were written is immaterial."""
    for n, (computed, archived) in enumerate(zip(actual, expected), 1):
        if computed['n'] != archived['n']:
            return {'round': n, 'counts': [computed['n'], archived['n']]}
        for key in ('sig0', 'sig1'):
            got = dict(freeze(computed[key]))
            want = dict(freeze(archived[key]))
            if len(got) != len(computed[key]) or len(want) != len(archived[key]):
                return {'round': n, 'reading': key, 'repeated description': True}
            if got != want:
                return {'round': n, 'reading': key, 'replayed only': sorted((Counter(got) - Counter(want)).items()),
                        'archived only': sorted((Counter(want) - Counter(got)).items())}
    if len(actual) != len(expected):
        return {'round lengths': [len(actual), len(expected)]}
    return None


def differences(counts, order):
    result = counts
    for _ in range(order):
        result = [after - before for before, after in zip(result, result[1:])]
    return result


def settling_cuts(row):
    """Locate the last nonzero Dth difference in either recorded reading."""
    kind = row['kind']
    if not kind.startswith('dim '):
        return {}
    dimension = int(kind.split()[-1])
    rounds = row['rows']
    cuts = {}
    for key in ('sig0', 'sig1'):
        series = defaultdict(lambda: [0] * len(rounds))
        for index, entry in enumerate(rounds):
            for description, count in entry[key]:
                series[freeze(description)][index] = count
        cut = max(3, dimension)
        for counts in series.values():
            values = differences(counts, dimension)
            last = next((end for end, value in enumerate(reversed(values)) if value), None)
            if last is not None:
                cut = max(cut, len(counts) - last)
        cuts[key] = cut
    return cuts


def classification(rows, end):
    if end.startswith('stalls'):
        return 'stalls'
    if end.startswith('closes'):
        return 'closes'
    counts = [row['n'] for row in rows]
    for dimension in range(1, 5):
        tail = differences(counts[-8:], dimension - 1)
        if len(counts) >= 8 and tail[0] > 0 and len(set(tail)) == 1:
            return f'dim {dimension}'
    return 'unread'


def short_bound(row):
    return row['end'] == 'bound' and len(row['rows']) < ROUND_LIMIT


def late_reading(row, cuts):
    if not cuts:
        return False
    dimension = int(row['kind'].split()[-1])
    return any(row['M'] + offset < cuts[key] <= ROUND_LIMIT - dimension
               for key, offset in (('sig0', 5), ('sig1', 7)))


def read_archives(laws):
    for law in laws:
        with gzip.open(STUDY / f'grown_fresh_{law}.jsonl.gz', 'rt') as stream:
            for line in stream:
                row = json.loads(line)
                if row['knot law'] != law:
                    raise ValueError((law, row['knot law']))
                yield row


def pilot_indices(records, extend):
    if extend:
        by_kind = defaultdict(list)
        for row in records:
            if short_bound(row):
                by_kind[row['kind']].append(row)
        return {max(rows, key=lambda r: r['rows'][-1]['n'])['index'] for rows in by_kind.values()}
    by_kind = defaultdict(list)
    for row in records:
        by_kind[(row['knot law'], row['kind'], short_bound(row))].append(row)
    chosen = set()
    rng = Random(SEED)
    for candidates in by_kind.values():
        chosen.add(rng.choice(candidates)['index'])
        chosen.add(max(candidates, key=lambda r: r['knots'])['index'])
    return chosen


def stratified_indices(records, cuts):
    by_kind = defaultdict(list)
    selected = set()
    for row in records:
        if late_reading(row, cuts[row['knot law'], row['index']]):
            selected.add(row['index'])
        by_kind[(row['knot law'], row['kind'], row['end'], len(row['rows']))].append(row['index'])
    rng = Random(SEED)
    for candidates in by_kind.values():
        selected.update(rng.sample(candidates, min(3, len(candidates))))
    return selected


def rename_start(stars):
    return [[1_000_007 - 3 * label for label in reversed(knot)] for knot in reversed(stars)]


def last_fall(rows):
    falls = [n for n in range(2, len(rows) + 1) if rows[n - 2]['n'] > rows[n - 1]['n']]
    return falls[-1] if falls else None


def extension_pilot_data(path, records, plan_keys):
    if path is None:
        return {}
    pilot = json.loads(path.read_text())
    if pilot['knot cap'] is not None or pilot['round limit'] != ROUND_LIMIT or pilot['differences']:
        raise ValueError(f'unmatched extension pilot: {path.name}')
    archive_by_name = {(r['index'], r['knot law']): r for r in records}
    donor_runs = {}
    for record in pilot['records checked']:
        name = record['index'], record['knot law']
        if name not in archive_by_name:
            continue
        archived = archive_by_name[name]
        if record['stars'] != archived['stars']:
            raise ValueError(f'unmatched pilot start: {name}')
        live_max, first_fresh = record['M from live neighbours and first fresh']
        computed = Replay(record['rows'], record['end'], record['knots'], record['M'], live_max, first_fresh,
                          record['all live parents named by one join'], record['all loose distinctions taken by one birth'],
                          {int(n): check for n, check in record['name checks'].items()})
        if compare_rounds(computed.rows[:len(archived['rows'])], archived['rows']) is not None:
            raise ValueError(f'unmatched pilot readings: {name}')
        donor_runs[name] = computed
        plan_keys[name] = first_plan_key(record['stars'])
    return donor_runs


def run(extend, selection, laws, reuse_extension_pilot):
    opened = perf_counter()
    records = list(read_archives(laws))
    if extend:
        records = sorted((r for r in records if short_bound(r)),
                         key=lambda r: (r['kind'] == 'unread', r['index'], r['knot law']))
    cuts = {(row['knot law'], row['index']): settling_cuts(row) for row in records}
    if selection == 'pilot':
        selected = pilot_indices(records, extend)
    elif selection == 'stratified':
        selected = stratified_indices(records, cuts)
    else:
        selected = {row['index'] for row in records}

    out = {'knot cap': None if extend else KNOT_CAP, 'round limit': ROUND_LIMIT, 'laws': laws,
           'selection': selection, 'seed for sampling and pilots': SEED,
           'available records': len(records), 'differences': [], 'omitted after round 1': 0,
           'records checked': [], 'identity controls': [], 'input load seconds': round(perf_counter() - opened, 3)}
    plan_keys = {}
    donor_runs = extension_pilot_data(reuse_extension_pilot, records, plan_keys)
    if reuse_extension_pilot is not None:
        out['pilot source'] = reuse_extension_pilot.name
    certify_matches = extend and selection == 'all'
    plan_donors = defaultdict(list)
    for name, key in plan_keys.items():
        plan_donors[key].append(name)
    totals = defaultdict(Counter)
    checkpoints = Counter()
    renamed_kinds = set()

    for row in records:
        began = perf_counter()
        law, index = row['knot law'], row['index']
        full = index in selected or not row['rows']
        stop = ROUND_LIMIT if full else 1
        report_cuts = cuts[law, index]
        name_rounds = set(report_cuts.values()) | {len(row['rows'])}
        source = None
        if certify_matches:
            name = index, law
            key = plan_keys.get(name)
            if key is None:
                key = first_plan_key(row['stars'])
            if name in donor_runs:
                source = name
            else:
                source = next((donor for donor in plan_donors[key]
                               if donor[1] == law or not donor_runs[donor].all_loose_births), None)
        if source is None:
            computed = grow(row['stars'], law, stop_at_round=stop,
                            knot_cap=None if extend else KNOT_CAP, checkpoints=name_rounds)
            if certify_matches:
                donor_runs[name] = computed
                plan_donors[key].append(name)
        else:
            computed = reuse_after_first_round(donor_runs[source], row['stars'], law)
        archived = row['rows']
        expected = archived if full else archived[:1]
        actual = computed.rows if not extend else computed.rows[:len(archived)]
        mismatches = compare_rounds(actual, expected)
        witnesses, computed_loose = incidence(row['stars'])
        if not extend:
            eligible = [ws if computed_loose[n] else set() for n, ws in enumerate(witnesses)]
            measured = joins(eligible)
            specified = direct_start_joins(eligible)
            if measured != specified:
                mismatches = {'first join groups': [measured, specified], 'readings': mismatches}
        if full and not extend:
            got = (computed.end, computed.knots, classification(computed.rows, computed.end))
            want = (row['end'], row['knots'], row['kind'])
            if got != want:
                mismatches = {'end, knots and growth kind': [got, want], 'readings': mismatches}
        if full and extend:
            prefix_total = len(row['stars']) + sum(item['n'] for item in actual)
            previous_total = prefix_total - actual[-1]['n']
            if not previous_total <= KNOT_CAP < prefix_total == row['knots']:
                mismatches = {'expected cap crossing absent': [previous_total, prefix_total], 'readings': mismatches}
        if computed.M != row['M'] or computed_loose != row['loose']:
            mismatches = {'computed and archived M': [computed.M, row['M']],
                          'computed and archived loose counts': [computed_loose, row['loose']],
                          'readings': mismatches}
        if mismatches:
            out['differences'].append({'index': index, 'stars': row['stars'], 'law': law, 'detail': mismatches})

        group = totals[law, row['kind'], row['end'], len(archived)]
        group['records'] += 1
        group['first round attempts'] += 1
        if not extend:
            group['first join plans checked by subsets'] += 1
        group['saved rounds checked'] += min(len(actual), len(expected))
        group['saved births checked'] += sum(saved['n'] for saved in expected)
        group['new rounds'] += max(0, len(computed.rows) - len(archived))
        group['new births'] += sum(r['n'] for r in computed.rows[len(archived):])

        if full:
            group['complete replays'] += 1
            if source is None:
                group['direct replays in this run'] += 1
            elif source == name:
                group['direct replays from pilot'] += 1
            else:
                group['replays by equal first plans'] += 1
            late = late_reading(row, report_cuts)
            if late:
                group['late replays'] += 1
            if late or short_bound(row) or selection == 'pilot':
                first, last = computed.live_neighbour_max, computed.first_fresh_max
                detail = {'index': index, 'stars': row['stars'], 'knot law': law, 'kind': row['kind'],
                          'M': computed.M, 'M from live neighbours and first fresh': [first, last],
                          'archived rounds': len(archived), 'archived knots': row['knots'], 'archived end': row['end'],
                          'archived settling cuts': report_cuts, 'archived last strict fall': last_fall(archived),
                          'late by at least one archived reading': late,
                          'last round with any join': max((n for n, signed in enumerate(computed.rows, 1)
                                                           if any(k[0] == 'join' for k, _ in signed['sig0'])),
                                                          default=None),
                          'all live parents named by one join': computed.all_live_joins,
                          'all loose distinctions taken by one birth': computed.all_loose_births,
                          'name checks': computed.name_checks}
                if extend:
                    detail.update({'n knots': len(row['stars']), 'rows': computed.rows,
                                   'knots': computed.knots, 'end': computed.end,
                                   'kind at extension': classification(computed.rows, computed.end)})
                    if source is not None:
                        detail.update({'same first plan and laws agree through replay': source,
                                       'first plan key': key})
                out['records checked'].append(detail)

            for tag, checkpoint in list(report_cuts.items()) + [('last saved round', len(archived))]:
                name_check = computed.name_checks.get(checkpoint)
                if name_check is not None:
                    checkpoints[tag, 'checked'] += 1
                    checkpoints[tag, 'same description for distinct parents'] += bool(
                        name_check['births with equally described distinct parents'])
                    checkpoints[tag, 'different parent rosters give same reading'] += bool(
                        name_check['two different parent rosters with one reading'])
        else:
            out['omitted after round 1'] += 1

        if not extend and full and row['kind'] != 'stalls' and (law, row['kind']) not in renamed_kinds:
            renamed_kinds.add((law, row['kind']))
            renamed = grow(rename_start(row['stars']), law)
            renamed_match = compare_rounds(renamed.rows, computed.rows) is None and (renamed.M, renamed.end) == (
                computed.M, computed.end)
            out['identity controls'].append({'index': index, 'stars': row['stars'], 'law': law,
                                             'kind': row['kind'], 'renamed readings match': renamed_match})
        group['seconds'] += perf_counter() - began

    out['by law, kind, ending, saved rounds'] = [
        {'law': law, 'kind': kind, 'end': end, 'archived rounds': length,
         **{key: round(value, 3) if key == 'seconds' else value for key, value in stats.items()}}
        for (law, kind, end, length), stats in sorted(totals.items())
    ]
    out['names at checkpoints'] = [
        {'checkpoint': name, 'measure': measure, 'records': count}
        for (name, measure), count in sorted(checkpoints.items())
    ]
    out['wall seconds'] = round(perf_counter() - opened, 3)
    out['peak resident KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extend', action='store_true', help='run just the shortened capped starts through round 24')
    parser.add_argument('--selection', choices=('pilot', 'stratified', 'all'), default='all')
    parser.add_argument('--law', choices=LAWS, help='limit the run to one law')
    parser.add_argument('--reuse-extension-pilot', type=Path, help='reuse direct replays at the extended horizon')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.reuse_extension_pilot and not (args.extend and args.selection == 'all'):
        parser.error('--reuse-extension-pilot requires --extend with --selection all')
    result = run(args.extend, args.selection, (args.law,) if args.law else LAWS, args.reuse_extension_pilot)
    with args.output.open('w') as stream:
        json.dump(result, stream, separators=(',', ':'))
        stream.write('\n')
    renaming_failure = any(not c['renamed readings match'] for c in result['identity controls'])
    if result['differences'] or renaming_failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
