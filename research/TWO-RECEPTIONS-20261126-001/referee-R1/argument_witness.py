"""Check explicit starts against the study's growth engine and exact projections."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from time import perf_counter


BASE = Path(__file__).resolve().parents[3]
ENGINE = BASE / 'experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
sys.path.insert(0, str(ENGINE))
import eng


# A smaller name is taken first. The two distinctions selected by the
# four one-parent births precede the distinction selected by the join.
PARITY_START = [
    [10, 4, 5],             # left parent of the join
    [11, 6, 7],             # right parent of the join
    [2, 4, 5, 6, 7],        # met by both parents of the join
    [2, 0, 3, 8],           # met by the parent holding distinctions 12 and 13
    [2, 1, 9],              # met by the parent holding distinctions 14 and 15
    [0, 1, 3],              # met by all four one-parent births
    [8, 12, 13],            # left parent with two loose distinctions
    [9, 14, 15],            # right parent with two loose distinctions
]


def own_counts(roster):
    return Counter(u for group in roster.groups for u in group)


def add_loose(state, u):
    d = len(state.holders)
    state.places[u].append(d)
    state.holders.append([u])
    state.barred.append(False)
    state.maker.append(u)


def present(state, guard):
    return eng.build_roster(state, eng.live_members(state), 'check', guard)


def projection_check(state):
    """Enumerate every allowed joint state via independent binary elimination.

    Each reported projection is the entire even-parity relation on its places
    exactly when it has 2**(arity-1) members. Then it is nonempty and proper,
    and dropping any distinction leaves all assignments possible.
    """
    rows = [sum(1 << d for d in places) for places in state.places]
    reduced = list(rows)
    pivot_columns = []
    for d in range(state.n_distinctions):
        i = len(pivot_columns)
        j = next((j for j in range(i, len(rows)) if (reduced[j] >> d) & 1), None)
        if j is None:
            continue
        reduced[i], reduced[j] = reduced[j], reduced[i]
        for k in range(len(reduced)):
            if k != i and ((reduced[k] >> d) & 1):
                reduced[k] ^= reduced[i]
        pivot_columns.append(d)
    free = sorted(set(range(state.n_distinctions)) - set(pivot_columns))
    projections = [set() for _ in rows]
    for choice in range(1 << len(free)):
        assignment = sum(((choice >> k) & 1) << d for k, d in enumerate(free))
        for d, row in zip(pivot_columns, reduced):
            assignment |= ((assignment & row).bit_count() % 2) << d
        assert all((assignment & row).bit_count() % 2 == 0 for row in rows)
        for seen, row in zip(projections, rows):
            seen.add(assignment & row)
    failed = [i for i, (row, seen) in enumerate(zip(rows, projections))
              if row.bit_count() < 3 or len(seen) != 1 << (row.bit_count() - 1)]
    return dict(allowed_states=1 << len(free), checked=len(rows), failed=failed,
                arities=[row.bit_count() for row in rows],
                projection_sizes=[len(seen) for seen in projections])


def parity_case(knot_law):
    law = eng.Law('ORD', 'CANCEL-WAIT', 'MET', knot_law, 'OLDEST')
    guard = eng.Guard()
    state = eng.from_stars(PARITY_START)
    before = projection_check(state) if knot_law == 'parity' else None
    rec = eng.play_round(state, law, guard)
    assert not rec['short']
    after = projection_check(state) if knot_law == 'parity' else None
    births = [{k: b[k] for k in ('id', 'parents', 'inputs', 'D', 'f', 'implied')}
              for b in rec['births']]
    second = eng.play_round(state, law, guard)
    short = second['short']
    if knot_law == 'parity':
        assert not before['failed'] and not after['failed']
        assert len(births) == 5 and [b['id'] for b in births if b['implied']] == [8]
        assert all(b['D'] == 1 for b in births) and births[0]['f'] == 0
        assert short == [9, 10, 11, 12]
        assert all(second['owe'][u] == 3 and second['h'][u] == 1 for u in short)
    else:
        assert all(b['f'] >= b['D'] and b['f'] > 0 for b in births)
        assert not short
    return dict(law=knot_law, stars=PARITY_START, first_groups=rec['groups'],
                first_short=rec['short'], first_births=births,
                demand_groups=rec['demand'].groups, second_groups=second['groups'],
                second_short=short, second_owing=second['owe'], second_holds=second['h'],
                initial_projections=before, after_first_round_projections=after)


def added_case():
    law = eng.Law('ORD', 'CANCEL-WAIT', None, 'nae')
    starts = [[0, 1, 2], [0, 3, 4, 5]]
    guard = eng.Guard()
    state = eng.from_stars(starts)
    births = eng.play_round(state, law, guard)['births']
    children = [b['id'] for b in births if b['parents'] == (1,)]
    cases = {}
    for target in [None, children[0], 0]:
        changed = state.copy()
        if target is not None:
            add_loose(changed, target)
        roster = present(changed, guard)
        owed = own_counts(roster)
        cases[str(target)] = {u: [owed[u], roster.h[u]] for u in children}
        if target == 0:
            assert all(owed[u] == 3 and roster.h[u] == 2 for u in children)
        else:
            assert all(owed[u] == 2 <= roster.h[u] for u in children)
    return dict(start=starts, children=children, owing_and_holdings_by_addition_target=cases)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=('parity', 'nae', 'addition', 'all'))
    args = parser.parse_args()
    cases = [args.case] if args.case != 'all' else ['parity', 'nae', 'addition']
    for case in cases:
        start = perf_counter()
        result = added_case() if case == 'addition' else parity_case(case)
        print(json.dumps(dict(case=case, result=result, seconds=perf_counter() - start)))
