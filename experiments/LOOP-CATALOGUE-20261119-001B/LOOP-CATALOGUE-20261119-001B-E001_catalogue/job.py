"""Shared-runner job for LOOP-CATALOGUE-20261119-001B-E001: which loops of knots feed themselves, and the catalogue.

Part E: fresh random arrangements (sampler.py; seeds 10^7 n + k) of 6 to 14 knots, 100,000 per size to 12 and 50,000 at 13 and
14, in shards of 10,000.  Every start is read by the eddy rule (eddy.py).  Grown (36 rounds, 30,000 junctions or 60 s) are every
rule-eddy, every start with a loop (outside the rule's scope too: eddy.loop_rank_any), and one in 400 of the other non-stalled
starts.  Each shard also counts, over its
growers, the live share and the chordless cycles of the knot graph (all, all-live, all-live of length 5 or at least 7).
Part S: SCALE-SHARE's 64 Metropolis chains regenerated (scale.chain, its seeds), read and grown as part E (one in 100 controls).
Part C: every catalogue entry (catalogue.json: the minimal eddies to eight knots), grown under parity to 40 rounds, 30,000
junctions or 300 s and compared with the cluster rule's series, and under not-all-equal (naelib) to 14 rounds.
Part I: interfaces.  For each entry and each knot k (one per orbit): a spare at k; a lone knot hung at k; a lone knot with one
spare hung at k; a hanging path of two lone knots at k; the ring of five with one spare joined to k by a shared distinction.  Each
is read by the rule (equation.py) and grown to 30 rounds, 30,000 junctions or 120 s.
Part R: rings of 8 to 13 knots with one spare, and bare, read and grown to 50 rounds or 30,000 junctions; and the ring of eight
with a spare at knot 0 and a lone knot hung at knot 0 or knot 1 (the advisor's check that the two loops of an even ring take their
entries separately).  Every one-loop start also records its round-weight W (loopweight.py) and the root of W = 1.
Part U: every start the rule could not decide in the eight-knot search (undecided.json), grown and classified."""
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
import sampler as SM  # noqa: E402
import catalogue as CT  # noqa: E402
import equation as Q  # noqa: E402
import loopweight as LW  # noqa: E402
J = E.J
ROOT = E.ROOT


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def scale():
    return _load('ss_scale', ROOT / 'experiments/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/scale.py')


