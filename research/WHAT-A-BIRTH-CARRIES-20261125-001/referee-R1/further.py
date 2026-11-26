"""Recount the further-reaching probe from its stored records.

Use --limit for a prefix of each input. The default reads each stored row.
The first round is derived from the supplied starts and the group, owing,
shortness, and taking rules. No growth or analysis code is imported.
"""

import argparse
import ast
import gzip
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / 'checks' / 'reach_further'
RESEARCH = DATA.parents[2]
SCAN_FILES = ('rings', 'census_wide', 'census_near', 'census_five_m2many')
LINK_FILES = ('links_rings', 'links_census', 'links_five', 'links_ringk')
FURTHER_MOST = 'MET2-MANY'
RATION_CAP = 'CAP-3'
COURSE_NAMES = {
    (0, 0, 0, 0): 'no change',
    (0, 1, 1, 2): 'number barred',
    (0, 0, 0, 1): 'both barred only',
    (0, 1, 1, 0): 'exactly one barred',
    (0, 1, 0, 2): 'one alone matters, the other once it is gone',
    (0, 1, 1, 1): 'at least one barred',
    (0, 1, 0, 1): 'only one matters',
    (0, 1, 2, 3): 'four different courses',
}


def rows(name, limit):
    with gzip.open(DATA / f'{name}.jsonl.gz', 'rt') as source:
        yield from map(json.loads, itertools.islice(source, limit))


def configuration(spec):
    return tuple(spec[key] for key in ('start', 'take', 'ration', 'treatment', 'knot_law'))


def stop_name(row):
    if 'error' in row:
        return f'error {row["returncode"]}'
    return row['stop'] or 'read to bound'


def canonical_classes(labels):
    names = {}
    return tuple(names.setdefault(label, len(names)) for label in labels)


def course_name(labels):
    base, first, second, both = labels
    forward = canonical_classes(labels)
    reverse = canonical_classes((base, second, first, both))
    key = max(forward, reverse)
    return COURSE_NAMES.get(key, ','.join(map(str, key)))


def record_test(tally, test):
    classes = test['classes']
    assert len(classes) == 4
    t1, t2 = test['meets']
    assert min(t1, t2) > test['s']
    tally['four-run tests'] += 1
    tally[f'course: {course_name(classes)}'] += 1
    tally[f'pair chosen: {test["why"]}'] += 1
    tally[f'first meeting delays: {sorted((t1 - test["s"], t2 - test["s"]))}'] += 1
    tally[f'part separation after round {test["s"]}'] += 1
    tally[f'first course differences: {test["first differs"]}'] += 1
    if classes[1] != classes[2]:
        tally['which one barred'] += 1
        tally['which one barred, same first-meeting round' if t1 == t2
              else 'which one barred, different first-meeting rounds'] += 1
    for idx, difference_round in enumerate(test['first differs'], 1):
        assert (difference_round is None) == (classes[idx] == classes[0])
    if 'last' in test:
        tally[f'common course read through round {test["last"]}'] += 1
        m_value = test.get('m', {}).get('m')
    else:
        m_value = test['m']
    tally[f'm: {m_value}'] += 1
    if m_value is None:
        assert len(set(classes)) == 1


def scan_recount(records):
    rules = defaultdict(Counter)
    candidate_settings = set()
    keyed = {}
    for row in records:
        setting = configuration(row['spec'])
        assert setting not in keyed
        keyed[setting] = row
        tally = rules[row['spec']['take']]
        tally['settings'] += 1
        tally[f'run stop: {stop_name(row)}'] += 1
        if 'error' in row:
            continue
        tally[f'unbarred run read through round {row["rounds_read"]}'] += 1
        tally['settings with a recorded take in rounds 2 onward'] += row['takes made'] > 0
        tally['takes recorded, rounds 2 onward'] += row['takes made']
        tally['settings with four-run tests'] += bool(row['tests'])
        if len(row['tests']) == 12:
            tally['settings reaching the twelve-test cap'] += 1
        if row['tests']:
            candidate_settings.add(setting)
        for split in row['by_s']:
            tally['first parts with at least two other parts met through made knots'] += split['X with two or more']
            tally['first parts meeting others in distinct rounds'] += split['X met in different rounds']
            pairs = dict(split['pairs'])
            alike = pairs.get('alike', 0)
            unlike = pairs.get('not alike', 0)
            different = pairs.get('first met in different rounds', 0)
            assert different <= unlike + alike
            tally['alike second pairs'] += alike
            tally['unlike second pairs as classified'] += unlike
            tally['undecided symmetry comparisons'] += pairs.get('undecided', 0)
            tally['second pairs with distinct first-meeting rounds'] += different
            tally['lower bound on unlike or distinct-round pairs'] += max(unlike, different)
            tally['upper bound on unlike or distinct-round pairs'] += min(alike + unlike, unlike + different)
            for key, count in split['first meetings (round, made only)']:
                meeting_round, made_only = ast.literal_eval(key)
                assert meeting_round > split['s'] and count % 2 == 0
                name = 'only made linking knots' if made_only else 'other or empty linking set'
                tally[f'first meetings: {name}'] += count // 2
                tally[f'first meetings: {name}, delay {meeting_round - split["s"]}'] += count // 2
        for test in row['tests']:
            record_test(tally, test)
    return rules, candidate_settings, keyed


