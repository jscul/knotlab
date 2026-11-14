"""Validate this restricted referee delivery and record reproducible hashes.

Reads only this directory and the input paths explicitly allowed by the user.
Writes only run_manifest.json in this directory; no Git or network operations.
"""
import ast
import datetime
import hashlib
import json
import resource
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
START = datetime.datetime(2026, 11, 14, 1, 6, 52, tzinfo=datetime.timezone.utc)
INPUTS = [
    'research/CENSUS-FORGET-20261114-001/census_forget.md',
    'research/CENSUS-FORGET-20261114-001/preregistration.md',
    'research/CENSUS-FORGET-20261114-001/advisor_review_answer.md',
    'research/FREE-TARGET-20261114-001/referee-R1/codex/codex_report.md',
    'research/FREE-TARGET-20261114-001/referee-R1/codex/direct_bonds.py',
    'research/FREE-TARGET-20261114-001/referee-R1/codex/relations_audit.py',
    'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py',
    'experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl',
    'experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/reading.json',
    'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz',
    'experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz',
]
FILES = [
    'codex_report.md', 'target_inventory.py', 'target_inventory.json',
    'direct_other_targets.py', 'direct_other_targets.jsonl',
    'direct_other_targets_odd.jsonl', 'direct_delayed_S.jsonl',
    'validate_other_targets.py', 'direct_validation.json',
    'sample_audit.py', 'sample_audit.json', 'sample_audit.md', 'sample_run.log',
    'chain_share_audit.py', 'chain_share_audit.json', 'chain_share_audit.md',
    'finalize_referee.py',
]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parsed = {}
    for name in FILES:
        path = OUT / name
        assert path.is_file() and path.stat().st_size
        if path.suffix == '.json':
            parsed[name] = json.loads(path.read_text())
        elif path.suffix == '.jsonl':
            parsed[name] = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        elif path.suffix == '.py':
            ast.parse(path.read_text(), filename=name)
    inventory = parsed['target_inventory.json']
    assert inventory['summary']['families'] == 657
    assert inventory['summary']['counts']['all']['other_own'] == 183
    assert inventory['summary']['counts']['certified']['other_own'] == 153
    groups = inventory['all_certificate_scope']
    safe_single = groups['c=1 other']['no_other_own'] - groups['c=1 other']['no_other_own_but_delayed_S']
    safe_multi = groups['c>=2']['no_other_own'] - groups['c>=2']['no_other_own_but_delayed_S']
    assert (safe_single, safe_multi) == (384, 1046)
    points = sum((parsed[name] for name in ('direct_other_targets.jsonl',
                  'direct_other_targets_odd.jsonl', 'direct_delayed_S.jsonl')), [])
    assert len(points) == 112 and all(r['minimum'] == 3 for r in points)
    assert parsed['direct_validation.json']['passed']
    assert parsed['direct_validation.json']['point_count'] == 112
    assert all(all(r['verification']['every_deletion_full']) for r in points)
    sample = parsed['sample_audit.json']
    assert sample['status'] == 'pass'
    assert sample['summary']['sample_families'] == 127
    assert sample['summary']['sample_R_i'] == 318
    assert sample['summary']['source_completed_verdicts_matched'] == 103
    assert sample['summary']['mismatches'] == 0
    # Verify provenance for the mutable in-task inventory and worker scripts.
    provenance_checks = []
    for filename in ('sample_audit.json', 'chain_share_audit.json'):
        data = parsed[filename]
        for field in ('input_sha256', 'inputs_sha256', 'source_sha256'):
            mapping = data.get(field, {})
            if not isinstance(mapping, dict):
                continue
            for name, expected in mapping.items():
                p = Path(name)
                if not p.is_absolute():
                    p = ROOT / p
                if not p.is_file() or not isinstance(expected, str) or len(expected) != 64:
                    continue
                # All paths here have already been admitted by this task's
                # lane; refuse prohibited producer Python even for hashing.
                if p.suffix == '.py' and any(part in str(p) for part in (
                    'experiments/FREE-TARGET-20261114-001A/',
                    'experiments/CENSUS-FORGET-20261114-001A/')):
                    raise AssertionError('prohibited producer Python in provenance')
                actual = sha(p)
                provenance_checks.append({'file': filename, 'input': name,
                                           'matches': actual == expected})
    assert all(r['matches'] for r in provenance_checks), provenance_checks
    now = datetime.datetime.now(datetime.timezone.utc)
    result = {
        'scope_kind': 'epic', 'scope_id': 'CENSUS-FORGET-20261114-001',
        'activity': 'restricted independent referee; no lifecycle changes',
        'verdict': 'Refuted',
        'started_utc': START.isoformat(), 'finished_utc': now.isoformat(),
        'elapsed_minutes': (now - START).total_seconds()/60,
        'python': '/home/jscul/p-vs-np-contact-first/.venv/bin/python -B',
        'input_sha256': {name: sha(ROOT / name) for name in INPUTS},
        'output_sha256': {name: sha(OUT / name) for name in FILES},
        'validation': {'all_json_jsonl_parse': True, 'all_python_ast_parse': True,
            'direct_points': 112, 'all_direct_global_minima': 3,
            'fresh_truth_table_controls': 16, 'inherited_search_controls': 6,
            'sample_families': 127, 'sample_R_i': 318,
            'sample_completed_source_verdicts_reproduced': 103,
            'sample_mismatches': 0, 'sample_caps_new_nonforgetting_certificates': 24,
            'provenance_checks': provenance_checks},
        'safe_restricted_subtotal': {'single_call_nonchains': safe_single,
            'multicall_nonchains': safe_multi, 'chain_draws': 5633,
            'draws': 5633 + safe_single + safe_multi,
            'qualification': 'Sufficient restricted tally, conditional on inherited uniform ray growth and corrected gap/ancestry arguments; not a full all-copy classification'},
        'invocations': [
            'target_inventory.py',
            'direct_other_targets.py --ids f25a8e17968d,3fe70047c198,f3c4843e45fa,ec647c80edb0,c6cbc657bedb --depths 1,2,3,4,6,10 --extras 1,2 --seconds 5 --max-size 4',
            'direct_other_targets.py --ids f25a8e17968d,3fe70047c198,f3c4843e45fa,ec647c80edb0,c6cbc657bedb --depths 5,7,9,11 --extras 1,2 --seconds 10 --max-size 4 --output direct_other_targets_odd.jsonl',
            'direct_other_targets.py --ids e8ce853eb78a --depths 1,2,3,4,5,6 --extras 1,2 --seconds 15 --max-size 4 --output direct_delayed_S.jsonl',
            'validate_other_targets.py', 'sample_audit.py', 'chain_share_audit.py',
            'finalize_referee.py'],
        'resource_observations': {'max_task_compute_processes': 3,
            'per_worker_address_space_cap_bytes': 2*1024**3,
            'sample_peak_rss_kib': sample['peak_rss_kib'],
            'main_direct_peak_rss_kib': max(r['peak_rss_kib'] for r in points),
            'finalizer_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'sample_compute_seconds': sample['seconds'],
            'all_commands_under_15_minutes': True,
            'no_resource_or_timeout_result_promoted': True},
        'limitations': [
            'Only the specified sample receives a fully fresh relation/semigroup recomputation.',
            'Census first-ray growth authority is inherited; this task recounts its records.',
            'The 188 excluded certificates are not all classified as bounded.',
            'Nominal Wilson intervals do not themselves validate the sampling model.',
            'No canonical definitions, research status, shared correction log, or public record changed.'],
    }
    assert result['elapsed_minutes'] < 60
    (OUT / 'run_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'elapsed_minutes': result['elapsed_minutes'],
                      'direct_points': 112, 'sample_families': 127,
                      'safe_restricted_draws': result['safe_restricted_subtotal']['draws'],
                      'provenance_checks': len(provenance_checks)}, indent=2))


if __name__ == '__main__':
    main()
