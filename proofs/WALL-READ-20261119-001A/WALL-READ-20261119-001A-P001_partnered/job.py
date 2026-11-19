"""Shared-runner job for WALL-READ-20261119-001A-P001's machine check (frozen with the proof).

Each case runs in a forked child limited by RLIMIT_AS and a wall clock.
- part-n (n = 3, 4, 5): the partnered start of order n, grown by the program's engine (its hub realization) and by the roster
  engine; rounds 1..T with T = 3, 1, 1 (the next round needs 2^124 cliques for n = 4); M1.
- ctl-...: controls of M2 (open 2^(n-1) -/+ 1 for n = 3, 4; n = 2 for 10 rounds).
- lem-rand-n (n = 6..13): 125 random starts of n knots within seven places (REDUCE-BLOCKS' sampler sample_any, seed
  'wall-read-A-<case>'), every stage of rounds 0..5; M3 and M4.
- lem-expl-i (i = 0..15): EXPLOSIVE's 16 explosive starts, the same; M3 and M4."""
import importlib.util
import itertools
import random
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import rosterlib as RL  # noqa: E402


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


RB = _load('wr_rbjob', 'proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/job.py')
HB = RB.HB


def partnered(n, open_count=None):
    pts = list(range(2 * n))
    blocks = [frozenset((u, v)) for u, v in itertools.combinations(pts, 2) if u // 2 != v // 2]
    return [open_count if open_count is not None else 2 ** (n - 1)] * (2 * n), blocks


def hub_start(opn, blocks):
    """A start whose live knots are 0..L-1 with these open counts and one dead knot per block (then H(X) of REDUCE-BLOCKS)."""
    L = len(opn)
    e = []
    for h, B in enumerate(blocks):
        for k in sorted(B):
            e.append((k, L + h))
    sh = Counter()
    for a, b in e:
        sh[a] += 1
        sh[b] += 1
    sizes = [sh[k] + opn[k] for k in range(L)] + [sh[L + h] for h in range(len(blocks))]
    return HB.hub_realization(sizes, e)


def predicted(n, T):
    """Theorem 1: per-round [((parents, open), count)] for rounds 1..T, the count of round T + 1, and its parent count m_T."""
    N = [2 * n, 2 ** n]
    while len(N) < T + 2:
        N.append(2 ** (N[-1] // 2) - N[-2])
    out = []
    for t in range(1, T + 1):
        p = n if t == 1 else N[t - 1] // 2
        out.append([((p, 2 ** (N[t] // 2 - 1) - p), N[t])])
    return out, N[T + 1], N[T] // 2


def child(conn, fn, args):
    import resource
    lim = args[-1]
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    try:
        fn(conn, *args[:-1])
    except MemoryError:
        conn.send({'end': 'memory'})


def isolated(fn, args, seconds, mem):
    """Run fn(conn, *args) in a forked child; collect every message until it ends, is killed by memory, or runs out of time."""
    import multiprocessing as mp
    ctx = mp.get_context('fork')
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=child, args=(b, fn, tuple(args) + (mem,)))
    pr.start()
    b.close()
    msgs = []
    t0 = time.time()
    end = 'time'
    while time.time() - t0 < seconds:
        if a.poll(1.0):
            try:
                m = a.recv()
            except EOFError:
                end = 'memory' if pr.exitcode not in (0, None) or not msgs or msgs[-1] != 'done' else 'done'
                break
            if m == 'done':
                end = 'done'
                break
            msgs.append(m)
        elif not pr.is_alive():
            end = 'memory'
            break
    pr.kill()
    pr.join(5)
    return msgs, end


# -- M1, M2 -------------------------------------------------------------------------------------------------------------------

def _engine_keys(conn, sizes, edges, T):
    conn.send({'engine': HB.grow_keys(sizes, edges, T)})
    conn.send('done')


def _engine_open_count(conn, sizes, edges, T):
    """Program engine: keys of rounds 1..T and the next count as sum(open of round T) / parents of round T + 1."""
    J = HB.J
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    keys = []
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None:
            keys.append('stall')
            break
        if r['new'] == 0:
            keys.append('closed')
            break
        keys.append(sorted(Counter((P.parents[j], P.fresh[j]) for j, ro in enumerate(P.round_of) if ro == t).items()))
    conn.send({'engine': [k if isinstance(k, str) else [[list(a), c] for a, c in k] for k in keys],
               'open_sum': sum(P.fresh[j] for j, ro in enumerate(P.round_of) if ro == T)})
    conn.send('done')


def _roster_keys(conn, opn, blocks, T):
    recs = list(RL.grow(opn, blocks, T))
    keys, osum, offs = [], None, []
    for r in recs:
        if 'end' in r:
            keys.append(r['end'])
        elif 'keys' in r:
            keys.append([[list(a), c] for a, c in r['keys']])
            osum = r['open_sum']
        else:
            offs.append(r['offshoots'])
    conn.send({'roster': keys, 'open_sum': osum, 'offshoots': offs})
    conn.send('done')


def run_part(n):
    T = {3: 3, 4: 1, 5: 1}[n]
    opn, blocks = partnered(n)
    sizes, edges = hub_start(opn, blocks)
    want, nxt, m_T = predicted(n, T)
    me, ee = isolated(_engine_open_count, (sizes, edges, T), 900, 7 << 30)
    mr, er = isolated(_roster_keys, (opn, blocks, T), 900, 7 << 30)
    eng = me[0] if me else {}
    ros = mr[0] if mr else {}
    norm = lambda ks: [k if isinstance(k, str) else [(tuple(a), c) for a, c in k] for k in ks]
    return {'n': n, 'T': T, 'predicted_keys': [[[list(a), c] for a, c in r] for r in want], 'predicted_next': nxt,
            'next_parents': m_T, 'engine': eng, 'engine_end': ee, 'roster': ros, 'roster_end': er,
            'hub_knots': len(sizes), 'max_places': max(sizes),
            'engine_ok': bool(eng) and norm(eng.get('engine', [])) == want,
            'roster_ok': bool(ros) and norm(ros.get('roster', [])) == want,
            'engine_next_ok': bool(eng) and eng.get('open_sum') == nxt * m_T,
            'roster_next_ok': bool(ros) and ros.get('open_sum') == nxt * m_T}


def run_ctl(kind, n):
    if kind == 'ring':
        opn, blocks = partnered(2)
        mr, er = isolated(_roster_keys, (opn, blocks, 10), 120, 3 << 30)
        sizes, edges = hub_start(opn, blocks)
        me, ee = isolated(_engine_keys, (sizes, edges, 10), 120, 3 << 30)
        ros = mr[0]['roster'] if mr else None
        eng = me[0]['engine'] if me else None
        counts = [sum(c for _, c in k) for k in ros] if ros else None
        return {'roster_counts': counts, 'engine': eng, 'roster': ros,
                'ok': counts == [4] * 10 and [[[list(a), c] for a, c in k] for k in eng] == ros}
    o = 2 ** (n - 1) + (-1 if kind == 'low' else 1)
    opn, blocks = partnered(n, o)
    sizes, edges = hub_start(opn, blocks)
    me, ee = isolated(_engine_keys, (sizes, edges, 1), 300, 4 << 30)
    mr, er = isolated(_roster_keys, (opn, blocks, 1), 300, 4 << 30)
    eng = me[0]['engine'] if me else None
    ros = mr[0] if mr else None
    if kind == 'low':
        ok = eng == ['stall'] and ros['roster'] == ['stall']
    else:
        ok = ros['offshoots'] == [2 * n] and eng and eng != ['stall'] and \
            sum(c for (p, f), c in eng[0] if p == 1) == 2 * n
    return {'engine': eng, 'roster': ros, 'ok': bool(ok)}


# -- M3, M4 -------------------------------------------------------------------------------------------------------------------

def _lemmas(conn, opn, blocks, T, seed):
    rng = random.Random(seed)
    pend = {}

    def on_stage(t, pts, B, par):
        if par is not None and (t - 1) in pend:
            st = pend.pop(t - 1)
            grp = [j for j in pts if len(par[j]) >= 2]       # the groups of round t; offshoots have one parent
            res = {'t': t - 1, 'points': st['points'], 'blocks': st['blocks'], 'groups': len(grp)}
            # Lemma 2: a maximal clique held by no block is a group unless it is a lone point (no candidate); a partnered set of
            # k >= 2 extends to cliques of two or more points, so it needs no such term
            res['bound_k'] = 2 ** st['k_any'] - st['blocks'] - (st['lone'] if st['k_any'] < 2 else 0)
            res['k_any'] = st['k_any']
            res['bound_w'] = st['mc_w'] - st['blocks'] - st['lone']
            res['lemma2_ok'] = res['bound_k'] <= res['groups'] and res['bound_w'] <= res['groups']
            if st['iso'] is not None and 2 <= st['iso'][0] <= 10:
                k, pairs = st['iso']
                byx = {}
                for j in grp:
                    for x in par[j]:
                        byx.setdefault(x, set()).add(j)
                Q = {}
                bad = False
                held = 0
                for bitsel in range(2 ** k):
                    T_ = frozenset(pairs[i][(bitsel >> i) & 1] for i in range(k))
                    c = set.intersection(*[byx.get(x, set()) for x in T_])
                    if c:
                        Q[bitsel] = min(c)
                        if frozenset(par[Q[bitsel]]) & frozenset(x for p in pairs for x in p) != T_:
                            bad = True
                    else:
                        held += 1
                        if not any(T_ <= Bb for Bb in st['B']):
                            bad = True
                full = (1 << k) - 1
                good_pairs = [s for s in Q if s < (s ^ full) and (s ^ full) in Q]
                for s in good_pairs:
                    if par[Q[s]] & par[Q[s ^ full]]:
                        bad = True
                for s1, s2 in itertools.combinations([s for s in Q], 2):
                    if s2 != (s1 ^ full) and not (par[Q[s1]] & par[Q[s2]]):
                        bad = True
                res['iso_k'] = k
                res['iso_new_k'] = len(good_pairs)
                res['lemma3_ok'] = (not bad) and len(good_pairs) >= 2 ** (k - 1) - st['blocks']
            conn.send(res)
        if t > T:
            return
        bits = RL.Bits(pts, B)
        ka, ki = RL.best_sets(bits, restarts=3)
        Wn = min(12, len(pts))
        Wp = rng.sample(sorted(pts), Wn) if len(pts) > Wn else list(pts)
        G = RL.candidate_graph(Wp, B)
        mc = sum(1 for _ in nx.find_cliques(G)) if Wp else 0
        lone = sum(1 for i in range(bits.N) if not bits.rows[i].any())
        pend[t] = {'points': len(pts), 'blocks': len(B), 'k_any': ka[0], 'iso': (ki[0], ki[4]) if ki else None,
                   'mc_w': mc, 'B': B, 'lone': lone}

    for r in RL.grow(opn, blocks, T + 1, on_stage=on_stage):
        if 'end' in r:
            conn.send({'end_growth': r['end'], 't': r['t']})
            break
    conn.send('done')


def run_lemmas(starts, tag):
    tally = Counter()
    bad = []
    k_seen = Counter()
    for i, (sizes, e) in enumerate(starts):
        opn, blocks = RL.roster_of(sizes, e)
        if not opn:
            tally['no live knot'] += 1
            continue
        msgs, end = isolated(_lemmas, (opn, blocks, 5, f'wall-read-A-{tag}-{i}'), 120, 3 << 30)
        tally['end ' + end] += 1
        for m in msgs:
            if 'lemma2_ok' not in m:
                continue
            tally['stages'] += 1
            tally['lemma2 ' + ('ok' if m['lemma2_ok'] else 'FAIL')] += 1
            k_seen[m['k_any']] += 1
            if 'lemma3_ok' in m:
                tally['lemma3 ' + ('ok' if m['lemma3_ok'] else 'FAIL')] += 1
                if m['iso_new_k'] > 0 and m['iso_k'] >= 2:
                    tally['lemma3 nontrivial'] += 1
            if (not m['lemma2_ok'] or m.get('lemma3_ok') is False) and len(bad) < 10:
                bad.append([sizes, e, m])
    return {'tally': dict(tally), 'k_any': dict(k_seen), 'bad': bad}


def cases():
    for n in (3, 4, 5):
        yield f'part-{n}', {'kind': 'part', 'n': n}
    for n in (3, 4):
        yield f'ctl-low-{n}', {'kind': 'ctl', 'c': 'low', 'n': n}
        yield f'ctl-high-{n}', {'kind': 'ctl', 'c': 'high', 'n': n}
    yield 'ctl-ring', {'kind': 'ctl', 'c': 'ring', 'n': 2}
    for n in range(6, 14):
        yield f'lem-rand-{n:02d}', {'kind': 'rand', 'n': n}
    for i in range(16):
        yield f'lem-expl-{i:02d}', {'kind': 'expl', 'i': i}


def run(case_id, payload):
    k = payload['kind']
    if k == 'part':
        return run_part(payload['n'])
    if k == 'ctl':
        return run_ctl(payload['c'], payload['n'])
    if k == 'rand':
        rng = random.Random(f'wall-read-A-{case_id}')
        ss, tries = RB.sample_any(payload['n'], rng, 125)
        out = run_lemmas(ss, case_id)
        out['tries'] = tries
        return out
    if k == 'expl':
        pop = RB.load_population()
        x = pop[payload['i']]
        return run_lemmas([(x['sizes'], x['edges'])], case_id)
    raise ValueError(k)
