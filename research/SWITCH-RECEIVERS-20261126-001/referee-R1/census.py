"""Recount the receiver archive using the saved own-birth and short-knot counts."""

import argparse
from ast import literal_eval
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from hashlib import file_digest
from itertools import combinations, islice, permutations, product
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
SENDERS = ('g1:3@0', 'g3:22@0', 'g6:122@0', 'g7:122@0', 'stub')
LAWS = ('CAP-3', 'CAP-4', 'CAP-5', 'REC-ONE-FEWER', 'ORD')
STEPS = (2, 3, 4, 5)
ROUND_LIMIT, KNOT_LIMIT = 16, 3000
PAIRS = tuple(combinations(SENDERS, 2))
SHARINGS = {
    1: (),
    3: ((0, 1),),
    6: ((0, 1), (0, 2)),
    7: ((0, 1), (0, 2), (1, 2)),
    13: ((0, 3), (1, 3), (2, 3)),
    14: ((0, 1), (0, 3), (1, 2)),
    15: ((0, 3), (1, 2), (1, 3), (2, 3)),
    16: ((0, 1), (0, 3), (1, 2), (2, 3)),
    17: ((0, 1), (0, 2), (0, 3), (1, 2), (2, 3)),
    18: ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)),
}


def tally(items):
    return dict(sorted(Counter(items).items()))


def parse_start(name):
    match = re.fullmatch(r'n([1-4]):g(\d+):([0-3]+)@(\d+)', name)
    if match is None:
        return None
    n, pattern, counts, site = match.groups()
    shares = SHARINGS[int(pattern)]
    loose = tuple(map(int, counts))
    assert len(loose) == int(n) and int(site) < int(n)
    return shares, loose, int(site)


def connected(n, shares):
    reached = {0}
    for _ in range(n - 1):
        for left, right in shares:
            if left in reached or right in reached:
                reached.update((left, right))
    return len(reached) == n


def sited_key(shares, loose, site):
    """Canonical key across all knot relabelings, including the designated site."""
    return min(
        (
            tuple(sorted(tuple(sorted((labels[a], labels[b]))) for a, b in shares)),
            tuple(sorted((labels[i], count) for i, count in enumerate(loose))),
            labels[site],
        )
        for labels in permutations(range(len(loose)))
    )


def roster_check(names):
    """Enumerate connected beginnings up to four knots independently of the record."""
    starters = [parse_start(name) for name in sorted(names)]
    observed = [sited_key(*start) for start in starters if start is not None]
    expected = set()
    for n in range(1, 5):
        pairs = tuple(combinations(range(n), 2))
        for count in range(n - 1, len(pairs) + 1):
            for shares in combinations(pairs, count):
                if not connected(n, shares):
                    continue
                degrees = [sum(knot in pair for pair in shares) for knot in range(n)]
                for loose in product(*(range(max(0, 3 - degree), 4) for degree in degrees)):
                    if any(loose):
                        expected.update(sited_key(shares, loose, site) for site in range(n))
    assert len(observed) == len(set(observed))
    assert set(observed) == expected
    assert {name for name in names if parse_start(name) is None} == {'ring', 'copier', 'source'}
    return tally(len(key[1]) for key in expected)


def first_difference(left, right):
    return next((r for r, (a, b) in enumerate(zip(left, right), 1) if a != b), None)


def first_present(values):
    return min((value for value in values if value is not None), default=None)


def sender_classes(vectors):
    groups = defaultdict(list)
    for sender, vector in zip(SENDERS, vectors):
        groups[vector].append(sender)
    return tuple(sorted(tuple(group) for group in groups.values()))


