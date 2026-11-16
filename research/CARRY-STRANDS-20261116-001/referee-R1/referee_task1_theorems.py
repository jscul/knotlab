"""Referee R1, task 1: Theorems 1-3 on small patterns (fresh code only).

Exhaustive: every atom pattern on n = 4 (the 12 atoms {a, b} -> c, every
subset) with every held set.  Random: n = 5..12, varied densities and held
sets, own seeds.

Checks per pattern, w = 1, 2, 3:
  T1   spend-only phase(v) = ceil(sigma(v) / w) for every forced v
       (sigma exact: Knuth and, for n <= 8, the exhaustive set method);
  T2a  T_w(spend) >= max sigma;  T2b  in each spend-only phase, the BFS
       distance to each newly forced v >= 2^sigma_F(v) - 1 (sigma_F over the
       phase's start); T2c  T_1 <= sigma_max * ceil(log2(n + 1));
       (contrast: the same distance bound for the keep law, counted);
  T3   keep-law one-phase reach == pebble-game (sliding) reach, from F = H,
       and the full keep-law phase vector == the iterated pebble phases;
  COPY the copying variant (spend-only multisets + copy step): its reach
       against the pebble reach; least w' with copy-reach(w') >= pebble(w).
Also: every law ends in the closure.
"""

import itertools
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402

WS = (1, 2, 3)


def check_pattern(args):
    n, atoms, held = args
    held = set(held)
    out = {"bad": [], "sigma_max": 0, "keep_ne_spend": 0, "copy_ne_pebble": 0,
           "copy_extra": {}, "keep_dist_bound_viol": 0, "spend_dist_checks": 0}
    clo = R.closure(n, atoms, held)
    sig = R.sigma(n, atoms, held, brute=(n <= 8))
    fin = [v for v in range(n) if sig[v] < R.INF]
    assert set(fin) == clo
    smax = max((sig[v] for v in fin), default=0)
    out["sigma_max"] = smax

    def bad(tag, **kw):
        if len(out["bad"]) < 3:
            out["bad"].append({"tag": tag, "n": n, "atoms": atoms, "held": sorted(held), **kw})

    for w in WS:
        sp = R.run_law(n, atoms, held, w, "spend", with_sigma_F=True)
        kp = R.run_law(n, atoms, held, w, "keep", with_sigma_F=True)
        for name, r in (("spend", sp), ("keep", kp)):
            if r["forced"] != clo:
                bad("closure", w=w, law=name)
        # Theorem 1
        for v in fin:
            if sp["phase"][v] != math.ceil(sig[v] / w):
                bad("T1", w=w, v=v, phase=sp["phase"][v], sigma=sig[v])
                break
        # Theorem 2
        if sp["T"] < smax:
            bad("T2a", w=w, T=sp["T"], sigma_max=smax)
        for ph in sp["firsts"]:
            for v, (dist, sF) in ph.items():
                out["spend_dist_checks"] += 1
                if dist < 2 ** sF - 1:
                    bad("T2b", w=w, v=v, dist=dist, sigma_F=sF)
            sm = max(sF for (_, sF) in ph.values())
            # the phase's rounds >= the largest sigma_F it forces
        for t, ph in enumerate(sp["firsts"]):
            sm = max(sF for (_, sF) in ph.values())
            if R.rounds_of(sp["L"][t]) < sm:
                bad("T2 phase rounds", w=w, t=t + 1)
        for ph in kp["firsts"]:
            for v, (dist, sF) in ph.items():
                if dist < 2 ** sF - 1:
                    out["keep_dist_bound_viol"] += 1
        if w == 1 and sp["T"] > smax * math.ceil(math.log2(n + 1)):
            bad("T2c", T=sp["T"], sigma_max=smax)
        if w == 1 and kp["phase"] != sp["phase"]:
            bad("w1 keep != spend", w=w)
        if kp["phase"] != sp["phase"]:
            out["keep_ne_spend"] += 1
        # Theorem 3: one phase from H, and all phases
        kr = R.one_phase_reach(atoms, held, w, "keep")
        pr = R.pebble_reach(n, atoms, held, w) - held
        if kr != pr:
            bad("T3 one phase", w=w, keep=sorted(kr), pebble=sorted(pr))
        pph, pP, pF = R.pebble_phases(n, atoms, held, w)
        if pph != kp["phase"]:
            bad("T3 phases", w=w, keep=kp["phase"], pebble=pph)
        # copying variant
        cr = R.one_phase_reach(atoms, held, w, "copy")
        sr = R.one_phase_reach(atoms, held, w, "spend")
        if not cr <= pr:
            bad("copy exceeds pebble", w=w, copy=sorted(cr), pebble=sorted(pr))
        if not sr <= cr:
            bad("spend exceeds copy", w=w)
        if cr != pr:
            out["copy_ne_pebble"] += 1
        extra = None
        for e in range(0, 4):
            if R.one_phase_reach(atoms, held, w + e, "copy") >= pr:
                extra = e
                break
        out["copy_extra"][f"w{w}"] = extra
    return out


def all_n4():
    n = 4
    base = [(a, b, c) for c in range(n) for a, b in itertools.combinations([x for x in range(n) if x != c], 2)]
    assert len(base) == 12
    for mask in range(1 << 12):
        atoms = [base[i] for i in range(12) if (mask >> i) & 1]
        for hm in range(1 << n):
            yield (n, atoms, [v for v in range(n) if (hm >> v) & 1])


