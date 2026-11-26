"""Exact sparse fermion engine for one round of one-parent births of a parity knot.

Distinctions are modes. Old distinction j is mode j; child j's fresh distinctions y_j, z_j are modes n + 2j and n + 2j + 1. A
state is a pair of arrays (basis, amplitude): basis is an occupation bit mask (bit m set = mode m holds 1), amplitudes are small
Gaussian integers stored as complex numbers, so every sum here is exact. A listing is the order in which modes are written down
(the literature's Jordan-Wigner order); creators and annihilators pick up (-1) for every occupied mode listed before them.

Nothing here imports the predecessor's code or its referee's.
"""

from fractions import Fraction
from itertools import combinations, permutations, product

import numpy as np


class Modes:
    def __init__(self, n, listing=None):
        self.n = n
        self.M = 3 * n
        listing = list(range(self.M)) if listing is None else list(listing)
        assert sorted(listing) == list(range(self.M))
        rank = {m: i for i, m in enumerate(listing)}
        # before[m]: bit mask of the modes listed before m
        self.before = [sum(1 << k for k in range(self.M) if rank[k] < rank[m]) for m in range(self.M)]
        self.parity = np.zeros(1 << self.M, dtype=np.int8)
        for v in range(1, 1 << self.M):
            self.parity[v] = self.parity[v >> 1] ^ (v & 1)

    def x(self, j):
        return j

    def y(self, j):
        return self.n + 2 * j

    def z(self, j):
        return self.n + 2 * j + 1

    def sign(self, basis, m):
        return 1 - 2 * self.parity[basis & self.before[m]].astype(np.int64)


def state(basis, amp):
    return (np.asarray(basis, dtype=np.int64), np.asarray(amp, dtype=complex))


def empty():
    return state([], [])


def join(*parts):
    return (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]))


def simplify(psi):
    """Merge repeated basis states and drop zeros."""
    b, a = psi
    if len(b) == 0:
        return psi
    u, inv = np.unique(b, return_inverse=True)
    out = np.zeros(len(u), dtype=complex)
    np.add.at(out, inv, a)
    keep = out != 0
    return u[keep], out[keep]


def create(F, m, psi):
    b, a = psi
    bit = 1 << m
    ok = (b & bit) == 0
    b, a = b[ok], a[ok]
    return b | bit, a * F.sign(b, m)


def annihilate(F, m, psi):
    b, a = psi
    bit = 1 << m
    ok = (b & bit) != 0
    b, a = b[ok], a[ok]
    return b ^ bit, a * F.sign(b, m)


def scale(psi, c):
    return psi[0], psi[1] * c


def add(*parts):
    return simplify(join(*parts))


def gamma(F, m, psi):
    """c + c+ (a Majorana operator): flips mode m with its listing sign."""
    return add(annihilate(F, m, psi), create(F, m, psi))


def gamma_p(F, m, psi):
    """i (c+ - c)."""
    return add(scale(create(F, m, psi), 1j), scale(annihilate(F, m, psi), -1j))


def number_split(psi, m):
    b, a = psi
    bit = 1 << m
    on = (b & bit) != 0
    return (b[~on], a[~on]), (b[on], a[on])


def birth(F, j, psi, pair="yz"):
    """K_j = (1 - n_x)(1 + c+_A c+_B) + n_x (c+_y + c+_z); pair "yz" writes c+_y c+_z (c+_z acts first)."""
    x, y, z = F.x(j), F.y(j), F.z(j)
    empty_parent, full_parent = number_split(psi, x)
    first, second = (z, y) if pair == "yz" else (y, z)
    both = create(F, second, create(F, first, empty_parent))
    return add(empty_parent, both, create(F, y, full_parent), create(F, z, full_parent))


def flip(F, kind, j, psi, record="y"):
    """Reader j's flip on its old distinction and its record: F1 = -i g'_x g_r, F2 = i g_x g'_r, F3 = i g_x g_r."""
    x = F.x(j)
    r = F.y(j) if record == "y" else F.z(j)
    if kind == "F1":
        return scale(gamma_p(F, x, gamma(F, r, psi)), -1j)
    if kind == "F2":
        return scale(gamma(F, x, gamma_p(F, r, psi)), 1j)
    if kind == "F3":
        return scale(gamma(F, x, gamma(F, r, psi)), 1j)
    raise ValueError(kind)


def zread(F, j, psi):
    b, a = psi
    on = (b >> F.x(j)) & 1
    return b, a * (1 - 2 * on)


def inner(phi, psi):
    """<phi|psi>, exact."""
    pb, pa = phi
    qb, qa = psi
    common, i, k = np.intersect1d(pb, qb, assume_unique=True, return_indices=True)
    return complex(np.sum(np.conj(pa[i]) * qa[k]))


def exact(value, norm):
    re, im = value.real, value.imag
    assert abs(im) < 1e-9 and abs(re - round(re)) < 1e-9, value
    return Fraction(int(round(re)), norm)


def vacuum():
    return state([0], [1])


def start(F, order, signs=None):
    """The positive parity knot created in the given order (order[0] first); with signs, sum_x h(x) c+_{i1}...c+_{ik}|0>
    with i1 < ... < ik instead."""
    n = F.n
    parts = []
    for word in product((0, 1), repeat=n):
        if sum(word) % 2:
            continue
        v = vacuum()
        if signs is None:
            for k in order:
                if word[k]:
                    v = create(F, F.x(k), v)
        else:
            for k in sorted(range(n), reverse=True):
                if word[k]:
                    v = create(F, F.x(k), v)
            v = scale(v, signs[word])
        parts.append(v)
    return add(*parts)


