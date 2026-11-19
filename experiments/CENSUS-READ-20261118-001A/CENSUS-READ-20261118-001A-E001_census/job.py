"""Shared-runner job for CENSUS-READ-20261118-001A-E001: the incremental reader R3 (RING-READ-20261118-001B, frozen) on every
stage of the TOUCH-CENSUS arrangements and on FRESH-COUNT's 247 mixed-count stages.

Cases: shards of 50 census arrangements (sorted key list, as TOUCH-CENSUS), and the 60 mixed seeds (700000 + s, as
FRESH-COUNT's `reader_mixed`).  For each stage the table is exact up to H = (largest junction) + 2 over every bond with a side
of at most min(junctions, 6) junctions (all junctions at 14 or fewer), pooled above; the readers see only the table.

Per stage: R1 (BOND-NEXT-JOIN's stages run on to H + 1), R3 (frozen), R3m (R3 without its one-shared-distinction filter), and,
for the mixed stages, FRESH-COUNT's own threshold reader.  Each output is classed as exact, outside swap (the truth with one
junction J replaced by the set of all loose distinctions), same states (another presentation of the same allowed states,
such as a Whitney twist at a 2-separation), or misread.  Each stage is tagged by the vertex connectivity of its junction graph
with the outside vertex.  At every stage R3 reads exactly, its verdict at every horizon h (table pooled above h, stages to h + 1).
"""
import random
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental'))
import reader3 as R3  # noqa: E402  (checks ticket A's ringread.py hash)
R = R3.R
B = R.B
CENSUS = ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'
sys.path.insert(0, str(CENSUS))
import arrlib as A  # noqa: E402
S = A.S
F = A.F
FRESH = ROOT / 'experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count'

SHARD = 50
RMAX = 8
JCAP = 120
_ARR = None


def load():
    """The census's sorted arrangement list (TOUCH-CENSUS job.py's order), regenerated, not read from its cache."""
    arr = A.arrangements(5, labelled=True)
    return sorted(arr)


def setup(params):
    global _ARR
    _ARR = load()


def cases():
    data = _ARR if _ARR is not None else load()
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:04d}', {'part': 'census', 'lo': s, 'hi': min(len(data), s + SHARD)}
    for s in range(60):
        yield f'mixed-{s:02d}', {'part': 'mixed', 'seed': 700000 + s}


def r3m(table, top):
    """R3 without the filter refusing a clique that meets a known junction in two or more distinctions."""
    table = B.normalize_distance_pairs(table)
    labels = B.table_labels(table)
    known, known_set, basis = [], set(), {}
    for s in range(3, top + 1):
        raw = {p for p, d in table.items() if d < s}
        holders = {}
        for i, st in enumerate(known):
            for b in st:
                holders.setdefault(b, set()).add(i)
        crossed = set()
        for sup in R3.groups(known, s):
            for x, y in combinations(R3.bits_of(sup), 2):
                if not (holders.get(x, set()) & holders.get(y, set())):
                    crossed.add((x, y))
        found = B.clique_stars(labels, raw - crossed)
        for c in sorted(found, key=lambda c: (len(c), sorted(c))):
            if c in known_set or len(c) > s:
                continue
            w = sum(1 << b for b in c)
            if R.in_span(w, basis):
                continue
            known.append(c)
            known_set.add(c)
            R.add_row(w, basis)
    return set(known)


def rank(words):
    basis = {}
    for w in words:
        R.add_row(w, basis)
    return len(basis)


def verdict(got, truth, loose):
    """exact; outside_swap (one junction replaced by the loose set); same_states (another presentation of the same allowed
    states: the junctions span the same parity space, e.g. a Whitney twist); misread (different allowed states)."""
    if got == truth:
        return 'exact'
    if loose and len(got) == len(truth) and loose in got and len(truth - got) == 1:
        return 'outside_swap'
    g = [sum(1 << b for b in s) for s in got]
    t = [sum(1 << b for b in s) for s in truth]
    rg, rt = rank(g), rank(t)
    if rg == rt and rank(g + t) == rt:
        return 'same_states'
    return 'misread'


def connectivity(stars):
    """Vertex connectivity of the junction graph with the outside vertex: 'three' (3-connected), 'two', 'one' (cut vertex),
    'zero' (the outside vertex isolated: nothing loose), or 'small' (at most three vertices)."""
    import networkx as nx
    adj = R.junction_graph(stars)
    G = nx.Graph()
    for u in range(len(adj)):
        G.add_node(u)
        for v in adj[u]:
            G.add_edge(u, v)
    if G.number_of_nodes() <= 3:
        return 'small'
    k = nx.node_connectivity(G)
    return {0: 'zero', 1: 'one', 2: 'two'}.get(k, 'three')


