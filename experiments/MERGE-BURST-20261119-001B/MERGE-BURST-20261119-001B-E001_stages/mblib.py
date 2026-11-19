"""MERGE-BURST-20261119-001B: explosive starts read from their stages.

**The stage identity** (BREAK-EDDIES, confirmed by its referee on 369 of 369 tests): the cheapest growth continued from its stage
after s rounds is the growth of that stage taken as a start. Its knots are the junctions, with their distinctions as places, two
junctions sharing a distinction touch, and the live junctions are those still holding a loose distinction.

**The reading.** The stage's map is reduced to its maximal blocks: a block inside another, or equal to it, adds no candidate pair
and no common neighbour that the larger block does not already supply (this is the study's hypothesis, checked by growth). Once
the reduced stage lies in the proved class, its future is the stage's own growth. DOUBLE-IDENT's identification holds
in the class with no bound on places, and DEAD-CAP's branch system counts it exactly; that count uses no bound on places either.
So the future is classified (closes, polynomial of a dimension, or exponential) and counted without building it.

**The child.** Each start grows in a forked child limited by RLIMIT_AS and a wall clock. After each round it reports the count, the
largest group, and the stage's class. When the stage lies in the class it reports the stage's reading and the branch system's
counts for the next H rounds, then grows up to V more rounds to check them."""
import importlib.util
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


DL = _load('mb_deadlib', 'proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/deadlib.py')
CC = _load('mb_cc', 'proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py')
DC, J = CC.DC, CC.J


def stage_of(P):
    owners = defaultdict(list)
    for j, bits in enumerate(P.bits_of):
        for b in bits:
            owners[b].append(j)
    e = sorted(tuple(sorted(o)) for o in owners.values() if len(o) == 2)
    return [len(b) for b in P.bits_of], e


def reduced(sz, e):
    """The stage's map with every block that lies inside another block dropped (equal blocks kept once): the maximal blocks.
    Returns (A, verdict), where A is deadlib's analysis rebuilt on the maximal blocks and verdict is 'in' when the reduced map
    has no stall, no two maximal blocks sharing two points, no cycle of three maximal blocks, and two or more loose distinctions;
    otherwise the failing condition."""
    import itertools
    import networkx as nx
    A = DL.analyse(sz, e)
    live = A['live']
    sets = {}
    for w, B in sorted(A['blocks'].items()):
        sets.setdefault(B, w)
    maximal = {B: w for B, w in sets.items() if not any(B < C for C in sets)}
    A['blocks'] = {w: B for B, w in maximal.items()}
    of = defaultdict(list)
    for w, B in A['blocks'].items():
        for k in B:
            of[k].append(w)
    A['of'] = dict(of)
    for B1, B2 in itertools.combinations(A['blocks'].values(), 2):
        if len(B1 & B2) >= 2:
            return A, 'two blocks share two points'
    ofs = {k: set(v) for k, v in of.items()}
    for x, y, z in itertools.combinations(sorted(ofs), 3):
        if ofs[x] & ofs[y] and ofs[y] & ofs[z] and ofs[z] & ofs[x] and not (ofs[x] & ofs[y] & ofs[z]):
            return A, 'cycle of three blocks'
    if any(A['d'][k] > A['open'][k] for k in live):
        return A, 'stall'
    if sum(A['open'][k] for k in live) < 2:
        return A, 'one loose or none'
    G = nx.Graph()
    G.add_nodes_from(('p', k) for k in live)
    for w, B in A['blocks'].items():
        for k in B:
            G.add_edge(('b', w), ('p', k))
    pieces = []
    for comp in nx.connected_components(G):
        Hh = G.subgraph(comp)
        pts = sorted(x[1] for x in comp if x[0] == 'p')
        pieces.append({'points': pts, 'blocks': sorted(x[1] for x in comp if x[0] == 'b'),
                       'rank': Hh.number_of_edges() - Hh.number_of_nodes() + 1, 'rays': sum(A['rays'][k] for k in pts), 'H': Hh})
    A['pieces'] = pieces
    return A, 'in'


def child(conn, sizes, edges, T, H, V, mem):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None:
            conn.send({'kind': 'stall', 't': t})
            return
        if r['new'] == 0:
            conn.send({'kind': 'closed', 't': t})
            return
        born = [j for j, ro in enumerate(P.round_of) if ro == t]
        rec = {'kind': 'round', 't': t, 'count': len(born), 'group': max(P.parents[j] for j in born), 'junctions': len(P.bits_of)}
        sz, e = stage_of(P)
        c = DC.classify(sz, e)
        A, rv = reduced(sz, e)
        rec['stage'] = c
        rec['reduced'] = rv
        conn.send(rec)
        if rv == 'in':
            rd, det = DL.reading(A)
            ranks = [p['rank'] for p in A['pieces']]
            x = DL.exact_counts(A, H)
            rates = []
            for p in A['pieces']:
                if p['rank'] == 1:
                    nn, W = DL.one_cycle_W(A, p)
                    rates.append(DL.rate_of(W))
            conn.send({'kind': 'reading', 't': t, 'class': c, 'reading': rd, 'ranks': sorted(set(ranks)), 'pieces': len(ranks),
                       'maximal_blocks': len(A['blocks']), 'largest_block': max((len(B) for B in A['blocks'].values()), default=0),
                       'live': len(A['live']), 'predicted': x[1:], 'rate1': max(rates) if rates else None})
            # check: grow up to V more rounds, each sent as it completes; after the first, read the reduced stage again
            for k in range(1, V + 1):
                r = P.step(J.F.fewest, None)
                if r is None or r['new'] == 0:
                    conn.send({'kind': 'check_round', 'k': k, 'count': 0})
                    break
                conn.send({'kind': 'check_round', 'k': k, 'count': sum(1 for j, ro in enumerate(P.round_of) if ro == t + k)})
                if k == 1:
                    sz2, e2 = stage_of(P)
                    A2, rv2 = reduced(sz2, e2)
                    rd2 = DL.reading(A2)[0] if rv2 == 'in' else rv2
                    conn.send({'kind': 'stability', 'reading_next': rd2})
            conn.send({'kind': 'check_done'})
            return
    conn.send({'kind': 'horizon', 't': T})


def follow(sizes, edges, T=60, H=40, V=8, mem=6_000_000_000, seconds=900):
    import multiprocessing as mp
    ctx = mp.get_context('fork')
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=child, args=(b, sizes, edges, T, H, V, mem))
    pr.start()
    b.close()
    out = {'rounds': [], 'reading': None, 'check': [], 'stability': None, 'end': 'resource'}
    t0 = time.time()
    while True:
        if a.poll(1.0):
            try:
                m = a.recv()
            except EOFError:
                out['end'] = 'memory' if time.time() - t0 < seconds else 'time'
                break
            k = m['kind']
            if k == 'round':
                out['rounds'].append(m)
            elif k == 'reading':
                out['reading'] = m
                out['end'] = 'read'
            elif k == 'check_round':
                out['check'].append(m['count'])
            elif k == 'stability':
                out['stability'] = m['reading_next']
            elif k == 'check_done':
                break
            else:
                out['end'] = k
                break
            continue
        if not pr.is_alive() and not a.poll(0):
            if out['end'] != 'read':
                out['end'] = 'memory'
            break
        if time.time() - t0 > seconds:
            pr.kill()
            if out['end'] != 'read':
                out['end'] = 'time'
            break
    pr.join(5)
    if pr.is_alive():
        pr.kill()
    out['seconds'] = round(time.time() - t0, 1)
    return out
