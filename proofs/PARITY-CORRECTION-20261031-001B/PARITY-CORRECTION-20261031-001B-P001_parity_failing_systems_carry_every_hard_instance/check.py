#!/usr/bin/env python3
"""Checks for PARITY-CORRECTION-20261031-001B: parity's failing systems carry every hard instance of its coupling family.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv (sympy)."""
import hashlib
import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/PARITY-CORRECTION-20261031-001A/PARITY-CORRECTION-20261031-001A-P001_parity_coupling_family_is_hard_except_at_six_points"
sys.path.insert(0, str(A_DIR))
import parity_lib as L  # noqa: E402
from parity_lib import GQ  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
a_status = json.loads((A_DIR / "result.json").read_text())["status"], json.loads((A_DIR / "manifest.json").read_text())["status"]
check("0 dependency artifacts bound by hash; ticket A Proved and passed", not bad and a_status == ("passed", "Proved"),
      {"parents": len(manifest["parent_bindings"]), "mismatched": bad, "A": a_status})

# ------------------------------------------------------------------------------------------------ 1. the piece
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
PIECE = [tuple(l) for l in census["8"]["rows"][11]["lines"]]
SIGNS = [0, 0, 0, 1, 0, 0, 0, 0]                   # one negated incidence on line 3
PORT_LINE, PORT_POINT = 0, 4                        # the incidence (q, m) = (4, line 0) is swapped with the host's
assert PIECE[PORT_LINE][0] == PORT_POINT
kb = L.kernel_basis(PIECE)
kernel = [0]
for v in kb:
    kernel += [w ^ v for w in kernel]
bmask = sum(bit << i for i, bit in enumerate(SIGNS))
certs = [s for s in kernel if L.popcount(s & bmask) % 2 == 1 and not s >> PORT_LINE & 1]
cert = min(certs)
check("1 the piece: census graph n = 8 #11, cubic, simple, connected, no repeated lines, GF(2) rank 6; with line 3 negated it is "
      "parity-unsolvable, with a certificate (lines covering every point evenly, odd number of negations) avoiding the port line 0",
      L.is_cubic(PIECE) and L.is_simple(PIECE) and L.is_connected(PIECE) and not L.has_repeated_lines(PIECE)
      and len(L.reduce_basis(L.line_masks_of_points(PIECE))) == 6 and not L.solvable(PIECE, SIGNS) and bool(certs),
      {"lines": PIECE, "negated line": PIECE[3], "port": {"line": PIECE[PORT_LINE], "point": PORT_POINT},
       "certificate (lines)": [PIECE[i] for i in range(8) if cert >> i & 1], "certificates avoiding the port line": len(certs)})

# ------------------------------------------------------------------------------------------------ 2. the transfer matrix
lam = sp.Symbol("lam")
coef = [[[0] * 9 for _ in range(2)] for _ in range(2)]   # coef[x][x'][k]: colourings with q = x' and k mismatched lines
for c in range(1 << 8):
    for xin in (0, 1):
        k = 0
        for i, l in enumerate(PIECE):
            s = SIGNS[i] + sum(xin if (i == PORT_LINE and p == PORT_POINT) else (c >> p & 1) for p in l)
            k += s & 1
        coef[xin][c >> PORT_POINT & 1][k] += 1
G = sp.Matrix(2, 2, lambda i, j: sum(cf * lam ** k for k, cf in enumerate(coef[i][j])))
det, tr = sp.factor(G.det()), sp.factor(G.trace())
roots = sorted(sp.solve(sp.Poly(G.det(), lam), lam))
check("2 transfer matrix G (host point's colour -> colour delivered to the host line): det G = -16 lam^2 (lam-1)^6 (lam+1)^6, "
      "tr G = 8 lam (lam+1)^4 (lam^2+1); det G vanishes only at lam in {0, 1, -1}",
      sp.expand(det + 16 * lam ** 2 * (lam - 1) ** 6 * (lam + 1) ** 6) == 0
      and sp.expand(tr - 8 * lam * (lam + 1) ** 4 * (lam ** 2 + 1)) == 0 and roots == [-1, 0, 1],
      {"G": [[str(sp.factor(G[i, j])) for j in range(2)] for i in range(2)], "det": str(det), "trace": str(tr)})