def read_stage(stars, fresh_reader=None):
    """All readings of one presentation.  stars: list of junction distinction sets."""
    stars = [frozenset(s) for s in stars]
    truth = set(stars)
    own = R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    n = len(stars)
    K = max(map(len, stars))
    H = K + 2
    m = n if n <= 14 else 6
    table, _ = R.bond_table(stars, m, H)
    shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
    out = {'junctions': n, 'distinctions': len(own), 'largest': K, 'loose': len(loose),
           'max_shared': max(shared.values()) if shared else 0, 'sizes': dict(Counter(map(len, stars))),
           'min_distance': min(table.values()) if table else None, 'connectivity': connectivity(stars),
           'table_complete': n <= 14}
    for name, reader in (('r1', lambda t, top: R.r1(t, top)), ('r3', R3.r3), ('r3m', r3m)):
        got = reader(table, H + 1)
        out[name] = verdict(got, truth, loose)
        if out[name] != 'exact':
            out[name + '_missed'] = len(truth - got)
            out[name + '_extra'] = len(got - truth)
    if fresh_reader is not None:
        out['fresh_reader'] = fresh_reader(stars)
    for name in ('r3', 'r3m'):
        if out[name] != 'exact':
            continue
        reader = R3.r3 if name == 'r3' else r3m
        by_h = {h: reader(R.pooled(table, h), h + 1) == truth for h in range(H - 1, 0, -1)}
        out[name + '_exact_by_horizon'] = {str(h): v for h, v in by_h.items()}
        least = None
        for h in range(H - 1, 0, -1):
            if by_h[h]:
                least = h
            else:
                break
        out[name + '_least_horizon'] = least
        out[name + '_monotone'] = all(not v for h, v in by_h.items() if least is not None and h < least)
    return out


def census_stages(key):
    stars = A.stars_of(key)
    P = S.from_junctions(stars)
    stages, outcome = [], 'alive'
    for r in range(RMAX + 1):
        if len(P.bits_of) > JCAP:
            outcome = 'cap'
            break
        st = read_stage(P.bits_of)
        st['round'] = r
        stages.append(st)
        if r == RMAX:
            break
        res = P.step(S.gf2(F.fewest), None)
        if res is None:
            outcome = 'stall'
            break
        if res['new'] == 0:
            outcome = 'closed'
            break
    return {'key': [list(key[0]), list(key[1])], 'knots': len(key[0]), 'outcome': outcome, 'stages': stages}


_FRESH_READER = None


def fresh_reader():
    """FRESH-COUNT's own threshold reader (bonds.read_stars on its exact table), its verdict classes."""
    global _FRESH_READER
    if _FRESH_READER is None:
        sys.path.insert(0, str(FRESH))
        import bonds  # noqa: E402

        def run_it(stars):
            allbits, d = bonds.distances(stars, limit=3_000_000)
            kmax = max(len(s) for s in stars)
            got = set(bonds.read_stars(allbits, d, kmax))
            truth = set(stars)
            own = R.owners(stars)
            loose = frozenset(b for b, js in own.items() if len(js) == 1)
            if got == truth:
                return 'exact'
            if got == truth | {loose}:
                return 'exact_plus_all_loose'
            return 'misread'
        _FRESH_READER = run_it
    return _FRESH_READER


def mixed_stages(seed):
    """FRESH-COUNT job.py `reader_mixed`, replayed: same seed use, same stage rule."""
    rng = random.Random(seed)
    a = rng.choice([3, 4])
    q = rng.choice([0.1, 0.2, 0.4])
    P = F.Presentation(a)
    stages = []
    for _ in range(6):
        if len(P.bits_of) > 16:
            break
        st = read_stage(P.bits_of, fresh_reader())
        st['round'] = P.rounds
        stages.append(st)
        s = P.step(F.surplus(q), None, rng)
        if s is None or s['new'] == 0:
            break
    return {'seed': seed, 'a': a, 'q': q, 'stages': stages}


def run(case_id, p):
    if p['part'] == 'mixed':
        return mixed_stages(p['seed'])
    data = _ARR if _ARR is not None else load()
    return {'arrangements': [census_stages(k) for k in data[p['lo']:p['hi']]]}
