#!/usr/bin/env python3
"""Check of HUB-DIMENSION-20261024-001B-P001 (standard library only, seed 20261024).

Labels on edges (0 = vacuum, 1 = tau); the Fibonacci rule allows a triangle with 0, 2 or 3 tau edges. Weights in Turaev-Viro form:
d per tau edge (1 per vacuum edge), t2 and t3 per triangle with two or three tau edges (1 with none), W[c] per admissible tetrahedron
class c (classes whose four faces obey the rule: 0 = no tau, 4 = a star of three tau edges at a vertex, 8 = a four-cycle, 9 = five tau
edges, 10 = all six), and v per vertex. The 2-3 identity: for every labelling of the nine boundary edges with admissible boundary
triangles, theta(equator) W W = sum over the new edge of d^[tau] theta theta theta W W W. The 1-4 identity: W(T) = v * sum over the four
new edges of d^(number of tau) times the six new triangles' and four new tetrahedra's weights.
Checks:
- the distinct identities are generated as exact polynomials (19 of them);
- they contain the four polynomials used in the proof (up to sign);
- on random non-zero rational values of W9, t2, t3, the relations derived from them give d^2 = d + 1 exactly when the fourth holds,
  and W10 = -(W9 t2)^2 always;
- the explicit point d = phi, t2 = 1/phi, t3 = 1, W0 = 1, W4 = phi, W8 = phi, W9 = 1, W10 = -1/phi^2, v = (5 - sqrt 5)/10 satisfies
  every identity exactly (arithmetic in Q(sqrt 5));
- with all weights 1 some identity fails (unweighted counts are not invariant).
Controls: the explicit point with W10 replaced by +1/phi^2 fails; the identities generated without the new edge's weight d reject the
explicit point; a rational perturbation of d leaves a non-zero residual.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
E4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def canon(bits6):
    best = None
    for p in itertools.permutations(range(4)):
        lab = {frozenset(e): b for e, b in zip(E4, bits6)}
        key = tuple(lab[frozenset((p[a], p[b]))] for a, b in E4)
        best = key if best is None or key < best else best
    return best


CLASSES = sorted({canon(b) for b in itertools.product((0, 1), repeat=6)})
CIDX = {c: i for i, c in enumerate(CLASSES)}


def class_faces(c):
    lab = {frozenset(e): b for e, b in zip(E4, c)}
    return [lab[frozenset((a, b))] + lab[frozenset((a, d))] + lab[frozenset((b, d))] for a, b, d in itertools.combinations(range(4), 3)]


ADM = [i for i, c in enumerate(CLASSES) if all(f in (0, 2, 3) for f in class_faces(c))]
VARS = ["d", "t2", "t3", "v"] + [f"W{i}" for i in ADM]
VI = {name: k for k, name in enumerate(VARS)}


# ---------------------------------------------------------------- polynomials: dict monomial (exponent tuple) -> Fraction
def const(c):
    return {(0,) * len(VARS): Fraction(c)} if c else {}


def var(name):
    e = [0] * len(VARS)
    e[VI[name]] = 1
    return {tuple(e): Fraction(1)}


def mul(p, q):
    out = {}
    for a, x in p.items():
        for b, y in q.items():
            m = tuple(i + j for i, j in zip(a, b))
            out[m] = out.get(m, 0) + x * y
    return {m: c for m, c in out.items() if c != 0}


def add(p, q, s=1):
    out = dict(p)
    for m, c in q.items():
        out[m] = out.get(m, 0) + s * c
    return {m: c for m, c in out.items() if c != 0}


def evaluate(p, values, one, zero):
    tot = zero
    for m, c in p.items():
        term = one * c
        for k, e in enumerate(m):
            for _ in range(e):
                term = term * values[VARS[k]]
        tot = tot + term
    return tot


def key(p):
    return tuple(sorted(p.items()))


# ---------------------------------------------------------------- the identities
def tet_class(lab, verts):
    return CIDX[canon(tuple(lab[frozenset((verts[a], verts[b]))] for a, b in E4))]


def tri_w(lab, a, b, c):
    return lab[frozenset((a, b))] + lab[frozenset((a, c))] + lab[frozenset((b, c))]


def theta(w):
    return {0: const(1), 2: var("t2"), 3: var("t3")}.get(w)


def tet_w(c):
    return var(f"W{c}") if c in ADM else None


def identities(with_d=True):
    eqs = {}
    eq = [1, 2, 3]
    bd = [frozenset(e) for e in [(1, 2), (1, 3), (2, 3), ("a", 1), ("a", 2), ("a", 3), ("b", 1), ("b", 2), ("b", 3)]]
    btri = [("a", 1, 2), ("a", 1, 3), ("a", 2, 3), ("b", 1, 2), ("b", 1, 3), ("b", 2, 3)]
    for bits in itertools.product((0, 1), repeat=9):
        lab = dict(zip(bd, bits))
        if any(tri_w(lab, *t) not in (0, 2, 3) for t in btri):
            continue
        L = const(0)
        th, w1, w2 = theta(tri_w(lab, 1, 2, 3)), tet_w(tet_class(lab, ["a", 1, 2, 3])), tet_w(tet_class(lab, ["b", 1, 2, 3]))
        if th is not None and w1 is not None and w2 is not None:
            L = mul(mul(th, w1), w2)
        R = const(0)
        for x in (0, 1):
            lab[frozenset(("a", "b"))] = x
            term = var("d") if (x and with_d) else const(1)
            for v in eq:
                t = theta(tri_w(lab, "a", "b", v))
                term = mul(term, t) if t is not None else {}
            for u, v in ((1, 2), (2, 3), (1, 3)):
                w = tet_w(tet_class(lab, ["a", "b", u, v]))
                term = mul(term, w) if w is not None else {}
            R = add(R, term)
        del lab[frozenset(("a", "b"))]
        e = add(L, R, -1)
        if e:
            eqs[key(e)] = e
    bd4 = [frozenset(e) for e in itertools.combinations([1, 2, 3, 4], 2)]
    for bits in itertools.product((0, 1), repeat=6):
        lab = dict(zip(bd4, bits))
        if any(tri_w(lab, *t) not in (0, 2, 3) for t in itertools.combinations([1, 2, 3, 4], 3)):
            continue
        w = tet_w(tet_class(lab, [1, 2, 3, 4]))
        L = w if w is not None else const(0)
        R = const(0)
        for nb in itertools.product((0, 1), repeat=4):
            for v, x in zip([1, 2, 3, 4], nb):
                lab[frozenset((0, v))] = x
            term = const(1)
            for _ in range(sum(nb)):
                term = mul(term, var("d"))
            for u, v in itertools.combinations([1, 2, 3, 4], 2):
                t = theta(tri_w(lab, 0, u, v))
                term = mul(term, t) if t is not None else {}
            for s in [1, 2, 3, 4]:
                ww = tet_w(tet_class(lab, [0] + [q for q in [1, 2, 3, 4] if q != s]))
                term = mul(term, ww) if ww is not None else {}
            R = add(R, term)
        e = add(L, mul(var("v"), R), -1)
        if e:
            eqs[key(e)] = e
    return list(eqs.values())


def P(*terms):
    """polynomial from (coefficient, {var: exponent}) terms"""
    out = {}
    for c, ex in terms:
        e = [0] * len(VARS)
        for name, k in ex.items():
            e[VI[name]] = k
        out[tuple(e)] = out.get(tuple(e), 0) + Fraction(c)
    return {m: c for m, c in out.items() if c}


# ---------------------------------------------------------------- Q(sqrt 5)
class Q5:
    def __init__(self, a, b=0):
        self.a, self.b = Fraction(a), Fraction(b)

    def __add__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __mul__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a * o.a + 5 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __neg__(self):
        return Q5(-self.a, -self.b)

    def inv(self):
        n = self.a * self.a - 5 * self.b * self.b
        return Q5(self.a / n, -self.b / n)

    def iszero(self):
        return self.a == 0 and self.b == 0

    def __repr__(self):
        return f"{self.a}+{self.b}*sqrt5"


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    eqs = identities()
    keys = {key(e) for e in eqs} | {key({m: -c for m, c in e.items()}) for e in eqs}
    used = {
        "(i)   W4 W9 t2 (W9 d t2 t3 - 1)": P((1, {"W4": 1, "W9": 2, "d": 1, "t2": 2, "t3": 1}), (-1, {"W4": 1, "W9": 1, "t2": 1})),
        "(ii)  W9 t2 (W9^2 d t3^2 - W8)": P((1, {"W9": 3, "d": 1, "t2": 1, "t3": 2}), (-1, {"W8": 1, "W9": 1, "t2": 1})),
        "(iii) W9 (W10 W9 d t3^3 + W8^2 t2^3)": P((1, {"W10": 1, "W9": 2, "d": 1, "t3": 3}), (1, {"W8": 2, "W9": 1, "t2": 3})),
        "(iv)  W8 t2 (W4^2 t2 - W8)": P((1, {"W8": 1, "W4": 2, "t2": 2}), (-1, {"W8": 2, "t2": 1})),
        "(v)   W4^2 - W8^3 t2^3 - W9^3 d t3^3": P((1, {"W4": 2}), (-1, {"W8": 3, "t2": 3}), (-1, {"W9": 3, "d": 1, "t3": 3})),
    }
    present = {name: key(p) in keys for name, p in used.items()}
    # the derivation on random non-zero rationals: (i) d = 1/(W9 t2 t3); (ii) W8 = W9^2 d t3^2; (iii) W10 = -W8^2 t2^3/(W9 d t3^3);
    # (iv) W4^2 = W8/t2; then (v) holds exactly when d^2 = d + 1, and W10 = -(W9 t2)^2 always
    w10_ok, v_iff_ok = True, True
    for _ in range(200):
        W9, t2, t3 = (Fraction(rng.choice([-1, 1]) * rng.randint(1, 9), rng.randint(1, 9)) for _ in range(3))
        d = 1 / (W9 * t2 * t3)
        W8 = W9 ** 2 * d * t3 ** 2
        W10 = -W8 ** 2 * t2 ** 3 / (W9 * d * t3 ** 3)
        W4sq = W8 / t2
        w10_ok &= W10 == -(W9 * t2) ** 2
        v_res = W4sq - W8 ** 3 * t2 ** 3 - W9 ** 3 * d * t3 ** 3
        v_iff_ok &= (v_res == 0) == (d * d == d + 1)
        # (v) as a multiple of (1 + d - d^2): v_res = (W9 t3 / t2^2) (1 - u^2 - u) with u = 1/d
        u = 1 / d
        v_iff_ok &= v_res == (W9 * t3 / t2 ** 2) * (1 - u * u - u)
    phi = Q5(Fraction(1, 2), Fraction(1, 2))
    point = {"d": phi, "t2": phi.inv(), "t3": Q5(1), "v": Q5(Fraction(1, 2), Fraction(-1, 10)), "W0": Q5(1), "W4": phi,
             "W8": phi, "W9": Q5(1), "W10": -(phi * phi).inv()}
    def satisfies(pt, eqset):
        return all(evaluate(e, pt, Q5(1), Q5(0)).iszero() for e in eqset)
    exact = {"distinct identities": len(eqs), "explicit point satisfies all": satisfies(point, eqs),
             "d^2 = d + 1 at the point": (phi * phi + -phi + Q5(-1)).iszero(),
             "W10 at the point": repr(point["W10"]), "W10 = -(W9 t2)^2 at the point":
                 (point["W10"] + point["W9"] * point["W9"] * point["t2"] * point["t2"]).iszero()}
    ones = {name: Fraction(1) for name in VARS}
    unweighted = {"all weights 1 fail some identity": any(evaluate(e, ones, Fraction(1), Fraction(0)) != 0 for e in eqs)}
    flipped = dict(point)
    flipped["W10"] = (phi * phi).inv()
    pert = dict(point)
    pert["d"] = Q5(Fraction(8, 5))
    controls = {
        "the point with a positive all-tau weight fails": not satisfies(flipped, eqs),
        "identities without the new edge's weight reject the point": not satisfies(point, identities(with_d=False)),
        "a rational perturbation of d leaves a residual": not satisfies(pert, eqs),
    }
    ok = (all(present.values()) and w10_ok and v_iff_ok and exact["explicit point satisfies all"] and exact["d^2 = d + 1 at the point"]
          and exact["W10 = -(W9 t2)^2 at the point"] and unweighted["all weights 1 fail some identity"] and all(controls.values()))
    result["checks"] = {"admissible tetrahedron classes": ADM, "identities used in the proof are present": present,
                        "derivation on 200 random non-zero rationals": {"W10 = -(W9 t2)^2": w10_ok,
                                                                        "(v) holds exactly when d^2 = d + 1": v_iff_ok},
                        "exact solution": exact, "unweighted": unweighted}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
