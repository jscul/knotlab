"""Reconcile exact Q1/R/R1 quantifiers and verify each rescued/exception phase."""
import json
import time

import coverage_run as audit
import coverage_direct as direct


def main():
    start = time.monotonic()
    rows = [json.loads(line) for line in (audit.HERE / 'coverage_results.jsonl').open()]
    bykey = {r['key']: r for r in rows}
    digest = {r['key']: r for r in audit.gzrows(audit.DIGEST)}
    study = {r['key']: r for r in audit.read_json(audit.DATA / 'results.json')['families']}
    inside = [r for r in rows if r['in_scope']]
    rescued = [r for r in inside if r['R'] and r['R']['exists_good_each_Q_residue']
               and not r['R']['strict_each_R_residue']]
    extra_r1 = [r for r in inside if r['syntax']['R1_all'] and r['verdict'] != 'bounded']
    exceptions = [r for r in inside if r['R'] and r['R']['some_exception_only_Q_residue']]
    old_ambiguous = [r for r in study.values() if r['in_scope'] and r['R']['window_complete']
                     and r['R']['q1_exception_only'] is None]
    assert {r['key'] for r in old_ambiguous} == {r['key'] for r in rescued}
    unknown = [r for r in inside if r['R'] is None and r['syntax']['candidates']]
    no_candidate_incomplete = [r for r in inside if r['R'] is None and not r['syntax']['candidates']]
    assert (len(rescued), len(extra_r1), len(exceptions), len(unknown), len(no_candidate_incomplete)) == (5, 2, 9, 68, 4)

    def original(rec):
        d = digest[rec['key']]
        result = {k: d[k] for k in ('key_sha256', 'key', 'weight', 'in_scope', 'wrapper', 'stratum',
                                   'verdict', 'caps', 'window_complete', 'window_verdict', 'preperiod', 'period', 'U_by_s')}
        result['R1_all'] = rec['syntax']['R1_all']
        if rec['R']:
            result.update({k: rec['R'][k] for k in ('exists_good_each_Q_residue', 'strict_each_R_residue',
                                                   'some_exception_only_Q_residue')})
        return result

    phase_checks = []
    for rec in exceptions + rescued:
        key = rec['key']
        w = audit.window.Window(json.loads(key), rec['S'])
        levels, mu, period = audit.q_orbit(w, digest[key]['preperiod'], digest[key]['period'])
        for phase in rec['R']['residues']:
            s = phase['s']
            index = s if s < len(levels) else mu + (s - mu) % period
            found = None
            attempts = 0
            # Sort deterministically by an independently reconstructed state.
            for q, (entry, word) in levels[index].items():
                if rec in rescued:
                    candidates = [c for c in rec['syntax']['candidates'] if q[1][w.km + c[0]] < w.km
                                  and not audit.triple_info(audit.projected_local_rows(w, q, c))['exception']]
                    if not candidates:
                        continue
                else:
                    candidates = []
                cnf = direct.word_cnf(json.loads(key), rec['S'], entry, word)
                attempts += 1
                searched = direct.least_other_bond(cnf)
                if searched['minimum'] is None:
                    continue
                candidate_check = direct.verify_candidate(cnf, q, candidates[0], False) if candidates else None
                found = {'key_sha256': rec['key_sha256'], 'kind': 'existential_rescue' if rec in rescued else 'exception_other_bond',
                         's': s, 'Q_phase': phase['Q_phase'], 'U': phase['U'],
                         'entry': entry, 'word': list(word), 'Q': {'J': hex(q[0]), 'partition': list(q[1])},
                         'variables': cnf['n'], 'clauses': len(cnf['clauses']), 'search_attempts': attempts,
                         'direct_search': searched, 'surviving_candidate_check': candidate_check}
                break
            assert found is not None, (rec['key_sha256'], phase)
            phase_checks.append(found)
    bounded = [r for r in inside if r['verdict'] == 'bounded']
    strict = [r for r in bounded if r['R'] and r['R']['strict_each_R_residue']]
    some = [r for r in bounded if r['R'] and r['R']['exists_good_each_Q_residue']]
    r1bounded = [r for r in bounded if r['syntax']['R1_all']]
    den = sum(r['weight'] for r in bounded)
    exact = {'bounded_families': len(bounded), 'bounded_weight': den,
             'strict_R_families': len(strict), 'strict_R_weight': sum(r['weight'] for r in strict),
             'some_R_families': len(some), 'some_R_weight': sum(r['weight'] for r in some),
             'R1_bounded_families': len(r1bounded), 'R1_bounded_weight': sum(r['weight'] for r in r1bounded),
             'strict_R_percent': 100 * sum(r['weight'] for r in strict) / den,
             'some_R_percent': 100 * sum(r['weight'] for r in some) / den,
             'R1_percent': 100 * sum(r['weight'] for r in r1bounded) / den,
             'R_percent_increase_points': 100 * sum(r['weight'] for r in rescued) / den}
    assert exact['some_R_weight'] - exact['strict_R_weight'] == 5
    result = {'counts': exact, 'R1_extra_two': [original(r) for r in extra_r1],
              'existential_R_extra_five_and_resolved_Q1_ambiguities': [original(r) for r in rescued],
              'exception_only_exact_nine': [original(r) for r in exceptions],
              'Q1_remaining_unknown': {'families': len(unknown), 'weight': sum(r['weight'] for r in unknown),
                                       'keys': [r['key_sha256'] for r in unknown]},
              'incomplete_Q_no_reading_candidate_definitely_not_exception_only': [original(r) for r in no_candidate_incomplete],
              'known_not_exception_only_in_scope': len(inside) - len(exceptions) - len(unknown),
              'per_Q_phase_direct_certificates': phase_checks,
              'phase_certificates': len(phase_checks),
              'exception_other_bond_phase_certificates': sum(r['kind'] == 'exception_other_bond' for r in phase_checks),
              'rescued_surviving_phase_certificates': sum(r['kind'] == 'existential_rescue' for r in phase_checks),
              'reconstructed_complete_Q_orbits_in_scope': sum(r['R'] is not None for r in inside),
              'whole_window_projection_crosschecks': sum(r['R']['whole_window_crosschecks'] for r in inside if r['R']),
              'Q_phase_union_over_R_phase_disagreements': [r['key_sha256'] for r in inside if r['R'] and
                                                          r['R']['exists_good_each_Q_residue'] != r['R']['exists_good_each_R_residue_union']],
              'scope': 'CARRY window-stage classifications, before path-DP additions; exact recorded weights inherited from digest.',
              'validation': 'V2 independent same-task code and SAT; earlier permitted referee algorithms reused, no external replication.',
              'seconds': time.monotonic() - start}
    (audit.HERE / 'coverage_reconciliation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k in ('counts', 'phase_certificates',
                     'exception_other_bond_phase_certificates', 'rescued_surviving_phase_certificates',
                     'reconstructed_complete_Q_orbits_in_scope', 'whole_window_projection_crosschecks', 'seconds')}, indent=2))


if __name__ == '__main__':
    main()