def first_round_parents(knots, treatment, holders):
    """Enumerate the joins and offshoots directly on a small supplied start."""
    loose_counts = [sum(len(holders[d]) == 1 for d in places) for places in knots]
    met_sets = [{u for d in places for u in holders[d] if u != w} for w, places in enumerate(knots)]
    live = {u for u, n in enumerate(loose_counts) if n}
    met_pairs = {frozenset(pair) for members in met_sets
                 for pair in itertools.combinations(members & live, 2)}
    groups = []
    for size in range(len(live), 2, -1):
        for part in map(frozenset, itertools.combinations(sorted(live), size)):
            if any(part <= members for members in met_sets) or any(part <= group for group in groups):
                continue
            if all(frozenset(pair) in met_pairs for pair in itertools.combinations(part, 2)):
                groups.append(part)
    uncovered_pairs = [pair for pair in met_pairs if not any(pair <= group for group in groups)]
    groups.extend(uncovered_pairs)
    owe = Counter(u for group in groups for u in group)
    short = {u for u in live if owe[u] > loose_counts[u]}
    kept = [group for group in groups if group.isdisjoint(short)]
    kept_count = Counter(u for group in kept for u in group)
    offshoots = [(u,) for u in live - short for _ in range(loose_counts[u] - kept_count[u])]
    if treatment == 'CANCEL-OFFSHOOT':
        offshoots.extend((u,) for u in short for _ in range(loose_counts[u]))
    return kept + offshoots, met_sets


def first_round_takes(knots, take, treatment):
    holders = defaultdict(set)
    for u, places in enumerate(knots):
        for d in places:
            holders[d].add(u)
    births, met_sets = first_round_parents(knots, treatment, holders)
    reach, choice = take.split('-')
    if reach == 'MET2':
        met_sets = [(members | set.union(set(), *(met_sets[v] for v in members))) - {u}
                    for u, members in enumerate(met_sets)]
    taken = 0
    for parents in births:
        sources = set.intersection(*(met_sets[u] for u in parents)) - set(parents)
        held = {d for u in parents for d in knots[u]}
        offer = {d for u in sources for d in knots[u] if len(holders[d]) >= 2} - held
        counts = [len(holders[d]) for d in offer]
        if choice == 'ALL':
            taken += len(offer)
        elif choice == 'SOLE':
            taken += len(offer) == 1
        elif counts:
            best = max(counts) if choice == 'MANY' else min(counts)
            taken += counts.count(best) == 1
    return taken


def recount_first_round(scan, observed_controls):
    with (RESEARCH / 'KNOTS-WITHIN-REACH-20261125-001A' / 'census_starts.json').open() as source:
        census = {f'census:{i}': row['stars'] for i, row in enumerate(json.load(source))}
    with (RESEARCH / 'WHAT-A-BIRTH-CARRIES-20261125-001B' / 'starts.json').open() as source:
        rings = json.load(source)
    starts = {**census, **rings['stars'], rings['extra']['name']: rings['extra']['stars']}
    first = {}
    groups = defaultdict(Counter)
    for setting, row in scan.items():
        name, take, _, treatment, _ = setting
        identity = (name, take, treatment)
        if identity not in first:
            first[identity] = first_round_takes(starts[name], take, treatment)
        count = first[identity]
        if name.startswith('census:'):
            census_row = int(name.split(':')[1])
            group = 'census of three and four knots' if census_row < 219 else 'census of five knots'
        else:
            group = 'original rings'
        tally = groups[f'{group} / {take}']
        if 'error' in row:
            tally['timed out settings with an independently derived first-round take'] += count > 0
            continue
        if row['rounds_read'] == 0:
            tally['settings with no archived round read'] += 1
            continue
        tally['settings with a retained round'] += 1
        tally['settings with first-round takes'] += count > 0
        tally['settings with takes in first round only'] += bool(count and not row['takes made'])
        tally['settings with takes in any retained round'] += bool(count or row['takes made'])
    for item in observed_controls:
        name, take, _, treatment, _ = item['setting']
        assert first[(name, take, treatment)] == item['takes']
    return groups


