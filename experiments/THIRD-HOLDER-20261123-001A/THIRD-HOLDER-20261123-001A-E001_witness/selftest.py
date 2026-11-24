"""Engine self-test (part of row G's code checks): the bit-operation enumeration, the backtracking search and a plain
itertools enumeration agree on 200 seeded random structures of parity and not-all-equal knots of three and four places."""
import itertools, random, json
import numpy as np
import common as c

rng = random.Random(20261123)
bad = 0
for t in range(200):
    n = rng.randint(3, 13); names = [f'v{i}' for i in range(n)]
    knots = []
    for _ in range(rng.randint(1, 6)):
        ar = rng.choice((3, 3, 4)) if n >= 4 else 3
        knots.append((rng.choice(('even', 'odd', 'nae')), tuple(rng.sample(names, ar))))
    outer = rng.sample(names, rng.randint(0, min(4, n)))
    a = c.enumerate_counts(names, knots, outer, max_lo=rng.randint(0, 5))
    b, _ = c.backtrack_counts(names, knots, outer)
    d = np.zeros(1 << len(outer), dtype=np.int64)
    for w in itertools.product((0, 1), repeat=n):
        val = dict(zip(names, w))
        if all(c.LAW_FN[l]([val[m] for m in mem]) for l, mem in knots):
            key = 0
            for v in outer: key = key * 2 + val[v]
            d[key] += 1
    if not (np.array_equal(a, b) and np.array_equal(a, d)): bad += 1
print('engine self-test: mismatches', bad, 'of 200 random structures:', 'PASS' if bad == 0 else 'FAIL')
json.dump(dict(structures=200, mismatches=bad), open(f'{c.ART}/selftest.json', 'w'))
