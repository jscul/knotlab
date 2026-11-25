"""The engine of DESCENT-HELD-20261125-001A-E001: SD's complete round (steps 1-8) with the three forms of DH 3.2.

Written from the frozen texts (SD lines 34-77; DH 1-4; the pre-registration), not from any other program. Step 1's groups
are lr_core.compute_groups, imported unchanged. Readings: deviations.md, items 1-14.

Forms: None (the base law B), 'PU' = NEXT3-PLACES (usable), 'PB' = NEXT3-PLACES (barred), 'BB' = NEXT3-BARRED.
Knot laws: 'parity' (closing exception acts) or 'nae' (no closing exception).
"""
from __future__ import annotations

from collections import Counter, defaultdict

from dh_common import compute_groups, LAWS_JSON

FORMS = ('PU', 'PB', 'BB')
FORM_NAMES = {None: 'base', 'PU': 'NEXT3-PLACES (usable)', 'PB': 'NEXT3-PLACES (barred)', 'BB': 'NEXT3-BARRED'}


# ================================================================================================= laws
class Law:
    __slots__ = ('name', 'ration', 'treatment', 'release', 'fillers', 'base')

    def __init__(self, name, ration, treatment, release='RELEASE', fillers=False, base=True):
        self.name, self.ration, self.treatment, self.release, self.fillers, self.base = \
            name, ration, treatment, release, fillers, base

    def __repr__(self):
        return 'Law(%s: %s/%s/%s%s)' % (self.name, self.ration, self.treatment, self.release,
                                        '/FILLERS' if self.fillers else '')

    def text(self):
        return '%s/%s/%s%s' % (self.ration, self.treatment, self.release, '/FILLERS' if self.fillers else '')


def laws_from_json():
    out = []
    for grp in ('recorded', 'holding'):
        for e in LAWS_JSON[grp]:
            out.append(Law(e['name'], e['ration'], e['treatment'], e['release'],
                           'FILLERS' in e.get('extras', []), e.get('base', True)))
    return out


LAWS = laws_from_json()                       # the 14 laws in laws.json order
LAW = {L.name: L for L in LAWS}
RECORDED = [L for L in LAWS if L.release == 'RELEASE']          # the ten recorded laws
BASES = [L for L in LAWS if L.base]                               # the eleven bases
RELEASE_BASES = [L for L in BASES if L.release == 'RELEASE']      # the seven RELEASE bases


def fresh(ration, p, D):
    """SD line 60-62: the ordinary count q and the rations (no closing exception)."""
    q = max(D, 3 - p, 1)
    if ration == 'ORD':
        return q
    if ration.startswith('CAP-'):
        return min(q, int(ration[4:]))
    if ration.startswith('RATION-'):
        return max(int(ration[7:]), 3 - p)
    if ration == 'ONE-FEWER':
        return min(q, max(3 - p, 0, q - 1))
    if ration == 'FLOOR0':
        return max(3 - p, 0)
    if ration == 'FLOOR1':
        return max(3 - p, 1)
    raise ValueError(ration)


def target_of(kap, swap=False, M=3):
    """DH 3.2 step 3.  kap: the parents' counts (already reduced mod M).  Returns (target or None, parents differ)."""
    vals = set(kap)
    if len(vals) == 1:
        return (next(iter(vals)) + 1) % M, False
    if not swap or len(vals) != 2:
        return None, True
    a, b = sorted(vals)
    c = a if (a + 1) % M == b else b            # the c with {c, c+1} = {a, b}
    return (c + 2) % M, True


