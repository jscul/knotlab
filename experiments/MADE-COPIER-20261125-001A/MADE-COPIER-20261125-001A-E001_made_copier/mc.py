"""Engine of MADE-COPIER-20261125-001A: the readings of "two of it", written from the frozen text.

  P  research/MADE-COPIER-20261125-001A/preregistration.md     D  research/MADE-COPIER-20261125-001/definitions.md
  FD research/PARTS-MEET-AGAIN-20261124-001/definitions.md     SD research/RING-IN-BALANCE-20261123-001/definitions.md
Readings taken where the text leaves a choice are numbered in deviations.md of this folder (cited R n).

The growth is the fold study's engine (pm.py, knots.py, paired.py of PARTS-MEET-AGAIN-20261124-001A-E001), imported
unchanged.  What is new here: starts and renamings from starts.json; descents (D 2.6); tie classes (D 3.3); the three
readings (D 3.1 to 3.3); the paired runs of D 4; the owner's arm (D 7).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
FOLD = os.path.join(ROOT, 'experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
DATA = os.path.join(ROOT, 'research/MADE-COPIER-20261125-001A')
OUT = os.path.join(ROOT, 'artifacts/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier')
FOLD_SHA = {'pm.py': '3aa69b5b96505f24f28640ef483c09d8831440ab7ebfcdc4849785ead818dde7'}

sys.path.insert(0, FOLD)
import knots as K  # noqa: E402
import paired as P  # noqa: E402
import pm  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

with open(os.path.join(DATA, 'starts.json')) as _f:
    STARTS = json.load(_f)

ROUNDS = 6
KNOT_BOUND = 500


def fold_hashes():
    out = {}
    for fn in ('pm.py', 'knots.py', 'paired.py'):
        with open(os.path.join(FOLD, fn), 'rb') as f:
            out[fn] = hashlib.sha256(f.read()).hexdigest()
    return out


# ------------------------------------------------------------------------------------------------------------ laws
T3 = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
TS = {'CANCEL-RETIRE': 'RETIRE', 'CANCEL-OFFSHOOT': 'OFFSHOOT', 'CANCEL-WAIT': 'WAIT'}


def base_kw(base):
    """'COPY-LAW(RETIRE)', 'CAP-3(WAIT)', 'FBP(OFFSHOOT)', 'FLOOR0(RETIRE)', 'ONE-FEWER(WAIT)' -> Law kwargs."""
    nm, t = base.split('(')
    t = 'CANCEL-' + t.rstrip(')')
    ration = {'COPY-LAW': 'FLOOR1', 'CAP-3': 'CAP-3', 'FBP': 'FLOOR1', 'FLOOR0': 'FLOOR0',
              'ONE-FEWER': 'ONE-FEWER'}[nm]
    kw = dict(ration=ration, treatment=t)
    if nm == 'FBP':
        kw['fresh_by_parents'] = True
    return kw


BASES_COPY = ['COPY-LAW(%s)' % TS[t] for t in T3]
BASES_CAP3 = ['CAP-3(%s)' % TS[t] for t in T3]
BASES_FBP = ['FBP(%s)' % TS[t] for t in T3]
NINE = BASES_COPY + BASES_CAP3 + BASES_FBP
RULES = ('OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT')


def make_law(base, take=None, choice='OLDEST', knot_law='parity', **extra):
    kw = base_kw(base)
    if take:
        kw['take'] = take
        kw['choice'] = choice
    kw.update(extra)
    return pm.Law(knot_law=knot_law, **kw)


# ---------------------------------------------------------------------------------------------------------- starts
class Design:
    __slots__ = ('name', 'stars', 'X', 'Y', 's', 'barred', 'family', 'Z', 'renaming', 'label_map')

    def __init__(self, name, stars, X, Y, s, barred=(), family=None, Z=None, renaming=None):
        self.name, self.stars, self.X, self.Y, self.s = name, stars, list(X), list(Y), s
        self.barred, self.family, self.Z, self.renaming = list(barred), family, (list(Z) if Z else None), renaming

    def start(self):
        return build_start(self.stars, self.renaming, self.barred, self.name)


def build_start(stars, renaming=None, barred_labels=(), design=None):
    """D 4.5: a renaming changes names only (n1: names reversed; n2, n3, n4: label maps of starts.json)."""
    if renaming in (None, 'n0'):
        S = pm.from_stars(stars)
    elif renaming == 'n1':
        S = pm.from_stars(stars, reverse_names=True)
    else:
        m = STARTS['renamings'][design][renaming]
        S = pm.from_stars([[m[str(l)] for l in k] for k in stars])
    for lab in barred_labels:
        if renaming not in (None, 'n0', 'n1'):
            lab = STARTS['renamings'][design][renaming][str(lab)]
        S.barred[S.labels.index(lab)] = True
    return S


def family_of(name):
    if name.startswith('made'):
        return 'made'
    if name.startswith('ystart'):
        return 'ystart'
    return 'other'


def design(name, renaming=None):
    d = STARTS['designs'][name]
    return Design(name, d['stars'], d['X'], d['Y'], d['s'], family=family_of(name), renaming=renaming)


DESIGNS_MADE = ['made-2', 'made-3', 'made-4', 'made-5', 'made-6']
KINDS = ['one-2', 'one-3', 'two-22', 'two-23', 'two-33', 'three-222']
DESIGNS_YSTART = ['ystart-' + k for k in KINDS]
CLASS_MADE = ['made-3', 'made-4', 'made-5', 'made-6']
CLASS_START = ['ystart-one-2', 'ystart-one-3', 'ystart-two-23', 'ystart-two-33', 'ystart-three-222']
RUN2_DESIGNS = DESIGNS_MADE + ['made-2-exchanged'] + DESIGNS_YSTART


def renamings_for(name):
    """D 4.5: n1, n3, n4 on the made designs; n1 to n4 on the others."""
    keys = list(STARTS['renamings'][name].keys())
    return [k for k in ('n1', 'n2', 'n3', 'n4') if k in keys]


def alone(name, which):
    """D 4.6: 'X alone' or 'Y alone'."""
    a = STARTS['alone'][name][which]
    key = 'X' if which == 'X alone' else 'Y'
    pat = a.get('X') if which == 'X alone' else a.get('Y')
    if which == 'X alone':
        return Design(name + '|X alone', a['stars'], a['X'], [], a['s'], barred=a['barred'], family='alone')
    return Design(name + '|Y alone', a['stars'], [], a['Y'], a['s'], barred=a['barred'], family='alone')


def third(kind_y, kind_z, where):
    """D 7.8: ystart-<kind_y> followed by Z's knots of kind_z named before Y ('before') or after ('after')."""
    base = STARTS['designs']['ystart-' + kind_y]
    key = [k for k in STARTS['third pattern']['knots'][kind_z] if k.startswith('Z named ' + where)][0]
    zk = STARTS['third pattern']['knots'][kind_z][key]
    stars = base['stars'] + zk
    n0 = len(base['stars'])
    Z = list(range(n0 + 1, n0 + len(zk)))
    return Design('ystart-%s|Z=%s %s' % (kind_y, kind_z, where), stars, base['X'], base['Y'], 0, family='third', Z=Z)


