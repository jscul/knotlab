"""Direct complete-word and named-rival controls for two wider not-all-equal holders."""
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
import json


class TruthColumns:
    """One bit for each assignment, including the two constant assignments."""
    def __init__(self, n):
        self.n = n
        assignments = 1 << n
        self.all = (1 << assignments) - 1
        self.ones = []
        for j in range(n):
            half = 1 << j
            repeat = self.all // ((1 << (2*half)) - 1)
            self.ones.append(repeat * (((1 << half) - 1) << half))
        self.pairs = {(i,j): self.ones[i] ^ self.ones[j] for i,j in combinations(range(n),2)}

    def allowed(self, names):
        all_one = all_zero = self.all
        for j in names:
            all_one &= self.ones[j]
            all_zero &= self.all ^ self.ones[j]
        return self.all ^ (all_zero | all_one)

    def correlations(self, words):
        size = words.bit_count()
        return {pair: 1 - 2*Fraction((words & col).bit_count(), size)
                for pair,col in self.pairs.items()}


def exact_case(q,r,k, rivals=False):
    n = q+r-k
    truth = TruthColumns(n)
    left = tuple(range(q))
    right = tuple(range(k)) + tuple(range(q,n))
    a,b = q-k,r-k
    support = truth.allowed(left) & truth.allowed(right)
    total = support.bit_count()
    assert total == (1 << n) - (1 << (a+1)) - (1 << (b+1)) + 2
    corr = truth.correlations(support)
    for (i,j), c in corr.items():
        formula = 2 - (1 << (b+1))*int(i in left and j in left)
        formula -= (1 << (a+1))*int(i in right and j in right)
        assert c == Fraction(formula,total)
    nonmixed = sum((support & ~truth.allowed(tri) != 0) for tri in combinations(range(n),3))
    assert nonmixed == n*(n-1)*(n-2)//6
    def pair(i,j):
        return corr[tuple(sorted((i,j)))]
    separations = sum(abs(pair(i,j)) <= abs(pair(i,h)*pair(h,j))
                      for i,j in combinations(range(n),2) for h in range(n) if h not in (i,j))
    if k >= 2:
        assert separations == 0
    sample = dict(arity=[q,r],shared=k,allowed=total,pair_correlations=sorted(set(map(str,corr.values()))),
                  no_strict_product=separations)
    if not rivals:
        return sample
    # Every triple realizes a constant in the target. A rule on three names
    # would force that triple to be mixed, which three pair rates detect.
    # Search a superset of lawful rivals: every named cover by supports >=4
    # with each name held once or twice, allowing repeated and implied rules.
    offers = [tuple(s) for m in range(4,n+1) for s in combinations(range(n),m)]
    masks = [sum(1 << i for i in names) for names in offers]
    words = [truth.allowed(names) for names in offers]
    cased = identical = 0
    readings = [(col, (support & col).bit_count()) for col in truth.pairs.values()]
    covers = []
    for m in range(1,2*n//4+1):
        for indexes in combinations_with_replacement(range(len(offers)),m):
            seen = twice = 0
            candidate = truth.all
            for idx in indexes:
                bits = masks[idx]
                if bits & twice:
                    break
                twice |= seen & bits
                seen |= bits
                candidate &= words[idx]
            else:
                if seen != (1 << n)-1 or not candidate:
                    continue
                cased += 1
                size = candidate.bit_count()
                if all(total*(col & candidate).bit_count() == size*ref for col,ref in readings):
                    identical += (candidate == support)
                    covers.append([offers[j] for j in indexes])
    sample.update(named_covers_considered=cased,matching_named_covers=covers,
                  matching_named_states_equal=identical)
    return sample


def multiple_meetings(private_sizes, meetings):
    """Decode a full exact table without giving the decoder the holder names."""
    holdings = [set() for _ in private_sizes]
    next_name = 0
    for holder, size in enumerate(private_sizes):
        holdings[holder].update(range(next_name, next_name + size))
        next_name += size
    for left, right, size in meetings:
        shared = range(next_name, next_name + size)
        holdings[left].update(shared)
        holdings[right].update(shared)
        next_name += size
    truth = TruthColumns(next_name)
    words = truth.all
    for holder in holdings:
        words &= truth.allowed(holder)
    corr = truth.correlations(words)

    def read(x, y):
        return corr[tuple(sorted((x, y)))]

    unseen = set(range(next_name))
    groups = []
    while unseen:
        x = min(unseen)
        group = {x}
        for y in unseen - {x}:
            if all(read(x, z) == read(y, z) for z in range(next_name) if z not in (x, y)):
                group.add(y)
        groups.append(tuple(sorted(group)))
        unseen -= group
    constant_chance = []
    for group in groups:
        i, j = group[:2]
        within = read(i, j)
        chance = within + (1 - within) * Fraction(1, 1 << (len(group) - 1))
        assert chance == Fraction((words & ~truth.allowed(group)).bit_count(), words.bit_count())
        constant_chance.append(chance)
    joined = set()
    for i, j in combinations(range(len(groups)), 2):
        x, y = groups[i][0], groups[j][0]
        if all(abs(read(x, y)) * constant_chance[k] > abs(read(x, g[0]) * read(g[0], y))
               for k, g in enumerate(groups) if k not in (i, j)):
            joined.add((i, j))
    recovered = []
    for width in range(len(groups), 1, -1):
        for members in combinations(range(len(groups)), width):
            if not all(pair in joined for pair in combinations(members, 2)):
                continue
            names = frozenset(n for m in members for n in groups[m])
            if not any(names <= other for other in recovered):
                recovered.append(names)
    assert set(map(frozenset, holdings)) == set(recovered)
    return dict(names=next_name, allowed=words.bit_count(), pair_numerators=len(corr),
                decoded_groups=groups, decoded_holdings=sorted(sorted(h) for h in recovered))


if __name__ == '__main__':
    required = [(4,4,3),(4,4,2),(4,5,3),(4,5,2)]
    beyond = [(4,4,1),(5,5,4),(5,6,2),(6,7,3),(8,7,5),(7,8,2)]
    print(json.dumps({"bare_named_competitors":[exact_case(*case,True) for case in required],
                      "further_literal_controls":[exact_case(*case) for case in beyond],
                      "later_advised_class_controls":[
                          multiple_meetings((2,2,2), ((0,1,2),(1,2,2))),
                          multiple_meetings((2,3,3), ((0,1,2),(1,2,3))),
                          multiple_meetings((2,2,2,2), ((0,1,2),(0,2,2),(0,3,2)))
                      ]},indent=2))
