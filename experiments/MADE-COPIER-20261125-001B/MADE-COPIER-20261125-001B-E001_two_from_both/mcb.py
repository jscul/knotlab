"""Engine of MADE-COPIER-20261125-001B-E001: the readings of "two parts the same as Y, each descended from both".

  PB research/MADE-COPIER-20261125-001B/preregistration.md     DB research/MADE-COPIER-20261125-001/definitions_b.md
  D, P ticket A's definitions and pre-registration            FD, SD the fold study's and the shared definitions
Readings taken where the text leaves a choice are numbered in deviations.md of this folder.

The growth is the fold study's engine (pm.py), imported unchanged through ticket A's engine (mc.py, also unchanged), from
which the descents, the paired runs and the knot tests are used.  The fold engine's guard limits are multiplied by ten
here, at import (DB 3.9); the fold engine's file is not edited.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
A_DIR = os.path.join(ROOT, 'experiments/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier')
DATA_B = os.path.join(ROOT, 'research/MADE-COPIER-20261125-001B')
OUT_B = os.path.join(ROOT, 'artifacts/MADE-COPIER-20261125-001B/MADE-COPIER-20261125-001B-E001_two_from_both')

sys.path.insert(0, A_DIR)
import mc  # noqa: E402  (ticket A's engine; it puts the fold engine on the path)
import networkx as nx  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P

# DB 3.9: the fold engine's guard limits multiplied by ten, set at import
GUARD_FACTOR = 10
if not getattr(pm, '_guard_times_ten', False):
    for _k in list(pm.GUARD):
        pm.GUARD[_k] = pm.GUARD[_k] * GUARD_FACTOR
    pm._guard_times_ten = True

with open(os.path.join(DATA_B, 'starts_b.json')) as _f:
    STB = json.load(_f)
with open(os.path.join(DATA_B, 'rosters_b.json')) as _f:
    ROSB = json.load(_f)

KINDS8 = ['one-2', 'one-3', 'two-22', 'two-23', 'two-33', 'three-222', 'pairs-3', 'pairs-4']
WAYS = ['W1', 'W2', 'W3', 'W4']
KNOT_BOUND = 2000
SETTLED4_EXCLUDED = ('one-3', 'two-23', 'two-33', 'three-222', 'pairs-3', 'pairs-4')
BASES6 = mc.BASES_COPY + mc.BASES_CAP3
LAW_KEY = {b: b.split('(')[0] + '-' + b.split('(')[1][:-1] for b in BASES6}   # 'COPY-LAW(RETIRE)' -> 'COPY-LAW-RETIRE'


def rounds_for(base):
    """DB 3.9: 8 rounds, 10 under CAP-3(t)."""
    return 10 if base.startswith('CAP-3') else 8


def law1(base, knot_law, release='RELEASE'):
    """Arm 1: a base law with no taking rule (DB 1.1)."""
    extra = {} if release == 'RELEASE' else {'release': 'HOLD'}
    return mc.make_law(base, None, 'OLDEST', knot_law, **extra)


def grow(S0, law, base, rounds=None):
    return pm.Run(S0, law, rounds=rounds or rounds_for(base), knot_bound=KNOT_BOUND)


# ---------------------------------------------------------------------------------------------------------- starts
def build(stars, barred=()):
    return mc.build_start(stars, None, list(barred))


def start_b(key):
    d = STB['starts'][key]
    return build(d['stars']), list(d['X']), list(d['Y'])


def alone_b(kind, which):
    """'X alone' (labels from 0) or 'Y alone' (labels from 100): the part with e barred; its members."""
    a = STB['alone'][kind][which]
    mem = a['X'] if which == 'X alone' else a['Y']
    return build(a['stars'], a['barred']), list(mem)


def part_knots(kind, which='X'):
    return STB['parts'][kind]['X (labels from 0)' if which == 'X' else 'Y (labels from 100)']


def member_knots(part_stars, n_members):
    """A part's knots: first dead knot (0), its members (1..n), then further dead knots."""
    return list(range(1, 1 + n_members))


