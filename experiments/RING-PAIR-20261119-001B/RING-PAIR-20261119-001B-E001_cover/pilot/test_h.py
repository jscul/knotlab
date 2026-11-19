import sys, time
from animals import orbit_counts
from gamma import complex_of
import joinlib as J
R = J.ring_edges(5)
N = int(sys.argv[1])
for name, n, e, grown in [('ring', 5, R, None), ('ring+lone', 6, R + [(0, 5)], [6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 21, 24, 28, 32]),
                          ('5-5', 10, R + J.ring_edges(5, 5) + [(0, 5)], [10, 14, 24, 42, 78, 154, 310, 638, 1346, 2888, 6278, 13822, 30776])]:
    sz, E, big, tri = complex_of(n, e)
    t = time.time()
    oc = orbit_counts(n, E, tri, N)
    print(name, [str(x) for x in oc], 'grown', grown[:N] if grown else None, round(time.time() - t, 1))