# ------------------------------------------------------------------------------------------------------------ runs
def grow(design_or_start, law, rounds=ROUNDS, knot_bound=KNOT_BOUND, ctx=None, records=None, snapshots=None,
         on_round=None):
    S0 = design_or_start.start() if isinstance(design_or_start, Design) else design_or_start
    return pm.Run(S0, law, rounds=rounds, knot_bound=knot_bound, ctx=ctx, records=records, snapshots=snapshots,
                  on_round=on_round)


def run_from_state(A, s, S_mod, law=None, ctx=None, rounds=None):
    """A comparison run from run A's structure after round s (modified), the same law and bounds (FD 5.1)."""
    r = pm.Run(S_mod, law or A.law, rounds=rounds or A.rounds_asked, knot_bound=A.knot_bound, ctx=ctx,
               records=A.records[:s], snapshots=A.snap[:s])
    return r


# --------------------------------------------------------------------------------------------------------- descent
def descent_map(S, X, Y, s):
    """D 2.6: every knot's descent: 'X only', 'Y only', 'both', 'neither'."""
    xd = P.side_of(S, X, s) if X else set()
    yd = P.side_of(S, Y, s) if Y else set()
    Xs, Ys = set(X), set(Y)
    out = {}
    for u in range(S.n_knots):
        if S.made[u] <= s and S.kind[u] != 'placed':
            out[u] = 'X only' if u in Xs else ('Y only' if u in Ys else 'neither')
        else:
            a, b = u in xd, u in yd
            out[u] = 'both' if (a and b) else ('X only' if a else ('Y only' if b else 'neither'))
    return out


def made_by_x(desc_pair):
    return any(x in ('X only', 'both') for x in desc_pair)


# ------------------------------------------------------------------------------------------------------------ ties
def parity_coords(S):
    """For every distinction d, its coordinate vector over a basis of the allowed states (kernel of H), as an int over
    the free columns: equal vectors <=> tied (equal in every allowed state); zero <=> frozen."""
    piv_rows = {}
    for u in S.knots():
        v = 0
        for d in S.places[u]:
            v |= 1 << d
        for p_, r in piv_rows.items():
            if (v >> p_) & 1:
                v ^= r
        if not v:
            continue
        p_ = (v & -v).bit_length() - 1
        for q in list(piv_rows):
            r = piv_rows[q]
            if (r >> p_) & 1:
                piv_rows[q] = r ^ v
        piv_rows[p_] = v
    coords = []
    for d in range(S.n_distinctions):
        if not S.holders[d]:
            coords.append(None)
            continue
        r = piv_rows.get(d)
        coords.append((1 << d) if r is None else (r ^ (1 << d)))
    return coords


