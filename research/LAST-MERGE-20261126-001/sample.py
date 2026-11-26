"""sample.py LAW OUT: grow a fresh seeded sample of 2,000 six-knot census starts, disjoint from the 1,000 that
SETTLE-BOUND-20261126-001 sampled (random.Random(20261126).sample over the census list), chosen by
random.Random(20261127).sample over the rest; to round 24 under LAW, as SETTLE-BOUND's bound.py grows them."""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'SETTLE-BOUND-20261126-001'))
import bound
alike = bound.alike
law, out = sys.argv[1], sys.argv[2]
C = alike.census(6)
first = {c[0] for c in random.Random(20261126).sample(C, 1000)}
rest = [c for c in C if c[0] not in first]
fresh = random.Random(20261127).sample(rest, 2000)
with open(out, 'w') as f:
    for i, gi, loose, stars in fresh:
        g = alike.grow(stars, rounds=bound.ROUNDS, knot_law=law)
        g.update({'n knots': 6, 'index': i, 'graph': gi, 'loose': loose, 'stars': stars, 'knot law': law,
                  'kind': alike.kind([r['n'] for r in g['rows']], g['end']), 'M': bound.M_of(stars, law)})
        f.write(json.dumps(g) + '\n'); f.flush()
