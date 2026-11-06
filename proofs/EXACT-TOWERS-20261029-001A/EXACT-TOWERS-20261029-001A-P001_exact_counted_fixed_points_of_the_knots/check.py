"""Checks for EXACT-TOWERS-20261029-001A-P001 (exact counted fixed points: which knots, at which sizes, with which factors).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 34 three-bit knots in 16 classes; for each class the signed coordinate permutations preserving it and their orbits on it
    (transitive exactly for the two parity classes, not-all-equal and twisted not-all-equal)
  2 enumeration: the fast enumeration gives the same shapes as a full canonical enumeration at three, four and five copies
    (3, 11, 104); the mutated size-first ordering misses shapes (control)
  3 census over hub gadgets of 3 to 6 copies, every shape and every placement: rebuilding and exact gadgets, irredundant ones (no two
    copies imposing the same constraint on the same variables), factors, the factor formula, single-scale gadgets (all three leg
    distances equal) and their dimensions
  4 the linear mechanism: for the parity classes every rebuilding gadget is exact, its solution set is affine and the factor is
    |solutions| / 4, a power of two
  5 single-scale irredundant exact gadgets (all three leg distances equal): their mechanisms, and the pendant-free ones with copies,
    distance, factor and dimension log m / log s
  6 mechanisms of every irredundant exact gadget of a class other than parity, first applicable of: a pendant (at most two variables
    cut off copies holding no leg), a hidden variable constant on all solutions (frozen), two variables always equal or always
    opposite (tied), automorphisms (signed permutations of the variables fixing the leg set and permuting the constraints)
    transitive on the relation, else none of these (listed with their automorphism orbits);
    6b for the x or (y != z) classes, how the counts of the two tuples far from both excluded tuples compare with the others
  7 the leg-copy lemma: in every irredundant exact gadget with its legs on three distinct copies, deleting the copy of a leg leaves
    exactly c completions of each excluded tuple
  8 not-all-equal at seven copies: the punctured Fano gadget is exact with factor 5 and its legs are pairwise at distance 3
  9 controls: a rebuilding gadget with non-uniform counts is detected; a doubled copy is flagged redundant and leaves the counts
    unchanged; brute-force counts agree with the tensor contraction on a sample
Run: python3 -B check.py [--write] [--quick]   (numpy; about fifteen minutes; --quick stops the census at five copies)"""
import hashlib, itertools, json, math, os, random, sys, time
from collections import Counter, defaultdict

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import exact_lib as X  # noqa: E402
out, ok_all = {}, True
MAXM = 5 if "--quick" in sys.argv else 6


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


def name(E):
    return {((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)): "parity (odd tuples allowed)",
            ((0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)): "parity (even tuples allowed)",
            ((0, 0, 0), (1, 1, 1)): "not-all-equal", ((0, 0, 1), (1, 1, 0)): "twisted not-all-equal",
            ((0, 0, 0), (0, 1, 1)): "x or (y != z)", ((0, 0, 1), (1, 1, 1)): "not x or (y != z)",
            ((0, 0, 0), (0, 1, 1), (1, 0, 1)): "three excluded {000, 011, 101}",
            ((0, 0, 1), (0, 1, 0), (1, 1, 1)): "three excluded {001, 010, 111}"}.get(E, str(E))


def slow_shapes(m, k=3):
    subsets = [frozenset(c) for r in range(2, m + 1) for c in itertools.combinations(range(m), r)]
    res = set()
    for legs in itertools.combinations_with_replacement(range(m), k):
        deg0 = [0] * m
        for c in legs:
            deg0[c] += 1
        if max(deg0) > 3:
            continue

        def rec(start, chosen, deg):
            if all(d == 3 for d in deg):
                adj = defaultdict(set)
                for S in chosen:
                    for a in S:
                        for b in S:
                            adj[a].add(b)
                seen, st = {0}, [0]
                while st:
                    u = st.pop()
                    for w in adj[u]:
                        if w not in seen:
                            seen.add(w)
                            st.append(w)
                if len(seen) == m:
                    res.add(key(m, legs, chosen))
                return
            for j in range(start, len(subsets)):
                S = subsets[j]
                if all(deg[c] < 3 for c in S):
                    for c in S:
                        deg[c] += 1
                    chosen.append(S)
                    rec(j, chosen, deg)
                    chosen.pop()
                    for c in S:
                        deg[c] -= 1
        rec(0, [], deg0[:])
    return res


