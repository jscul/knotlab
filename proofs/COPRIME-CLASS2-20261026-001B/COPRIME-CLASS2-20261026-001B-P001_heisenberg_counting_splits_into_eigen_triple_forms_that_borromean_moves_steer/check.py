"""Check for COPRIME-CLASS2-20261026-001B-P001: Heisenberg counting splits into eigen-triple forms that Borromean moves steer.
Standard library only (cp_lib.py in this directory). Run: python3 check.py [--write]"""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cp_lib as C  # noqa: E402

T31, F8, K52, S61 = ([1, 1, 1], 2), ([1, -2, 1, -2], 3), ([1, 1, 1, 2, -1, 2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)


def main():
    t0 = time.time()
    out, ok_all = {}, True

    # part 1: the groups (action is an automorphism; associativity sampled)
    rows1, ok1 = {}, True
    rng = random.Random(20261026)
    for (p, r, a, b) in [(7, 3, 2, 2), (5, 4, 2, 2), (5, 4, 2, 4), (7, 6, 3, 2), (5, 4, 2, 3)]:
        G = C.Group(p, r, a, b)
        E = G.elements()
        h = (0, 0, 0, 1)
        conj = lambda g: G.mul(G.mul(h, g), G.inv(h))
        N = [g for g in E if g[3] == 0]
        aut = all(conj(G.mul(x, y)) == G.mul(conj(x), conj(y)) for x in rng.sample(N, 60) for y in rng.sample(N, 60))
        act = all(conj((x, y, z, 0)) == (a * x % p, b * y % p, a * b * z % p, 0) for (x, y, z, _) in N)
        assoc = all(G.mul(G.mul(x, y), z) == G.mul(x, G.mul(y, z)) for x, y, z in ((rng.choice(E), rng.choice(E), rng.choice(E)) for _ in range(3000)))
        inv = all(G.mul(g, G.inv(g)) == (0, 0, 0, 0) for g in E)
        good = len(E) == p ** 3 * r and aut and act and assoc and inv
        rows1[f"p={p} r={r} (a,b)=({a},{b})"] = {"|G|": len(E), "conjugation by h is the stated automorphism": act and aut, "ok": good}
        ok1 &= good
    out["1_groups"] = {"rows": rows1, "ok": ok1}
    print("part 1:", ok1, flush=True)
    ok_all &= ok1

    # part 2: the counting formula against brute force (r-surgeries and rp-surgeries)
    rows2, ok2 = {}, True
    cases = [((7, 3, 2, 2), "3_1", T31, 3), ((7, 3, 2, 2), "4_1", F8, 3), ((5, 4, 2, 2), "4_1", F8, 4), ((5, 4, 2, 4), "4_1", F8, 4),
             ((5, 4, 2, 3), "4_1", F8, 4), ((7, 6, 3, 2), "3_1", T31, 6), ((7, 6, 3, 2), "5_2", K52, 6),
             ((5, 4, 2, 3), "3_1", T31, 20), ((5, 4, 2, 3), "4_1", F8, 20), ((5, 4, 2, 1), "4_1", F8, 20), ((7, 3, 2, 4), "4_1", F8, 21),
             ((5, 4, 2, 2), "4_1", F8, 20)]
    for (p, r, a, b), name, (w, n), s in cases:
        G = C.Group(p, r, a, b)
        ts = time.time()
        f, parts = C.hom_count(G, w, n, s)
        bf = C.brute_count(G, w, n, s)
        good = f == bf
        rows2[f"p={p} r={r} (a,b)=({a},{b}) S3_{s}({name})"] = {"formula": f, "brute force": bf, "ok": good,
                                                                "dims per character (k: dx, dy, N_k)": {k: v[:3] for k, v in parts.items()},
                                                                "seconds": round(time.time() - ts, 1)}
        ok2 &= good
    out["2_brute_force"] = {"rows": rows2, "ok": ok2}
    print("part 2:", ok2, {k: (v["formula"], v["brute force"]) for k, v in rows2.items()}, flush=True)
    ok_all &= ok2

    # part 3: the steering law in all four coincidence patterns, with failing controls
    rows3, ok3 = {}, True
    pat = [("pattern 3: a = b = g (p=7, r=3)", C.Group(7, 3, 2, 2), [S61] * 3, 3, [[(0, 0)], [(1, 1)], [(0, 0), (20, 1)]]),
           ("pattern 2: a = b != g (p=5, r=4)", C.Group(5, 4, 2, 2), [S61] * 3 + [F8] * 2, 4, [[(0, 0)], [(0, 1)], [(0, 0), (28, 2)]]),
           ("pattern 4: g = a != b (p=5, r=4)", C.Group(5, 4, 2, 4), [S61] * 3 + [F8] * 2, 4, [[(0, 0)], [(0, 2)], [(0, 0), (28, 2)]]),
           ("pattern 1: a, b, g distinct (p=7, r=6)", C.Group(7, 6, 3, 2), [T31, S61, K52] * 3, 6, [[(1, 1)], [(17, 1)], [(1, 1), (18, 1)]])]
    for label, G, summands, k, insertion_sets in pat:
        word, n = C.connected_sum(summands)
        for ins in insertion_sets:
            r = C.steer_test(G, word, n, ins, k)
            good = r["mismatches"][1] == 0
            rows3[f"{label} insertions {ins}"] = {**r, "ok": good}
            ok3 &= good
        # control: the left-to-right leaf convention (reverse each bundle) must mismatch on a nondegenerate insertion
        w2, tops = C.insert_at(word, insertion_sets[0], k)
        U, rels, arc = C.presentation(w2, n, G.r)
        Hx, Hy, Bm, _ = C.obstruction(G, U, rels, 1)
        gam = pow(G.a * G.b % G.p, G.p - 2, G.p)
        Hg, _, _ = C.cohomology(U, rels, gam, 1, G.p)
        Nact, act = C.kernel_counts(Hx, Hy, Bm, G.p)
        chars = (G.a, G.b, gam)
        L, o = tops[0], insertion_sets[0][0][1]
        bundles = [list(range(o + k * j, o + k * j + k)) for j in range(3)]
        rev = [[[C.leaf(H, arc, L, list(reversed(bq)), chars[t], G.p) for bq in bundles] for t, H in enumerate((Hx, Hy, Hg))]]
        pred = C.predicted_kernels(G, (Hx, Hy, Hg), rev)
        bad_ctl = sum(1 for a in act if act[a] != pred[a])
        rows3[f"{label} control: reversed leaf products"] = {"mismatching a": bad_ctl, "ok": bad_ctl > 0}
        ok3 &= bad_ctl > 0
        print("part 3", label, "done", flush=True)
    # other characters on one knot: every eigen-triple changes by the same law
    word, n = C.connected_sum([S61, F8, S61, S61, F8, S61, S61, F8, S61])
    for (a, b) in [(2, 2), (3, 3), (2, 4), (3, 4), (4, 2)]:
        r = C.steer_test(C.Group(5, 4, a, b), word, n, [(0, 0), (1, 13), (26, 8)], 4)
        good = r["mismatches"][1] == 0
        rows3[f"three insertions on interleaved 6_1/4_1, characters ({a},{b})"] = {**r, "ok": good}
        ok3 &= good
    out["3_steering"] = {"rows": rows3, "ok": ok3}
    print("part 3:", ok3, flush=True)
    ok_all &= ok3

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "COPRIME-CLASS2-20261026-001B-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
