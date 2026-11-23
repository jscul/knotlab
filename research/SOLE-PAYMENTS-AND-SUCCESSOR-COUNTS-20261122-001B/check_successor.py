"""Audit the two real payments, using the archived physical holdings and words."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE, = (ROOT / 'artifacts' / 'QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001B').glob('*/results.json')
FROZEN = 'da74be90b918eb5cff969aaa999f5412e8311dc45a40a21c040a6203dfcfdbf7'
BANKS = tuple(''.join(pair) for pair in product('01', repeat=2))


def lawful(law, values):
    count = values.count('1')
    return count % 2 == 0 if law == 'parity' else 0 < count < len(values)


def supports(law):
    return {pair: [bank for bank in BANKS if lawful(law, pair + bank)] for pair in BANKS}


def read(word, marks):
    return ''.join(word[m] for m in marks)


def owners(holdings):
    by_mark = defaultdict(set)
    for h, row in holdings.items():
        for m in row:
            by_mark[m].add(h)
    assert all(1 <= len(v) <= 2 for v in by_mark.values())
    return by_mark


def bind_cohorts(initial, cohorts):
    cuts = [dict(enumerate(initial))]
    for frame in cohorts[1:]:
        before = cuts[-1]
        after = before.copy()
        old_owners = owners(before)
        paid = []
        for row in frame['births']:
            h = row['knot']
            assert h not in after and len(row['parents']) == len(set(row['parents'])) == 2
            for parent, mark in zip(row['parents'], row['paid'], strict=True):
                assert old_owners[mark] == {parent}
                paid.append(mark)
            assert len(row['fresh']) == 2 and not set(row['fresh']).intersection(old_owners)
            after[h] = tuple(row['paid'] + row['fresh'])
        assert Counter(paid) == Counter(m for m, holders in old_owners.items() if len(holders) == 1)
        new_owners = owners(after)
        assert all(new_owners[m] == {row['knot']} for row in frame['births'] for m in row['fresh'])
        cuts.append(after)
    return cuts


def reconstruct(holdings, word):
    """Recover the growing enrollment and signals from one complete physical presentation."""
    current = holdings.copy()
    layers = []
    while len(current) > 5:
        owned = owners(current)
        latest = {h for h, row in current.items() if any(len(owned[m]) == 1 for m in row)}
        assert len(latest) == 5
        groups = {}
        for h in latest:
            parents = {p: m for m in current[h] for p in owned[m] - {h}}
            assert len(parents) == 2 and not latest.intersection(parents)
            groups[frozenset(parents)] = h, tuple(parents.values())
        assert len(groups) == 5
        layers.append(groups)
        current = {h: row for h, row in current.items() if h not in latest}

    count = Counter(frozenset(pair) for pair in owners(current).values() if len(pair) == 2)
    doubled, = (pair for pair, size in count.items() if size == 2)
    tripled, = (pair for pair, size in count.items() if size == 3)
    anchor, = doubled & tripled
    second, = doubled - {anchor}
    order = [anchor, second]
    while len(order) < 5:
        nxt, = (h for h in current if h not in order and frozenset((order[-1], h)) in count)
        order.append(nxt)
    by_phase = order[::2] + order[1::2]
    words = {h: (h,) for h in current}
    receipts = []
    for groups in reversed(layers):
        following = []
        for i, left in enumerate(by_phase):
            right = by_phase[(i + 1) % 5]
            child, inputs = groups[frozenset((left, right))]
            assert words[left][1:] == words[right][:-1]
            words[child] = (*words[left], words[right][-1])
            if i == 0 and words[child][-1] == anchor:
                receipts.append((child, int(len(set(read(word, inputs))) == 2)))
            following.append(child)
        by_phase = following
    return receipts


def complete(law, before, cohort, reference, pins):
    word = list(before)
    for row in cohort['births']:
        names = row['fresh']
        assert names == [len(word), len(word) + 1]
        quiet = read(reference, names)
        legal = supports(law)[read(before, row['paid'])]
        bank = next(bank for bank in (quiet, *legal) if bank in legal and
                    all(pins.get(m, v) == v for m, v in zip(names, bank, strict=True)))
        word.extend(bank)
    return ''.join(word)


def physical_view(holdings, word, root, radius, renaming=None):
    """All marks of the visited holders, with incidence and total holder count."""
    by_mark = owners(holdings)
    seen = {root}
    for _ in range(radius):
        seen |= {h for old in seen for m in holdings[old] for h in by_mark[m]}
    names = {m for h in seen for m in holdings[h]}
    rename = renaming or {}
    return {rename.get(m, m): (word[m], len(by_mark[m]), sorted(by_mark[m] & seen)) for m in names}


def row_of(cohort, knot):
    return next(row for row in cohort['births'] if row['knot'] == knot)


def receipt(row, word):
    return {**row, 'paid_values': read(word, row['paid']), 'fresh_values': read(word, row['fresh'])}


def payments(cohort, parent, word):
    return [{'to': row['knot'], 'mark': m, 'value': word[m]}
            for row in cohort['births'] for p, m in zip(row['parents'], row['paid'], strict=True)
            if p == parent]


def check_all(law, holdings, word):
    assert all(lawful(law, read(word, row)) for row in holdings.values())


def first_payment(law, frames, cuts, quiet, pulse):
    # These physical names are the two actual slots of 29; 65 is the other payment to 34.
    parent = row_of(frames[5], 29)
    outside = row_of(frames[5], 28)
    child = row_of(frames[6], 34)
    assert parent['fresh'] == [66, 67] and child['paid'] == [65, 67]
    assert frames[5]['enrolled_holder'] == 29 and frames[6]['enrolled_holder'] == 34
    assert read(quiet[5], parent['paid']) == '00' and read(pulse[5], parent['paid']) == '01'
    branches = {}
    for name, pins in (('other_child', {66: '0', 67: '1', 65: '1'}),
                       ('enrolled_child', {66: '1', 67: '0', 65: '1'})):
        at_parent = complete(law, pulse[4], frames[5], quiet[5], pins)
        at_child = complete(law, at_parent, frames[6], quiet[6], {})
        check_all(law, cuts[5], at_parent)
        check_all(law, cuts[6], at_child)
        assert reconstruct(cuts[6], at_child) == [(29, 1)]
        branches[name] = {'parent': receipt(parent, at_parent), 'outside_payer': receipt(outside, at_parent),
                          'next_enrolled': receipt(child, at_child), 'both_actual_payments': payments(frames[6], 29, at_child),
                          'whole_words_at_cuts_4_5_6': [pulse[4], at_parent, at_child]}
    hidden = branches['other_child']['whole_words_at_cuts_4_5_6'][-1]
    assert read(hidden, cuts[6][34]) == read(quiet[6], cuts[6][34]) == '1100'
    assert branches['enrolled_child']['next_enrolled']['paid_values'] == '10'
    swaps = [(57, 66)] + ([(56, 64)] if law == 'parity' else [])
    rename = {a: b for pair in swaps for a, b in (pair, pair[::-1])}
    assert set(rename).isdisjoint(cuts[6][34])
    qview = physical_view(cuts[6], quiet[6], 34, 1)
    assert qview == physical_view(cuts[6], hidden, 34, 1, rename)
    # At two contacts choose exactly the marks whose other holder is completely spent.
    by_mark = owners(cuts[6])
    earlier = [m for m in cuts[6][29] if all(len(by_mark[n]) == 2
               for h in by_mark[m] - {29} for n in cuts[6][h])]
    assert set(earlier) == set(parent['paid'])
    return {'quiet_parent': receipt(parent, quiet[5]), 'quiet_child': receipt(child, quiet[6]),
            'one_step_isomorphism_mark_swaps': swaps, 'holders_in_one_step': [28, 29, 34],
            'earlier_inputs_recognized_at_two_steps': earlier, 'branches': branches}


def later_payment(law, frames, cuts, quiet, pulse, saved):
    for words in (quiet, pulse):
        past = None
        for t, (cut, word) in enumerate(zip(cuts, words, strict=True)):
            check_all(law, cut, word)
            assert past is None or word.startswith(past)
            past = word
    differences = [m for m, (left, right) in enumerate(zip(quiet[-1], pulse[-1], strict=True)) if left != right]
    assert differences == saved['remaining_old_differences']
    restored = next(t for t in range(4, len(frames))
                    if all(quiet[t][m] == pulse[t][m] for row in frames[t]['births'] for m in row['fresh']))
    assert restored == saved['first_restored_quiet_fresh_bank_cut']
    last = cuts[-1]
    totals = []
    for word in (quiet[-1], pulse[-1]):
        reads = reconstruct(last, word)
        assert [h for h, s in reads] == [frames[t]['enrolled_holder'] for t in range(5, len(frames), 5)]
        renamed = {-h-1: tuple(-m-1 for m in row) for h, row in last.items()}
        assert reconstruct(renamed, {-m-1: v for m, v in enumerate(word)}) == [(-h-1, s) for h,s in reads]
        totals.append([s for _, s in reads])
    assert totals == [[0] * 6, [1] + [0] * 5]
    after_reset = next(t for t in range(5, len(frames), 5) if t > restored)
    assert after_reset == 10
    later = {}
    for t in (10, 11, 30):
        root = frames[t]['enrolled_holder']
        row = row_of(frames[t], root)
        assert receipt(row, quiet[t]) == receipt(row, pulse[t])
        first_reach = next(r for r in range(t + 1) if
                           physical_view(cuts[t], quiet[t], root, r) != physical_view(cuts[t], pulse[t], root, r))
        later[t] = {'same_complete_receipt': receipt(row, quiet[t]), 'first_contact_budget_with_named_difference': first_reach,
                    'whole_presentation_signal_totals': [sum(s for _,s in reconstruct(cuts[t], w[t])) for w in (quiet, pulse)]}
    later[10]['two_payments_identical_in_both_histories'] = payments(frames[11], 50, quiet[11])
    assert later[10]['two_payments_identical_in_both_histories'] == payments(frames[11], 50, pulse[11])
    return {'recovered_streams_through_six_returns': totals, 'whole_present_recount_after_renaming': True,
            'permanently_different_old_marks': {m: sorted(owners(last)[m]) for m in differences},
            'first_common_fresh_cohort_after_first_signal': restored, 'matched_receipts': later}


def repeated_pulses(law, frames, cuts, quiet):
    result = []
    for pattern in product((0, 1), repeat=3):
        word = list(quiet[21])
        for t, signal in zip((5, 10, 15), pattern, strict=True):
            if not signal:
                continue
            previous = frames[t-1]['enrolled_holder']
            target = row_of(frames[t], frames[t]['enrolled_holder'])
            outside, = set(target['parents']) - {previous}
            selected = target['paid'][target['parents'].index(outside)]
            changed = [selected]
            if law == 'parity':
                changed = row_of(frames[t-1], outside)['fresh'] + row_of(frames[t+1], frames[t+1]['enrolled_holder'])['paid']
            for m in changed:
                word[m] = '1' if quiet[21][m] == '0' else '0'
        check_all(law, cuts[21], word)
        assert [s for _, s in reconstruct(cuts[21], word)] == [*pattern, 0]
        for t in (20, 21):
            root = frames[t]['enrolled_holder']
            assert physical_view(cuts[t], word, root, 3) == physical_view(cuts[t], quiet[t], root, 3)
        result.append({'earlier_signals': list(pattern), 'sum': sum(pattern)})
    return {'all_three_return_patterns': result, 'identical_fourth_return_and_next_child_within_three_steps': True}


def selected_parity_control(law, frames, cuts, quiet):
    # An explicitly supplied writer with the phase flag and its already bound outgoing slot.
    pattern = (1, 1, 0, 1, 0, 1)
    word = quiet[0]
    count = 0
    for t in range(1, len(frames)):
        parent = frames[t-1]['enrolled_holder']
        holder = frames[t]['enrolled_holder']
        row = row_of(frames[t], holder)
        incoming = read(word, row['paid'])
        p = int(incoming[row['parents'].index(parent)])
        q = int(incoming[1 - row['parents'].index(parent)])
        assert p == count % 2
        if t % 5 == 0:
            assert p ^ q == pattern[t//5-1]
            count += p ^ q
        selected = q if t % 5 == 0 else p
        assert selected == count % 2
        pins = {}
        if t+1 < len(frames):
            following = row_of(frames[t+1], frames[t+1]['enrolled_holder'])
            role = following['parents'].index(holder)
            pins[following['paid'][role]] = str(selected)
            if (t+1) % 5 == 0:
                pins[following['paid'][1-role]] = str(selected ^ pattern[(t+1)//5-1])
        word = complete(law, word, frames[t], quiet[t], pins)
        check_all(law, cuts[t], word)
    assert [s for _, s in reconstruct(cuts[-1], word)] == list(pattern)
    return {'requested_test_stream': list(pattern), 'actual_signals': count,
            'consecutive_deliveries_checked_through_handoff': len(frames) - 1,
            'writer_supplied_phase_roles_and_prospective_binding': True}


def main():
    assert sha256((HERE / 'preregistration.md').read_bytes()).hexdigest() == FROZEN
    data = json.loads(SOURCE.read_bytes())
    result = {'frozen_sha256': FROZEN, 'source': str(SOURCE.relative_to(ROOT)),
              'source_sha256': sha256(SOURCE.read_bytes()).hexdigest(), 'laws': {}}
    for law, recorded in data['laws'].items():
        frames = recorded['named_funded_ordinary_cohorts']
        cuts = bind_cohorts(data['archived_five_odd_source'], frames)
        quiet = recorded['continuous_valued_histories']['quiet']['actual_complete_words_by_consecutive_cut']
        saved = recorded['same_age_local_signal_tally_control']
        pulse = saved['early_signal_actual_complete_words_by_cut']
        table = supports(law)
        for paid, legal in table.items():
            assert all({b[slot] for b in legal} == {'0', '1'} for slot in (0,1))
            if law == 'parity':
                assert all((paid[0] != paid[1]) == (b[0] != b[1]) for b in legal)
            else:
                assert '01' in legal and '10' in legal
        result['laws'][law] = {'complete_fresh_bank_support': table,
                               'next_payment_of_first_return': first_payment(law, frames, cuts, quiet, pulse),
                               'identical_later_receipt_and_next_payment': later_payment(law, frames, cuts, quiet, pulse, saved),
                               'several_early_signals': repeated_pulses(law, frames, cuts, quiet),
                               'deliberate_writing_control': selected_parity_control(law, frames, cuts, quiet)}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
