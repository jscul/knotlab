#!/usr/bin/env python3
"""Finite checks for LOGIC-AXIS-20261107-001A-P001 (rulers without ends).

Each check states its exact range; the uniform arguments are in proof.md. Each has a control that is
run on a deliberately wrong or opposite input and must be rejected.

    python3 -B check.py          verify against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

from axis_lib import (ParityLaw, all_knots_through, chained, gauge_law, grid_edges,  # noqa: E402
                      ledrappier_triangle, shortest_cycle_through, tseitin_law)
from knotlab.relations import Relation  # noqa: E402

RNG = random.Random(20261107)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def site(v):
    """Site of a variable: grid edges are (direction, lower endpoint); points are their own site."""
    return v[1] if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], tuple) else v


def sup(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def endpoints(edge):
    k, s = edge
    return [s, tuple(x + (1 if i == k else 0) for i, x in enumerate(s))]


def d_graph(e, f):
    return min(sum(abs(a - b) for a, b in zip(p, q)) for p in endpoints(e) for q in endpoints(f))


# ---------------------------------------------------------------------------------------------------
def check_dependencies() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    mismatched, statuses = {}, {}
    for path, digest in manifest["parent_bindings"].items():
        if sha256(ROOT / path) != digest:
            mismatched[path] = "digest"
        statuses[path] = json.loads((ROOT / path).read_text()).get("status")
    ok = not mismatched and all(s in ("Proved", "passed") for s in statuses.values())
    return {"pass": ok, "info": {"mismatched": mismatched, "statuses": statuses}}


def random_far_sets(law: ParityLaw, reach: int, size_a: int, size_b: int):
    variables = law.vars
    while True:
        a = RNG.sample(variables, size_a)
        b = [v for v in RNG.sample(variables, min(len(variables), 4 * size_b + 8))
             if all(sup(site(v), site(w)) > reach for w in a)][:size_b]
        if len(b) == size_b:
            return a, b


def check_splitting() -> dict:
    """(2) Parity laws whose finite moves have diameter <= 1 split at range 1 (boxes are finite, so
    finite moves are everything; the generators are vertex flips or plaquettes)."""
    info, ok = {}, True
    for name, law in (("gauge 8x8", gauge_law((8, 8))), ("tseitin 8x8", tseitin_law((8, 8))),
                      ("tseitin 4x4x4", tseitin_law((4, 4, 4)))):
        trials = 0
        for _ in range(300):
            a, b = random_far_sets(law, 1, RNG.randint(1, 3), RNG.randint(1, 3))
            trials += 1
            if not law.projection_is_product(a, b):
                ok = False
                info[f"{name} failure"] = [a, b]
                break
        info[name] = f"{trials} random pairs of sets more than 1 apart: joint projection = product"
    # control: Ledrappier's patch does not split; its Frobenius corners are correlated at distance 4
    led = ledrappier_triangle(8)
    control = not led.projection_is_product([(0, 0)], [(4, 0), (0, 4)])
    info["control: Ledrappier corners (0,0) | (4,0),(0,4) are not a product"] = control
    return {"pass": ok and control, "info": info}


def check_chaining() -> dict:
    """(1) Every knot of a law splitting at range 1 is 1-chained (exhaustive through one variable)."""
    info, ok = {}, True
    for name, law, u, size in (("gauge 6x6", gauge_law((6, 6)), (0, (2, 2)), 8),
                               ("tseitin 6x6", tseitin_law((6, 6)), (0, (2, 2)), 8)):
        knots = all_knots_through(law, u, size)
        bad = [sorted(k) for k in knots if not chained([site(v) for v in k], 1)]
        info[name] = {"knots through the central edge (size <= %d)" % size: len(knots), "not 1-chained": len(bad)}
        ok = ok and not bad and len(knots) > 0
    led = ledrappier_triangle(8)
    frob = [(0, 0), (4, 0), (0, 4)]
    control = led.is_knot(frob) and not chained(frob, 1)
    info["control: Frobenius triangle {(0,0),(4,0),(0,4)} of Ledrappier is a knot and not 1-chained"] = control
    return {"pass": ok and control, "info": info}


def check_gauge_plane() -> dict:
    """(3) Gauge law on the plane: 2 d + 1 <= bond distance <= 2 d + 7 (d = graph distance of the edges)."""
    info, ok = {}, True
    # cross-validation of the cycle method against the knot search on a 7x7 box
    law = gauge_law((7, 7))
    e = (0, (3, 3))
    disagree = 0
    pairs = 0
    for f in law.vars:
        if f == e or d_graph(e, f) > 2:
            continue
        s = law.smallest_knot(e, f, 2 * d_graph(e, f) + 8)
        pairs += 1
        if s is None or len(s) != shortest_cycle_through((7, 7), e, f):
            disagree += 1
    info["7x7: knot search vs shortest cycle through both edges"] = f"{pairs} pairs, {disagree} disagreements"
    ok = ok and disagree == 0
    # bounds on a 41x41 box (edges far from the boundary)
    shape = (41, 41)
    offsets: dict[int, int] = {}
    violations = 0
    for e in ((0, (20, 20)), (1, (20, 20))):
        for f in grid_edges(shape):
            if f == e or d_graph(e, f) > 14 or RNG.random() > 0.2:
                continue
            delta = shortest_cycle_through(shape, e, f) - 1
            d = d_graph(e, f)
            offsets[delta - 2 * d] = offsets.get(delta - 2 * d, 0) + 1
            if not (2 * d + 1 <= delta <= 2 * d + 7):
                violations += 1
    info["41x41: observed bond distance - 2d"] = dict(sorted(offsets.items()))
    info["41x41: violations of 2d+1 <= delta <= 2d+7"] = violations
    ok = ok and violations == 0 and sum(offsets.values()) > 300
    # control: Ledrappier's Frobenius pair at distance 8 has bond distance 2 < 2*8+1
    led = ledrappier_triangle(8)
    s = led.smallest_knot((0, 0), (8, 0), 3)
    control = s is not None and len(s) - 1 < 2 * 8 + 1
    info["control: Ledrappier (0,0)-(8,0) bond distance 2 violates the lower bound"] = control
    return {"pass": ok and control, "info": info}


def check_tseitin_space() -> dict:
    """(3) Tseitin on Z^3: take the closest endpoints a of e and c of f (graph distance d). Every shortest
    path from a to c avoids the other two endpoints, and its vertex set U has a cut that is a knot through
    e and f with (2*3-2)(d+1)+2 = 4d+6 edges. The lower bound is check 1's splitting with Theorem 1."""
    shape = (7, 7, 7)
    law = tseitin_law(shape)
    edges = set(law.vars)
    inner = sorted(e for e in edges if all(1 <= x <= 4 for x in e[1]))
    violations, tested, exact = 0, 0, 0
    for _ in range(80):
        e, f = RNG.sample(inner, 2)
        pairs = [(sum(abs(x - y) for x, y in zip(p, q)), p, q) for p in endpoints(e) for q in endpoints(f)]
        d, a, c = min(pairs)
        a2 = [x for x in endpoints(e) if x != a][0]
        c2 = [x for x in endpoints(f) if x != c][0]
        if a2 == c or c2 == a:
            continue
        path = _monotone_path(a, c, {a2, c2}, shape)
        tested += 1
        if path is None or len(path) != d + 1:
            violations += 1
            continue
        cut = _cut(path, edges)
        if not (e in cut and f in cut and law.is_knot(sorted(cut)) and len(cut) == 4 * (d + 1) + 2):
            violations += 1
        else:
            exact += 1
    pair = [(2, 2, 2), (4, 4, 4)]
    control = not law.is_knot(sorted(_cut(pair, edges)))
    return {"pass": violations == 0 and tested >= 50 and control,
            "info": {"random interior pairs": tested, "violations": violations,
                     "path cuts that are knots of exactly 4d+6 edges": exact,
                     "control: the cut of two separated vertices is not a knot": control}}


