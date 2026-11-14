"""Required finite gates and independent replay of smoke certificates."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from certificates import (CADICAL, check_state, unpack_state, verify_bond_certificate)
from job import atomic_json
from pattern import pattern, level_ids
from search import SearchEngine


def tree_gate():
    key = [1, [0], [0], [0], [[0, 1, 2]]]
    K, nvars = pattern(key, 9), 1023
    work = HERE / 'work' / 'G_tree'
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    engine = SearchEngine(K, nvars, work)
    rows = []
    try:
        for s in range(1, 5):
            A, B = level_ids(3), level_ids(3 + s)
            deadline = time.monotonic() + 300
            any_result = engine.search(A, B, deadline=deadline, corrupt_test=(s == 1))
            target = engine.search(A, B, allowed=range((1 << (4 + s)) - 1), deadline=deadline)
            verify_bond_certificate(K, nvars, any_result)
            verify_bond_certificate(K, nvars, target)
            rows.append({'s': s, 'expected': s + 2, 'anywhere': any_result,
                         'target_restricted': target,
                         'passed': any_result['L'] == target['L'] == s + 2})
        # Flip exactly one pinned value in a witness. Regardless of whether
        # the new value still satisfies the knots, it violates its assignment.
        result = rows[0]['anywhere']
        item = result['certificate']['maximal_proper'][0]
        state = unpack_state(result['certificate']['state_pool'][item['state_indices'][0]], nvars)
        units = [-v - 1 for v in item['support']]
        assert check_state(K, state, units)
        state[item['support'][0]] ^= 1
        state_rejected = not check_state(K, state, units)
        proof_rejected = result['certificate']['refutation']['corrupted_hint_rejected']
        return {'passed': all(r['passed'] for r in rows), 'cases': rows,
                'corruption': {'flipped_state_value_rejected': state_rejected,
                               'changed_effective_proof_hint_rejected': proof_rejected}}
    finally:
        engine.close()
        shutil.rmtree(work)


def latest_records(path):
    latest = {}
    if path.exists():
        for line in path.read_text().splitlines():
            record = json.loads(line)
            latest[record['case']] = record
    return list(latest.values())


def mono_records():
    """Latest gate evidence, retaining memory retries in separate outputs."""
    records = {r['case']: {**r, 'run_directory': 'mono_gate'}
               for r in latest_records(HERE / 'mono_gate' / 'results.jsonl')}
    for directory in ('mono_retry', 'mono_remaining_retry', 'mono_additional_retry', 'mono_bounded_retry'):
        for record in latest_records(HERE / directory / 'results.jsonl'):
            expected_previous = 'mono_remaining_retry' if directory == 'mono_bounded_retry' else 'mono_gate'
            assert records[record['case']]['run_directory'] == expected_previous
            assert records[record['case']]['status'] == 'memory'
            if directory == 'mono_retry':
                assert record['case'] == 'b7af5bcb77f74404b9e42ebf5b166c8a405073106163c3a2e171a0e416846dd4'
            else:
                config = json.loads((HERE / directory / 'job.json').read_text())
                assert record['case'] in config['params']['ids'].split(',')
            records[record['case']] = {**record, 'run_directory': directory}
    return list(records.values())


def aggregate():
    receipt = json.loads((HERE / 'final_execution_source_hashes.json').read_text())
    actual_sources = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                      for name in receipt['runtime_sha256']}
    assert actual_sources == receipt['runtime_sha256'], 'runtime source changed after execution freeze'
    archive = HERE / 'validation_history' / 'before_close_cleanup'
    memo_archive = HERE / 'validation_history' / 'before_memo_bounds'
    presence_archive = HERE / 'validation_history' / 'before_presence_encoding'
    archived_searches = {hashlib.sha256((p / 'search.py').read_bytes()).hexdigest()
                         for p in (archive, memo_archive, presence_archive)}
    predecessor = json.loads((HERE / 'continuation_provenance.json').read_text())
    assert all(hashlib.sha256((archive / name).read_bytes()).hexdigest() == digest
               for name, digest in predecessor['preserved_gates'].items()), 'completed gate evidence changed'
    for receipt_name in ('execution_source_hashes.json', 'mono_retry_source_hashes.json',
                         'mono_remaining_retry_source_hashes.json', 'mono_additional_retry_source_hashes.json',
                         'mono_remaining_retry_after_cleanup_source_hashes.json',
                         'mono_additional_retry_after_cleanup_source_hashes.json',
                         'mono_bounded_retry_source_hashes.json'):
        retry_receipt = json.loads((HERE / receipt_name).read_text())
        for name, digest in retry_receipt['runtime_sha256'].items():
            current = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            assert current == digest or (name == 'search.py' and digest in archived_searches), 'unrecorded runtime source change'
    controls = latest_records(HERE / 'final_encoding_controls' / 'results.jsonl')
    assert {r['case'] for r in controls} == {'brute', 'pattern', 'tree'}
    assert all(r['status'] == 'ok' and r['result']['passed'] for r in controls)
    gates = {}
    for short in ('brute', 'pattern', 'tree'):
        path = HERE / f'g_{short}.json'
        gates[f'G-{short}'] = json.loads(path.read_text()) if path.exists() else {'passed': False, 'pending': True}
    mono = mono_records()
    successful = [r for r in mono if r['status'] == 'ok']
    comparisons = [{'case': r['case'], **c} for r in successful for c in r['result']['comparisons']]
    selected = json.loads((HERE / 'mono_selection.json').read_text())
    exact_mono_roster = len(selected) == len(set(selected)) == 50 and {r['case'] for r in mono} == set(selected)
    entry_modules = {'mono_gate': 'mono_job.py', 'mono_retry': 'mono_retry_job.py',
                     'mono_remaining_retry': 'mono_remaining_retry_job.py',
                     'mono_additional_retry': 'mono_remaining_retry_job.py',
                     'mono_bounded_retry': 'mono_bounded_retry_job.py'}
    mono_hashes = {directory: hashlib.sha256((HERE / module).read_bytes()).hexdigest()
                   for directory, module in entry_modules.items()}
    mono_receipts_match = all(r['job_sha'] == mono_hashes[r['run_directory']] for r in mono)
    original = latest_records(HERE / 'mono_gate' / 'results.jsonl')
    retained_failures = [{k: v for k, v in r.items() if k != 'result'}
                         for r in original if r['status'] != 'ok']
    retry_failures = []
    for directory in ('mono_retry', 'mono_remaining_retry', 'mono_additional_retry', 'mono_bounded_retry'):
        for line in (HERE / directory / 'results.jsonl').read_text().splitlines():
            record = json.loads(line)
            if record['status'] != 'ok':
                retry_failures.append({'run_directory': directory,
                                       **{k: v for k, v in record.items() if k != 'result'}})
    gates['G-mono'] = {'passed': len(successful) == 50 and exact_mono_roster and mono_receipts_match
                       and all(r['result']['passed'] and len(r['result']['comparisons']) == 4
                               and r['result']['N10']['union']['verdict'] == 'alive'
                               for r in successful),
                       'case_count': len(successful), 'required_cases': 50,
                       'exact_roster': exact_mono_roster,
                       'runner_job_hashes_match': mono_receipts_match,
                       'retry_cases': [r['case'] for r in mono if r['run_directory'] != 'mono_gate'],
                       'retained_original_attempt_failures': retained_failures,
                       'retained_retry_attempt_failures': retry_failures,
                       'source_epochs': 'Original successful cases use archived pre-cleanup search.py;700620 uses callback cleanup;0758 and smoke use final bounded memoization and equivalent presence exclusions. Exact search, correction/exclusion meaning, certificates and budgets unchanged; timing/witnesses/undecided outcomes can differ.',
                       'numeric_comparisons': sum(c['numeric'] for c in comparisons),
                       'comparisons': comparisons,
                       'failures': [r['case'] for r in mono if r['status'] != 'ok' or not r['result']['passed']]}
    smoke = latest_records(HERE / 'smoke' / 'results.jsonl')
    ok = [r for r in smoke if r['status'] == 'ok']
    pilot = json.loads((HERE / 'prepared' / 'population_P.json').read_text())
    expected_smoke = {payload['id'] for payload in pilot['keys'][:20]}
    exact_smoke_roster = {r['case'] for r in smoke} == expected_smoke
    job_hash = hashlib.sha256((HERE / 'job.py').read_bytes()).hexdigest()
    smoke_receipts_match = all(r['job_sha'] == job_hash for r in smoke)
    bonds = states = 0
    errors = []
    for record in ok:
        try:
            result = record['result']
            K = pattern(result['key'], result['N'])
            for row in result['levels']:
                for field in ('anywhere', 'target_restricted'):
                    summary = verify_bond_certificate(K, result['nvars'], row.get(field, {}))
                    bonds += summary['bonds']
                    states += summary['states']
                for entry in row.get('per_target', []):
                    summary = verify_bond_certificate(K, result['nvars'], entry)
                    bonds += summary['bonds']
                    states += summary['states']
        except Exception as exc:
            errors.append({'case': record['case'], 'error': repr(exc)})
    corruption = gates['G-tree'].get('corruption', {})
    gates['G-cert'] = {'passed': len(ok) == 20 and exact_smoke_roster and smoke_receipts_match
                       and not errors and all(corruption.values()) and len(corruption) == 2,
                       'smoke_ok': len(ok), 'required_smoke_cases': 20,
                       'exact_smoke_roster': exact_smoke_roster,
                       'runner_job_hashes_match': smoke_receipts_match,
                       'bonds_replayed': bonds, 'proper_projection_states_replayed': states,
                       'corruption': corruption, 'failures': errors}
    version = subprocess.run([CADICAL, '--version'], capture_output=True, text=True, check=True).stdout.strip()
    root = HERE.parents[3]
    input_paths = [
        'research/LEVEL-REACH-20261114-001/codex_spec.md',
        'research/LEVEL-REACH-20261114-001/codex_spec_addendum.md',
        'research/LEVEL-REACH-20261114-001/design.md',
        'docs/tooling/shared-runner.md',
        'scripts/longrun.py',
    ]
    answer = {'all_passed': all(v['passed'] for v in gates.values()), 'gates': gates,
              'solver_version': version,
              'continuation': {'preserved_gate_evidence_verified': True,
                               'predecessor_receipt': 'continuation_provenance.json',
                               'execution_receipt': 'execution_source_hashes.json',
                               'retry_execution_receipt': 'mono_retry_source_hashes.json',
                               'remaining_retry_execution_receipt': 'mono_remaining_retry_source_hashes.json',
                               'additional_retry_execution_receipt': 'mono_additional_retry_source_hashes.json',
                               'final_execution_receipt': 'final_execution_source_hashes.json',
                               'close_cleanup_provenance': 'close_cleanup_provenance.json',
                               'post_cleanup_retry_receipt': 'mono_remaining_retry_after_cleanup_source_hashes.json',
                               'post_cleanup_additional_retry_receipt': 'mono_additional_retry_after_cleanup_source_hashes.json',
                               'bounded_retry_receipt': 'mono_bounded_retry_source_hashes.json',
                               'memoization_change_provenance': 'memo_bounds_provenance.json',
                               'support_encoding_change_provenance': 'presence_encoding_provenance.json',
                               'runtime_sources_unchanged_since_freeze': True,
                               'P_population_unchanged': True,
                               'runtime_change': 'E_R rule clarified; closed-engine callbacks detached; optional caches bounded; support exclusions use equivalent auxiliary presence clauses. No original-pattern, exact-search, correction/exclusion meaning, certificate or budget change. Timed outcomes can differ.'},
              'code_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(HERE.glob('*.py'))},
              'input_sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                               for name in input_paths},
              'evidence_sha256': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in [HERE / 'g_brute.json', HERE / 'g_pattern.json', HERE / 'g_tree.json',
                                            HERE / 'g_brute_fallback.json',
                                            HERE / 'mono_gate' / 'results.jsonl', HERE / 'mono_gate' / 'job.json',
                                            HERE / 'mono_selection.json', HERE / 'smoke' / 'results.jsonl',
                                            HERE / 'mono_retry' / 'results.jsonl', HERE / 'mono_retry' / 'job.json',
                                            HERE / 'mono_remaining_retry' / 'results.jsonl',
                                            HERE / 'mono_remaining_retry' / 'job.json',
                                            HERE / 'mono_additional_retry' / 'results.jsonl',
                                            HERE / 'mono_additional_retry' / 'job.json',
                                            HERE / 'mono_bounded_retry' / 'results.jsonl',
                                            HERE / 'mono_bounded_retry' / 'job.json',
                                            HERE / 'smoke' / 'job.json', HERE / 'prepared' / 'population_P.json',
                                            HERE / 'prepared' / 'population_R.json',
                                            HERE / 'continuation_provenance.json', HERE / 'execution_source_hashes.json',
                                            HERE / 'mono_retry_source_hashes.json',
                                            HERE / 'mono_remaining_retry_source_hashes.json',
                                            HERE / 'mono_additional_retry_source_hashes.json',
                                            HERE / 'final_execution_source_hashes.json',
                                            HERE / 'close_cleanup_provenance.json',
                                            HERE / 'mono_remaining_retry_after_cleanup_source_hashes.json',
                                            HERE / 'mono_additional_retry_after_cleanup_source_hashes.json',
                                            HERE / 'mono_bounded_retry_source_hashes.json',
                                            HERE / 'memo_bounds_provenance.json',
                                            HERE / 'presence_encoding_provenance.json',
                                            HERE / 'final_controls' / 'job.json',
                                            HERE / 'final_controls' / 'results.jsonl',
                                            HERE / 'bounded_controls' / 'job.json',
                                            HERE / 'bounded_controls' / 'results.jsonl',
                                            HERE / 'final_encoding_controls' / 'job.json',
                                            HERE / 'final_encoding_controls' / 'results.jsonl',
                                            archive / 'search.py', archive / 'g_brute.json',
                                            archive / 'g_pattern.json', archive / 'g_tree.json',
                                            archive / 'mono_remaining_retry_4G_job.json',
                                            archive / 'mono_remaining_retry_failed_4G.jsonl',
                                            archive / 'mono_additional_retry_3G_job.json',
                                            archive / 'mono_additional_retry_failed_3G.jsonl',
                                            memo_archive / 'search.py', memo_archive / 'g_brute.json',
                                            memo_archive / 'g_brute_fallback.json', memo_archive / 'g_pattern.json',
                                            memo_archive / 'g_tree.json', memo_archive / 'final_execution_source_hashes.json',
                                            presence_archive / 'search.py', presence_archive / 'g_brute.json',
                                            presence_archive / 'g_brute_fallback.json', presence_archive / 'g_pattern.json',
                                            presence_archive / 'g_tree.json', presence_archive / 'final_execution_source_hashes.json']},
              'lrat_source_sha256': hashlib.sha256((HERE / 'lrat_check.c').read_bytes()).hexdigest(),
              'lrat_binary_sha256': hashlib.sha256((HERE / 'lrat_check').read_bytes()).hexdigest()}
    atomic_json(HERE / 'gates.json', answer)
    return answer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['tree', 'aggregate'])
    args = parser.parse_args()
    if args.phase == 'tree':
        result = tree_gate()
        atomic_json(HERE / 'g_tree.json', result)
        print(json.dumps({'gate': 'G-tree', 'passed': result['passed'], 'corruption': result['corruption']}))
    else:
        result = aggregate()
        print(json.dumps({'all_passed': result['all_passed'],
                          'gates': {k: v['passed'] for k, v in result['gates'].items()}}))
