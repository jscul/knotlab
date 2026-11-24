"""Shared code for REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001 (can ordinary growth with both laws reach the structures
with a hidden excess?).

Frozen definitions: research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/preregistration.md.  Nothing here changes a
definition; readings are listed in deviations.md of this folder.

Recorded code reused (read-only; imported or copied, source named at each use):
  * the ordinary growth engine `end_operator` (ORDINARY-DYNAMICS-20261120-001A), imported;
  * the growth wrapper `grow` and the sparse draws `p3_draws` (REVIEW-LEADS-20261123-001A lib.py): `p3_draws` imported,
    `grow` copied below with two changes named there;
  * the scorer `evaluate(M)` of docs/prompts/missed_leads_checks/finished_weighting_chsh.py, executed up to its section 1
    (as THIRD-HOLDER-20261123-001B common.load_starter does);
  * the batched exact hiding test, float score and exact (Fraction) best score of THIRD-HOLDER-20261123-001B common.py
    (themselves copied from REVIEW-LEADS-20261123-001C), copied below (marked COPIED).
"""
import itertools
import json
import os
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from math import gcd
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
ART = ROOT / 'artifacts' / TICKET / HERE.name
ART.mkdir(parents=True, exist_ok=True)
TH_ART = ROOT / 'artifacts/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest'
TH_EXP = ROOT / 'experiments/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest'
ORDINARY = ROOT / 'experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'
RL_A = ROOT / 'experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test'
STARTER = ROOT / 'docs/prompts/missed_leads_checks/finished_weighting_chsh.py'

sys.path.insert(0, str(ORDINARY))
import end_operator as EO  # noqa: E402  (recorded ordinary growth engine)

ROUNDS = 3            # "for 3 rounds"
DMAX = 20             # "or until a stage passes 20 distinctions"
LAW_CAP = 4096        # "at most 4,096 per history"
LAW_SEED = 2026112340  # "4,096 drawn by seed 2026112340"
T2_DMAX = 16          # T2: stages of at most 16 distinctions
OBS = ('x1', 'x2', 'x3', 'y1', 'y2', 'y3')


def load_starter():
    """Exec only the definitions of the starter (up to its section 1); gives `evaluate`."""
    src = STARTER.read_text()
    cut = src.index('# ---- 1. a four-type preparation')
    ns = {'__name__': 'starter'}
    exec(compile(src[:cut], str(STARTER), 'exec'), ns)
    return ns


# ======================================================================================================================
# Targets
# ======================================================================================================================
def parse_knots(lst):
    out = []
    for s in lst:
        law, rest = s.split('(')
        out.append((law, tuple(rest.rstrip(')').split(','))))
    return out


def fmt_knot(law, mem):
    return f'{law}({",".join(mem)})'


def load_targets():
    """Every structure of THIRD-HOLDER-20261123-001B's list of structures with a hidden excess (structures_found.json),
    in file order, with the seven-knot structure and the pencil 9-knot structure marked.  Returns a list of dicts."""
    found = json.loads((TH_ART / 'structures_found.json').read_text())
    sys.path.insert(0, str(TH_EXP))
    import structures as th_struct  # recorded knot lists of the pencil and the 18-knot structure
    sys.path.pop(0)
    pencil = sorted(th_struct.PENCIL_A + th_struct.PENCIL_B)
    eighteen = sorted(th_struct.EIGHTEEN_A + th_struct.EIGHTEEN_B)
    # the seven-knot structure of research/THIRD-HOLDER-20261123-001B/result.md ("The seven knots"), internal names as stored
    seven = sorted([('nae', ('x1', 'x2', 's1')), ('nae', ('x1', 'x3', 's2')), ('even', ('x2', 'Ah1', 'Ah2')),
                    ('odd', ('x3', 'Ah1', 'Ah2')), ('even', ('y2', 'Bh1', 'Bh2')), ('odd', ('s1', 'Bh1', 'Bh2')),
                    ('odd', ('y1', 'y2', 'y3', 's2'))])
    out = []
    for i, f in enumerate(found):
        ks = parse_knots(f['knots_A']) + parse_knots(f['knots_B'])
        key = sorted(ks)
        tag = []
        if key == seven:
            tag.append('seven')
        if key == pencil:
            tag.append('pencil')
        if key == eighteen:
            tag.append('eighteen')
        out.append(dict(tid=i, knots=ks, side_A=len(f['knots_A']), source=f['source'], score=f['score'], M=f.get('M'),
                        tags=tag))
    return out


