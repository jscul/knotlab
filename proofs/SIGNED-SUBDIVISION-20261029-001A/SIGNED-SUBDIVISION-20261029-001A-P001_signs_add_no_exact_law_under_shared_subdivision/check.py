"""Checks for SIGNED-SUBDIVISION-20261029-001A-P001 (signs add no exact law under shared subdivision).

Weighted rules: a law with weights plus or minus one on a knot's tuples, on every up triangle (S2) or on every triangle with one
placement for up and one for down triangles (S1); sign patterns up to a global sign per law.  Scale k: the fine sum F(x) over
fine assignments restricting to a coarse assignment x, against the coarse weight W(x) (ss_lib.py).  Exact: F = c W with c != 0;
support-exact: same support (the interference reading of allowed states).
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 34 knots, 122 rule shapes, 135,440 signed rules
  2 unsigned baseline: exact shapes at scale 2 (coarse sides 2, 3) and scale 3 (coarse side 2) are those of SHARED-SUBDIVISION
  3 gauge lemma: S1 edge gauges (a sign function on each edge class, applied to the up and the down triangle that share it) and S2
    unary gauges (sign functions of the three corners whose product is 1) leave F and W unchanged; checked on 200 random
    (rule, gauge) pairs at coarse sides 2 and 3; the orbits of the 135,440 signed rules are counted
  4 census on orbit representatives: support-exact and exact at scale 2 on coarse side 2, then side 3 and side 4 for the survivors,
    and at scale 3 on coarse side 2, then side 3 for the survivors
  5 survivors: support-exact orbits occur only in the counted-exact shapes; at scale 2 every orbit of those 22 shapes is
    support-exact and the exact ones are the unsigned orbit (one of two) for parity and three-excluded, and two of eight for
    twisted not-all-equal; at scale 3, six of the eight orbits of each twisted not-all-equal shape are support-exact, all of
    them exact; the orbits support-exact at coarse side 2 only lie outside the counted-exact shapes
  6 controls that must fire: a weight of magnitude 2 on one tuple of an exact shape breaks exactness; the up part of a gauge
    applied alone (no cancellation) changes F on a shape with many fine assignments; a non-exact shape with the all-plus
    signs stays non-exact
Run: .venv/bin/python -B check.py [--write]   (numpy)"""
import hashlib, itertools, json, os, random, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import ss_lib as S  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1800], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: d for r, d in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1
SHAPES = S.rule_shapes()


def patterns(P1, P2):
    if P2 is None:
        return [(e, None) for e in S.sign_patterns(len(P1))]
    return [(e1, e2) for e1 in S.sign_patterns(len(P1)) for e2 in S.sign_patterns(len(P2))]


n_signed = sum(len(patterns(P1, P2)) for _, P1, P2 in SHAPES)
report("1 knots, rule shapes and signed rules", len(S.K34) == 34 and len(SHAPES) == 122 and n_signed == 135440,
       {"knots": len(S.K34), "shapes": len(SHAPES), "signed rules": n_signed})


def weights(P1, P2, e1, e2):
    return S.wvec(P1, e1), (S.wvec(P2, e2) if P2 is not None else None)


def name(s, P1, P2):
    ex = lambda P: "".join("".join(map(str, t)) + " " for t in sorted(set(S.cube) - P)).strip()
    return f"{s} {S.kind(P1)} excl {ex(P1)}" + (f" / {ex(P2)}" if P2 is not None else "")


# ---------------------------------------------------------------- 2 unsigned baseline
base = {}
for mk in ((2, 2), (3, 2), (2, 3)):
    base[mk] = sorted(name(s, P1, P2) for s, P1, P2 in SHAPES
                      if S.decide(mk[0], mk[1], *weights(P1, P2, [1] * len(P1), [1] * len(P2) if P2 else None),
                                  primes=S.PRIMES[:3])["exact"])
