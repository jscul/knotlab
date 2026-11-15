"""Choose the reading order once, then decide guard vectors and restore original positions."""
from dataclasses import dataclass
from functools import cache
from itertools import product
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = "TWO-RELAY-PADDING-20261115-001"
CURRENT = "SWAPPED-ROUTE-GROUPING-20261115-001"


@cache
def family(ticket, slug, filename):
    path = ROOT / "proofs" / ticket / (ticket + "-P001_" + slug) / filename
    return runpy.run_path(str(path))


@dataclass(frozen=True)
class Grouping:
    """An independently checkable order and a smallest tuple of conditioned, typed names."""
    swaps: tuple
    removed: tuple
    branches: tuple
    middles: tuple
    pads: tuple

    def witness(self, raw):
        if len(raw) != 24 + 12*len(self.branches) or any(bit not in (0, 1) for bit in raw):
            raise ValueError("expected the endpoint guards and all branch guard triples")
        ordered = list(raw[:24])
        for b in self.branches:
            ordered.extend(raw[24 + 12*b : 36 + 12*b])
        nested = family(PREVIOUS+"D", "nested_pair_grouping", "check.py")["solve"]
        for values in product((0, 1), repeat=len(self.removed)):
            answer = nested(self.middles, self.pads, ordered, dict(zip(self.removed, values)))
            if answer is not None:
                boundaries, occurrence_values = answer
                restored = [0] * len(occurrence_values)
                for i, b in enumerate(self.branches):
                    restored[3*b:3*b+3] = occurrence_values[3*i:3*i+3]
                return boundaries, restored
        return None


def prepare(middles, pads):
    zero = family(CURRENT+"A", "swap_equations", "solver.py")["zero_order"](middles, pads)
    if zero is None:
        optimize = family(CURRENT+"B", "minimum_exceptions", "solver.py")["optimal_order"]
        swaps, removed = optimize(middles, pads)
    else:
        swaps, removed = zero, ()
    branches = tuple(2*i + (side ^ swap) for i, swap in enumerate(swaps) for side in (0, 1))
    return Grouping(tuple(swaps), tuple(removed), branches, tuple(middles[b] for b in branches),
                    tuple(pads[2*b + side] for b in branches for side in (0, 1)))


def solve(middles, pads, raw):
    return prepare(middles, pads).witness(raw)


def independent_blocks(middles, pads):
    """Split at every boundary that no name spans. Reindex each block in its original order."""
    previous = family(PREVIOUS+"D", "nested_pair_grouping", "check.py")
    word = previous["named_word"](middles, pads)
    mate = previous["partner_positions"](word)
    tables = ([-1]*len(word), [-1]*len(word))

    def reindex(items, table):
        result = []
        count = 0
        for x in items:
            if table[x] < 0:
                table[x] = count
                count += 1
            result.append(table[x])
        return result, count

    first = farthest = 0
    for stage in range(len(middles)//2):
        for pos in range(6*stage, 6*stage+6):
            farthest = max(farthest, mate[pos]//6)
        if farthest <= stage:
            end = stage+1
            m, _ = reindex(middles[2*first:2*end], tables[0])
            p, count = reindex(pads[4*first:4*end], tables[1])
            yield first, end, m, p, count == len(p)
            first = end


def private_drop(middles, raw):
    """Find a 1-to-0 witness in a block with a different pad at every implication."""
    r = len(middles)//2
    # Boundaries have indices 0..r; middle names were densely indexed within this block.
    links = [[] for _ in range(r+2+max(middles))]
    edges = []
    for b, name in enumerate(middles):
        mid = r+1+name
        for side, (u,v) in enumerate(((b//2,mid),(mid,b//2+1))):
            start = 24+12*b+6*side
            mask = 2*int(all(raw[start:start+3])) + int(all(raw[start+3:start+6]))
            edges.append((u,v,mask))
            if mask == 3:
                links[u].append(v)
    reachable = bytearray(len(links))
    reachable[0] = 1
    todo = [0]
    while todo:
        for v in links[todo.pop()]:
            if not reachable[v]:
                reachable[v] = 1
                todo.append(v)
    if reachable[r]:
        return None
    values = []
    for b, name in enumerate(middles):
        values.append(reachable[r+1+name])
        for u,v,mask in edges[2*b:2*b+2]:
            # For a dropping implication, release it with the pad value whose half is off.
            values.append(int(bool(reachable[u] and not reachable[v] and (mask & 1))))
    return list(reachable[:r+1]), values


def solve_by_blocks(middles, pads, raw):
    """Switch readers at every unshared boundary, returning values in original physical order."""
    blocks = list(independent_blocks(middles, pads))
    r = len(middles)//2
    if len(raw) != 24*(r+1) or any(bit not in (0, 1) for bit in raw):
        raise ValueError("expected all raw guard bits")
    start, end = all(raw[:12]), all(raw[12:24])
    boundaries = [int(start)]*(r+1)
    occurrences = [0]*(6*r)
    if start:
        occurrences[::3] = [1]*(2*r)
    if not start or not end:
        return boundaries, occurrences
    for first, last, m, p, private in blocks:
        local_raw = [1]*24 + list(raw[24+24*first:24+24*last])
        answer = private_drop(m,local_raw) if private else solve(m,p,local_raw)
        if answer is not None:
            local_boundaries, local_values = answer
            boundaries[first:last+1] = local_boundaries
            boundaries[last+1:] = [0]*(r-last)
            occurrences[6*first:6*last] = local_values
            occurrences[6*last:] = [0]*(6*(r-last))
            return boundaries, occurrences
    return None
