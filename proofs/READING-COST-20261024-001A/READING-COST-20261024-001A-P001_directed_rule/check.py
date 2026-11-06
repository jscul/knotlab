#!/usr/bin/env python3
"""Check of READING-COST-20261024-001A-P001 (standard library only, seed 20261024).

Uses the wall graph, cover machinery and own solver of WALLS-WITH-CHOICES-20261024-001A-P001's check.

For the six directed contacts (allowed places {0, 2}: 54, 62, 110, 147, 155, 203):
- Lemma 1: in random configurations of every non-fitting twist on 3 x 3, 3 x 4, 4 x 4, 4 x 5 and 5 x 5, an up-triangle state leads only
  to the down triangle of its square, and a down-triangle state only to the square above or to the left; so walls move up or left and
  each move is allowed by itself.
- Lemmas 4 and 5, Theorem 6: crossing walls of cover assignments with 1 to 7 sheets are shortened by the ordered maximum and the split
  until they are simple on the type-preserving cover; every intermediate wall is checked to be valid, good in the same case and,
  after the maximum, comparable with its translates.
- Theorem 7: the decider (cycle test for classes with c1 c2 > 0; arc consistency on the max-closed problem of each candidate period
  otherwise) is compared with ground truth: simple cycles of the wall graph on 3 x 3 and 3 x 4 (equal to the frozen record there for
  these contacts, ticket WALLS-WITH-CHOICES-20261024-001B), and the own solver on covers and strips on 4 x 4 and 4 x 5.
Controls: dropping the window constraint accepts a contradicting class; taking the other piece of a split loses goodness; reading
the type-preserving lattice with the placement's twist instead of the frame's leaves repeated squares.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from collections import Counter, deque
from math import gcd
from pathlib import Path

sys.setrecursionlimit(20000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "wall_check", ROOT / "proofs/WALLS-WITH-CHOICES-20261024-001A/WALLS-WITH-CHOICES-20261024-001A-P001_wall_theorem/check.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
DR = A.DR

DIRECTED = (54, 62, 110, 147, 155, 203)
WITH_CHOICES = (62, 110, 155, 203)
UP, LEFT = (0, 1), (-1, 0)          # square moves in (i, j)
CLASSES = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1), (1, 3), (3, 1), (1, -3), (3, -1)]


# ------------------------------------------------------------------ Lemma 1: walls move up or left, one move at a time

def square_graph(R, L, M, q, x, moves):
    """{(i, j, b): {direction: (i2, j2, b2)}} for walls oriented up or left. Raises if the directed structure fails."""
    G = A.wall_graph(R, L, M, q, x, moves)
    out = {}
    for i in range(L):
        for j in range(M):
            for b in (0, 1):
                for k in (0, 1):   # entry through the bottom (0) or the right edge (1) of the up triangle
                    for (s2, b2), dk in G[((0, i, j, k), b)]:
                        if not (s2 == (1, i, j, 0) and b2 == b and dk == (0, 0)):
                            raise AssertionError(f"up state {(i, j, k, b)} of {R} leaves through {s2}")
                for (s2, b2), dk in G[((0, i, j, 2), b)]:
                    if s2[0] != 1 or s2[3] == 0:
                        raise AssertionError(f"reversed up state {(i, j, b)} of {R} goes to {s2}")
                opts = {}
                for (s2, b2), dk in G[((1, i, j, 0), b)]:
                    typ2, i2, j2, k2 = s2
                    if typ2 != 0 or k2 not in (0, 1):
                        raise AssertionError(f"down state {(i, j, b)} of {R} leaves to {s2}")
                    if G[((0, i2, j2, k2), b2)]:
                        opts[UP if k2 == 0 else LEFT] = (i2, j2, b2)
                out[(i, j, b)] = opts
    return out


def lifted_allowed(SG, L, M, qf, ell):
    """allowed(t, s, d): may a wall of left value ell leave the lifted square (t, s) in direction d?"""
    def allowed(t, s, d):
        i, j = (s - t) // 2, (s + t) // 2
        b = ell ^ ((qf[0] * (i // L) + qf[1] * (j // M)) & 1)
        return d in SG[(i % L, j % M, b)]
    return allowed


# ------------------------------------------------------------------ Theorem 7: the decider

def window(c, L, M):
    """(T, D) with T > 0 for w' = +-(c1 L, c2 M) in (t, s) = (j - i, i + j) coordinates."""
    dt, ds = c[1] * M - c[0] * L, c[0] * L + c[1] * M
    return (dt, ds) if dt > 0 else (-dt, -ds)


