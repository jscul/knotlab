"""Fixtures, test groups and calibration constants of CLASSK-DICHOTOMY-20261026-001B-E001 (shared by predict.py and run.py).

Characters are exponents of the generator Z of mu_r(F_p) used by ck_lib (the smallest element of order r): Z = 3 for
(p, r) = (7, 6) and Z = 2 for (5, 4); the fixtures use the same zeta.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def find_root():
    for parent in [HERE] + list(HERE.parents):
        if (parent / "proofs" / "CLASSK-DICHOTOMY-20261026-001A").exists():
            return parent
    return Path("/home/jscul/p-vs-np-contact-first")


ROOT = find_root()
LIBA = next((ROOT / "proofs/CLASSK-DICHOTOMY-20261026-001A").glob("CLASSK-DICHOTOMY-20261026-001A-P001_*"))
sys.path.insert(0, str(LIBA))
import ck_lib as L  # noqa: E402  (read-only: class-(K) groups, gadget models, template counts, the bilinear counter)

FIELDS = {(7, 6): 3, (5, 4): 2}

# fixture: (p, r, slot exponents (normalized), knots per role, graph name, n, gadget edges, summand roles, fixture edges)
FIXTURES = {
    "P1-K2": (7, 6, (1, 2, 3), {"x": "3_1", "y": "6_1", "t": "5_2"}, "K2", 2, [(0, 1)],
              ["x", "x", "y", "t"], [(0, 1, 2, 3)]),
    "P1-digon": (7, 6, (1, 2, 3), {"x": "3_1", "y": "6_1", "t": "5_2"}, "digon", 2, [(0, 1), (0, 1)],
                 ["x", "x", "y", "y", "t", "t"], [(0, 1, 2, 4), (0, 1, 3, 5)]),
    "P1-K2+K2": (7, 6, (1, 2, 3), {"x": "3_1", "y": "6_1", "t": "5_2"}, "K2+K2", 4, [(0, 1), (2, 3)],
                 ["x", "x", "x", "x", "y", "t", "y", "t"], [(0, 1, 4, 5), (2, 3, 6, 7)]),
    "P2-K2": (7, 6, (1, 1, 4), {"x": "3_1", "y": "3_1", "t": "6_1"}, "K2", 2, [(0, 1)],
              ["x", "x", "y", "t"], [(0, 1, 2, 3)]),
    "P2-digon": (7, 6, (1, 1, 4), {"x": "3_1", "y": "3_1", "t": "6_1"}, "digon", 2, [(0, 1), (0, 1)],
                 ["x", "x", "y", "y", "t", "t"], [(0, 1, 2, 4), (0, 1, 3, 5)]),
    "P3-K2": (7, 6, (2, 2, 2), {"x": "6_1", "y": "6_1", "t": "6_1"}, "K2", 2, [(0, 1)],
              ["x", "x", "y", "t"], [(0, 1, 2, 3)]),
    "P3-digon": (7, 6, (2, 2, 2), {"x": "6_1", "y": "6_1", "t": "6_1"}, "digon", 2, [(0, 1), (0, 1)],
                 ["x", "x", "y", "y", "t", "t"], [(0, 1, 2, 4), (0, 1, 3, 5)]),
    "P2-K2 at p=5": (5, 4, (1, 1, 2), {"x": "6_1", "y": "6_1", "t": "4_1"}, "K2", 2, [(0, 1)],
                     ["x", "x", "y", "t"], [(0, 1, 2, 3)]),
}


def group(p, r, bexp, pairs):
    """class-(K) group with B exponents bexp and one A coordinate per listed commutator pair (i, i2), beta(e_i, e_i2) = 1"""
    aexp, beta = [], {}
    for (i, i2) in pairs:
        aexp.append((bexp[i] + bexp[i2]) % r)
        beta[(i, i2, len(aexp) - 1)] = 1
    return L.KGroup(p, r, bexp, aexp, beta)


GROUPS = {
    (7, 6): {
        "free class 2 on characters (3, 2, 6)": ([1, 2, 3], [(0, 1), (0, 2), (1, 2)]),
        "two hard sectors (3, 2, 6, 4, 5)": ([1, 2, 3, 4, 5], [(0, 1), (0, 2), (1, 2), (4, 3)]),
        "trivial-character commutators (1, 3, 2, 6)": ([0, 1, 2, 3], [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3)]),
        "free class 2 on characters (3, 3, 4)": ([1, 1, 4], [(0, 1), (0, 2), (1, 2)]),
        "pattern 2 with a trivial character (1, 3, 3, 4)": ([0, 1, 1, 4], [(1, 2), (1, 3), (2, 3), (0, 1), (0, 3)]),
        "free class 2 on three coordinates of character 2": ([2, 2, 2], [(0, 1), (0, 2), (1, 2)]),
        "Heisenberg (2, 2)": ([2, 2], [(0, 1)]),
        "pattern 3 with a trivial character (1, 2, 2)": ([0, 2, 2], [(0, 1), (1, 2), (0, 2)]),
    },
    (5, 4): {
        "Heisenberg alpha = beta = 2": ([1, 1], [(0, 1)]),
        "Heisenberg (2, 4), gamma = alpha": ([1, 2], [(0, 1)]),
        "free class 2 on characters (2, 2, 4)": ([1, 1, 2], [(0, 1), (0, 2), (1, 2)]),
        "with a trivial character (1, 2, 2, 4)": ([0, 1, 1, 2], [(1, 2), (1, 3), (2, 3), (0, 1), (0, 3)]),
    },
}

# u-pairing calibration on single twist-knot exteriors (pre-registered from scoping/upair.py; re-measured in the run):
# is u u v nonzero in H^2(X; F_tau) for v in H^1(X; F_tau)?  keyed by (p, knot, exponent of tau)
CALIBRATION = {
    (7, "3_1", 1): True, (7, "3_1", 5): True, (7, "6_1", 2): True, (7, "6_1", 4): True, (7, "5_2", 3): False,
    (5, "6_1", 1): True, (5, "6_1", 3): True, (5, "4_1", 2): False,
}


# fixture-group pairs not evaluated, decided from model sizes alone before the freeze (template enumeration about 4e7 or more,
# or an obstruction cover of p^8 or more variables): pattern 3 with three coordinates in one regraded slot character
EXCLUDE = {
    (f, g) for f in ("P3-K2", "P3-digon")
    for g in ("free class 2 on characters (3, 3, 4)", "pattern 2 with a trivial character (1, 3, 3, 4)",
              "free class 2 on three coordinates of character 2")
}


def all_groups(p, r):
    return {name: group(p, r, bexp, pairs) for name, (bexp, pairs) in GROUPS[(p, r)].items()}


def groups_for(fname):
    p, r = FIXTURES[fname][0], FIXTURES[fname][1]
    return {name: G for name, G in all_groups(p, r).items() if (fname, name) not in EXCLUDE}