def way_start(xstars, xinfo, ystars, yinfo, way, other=None):
    """DB 2.3: X's part, then Y's part, joined by one of W1 to W4; new shared places labelled from 501 in the order
    listed.  xinfo / yinfo: {'members': n, 'first member': i, 'first dead knot': 0}.  other: None, or 'X', 'Y' or 'both'
    for the other-member swap (the member used is the part's 'other member')."""
    xs = [list(k) for k in xstars]
    ys = [list(k) for k in ystars]
    nx_ = len(xs)
    def member(info, use_other):
        o = info.get('other member')
        return 1 + (o if (use_other and o is not None) else info['first member'])
    xm = member(xinfo, other in ('X', 'both'))
    ym = member(yinfo, other in ('Y', 'both'))
    lab = [501]

    def new2():
        a, b = lab[0], lab[0] + 1
        lab[0] += 2
        return [a, b]
    extra = []
    if way == 'W1':
        a = new2()
        b = new2()
        xs[xm] += a
        ys[ym] += b
        extra.append(a + b)
    elif way == 'W2':
        a = new2()
        xs[xinfo['first dead knot']] += a
        ys[ym] += a
    elif way == 'W3':
        a = new2()
        ys[yinfo['first dead knot']] += a
        xs[xm] += a
    elif way == 'W4':
        k = []
        for i in range(xinfo['members']):
            a = new2()
            xs[1 + i] += a
            k += a
        for i in range(yinfo['members']):
            a = new2()
            ys[1 + i] += a
            k += a
        extra.append(k)
    else:
        raise ValueError(way)
    stars = xs + ys + extra
    X = list(range(1, 1 + xinfo['members']))
    Y = [nx_ + 1 + i for i in range(yinfo['members'])]
    return stars, X, Y


# ----------------------------------------------------------------------------------------------- exact form classes
class Forms:
    """Exact classes of parts: SD lines 29-30 (a renaming of members carrying h, k and the inclusion-maximal met
    sets), with member marks when asked (DB 2.5).  Candidates are bucketed by invariants and the Weisfeiler-Lehman hash
    and decided by an exact isomorphism test; a hash never decides."""

    def __init__(self, marked=False, seconds=None, hash_above=None):
        self.marked = marked
        self.buckets = defaultdict(list)
        self.desc = []
        self.seconds = seconds          # deviations 33: a time limit (processor seconds) on one exact test
        self.undecided = 0
        self.undecided_sizes = Counter()  # members of the part in each undecided test
        self.hash_above = hash_above    # deviations 33: a part of more members is classed by its bucket key alone
        self.by_hash = 0
        self.by_hash_classes = set()

    def iso(self, G, H):
        if not self.seconds:
            return nx.is_isomorphic(G, H, node_match=lambda a, b: a['c'] == b['c'])
        import signal

        class _T(Exception):
            pass

        def h(*a):
            raise _T()
        old = signal.signal(signal.SIGVTALRM, h)
        signal.setitimer(signal.ITIMER_VIRTUAL, self.seconds)
        try:
            return nx.vf2pp_is_isomorphic(G, H, node_label='c')
        except _T:
            return None
        finally:
            signal.setitimer(signal.ITIMER_VIRTUAL, 0)
            signal.signal(signal.SIGVTALRM, old)

    @staticmethod
    def graph(R, part, marks=None):
        ms = set(part)
        G = nx.Graph()
        for u in part:
            c = 'm%d,%d' % (R.h[u], R.k[u])
            if marks is not None:
                c += '|' + marks.get(u, 'neither')
            G.add_node(('m', u), c=c)
        for i, M in enumerate(R.maxsets):
            if next(iter(M)) in ms:
                G.add_node(('s', i), c='s')
                for u in M:
                    G.add_edge(('s', i), ('m', u))
        return G

    def classify(self, R, part, marks=None):
        G = self.graph(R, part, marks if self.marked else None)
        cols = tuple(sorted(d['c'] for _, d in G.nodes(data=True)))
        key = (len(part), G.number_of_edges(), cols, nx.weisfeiler_lehman_graph_hash(G, node_attr='c'))
        if self.hash_above is not None and len(part) > self.hash_above:
            self.by_hash += 1
            if self.buckets[key]:
                return self.buckets[key][0][0]
        for cid, H in self.buckets[key]:
            same = self.iso(G, H)
            if same is None:
                self.undecided += 1
                self.undecided_sizes[len(part)] += 1
                continue
            if same:
                return cid
        cid = len(self.desc)
        if self.hash_above is not None and len(part) > self.hash_above:
            self.by_hash_classes.add(cid)
        self.buckets[key].append((cid, G))
        order = sorted(part)
        idx = {u: i for i, u in enumerate(order)}
        self.desc.append({'hk': [[R.h[u], R.k[u]] for u in order],
                          'marks': [marks.get(u, 'neither') for u in order] if (self.marked and marks) else None,
                          'maxsets': sorted(sorted(idx[u] for u in M) for M in R.maxsets if next(iter(M)) in set(part))})
        return cid

    def graph_of_desc(self, cid):
        d = self.desc[cid]
        G = nx.Graph()
        for i, (h, k) in enumerate(d['hk']):
            c = 'm%d,%d' % (h, k) + (('|' + d['marks'][i]) if d.get('marks') else '')
            G.add_node(('m', i), c=c)
        for j, M in enumerate(d['maxsets']):
            G.add_node(('s', j), c='s')
            for i in M:
                G.add_edge(('s', j), ('m', i))
        return G


