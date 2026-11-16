"""Tie chains along a sub-window ray, at every depth (DIRECT-REACH-20261115-001, the thread's own code, 2026-11-16).

For descriptions whose orbits grow (the window tree of exploratory/window_tree.py needs orbits of at most 4 addresses), a tie chain can
still be carried by a few addresses per level. Take S_k0, a few addresses at level k0, and an eventually periodic letter sequence c_k;
set S_(k+1) = {x·c_k(x) : x in S_k}, one letter for each element. The window W_k is the set of knots placed at level k whose members all lie in S_k ∪ S_k·{0,1}. W_j and W_(j+1) share only S_(j+1), and W_j, W_(j+2) share nothing, so the windows form a path, and
their union is a sub-pattern of the depth-N pattern for every N > k (knots at x in S_k with a child member exist once N > k).

A knot placed at v with x = m_i(v) in S_k has its term j's member at (m_j · m_i^(-1))(x), so the type of S_k (for each element x and
each composite g = m_j · m_i^(-1): the index of g(x) in S_k or 'outside', and g's section at x) determines W_k up to renaming, and the
type of S_(k+1) is a function of the type of S_k and the letters: g(x_i·c_i) = g(x_i)·g|_(x_i)(c_i) lies in S_(k+1) exactly when
g(x_i) = x_j is in S_k and g|_(x_i)(c_i) = c_j. The forward message (the assignments of S_k allowed by W_k0..W_(k-1)) and the tie relation between S_k0 and
S_k (pairs forced equal or unequal in W_k0..W_k) are functions of the previous ones and the type, so the whole state is eventually
periodic and "some element of S_k0 is tied to some element of S_k for every k" is a finite check.

A tie forced in a sub-pattern is forced in the whole pattern; with the whole pattern alive at every depth (an automatic state,
exploratory/automatic_life.py) both members are free by complement symmetry, so the tie is a bond of two members, and one tie class
meets level k0 and every deeper level: L_N(k0, s) = 2 for every s >= 1 and every N >= k0 + s.
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'exploratory'))
from window_types import Description  # noqa: E402


class Extended:
    """The description's automaton with inverse states s..2s-1, and the composite words m_j · m_i^(-1) of its used maps."""

    def __init__(self, D):
        sw, d0, d1 = D.aut
        s = len(sw)
        self.s = s
        self.sw = list(sw) + list(sw)
        self.d = [list(d0) + [0] * s, list(d1) + [0] * s]
        for q in range(s):
            for a in (0, 1):
                b = a ^ sw[q]                      # the inverse of q reads q's output a and returns q's input b
                self.d[a][s + q] = s + (d0[q] if b == 0 else d1[q])
        self.D = D
        inv = [tuple(s + q for q in reversed(w)) for w in D.maps]
        self.comp = {(j, i): tuple(D.maps[j]) + inv[i] for j in range(len(D.maps)) for i in range(len(D.maps))}

    def step(self, ws, b):
        c, new = b, list(ws)
        for i in range(len(ws) - 1, -1, -1):
            q = ws[i]
            new[i] = self.d[c][q]
            c ^= self.sw[q]
        return c, tuple(new)

    def image(self, word, bits):
        ws, out = tuple(word), []
        for b in bits:
            c, ws = self.step(ws, b)
            out.append(c)
        return tuple(out), ws


def initial_type(E, S):
    """For each element x of S and each composite m_j · m_i^(-1): (index of its image in S, or None; its section at x)."""
    index = {x: i for i, x in enumerate(S)}
    keys = sorted(E.comp)
    rows = []
    for x in S:
        row = []
        for key in keys:
            y, ws = E.image(E.comp[key], x)
            j = index.get(y)
            row.append((j, ws) if j is not None else (None, None))
        rows.append(tuple(row))
    return tuple(rows)


def next_type(E, T, c):
    """c: one letter per element (S_(k+1) = {x_i·c_i}); g(x_i·c_i) = g(x_i)·g|_(x_i)(c_i) is in S_(k+1) iff g(x_i) = x_j and the
    output letter is c_j."""
    rows = []
    for i, row in enumerate(T):
        new = []
        for j, ws in row:
            if j is None:
                new.append((None, None))
                continue
            out, nws = E.step(ws, c[i])
            new.append((j, nws) if out == c[j] else (None, None))
        rows.append(tuple(new))
    return tuple(rows)