def key(m, legs, hid):
    return min((tuple(sorted(p[c] for c in legs)), tuple(sorted(tuple(sorted(p[c] for c in S)) for S in hid)))
               for p in itertools.permutations(range(m)))


def counts_of(m, legs, hid, choice, P, path=None):
    sp = X.spec(m, legs, hid)
    return np.einsum(sp, *[P[c] for c in choice], optimize=path if path is not None else "greedy")


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    # 1 classes and their symmetries
    sym = {}
    transitive = set()
    for K in X.reps:
        G = X.autK(K)
        orbs, seen = [], set()
        for s in sorted(K):
            if s in seen:
                continue
            o = {X.act(s, p, f) for p, f in G}
            seen |= o
            orbs.append(len(o))
        sym[name(X.excl(K))] = {"symmetries": len(G), "orbit sizes on allowed tuples": sorted(orbs)}
        if len(orbs) == 1:
            transitive.add(X.excl(K))
    expect_tr = {((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)), ((0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)),
                 ((0, 0, 0), (1, 1, 1)), ((0, 0, 1), (1, 1, 0))}
    report("1 knots, classes and their symmetries", len(X.K34) == 34 and len(X.reps) == 16 and transitive == expect_tr,
           {"knots": len(X.K34), "classes": len(X.reps), "transitive on allowed tuples": sorted(name(E) for E in transitive),
            "by class": sym})

    # 2 enumeration
    fast_ok = {}
    for m in (3, 4, 5):
        fast = {key(m, l, h) for l, h in X.gadgets(m)}
        slow = slow_shapes(m)
        fast_ok[m] = (len(fast), len(slow), fast == slow)
    import builtins
    orig_sorted = builtins.sorted

    def bad_sorted(it, **kw):
        lst = list(it)
        if lst and isinstance(lst[0], tuple) and all(isinstance(x, int) for x in lst[0]):
            return orig_sorted(lst, key=lambda c: (len(c), c))
        return orig_sorted(lst, **kw)
    X.sorted = bad_sorted
    bad4 = len({key(4, l, h) for l, h in X.gadgets(4)})
    del X.sorted
    report("2 enumeration complete", all(v[2] for v in fast_ok.values()) and bad4 < fast_ok[4][1],
           {"(fast, full, equal) by copies": fast_ok, "size-first ordering at four copies finds": bad4})

    # 3-7 census
    census = {name(X.excl(K)): {} for K in X.reps}
    single = []
    formula_ok = True
    lin = {"rebuilding": 0, "exact": 0, "affine": 0, "factor = |S|/4, a power of two": 0}
    xor_far = Counter()
    collapse = Counter()
    others = []
    legcopy = {"gadgets": 0, "leg copies leaving exactly c": 0, "all copies leaving exactly c": 0}
    sample = []
    rng = random.Random(1)
    shapes_n = {}
    for m in range(3, MAXM + 1):
        G = X.gadgets(m)
        shapes_n[m] = len(G)
        for gi, (legs, hid) in enumerate(G):
            sp = X.spec(m, legs, hid)
            n = 3 + len(hid)
            distinct = len(set(legs)) == 3
            for K in X.reps:
                E = X.excl(K)
                nm = name(E)
                PL = X.placements(K)
                PLs = set(PL)
                P = [X.T(Q) for Q in PL]
                row = census[nm].setdefault(m, {"rebuilding shapes": set(), "exact shapes": set(), "irredundant exact shapes": set(),
                                                "exact gadgets": 0, "irredundant exact gadgets": 0, "factors": Counter(),
                                                "pendant-free exact shapes": set(), "pendant-free exact gadgets": 0,
                                                "single-scale (factor, distance)": Counter(),
                                                "single-scale pendant-free (factor, distance)": Counter()})
                path = None
                for choice in itertools.product(range(len(P)), repeat=m):
                    ops = [P[c] for c in choice]
                    if path is None:
                        path = np.einsum_path(sp, *ops, optimize="greedy")[0]
                    C = np.einsum(sp, *ops, optimize=path)
                    if rng.random() < 0.0004:
                        sample.append((m, legs, hid, choice, K, C.copy()))
                    R = frozenset(s for s in X.cube if C[s] > 0)
                    if R not in PLs:
                        continue
                    row["rebuilding shapes"].add(gi)
                    vals = {int(C[s]) for s in R}
                    if len(E) == 4:
                        lin["rebuilding"] += 1
                    if nm in ("x or (y != z)", "not x or (y != z)"):
                        ex = [t for t in X.cube if t not in R]
                        far = [t for t in R if all(sum(x != y for x, y in zip(t, e)) >= 2 for e in ex)]
                        near = [t for t in R if t not in far]
                        xor_far["rebuilding gadgets"] += 1
                        xor_far["far tuples at least every near tuple"] += min(int(C[t]) for t in far) >= max(int(C[t]) for t in near)
                        xor_far["far sum above near sum, per tuple"] += (sum(int(C[t]) for t in far) / len(far) > sum(int(C[t]) for t in near) / len(near))
                    if len(vals) != 1:
                        continue
                    c = vals.pop()
                    formula_ok &= c * len(K) == int(C.sum())
                    cops = X.copies_of(m, legs, hid, choice, PL)
                    row["exact shapes"].add(gi)
                    row["exact gadgets"] += 1
                    S = X.solutions(n, cops)
                    fr, ti = X.frozen_and_tied(n, S)
                    if len(E) == 4:
                        lin["exact"] += 1
                        Z = (S ^ S[0]).astype(np.int64) @ (1 << np.arange(n, dtype=np.int64))
                        Zs = set(Z.tolist())
                        lin["affine"] += all((int(u) ^ int(v)) in Zs for u in Z for v in Z)
                        lin["factor = |S|/4, a power of two"] += (len(S) == 4 * c and c & (c - 1) == 0)
                    if X.redundant(cops):
                        continue
                    pend = X.has_pendant(n, cops)
                    mech_g = "linear" if len(E) == 4 else None
                    if len(E) != 4:
                        if pend:
                            mech_g = "pendant"
                        elif fr:
                            mech_g = "frozen hidden variable"
                        elif ti:
                            mech_g = "tied pair"
                        else:
                            Gs = X.struct_aut(n, cops)
                            orb = {X.act(min(R), pi[:3], f[:3]) for pi, f in Gs}
                            mech_g = "transitive automorphisms" if orb == set(R) else "none of these"
                            if mech_g == "none of these":
                                orbs, seen_t = [], set()
                                for t0 in sorted(R):
                                    if t0 in seen_t:
                                        continue
                                    o = {X.act(t0, pi[:3], f[:3]) for pi, f in Gs}
                                    seen_t |= o
                                    orbs.append(len(o))
                                others.append({"copies": m, "shape": sp, "class": nm, "factor": c, "leg distances": X.leg_dist(n, cops),
                                               "automorphisms": len(Gs), "orbit sizes on the relation": sorted(orbs)})
                        collapse[(nm, mech_g)] += 1
                    row["irredundant exact shapes"].add(gi)
                    row["irredundant exact gadgets"] += 1
                    row["factors"][c] += 1
                    if not pend:
                        row["pendant-free exact shapes"].add(gi)
                        row["pendant-free exact gadgets"] += 1
                    if distinct:
                        legcopy["gadgets"] += 1
                        exc = [t for t in X.cube if t not in R]
                        okl = oka = True
                        for ci in range(m):
                            S2 = X.solutions(n, [cp for j, cp in enumerate(cops) if j != ci])
                            for t in exc:
                                cnt = int(np.sum(np.all(S2[:, :3] == np.array(t, dtype=np.int8), axis=1)))
                                if cnt != c:
                                    oka = False
                                    if ci in legs:
                                        okl = False
                        legcopy["leg copies leaving exactly c"] += okl
                        legcopy["all copies leaving exactly c"] += oka
                    d = X.leg_dist(n, cops)
                    if len(set(d)) == 1:
                        row["single-scale (factor, distance)"][(c, d[0])] += 1
                        if not pend:
                            row["single-scale pendant-free (factor, distance)"][(c, d[0])] += 1
                        single.append({"copies": m, "shape": sp, "class": nm, "placements": [sorted(set(X.cube) - PL[q]) for q in choice],
                                       "factor": c, "distance": d[0], "dimension": round(math.log(m) / math.log(d[0]), 6),
                                       "pendant": pend, "frozen hidden": bool(fr), "tied pair": bool(ti), "mechanism": mech_g,
                                       "parity": len(E) == 4})
        print(f"  census at {m} copies done ({time.time() - T0:.0f}s)", flush=True)
    table = {}
    for nm, rows in census.items():
        t = {}
        for m, row in rows.items():
            if not row["rebuilding shapes"]:
                continue
            t[m] = {"rebuilding shapes": len(row["rebuilding shapes"]), "exact shapes": len(row["exact shapes"]),
                    "exact gadgets": row["exact gadgets"], "irredundant exact shapes": len(row["irredundant exact shapes"]),
                    "irredundant exact gadgets": row["irredundant exact gadgets"],
                    "pendant-free exact shapes": len(row["pendant-free exact shapes"]),
                    "pendant-free exact gadgets": row["pendant-free exact gadgets"],
                    "factors (irredundant)": dict(sorted(row["factors"].items())),
                    "single-scale (factor, distance)": {f"({a}, {b})": v for (a, b), v in sorted(row["single-scale (factor, distance)"].items())},
                    "single-scale pendant-free (factor, distance)": {f"({a}, {b})": v for (a, b), v in
                                                                     sorted(row["single-scale pendant-free (factor, distance)"].items())}}
        if t:
            table[nm] = t
    smallest = {nm: min((m for m, r in t.items() if r["exact gadgets"]), default=None) for nm, t in table.items()}
    report("3 census of exact counted fixed points (3 to 6 copies)", formula_ok,
           {"shapes": shapes_n, "factor formula holds for every exact gadget": formula_ok, "smallest exact size": smallest,
            "by class and size": table})

    report("4 linear mechanism (parity)", lin["rebuilding"] == lin["exact"] == lin["affine"] == lin["factor = |S|/4, a power of two"],
           lin)

    mech = Counter()
    dims = defaultdict(set)
    for g in single:
        mech[(g["class"], g["mechanism"])] += 1
        if not g["pendant"]:
            dims[g["class"]].add((g["copies"], g["distance"], g["factor"], g["dimension"], g["mechanism"]))
    report("5 single-scale irredundant exact gadgets", True,
           {"mechanism counts": {f"{a}: {b}": v for (a, b), v in sorted(mech.items())},
            "pendant-free (copies, distance, factor, dimension, mechanism) by class": {k: sorted(v) for k, v in dims.items()}})

    total_np = sum(r["irredundant exact gadgets"] for nm, t in table.items() if not nm.startswith("parity") for r in t.values())
    none_summary = Counter((o["class"], o["copies"], o["shape"], o["factor"], o["leg distances"], o["automorphisms"],
                            tuple(o["orbit sizes on the relation"])) for o in others)
    report("6 mechanisms of all irredundant exact gadgets of the classes other than parity",
           sum(collapse.values()) == total_np and total_np > 0,
           {"counts (first applicable of: pendant, frozen hidden variable, tied pair, transitive automorphisms)":
            {f"{a}: {b}": v for (a, b), v in sorted(collapse.items())}, "irredundant exact gadgets of these classes": total_np,
            "none of these": len(others),
            "none of these, by (class, copies, shape, factor, leg distances, automorphisms, orbit sizes)":
            {str(k): v for k, v in sorted(none_summary.items(), key=str)}})
    report("6b x or (y != z): the two tuples far from both excluded tuples", xor_far["rebuilding gadgets"] > 0, dict(xor_far))
    report("7 leg-copy lemma", legcopy["gadgets"] == legcopy["leg copies leaving exactly c"] and legcopy["gadgets"] > 0, legcopy)

    # 8 not-all-equal at seven copies: the punctured Fano gadget
    NAE = frozenset(X.cube) - {(0, 0, 0), (1, 1, 1)}
    lines = [(0, 1, 3), (0, 4, 5), (0, 2, 6), (1, 2, 4), (2, 3, 5), (3, 4, 6), (1, 5, 6)]
    # legs 0, 1, 2 replace point 0 on its three lines; points 1..6 become variables 3..8
    pid = {i: i + 2 for i in range(1, 7)}
    cops = [((0, pid[1], pid[3]), NAE), ((1, pid[4], pid[5]), NAE), ((2, pid[2], pid[6]), NAE)] + \
           [((pid[x], pid[y], pid[z]), NAE) for x, y, z in lines[3:]]
    S = X.solutions(9, cops)
    cnt = Counter(tuple(r[:3]) for r in S.tolist())
    fano_ok = {t for t in cnt} == set(NAE) and set(cnt.values()) == {5} and X.leg_dist(9, cops) == (3, 3, 3)
    report("8 not-all-equal at seven copies (punctured Fano gadget)", fano_ok,
           {"counts": {str(t): cnt[t] for t in X.cube}, "leg distances": X.leg_dist(9, cops),
            "dimension log 7 / log 3": round(math.log(7) / math.log(3), 6)})

    # 9 controls
    K = next(K for K in X.reps if X.excl(K) == ((0, 0, 0), (0, 1, 1)))
    PL = X.placements(K)
    P = [X.T(Q) for Q in PL]
    found = None
    for legs, hid in X.gadgets(4):
        for choice in itertools.product(range(3), repeat=4):
            C = counts_of(4, legs, hid, choice, P)
            R = frozenset(s for s in X.cube if C[s] > 0)
            if R in set(PL):
                found = sorted(int(C[s]) for s in R)
                break
        if found:
            break
    nonuniform = found is not None and len(set(found)) > 1
    TW1 = frozenset(X.cube) - {(0, 1, 1), (1, 0, 0)}
    TW2 = frozenset(X.cube) - {(0, 1, 0), (1, 0, 1)}
    tet = [((0, 3, 4), TW1), ((1, 3, 5), TW1), ((2, 4, 5), TW2), ((3, 4, 5), TW1)]
    c1 = Counter(tuple(r[:3]) for r in X.solutions(6, tet).tolist())
    c2 = Counter(tuple(r[:3]) for r in X.solutions(6, tet + [((3, 4, 5), TW1)]).tolist())
    red = X.redundant(tet + [((3, 4, 5), TW1)]) and not X.redundant(tet) and c1 == c2
    agree = 0
    for (m, legs, hid, choice, Kk, C) in sample:
        cops = X.copies_of(m, legs, hid, choice, X.placements(Kk))
        Sx = X.solutions(3 + len(hid), cops)
        cb = Counter(tuple(r[:3]) for r in Sx.tolist())
        agree += all(cb[s] == int(C[s]) for s in X.cube)
    report("9 controls", nonuniform and red and agree == len(sample) and len(sample) >= 50,
           {"x or (y != z), four copies, counts on its relation": found, "doubled copy flagged redundant, counts unchanged": red,
            "brute force agrees with contraction": f"{agree}/{len(sample)}"})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        minimal = [g for g in single if not g["pendant"]]
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "single_scale_irredundant_exact_gadgets": minimal,
                   "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
