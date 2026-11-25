"""Shared code of KNOTS-WITHIN-REACH-20261125-001A-E001: paths, the fold study's engine (imported unchanged), the laws,
the seeds, the growth driver, the structure's graphs and the counts.

Written from the frozen texts alone (the drafter's prototype was not seen):
  SD  research/RING-IN-BALANCE-20261123-001/definitions.md          (by line)
  FD  research/PARTS-MEET-AGAIN-20261124-001/definitions.md          (by section.item)
  KD  research/KNOTS-WITHIN-REACH-20261125-001/definitions.md        (by section.item)
  PR  research/KNOTS-WITHIN-REACH-20261125-001A/preregistration.md
Readings taken where the texts leave a choice are numbered in deviations.md of this folder (cited "R n").
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import random
import resource
import sys
import time
from collections import defaultdict, deque

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
ENGINE = os.path.join(ROOT, 'experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
DATA = os.path.join(ROOT, 'research/KNOTS-WITHIN-REACH-20261125-001A')
OUT = os.path.join(ROOT, 'artifacts/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach')
SCRATCH = '/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/7d6e7b9e-634d-564b-a5b8-21bd756b246b/scratchpad/reach_impl'
ENGINE_SHA = {'pm.py': '3aa69b5b96505f24f28640ef483c09d8831440ab7ebfcdc4849785ead818dde7',
              'knots.py': '9138ae86894fed04a5dde1a5af523f36d41ef26567ccb0b6f4aa7488eeadcd45'}


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


for _f, _h in ENGINE_SHA.items():
    assert sha256(os.path.join(ENGINE, _f)) == _h, 'the engine file %s differs from the frozen one' % _f
sys.path.insert(0, ENGINE)
import pm      # noqa: E402  (read-only; never edited)
import knots   # noqa: E402

# KD 7.4: the fold engine's guard multiplied by ten (R 1).  Set at import on the imported module; the file is unchanged.
pm.GUARD.update({'pairs': 200000, 'groups': 200000, 'births': 200000, 'distinctions': 4000000,
                 'incidences': 20000000, 'cliques': 2000000})
KNOT_BOUND = 50000

T0 = time.time()


def cap_memory(gb=6):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def log(*a):
    print('[%8.1fs %6.0fMB]' % (time.time() - T0, peak_mb()), *a, flush=True)


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (set, frozenset, tuple)):
        return list(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def write_json(path, obj):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'wt') as f:
        json.dump(obj, f, sort_keys=True, default=_default)


def read_json(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.load(f)


class JsonlWriter:
    def __init__(self, path):
        self.path = path
        op = gzip.open if path.endswith('.gz') else open
        self.f = op(path, 'at')

    def write(self, obj):
        self.f.write(json.dumps(obj, sort_keys=True, default=_default) + '\n')
        self.f.flush()

    def close(self):
        self.f.close()


def read_jsonl(path):
    op = gzip.open if path.endswith('.gz') else open
    out = []
    if not os.path.exists(path):
        return out
    with op(path, 'rt') as f:
        try:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass       # a line cut by a stopped process
        except EOFError:
            pass                   # a file still being written (or cut): the complete lines read so far
    return out


# ---------------------------------------------------------------------------------------------------------- the data
_CACHE = {}


def census():
    if 'census' not in _CACHE:
        _CACHE['census'] = read_json(os.path.join(DATA, 'census_starts.json'))
    return _CACHE['census']


def named():
    if 'named' not in _CACHE:
        _CACHE['named'] = read_json(os.path.join(DATA, 'named_starts.json'))
    return _CACHE['named']


def five_order():
    if 'five' not in _CACHE:
        _CACHE['five'] = read_json(os.path.join(DATA, 'five_knot_order.json'))
    return _CACHE['five']


def small_census():
    """The 219 three- and four-knot census starts, in file order (file indices)."""
    return [i for i, x in enumerate(census()) if x['n'] in (3, 4)]


def scratch64():
    """The 64 starts of the drafter's runs: random.Random(20261125).sample of the 3,376 census starts in file order
    (PR Known 3); reproduces five_knot_order.json's marks (checked in run 0)."""
    idx = [i for i, x in enumerate(census()) if x['n'] >= 3]
    return set(random.Random(20261125).sample(idx, 64))


