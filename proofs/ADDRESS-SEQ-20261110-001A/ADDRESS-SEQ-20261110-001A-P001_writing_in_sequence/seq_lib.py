"""Shared pieces for ADDRESS-SEQ-20261110-001: the frozen targeted search from any start, the learner M1, and the address readout."""
import heapq
import importlib.util
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AD = load("addr", "proofs/ADDRESS-20261110-001A/ADDRESS-20261110-001A-P001_a_learned_address_among_three_atoms/check.py")
C = load("rise", "proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py")
LH = load("holds", "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py")
LL = load("layers", "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py")
L = load("steer", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
ST, SL = LL.ST, LL.SL
CAP = 300000


def bits(v, n):
    return [(v >> i) & 1 for i in range(n)]


def acting(K, Y, s_int, n_atoms):
    s = bits(s_int, 3 * K.n)
    return tuple(j for j in range(n_atoms) if LH.atom_role(K, Y, s, j) == "line")


def search_from(Y, K, P, start, named, n_atoms, levels):
    """ADDRESS-20261110-001A's targeted search with its target rule, from the configuration start = (law bits, state bits)"""
    floor2 = abs(K.chi)
    Z = K.classes()
    want = ["line" if j in named else "transparent" for j in range(n_atoms)]
    s_start = bits(start[0], 3 * K.n)
    target = None
    for a in itertools.product((0, 1), repeat=len(Z)):
        s = list(s_start)
        for ai, z in zip(a, Z):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        if [LH.atom_role(K, Y, s, j) for j in range(n_atoms)] != want:
            continue
        faces = [[v for v in range(K.V) if levels[v] == "atom %d" % j and K.d[v] >= 3] for j in sorted(named)]
        for combo in itertools.product(*faces):
            xm = AD.floor_model(LH, K, s, set(combo))
            if xm is not None:
                target = (sum(b << e for e, b in enumerate(s)), sum(b << p for p, b in enumerate(xm)))
                break
        if target:
            break
    if target is None:
        return None, 0

    def h(s, x):
        return bin(s ^ target[0]).count("1") + bin(x ^ target[1]).count("1")

    def done(ag):
        return all(any(ag[v] >= 3 and levels[v] == "atom %d" % j for v in range(K.V)) for j in named)
    prev, heap, tick = {start: None}, [(h(*start), 0, start)], 0
    while heap and len(prev) < CAP:
        _, _, (s, x) = heapq.heappop(heap)
        vi, ag, w = P.full(s, x)
        if w == floor2 and done(ag):
            return (s, x), len(prev)
        for kind, t, y, w2 in P.neighbours(s, x, vi, ag, w):
            if w2 <= floor2 + 4 and (t, y) not in prev:
                prev[(t, y)] = 1
                tick += 1
                heapq.heappush(heap, (h(t, y), tick, (t, y)))
    return None, len(prev)


def m1(P, s, x, floor2, rng, rounds=200):
    """ADDRESS-STEER-20261110-001C's learner: a random move lowering W, else keeping it, until the floor"""
    for _ in range(rounds):
        vi, ag, w = P.full(s, x)
        if w == floor2:
            break
        nb = P.neighbours(s, x, vi, ag, w)
        pick = [m for m in nb if m[3] < w] or [m for m in nb if m[3] == w]
        if not pick:
            break
        _, s, x, _ = rng.choice(pick)
    return s, x, P.full(s, x)[2]


def space(kk, l0, dists):
    S = SL.octahedral_sphere(kk)
    sph = L.Sphere(S, f"K_{kk}")
    dist = ST.G.line_distance(S, l0)
    lines = [l0] + [min(t for t, dd in dist.items() if dd == d) for d in dists]
    Y = LL.Layered(S, sph.s0, sph.flat_state(sph.K.lines.index(l0)))
    for l in lines:
        Y.grow(l)
    Y.learn(4)
    return Y
