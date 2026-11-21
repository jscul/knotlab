"""Discriminators on complete observed histories for the frozen six-rule study."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import lcm

from predict import READ_ORDER, text_word
from replay import (CLEAR, FRESH, differences, encode_law, first_difference, fixed_one, private,
                    shared, sharing_fields, total_variation, values)


def legal(c, row, *, raw=False):
    answer = row[2 if raw else 3]
    return answer is not None and answer in c.allowed[row[0]]


def cond(value, divisor):
    return value / divisor if divisor else None


def one_round(replay, h, k, *, on_success=False, tag=CLEAR):
    return replay.run((h,), (k,), on_success=on_success, tag=tag)


def events(c, rows, slot):
    """Masses and named mismatch expectations in one slot, with raw score kept."""
    mass = Counter({key: Fraction() for key in ('launch', 'source_ready', 'two_answers', 'agreement',
                                                'covered_meeting', 'recorded_score', 'raw_score')})
    mismatched = Counter()
    raw_mismatched = Counter()
    for (ready, a, b), p in rows.items():
        pair = a[slot], b[slot]
        shown = tuple(row[3] for row in pair)
        joint = all(y is not None for y in shown)
        mass['launch'] += p
        mass['source_ready'] += p * ready
        for i, row in enumerate(pair):
            side = 'left' if i == 0 else 'right'
            mass[f'{side}_missing'] += p * (row[3] is None and row[0] is not None)
            mass[f'{side}_wrong'] += p * (row[3] is not None and not legal(c, row))
            mass[f'{side}_{row[1]}'] += p
        mass['two_answers'] += p * joint
        if all(r[0] is not None for r in pair):
            for e in shared(c.holdings, pair[0][0], pair[1][0]):
                mismatched.setdefault(e, Fraction())
                raw_mismatched.setdefault(e, Fraction())
        if joint:
            d = differences(c.holdings, *pair)
            raw_d = differences(c.holdings, *pair, raw=True)
            mass['agreement'] += p * (not d)
            mass['covered_meeting'] += p * bool(shared(c.holdings, pair[0][0], pair[1][0]))
            mass['recorded_score'] += p * (not d and all(legal(c, row) for row in pair))
            mass['raw_score'] += p * (not raw_d and all(legal(c, row, raw=True) for row in pair))
            for e in d:
                mismatched[e] += p
            for e in raw_d:
                raw_mismatched[e] += p
    mass['agreement_given_two_answers'] = cond(mass['agreement'], mass['two_answers'])
    mass['recorded_score_given_ready'] = cond(mass['recorded_score'], mass['source_ready'])
    mass['raw_score_given_ready'] = cond(mass['raw_score'], mass['source_ready'])
    return dict(mass=mass, mismatch_expectation_by_named_mark=mismatched, raw_mismatch_expectation_by_named_mark=raw_mismatched)


def answer_table(rows):
    if rows is None:
        return None
    counter = Counter()
    for (_, a, b), p in rows.items():
        counter[a[0][3], b[0][3]] += p
    ordered = (*READ_ORDER, None)
    return {'shape': [9, 9], 'ordered_words': [text_word(w) for w in READ_ORDER] + ['failure'],
            'ordinary_cells': [str(counter[y, z]) for y, z in product(READ_ORDER, repeat=2)],
            'left_failure_row': [str(counter[None, z]) for z in ordered],
            'right_failure_column': [str(counter[y, None]) for y in READ_ORDER],
            'law_total_mass': sum(counter.values()), 'positive_cell_count': len(counter),
            'zero_cells_including_failure': 81 - len(counter),
            'common_denominator': lcm(*(p.denominator for p in counter.values()))}


def fresh(replay):
    configs = tuple(product(*replay.c.roles))
    rows = {}
    for a, b in configs:
        attempts = one_round(replay, a, b)
        accepted = one_round(replay, a, b, on_success=True)
        rows[f'{a},{b}'] = {'launch': answer_table(attempts), 'conditional': answer_table(accepted),
                            'events': events(replay.c, attempts, 0),
                            'source_acceptance': replay.acceptance}
    return rows


def changed_mass(c, rows, side, i, j):
    change_by_mark = Counter()
    equal_by_mark = Counter()
    mass = Counter({key: Fraction() for key in ('comparison_missing', 'both_words', 'some_change')})
    witness = {}
    for (ready, a, b), p in rows.items():
        path = (a, b)[side]
        if path[i][3] is None or path[j][3] is None:
            mass['comparison_missing'] += p
            continue
        x, y = path[i], path[j]
        changed = differences(c.holdings, x, y)
        mass['both_words'] += p
        mass['some_change'] += p * bool(changed)
        for e in shared(c.holdings, x[0], y[0]):
            if e in changed:
                change_by_mark[e] += p
                witness.setdefault(e, {'complete_history': (ready, path), 'joint_branch_mass': p})
            else:
                equal_by_mark[e] += p
    return dict(mass=mass, change_by_mark=change_by_mark, equal_by_mark=equal_by_mark,
                change_given_both=cond(mass['some_change'], mass['both_words']), witness=witness)


def single_reads(replay):
    out = {}
    for h, k in product(range(len(replay.c.holdings)), repeat=2):
        for seq in ((h, k), (h, k, h)):
            rows = fixed_one(replay, seq)
            settings = ','.join(map(str, seq))
            symbols = Counter()
            for (_, a, _), p in rows.items():
                symbols[values(a)] += p
            comparisons = [(0, 1)] if len(seq) == 2 else [(0, 1), (1, 2), (0, 2)]
            out[settings] = {'launch': encode_law(symbols, [9] * len(seq)),
                             'complete_local': encode_law(private(rows, 0)),
                             'comparisons': {f'{i},{j}': changed_mass(replay.c, rows, 0, i, j) for i, j in comparisons}}
    return out


def fixed_histories(replay):
    local_programs = tuple(tuple(product((None, *role), repeat=2)) for role in replay.c.roles)
    laws = ({}, {})
    records = []
    for a, b in product(*local_programs):
        rows = replay.run(a, b)
        laws[0].setdefault(a, {})[b] = private(rows, 0)
        laws[1].setdefault(b, {})[a] = private(rows, 1)
        active = sum(h is not None for h in a+b)
        record = {'left': a, 'right': b, 'positive_complete_joint_records': len(rows),
                  'common_denominator': lcm(*(p.denominator for p in rows.values())),
                  'displayed_answer_cells_including_failure': 9 ** active,
                  'displayed_zero_cells_including_failure': 9 ** active - len({
                      (values(left), values(right)) for _, left, right in rows}),
                  'events_per_slot': [events(replay.c, rows, i) for i in (0, 1)]}
        if all(h is not None for h in a+b) and a[0] == a[1] and b[0] == b[1]:
            record['complete_joint_repeat_law'] = encode_law(rows)
            record['repeat_changes'] = [changed_mass(replay.c, rows, i, 0, 1) for i in (0, 1)]
        records.append(record)
    privacy = []
    for role, by_script in enumerate(laws):
        deepest = Counter()
        nonzero = []
        zero = 0
        for own, by_remote in by_script.items():
            for a, b in combinations(by_remote, 2):
                first, second = by_remote[a], by_remote[b]
                if first == second:
                    zero += 1
                    continue
                delta = total_variation(first, second)
                witness = first_difference(first, second)
                deepest[witness['slot']] += 1
                nonzero.append({'own': own, 'far_first': a, 'far_second': b, 'full_tv': delta, **witness})
        privacy.append({'observer': role, 'zero': zero, 'nonzero': len(nonzero),
                        'maximum_tv': max((case['full_tv'] for case in nonzero), default=Fraction()),
                        'count_by_first_leaking_slot': deepest, 'different_cases': nonzero})
    return dict(conditions=records, fixed_two_slot_privacy=privacy, role_programs=local_programs)


def sweep_events(c, rows, observer):
    bad = Counter()
    mismatched = Counter()
    for (ready, a, b), p in rows.items():
        own, far = (a, b)[::1 if observer == 0 else -1]
        missing_own = sum(word[3] is None for word in own)
        missing_far = sum(word[3] is None for word in far)
        wrong_own = sum(word[3] is not None and not legal(c, word) for word in own)
        wrong_far = sum(word[3] is not None and not legal(c, word) for word in far)
        repeats = sum(s[3] != t[3] for s, t in zip(far, far[1:]) if s[3] is not None and t[3] is not None)
        mismatches = [e for s, t in zip(own, far, strict=True) for e in differences(c.holdings, s, t)]
        own_bad = bool(missing_own or wrong_own)
        far_bad = bool(missing_far or wrong_far or repeats)
        bad['A_bad'] += p * own_bad
        bad['B_bad'] += p * far_bad
        bad['A_or_B_bad'] += p * (own_bad or far_bad)
        bad['setup_failed'] += p * (not ready)
        bad['A_has_missing'] += p * bool(missing_own)
        bad['B_has_missing'] += p * bool(missing_far)
        bad['A_has_wrong'] += p * bool(wrong_own)
        bad['B_has_wrong'] += p * bool(wrong_far)
        bad['B_has_unstable_repeat'] += p * bool(repeats)
        bad['A_missing_count'] += p * missing_own
        bad['B_missing_count'] += p * missing_far
        bad['A_wrong_count'] += p * wrong_own
        bad['B_wrong_count'] += p * wrong_far
        bad['B_repeat_flip_count'] += p * repeats
        bad['disagreement_event'] += p * bool(mismatches)
        bad['E_N'] += p * len(mismatches)
        bad['mismatch_or_B_bad'] += p * (bool(mismatches) or far_bad)
        bad['mismatch_or_any_bad'] += p * (bool(mismatches) or far_bad or own_bad)
        for x, y in zip(own, far, strict=True):
            for e in shared(c.holdings, x[0], y[0]):
                mismatched.setdefault(e, Fraction())
        for e in mismatches:
            mismatched[e] += p
    return bad, mismatched


def assembled_violations(c, own, far_role):
    if not all(legal(c, row) for row in own):
        return None
    own_assignments = {e: (row[3] >> j) & 1
                       for row in own for j, e in enumerate(c.holdings[row[0]])}
    return tuple(h for h in far_role if all(e in own_assignments for e in c.holdings[h])
                 and sum(own_assignments[e] << j for j, e in enumerate(c.holdings[h])) not in c.allowed[h])


def assembled_events(c, own_law, far_role):
    fail = Counter()
    union = Fraction()
    for (_, own), p in own_law.items():
        rejected = assembled_violations(c, own, far_role)
        if rejected is None:
            fail['A_bad'] += p
        else:
            for holder in rejected:
                fail[holder] += p
        if rejected is None or rejected:
            union += p
    return fail, union


def sweep(replay):
    c = replay.c
    charge = [set(w.bit_count() % 2 for w in answers) for answers in c.allowed]
    odd = all(len(x) == 1 for x in charge) and sum(next(iter(x)) for x in charge) % 2 == 1
    result = []
    for observer in (0, 1):
        own, far = c.roles[::1 if observer == 0 else -1]
        complete_cover = ({e for h in own for e in c.holdings[h]} == {e for h in far for e in c.holdings[h]}
                          and len({e for h in own for e in c.holdings[h]}) == 3 * len(own) == 3 * len(far))
        for reverse in (False, True):
            program = own[::-1] if reverse else own
            laws = {}
            counts = {}
            by_mark = {}
            for j in far:
                rows = replay.run(*(program, (j,) * len(own))[::1 if observer == 0 else -1])
                laws[j] = private(rows, observer)
                counts[j], by_mark[j] = sweep_events(c, rows, observer)
            references = {}
            for k in far:
                tvs = {j: total_variation(laws[k], laws[j]) for j in far}
                assembled, exact = assembled_events(c, laws[k], far)
                transferred = counts[k]['A_bad'] + sum(
                    counts[j]['mismatch_or_B_bad'] + tvs[j] for j in far)
                bound = counts[k]['A_bad'] + sum(counts[j]['E_N'] + counts[j]['B_bad'] + tvs[j] for j in far)
                if odd and complete_cover:
                    assert exact == 1 and exact <= sum(assembled.values()) <= transferred <= bound
                references[k] = {'tv_to_each_holder': tvs, 'tv_sum': sum(tvs.values()),
                                 'max_tv': max(tvs.values()), 'assembled_violation_or_A_bad': exact,
                                 'assembled_events': [(j, assembled[j]) for j in ('A_bad', *far)],
                                 'assembled_sum': sum(assembled.values()),
                                 'assembled_event_overcount': sum(assembled.values()) - exact,
                                 'union_event_bound': transferred, 'counted_bound': bound,
                                 'counted_over_union_bound': bound - transferred}
            result.append({'observer': observer, 'own_sweep': program, 'fixed_holders': far,
                           'odd_complete_cover': bool(odd and complete_cover), 'counts_by_holder': counts,
                           'mismatch_by_holder_and_mark': by_mark, 'reference_checks': references,
                           'one_sided_complete_laws': {j: encode_law(laws[j]) for j in far},
                           'sum_expected_mismatches': sum(event['E_N'] for event in counts.values())})
    return result


def compared_private(a, b, which):
    first, second = private(a, which), private(b, which)
    return dict(first_law=encode_law(first), second_law=encode_law(second),
                full_tv=total_variation(first, second), first_difference=first_difference(first, second))


def adaptive(replay):
    holds, roles = replay.c.holdings, replay.c.roles
    out = []
    for observer in (0, 1):
        own, remote = roles[::1 if observer == 0 else -1]
        first, nxt = own[0], own[min(len(own)-1, 1)]
        remotely_shared = set().union(*(set(holds[h]) for h in remote))
        shared_mark = min(set(holds[first]) & remotely_shared)
        place = holds[first].index(shared_mark)
        includes = next((h for h in remote if shared_mark in holds[h]), None)
        excludes = next((h for h in remote if shared_mark not in holds[h]), None)

        def local_policy(history):
            slot = len(history)
            if slot == 1:
                return None
            if slot != 3:
                return first
            y = history[0][3]
            return nxt if y is not None and (y >> place & 1) and history[2][3] is not None else first

        remotes = ((None, includes, None, None), (None, excludes, None, None))
        first_law, second_law = [replay.run(*(local_policy, seq)[::1 if observer == 0 else -1]) for seq in remotes]
        positive = []
        # Deliver the other setting as an actual extra local register only on the
        # designated positive control. This replaces neither local receipt nor answer.
        for rows, far_setting in zip((first_law, second_law), (includes, excludes), strict=True):
            positive.append(Counter({(ready, path[:1] + (path[1] + (far_setting,),) + path[2:]): p
                                     for (ready, path), p in private(rows, observer).items()}))
        far_first, far_alt = remote[0], remote[min(len(remote)-1, 1)]
        own_fixed = own if len(own) > 1 else (own[0], own[0])

        def remote_policy(history):
            return far_alt if len(history) == 1 and history[0][3] is not None and history[0][3] & 1 else far_first

        fixed_far = (far_first,) * len(own_fixed)
        adaptive_far = replay.run(*(own_fixed, remote_policy)[::1 if observer == 0 else -1])
        nonadaptive_far = replay.run(*(own_fixed, fixed_far)[::1 if observer == 0 else -1])
        out.append(dict(observer=observer, local_first=first, local_alternative=nxt, shared_mark=shared_mark,
                        far_slot_2=[includes, excludes], observer_adaptive=compared_private(first_law, second_law, observer),
                        delivered_far_setting_control={'full_tv': total_variation(*positive),
                                                       'first_difference': first_difference(*positive)},
                        far_adaptive=compared_private(adaptive_far, nonadaptive_far, observer),
                        far_local_first=far_first, far_local_alternative=far_alt, observer_fixed=own_fixed))
    return out


def unilateral(replay, first, then, near, *, on_success=False):
    """Asked-near, idle-far, then the far asks while the near idles."""
    l, r = ((first, None), (None, then))[::1 if near == 0 else -1]
    rows = replay.run(l, r, on_success=on_success)
    if rows is None:
        return None
    observer_groups = {}
    idle = Counter()
    marginal = Counter()
    for (prepared, a, b), p in rows.items():
        local, remote = (a, b)[::1 if near == 0 else -1]
        key = prepared, local[0]
        observer_groups.setdefault(key, Counter())[remote[1]] += p
        idle[remote[0]] += p
        marginal[prepared, remote[1]] += p
    expected = Counter({(None, 'idle', None, None, None): Fraction(1)})
    assert idle == expected
    solo = fixed_one(replay, (then,), observer=1-near, on_success=on_success)
    nonselective_control = Counter({(ready, path[0]): p for (ready, path), p in private(solo, 1-near).items()})
    compared_no_communication = total_variation(marginal, nonselective_control)
    bits = sharing_fields(replay.c.holdings, first, then)
    conditions = []
    for (prepared, first_record), counts in observer_groups.items():
        near_word = first_record[3]
        total = sum(counts.values())
        conditional = Counter({record: p / total for record, p in counts.items()})
        supported_answers = {text_word(row[3]): p for row, p in conditional.items() if row[3] is not None}
        conditional_bits = {}
        for name, (a, b) in bits.items():
            zero = sum(p for row, p in conditional.items() if row[3] is not None and not (row[3] >> b & 1))
            one = sum(p for row, p in conditional.items() if row[3] is not None and row[3] >> b & 1)
            conditional_bits[name] = {'near_bit': None if near_word is None else near_word >> a & 1,
                                      'far_read_zero': zero, 'far_read_one': one,
                                      'far_absent': 1-zero-one, 'bit_guess_if_far_read': cond(max(zero, one), zero+one)}
        support_mass = sum(supported_answers.values())
        conditions.append(dict(source_ready=prepared, near_record=first_record, near_mass=total,
                               conditional_full_far_law=encode_law(conditional),
                               conditional_shared_bits=conditional_bits, far_word_support=supported_answers,
                               best_ordinary_word_success_per_trial=max(supported_answers.values(), default=Fraction()),
                               best_whole_word_if_far_read=cond(max(supported_answers.values(), default=Fraction()), support_mass)))
    return dict(near_role=near, first=first, then=then,
                idle_local_law=encode_law(idle), far_idle_new_address=0, far_idle_fired_pairs=0,
                far_idle_additional_clock_events=0, far_idle_new_latch_writes=0,
                nonselective_far=encode_law(marginal), far_first_control=encode_law(nonselective_control),
                far_marginal_tv=compared_no_communication, conditions=conditions)
