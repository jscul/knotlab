"""Extend the complete connected state and ordinary-growth census to ten distinctions."""

from collections import Counter, defaultdict
import gzip
import json

from census_diagnostics import HERE, ROOT, diagnostics
from census_irredundant import LAWS, census_width, update_minima


WIDTH = 10
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
OLD_OUTPUT = ROOT / 'artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant'
STRUCTURAL_OUTPUT = (ROOT / 'artifacts/FOUR-READINGS-20261120-001C'
                     / 'FOUR-READINGS-20261120-001C-E001_embodied_settings')


def alternative_outcomes(rows):
    totals = Counter(named_aliases_with_same_presentation_type=0,
                     named_aliases_with_multiple_types=0, named_aliases_with_live_holder=0,
                     named_aliases_with_one_roster=0, state_orbits_with_only_closed_alternatives=0)
    by_status = defaultdict(Counter)
    for row in rows:
        if row['named_presentations_per_state'] <= 1:
            continue
        weight = row['named_states_in_orbit']
        multiple_types = len(row['presentations']) > 1
        has_live = any(p['has_loose_distinction'] for p in row['presentations'])
        one_roster = row['named_rosters_per_state'] == 1
        statuses = {p['status'] for p in row['presentations']}
        totals['named_aliases_with_same_presentation_type'] += weight * (not multiple_types)
        totals['named_aliases_with_multiple_types'] += weight * multiple_types
        totals['named_aliases_with_live_holder'] += weight * has_live
        totals['named_aliases_with_one_roster'] += weight * one_roster
        totals['state_orbits_with_only_closed_alternatives'] += statuses == {'closed'}
        tally = by_status[','.join(sorted(statuses))]
        tally['orbits'] += 1
        tally['named_states'] += weight
        tally['named_states_with_one_roster'] += weight * one_roster
    return {'named_holding_ambiguity': totals, 'by_first_outcome': by_status}


def combine_counts(previous, added):
    totals = {law: Counter() for law in LAWS}
    for counts in (*previous.values(), added):
        for law, cells in counts['laws'].items():
            totals[law].update({key: val for key, val in cells.items() if isinstance(val, int)})
    return totals


def previous_certificates(result, earlier):
    readouts = result['recovery']
    keys = {'mandatory': 'mandatory', 'one_flip': 'single_word', 'residual': 'residual'}
    for old, new in keys.items():
        for units in ('orbits', 'named_states'):
            assert readouts[f'{new}_{units}'] == earlier['covered'][f'{old}_{units}']
    assert readouts['state_orbits'] == earlier['state_orbits']


def main():
    expected = json.loads((STRUCTURAL_OUTPUT / 'census_summary.json').read_text())
    before = json.loads((OLD_OUTPUT / 'census_summary.json').read_text())['by_width']
    earlier_certificates = json.loads((OLD_OUTPUT / 'certificates.json').read_text())['widths']
    with gzip.open(OLD_OUTPUT / 'census_cases.json.gz', 'rt') as record:
        older_cases = json.load(record)

    syntax, laws, cases, entries = census_width(WIDTH)
    assert syntax['all_up_to_renaming'] == expected['by_size'][str(WIDTH)]['structural']['presentations']
    print('Ten-distinction structural and state classes', dict(syntax=syntax, laws=laws), flush=True)
    additions = {'syntax': syntax, 'laws': laws}
    summary = {'width': WIDTH, **additions, 'totals_through_width': combine_counts(before, additions),
               'outcomes_at_equal_states': {}, 'width_ten_minimum_holder_counts': {}}
    for law in LAWS:
        summary['outcomes_at_equal_states'][law] = alternative_outcomes(cases[law])
        minima = {}
        update_minima(minima, WIDTH, entries[law])
        summary['width_ten_minimum_holder_counts'][law] = minima

    receipts = {}
    for n, previous in (*older_cases.items(), (str(WIDTH), cases)):
        results = diagnostics(int(n), previous['nae'])
        if int(n) < WIDTH:
            previous_certificates(results, earlier_certificates[n])
        receipts[n] = results
        print(f'width {n}: {results["recovery"]}', flush=True)

    OUTPUT.mkdir(exist_ok=True, parents=True)
    (OUTPUT / 'census_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUTPUT / 'census_cases.json.gz').write_bytes(gzip.compress(json.dumps(cases).encode(), mtime=0))
    (OUTPUT / 'census_diagnostics.json').write_text(json.dumps(receipts, indent=2) + '\n')


if __name__ == '__main__':
    main()
