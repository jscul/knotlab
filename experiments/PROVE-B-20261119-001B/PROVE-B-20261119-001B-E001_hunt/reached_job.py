"""Shared-runner job for PROVE-B-20261119-001B: hunt a counterexample to Claim B in reached stages, where the advisor's
configuration (a junction whose edges split evenly between two holders, a class-breaking table symmetry swapping one edge of each,
and a tie broken by a join's discount) could arise.

Starts: every connected junction multigraph on 3 junctions (shared multiplicities 1 to 4) or 4 junctions (multiplicities 1 to 3),
with 0 to 3 loose distinctions per junction, legal (every junction at least 3 distinctions, no cut vertex but the
outside one), one per orbit of the underlying multigraph's automorphisms.  Each start is grown by complete rounds under the
census's law (cheapest counts, elimination over GF(2)), rounds 1 to 3, while stages keep at most 14 junctions.
For every open stage of round 1 or later: every isometry of its full table onto itself, one per coset of holder-class
permutations (images of each holder class in increasing order), including those that break holder classes (VF2 on the full table,
cap 20,000 enumerated); those that carry the equations are skipped (Claim B*); for those that keep what the round reads, the
extension is checked entry by entry against the next stage's full table (bonds when at most 15 vertices, else exact_table_v2 with
no bound, under a 300 s alarm per stage).  A failure is a counterexample to Claim B in a reached stage.
Cases: one per (underlying simple graph, multiplicity of its first edge, one of 12 interleaved parts).  Control (control.py): the advisor's 7-junction start,
which must fail."""
import importlib.util
import itertools
import signal
import sys
from collections import Counter
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_e = importlib.util.spec_from_file_location('extend_round', ROOT / 'experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.py')
EX = importlib.util.module_from_spec(_e)
sys.modules[_e.name] = EX
_e.loader.exec_module(EX)
L = EX.L
C = EX.C
FULL = 14
ROUNDS = 3
CAP_ISO = 20000
LIMIT = 300
MULT3 = (1, 2, 3, 4)
MULT4 = (1, 2, 3)
LOOSE = (0, 1, 2, 3)


def graphs():
    out = []
    for g in nx.graph_atlas_g():
        if g.number_of_nodes() in (3, 4) and nx.is_connected(g):
            out.append(nx.convert_node_labels_to_integers(g))
    return out


def setup(params):
    pass


SPLIT = 12


def cases():
    for i, g in enumerate(graphs()):
        for m0 in (MULT3 if g.number_of_nodes() == 3 else MULT4):
            for k in range(SPLIT):
                yield f'g{i:02d}-m{m0}-{k:02d}', {'graph': i, 'first': m0, 'part': k}


