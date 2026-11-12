#!/usr/bin/env python3
"""Referee PARITY-MIX-R1: parity knots among not-all-equal stitched copies, rebuilt with the referee's own code (ref_lib.py of the
BASES-WITHIN referee folder for the 45 harmonies of period at most 16; no import of parity_lib.py, shift_lib.py, check.py or the
census's other modules).

Encoding (different from the census's): each copy x on the n x m repeat holds one class j of the harmony's states up to flips
(one-hot s[x][j]) and a flip bit f[x]; its bits are b[x][i] = rep_j(i) xor f[x]. The mixed knot at cell (r, c) is on copies
(x, y, z) = ((r, c), (r, c + 1), (r + 1, c)): either the not-all-equal one-order stitch NAE(b[x][i], b[y][i + a], b[z][i + b]) for every
kind (a, b) and place i, or a flip-blind parity knot b[x][i] xor b[y][i] xor b[z][i] = t for every place i, with one hidden t per knot.
Count r: the copies (r, c), c = 0 .. m - 1. Two states compared up to flips compare classes only.

Measures per placement K (the cells with parity): a state?; for r >= 1, count r flip-frozen (one class tuple in every state), fixed by
count 0 (two states with the same classes on count 0 have the same classes on count r), reached by the frozen propagation rule (from
count 0: a parity knot with two known members makes the third known; a not-all-equal knot does in a slot where the other two classes
always leave one class). And, for each count fixed but unreached, where its fixing already holds:
  B1 the parity knots' own linear algebra over F_2^P / <1...1> (copies free, no states, no stitches);
  B2 the parity knots with each copy a state (no stitches);
  BN the stitches outside K with each copy a state (no parity knots);
  only the whole (fixed with both, in neither B2 nor BN).
Fixed in a relaxation implies fixed in the whole, so the four classes are nested as listed."""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402

_HS = None


def hs():
    global _HS
    if _HS is None:
        _HS = RL.harmonies()
    return _HS


def setup(h):
    P = h["P"]
    full = (1 << P) - 1
    W = sorted(sum(b << i for i, b in enumerate(w)) for w in RL.states(h))
    reps = sorted({min(w, w ^ full) for w in W})
    return {"h": h, "name": " + ".join(h["orbits"]), "P": P, "full": full, "kinds": [tuple(k) for k in h["kinds"]], "W": W,
            "reps": reps, "rep index": {w: reps.index(min(w, w ^ full)) for w in W}}


def bit(w, i, P):
    return (w >> (i % P)) & 1


def stitch(u, v, w, st):
    P = st["P"]
    return all(len({bit(u, i, P), bit(v, i + a, P), bit(w, i + b, P)}) == 2 for a, b in st["kinds"] for i in range(P))


def census(st):
    W, full, P = st["W"], st["full"], st["P"]
    Ws = set(W)
    fb = [(u, v, w) for u in W for v in W for w in (u ^ v, u ^ v ^ full) if w in Ws]
    both = [t for t in fb if stitch(*t, st)]
    classes = set(st["reps"])
    # largest d: a subspace of F_2^P / <1> whose non-zero elements are all classes (d = 2 iff some class sum is a class)
    canon = lambda x: min(x, x ^ full)
    best = 0

    def grow(span, last):
        nonlocal best
        best = max(best, len(span).bit_length() - 1)
        for x in st["reps"]:
            if x <= last or x in span:
                continue
            new = span | {canon(s ^ x) for s in span}
            if all(y in classes for y in new if y):
                grow(new, x)
    grow({0}, -1)
    R = [(u, v, w) for u in W for v in W for w in W if stitch(u, v, w, st)]
    ri = st["rep index"]
    func = {}
    for slot in range(3):
        o = [j for j in range(3) if j != slot]
        seen, ok = {}, True
        for t in R:
            if seen.setdefault((ri[t[o[0]]], ri[t[o[1]]]), ri[t[slot]]) != ri[t[slot]]:
                ok = False
                break
        func[slot] = ok
    return {"harmony": st["name"], "P": P, "states": len(W), "classes": len(st["reps"]), "flip-blind triples": len(fb),
            "flip-blind triples in the stitch": len(both), "largest subspace": best if fb else 0, "stitch triples": len(R),
            "functional slots": func}