def rotations(counts):
    return {counts[i:] + counts[:i] for i in range(len(counts))}


def ring_symmetries(counts):
    preserving = sum(counts == counts[i:] + counts[:i] for i in range(len(counts)))
    reverse = counts[::-1]
    return preserving + sum(counts == reverse[i:] + reverse[:i] for i in range(len(counts)))


def ring_roster():
    result = {}
    for size, max_loose in ((5, 5), (6, 4), (7, 3)):
        canonical = set()
        for counts in itertools.product(range(2, max_loose + 1), repeat=size):
            canonical.add(min(rotations(counts) | rotations(counts[::-1])))
        result[size] = canonical
    return result


def links_recount(records, rings=False):
    groups = defaultdict(Counter)
    starts_with_tests = defaultdict(set)
    starts_with_which = defaultdict(set)
    starts_without_start_held_links = defaultdict(set)
    asym_starts_without_start_held_links = defaultdict(set)
    ring_counts = defaultdict(set)
    which_cases = []
    observed_tests = set()
    keyed = {}
    for row in records:
        spec = row['spec']
        setting = configuration(spec)
        assert setting not in keyed
        keyed[setting] = row
        name = spec['start']
        if rings:
            counts = tuple(map(int, name.removeprefix('ringk:').split(',')))
            ring_counts[spec['ration']].add(counts)
            group = f'{len(counts)} knots / {spec["ration"]}'
        else:
            group = spec['take']
        tally = groups[group]
        tally['settings'] += 1
        tally[f'run stop: {stop_name(row)}'] += 1
        if 'error' in row:
            continue
        tally[f'unbarred run read through round {row["rounds_read"]}'] += 1
        if row['rows']:
            observed_tests.add(setting)
            starts_with_tests[group].add(name)
            tally['settings with four-run tests'] += 1
        if rings:
            symmetry_count = ring_symmetries(counts)
            tally['settings with trivial start symmetries'] += symmetry_count == 1
            tally['settings with equal knots'] += len(set(counts)) == 1
            tally['settings with tests and trivial start symmetries'] += (
                symmetry_count == 1 and bool(row['rows']))
            tally['tests with trivial start symmetries'] += (symmetry_count == 1) * len(row['rows'])
            tally['tests with equal knots'] += (len(set(counts)) == 1) * len(row['rows'])
        for test in row['rows']:
            record_test(tally, test)
            assert len(test['links']) == 2
            start_held = [link['start knot holds a linking distinction'] for link in test['links']]
            tally[f'number of second parts with a start-held linking distinction: {sum(start_held)}'] += 1
            for link in test['links']:
                tally[f'link verdict: {link["verdict"]}'] += 1
                tally['links passing the recorded ancestral predicate'] += link['ancestral']
                for label in link['classes of linking knots']:
                    tally[f'links carrying the recorded label: {label}'] += 1
            if not any(start_held) and rings:
                starts_without_start_held_links[group].add(name)
                tally['no start-held link tests with trivial start symmetries'] += symmetry_count == 1
                if symmetry_count == 1:
                    asym_starts_without_start_held_links[group].add(name)
            if test['classes'][1] != test['classes'][2]:
                tally[f'which one barred, with {sum(start_held)} start-held links'] += 1
                starts_with_which[group].add(name)
                which_cases.append({'setting': setting, 'test': test})
    for group, tally in groups.items():
        tally['distinct starts with four-run tests'] = len(starts_with_tests[group])
        tally['distinct starts with which one barred'] = len(starts_with_which[group])
        if rings:
            tally['distinct starts with no start-held link tests'] = len(starts_without_start_held_links[group])
            tally['distinct starts with no start-held tests and trivial start symmetries'] = len(
                asym_starts_without_start_held_links[group])
    return groups, ring_counts, which_cases, keyed, observed_tests


