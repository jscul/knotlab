"""Shared-runner job for DEAD-CAP-20261119-001A-P001's machine check (frozen with the proof).

Cases:
- d1-n-c: D1 on connected graphs of n knots (networkx's atlas, n = 1..6), chunk c: every dead set and open assignment, read on the
  data (no sizes needed). The class conditions are evaluated from their definitions, then Lemma 1, Lemma 2's skeleton, its ray
  kinds and its boundary are checked.
- census-c: D2/D3 on the touch census's in-class arrangements with a dead knot, chunk c.
- rand-n-s: D2/D3/D4/D6 on random in-class starts of n knots (6..16) with a dead knot, within five places (sampler A), seed s.
- skel-k-s: the same on skeleton starts (sampler B): k dead three-place hubs, each with three five-place members, members joined
  through chains of one or two two-point blocks or ended by a connector and an end knot.
- fam: D5 on the theta and T_1, T_2, T_3.
Every start in D2 is grown by the engine to round 20 or 4,000 junctions and compared with the branch system round by round."""
import importlib.util
import itertools
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import deadlib as DL  # noqa: E402

_s = importlib.util.spec_from_file_location('cc_mc_d', ROOT / 'proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py')
CC = importlib.util.module_from_spec(_s)
sys.modules['cc_mc_d'] = CC
_s.loader.exec_module(CC)
DC, DM, SL, J = CC.DC, CC.DM, CC.SL, CC.J
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

T, MAXJ = 20, 4000
N_RAND, N_SKEL = 1250, 250
ATLAS = None


def atlas(n):
    global ATLAS
    if ATLAS is None:
        ATLAS = defaultdict(list)
        for G in nx.graph_atlas_g():
            if G.number_of_nodes() >= 1 and nx.is_connected(G):
                ATLAS[G.number_of_nodes()].append(G)
    return ATLAS[n]