@dataclass
class Panel:
    name: str
    d: int
    law: str
    births: dict
    shorts: dict
    lengths: dict
    knots: dict
    stored_first: int | None
    stored_classes: tuple
    stored_stub_firsts: dict

    @classmethod
    def read(cls, row):
        runs = row['by sender']
        assert set(runs) == set(SENDERS)
        births = {s: tuple(runs[s]['own births']) for s in SENDERS}
        shorts = {s: tuple(runs[s]['A short']) for s in SENDERS}
        lengths = {s: runs[s]['rounds'] for s in SENDERS}
        knots = {s: runs[s]['knots'] for s in SENDERS}
        for s in SENDERS:
            assert 0 < len(births[s]) == len(shorts[s]) == lengths[s] <= ROUND_LIMIT
            assert all(x >= 0 for x in births[s] + shorts[s])
            assert runs[s]['rounds with the stub'] == min(lengths[s], lengths['stub'])
        first = row['first differs']
        assert row['rounds compared'] == min(lengths.values())
        assert first is None or 1 <= first <= min(lengths.values())
        short_before = None if first is None else any(any(series[:first - 1]) for series in shorts.values())
        assert row['own short before'] is short_before
        classes = tuple(sorted(tuple(sorted(group)) for group in row['classes']))
        assert sorted(s for group in classes for s in group) == sorted(SENDERS)
        assert (len(classes) == 1) == (first is None)
        stub_firsts = {s: runs[s]['differs from the stub'] for s in SENDERS}
        assert stub_firsts['stub'] is None
        return cls(row['A'], row['d'], row['law'], births, shorts, lengths, knots,
                   first, classes, stub_firsts)

    @property
    def common(self):
        return min(self.lengths.values())

    def no_prior_short(self, round_number, senders=SENDERS):
        return all(not any(self.shorts[s][:round_number - 1]) for s in senders)

    def compare(self):
        pair_firsts = {(a, b): first_difference(self.births[a], self.births[b]) for a, b in PAIRS}
        pair_first = first_present(pair_firsts.values())
        common_first = pair_first if pair_first is not None and pair_first <= self.common else None
        classes = sender_classes(tuple(self.births[s][:self.common] for s in SENDERS))
        assert (len(classes) == 1) == (common_first is None)
        if common_first is not None:
            assert self.stored_first is not None and self.stored_first <= common_first
        for group in self.stored_classes:
            assert any(set(group) <= set(count_group) for count_group in classes)
        for s, stored_round in self.stored_stub_firsts.items():
            raw_round = first_difference(self.births[s], self.births['stub'])
            assert stored_round is None or 1 <= stored_round <= min(self.lengths[s], self.lengths['stub'])
            if raw_round is not None:
                assert stored_round is not None and stored_round <= raw_round
        known_stored_first = first_present((self.stored_first, *self.stored_stub_firsts.values()))
        return Comparison(self, common_first, pair_first, pair_firsts, classes, known_stored_first)


@dataclass
class Comparison:
    panel: Panel
    common_first: int | None
    pair_first: int | None
    pair_firsts: dict
    count_classes: tuple
    earliest_by_recorded_comparisons: int | None


def band(first, d):
    if first is None:
        return 'unresolved'
    if first < d:
        return 'before d'
    if first <= 2 * d:
        return 'd through 2d'
    return 'after 2d'


def bands(firsts, d):
    counts = Counter(band(first, d) for first in firsts)
    return {key: counts[key] for key in ('before d', 'd through 2d', 'after 2d', 'unresolved')}


def opportunities(comparisons, r):
    """An eligible prefix has no difference or short own knot before round r."""
    counts = Counter()
    for comparison in comparisons:
        p = comparison.panel
        if p.common >= r:
            counts['all five reached'] += 1
            if p.no_prior_short(r):
                counts['all five reached without prior own shortness'] += 1
                if comparison.common_first is None or comparison.common_first >= r:
                    counts['all five reached with eligible count prefix'] += 1
                if p.stored_first is None or p.stored_first >= r:
                    counts['all five reached with eligible recorded signature prefix'] += 1
        available = [pair for pair in PAIRS if min(p.lengths[s] for s in pair) >= r]
        counts['pairs reached'] += len(available)
        if available:
            counts['receivers with a pair reached'] += 1
        stub_pairs = [pair for pair in available if 'stub' in pair]
        counts['stub pairs reached'] += len(stub_pairs)
        if stub_pairs:
            counts['receivers with a stub pair reached'] += 1
        eligible = [pair for pair in available if p.no_prior_short(r, pair)
                    and (comparison.pair_firsts[pair] is None or comparison.pair_firsts[pair] >= r)]
        counts['pairs with eligible count prefix'] += len(eligible)
        counts['stub pairs with eligible count prefix'] += sum('stub' in pair for pair in eligible)
        if eligible:
            counts['receivers with an eligible count pair'] += 1
    keys = ('all five reached', 'all five reached without prior own shortness',
            'all five reached with eligible count prefix', 'all five reached with eligible recorded signature prefix',
            'pairs reached', 'receivers with a pair reached', 'stub pairs reached',
            'receivers with a stub pair reached', 'pairs with eligible count prefix',
            'stub pairs with eligible count prefix', 'receivers with an eligible count pair')
    return {key: counts[key] for key in keys}


