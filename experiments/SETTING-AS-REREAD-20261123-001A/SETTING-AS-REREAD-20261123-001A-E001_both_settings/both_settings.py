"""SETTING-AS-REREAD-20261123-001A-E001: checks (a) to (f) and row G of the frozen note.

Frozen design: research/SETTING-AS-REREAD-20261123-001A/preregistration.md ("Definitions (frozen)", "Predictions
(frozen)", "Runs and stop rule").  Readings taken where the note leaves a choice: deviations.md of this folder, written
before the runs.

Recorded code reused read-only, imported by path and never changed (sha256 asserted at import):
  * qlaw.py of ONE-PARENT-REREAD-20261123-001A-E001: class QGrowth (rule Q on full holdings), the engine of record for
    check (a), (e) and row G (1).  Through it rlaw.py of REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001 (qlaw sets
    rlaw.USE_C = False at import, asserted here, so nothing is built in another ticket's folder), the review-leads
    lib.py (p3_draws, grow) and the recorded end_operator.py.
  * docs/prompts/missed_leads_checks/finished_weighting_chsh.py executed up to its section 1 (gives evaluate(M)), as
    REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B common.load_starter does.  Row G (2) only.
Written here, independently of every thread check script: a round-1 planner for rule Q (`plan_round1`, from the
definitions of end_operator and qlaw, used as a cross-check of QGrowth), the word-by-word enumeration of every
stage-1 structure, the joint distribution of the complete records in exact integers, hiding, and the three scores.

Parts (one per run):
  g_draws  row G (1): QGrowth with re-reading off against the recorded driver lib.grow on the 280 funded sparse draws
           under not-all-equal (12 rounds, 5,000 knots: stars, knots per stage, outcome).  Beside it: plan_round1
           against end_operator.step (re-reading off) and against QGrowth (re-reading on, conventions O and N) on
           round 1 of the same draws.
  main     checks (a), (b), (c), (d) and row G (2).
  e        check (e): every structure with one or two of the eleven knots left out.
  f        check (f): every even/odd assignment of the nine parity knots (--lo/--hi slice the 512).
usage (repo root):
  OMP_NUM_THREADS=1 timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --part P [--lo L --hi H]
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
ART = ROOT / 'artifacts' / TICKET / HERE.name

INPUTS = {
    'preregistration': ('research/SETTING-AS-REREAD-20261123-001A/preregistration.md',
                        '2fe6c5101d0fdcd92fa24ed9507abad7104872c66139e4d73c9b4ecb34540cd9'),
    'qlaw': ('experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/qlaw.py',
             '457abaa5a05e05785282b31dcd5f58a5eb6181f0a1a7adf7df81d4867c747942'),
    'rlaw': ('experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/rlaw.py',
             '29aa3d9112d4a12b2d7970756c455e11dd3ed7abaef99b85daa64f4c4222d8f8'),
    'lib': ('experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test/lib.py',
            'c2bfbfd88aad35907fb4010bc43ab0454cbc53446145323050f697b831a9ae21'),
    'scorer': ('docs/prompts/missed_leads_checks/finished_weighting_chsh.py',
               'ec55774ae031b2d72f07a3cddc086d9d2f562b808fb5514d339f4621714b4194'),
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


for _k, (_p, _h) in INPUTS.items():
    assert sha256(ROOT / _p) == _h, f'{_k} differs from the recorded file'


def load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


Q = load_by_path('qlaw', ROOT / INPUTS['qlaw'][0])
assert Q.rlaw.USE_C is False


def load_scorer():
    """The recorded scorer's definitions, executed up to its section 1 (as REREAD...-001B common.load_starter)."""
    path = ROOT / INPUTS['scorer'][0]
    src = path.read_text()
    cut = src.index('# ---- 1. a four-type preparation')
    ns = {'__name__': 'starter'}
    exec(compile(src[:cut], str(path), 'exec'), ns)
    return ns['evaluate']


# ======================================================================================================================
# The structure (pre-registration, "The structure").  Alice's knots first, then Bob's, in the note's order.
# ======================================================================================================================
KNOTS = [
    ('even', ('x1', 'x2', 'x3', 'c')),     # 0  Alice's live knot (loose x1)
    ('nae', ('c', 'x2', 's1')),           # 1
    ('nae', ('c', 'x3', 's2')),           # 2
    ('even', ('x2', 'h1', 'h2')),         # 3
    ('odd', ('x3', 'h1', 'h2')),          # 4
    ('even', ('y1', 'y2', 'y3', 't')),     # 5  Bob's live knot (loose y1)
    ('even', ('t', 'm1', 'm2')),          # 6
    ('even', ('s1', 'm1', 'm2')),         # 7
    ('even', ('y2', 'k1', 'k2')),         # 8
    ('odd', ('y3', 'k1', 'k2')),          # 9
    ('odd', ('s2', 'k1', 'k2')),          # 10
]
SIDE = ['A'] * 5 + ['B'] * 6
PARITY_KNOTS = [k for k, (law, _) in enumerate(KNOTS) if law in ('even', 'odd')]   # the nine parity knots
OLD_NAMES = []                       # first appearance along the knots (deviations A2)
for _law, _mem in KNOTS:
    for _x in _mem:
        if _x not in OLD_NAMES:
            OLD_NAMES.append(_x)
NAME_ID = {x: i for i, x in enumerate(OLD_NAMES)}
ID_NAME = {i: x for x, i in NAME_ID.items()}
OPTS_A = ('x2', 'x3', 'c')           # the note's order; checked against the planner's options
OPTS_B = ('y2', 'y3', 't')
OWN_A = ['x1', 'x2', 'x3', 'c', 's1', 's2', 'h1', 'h2', 'zA']                   # held by Alice's knots, with her fresh
OWN_B = ['y1', 'y2', 'y3', 't', 'm1', 'm2', 's1', 'k1', 'k2', 's2', 'zB']        # held by Bob's knots, with his fresh
PLACEMENTS = ((0, 0), (0, 1), (1, 0), (1, 1))


def frac(x):
    return None if x is None else str(Fraction(x))


# ======================================================================================================================
# Round 1 of rule Q: an independent planner (from the definitions of end_operator.py and qlaw.py), and QGrowth.
# ======================================================================================================================
def _maximal(sets):
    """Inclusion-maximal sets among those with at least two members, as sorted tuples."""
    cand = {frozenset(s) for s in sets if len(s) >= 2}
    return sorted(tuple(sorted(s)) for s in cand if not any(s < o for o in cand))


def _groups(nodes, blocks):
    """end_operator's groups: every maximal set of three or more pairwise adjacent knots held by no one witnessed set
    (sorted), then every adjacent pair in none of them (sorted).  Adjacent: together in some witnessed set."""
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for b in blocks:
        g.add_edges_from(itertools.combinations(b, 2))
    bsets = [set(b) for b in blocks]
    big = sorted(tuple(sorted(c)) for c in nx.find_cliques(g) if len(c) >= 3 and not any(set(c) <= b for b in bsets))
    covered = {p for c in big for p in itertools.combinations(c, 2)}
    pairs = sorted(e for e in (tuple(sorted(e)) for e in g.edges) if e not in covered)
    return tuple(big) + tuple(pairs)


