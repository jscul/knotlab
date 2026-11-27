"""Independent finite checks for the signed close and simultaneous sibling weighting.

Run from the repository root with standard Python. The only imported project tool is
the canonical command on an independently found support witness.
"""

import argparse
import itertools
import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from math import prod, sqrt


def signed_involutions():
    for image in itertools.permutations(range(3)):
        if any(image[image[i]] != i for i in range(3)):
            continue
        for signs in itertools.product((1, -1), repeat=3):
            if all(signs[image[i]] == signs[i] for i in range(3)):
                yield image, signs


def commutes_with_swap(operator):
    image, signs = operator
    swap = (0, 2, 1)
    return all(image[swap[i]] == swap[image[i]] and signs[swap[i]] == signs[i]
               for i in range(3))


def best_chsh(readers, correlation):
    # B0 and B1 enter separately, so their exact optimizations can be done independently.
    values = [[correlation(a, b) for b in readers] for a in readers]
    best = None
    for i, r in enumerate(values):
        for j, s in enumerate(values):
            upper = [x + y for x, y in zip(r, s)]
            lower = [x - y for x, y in zip(r, s)]
            score = max(upper) + max(lower)
            if best is None or score > best[0]:
                best = (score, [i, j, upper.index(max(upper)), lower.index(max(lower))])
    return best


def operation_check(pilot):
    # Ordered local alphabet is (equal, mixed 01, mixed 10). The amplitude
    # matrix [[2,1,1],[1,1,1],[1,1,1]] / sqrt(12) follows by splitting each
    # E/M orbit's probability equally among all its named representatives.
    amps = [[2, 1, 1], [1, 1, 1], [1, 1, 1]]
    def correlation(a, b, coherent):
        ia, sa = a
        ib, sb = b
        return sum(amps[x][y] * amps[ia[x]][ib[y]] * sa[x] * sb[y]
                   for x, y in itertools.product(range(3), repeat=2)
                   if coherent or (ia[x], ib[y]) == (x, y))

    readers = list(signed_involutions())
    families = {'swap_invariant': [a for a in readers if commutes_with_swap(a)],
                'named': readers}
    results = {}
    for name, operators in families.items():
        subset = operators[:4] if pilot else operators
        modes = {}
        for coherent in (False, True):
            score, settings = best_chsh(subset, lambda a, b: correlation(a, b, coherent))
            modes['coherent' if coherent else 'diagonal'] = {
                'CHSH': str(Fraction(score, 12)), 'settings': [subset[i] for i in settings]}
        results[name] = {'operators': len(subset), 'modes': modes}
    # In the encoded E,M basis det of the 2 by 2 amplitude table is 1/6.
    results['unrestricted_coherent'] = {'concurrence': '1/3', 'CHSH': '2*sqrt(10)/3',
                                        'value': 2 * sqrt(10) / 3}
    return results


def parity_fixture(n, complete):
    pairs = [pair for pair in itertools.combinations(range(n), 2)
             if complete or (pair[1] - pair[0]) % n in (1, n - 1)]
    k = len(pairs)
    held = [sum(1 << i for i, pair in enumerate(pairs) if p in pair) for p in range(n)]
    loose = [1 << (k + p) for p in range(n)]
    parents = [h | l for h, l in zip(held, loose)]
    words = [x | sum(l for h, l in zip(held, loose) if (x & h).bit_count() % 2)
             for x in range(1 << k)]
    invisible = [[w for w in words if w and not w & h] for h in parents]
    symmetries = []
    for p in itertools.permutations(range(n)):
        images = [tuple(sorted((p[a], p[b]))) for a, b in pairs]
        if set(images) == set(pairs):
            symmetries.append((p, [pairs.index(j) for j in images] + [k + p[i] for i in range(n)]))

    def mapped(word, positions):
        return sum(1 << b for a, b in enumerate(positions) if word & (1 << a))

    fixed = [[d for d in candidates if all(mapped(d, mapping) == d for image, mapping
                                           in symmetries if image[i] == i)]
             for i, candidates in enumerate(invisible)]
    assert all(len(options) == 1 for options in fixed)
    shifts = [options[0] for options in fixed]
    assert all(mapped(shifts[i], positions) == shifts[p[i]] for i in range(n)
               for p, positions in symmetries)
    return words, parents, loose, shifts, {
        'all_shared_pairs': pairs, 'allowed': len(words), 'invisible': [len(ds) for ds in invisible],
        'stabilizer_fixed': [len(ds) for ds in fixed], 'relabelings': len(symmetries),
        'shifted_distinctions': [[i for i in range(k+n) if d & (1 << i)] for d in shifts]}


