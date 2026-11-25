"""Validate the sealed recount and compare it with the earlier referee's four rules."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path

import job


CONTROLS = ('MOST', 'SOLE', 'RECENT', 'OUTER')
OLD_ARTIFACTS = job.ROOT / ('artifacts/WIDENING-ROSTERS-20261125-001D/'
                           'WIDENING-ROSTERS-20261125-001D-E001_links/referee')
ARCHIVES = job.ROOT / 'research/WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further'
COUNT_FIELDS = ('only_made_count', 'strict_count', 'strict_direct_outer_count',
                'strict_direct_outer_any_count', 'strict_with_outer_elsewhere_count')


def event_key(event):
    return event['s'], event['t'], tuple(event['X']), tuple(event['Y'])


def read_results(path, cases, contract):
    expected = {(case, rule, law) for case in cases for rule in contract['rules']
                for law in contract['knot_laws']}
    state = job.previous.read_json(path / 'state.json')
    config = job.previous.read_json(path / 'job.json')
    if (not state['complete'] or state['error'] or config['params'] or
            state['counts']['ok'] != len(expected)):
        raise ValueError('expected a complete run on the full frozen set')
    job.check_hash(Path(config['job']), state['job_sha'])
    results = {}
    with (path / 'results.jsonl').open() as file:
        for line in file:
            row = json.loads(line)
            if row['status'] != 'ok' or row['job_sha'] != state['job_sha']:
                raise ValueError(f'unexpected runner record: {row["case"]}')
            result = row['result']
            label = tuple(result[name] for name in ('case', 'rule', 'kl'))
            if label not in expected or label in results or '--'.join(label) != row['case']:
                raise ValueError(f'duplicate or unexpected trajectory: {label}')
            verify_result(result, cases[label[0]])
            results[label] = result
    if results.keys() != expected:
        raise ValueError('the runner results omit trajectories')
    return results, state


def verify_result(result, case):
    rounds = result['rounds_read']
    events = result['events']
    keys = [event_key(event) for event in events]
    outer = result['outer_takes']
    if (result['start'] != case['start'] or not 0 <= rounds <= case['rounds']
            or (result['stop'] is None and rounds != case['rounds'])
            or ((result['stop'] == 'knots') != (result['knots'] > case['knot_bound']))
            or result['split_coverage'] != [s for s in case['splits'] if s < rounds]
            or result['meetings_count'] != len(events) or len(set(keys)) != len(events)
            or keys != sorted(keys) or result['outer_take_count'] != len(outer)
            or len(outer) > result['takes'] or len(set(map(tuple, outer))) != len(outer)
            or any(not 0 < take[0] <= rounds for take in outer)):
        raise ValueError(f'bad completed-round accounting for {result["case"]}/{result["rule"]}')
    if any(s not in case['splits'] or not s < t <= rounds or set(x) & set(y) or x >= y
           for s, t, x, y in keys):
        raise ValueError('misidentified first meeting')
    names = ('strict_count', 'strict_direct_outer_count', 'strict_direct_outer_any_count',
             'strict_with_outer_elsewhere_count')
    strict = [e for e in events if e['strict']]
    wanted = (len(strict), sum(e['direct_outer'] for e in strict),
              sum(e['direct_outer_any'] for e in strict),
              sum(bool(outer) and not e['direct_outer_any'] for e in strict))
    counts = result['event_counts']
    if (tuple(counts.get(name, 0) for name in names) != wanted
            or not len(strict) <= counts.get('only_made_count', 0) <= len(events)
            or [event_key(e) for e in result['strict_events']] != [event_key(e) for e in strict]
            or any(not e['linking_knots'] for e in result['strict_events'])
            or any(e['strict'] and e['start_knot_holds_linking_distinction'] for e in events)
            or any(e['direct_outer'] and not e['direct_outer_any'] for e in events)
            or len(result['event_provenance']) != len(events)):
        raise ValueError('inconsistent strict meeting accounting')
    actual = hashlib.sha256(b''.join(job.row_bytes(e) for e in events)).hexdigest()
    if actual != result['events_sha256']:
        raise ValueError('first meeting digest mismatch')


def read_controls(cases, contract, candidates):
    expected = {(case, rule, law) for case in cases for rule in CONTROLS
                for law in contract['knot_laws']}
    summary = job.previous.read_json(OLD_ARTIFACTS / 'summary.json')
    for name in ('cases.jsonl', 'first_meetings.jsonl.gz'):
        job.check_hash(OLD_ARTIFACTS / name, summary['files_sha256'][name])
    controls = {}
    with (OLD_ARTIFACTS / 'cases.jsonl').open() as file:
        for line in file:
            record = json.loads(line)
            label = tuple(record[name] for name in ('case', 'rule', 'kl'))
            if label not in expected or label in controls:
                raise ValueError(f'unexpected earlier rule receipt: {label}')
            controls[label] = record
    if controls.keys() != expected:
        raise ValueError('earlier study omitted a trajectory')
    strict_candidates = {(case, law) for (case, _, law), value in candidates.items()
                         if value['strict_events']}
    records = defaultdict(list)
    made_keys = defaultdict(dict)
    current = None
    with gzip.open(OLD_ARTIFACTS / 'first_meetings.jsonl.gz', 'rt') as file:
        for line in file:
            event = json.loads(line)
            case_id, rule, law = label = tuple(event[k] for k in ('case', 'rule', 'kl'))
            start_held = bool(event['start_held_linking_distinctions'])
            strict = event['only_made_knots'] and not start_held
            key = event_key(event)
            records[label].append((key, event['only_made_knots'], start_held))
            if rule == 'MOST' and strict and (case_id, law) in strict_candidates:
                if current != label:
                    case = cases[case_id]
                    stars = job.previous.raw_start(case['start'], job.settings['named'], job.settings['census'])
                    stages, rounds, _, stop = job.previous.grow(stars, case, rule, law)
                    receipt = controls[label]
                    if (len(rounds), stages[-1].n_knots, stop) != tuple(
                            receipt[k] for k in ('rounds_read', 'knots', 'stop')):
                        raise ValueError(f'earlier trajectory no longer reproduces: {label}')
                    knot_ids, distinction_ids = job.stable_identities(stages, rounds)
                    current = label
                made_keys[label][key] = job.physical_keys(event, knot_ids, distinction_ids)
    for label, receipt in controls.items():
        rows = records[label]
        counts = receipt['counts']
        if (len(rows) != counts.get('meetings', 0) or
                sum(made for _, made, _ in rows) != counts.get('only_made_meetings', 0) or
                sum(made and not held for _, made, held in rows) !=
                counts.get('only_made_no_start_holder_meetings', 0)):
            raise ValueError(f'earlier meeting stream miscounts its receipts: {label}')
    return controls, records, made_keys


def find_archive_part_pairs(cases, old_records):
    old_contract = job.previous.read_json(job.PREDECESSOR / 'contract.json')
    files = {}
    for source in {case['source'] for case in cases.values()}:
        file = ARCHIVES / source
        job.check_hash(file, old_contract['inputs'][str(file.relative_to(job.ROOT))])
        with gzip.open(file, 'rt') as stream:
            files[source] = [json.loads(line) for line in stream]
    identified = defaultdict(set)
    totals = defaultdict(Counter)
    for label, case in cases.items():
        raw = files[case['source']][case['line'] - 1]
        counts = totals[case['source']]
        if (raw['spec']['take'] != 'MET2-MANY' or
                any(raw['spec'][name] != case[name] for name in ('start', 'ration', 'treatment')) or
                len(raw['rows']) != case['archive_rows']):
            raise ValueError(f'archive record does not match frozen case {label}')
        records = old_records[label, 'MOST', 'nae']
        for row in raw['rows']:
            sides = []
            for t, size, link in zip(row['meets'], row['sizes'][1:], row['links'], strict=True):
                made = link['verdict'] == 'only through made knots'
                held = link['start knot holds a linking distinction']
                choices = defaultdict(dict)
                for key, made_here, held_here in records:
                    s, when, x, y = key
                    if (s, when, made_here, held_here) != (row['s'], t, made, held):
                        continue
                    for a, b in ((x, y), (y, x)):
                        if len(a) == row['sizes'][0] and len(b) == size:
                            choices[a][b] = key
                sides.append(choices)
            first, second = sides
            assignments = [(first[x][y], second[x][z]) for x in first.keys() & second.keys()
                           for y in first[x] for z in second[x] if y != z]
            if len(assignments) == 1:
                counts['unique_archive_rows'] += 1
                identified[label].update(assignments[0])
            elif assignments:
                counts['ambiguous_archive_rows'] += 1
            else:
                counts['unrecovered_archive_rows'] += 1
            counts['archive_rows'] += 1
        counts['distinct_uniquely_identified_pairs'] += len(identified[label])
    return identified, totals


def write_gzip_rows(path, rows):
    with path.open('xb') as raw, gzip.GzipFile(fileobj=raw, filename='', mode='wb', mtime=0) as file:
        for row in rows:
            file.write(job.row_bytes(row))


def compare_ring_archive(cases, strict_matches):
    """Use the older ring sweep's explicit side IDs, which the links summary omits."""
    archive = ARCHIVES / 'rings.jsonl.gz'
    with gzip.open(archive, 'rt') as stream:
        sweep = [json.loads(line) for line in stream]
    recipe = ('start', 'ration', 'treatment')
    receipts = {}
    for label, case in cases.items():
        if case['source'] != 'links_rings.jsonl.gz':
            continue
        row, = [r for r in sweep if r['spec']['take'] == 'MET2-MANY' and
                r['spec']['knot_law'] == 'nae' and all(r['spec'][k] == case[k] for k in recipe)]
        pairs = set()
        for test in row['tests']:
            for side, t in zip(('Y1', 'Y2'), test['meets'], strict=True):
                x, y = sorted((tuple(sorted(test['X'])), tuple(sorted(test[side]))))
                pairs.add((test['s'], t, x, y))
        counts = Counter()
        for match in strict_matches:
            if (match['case'] == label and match['kl'] == 'nae' and
                    match['same_physical_receipt_as_most'] and event_key(match) in pairs):
                counts[match['rule']] += 1
        receipts[label] = {'start': case['start'], 'archived_pair_count': len(pairs),
                           'archived_pairs': sorted(pairs),
                           'strict_physical_pair_matches_in_not_all_equal': dict(counts)}
    with archive.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'source': str(archive.relative_to(job.ROOT)), 'source_sha256': sha, 'records': receipts}


