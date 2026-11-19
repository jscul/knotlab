"""Shared-runner job for WALL-READ-20261119-001B-E001 (frozen with research/WALL-READ-20261119-001/preregistration.md).

The roster engine and the partnered-set search are WALL-READ-20261119-001A-P001's rosterlib.py (frozen with that proof). Every case
runs in a forked child limited by RLIMIT_AS and a wall clock.
- eq-census-c (c = 0..15): every touch-census arrangement, chunk c of 16: the program engine's per-round (parents, open) multisets
  (REDUCE-BLOCKS' hublib.grow_keys) against the roster engine's, rounds 1..6, with stall and close verdicts (B1).
- eq-rand-n (n = 6..13): 125 random starts of n knots within seven places (REDUCE-BLOCKS' sample_any, seed 'wall-read-B-<case>'),
  each in a child (3 GB, 120 s), rounds 1..6 (B1).
- eq-read-00, eq-read-04: MERGE-BURST's two read starts, start-00 to round 14 and start-04 to round 7, in a child (7 GB, 900 s) (B1).
- follow-XX (XX = 00..15): MERGE-BURST's 16 starts followed by the roster engine in a child (7 GB, 20 minutes). Each built stage
  reports its count, groups, offshoots, largest group, blocks and largest block, whether one block holds every live point, the best
  partnered sets (greedy, both modes, 3 seeded restarts), the lone points, and the sub-count bound; start-03's stage 7 is also
  listed by fastlib's Bron-Kerbosch, an enumeration separate from networkx's (B2-B6).

**The sub-count bound** at a stage (Lemma 2): W runs through seeded random samples (seed 'wall-read-B-<start>-<t>-<s>') of
s = 16, 24, 32, 40, 48, 56, 64, 80, 96, 128 points (s at most the stage's points); the maximal cliques of G[W] are counted by networkx
until the count finishes or 120 s pass for that W, and the procedure stops at the first W that does not finish, or when 240 s
have been spent at the stage (stages of fewer than 1,000 points stop after s = 32). The bound is the largest finished count minus
the blocks and the lone points."""
import importlib.util
import random
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PA = ROOT / 'proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered'
sys.path.insert(0, str(PA))
import rosterlib as RL  # noqa: E402

sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