def census_stars(i):
    return census()[i]['stars']


def start_stars(key):
    """key: 'census:<i>' or a named start's key or a control's key."""
    if key.startswith('census:'):
        return census_stars(int(key.split(':')[1]))
    N = named()
    if key in N['named_starts']:
        return N['named_starts'][key]
    return N['controls'][key]


def make_start(key):
    return pm.from_stars(start_stars(key))


# ----------------------------------------------------------------------------------------------------------- seeds
def rng_for(start, law, knot_law, cls):
    """KD 2.4: random.Random(n), n = int.from_bytes(sha256('KWR|<start>|<law>|<knot law>|<class>'), 'big')."""
    text = 'KWR|%s|%s|%s|%s' % (start, law, knot_law, cls)
    n = int.from_bytes(hashlib.sha256(text.encode('utf-8')).digest(), 'big')
    return random.Random(n)


def sample_sorted(rng, cands, k):
    """KD 2.3: uniformly without replacement from the candidate list sorted by name."""
    c = sorted(cands)
    if len(c) <= k:
        return list(c)
    return rng.sample(c, k)


# ------------------------------------------------------------------------------------------------------------ laws
# claim section 2 (the table of laws); T1-T4 = Q, MET, STEPS-1, STEPS-2 on CAP-3(RETIRE); T5-T8 the same on
# COPY-LAW(RETIRE); T9, T10 CARRY under OLDEST (R 3).
LAWS = {
    'L0': dict(ration='ORD', treatment='STALL'),
    'L1': dict(ration='CAP-3', treatment='CANCEL-WAIT'),
    'L2': dict(ration='CAP-3', treatment='CANCEL-WAIT', fillers=True),
    'L3': dict(ration='FLOOR1', treatment='CANCEL-RETIRE'),
    'L4': dict(ration='FLOOR1', treatment='CANCEL-OFFSHOOT'),
    'L5': dict(ration='FLOOR1', treatment='CANCEL-WAIT'),
    'L6': dict(ration='CAP-3', treatment='CANCEL-RETIRE'),
    'L7': dict(ration='CAP-3', treatment='CANCEL-OFFSHOOT'),
    'L8': dict(ration='RATION-3', treatment='STALL'),
    'L9': dict(ration='ORD', treatment='CANCEL-RETIRE'),
    'L10': dict(ration='CAP-2', treatment='CANCEL-RETIRE'),
    'L11': dict(ration='CAP-4', treatment='CANCEL-RETIRE'),
}
for _i, _t in enumerate(('Q', 'MET', 'STEPS-1', 'STEPS-2')):
    LAWS['T%d' % (_i + 1)] = dict(ration='CAP-3', treatment='CANCEL-RETIRE', take=_t)
    LAWS['T%d' % (_i + 5)] = dict(ration='FLOOR1', treatment='CANCEL-RETIRE', take=_t)
LAWS['T9'] = dict(ration='CAP-3', treatment='CANCEL-RETIRE', take='CARRY', choice='OLDEST')
LAWS['T10'] = dict(ration='FLOOR1', treatment='CANCEL-RETIRE', take='CARRY', choice='OLDEST')
BASE_OF = {'T1': 'L6', 'T2': 'L6', 'T3': 'L6', 'T4': 'L6', 'T9': 'L6',
           'T5': 'L3', 'T6': 'L3', 'T7': 'L3', 'T8': 'L3', 'T10': 'L3'}
LEMMA_R_TREATMENTS = ('STALL', 'CANCEL-OFFSHOOT', 'CANCEL-RETIRE')


def make_law(label, knot_law='nae', release='RELEASE', choice=None):
    d = dict(LAWS[label])
    d['knot_law'] = knot_law
    d['release'] = release
    d['closing'] = 'IMPLIED'
    if choice is not None:
        d['choice'] = choice
    return pm.Law(**d)


def taking_free(law):
    return law.take is None and law.treatment != 'SHORT-TAKES'


