#!/usr/bin/env python3
"""Check of WALLS-WITH-CHOICES-20261024-001A-P001 (standard library only).

Shared machinery (placements, frames, cylinder covers, the solver, wall moves) is imported from the closed proof
DIRECTIONAL-RIGIDITY-20261023-001B-P001.

- Theorem 1, direction (=>), on sampled configurations of the 27 three-place tiling placements with a constant frame, on 3 x 3 and
  3 x 4 in every non-fitting twist, along every odd class among eight: when the own solver finds an assignment on a cyclic cover,
  the check traces the walls of that assignment, picks one whose period meets the cylinder's loop an odd number of times, and
  verifies that its torus projection is a closed walk of valid wall moves with a transverse class and no overlap in Z c + Z e.
- Theorem 1, direction (<=): from that closed walk alone it rebuilds an assignment of the cylinder (constant between the walls'
  translates) and verifies it triangle by triangle on a window; and when the own solver finds a strip with no assignment, it
  verifies that no simple cycle of the wall graph passes the criterion.
- Theorem 2 (directed walls): on the frozen exhaustive rows of DIRECTIONAL-RIGIDITY-20261023-001A-E001, no configuration of the six
  bending placements whose allowed lone places are {0, 2} splits the open first quadrant; on the samples, their first-quadrant odd
  classes contradict exactly when the wall graph has a no cycle.
- Controls: comparing each visit only with the first visit to its triangle misreads a certified configuration of placement 151;
  a certified configuration of placement 151 splits the first quadrant, so Theorem 2 needs directed walls; a wall read with the
  wrong left value fails the move rules.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

sys.setrecursionlimit(20000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "dr_check", ROOT / "proofs/DIRECTIONAL-RIGIDITY-20261023-001B/DIRECTIONAL-RIGIDITY-20261023-001B-P001_rigid_contacts/check.py")
DR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DR)

SEED = 20261024
CLASSES = DR.CLASSES
TWISTS = DR.TWISTS
DIRECTED = (54, 62, 110, 147, 155, 203)
EXAMPLES = DR.SELECTIVE_EXAMPLES + [(151, (0, 1), 210021)]   # the last one exposed the first-visit-only overlap test
NB = ((1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1))


# ------------------------------------------------------------------ wall graph with free and pinned places

def frame_data(R, L, M, q):
    fr, flipped = DR.frame(R)
    U = fr & DR.comp(fr)
    free = {DR.lone(p) for p in range(8) if U >> p & 1} - {None}
    pinned = {DR.lone(p): DR.bit(p, DR.lone(p)) for p in range(8)
              if fr >> p & 1 and not U >> p & 1 and DR.lone(p) is not None}
    qf = (q[0] ^ (L & 1), q[1] ^ (M & 1)) if flipped else q
    return fr, flipped, free, pinned, qf


def torus_coins(x, L, M, flipped):
    return {(typ, i, j): ((x >> (2 * (j * L + i) + typ)) & 1) ^ (((i + j) & 1) if flipped else 0)
            for typ in (0, 1) for i in range(L) for j in range(M)}


def allowed(turn, place, coin, b, free, pinned):
    """A turn is allowed when its lone corner's place is free, or pinned with the coin's value on the turn's side."""
    return place in free or (place in pinned and pinned[place] ^ coin ^ b == turn)


def wall_graph(R, L, M, q, x, moves):
    """State (triangle, entry edge, relative left value b) -> list of (next state, deck shift)."""
    fr, flipped, free, pinned, qf = frame_data(R, L, M, q)
    coin = torus_coins(x, L, M, flipped)
    G = {}
    for s in moves:
        for b in (0, 1):
            G[(s, b)] = [((s2, b ^ ((qf[0] * dk[0] + qf[1] * dk[1]) & 1)), dk)
                         for turn, place, s2, dk in moves[s] if allowed(turn, place, coin[s[:3]], b, free, pinned)]
    return G


def overlaps(path, first_only=False):
    """Differences of positions of two visits to one torus triangle within one traversal (path: [(state, position)])."""
    visits, out = {}, []
    for (st, _b), p in path:
        seen = visits.setdefault(st[:3], [])
        for p0 in (seen[:1] if first_only else seen):
            out.append((p[0] - p0[0], p[1] - p0[1]))
        seen.append(p)
    return out


def good(c, e, ov):
    D = DR.det(c, e)
    return D != 0 and not any(DR.det(d, e) % D == 0 and DR.det(c, d) % D == 0 for d in ov)