def by_round(comparisons, first_by):
    hits = []
    for c in comparisons:
        first = first_by(c)
        if first is not None and first > 2 * c.panel.d and c.panel.no_prior_short(first):
            hits.append((c, first))
    return hits


def curve_groups(hits):
    panels = [c.panel for c, _ in hits]
    if not panels:
        return {}
    equal_horizon = min(p.common for p in panels)
    sender_horizons = {s: min(p.lengths[s] for p in panels) for s in SENDERS}
    modes = {
        'complete recorded count vectors': lambda p: tuple(p.births[s] for s in SENDERS),
        'count vectors through shortest horizon per sender': lambda p: tuple(
            p.births[s][:sender_horizons[s]] for s in SENDERS),
        'count vectors through shortest horizon across all senders and receivers': lambda p: tuple(
            p.births[s][:equal_horizon] for s in SENDERS),
        'partition of senders by recorded signatures': lambda p: p.stored_classes,
    }
    result = {'shortest horizon across all senders and receivers': equal_horizon,
              'shortest horizon per sender': sender_horizons}
    for description, key in modes.items():
        groups = defaultdict(list)
        for p in panels:
            groups[key(p)].append(p.name)
        result[description] = sorted((sorted(group) for group in groups.values()), key=lambda g: (-len(g), g))
    return result


def alternating(series):
    return len(series) >= 3 and all(bool(a) != bool(b) for a, b in zip(series, series[1:]))


def hit_record(c, first):
    p = c.panel
    start = parse_start(p.name)
    site_data = {}
    if start is not None:
        shares, loose, site = start
        site_sharings = sum(site in pair for pair in shares)
        site_data = {'loose counts': loose, 'site loose': loose[site], 'site sharings': site_sharings,
                     'site places before joining': loose[site] + site_sharings, 'sharings': shares, 'site': site}
    return {
        'receiver': p.name, **site_data,
        'recorded first': p.stored_first, 'common count first': c.common_first,
        'pairwise count first': c.pair_first, 'common rounds': p.common,
        'recorded classes': p.stored_classes, 'count classes': c.count_classes,
        'stub firsts from recorded signatures': p.stored_stub_firsts,
        'stub firsts from counts': {s: first_difference(p.births[s], p.births['stub']) for s in SENDERS},
        'alternating own shortness from first difference':
            [s for s in SENDERS if alternating(p.shorts[s][first - 1:])],
    }