def grow(F, psi, commit, pairs=None):
    for j in commit:
        psi = birth(F, j, psi, pairs[j] if pairs else "yz")
    return psi


def scheduled(F, schedule, pairs=None):
    """A schedule of 2n events ('c', j) and ('b', j): creation of old distinction j (if it holds 1) and birth of child j."""
    n = F.n
    parts = []
    for word in product((0, 1), repeat=n):
        if sum(word) % 2:
            continue
        v = vacuum()
        for kind, j in schedule:
            if kind == "c":
                if word[j]:
                    v = create(F, F.x(j), v)
            else:
                v = birth(F, j, v, pairs[j] if pairs else "yz")
        parts.append(v)
    return add(*parts)


class Readers:
    def __init__(self, F, kinds, records=None):
        self.F = F
        self.kinds = kinds
        self.records = records or ["y"] * F.n

    def apply(self, letters, psi):
        """letters: one of 'I', 'Z', 'F' per reader."""
        for j, letter in enumerate(letters):
            if letter == "Z":
                psi = zread(self.F, j, psi)
            elif letter == "F":
                psi = flip(self.F, self.kinds[j], j, psi, self.records[j])
        return psi


def norm_of(psi):
    return exact(inner(psi, psi), 1).numerator


def expectations(psi, readers, words):
    nrm = norm_of(psi)
    return {w: exact(inner(psi, readers.apply(w, psi)), nrm) for w in words}


def even_sets(n):
    return [frozenset(c) for k in range(0, n + 1, 2) for c in combinations(range(n), k)]


def corr_word(n, T):
    return "".join("F" if j in T else "Z" for j in range(n))


def correlations(psi, readers):
    n = readers.F.n
    words = {T: corr_word(n, T) for T in even_sets(n)}
    e = expectations(psi, readers, set(words.values()))
    return {T: e[w] for T, w in words.items()}


def full_contradiction(c):
    sets = list(c)
    if not all(abs(v) == 1 for v in c.values()):
        return False
    f = {T: c[T] / c[frozenset()] for T in sets}
    character = all(f[T ^ U] == f[T] * f[U] for T in sets for U in sets)
    return not character


def all_words(n):
    return ["".join(w) for w in product("IZF", repeat=n)]


# ---------------------------------------------------------------- the n-reader target, in an n-place qubit model

def target_expectations(n, signs=None):
    """Reversal-signed n-knot, amplitude (-1)^C(|x|,2) on even words, read with Z and X; returns E(word) for words in IZF
    (F standing for X)."""
    words = [w for w in product((0, 1), repeat=n) if sum(w) % 2 == 0]
    amp = {w: (-1) ** (sum(w) * (sum(w) - 1) // 2) if signs is None else signs[w] for w in words}
    out = {}
    for letters in all_words(n):
        total = 0
        for w in words:
            v = list(w)
            ph = 1
            for j, letter in enumerate(letters):
                if letter == "Z" and v[j]:
                    ph = -ph
            for j, letter in enumerate(letters):
                if letter == "F":
                    v[j] ^= 1
            total += amp[w] * ph * amp.get(tuple(v), 0)
        out[letters] = Fraction(total, len(words))
    return out


def matches(e_fock, e_target, relabel=frozenset()):
    """Same table after relabelling the X outcomes of the readers in relabel."""
    for w, v in e_target.items():
        k = sum(1 for j in relabel if w[j] == "F")
        if e_fock[w] != (-1) ** k * v:
            return False
    return True


def relabellings_matching(e_fock, e_target, n):
    return [R for k in range(n + 1) for R in map(frozenset, combinations(range(n), k))
            if matches(e_fock, e_target, R)]


# ---------------------------------------------------------------- orders and relations

def cyclic_shifts(order):
    return [tuple(order[k:]) + tuple(order[:k]) for k in range(len(order))]


def crossing(schedule, n):
    pos = {}
    for i, ev in enumerate(schedule):
        pos[ev] = i
    rel = set()
    for i, j in combinations(range(n), 2):
        a, b = pos[("c", i)], pos[("b", i)]
        c, d = pos[("c", j)], pos[("b", j)]
        if a < c < b < d or c < a < d < b:
            rel.add((i, j))
    return rel


def is_cut(rel, n):
    """rel (pairs i < j) is the set of pairs across a split of the readers into two groups (possibly one empty)."""
    side = [0] + [1 if (0, j) in rel else 0 for j in range(1, n)]
    return all(((i, j) in rel) == (side[i] != side[j]) for i, j in combinations(range(n), 2))


def complete(n):
    return set(combinations(range(n), 2))


def schedules(n):
    """Every sequence of the 2n events with each creation before its own birth."""
    out = []

    def rec(seq, started, done):
        if len(seq) == 2 * n:
            out.append(tuple(seq))
            return
        for j in range(n):
            if j not in started:
                rec(seq + [("c", j)], started | {j}, done)
            elif j not in done:
                rec(seq + [("b", j)], started, done | {j})

    rec([], frozenset(), frozenset())
    return out


def round_schedule(sigma, pi):
    return tuple([("c", j) for j in sigma] + [("b", j) for j in pi])


def depth_first(sigma):
    return tuple(ev for j in sigma for ev in (("c", j), ("b", j)))
