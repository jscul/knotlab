"""Recount the history-based takes and first meetings using the D referee."""

from collections import Counter
import hashlib
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONTRACT_PATH = HERE.parent / 'contract.json'
PREDECESSOR = ROOT / ('experiments/WIDENING-ROSTERS-20261125-001D/'
                      'WIDENING-ROSTERS-20261125-001D-E001_links')
REFEREE = PREDECESSOR / 'referee'
sys.path.insert(0, str(REFEREE))
import referee as previous


def row_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def identity(value):
    return hashlib.sha256(row_bytes(value)).hexdigest()


def unique(values):
    if len(values) == 1:
        return next(iter(values))
    return None


def unique_latest(rounds):
    if not rounds:
        return None
    latest = max(rounds.values())
    return unique([d for d, t in rounds.items() if t == latest])


class HistorySelector(previous.Selector):
    """Read past extra takes from the holders and parent lists in a completed snapshot."""

    def __init__(self, stage, rule):
        super().__init__(stage, rule, None)
        self.stage = stage
        self.last_takes = {}

    def last_take(self, d):
        if d not in self.last_takes:
            state = self.stage
            # A later holder gained d as an extra if it neither made d nor inherited it.
            self.last_takes[d] = max((state.made[knot] for knot in state.holders[d]
                                      if state.made[knot] > 0 and knot != state.maker[d]
                                      and all(d not in state.places[parent]
                                              for parent in state.parents[knot])), default=0)
        return self.last_takes[d]

    def creation(self, d):
        maker = self.stage.maker[d]
        return 0 if maker is None else self.stage.made[maker]

    def select(self, offer):
        if len(offer) <= 1:
            return unique(offer)
        if self.rule == 'EVER':
            return unique([d for d in offer if self.last_take(d) > 0])
        if self.rule == 'LAST_USE':
            return unique_latest({d: t for d in offer if (t := self.last_take(d)) > 0})
        if self.rule == 'NEWEST':
            return unique_latest({d: self.creation(d) for d in offer})
        if self.rule == 'SOLE_MADE':
            return unique([d for d in offer if self.stage.maker[d] is not None])
        if self.rule == 'THREE':
            return unique([d for d in offer if len(self.holders[d]) == 3])
        raise ValueError(self.rule)

    def choose(self, stage, law, birth, roster):
        _, suppliers = self.offers(birth['parents'])
        d = self.select(suppliers)
        return [] if d is None else [(d, tuple(sorted(suppliers[d])))]


def compare_to_most(outcomes, before, suppliers, choice):
    counts = {d: len(before.holders[d]) for d in suppliers}
    max_count = max(counts.values())
    most = unique([d for d, n in counts.items() if n == max_count])
    if choice == most:
        outcomes['both_abstain' if choice is None else 'same_choice'] += 1
    elif choice is None:
        outcomes['most_only'] += 1
    elif most is None:
        outcomes['history_rule_only'] += 1
    else:
        outcomes['different_choice'] += 1
    if choice is not None and counts[choice] < max_count:
        outcomes['selected_below_maximum'] += 1
        if most is not None:
            outcomes['selected_below_unique_maximum'] += 1
    return most, max_count, counts.get(choice)


def grow(stars, case, rule, knot_law):
    engine = previous.eng
    law = engine.Law(case['ration'], case['treatment'], 'MET-SOLE', knot_law)
    guard = engine.Guard()
    stages = [engine.from_stars(stars)]
    rounds, reach = [], []
    outcomes = Counter()
    last_take = {}
    stop = None
    original = engine.candidates
    try:
        for t in range(1, case['rounds'] + 1):
            before = stages[-1]
            after = before.copy()
            selector = HistorySelector(before, rule)
            engine.candidates = selector.choose
            try:
                record = engine.play_round(after, law, guard)
            except engine.GuardStop:
                stop = 'guard'
                break
            stages.append(after)
            rounds.append(record['births'])
            for d, recorded in selector.last_takes.items():
                if last_take.get(d, 0) != recorded:
                    raise ValueError('holder history disagrees with completed-round take ledger')
            round_takes = []
            for birth in record['births']:
                c1, suppliers = selector.offers(birth['parents'])
                (choice,) = birth['takes'] or (None,)
                if choice is not None and choice not in suppliers:
                    raise ValueError('birth took an ineligible distinction')
                if len(suppliers) > 1:
                    most, maximum, chosen_count = compare_to_most(outcomes, before, suppliers, choice)
                if choice is not None:
                    take = {'recipient': birth['id'], 'c': choice, 'c1': sorted(c1),
                            'near_eligible': choice in c1, 'c2': sorted(suppliers)}
                    if len(suppliers) > 1:
                        take.update(most_on_same_offer=most, max_holders=maximum,
                                    chosen_holders=chosen_count)
                    round_takes.append(take)
            reach.append(round_takes)
            last_take.update((take['c'], t) for take in round_takes)
            if after.n_knots > case['knot_bound']:
                stop = 'knots'
                break
    finally:
        engine.candidates = original
    return stages, rounds, reach, stop, dict(outcomes)


