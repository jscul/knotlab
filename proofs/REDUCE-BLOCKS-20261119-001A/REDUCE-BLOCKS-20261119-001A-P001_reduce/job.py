"""Shared-runner job for REDUCE-BLOCKS-20261119-001A-P001's machine check (frozen with the proof).

Every comparison runs in a forked child (3 GB, 120 s): X and its hub realization H(X) are grown and their per-round (parents,
fresh) multisets compared from round 1 on.
- census-c: every touch-census arrangement, stalls included, chunk c of 16, 6 rounds.
- rand-n: 125 random starts of n knots (6..13) within seven places, with no class filter (sample_any), 6 rounds, junction cap
  200,000 within the child's limits.
- stage-i: explosive start i of EXPLOSIVE (16): its stages after s = 1..6 rounds, each against its H, 3 rounds."""
import importlib.util
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import hublib as HB  # noqa: E402

sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


EX = _load('rb_ex', 'experiments/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/job.py')
MB = _load('rb_mb', 'experiments/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/mblib.py')
DC, J = HB.DC, HB.J


def cases():
    for c in range(16):
        yield f'census-{c:02d}', {'kind': 'census', 'c': c}
    for n in range(6, 14):
        yield f'rand-{n:02d}', {'kind': 'rand', 'n': n}
    for i in range(16):
        yield f'stage-{i:02d}', {'kind': 'stage', 'i': i}


def _child(conn, sizes, edges, T, s):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (3_000_000_000, 3_000_000_000))
    if s:
        P = J.S.from_junctions(J.stars_from(sizes, edges))
        P.linalg = False
        for _ in range(s):
            r = P.step(J.F.fewest, None)
            if r is None or r['new'] == 0:
                conn.send({'skip': 'ended before the stage'})
                return
        sizes, edges = MB.stage_of(P)
    conn.send(HB.compare(sizes, edges, T))


def isolated(sizes, edges, T, s=0, seconds=120):
    import multiprocessing as mp
    ctx = mp.get_context('fork')
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=_child, args=(b, sizes, edges, T, s))
    pr.start()
    b.close()
    res = {'skip': 'limit'}
    t0 = time.time()
    while time.time() - t0 < seconds:
        if a.poll(1.0):
            try:
                res = a.recv()
            except EOFError:
                res = {'skip': 'memory'}
            break
        if not pr.is_alive() and not a.poll(0):
            res = {'skip': 'memory'}
            break
    pr.kill()
    pr.join(5)
    return res


def run(case_id, payload):
    k = payload['kind']
    tally = Counter()
    bad = []
    if k == 'census':
        R = load_results(str(ROOT / 'runs/touch-census'))
        keys = [(tuple(a['key'][0]), tuple(a['key'][1])) for r in R.values() if r.get('status') == 'ok' for a in r['result']['arrangements']]
        for key in keys[payload['c']::16]:
            sizes, e = DC.edges_of(key)
            res = HB.compare(sizes, e, 6)
            tally['equal' if res['equal'] else 'differ'] += 1
            if not res['equal'] and len(bad) < 10:
                bad.append([sizes, e])
        return {'tally': dict(tally), 'bad': bad}
    if k == 'rand':
        rng = random.Random(f'reduce-blocks-{case_id}')
        ss, tries = sample_any(payload['n'], rng, 125)
        for sizes, e in ss:
            res = isolated(sizes, e, 6)
            key = 'skip ' + res['skip'] if 'skip' in res else ('equal' if res['equal'] else 'differ')
            tally[key] += 1
            if key == 'differ' and len(bad) < 10:
                bad.append([sizes, e])
        return {'tally': dict(tally), 'bad': bad, 'tries': tries}
    if k == 'stage':
        pop = load_population()
        if payload['i'] >= len(pop):
            return {'tally': {}, 'bad': []}
        x = pop[payload['i']]
        for s in range(1, 7):
            res = isolated(x['sizes'], x['edges'], 3, s=s)
            key = 'skip ' + res['skip'] if 'skip' in res else ('equal' if res['equal'] else 'differ')
            tally[key] += 1
            if key == 'differ':
                bad.append([x['sizes'], x['edges'], s])
        return {'tally': dict(tally), 'bad': bad}
    raise ValueError(k)


def sample_any(n, rng, want):
    """Random starts within seven places with no class filter: a random tree plus Poisson(1, 2 or 3) extra lines, each knot dead
    with probability 0.2 (given extra shared distinctions to reach three places), live knots at shared plus their pairwise demand
    (minus 0 or 1) plus a spare at 0.3; kept when connected, within 3 to 7 places, and not stalling."""
    out, tries, seen = [], 0, set()
    while len(out) < want and tries < want * 400:
        tries += 1
        edges = EX.tree(n, rng)
        have = set(edges)
        non = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in have]
        r = min(EX.poisson(rng.choice((1.0, 2.0, 3.0)), rng), len(non))
        e = edges + rng.sample(non, r)
        dead = [k for k in range(n) if rng.random() < 0.2]
        for w in dead:
            for _ in range(6):
                shw = sum(1 for a, b in e if w in (a, b))
                if shw >= 3:
                    break
                nbw = sorted({b if a == w else a for a, b in e if w in (a, b)})
                e.append(tuple(sorted((w, rng.choice(nbw)))))
        sh = Counter()
        nb = {k: set() for k in range(n)}
        for a, b in e:
            sh[a] += 1
            sh[b] += 1
            nb[a].add(b)
            nb[b].add(a)
        live = set(range(n)) - set(dead)
        dp = Counter()
        for w in range(n):
            B = nb[w] & live
            if len(B) >= 2:
                for k in B:
                    dp[k] += len(B) - 1
        sizes = [sh[k] if k in dead else sh[k] + max(1, dp[k] - rng.choice((0, 0, 1))) + (1 if rng.random() < 0.3 else 0) for k in range(n)]
        if max(sizes) > 7 or min(sizes) < 3:
            continue
        e = sorted(e)
        key = (tuple(sizes), tuple(e))
        if key in seen or not J.connected(n, e) or DC.classify(sizes, e) == 'stall':
            continue
        seen.add(key)
        out.append((sizes, e))
    return out, tries


def load_population():
    R = load_results(str(ROOT / 'runs/explosive'))
    out = []
    for cid, r in sorted(R.items()):
        if cid.startswith('cap-7'):
            for x in r['result']['starts']:
                if x['measured'] == 'explosive':
                    out.append({'sizes': x['sizes'], 'edges': [tuple(y) for y in x['edges']], 'n': x['n']})
    out.sort(key=lambda x: (x['n'], sum(x['sizes']), x['sizes'], x['edges']))
    return out
