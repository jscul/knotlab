"""Atom patterns: native rounds, untangling phases, rank and fringe.

An atom pattern is an array of atoms (a, b, c), each read "a and b together
demand c" (the clause ~a ~b c), over distinctions 0..n-1, together with a set
of held distinctions, set to 1 by the outside.  A distinction is forced when
it is 1 in every allowed state with the held ones at 1; for atoms that is the
forward closure of the held set.

Native rounds: every atom whose two demanders are forced forces its demanded
distinction one round later.  Untangling phases: at a phase's start every
atom with a forced demander is read as the two-place rule other -> demanded,
and the phase adds everything reachable along those rules.  Rank: held
distinctions have rank 0, an atom gives combine(r_a, r_b) (the larger, or one
more when equal), and a distinction takes the least rank of a derivation
tree (relaxation downward from infinity, independently of the phases; the
numerically least solution of the equations would be wrong on unsupported
cycles).

The dual law spreads unforcedness on acyclic patterns: an atom dies when a
demander is unforced; an unheld distinction is unforced when every atom
demanding it is dead.  At a dual phase's start, an unheld distinction with
no live atom is a seed, and one with exactly one live atom (a, b -> v) gets
the rules a -> v and b -> v; the phase adds what is reachable.  Its count is
the least generalized Strahler number of a derivation of unforcedness (the
largest child, plus one when the largest occurs twice or more).
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order

INF = np.iinfo(np.int64).max // 4


class Pattern:
    def __init__(self, n, atoms, held):
        self.n = int(n)
        atoms = np.asarray(atoms, dtype=np.int64).reshape(-1, 3)
        self.a, self.b, self.c = atoms[:, 0].copy(), atoms[:, 1].copy(), atoms[:, 2].copy()
        self.held = np.zeros(self.n, dtype=bool)
        self.held[np.asarray(list(held), dtype=np.int64)] = True

    @property
    def m(self):
        return len(self.a)


def native_rounds(p):
    """Synchronous rounds; returns (forced mask, round of first forcing, R)."""
    forced = p.held.copy()
    when = np.where(forced, 0, -1).astype(np.int64)
    r = 0
    while True:
        fire = forced[p.a] & forced[p.b] & ~forced[p.c]
        if not fire.any():
            return forced, when, r
        r += 1
        new = np.unique(p.c[fire])
        forced[new] = True
        when[new] = r


def _reach(n, src_mask, tails, heads):
    """Distinctions reachable from src_mask along directed rules tail -> head."""
    s = n  # super-source
    rows = np.concatenate([tails, np.full(int(src_mask.sum()), s)])
    cols = np.concatenate([heads, np.flatnonzero(src_mask)])
    g = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n + 1, n + 1))
    order = breadth_first_order(g, s, directed=True, return_predecessors=False)
    out = np.zeros(n, dtype=bool)
    order = order[order != s]
    out[order] = True
    return out | src_mask


def untangling_phases(p):
    """Phases of two-place reasoning; returns (forced mask, phase of first forcing, P)."""
    forced = p.held.copy()
    phase = np.where(forced, 0, -1).astype(np.int64)
    t = 0
    while True:
        fa, fb = forced[p.a], forced[p.b]
        tails = np.concatenate([p.b[fa], p.a[fb]])
        heads = np.concatenate([p.c[fa], p.c[fb]])
        new = _reach(p.n, forced, tails, heads) & ~forced
        if not new.any():
            return forced, phase, t
        t += 1
        forced |= new
        phase[new] = t


def dual_phases(p):
    """Phases of the dual law on an acyclic pattern; phase 0 already follows
    the rules from the undemanded unheld distinctions.  Returns (unforced
    mask, phase, P_dual = number of reachability computations, 0 when no
    distinction is unforced)."""
    held = p.held
    unf = np.zeros(p.n, dtype=bool)
    phase = np.full(p.n, -1, dtype=np.int64)
    demanded = np.bincount(p.c, minlength=p.n) > 0
    seeds = ~held & ~demanded
    if not seeds.any():
        return unf, phase, 0
    t = 0
    while True:
        dead = unf[p.a] | unf[p.b]
        alive_cnt = np.bincount(p.c[~dead], minlength=p.n)
        open_v = ~held & ~unf
        if t > 0:
            seeds = open_v & (alive_cnt == 0)
        one = ~dead & (alive_cnt[p.c] == 1) & open_v[p.c]
        tails = np.concatenate([p.a[one], p.b[one]])
        heads = np.concatenate([p.c[one], p.c[one]])
        new = _reach(p.n, unf | seeds, tails, heads) & ~unf & ~held
        if not new.any():
            return unf, phase, t
        unf |= new
        phase[new] = t
        t += 1


def dual_rank(p):
    """Least generalized Strahler number of a derivation of unforcedness."""
    held = p.held
    m = p.m
    order = np.argsort(p.c, kind="stable")
    cs = p.c[order]
    starts = np.searchsorted(cs, np.arange(p.n + 1))
    demanded = starts[1:] > starts[:-1]
    d = np.where(~held & ~demanded, 0, INF).astype(np.int64)
    while True:
        death = np.minimum(d[p.a], d[p.b])[order]  # per atom, grouped by c
        mx = np.full(p.n, -1, dtype=np.int64)
        np.maximum.at(mx, cs, death)
        cnt = np.zeros(p.n, dtype=np.int64)
        np.add.at(cnt, cs, (death == mx[cs]).astype(np.int64))
        cand = np.where(mx >= INF, INF, np.where(cnt >= 2, mx + 1, mx))
        cand = np.where(held | ~demanded, d, cand)
        upd = cand < d
        if not upd.any():
            return d
        d = np.where(upd, cand, d)


def combine(ra, rb):
    """Elementwise rank of an atom from its demanders' ranks (INF stays INF)."""
    ra = np.asarray(ra)
    rb = np.asarray(rb)
    hi = np.maximum(ra, rb)
    out = np.where(ra == rb, hi + 1, hi)
    return np.where(hi >= INF, INF, out)