def act(operators, word):
    sign = 1
    for shift, phase in operators:
        if (word & phase).bit_count() % 2:
            sign *= -1
        word ^= shift
    return word, sign


def value_table(ops, words, coherent, phases=None):
    moments = {}
    support = set(words)
    for powers in itertools.product((0, 1), repeat=len(ops)):
        product = [o for p, o in zip(powers, ops) if p]
        moment = 0
        for w in words:
            moved, sign = act(product, w)
            if (coherent and moved in support) or moved == w:
                if phases:
                    sign *= phases[w] * phases[moved]
                moment += sign
        moments[powers] = Fraction(moment, len(words))
    return [sum(v * prod(a for a, p in zip(outputs, powers) if p) for powers, v in moments.items())
            / (1 << len(ops)) for outputs in itertools.product((1, -1), repeat=len(ops))]


def sequential_from_zero(first, second):
    out = {}
    for a, b in itertools.product((1, -1), repeat=2):
        amplitudes = {0: 1}
        for read, written in ((first, a), (second, b)):
            updated = Counter(amplitudes)
            for w, value in amplitudes.items():
                moved, sign = act([read], w)
                updated[moved] += written * sign * value
            amplitudes = updated
        out[f'{a:+}/{b:+}'] = str(Fraction(sum(v*v for v in amplitudes.values()), 16))
    return out


def sign_checks(pilot):
    fixtures = [(3, False)] if pilot else [(3, False), (4, False), (4, True)]
    report = {}
    for n, complete in fixtures:
        words, parents, loose, shifts, row = parity_fixture(n, complete)
        signed = list(zip(shifts, loose))
        free_changes = [(d, 0) for d in shifts]
        relative = set()
        for order in itertools.permutations(range(n)):
            for w in words:
                end1, sign1 = act([signed[i] for i in order], w)
                end2, _ = act([free_changes[i] for i in order], w)
                assert end1 == end2
                relative.add(sign1)
        row.update(relative_to_unsigned=sorted(relative))
        if n == 3:
            opposite = [next(1 << j for j, pair in enumerate(row['all_shared_pairs']) if i not in pair)
                        for i in range(n)]
            row['old_words_shared_then_loose'] = [format(w, '06b')[::-1] for w in words]
            row['changes_rostered_readers_can_write'] = [
                sum(bool(w) and (w & ~(e | l)) == 0 for w in words) for e, l in zip(opposite, loose)]
            row['opposite_exchange_global_phase'] = sorted({
                act([(0, opposite[i]), signed[i]], w)[1] * act([signed[i], (0, opposite[i])], w)[1]
                for i in range(n) for w in words})
            z, u, t = (0, opposite[0]), signed[0], free_changes[0]
            row['sequential_from_basis_word_zero'] = {
                'Z_then_signed': sequential_from_zero(z, u), 'signed_then_Z': sequential_from_zero(u, z),
                'Z_then_unsigned': sequential_from_zero(z, t), 'unsigned_then_Z': sequential_from_zero(t, z)}
            row['ordinary_actions_identical_signed_unsigned'] = all(
                act([s], w)[0] == act([t], w)[0] for s, t in zip(signed, free_changes) for w in words)
            phases = {w: (-1)**int((w & 7).bit_count() >= 2) for w in words}
            # D(w)=(-1)^(s0*s1+s0*s2+s1*s2); D leaves every value probability fixed.
            row['unsigned_shift_conjugate_to_signed'] = all(
                act([s], w)[1] == phases[w] * phases[act([t], w)[0]]
                for s, t in zip(signed, free_changes) for w in words)
            row['four_context_product_relative_sign'] = {}
            for family, changes in [('signed', signed), ('unsigned', free_changes)]:
                old_contexts = []
                for i in range(n):
                    old_contexts.extend([(0, opposite[j]) for j in range(n) if i != j])
                    old_contexts.append(changes[i])
                row['four_context_product_relative_sign'][family] = sorted({
                    act(old_contexts, w)[1] * act(changes, w)[1] for w in words})
            row['contexts'] = {}
            for chosen in itertools.product((0, 1), repeat=n):
                ops = [signed[i] if q else (0, opposite[i]) for i, q in enumerate(chosen)]
                unsigned_ops = [free_changes[i] if q else (0, opposite[i]) for i, q in enumerate(chosen)]
                ordinary = [(0, loose[i] if q else opposite[i]) for i, q in enumerate(chosen)]
                assert value_table(ordinary, words, False) == value_table(ordinary, words, True)
                expected = {1: 1, 3: -1}.get(sum(chosen), 0)
                target = [Fraction(1 + expected * prod(a), 8)
                          for a in itertools.product((1, -1), repeat=n)]
                coherent_table = value_table(ops, words, True)
                assert coherent_table == target
                assert value_table(unsigned_ops, words, True, phases) == coherent_table
                dephased_table = value_table(ops, words, False)
                assert dephased_table == [Fraction(1, 8)] * 8
                # A supplied reader on physical bits can perform these single-bit
                # flips on the full six-bit carrier. No such flip keeps the old law.
                physical = [(opposite[i], 0) if q else (loose[i], opposite[i]) for i, q in enumerate(chosen)]
                assert all((w ^ d) not in words for d, z in physical for w in words)
                physical_rephased = value_table(physical, words, True, phases)
                assert physical_rephased == target
                row['contexts'][''.join(map(str, chosen))] = {
                    'signed_coherent': list(map(str, coherent_table)),
                    'unsigned_positive_coherent': list(map(str, value_table(unsigned_ops, words, True))),
                    'unsigned_rephased_coherent': list(map(str, value_table(unsigned_ops, words, True, phases))),
                    'two_physical_bits_positive_coherent': list(map(str, value_table(physical, words, True))),
                    'two_physical_bits_rephased_coherent': list(map(str, physical_rephased)),
                    'signed_dephased': list(map(str, dephased_table)),
                    'ordinary_values': list(map(str, value_table(ordinary, words, False)))}
        report['complete_four' if complete else f'ring_{n}'] = row
    return report


