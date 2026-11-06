"""Checks for SHARED-SUBDIVISION-20261029-001A-P001 (which knots reproduce themselves under shared subdivision of the triangular
lattice).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 34 knots in 16 classes and the 122 rules: S2 (a knot on every up triangle, 34) and S1 (one placement on every up triangle and
    one on every down triangle, from one class, 88)
  2 the counting engine agrees with an independent exact count in Python integers (float and residues) on sampled coarse assignments
    of every rule: scale 2 on the 6-torus and on the 8-torus, scale 3 on the 9-torus
  3 scale 2: set-level and counted exactness of every rule on the 6- and 8-tori (coarse 3- and 4-tori)
  4 scale 3: set-level and counted exactness of every rule on the 9-torus (coarse 3-torus)
  5 solution counts on the L-torus for L = 2..11 (transfer-matrix traces): entropy per site at L = 11 and the largest log2(count) / L
  6 affineness: every exact rule has an affine solution set on the 3- to 6-tori; every other rule has a non-affine one on some torus
    of side 3 to 6
  7 the exact rules by family: parity on up triangles; frozen (at most 4 solutions on every torus of side 2 to 11); line-constant
    (every solution on the 3- to 6-tori constant along one lattice direction, 2^L solutions)
  8 controls: not-all-equal on all triangles gains coarse assignments it forbids at both scales; every rule with entropy above 0.1 bit
    per site at L = 11 is exact at neither scale
Run: python3 -B check.py [--write]   (numpy; about forty minutes)"""
import hashlib, json, math, os, random, sys, time
from collections import Counter, defaultdict

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import shared_lib as S  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


def label(scheme, A, B):
    return f"{scheme} up {S.excl(A)}" + (f" down {S.excl(B)}" if B is not None else "")