class Ties:
    """Tie classes of a structure under a knot law.  cls[d] = class id (None if d is in no class of two or more and
    not frozen); sign[d] = 0 or 1 relative to the class representative (parity: always 0); frozen: set; unsat."""

    __slots__ = ('cls', 'sign', 'frozen', 'unsat', 'classes')

    def __init__(self):
        self.cls, self.sign, self.frozen, self.unsat, self.classes = {}, {}, set(), False, []

    def tied(self, a, b):
        return a in self.cls and b in self.cls and self.cls[a] == self.cls[b]

    def members(self, d):
        c = self.cls.get(d)
        return [] if c is None else self.classes[c]


def ties_parity(S):
    T = Ties()
    coords = parity_coords(S)
    groups = defaultdict(list)
    for d, c in enumerate(coords):
        if c is None:
            continue
        if c == 0:
            T.frozen.add(d)
        else:
            groups[c].append(d)
    for ds in groups.values():
        if len(ds) >= 2:
            cid = len(T.classes)
            T.classes.append(sorted(ds))
            for d in ds:
                T.cls[d] = cid
                T.sign[d] = 0
    return T


def ties_nae(S, seed=0, n_samples=24, per_pass=64):
    """Sampled allowed states give candidate classes; every claimed tie is confirmed by a solver (R 6; deviations 40,
    43, 45: at most `per_pass` separating states are added before the classes are formed again, and every solver call
    is made under random phases so that the states found differ; the loop ends only on a pass in which the solver
    confirms every claim, so the partition and the signs do not depend on the sampling)."""
    T = Ties()
    nd = S.n_distinctions
    ds = [d for d in range(nd) if S.holders[d]]
    sat = Solver(name='minisat22')
    try:
        for u in S.knots():
            vs = [d + 1 for d in S.places[u]]
            sat.add_clause(vs)
            sat.add_clause([-v for v in vs])
        if not sat.solve():
            T.unsat = True
            return T
        rng = random.Random(seed)

        def phases():
            sat.set_phases([(d + 1) if rng.random() < 0.5 else -(d + 1) for d in ds])

        def model_bits(m):
            arr = bytearray(nd)
            for x in m:
                if 0 < x <= nd:
                    arr[x - 1] = 1
            return arr
        s0 = model_bits(sat.get_model())
        sig = dict.fromkeys(ds, 0)
        count = [1]

        def add(sample):
            bit = 1 << count[0]
            for d in ds:
                if sample[d] != s0[d]:
                    sig[d] |= bit
            count[0] += 1
        for _ in range(n_samples - 1):
            k = 3
            while k >= 0:
                assum = [(d + 1) * (1 if rng.random() < 0.5 else -1) for d in rng.sample(ds, min(k, len(ds)))]
                phases()
                if sat.solve(assumptions=assum):
                    add(model_bits(sat.get_model()))
                    break
                k -= 1
        while True:
            groups = defaultdict(list)
            for d in ds:
                groups[sig[d]].append(d)
            claims = []
            for g, members in groups.items():
                if len(members) < 2:
                    continue
                r = members[0]
                for m in members[1:]:
                    claims.append((r, m, s0[m] ^ s0[r]))      # 0: claimed equal, 1: claimed unequal
            new = []
            for r, m, rel in claims:
                if any((x[r] ^ x[m]) != rel for x in new):
                    continue
                # equal claimed: is there a state with x_r = 1, x_m = 0?  unequal: x_r = 1, x_m = 1?  (by the
                # symmetry of flipping every distinction one check is enough)
                assum = [r + 1, -(m + 1)] if rel == 0 else [r + 1, m + 1]
                phases()
                if sat.solve(assumptions=assum):
                    new.append(model_bits(sat.get_model()))
                    if len(new) >= per_pass:
                        break
            if not new:
                break
            for x in new:
                add(x)
        for g, members in groups.items():
            if len(members) >= 2:
                cid = len(T.classes)
                T.classes.append(sorted(members))
                for m in members:
                    T.cls[m] = cid
                    T.sign[m] = s0[m] ^ s0[members[0]]
    finally:
        sat.delete()
    return T


def ties(S, knot_law, seed=0):
    return ties_parity(S) if knot_law == 'parity' else ties_nae(S, seed)


