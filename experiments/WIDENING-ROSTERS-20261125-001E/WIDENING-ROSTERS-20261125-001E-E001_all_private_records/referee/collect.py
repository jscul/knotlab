"""Export the checked physical results and their weights in frozen request order."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path

from driver import INPUT, ROOT, compact, physical_key, requests


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def check_receipt(row, wanted):
    if any(row[key] != wanted[key] for key in ('count', 'width')):
        raise ValueError(f'wrong occurrence count or width: {physical_key(wanted)}')
    if row['outcome'] in ('undecided', 'incoherent'):
        return
    bits = ''.join(str(int(row[name])) for name in ('product', 'proper_a', 'proper_b'))
    derived = bits if row['a_width'] and row['b_width'] else 'empty-arm'
    if row['outcome'] != derived:
        raise ValueError(f'outcome does not match verified conditions: {physical_key(row)}')
    if row['core_rows'] == 2 and row['a_width'] and row['b_width']:
        expected = '111'
        if row['extra_shared_width']:
            expected = '100' if row['law'] == 'nae' else '000'
        if not row['coherent'] or not row['c_open'] or row['outcome'] != expected:
            raise ValueError(f'two-holder result does not match closed form: {physical_key(row)}')


def collect(run, out):
    plan = json.loads((out / 'rehearsal_plan.json').read_bytes())
    for file, expected in plan['software_sha256'].items():
        if digest(ROOT / file) != expected:
            raise ValueError(f'software changed after timing: {file}')
    if digest(INPUT / 'requests.jsonl') != plan['requests_sha256']:
        raise ValueError('physical requests changed after timing')
    state = json.loads((run / 'state.json').read_bytes())
    cfg = json.loads((run / 'job.json').read_bytes())
    cases = requests()
    expected = {physical_key(row): row for row in cases}
    results = {}
    failures = []
    with (run / 'results.jsonl').open(encoding='utf-8') as source:
        for line in source:
            group = json.loads(line)
            if group['status'] != 'ok':
                failures.append({name: group[name] for name in ('case', 'status', 'error')})
                continue
            if group['job_sha'] != state['job_sha']:
                raise ValueError(f'different execution source in {group["case"]}')
            for row in group['result']['records']:
                key = physical_key(row)
                if key in results or key not in expected:
                    raise ValueError(f'duplicate or unexpected physical result: {key}')
                check_receipt(row, expected[key])
                results[key] = row
    if missing := expected.keys() - results.keys():
        failures.extend({'physical_key': key, 'status': 'missing'} for key in sorted(missing))

    output = out / 'records.jsonl.gz'
    by_law = defaultdict(lambda: defaultdict(Counter))
    methods = Counter()
    first = {}
    hashes = hashlib.sha256()
    with output.open('xb') as file, gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as target:
        for key, wanted in expected.items():
            if key not in results:
                continue
            row = results[key]
            group = by_law[row['law']][row['outcome']]
            group['unique'] += 1
            group['occurrences'] += row['count']
            methods[row['method']] += 1
            first.setdefault(f"{row['law']}/{row['outcome']}", {**row, 'example': wanted['example']})
            line = compact(row) + b'\n'
            hashes.update(line)
            target.write(line)

    # Check the retained bytes independently of the write path.
    line_count = 0
    replay_hash = hashlib.sha256()
    with gzip.open(output, 'rb') as source:
        while block := source.read(1024 * 1024):
            replay_hash.update(block)
            line_count += block.count(b'\n')
    if line_count != len(results) or replay_hash.hexdigest() != hashes.hexdigest():
        raise ValueError('retained physical results failed hash or row-count replay')
    elapsed = (datetime.fromisoformat(state['heartbeat']) - datetime.fromisoformat(state['started'])).total_seconds()
    summary = {
        'requests': len(expected), 'checked': len(results), 'failures': failures,
        'by_law': by_law, 'by_method': methods, 'first_examples': first,
        'raw_records_sha256': hashes.hexdigest(), 'compressed_records_sha256': digest(output),
        'runtime': {'wall_seconds': elapsed, 'peak_runner_rss_mib': state['peak_rss_mb'],
                    'status': state['counts'], 'settings': {name: cfg[name] for name in (
                        'workers', 'cpu_quota', 'mem_max', 'case_timeout', 'case_mem', 'job_sha')}},
    }
    with (out / 'summary.json').open('x', encoding='utf-8') as target:
        json.dump(summary, target, indent=2)
        target.write('\n')
    return len(results), failures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    checked, failures = collect(args.run, args.out)
    print(f'Replayed {checked} physical records; {len(failures)} incomplete or failed entries')
