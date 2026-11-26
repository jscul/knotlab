"""Recount the frozen predictions against the saved growth readings."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import islice
import json
from math import comb
from pathlib import Path


STUDY = Path(__file__).resolve().parent.parent
PANELS = {
    ('uniform', 'nae'): 'held_out_nae',
    ('uniform', 'parity'): 'held_out_parity',
    ('stratified', 'nae'): 'grown_stratified_nae',
    ('stratified', 'parity'): 'grown_stratified_parity',
    ('handbuilt', 'nae'): 'grown_handbuilt_nae',
    ('handbuilt', 'parity'): 'grown_handbuilt_parity',
    ('grow7', 'nae'): 'grown_grow7_nae',
    ('grow7', 'parity'): 'grown_grow7_parity',
    ('horizon', 'nae'): 'grown_horizon_nae',
}
READINGS = ('sig0', 'sig1')
FROZEN_DIGEST = 'd6aefb73dc32220c61166efc94e568c0a6906f48a7ccf7eb508d72c1ab3f699d'


def inputs(panels, limit):
    growth = {}
    for panel, stem in panels.items():
        with gzip.open(STUDY / (stem + '.jsonl.gz'), 'rt') as stream:
            for record in map(json.loads, islice(stream, limit)):
                key = (*panel, record['index'])
                assert key not in growth, key
                growth[key] = record
    predictions = {}
    digest = sha256()
    prediction_count = 0
    with gzip.open(STUDY / 'predictions.jsonl.gz', 'rb') as stream:
        for line in stream:
            digest.update(line)
            prediction_count += 1
            record = json.loads(line)
            key = (record['set'], record['knot law'], record['index'])
            if key in growth:
                assert key not in predictions, key
                predictions[key] = record
    assert digest.hexdigest() == FROZEN_DIGEST
    assert growth.keys() == predictions.keys()
    if limit is None and panels == PANELS:
        assert len(growth) == prediction_count
    return growth, predictions


def read_rows(record):
    """Read the two multisets as typed tuples, checking their marginal counts."""
    readings = [], []
    for row in record['rows']:
        flat = Counter()
        with_parents = Counter()
        marginal = Counter()
        for (kind, parents, fresh, places), count in row['sig0']:
            key = (kind, parents, fresh, places)
            assert count > 0 and key not in flat, key
            flat[key] = count
        for (kind, parents), count in row['sig1']:
            parent_kinds = tuple(tuple(parent) for parent in parents)
            assert len(parent_kinds) == kind[1] and parent_kinds == tuple(sorted(parent_kinds))
            key = tuple(kind), parent_kinds
            assert count > 0 and key not in with_parents, key
            with_parents[key] = count
            marginal[tuple(kind)] += count
        assert flat == marginal and sum(flat.values()) == row['n'], row
        readings[0].append(flat)
        readings[1].append(with_parents)
    return readings


def first_difference(first, second, stop, closed):
    """Compare the saved rounds and, at closure, the remaining zero rounds."""
    for index in range(stop):
        if first[index] != second[index]:
            return index + 1
    if closed:
        for index in range(stop, len(second)):
            if second[index]:
                return index + 1
    return None


def differences(counts, order):
    for _ in range(order):
        counts = [high - low for low, high in zip(counts, counts[1:])]
    return counts


def dimension(counts, end, max_dimension=4):
    if end.startswith(('closes', 'stalls')):
        return end.split()[0]
    if len(counts) < 10:
        return 'unread'
    for candidate in range(1, max_dimension + 1):
        suffix = differences(counts[-8:], candidate - 1)
        if len(suffix) >= 2 and suffix[0] > 0 and len(set(suffix)) == 1:
            return f'dim {candidate}'
    ratios = [Fraction(b, a) for a, b in zip(counts[-5:], counts[-4:]) if a]
    if len(ratios) == 4 and min(ratios) > Fraction(105, 100) and max(ratios) - min(ratios) < Fraction(1, 100):
        return f'rate {float(ratios[-1]):.2f}'
    return 'unread'


def settling_cut(rows, dim):
    """Locate the last nonzero difference of order dim across all kinds."""
    floor = max(dim, 3)
    ceiling = len(rows) - 2
    if floor > ceiling:
        return None
    coeffs = [(-1) ** (dim - i) * comb(dim, i) for i in range(dim + 1)]
    for i in reversed(range(len(rows) - dim)):
        diff = Counter()
        for row, factor in zip(rows[i:i + dim + 1], coeffs):
            for kind, count in row.items():
                diff[kind] += count * factor
        if any(diff.values()):
            cut = max(floor, i + dim + 1)
            return cut if cut <= ceiling else None
    return floor


def keys_as_strings(tallies):
    return {' / '.join(str(item) for item in key): n for key, n in sorted(tallies.items(), key=lambda row: str(row[0]))}


def compare_fields(expected, current):
    result = {}
    for field, value in current.items():
        if isinstance(value, dict):
            result[field] = {key: [expected[field].get(key), value.get(key)]
                             for key in sorted(expected[field].keys() | value.keys())
                             if expected[field].get(key) != value.get(key)}
        else:
            result[field] = {'exact ordered match': expected[field] == value,
                             'recorded entries': len(expected[field]), 'recounted entries': len(value)}
    return result


def forecast_window_finding(guessed_dim, guessed_cut, fit, n):
    if not guessed_dim:
        return 'no positive dimension forecast'
    expected_eligible = guessed_cut <= n - 2
    if fit is None:
        return 'forecast eligible, no observed fit' if expected_eligible else 'neither cut eligible'
    if not expected_eligible:
        return 'observed fit eligible, forecast cut outside'
    return 'cut matches' if fit == guessed_cut else 'cut differs'


def read_drawn_strata():
    with (STUDY / 'stratified.jsonl').open() as stream:
        return {x['index']: x['drawn for'] for x in map(json.loads, stream)}


def discrepancy_rows(actual, forecast, firsts, n):
    witness = {}
    for name, observed, predicted, round_number in zip(READINGS, actual, forecast, firsts):
        if round_number is None:
            continue
        before = observed[round_number - 1] if round_number <= n else Counter()
        after = predicted[round_number - 1] if round_number <= len(predicted) else Counter()
        witness[name] = {'round': round_number, 'grown only': sorted((before - after).items()),
                         'predicted only': sorted((after - before).items())}
    return witness


def birth_kinds(reading):
    counts = Counter()
    for (kind, _, _, _), n in reading.items():
        counts[kind] += n
    return counts


def comparing_laws(growth, predictions):
    tallies = Counter()
    for key, grown in growth.items():
        panel, law, index = key
        if law != 'nae':
            continue
        parity_key = (panel, 'parity', index)
        if parity_key not in growth:
            continue
        parity = growth[parity_key]
        assert grown['stars'] == parity['stars'], key
        tallies[panel, 'paired starts'] += 1
        if predictions[key]['read'] != 'predicted':
            continue
        assert predictions[parity_key]['read'] == 'predicted', key
        tallies[panel, 'accepted pairs'] += 1
        overlapping_rounds = min(len(grown['rows']), len(parity['rows']))
        match = grown['rows'][:overlapping_rounds] == parity['rows'][:overlapping_rounds]
        label = 'same saved rows and end' if match and grown['end'] == parity['end'] and len(grown['rows']) == len(parity['rows']) else (
            'same overlapping rows only' if match else 'different in overlapping rows')
        tallies[panel, label] += 1
        if predictions[key]['rows'] == predictions[parity_key]['rows']:
            tallies[panel, 'identical frozen predictions'] += 1
    for (panel, law, index), grown in growth.items():
        if panel == 'horizon':
            common = ('uniform', law, index)
            if common not in growth:
                continue
            uniform = growth[common]
            assert uniform['stars'] == grown['stars']
            length = min(len(uniform['rows']), len(grown['rows']))
            tallies['horizon', 'paired with uniform'] += 1
            tallies['horizon', 'same uniform prefix' if grown['rows'][:length] == uniform['rows'][:length] else 'different uniform prefix'] += 1
    return keys_as_strings(tallies)


def recount(limit):
    growth, predictions = inputs(PANELS, limit)
    drawn = read_drawn_strata()
    p1, p2, stalls, support, strata, eligibility, conditional, archive = (Counter() for _ in range(8))
    misses = []
    witnesses = []
    shorter = []
    with_open_dimension = []
    dimension_mismatches = []
    observed_k_differences = []
    forecast_fit_differences = []
    alternate_eligibility = []
    for key, grown in growth.items():
        panel, law, index = key
        horizon = 40 if panel == 'horizon' else 24
        p = predictions[key]
        rows = grown['rows']
        n = len(rows)
        counts = [row['n'] for row in rows]
        assert all(count > 0 for count in counts), key
        assert grown['knots'] == len(grown['stars']) + sum(counts), key
        archive[panel, law, 'records'] += 1
        archive[panel, law, 'rounds saved'] += n
        archive[panel, law, 'births saved'] += sum(counts)
        end = grown['end']
        if ' at round ' in end:
            assert int(end.rsplit(' ', 1)[1]) == n + 1, key
        if end == 'rounds':
            assert n == horizon, key
        if end == 'bound':
            assert grown['knots'] > 30000 and grown['knots'] - counts[-1] <= 30000, key
        actual = read_rows(grown)
        observed_kind = dimension(counts, end)
        if observed_kind != grown['kind']:
            dimension_mismatches.append([key, grown['kind'], observed_kind])
        support[panel, law, p['read'], end.split(' at ')[0], 'rounds', n] += 1
        support[panel, law, p['read'], 'growth label', observed_kind, 'predicted dimension', p['D']] += 1
        if p['read'] != 'predicted':
            assert p['rows'] is None and p['D'] is None
            if p['read'] == 'stall':
                stalls[panel, law, 'read as stalling: grown ' + end] += 1
            else:
                p1[panel, law, 'not predicted: ' + p['read']] += 1
            continue

        forecast = read_rows(p)
        assert len(p['rows']) == horizon and n <= horizon, key
        firsts = [first_difference(read, estimate, n, end.startswith('closes')) for read, estimate in zip(actual, forecast)]
        first = min((round_number for round_number in firsts if round_number is not None), default=None)
        if end.startswith('stalls'):
            first = end
        part = 'proved class' if p['stratum'] == 'proved class' else 'a new reading'
        interpretation = 'agree in every round read' if first is None else 'differ'
        p1[panel, law, part, interpretation] += 1
        for name, diff in zip(READINGS, firsts):
            conditional[panel, law, 'P1 reading', name, 'agree' if diff is None else 'differ'] += 1
        strata[panel, law, 'structure', p['stratum'], interpretation] += 1
        for tag in p['rare strata']:
            strata[panel, law, 'member', tag, interpretation] += 1
        if panel == 'stratified':
            strata[panel, law, 'first selection', drawn[index], interpretation] += 1
        if first is not None:
            misses.append({'set': panel, 'knot law': law, 'index': index, 'stratum': p['stratum'],
                           'rare strata': p['rare strata'], 'first differing round': first, 'stars': grown['stars']})
            closed = end.startswith('closes')
            total_miss = first_difference(counts, [row['n'] for row in p['rows']], n, closed)
            kind_miss = first_difference(list(map(birth_kinds, actual[0])), list(map(birth_kinds, forecast[0])), n, closed)
            witnesses.append({'record': key, 'stratum': p['stratum'], 'memberships': p['rare strata'],
                              'selected for': drawn.get(index) if panel == 'stratified' else None,
                              'diagnostic first difference by total and by birth kind': [total_miss, kind_miss],
                              'difference': discrepancy_rows(actual, forecast, firsts, n)})

        d = p['D']
        forecast_ks = [p['K0'], p['K1']]
        seen_dim = int(observed_kind.split()[1]) if observed_kind.startswith('dim ') else None
        if not seen_dim:
            p2[panel, law, 'kind ' + observed_kind.split()[0]] += 1
        else:
            p2[panel, law, 'grown D equals the predicted' if seen_dim == d else 'grown D differs'] += 1
        if d == 0 or observed_kind == 'closes':
            last_forecast_birth = max((i for i, kinds in enumerate(forecast[0], 1) if kinds), default=0)
            conditional[panel, law, 'closure and zero D', d, observed_kind] += 1
            conditional[panel, law, 'closure and zero D', interpretation] += 1
            conditional[panel, law, 'last nonzero forecast round', 'matches' if last_forecast_birth == n else 'differs'] += 1
            if d == 0:
                assert forecast_ks == [max(last_forecast_birth, 3)] * 2, key
        if n != horizon:
            shorter.append({'record': key, 'saved': n, 'end': end, 'knots': grown['knots'], 'D': d,
                            'label': observed_kind, 'matches': first is None, 'predicted cuts': forecast_ks})
        if seen_dim != d and (seen_dim is not None or d > 0):
            with_open_dimension.append({'record': key, 'saved': n, 'end': end, 'last counts': counts[-8:], 'D': d,
                                        'label': observed_kind, 'extended label': dimension(counts, end, 7),
                                        'predicted cuts': forecast_ks, 'matches': first is None})
        for name, read, estimate, kp in zip(READINGS, actual, forecast, forecast_ks):
            observed_k = settling_cut(read, seen_dim) if seen_dim else None
            if observed_k is not None:
                conditional[panel, law, name, 'observed cut available'] += 1
            if seen_dim:
                if kp > n - 2:
                    p2[panel, law, name, 'predicted K past the rounds read'] += 1
                else:
                    p2[panel, law, name, 'K as predicted' if observed_k == kp else 'K differs'] += 1
                    conditional[panel, law, name, 'P1 comparison', interpretation, 'K matches' if observed_k == kp else 'K differs'] += 1
                if observed_k != kp:
                    observed_k_differences.append({'record': key, 'reading': name, 'saved': n, 'predicted': kp,
                                                   'observed': observed_k, 'P1 matches': first is None})
            if d > 0:
                read_at_guessed_d = observed_k if seen_dim == d else settling_cut(read, d)
                fit_on_forecast_prefix = settling_cut(estimate[:n], d)
                fit_on_full_forecast = settling_cut(estimate, d)
                outcome = forecast_window_finding(d, kp, read_at_guessed_d, n)
                eligibility[panel, law, name, observed_kind, outcome] += 1
                if kp <= n - 2:
                    conditional[panel, law, name, 'cut could be earlier' if kp > max(d, 3) else 'cut at lower limit'] += 1
                    conditional[panel, law, name, 'cut could be later' if kp < n - 2 else 'cut at upper limit'] += 1
                if n < horizon and seen_dim:
                    conditional[panel, law, name, 'included shorter record', outcome] += 1
                if (kp <= n - 2) != (read_at_guessed_d is not None):
                    alternate_eligibility.append({'record': key, 'reading': name, 'saved': n, 'predicted': kp,
                                                  'observed at predicted D': read_at_guessed_d, 'outcome': outcome})
                if kp != fit_on_full_forecast or fit_on_forecast_prefix != (kp if kp <= n - 2 else None):
                    forecast_fit_differences.append({'record': key, 'reading': name, 'saved': n, 'predicted': kp,
                                                     'fit to saved prefix': fit_on_forecast_prefix,
                                                     'fit to full forecast': fit_on_full_forecast})

    expected = json.loads((STUDY / 'score.json').read_text())
    current = {'P1 and P3': keys_as_strings(p1), 'P2': keys_as_strings(p2),
               'read as stalling': keys_as_strings(stalls), 'misses': misses}
    return {'prefix per panel': limit, 'score fields': compare_fields(expected, current) if limit is None else None,
            'archives': keys_as_strings(archive), 'comparison by law and horizon': comparing_laws(growth, predictions),
            'counts': {key: value for key, value in current.items() if key != 'misses'},
            'record labels and lengths': keys_as_strings(support), 'by stratum': keys_as_strings(strata),
            'additional checks': keys_as_strings(conditional), 'cut eligibility by forecast and observed fit': keys_as_strings(eligibility),
            'grown labels that do not reproduce': dimension_mismatches, 'positive dimension not matched by label': with_open_dimension,
            'accepted records below the target horizon': shorter, 'observed settling cut differences': observed_k_differences,
            'forecast cut differences against its finite rows': forecast_fit_differences,
            'one cut eligible but the other not': alternate_eligibility, 'first differing counts': witnesses}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    args.output.write_text(json.dumps(recount(args.limit), indent=2) + '\n')