def holders_of(knots):
    h = defaultdict(list)
    for k, (law, mem) in enumerate(knots):
        for m in mem:
            h[m].append(k)
    return h


def connected(sub, knots):
    """Are the knots `sub` (indices into knots) one connected part (two knots meet when they share a distinction)?"""
    s = set(sub)
    h = defaultdict(list)
    for k in sub:
        for m in knots[k][1]:
            h[m].append(k)
    adj = defaultdict(set)
    for hs in h.values():
        for a, b in itertools.combinations(hs, 2):
            adj[a].add(b)
            adj[b].add(a)
    first = sub[0]
    seen = {first}
    todo = [first]
    while todo:
        v = todo.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen) == len(s)


def founder_starts(knots):
    """Every proper non-empty subset of the target's knots (bitmask over knot indices), classified: 'grown' when connected
    and holding all six observer distinctions, else 'no_observer' or 'not_connected' (an observer missing is checked
    first)."""
    n = len(knots)
    res = []
    for mask in range(1, (1 << n) - 1):
        sub = [k for k in range(n) if mask >> k & 1]
        dist = {m for k in sub for m in knots[k][1]}
        if not all(o in dist for o in OBS):
            res.append((mask, 'no_observer'))
        elif not connected(sub, knots):
            res.append((mask, 'not_connected'))
        else:
            res.append((mask, 'grown'))
    return res


# ======================================================================================================================
# Growth: the recorded operator, driven from a start given as knots with names
# ======================================================================================================================
def from_stars_ext(stars):
    """end_operator.from_stars, extended to distinctions with three or more holders (every two holders of a shared
    distinction meet).  With at most two holders per distinction it is the recorded function (checked in gates.py)."""
    holders = defaultdict(list)
    graph = [set() for _ in stars]
    for knot, support in enumerate(stars):
        for distinction in support:
            holders[distinction].append(knot)
    opens = Counter()
    for row in holders.values():
        if len(row) == 1:
            opens[row[0]] += 1
        else:
            if len(set(row)) != len(row):
                raise ValueError('a knot holds a distinction twice')
            for a, b in itertools.combinations(row, 2):
                graph[a].add(b)
                graph[b].add(a)
    todo = [0]
    seen = {0}
    for v in todo:
        unseen = graph[v] - seen
        seen.update(unseen)
        todo.extend(unseen)
    if len(seen) != len(graph):
        raise ValueError('not one connected presentation')
    return EO.End(opens, tuple(row & opens.keys() for row in graph))


