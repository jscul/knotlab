"""Validate and hash only this referee's authored outputs; no publication."""
import ast
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('/home/jscul/p-vs-np-contact-first')
EXPECTED = (
    'codex_report.md',
    'grow_core.py', 'grow_search.py', 'grow_lemma_audit.py',
    'grow_global_exact.py', 'grow_validate.py', 'grow_proof_review.md',
    'grow_sample.json', 'grow_inputs.json', 'grow_controls.json',
    'grow_smoke.jsonl', 'grow_results.jsonl', 'grow_halo6.jsonl',
    'grow_branching.jsonl', 'grow_lemma_audit.json', 'grow_global_exact.json',
    'grow_validation.json',
    'window_prepare.py', 'window_audit.py', 'window_censor_probe.py',
    'window_contract.md', 'window_inputs.json', 'window_results.json', 'window_results.jsonl',
    'window_censor_probe.json', 'window_manifest.json', 'window_audit.md',
    'scope_audit.py', 'scope_audit.json', 'scope_audit.md',
    'scope_global_review.md', 'referee_finalize.py',
)


def main():
    files = {}
    checks = []
    for name in EXPECTED:
        path = HERE / name
        assert path.is_file() and path.parent == HERE, name
        data = path.read_bytes()
        if path.suffix == '.json':
            json.loads(data)
            checks.append({'file': name, 'check': 'JSON parse'})
        elif path.suffix == '.jsonl':
            lines = [line for line in data.splitlines() if line.strip()]
            for line in lines:
                json.loads(line)
            checks.append({'file': name, 'check': 'JSONL parse', 'rows': len(lines)})
        elif path.suffix == '.py':
            ast.parse(data, filename=str(path))
            checks.append({'file': name, 'check': 'Python AST parse, no execution'})
        files[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    grow = json.loads((HERE / 'grow_validation.json').read_text())
    lemma = json.loads((HERE / 'grow_lemma_audit.json').read_text())
    window = json.loads((HERE / 'window_results.json').read_text())
    scope = json.loads((HERE / 'scope_audit.json').read_text())
    assert grow['positive_bonds_reverified'] == 119
    assert grow['independent_global_exact_depth_cases'] == 48
    assert grow['counterexamples_to_claimed_bound'] == []
    assert lemma['families'] == 632
    assert lemma['r_counts'] == {'1': 318, '2': 163, '3': 55, '4': 96}
    assert window['all_passed'] and window['families'] == 16
    assert window['state_values_checked'] == 21805
    assert not scope['scope_mismatches'] and not scope['earlier_inventory_mismatches']
    assert (HERE / 'codex_report.md').read_text().startswith('Verdict: **Confirmed with fixes**.')
    result = {
        'scope': 'independent referee CARRY-BOUND-20261114-001 R1',
        'verdict': 'Confirmed with fixes',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'interpreter': sys.executable,
        'files': files, 'syntax_checks': checks,
        'scientific_checks': {
            'growers_recomputed': 632, 'global_exact_minima': 48,
            'direct_positive_bonds_alternate_solver': 119,
            'grow_timeouts_preserved': len(grow['timeouts']),
            'window_panel': 16, 'final_bounded_in_panel': 15,
            'window_state_values_checked': 21805,
            'window_direct_checks_including_size7': 191,
            'scope_flags_rechecked': 5964,
            'new_correction': 'Narrowing: >6 is censored; eight verified size-7 states',
            'block_found': False,
        },
        'boundaries': {
            'write_root': str(HERE), 'network_used': False,
            'git_state_changed': False, 'published': False,
            'forbidden_study_python_opened_or_imported': False,
            'max_parallel_computational_processes': 3,
            'resource_limit_gb': 10,
            'validation_class': 'V2, fresh same-task code and permitted prior referee reuse',
            'external_or_human_replication': False,
            'global_corrections_log_edited': False,
        },
        'limitations': [
            'All-family window certificates were not all independently replayed; selected panel was.',
            'The seven existing path-DP certificates were inspected as data, not reimplemented.',
            'Raw per-key draw weights are inherited from allowed digest and earlier referee records.',
            'Global correction log was outside the specified scientific input list.',
            'Global-minimum support closure is proved only for the eight normalized chain families.',
        ],
    }
    (HERE / 'referee_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'verdict': result['verdict'], 'files_hashed': len(files),
                      'syntax_checks': len(checks), 'scientific_checks': result['scientific_checks']}))


if __name__ == '__main__':
    main()
