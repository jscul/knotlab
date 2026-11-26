"""Rebuild one ordinary round, tied shortest moves, and class read/change minima."""
import argparse
import json
from collections import Counter
from itertools import combinations
from functools import reduce
from operator import or_, xor
from pathlib import Path


def places(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def mask(ids):
    return sum(1 << i for i in ids)


def union(rows):
    return reduce(or_, rows, 0)


def ring(n):
    return [mask(((i-1) % n, i, n+2*i, n+2*i+1)) for i in range(n)]


def multiplicities(rows):
    return Counter(i for row in rows for i in places(row))


def loose(rows):
    return mask(i for i, uses in multiplicities(rows).items() if uses == 1)


def groups(rows, live):
    """Exhaust the live subsets. A covered pair is spent only in its larger join."""
    neighbours = [{j for j, other in enumerate(rows) if i != j and row & other}
                  for i, row in enumerate(rows)]
    pairs = {pair for pair in combinations(live, 2)
             if neighbours[pair[0]] & neighbours[pair[1]]}
    largest = []
    for size in range(len(live), 2, -1):
        for subset in combinations(live, size):
            if (all(pair in pairs for pair in combinations(subset, 2))
                and not set.intersection(*(neighbours[i] for i in subset))
                and not any(set(subset) <= set(group) for group in largest)):
                largest.append(subset)
    covered = {pair for group in largest for pair in combinations(group, 2)}
    return sorted(largest) + sorted(pairs - covered)


def grow(old):
    available = loose(old)
    supply = [list(places(row & available)) for row in old]
    live = [i for i, stock in enumerate(supply) if stock]
    births = []
    for group in groups(old, live):
        births.append(mask(supply[i].pop(0) for i in group))
    births.extend(1 << i for stock in supply for i in stock)
    provisional = old + births
    children = range(len(old), len(provisional))
    demand = Counter(i for group in groups(provisional, children) for i in group)
    result = old.copy()
    next_id = union(old).bit_length()
    for i, row in zip(children, births):
        floor = 0 if row == available else max(1, 3-row.bit_count())
        count = max(demand[i], floor)
        result.append(row | mask(range(next_id, next_id+count)))
        next_id += count
    return result


def residual(word, basis):
    for top in sorted(basis, reverse=True):
        if word & (1 << top):
            word ^= basis[top]
    return word


def independent(words):
    basis = {}
    for word in words:
        rest = residual(word, basis)
        if rest:
            basis[rest.bit_length()-1] = rest
    return basis


def parity(mask_a, mask_b):
    return (mask_a & mask_b).bit_count() % 2


def syndrome(word, equations):
    return sum(parity(word, row) << i for i, row in enumerate(equations))


def kernel(equations, width):
    """Eliminate column syndromes, keeping each dependence as a legal change."""
    pivots = {}
    changes = []
    for i in range(width):
        word = 1 << i
        value = syndrome(word, equations)
        while value:
            top = value.bit_length()-1
            if top not in pivots:
                pivots[top] = value, word
                break
            previous, origin = pivots[top]
            value ^= previous
            word ^= origin
        else:
            changes.append(word)
    return changes


def move_list(equations, allowed_basis):
    """A size layer must finish before its covered distinctions may be removed."""
    active = union(allowed_basis)
    remaining = active
    moves = []
    bits = [1 << i for i in places(active)]
    columns = {bit: syndrome(bit, equations) for bit in bits}
    for size in range(1, len(bits)+1):
        additions = []
        for subset in combinations(bits, size):
            if reduce(xor, (columns[bit] for bit in subset)) == 0:
                word = sum(subset)
                if word & remaining:
                    additions.append(word)
        moves.extend(additions)
        remaining &= ~union(additions)
        if not remaining:
            break
    return sorted(moves)


def shortest_with_syndrome(equations, wanted, width):
    """Join two lists of words of weight at most r, up to the first hit."""
    columns = [syndrome(1 << i, equations) for i in range(width)]
    best = {0: 0}
    for radius in range(1, width+1):
        for subset in combinations(range(width), radius):
            key = reduce(xor, (columns[i] for i in subset))
            if key not in best:
                best[key] = mask(subset)
        candidates = (word ^ best[key ^ wanted] for key, word in best.items()
                      if key ^ wanted in best)
        answer = min(candidates, default=None, key=int.bit_count)
        if answer is not None:
            # Every lighter candidate also splits into two words of weight <= radius.
            return answer
    raise ValueError("unreachable syndrome")


def outside(candidates, basis):
    return next((word for word in candidates if residual(word, basis)), None)


def preparation(stage, pinned):
    width = union(stage).bit_length()
    equations = stage + ([1 << i for i in places(loose(stage))] if pinned else [])
    allowed = kernel(equations, width)
    moves = move_list(equations, allowed)
    return width, equations, allowed, moves


def read_case(n, stage, pinned):
    width, eq, allowed, moves = preparation(stage, pinned)
    move_basis = independent(moves)
    extra = outside(allowed, move_basis)
    assert len(allowed)-len(move_basis) == int(extra is not None)
    counts = multiplicities(moves)
    info = dict(width=width, grown_places=[list(places(r)) for r in stage],
                rank_allowed=len(allowed), rank_moves=len(move_basis),
                classes=2**(len(allowed)-len(move_basis)),
                moves=[list(places(r)) for r in moves],
                move_sizes=dict(Counter(r.bit_count() for r in moves)),
                holder_counts=dict(Counter(counts.values())),
                old_ring_in_moves=not residual((1 << n)-1, move_basis),
                distances=None)
    if extra is not None:
        rows = list(move_basis.values())
        label = shortest_with_syndrome(rows+[extra], 1 << len(rows), width)
        change = shortest_with_syndrome(eq+[label], 1 << len(eq), width)
        assert syndrome(label, moves) == 0 and syndrome(change, eq) == 0
        assert parity(label, change)
        info.update(distances=[label.bit_count(), change.bit_count()],
                    least_label=list(places(label)), least_change=list(places(change)))
    return info


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sizes", nargs="+", type=int, choices=range(5, 9))
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    results = {}
    for n in args.sizes:
        stage = grow(ring(n))
        results[n] = {name: read_case(n, stage, pinned)
                      for name, pinned in (("free", False), ("pinned", True))}
        for name, case in results[n].items():
            print(n, name, case["rank_allowed"], case["rank_moves"], case["move_sizes"],
                  case["holder_counts"], case["distances"])
    if args.output:
        args.output.write_text(json.dumps(results, indent=1)+"\n")


if __name__ == "__main__":
    main()
