"""Reconcile only referee outputs; no study implementation or batch is accessed."""
from collections import Counter
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


def subset_result(rows):
    q = list(rows)
    answer = dict(count=len(q), indices=[r['idx'] for r in q],
                  eventual_bounded_counts=dict(Counter(str(r['exact_eventual_boundedness']['eventually_bounded']) for r in q)))
    positive = [r for r in q if r['exact_eventual_boundedness']['eventually_bounded'] is True]
    if positive:
        answer.update(
            largest_depth_threshold=max(r['exact_eventual_boundedness']['depth_threshold'] for r in positive),
            largest_uniform_cost_bound=max(r['exact_eventual_boundedness']['uniform_cost_bound'] for r in positive),
            period_counts=dict(Counter(r['exact_eventual_boundedness']['period'] for r in positive)),
            cost_bound_counts=dict(Counter(r['exact_eventual_boundedness']['uniform_cost_bound'] for r in positive)),
        )
        prefix_verified = []
        for r in positive:
            onset = r['exact_eventual_boundedness']['depth_threshold']
            prefix = r['L_recomputed'][:onset - 1]
            if len(prefix) == onset - 1 and all(x < 10 ** 9 for x in prefix):
                prefix_verified.append(r['idx'])
        answer['finite_early_prefix_verified_indices'] = prefix_verified
        answer['all_depths_finitely_bounded_count_after_prefix_check'] = len(prefix_verified)
    return answer


def main():
    rows = [json.loads(x) for x in (HERE / 'recomputed.jsonl').read_text().splitlines()]
    selection = load('sample_selection.json')
    controls = load('controls.json')
    history = load('history_audit.json')
    assert len(rows) == len({r['idx'] for r in rows})
    assert {r['idx'] for r in rows} == set(selection['selected'])
    assert all(r['status'] == 'done' and r['complete'] for r in rows)
    assert all(not r['field_disagreements'] for r in rows)
    assert all(r['gate_ok'] is not False for r in rows)
    assert all(r['gate_ok'] is not None or r['record_depths'] == 0 for r in rows)
    assert not controls['cycle_disagreements'] and not controls['block_disagreements']
    assert not history['summary_recalculation']['top_level_differences']
    assert not history['summary_recalculation']['nested_counter_differences']
    assert not history['row_issues']
    flat = [r for r in rows if r['record_class'] == 'flat' and r['zero_mean'] and not r['bounded_all']]
    others = [r for r in rows if r['record_class'] != 'flat' and r['zero_mean'] and not r['bounded_all']]
    extra = [r for r in flat + others if r['exact_eventual_boundedness']['eventually_bounded'] is True]
    fields = sorted(rows[0]['field_comparisons'])
    summary = dict(
        verdict='Confirmed with fixes',
        scope_kind='epic', scope_id='PROVED-RATE-20261113-001', referee='referee-R1',
        expected_sample=selection['unique_count'], independently_recomputed=len(rows),
        graph_nodes_total=sum(r['nodes'] for r in rows),
        graph_nodes_range=[min(r['nodes'] for r in rows), max(r['nodes'] for r in rows)],
        graph_edges_total=sum(r['edges'] for r in rows),
        compared_fields=fields, compared_fields_count=len(fields),
        compared_cells=len(fields) * len(rows), field_disagreements=[],
        recorded_depth_gate_values=sum(len(r['L_recomputed']) for r in rows),
        gate_checked_families=sum(r['gate_ok'] is True for r in rows),
        gate_unchecked_no_prior_L=[r['idx'] for r in rows if r['gate_ok'] is None],
        gate_mismatches=[], resource_failures=[],
        rate_distribution=dict(Counter(str(r['lambda']) for r in rows)),
        all_46_flat=subset_result(flat), other_zero_only_sample=subset_result(others),
        all_sample=subset_result(rows),
        strengthened_complete_boundedness_lower_count=(
            history['summary_recalculation']['all_complete']['bounded_all'] + len(extra)),
        strengthened_count_qualification='305 submitted sufficient-test positives plus 56 newly certified disjoint cases; not a full independent rerun of 655 graphs',
        remaining_complete_zero_only_unassessed=(
            history['summary_recalculation']['overall']['zero_mean_without_bounded_all'] - len(extra)),
        synthetic_simple_cycle_comparisons=controls['cycle_cases'],
        direct_set_semantic_comparisons=controls['block_cases'],
        runtime=dict(
            python=sys.version, invocation='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/jscul/p-vs-np-contact-first/.venv/bin/python -B',
            compute_processes_per_command=1, configured_address_space_bytes=7 * 1024 ** 3,
            family_wall_limit_seconds=540, node_cap=2_000_000,
            sum_family_seconds=sum(r['seconds'] for r in rows),
            largest_family_seconds=max(r['seconds'] for r in rows),
            peak_rss_kib=max(r['peak_rss_kib'] for r in rows),
            controls_seconds=controls['seconds'],
        ),
        validation_independence='V2 fresh DP and graph reconstruction, same-task AI review and independent small controls; not external or human replication',
        forbidden_producer_code_accessed=False,
        batch_history_independently_verified=False,
    )
    for source in sorted(HERE.glob('*.py')):
        ast.parse(source.read_text(), filename=str(source))
    frozen_hash = selection['input_sha256'][str((HERE / 'recompute.py').relative_to(HERE.parents[3]))]
    assert hashlib.sha256((HERE / 'recompute.py').read_bytes()).hexdigest() == frozen_hash
    path = HERE / 'referee_summary.json'
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    # Compact console output only; the complete per-family evidence stays in files.
    print(json.dumps({k: summary[k] for k in ('independently_recomputed', 'compared_cells', 'recorded_depth_gate_values',
                                             'strengthened_complete_boundedness_lower_count', 'remaining_complete_zero_only_unassessed', 'runtime')}, indent=2))


if __name__ == '__main__':
    main()
