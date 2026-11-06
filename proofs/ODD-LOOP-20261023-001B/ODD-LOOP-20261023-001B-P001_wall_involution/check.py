#!/usr/bin/env python3
"""Check of ODD-LOOP-20261023-001B-P001: the wall involution and the odd-loop identity.

Standard library only. Tori have periods w1 = (Lh, 0) and w2 = (s, Lv). For a sector q (a nonzero twist) and a primitive class c
with q(c) odd, L_q(c) is the set of orientations whose sector-q strong components wind in class c and nothing else. The other
sector odd on c is q' = q + chi_c with chi_c = (c2, c1) mod 2. The wall involution Phi:
- takes the strong component S* that is invariant under the sheet swap and whose projection contains the smallest vertex;
- builds the wall gamma: the edges joining the lift K of that projection to the part of the c-cover above K;
- flips the twist on gamma and the bit of every wall edge whose end outside the projection is its head;
- returns to the standard twist by the gauge transformation of the set R with delta R = gamma + (standard cocycle of chi_c).

The check verifies, for every orientation examined:
- the wall lemma: the moved digraph has exactly the same arcs on directed cycles;
- that Phi maps L_q(c) into L_q'(c);
- that Phi applied from sector q' returns the orientation.
It examines every orientation of the 3 x 3 torus at shears 0 and 1, and random walks inside nine line events on larger and sheared
tori (classes (1, 0), (0, 1), (1, -1), (1, 1)). On 3 x 3 the line counts are compared with TWIST-RELATIONS-20261022-001A-P001.

Controls, each of which must be rejected at least once:
- the straight-band rule (move the seam to the smallest top of an inert straight band) is not an involution on a stored 4 x 4
  orientation, on which the wall involution works;
- moving the twist along the wall without the bit flips changes the cyclic arcs;
- keeping the orientation and changing only the sector (moving nothing) leaves the line event.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXACT = ROOT / "proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/result.json"
SECTORS = ((1, 0), (0, 1), (1, 1))
WALKS = [  # (Lh, Lv, s, sector, class, steps)
    (4, 4, 1, (1, 0), (1, 0), 2500),
    (5, 4, 2, (0, 1), (0, 1), 2500),
    (6, 5, 0, (1, 0), (1, 0), 2500),
    (6, 5, 2, (1, 1), (1, 0), 2500),
    (7, 7, 3, (0, 1), (0, 1), 2000),
    (8, 6, 1, (1, 0), (1, -1), 2000),
    (5, 7, 2, (0, 1), (1, -1), 2000),
    (9, 4, 4, (1, 0), (1, 0), 2000),
    (6, 5, -3, (1, 0), (1, 1), 2000),
]
STRAIGHT_COUNTEREXAMPLE = ((4, 4, 0), (1, 0), (1, 0),
                           [0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])


class Torus:
    def __init__(self, Lh, Lv, s):
        self.Lh, self.Lv, self.s, self.V = Lh, Lv, s, Lh * Lv
        self.edges = []
        for u in range(self.V):
            x, y = u % Lh, u // Lh
            self.edges.append((u, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
            if y + 1 < Lv:
                self.edges.append((u, u + Lh, (0, 0)))
            else:
                X = x - s
                a = X // Lh
                self.edges.append((u, X - a * Lh, (a, 1)))


def cocycle(T, q):
    return [(a * q[0] + b * q[1]) & 1 for (_u, _w, (a, b)) in T.edges]


def arcs(T, x, t):
    """Twisted double cover, node 2v + sheet: x_e = 1 gives (u,0) -> (w,t) and (w,1-t) -> (u,1), x_e = 0 the reverses."""
    out = [[] for _ in range(2 * T.V)]
    for (u, w, _o), bit, te in zip(T.edges, x, t):
        if bit:
            out[2 * u].append(2 * w + te)
            out[2 * w + (1 ^ te)].append(2 * u + 1)
        else:
            out[2 * w + te].append(2 * u)
            out[2 * u + 1].append(2 * w + (1 ^ te))
    return out


def components(out):
    """Strong components (Kosaraju), labelled by their smallest node."""
    n = len(out)
    rev = [[] for _ in range(n)]
    for i in range(n):
        for j in out[i]:
            rev[j].append(i)
    seen, order = [False] * n, []
    for r in range(n):
        if seen[r]:
            continue
        seen[r] = True
        stack = [(r, 0)]
        while stack:
            v, i = stack.pop()
            if i < len(out[v]):
                stack.append((v, i + 1))
                w = out[v][i]
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                order.append(v)
    comp = [-1] * n
    for r in reversed(order):
        if comp[r] >= 0:
            continue
        comp[r], stack, members = r, [r], [r]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if comp[w] < 0:
                    comp[w] = r
                    stack.append(w)
                    members.append(w)
        low = min(members)
        for v in members:
            comp[v] = low
    return comp


def cyclic_arcs(out, comp):
    return {(i, j) for i in range(len(out)) for j in out[i] if comp[i] == comp[j]}


def norm(c):
    a, b = c
    return (a, b) if a > 0 or (a == 0 and b > 0) else (-a, -b)


def line_class(T, t, comp):
    """(kind, class) of the projected cyclic edges: 0 contractible, 1 cross, 2 winding in one primitive class."""
    parent, pos, gens = list(range(T.V)), [(0, 0)] * T.V, {}

    def find(v):
        dx = dy = 0
        while parent[v] != v:
            dx, dy = dx + pos[v][0], dy + pos[v][1]
            v = parent[v]
        return v, (dx, dy)

    for (u, w, (a, b)), te in zip(T.edges, t):
        if comp[2 * u] != comp[2 * w + te]:
            continue
        (ru, pu), (rw, pw) = find(u), find(w)
        d = (pu[0] + a - pw[0], pu[1] + b - pw[1])
        if ru == rw:
            if d != (0, 0):
                gens.setdefault(ru, []).append(d)
        else:
            parent[rw], pos[rw] = ru, d
            gens.setdefault(ru, []).extend(gens.pop(rw, []))
    kind, cls = 0, None
    for g in gens.values():
        if any(g[i][0] * g[j][1] - g[i][1] * g[j][0] for i in range(len(g)) for j in range(i + 1, len(g))):
            return 1, None
        if g:
            x, y = g[0]
            k = gcd(abs(x), abs(y))
            kind, cls = 2, norm((x // k, y // k))
    return kind, cls


def chi(c):
    return (c[1] & 1, c[0] & 1)


def other(q, c):
    h = chi(c)
    return ((q[0] + h[0]) & 1, (q[1] + h[1]) & 1)


def wall(T, comp, c):
    """The wall above the canonical swap-invariant strong component; returns (gamma, flips, r, P)."""
    V, Lh, Lv, s = T.V, T.Lh, T.Lv, T.s
    inv = {comp[2 * v] for v in range(V) if comp[2 * v] == comp[2 * v + 1]}
    if not inv:
        raise AssertionError("no swap-invariant strong component")
    star = min(inv, key=lambda r: min(v for v in range(V) if comp[2 * v] == r))
    P = {v for v in range(V) if comp[2 * v] == star}
    c1, c2 = c
    beta = [c1 * b - c2 * a for (_u, _w, (a, b)) in T.edges]          # level change in the c-cover
    adj = [[] for _ in range(V)]
    for e, (u, w, _o) in enumerate(T.edges):
        adj[u].append((w, beta[e]))
        adj[w].append((u, -beta[e]))
    # K: the component of the lift of P through the smallest vertex; it must contain one lift of each vertex of P
    v0 = min(P)
    level, stack = {v0: 0}, [v0]
    while stack:
        u = stack.pop()
        for w, bt in adj[u]:
            if w in P:
                if w not in level:
                    level[w] = level[u] + bt
                    stack.append(w)
                elif level[w] != level[u] + bt:
                    raise AssertionError("the projection of S* carries a second class")
    cv = (c1 * Lh + c2 * s, c2 * Lv)
    unit = Lh * Lv                                                    # det(c, d) in the plane, for det(c, d) = 1

    def height(v, j):
        return cv[0] * (v // Lh) - cv[1] * (v % Lh) + j * unit

    K = {(v, level[v]) for v in P}
    hmin = min(height(v, j) for v, j in K)
    hmax = max(height(v, j) for v, j in K)
    top = hmax + max(abs(cv[1]), abs(cv[0]))                          # one lattice step above the highest point of K
    window = set()
    for v in range(V):
        j = -((height(v, 0) - hmin) // unit)
        while height(v, j) <= top:
            if (v, j) not in K:
                window.add((v, j))
            j += 1
    seeds = [z for z in window if height(*z) > hmax]
    if not seeds:
        raise AssertionError("empty window above K")
    up, stack = set(seeds), list(seeds)
    while stack:
        u, j = stack.pop()
        for w, bt in adj[u]:
            z = (w, j + bt)
            if z in window and z not in up:
                up.add(z)
                stack.append(z)
    gamma, flips = set(), set()
    for e, (u, w, _o) in enumerate(T.edges):
        if u in P and w not in P and (w, level[u] + beta[e]) in up:
            gamma.add(e)
            flips.add(e)                                              # the free end is the head: flip twist and bit
        elif w in P and u not in P and (u, level[w] - beta[e]) in up:
            gamma.add(e)                                              # the free end is the tail: flip the twist only
    if not gamma:
        raise AssertionError("empty wall")
    h = chi(c)
    nb = [[] for _ in range(V)]
    for e, (u, w, (a, b)) in enumerate(T.edges):
        f = (e in gamma) ^ ((a * h[0] + b * h[1]) & 1)
        nb[u].append((w, f))
        nb[w].append((u, f))
    r, stack = [None] * V, [0]
    r[0] = 0
    while stack:
        u = stack.pop()
        for w, f in nb[u]:
            if r[w] is None:
                r[w] = r[u] ^ f
                stack.append(w)
            elif r[w] != r[u] ^ f:
                raise AssertionError("the wall is not in the class of chi_c")
    return gamma, flips, r, P


def phi(T, x, comp, c):
    gamma, flips, r, P = wall(T, comp, c)
    return [bit ^ (e in flips) ^ r[T.edges[e][0]] for e, bit in enumerate(x)], gamma, flips


def examine(T, x, q, c, out, comp, stats, controls):
    """x lies in L_q(c) with q(c) odd; out and comp describe its sector-q double cover."""
    t = cocycle(T, q)
    q2 = other(q, c)
    x2, gamma, flips = phi(T, x, comp, c)
    # the wall lemma: same arcs on directed cycles after the move
    t1 = [te ^ (e in gamma) for e, te in enumerate(t)]
    x1 = [bit ^ (e in flips) for e, bit in enumerate(x)]
    out1 = arcs(T, x1, t1)
    same = cyclic_arcs(out1, components(out1)) == cyclic_arcs(out, comp)
    # the image lies in L_q'(c), and Phi from sector q' returns x
    out2 = arcs(T, x2, cocycle(T, q2))
    comp2 = components(out2)
    image = line_class(T, cocycle(T, q2), comp2) == (2, c)
    back = image and phi(T, x2, comp2, c)[0] == x
    stats["examined"] += 1
    stats["lemma holds"] += same
    stats["image in the other line event"] += image
    stats["involution returns"] += bool(back)
    stats["walls with both edge directions"] += len({e % 2 for e in gamma}) == 2
    stats["walls with flipped bits"] += bool(flips)
    stats["walls with twist-only edges"] += len(flips) < len(gamma)
    # controls
    out0 = arcs(T, x, t1)
    controls["twist moved without bit flips changes the cyclic arcs"] += cyclic_arcs(out0, components(out0)) != cyclic_arcs(out, comp)
    outq = arcs(T, x, cocycle(T, q2))
    controls["sector changed without a move leaves the line event"] += line_class(T, cocycle(T, q2), components(outq)) != (2, c)
    return same and image and back


def inert_tops(T, x, q):
    """Tops b of straight bands [a, b) whose double-cover lift splits into a predecessor-closed half and its swap image."""
    out = arcs(T, x, cocycle(T, q))
    preds = [[] for _ in range(2 * T.V)]
    for i in range(2 * T.V):
        for j in out[i]:
            preds[j].append(i)
    tops = set()
    for a in range(T.Lv):
        for b in range(a + 1, T.Lv + 1):
            if b - a == T.Lv:
                continue
            L = {2 * v + k for v in range(T.V) if a <= v // T.Lh < b for k in (0, 1)}
            M, changed = set(L), True
            while changed:
                changed = False
                for z in list(M):
                    if any(y not in M for y in preds[z]):
                        M.discard(z)
                        changed = True
            if not (M & {z ^ 1 for z in M}) and (M | {z ^ 1 for z in M}) == L:
                tops.add(b)
    return tops


def run() -> dict[str, object]:
    checks, failures = {}, []
    controls = {"twist moved without bit flips changes the cyclic arcs": 0,
                "sector changed without a move leaves the line event": 0,
                "straight-band rule not an involution on the stored 4 x 4 orientation": 0}
    exact = json.loads(EXACT.read_text())["checks"]["exhaustive"]
    keys = ("lemma holds", "image in the other line event", "involution returns", "walls with both edge directions",
            "walls with flipped bits", "walls with twist-only edges")

    # every orientation of the 3 x 3 torus at shears 0 and 1
    for s in (0, 1):
        T = Torus(3, 3, s)
        m = len(T.edges)
        stats = {"examined": 0, **{k: 0 for k in keys}}
        counts = {}
        for mask in range(1 << m):
            x = [(mask >> e) & 1 for e in range(m)]
            for q in SECTORS:
                out = arcs(T, x, cocycle(T, q))
                comp = components(out)
                kind, c = line_class(T, cocycle(T, q), comp)
                if kind != 2 or not ((c[0] * q[0] + c[1] * q[1]) & 1):
                    continue
                counts[(q, c)] = counts.get((q, c), 0) + 1
                examine(T, x, q, c, out, comp, stats, controls)
        label = f"3x3 s={s} exhaustive"
        lines = {f"{q[0]}{q[1]}": {f"{c[0]},{c[1]}": n for (qq, c), n in counts.items() if qq == q} for q in SECTORS}
        checks[label] = {**stats, "line counts": lines,
                         "identity": all(counts.get((other(q, c), c), 0) == n for (q, c), n in counts.items())}
        if lines != {k: v for k, v in exact[f"3x3 s={s}"]["odd_lines"].items() if k != "00"}:
            failures.append(f"{label}: line counts differ from TWIST-RELATIONS-20261022-001A-P001")
        if not checks[label]["identity"]:
            failures.append(f"{label}: identity fails")
        if any(stats[k] != stats["examined"] for k in keys[:3]):
            failures.append(f"{label}: wall lemma or involution fails")

    # random walks inside line events on larger and sheared tori
    for (Lh, Lv, s, q, c, steps) in WALKS:
        T = Torus(Lh, Lv, s)
        m, t = len(T.edges), cocycle(T, q)
        rng = random.Random(f"wall-{Lh}x{Lv}-{s}-{q}-{c}")

        def state(x):
            out = arcs(T, x, t)
            comp = components(out)
            return out, comp, line_class(T, t, comp) == (2, c)

        while True:
            x = [rng.getrandbits(1) for _ in range(m)]
            out, comp, inside = state(x)
            if inside:
                break
        stats = {"examined": 0, **{k: 0 for k in keys}}
        seen = set()
        for _ in range(steps):
            e = rng.randrange(m)
            x[e] ^= 1
            out1, comp1, inside = state(x)
            if not inside:
                x[e] ^= 1
                continue
            out, comp = out1, comp1
            key = tuple(x)
            if key in seen:
                continue
            seen.add(key)
            examine(T, x, q, c, out, comp, stats, controls)
        label = f"{Lh}x{Lv} s={s} sector {q[0]}{q[1]} class {c[0]},{c[1]}: walk of {steps} steps"
        checks[label] = stats
        if stats["examined"] == 0 or any(stats[k] != stats["examined"] for k in keys[:3]):
            failures.append(f"{label}: wall lemma or involution fails")

    # control: the straight-band rule on the stored orientation, and the wall involution on the same orientation
    (Lh, Lv, s), q, c, x = STRAIGHT_COUNTEREXAMPLE
    T = Torus(Lh, Lv, s)
    b = min(inert_tops(T, x, q))
    x2 = [bit ^ ((e // 2) // T.Lh < b) for e, bit in enumerate(x)]
    q2 = other(q, c)
    out2 = arcs(T, x2, cocycle(T, q2))
    in_line = line_class(T, cocycle(T, q2), components(out2)) == (2, c)
    controls["straight-band rule not an involution on the stored 4 x 4 orientation"] += in_line and min(inert_tops(T, x2, q2)) != b
    out = arcs(T, x, cocycle(T, q))
    stats = {"examined": 0, **{k: 0 for k in keys}}
    ok = examine(T, x, q, c, out, components(out), stats, {k: 0 for k in controls})
    checks["stored 4x4 orientation"] = {"straight-band top": b, "top after the straight-band move": min(inert_tops(T, x2, q2)),
                                        "wall involution works": ok}
    if not ok:
        failures.append("the wall involution fails on the stored 4 x 4 orientation")
    if not all(v > 0 for v in controls.values()):
        failures.append("a control was not rejected")
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"], "controls": outcome["controls"], "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: the wall involution and the odd-loop identity checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
