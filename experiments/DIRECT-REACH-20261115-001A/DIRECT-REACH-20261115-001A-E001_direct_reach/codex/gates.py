"""Assemble the three gates from durable shared-runner records."""
import collections
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reuse import HERE, ROOT, provenance
from job import atomic_json


def summarize():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from longrun import load_results
    records = load_results(HERE / 'gates_checked')
    groups = collections.defaultdict(list)
    errors = []
    for key, row in records.items():
        if row['status'] != 'ok':
            errors.append({'case': key, 'status': row['status'], 'error': row.get('error')})
        else:
            groups[row['result']['gate']].append(row['result'])
    expected = {'G-tie': 50, 'G-reach': 146, 'G-hom': 1}
    gates = {}
    for name, count in expected.items():
        rows = groups[name]
        gates[name] = {'expected_cases': count, 'completed_cases': len(rows),
                       'passed': len(rows) == count and all(r.get('passed') is True for r in rows),
                       'failures': [{k: v for k, v in row.items()
                                     if k in ('description', 'index', 'comparisons', 'passed')}
                                    for row in rows if row.get('passed') is not True]}
    gates['G-tie']['alive_descriptions'] = sum(r['truth']['states'] > 0 for r in groups['G-tie'])
    gates['G-tie']['dead_descriptions'] = sum(r['truth']['states'] == 0 for r in groups['G-tie'])
    gates['G-tie']['enumeration'] = 'exhaustive plain backtracking; fully free completion subcubes counted exactly'
    gates['G-reach']['compared_cells'] = sum(len(r['comparisons']) for r in groups['G-reach'])
    if groups['G-hom']:
        gates['G-hom']['detail'] = groups['G-hom'][0]
    execution_manifests = {row['result']['source_manifest']['sha256']: row['result']['source_manifest']
                           for row in records.values() if row['status'] == 'ok'}
    result = {'passed': not errors and all(g['passed'] for g in gates.values()),
              'gates': gates, 'errors': errors,
              'execution_source_manifests': list(execution_manifests.values()),
              'inspection_provenance': provenance(),
              'records': 'gates_checked/results.jsonl'}
    atomic_json(HERE / 'gates.json', result)
    print(json.dumps({k: {'passed': v['passed'], 'completed_cases': v['completed_cases']}
                      for k, v in gates.items()}, indent=2))
    return result


if __name__ == '__main__':
    summarize()