def ties_brute(S, knot_law):
    """Every assignment (small structures): tie classes as frozensets of distinctions, frozen set, unsat."""
    ds = [d for d in range(S.n_distinctions) if S.holders[d]]
    allowed = _brute_allowed(S, knot_law)
    if not allowed:
        return None
    frozen = {d for d in ds if all(((a >> d) & 1) == ((allowed[0] >> d) & 1) for a in allowed)}
    cls = []
    seen = set()
    for i, a in enumerate(ds):
        if a in seen or a in frozen:
            continue
        group = [a]
        for b in ds[i + 1:]:
            if b in frozen or b in seen:
                continue
            rel = {((x >> a) & 1) ^ ((x >> b) & 1) for x in allowed}
            if len(rel) == 1:
                group.append(b)
        if len(group) >= 2:
            seen.update(group)
            cls.append(frozenset(group))
    return {'classes': set(cls), 'frozen': frozen}


def _brute_allowed(S, knot_law):
    D = S.n_distinctions
    rows = []
    for u in S.knots():
        r = 0
        for d in S.places[u]:
            r |= 1 << d
        rows.append(r)
    out = []
    for a in range(1 << D):
        ok = True
        for r in rows:
            x = a & r
            if knot_law == 'parity':
                if bin(x).count('1') & 1:
                    ok = False
                    break
            elif x == 0 or x == r:
                ok = False
                break
        if ok:
            out.append(a)
    return out


# ------------------------------------------------------------------------------------------------- the readings
def places_of(S, knots_):
    out = set()
    for u in knots_:
        out.update(S.places[u])
    return out


def y_knots(S, Y):
    """D 2.4: Y's members and every knot that holds a place of a member."""
    out = set(Y)
    for u in Y:
        for d in S.places[u]:
            out.update(S.holders[d])
    return sorted(out)


class Reference:
    """Y as it was after round s, for the three readings."""

    def __init__(self, S_s, R_s, members, s, X=None):
        self.S_s, self.R_s, self.members, self.s = S_s, R_s, sorted(members), s
        self.knots = y_knots(S_s, members)
        self.places = sorted(places_of(S_s, members))
        self.graph = P.roster_graph(R_s, self.members)
        import networkx as nx
        self.wl = nx.weisfeiler_lehman_graph_hash(self.graph, node_attr='c')
        self.inv = (len(self.members), tuple(sorted((R_s.h[u], R_s.k[u]) for u in self.members)),
                    self.graph.number_of_edges())
        self.X = sorted(X) if X else []
        self.x_places = sorted(places_of(S_s, self.X)) if X else []
        self.built = BuiltPattern(S_s, self.knots, s)


def same_as(ref, R_t, part):
    """SD lines 29-30: a renaming of members carrying h, k and the maximal met sets (via paired.roster_graph)."""
    import networkx as nx
    if len(part) != len(ref.members):
        return False
    hk = tuple(sorted((R_t.h[u], R_t.k[u]) for u in part))
    if hk != ref.inv[1]:
        return False
    G = P.roster_graph(R_t, part)
    if G.number_of_edges() != ref.inv[2] or G.number_of_nodes() != ref.graph.number_of_nodes():
        return False
    if nx.weisfeiler_lehman_graph_hash(G, node_attr='c') != ref.wl:
        return False
    return nx.is_isomorphic(G, ref.graph, node_match=lambda a, b: a['c'] == b['c'])


def form_reading(ref, S_t, R_t, desc):
    """D 3.1: parts the same as Y containing a member made after round s, with their members' descents."""
    out = []
    for i, part in enumerate(R_t.parts):
        if not any(S_t.made[u] > ref.s or S_t.kind[u] == 'placed' for u in part):
            continue
        if same_as(ref, R_t, part):
            ds = Counter(desc.get(u, 'neither') for u in part)
            kind_ = next(iter(ds)) if len(ds) == 1 else 'mixed'
            out.append({'part': list(part), 'descent': kind_, 'descents': dict(ds)})
    return out


def form_summary(parts):
    c = Counter(p['descent'] for p in parts)
    return {'n': len(parts), 'by_descent': dict(c), 'two_made_by_X': c.get('X only', 0) >= 2}


