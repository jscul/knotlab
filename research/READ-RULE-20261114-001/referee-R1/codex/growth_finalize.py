"""Bind this audit lane's exact outputs, source versions, and retained caps."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/jscul/p-vs-np-contact-first')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = (HERE / 'growth_search.py').read_text()
    inserted = """            if row['minimum'] <= 3:
                # Every possible smaller 2-bond consists exactly of one root
                # and one target, both already in this prefix. No arbitrary
                # third member beyond the prefix can make a smaller bond.
                row['global_exact'] = True
                row['global_reason'] = 'minimum at most 3; all root-target pairs are present and exhaustively tested, and every singleton is full by living complement closure'
                row['status'] = 'exact_global'
"""
    assert source.count(inserted) == 1
    launch = HERE / 'growth_search_launch_v1.py'
    launch.write_text(source.replace(inserted, ''))
    version_note = {
        'growth_smoke.jsonl': 'ran launch_v1',
        'growth_deeper_simple.jsonl': 'started launch_v1; during execution the current source gained only the minimum<=3 classification block shown in growth_finalize.py. Every successful row has minimum>=6, so the added branch was unexercised. The meta source hash describes completion-time source; the exact launch source is retained.',
        'growth_unresolved_prefix.jsonl': 'ran current growth_search.py',
        'launch_v1_sha256': sha(launch),
        'current_sha256': sha(HERE / 'growth_search.py'),
        'search_algorithm_changed_during_run': False,
        'artifact_fields_changed_for_any_deeper_simple_row': False,
    }
    (HERE / 'growth_source_versions.json').write_text(json.dumps(version_note, indent=2, sort_keys=True) + '\n')
    # Preserve the sole failed positive-witness probe. Its lower-size exclusion
    # was then reproduced and combined with an independently checked upper
    # witness, rather than interpreted as a mathematical failure.
    fresh = json.loads((HERE / 'growth_hand_read_exception_results.json').read_text())
    row = next(r for r in fresh['rows'] if r['sample'] == 'main_positive_gadget' and r['absolute_depth'] == 6)
    initial_cap = {'key': row['key'], 'key_sha256': row['key_sha256'],
                   'absolute_depth': 6, 'S_call_length': 5, 'cutoff': 8,
                   'variables': 22, 'clauses': 40, 'status': 'timeout',
                   'minimum': None, 'all_sizes_2_through_7_exhausted': True,
                   'proved_lower_bound_prefix': 8, 'time_cap_seconds': 60,
                   'actual_seconds': 66.33404519292526,
                   'queries': 7834, 'iterations': 5320, 'models': 15422,
                   'peak_rss_kib': 59568,
                   'source': 'growth_hand_read_exception_initial.py',
                   'source_sha256': sha(HERE / 'growth_hand_read_exception_initial.py'),
                   'provenance': 'transcribed from the failed command tool output; not a fresh measurement',
                   'resolved_by': 'exact lower-size-only search plus explicit d+2 witness, in growth_hand_read_exception_results.json'}
    (HERE / 'growth_hand_read_exception_initial_cap.json').write_text(json.dumps(initial_cap, indent=2, sort_keys=True) + '\n')
    files = ['q3_results.json', 'growth_smoke.jsonl', 'growth_deeper_simple.jsonl',
             'growth_unresolved_prefix.jsonl', 'growth_handdesigned.json',
             'growth_hand_read_exception_results.json',
             'growth_source_versions.json', 'growth_hand_read_exception_initial_cap.json']
    parsed = {}
    for name in files:
        text = (HERE / name).read_text()
        parsed[name] = ([json.loads(line) for line in text.splitlines() if line]
                        if name.endswith('.jsonl') else json.loads(text))
    q3 = parsed['q3_results.json']
    simple = parsed['growth_deeper_simple.jsonl']
    unresolved = parsed['growth_unresolved_prefix.jsonl']
    design = parsed['growth_handdesigned.json']
    assert len(q3['rows']) == 12 and all(r['minimum'] == 2 for r in q3['rows'])
    assert len(simple) == 16 and sum(r['global_exact'] for r in simple) == 10
    assert sum(r['status'] == 'timeout' for r in simple) == 6
    assert len(unresolved) == 20 and all(r['minimum'] in (3, 4) for r in unresolved)
    assert len(fresh['rows']) == 12 and all(r['minimum'] == r['absolute_depth'] + 2 for r in fresh['rows'])
    for r in simple + unresolved + design['stall_rows'] + design['fixed_lag_full_prefix_rows']:
        if r.get('minimum') is not None:
            assert r['verification']['is_bond']
            assert r['verification']['every_single_deletion_full']
    for r in fresh['rows']:
        assert r['explicit_chain_witness_check']['is_bond']
        assert r['explicit_chain_witness_check']['every_single_deletion_full']
    for r in q3['rows']:
        assert r['explicit_check']['is_bond'] and r['explicit_check']['every_single_deletion_full']
    summary = {'Q3_exact_global_depth_cells': 12,
               'deeper_simple_exact_global_depth_cells': 10,
               'deeper_simple_retained_timeouts': 6,
               'unresolved_family_exact_prefix_cells': 20,
               'unresolved_global_exact_cells': sum(r['global_exact'] for r in unresolved),
               'fresh_syntactic_converse_counterexample_depth_cells': 12,
               'stall_exact_global_cells': len(design['stall_rows']),
               'fixed_lag_exact_full_prefix_cells': len(design['fixed_lag_full_prefix_rows']),
               'fixed_lag_exact_reduced_prefix_cells': len(design['fixed_lag_reduced_rows']),
               'all_recorded_successful_witnesses_check_every_single_deletion': True,
               'V_level': 'producer-independent direct CNF construction using permitted prior referee exact search, plus fresh independent complete-projection witness checks; not external replication',
               'sources': {str((HERE / name).relative_to(ROOT)): sha(HERE / name) for name in files},
               'own_code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(HERE.glob('growth_*.py'))},
               'q3_code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(HERE.glob('q3_*.py'))},
               'python': sys.executable,
               'preserved_caps': ['six deeper-simple 30s timeouts', 'one initial positive-gadget 60s timeout, subsequently resolved by a supplied witness'],
               'not_performed': ['network calls', 'git mutations', 'publication', 'READ producer/checker Python import or read', 'scope/lifecycle writes'],
               'thread_id': '01a1d936-2ede-72c2-a41b-c56e37c83eff'}
    context = [
        'research/READ-RULE-20261114-001/read_rule.md',
        'research/READ-RULE-20261114-001/preregistration.md',
        'research/READ-RULE-20261114-001/codex_spec.md',
        'research/READ-RULE-20261114-001/advisor_review_answer.md',
        'research/READ-RULE-20261114-001/advisor_proof_answer.md',
        'proofs/READ-RULE-20261114-001A/READ-RULE-20261114-001A-P001_read_rule/proof.md',
        'research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_global_exact.py',
        'research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_search.py',
        'research/CARRY-BOUND-20261114-001/carry_bound.md',
    ]
    summary['context_sources_sha256'] = {name: sha(ROOT / name) for name in context}
    summary['peak_reported_rss_kib'] = max(
        q3['peak_rss_kib'], design['peak_rss_kib'], fresh['peak_rss_kib'],
        initial_cap['peak_rss_kib'],
        *(r.get('peak_rss_kib', 0) for r in simple + unresolved))
    (HERE / 'growth_manifest.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if not k.endswith('sha256') and k not in ['sources']}, indent=2))

if __name__ == '__main__':
    main()
