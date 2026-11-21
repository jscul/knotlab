"""Literal local gates, physical engine replay and parity continuation witnesses."""

from collections import Counter, defaultdict, deque
import gzip
from itertools import combinations, product
import json
import sys

import numpy as np

from census_exact_rates import owners
from census_rate_tables import as_tuple, parity_table
from census_stages import OUTPUT, ROOT, following, mask_of, width
from census_weighted import canonical_weighted
from census_rates import canonical_pair_table
from census_reached import named_rows
from model import parity_counts, spanned
from census_replay import check_source, literal_counts


ENGINE = 'NAE-GROWTH-20261119-001B'
sys.path.insert(0, str(ROOT / 'experiments' / ENGINE / f'{ENGINE}-E001_nae'))
import naelib


def native(rows, law):
    state = naelib.S.from_junctions(rows)
    rule = naelib.nae_rule if law == 'nae' else naelib.parity_rule
    outcome = state.step(rule(naelib.F.fewest), None)
    if outcome is None:
        return 'stall', rows, ()
    if not outcome['new']:
        return 'closed', rows, ()
    n = len(rows)
    new_rows = tuple(tuple(s) for s in state.bits_of)
    births = []
    for i in range(n, len(new_rows)):
        original = new_rows[i][:state.parents[i]]
        parents = tuple(sorted(next(j for j in state.owner[x] if j != i) for x in original))
        births.append((parents, state.fresh[i]))
    return 'births', new_rows, tuple(births)


def replay_allocation(before, wanted, alternative, wanted_parents, actual_parents):
    old = owners(before)
    n = width(before)
    placed = defaultdict(deque)
    for key, row in zip(actual_parents, alternative[len(before):], strict=True):
        placed[key].append(row)
    move = {}
    for (parents, price), row in zip(wanted_parents, wanted[len(before):], strict=True):
        target = placed[(tuple(parents), price)].popleft()
        old_slots = {old[x][0]: x for x in target if x < n}
        fresh = sorted(x for x in row if x >= n)
        target_fresh = sorted(x for x in target if x >= n)
        move.update((x, old_slots[old[x][0]]) for x in row if x < n)
        move.update(zip(fresh, target_fresh, strict=True))
    mapped = tuple(move.get(i, i) for i in range(width(wanted)))
    assert sorted(mapped) == list(range(width(wanted)))
    assert named_rows(wanted, mapped) == named_rows(alternative)


def actual_cases(records, law):
    checked = Counter()
    for source in records:
        before = tuple(map(tuple, source['source_rows']))
        check_source(before, law, source['source_width'])
        checked['literal_sources'] += 1
        for age, expected in enumerate(source['attempts'], start=1):
            status, reached, births = native(before, law)
            assert status == expected, (law, before, expected, status)
            checked['checked_cuts'] += 1
            if status != 'births':
                break
            row = source['stages'][age - 1]
            physical = tuple(map(tuple, row['rows']))
            replay_allocation(before, physical, reached, row['recorded_births'], births)
            checked['old_fresh_allocation_replays'] += 1
            before = physical
        if source['stages']:
            last = source['stages'][-1]
            status, _, births = native(tuple(map(tuple, last['rows'])), law)
            assert (status, len(births)) == (last['next_status'], last['next_birth_count'])
            checked['last_stage_counts'] += 1
        if source['source_components'] > 1:
            checked['source_unions'] += 1
    return dict(checked)


def membership_matrix(multiplicity, arity, pinned):
    vals = np.empty((3,) * arity, dtype=object)
    for settings in np.ndindex(vals.shape):
        fixed = set(settings) - {0}
        if len(fixed) > 1 or fixed and not set(pinned) <= fixed:
            vals[settings] = 0
        else:
            vals[settings] = 1 if fixed else 1 << (multiplicity - len(pinned))
    return vals


def count_with_pins(rows, newest, pins):
    """Directly sum latest-holder modes before the complete older-mode sum."""
    youngest = set(newest)
    older = [h for h in range(len(rows)) if h not in youngest]
    settings = np.array(list(product(range(3), repeat=len(older))), dtype=int).T
    index = dict(zip(older, settings, strict=True))
    totals = np.ones(settings.shape[-1], dtype=object)
    shares = Counter(owners(rows).values())
    fix = defaultdict(list)
    for name, value in pins.items():
        fix[owners(rows)[name]].append(value + 1)
    contributions = {scope: membership_matrix(q, len(scope), fix[scope]) for scope, q in shares.items()}
    pending = defaultdict(list)
    for scope, factor in contributions.items():
        younger = [h for h in scope if h in youngest]
        if younger:
            assert len(younger) == 1
            pending[younger[0]].append((scope, factor))
        else:
            totals *= factor[tuple(index[h] for h in scope)]
    for h in older:
        signs = np.array([1, -1, -1], dtype=object)
        totals *= signs[index[h]]
    for new in newest:
        fused = np.zeros(len(totals), dtype=object)
        for local in (0, 1, 2):
            weight = np.ones(len(totals), dtype=object)
            for scope, factor in pending[new]:
                weight *= factor[tuple(local if h == new else index[h] for h in scope)]
            fused += weight if local == 0 else -weight
        totals *= fused
    return int(totals.sum())


