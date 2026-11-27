"""Independent weighting on ordinary starts. Realise a prescribed list of common neighbours."""
from itertools import combinations
import random

SEED = 7180319


def make_start(blocks, loose, rng):
    """One spent knot per block. Join spent knots so the presentation is connected."""
    n = len(loose)
    count = max(9 - n, 3, len(blocks))
    stars = [[] for _ in range(n + count)]
    label = 0

    def share(a, b):
        nonlocal label
        stars[a].append(label)
        stars[b].append(label)
        label += 1

    for i, block in enumerate(blocks):
        for k in block:
            share(k, n + i)
    for i in range(count):
        share(n + i, n + (i + 1) % count)
        if i >= len(blocks):
            share(n + i, n + (i + 1) % count)
    for k, amount in enumerate(loose):
        while len(stars[k]) + amount < 3:
            share(k, n + next(i for i, b in enumerate(blocks) if k in b))
        for _ in range(amount):
            stars[k].append(label)
            label += 1
    rng.shuffle(stars)
    return stars


def sample(index):
    rng = random.Random(SEED + 1103515245 * index)
    family = index % 4
    if family == 0:
        # One cycle of pair blocks, with up to two attachments.
        n = rng.randrange(4, 8)
        blocks = [{k, (k + 1) % n} for k in range(n)]
    elif family == 1:
        # Two overlapping groups, each with its own member.
        n = 4
        blocks = [{0, 1}, {0, 2}, {1, 2}, {0, 3}, {1, 3}]
    elif family == 2:
        # Two or three overlapping common-neighbour blocks.
        n = rng.randrange(4, 8)
        blocks = [set(range(n - 1)), set(range(1, n))]
        if rng.getrandbits(1):
            blocks.append(set(rng.sample(range(n), rng.randint(2, n - 1))))
    else:
        # A connected list of pair blocks; each additional pair is sampled independently.
        n = rng.randrange(4, 8)
        blocks = [{i, rng.randrange(i)} for i in range(1, n)]
        for a, b in combinations(range(n), 2):
            if {a, b} not in blocks and rng.random() < .33:
                blocks.append({a, b})

    for _ in range(rng.randrange(3)):
        anchor = rng.randrange(n)
        blocks.append({anchor, n})
        n += 1
    # Set demand by maximal complete sets with no common neighbour (Lemma R).
    pairs = set(pair for b in blocks for pair in combinations(sorted(b), 2))
    valid = []
    for k in range(n, 2, -1):
        for subset in combinations(range(n), k):
            s = set(subset)
            if (all(p in pairs for p in combinations(subset, 2))
                    and not any(s <= b for b in blocks)
                    and not any(s <= g for g in valid)):
                valid.append(s)
    groups = valid + [set(p) for p in pairs if not any(set(p) <= g for g in valid)]
    demand = [sum(v in g for g in groups) for v in range(n)]
    loose = [max(1, d) + rng.choices((0, 1, 2), weights=(6, 3, 1))[0] for d in demand]
    return make_start(blocks, loose, rng)
