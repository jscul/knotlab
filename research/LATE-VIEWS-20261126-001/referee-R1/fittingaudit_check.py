"""Compare fitting predictions with the archives and replay the smallest starts."""

import argparse
from collections import Counter
import json
from pathlib import Path
import resource
from time import perf_counter

from fittingaudit import (
    FITTING, READINGS, archive_rows, case_key, closed, first_difference,
    label_counts, observed_dimension, outcome, recorded_kind, select, settle,
    table, violates_parity_knot_test, view,
)
from map_predict import evaluate
from regrow import grow


CONTROLS = {
    'five, not-all-equal': ('relay', 'cells'),
    'five, parity': ('not-all-equal on parity',),
}
CONTROL_TABLES = {
    'relay': 'control_no_relay_5_nae',
    'cells': 'control_no_cells_5_nae',
    'not-all-equal on parity': 'control_nae_reading_on_parity_5',
}


class Check:
    def __init__(self):
        self.tally = Counter()
        self.by_stratum = Counter()
        self.cuts = Counter()
        self.slack = Counter()
        self.read_by_admission = Counter()
        self.counts = Counter()
        self.first60 = []
        self.strict_only = []
        self.misses = []
        self.unread = []

    def compare(self, prediction, record, label):
        reason = prediction['read']
        inadmissible_parity = record.get('parity knot test failed')
        if inadmissible_parity is None:
            admission = 'not-all-equal record'
        else:
            admission = 'fails the parity knot test' if inadmissible_parity else 'passes the parity knot test'
        if reason != 'predicted':
            self.tally[label, 'not predicted: ' + reason] += 1
            self.read_by_admission[admission, 'not predicted: ' + reason] += 1
            return

        rows = prediction['rows']
        observed = record['rows']
        self.counts['accepted saved rounds compared'] += len(observed)
        self.counts['accepted saved births compared'] += sum(row['n'] for row in observed)
        self.counts['accepted closure tails compared'] += closed(record)
        self.counts['rounds compared after closure'] += (len(rows) - len(observed)) if closed(record) else 0

        first = {reading: first_difference(rows, record, reading) for reading in READINGS}
        strict = {reading: first_difference(rows, record, reading, strict=True) for reading in READINGS}
        first0, first1 = (first[reading] for reading in READINGS)
        both_held = first0 is None and first1 is None
        result = 'agree every round' if both_held else 'differ'
        self.tally[label, result] += 1
        self.by_stratum[prediction['stratum'], result] += 1
        self.read_by_admission[admission, result] += 1
        self.counts['accepted'] += 1
        if first != strict:
            self.strict_only.append({'case': case_key(record), 'saved disagreements': first, 'full check': strict})
        if not both_held:
            self.misses.append([*case_key(record), label, first0, first1])
            if len(self.first60) < 60:
                differing = (first0 or first1) - 1
                self.first60.append({'index': record['index'], 'kind': record['kind'], 'stars': record['stars'],
                                     'first differing round': first, 'grown': observed[differing]['sig0'],
                                     'predicted': rows[differing]['sig0']})

        dim = int(label.split()[1]) if label.startswith('dim ') else None
        if dim is None:
            if label == 'unread':
                wider = observed_dimension([row['n'] for row in observed], largest=6)
                self.unread.append([*case_key(record), len(observed), wider, prediction['D'],
                                    *(settle(observed, reading, wider) if wider else None for reading in READINGS),
                                    prediction['K0'], prediction['K1']])
            return
        self.cuts['predicted D', 'equals the observed' if dim == prediction['D'] else 'differs'] += 1
        for j, reading in enumerate(READINGS):
            cut = prediction[f'K{j}']
            if cut > len(observed) - 2:
                self.cuts[reading, 'predicted K past the rounds read'] += 1
                continue
            empirical_cut = settle(observed, reading, dim)
            self.cuts[reading, 'K as predicted' if empirical_cut == cut else 'K differs'] += 1
            self.slack[reading, (empirical_cut or 0) - cut] += 1

    def as_dict(self):
        return {'tally': label_counts(self.tally), 'by stratum': label_counts(self.by_stratum),
                'settling round': label_counts(self.cuts), 'observed K minus predicted': label_counts(self.slack),
                'comparison scope': dict(self.counts), 'by parity admission': label_counts(self.read_by_admission),
                'all saved-prefix misses [start size, census index, label, sig0 round, sig1 round]': self.misses,
                'extra strict-end discrepancies': self.strict_only,
                'accepted unread [size, census index, saved rounds, wider observed D, predicted D, observed K0, observed K1, predicted K0, predicted K1]': self.unread}