def G_at(v):
    return [[sum((cf * v ** k for k, cf in enumerate(coef[i][j])), 0 * v) for j in range(2)] for i in range(2)]


# ------------------------------------------------------------------------------------------------ 3. the splice
def splice(lines, signs, li, pos, k):
    """replace the incidence (lines[li][pos], line li) by a chain of k pieces: the host point enters the first piece's port line in
    place of its port point, each piece's port point enters the next piece's port line, and the last enters host line li"""
    n = L.npoints(lines)
    out, osg = [list(l) for l in lines], list(signs)
    prev = lines[li][pos]
    for t in range(k):
        off = n + 8 * t
        for i, l in enumerate(PIECE):
            out.append([prev if (i == PORT_LINE and p == PORT_POINT) else off + p for p in l])
            osg.append(SIGNS[i])
        prev = off + PORT_POINT
    out[li][pos] = prev
    return [tuple(l) for l in out], osg


def certificate_in(lines, signs, n_host, t):
    """the t-th piece's certificate, relabelled, as a line set of the spliced system"""
    start = n_host + 8 * t                          # the spliced system has n_host host lines, then 8 lines per piece
    return sum(1 << (start + i) for i in range(8) if cert >> i & 1)


FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
K43 = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
K33 = [(0, 1, 2)] * 3
rng = random.Random(20261031)
hosts = [("theta(K3,3)", L.theta(K33), None), ("theta(K4^(3))", L.theta(K43), None), ("theta(Fano)", L.theta(FANO), None),
         ("Fano", FANO, None), ("K4^(3)", K43, None)]
for row in census["6"]["rows"][:3]:
    H = [tuple(l) for l in row["lines"]]
    hosts.append((f"census n=6 {H}", H, None))
for name, H, _ in list(hosts[:4]):
    hosts.append((name + " signed", H, [rng.randint(0, 1) for _ in H]))
hosts = [(name, H, signs or [0] * len(H)) for name, H, signs in hosts]

struct_bad, struct_n = [], 0
for name, H, signs in hosts:
    for li, pos in [(0, 0), (len(H) - 1, 2)]:
        for k in (1, 2, 3):
            S, Ss = splice(H, signs, li, pos, k)
            ker_ok = all(L.popcount(certificate_in(S, Ss, len(H), t) & sum(b << i for i, b in enumerate(Ss))) % 2 == 1
                         and all(sum(1 for i in range(len(S)) if certificate_in(S, Ss, len(H), t) >> i & 1 and p in S[i]) % 2 == 0
                                 for p in range(L.npoints(S)))
                         for t in range(k))
            props = {"cubic": L.is_cubic(S), "simple": L.is_simple(S), "connected": L.is_connected(S) == L.is_connected(H),
                     "no repeated lines (when the host has none)": L.has_repeated_lines(S) <= L.has_repeated_lines(H),
                     "parity-unsolvable": not L.solvable(S, Ss), "every piece's certificate survives": ker_ok}
            struct_n += 1
            if not all(props.values()):
                struct_bad.append((name, li, pos, k, props))
check("3 every spliced system (12 hosts, plain and signed, two incidences, chains of 1-3 pieces) is cubic, simple, connected like its "
      "host, has no repeated lines when the host has none, and is parity-unsolvable with every piece's certificate intact",
      not struct_bad and struct_n == 6 * len(hosts), {"spliced systems": struct_n, "failures": struct_bad[:2]})

# ------------------------------------------------------------------------------------------------ 4. the transfer model, directly
def cut_counts(lines, signs, li, pos, v):
    """F(x, y): the host with incidence (p, line li) cut, point p coloured x, line li reading y in place of p (brute force)"""
    n = L.npoints(lines)
    p = lines[li][pos]
    F = [[0 * v, 0 * v], [0 * v, 0 * v]]
    for c in range(1 << n):
        for y in (0, 1):
            k = 0
            for i, l in enumerate(lines):
                s = signs[i] + sum(y if (i == li and j == pos) else (c >> q & 1) for j, q in enumerate(l))
                k += s & 1
            F[c >> p & 1][y] = F[c >> p & 1][y] + v ** k
    return F


