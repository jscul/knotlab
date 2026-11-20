"""Independent exact parity trace calculation after eliminating each passive pair of knots."""
from collections import Counter
from fractions import Fraction
from itertools import product

SETTINGS = tuple(product(range(2), repeat=2))
WORDS = tuple(product(range(2), repeat=3))


def permute(word, indices, active):
    if not active:
        return word
    values = list(word)
    first, second = indices
    values[first], values[second] = values[second], values[first]
    return tuple(values)


def outputs(x, y, bias=Fraction(1, 2), reveal="endpoint", switch="ordinary", funding="ordinary", policy="fixed"):
    pair_table, alice_record, bob_record = Counter(), Counter(), Counter()
    for u, v in SETTINGS:
        ready_a, ready_b = x == u, y == v
        if policy in ("bob_responds", "both_respond"):
            ready_b = bool(y)  # y is an independent message selecting a local action.
        if policy == "both_respond":
            ready_a = True
        funded = ready_a and ready_b
        birth_a, birth_b = (ready_a, ready_b) if funding == "separate" else (funded, funded)
        if funding == "always":
            birth_a = birth_b = True
        weight = (bias if v else 1 - bias) / (2 * len(WORDS))
        for left in WORDS:
            p, q = (0, 1), (1, 2) if switch == "ordinary" else (0, 1)
            after_p = permute(left, p, u)
            after_q = permute(after_p, q, v)
            after_second_p = permute(after_q, p, u)
            right = permute(after_second_p, q, v)
            a, b = int(birth_a and left[0]), int(birth_b and right[0])
            alice = (u, left, birth_a, a)
            bob = (v, right, birth_b, b)
            if reveal == "preparation":
                alice += (v,)
                bob += (u,)
            if reveal == "switches":
                alice += (after_p, after_q)
                bob += (after_q, after_second_p)
            pair_table[a, b] += weight
            alice_record[alice] += weight
            bob_record[bob] += weight
    assert sum(pair_table.values()) == sum(alice_record.values()) == sum(bob_record.values()) == 1
    return pair_table, alice_record, bob_record


def tv(p, q):
    return sum(abs(p[key] - q[key]) for key in p.keys() | q.keys()) / 2


def analysis(**options):
    tables = {xy: outputs(*xy, **options) for xy in SETTINGS}
    correlations = [sum((-1)**(a + b) * v for (a, b), v in tables[xy][0].items()) for xy in SETTINGS]
    signed = sum(correlations[:3]) - correlations[3]
    record_tv = ([tv(tables[x, 0][1], tables[x, 1][1]) for x in range(2)],
                 [tv(tables[0, y][2], tables[1, y][2]) for y in range(2)])
    selected_tv = ([abs(sum(v for (a,b),v in tables[x,0][0].items() if a) -
                        sum(v for (a,b),v in tables[x,1][0].items() if a)) for x in range(2)],
                   [abs(sum(v for (a,b),v in tables[0,y][0].items() if b) -
                        sum(v for (a,b),v in tables[1,y][0].items() if b)) for y in range(2)])
    return correlations, signed, selected_tv, record_tv, tables


if __name__ == "__main__":
    for name, settings in [("hidden", {}), ("underlying types revealed", dict(reveal="preparation")),
                           ("interior accessible", dict(reveal="switches")), ("biased", dict(bias=Fraction(3,4))),
                           ("commuting", dict(switch="commuting")), ("cancel per side", dict(funding="separate")),
                           ("always funded", dict(funding="always")), ("free message at Bob", dict(policy="bob_responds")),
                           ("always-ready Alice", dict(policy="both_respond"))]:
        e, s, bit, record, tables = analysis(**settings)
        print(name, "E", tuple(map(str,e)), "S",s,"TV bits",bit,"TV records",record)
        if name == "hidden":
            assert s == Fraction(9,4) and all(v == 0 for wing in record for v in wing)
            assert [[tables[xy][0][ab]*32 for ab in SETTINGS] for xy in SETTINGS] == [
                [28,0,0,4], [28,0,0,4], [28,0,0,4], [26,2,2,2]]
        elif name == "underlying types revealed":
            assert all(v == Fraction(1,2) for wing in record for v in wing)
        elif name == "biased":
            assert bit[0] == [Fraction(1,8)] * 2 and record[0] == [Fraction(1,4)] * 2
        elif name == "interior accessible":
            assert all(v == Fraction(1,4) for wing in record for v in wing)
        elif name == "free message at Bob":
            assert record[0] == [Fraction(1,2)]*2 and bit[0] == [Fraction(1,4)]*2
        elif name == "always-ready Alice":
            assert record[0] == [1]*2 and bit[0] == [Fraction(1,2)]*2
        else:
            assert abs(s) <= 2
