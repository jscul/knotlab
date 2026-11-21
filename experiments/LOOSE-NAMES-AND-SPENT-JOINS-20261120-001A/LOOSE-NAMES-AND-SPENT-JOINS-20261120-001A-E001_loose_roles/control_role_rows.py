"""Exact necessary loose-index tests, without the physical roles as input."""

from itertools import combinations, product


TESTS = ('minimum_and_arity', 'historical_screen', 'proper_triples', 'funded_twin_roles',
         'constant_input_mass', 'unary_binary_input_row', 'absolute_exterior',
         'companion_pair_exterior', 'companion_triple_exterior', 'input_triple_exterior')
PATTERNS = tuple((1, *bits) for bits in product((1, -1), repeat=3))
FOURIER = tuple((signs, tuple(signs[i] * signs[j] for i, j in combinations(range(4), 2)),
                 signs[1] * signs[2] * signs[3]) for signs in PATTERNS)


def signed_table(n, total, counts):
    signed = [[total if i == j else 0 for j in range(n)] for i in range(n)]
    for (a, b), count in zip(combinations(range(n), 2), counts, strict=True):
        signed[a][b] = signed[b][a] = total - 2 * count
    return signed


def mono_triple(t, c, triple):
    a, b, d = triple
    return t + c[a][b] + c[a][d] + c[b][d]


def historical(t, c, companions, q):
    if len(companions) == 2:
        a, b = companions
        return t + c[a][b] == 2 * q
    if len(companions) == 3:
        return mono_triple(t, c, companions) == 4 * q
    return all(mono_triple(t, c, names) > 4 * q for names in combinations(companions, 3))


def constant_inputs(t, c, inputs, mass):
    if not inputs or mass > t or (len(inputs) > 1 and mass == t):
        return False
    if len(inputs) == 1:
        return mass == t
    return historical(t, c, inputs, mass)


def pair_projection(t, c, x, q, companions, exterior):
    for a, b in combinations(companions, 2):
        mono = t + c[a][b]
        for y in exterior:
            h = c[x][y]
            relative = c[a][y] + c[b][y]
            if 2 * (q - h) > mono + relative or 2 * (q + h) > mono - relative:
                return (a, b, y)
    return None


def triple_projection(t, c, x, q, companions, exterior, scale=1):
    """A four-way signed moment must satisfy all eight joint mass bounds."""
    for a, b, d in combinations(companions, 3):
        for y in exterior:
            known = (c[a][b], c[a][d], c[a][y], c[b][d], c[b][y], c[d][y])
            h = scale * c[x][y]
            low, high = -t, t
            for signs, contrasts, product_sign in FOURIER:
                value = t + sum(r * u for r, u in zip(contrasts, known, strict=True))
                # A constant companion triple with the stated y sign contains
                # the analogous event on the complete companion set.
                need = 4 * (q - signs[3] * h) if signs[1] == signs[2] == 1 else 0
                if product_sign == 1:
                    low = max(low, need - value)
                else:
                    high = min(high, value - need)
                if low > high:
                    return {'names': (a, b, d, y), 'incompatible_bounds': (low, high)}
    return None


def inspect_name(t, c, x):
    names = set(range(len(c)))
    q = -min(c[x][y] for y in names - {x})
    rest = tuple(y for y in range(len(c)) if x != y and c[x][y] == -q)
    support = set(rest) | {x}
    result = {'name': x, 'negative_minimum_numerator': q, 'support': sorted(support), 'fresh_twins': (),
              'inputs': (), 'rejections': {}}
    reject = result['rejections']
    if q <= 0 or len(rest) < 2:
        reject['minimum_and_arity'] = 'need a negative minimum with at least two companions'
        return result
    if not historical(t, c, rest, q):
        reject['historical_screen'] = 'companion constant mass'
        return result

    exterior = sorted(names - support)
    twins = {x} | {u for u in rest if all(c[x][z] == c[u][z] for z in names - {x, u})}
    inputs = tuple(sorted(support - twins))
    result['fresh_twins'], result['inputs'] = sorted(twins), inputs
    scale = (1 << len(twins)) - 1
    if len(support) > 3:
        forced = next((p for p in combinations(sorted(support), 3) if mono_triple(t, c, p) <= 0), None)
        if forced is not None:
            reject['proper_triples'] = forced
    if not inputs or len(twins) < max(1, 3 - len(inputs)):
        reject['funded_twin_roles'] = 'at least one inherited input and the arity floor'
    if not constant_inputs(t, c, inputs, scale * q):
        reject['constant_input_mass'] = 'inherited input count and constant mass disagree'
    if len(inputs) in (1, 2):
        differing = next((z for z in sorted(names - twins)
                          if len(inputs) * scale * c[x][z] != -sum(c[u][z] for u in inputs)), None)
        if differing is not None:
            reject['unary_binary_input_row'] = differing

    excessive = next((y for y in exterior if abs(c[x][y]) > q), None)
    if excessive is not None:
        reject['absolute_exterior'] = excessive
    impossible_pair = pair_projection(t, c, x, q, rest, exterior)
    if impossible_pair is not None:
        reject['companion_pair_exterior'] = impossible_pair
    impossible = triple_projection(t, c, x, q, rest, exterior)
    if impossible is not None:
        reject['companion_triple_exterior'] = impossible
    if len(inputs) >= 3:
        input_impossible = triple_projection(t, c, x, scale * q, inputs, exterior, scale)
        if input_impossible is not None:
            reject['input_triple_exterior'] = input_impossible
    return result


def controls(n, total, counts, rows, law):
    c = signed_table(n, total, counts)
    predictions = [inspect_name(total, c, x) for x in range(n)]
    own = [[] for _ in range(n)]
    for row in rows:
        for x in row:
            own[x].append(set(row))
    assert all(len(h) in (1, 2) for h in own)
    loose = {x for x in range(n) if len(own[x]) == 1}
    spent = set(range(n)) - loose
    by_test = {}
    active = set(range(n))
    baseline = {p['name'] for p in predictions if not set(TESTS[:2]).intersection(p['rejections'])}
    for t in TESTS:
        tested = active.copy()
        rejected = {p['name'] for p in predictions if t in p['rejections']}
        active -= rejected
        by_test[t] = {'entering_loose': len(tested & loose), 'entering_spent': len(tested & spent),
                      'excluded_loose': len(tested & rejected & loose), 'excluded_spent': len(tested & rejected & spent),
                      'retained_loose': len(active & loose), 'retained_spent': len(active & spent),
                      'standalone_spent_denominator': len(baseline & spent),
                      'standalone_baseline_excluded_spent': len(baseline & rejected & spent)}
    if law == 'nae':
        assert loose <= active
        for x in loose:
            p = predictions[x]
            assert set(p['support']) == own[x][0]
            assert set(p['fresh_twins']) == own[x][0] & loose
    else:
        assert all(c[a][b] in (0, total) for a, b in combinations(range(n), 2))
        assert not active
    return dict(actual_loose=sorted(loose), spent_names=len(spent), predictions=predictions,
                historical_false=sorted(baseline & spent), surviving_false=sorted(active & spent),
                per_test=by_test)