def simple_cycles(G, cap=20000):
    """Simple cycles of the wall graph as ([(state, position)], displacement), from the smallest state of each."""
    nodes = sorted(G)
    idx = {v: i for i, v in enumerate(nodes)}
    out = []
    for si, s in enumerate(nodes):
        stack, on, path = [(s, iter(G[s]), (0, 0))], {s}, [(s, (0, 0))]
        while stack:
            v, it, pos = stack[-1]
            moved = False
            for w, dk in it:
                if idx[w] < si:
                    continue
                np_ = (pos[0] + dk[0], pos[1] + dk[1])
                if w == s:
                    out.append((list(path), np_))
                    if len(out) >= cap:
                        return out, True
                elif w not in on:
                    on.add(w)
                    path.append((w, np_))
                    stack.append((w, iter(G[w]), np_))
                    moved = True
                    break
            if not moved:
                stack.pop()
                on.discard(v)
                path.pop()
    return out, False


def has_cycle(G):
    color = {}
    for s0 in G:
        if s0 in color:
            continue
        color[s0] = 1
        stack = [(s0, iter(G[s0]))]
        while stack:
            v, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[v] = 2
                stack.pop()
                continue
            w = nxt[0]
            if color.get(w) == 1:
                return True
            if w not in color:
                color[w] = 1
                stack.append((w, iter(G[w])))
    return False


# ------------------------------------------------------------------ assignments and their walls, lifted to Z^2

def corners(typ, i, j):
    return [(i + a, j + b) for a, b in (DR.UPO if typ == 0 else DR.DNO)]


def edge_points(typ, i, j, k):
    cs, ccw = corners(typ, i, j), DR.CCW[typ]
    return cs[ccw[k]], cs[ccw[(k + 1) % 3]]


def neighbour_across(typ, i, j, k):
    """The triangle across edge k of triangle (typ, i, j), and that edge's number in it."""
    edge = set(edge_points(typ, i, j, k))
    i0, j0 = min(p[0] for p in edge), min(p[1] for p in edge)
    for t2 in (0, 1):
        for i2 in (i0 - 1, i0):
            for j2 in (j0 - 1, j0):
                if (t2, i2, j2) == (typ, i, j):
                    continue
                for k2 in range(3):
                    if set(edge_points(t2, i2, j2, k2)) == edge:
                        return (t2, i2, j2), k2
    raise ValueError("no neighbour")


def triangle_with_edge(p1, p2):
    for typ in (0, 1):
        for i in (min(p1[0], p2[0]) - 1, min(p1[0], p2[0])):
            for j in (min(p1[1], p2[1]) - 1, min(p1[1], p2[1])):
                for k in range(3):
                    if set(edge_points(typ, i, j, k)) == {p1, p2}:
                        return (typ, i, j), k
    raise ValueError("no triangle")


def cover_assignment(R, L, M, q, x, c, max_sheets=12):
    for m in range(1, max_sheets + 1):
        n, cl, nodes = DR.clauses(R, L, M, q, x, c, m, True)
        a = DR.dpll(n, cl)
        if a is not None and DR.satisfies(cl, a):
            return m, a, nodes
    return None


def frame_assignment(R, L, M, q, c, m, a, nodes):
    """The cover's assignment lifted to Z^2 (Lemma A of the predecessor) and put in the constant frame."""
    _, flipped, _, _, _ = frame_data(R, L, M, q)

    def F(p):
        d = DR.deck(p, L, M)
        t = c[0] * d[1] - c[1] * d[0]
        v = a[nodes[(DR.vid(p, L, M), t % m)]] ^ ((q[0] * d[0] + q[1] * d[1]) & 1)
        return v ^ (((p[0] + p[1]) & 1) if flipped else 0)
    return F


