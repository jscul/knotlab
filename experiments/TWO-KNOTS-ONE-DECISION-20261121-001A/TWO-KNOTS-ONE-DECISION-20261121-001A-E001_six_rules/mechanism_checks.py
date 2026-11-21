"""Independent amplitude and physical-word checks for the supported finite cases."""

from collections import Counter
from dataclasses import replace
from fractions import Fraction
from itertools import combinations, product

from predict import READ_ORDER, parity, primitive_compile, project_columns
from replay import CLEAR, FRESH, Catalogue, Replay, encode_law, fixed_one, private, state_code, total_variation
from readouts import answer_table, changed_mass, events, one_round


def permutations(replay):
    """Multiply actual signed permutations on every W word, both orderings."""
    device = replay.device
    words = device.carrier
    masks = device.flips
    signs = device.signs
    positions = {e: i for i, e in enumerate(device.marks)}
    encode = {0: '101', 1: '011'}

    def operation(w, e, h=None):
        return w ^ masks[e], (w >> positions[e] & 1) ^ signs[e] ^ ((h,e) in device.reversed_occurrences)

    def read(w, es, h=None):
        sign = 0
        for e in es:
            w, phase = operation(w, e, h)
            sign ^= phase
        return w, sign

    membership = set(words)
    tracks = []
    for e in device.marks:
        for w in words:
            after, sign = operation(w, e)
            assert after in membership and read(w, (e, e)) == (w, 0)
            first_bits = [encode[w >> i & 1] for i in range(len(positions))]
            second_bits = [encode[after >> i & 1] for i in range(len(positions))]
            pairs = [(m, 0, 1) for m in device.named_mask(masks[e])]
            swapped = list(first_bits)
            for m, i, j in pairs:
                row = list(first_bits[positions[m]])
                row[i], row[j] = row[j], row[i]
                swapped[positions[m]] = ''.join(row)
            assert swapped == second_bits
            tracks.append((e, w, after, sign, pairs))
    products = []
    commutator_checks = 0
    product_checks = 0
    for h, es in enumerate(device.holdings):
        for a, b in combinations(es, 2):
            for w in words:
                assert read(w, (a, b), h) == read(w, (b, a), h)
                commutator_checks += 1
        for selection in range(1 << len(es)):
            selected = tuple(sorted(m for j, m in enumerate(es) if selection >> j & 1))
            values = {parity(w & selection) for w in device.allowed[h]}
            if len(values) == 1:
                sign = values.pop()
                observed = {read(w, selected, h)[1] for w in words}
                for w in words:
                    assert read(w, selected, h) == (w, sign)
                    product_checks += 1
                assert observed == {sign}
                products.append((h, selected, sign))
    answer_exchanges = []
    legal = ('110', '101', '011')
    for bit, answer in encode.items():
        swaps = (int(not bit), 2)
        for word in legal:
            copy = list(word)
            i, j = swaps
            copy[i], copy[j] = copy[j], copy[i]
            assert ''.join(copy) in legal
            if word == '110':
                assert ''.join(copy) == answer
            answer_exchanges.append((bit, swaps, word, ''.join(copy)))
    return {'checked_physical_basis_reads': len(tracks), 'physical_basis_replay': tracks,
            'local_ordered_products': products, 'product_checks': product_checks,
            'local_commutator_checks': commutator_checks, 'ternary_answer_exchanges': answer_exchanges,
            'private_preparation_and_uncomputation': 'See the shared mechanism record for the supplied coherent operations.'}


def read_effects(c, compiled, h, tagged):
    """Integer K* K for all local Kraus operators, denominator 64.

    Columns come from literal expansion of joint pointer/branch amplitudes.
    Pointer alternative t=0 applies I. Alternative t=1 applies (-1)^b U.
    Coherent cleanup makes the alternatives share the same zero tag register.
    """
    by_result = {}
    for output, tag in product(READ_ORDER, (0, 1) if tagged else (None,)):
        columns = project_columns(c.holdings, compiled, h, output, tag=tag)
        effect = {}
        # Rows of the Kraus matrix accumulated by actual returned native word.
        by_word = {}
        for col, values in enumerate(columns):
            for w, a in values.items():
                by_word.setdefault(w, []).append((col, a))
        for vector in by_word.values():
            for (i, a), (j, b) in product(vector, repeat=2):
                effect[i, j] = effect.get((i, j), 0) + a * b
        by_result[output, tag] = {ij: v for ij, v in effect.items() if v}
    return by_result


