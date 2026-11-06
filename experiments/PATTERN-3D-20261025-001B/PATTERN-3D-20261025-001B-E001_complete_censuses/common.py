"""Shared helpers for PATTERN-3D-20261025-001B-E001: building the census binary, decoding rules, and classifying reduced rules.
The exact law test and the groupoid recognizer come from the closed proof PATTERN-3D-20261025-001A-P001 (check.py)."""
from __future__ import annotations

import importlib.util
import itertools
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/PATTERN-3D-20261025-001B/PATTERN-3D-20261025-001B-E001_complete_censuses"
A_CHECK = ROOT / "proofs/PATTERN-3D-20261025-001A/PATTERN-3D-20261025-001A-P001_the_moves_force_a_groupoid/check.py"
_spec = importlib.util.spec_from_file_location("pattern3d_a_check", A_CHECK)
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
GCC_FLAGS = ["-O3", "-march=native"]


def build_binary() -> Path:
    d = Path(tempfile.mkdtemp(prefix="pattern3d_census_"))
    exe = d / "census"
    subprocess.run(["gcc", *GCC_FLAGS, "-o", str(exe), str(HERE / "census.c")], check=True)
    return exe


def run_census(exe: Path, mode: str, n: int, start: int, end: int):
    out = subprocess.run([str(exe), mode, str(n), str(start), str(end)], check=True, capture_output=True, text=True).stdout
    surv, stats = [], None
    for line in out.splitlines():
        if line.startswith("SURV "):
            _, i, lam, mu = line.split()
            surv.append([int(i), int(lam), int(mu)])
        elif line.startswith("STATS "):
            stats = {kv.split("=")[0]: int(kv.split("=")[1]) for kv in line.split()[1:]}
    return surv, stats


def decode_relation(index: int, n: int):
    return {(t // (n * n), (t // n) % n, t % n) for t in range(n ** 3) if index >> t & 1}


def decode_table(index: int, n: int):
    op, t = {}, index
    for a in range(n):
        for b in range(n):
            op[(a, b)] = t % n
            t //= n
    return {(a, b, z) for (a, b), z in op.items()}


def encode_table(rows):
    """rows like '0213/1302/3120/2031' -> census table index"""
    n = len(rows.split("/"))
    idx, mult = 0, 1
    for a, row in enumerate(rows.split("/")):
        for b, ch in enumerate(row):
            idx += int(ch) * mult
            mult *= n
    return idx


def encode_relation(R, n):
    return sum(1 << ((x * n + y) * n + z) for x, y, z in R)


def canon(R, n):
    best = None
    for perm in itertools.permutations(range(n)):
        for rev in (False, True):
            S = tuple(sorted(((perm[b], perm[a], perm[c]) if rev else (perm[a], perm[b], perm[c])) for a, b, c in R))
            if best is None or S < best:
                best = S
    return best


def pullback_structure(R):
    """If R is the pullback of a deterministic groupoid rule along classes of interchangeable labels, all of one size, return
    (class size, groupoid components); else None. Labels x, y are interchangeable when replacing x by y in any one place of any
    triple of R (and back) stays in R."""
    labels = sorted({l for t in R for l in t})
    def inter(x, y):
        for t in R:
            for k in range(3):
                if t[k] in (x, y):
                    u = list(t); u[k] = y if t[k] == x else x
                    if tuple(u) not in R:
                        return False
        return True
    classes = []
    for x in labels:
        for c in classes:
            if inter(c[0], x):
                c.append(x)
                break
        else:
            classes.append([x])
    cls = {x: i for i, c in enumerate(classes) for x in c}
    sizes = {len(c) for c in classes}
    Q = {(cls[a], cls[b], cls[c]) for a, b, c in R}
    if len(sizes) != 1:
        return None
    # pullback: R must contain every triple of labels whose classes form a triple of Q
    if len(R) != len(Q) * next(iter(sizes)) ** 3:
        return None
    g = A.groupoid_structure(Q)
    if g is None:
        return None
    return next(iter(sizes)), g


def classify_reduced(Rr, n, lam, mu):
    """name of the reduced rule's type, and whether it is a groupoid pullback consistent with (lam, mu)"""
    ps = pullback_structure(Rr)
    ok = False
    name = None
    if ps is not None:
        k, comps = ps
        ok = (k == lam) and all(o * g * k ** 4 == mu for o, g in comps)
        labels = sorted({l for t in Rr for l in t})
        if k > 1:
            name = f"free on {k} labels" + ("" if comps == [(1, 1)] else f" over {comps}")
        elif comps == [(1, 1)] * len(comps):
            name = {1: "one constant", 2: "two constants", 3: "three constants", 4: "four constants"}.get(len(comps),
                                                                                                       f"{len(comps)} constants")
        elif len(comps) == 1 and comps[0][0] == 1:
            order = comps[0][1]
            comp = {(a, b): c for a, b, c in Rr}
            e = next(x for x in labels if comp.get((x, x)) == x)
            invol = sum(1 for x in labels if comp.get((x, x)) == e)
            name = {2: "Z2", 3: "Z3"}.get(order) or ("Z4" if order == 4 and invol == 2 else "Z2xZ2" if order == 4 else f"group {order}")
        elif comps == [(2, 1)]:
            name = "pair groupoid"
        else:
            name = f"groupoid {comps}"
    return name, ok
