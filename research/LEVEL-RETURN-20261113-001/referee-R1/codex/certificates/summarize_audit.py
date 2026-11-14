"""Summarize completed finite checks; no producer imports or external writes."""
from pathlib import Path
import json
import platform
import pysat
import fresh_certify as audit

HERE = Path(__file__).resolve().parent
summary = json.loads(audit.SUMMARY.read_text())
r1_keys = {r['key'] for r in summary['R1']['rows']}
r1_cases = {f'{key}-L{n:02d}' for key in r1_keys for n in range(13,17)}
attempts = {}
inputs = {}
for path in sorted(HERE.glob('*.result.json')):
    value = json.loads(path.read_text())
    value['result_path'] = path.name
    attempts.setdefault(value['case'], []).append(value)
    inputs[value['case']] = value
for path in sorted(HERE.glob('*.input.json')):
    value = json.loads(path.read_text())
    inputs[value['case']] = value


def record(case):
    source = inputs[case]
    candidates = attempts.get(case, [])
    certified = [v for v in candidates if v['certified']]
    best = certified[-1] if certified else candidates[-1] if candidates else None
    return {'case': case, 'knots': source['knots'],
            'registered_verdict': source['registered']['verdict'],
            'pattern_sha256': source['pattern_sha256'],
            'unconditional_cnf_sha256': source['unconditional_cnf_sha256'],
            'registered_pattern_hash_matches': source['registered_pattern_hash_matches'],
            'registered_count_matches': source['registered_count_matches'],
            'fresh_verdict': best['verdict'] if best else 'not solved',
            'fresh_certified': bool(best and best['certified']),
            'certificate_result': best['result_path'] if best else None,
            'attempts': [{'result': v['result_path'], 'solver': v['solver'],
                          'conflict_budget': v['conflict_budget'],
                          'verdict': v['verdict'], 'certified': v['certified'],
                          'seconds': v['seconds']} for v in candidates]}


r1 = [record(c) for c in sorted(r1_cases) if c in inputs]
other = [record(c) for c in sorted(set(inputs)-r1_cases)]
controls = json.loads((HERE/'controls.json').read_text())
inventory = json.loads((HERE/'inventory.json').read_text())
counts = {}
for value in r1:
    name = ('certified '+value['fresh_verdict']) if value['fresh_certified'] else 'not certified'
    counts[name] = counts.get(name,0)+1
disagreements = [v['case'] for values in attempts.values() for v in values
                 if not v['agrees_with_registered_decided']]
result = {
    'scope_id': 'LEVEL-RETURN-20261113-001',
    'lane': 'independent finite certificate audit',
    'source_reading': 'No Python or C from either LEVEL-RETURN producer family was read or imported. LEVEL-RETURN summarize.py was not read.',
    'independence': 'Earlier independently authored pattern generator and RUP checker reused; finite checks by a subagent in the same AI task, not human review or external replication.',
    'primary_evidence': 'Fresh checked finite models and RUP refutations, not original certificate replay.',
    'r1_coverage': {'planned_cases': 28, 'reconstructed_cases': len(r1),
                    'counts': counts,
                    'all_reconstructed_counts_and_hashes_match': all(v['registered_count_matches'] and v['registered_pattern_hash_matches'] for v in r1),
                    'fresh_versus_registered_decided_disagreements': disagreements},
    'r1_cases': r1,
    'other_cases': other,
    'original_replay_gap': inventory,
    'controls': {'direct_small_patterns': len(controls['direct_letter_by_letter_pattern_agreements']),
                 'wrong_word_order_detected': len(controls['wrong_word_order_detected']),
                 'proof_controls': controls['proof_controls'],
                 'model_controls': controls['model_controls'],
                 'native_lrat_conversion_control': json.loads((HERE/'native_control.json').read_text()) if (HERE/'native_control.json').exists() else None},
    'unresolved_registered_dead_cases': [v['case'] for v in r1 if v['registered_verdict']=='dead' and not v['fresh_certified']],
    'original_undecided_cases': [v['case'] for v in r1 if v['registered_verdict']=='undecided'],
    'limits': ['Deleted original CNFs, models, and LRAT files cannot be independently replayed or compared clause by clause.',
               'Only the explicitly listed cases have fresh certification; unsampled registered verdicts remain outside this audit.',
               'Complement symmetry is checked and used as a satisfiability-preserving unit restriction for refutations.',
               'Finite case checks do not establish any all-level statement.'],
    'runtime': {'python': platform.python_version(), 'pysat': pysat.__version__,
                'resource_limit': '3 GiB address space per process; one compute process at a time in this lane',
                'invocation_prefix': '/home/jscul/p-vs-np-contact-first/.venv/bin/python -B',
                'temporary_stream_disclosure': 'Initial PySAT controls/solves did not set tempfile.tempdir or TMPDIR, so closed unlinked temporary proof streams used the default /tmp policy. Initial compiler scratch policy was likewise not overridden; compiler intermediates may have used /tmp. Before further solver creation, tempfile.tempdir and TMPDIR were set to this certificates directory. All retained artifacts are in this directory.',
                'checker_compile': 'g++ -O3 -std=c++17 check_rup_fast.cpp -lz -o check_rup_fast',
                'ownership': 'Only this certificates directory was intentionally modified; no git state change, network call, or publication.'},
    'final_source_sha256': {name: audit.sha((HERE/name).read_bytes()) for name in
                      ('fresh_certify.py','native_refute.py','summarize_audit.py','check_rup_fast.cpp','check_rup_fast')},
    'runner_provenance': 'The adapter evolved during the audit (bounded passes, explicit C-stream flush, timeout handling and temp-path correction). Final adapter hashes inventory the retained source only; they are not asserted as historical per-case runner hashes. Per-case generator and control checker hashes bind the unchanged independent generator/checker.',
    'retention': 'Checked models/refutations and compressed CNFs are retained. Only own regenerable uncompressed CNF/LRAT scratch was removed after compression. The checker binary is retained for parent replay.'
}
audit.dump(HERE/'audit_summary.json',result)
print(json.dumps({'r1': result['r1_coverage'], 'other_cases':len(other),
                  'unresolved_registered_dead_cases':result['unresolved_registered_dead_cases']}),flush=True)
