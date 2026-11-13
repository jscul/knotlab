"""Check constructive steps of the across-span proof against the base 16 NAE law."""
from collections import deque
from functools import lru_cache
from itertools import pairwise
import json
import random


def nae_transition(before, after, x):
    """Check both original NAE triples wherever they are wholly in these words."""
    raw = tuple(bit ^ (x % 2) for bit in before)
    next_raw = tuple(bit ^ ((x + 1) % 2) for bit in after)
    for r, bit in enumerate(raw):
        for neighbour in (r + 1, r - 2):
            if 0 <= neighbour < len(raw) and bit == raw[neighbour] == next_raw[r]:
                return False
    return True


def strip_transition(before, after):
    return all(
        bit == after[r] or all(
            before[s] != bit for s in (r + 1, r - 2) if 0 <= s < len(before)
        )
        for r, bit in enumerate(before)
    )


def words(width):
    return [tuple((i >> r) & 1 for r in range(width)) for i in range(1 << width)]


def fold(r, width):
    if r < 0:
        return r % 3
    if r >= width:
        return width - 3 + (r - width + 3) % 3
    return r


@lru_cache(None)
def successors(width):
    roster = words(width)
    return {p: [q for q in roster if strip_transition(p, q)] for p in roster}


def shortest_paths(start):
    paths = {start: [start]}
    queue = deque([start])
    while queue:
        p = queue.popleft()
        for q in successors(len(p))[p]:
            if q not in paths:
                paths[q] = [*paths[p], q]
                queue.append(q)
    return paths


def local_trajectory(path, background):
    """Return only the enlarged interval. The caller keeps the outside fixed."""
    width = len(path[0])
    moves = sum(p != q for p, q in pairwise(path))
    margin = 2 * moves
    rows = range(-margin, width + margin)
    local = [tuple(path[0][fold(r, width)] for r in rows)]
    for p, q in pairwise(path):
        moves -= p != q
        local.append(tuple(
            q[fold(r, width)] if -2 * moves <= r < width + 2 * moves else v
            for r, v in zip(rows, local[-1])
        ))
    padded = [background[:2] + word + background[2:] for word in local]
    for x, (a, b) in enumerate(pairwise(padded)):
        assert nae_transition(a, b, x)
    for x, word in enumerate(local):
        assert word[margin:margin + width] == path[x]
    return local


def main():
    valid = invalid = 0
    for width in range(3, 7):
        roster = words(width)
        for r in range(-23, width + 23):
            for step in (1, -2):
                assert fold(r + step, width) - fold(r, width) in (1, -2)
        for p in roster:
            for q in roster:
                legal = strip_transition(p, q)
                assert nae_transition(p, q, 0) == legal == nae_transition(p, q, 1)
                if legal:
                    extended = [tuple(w[fold(r,width)] for r in range(-5,width+6)) for w in (p,q)]
                    assert nae_transition(*extended,0)
                    valid += 1
                else:
                    invalid += 1
    path_count = 0
    for width in (3, 4):
        for start in words(width):
            for path in shortest_paths(start).values():
                assert len(path) <= 1 << width
                local_trajectory([path[0], *path, path[-1]], (1, 0, 1, 0))
                path_count += 1
    rng = random.Random(16)
    simultaneous = 0
    for _ in range(150):
        patches = []
        for width in (3, 5):
            path = [rng.choice(words(width))]
            for step in range(6):
                path.append(rng.choice(successors(width)[path[-1]]))
            patches.append(local_trajectory(path, (1, 0, 0, 1)))
        states = [(1, 1) + p + q + (0, 1) for p,q in zip(*patches)]
        for x,(p,q) in enumerate(pairwise(states)):
            assert nae_transition(p,q,x)
        simultaneous += 1
    # Cropping without a collar can turn a permitted change into a violation.
    assert strip_transition((0,1,0),(1,1,0))
    assert not strip_transition((0,0,0,1,0),(0,0,1,1,0))
    assert valid and invalid
    print(json.dumps(dict(valid_folded_steps=valid,rejected_steps=invalid,
                          reachable_pairs_localized=path_count,adjacent_patches=simultaneous,
                          failed_zero_margin_control=True),indent=2))


if __name__ == "__main__":
    main()
