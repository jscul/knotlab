"""Candidate complex of a bare start: knots, Gamma edges = round-1 groups (pairs), filled triangles = sunflower triples
(three knots pairwise candidates through one common neighbour).  Prints them."""
import sys, json, itertools
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins')
import joinlib as J
S = J.S
def complex_of(n, edges, surplus=None):
    sz = J.bare_sizes(n, edges, surplus)
    P = S.from_junctions(J.stars_from(sz, edges))
    gs = P.groups_among(list(range(n)))
    E = [tuple(sorted(g)) for g in gs if len(g) == 2]
    big = [tuple(sorted(g)) for g in gs if len(g) > 2]
    nb = P.nbr
    tri = []
    for a, b, c in itertools.combinations(range(n), 3):
        if all(tuple(sorted(p)) in set(E) for p in [(a, b), (b, c), (a, c)]):
            common = nb[a] & nb[b] & nb[c]
            tri.append(((a, b, c), sorted(common)))
    return sz, E, big, tri
if __name__ == '__main__':
    R = J.ring_edges(5)
    for name, n, e in [('ring', 5, R), ('ring+lone', 6, R + [(0, 5)]), ('5-5', 10, R + J.ring_edges(5, 5) + [(0, 5)])]:
        print(name, complex_of(n, e))