def stable_identities(stages, rounds):
    """Anchor comparisons across selectors in ancestry and the maker of each distinction."""
    knot_ids = [f'start knot {knot}' for knot in range(stages[0].n_knots)]
    distinction_ids = [f'start distinction {d}' for d in range(stages[0].n_distinctions)]
    for t, births in enumerate(rounds, 1):
        for birth in births:
            parents = sorted(knot_ids[knot] for knot in birth['parents'])
            knot_ids.append(identity((t, birth['kind'], parents, birth['off_index'])))
            distinction_ids.extend(identity((knot_ids[-1], i)) for i, _ in enumerate(birth['fresh']))
    supports = stages[-1].places
    if len(knot_ids) != len(supports) or len(distinction_ids) != stages[-1].n_distinctions:
        raise ValueError('birth identities do not cover the final completed stage')
    knots_with_support = [identity((k, sorted(distinction_ids[d] for d in support)))
                          for k, support in zip(knot_ids, supports, strict=True)]
    return knots_with_support, distinction_ids


def physical_keys(event, knot_ids, distinction_ids):
    parts = [sorted(knot_ids[knot] for knot in event[side]) for side in ('X', 'Y')]
    flip = parts[1] < parts[0]
    parts.sort()
    split_and_round = identity((event['s'], event['t'], parts))
    routes = []
    for route in event['routes']:
        x = knot_ids[route['v' if flip else 'u']]
        y = knot_ids[route['u' if flip else 'v']]
        routes.append((route['route'], knot_ids[route['w']], x, y,
                       sorted(distinction_ids[d] for d in route['contacts'])))
    witnesses = sorted(knot_ids[knot] for knot in event['linking_knots'])
    mixed = sorted((kind, knot_ids[knot]) for kind, knot in event['mixed_witnesses'])
    linking = sorted(distinction_ids[d] for d in event['linking_distinctions'])
    start_held = sorted(distinction_ids[d] for d in event['start_held_linking_distinctions'])
    full = identity((split_and_round, event['meeting_types'], witnesses, mixed, linking,
                     start_held, sorted(routes)))
    return split_and_round, full


def event_receipts(events, stages, rounds, reach):
    knot_ids, distinction_ids = stable_identities(stages, rounds)
    takes_by_round = [{take['recipient']: take for take in takes} for takes in reach]
    rows, provenance, strict_examples = [], [], []
    counts = Counter()
    has_outer = any(not take['near_eligible'] for takes in reach for take in takes)
    for event in sorted(events, key=lambda e: (e['s'], e['t'], e['X'], e['Y'])):
        start_held = bool(event['start_held_linking_distinctions'])
        strict = event['only_made_knots'] and not start_held
        crossing = {newborn for newborn, offer in event['take_offers'].items()
                    if offer['c'] not in offer['c1']}
        pure = [route for route in event['routes'] if route['route'] == 'take'
                and not route['near_eligible']]
        if pure and not crossing:
            raise ValueError('a pure outer crossing must be an actual outer crossing')
        row = {key: event[key] for key in ('s', 't', 'X', 'Y', 'meeting_types')}
        row.update(strict=strict, start_knot_holds_linking_distinction=start_held,
                   direct_outer=bool(pure), direct_outer_any=bool(crossing))
        rows.append(row)
        provenance.append(physical_keys(event, knot_ids, distinction_ids))
        counts['only_made_count'] += int(event['only_made_knots'])
        if strict:
            counts['strict_count'] += 1
            counts['strict_direct_outer_count'] += int(bool(pure))
            counts['strict_direct_outer_any_count'] += int(bool(crossing))
            counts['strict_with_outer_elsewhere_count'] += int(has_outer and not crossing)
            strict_examples.append({**row,
                                    'linking_knots': event['linking_knots'],
                                    'linking_distinctions': event['linking_distinctions'],
                                    'outer_crossing_takes': [takes_by_round[row['t'] - 1][newborn]
                                                             for newborn in sorted(crossing)],
                                    'pure_outer_routes': [{k: route[k] for k in ('w', 'u', 'v', 'newborn', 'contacts')}
                                                          for route in pure]})
    digest = hashlib.sha256()
    for row in rows:
        digest.update(row_bytes(row))
    return rows, provenance, strict_examples, dict(counts), digest.hexdigest()


