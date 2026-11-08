"""Composition at recurring lags (RECUR-PATH-20261108-001A), on PATH-GROWTH-20261108-001A's growth_lib and NATIVE-PATH-20261108-001A's
path_lib.

In a linear path every contact's row sequence of M^T is eventually periodic, and composition is arrival: the last contact binds the
end rings exactly at the lags where it depends on both (INTERMITTENT-NET-20261108-001A), so the composing lags are fixed by the path.
analyze() gives three readings of composition:
- "every lag" (A34): every contact binds its two rings at every lag, and the last contact binds the end rings at every lag from the
  light cone on (growth_lib.native);
- "recurring, persistent": every contact binds its two rings at every lag, and the last contact binds the end rings at some lag of
  its eventual cycle, hence at lags recurring with its period;
- "recurring, binding there": the last contact binds the end rings at some lag of its eventual cycle, and at every such lag of the
  contacts' joint eventual cycle every contact binds its own two rings (INTERMITTENT-NET-20261108-001's native intermittent
  composition, for paths).
"every lag" implies "recurring, persistent", which implies "recurring, binding there"."""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PATH-GROWTH-20261108-001A/PATH-GROWTH-20261108-001A-E001_size_sweep"))
import growth_lib as G  # noqa: E402

PL = G.PL


def orbit(rows, start, cap):
    """(seq, T1, p): seq[t - 1] is the row at lag t for t = 1 .. T1 + p - 1, and lags T1 .. T1 + p - 1 form the eventual cycle; None
    when the sequence does not repeat within cap lags"""
    seen, seq, r, T = {}, [], start, 0
    tabs = None
    while T < cap:
        if T == 64:
            tabs = G._tables(rows)
        r = G._step(rows, r) if tabs is None else G._step_tab(tabs, r)
        T += 1
        if r in seen:
            return seq, seen[r], T - seen[r]
        seen[r] = T
        seq.append(r)
    return None


def row_at(o, T):
    seq, T1, p = o
    return seq[T - 1] if T - 1 < len(seq) else seq[T1 - 1 + (T - T1) % p]


def analyze(rules, sizes, ks, laws, cap=200000, joint_cap=1000000):
    """{"persist", "share", "every lag", "recurring, persistent", "recurring, binding there", "periods"}; a verdict is None when a
    row sequence (or the joint cycle) runs past its cap"""
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [PL.mask(blocks, f"R{i}") for i in range(n)]
    L = PL.light_cone(sizes, ks)
    last = n - 2
    own = [(lambda r, a=m[c], b=m[c + 1]: bool(r & a) and bool(r & b)) for c in range(n - 1)]
    ends = lambda r: bool(r & m[0]) and bool(r & m[-1])
    out = {"persist": None, "share": None, "every lag": None, "recurring, persistent": None, "recurring, binding there": None,
           "periods": None}
    o_last = orbit(rows, 1 << last, cap)
    if o_last is None:
        return out
    seq, T1, p = o_last
    cycle = [seq[T1 - 1 + j] for j in range(p)]
    share = sum(1 for r in cycle if ends(r)) / p
    out["share"] = share
    persist = all(own[last](r) for r in seq)
    if persist:
        for c in range(n - 2):
            ok = G.contact_ok(rows, 1 << c, own[c], lambda r: True, 1, cap)
            if ok is None:
                persist = None
                break
            if not ok:
                persist = False
                break
    out["persist"] = persist
    if share == 0:
        out["every lag"] = out["recurring, persistent"] = out["recurring, binding there"] = False
        return out
    if persist is None:
        return out
    # every lag from the light cone on: the lags L .. T1 - 1 before the cycle, and every phase of the cycle, all of which recur
    # after L (E001 checked only the lags L .. T1 + p - 1, which is empty when the cycle ends before L)
    out["every lag"] = bool(persist) and all(ends(row_at(o_last, T)) for T in range(L, T1)) and all(ends(r) for r in cycle)
    out["recurring, persistent"] = bool(persist)
    if persist:
        out["recurring, binding there"] = True
        return out
    orbits = []
    for c in range(n - 2):
        o = orbit(rows, 1 << c, cap)
        if o is None:
            return out
        orbits.append(o)
    orbits.append(o_last)
    out["periods"] = [o[2] for o in orbits]
    P = 1
    for o in orbits:
        P = P * o[2] // math.gcd(P, o[2])
        if P > joint_cap:
            return out
    Tstar = max(o[1] for o in orbits)
    for T in range(Tstar, Tstar + P):
        if ends(row_at(o_last, T)) and not all(own[c](row_at(orbits[c], T)) for c in range(n - 1)):
            out["recurring, binding there"] = False
            return out
    out["recurring, binding there"] = True
    return out