class Arr:
    """the arrangement's CNF on one copy of the variables"""

    def __init__(self, st, n, m, K, use_nae=True, use_par=True, base=0):
        self.st, self.n, self.m = st, n, m
        P, C = st["P"], len(st["reps"])
        self.nxt = base + 1
        new = lambda: self._new()
        self.s = [[new() for _ in range(C)] for _ in range(n * m)]
        self.f = [new() for _ in range(n * m)]
        self.b = [[new() for _ in range(P)] for _ in range(n * m)]
        cl = []
        for x in range(n * m):
            cl.append(self.s[x][:])
            for j1 in range(C):
                for j2 in range(j1 + 1, C):
                    cl.append([-self.s[x][j1], -self.s[x][j2]])
            for j, rep in enumerate(st["reps"]):
                for i in range(P):
                    s, bb, f = self.s[x][j], self.b[x][i], self.f[x]
                    if bit(rep, i, P):
                        cl += [[-s, bb, f], [-s, -bb, -f]]
                    else:
                        cl += [[-s, -bb, f], [-s, bb, -f]]
        for r in range(n):
            for c in range(m):
                x, y, z = self.v(r, c), self.v(r, c + 1), self.v(r + 1, c)
                cell = r * m + c
                if cell in K:
                    if not use_par:
                        continue
                    t = new()
                    for i in range(P):
                        lits = [self.b[x][i], self.b[y][i], self.b[z][i], t]
                        for sg in itertools.product((1, -1), repeat=4):
                            if sum(s < 0 for s in sg) % 2:
                                cl.append([s * l for s, l in zip(sg, lits)])
                elif use_nae:
                    for a, bk in st["kinds"]:
                        for i in range(P):
                            tt = [self.b[x][i], self.b[y][(i + a) % P], self.b[z][(i + bk) % P]]
                            cl += [tt, [-l for l in tt]]
        self.cl = cl

    def _new(self):
        v = self.nxt
        self.nxt += 1
        return v

    def v(self, r, c):
        return (r % self.n) * self.m + (c % self.m)


def solve(cl, assumptions=()):
    with Glucose4(bootstrap_with=cl) as s:
        return s.solve(assumptions=list(assumptions))


def fixing(st, n, m, K, use_nae=True, use_par=True, want_frozen=True):
    """(state?, frozen[r], fixed[r]) for r = 1 .. n - 1, up to flips (classes)"""
    A = Arr(st, n, m, K, use_nae, use_par)
    if not solve(A.cl):
        return False, None, None
    B = Arr(st, n, m, K, use_nae, use_par, base=A.nxt)
    nxt = B.nxt
    cl = A.cl + B.cl
    C = len(st["reps"])
    a0 = nxt
    nxt += 1
    for c in range(m):
        x = A.v(0, c)
        for j in range(C):
            cl += [[-a0, -A.s[x][j], B.s[x][j]], [-a0, A.s[x][j], -B.s[x][j]]]
    D = {}
    for r in range(1, n):
        D[r] = nxt
        nxt += 1
        ds = []
        for c in range(m):
            x = A.v(r, c)
            for j in range(C):
                d = nxt
                nxt += 1
                cl += [[-d, A.s[x][j]], [-d, -B.s[x][j]]]
                ds.append(d)
        cl.append([-D[r]] + ds)
    frozen, fixed = [], []
    with Glucose4(bootstrap_with=cl) as s:
        for r in range(1, n):
            fr = (not s.solve(assumptions=[D[r]])) if want_frozen else None
            fx = bool(fr) or not s.solve(assumptions=[a0, D[r]])
            frozen.append(fr)
            fixed.append(fx)
    return True, frozen, fixed


def propagation(n, m, K, func):
    v = lambda r, c: (r % n) * m + (c % m)
    known = {v(0, c) for c in range(m)}
    ks = [(r * m + c, (v(r, c), v(r, c + 1), v(r + 1, c))) for r in range(n) for c in range(m)]
    changed = True
    while changed:
        changed = False
        for cell, t in ks:
            unk = [j for j in range(3) if t[j] not in known]
            if len(unk) == 1 and (cell in K or func[unk[0]]):
                known.add(t[unk[0]])
                changed = True
    return [all(v(r, c) in known for c in range(m)) for r in range(1, n)]