# ================================================================================================= structure
class Struct:
    """A structure on real knots with the record of parents and each knot's counts (DH 2.1-2.2)."""

    def __init__(self, stars, barred_labels=()):
        labels = sorted({d for s in stars for d in s})
        idx = {lab: i for i, lab in enumerate(labels)}
        self.places = [[idx[d] for d in s] for s in stars]
        m = len(labels)
        self.holders = [[] for _ in range(m)]
        for u, P in enumerate(self.places):
            for d in P:
                self.holders[d].append(u)
        assert all(1 <= len(h) <= 2 for h in self.holders), 'a distinction with no holder or more than two'
        self.barred = [False] * m
        self.bround = [None] * m          # round at which a distinction was barred (0: at the start)
        for lab in barred_labels:
            d = idx[lab]
            assert len(self.holders[d]) == 1
            self.barred[d] = True
            self.bround[d] = 0
        self.dround = [0] * m             # round at which a distinction was made
        nk = len(stars)
        self.parents = [()] * nk
        self.born = [0] * nk
        self.ps = [0] * nk                # parent steps
        self.kids = [[] for _ in range(nk)]
        self.p = [0] * nk
        self.D = [None] * nk
        self.F = [None] * nk              # base count F (what the new knot received before s)
        self.FB = [None] * nk             # F_B(p, D) (equal to F except at a closing birth, registered reading)
        self.s = [0] * nk
        bb = [sum(1 for d in P if self.barred[d]) for P in self.places]
        self.z = list(bb)                 # barred at birth (for a start knot: as handed in)
        self.b = list(bb)                 # barred places now
        self.ret = [0] * nk               # barred places added by retiring
        self.retired_round = [None] * nk
        self.closing = [False] * nk
        self.differ = [False] * nk        # counted at DH 3.2 step 3
        self.hyp_s = [None] * nk          # at a closing birth (registered reading): the s it would need
        self.round = 0
        self.n_loose = sum(1 for h in self.holders if len(h) == 1)
        self.cand = set(range(nk))        # knots that may hold a usable loose distinction
        self.k_at = [nk]                  # number of knots after each round (index = round)
        self.m_at = [m]                   # number of distinctions after each round

    # ------------------------------------------------------------------------------------------ reading
    def n_knots(self):
        return len(self.places)

    def usable(self, u):
        H, B = self.holders, self.barred
        return [d for d in self.places[u] if len(H[d]) == 1 and not B[d]]

    def members(self):
        out = {}
        for u in sorted(self.cand):
            us = self.usable(u)
            if us:
                out[u] = us
            else:
                self.cand.discard(u)
        return out

    def meets(self, u):
        out = set()
        H = self.holders
        for d in self.places[u]:
            for w in H[d]:
                if w != u:
                    out.add(w)
        return out

    def met_family(self, hold):
        acc = defaultdict(set)
        H = self.holders
        for u in hold:
            for d in self.places[u]:
                for w in H[d]:
                    if w != u:
                        acc[w].add(u)
        return {frozenset(s) for s in acc.values() if len(s) >= 2}

    def kappa(self, u, form):
        """The count of DH 3.2 step 2 (not reduced)."""
        if form == 'BB':
            return self.b[u]
        return len(self.places[u])


