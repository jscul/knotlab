"""Check pair-rate recovery on wider branches attached to ternary cores."""
from fractions import Fraction
from itertools import combinations
import json


def count(states, support):
    """Return the allowed assignments of a not-all-equal holder as a bit set."""
    every_word, columns = states
    zeros = ones = every_word
    for i in support:
        ones &= columns[i]
        zeros &= ~columns[i]
    return every_word ^ (zeros | ones)


def read(holders):
    size = max(map(max, holders)) + 1
    every_word = (1 << (1 << size)) - 1
    col = []
    for i in range(size):
        length = 1 << i
        copies = every_word // ((1 << (2*length)) - 1)
        col.append(copies * (((1 << length)-1) << length))
    restrictions = [count((every_word, col), h) for h in holders]
    allowed = every_word
    for rule in restrictions:
        allowed &= rule
    for omit in range(len(holders)):
        relaxed = every_word
        for j, rule in enumerate(restrictions):
            if j != omit:
                relaxed &= rule
        assert relaxed != allowed
    number = allowed.bit_count()
    C = {}
    for i in range(size):
        for j in range(size):
            disagree = (allowed & (col[i] ^ col[j])).bit_count()
            C[i,j] = 1 - 2 * Fraction(disagree, number)
            if i != j:
                assert abs(C[i,j]) < 1
    implied_triples = [h for h in combinations(range(size), 3)
                       if 1 + sum(C[i,j] for i,j in combinations(h, 2)) == 0]
    core = {i for h in implied_triples for i in h}
    assert core == {i for h in holders if len(h) == 3 for i in h}
    # Connected collections of forbidden constant triples identify the ternary parts.
    parts = []
    for triple in implied_triples:
        merged = [part for part in parts if set(triple) & part]
        parts = [part for part in parts if part not in merged]
        parts.append(set(triple).union(*merged))
    joined = {i: set() for i in range(size)}
    for i,j in combinations(range(size),2):
        if any({i,j} <= part for part in parts):
            continue
        if not any(C[i,k]*C[k,j] == C[i,j] for k in range(size) if k not in (i,j)):
            joined[i].add(j)
            joined[j].add(i)
    wide = set()
    for i, others in joined.items():
        for j in others:
            common = (joined[i] | {i}) & (joined[j] | {j})
            if len(common) >= 4:
                wide.add(tuple(sorted(common)))
    assert wide == {tuple(sorted(h)) for h in holders if len(h)>3}
    decoded = every_word
    for h in list(wide) + implied_triples:
        decoded &= count((every_word,col),h)
    assert decoded == allowed
    return {"names":size, "words": number, "core_names":sorted(core),
            "wide_holdings_recovered":[list(h) for h in sorted(wide)]}


if __name__ == "__main__":
    fixtures = {
        "two levels of wide branches":[[0,1,2],[0,3,4,5],[3,6,7,8,9],[1,10,11,12]],
        "three mutually meeting core holders":[[0,1,3],[0,2,4],[1,2,5],[3,6,7,8],[6,9,10,11,12],[4,13,14,15]],
        "a core with a repeated meeting":[[0,1,2],[0,1,3],[2,4,5,6],[3,7,8,9,10]],
        "two mutually meeting cores joined through a wide holder":[
            [0,1,3],[0,2,4],[1,2,5],[6,7,9],[6,8,10],[7,8,11],[3,9,12,13],[12,14,15,16]],
        "three repeated-meeting cores on one wide holder":[
            [0,1,2],[0,1,3],[4,5,6],[4,5,7],[8,9,10],[8,9,11],[2,6,10,12,13]],
    }
    print(json.dumps({label: read(h) for label, h in fixtures.items()}, indent=2))
