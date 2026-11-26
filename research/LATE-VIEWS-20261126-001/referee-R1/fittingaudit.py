"""Read the fitting archives, reconstruct their admission, and check both views."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
from itertools import combinations, pairwise
import json
from math import comb
from pathlib import Path
import resource
from time import perf_counter


STUDY = Path(__file__).resolve().parents[1]
RESEARCH = STUDY.parent
LOOK = RESEARCH / 'LOOK-ALIKE-20261126-001'
BOUND = RESEARCH / 'SETTLE-BOUND-20261126-001'
READINGS = ('sig0', 'sig1')


@dataclass(frozen=True)
class Archive:
    law: str
    horizon: int
    path: Path
    table: str


FITTING = {
    'one to four, not-all-equal': Archive('nae', 20, LOOK / 'phase1_grown.jsonl.gz', 'check_1to4_nae'),
    'five, not-all-equal': Archive('nae', 24, BOUND / 'grown_g5_nae.jsonl.gz', 'check_5_nae'),
    'five, parity': Archive('parity', 24, BOUND / 'grown_g5_par.jsonl.gz', 'check_5_parity'),
}


@dataclass(frozen=True)
class Inventory:
    loose: tuple
    groups: tuple
    cells: tuple
    leftovers: int | None
    pieces: tuple
    stratum: str | None

    def disposition(self, law):
        if self.leftovers is None:
            return 'stall'
        if sum(self.loose) == 0:
            return 'none'
        if sum(self.loose) == 1 and law == 'parity':
            return 'one loose'
        if any(cyclic for cyclic, _ in self.pieces):
            return 'a piece with a cycle'
        return 'predicted'

    def relay_count(self, law):
        if law == 'parity' and len(self.pieces) == 1:
            return 0
        return sum(chains == 0 for _, chains in self.pieces)


def archive_rows(path):
    with gzip.open(path, 'rt') as stream:
        yield from map(json.loads, stream)


def case_key(record):
    return len(record['stars']), record['index']


def table(name):
    return json.loads((STUDY / 'fitting' / f'{name}.json').read_text())


def closed(record):
    return record['end'].startswith('closes at round ')


def sum_counts(reading):
    return sum(number for _, number in reading)


def view(row, reading):
    if reading == 'sig0':
        return {tuple(kind): number for kind, number in row[reading]}
    return {(tuple(kind), tuple(map(tuple, parents))): number
            for (kind, parents), number in row[reading]}


def differences(numbers):
    return [following - previous for previous, following in pairwise(numbers)]


def observed_dimension(numbers, largest=4):
    if len(numbers) < 10:
        return None
    tail = numbers[-8:]
    for dim in range(1, largest + 1):
        if len(tail) >= 2 and len(set(tail)) == 1 and tail[0] > 0:
            return dim
        tail = differences(tail)
    return None


def outcome(record):
    if record['end'].startswith('stalls'):
        return 'stalls'
    if closed(record):
        return 'closes'
    numbers = [row['n'] for row in record['rows']]
    dim = observed_dimension(numbers)
    if dim is not None:
        return f'dim {dim}'
    if len(numbers) >= 10:
        ratios = [Fraction(b, a) for a, b in pairwise(numbers[-5:])]
        if min(ratios) > Fraction(21, 20) and max(ratios) - min(ratios) < Fraction(1, 100):
            return f'rate {float(ratios[-1]):.2f}'
    return 'unread'


def recorded_kind(record):
    kind = outcome(record)
    assert record['kind'] == kind, (case_key(record), record['kind'], kind)
    return 'rate' if kind.startswith('rate ') else kind


def roster(stars):
    holders = defaultdict(list)
    for name, knot in enumerate(stars):
        for distinction in knot:
            holders[distinction].append(name)

    meeting = [set() for _ in stars]
    loose = [0] * len(stars)
    for holders_of_one in holders.values():
        if len(holders_of_one) == 1:
            (a,) = holders_of_one
            loose[a] += 1
        else:
            a, b = holders_of_one
            meeting[a].add(b)
            meeting[b].add(a)

    live = {name for name, count in enumerate(loose) if count}
    raw_blocks = [frozenset(names & live) for names in meeting]
    pair_counts = Counter(pair for block in raw_blocks for pair in combinations(sorted(block), 2))
    pairwise_sets = []
    for size in range(len(live), 2, -1):
        for names in combinations(sorted(live), size):
            members = frozenset(names)
            if (not any(members < other for other in pairwise_sets)
                    and all(pair in pair_counts for pair in combinations(names, 2))):
                pairwise_sets.append(members)
    cells = tuple(cell for cell in pairwise_sets if not any(cell <= group for group in raw_blocks))
    groups = cells + tuple(frozenset(pair) for pair in pair_counts
                           if not any(set(pair) <= cell for cell in cells))
    demand = Counter(name for group in groups for name in group)
    leftover_at = {name: loose[name] - demand[name] for name in live}
    if any(count < 0 for count in leftover_at.values()):
        return Inventory(tuple(loose), groups, cells, None, (), None)

    unique = {group for group in raw_blocks if len(group) >= 2}
    blocks = {group for group in unique if not any(group < other for other in unique)
              and not any(group <= cell for cell in cells)}
    block_overlap = any(len(block & cell) >= 2 for block in blocks for cell in cells)
    cell_overlap = max((len(a & b) for a, b in combinations(cells, 2)), default=0)
    if cells:
        if cell_overlap >= 2:
            stratum = 'group cells sharing two knots'
        elif block_overlap:
            stratum = 'a block meeting a group cell in two knots'
        elif cell_overlap == 1:
            stratum = 'group cells sharing a knot'
        else:
            stratum = 'group cells'
    elif max(pair_counts.values(), default=0) >= 2:
        stratum = 'repeated blocks only'
    elif sum(loose) == 1:
        stratum = 'one loose distinction'
    else:
        stratum = 'proved class'

    pieces = []
    unseen = set(live)
    connections = tuple(blocks) + cells
    while unseen:
        component = {min(unseen)}
        meeting_sets = set()
        while True:
            enlarged = set(component)
            for group in connections:
                if group & component:
                    enlarged.update(group)
                    meeting_sets.add(group)
            if enlarged == component:
                break
            component = enlarged
        unseen.difference_update(component)
        rank = sum(len(group) - 1 for group in meeting_sets) - len(component) + 1
        filled = sum(len(block & cell) - 1 for block in blocks & meeting_sets for cell in cells
                     if len(block & cell) >= 2)
        chains = sum(leftover_at[name] * max(3 - loose[name], 0) for name in component)
        pieces.append((rank != filled, chains))

    return Inventory(tuple(loose), groups, cells, sum(leftover_at.values()), tuple(pieces), stratum)


def parity_span(stars):
    distinctions = sorted(set().union(*map(set, stars)))
    names = {distinction: i for i, distinction in enumerate(distinctions)}
    rules = [sum(1 << names[d] for d in knot) for knot in stars]
    span = {0}
    for rule in rules:
        span |= {previous ^ rule for previous in span}
    return distinctions, rules, span


def violates_parity_knot_test(stars):
    """Check whether another independent parity equation survives on a knot's places."""
    _, rules, span = parity_span(stars)
    return any(rule != combination and combination & ~rule == 0
               for rule in rules for combination in span - {0})