# ================================================================================================= one complete round
def do_round(S, L, form=None, knot_law='parity', pd_swap=False, closing_swap=False, M=3, all_loose_short=False):
    """One complete round (SD steps 1-8) with DH 3.2's change to step 7, in place.  Returns the round's record.
    all_loose_short: a deliberately wrong engine (shortness counted on every loose place), used only by part 0 (f)."""
    rnd = S.round + 1
    places, H, B = S.places, S.holders, S.barred
    avail0 = S.members()
    hold = {u: len(v) for u, v in avail0.items()}
    rec = {'round': rnd, 'members': len(hold), 'groups': 0, 'short': [], 'waited': [], 'retired': [], 'births': 0,
           'stalled': False, 'closing': False, 'newly_barred': 0, 'new': []}
    S.round = rnd
    if not hold:
        S.k_at.append(len(places)); S.m_at.append(len(H))
        return rec
    fam = S.met_family(hold)
    groups = compute_groups(sorted(hold), fam)
    rec['groups'] = len(groups)
    owe = Counter(u for g in groups for u in g)
    if all_loose_short:
        cap = {u: sum(1 for d in places[u] if len(H[d]) == 1) for u in hold}
    else:
        cap = hold
    short = {u for u in hold if owe[u] > cap[u]}
    rec['short'] = sorted(short)
    if L.treatment == 'STALL' and short:
        rec['stalled'] = True
        S.k_at.append(len(places)); S.m_at.append(len(H))
        return rec
    kept = [g for g in groups if not short.intersection(g)]
    cc = Counter(u for g in groups if short.intersection(g) for u in g)
    avail = {u: list(v) for u, v in avail0.items()}
    births = []
    for g in kept:
        births.append((g, [avail[u].pop() for u in g]))
    hold_rule = L.release == 'HOLD'
    for u in sorted(hold):
        if u in short:
            if L.treatment == 'CANCEL-OFFSHOOT':
                while avail[u]:
                    births.append(((u,), [avail[u].pop()]))
            elif L.treatment == 'CANCEL-RETIRE':
                n = len(avail[u])
                for d in avail[u]:
                    B[d] = True
                    S.bround[d] = rnd
                S.b[u] += n
                S.ret[u] += n
                S.retired_round[u] = rnd
                rec['newly_barred'] += n
                rec['retired'].append(u)
                avail[u] = []
            elif L.treatment == 'CANCEL-WAIT':
                rec['waited'].append(u)
            else:
                raise AssertionError(L.treatment)
        else:
            keep = cc[u] if hold_rule else 0
            while len(avail[u]) > keep:
                births.append(((u,), [avail[u].pop()]))
    new = []
    ps = S.ps
    for parents, taken in births:
        x = len(places)
        places.append(list(taken))
        for d in taken:
            assert len(H[d]) == 1 and not B[d]
            H[d].append(x)
        S.n_loose -= len(taken)
        S.parents.append(tuple(parents))
        S.born.append(rnd)
        S.ps.append(1 + max(ps[y] for y in parents))
        S.kids.append([])
        for y in parents:
            S.kids[y].append(x)
        for lst, v in ((S.p, len(parents)), (S.D, None), (S.F, None), (S.FB, None), (S.s, 0), (S.z, 0), (S.b, 0),
                       (S.ret, 0), (S.retired_round, None), (S.closing, False), (S.differ, False), (S.hyp_s, None)):
            lst.append(v)
        S.cand.add(x)
        new.append(x)
    # step 6: demand
    dhold = {x: 1 for x in new}
    for u in hold:
        h = sum(1 for d in places[u] if len(H[d]) == 1 and not B[d])
        if h:
            dhold[u] = h
    dgroups = compute_groups(sorted(dhold), S.met_family(dhold)) if new else []
    Dc = Counter(u for g in dgroups for u in g)
    closing_round = len(new) == 1 and S.n_loose == 0 and knot_law == 'parity'
    rec['closing'] = closing_round
    for x in new:
        p = S.p[x]
        Dx = Dc[x]
        S.D[x] = Dx
        FB = fresh(L.ration, p, Dx)
        S.FB[x] = FB
        registered_closing = closing_round and not closing_swap
        F = 0 if registered_closing else FB
        if closing_round:
            S.closing[x] = True
        s = 0
        if form is not None:
            kap = [S.kappa(y, form) % M for y in S.parents[x]]
            target, differ = target_of(kap, pd_swap, M)
            S.differ[x] = differ
            if target is not None:
                zF = (F - min(F, Dx)) if L.fillers else 0
                cur = (p + F) if form in ('PU', 'PB') else zF
                s = (target - cur) % M
            if registered_closing:
                S.hyp_s[x] = s           # computed with F = 0 (and z_F = 0)
                s = 0
        S.F[x] = F
        S.s[x] = s
        if form == 'PU':
            total = F + s
            nu = min(total, Dx) if L.fillers else total
            nb = total - nu
        else:
            nu = min(F, Dx) if L.fillers else F
            nb = (F - nu) + s
        for i in range(nu + nb):
            d = len(H)
            H.append([x])
            barred = i >= nu
            B.append(barred)
            S.bround.append(rnd if barred else None)
            S.dround.append(rnd)
            places[x].append(d)
        S.n_loose += nu + nb
        S.z[x] = nb
        S.b[x] = nb
        rec['newly_barred'] += nb
    rec['births'] = len(new)
    rec['new'] = new
    S.k_at.append(len(places))
    S.m_at.append(len(H))
    return rec