def rank(p, max_iter=None):
    """Least rank over derivations, by relaxation from INF (held = 0)."""
    r = np.where(p.held, 0, INF).astype(np.int64)
    it = 0
    while True:
        it += 1
        cand = combine(r[p.a], r[p.b])
        best = np.full(p.n, INF, dtype=np.int64)
        np.minimum.at(best, p.c, cand)
        upd = best < r
        if not upd.any():
            return r
        r = np.where(upd, best, r)
        if max_iter and it > max_iter:
            raise RuntimeError("rank relaxation did not settle")


def log2_fringe(p):
    """log2 of the fewest held leaves (with multiplicity) in a derivation tree."""
    f = np.where(p.held, 0.0, np.inf)  # log2 of leaf count
    while True:
        fa, fb = f[p.a], f[p.b]
        hi = np.maximum(fa, fb)
        lo = np.minimum(fa, fb)
        with np.errstate(invalid="ignore"):
            cand = np.where(np.isinf(hi), np.inf, hi + np.log2(1.0 + np.exp2(lo - hi)))
        best = np.full(p.n, np.inf)
        np.minimum.at(best, p.c, cand)
        upd = best < f - 1e-12
        if not upd.any():
            return f
        f = np.where(upd, best, f)


# ---------------------------------------------------------------- generators

def random_pattern(n, c, rng):
    """m = round(c n) atoms with three distinct uniformly random distinctions."""
    m = int(round(c * n))
    trip = np.empty((m, 3), dtype=np.int64)
    trip[:, 0] = rng.integers(0, n, m)
    trip[:, 1] = rng.integers(0, n - 1, m)
    trip[:, 1] += trip[:, 1] >= trip[:, 0]
    lo = np.minimum(trip[:, 0], trip[:, 1])
    hi = np.maximum(trip[:, 0], trip[:, 1])
    z = rng.integers(0, n - 2, m)
    z += z >= lo
    z += z >= hi
    trip[:, 2] = z
    return trip


