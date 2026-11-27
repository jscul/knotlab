"""A second weighting, favoring two groups with two common live knots."""
import json
import random
import sys
from collections import Counter
from draw import realize
from reading import compare, roster


def case(i):
    r = random.Random(903147 + i)
    n = 5
    families = [(0, 1, 4), (0, 2), (1, 2), (0, 3), (1, 3)]
    for _ in range(r.randrange(4)):
        families.append((r.randrange(n), n))
        n += 1
    demand = Counter(k for g in roster(families) for k in g)
    opens = [demand[k] + r.choice([0, 0, 1, 1, 2]) for k in range(n)]
    if i % 2 == 0:
        k = r.choice([k for k in range(n) if demand[k] == 1])
        opens[k] = 2
    return realize(n, families, opens), families, opens


if __name__ == '__main__':
    for i in range(int(sys.argv[1])):
        stars, families, opens = case(i)
        res = {law: compare(stars, law, 8) for law in ('nae', 'parity')}
        print(json.dumps(dict(draw=i, knots=len(stars), families=families, opens=opens, result=res)), flush=True)
