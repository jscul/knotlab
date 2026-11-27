"""Seeded finite starts given by live knots and witnesses for their common neighbours."""
import argparse
import json
import random
import time
from collections import Counter
from itertools import combinations
from reading import compare, roster


def realize(n, families, opens):
    """Distinct live and dead knots; every common-neighbour witness is a dead knot."""
    stars = [[] for _ in range(n + len(families))]
    serial = 0

    def add(*owners):
        nonlocal serial
        for k in owners:
            stars[k].append(serial)
        serial += 1

    for j, f in enumerate(families):
        for k in f:
            add(k, n+j)
    for j in range(len(families)-1):
        add(n+j, n+j+1)
    if len(families) == 1:
        stars.append([])
        for _ in range(3):
            add(n, n+1)
    for k, count in enumerate(opens):
        for _ in range(count):
            add(k)
    for j, f in enumerate(families):
        while len(stars[n+j]) < 3:
            add(n+j, f[0])
    for k in range(n):
        while len(stars[k]) < 3:
            add(k, next(n+j for j, f in enumerate(families) if k in f))
    while len(stars) < 8:
        stars.append([])
        for _ in range(3):
            add(n, len(stars) - 1)
    return stars


def draw(index, seed):
    r = random.Random(seed + index)
    if index % 4 == 0:
        n = r.choice([5, 6, 7])
        families = [(i, r.randrange(i)) for i in range(1, n)]
    elif index % 4 == 1:
        n = r.choice([5, 6, 7])
        families = [tuple(range(3)), (2, 3)] + [(i, r.randrange(i)) for i in range(4, n)]
        families += [r.choice(families)]
    else:
        size = r.choice([3, 4, 5])
        shared = r.randint(2, size-1)
        outsiders = r.choice([1, 2, 3])
        n = size + outsiders
        families = [tuple(range(shared)) + tuple(range(size, n))]
        families += [p for p in combinations(range(size), 2) if not set(p) <= set(range(shared))]
        if index % 4 == 3:
            families += [(r.randrange(n), n)]
            n += 1
    demand = Counter(x for g in roster(families) for x in g)
    opens = [max(1, demand[k]) for k in range(n)]
    if index % 4 >= 2:
        k = r.choice([k for k in range(n) if demand[k] == 1] or list(range(n)))
        opens[k] += 1
    else:
        for k in r.sample(range(n), r.choice([0, 1, 2])):
            opens[k] += 1
    return realize(n, families, opens), families, opens


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--start', type=int, default=0)
    p.add_argument('--stop', type=int, default=32)
    p.add_argument('--depth', type=int, default=8)
    p.add_argument('--seed', type=int, default=468923)
    args = p.parse_args()
    for i in range(args.start, args.stop):
        t = time.perf_counter()
        stars, families, opens = draw(i, args.seed)
        result = {law: compare(stars, law, args.depth) for law in ('nae', 'parity')}
        print(json.dumps(dict(draw=i, knots=len(stars), families=families, opens=opens, result=result,
                              seconds=round(time.perf_counter()-t, 5))), flush=True)
