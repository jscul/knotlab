"""REROUTE-20261109-001, post-hoc reading: re-routing leaves the cellular automaton itself unchanged. Each network is built cell by cell
with LOOP-NET-20261108-001A's loopnet_lib.network (rule-60 rings, law-(12, 12) contacts, g cells per contact) and its update rows with
SEPARATE-20261108-001A's net_lib.matrix. Cells are labelled without reference to rings: a contact by its id, an own cell by the dart
whose corner holds it and its offset along the corner. Two networks are the same automaton when every labelled row reads the same
labelled cells.

    .venv/bin/python3 -B same_automaton.py    writes same_automaton.json beside it
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/REROUTE-20261109-001B/REROUTE-20261109-001B-P001_rerouting_keeps_persistence"))
import reroute_lib as RR  # noqa: E402

LN = RR.P.LN
NL = LN.N


def map_of(sig):
    """a rotation system (rings -> contacts in cyclic order) and edges (contact -> its two rings, dart 2e on the first)"""
    cyc = RR.cycles(sig)
    ring_of = {d: i for i, r in enumerate(cyc) for d in r}
    rot = {i: [d >> 1 for d in r] for i, r in enumerate(cyc)}
    edges = [(ring_of[2 * e], ring_of[2 * e + 1]) for e in range(len(sig) // 2)]
    return cyc, rot, edges


def labelled_rows(sig, g):
    cyc, rot, edges = map_of(sig)
    sizes, contacts = LN.network(rot, edges, g)
    rings, n, blocks = NL.layout(sizes, contacts)
    rows, n2, _ = NL.matrix(sizes, [60] * len(sizes), contacts)
    label = {}
    for c in range(len(contacts)):
        label[c] = ("contact", c)
    for i, v in enumerate(sorted(rot, key=repr)):
        # loopnet_lib numbers rings in the order of sorted(rot, key=repr); ring v's darts in its cyclic order
        R, ds = rings[i], cyc[v]
        cpos = [j for j, b in enumerate(R) if b < len(contacts)]
        assert [R[j] for j in cpos] == [d >> 1 for d in ds], "order"
        for k, j in enumerate(cpos):
            d = ds[k]
            nxt = cpos[(k + 1) % len(cpos)]
            off = 1
            jj = (j + 1) % len(R)
            while jj != nxt:
                label[R[jj]] = ("corner", d, off)
                off += 1
                jj = (jj + 1) % len(R)
    out = {}
    for b in range(n):
        row = rows[b]
        out[label[b]] = sorted(label[x] for x in range(n) if row >> x & 1)
    return out


if __name__ == "__main__":
    rng = random.Random(7)
    res, ok = [], True
    for kind in ("square", "triangular", "honeycomb"):
        for n in (4, 6):
            sig, rot, edges, B = RR.lattice(kind, n)
            cl = RR.classes(kind, rot)
            line = {"square": (1,), "triangular": (0,), "honeycomb": (0, 1)}[kind]
            S_line = set().union(*[cl[k] for k in line])
            F = RR.face_moves(sig)
            S_rand = set()
            for _ in range(4 * n * n):
                T = S_rand.symmetric_difference(rng.choice(F))
                if RR.is_network(RR.reroute(sig, T)):
                    S_rand = T
            for g in (2, 3):
                base = labelled_rows(sig, g)
                for name, S in (("line network", S_line), ("random re-routing", S_rand)):
                    same = labelled_rows(RR.reroute(sig, S), g) == base
                    ok &= same
                    res.append({"lattice": kind, "n": n, "g": g, "re-routing": name, "same automaton": same, "cells": len(base)})
    out = {"every re-routing read is the torus's own automaton": ok, "rows": res}
    (HERE / "same_automaton.json").write_text(json.dumps(out, indent=1) + "\n")
    print(ok, len(res))
