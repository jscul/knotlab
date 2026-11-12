"""Bases within bases (research/BASES-WITHIN-20261112-001/preregistration.md, ticket A).

A harmony (A70) is a one-shift not-all-equal base all of whose states repeat; W is its set of states (periodic words, closed under
shifts and the mirror), P the least common multiple of their periods. Bases within bases: each distinction X_j of an outer base O
becomes a copy of an inner harmony I (distinctions x_(j,i), i an integer, with I's knots), and each outer knot NAE(X_a, X_b, X_c)
becomes NAE(x_(a,i), x_(b,i), x_(c,i)) at every place i. Written O[I]. With O = I = H at every level, level k is the base along k
shifts whose every line (all coordinates but one fixed) is a state of H (the literature's axial power of H).

Every state of O[I] repeats with period dividing P along the inner shift (its rows are states of I), so states are enumerated on Z_P:
row j is a cyclic word of length P satisfying I's kinds cyclically, which is the same as a state of I of period dividing P."""
import itertools
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HARMONY-ARITH-20261112-001A/HARMONY-ARITH-20261112-001A-P001_binding_and_harmonies"))
import harm_lib as H  # noqa: E402


def harmonies(max_span=8, max_period=16):
    """distinct NAE harmony state sets of 1 to 3 kinds, span 2 to max_span: (orbit words, one kind set, P), P <= max_period"""
    seen = {}
    for Wsp in range(2, max_span + 1):
        for S in H.patterns(Wsp):
            st, cyc = H.classify(Wsp, S, "NAE")
            if st != "harmony":
                continue
            key = tuple(sorted(H.canon(c) for c in cyc))
            if key not in seen:
                seen[key] = S
    out = []
    for key, S in seen.items():
        P = 1
        for w in key:
            P = P * len(w) // __import__("math").gcd(P, len(w))
        if P <= max_period:
            out.append({"orbits": ["".join(map(str, w)) for w in key], "kinds": [list(k) for k in S], "P": P})
    return sorted(out, key=lambda h: (sum(len(o) for o in h["orbits"]), h["orbits"]))


def states(h):
    """every state of the harmony as a cyclic word of length P"""
    P = h["P"]
    out = set()
    for o in h["orbits"]:
        p = len(o)
        for r in range(p):
            out.add(tuple(int(o[(i + r) % p]) for i in range(P)))
    return sorted(out)


def knot_clauses(t, law="NAE"):
    """clauses of one knot on the variables t under the law (NAE; 'exactly one' only for the positive control)"""
    if law == "NAE":
        return [[t[0], t[1], t[2]], [-t[0], -t[1], -t[2]]]
    if law == "exactly one":
        return [[t[0], t[1], t[2]], [-t[0], -t[1]], [-t[0], -t[2]], [-t[1], -t[2]]]
    raise ValueError(law)


def line_clauses(var, P, kinds, law="NAE"):
    """knots of the given kinds, cyclically on one line of length P; var(i) is the variable at place i"""
    cl = []
    for (_, a, b) in kinds:
        for i in range(P):
            cl += knot_clauses((var(i), var((i + a) % P), var((i + b) % P)), law)
    return cl


def count(cl, nvars, cap, project=None):
    """number of solutions (or of distinct values of the projected variables), None over the cap"""
    seen = 0
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            seen += 1
            if seen > cap:
                return None
            vs = project if project is not None else range(1, nvars + 1)
            s.add_clause([-v if m[v - 1] > 0 else v for v in vs])
    return seen


def axial_clauses(h, k):
    """level k: Z_P^k, the harmony's kinds along every line of every axis"""
    P = h["P"]
    idx = {c: n + 1 for n, c in enumerate(itertools.product(range(P), repeat=k))}
    cl = []
    for axis in range(k):
        for rest in itertools.product(range(P), repeat=k - 1):
            def var(i, rest=rest, axis=axis):
                c = list(rest[:axis]) + [i] + list(rest[axis:])
                return idx[tuple(c)]
            cl += line_clauses(var, P, h["kinds"])
    return cl, idx


