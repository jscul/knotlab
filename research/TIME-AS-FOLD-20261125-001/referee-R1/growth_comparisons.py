"""Paired comparisons using independently grown runs."""

from collections import Counter

from growth_model import Growth, Returns, bits, mask_of, maximal_sets


def descent(growth, part, selected):
    mask = mask_of(part)
    return {
        name for name in range(len(growth.knots))
        if growth.descends(name, mask, selected)
    }


def own_and_joint(growth, x, y, selected):
    x_desc = descent(growth, x, selected)
    y_desc = descent(growth, y, selected)
    own, joint = Counter(), Counter()
    for knot in growth.knots:
        if knot.born > selected and x_desc.intersection(knot.parents):
            (joint if y_desc.intersection(knot.parents) else own)[knot.born] += 1
    return own, joint


def names_for_trace(growth, descendants, selected):
    knots = {}
    distinctions = {}
    knot_seq = distinction_seq = 0
    for name, knot in enumerate(growth.knots):
        fresh = [d for d in knot.places if d not in knot.inputs]
        if knot.born <= selected:
            knots[name] = (0, name)
            for d in fresh:
                distinctions[d] = (0, d)
        elif name in descendants:
            knots[name] = (1, knot_seq)
            knot_seq += 1
            for d in fresh:
                distinctions[d] = (1, distinction_seq)
                distinction_seq += 1
    return knots, distinctions


def trace(growth, x, selected, excluded_side=()):
    x_desc = descent(growth, x, selected)
    knot_names, distinctions = names_for_trace(growth, x_desc, selected)
    trace_by_round = {}
    demands_by_round = {}
    for t in range(selected + 1, growth.round_count() + 1):
        _, _, _, _, first, births = growth.records[t - 1]
        roster = growth.rosters[t]
        own_births = [
            (u, knot) for u, knot in enumerate(births, first)
            if all(p in x_desc and p not in excluded_side for p in knot.parents)
        ]
        x_live = x_desc.intersection(roster.members)
        live_mask = mask_of(x_live)
        met = maximal_sets(m & live_mask for m in roster.met_sets if (m & live_mask).bit_count() > 1)
        trace_by_round[t] = (
            tuple(
                (
                    len(knot.parents) == 1,
                    tuple(knot_names[p] for p in knot.parents),
                    tuple(sorted((distinctions.get(d, (2, 0)), d in knot.shared_inputs) for d in knot.inputs)),
                    knot.usable_fresh,
                    knot.barred_fresh,
                )
                for _, knot in own_births
            ),
            tuple(
                (knot_names[u], roster.h[u], roster.k.get(u, 0))
                for u in sorted(x_live)
            ),
            tuple(sorted(tuple(knot_names[u] for u in bits(m)) for m in met)),
        )
        demands_by_round[t] = tuple(knot.demand for _, knot in own_births)
    return trace_by_round, demands_by_round


def first_diff(left, right, first, last):
    return next((t for t in range(first, last + 1) if left[t] != right[t]), None)


def sum_after(counts, first, last):
    return sum(counts[t] for t in range(first + 1, last + 1))