model_bad, model_n = [], 0
for name, H, signs in hosts:
    if L.npoints(H) > 12:
        continue
    for v in (Fraction(2), GQ(1, 1)):
        F = cut_counts(H, signs, 0, 0, v)
        Gv = G_at(v)
        Gk = [[1 if i == j else 0 for j in range(2)] for i in range(2)]
        for k in (1, 2, 3):
            Gk = [[sum((Gk[i][m] * Gv[m][j] for m in range(2)), 0 * v) for j in range(2)] for i in range(2)]
            S, Ss = splice(H, signs, 0, 0, k)
            predicted = sum((F[i][j] * Gk[i][j] for i in range(2) for j in range(2)), 0 * v)
            model_n += 1
            if not L.m_par(S, v, Ss) == predicted:
                model_bad.append((name, L.show(v), k))
check("4 the transfer model, by direct computation: M(H_k) = sum_{x,y} F_H(x, y) G^k(x, y), with F_H from the cut host by brute force "
      "and M(H_k) by variable elimination on the spliced system (hosts up to 12 points, k = 1, 2, 3, lam = 2 and 1 + i)",
      not model_bad and model_n > 0, {"cases": model_n, "failures": model_bad[:2]})

# ------------------------------------------------------------------------------------------------ 5. the two-call formula, end to end
LAMS = [Fraction(2), Fraction(1, 3), Fraction(-2), Fraction(5, 7), GQ(1, 1), GQ(Fraction(-3, 2), Fraction(1, 2))]
e2e_bad, e2e_n, sample = [], 0, {}
for name, H, signs in hosts:
    for v in LAMS:
        Gv = G_at(v)
        trG, detG = Gv[0][0] + Gv[1][1], Gv[0][0] * Gv[1][1] - Gv[0][1] * Gv[1][0]
        S1, s1 = splice(H, signs, 0, 0, 1)
        S2, s2 = splice(H, signs, 0, 0, 2)
        m1, m2 = L.m_par(S1, v, s1), L.m_par(S2, v, s2)
        recovered = (trG * m1 - m2) / detG
        direct = L.m_par(H, v, signs)
        e2e_n += 1
        if not recovered == direct:
            e2e_bad.append((name, L.show(v), L.show(recovered), L.show(direct)))
        if name == "theta(Fano)" and v == Fraction(2):
            sample = {"M(theta Fano; 2)": L.show(direct), "M(H_1)": L.show(m1), "M(H_2)": L.show(m2)}
check("5 two calls on parity-unsolvable systems recover the count: M(H) = (tr G M(H_1) - M(H_2)) / det G on 12 hosts (theta images of "
      "K3,3, K4^(3) and Fano, Fano, K4^(3), census n = 6, and signed copies) at four real and two complex couplings",
      not e2e_bad and e2e_n == len(hosts) * len(LAMS), {"cases": e2e_n, "failures": e2e_bad[:2], "theta(Fano) at lam = 2": sample})

# ------------------------------------------------------------------------------------------------ 6. contrast: the knot's failures do not transplant
transplanted, tried = 0, 0
for n in (3, 4, 5, 6):
    for row in census[str(n)]["rows"]:
        H = [tuple(l) for l in row["lines"]]
        if L.m_nae(H, Fraction(0), L.brute) == 0:
            continue                                # host must be 2-colourable
        for (li, pos), (fl, fp) in itertools.product([(0, 0), (len(H) - 1, 1)], [(0, 0), (3, 1), (6, 2)]):
            m = L.npoints(H)
            S = [list(l) for l in H] + [[m + q for q in l] for l in FANO]
            p, q = H[li][pos], m + FANO[fl][fp]
            S[li][pos], S[len(H) + fl][fp] = q, p          # swap the incidences (p, li) and (q, Fano line fl)
            S = [tuple(l) for l in S]
            tried += 1
            transplanted += L.m_nae(S, Fraction(0), L.brute) == 0
check("6 contrast (observed): splicing the knot's failing Fano plane into a 2-colourable census host (n <= 6) at an incidence never "
      "keeps the failure: every such system is 2-colourable", transplanted == 0 and tried > 0,
      {"spliced systems": tried, "not 2-colourable": transplanted,
       "why no analogue of the two-call splice can exist for the knot": "the knot's connected failing systems are exactly the Pfaffian "
                                           "ones, on which the dimer law is a determinant; a failure-keeping splice with a recovery "
                                           "formula for every host would make perfect matchings of cubic bipartite graphs (Dagum-Luby, "
                                           "#P-complete) polynomial to count"})

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
