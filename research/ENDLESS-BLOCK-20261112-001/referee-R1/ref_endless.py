#!/usr/bin/env python3
"""Referee ENDLESS-BLOCK-R1: the one-order arm by transfer matrices, with the referee's own code (the referee's ref_lib.py of the
BASES-WITHIN referee folder for the harmonies; no import of endless_lib.py, nest_lib.py or check.py).

    python3 -B ref_endless.py --part one|sat|every [--kmax 48]

one:   for every harmony, the relation R of one knot under one order (the allowed triples of states of the three copies: for every
       kind (0, a, b) and every i, NAE(u(i), v(i + a), w(i + b))), its count matrix M(u, w) = #{v : R(u, v, w)} (v the pendant copy of
       a chain knot), and on the closed chain of k knots (copies x_0, ..., x_(k-1) on the loop, x_i in slot 0 and x_(i+1) in slot 2
       of knot i): the number of states trace(M^k), and every tie between the root copy x_0 and a loop copy x_j (place i of x_0,
       place i' of x_j, relation r), read from the pairs (u, w) with (A^j)(u, w) > 0 and (A^(k-j))(w, u) > 0, A = [M > 0]; for
       k = 2 to kmax. The open chain: ties at spine distance d, from A^d alone (every extension exists since R holds the diagonal).
sat:   cross-checks of the transfer-matrix counts and ties by direct SAT on the substituted closed chains (the referee's clauses).
every: the every-order and lagged arms (E1, E2) by SAT counts on the closed chain of 3 and the chain of 4."""
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as R  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402


def words(h):
    W = R.states(h)
    return W, np.array(W, dtype=np.uint8)


def relation(h):
    """R as a boolean array over W x W x W (u: slot 0, v: slot 1, w: slot 2)"""
    W, A = words(h)
    P = h["P"]
    n = len(W)
    ok = np.ones((n, n, n), dtype=bool)
    for a, b in h["kinds"]:
        Va = np.roll(A, -a, axis=1)        # Va[v, i] = v(i + a)
        Wb = np.roll(A, -b, axis=1)
        for i in range(P):
            u = A[:, i][:, None, None]
            v = Va[:, i][None, :, None]
            w = Wb[:, i][None, None, :]
            ok &= ~((u == v) & (v == w))
    return W, ok


def ties_from_pairs(W, pairs):
    """place-level ties between the two copies over the allowed pairs (u, w): {(i, i'): r}"""
    if not pairs:
        return None
    U = np.array([W[u] for u, _ in pairs], dtype=np.uint8)
    V = np.array([W[w] for _, w in pairs], dtype=np.uint8)
    P = U.shape[1]
    out = {}
    for i in range(P):
        for j in range(P):
            x = U[:, i] ^ V[:, j]
            if np.all(x == x[0]):
                out[(i, j)] = int(x[0])
    return out


def own_ties(W):
    pairs = [(u, u) for u in range(len(W))]
    return ties_from_pairs(W, pairs)