# ================================================================================================= runs
def grow(stars, L, form=None, knot_law='parity', R=8, N=3000, stop='change', pd_swap=False, closing_swap=False,
         barred_labels=(), S=None, all_loose_short=False):
    """A run (DH 1.1, deviations 6).  Returns (S, records, end)."""
    if S is None:
        S = Struct(stars, barred_labels)
    recs = []
    end = None
    while True:
        if S.round >= R:
            end = 'R'
            break
        rec = do_round(S, L, form, knot_law, pd_swap, closing_swap, all_loose_short=all_loose_short)
        recs.append(rec)
        if rec['stalled']:
            end = 'stalled'
            break
        if rec['births'] == 0 and (stop == 'birth' or rec['newly_barred'] == 0):
            end = 'stopped' if rec['members'] == 0 else 'jammed'
            break
        if len(S.places) > N:
            end = 'N'
            break
    return S, recs, end


def rounds_changed(recs):
    return sum(1 for r in recs if r['births'] or r['newly_barred'])


# ================================================================================================= reading a run
def snapshot_stars(S, t):
    """The structure after round t as stars (its own names) and its barred labels (deviations 25)."""
    K = S.k_at[t]
    stars = [list(S.places[u]) for u in range(K)]
    barred = [d for d in range(S.m_at[t]) if S.bround[d] is not None and S.bround[d] <= t]
    return stars, barred


def b_at(S, u, t):
    return sum(1 for d in S.places[u] if S.bround[d] is not None and S.bround[d] <= t)


def kappa_b_at(S, t):
    """Barred places of every knot after round t: those barred at birth (or as handed in) and those retiring added
    by round t."""
    K = S.k_at[t]
    rr, z, ret = S.retired_round, S.z, S.ret
    return [z[u] + (ret[u] if rr[u] is not None and rr[u] <= t else 0) for u in range(K)]


def place_kind(S, x, y):
    if y in S.parents[x]:
        return 'parent'
    if x in S.parents[y]:
        return 'child'
    if S.born[x] == 0 and S.born[y] == 0:
        return 'start'
    return 'other'


KINDS = ('parent', 'child', 'start', 'other')


def place_rule(S, form, t=None, M=3, stamp=None, pred=None, keep_wrong=50, kap_override=None):
    """The place rule (DH 4.1) on the structure after round t (default: the last).  Counts right and wrong places by kind.
    form 'PU'/'PB'/None: kappa = number of places; 'BB': barred places at t.  stamp/pred: a written stamp and its rule
    (the fives stamp, deviations 9) in place of the count."""
    if t is None:
        t = S.round
    K = S.k_at[t]
    mt = S.m_at[t]
    if stamp is None:
        if kap_override is not None:
            kap = kap_override
        elif form == 'BB':
            if t == S.round:
                kap = S.b
            else:
                kap = kappa_b_at(S, t)
        else:
            kap = [len(P) for P in S.places]
    out = {k: [0, 0] for k in KINDS}        # [right, wrong]
    wrong = []
    H = S.holders
    for d in range(mt):
        h = H[d]
        if len(h) < 2:
            continue
        a, c = h
        if a >= K or c >= K:
            continue
        for x, y in ((a, c), (c, a)):
            kind = place_kind(S, x, y)
            if stamp is None:
                pp = (kap[y] - kap[x]) % M == M - 1
            else:
                pp = pred(stamp[x], stamp[y])
            right = pp == (kind == 'parent')
            out[kind][0 if right else 1] += 1
            if not right and len(wrong) < keep_wrong:
                wrong.append((d, x, y, kind))
    nwrong = sum(v[1] for v in out.values())
    return {'by_kind': out, 'wrong': nwrong, 'right': sum(v[0] for v in out.values()), 'wrong_list': wrong}