def plan_round1(stars, reread=True, choice=None, convention='O'):
    """One round of ordinary growth (reread=False) or rule Q on full holdings, every newborn not-all-equal (no closing).

    stars: list of tuples of distinction ids.  choice: {birth index: distinction} for re-reading births (else the
    convention: O smallest id, N largest).  Returns a dict with status, parents, inputs, options, demand, fresh."""
    holders = defaultdict(list)
    for k, s in enumerate(stars):
        assert len(set(s)) == len(s)
        for d in s:
            holders[d].append(k)
    loose = {k: [d for d in s if len(holders[d]) == 1] for k, s in enumerate(stars)}
    loose = {k: v for k, v in loose.items() if v}
    if not loose:
        return dict(status='closed')
    opens = {k: len(loose[k]) for k in sorted(loose)}
    sets = [set(s) for s in stars]
    raw = [frozenset(k for k in opens if k != j and sets[k] & sets[j]) for j in range(len(stars))]
    blocks = _maximal(raw)
    groups = _groups(list(opens), blocks)
    used = Counter(v for gr in groups for v in gr)
    short = [(k, used[k] - opens[k]) for k in opens if used[k] > opens[k]]
    if short:
        return dict(status='stall', groups=[list(x) for x in groups], shortages=short, opens=opens)
    parents = list(groups) + [(k,) for k in opens for _ in range(opens[k] - used[k])]
    pool = {k: list(v) for k, v in loose.items()}
    inputs, options = [], []
    for i, ps in enumerate(parents):
        row = [pool[p].pop() for p in ps]          # loose distinctions, last listed first (rlaw, lib.grow)
        opt = None
        if reread and len(ps) == 1:
            sh = sorted(d for d in stars[ps[0]] if len(holders[d]) >= 2)   # shared at the start of the round
            if sh:
                opt = sh
                if choice is not None and i in choice:
                    d = choice[i]
                    assert d in sh
                else:
                    d = sh[0] if convention == 'O' else sh[-1]
                row.append(d)
        inputs.append(tuple(row))
        options.append(opt)
    assert not any(pool.values())
    # lookahead: births live with one opening; an old knot holding a taken distinction witnesses the births taking it;
    # births taking a common distinction witness each other
    takers = defaultdict(list)
    for i, row in enumerate(inputs):
        for d in row:
            takers[d].append(i)
    wit = defaultdict(set)
    for d, bs in takers.items():
        for h in holders[d]:
            wit[('old', h)].update(bs)
        if len(bs) > 1:
            for b in bs:
                wit[('new', b)].update(x for x in bs if x != b)
    groups2 = _groups(list(range(len(parents))), _maximal(wit.values()))
    cnt = Counter(v for gr in groups2 for v in gr)
    demand = [cnt[i] for i in range(len(parents))]
    fresh = [max(demand[i], 3 - len(inputs[i]), 1) for i in range(len(parents))]
    return dict(status='extend', parents=[tuple(p) for p in parents], inputs=inputs, options=options, demand=demand,
                fresh=fresh, groups=[list(x) for x in groups], opens=opens)


def q_round1(stars, choice=None, convention='O', reread=True):
    """Round 1 by the engine of record, QGrowth (law 'nae': every newborn not-all-equal, no closing; exact demand)."""
    g = Q.QGrowth([tuple(s) for s in stars], 'nae', convention, reread=reread, bound_next=False)
    r = g.plan(max_births=None, choice=choice)
    out = dict(status=r.status)
    if r.status == 'extend':
        out.update(parents=[tuple(p) for p in r.parents], inputs=[tuple(x) for x in r.inputs], fresh=list(r.fresh),
                   demand=list(r.demand), paid=[list(p) for p in r.paid])
    elif r.status == 'stall':
        out['shortages'] = [tuple(x) for x in r.shortages]
    return out


def same_round(mine, eng):
    if mine['status'] != eng['status']:
        return False
    if mine['status'] == 'extend':
        return (mine['parents'] == eng['parents'] and [tuple(x) for x in mine['inputs']] == eng['inputs']
                and mine['fresh'] == eng['fresh'] and mine['demand'] == eng['demand'])
    if mine['status'] == 'stall':
        return [tuple(x) for x in mine['shortages']] == eng['shortages']
    return True


def all_choices(plan):
    """Every choice of the round's re-reading births: list of {birth index: distinction}."""
    rr = [i for i, o in enumerate(plan['options']) if o]
    return [dict(zip(rr, ds)) for ds in itertools.product(*[plan['options'][i] for i in rr])]


# ======================================================================================================================
# Word-by-word enumeration.
# ======================================================================================================================
_BITS = {}


def _bits(n):
    if n not in _BITS:
        idx = np.arange(1 << n, dtype=np.int64)
        _BITS[n] = (idx, [((idx >> i) & 1).astype(np.int8) for i in range(n)])
    return _BITS[n]


def allowed_words(names, knots):
    """Every allowed word of the structure (knots over names), as int codes: bit i is the value of names[i]."""
    n = len(names)
    assert n <= 24
    pos = {x: i for i, x in enumerate(names)}
    idx, B = _bits(n)
    ok = np.ones(1 << n, dtype=bool)
    for law, mem in knots:
        s = B[pos[mem[0]]].copy()
        for x in mem[1:]:
            s += B[pos[x]]
        if law == 'even':
            ok &= (s & 1) == 0
        elif law == 'odd':
            ok &= (s & 1) == 1
        elif law == 'nae':
            ok &= (s > 0) & (s < len(mem))
        else:
            raise ValueError(law)
    return idx[ok], pos


def key_of(W, pos, rec):
    """Big-endian code of the record `rec` (a list of names) in each word."""
    k = np.zeros(len(W), dtype=np.int64)
    for x in rec:
        k = (k << 1) | ((W >> pos[x]) & 1)
    return k


def joint(W, pos, recA, recB, weights=None):
    kA, kB = key_of(W, pos, recA), key_of(W, pos, recB)
    J = np.zeros((1 << len(recA), 1 << len(recB)), dtype=np.int64)
    np.add.at(J, (kA, kB), 1 if weights is None else weights)
    return J


def dist_of(W, pos, names, weights=None):
    k = key_of(W, pos, names)
    out = np.zeros(1 << len(names), dtype=np.int64)
    np.add.at(out, k, 1 if weights is None else weights)
    return out


def same_dist(c1, c2):
    n1, n2 = int(c1.sum()), int(c2.sum())
    return bool(np.array_equal(c1 * n2, c2 * n1))


def tv(c1, c2):
    n1, n2 = int(c1.sum()), int(c2.sum())
    return sum((abs(Fraction(int(x), n1) - Fraction(int(y), n2)) for x, y in zip(c1, c2)), Fraction(0)) / 2


# ======================================================================================================================
# Hiding and the three scores, exact.
# ======================================================================================================================
def hidden_info(J, As, Bs):
    """J[(a, b)] for a in As, b in Bs.  Alice hidden: for each a her record has one distribution for every b."""
    out = {}
    for who, own, far in (('A', As, Bs), ('B', Bs, As)):
        ok, worst = True, Fraction(0)
        per = {}
        for o in own:
            margs = [(J[(o, f)].sum(1) if who == 'A' else J[(f, o)].sum(0)) for f in far]
            this = all(same_dist(m, margs[0]) for m in margs[1:])
            per[str(o)] = this
            ok &= this
            for m1, m2 in itertools.combinations(margs, 2):
                worst = max(worst, tv(m1, m2))
        out[who] = dict(hidden=bool(ok), per_own_choice=per, largest_change=str(worst))
    out['both'] = out['A']['hidden'] and out['B']['hidden']
    return out


