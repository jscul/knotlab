"""A point-set checker of the affine-hull rules and explicit witness trees."""

from functools import cache
from itertools import product


def parity(v):
    return v.bit_count() % 2


def masks(m):
    return range(1 << m)


def full_relations(m, a, b, charge=1):
    n = m + 1
    left, right = set(), set()
    for x in range(1 << n):
        products = sum((((x >> i) & 3) == 3) << i for i in range(m))
        value = parity(products)
        for free in (0, 1):
            left.add(x | (value << n) | (parity(products & a) << (n + 1)) | (free << (n + 2)))
            right.add(x | ((value ^ charge) << n) | (free << (n + 1)) | (parity(products & b) << (n + 2)))
    return frozenset(left), frozenset(right)


def affine_hull(points):
    if not points:
        return frozenset()
    origin = min(points)
    covered = {0}
    for point in points:
        offset = origin ^ point
        if offset not in covered:
            covered.update([v ^ offset for v in covered])
    return frozenset(v ^ origin for v in covered)


class Auditor:
    def __init__(self, m, a, b, charge=1):
        self.m, self.n = m, m + 1
        self.left, self.right = full_relations(m, a, b, charge)
        self.visible = frozenset(range(1 << (m + 4)))
        self.plane = cache(lambda q: frozenset(x for x in self.visible if parity(x & q)))
        self.close = cache(self._close)

    def _close(self, cell):
        while cell:
            reduced = affine_hull(cell & self.left) & affine_hull(cell & self.right)
            if cell == reduced:
                break
            cell = reduced
        return cell

    def verify_tree(self, tree, cell=None):
        if cell is None:
            cell = self.visible
        cell = self.close(cell)
        if tree is None:
            if cell:
                raise ValueError("leaf survives full affine saturation")
            return 1, 0
        q, low, high = tree
        if not 0 < q < 1 << (self.m + 4):
            raise ValueError("invalid XOR query")
        zero, one = cell - self.plane(q), cell & self.plane(q)
        if not zero or not one:
            raise ValueError("unnecessary or constant split in certificate")
        l, dl = self.verify_tree(low, zero)
        h, dh = self.verify_tree(high, one)
        return l + h, 1 + max(dl, dh)

    def optimum(self):
        @cache
        def opt(cell):
            if not cell:
                return 1, 0
            splits = set()
            for q in range(1, 1 << (self.m + 4)):
                plane = self.plane(q)
                yes = cell & plane
                if yes and yes != cell:
                    no = cell - yes
                    if min(cell) in yes:
                        yes, no = no, yes
                    splits.add((yes, no))
            best_leaves = best_depth = len(cell)
            for yes, no in splits:
                l, dl = opt(self.close(yes))
                h, dh = opt(self.close(no))
                best_leaves = min(best_leaves, l + h)
                best_depth = min(best_depth, 1 + max(dl, dh))
            return best_leaves, best_depth
        return opt(self.close(self.visible))

    def within(self, budget):
        # Directly enumerate every ambient linear form and every leaf allocation.
        # This separate point-set implementation makes no translation or mask reductions.
        @cache
        def solve(cell, limit):
            if not cell:
                return True
            if limit < 2:
                return False
            for q in range(1, 1 << (self.m + 4)):
                yes = cell & self.plane(q)
                if not yes or yes == cell:
                    continue
                no = self.close(cell - yes)
                yes = self.close(yes)
                if no and yes and limit < 4:
                    continue
                for i in range(1, limit):
                    j = limit - i
                    if ((solve(no, i) and solve(yes, j)) if i <= j else
                            (solve(yes, j) and solve(no, i))):
                        return True
            return False
        return solve(self.close(self.visible), budget)


def question(q, low, high):
    return [q, low, high]


def full_input_splits(variables):
    if not variables:
        return None
    child = full_input_splits(variables[1:])
    return question(1 << variables[0], child, child)


def strategy(m, cut=None):
    if cut is None:
        return full_input_splits(list(range(1, m + 1, 2)))
    # XOR(a,b)=1 forces a discrepancy in the prefix; its complementary case forces one in the suffix.
    compare = 3 << (m + 2)
    return question(compare, full_input_splits(list(range(cut + 1, m + 1, 2))),
                    full_input_splits(list(range(1, cut + 1, 2))))


def explicit(m, cut):
    mask = (1 << cut) - 1
    tree = strategy(m, cut)
    return mask, tree, Auditor(m, mask, mask).verify_tree(tree)


if __name__ == "__main__":
    for m in range(1, 8):
        cut = None if m <= 4 else {5: 2, 6: 2, 7: 4}[m]
        a = 0 if cut is None else (1 << cut) - 1
        print(m, a, Auditor(m, a, a).verify_tree(strategy(m, cut)))
