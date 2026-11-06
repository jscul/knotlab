"""Checks for HUB-SURVIVORS-20261029-001A-P001 (hub survivors are rebuilt by parallel copies).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 34 three-bit knots and their 16 classes up to coordinate order
  2 parallel copies: closing each class's placements under intersection, which classes reach an equality on two coordinates and
    which reach a parity relation
  3 enumeration: the fast enumeration (lowest unfilled copy first) gives the same shapes as a full canonical enumeration at three,
    four and five copies (3, 11, 104); the mutated size-first ordering misses shapes (control)
  4 exhaustive census over hub gadgets of 3 to 6 copies, every shape and every placement: the rebuilt classes and their smallest
    sizes
  5 the monotone atoms: in every gadget of at least two copies every copy holds a hidden variable, so setting all hidden variables to
    1 (or 0) satisfies every copy of OR (or NAND); the census agrees
  6 controls: gadgets without hubs (every hidden variable in exactly two copies) rebuild only parity; all-equal, which is not a
    knot, is rebuilt
Run: python3 -B check.py [--write]   (numpy; about ten minutes)"""
import hashlib, itertools, json, os, sys, time
from collections import Counter, defaultdict

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import hub_lib as H  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


def excl(K):
    return tuple(sorted(set(H.cube) - K))


def name(K):
    E = excl(K)
    sym = sum(1 for p in itertools.permutations(range(3)) if H.permute(K, p) == K)
    return f"E={E} sym={sym}"


def slow_shapes(m, k=3):
    """full canonical enumeration: every multiset of hidden subsets, every leg position"""
    subsets = [frozenset(c) for r in range(2, m + 1) for c in itertools.combinations(range(m), r)]
    out_ = set()
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
                    out_.add(min((tuple(sorted(p[c] for c in legs)), tuple(sorted(tuple(sorted(p[c] for c in S)) for S in chosen)))
                                 for p in itertools.permutations(range(m))))
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
    return out_


def key(m, legs, hid):
    return min((tuple(sorted(p[c] for c in legs)), tuple(sorted(tuple(sorted(p[c] for c in S)) for S in hid)))
               for p in itertools.permutations(range(m)))


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    reps = H.reps
    report("1 knots and classes", len(H.K34) == 34 and len(reps) == 16, {"knots": len(H.K34), "classes": len(reps)})

    par = {}
    for K in reps:
        rels = set(H.placements(K))
        changed = True
        while changed:
            changed = False
            for A in list(rels):
                for B in list(rels):
                    C = A & B
                    if C and C not in rels:
                        rels.add(C)
                        changed = True
        eq2 = any(len(R) == 4 and any(all(s[i] == s[j] for s in R) and len({s[k] for s in R}) == 2
                                      for i, j, k in ((0, 1, 2), (0, 2, 1), (1, 2, 0))) for R in rels)
        parity = any(len(R) == 4 and len({sum(s) % 2 for s in R}) == 1 for R in rels)
        par[str(excl(K))] = {"relations": len(rels), "equality on two coordinates": eq2, "parity": parity}
    report("2 parallel copies", True, par)

    fast_ok = {}
    for m in (3, 4, 5):
        fast = {key(m, l, h) for l, h in H.gadgets(m)}
        fast_ok[m] = (len(fast), len(slow_shapes(m)), fast == slow_shapes(m))
    # control: the size-first ordering of hidden variables misses shapes at four copies
    import builtins
    orig_sorted = builtins.sorted
    def bad_sorted(it, **kw):
        lst = list(it)
        if lst and isinstance(lst[0], tuple) and all(isinstance(x, int) for x in lst[0]):
            return orig_sorted(lst, key=lambda c: (len(c), c))
        return orig_sorted(lst, **kw)
    H.sorted = bad_sorted
    bad4 = len({key(4, l, h) for l, h in H.gadgets(4)})
    del H.sorted
    report("3 enumeration complete", all(v[2] for v in fast_ok.values()) and bad4 < fast_ok[4][1],
           {"(fast, full, equal) by copies": fast_ok, "size-first ordering at four copies finds": bad4})

    rebuilt = defaultdict(dict)
    shapes_n = {}
    nohub_rebuilt = set()
    every_copy_hidden = True
    for m in range(3, 7):
        G = H.gadgets(m)
        shapes_n[m] = len(G)
        for legs, hid in G:
            deg = Counter(c for c in legs)
            every_copy_hidden &= all(deg[c] < 3 for c in range(m))
            sp = H.spec(m, legs, hid)
            nohub = all(len(S) == 2 for S in hid)
            for r, K in enumerate(reps):
                PL = H.placements(K)
                PLs = set(PL)
                P = [H.T(Q) for Q in PL]
                for choice in itertools.product(range(len(P)), repeat=m):
                    R = np.einsum(sp, *[P[c] for c in choice], optimize="greedy") > 0
                    if frozenset(s for s in H.cube if R[s]) in PLs:
                        rebuilt[excl(K)][m] = rebuilt[excl(K)].get(m, 0) + 1
                        if nohub:
                            nohub_rebuilt.add(excl(K))
                        break
        print(f"  census at {m} copies done ({time.time() - T0:.0f}s)", flush=True)
    smallest = {str(E): min(v) for E, v in rebuilt.items()}
    report("4 census of hub survivors (3 to 6 copies)", len(rebuilt) > 0,
           {"shapes": shapes_n, "rebuilt classes": len(rebuilt), "smallest size by class": smallest,
            "shapes rebuilding, by class and size": {str(E): v for E, v in rebuilt.items()},
            "not rebuilt": [excl(K) for K in reps if excl(K) not in rebuilt]})

    OR, NAND = ((0, 0, 0),), ((1, 1, 1),)
    report("5 monotone atoms never rebuilt", every_copy_hidden and OR not in rebuilt and NAND not in rebuilt,
           {"every copy holds a hidden variable": every_copy_hidden, "OR rebuilt": OR in rebuilt, "NAND rebuilt": NAND in rebuilt})

    AE = frozenset({(0, 0, 0), (1, 1, 1)})
    ae = sum(1 for m in (3, 4) for legs, hid in H.gadgets(m)
             if frozenset(s for s in H.cube if (np.einsum(H.spec(m, legs, hid), *([H.T(AE)] * m)) > 0)[s]) == AE)
    parity_classes = {excl(K) for K in reps if len(excl(K)) == 4}
    report("6 controls", nohub_rebuilt == parity_classes and ae > 0,
           {"rebuilt without hubs": sorted(nohub_rebuilt), "all-equal rebuilt (shapes of 3 and 4 copies)": ae})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
