"""Run 4b and its probe: every choice of the uniform takes enumerated (PR, Settled 3), and KD 7.3's numberings.

A history is the sequence of the takes' choices, in the engine's birth order; its weight under uniform takes is the
product of 1/(number of candidates) over its decisions.  Histories are enumerated by an odometer over that sequence:
each history is grown again from the start with a chooser that follows the prefix and takes the first candidate after
it (the candidate counts of a history depend only on its earlier choices)."""
from __future__ import annotations

import time
from fractions import Fraction

import networkx as nx

import kwr

pm = kwr.pm


def numberings(stars, rng=None, further=0):
    """KD 7.3: the 4n numberings of a start (n distinctions named 0..n-1 by FD 2.1, m knots): for k = 0..n-1 the
    renaming i -> (i + k) mod n or i -> (n - 1 - i + k) mod n, each with the knots in their given order or reversed;
    then `further` numberings from random.Random(202611252) (shuffle of range(n), then of range(m))."""
    labels = sorted({d for s in stars for d in s})
    n, m = len(labels), len(stars)
    name = {lab: i for i, lab in enumerate(labels)}
    out = []
    for k in range(n):
        for refl in (False, True):
            for rev in (False, True):
                if refl:
                    st = [[(n - 1 - name[d] + k) % n for d in s] for s in stars]
                else:
                    st = [[(name[d] + k) % n for d in s] for s in stars]
                if rev:
                    st = st[::-1]
                out.append({'id': 'k%d%s%s' % (k, 'r' if refl else '', 'K' if rev else ''), 'stars': st})
    if further:
        import random
        R = random.Random(202611252)
        for i in range(further):
            perm = list(range(n))
            R.shuffle(perm)
            ko = list(range(m))
            R.shuffle(ko)
            st = [[perm[name[d]] for d in stars[j]] for j in ko]
            out.append({'id': 'f%d' % i, 'stars': st})
    return out


class Script:
    def __init__(self, script):
        self.script = script
        self.opts = []

    def __call__(self, key, cands):
        i = len(self.opts)
        c = self.script[i] if i < len(self.script) else 0
        self.opts.append(len(cands))
        return cands[c]


def grow_with(stars, law, rounds, chooser, knot_bound=kwr.KNOT_BOUND):
    S = pm.from_stars(stars)
    stop = None
    while S.round < rounds:
        N, Dn = S.n_knots, S.n_distinctions
        barred, cand = list(S.barred), set(S.cand)
        try:
            rec = pm.round_step(S, law, {'chooser': chooser})
        except pm.GuardStop:
            kwr.rollback(S, N, Dn, barred, cand)
            stop = 'guard'
            break
        if rec['stalled'] or rec['stopped'] or rec['jammed']:
            stop = 'ended'
            break
        if S.n_knots > knot_bound:
            stop = 'knots'
            break
    return S, stop


def structure_graph(S):
    """The structure with its birth record, as a labelled directed graph (knots: kind and round; distinctions:
    barred; knot -> distinction 'holds'; knot -> parent 'parent'), for isomorphism up to renaming."""
    G = nx.DiGraph()
    for u in range(S.n_knots):
        G.add_node(('k', u), lab='k:%s:%d' % (S.kind[u], S.made[u]))
    for d in range(S.n_distinctions):
        G.add_node(('d', d), lab='d:%d' % int(S.barred[d]))
    for u in range(S.n_knots):
        for d in S.places[u]:
            G.add_edge(('k', u), ('d', d), lab='h')
        for p in S.parents[u]:
            G.add_edge(('k', u), ('k', p), lab='p')
    return G


def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr='lab', edge_attr='lab', iterations=4)


def enumerate_case(stars, law, rounds, cap=100000, deadline=None, keep=True):
    """All histories of one numbering: [(graph, weight)], or None when more than `cap` histories or past deadline."""
    script = []
    out = []
    while True:
        ch = Script(script)
        S, stop = grow_with(stars, law, rounds, ch)
        w = Fraction(1)
        for k in ch.opts:
            w /= k
        out.append((S, w) if keep else w)
        if len(out) > cap or (deadline is not None and time.time() > deadline):
            return None, len(out)
        full = script + [0] * (len(ch.opts) - len(script))
        i = len(full) - 1
        while i >= 0 and full[i] + 1 >= ch.opts[i]:
            i -= 1
        if i < 0:
            break
        script = full[:i] + [full[i] + 1]
    return out, len(out)


def enumerate_classes(stars, law, rounds, classes, cap=100000, deadline=None):
    """Streaming: every history of one numbering, each final structure added at once to the isomorphism classes
    (only one representative graph per class is kept).  Returns ({class index: weight}, histories) or (None, n)."""
    script = []
    acc = {}
    n = 0
    while True:
        ch = Script(script)
        S, stop = grow_with(stars, law, rounds, ch)
        w = Fraction(1)
        for k in ch.opts:
            w /= k
        n += 1
        a = classes_of([(S, w)], classes)
        for i, x in a.items():
            acc[i] = acc.get(i, Fraction(0)) + x
        if n > cap or (deadline is not None and time.time() > deadline):
            return None, n
        full = script + [0] * (len(ch.opts) - len(script))
        i = len(full) - 1
        while i >= 0 and full[i] + 1 >= ch.opts[i]:
            i -= 1
        if i < 0:
            break
        script = full[:i] + [full[i] + 1]
    return acc, n


def classes_of(histories, classes):
    """Add the weights of the histories to the isomorphism classes (list of [hash, graph, {numbering: weight}])."""
    acc = {}
    if isinstance(classes, list):
        raise TypeError('classes must be a Classes()')
    for S, w in histories:
        G = structure_graph(S)
        h = wl(G)
        found = None
        for i, GG in classes.by_hash.get(h, []):
            if nx.is_isomorphic(G, GG, node_match=lambda a, b: a['lab'] == b['lab'],
                                edge_match=lambda a, b: a['lab'] == b['lab']):
                found = i
                break
        if found is None:
            found = classes.n
            classes.n += 1
            classes.by_hash.setdefault(h, []).append((found, G))
        acc[found] = acc.get(found, Fraction(0)) + w
    return acc


class Classes:
    """Isomorphism classes of structures with their birth record, indexed by Weisfeiler-Lehman hash."""

    def __init__(self):
        self.by_hash = {}
        self.n = 0

    def __len__(self):
        return self.n
