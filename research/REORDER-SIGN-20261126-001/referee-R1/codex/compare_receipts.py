"""Compare saved outputs after the independent computations. No study imports."""

import json
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]
ARTIFACT = STUDY.parents[1] / 'artifacts' / STUDY.name / (STUDY.name + '-E001_reorder_signs')
SCORED = ('000', '110', '101', '011')


def read(path):
    return json.loads(path.read_text())


def compare_listing_and_block(saved, listings, block):
    for row, other in zip(saved['P1_reversal_lemma'], listings['reversal']):
        assert row['n'] == other['n']
        assert row['full_contradiction'] == bool(other['noncharacter_witness'])
        assert row['reversal_sign_is_quarter_turn_per_occupied'] and row['identity']
    for row, other in zip(saved['P2_knot_census'], listings['permutation_census']):
        assert (row['orders'], row['orders_with_full_contradiction'], row['nonvanishing_polar_form_orders']) == (
            other['orders_checked'], other['full_contradictions'], other['orders_with_nonzero_polar_form'])
        assert row['equals_prefix_suffix_reversals'] and row['parity_predicts_exactly'] == (row['n'] == 3)
    phase_map = block['reference_then_commit_to_phase']
    for order, row in saved['P3_ternary_experiment_reference_production'].items():
        other = block['readout_by_phase'][phase_map['abc'][order]]
        assert row['correlations_ZZZ_XXZ_XZX_ZXX'] == [other['full_correlations'][s] for s in SCORED]
        assert row['product_P'] == other['product_even_correlations']
        assert row['target']['exact_cells'] == other['fixed_label_exact_cells']
        assert row['target']['matches_up_to_relabelling'] == bool(other['target_matching_x_outcome_relabels'])
        assert row['win_rate_on_scored_settings'] == other['fixed_label_win']
        assert row['old_distinction_alone_win_rate'] == block['controls']['old_only_every_reference_and_order']['fixed_label_win']
        positive = block['controls']['swap_plus_one_every_baseline_order']
        assert saved['P3_ternary_control_s_plus_one'][order] == {
            'win_rate': positive['fixed_label_win'], 'full_contradiction': positive['full_contradiction']}
    for ref, phase_by_commit in phase_map.items():
        summary = saved['P3_ternary_reference_variation']['reference_' + ref]
        assert summary['these_are_the_orders_odd_relative_to_the_reference']
        assert summary['orders_with_full_contradiction'] == sum(
            block['readout_by_phase'][phase]['full_contradiction'] for phase in phase_by_commit.values())
    for name, other in block['equal_mixtures_with_order_unavailable'].items():
        row = saved['P4_order_blind'][name]
        assert row['average_ZZZ_XXZ_XZX_ZXX'] == [other['full_correlations'][s] for s in SCORED]
        assert row['best_mermin_score'] == other['best_mermin_with_fixed_z_and_x_operators']
    survivors = saved['P5_coherent_sum']['single_ternary']
    for name, kind in [('equal_weight', 'uniform'), ('sign_weight', 'sign_of_order')]:
        assert survivors['R2_surviving_words_' + name] == block['coherent_order_sums'][kind]['parent_word_count']


def compare_fermionic(saved, fock, prototype, block):
    target = [[Fraction(v) for v in block['target'][format(s, '03b')]] for s in range(8)]
    idx = fock['full_local_case_index']
    p7 = prototype['P7_rule_applied_to_readings']
    comparisons = 0
    p7_ids = set()
    for key, group in saved.items():
        parent_key, flip = key.split('/')
        parents = parent_key.removeprefix('parents_created_').replace('_', '')
        flip_index = idx['flip_axis'].index(flip[-1] * 3)
        all_correlations = []
        for order, row in group['orders'].items():
            # First pair and record choices are respectively yz at every child and y at every reader.
            assert idx['pair_order_axis'][0] == ['yz'] * 3 and idx['record_axis'][0] == 'yyy'
            table_id = idx['table_ids'][parents + '/' + order][flip_index]
            receipt = fock['probability_tables'][str(table_id)]
            table = [[Fraction(v, receipt['denominator']) for v in nums] for nums in receipt['numerators']]
            corr = [sum(v * (-1) ** o.bit_count() for o, v in enumerate(table[int(s, 2)])) for s in SCORED]
            all_correlations.append(corr)
            fixed_win = Fraction(1, 2) + (corr[0] - sum(corr[1:])) / 8
            assert corr == row['ZZZ_XXZ_XZX_ZXX'] and prod(corr) == row['product_P']
            assert row['full_contradiction'] == (prod(corr) == -1)
            assert fixed_win == row['scored_win_fixed_labels']
            if flip == 'F1':
                assert (table == target) == (parents == order)
            else:
                assert table != target
            if parents == 'abc' and flip == 'F1':
                p7_ids.add(table_id)
                p7_row = p7['per_order'][order]
                assert Fraction(p7_row['win_rate']) == fixed_win
                assert p7_row['target']['exact_cells'] == sum(
                    a == b for rr, tt in zip(table, target) for a, b in zip(rr, tt))
                assert p7_row['target']['matches_up_to_relabelling'] == (prod(corr) == -1)
            comparisons += 1
        base, ab, ac, bc = [sum(column) / len(all_correlations) for column in zip(*all_correlations)]
        best = max(abs(base - a*b*ab - a*c*ac - b*c*bc) for a, b, c in product((1, -1), repeat=3))
        assert round(float(best), 12) == group['order_blind_best_mermin_score']
        assert group['coherent_sum_old_words_present'] == ['000']
        surviving = block['coherent_order_sums']['uniform']['nine_bit_word_count']
        assert group['coherent_sum_norm_squared_over_36'] == Fraction(surviving, block['grown_word_count'])
    assert len(p7_ids) == p7['distinct_tables_across_orders'] == 6
    return comparisons


if __name__ == '__main__':
    prototype = read(ARTIFACT / 'results.json')
    block = read(HERE / 'block.json')
    compare_listing_and_block(prototype, read(HERE / 'listings.json'), block)
    count = compare_fermionic(read(STUDY / 'verify_fock.json'), read(HERE / 'fock.json'), prototype, block)
    print(f'Agreed on the listing and ternary summaries, the six frozen P7 outcomes, and all {count} archived Fock rows.')