def cuts_against_loose(stars):
    """Find start knots whose removal leaves some other knot with no path to a loose distinction."""
    loose_marker = len(stars)
    holders = defaultdict(list)
    meeting = [set() for _ in range(loose_marker + 1)]
    for knot, distinctions in enumerate(stars):
        for distinction in distinctions:
            holders[distinction].append(knot)
    for names in holders.values():
        a, b = names if len(names) == 2 else [names[0], loose_marker]
        meeting[a].add(b)
        meeting[b].add(a)
    failures = []
    for removed in range(loose_marker):
        pending = [loose_marker]
        reached = {loose_marker}
        while pending:
            new = meeting[pending.pop()] - reached - {removed}
            reached.update(new)
            pending.extend(new)
        if len(reached) != loose_marker:
            failures.append(removed)
    return failures


def parity_certificates(stars, expected_failures):
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    distinctions, rules, span = parity_span(stars)
    checked = []
    seen = []
    for index, rule in enumerate(rules):
        supported_equations = sorted(equation for equation in span if equation and equation & ~rule == 0)
        if len(supported_equations) == 1:
            continue
        seen.append(index)
        positions = {f'x{distinction}': 1 << position for position, distinction in enumerate(distinctions)
                     if rule & (1 << position)}
        shown = tuple(positions)

        def allowed(state):
            mask = sum(positions[name] for name, value in state.items() if value)
            return all((mask & equation).bit_count() % 2 == 0 for equation in supported_equations)

        projected = Relation.from_predicate(shown, allowed)
        result = check_knot(projected, shown[:-1], shown[-1])
        assert result.binding and not result.loss_on_erasure and result.coexistence
        checked.append({'start knot position': index,
                        'coexisting projected assignments': len(projected.rows),
                        'surviving proper-subset parity constraints': [
                            [name for name, position in positions.items() if equation & position]
                            for equation in supported_equations if equation != rule
                        ]})
    assert seen == expected_failures
    return checked


