"""SLOW-LOOP-R1 task 2: a slow arm's fast loop runs exactly as Novelty+ alone until its first move.

(a) From the stored runs (test/, stress/, posthoc/ results.jsonl): every slow-arm run that made no rebuild must have
    the same flips, solved flag and fast work as NOV's run with the same instance and run index (both use
    run_seed(stage, cell, seed, r)). Runs with rebuilds are counted but cannot be compared from the data.
(b) Fresh runs (the study's run_slow under test, policies from policies.json, the cell's re-tuned Novelty+): the run is
    stopped at its first rebuild by wrapping slow_loop.reduce_pattern; the state the driver has read back at that
    moment (x at every distinction, last-flip times, fast RNG state, step counter t, flips, fast work) is compared with
    Novelty+ alone (the study's handle and fl_run, as run_fast does) capped at the same number of flips.
Output: referee_task2_identity.json.
"""
from __future__ import annotations

import collections
import ctypes
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
EXP = os.path.join(ROOT, "experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
ART = os.path.join(ROOT, "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
os.environ.setdefault("SLOW_LOOP_BUILD",
                      "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build")
sys.path.insert(0, EXP)
import numpy as np  # noqa: E402

import slow_loop as S  # noqa: E402  (under test)

CELLS = {  # (family, density, window, n, cap) as in job.py
    "local-w10-3200": ("local", 4.0, 10, 3200, 2 * 10**8), "local-w40-3200": ("local", 4.0, 40, 3200, 2 * 10**8),
    "rand-3200": ("rand", 2.1, 10, 3200, 2 * 10**8), "block-3200": ("block", 2.5, 20, 3200, 2 * 10**8),
    "local-w10-800": ("local", 4.0, 10, 800, 2 * 10**7), "local-w40-800": ("local", 4.0, 40, 800, 2 * 10**7),
    "rand-800": ("rand", 2.1, 10, 800, 2 * 10**7), "block-800": ("block", 2.5, 20, 800, 2 * 10**7),
    "embed-3200": ("embed", 0.0, 10, 3200, 2 * 10**8), "embed-800": ("embed", 0.0, 10, 800, 2 * 10**7)}
EMBED = {"frac": 0.25, "alpha_r": 2.1, "alpha_l": 4.0, "alpha_c": 0.02, "w": 10}


def part_a():
    out = {}
    for stage in ("test", "stress", "posthoc"):
        nov = {}
        rows = []
        for line in open(os.path.join(ART, stage, "results.jsonl")):
            r = json.loads(line)
            x = r.get("result")
            if not x or x.get("arm") == "CDCL":
                continue
            rows.append(x)
        if stage == "posthoc":  # RNDO uses the test stage's seeds; its NOV runs are in test/
            for line in open(os.path.join(ART, "test", "results.jsonl")):
                x = json.loads(line).get("result")
                if x and x.get("arm") == "NOV":
                    nov[(x["cell"], x["seed"])] = x["runs"]
        for x in rows:
            if x["arm"] == "NOV":
                nov[(x["cell"], x["seed"])] = x["runs"]
        c = collections.Counter()
        bad = []
        for x in rows:
            if x["arm"] in ("NOV", "PS"):
                continue
            base = nov.get((x["cell"], x["seed"]))
            for i, q in enumerate(x["runs"]):
                if q.get("rebuilds", 0) > 0:
                    c[(x["arm"], "with_rebuild")] += 1
                    continue
                c[(x["arm"], "no_rebuild")] += 1
                b = base[i]
                same = (q["flips"], q["solved"], q["work_fast"]) == (b["flips"], b["solved"], b["work_fast"])
                if same:
                    c[(x["arm"], "no_rebuild_identical")] += 1
                else:
                    bad.append({"cell": x["cell"], "arm": x["arm"], "seed": x["seed"], "run": i,
                                "slow": [q["flips"], q["solved"], q["work_fast"]], "nov": [b["flips"], b["solved"],
                                                                                         b["work_fast"]]})
        out[stage] = {"counts": {f"{a}|{k}": v for (a, k), v in sorted(c.items())}, "mismatches": len(bad),
                      "mismatch_examples": bad[:10]}
    return out


class FirstMove(Exception):
    pass


def capture_first_rebuild(inst, nov, rs, cap, pol):
    orig = S.reduce_pattern

    def wrapped(*a, **k):
        fr = sys._getframe(2)  # run_slow's frame (wrapped <- build <- run_slow)
        loc = fr.f_locals
        raise FirstMove({"flips": int(loc["flips"]), "xs": np.array(loc["xs"]), "lf": np.array(loc["lf"]),
                         "rng": np.array(loc["rngst"]), "t": int(loc["t"]), "work_fast": int(loc["work_fast"]),
                         "roots": np.array(loc["roots"])})

    S.reduce_pattern = wrapped
    try:
        r = S.run_slow(inst, "novelty_plus", nov, rs, cap, pol)
        return None, r
    except FirstMove as e:
        return e.args[0], None
    finally:
        S.reduce_pattern = orig


def nov_capped(inst, nov, rs, cap):
    L = S.lib()
    x, r = S.initial_state(inst.n, rs)
    h, w0 = S._handle(inst.n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x, np.full(inst.n, -1, np.int64), r, 0, 0)
    p = np.zeros(4)
    p[:2] = nov
    out = np.zeros(5)
    L.fl_run(h, 4, p, int(cap), out)
    xs = np.zeros(inst.n, np.uint8)
    lf = np.zeros(inst.n, np.int64)
    rg = np.zeros(2, np.uint64)
    tt = ctypes.c_int64(0)
    L.fl_get(h, xs, lf, rg, ctypes.byref(tt), np.zeros(max(1, inst.m), np.int32), np.zeros(max(1, inst.m), np.uint8))
    L.fl_free(h)
    return {"flips": int(out[0]), "solved": bool(out[1]), "xs": xs, "lf": lf, "rng": rg, "t": int(tt.value),
            "work_fast": int(out[3]) + w0}


def part_b(cells, arms, n_inst, n_runs):
    tun = json.load(open(os.path.join(ART, "retuned.json")))
    pols = json.load(open(os.path.join(ART, "policies.json")))
    c = collections.Counter()
    bad = []
    first_flips = collections.defaultdict(list)
    for cell in cells:
        fam, a, w, n, cap = CELLS[cell]
        nov = tuple(tun[cell]["NOV"])
        for i in range(n_inst):
            seed = 7_100_000 + i
            inst = S.planted_embed(n, seed, **EMBED) if fam == "embed" else S.planted(fam, n, a, seed, w=w)
            for arm in arms:
                pol = dict(pols["GO" if arm in ("GO", "RNDO") else "G"])
                if arm in ("RND", "RNDO"):
                    pol["mode"] = 1
                if arm == "Gx":
                    pol["beta"] = 0.5
                for r in range(n_runs):
                    rs = S.run_seed("test", cell, seed, r)
                    st, full = capture_first_rebuild(inst, nov, rs, cap, pol)
                    if st is None:  # never moved: the whole run must equal NOV's
                        b = S.run_fast(inst, "novelty_plus", nov, rs, cap)
                        same = (full["flips"], full["solved"], full["work_fast"]) == (b["flips"], b["solved"],
                                                                                    b["work_fast"])
                        c[(arm, "no_move", same)] += 1
                        if not same:
                            bad.append({"cell": cell, "arm": arm, "seed": seed, "run": r, "kind": "no_move",
                                        "slow": [full["flips"], full["work_fast"]], "nov": [b["flips"], b["work_fast"]]})
                        continue
                    b = nov_capped(inst, nov, rs, st["flips"])
                    roots = st["roots"]
                    same = (b["flips"] == st["flips"] and not b["solved"] and np.array_equal(b["xs"][roots], st["xs"])
                            and np.array_equal(b["lf"][roots], st["lf"]) and np.array_equal(b["rng"], st["rng"])
                            and b["t"] == st["t"] and b["work_fast"] == st["work_fast"]
                            and len(roots) == inst.n)
                    c[(arm, "first_move", bool(same))] += 1
                    first_flips[f"{cell}|{arm}"].append(st["flips"])
                    if not same:
                        bad.append({"cell": cell, "arm": arm, "seed": seed, "run": r, "kind": "first_move",
                                    "slow_flips": st["flips"], "nov_flips": b["flips"], "nov_solved": b["solved"],
                                    "x_equal": bool(np.array_equal(b["xs"][roots], st["xs"])),
                                    "work": [st["work_fast"], b["work_fast"]]})
    return {"counts": {f"{a}|{k}|{'identical' if s else 'DIFFERENT'}": v for (a, k, s), v in sorted(c.items())},
            "mismatches": len(bad), "mismatch_examples": bad[:10],
            "median_flips_at_first_move": {k: float(np.median(v)) for k, v in first_flips.items()}}


def main():
    t0 = time.time()
    res = {"a_stored_runs": part_a()}
    t1 = time.time()
    res["b_fresh_runs"] = part_b(["local-w10-3200", "local-w40-3200", "embed-3200", "block-3200", "local-w10-800",
                                  "rand-800", "embed-800"], ["G", "GO", "RND", "RNDO", "Gx"], 10, 5)
    res["seconds"] = {"a": round(t1 - t0, 1), "b": round(time.time() - t1, 1)}
    with open(os.path.join(HERE, "referee_task2_identity.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
