"""Focused final reconciliation and a fresh relation calculation for the chain.

This does not rerun the census. No producer Python or network is used, and
all writes stay in this referee directory. The recurrence below is separate
from the direct CNF/CEGAR searches that generated the finite measurements.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import resource
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex'
RESOURCE_LIMIT = 1024**3
resource.setrlimit(resource.RLIMIT_AS, (RESOURCE_LIMIT, RESOURCE_LIMIT))
PREEXISTING = {'brief_codex.md', 'codex_last_message.md'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((HERE / name).read_text())


def chain_relation(depth):
    """Project hidden x_0,...,x_{d-2} by two-state dynamic enumeration."""
    size = depth+2
    allowed = []
    for value in range(1 << size):
        possible = {(value >> 0) & 1}
        for j in range(depth):
            w = (value >> (j+1)) & 1
            possible = {x for x in (0, 1)
                        if any(not (previous == x == w) for previous in possible)}
        if ((value >> (depth+1)) & 1) in possible:
            allowed.append(value)
    return allowed


def discard_coordinate(value, j):
    return (value & ((1 << j)-1)) | ((value >> (j+1)) << j)


def chain_checks():
    rows = []
    for depth in range(1, 13):
        relation = chain_relation(depth)
        size = depth+2
        forbidden = sorted(set(range(1 << size))-set(relation))
        assert len(forbidden) == 2
        assert forbidden[0] ^ forbidden[1] == (1 << size)-1
        deletion_sizes = [len({discard_coordinate(value, j) for value in relation})
                          for j in range(size)]
        assert deletion_sizes == [1 << (size-1)]*size
        # Every assignment to root plus all pendants extends: that mandatory
        # d+1-member lower-bound set cannot itself be a bond.
        mandatory = {value & ((1 << (depth+1))-1) for value in relation}
        assert len(mandatory) == 1 << (depth+1)
        rows.append(dict(absolute_depth=depth, support_size=size,
                         projection_cardinality=len(relation),
                         forbidden=forbidden, every_single_deletion_full=True,
                         root_and_all_pendants_full=True))
    # Deliberate mutation: two independent successive constraints cannot be
    # replaced by one root/endpoint NAE with an unobserved pendant.
    correct = chain_relation(2)
    wrong = [value for value in range(16)
             if not (((value >> 0) & 1) == ((value >> 2) & 1) == ((value >> 3) & 1))]
    assert correct != wrong
    return dict(method='fresh two-state recurrence, no SAT or relation library',
                rows=rows, malformed_collapsed_chain_rejected=True)


def ledger_hashes(name, sections):
    result = []
    ledger = load(name)
    for section in sections:
        for relative, expected in ledger[section].items():
            path = ROOT / relative
            # Explicitly disallow even a hash read of either prohibited
            # Python tree. Hash inputs are scientific records/allowed code.
            assert not (path.suffix == '.py' and relative.startswith((
                'experiments/READ-RULE-20261114-001B/',
                'proofs/READ-RULE-20261114-001Z/')))
            assert digest(path) == expected, (name, relative)
            result.append(relative)
    return len(result)


def counts():
    with (HERE/'coverage_results.jsonl').open() as source:
        rows = [json.loads(line) for line in source if line.strip()]
    assert len(rows) == 5964 and len({r['key'] for r in rows}) == 5964
    scope = [r for r in rows if r['in_scope']]
    bounded = [r for r in scope if r['verdict'] == 'bounded']
    assert len(scope) == 5789 and sum(r['weight'] for r in scope) == 5853
    assert len(bounded) == 5067 and sum(r['weight'] for r in bounded) == 5129
    correct = [r for r in bounded if r['R'].get('exists_good_each_Q_residue')]
    strict = [r for r in bounded if r['R'].get('strict_each_R_residue')]
    assert len(correct) == 4484 and sum(r['weight'] for r in correct) == 4491
    assert len(strict) == 4479 and sum(r['weight'] for r in strict) == 4486
    assert sum(r['syntax']['R1_all'] for r in scope) == 471
    assert sum(r['syntax']['R1_all'] for r in bounded) == 469
    reconciled = load('coverage_reconciliation.json')
    assert reconciled['Q1_remaining_unknown']['families'] == 68
    assert len(reconciled['Q1_remaining_unknown']['keys']) == 68
    direct = load('coverage_direct.json')
    assert direct['exception_families'] == 9 and direct['nonexception_families'] == 20
    assert direct['exact_Q_states_checked'] == 919
    assert direct['candidate_readings_checked'] == 1996
    assert direct['all_exception_W_no_bond_through_p_x']
    assert direct['all_nine_have_other_bonds_at_most_three']
    q3 = load('q3_results.json')
    assert len(q3['rows']) == 12
    assert all(r['minimum'] == 2 and r['global_exact'] for r in q3['rows'])
    hand = load('growth_hand_read_exception_results.json')
    assert len(hand['rows']) == 12
    assert all(r['minimum'] == r['absolute_depth']+2 and r['global_exact']
               and r['S_call_length'] == r['absolute_depth']-1 for r in hand['rows'])
    assert all(r['explicit_chain_witness_check']['is_bond'] for r in hand['rows'])
    simple = [json.loads(line) for line in (HERE/'growth_deeper_simple.jsonl').read_text().splitlines()]
    unresolved = [json.loads(line) for line in (HERE/'growth_unresolved_prefix.jsonl').read_text().splitlines()]
    assert Counter(r['status'] for r in simple) == {'exact_global': 10, 'timeout': 6}
    assert Counter(r['status'] for r in unresolved) == {'exact_global': 1, 'exact_prefix': 19}
    pumping = load('pumping_results.json')
    assert len(pumping['samples']) == 11 and all(s['complete'] for s in pumping['samples'])
    assert pumping['census_identity_arguments']['families'] == 5964
    assert pumping['census_identity_arguments']['repeated_argument_calls'] == 0
    assert pumping['script_sha256'] == digest(HERE/'pumping_audit.py')
    return dict(census_rows=5964, bounded_families=5067, bounded_draw_weight=5129,
                R_correct_families=4484, R_correct_draw_weight=4491,
                R_correct_weight_percent=100*4491/5129,
                R_strict_families=4479, R_strict_draw_weight=4486,
                R1_scope_families=471, R1_bounded_families=469,
                exception_direct_states=919, candidate_direct_checks=1996,
                q3_exact_global_cells=12, fresh_converse_exact_global_cells=12,
                deeper_simple_global_cells=10, deeper_simple_retained_timeouts=6,
                unresolved_global_cells=1, unresolved_prefix_only_cells=19,
                exact_monoids=11)


def main():
    started = time.monotonic()
    parsed = {}
    for path in sorted(HERE.iterdir()):
        if path.name in PREEXISTING or path.name == 'referee_manifest.json':
            continue
        if path.suffix == '.py':
            ast.parse(path.read_text(), filename=path.name)
            parsed[path.name] = 'AST parses'
        elif path.suffix == '.json':
            json.loads(path.read_text())
            parsed[path.name] = 'JSON parses'
        elif path.suffix == '.jsonl':
            count = 0
            with path.open() as source:
                for line in source:
                    if line.strip():
                        json.loads(line)
                        count += 1
            parsed[path.name] = {'JSONL_rows': count}
    links = []
    for target in re.findall(r'\]\(([^)]+)\)', (HERE/'codex_report.md').read_text()):
        if '://' not in target:
            assert (HERE/target).exists(), target
            links.append(target)
    output = dict(all_checks_passed=True, script_sha256=digest(Path(__file__)),
                  chain_relation_checks=chain_checks(), reconciled_counts=counts(),
                  coverage_bound_hashes=ledger_hashes('coverage_manifest.json', ['files_sha256']),
                  growth_bound_hashes=ledger_hashes('growth_manifest.json',
                      ['own_code_sha256', 'q3_code_sha256', 'sources', 'context_sources_sha256']),
                  parsed=parsed, report_local_links_checked=links,
                  independence='same-task independent code plus mathematical review; no external replication',
                  scientific_status='audit only; no lifecycle or published record modified',
                  no_network=True, python=sys.executable,
                  seconds=round(time.monotonic()-started, 3),
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (HERE/'referee_validation.json').write_text(json.dumps(output, indent=2)+'\n')
    files = {str(path.relative_to(ROOT)): digest(path) for path in sorted(HERE.iterdir())
             if path.is_file() and path.name not in PREEXISTING | {'referee_manifest.json'}}
    manifest = dict(scope_kind='epic', scope_id='READ-RULE-20261114-001',
                    role='independent referee audit, no lifecycle ownership changes',
                    verdict='Confirmed with fixes',
                    files_written_sha256=files,
                    preexisting_files_preserved=sorted(PREEXISTING),
                    source_of_scientific_claims=['explicit proof repair', 'fresh exact local enumeration',
                                                'fresh READ code with authorised earlier referee SAT reuse',
                                                'new wrapper counterexample with uniform pendant proof'],
                    comparison_literature_status='from memory, unverified; no network',
                    final_check='referee_validation.json')
    (HERE/'referee_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(all_checks_passed=True, owned_files=len(files)+1,
                         chain_depths_checked=12, seconds=output['seconds'],
                         peak_rss_kib=output['peak_rss_kib'])))


if __name__ == '__main__':
    main()