def tag_joint(rows):
    counter = Counter()
    for (ready, left, right), p in rows.items():
        a, b = left[-1], right[-1]
        counter[ready, (a[3], a[4]), (b[3], b[4])] += p
    return counter


def forget_tag(rows):
    counter = Counter()
    for (ready, left, right), p in rows.items():
        clean = tuple(tuple(r[:4] + (None,) for r in path) for path in (left, right))
        counter[ready, *clean] += p
    return counter


def marked_reads(replay):
    c = replay.c
    compiled = primitive_compile(c.holdings, c.allowed)
    accepted = compiled[3]
    local_effects = {(h, tagged): read_effects(c, compiled, h, tagged)
                     for h in range(len(c.holdings)) for tagged in (False, True)}
    fresh = {}
    patterns = {'left': ('held', 'none'), 'right': ('none', 'held'), 'both': ('held', 'held'),
                'left_ignored': ('ignored', 'none'), 'right_ignored': ('none', 'ignored'),
                'both_ignored': ('ignored', 'ignored'), 'uncomputed': ('uncomputed', 'uncomputed')}
    private_laws = {label: ({}, {}) for label in patterns}
    physics = 0
    for left, right in product(*c.roles):
        controls = {}
        for label, tag in patterns.items():
            ready = one_round(replay, left, right, tag=tag, on_success=True)
            launch = one_round(replay, left, right, tag=tag)
            if label in ('left', 'right', 'both', 'uncomputed'):
                t = tuple(which == 'held' for which in tag)
                inferred = {}
                for (y, ey), (z, ez) in product(*(local_effects[h, t[i]].items()
                                                  for i, h in enumerate((left, right)))):
                    physics += 1
                    numerator = sum(v * ez.get(ij, 0) for ij, v in ey.items())
                    p = Fraction(numerator, len(accepted) * 4096)
                    if p:
                        inferred[True, y, z] = p
                assert inferred == tag_joint(ready)
            if label.endswith('_ignored'):
                held_label = label.removesuffix('_ignored')
                held = one_round(replay, left, right, tag=patterns[held_label])
                assert launch == forget_tag(held)
            if label == 'uncomputed':
                assert launch == one_round(replay, left, right)
            controls[label] = dict(launch=encode_law(launch),
                                   conditional=encode_law(ready),
                                   displayed_launch=answer_table(launch),
                                   displayed_conditional=answer_table(ready),
                                   events=events(c, launch, 0))
            for i, h in enumerate((left, right)):
                private_laws[label][i].setdefault(h, []).append(private(launch, i))
        fresh[f'{left},{right}'] = controls
    repeats = {}
    for i, role in enumerate(c.roles):
        holder = role[0]
        focused = []
        for label, tags in patterns.items():
            if tags[i] == 'none':
                continue
            for both_slots in (False, True):
                profiles = ((tags, FRESH), (tags if both_slots else CLEAR, FRESH))
                p = fixed_one(replay, (holder, holder), observer=i, profiles=profiles, poststates=True)
                simple = Counter()
                expanded = []
                for (prepared, l, r, states), mass in p.items():
                    simple[prepared, l, r] += mass
                    expanded.append((prepared, l, r, [state_code(s) for s in states], mass))
                focused.append(dict(tag=label, in_both_slots=both_slots, holder=holder,
                                    first_mark=c.holdings[holder][0],
                                    events=[events(c, simple, j) for j in (0, 1)],
                                    first_mark_compare=changed_mass(c, simple, i, 0, 1),
                                    state_and_record_trajectories=expanded))
        repeats[i] = focused
    privacy = {label: [max((total_variation(a, b) for variants in side.values()
                          for a, b in combinations(variants, 2)), default=Fraction())
                       for side in by_role]
               for label, by_role in private_laws.items()}
    assert all(d == 0 for distance in privacy.values() for d in distance)
    return dict(fresh=fresh, targeted_repeats=repeats, explicitly_checked_amplitude_cells=physics,
                maximum_fresh_complete_local_tv_by_side=privacy)


def rewrite_mask(mask, relabel):
    return sum(1 << j for i, j in relabel.items() if mask >> i & 1)


def reverse_answer(word):
    return None if word is None else ((word & 1) << 2) | (word & 2) | ((word & 4) >> 2)