class UniformTakes:
    """KD 7.1: each take chooses uniformly among its candidates (sorted by name), drawn in birth order with one
    random.Random for the run (R 4)."""

    def __init__(self, rng):
        self.rng = rng
        self.draws = 0

    def __call__(self, key, cands):
        self.draws += 1
        return self.rng.choice(cands)


# ------------------------------------------------------------------------------------------------------ the growth
class Grown:
    """One start grown under one law, in place, round by round, keeping per-round records (no snapshots).
    Stops: ended (stalled, stopped, jammed: SD lines 83-84), 'knots' (the first round leaving more than the knot bound),
    'guard' (KD 7.4; the round is not read and is rolled back), 'rounds' (the bound on rounds)."""

    def __init__(self, start_key, law, rounds, knot_bound=KNOT_BOUND, ctx=None, on_round=None, S=None,
                 parts_every_round=True):
        self.start_key = start_key
        self.law = law
        self.S = S if S is not None else make_start(start_key)
        self.ctx = ctx or {}
        self.rounds_asked = rounds
        self.knot_bound = knot_bound
        self.recs = []                 # compact per-round records, index t-1 for round t
        self.n_knots = [self.S.n_knots]          # after round t, index t
        self.n_dist = [self.S.n_distinctions]
        self.members = [sorted(u for u, _, _ in pm.live_members(self.S))]   # members after round t
        self.parts = [parts_of(self.S, self.members[0])] if parts_every_round else None
        self.parts_every_round = parts_every_round
        self.retired = set()
        self.stop = None
        self.guard = None
        self.ended = None              # 'stalled' | 'stopped' | 'jammed'
        self.parity_closing_round = None   # Settled 4 / R 9: first round with a birth taking every loose, none barred
        self.on_round = on_round
        self.grow_to(rounds)

    def grow_to(self, rounds):
        S = self.S
        while self.stop is None and S.round < rounds:
            N, Dn = S.n_knots, S.n_distinctions
            barred = list(S.barred)
            cand = set(S.cand)
            loose_total = 0
            any_barred = False
            for d in range(Dn):
                if len(S.holders[d]) == 1:
                    loose_total += 1
                    if S.barred[d]:
                        any_barred = True
            try:
                rec = pm.round_step(S, self.law, self.ctx)
            except pm.GuardStop as g:
                rollback(S, N, Dn, barred, cand)
                self.stop = 'guard'
                self.guard = {'round': S.round + 1, 'what': g.what, 'value': g.value, 'where': g.where}
                break
            t = S.round
            births = rec['births']
            close = False
            if not any_barred:
                for b in births:
                    if len(set(b['inputs'])) == loose_total and all(len(S.holders[d]) >= 2 for d in b['inputs']):
                        close = True
            if close and self.parity_closing_round is None:
                self.parity_closing_round = t
            self.retired.update(rec['retired'])
            mem = sorted(u for u, _, _ in pm.live_members(S))
            prev_parts = self.parts[-1] if self.parts_every_round else None
            self.members.append(mem)
            if self.parts_every_round:
                self.parts.append(parts_of(S, mem))
            # births by part of the roster before the round (the part holding the birth's parents)
            bpart = None
            if prev_parts is not None:
                pidx = {}
                for i, P in enumerate(prev_parts):
                    for u in P:
                        pidx[u] = i
                cnt = defaultdict(int)
                for b in births:
                    cnt[pidx.get(b['parents'][0], -1)] += 1
                bpart = sorted(cnt.values(), reverse=True)
            self.recs.append({'round': t, 'births': len(births), 'joins': rec['n_joins'],
                              'offshoots': rec['n_offshoots'], 'short': len(rec['short']),
                              'retired': len(rec['retired']), 'waiting': len(rec['waiting']),
                              'stalled': rec['stalled'], 'closing_parity': close, 'births_by_part': bpart,
                              'n_takes': rec.get('n_takes', 0)})
            self.n_knots.append(S.n_knots)
            self.n_dist.append(S.n_distinctions)
            if self.on_round is not None:
                self.on_round(self, rec)
            if rec['stalled']:
                self.ended = 'stalled'
            elif rec['stopped']:
                self.ended = 'stopped'
            elif rec['jammed']:
                self.ended = 'jammed'
            if self.ended:
                self.stop = 'ended'
                break
            if S.n_knots > self.knot_bound:
                self.stop = 'knots'
                break
        if self.stop is None and S.round >= rounds:
            self.stop_at_rounds = True
        return self

    @property
    def rounds_done(self):
        return self.S.round

    def births(self):
        return [r['births'] for r in self.recs]

    def reached(self, t):
        """Whether the structure after round t exists in this run (t <= the last round read)."""
        return t <= self.S.round

    def resume(self, rounds):
        if self.stop in ('rounds', None) or (self.stop is None):
            self.stop = None
        if self.stop is None:
            self.grow_to(rounds)
        return self


