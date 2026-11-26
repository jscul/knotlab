"""recur.py: does growing a start and then exchanging it give the start back?  RECURSION-LEAD-20261126-001 (a check by
the thread, not registered); README.md.  Exploration before any freeze.

The exchange is SECOND-CHECK-20261126-001's (commute.exchanged): under parity, with the stage's loose values pinned or
free, each shortest allowed change through a distinction (every tie) is read as a knot holding the distinctions it
changes.  For a start S: G(S) is one round of ordinary growth under parity (forbid.grown), E the exchange.  Read whether
E(G(S)) is lawful (every exchanged knot with three or more places, every distinction held by at most two), whether it is
S up to renaming (labelled multigraphs, knots with their loose counts; commute.same), and, when it is a lawful start but
not S, what E(G(.)) does to it in turn, up to STEPS times: a return to S, a fixed other start, a cycle, or a stop.

    recur.py explore OUT.jsonl"""
import sys, os, json, random, importlib.util, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'SECOND-CHECK-20261126-001'))
_argv = sys.argv; sys.argv = sys.argv[:1]
_spec = importlib.util.spec_from_file_location('commute_mod', ROOT / 'research/SECOND-CHECK-20261126-001/commute.py')
src = open(ROOT / 'research/SECOND-CHECK-20261126-001/commute.py').read()
src = src[:src.index('\nfor n in range(5, 11):')]          # the module's functions, without its own loop
CM = type(sys)('commute_mod'); CM.__file__ = str(ROOT / 'research/SECOND-CHECK-20261126-001/commute.py')
exec(compile(src, CM.__file__, 'exec'), CM.__dict__)
sys.argv = _argv
classes, forbid = CM.classes, CM.forbid
sys.path.insert(0, str(ROOT / 'research' / 'LAYERS-20261126-001'))
import layers as LY
STEPS = 4


def exchanged_fast(supports, pin):
    """the same exchange by shortest cycles of the graph reading (no enumeration of the allowed states): with loose values
    pinned a loose distinction has no allowed change and joins no move; free, it is a line to one unconstrained vertex"""
    names = sorted({x for r in supports for x in r}); idx = {x: i for i, x in enumerate(names)}
    holders = collections.defaultdict(list)
    for k, r in enumerate(supports):
        for x in r: holders[x].append(k)
    U = len(supports); adj = collections.defaultdict(list); lines = {}
    for x, h in holders.items():
        if len(h) == 1 and pin: continue
        a, b = (h[0], h[1]) if len(h) == 2 else (h[0], U); lines[idx[x]] = (a, b)
        adj[a].append((b, idx[x])); adj[b].append((a, idx[x]))
    moves = set()
    for e, (a, b) in lines.items():
        dist = {a: 0}; Q = [a]
        for v in Q:
            for w, f in adj[v]:
                if f != e and w not in dist: dist[w] = dist[v] + 1; Q.append(w)
        if b not in dist: continue
        paths = [(b, 0)]
        while paths:
            v, mask = paths.pop()
            if v == a: moves.add(mask | (1 << e)); continue
            for w, f in adj[v]:
                if f != e and dist.get(w, -9) == dist[v] - 1: paths.append((w, mask | (1 << f)))
    return tuple(tuple(names[i] for i in range(len(names)) if (t >> i) & 1) for t in sorted(moves))


def lawful(ex):
    held = collections.Counter(x for k in ex for x in k)
    return bool(ex) and all(len(k) >= 3 for k in ex) and all(v <= 2 for v in held.values())


def step(S, pin):
    st, status, births = forbid.grown(S, 'parity', 'ordinary')
    if status != 'funded': return None, 'does not grow (%s)' % status
    ex = exchanged_fast(st, pin)
    if not lawful(ex): return ex, 'exchange not lawful'
    return ex, 'lawful'


def orbit(S, pin):
    seen = [S]; out = []
    cur = S
    for i in range(STEPS):
        ex, why = step(cur, pin)
        if why != 'lawful': out.append(why); break
        hit = next((j for j, T in enumerate(seen) if CM.same(ex, T)), None)
        if hit is not None:
            out.append('returns to the start' if hit == 0 else ('fixed at step %d' % hit if hit == len(seen) - 1 else 'cycle back to step %d' % hit))
            break
        out.append('a new start (%d knots)' % len(ex)); seen.append(ex); cur = ex
    return out


def tree_start(n, rng):
    sys.path.insert(0, str(ROOT / 'research' / 'ON-DEMAND-20261126-001'))
    import run as ODR
    sizes, edges = ODR.WL.sample('tree', n, rng)
    return tuple(tuple(k) for k in ODR.stars_of(sizes, edges))


def structures():
    for n in range(4, 11): yield 'ring of %d' % n, classes.ring(n, 2)
    rng = random.Random(20261207)
    for n in (5, 6, 7, 8):
        for j in range(3): yield 'tree of %d (%d)' % (n, j), tree_start(n, rng)
    for name, rings, joins in LY.STRUCTURES[3:9]:
        yield name, LY.build(rings, joins)[0]


def shape(S):
    """the start's sharing pattern: shared distinctions per knot, whether it is one ring, the loose counts"""
    holders = collections.defaultdict(list)
    for k, r in enumerate(S):
        for x in r: holders[x].append(k)
    deg = collections.Counter(); nb = collections.defaultdict(set)
    for x, h in holders.items():
        if len(h) == 2: deg[h[0]] += 1; deg[h[1]] += 1; nb[h[0]].add(h[1]); nb[h[1]].add(h[0])
    loose = [sum(1 for x in r if len(holders[x]) == 1) for r in S]
    seen = {0}; st = [0]
    while st:
        a = st.pop()
        for b in nb[a]:
            if b not in seen: seen.add(b); st.append(b)
    ring = len(S) >= 3 and all(deg[k] == 2 and len(nb[k]) == 2 for k in range(len(S))) and len(seen) == len(S)
    return {'most shared distinctions at a knot': max(deg.values(), default=0), 'one ring': ring, 'loose': loose}


def frozen_items(which):
    if which == 'census':
        S = forbid.census()
        for i, s in enumerate(S): yield 'census %d' % i, forbid.supports_of(s)
    else:
        for n in (6, 7, 8):
            for j, s in enumerate(forbid.sampled(n, 300, 20261206 + n)): yield 'held out %d-%d' % (n, j), forbid.supports_of(s)


if __name__ == '__main__':
    if sys.argv[1] in ('census', 'heldout'):
        with open(sys.argv[2], 'w') as f:
            for name, S in frozen_items(sys.argv[1]):
                rec = {'start': name, 'knots': len(S)}; rec.update(shape(S))
                try:
                    ex, why = step(S, True); rec['pinned exchange'] = why
                    if why == 'lawful':
                        rec['returns'] = CM.same(ex, S); rec['orbit'] = orbit(S, True)
                    ex2, why2 = step(S, False); rec['free exchange'] = why2
                except Exception as e: rec['error'] = repr(e)[:200]
                f.write(json.dumps(rec) + '\n'); f.flush()
    if sys.argv[1] == 'explore':
        with open(sys.argv[2], 'w') as f:
            for name, S in structures():
                rec = {'structure': name, 'knots': len(S), 'pinned': orbit(S, True), 'free': orbit(S, False)}
                f.write(json.dumps(rec) + '\n'); f.flush(); print(json.dumps(rec), flush=True)
