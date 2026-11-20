"""Exact Boolean measurements and independent ordinary first-step replay."""
from collections import Counter, defaultdict
from itertools import combinations, product

from pysat.solvers import Solver


def bits(mask):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def mask_of(items):
    return sum(1 << i for i in set(items))


def width(rows):
    return max(max(r) for r in rows) + 1


def accepts(rows, state, law):
    for row in rows:
        weight = sum((state >> i) & 1 for i in row)
        if (weight % 2 if law == 'parity' else weight in (0, len(row))):
            return False
    return True


def allowed(rows, law):
    return tuple(s for s in range(1 << width(rows)) if accepts(rows, s, law))


def literal_counts(states, n):
    return len(states), {(i, j): sum(((x >> i) ^ (x >> j)) & 1 for x in states)
                         for i, j in combinations(range(n), 2)}


def reduced(rows):
    basis = {}
    for x in rows:
        for k in sorted(basis, reverse=True):
            if x & (1 << k):
                x ^= basis[k]
        if x:
            k = x.bit_length() - 1
            for j in basis:
                if basis[j] & (1 << k):
                    basis[j] ^= x
            basis[k] = x
    return tuple(basis[k] for k in sorted(basis, reverse=True))


def spanned(x, basis):
    for b in basis:
        if x & (1 << (b.bit_length() - 1)):
            x ^= b
    return x == 0


def parity_counts(rows):
    n = width(rows)
    basis = reduced(map(mask_of, rows))
    count = 1 << (n - len(basis))
    return count, {(i, j): 0 if spanned((1 << i) | (1 << j), basis) else count // 2
                   for i, j in combinations(range(n), 2)}


def parity_local(rows):
    """Number of independent constraints supported entirely inside each row."""
    checks = tuple(map(mask_of, rows))
    rank = len(reduced(checks))
    return [rank - len(reduced(x & ~scope for x in checks)) for scope in checks]


def parity_bonds(rows):
    sums = {0}
    for check in reduced(map(mask_of, rows)):
        sums |= {s ^ check for s in sums}
    answer = []
    for support in sorted(sums - {0}, key=int.bit_count):
        if all(b & support != b for b in answer):
            answer.append(support)
    return frozenset(answer)


def nae_solver(rows):
    clauses = []
    for row in rows:
        positive = [i + 1 for i in row]
        clauses.extend((positive, [-v for v in positive]))
    return Solver(name='g3', bootstrap_with=clauses)


def nae_lawful(rows):
    with nae_solver(rows) as sat:
        for row in rows:
            # Global complement exchanges the two values of the first mark.
            for tail in product((0, 1), repeat=len(row)-1):
                if not any(tail):
                    continue
                word = (0, *tail)
                pinned = [i+1 if b else -i-1 for i, b in zip(row, word)]
                if not sat.solve(assumptions=pinned):
                    return False
    return True


def nae_separator(rows, other):
    """A named word satisfying rows and monochromatic on a support of other."""
    assert width(rows) == width(other)
    with nae_solver(rows) as sat:
        for k, row in enumerate(other):
            if sat.solve(assumptions=[-i-1 for i in row]):
                word = mask_of(v-1 for v in sat.get_model() if v > 0)
                assert accepts(rows, word, 'nae') and not accepts(other, word, 'nae')
                return {'violated_holder': k, 'ones': list(bits(word))}
    return None


def nae_counts(rows):
    """Inclusion-exclusion over monochromatic holdings, quotienting equal marks.

    For a fixed subset of failed holdings all marks in each joined block
    agree. A pair in different blocks disagrees on exactly half the assignments.
    Accumulating coefficients for a whole block avoids a pair loop per subset.
    """
    n = width(rows)
    scopes = tuple(set(map(mask_of, rows)))
    coefficients = Counter()
    total = 0

    def visit(i, blocks, weight):
        nonlocal total
        if i == len(scopes):
            total += weight
            for block in blocks:
                coefficients[block] += weight
            return
        visit(i + 1, blocks, weight)
        united = scopes[i]
        untouched = []
        old_rank = 0
        for block in blocks:
            if block & scopes[i]:
                united |= block
                old_rank += block.bit_count() - 1
            else:
                untouched.append(block)
        extra_rank = united.bit_count() - 1 - old_rank
        visit(i + 1, (*untouched, united), -(weight >> extra_rank))

    visit(0, (), 1 << n)
    pairs = {(i, j): total for i, j in combinations(range(n), 2)}
    for block, coefficient in coefficients.items():
        if coefficient:
            for ij in combinations(bits(block), 2):
                pairs[ij] -= coefficient
    assert all(d % 2 == 0 and 0 <= d <= 2*total for d in pairs.values())
    return total, {ij: d // 2 for ij, d in pairs.items()}


def ownership(rows):
    owners = defaultdict(list)
    for i, row in enumerate(rows):
        for x in row:
            owners[x].append(i)
    return owners


def groups(live, witnesses):
    """Maximal unheld pairwise witnessed groups, then uncovered witnessed pairs."""
    live = sorted(live)
    joined = {pair for w in witnesses for pair in combinations(sorted(w), 2)}
    # Only maximal cliques need be tested: once unheld, every enlargement
    # remains unheld. Subsets of a held maximal clique are all held.
    neighbors = {u: set() for u in live}
    for i,j in joined:
        neighbors[i].add(j)
        neighbors[j].add(i)
    maximal = []
    def extend(clique, possible, excluded):
        if not possible and not excluded:
            if len(clique) >= 3 and not any(clique <= w for w in witnesses):
                maximal.append(tuple(sorted(clique)))
            return
        pivot = max(possible | excluded, key=lambda x: len(possible & neighbors[x]))
        for v in sorted(possible - neighbors[pivot]):
            extend(clique | {v}, possible & neighbors[v], excluded & neighbors[v])
            possible.remove(v)
            excluded.add(v)
    if live:
        extend(set(), set(live), set())
    covered = {ij for clique in maximal for ij in combinations(clique, 2)}
    return tuple(sorted((*maximal, *(joined-covered))))


def growth(rows, law):
    """Connected old source; apply only the archived complete-step rule."""
    owner = ownership(rows)
    loose = Counter(h[0] for h in owner.values() if len(h) == 1)
    if not loose:
        return 'closed', ()
    witnesses = [set() for _ in rows]
    for h in owner.values():
        if len(h) == 2:
            a,b = h
            if a in loose:
                witnesses[b].add(a)
            if b in loose:
                witnesses[a].add(b)
    multi = groups(loose, witnesses)
    owed = Counter(u for p in multi for u in p)
    if any(owed[u] > h for u, h in loose.items()):
        return 'stall', ()
    parents = list(multi) + [(u,) for u in sorted(loose) for _ in range(loose[u]-owed[u])]
    rosters = [set() for _ in rows]
    for i, ps in enumerate(parents):
        for u in ps:
            rosters[u].add(i)
    successor = groups(range(len(parents)), rosters)
    demand = Counter(i for p in successor for i in p)
    births = tuple((p, 0 if law == 'parity' and len(parents)==1 else max(1, 3-len(p), demand[i]))
                   for i, p in enumerate(parents))
    return 'births', births


def build(joins, private):
    rows = [[] for _ in private]
    mark = 0
    for a,b in joins:
        rows[a].append(mark)
        rows[b].append(mark)
        mark += 1
    for row, count in zip(rows, private):
        row.extend(range(mark, mark+count))
        mark += count
    return tuple(tuple(row) for row in rows)


def add(rows, holders):
    mark = width(rows)
    return tuple((*row,mark) if i in holders else row for i,row in enumerate(rows))
