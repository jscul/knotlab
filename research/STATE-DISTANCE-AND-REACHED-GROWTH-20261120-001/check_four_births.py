"""Exact inverse checks for the 28-name second cut from one four-place knot."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import lcm
import json


PAIRS = list(combinations(range(4), 2))


def constructor():
    """Name the four earlier live holders and their six two-parent children."""
    center = tuple(range(4))
    old = [[i] for i in range(4)]
    following = []
    for i, j in PAIRS:
        a, b = 4 + i * 3 + len(old[i]) - 1, 4 + j * 3 + len(old[j]) - 1
        old[i].append(a)
        old[j].append(b)
        fresh = 16 + 2 * len(following)
        following.append((a, b, fresh, fresh + 1))
    return [center, *map(tuple, old), *following]


def signed_counts(n, holders):
    """Inclusion-exclusion over constant holders; no word sample."""
    sums = [[0] * n for _ in range(n)]
    total = 0
    for mask in range(1 << len(holders)):
        parent = list(range(n))
        def root(x):
            while x != parent[x]:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, holder in enumerate(holders):
            if (mask >> i) & 1:
                base = root(holder[0])
                for x in holder[1:]:
                    parent[root(x)] = base
        groups = {}
        for x in range(n):
            groups.setdefault(root(x), []).append(x)
        weight = (-1 if mask.bit_count() % 2 else 1) << len(groups)
        total += weight
        for members in groups.values():
            for x, y in combinations(members, 2):
                sums[x][y] += weight
                sums[y][x] += weight
    for x in range(n):
        sums[x][x] = total
    return total, sums


def uniform_table(n, holders):
    total, sums = signed_counts(n, holders)
    return total, [[Fraction(v, total) for v in row] for row in sums]


def inherited_table(holders):
    """First-cut words are equiprobable. Average conditional second-cut pairs."""
    n = 28
    rows = [[0] * n for _ in range(n)]
    population = 0
    fresh_pairs = {(a, b) for _, _, a, b in holders[5:]}
    # Conditional sign means are multiples of 1/3. One old word has one vote.
    for word in range(1 << 16):
        bits = [(word >> i) & 1 for i in range(16)]
        if any(len({bits[i] for i in h}) == 1 for h in holders[:5]):
            continue
        population += 1
        means = [3 * (1 - 2 * b) for b in bits]
        for a, b, _, _ in holders[5:]:
            mean = -(1 - 2 * bits[a]) if bits[a] == bits[b] else 0
            means.extend([mean, mean])
        for i, x in enumerate(means):
            for j in range(i+1, n):
                amount = x * means[j]
                if (i,j) in fresh_pairs:
                    amount = -3 if x else 0
                rows[i][j] += amount
    table = [[Fraction(1) if i == j else Fraction(rows[min(i,j)][max(i,j)], 9*population)
              for j in range(n)] for i in range(n)]
    return population, table


def possible_loose(table):
    """No marked roles. Filter minimum groups using the probabilities they force."""
    n = len(table)
    skipped = Counter()
    viable = {}
    for x in range(n):
        minimum = min(v for y,v in enumerate(table[x]) if x != y)
        others = tuple(y for y in range(n) if x != y and table[x][y] == minimum)
        if len(others) < 2:
            skipped['too few places'] += 1
            continue
        def all_equal(triple):
            return (1 + sum(table[i][j] for i,j in combinations(triple,2))) / 4
        # Other physical positions can be constant exactly with probability -minimum.
        if len(others) == 2 and (1 + table[others[0]][others[1]])/2 != -minimum:
            skipped['two-name constant probability'] += 1
        elif len(others) == 3 and all_equal(others) != -minimum:
            skipped['three-name constant probability'] += 1
        elif len(others) > 3 and any(all_equal(sub) <= -minimum for sub in combinations(others,3)):
            # Full projection includes a word constant on the triple and mixed on the remainder.
            skipped['proper triple must have strictly larger constant probability'] += 1
        else:
            viable[x] = tuple(sorted((x, *others)))
    return viable, dict(skipped)


def old_holder(table, fresh, old, young, inherited):
    candidates = {z: table[old][z] if inherited else table[old][z] - table[fresh][z]
                  for z in range(len(table)) if z not in (young if inherited else (fresh,old))}
    least = min(candidates.values())
    return tuple(sorted([old] + [z for z,v in candidates.items() if v==least]))


def next_groups(edges):
    """At this cut the physical witnesses are the former parents at each endpoint."""
    def coheld(i, j):
        return bool(set(edges[i]) & set(edges[j]))
    groups = []
    ids = range(len(edges))
    for triple in combinations(ids,3):
        if all(coheld(i,j) for i,j in combinations(triple,2)) and not set.intersection(*(set(edges[i]) for i in triple)):
            groups.append(triple)
    for i,j in combinations(ids,2):
        if coheld(i,j) and not any(i in group and j in group for group in groups):
            groups.append((i,j))
    return groups


def cycle_rival(residual):
    """Four earlier live holders and four witnesses, all with four positions."""
    cycle = [(0,1), (1,2), (2,3), (0,3)]
    old = [[] for _ in range(4)]
    witnesses = [[] for _ in range(4)]
    new = []
    for i,(a,b) in enumerate(cycle):
        old[a].extend((2*i,8+2*i))
        old[b].extend((2*i+1,9+2*i))
        witnesses[i].extend((8+2*i,9+2*i))
        new.append((2*i,2*i+1,20+2*i,21+2*i))
    for i,(a,b) in enumerate(residual):
        witnesses[a].append(16+i)
        witnesses[b].append(16+i)
    return old + witnesses, new


def run():
    holders = constructor()
    n = 28
    total,uniform = uniform_table(n,holders)
    previous_total,inherited = inherited_table(holders)
    res = {}
    for label,table in [('uniform',uniform),('inherited',inherited)]:
        viable,skipped = possible_loose(table)
        # Some inherited middle names produce a ternary candidate, separately ruled out
        # by the same table-wide ternary condition used for all competing holders.
        forced_triples = [tri for tri in combinations(range(n),3) if
                          sum(table[i][j] for i,j in combinations(tri,2)) == -1]
        assert not forced_triples
        viable = {x:h for x,h in viable.items() if len(h)>=4}
        assert set(viable) == set(range(16,28))
        young = sorted(set(viable.values()))
        assert set(young) == set(holders[5:])
        old_rows = {}
        for h in young:
            f = max(h)
            for x in sorted(h)[:2]:
                k = old_holder(table,f,x,h,label=='inherited')
                assert len(k)==4 and k in holders[1:5]
                old_rows[x] = k
        res[label] = dict(loose_candidates=viable,excluded=skipped,forced_triples=forced_triples,
                          old_parent_containment=old_rows)
    compatible = []
    for width in range(1,7):
        for es in combinations(PAIRS,width):
            groups = next_groups(es)
            if all(sum(j in g for g in groups)==2 for j in range(width)):
                degrees = [sum(i in edge for edge in es) for i in range(4)]
                compatible.append([es,groups,degrees])
    res['funding_compatible_subsets_of_63'] = compatible
    residuals = [tuple(e for e in PAIRS if e not in matching) for matching in combinations(PAIRS,2)
                 if len(set().union(*matching))==4]
    residuals += [tuple(e for e in matching for _ in range(2)) for matching in combinations(PAIRS,2)
                  if len(set().union(*matching))==4]
    reported_den = lcm(*(((1-uniform[i][j])/2).denominator for i,j in combinations(range(28),2)))
    assert reported_den > 1
    # Compute the denominator of the actual inherited old marginal after the putative
    # last fresh names are excluded. A common relabeling preserves this denominator.
    actual_cycle = {(0,1),(1,2),(2,3),(0,3)}
    retained = set(range(28))
    for edge,h in zip(PAIRS,holders[5:]):
        if edge in actual_cycle:
            retained.difference_update(h[-2:])
    old_den = lcm(*(((1-inherited[i][j])/2).denominator for i,j in combinations(sorted(retained),2)))
    tests=[]
    for m in residuals:
        pre, new = cycle_rival(m)
        pre_total,_ = signed_counts(20,pre)
        full_total,_ = signed_counts(28,pre+new)
        assert full_total % reported_den != 0
        assert pre_total % old_den != 0
        tests.append(dict(residual=m,previous_allowed=pre_total,current_allowed=full_total))
    res.update(uniform_allowed=total,uniform_pair_denominator=reported_den,
               previous_words_inherited_mass_averaged=previous_total,
               inherited_old_marginal_denominator=old_den,all_six_cycle_placements=tests,
               unique_current_holdings=holders,next_birth_parent_indices=next_groups(PAIRS))
    return res


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