# ---------------------------------------------------------------------------------------- built structure (D 3.2)
class BuiltPattern:
    """Y's knots with their places as they were after round s."""

    def __init__(self, S, knots_, s):
        self.knots = list(knots_)
        self.idx = {u: i for i, u in enumerate(self.knots)}
        kset = set(self.knots)
        self.places = sorted(places_of(S, self.knots))
        self.nplaces = [len(S.places[u]) for u in self.knots]
        # per place: (frozenset of pattern-knot indices holding it, outside holder?, loose?, barred?)
        self.key = {}
        for d in self.places:
            inside = frozenset(self.idx[w] for w in S.holders[d] if w in kset)
            outside = any(w not in kset for w in S.holders[d])
            loose = len(S.holders[d]) == 1
            self.key[d] = (inside, outside, loose, bool(S.barred[d]) and loose)
        self.multiset = Counter(self.key.values())
        # knot signatures: (number of places, loose places, barred loose places)
        self.sig = []
        for u in self.knots:
            lo = sum(1 for d in S.places[u] if len(S.holders[d]) == 1)
            ba = sum(1 for d in S.places[u] if len(S.holders[d]) == 1 and S.barred[d])
            self.sig.append((len(S.places[u]), lo, ba))
        # pairwise shared places
        self.shared = {}
        for i, u in enumerate(self.knots):
            for j, w in enumerate(self.knots):
                if i < j:
                    self.shared[(i, j)] = len(set(S.places[u]) & set(S.places[w]))
        # an order in which every knot after the first shares a place with an earlier one
        order = [0]
        rest = set(range(1, len(self.knots)))
        while rest:
            nxt = None
            for j in sorted(rest):
                if any(self.shared[(min(i, j), max(i, j))] for i in order):
                    nxt = j
                    break
            if nxt is None:
                nxt = min(rest)
            order.append(nxt)
            rest.discard(nxt)
        self.order = order


def find_renamings(pat, S, candidates, mode='two', limit=10000):
    """D 3.2: connected sets K' of candidate knots carried onto the pattern's knots by a renaming (phi on knots, psi
    on places keeping incidence; per place: holders inside, a holder outside, loose, barred).  mode 'two': stop at two
    sets with no common knot or at `limit` distinct sets; 'count': count distinct sets up to `limit`.
    Returns {'sets': [...], 'bound_hit': bool, 'disjoint_pair': (a, b) or None, 'share_no_place': bool or None}."""
    cand = set(candidates)
    n = len(pat.knots)
    sig_of = {}
    for x in cand:
        lo = sum(1 for d in S.places[x] if len(S.holders[d]) == 1)
        ba = sum(1 for d in S.places[x] if len(S.holders[d]) == 1 and S.barred[d])
        sig_of[x] = (len(S.places[x]), lo, ba)
    by_sig = defaultdict(list)
    for x in sorted(cand):
        by_sig[sig_of[x]].append(x)
    found = []
    found_set = set()
    state = {'bound': False, 'pair': None}
    phi = [None] * n
    used = set()

    def neighbours(x):
        out = set()
        for d in S.places[x]:
            out.update(S.holders[d])
        out.discard(x)
        return out

    def check_full():
        kset = set(phi)
        inv = {x: i for i, x in enumerate(phi)}
        ms = Counter()
        pls = set()
        for x in phi:
            pls.update(S.places[x])
        for d in pls:
            inside = frozenset(inv[w] for w in S.holders[d] if w in kset)
            outside = any(w not in kset for w in S.holders[d])
            loose = len(S.holders[d]) == 1
            ms[(inside, outside, loose, bool(S.barred[d]) and loose)] += 1
        return ms == pat.multiset

    def rec(k):
        if state['bound'] or state['pair'] is not None:
            return
        if k == n:
            if check_full():
                fs = frozenset(phi)
                if fs not in found_set:
                    found_set.add(fs)
                    found.append(fs)
                    if mode == 'two':
                        for g in found[:-1]:
                            if not (g & fs):
                                state['pair'] = (g, fs)
                                return
                    if len(found) >= limit:
                        state['bound'] = True
            return
        i = pat.order[k]
        if k == 0:
            pool = by_sig.get(pat.sig[i], [])
        else:
            # must share places with the images of the earlier knots it shares places with
            prev = [j for j in pat.order[:k] if pat.shared[(min(i, j), max(i, j))]]
            if prev:
                pool = None
                for j in prev:
                    nb = neighbours(phi[j]) & cand
                    pool = nb if pool is None else (pool & nb)
                pool = sorted(x for x in (pool or ()) if sig_of[x] == pat.sig[i])
            else:
                pool = by_sig.get(pat.sig[i], [])
        for x in pool:
            if x in used:
                continue
            ok = True
            px = set(S.places[x])
            for j in pat.order[:k]:
                if len(px & set(S.places[phi[j]])) != pat.shared[(min(i, j), max(i, j))]:
                    ok = False
                    break
            if not ok:
                continue
            phi[i] = x
            used.add(x)
            rec(k + 1)
            used.discard(x)
            phi[i] = None
            if state['bound'] or state['pair'] is not None:
                return
    rec(0)
    pair = state['pair']
    share = None
    if pair is not None:
        a, b = pair
        share = not (places_of(S, a) & places_of(S, b))
    return {'sets': [sorted(x) for x in found], 'n': len(found), 'bound_hit': state['bound'],
            'disjoint_pair': [sorted(pair[0]), sorted(pair[1])] if pair else None, 'share_no_place': share}


