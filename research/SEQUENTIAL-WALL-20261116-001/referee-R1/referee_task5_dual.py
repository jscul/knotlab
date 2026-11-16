"""Task 5: Theorem 6's dual law on acyclic patterns.

(a) every distinction is forced (closure) or found unforced by the dual law,
    never both; for n <= 10 the unforced set is also checked against the
    complement of the brute-force forced set;
(b) each distinction's dual phase equals the least generalized Strahler number
    of a derivation of unforcedness (DP in topological order); a mutant (plain
    max, no +1) must disagree somewhere, to show the test has power;
(c) structured controls: ladder and pyramid have nothing unforced (P_dual = 0);
(d) bonus: P_dual and min(P, P_dual) on layered circuits, w = 1024, against
    the study's table.
"""

import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402

INF = C.INF


def brute_forced(n, atoms, held):
    held = set(held)
    free = [v for v in range(n) if v not in held]
    always = [True] * n
    for bits in itertools.product((0, 1), repeat=len(free)):
        x = [1] * n
        for v, bt in zip(free, bits):
            x[v] = bt
        if all((not (x[a] and x[b])) or x[c] for (a, b, c) in atoms):
            always = [al and bool(xv) for al, xv in zip(always, x)]
    return always


def random_acyclic(n, m, rng):
    topo = rng.permutation(n).tolist()
    pos = {v: i for i, v in enumerate(topo)}
    atoms = []
    for _ in range(m):
        i = int(rng.integers(2, n))           # position of c
        a, b = rng.choice(i, size=2, replace=False).tolist()
        atoms.append((topo[a], topo[b], topo[i]))
    return atoms, topo


def mutant_dual(n, atoms, held, topo):
    held = set(held)
    by_c = [[] for _ in range(n)]
    for (a, b, c) in atoms:
        by_c[c].append((a, b))
    d = [INF] * n
    for v in topo:
        if v in held:
            continue
        if not by_c[v]:
            d[v] = 0
            continue
        mx = max(min(d[a], d[b]) for (a, b) in by_c[v])
        if mx < INF:
            d[v] = mx
    return d


def ladder(k):
    n = [0]
    def new():
        n[0] += 1
        return n[0] - 1
    h1, h2 = new(), new()
    x = [new()]
    atoms = []
    for _ in range(k):
        y, z, xn = new(), new(), new()
        atoms += [(x[-1], h1, y), (x[-1], h2, z), (y, z, xn)]
        x.append(xn)
    return n[0], atoms, [h1, h2, x[0]]


def pyramid(h):
    idx = {}
    for i in range(h + 1):
        for j in range(h + 1 - i):
            idx[i, j] = len(idx)
    atoms = [(idx[i - 1, j], idx[i - 1, j + 1], idx[i, j]) for i in range(1, h + 1) for j in range(h + 1 - i)]
    return len(idx), atoms, [idx[0, j] for j in range(h + 1)]


