"""Shared-runner job for NAE-GROWTH-20261119-001B-E001: the cheapest growth under parity and under not-all-equal, side by side.

Part C: every census arrangement (arrlib, 26,441 connected arrangements of one to five knots of three to five places), in shards of
100, grown under the fewest counts by both laws to 14 rounds, 3,000 junctions or 120 seconds each.  Parity reads "implied"
structurally (FRESH-COUNT's test, equal to GF(2) by its gate); not-all-equal reads it by SAT (naelib).  Each run logs every implied
junction, and the not-all-equal run logs the hypotheses of the no-implication lemma: the fewest places of any junction, the most
bits one parent gives one junction, and the fewest places a parent keeps outside a new junction.
Part B: every stage of the not-all-equal growth from the census arrangements of one to four knots with at most 15 distinctions
(to 8 rounds): the exact bond-distance tables of the same stars under both laws (bondlib; a pair in no bond gets 0, read as
infinite), the stars themselves, the junctions whose removal leaves the allowed states unchanged (redundant), the parents of each
junction of the next round (who joins whom), and BOND-NEXT-JOIN's distance reader run on each (outside its proved family: a
control).
Part P: the pilot starts of the ring line (rings of five, a spare-less ring, a chain, a two-ring join), both laws, 14 rounds."""
import importlib.util
import itertools
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import naelib as N  # noqa: E402
import bondlib as B  # noqa: E402
J = N.J
sys.path.insert(0, str(N.ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib  # noqa: E402

ROUNDS, MAXJ, TMAX = 14, 3000, 120.0
BMAX, BROUNDS = 15, 8
READER = N.ROOT / 'proofs/BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/check_rearrangements.py'


def reader():
    spec = importlib.util.spec_from_file_location('bnj_reader', READER)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def start(sizes, edges):
    P = N.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    return P


def logged(law, log, hyp, joins=None):
    def base(P, info, rng):
        if joins is not None:
            joins.append([])
        for i in info:
            jid = i['j']
            old = P.bits_of[jid][:i['p']]
            given = {}
            for b in old:
                for o in P.owner[b]:
                    if o != jid:
                        given[o] = given.get(o, 0) + 1
            for o, g in given.items():
                hyp['max_given'] = max(hyp['max_given'], g)
                hyp['min_kept'] = min(hyp['min_kept'], len(P.bits_of[o]) - g)
            if joins is not None:
                joins[-1].append(sorted(given))
            if i['implied']:
                log.append([P.rounds, i['p'], i['d']])
        return N.F.fewest(P, info, rng)
    base.__name__ = 'fewest'
    return N.nae_rule(base) if law == 'nae' else base


def grow(sizes, edges, law, rounds=ROUNDS, maxj=MAXJ, tmax=TMAX, stages=None, joins=None):
    P = start(sizes, edges)
    log, hyp = [], {'max_given': 0, 'min_kept': 10 ** 9}
    rule = logged(law, log, hyp, joins)
    t0, out = time.time(), 'alive'
    if stages is not None:
        stages.append([list(s) for s in P.bits_of])
    for _ in range(rounds):
        r = P.step(rule, None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if stages is not None:
            stages.append([list(s) for s in P.bits_of])
        if len(P.bits_of) > maxj:
            out = 'cap'
            break
        if time.time() - t0 > tmax:
            out = 'time'
            break
    hyp['min_places'] = min(len(s) for s in P.bits_of)
    if hyp['min_kept'] == 10 ** 9:
        hyp['min_kept'] = None
    return {'outcome': out, 'rounds': P.rounds, 'counts': P.counts_by_round(), 'implied': log,
            'seconds': round(time.time() - t0, 2), **hyp}


def both(sizes, edges, **kw):
    return {'parity': grow(sizes, edges, 'parity', **kw), 'nae': grow(sizes, edges, 'nae', **kw)}


def stage_tables(stars, R):
    n = 1 + max(b for s in stars for b in s)
    out = {'junctions': len(stars), 'bits': n, 'largest': max(len(s) for s in stars)}
    owners = {}
    for j, s in enumerate(stars):
        for b in s:
            owners.setdefault(b, []).append(j)
    out['cycle_rank'] = sum(len(o) == 2 for o in owners.values()) - len(stars) + 1
    truth = {frozenset(str(b) for b in s) for s in stars}
    tabs = {}
    for law in ('parity', 'nae'):
        st = B.states(n, stars, law)
        redundant = sum(len(B.states(n, stars[:j] + stars[j + 1:], law)) == len(st) for j in range(len(stars)))
        T = {k: (0 if d == n else d) for k, d in B.table(n, st, n).items()}     # a pair in no bond: 0 (infinite)
        tabs[law] = T
        named = {(str(x), str(y)): (6 if d == 0 else min(d, 6)) for (x, y), d in T.items()}
        got = R.recover_stars(named)
        out[law] = {'states': int(len(st)), 'redundant': redundant, 'reader_exact': got == truth,
                    'reader_missing': len(truth - got), 'reader_extra': len(got - truth),
                    'table': [T[(x, y)] for x, y in itertools.combinations(range(n), 2)]}
    diff = [[x, y, tabs['parity'][(x, y)], tabs['nae'][(x, y)]] for (x, y) in tabs['parity']
            if tabs['parity'][(x, y)] != tabs['nae'][(x, y)]]
    out['stars'] = [list(x) for x in stars]
    out['tables_equal'] = not diff
    out['differences'] = len(diff)
    out['nae_larger'] = sum(1 for d in diff if (d[3] or 10 ** 9) > (d[2] or 10 ** 9))
    out['nae_smaller'] = sum(1 for d in diff if (d[3] or 10 ** 9) < (d[2] or 10 ** 9))
    return out


def pilot_starts():
    R = J.ring_edges
    out = {
        'ring5-bare': (J.bare_sizes(5, R(5)), R(5)),
        'ring5-spare1': ([4] * 5, R(5)),
        'ring44445': ([4, 4, 4, 4, 5], R(5)),
        'ring5-five-place': ([5] * 5, R(5)),
        'chain333': ([3, 3, 3], [(0, 1), (1, 2)]),
        'pair33': ([3, 3], [(0, 1)]),
        'lone3': ([3], []),
        'lone5': ([5], []),
    }
    e = R(5) + R(5, 5) + [(0, 5)]
    out['two-ring-bare'] = (J.bare_sizes(10, e), e)
    return out


def cases():
    keys = sorted(arrlib.arrangements(5))
    for s in range(0, len(keys), 100):
        yield f'C-{s // 100:04d}', {'part': 'C', 'keys': [[list(a), list(b)] for a, b in keys[s:s + 100]]}
    small = [k for k in keys if len(k[0]) <= 4]
    for s in range(0, len(small), 100):
        yield f'B-{s // 100:04d}', {'part': 'B', 'keys': [[list(a), list(b)] for a, b in small[s:s + 100]]}
    for name, (sz, e) in pilot_starts().items():
        yield f'P-{name}', {'part': 'P', 'start': [list(sz), [list(x) for x in e]]}


def run(case_id, payload):
    if payload['part'] == 'C':
        out = []
        for a, b in payload['keys']:
            sz, e = edges_of((tuple(a), tuple(b)))
            out.append(dict(both(sz, e), key=[a, b]))
        return {'arrangements': out}
    if payload['part'] == 'P':
        sz, e = payload['start']
        return {'start': payload['start'], **both(sz, [tuple(x) for x in e], maxj=20000, tmax=300.0)}
    R = reader()
    out = []
    for a, b in payload['keys']:
        sz, e = edges_of((tuple(a), tuple(b)))
        stages, joins = [], []
        g = grow(sz, e, 'nae', rounds=BROUNDS, maxj=MAXJ, stages=stages, joins=joins)
        rows = []
        for t, stars in enumerate(stages):
            if 1 + max(x for s in stars for x in s) > BMAX:
                break
            # who joins whom next: the parents (junction ids of this stage) of each junction of the next round; [] if none
            nxt = joins[t] if t < len(joins) else []
            rows.append(dict(stage_tables(stars, R), round=t, next_parents=nxt))
        out.append({'key': [a, b], 'outcome': g['outcome'], 'stages': rows})
    return {'arrangements': out}