def random_small(seed=916, per_n=3000, jump_per_n=2000):
    """Uniform random held sets at varied densities, plus patterns at the
    jump (m = 3n, held = first k* of a uniform order)."""
    rng = np.random.default_rng(seed)
    for n in range(5, 13):
        for _ in range(per_n):
            c = float(rng.choice([1.0, 1.5, 2.0, 3.0, 4.0, 6.0]))
            m = max(1, int(round(c * n)))
            A = R.RC.random_atoms(n, m, rng)
            atoms = [tuple(int(x) for x in row) for row in A]
            k = int(rng.integers(2, max(3, n // 2 + 2)))
            held = rng.choice(n, k, replace=False).tolist()
            yield (n, atoms, held)
        for _ in range(jump_per_n):
            A = R.RC.random_atoms(n, 3 * n, rng)
            atoms = [tuple(int(x) for x in row) for row in A]
            order = rng.permutation(n).tolist()
            k = R.k_star(n, atoms, order)
            yield (n, atoms, order[:k])


def zipper(k):
    h1, h2 = 0, 1
    p, q = 2, 3
    atoms = [(h1, h2, p), (h1, h2, q)]
    n = 4
    for _ in range(k):
        pn, qn = n, n + 1
        n += 2
        atoms += [(p, q, pn), (pn, q, qn)]
        p, q = pn, qn
    return (n, atoms, [h1, h2])


def structured_small():
    for k in range(1, 7):
        n, at, H, _ = R.ladder(k)
        yield (n, at, sorted(H))
    for h in range(1, 7):
        n, at, H, _ = R.pyramid(h)
        yield (n, at, sorted(H))
    for d, ell in ((1, 1), (2, 1), (2, 2), (3, 1)):
        n, at, H, _ = R.subdivided_tree(d, ell)
        yield (n, at, sorted(H))
    # zipper: p0, q0 begin; p_{i+1} = (p_i, q_i), q_{i+1} = (p_{i+1}, q_i).
    # Pebbling with sliding needs 2 pebbles at any length; copying needs 3.
    for k in range(1, 5):
        yield zipper(k)
    # the gates' G8 shape: chains h..x and h..y, (x, y -> c), (c, x -> t)
    hh, g, n, atoms = 0, 1, 2, []
    ends = []
    for _ in range(2):
        u = hh
        for _ in range(3):
            atoms.append((u, g, n)); u = n; n += 1
        ends.append(u)
    x, y = ends
    atoms += [(x, y, n), (n, x, n + 1)]
    yield (n + 2, atoms, [hh, g])


def aggregate(results):
    agg = {"cases": 0, "bad": [], "n_bad": 0, "sigma_max_hist": {}, "keep_ne_spend_cases": 0,
           "copy_ne_pebble_cases": 0, "copy_extra_hist": {}, "keep_dist_bound_violations": 0,
           "spend_dist_checks": 0}
    for r in results:
        agg["cases"] += 1
        if r["bad"]:
            agg["n_bad"] += 1
            if len(agg["bad"]) < 10:
                agg["bad"] += r["bad"]
        s = str(r["sigma_max"])
        agg["sigma_max_hist"][s] = agg["sigma_max_hist"].get(s, 0) + 1
        agg["keep_ne_spend_cases"] += int(r["keep_ne_spend"] > 0)
        agg["copy_ne_pebble_cases"] += int(r["copy_ne_pebble"] > 0)
        agg["keep_dist_bound_violations"] += r["keep_dist_bound_viol"]
        agg["spend_dist_checks"] += r["spend_dist_checks"]
        for w, e in r["copy_extra"].items():
            key = f"{w}:+{e}"
            agg["copy_extra_hist"][key] = agg["copy_extra_hist"].get(key, 0) + 1
    return agg


def main():
    out = {}
    with Pool(4) as pool:
        t0 = time.time()
        res = pool.map(check_pattern, list(all_n4()), chunksize=256)
        out["n4_exhaustive"] = aggregate(res)
        out["n4_exhaustive"]["seconds"] = round(time.time() - t0, 1)
        print("n4", json.dumps({k: v for k, v in out["n4_exhaustive"].items() if k != "bad"}), flush=True)
        t0 = time.time()
        res = pool.map(check_pattern, list(random_small()), chunksize=8)
        out["random_n5_12"] = aggregate(res)
        out["random_n5_12"]["seconds"] = round(time.time() - t0, 1)
        print("rand", json.dumps({k: v for k, v in out["random_n5_12"].items() if k != "bad"}), flush=True)
        t0 = time.time()
        res = pool.map(check_pattern, list(structured_small()), chunksize=1)
        out["structured_small"] = aggregate(res)
        out["structured_small"]["seconds"] = round(time.time() - t0, 1)
        print("struct", json.dumps({k: v for k, v in out["structured_small"].items() if k != "bad"}), flush=True)
    with open(os.path.join(HERE, "referee_task1_theorems.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for k, v in out.items():
        print(k, "bad cases:", v["n_bad"], v["bad"][:2])


if __name__ == "__main__":
    main()
