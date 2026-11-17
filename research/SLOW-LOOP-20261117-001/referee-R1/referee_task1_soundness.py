"""SLOW-LOOP-R1 task 1a/1b: soundness of the probes and of the rebuild, by brute force on small planted instances.

Under test (the study's code, called, not copied): slow_loop.planted / planted_embed (instance generators),
slow_loop._handle / initial_state, the C functions fl_run and sl_probe (probing on a handle), and
slow_loop.reduce_pattern (-> C sl_reduce, the tie cascade and rebuild). Every check is made by the referee's own
oracle (referee_oracle.py): full enumeration of the 2^n states.

Per instance, rounds of: for each probe mode (0 guided after a short fast-loop epoch, 1 random, 2 static), a fresh
handle on the current (reduced, signed) pattern, sl_probe with a drawn budget, probe budget pb, shadow share beta and J;
every tie and shadow knot written is mapped to original ids and checked on the ORIGINAL allowed set A. Then the union
of the round's finds is applied with reduce_pattern, and the referee checks:
  (i)   every distinction's (root, parity) holds on A;
  (ii)  the reduced pattern (on class roots) has, once lifted by x_v = y_root(v) ^ parity(v), exactly A, one for one;
  (iii) every original and shadow knot is either kept (its canonical image is among the reduced knots), or always holds
        under the ties ('always'), never 'binding2' (a two-class constraint silently dropped) or 'contra';
        and every reduced knot is the image of some original or shadow knot;
  (iv)  no contradiction is reported.
The next round probes the reduced pattern. Output: referee_task1_soundness.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "../../../experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
os.environ.setdefault("SLOW_LOOP_BUILD",
                      "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build")
sys.path.insert(0, os.path.abspath(EXP))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import referee_oracle as O  # noqa: E402

MUTANT_TIE = int(os.environ.get("REFEREE_MUTANT", "") == "tie")
MUTANT_SH = int(os.environ.get("REFEREE_MUTANT", "") == "shadow")
import slow_loop as S  # noqa: E402  (under test)


def make_instance(cfg):
    fam = cfg["family"]
    if fam == "embed":
        return S.planted_embed(cfg["n"], cfg["seed"], frac=cfg["frac"], alpha_r=2.1, alpha_l=4.0,
                               alpha_c=cfg["alpha_c"], w=cfg["w"])
    return S.planted(fam, cfg["n"], cfg["alpha"], cfg["seed"], w=cfg["w"])


def draw_configs(N, seed=20261117):
    rng = np.random.default_rng(seed)
    cfgs = []
    for i in range(N):
        kind = ["rand", "block", "local_w10s", "local_w40s", "embed"][i % 5]
        n = int(rng.integers(10, 21))
        if kind == "rand":
            cfg = dict(family="rand", alpha=float(rng.choice([1.5, 2.1, 3.0, 4.0])), w=10)
        elif kind == "block":
            cfg = dict(family="block", alpha=float(rng.choice([2.0, 2.5, 3.5])), w=int(rng.choice([3, 4, 5])))
        elif kind == "local_w10s":
            cfg = dict(family="local", alpha=float(rng.choice([2.5, 4.0])), w=int(rng.choice([2, 3, 4])))
        elif kind == "local_w40s":
            cfg = dict(family="local", alpha=float(rng.choice([2.5, 4.0])), w=int(rng.choice([5, 6, 8])))
        else:
            n = int(rng.integers(14, 21))
            cfg = dict(family="embed", frac=float(rng.choice([0.25, 0.5])), alpha_c=float(rng.choice([0.1, 0.2])),
                       w=int(rng.choice([2, 3])))
        cfg.update(kind=kind, n=n, seed=31_000_000 + i, rseed=int(rng.integers(0, 2**62)))
        cfgs.append(cfg)
    return cfgs


def probe_cfg(rng, mode):
    pb = int(rng.choice([10**7, 10**7, 10**7, 4000, 50, 5]))
    return dict(mode=mode, budget=int(rng.choice([0, 0, 10**9, 2000])), pb=pb,
                beta=float(rng.choice([0.0, 0.5, 1.0, 1.0])), J=int(rng.choice([1, 2, 4, 8])),
                abort=int(rng.choice([0, 0, 0, 2])), flips=int(rng.choice([5, 30, 200])))


def work_one(cfg):
    t0 = time.time()
    L = S.lib()
    rng = np.random.default_rng(cfg["rseed"])
    # planted_embed has no retry guard: at tiny n a sub-pattern whose hidden values are all equal admits no knot and
    # the generator never returns (impossible at the study's sizes). Such instances are skipped and counted.
    import signal

    def _alarm(*_):
        raise TimeoutError

    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(3)
    try:
        inst = make_instance(cfg)
    except TimeoutError:
        return dict(cfg=cfg, skipped_generator=True, m=0, n_allowed=0, ties_checked=0, shadows_checked=0, rounds=0,
                    reduces=0, bij_checks=0, dropped_checked=0, kept_checked=0, contra_probe=0, contra_reduce=0,
                    violations=[], probes=0)
    finally:
        signal.alarm(0)
    n = inst.n
    A = O.allowed(n, inst.knots)
    res = dict(cfg=cfg, m=int(inst.m), n_allowed=int(len(A)), ties_checked=0, shadows_checked=0, rounds=0,
               reduces=0, bij_checks=0, dropped_checked=0, kept_checked=0, contra_probe=0, contra_reduce=0,
               violations=[], probes=0)
    if inst.hidden is not None and O.as_set(A).isdisjoint({bytes(inst.hidden.astype(np.uint8))}):
        res["violations"].append({"what": "planted state not allowed by own oracle"})
    if len(A) == 0:
        res["violations"].append({"what": "no allowed state"})
        return res
    # true tie classes (for information): pairs with constant parity over A
    const = np.all(A == A[0:1], axis=0)
    ties = S.Ties(n)
    shadows = []
    roots = np.arange(n)
    kv = inst.knots.copy()
    ks = np.zeros_like(kv, dtype=np.uint8)
    idle = 0
    for rnd in range(10):
        res["rounds"] += 1
        new_t, new_b = [], []
        m = len(kv)
        for mode in (0, 1, 2):
            pc = probe_cfg(rng, mode)
            nr = len(roots)
            col = np.full(n, -1, dtype=np.int64)
            col[roots] = np.arange(nr)
            kvn = col[kv].astype(np.int32) if m else np.zeros((0, 3), np.int32)
            x, rs = S.initial_state(nr, int(rng.integers(0, 2**62)))
            h, _ = S._handle(nr, kvn, ks if m else np.zeros((0, 3), np.uint8), x, np.full(nr, -1, np.int64), rs,
                             int(rng.integers(0, 2**62)), 0, None)
            if mode == 0:
                L.fl_run(h, 4, np.array([0.5, 0.05, 0.0, 0.0]), int(pc["flips"]), np.zeros(5))
            capt = capb = 4 * max(m, 1) + 16
            tb = np.zeros(3 * capt, np.int32)
            bb = np.zeros(6 * capb, np.int32)
            out = np.zeros(6)
            L.sl_probe(h, pc["mode"], pc["budget"], pc["pb"], pc["beta"], pc["J"], pc["abort"], tb, capt, bb, capb, out)
            L.fl_free(h)
            res["probes"] += 1
            if out[5]:
                res["contra_probe"] += 1
                res["violations"].append({"what": "sl_probe reported a contradiction", "round": rnd, "probe": pc})
            nt, nb = int(out[1]), int(out[2])
            for j in range(nt):
                p, q, par = (int(z) for z in tb[3 * j: 3 * j + 3])
                par ^= MUTANT_TIE  # negative control only (REFEREE_MUTANT=tie): every tie with the wrong parity
                P, Q = int(roots[p]), int(roots[q])
                res["ties_checked"] += 1
                wit = O.tie_witness(A, P, Q, par)
                if wit is not None:
                    res["violations"].append({"what": "tie fails", "round": rnd, "probe": pc, "tie": [P, Q, par],
                                              "witness": wit.tolist()})
                new_t.append((P, Q, par))
            for j in range(nb):
                a, b, c, sa, sb, sc = (int(z) for z in bb[6 * j: 6 * j + 6])
                sa ^= MUTANT_SH  # negative control only (REFEREE_MUTANT=shadow): one sign of every shadow flipped
                sh = (int(roots[a]), int(roots[b]), int(roots[c]), sa, sb, sc)
                res["shadows_checked"] += 1
                wit = O.shadow_witness(A, *sh)
                if wit is not None:
                    res["violations"].append({"what": "shadow fails", "round": rnd, "probe": pc, "shadow": list(sh),
                                              "witness": wit.tolist()})
                new_b.append(sh)
        if not new_t and not new_b:
            idle += 1
            if idle >= 2:
                break
            continue
        idle = 0
        shadows.extend(new_b)
        nt_arr = np.array(new_t, dtype=np.int32).reshape(-1, 3)
        roots, kv, ks, _w = S.reduce_pattern(inst.knots, shadows, ties, nt_arr)
        res["reduces"] += 1
        if ties.contradiction:
            res["contra_reduce"] += 1
            res["violations"].append({"what": "reduce reported a contradiction", "round": rnd})
        root, rpar = ties.root.copy(), ties.rpar.copy()
        # (i) every distinction's tie to its root holds on A; roots are their own roots with parity 0
        bad = np.nonzero(np.any((A ^ A[:, root]) != rpar[None, :], axis=0))[0]
        if len(bad):
            v = int(bad[0])
            row = A[np.nonzero((A[:, v] ^ A[:, root[v]]) != rpar[v])[0][0]]
            res["violations"].append({"what": "class tie fails", "round": rnd, "v": v, "root": int(root[v]),
                                      "par": int(rpar[v]), "witness": row.tolist()})
        if np.any(root[root] != root) or np.any(rpar[root] != 0):
            res["violations"].append({"what": "root map not idempotent", "round": rnd})
        if not np.array_equal(np.sort(roots), np.unique(root)):
            res["violations"].append({"what": "returned roots differ from the classes", "round": rnd})
        # (ii) one-for-one lift
        nr = len(roots)
        col = np.full(n, -1, dtype=np.int64)
        col[roots] = np.arange(nr)
        if len(kv) and (np.any(col[kv] < 0)):
            res["violations"].append({"what": "a reduced knot names a non-root", "round": rnd})
            break
        B = O.allowed(nr, col[kv] if len(kv) else np.zeros((0, 3), np.int64), ks)
        Lf = O.lift(B, roots, root, rpar)
        sA, sL = O.as_set(A), O.as_set(Lf)
        res["bij_checks"] += 1
        if sA != sL or len(B) != len(A):
            lost = sorted(sA - sL)[:1]
            gained = sorted(sL - sA)[:1]
            res["violations"].append({"what": "lift is not one-for-one onto A", "round": rnd, "nA": len(A),
                                      "nB": int(len(B)),
                                      "lost_example": [list(x) for x in lost], "gained_example": [list(x) for x in gained]})
        # (iii) dropped knots always hold; kept ones are exactly the reduced pattern
        kept_mine = set()
        allk = [(tuple(int(z) for z in k), (0, 0, 0)) for k in inst.knots] + \
               [((a, b, c), (sa, sb, sc)) for (a, b, c, sa, sb, sc) in shadows]
        for mem, sg in allk:
            r, s = O.map_knot(root, rpar, mem, sg)
            kind, canon = O.classify_image(r, s)
            if kind == "kept":
                kept_mine.add(canon)
                res["kept_checked"] += 1
            else:
                res["dropped_checked"] += 1
                if kind != "always":
                    res["violations"].append({"what": f"dropped knot is {kind}", "round": rnd, "knot": [mem, sg],
                                              "image": [r, s]})
        kept_engine = {(tuple(int(z) for z in kv[i]), tuple(int(z) for z in ks[i])) for i in range(len(kv))}
        if kept_engine != kept_mine:
            res["violations"].append({"what": "reduced knots differ from the referee's images",
                                      "round": rnd, "only_engine": len(kept_engine - kept_mine),
                                      "only_referee": len(kept_mine - kept_engine)})
        if len(kept_engine) != len(kv):
            res["violations"].append({"what": "duplicate reduced knots", "round": rnd})
    # information: classes found vs true classes (pairs with constant parity on A)
    sig = [bytes(A[:, v] ^ A[0, v]) for v in range(n)]
    res["true_classes"] = len(set(sig))
    res["found_classes"] = int(len(np.unique(ties.root)))
    res["constant_cols"] = int(const.sum())
    res["seconds"] = round(time.time() - t0, 3)
    return res


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    S.lib()  # build once before the workers fork
    from multiprocessing import Pool
    cfgs = draw_configs(N)
    t0 = time.time()
    with Pool(8) as pool:
        rs = pool.map(work_one, cfgs, chunksize=4)
    tot = {k: sum(r[k] for r in rs) for k in ("ties_checked", "shadows_checked", "reduces", "bij_checks",
                                             "dropped_checked", "kept_checked", "contra_probe", "contra_reduce",
                                             "probes", "rounds")}
    viol = [dict(v, cfg=r["cfg"]) for r in rs for v in r["violations"]]
    by_kind = {}
    for r in rs:
        k = r["cfg"]["kind"]
        d = by_kind.setdefault(k, dict(instances=0, ties=0, shadows=0, reduces=0, violations=0, n_allowed_median=[],
                                       found_vs_true=[]))
        if r.get("skipped_generator"):
            continue
        d["instances"] += 1
        d["ties"] += r["ties_checked"]
        d["shadows"] += r["shadows_checked"]
        d["reduces"] += r["reduces"]
        d["violations"] += len(r["violations"])
        d["n_allowed_median"].append(r["n_allowed"])
        if "true_classes" in r:
            d["found_vs_true"].append(r["found_classes"] - r["true_classes"])
    for d in by_kind.values():
        d["n_allowed_median"] = float(np.median(d["n_allowed_median"]))
        f = np.array(d.pop("found_vs_true"))
        d["instances_where_probing_reached_true_classes"] = int(np.sum(f == 0))
    tot["skipped_generator"] = sum(1 for r in rs if r.get("skipped_generator"))
    out = dict(instances=N, totals=tot, violations=len(viol), violation_examples=viol[:20], by_kind=by_kind,
               seconds=round(time.time() - t0, 1),
               n_range=[min(r["cfg"]["n"] for r in rs), max(r["cfg"]["n"] for r in rs)])
    out["mutant"] = os.environ.get("REFEREE_MUTANT", "")
    if out["mutant"]:
        kinds = {}
        for v in viol:
            kinds[v["what"]] = kinds.get(v["what"], 0) + 1
        out["violation_kinds"] = kinds
        out["instances_with_violation"] = sum(1 for r in rs if r["violations"])
        out["instances_with_finds"] = sum(1 for r in rs if r["ties_checked"] + r["shadows_checked"] > 0)
        out.pop("violation_examples")
    fn = "referee_task1_soundness.json" if not out["mutant"] else f"referee_task1_control_{out['mutant']}.json"
    with open(os.path.join(HERE, fn), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("instances", "totals", "violations", "seconds", "n_range")}, indent=1))
    print(json.dumps(by_kind, indent=1))


if __name__ == "__main__":
    main()
