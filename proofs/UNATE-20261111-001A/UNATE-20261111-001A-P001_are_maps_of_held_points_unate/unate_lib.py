"""Are maps of held points unate (research/UNATE-20261111-001/preregistration.md, ticket A).

Two exact searches for a map of three held points that is not unate:
- the census of THREE-IN-20261110-001 on the deeper spaces of DEEP-MEM-20261111-001, and at radius 2 on S1;
- random small knot spaces: a random 3-regular bipartite incidence of n points and n lines (every line on three distinct points), a
  random rotation at every vertex, built into a 2-coloured triangulation of an orientable surface by grow_lib.build, with its Kasteleyn
  law and every class. All floor states are enumerated by brute force, and every interface (three held points, one output point, all
  distinct) is read from them at once: a 16-bit mask of which (input pattern, output value) pairs occur."""
import itertools
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(next((ROOT / "proofs/GROW-HANDLE-20261110-001A").glob("*/"))))
sys.path.insert(0, str(ROOT / "proofs/THREE-IN-20261110-001A/THREE-IN-20261110-001A-P001_maps_of_three_held_points"))
import grow_lib as GL  # noqa: E402
import census_lib as C  # noqa: E402

SL = GL.SL


def random_map(n, rng):
    """a random 3-regular bipartite incidence with every line on three distinct points, and a random rotation at every vertex"""
    while True:
        stubs = [p for p in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        if all(len({stubs[3 * l + k] for k in range(3)}) == 3 for l in range(n)):
            break
    colour = {("L", l): 1 for l in range(n)}
    colour.update({("P", p): 0 for p in range(n)})
    partner, used = {}, {p: 0 for p in range(n)}
    for l in range(n):
        for k in range(3):
            p = stubs[3 * l + k]
            j = used[p]
            used[p] += 1
            partner[("L", l, k)] = ("P", p, j)
            partner[("P", p, j)] = ("L", l, k)
    rot = {}
    for v in sorted(colour):
        order = [0, 1, 2] if rng.random() < 0.5 else [0, 2, 1]
        rot[v] = [v + (k,) for k in order]
    return colour, rot, partner


def space(n, seed):
    rng = random.Random(seed)
    S = GL.build("random n=%d seed=%d" % (n, seed), *random_map(n, rng))
    K = SL.KnotSpace(S)
    return S, K


def all_classes(K):
    s0 = K.signing()
    Z = K.classes()
    out = []
    for a in itertools.product((0, 1), repeat=len(Z)):
        s = list(s0)
        for ai, z in zip(a, Z):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        out.append(s)
    return out


STATES = {}


def floor_states(K, s):
    """every assignment satisfying every line (NAE on its signed literals), by brute force"""
    n = K.n
    if n not in STATES:
        STATES[n] = ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.uint8)
    X = STATES[n]
    ok = np.ones(len(X), dtype=bool)
    for i in range(n):
        L = [X[:, K.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
        ok &= ~((L[0] == L[1]) & (L[1] == L[2]))
    return X[ok]


def masks(sols, n):
    """for every (sorted input triple, output) the 16-bit mask of occurring (pattern, value) pairs: bit 2*(4a+2b+c) + o"""
    out = {}
    if len(sols) == 0:
        return out
    cols = sols.astype(np.int64)
    for tri in itertools.combinations(range(n), 3):
        key = cols[:, tri[0]] * 4 + cols[:, tri[1]] * 2 + cols[:, tri[2]]
        for o in range(n):
            if o in tri:
                continue
            code = key * 2 + cols[:, o]
            out[(tri, o)] = int(np.bitwise_or.reduce(np.left_shift(1, code)))
    return out


KIND = {}


def mask_map(mask):
    m = ""
    for k in range(8):
        h0, h1 = (mask >> (2 * k)) & 1, (mask >> (2 * k + 1)) & 1
        m += "x" if not (h0 or h1) else ("u" if h0 and h1 else ("1" if h1 else "0"))
    return m


def kind_of(mask):
    if mask not in KIND:
        KIND[mask] = C.kind(mask_map(mask))
    return KIND[mask]
