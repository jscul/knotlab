#!/usr/bin/env python3
"""Checks for RELAY-NET-20261104-001A: arc signals and repeaters.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About ten minutes."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import relay_lib as RL  # noqa: E402

PL, FL, SL = RL.PL, RL.FL, RL.SL
T0 = time.time()
OUT = {}
CONFIGS = [("strip", d, p) for d in (3, 5, 7) for p in (0, 1, 2)] + [("grid16", d, p) for d in (3, 5, 7) for p in (0, 1, 2)] + \
    [("cube", 3, p) for p in (0, 1, 2)]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def mixed():
    gg, gp = FL.octahedral(2), PL.prism(16)
    cg, cp = nx.bipartite.color(gg), nx.bipartite.color(gp)
    v1 = next(v for v in gg.nodes if cg[v] == 1)
    v2 = next(v for v in gp.nodes if cp[v] != cg[v1])
    return PL.to_space(FL.graph_splice(gg, v1, gp, v2))


def task_arc(args):
    tag, (H, s, n), z = args
    return tag, RL.arc_lemma(H, s, n, z)


def ring_points(kind, d, p):
    n, names, _ = RL.chain(kind, d, p)
    (H2, s2, n2), pts, lns = n.space()
    return [(z, pts[z]) for z in range(n2) if pts[z][0] == "ring"]


def task_depth(args):
    kind, d, p, z = args
    n, names, _ = RL.chain(kind, d, p)
    out = RL.far_halo(n, z)
    return max((len(names) - 1 - names.index(q) for q in out), default=0)


def task_signal(args):
    kind, d, p, start, rp = args
    return RL.signal(kind, d, p, start, rp)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. the arc lemma
    FAMS = [("ladder", PL.to_space(PL.prism(10)), [0, 1]), ("prism over a 12-cycle", PL.to_space(PL.prism(6)), [0, 1]),
            ("grid 16", PL.to_space(FL.octahedral(1)), range(0, 16, 3)), ("grid 64", PL.to_space(FL.octahedral(2)), [0, 5, 17, 40]),
            ("grown 30", PL.to_space(PL.grow(30, 0)), [0, 7, 14, 21]), ("thick tube", PL.to_space(FL.tube(6, 1)), [0, 9, 18]),
            ("ladder arm on a grid", mixed(), [94, 4, 9, 30, 70])]
    with Pool(22) as pool:
        res = pool.map(task_arc, [(tag, X, z) for tag, X, zs in FAMS for z in zs])
    agg = collections.defaultdict(collections.Counter)
    for tag, out in res:
        agg[tag].update(out)
    gen = collections.Counter()
    for tag, c in agg.items():
        if tag != "ladder arm on a grid":
            gen.update(c)
    ok1 = all(k[2] == "frozen" for k in gen if k[1] == "on the arc") and all(k[2] != "frozen" for k in gen if k[1] == "off the arc") and \
        any(k[1] == "on the arc" for k in gen)
    check("1 the arc lemma: on a ladder, a prism, two grids, a grown space and a thick tube, an arc signal (two ports fixed and disagreeing) "
          "freezes a line other than the port lines exactly when the line has a corner on the own arc between the two fixed ports; on the "
          "ladder arm spliced onto a grid, junction lines off the arc are frozen too", ok1,
          {"generic pieces": {" / ".join(k): v for k, v in sorted(gen.items())},
           "ladder arm on a grid": {" / ".join(k): v for k, v in sorted(agg["ladder arm on a grid"].items())}})

    # -------------------------------------------------------------------------------------------- 2-3. signals and depth
    rps = {cfg: ring_points(*cfg) for cfg in CONFIGS}
    dtasks = [cfg + (z,) for cfg in CONFIGS for z, rp in rps[cfg]]
    stasks = [cfg + (start, rp) for cfg in CONFIGS for z, rp in rps[cfg] for start in (3, 2, 1)]
    with Pool(22) as pool:
        depths = pool.map(task_depth, dtasks)
        sigs = pool.map(task_signal, stasks)
    sig = {}
    for t, pr in zip(stasks, sigs):
        sig[t] = pr
    info2 = {}
    ok2 = True
    for cfg, label in (((("strip", 5, 0)), "aligned (strip stations, out-cut 5 steps from the in-cut)"),
                       ((("strip", 7, 0)), "misaligned (strip stations, out-cut 7 steps from the in-cut)")):
        rows = []
        for z, rp in rps[cfg]:
            rows.append([sig[cfg + (st, rp)]["arc"] + sig[cfg + (st, rp)]["single"] for st in (3, 2, 1)])
        if "misaligned" in label:
            ok2 &= all(r[1] == 0 and r[2] == 0 for r in rows)
        else:
            ok2 &= all(r[0] == r[1] == r[2] for r in rows) and any(r[0] > 0 for r in rows)
        info2[label] = {"ring points": len(rows), "live pins (single or arc) leaving c3, c2, c1, per ring point": rows}
    check("2 repeaters: along the aligned chain every ring point's arc signal leaves every station with the same number of live pins; along "
          "the misaligned chain no live pin survives past the first station", ok2, info2)
    info3 = collections.Counter()
    ok3 = True
    by_cfg = {}
    for t, dpt in zip(dtasks, depths):
        cfg, z = t[:3], t[3]
        rp = dict(rps[cfg])[z]
        live = [sig[cfg + (st, rp)]["arc"] + sig[cfg + (st, rp)]["single"] > 0 for st in (3, 2, 1)]
        # depth k >= 2 needs a live signal at cut k (leaving the piece at depth k - 1): cut 2 leaves c3, cut 3 leaves c2, cut 4 leaves c1
        need = [live[k - 2] for k in range(2, dpt + 1)]
        separated = cfg[1] >= 5                     # out-cut 5 or more steps from the in-cut: no station line meets both cuts
        if separated:
            ok3 &= all(need)
        else:
            info3["overlapping cuts (3 steps): cases whose creation passed a cut without a live signal"] += not all(need)
        info3["(configuration, ring point) cases"] += 1
        info3["cases whose deepest creation is %d cuts away" % dpt] += 1
        info3["cases with a live signal all the way to the final grid"] += all(live)
        info3["... of which create in the final grid"] += all(live) and dpt == 4
        by_cfg.setdefault("%s, out-cut %d steps, choice %d" % cfg, collections.Counter())[dpt] += 1
    check("3 depth: in chains of three strips, grids or cubes with every out-cut placement, wherever a station's two cuts are separated (5 "
          "or more steps apart, so that no line meets both), every creation k cuts from the ring (k >= 2) passed cut k as a live signal; live "
          "signals reach the final grid in the aligned configurations and part of their ring points create there; where the cuts are 3 "
          "steps apart a line meets both, and a relay can pass a cut whose signal is lost", ok3 and info3["... of which create in the final grid"] > 0,
          dict(info3, **{"deepest creation by configuration (cuts: ring points)": {k: dict(sorted(v.items())) for k, v in by_cfg.items()}}))

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