def one_part(kmax):
    rows = []
    for idx, h in enumerate(R.harmonies()):
        t0 = time.time()
        W, ok = relation(h)
        n = len(W)
        M = ok.sum(axis=1).astype(object)           # counts over the pendant v: M[u, w]
        Ab = (M > 0)
        diag = all(ok[u, u, u] for u in range(n))
        own = own_ties(W)
        # open chain: ties at spine distance d from A^d (the diagonal is in R, so every value extends)
        Ad = np.eye(n, dtype=bool)
        open_ties = {}
        for d in range(1, 4):
            Ad = (Ad.astype(int) @ Ab.astype(int)) > 0
            pairs = [(u, w) for u in range(n) for w in range(n) if Ad[u, w]]
            t = ties_from_pairs(W, pairs)
            open_ties[d] = sorted(f"{i},{j},{r}" for (i, j), r in t.items()) if t else []
        # the transfer digraph without its loops: the shortest closed walk with a non-constant step
        off = Ab & ~np.eye(n, dtype=bool)
        girth = None
        Pk = np.eye(n, dtype=bool)
        reach = [Pk]
        Bin = Ab.astype(int)
        for k in range(1, kmax + 1):
            reach.append((reach[-1].astype(int) @ Bin) > 0)
        # closed walks of length k containing a non-loop step exist iff some u has an off-diagonal w with
        # (A^1 off)(u, w) and (A^(k-1))(w, u)
        for k in range(1, kmax + 1):
            if np.any(off & reach[k - 1].T):
                girth = k
                break
        loops = {}
        Mk = [np.eye(n, dtype=object)]
        for k in range(1, 9):
            Mk.append(Mk[-1].dot(M))
        eye = np.eye(n, dtype=bool)
        for k in range(2, kmax + 1):
            states = int(sum(Mk[k][u, u] for u in range(n))) if k <= 8 else None
            root = int(np.sum(np.diag(reach[k])))
            locked = all(not np.any((reach[j] & reach[k - j].T) & ~eye) for j in range(1, k))
            entry = {"states": states, "root states": root, "loop copies all equal in every state": locked}
            if k in (2, 3, 4, 6) or locked != loops.get(k - 1, {}).get("loop copies all equal in every state", locked):
                tj = {}
                for j in range(1, k):
                    X = reach[j] & reach[k - j].T
                    pairs = [(int(u), int(w)) for u, w in zip(*np.nonzero(X))]
                    t = ties_from_pairs(W, pairs) or {}
                    tj[j] = sorted(f"{i},{jj},{r}" for (i, jj), r in t.items())
                entry["ties of x_0 with x_j"] = tj
            loops[k] = entry
        lock_lengths = [k for k in range(2, kmax + 1) if loops[k]["loop copies all equal in every state"]]
        rows.append({"i": idx, "orbits": h["orbits"], "P": P_of(h), "states": n, "diagonal in R": diag,
                     "single knot ties copies (open distance 1)": bool(open_ties[1]), "open-chain ties by distance": open_ties,
                     "shortest closed walk with a step (girth)": girth, "loop lengths that lock (2..kmax)": lock_lengths,
                     "loops": {str(k): v for k, v in loops.items()}, "seconds": round(time.time() - t0, 1)})
        print(idx, h["orbits"][:2], n, "girth", girth, "locks", lock_lengths[:6], "...", round(time.time() - t0, 1), flush=True)
    return rows


def P_of(h):
    return h["P"]


# ---------------------------------------------------------------- direct SAT cross-checks

def clauses_one_order(h, Ppat):
    n, PK = Ppat
    P = h["P"]
    var = lambda v, i: v * P + (i % P) + 1
    cl = []
    for v in range(n):
        for a, b in h["kinds"]:
            for i in range(P):
                t = (var(v, i), var(v, i + a), var(v, i + b))
                cl += [list(t), [-x for x in t]]
    for (x, y, z) in PK:
        for a, b in h["kinds"]:
            for i in range(P):
                t = (var(x, i), var(y, i + a), var(z, i + b))
                cl += [list(t), [-u for u in t]]
    return cl, n * P, var