def examine(growth, record):
    start_round = record['t0']
    original_part = tuple(record['P0'])
    j = record['j']
    x = tuple(record['X'])
    chain = Returns(growth).chain((start_round, original_part))
    y_at_each = [original_part] + [tick.qualifies[0] for tick in chain]
    rounds = [start_round] + [tick.round for tick in chain]
    y = y_at_each[j]
    selected = rounds[j]
    period = rounds[j + 1] - selected
    own, joint = own_and_joint(growth, x, y, selected)
    part_class = growth.rosters[selected]
    cross = part_class.adjacency.copy()
    for u in cross:
        cross[u] |= part_class.direct[u]
    connected = mask_of(y)
    while True:
        larger = connected
        for u in bits(connected):
            larger |= cross[u]
        if larger == connected:
            break
        connected = larger
    trace_A, demands_A = trace(growth, x, selected)
    x_in_A = descent(growth, x, selected)
    y_in_A = descent(growth, y, selected)
    trace_A_strict, _ = trace(growth, x, selected, y_in_A)
    result = {
        'selector': {'part_is_separate': not bool(connected & mask_of(x)),
                     'part_has_knot_made_after_start': any(growth.knots[u].born for u in x)},
        'tick_rounds': rounds[j:j + 5],
        'all_return_rounds': rounds[1:],
        'run_A': {'rounds': growth.round_count(), 'knots': len(growth.knots), 'stop': growth.stop},
        'P_j': list(y),
        'own_A_per_period': [sum_after(own, rounds[i], rounds[i + 1]) for i in range(j, j + 4)],
        'joint_A_per_period': [sum_after(joint, rounds[i], rounds[i + 1]) for i in range(j, j + 4)],
        'bars': [],
    }
    counts = result['own_A_per_period']
    clause1 = len(set(counts)) == 1 and counts[0] > 0
    c_iii_fails = False
    c_fails = not clause1
    confirmed = 0
    strict_confirmed = 0
    for r in (1, 2, 3):
        tick = chain[j + r - 1]
        t = tick.round
        y_now = tick.qualifies[0]
        excluded = set(y_now) - x_in_A
        bar_all = {u for q in tick.qualifies for u in q} - x_in_A
        bar_off = {u for q in tick.off for u in q} - x_in_A

        def barred(knots):
            return Growth(None, growth.law, prefix=growth, after=t, bar=knots).grow()

        if c_iii_fails and c_fails:
            result['bars'].append({'r': r, 'examined': False})
            continue
        B = barred(excluded)
        end = min(growth.round_count(), B.round_count())
        trace_B, demands_B = trace(B, x, selected)
        trace_B_strict, _ = trace(B, x, selected, descent(B, y, selected))
        course_differs = first_diff(trace_A, trace_B, t + 1, end)
        demand_differs = first_diff(demands_A, demands_B, t + 1, end)
        own_B, joint_B = own_and_joint(B, x, y, selected)
        after_lag = [q for q in range(t + 2 * period + 1, B.round_count() + 1) if own_B[q]]
        c_fails |= bool(after_lag)
        grown_2 = end >= t + 2 * period
        grown_4 = end >= t + 4 * period
        out = {
            'r': r,
            'examined': True,
            't_bar': t,
            'barred_part': list(y_now),
            'qualifying_parts': [list(part) for part in tick.qualifies],
            'parts_given_off': [list(part) for part in tick.off],
            'X_desc_in_barred_part': len(set(y_now) & x_in_A),
            'B': {'rounds': B.round_count(), 'stop': B.stop},
            'course_differs': course_differs,
            'demand_differs': demand_differs,
            'grown_2_periods': grown_2,
            'grown_4_periods': grown_4,
            'own_A_after_bar_by_round': {str(q): n for q, n in own.items() if q > t},
            'own_B_after_bar_by_round': {str(q): n for q, n in own_B.items() if q > t},
            'joint_B_after_bar': sum_after(joint_B, t, B.round_count()),
            'own_after_lag_rounds': after_lag,
            'e': sum_after(own_B, t, B.round_count()),
        }
        for key, group, applies in (("B'", bar_off, bool(tick.off)), ("Ball", bar_all, len(tick.qualifies) > 1)):
            if not applies:
                continue
            branch = barred(group)
            branch_trace, _ = trace(branch, x, selected)
            out[key] = {
                'course_differs': first_diff(trace_A, branch_trace, t + 1, min(end, branch.round_count()))
            }
        if course_differs is None or course_differs > t + 2 * period:
            out['c_iii'] = 'equal' if grown_2 else 'undecided'
            c_iii_fails |= grown_2
        else:
            M = Growth(None, growth.law, prefix=growth, after=t,
                       mask=(x, y_now, selected, t)).grow(min(18, t + 4 * period))
            trace_M, _ = trace(M, x, selected)
            trace_M_strict, _ = trace(M, x, selected, descent(M, y, selected))
            out['M'] = {'rounds': M.round_count(), 'stop': M.stop}
            for periods in (2, 4):
                checked = min(t + periods * period, B.round_count())
                through = min(checked, M.round_count())
                differs = first_diff(trace_B, trace_M, t + 1, through)
                out[f'M_equals_B_{periods}'] = differs is None and through == checked
                if periods == 2:
                    out['M_differs_from_B_at'] = differs
                    strict_course = first_diff(trace_A_strict, trace_B_strict, t + 1, min(end, checked))
                    strict_mask = first_diff(trace_B_strict, trace_M_strict, t + 1, through)
                    out['exclude_joint_with_Y_sensitivity'] = {
                        'course_differs': strict_course,
                        'M_equals_B_2': strict_mask is None and through == checked,
                    }
                    if strict_course is not None and strict_mask is None and through == checked:
                        strict_confirmed += 1
            if out['M_equals_B_2']:
                confirmed += 1
                out['c_iii'] = 'differs'
            else:
                out['c_iii'] = 'unconfirmed'
        result['bars'].append(out)
    X_barred = Growth(None, growth.law, prefix=growth, after=selected, bar=x).grow()
    shared_horizon = min(growth.round_count(), X_barred.round_count())
    Y_in_X_barred = Returns(X_barred).chain((selected, y))
    result['X_barred'] = {
        'Y_ticks_A': rounds[j + 1:],
        'Y_ticks_X_barred': [tick.round for tick in Y_in_X_barred],
        'rounds': X_barred.round_count(),
        'stop': X_barred.stop,
    }
    result['X_barred_common_rounds'] = {
        'horizon': shared_horizon,
        'Y_ticks_A': [t for t in rounds[j + 1:] if t <= shared_horizon],
        'Y_ticks_X_barred': [tick.round for tick in Y_in_X_barred if tick.round <= shared_horizon],
    }
    result['clause1'] = clause1
    result['verdict_C'] = 'fails' if c_fails else 'not implemented beyond failure checks'
    result['verdict_C_iii'] = 'fails' if c_iii_fails else 'holds' if confirmed == 3 else 'undecided'
    result['exclude_joint_with_Y_confirmed_bars'] = strict_confirmed
    return result