def _monotone_path(a, c, avoid, shape):
    """A shortest lattice path from a to c avoiding the given vertices, or None (breadth-first)."""
    from collections import deque
    prev = {a: None}
    queue = deque([a])
    while queue:
        v = queue.popleft()
        if v == c:
            break
        for k in range(len(v)):
            for step in (1, -1):
                w = tuple(x + (step if i == k else 0) for i, x in enumerate(v))
                if all(0 <= w[i] < shape[i] for i in range(len(w))) and w not in prev and w not in avoid:
                    prev[w] = v
                    queue.append(w)
    if c not in prev:
        return None
    path, v = [], c
    while v is not None:
        path.append(v)
        v = prev[v]
    return path


def _cut(vertices, edges):
    inside = set(vertices)
    return {e for e in edges if (endpoints(e)[0] in inside) != (endpoints(e)[1] in inside)}


def thread_relation(m: int) -> tuple[Relation, list[str]]:
    """Window of the atom thread on Z: w0..wm, L1..Lm, atoms w(t-1) & L(t) -> w(t)."""
    names = [f"w{t}" for t in range(m + 1)] + [f"L{t}" for t in range(1, m + 1)]
    clauses = [f"-w{t - 1} -L{t} w{t}" for t in range(1, m + 1)]
    return Relation.from_cnf(clauses, names), names