def summarize(run, output):
    job.setup({})
    contract = job.settings['contract']
    cases = {case['id']: case for case in job.settings['cases']}
    results, state = read_results(run, cases, contract)
    controls, old_records, made_keys = read_controls(cases, contract, results)
    identified, archive_totals = find_archive_part_pairs(cases, old_records)
    by_law_rule, by_source = defaultdict(Counter), defaultdict(Counter)
    pairs, matched, examples = [], [], {}
    for _, (case, rule, law) in job.cases():
        label = case['id'], rule, law
        result = results[label]
        names = {k: result[k] for k in ('case', 'start', 'rule', 'kl', 'rounds_read', 'stop', 'knots')}
        totals = Counter({k: result[k] for k in ('takes', 'outer_take_count', 'meetings_count')})
        totals.update({name: result['event_counts'].get(name, 0) for name in COUNT_FIELDS})
        totals['trajectories'] += 1
        totals['trajectories_with_outer'] += int(bool(totals['outer_take_count']))
        totals['trajectories_with_strict'] += int(bool(totals['strict_count']))
        totals['stop_' + (result['stop'] or 'completed')] += 1
        choices = result['plural_choice_comparison']
        totals.update(choices)
        if totals['strict_count']:
            totals.update({f'{k}_on_strict_trajectories': v for k, v in choices.items()})
        baseline_label = case['id'], 'MOST', law
        physical = made_keys[baseline_label]
        by_parts = {keys[0] for keys in physical.values()}
        by_full = {keys[1] for keys in physical.values()}
        legacy_keys = {physical[key][1] for key in (identified[case['id']] & physical.keys())}
        for event, keys in zip(result['events'], result['event_provenance'], strict=True):
            if not event['strict']:
                continue
            match = {'same_parts_and_round_as_most': keys[0] in by_parts,
                     'same_physical_receipt_as_most': keys[1] in by_full,
                     'same_receipt_as_uniquely_located_archive_meeting': law == 'nae' and keys[1] in legacy_keys}
            totals.update({k: int(v) for k, v in match.items()})
            matched.append({**names, **event, **match})
        if result['strict_events'] and (rule, law) not in examples:
            examples[rule, law] = {**names, 'event': result['strict_events'][0],
                                   'example_outer_takes_elsewhere': result['outer_takes'][:2]}
        paired = {}
        for comparator in CONTROLS:
            control_label = case['id'], comparator, law
            control = controls[control_label]
            common_round = min(control['rounds_read'], result['rounds_read'])
            common = [r for r in old_records[control_label] if r[0][1] <= common_round]
            now = [e for e in result['events'] if e['t'] <= common_round]
            paired[comparator] = {'rounds_read': control['rounds_read'], 'stop': control['stop'],
                                  'common_completed_rounds': common_round,
                                  'observed_meetings': control['counts'].get('meetings', 0),
                                  'observed_outer_takes': control['counts'].get('outer_takes', 0),
                                  'control_meetings_through_common_round': len(common),
                                  'candidate_meetings_through_common_round': len(now),
                                  'control_strict_through_common_round': sum(made and not held for _, made, held in common),
                                  'candidate_strict_through_common_round': sum(e['strict'] for e in now)}
        pairs.append({**names, 'counts': dict(totals), 'controls': paired})
        by_law_rule[rule, law].update(totals)
        by_source[case['source'], rule, law].update(totals)
    runtime = (datetime.fromisoformat(state['heartbeat']) - datetime.fromisoformat(state['started'])).total_seconds()
    write_gzip_rows(output / 'paired.jsonl.gz', pairs)
    write_gzip_rows(output / 'physical_matches.jsonl.gz', matched)
    summary = {'configurations': len(results), 'status': state['counts'], 'wall_seconds': runtime,
               'peak_runner_rss_mib': state['peak_rss_mb'], 'timing': 'timing.json',
               'by_rule_and_law': {'/'.join(key): group for key, group in by_law_rule.items()},
               'by_source_rule_and_law': {'/'.join(key): group for key, group in by_source.items()},
               'historical_archive_identification': archive_totals,
               'ring_archive_identification': compare_ring_archive(cases, matched),
               'representative_strict_meetings': {'/'.join(key): value for key, value in examples.items()}}
    with (output / 'summary.json').open('x') as file:
        json.dump(summary, file, indent=2)
        file.write('\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    summarize(args.run, args.output)