def chain(L):
    """x_0 held; (x_i, h_i -> x_{i+1}) with h_i held."""
    x = list(range(L + 1))
    h = list(range(L + 1, 2 * L + 1))
    atoms = [(x[i], h[i], x[i + 1]) for i in range(L)]
    return Pattern(2 * L + 1, atoms, [x[0]] + h), x[L]


def ladder(k):
    """x_{i+1} demanded by y_i and z_i, each demanded by x_i with one held helper."""
    n = 0
    def new():
        nonlocal n
        n += 1
        return n - 1
    hold1, hold2 = new(), new()
    x = [new()]
    atoms = []
    for _ in range(k):
        y, z, xn = new(), new(), new()
        atoms += [(x[-1], hold1, y), (x[-1], hold2, z), (y, z, xn)]
        x.append(xn)
    return Pattern(n, atoms, [hold1, hold2, x[0]]), x[-1]


def pyramid(h):
    """Rows 0..h; row 0 held; v(i,j) demanded by v(i-1,j) and v(i-1,j+1)."""
    idx = {}
    for i in range(h + 1):
        for j in range(h + 1 - i):
            idx[i, j] = len(idx)
    atoms = [(idx[i - 1, j], idx[i - 1, j + 1], idx[i, j]) for i in range(1, h + 1) for j in range(h + 1 - i)]
    return Pattern(len(idx), atoms, [idx[0, j] for j in range(h + 1)]), idx[h, 0]


def balanced_and_tree(d):
    """Complete binary tree of atoms of height d over 2^d held leaves (no reuse)."""
    leaves = list(range(2 ** d))
    n = len(leaves)
    level, atoms = leaves, []
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            atoms.append((level[i], level[i + 1], n))
            nxt.append(n)
            n += 1
        level = nxt
    return Pattern(n, atoms, leaves), level[0]


def alternating_circuit(depth, width, rng, p_one=0.5, first="AND", mixed=False):
    """Layered monotone circuit, fan-in 2 from the layer below (two distinct
    random gates).  Gates alternate AND/OR by layer, or, with mixed=True, each
    gate is AND or OR with chance 1/2 (then the true fraction is a martingale).
    Each layer is (is_and boolean array, input pairs)."""
    inputs = (rng.random(width) < p_one).astype(bool)
    layers = []
    kind = first
    for _ in range(depth):
        pairs = np.empty((width, 2), dtype=np.int64)
        pairs[:, 0] = rng.integers(0, width, width)
        pairs[:, 1] = rng.integers(0, width - 1, width)
        pairs[:, 1] += pairs[:, 1] >= pairs[:, 0]
        is_and = rng.random(width) < 0.5 if mixed else np.full(width, kind == "AND")
        layers.append((is_and, pairs))
        kind = "OR" if kind == "AND" else "AND"
    return inputs, layers


def unlayered_circuit(n_inputs, n_gates, rng, p_one=0.5):
    """Each gate reads two distinct random earlier nodes (inputs or gates) and
    is AND or OR with chance 1/2.  Returned as one layer per gate over the
    growing node list, for evaluation and conversion."""
    inputs = (rng.random(n_inputs) < p_one).astype(bool)
    gates = []
    for g in range(n_gates):
        k = n_inputs + g
        x = int(rng.integers(0, k))
        y = int(rng.integers(0, k - 1))
        y += y >= x
        gates.append((bool(rng.random() < 0.5), x, y))
    return inputs, gates


def unlayered_to_atoms(inputs, gates):
    n_in = len(inputs)
    t = 0
    node = list(range(1, n_in + 1))
    n = n_in + 1
    atoms = []
    for is_and, x, y in gates:
        g = n
        n += 1
        if is_and:
            atoms.append((node[x], node[y], g))
        else:
            atoms += [(node[x], t, g), (node[y], t, g)]
        node.append(g)
    vals = list(inputs.tolist())
    for is_and, x, y in gates:
        vals.append((vals[x] and vals[y]) if is_and else (vals[x] or vals[y]))
    held = [t] + [node[i] for i in range(n_in) if inputs[i]]
    return Pattern(n, atoms, held), np.array(node), np.array(vals, dtype=bool)