def axial_count(h, k, cap=200000):
    cl, idx = axial_clauses(h, k)
    return count(cl, len(idx), cap)


def linear_states(h, k):
    """states of the form x(c) = u(m . c + a), u a state, m in Z_P^k, whose every line is a state: their number"""
    P = h["P"]
    W = set(states(h))
    coords = list(itertools.product(range(P), repeat=k))
    good_m = []
    for m in itertools.product(range(P), repeat=k):
        # every line along axis t reads u(m_t * i + const): a state for every u and const iff the decimated word is a state
        ok = True
        for t in range(k):
            for u in W:
                if tuple(u[(m[t] * i) % P] for i in range(P)) not in W:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            good_m.append(m)
    arrays = set()
    for u in W:
        for m in good_m:
            arrays.add(tuple(u[sum(mi * ci for mi, ci in zip(m, c)) % P] for c in coords))
    return len(arrays)


def composite_clauses(outer_knots, nouter, h, offsets=None, law="NAE"):
    """O[I] for a finite outer pattern: rows j = 0..nouter-1 are states of I on Z_P; outer knot (a, b, c) binds x_(a,i+s), x_(b,i+t),
    x_(c,i+u) at every place i, (s, t, u) its offsets (all 0: a binding at one place)"""
    P = h["P"]

    def v(j, i):
        return j * P + (i % P) + 1
    cl = []
    for j in range(nouter):
        cl += line_clauses(lambda i, j=j: v(j, i), P, h["kinds"], law)
    for n, (a, b, c) in enumerate(outer_knots):
        s, t, u = offsets[n] if offsets is not None else (0, 0, 0)
        for i in range(P):
            cl += knot_clauses((v(a, i + s), v(b, i + t), v(c, i + u)), law)
    return cl, v


def lives(outer_knots, nouter, h, offsets=None, law="NAE"):
    cl, v = composite_clauses(outer_knots, nouter, h, offsets, law)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return s.solve()


def chain_free(outer_knots):
    """no closed chain of knots: the incidence of distinctions and knots has no cycle (the literature's Berge-acyclic pattern)"""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for n, e in enumerate(outer_knots):
        for x in e:
            a, b = find(("k", n)), find(("d", x))
            if a == b:
                return False
            parent[a] = b
    return True


def signed_nae_lives(outer_knots, nouter, signs):
    """the alternation's offsets read as signs: x_(j,i+s) = x_(j,i) xor (s mod 2); brute force over the outer distinctions"""
    for x in itertools.product((0, 1), repeat=nouter):
        if all(not ((x[a] ^ sa) == (x[b] ^ sb) == (x[c] ^ sc)) for (a, b, c), (sa, sb, sc) in zip(outer_knots, signs)):
            return True
    return False


def outer_states(outer_knots, nouter):
    return {s for s in itertools.product((0, 1), repeat=nouter) if all(not (s[a] == s[b] == s[c]) for (a, b, c) in outer_knots)}


def column_projection(outer_knots, nouter, h):
    """the set of column-0 values of the states of O[I] (the outer states O[I] realises), for a binding at one place"""
    cl, v = composite_clauses(outer_knots, nouter, h)
    proj = [v(j, 0) for j in range(nouter)]
    out = set()
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            col = tuple(int(m[x - 1] > 0) for x in proj)
            out.add(col)
            s.add_clause([-x if m[x - 1] > 0 else x for x in proj])
    return out


def outer_patterns(max_vars=6, max_knots=4):
    """connected NAE knot patterns (3-sets) on up to max_vars distinctions with 1 to max_knots knots, one per isomorphism class"""
    found = {}
    for n in range(3, max_vars + 1):
        triples = list(itertools.combinations(range(n), 3))
        perms = list(itertools.permutations(range(n)))
        for m in range(1, max_knots + 1):
            for E in itertools.combinations(triples, m):
                if set(itertools.chain(*E)) != set(range(n)):
                    continue
                # connected
                comp = {0}
                grow = True
                while grow:
                    grow = False
                    for e in E:
                        if comp & set(e) and not set(e) <= comp:
                            comp |= set(e)
                            grow = True
                if comp != set(range(n)):
                    continue
                key = min(tuple(sorted(tuple(sorted(p[x] for x in e)) for e in E)) for p in perms)
                found.setdefault((n, key), key)
    return [(n, list(k)) for (n, k) in sorted(found)]


FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def pair_count(ho, hi, cap=200000):
    """O[I] for two harmonies: rows states of hi (period P_I), columns states of ho (period P_O), on Z_PO x Z_PI"""
    Po, Pi = ho["P"], hi["P"]

    def v(j, i):
        return j * Pi + i + 1
    cl = []
    for j in range(Po):
        cl += line_clauses(lambda i, j=j: v(j, i), Pi, hi["kinds"])
    for i in range(Pi):
        cl += line_clauses(lambda j, i=i: v(j, i), Po, ho["kinds"])
    return count(cl, Po * Pi, cap)


def known_arrays(h, k):
    """the linear states u(m . c + a) and the mirror-lift states u_1(c_1) xor ... xor u_k(c_k), each u a state: their union's size,
    and each family's"""
    P = h["P"]
    W = states(h)
    Ws = set(W)
    coords = list(itertools.product(range(P), repeat=k))
    good_m = [m for m in itertools.product(range(P), repeat=k)
              if all(tuple(u[(m[t] * i) % P] for i in range(P)) in Ws for t in range(k) for u in W)]
    lin = {tuple(u[sum(mi * ci for mi, ci in zip(m, c)) % P] for c in coords) for u in W for m in good_m}
    xor = set()
    for us in itertools.product(W, repeat=k):
        xor.add(tuple(sum(us[t][c[t]] for t in range(k)) % 2 for c in coords))
    return {"linear": len(lin), "mirror lift": len(xor), "union": len(lin | xor)}


CONTROL_INNER = {"orbits": ["001"], "kinds": [[0, 1, 2]], "P": 3}   # exactly one: x_i + x_(i+1) + x_(i+2) = 1, states the shifts of 001
CONTROL_OUTER = (5, [(0, 1, 2), (0, 1, 3), (2, 3, 4)])               # the advisor's: O has 2 states under exactly one; O[I] must end


def control():
    """positive control: a law without the mirror, where a binding at one place ends a living outer pattern"""
    n, E = CONTROL_OUTER
    o = sum(1 for x in itertools.product((0, 1), repeat=n) if all(x[a] + x[b] + x[c] == 1 for (a, b, c) in E))
    return {"outer states": o, "O[I] lives": lives(E, n, CONTROL_INNER, law="exactly one")}


def tie_class(knots, nvars, root, law="NAE"):
    """the distinctions tied to root: equal to it in every state, or unequal in every state (None if no state). Knots are triples of
    variable numbers 1..nvars. A model that separates root from a candidate removes every candidate it separates."""
    cl = []
    for t in knots:
        cl += knot_clauses(t, law)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        if not s.solve():
            return None
        m0 = s.get_model()
        val = lambda m, v: m[v - 1] > 0
        rel = {v: val(m0, root) ^ val(m0, v) for v in range(1, nvars + 1)}
        cand = set(rel) - {root}
        tied = {root}
        while cand:
            y = min(cand)
            a = [root if val(m0, root) else -root, -y if val(m0, y) else y]
            if s.solve(assumptions=a):
                m = s.get_model()
                cand -= {v for v in cand if (val(m, root) ^ val(m, v)) != rel[v]}
            else:
                cand.discard(y)
                tied.add(y)
        return tied


def bond_distances(knots, nvars, root):
    """fewest knots in a chain from root to each distinction"""
    adj = {v: set() for v in range(1, nvars + 1)}
    for t in knots:
        for a in t:
            adj[a] |= set(t) - {a}
    dist = {root: 0}
    frontier = [root]
    while frontier:
        nxt = []
        for a in frontier:
            for b in adj[a]:
                if b not in dist:
                    dist[b] = dist[a] + 1
                    nxt.append(b)
        frontier = nxt
    return dist


# ---- the finite seed arms ----