AJ = _load('wr_ajob', 'proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/job.py')
RB, HB = AJ.RB, AJ.HB
FL = _load('wr_fastlib', 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py')
SIZES = (16, 24, 32, 40, 48, 56, 64, 80, 96, 128)


def norm_engine(ks):
    return [k if isinstance(k, str) else sorted((tuple(a), c) for a, c in k) for k in ks]


def compare(sizes, e, T):
    a = norm_engine(HB.grow_keys(sizes, e, T))
    opn, blocks = RL.roster_of(sizes, e)
    b = norm_engine(RL.keys_by_round(opn, blocks, T))
    if a and a[-1] == 'cap':
        m = len(a) - 1
        return {'equal': a[:m] == b[:m], 'rounds': m, 'cap': True}
    return {'equal': a == b, 'rounds': len(a)}


def _cmp_child(conn, sizes, e, T):
    conn.send(compare(sizes, e, T))
    conn.send('done')


def subcount(bits, B, lone, t, tag, budget):
    rng_tag = f'wall-read-B-{tag}-{t}'
    best, best_s, tried = 0, 0, []
    t_stage = time.time()
    for s in SIZES:
        if s > bits.N or time.time() - t_stage > budget or (bits.N < 1000 and s > 32):
            break
        rng = random.Random(f'{rng_tag}-{s}')
        W = rng.sample(range(bits.N), s)
        G = nx.Graph()
        G.add_nodes_from(W)
        for i in range(s):
            for j in range(i + 1, s):
                if bits.adjacent(W[i], W[j]):
                    G.add_edge(W[i], W[j])
        t0 = time.time()
        c, done = 0, True
        for _ in nx.find_cliques(G):
            c += 1
            if (c & 1023) == 0 and time.time() - t0 > 120:
                done = False
                break
        tried.append([s, c, done, round(time.time() - t0, 1)])
        if not done:
            break
        if c > best:
            best, best_s = c, s
    return {'mc': best, 'mc_s': best_s, 'tried': tried, 'bound_w': best - len(B) - lone}


def fastlib_groups(pts, B):
    cand = {v: set() for v in pts}
    of = {v: set() for v in pts}
    for i, b in enumerate(B):
        bl = sorted(b)
        for v in bl:
            of[v].add(i)
            cand[v].update(bl)
    for v in pts:
        cand[v].discard(v)
    big = []
    for C in FL.maximal_cliques(cand, [u for u in pts if cand[u]]):
        if len(C) >= 3 and not set.intersection(*[of[x] for x in C]):
            big.append(frozenset(C))
    covered = set()
    for S in big:
        sl = sorted(S)
        for i in range(len(sl)):
            for j in range(i + 1, len(sl)):
                covered.add((sl[i], sl[j]))
    pairs = sum(1 for u in pts for v in cand[u] if u < v and (u, v) not in covered)
    return {'groups': len(big) + pairs, 'largest': max((len(S) for S in big), default=2 if pairs else 0)}


def _follow(conn, opn, blocks, tag):
    def on_stage(t, pts, B, par):
        rec = {'kind': 'stage', 't': t, 'points': len(pts), 'blocks': len(B)}
        if len(pts) > 60000:
            rec['skipped'] = 'over 60,000 points'
            conn.send(rec)
            return
        t0 = time.time()
        bits = RL.Bits(pts, B)
        lone = sum(1 for i in range(bits.N) if not bits.rows[i].any())
        rec['lone'] = lone
        rec['edges'] = int(np.bitwise_count(bits.rows).sum()) // 2
        ka, ki = RL.best_sets(bits, restarts=3)
        rec['k_any'] = ka[0]
        rec['k_iso'] = ki[0] if ki else None
        rec['bound_k'] = 2 ** ka[0] - len(B) - (lone if ka[0] < 2 else 0)
        if ki and ki[0] >= 3:
            rec['bound_two'] = [2 ** ki[0] - len(B), 2 ** (ki[0] - 1) - len(B)]   # N(t+1) bound; order of stage t+1's set
        rec['partner_secs'] = round(time.time() - t0, 1)
        conn.send(dict(rec, partial=True))
        rec.update(subcount(bits, B, lone, t, tag, 240))
        if tag == 'start-03' and t == 7:
            rec['fastlib'] = fastlib_groups(pts, B)
        conn.send(rec)

    for r in RL.grow(opn, blocks, 40, on_stage=on_stage):
        conn.send(dict(r, kind='round'))
        if 'end' in r:
            break
    conn.send('done')


def cases():
    for c in range(16):
        yield f'eq-census-{c:02d}', {'kind': 'census', 'c': c}
    for n in range(6, 14):
        yield f'eq-rand-{n:02d}', {'kind': 'rand', 'n': n}
    for s, T in (('start-00', 14), ('start-04', 7)):
        yield f'eq-read-{s[-2:]}', {'kind': 'read', 'start': s, 'T': T}
    for i in range(16):
        yield f'follow-{i:02d}', {'kind': 'follow', 'start': f'start-{i:02d}'}


def mb_start(name):
    R = load_results(str(ROOT / 'runs/merge-burst'))
    st = R[name]['result']['start']
    return st['sizes'], [tuple(x) for x in st['edges']]


def run(case_id, payload):
    k = payload['kind']
    tally = Counter()
    bad = []
    if k == 'census':
        R = load_results(str(ROOT / 'runs/touch-census'))
        keys = [(tuple(a['key'][0]), tuple(a['key'][1])) for r in R.values() if r.get('status') == 'ok'
                for a in r['result']['arrangements']]
        for key in keys[payload['c']::16]:
            sizes, e = RB.DC.edges_of(key)
            res = compare(sizes, e, 6)
            tally['equal' if res['equal'] else 'differ'] += 1
            if not res['equal'] and len(bad) < 10:
                bad.append([sizes, e])
        return {'tally': dict(tally), 'bad': bad}
    if k == 'rand':
        rng = random.Random(f'wall-read-B-{case_id}')
        ss, tries = RB.sample_any(payload['n'], rng, 125)
        for sizes, e in ss:
            msgs, end = AJ.isolated(_cmp_child, (sizes, e, 6), 120, 3 << 30)
            key = ('equal' if msgs[0]['equal'] else 'differ') if msgs else 'skip ' + end
            tally[key] += 1
            if key == 'differ' and len(bad) < 10:
                bad.append([sizes, e])
        return {'tally': dict(tally), 'bad': bad, 'tries': tries}
    if k == 'read':
        sizes, e = mb_start(payload['start'])
        msgs, end = AJ.isolated(_cmp_child, (sizes, e, payload['T']), 900, 7 << 30)
        return {'result': msgs[0] if msgs else None, 'end': end}
    if k == 'follow':
        sizes, e = mb_start(payload['start'])
        opn, blocks = RL.roster_of(sizes, e)
        msgs, end = AJ.isolated(_follow, (opn, blocks, payload['start']), 1200, 7 << 30)
        return {'start': payload['start'], 'records': msgs, 'end': end}
    raise ValueError(k)