def grow(stars, law_rule, rounds=ROUNDS, dmax=DMAX, placement=None):
    """Ordinary growth by the recorded `end_operator.step`, copied from REVIEW-LEADS-20261123-001A lib.grow with two
    changes: (1) the stop is the pre-registration's (after `rounds` rounds, or once a stage has more than `dmax`
    distinctions; that stage is kept), (2) `from_stars_ext` for starts with a distinction held three or more times.
    `law_rule` is 'nae' (no closing) or 'parity' (a sole birth taking every loose distinction closes).
    `placement`: None = the wrapper's rule (a birth takes the last remaining loose distinction of each parent, in the
    star's order); else a callable (round, birth index, parent, list of remaining loose) -> index to take.
    Returns dict: stars (tuples of ints, birth order), n_at (knots at each stage), D_at (distinctions at each stage),
    births (per round: list of (parents, inputs, fresh ids)), outcome, closing (round of a closing birth or None)."""
    stars = [tuple(s) for s in stars]
    counts = Counter(d for s in stars for d in s)
    loose = {k: [d for d in s if counts[d] == 1] for k, s in enumerate(stars)}
    top = max(counts) + 1
    end = from_stars_ext(stars)
    n_at = [len(stars)]
    D_at = [len(counts)]
    births, outcome, closing = [], 'rounds', None
    r = 0
    while True:
        if r >= rounds:
            outcome = 'rounds'
            break
        if D_at[-1] > dmax:
            outcome = 'distinctions'
            break
        turn = EO.step(end, law_rule)
        if turn.status in ('closed', 'stall'):
            outcome = turn.status
            break
        base = len(stars)
        record = []
        for bi, (parents, fresh) in enumerate(zip(turn.parents, turn.fresh, strict=True)):
            inputs = []
            for p in parents:
                if placement is None:
                    inputs.append(loose[p].pop())
                else:
                    j = placement(r, bi, p, loose[p])
                    inputs.append(loose[p].pop(j))
            made = tuple(range(top, top + fresh))
            top += fresh
            stars.append(tuple(inputs) + made)
            loose[len(stars) - 1] = list(made)
            record.append((tuple(parents), tuple(inputs), made))
        births.append(record)
        n_at.append(len(stars))
        D_at.append(D_at[-1] + sum(len(m) for _, _, m in record))
        r += 1
        if turn.implied:
            outcome = 'closed_by_birth'
            closing = r
            break
        nxt = turn.end
        end = EO.End({base + i: c for i, c in nxt.opens.items()},
                     tuple(tuple(base + i for i in blk) for blk in nxt.blocks))
    return dict(stars=stars, n_at=n_at, D_at=D_at, births=births, outcome=outcome, closing=closing)


def start_stars(knots, mask):
    """Founder start of a target: (stars with integer distinctions, laws, name of each integer, observer integers)."""
    sub = [k for k in range(len(knots)) if mask >> k & 1]
    names = []
    for k in sub:
        for m in knots[k][1]:
            if m not in names:
                names.append(m)
    idx = {m: i for i, m in enumerate(names)}
    stars = [tuple(idx[m] for m in knots[k][1]) for k in sub]
    laws = [knots[k][0] for k in sub]
    obs = tuple(idx[o] for o in OBS)
    return stars, laws, names, obs, sub


# ======================================================================================================================
# Law assignments of the newborns
# ======================================================================================================================
def assignments(n, key, k=2):
    """Every assignment of a law index (k = 2: 0 parity even, 1 not-all-equal; k = 3: 0 even, 1 odd, 2 not-all-equal) to n
    newborns when k^n <= LAW_CAP; else LAW_CAP distinct assignments drawn by numpy.random.default_rng([LAW_SEED, *key])
    (k = 3: [LAW_SEED, 3, *key]).  Returns (array (A, n) of int8, 'all' or 'drawn').  Column j is the j-th newborn in
    birth order, so the assignment of a stage is a prefix of the columns."""
    if n == 0:
        return np.zeros((1, 0), dtype=np.int8), 'all'
    if k ** n <= LAW_CAP:
        a = np.array(list(itertools.product(range(k), repeat=n)), dtype=np.int8)[:, ::-1].copy()
        return a, 'all'
    rng = np.random.default_rng([LAW_SEED, *key] if k == 2 else [LAW_SEED, 3, *key])
    seen = set()
    rows = []
    while len(rows) < LAW_CAP:
        row = rng.integers(0, k, size=n, dtype=np.int8)
        b = row.tobytes()
        if b not in seen:
            seen.add(b)
            rows.append(row)
    return np.array(rows, dtype=np.int8), 'drawn'


# ======================================================================================================================
# Knot tensors and contraction
# ======================================================================================================================
def law_tensor(law, k):
    """0/1 tensor of shape (2,)*k: allowed values of a knot of k places."""
    idx = np.indices((2,) * k).reshape(k, -1)
    s = idx.sum(0)
    if law == 'nae':
        ok = (s != 0) & (s != k)
    elif law == 'even':
        ok = s % 2 == 0
    elif law == 'odd':
        ok = s % 2 == 1
    else:
        raise ValueError(law)
    return ok.astype(np.int64).reshape((2,) * k)