def candidate_classes(L, M, qf, limit):
    out = []
    for e1 in range(-2 * M - 2, 2 * M + 3):
        for e2 in range(-2 * L - 2, 2 * L + 3):
            dt, ds = e2 * M - e1 * L, e1 * L + e2 * M
            if 0 < dt <= limit and abs(ds) <= dt and (qf[0] * e1 + qf[1] * e2) % 2 == 0:
                out.append((e1, e2))
    return out


def good_wall_of_class(allowed, N, Ds, T, D, case, S0, use_window=True):
    """Arc consistency on x_0..x_{N-1} (wall heights at t = 0..N-1, x_{t+N} = x_t + Ds), x_0 in [0, S0).
    Constraints: allowed moves between consecutive times; x_t - x_{t-T} < D (case A) or > D (case B). All are max-closed."""
    lo, hi = -N - 2, S0 + N + 2
    dom = [set(v for v in range(lo, hi + 1) if (v - t) % 2 == 0) for t in range(N)]
    dom[0] = set(v for v in dom[0] if 0 <= v < S0)
    cons = []
    for t in range(N):
        k1, r1 = divmod(t + 1, N)
        cons.append((t, r1, (lambda tt, kk: lambda va, vb: abs(vb + kk * Ds - va) == 1 and
                             allowed(tt, va, UP if vb + kk * Ds == va + 1 else LEFT))(t, k1)))
        if use_window:
            k0, r0 = divmod(t - T, N)
            if case == "A":
                cons.append((t, r0, (lambda kk: lambda va, vb: va - (vb + kk * Ds) < D)(k0)))
            else:
                cons.append((t, r0, (lambda kk: lambda va, vb: va - (vb + kk * Ds) > D)(k0)))
    arcs = {}
    for a, b, p in cons:
        arcs.setdefault(a, []).append((b, p, False))
        arcs.setdefault(b, []).append((a, p, True))
    queue, inq = deque(range(N)), set(range(N))
    while queue:
        a = queue.popleft()
        inq.discard(a)
        for b, p, rev in arcs.get(a, []):
            if rev:
                new = set(vb for vb in dom[b] if any(p(vb, va) for va in dom[a]))
            else:
                new = set(vb for vb in dom[b] if any(p(va, vb) for va in dom[a]))
            if new != dom[b]:
                dom[b] = new
                if not new:
                    return False
                if b not in inq:
                    queue.append(b)
                    inq.add(b)
    return all(dom)


def type_lattice(L, M, qf):
    g = gcd(L, M)
    a, b = M // g, L // g
    S0 = 2 * L * M // g * (1 if (qf[0] * a + qf[1] * b) % 2 == 0 else 2)
    index = 1 if qf == (0, 0) else 2
    return S0, index * L * M


def decide(R, L, M, q, x, c, moves, use_window=True):
    if c[0] * c[1] > 0:   # WALLS-WITH-CHOICES-20261024-001A-P001, Theorem 3
        return A.has_cycle(A.wall_graph(R, L, M, q, x, moves))
    SG = square_graph(R, L, M, q, x, moves)
    qf = A.frame_data(R, L, M, q)[4]
    T, D = window(c, L, M)
    S0, size = type_lattice(L, M, qf)
    for e in candidate_classes(L, M, qf, size):
        if DR.det(c, e) == 0:
            continue
        N, Ds = e[1] * M - e[0] * L, e[0] * L + e[1] * M
        for ell in (0, 1):
            allowed = lifted_allowed(SG, L, M, qf, ell)
            for case in ("A", "B"):
                if good_wall_of_class(allowed, N, Ds, T, D, case, S0, use_window):
                    return True
    return False


# ------------------------------------------------------------------ Lemmas 4 and 5: ordered maximum and split

def value(W, t):
    t0, vals, (N, Ds) = W
    k, r = divmod(t - t0, N)
    return vals[r] + k * Ds


def translate(W, v):
    t0, vals, h = W
    return (t0 + v[0], [s + v[1] for s in vals], h)