def renamings_brute(pat, S, candidates):
    """Every injective map of the pattern's knots into the candidates (small cases): the distinct knot sets carried
    onto the pattern's knots (D 3.2's conditions, connectedness of the set included)."""
    import itertools
    n = len(pat.knots)
    cand = sorted(candidates)
    out = set()
    for img in itertools.permutations(cand, n):
        kset = set(img)
        inv = {x: i for i, x in enumerate(img)}
        pls = set()
        for x in img:
            pls.update(S.places[x])
        ms = Counter()
        for d in pls:
            inside = frozenset(inv[w] for w in S.holders[d] if w in kset)
            outside = any(w not in kset for w in S.holders[d])
            loose = len(S.holders[d]) == 1
            ms[(inside, outside, loose, bool(S.barred[d]) and loose)] += 1
        if ms == pat.multiset and all(len(S.places[img[i]]) == pat.nplaces[i] for i in range(n)):
            out.add(frozenset(img))
    # connected sets only (the pattern's knots are connected, so an incidence-preserving image is too)
    return out


def built_reading(ref, S_t, desc, mode='two'):
    made = [u for u in range(S_t.n_knots) if (S_t.made[u] > ref.s or S_t.kind[u] == 'placed')
            and u not in S_t.removed]
    res = find_renamings(ref.built, S_t, made, mode=mode)
    res['descents'] = [dict(Counter(desc.get(u, 'neither') for u in st)) for st in res['sets'][:20]]
    if res['disjoint_pair']:
        a, b = res['disjoint_pair']
        res['pair_descents'] = [dict(Counter(desc.get(u) for u in a)), dict(Counter(desc.get(u) for u in b))]
        res['two_made_by_X'] = all(desc.get(u) == 'X only' for u in a + b)
    else:
        res['two_made_by_X'] = False
    return res


# ------------------------------------------------------------------------------------------------ values (D 3.3)
def eligible_places(ref, ties_s, of='Y'):
    """Places v of the pattern (Y, or X for P9) free and tied to no place of the other pattern after round s."""
    own = ref.places if of == 'Y' else ref.x_places
    other = set(ref.x_places if of == 'Y' else ref.places)
    out = []
    for v in own:
        if v in ties_s.frozen:
            continue
        if any(ties_s.tied(v, w) for w in other):
            continue
        out.append(v)
    return out


def values_reading(ref, S_t, ties_t, desc, eligible, nd_s):
    """Two usable loose made distinctions tied to one eligible place v (made = a fresh distinction of a knot made after
    round s: name >= nd_s, the number of distinctions after round s)."""
    cases = []
    for v in eligible:
        mem = ties_t.members(v)
        if not mem:
            continue
        made = [d for d in mem if d >= nd_s]
        if not made:
            continue
        ul = [d for d in made if len(S_t.holders[d]) == 1 and not S_t.barred[d]]
        other = [d for d in made if d not in ul]
        if len(ul) >= 2:
            dd = {d: desc.get(S_t.holders[d][0], 'neither') for d in ul}
            cases.append({'v': v, 'two': ul, 'descents': [dd[d] for d in ul],
                          'made_by_X': made_by_x(list(dd.values())),
                          'by_Y_only': all(x == 'Y only' for x in dd.values()),
                          'signs': [ties_t.sign.get(d, 0) ^ ties_t.sign.get(v, 0) for d in ul],
                          'made_not_loose': other, 'holders_v_t': len(S_t.holders[v])})
    return cases


# ------------------------------------------------------------------------------------------------- the owner's arm
def members_after(S):
    return [u for u in S.cand if u not in S.removed and S.hk(u)[0] > 0]


def side(S, pat, s):
    return P.side_of(S, pat, s) if pat else set()


def ending(run, pat, s, T):
    """D 7.2, 7.3: the round of ending (first t >= s after which no knot of the pattern and its descendants is a
    member), whether it makes a birth in round T, and whether every member left waits."""
    SE = run.snap[min(T, run.rounds_done)]
    sd = side(SE, pat, s)
    end = None
    for t in range(s, min(T, run.rounds_done) + 1):
        S = run.snap[t]
        if not any(u in sd for u in members_after(S)):
            end = t
            break
    out = {'round_of_ending': end}
    if T > run.rounds_done:
        out['note'] = 'run ended before T'
    if end is not None:
        out['state'] = 'ended at %d' % end
        return out
    rec = run.records[T - 1] if T >= 1 and T <= len(run.records) else None
    births = [b for b in rec['births'] if any(p in sd for p in b['parents'])] if rec else []
    if births:
        out['state'] = 'makes a birth in round T'
        return out
    mem = [u for u in members_after(run.snap[T]) if u in sd]
    waits = rec is not None and all(u in set(rec['waiting']) for u in mem)
    out['state'] = 'every member left waits' if (mem and waits) else 'members left, no birth'
    return out


