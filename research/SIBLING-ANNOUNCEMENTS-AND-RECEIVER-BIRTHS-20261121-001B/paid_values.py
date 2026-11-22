"""All ordinary NAE value observations and constructive lifts on four paid siblings."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import lcm, prod

PAIRS = tuple(combinations(range(4), 2))
ROOTS = tuple(u for u in product((0, 1), repeat=4) if len(set(u)) == 2)
TRIPLES = tuple(product((0, 1), repeat=3))
COMPANIONS = tuple(tuple(j for j in range(4) if j != i) for i in range(4))
PAIR_KEYS = tuple((i, j) for i in range(4) for j in COMPANIONS[i])


def digits(word):
    return ''.join(map(str, word))


def local_legal(u, r):
    return any(v != u for v in r)


def fresh_choices(pair, grant):
    return tuple(digits(y) for y in product((0, 1), repeat=grant)
                 if len(set(pair + y)) == 2)


def distribution(full):
    """Classify complete, paid, fresh, or one-new-place access from the same integer masses."""
    full_key = lambda p, y: p + '/' + y
    views = {'whole_holding': full_key, 'paid_pair': lambda p, y: p,
             'fresh_roster': lambda p, y: y, 'one_fresh': lambda p, y: y[0]}
    answer = {}
    for name, project in views.items():
        cells = defaultdict(lambda: [0, 0])
        for (p, y), mass in sorted(full.items()):
            observed = cells[project(p, y)]
            for u in range(2):
                observed[u] += mass[u]
        denom = sum(sum(v) for v in cells.values())
        right = sum(max(v) for v in cells.values())
        tie = sum(sum(v) for v in cells.values() if v[0] == v[1])
        certain = sum(sum(v) for v in cells.values() if min(v) == 0)
        assert all(sum(v[u] for v in cells.values()) * 2 == denom for u in (0, 1))
        answer[name] = {'denominator': denom, 'best_correct_mass': right,
                        'best_accuracy': str(Fraction(right, denom)), 'tie_mass': tie,
                        'certain_mass': certain,
                        'cells_u0_u1': {key: v for key, v in sorted(cells.items())},
                        'p_u1_given_cell': {key: str(Fraction(v[1], sum(v)))
                                            for key, v in sorted(cells.items())}}
    return answer


def weighted_holdings(grant):
    """One exact partition function for each funding and all 4 physical focal choices."""
    keys = [(f, b, w) for f in range(4) for b in range(6)
            for w in ('old_uniform_then_local', 'complete_new_uniform')]
    totals = {key: defaultdict(lambda: [0, 0]) for key in keys}
    choices = {pair: fresh_choices(pair, grant)
               for pair in product((0, 1), repeat=2)}
    unit = lcm(*(len(y) for y in choices.values()))
    earlier = later = 0
    for rows in product(TRIPLES, repeat=4):
        roots = [u for u in ROOTS if all(local_legal(c, r) for c, r in zip(u, rows))]
        if not roots:
            continue
        earlier += len(roots)
        x = dict(zip(PAIR_KEYS, (b for r in rows for b in r)))
        pay = [(x[i, j], x[j, i]) for i, j in PAIRS]
        multiplicity = prod(len(choices[p]) for p in pay)
        later += len(roots) * multiplicity
        for focus in range(4):
            ones = sum(u[focus] for u in roots)
            zeros = len(roots) - ones
            for b, p in enumerate(pay):
                arr = choices[p]
                factors = (('old_uniform_then_local', unit // len(arr)),
                           ('complete_new_uniform', multiplicity // len(arr)))
                for w, factor in factors:
                    bank = totals[focus, b, w]
                    for y in arr:
                        counts = bank[digits(p), y]
                        counts[0] += zeros * factor
                        counts[1] += ones * factor
    assert earlier == 14 * 7 ** 4
    out = {}
    classes = defaultdict(set)
    for (f, b, w), bank in totals.items():
        result = distribution(bank)
        assert result['whole_holding']['denominator'] == (earlier * unit
            if w == 'old_uniform_then_local' else later)
        role = 'incident' if f in PAIRS[b] else 'nonincident'
        out[f'F{f}/B{digits(PAIRS[b])}/{w}'] = result
        for v, events in result.items():
            classes[(role, w, v)].add(events['best_accuracy'])
    assert all(len(v) == 1 for v in classes.values())
    return {'grant': grant, 'earlier_words': earlier, 'complete_next_words': later,
            'old_uniform_integer_unit': unit, 'by_physical_case': out,
            'class_accuracy': {'/'.join(k): v.pop() for k, v in sorted(classes.items())}}


def rows_from_directed(x):
    return tuple(tuple(x[i, j] for j in COMPANIONS[i]) for i in range(4))


def validate_pins(x, subsets, fixed):
    for (i, j), (a, b) in zip(subsets, fixed, strict=True):
        assert (x[i, j], x[j, i]) == (a, b)
    for (i, j) in PAIRS:
        if (i, j) not in subsets:
            assert x[i, j] != x[j, i]


def support_lifts():
    """Every certificate leaves arbitrary already lawful future values intact."""
    sparse = []
    for size in (0, 1, 2):
        for fixed_pairs in combinations(PAIRS, size):
            free = [e for e in PAIRS if e not in fixed_pairs]
            for fixed in product(tuple(product((0, 1), repeat=2)), repeat=size):
                x = {}
                for (i, j), (a, b) in zip(fixed_pairs, fixed, strict=True):
                    x[i, j], x[j, i] = a, b
                for orientations in product((0, 1), repeat=len(free)):
                    for (i, j), a in zip(free, orientations, strict=True):
                        x[i, j], x[j, i] = a, 1-a
                    rows = rows_from_directed(x)
                    if all(len(set(r)) == 2 for r in rows):
                        break
                else:
                    raise AssertionError((fixed_pairs, fixed))
                validate_pins(x, fixed_pairs, fixed)
                assert all(all(local_legal(c, r) for c, r in zip(u, rows)) for u in ROOTS)
                sparse.append([list(map(digits, fixed_pairs)), list(map(digits, fixed)), list(map(digits, rows))])
    focal = []
    sibling = []
    star = []
    for f in range(4):
        tri = COMPANIONS[f]
        internals = tuple(combinations(tri, 2))
        for u in ROOTS:
            for x0 in TRIPLES:
                if not local_legal(u[f], x0):
                    continue
                x = {(f,j):b for j,b in zip(tri, x0)}
                x.update({(j,f):1-b for j,b in zip(tri, x0)})
                for i,j in zip(tri, tri[1:]+tri[:1]):
                    x[i,j], x[j,i] = 0,1
                rows = rows_from_directed(x)
                validate_pins(x, (), ())
                assert rows[f] == x0 and all(local_legal(c,r) for c,r in zip(u,rows))
                focal.append([f, digits(u), digits(x0), list(map(digits,rows))])
            for fixed in product(tuple(product((0,1),repeat=2)), repeat=3):
                x = {}
                for (i,j),(a,b) in zip(internals,fixed,strict=True):
                    x[i,j], x[j,i] = a,b
                for j in tri:
                    x[f,j], x[j,f] = u[j], 1-u[j]
                validate_pins(x,internals,fixed)
                rows = rows_from_directed(x)
                assert all(local_legal(c,r) for c,r in zip(u,rows))
                sibling.append([f,digits(u),list(map(digits,fixed)),list(map(digits,rows))])
        for h in (0,1):
            rows = [tuple(h if j==f else 1-h for j in COMPANIONS[i]) for i in range(4)]
            rows[f] = (h,h,h)
            matching = [digits(u) for u in ROOTS if all(local_legal(c,r) for c,r in zip(u,rows))]
            assert matching and all(int(u[f])==1-h for u in matching)
            star.append([f,h,list(map(digits,rows)),matching])
    return {'all_sparse_inputs_and_one_mixed_lift': sparse,
            'sparse_records':len(sparse), 'sparse_root_lifts':14*len(sparse),
            'all_focal_word_and_future_lifts':focal, 'focal_records':len(focal),
            'sibling_only_paid_bank_lifts':sibling, 'sibling_records':len(sibling),
            'three_incident_which_word_examples':star}


def sibling_guess():
    """Reach the actual three-parent sibling receiver using both named priors at age two.

    Its three true parents each give one of their two fresh places. Given their input
    pairs their local fresh words are independent. At this receiver choose uniformly
    among lawful one-place extensions; other children retain their own private places.
    """
    choices = {pair: fresh_choices(pair, 2) for pair in product((0,1), repeat=2)}
    counts = {(f,w):defaultdict(lambda:[0,0]) for f in range(4) for w in
              ('old_uniform_through_two_cuts','uniform_complete_second_cut')}
    # Each of the three consumed places has marginal denominator dividing 12.
    local_unit = 12**3
    for rows in product(TRIPLES,repeat=4):
        roots = [u for u in ROOTS if all(local_legal(c,r) for c,r in zip(u,rows))]
        if not roots:
            continue
        x=dict(zip(PAIR_KEYS,(v for r in rows for v in r)))
        y={e:choices[(x[e],x[e[1],e[0]])] for e in PAIRS}
        mult=prod(map(len,y.values()))
        for f in range(4):
            used=tuple(combinations(COMPANIONS[f],2))
            common=prod(len(y[e]) for e in used)
            ones=sum(u[f] for u in roots)
            mass=(len(roots)-ones,ones)
            for v in TRIPLES:
                reps=prod(sum(word[0]==str(b) for word in y[e]) for e,b in zip(used,v))
                if not reps: continue
                z=tuple(a for a in (0,1) if len(set(v+(a,)))==2)
                for w,unit in [('old_uniform_through_two_cuts',local_unit),
                               ('uniform_complete_second_cut',mult)]:
                    assert unit%common==0
                    weight=unit//common*reps*(2//len(z))
                    for a in z:
                        cell=counts[f,w][(digits(v),str(a))]
                        for c in (0,1):
                            cell[c]+=mass[c]*weight
    answers = {}
    for (f, w), cells in counts.items():
        result = distribution(cells)
        result['three_paid_inputs'] = result.pop('paid_pair')
        answers[f'F{f}/{w}'] = result
    return answers