def run_admission(pilot):
    output = {}
    for name, archive in FITTING.items():
        if name == 'five, not-all-equal':
            continue
        tested = 0
        failures = []
        # The small archived records supply starts for the parity check only.
        for record in archive_rows(archive.path):
            stars = record['stars']
            cuts = cuts_against_loose(stars)
            assert bool(cuts) == violates_parity_knot_test(stars), case_key(record)
            tested += 1
            if not cuts:
                continue
            data = roster(stars)
            failures.append({'knots': len(stars), 'census index': record['index'], 'starting rules': stars,
                             'parity predictor disposition': data.disposition('parity'),
                             'failed knot tests': parity_certificates(stars, cuts)})
            if pilot is not None and len(failures) >= pilot:
                break
        output[name] = {'records checked': tested, 'starts violating parity knot test': failures}
    return output


def label_counts(names):
    return {' / '.join(map(str, key)): count for key, count in sorted(names.items())}


def first_difference(predicted, record, reading, strict=False):
    observed = record['rows']
    assert len(predicted) >= len(observed)
    for number, (p, o) in enumerate(zip(predicted, observed), 1):
        if view(p, reading) != view(o, reading):
            return number
    if strict:
        if record['end'].startswith('stalls'):
            return len(observed) + 1
        if closed(record):
            for number, p in enumerate(predicted[len(observed):], len(observed) + 1):
                if sum_counts(p[reading]):
                    return number
    return None


def settle(rows, reading, dim):
    """Use exact finite differences; any first unsupported birth kind is included."""
    samples = [view(row, reading) for row in rows]
    stencil = [(-1) ** (dim - i) * comb(dim, i) for i in range(dim + 1)]
    last_nonzero = dim
    for end in range(len(samples), dim, -1):
        contrast = Counter()
        for weight, sample in zip(stencil, samples[end - dim - 1:end], strict=True):
            for kind, count in sample.items():
                contrast[kind] += weight * count
        if any(contrast.values()):
            last_nonzero = end
            break
    cut = max(3, last_nonzero)
    return cut if cut <= len(rows) - 2 else None


def select(records, archive, pilot):
    bins = Counter()
    for record in records:
        data = roster(record['stars'])
        if pilot is not None:
            # Include early stops, each admitted dimension and both relay statuses.
            key = (record['kind'], data.disposition(archive.law), data.stratum,
                   bool(data.relay_count(archive.law)), record['end'])
            if bins[key] >= pilot:
                continue
            bins[key] += 1
        yield record, data