def projected_pair(replay, pair):
    return Counter({(a[0][3], b[0][3]): p for (_, a, b), p in one_round(replay, *pair).items()})


def recodings(replay):
    c = replay.c
    base = replay.device
    n = len(base.marks)
    relabel = {i: n-1-i for i in base.marks}
    permuted = tuple(tuple(relabel[e] for e in marks) for marks in c.holdings)
    cc = Catalogue(permuted, c.roles, c.allowed)
    moved = replace(base, holdings=permuted,
                    identities=tuple((h, rewrite_mask(bits,relabel), b) for h,bits,b in base.identities),
                    carrier=tuple(sorted(rewrite_mask(w,relabel) for w in base.carrier)),
                    flips={relabel[e]: rewrite_mask(d,relabel) for e,d in base.flips.items()},
                    signs={relabel[e]: sign for e,sign in base.signs.items()},
                    accepted_words=tuple(sorted(rewrite_mask(w,relabel) for w in base.accepted_words)),
                    reversed_occurrences=frozenset((h,relabel[e]) for h,e in base.reversed_occurrences))
    assert permutations(Replay(cc, 'coherent', device=moved))['checked_physical_basis_reads']
    transported = Replay(cc, 'coherent', device=moved)
    solved = Replay(cc, 'coherent')
    rev_slots = Catalogue(tuple(h[::-1] for h in c.holdings), c.roles,
                          tuple(tuple(sorted(reverse_answer(w) for w in ws)) for ws in c.allowed))
    solved_slots = Replay(rev_slots, 'coherent')
    pairing = {}
    for a,b in product(*c.roles):
        before = projected_pair(replay, (a,b))
        after = projected_pair(transported, (a,b))
        recompiled = projected_pair(solved, (a,b))
        reordered = projected_pair(solved_slots, (a,b))
        swapped = Counter({(reverse_answer(y),reverse_answer(z)): p for (y,z),p in reordered.items()})
        assert before == after and before == swapped
        pairing[f'{a},{b}'] = dict(transported_tv=total_variation(before, after),
                                  recompiled_tv=total_variation(before, recompiled),
                                  restored_slot_order_tv=total_variation(before, swapped),
                                  recompiled_answer_table=answer_table(one_round(solved,a,b)))
    return dict(mark_permutation=relabel, transported_masks=transported.device.flips,
                transported_signs=transported.device.signs,
                recompiled_masks=solved.device.flips, recompiled_signs=solved.device.signs,
                recompiled_named_certificate=solved.device.certificate(),
                physically_recompiled_is_transport=(solved.device.flips == transported.device.flips
                                                     and solved.device.signs == transported.device.signs),
                by_pair=pairing)


def incidence_control(replay):
    c = replay.c
    h = c.roles[1][0]
    mark = min(c.holdings[h])
    place = c.holdings[h].index(mark)
    changed_words = tuple(tuple(sorted(w ^ (1 << place) for w in allowed)) if i == h else allowed
                          for i, allowed in enumerate(c.allowed))
    calibrated_c = Catalogue(c.holdings, c.roles, changed_words)
    d = replace(replay.device, allowed=changed_words, reversed_occurrences=frozenset({(h,mark)}))
    calibrated = Replay(calibrated_c, 'coherent', device=d)
    recompiled = Replay(calibrated_c, 'coherent')
    cases = {}
    for a,b in product(*c.roles):
        original = one_round(replay,a,b)
        shown = one_round(calibrated,a,b)
        changed = one_round(recompiled,a,b)
        raw_before = Counter({(l[0][2],r[0][2]): p for (_,l,r),p in original.items()})
        raw_after = Counter({(l[0][2],r[0][2]): p for (_,l,r),p in shown.items()})
        assert raw_before == raw_after
        cases[f'{a},{b}'] = dict(actual_raw_effects_unchanged=raw_before == raw_after,
                                incidence_flip=events(calibrated_c,shown,0),
                                recompile=events(calibrated_c,changed,0),
                                recorded_tv=total_variation(projected_pair(calibrated,(a,b)),
                                                            projected_pair(recompiled,(a,b))))
    return dict(mark=mark, second_holder=h, supplied_charge_change='other original laws retained',
                same_apparatus_raw_masks=calibrated.device.flips,
                recompiled_raw_masks=recompiled.device.flips,
                selected_comparator_different_instrument=calibrated.device.flips != recompiled.device.flips,
                cases=cases)