def rollback(S, N, Dn, barred, cand):
    """Undo a round that a guard stopped after it had begun to change S (FD's engine raises after appending the new
    knots in the demand step or the fresh-distinction guard)."""
    for x in range(N, len(S.places)):
        for d in S.places[x]:
            if d < len(S.holders):
                S.holders[d] = [w for w in S.holders[d] if w < N]
    del S.places[N:]
    del S.parents[N:]
    del S.made[N:]
    del S.kind[N:]
    del S.holders[Dn:]
    S.barred[:] = barred[:Dn]
    S.cand = set(cand)
    S._lev = {k: v for k, v in S._lev.items() if k[0] < N}
    S.span = pm.build_span(S)


# ------------------------------------------------------------------------------------------- roster: met sets, parts
def met_sets(S, members, upto=None):
    """{w: frozenset of members other than w that w meets}, for knots w < upto whose met set has >= 2 members
    (SD lines 25-26, FD 1.3), read in the structure of the knots < upto (default: all)."""
    mset = set(members)
    N = S.n_knots if upto is None else upto
    raw = defaultdict(set)
    for u in members:
        for d in S.places[u]:
            for w in S.holders[d]:
                if w != u and w < N:
                    raw[w].add(u)
    return {w: frozenset(m) for w, m in raw.items() if len(m) >= 2}


def parts_of(S, members, upto=None, ms=None):
    """The parts: components of joinable among the members (SD lines 27-28)."""
    if ms is None:
        ms = met_sets(S, members, upto)
    par = {u: u for u in members}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for M in ms.values():
        it = iter(M)
        a = find(next(it))
        for b in it:
            rb = find(b)
            if rb != a:
                par[rb] = a
    comp = defaultdict(list)
    for u in members:
        comp[find(u)].append(u)
    return sorted(tuple(sorted(c)) for c in comp.values())


def past_its_start(S, members, upto=None):
    """SD line 28: no member meets a member."""
    mset = set(members)
    N = S.n_knots if upto is None else upto
    for u in members:
        for d in S.places[u]:
            for w in S.holders[d]:
                if w != u and w < N and w in mset:
                    return False
    return True


def witnessed_graph(S, members, upto=None, ms=None):
    """Bipartite graph members <-> met sets; ws(u, v) = half the distance (KD 1.4)."""
    if ms is None:
        ms = met_sets(S, members, upto)
    idx = {u: i for i, u in enumerate(members)}
    rows, cols = [], []
    k = len(members)
    for j, (w, M) in enumerate(sorted(ms.items())):
        for u in M:
            rows.append(idx[u])
            cols.append(k + j)
    n = k + len(ms)
    G = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n, n))
    return G, idx


def ws_from(S, members, sources, upto=None, ms=None):
    """{source: array of ws to every member (index order of `members`), inf between parts}."""
    G, idx = witnessed_graph(S, members, upto, ms)
    if not sources:
        return {}, idx
    D = shortest_path(G, method='D', directed=False, unweighted=True, indices=[idx[s] for s in sources])
    D = D[:, :len(members)] / 2.0
    return {s: D[i] for i, s in enumerate(sources)}, idx


