"""sample.py LAW OUT [FIRST LAST]: grow a fresh seeded sample of 2,000 six-knot census starts for the held-out test,
disjoint from the 1,000 of SETTLE-BOUND-20261126-001 (random.Random(20261126).sample over the census list) and the 2,000
of LAST-MERGE-20261126-001 (random.Random(20261127).sample over the rest), chosen by random.Random(20261128).sample over
what remains; to round 24 under LAW, as SETTLE-BOUND's bound.py grows them (the look-alike study's growth, unchanged).
FIRST LAST: only the sampled starts at those positions (for timing)."""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'SETTLE-BOUND-20261126-001'))
import bound
alike = bound.alike


def fresh():
    C = alike.census(6)
    first = random.Random(20261126).sample(C, 1000)
    rest = [c for c in C if c[0] not in {x[0] for x in first}]
    second = random.Random(20261127).sample(rest, 2000)
    rest = [c for c in rest if c[0] not in {x[0] for x in second}]
    return random.Random(20261128).sample(rest, 2000)


if __name__ == '__main__':
    law, out = sys.argv[1], sys.argv[2]
    S = fresh()
    if len(sys.argv) > 4: S = S[int(sys.argv[3]):int(sys.argv[4])]
    with open(out, 'w') as f:
        for i, gi, loose, stars in S:
            g = alike.grow(stars, rounds=bound.ROUNDS, knot_law=law)
            g.update({'n knots': 6, 'index': i, 'graph': gi, 'loose': loose, 'stars': stars, 'knot law': law,
                      'kind': alike.kind([r['n'] for r in g['rows']], g['end'])})
            f.write(json.dumps(g) + '\n'); f.flush()
