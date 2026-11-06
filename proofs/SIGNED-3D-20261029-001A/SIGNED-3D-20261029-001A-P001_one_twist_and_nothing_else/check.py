"""Checks for SIGNED-3D-20261029-001A-P001 (signed bit laws on ordered triangulations: one twist and nothing else).

The census is exhaustive: a complete SAT encoding of every move identity, solved for every pair of factors, with every support and every
sign pattern enumerated by blocking clauses until the solver reports none left.
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the identities: 10,880 (two orientations; 10 kinds of 2-3 move with 512 boundary labellings, 5 kinds of 1-4 move with 64), identical to
    those of the generator of TWIST-3D-20261025-001A with the full triangle rule
  2 factors: for lambda in {0, +-1, +-2} and mu in {0, +-1, ..., +-16}, a nonzero law exists exactly for (1, 1), (1, 2), (2, 16), their
    negatives, and mu = 0; negating a law sends (lambda, mu) to (-lambda, -mu)
  3 supports: for (1, 1), (1, 2) and (2, 16) the supports are exactly the seven counting supports, the same for both orientations
  4 signs: all sign patterns on each support, split into face-gauge orbits: 1, 1, 1, 2, 2, 4, 1 (twelve classes); every pattern is the same
    for both orientations; the orbits are those of the untwisted law, the twisted Dijkgraaf-Witten law (-1)^(x_01 x_12 x_23) and its
    translate, and the mixed laws on even-or-odd
  5 direct evaluation: the twelve representatives pass every identity, independently of the encoding, and random face gauges keep them passing
  6 the vertex order: exactly the seven untwisted classes have a member that is the same for both orientations and invariant under the 24
    vertex permutations
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat; about two minutes)"""
import hashlib, importlib.util, itertools, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import signed3d_lib as L  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the identities
ids = L.identities()
twp = os.path.join(ROOT, "proofs/TWIST-3D-20261025-001A/TWIST-3D-20261025-001A-P001_twists_add_nothing_to_counting/check.py")
spec = importlib.util.spec_from_file_location("twist3d_check", twp)
tw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tw)
theirs = tw.identities(frozenset(tw.CUBE), oriented=True)
same = theirs == ids
kinds = {"2-3": sum(1 for k, _, _ in ids if k == 0), "1-4": sum(1 for k, _, _ in ids if k == 1)}
report("1 the 10,880 identities equal those of TWIST-3D-20261025-001A (full triangle rule, both orientations)", same and len(ids) == 10880,
       {"identities": len(ids), "by kind": kinds, "identical to TWIST-3D generator": same})

# ---------------------------------------------------------------- 2 factors
C = L.Census(ids)
feas = [(lam, mu) for lam in L.LAMS for mu in L.MUS if C.solve(lam, mu) is not None]
want = {(1, 1), (1, 2), (2, 16), (-1, -1), (-1, -2), (-2, -16)} | {(lam, 0) for lam in L.LAMS}
neg_ok = True
for lam, mu in ((1, 1), (1, 2), (2, 16)):
    W = C.weights(C.solve(lam, mu))
    neg_ok &= L.direct_ok(ids, W, lam, mu) and L.direct_ok(ids, {k: -v for k, v in W.items()}, -lam, -mu)
report("2 factors: nonzero laws exist exactly for (1,1), (1,2), (2,16), their negatives, and mu = 0", set(feas) == want and neg_ok,
       {"feasible (lambda, mu)": feas, "clauses": len(C.cl), "negating a law negates both factors": neg_ok})

# ---------------------------------------------------------------- 3 supports
sup_found, sup_ok = {}, True
for lam, mu in ((1, 1), (1, 2), (2, 16)):
    sups = C.supports(lam, mu)
    names = []
    for sp in sups:
        nm = next((n for n, S in L.SUPPORTS.items() if S == sp[1] == sp[-1]), None)
        names.append(nm)
        sup_ok &= nm is not None and L.FACTORS[nm] == (lam, mu)
    sup_found[f"({lam}, {mu})"] = sorted(str(n) for n in names)
sup_ok &= sorted(n for v in sup_found.values() for n in v) == sorted(L.SUPPORTS)
report("3 supports are exactly the seven counting supports, the same for both orientations", sup_ok, sup_found)

