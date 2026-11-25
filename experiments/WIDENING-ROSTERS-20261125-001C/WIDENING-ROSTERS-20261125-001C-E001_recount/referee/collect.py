"""Validate finished shared-runner rows and export the neutral recount records."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from recount import CONTRACT_DIR, HERE, KNOT_LAWS, read_json


def validate_stage(stage, case, knot_law):
    if (stage['case'], stage['kl']) != (case['id'], knot_law):
        raise ValueError(f'wrong case on stage row: {stage}')
    members = stage['members']
    parts = stage['part_sizes']
    degrees = {int(degree): count for degree, count in stage['degree_histogram'].items()}
    maxima = stage['greatest_counts']
    if not 0 <= members <= stage['knots'] or sum(parts) != members:
        raise ValueError(f'member count does not match part sizes: {stage}')
    if parts != sorted(parts, reverse=True) or any(size <= 0 for size in parts):
        raise ValueError(f'invalid part sizes: {stage}')
    if sum(degrees.values()) != members or degrees.get(0, 0) != parts.count(1):
        raise ValueError(f'degrees do not match membership: {stage}')
    if sum(degree * count for degree, count in degrees.items()) != 2 * stage['pairs']:
        raise ValueError(f'degrees do not match pair count: {stage}')
    if len(maxima) != case['r_max'] + 1 or maxima != sorted(maxima):
        raise ValueError(f'invalid maximum reach vector: {stage}')
    if maxima[0] != int(bool(members)) or maxima[-1] > max(parts, default=0):
        raise ValueError(f'reach vector outside member counts: {stage}')
    if len(maxima) > 1 and maxima[1] != 1 + max(degrees, default=-1):
        raise ValueError(f'one-step reach does not match maximum degree: {stage}')
    if len(bytes.fromhex(stage['reach_sha256'])) != hashlib.sha256().digest_size:
        raise ValueError(f'invalid SHA-256: {stage}')


def validate_case(payload, case, knot_law):
    terminal = payload['terminal']
    stages = payload['stages']
    if (terminal['case'], terminal['kl']) != (case['id'], knot_law):
        raise ValueError(f'wrong case on terminal row: {terminal}')
    reached = [round_ for round_ in case['rounds'] if round_ <= terminal['round']]
    omitted = [round_ for round_ in case['rounds'] if round_ > terminal['round']]
    if reached != [stage['round'] for stage in stages] or omitted != terminal['omitted_rounds']:
        raise ValueError(f'missing or unexpected stage: {terminal}')
    knots = [stage['knots'] for stage in stages] + [terminal['knots']]
    if knots != sorted(knots):
        raise ValueError(f'whole-history size decreased: {terminal}')
    if any(stage['knots'] > case['knot_bound'] and stage['round'] != terminal['round']
           for stage in stages):
        raise ValueError(f'continued growing after the knot bound: {terminal}')
    for stage in stages:
        validate_stage(stage, case, knot_law)


def write_rows(path, rows):
    with path.open('x', encoding='utf-8') as file:
        for row in rows:
            file.write(json.dumps(row, separators=(',', ':')) + '\n')


def collect(result_path, output_dir):
    contract = read_json(CONTRACT_DIR / 'contract.json')
    cases = read_json(CONTRACT_DIR / contract['cases'])
    with result_path.open(encoding='utf-8') as file:
        records = [json.loads(line) for line in file]
    by_id = {row['case']: row for row in records}
    if len(by_id) != len(records):
        raise ValueError('multiple attempts found in a run configured without retries')
    expected = {f"{case['id']}/{kl}" for case in cases for kl in KNOT_LAWS}
    if unexpected := by_id.keys() - expected:
        raise ValueError(f'unexpected cases: {sorted(unexpected)}')
    rows = []
    terminals = []
    incomplete = 0
    for case in cases:
        for knot_law in KNOT_LAWS:
            case_id = f"{case['id']}/{knot_law}"
            record = by_id.get(case_id, {'status': 'missing', 'error': None})
            if record['status'] != 'ok':
                terminals.append({
                    'case': case['id'],
                    'kl': knot_law,
                    'reason': record['status'],
                    'error': record['error'],
                    'omitted_rounds': case['rounds'],
                })
                incomplete += 1
                continue
            payload = record['result']
            validate_case(payload, case, knot_law)
            rows.extend(payload['stages'])
            terminals.append(payload['terminal'])
    output_dir.mkdir(parents=True, exist_ok=True)
    target_names = ('stages.jsonl', 'terminal.jsonl')
    for name in target_names:
        if (output_dir / name).exists():
            raise FileExistsError(output_dir / name)
    write_rows(output_dir / target_names[0], rows)
    write_rows(output_dir / target_names[1], terminals)
    return len(rows), len(terminals), incomplete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    rows, terminals, incomplete = collect(args.results, args.output_dir)
    print(f'Validated and exported {rows} reached stages and {terminals} terminal records from {HERE.name}')
    if incomplete:
        print(f'{incomplete} cases missing or incomplete; their rounds are recorded as omitted')


if __name__ == '__main__':
    main()