def place_verdict_map(S, form, t=None, M=3):
    """{(d, x, y): (kind, predicted parent)} on the structure after round t."""
    if t is None:
        t = S.round
    K = S.k_at[t]
    if form == 'BB':
        kap = S.b if t == S.round else kappa_b_at(S, t)
    else:
        kap = [len(P) for P in S.places]
    out = {}
    for d in range(len(S.holders)):
        h = S.holders[d]
        if len(h) < 2 or h[0] >= K or h[1] >= K:
            continue
        a, c = h
        for x, y in ((a, c), (c, a)):
            out[(d, x, y)] = (place_kind(S, x, y), (kap[y] - kap[x]) % M == M - 1)
    return out


def descent_summary(S, recs):
    """(b), (b'), greatest difference (by round), the first rounds, from the record (deviations 7)."""
    ps = S.ps
    counted_first = None
    bprime_first = None
    bprime_births_first = []
    greatest = 0
    by_round = {}
    for r in recs:
        g_r = 0
        for x in r['new']:
            pp = [ps[y] for y in S.parents[x]]
            g = ps[x] - min(pp)
            if g > g_r:
                g_r = g
            if len(set(pp)) > 1 and counted_first is None:
                counted_first = r['round']
            if len({v % 3 for v in pp}) > 1:
                if bprime_first is None:
                    bprime_first = r['round']
                if bprime_first == r['round']:
                    bprime_births_first.append(x)
        if r['new']:
            by_round[r['round']] = g_r
            greatest = max(greatest, g_r)
    return {'counted': counted_first is not None, 'counted_first_round': counted_first,
            'bprime_fails': bprime_first is not None, 'bprime_first_round': bprime_first,
            'bprime_first_births': bprime_births_first, 'greatest': greatest, 'greatest_by_round': by_round,
            'max_ps': max(ps) if ps else 0}


def lq_condition_fails(S, recs):
    """Deviations 8: rounds in which a start knot waits and a start knot it meets is a parent of a birth of that round."""
    out = []
    for r in recs:
        W = [u for u in r['waited'] if S.born[u] == 0]
        if not W:
            continue
        P = {y for x in r['new'] for y in S.parents[x] if S.born[y] == 0}
        if not P:
            continue
        for u in W:
            if S.meets(u) & P:
                out.append(r['round'])
                break
    return out


def condition_a(S, form, start_k=None):
    """DH 4.5 (a) on the start (deviations 12)."""
    K = S.k_at[0] if start_k is None else start_k
    for d in range(S.m_at[0]):
        h = S.holders[d]
        if len(h) == 2 and h[0] < K and h[1] < K:
            x, y = h
            if form == 'BB':
                cx, cy = b_at(S, x, 0), b_at(S, y, 0)
            else:
                cx, cy = len(S.places[x]), len(S.places[y])
            if (cx - cy) % 3:
                return False
    return True


def condition_c(S, form):
    if form != 'BB':
        return True
    return all(v % 3 == 0 for v in S.ret)


def condition_d(S):
    return not any(c and (h or 0) > 0 for c, h in zip(S.closing, S.hyp_s))


def first_no_birth_round(recs):
    for r in recs:
        if r['births'] == 0:
            return r['round']
    return None


