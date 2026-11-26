"""explore.py WEIGHTING N COUNT T SEED OUT.json: exploration before the freeze (not a test).  For COUNT starts of N knots
drawn by a WEIGHTINGS-20261119-001B weighting (random.Random(SEED)), and one reader each (a live start knot, the same
generator), the least radius r_t (holder steps from the reader in the start's roster) such that the growth run on the
ball of radius r gives the reader's view exactly through round t, for t = 1..T, under not-all-equal."""
import sys, os, json, random, time, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ondemand as O
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
_s = importlib.util.spec_from_file_location('wl', ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
WL = importlib.util.module_from_spec(_s); _s.loader.exec_module(WL)
sys.path.insert(0, os.path.join(HERE, '..', 'LATE-VIEWS-20261126-001'))
from sample_grow import stars_of


def least_radii(opn, places, B, reader, T, law='nae'):
    full = O.grow(opn, places, B, T, law)
    Vf = O.view(full, reader)
    D = O.dist_from(reader, set(opn), B); R = max(D.values())
    first = {}
    for r in range(0, R + 1):
        g = O.grow(opn, places, B, T, law, region={v for v in D if D[v] <= r})
        V = O.view(g, reader)
        ok = 0
        while ok < len(Vf) and ok < len(V) and V[ok] == Vf[ok]: ok += 1
        if len(V) == len(Vf) and ok == len(Vf) and g['end'] == full['end']: ok = T
        for t in range(1, ok + 1): first.setdefault(t, r)
        if ok >= T: break
    return first, R, full['end'], len(Vf)


if __name__ == '__main__':
    kind, N, count, T, seed, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    rng = random.Random(seed); res = []
    for i in range(count):
        sizes, edges = WL.sample(kind, N, rng); stars = stars_of(sizes, edges)
        opn, places, B = O.roster(stars)
        if not opn: continue
        reader = rng.choice(sorted(opn)); t0 = time.time()
        first, R, end, nr = least_radii(opn, places, B, reader, T)
        res.append({'i': i, 'reader': reader, 'eccentricity': R, 'end': end, 'rounds': nr,
                    'least radius by round': first, 'seconds': round(time.time() - t0, 2)})
        print(json.dumps(res[-1]), flush=True)
    json.dump(res, open(out, 'w'), indent=1)