def trace(F, tri, k, L, M, closes, limit=50000):
    """Follow the wall that enters triangle tri through edge k until it returns to a translate (accepted by closes) of the
    start with the same entry edge. Returns ([(triangle in Z^2, entry edge)], period in classes), period (0, 0) for a loop."""
    start = (tri, k)
    seq = []
    for _ in range(limit):
        typ, i, j = tri
        cut = [kk for kk in range(3) if F(edge_points(typ, i, j, kk)[0]) != F(edge_points(typ, i, j, kk)[1])]
        if len(cut) != 2 or k not in cut:
            raise ValueError("not a wall")
        seq.append((tri, k))
        exit_k = cut[0] if cut[1] == k else cut[1]
        tri, k = neighbour_across(typ, i, j, exit_k)
        dv = (tri[1] - start[0][1], tri[2] - start[0][2])
        if tri[0] == start[0][0] and k == start[1] and dv[0] % L == 0 and dv[1] % M == 0:
            hc = (dv[0] // L, dv[1] // M)
            if hc == (0, 0) or closes(hc):
                return seq, hc
    raise ValueError("wall did not close")


def crossing_wall(R, L, M, q, x, c, m, a, nodes):
    """A wall of the cover assignment whose period meets the loop of class c an odd number of times."""
    F = frame_assignment(R, L, M, q, c, m, a, nodes)
    w = (c[0] * L, c[1] * M)
    closes = lambda hc: DR.det(c, hc) % m == 0
    p, path = (0, 0), []
    for axis, n in ((0, w[0]), (1, w[1])):
        step = 1 if n > 0 else -1
        for _ in range(abs(n)):
            p2 = (p[0] + step, p[1]) if axis == 0 else (p[0], p[1] + step)
            path.append((p, p2))
            p = p2
    for p1, p2 in path:
        if F(p1) == F(p2):
            continue
        tri, k = triangle_with_edge(p1, p2)
        seq, hc = trace(F, tri, k, L, M, closes)
        if hc != (0, 0) and (DR.det(c, hc) // m) % 2:
            return seq, hc, F
    return None


def closed_walk(seq, hc, R, L, M, q, x, F, moves, wrong_side=False):
    """The traced wall as states of the torus wall graph. Checks every move against the rules and the left value's constancy;
    returns (moves valid, minimal closed walk [(state, position)], its displacement in classes)."""
    _, flipped, free, pinned, qf = frame_data(R, L, M, q)
    coin = torus_coins(x, L, M, flipped)
    states = []
    for (typ, i, j), k in seq:
        left = edge_points(typ, i, j, k)[1 if wrong_side else 0]   # walking in through edge k, the left end is its start
        d = (i // L, j // M)
        b = F(left) ^ ((qf[0] * d[0] + qf[1] * d[1]) & 1)
        states.append((((typ, i % L, j % M, k), b), d))
    ok = True
    n = len(states)
    for idx in range(n):
        (s, b), _d = states[idx]
        (s2, b2), d2 = states[(idx + 1) % n]
        opts = [(turn, place, dk) for turn, place, s3, dk in moves[s] if s3 == s2]
        ok = ok and any(allowed(turn, place, coin[s[:3]], b, free, pinned)
                        and b2 == b ^ ((qf[0] * dk[0] + qf[1] * dk[1]) & 1) for turn, place, dk in opts)
    first = states[0][0]
    P = next((t for t in range(1, n) if states[t][0] == first), n)
    if P < n:
        e = (states[P][1][0] - states[0][1][0], states[P][1][1] - states[0][1][1])
    else:
        e = hc
    return ok, states[:P], e


def rebuild_and_verify(R, L, M, q, x, c, walk, e):
    """From a good closed walk alone, build the cylinder assignment (walls at the translates of its lift by multiples of the
    class vector, constant between them) and verify it triangle by triangle on a window."""
    fr, flipped, free, pinned, qf = frame_data(R, L, M, q)
    coin = torus_coins(x, L, M, flipped)
    w = (c[0] * L, c[1] * M)
    h = (e[0] * L, e[1] * M)
    base = [((s[0], s[1] + d[0] * L, s[2] + d[1] * M), s[3], b) for (s, b), d in walk]
    radius = 2 * (abs(w[0]) + abs(w[1]) + abs(h[0]) + abs(h[1])) + 8
    (typ0, i0, j0), k0, b0 = base[0]
    left0 = edge_points(typ0, i0, j0, k0)[0]
    # every translate W + r h + k w meeting the box around left0 (h moves at least one lattice step, so these ranges suffice)
    K = radius + 2
    B = K * (abs(w[0]) + abs(w[1])) + 3 * radius
    margin = radius + 4
    cut = set()
    for kw in range(-K, K + 1):
        for r_ in range(-B, B + 1):
            ox, oy = r_ * h[0] + kw * w[0], r_ * h[1] + kw * w[1]
            if abs(i0 + ox - left0[0]) > margin + abs(h[0]) + abs(h[1]) or abs(j0 + oy - left0[1]) > margin + abs(h[0]) + abs(h[1]):
                continue
            for (typ, i, j), k, _b in base:
                cut.add(frozenset(edge_points(typ, i + ox, j + oy, k)))
    d0 = (i0 // L, j0 // M)
    F = {left0: b0 ^ ((qf[0] * d0[0] + qf[1] * d0[1]) & 1)}
    queue, consistent = [left0], True
    while queue:
        p = queue.pop()
        for dv in NB:
            p2 = (p[0] + dv[0], p[1] + dv[1])
            if abs(p2[0] - left0[0]) > radius or abs(p2[1] - left0[1]) > radius:
                continue
            v = F[p] ^ (frozenset((p, p2)) in cut)
            if p2 in F:
                consistent = consistent and F[p2] == v
            else:
                F[p2] = v
                queue.append(p2)
    inner = radius // 3
    fails = checked = 0
    for typ in (0, 1):
        for i in range(left0[0] - inner, left0[0] + inner):
            for j in range(left0[1] - inner, left0[1] + inner):
                cs = corners(typ, i, j)
                pat = sum(F[pp] << kk for kk, pp in enumerate(cs))
                xt = coin[(typ, i % L, j % M)] ^ ((qf[0] * (i // L) + qf[1] * (j // M)) & 1)
                rel = DR.comp(fr) if xt else fr
                fails += not rel >> pat & 1
                checked += 1
    qp = all(F[(p[0] + w[0], p[1] + w[1])] == F[p] ^ 1 for p in F
             if abs(p[0] - left0[0]) <= inner and abs(p[1] - left0[1]) <= inner and (p[0] + w[0], p[1] + w[1]) in F)
    return consistent and fails == 0 and checked > 0 and qp


def certify_strip_unsat(R, L, M, q, x, c):
    for periods in (12, 24, 36):
        n, cl, _ = DR.clauses(R, L, M, q, x, c, periods, False)
        if DR.dpll(n, cl) is None:
            return True
    return False


# ------------------------------------------------------------------ checks

def theorem1_checks(rng, placements):
    out = {"configurations": 0, "odd classes certified": 0, "undetermined": 0,
           "with assignments": 0, "crossing wall found": 0, "its moves valid": 0, "its closed walk passes the criterion": 0,
           "assignment rebuilt from the walk alone": 0,
           "contradicting": 0, "no simple cycle passes the criterion (contradicting)": 0, "simple-cycle enumeration capped": 0,
           "Theorem 2: directed first-quadrant odd classes": 0, "Theorem 2: verdict equals cycle existence": 0}
    moves = {(3, 3): DR.wall_moves(3, 3), (3, 4): DR.wall_moves(3, 4)}
    for R in placements:
        for L, M in ((3, 3), (3, 4)):
            fit = DR.fitting(R, L, M)
            configs = [(q, rng.randrange(1 << (2 * L * M))) for q in TWISTS if q not in fit]
            if (L, M) == (3, 3):
                configs += [(q, x) for R2, q, x in EXAMPLES if R2 == R]
            for q, x in configs:
                out["configurations"] += 1
                odd = DR.odd_classes(CLASSES, fit, q)
                G = wall_graph(R, L, M, q, x, moves[(L, M)])
                cycles = None
                cyc_exists = has_cycle(G)
                for c in odd:
                    cov = cover_assignment(R, L, M, q, x, c)
                    if cov is not None:
                        verdict = False
                        out["odd classes certified"] += 1
                        out["with assignments"] += 1
                        found = crossing_wall(R, L, M, q, x, c, *cov)
                        if found is not None:
                            seq, hc, F = found
                            out["crossing wall found"] += 1
                            ok, walk, e = closed_walk(seq, hc, R, L, M, q, x, F, moves[(L, M)])
                            out["its moves valid"] += ok
                            g = ok and good(c, e, overlaps(walk))
                            out["its closed walk passes the criterion"] += g
                            out["assignment rebuilt from the walk alone"] += g and rebuild_and_verify(R, L, M, q, x, c, walk, e)
                    elif certify_strip_unsat(R, L, M, q, x, c):
                        verdict = True
                        out["odd classes certified"] += 1
                        out["contradicting"] += 1
                        if cycles is None:
                            cycles = simple_cycles(G)
                        cyc, capped = cycles
                        out["simple-cycle enumeration capped"] += capped
                        out["no simple cycle passes the criterion (contradicting)"] += not any(
                            good(c, e, overlaps(p)) for p, e in cyc)
                    else:
                        out["undetermined"] += 1
                        continue
                    if R in DIRECTED and c[0] * c[1] > 0:
                        out["Theorem 2: directed first-quadrant odd classes"] += 1
                        out["Theorem 2: verdict equals cycle existence"] += verdict == (not cyc_exists)
    return out


def theorem2_rows(rows):
    total = split = 0
    for r in rows:
        if r["R"] not in DIRECTED:
            continue
        cls = [tuple(c) for c in r["classes"]]
        q1 = [k for k, c in enumerate(cls) if c[0] * c[1] > 0]
        for t in r["twists"].values():
            q1odd = sum(1 << k for k in q1 if t["odd_mask"] >> k & 1)
            if not q1odd:
                continue
            total += t["total"]
            split += sum(n for m, n in t["patterns"].items() if (int(m) & q1odd) not in (0, q1odd))
    return {"configurations and twists with a first-quadrant odd class": total, "split": split}


def controls_checks():
    out = {}
    L = M = 3
    moves = DR.wall_moves(L, M)
    # (1) first-visit-only overlaps misread placement 151, twist 01, configuration 210021 along some class
    R, q, x = 151, (0, 1), 210021
    G = wall_graph(R, L, M, q, x, moves)
    cyc, _ = simple_cycles(G)
    fit = DR.fitting(R, L, M)
    wrong = 0
    for c in DR.odd_classes(CLASSES, fit, q):
        truth = DR.certify(R, L, M, q, x, c)
        pred_first = not any(good(c, e, overlaps(p, first_only=True)) for p, e in cyc)
        pred_all = not any(good(c, e, overlaps(p)) for p, e in cyc)
        wrong += (pred_first != truth) and (pred_all == truth)
    out["classes misread by first-visit-only overlaps, read right with all pairs (must be > 0)"] = wrong
    # (2) a certified configuration of 151 splits the first quadrant
    R, q, x = 151, (0, 1), 110633
    v11, v21 = DR.certify(R, L, M, q, x, (1, 1)), DR.certify(R, L, M, q, x, (2, 1))
    out["placement 151 splits the first quadrant (assignment along (1,1), contradiction along (2,1))"] = (v11 is False and v21 is True)
    # (3) reading the left value from the wrong end of the entry edge breaks the move rules
    R, q, x = 147, (0, 1), 30817
    c = (1, 1)
    cov = cover_assignment(R, L, M, q, x, c)
    seq, hc, F = crossing_wall(R, L, M, q, x, c, *cov)
    ok_right, _, _ = closed_walk(seq, hc, R, L, M, q, x, F, moves)
    ok_wrong, _, _ = closed_walk(seq, hc, R, L, M, q, x, F, moves, wrong_side=True)
    out["a traced wall is valid with its left value and invalid with the right one"] = ok_right and not ok_wrong
    return out


def main() -> int:
    rng = random.Random(SEED)
    census = [json.loads(l) for l in DR.CENSUS.read_text().splitlines() if l.strip()]
    three = sorted(r["R"] for r in census if r["kind"] == "three" and r["class"] == "TILING")
    framed = [R for R in three if DR.frame(R) is not None]
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    checks = {"placements with a constant frame": framed}
    checks["Theorem 1 and Theorem 2 on samples"] = t1 = theorem1_checks(rng, framed)
    print("theorems on samples", flush=True)
    rows = [json.loads(l) for l in DR.A_ROWS.read_text().splitlines() if l.strip()]
    checks["Theorem 2 on the frozen exhaustive rows"] = t2 = theorem2_rows(rows)
    controls = controls_checks()
    print("controls", flush=True)
    ok = (len(framed) == 27 and t1["undetermined"] == 0 and t1["with assignments"] > 0 and t1["contradicting"] > 0
          and t1["crossing wall found"] == t1["its moves valid"] == t1["its closed walk passes the criterion"]
          == t1["assignment rebuilt from the walk alone"] == t1["with assignments"]
          and t1["no simple cycle passes the criterion (contradicting)"] == t1["contradicting"]
          and t1["Theorem 2: verdict equals cycle existence"] == t1["Theorem 2: directed first-quadrant odd classes"] > 0
          and t2["split"] == 0 and t2["configurations and twists with a first-quadrant odd class"] > 0
          and controls["classes misread by first-visit-only overlaps, read right with all pairs (must be > 0)"] > 0
          and all(v for k, v in controls.items() if not k.endswith("(must be > 0)")))
    result["checks"], result["controls"] = checks, controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": checks, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
