"""RING-LAW-20261109-001B-E001: laws that see their rings, on the lattice tori (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/RING-LAW-20261109-001B/RING-LAW-20261109-001B-E001_laws_on_tori/run/result.json

Networks: square, triangular and honeycomb n x n tori (n = 4, 5, 6) at g = 2 and their line networks (REROUTE-20261109-001B), every
contact's law (u, v) with u on the ring through dart 2c. Translations act on both networks, so one contact of each class stands for
all; rings are read in full. Readings (RING-LAW-20261109-001A's ring_law_lib): R1, for all 256 laws, whether the representative
contacts bind both their rings at every lag (affine laws, exactly by the row orbit) or to lag HB (nonlinear laws, by SAT, stopping at
the first lag that fails); R2, for the laws of SELECTED, whether they need both rings at every lag to H; R3, for the same laws, whether
every ring's plain first need comes at its light-cone lag for every representative contact. R2 and R3 take a pair of sampled first rows
differing only in a ring's cells as a witness of needing, and decide every lag not witnessed by SAT, so both are exact."""
import collections
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RING-LAW-20261109-001A/RING-LAW-20261109-001A-P001_which_laws_see_rings"))
import ring_law_lib as L  # noqa: E402

RR = L.RR
OUT = ROOT / "artifacts" / "RING-LAW-20261109-001B" / "RING-LAW-20261109-001B-E001_laws_on_tori" / "run"
KINDS = ("square", "triangular", "honeycomb")
SIZES = (4, 5, 6)
GROUPINGS = ("torus", "lines")
LINE = {"square": (1,), "triangular": (0,), "honeycomb": (0, 1)}
LAWS = [(u, v) for u in range(16) for v in range(16)]
SELECTED = [(12, 12)] + [(w, w) for w in (1, 2, 4, 7, 8, 11, 13, 14)]
HB, H, W, SEED = 6, 64, 4, 20261114


def network(kind, n, grouping):
    sig, rot, edges, B = RR.lattice(kind, n)
    S = set() if grouping == "torus" else set().union(*[RR.classes(kind, rot)[k] for k in LINE[kind]])
    reps = list(rot[((0, 0), 0)] if kind == "honeycomb" else rot[(0, 0)][:len(rot[(0, 0)]) // 2])
    return RR.reroute(sig, S), reps


def r1(args):
    kind, n, grouping, law = args
    sig, reps = network(kind, n, grouping)
    net = L.Net(sig, 2, law)
    k = L.classify(law)
    if k["affine"]:
        res = [net.affine_persistence(c) for c in reps]
        return args, "binds at every lag" if all(res) else ("undecided" if None in res else "fails")
    for T in range(1, HB + 1):
        for c in reps:
            if not all(L.binds_exactly(net, c, X, T) for X in net.contact_rings(c)):
                return args, "fails at lag %d" % T
    return args, "binds to lag %d" % HB


def r23(args):
    kind, n, grouping, law = args
    sig, reps = network(kind, n, grouping)
    net = L.Net(sig, 2, law)
    rng = np.random.default_rng(SEED + 1000 * KINDS.index(kind) + 10 * n + GROUPINGS.index(grouping))
    rings = range(len(net.rings))
    cones = {X: net.light_cone(X) for X in rings}
    horizon = max(H, max(max(c.values()) for c in cones.values()))
    witnessed = {X: net.witnessed_needs(X, horizon, W, rng) for X in rings}
    sat_calls = 0
    # R2: every representative contact needs both its rings at every lag to H
    r2_fail = []
    for c in reps:
        for X in net.contact_rings(c):
            for T in range(1, H + 1):
                if T not in witnessed[X][c]:
                    sat_calls += 1
                    if not L.needs_exactly(net, c, X, T):
                        r2_fail.append((c, X, T))
    # R3: the plain first need of every ring for every representative contact
    late, pairs = [], 0
    for X in rings:
        for c in reps:
            if c in net.ring_cells(X):
                continue
            d = cones[X].get(c)
            pairs += 1
            if d is None:
                late.append((X, c, None))
                continue
            if d not in witnessed[X][c]:
                sat_calls += 1
                if not L.needs_exactly(net, c, X, d):
                    late.append((X, c, d))
    return args, {"needs both rings at every lag to %d" % H: not r2_fail, "first failures": r2_fail[:5],
                  "(ring, contact) pairs": pairs, "late": len(late), "late examples": late[:5], "SAT calls": sat_calls}


def main():
    t0 = time.time()
    nets = [(k, n, gr) for k in KINDS for n in SIZES for gr in GROUPINGS]
    with Pool(16) as pool:
        b1 = dict(pool.map(r1, [net + (law,) for net in nets for law in LAWS], chunksize=8))
        b23 = dict(pool.map(r23, sorted([net + (law,) for net in nets for law in SELECTED], key=lambda a: -a[1]), chunksize=1))
    table, seeing_binders = {}, []
    for net in nets:
        cnt = collections.Counter()
        for law in LAWS:
            k = L.classify(law)
            cls = ("affine" if k["affine"] else "nonlinear") + (", sees the routing" if k["sees the routing"] else ", blind") + \
                  (", both rings pass" if k["both rings pass"] else ", a ring cut")
            v = b1[net + (law,)]
            cnt[(cls, v)] += 1
            if k["sees the routing"] and v.startswith("binds"):
                seeing_binders.append([*net, list(law), v])
        table["%s %d %s" % net] = {"%s: %s" % key: m for key, m in sorted(cnt.items())}
    plain = {"%s %d %s %s" % (*net, law): b23[net + (law,)] for net in nets for law in SELECTED}
    sel_nl = [law for law in SELECTED if not L.classify(law)["affine"]]
    h1 = not seeing_binders
    h2 = all(b23[net + (law,)]["needs both rings at every lag to %d" % H] for net in nets for law in sel_nl)
    h3 = all(b23[net + (law,)]["late"] == 0 for net in nets for law in sel_nl)
    control = {"%s %d %s" % net: b23[net + ((12, 12),)]["late"] for net in nets}
    result = {"experiment": "RING-LAW-20261109-001B-E001",
              "H1 no law that sees the routing binds both rings at every lag read": h1,
              "H2 the eight symmetric nonlinear laws need both rings at every lag to 64": h2,
              "H3 under them every torus and line network read is on time": h3,
              "laws that see the routing and bind": seeing_binders, "control (12, 12): late (ring, contact) pairs": control,
              "binding by class of law": table, "needing and the plain reading": plain, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("binding by class of law", "needing and the plain reading")}, indent=1))


if __name__ == "__main__":
    main()
