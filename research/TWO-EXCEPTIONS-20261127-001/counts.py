"""counts.py: structure only. Under a named weighting of WEIGHTINGS-20261119-001B at a given size, how often an accepted
start (late-views class) whose node core finishes lies in the proved class N1-N3 (CHAIN-COUNT-20261127-001), and how
often it fails N1 (chained twins) or N2 (lifts that do not meet); also cores over the cap and cores that do not finish.
Counted by draw with repeats (the weighting's own count) and by distinct start up to renaming.

    counts.py KIND KNOTS DRAWS SEED"""
import sys, os, json, random, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'CHAIN-COUNT-20261127-001'))
sys.path.insert(0, os.path.join(HERE, '..', 'GRADED-ORDER-20261126-001'))
import ext, graded
twins, late = ext.twins, ext.late
kind, n, draws, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
spec = importlib.util.spec_from_file_location('wl', graded.ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
WL = importlib.util.module_from_spec(spec); spec.loader.exec_module(WL)
rng = random.Random(seed); per_draw = collections.Counter(); distinct = collections.Counter(); seen = {}
for i in range(draws):
    sizes, edges = graded.sample_start(WL, kind, n, rng)
    stars = graded.stars_of(sizes, edges)
    M = late.Map(stars)
    if M.cls != 'in': per_draw['not accepted'] += 1; continue
    key = graded.canon(sizes, edges)
    if key not in seen:
        try:
            r = ext.check_start(stars, 2)
            if r is None: out = 'core does not finish by rank 25'
            else:
                T = twins.twins(stars, cycles=True)
                n1, n2, n3 = not T, not r['star fails'], not r['n3 fails']
                chains = any(M.chains.values())
                out = ('in the class' if n1 and n2 and n3 else
                       'fails N1 (chained twins)' if not n1 else
                       'fails N2 only (lifts do not meet)' if not n2 else 'fails N3 only')
                if out == 'in the class': out += ', with chains' if chains else ', no chains'
        except RuntimeError: out = 'core over the cap'
        seen[key] = out; distinct[out] += 1
    per_draw[seen[key]] += 1
print(json.dumps({'weighting': kind, 'knots': n, 'draws': draws, 'seed': seed,
                  'accepted draws with repeats': dict(per_draw), 'distinct accepted starts': dict(distinct)}))