def is_valid(W, allowed):
    t0, vals, (N, Ds) = W
    for t in range(t0, t0 + N):
        a, b = value(W, t), value(W, t + 1)
        if abs(b - a) != 1 or not allowed(t, a, UP if b == a + 1 else LEFT):
            return False
    return True


def good_case(W, T, D):
    t0, vals, (N, Ds) = W
    if all(value(W, t) - value(W, t - T) < D for t in range(t0, t0 + N)):
        return "A"
    if all(value(W, t) - value(W, t - T) > D for t in range(t0, t0 + N)):
        return "B"
    return None


def lattice_vectors(L, M, qf, radius):
    return [(b * M - a * L, a * L + b * M) for a in range(-radius, radius + 1) for b in range(-radius, radius + 1)
            if (qf[0] * a + qf[1] * b) % 2 == 0]


def ordered_max(W, lam):
    """Lemma 4: the maximum of the translates W + v with det(h, v) <= 0 that can reach above W."""
    t0, vals, (N, Ds) = W
    dev = [vals[r] - Ds * r / N for r in range(N)]
    osc = max(dev) - min(dev)
    keep = [v for v in lam if N * v[1] - Ds * v[0] <= 0 and v[1] - Ds / N * v[0] >= -osc - 2]
    Ws = [translate(W, v) for v in keep]
    return (t0, [max(value(X, t) for X in Ws) for t in range(t0, t0 + N)], (N, Ds))


def comparable_with_translates(W, lam):
    t0, vals, (N, Ds) = W
    for v in lam:
        V = translate(W, v)
        diffs = [value(V, t) - value(W, t) for t in range(t0, t0 + N)]
        if min(diffs) < 0 < max(diffs):
            return False
    return True


