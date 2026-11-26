"""Ordinary parity growth, shortest changes and knot renamings on three rings.

Read only the canonical growth interface. Enumerate every least change through
each named distinction, all knot-moving involutions, and every distinction
bijection above each involution. All binary-vector operations are over F2.
"""

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from functools import reduce
from operator import xor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/FORBID-EDITS-20261126-001"))
from forbid import grown


def mask(indices):
    return sum(1 << i for i in indices)


def xor_basis(words):
    basis = {}
    for word in words:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = word
                break
            word ^= basis[pivot]
    return basis


def indices(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def read_parity(word, marks):
    return (word & marks).bit_count() % 2


def source(n):
    # i is shared by old knots i and i+1. The other two names are held once.
    return tuple(
        tuple(sorted(((i - 1) % n, i, n + 2 * i, n + 2 * i + 1)))
        for i in range(n)
    )


def holders(rows):
    by_mark = defaultdict(list)
    for knot, row in enumerate(rows):
        for mark in row:
            by_mark[mark].append(knot)
    assert set(by_mark) == set(range(len(by_mark)))
    assert all(1 <= len(group) <= 2 for group in by_mark.values())
    return [tuple(by_mark[i]) for i in range(len(by_mark))]


def shortest_changes(owners):
    """Stop once all marks have a minimum. Keep all ties in that last size."""
    columns = [mask(group) for group in owners]
    marks = set(range(len(owners)))
    missing = marks.copy()
    minimum = {}
    count = Counter()
    shortest = set()
    for width in range(1, len(owners) + 1):
        covered = set()
        for support in itertools.combinations(range(len(owners)), width):
            new_marks = missing.intersection(support)
            if new_marks and reduce(xor, (columns[i] for i in support), 0) == 0:
                shortest.add(mask(support))
                covered.update(new_marks)
                count.update(new_marks)
        for mark in covered:
            minimum[mark] = width
        missing -= covered
        if not missing:
            break
    assert not missing
    return shortest, [{"size": minimum[i], "ties": count[i]} for i in sorted(marks)]


def class_read(n, age, rows, owners, shortest):
    """Compute the dimensions and a literal witness for either read value."""
    equations = list(map(mask, rows))
    dimension = len(owners) - len(xor_basis(equations))
    hdim = len(xor_basis(shortest))
    old_shared = mask(i for i, group in enumerate(owners)
                      if len(group) == 2 and max(group) < n)
    bits = list(indices(old_shared))
    assert len(bits) == n
    if age == 0:
        assert dimension == hdim
        return dimension, hdim, old_shared, None
    assert dimension == hdim + 1
    assert all(read_parity(word, old_shared) == 0 for word in shortest)
    # An original shared distinction plus one paid mark at either holder and
    # a loose mark on each of the two child holders is an odd legal change.
    edge = bits[0]
    support = [edge]
    for old in owners[edge]:
        paid = next(i for i, group in enumerate(owners)
                    if len(group) == 2 and old in group and max(group) >= n)
        child = max(owners[paid])
        loose = next(i for i, group in enumerate(owners) if group == (child,))
        support.extend((paid, loose))
    assert len(set(support)) == 5
    witness = mask(support)
    assert read_parity(witness, old_shared) == 1
    assert all(read_parity(witness, row) == 0 for row in equations)
    assert len(xor_basis([*shortest, witness])) == dimension
    return dimension, hdim, old_shared, witness


def knot_involutions(n, rows, owners, buckets):
    """Enumerate all old permutations, extend by the unique child parent sets."""
    old_pairs = {group for group in owners if len(group) == 2 and max(group) < n}
    children = {}
    if len(rows) > n:
        loose_holders = {group[0] for group in owners if len(group) == 1}
        assert loose_holders == set(range(n, len(rows)))
        for child in range(n, len(rows)):
            parents = tuple(sorted(group[0] for group in owners
                                   if len(group) == 2 and group[1] == child))
            assert parents and parents not in children and max(parents) < n
            children[parents] = child
    identity = tuple(range(n))
    for old_map in itertools.permutations(range(n)):
        if old_map == identity or any(old_map[old_map[i]] != i for i in range(n)):
            continue
        if {tuple(sorted(old_map[i] for i in pair)) for pair in old_pairs} != old_pairs:
            continue
        mapping = [*old_map, *range(n, len(rows))]
        for parents, child in children.items():
            image = tuple(sorted(old_map[p] for p in parents))
            assert image in children
            mapping[child] = children[image]
        for group, marks in buckets.items():
            image = tuple(sorted(mapping[i] for i in group))
            assert len(buckets[image]) == len(marks)
        assert sorted(mapping) == list(range(len(rows)))
        assert all(mapping[j] == i for i, j in enumerate(mapping))
        yield tuple(mapping)


def mark_lifts(mapping, buckets, width):
    """Choose a bijection on each pair of holder groups or a local involution."""
    seen = set()
    choices = []
    for group, marks in buckets.items():
        if group in seen:
            continue
        image = tuple(sorted(mapping[k] for k in group))
        seen.update((group, image))
        options = []
        for target in itertools.permutations(buckets[image]):
            forward = dict(zip(marks, target, strict=True))
            if image == group:
                if any(forward[j] != i for i, j in forward.items()):
                    continue
            else:
                forward.update(dict(zip(target, marks, strict=True)))
            options.append(forward)
        choices.append(options)
    for parts in itertools.product(*choices):
        lift = [None] * width
        for part in parts:
            for mark, image in part.items():
                lift[mark] = image
        assert sorted(lift) == list(range(width))
        assert all(lift[j] == i for i, j in enumerate(lift))
        yield lift


def shortest_chain(mapping, owners, omit_fixed_marks):
    """Find a shortest chain from a knot to its mate. Include the named joins."""
    by_pair = {group: i for i, group in enumerate(owners) if len(group) == 2}
    assert len(by_pair) == sum(len(group) == 2 for group in owners)
    adj = defaultdict(list)
    for pair, mark in by_pair.items():
        a, b = pair
        image = by_pair[tuple(sorted((mapping[a], mapping[b])))]
        if omit_fixed_marks and image == mark:
            continue
        adj[a].append((b, mark, image))
        adj[b].append((a, mark, image))
    best = None
    for start, end in enumerate(mapping):
        seen = {start}
        todo = deque([(start, (start,), (), ())])
        while todo:
            at, knots, marks, images = todo.popleft()
            if at == end:
                candidate = (len(marks), knots, marks, images)
                if best is None or candidate < best:
                    best = candidate
                break
            for after, mark, image in sorted(adj[at]):
                if after not in seen:
                    seen.add(after)
                    todo.append((after, (*knots, after), (*marks, mark), (*images, image)))
    if best is None:
        return None
    _, knots, marks, images = best
    pairs = sorted({min(i, j) for i, j in enumerate(mapping)})
    pair_of = {i: pairs.index(min(i, j)) for i, j in enumerate(mapping)}
    assert pair_of[knots[0]] == pair_of[knots[-1]] and knots[0] != knots[-1]
    for choice in range(1 << len(pairs)):
        # Changing the side named first at any knot pair changes both adjacent
        # comparisons. Every choice gives exchange on the same closed chain.
        side = [(i > j) ^ ((choice >> pair_of[i]) & 1) for i, j in enumerate(mapping)]
        assert sum(side[a] ^ side[b] for a, b in zip(knots, knots[1:])) % 2 == 1
    return {"knots": knots, "shared_marks": marks, "image_marks": images,
            "knot_pairs": [min(k, mapping[k]) for k in knots],
            "first_side_choices_checked": 1 << len(pairs)}


def involution_record(n, age, rows, owners, shortest, old_shared, odd, knot_map, buckets):
    equations = list(map(mask, rows))
    fixed_counts = Counter()
    class_actions = Counter()
    for lift in mark_lifts(knot_map, buckets, len(owners)):
        assert {mask(lift[i] for i in indices(word)) for word in shortest} == shortest
        assert mask(lift[i] for i in indices(old_shared)) == old_shared
        representatives = (0,) if odd is None else (0, odd)
        images = tuple(read_parity(mask(lift[i] for i in indices(word)), old_shared)
                       for word in representatives)
        class_actions[images] += 1
        eqs = equations + [mask((i, j)) for i, j in enumerate(lift) if i < j]
        rank = len(xor_basis(eqs))
        allowed = 1 << (len(owners) - rank)
        if age:
            both = len(xor_basis([*eqs, old_shared])) > rank
            by_class = (allowed // 2, allowed // 2) if both else (allowed, 0)
        else:
            by_class = (allowed,)
        fixed_marks = sum(i == j for i, j in enumerate(lift))
        fixed_counts[fixed_marks, by_class] += 1
    fixed_knots = [i for i, j in enumerate(knot_map) if i == j]
    exchange = None
    if not fixed_knots:
        exchange = {"all_shared_marks": shortest_chain(knot_map, owners, False),
                    "moving_shared_marks_only": shortest_chain(knot_map, owners, True)}
        assert exchange["all_shared_marks"] is not None
    return {
        "old_knot_images": knot_map[:n], "knot_images": knot_map, "fixed_knots": fixed_knots,
        "physical_involutions": sum(class_actions.values()),
        "physical_involutions_exchanging_assignment_classes": sum(
            c for images, c in class_actions.items() if images != tuple(range(len(images)))),
        "free_on_marks": sum(c for (f, _), c in fixed_counts.items() if f == 0),
        "fixed_assignments": [
            {"fixed_marks": f, "assignments_by_class": counts, "physical_involutions": c}
            for (f, counts), c in sorted(fixed_counts.items())
        ],
        "exchange_chain": exchange,
    }


def check_stage(n, age):
    rows = source(n)
    if age:
        rows, status, _ = grown(rows, "parity", "ordinary")
        assert status == "funded"
    owners = holders(rows)
    buckets = defaultdict(list)
    for i, group in enumerate(owners):
        buckets[group].append(i)
    shortest, ties = shortest_changes(owners)
    dim, hdim, old_shared, odd = class_read(n, age, rows, owners, shortest)
    maps = [involution_record(n, age, rows, owners, shortest, old_shared, odd, p, buckets)
            for p in knot_involutions(n, rows, owners, buckets)]
    free = [m for m in maps if not m["fixed_knots"]]
    return {
        "source_knots": n, "round": age, "knots": len(rows), "distinctions": len(owners),
        "supports": rows, "old_shared": list(indices(old_shared)),
        "allowed_dimension": dim, "shortest_dimension": hdim, "class_count": 1 << (dim - hdim),
        "assignments_per_class": 1 << hdim,
        "distinct_shortest_changes_by_size": dict(sorted(Counter(w.bit_count() for w in shortest).items())),
        "minimum_through_each_mark": ties, "odd_change_witness": None if odd is None else list(indices(odd)),
        "knot_involutions": len(maps),
        "physical_involutions": sum(m["physical_involutions"] for m in maps),
        "physical_involutions_exchanging_assignment_classes": sum(
            m["physical_involutions_exchanging_assignment_classes"] for m in maps),
        "knot_involutions_free_on_knots": len(free),
        "physical_involutions_free_on_knots": sum(m["physical_involutions"] for m in free),
        "physical_involutions_free_on_knots_and_marks": sum(m["free_on_marks"] for m in free),
        "free_knot_maps_exchanging_sides_around_a_chain": sum(
            m["exchange_chain"]["all_shared_marks"] is not None for m in free),
        "free_knot_maps_exchanging_sides_using_only_moving_shared_marks": sum(
            m["exchange_chain"]["moving_shared_marks_only"] is not None for m in free),
        "involutions": maps,
    }


# Post-read comparison. These functions implement the two named lifts and the
# named kept, complement-flipped and moved-only-flipped sectors from their
# definitions. The blind reconstruction above does not use this section.
def named_lift(knot_map, buckets, count, maximal):
    lift = [None] * count
    for group, marks in buckets.items():
        image = tuple(sorted(knot_map[i] for i in group))
        targets = buckets[image].copy()
        if maximal and image == group:
            for j in range(0, len(targets) - 1, 2):
                targets[j], targets[j + 1] = targets[j + 1], targets[j]
        for mark, partner in zip(marks, targets, strict=True):
            lift[mark] = partner
    assert all(lift[j] == i for i, j in enumerate(lift))
    return lift


def moved_parts(knot_map, mark_map, owners):
    moved = {i for i, j in enumerate(knot_map) if i != j}
    adj = {k: set() for k in moved}
    for i, group in enumerate(owners):
        if len(group) == 2 and i != mark_map[i] and moved.issuperset(group):
            a, b = group
            adj[a].add(b)
            adj[b].add(a)
    left = moved.copy()
    parts = []
    while left:
        seed = min(left)
        todo = [seed]
        part = {seed}
        while todo:
            for knot in adj[todo.pop()] - part:
                part.add(knot)
                todo.append(knot)
        left -= part
        parts.append(sorted(part))
    exchanging = any(knot_map[part[0]] in part for part in parts)
    return parts, "one" if exchanging else "two" if len(parts) == 2 else "several"


def local_factor(terms, function):
    """A small table in the variables surviving the equal/opposite equations."""
    import numpy as np

    variables = tuple(sorted({i for i, _ in terms}))
    index = [(variables.index(i), offset) for i, offset in terms]
    values = [function([point[j] ^ offset for j, offset in index])
              for point in itertools.product((0, 1), repeat=len(variables))]
    return variables, np.array(values, dtype=np.int64).reshape((2,) * len(variables))


def sum_product(factors):
    """Eliminate one binary variable at a time, choosing the smallest product."""
    import numpy as np

    factors = list(factors)
    while True:
        neighborhoods = defaultdict(set)
        for variables, _ in factors:
            for i in variables:
                neighborhoods[i].update(variables)
        if not neighborhoods:
            return int(np.prod([v for _, v in factors], dtype=np.int64))
        drop = min(neighborhoods, key=lambda i: (len(neighborhoods[i]), i))
        group = tuple(sorted(neighborhoods[drop]))
        joint = np.ones((2,) * len(group), dtype=np.int64)
        keep = []
        for variables, table in factors:
            if drop in variables:
                joint *= table.reshape(tuple(2 if i in variables else 1 for i in group))
            else:
                keep.append((variables, table))
        remaining = tuple(i for i in group if i != drop)
        keep.append((remaining, joint.sum(axis=group.index(drop))))
        factors = keep


def sector_counts(n, rows, law, lift, mismatch):
    """Return counts by parity of the old shared marks on the named sector."""
    terms = []
    for mark, partner in enumerate(lift):
        if mismatch == "all" and mark == partner:
            return [0, 0]
        terms.append((min(mark, partner), int(mismatch != "none" and mark > partner)))
    allowed = (lambda values: sum(values) % 2 == 0) if law == "parity" else (
        lambda values: min(values) != max(values))
    factors = [local_factor([terms[i] for i in row], allowed) for row in rows]
    sign = local_factor(terms[:n], lambda values: 1 if sum(values) % 2 == 0 else -1)
    total = sum_product(factors)
    signed = sum_product([*factors, sign])
    assert 0 <= total <= 1 << len(lift) and abs(signed) <= total
    assert (total + signed) % 2 == 0
    return [(total + signed) // 2, (total - signed) // 2]


def postread_stage(n, age, law):
    rows = source(n)
    if age:
        rows, status, _ = grown(rows, law, "ordinary")
        assert status == "funded"
    owners = holders(rows)
    buckets = defaultdict(list)
    for i, group in enumerate(owners):
        buckets[group].append(i)
    # Reflections form one conjugacy class for odd n and two for even n.
    # An even ring also has the central renaming sending i to i+n/2.
    representatives = {tuple(-i % n for i in range(n))}
    if n % 2 == 0:
        representatives.update((tuple((1-i) % n for i in range(n)),
                                tuple((i + n // 2) % n for i in range(n))))
    allowed = sector_counts(n, rows, law, list(range(len(owners))), "none")
    named = []
    for knot_map in knot_involutions(n, rows, owners, buckets):
        if knot_map[:n] not in representatives:
            continue
        for maximal in (False, True):
            lift = named_lift(knot_map, buckets, len(owners), maximal)
            assert set(lift[:n]) == set(range(n))
            parts, kind = moved_parts(knot_map, lift, owners)
            fixed = sum(i == j for i, j in enumerate(lift))
            named.append({
                "old_knot_images": knot_map[:n], "lift": "max" if maximal else "min",
                "kind": kind, "moved_knot_components": parts, "fixed_distinctions": fixed,
                "kept_by_old_shared_parity": sector_counts(n, rows, law, lift, "none"),
                "globally_flipped_by_old_shared_parity": sector_counts(n, rows, law, lift, "all"),
                "flipped_on_moved_by_old_shared_parity": sector_counts(n, rows, law, lift, "moved"),
            })
    return {"source_knots": n, "round": age, "law": law, "knots": len(rows),
            "distinctions": len(owners), "allowed_by_old_shared_parity": allowed,
            "named_involutions": named}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ring", type=int, action="append", choices=(4, 5, 6))
    parser.add_argument("--round", type=int, action="append", choices=(0, 1))
    parser.add_argument("--with-named-sectors", action="store_true",
                        help="also compute the explicitly post-read sector comparisons")
    args = parser.parse_args()
    stages = [check_stage(n, age) for n in (args.ring or (4, 5, 6))
              for age in (args.round or (0, 1))]
    result = {
        "preparation": "Ring with two loose distinctions at each old knot, all loose values free.",
        "motion": "Every tied least-cardinality legal parity change through every physical mark.",
        "renamings": "All incidence-preserving involutions moving at least one knot; all distinction lifts.",
        "class_action": "A renaming fixes zero and permutes shortest changes. The grown classes are exactly the two values of the original shared parity, which every listed lift preserves.",
        "chain_read": "A closed chain of knot pairs can return at the other representative. The sequence of shared-mark orbits specifies the chain. The side named first at each pair is arbitrary.",
        "weighting_read": "On a grown ring, the normalized positive weighting and its product with the old shared parity sign give identical ordinary assignment and renaming records. Both are fixed by every shortest change and every listed renaming. Translation by the odd legal witness preserves the first and reverses the second under a supplied signed-change read.",
        "stages": stages,
    }
    if args.with_named_sectors:
        result["post_read_named_sectors"] = [
            postread_stage(n, age, law) for n in (args.ring or (4, 5, 6))
            for age in (args.round or (0, 1)) for law in ("parity", "nae")]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
