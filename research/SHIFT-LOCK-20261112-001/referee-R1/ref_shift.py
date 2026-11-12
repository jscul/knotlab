#!/usr/bin/env python3
"""Referee SHIFT-LOCK-R1: the mixed-knot arrangements, with the referee's own code (ref_lib.py of the BASES-WITHIN referee folder for
the harmonies; no import of shift_lib.py, loop_lib.py or endless_lib.py).

    python3 -B ref_shift.py --part mixed [--workers 8]     (every harmony, n, m = 2 .. 9: result_mixed.jsonl, one line per cell)
    python3 -B ref_shift.py --part square                  (0011 and 0011 + 01, n, m = 2 .. 16: locks; result_square.json)
    python3 -B ref_shift.py --part ledrappier              (the XOR law on the same three copies, n x n to 32: result_ledrappier.json)

Copies at (r, c) in Z_n x Z_m, each a state of the harmony on Z_P (its own kinds); the mixed knot on copies (x, x + (0, 1), x + (1, 0))
binds NAE((x, i), (x + (0, 1), i + a), (x + (1, 0), i + b)) for every kind (0, a, b) and every place i. Locked: every state has all
copies equal. A state repeats along a step s (sup-norm at most 2, reduced mod (n, m), not zero, one of s and -s) when
X(x + s)(i) = X(x)(i + a) xor e at every copy x and place i, for one shift a and flip e. With Glucose 4 and no conflict budget (the
census bounded each call to 20,000 conflicts and left 376 cells unsettled)."""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as R  # noqa: E402

_HS = None


def hs():
    """the 45 harmonies, computed once per process"""
    global _HS
    if _HS is None:
        _HS = R.harmonies()
    return _HS


SHORT = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 0), (0, 2), (2, 1), (1, 2), (2, -1), (1, -2), (2, 2), (2, -2)]


def steps(n, m):
    seen, out = set(), []
    for a, b in SHORT:
        red, neg = (a % n, b % m), ((-a) % n, (-b) % m)
        if red == (0, 0) or red in seen or neg in seen:
            continue
        seen.add(red)
        out.append((a, b))
    return out


def base_cnf(h, n, m):
    P = h["P"]
    var = lambda r, c, i: ((r % n) * m + (c % m)) * P + (i % P) + 1
    cl = []
    for r in range(n):
        for c in range(m):
            for a, b in h["kinds"]:
                for i in range(P):
                    t = (var(r, c, i), var(r, c, i + a), var(r, c, i + b))
                    cl += [list(t), [-x for x in t]]
                    t = (var(r, c, i), var(r, c + 1, i + a), var(r + 1, c, i + b))
                    cl += [list(t), [-x for x in t]]
    nv = n * m * P
    # non-constant: some copy differs from copy (0, 0) at some place
    aux, nxt = [], nv + 1
    for r in range(n):
        for c in range(m):
            if (r, c) == (0, 0):
                continue
            for i in range(P):
                y = nxt
                nxt += 1
                p, q = var(0, 0, i), var(r, c, i)
                cl += [[-y, p, q], [-y, -p, -q]]
                aux.append(y)
    cl.append(aux)
    return cl, var


def mixed_cell(args):
    hi, n, m = args
    h = hs()[hi]
    P = h["P"]
    t0 = time.time()
    cl, var = base_cnf(h, n, m)
    out = {"i": hi, "orbits": h["orbits"], "n": n, "m": m}
    with Glucose4(bootstrap_with=cl) as s:
        if not s.solve():
            out["locks"] = True
            out["seconds"] = round(time.time() - t0, 2)
            return out
    out["locks"] = False
    found = None
    for (a, b) in steps(n, m):
        for sh in range(P):
            for e in (0, 1):
                extra = []
                for r in range(n):
                    for c in range(m):
                        for i in range(P):
                            x, y = var(r + a, c + b, i), var(r, c, i + sh)
                            if e:
                                extra += [[x, y], [-x, -y]]
                            else:
                                extra += [[-x, y], [x, -y]]
                with Glucose4(bootstrap_with=cl + extra) as s:
                    if s.solve():
                        found = [[a, b], sh, e]
                        break
            if found:
                break
        if found:
            break
    out["short-step state"] = found
    out["seconds"] = round(time.time() - t0, 2)
    return out


def lock_only(h, n, m):
    cl, var = base_cnf(h, n, m)
    with Glucose4(bootstrap_with=cl) as s:
        return not s.solve()


def ledrappier(N=32):
    """x(r, c) + x(r, c+1) + x(r+1, c) = 0 mod 2 on Z_n x Z_n: a non-constant (non-zero) solution iff the kernel is not zero"""
    out = {}
    for n in range(2, N + 1):
        rows = []
        idx = lambda r, c: (r % n) * n + (c % n)
        for r in range(n):
            for c in range(n):
                v = (1 << idx(r, c)) ^ (1 << idx(r, c + 1)) ^ (1 << idx(r + 1, c))
                rows.append(v)
        rank, piv = 0, {}
        for v in rows:
            for b in sorted(piv, reverse=True):
                if v >> b & 1:
                    v ^= piv[b]
            if v:
                piv[v.bit_length() - 1] = v
                rank += 1
        out[n] = n * n - rank
    return out


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    t0 = time.time()
    if part == "mixed":
        workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
        path = HERE / "result_mixed.jsonl"
        done = set()
        if path.exists():
            done = {(x["i"], x["n"], x["m"]) for x in map(json.loads, open(path))}
        items = [(i, n, m) for i in range(45) for n in range(2, 10) for m in range(2, 10) if (i, n, m) not in done]
        sizes = [len(R.states(h)) for h in hs()]
        items.sort(key=lambda t: -sizes[t[0]] * t[1] * t[2])
        with Pool(workers) as pool, open(path, "a") as f:
            for k, row in enumerate(pool.imap_unordered(mixed_cell, items, chunksize=1)):
                f.write(json.dumps(row) + "\n")
                f.flush()
                if (k + 1) % 100 == 0:
                    print(k + 1, "/", len(items), round(time.time() - t0, 1), "s", flush=True)
    elif part == "square":
        hs = R.harmonies()
        res = {}
        for h in hs:
            if h["orbits"] in (["0011"], ["0011", "01"]):
                res["+".join(h["orbits"])] = [[n, m] for n in range(2, 17) for m in range(2, 17) if lock_only(h, n, m)]
                print(h["orbits"], len(res["+".join(h["orbits"])]), flush=True)
        (HERE / "result_square.json").write_text(json.dumps(res, indent=1) + "\n")
    elif part == "ledrappier":
        k = ledrappier()
        (HERE / "result_ledrappier.json").write_text(json.dumps({"kernel dimension by n": k,
                                                                 "unlocking n": [n for n, d in k.items() if d > 0]}, indent=1) + "\n")
        print([n for n, d in k.items() if d > 0])
    print("done", part, round(time.time() - t0, 1), "s")
