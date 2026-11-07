#!/usr/bin/env python3
"""Checks for COUNT-SURFACES-20261107-001A: the knot's count on closed surfaces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, numpy). Single process; about a minute."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import surface_lib as L  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def combine(s0, Z, a):
    s = list(s0)
    for ai, z in zip(a, Z):
        if ai:
            s = [u ^ w for u, w in zip(s, z)]
    return s


def class_signings(K, D=()):
    """one signing per class among those whose even faces are exactly D"""
    s0 = K.signing(D)
    Z = K.classes()
    return [(a, combine(s0, Z, a)) for a in itertools.product((0, 1), repeat=len(Z))]


def vertex_graph_dist(S, v0):
    from collections import defaultdict
    adj = defaultdict(set)
    for t in range(S.nt):
        for a, b in itertools.combinations(S.vert[t], 2):
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
    dist, fr = {v0: 0}, [v0]
    while fr:
        nx = []
        for v in fr:
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    nx.append(w)
        fr = nx
    return dist


def surfaces(rng):
    """(surface, expected chi, expected orientability)"""
    out = []
    for pqr in [(7, 2, 1), (7, 4, 1), (3, 0, 3), (4, 1, 3), (5, 2, 1), (34, 1, 1), (17, 16, 2), (6, 2, 6), (9, 4, 7), (12, 5, 5)]:
        out.append((L.torus(*pqr), 0, True))
    for mhc in [(2, 3, 0), (3, 3, 0), (4, 2, 1), (5, 3, 1), (6, 5, 0), (3, 7, 1)]:
        out.append((L.klein(*mhc), 0, False))
    for m in range(1, 6):
        out.append((L.projective_plane(m), 1, False))
    for k in range(1, 5):
        out.append((L.octahedral_sphere(k), 2, True))
    for pqr in [(3, 0, 3), (4, 1, 3), (6, 2, 4)]:
        T = L.torus(*pqr)
        far = max(vertex_graph_dist(T, 0).items(), key=lambda kv: kv[1])[0]
        out.append((L.double_cover(T, [0, far]), -2, True))
    for k, b in [(2, 2), (3, 4), (3, 6), (4, 4)]:
        O = L.octahedral_sphere(k)
        K0 = L.KnotSpace(O)
        corners = [v for v in range(K0.V) if K0.d[v] == 2]
        out.append((L.double_cover(O, corners[:b]), 4 - b, True))
    K3 = L.klein(3, 3, 0)
    out.append((L.double_cover(K3, [0, max(vertex_graph_dist(K3, 0).items(), key=lambda kv: kv[1])[0]]), -2, None))
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)
    SURF = surfaces(rng)

    # 1. constructions
    rows, ok1 = [], True
    for S, chi, ori in SURF:
        K = L.KnotSpace(S)
        good = S.validate() and S.connected() and S.euler() == chi and (ori is None or S.orientable() == ori) and len(K.points) == len(K.lines)
        ok1 &= good
        rows.append((S.name, K.n, S.euler(), S.orientable(), K.simple(), good))
    check("1 every construction is a closed surface triangulated in two alternating colours (vertex links are cycles) with the expected "
          "Euler characteristic and orientability", ok1, {"surfaces": len(rows), "rows": rows})

    # 2. parity lemma, existence of signings, classes
    ok2, info2 = True, []
    for S, chi, _ in SURF:
        K = L.KnotSpace(S)
        par = True
        for _ in range(5):
            s = [rng.randrange(2) for _ in range(3 * K.n)]
            f = K.flip(s)
            D = K.even_faces(s)
            par &= len(D) % 2 == chi % 2
            for _ in range(4):
                x = L.random_assignment(K.n, rng)
                _, agree = K.tallies(s, x)
                par &= all(agree[v] % 2 == (K.d[v] + f[v]) % 2 for v in range(K.V))
        kast = K.signing(()) is not None
        Ds_ok, Ds_bad = True, True
        for _ in range(4):
            size = rng.choice([c for c in range(1, min(K.V, 6) + 1) if c % 2 == chi % 2])
            D = rng.sample(range(K.V), size)
            s = K.signing(D)
            Ds_ok &= s is not None and K.even_faces(s) == sorted(D)
            D2 = rng.sample(range(K.V), size + 1) if size + 1 <= K.V else None
            if D2:
                Ds_bad &= K.signing(D2) is None
        dim = len(K.classes())
        good = par and kast == (chi % 2 == 0) and Ds_ok and Ds_bad and dim == 2 - chi
        ok2 &= good
        info2.append((S.name, chi, kast, dim, good))
    check("2 agree_v = d_v + flip_v (mod 2) under every tested assignment and signing; the even faces D satisfy |D| = chi (mod 2); every "
          "tested D of that parity is realized and none of the other; signings without even faces exist iff chi is even; the classes "
          "modulo gauge number 2^(2 - chi)", ok2, {"rows": info2})

    # 3. the count
    ok3, tested, forced = True, 0, {}
    for S, chi, _ in SURF:
        K = L.KnotSpace(S)
        for _ in range(4):
            s = [rng.randrange(2) for _ in range(3 * K.n)] if rng.random() < 0.5 else K.signing(())
            if s is None:
                s = K.signing(rng.sample(range(K.V), 1))
            D = K.even_faces(s)
            for _ in range(6):
                x = L.random_assignment(K.n, rng)
                good, viol, E = K.count_identity(s, x)
                ok3 &= good
                tested += 1
                key = "lines" if chi > len(D) else ("vertices" if chi < len(D) else "none")
                forced.setdefault(key, set()).add(S.name.split("(")[0])
                if chi > len(D):
                    ok3 &= viol >= (chi - len(D)) // 2
                if chi < len(D):
                    ok3 &= E >= (len(D) - chi) // 2
    check("3 the count: violated lines - sum_v floor(agree_v / 2) = (chi - |D|) / 2 under every tested assignment, so the lines are forced "
          "to fail iff chi > |D| and the vertices to over-agree iff chi < |D|", ok3,
          {"assignments": tested, "which side is forced, by surface family": {k: sorted(v) for k, v in forced.items()}})

    # 4. satisfying assignments and corner maps
    small = [(L.torus(7, 2, 1), ()), (L.torus(3, 0, 3), ()), (L.torus(4, 1, 3), ()), (L.klein(3, 3, 0), ()), (L.klein(4, 2, 1), ()),
             (L.projective_plane(2), "one corner"), (L.projective_plane(2), "three corners"), (L.octahedral_sphere(2), "two corners"),
             (L.double_cover(L.torus(3, 0, 3), [0, 4]), ())]
    ok4, info4 = True, []
    for S, Dspec in small:
        K = L.KnotSpace(S)
        corners = [v for v in range(K.V) if K.d[v] == 2]
        D = {(): [], "one corner": corners[:1], "three corners": corners, "two corners": corners[:2]}[Dspec]
        cls = class_signings(K, D)
        As = K.matchings(D)
        per = {a: 0 for a, _ in cls}
        exactly_one = True
        for A in As:
            hits = [a for a, s in cls if K.assignment_from(A, s) is not None]
            exactly_one &= len(hits) == 1
            for a in hits:
                per[a] += 1
        brute = {a: K.brute_count(s) for a, s in cls}
        good = exactly_one and all(brute[a] == 2 * per[a] for a, _ in cls)
        ok4 &= good
        info4.append((S.name, Dspec or "none", K.chi, len(As), {str(a): brute[a] for a, _ in cls}, good))
    check("4 every corner map A (one corner per line, vertex degrees odd off D and even on D) agrees with exactly one sign class, and each "
          "class has exactly 2 satisfying assignments per corner map it accepts (brute force)", ok4, {"spaces": info4})

    # 5. the sphere: forced only without even faces
    ok5, info5 = True, []
    for k in range(2, 6):
        S = L.octahedral_sphere(k)
        K = L.KnotSpace(S)
        corners = [v for v in range(K.V) if K.d[v] == 2]
        hexes = [v for v in range(K.V) if K.d[v] == 3]
        Ds = {"none": [], "two corners": corners[:2], "two far faces": [corners[0], hexes[-1]], "four corners": corners[:4],
              "six corners (trivial signs)": corners}
        res = {}
        for name, D in Ds.items():
            s = K.signing(D)
            res[name] = K.sat(s)[0]
        good = res["none"] is False and all(v for kk, v in res.items() if kk != "none")
        ok5 &= good
        info5.append((k, K.n, res))
    check("5 on the octahedral spheres K_2..K_5 the knot is unsatisfiable with no even face and satisfiable with 2, 4 or 6", ok5, info5)

    # 6. lattice tori: the triangle criterion against SAT, and the classification
    ok6, n6, kinds = True, 0, {}
    for N in range(1, 41):
        for (p, q, r) in L.hnf_sublattices(N):
            S = L.torus(p, q, r)
            K = L.KnotSpace(S)
            C = L.labelled_classes(K)
            sat = {lab for lab, s in C.items() if K.sat(s)[0]}
            ok6 &= sat == L.satisfiable_classes(p, q, r)
            kind = L.torus_kind(p, q, r)
            if kind == "thin":
                kind += "-even" if N % 2 == 0 else "-odd"
            if (p, q, r) in L.FANO_TORI:
                kind = "Fano"
            key = (kind, 4 - len(sat))
            kinds[str(key)] = kinds.get(str(key), 0) + 1
            n6 += 1
    expect = {"degenerate": 1, "thin-even": 1, "thin-odd": 0, "other": 0, "Fano": 1}
    ok6 &= all(int(k.split(", ")[1].rstrip(")")) == expect[k.split("'")[1]] for k in kinds)
    crit, nc = {}, 0
    for N in range(41, 121):
        for (p, q, r) in L.hnf_sublattices(N):
            kind = L.torus_kind(p, q, r)
            if kind == "thin":
                kind += "-even" if N % 2 == 0 else "-odd"
            key = (kind, 4 - len(L.satisfiable_classes(p, q, r)))
            crit[str(key)] = crit.get(str(key), 0) + 1
            nc += 1
    ok6 &= all(int(k.split(", ")[1].rstrip(")")) == expect[k.split("'")[1]] for k in crit)
    check("6 lattice tori: for every sublattice of index <= 40 the satisfiable classes are exactly the triangle criterion's; unsatisfiable "
          "classes occur exactly on degenerate tori, thin tori of even index (one class each) and the two Fano tori (the untwisted class); "
          "the criterion alone gives the same classification for every index 41..120", ok6,
          {"tori by SAT": n6, "(kind, unsatisfiable classes) by SAT": kinds, "tori by the criterion": nc, "by the criterion": crit})

    # 7. thin tori are cyclic chains, and a violated line is found by binary search
    ok7, info7 = True, []
    for (p, q, r) in [(34, 1, 1), (17, 16, 2), (40, 38, 1), (128, 1, 1), (512, 510, 1), (1024, 1, 1)]:
        S = L.torus(p, q, r)
        K = L.KnotSpace(S)
        ch = L.chain(K)
        good = ch is not None and sorted(ch[0]) == list(range(K.n)) and sorted(c for c, _ in ch[1]) == list(range(K.n))
        C = L.labelled_classes(K)
        miss = [lab for lab in C if lab not in L.satisfiable_classes(p, q, r)]
        good &= len(miss) == 1
        lab = miss[0]
        good &= not K.sat(C[lab])[0]
        mq = 0
        for _ in range(40):
            x = L.random_assignment(K.n, rng)
            li, Q = L.find_violated_line(K, C[lab], x, ch)
            lit = [x[K.pt[li][kk]] ^ C[lab][3 * li + kk] for kk in range(3)]
            good &= li is not None and lit[0] == lit[1] == lit[2]
            mq = max(mq, len(Q))
        import math
        good &= mq <= 2 * math.ceil(math.log2(K.n)) + 8
        ok7 &= good
        info7.append(((p, q, r), K.n, lab, mq))
    check("7 thin tori of even index: every line holds three consecutive slices of one cycle, the missing class is unsatisfiable, and "
          "binary search finds a violated line with at most 2 log2 n + 8 queries", ok7, {"(torus, n, class, most queries)": info7})

    # 8. other surfaces: every sign class satisfiable
    ok8, info8 = True, {}
    kl = []
    for c in (0, 1):
        for m in range(2, 17):
            for h in range(1, 17):
                if m * h > 64:
                    continue
                K = L.KnotSpace(L.klein(m, h, c))
                if not K.simple():
                    continue
                C = L.labelled_classes(K)
                allsat = all(K.sat(s)[0] for s in C.values())
                kl.append(allsat)
    ok8 &= all(kl) and len(kl) > 0
    info8["simple lattice Klein bottles (m*h <= 64, both glide families), every class satisfiable"] = f"{sum(kl)}/{len(kl)}"
    pp = []
    for m in range(1, 7):
        K = L.KnotSpace(L.projective_plane(m))
        corners = [v for v in range(K.V) if K.d[v] == 2]
        others = [v for v in range(K.V) if K.d[v] == 3]
        for D in [corners[:1], corners, rng.sample(others, 1), rng.sample(others, min(3, len(others)))]:
            for a, s in class_signings(K, D):
                pp.append(K.sat(s)[0])
    ok8 &= all(pp)
    info8["projective planes m = 1..6, one or three even faces, both classes"] = f"{sum(pp)}/{len(pp)}"
    g2 = []
    for pqr in [(3, 0, 3), (4, 1, 3), (5, 2, 2), (4, 0, 4), (5, 1, 5), (6, 2, 4), (7, 3, 3)]:
        T = L.torus(*pqr)
        dist = vertex_graph_dist(T, 0)
        for sep in (1, 2, 3):
            far = [v for v, d in dist.items() if d == sep]
            if not far:
                continue
            K = L.KnotSpace(L.double_cover(T, [0, far[0]]))
            g2.append(all(K.sat(s)[0] for _, s in class_signings(K)))
    ok8 &= all(g2)
    info8["genus-2 double covers of tori (two branch points), all 16 classes"] = f"{sum(g2)}/{len(g2)}"
    oc = {}
    for k in (2, 3, 4):
        O = L.octahedral_sphere(k)
        K0 = L.KnotSpace(O)
        corners = [v for v in range(K0.V) if K0.d[v] == 2]
        for b in (2, 4, 6):
            K = L.KnotSpace(L.double_cover(O, corners[:b]))
            res = [K.sat(s)[0] for _, s in class_signings(K)]
            oc[f"K_{k} branched at {b} corners (chi {4 - b})"] = f"{sum(res)}/{len(res)} classes satisfiable"
            ok8 &= (all(res) if b > 2 else not any(res))
    info8["double covers of the knot spheres"] = oc
    check("8 off the sphere every tested sign class is satisfiable: simple lattice Klein bottles, projective planes, genus-2 covers; double "
          "covers of K_k branched at 4 or 6 corners (torus, genus 2) are satisfiable in every class, at 2 corners (a sphere) in none",
          ok8, info8)

    # 9. controls
    ctrl = {}
    S = L.torus(5, 2, 1)
    K = L.KnotSpace(S)
    s = K.signing(())
    bad_chi = any(2 * (K.tallies(s, x)[0] - sum(a // 2 for a in K.tallies(s, x)[1])) != K.chi + 2
                  for x in (L.random_assignment(K.n, rng) for _ in range(5)))
    ctrl["the identity with chi + 2 fails"] = bad_chi
    wrong = 0
    for N in range(2, 25):
        for (p, q, r) in L.hnf_sublattices(N):
            from fractions import Fraction
            import math
            mirrored = set()
            for s_ in range(0, p + 1):
                lo, hi = Fraction(s_ * q, p), Fraction(r) + Fraction(s_ * (q - r), p)
                for t in range(math.ceil(min(lo, hi)), math.floor(max(lo, hi)) + 1):
                    mirrored.add(((p + s_) % 2, (q + r + t) % 2))
            KK = L.KnotSpace(L.torus(p, q, r))
            C = L.labelled_classes(KK)
            sat = {lab for lab, sg in C.items() if KK.sat(sg)[0]}
            wrong += sat != mirrored
    ctrl["a reflected triangle disagrees with SAT on some torus"] = wrong > 0
    K = L.KnotSpace(L.torus(7, 2, 1))
    cls = class_signings(K)
    As = K.matchings(())
    ctrl["counting every corner map for every class (ignoring the signs' holonomy) is wrong on the Fano torus"] = any(
        K.brute_count(sg) != 2 * len(As) for _, sg in cls)
    K = L.KnotSpace(L.torus(35, 1, 1))
    C = L.labelled_classes(K)
    ctrl["odd thin torus: every class satisfiable, so there is nothing to find"] = all(K.sat(sg)[0] for sg in C.values())
    K = L.KnotSpace(L.torus(7, 2, 1))
    C = L.labelled_classes(K)
    ctrl["Fano torus: only the untwisted class fails"] = [lab for lab, sg in C.items() if not K.sat(sg)[0]] == [(0, 0)]
    check("9 controls: each check can fail", all(ctrl.values()), ctrl)

    out = {"status": "passed", "checks": OUT}
    res = HERE / "result.json"
    if "--write" in sys.argv:
        res.write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())
        same = json.loads(json.dumps(out, default=str))["checks"] == old["checks"]
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