def audit_cell(panels, d):
    comparisons = [p.compare() for p in panels]
    pairs = defaultdict(Counter)
    pair_first_shortness = defaultdict(Counter)
    for c in comparisons:
        p = c.panel
        for pair in PAIRS:
            rounds = min(p.lengths[s] for s in pair)
            first = c.pair_firsts[pair]
            measures = pairs[' and '.join(pair)]
            measures['ended before 16'] += rounds < ROUND_LIMIT
            measures['unresolved before 16'] += first is None and rounds < ROUND_LIMIT
            measures['unresolved through 16'] += first is None and rounds == ROUND_LIMIT
            measures[band(first, d)] += 1
            if first is not None:
                branches = sum(any(p.shorts[s][:first - 1]) for s in pair)
                pair_first_shortness[band(first, d)][branches] += 1
    raw_common_hits = by_round(comparisons, lambda c: c.common_first)
    stored_hits = by_round(comparisons, lambda c: c.panel.stored_first)
    round_counts = Counter()
    for c in comparisons:
        p, first = c.panel, c.pair_first
        if first is None or first <= 2 * d:
            continue
        first_pairs = [pair for pair, seen in c.pair_firsts.items() if seen == first]
        if any(p.no_prior_short(first, pair) for pair in first_pairs):
            round_counts['any first pair without prior own shortness'] += 1
        if p.no_prior_short(first) and p.common >= first - 1:
            round_counts['all five without prior own shortness, known through preceding round'] += 1
        if p.no_prior_short(first) and p.common < first - 1:
            round_counts['no prior own shortness observed, all-five status censored'] += 1
    return {
        'receiver cells': len(panels),
        'individual runs': sum(len(p.lengths) for p in panels),
        'individual run horizons': tally(n for p in panels for n in p.lengths.values()),
        'individual runs ending before 16, above knot limit': sum(
            p.lengths[s] < ROUND_LIMIT and p.knots[s] > KNOT_LIMIT for p in panels for s in SENDERS),
        'individual runs ending before 16, at or below knot limit': sum(
            p.lengths[s] < ROUND_LIMIT and p.knots[s] <= KNOT_LIMIT for p in panels for s in SENDERS),
        'all-five horizons': tally(p.common for p in panels),
        'firsts by band from recorded signature summary, common': bands((p.stored_first for p in panels), d),
        'firsts by band from raw own-birth counts, common': bands((c.common_first for c in comparisons), d),
        'firsts by band from raw own-birth counts, pairwise': bands((c.pair_first for c in comparisons), d),
        'firsts by band from stored common and stored stub contrasts': bands(
            (c.earliest_by_recorded_comparisons for c in comparisons), d),
        'recorded common earliest first or sender partition differs from counts': {
            'first differs': sum(c.common_first != c.panel.stored_first for c in comparisons),
            'partition differs': sum(c.count_classes != c.panel.stored_classes for c in comparisons),
            'stub contrasts differ': sum(
                first_difference(p.births[s], p.births['stub']) != p.stored_stub_firsts[s]
                for p in panels for s in SENDERS if s != 'stub'),
        },
        'common first absent, pairwise count first present': [
            {'receiver': c.panel.name, 'common rounds': c.panel.common, 'first': c.pair_first}
            for c in comparisons if c.common_first is None and c.pair_first is not None],
        'stored common first absent, stored pairwise stub first present': [
            {'receiver': c.panel.name, 'common rounds': c.panel.common, 'first': c.earliest_by_recorded_comparisons}
            for c in comparisons if c.panel.stored_first is None and c.earliest_by_recorded_comparisons is not None],
        'pair counts by sender comparison': pairs,
        'pairwise first differences by number of sender runs with a prior short own knot': pair_first_shortness,
        'opportunities by round': {
            r: opportunities(comparisons, r) for r in range(1, max(ROUND_LIMIT, 4 * d + 3) + 1)},
        'recorded first when prior shortness absent': tally(
            p.stored_first for p in panels if p.stored_first is not None and p.no_prior_short(p.stored_first)),
        'switch firsts from recorded signatures': tally(first for _, first in stored_hits),
        'switch firsts from counts, common': tally(first for _, first in raw_common_hits),
        'switch counts from pairwise first differences by shortness check': dict(round_counts),
        'switch receivers from recorded signatures': [hit_record(c, first) for c, first in stored_hits],
        'switch receivers from counts, common': [c.panel.name for c, _ in raw_common_hits],
        'curves of switch receivers from recorded signatures': curve_groups(stored_hits),
    }


def load_panels(path, limit=None):
    with gzip.open(path, 'rt') as stream:
        return [json.loads(line) for line in islice(stream, limit)]


