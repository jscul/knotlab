"""A connected marked not-all-equal pair with different family counts."""
import argparse
import json
import time
from functools import reduce
from operator import and_, or_
from census_tools import HERE, connected, tree


def rows_for(second_loose_holder):
    rows = []
    for base in (0, 9):
        rows.append((base, base+1, base+2))
        rows.extend((base+i, base+3+2*i, base+4+2*i) for i in range(3))
    left = tuple(range(3, 9)) + (18, 19)
    right = tuple(range(12, 18)) + (18,)
    if second_loose_holder:
        right += (20,)
    else:
        left += (20,)
    return rows + [left, right]


def masks(rows):
    return [sum(1 << i for i in r) for r in rows]


def count_states(n, rows):
    universe = (1 << (1 << n)) - 1
    # Bit s of each column gives the named distinction's value at state s.
    columns = [universe // ((1 << (1 << j)) + 1) << (1 << j) for j in range(n)]
    allowed = universe
    for r in rows:
        mono_one = reduce(and_, (columns[j] for j in r))
        mono_zero = universe ^ reduce(or_, (columns[j] for j in r))
        allowed &= ~(mono_one | mono_zero)
    return allowed


def named_groups(group_masks):
    return [[i for i in range(m.bit_length()) if m & (1 << i)] for m in group_masks]


def form(rows, allowed):
    r = masks(rows)
    counts = [sum(i in support for support in rows) for i in range(21)]
    loose = [i for i, count in enumerate(counts) if count == 1]
    families, levels = tree(r)
    max_meeting = max(len(set(s) & set(t)) for j, s in enumerate(rows) for t in rows[:j])
    assert max(counts) == 2 and max_meeting <= 2 and connected(r)
    return dict(supports=rows, loose=loose, families=named_groups(families),
                threshold_groups=[[t, named_groups(g)] for t, g in levels],
                allowed_states=allowed.bit_count(), connected=connected(r),
                max_pair_sharing=max_meeting, largest_knot=max(map(len, rows)),
                redundant_rows=[i for i in range(len(rows))
                                if count_states(21, rows[:i] + rows[i+1:]) == allowed])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    begin = time.monotonic()
    left, right = rows_for(True), rows_for(False)
    assert left[:8] == right[:8]
    if args.pilot:
        print('one full-width reading', count_states(21, left).bit_count(),
              'elapsed seconds', round(time.monotonic()-begin, 3))
        return
    base = count_states(21, left[:8])
    first, second = count_states(21, left), count_states(21, right)
    assert first == base == second and first.bit_count() == 162**2 * 8
    forms = [form(left, first), form(right, second)]
    assert [f['families'] for f in forms] == [[[19], [20]], [[19, 20]]]
    assert all(f['redundant_rows'] == [8, 9] for f in forms)
    record = dict(description='Two copies of the same four-knot start. The two added laws '
                  'share distinction 18. The marked loose distinctions are 19 and 20.',
                  forms=forms, allowed_sets_equal=(first == second),
                  words_differing=(first ^ second).bit_count(),
                  all_eight_core_laws_alone_allow_the_same_words=(first == base),
                  elapsed_seconds=round(time.monotonic()-begin, 3))
    (HERE / 'family_witness.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