def cases():
    for n in range(1, 7):
        m = len(atlas(n))
        for c in range((m + 7) // 8):
            yield f'd1-{n}-{c:02d}', {'kind': 'd1', 'n': n, 'chunk': c}
    for c in range(12):
        yield f'census-{c:02d}', {'kind': 'census', 'chunk': c}
    for n in range(6, 17):
        yield f'rand-{n:02d}', {'kind': 'rand', 'n': n}
    for k in (2, 3, 4):
        for s in range(2):
            yield f'skel-{k}-{s}', {'kind': 'skel', 'k': k, 's': s}
    yield 'fam', {'kind': 'fam'}


# ---- D1: on the data --------------------------------------------------------------------------------------------------------
def data_class(n, nbr, live, opn):
    """(S0, S3, S4, S6') read on (graph, live set, open counts), and the blocks; None if a condition fails."""
    blocks = {w: frozenset(nbr[w] & live) for w in range(n) if len(nbr[w] & live) >= 2}
    for u, v in itertools.combinations(sorted(live), 2):
        if len(nbr[u] & nbr[v]) >= 2:
            return 'S4', blocks
    cand = defaultdict(set)
    for B in blocks.values():
        for u, v in itertools.combinations(B, 2):
            cand[u].add(v)
            cand[v].add(u)
    for a in live:
        for b, c in itertools.combinations(sorted(cand[a]), 2):
            if a < b and a < c and c in cand[b] and not (nbr[a] & nbr[b] & nbr[c]):
                return 'S3', blocks
    d = {k: len(cand[k]) for k in live}
    if any(opn[k] < d[k] for k in live):
        return 'S0', blocks
    if sum(opn[k] for k in live) < 2:
        return 'S6', blocks
    return 'in', blocks


def cycle3(blocks):
    """A cycle of three blocks: points a, b, c pairwise in three different blocks, with no block holding all three."""
    of = defaultdict(set)
    for w, B in blocks.items():
        for k in B:
            of[k].add(w)
    pts = sorted(of)
    for a, b, c in itertools.combinations(pts, 3):
        ab, bc, ca = of[a] & of[b], of[b] & of[c], of[c] & of[a]
        if ab and bc and ca and not (of[a] & of[b] & of[c]):
            return True
    return False


def run_d1(n, chunk):
    gs = atlas(n)[chunk * 8:(chunk + 1) * 8]
    tally = Counter()
    bad = []
    for G in gs:
        nbr = {k: set(G[k]) for k in G}
        deg = {k: G.degree(k) for k in G}
        if max(deg.values(), default=0) > 5:
            continue
        for dead in itertools.chain.from_iterable(itertools.combinations(range(n), r) for r in range(n)):
            live = set(range(n)) - set(dead)
            # demand among live knots, as in Lemma 1 (needs S4 and S3 first, so read it from the data)
            ranges = []
            for k in range(n):
                ranges.append([0] if k in dead else list(range(1, 5 - deg[k] + 1)))
            for opn in itertools.product(*ranges):
                st, blocks = data_class(n, nbr, live, opn)
                s4ok = st != 'S4'
                if s4ok:
                    c3 = cycle3(blocks)
                    if (st == 'S3') != c3:
                        bad.append(['boundary', n, sorted(G.edges()), sorted(dead), list(opn)])
                if st != 'in':
                    tally[st] += 1
                    continue
                tally['in'] += 1
                # Lemma 1
                of = defaultdict(list)
                for w, B in blocks.items():
                    for k in B:
                        of[k].append(w)
                ok = all(len(set(B1) & set(B2)) <= 1 for B1, B2 in itertools.combinations(blocks.values(), 2))
                ok &= len(set(blocks.values())) == len(blocks)
                prof = {k: tuple(sorted(len(blocks[w]) for w in of[k])) for k in live}
                ok &= all(p in {(), (2,), (3,), (4,), (5,), (2, 2), (2, 3)} for p in prof.values())
                ok &= all(len(B) <= 5 for B in blocks.values())
                # rays only at lone points and 2-block ends with open 2
                for k in live:
                    d = sum(len(blocks[w]) - 1 for w in of[k])
                    s = opn[k] - d
                    R = {1: 2, 2: 1}.get(opn[k], 0)
                    if s * R > 0 and not (prof[k] == () or (prof[k] == (2,) and opn[k] == 2)):
                        ok = False
                if not ok:
                    bad.append(['lemma', n, sorted(G.edges()), sorted(dead), list(opn)])
    return {'tally': dict(tally), 'bad': bad[:20], 'n_bad': len(bad)}


# ---- D2/D3/D4: realizable starts --------------------------------------------------------------------------------------------
def read_start(sizes, e, tag):
    A = DL.analyse(sizes, e)
    rd, det = DL.reading(A)
    D, why = DM.predict(sizes, e)
    g = J.grow(sizes, e, rounds=T, maxj=MAXJ)
    cs = g['counts']
    x = DL.exact_counts(A, len(cs) - 1)
    ranks = [P['rank'] for P in A['pieces']]
    rates, d4 = [], []
    for P in A['pieces']:
        if P['rank'] == 1:
            nn, W = DL.one_cycle_W(A, P)
            r1 = DL.rate_of(W)
            if r1 > 1.0:
                r2 = DL.branch_rate(A, P)
                d4.append(abs(r1 - r2) < 1e-6)
            rates.append(r1)
        elif P['rank'] >= 2:
            rates.append(DL.branch_rate(A, P))
    return {'tag': tag, 'n': len(sizes), 'dead': sum(o == 0 for o in A['open']), 'max_places': max(sizes), 'ranks': ranks,
            'reading': rd, 'program': SL.label(D), 'agree_reading': rd == SL.label(D), 'rounds': len(cs) - 1,
            'counts_equal': x == cs, 'rate': max(rates) if rates else 1.0, 'd4': d4, 'sizes': sizes, 'edges': e if max(ranks) >= 2 else None}


def realize(n, edges, dead, surplus, rng):
    """Sizes for a simple graph with dead knots: live knots at shared + max(1, d) (+ surplus), dead knots at shared, with extra
    multiplicity on lines at dead knots until each has three places.  None if impossible within five places."""
    e = list(edges)
    for _ in range(12):
        sh = Counter()
        nb = defaultdict(set)
        for a, b in e:
            sh[a] += 1
            sh[b] += 1
            nb[a].add(b)
            nb[b].add(a)
        short = [w for w in dead if sh[w] < 3]
        if not short:
            break
        w = short[0]
        cand = sorted(nb[w])
        e.append(tuple(sorted((w, rng.choice(cand)))))
    else:
        return None
    sh = Counter()
    nb = defaultdict(set)
    for a, b in e:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    live = set(range(n)) - set(dead)
    blocks = [nb[w] & live for w in range(n) if len(nb[w] & live) >= 2]
    d = Counter()
    for B in blocks:
        for k in B:
            d[k] += len(B) - 1
    sizes = [sh[k] if k in dead else sh[k] + max(1, d[k]) + surplus.get(k, 0) for k in range(n)]
    if max(sizes) > 5 or min(sizes) < 3:
        return None
    return sizes, sorted(e)


def sample_rand(n, rng, want):
    out, tries = [], 0
    while len(out) < want and tries < want * 4000:
        tries += 1
        tree = W_tree(n, rng)
        lam = rng.choice((0.5, 1.0, 2.0))
        have = set(tree)
        non = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in have]
        r = min(_poisson(lam, rng), len(non))
        edges = tree + rng.sample(non, r)
        dead = [k for k in range(n) if rng.random() < 0.35]
        if not dead:
            continue
        surplus = {k: 1 for k in range(n) if rng.random() < 0.3}
        z = realize(n, edges, dead, surplus, rng)
        if z is None:
            continue
        sizes, e = z
        if not J.connected(n, e) or DC.classify(sizes, e) != 'in':
            continue
        if not any(sizes[k] == sum(1 for x in e if k in x) for k in range(n)):
            continue
        out.append((sizes, e))
    return out, tries