def window_knots(E, T):
    """Knots placed at level k whose members all lie in S_k ∪ S_k·{0,1}, on variables 0..n-1 (S_k) and n + 2j + b (child (j, b)).
    A knot placed at v is found from x = m_i(v) in S_k for one of its terms i: v = m_i^(-1)(x), and its term j's member is
    (m_j · m_i^(-1))(x), with the term's child letter if any."""
    D = E.D
    keys = sorted(E.comp)
    col = {key: c for c, key in enumerate(keys)}
    n = len(T)
    knots = set()
    for a in range(n):
        for p in D.placements:
            terms = [divmod(t, 3) for t in p]
            for wi_i, _ in terms:
                mi = D.slot_map[wi_i]
                mem = []
                for wj, slot in terms:
                    j, _ = T[a][col[(D.slot_map[wj], mi)]]
                    if j is None:
                        break
                    mem.append(j if slot == 0 else n + 2 * j + slot - 1)
                else:
                    if len(set(mem)) == 3:
                        knots.add(tuple(sorted(mem)))
    return tuple(sorted(knots))


_SAT = {}


def window_states(n, knots):
    """Allowed assignments of the window as (x on S_k, y on the 2n children), from all 2^(3n) assignments."""
    key = (n, knots)
    if key not in _SAT:
        nv = 3 * n
        X = (np.arange(1 << nv, dtype=np.int64)[:, None] >> np.arange(nv)) & 1
        ok = np.ones(len(X), dtype=bool)
        for a, b, c in knots:
            s = X[:, a] + X[:, b] + X[:, c]
            ok &= (s != 0) & (s != 3)
        rows = np.nonzero(ok)[0]
        _SAT[key] = [(int(r) & ((1 << n) - 1), int(r) >> n) for r in rows]
    return _SAT[key]


def child_part(y, n, c):
    """Assignment of S_(k+1) = {x_j·c_j} from the children assignment y (bit 2j + b is child (j, b))."""
    z = 0
    for j in range(n):
        z |= ((y >> (2 * j + c[j])) & 1) << j
    return z


def run_chain(D, S, letters_prefix, letters_cycle, max_steps=400):
    """Returns dict(ok, steps, start, period, ...) for the chain from S (addresses of one level, as bit tuples)."""
    n = len(S)
    E = D if isinstance(D, Extended) else Extended(D)
    T = initial_type(E, S)
    m = frozenset(range(1 << n))
    rel = frozenset((i, i, 0) for i in range(n))          # (top index, current index, sign)
    seen = {}
    history = []
    L = len(letters_prefix)
    for step in range(max_steps):
        phase = step if step < L else L + (step - L) % len(letters_cycle)
        state = (T, m, rel, phase if step >= L else ('pre', step))
        if step >= L and state in seen:
            start = seen[state]
            return dict(ok=all(h['tied'] for h in history), steps=step, start=start, period=step - start,
                        tied_every_step=[h['tied'] for h in history], window_knots=[h['knots'] for h in history])
        if step >= L:
            seen[state] = step
        c = letters_prefix[step] if step < L else letters_cycle[(step - L) % len(letters_cycle)]
        knots = window_knots(E, T)
        R = set()
        for x, y in window_states(n, knots):
            if x in m:
                R.add((x, child_part(y, n, c)))
        if not R:
            return dict(ok=False, dead_at=step)
        # ties between current S_k (in the projection onto S_k) and S_(k+1)
        newrel = set()
        for (i0, j, sg) in rel:
            for j2 in range(n):
                vals = {((x >> j) ^ (z >> j2)) & 1 for x, z in R}
                if len(vals) == 1:
                    newrel.add((i0, j2, sg ^ vals.pop()))
        # within S_(k+1) ties close the relation
        Z = {z for _, z in R}
        for (i0, j, sg) in list(newrel):
            for j2 in range(n):
                vals = {((z >> j) ^ (z >> j2)) & 1 for z in Z}
                if len(vals) == 1:
                    newrel.add((i0, j2, sg ^ vals.pop()))
        history.append(dict(tied=bool(newrel), knots=len(knots)))
        T = next_type(E, T, c)
        m = frozenset(Z)
        rel = frozenset(newrel)
    return dict(ok=False, reason='no repeat within %d steps' % max_steps)


def addresses(k):
    return [tuple((y >> (k - 1 - i)) & 1 for i in range(k)) for y in range(1 << k)]


def letter_rules(n, periodic=True):
    """Constant letter vectors, then (if periodic) period-2 alternations of two constant vectors."""
    vecs = list(itertools.product((0, 1), repeat=n))
    out = [((), (v,)) for v in vecs]
    if periodic:
        out += [((), (v, w)) for v in vecs for w in vecs if v != w]
    return out


def search(key, k0s=(1, 2, 3), max_size=3):
    """First (k0, S, letters) whose chain carries a tie to every deeper level; None if none in the family."""
    E = Extended(Description(key))
    for k0 in k0s:
        level = addresses(k0)
        for size in range(1, max_size + 1):
            for S in itertools.combinations(level, size):
                for pre, cyc in letter_rules(size, periodic=size <= 3):
                    r = run_chain(E, list(S), list(pre), list(cyc))
                    if r.get('ok'):
                        return dict(k0=k0, S=[''.join(map(str, x)) for x in S], prefix=[list(v) for v in pre], cycle=[list(v) for v in cyc],
                                    start=r['start'], period=r['period'], window_knots=sorted(set(r['window_knots'])))
    return None


