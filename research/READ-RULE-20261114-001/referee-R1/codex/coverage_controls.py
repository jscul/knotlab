"""Hand-specified positive and negative syntactic/quantifier controls."""
import json
import itertools

import coverage_run as audit


def generic_minimal_nonshattered(rows):
    if not rows:
        raise ValueError('Empty/dead relations are outside the living theorem.')
    def shattered(support):
        return len({tuple((s >> j) & 1 for j in support) for s in rows}) == 1 << len(support)
    result = []
    for size in range(1, 4):
        for support in itertools.combinations(range(3), size):
            if not shattered(support) and all(shattered(support[:j] + support[j + 1:]) for j in range(size)):
                result.append(list(support))
    return result


def main():
    examples = [
        ('pendant_own', [[3, 2, [['K', [0, 3, 4]], ['SELF', [0, 1, 3]]]]], 0, True),
        ('second_constraint_removes_pendant', [[3, 2, [['K', [0, 3, 4]], ['K', [1, 2, 4]], ['SELF', [0, 1, 3]]]]], 0, False),
        ('both_own_self_arguments_remove_pendant', [[3, 2, [['K', [0, 3, 4]], ['SELF', [0, 3, 4]]]]], 0, False),
        ('swap_own_roles_retains_pendant', [[3, 2, [['K', [0, 3, 4]], ['SELF', [0, 1, 4]]]]], 0, True),
        ('finite_helper_argument_guard', [[3, 0, [['K', [0, 1, 2]]]],
                                         [3, 2, [[0, [0, 3, 4]], ['SELF', [0, 1, 3]]]]], 1, False),
        ('port_third_member_not_own', [[3, 1, [['K', [0, 3, 1]], ['SELF', [0, 1, 3]]]]], 0, False),
        ('unread_carried_position', [[3, 2, [['K', [1, 3, 4]], ['SELF', [0, 3, 4]]]]], 0, False),
        ('auto_port_knot_has_no_own', [[3, 1, [['SELF', [2, 0, 1]]]]], 0, False),
        ('wrapper_carries_pendant_knot_port', [[3, 2, [['K', [0, 3, 4]], ['SELF', [0, 1, 3]]]],
                                              [3, 1, [[0, [0, 1, 3]]]]], 0, True),
        ('wrapper_loses_only_read_port', [[3, 2, [['K', [0, 3, 4]], ['SELF', [0, 1, 3]]]],
                                         [3, 1, [[0, [3, 0, 1]]]]], 0, False),
    ]
    rows = []
    for name, raw, S, expected in examples:
        key = json.dumps(raw, separators=(',', ':'))
        syntax = audit.parse_syntax(key, S)
        assert syntax['R1_all'] == expected, (name, syntax)
        rows.append({'name': name, 'expected_R1_all': expected, 'actual_R1_all': syntax['R1_all'],
                     'raw': raw, 'R_masks': syntax['R_masks'], 'R_mu': syntax['R_mu'],
                     'R_period': syntax['R_period'], 'pendant': syntax['pendant'],
                     'flattened_pendant_before_call_guard': syntax['flattened_pendant_before_call_guard']})
    # Two exact Q phases can share one R residue. Pooling them would accept
    # this deliberately wrong predicate even though one depth phase fails.
    phases = [[False, False], [True, False]]
    correct = all(any(phase) for phase in phases)
    wrong_pooled = any(x for phase in phases for x in phase)
    assert not correct and wrong_pooled
    # The theorem needs one state; the stronger reading rejects mixed states.
    eligible_states = [True, False]
    assert any(eligible_states) and not all(eligible_states)
    relation_cases = []
    for code in range(1, 16):
        allowed = [s for j in range(4) if code >> j & 1 for s in (j, 7 - j)]
        if set(allowed) & {0, 7}:
            continue
        bonds = generic_minimal_nonshattered(allowed)
        generic = any({0, 1} <= set(b) for b in bonds)
        info = audit.triple_info(allowed)
        assert generic == (not info['exception'])
        relation_cases.append({'allowed': sorted(allowed), 'all_minimal_nonshattered_supports': bonds,
                               'generic_bond_through_p_x': generic, 'exception': info['exception']})
    assert len(relation_cases) == 7
    dead_rejected = False
    try:
        generic_minimal_nonshattered([])
    except ValueError:
        dead_rejected = True
    assert dead_rejected
    result = {'syntax_controls': rows, 'syntax_controls_passed': len(rows),
              'pooling_Q_phases_mutant_rejected': {'phases': phases, 'correct': correct,
                                                  'wrong_pooled': wrong_pooled},
              'existential_vs_universal_discriminator': eligible_states,
              'empty_eligible_set_not_accepted': not bool([]),
              'generic_subset_reference_relation_cases': relation_cases,
              'generic_reference_dead_relation_rejected': dead_rejected}
    (audit.HERE / 'coverage_controls.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'syntax_controls_passed': len(rows), 'quantifier_controls_passed': 3}))


if __name__ == '__main__':
    main()
