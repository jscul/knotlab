#!/usr/bin/env python3
"""Checks for PERIODIC-READ-20261111-001B-P001: the two-class lemma and the global hollow triples of OVERLAP-READ-20261111-001.

The lemma: if the knots of a pattern split into two classes A and B, every co-knotted pair in exactly one knot of each, then A, B and
A u B have the same states (OVERLAP-READ's L5: same pair counts, same states). The six-regular one-pair weaves Z^2/L split so, into
the knots {x, x+(1,0), x+(1,1)} and {x, x+(0,1), x+(1,1)}.

  C1. The lemma on every six-regular one-pair weave with 12 to 24 distinctions (brute force): states(A) = states(B) = states(A u B).
  G1. Registered: in each of OVERLAP-READ's 98 swap-made bases whose added sets are forced only by the whole base, every such added set
      is a knot of the source weave that the swaps removed.
  G2. Registered: where every removed source knot lies in one class, the other class's knots (all still present) force each of them.
  M.  Measured: for the rest, whether the other class's remaining knots together with the swapped-in knots force it.
  C2. Mutation: a random half of the knots in place of the other class does not force them (so G2 can fail).

Usage: check.py [--write]   (the workspace .venv, from the repository root)
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "OVERLAP-READ-20261111-001A" / "OVERLAP-READ-20261111-001A-E001_emergence_census"))
import census as c  # noqa: E402  (OVERLAP-READ's frozen census: its recipe for the swap-made bases and its readers)

import tempfile  # noqa: E402

ka = c.ka
c.OUT = tempfile.mkdtemp(prefix="periodic-read-b-")   # the census's log goes to a temporary folder, not beside this file


def classes(a, b, cc):
    def red(x, y):
        q, x0 = divmod(x, a)
        return x0, (y - q * b) % cc
    idx = {(x, y): x * cc + y for x in range(a) for y in range(cc)}
    up = {tuple(sorted(idx[red(*p)] for p in ((x, y), (x + 1, y), (x + 1, y + 1)))) for x in range(a) for y in range(cc)}
    down = {tuple(sorted(idx[red(*p)] for p in ((x, y), (x, y + 1), (x + 1, y + 1)))) for x in range(a) for y in range(cc)}
    return up, down


def c1():
    tested = bad = 0
    for V in range(12, 25):
        for a in range(1, V + 1):
            if V % a:
                continue
            cc = V // a
            for b in range(cc):
                r = ka.lattice_torus_with_coords(a, b, cc)
                if r is None:
                    continue
                up, down = classes(a, b, cc)
                sa = set(ka.all_states(V, sorted(up), ka.LAWS["NAE"]).tolist())
                sb = set(ka.all_states(V, sorted(down), ka.LAWS["NAE"]).tolist())
                sw = set(ka.all_states(V, r[1], ka.LAWS["NAE"]).tolist())
                tested += 1
                bad += not (sa == sb == sw)
    return {"weaves": tested, "violations": bad}


def main():
    out = {"C1": c1()}
    tori = c.ns_faithful_tori(c.NS_V)
    index = {(t["V"], tuple(t["lattice"])): i for i, t in enumerate(tori)}
    g = json.load(open(ROOT / "research" / "OVERLAP-READ-20261111-001" / "global_obstructions.json"))
    glob = [r for r in g["part 2"] if r["global"]]
    rows = []
    for f in glob:
        n = index[(f["V"], tuple(f["torus"]))]
        tor = tori[n]
        a, b, cc = tor["lattice"]
        up, down = classes(a, b, cc)
        src = {tuple(sorted(t)) for t in tor["T"]}
        W = c.ns_swap_worlds(tor["V"], [tuple(t) for t in tor["T"]], f["swaps"], seed=c.NS_SEED + 1000 * n + 10 * f["swaps"] + f["rep"])
        Ws = {tuple(sorted(t)) for t in W}
        removed, added = src - Ws, Ws - src
        V = tor["V"]
        bb = c.SatBase(V, W)
        fr, ti, ex, na = bb.emergent()
        bb.close()
        glob_sets = [S for S in fr + ti + ex
                     if not any(c.forced(V, c.ball_knots(W, S, r), S) and len(c.ball_knots(W, S, r)) < len(W) for r in range(1, 10))]
        one_class = removed <= up or removed <= down
        rec = {"V": V, "torus": tor["lattice"], "swaps": f["swaps"], "rep": f["rep"], "global sets": len(glob_sets),
               "removed": len(removed), "removed in one class": one_class, "G1": all(tuple(S) in removed for S in glob_sets)}
        if one_class:
            other = down if removed <= up else up
            rec["G2"] = all(c.forced(V, sorted(other), S) for S in glob_sets if tuple(S) in removed)
            rng = random.Random(V + f["rep"])
            half = rng.sample(sorted(Ws), len(other))
            rec["mutation forces all"] = all(c.forced(V, half, S) for S in glob_sets if tuple(S) in removed)
        else:
            rec["other class remaining plus swapped-in forces"] = all(
                c.forced(V, sorted(((down if S in up else up) & Ws) | added), S) for S in [tuple(x) for x in glob_sets] if S in removed)
        rows.append(rec)
        print(rec, flush=True)
    out["rows"] = rows
    out["G1"] = {"bases": len(rows), "holds on": sum(r["G1"] for r in rows), "holds": all(r["G1"] for r in rows)}
    g2 = [r for r in rows if r["removed in one class"]]
    out["G2"] = {"bases with removed knots in one class": len(g2), "holds on": sum(r["G2"] for r in g2), "holds": all(r["G2"] for r in g2)}
    rest = [r for r in rows if not r["removed in one class"]]
    out["M"] = {"bases with removed knots in both classes": len(rest),
                "forced by the other class's remaining knots and the swapped-in knots": sum(r["other class remaining plus swapped-in forces"] for r in rest)}
    out["C2"] = {"mutations that force everything": sum(r["mutation forces all"] for r in g2), "holds": not all(r["mutation forces all"] for r in g2) if g2 else False}
    out["C1"]["holds"] = out["C1"]["violations"] == 0
    out["failures"] = [k for k in ("C1", "G1", "G2", "C2") if not out[k]["holds"]]
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not out["failures"] else "failed", "claim": manifest["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