def signature(S, recs, form):
    """DH 8.2's signature (labelled as a signature wherever used)."""
    nk = len(S.places)
    ms = Counter((S.born[u], S.ps[u], S.p[u], len(S.places[u]), S.z[u], S.s[u], len(S.kids[u]), S.b[u])
                 for u in range(nk))
    pr = place_rule(S, form if form else None)
    return {'births_by_round': [r['births'] for r in recs],
            'knots': sorted([list(k) + [v] for k, v in ms.items()]),
            'place_rule': pr['by_kind']}


# ================================================================================================= knot-test adapter
class KS:
    """The attributes knots.py reads (n_knots, removed, holders, places, n_distinctions), for the structure after t."""

    def __init__(self, S, t=None):
        if t is None:
            t = S.round
        K = S.k_at[t]
        m = S.m_at[t]
        self.places = [list(S.places[u]) for u in range(K)]
        self.holders = [[w for w in S.holders[d] if w < K] for d in range(m)]
        self.n_knots = K
        self.removed = set()
        self.n_distinctions = m


def iso_graph(stars, barred):
    import networkx as nx
    G = nx.Graph()
    bs = set(barred)
    for u, P in enumerate(stars):
        G.add_node(('k', u), lab='k')
        for d in P:
            G.add_node(('d', d), lab='b' if d in bs else 'd')
            G.add_edge(('k', u), ('d', d))
    return G


def _refine(G1, G2):
    """Colour refinement run on both graphs together (so that colours are comparable); the stable colours are an
    isomorphism-invariant labelling.  Returns False when the colour histograms differ (not isomorphic)."""
    nodes = [(0, v) for v in G1.nodes] + [(1, v) for v in G2.nodes]
    adj = {(0, v): [(0, w) for w in G1.adj[v]] for v in G1.nodes}
    adj.update({(1, v): [(1, w) for w in G2.adj[v]] for v in G2.nodes})
    col = {}
    for x in nodes:
        g = G1 if x[0] == 0 else G2
        col[x] = g.nodes[x[1]]['lab']
    ids = {}
    col = {x: ids.setdefault(c, len(ids)) for x, c in col.items()}
    ncol = len(ids)
    while True:
        sig = {x: (col[x], tuple(sorted(col[w] for w in adj[x]))) for x in nodes}
        ids = {}
        new = {x: ids.setdefault(s, len(ids)) for x, s in sig.items()}
        h0 = Counter(new[x] for x in nodes if x[0] == 0)
        h1 = Counter(new[x] for x in nodes if x[0] == 1)
        if h0 != h1:
            return False
        col = new
        if len(ids) == ncol:
            break
        ncol = len(ids)
    for x in nodes:
        g = G1 if x[0] == 0 else G2
        g.nodes[x[1]]['wl'] = col[x]
    return True


def isomorphic_vf2pp(st1, b1, st2, b2):
    """VF2++ on the bipartite graph of knots and distinctions (kept for small cross-checks only: it stalls on the
    symmetric structures of these runs)."""
    import networkx as nx
    G1, G2 = iso_graph(st1, b1), iso_graph(st2, b2)
    if not _refine(G1, G2):
        return False
    return nx.vf2pp_is_isomorphic(G1, G2, node_label='wl')


def _knot_multigraph(stars, barred):
    """The structure as a multigraph on knots: each knot labelled (usable loose, barred loose), each pair of knots
    joined by the number of distinctions they share.  Two structures are isomorphic (knots and distinctions, marks
    kept) exactly when these labelled multigraphs are: loose distinctions of one knot with one mark are interchangeable,
    and so are the distinctions two knots share."""
    hold = defaultdict(list)
    for u, P in enumerate(stars):
        for d in P:
            hold[d].append(u)
    bs = set(barred)
    n = len(stars)
    lab = [[0, 0] for _ in range(n)]
    adj = [defaultdict(int) for _ in range(n)]
    for d, hs in hold.items():
        if len(hs) == 1:
            lab[hs[0]][1 if d in bs else 0] += 1
        elif len(hs) == 2:
            a, c = hs
            adj[a][c] += 1
            adj[c][a] += 1
        else:
            raise AssertionError('more than two holders')
    return [tuple(x) for x in lab], [dict(a) for a in adj], len(hold)


