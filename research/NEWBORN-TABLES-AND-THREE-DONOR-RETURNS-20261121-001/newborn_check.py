"""Check settings on one actual first-round child, independently of the scientific replay."""

from collections import Counter
from fractions import Fraction as F
from itertools import product


def bits(n):
    return list(product((0, 1), repeat=n))


TRIPLES = bits(3)


def allowed(word, law):
    return sum(word) % 2 == 0 if law == "parity" else len(set(word)) == 2


def newborn_matrix(width, law, clean):
    # An isolated original makes one unary child per old place. All children
    # share that original. Their next groups are pairs, hence width-1 fresh
    # places per child for the widths in this test.
    fresh = width - 1
    starts = [s for s in bits(width) if allowed(s, law)]
    children = {b: {v for v in bits(fresh) if allowed((b,) + v, law)} for b in (0, 1)}
    overlaps = {(a, b): len(children[a] & children[b]) for a, b in bits(2)}
    suffixes = bits(fresh - 3)
    factors = Counter()
    for old in starts:
        for other in (starts if clean else (old,)):
            scale = 1
            for a, b in zip(old[1:], other[1:]):
                scale *= overlaps[a, b]
            factors[old[0], other[0]] += scale
    matrix = {}
    for x, y in product(TRIPLES, repeat=2):
        matrix[x, y] = sum(
            multiplicity
            for (a, b), multiplicity in factors.items()
            for exterior in suffixes
            if x + exterior in children[a] and y + exterior in children[b]
        )
    return matrix


def setting_table(matrix):
    trace = sum(matrix[w, w] for w in TRIPLES)
    table = {}
    for change, outcome in product(TRIPLES, repeat=2):
        total = 0
        for (x, y), weight in matrix.items():
            if any(not flag and (x[i] != outcome[i] or y[i] != outcome[i])
                   for i, flag in enumerate(change)):
                continue
            phase = sum(outcome[i] * (x[i] ^ y[i]) for i, flag in enumerate(change) if flag)
            total += (-1) ** phase * weight
        table[change, outcome] = F(total, trace * 2 ** sum(change))
    assert all(sum(table[c, v] for v in TRIPLES) == 1 for c in TRIPLES)
    return table, trace


def answer_lists(table, law):
    zero, one = (0, 0, 0), (1, 1, 1)
    mixed_z = sum(table[zero, z] for z in TRIPLES if 0 < sum(z) < 3)
    all_plus_x = table[one, zero]
    weights = {}
    for z, x in product(TRIPLES, repeat=2):
        prob_x = table[one, x]
        if law == "parity":
            p = table[zero, z] * prob_x
        elif 0 < sum(z) < 3:
            p = mixed_z / 6 if x == zero else F(0)
        else:
            p = (prob_x - (mixed_z if x == zero else 0)) / 2
        weights[z, x] = p
    assert min(weights.values()) >= 0 and sum(weights.values()) == 1
    for setting in TRIPLES:
        marginal = Counter()
        for (z, x), p in weights.items():
            observed = tuple((x if flag else z)[i] for i, flag in enumerate(setting))
            marginal[observed] += p
        assert all(marginal[v] == table[setting, v] for v in TRIPLES)
    return mixed_z, all_plus_x


def direct_four(law, clean):
    # Verify the contraction once without identifying repeated child factors.
    olds = [s for s in bits(4) if allowed(s, law)]
    rows = Counter()
    for exterior in product(TRIPLES, repeat=3):
        for s in olds:
            if not all(allowed((b,) + v, law) for b, v in zip(s[1:], exterior)):
                continue
            tag = (exterior,) if clean else (exterior, s)
            rows[tag, s[0]] += 1
    result = Counter()
    for tag in {k[0] for k in rows}:
        amp = {x: sum(rows[tag, b] for b in (0, 1) if allowed((b,) + x, law)) for x in TRIPLES}
        for x, y in product(TRIPLES, repeat=2):
            result[x, y] += amp[x] * amp[y]
    return result


def disclosed_parent_check():
    # First-round four-place not-all-equal child. The paid bit can be announced
    # before the three settings. Each value has half the full launches.
    for excluded in (0, 1):
        amplitude = {w: int(w != (excluded,) * 3) for w in TRIPLES}
        rho = {(x, y): amplitude[x] * amplitude[y] for x, y in product(TRIPLES, repeat=2)}
        table, _ = setting_table(rho)
        all_x, all_z = (1, 1, 1), (0, 0, 0)
        lhs = sum(table[all_x, ans] for ans in TRIPLES if sum(ans) >= 2)
        rhs = table[all_z, (excluded,) * 3]
        for i in range(3):
            settings = tuple(int(j == i) for j in range(3))
            rhs += sum(table[settings, ans] for ans in TRIPLES
                       if ans[i] and any(ans[j] != excluded for j in range(3) if j != i))
        assert lhs - rhs == F(1, 14)
        bounds = []
        for z, x in product(TRIPLES, repeat=2):
            bad = int(z == (excluded,) * 3)
            bad += sum(bool(x[i]) and any(z[j] != excluded for j in range(3) if j != i)
                       for i in range(3))
            bounds.append(int(sum(x) >= 2) - bad)
        assert max(bounds) == 0
        print("announced paid bit", excluded, "herald", F(1, 2), "witness", lhs - rhs)

    for val in (0, 1):
        sibling_words = [(val,) * 3] * 3
        old = [s for s in bits(4) if allowed(s, "not-all-equal")
               and all(allowed((b,) + v, "not-all-equal") for b, v in zip(s[1:], sibling_words))]
        assert old == [(val, 1 - val, 1 - val, 1 - val)]
        assert sum(allowed((val,) + w, "not-all-equal") for w in TRIPLES) == 7
        retained = sum(newborn_matrix(4, "not-all-equal", False)[w, w] for w in TRIPLES)
        clean = sum(newborn_matrix(4, "not-all-equal", True)[w, w] for w in TRIPLES)
        assert (F(7, retained), F(7, clean), F(7, 16 * retained)) == (
            F(1, 4802), F(1, 50018), F(1, 76832)
        )


def main():
    disclosed_parent_check()
    for w, law in product((4, 5), ("parity", "not-all-equal")):
        totals = []
        for clean in (False, True):
            matrix = newborn_matrix(w, law, clean)
            if w == 4:
                assert matrix == direct_four(law, clean)
            table, trace = setting_table(matrix)
            mixed, plus = answer_lists(table, law)
            print(w, law, "clean" if clean else "retained", "normalizer", trace,
                  "ordinary mixed", mixed, "all changes plus", plus)
            totals.append(trace)
        print("clean launches", F(totals[1], (2**w) * totals[0]))
    # Sector and its simultaneous ordinary complement, with true trace
    # weights. The first slot of each vector is 000 and the last is 111.
    for den in range(1, 7):
        for i, j in product(range(den + 1), repeat=2):
            if i + j < den:
                continue
            a = [i] + [den] * 6 + [j]
            rho = {(x, y): a[m]*a[n] + a[7-m]*a[7-n] for m,x in enumerate(TRIPLES)
                   for n,y in enumerate(TRIPLES)}
            table, _ = setting_table(rho)
            answer_lists(table, "not-all-equal")
    print("Every one of the eight settings and eight outcomes matched its answer-list marginal.")


if __name__ == "__main__":
    main()