if __name__ == '__main__':
    from window_types import population_D
    wt = json.load(open(HERE / 'exploratory/window_tree_census.json'))['cases']
    rows = {}
    which = sys.argv[1] if len(sys.argv) > 1 else 'constant-2'
    for cid, key, prof, cls in population_D():
        if which == 'constant-2' and prof != [2, 2, 2, 2]:
            continue
        bounded = 'k3' in wt[cid]
        r = search(key, k0s=(3, 2, 1), max_size=3)
        if r is None:
            r = search(key, k0s=(3, 2), max_size=4)
        rows[cid] = dict(profile=prof, relative_class=cls, bounded_orbits=bounded, chain=r)
        print(cid[:12], prof, cls, 'bounded' if bounded else 'growing', json.dumps(r), flush=True)
    json.dump(rows, open(HERE / ('chain_ties_%s.json' % which), 'w'), indent=1)
    found = sum(1 for r in rows.values() if r['chain'])
    print('chains found', found, 'of', len(rows), '| growing orbits:',
          sum(1 for r in rows.values() if r['chain'] and not r['bounded_orbits']), 'of',
          sum(1 for r in rows.values() if not r['bounded_orbits']))


def run_anchored(E, S, letters_prefix, letters_cycle, max_steps=400):
    """The chain with the top assignment carried in the message (the anchor): m_k is a set of (assignment of S_k0, assignment of
    S_k) allowed by W_k0..W_(k-1). At each step, for each element j of S_(k+1): the anchor elements tied to it, and the anchor pairs
    (i, i') with {x_i, x_i', y_j} constrained (a pattern of the three missing). Returns the per-step lists and the period."""
    n = len(S)
    T = initial_type(E, S)
    m = frozenset((a, a) for a in range(1 << n))
    L = len(letters_prefix)
    seen, history = {}, []
    for step in range(max_steps):
        if step >= L:
            phase = (step - L) % len(letters_cycle)
            state = (T, m, phase)
            if state in seen:
                start = seen[state]
                return dict(steps=step, start=start, period=step - start, history=history)
            seen[state] = step
        c = letters_prefix[step] if step < L else letters_cycle[(step - L) % len(letters_cycle)]
        knots = window_knots(E, T)
        by_x = {}
        for x, y in window_states(n, knots):
            by_x.setdefault(x, set()).add(child_part(y, n, c))
        new = frozenset((a, z) for a, x in m for z in by_x.get(x, ()))
        if not new:
            return dict(dead_at=step, history=history)
        ties, triples = [], []
        for j in range(n):
            for i in range(n):
                vals = {((a >> i) ^ (z >> j)) & 1 for a, z in new}
                if len(vals) == 1:
                    ties.append((i, j, vals.pop()))
            for i in range(n):
                for i2 in range(i + 1, n):
                    pats = {(((a >> i) & 1), ((a >> i2) & 1), ((z >> j) & 1)) for a, z in new}
                    if len(pats) < 8:
                        triples.append((i, i2, j))
        history.append(dict(ties=ties, triples=triples, knots=len(knots)))
        T = next_type(E, T, c)
        m = new
    return dict(reason='no repeat within %d steps' % max_steps, history=history)


def free_pairs_from_machines(Ms, k):
    """Pairs (u, v) of level-k addresses (as bit tuples) shown free at every depth: two automatic states with different parities."""
    from automatic_life import values_at_depth
    vals = [values_at_depth(M, k) for M in Ms]
    base = (1 << k) - 1
    out = set()
    for u in range(1 << k):
        for v in range(u + 1, 1 << k):
            par = {f[base + u] ^ f[base + v] for f in vals}
            if len(par) == 2:
                out.add((u, v))
    return out


def search_bounded3(key, Ms, k0=3, max_size=3):
    """First anchored chain from level k0 such that every step has a tie to the anchor, or a constrained triple {x_i, x_i', y_j}
    with (x_i, x_i') free at every depth (two automatic states with different parities). Then L_N(k0, s) <= 3 for every s, N."""
    E = Extended(Description(key))
    free = free_pairs_from_machines(Ms, k0)
    level = addresses(k0)
    num = {x: int(''.join(map(str, x)), 2) for x in level}
    for size in range(2, max_size + 1):
        for S in itertools.combinations(level, size):
            for pre, cyc in letter_rules(size, periodic=size <= 3):
                r = run_anchored(E, list(S), list(pre), list(cyc))
                if 'period' not in r:
                    continue

                def good(h):
                    if h['ties']:
                        return 'tie'
                    for i, i2, j in h['triples']:
                        a, b = sorted((num[S[i]], num[S[i2]]))
                        if (a, b) in free:
                            return 'triple'
                    return None
                verdicts = [good(h) for h in r['history']]
                if all(verdicts):
                    return dict(k0=k0, S=[''.join(map(str, x)) for x in S], prefix=[list(v) for v in pre],
                                cycle=[list(v) for v in cyc], start=r['start'], period=r['period'], verdicts=verdicts)
    return None


