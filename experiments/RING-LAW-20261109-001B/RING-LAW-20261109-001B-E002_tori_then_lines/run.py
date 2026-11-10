"""RING-LAW-20261109-001B-E002: laws that see their rings, on the lattice tori and their line networks (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/RING-LAW-20261109-001B/RING-LAW-20261109-001B-E002_tori_then_lines/run/result.json

E001's readings with E001's library and code, in a feasible order: R2 and R3 first on all 18 networks, then R1 on the nine tori and on
the line networks of n = 4 and 5 (E001 was stopped for cost while reading R1 on the line networks; see contract.json). Every finished
reading is also appended to partial.jsonl as it arrives.

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
OUT = ROOT / "artifacts" / "RING-LAW-20261109-001B" / "RING-LAW-20261109-001B-E002_tori_then_lines" / "run"
LINE_SIZES_R1 = (4, 5)
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


def timed_r1(args):
    t = time.time()
    key, val = r1(args)
    return key, (val, time.time() - t)


def timed_r23(args):
    t = time.time()
    key, val = r23(args)
    return key, (val, time.time() - t)


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    nets = [(k, n, gr) for k in KINDS for n in SIZES for gr in GROUPINGS]
    log = open(OUT / "progress.txt", "w")
    part = open(OUT / "partial.jsonl", "w")
    b1, b23 = {}, {}
    nets1 = [net for net in nets if net[2] == "torus" or net[1] in LINE_SIZES_R1]
    with Pool(16) as pool:
        for i, (key, val) in enumerate(pool.imap_unordered(timed_r23, sorted([net + (law,) for net in nets for law in SELECTED], key=lambda a: -a[1]), chunksize=1)):
            b23[key] = val[0]
            print(json.dumps({"reading": "R2 R3", "key": key, "value": val[0], "seconds": round(val[1], 1)}), file=part, flush=True)
            print("r23", i, key, round(val[1]), {k: v for k, v in val[0].items() if "examples" not in k}, round(time.time() - t0), file=log, flush=True)
        r1_jobs = sorted([net + (law,) for net in nets1 for law in LAWS], key=lambda a: (a[2] != "torus", a[1]))
        for i, (key, val) in enumerate(pool.imap_unordered(timed_r1, r1_jobs, chunksize=4)):
            b1[key] = val[0]
            print(json.dumps({"reading": "R1", "key": key, "value": val[0], "seconds": round(val[1], 1)}), file=part, flush=True)
            if val[1] > 30 or i % 500 == 0:
                print("r1", i, key, val, round(time.time() - t0), file=log, flush=True)
    table, seeing_binders = {}, []
    for net in nets1:
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
    passing = lambda law: L.classify(law)["both rings pass"]
    h1 = not [r for r in seeing_binders if r[2] == "torus"]
    h2 = any(r[0] == "square" and r[2] == "lines" and passing(tuple(r[3])) for r in seeing_binders) and \
        not [r for r in seeing_binders if r[0] != "square" and r[2] == "lines" and passing(tuple(r[3]))]
    h3 = all(b23[net + (law,)]["needs both rings at every lag to %d" % H] for net in nets for law in sel_nl)
    h4 = all(b23[net + (law,)]["late"] == 0 for net in nets for law in sel_nl)
    control = {"%s %d %s" % net: b23[net + ((12, 12),)]["late"] for net in nets}
    result = {"experiment": "RING-LAW-20261109-001B-E002",
              "H1 on no torus does a law that sees the routing bind both rings at every lag read": h1,
              "H2 on the square line networks some law that sees the routing with both rings passing binds to lag 6, on the others none": h2,
              "H3 the eight symmetric nonlinear laws need both rings at every lag to 64": h3,
              "H4 under them every torus and line network read is on time": h4,
              "laws that see the routing and bind": seeing_binders, "control (12, 12): late (ring, contact) pairs": control,
              "binding by class of law": table, "needing and the plain reading": plain, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("binding by class of law", "needing and the plain reading")}, indent=1))


if __name__ == "__main__":
    main()
