"""Readings made from the sweeps' saved classes, after the advisor's review: the swap pairs, and the round in which
pairs that agree to two steps are first told apart.  Usage: after.py swap_family.jsonl every_seed.jsonl"""
import sys, os, json, gzip, collections, itertools
ARGS = [os.path.abspath(p) for p in sys.argv[1:]]          # the engine's folder becomes the working directory on import
import profile
def load(p):
    f = gzip.open(p, 'rt') if p.endswith('.gz') else open(p)
    rows = [json.loads(l) for l in f if l.strip()]
    return [r for r in rows if 'error' not in r], [r for r in rows if 'error' in r]
grp = lambda r: ('take of a sole candidate' if r['spec']['take'] else 'no taking rule', {'CANCEL-RETIRE': 'retire', 'CANCEL-OFFSHOOT': 'offshoots', 'CANCEL-WAIT': 'wait'}[r['spec']['treatment']])

# 1. the swap pairs: the same knots at the same distances, the two end knots exchanged
rows, bad = load(ARGS[0])
print('swap family:', len(rows), 'studies finished,', len(bad), 'stopped at the time limit')
sw = profile.swap_seeds(); lay = {s['name']: profile.layers(s, 99) for s in sw}
tot = collections.Counter(); hit = collections.Counter(); n = collections.Counter(); ex = []
for r in rows:
    names = r['names']; cl = dict(zip(names, r['class by round'][-1]))
    pairs = [(a, b) for a, b in itertools.combinations(names, 2) if lay[a] == lay[b]]
    assert len(pairs) == 27
    apart = [(a, b) for a, b in pairs if cl[a] != cl[b]]
    g = grp(r); n[g] += 1; tot[g] += len(apart); hit[g] += bool(apart)
    if apart: ex.append((r['spec']['ration'], r['spec']['treatment'], r['spec']['take'], r['first'], r['R*'], len(apart), apart[0]))
for g in sorted(n): print('  %-26s %-9s studies %3d | with a swap pair told apart %3d | swap pairs told apart %4d of %4d' % (g[0], g[1], n[g], hit[g], tot[g], 27 * n[g]))
print('  all: studies with a swap pair told apart', sum(hit.values()), 'of', len(rows), '| pairs', sum(tot.values()), 'of', 27 * len(rows))
for e in ex[:6]: print('   ', e)
print('  by first seed:', sorted(collections.Counter(e[3] for e in ex).items()))

# 2. pairs of the 345 seeds that agree to two steps: the round in which they are first told apart
rows, bad = load(ARGS[1])
S = profile.every_seed(); r2 = {s['name']: profile.reach(s, 2) for s in S}; r3 = {s['name']: profile.reach(s, 3) for s in S}
far = {s['name']: max(d for d, _, _ in profile.reach(s, 99)[0]) for s in S}
print('\n345 seeds:', len(rows), 'studies finished,', len(bad), 'stopped:', sorted((b['spec']['ration'], b['spec']['treatment'], b['spec']['take'], b['spec']['first']) for b in bad))
print('  seeds whose farthest knot is at most two steps from the held knot:', sum(1 for v in far.values() if v <= 2), 'of', len(far))
names = rows[0]['names']
P2 = [(a, b) for a, b in itertools.combinations(names, 2) if r2[a] == r2[b]]
P3 = [(a, b) for a, b in P2 if r3[a] == r3[b]]
print('  pairs that agree to two steps:', len(P2), '| to three:', len(P3), '| of', len(names) * (len(names) - 1) // 2)
first = collections.defaultdict(collections.Counter); st = collections.Counter(); sthit = collections.Counter(); Rs = collections.defaultdict(collections.Counter)
for r in rows:
    assert r['names'] == names
    g = grp(r); st[g] += 1; Rs[g][r['R*']] += 1; cb = r['class by round']; ix = {m: i for i, m in enumerate(names)}
    h = 0
    for a, b in P2:
        t = next((k + 1 for k, c in enumerate(cb) if c[ix[a]] != c[ix[b]]), None)
        first[g][t if t else 'never'] += 1; h += bool(t)
    sthit[g] += bool(h)
for g in sorted(st):
    print('  %-26s %-9s studies %3d (R* %s) | with such a pair told apart %3d | first told apart in round: %s' % (g[0], g[1], st[g], dict(sorted(Rs[g].items())), sthit[g], dict(sorted(first[g].items(), key=str))))
# 3. the share of all pairs told apart, and of pairs with the same held knot, for the baselines
print('\n  all pairs told apart: %d of %d (%.1f%%)' % (sum(r['pairs told apart'] for r in rows), sum(r['pairs'] for r in rows), 100 * sum(r['pairs told apart'] for r in rows) / sum(r['pairs'] for r in rows)))
ho = [r for r in rows if r['first'] in 'KLMNO']
print('  held-out first seeds: %d studies, all pairs told apart %.1f%%' % (len(ho), 100 * sum(r['pairs told apart'] for r in ho) / sum(r['pairs'] for r in ho)))
