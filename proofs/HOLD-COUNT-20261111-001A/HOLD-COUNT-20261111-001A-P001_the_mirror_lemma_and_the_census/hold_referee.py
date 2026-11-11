#!/usr/bin/env python3
"""Referee (hold_referee.py) for HOLD-COUNT-20261111-001A (research/HOLD-COUNT-20261111-001/preregistration.md), fresh code.

It imports nothing from the learning line or from hold_lib: it reads only spaces.json (each space's lines and the signing of every
class, written by check.py --part export) and result.json (the census summary), and checks three things.

R1. The mirror lemma's combinatorial core, exhaustively: for n = 1..8 held points, moduli m = 2..6 with n >= m - 1, and codes of
    k = 1..3 output points, a map e from residues mod m to k-bit codes with e((n - c) mod m) = NOT e(c mod m) for every count
    c = 0..n exists exactly when m is even and n is odd, and then an injective one exists exactly when 2^k >= m.
R2. The lemma's hypothesis on every space: on every class, the set of states satisfying every line (not-all-equal on its signed
    literals) is closed under flipping every point. With R1 this gives P0 on every space.
R3. Each least instance the census reports (P1, P2 and the other kinds) is recomputed from the space's lines: the held pattern is total,
    the output points are decided, and they hold the stated count."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def r1():
    bad = []
    for n in range(1, 9):
        for m in range(2, 7):
            if n < m - 1:
                continue
            for k in range(1, 4):
                full = (1 << k) - 1
                any_e = inj_e = False
                for e in itertools.product(range(1 << k), repeat=m):
                    if all(e[(n - c) % m] == e[c % m] ^ full for c in range(n + 1)):
                        any_e = True
                        if len(set(e)) == m:
                            inj_e = True
                            break
                want_any = (m % 2 == 0) and (n % 2 == 1)
                want_inj = want_any and (1 << k) >= m
                if any_e != want_any or inj_e != want_inj:
                    bad.append({"n": n, "m": m, "k": k, "exists": any_e, "injective exists": inj_e})
    return {"cases": sum(1 for n in range(1, 9) for m in range(2, 7) if n >= m - 1) * 3, "disagreements": bad}


def floor(space, signs):
    n = space["n"]
    x = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for i, pts in enumerate(space["lines"]):
        v = [((x >> p) & 1) ^ signs[3 * i + j] for j, p in enumerate(pts)]
        ok &= ~((v[0] == v[1]) & (v[1] == v[2]))
    return x[ok]


def r2(spaces):
    failures, classes = [], 0
    for sp in spaces:
        full = (1 << sp["n"]) - 1
        for ci, s in enumerate(sp["classes"]):
            states = floor(sp, s)
            classes += 1
            if not np.array_equal(np.sort(states ^ full), states):
                failures.append((sp["label"], ci))
    return {"spaces": len(spaces), "classes": classes, "not closed under flipping every point": failures}


def reading(states, held, ref, outs):
    """None if a held pattern is missing or an output undecided, else the outputs' values at each of the 8 patterns"""
    if ref is not None:
        states = states[((states >> ref) & 1) == 0]
    vals = {}
    for x in states.tolist():
        k = sum(((x >> p) & 1) << (2 - i) for i, p in enumerate(held))
        v = tuple((x >> o) & 1 for o in outs)
        if vals.setdefault(k, v) != v:
            return None
    return vals if len(vals) == 8 else None


def holds(vals, m):
    for eps in range(8):
        res = {k: bin(k ^ eps).count("1") % m for k in range(8)}
        if all((res[a] == res[b]) == (vals[a] == vals[b]) for a in range(8) for b in range(a)):
            return True
    return False


def r3(spaces, summary):
    by_label = {sp["label"]: sp for sp in spaces}
    rows = []
    for kind, info in sorted(summary["least"].items()):
        if info is None:
            continue
        inst = info["first instance"]
        sp = by_label[info["label"]]
        states = floor(sp, sp["classes"][inst["class index"]])
        held, ref = tuple(inst["held"]), inst.get("reference")
        outs = inst["out"] if isinstance(inst.get("out"), list) else ([inst["out"]] if "out" in inst else None)
        if kind.startswith("parity"):
            if outs is None:
                # a parity reading with a reference: find the point
                cand = [o for o in range(sp["n"]) if o not in held and o != ref]
                ok = False
                for o in cand:
                    v = reading(states, held, ref, [o])
                    if v and all(v[k][0] == (bin(k).count("1") & 1) ^ v[0][0] for k in range(8)):
                        ok = True
                        break
            else:
                v = reading(states, held, ref, outs)
                ok = bool(v) and all(v[k][0] == (bin(k).count("1") & 1) ^ v[0][0] for k in range(8))
        elif kind.startswith("majority"):
            v = reading(states, held, ref, outs)
            ok = bool(v) and any(all(v[k][0] == (int(bin(k ^ e).count("1") >= 2)) for k in range(8)) for e in range(8))
        elif kind.startswith("full adder"):
            v = reading(states, held, ref, outs)
            ok = bool(v) and holds(v, 4)
        else:
            m = int(kind.split()[1].rstrip(","))
            v = reading(states, held, ref, outs)
            ok = bool(v) and holds(v, m)
        rows.append({"kind": kind, "label": info["label"], "confirmed": ok})
    return rows


def main():
    spaces = json.loads((HERE / "spaces.json").read_text())["spaces"]
    summary = json.loads((HERE / "result.json").read_text())["checks"]["result"]
    out = {"R1 the lemma's core": r1(), "R2 closed under flipping every point": r2(spaces), "R3 least instances": r3(spaces, summary)}
    out["passed"] = (not out["R1 the lemma's core"]["disagreements"]
                     and not out["R2 closed under flipping every point"]["not closed under flipping every point"]
                     and all(r["confirmed"] for r in out["R3 least instances"]))
    (HERE / "referee.json").write_text(json.dumps(out, indent=1) + "\n")
    print("referee passed" if out["passed"] else "referee FAILED")
    sys.exit(0 if out["passed"] else 1)


if __name__ == "__main__":
    main()