def nae():
    return _load('ng_naelib', ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py')


def read_and_grow(sz, e, control, rounds=36, maxj=30000, tmax=60.0):
    """The rule's verdict; growth for every rule-eddy, every start with a loop (outside the rule's scope too, by
    eddy.loop_rank_any) and the controls.  Returns (record, the blocks for the statistics) or (record, None) on a stall."""
    v = E.eddy(sz, e)
    if v == 'stall':
        return {'rule': 'stall'}, None
    A = E.analyse_all(sz, e)
    if v == 'out':
        rank = E.loop_rank_any(sz, e) or 0
        v = 'out-loop' if rank else 'out'
        rec = {'rule': v, 'block_rank': rank, 'meet': False, 'exact': False}
    else:
        P = E.pieces(A)
        rank = sum(p[2] for p in P)
        rec = {'rule': str(v), 'block_rank': rank, 'meet': any(p[4] and p[2] >= 1 for p in P), 'exact': E.exact(A)}
    if v is True or rank >= 1 or control:
        cls, c = E.growth_class(sz, e, rounds=rounds, maxj=maxj, tmax=tmax)
        pred = E.Cl.series(sz, e, len(c))
        rec.update(growth=cls, counts=c, equal_to_rule=isinstance(pred, list) and pred == c, sizes=sz, edges=[list(x) for x in e])
    return rec, A


def cycle_stats(n, e, A):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(set(e))
    live = set(A['live'])
    allc = alive = along = 0
    for c in nx.chordless_cycles(G):
        allc += 1
        if set(c) <= live:
            alive += 1
            along += len(c) == 5 or len(c) >= 7
    return len(live) / n, allc, alive, along


def part_e(n, seeds, every=400):
    out, stats = [], {'growers': 0, 'live_share': 0.0, 'cycles': 0, 'all_live': 0, 'all_live_long': 0, 'with_block_cycle': 0}
    for k, s in enumerate(seeds):
        sz, e = SM.sample(n, s)
        rec, A = read_and_grow(sz, e, control=(k % every == 0))
        if A is None:
            continue
        stats['growers'] += 1
        ls, a, b, c = cycle_stats(n, e, A)
        stats['live_share'] += ls
        stats['cycles'] += a
        stats['all_live'] += b
        stats['all_live_long'] += c
        stats['with_block_cycle'] += rec['block_rank'] >= 1
        if 'growth' in rec:
            out.append(dict(rec, seed=s))
    return {'grown': out, 'stats': stats}


def part_s(n, seed):
    S = scale()
    samp = S.chain(n, 1000, seed, dense=seed >= 4)
    out, stats = [], {'growers': 0, 'live_share': 0.0, 'cycles': 0, 'all_live': 0, 'all_live_long': 0, 'with_block_cycle': 0}
    for k, (sizes, M) in enumerate(samp):
        sz, e = S.edges_of(sizes, M)
        rec, A = read_and_grow(sz, e, control=(k % 100 == 0))
        if A is None:
            continue
        stats['growers'] += 1
        ls, a, b, c = cycle_stats(n, e, A)
        stats['live_share'] += ls
        stats['cycles'] += a
        stats['all_live'] += b
        stats['all_live_long'] += c
        stats['with_block_cycle'] += rec['block_rank'] >= 1
        if 'growth' in rec:
            out.append(dict(rec, sample=k))
    return {'grown': out, 'stats': stats}


def part_c(entry):
    sz, e = entry['sizes'], [tuple(x) for x in entry['edges']]
    t0 = time.time()
    cls, c = E.growth_class(sz, e, rounds=40, maxj=30000, tmax=300.0)
    pred = E.Cl.series(sz, e, len(c))
    N = nae()
    P, out = N.grow(sz, e, 'nae', rounds=12, maxj=20000)
    cn = P.counts_by_round()
    eq = Q.equation(sz, e)
    A = E.Cl.analyse(sz, e)
    return {'entry': entry, 'parity': c, 'growth_class': cls, 'equal_to_rule': pred == c, 'nae': cn, 'nae_outcome': out,
            'nae_equal': cn == c[:len(cn)], 'equation': eq, 'W': weight_of(sz, e), 'exact': E.exact(A),
            'verdict': str(E.eddy(sz, e)), 'seconds': round(time.time() - t0, 1)}


def weight_of(sz, e):
    W = LW.round_weight(sz, e, 30)
    if W is None:
        return None
    r = LW.root(W)
    return {'W': W[:16], 'W1': sum(W), 'rate': None if r is None else round(1 / r, 6)}


def attach(entry, k, kind):
    """The entry's graph with an attachment at knot k; returns (n, edges, spares)."""
    n, edges, sp = entry['n'], [tuple(x) for x in entry['edges']], list(entry['spares'])
    if kind == 'spare':
        sp[k] += 1
        return n, edges, sp
    if kind in ('lone', 'lone+spare'):
        return n + 1, edges + [(k, n)], sp + [1 if kind == 'lone+spare' else 0]
    if kind == 'path2':
        return n + 2, edges + [(k, n), (n, n + 1)], sp + [0, 0]
    if kind == 'ring5':
        ring = [(n + i, n + (i + 1) % 5) for i in range(5)]
        return n + 5, edges + ring + [(k, n)], sp + [0, 1, 0, 0, 0]
    raise ValueError(kind)


def orbits(entry):
    """One knot per orbit of the entry's renamings (knots with equal canonical attachment of a spare)."""
    seen, reps = set(), []
    for k in range(entry['n']):
        n, e, sp = attach(entry, k, 'spare')
        key = CT.canon(*CT.start(n, e, sp))
        if key not in seen:
            seen.add(key)
            reps.append(k)
    return reps


def part_i(entry):
    rows = []
    base = Q.equation(entry['sizes'], [tuple(x) for x in entry['edges']])
    for k in orbits(entry):
        for kind in ('spare', 'lone', 'lone+spare', 'path2', 'ring5'):
            n, e, sp = attach(entry, k, kind)
            sz, ee = CT.start(n, e, sp)
            eq = Q.equation(sz, ee)
            g = J.grow(sz, ee, rounds=30, maxj=30000, tmax=120.0)
            c = g['counts']
            pred = E.Cl.series(sz, ee, len(c))
            rows.append({'knot': k, 'kind': kind, 'sizes': sz, 'edges': [list(x) for x in ee], 'equation': eq, 'counts': c[:30],
                         'outcome': g['outcome'], 'equal_to_rule': pred == c, 'rule': str(E.eddy(sz, ee)),
                         'exact': E.exact(E.Cl.analyse(sz, ee)), 'W': weight_of(sz, ee), 'on_loop': k in loop_knots(entry)})
    return {'entry': entry, 'base': base, 'W': weight_of(entry['sizes'], [tuple(x) for x in entry['edges']]), 'interfaces': rows}


def loop_knots(entry):
    A = E.Cl.analyse(entry['sizes'], [tuple(x) for x in entry['edges']])
    out = set()
    for ks, bs, r, bare, meet in E.pieces(A):
        if r >= 1:
            for i in bs:
                out |= set(A['blocks'][i])
    return out


def part_r(n, spare):
    edges = [(i, (i + 1) % n) for i in range(n)]
    edges = [tuple(sorted(x)) for x in edges]
    sp = [1 if (spare and i == 0) else 0 for i in range(n)]
    sz, e = CT.start(n, edges, sp)
    cls, c = E.growth_class(sz, e, rounds=50, maxj=30000, tmax=300.0)
    pred = E.Cl.series(sz, e, len(c))
    return {'n': n, 'spare': spare, 'sizes': sz, 'counts': c, 'growth_class': cls, 'equal_to_rule': pred == c,
            'rule': str(E.eddy(sz, e)), 'equation': Q.equation(sz, e), 'W': weight_of(sz, e)}


def part_r8(where):
    """The advisor's two-loop placement check on the ring of eight: a spare at knot 0, and a lone knot hung at knot 0 or 1."""
    n = 8
    edges = [tuple(sorted((i, (i + 1) % n))) for i in range(n)] + [(where, 8)]
    sp = [1] + [0] * 8
    sz, e = CT.start(9, edges, sp)
    cls, c = E.growth_class(sz, e, rounds=50, maxj=30000, tmax=300.0)
    pred = E.Cl.series(sz, e, len(c))
    return {'hang_at': where, 'sizes': sz, 'counts': c, 'growth_class': cls, 'equal_to_rule': pred == c,
            'rule': str(E.eddy(sz, e)), 'equation': Q.equation(sz, e)}


def part_u(starts):
    """The starts the rule cannot decide (a loop holding a known break, or outside its scope with a loop), met in the eight-knot
    search: each grown to 30 rounds, 5,000 junctions or 60 s and classified."""
    out = []
    for st in starts:
        sz, e = st['sizes'], [tuple(x) for x in st['edges']]
        A = E.analyse_all(sz, e)
        P = E.pieces(A)
        cls, c = E.growth_class(sz, e, rounds=30, maxj=5000, tmax=60.0)
        out.append(dict(st, growth=cls, counts=c[:30], meet=any(p[4] and p[2] >= 1 for p in P),
                        broken=bool(E.broken_blocks(A)), scope=A['scope']))
    return {'starts': out}


def cases():
    for n in range(6, 15):
        total = 100000 if n <= 12 else 50000
        for s in range(0, total, 10000):
            yield f'E-n{n:02d}-{s // 10000:02d}', {'part': 'E', 'n': n, 'seeds': [10 ** 7 * n + s + k for k in range(10000)]}
    for n in (5, 6, 7, 8, 10, 12, 16, 20):
        for seed in range(8):
            yield f'S-n{n:02d}-c{seed}', {'part': 'S', 'n': n, 'seed': seed}
    cat = json.loads((HERE / 'catalogue.json').read_text())
    for i, entry in enumerate(cat):
        yield f'C-{i:02d}', {'part': 'C', 'entry': entry}
        yield f'I-{i:02d}', {'part': 'I', 'entry': entry}
    for n in range(8, 14):
        for spare in (0, 1):
            yield f'R-n{n:02d}-s{spare}', {'part': 'R', 'n': n, 'spare': spare}
    for where in (0, 1):
        yield f'R8-hang{where}', {'part': 'R8', 'where': where}
    und = json.loads((HERE / 'undecided.json').read_text())
    for s in range(0, len(und), 40):
        yield f'U-{s // 40:03d}', {'part': 'U', 'starts': und[s:s + 40]}


def run(case_id, payload):
    p = payload['part']
    if p == 'E':
        return part_e(payload['n'], payload['seeds'])
    if p == 'S':
        return part_s(payload['n'], payload['seed'])
    if p == 'C':
        return part_c(payload['entry'])
    if p == 'I':
        return part_i(payload['entry'])
    if p == 'R8':
        return part_r8(payload['where'])
    if p == 'U':
        return part_u(payload['starts'])
    return part_r(payload['n'], payload['spare'])