def controls(limit, initial_scan):
    take_rows = list(rows('check_take', limit))
    rename_rows = list(rows('renumber', limit))
    take_settings = {(r['start'], r['law']) for r in take_rows}
    rename_settings = {(r['start'], r['law']) for r in rename_rows}
    assert len(take_rows) == len(take_settings) == len(rename_rows) == len(rename_settings)
    assert take_settings == rename_settings
    omitted_round_one = []
    for row in take_rows:
        law = row['law'].split('/')
        setting = (row['start'], law[3], law[0], law[1], law[4])
        match = initial_scan.get(setting)
        if match and match['rounds_read'] == row['rounds']:
            missing = row['births that took'] - match['takes made']
            assert missing >= 0
            if missing:
                omitted_round_one.append({'setting': setting, 'takes': missing})
    return {
        'take settings': len(take_rows),
        'take distinct starts': len({r['start'] for r in take_rows}),
        'take settings with an actual take': sum(r['births that took'] > 0 for r in take_rows),
        'take settings with all births checked': sum(r['same as the rule'] == r['births'] for r in take_rows),
        'births with and without takes': dict(Counter({
            'with': sum(r['births that took'] for r in take_rows),
            'without': sum(r['births'] - r['births that took'] for r in take_rows),
        })),
        'births matching the take recomputation': sum(r['same as the rule'] for r in take_rows),
        'renumber settings with a four-run test': sum(r['tests'] > 0 for r in rename_rows),
        'renumber settings with a changing course': sum(
            any(len(set(ast.literal_eval(outcome[1])[1])) > 1 for outcome, _ in r['outcomes'])
            for r in rename_rows),
        'renumberings': sum(r['renumberings'] for r in rename_rows),
        'renumberings with equal archived summaries': sum(r['same'] for r in rename_rows),
        'round-one takes omitted from the scan counts for check settings': sum(
            item['takes'] for item in omitted_round_one),
        'settings whose scan take count omits observed round-one takes': omitted_round_one,
    }


def main(limit):
    result = {
        'scope': 'Independent recount of archived summaries, with one deterministic reader.',
        'comparison limits': [
            'Neither the individual birth data for all tests nor alternate barred-run link readings are stored here.',
            'A first part contributes at most one eligible second-part pair at a marked round.',
            'The link archives omit the common course bounds even though the sweep archives retain them.',
            'The late ring archive stores the reported minimum but omits entry values and witness positions.',
            'A recorded false ancestral predicate excludes a direct parent of both met members.',
            'Course partitions do not establish dependence on form with the same placement and arrival conditions.',
        ],
        'scan counts': {},
        'link counts': {},
        'links for which cases': {},
        'links selection relative to scan': {},
    }
    total = Counter()
    initial_scan = {}
    scan_m2_examples = []
    scan_m2_positions = Counter()
    scan_sources = {'links_rings': 'rings', 'links_census': 'census_wide', 'links_five': 'census_five_m2many'}
    scan_candidates = {}
    for name in SCAN_FILES:
        groups, candidates, keyed = scan_recount(rows(name, limit))
        result['scan counts'][name] = groups
        scan_candidates[name] = candidates
        assert not (initial_scan.keys() & keyed.keys())
        initial_scan.update(keyed)
        for counts in groups.values():
            for key, value in counts.items():
                if key == 'settings' or key.startswith('run stop:'):
                    total[key] += value
        for setting, row in keyed.items():
            for test in row.get('tests', []):
                if test.get('m', {}).get('m') == 2:
                    scan_m2_examples.append({'setting': setting, 'test': test})
                    entries = test['m']['entries']
                    assert len(entries) == 2 and entries[0][2] != entries[1][2]
                    positions = [(t, ast.literal_eval(position)[0]) for t, _, position in entries]
                    scan_m2_positions[str(positions)] += 1
    result['sweep settings and stops'] = total
    result['sweep records reporting m of two'] = scan_m2_examples
    result['m of two recorded witness rounds and kinds'] = scan_m2_positions
    expected = ring_roster()
    for name in LINK_FILES:
        ring = name == 'links_ringk'
        groups, observed_rings, which_cases, keyed, observed_tests = links_recount(rows(name, limit), ring)
        result['link counts'][name] = groups
        result['links for which cases'][name] = which_cases
        if ring:
            if limit is None:
                all_rings = set.union(*expected.values())
                assert observed_rings == {RATION_CAP: all_rings, 'FLOOR1': all_rings}
            continue
        candidates = scan_candidates[scan_sources[name]]
        result['links selection relative to scan'][name] = {
            'sweep settings with a four-run test': len(candidates),
            'link settings': len(keyed),
            'link settings with tests': len(observed_tests),
            'tested sweep settings absent from link archive': sorted(candidates - keyed.keys()),
            'extra link settings absent from tested sweep settings': sorted(keyed.keys() - candidates),
        }
    result['ring roster by number of knots'] = {
        size: {'classes': len(roster), 'equal knots': sum(len(set(c)) == 1 for c in roster),
               'trivial start symmetries': sum(ring_symmetries(c) == 1 for c in roster)}
        for size, roster in expected.items()
    }
    result['archived controls'] = controls(limit, initial_scan)
    observed = result['archived controls']['settings whose scan take count omits observed round-one takes']
    result['first round from the supplied starts'] = recount_first_round(initial_scan, observed)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    print(json.dumps(main(args.limit), indent=2, sort_keys=True))
