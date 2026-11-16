"""The w-carry law on atom patterns (CARRY-STRANDS-20261116-001).

In a phase with forced set F, the law carries at most w open (unforced)
distinctions at once, each derivable from F in this phase.  Steps:
  begin   carry c for an atom (a, b -> c) with a, b in F;
  follow  for an atom (x, b -> c) or (b, x -> c) with b in F and x carried:
          carry c in place of x (spend x), or also keep x;
  open use taken while carried: for an atom (x, y -> c) with x, y carried,
          carry c in place of both (spend both), in place of one of them
          (keep the other), or beside both (keep both);
  release drop a carried distinction.
The spend-only law never keeps (states are multisets, so a distinction can be
derived again while another copy is carried); the keep law may keep (states
are sets: keeping is what copying would buy, as in black pebbling with
sliding).  The phase forces every distinction carried in a state reachable
from the empty state.  w = 1 is the forcing law of
SEQUENTIAL-WALL-20261116-001 under either law.  The phase's doubling rounds
are ceil(log2(1 + L)), L the largest breadth-first distance (in steps) to the
first state carrying a newly forced distinction.
"""

import math
import os
import sys
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SW = os.path.join(ROOT, "experiments", "SEQUENTIAL-WALL-20261116-001A",
                  "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")
sys.path.insert(0, SW)
import atoms as A  # noqa: E402,F401


class StateCap(Exception):
    pass


def _phase_rules(p, forced):
    a, b, c = p.a.tolist(), p.b.tolist(), p.c.tolist()
    starts, follow, joins = set(), {}, {}
    for x, y, z in zip(a, b, c):
        if forced[z]:
            continue
        fx, fy = forced[x], forced[y]
        if fx and fy:
            starts.add(z)
        elif fx:
            follow.setdefault(y, set()).add(z)
        elif fy:
            follow.setdefault(x, set()).add(z)
        else:
            key = (x, y) if x < y else (y, x)
            joins.setdefault(key, set()).add(z)
    return sorted(starts), {k: sorted(v) for k, v in follow.items()}, {k: sorted(v) for k, v in joins.items()}


def _bfs(w, keep, starts, follow, joins, max_states):
    """Breadth-first search over carried states (sorted tuples; multisets for
    the spend-only law, sets for the keep law).  Returns {distinction: first
    distance} and the number of states."""
    dist = {(): 0}
    first = {}
    q = deque([()])

    def norm(t):
        return tuple(sorted(set(t))) if keep else tuple(sorted(t))

    while q:
        M = q.popleft()
        d = dist[M]
        for v in M:
            if v not in first:
                first[v] = d
        L = len(M)
        nbrs = []
        if L < w:
            for z in starts:
                nbrs.append(norm(M + (z,)))
        for i, x in enumerate(M):
            rest = M[:i] + M[i + 1:]
            nbrs.append(rest)  # release
            for z in follow.get(x, ()):
                nbrs.append(norm(rest + (z,)))
                if keep and L < w:
                    nbrs.append(norm(M + (z,)))
        for i in range(L):
            for j in range(i + 1, L):
                x, y = M[i], M[j]
                if x == y:
                    continue
                key = (x, y) if x < y else (y, x)
                zs = joins.get(key)
                if not zs:
                    continue
                rest = tuple(M[k] for k in range(L) if k != i and k != j)
                for z in zs:
                    nbrs.append(norm(rest + (z,)))
                    if keep:
                        nbrs.append(norm(rest + (x, z)))
                        nbrs.append(norm(rest + (y, z)))
                        if L < w:
                            nbrs.append(norm(M + (z,)))
        for N in nbrs:
            if N not in dist:
                dist[N] = d + 1
                if len(dist) > max_states:
                    raise StateCap(len(dist))
                q.append(N)
    return first, len(dist)


def carried_phases(p, w, keep=True, max_states=5_000_000):
    """Phases of the w-carry law (keep or spend-only).  Returns a dict with the forced mask,
    each distinction's phase, P, the per-phase largest distance L_t, the
    doubling rounds T and the states visited."""
    forced = p.held.copy().tolist()
    phase = [0 if f else -1 for f in forced]
    t = 0
    Ls, states = [], 0
    while True:
        starts, follow, joins = _phase_rules(p, forced)
        first, ns = _bfs(w, keep, starts, follow, joins, max_states)
        states += ns
        new = [v for v in first if not forced[v]]
        if not new:
            break
        t += 1
        Ls.append(max(first[v] for v in new))
        for v in new:
            forced[v] = True
            phase[v] = t
    T = sum(int(math.ceil(math.log2(1 + L))) for L in Ls)
    return {"forced": np.array(forced), "phase": np.array(phase), "P": t, "L": Ls, "T": T, "states": states}
