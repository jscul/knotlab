"""Does anything in the scan depend on names?  Each start is run as given and under seeded renumberings of its knots and
distinctions; the name-free tallies (knots, parts and their sizes, first meetings, pairs alike or not, and the multiset
of four-run outcomes with every eligible first part tested) must be the same."""
import sys, json, random, collections
import scan2
from scan2 import eng, stars_of
def tally(law, stars):
    o = scan2.scan(law, 'x', stars, max_tests=10 ** 6)
    by = [(r['s'], r['parts'], r['part sizes'], r['first meetings (round, made only)'], r['X with two or more'], r['X met in different rounds'], r['pairs'], r['orbit shapes']) for r in o['by_s']]
    def canon(t):
        # which second part is listed first is a matter of names: put the one met earlier first, and name the classes
        # of the four courses in order of first appearance
        c = list(t['classes']); m = list(t['meets']); sz = [len(t['Y1']), len(t['Y2'])]
        alt = ([c[0], c[2], c[1], c[3]], [m[1], m[0]], [sz[1], sz[0]])
        def ren(cl):
            seen = {}
            return tuple(seen.setdefault(x, len(seen)) for x in cl)
        return min((tuple(m), ren(c), tuple(sz)), (tuple(alt[1]), ren(alt[0]), tuple(alt[2])))
    tests = sorted((t['why'], t['s'], canon(t), len(t['X']), str((t.get('m') or {}).get('m'))) for t in o['tests'])
    return json.dumps([o['rounds_read'], o['stop'], o['knots'], o['takes made'], by, tests])
spec = json.loads(sys.argv[1]); n = int(sys.argv[2])
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
stars = stars_of(spec['start'])
base = tally(law, stars)
ds = sorted({d for st in stars for d in st})
same = 0
for seed in range(n):
    rng = random.Random(1000 + seed)
    perm = ds[:]; rng.shuffle(perm); m = dict(zip(ds, perm))
    st2 = [[m[d] for d in st] for st in stars]
    for st in st2: rng.shuffle(st)
    rng.shuffle(st2)
    same += tally(law, st2) == base
b = json.loads(base)
print(json.dumps({'start': spec['start'], 'law': law.name(), 'renumberings': n, 'same': same, 'tests': len(b[5]),
                  'outcomes': sorted(collections.Counter((t[0], str(t[2])) for t in b[5]).items())}))
