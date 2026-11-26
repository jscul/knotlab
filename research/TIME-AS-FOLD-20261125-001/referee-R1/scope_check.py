"""Reconstruct the selection and compare the tests with the clocks they actually used."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import islice
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.name
TICKET = STUDY + 'A'
REG = ROOT / 'research' / TICKET
RAW = next((ROOT / 'artifacts' / TICKET).glob('*_count_of_returns'))
CONTRACT = next((ROOT / 'experiments' / TICKET).glob('*/contract.json'))
KEYS = ('group', 'start', 'base', 'rule', 'choice', 'knot_law')


def key(row):
    return tuple(row[k] for k in KEYS)


def rows(path, limit):
    with gzip.open(path, 'rt') as f:
        yield from map(json.loads, islice(f, limit))


def sort_key():
    rules = json.loads((REG / 'rules.json').read_text())
    base_laws = []
    for name, description in rules['base_laws'].items():
        if '(t)' in name:
            for t in ('RETIRE', 'OFFSHOOT', 'WAIT'):
                if 'CANCEL-' + t in description.split(' (')[0]:
                    base_laws.append(name.replace('(t)', '(' + t + ')'))
        else:
            base_laws.append(name)
    rule_order = list(dict.fromkeys(None if r['id'] == 'none' else r['id'] for r in rules['rules']))
    fields = (['main', 'fbp', 'dbt'], list(json.loads((REG / 'starts.json').read_text())['named']),
              base_laws, rule_order, rules['choices'], ['nae', 'parity'])
    return lambda k: tuple(c.index(v) for c, v in zip(fields, k))


def prototype_key(item, row):
    return (item, row['Y_size'], row['X_size'], row['j'], tuple(row['Y_rounds'][:5]),
            tuple(row['per_period_own']), tuple(row['per_period_joint']), tuple(row['differs_at']))


def check(limit):
    tests = Counter()
    positives = defaultdict(list)
    details = defaultdict(Counter)
    held_by_source = defaultdict(list)
    boundary_evidence = {}
    cap = Counter()
    all_keys = []
    per_group = Counter()
    ticks = Counter()
    meetings = Counter()
    proto_signatures = Counter()
    for row in rows(RAW / 'run4.jsonl.gz', limit):
        k = key(row)
        if 'X' not in row:
            continue
        tests[k] += 1
        cap[(k, row['t0'], tuple(row['P0']), row['j'])] += 1
        if row['verdict_C_iii'] != 'holds':
            continue
        positives[k].append((row['t0'], tuple(row['P0']), row['j']))
        held_by_source[k].append(row)
        rule = row['rule']
        bx = row['X_barred']
        both = min(bx['rounds'], row['run_A']['rounds'])
        ta = tuple(t for t in bx['Y_ticks_A'] if t <= both)
        tb = tuple(t for t in bx['Y_ticks_X_barred'] if t <= both)
        outcomes = details[rule]
        outcomes['tests'] += 1
        outcomes['X_has_three_members'] += len(row['X']) == 3
        outcomes['Y_three_members_period_three'] += row['Y_size'] == 3 and set(row['Y_periods']) == {3}
        outcomes['Y_returns_after_X_barred'] += bool(tb)
        outcomes['Y_returns_fewer_at_common_horizon'] += len(tb) < len(ta)
        outcomes['Y_equal_at_common_horizon'] += tb == ta
        outcomes['Y_equal_at_respective_horizons'] += bx['Y_ticks_A'] == bx['Y_ticks_X_barred']
        outcomes['all_three_bars_Bprime_change_course'] += all(
            isinstance(b["B'"],dict) and b["B'"].get('course_differs') is not None for b in row['bars'])
        made_bars = sum(bool(b.get('meeting') and b['meeting']['made_by_growth']) for b in row['bars'])
        outcomes['made_meetings_at_' + str(made_bars) + '_of_three_bars'] += 1
        for b in row['bars']:
            m = b.get('meeting')
            meetings[(rule, 'made' if m and m['made_by_growth'] else ('only start' if m else 'unspecified'))] += 1
        signature = (k, row['Y_size'], len(row['X']), row['j'], tuple(row['tick_rounds']),
                     tuple(row['own_A_per_period']), tuple(row['joint_A_per_period']),
                     tuple(b['course_differs'] for b in row['bars']))
        proto_signatures[signature] += 1

    for path in [*sorted(RAW.glob('run1_part*.jsonl.gz')), RAW / 'run2.jsonl.gz', RAW / 'run3.jsonl.gz']:
        for row in rows(path, limit):
            unfiltered = row['nopast']
            if not unfiltered['n_clocks']:
                continue
            k = key(row)
            all_keys.append(k)
            per_group[k[0]] += 1
            if k[0] == 'fbp' and k[1] == 'DW(5,3)':
                # Only a few neighboring runs are needed to explain the ordering discrepancy.
                if k[2:] in (('COPY-LAW(WAIT)','STEPS-3:join','BY-COUNT','parity'),
                             ('CAP-3(RETIRE)','MET:offshoot','OLDEST','parity')):
                    candidates = []
                    for s in row['nopast_series']:
                        if s['clock']:
                            for j in (0,1):
                                periods = s['periods'][j:j+4]
                                if len(periods)==4 and len(set(periods))==1:
                                    t = s['t0'] if not j else s['ticks'][0][0]
                                    candidates.append([t,row['per_round'][t][2]])
                    boundary_evidence[str(k)] = {'eligible_clock_starts_and_number_of_parts_at_choice':candidates,
                        'clock_count':unfiltered['n_clocks'], 'clocks_in_compact_record':sum(s['clock'] for s in row['nopast_series'])}
            if k in positives:
                # In run A, every followed first return listed in the record gives a test
                # of whether X itself has the same form again after the round of choice.
                returns = set()
                for s in row['nopast_series']:
                    timeline = [(s['t0'],tuple(s['P0']))] + [(v[0],tuple(v[1])) for v in s['ticks']]
                    returns.update(timeline[:-1])
                for h in held_by_source[k]:
                    details[k[3]]['X_with_a_recorded_own_first_return_in_A'] += (h['t_j'],tuple(h['X'])) in returns
                    details[k[3]]['baseline_series_listing_at_storage_cap'] += len(row['nopast_series'])>=200
                lookup = {(s['t0'], tuple(s['P0'])): s for s in row['nopast_series']}
                for t, p, j in positives[k]:
                    s = lookup[t, p]
                    off_per_tick = [tick[2] for tick in s['ticks']]
                    outcomes = details[k[3]]
                    outcomes['clock_gives_off_in_four_test_periods'] += all(off_per_tick[j:j+4])
                    outcomes['clock_gives_off_in_any_equal_four'] += any(
                        len(set(s['periods'][i:i+4])) == 1 and all(off_per_tick[i:i+4])
                        for i in range(len(s['periods'])-3))
                    outcomes['run_contains_a_clock_that_gives_off_at_four'] += unfiltered['clock_off4']
            if k[0] == 'main' and k[3] in ('STEPS-1','MET') and (
                    (k[3] == 'STEPS-1' and k[2].startswith('COPY-LAW')) or
                    (k[3] == 'MET' and k[2] in ('RING-LAW','CAP-3(RETIRE)','CAP-3(OFFSHOOT)'))):
                ticks[k[3]] += 1
    # Only run 1 contributes to either 5,000 cutoff.
    eligible1 = [k for k in all_keys if k[0] in ('main', 'fbp','dbt')]
    assert len(eligible1) == len(set(eligible1))
    by_definition = sorted(eligible1, key=sort_key())
    actual = set(all_keys[:5000])
    registered = set(by_definition[:5000])
    proto = json.loads((REG/'compare.json').read_text())['paired']['cases']
    expected = Counter()
    for row in proto:
        p = row['run']
        rule = p['take'] + ((':' + p['family'].split(':')[-1]) if p['family'] else '')
        k = key(dict(p, rule=rule))
        expected[prototype_key(k, row)] += 1
    c = json.loads(CONTRACT.read_text())
    frozen = dict(c['data_files'])
    for field in ('preregistration','definitions','claim','fold_definitions','shared_definitions'):
        frozen[c[field]] = c[field + '_sha256']
    return {
        'frozen_hashes_equal': {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in frozen.items()},
        'eligible_baseline_runs_by_group': per_group, 'eligible_primary_runs_with_a_clock': ticks,
        'selected_input_order': {'from_written_order':dict(Counter(k[0] for k in actual)),
                                 'from_registered_order':dict(Counter(k[0] for k in registered)),
                                 'registered_only':sorted(registered-actual,key=str),
                                 'written_only':sorted(actual-registered,key=str),
                                 'first_different_position':next((i for i,(a,b) in enumerate(zip(all_keys,by_definition),1)
                                                                   if a!=b),None),
                                 'nonempty_test_runs_outside_written_prefix':len(tests.keys()-actual),
                                 'registered_only_nonempty_run_records':sum(tests[k] for k in registered-actual),
                                 'written_only_test_records':sum(tests[k] for k in actual-registered),
                                 'selected_runs_with_test_records':len(actual & tests.keys()),
                                 'selected_runs_with_no_test_records':len(actual-tests.keys())},
        'boundary_run_evidence':boundary_evidence,
        'test_rows':sum(tests.values()), 'clock_and_j_groups_with_tests':len(cap),
        'second_parts_per_clock_and_j_histogram':dict(Counter(cap.values())),
        'C_iii_by_rule':dict(details), 'first_meetings_across_accepted_bars':
            {r:{m:n for (s,m),n in meetings.items() if s==r} for r in details},
        'prototype_positive_tests':sum(expected.values()),
        'prototype_tests_matched_including_j_rounds_counts_and_three_difference_rounds':
            sum((expected & proto_signatures).values()),
        'unmatched_disclosed_signatures':[{'signature':s,'multiplicity':n} for s,n in (expected-proto_signatures).items()]}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='first rows per file for the timing check')
    args = parser.parse_args()
    print(json.dumps(check(args.limit), indent=2))
