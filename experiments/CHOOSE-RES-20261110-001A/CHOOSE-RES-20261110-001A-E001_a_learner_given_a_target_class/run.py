"""CHOOSE-RES-20261110-001A-E001: a learner given a target class (exploratory; see contract.json).

A class-forced pair resolves into one of three other classes. C7 is told a target class and keeps the class its own sign changes have made
so far; it walks the second hole by distance in the class cover to the copy of the over-agreeing face that gives the target. R0 and R3
(NATIVE-TARGET-20261110-001A) are read for the class they reach without a target. Writes
artifacts/CHOOSE-RES-20261110-001A/CHOOSE-RES-20261110-001A-E001_a_learner_given_a_target_class/run/result.json."""
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/CHOOSE-RES-20261110-001A/CHOOSE-RES-20261110-001A-E001_a_learner_given_a_target_class/run"
T0 = time.time()


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def log(*a):
    print(round(time.time() - T0, 1), *a, flush=True)


def xor(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def cover_distance(T, w0, target):
    """graph distance in the four-sheeted cover of T's 1-skeleton (a side adds its class contribution) to (w0, target)"""
    step = {}
    for i in range(T.n):
        for k in range(3):
            u, w = T.ends(i, k)
            cb = tuple(T.contrib[3 * i + k])
            step.setdefault(u, []).append((w, cb))
            step.setdefault(w, []).append((u, cb))
    d, dq = {(w0, target): 0}, deque([(w0, target)])
    while dq:
        v, a = dq.popleft()
        for w, cb in step[v]:
            st = (w, xor(a, cb))
            if st not in d:
                d[st] = d[(v, a)] + 1
                dq.append(st)
    return d


def run_target(T, f, deg, w0, acc, target, rng, budget):
    f, deg = list(f), list(deg)
    dt = T.dist(w0)
    cover = cover_distance(T, w0, target)
    holes = sorted([v for v in range(T.V) if deg[v] == 0], key=lambda v: dt[v])
    moves, steps = [], 0
    for idx, h in enumerate(holes):
        final, last = idx == len(holes) - 1, None
        while deg[h] == 0:
            if steps >= budget:
                return False, steps, moves, acc
            cand = [(i, f[i]) for i in T.lines_at[h]]
            cand = [c for c in cand if c[1] != last] or cand

            def score(c):
                i, w = c
                if not final:
                    return dt[w]
                e = 3 * i + T.side(i, h, w)
                return cover.get((w, xor(acc, tuple(T.contrib[e]))), 10 ** 9)
            best = min(score(c) for c in cand)
            i, w = rng.choice([c for c in cand if score(c) == best])
            k = T.side(i, h, w)
            acc = xor(acc, tuple(T.contrib[3 * i + k]))
            moves.append((i, k))
            deg[h] += 1
            deg[w] -= 1
            f[i] = h
            steps += 1
            last, h = h, w
    return all(d == 1 for d in deg), steps, moves, acc


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    R = load("native_run", "experiments/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run.py")
    G = load("grow_lib", "proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py")
    L = load("steer_lib", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
    H, SL = R.H, R.H.SL
    tori = [H.Torus(*t) for t in H.class_forced_tori(40)]
    st = R.starts(tori)
    rng = random.Random(1110)
    cases = []  # (space name, kind, T, s0, x, k)
    for T in tori:
        if T.params in [tuple(t) for t in SL.FANO_TORI] or T.params[1:] == (1, 1):
            for x, k in st[T.name][:50]:
                cases.append((T.name, "Fano" if T.params[0] == 7 else "thin", T, T.classes[T.forced[0]], x, k))
    fano = SL.torus(7, 2, 1)
    P = next(t for t in range(fano.nt) if fano.colour[t] == 0)
    for kk in (2, 3, 4):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        reps, _ = G.line_orbits(S)
        for l0 in reps:
            x = sph.flat_state(sph.K.lines.index(l0))
            for chir in (0, 1):
                for sg in itertools.permutations(range(3)):
                    g = G.Growth(S, sph.s0, l0, fano, P, sg, chir)
                    if g.chi != 0:
                        continue
                    T = G.GrownTorus(g.G, f"K_{kk}+atom at line {l0}, chirality {chir}, sigma {sg}", g.completions[0])
                    s0 = T.classes[T.natural]
                    xg, vmin, _ = g.extend(s0, x, sph.K)
                    assert vmin == 1
                    cases.append((T.name, "grown", T, s0, xg, rng.randrange(3)))
    log("cases", len(cases))
    rows, short_share = [], {}
    for name, kind, T, s0, x, k in cases:
        w = T.forced[0]
        s2, f, deg, l0, w0 = T.split(s0, x, k)
        acc0 = T.label([a ^ b for a, b in zip(s2, s0)])
        lb = {}
        for dl in H.LABELS[1:]:
            a, b = [e for e in H.LABELS[1:] if e != dl]
            lb[dl] = min(T.systole(dl), T.systole(a) + T.systole(b))
        short = min(lb, key=lambda dl: lb[dl])
        row = {"space": name, "kind": kind, "points": T.n}
        for c in T.classes:
            if c == w:
                continue
            delta = xor(c, w)
            M, cost = T.cheapest_matching(f, c)
            ok, steps, moves, acc = run_target(T, f, deg, w0, acc0, delta, rng, 50 * T.V * T.V)
            hit = False
            if ok:
                sf, local = T.replay(s2, x, moves)
                z = [a ^ b for a, b in zip(sf, s0)]
                hit = local and T.label(z) == delta and T.label(z) == acc
            row["%d%d" % delta] = {"lower bound": lb[delta], "cheapest": 1 + cost, "C7 resolved": ok, "C7 hit": bool(hit), "C7 re-signings": steps + 1}
        for rule in ("R0", "R3"):
            ok, steps, moves = R.run(T, None, R.Conf(f, deg, s2), rule, rng, 50 * T.V * T.V)
            sf, _ = T.replay(s2, x, moves)
            z = [a ^ b for a, b in zip(sf, s0)]
            row[rule] = {"resolved": ok, "class change": "%d%d" % T.label(z), "short": T.label(z) == short}
        row["short class change"] = "%d%d" % short
        rows.append(row)
    # summaries
    summ = {}
    for r in rows:
        key = r["space"] if r["kind"] != "grown" else "grown tori"
        s = summ.setdefault(key, {"runs": 0, "C7 hits": 0, "C7 targets": 0, "C7/cheapest by class change": {}, "R0 short": 0, "R3 short": 0,
                                  "points": r["points"], "kind": r["kind"], "C7 max re-signings": 0})
        s["runs"] += 1
        for dl in ("01", "10", "11"):
            if dl in r:
                s["C7 targets"] += 1
                s["C7 hits"] += r[dl]["C7 hit"]
                s["C7 max re-signings"] = max(s["C7 max re-signings"], r[dl]["C7 re-signings"] if r[dl]["C7 hit"] else 0)
                acc_ = s["C7/cheapest by class change"].setdefault(dl, [0, 0, 0])
                acc_[0] += r[dl]["C7 re-signings"]
                acc_[1] += r[dl]["cheapest"]
                acc_[2] = r[dl]["lower bound"] if r["kind"] != "grown" else max(acc_[2], r[dl]["lower bound"])
        s["R0 short"] += r["R0"]["short"]
        s["R3 short"] += r["R3"]["short"]
    for s in summ.values():
        s["C7/cheapest by class change"] = {dl: {"mean C7": round(v[0] / s["runs"], 2), "mean cheapest": round(v[1] / s["runs"], 2), "lower bound": v[2]}
                                            for dl, v in s["C7/cheapest by class change"].items()}
    thin_big = [s for s in summ.values() if s["kind"] == "thin" and s["points"] >= 20]
    RES = {"summary": summ, "rows": rows}
    RES["decisions"] = {
        "Q2: C7 reaches every target from every start": all(s["C7 hits"] == s["C7 targets"] for s in summ.values()),
        "Q2: C7 mean within twice the cheapest on every space": all(v["mean C7"] <= 2 * v["mean cheapest"] for s in summ.values()
                                                                    for v in s["C7/cheapest by class change"].values()),
        "Q3: R0 short in > 80% on every thin torus >= 20 points": all(s["R0 short"] > 0.8 * s["runs"] for s in thin_big),
        "Q3: R3 short in > 80% on every thin torus >= 20 points": all(s["R3 short"] > 0.8 * s["runs"] for s in thin_big),
        "Q4: C7 hits every class on every grown torus within 10": summ["grown tori"]["C7 hits"] == summ["grown tori"]["C7 targets"]
        and summ["grown tori"]["C7 max re-signings"] <= 10,
    }
    RES["seconds"] = round(time.time() - T0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")
    log("wrote", json.dumps(RES["decisions"], indent=1))
    for k_, s in summ.items():
        print(k_, {x: s[x] for x in ("runs", "C7 hits", "C7 targets", "R0 short", "R3 short", "C7 max re-signings")}, s["C7/cheapest by class change"])


if __name__ == "__main__":
    main()