def _signs(m):
    if m == 0:
        return np.ones((1, 0), dtype=np.int64)
    a = np.arange(1 << m, dtype=np.int64)[:, None]
    return 1 - 2 * ((a >> np.arange(m, dtype=np.int64)[None, :]) & 1)


def _scale(J):
    N = {ab: int(J[ab].sum()) for ab in PLACEMENTS}
    assert all(v > 0 for v in N.values())
    L = math.lcm(*N.values())
    return N, L, {ab: L // N[ab] for ab in PLACEMENTS}


def _dtype(L):
    return np.int64 if 4 * L < 2 ** 62 else object


def exact_value(J, A, B, k):
    """|E00 + E01 + E10 + E11 - 2 E_k| in Fractions from response functions A[a], B[b] (+-1 vectors over records)."""
    E = {ab: Fraction(int(np.asarray(A[ab[0]], dtype=object) @ J[ab].astype(object) @ np.asarray(B[ab[1]], dtype=object)),
                      int(J[ab].sum())) for ab in PLACEMENTS}
    return abs(sum(E.values()) - 2 * E[k]), E


def _merge(G):
    """Columns of G grouped by positive proportionality (zero columns dropped)."""
    groups = {}
    for col in range(G.shape[1]):
        v = G[:, col]
        if not v.any():
            continue
        g = math.gcd(*[int(x) for x in v])
        groups.setdefault(tuple(int(x) // g for x in v), []).append(col)
    return list(groups.values())


def _enum_cols(J, c, L, groups):
    """Enumerate every sign assignment of the merged column generators (both column settings); the row side answers
    best (sum of absolute values).  Returns (value * L, placement, row functions, column functions)."""
    dt = _dtype(L)
    RA = J[(0, 0)].shape[0]
    K = {}
    for (a, b) in PLACEMENTS:
        K[(a, b)] = (np.stack([J[(a, b)][:, g].sum(1) for g in groups[b]], axis=1) if groups[b]
                     else np.zeros((RA, 0), dtype=np.int64)).astype(dt)
    S = [_signs(len(groups[0])), _signs(len(groups[1]))]
    if len(groups[0]) > 0:            # the value is unchanged when every function is negated
        S[0] = S[0][S[0][:, 0] == 1]
    elif len(groups[1]) > 0:
        S[1] = S[1][S[1][:, 0] == 1]
    S = [x.astype(dt) for x in S]
    P = {(a, b): S[b] @ K[(a, b)].T for (a, b) in PLACEMENTS}
    best = None
    for k in PLACEMENTS:
        s = {ab: (-1 if ab == k else 1) for ab in PLACEMENTS}
        Q0 = [s[(a, 0)] * c[(a, 0)] * P[(a, 0)] for a in (0, 1)]
        Q1 = [s[(a, 1)] * c[(a, 1)] * P[(a, 1)] for a in (0, 1)]
        n0, n1 = Q0[0].shape[0], Q1[0].shape[0]
        chunk = max(1, (1 << 21) // max(1, n1 * RA))
        for i0 in range(0, n0, chunk):
            tot = 0
            for a in (0, 1):
                tot = tot + np.abs(Q0[a][i0:i0 + chunk, None, :] + Q1[a][None, :, :]).sum(-1)
            flat = int(np.argmax(tot))
            i, j = divmod(flat, n1)
            v = int(tot[i, j])
            if best is None or v > best[0]:
                best = (v, k, i0 + i, j)
    v, k, i, j = best
    s = {ab: (-1 if ab == k else 1) for ab in PLACEMENTS}
    Bf = []
    for b, ib in ((0, i), (1, j)):
        f = np.ones(J[(0, b)].shape[1], dtype=np.int64)
        for gi, g in enumerate(groups[b]):
            f[g] = int(S[b][ib, gi])
        Bf.append(f)
    Af = []
    for a in (0, 1):
        T = sum(s[(a, b)] * c[(a, b)] * (J[(a, b)].astype(dt) @ Bf[b].astype(dt)) for b in (0, 1))
        Af.append(np.where(np.asarray(T, dtype=object) >= 0, 1, -1).astype(np.int64))
    return v, k, Af, Bf


def chsh_functions(J):
    """Score over every +-1 function of each observer's record (one function per setting), exact.  Positively
    proportional generators of the enumerated side are merged (the value is convex in them, so the largest value has
    equal signs on them); the side with fewer merged generators is enumerated and the other answers best."""
    N, L, c = _scale(J)
    colg = [_merge(np.vstack([J[(0, b)], J[(1, b)]])) for b in (0, 1)]
    rowg = [_merge(np.vstack([J[(a, 0)].T, J[(a, 1)].T])) for a in (0, 1)]
    if sum(map(len, colg)) <= sum(map(len, rowg)):
        v, k, A, B = _enum_cols(J, c, L, colg)
        side = 'B'
    else:
        JT = {(b, a): J[(a, b)].T for (a, b) in PLACEMENTS}
        cT = {(b, a): c[(a, b)] for (a, b) in PLACEMENTS}
        v, kT, B, A = _enum_cols(JT, cT, L, rowg)
        k = (kT[1], kT[0])
        side = 'A'
    val = Fraction(v, L)
    chk, E = exact_value(J, A, B, k)
    assert chk == val, (chk, val)
    return val, dict(enumerated=side, merged=[len(g) for g in (colg if side == 'B' else rowg)], placement=list(k),
                     E={f'{a}{b}': str(e) for (a, b), e in E.items()},
                     A=[[int(x) for x in f] for f in A], B=[[int(x) for x in f] for f in B])


def chsh_functions_brute(J, limit=22):
    """The same score with no merging: every pair of Alice's functions on the record values that occur, Bob's best
    response by the sum of absolute values, over the four placements of the minus sign.  None when too large."""
    N, L, c = _scale(J)
    dt = _dtype(L)
    occ = [np.nonzero(J[(a, 0)].sum(1) + J[(a, 1)].sum(1))[0] for a in (0, 1)]
    n0, n1 = len(occ[0]), len(occ[1])
    if n0 + n1 > limit:
        return None
    sub = {(a, b): J[(a, b)][occ[a], :].astype(dt) for (a, b) in PLACEMENTS}
    best = 0
    total = 1 << (n0 + n1)
    CH = 1 << 15
    for st in range(0, total, CH):
        idx = np.arange(st, min(total, st + CH), dtype=np.int64)[:, None]
        sg = (1 - 2 * ((idx >> np.arange(n0 + n1, dtype=np.int64)[None, :]) & 1)).astype(dt)
        A0, A1 = sg[:, :n0], sg[:, n0:]
        for k in PLACEMENTS:
            s = {ab: (-1 if ab == k else 1) for ab in PLACEMENTS}
            tot = 0
            for b in (0, 1):
                Lb = s[(0, b)] * c[(0, b)] * (A0 @ sub[(0, b)]) + s[(1, b)] * c[(1, b)] * (A1 @ sub[(1, b)])
                tot = tot + np.abs(Lb).sum(1)
            best = max(best, int(np.max(tot)))
    return Fraction(best, L)


def chsh_parities(J, kA, kB, include_empty=False):
    """Score over parities of the record's values (non-empty sets, as the recorded scorer; with include_empty the
    constant outcome too), one parity per setting and observer, exact."""
    N, L, c = _scale(J)
    dt = _dtype(L)

    def H(k):
        ms = list(range(0 if include_empty else 1, 1 << k))
        return np.array([[1 - 2 * (bin(m & r).count('1') & 1) for r in range(1 << k)] for m in ms], dtype=np.int64), ms

    HA, mA = H(kA)
    HB, mB = H(kB)
    D = {ab: (c[ab] * (HA @ J[ab] @ HB.T).astype(dt)) for ab in PLACEMENTS}
    best = None
    for k in PLACEMENTS:
        s = {ab: (-1 if ab == k else 1) for ab in PLACEMENTS}
        T = (s[(0, 0)] * D[(0, 0)][:, None, :, None] + s[(0, 1)] * D[(0, 1)][:, None, None, :]
             + s[(1, 0)] * D[(1, 0)][None, :, :, None] + s[(1, 1)] * D[(1, 1)][None, :, None, :])
        T = np.abs(T)
        flat = int(np.argmax(T))
        v = int(T.flat[flat])
        if best is None or v > best[0]:
            best = (v, k, np.unravel_index(flat, T.shape))
    v, k, (i0, i1, j0, j1) = best
    return Fraction(v, L), dict(placement=list(k), masks_A=[mA[i0], mA[i1]], masks_B=[mB[j0], mB[j1]])


def old_part(J, fA, fB):
    """Sum a joint table over the last fA bits of Alice's record and the last fB of Bob's (the fresh values)."""
    out = {}
    for ab, M in J.items():
        RA, RB = M.shape
        out[ab] = M.reshape(RA >> fA, 1 << fA, RB >> fB, 1 << fB).sum(axis=(1, 3))
    return out


def evaluate_test(J, kA, kB, fA=1, fB=1, brute=True):
    """J[(a, b)], a, b in {0, 1}: integer weights of the complete records.  Hidden, and the three scores."""
    res = dict(words={f'{a}{b}': int(J[(a, b)].sum()) for (a, b) in PLACEMENTS})
    if any(v == 0 for v in res['words'].values()):
        res['status'] = 'no allowed word in some stage-1 structure'
        return res
    res['status'] = 'ok'
    res['hidden'] = hidden_info(J, (0, 1), (0, 1))
    s1, d1 = chsh_functions(J)
    res['score_i'] = str(s1)
    res['score_i_detail'] = d1
    if brute:
        b1 = chsh_functions_brute(J)
        res['score_i_brute'] = frac(b1)
        if b1 is not None:
            assert b1 == s1, ('score (i): merged and unmerged enumeration differ', b1, s1)
    s2, d2 = chsh_parities(J, kA, kB)
    res['score_ii'] = str(s2)
    res['score_ii_detail'] = d2
    s2e, _ = chsh_parities(J, kA, kB, include_empty=True)
    res['score_ii_with_constant'] = str(s2e)
    Jo = old_part(J, fA, fB)
    s3, d3 = chsh_functions(Jo)
    res['score_iii'] = str(s3)
    res['score_iii_detail'] = d3
    if brute:
        b3 = chsh_functions_brute(Jo)
        res['score_iii_brute'] = frac(b3)
        if b3 is not None:
            assert b3 == s3
    res['hidden_excess'] = bool(res['hidden']['both'] and s1 > 2)
    res['hidden_excess_ii'] = bool(res['hidden']['both'] and s2 > 2)
    res['hidden_excess_iii'] = bool(res['hidden']['both'] and s3 > 2)
    return res


# ======================================================================================================================
# Stage-1 structures.
# ======================================================================================================================
def build_stage1(knots, plan, roleA='x1', roleB='y1'):
    """Old knots plus each birth of the planned round as a not-all-equal knot over its inputs and fresh distinctions.
    Fresh names: zA (, zA2, ...) for the birth taking x1, zB for the one taking y1, n<i>_<j> for any other."""
    names = [x for x in OLD_NAMES if any(x in mem for _, mem in knots)]
    new, fresh_names = [], {}
    for i, (row, f) in enumerate(zip(plan['inputs'], plan['fresh'], strict=True)):
        ins = [ID_NAME[d] for d in row]
        if ins[0] == roleA and len(plan['parents'][i]) == 1:
            base = 'zA'
        elif ins[0] == roleB and len(plan['parents'][i]) == 1:
            base = 'zB'
        else:
            base = f'n{i}_'
        fr = [base if (j == 0 and base in ('zA', 'zB')) else f'{base}{j + 1}' for j in range(f)]
        fresh_names[i] = fr
        new.append(('nae', tuple(ins + fr)))
        names += fr
    return names, list(knots) + new, fresh_names


def choice_label(plan, i):
    return ID_NAME[plan['inputs'][i][-1]]


# ======================================================================================================================
# Row G (1): the engine against the recorded driver on the 280 funded sparse draws.
# ======================================================================================================================
def part_g_draws():
    t0 = time.time()
    res = Counter()
    bad = []
    per_arm = Counter()
    for dr in Q.lib.p3_draws():
        st = [tuple(s) for s in dr['stars']]
        h = Q.lib.grow(st, 'nae', Q.HORIZON, Q.CAP, time_limit=None)
        if h['outcome'] == 'stall' or not h['births']:
            continue
        res['funded'] += 1
        per_arm[dr['arm']] += 1
        g = Q.run_ab(st, 'nae', 'O', reread=False, bound_next=False)
        ok = [tuple(s) for s in h['stars']] == g.stars and h['n_at'] == g.n_at and h['outcome'] == g.outcome
        res['engine_equals_recorded'] += ok
        res['rounds_compared'] += len(g.rounds)
        if not ok:
            bad.append(dict(arm=dr['arm'], draw=dr['draw'], engine=[g.n_at, g.outcome], recorded=[h['n_at'], h['outcome']]))
        # beside: round 1 by this file's planner against end_operator.step and against QGrowth
        mine = plan_round1(st, reread=False)
        turn = Q.lib.EO.step(Q.lib.EO.from_stars(st), 'nae')
        eo_ok = (mine['status'] == turn.status and
                 (mine['status'] != 'extend' or (mine['parents'] == [tuple(p) for p in turn.parents]
                                                 and mine['fresh'] == list(turn.fresh)
                                                 and mine['demand'] == list(turn.demand))))
        res['planner_off_equals_end_operator_round1'] += eo_ok
        eng = q_round1(st, reread=False)
        res['planner_off_equals_qgrowth_round1'] += same_round(mine, eng)
        for conv in ('O', 'N'):
            m = plan_round1(st, reread=True, convention=conv)
            e = q_round1(st, reread=True, convention=conv)
            res[f'planner_Q{conv}_equals_qgrowth_round1'] += same_round(m, e)
            if m['status'] == 'extend':
                res[f'reread_births_round1_{conv}'] += sum(1 for o in m['options'] if o)
        if not (eo_ok and same_round(mine, eng)):
            bad.append(dict(arm=dr['arm'], draw=dr['draw'], planner_mismatch=True))
    out = dict(part='g_draws', counts=dict(res), funded_per_arm={str(k): v for k, v in sorted(per_arm.items())},
               mismatches=bad, seconds=round(time.time() - t0, 1), inputs={k: v[1] for k, v in INPUTS.items()})
    write_json('g_draws.json', out)
    print(json.dumps(dict(counts=dict(res), mismatches=len(bad), seconds=out['seconds'])))


# ======================================================================================================================
# Main: checks (a), (b), (c), (d) and row G (2).
# ======================================================================================================================
def full_round1_table(stars):
    """Every choice of round 1 by both engines.  Returns (base plan, rows, all equal)."""
    base = plan_round1(stars)
    rows = []
    all_eq = same_round(base, q_round1(stars))
    for ch in all_choices(base) if base['status'] == 'extend' else []:
        m = plan_round1(stars, choice=ch)
        e = q_round1(stars, choice=ch)
        eq = same_round(m, e)
        all_eq &= eq
        rows.append(dict(choice={str(i): ID_NAME[d] for i, d in ch.items()}, plan=m, engine=e, equal=eq))
    return base, rows, all_eq


def plan_json(p):
    if p['status'] != 'extend':
        return dict(status=p['status'], shortages=p.get('shortages'), groups=p.get('groups'))
    return dict(status='extend', parents=[list(x) for x in p['parents']],
                inputs=[[ID_NAME[d] for d in row] for row in p['inputs']],
                options=[None if o is None else [ID_NAME[d] for d in o] for o in p['options']],
                demand=p['demand'], fresh=p['fresh'], groups=p['groups'],
                opens={str(k): v for k, v in p['opens'].items()})


def part_main():
    t0 = time.time()
    stars = [tuple(NAME_ID[x] for x in mem) for _, mem in KNOTS]
    out = dict(part='main', inputs={k: v[1] for k, v in INPUTS.items()}, names=OLD_NAMES,
               knots=[f'{law}({",".join(mem)})' for law, mem in KNOTS])

    # ---------------- (a) round 1 ----------------
    base, rows, all_eq = full_round1_table(stars)
    assert base['status'] == 'extend'
    births = [dict(index=i, parents=list(p), parent_knots=[f'{KNOTS[k][0]}({",".join(KNOTS[k][1])})' for k in p],
                   loose_taken=ID_NAME[base['inputs'][i][0]],
                   options=None if base['options'][i] is None else [ID_NAME[d] for d in base['options'][i]])
              for i, p in enumerate(base['parents'])]
    iA = [i for i, b in enumerate(births) if b['loose_taken'] == 'x1'][0]
    iB = [i for i, b in enumerate(births) if b['loose_taken'] == 'y1'][0]
    convO = plan_round1(stars, convention='O')
    convN = plan_round1(stars, convention='N')
    out['a'] = dict(status=base['status'], n_births=len(base['parents']), births=births,
                    one_parent_births=sum(1 for p in base['parents'] if len(p) == 1),
                    live_knots={str(k): v for k, v in base['opens'].items()}, groups=base['groups'],
                    choices=[dict(choice=r['choice'], inputs=plan_json(r['plan'])['inputs'], fresh=r['plan']['fresh'],
                                  demand=r['plan']['demand'], engines_equal=r['equal']) for r in rows],
                    engines_equal_every_choice=bool(all_eq),
                    convention_O_takes=[choice_label(convO, i) for i in (iA, iB)],
                    convention_N_takes=[choice_label(convN, i) for i in (iA, iB)])
    assert tuple(births[iA]['options']) == OPTS_A and tuple(births[iB]['options']) == OPTS_B, 'options differ from the note'

    # ---------------- the nine stage-1 structures, word by word ----------------
    old_W, old_pos = allowed_words(OLD_NAMES, KNOTS)
    structs, s1info = {}, {}
    for a in OPTS_A:
        for b in OPTS_B:
            ch = {iA: NAME_ID[a], iB: NAME_ID[b]}
            p = plan_round1(stars, choice=ch)
            assert same_round(p, q_round1(stars, choice=ch))
            names, knots1, fr = build_stage1(KNOTS, p)
            assert names[:16] == OLD_NAMES and names[16:] == ['zA', 'zB'], names
            W, pos = allowed_words(names, knots1)
            # every old word extends; no other word appears
            oldp = W & ((1 << 16) - 1)
            u, cnt = np.unique(oldp, return_counts=True)
            assert np.array_equal(u, np.sort(old_W)), 'the allowed old words changed'
            structs[(a, b)] = (W, pos)
            s1info[f'{a}|{b}'] = dict(knots=[f'{law}({",".join(m)})' for law, m in knots1[11:]], words=int(len(W)),
                                      completions=dict(Counter(int(x) for x in cnt)))
    out['old_words'] = int(len(old_W))
    out['stage1'] = s1info

    # ---------------- (b) nine pairs of option pairs ----------------
    pairsA = list(itertools.combinations(OPTS_A, 2))
    pairsB = list(itertools.combinations(OPTS_B, 2))
    evaluate = load_scorer()
    b_rows, g2 = [], []
    for pa in pairsA:
        for pb in pairsB:
            recA, recB = ['x1', pa[0], pa[1], 'zA'], ['y1', pb[0], pb[1], 'zB']
            J = {(i, j): joint(*structs[(pa[i], pb[j])], recA, recB) for (i, j) in PLACEMENTS}
            r = evaluate_test(J, 4, 4)
            r.update(pair_A=list(pa), pair_B=list(pb), record_A=recA, record_B=recB)
            b_rows.append(r)
            # row G (2): the recorded scorer on the 8x8 table of old words by (x1, o0, o1) and (y1, p0, p1)
            M = joint(old_W, old_pos, ['x1', pa[0], pa[1]], ['y1', pb[0], pb[1]])
            ev = evaluate(M)
            if ev is None:
                g2.append(dict(pair_A=list(pa), pair_B=list(pb), scorer=None, agree=False))
            else:
                best, ns, tvv, arg = ev
                agree_score = abs(best - float(Fraction(r['score_ii']))) < 1e-9
                agree_hidden = bool(ns) == r['hidden']['both']
                g2.append(dict(pair_A=list(pa), pair_B=list(pb), scorer_score=best, scorer_hidden=bool(ns),
                               scorer_largest_change=str(tvv), mine_score_ii=r['score_ii'],
                               mine_hidden=r['hidden']['both'], agree_score=bool(agree_score),
                               agree_hidden=bool(agree_hidden), agree=bool(agree_score and agree_hidden)))
            print('b', pa, pb, r['words'], r['hidden']['both'], r['score_i'], r['score_ii'], r['score_iii'], flush=True)
    out['b'] = b_rows
    out['g2'] = dict(rows=g2, all_agree=all(x['agree'] for x in g2))

    # ---------------- (c) the pair (x2, x3) against (y2, y3) ----------------
    pa, pb = ('x2', 'x3'), ('y2', 'y3')
    recA, recB = ['x1', 'x2', 'x3', 'zA'], ['y1', 'y2', 'y3', 'zB']
    c_out = {}
    # (s1, s2)
    sdist = {}
    for (i, j) in PLACEMENTS:
        W, pos = structs[(pa[i], pb[j])]
        d = dist_of(W, pos, ['s1', 's2'])
        sdist[(i, j)] = d
    c_out['s1s2'] = {f'{pa[i]}|{pb[j]}': {f'{v >> 1}{v & 1}': str(Fraction(int(sdist[(i, j)][v]), int(sdist[(i, j)].sum())))
                                         for v in range(4)} for (i, j) in PLACEMENTS}
    c_out['s1s2_same_for_alice_choice_given_bob'] = {pb[j]: same_dist(sdist[(0, j)], sdist[(1, j)]) for j in (0, 1)}
    c_out['s1s2_same_for_bob_choice_given_alice'] = {pa[i]: same_dist(sdist[(i, 0)], sdist[(i, 1)]) for i in (0, 1)}
    # every distinction held by each observer's own knots, with its fresh one
    def own_dependence(sets):
        own = {}
        for who, names, far_is_bob in sets:
            per = {}
            for o in (0, 1):
                ds = []
                for f in (0, 1):
                    ij = (o, f) if far_is_bob else (f, o)
                    W, pos = structs[(pa[ij[0]], pb[ij[1]])]
                    ds.append(dist_of(W, pos, names))
                own_choice = pa[o] if far_is_bob else pb[o]
                per[own_choice] = dict(same=same_dist(ds[0], ds[1]), change=str(tv(ds[0], ds[1])))
            own[who] = dict(names=names, per_own_choice=per,
                            depends_on_far_choice=not all(v['same'] for v in per.values()))
        return own
    c_out['own_distinctions'] = own_dependence((('A', OWN_A, True), ('B', OWN_B, False)))
    # beside, added after the first run (deviations B4): the same without the two shared distinctions s1 and s2
    c_out['own_without_s1_s2'] = own_dependence((('A', [x for x in OWN_A if x not in ('s1', 's2')], True),
                                                 ('B', [x for x in OWN_B if x not in ('s1', 's2')], False)))
    # the old words' distribution held fixed at that of each one choice (deviations A11)
    fixed = {}
    refs = [(f'{pa[i]}|{pb[j]}', (i, j)) for (i, j) in PLACEMENTS] + [('old structure (beside)', None)]
    for label, ref in refs:
        if ref is None:
            nstar = {int(w): 1 for w in old_W}
        else:
            W, pos = structs[(pa[ref[0]], pb[ref[1]])]
            u, cnt = np.unique(W & ((1 << 16) - 1), return_counts=True)
            nstar = dict(zip(u.tolist(), cnt.tolist()))
        J = {}
        for (i, j) in PLACEMENTS:
            W, pos = structs[(pa[i], pb[j])]
            oldp = W & ((1 << 16) - 1)
            u, inv, cnt = np.unique(oldp, return_inverse=True, return_counts=True)
            n_here = cnt[inv]
            ns = np.array([nstar[int(w)] for w in oldp], dtype=np.int64)
            K = 4
            assert np.all((K * ns) % n_here == 0)
            wts = (K * ns) // n_here
            # each old word keeps its weight in total
            tot_by_old = np.zeros(len(u), dtype=np.int64)
            np.add.at(tot_by_old, inv, wts)
            assert np.array_equal(tot_by_old, K * np.array([nstar[int(w)] for w in u], dtype=np.int64))
            J[(i, j)] = joint(W, pos, recA, recB, weights=wts)
        r = evaluate_test(J, 4, 4)
        r['reference'] = label
        fixed[label] = r
        print('c fixed', label, r['hidden']['both'], r['score_i'], r['score_ii'], r['score_iii'], flush=True)
    c_out['fixed'] = fixed
    out['c'] = c_out

    # ---------------- (d) three options each ----------------
    recA5, recB5 = ['x1', 'x2', 'x3', 'c', 'zA'], ['y1', 'y2', 'y3', 't', 'zB']
    J9 = {(a, b): joint(*structs[(a, b)], recA5, recB5) for a in OPTS_A for b in OPTS_B}
    hid = hidden_info(J9, OPTS_A, OPTS_B)
    per_choice = {}
    for a in OPTS_A:
        for b in OPTS_B:
            ra = all(same_dist(J9[(a, b)].sum(1), J9[(a, f)].sum(1)) for f in OPTS_B)
            rb = all(same_dist(J9[(a, b)].sum(0), J9[(f, b)].sum(0)) for f in OPTS_A)
            per_choice[f'{a}|{b}'] = dict(alice_same_for_every_far_choice=ra, bob_same_for_every_far_choice=rb)
    subs = []
    for pa_ in pairsA:
        for pb_ in pairsB:
            J = {(i, j): J9[(pa_[i], pb_[j])] for (i, j) in PLACEMENTS}
            r = evaluate_test(J, 5, 5)
            r.update(pair_A=list(pa_), pair_B=list(pb_))
            subs.append(r)
            print('d', pa_, pb_, r['hidden']['both'], r['score_i'], r['score_ii'], r['score_iii'], flush=True)
    out['d'] = dict(record_A=recA5, record_B=recB5, words={f'{a}|{b}': int(J9[(a, b)].sum()) for a in OPTS_A for b in OPTS_B},
                    hidden=hid, per_choice=per_choice, all_nine_hidden=all(v['alice_same_for_every_far_choice'] and
                                                                         v['bob_same_for_every_far_choice']
                                                                         for v in per_choice.values()),
                    subtests=subs, largest_score_i=str(max(Fraction(s['score_i']) for s in subs)),
                    largest_score_i_hidden_subtests=str(max((Fraction(s['score_i']) for s in subs
                                                             if s['hidden']['both']), default=Fraction(0))))
    out['seconds'] = round(time.time() - t0, 1)
    write_json('main.json', out)
    print('main done', out['seconds'])


# ======================================================================================================================
# (e) knots left out.
# ======================================================================================================================
def analyse_substructure(removed):
    keep = [k for k in range(len(KNOTS)) if k not in removed]
    knots = [KNOTS[k] for k in keep]
    stars = [tuple(NAME_ID[x] for x in mem) for _, mem in knots]
    row = dict(removed=list(removed), removed_knots=[f'{KNOTS[k][0]}({",".join(KNOTS[k][1])})' for k in removed])
    present = {x for _, mem in knots for x in mem}
    if 'x1' not in present or 'y1' not in present:
        row.update(status='x1 or y1 held by no knot', strict=False, loose=False, two_one_parent=False)
        return row, None
    base, rows, all_eq = full_round1_table(stars)
    row['engines_equal_every_choice'] = bool(all_eq)
    row['round1'] = plan_json(base)
    if base['status'] == 'extend':
        row['round1']['parents_original'] = [[keep[k] for k in p] for p in base['parents']]
    row['status'] = base['status']
    if base['status'] != 'extend':
        row.update(strict=False, loose=False, two_one_parent=False)
        return row, None
    on = {}
    for i, (p, ins) in enumerate(zip(base['parents'], base['inputs'], strict=True)):
        if len(p) == 1 and ID_NAME[ins[0]] in ('x1', 'y1'):
            on[ID_NAME[ins[0]]] = i
    ok_two = ('x1' in on and 'y1' in on and all(base['options'][on[x]] and len(base['options'][on[x]]) >= 2
                                                   for x in ('x1', 'y1')))
    row['births'] = len(base['parents'])
    row['options_x1'] = None if 'x1' not in on or not base['options'][on['x1']] else [ID_NAME[d] for d in base['options'][on['x1']]]
    row['options_y1'] = None if 'y1' not in on or not base['options'][on['y1']] else [ID_NAME[d] for d in base['options'][on['y1']]]
    row['strict'] = bool(ok_two and len(base['parents']) == 2)
    row['loose'] = bool(ok_two)
    # beside (added after the first run, deviations B): exactly two one-parent births, on x1 and y1, joint births allowed
    row['two_one_parent'] = bool(ok_two and sum(1 for p in base['parents'] if len(p) == 1) == 2)
    return row, (keep, knots, stars, base, on) if ok_two else None


def run_b_on(knots, stars, base, on):
    """(b) on a structure meeting the conditions of (e): every pair of option pairs, every choice of any other
    re-reading birth (held the same across the four stage-1 structures of a test)."""
    iA, iB = on['x1'], on['y1']
    optsA = [ID_NAME[d] for d in base['options'][iA]]
    optsB = [ID_NAME[d] for d in base['options'][iB]]
    others = [i for i, o in enumerate(base['options']) if o and i not in (iA, iB)]
    other_choices = [dict(zip(others, ds)) for ds in itertools.product(*[base['options'][i] for i in others])]
    res = []
    cache = {}
    summed = Counter()
    for oc in other_choices:
        for pa in itertools.combinations(optsA, 2):
            for pb in itertools.combinations(optsB, 2):
                J, fresh_counts, s1 = {}, {}, {}
                fA = fB = None
                for (i, j) in PLACEMENTS:
                    ch = dict(oc)
                    ch[iA], ch[iB] = NAME_ID[pa[i]], NAME_ID[pb[j]]
                    key = tuple(sorted(ch.items()))
                    if key not in cache:
                        p = plan_round1(stars, choice=ch)
                        assert same_round(p, q_round1(stars, choice=ch))
                        names, knots1, fr = build_stage1(knots, p)
                        cache[key] = (names, knots1, fr, p['fresh'], len(names))
                    names, knots1, fr, fc, nn = cache[key]
                    recA = ['x1', pa[0], pa[1]] + fr[iA]
                    recB = ['y1', pb[0], pb[1]] + fr[iB]
                    assert fA in (None, len(fr[iA])) and fB in (None, len(fr[iB]))
                    fA, fB = len(fr[iA]), len(fr[iB])
                    J[(i, j)], how = joint_summing_others(names, knots1, fr, len(knots), (iA, iB), recA, recB)
                    summed[how] += 1
                    fresh_counts[f'{i}{j}'] = fc
                    s1[f'{i}{j}'] = nn
                r = evaluate_test(J, 3 + fA, 3 + fB, fA, fB)
                r.update(pair_A=list(pa), pair_B=list(pb), other_choice={str(k): ID_NAME[v] for k, v in oc.items()},
                         fresh=fresh_counts, distinctions=s1)
                res.append(r)
    return res, dict(summed)


def joint_summing_others(names, knots1, fr, n_old, keep_births, recA, recB):
    """The joint record table of a stage-1 structure.  With no birth other than those on x1 and y1 every word is
    enumerated.  Otherwise (loose reading of (e) only) the fresh distinctions of the other births, each held by its
    newborn alone, are summed out exactly: a not-all-equal newborn whose other members are all equal has 2^f - 1
    completions of its f fresh distinctions, else 2^f.  Where the structure has at most 22 distinctions the full
    enumeration is also made and must agree (asserted)."""
    others = [i for i in fr if i not in keep_births]
    if not others:
        W, pos = allowed_words(names, knots1)
        return joint(W, pos, recA, recB), 'enumerated'
    gone = {x for i in others for x in fr[i]}
    red_names = [x for x in names if x not in gone]
    newborns = knots1[n_old:]
    births = sorted(fr)
    keep_knots = list(knots1[:n_old])
    factors = []
    for i, kn in zip(births, newborns, strict=True):
        if i in others:
            law, mem = kn
            ins = [x for x in mem if x not in gone]
            f = len(mem) - len(ins)
            assert law == 'nae' and f == len(fr[i]) and not any(x in m for _, m in knots1 if m != mem for x in fr[i])
            factors.append((ins, f))
        else:
            keep_knots.append(kn)
    W, pos = allowed_words(red_names, keep_knots)
    wts = np.ones(len(W), dtype=np.int64)
    for ins, f in factors:
        vals = [(W >> pos[x]) & 1 for x in ins]
        alleq = np.ones(len(W), dtype=bool)
        for v in vals[1:]:
            alleq &= (v == vals[0])
        wts *= (1 << f) - alleq.astype(np.int64)
    J = joint(W, pos, recA, recB, weights=wts)
    if len(names) <= 22:
        Wf, pf = allowed_words(names, knots1)
        assert np.array_equal(J, joint(Wf, pf, recA, recB)), 'summing out differs from full enumeration'
        return J, 'summed out, checked against full enumeration'
    return J, 'summed out'


def part_e():
    t0 = time.time()
    rows = []
    subsets = [(k,) for k in range(11)] + list(itertools.combinations(range(11), 2))
    for rem in subsets:
        row, ctx = analyse_substructure(rem)
        if ctx is not None:
            keep, knots, stars, base, on = ctx
            tests, how = run_b_on(knots, stars, base, on)
            row['b'] = tests
            row['tables_made'] = how
            row['hidden_excess'] = any(t.get('hidden_excess') for t in tests)
            row['largest_hidden_score_i'] = str(max((Fraction(t['score_i']) for t in tests
                                                     if t['status'] == 'ok' and t['hidden']['both']), default=Fraction(0)))
        rows.append(row)
        print('e', rem, row['status'], row.get('births'), row['strict'], row['loose'], row.get('hidden_excess'),
              row.get('largest_hidden_score_i'), flush=True)
    out = dict(part='e', rows=rows, n=len(rows),
               strict_met=[r['removed'] for r in rows if r['strict']],
               loose_met=[r['removed'] for r in rows if r['loose']],
               strict_hidden_excess=[r['removed'] for r in rows if r['strict'] and r.get('hidden_excess')],
               loose_hidden_excess=[r['removed'] for r in rows if r['loose'] and r.get('hidden_excess')],
               two_one_parent_met=[r['removed'] for r in rows if r['two_one_parent']],
               two_one_parent_hidden_excess=[r['removed'] for r in rows if r['two_one_parent'] and r.get('hidden_excess')],
               engines_equal_everywhere=all(r.get('engines_equal_every_choice', True) for r in rows),
               seconds=round(time.time() - t0, 1), inputs={k: v[1] for k, v in INPUTS.items()})
    write_json('e.json', out)
    print('e done', out['seconds'], 'strict', out['strict_met'], 'loose', out['loose_met'])


# ======================================================================================================================
# (f) every even/odd assignment of the nine parity knots.
# ======================================================================================================================
def part_f(lo, hi):
    t0 = time.time()
    stars = [tuple(NAME_ID[x] for x in mem) for _, mem in KNOTS]
    base = plan_round1(stars)
    iA = [i for i, ins in enumerate(base['inputs']) if ID_NAME[ins[0]] == 'x1'][0]
    iB = [i for i, ins in enumerate(base['inputs']) if ID_NAME[ins[0]] == 'y1'][0]
    pa, pb = ('x2', 'x3'), ('y2', 'y3')
    recA, recB = ['x1', 'x2', 'x3', 'zA'], ['y1', 'y2', 'y3', 'zB']
    newborn = {}
    for (i, j) in PLACEMENTS:
        ch = {iA: NAME_ID[pa[i]], iB: NAME_ID[pb[j]]}
        p = plan_round1(stars, choice=ch)
        assert same_round(p, q_round1(stars, choice=ch))
        newborn[(i, j)] = p
    original = sum(1 << j for j, k in enumerate(PARITY_KNOTS) if KNOTS[k][0] == 'odd')
    rows = []
    for asg in range(lo, hi):
        knots = list(KNOTS)
        for j, k in enumerate(PARITY_KNOTS):
            knots[k] = ('odd' if (asg >> j) & 1 else 'even', KNOTS[k][1])
        J = {}
        for (i, j) in PLACEMENTS:
            names, knots1, fr = build_stage1(knots, newborn[(i, j)])
            W, pos = allowed_words(names, knots1)
            J[(i, j)] = joint(W, pos, recA, recB)
        r = evaluate_test(J, 4, 4)
        slim = dict(assignment=asg, laws=[knots[k][0] for k in PARITY_KNOTS], original=(asg == original),
                    words=r['words'], status=r['status'])
        if r['status'] == 'ok':
            slim.update(hidden_A=r['hidden']['A']['hidden'], hidden_B=r['hidden']['B']['hidden'],
                        hidden=r['hidden']['both'], score_i=r['score_i'], score_ii=r['score_ii'],
                        score_ii_with_constant=r['score_ii_with_constant'], score_iii=r['score_iii'],
                        hidden_excess=r['hidden_excess'], hidden_excess_ii=r['hidden_excess_ii'],
                        hidden_excess_iii=r['hidden_excess_iii'],
                        largest_change_A=r['hidden']['A']['largest_change'], largest_change_B=r['hidden']['B']['largest_change'])
        rows.append(slim)
    out = dict(part='f', lo=lo, hi=hi, parity_knots=[f'{KNOTS[k][0]}({",".join(KNOTS[k][1])})' for k in PARITY_KNOTS],
               original_assignment=original, rows=rows, seconds=round(time.time() - t0, 1),
               inputs={k: v[1] for k, v in INPUTS.items()})
    write_json(f'f_{lo:03d}-{hi:03d}.json', out)
    print('f done', lo, hi, out['seconds'], 'hidden excess', sum(1 for r in rows if r.get('hidden_excess')))


# ======================================================================================================================
# Self-test of the scoring code on objects that are not this study's structure.
# ======================================================================================================================
def _naive_functions(J):
    """Every function on both sides (records of at most 2 bits), no best response: the definition itself."""
    N, L, c = _scale(J)
    RA, RB = J[(0, 0)].shape
    SA, SB = _signs(RA), _signs(RB)
    best = 0
    for k in PLACEMENTS:
        s = {ab: (-1 if ab == k else 1) for ab in PLACEMENTS}
        for a0 in SA:
            for a1 in SA:
                A = (a0, a1)
                # value for every Bob pair at once
                V = {ab: s[ab] * c[ab] * (SB @ (J[ab].T @ A[ab[0]])) for ab in PLACEMENTS}
                tot = V[(0, 0)][:, None] + V[(0, 1)][None, :] + V[(1, 0)][:, None] + V[(1, 1)][None, :]
                best = max(best, int(np.abs(tot).max()))
    return Fraction(best, L)


def _naive_parities(J, kA, kB, include_empty):
    N, L, c = _scale(J)
    ms = lambda k: range(0 if include_empty else 1, 1 << k)
    chi = lambda m, r: 1 - 2 * (bin(m & r).count('1') & 1)
    E = {}
    for ab in PLACEMENTS:
        for mA in ms(kA):
            for mB in ms(kB):
                E[(ab, mA, mB)] = Fraction(sum(int(J[ab][r, q]) * chi(mA, r) * chi(mB, q) for r in range(1 << kA)
                                               for q in range(1 << kB)), N[ab])
    best = Fraction(0)
    for k in PLACEMENTS:
        for a0 in ms(kA):
            for a1 in ms(kA):
                for b0 in ms(kB):
                    for b1 in ms(kB):
                        m = {(0, 0): (a0, b0), (0, 1): (a0, b1), (1, 0): (a1, b0), (1, 1): (a1, b1)}
                        v = sum(E[(ab, *m[ab])] for ab in PLACEMENTS) - 2 * E[(k, *m[k])]
                        best = max(best, abs(v))
    return best


def part_selftest():
    t0 = time.time()
    rng = np.random.default_rng(2026112399)
    out = Counter()
    for trial in range(150):
        k = int(rng.integers(1, 3))
        J = {ab: rng.integers(0, 4, size=(1 << k, 1 << k)).astype(np.int64) for ab in PLACEMENTS}
        for ab in PLACEMENTS:
            J[ab][0, 0] += 1
        s, _ = chsh_functions(J)
        assert s == chsh_functions_brute(J) == _naive_functions(J), trial
        for inc in (False, True):
            assert chsh_parities(J, k, k, inc)[0] == _naive_parities(J, k, k, inc), trial
        out['random_tables'] += 1
    for trial in range(40):     # larger tables: merged against unmerged only
        J = {ab: (rng.integers(0, 3, size=(8, 8)) * (rng.random((8, 8)) < 0.5)).astype(np.int64) for ab in PLACEMENTS}
        for ab in PLACEMENTS:
            J[ab][0, 0] += 1
        assert chsh_functions(J)[0] == chsh_functions_brute(J), trial
        out['random_tables_8'] += 1
    # a non-local box: records of one bit, r_A xor r_B = a b
    J = {(a, b): np.array([[int((x ^ y) == (a & b)) for y in (0, 1)] for x in (0, 1)], dtype=np.int64)
         for (a, b) in PLACEMENTS}
    assert chsh_functions(J)[0] == 4 and chsh_parities(J, 1, 1)[0] == 4
    out['box'] = 1
    # the recorded scorer's four-type preparation (its section 1), rebuilt as four finished-structure tables
    evaluate = load_scorer()
    M = np.zeros((8, 8), dtype=np.int64)
    for x1, x2, x3, y1, y2, y3 in itertools.product((0, 1), repeat=6):
        if x2 != x3 and y2 != y3 and (x1 ^ y1) == ((x1 ^ x3) & (y1 ^ y2)):
            M[x1 * 4 + x2 * 2 + x3, y1 * 4 + y2 * 2 + y3] += 1
    J = {}
    for (a, b) in PLACEMENTS:
        T = np.zeros((16, 16), dtype=np.int64)
        for xa in range(8):
            for yb in range(8):
                for za in (0, 1):
                    for zb in (0, 1):
                        xs, ys = ((xa >> 2) & 1, (xa >> 1) & 1, xa & 1), ((yb >> 2) & 1, (yb >> 1) & 1, yb & 1)
                        if not (xs[0] == xs[1 + a] == za) and not (ys[0] == ys[1 + b] == zb):
                            T[xa * 2 + za, yb * 2 + zb] += M[xa, yb]
        J[(a, b)] = T
    best, ns, _, _ = evaluate(M)
    mine = chsh_parities(J, 4, 4)[0]
    assert abs(best - float(mine)) < 1e-9 and bool(ns) == hidden_info(J, (0, 1), (0, 1))['both']
    out['scorer_example_score_ii'] = str(mine)
    out['scorer_example_score_i'] = str(chsh_functions(J)[0])
    out['seconds'] = round(time.time() - t0, 1)
    write_json('selftest.json', dict(out))
    print(json.dumps(dict(out)))


def write_json(name, obj):
    ART.mkdir(parents=True, exist_ok=True)
    (ART / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', required=True, choices=('selftest', 'g_draws', 'main', 'e', 'f'))
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=512)
    a = ap.parse_args()
    if a.part == 'selftest':
        part_selftest()
    elif a.part == 'g_draws':
        part_g_draws()
    elif a.part == 'main':
        part_main()
    elif a.part == 'e':
        part_e()
    else:
        part_f(a.lo, a.hi)


if __name__ == '__main__':
    main()