def evaluate_circuit(inputs, layers):
    vals = [inputs.copy()]
    for is_and, pairs in layers:
        u, v = vals[-1][pairs[:, 0]], vals[-1][pairs[:, 1]]
        vals.append(np.where(is_and, u & v, u | v))
    return vals


def circuit_to_atoms(inputs, layers):
    """Monotone circuit value as an atom pattern (Goldschlager's problem in Horn
    form): input gates true are held; AND gate g = (x, y -> g); OR gate g = two
    atoms (x, t -> g), (y, t -> g) with one shared held distinction t."""
    width = len(inputs)
    t = 0
    ids = [np.arange(1, width + 1)]
    n = width + 1
    atoms = []
    for is_and, pairs in layers:
        g = np.arange(n, n + width)
        n += width
        x, y = ids[-1][pairs[:, 0]], ids[-1][pairs[:, 1]]
        o = ~is_and
        atoms.append(np.stack([x[is_and], y[is_and], g[is_and]], 1))
        atoms.append(np.stack([x[o], np.full(int(o.sum()), t), g[o]], 1))
        atoms.append(np.stack([y[o], np.full(int(o.sum()), t), g[o]], 1))
        ids.append(g)
    held = [t] + list(ids[0][inputs])
    return Pattern(n, np.concatenate(atoms) if atoms else np.zeros((0, 3)), held), ids


# ---------------------------------------------------------- not-all-equal side

def nae_propagate(n, triples, assigned):
    """Unit propagation for not-all-equal triples from a partial assignment
    {var: 0/1}: two equal members force the third to differ.  Returns the
    final partial assignment and the round count, or None on a conflict."""
    val = dict(assigned)
    rounds = 0
    while True:
        new = {}
        for t in triples:
            known = [(v, val[v]) for v in t if v in val]
            if len(known) == 3:
                if known[0][1] == known[1][1] == known[2][1]:
                    return None, rounds
            elif len(known) == 2 and known[0][1] == known[1][1]:
                (u,) = [v for v in t if v not in val]
                want = 1 - known[0][1]
                if new.get(u, want) != want:
                    return None, rounds
                new[u] = want
        if not new:
            return val, rounds
        rounds += 1
        val.update(new)


def circuit_to_nae(inputs, layers):
    """Monotone circuit as not-all-equal triples with two held constants
    T = 1 and F = 0.  A wire carries 'set to 1' or 'unset'.  AND: NAE(x, y, g0)
    sets g0 = 0 exactly when x = y = 1; NAE(g0, F, g) then sets g = 1.  OR:
    NAE(x, T, g0) and NAE(y, T, g0) set g0 = 0 when either is 1; NAE(g0, F, g)
    flips back.  Inputs true are assigned 1; false inputs stay unset."""
    width = len(inputs)
    T, F = 0, 1
    n = 2
    ids = [np.arange(n, n + width)]
    n += width
    triples = []
    for is_and, pairs in layers:
        prev = ids[-1]
        g0 = np.arange(n, n + width); n += width
        g = np.arange(n, n + width); n += width
        for i in range(width):
            x, y = int(prev[pairs[i, 0]]), int(prev[pairs[i, 1]])
            if is_and[i]:
                triples.append((x, y, int(g0[i])))
            else:
                triples.append((x, T, int(g0[i])))
                triples.append((y, T, int(g0[i])))
            triples.append((int(g0[i]), F, int(g[i])))
        ids.append(g)
    assigned = {T: 1, F: 0}
    for i in range(width):
        if inputs[i]:
            assigned[int(ids[0][i])] = 1
    return n, triples, assigned, ids