def compare_saved_table(check, saved, full):
    actual = check.as_dict()
    keys = ['tally']
    keys.extend(key for key in ('settling round', 'by stratum', 'observed K minus predicted') if key in saved)
    differences = {key: {'recount': actual[key], 'archived table': saved[key]}
                   for key in keys if full and actual[key] != saved[key]}
    if full and check.first60 != saved['misses (first 60)']:
        differences['first mismatches'] = {'recount': check.first60, 'archived table': saved['misses (first 60)']}
    return differences


def original_variant(stars, horizon, law, control):
    if control == 'not-all-equal on parity':
        return evaluate(stars, horizon, law='nae')
    return evaluate(stars, horizon, law=law, control=control)


def cases_control_can_change(baseline, control, n):
    return any(view(a, reading) != view(b, reading)
               for a, b in zip(baseline[:n], control[:n], strict=True) for reading in READINGS)


def fit_archive(name, archive, pilot):
    frozen, revised = Check(), Check()
    revised_departures = []
    controls = {control: Check() for control in CONTROLS.get(name, ())}
    sensitivity = {control: Counter() for control in controls}
    for record, roster in select(archive_rows(archive.path), archive, pilot):
        stars = record['stars']
        label = recorded_kind(record)
        if archive.law == 'parity':
            record['parity knot test failed'] = violates_parity_knot_test(stars)
        baseline = evaluate(stars, 24, law=archive.law)
        assert baseline['read'] == roster.disposition(archive.law), case_key(record)
        if baseline['read'] == 'predicted':
            assert roster.stratum == baseline['stratum'], case_key(record)
        frozen.compare(baseline, record, label)
        graded = evaluate(stars, 24, law=archive.law, mode='graded')
        revised.compare(graded, record, label)
        changed_fields = [key for key in ('read', 'stratum', 'D', 'K0', 'K1', 'rows') if graded[key] != baseline[key]]
        if changed_fields:
            revised_departures.append([*case_key(record), changed_fields])
        for name_of_control, audit in controls.items():
            changed = original_variant(stars, archive.horizon, archive.law, name_of_control)
            audit.compare(changed, record, label)
            if changed['read'] != 'predicted':
                continue
            if baseline['read'] == 'predicted':
                cover = sensitivity[name_of_control]
                cover['accepted by the baseline and control'] += 1
                cover['departure possible in the saved birth rounds'] += cases_control_can_change(
                    baseline['rows'], changed['rows'], len(record['rows']))
                cover['departure possible by the nominal horizon'] += cases_control_can_change(
                    baseline['rows'], changed['rows'], archive.horizon)
            else:
                sensitivity[name_of_control]['accepted by the control alone'] += 1

    return {
        'frozen': frozen.as_dict(), 'post-freeze graded': revised.as_dict(),
        'fields changed by graded forecasts through round 24 [size, census index, fields]': revised_departures,
        'differences from saved fitting table': compare_saved_table(frozen, table(archive.table), pilot is None),
        'controls': {control: {**audit.as_dict(), 'leverage': dict(sensitivity[control]),
                               'differences from saved control comparison': compare_saved_table(
                                   audit, table(CONTROL_TABLES[control]), pilot is None)}
                     for control, audit in controls.items()},
    }


def prefix(record, horizon, start_size):
    if len(record['rows']) < horizon:
        return record
    rows = record['rows'][:horizon]
    return {**record, 'rows': rows, 'end': 'rounds', 'knots': start_size + sum(r['n'] for r in rows)}