class _Intern:
    def __init__(self):
        self.ids = {}

    def __call__(self, key):
        return self.ids.setdefault(key, len(self.ids))


def _prune(lab, adj, I):
    """Absorb pendant knots into their one neighbour, round by round (an isomorphism-invariant reduction)."""
    lab = {u: I(('L', l)) for u, l in enumerate(lab)}
    adj = {u: dict(a) for u, a in enumerate(adj)}
    while True:
        leaves = [u for u, a in adj.items() if len(a) == 1]
        leaves = [u for u in leaves if not (len(adj[next(iter(adj[u]))]) == 1)]    # keep a pair joined only together
        if not leaves:
            break
        pend = defaultdict(list)
        for l in leaves:
            (v, m), = adj[l].items()
            pend[v].append((lab[l], m))
        for l in leaves:
            (v, m), = adj[l].items()
            del adj[v][l]
            del adj[l]
            del lab[l]
        for v, lst in pend.items():
            lab[v] = I(('P', lab[v], tuple(sorted(lst))))
    return lab, adj


def _refine2(c0, c1, adj0, adj1, I):
    """Colour refinement on both graphs with shared colour names; False when the histograms differ."""
    while True:
        n_before = len(set(c0.values()) | set(c1.values()))
        s0 = {u: I(('R', c0[u], tuple(sorted((c0[w], m) for w, m in adj0[u].items())))) for u in c0}
        s1 = {u: I(('R', c1[u], tuple(sorted((c1[w], m) for w, m in adj1[u].items())))) for u in c1}
        if Counter(s0.values()) != Counter(s1.values()):
            return None
        c0, c1 = s0, s1
        if len(set(c0.values()) | set(c1.values())) == n_before:
            return c0, c1


def isomorphic(st1, b1, st2, b2):
    """Exact isomorphism of knots and distinctions with marks: on the labelled multigraphs of knots (above), pendant
    knots absorbed, then individualization and refinement with a search over every candidate, the final bijection
    checked edge by edge."""
    if len(st1) != len(st2) or sorted(len(P) for P in st1) != sorted(len(P) for P in st2):
        return False
    l1, a1, m1 = _knot_multigraph(st1, b1)
    l2, a2, m2 = _knot_multigraph(st2, b2)
    if m1 != m2 or sorted(l1) != sorted(l2):
        return False
    I = _Intern()
    c0, adj0 = _prune(l1, a1, I)
    c1, adj1 = _prune(l2, a2, I)
    if Counter(c0.values()) != Counter(c1.values()):
        return False
    import sys as _s
    _s.setrecursionlimit(max(10000, _s.getrecursionlimit()))

    def search(c0, c1):
        r = _refine2(c0, c1, adj0, adj1, I)
        if r is None:
            return False
        c0, c1 = r
        cls0 = defaultdict(list)
        cls1 = defaultdict(list)
        for u, c in c0.items():
            cls0[c].append(u)
        for u, c in c1.items():
            cls1[c].append(u)
        big = [c for c, v in cls0.items() if len(v) > 1]
        if not big:
            mp = {cls0[c][0]: cls1[c][0] for c in cls0}
            for u, a in adj0.items():
                for w, m in a.items():
                    if adj1[mp[u]].get(mp[w]) != m:
                        return False
            return True
        c = min(big, key=lambda x: (len(cls0[x]), x))
        v = min(cls0[c])
        for w in sorted(cls1[c]):
            tag = I(('IND', len(I.ids)))
            d0 = dict(c0); d0[v] = tag
            d1 = dict(c1); d1[w] = tag
            if search(d0, d1):
                return True
        return False

    return search(c0, c1)
