#!/usr/bin/env python3
"""Checks for AFFINE-TOPS-20261021-001B-P001. The statements are in proof.md.

Laws: those of AFFINE-TOPS-20261021-001A-P001's checks (eleven census laws of CYCLE-TOPS-20261021-001A-E001 and the
3-net laws of Z4, Z2xZ2 and Z2xZ4, with certified tops), and the GF(4) law {(x, y, x + w y)}, whose top on GF(4) is
equality (certified below by polymorphisms that break every coarser equivalence).

Checks:
- Theorem 1. In random systems of every law, at every variable e of every knot and a second variable i:
  - the parallelogram relation's top image is the graph of one operation on e's top, Mal'tsev, the same for every knot
    through the range;
  - for the six small laws, every polymorphism found by randomized search that is Mal'tsev modulo the tops of the knot
    ranges induces exactly that operation, and every sampled polymorphism commutes with it;
  - the operation commutes with itself; x + y = F(x, o, y) is an abelian group with F = x - y + z, of exponent p;
  - the top image of every sampled system, restricted to variables with knot ranges, is closed under it coordinatewise.
- Corollary 2. Every three-variable circuit's top image is, after relabelling, the addition table of its group.
- Theorem 3. For every sampled system: components of rank two or more consist of variables with knot ranges; for
  laws whose knot tops have prime order p, the matroid equals the column matroid over GF(p) of a generator matrix
  read off the top image; for the 3-net of Z2xZ2 (tops of order 4, field GF(2)) every matroid has a binary
  representation; for the GF(4) law every matroid has a GF(4) representation read off its generator matrix, and the
  explicit system x + w y = z, x + w z = u carries U(2,4), represented over GF(4) and not over GF(2).

Controls, each of which must be rejected:
- 'every top image is closed under the parallelogram operation' (Thomsen's configuration in the 3-net of Q8);
- 'every law composing like cycles carries only binary matroids' (U(2,4) in the GF(4) law);
- 'the field is fixed by the size of the tops' (the tops of the Z2xZ2 3-net and of the GF(4) law both have four
  elements; one law gives binary matroids only in every sampled system, the other a non-binary one);
- 'knot relations are closed under a Mal'tsev operation below the tops' (K4 is not rectangular).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOPS_CENSUS = ROOT / "artifacts" / "CYCLE-TOPS-20261021-001A" / "CYCLE-TOPS-20261021-001A-E001_tops_census"
IMAGES_CENSUS = ROOT / "artifacts" / "KNOT-IMAGES-20261021-001A" / "KNOT-IMAGES-20261021-001A-E001_latin_census"

M3 = sorted(t for t in product(range(3), repeat=3) if sum(t) % 3 == 0)
G = (0, 1, 2, 2)
LIFT = sorted(t for t in product(range(4), repeat=3) if tuple(G[x] for x in t) in set(M3))
LOG = {1: 0, 2: 1, 3: 2}
EXP = {0: 1, 1: 2, 2: 3}


def gf4_mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[(LOG[a] + LOG[b]) % 3]


def gf4_inv(a):
    return EXP[(-LOG[a]) % 3]


# ------------------------------------------------------------------ laws

def cycle_tops_laws():
    out = {}
    for X in ((), ((2, 2, 2),), ((2, 2, 3),), ((2, 2, 3), (2, 3, 2)), ((2, 2, 3), (2, 3, 2), (3, 2, 2))):
        out["L-{" + ",".join("".join(map(str, t)) for t in X) + "}"] = {"sorts": [4], "rels": [((0, 0, 0), sorted(set(LIFT) - set(X)))]}
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    for a in (0, 1):
        g7 = list(range(6)) + [a]
        R = {t for t in product(range(7), repeat=3) if tuple(g7[x] for x in t) in K6} - {(a, a, a)}
        out[f"K6 lift at {a}"] = {"sorts": [7], "rels": [((0, 0, 0), sorted(R))]}
    P3 = sorted(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0)
    out["parity + J"] = {"sorts": [5], "rels": [((0, 0, 0), P3), ((0, 0), [(2, 2), (3, 3), (3, 4), (4, 3)])]}
    K4 = sorted(set(LIFT) - {(2, 2, 2)})
    out["K4 + Z3"] = {"sorts": [7], "rels": [((0, 0, 0), K4), ((0, 0, 0), sorted(tuple(x + 4 for x in t) for t in M3))]}
    out["parity"] = {"sorts": [2], "rels": [((0, 0, 0), P3)]}
    out["Z3"] = {"sorts": [3], "rels": [((0, 0, 0), M3)]}
    return out


def net(L):
    n = len(L)
    return {"sorts": [n, n, n], "rels": [((0, 1, 2), sorted((i, j, L[i][j]) for i in range(n) for j in range(n)))]}


def gf4_law():
    return {"sorts": [4], "rels": [((0, 0, 0), sorted((x, y, x ^ gf4_mul(2, y)) for x in range(4) for y in range(4)))]}


# ------------------------------------------------------------------ systems

def solve(law, sorts, cons):
    n = len(sorts)
    order = []
    for _, vs in cons:
        for v in vs:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    sets = [set(R) for _, R in law["rels"]]
    by_last = {}
    for ri, vs in cons:
        by_last.setdefault(max(pos[v] for v in vs), []).append((sets[ri], vs))
    out, a = [], [0] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in range(law["sorts"][sorts[v]]):
            a[v] = x
            if all(tuple(a[u] for u in vs) in R for R, vs in by_last.get(i, ())):
                go(i + 1)
    go(0)
    return out


def random_system(rng, law, nmax):
    sorts, cons = [], []
    for _ in range(rng.randint(1, 4)):
        ri = rng.randrange(len(law["rels"]))
        vs = []
        for s in law["rels"][ri][0]:
            have = [v for v in range(len(sorts)) if sorts[v] == s]
            if not have or (len(sorts) < nmax and rng.random() < 0.5):
                sorts.append(s)
                vs.append(len(sorts) - 1)
            else:
                vs.append(rng.choice(have))
        cons.append((ri, tuple(vs)))
    return sorts, cons


def range_key(name, B):
    return name + ",".join(map(str, B))


def free_map(Sb, m, sizes):
    fr = {}
    for k in range(1, m + 1):
        for Y in combinations(range(m), k):
            need = 1
            for v in Y:
                need *= sizes[v]
            fr[Y] = len({tuple(t[v] for v in Y) for t in Sb}) == need
    return fr


def circuits(fr):
    return [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]


def components(m, cs):
    parent = list(range(m))

    def f(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for C in cs:
        for v in C[1:]:
            parent[f(v)] = f(C[0])
    comp = {}
    for v in range(m):
        comp.setdefault(f(v), []).append(v)
    return list(comp.values())


def rank_of(fr, Y):
    best = 0
    for k in range(1, len(Y) + 1):
        for Z in combinations(Y, k):
            if fr[tuple(sorted(Z))]:
                best = k
    return best


# ------------------------------------------------------------------ polymorphisms (as in the tops census)

class Solver:
    def __init__(self, D, rels, k):
        self.D, self.rels = D, [[tuple(t) for t in R] for _, R in rels]
        self.args = list(product(range(D), repeat=k))
        self.idx = {a: i for i, a in enumerate(self.args)}
        self.dom0 = [set(range(D)) for _ in self.args]
        self.cons, self.by_var, seen = [], {}, set()
        for ri, R in enumerate(self.rels):
            for ts in product(R, repeat=k):
                sc = (ri, tuple(self.idx[tuple(t[i] for t in ts)] for i in range(len(R[0]))))
                if sc not in seen:
                    seen.add(sc)
                    self.cons.append(sc)
        for ci, (_, sc) in enumerate(self.cons):
            for v in set(sc):
                self.by_var.setdefault(v, []).append(ci)

    def restrict(self, args, values):
        self.dom0[self.idx[args]] &= set(values)

    def _revise(self, dom, ci):
        ri, sc = self.cons[ci]
        support = {v: set() for v in set(sc)}
        for t in self.rels[ri]:
            seen, good = {}, True
            for v, x in zip(sc, t):
                if x not in dom[v] or seen.get(v, x) != x:
                    good = False
                    break
                seen[v] = x
            if good:
                for v, x in seen.items():
                    support[v].add(x)
        changed = []
        for v, s in support.items():
            if s != dom[v]:
                if not s:
                    return None
                dom[v] = s
                changed.append(v)
        return changed

    def _propagate(self, dom, queue):
        queue, inq = list(queue), set(queue)
        while queue:
            ci = queue.pop()
            inq.discard(ci)
            ch = self._revise(dom, ci)
            if ch is None:
                return False
            for v in ch:
                for cj in self.by_var.get(v, ()):
                    if cj not in inq:
                        inq.add(cj)
                        queue.append(cj)
        return True

    def solve(self, rng=None):
        dom = [set(d) for d in self.dom0]
        if any(not d for d in dom) or not self._propagate(dom, range(len(self.cons))):
            return None

        def go(dom):
            free = [v for v, d in enumerate(dom) if len(d) > 1]
            if not free:
                return dom
            v = min(free, key=lambda u: (len(dom[u]), -len(self.by_var.get(u, ()))))
            vals = sorted(dom[v])
            if rng is not None:
                rng.shuffle(vals)
            for x in vals:
                d2 = [set(s) for s in dom]
                d2[v] = {x}
                if self._propagate(d2, self.by_var.get(v, ())):
                    r = go(d2)
                    if r is not None:
                        return r
            return None
        r = go(dom)
        return None if r is None else {a: next(iter(r[i])) for a, i in self.idx.items()}


# ------------------------------------------------------------------ parallelograms and groups

def parallelogram(Kb, k, e, i):
    rest = [v for v in range(k) if v not in (e, i)]
    cell = {}
    for t in Kb:
        cell.setdefault((t[i], tuple(t[v] for v in rest)), set()).add(t[e])
    us = sorted({t[i] for t in Kb})
    ws = sorted({tuple(t[v] for v in rest) for t in Kb})
    P = {}
    for u, u2 in product(us, repeat=2):
        for w, w2 in product(ws, repeat=2):
            for t1 in cell.get((u, w), ()):
                for t2 in cell.get((u2, w), ()):
                    for t3 in cell.get((u, w2), ()):
                        for t4 in cell.get((u2, w2), ()):
                            P.setdefault((t2, t1, t3), set()).add(t4)
    return P


def group_facts(op, n):
    add = lambda x, y: op[(x, 0, y)]
    neg = lambda y: op[(0, y, 0)]
    medial = all(op[(op[(a1, a2, a3)], op[(b1, b2, b3)], op[(c1, c2, c3)])] == op[(op[(a1, b1, c1)], op[(a2, b2, c2)], op[(a3, b3, c3)])]
                 for a1, a2, a3, b1, b2, b3, c1, c2, c3 in product(range(n), repeat=9))
    abelian = all(add(x, y) == add(y, x) and add(add(x, y), z) == add(x, add(y, z)) for x, y, z in product(range(n), repeat=3))
    affine = all(op[(x, y, z)] == add(add(x, neg(y)), z) for x, y, z in product(range(n), repeat=3))
    orders = set()
    for x in range(n):
        s, k = x, 1
        while s != 0:
            s, k = add(s, x), k + 1
        orders.add(k)
    primes = {k for k in orders if k > 1}
    return {"medial": medial, "abelian_group": abelian, "x_minus_y_plus_z": affine, "element_orders": sorted(orders),
            "elementary": len(primes) == 1 and all(all(k % d for d in range(2, k)) for k in primes)}


def rank_mod(rows, cols, q):
    """Rank over GF(q) (q prime, or 4) of the matrix restricted to the given columns."""
    M = [[r[c] for c in cols] for r in rows]
    rank, ncol = 0, len(cols)
    for c in range(ncol):
        piv = next((i for i in range(rank, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        if q == 4:
            inv = gf4_inv(M[rank][c])
            M[rank] = [gf4_mul(inv, x) for x in M[rank]]
            for i in range(len(M)):
                if i != rank and M[i][c] != 0:
                    f = M[i][c]
                    M[i] = [x ^ gf4_mul(f, y) for x, y in zip(M[i], M[rank])]
        else:
            inv = pow(M[rank][c], q - 2, q)
            M[rank] = [(inv * x) % q for x in M[rank]]
            for i in range(len(M)):
                if i != rank and M[i][c] != 0:
                    f = M[i][c]
                    M[i] = [(x - f * y) % q for x, y in zip(M[i], M[rank])]
        rank += 1
    return rank


def binary_representable(fr, m):
    """A matroid is binary exactly when its fundamental-circuit matrix over GF(2) represents it."""
    indep = [Y for Y in fr if fr[Y]]
    r = max((len(Y) for Y in indep), default=0)
    if r == 0:
        return not any(fr.values())
    basis = next(Y for Y in indep if len(Y) == r)
    rows = [[0] * m for _ in range(r)]
    for j, b in enumerate(basis):
        rows[j][b] = 1
    for v in range(m):
        if v in basis:
            continue
        circ = next(C for k in range(1, r + 2) for C in combinations(sorted(set(basis) | {v}), k)
                    if v in C and not fr[C] and all(fr[tuple(u for u in C if u != w)] for w in C))
        for j, b in enumerate(basis):
            rows[j][v] = 1 if b in circ else 0
    return all((rank_mod(rows, list(Y), 2) == len(Y)) == fr[Y] for Y in fr)


def generator_matroid_ok(T, kv_fr, q, to_vec):
    """The free sets of a translated top image equal the independent column sets of its generator matrix over GF(q)."""
    o = T[0]
    H = [to_vec(t, o) for t in T]
    n = len(H[0]) if H else 0
    basis = []
    for h in H:
        if rank_mod(basis + [list(h)], list(range(n)), q) > len(basis):
            basis.append(list(h))
    if not basis:
        return not any(kv_fr.values())
    return all((rank_mod(basis, list(Y), q) == len(Y)) == kv_fr[Y] for Y in kv_fr)


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    tops_rows = {json.loads(l)["law"]: json.loads(l) for l in (TOPS_CENSUS / "raw_rows.jsonl").read_text().splitlines()}
    image_rows = {json.loads(l)["law"]: json.loads(l) for l in (IMAGES_CENSUS / "raw_rows.jsonl").read_text().splitlines()}
    laws = cycle_tops_laws()
    for name, law in laws.items():
        law["tops"], law["names"] = tops_rows[name]["tops"], [""]
    for name in ("Z4", "Z2xZ2", "Z2xZ4"):
        row = image_rows[f"3-net {name}"]
        law = net(row["square"])
        law["tops"], law["names"] = row["tops"], ["0:", "1:", "2:"]
        laws[f"3-net {name}"] = law
    gf = gf4_law()
    # certify GF(4)'s top: every proper equivalence coarser than equality is broken by a polymorphism
    polys = [lambda x, y, z: x ^ y ^ z] + [lambda x, y, z, l=l: gf4_mul(l, x) for l in (2, 3)]
    R = set(gf["rels"][0][1])
    poly_ok = all(tuple(p(a[i], b[i], c[i]) for i in range(3)) in R for p in polys for a in R for b in R for c in R)

    def parts(items):
        if not items:
            yield []
            return
        for p in parts(items[1:]):
            for i in range(len(p)):
                yield p[:i] + [[items[0]] + p[i]] + p[i + 1:]
            yield [[items[0]]] + p
    broken = []
    for p in parts([0, 1, 2, 3]):
        if 1 < len(p) < 4:
            cls = {x: i for i, b in enumerate(p) for x in b}
            pairs = [(x, y) for b in p for x in b for y in b]
            broken.append(any(cls[f(a[0], b[0], c[0])] != cls[f(a[1], b[1], c[1])]
                              for f in polys for a in pairs for b in pairs for c in pairs))
    gf["tops"], gf["names"] = {"0,1,2,3": [[0], [1], [2], [3]], "0": [[0]]}, [""]
    laws["GF(4)"] = gf
    checks["gf4_top_certificate"] = {"polymorphisms_preserve": poly_ok, "coarser_equivalences": len(broken), "all_broken": all(broken)}
    if not (poly_ok and all(broken)):
        failures.append("GF(4) top certificate")

    rng = random.Random("affine-tops-B")
    thm1, cor2, thm3 = {}, {}, {}
    ops_by_law = {}
    for name, law in laws.items():
        ops = {}
        st = {"systems": 0, "knot_variables": 0, "functional": 0, "maltsev": 0, "consistent": 0, "closed_top_images": 0}
        c2 = {"ternary_circuits": 0, "addition_tables": 0}
        t3 = {"systems": 0, "components_ok": 0, "matroid_checked": 0, "matroid_ok": 0, "u24": 0}
        samples, tries = [], 0
        while st["systems"] < 80 and tries < 3000:
            tries += 1
            sorts, cons = random_system(rng, law, 6)
            S = solve(law, sorts, cons)
            if not S:
                continue
            keep = [v for v in range(len(sorts)) if rng.random() < 0.75] or [0]
            S = {tuple(s[v] for v in keep) for s in S}
            m = len(keep)
            rgs = [sorted({s[v] for s in S}) for v in range(m)]
            keys = [range_key(law["names"][sorts[keep[v]]], rgs[v]) for v in range(m)]
            if any(len(rgs[v]) > 1 and keys[v] not in law["tops"] for v in range(m)):
                continue
            maps = [{rgs[v][0]: 0} if len(rgs[v]) == 1 else {x: i for i, b in enumerate(law["tops"][keys[v]]) for x in b}
                    for v in range(m)]
            Sb = {tuple(maps[v][t[v]] for v in range(m)) for t in S}
            sizes = [len(set(mp.values())) for mp in maps]
            fr = free_map(Sb, m, sizes)
            cs = circuits(fr)
            st["systems"] += 1
            knot_vars = set()
            for C in cs:
                if len(C) < 3:
                    continue
                Kb = {tuple(t[v] for v in C) for t in Sb}
                k = len(C)
                if k == 3:
                    c2["ternary_circuits"] += 1
                for e in range(k):
                    knot_vars.add(C[e])
                    P = parallelogram(Kb, k, e, (e + 1) % k)
                    n = sizes[C[e]]
                    st["knot_variables"] += 1
                    func = len(P) == n ** 3 and all(len(v) == 1 for v in P.values())
                    st["functional"] += func
                    if not func:
                        continue
                    op = {key: next(iter(v)) for key, v in P.items()}
                    st["maltsev"] += all(op[(x, y, y)] == x and op[(x, x, y)] == y for x in range(n) for y in range(n))
                    ops.setdefault(keys[C[e]], op)
                    st["consistent"] += ops[keys[C[e]]] == op
            samples.append((Sb, m, keys, fr, cs, sizes))
        # closure of top images under the operations, and Corollary 2
        for Sb, m, keys, fr, cs, sizes in samples:
            kv = [v for v in range(m) if keys[v] in ops]
            if kv:
                T = {tuple(t[v] for v in kv) for t in Sb}
                tl = sorted(T)
                pick = tl if len(tl) <= 30 else [tl[rng.randrange(len(tl))] for _ in range(30)]
                st["closed_top_images"] += all(tuple(ops[keys[kv[j]]][(a[j], b[j], c[j])] for j in range(len(kv))) in T
                                               for a in pick for b in pick for c in pick)
            for C in cs:
                if len(C) == 3 and all(keys[v] in ops for v in C):
                    Kb = {tuple(t[v] for v in C) for t in Sb}
                    o = next(iter(Kb))
                    add = [lambda x, y, kk=keys[v]: ops[kk][(x, 0, y)] for v in C]
                    neg = [lambda y, kk=keys[v]: ops[kk][(0, y, 0)] for v in C]
                    # translate to a subgroup, then read the homomorphism (x, y) -> z
                    H = {tuple(add[j](t[j], neg[j](o[j])) for j in range(3)) for t in Kb}
                    hom = {(x, y): z for x, y, z in H}
                    n0, n1 = sizes[C[0]], sizes[C[1]]
                    phi = [hom.get((x, 0)) for x in range(n0)]
                    psi = [hom.get((0, y)) for y in range(n1)]
                    ok = len(hom) == len(H) == n0 * n1 and None not in phi and None not in psi \
                        and len(set(phi)) == n0 and len(set(psi)) == n1 \
                        and all(hom[(x, y)] == add[2](phi[x], psi[y]) for x in range(n0) for y in range(n1))
                    c2["addition_tables"] += ok
        groups = {k: group_facts(op, max(x for key in op for x in key) + 1) for k, op in ops.items()}
        st["groups"] = groups
        thm1[name], cor2[name] = st, c2
        ops_by_law[name] = (ops, samples)
        # Theorem 3
        primes = {k: g["element_orders"][-1] for k, g in groups.items()}
        for Sb, m, keys, fr, cs, sizes in samples:
            t3["systems"] += 1
            comps = components(m, [C for C in cs])
            comp_ok = True
            for comp in comps:
                r = rank_of(fr, comp)
                if r >= 2 and not all(keys[v] in ops for v in comp):
                    comp_ok = False
            t3["components_ok"] += comp_ok
            if name == "3-net Z2xZ2":
                t3["matroid_checked"] += 1
                t3["matroid_ok"] += binary_representable(fr, m)
            elif name == "GF(4)":
                kv = [v for v in range(m) if sizes[v] > 1]
                if kv:
                    T = sorted({tuple(t[v] for v in kv) for t in Sb})
                    kv_fr = {Y: fr[tuple(kv[i] for i in Y)] for k in range(1, len(kv) + 1) for Y in combinations(range(len(kv)), k)}
                    vec = lambda t, o: tuple(a ^ b for a, b in zip(t, o))
                    t3["matroid_checked"] += 1
                    t3["matroid_ok"] += generator_matroid_ok(T, kv_fr, 4, vec)
                t3["binary_too"] = t3.get("binary_too", 0) + binary_representable(fr, m)
                if m >= 4:
                    for Y in combinations(range(m), 4):
                        sub = {Z: fr[tuple(Y[i] for i in Z)] for k in range(1, 5) for Z in combinations(range(4), k)}
                        if all(sub[Z] == (len(Z) <= 2) for Z in sub):
                            t3["u24"] += 1
                            break
            else:
                kv = [v for v in range(m) if keys[v] in ops and primes.get(keys[v], 0) > 1 and sizes[v] == primes[keys[v]]]
                if not kv:
                    continue
                p = primes[keys[kv[0]]]
                if any(primes[keys[v]] != p for v in kv):
                    continue
                # generator matrix of the translated top image, coordinates identified with Z_p through a generator
                T = sorted({tuple(t[v] for v in kv) for t in Sb})
                o = T[0]
                coord = []
                for v in kv:
                    op = ops[keys[v]]
                    gen = next(x for x in range(sizes[v]) if x != 0)
                    mult, s = {0: 0}, 0
                    for k in range(1, p):
                        s = op[(s, 0, gen)] if k > 1 else gen
                        mult[s] = k
                    coord.append((op, mult))
                H = [tuple(coord[j][1][coord[j][0][(t[j], o[j], 0)]] for j in range(len(kv))) for t in T]
                basis = []
                for h in H:
                    if rank_mod(basis + [list(h)], list(range(len(kv))), p) > len(basis):
                        basis.append(list(h))
                sub_fr = {Y: fr[tuple(sorted(kv[i] for i in Y))] for k in range(1, len(kv) + 1) for Y in combinations(range(len(kv)), k)}
                t3["matroid_checked"] += 1
                t3["matroid_ok"] += all((rank_mod(basis, list(Y), p) == len(Y)) == sub_fr[Y] for Y in sub_fr) if basis else \
                    not any(sub_fr.values())
        thm3[name] = t3

    # Theorem 1(a),(b): polymorphisms of the small laws
    poly = {}
    for name in ("parity + J", "K4 + Z3", "L-{222}", "L-{}", "parity", "Z3"):
        law, row = laws[name], tops_rows[name]
        ops = ops_by_law[name][0]
        D = law["sorts"][0]
        found, agree, commute = 0, 0, 0
        for trial in range(4):
            S = Solver(D, law["rels"], 3)
            for B in row["knot_ranges"]:
                cls = {x: i for i, b in enumerate(law["tops"][range_key("", B)]) for x in b}
                for a, b in product(B, repeat=2):
                    S.restrict((a, b, b), [x for x in B if cls[x] == cls[a]])
                    S.restrict((a, a, b), [x for x in B if cls[x] == cls[b]])
            F = S.solve(random.Random(f"{name}-{trial}"))
            if F is None:
                continue
            found += 1
            ok = True
            for B in row["knot_ranges"]:
                key = range_key("", B)
                if key not in ops:
                    continue
                blocks = law["tops"][key]
                cls = {x: i for i, b in enumerate(blocks) for x in b}
                ok = ok and all(cls[F[(blocks[a][0], blocks[b][0], blocks[c][0])]] == ops[key][(a, b, c)]
                                for a, b, c in product(range(len(blocks)), repeat=3))
            agree += ok
        # random binary polymorphisms commute with the operation on each knot top
        for trial in range(4):
            Gp = Solver(D, law["rels"], 2).solve(random.Random(f"{name}-g-{trial}"))
            if Gp is None:
                continue
            ok = True
            for key, op in ops.items():
                blocks = law["tops"][key]
                cls = {x: i for i, b in enumerate(blocks) for x in b}
                Bset = {x for b in blocks for x in b}
                if not all(Gp[(x, y)] in Bset for x in Bset for y in Bset):
                    ok = False
                    continue
                g = {(a, b): cls[Gp[(blocks[a][0], blocks[b][0])]] for a in range(len(blocks)) for b in range(len(blocks))}
                n = len(blocks)
                ok = ok and all(g[(op[(a1, b1, c1)], op[(a2, b2, c2)])] == op[(g[(a1, a2)], g[(b1, b2)], g[(c1, c2)])]
                                for a1, b1, c1, a2, b2, c2 in product(range(n), repeat=6))
            commute += ok
        poly[name] = {"maltsev_polymorphisms_found": found, "induce_the_parallelogram_operation": agree,
                      "binary_polymorphisms_commuting": commute}
    checks["theorem_1"] = thm1
    checks["theorem_1_polymorphisms"] = poly
    checks["corollary_2"] = cor2
    checks["theorem_3"] = thm3

    ok1 = all(s["systems"] == 80 and s["knot_variables"] == s["functional"] == s["maltsev"] == s["consistent"]
              and s["closed_top_images"] == sum(1 for smp in ops_by_law[n][1] if any(k in ops_by_law[n][0] for k in smp[2]))
              and all(g["medial"] and g["abelian_group"] and g["x_minus_y_plus_z"] and g["elementary"] for g in s["groups"].values())
              for n, s in thm1.items())
    ok1 = ok1 and all(v["maltsev_polymorphisms_found"] == v["induce_the_parallelogram_operation"] == 4
                      and v["binary_polymorphisms_commuting"] == 4 for v in poly.values())
    if not ok1:
        failures.append("Theorem 1")
    if not all(c["ternary_circuits"] >= c["addition_tables"] and c["addition_tables"] == sum(
            1 for smp in ops_by_law[n][1] for C in smp[4] if len(C) == 3 and all(smp[2][v] in ops_by_law[n][0] for v in C))
               for n, c in cor2.items()):
        failures.append("Corollary 2")
    if not all(t["components_ok"] == t["systems"] and t["matroid_ok"] == t["matroid_checked"] for t in thm3.values()):
        failures.append("Theorem 3")

    # the explicit U(2,4) system of the GF(4) law: x + w y = z and x + w z = u
    S = solve(laws["GF(4)"], [0, 0, 0, 0], [(0, (0, 1, 2)), (0, (0, 2, 3))])
    fr = free_map(S, 4, [len({s[v] for s in S}) for v in range(4)])
    explicit = {"uniform_2_4": all(fr[Z] == (len(Z) <= 2) for Z in fr),
                "gf4_generator_matrix": generator_matroid_ok(sorted(S), fr, 4, lambda t, o: tuple(a ^ b for a, b in zip(t, o))),
                "binary": binary_representable(fr, 4)}
    checks["theorem_3_explicit_u24"] = explicit
    if not (explicit["uniform_2_4"] and explicit["gf4_generator_matrix"] and not explicit["binary"]):
        failures.append("Theorem 3 explicit U(2,4)")

    # controls
    Q8 = image_rows["3-net Q8"]["square"]
    T = {(x1, x2, x3) for x1, x2, x3 in product(range(8), repeat=3)
         if any(Q8[x1][y2] == Q8[x2][y1] and Q8[x1][y3] == Q8[x3][y1] and Q8[x2][y3] == Q8[x3][y2]
                for y1, y2, y3 in product(range(8), repeat=3))}
    Tb = {tuple(x & 3 for x in t) for t in T}
    closed = all(tuple(a[j] ^ b[j] ^ c[j] for j in range(3)) in Tb for a in Tb for b in Tb for c in Tb)
    controls["every_top_image_closed_under_the_operation"] = {"q8_thomsen_closed": closed, "rejected": not closed}
    controls["only_binary_matroids"] = {"u24_systems_in_gf4_law": thm3["GF(4)"]["u24"], "explicit_u24_binary": explicit["binary"],
                                        "rejected": explicit["uniform_2_4"] and not explicit["binary"]}
    z22 = thm3["3-net Z2xZ2"]
    controls["field_fixed_by_top_size"] = {
        "z2xz2_top_size": 4, "gf4_top_size": 4, "z2xz2_binary_checked": z22["matroid_checked"], "z2xz2_binary": z22["matroid_ok"],
        "gf4_u24": thm3["GF(4)"]["u24"],
        "rejected": z22["matroid_ok"] == z22["matroid_checked"] > 0 and explicit["uniform_2_4"] and not explicit["binary"]}
    K4 = set(LIFT) - {(2, 2, 2)}
    fib = {}
    for t in K4:
        fib.setdefault((t[0],), set()).add(t[1:])
    vals = list(fib.values())
    not_rect = any(a & b and a != b for a in vals for b in vals)
    controls["closed_below_the_tops"] = {"k4_rectangular_at_first_variable": not not_rect, "rejected": not_rect}
    for k, v in controls.items():
        if not v["rejected"]:
            failures.append(f"control not rejected: {k}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