def starts(g, first):
    n = g.number_of_nodes()
    edges = sorted(g.edges())
    auts = [m for m in isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
    seen = set()
    M = MULT3 if n == 3 else MULT4
    for rest in itertools.product(M, repeat=len(edges) - 1):
        mult = (first,) + rest
        for ell in itertools.product(LOOSE, repeat=n):
            key = None
            for m in auts:  # the orbit key: the least image
                em = tuple(sorted((tuple(sorted((m[u], m[v]))), k) for (u, v), k in zip(edges, mult)))
                lm = tuple(ell[[w for w in range(n) if m[w] == j][0]] for j in range(n))
                cand = (em, lm)
                key = cand if key is None or cand < key else key
            # this case owns the orbit only when the orbit's least image has this first-edge multiplicity
            if key[0][0][1] != first or key in seen:
                continue
            seen.add(key)
            stars = [set() for _ in range(n)]
            b = 0
            for (u, v), k in zip(edges, mult):
                for _ in range(k):
                    stars[u].add(b)
                    stars[v].add(b)
                    b += 1
            for j, k in enumerate(ell):
                for _ in range(k):
                    stars[j].add(b)
                    b += 1
            if any(len(s) < 3 for s in stars):
                continue
            h = g.copy()
            for j in range(n):
                if ell[j]:
                    h.add_edge(j, 'o')
            if set(nx.articulation_points(h)) - {'o'}:
                continue
            yield [frozenset(s) for s in stars], mult, ell


class CosetMatcher(isomorphism.GraphMatcher):
    """VF2 restricted to one representative per coset of holder-class permutations: inside each holder class of the first
    graph, the images increase.  Enforced during the search, so the twins' factorial is never enumerated."""

    def __init__(self, g1, g2, cls_of, **kw):
        super().__init__(g1, g2, **kw)
        self.cls_of = cls_of

    def semantic_feasibility(self, n1, n2):
        if not super().semantic_feasibility(n1, n2):
            return False
        for y in self.cls_of.get(n1, ()):
            if y in self.core_1:
                if (y < n1) != (self.core_1[y] < n2):
                    return False
        return True


def coset_reps(stars, tab, labels):
    """Table self-isometries, one per coset of holder-class permutations (images of each holder class in increasing order),
    including isometries that break holder classes."""
    own = L.owners(stars)
    classes = {}
    for x in labels:
        classes.setdefault(tuple(sorted(own[x])), []).append(x)
    cls_of = {x: [y for y in v if y != x] for v in classes.values() if len(v) > 1 for x in v}
    g = L.coloured(tab, labels)
    m = CosetMatcher(g, g, cls_of, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    n = 0
    for phi in m.isomorphisms_iter():
        n += 1
        if n > CAP_ISO:
            yield 'cap'
            return
        yield phi


def test_stage(a, a1, c, examples, where):
    ta, la = L.table(a)
    idx = {x: i for i, x in enumerate(la)}
    wa = [sum(1 << idx[x] for x in s) for s in a]
    ra = L.rank(wa)
    R = EX.reading(a)
    t1 = None
    for phi in coset_reps(a, ta, la):
        if phi == 'cap':
            c['capped_stages'] += 1
            break
        mapped = [sum(1 << idx[phi[x]] for x in s) for s in a]
        if L.rank(wa + mapped) == ra:
            c['carrying_equations'] += 1
            continue
        psi = EX.keeps_reading(phi, a, a, R, R)
        if psi is None:
            c['not_keeping_reading'] += 1
            continue
        c['keeping_reading_not_equations'] += 1
        own = L.owners(a)
        breaks = any(tuple(sorted(own[x])) != tuple(sorted(own[phi[x]])) for x in la)
        c['of_which_break_holder_classes'] += breaks
        phi2 = EX.extension(phi, psi, a, a, a1, a1)
        if phi2 is None:
            c['rounds_do_not_correspond'] += 1
            continue
        if t1 is None:
            t1 = EX.full_table(a1)
        ta1, la1 = t1
        ok = all(ta1[(x, y)] == ta1[tuple(sorted((phi2[x], phi2[y])))] for (x, y) in ta1)
        c['extensions_isometry' if ok else 'extensions_fail_CLAIM_B'] += 1
        if not ok and len(examples) < 10:
            examples.append({'where': where, 'stage': [sorted(s) for s in a],
                             'swap': {str(k): v for k, v in phi.items() if k != v}})


def run(case_id, p):
    g = graphs()[p['graph']]
    c = Counter()
    examples = []
    for j, (stars, mult, ell) in enumerate(starts(g, p['first'])):
        if j % SPLIT != p['part']:
            continue
        c['starts'] += 1
        P = C.S.from_junctions([sorted(s) for s in stars])
        cur = [frozenset(s) for s in P.bits_of]
        for r in range(1, ROUNDS + 2):
            res = P.step(C.S.gf2(C.F.fewest), None)
            if res is None or res['new'] == 0:
                break
            nxt = [frozenset(b) for b in P.bits_of]
            if r >= 2 and len(cur) <= FULL and L.live_set(cur):
                c['open_stages'] += 1
                signal.signal(signal.SIGALRM, EX._late)
                signal.alarm(LIMIT)
                try:
                    test_stage(cur, nxt, c, examples, {'mult': list(mult), 'loose': list(ell), 'round': r - 1})
                except EX.Late:
                    c['late'] += 1
                finally:
                    signal.alarm(0)
            cur = nxt
            if len(cur) > FULL + 30:
                break
    return {'counts': dict(c), 'examples': examples}
