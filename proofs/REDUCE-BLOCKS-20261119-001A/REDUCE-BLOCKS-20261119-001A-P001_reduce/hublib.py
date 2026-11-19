"""REDUCE-BLOCKS-20261119-001A-P001: the hub realization of a start's maximal blocks, and the engine on both.

**The hub realization H(X).** Its live knots are X's live knots, with the same open counts. For every maximal block B of X (a
set N(w) ∩ live with at least two points, not inside another), H(X) has one dead hub that shares one distinction with each point
of B. A two-point block's hub shares one more distinction with a dead connector, so that it has three places. Dead connectors join
the hubs in a chain, and each live knot in no block hangs on its own connector, so that H(X) is connected.
- **No connector holds two live knots,** and no live knot touches a live knot. So H(X)'s blocks are exactly X's maximal blocks.
- **Places.** A live knot gets shared + open places, and a dead knot gets its shared count, at least three.

**The comparison.** X and H(X) are grown by the program's engine (joinlib's state, the fewest counts, structural implied test).
Their per-round multisets of (parents, fresh) are compared from round 1 on. Round 0 counts the knots, which differ."""
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('rb_cc', ROOT / 'proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py')
CC = importlib.util.module_from_spec(_s)
sys.modules['rb_cc'] = CC
_s.loader.exec_module(CC)
DC, J = CC.DC, CC.J


def live_and_blocks(sizes, edges):
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    ls = set(live)
    fam = {frozenset(nb[w] & ls) for w in range(n) if len(nb[w] & ls) >= 2}
    maximal = sorted((B for B in fam if not any(B < C for C in fam)), key=sorted)
    return live, opn, maximal


def hub_realization(sizes, edges):
    live, opn, maximal = live_and_blocks(sizes, edges)
    idx = {k: i for i, k in enumerate(live)}
    e = []
    nxt = len(live)
    hubs = []
    for B in maximal:
        h = nxt
        nxt += 1
        hubs.append(h)
        for k in sorted(B):
            e.append((idx[k], h))
    inblock = set().union(*maximal) if maximal else set()
    lone = [k for k in live if k not in inblock]
    conns = []
    for h in hubs + [None] * len(lone):
        c = nxt
        nxt += 1
        conns.append(c)
        if h is not None:
            e.append((h, c))
    for c, k in zip(conns[len(hubs):], lone):
        e.append((idx[k], c))
    for c1, c2 in zip(conns, conns[1:]):
        e.append((c1, c2))
    n = nxt
    sh = Counter()
    for a, b in e:
        sh[a] += 1
        sh[b] += 1
    # dead knots need three places: add a shared distinction between a short dead knot and a dead neighbour (or its connector)
    dead = set(range(len(live), n))
    nbd = defaultdict(set)
    for a, b in e:
        nbd[a].add(b)
        nbd[b].add(a)
    for w in sorted(dead):
        while sh[w] < 3:
            cand = sorted(x for x in nbd[w] if x in dead)
            if not cand:
                c = nxt
                nxt += 1
                dead.add(c)
                e.append((w, c))
                nbd[w].add(c)
                nbd[c].add(w)
                sh[w] += 1
                sh[c] += 1
                continue
            x = cand[0]
            e.append((w, x))
            sh[w] += 1
            sh[x] += 1
    n = nxt
    for w in sorted(dead):
        while sh[w] < 3:
            x = sorted(y for y in nbd[w] if y in dead)[0]
            e.append((w, x))
            sh[w] += 1
            sh[x] += 1
    sizes_h = [sh[i] + opn[live[i]] if i < len(live) else sh[i] for i in range(n)]
    return sizes_h, sorted(tuple(sorted(x)) for x in e)


def grow_keys(sizes, edges, T, maxj=200000):
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    out = []
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None:
            out.append('stall')
            break
        if r['new'] == 0:
            out.append('closed')
            break
        out.append(sorted(Counter((P.parents[j], P.fresh[j]) for j, ro in enumerate(P.round_of) if ro == t).items()))
        if len(P.bits_of) > maxj:
            out.append('cap')
            break
    return out


def compare(sizes, edges, T):
    sh_, eh = hub_realization(sizes, edges)
    a = grow_keys(sizes, edges, T)
    b = grow_keys(sh_, eh, T)
    m = min(len(a), len(b))
    return {'equal': a[:m] == b[:m] and (len(a) == len(b) or a[m - 1:m] in (['cap'],) or b[m - 1:m] in (['cap'],)),
            'rounds': m, 'hub_knots': len(sh_), 'knots': len(sizes)}
