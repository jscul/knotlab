"""Validate and retain independent first meetings, actual takes, and literal projections."""

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from project import read_projection
from referee import FAMILY, ROOT, read_json


def record_bytes(row):
    return (json.dumps(row, separators=(',', ':')) + '\n').encode('utf-8')


def gzip_output(stack, path):
    file = stack.enter_context(path.open('xb'))
    return stack.enter_context(gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0))


def canonical_knots(mask):
    clauses = []
    for state in range(8):
        if not mask & (1 << state):
            clauses.append(' '.join(('~' if state & bit else '') + name
                                    for bit, name in zip((4, 2, 1), ('A', 'B', 'c'), strict=True)))
    cnf = '; '.join(clauses) if clauses else 'A ~A'
    output = subprocess.run(
        [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf,
         '--loops', 'A', 'B', '--contact', 'c', '--json'],
        cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')},
        check=True, capture_output=True)
    verdict = json.loads(output.stdout)
    ab, ac, bc, factored, kind = read_projection(mask)
    if (sum(1 << int(word, 2) for word in verdict['allowed']) != mask
            or verdict['is_knot'] != (kind == 'joint')):
        raise ValueError(f'canonical checker disagrees for mask {mask}')
    return {'ab': ab, 'ac': ac, 'bc': bc, 'factored_ac_bc': factored,
            'classification': kind, 'canonical': verdict}


def event_key(event):
    return (event['s'], tuple(event['X']), tuple(event['Y']))


def check_takes(result, events_out, takes_out, masks_out, mask_dir, case):
    labels = {key: result[key] for key in ('case', 'kl', 'rule')}
    extent = int(result['rounds_read'])
    if not 0 <= extent <= case['rounds'] or len(result['reach']) != extent:
        raise ValueError(f'invalid completed round accounting: {labels}')
    counts = Counter({'trajectories': 1})
    for round_, takes in enumerate(result['reach'], 1):
        for take in takes:
            if (not set(take['c1']) <= set(take['c2']) or take['c'] not in take['c2']
                    or take['near_eligible'] != (take['c'] in take['c1'])):
                raise ValueError(f'actual take does not match its offer sets: {labels}, {take}')
            counts['takes'] += 1
            counts['outer_takes'] += int(not take['near_eligible'])
            takes_out.write(record_bytes({**labels, 't': round_, **take}))
    if counts['outer_takes']:
        counts['trajectories_with_outer_takes'] += 1
    event_keys = set()
    expected_masks = 0
    has_outer_take = bool(counts['outer_takes'])
    for event in result['events']:
        key = event_key(event)
        if (key in event_keys or not key[1] < key[2] or set(key[1]) & set(key[2])
                or key[0] not in case['splits'] or not key[0] < event['t'] <= extent):
            raise ValueError(f'invalid first meeting: {labels}, {key}')
        event_keys.add(key)
        events_out.write(record_bytes({**labels, **event}))
        counts['meetings'] += 1
        counts['no_pure_routes'] += int(not event['routes'])
        counts['mixed_witnesses'] += len(event['mixed_witnesses'])
        if event['only_made_knots']:
            counts['only_made_meetings'] += 1
        strict = event['only_made_knots'] and not event['start_held_linking_distinctions']
        outer_trigger = any(offer['c'] not in offer['c1'] for offer in event['take_offers'].values())
        outer_pure_route = any(route['route'] == 'take' and not route['near_eligible']
                               for route in event['routes'])
        if strict:
            counts['only_made_no_start_holder_meetings'] += 1
            if outer_trigger:
                counts['strict_meetings_with_direct_outer_take'] += 1
                counts['strict_meetings_with_pure_direct_outer_take'] += int(outer_pure_route)
            elif has_outer_take:
                counts['strict_meetings_with_outer_take_elsewhere'] += 1
        for route in event['routes']:
            contacts = set(route['contacts'])
            if not contacts <= set(route['x_arms']) & set(route['y_arms']):
                raise ValueError(f'shared identity absent from one route arm: {labels}, {route}')
            if contacts & (set(route['a']) | set(route['b'])) or set(route['a']) & set(route['b']):
                raise ValueError(f'literal is shared or equals contact: {labels}, {route}')
            counts[f"routes_{route['route']}"] += 1
            counts['split_arm_routes'] += int(not contacts)
            counts['shared_candidates'] += len(contacts)
            counts['start_held_candidates'] += len(route['start_held_contacts'])
            counts['made_candidates'] += len(contacts) - len(route['start_held_contacts'])
            if not route['w_ancestor_u'] and not route['w_ancestor_v']:
                counts['routes_with_w_ancestor_of_neither_endpoint'] += 1
            if not (route['w_ancestor_u'] and route['w_ancestor_v']):
                counts['routes_with_w_not_ancestor_of_both_endpoints'] += 1
            expected_masks += len(contacts) * len(route['a']) * len(route['b'])
    digest = None
    if result['rule'] == 'MOST':
        if (result['projection_count'] != expected_masks
                or sum(result['classifications'].values()) != expected_masks):
            raise ValueError(f'not every literal occurrence was projected: {labels}')
        mask_path = mask_dir / f"{labels['case']}--{labels['rule']}--{labels['kl']}.jsonl.gz"
        if result['mask_file'] != mask_path.name or mask_path.stat().st_size != result['mask_bytes']:
            raise ValueError(f'literal stream is absent or changed size: {labels}')
        checksum = hashlib.sha256()
        line_count = 0
        with gzip.open(mask_path, 'rb') as stream:
            while block := stream.read(1024 * 1024):
                checksum.update(block)
                line_count += block.count(b'\n')
        digest = checksum.hexdigest()
        if line_count != expected_masks or digest != result['projection_sha256']:
            raise ValueError(f'literal count or SHA-256 failed after replaying gzip: {labels}')
        with mask_path.open('rb') as stream:
            shutil.copyfileobj(stream, masks_out)
        counts['literal_occurrences'] += expected_masks
        counts.update({f'literal_{kind}': count for kind, count in result['classifications'].items()})
    return counts, digest