def is_knot_rel(rel: Relation, s) -> bool:
    p = rel.project(list(s))
    return len(s) >= 3 and not p.is_full() and not p.is_empty() and all(
        p.project([x for x in s if x != y]).is_full() for y in s)


def check_thread() -> dict:
    """(3) Atom thread: bond distance between witnesses = number of loops between them + 1, and every
    knot through them contains all those loops."""
    from itertools import combinations
    m = 5
    rel, names = thread_relation(m)
    info, ok = {}, True
    for s_, t_ in [(0, 1), (0, 2), (1, 3), (0, 4), (1, 5), (0, 5)]:
        u, v = f"w{s_}", f"w{t_}"
        rest = [x for x in names if x not in (u, v)]
        knots = [tuple((u, v) + c) for r in range(1, len(rest) + 1) for c in combinations(rest, r)
                 if is_knot_rel(rel, (u, v) + c)]
        smallest = min(len(k) for k in knots) - 1
        loops = {f"L{r}" for r in range(s_ + 1, t_ + 1)}
        all_contain = all(loops <= set(k) for k in knots)
        info[f"{u}-{v}"] = {"bond distance": smallest, "loops between": len(loops), "knots": len(knots),
                            "every knot contains the loops between": all_contain}
        ok = ok and smallest == len(loops) + 1 and all_contain
    # control: a chain of two-place ties x0=x1=...=x5 has no knot at all
    tie_names = [f"x{i}" for i in range(6)]
    ties = Relation.from_cnf([f"-x{i} x{i + 1}" for i in range(5)] + [f"x{i} -x{i + 1}" for i in range(5)], tie_names)
    tie_knots = [c for r in range(3, 7) for c in combinations(tie_names, r) if is_knot_rel(ties, c)]
    info["control: equality chain of 6 has knots"] = len(tie_knots)
    return {"pass": ok and not tie_knots, "info": info}


def poly_mul(p: dict, c: dict) -> dict:
    out: dict = {}
    for (a, b), _ in p.items():
        for (x, y), _ in c.items():
            key = (a + x, b + y)
            out[key] = out.get(key, 0) ^ 1
    return {k: 1 for k, v in out.items() if v}


def check_one_bit_per_site() -> dict:
    """(4) One distinction per site: multiplication by a nonzero polynomial is injective on finite
    configurations (no finite moves); exhaustive rank over supports in a 5x5 window."""
    from axis_lib import rank
    ok, tested = True, 0
    window = [(i, j) for i in range(5) for j in range(5)]
    for _ in range(40):
        p = {(i, j): 1 for i in range(3) for j in range(3) if RNG.random() < 0.5}
        if not p:
            continue
        images = []
        for w in window:
            image = poly_mul(p, {w: 1})
            images.append(sum(1 << (a * 20 + b) for (a, b) in image))
        tested += 1
        if rank(images) != len(window):
            ok = False
    # control: the gauge law (two distinctions per site) has a nonzero finite move, a vertex flip
    law = gauge_law((5, 5))
    flip = {(0, (2, 2)): 1, (1, (2, 2)): 1, (0, (1, 2)): 1, (1, (2, 1)): 1}
    control = law.allows(flip)
    return {"pass": ok and tested >= 30 and control,
            "info": {"random nonzero 3x3 checks": tested, "all injective on the 5x5 window": ok,
                     "control: gauge vertex flip is a nonzero finite allowed state": control}}


def product_law(n: int) -> ParityLaw:
    pts = [(i, j) for i in range(n + 1) for j in range(n + 1 - i)]
    s = set(pts)
    variables = [(kind, p) for p in pts for kind in "xyz"]
    checks = [[("x", (i, j)), ("x", (i + 1, j)), ("x", (i, j + 1))] for (i, j) in pts if (i + 1, j) in s and (i, j + 1) in s]
    checks += [[("x", p), ("y", p), ("z", p)] for p in pts]
    return ParityLaw(variables, checks)


