#!/usr/bin/env python3
"""Checks for PENDANT-LINE-20261106-001B: one new line never adds creation.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). Uses up to 22 processes."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pend_lib as PL  # noqa: E402

LL = PL.LL
SL = LL.SL
CL, GL = SL.CL, SL.GL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def shapes():
    """(far side, near classes k, far columns, s, u, signs): the line's points both near (with a third class), one on the gluing line,
    or both on it; one or two far classes"""
    out = []
    for fname, F in SL.FARS:
        reps, rows = LL.far_classes(F)
        for c in reps:
            out.append((fname, 3, [c], 3, 4, (0, 0)))
            for y in range(3):
                for sg in (0, 1):
                    out.append((fname, 2, [c], y, 3, (sg, 0)))
                for y2 in range(y + 1, 3):
                    for sg in itertools.product((0, 1), repeat=2):
                        out.append((fname, 1, [c], y, y2, sg))
        for pair in itertools.combinations(reps, 2):
            out.append((fname, 2, list(pair), 3, 4, (0, 0)))
            for y in range(3):
                for sg in (0, 1):
                    out.append((fname, 1, list(pair), y, 3, (sg, 0)))
                for y2 in range(y + 1, 3):
                    for sg in itertools.product((0, 1), repeat=2):
                        out.append((fname, 0, list(pair), y, y2, sg))
    return out


def local_task(args):
    fname, k, cols, s, u, sig = args
    F = dict(SL.FARS)[fname]
    reps, rows = LL.far_classes(F)
    fr = LL.far_relation(rows, cols)
    rel = LL.near_relations(k) if k > 0 else np.array([sum(1 << (i * 1) for i in range(6))], dtype=np.uint64)
    L = PL.PendLocal(k, fr, len(cols), s, u, sig)
    tot = collections.Counter()
    step = 1 << 19
    for a in range(0, len(rel), step):
        ok, off, thr, through = PL.implication(L, rel[a:a + step])
        tot["configurations"] += int(ok.sum())
        tot["crossing knots through the new point"] += through
        tot["with every crossing knot off the new point reached"] += int((ok & off).sum())
        tot["... and one through it not reached (counterexample)"] += int((ok & off & thr).sum())
        tot["with one through it not reached (then always one off it too)"] += int((ok & thr).sum())
    return args, tot


def global_task(seed):
    r = random.Random(seed)
    if seed % 2:
        b = r.choice(sorted(GL.SP))
        H, s, n = GL.SP[b]
        M = r.randrange(len(H))
        AN = CL.solutions(H, s, n, skip=M)
    else:
        n = r.randint(7, 10)
        m = r.randint(n - 2, n + 3)
        H = [tuple(r.sample(range(n), 3)) for _ in range(m)]
        s = [[r.randint(0, 1) for _ in range(3)] for _ in range(m)]
        AN = CL.solutions(H, s, n)
    out = collections.Counter()
    if len(AN) == 0:
        return out
    s_, u_ = r.sample(range(n), 2)
    AP = SL.pendant(AN, s_, u_, (0, r.randint(0, 1), r.randint(0, 1)))
    for l in range(len(H)):
        if len(set(H[l])) < 3 or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS:
            eqW, eqC, nc, sc, thr = SL.compare_hidden(AN, AP, H, s, n, 1, l, F)
            out["cases"] += 1
            out["creation unchanged"] += eqC
            out["new knots off the point unchanged"] += eqW
            out["the side without the point creates"] += nc
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1
        total = collections.defaultdict(collections.Counter)
        for args, tot in pool.imap_unordered(local_task, shapes()):
            where = "both near" if args[3] >= 3 else ("one on the gluing line" if args[4] >= 3 else "both on the gluing line")
            total["%s, the line's points %s, %d far" % (args[0], where, len(args[2]))].update(tot)
        allc = collections.Counter()
        for c in total.values():
            allc.update(c)
        ok1 = allc["... and one through it not reached (counterexample)"] == 0 and allc["with one through it not reached (then always one off it too)"] > 0
        check("1 exhaustive local implication: on every non-degenerate local configuration (the gluing line, the new line's two points "
              "near or on the gluing line, one further class, one or two far classes of the four far sides), if every crossing knot off "
              "the new point is reached by the two-round rule, so is every crossing knot through it; configurations with an unreached "
              "knot through the new point exist, and each has an unreached knot off it", ok1,
              {"totals": dict(allc), "by shape": {k: dict(v) for k, v in sorted(total.items())}})

        # 2
        glo = collections.Counter()
        for c in pool.imap_unordered(global_task, range(1500), chunksize=4):
            glo.update(c)
        check("2 corroboration on census and random near sides with a random pendant line: creation and the new knots off the point are "
              "unchanged in every case", glo["cases"] == glo["creation unchanged"] == glo["new knots off the point unchanged"] > 0, dict(glo))

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
