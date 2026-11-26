"""Value and lift controls on the five-knot parity input with two exchanged branches."""
from collections import Counter
from itertools import permutations
import json
from table_rebuild import GROWTH, allowed_words, forbid, count_pairs, readings, lift, weights


def test():
    start = json.loads((GROWTH / 'starts.json').read_text())[3097]
    rows = forbid.supports_of(start)
    words = list(allowed_words(rows, 'parity'))
    first = lift(rows, (0, 2, 1, 4, 3))
    second = first[:]
    second[2], second[3], second[4], second[5] = 5, 4, 3, 2
    for p in [first, second]:
        assert all(p[p[d]] == d for d in range(len(p)))
        assert {tuple(sorted(p[d] for d in r)) for r in rows} == set(rows)
    projections = {}
    samples = []
    for w in words:
        def factors(p):
            pairs = [(i, j) for i, j in enumerate(p) if i < j]
            dif = sum(((w >> i) ^ (w >> j)) & 1 for i, j in pairs)
            return (weights(w, p)['odd number of double ones negative'], dif)
        (q, k), (r, l) = factors(first), factors(second)
        samples.append({'q first': q, 'q second': r, 'q product': q*r, 'q sum': q+r,
                        'q first on complement': weights(1023 ^ w, first)['odd number of double ones negative'],
                        'negative on two or three unlike pairs': (-1) ** (k*(k-1)//2),
                        'either lift has exactly two unlike pairs': -1 if 2 in (l,k) else 1})
    for key in samples[0]:
        masses = [s[key] for s in samples]
        tables = count_pairs(words, masses, 10)
        projections[key] = dict(totals=dict(Counter(masses)),linear=readings(tables,10,False),
                                squared=readings(tables,10,True))
    p = first
    posneg = {str(out): [format(w, '010b') for w,s in zip(words,samples) if w&1 == 0 and (w>>1)&1 == 1 and s['q first']==out] for out in (1,-1)}
    return dict(permutations=[first, second], results=projections, equal_reading_opposite_signs=posneg)


if __name__ == '__main__':
    print(json.dumps(test(), indent=1))