def main():
    t0 = time.time()
    rng = np.random.default_rng(np.random.SeedSequence([7734, 0]))
    st = {"cases": 0, "distinctions": 0, "unforced": 0, "partition_fail": 0, "brute_checked": 0,
          "brute_fail": 0, "phase_ne_dual_strahler": 0, "pdual_fail": 0, "mutant_disagrees_cases": 0,
          "max_dual_phase": 0, "dual_phase_hist": {}}
    fails = []
    for it in range(30000):
        n = int(rng.integers(5, 13))
        m = int(rng.integers(max(1, n // 2), 4 * n + 1))
        atoms, topo = random_acyclic(n, m, rng)
        k = int(rng.integers(0, n // 2 + 1))
        held = rng.permutation(n)[:k].tolist()
        forced = C.closure_worklist(n, atoms, held)
        unf, dph, Pd = C.dual_law_py(n, atoms, held)
        ds = C.dual_strahler_topo(n, atoms, held, topo)
        st["cases"] += 1
        st["distinctions"] += n
        st["unforced"] += sum(unf)
        bad = False
        if not all(forced[v] != unf[v] for v in range(n)):
            st["partition_fail"] += 1
            bad = True
        if n <= 10 and it % 3 == 0:
            st["brute_checked"] += 1
            bf = brute_forced(n, atoms, held)
            if bf != forced or any(unf[v] == bf[v] for v in range(n)):
                st["brute_fail"] += 1
                bad = True
        if dph != ds:
            st["phase_ne_dual_strahler"] += 1
            bad = True
        fin = [x for x in dph if x != INF]
        if Pd != ((max(fin) + 1) if fin else 0):
            st["pdual_fail"] += 1
            bad = True
        for x in fin:
            st["dual_phase_hist"][str(x)] = st["dual_phase_hist"].get(str(x), 0) + 1
        st["max_dual_phase"] = max(st["max_dual_phase"], max(fin) if fin else 0)
        if mutant_dual(n, atoms, held, topo) != ds:
            st["mutant_disagrees_cases"] += 1
        if bad and len(fails) < 5:
            fails.append({"n": n, "atoms": atoms, "held": held, "dual_phase": [str(x) for x in dph],
                          "dual_strahler": [str(x) for x in ds]})
    st["failures"] = fails
    st["seconds"] = round(time.time() - t0, 1)
    out = {"random_acyclic": st}
    print("random_acyclic", {k: v for k, v in st.items() if k != "failures"}, flush=True)

    ctrl = {}
    for k in (2, 8, 32):
        n, atoms, held = ladder(k)
        unf, _, Pd = C.dual_law_py(n, atoms, held)
        ctrl[f"ladder-{k}"] = {"unforced": sum(unf), "P_dual": Pd, "P": C.phases_py(n, atoms, held)[2]}
    for h in (4, 8, 16):
        n, atoms, held = pyramid(h)
        unf, _, Pd = C.dual_law_py(n, atoms, held)
        ctrl[f"pyramid-{h}"] = {"unforced": sum(unf), "P_dual": Pd, "P": C.phases_py(n, atoms, held)[2]}
    out["structured"] = ctrl
    print("structured", ctrl, flush=True)

    circ = {}
    study_pdual = {8: 4.0, 16: 5.0, 32: 6.0, 64: 8.5}
    study_two = {8: 4.0, 16: 5.0, 32: 6.0, 64: 8.0}
    for d in (8, 16, 32, 64):
        t1 = time.time()
        recs = []
        for s in range(10):
            rng = np.random.default_rng(np.random.SeedSequence([7734, 1, 1024, d, s]))
            inputs, layers = C.layered_circuit(1024, d, rng)
            n, A, hm = C.layered_to_atoms(inputs, layers)
            atoms = [tuple(x) for x in A.tolist()]
            held = np.flatnonzero(hm).tolist()
            forced = C.closure_worklist(n, atoms, held)
            unf, dph, Pd = C.dual_law_py(n, atoms, held)
            _, _, P, _ = C.phases_np(n, A, hm)
            recs.append({"P": P, "P_dual": Pd, "two_sided": min(P, Pd),
                         "partition_ok": all(forced[v] != unf[v] for v in range(n))})
        circ[str(d)] = {"P_dual_median": float(np.median([r["P_dual"] for r in recs])),
                        "two_sided_median": float(np.median([r["two_sided"] for r in recs])),
                        "P_median": float(np.median([r["P"] for r in recs])),
                        "P_dual_all": [r["P_dual"] for r in recs],
                        "partition_ok_all": all(r["partition_ok"] for r in recs),
                        "study_P_dual_median": study_pdual[d], "study_two_sided_median": study_two[d],
                        "seconds": round(time.time() - t1, 1)}
        print("w1024 d", d, circ[str(d)], flush=True)
    out["layered_w1024"] = circ
    out["seconds_total"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_task5_dual.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