def sat_count(cl, nv, cap):
    c = 0
    with Glucose4(bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            c += 1
            if c > cap:
                return None
            s.add_clause([-(i + 1) if m[i] > 0 else (i + 1) for i in range(nv)])
    return c


def sat_tied(cl, a, b):
    """relation forced between variables a and b (1-based), or None"""
    with Glucose4(bootstrap_with=cl) as s:
        if not s.solve():
            return "dead"
        m = s.get_model()
        r = (m[a - 1] > 0) ^ (m[b - 1] > 0)
        # other relation possible?
        want = [a, b if not r else -b]       # a true, b equal (r=0 -> try b false i.e. unequal)
        want = [a, -b] if r == 0 else [a, b]
        return None if s.solve(assumptions=want) else int(r)


def closed_chain(k):
    return (2 * k, [(2 * i, 2 * i + 1, (2 * i + 2) % (2 * k)) for i in range(k)])


def sat_part():
    one = json.loads((HERE / "result_one.json").read_text())["rows"]
    hs = R.harmonies()
    out = []
    for row in one:
        h = hs[row["i"]]
        if len(R.states(h)) > 66 or not row["loop lengths that lock (2..kmax)"]:
            continue
        g = row["shortest closed walk with a step (girth)"]
        for k in sorted({3, g - 1, g, g + 1} - {1, 2}):
            if str(k) not in row["loops"]:
                continue
            cl, nv, var = clauses_one_order(h, closed_chain(k))
            pred = row["loops"][str(k)]["states"]
            c = sat_count(cl, nv, cap=20000) if (pred is not None and pred <= 20000) else "not counted (over 20,000)"
            item = {"i": row["i"], "orbits": h["orbits"], "k": k, "SAT states": c, "transfer states": pred,
                    "agree": (c == pred) if isinstance(c, int) else None}
            # the lock: root (x_0, 0) against (x_1, 0) and (x_1, i) for every i, by SAT
            locked = row["loops"][str(k)]["loop copies all equal in every state"]
            r_sat = [sat_tied(cl, var(0, 0), var(2, i)) for i in range(h["P"])]
            item["SAT ties of (x0, 0) with x1"] = r_sat
            if "ties of x_0 with x_j" in row["loops"][str(k)]:
                tj = row["loops"][str(k)]["ties of x_0 with x_j"]["1"]
                pred_r = [next((int(s.split(",")[2]) for s in tj if s.split(",")[0] == "0" and s.split(",")[1] == str(i)), None)
                          for i in range(h["P"])]
                item["transfer ties of (x0, 0) with x1"] = pred_r
                item["ties agree"] = pred_r == r_sat
            item["locked (transfer)"] = locked
            out.append(item)
            print(item["i"], h["orbits"][:1], k, c, pred, item.get("ties agree"), flush=True)
    return out


# ---------------------------------------------------------------- every order and lagged

def h_knots(h):
    P = h["P"]
    return sorted({tuple(sorted((i % P, (i + a) % P, (i + b) % P))) for a, b in h["kinds"] for i in range(P)})


def clauses_every(h, Ppat, lags=None):
    n, PK = Ppat
    P = h["P"]
    var = lambda v, i: v * P + (i % P) + 1
    cl = []
    for v in range(n):
        for a, b in h["kinds"]:
            for i in range(P):
                t = (var(v, i), var(v, i + a), var(v, i + b))
                cl += [list(t), [-x for x in t]]
    K = h_knots(h)
    for e, (x, y, z) in enumerate(PK):
        sx, sy, sz = (lags or {}).get(e, (0, 0, 0))
        for k3 in K:
            for p, q, r in itertools.permutations(k3):
                t = (var(x, p + sx), var(y, q + sy), var(z, r + sz))
                cl += [list(t), [-u for u in t]]
    return cl, n * P


def every_part():
    out = []
    for idx, h in enumerate(R.harmonies()):
        W = R.states(h)
        P = h["P"]
        if len(W) > 40:
            continue
        cl, nv = clauses_every(h, closed_chain(3))
        c3 = sat_count(cl, nv, 5000)
        cl, nv = clauses_every(h, (9, [(2 * i, 2 * i + 1, 2 * i + 2) for i in range(4)]))
        c4 = sat_count(cl, nv, 5000)
        lag = []
        for s in range(P):
            cl, nv = clauses_every(h, closed_chain(3), lags={0: (s, 0, 0)})
            c = sat_count(cl, nv, 5000)
            g = math.gcd(P, s)
            fixed = sum(1 for w in W if all(w[i] == w[(i + g) % P] for i in range(P)))
            lag.append({"lag": s, "states": c, "predicted (fixed by the shift by gcd)": fixed, "agree": c == fixed})
        out.append({"i": idx, "orbits": h["orbits"], "states of H": len(W), "every order, closed chain of 3": c3, "chain of 4": c4,
                    "E1 agrees": c3 == len(W) and c4 == len(W), "E2 lag cells agree": sum(x["agree"] for x in lag), "lag cells": len(lag)})
        print(idx, h["orbits"][:1], len(W), c3, c4, out[-1]["E2 lag cells agree"], len(lag), flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    kmax = int(sys.argv[sys.argv.index("--kmax") + 1]) if "--kmax" in sys.argv else 48
    t0 = time.time()
    res = {"one": lambda: {"rows": one_part(kmax)}, "sat": lambda: {"rows": sat_part()}, "every": lambda: {"rows": every_part()}}[part]()
    res["seconds"] = round(time.time() - t0, 1)
    (HERE / f"result_{part}.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("wrote", part, res["seconds"], "s")