def check_hash(path, wanted):
    with path.open('rb') as file:
        actual = hashlib.file_digest(file, 'sha256').hexdigest()
    if actual != wanted:
        raise ValueError(f'frozen referee input changed: {path}')


def setup(params):
    global settings
    contract = previous.read_json(CONTRACT_PATH)
    cases_path = ROOT / contract['cases']
    old_contract = PREDECESSOR / 'contract.json'
    for path in (cases_path, old_contract):
        check_hash(path, contract['inputs'][str(path.relative_to(ROOT))])
    prior = previous.read_json(old_contract)
    for path in (previous.STARTS, previous.CENSUS):
        check_hash(path, prior['inputs'][str(path.relative_to(ROOT))])
    if params.get('assay') != '1' and params.get('cases'):
        raise ValueError('an evidence run must use the frozen population in order')
    settings = {'contract': contract, 'cases': previous.read_json(cases_path),
                'named': previous.read_json(previous.STARTS), 'census': previous.read_json(previous.CENSUS),
                'params': params}


def cases():
    selected = set(settings['params'].get('cases', '').split(',')) - {''}
    for case in settings['cases']:
        if selected and case['id'] not in selected:
            continue
        for rule in settings['contract']['rules']:
            for law in settings['contract']['knot_laws']:
                yield f"{case['id']}--{rule}--{law}", (case, rule, law)


def run(case_id, payload):
    case, rule, law = payload
    start = perf_counter()
    stars = previous.raw_start(case['start'], settings['named'], settings['census'])
    stages, rounds, reach, stop, choices = grow(stars, case, rule, law)
    after_growth = perf_counter()
    events = previous.first_meetings(stages, rounds, reach, case['splits'])
    after_meetings = perf_counter()
    rows, provenance, strict, counts, digest = event_receipts(events, stages, rounds, reach)
    outer = [[t, take['recipient'], take['c']] for t, takes in enumerate(reach, 1)
             for take in takes if not take['near_eligible']]
    result = {'case': case['id'], 'rule': rule, 'kl': law, 'start': case['start'],
              'knots': stages[-1].n_knots, 'rounds_read': len(rounds), 'stop': stop,
              'split_coverage': [s for s in case['splits'] if s < len(rounds)],
              'takes': sum(map(len, reach)), 'outer_take_count': len(outer), 'outer_takes': outer,
              'meetings_count': len(rows), 'events': rows, 'events_sha256': digest,
              'event_provenance': provenance, 'strict_events': strict,
              'event_counts': counts, 'plural_choice_comparison': choices}
    metrics = {'grow_seconds': after_growth - start, 'meeting_seconds': after_meetings - after_growth}
    if settings['params'].get('assay') == '1':
        metrics['receipt_bytes'] = len(row_bytes(result))
    end = perf_counter()
    metrics.update(receipt_seconds=end - after_meetings, seconds=end - start,
                   peak_self_rss_kib=getrusage(RUSAGE_SELF).ru_maxrss)
    if settings['params'].get('assay') == '1':
        return metrics
    result['metrics'] = metrics
    return result
