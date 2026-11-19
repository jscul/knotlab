"""Shared-runner job for PROVE-B-20261119-001B part M (Amendment 1): Claim B on reached stages whose starts meet once.
Starts: PARENT-RULE part S's 503,039 legal meet-once arrangements of 2 to 7 junctions (the same enumeration and cases).  Each is
grown by the census's law; the start itself (round 0: Claim B for meet-once arrangements in general) and its stage of round 1,
each with at most 14 junctions, are tested against their next stage, and counted apart ('start' and 'reached').  A
stage whose table has a discrete Weisfeiler-Leman colouring has no table symmetry but the identity and is skipped (counted).
Otherwise test_stage_fast: every table symmetry that could keep the round's reading (VF2 restricted by loose and live-star
labels), one per coset of holder-class permutations, holder-breaking ones included (cap 20,000); those carrying the equations skipped; for those keeping the round's reading, the extension checked entry by entry on
the next stage (bonds when at most 15 vertices, else exact_table_v2 with no bound, under a 300 s alarm).  A failure is a
counterexample to Claim B on a reached stage from a meet-once start."""
import importlib.util
import itertools
import signal
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reached_job as RJ  # noqa: E402
EX, L = RJ.EX, RJ.L
_s = importlib.util.spec_from_file_location('static_job_pb', ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_job.py')
SJ = importlib.util.module_from_spec(_s)
sys.modules[_s.name] = SJ
_s.loader.exec_module(SJ)
FULL = 14
NMAX_START = 6  # the hunt covers starts of at most 6 junctions (all of them); 7-junction cases are skipped


def setup(params):
    SJ.atlas()


def cases():
    for cid, p in SJ.cases():
        if p['n'] <= NMAX_START:
            yield cid, p


def reading_colours(stars, tab, labels):
    """The table graph, its Weisfeiler-Leman colours refined by what any reading-keeping isometry must keep: whether a
    distinction is loose, and whether it lies on a live junction.  Restricting VF2 by these is sound for finding the
    reading-keeping isometries, which are the only ones tested."""
    own = L.owners(stars)
    live = set(L.live_set(stars, own))
    g = L.coloured(tab, labels)
    for x in labels:
        g.nodes[x]['k'] = (g.nodes[x]['k'], len(own[x]) == 1, any(j in live for j in own[x]))
    return g


def test_stage_fast(a, a1, c, examples, where, table=None):
    """reached_job.test_stage, with VF2 restricted by reading_colours (cosets of holder-class permutations, holder-breaking
    isometries included)."""
    ta, la = table if table is not None else L.table(a)
    idx = {x: i for i, x in enumerate(la)}
    wa = [sum(1 << idx[x] for x in s) for s in a]
    ra = L.rank(wa)
    R = EX.reading(a)
    own = L.owners(a)
    classes = {}
    for x in la:
        classes.setdefault(tuple(sorted(own[x])), []).append(x)
    cls_of = {x: [y for y in v if y != x] for v in classes.values() if len(v) > 1 for x in v}
    g = reading_colours(a, ta, la)
    m = RJ.CosetMatcher(g, g, cls_of, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    t1 = None
    n = 0
    for phi in m.isomorphisms_iter():
        n += 1
        if n > RJ.CAP_ISO:
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
        c['of_which_break_holder_classes'] += any(tuple(sorted(own[x])) != tuple(sorted(own[phi[x]])) for x in la)
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
            examples.append({'where': where, 'stage': [sorted(s) for s in a], 'swap': {str(k): v for k, v in phi.items() if k != v}})


def discrete(stars):
    """(whether the table's Weisfeiler-Leman colouring is discrete, the table)"""
    tab, labels = L.table(stars)
    g = L.coloured(tab, labels)
    ks = [d['k'] for _, d in g.nodes(data=True)]
    return len(set(ks)) == len(ks), (tab, labels)


def run(case_id, p):
    G = dict(SJ.atlas())
    c = Counter()
    examples = []
    for gi in p['graphs']:
        g = nx.convert_node_labels_to_integers(G[gi])
        n = g.number_of_nodes()
        auts = [tuple(m[i] for i in range(n)) for m in nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
        for ell in itertools.product(range(SJ.lmax(n) + 1), repeat=n):
            if any(tuple(ell[s[i]] for i in range(n)) < ell for s in auts):
                continue
            if not SJ.legal(g, ell):
                continue
            c['starts'] += 1
            start = SJ.arrangement(g, ell)
            P = EX.C.S.from_junctions([sorted(s) for s in start])
            stages = [[frozenset(s) for s in P.bits_of]]  # round 0, the start itself: Claim B for meet-once arrangements in general
            for r in range(1, 3):
                res = P.step(EX.C.S.gf2(EX.C.F.fewest), None)
                if res is None or res['new'] == 0:
                    break
                stages.append([frozenset(b) for b in P.bits_of])
            for r in range(len(stages) - 1):
                cur, nxt = stages[r], stages[r + 1]
                if len(cur) > FULL or not L.live_set(cur):
                    continue
                kind = 'start' if r == 0 else 'reached'
                c[f'{kind}_open_stages'] += 1
                disc, tab = discrete(cur)
                if disc:
                    c[f'{kind}_without_symmetry'] += 1
                    continue
                c0 = Counter()
                signal.signal(signal.SIGALRM, EX._late)
                signal.alarm(RJ.LIMIT)
                try:
                    test_stage_fast(cur, nxt, c0, examples, {'atlas': gi, 'loose': list(ell), 'round': r}, tab)
                except EX.Late:
                    c0['late'] += 1
                finally:
                    signal.alarm(0)
                for k, v in c0.items():
                    c[f'{kind}_{k}'] += v
                continue
                signal.signal(signal.SIGALRM, EX._late)
                signal.alarm(RJ.LIMIT)
                try:
                    RJ.test_stage(cur, nxt, c, examples, {'atlas': gi, 'loose': list(ell), 'round': r})
                except EX.Late:
                    c['late'] += 1
                finally:
                    signal.alarm(0)
    return {'counts': dict(c), 'examples': examples}