def collect(run_dir, out_dir):
    contract = read_json(FAMILY / 'contract.json')
    cases = read_json(FAMILY / contract['cases'])
    expected = [f"{case['id']}--{rule}--{kl}"
                for case in cases for rule in contract['rules'] for kl in contract['knot_laws']]
    state = read_json(run_dir / 'state.json')
    config = read_json(run_dir / 'job.json')
    offsets = {}
    case_seconds = []
    finished = []
    outs = ('cases.jsonl', 'first_meetings.jsonl.gz', 'takes.jsonl.gz', 'literal_masks.jsonl.gz',
            'canonical.json', 'summary.json')
    if any((out_dir / name).exists() for name in outs):
        raise FileExistsError(f'output already present at {out_dir}')
    group_totals = defaultdict(Counter)
    rule_totals = defaultdict(Counter)
    missing = []
    masks_seen = set()
    with (run_dir / 'results.jsonl').open('rb') as source, ExitStack() as stack:
        while line := source.readline():
            row = json.loads(line)
            if row['case'] in offsets:
                raise ValueError(f'duplicate result: {row["case"]}')
            if row['job_sha'] != state['job_sha']:
                raise ValueError(f'result used unexpected program: {row["case"]}')
            offsets[row['case']] = source.tell() - len(line)
        if unexpected := offsets.keys() - set(expected):
            raise ValueError(f'unexpected result configurations: {sorted(unexpected)}')
        out_dir.mkdir(parents=True, exist_ok=True)
        totals_out = stack.enter_context((out_dir / outs[0]).open('xb'))
        events_out = gzip_output(stack, out_dir / outs[1])
        takes_out = gzip_output(stack, out_dir / outs[2])
        masks_out = stack.enter_context((out_dir / outs[3]).open('xb'))
        mask_dir = Path(config['params']['mask_dir'])
        by_id = {case['id']: case for case in cases}
        for key in expected:
            case_id, rule, kl = key.split('--')
            offset = offsets.get(key)
            if offset is not None:
                source.seek(offset)
                row = json.loads(source.readline())
            else:
                row = {'status': 'missing', 'error': None}
            if row['status'] != 'ok':
                missing.append({'case': key, 'status': row['status'], 'error': row['error']})
                continue
            result = row['result']
            if (result['case'], result['rule'], result['kl']) != (case_id, rule, kl):
                raise ValueError(f'result payload has the wrong configuration for {key}')
            case = by_id[case_id]
            offset = masks_out.tell()
            counts, mask_digest = check_takes(result, events_out, takes_out, masks_out, mask_dir, case)
            labels = {k: result[k] for k in ('case', 'rule', 'kl', 'start', 'rounds_read', 'knots', 'stop')}
            totals = {**labels, 'source': case['source'], 'ration': case['ration'],
                      'treatment': case['treatment'], 'counts': dict(counts),
                      'projection_sha256': mask_digest, 'metrics': result['metrics']}
            if rule == 'MOST':
                masks_seen.update(result['distinct_masks'])
                totals['projection_counts'] = result['classifications']
                totals['projection_gzip_offset'] = offset
                totals['projection_gzip_bytes'] = result['mask_bytes']
                totals['sat_counts'] = result['sat_counts']
                totals['literal_annotations'] = result['literal_annotations']
            totals_out.write(record_bytes(totals))
            group_totals[rule, kl, case['source']].update(counts)
            rule_totals[rule, kl].update(counts)
            finished.append(datetime.fromisoformat(row['finished_at']))
            case_seconds.append(row['seconds'])
    with (out_dir / outs[4]).open('xb') as target:
        target.write(record_bytes({str(mask): canonical_knots(mask) for mask in sorted(masks_seen)}))
    start = datetime.fromisoformat(state['started'])
    end = datetime.fromisoformat(state['heartbeat'])
    summary = {
        'status': state['counts'], 'expected_configurations': len(expected),
        'not_run': missing, 'distinct_projected_masks': sorted(masks_seen),
        'files_sha256': {name: hashlib.file_digest((out_dir / name).open('rb'), 'sha256').hexdigest()
                         for name in outs[:-1]},
        'by_rule_and_knot_law': {'/'.join(key): dict(value) for key, value in sorted(rule_totals.items())},
        'by_source_rule_and_knot_law': {'/'.join(key): dict(value)
                                      for key, value in sorted(group_totals.items())},
        'runtime': {'started': state['started'], 'finished': state['heartbeat'],
                    'wall_seconds': (end - start).total_seconds(),
                    'peak_runner_rss_mib': state['peak_rss_mb'],
                    'longest_configuration_seconds': max(case_seconds, default=0),
                    'first_configuration_seconds': (min(finished) - start).total_seconds() if finished else None,
                    'configuration': {name: config[name] for name in (
                        'case_mem', 'case_timeout', 'cpu_quota', 'mem_max', 'runtime_max', 'workers', 'job_sha')}},
    }
    with (out_dir / outs[5]).open('x', encoding='utf-8') as target:
        json.dump(summary, target, indent=2)
        target.write('\n')
    print(f'Validated {len(finished)} configurations, {len(masks_seen)} literal tables, {len(missing)} missing')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('out_dir', type=Path)
    args = parser.parse_args()
    collect(args.run_dir, args.out_dir)