# ------------------------------------------------------------------------------------------------- holder steps
class Graphs:
    """The holder graph (KD 1.1) and the parent graph (KD 1.2) of the structure of the knots < N (the structure after
    the round that made knot N - 1: knots are named in birth order and places are fixed at birth)."""

    def __init__(self, S, N=None):
        self.S = S
        self.N = S.n_knots if N is None else N
        N = self.N
        self.made = np.array(S.made[:N], dtype=np.int32)
        # incidences of distinctions held by two or more knots < N
        k_rows, d_cols = [], []
        two_rows, two_cols = [], []
        self.max_holders = 1
        dmap = {}
        for d, hs in enumerate(S.holders):
            hh = [w for w in hs if w < N]
            if len(hh) >= 2:
                if len(hh) > self.max_holders:
                    self.max_holders = len(hh)
                j = dmap.setdefault(d, len(dmap))
                for w in hh:
                    k_rows.append(w)
                    d_cols.append(j)
                if len(hh) == 2:
                    two_rows.append(hh[0])
                    two_cols.append(hh[1])
        self.n_shared = len(dmap)
        self.dmap = dmap
        self.k_rows = np.array(k_rows, dtype=np.int64)
        self.d_cols = np.array(d_cols, dtype=np.int64)
        self.two_holders = (self.max_holders <= 2)
        if self.two_holders:
            r = np.array(two_rows, dtype=np.int64)
            c = np.array(two_cols, dtype=np.int64)
            self.knot_graph = csr_matrix((np.ones(len(r), dtype=np.int8), (r, c)), shape=(N, N))
        else:
            self.knot_graph = None
        n = N + self.n_shared
        self.bip = csr_matrix((np.ones(len(k_rows), dtype=np.int8), (self.k_rows, N + self.d_cols)), shape=(n, n))
        pr, pc = [], []
        for x in range(N):
            for p in S.parents[x]:
                pr.append(x)
                pc.append(p)
        self.parent_graph = csr_matrix((np.ones(len(pr), dtype=np.int8), (pr, pc)), shape=(N, N))

    def hs(self, sources, batch=64):
        """Holder steps from each source to every knot < N (float array, inf when no path)."""
        out = {}
        for i in range(0, len(sources), batch):
            src = list(sources[i:i + batch])
            if self.two_holders:
                D = shortest_path(self.knot_graph, method='D', directed=False, unweighted=True, indices=src)
            else:
                D = shortest_path(self.bip, method='D', directed=False, unweighted=True, indices=src)
                D = D[:, :self.N] / 2.0
            for s, row in zip(src, D):
                out[s] = row
        return out

    def ps(self, sources, batch=64):
        out = {}
        for i in range(0, len(sources), batch):
            src = list(sources[i:i + batch])
            D = shortest_path(self.parent_graph, method='D', directed=False, unweighted=True, indices=src)
            for s, row in zip(src, D):
                out[s] = row
        return out

    def hs_not_through(self, sources, blocked):
        """Holder steps where knots in `blocked` are counted, not stepped through (the retired-knot swap of run 2).
        A source is always stepped out of.  Python BFS on the two-holder knot graph or the bipartite graph."""
        blocked = set(blocked)
        S = self.S
        N = self.N
        out = {}
        for s in sources:
            dist = np.full(N, np.inf)
            dist[s] = 0
            q = deque([s])
            while q:
                x = q.popleft()
                if x != s and x in blocked:
                    continue
                dx = dist[x]
                for d in S.places[x]:
                    for w in S.holders[d]:
                        if w < N and dist[w] == np.inf:
                            dist[w] = dx + 1
                            q.append(w)
            out[s] = dist
        return out

    def steps_from_start(self, n_start):
        """s(u) = least hs(u, c) over start knots c (KD 1.3)."""
        D = self.hs(list(range(n_start)))
        return np.min(np.vstack([D[c] for c in range(n_start)]), axis=0)


def counts_from(dist, upto):
    """H(r) for r = 0 .. upto from a distance row: the number of knots with hs <= r."""
    fin = dist[np.isfinite(dist)]
    fin = fin[fin <= upto].astype(np.int64)
    c = np.bincount(fin, minlength=upto + 1)[:upto + 1]
    return [int(x) for x in np.cumsum(c)]


def greatest(dist):
    fin = dist[np.isfinite(dist)]
    return int(fin.max()) if len(fin) else 0