def two_leftovers(records):
    pairs = Counter()
    scopes = defaultdict(Counter)
    admissions = defaultdict(Counter)
    witnesses = {}
    for record in records:
        if record['kind'] != 'dim 2':
            continue
        data = roster(record['stars'])
        assert data.leftovers is not None
        rows = record['rows']
        offshoots = lambda row: sum(count for kind, count in row['sig0'] if kind[0] == 'offshoot')
        assert data.leftovers == offshoots(rows[0]), case_key(record)
        if data.leftovers != 2:
            continue
        tail = rows[-8:]
        offshoot_counts = tuple(map(offshoots, tail))
        join_slope = differences([view(row, 'sig0').get(('join', 2, 2, 4), 0) for row in tail])
        total_slope = differences([row['n'] for row in tail])
        assert len(set(offshoot_counts)) == 1 and len(set(total_slope)) == 1, case_key(record)
        pair = offshoot_counts[0], total_slope[0]
        pairs[pair] += 1
        scopes[len(record['stars'])][pair] += 1
        admissions[data.disposition('nae')][pair] += 1
        witnesses.setdefault(pair, {'knots': len(record['stars']), 'census index': record['index'],
                                    'stars': record['stars'], 'last eight total counts': [row['n'] for row in tail],
                                    'last eight offshoot counts': offshoot_counts,
                                    'last seven changes in two-parent two-fresh joins': join_slope})
    return {'offshoot count and slope / count': label_counts(pairs),
            'by starting knots': {n: label_counts(counter) for n, counter in sorted(scopes.items())},
            'by predictor disposition': {status: label_counts(counter) for status, counter in sorted(admissions.items())},
            'first census witness for each pair': label_counts(witnesses)}


def inventory_section(archive, pilot):
    facts = Counter()
    ends = Counter()
    counts = Counter()
    saved = Counter()
    classes = Counter()
    parity_invalid = Counter()
    control_opportunities = Counter()
    seen = set()
    truncated = []
    unread = []
    for record, data in select(archive_rows(archive.path), archive, pilot):
        key = case_key(record)
        assert key not in seen, key
        seen.add(key)
        assert tuple(record['loose']) == data.loose, key
        kind = recorded_kind(record)
        read = data.disposition(archive.law)
        rows = record['rows']
        horizon = len(rows)
        assert all(row['n'] == sum_counts(row['sig0']) == sum_counts(row['sig1']) for row in rows), key
        assert sum(row['n'] for row in rows) + len(record['stars']) == record['knots'], key
        if record['end'] == 'rounds':
            assert horizon == archive.horizon, key
        if record['end'] == 'bound':
            assert record['knots'] > 30_000, key
        if closed(record):
            assert record['end'] == f'closes at round {horizon + 1}', key
            assert rows[-1]['sig0'][0][0][2] == 0 and rows[-1]['n'] == 1, key
        counts[(kind, read)] += 1
        ends[(record['end'], read)] += 1
        saved[(horizon, read)] += 1
        facts['records'] += 1
        facts['saved rounds'] += horizon
        facts['saved births'] += record['knots'] - len(record['stars'])
        facts['dimension-labelled records'] += kind.startswith('dim ')
        if archive.law == 'parity' and violates_parity_knot_test(record['stars']):
            parity_invalid[(record['end'], read)] += 1
        if read != 'predicted':
            continue
        facts['accepted'] += 1
        facts['accepted saved rounds'] += horizon
        facts['accepted saved births'] += record['knots'] - len(record['stars'])
        classes[data.stratum] += 1
        if horizon == archive.horizon:
            facts['accepted with every birth round saved to horizon'] += 1
        if closed(record):
            facts['accepted with recorded closure before a complete horizon'] += horizon < archive.horizon
        if record['end'] == 'bound' and horizon < archive.horizon:
            truncated.append([*key, kind, horizon, record['knots']])
        if kind.startswith('dim '):
            facts['accepted with a dimension label'] += 1
        if kind == 'unread':
            unread.append([*key, horizon, record['knots'],
                           observed_dimension([row['n'] for row in rows], largest=6)])
        control_opportunities['no relay: at least one piece with a relay'] += data.relay_count(archive.law) > 0
        control_opportunities['no cells: at least one cell'] += bool(data.cells)
        control_opportunities['wrong knot law: a lone piece without chains'] += (
            len(data.pieces) == 1 and data.pieces[0][1] == 0
        )
        control_opportunities['dimension three or four and a cell'] += (
            kind in ('dim 3', 'dim 4') and bool(data.cells)
        )

    return {'source': str(archive.path.relative_to(RESEARCH.parent)), 'horizon': archive.horizon,
            'counts': dict(facts), 'label and disposition / count': label_counts(counts),
            'end and disposition / count': label_counts(ends), 'saved rounds and disposition / count': label_counts(saved),
            'accepted by stratum': dict(sorted(classes.items())),
            'failed parity knot test by end and disposition / count': label_counts(parity_invalid),
            'control opportunities within accepted starts': dict(control_opportunities),
            'accepted caps before horizon [knots in start, census index, label, rounds, knots after last round]': truncated,
            'accepted unread [knots in start, census index, rounds, knots after last round, wider finite-difference label]': unread}


