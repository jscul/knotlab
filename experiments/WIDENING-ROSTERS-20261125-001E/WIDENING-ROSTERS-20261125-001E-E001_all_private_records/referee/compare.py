"""Compare the two finished calculations on physical identity and occurrence weight."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from driver import compact, physical_key


def file_sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def compare(primary, independent):
    first = {}
    second = {}
    with primary.open(encoding='utf-8') as source:
        for line in source:
            group = json.loads(line)
            if group['status'] != 'ok':
                raise ValueError(f'primary group incomplete: {group["case"]}')
            raw = group['result']
            if raw['total_requests'] != len(raw['rows']):
                raise ValueError(f'primary group size mismatch: {group["case"]}')
            for u, v, c, outcome, weight in raw['rows']:
                key = (raw['law'], raw['system'], u, v, c)
                if key in first:
                    raise ValueError(f'duplicate primary key: {key}')
                first[key] = (outcome, weight)
    with gzip.open(independent, 'rt', encoding='utf-8') as source:
        for line in source:
            row = json.loads(line)
            key = physical_key(row)
            if key in second:
                raise ValueError(f'duplicate independent key: {key}')
            second[key] = (row['outcome'], row['count'])

    equal = hashlib.sha256()
    differences = []
    shared = first.keys() & second.keys()
    for key in sorted(shared):
        if first[key] != second[key]:
            differences.append({'key': key, 'primary': first[key], 'independent': second[key]})
        else:
            equal.update(compact([*key, *first[key]]) + b'\n')
    return {'primary_records': len(first), 'independent_records': len(second),
            'matching_records': len(shared) - len(differences),
            'missing_from_independent': sorted(first.keys() - second.keys()),
            'missing_from_primary': sorted(second.keys() - first.keys()),
            'differences': differences, 'shared_decisions_sha256': equal.hexdigest(),
            'primary_sha256': file_sha256(primary), 'independent_sha256': file_sha256(independent)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primary', type=Path)
    parser.add_argument('independent', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = compare(args.primary, args.independent)
    with args.output.open('x', encoding='utf-8') as target:
        json.dump(result, target, indent=2)
        target.write('\n')
    print(f"Matched {result['matching_records']} physical records")
