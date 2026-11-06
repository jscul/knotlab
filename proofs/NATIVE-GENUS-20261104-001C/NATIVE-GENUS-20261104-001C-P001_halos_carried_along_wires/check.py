#!/usr/bin/env python3
"""Checks for NATIVE-GENUS-20261104-001C: halos carried along wires.

Two atoms on plane networks whose pieces are joined by a rigid strip or a hub (the RELAY-NET constructions). Atom X sits at a point whose
opened halo is relayed into a far piece; atom Y sits in that piece. Each atom's halo (the base-side lines where its removals create) is
computed with that atom alone (exact); the whole space is computed exactly where it has at most 26 points.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes. About two hours."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001A/NATIVE-GENUS-20261104-001A-P001_the_creation_map_splits_by_atom"))
import genus_lib as GL  # noqa: E402

SL, RL = GL.RL.SL, GL.RL
T0 = time.time()
OUT = {}
ID = (0, 1, 2)
F = GL.FANO
g = lambda i: ("g", i)  # noqa: E731


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def dumbbell(size):
    """two 4-point cubes joined by a rigid strip from a ring over a 2*size-cycle (STRIP-RELAY C): grid1 is split at a point and receives"""
    h, part, v1, v3 = SL.dumbbell(GL.PL.prism(size), 0, 0, False)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    return GL.base(H2, s2, n2), [part[pts[q]] for q in range(n2)], [part[lns[k]] for k in range(len(H2))]


def hubnet():
    """a cube hub relaying into two small prisms A and B (RELAY-NET B), with the ring"""
    n = RL.hub("cube", "prism3", "prism3", 0, (0, 1))
    (H2, s2, n2), pts, lns = n.space()
    return GL.base(H2, s2, n2), [pts[q][0] for q in range(n2)], [lns[k][0] for k in range(len(H2))]


def halo(S, res, atom):
    """base-side line keys where the atom's removals create"""
    return sorted({S.lkey[L] for M, row in res.items() if S.owner[M] == atom for L, v in row.items()
                   if v and any(v) and S.owner[L] is None}, key=str)


def cut_lines(S, atom):
    """base-side line keys holding a point of the atom (an emitter's cut lines)"""
    return sorted({S.lkey[k] for k, L in enumerate(S.H) if S.owner[k] is None and any(S.pkey[q][0] == atom for q in L)}, key=str)


def ports_lines(S, atom):
    """base-side line keys through the base points that the atom's lines hold (a receiver's ports)"""
    pts = {q for k, L in enumerate(S.H) if S.owner[k] == atom for q in L if S.pkey[q][0] == "g"}
    return sorted({S.lkey[k] for k, L in enumerate(S.H) if S.owner[k] is None and set(L) & pts}, key=str)


def touching(S):
    """atoms whose cuts share an edge: a line of one atom holding a point of another"""
    pown = [k[0] if k[0] != "g" else None for k in S.pkey]
    return sorted({tuple(sorted((S.owner[k], pown[q]))) for k, L in enumerate(S.H) if S.owner[k] is not None for q in L
                   if pown[q] is not None and pown[q] != S.owner[k]})


