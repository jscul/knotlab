"""Focused checks of the sealed prediction, replay accounting and six-rule discriminators."""

from argparse import ArgumentParser
from fractions import Fraction
from gzip import open as gzip_open
from hashlib import sha256
from json import loads
from pathlib import Path


def load(path):
    if path.suffix == '.gz':
        with gzip_open(path, 'rt') as file:
            return loads(file.read())
    return loads(path.read_text())


def mass(table):
    return sum(Fraction(p) for kind in ('ordinary_cells','left_failure_row','right_failure_column')
               for p in table[kind])


def check(folder):
    pred_path = folder / 'prospective.json'
    receipt = load(folder / 'prediction_receipt.json')
    assert sha256(pred_path.read_bytes()).hexdigest() == receipt['prediction_sha256']
    pred = load(pred_path)['catalogues']
    comparison = load(folder / 'archive_comparison.json')
    assert comparison['prediction_sha256'] == receipt['prediction_sha256']
    assert comparison['compared_at_host_utc'] > receipt['recorded_at_host_utc']
    for rows in comparison['comparisons'].values():
        assert sum(x['compared_cells'] for x in rows.values()) == 576
        assert sum(x['equal_zero_cells'] for x in rows.values()) == 504
    computed = load(folder / 'results.json.gz')
    assert computed['frozen_design_sha256'] == receipt['frozen_design_sha256']
    assert computed['sequential_replay_source_sha256']['predict.py'] == receipt['independent_producer_sha256']
    catalogues = computed['catalogues']
    assert set(catalogues) == set(pred)
    initial_count, fixed_count, tag_count = 0, 0, 0
    for key, value in catalogues.items():
        hold_n = len(value['holdings'])
        setting_n = len(value['independent_settings'][0]) * len(value['independent_settings'][1])
        models = value['models']
        assert models['relaxed']['compiler']['minimum_reversal_masks'] == [[]]
        assert models['relaxed']['compiler'] == models['coherent']['compiler']
        for name, data in models.items():
            if name == 'relaxed':
                continue
            assert len(data['single_reader']) == 2 * hold_n**2
            assert len(data['fixed_histories']['conditions']) == (len(value['independent_settings'][0])+1)**2 * (
                                                                   len(value['independent_settings'][1])+1)**2
            assert len(data['unilateral']) == 2 * setting_n
            fixed_count += len(data['fixed_histories']['conditions'])
            ready = Fraction(data['source_acceptance'])
            for pair, tables in data['fresh'].items():
                assert mass(tables['launch']) == 1
                assert Fraction(tables['launch']['left_failure_row'][-1]) == 1 - ready
                if ready:
                    assert mass(tables['conditional']) == 1
                else:
                    assert tables['conditional'] is None
                if name in pred[key]['tables']:
                    expected = pred[key]['tables'][name][pair]
                    assert all(tables[a]['ordinary_cells'] == expected[a] for a in ('conditional','launch'))
                    initial_count += len(expected['conditional']) + len(expected['launch'])
            for view in data['unilateral']:
                assert view['launch']['far_marginal_tv'] == '0'
                assert all(view['launch'][flag] == 0 for flag in ('far_idle_new_address','far_idle_fired_pairs',
                                                                'far_idle_additional_clock_events','far_idle_new_latch_writes'))
        tag = value['mechanism_checks']['coherence_and_marks']
        tag_count += tag['explicitly_checked_amplitude_cells']
        assert set(tag['maximum_fresh_complete_local_tv_by_side']) == {
            'left','right','both','left_ignored','right_ignored','both_ignored','uncomputed'}
        assert all(row == ['0','0'] for row in tag['maximum_fresh_complete_local_tv_by_side'].values())

    signed = catalogues['signed']
    checks = signed['mechanism_checks']
    models = signed['models']
    assert len(models['coherent']['fresh']) == 9
    assert models['coherent']['compiler']['local_flips'] == {
        '0':[], '1':[], '2':[], '3':[1,2,7,8], '4':[0,2,6,8], '5':[0,1,6,7],
        '6':[1,2,7,8], '7':[0,2,6,8], '8':[0,1,6,7]}
    for k,score in (('coherent','1'), ('dephased','2/3'), ('independent','1/2'), ('literal','1'), ('erasure','0')):
        assert sum(Fraction(x['events']['mass']['recorded_score']) for x in models[k]['fresh'].values()) / 9 == Fraction(score)
    for k,mismatch,tv in (('coherent','3','0'), ('literal','0','1/2'), ('literal_biased','0','7/12')):
        for s in models[k]['held_reader_sweep']:
            assert s['sum_expected_mismatches'] == mismatch
            assert all(c['max_tv'] == tv for c in s['reference_checks'].values())
            assert all(c['assembled_violation_or_A_bad'] == '1' for c in s['reference_checks'].values())
    for k, delta in (('coherent','0'), ('literal','1/4'), ('literal_biased','1/3')):
        assert all(x['far_adaptive']['full_tv'] == delta for x in models[k]['adaptive_histories'])
    for pair in models['coherent']['unilateral']:
        for cond in pair['launch']['conditions']:
            assert set(b['bit_guess_if_far_read'] for b in cond['conditional_shared_bits'].values()) == {'1'}
            assert cond['best_whole_word_if_far_read'] == '1/2'
            assert len(cond['far_word_support']) == 2
    fail = checks['writer_failures']
    assert fail['not_ready']['changes']['change_given_both'] == '0'
    assert fail['disconnected']['changes']['change_given_both'] == '1/2'
    assert not checks['recodings']['physically_recompiled_is_transport']
    assert all(p['recompiled_tv'] == '0' for p in checks['recodings']['by_pair'].values())
    assert catalogues['nae']['models']['coherent']['source_acceptance'] == '51/256'
    assert catalogues['small_nae']['models']['coherent']['source_acceptance'] == '9/16'
    print(f'Verified {initial_count} prospective launch/conditional cells, {fixed_count} fixed two-slot conditions, '
          f'{tag_count} independent tagged/untagged amplitude cells and the scientific discriminators.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('artifact_directory', type=Path)
    check(parser.parse_args().artifact_directory)