def replays_small(pilot):
    archive = FITTING['one to four, not-all-equal']
    counts = {law: Counter() for law in ('nae', 'parity')}
    checks = {(law, horizon): Check() for law in counts for horizon in (20, 24)}
    wrong_archive = []
    for record, data in select(archive_rows(archive.path), archive, pilot):
        stars = record['stars']
        for law in counts:
            fresh = grow(stars, rounds=24, law=law, cap=30_000)
            assert not fresh['end'].startswith('replay limit'), (case_key(record), law, fresh['end'])
            fresh.update(stars=stars, index=record['index'])
            if law == 'parity':
                fresh['parity knot test failed'] = violates_parity_knot_test(stars)
            counts[law]['records replayed'] += 1
            counts[law]['births replayed'] += fresh['knots'] - len(stars)
            counts[law]['birth rounds replayed'] += len(fresh['rows'])
            counts[law]['census cases failing parity knot test'] += fresh.get('parity knot test failed', False)
            counts[law]['saved ends: ' + fresh['end']] += 1
            small = prefix(fresh, 20, len(stars))
            if law == 'nae' and any(small[key] != record[key] for key in ('rows', 'end', 'knots')):
                wrong_archive.append(case_key(record))
            for horizon in (20, 24):
                result = prefix(fresh, horizon, len(stars))
                prediction = evaluate(stars, horizon, law=law)
                assert prediction['read'] == data.disposition(law), case_key(record)
                result['kind'] = outcome(result)
                checks[law, horizon].compare(prediction, result, result['kind'])
    return {'replay counts': {law: dict(numbers) for law, numbers in counts.items()},
            'one-to-four knot archived not-all-equal discrepancies': wrong_archive,
            'comparisons on newly replayed data': {f'{law} to {horizon}': result.as_dict()
                                                  for (law, horizon), result in checks.items()}}


def replays_capped(pilot):
    """Use a higher knot cap on the fitted cases whose saved runs stopped early."""
    archives = tuple(FITTING[name] for name in ('five, not-all-equal', 'five, parity'))
    sources = [archive_rows(archive.path) for archive in archives]
    checked = []
    bins = Counter()
    for records in zip(*sources, strict=True):
        selected = records[0]
        key = case_key(selected)
        stars = selected['stars']
        assert key == case_key(records[1]) and stars == records[1]['stars'], key
        if selected['end'] != 'bound' or len(selected['rows']) >= 24:
            continue
        rank = recorded_kind(selected)
        if pilot is not None and bins[rank] >= pilot:
            continue
        comparisons = {}
        for record, archive in zip(records, archives, strict=True):
            prediction = evaluate(stars, 24, law=archive.law)
            if prediction['read'] != 'predicted':
                break
            result = grow(stars, rounds=24, law=archive.law, cap=200_000)
            assert result['end'] == 'rounds', (key, result['end'])
            assert result['rows'][:len(record['rows'])] == record['rows'], (key, archive.law)
            comparisons[archive.law] = {
                'saved rounds': len(record['rows']), 'new end': result['end'], 'knots after round 24': result['knots'],
                'new birth totals': [row['n'] for row in result['rows'][len(record['rows']):]],
                'new observed dimension among 1–6': observed_dimension([row['n'] for row in result['rows']], largest=6),
                'first differing round': {reading: first_difference(prediction['rows'], result, reading, strict=True)
                                         for reading in READINGS},
            }
        if comparisons:
            bins[rank] += 1
            checked.append({'census index': key[1], 'archived label': rank, 'laws': comparisons})
    return {'new knot cap': 200_000, 'new horizon': 24, 'start count by archived label': dict(bins), 'replayed': checked}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=('predictions', 'small-replay', 'cap-replay'))
    parser.add_argument('--pilot', type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    started = perf_counter()
    if args.part == 'predictions':
        report = {name: fit_archive(name, archive, args.pilot) for name, archive in FITTING.items()}
    elif args.part == 'small-replay':
        report = replays_small(args.pilot)
    else:
        report = replays_capped(args.pilot)
    report['pilot cases per bin'] = args.pilot
    report['elapsed seconds'] = round(perf_counter() - started, 3)
    report['peak RSS KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report['address space cap KiB'] = resource.getrlimit(resource.RLIMIT_AS)[0] // 1024
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