def gf2_fixed(n, m, K):
    """B1: for r >= 1, is count r zero in every solution of the parity knots (x + y + z = 0 over F_2, copies free) with count 0 zero"""
    N = n * m
    v = lambda r, c: (r % n) * m + (c % m)
    rows = []
    for cell in K:
        r, c = divmod(cell, m)
        e = 0
        for x in (v(r, c), v(r, c + 1), v(r + 1, c)):
            e ^= 1 << x
        if e:
            rows.append(e)
    for c in range(m):
        rows.append(1 << v(0, c))
    # reduced row echelon form; a coordinate x is zero in every solution iff e_x lies in the row space
    basis = {}
    for e in rows:
        for p in sorted(basis, reverse=True):
            if (e >> p) & 1:
                e ^= basis[p]
        if e:
            p = e.bit_length() - 1
            for q in list(basis):
                if (basis[q] >> p) & 1:
                    basis[q] ^= e
            basis[p] = e

    def in_span(e):
        for p in sorted(basis, reverse=True):
            if (e >> p) & 1:
                e ^= basis[p]
        return e == 0
    return [all(in_span(1 << v(r, c)) for c in range(m)) for r in range(1, n)]


def analyse(st, n, m, K, func):
    ok, frozen, fixed = fixing(st, n, m, K)
    row = {"k": len(K), "state": ok}
    if not ok:
        return row
    reach = propagation(n, m, K, func)
    fbu = [r for r in range(n - 1) if fixed[r] and not frozen[r] and not reach[r]]
    row.update({"flip-frozen": sum(frozen), "fixed": sum(fixed), "reached": sum(reach), "fixed but unreached": len(fbu),
                "full fixing": all(fixed) and not all(frozen)})
    if fbu:
        b1 = gf2_fixed(n, m, K)
        _, _, fx2 = fixing(st, n, m, K, use_nae=False, want_frozen=False)
        okn, _, fxn = fixing(st, n, m, K, use_par=False, want_frozen=False)
        src = []
        for r in fbu:
            if b1[r]:
                src.append("B1 parity algebra")
            elif fx2[r]:
                src.append("B2 parity and states")
            elif fxn[r]:
                src.append("BN stitches alone")
            else:
                src.append("only the whole")
        row["sources"] = src
    return row


def translates(K, n, m):
    out = set()
    for dr in range(n):
        for dc in range(m):
            out.add(frozenset(((c // m + dr) % n) * m + (c % m + dc) % m for c in K))
    return out


def classes(n, m):
    seen, out = set(), []
    for mask in range(1 << (n * m)):
        K = frozenset(c for c in range(n * m) if (mask >> c) & 1)
        if K in seen:
            continue
        orb = translates(K, n, m)
        seen |= orb
        out.append(sorted(orb, key=lambda k: sorted(k)))
    return out


def job(arg):
    i, n = arg
    st = setup(hs()[i])
    func = census(st)["functional slots"]
    rows = []
    t0 = time.time()
    for orb in classes(n, n):
        rep = orb[0]
        alive = solve(Arr(st, n, n, rep).cl)
        for K in orb:            # every placement; the state is checked on each translate as well when the class survives
            if alive:
                rows.append({"cells": sorted(K), **analyse(st, n, n, K, func)})
            else:
                rows.append({"cells": sorted(K), "k": len(K), "state": False, "by class": True})
    return {"i": i, "harmony": st["name"], "n": n, "rows": rows, "seconds": round(time.time() - t0, 1)}


def main():
    part = sys.argv[1]
    t0 = time.time()
    H = hs()
    if part == "census":
        rows = [census(setup(h)) for h in H]
        (HERE / "result_census.json").write_text(json.dumps({"harmonies": len(rows), "rows": rows}, indent=1) + "\n")
        for r in rows:
            if r["flip-blind triples"] or any(r["functional slots"].values()):
                print(r)
        print("done", round(time.time() - t0, 1), "s")
        return
    n = int(part[1:])
    census_rows = json.loads((HERE / "result_census.json").read_text())["rows"]
    pick = [i for i, r in enumerate(census_rows) if r["flip-blind triples"]]
    out = []
    with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as pool:
        for res in pool.imap_unordered(job, [(i, n) for i in pick]):
            out.append(res)
            with open(HERE / f"result_{part}.jsonl", "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res["harmony"], len(res["rows"]), res["seconds"], "s", flush=True)
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
