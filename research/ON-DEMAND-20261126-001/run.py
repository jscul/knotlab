"""run.py POPULATION COUNT SEED T OUT.jsonl: the frozen tests (README, "Frozen") on one population.  ON-DEMAND-20261126-001.

For each start (drawn as the population says, random.Random(SEED)) and one reader (a live start knot, the same
generator), under both knot laws:
  H1  the growth on the live knots within t + 1 holder steps of the reader (the reach of round t; blocks of every holder
      cut to it, open counts unchanged) against the full growth, the reader's view through round t, for t = 1..T; and
      within t steps, reported; the births the region makes that the full growth does not (named by descent), and the
      births the view rests on, reported;
  H2  three regions holding the reach (t drawn), each the reach plus every further live knot with probability one half,
      and the reach, then half the rest, then all admitted, each against the full growth through round t;
  H3  under parity, how each region growth that differs ends; for a start that stalls in round 1, the least number of
      holder steps whose knots stall too (none when the short knot is outside the reader's piece).
POPULATION: tree40 (WEIGHTINGS 'tree', 40 knots), treeplus25 (WEIGHTINGS 'tree+', 25 knots), census6 (the uniform
six-knot sample of LATE-VIEWS-20261126-001).  The full growth stops before a round of more than CAP births; rounds past it are not read (the region growths are
not capped)."""
import sys, os, json, random, time, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ondemand as O
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
_s = importlib.util.spec_from_file_location('wl', ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
WL = importlib.util.module_from_spec(_s); _s.loader.exec_module(WL)
sys.path.insert(0, os.path.join(HERE, '..', 'LATE-VIEWS-20261126-001'))
from sample_grow import stars_of
CAP = 3000


def population(name, count, rng):
    if name == 'census6':
        import sample as LS
        S = LS.fresh()
        for i, gi, loose, stars in rng.sample(S, min(count, len(S))): yield i, stars
        return
    kind, n = {'tree40': ('tree', 40), 'treeplus25': ('tree+', 25)}[name]
    for i in range(count):
        sizes, edges = WL.sample(kind, n, rng); yield i, stars_of(sizes, edges)


def views(g, k, t):
    V = O.view(g, k)[:t]
    return V + [(collections.Counter(), collections.Counter())] * (t - len(V))


def readable(full, T):
    """the rounds of the full growth that can be compared: all T, or those before a cap"""
    return len(full['rounds']) if full['end'] == 'cap' else T


def keys(g):
    """per round, the multiset of births named by descent (a start knot by its number, a birth by its parents' names)"""
    name = {}; out = []
    for row in g['rounds']:
        c = collections.Counter()
        for j in row:
            name[j] = tuple(sorted(name.get(v, ('start', v)) for v in g['par'][j])); c[name[j]] += 1
        out.append(c)
    return out


def needed(full, k, t):
    """the births of rounds 1..t of the full growth that the reader's view through round t rests on: its births and
    every birth among their ancestors by parenthood; against all births of those rounds"""
    rows = full['rounds'][:t]; inview = [j for row in rows for j in row if k in full['anc'][j]]
    born = {j for row in rows for j in row}; seen = set(inview); st = list(inview)
    while st:
        j = st.pop()
        for v in full['par'].get(j, ()):
            if v in born and v not in seen: seen.add(v); st.append(v)
    return len(seen), len(born)


def draw(opn, B, rng, T):
    """the reader and the random regions, drawn in the order the frozen runs drew them"""
    k = rng.choice(sorted(opn)); D = O.dist_from(k, set(opn), B)
    reach = lambda r: {v for v in D if D[v] <= r}
    tH2 = [rng.randint(1, T) for _ in range(3)]
    extra = [{v for v in opn if v not in reach(t + 1) and rng.random() < 0.5} for t in tH2]
    rest = sorted(set(opn) - reach(tH2[0] + 1)); rng.shuffle(rest)
    return k, D, tH2, extra, rest


def one(name, i, stars, rng, T, drawn=None, region_cap=None):
    opn, places, B = O.roster(stars)
    if not opn: return None
    k, D, tH2, extra, rest = drawn if drawn is not None else draw(opn, B, rng, T)
    reach = lambda r: {v for v in D if D[v] <= r}
    rec = {'population': name, 'index': i, 'reader': k, 'eccentricity': max(D.values()), 'live': len(opn),
           'live in the reader piece': len(D), 'laws': {}}
    def G(t, law, region):
        g = O.grow(opn, places, B, t, law, region=region, cap=region_cap)
        return g, (g['end'] == 'cap')
    for law in ('nae', 'parity'):
        full = O.grow(opn, places, B, T, law, cap=CAP); r = {'end': full['end'], 'rounds read': readable(full, T)}
        if full['end'] == 'stall':
            r['least steps whose knots stall'] = next((q for q in range(0, max(D.values()) + 1)
                                                       if O.grow(opn, places, B, 1, law, region=reach(q))['end'] == 'stall'), None)
            rec['laws'][law] = r; continue
        n = r['rounds read']; Vf = views(full, k, n); Kf = keys(full) + [collections.Counter()] * T
        h1 = {}; h1t = {}; ends = {}; prov = {}; need = {}; capped = []
        for t in range(1, n + 1):
            g, c = G(t, law, reach(t + 1))
            if c: capped.append(['H1', t]); continue
            h1[t] = views(g, k, t) == Vf[:t]
            if not h1[t]: ends[t] = g['end']
            Kg = keys(g); kg = Kg[t - 1] if len(Kg) >= t else collections.Counter()
            prov[t] = [sum((kg - Kf[t - 1]).values()), sum(kg.values())]
            g0, c0 = G(t, law, reach(t))
            if not c0: h1t[t] = views(g0, k, t) == Vf[:t]
            need[t] = needed(full, k, t)
        r['H1 within t + 1 steps agrees'] = h1; r['within t steps agrees'] = h1t; r['region ends where H1 differs'] = ends
        r['births of the region not in the full growth, of all the region\'s births, at round t'] = prov
        r['births needed, of all births, through round t'] = need
        h2 = []
        for t, X in zip(tH2, extra):
            if t > n: continue
            g, c = G(t, law, reach(t + 1) | X)
            if c: capped.append(['H2', t]); continue
            h2.append([t, len(X), views(g, k, t) == Vf[:t]])
        t = tH2[0]
        if t <= n:
            steps = [reach(t + 1), reach(t + 1) | set(rest[:len(rest) // 2]), set(opn)]
            oks = []
            for R in steps:
                g, c = G(t, law, R)
                if c: capped.append(['H2 admitted', t]); continue
                oks.append(views(g, k, t) == Vf[:t])
            h2.append([t, 'admitted in three steps', oks])
        r['H2'] = h2; r['region growths stopped at the cap, not read'] = capped
        rec['laws'][law] = r
    return rec


def child(conn, name, i, stars, T, drawn, limit):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    try: conn.send(one(name, i, stars, None, T, drawn, region_cap=CAP))
    except MemoryError: conn.send('memory')
    conn.close()


def guarded(name, i, stars, rng, T, limit=3 << 30, seconds=300):
    """the deviation recorded before the rerun of the tree-plus-lines set: each start in a child process with 3 GB of
    address space and 300 seconds, region growths capped like the full growth; a start over either is not read"""
    import multiprocessing as mp
    opn, places, B = O.roster(stars)
    if not opn: return None
    drawn = draw(opn, B, rng, T)
    a, b = mp.Pipe(False); p = mp.get_context('fork').Process(target=child, args=(b, name, i, stars, T, drawn, limit))
    p.start(); out = a.recv() if a.poll(seconds) else 'time'
    p.join(5)
    if p.is_alive(): p.kill(); p.join()
    if isinstance(out, dict) or out is None: return out
    return {'population': name, 'index': i, 'reader': drawn[0], 'not read': out}


if __name__ == '__main__':
    name, count, seed, T, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    guard = len(sys.argv) > 6 and sys.argv[6] == 'guarded'
    rng = random.Random(seed)
    with open(out, 'w') as f:
        for i, stars in population(name, count, rng):
            t0 = time.time(); rec = guarded(name, i, stars, rng, T) if guard else one(name, i, stars, rng, T)
            if rec is None: continue
            rec['seconds'] = round(time.time() - t0, 2); f.write(json.dumps(rec) + '\n'); f.flush()
