"""Reconcile preserved relation-free runs without rerunning their searches."""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    inputs=json.loads((HERE/'middle_inputs.json').read_text())
    records=[r for p in sorted(HERE.glob('middle_panel*.jsonl')) for r in rows(p)]
    records+=rows(HERE/'middle_remaining_small.jsonl')
    by_cell={(r['case'],r['depth']):r for r in records}
    assert len(by_cell)==len(records)
    assert len({r['case'] for r in records})==65
    retry=rows(HERE/'middle_remaining.jsonl')
    disagreements=[]
    for r in retry:
        old=by_cell[(r['case'],r['depth'])]
        if r.get('minimum') is not None and old.get('minimum') is not None:
            assert r['minimum']==old['minimum']
        if r['status']!=old['status']:
            disagreements.append({'case':r['case'],'depth':r['depth'],
                                  'first_status':old['status'],'retry_status':r['status']})
    for r in records:
        if r.get('witness'):
            assert r['verification']['is_bond']
            assert r['verification']['every_single_deletion_full']
            assert r['verification']['living']
            assert len(r['witness'])==r['minimum']
            if r['minimum']==3:
                assert any(x['size']==2 and x['exhausted'] for x in r['by_size'])
                assert r['global_minimum']==3
            elif r['minimum']>=4:
                assert r['global_minimum'] is None
        if r.get('endpoint_only_bond'):
            assert r['endpoint_only_verification']['is_bond']
            assert any(x['endpoint_allocations_only'] for x in r['endpoint_only_locations'])
    missing=[{'case':i,'sha':inputs[i]['key_sha256'][:12],'depth':d,
              'reason':'same hard cell interrupted twice' if i==62 else 'deep cell not started after resource reassessment'}
             for i in range(65) for d in (3,4,6) if (i,d) not in by_cell]
    representatives=[]
    for i in (0,3,18,29,30,44,57):
        cells=[]
        for d in (3,4,6):
            r=by_cell[(i,d)]
            cells.append({k:r.get(k) for k in ('depth','minimum','global_minimum','witness',
                    'allocation_locations','endpoint_only_bond','endpoint_only_locations','status')})
        representatives.append({'case':i,'sha':inputs[i]['key_sha256'][:12],
                                'stratum':inputs[i]['stratum'],'cells':cells})
    wordrows=rows(HERE/'middle_word_results.jsonl')
    assert all(r['bond']['verification']['is_bond'] for r in wordrows)
    joined=[{'case':r['case'],'depth':r['depth'],'prefix_minimum':len(r['endpoint_only_bond']),
             'witness':r['endpoint_only_bond']} for r in records
            if r.get('minimum') is None and r.get('endpoint_only_bond') and
               r.get('proved_lower_bound')==len(r['endpoint_only_bond'])]
    result={
        'population_label':'65 known residual families; not a proved mechanism class',
        'families':65,'completed_record_cells':len(records),
        'configured_depths':[3,4,6],
        'status':dict(collections.Counter(r['status'] for r in records)),
        'minima':dict(collections.Counter(str(r.get('minimum')) for r in records)),
        'global_exact_size_three_cells':sum(r.get('global_minimum')==3 for r in records),
        'finite_prefix_exact_size_four_cells':sum(r.get('minimum')==4 for r in records),
        'additional_prefix_minima_from_completed_lower_exclusion_and_alternative_witness':joined,
        'side_members_in_chosen_primary_witnesses':sum(any(x['side_members'] for x in r.get('allocation_locations',[])) for r in records),
        'root_target_allocation_only_alternative_cells':sum(bool(r.get('endpoint_only_bond')) for r in records),
        'missing_cells':missing,'retry_records':len(retry),'retry_status_differences':disagreements,
        'representatives':representatives,
        'large_depth_selected_word_checks':len(wordrows),
        'large_depth_selected_word_depths':sorted({r['depth'] for r in wordrows}),
        'large_depth_role':'positive bonds and least-through-specified-copy when size3; not an exhaustive word search',
        'total_search_cell_seconds':sum(r.get('seconds',0) or 0 for r in records+retry),
        'peak_search_rss_kib':max(r.get('peak_rss_kib',0) for r in records+retry),
        'scope':'full-prefix member search, exact infinite-state projection by usual-limit boundaries; positive3 plus all endpoint pairs are globally exact,4 remains finite-prefix exact only',
        'inputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('middle_*.jsonl'))}}
    (HERE/'middle_summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    lines=['# Relation-free bond locations', '',
       '**Verdict: the residual 65 are not a proved middle-member mechanism.**', '',
       'All 65 families were included in the small-depth panel. The SAT search uses the',
       'permitted earlier referee code, exact usual-limit boundaries and no per-call',
       'transfer relations or study TOP Python. Fresh code records allocating copies,',
       'including side-subtree addresses, and rechecks every positive support with',
       'MiniSat22, separately from the search backend.', '',
       f"The primary files contain {len(records)} cells: {result['status']}. There are",
       f"{result['global_exact_size_three_cells']} globally exact size-three minima and",
       f"{result['finite_prefix_exact_size_four_cells']} exact finite-prefix size-four minima.",
       f"Another {len(joined)} size-four prefix minimum follows by joining a completed",
       'size-three exclusion with a separately verified endpoint-only size-four bond.',
       'A size-three witness is globally least because every possible main-port/target-own',
       'pair has already been exhausted, and a two-member support has no auxiliary',
       'member that could hide outside the prefix. A size-four prefix minimum has no',
       'such closure; an unsearched distant third member could in principle lower it.', '',
       '| Family | Stratum | L(3), L(4), L(6) | Allocation depths in chosen depth-6 bond |',
       '| --- | --- | --- | --- |']
    for x in representatives:
        vals=', '.join(str(r['minimum'])+('*' if r['minimum'] and r['minimum']>=4 else '') for r in x['cells'])
        loc=x['cells'][-1]['allocation_locations'][0]['members']
        alloc=[r['allocation_depth'] for r in loc]
        lines.append(f"| `{x['sha']}` | {x['stratum']} | {vals} | {alloc} |")
    lines += ['', '* means a finite-prefix minimum, not a global minimum proof.', '',
       'Every row stores its actual IDs, allocating depth, address, signed difference',
       'from the target level, and side-subtree attachment/descent if applicable.',
       'The chosen primary witnesses have no side allocations; that is a property of',
       'the returned witnesses, not an exclusion theorem for other least bonds.', '',
       '**Block for the claimed necessity of middle members.** Independent word CNF',
       'checks at depths 8,9,10,11,12,13,20,50 found root/target-allocation-only bonds',
       'in `fea4933ecaf1`, `fd60333c5872`, and `5ceea39607cb`. The independent',
       '`pinning_window_results_toponly.json` supplies complete eventual finite-Q',
       'certificates (rather than extrapolating the finite word roster). In particular',
       '`fea4933ecaf1` has eventual global least value 3 and allocations [0,0,s].', '',
       '**Narrowing of what was tested.** The named numerical localisation window',
       'depends on C and m!. Interior members at these tiny depths do not refute it.',
       'The synthetic example in `localisation_audit.md` instead gives a genuinely',
       'nonlocal least bond beyond its explicit threshold and also a local least bond.', '',
       '**Preserved limits.** Case 62 at depth 6 was interrupted in two owned runs',
       'after its solver overran a soft cell timeout; no result is inferred. The',
       'completed rows survive. Remaining small cases used limited Glucose; an',
       'interrupted call raises SearchTimeout, never an UNSAT verdict. Two high-branching',
       'depth-6 cells were skipped by the predeclared copy-count estimate; two final',
       'deep cells were not started. Other soft timeouts remain explicit in the JSON.',
       'No interrupted/capped/missing cell is used as mathematical negative evidence.', '',
       'See `middle_summary.json` for exact counts, all missing cells, retries, timing',
       'and hashes; `middle_bonds_soft_timeout.py` preserves the byte-identical earlier',
       'producer version for the first primary files. The code remains within the',
       'requested referee directory; no network, Git mutation or publication was used.', '']
    (HERE/'middle_audit.md').write_text('\n'.join(lines))
    print(json.dumps({k:result[k] for k in ('families','completed_record_cells','status','minima',
        'global_exact_size_three_cells','finite_prefix_exact_size_four_cells','missing_cells',
        'peak_search_rss_kib','total_search_cell_seconds')},indent=2))


if __name__=='__main__':
    main()
