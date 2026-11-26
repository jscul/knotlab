"""What decides the class where the registered count profile does not?  (A check by the thread after the registered
study FOLLOWS-THE-FORM-20261125-001A closed; not a registered study.)

Written BEFORE its first run.  For one study (law, first seed, family) every start is grown again on the shared
engine, and for each second seed these are kept, through the study's last common round R*:
  own   what the first seed's own descent makes (FF 5): the classes are by this;
  sec   what the SECOND seed's own descent makes: its births round by round, each by kind, parents, places, fresh, takes;
  both  the same for the births that are of both seeds;
and, from the seed alone, the second seed as seen from its held knot out to 0, 1 and 2 steps (each knot with its loose
count and its number of partners).
Two ladders of profiles are then tried.  A profile DECIDES the class in a study when no two second seeds with the
same profile are told apart; beside it is the number of pairs that share the profile, since a profile that no two
seeds share decides nothing.
  counts, in order:  the held knot | the held knot + how many births the second seed makes each round (the registered
                     profile) | the held knot + what those births are | the held knot + those + the births of both
  reach, in order:   the seed to 0 steps (the held knot) | to 1 step | to 2 steps | the whole seed
Expected, before the run: the held knot with what the second seed's own births are decides the class in every study
(what is followed is counts, round by round); and the seed to 2 steps decides it wherever there is no taking rule.

Added AFTER two timed studies were seen (ordinary count, retiring, no take, first seed K; ordinary count, waiting,
sole take, first seed L), in which the expectation above already failed: the three "shared" profiles (the births of
both seeds alone) and the seed to three steps; and, after the first sweep, the profile "knots" (the same knots, without
which is next to which).

Added after an advisor model read the first tables (its points are in the README): the profiles "layers" (each knot
by its distance from the held knot, its loose count and its number of partners, WITHOUT which knots are partners),
the class of every second seed through each round (so that any further profile can be tallied from the output), and
the family `swap`: five knots in a row held at the middle one, in pairs that differ only in which end knot is the
partner of which neighbour of the held knot.  In the 345 seeds no two share their layers, so there "which knots are
partners" cannot be told from counts by distance; the swap pairs share their layers by construction.  No expectation
was written for the swap pairs: I did not know."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get('PROBE_FFP', os.path.join(HERE, '..', 'second_count')))     # run its make_engine.py first
import ffp
from ffp import eng, read, SEEDS, start, at_features

def grow(law, stars, nf, rounds):
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=3000)
    bits = read.desc_bits(run, 0, {u: (0 if u < nf else 1) for u in range(len(stars))})
    S = run.S; own = []; sec = []; both = []
    e = lambda b: (b['kind'], len(b['parents']), len(S.places[b['id']]), b['f'], len(b['takes']))
    for t in range(1, run.rounds_read + 1):
        bs = run.recs[t - 1]['births']
        own.append(tuple(sorted(e(b) for b in bs if bits[b['id']] == 1)))
        sec.append(tuple(sorted(e(b) for b in bs if bits[b['id']] == 2)))
        both.append(tuple(sorted(e(b) for b in bs if bits[b['id']] == 3)))
    return {'read': run.rounds_read, 'own': own, 'sec': sec, 'both': both}

def reach(secseed, d):
    """The second seed out to d steps from its held knot, up to renaming: each knot within d steps with its loose
    count and its number of partners, and which of them are partners."""
    ks = secseed['knots']; at = secseed['at']; hold = defaultdict(list)
    for i, k in enumerate(ks):
        for x in k: hold[x].append(i)
    loose = [sum(1 for x in k if len(hold[x]) == 1) for k in ks]
    nb = [sorted({j for x in k for j in hold[x] if j != i}) for i, k in enumerate(ks)]
    dist = {at: 0}; q = [at]
    while q:
        u = q.pop(0)
        for v in nb[u]:
            if v not in dist: dist[v] = dist[u] + 1; q.append(v)
    inside = sorted(u for u in dist if dist[u] <= d)
    best = None
    for p in itertools.permutations(range(len(inside))):
        if inside[p[0]] != at: continue                         # the held knot first
        order = [inside[i] for i in p]; pos = {u: i for i, u in enumerate(order)}
        key = (tuple((dist[u], loose[u], len(nb[u])) for u in order),
               tuple(sorted((pos[u], pos[v]) for u in order for v in nb[u] if v in pos and pos[u] < pos[v])))
        if best is None or key < best: best = key
    return best

def layers(secseed, d):
    """Each knot within d steps of the held knot by (distance, loose count, number of partners), as a multiset."""
    return tuple(sorted(reach(secseed, d)[0]))

def swap_seeds():
    """Five knots in a row, c - a - h - b - d, held at the middle one: for each h in 0..2, a < b in 1..3 and c < d in
    2..4, the seed and the same with the two end knots exchanged.  27 pairs, 54 seeds."""
    out = []
    for h in range(3):
        for a, b in itertools.combinations((1, 2, 3), 2):
            for c, d in itertools.combinations((2, 3, 4), 2):
                for x, y in ((c, d), (d, c)):
                    lo = (x, a, h, b, y)
                    out.append({'name': 'row5:%d,%d,[%d],%d,%d' % lo, 'knots': _seed('path', lo), 'at': 2})
    return out

def _seed(shape, loose):
    n = len(loose)
    pairs = {'star3': [(0, 1), (0, 2), (0, 3)]}.get(shape)
    if shape == 'path': pairs = [(i, i + 1) for i in range(n - 1)]
    if shape == 'ring': pairs = [(i, (i + 1) % n) for i in range(n)]
    knots = [[] for _ in range(n)]; nxt = 0
    for a, b in pairs:
        knots[a].append(nxt); knots[b].append(nxt); nxt += 1
    for i in range(n):
        for _ in range(loose[i]):
            knots[i].append(nxt); nxt += 1
    return knots

def every_seed():
    """Every second seed of the study's four families, and the rest of the written list of 207 from which the
    held-out family was drawn (FF 3), one for each form up to renaming: 345 seeds (138 forms in the three families
    grown before the freeze, and the 207 of the written list)."""
    out = []; seen = set()
    def add(name, knots, at):
        if not all(len(k) + (1 if i == at else 0) >= 3 for i, k in enumerate(knots)): return
        s = {'name': name, 'knots': knots, 'at': at}; c = reach(s, 99)
        if c in seen: return
        seen.add(c); out.append(s)
    for fam in ('mixed', 'chains', 'second'):
        for s in SEEDS['second'][fam]: add(s['name'], s['knots'], s['at'])
    n_seen = len(out)
    for n in (1, 2, 3, 4):
        for lo in itertools.product(range(4), repeat=n):
            for at in range(n): add('path:%s@%d' % (','.join(map(str, lo)), at), _seed('path', lo), at)
    for lo in itertools.product(range(4), repeat=4):
        for at in (0, 1): add('star3:%d;%d,%d,%d@%s' % (lo + ('centre' if at == 0 else 'arm',)), _seed('star3', lo), at)
    for n in (3, 4):
        for lo in itertools.product(range(4), repeat=n): add('ring:%s@0' % ','.join(map(str, lo)), _seed('ring', lo), 0)
    assert len(out) - n_seen == 207, len(out) - n_seen
    assert {s['name'] for s in SEEDS['second']['fresh']} <= {s['name'] for s in out}
    return out

def study(law, F, family, rounds):
    secs = every_seed() if family == 'every' else swap_seeds() if family == 'swap' else SEEDS['second'][family]
    runs = {s['name']: grow(law, *start(F, s), rounds) for s in secs}
    bare = grow(law, *start(F, None), rounds)
    names = [s['name'] for s in secs]; seed_of = {s['name']: s for s in secs}
    Rs = min([bare['read']] + [r['read'] for r in runs.values()])
    cls = {}; seen = {}
    for n in names: cls[n] = seen.setdefault(tuple(runs[n]['own'][:Rs]), len(seen))
    held = {n: at_features(seed_of[n]) for n in names}
    whole = {n: reach(seed_of[n], 99) for n in names}
    knots_of = {n: tuple(sorted((a, b) for _, a, b in whole[n][0])) for n in names}
    prof = {
        'counts 0: the held knot': lambda n: held[n],
        'counts 1: + how many births the second seed makes each round': lambda n: (held[n], tuple(len(x) for x in runs[n]['sec'][:Rs])),
        'counts 2: + what those births are': lambda n: (held[n], tuple(runs[n]['sec'][:Rs])),
        'counts 3: + the births of both': lambda n: (held[n], tuple(runs[n]['sec'][:Rs]), tuple(runs[n]['both'][:Rs])),
        'shared 1: the held knot + how many births of both each round': lambda n: (held[n], tuple(len(x) for x in runs[n]['both'][:Rs])),
        'shared 2: the held knot + what the births of both are': lambda n: (held[n], tuple(runs[n]['both'][:Rs])),
        'shared 3: what the births of both are, without the held knot': lambda n: tuple(runs[n]['both'][:Rs]),
        'knots: the held knot + every knot of the seed by its loose count and its number of partners, not which is next to which': lambda n: (held[n], knots_of[n]),
        'reach 0: the held knot': lambda n: reach(seed_of[n], 0),
        'reach 1: the seed to one step': lambda n: reach(seed_of[n], 1),
        'reach 2: the seed to two steps': lambda n: reach(seed_of[n], 2),
        'reach 3: the seed to three steps': lambda n: reach(seed_of[n], 3),
        'reach all: the whole seed': lambda n: whole[n],
        'layers 1: the knots to one step by distance, loose count and partners, not which are partners': lambda n: layers(seed_of[n], 1),
        'layers 2: the same to two steps': lambda n: layers(seed_of[n], 2),
        'layers all: the same for the whole seed': lambda n: layers(seed_of[n], 99),
    }
    out = {'law': law.name(), 'first': F, 'family': family, 'R*': Rs, 'classes': len(set(cls.values())), 'profiles': {}, 'examples': {}}
    pairs = list(itertools.combinations(names, 2))
    out['pairs told apart'] = sum(1 for a, b in pairs if cls[a] != cls[b]); out['pairs'] = len(pairs)
    out['names'] = names; out['class by round'] = []
    for r in range(1, Rs + 1):
        ids = {}; out['class by round'].append([ids.setdefault(tuple(runs[n]['own'][:r]), len(ids)) for n in names])
    for k, f in prof.items():
        v = {n: f(n) for n in names}
        same = [(a, b) for a, b in pairs if v[a] == v[b]]
        apart = [(a, b) for a, b in same if cls[a] != cls[b]]
        out['profiles'][k] = {'values': len(set(v.values())), 'pairs sharing it': len(same), 'of those told apart': len(apart)}
        if apart: out['examples'][k] = apart[:3]
    return out

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), 'nae')
    t0 = time.time()
    o = study(law, spec['first'], spec['family'], spec.get('rounds', 9))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