def horizon_check(pilot):
    # The historical NAE census witness 38 supplies these holdings. Each
    # round's truth table and its different stopping marginals are rebuilt.
    stages = [((0, 1, 2), (0, 3, 4, 5), (1, 2, 3, 4, 6, 7)),
              ((5, 6, 8), (7, 9, 10)), ((8, 9, 11), (10, 12, 13))]
    masks = [[sum(1 << j for j in scope) for scope in stage] for stage in stages]
    ok = lambda z, rules: all((z & m) not in (0, m) for m in rules)
    old = [w for w in range(256) if ok(w, masks[0])]
    tested = old[:2] if pilot else old
    changed = 0
    witness = None
    for w in tested:
        mids = [w | (j << 8) for j in range(8) if ok(w | (j << 8), masks[1])]
        counts = [sum(ok(m | (h << 11), masks[2]) for h in range(8)) for m in mids]
        if min(counts) != max(counts):
            changed += 1
            if witness is None:
                # The event "the two old inputs of the second-round join agree"
                # is invariant under their exchange and global value complementation.
                event = [bool(m & 1 << 8) == bool(m & 1 << 9) for m in mids]
                witness = {'old_in_id_order': format(w, '08b')[::-1],
                           'prefixes_and_completion_counts': [
                               [format(m >> 8, '03b')[::-1], c] for m, c in zip(mids, counts)],
                           'P_event_stopping_after_one': str(Fraction(sum(event), len(mids))),
                           'P_event_stopping_after_two': str(Fraction(
                               sum(c for e, c in zip(event, counts) if e), sum(counts)))}
                assert witness['P_event_stopping_after_one'] != witness['P_event_stopping_after_two']
    return {'start_distinctions': 8, 'admissible_starts_tested': len(tested),
            'old_starts_with_incompatible_marginals': changed, 'first_mismatch': witness}


FOUNDER = (0, 0, 1)
STAR = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))


def fresh_pairs(bit):
    return [pair for pair in itertools.product(range(2), repeat=2)
            if len(set((bit,) + pair)) == 2]