def takes_between(run, X, Y, s, T):
    """D 7.5: the first round at which a birth descended from Y only takes (step 5') a distinction with, at the start
    of that round, a holder descended from X only; the reverse; joint births apart."""
    SE = run.snap[min(T, run.rounds_done)]
    desc = descent_map(SE, X, Y, s)
    out = {'Y takes from X': None, 'X takes from Y': None, 'joint takes': None}
    for t in range(s + 1, min(T, run.rounds_done) + 1):
        Sb = run.snap[t - 1]
        for b in run.records[t - 1]['births']:
            if not b['rule_takes']:
                continue
            db = desc.get(b['id'])
            for d in b['rule_takes']:
                hd = {desc.get(w) for w in Sb.holders[d]}
                if db == 'Y only' and 'X only' in hd and out['Y takes from X'] is None:
                    out['Y takes from X'] = t
                if db == 'X only' and 'Y only' in hd and out['X takes from Y'] is None:
                    out['X takes from Y'] = t
                if db == 'both' and out['joint takes'] is None:
                    out['joint takes'] = t
    return out


def relation(take_round, diff_round):
    if take_round is None:
        return 'no take'
    if diff_round is None:
        return 'take, no difference'
    if take_round < diff_round:
        return 'strictly before'
    if take_round == diff_round:
        return 'same round'
    return 'after'



# ------------------------------------------------------------------------------------------- knot tests (D 8)
def knot_tests_A(run):
    kt = K.test_run(run.snap, run.law)
    return brief(kt)


def knot_tests_cmp(run, s, A_fail_knots=(), full=False):
    """A comparison run at its last round read (as the fold study: knots made by round s keep run A's verdict under
    not-all-equal; parity tests every knot).  full: test every knot (a run from another start)."""
    last = run.rounds_done
    if run.law.knot_law == 'parity' or full:
        return brief(K.test_run(run.snap, run.law, rounds=[last]))
    kt = K.test_run(run.snap, run.law, rounds=[last], only_new_after=s)
    redo = [u for u in A_fail_knots if u < run.snap[last].n_knots]
    if redo:
        d = K.nae_direct(run.snap[last], redo)
        kt['verdicts'] += len(d)
        kt['fails'] += [K._fail_row(run.snap[last], u, last, 'direct') for u, v in d.items() if not v]
    return brief(kt)


def brief(kt):
    return {'verdicts': kt['verdicts'], 'n_fails': len(kt['fails']), 'fails': kt['fails'][:12],
            'fail_kinds': dict(Counter(f['kind'] for f in kt['fails'])),
            'n_disagree': len(kt['disagree']), 'disagree': kt['disagree'][:6], 'n_untested': len(kt['untested']),
            'birth_vs_direct': kt['birth_vs_direct']}


# --------------------------------------------------------------------------------------------- PO1 (B1, checked)
def po1_check(run, X, s, knot_law):
    """PO1: the allowed states restricted to the distinctions held by X and its descendants after round t are the same
    after the last round read (by containment, the same after every later round); and no birth without a parent among
    X's members (X and its descendants) takes a usable loose distinction of a member."""
    R = run.rounds_done
    out = {'same': True, 'rows': [], 'loose_taken_by_other': 0}
    if R <= s:
        return out
    SR = run.snap[R]
    for t in range(s, R):
        St = run.snap[t]
        xd = P.side_of(St, X, s)
        Dt = sorted(places_of(St, xd))
        cut = None
        if knot_law == 'parity':
            a = _proj_rank(St, Dt)
            b = _proj_rank(SR, Dt)
        else:
            if len(Dt) > 12:
                cut = 12
                Dt = Dt[:12]
            a = _nae_count(St, Dt)
            b = _nae_count(SR, Dt)
        out['rows'].append({'t': t, 'n': len(Dt), 'cut_to_12': bool(cut), 'at_t': a, 'at_last': b})
        if a != b:
            out['same'] = False
    for t in range(s + 1, R + 1):
        Sb = run.snap[t - 1]
        xd = P.side_of(Sb, X, s)
        for b in run.records[t - 1]['births']:
            for d in b['inputs']:
                hs = Sb.holders[d]
                if len(hs) == 1 and not Sb.barred[d] and hs[0] in xd and hs[0] not in b['parents']:
                    out['loose_taken_by_other'] += 1
    return out


def _proj_rank(S, D):
    coords = parity_coords(S)
    B = K.Basis()
    for d in D:
        if coords[d]:
            B.insert(coords[d])
    return B.rank()


def _nae_count(S, D):
    sat = Solver(name='minisat22')
    try:
        for u in S.knots():
            vs = [d + 1 for d in S.places[u]]
            sat.add_clause(vs)
            sat.add_clause([-v for v in vs])
        n = 0
        for mask in range(1 << len(D)):
            assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(D)]
            if sat.solve(assumptions=assum):
                n += 1
        return n
    finally:
        sat.delete()


