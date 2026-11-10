"""CHOOSE-RES-20261110-001 stress test, one size past ticket A (thin tori to 40 points): torus(N, 1, 1) for N = 42, 44, 46, 50 SAT-found
least states each with a random split (seed 1112): C7 into every class, and R0 and R3 read for the class they reach. Post hoc (not
pre-registered, labelled so): C7', which is C7 refusing to enter the over-agreeing face in the wrong sheet when another move exists, on the
same thin starts and on ticket A's 60 grown tori. Writes stress_test.json beside this file."""
import importlib.util
import itertools
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = load("choose_run", "experiments/CHOOSE-RES-20261110-001A/CHOOSE-RES-20261110-001A-E001_a_learner_given_a_target_class/run.py")
R = load("native_run", "experiments/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run.py")
G = load("grow_lib", "proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py")
L = load("steer_lib", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
H, SL = R.H, R.H.SL


def run_target_strict(T, f, deg, w0, acc, target, rng, budget):
    """C7, but entering w0 in the wrong sheet is taken only when no other move exists"""
    f, deg = list(f), list(deg)
    dt = T.dist(w0)
    cover = A.cover_distance(T, w0, target)
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
                a2 = A.xor(acc, tuple(T.contrib[3 * i + T.side(i, h, w)]))
                if w == w0 and a2 != target:
                    return 10 ** 8
                return cover.get((w, a2), 10 ** 9)
            best = min(score(c) for c in cand)
            i, w = rng.choice([c for c in cand if score(c) == best])
            k = T.side(i, h, w)
            acc = A.xor(acc, tuple(T.contrib[3 * i + k]))
            moves.append((i, k))
            deg[h] += 1
            deg[w] -= 1
            f[i] = h
            steps += 1
            last, h = h, w
    return all(d == 1 for d in deg), steps, moves, acc


rng = random.Random(1112)
out = {"thin": [], "grown, post hoc C7'": None}
for N in (42, 44, 46):
    T = H.Torus(N, 1, 1)
    s0 = T.classes[T.forced[0]]
    w = T.forced[0]
    xs = T.least_states_sat(s0, rng, 50)
    sys_ = {d: T.systole(d) for d in H.LABELS[1:]}
    short = min(sys_, key=lambda d: sys_[d])
    row = {"torus": T.name, "starts": len(xs), "C7 hits": 0, "C7' hits": 0, "targets": 0, "R0 short": 0, "R3 short": 0}
    for x in xs:
        s2, f, deg, l0, w0 = T.split(s0, x, rng.randrange(3))
        acc0 = T.label([a ^ b for a, b in zip(s2, s0)])
        for c in T.classes:
            if c == w:
                continue
            delta = A.xor(c, w)
            row["targets"] += 1
            for name, fn in (("C7", A.run_target), ("C7'", run_target_strict)):
                ok, st, mv, acc = fn(T, f, deg, w0, acc0, delta, rng, 50 * T.V * T.V)
                if ok:
                    sf, local = T.replay(s2, x, mv)
                    row[name + " hits"] += bool(local and T.label([a ^ b for a, b in zip(sf, s0)]) == delta)
        for rule in ("R0", "R3"):
            ok, st, mv = R.run(T, None, R.Conf(f, deg, s2), rule, rng, 50 * T.V * T.V)
            sf, _ = T.replay(s2, x, mv)
            row[rule + " short"] += T.label([a ^ b for a, b in zip(sf, s0)]) == short
    out["thin"].append(row)
    print(row, flush=True)
fano = SL.torus(7, 2, 1)
P = next(t for t in range(fano.nt) if fano.colour[t] == 0)
g_hits = g_tot = 0
rr = random.Random(1110)
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
                T = G.GrownTorus(g.G, "grown", g.completions[0])
                s0 = T.classes[T.natural]
                xg, _, _ = g.extend(s0, x, sph.K)
                s2, f, deg, ll, w0 = T.split(s0, xg, rr.randrange(3))
                acc0 = T.label([a ^ b for a, b in zip(s2, s0)])
                for c in T.classes:
                    if c == T.natural:
                        continue
                    delta = A.xor(c, T.natural)
                    ok, st, mv, acc = run_target_strict(T, f, deg, w0, acc0, delta, rr, 50 * T.V * T.V)
                    g_tot += 1
                    if ok:
                        sf, local = T.replay(s2, xg, mv)
                        g_hits += bool(local and T.label([a ^ b for a, b in zip(sf, s0)]) == delta)
out["grown, post hoc C7'"] = {"hits": g_hits, "targets": g_tot}
print(out["grown, post hoc C7'"])
(HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
