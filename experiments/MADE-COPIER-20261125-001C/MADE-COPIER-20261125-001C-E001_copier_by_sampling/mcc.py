"""Engine of MADE-COPIER-20261125-001C-E001: a copier by sampling, written from the frozen texts.

  PC research/MADE-COPIER-20261125-001C/preregistration.md      DC research/MADE-COPIER-20261125-001/definitions_c.md
  D  research/MADE-COPIER-20261125-001/definitions.md            DB research/MADE-COPIER-20261125-001/definitions_b.md
  FD research/PARTS-MEET-AGAIN-20261124-001/definitions.md       SD research/RING-IN-BALANCE-20261123-001/definitions.md
Readings taken where the text leaves a choice are numbered in deviations.md of this folder (cited dev n).

The growth is the fold study's engine (pm.py, knots.py, paired.py), imported unchanged; ticket A's engine (mc.py) is
imported for its descents and tie classes.  Two module attributes of pm are set at import, the files unedited:
pm.GUARD multiplied by ten (DB 3.9, DC 1.5) and pm.take_candidates replaced by a wrapper that returns the engine's own
lists unchanged except inside a fully masked continuation (DC 4.1; dev 3).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
FOLD = os.path.join(ROOT, 'experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
TA = os.path.join(ROOT, 'experiments/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier')
DATA = os.path.join(ROOT, 'research/MADE-COPIER-20261125-001C')
DATA_A = os.path.join(ROOT, 'research/MADE-COPIER-20261125-001A')
OUT = os.path.join(ROOT, 'artifacts/MADE-COPIER-20261125-001C/MADE-COPIER-20261125-001C-E001_copier_by_sampling')
ENGINE_SHA = {
    'pm.py': '3aa69b5b96505f24f28640ef483c09d8831440ab7ebfcdc4849785ead818dde7',
    'knots.py': '9138ae86894fed04a5dde1a5af523f36d41ef26567ccb0b6f4aa7488eeadcd45',
    'paired.py': '70a691de9206bb4026dea02bc3c78091530f2031a9e8773cd6c1e9c1ae33d8f7',
    'mc.py': 'c7891c8d7ac30c1b180c5c1c8939e036d83bcc919cab7eb748bafac56c7e4927',
}

sys.path.insert(0, FOLD)
sys.path.insert(0, TA)
import networkx as nx  # noqa: E402
import knots as K  # noqa: E402
import paired as P  # noqa: E402
import pm  # noqa: E402
import mc  # noqa: E402

# this folder first again (mc.py puts the fold engine's folder first): no module of this folder is shadowed
while HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)


def engine_hashes():
    out = {}
    for fn in ('pm.py', 'knots.py', 'paired.py'):
        with open(os.path.join(FOLD, fn), 'rb') as f:
            out[fn] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(TA, 'mc.py'), 'rb') as f:
        out['mc.py'] = hashlib.sha256(f.read()).hexdigest()
    return out


# ------------------------------------------------------------------------------------- module attributes set at import
if not getattr(pm, '_mcc_guard_x10', False):
    for _k in list(pm.GUARD):
        pm.GUARD[_k] *= 10                       # DB 3.9: the fold engine's limits multiplied by ten
    pm._mcc_guard_x10 = True

_ORIG_TC = pm.take_candidates
_TC_MASK = [None]      # set only while a fully masked continuation grows (dev 3)
_TC_VERIFY = [False]   # tests: every call compared with the fold engine's own function (dev 40)
_TC_CACHE = {'S': None, 'nk': -1, 'nd': -1, 'meets': {}, 'base': {}}


def _meets(S, p, cache):
    m = cache['meets'].get(p)
    if m is None:
        m = S.meets(p)
        cache['meets'][p] = m
    return m


def _cached_candidates(S, take, b):
    """The fold engine's take_candidates for MET, STEPS-1 and STEPS-2, computed once per parent within a round (dev
    40): the takes of a round are all formed on the structure at the start of the round, which no take changes, so
    a parent's met knots and an offshoot's candidates before its own inputs are removed are the same for every birth
    of the round.  Returns None for any other rule (the engine's function is then used)."""
    c = _TC_CACHE
    if c['S'] is not S or c['nk'] != S.n_knots or c['nd'] != S.n_distinctions:
        c.update(S=S, nk=S.n_knots, nd=S.n_distinctions, meets={}, base={})
    H = S.holders
    ps = b['parents']
    have = set(b['inputs'])
    if b['kind'] == 'join':
        if take != 'MET':
            return []
        ms = sorted((_meets(S, p, c) for p in ps), key=len)
        common = set(ms[0]) if ms else set()
        for m in ms[1:]:
            common &= m
        pset = set(ps)
        common -= pset
        cs = set()
        for w in common:
            for d in S.places[w]:
                # "held by no parent" read as "no holder is a parent" (d is a place of p exactly when p holds d)
                if len(H[d]) >= 2 and not any(x in pset for x in H[d]):
                    cs.add(d)
        return [sorted(cs - have)]
    if take not in ('MET', 'STEPS-1', 'STEPS-2'):
        return None
    p = ps[0]
    key = (take, p)
    base = c['base'].get(key)
    if base is None:
        own = set(S.places[p])
        cs = set()
        if take == 'MET':
            src = _meets(S, p, c)
        else:
            src = S.level(p, int(take.split('-')[1]))
        for w in src:
            for d in S.places[w]:
                if len(H[d]) >= 2 and d not in own:
                    cs.add(d)
        base = sorted(cs)
        c['base'][key] = base
    return [[d for d in base if d not in have]]


def _take_candidates(S, take, b, members_parts=None):
    out = None
    if take in ('MET', 'STEPS-1', 'STEPS-2'):
        out = _cached_candidates(S, take, b)
    if out is None:
        out = _ORIG_TC(S, take, b, members_parts)
    if _TC_VERIFY[0]:
        ref = _ORIG_TC(S, take, b, members_parts)
        if ref != out:
            raise AssertionError('cached candidates differ: %r %r %r' % (b, ref, out))
    m = _TC_MASK[0]
    if m is None:
        return out
    ps = b['parents']
    A, B = m.A, m.B
    in_a = any(p in A for p in ps)
    in_b = any(p in B for p in ps)
    if not (in_a or in_b):
        return out
    H = S.holders
    res = []
    for c in out:
        res.append([d for d in c if not ((in_a and any(w in B for w in H[d])) or (in_b and any(w in A for w in H[d])))])
    return res


if not getattr(pm, '_mcc_tc_wrapped', False):
    pm.take_candidates = _take_candidates
    pm._mcc_tc_wrapped = True

_ORIG_ROW = pm.St.row


def _row(self, u):
    """The fold engine's St.row (a knot's places as the bits of an integer), built in one pass (dev 41)."""
    P = self.places[u]
    if len(P) < 64:
        return _ORIG_ROW(self, u)
    ba = bytearray(max(P) // 8 + 1)
    for d in P:
        ba[d >> 3] |= 1 << (d & 7)
    return int.from_bytes(ba, 'little')


if not getattr(pm, '_mcc_row_wrapped', False):
    pm.St.row = _row
    pm._mcc_row_wrapped = True

ROUNDS = 8
KNOT_BOUND = 500

# --------------------------------------------------------------------------------------------------------- the census
_FACT = {3: 6, 4: 24, 5: 120}


def automorphisms(G, n):
    E = {frozenset(e) for e in G.edges()}
    out = []
    for p in itertools.permutations(range(n)):
        if all(frozenset((p[a], p[b])) in E for a, b in G.edges()):
            out.append(p)
    return out


def stars_of(n, edges, loose):
    """DC 1.1: one shared distinction for each pair of knots the graph joins, in sorted order, then the loose
    distinctions in knot order."""
    edges = sorted(tuple(sorted(e)) for e in edges)
    stars = [[] for _ in range(n)]
    for lab, (a, b) in enumerate(edges):
        stars[a].append(lab)
        stars[b].append(lab)
    lab = len(edges)
    for i in range(n):
        for _ in range(loose[i]):
            stars[i].append(lab)
            lab += 1
    return stars


def rebuild_census():
    """DC 1.1, rebuilt from the rule: connected graphs of networkx's graph atlas on 3 to 5 nodes, a loose count 0 to 3
    on each knot with degree plus loose count at least 3 and at least one live knot, each kept when least in its orbit."""
    atlas = nx.graph_atlas_g()
    out = []
    for n in (3, 4, 5):
        for g, G in enumerate(atlas):
            if G.number_of_nodes() != n or not nx.is_connected(G):
                continue
            auts = automorphisms(G, n)
            deg = [G.degree(i) for i in range(n)]
            edges = sorted(tuple(sorted(e)) for e in G.edges())
            for loose in itertools.product(range(4), repeat=n):
                if any(deg[i] + loose[i] < 3 for i in range(n)) or not any(loose):
                    continue
                imgs = []
                for p in auts:
                    im = [0] * n
                    for i in range(n):
                        im[p[i]] = loose[i]
                    imgs.append(tuple(im))
                if loose != min(imgs):
                    continue
                stab = sum(1 for im in imgs if im == loose)
                out.append({'id': 'n%d-g%d-%s' % (n, g, ''.join(map(str, loose))), 'n': n, 'g': g,
                            'loose': list(loose), 'labelled': _FACT[n] // stab, 'edges': edges,
                            'stars': stars_of(n, edges, loose)})
    return out


with open(os.path.join(DATA, 'starts_c.json')) as _f:
    STARTS_C = json.load(_f)
with open(os.path.join(DATA, 'cases_c.json')) as _f:
    CASES_C = json.load(_f)
with open(os.path.join(DATA_A, 'starts.json')) as _f:
    STARTS_A = json.load(_f)

_ATLAS = None


def census():
    """The census list of starts_c.json with stars rebuilt by the rule (the gate checks the rebuilt list)."""
    global _ATLAS
    if _ATLAS is None:
        atlas = nx.graph_atlas_g()
        out = []
        for e in STARTS_C['starts']:
            G = atlas[e['g']]
            out.append(dict(e, stars=stars_of(e['n'], G.edges(), e['loose'])))
        _ATLAS = out
    return _ATLAS


ID_INDEX = None


def start_by_id(sid):
    global ID_INDEX
    if ID_INDEX is None:
        ID_INDEX = {e['id']: i for i, e in enumerate(census())}
    return census()[ID_INDEX[sid]]


def order():
    """DC 1.5: random.Random('C|order').sample(range(3376), 3376)."""
    return random.Random('C|order').sample(range(3376), 3376)


def run_order(knot_law):
    """The starts of a run in order: under parity the set-aside starts skipped (DC 1.1, 1.5)."""
    C = census()
    o = order()
    if knot_law == 'parity':
        return [i for i in o if not C[i]['set_aside_parity']]
    return o


# ------------------------------------------------------------------------------------------------------------- laws
RATIONS = ('FLOOR1', 'FBP', 'CAP-2', 'CAP-3', 'CAP-4', 'ORD', 'RATION-2')
TREATS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
TAKES = ('MET', 'STEPS-1')


class Spec:
    """A law of the family with its knot law, release rule and weighting of takes (T1 take-by-take, T2 holder)."""
    __slots__ = ('ration', 'treatment', 'take', 'knot_law', 'release', 'weighting')

    def __init__(self, ration, treatment, take, knot_law, release='RELEASE', weighting='T1'):
        assert ration in RATIONS and treatment in TREATS and take in ('MET', 'STEPS-1', 'STEPS-2')
        assert knot_law in ('parity', 'nae') and release in ('RELEASE', 'HOLD') and weighting in ('T1', 'T2')
        self.ration, self.treatment, self.take = ration, treatment, take
        self.knot_law, self.release, self.weighting = knot_law, release, weighting

    def law(self):
        kw = dict(ration='FLOOR1' if self.ration == 'FBP' else self.ration, treatment=self.treatment,
                  release=self.release, knot_law=self.knot_law, take=self.take, choice='OLDEST')
        if self.ration == 'FBP':
            kw['fresh_by_parents'] = True
        return pm.Law(**kw)

    def name(self):
        return '%s/%s/%s/%s/%s/%s' % (self.ration, self.treatment, self.release, self.take, self.knot_law,
                                       self.weighting)

    def key(self):
        return (self.ration, self.treatment, self.take, self.knot_law, self.release, self.weighting)

    @staticmethod
    def from_name(nm):
        r, t, rel, tk, kl, w = nm.split('/')
        return Spec(r, t, tk, kl, rel, w)


def family(take, knot_law, release='RELEASE', weighting='T1'):
    """DC 1.3's order for one taking rule: ration, then treatment."""
    return [Spec(r, t, take, knot_law, release, weighting) for r in RATIONS for t in TREATS]


def family_both(knot_law, release='RELEASE', weighting='T1'):
    """The 42 laws of one knot law in DC 1.3's order (ration, treatment, taking rule)."""
    return [Spec(r, t, tk, knot_law, release, weighting) for r in RATIONS for t in TREATS for tk in TAKES]


# ------------------------------------------------------------------------------------------------------------ seeds
def base_seed(start_id, spec, i):
    """DC 1.4 without the weighting's token: C|<start id>|<ration>|<treatment>|<knot law>|<i>[|STEPS-k][|HOLD]."""
    s = 'C|%s|%s|%s|%s|%d' % (start_id, spec.ration, spec.treatment, spec.knot_law, i)
    if spec.take != 'MET':
        s += '|' + spec.take
    if spec.release == 'HOLD':
        s += '|HOLD'
    return s


def t2(spec):
    return '|T2' if spec.weighting == 'T2' else ''


def growth_seed(start_id, spec, i):
    return base_seed(start_id, spec, i) + t2(spec)


def cont_seed(base, spec, kind, s, i):
    """A continuation's seed: its growth's seed followed by |<kind>|<s>|<i>, with |T2 last of all (dev 5)."""
    return '%s|%s|%d|%d%s' % (base, kind, s, i, t2(spec))


# --------------------------------------------------------------------------------------------------------- samplers
class Sampler:
    """The take-by-take weighting (T1): one call rnd.randrange(len(candidates)) per take; the holder weighting (T2):
    one call rnd.choices(candidates, weights=h, k=1)[0], h the holders of each candidate at the start of the round.
    Candidates arrive sorted by name from the fold engine; a single candidate also makes its call (DC 1.4)."""

    def __init__(self, seed, weighting='T1'):
        self.rnd = random.Random(seed)
        self.weighting = weighting
        self.S = None          # the structure at the start of the round (set by the run)
        self.calls = 0
        self.multi = 0         # takes with two or more candidates
        self.log = None

    def __call__(self, key, cands):
        self.calls += 1
        if len(cands) >= 2:
            self.multi += 1
        if self.weighting == 'T1':
            d = cands[self.rnd.randrange(len(cands))]
        else:
            H = self.S.holders
            d = self.rnd.choices(cands, weights=[len(H[x]) for x in cands], k=1)[0]
        if self.log is not None:
            self.log.append((key, tuple(cands), d))
        return d


class Grown:
    """One growth or continuation: pm.Run with the chooser, the states after every round kept by reference (a state is
    never changed by the engine once its round is over; pm.Run copies before each round)."""

    def __init__(self, S0, law, sampler, rounds=ROUNDS, knot_bound=KNOT_BOUND, prefix_snaps=None, prefix_recs=None,
                 mask=None, full_mask=False):
        snaps = list(prefix_snaps or []) + [S0]
        sampler.S = S0

        def on_round(run, S, rec):
            sampler.S = S
            snaps.append(S)
        ctx = {'chooser': sampler}
        if mask is not None:
            ctx['mask'] = mask
        if full_mask:
            assert mask is not None
            _TC_MASK[0] = mask
        try:
            self.run = pm.Run(S0, law, rounds=rounds, knot_bound=knot_bound, ctx=ctx, keep=False,
                              snapshots=prefix_snaps, records=prefix_recs, on_round=on_round)
        finally:
            _TC_MASK[0] = None
        self.snaps = snaps
        self.records = self.run.records
        self.R = self.run.rounds_done
        self.stop = self.run.stop
        self.guard = self.run.guard
        self.law = law
        self.sampler = sampler
        assert len(self.snaps) == self.R + 1

    @property
    def S(self):
        return self.snaps[-1]

    def knots(self):
        S = self.S
        return S.n_knots - len(S.removed)


def start_state(stars):
    return pm.from_stars(stars)


def grow(stars, spec, seed, rounds=ROUNDS, knot_bound=KNOT_BOUND):
    return Grown(start_state(stars), spec.law(), Sampler(seed, spec.weighting), rounds, knot_bound)


def retired_knots(records, upto):
    out = set()
    for rec in records[:upto]:
        out.update(rec['retired'])
    return out


# ------------------------------------------------------------------------------------------------------- the roster
class LR:
    """The roster of a structure for reading (members, h, k, maximal met sets, parts), equal to pm.build_roster's
    with no mask; the groups (cliques) are not formed (dev 9)."""
    __slots__ = ('members', 'h', 'k', 'maxsets', 'parts', 'part_of', 'part_sets', 'S', '_cls', '_graph', '_sig',
                 '_wl')


def light_roster(S):
    mem = pm.live_members(S)
    R = LR()
    R.S = S
    R.members = tuple(sorted(u for u, _, _ in mem))
    R.h = {u: h for u, h, _ in mem}
    R.k = {u: k for u, _, k in mem}
    sc, inc, _ = pm.met_sets(S, R.members, early_pairs=True)
    if sc:
        m = max(len(M) for M in sc)
        pm._guard('pairs', m * (m - 1) // 2, 'read')
    R.maxsets, _ = pm.maximal_sets(sc)
    ub = sum(len(M) * (len(M) - 1) // 2 for M in R.maxsets)
    if ub > pm.GUARD['pairs']:
        seen = set()
        for M in R.maxsets:
            L = sorted(M)
            for i, a in enumerate(L):
                for b in L[i + 1:]:
                    seen.add((a, b))
        pm._guard('pairs', len(seen), 'read')
    parent = {u: u for u in R.members}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for M in R.maxsets:
        it = iter(M)
        a = find(next(it))
        for b in it:
            rb = find(b)
            if rb != a:
                parent[rb] = a
    comp = defaultdict(list)
    for u in R.members:
        comp[find(u)].append(u)
    R.parts = sorted(tuple(sorted(c)) for c in comp.values())
    R.part_of = {}
    for i, Pt in enumerate(R.parts):
        for u in Pt:
            R.part_of[u] = i
    R.part_sets = [[] for _ in R.parts]
    for M in R.maxsets:
        R.part_sets[R.part_of[next(iter(M))]].append(M)
    R._cls = None
    R._graph = {}
    R._sig = {}
    R._wl = {}
    return R


def roster_or_none(S):
    try:
        return light_roster(S)
    except pm.GuardStop:
        return None


def classes(R):
    """FD 1.6: classes of parts linked by a shared distinction."""
    if R._cls is None:
        S = R.S
        n = len(R.parts)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        by_d = {}
        for u in R.members:
            pu = R.part_of[u]
            for d in S.places[u]:
                q = by_d.get(d)
                if q is None:
                    by_d[d] = pu
                else:
                    a, b = find(q), find(pu)
                    if a != b:
                        parent[b] = a
        R._cls = [find(i) for i in range(n)]
    return R._cls


def part_sig(R, i):
    s = R._sig.get(i)
    if s is None:
        Pt = R.parts[i]
        s = (len(Pt), tuple(sorted((R.h[u], R.k[u]) for u in Pt)), tuple(sorted(len(M) for M in R.part_sets[i])))
        R._sig[i] = s
    return s


def part_graph(R, i):
    G = R._graph.get(i)
    if G is None:
        G = nx.Graph()
        for u in R.parts[i]:
            G.add_node(('m', u), c='m%d,%d' % (R.h[u], R.k[u]))
        for j, M in enumerate(R.part_sets[i]):
            G.add_node(('s', j), c='s')
            for u in M:
                G.add_edge(('s', j), ('m', u))
        R._graph[i] = G
    return G


def part_wl(R, i):
    w = R._wl.get(i)
    if w is None:
        w = nx.weisfeiler_lehman_graph_hash(part_graph(R, i), node_attr='c')
        R._wl[i] = w
    return w


class Form:
    """The form of a part (DC 0: its class under SD lines 29-30)."""
    __slots__ = ('sig', 'graph', 'wl', 'members', 'hk', 'sets')

    def __init__(self, R, i):
        self.sig = part_sig(R, i)
        self.graph = part_graph(R, i)
        self.wl = part_wl(R, i)
        self.members = list(R.parts[i])
        self.hk = [[R.h[u], R.k[u]] for u in R.parts[i]]
        self.sets = [sorted(M) for M in R.part_sets[i]]

    def key(self):
        return '%d|%s|%s|%s' % (self.sig[0], ','.join('%d%d' % hk for hk in self.sig[1]),
                                ','.join(map(str, self.sig[2])), self.wl[:10])

    def same(self, other):
        if self.sig != other.sig or self.wl != other.wl:
            return False
        return nx.is_isomorphic(self.graph, other.graph, node_match=lambda a, b: a['c'] == b['c'])

    def matches(self, R, i):
        if part_sig(R, i) != self.sig or part_wl(R, i) != self.wl:
            return False
        return nx.is_isomorphic(self.graph, part_graph(R, i), node_match=lambda a, b: a['c'] == b['c'])

    def describe(self):
        return {'members': len(self.members), 'hk': sorted(self.hk), 'met_sets': sorted(len(M) for M in self.sets),
                'key': self.key()}


def form_of(R, members):
    i = R.part_of[members[0]]
    assert tuple(sorted(members)) == R.parts[i]
    return Form(R, i)


# ---------------------------------------------------------------------------------------------------------- pairs
def pairs_of_round(S, R, rule='sampled', seed=None, s=None):
    """DC 2.2: every ordered pair (X, Y) of parts after round s, X a made pattern, Y another part, wholly apart; more
    than eight: eight sampled uniformly from the lexicographic list with random.Random(<seed> + '|P|<s>').sample.
    rule 'scratch' (the gate R0 only): the first eight parts by name, at most eight pairs, in lexicographic order."""
    parts = R.parts
    cls = classes(R)
    made = [all(S.made[u] > 0 for u in Pt) for Pt in parts]
    idx = range(len(parts)) if rule in ('sampled', 'every') else range(min(8, len(parts)))
    out, removed = [], 0
    for i in idx:
        if not made[i]:
            continue
        for j in idx:
            if j == i:
                continue
            if cls[i] != cls[j]:
                out.append((i, j))
            else:
                removed += 1
    n_all = len(out)
    if len(out) > 8 and rule != 'every':      # rule 'every' (R6, DC 2.2's swap): every pair, none sampled
        if rule == 'sampled':
            out = sorted(random.Random('%s|P|%d' % (seed, s)).sample(out, 8))
        else:
            out = out[:8]
    return [(parts[i], parts[j]) for i, j in out], n_all, removed


# --------------------------------------------------------------------------------------------- parity residues (ties)
def residue(span, v):
    """The canonical representative of v modulo the span (pm's echelon basis {leading bit: row})."""
    out = 0
    while v:
        p = v.bit_length() - 1
        b = span.get(p)
        if b is None:
            out |= 1 << p
            v ^= 1 << p
        else:
            v ^= b
    return out


def eligible_places(S_s, X, Y):
    """D 3.3 / DC 3.2: the places v of Y after round s that are free and tied to no place of X (parity: by residues
    over the rules after round s; checked against mc.ties_parity, dev 11)."""
    sp = S_s.span
    yp = sorted({d for u in Y for d in S_s.places[u]})
    xp = sorted({d for u in X for d in S_s.places[u]})
    xr = {residue(sp, 1 << d) for d in xp}
    out = []
    for v in yp:
        r = residue(sp, 1 << v)
        if r == 0 or r in xr:
            continue
        out.append(v)
    return out


class TieCache:
    """Made distinctions tied to places, read birth by birth: by S1 and S3 (PC, Settled 7; D 6.1, 6.3) a birth with
    one fresh distinction f, not implied, has f tied to v exactly when the sum of its inputs and v lies in the span of
    the rules before its round; no other made distinction is tied to v (dev 11; checked against mc.ties_parity)."""

    def __init__(self, snaps, records):
        self.snaps, self.records = snaps, records
        self._births = {}
        self._rv = {}

    def births(self, r):
        """[(fresh distinction, residue of the sum of the inputs over the rules before round r)] for round r."""
        x = self._births.get(r)
        if x is None:
            sp = self.snaps[r - 1].span
            x = []
            for b in self.records[r - 1]['births']:
                if b['f'] != 1 or b['implied']:
                    continue
                vec = 0
                for d in b['inputs']:
                    vec |= 1 << d
                x.append((b['fresh'][0], residue(sp, vec)))
            self._births[r] = x
        return x

    def rv(self, r, v):
        key = (r, v)
        x = self._rv.get(key)
        if x is None:
            x = residue(self.snaps[r - 1].span, 1 << v)
            self._rv[key] = x
        return x

    def new_ties(self, r, elig):
        out = {}
        bs = self.births(r)
        if not bs:
            return out
        for v in elig:
            rv = self.rv(r, v)
            got = [f for f, rb in bs if rb == rv]
            if got:
                out[v] = got
        return out


# ------------------------------------------------------------------------------------------------------ the readings
FORM_R = ('form', 'both', 'Yown_form', 'formany_X')       # formany_X: form without "Y's form not X's form" (dev 17)
VAL_R = ('vX', 'v1b', 'vbb', 'vA', 'Yown_val')
CLAIMED = ('form', 'both', 'vX')
REPORTED = ('v1b', 'vbb', 'vA')
YOWN = {'form': 'Yown_form', 'both': 'Yown_form', 'formany_X': 'Yown_form', 'vX': 'Yown_val', 'v1b': 'Yown_val',
        'vbb': 'Yown_val', 'vA': 'Yown_val'}


class PairRef:
    """A pair (X, Y) after round s with what its readings need (DC 3)."""

    def __init__(self, S_s, R_s, X, Y, s, knot_law, values=True):
        self.X, self.Y, self.s = tuple(sorted(X)), tuple(sorted(Y)), s
        self.Xs, self.Ys = set(self.X), set(self.Y)
        self.xform = form_of(R_s, list(self.X))
        self.yform = form_of(R_s, list(self.Y))
        self.same_form = self.xform.same(self.yform)
        self.values = values and knot_law == 'parity'
        self.elig = eligible_places(S_s, self.X, self.Y) if self.values else []
        self.nd_s = S_s.n_distinctions
        self.nk_s = S_s.n_knots


class Sides:
    """X and its descendants, Y and its descendants (FD 4.2), kept round by round from the birth records."""

    def __init__(self, X, Y):
        self.xd, self.yd = set(X), set(Y)

    def add_round(self, rec):
        for b in rec['births']:
            ps = b['parents']
            if any(p in self.xd for p in ps):
                self.xd.add(b['id'])
            if any(p in self.yd for p in ps):
                self.yd.add(b['id'])

    def descent(self, u, S, ref):
        if S.made[u] <= ref.s and u < ref.nk_s:
            return 'X only' if u in ref.Xs else ('Y only' if u in ref.Ys else 'neither')
        a, b = u in self.xd, u in self.yd
        return 'both' if (a and b) else ('X only' if a else ('Y only' if b else 'neither'))


def met(R, sides):
    """The meeting (FD 4.3): a member of X or its descendants and one of Y or its descendants in one part."""
    px = {R.part_of[u] for u in R.members if u in sides.xd}
    if not px:
        return False
    return any(R.part_of[u] in px for u in R.members if u in sides.yd)


def form_counts(R, S, sides, ref):
    """Parts the same as Y's form containing a member made after round s, counted by the descent of their members."""
    c = Counter()
    for i in range(len(R.parts)):
        Pt = R.parts[i]
        if not any(S.made[u] > ref.s for u in Pt):
            continue
        if not ref.yform.matches(R, i):
            continue
        ds = {sides.descent(u, S, ref) for u in Pt}
        c[next(iter(ds)) if len(ds) == 1 else 'mixed'] += 1
    return c


def form_readings(c, ref):
    out = set()
    if c['X only'] >= 2:
        out.add('formany_X')
        if not ref.same_form:
            out.add('form')
    if c['both'] >= 2:
        out.add('both')
    if c['Y only'] >= 2:
        out.add('Yown_form')
    if sum(c.values()) >= 2:
        out.add('yform_any')        # two parts of Y's form, any descent (reported in the gate only, dev 35)
    return out


def value_readings(S, tied, sides, ref):
    out = set()
    detail = []
    for v, fs in tied.items():
        ul = [d for d in fs if len(S.holders[d]) == 1 and not S.barred[d]]
        if len(ul) < 2:
            continue
        ds = Counter(sides.descent(S.holders[d][0], S, ref) for d in ul)
        got = set()
        if ds['X only'] >= 2:
            got.add('vX')
        if ds['X only'] >= 1 and ds['both'] >= 1:
            got.add('v1b')
        if ds['both'] >= 2:
            got.add('vbb')
        if ds['X only'] + ds['both'] >= 1:
            got.add('vA')
        if ds['Y only'] >= 2:
            got.add('Yown_val')
        if got:
            detail.append({'v': v, 'n': len(ul), 'descents': dict(ds)})
        out |= got
    return out, detail


class PairReading:
    """The readings of one pair through one run (growth or continuation)."""
    __slots__ = ('ref', 'sides', 'meet', 'first', 'first_after', 'detail', 'by_round', 'counts', 'tied')

    def __init__(self, ref):
        self.ref = ref
        self.sides = Sides(ref.X, ref.Y)
        self.meet = None
        self.first = {}          # reading -> first round t > s met
        self.first_after = {}    # reading -> first round t >= meeting round met
        self.detail = {}
        self.by_round = {}
        self.counts = {}
        self.tied = {v: [] for v in ref.elig}

    def note(self, got, t):
        for g in got:
            if g not in self.first or t < self.first[g]:
                self.first[g] = t
            if self.meet is not None and t >= self.meet and (g not in self.first_after or t < self.first_after[g]):
                self.first_after[g] = t


def read_pairs(snaps, records, R, refs, need_form=True, need_values=True, rosters=None, keep_rounds=False,
               ties=None):
    """Read every pair of `refs` (all of one s) at every round t > s through R.  rosters: optional cache {t: LR}."""
    if not refs:
        return []
    s = refs[0].s
    out = [PairReading(ref) for ref in refs]
    rosters = rosters if rosters is not None else {}
    tc = ties if ties is not None else TieCache(snaps, records)
    for t in range(s + 1, R + 1):
        rec = records[t - 1]
        for pr in out:
            pr.sides.add_round(rec)
            if need_values and pr.ref.values and pr.ref.elig:
                for v, fs in tc.new_ties(t, pr.ref.elig).items():
                    pr.tied[v].extend(fs)
        S = snaps[t]
        Rt = rosters.get(t, 0)
        if Rt == 0:
            Rt = roster_or_none(S)
            rosters[t] = Rt
        if Rt is None:
            continue
        for pr in out:
            if pr.meet is None and met(Rt, pr.sides):
                pr.meet = t
            got = set()
            if need_form:
                c = form_counts(Rt, S, pr.sides, pr.ref)
                got |= form_readings(c, pr.ref)
                if keep_rounds:
                    pr.counts[t] = dict(c)
            if need_values and pr.ref.values and pr.ref.elig:
                vg, det = value_readings(S, pr.tied, pr.sides, pr.ref)
                got |= vg
                if det and 'values' not in pr.detail:
                    pr.detail['values'] = {'t': t, 'places': det}
            if keep_rounds:
                pr.by_round[t] = sorted(got)
            pr.note(got, t)
    return out


def placed_state(S, t, parent_knot):
    """DC 4.7: two parts of Y's form placed into the state read after round t (and no other): each is two new knots
    y1', y2', each holding one new loose usable distinction of its own and one shared with a new dead knot w'; y1', y2'
    recorded as offshoots made in round t with the one parent `parent_knot`, w' with kind 'placed' and no parents.
    Returns the placed copy and the new members (read, never grown)."""
    T = S.copy()
    extra = []
    for _ in range(2):
        nd = T.n_distinctions
        dy1, dy2, e1, e2 = nd, nd + 1, nd + 2, nd + 3
        for _d in range(4):
            T.holders.append([])
            T.barred.append(False)
        for knot_places, par, kind in (([dy1, e1], (parent_knot,), 'offshoot'),
                                       ([dy2, e2], (parent_knot,), 'offshoot'),
                                       ([e1, e2], (), 'placed')):
            u = T.n_knots
            T.places.append(list(knot_places))
            T.parents.append(tuple(par))
            T.made.append(t)
            T.kind.append(kind)
            for d in knot_places:
                T.holders[d].append(u)
            if kind == 'offshoot':
                T.cand.add(u)
                extra.append(u)
    return T, extra


def placed_form_reading(snaps, records, ref, r, parent_knot):
    """The form readings of the state read after round r with the placement (sides read through round r)."""
    sides = Sides(ref.X, ref.Y)
    for t in range(ref.s + 1, r + 1):
        sides.add_round(records[t - 1])
    T, extra = placed_state(snaps[r], r, parent_knot)
    for u in extra:
        if any(p in sides.xd for p in T.parents[u]):
            sides.xd.add(u)
        if any(p in sides.yd for p in T.parents[u]):
            sides.yd.add(u)
    Rt = roster_or_none(T)
    if Rt is None:
        return set(), {}
    c = form_counts(Rt, T, sides, ref)
    return form_readings(c, ref), dict(c)


# --------------------------------------------------------------------------------------------------- the knot test
def parent_birth(records, u, made):
    if made <= 0:
        return None
    for b in records[made - 1]['births']:
        if b['id'] == u:
            return b
    return None


def reduced_for_parity(S):
    """A structure with the same parity verdicts for every knot (dev 39): each knot keeps its shared places and the
    first of its loose places (by name), the rest dropped, and the kept distinctions renumbered in order.  A knot
    holding a loose distinction constrains no other knot (any solution of the other rules extends to it), and its own
    verdict is whether its shared places are free together under the other rules, whatever its number of loose
    places; so dropping all but one loose place of a knot changes no verdict."""
    H = S.holders
    keep = set()
    for u in range(S.n_knots):
        if u in S.removed:
            continue
        first_loose = None
        for d in S.places[u]:
            if len(H[d]) >= 2:
                keep.add(d)
            elif first_loose is None or d < first_loose:
                first_loose = d
        if first_loose is not None:
            keep.add(first_loose)
    ren = {d: i for i, d in enumerate(sorted(keep))}
    T = pm.St()
    T.places = [[ren[d] for d in P if d in ren] for P in S.places]
    T.holders = [[] for _ in ren]
    for u, Pl in enumerate(T.places):
        for d in Pl:
            T.holders[d].append(u)
    T.barred = [False] * len(ren)
    T.parents = list(S.parents)
    T.made = list(S.made)
    T.kind = list(S.kind)
    T.removed = set(S.removed)
    return T


def parity_verdicts(S):
    """The fold engine's parity test (both methods) on the reduced structure: {'pass': {knot: bool}, 'fail',
    'disagree', 'n'}; and the number of distinctions read."""
    T = reduced_for_parity(S)
    pt = K.parity_test(T)
    pt['distinctions_read'] = T.n_distinctions
    pt['distinctions'] = S.n_distinctions
    return pt


def knot_test(G, only_new_after=None):
    """DC 8: every knot tested at the last round read (parity: both methods; not-all-equal: the birth method on every
    made knot and the direct test on every knot of at most 12 places, as the fold engine's test_run).  Each failure
    dated by its round made and classified (kind, parents, took a distinction, implied)."""
    law = G.law
    R = G.R
    if law.knot_law == 'parity':
        pt = parity_verdicts(G.S)
        ks = [u for u in pt['pass'] if only_new_after is None or G.S.made[u] > only_new_after]
        fails = [u for u in ks if not pt['pass'][u]]
        res = {'verdicts': len(ks), 'disagree': len(pt['disagree'])}
    else:
        kt = K.test_run(G.snaps, law, rounds=[R], only_new_after=only_new_after)
        fails = sorted({f['knot'] for f in kt['fails']})
        res = {'verdicts': kt['verdicts'], 'disagree': len(kt['disagree']), 'untested': len(kt['untested']),
               'birth_vs_direct': kt['birth_vs_direct']}
    rows = []
    S = G.S
    for u in fails:
        b = parent_birth(G.records, u, S.made[u])
        rows.append({'knot': u, 'made': S.made[u], 'kind': S.kind[u], 'parents': len(S.parents[u]),
                     'places': len(S.places[u]), 'took': bool(b and b['rule_takes']),
                     'implied': bool(b and b['implied'])})
    res['fails'] = rows
    res['n_fails'] = len(rows)
    return res


def knot_test_every_round(G):
    """D 8 (R9): every knot at every round read (parity, both methods)."""
    first = {}
    dis = 0
    verdicts = 0
    for t in range(G.R + 1):
        pt = K.parity_test(G.snaps[t])
        verdicts += pt['n']
        dis += len(pt['disagree'])
        for u in pt['fail']:
            first.setdefault(u, t)
    return {'verdicts': verdicts, 'disagree': dis, 'fails': sorted(first), 'first_round': first}


# ------------------------------------------------------------------------------------------------------ statistics
def fisher_greater(a, n1, b, n2):
    """One-sided Fisher exact p-value, null: rate a/n1 not greater than b/n2 (P(X >= a), hypergeometric)."""
    from scipy.stats import fisher_exact
    if n1 == 0 or n2 == 0:
        return 1.0
    return float(fisher_exact([[a, n1 - a], [b, n2 - b]], alternative='greater')[1])


def fisher_two(a, n1, b, n2):
    from scipy.stats import fisher_exact
    if n1 == 0 or n2 == 0:
        return 1.0
    return float(fisher_exact([[a, n1 - a], [b, n2 - b]], alternative='two-sided')[1])


def agresti_caffo(a, n1, b, n2):
    p1 = (a + 1) / (n1 + 2)
    p2 = (b + 1) / (n2 + 2)
    se = math.sqrt(p1 * (1 - p1) / (n1 + 2) + p2 * (1 - p2) / (n2 + 2))
    d = p1 - p2
    return [round(d - 1.959964 * se, 4), round(d + 1.959964 * se, 4)]


def clopper_pearson(x, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if x == 0 else float(beta.ppf(a / 2, x, n - x + 1))
    hi = 1.0 if x == n else float(beta.ppf(1 - a / 2, x + 1, n - x))
    return [lo, hi]


# --------------------------------------------------------------------------------------------------- continuations
KINDS = ('BN', 'BY', 'BX', 'BM', 'BT')


class Growth:
    """A sampled growth (DC 1.4): one start, one law, one sample of its takes, grown to the bounds; with its rosters
    and pairs.  base: the seed without the weighting's token (default DC 1.4's; R0b and R8 give their own)."""

    def __init__(self, stars, spec, sid, i, rounds=ROUNDS, knot_bound=KNOT_BOUND, base=None, pair_rule='sampled'):
        self.spec, self.sid, self.i = spec, sid, i
        self.base = base if base is not None else base_seed(sid, spec, i)
        self.seed = self.base + t2(spec)
        self.rounds, self.knot_bound = rounds, knot_bound
        self.law = spec.law()
        self.G = Grown(start_state(stars), self.law, Sampler(self.seed, spec.weighting), rounds, knot_bound)
        self.rosters = {}
        self.pair_rule = pair_rule
        self.ties = TieCache(self.G.snaps, self.G.records)

    def roster(self, t):
        if t not in self.rosters:
            self.rosters[t] = roster_or_none(self.G.snaps[t])
        return self.rosters[t]

    def pairs(self):
        """{s: ([(X, Y)], ordered pairs before sampling, ordered pairs removed by "wholly apart")}, s = 1..4 and
        s < the last round read (DC 2.2)."""
        out = {}
        for s in range(1, 5):
            if s >= self.G.R:
                break
            R = self.roster(s)
            if R is None:
                out[s] = ([], 0, 0)
                continue
            out[s] = pairs_of_round(self.G.snaps[s], R, self.pair_rule, self.seed, s)
        return out

    def ref(self, s, X, Y, values=True):
        return PairRef(self.G.snaps[s], self.roster(s), X, Y, s, self.spec.knot_law, values)

    def continuation(self, kind, s, X, Y, i):
        """DC 4.1: from the state after round s, under the same law, takes sampled under the growth's weighting."""
        S_s = self.G.snaps[s]
        k2 = kind[:2]          # BN3, BY3, BX3 (DC 4.4's swap at 300) act as BN, BY, BX; the seed keeps the token
        if k2 == 'BY':
            S0 = P.bar_part(S_s, Y)
        elif k2 == 'BX':
            S0 = P.bar_part(S_s, X)
        else:
            S0 = S_s
        mask = None
        if k2 in ('BM', 'BT'):
            mask = pm.Mask('XY', set(X), set(Y))
        seed = cont_seed(self.base, self.spec, kind, s, i)
        G = Grown(S0, self.law, Sampler(seed, self.spec.weighting), self.rounds, self.knot_bound,
                  prefix_snaps=self.G.snaps[:s], prefix_recs=self.G.records[:s], mask=mask,
                  full_mask=(k2 == 'BT'))
        return G, seed