EXACT_SHAPES = set(base[(2, 2)])
report("2 unsigned baseline equals the counted census (22 at scale 2, 6 at scale 3)",
       len(base[(2, 2)]) == 22 and base[(3, 2)] == base[(2, 2)] and len(base[(2, 3)]) == 6,
       {"scale 2, side 2": len(base[(2, 2)]), "scale 2, side 3": len(base[(3, 2)]), "scale 3, side 2": len(base[(2, 3)]),
        "scale 3 shapes": base[(2, 3)]})

# ---------------------------------------------------------------- 3 gauge lemma and orbits
PAIRS = list(itertools.product((0, 1), repeat=2))
SIGNF2 = [dict(zip(PAIRS, v)) for v in itertools.product((1, -1), repeat=4)]
SIGNF1 = [{0: a, 1: b} for a in (1, -1) for b in (1, -1)]


def s1_gauge(hH, hD, hV):
    # up (a,b,c) = sites (i,j),(i+1,j),(i,j+1); down (d,e,f) = (i+1,j),(i,j+1),(i+1,j+1)
    # horizontal edges: up (a,b), down (e,f); diagonal: up (b,c), down (d,e); vertical: up (a,c), down (d,f)
    return (lambda t: hH[(t[0], t[1])] * hD[(t[1], t[2])] * hV[(t[0], t[2])],
            lambda t: hH[(t[1], t[2])] * hD[(t[0], t[1])] * hV[(t[0], t[2])])


def s2_gauge(g1, g2):
    g3 = {x: g1[x] * g2[x] for x in (0, 1)}
    return (lambda t: g1[t[0]] * g2[t[1]] * g3[t[2]], None)


S1G = [s1_gauge(*h) for h in itertools.product(SIGNF2, repeat=3)]
S2G = [s2_gauge(*g) for g in itertools.product(SIGNF1, repeat=2)]


def apply(P, e, g):
    return tuple(x * g(t) for x, t in zip(e, sorted(P)))


def norm(e):
    return None if e is None else tuple(x * e[0] for x in e)


rng = random.Random(29)
inv_bad = 0
for trial in range(200):
    s, P1, P2 = rng.choice(SHAPES)
    e1, e2 = rng.choice(patterns(P1, P2))
    gu, gd = rng.choice(S2G if s == "S2" else S1G)
    f1 = apply(P1, e1, gu)
    f2 = apply(P2, e2, gd) if P2 is not None else None
    m = 2 if trial < 150 else 3
    p = S.PRIMES[0]
    w0 = weights(P1, P2, e1, e2)
    w1 = (S.wvec(P1, f1), S.wvec(P2, f2) if P2 is not None else None)
    if S.fine_sums(m, 2, *w0, p) != S.fine_sums(m, 2, *w1, p) or S.coarse_weights(m, *w0, p) != S.coarse_weights(m, *w1, p):
        inv_bad += 1
ORBITS = []  # (shape index, representative (e1, e2), orbit size)
for si, (s, P1, P2) in enumerate(SHAPES):
    seen = set()
    for e1, e2 in patterns(P1, P2):
        if (e1, e2) in seen:
            continue
        orb = set()
        for gu, gd in (S2G if s == "S2" else S1G):
            orb.add((norm(apply(P1, e1, gu)), norm(apply(P2, e2, gd)) if P2 is not None else None))
        seen |= orb
        ORBITS.append((si, (e1, e2), len(orb)))
report("3 gauge lemma (gauge-related rules have identical fine and coarse sums) and gauge orbits",
       inv_bad == 0 and sum(o[2] for o in ORBITS) == n_signed,
       {"random (rule, gauge) pairs": 200, "mismatches": inv_bad, "orbits": len(ORBITS),
        "orbit sizes sum to the signed rules": sum(o[2] for o in ORBITS) == n_signed})