def merge_descs(descs_lists):
    """Global classes over several jobs' Forms descriptions: [(job, [desc...])] -> {(job, local id): global id},
    [global desc].  Exact isomorphism decides."""
    reg = defaultdict(list)
    out, gl = {}, []
    for job, descs in descs_lists:
        for lid, d in enumerate(descs):
            G = desc_graph(d)
            cols = tuple(sorted(x['c'] for _, x in G.nodes(data=True)))
            key = (len(d['hk']), G.number_of_edges(), cols, nx.weisfeiler_lehman_graph_hash(G, node_attr='c'))
            found = None
            for gid, H in reg[key]:
                if nx.is_isomorphic(G, H, node_match=lambda a, b: a['c'] == b['c']):
                    found = gid
                    break
            if found is None:
                found = len(gl)
                reg[key].append((found, G))
                gl.append(d)
            out[(job, lid)] = found
    return out, gl


def desc_graph(d):
    G = nx.Graph()
    for i, (h, k) in enumerate(d['hk']):
        c = 'm%d,%d' % (h, k) + (('|' + d['marks'][i]) if d.get('marks') else '')
        G.add_node(('m', i), c=c)
    for j, M in enumerate(d['maxsets']):
        G.add_node(('s', j), c='s')
        for i in M:
            G.add_edge(('s', j), ('m', i))
    return G


def form_text(d):
    """A plain description of a form: members' h (and k where not 0), maximal met sets as member positions."""
    hk = ['%d' % h if k == 0 else '%d/%d' % (h, k) for h, k in d['hk']]
    return 'members h %s; maximal met sets %s' % ('[' + ', '.join(hk) + ']', d['maxsets'])


# ------------------------------------------------------------------------------------------------ reading a roster
def roster_or_none(S, law):
    try:
        return pm.roster_of(S.copy(), law)
    except pm.GuardStop:
        return None


def descent_kind(ds):
    return next(iter(ds)) if len(ds) == 1 else 'mixed'


def read_parts(S, R, desc, forms, mforms=None):
    """Every part of the roster: (form class, descent kind, members, marked class)."""
    out = []
    for part in R.parts:
        cid = forms.classify(R, part)
        ds = Counter(desc.get(u, 'neither') for u in part)
        mcid = mforms.classify(R, part, desc) if mforms is not None else None
        out.append((cid, descent_kind(ds), sorted(part), mcid))
    return out


def members_now(S):
    return {u for u in S.cand if u not in S.removed and S.hk(u)[0] > 0}


def ended(S, knots_):
    """SD line 91, read for a set of knots: none of them is a member after the round."""
    mem = members_now(S)
    return not any(u in mem for u in knots_)


def how_ended(run, knots_, upto):
    """For each knot of the set that was a member: the round it stopped being one and how (DB 3.5)."""
    mems = [members_now(run.snap[t]) for t in range(0, upto + 1)]
    out = Counter()
    for u in knots_:
        was = None
        for t in range(0, upto + 1):
            if u in mems[t]:
                was = t
        if was is None or was >= upto:
            continue
        rec = run.records[was]
        if u in rec['retired']:
            how = 'barred when it retired'
        else:
            closers = [b for b in rec['births'] if u in b['parents'] and b['implied']]
            how = 'gave its last to a birth that closed' if closers else 'gave every usable loose distinction to births'
        out[how] += 1
    return dict(out)


def first_joint_births(run, X, Y, s, upto=None):
    """DB 3.2: births with one parent descended from X only and one from Y only; the first round with any."""
    upto = upto or run.rounds_done
    for t in range(s + 1, upto + 1):
        Sb = run.snap[t - 1]
        desc = mc.descent_map(Sb, X, Y, s)
        js = [b for b in run.records[t - 1]['births']
              if any(desc.get(p) == 'X only' for p in b['parents']) and any(desc.get(p) == 'Y only' for p in b['parents'])]
        if js:
            return {'round': t, 'births': [{'knot': b['id'], 'parents': b['parents'], 'kind': b['kind']} for b in js[:8]],
                    'n': len(js)}
    return None


def side_sets(S, X, Y, s):
    desc = mc.descent_map(S, X, Y, s)
    yo = {u for u, d in desc.items() if d == 'Y only'}
    xo = {u for u, d in desc.items() if d == 'X only'}
    return desc, xo, yo