def sha256(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def rule_recount(path):
    cases = []
    for row in load_panels(path):
        if row['reading'] != 'classes':
            continue
        p = Panel.read(row)
        c = p.compare()
        a = int(p.name.split(':')[1][0])
        first, count_first = p.stored_first, c.common_first
        cases.append({'receiver site loose count': a, 'cap': row['cap'], 'd': p.d,
                      'passes recorded switch filter': first is not None and first > 2 * p.d and p.no_prior_short(first),
                      'passes count switch filter': count_first is not None and count_first > 2 * p.d
                      and p.no_prior_short(count_first),
                      **hit_record(c, first or p.common + 1)})
    return cases


def check_table(path, cells):
    """Compare the independent count reading with every published census table row."""
    cell_rows, receiver_rows = set(), set()
    for line in path.read_text().splitlines():
        if line.startswith('| '):
            fields = [field.strip() for field in line.split('|')[1:-1]]
            law = fields[0]
            if law not in LAWS:
                continue
            d = int(fields[1])
            cell = cells[law][d]
            assert int(fields[2]) == cell['receiver cells']
            assert tuple(map(int, fields[3].split('/'))) == tuple(
                cell['firsts by band from raw own-birth counts, common'].values())
            assert int(fields[4]) == len(cell['switch receivers from counts, common'])
            assert literal_eval(fields[5]) == cell['switch firsts from counts, common']
            assert (law, d) not in cell_rows
            cell_rows.add((law, d))
        elif re.fullmatch(r'CAP-[345], d = 3: \d+ switching receivers', line):
            law = line.split(',')[0]
        elif line.startswith('   n'):
            match = re.fullmatch(r'\s*(\S+)\s+first (\d+)\s+classes: (.*?)  alternate-short after with: (.*)', line)
            assert match is not None
            name, first, classes, alternating_senders = match.groups()
            hit = next(row for row in cells[law][3]['switch receivers from recorded signatures'] if row['receiver'] == name)
            assert int(first) == hit['common count first']
            assert tuple(tuple(c.split(',')) for c in classes.split(' | ')) == hit['count classes']
            assert literal_eval(alternating_senders) == hit['alternating own shortness from first difference']
            assert (law, name) not in receiver_rows
            receiver_rows.add((law, name))
    assert cell_rows == set(product(LAWS, STEPS))
    assert receiver_rows == {(law, name) for law in LAWS for name in cells[law][3]['switch receivers from counts, common']}
    return {'source': path.name, 'verified law-by-step rows': len(cell_rows),
            'verified receiver rows at three steps': len(receiver_rows)}


def census_recount(limit=None):
    source = HERE.parent / 'receivers_runs.jsonl.gz'
    panels_by_cell = defaultdict(list)
    for row in load_panels(source, limit):
        p = Panel.read(row)
        assert p.law in LAWS and p.d in STEPS
        panels_by_cell[p.law, p.d].append(p)
    for panels in panels_by_cell.values():
        assert len(panels) == len({p.name for p in panels})
    out = {'source': source.name, 'sha256': sha256(source),
           'scope': 'Every recorded receiver, law and separation, each with five recorded senders.',
           'observable': 'The archive saves complete own-birth counts and own-short counts per recorded round. '
                         'It saves the first differences and classes derived from birth signatures. '
                         'The per-round birth signatures are absent.',
           'common comparison': 'The common window ends at the earliest stop among the five sender runs.',
           'pairwise comparison': 'Each pair can be compared until that pair stops. '
                                  'A late difference still needs an eligible prefix. An unobserved round is unresolved.',
           'order': {'law': LAWS, 'd': STEPS, 'senders': SENDERS}, 'cells': {}}
    if limit is None:
        assert set(panels_by_cell) == set(product(LAWS, STEPS))
        names = {p.name for p in panels_by_cell[LAWS[0], STEPS[0]]}
        for panels in panels_by_cell.values():
            assert len(panels) == 646 and {p.name for p in panels} == names
        out['independently enumerated sited starts by knot count'] = roster_check(names)
        out['additional starts from the bench'] = ['ring', 'copier', 'source']
    for (law, d), panels in panels_by_cell.items():
        out['cells'].setdefault(law, {})[d] = audit_cell(panels, d)
    if limit is None:
        out['published table check'] = check_table(HERE.parent / 'receivers_table.md', out['cells'])
    out['cap of three count vectors'] = {}
    for d in STEPS:
        comparisons = [p.compare() for p in panels_by_cell.get(('CAP-3', d), [])]
        hits = by_round(comparisons, lambda c: c.panel.stored_first)
        if not hits:
            continue
        out['cap of three count vectors'][d] = {
            s: {p.name: {'own births': p.births[s], 'own short': p.shorts[s], 'final knots': p.knots[s]}
                for c, _ in hits for p in [c.panel]}
            for s in SENDERS
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='Measure the same analysis on a prefix of receiver rows.')
    parser.add_argument('--output', type=Path, help='Write the full recount to this JSON file.')
    args = parser.parse_args()
    out = census_recount(args.limit)
    path = HERE.parent / 'rule_runs.jsonl.gz'
    out['rule archive'] = {'source': path.name, 'sha256': sha256(path), 'cases': rule_recount(path)}
    if args.output:
        args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(sum(cell['receiver cells'] for law in out['cells'].values() for cell in law.values()), 'receiver rows')


if __name__ == '__main__':
    main()