_LT = {}


def lt(law, k):
    key = (law, k)
    if key not in _LT:
        _LT[key] = law_tensor(law, k)
    return _LT[key]


LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def contract(factors, keep, batch=None):
    """Sum over every variable not in `keep` of the product of `factors`.

    factors: list of (vars tuple, array); an array may carry a leading batch axis (then its vars are its other axes and
    the factor is listed with batched=True as (vars, array, True)).  keep: tuple of variables kept, in output order.
    batch: size of the batch axis or None.  Exact: int64 when the number of summed variables is at most 60, else Python
    integers (object arrays).  Returns array of shape ([batch,] 2,...,2)."""
    fs = []
    allv = set()
    for f in factors:
        if len(f) == 3:
            v, a, b = f
        else:
            (v, a), b = f, False
        fs.append((tuple(v), a, b))
        allv.update(v)
    allv.update(keep)
    elim = [v for v in allv if v not in set(keep)]
    use_obj = len(elim) > 60
    if use_obj:
        fs = [(v, a.astype(object), b) for v, a, b in fs]
    keepset = set(keep)
    # greedy: eliminate the variable whose merged scope is smallest
    remaining = set(elim)
    while remaining:
        best = None
        for v in remaining:
            scope = set()
            for fv, _, _ in fs:
                if v in fv:
                    scope.update(fv)
            sz = len(scope)
            if best is None or sz < best[0]:
                best = (sz, v)
        v = best[1]
        touch = [f for f in fs if v in f[0]]
        rest = [f for f in fs if v not in f[0]]
        scope = []
        for fv, _, _ in touch:
            for u in fv:
                if u not in scope:
                    scope.append(u)
        out_vars = tuple(u for u in scope if u != v)
        new = _einsum(touch, out_vars)
        fs = rest + [new]
        remaining.discard(v)
    res = _einsum(fs, tuple(keep))
    return res[1]


def _einsum(fs, out_vars):
    """Product of factors fs, keeping out_vars (and the batch axis if any factor is batched)."""
    letters = {}
    for fv, _, _ in fs:
        for u in fv:
            if u not in letters:
                letters[u] = LETTERS[len(letters)]
    for u in out_vars:
        if u not in letters:
            letters[u] = LETTERS[len(letters)]
    if len(letters) > 51:
        raise RuntimeError('too many axes in one product')
    anyb = any(b for _, _, b in fs)
    ops = []
    subs = []
    for fv, a, b in fs:
        s = ''.join(letters[u] for u in fv)
        subs.append(('Z' if b else '') + s)
        ops.append(a)
    outs = ('Z' if anyb else '') + ''.join(letters[u] for u in out_vars)
    # variables of out_vars held by no factor are free: broadcast with a ones tensor
    free = [u for u in out_vars if not any(u in fv for fv, _, _ in fs)]
    for u in free:
        subs.append(letters[u])
        ops.append(np.ones(2, dtype=ops[0].dtype if ops else np.int64))
    if not ops:
        return (tuple(out_vars), np.ones((2,) * len(out_vars), dtype=np.int64), False)
    expr = ','.join(subs) + '->' + outs
    arr = np.einsum(expr, *ops, optimize=len(ops) > 2)
    return (tuple(out_vars), arr, anyb)


# ======================================================================================================================
# Stage tables
# ======================================================================================================================
def founder_factors(stars, laws, upto):
    return [(stars[k], lt(laws[k], len(stars[k]))) for k in range(upto)]


def newborn_factor_batched(star, col, choices=('even', 'nae')):
    """A newborn's factor over its distinctions with a leading batch axis: row b is the law choices[col[b]]."""
    k = len(star)
    stack = np.stack([lt(c, k) for c in choices])        # (len(choices), 2,..,2)
    return (star, stack[col.astype(np.int64)], True)