def five_archive_overlap(pilot):
    left = archive_rows(LOOK / 'phase2_grown.jsonl.gz')
    right = archive_rows(BOUND / 'grown_g5_nae.jsonl.gz')
    counts = Counter()
    for a, b in zip(left, right, strict=True):
        assert case_key(a) == case_key(b)
        keys = ('stars', 'loose', 'graph', 'rows', 'end', 'kind', 'knots')
        counts['compared'] += 1
        counts['equal in every growth and census field'] += all(a[key] == b[key] for key in keys)
        if pilot is not None and counts['compared'] == pilot:
            break
    return dict(counts)


def summarize_law_swap(pilot):
    left = archive_rows(FITTING['five, not-all-equal'].path)
    right = archive_rows(FITTING['five, parity'].path)
    counts = Counter()
    rounds = Counter()
    for nae, parity in zip(left, right, strict=True):
        key = case_key(nae)
        assert key == case_key(parity) and nae['stars'] == parity['stars']
        if pilot is not None and counts['compared'] >= pilot:
            break
        counts['compared'] += 1
        inventory = roster(nae['stars'])
        if not closed(parity):
            assert nae['rows'] == parity['rows'] and nae['end'] == parity['end'], key
            counts['identical in both laws without a parity closure'] += 1
            continue
        end = len(parity['rows'])
        a_last, b_last = nae['rows'][end - 1], parity['rows'][-1]
        ap, bp = a_last['sig1'][0][0], b_last['sig1'][0][0]
        assert nae['rows'][:end - 1] == parity['rows'][:-1], key
        assert a_last['n'] == b_last['n'] == 1 and ap[1] == bp[1] and ap[0][:2] == bp[0][:2]
        assert ap[0][2] > 0 and bp[0][2] == 0
        counts['parity closures'] += 1
        counts['closures accepted by both laws'] += inventory.disposition('parity') == 'predicted'
        counts['closures accepted by not-all-equal only'] += inventory.disposition('parity') == 'one loose'
        counts['closures rejected as cyclic by both laws'] += inventory.disposition('nae') == 'a piece with a cycle'
        if inventory.disposition('nae') == 'predicted':
            rounds[end] += 1
    return {'counts': dict(counts), 'closing birth rounds for starts accepted under not-all-equal': dict(sorted(rounds.items()))}


def run_inventory(pilot):
    chosen = (record for archive in list(FITTING.values())[:2]
              for record, _ in select(archive_rows(archive.path), archive, pilot))
    return {'archives': {name: inventory_section(archive, pilot) for name, archive in FITTING.items()},
            'five-knot fit and earlier look-alike five-knot archive': five_archive_overlap(pilot),
            'five-knot comparison of laws': summarize_law_swap(pilot),
            'descriptive two-leftover result, not-all-equal dimension 2': two_leftovers(chosen)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=('inventory', 'admission'))
    parser.add_argument('--pilot', type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    started = perf_counter()
    if args.part == 'inventory':
        report = run_inventory(args.pilot)
    else:
        report = run_admission(args.pilot)
    report['pilot cases per bin'] = args.pilot
    report['elapsed seconds'] = round(perf_counter() - started, 3)
    report['peak RSS KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report['address space cap KiB'] = resource.getrlimit(resource.RLIMIT_AS)[0] // 1024
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