def compare_rates(records, measure, law):
    verified = Counter()
    for entry in measure['records']:
        stage = records[entry['source_index']]['stages'][entry['age'] - 1]
        rows = tuple(map(tuple, stage['rows']))
        n = stage['width']
        key = as_tuple(entry['table_key'])
        if law == 'parity':
            total, counts = parity_counts(rows)
            assert total == entry['allowed_states']
            assert key == canonical_weighted(n, total, counts).key
            verified['independent_parity_tables'] += 1
            if n <= 10:
                assert (total, counts) == literal_counts(rows, law)
                verified['literal_pair_tables'] += 1
            continue
        total = entry['allowed_states']
        counts = dict(zip(combinations(range(n), 2), entry['disagreement_counts'], strict=True))
        if n <= 10:
            assert (total, counts) == literal_counts(rows, law)
            verified['literal_pair_tables'] += 1
        if n <= 12 and verified['earlier_canonical_key_checks'] < 128:
            older = canonical_pair_table(n, total, counts)
            assert (key, entry['table_automorphisms']) == (older.key, older.automorphisms)
            verified['earlier_canonical_key_checks'] += 1
        if entry['contraction_work']:
            assert count_with_pins(rows, stage['youngest'], {}) == total
            marks = ((0, 1), (0, n - 1), (n - 2, n - 1))
            for i, j in marks:
                assert 2 * count_with_pins(rows, stage['youngest'], {i: 0, j: 1}) == counts[i, j]
            verified['independent_large_word_counts'] += 1
            verified['independent_large_pair_counts'] += len(marks)
    return dict(verified)


def separating_check(left, right, width):
    if left == right:
        return None
    for k in range(1, width + 1):
        for names in combinations(range(width), k):
            m = mask_of(names)
            if spanned(m, left) != spanned(m, right):
                return names


def trace_parity(result):
    kept = {}
    for label in ('different_next_birth_counts', 'same_states_different_births'):
        witness = result['minima'][label]
        left, right = (tuple(map(tuple, s['stage_rows'])) for s in witness['arms'])
        n = width(left)
        p, a = parity_table(left)
        q, b = parity_table(right)
        assert p.key == q.key
        assert p.key == as_tuple(witness['table_key'])
        # The stored common names, not just another table isomorphism, give equality.
        (A, P), (B, Q) = parity_counts(left), parity_counts(right)
        assert all(P[ij] * B == Q[ij] * A for ij in P)
        marker = separating_check(a, b, n)
        if label == 'same_states_different_births':
            assert a == b
        record = {'same_named_states': a == b, 'common_basis_if_equal': a if a == b else None,
                  'least_full_marginal_order': None if marker is None else len(marker),
                  'least_support_marginal_order': None if marker is None else len(marker),
                  'check_permitted_only_in_one_space': marker, 'four_following_cuts': []}
        present = [left, right]
        for _ in range(4):
            current = []
            for i, rows in enumerate(present):
                status, count = following(rows)
                if count > 1024:
                    current.append({'status': 'cap', 'planned_births': count, 'width': width(rows)})
                    continue
                status2, later, roster = native(rows, 'parity')
                assert (status, count) == (status2, len(roster))
                present[i] = later
                current.append({'status': status, 'births': count, 'width': width(later)})
            record['four_following_cuts'].append(current)
            if any(s['status'] == 'cap' for s in current):
                break
        kept[label] = record
    return kept


def main():
    with gzip.open(OUTPUT / 'census_stages.json.gz', 'rt') as file:
        raw = json.load(file)
    with gzip.open(OUTPUT / 'census_rate_tables.json.gz', 'rt') as file:
        num = json.load(file)
    summary = json.loads((OUTPUT / 'census_summary.json').read_text())
    answer = {}
    for law in raw:
        answer[law] = dict(physical=actual_cases(raw[law], law), rates=compare_rates(raw[law], num[law], law))
        print(law, answer[law], flush=True)
    answer['parity_continuations'] = trace_parity(summary['parity'])
    (OUTPUT / 'census_verification.json').write_text(json.dumps(answer, indent=2) + '\n')


if __name__ == '__main__':
    main()