def exactness(N, sols):
    supp = {x for x, (f, r) in N.items() if f > 0}
    res = {N[x][1] for x in sols}
    fl = {N[x][0] for x in sols}
    return {"set": supp == sols, "counted": supp == sols and len(res) <= 1, "extra": len(supp - sols), "missing": len(sols - supp),
            "coarse solutions": len(sols), "extensions": sorted(fl)[:3]}


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    R = S.rules()
    report("1 knots, classes and rules", len(S.K34) == 34 and len(S.reps) == 16 and len(R) == 122
           and sum(1 for r in R if r[0] == "S2") == 34, {"knots": len(S.K34), "classes": len(S.reps), "rules": len(R)})

    rng = random.Random(7)
    rows = []
    agree, tested = 0, 0
    for scheme, A, B in R:
        row = {"rule": label(scheme, A, B), "scheme": scheme}
        for (L, k) in ((6, 2), (8, 2), (9, 3)):
            N = S.coarse_counts(L, k, A, B)
            sols = S.coarse_solutions(L // k, A, B)
            row[f"L={L} k={k}"] = exactness(N, sols)
            keys = list(N)
            sample = rng.sample(keys, 2 if L < 8 else 1)
            sample += [x for x in list(sols)[:1]]
            for xs in sample:
                e = S.exact_counts_python(L, k, A, B, xs)
                tested += 1
                agree += (N[xs][1] == tuple(e % p for p in S.PRIMES)) and (abs(N[xs][0] - e) <= 1e-9 * max(1.0, e))
        row["exact at scale 2"] = row["L=6 k=2"]["counted"] and row["L=8 k=2"]["counted"]
        row["set-exact at scale 2"] = row["L=6 k=2"]["set"] and row["L=8 k=2"]["set"]
        row["exact at scale 3"] = row["L=9 k=3"]["counted"]
        row["set-exact at scale 3"] = row["L=9 k=3"]["set"]
        counts = [S.solution_count(L, A, B) for L in range(2, 12)]
        row["solutions L=2..11"] = counts
        row["entropy per site at L=11"] = round(math.log2(counts[-1]) / 121, 4) if counts[-1] > 0 else None
        row["max log2(count)/L"] = round(max(math.log2(c) / L for L, c in zip(range(2, 12), counts) if c > 0), 4)
        aff = {}
        for L in (3, 4, 5, 6):
            sl = S.solutions(L, A, B)
            aff[L] = None if sl is None else S.affine(L, sl)
            if sl and (row["exact at scale 2"] or row["exact at scale 3"]):
                row.setdefault("line directions", {})[L] = sorted(set.intersection(*[set(S.line_constant(L, s)) for s in sl]))
        row["affine 3..6"] = aff
        rows.append((row, scheme, A, B))
        print(f"  {row['rule']}: scale 2 {row['exact at scale 2']}, scale 3 {row['exact at scale 3']} ({time.time() - T0:.0f}s)",
              flush=True)
    report("2 engine agrees with an independent exact count", agree == tested and tested > 300, {"sampled assignments": tested,
                                                                                               "agreeing": agree})

    ex2 = [r for r, *_ in rows if r["exact at scale 2"]]
    ex3 = [r for r, *_ in rows if r["exact at scale 3"]]
    set_only2 = [r["rule"] for r, *_ in rows if r["set-exact at scale 2"] and not r["exact at scale 2"]]
    set_only3 = [r["rule"] for r, *_ in rows if r["set-exact at scale 3"] and not r["exact at scale 3"]]
    split6_8 = [r["rule"] for r, *_ in rows if r["L=6 k=2"]["counted"] != r["L=8 k=2"]["counted"]]
    report("3 scale 2 (6- and 8-tori)", True,
           {"exact rules": len(ex2), "by scheme": dict(Counter(r["scheme"] for r in ex2)), "set-exact but not counted": set_only2,
            "exact on one torus only": split6_8, "rules": [r["rule"] for r in ex2]})
    report("4 scale 3 (9-torus)", True,
           {"exact rules": len(ex3), "by scheme": dict(Counter(r["scheme"] for r in ex3)), "set-exact but not counted": set_only3,
            "rules": [r["rule"] for r in ex3]})

    ent = {r["rule"]: (r["entropy per site at L=11"], r["max log2(count)/L"]) for r, *_ in rows}
    exact_any = [r for r, *_ in rows if r["exact at scale 2"] or r["exact at scale 3"]]
    report("5 solution counts and entropy", all(r["max log2(count)/L"] <= 1.0 + 1e-9 for r in exact_any),
           {"exact rules: largest log2(count)/L": max(r["max log2(count)/L"] for r in exact_any),
            "exact rules: largest entropy per site at L=11": max(r["entropy per site at L=11"] for r in exact_any),
            "entropy by rule": ent})

    aff_ok = all(all(v is True for v in r["affine 3..6"].values()) for r in exact_any)
    nonexact = [r for r, *_ in rows if not (r["exact at scale 2"] or r["exact at scale 3"])]
    nonaff_ok = all(any(v is False for v in r["affine 3..6"].values()) for r in nonexact)
    report("6 affineness", aff_ok and nonaff_ok,
           {"exact rules affine on every torus of side 3 to 6": aff_ok,
            "every other rule non-affine on some torus of side 3 to 6": nonaff_ok,
            "other rules with no affineness verdict": [r["rule"] for r in nonexact if not any(v is False for v in r["affine 3..6"].values())]})

    fam = {}
    fam_ok = True
    for r, scheme, A, B in rows:
        if not (r["exact at scale 2"] or r["exact at scale 3"]):
            continue
        frozen = max(r["solutions L=2..11"]) <= 4
        lines = all(r.get("line directions", {}).get(L) for L in (3, 4, 5, 6)) and \
            all(abs(c - 2 ** L) < 0.5 for L, c in zip(range(2, 12), r["solutions L=2..11"]))
        parity_up = scheme == "S2" and len(S.excl(A)) == 4
        f = "parity on up triangles" if parity_up else ("frozen" if frozen else ("line-constant" if lines else "other"))
        fam_ok &= f != "other"
        fam[r["rule"]] = {"family": f, "scale 2": r["exact at scale 2"], "scale 3": r["exact at scale 3"],
                          "solutions L=2..11": [int(c) for c in r["solutions L=2..11"]],
                          "extensions at L=8 and L=9": (r["L=8 k=2"]["extensions"], r["L=9 k=3"]["extensions"]),
                          "line directions": r.get("line directions", {}).get(6)}
    report("7 the exact rules by family", fam_ok, {"families": dict(Counter(v["family"] for v in fam.values())), "rules": fam})

    nae = next((r for r, scheme, A, B in rows if scheme == "S1" and S.excl(A) == ((0, 0, 0), (1, 1, 1))), None)
    high = [r["rule"] for r, *_ in rows if (r["entropy per site at L=11"] or 0) > 0.1 and (r["exact at scale 2"] or r["exact at scale 3"])]
    report("8 controls", nae is not None and nae["L=8 k=2"]["extra"] > 0 and nae["L=9 k=3"]["extra"] > 0 and not high,
           {"not-all-equal on all triangles: forbidden coarse assignments gained (8-torus, 9-torus)":
                (nae["L=8 k=2"]["extra"], nae["L=9 k=3"]["extra"]),
            "rules with entropy above 0.1 bit per site that are exact": high})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status, "checks": {"ok": ok_all, **out},
                   "rules": [r for r, *_ in rows], "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
