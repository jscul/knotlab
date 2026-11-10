"""The census of maps with three held points (research/THREE-IN-20261110-001/preregistration.md, ticket A).

For a group G (a leaf or a top-level composite) with sides s1, s2, s3, its neighbourhood N(G) is every point of every line through a side.
The floor states (every line satisfied; a Kasteleyn law has no even face) are projected onto N(G) exactly, by SAT enumeration. An
interface is three held inputs and one output, all in N(G): either the three sides held and the output another point of N(G), or two
sides and one other point held and the output any point of N(G) not held. A map is the readings at the eight input patterns (0, 1, u
undecided, x excluded), inputs in sorted order, pattern index 4a + 2b + c."""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/IN-OUT-20261110-001A/IN-OUT-20261110-001A-P001_inputs_and_outputs"))
import io_lib as I  # noqa: E402

W = I.W
PATTERNS = list(itertools.product((0, 1), repeat=3))
NEG = {"0": "1", "1": "0", "u": "u", "x": "x"}


def neighbourhood(K, ports):
    return sorted({K.pt[i][k] for i in I.near_lines(K, ports, 0) for k in range(3)})


def projection(K, s, pts):
    from pysat.solvers import Solver
    out = []
    with Solver(name="cadical153", bootstrap_with=list(K.clauses(s))) as so:
        while so.solve():
            m = so.get_model()
            row = [int(m[p] > 0) for p in pts]
            out.append(row)
            so.add_clause([-(p + 1) if v else (p + 1) for p, v in zip(pts, row)])
    return np.array(out, dtype=np.uint8).reshape(-1, len(pts))


def interfaces(ports, Np):
    """(inputs sorted, output) pairs: the three sides held, or two sides and one other point held"""
    sides = sorted(ports)
    others = [p for p in Np if p not in sides]
    out = [(tuple(sides), o) for o in others]
    for pair in itertools.combinations(sides, 2):
        for h in others:
            ins = tuple(sorted(pair + (h,)))
            for o in Np:
                if o not in ins:
                    out.append((ins, o))
    return out


def read(P, idx, ins, o):
    """the map from the projection P (rows over N(G), idx point -> column)"""
    if len(P) == 0:
        return "x" * 8
    key = P[:, idx[ins[0]]] * 4 + P[:, idx[ins[1]]] * 2 + P[:, idx[ins[2]]]
    out = P[:, idx[o]]
    m = ""
    for k in range(8):
        vals = set(out[key == k].tolist())
        m += "x" if not vals else ("u" if len(vals) == 2 else str(vals.pop()))
    return m


def self_dual(m):
    return all(m[7 - k] == NEG[m[k]] for k in range(8))


def total_type(m):
    """for a map with every reading decided: dictator, majority or parity (each up to negations), else other"""
    f = [int(c) for c in m]
    for i in range(3):
        for g in (0, 1):
            if all(f[k] == (PATTERNS[k][i] ^ g) for k in range(8)):
                return "dictator"
    for g in itertools.product((0, 1), repeat=4):
        if all(f[k] == (int(sum(PATTERNS[k][i] ^ g[i] for i in range(3)) >= 2) ^ g[3]) for k in range(8)):
            return "majority"
    for g in (0, 1):
        if all(f[k] == (sum(PATTERNS[k]) % 2) ^ g for k in range(8)):
            return "parity"
    return "other"


def non_unate(m):
    """the inputs in which the decided readings move both ways: some pair of patterns differing only there has the output rising
    with the input and another has it falling"""
    out = []
    for i in range(3):
        up = down = False
        for k in range(8):
            if PATTERNS[k][i] == 0:
                k2 = k + (4 >> i)
                a, b = m[k], m[k2]
                if a in "01" and b in "01" and a != b:
                    up |= (a, b) == ("0", "1")
                    down |= (a, b) == ("1", "0")
        if up and down:
            out.append(i)
    return out


def kind(m):
    if all(c in "01" for c in m):
        return "total " + total_type(m)
    if all(c == "x" for c in m):
        return "no floor state"
    if all(c in "ux" for c in m):
        return "never decided"
    return "partial, non-unate" if non_unate(m) else "partial, unate"
