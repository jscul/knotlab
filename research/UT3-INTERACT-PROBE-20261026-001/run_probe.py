"""Reproduce UT3-INTERACT-PROBE-20261026-001: interacting obstruction blocks for G = UT3(F4) x| <h>, h: (x,y,z) -> (w^2 x, w^2 y, w z).
Standard library only; imports the committed probe of UT3-TWIST-PROBE-20261025-001 and frozen checks read-only. Writes probe_output.json."""
import itertools
import json
import random
import time
from collections import Counter
from pathlib import Path

from bimap import PR, SLA, analyze, extract, tensor

HERE = Path(__file__).resolve().parent


def full_twist(n):
    return [i for _ in range(n) for i in range(1, n)]


def chain_code(n, t):
    """closure of sigma_1^3 ... sigma_{n-1}^3 (connected sum of n-1 trefoils) times t full twists"""
    return SLA.gauss_from_braid([i for i in range(1, n) for _ in range(3)] + full_twist(n) * t, n)


def rank_bits(rows):
    piv, r = {}, 0
    for x in rows:
        while x:
            c = x.bit_length() - 1
            if c in piv:
                x ^= piv[c]
            else:
                piv[c] = x
                r += 1
                break
    return r


def corank_distribution(G, code):
    U, rels = SLA.surgery_presentation(code, 3)
    psi = next(p for p in PR.characters(U, rels) if p[0] == 1)
    Hx, Hy, Bvals, _ = extract(G, U, rels, psi)
    u, v = len(Hx), len(Hy)
    w, T = tensor(Bvals, u, v)
    Trows = [[sum(T[t][i][j] << j for j in range(v)) for t in range(w)] for i in range(u)]
    dist = Counter()
    for a in range(1 << u):
        rows, x, i = [0] * w, a, 0
        while x:
            if x & 1:
                rows = [r ^ s for r, s in zip(rows, Trows[i])]
            x >>= 1
            i += 1
        dist[v - rank_bits(rows)] += 1
    return dict(sorted(dist.items())), sum(c * 2 ** k for k, c in dist.items())


def main():
    t0 = time.time()
    rng = random.Random(20261026)
    GH, GE = PR.make_group(PR.ALPHA["hard"]), PR.make_group(PR.ALPHA["easy"])
    out = {"group facts": {"hard": PR.facts(GH), "easy": PR.facts(GE)}, "families": {}}
    fam = out["families"]
    for label, code, checks in ([(f"control: S3_3((3_1)^#{k})", PR.power(SLA.gauss_from_braid([1, 1, 1], 2), k), True) for k in (1, 2, 3, 4)]
                                + [(f"F1: S3_3 of closure of (s1 s2^-1)^{n}", SLA.gauss_from_braid([1, -2] * n, 3), True) for n in (2, 4, 5, 7, 8)]
                                + [(f"F2: S3_3 of closure of (s1^3 s2^3)^{m}", SLA.gauss_from_braid([1, 1, 1, 2, 2, 2] * m, 3), True) for m in (1, 2, 4, 5)]
                                + [(f"chain control: S3_3 of trefoil chain on {n} strands, t = 0", chain_code(n, 0), True) for n in (3, 6, 9)]
                                + [(f"coupled: S3_3 of trefoil chain on {n} strands, t = 1", chain_code(n, 1), n <= 12) for n in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15)]):
        r = analyze(GH, code, rng=rng, checks=checks)
        fam[label] = r
        x = r.get("psi=1", {})
        print(f"{label}: H1 {r['H1']} blocks {x.get('blocks')} sizes {x.get('block sizes (F2)')} radicals {x.get('radicals (L,R)')} "
              f"basis {x.get('random basis changes agree')} ({time.time() - t0:.0f} s)", flush=True)
    inv = {}
    for n in (6, 9):
        rows = []
        for kw in ({}, {"section": lambda x, y: PR.fmul(x, y)}, {"shift_reps": True}, {"shift_reps": True}):
            r = analyze(GH, chain_code(n, 1), rng=rng, checks=True, **kw)["psi=1"]
            rows.append([r["blocks"], r["block sizes (F2)"], r.get("random basis changes agree")])
        inv[f"n={n}, t=1 (default, section z = x*y, two coboundary shifts)"] = rows
    out["section, representative and basis-change checks"] = inv
    print("invariance:", inv, flush=True)
    counts = {}
    for n in (6, 9, 12):
        dist, rs = corank_distribution(GH, chain_code(n, 1))
        counts[f"n={n}"] = {"F2-corank distribution of a -> B(a,.)": dist, "rank-sum": rs, "big block count c = rank-sum / 7^(m-1)": rs / 7 ** (n // 3 - 1)}
    for n in (6, 9):
        code = chain_code(n, 1)
        U, rels = SLA.surgery_presentation(code, 3)
        psi = next(p for p in PR.characters(U, rels) if p[0] == 1)
        pr = PR.probe(GH, U, rels, psi, max_span=14)
        counts[f"n={n}"]["Gauss-sum liftable"] = pr.get("liftable")
        counts[f"n={n}"]["rank-sum x 4^(dim Z1_x - dim H1_x)"] = counts[f"n={n}"]["rank-sum"] * 4 ** (pr["D"] // 2 - (8 if n == 6 else 14))
        pe = PR.probe(GE, U, rels, psi, max_span=8)
        counts[f"n={n}"]["easy action: span, liftable"] = [pe["span"], pe.get("liftable")]
    out["counts"] = counts
    print("counts:", counts, flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "probe_output.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