# ---------------------------------------------------------------- 4 signs and orbits
REPS = {("all 0", "untwisted"): L.law(L.SUPPORTS["all 0"]), ("all 1", "untwisted"): L.law(L.SUPPORTS["all 1"]),
        ("all equal", "untwisted"): L.law(L.SUPPORTS["all equal"]), ("free", "untwisted"): L.law(L.SUPPORTS["free"]),
        ("even cocycles", "untwisted"): L.law(L.ZEVEN), ("even cocycles", "twisted"): L.law(L.ZEVEN, L.twist_even),
        ("odd cocycles", "untwisted"): L.law(L.ZODD), ("odd cocycles", "twisted"): L.law(L.ZODD, L.twist_odd),
        ("even or odd", "untwisted"): L.mixed(False, False), ("even or odd", "twisted on even"): L.mixed(True, False),
        ("even or odd", "twisted on odd"): L.mixed(False, True), ("even or odd", "twisted on both"): L.mixed(True, True)}
orb_rep, orb_ok, all_sols = {}, True, {}
for name, S in L.SUPPORTS.items():
    lam, mu = L.FACTORS[name]
    sols = C.sign_solutions(lam, mu, {1: S, -1: S})
    all_sols[name] = sols
    orbits = {}
    for W in sols:
        orbits.setdefault(L.orbit_key(W), []).append(W)
    orient = all(W[(1, l)] == W[(-1, l)] for W in sols for l in L.LABS)
    reps = {kind: L.orbit_key(W) for (nm, kind), W in REPS.items() if nm == name}
    hit = sorted(kind for kind, key in reps.items() if key in orbits)
    orb_ok &= orient and len(hit) == len(reps) == len(orbits) and len(set(reps.values())) == len(reps)
    orb_rep[name] = {"sign patterns": len(sols), "face-gauge orbits": len(orbits), "orbit sizes": sorted(len(v) for v in orbits.values()),
                     "same for both orientations": orient, "orbits identified": hit}
orb_ok &= sum(v["face-gauge orbits"] for v in orb_rep.values()) == 12
report("4 twelve classes up to face gauge: the counting laws, the twisted Dijkgraaf-Witten law, its translate and the mixed laws", orb_ok, orb_rep)

# ---------------------------------------------------------------- 5 direct evaluation and the gauge
rng = random.Random(20261029)
dir_ok = {f"{a}: {b}": L.direct_ok(ids, W, *L.FACTORS[a]) for (a, b), W in REPS.items()}
g_ok = True
for (a, b), W in list(REPS.items())[:12]:
    for _ in range(3):
        tau = {f: rng.choice((1, -1)) for f in itertools.product((0, 1), repeat=3)}
        g_ok &= L.direct_ok(ids, L.gauge(W, tau), *L.FACTORS[a])
report("5 the twelve representatives pass every identity by direct evaluation; random face gauges keep them passing",
       all(dir_ok.values()) and g_ok, {"direct evaluation": dir_ok, "random face gauges (3 per law)": g_ok})

# ---------------------------------------------------------------- 6 the vertex order
symb = {(a, b): L.symmetric_member(W) for (a, b), W in REPS.items()}
sym = {f"{a}: {b}": v for (a, b), v in symb.items()}
sym_ok = all(v == (b == "untwisted") for (a, b), v in symb.items())
report("6 only the untwisted classes have a member invariant under the vertex permutations (the twist needs the order)", sym_ok, sym)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
W = L.law(L.ZEVEN, L.twist_even)
l0 = next(l for l in sorted(L.ZEVEN) if L.twist_even(l) == 1 and any(l))
W2 = dict(W)
W2[(1, l0)] = W2[(-1, l0)] = -1
ctrl["the twisted law with one more sign flipped fails an identity"] = not L.direct_ok(ids, W2, 1, 2)
Wf = L.law(L.SUPPORTS["free"], L.twist_even)
ctrl["the twist on the free support fails for every factor pair"] = not any(L.direct_ok(ids, Wf, lam, mu) for lam in (1, 2) for mu in (1, 2, 16))
fix = [C.nz[(s, l)] if l in L.ZEVEN else -C.nz[(s, l)] for s in (1, -1) for l in L.LABS]
bad = [C.ng[(s, l)] if l == l0 else -C.ng[(s, l)] for s in (1, -1) for l in sorted(L.ZEVEN)]
ctrl["the encoding rejects that flipped pattern"] = C.solve(1, 2, fix + bad) is None
C23 = L.Census(ids, use14=False)
extra = C23.supports(1, 1, cap=40)   # mu is idle here: no 1-4 identities
ctrl["the 2-3 identities alone admit supports outside the seven"] = any(not any(S == sp[1] == sp[-1] for S in L.SUPPORTS.values()) for sp in extra)
m0 = C.solve(1, 0)
ctrl["laws with mu = 0 exist (excluded: the state sum vanishes after any 1-4 move)"] = m0 is not None
report("7 controls fire", all(ctrl.values()), ctrl)

out["classes"] = {f"{a}: {b}": {"support size": len(L.SUPPORTS[a]), "factors": L.FACTORS[a]} for (a, b) in REPS}
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-3D-20261029-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