def stage_tables(stars, laws_founders, n_founders, n_stage, newborn_laws, keep, closing_idx=None, choices=('even', 'nae')):
    """Observer tables of one stage (the first n_stage knots) for a batch of newborn law assignments.

    newborn_laws: array (B, n_stage - n_founders) of indices into `choices`.  A knot listed in closing_idx (an implied
    parity closing birth with no fresh distinction) adds no factor (its sign is the implied one; gates.py checks that the
    implied relation holds on every allowed word).  keep: the six observer distinctions.  Returns array (B, 64)
    (object dtype when large) with index x1*32 + x2*16 + x3*8 + y1*4 + y2*2 + y3."""
    B = newborn_laws.shape[0]
    fs = founder_factors(stars, laws_founders, n_founders)
    for j, k in enumerate(range(n_founders, n_stage)):
        if closing_idx is not None and k in closing_idx:
            continue
        fs.append(newborn_factor_batched(stars[k], newborn_laws[:, j], choices))
    if n_stage > n_founders:
        res = contract(fs, keep, batch=B)
        if res.ndim == len(keep):          # no batched factor survived (every newborn was a closing birth)
            res = np.broadcast_to(res, (B,) + res.shape)
    else:
        res = contract(fs, keep)
        res = np.broadcast_to(res, (B,) + res.shape)
    return np.ascontiguousarray(res).reshape(B, 64)


def brute_table(stars, laws, keep):
    """Observer table of a structure (all knots given with their laws) by enumerating every word of its distinctions."""
    names = sorted({d for s in stars for d in s})
    pos = {d: i for i, d in enumerate(names)}
    n = len(names)
    T = np.zeros(64, dtype=np.int64)
    step = 1 << min(n, 22)
    for off in range(0, 1 << n, step):
        idx = np.arange(off, off + step, dtype=np.int64)
        ok = np.ones(step, dtype=bool)
        for s, law in zip(stars, laws):
            sm = sum(((idx >> pos[d]) & 1) for d in s)
            k = len(s)
            if law == 'nae':
                ok &= (sm != 0) & (sm != k)
            elif law == 'even':
                ok &= sm % 2 == 0
            else:
                ok &= sm % 2 == 1
        key = np.zeros(step, dtype=np.int64)
        for o in keep:
            key = key * 2 + ((idx >> pos[o]) & 1) if o in pos else key * 2
        T += np.bincount(key[ok], minlength=64)
    return T


