"""What a knot space needs to compute parity (research/PARITY-NEEDS-20261111-001/preregistration.md, ticket A).

Two families of small knot spaces, searched exactly with UNATE-20261111-001's reading (every class, every interface of three held points
and one output, all floor states enumerated):
- lattice tori (genus 1): every simple, non-degenerate triangular-lattice torus with up to MAX_TORUS points (surface_lib.hnf_sublattices);
- random knot spaces steered to a genus: UNATE's random incidence, with the rotation at each vertex changed by a seeded random walk on
  the face count until the genus is the target (a space that does not reach it in WALK steps is skipped and counted).
Each space has a time cap (SPACE_CAP seconds); a space over it is dropped by rule and counted."""
import itertools
import random
import signal
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/UNATE-20261111-001A/UNATE-20261111-001A-P001_are_maps_of_held_points_unate"))
import unate_lib as U  # noqa: E402

GL, SL = U.GL, U.SL
MAX_TORUS, WALK, SPACE_CAP = 20, 4000, 300


def faces_of(rot, partner):
    nxt = {}
    for v, ds in rot.items():
        for j, d in enumerate(ds):
            nxt[d] = ds[(j + 1) % 3]
    seen, F = set(), 0
    for d0 in (d for ds in rot.values() for d in ds):
        if d0 in seen:
            continue
        F += 1
        d = d0
        while d not in seen:
            seen.add(d)
            d = nxt[partner[d]]
    return F


def steered(n, g, seed):
    """UNATE's random incidence and rotation, then a random walk on vertex rotations toward n + 2 - 2g faces"""
    rng = random.Random(seed)
    colour, rot, partner = U.random_map(n, rng)
    target = n + 2 - 2 * g
    F = faces_of(rot, partner)
    verts = sorted(rot)
    for _ in range(WALK):
        if F == target:
            break
        v = rng.choice(verts)
        r = rot[v]
        rot[v] = [r[0], r[2], r[1]]
        F2 = faces_of(rot, partner)
        if abs(F2 - target) <= abs(F - target):
            F = F2
        else:
            rot[v] = r
    if F != target:
        return None
    S = GL.build("steered n=%d g=%d seed=%d" % (n, g, seed), colour, rot, partner)
    return S, SL.KnotSpace(S)


def tori():
    out = []
    for N in range(3, MAX_TORUS + 1):
        for t in SL.hnf_sublattices(N):
            if SL.torus_kind(*t) == "degenerate":
                continue
            S = SL.torus(*t)
            K = SL.KnotSpace(S)
            if K.simple():
                out.append((t, N))
    return out


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def read_space(K, cap=SPACE_CAP):
    """kinds of every map of three held points in every class, or None if over the time cap"""
    from collections import Counter
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    try:
        counts, first = Counter(), {}
        for ci, s in enumerate(U.all_classes(K)):
            sols = U.floor_states(K, s)
            for (tri, o), mask in U.masks(sols, K.n).items():
                k = U.kind_of(mask)
                counts[k] += 1
                if k in ("total majority", "total parity", "partial, non-unate", "total other") and k not in first:
                    first[k] = {"class index": ci, "inputs": tri, "output": o, "map": U.mask_map(mask)}
        signal.alarm(0)
        return counts, first
    except Timeout:
        return None
