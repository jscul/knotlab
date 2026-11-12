#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, side checks (after ref_line.py; the referee's own code, no import of the census's libraries):

  1. the census row by row: every harmony's period, states, kinds and its orbits' (period, antiperiodic, |Q|, |A|, cyclic subgroups
     inside, cosets inside), against result_census.json read as data;
  2. the Z2 x Z2 blocks (graphs of the two order-3 automorphisms of {0, half shift, flip, both}) and free pairs H x H (H any cyclic
     subgroup of Q of order at least 2), and every coset of either inside A (lagged forms);
  3. the 32 harmonies of span exactly 9: the same analysis;
  4. the theorem's lemma on its own: for every reduced Latin square of order 2 to 5 and every not-all-equal colouring of its rows,
     columns and symbols, at most one of the three is not constant (exhaustive); the same by SAT on random Latin squares of order
     6 to 10;
  5. the theorem's chain where its premise can fail: not-all-equal laws that are not harmonies (1 to 3 kinds of span at most 5, periods
     4 to 10, all periodic states), every permutive sub-stitch of order 2 or 3 on one set S, and whether the states of S then differ
     only at places free in every state of S (the proof's conclusion before its last step).

    python3 -B ref_line_checks.py      (writes result_checks.json)"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402
import ref_line as L  # noqa: E402

CENSUS = HERE.parents[2] / "proofs" / "LINE-LOCK-20261112-001A" / "LINE-LOCK-20261112-001A-P001_lines_in_increments"


def orbit_key(o):
    return (o["orbit period"], bool(o["antiperiodic"]), o["|Q|"] if "|Q|" in o else o["Q"], o["|A|"] if "|A|" in o else o["A"],
            o["cyclic subgroups inside"], o["cosets inside"])


def check_rows():
    mine = json.loads((HERE / "result_line.json").read_text())["rows"]
    theirs = json.loads((CENSUS / "result_census.json").read_text())["checks"]["result"]["rows"]
    key = lambda r: (r["P"], r["states"], r["kinds"], tuple(sorted(orbit_key(o) for o in r["orbits"])))
    km, kt = sorted(map(key, mine)), sorted(map(key, theirs))
    diff = [k for k in km if k not in kt] + [k for k in kt if k not in km]
    return {"harmonies (referee, census)": [len(mine), len(theirs)], "rows agree": km == kt, "differences": [str(d) for d in diff[:10]]}


def group(h, u):
    P = h["P"]
    full = (1 << P) - 1
    p = min(s for s in range(1, P + 1) if L.rot(u, s, P) == u)
    anti = any(L.rot(u, s, P) == u ^ full for s in range(P))
    Q = [(a, 0) for a in range(p)] if anti else [(a, e) for a in range(p) for e in (0, 1)]
    act = lambda g, x: L.rot(x, g[0], P) ^ (full if g[1] else 0)
    add = lambda g, k: ((g[0] + k[0]) % p, (g[1] + k[1]) % 2)
    A = {(y, z) for y in Q for z in Q if L.stitch(u, act(y, u), act(z, u), h["kinds"], P)}
    return p, anti, Q, add, A


def blocks(h):
    """Z2 x Z2 blocks and free pairs, as subgroups and as cosets, in every orbit"""
    out = {"Z2xZ2 blocks": 0, "Z2xZ2 block cosets": 0, "free pairs": 0, "free pair cosets": 0, "orbits with a Z2xZ2": 0}
    for u, orb in L.orbits(h):
        p, anti, Q, add, A = group(h, u)
        pair = lambda d, x: (add(d[0], x[0]), add(d[1], x[1]))
        z = (0, 0)
        shapes = []
        if not anti and p % 2 == 0:
            out["orbits with a Z2xZ2"] += 1
            k, e = (0, 1), (p // 2, 0)
            ke = add(k, e)
            shapes += [("block", [(z, z), (k, e), (e, ke), (ke, k)]), ("block", [(z, z), (e, k), (ke, e), (k, ke)])]
        seen = set()
        for g in Q:
            if g == z:
                continue
            H, x = [z], g
            while x != z:
                H.append(x)
                x = add(x, g)
            if frozenset(H) in seen:
                continue
            seen.add(frozenset(H))
            shapes.append(("pair", [(a, b) for a in H for b in H]))
        for kind, pts in shapes:
            if all(x in A for x in pts):
                out["Z2xZ2 blocks" if kind == "block" else "free pairs"] += 1
            S = set(pts)
            for d in A:
                if d in S:
                    continue
                if all(pair(d, x) in A for x in pts):
                    out["Z2xZ2 block cosets" if kind == "block" else "free pair cosets"] += 1
    return out


def span9():
    old = {(h["P"], tuple(sorted(h["orbits"]))) for h in RL.harmonies(max_span=8, max_period=10 ** 6)}
    rows = []
    for h in RL.harmonies(max_span=9, max_period=10 ** 9):
        if (h["P"], tuple(sorted(h["orbits"]))) in old:
            continue
        W = sorted(sum(b << i for i, b in enumerate(w)) for w in RL.states(h))
        hh = {"name": " + ".join(h["orbits"]), "P": h["P"], "kinds": [tuple(k) for k in h["kinds"]], "W": W}
        orbs = L.orbits(hh)
        an = [L.analyse_orbit(hh, u, o) for u, o in orbs]
        rows.append({"harmony": hh["name"], "P": hh["P"], "states": len(W), "orbits": len(orbs), "free site": L.free_site(hh),
                     "genuine subgroups": sum(len(o["genuine subgroups"]) for o in an),
                     "genuine cosets": sum(len(o["genuine cosets"]) for o in an), **blocks(hh)})
        print("span 9:", hh["name"][:50], hh["P"], len(W), flush=True)
    return rows


def latin_reduced(n):
    """all reduced Latin squares of order n (first row and column 0..n-1)"""
    out = []
    sq = [[None] * n for _ in range(n)]
    sq[0] = list(range(n))
    for i in range(n):
        sq[i][0] = i

    def fill(c):
        if c == n * n:
            out.append([r[:] for r in sq])
            return
        i, j = divmod(c, n)
        if i == 0 or j == 0:
            fill(c + 1)
            return
        for s in range(n):
            if all(sq[i][t] != s for t in range(j)) and all(sq[t][j] != s for t in range(i)) and \
                    all(sq[i][t] != s for t in range(j + 1, n) if sq[i][t] is not None):
                if any(sq[t][j] == s for t in range(n) if t != i and sq[t][j] is not None):
                    continue
                sq[i][j] = s
                fill(c + 1)
                sq[i][j] = None
    fill(0)
    return out


def lemma_exhaustive(nmax=5):
    res = {}
    for n in range(2, nmax + 1):
        sqs = latin_reduced(n)
        cells = np.array([(i, j, s[i][j]) for s in sqs for i in range(n) for j in range(n)]).reshape(len(sqs), n * n, 3)
        cols = np.array(list(itertools.product((0, 1), repeat=n)), dtype=np.int8)  # 2^n
        bad = 0
        colourings = 0
        for q in range(len(sqs)):
            r, c, s = cells[q, :, 0], cells[q, :, 1], cells[q, :, 2]
            for xi in range(len(cols)):
                x = cols[xi][r]
                # y and z over all: (2^n, n^2) arrays
                Y = cols[:, c]
                Z = cols[:, s]
                tot = x[None, None, :] + Y[:, None, :] + Z[None, :, :]
                okyz = ((tot != 0) & (tot != 3)).all(axis=2)  # (2^n, 2^n) not-all-equal on every cell
                if not okyz.any():
                    continue
                ys, zs = np.nonzero(okyz)
                for yi, zi in zip(ys, zs):
                    colourings += 1
                    nonconst = sum(1 for v in (cols[xi], cols[yi], cols[zi]) if 0 < v.sum() < n)
                    if nonconst > 1:
                        bad += 1
        res[n] = {"reduced squares": len(sqs), "NAE colourings": colourings, "with two fibres not constant": bad}
        print("lemma order", n, res[n], flush=True)
    return res


def random_latin(n, rng):
    while True:
        sq = [[None] * n for _ in range(n)]
        ok = True

        def fill(c):
            if c == n * n:
                return True
            i, j = divmod(c, n)
            cand = [s for s in range(n) if all(sq[i][t] != s for t in range(j)) and all(sq[t][j] != s for t in range(i))]
            rng.shuffle(cand)
            for s in cand:
                sq[i][j] = s
                if fill(c + 1):
                    return True
            sq[i][j] = None
            return False
        if fill(0):
            return sq


def lemma_sat(orders=range(6, 11), per=20, seed=7):
    rng = random.Random(seed)
    res = {}
    for n in orders:
        unsat = 0
        for _ in range(per):
            sq = random_latin(n, rng)
            x = lambda j: 1 + j
            y = lambda k: 1 + n + k
            z = lambda l: 1 + 2 * n + l
            cl = []
            for i in range(n):
                for j in range(n):
                    t = [x(i), y(j), z(sq[i][j])]
                    cl += [t, [-v for v in t]]
            cl += [[x(j) for j in range(n)], [-x(j) for j in range(n)], [y(j) for j in range(n)], [-y(j) for j in range(n)]]
            with Glucose4(bootstrap_with=cl) as so:
                unsat += not so.solve()
        res[n] = {"random squares": per, "two fibres not constant impossible (UNSAT)": unsat}
        print("lemma SAT order", n, res[n], flush=True)
    return res


LATIN2 = [[[0, 1], [1, 0]], [[1, 0], [0, 1]]]
LATIN3 = [s for s in (list(map(list, p)) for p in itertools.product(itertools.permutations(range(3)), repeat=3))
          if all(len({s[i][j] for i in range(3)}) == 3 for j in range(3))]


def nonharmony_chain(max_span=5, periods=range(4, 11), max_states=60):
    """permutive sub-stitches on one set S in not-all-equal laws that are not harmonies, and the proof's conclusion"""
    assert len(LATIN3) == 12
    tried = found2 = found3 = fails = 0
    laws = set()
    examples = []
    for span in range(2, max_span + 1):
        for S in RL.kind_sets(span, 3):
            kinds = [tuple(k) for k in S]
            for P in periods:
                full = (1 << P) - 1
                W = [w for w in range(1 << P) if all(len({(w >> (i % P)) & 1, (w >> ((i + a) % P)) & 1, (w >> ((i + b) % P)) & 1}) == 2
                                                     for a, b in kinds for i in range(P))]
                if len(W) < 2 or len(W) > max_states:
                    continue
                tried += 1
                n = len(W)
                ok = np.zeros((n, n, n), dtype=bool)
                for x in range(n):
                    for y in range(n):
                        for z in range(n):
                            ok[x, y, z] = L.stitch(W[x], W[y], W[z], kinds, P)

                def free(w, i):
                    bit = lambda t: (w >> (t % P)) & 1
                    return all(bit(o[0]) != bit(o[1]) for a, b in kinds for o in ((i + a, i + b), (i - a, i - a + b), (i - b, i - b + a)))

                def conclusion(Sset):
                    diff = [i for i in range(P) if len({(W[s] >> i) & 1 for s in Sset}) > 1]
                    return all(free(W[s], i) for s in Sset for i in diff)
                for m, squares in ((2, LATIN2), (3, LATIN3)):
                    for Sset in itertools.combinations(range(n), m):
                        for sq in squares:
                            if all(ok[Sset[i], Sset[j], Sset[sq[i][j]]] for i in range(m) for j in range(m)):
                                if m == 2:
                                    found2 += 1
                                else:
                                    found3 += 1
                                laws.add((tuple(kinds), P))
                                good = conclusion(Sset)
                                fails += not good
                                if len(examples) < 5:
                                    examples.append({"kinds": kinds, "P": P, "states": [format(W[s], f"0{P}b")[::-1] for s in Sset],
                                                     "order": m, "conclusion holds": good})
                                break
    return {"laws and periods tried": tried, "with a permutive sub-stitch": len(laws), "order-2 sets found": found2,
            "order-3 sets found": found3, "sets where the states differ at a place not free in all of them": fails, "examples": examples}


def main():
    t0 = time.time()
    out = {"rows": check_rows()}
    print(out["rows"], flush=True)
    hs = L.span8_harmonies() + [L.odd_harmony(n, S) for n, S in L.ODD_SETS]
    tot = {}
    for h in hs:
        for k, v in blocks(h).items():
            tot[k] = tot.get(k, 0) + v
    out["blocks and free pairs, 73 harmonies"] = tot
    print(tot, flush=True)
    out["lemma, exhaustive"] = lemma_exhaustive()
    out["lemma, SAT"] = lemma_sat()
    out["chain on laws that are not harmonies"] = nonharmony_chain()
    print(out["chain on laws that are not harmonies"], flush=True)
    (HERE / "result_checks.json").write_text(json.dumps(out, indent=1) + "\n")
    rows9 = span9()
    out["span 9"] = {"harmonies": len(rows9), "periods": sorted({r["P"] for r in rows9}),
                     "free sites": sum(1 for r in rows9 if r["free site"]),
                     "genuine subgroups": sum(r["genuine subgroups"] for r in rows9), "genuine cosets": sum(r["genuine cosets"] for r in rows9),
                     "Z2xZ2 blocks and cosets": sum(r["Z2xZ2 blocks"] + r["Z2xZ2 block cosets"] for r in rows9),
                     "free pairs and cosets": sum(r["free pairs"] + r["free pair cosets"] for r in rows9), "rows": rows9}
    (HERE / "result_checks.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out["span 9"].items() if k != "rows"})
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