# ---------------------------------------------------------------- 4 census on representatives
t1 = time.time()
rows = []
for si, (e1, e2), size in ORBITS:
    s, P1, P2 = SHAPES[si]
    w = weights(P1, P2, e1, e2)
    r = {"shape": name(s, P1, P2), "signs": [e1, e2], "orbit": size}
    r["s2 side2"] = S.decide(2, 2, *w, primes=S.PRIMES[:3])
    r["s3 side2"] = S.decide(2, 3, *w, primes=S.PRIMES[:3])
    if r["s2 side2"]["support_exact"] and not r["s2 side2"]["vacuous"]:
        r["s2 side3"] = S.decide(3, 2, *w, primes=S.PRIMES[:3])
        if r["s2 side3"]["support_exact"]:
            r["s2 side4"] = S.decide(4, 2, *w, primes=S.PRIMES[:4])
    if r["s3 side2"]["support_exact"] and not r["s3 side2"]["vacuous"]:
        r["s3 side3"] = S.decide(3, 3, *w, primes=S.PRIMES)
    rows.append(r)
print("   census on representatives:", round(time.time() - t1, 1), "s", flush=True)


def survives(r, scale):
    if scale == 2:
        keys = ("s2 side2", "s2 side3", "s2 side4")
    else:
        keys = ("s3 side2", "s3 side3")
    return all(k in r and r[k]["exact"] and not r[k]["vacuous"] for k in keys)


def support_survives(r, scale):
    keys = ("s2 side2", "s2 side3", "s2 side4") if scale == 2 else ("s3 side2", "s3 side3")
    return all(k in r and r[k]["support_exact"] and not r[k]["vacuous"] for k in keys)


surv2 = [r for r in rows if survives(r, 2)]
surv3 = [r for r in rows if survives(r, 3)]
sup2 = [r for r in rows if support_survives(r, 2)]
sup3 = [r for r in rows if support_survives(r, 3)]
side2_only = [r for r in rows if r["s2 side2"]["support_exact"] and not r["s2 side2"]["vacuous"] and not support_survives(r, 2)]
report("4 census on the gauge-orbit representatives",
       True,
       {"orbits": len(rows), "scale 2 exact (sides 2-4)": len(surv2), "scale 2 support-exact": len(sup2),
        "scale 3 exact (sides 2-3)": len(surv3), "scale 3 support-exact": len(sup3),
        "support-exact at side 2 only (scale 2)": len(side2_only),
        "signed rules in surviving orbits, scale 2": sum(r["orbit"] for r in surv2),
        "signed rules in surviving orbits, scale 3": sum(r["orbit"] for r in surv3)})

# ---------------------------------------------------------------- 5 survivors
SCALE3_SHAPES = set(base[(2, 3)])
exact_orbits_by_shape = Counter(r["shape"] for r in surv2)
exact3_orbits_by_shape = Counter(r["shape"] for r in surv3)
orbits_by_shape = Counter(r["shape"] for r in rows)
unsigned_rows = {r["shape"]: r for r in rows if all(x == 1 for x in r["signs"][0])
                 and (r["signs"][1] is None or all(x == 1 for x in r["signs"][1]))}
c_a = {r["shape"] for r in sup2} <= EXACT_SHAPES and {r["shape"] for r in sup3} <= SCALE3_SHAPES
sup3_by_shape = Counter(r["shape"] for r in sup3)
c_b = all(support_survives(r, 2) for r in rows if r["shape"] in EXACT_SHAPES) and \
    all(orbits_by_shape[sh] == 8 and sup3_by_shape[sh] == 6 for sh in SCALE3_SHAPES) and \
    sorted(id(r) for r in sup3) == sorted(id(r) for r in surv3)
TWISTED = {sh for sh in EXACT_SHAPES if "not-all-equal" in sh}
c_f = all(exact_orbits_by_shape[sh] == (2 if sh in TWISTED else 1) and orbits_by_shape[sh] == (8 if sh in TWISTED else 2)
          for sh in EXACT_SHAPES) and TWISTED == SCALE3_SHAPES
