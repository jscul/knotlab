"""SLOW-LOOP-R1 task 1c: the full driver run_slow (under test) on small planted instances, checked by brute force.

Policies: GO as frozen (policies.json), GO with random targets (RNDO), GO with shadow knots (beta 0.5), ST (static), and
an extreme eager one (epoch 0.2 n, slow budget 20 times the fast work, every target followed by 4 shadow probes,
probe budget 10^5). Fast loop: Novelty+ at the primary cell's re-tuned setting (0.75, 0.1), and at two deliberately
weak settings ((0, 0), probSAT with cb = 0, a random walk, and cb = -2, which prefers high-break flips) so that, at small n, the search lasts past the first
epochs and the slow loop moves. Checks by the referee's oracle: the reported state satisfies every original knot; no
contradiction; with debug, every final (root, parity) and shadow knot holds on the original allowed set A, and the
final reduced pattern lifted is A one for one. Output: referee_task1c_runslow.json.
"""
from __future__ import annotations

import collections
import json
import os
import signal
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
ART = os.path.join(ROOT, "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
sys.path.insert(0, HERE)
import referee_task1_soundness as T1  # noqa: E402  (sets the path to the study's code and the build dir)
import numpy as np  # noqa: E402

import referee_oracle as O  # noqa: E402

S = T1.S
POLS = json.load(open(os.path.join(ART, "policies.json")))
POLICIES = {
    "GO": dict(POLS["GO"]),
    "RNDO": dict(POLS["GO"], mode=1),
    "GO_shadow": dict(POLS["GO"], beta=0.5),
    "ST": dict(POLS["ST"]),
    "EXTREME": {"e": 0.2, "rho": 20.0, "beta": 1.0, "J": 4, "pb": 100000, "backoff": False, "mode": 0},
}
FAST = {"nov_cell": ("novelty_plus", (0.75, 0.1)), "nov_greedy": ("novelty_plus", (0.0, 0.0)),
        "walk": ("probsat_poly", (0.0, 1.0)), "anti": ("probsat_poly", (-2.0, 1.0))}


def work_one(cfg):
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(3)
    try:
        inst = T1.make_instance(cfg)
    except TimeoutError:
        return {"skipped": 1}
    finally:
        signal.alarm(0)
    A = O.allowed(inst.n, inst.knots)
    out = collections.Counter()
    viol = []
    for pname, pol in POLICIES.items():
        for fname, (algo, prm) in FAST.items():
            for r in range(2):
                seed = cfg["seed"] * 10 + r
                res = S.run_slow(inst, algo, prm, seed, 10**6, pol, static=(pname == "ST"), debug=True)
                key = f"{pname}|{fname}"
                out[key + "|runs"] += 1
                out[key + "|with_rebuild"] += int(res["rebuilds"] > 0)
                out[key + "|moves"] += int(np.sum(res["root"] != np.arange(inst.n))) + len(res["shadow_list"])
                out[key + "|solved"] += int(res["solved"])
                if res["contradiction"]:
                    viol.append({"what": "contradiction", "policy": key, "cfg": cfg, "seed": seed})
                if res["solved"]:
                    ok = bool(O.sat_rows(res["state"], inst.knots)[0])
                    out[key + "|state_checked"] += 1
                    if not ok:
                        viol.append({"what": "reported state violates an original knot", "policy": key, "cfg": cfg,
                                     "seed": seed, "state": res["state"].tolist()})
                    if ok != bool(res["verified"]):
                        viol.append({"what": "engine's own verification disagrees", "policy": key, "cfg": cfg})
                root, rpar = res["root"], res["rpar"]
                if np.any((A ^ A[:, root]) != rpar[None, :]):
                    viol.append({"what": "final tie fails on A", "policy": key, "cfg": cfg, "seed": seed})
                for sh in res["shadow_list"]:
                    if O.shadow_witness(A, *sh) is not None:
                        viol.append({"what": "shadow fails on A", "policy": key, "cfg": cfg, "seed": seed,
                                     "shadow": list(sh)})
                out["shadows_checked"] += len(res["shadow_list"])
                roots = res["roots"]
                col = np.full(inst.n, -1, dtype=np.int64)
                col[roots] = np.arange(len(roots))
                kv = res["kv"]
                B = O.allowed(len(roots), col[kv] if len(kv) else np.zeros((0, 3), np.int64), res["ks"])
                Lf = O.lift(B, roots, root, rpar)
                out["bijection_checked"] += 1
                if O.as_set(Lf) != O.as_set(A) or len(B) != len(A):
                    viol.append({"what": "final reduced pattern not one-for-one with A", "policy": key, "cfg": cfg,
                                 "seed": seed, "nA": len(A), "nB": len(B)})
    return {"counts": dict(out), "violations": viol}


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    S.lib()
    cfgs = T1.draw_configs(N, seed=77)
    for c in cfgs:
        c["seed"] += 1_000_000
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(8) as pool:
        rs = pool.map(work_one, cfgs, chunksize=2)
    tot = collections.Counter()
    viol = []
    skipped = 0
    for r in rs:
        if "skipped" in r:
            skipped += 1
            continue
        tot.update(r["counts"])
        viol += r["violations"]
    out = {"instances": N, "skipped_generator": skipped, "counts": dict(sorted(tot.items())),
           "violations": len(viol), "violation_examples": viol[:20], "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(HERE, "referee_task1c_runslow.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