def check_product_law() -> dict:
    """(5) Ledrappier on x, z free, y = x + z: the six variables y,z at 0, 2^k e1, 2^k e2 form a knot,
    every variable is flipped by the finite move {y_p, z_p}, and the knot is a long-range shortcut."""
    law = product_law(8)
    info, ok = {}, True
    for k in (1, 2, 3):
        a, b = (2 ** k, 0), (0, 2 ** k)
        six = [("y", (0, 0)), ("z", (0, 0)), ("y", a), ("z", a), ("y", b), ("z", b)]
        knot = law.is_knot(six)
        moves = all(law.allows({("y", p): 1, ("z", p): 1}) for _, p in six)
        s = law.smallest_knot(("y", (0, 0)), ("y", a), 6)
        info[f"k={k}"] = {"six-set is a knot": knot, "each variable flipped by a finite move": moves,
                          "bond distance y(0,0)-y(2^k,0) <= 5": s is not None and len(s) - 1 <= 5}
        ok = ok and knot and moves and s is not None and len(s) - 1 <= 5
    # the identity behind it on the infinite plane: (1+X+Y)^(2^k) = 1 + X^(2^k) + Y^(2^k) over F2
    base = {(0, 0): 1, (1, 0): 1, (0, 1): 1}
    power = {(0, 0): 1}
    identities = []
    for k in range(1, 7):
        power = {(0, 0): 1}
        for _ in range(2 ** k):
            power = poly_mul(base, power)
        identities.append(set(power) == {(0, 0), (2 ** k, 0), (0, 2 ** k)})
    info["(1+X+Y)^(2^k) = 1+X^(2^k)+Y^(2^k) for k=1..6"] = all(identities)
    # control: drop one variable; the five that remain are not a knot
    five = [("y", (0, 0)), ("z", (0, 0)), ("y", (2, 0)), ("z", (2, 0)), ("y", (0, 2))]
    control = not law.is_knot(five)
    info["control: five of the six are not a knot"] = control
    return {"pass": ok and all(identities) and control, "info": info}


def check_conservative() -> dict:
    """(6) Conservative extension: refining parity knots keeps the old knot and its bond distance."""
    old = ["a", "b", "c"]
    checks = [["a", "b", "c"]]
    variables = list(old)
    fresh = 0
    stays = []
    for step in range(6):
        law = ParityLaw(variables, checks)
        # refine the seed knot, or a random knot among the explicit checks
        target = checks[0] if step % 2 == 0 else RNG.choice(checks)
        u, v, w = f"u{fresh}", f"v{fresh}", f"w{fresh}"
        fresh += 1
        x, y, z = target
        variables += [u, v, w]
        checks += [[x, u, v], [y, v, w], [z, w, u]]
        law = ParityLaw(variables, checks)
        stays.append(law.is_knot(old) and len(law.smallest_knot("a", "b", 3)) - 1 == 2
                     and law.rank_of(old) == 2)
    tied = ParityLaw(variables, checks + [["a", "b"]])
    control = not tied.is_knot(old)
    return {"pass": all(stays) and control,
            "info": {"refinements": len(stays), "old knot kept, bond distance a-b stays 2": all(stays),
                     "control: adding the tie a=b destroys the old knot": control}}


def run() -> dict:
    checks = {
        "0 dependency artifacts bound by hash; upstream proofs Proved": check_dependencies(),
        "1 splitting: random far-apart sets in gauge/Tseitin boxes project as products (control: Ledrappier)": check_splitting(),
        "2 chaining: every knot (size <= 8) through a central edge of gauge/Tseitin 6x6 is 1-chained (control: Frobenius triangle)": check_chaining(),
        "3 gauge plane: 2d+1 <= bond distance <= 2d+7, knot search = shortest cycle (control: Ledrappier pair)": check_gauge_plane(),
        "4 Tseitin Z^3 box: the cut of a shortest vertex path is a knot through e and f with 4d+6 edges (control: two separated vertices)": check_tseitin_space(),
        "5 atom thread: bond distance between witnesses = loops between them + 1 (control: equality chain has no knot)": check_thread(),
        "6 one distinction per site: no finite moves (control: gauge vertex flip)": check_one_bit_per_site(),
        "7 product law: natively open six-variable knot is a long-range shortcut (control: five of six)": check_product_law(),
        "8 conservative refinement keeps the old knot (control: a tie destroys it)": check_conservative(),
    }
    failures = [name for name, value in checks.items() if not value["pass"]]
    return {"checks": checks, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
              "claim": manifest["claim"], **outcome}
    print(json.dumps(outcome, indent=1, default=str)[:6000])
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