SEEDS = {
    "one knot": (3, [(0, 1, 2)]),
    "two knots sharing one": (5, [(0, 1, 2), (2, 3, 4)]),
    "two knots sharing two": (4, [(0, 1, 2), (0, 1, 3)]),
    "closed chain of three": (6, [(0, 1, 2), (2, 3, 4), (4, 5, 0)]),
    "Fano less one knot": (7, FANO[:-1]),
}


def box_power(m, E, k):
    """level k of a finite seed: addresses in {0..m-1}^k; for each digit t and each knot (a, b, c) of the seed, a knot on the three
    addresses equal except at digit t, which reads a, b, c (the literature's Cartesian product of the seed with itself k times)"""
    addrs = list(itertools.product(range(m), repeat=k))
    idx = {d: n + 1 for n, d in enumerate(addrs)}
    knots = []
    for t in range(k):
        for d in addrs:
            if d[t] != 0:
                continue
            for (a, b, c) in E:
                knots.append(tuple(idx[d[:t] + (x,) + d[t + 1:]] for x in (a, b, c)))
    return knots, idx


def seed_ties(m, E):
    """tie relation of the seed: for each pair (a, b), None if untied, else the constant a xor b"""
    sts = [s for s in itertools.product((0, 1), repeat=m) if all(not (s[a] == s[b] == s[c]) for (a, b, c) in E)]
    rel = {}
    for a in range(m):
        for b in range(m):
            vals = {s[a] ^ s[b] for s in sts}
            rel[(a, b)] = vals.pop() if len(vals) == 1 else None
    return rel, len(sts)


def predicted_box_ties(m, E, k, d):
    """the product-tie lemma's prediction for the tie class of address d"""
    rel, _ = seed_ties(m, E)
    out = set()
    for e in itertools.product(range(m), repeat=k):
        if all(rel[(d[t], e[t])] is not None for t in range(k)):
            out.add(e)
    return out


def gasket(level):
    """the drawn three-copy nesting of one knot (the literature's Sierpinski gasket): level 0 is one knot on corners A, B, C;
    level n is three copies of level n-1, copy 0 at A, copy 1 at B, copy 2 at C, the copies sharing their meeting corners.
    Returns (knots, number of distinctions, the corners A, B, C)."""
    knots = [(1, 2, 3)]
    n, A, B, C = 3, 1, 2, 3
    for _ in range(level):
        # copy 0 keeps the labels; copies 1 and 2 are relabelled, with copy0.B = copy1.A, copy0.C = copy2.A, copy1.C = copy2.B
        def relabel(base_knots, base_n, mapping_fixed, offset):
            mp = {}
            nxt = offset
            for v in range(1, base_n + 1):
                if v in mapping_fixed:
                    mp[v] = mapping_fixed[v]
                else:
                    nxt += 1
                    mp[v] = nxt
            return [tuple(mp[x] for x in kn) for kn in base_knots], mp, nxt
        k0 = knots
        k1, m1, top = relabel(knots, n, {A: B}, n)
        k2, m2, top = relabel(knots, n, {A: C, B: m1[C]}, top)
        knots = k0 + k1 + k2
        A, B, C = A, m1[B], m2[C]
        n = top
    return knots, n, (A, B, C)


def axial_knots(h, k):
    """the knots of level k of a harmony on Z_P^k, as triples of variable numbers"""
    P = h["P"]
    idx = {c: n + 1 for n, c in enumerate(itertools.product(range(P), repeat=k))}
    knots = []
    for axis in range(k):
        for rest in itertools.product(range(P), repeat=k - 1):
            def var(i, rest=rest, axis=axis):
                return idx[tuple(list(rest[:axis]) + [i % P] + list(rest[axis:]))]
            for (_, a, b) in h["kinds"]:
                for i in range(P):
                    knots.append((var(i), var(i + a), var(i + b)))
    return knots, idx


def harmony_line_ties(h):
    """places of Z_P tied to place 0 in every state of the harmony"""
    W = states(h)
    return {i for i in range(h["P"]) if len({u[0] ^ u[i] for u in W}) == 1}
