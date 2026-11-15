"""Finite bases for conditional affine refutations with a quadratic promise."""
from collections import Counter
from functools import cache
from itertools import combinations
import json


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def parity(value):
    return value.bit_count() % 2


def xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def insert(pivots, value):
    while value:
        top = value.bit_length() - 1
        if not pivots[top]:
            pivots[top] = value
            return True
        value ^= pivots[top]
    return False


def linear_table(n, coefficients):
    return sum(1 << x for x in range(1 << n) if parity(x & coefficients))


class AffineSearch:
    def __init__(self, n):
        self.n = n
        self.universe = (1 << (1 << n)) - 1
        self.hyperplanes = [linear_table(n, c) for c in range(1, 1 << n)]
        self.hull = cache(self.affine_hull)

    def affine_hull(self, points):
        if not points:
            return 0
        start = (points & -points).bit_length() - 1
        basis = [0] * self.n
        for point in bits(points):
            insert(basis, point ^ start)
        generated = [start]
        for direction in basis:
            if direction:
                generated += [v ^ direction for v in generated]
        return sum(1 << v for v in generated)

    def fits(self, rich, plain, budget):
        @cache
        def attempt(space, left):
            if left <= 0:
                return False
            while space:
                smaller = self.hull(space & rich) & self.hull(space & plain)
                if smaller == space:
                    break
                space = smaller
            if not space:
                return True
            if left == 1:
                return False
            choices = set()
            for yes in self.hyperplanes:
                one = space & yes
                zero = space ^ one
                if not zero or not one:
                    continue
                # Flipping query orientation gives the identical unordered split.
                smaller, larger = sorted((one, zero))
                if smaller in choices:
                    continue
                choices.add(smaller)
                for k in range(1, left):
                    if attempt(smaller, k) and attempt(larger, left - k):
                        return True
            return False

        return attempt(self.universe, budget)


def form_table(n, terms, mask, linear):
    rows = [0] * n
    table = 0
    for p in bits(mask):
        i, j = terms[p]
        rows[i] |= 1 << j
        rows[j] |= 1 << i
        table ^= linear[1 << i] & linear[1 << j]
    pivots = [0] * n
    rank = sum(insert(pivots, row) for row in rows)
    return table, rank


def polar_classes(n, terms, total):
    # Each verified generator preserves the standard polar form with
    # pairs (0,1),(2,3),... . A subgroup already gives a complete partition.
    units = [1 << i for i in range(n)]
    even = [1 << i for i in range(0, n, 2)]
    generators = units + [a ^ b for a, b in combinations(even, 2)]
    transforms = []
    for g in generators:
        dual = xor(1 << (i ^ 1) for i in bits(g))
        columns = [u ^ (g if parity(dual & u) else 0) for u in units]
        assert all(xor(columns[j] for j in bits(c)) == u for u, c in zip(units, columns))
        images = []
        for a, b in terms:
            ac = [(c >> a) & 1 for c in columns]
            bc = [(c >> b) & 1 for c in columns]
            images.append(sum(((ac[i]*bc[j]) ^ (ac[j]*bc[i])) << p
                              for p, (i, j) in enumerate(terms)))
        assert xor(images[i] for i in bits(total)) == total
        cut = min(8, len(terms))
        lo = [xor(images[i] for i in bits(x)) for x in range(1 << cut)]
        hi = [xor(images[cut+i] for i in bits(x)) for x in range(1 << (len(terms)-cut))]
        transforms.append((lo, hi))
    seen = set()
    cut = min(8, len(terms))
    low_mask = (1 << cut) - 1
    for seed in range(1 << len(terms)):
        if seed in seen:
            continue
        todo = [seed]
        seen.add(seed)
        size = 0
        while todo:
            cur = todo.pop()
            size += 1
            for lo, hi in transforms:
                nxt = lo[cur & low_mask] ^ hi[cur >> cut]
                if nxt not in seen:
                    todo.append(nxt)
                    seen.add(nxt)
        yield seed, size
    assert len(seen) == 1 << len(terms)


def finite_bases():
    results = {}
    for t in (1, 2, 3):
        n = 2*t
        N = 1 << n
        full = (1 << N) - 1
        linear = [linear_table(n, c) for c in range(N)]
        terms = list(combinations(range(n), 2))
        total = sum(1 << p for p, (i,j) in enumerate(terms) if i%2 == 0 and j == i+1)
        qt, rank = form_table(n, terms, total, linear)
        assert rank == n
        # The pinned inequality is needed only from half-rank three onward.
        # At half-rank two it can fail, even when the free inequality holds.
        solvers = ({"free": AffineSearch(n + 1)} if t <= 2
                   else {"pinned": AffineSearch(n)})
        counts = {key: Counter() for key in solvers}
        tested = Counter()
        covered = 0
        for fmask, multiplicity in polar_classes(n, terms, total):
            _, rank = form_table(n, terms, total ^ fmask, linear)
            if rank != n:
                continue
            covered += multiplicity
            fbase, _ = form_table(n, terms, fmask, linear)
            for ell in linear:
                for f in (fbase ^ ell, fbase ^ ell ^ full):
                    domain = full ^ f
                    for q in (qt, qt ^ full):
                        for key, solver in solvers.items():
                            if key == "pinned":
                                exponent = t-1
                                rich, plain = domain & (full ^ q), q
                            else:
                                exponent = t
                                rich = (domain & (full ^ q)) | ((domain & q) << N)
                                plain = q | ((full ^ q) << N)
                            demand = ((domain.bit_count() << exponent) + N - 1) // N
                            if demand >= 2 and solver.fits(rich, plain, demand-1):
                                raise ValueError((t,key,fmask,hex(f),hex(q),demand))
                            counts[key][demand] += multiplicity
                            tested[key] += 1
        # Independent direct matrix count for the nonsingular second form.
        brute = sum(form_table(n,terms,total ^ m,linear)[1] == n
                    for m in range(1 << len(terms)))
        assert covered == brute
        for key in counts:
            assert sum(counts[key].values()) == 4*N*covered
        results[str(t)] = {"nonsingular_second_forms": covered,
                            "represented_cases_by_required_leaves": {k: dict(sorted(v.items())) for k,v in counts.items()},
                            "tested_representatives_with_signs": dict(tested)}
    return results


if __name__ == "__main__":
    print(json.dumps({"status":"passed","finite_bases":finite_bases()},sort_keys=True))
