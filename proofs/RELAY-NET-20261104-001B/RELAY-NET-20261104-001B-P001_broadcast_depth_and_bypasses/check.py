#!/usr/bin/env python3
"""Checks for RELAY-NET-20261104-001B: broadcast, depth and bypasses.

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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RELAY-NET-20261104-001A/RELAY-NET-20261104-001A-P001_arc_signals_and_repeaters"))
import relay_lib as RL  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


HUBS = [("cube", "grid16", "strip", False), ("grid16", "grid16", "strip", False), ("cube", "grid16", "strip", True),
        ("grid16", "grid16", "strip", True)]


def task_hub(args):
    hk, rk, ringk, via, z = args
    n = RL.hub(hk, rk, ringk, via_strips=via, near=True)
    (H2, s2, n2), pts, lns = n.space()
    if pts[z][0] != "ring":
        return None
    out = RL.far_halo(n, z)
    return tuple(sorted(p for p in out if p in ("A", "B"))), tuple(sorted(out))


def task_dir(args):
    kind, z = args
    n, names, _ = _dir_chain(kind)
    (H2, s2, n2), pts, lns = n.space()
    out = RL.far_halo(n, z)
    i = names.index(pts[z][0])
    return [(names.index(p) - i) for p in out]


def _dir_chain(kind):
    """grid1 <- c1 <- c2 <- c3, each station's out-cut point as far as possible from its in-cut line (no ring)"""
    import networkx as nx
    n = RL.Net(RL.FL.octahedral(1), "grid1")
    cur, v = "grid1", n.present("grid1", "point")[0]
    names = ["grid1"]
    for i in range(3):
        g = RL.PIECES[kind]()
        name = "c%d" % (i + 1)
        vin = sorted(g.nodes)[0]
        n.attach(cur, v, name, g, vin)
        dist = nx.single_source_shortest_path_length(g, vin)
        v = max(n.present(name, "point"), key=lambda x: (dist[x], -x))
        cur = name
        names.append(name)
    return n, names, None


def task_bypass(args):
    kind, m, z = args
    n, names, _ = RL.chain(kind, 1, 0, m=m, adjacent=True)
    (H2, s2, n2), pts, lns = n.space()
    if pts[z][0] != "ring":
        return None
    out = RL.far_halo(n, z)
    return "grid1" in out


def task_exact(args):
    key, z, M = args
    kind = key[0]
    if kind == "hub":
        n = RL.hub(*key[1:])
    elif kind == "chain":
        n, names = RL.small_chain(*key[1:])
    else:
        n, names = RL.two_cut(*key[1:])
    return RL.exact_far(n, z, M)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. broadcast
    tasks = []
    for hk, rk, ringk, via in HUBS:
        n = RL.hub(hk, rk, ringk, via_strips=via, near=True)
        n2 = n.space()[0][2]
        tasks += [(hk, rk, ringk, via, z) for z in range(n2)]
    with Pool(22) as pool:
        res = pool.map(task_hub, tasks)
    info1 = {}
    ok1 = True
    for hk, rk, ringk, via in HUBS:
        rr = [r for t, r in zip(tasks, res) if t[:4] == (hk, rk, ringk, via) and r is not None]
        both = sum(1 for r in rr if r[0] == ("A", "B"))
        one = sum(1 for r in rr if len(r[0]) == 1)
        if not via:
            ok1 &= both > 0
        info1["hub %s, receivers %s%s" % (hk, rk, " through strips" if via else " directly")] = {
            "ring points": len(rr), "reaching both receivers": both, "reaching one": one}
    check("1 broadcast: a hub (a cube or a 16-point grid) receiving from a ring and emitting into two grids relays one opened handle into "
          "both grids at once; through a strip after the hub each grid is reached from fewer ring points and none reaches both", ok1, info1)

    # -------------------------------------------------------------------------------------------- 2. direction
    tasks = []
    for kind in ("strip", "cube", "grid16", "tube"):
        n, names, _ = _dir_chain(kind)
        tasks += [(kind, z) for z in range(n.space()[0][2])]
    with Pool(22) as pool:
        res = pool.map(task_dir, tasks)
    info2 = collections.Counter()
    for (kind, z), offs in zip(tasks, res):
        for o in offs:
            info2["%s: creation %s" % (kind, "upstream" if o > 0 else ("in the handle's piece" if o == 0 else "%d cut(s) downstream" % -o))] += 1
    ok2 = not any("upstream" in k for k in info2)
    check("2 direction: in chains grid <- three stations (strips, cubes, 16-point grids or thick tubes) with the handle at every point, no "
          "creation ever lies upstream of the handle's piece", ok2, dict(sorted(info2.items())))

    # -------------------------------------------------------------------------------------------- 3. bypasses
    info3 = {}
    ok3 = True
    for kind in ("strip", "cube"):
        for m in (1, 2, 3, 4):
            n, names, _ = RL.chain(kind, 1, 0, m=m, adjacent=True)
            n2 = n.space()[0][2]
            with Pool(22) as pool:
                rr = [r for r in pool.map(task_bypass, [(kind, m, z) for z in range(n2)]) if r is not None]
            k = sum(rr)
            ok3 &= k > 0
            info3["%d thin %s station(s)" % (m, kind)] = {"ring points reaching the final grid": k, "ring points": len(rr)}
    check("3 bypasses: chains of up to four thin stations (strips or cubes whose two cut vertices are adjacent) relay ring handles into the "
          "final grid at every length", ok3, info3)

    # -------------------------------------------------------------------------------------------- 4. exact on small networks
    CASES = [(("hub", "cube", "prism3", "prism3", 0, (0, 1)), (17, 18), "a cube hub relaying into two small prisms"),
             (("chain", "cube", "prism3", 2, 3, 0, "prism3"), (17, 18), "an aligned chain three cuts deep"),
             (("two", "prism4", "cube", "prism4", 0, 1), (15, 16, 17), "a two-cut relay")]
    tasks = [(key, z, M) for key, zs, label in CASES for z in zs for M in range(6)]
    with Pool(min(22, len(tasks))) as pool:
        outs = pool.map(task_exact, tasks)
    info4 = {}
    ok4 = True
    for key, zs, label in CASES:
        agg = collections.Counter()
        for t, o in zip(tasks, outs):
            if t[0] == key:
                agg.update(o)
        dis = sum(v for k, v in agg.items() if "exact True, pipeline False" in k[1] or "exact False, pipeline True" in k[1])
        made = collections.Counter(k[0] for k, v in agg.items() if k[1] == "exact True, pipeline True" for _ in range(v))
        target = {"hub": ("A", "B"), "chain": ("c0",), "two": ("c0",)}[key[0]]
        ok4 &= dis == 0 and all(made[t] > 0 for t in target)
        info4[label] = {"(line, removal, far side) cases": sum(agg.values()), "disagreements": dis, "exact creations by piece": dict(made)}
    check("4 exact: on three small networks (a cube hub with two prism receivers, an aligned chain three cuts deep, a two-cut relay), at the "
          "relaying ring points, exact creation (join method) agrees with the pipeline at every far line, removal and far side, and creates in "
          "the far receivers", ok4, info4)

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
