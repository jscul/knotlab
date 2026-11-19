"""Shared-runner job for EXPLOSIVE-20261119-001B-E001 (frozen with the pre-registration).

Cases:
- cap-C-n: random starts of n knots within C places (C = 5: n = 6..12; C = 7: n = 6..10), POP per case, seeded by the case id.
  A start is kept when it does not stall, satisfies (S4), and holds at least one cycle of three blocks.
- cycle-n: the stratum the advisor asked for: random starts of n knots within five places (n = 6..12) kept only when some piece's
  filled map keeps a cycle (b1 >= 1), up to POP_B per case.
- census: every touch-census arrangement that does not stall, satisfies (S4), and holds a cycle of three blocks (471; explored
  before the freeze, disclosed).
- ref: the BREAK-EDDIES referee's shapes (population_ref.json), the named explosive references, grown to MAXJ_REF junctions
  (they calibrate the class rule; disclosed).
Each start: the filled map's structure and reading, then the engine to round T or MAXJ junctions with its largest group per
round, in a child process limited to 2.5 GB and 30 s (outcome 'resource' when stopped; its rounds so far are kept)."""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import filllib as F  # noqa: E402

sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

T, MAXJ, MAXJ_REF, POP, POP7, POP_B = 20, 6000, 40000, 300, 200, 100
DC, J = F.DC, F.J


def cases():
    for n in range(6, 13):
        yield f'cap-5-{n:02d}', {'kind': 'cap', 'cap': 5, 'n': n}
    for n in range(6, 11):
        yield f'cap-7-{n:02d}', {'kind': 'cap', 'cap': 7, 'n': n}
    for n in range(6, 13):
        yield f'cycle-{n:02d}', {'kind': 'cycle', 'n': n}
    yield 'census', {'kind': 'census'}
    yield 'ref', {'kind': 'ref'}


def tree(n, rng):
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


def poisson(lam, rng):
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def sample(n, cap, rng, want, need_cycle=False):
    out, tries, seen = [], 0, set()
    while len(out) < want and tries < want * 3000:
        tries += 1
        edges = tree(n, rng)
        have = set(edges)
        non = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in have]
        r = min(poisson(rng.choice((1.0, 2.0, 3.0)), rng), len(non))
        edges = edges + rng.sample(non, r)
        dead = [k for k in range(n) if rng.random() < 0.2]
        sh = Counter()
        nb = defaultdict(set)
        e = list(edges)
        ok = True
        for w in dead:
            for _ in range(6):
                sh = Counter()
                for a, b in e:
                    sh[a] += 1
                    sh[b] += 1
                if sh[w] >= 3:
                    break
                nbw = sorted({b if a == w else a for a, b in e if w in (a, b)})
                e.append(tuple(sorted((w, rng.choice(nbw)))))
        sh = Counter()
        for a, b in e:
            sh[a] += 1
            sh[b] += 1
            nb[a].add(b)
            nb[b].add(a)
        live = set(range(n)) - set(dead)
        blocks = [nb[w] & live for w in range(n) if len(nb[w] & live) >= 2]
        dpair = Counter()
        for B in blocks:
            for k in B:
                dpair[k] += len(B) - 1
        sizes = [sh[k] if k in dead else sh[k] + max(1, dpair[k] - rng.choice((0, 0, 1))) + (1 if rng.random() < 0.3 else 0) for k in range(n)]
        if max(sizes) > cap or min(sizes) < 3:
            continue
        e = sorted(e)
        key = (tuple(sizes), tuple(e))
        if key in seen or not J.connected(n, e):
            continue
        S = F.structure(sizes, e)
        if S['stall'] or not S['s4'] or S['tri'] == 0:
            continue
        if need_cycle and not any(p['b1'] > 0 for p in S['pieces']):
            continue
        seen.add(key)
        out.append((sizes, e))
    return out, tries


CHILD_MEM, CHILD_SECONDS = 2_500_000_000, 30