# ------------------------------------------------------------------------------------------- readings per round
def roster_or_none(view, t):
    """The roster after round t, or None where the fold engine's guard stops it (P, Bounds: "not read")."""
    try:
        return view.roster(t)
    except pm.GuardStop:
        return None


def readings_per_round(run, ref, X, Y, s, knot_law, built=True, values=True, form=True, xref=True, seed=0):
    """D 3: at every round t > s of a run: the form reading, the built-structure reading and the values reading (Y's
    places; X's places for P9; Y handing on its own value), with descents."""
    view = P.RunView(run)
    S_s = run.snap[s]
    nd_s = S_s.n_distinctions
    T_s = ties(S_s, knot_law, seed)
    elig_Y = eligible_places(ref, T_s, 'Y') if values else []
    elig_X = eligible_places(ref, T_s, 'X') if (values and ref.X) else []
    rows = []
    for t in range(s + 1, run.rounds_done + 1):
        S_t = run.snap[t]
        desc = descent_map(S_t, X, Y, s)
        row = {'t': t, 'knots': S_t.n_knots}
        if form:
            R_t = roster_or_none(view, t)
            if R_t is None:
                row['form not read'] = 'the roster met the fold engine\'s guard'
            else:
                parts = form_reading(ref, S_t, R_t, desc)
                row['form'] = form_summary(parts)
                row['form_parts'] = parts[:10]
        if built:
            row['built'] = built_reading(ref, S_t, desc)
        if values:
            T_t = ties(S_t, knot_law, seed + t)
            vy = values_reading(ref, S_t, T_t, desc, elig_Y, nd_s)
            vx = values_reading(ref, S_t, T_t, desc, elig_X, nd_s) if elig_X else []
            row['values_Y'] = vy
            row['values_X'] = vx
            # every tie class containing a made distinction (run 6)
            row['made_tied'] = sum(1 for c in T_t.classes if any(d >= nd_s for d in c))
            row['made_tied_classes'] = [c for c in T_t.classes if any(d >= nd_s for d in c)][:6]
        rows.append(row)
    return {'eligible_Y': elig_Y, 'eligible_X': elig_X, 'rows': rows,
            'ties_s': {'classes': T_s.classes[:10], 'frozen': sorted(T_s.frozen)[:20], 'unsat': T_s.unsat}}


def values_flags(rr):
    """At some round / at the last round read: two of Y made by X; Y handing on its own value; two of X's place."""
    out = {'Y_by_X_some': None, 'Y_by_X_last': False, 'Y_own_some': None, 'X_place_by_X_some': None, 'cases': []}
    rows = rr['rows']
    for i, row in enumerate(rows):
        for c in row.get('values_Y', []):
            if c['made_by_X'] and out['Y_by_X_some'] is None:
                out['Y_by_X_some'] = row['t']
            if c['by_Y_only'] and out['Y_own_some'] is None:
                out['Y_own_some'] = row['t']
            if c['made_by_X'] and i == len(rows) - 1:
                out['Y_by_X_last'] = True
            if len(out['cases']) < 8:
                out['cases'].append(dict(c, t=row['t']))
        for c in row.get('values_X', []):
            if c['made_by_X'] and out['X_place_by_X_some'] is None:
                out['X_place_by_X_some'] = row['t']
    return out


def form_flags(rr):
    rows = rr['rows']
    some = next((r['t'] for r in rows if r.get('form', {}).get('two_made_by_X')), None)
    one = next((r['t'] for r in rows if r.get('form', {}).get('by_descent', {}).get('X only', 0) >= 1), None)
    anyp = next((r['t'] for r in rows if r.get('form', {}).get('n', 0) >= 1), None)
    last = bool(rows and rows[-1].get('form', {}).get('two_made_by_X'))
    yret = next((r['t'] for r in rows if r.get('form', {}).get('by_descent', {}).get('Y only', 0) >= 1), None)
    return {'two_by_X_some': some, 'two_by_X_last': last, 'one_by_X_some': one, 'any_some': anyp,
            'Y_returning_some': yret}


def built_flags(rr):
    rows = rr['rows']
    some = next((r['t'] for r in rows if r.get('built', {}).get('two_made_by_X')), None)
    anyr = next((r['t'] for r in rows if r.get('built', {}).get('n', 0) >= 1), None)
    bound = any(r.get('built', {}).get('bound_hit') for r in rows)
    return {'two_by_X_some': some, 'any_renaming_some': anyr, 'bound_hit': bound}


def n4_map(stars, name):
    """D 4.5's n4 procedure: labels = sorted(labels); perm = labels[:]; random.Random('2026112506|' + name).shuffle(perm);
    label labels[i] to perm[i]."""
    labels = sorted({l for k in stars for l in k})
    perm = labels[:]
    random.Random('2026112506|' + name).shuffle(perm)
    return {str(a): b for a, b in zip(labels, perm)}