def W_tree(n, rng):
    if n == 2:
        return [(0, 1)]
    code = [rng.randrange(n) for _ in range(n - 2)]
    deg = [1] * n
    for x in code:
        deg[x] += 1
    edges = []
    for x in code:
        leaf = min(i for i in range(n) if deg[i] == 1)
        edges.append(tuple(sorted((leaf, x))))
        deg[leaf] -= 1
        deg[x] -= 1
    u, v = [i for i in range(n) if deg[i] == 1]
    edges.append((u, v))
    return edges


def _poisson(lam, rng):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def sample_skel(k, rng, want):
    """Skeleton starts: k dead hubs (3 places) with three members each; member slots paired into chains of one two-point block
    (member - X - member) or two (member - X - Y - Z - member), or ended (member - X - K); then sized as in realize()."""
    out, tries = [], 0
    while len(out) < want and tries < want * 400:
        tries += 1
        edges, nxt = [], 0

        def new():
            nonlocal nxt
            nxt += 1
            return nxt - 1
        hubs = [new() for _ in range(k)]
        slots = []
        for h in hubs:
            for _ in range(3):
                m = new()
                edges.append((h, m))
                slots.append(m)
        rng.shuffle(slots)
        while slots:
            a = slots.pop()
            if slots and rng.random() < 0.7:
                b = slots.pop()
                if rng.random() < 0.6:
                    x = new()
                    edges += [(a, x), (b, x)]
                else:
                    x, y, z = new(), new(), new()
                    edges += [(a, x), (x, y), (y, z), (z, b)]
            else:
                x, kk = new(), new()
                edges += [(a, x), (x, kk)]
        n = nxt
        e = [tuple(sorted(x)) for x in edges]
        if len(set(e)) != len(e) or not J.connected(n, e):
            continue
        surplus = {q: 1 for q in range(n) if q not in hubs and rng.random() < 0.15}
        z = realize(n, e, hubs, surplus, rng)
        if z is None:
            continue
        sizes, e2 = z
        if DC.classify(sizes, e2) != 'in':
            continue
        out.append((sizes, e2))
    return out, tries


def run(case_id, payload):
    kind = payload['kind']
    if kind == 'd1':
        return run_d1(payload['n'], payload['chunk'])
    if kind == 'census':
        R = load_results(str(ROOT / 'runs/touch-census'))
        keys = [(tuple(a['key'][0]), tuple(a['key'][1])) for r in R.values() if r.get('status') == 'ok' for a in r['result']['arrangements']]
        keys = keys[payload['chunk']::12]
        res = []
        for key in keys:
            sizes, e = DC.edges_of(key)
            if DC.classify(sizes, e) != 'in':
                continue
            sh = Counter()
            for a, b in e:
                sh[a] += 1
                sh[b] += 1
            if all(sizes[k] > sh[k] for k in range(len(sizes))):
                continue
            res.append(read_start(sizes, e, 'census'))
        return {'starts': res}
    if kind == 'rand':
        rng = random.Random(f'dead-cap-rand-{payload["n"]}')
        ss, tries = sample_rand(payload['n'], rng, N_RAND // 11 + 1)
        return {'starts': [read_start(s, e, 'rand') for s, e in ss], 'tries': tries}
    if kind == 'skel':
        rng = random.Random(f'dead-cap-skel-{payload["k"]}-{payload["s"]}')
        ss, tries = sample_skel(payload['k'], rng, N_SKEL)
        return {'starts': [read_start(s, e, 'skel') for s, e in ss], 'tries': tries}
    if kind == 'fam':
        res = []
        e = []
        for i in range(3):
            e += [(0, 2 + i), (1, 5 + i), (2 + i, 8 + i), (5 + i, 8 + i)]
        e = [tuple(sorted(x)) for x in e]
        theta = read_start([3, 3] + [5] * 6 + [3] * 3, e, 'theta')
        A = DL.analyse([3, 3] + [5] * 6 + [3] * 3, e)
        theta['series_to_25'] = DL.exact_counts(A, 25)
        res.append(theta)
        for h in (1, 2, 3):
            s, e = CC.family_T(h)
            res.append(read_start(s, e, f'T_{h}'))
        return {'starts': res}
    raise ValueError(kind)