def region_count(keys, lreg_by_key):
    return dict(collections.Counter(lreg_by_key[k] for k in keys))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # ---------------------------------------------------------------------------------------- 1. a rigid strip, exact
        S0, preg, lreg = dumbbell(4)
        lreg_by_key = {S0.lkey[k]: lreg[k] for k in range(len(S0.H))}
        relays = {}
        for q in range(S0.n):
            SX = GL.build((S0, [("X", "point", g(q), F, 0, ID)]))
            relays["%d (%s)" % (q, preg[q])] = region_count(halo(SX, GL.matrix(SX, pool=pool), "X"), lreg_by_key)
        z = 10
        DX = (S0, [("X", "point", g(z), F, 0, ID)])
        SX = GL.build(DX)
        rX = GL.matrix(SX, pool=pool)
        hX = halo(SX, rX, "X")
        info1 = {"plane points": S0.n, "halo of a lone atom at each point, by piece": relays, "X at": (z, preg[z]),
                 "X's halo by piece": region_count(hX, lreg_by_key)}
        ok1 = preg[z] == "grid2" and any(lreg_by_key[k] == "grid1" for k in hX)
        cases = [("point", q) for q in range(S0.n) if preg[q] in ("grid1", "grid2") and q != z] + \
                [("line", k) for k in range(len(S0.H)) if lreg[k] in ("grid1", "grid2")]
        rows = []
        for kind, pos in cases:
            DY = (S0, [("Y", kind, g(pos), F, 0, ID)])
            SY = GL.build(DY)
            rY = GL.matrix(SY, pool=pool)
            hY = halo(SY, rY, "Y")
            DXY = (S0, [("X", "point", g(z), F, 0, ID), ("Y", kind, g(pos), F, 0, ID)])
            S = GL.build(DXY)
            assert len(GL.CL.solutions(S.H, S.s, S.n)) == 0
            r = GL.matrix(S, procs=8)  # 26 points: a smaller pool, since each removal holds a large solution set
            nat = GL.native(S, r)
            pown = [k[0] for k in S.pkey]
            pieces = sorted(sorted({pown[q] for q in piece}) for piece in nat["interior pieces"])
            near = cut_lines(SY, "Y") if kind == "point" else ports_lines(SY, "Y")
            row = {"Y": "%s at %s %d (%s)" % ("emitter" if kind == "point" else "receiver", kind, pos, preg[pos] if kind == "point" else lreg[pos]),
                   "points": S.n, "touching": touching(S), "genus": GL.sat_genus(S), "counts": nat["counts"], "quiet parts": nat["quiet parts"],
                   "pieces by atom": pieces,
                   "X's halo meets Y's cut or ports": len(set(hX) & set(near)), "X's halo meets Y's halo": len(set(hX) & set(hY)),
                   "halos in the whole space equal the halos alone": halo(S, r, "X") == [k for k in hX if k in S.lkey] and
                   halo(S, r, "Y") == [k for k in hY if k in S.lkey]}
            rows.append(row)
        info1["second atom"] = rows
        overl = [r for r in rows if r["X's halo meets Y's cut or ports"] or r["X's halo meets Y's halo"]]
        ok1 &= all(r["genus"] == 2 for r in rows) and all(r["halos in the whole space equal the halos alone"] for r in rows)
        info1["placements where the halos overlap"] = len(overl)
        sep = [r for r in rows if not r["touching"]]
        good = [r for r in sep if len(r["counts"]) == 1 and r["counts"][0][1] == 2 and r["pieces by atom"] == [["X"], ["Y"]]]
        info1["separated placements"] = len(sep)
        info1["separated placements counted 2 through interior points, one piece per atom"] = len(good)
        ok1 &= len(overl) > 0 and len(good) == len(sep)
        check("1 a rigid strip: atom X in the far cube, whose halo crosses the strip into the near cube; a second atom Y at every other point "
              "and line of both cubes; exact on the whole space (26 points)", ok1, info1)

        # ---------------------------------------------------------------------------------------- 2. a hub, by the splitting lemma
        S0, preg, lreg = hubnet()
        lreg_by_key = {S0.lkey[k]: lreg[k] for k in range(len(S0.H))}
        info2, landings = {"plane points": S0.n}, 0
        for z in [q for q in range(S0.n) if preg[q] == "ring"]:
            SX = GL.build((S0, [("X", "point", g(z), F, 0, ID)]))
            hX = halo(SX, GL.matrix(SX, pool=pool), "X")
            land = sorted({S0.line(k) for k in hX if lreg_by_key[k] in ("A", "B")})
            ys = []
            for pos in sorted({q for k in land for q in S0.H[k] if preg[q] in ("A", "B")}):
                SY = GL.build((S0, [("Y", "point", g(pos), F, 0, ID)]))
                rY = GL.matrix(SY, pool=pool)
                meet = len(set(hX) & set(cut_lines(SY, "Y")))
                landings += meet > 0
                ys.append({"Y at point": "%d (%s)" % (pos, preg[pos]), "X's halo meets Y's cut": meet,
                           "Y's halo by piece": region_count(halo(SY, rY, "Y"), lreg_by_key)})
            info2["X at ring point %d" % z] = {"X's halo by piece": region_count(hX, lreg_by_key), "Y where it lands": ys}
        info2["placements where X's halo meets Y's cut"] = landings
        check("2 a hub: an opened atom X at each ring point; where its halo crosses the hub into a receiver, a second atom Y at each receiver "
              "point it reaches (each atom alone, exact; the whole space, 31 points, follows by the splitting lemma)", landings > 0, info2)

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
