"""handbuilt.py OUT.jsonl: starts built by hand outside the census, each with a group cell of four to six knots or with
group cells that meet (the advisor's request before the freeze: every cell in the census is small).  A start is given
by its knots' places and the pairs of knots sharing a distinction; each distinction lies in at most two knots."""
import sys, json, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from sample_grow import stars_of


def clique(n): return list(itertools.combinations(range(n), 2))


def build():
    S = []
    def add(name, sizes, edges): S.append({'name': name, 'sizes': sizes, 'edges': edges, 'stars': stars_of(sizes, edges)})
    for g in (4, 5, 6):
        for loose in (1, 2, 3):
            add('all %d knots touching pairwise, %d loose each' % (g, loose), [g - 1 + loose] * g, clique(g))
    add('five touching pairwise, loose 1, 1, 2, 2, 3', [5, 5, 6, 6, 7], clique(5))
    add('six touching pairwise, loose 1 except two with 2', [6, 6, 6, 6, 7, 7], clique(6))
    tri = [(0, 1), (0, 2), (1, 2)]
    add('two triples sharing a knot, loose 1', [3, 3, 5, 3, 3], tri + [(2, 3), (2, 4), (3, 4)])
    add('two triples sharing a knot, loose 2', [4, 4, 6, 4, 4], tri + [(2, 3), (2, 4), (3, 4)])
    add('two triples joined through a knot', [5, 5, 8, 6, 8, 5, 5],
        tri + [(2, 3), (3, 4), (4, 5), (4, 6), (5, 6)])
    add('four touching pairwise with a knot hanging from each', [8, 8, 8, 8, 4, 4, 4, 4],
        clique(4) + [(0, 4), (1, 5), (2, 6), (3, 7)])
    add('five touching pairwise with one hanging knot', [7, 7, 7, 7, 9, 6], clique(5) + [(4, 5)])
    add('three triples around one knot, loose 1', [3, 3, 3, 3, 3, 3, 7],
        [(0, 1), (0, 6), (1, 6), (2, 3), (2, 6), (3, 6), (4, 5), (4, 6), (5, 6)])
    return S


if __name__ == '__main__':
    with open(sys.argv[1], 'w') as f:
        for i, x in enumerate(build()):
            x['index'] = i; f.write(json.dumps(x) + '\n')
    print(len(build()))
