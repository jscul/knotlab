"""Checks for GEOMETRY-LAW-20261029-001B-P001 (four places: only parity and a chained implication survive).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 742 four-bit knots, their 106 classes up to coordinate order, stabilizer sizes, and the knots that orient a vertex
    (symmetry group inside the rotations of a cyclic order): 96 relations in 6 classes
  2 exhaustive census of native gadgets with four legs and 2 or 3 copies (every shape, every placement of every class): exactly the
    even parity class (every gadget), the odd parity class (exactly the gadgets with an odd number of copies) and the implication
    between pair parities (exactly the chains) are rebuilt; every output is co-independent; for every non-affine class every other
    output knot excludes fewer tuples
  3 chains of 2 to 7 copies rebuild the implication class (and the even parity class)
  4 random native gadgets of 4 copies: only the parity classes are rebuilt, and the implication class only by chains
  5 no orienting class is rebuilt by the gadgets of 2
  6 controls that must fire: with self-gluing more classes are rebuilt; all-equal on four bits, which is not co-independent, is
    rebuilt by every native shape; the bigon does not rebuild the odd parity class
Run: python3 -B check.py [--write]   (numpy for tensor contraction)"""
import hashlib, itertools, json, os, sys, time
from collections import Counter

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from census4 import (knots, permute, stabilizer, orbit_key, tensor, shapes, Gadget, survey, describe, CUBE, PERMS)  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1200], flush=True)


def co_independent(R):
    E = set(CUBE) - R
    return all(sum(a != b for a, b in zip(s, e)) >= 2 for s in E for e in E if s != e)


def rotations(cyc):
    n = len(cyc)
    res = set()
    for r in range(n):
        p = [None] * n
        for i in range(n):
            p[cyc[i]] = cyc[(i + r) % n]
        res.add(tuple(p))
    return res


EVEN = frozenset(x for x in CUBE if sum(x) % 2 == 0)
ODD = frozenset(x for x in CUBE if sum(x) % 2 == 1)
IMP = frozenset(x for x in CUBE if ((x[0] + x[1]) % 2, (x[2] + x[3]) % 2) != (1, 0))


def chain(L):
    """copies 0..L-1 in a path sharing pairs; legs: left pair of copy 0, right pair of copy L-1 (its slots 0, 1)"""
    legs = [2] + [0] * (L - 2) + [2]
    mt = []
    for i in range(L - 1):
        tgt = (2, 3) if i + 1 == L - 1 else (0, 1)
        mt += [((i, 2), (i + 1, tgt[0])), ((i, 3), (i + 1, tgt[1]))]
    return legs, mt


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    allK = knots()
    classes = {orbit_key(K) for K in allK}
    stabs = Counter(len(stabilizer(K)) for K in allK)
    cyc4 = [c for c in itertools.permutations(range(4)) if c[0] == 0]
    orient = [K for K in allK if any(set(stabilizer(K)) <= rotations(c) for c in cyc4)]
    orient_classes = {orbit_key(K) for K in orient}
    report("1 knots, classes, orientation",
           len(allK) == 742 and len(classes) == 106 and len(orient) == 96 and len(orient_classes) == 6,
           {"knots": len(allK), "classes": len(classes), "stabilizer sizes": dict(sorted(stabs.items())),
            "orienting relations": len(orient), "orienting classes": len(orient_classes),
            "orienting stabilizer sizes": dict(Counter(len(stabilizer(K)) for K in orient))})

    reps, placements, rebuilt, outputs = survey(m_values=(2, 3), rand_m=(), log=lambda *a, **k: None)
    S2, S3 = shapes(2), shapes(3)
    chains = {(2, i) for i, (l, mt) in enumerate(S2) if Gadget(2, l, mt).is_pair_chain()} | \
             {(3, i) for i, (l, mt) in enumerate(S3) if Gadget(3, l, mt).is_pair_chain()}
    allshapes = {(2, i) for i in range(len(S2))} | {(3, i) for i in range(len(S3))}
    by = {k: {(m, si) for (m, si, c) in v} for k, v in rebuilt.items()}
    ke, ko, ki = orbit_key(EVEN), orbit_key(ODD), orbit_key(IMP)
    noncoind = sum(c["not co-independent or empty"] for c in outputs.values())
    dec_bad = []
    for key, cnt in outputs.items():
        if len(key) == 8:  # parity classes
            continue
        for okey in cnt:
            if okey in ("full", "not co-independent or empty") or okey == key:
                continue
            if 16 - len(okey) >= 16 - len(key):
                dec_bad.append((describe(frozenset(key)), describe(frozenset(okey))))
    ok2 = (set(by) == {ke, ko, ki} and by[ke] == allshapes and by[ko] == {(3, i) for i in range(len(S3))}
           and by[ki] == chains and noncoind == 0 and not dec_bad)
    report("2 exhaustive census (2 and 3 copies)", ok2,
           {"shapes": {"2": len(S2), "3": len(S3)}, "chain shapes": sorted(chains), "rebuilt classes": len(by),
            "even parity rebuilt by": sorted(by.get(ke, ())), "odd parity rebuilt by": sorted(by.get(ko, ())),
            "implication rebuilt by": sorted(by.get(ki, ())), "implication": describe(IMP),
            "outputs not co-independent": noncoind, "non-decreasing arrows": dec_bad[:3]})

    ch_ok = {}
    for L in range(2, 8):
        legs, mt = chain(L)
        G = Gadget(L, legs, mt)
        last = permute(IMP, (2, 3, 0, 1))
        R = G.relation([tensor(IMP)] * (L - 1) + [tensor(last)])
        Re = G.relation([tensor(EVEN)] * L)
        ch_ok[L] = (R == IMP, Re == EVEN, G.is_pair_chain())
    report("3 chains of 2 to 7 copies rebuild the implication", all(all(v) for v in ch_ok.values()), ch_ok)

    _, _, rebuilt4, outputs4 = survey(m_values=(), rand_m=(4,), rand_n=300, log=lambda *a, **k: None)
    r4 = {k: sorted({c for (_, _, c) in v}) for k, v in rebuilt4.items()}
    ok4 = set(r4) <= {ke, ko, ki} and (ki not in r4 or r4[ki] == [True])
    report("4 random gadgets of 4 copies", ok4,
           {"rebuilt classes": [describe(frozenset(k)) for k in r4], "implication only on chains": r4.get(ki, "not met")})

    report("5 no orienting class is rebuilt", not (orient_classes & set(by)), {"orienting classes rebuilt": len(orient_classes & set(by))})

    _, _, rebuiltL, _ = survey(m_values=(2, 3), rand_m=(), loops=True, log=lambda *a, **k: None)
    extra = set(rebuiltL) - set(by)
    AE = frozenset({(0, 0, 0, 0), (1, 1, 1, 1)})
    ae = [Gadget(m, l, mt).relation([tensor(AE)] * m) == AE for m in (2, 3) for (l, mt) in shapes(m)]
    bigon = Gadget(2, *S2[0])
    odd_by_bigon = bigon.relation([tensor(ODD)] * 2)
    report("6 controls fire", bool(extra) and all(ae) and odd_by_bigon == EVEN,
           {"classes rebuilt only with self-gluing": len(extra), "all-equal rebuilt by every native shape": all(ae),
            "bigon of the odd class gives the even class": odd_by_bigon == EVEN})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
