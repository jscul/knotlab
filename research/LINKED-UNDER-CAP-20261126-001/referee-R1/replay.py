"""Replay stratified samples of the census and the repeated-change pass."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import random
import resource
import sys
from time import perf_counter

from growth import FAR, RECEIVER, build_pair, far_members, first_own_difference, grow, link_status, perturb, sharing_counts


STUDY = Path(__file__).resolve().parents[1]
SEED = 20261126
FIRST = 'linked_runs.jsonl.gz'
SECOND_SWITCH = 'again_linked_runs_caps36.jsonl.gz'
SECOND_CENSUS = 'again_linked_runs_receivers.jsonl.gz'
RECEDE = 'SECOND-SWITCH-20261126-001/recede_runs.jsonl.gz'
RECEIVERS = 'SWITCH-RECEIVERS-20261126-001/receivers_runs.jsonl.gz'
RULE = 'SWITCH-RECEIVERS-20261126-001/rule_runs.jsonl.gz'


def load(file):
    with gzip.open(STUDY / file, 'rt') as source:
        yield from (json.loads(line) for line in source if line.strip())


def switch_kind(case):
    return case['A'].startswith('tri:')


def case_key(case):
    return case['law'], case['A'], case['B']


def first_selection():
    rng = random.Random(SEED)
    strata = defaultdict(list)
    for case in load(FIRST):
        if 'law' not in case:
            continue
        links = case['linked']
        after_eight = links[7] if len(links) >= 8 else None
        strata[case['law'], switch_kind(case), after_eight is True].append(case)
    return [(stratum, rng.choice(sorted(cases, key=case_key))) for stratum, cases in sorted(strata.items())]


def second_selection():
    rng = random.Random(SEED)
    switch = list(load(SECOND_SWITCH))
    census = list(load(SECOND_CENSUS))

    def pick(options):
        return rng.choice(sorted(options, key=case_key))

    selection = []
    for law in sorted({r['law'] for r in switch}):
        for placed in (False, True):
            case = pick(r for r in switch if r['law'] == law and ('knot' in r['changes'][1]) == placed)
            selection.append((('switch kind', law, 'round-seven change placed' if placed else 'no round-seven target'), case))
    extinct = pick(r for r in switch if None in r['changes'][0]['linked after it'][3:])
    if extinct not in [case for _, case in selection]:
        selection.append((('switch kind', 'no far member after the first change'), extinct))
    for heard in (False, True):
        case = pick(r for r in census if (r['changes'][0]['heard'] is not None) == heard)
        selection.append((('census receiver', 'first change heard' if heard else 'first change unheard'), case))
    return selection


def horizon(phase, case):
    if phase == 'second':
        return 32, 10000
    return (24, 6000) if switch_kind(case) else (16, 3000)


def case_plan(phase, case, strata):
    rounds, bound = horizon(phase, case)
    changed_horizon = (24, 6000) if phase == 'first' else (rounds, bound)
    return {'phase': phase, 'stratum': strata, 'key': case_key(case), 'rounds': rounds, 'bound': bound,
            'changed horizon': changed_horizon}


def links(history):
    return [link_status(state) for state in history.states[1:]]


def first_replay(case, history, plan):
    row = {'A': case['A'], 'B': case['B'], 'law': case['law'], 'rounds': len(history.rows),
           'linked': links(history), 'changes': []}
    if not switch_kind(case):
        row['knots'] = len(history.states[-1].knots)
    rounds, bound = plan['changed horizon']
    count_changes = []
    tighter_window = 0
    tighter_window_hearings = 0
    for t0 in (3, 5, 8):
        if t0 >= len(history.rows) or row['linked'][t0 - 1] is None:
            continue
        for want in (True, False):
            for knot, sharings in far_members(history.states[t0], want)[:5]:
                changed = perturb(history, t0, knot, rounds=rounds, bound=bound)
                heard, common = first_own_difference(history, changed, t0)
                row['changes'].append({'t0': t0, 'linked': want, 'knot': knot, 'sharings': sharings,
                                       'heard': heard, 'rounds': common})
                if heard is not None:
                    count_changes.append([t0, knot, heard, len(history.rows[heard - 1].own_births),
                                          len(changed.rows[heard - 1].own_births)])
                if not switch_kind(case):
                    bound_crossing = next((s.round for s in changed.states[t0 + 1:common + 1]
                                           if len(s.knots) > plan['bound']), common)
                    tighter_window += bound_crossing < common
                    tighter_window_hearings += heard is not None and heard > bound_crossing
    return row, {'changes cut earlier with the baseline bound': tighter_window,
                 'hearings outside that tighter window': tighter_window_hearings,
                 'own birth counts at first hearing': count_changes}


def second_replay(case, history):
    row = {'A': case['A'], 'B': case['B'], 'law': case['law'], 'rounds': len(history.rows),
           'knots': len(history.states[-1].knots), 'changes': []}
    count_changes = []
    for t0 in (3, 7, 11, 15):
        if t0 >= len(history.rows):
            break
        options = far_members(history.states[t0], True)
        if not options:
            row['changes'].append({'t0': t0, 'none linked': True})
            break
        knot, sharings = options[0]
        changed = perturb(history, t0, knot)
        heard, common = first_own_difference(history, changed, t0)
        row['changes'].append({'t0': t0, 'knot': knot, 'sharings': sharings, 'heard': heard,
                               'rounds': common, 'linked after it': links(changed)})
        if heard is not None:
            count_changes.append([t0, knot, heard, len(history.rows[heard - 1].own_births),
                                  len(changed.rows[heard - 1].own_births)])
        history = changed
    return row, {'own birth counts at first hearing': count_changes}


def series_check(source, field, archived, rebuilt, prefix=False, **where):
    if prefix:
        rebuilt = rebuilt[:len(archived)]
    n = min(len(archived), len(rebuilt))
    mismatches = [r for r, (old, new) in enumerate(zip(archived, rebuilt), 1) if old != new]
    return {'source': source, 'field': field, 'rounds checked': n, 'length match': len(archived) == len(rebuilt),
            'mismatch rounds': mismatches, 'archived': archived, 'rebuilt': rebuilt, **where}


def study_round_checks(phase, case, observed):
    if phase == 'first':
        return [series_check(FIRST, 'linked', case['linked'], observed['linked'])]
    source = SECOND_SWITCH if switch_kind(case) else SECOND_CENSUS
    observed_changes = {(c['t0'], c['knot']): c for c in observed['changes'] if 'knot' in c}
    checks = []
    for old in case['changes']:
        if 'linked after it' in old:
            key = old['t0'], old['knot']
            new = observed_changes.get(key, {})
            checks.append(series_check(source, 'linked after it', old['linked after it'], new.get('linked after it', []),
                                       t0=key[0], knot=key[1]))
    return checks


def predecessor_tables():
    recede = {row['B']: row for row in load(STUDY.parent / RECEDE)}
    panel = {}
    for source in (RECEIVERS, RULE):
        panel[source] = {(row['law'], row['A']): row['by sender'] for row in load(STUDY.parent / source)
                         if row.get('d') == 3 and 'by sender' in row}
    return recede, panel


def unsized_label(label):
    prefix, _, rest = label.partition(':')
    return rest if prefix.startswith('n') and prefix[1:].isdigit() else label


def predecessor_checks(plan, history, tables):
    recede, panel = tables
    law, receiver, far = plan['key']
    own = [len(row.own_births) for row in history.rows]
    out = []
    if law == 'CAP-3' and receiver == 'tri:122@0' and far in recede:
        row = recede[far]
        out.append(series_check(RECEDE, 'own births', row['own births'], own, prefix=True))
        nearest = []
        waiting = []
        for state in history.states[1:row['rounds'] + 1]:
            counts = sharing_counts(state)
            far_members = [u for u in state.members if state.knots[u].roles == FAR and u in counts]
            nearest.append(min((counts[u] for u in far_members), default=None))
            waiting.append(min((counts[u] for u in far_members if state.knots[u].born < state.round), default=None))
        out.append(series_check(RECEDE, 'nearest far member', row['nearest far member'], nearest))
        out.append(series_check(RECEDE, 'nearest far member that waited', row['nearest far member that waited'], waiting))
    for source, sender in ((RECEIVERS, far), (RULE, unsized_label(far))):
        row = panel[source].get((law, receiver), {}).get(sender)
        if row is None:
            continue
        out.append(series_check(source, 'own births', row['own births'], own, prefix=True, sender=sender))
        short = [sum(history.states[c].knots[u].roles == RECEIVER for u in r.short)
                 for c, r in enumerate(history.rows[:row['rounds']])]
        out.append(series_check(source, 'A short', row['A short'], short, sender=sender))
    return out


def run_case(phase, case, plan, tables):
    started = perf_counter()
    law, receiver, far = plan['key']
    baseline = grow(build_pair(receiver, far), int(law.rsplit('-', 1)[1]), plan['rounds'], plan['bound'])
    observed, extra = first_replay(case, baseline, plan) if phase == 'first' else second_replay(case, baseline)
    series = study_round_checks(phase, case, observed) + predecessor_checks(plan, baseline, tables)
    archival_differences = sorted(key for key in observed.keys() | case.keys()
                                  if key not in observed or key not in case or observed[key] != case[key])
    return {'selection': plan, 'terminal knots': len(baseline.states[-1].knots), 'replay': observed,
            'archive mismatches': {key: {'observed': observed.get(key), 'expected': case.get(key)}
                                   for key in archival_differences},
            'round comparisons': series, **extra, 'wall seconds': round(perf_counter() - started, 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('first', 'second', 'both'), default='both')
    parser.add_argument('--limit-cases', type=int)
    parser.add_argument('--list', action='store_true', help='List the seeded cases in JSON')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    phases = ('first', 'second') if args.phase == 'both' else (args.phase,)
    selected = []
    for phase in phases:
        candidates = first_selection() if phase == 'first' else second_selection()
        selected.extend((phase, case, case_plan(phase, case, strata)) for strata, case in candidates[:args.limit_cases])
    if args.list:
        print(json.dumps([plan for _, _, plan in selected], indent=2))
        return 0
    started = perf_counter()
    tables = predecessor_tables()
    cases = [run_case(phase, case, plan, tables) for phase, case, plan in selected]
    counts = Counter()
    by_series = defaultdict(Counter)
    for entry in cases:
        name = entry['selection']['phase']
        changes = entry['replay']['changes']
        counts[f'{name} pairs'] += 1
        counts[f'{name} changes placed'] += sum('knot' in c for c in changes)
        counts[f'{name} archive mismatch pairs'] += bool(entry['archive mismatches'])
        for key in ('changes cut earlier with the baseline bound', 'hearings outside that tighter window'):
            counts[key] += entry.get(key, 0)
        for check in entry['round comparisons']:
            kind = 'predecessor' if '/' in check['source'] else name
            counts[f'{kind} archived round values checked'] += check['rounds checked']
            bad = bool(check['mismatch rounds']) or not check['length match']
            counts[f'{kind} archive mismatch series'] += bad
            by_series[check['source']][check['field']] += check['rounds checked']
    info = {'seed': SEED,
            'sample': ('First pass samples one pair per law and receiver family with and without a class link after round '
                       '8. Second pass samples one switch-kind pair per cap with and without a round-7 change, one far-'
                       'member extinction case if absent, and one census-receiver pair in each first-hearing category.'),
            'archive coverage': ('The census supplies baseline class-link status by round. The second pass supplies class-'
                                 'link status by round for each growth with a placed change. Compatible predecessor '
                                 'records supply strict own birth counts and also nearest holder-step counts or strict '
                                 'own short counts. The change targets, holder steps at each target, first hearings, read '
                                 'horizons and available terminal knot totals are single readings.'),
            'ledger': dict(counts), 'round values by source and field': dict(by_series),
            'wall seconds': round(perf_counter() - started, 4),
            'peak RSS KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'cases': cases}
    if args.output:
        args.output.write_text(json.dumps(info, indent=2) + '\n')
        print(json.dumps({'ledger': info['ledger'], 'wall seconds': info['wall seconds'],
                          'peak RSS KiB': info['peak RSS KiB']}))
    else:
        print(json.dumps(info, indent=2))
    return any('mismatch' in key and count for key, count in counts.items())


if __name__ == '__main__':
    sys.exit(main())