c_c = all(survives(unsigned_rows[sh], 2) for sh in EXACT_SHAPES) and all(survives(unsigned_rows[sh], 3) for sh in SCALE3_SHAPES)
c_d = all(survives(r, 3) for r in surv2 if r["shape"] in SCALE3_SHAPES)
c_e = all(r["shape"] not in EXACT_SHAPES for r in side2_only)
report("5 survivors: no new shape; at scale 2 every sign pattern of a counted-exact shape stays support-exact; exactness keeps the unsigned orbit",
       c_a and c_b and c_c and c_d and c_e and c_f,
       {"(a) support-exact orbits lie in the counted-exact shapes": c_a,
        "(b) scale 2: every orbit of a counted-exact shape is support-exact; scale 3: 6 of 8 orbits per twisted shape, all exact": c_b,
        "(f) exact orbits per shape at scale 2: 1 of 2 (parity, three-excluded), 2 of 8 (twisted not-all-equal)": c_f,
        "(c) the orbit of the unsigned law is exact for every counted-exact shape": c_c,
        "(d) at the scale-3 shapes, every orbit exact at scale 2 is exact at scale 3": c_d,
        "(e) side-2-only orbits are outside the counted-exact shapes": c_e,
        "exact orbits / orbits, scale 2, by shape": {sh: f"{exact_orbits_by_shape[sh]}/{orbits_by_shape[sh]}" for sh in sorted(EXACT_SHAPES)},
        "exact orbits / orbits, scale 3, by shape": {sh: f"{exact3_orbits_by_shape[sh]}/{orbits_by_shape[sh]}" for sh in sorted(SCALE3_SHAPES)},
        "side-2-only shapes": sorted({r["shape"] for r in side2_only})})

# ---------------------------------------------------------------- 6 controls
ctrl = {}
s, P1, P2 = next(x for x in SHAPES if name(*x) in EXACT_SHAPES and x[0] == "S1")
w1, w2 = weights(P1, P2, [1] * len(P1), [1] * len(P2))
w1 = w1.copy(); idx = [t[0] * 4 + t[1] * 2 + t[2] for t in sorted(P1)][0]; w1[idx] = 2
ctrl["magnitude 2 on one tuple of an exact shape breaks exactness"] = not S.decide(3, 2, w1, w2, primes=S.PRIMES[:3])["exact"]
s, P1, P2 = next(x for x in SHAPES if x[0] == "S1" and S.kind(x[1]) == "atom")
e1 = S.sign_patterns(len(P1))[0]; e2 = S.sign_patterns(len(P2))[0]
w0 = weights(P1, P2, e1, e2)
F0 = S.fine_sums(2, 2, *w0, S.PRIMES[0])
changed = None
for gi, (gu, gd) in enumerate(S1G):
    if apply(P1, e1, gu) == tuple(e1):
        continue
    wbad = (S.wvec(P1, apply(P1, e1, gu)), S.wvec(P2, e2))  # the up part of a gauge alone: no cancellation
    if S.fine_sums(2, 2, *wbad, S.PRIMES[0]) != F0:
        changed = gi
        break
ctrl["the up part of a gauge alone changes F (found)"] = changed is not None
s, P1, P2 = next(x for x in SHAPES if x[0] == "S1" and S.kind(x[1]) == "not-all-equal type" and name(*x) not in EXACT_SHAPES)
ctrl["a non-exact shape (unsigned) stays non-exact"] = not S.decide(3, 2, *weights(P1, P2, [1] * len(P1), [1] * len(P2)),
                                                                   primes=S.PRIMES[:3])["exact"]
report("6 controls fire", all(ctrl.values()), ctrl)

out["orbit table"] = rows
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-SUBDIVISION-20261029-001A-P001",
               "status": "Proved" if ok_all else "Failed", "checks": out},
              open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
