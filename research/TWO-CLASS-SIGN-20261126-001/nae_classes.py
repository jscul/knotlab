"""nae_classes.py: the same map under not-all-equal (README.md). The allowed states are not a linear space there, so a
move is state-dependent: at a state x and a distinction d, the smallest sets t containing d with x + t allowed (every tie
kept, sizes up to MAX_MOVE). The classes are the components of the allowed states under these moves. Read: the number of
classes and their sizes; whether the global complement (always allowed under not-all-equal) joins or exchanges classes;
and whether some class-changing pair of states agrees on every loose distinction. Rings n = 3..7 with one or two loose
distinctions a knot, and a seeded sample of census starts, at the start and after one round of ordinary growth
(canonical engine), where the allowed states number at most MAX_STATES.

    nae_classes.py rings | sample N"""
import sys, json, itertools, random, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classes
forbid = classes.forbid
MAX_MOVE, MAX_STATES = 4, 20000


def allowed(supports):
    names = sorted({d for r in supports for d in r}); idx = {d: i for i, d in enumerate(names)}
    rows = [[idx[d] for d in r] for r in supports]; n = len(names)
    holders = collections.defaultdict(list)
    for k, r in enumerate(rows):
        for d in r: holders[d].append(k)
    out, x = [], [None] * n
    order = sorted(range(n), key=lambda d: -len(holders[d]))
    def ok(k):
        vals = [x[d] for d in rows[k]]
        if None in vals: return True
        return 0 in vals and 1 in vals
    def rec(i):
        if len(out) > MAX_STATES: return
        if i == n: out.append(sum(v << d for d, v in enumerate(x))); return
        d = order[i]
        for v in (0, 1):
            x[d] = v
            if all(ok(k) for k in holders[d]): rec(i + 1)
        x[d] = None
    rec(0)
    return names, rows, out


def components(names, rows, S):
    n = len(names); Sset = set(S)
    near = collections.defaultdict(set)
    for r in rows:
        for d in r: near[d].update(r)
    parent = {s: s for s in S}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for x in S:
        for d in range(n):
            pool = sorted((near[d] | {e for f in near[d] for e in near[f]}) - {d})
            for size in range(1, MAX_MOVE + 1):
                hits = []
                for rest in itertools.combinations(pool, size - 1):
                    t = (1 << d) | sum(1 << e for e in rest)
                    if x ^ t in Sset: hits.append(x ^ t)
                if hits:
                    for y in hits:
                        a, b = find(x), find(y)
                        if a != b: parent[a] = b
                    break
    comp = collections.Counter(find(s) for s in S)
    return {find(s) for s in S}, comp, find


def read_one(supports):
    names, rows, S = allowed(supports)
    if len(S) > MAX_STATES: return {'states': '>%d' % MAX_STATES, 'not run': True}
    if not S: return {'states': 0}
    roots, comp, find = components(names, rows, S)
    full = (1 << len(names)) - 1
    held = forbid.holders([tuple(names[i] for i in r) for r in rows])
    lmask = sum(1 << i for i, d in enumerate(names) if len(held[d]) == 1)
    by_loose = collections.defaultdict(set)
    for s in S: by_loose[s & lmask].add(find(s))
    return {'states': len(S), 'classes': len(roots), 'sizes': sorted(comp.values()),
            'complement keeps the class': all(find(s ^ full) == find(s) for s in S) if len(roots) > 1 else None,
            'two classes agree on every loose value': any(len(v) > 1 for v in by_loose.values())}


def read(name, supports):
    out = {'structure': name, 'start': read_one(supports)}
    st, status, births = forbid.grown(supports, 'nae', 'ordinary')
    out['after one round'] = read_one(st) if status == 'funded' else 'no round (stall or close)'
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'rings':
        for n in range(3, 8):
            for l in (1, 2):
                print(json.dumps(read('ring n=%d loose=%d' % (n, l), classes.ring(n, l))), flush=True)
    else:
        S = forbid.census(); rng = random.Random(20261126)
        for i in sorted(rng.sample(range(len(S)), int(sys.argv[2]))):
            print(json.dumps(read('census %d' % i, forbid.supports_of(S[i]))), flush=True)