def run_anchored_machines(E, S, letters_prefix, letters_cycle, Ms, max_steps=400):
    """run_anchored, also reporting constrained triples {x_i, y_j, y_j'} (one anchor element, two elements of S_(k+1)) and, from
    the automatic states Ms carried along the chain (each machine's state at every element), the pairs of S_(k+1) shown free at
    every depth (two machines with different parities). The machines' states are part of the periodic state."""
    n = len(S)
    T = initial_type(E, S)
    m = frozenset((a, a) for a in range(1 << n))
    q = []
    for M in Ms:
        row = []
        for x in S:
            st = M[2]
            for b in x:
                st = M[0][st][b]
            row.append(st)
        q.append(tuple(row))
    q = tuple(q)
    L = len(letters_prefix)
    seen, history = {}, []
    for step in range(max_steps):
        if step >= L:
            phase = (step - L) % len(letters_cycle)
            state = (T, m, q, phase)
            if state in seen:
                start = seen[state]
                return dict(steps=step, start=start, period=step - start, history=history)
            seen[state] = step
        c = letters_prefix[step] if step < L else letters_cycle[(step - L) % len(letters_cycle)]
        knots = window_knots(E, T)
        by_x = {}
        for x, y in window_states(n, knots):
            by_x.setdefault(x, set()).add(child_part(y, n, c))
        new = frozenset((a, z) for a, x in m for z in by_x.get(x, ()))
        if not new:
            return dict(dead_at=step, history=history)
        nq = tuple(tuple(M[0][row[i]][c[i]] for i in range(n)) for M, row in zip(Ms, q))
        free_deep = set()
        for j in range(n):
            for j2 in range(j + 1, n):
                par = {M[1][row[j]] ^ M[1][row[j2]] for M, row in zip(Ms, nq)}
                if len(par) == 2:
                    free_deep.add((j, j2))
        ties, triples, deep_triples = [], [], []
        for j in range(n):
            for i in range(n):
                vals = {((a >> i) ^ (z >> j)) & 1 for a, z in new}
                if len(vals) == 1:
                    ties.append((i, j, vals.pop()))
            for i in range(n):
                for i2 in range(i + 1, n):
                    pats = {(((a >> i) & 1), ((a >> i2) & 1), ((z >> j) & 1)) for a, z in new}
                    if len(pats) < 8:
                        triples.append((i, i2, j))
        for i in range(n):
            for j, j2 in free_deep:
                pats = {(((a >> i) & 1), ((z >> j) & 1), ((z >> j2) & 1)) for a, z in new}
                if len(pats) < 8:
                    deep_triples.append((i, j, j2))
        history.append(dict(ties=ties, triples=triples, deep_triples=deep_triples, knots=len(knots)))
        T = next_type(E, T, c)
        m = new
        q = nq
    return dict(reason='no repeat within %d steps' % max_steps, history=history)


def search_bounded3_machines(key, Ms, k0=3, max_size=3):
    """As search_bounded3, also accepting a constrained triple {x_i, y_j, y_j'} whose deep pair is free at every depth."""
    E = Extended(Description(key))
    free = free_pairs_from_machines(Ms, k0)
    level = addresses(k0)
    num = {x: int(''.join(map(str, x)), 2) for x in level}
    for size in range(1, max_size + 1):
        for S in itertools.combinations(level, size):
            for pre, cyc in letter_rules(size, periodic=size <= 3):
                r = run_anchored_machines(E, list(S), list(pre), list(cyc), Ms)
                if 'period' not in r:
                    continue

                def good(h):
                    if h['ties']:
                        return 'tie'
                    for i, i2, j in h['triples']:
                        if tuple(sorted((num[S[i]], num[S[i2]]))) in free:
                            return 'top-top-deep'
                    if h['deep_triples']:
                        return 'top-deep-deep'
                    return None
                verdicts = [good(h) for h in r['history']]
                if all(verdicts):
                    return dict(k0=k0, S=[''.join(map(str, x)) for x in S], prefix=[list(v) for v in pre],
                                cycle=[list(v) for v in cyc], start=r['start'], period=r['period'], verdicts=verdicts)
    return None