def _child(conn, sizes, e, maxj):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_MEM, CHILD_MEM))
    P = J.S.from_junctions(J.stars_from(sizes, e))
    P.linalg = False
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None:
            conn.send(('stall', None, None))
            return
        if r['new'] == 0:
            conn.send(('closed', 0, 0))
            return
        born = [j for j, ro in enumerate(P.round_of) if ro == t]
        conn.send(('round', len(born), max(P.parents[j] for j in born)))
        if len(P.bits_of) > maxj:
            conn.send(('cap', None, None))
            return
    conn.send(('alive', None, None))


def grow_isolated(sizes, e, maxj):
    """The engine in a child process with a memory and time limit; rounds stream back, so a child that runs out keeps its
    rounds. Outcome 'resource' when it is stopped."""
    import multiprocessing as mp
    import time
    ctx = mp.get_context('fork')
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=_child, args=(b, sizes, e, maxj))
    pr.start()
    b.close()
    counts, groups, outcome = [len(sizes)], [1], 'resource'
    t0 = time.time()
    while True:
        if a.poll(1.0):
            try:
                kind, c, g = a.recv()
            except EOFError:
                break
            if kind == 'round':
                counts.append(c)
                groups.append(g)
                continue
            if kind == 'closed':
                counts.append(0)
                groups.append(0)
            outcome = kind
            break
        if not pr.is_alive() and not a.poll(0):
            break
        if time.time() - t0 > CHILD_SECONDS:
            pr.kill()
            outcome = 'resource'
            break
    pr.join(5)
    if pr.is_alive():
        pr.kill()
    return {'outcome': outcome, 'counts': counts, 'groups': groups}


def read(sizes, e, tag, maxj=None):
    S = F.structure(sizes, e)
    g = grow_isolated(sizes, e, maxj or MAXJ)
    return {'tag': tag, 'n': len(sizes), 'max_places': max(sizes), 'dead': sum(o == 0 for o in S['open']), 'tri': S['tri'],
            'b1': [p['b1'] for p in S['pieces']], 'b2': [p['b2'] for p in S['pieces']], 'rank': [p['rank'] for p in S['pieces']],
            'reading': F.filled_reading(S),
            'overlap_point': S['overlap_point'], 'overlap_block': S['overlap_block'],
            'measured': F.measured(g), 'outcome': g['outcome'], 'counts': g['counts'],
            'groups': g['groups'], 'sizes': sizes, 'edges': e}


def run(case_id, payload):
    if payload['kind'] == 'cap':
        rng = random.Random(f'explosive-{case_id}')
        ss, tries = sample(payload['n'], payload['cap'], rng, POP if payload['cap'] == 5 else POP7)
        return {'starts': [read(s, e, f'cap{payload["cap"]}') for s, e in ss], 'tries': tries}
    if payload['kind'] == 'cycle':
        rng = random.Random(f'explosive-{case_id}')
        ss, tries = sample(payload['n'], 5, rng, POP_B, need_cycle=True)
        return {'starts': [read(s, e, 'cycle5') for s, e in ss], 'tries': tries}
    if payload['kind'] == 'census':
        R = load_results(str(ROOT / 'runs/touch-census'))
        res = []
        for r in R.values():
            if r.get('status') != 'ok':
                continue
            for a in r['result']['arrangements']:
                key = (tuple(a['key'][0]), tuple(a['key'][1]))
                sizes, e = DC.edges_of(key)
                S = F.structure(sizes, e)
                if S['stall'] or not S['s4'] or S['tri'] == 0:
                    continue
                res.append(read(sizes, e, 'census'))
        return {'starts': res}
    if payload['kind'] == 'ref':
        P = json.loads((ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population_ref.json').read_text())
        res = []
        for x in P:
            sizes, e = x['sizes'], [tuple(y) for y in x['edges']]
            r = read(sizes, e, 'ref ' + x['shape'], MAXJ_REF)
            res.append(r)
        return {'starts': res}
    raise ValueError(payload)