# ======================================================================================================================
# Evaluation: hiding (exact, integers), score (float screen, exact Fraction for candidates)
# ======================================================================================================================
# ---- COPIED from THIRD-HOLDER-20261123-001B common.py (itself copied from REVIEW-LEADS-20261123-001C) ----------------
REC = [(x1, x2, x3, z) for x1 in (0, 1) for x2 in (0, 1) for x3 in (0, 1) for z in (0, 1)]
SGN = np.array([[(-1) ** sum(b for b, m in zip(r, [(k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1]) if m) for r in REC]
                for k in range(1, 16)], dtype=np.int64)


def side_factor(a):
    f = np.zeros((8, 16), dtype=np.int64)
    for xa in range(8):
        x = [(xa >> 2) & 1, (xa >> 1) & 1, xa & 1]
        for z in (0, 1):
            if not (x[0] == x[1 + a] == z):
                f[xa, xa * 2 + z] = 1
    return f


F = [side_factor(0), side_factor(1)]
W = np.array([F[0].sum(1), F[1].sum(1)], dtype=np.int64)
C = [SGN @ F[a].T for a in (0, 1)]
Cf = [c.astype(np.float64) for c in C]
Wf = W.astype(np.float64)


def parallel_rows(u0, u1):
    s0 = u0.sum(-1, keepdims=True)
    s1 = u1.sum(-1, keepdims=True)
    return (u0 * s1 == u1 * s0).all(-1)


def hidden_batch(M):
    """M: (n,8,8) int64, entries below 2^24.  Hidden iff M W0 || M W1 (Alice) and M^T W0 || M^T W1 (Bob)."""
    M = np.asarray(M, dtype=np.int64)
    uA0 = M @ W[0]
    uA1 = M @ W[1]
    vB0 = np.einsum('nxy,x->ny', M, W[0])
    vB1 = np.einsum('nxy,x->ny', M, W[1])
    return parallel_rows(uA0, uA1), parallel_rows(vB0, vB1)


def E_tables(M):
    out = []
    for a in (0, 1):
        for b in (0, 1):
            num = np.einsum('kx,nxy,ly->nkl', Cf[a], M, Cf[b], optimize=True)
            den = np.einsum('x,nxy,y->n', Wf[a], M, Wf[b])
            out.append(num / den[:, None, None])
    return out


def chsh_best_from_E(E):
    E00, E01, E10, E11 = E
    n = E00.shape[0]
    best = np.zeros(n)
    for p in range(4):
        s = [1.0] * 4
        s[p] = -1.0
        u = s[0] * E00[:, :, None, :] + s[2] * E10[:, None, :, :]
        v = s[1] * E01[:, :, None, :] + s[3] * E11[:, None, :, :]
        hi = u.max(-1) + v.max(-1)
        lo = -(u.min(-1) + v.min(-1))
        best = np.maximum(best, np.maximum(hi, lo).max((1, 2)))
    return best


def score_batch(M, chunk=1500):
    M = np.asarray(M, dtype=np.float64)
    out = np.empty(M.shape[0])
    for i in range(0, M.shape[0], chunk):
        out[i:i + chunk] = chsh_best_from_E(E_tables(M[i:i + chunk]))
    return out


def exact_E(M):
    M = np.asarray(M, dtype=object)
    res = {}
    for a in (0, 1):
        for b in (0, 1):
            Ca = C[a].astype(object)
            Cb = C[b].astype(object)
            num = Ca.dot(M).dot(Cb.T)
            den = int(W[a].astype(object).dot(M).dot(W[b].astype(object)))
            res[a, b] = np.array([[Fraction(int(num[k, l]), den) for l in range(15)] for k in range(15)], dtype=object)
    return res


def exact_best(M, slack=1e-7):
    """Exact best |CHSH| over parity choices: float screen, exact evaluation of every combination within `slack` of the
    float best.  Returns Fraction."""
    Mf = np.asarray(M, dtype=np.float64)
    Mf = (Mf / Mf.sum())[None]
    E = E_tables(Mf)
    Ex = exact_E(M)
    E00, E01, E10, E11 = [e[0] for e in E]
    gbest = 0.0
    allv = []
    for p in range(4):
        s = np.ones(4)
        s[p] = -1
        V = (s[0] * E00[:, None, :, None] + s[1] * E01[:, None, None, :] + s[2] * E10[None, :, :, None]
             + s[3] * E11[None, :, None, :])
        allv.append(V)
        gbest = max(gbest, float(np.abs(V).max()))
    best = Fraction(-1)
    for p in range(4):
        s = [1] * 4
        s[p] = -1
        idx = np.argwhere(np.abs(allv[p]) >= gbest - slack)
        for kA0, kA1, kB0, kB1 in idx:
            v = (s[0] * Ex[0, 0][kA0, kB0] + s[1] * Ex[0, 1][kA0, kB1] + s[2] * Ex[1, 0][kA1, kB0]
                 + s[3] * Ex[1, 1][kA1, kB1])
            if abs(v) > best:
                best = abs(v)
    return best
# ---- end COPIED -------------------------------------------------------------------------------------------------------


def exact_hidden_obj(M):
    """Exact hiding test in Python integers for one 8x8 table (any size of entries)."""
    M = [[int(M[x][y]) for y in range(8)] for x in range(8)]
    w = [[int(W[a][x]) for x in range(8)] for a in (0, 1)]

    def par(u0, u1):
        s0, s1 = sum(u0), sum(u1)
        return all(p * s1 == q * s0 for p, q in zip(u0, u1))
    uA = [[sum(M[x][y] * w[b][y] for y in range(8)) for x in range(8)] for b in (0, 1)]
    vB = [[sum(M[x][y] * w[a][x] for x in range(8)) for y in range(8)] for a in (0, 1)]
    return par(uA[0], uA[1]), par(vB[0], vB[1])


def normalize(T):
    """Divide a table (64 entries, ints or object) by the gcd of its entries; return int64 when it fits, else object."""
    vals = [int(v) for v in np.asarray(T).reshape(-1)]
    g = 0
    for v in vals:
        g = gcd(g, v)
    if g == 0:
        return np.zeros(64, dtype=np.int64)
    vals = [v // g for v in vals]
    if max(vals) < (1 << 62):
        return np.array(vals, dtype=np.int64)
    return np.array(vals, dtype=object)


class Evaluator:
    """Cached evaluation of normalized observer tables: (hidden_A, hidden_B, float score, exact score or None).
    Exact score computed for every hidden table whose float score is at least 2 - 1e-6."""

    def __init__(self):
        self.cache = {}
        self.exact_calls = 0

    def run(self, tabs):
        """tabs: list of normalized 64-vectors.  Returns list of tuples (hA, hB, fscore, exact or None)."""
        out = [None] * len(tabs)
        todo_small, todo_big = [], []
        keys = []
        for i, t in enumerate(tabs):
            k = t.tobytes() if t.dtype != object else repr(tuple(int(v) for v in t)).encode()
            keys.append(k)
            if k in self.cache:
                out[i] = self.cache[k]
            elif t.dtype != object and int(t.max()) < (1 << 24):
                todo_small.append(i)
            else:
                todo_big.append(i)
        # dedupe inside the batch
        uniq = {}
        for i in todo_small:
            uniq.setdefault(keys[i], i)
        ids = list(uniq.values())
        if ids:
            Ms = np.stack([tabs[i] for i in ids]).reshape(-1, 8, 8)
            hA, hB = hidden_batch(Ms)
            sel = np.nonzero(hA & hB)[0]
            fs = np.full(len(ids), np.nan)
            if len(sel):
                fs[sel] = score_batch(Ms[sel] / Ms[sel].sum((1, 2), keepdims=True))
            for j, i in enumerate(ids):
                ex = None
                if hA[j] and hB[j] and fs[j] >= 2 - 1e-6:
                    ex = exact_best(Ms[j].astype(object))
                    self.exact_calls += 1
                self.cache[keys[i]] = (bool(hA[j]), bool(hB[j]), None if np.isnan(fs[j]) else float(fs[j]), ex)
        for i in todo_big:
            if keys[i] in self.cache:
                continue
            Mo = np.array([int(v) for v in tabs[i]], dtype=object).reshape(8, 8)
            hA, hB = exact_hidden_obj(Mo)
            fsc, ex = None, None
            if hA and hB:
                Mf = np.array([float(v) for v in tabs[i]]).reshape(1, 8, 8)
                fsc = float(score_batch(Mf / Mf.sum())[0])
                if fsc >= 2 - 1e-6:
                    ex = exact_best(Mo)
                    self.exact_calls += 1
            self.cache[keys[i]] = (hA, hB, fsc, ex)
        for i in range(len(tabs)):
            if out[i] is None:
                out[i] = self.cache[keys[i]]
        return out


def is_excess(ev):
    """Hidden on both sides with an exact score above 2."""
    return ev[0] and ev[1] and ev[3] is not None and ev[3] > 2


def support_key(T):
    return tuple(int(i) for i in np.nonzero(np.asarray([int(v) for v in np.asarray(T).reshape(-1)]))[0])


def proportional(T, U):
    """Exact: T and U (64 entries) proportional (same ratios) and both non-zero."""
    t = [int(v) for v in np.asarray(T).reshape(-1)]
    u = [int(v) for v in np.asarray(U).reshape(-1)]
    st, su = sum(t), sum(u)
    if st == 0 or su == 0:
        return False
    return all(a * su == b * st for a, b in zip(t, u))


def dump(path, rows, mode='w'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode) as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(',', ':'), default=str) + '\n')
