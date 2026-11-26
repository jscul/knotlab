"""Recount the four waiting-rule records with the standard library only."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations, islice, permutations, product
import json
from pathlib import Path
import random


STUDY = Path(__file__).resolve().parent.parent
PANELS = {
    'meeting_3': ('jam_d3_meeting.jsonl.gz', 3, 'meeting'),
    'meeting_2_sample': ('jam_d2_meeting_sample.jsonl.gz', 2, 'meeting'),
    'meeting_5_sample': ('jam_d5_meeting_sample.jsonl.gz', 5, 'meeting'),
    'share_3_sample': ('jam_d3_share_sample.jsonl.gz', 3, 'share'),
}
SEED = 20261126
WAITING = ('JOIN-FEWER', 'ONE-FEWER', 'REC-ONE-FEWER', 'CAP-3', 'FLOOR1', 'ORD')
LAWS = WAITING + ('JOIN-FEWER retire',)
ONE_FEWER = WAITING[:3]
BENCH = {
    'ring': [[4, 0, 5, 6, 7], [0, 1, 8, 9, 10], [1, 2, 11, 12, 13],
             [2, 3, 14, 15, 16], [3, 4, 17, 18, 19]],
    'copier': [[0, 1, 2], [0, 3, 4]],
    'source': [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14],
               [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20],
               [7, 8, 21, 22], [5, 8, 23, 24]],
    'stub': [[0]],
}
NAMED_TRIALS = {
    ('source', 'source'), ('ring', 'source'), ('copier', 'copier'),
    ('g1:3@0', 'source'), ('source', 'stub'),
}


def catalogue():
    """Make the four small meeting patterns and take representatives by symmetry."""
    starts = {}
    for label, size, shared in [(1, 1, []), (3, 2, [(0, 1)]),
                                (6, 3, [(0, 1), (0, 2)]),
                                (7, 3, list(combinations(range(3), 2)))]:
        knots = tuple(range(size))
        symmetries = [p for p in permutations(knots)
                      if {tuple(sorted((p[i], p[j]))) for i, j in shared} == set(shared)]
        for loose in product(range(4), repeat=size):
            places = [[token for token, holders in enumerate(shared) if i in holders] for i in knots]
            if any(len(places[i]) + loose[i] < 3 for i in knots):
                continue
            if loose != min(tuple(loose[p[i]] for i in knots) for p in symmetries):
                continue
            token = len(shared)
            for i, count in enumerate(loose):
                places[i].extend(range(token, token + count))
                token += count
            for i in knots:
                equivalents = [p[i] for p in symmetries if all(loose[p[j]] == loose[j] for j in knots)]
                if i == min(equivalents):
                    name = f'g{label}:{"".join(map(str, loose))}@{i}'
                    starts[name] = (places, i)
    assert len(starts) == 44
    starts.update((name, (places, 0)) for name, places in BENCH.items())
    return starts


def start_counts(places, root):
    holds = Counter(token for knot in places for token in knot)
    loose = [sum(holds[token] == 1 for token in knot) for knot in places]
    known = {root: 0}
    for step in range(1, len(places)):
        preceding = [i for i, d in known.items() if d == step - 1]
        for i, knot in enumerate(places):
            if i not in known and any(set(knot).intersection(places[j]) for j in preceding):
                known[i] = step
    return loose, [known[i] for i in range(len(places))]


def sited_fingerprint(places, root):
    """Forget names of knots and distinctions while preserving the joining knot."""
    held_by = defaultdict(set)
    for knot, tokens in enumerate(places):
        for token in tokens:
            held_by[token].add(knot)
    variants = []
    for order in permutations(i for i in range(len(places)) if i != root):
        names = {old: new for new, old in enumerate((root, *order))}
        variants.append(tuple(sorted(tuple(sorted(names[i] for i in holders)) for holders in held_by.values())))
    return min(variants)


def expected_changes(sender, distance, join, starts):
    places, root = starts[sender]
    loose, steps = start_counts(places, root)
    if sender == 'stub':
        loose[root] = 1 if join == 'meeting' else 2
    elif join == 'meeting':
        loose[root] += 1
    link_loose = 2 if join == 'meeting' else 1
    return {**{f'B{i}': (distance + j, loose[i]) for i, j in enumerate(steps)},
            **{f'bB{i}': (distance + j, loose[i]) for i, j in enumerate(steps) if loose[i]},
            **{f'{prefix}{i}': (i, link_loose) for prefix in ('L', 'bL') for i in range(1, distance)}}


def law_name(law):
    ration, treatment = law
    if treatment == 'CANCEL-RETIRE':
        return ration + ' retire'
    assert treatment == 'CANCEL-WAIT'
    return ration


def own_state(members, short):
    if not members:
        return 'no members'
    if not short:
        return 'no short'
    return 'all short' if short == members else 'some short'


def transition(without, changed):
    return {(False, False): 'neither', (False, True): 'starts',
             (True, False): 'ends', (True, True): 'both'}[without, changed]


def keys(distance):
    return [str(distance)] + (['2+'] if distance >= 2 else []) + (['3+'] if distance >= 3 else [])


def detail(rec, change):
    return {'receiver': rec['A'], 'sender': rec['B'], 'law': law_name(rec['law']),
            'distance': change['distance'], 'change': change['at'], 'heard': change['heard'],
            'rounds': change['rounds'], 'baseline members': rec['A members'],
            'baseline short': rec['A short'], 'changed short': change['A short with'],
            'baseline own births': rec['own births'], 'changed own births': change['own births with']}


class Panel:
    def __init__(self):
        self.rows = set()
        self.case = defaultdict(Counter)
        self.changes = defaultdict(lambda: defaultdict(Counter))
        self.by_round = defaultdict(lambda: defaultdict(Counter))
        self.risk_by_round = defaultdict(lambda: defaultdict(Counter))
        self.heard_by_round = defaultdict(lambda: defaultdict(Counter))
        self.no_wait_risk_receivers = defaultdict(lambda: defaultdict(set))
        self.no_wait_hearing_receivers = defaultdict(set)
        self.sign = defaultdict(Counter)
        self.barring = defaultdict(Counter)
        self.what_heard = defaultdict(dict)
        self.near_hearers = defaultdict(set)
        self.jammed_rows = defaultdict(set)
        self.no_short_rows = defaultdict(set)
        self.training_hits = defaultdict(Counter)
        self.trial_rows = {}
        self.stub = defaultdict(Counter)
        self.bench_receivers = defaultdict(Counter)
        self.bench_horizons = defaultdict(Counter)
        self.starting_jam_senders = defaultdict(Counter)
        self.exceptions = []
        self.shortfalls = defaultdict(Counter)
        self.own_shortfalls = defaultdict(Counter)

    def add(self, rec, starts, distance, join):
        a, b = rec['A'], rec['B']
        law = law_name(rec['law'])
        retire = law.endswith(' retire')
        assert a != 'stub' and b in starts and law in LAWS
        assert (rec['d'], rec['join']) == (distance, join)
        pair = (a, b)
        row_key = (*pair, law)
        assert row_key not in self.rows
        self.rows.add(row_key)
        members, short = rec['A members'], rec['A short']
        own_births, births = rec['own births'], rec['births']
        own_gap, gap = rec['A shortfall'], rec['shortfall']
        length = rec['rounds']
        assert all(len(arr) == length for arr in (members, short, own_births, births, own_gap, gap))
        assert all(0 <= s <= m for s, m in zip(short, members))
        assert all(0 <= own <= total for own, total in zip(own_births, births))
        assert length <= 12
        starts_size = len(starts[a][0]) + len(starts[b][0]) + distance - 1
        if join == 'meeting':
            starts_size += distance
        assert rec['knots'] == sum(births) + starts_size
        for s, own, whole in zip(short, own_gap, gap):
            assert sum(own.values()) == s and not (Counter(own) - Counter(whole))
            assert all(int(g) > 0 for g in whole)
            self.shortfalls[law].update(whole)
            self.own_shortfalls[law].update(own)
        states = [own_state(m, s) for m, s in zip(members, short)]
        self.case[law].update(['cases', f"stop: {rec['ended']}", f'baseline length: {length}'])
        jams = [s == 'all short' for s in states[1:]]
        if any(jams):
            self.jammed_rows[law].add(pair)
        if any(x and y for x, y in zip(jams, jams[1:])):
            self.case[law]['raw consecutive all-short pairs'] += 1
        if all(jams) and jams:
            self.case[law]['raw always all-short after round one'] += 1
        if any(s > 0 for s in short[1:]):
            self.case[law]['raw some short after round one'] += 1
        else:
            self.no_short_rows[law].add(a)
        for r, state in enumerate(states, 1):
            self.by_round[law][r][state] += 1
        targets = expected_changes(b, distance, join, starts)
        assert {c['at']: c['distance'] for c in rec['changes']} == {k: d for k, (d, _) in targets.items()}
        assert len({c['at'] for c in rec['changes']}) == len(rec['changes'])
        if pair in NAMED_TRIALS or pair == ('source', 'ring'):
            self.trial_rows[str(row_key)] = {
                'baseline shortfall': dict(sum((Counter(gaps) for gaps in gap), Counter())),
                'baseline own members': members,
                'baseline own short': short,
                'changes heard': {c['at']: [c['distance'], c['heard'], c['jammed without'], c['jammed with']]
                                  for c in rec['changes'] if c['heard'] is not None},
            }
        thresholds = {2: (set(), set()), 3: (set(), set())}
        for c in rec['changes']:
            self.add_change(rec, c, law, retire, pair, states, thresholds, targets[c['at']][1])
        for threshold, (risks, hearings) in thresholds.items():
            key = law + f' {threshold}+'
            no_wait = {r for r in risks if members[r - 1] and (not short[r - 1] or retire)}
            for round_no in risks:
                self.risk_by_round[key][round_no][states[round_no - 1]] += 1
                if round_no in no_wait:
                    self.no_wait_risk_receivers[key][round_no].add(a)
            for round_no in hearings:
                self.heard_by_round[key][round_no][states[round_no - 1]] += 1
            if risks:
                self.case[law][f'pairs with a {threshold}+ change'] += 1
                if any(r > 1 for r in no_wait):
                    self.case[law][f'pairs with live no-wait round after round one while a {threshold}+ change is at risk'] += 1
            if hearings:
                self.case[law][f'pairs hearing a {threshold}+ change'] += 1
                if hearings & no_wait:
                    self.case[law][f'pairs with a {threshold}+ hearing in a live no-wait baseline round'] += 1
                    self.no_wait_hearing_receivers[key].add(a)

    def add_change(self, rec, change, law, retire, pair, states, thresholds, target_loose):
        _, b = pair
        name, d, heard = change['at'], change['distance'], change['heard']
        available = change['rounds']
        assert 0 < available <= rec['rounds']
        assert heard is None or 1 <= heard <= available
        groups = [self.changes[law][k] for k in keys(d)]
        for counts in groups:
            counts.update(['attempted', f'common horizon: {available}'])
        sign = 'bar' if name.startswith('b') else 'add'
        target = 'link' if 'L' in name else 'sender'
        if d >= 3:
            self.sign[law][f'{sign} {target} attempted'] += 1
            if sign == 'bar':
                self.barring[law][f'{target_loose} usable distinctions before barring, attempted'] += 1
            if b == 'stub':
                self.stub[law]['attempted'] += 1
            if pair[0] in ('ring', 'copier'):
                self.bench_horizons[law][f'{pair[0]} horizon {available}'] += 1
        if d >= 2:
            for threshold, (risks, hearings) in thresholds.items():
                if d >= threshold:
                    risks.update(range(1, (heard or available) + 1))
                    if heard:
                        hearings.add(heard)
            for r in range(2, (heard or available) + 1):
                state = states[r - 1]
                for counts in groups:
                    counts[f'at-risk comparison-rounds: {state}'] += 1
                    if not retire and state in ('some short', 'all short') and r != heard:
                        counts['baseline wait but no first hearing'] += 1
        if heard is None:
            return
        i = heard - 1
        short_without = states[i] in ('some short', 'all short')
        jam_without = states[i] == 'all short'
        short_with = change['A short with'][i] > 0
        jam_with = change['jammed with']
        assert change['waiting own without'] == short_without and change['waiting own with'] == short_with
        assert change['jammed without'] == jam_without and (not jam_with or short_with)
        assert change['jammed without, round before'] == (states[i - 1] == 'all short' if i else None)
        altered_births = change['own births with']
        assert len(altered_births) == len(change['A short with'])
        assert available == min(len(altered_births), rec['rounds'])
        first_count_difference = next((r for r, (x, y) in enumerate(
            zip(rec['own births'][:available], altered_births), 1) if x != y), None)
        assert first_count_difference is None or first_count_difference >= heard
        if not retire and d >= 3 and law in ONE_FEWER and not (short_without or short_with):
            self.exceptions.append(detail(rec, change))
        if d >= 2 and not retire and jam_with and not jam_without:
            self.starting_jam_senders[law][str((d, b))] += 1
        before_short = bool(i and (rec['A short'][i - 1] or change['A short with'][i - 1])) and not retire
        ever_short = bool(any(rec['A short'][:i]) or any(change['A short with'][:i])) and not retire
        for counts in groups:
            counts.update(['heard', f'heard round: {heard}', f'lag: {heard - d}',
                           f'hearing baseline: {states[i]}',
                           'count first differs at hearing' if first_count_difference == heard else
                           'count first differs later' if first_count_difference else 'count agrees through end',
                           f'all short: {transition(jam_without, jam_with)}',
                           f'some short: {transition(short_without, short_with)}',
                           f'wait: {transition(short_without and not retire, short_with and not retire)}',
                           f'jam: {transition(jam_without and not retire, jam_with and not retire)}'])
            if before_short:
                counts['own wait in immediately preceding round in either growth'] += 1
            if ever_short:
                counts['own wait before hearing in either growth'] += 1
            if short_without and short_with and not retire and rec['A short'][i] == change['A short with'][i]:
                counts['same positive number of own waiters at hearing'] += 1
        if d >= 2:
            self.near_hearers[law].add(pair)
            if pair[0] in ('ring', 'copier'):
                self.bench_receivers[law][f'{pair[0]} at {d} steps'] += 1
        if d >= 3:
            self.what_heard[law][(*pair, name)] = heard
            self.sign[law][f'{sign} {target} heard'] += 1
            if sign == 'bar':
                self.barring[law][f'{target_loose} usable distinctions before barring, heard'] += 1
            if b == 'stub':
                self.stub[law]['heard'] += 1

    def summarize(self, starts):
        law_cases = {}
        for law, case in self.case.items():
            jammed = self.jammed_rows[law]
            heard = self.what_heard[law]
            per_receiver = defaultdict(set)
            for a, b, change in heard:
                per_receiver[a].add(b)
                self.training_hits[law][(a, b)] += 1
            receiver_panel = {a for a, b, key in self.rows if key == law}
            sender_panel = {b for a, b, key in self.rows if key == law}
            case['distinct receivers'] = len(receiver_panel)
            case['distinct senders'] = len(sender_panel)
            case['raw all-short pairs after round one'] = len(jammed)
            case['raw all-short pairs hearing a 2+ change'] = len(jammed & self.near_hearers[law])
            case['raw all-short pairs hearing a 3+ change'] = len(jammed & {k[:2] for k in heard})
            law_cases[law] = {
                'counts': case,
                'receivers hearing 3+ and their senders': {a: sorted(bs) for a, bs in per_receiver.items()},
                'receivers sited at three loose distinctions': sorted(
                    a for a in receiver_panel if start_counts(*starts[a])[0][starts[a][1]] == 3),
                'receivers with no own short knot after round one in at least one case': sorted(self.no_short_rows[law]),
            }
        made, record = self.what_heard['ONE-FEWER'], self.what_heard['REC-ONE-FEWER']
        shared = made.keys() & record.keys()
        only_made, only_record = made.keys() - record.keys(), record.keys() - made.keys()
        return {
            'cases': law_cases,
            'baseline rounds by own short status': self.by_round,
            'distinct at-risk pair-rounds by baseline own short status': self.risk_by_round,
            'distinct first-hearing pair-rounds by baseline own short status': self.heard_by_round,
            'distinct live receivers without waiting by threshold and law': {
                key: {'at risk after round one': sorted(set().union(*(names for r, names in rounds.items() if r > 1))),
                      'at risk at observed hearing round numbers':
                          sorted(set().union(*(names for r, names in rounds.items() if r in self.heard_by_round[key]))),
                      'at an actual hearing': sorted(self.no_wait_hearing_receivers[key])}
                for key, rounds in self.no_wait_risk_receivers.items()
            },
            'changes': self.changes,
            'sign and target for 3+ changes': self.sign,
            '3+ barred changes by usable count before barring': self.barring,
            '3+ stub changes': self.stub,
            '2+ hearings by the ring and the two-knot part': self.bench_receivers,
            '3+ horizons for the ring and the two-knot part': self.bench_horizons,
            'changes starting a whole own-roster jam by change distance and sender': self.starting_jam_senders,
            '3+ one-fewer waiting exceptions': self.exceptions,
            'shortfalls across unchanged growths': self.shortfalls,
            'own shortfalls across unchanged growths': self.own_shortfalls,
            '3+ record versus made': {
                'union': len(made.keys() | record.keys()), 'both': len(shared),
                'only made': len(only_made), 'only record': len(only_record),
                'shared with a different first round': sum(made[k] != record[k] for k in shared),
                'only made cases': sorted(only_made), 'only record cases': sorted(only_record),
            },
            '3+ known trial overlaps': {
                law: {'trial pairs': {str(pair): cs[pair] for pair in sorted(NAMED_TRIALS)},
                      'reverse of ring-to-source': cs['source', 'ring'],
                      'hearings excluding named pairs': sum(n for p, n in cs.items() if p not in NAMED_TRIALS),
                      'small-pair hearings potentially in two unidentified trials':
                          sum(sorted((n for (a, b), n in cs.items() if a[0] == b[0] == 'g'), reverse=True)[:2])}
                for law, cs in self.training_hits.items()
            },
            'named trial rows': self.trial_rows,
        }


def run(limit):
    starts = catalogue()
    senders = list(starts)
    pairs = list(product(senders[:-1], senders))
    sample = set(random.Random(SEED).sample(pairs, 400))
    forms = defaultdict(list)
    for name, (places, root) in starts.items():
        if name != 'stub':
            forms[sited_fingerprint(places, root)].append(name)
    duplicate_forms = [names for names in forms.values() if len(names) > 1]
    representatives = {alias: names[0] for names in duplicate_forms for alias in names}
    sample_control = Panel()
    distinct_control = Panel()
    out = {'sample seed': SEED, 'panels': {}, 'identical sited starts': duplicate_forms}
    assert {path.name for path in STUDY.glob('jam*.gz')} == {v[0] for v in PANELS.values()}
    for panel_name, (filename, distance, join) in PANELS.items():
        panel = Panel()
        repeated = {}
        agreement = 0
        path = STUDY / filename
        with gzip.open(path, 'rt') as stream:
            for line in islice(stream, limit):
                record = json.loads(line)
                panel.add(record, starts, distance, join)
                a, b = record['A'], record['B']
                ca, cb = representatives.get(a, a), representatives.get(b, b)
                if a in representatives or b in representatives:
                    new_key = (ca, cb, law_name(record['law']))
                    semantic = {k: v for k, v in record.items() if k not in ('A', 'B', 'seconds')}
                    identity = hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()
                    if new_key in repeated:
                        assert repeated[new_key] == identity, new_key
                        agreement += 1
                    repeated[new_key] = identity
                if panel_name == 'meeting_3':
                    if (a, b) in sample:
                        sample_control.add(record, starts, distance, join)
                    if (a, b) == (ca, cb):
                        distinct_control.add(record, starts, distance, join)
        if limit is None:
            expected = pairs if panel_name == 'meeting_3' else sample
            assert panel.rows == {(*pair, law) for pair in expected for law in LAWS}
        out['panels'][panel_name] = panel.summarize(starts)
        out['panels'][panel_name]['file'] = filename
        out['panels'][panel_name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        out['panels'][panel_name]['structurally repeated rows verified'] = agreement
    if limit is None:
        assert sample_control.rows == {(*pair, law) for pair in sample for law in LAWS}
        assert len(distinct_control.rows) == (len(forms) * (len(forms) + 1) * len(LAWS))
    out['panels']['meeting_3_sample_control'] = sample_control.summarize(starts)
    out['panels']['meeting_3_distinct_starts'] = distinct_control.summarize(starts)
    out['one-fewer meeting totals'] = {}
    for threshold in ('2+', '3+'):
        totals = Counter()
        for name in ('meeting_2_sample', 'meeting_3', 'meeting_5_sample'):
            panel = out['panels'][name]
            for law in ONE_FEWER:
                key = law + ' ' + threshold
                hearings = panel['distinct first-hearing pair-rounds by baseline own short status'].get(key, {})
                risks = panel['distinct at-risk pair-rounds by baseline own short status'].get(key, {})
                totals.update(panel['changes'].get(law, {}).get(threshold, {}))
                for r, counts in hearings.items():
                    totals['distinct hearing pair-rounds'] += sum(counts.values())
                    totals['distinct hearing pair-rounds, live without waiting'] += counts['no short']
                    totals['distinct hearing pair-rounds, no own members'] += counts['no members']
                for r, counts in risks.items():
                    if r > 1:
                        totals['distinct at-risk pair-rounds after round one'] += sum(counts.values())
                        totals['distinct at-risk pair-rounds, live without waiting, after round one'] += counts['no short']
                        totals['distinct at-risk pair-rounds, no own members, after round one'] += counts['no members']
                    if r in hearings:
                        totals['distinct at-risk pair-rounds at observed hearing rounds'] += sum(counts.values())
                        totals['distinct at-risk pair-rounds at observed hearing rounds, live without waiting'] += counts['no short']
                        totals['distinct at-risk pair-rounds at observed hearing rounds, no own members'] += counts['no members']
        out['one-fewer meeting totals'][threshold] = totals
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='rows per input file for a timed prefix')
    parser.add_argument('--output', type=Path, help='write the complete accounting as JSON')
    args = parser.parse_args()
    result = run(args.limit)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    for name, data in result['panels'].items():
        print(name, sum(c['counts']['cases'] for c in data['cases'].values()), 'rows')