def primitive(W, lam):
    t0, vals, (N, Ds) = W
    lamset = set(lam)
    for d in range(1, N + 1):
        if N % d == 0 and Ds % (N // d) == 0:
            per = (d, Ds // (N // d))
            if per in lamset and all(value(W, t + d) == value(W, t) + per[1] for t in range(t0, t0 + N)):
                return (t0, [value(W, t) for t in range(t0, t0 + d)], per)
    return W


def repeated_square(W, L, M, qf):
    t0, vals, (N, Ds) = W
    seen = {}
    for t in range(t0, t0 + N):
        s = value(W, t)
        i, j = (s - t) // 2, (s + t) // 2
        key = (i % L, j % M, (qf[0] * (i // L) + qf[1] * (j // M)) & 1)
        if key in seen:
            t1, s1 = seen[key]
            return t1, (t - t1, s - s1)
        seen[key] = (t, s)
    return None


def split(W, t1, v):
    t0, vals, (N, Ds) = W
    Wa = (t1, [value(W, t) for t in range(t1, t1 + v[0])], v)
    Wb = (t1 + v[0], [value(W, t) for t in range(t1 + v[0], t1 + N)], (N - v[0], Ds - v[1]))
    return Wa, Wb


def wall_from_walk(walk, e, L, M):
    pts = sorted(((j + pos[1] * M) - (i + pos[0] * L), (i + pos[0] * L) + (j + pos[1] * M))
                 for ((typ, i, j, k), b), pos in walk if typ == 1)
    if [t for t, _ in pts] != list(range(pts[0][0], pts[0][0] + len(pts))):
        return None
    return (pts[0][0], [s for _, s in pts], (e[1] * M - e[0] * L, e[0] * L + e[1] * M))


# ------------------------------------------------------------------ checks

def lemma1_checks(rng):
    count = 0
    for R in DIRECTED:
        for L, M in ((3, 3), (3, 4), (4, 4), (4, 5), (5, 5)):
            moves, fit = DR.wall_moves(L, M), DR.fitting(R, L, M)
            for q in ((0, 0), (0, 1), (1, 0), (1, 1)):
                if q in fit:
                    continue
                for _ in range(4):
                    square_graph(R, L, M, q, rng.randrange(1 << (2 * L * M)), moves)
                    count += 1
    return {"configurations": count, "directed structure holds": True}


SPLIT_EXAMPLES = [  # (placement, L, M, twist, configuration, class, sheets), located with the producer's scratch search
    (155, 3, 4, (0, 1), 12595308, (2, -1), 5), (155, 3, 4, (0, 1), 12595308, (1, -3), 5),
    (203, 3, 3, (0, 1), 30909, (1, -3), 7), (203, 3, 3, (0, 1), 186417, (1, -3), 5),
    (110, 3, 3, (0, 0), 219648, (2, -1), 7),
]


def shorten(R, L, M, q, x, c, m, a, nodes, moves, tally):
    """Lemmas 4 and 5 on the crossing wall of the cover assignment a; returns (start period, end period, splits)."""
    qf = A.frame_data(R, L, M, q)[4]
    SG = square_graph(R, L, M, q, x, moves)
    lam = lattice_vectors(L, M, qf, 12)
    T, D = window(c, L, M)
    seq, hc, F = A.crossing_wall(R, L, M, q, x, c, m, a, nodes)
    ok, walk, e = A.closed_walk(seq, hc, R, L, M, q, x, F, moves)
    if not ok:
        raise AssertionError("traced wall invalid")
    if e[1] * M - e[0] * L < 0:      # traced against the up-or-left orientation
        return None
    W = wall_from_walk(walk, e, L, M)
    ells = [l for l in (0, 1) if is_valid(W, lifted_allowed(SG, L, M, qf, l))]
    if len(ells) != 1:
        raise AssertionError("left value of a traced wall not determined")
    allowed = lifted_allowed(SG, L, M, qf, ells[0])
    case = good_case(W, T, D)
    if case is None:
        raise AssertionError("a crossing wall is not good")
    start, steps = W[2][0], 0
    while True:
        W = primitive(ordered_max(W, lam), lam)
        if not (is_valid(W, allowed) and good_case(W, T, D) == case and comparable_with_translates(W, lam)):
            raise AssertionError("ordered maximum failed")
        r = repeated_square(W, L, M, qf)
        if r is None:
            break
        t1, v = r
        Wa, Wb = split(W, t1, v)
        Vv = translate(W, v)
        up = all(value(Vv, t) >= value(W, t) for t in range(t1, t1 + W[2][0]))
        piece, other = ((Wb, Wa) if up else (Wa, Wb)) if case == "A" else ((Wa, Wb) if up else (Wb, Wa))
        if not (is_valid(piece, allowed) and good_case(piece, T, D) == case):
            raise AssertionError("split piece not good")
        tally["other piece not good"] += good_case(other, T, D) != case
        W, steps = piece, steps + 1
    if W[2][0] > type_lattice(L, M, qf)[1] or repeated_square(W, L, M, qf) is not None:
        raise AssertionError("shortened wall not simple on the type-preserving cover")
    return start, W[2][0], steps


def shortening_checks(rng):
    tally, random_part, examples = Counter(), Counter(), []
    longest = 0
    for R in WITH_CHOICES:
        for L, M, n in ((3, 3, 20), (3, 4, 8)):
            moves, fit = DR.wall_moves(L, M), DR.fitting(R, L, M)
            for _ in range(n):
                q = (rng.randrange(2), rng.randrange(2))
                if q in fit:
                    continue
                x = rng.randrange(1 << (2 * L * M))
                for c in DR.odd_classes([cc for cc in CLASSES if cc[0] * cc[1] <= 0], fit, q):
                    cov = A.cover_assignment(R, L, M, q, x, c, max_sheets=7)
                    if cov is None:
                        continue
                    out = shorten(R, L, M, q, x, c, cov[0], cov[1], cov[2], moves, tally)
                    if out is None:
                        random_part["traced against the orientation (skipped)"] += 1
                        continue
                    random_part["walls shortened"] += 1
                    random_part["walls that needed a split"] += out[2] > 0
                    longest = max(longest, out[0])
    for R, L, M, q, x, c, m in SPLIT_EXAMPLES:
        moves = DR.wall_moves(L, M)
        nv, cl, nodes = DR.clauses(R, L, M, q, x, c, m, True)
        a = DR.dpll(nv, cl)
        if a is None or not DR.satisfies(cl, a):
            raise AssertionError("listed cover has no assignment")
        start, end, steps = shorten(R, L, M, q, x, c, m, a, nodes, moves, tally)
        examples.append({"placement": R, "torus": f"{L}x{M}", "twist": f"{q[0]}{q[1]}", "configuration": x, "class": list(c),
                         "sheets": m, "starting period": start, "final period": end, "splits": steps})
    return {"random walls": dict(random_part), "longest random starting period": longest, "listed walls": examples,
            "other piece not good (control)": tally["other piece not good"]}


def decider_checks(rng):
    rows = []
    agree = disagree = undetermined = 0
    no_window_false_accepts = 0
    for R in DIRECTED:
        for L, M, n, truth_kind in ((3, 3, 25, "simple cycles"), (3, 4, 10, "simple cycles"),
                                    (4, 4, 4, "own solver"), (4, 5, 3, "own solver")):
            moves, fit = DR.wall_moves(L, M), DR.fitting(R, L, M)
            tally = Counter()
            for _ in range(n):
                q = (rng.randrange(2), rng.randrange(2))
                if q in fit:
                    continue
                x = rng.randrange(1 << (2 * L * M))
                cyc = None
                if truth_kind == "simple cycles":
                    cyc, capped = A.simple_cycles(A.wall_graph(R, L, M, q, x, moves), cap=10 ** 6)
                    if capped:
                        raise AssertionError("simple cycle enumeration capped")
                    info = [(e, A.overlaps(p)) for p, e in cyc]
                classes = CLASSES if truth_kind == "simple cycles" else [(1, 0), (0, 1), (1, -1), (1, 2), (2, -1)]
                for c in DR.odd_classes(classes, fit, q):
                    if cyc is not None:
                        truth = any(A.good(c, e, ov) for e, ov in info)
                    else:
                        cov = A.cover_assignment(R, L, M, q, x, c, max_sheets=10)
                        truth = True if cov is not None else (False if A.certify_strip_unsat(R, L, M, q, x, c) else None)
                    got = decide(R, L, M, q, x, c, moves)
                    if truth is None:
                        undetermined += 1
                        tally["undetermined"] += 1
                        continue
                    tally["agree" if got == truth else "disagree"] += 1
                    tally["assignment" if truth else "contradiction"] += 1
                    agree += got == truth
                    disagree += got != truth
                    if truth is False and c[0] * c[1] <= 0 and decide(R, L, M, q, x, c, moves, use_window=False):
                        no_window_false_accepts += 1
            rows.append({"placement": R, "torus": f"{L}x{M}", "ground truth": truth_kind, **dict(sorted(tally.items()))})
    return {"rows": rows, "agree": agree, "disagree": disagree, "undetermined": undetermined,
            "no-window decider accepts a contradicting class (control)": no_window_false_accepts}


def twist_control(rng):
    """Reading the type-preserving lattice with the placement's twist instead of the frame's: some shortened wall of a frame-flipped
    placement then shows a repeated square."""
    for R in (110, 62):
        L, M = 3, 3
        moves, fit = DR.wall_moves(L, M), DR.fitting(R, L, M)
        for _ in range(60):
            q = (rng.randrange(2), rng.randrange(2))
            if q in fit:
                continue
            qf = A.frame_data(R, L, M, q)[4]
            if qf == q:
                continue
            x = rng.randrange(1 << (2 * L * M))
            cyc, capped = A.simple_cycles(A.wall_graph(R, L, M, q, x, moves), cap=10 ** 6)
            for p, e in cyc:
                ov = A.overlaps(p)
                if ov and all((qf[0] * d[0] + qf[1] * d[1]) % 2 for d in ov) and \
                        not all((q[0] * d[0] + q[1] * d[1]) % 2 for d in ov):
                    return True
    return False


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    lem1 = lemma1_checks(rng)
    short = shortening_checks(rng)
    dec = decider_checks(rng)
    controls = {
        "dropping the window constraint accepts a contradicting class": dec["no-window decider accepts a contradicting class (control)"] > 0,
        "the other piece of a split can lose goodness": short["other piece not good (control)"] > 0,
        "the placement's twist instead of the frame's misreads the type-preserving lattice": twist_control(rng),
    }
    ok = (lem1["directed structure holds"] and short["random walls"].get("walls shortened", 0) > 0
          and all(ex["splits"] > 0 for ex in short["listed walls"])
          and dec["disagree"] == 0 and dec["undetermined"] == 0 and dec["agree"] > 0 and all(controls.values()))
    result["checks"] = {"Lemma 1": lem1, "Lemmas 4 and 5, Theorem 6": short, "Theorem 7": dec}
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
    summary = {k: v for k, v in result["checks"].items()}
    summary["Theorem 7"] = {k: v for k, v in dec.items() if k != "rows"}
    print(json.dumps({"status": result["status"], "checks": summary, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
