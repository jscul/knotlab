"""The drafter's probe, second version, for the readings the advisor asked for (run on the families already seen,
before the freeze; on the fresh material only after the engine's outputs are in).  One study a call."""
import sys, os, json, time, itertools, collections, resource
from collections import Counter, defaultdict
sys.setrecursionlimit(100000); sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('PROBE_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
XDIR = ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot'
import eng
sys.path.append(XDIR); os.chdir(XDIR)
import read
SEEDS = json.load(open(os.environ.get('PROBE_SEEDS', ROOT + '/research/FOLLOWS-THE-FORM-20261125-001A/seeds.json')))

def start(F, sec, linked=True):
    f = SEEDS['first'][F]; stars = [list(k) for k in f['knots']]
    nF = 1 + max(d for k in stars for d in k); link = nF
    stars[f['site']].append(link)
    nf = len(stars)
    if sec is not None:
        for k in sec['knots']: stars.append([d + nF + 1 for d in k])
        if linked: stars[nf + sec['at']].append(link)
        else: stars[nf + sec['at']].append(1 + max(d for k in stars for d in k))     # a loose distinction of its own
    return stars, nf

def at_features(sec):
    ks = sec['knots']; at = sec['at']; hold = defaultdict(list)
    for i, k in enumerate(ks):
        for d in k: hold[d].append(i)
    loose = sum(1 for d in ks[at] if len(hold[d]) == 1)
    partners = len({j for d in ks[at] for j in hold[d] if j != at})
    return (len(ks[at]) + 1, loose, partners)

def grow(law, stars, nf, rounds):
    run = eng.Run(law, stars=stars, rounds=rounds, knot_bound=3000)
    bits = read.desc_bits(run, 0, {u: (0 if u < nf else 1) for u in range(len(stars))})
    S = run.S; own = []; cone = []; y = []; nown = []; ncone = []; last_start = 0
    for t in range(1, run.rounds_read + 1):
        bs = run.recs[t - 1]['births']
        e = lambda b: (b['kind'], len(b['parents']), len(S.places[b['id']]), b['f'], len(b['takes']))
        o = tuple(sorted(e(b) for b in bs if bits[b['id']] == 1))
        c = tuple(sorted(e(b) + (bits[b['id']] == 1,) for b in bs if bits[b['id']] & 1))
        own.append(o); cone.append(c); nown.append(len(o)); ncone.append(len(c))
        y.append(sum(1 for b in bs if bits[b['id']] == 2))
        if any(u < len(stars) for u in run.recs[t - 1]['members']): last_start = t
    return {'read': run.rounds_read, 'stop': run.stop, 'own': own, 'cone': cone, 'y': y, 'nown': nown, 'ncone': ncone, 'last_start': last_start}

def classes(runs, key, R):
    seen = {}
    return {n: seen.setdefault(tuple(r[key][:R]), len(seen)) for n, r in runs.items()}

def study(law, F, family, rounds, linked=True):
    secs = SEEDS['second'][family]
    runs = {'(none)': grow(law, *start(F, None), rounds)}
    for s in secs: runs[s['name']] = grow(law, *start(F, s, linked), rounds)
    names = [s['name'] for s in secs]
    Rs = min(r['read'] for r in runs.values()); L = max(r['read'] for r in runs.values())
    Cown = classes(runs, 'own', Rs); Ccone = classes(runs, 'cone', Rs)
    out = {'law': law.name(), 'first': F, 'family': family, 'linked': linked, 'R*': Rs, 'L': L,
           'classes among forms, own': len({Cown[n] for n in names}), 'classes among forms, cone': len({Ccone[n] for n in names}),
           'bare start alone': not any(Cown[n] == Cown['(none)'] for n in names),
           'max last round a start knot is a member': max(r['last_start'] for r in runs.values())}
    # the count profile
    feat = {s['name']: at_features(s) for s in secs}
    def function_of(key):
        g = defaultdict(set)
        for n in names: g[key(n)].add(Cown[n])
        return all(len(v) == 1 for v in g.values())
    out['class is a function of the held knot'] = function_of(lambda n: feat[n])
    out['class is a function of the second seed\'s births by round'] = function_of(lambda n: tuple(runs[n]['y'][:Rs]))
    out['class is a function of both'] = function_of(lambda n: (feat[n], tuple(runs[n]['y'][:Rs])))
    # pairs: first told apart (own), and the round at which the cone records first differ
    pair = Counter()
    for a, b in itertools.combinations(names, 2):
        ra, rb = runs[a], runs[b]; r = min(ra['read'], rb['read'])
        t = next((i + 1 for i in range(r) if ra['own'][i] != rb['own'][i]), None)
        e = next((i + 1 for i in range(r) if ra['cone'][i] != rb['cone'][i]), None)
        pair['told apart at R*'] += Cown[a] != Cown[b]
        if t is None: pair['never' if r == L else 'not read further'] += 1
        else:
            pair['first told apart in round %d' % t] += 1
            if t >= 2: pair['in round 2 or later'] += 1
            if t >= 2 and e >= 2: pair['in round 2 or later, the round-1 record of every birth with a first-seed ancestor the same'] += 1
            if t >= 3 and e >= 3: pair['in round 3 or later, those records the same through round 2'] += 1
    out['pairs'] = dict(pair); out['pairs in all'] = len(names) * (len(names) - 1) // 2
    # fates on the study's window R*-2..R*
    fates = Counter()
    if Rs >= 4:
        for n in names:
            x = runs[n]['nown'][Rs - 3:Rs]; c = runs[n]['ncone'][Rs - 3:Rs]
            if x == [0, 0, 0]: fates['ends: no births in the cone' if c == [0, 0, 0] else 'ends: every birth is of both'] += 1
            elif x[0] == x[1] == x[2]: fates['steady'] += 1
            elif x[0] < x[1] < x[2]: fates['grows'] += 1
            elif x[0] > x[1] > x[2]: fates['shrinks'] += 1
            else: fates['other'] += 1
    else: fates['not read'] = len(names)
    out['fates'] = dict(fates)
    out['class of each form'] = {n: Cown[n] for n in names}
    return out

if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    spec = json.loads(sys.argv[1])
    law = eng.Law(spec['ration'], spec['treatment'], spec.get('take'), spec.get('knot_law', 'nae'))
    t0 = time.time()
    o = study(law, spec['first'], spec['family'], spec.get('rounds', 9), linked=spec.get('linked', True))
    o['seconds'] = round(time.time() - t0, 1); o['spec'] = spec
    print(json.dumps(o))
