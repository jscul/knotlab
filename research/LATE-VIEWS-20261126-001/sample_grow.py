"""sample_grow.py LAW OUT [COUNT]: a second weighting for the held-out test.  COUNT (default 1,000) starts of seven knots
drawn by the WEIGHTINGS-20261119-001B 'grow' weighting (knots added one at a time, 3 to 5 places each, each new knot
sharing one distinction with an existing knot chosen in proportion to its open places and, with probability 1/3, one
more with a second), random.Random(20261129); repeated draws are kept (the weighting counts them).  Grown to round 24
under LAW with the look-alike study's growth, unchanged."""
import sys, os, json, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'SETTLE-BOUND-20261126-001'))
import bound
alike = bound.alike


def stars_of(sizes, edges):
    stars = [[] for _ in sizes]; d = 0
    for a, b in edges: stars[a].append(d); stars[b].append(d); d += 1
    for k, s in enumerate(sizes):
        while len(stars[k]) < s: stars[k].append(d); d += 1
    return stars


def draws(count, n=7):
    path = ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py'
    spec = importlib.util.spec_from_file_location('wl', path); WL = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(WL)
    rng = random.Random(20261129)
    return [WL.sample('grow', n, rng) for _ in range(count)]


if __name__ == '__main__':
    law, out = sys.argv[1], sys.argv[2]
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    with open(out, 'w') as f:
        for i, (sizes, edges) in enumerate(draws(count)):
            stars = stars_of(sizes, edges)
            g = alike.grow(stars, rounds=bound.ROUNDS, knot_law=law)
            g.update({'n knots': 7, 'index': i, 'sizes': sizes, 'edges': edges, 'stars': stars, 'knot law': law,
                      'weighting': 'grow', 'kind': alike.kind([r['n'] for r in g['rows']], g['end'])})
            f.write(json.dumps(g) + '\n'); f.flush()
