import itertools
from collections import defaultdict
import joinlib_path  # noqa
import joinlib as J
def in_scope(n, edges, surplus):
    """H's scope: (i) every knot has shared + round-1 demand >= 3 (no floor distinction); (ii) every listed surplus distinction is
    on a knot of demand >= 2; (iii) round 1 has only pairs; (iv) no two knots have two common neighbours."""
    sh, d = J.shared_and_demand(n, edges)
    if any(sh[k] + d[k] < 3 for k in range(n)): return False, 'floor'
    if any(d[int(k)] < 2 for k, v in surplus.items() if v): return False, 'surplus at demand < 2'
    sz = J.bare_sizes(n, edges, surplus)
    P = J.S.from_junctions(J.stars_from(sz, edges))
    if any(len(g) > 2 for g in P.groups_among(list(range(n)))): return False, 'group of three'
    nb = defaultdict(set)
    for a, b in edges: nb[a].add(b); nb[b].add(a)
    for a, b in itertools.combinations(range(n), 2):
        if len(nb[a] & nb[b]) >= 2: return False, 'two common neighbours'
    return True, ''
