"""Replay literal assumption-labelled conflicts on the nine original visible bits."""
import json
from itertools import product


def bit(row, index):
    return (row >> index) & 1


def data(row):
    x0, x1, x2, x3, x4, x5, total, first, second = (bit(row, i) for i in range(9))
    products = (x0*x1, x1*x2, x2*x3, x3*x4, x4*x5)
    q = sum(products) % 2
    return q, first == products[0] and second == (products[1] ^ products[2])


def inside(row, c, guard):
    if bit(row, 4) != c:
        return False
    x0, x1, x2, x3 = (bit(row, i) for i in range(4))
    z = bit(row, 6) ^ (c & (x3 ^ bit(row, 5)))
    if guard == 0:
        return x3 == z == 0
    if guard == 1:
        return x1 == 1 and z == x0
    return (x1 ^ x3) == 1 and z == x2


def branch(row):
    x1, x3, c, x5, s, u = (bit(row, i) for i in (1, 3, 4, 5, 6, 7))
    d = x1 ^ x3
    h = u ^ d
    z = s ^ (c & (x3 ^ x5))
    reply = d if h else z ^ x3
    return c, h, reply


def affine_span(points):
    if not points:
        return set()
    anchor = next(iter(points))
    offsets = {0}
    for pt in points:
        delta = anchor ^ pt
        if delta not in offsets:
            offsets |= {a ^ delta for a in offsets}
    return {a ^ anchor for a in offsets}


def replay():
    universe = set(range(512))
    left = {v for v in universe if data(v)[1] and bit(v, 6) == data(v)[0]}
    right = {v for v in universe if bit(v, 6) != data(v)[0]}
    if (len(left), len(right)) != (64, 256):
        raise ValueError("wrong source relations")
    library = {(c, t): {v for v in universe if inside(v, c, t)}
               for c, t in product(range(2), range(3))}
    # One restriction of the plain side to this guard, then a rich-side emptiness check.
    library_sizes = []
    for key, g in sorted(library.items()):
        survived = affine_span(g & right)
        if not survived or survived & left or not g & left:
            raise ValueError(f"uncertified terminal {key}")
        library_sizes.append([len(g), len(g & left), len(g & right), len(survived)])
    cases = {}
    leaf_sizes = []
    uses = {}
    for c, h, a in product(range(2), repeat=3):
        t = ((0, 1), (1, 2))[h][a]
        leaf = {v for v in universe if branch(v) == (c, h, a)}
        assert leaf == affine_span(leaf)
        if not leaf & left or not leaf & right:
            raise ValueError("a branch has no points from one source before deductions")
        if not (leaf & left) <= library[c, t]:
            raise ValueError("rich-side guard entailment failed")
        # The raw guard of the branch alone is insufficient in every case.
        if leaf <= library[c, t]:
            raise ValueError("expected a genuine local inference at the application")
        leaf_sizes.append(len(leaf & left))
        uses[c, t] = 1 + uses.get((c, t), 0)
        cases[c, h, a] = leaf
    assert set.union(*cases.values()) == universe
    assert all(not a & b for i,a in enumerate(cases.values()) for b in list(cases.values())[i+1:])
    assert set.union(*(g & left for g in library.values())) == left
    # The other 8-case tree directly fixes the three even inputs; each evaluator is queried once at each leaf.
    for y in product(range(2), repeat=3):
        cell = {v for v in universe if tuple(bit(v,i) for i in (0,2,4)) == y}
        if (affine_span(cell & left) & right) or not cell & right:
            raise ValueError("direct tree does not close in two local steps")
    wrong = sorted((left & cases[0,0,0]) - library[0,1])
    if not wrong or wrong[0] != 0:
        raise ValueError("wrong reference should fail on the all-zero input")
    return dict(visible_rows=len(universe), rich_rows=len(left), plain_rows=len(right),
                original_cases=len(cases), distinct_terminal_proofs=len(library),
                terminal_calls=dict((str(key), n) for key,n in sorted(uses.items())),
                rich_points_per_leaf_in_order=leaf_sizes,
                guard_sizes_raw_rich_plain_and_plain_hull=library_sizes,
                wrong_guard_witness=wrong[0])


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True))
