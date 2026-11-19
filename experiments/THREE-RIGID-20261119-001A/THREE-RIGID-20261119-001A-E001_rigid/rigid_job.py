"""Shared-runner job for THREE-RIGID-20261119-001A: three-way rigidity on reached stages.

For a stage a: every isometry of its full bond-distance table onto itself, one per coset of holder-class permutations,
holder-breaking ones included (PROVE-B's CosetMatcher), with VF2 restricted by each distinction's multiset of three-way readings
(an invariant of every three-way-keeping symmetry, so the restriction loses none of them; cap 20,000).  Each is tested for keeping
every three-way reading (smallest bond holding three distinctions, less one, or none; from every bond) and for carrying the
equation space.  A symmetry that keeps pair and three-way readings but not the equations is a counterexample to three-way
rigidity; whether it also keeps the round's reading (EXTEND-ROUND's R) is recorded, since such a one would refute the three-way
form of Claim B only if, in addition, its extension failed (checked).
Populations (stages of round >= 1 with at most 14 junctions, open or closed):
- census: every census start (TOUCH-CENSUS, at most five knots), rounds 1 to 8;
- small: PROVE-B part B's 35,735 starts of 3 or 4 knots sharing up to 4 (3) distinctions, rounds 1 to 3;
- meet7: PARENT-RULE part S's legal meet-once starts of 7 junctions (417,297), round 1 (where Codex's meet-once failure lives).
Control: Codex's two reached counterexamples and Proposition X, whose failing swaps must be found and must break three-way
readings.  Also recorded per stage (the advisor's discriminator): whether the bonds of at most three distinctions span the
equations, in which case the lemma settles the stage."""
import importlib.util
import itertools
import signal
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_r = importlib.util.spec_from_file_location('reached_job_tr', ROOT / 'experiments/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt/reached_job.py')
RJ = importlib.util.module_from_spec(_r)
sys.modules[_r.name] = RJ
_r.loader.exec_module(RJ)
EX, L = RJ.EX, RJ.L
_s = importlib.util.spec_from_file_location('static_job_tr', ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_job.py')
SJ = importlib.util.module_from_spec(_s)
sys.modules[_s.name] = SJ
_s.loader.exec_module(SJ)
FULL = 14
CAP = 20000
LIMIT = 600
SPLIT_CENSUS = 100
SPLIT_SMALL = 12


def three(stars):
    p3 = {}
    for b in L.bonds(stars):
        k = len(b) - 1
        for t in combinations(sorted(b), 3):
            if p3.get(t, 10 ** 9) > k:
                p3[t] = k
    return p3


def check_stage(a, c, examples, where, nxt=None):
    ta, la = L.table(a)
    p3 = three(a)
    own = L.owners(a)
    # the advisor's discriminator: if the bonds of at most three distinctions span the equations, a symmetry keeping pair and
    # three-way readings maps them onto such bonds and so carries the equations (the lemma); a counterexample needs a deficit
    idx0 = {x: i for i, x in enumerate(la)}
    small = [sum(1 << idx0[x] for x in b) for b in L.bonds(a) if len(b) <= 3]
    r_small = L.rank(small)
    r_eq = L.rank([sum(1 << idx0[x] for x in s) for s in a])
    c['stages_spanned_by_small_bonds' if r_small == r_eq else 'stages_with_a_deficit'] += 1
    inv = {x: [] for x in la}
    for t, v in p3.items():
        for x in t:
            inv[x].append(v)
    g = L.coloured(ta, la)
    for x in la:
        g.nodes[x]['k'] = (g.nodes[x]['k'], tuple(sorted(inv[x])))
    ks = [d['k'] for _, d in g.nodes(data=True)]
    if len(set(ks)) == len(ks):
        c['stages_rigid_by_colours'] += 1
        return
    classes = {}
    for x in la:
        classes.setdefault(tuple(sorted(own[x])), []).append(x)
    cls_of = {x: [y for y in v if y != x] for v in classes.values() if len(v) > 1 for x in v}
    m = RJ.CosetMatcher(g, g, cls_of, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    idx = {x: i for i, x in enumerate(la)}
    wa = [sum(1 << idx[x] for x in s) for s in a]
    ra = L.rank(wa)
    R = EX.reading(a) if L.live_set(a) else None
    n = 0
    for phi in m.isomorphisms_iter():
        n += 1
        if n > CAP:
            c['capped_stages'] += 1
            break
        keeps3 = all(p3.get(tuple(sorted(phi[x] for x in t)), None) == v for t, v in p3.items())
        if not keeps3:
            c['symmetries_breaking_three_way'] += 1
            continue
        mapped = [sum(1 << idx[phi[x]] for x in s) for s in a]
        if L.rank(wa + mapped) == ra:
            c['three_way_keeping_carry_equations'] += 1
            continue
        c['THREE_WAY_RIGIDITY_COUNTEREXAMPLES'] += 1
        rk = R is not None and EX.keeps_reading(phi, a, a, R, R) is not None
        c['of_which_keep_reading'] += rk
        rec = {'where': where, 'stage': [sorted(s) for s in a], 'phi': {str(k): v for k, v in phi.items() if k != v}, 'keeps_reading': rk}
        if rk and nxt is not None:
            psi = EX.keeps_reading(phi, a, a, R, R)
            phi2 = EX.extension(phi, psi, a, a, nxt, nxt)
            t1, _ = EX.full_table(nxt)
            ok = phi2 is not None and all(t1[(x, y)] == t1[tuple(sorted((phi2[x], phi2[y])))] for (x, y) in t1)
            c['of_which_extend' if ok else 'of_which_fail_to_extend_CLAIM_B3'] += 1
            rec['extends'] = ok
        if len(examples) < 10:
            examples.append(rec)
    c['stages_searched'] += 1


def guarded(a, c, examples, where, nxt=None):
    signal.signal(signal.SIGALRM, EX._late)
    signal.alarm(LIMIT)
    try:
        check_stage(a, c, examples, where, nxt)
    except EX.Late:
        c['late'] += 1
    finally:
        signal.alarm(0)


def setup(params):
    SJ.atlas()


def cases():
    n_census = 26441
    for s in range(0, n_census, SPLIT_CENSUS):
        yield f'census-{s // SPLIT_CENSUS:04d}', {'pop': 'census', 'lo': s, 'hi': min(n_census, s + SPLIT_CENSUS)}
    for cid, p in RJ.cases():
        yield f'small-{cid}', dict(p, pop='small')
    for cid, p in SJ.cases():
        if p['n'] == 7:
            yield f'meet7-{cid}', dict(p, pop='meet7')


def grow_stages(start, rounds):
    P = EX.C.S.from_junctions([sorted(s) for s in start])
    out = []
    for _ in range(rounds + 1):
        res = P.step(EX.C.S.gf2(EX.C.F.fewest), None)
        if res is None or res['new'] == 0:
            break
        out.append([frozenset(b) for b in P.bits_of])
    return out


def run(case_id, p):
    c = Counter()
    examples = []
    if p['pop'] == 'census':
        data = EX.C.CJ.load()
        for i in range(p['lo'], p['hi']):
            st = grow_stages([frozenset(s) for s in EX.C.A.stars_of(data[i])], 8)
            for r, a in enumerate(st, 1):
                if len(a) > FULL:
                    break
                if r > 8:
                    break
                c['stages'] += 1
                guarded(a, c, examples, ('census', i, r), st[r] if r < len(st) else None)
    elif p['pop'] == 'small':
        g = RJ.graphs()[p['graph']]
        for j, (stars, mult, ell) in enumerate(RJ.starts(g, p['first'])):
            if j % RJ.SPLIT != p['part']:
                continue
            st = grow_stages(stars, 3)
            for r, a in enumerate(st, 1):
                if len(a) > FULL or r > 3:
                    break
                c['stages'] += 1
                guarded(a, c, examples, ('small', list(mult), list(ell), r), st[r] if r < len(st) else None)
    else:
        G = dict(SJ.atlas())
        for gi in p['graphs']:
            g = nx.convert_node_labels_to_integers(G[gi])
            n = g.number_of_nodes()
            auts = [tuple(m[i] for i in range(n)) for m in nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
            for ell in itertools.product(range(SJ.lmax(n) + 1), repeat=n):
                if any(tuple(ell[s[i]] for i in range(n)) < ell for s in auts):
                    continue
                if not SJ.legal(g, ell):
                    continue
                st = grow_stages(SJ.arrangement(g, ell), 1)
                if not st or len(st[0]) > FULL:
                    continue
                c['stages'] += 1
                guarded(st[0], c, examples, ('meet7', gi, ''.join(map(str, ell)), 1), st[1] if len(st) > 1 else None)
    return {'counts': dict(c), 'examples': examples}