def sibling_check():
    named = list(itertools.product(*(fresh_pairs(v) for v in FOUNDER)))
    orbits = defaultdict(list)
    for triple in named:
        # Independently swap the bits of each pair and permit exchange of
        # the two births whose founder inputs match.
        images = []
        for flips in itertools.product((0, 1), repeat=3):
            x, y, z = [pair[::-1] if flip else pair for pair, flip in zip(triple, flips)]
            images.extend(((x, y, z), (y, x, z)))
        orbits[min(images)].append(triple)
    weights = {w: Fraction(1, len(orbits) * len(members))
               for members in orbits.values() for w in members}
    mode = lambda p: int(p[0] != p[1])  # 0 equal, 1 mixed

    def table(weight):
        return [[sum(weight[w] for w in named if [mode(v) for v in w[:2]] == [a, b])
                 for b in (0, 1)] for a in (0, 1)]

    named_weights = {w: Fraction(1, len(named)) for w in named}
    assert sum(weights.values()) == sum(named_weights.values()) == 1
    equal_class = table(weights)
    ordinary = table(named_weights)
    # Start an urn with one equal and two mixed. Reinforce the first color
    # by one before the second draw; use the ordinary count for singleton 1.
    reinforced = [[Fraction(p, 3) * Fraction(q + (a == b), 4)
                   for b, q in enumerate((1, 2))] for a, p in enumerate((1, 2))]
    result = {}
    for name, t in [('equal_classes', equal_class), ('uniform_named', ordinary),
                    ('independent_equal_class_marginals', [[Fraction(1, 4)] * 2 for _ in range(2)]),
                    ('reinforcement_1_equal_2_mixed', reinforced)]:
        result[name] = {'table': [list(map(str, row)) for row in t],
                        'determinant': str(t[0][0] * t[1][1] - t[0][1] * t[1][0])}
    joined_named = [[sum(weights[w] for w in named if (w[0], w[1]) == (a, b))
                     for b in ((1, 1), (0, 1), (1, 0))] for a in ((1, 1), (0, 1), (1, 0))]
    assert joined_named == [[Fraction((2 if i == j == 0 else 1)**2, 12)
                             for j in range(3)] for i in range(3)]
    result['named_words'] = len(named)
    result['orbit_sizes'] = sorted(map(len, orbits.values()))
    result['named_reader_table'] = [list(map(str, row)) for row in joined_named]
    return result


def canonical_witness(fixed):
    cnf = []
    for scope in STAR:
        cnf.extend(' '.join(f'{s}x{d}' for d in scope) for s in ('', '~'))
    if fixed:
        cnf.extend(('~x0', '~x1', 'x2'))
    interface = [3, 4, 5, 6, 2]
    cmd = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(cnf),
           '--loops', *(f'x{d}' for d in interface[:-1]), '--contact', 'x2',
           '--witnesses', *(f'x{d}' for d in range(9) if d not in interface), '--json']
    output = json.loads(subprocess.check_output(cmd, env={**os.environ, 'PYTHONPATH': 'tools'}))
    return {'knot': output['is_knot'], 'allowed': len(output['allowed']),
            'K1': output['binding'], 'K2': output['loss_on_erasure'], 'K3': output['coexistence']}


def support_check(pilot):
    masks = [sum(1 << d for d in scope) for scope in STAR]
    all_words = [w for w in range(512) if all((w & m) not in (0, m) for m in masks)]
    fixed_words = [w for w in all_words if (w & 7) == 4]
    result = {}
    for name, words, fixed in [('001', fixed_words, True), ('all_six_founders', all_words, False)]:
        if pilot:
            # All necessary proper projections are present in this short trial.
            scopes = [m for m in range(512) if not (m & ~sum(1 << d for d in (3, 4, 5, 6, 2)))]
        else:
            scopes = range(512)
        projected = {m: len({w & m for w in words}) for m in scopes}
        knots = [m for m, count in projected.items()
                 if m.bit_count() >= 3 and 0 < count < 1 << m.bit_count()
                 and all(projected[m ^ (1 << d)] == 1 << (m.bit_count()-1)
                         for d in range(9) if m & (1 << d))]
        joined = [m for m in knots if m & (8 | 16) and m & (32 | 64)]
        as_places = lambda ms: [[d for d in range(9) if m & (1 << d)] for m in ms]
        result[name] = {'allowed_words': len(words), 'tested_subsets': len(scopes),
                        'knots': as_places(knots), 'joining_fresh_pairs': as_places(joined),
                        'canonical_five_distinction_witness': canonical_witness(fixed)}
    return result


def measured(function, *args):
    start = time.perf_counter()
    result = function(*args)
    return {'data': result, 'seconds': round(time.perf_counter() - start, 6)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    cap = 512 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    results = {'pilot': args.pilot, 'sibling_readers': measured(operation_check, args.pilot),
               'invisible_changes': measured(sign_checks, args.pilot),
               'horizons': measured(horizon_check, args.pilot),
               'sibling_orbits': measured(sibling_check),
               'supports': measured(support_check, args.pilot)}
    results['peak_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    results['canonical_child_peak_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
