#!/usr/bin/env python3
"""Checks for HANDLE-LOCALITY-20261103-001A: access is local; plane pieces keep it.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About five minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/PLANAR-THEOREM-20261102-001A/PLANAR-THEOREM-20261102-001A-P001_the_access_lemma_by_discrete_convexity"))
import planar_lib as PL  # noqa: E402
import potential_lib as POT  # noqa: E402

G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

src = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
exec(src[src.index("def tied_to("):src.index("def classify_pinnings(")])


def solve(lines, signs, pts):
    """solutions of a signed system on the listed points (columns in that order)"""
    idx = {p: i for i, p in enumerate(pts)}
    return G.states(len(pts))[G.sat_matrix([tuple(idx[q] for q in L) for L in lines], signs, len(pts)).all(axis=1)]


def pinnings(A, n, lines, cand, label):
    """every ordered pinning (p, a) of a six-pattern line by points of cand, classified relative to p; label(p, a) names the pair"""
    out = collections.Counter()
    tie = {p: tied_to(A, p, n) for p in range(n)}  # noqa: F821
    for L1 in lines:
        X = list(L1)
        I = {tuple(int(b) for b in r) for r in A[:, X]}
        if len(I) != 6:
            continue
        sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
        for p in cand:
            if p in X:
                continue
            tied = [i for i, y in enumerate(X) if y in tie[p]]
            for a in cand:
                if a == p or a in X or a in tie[p]:
                    continue
                for pv, av in itertools.product((0, 1), repeat=2):
                    rows = A[(A[:, p] == pv) & (A[:, a] == av)]
                    pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                    if len(pats) != 1:
                        continue
                    tau = next(iter(pats))
                    oi = odd_index(tau, sigma)  # noqa: F821
                    if tied:
                        kind = "(i)" if tied[0] != oi else "(i')"
                    else:
                        j, k = [i for i in range(3) if i != oi]
                        allowed = {(int(r[X[j]]), int(r[X[k]])) for r in A if int(r[p]) == pv}
                        excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                        kind = "(iv)" if not excl else ("(ii)" if any((e[0] != tau[j]) + (e[1] != tau[k]) == 1 for e in excl) else "(ii')")
                    out[(label(p, a), kind)] += 1
    return out


SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
PLANE = [("census %d" % idx, H, s, n) for idx, (H, s, n) in SP.items() if PL.incidence_planar(H)]
for size, seeds in ((10, range(3)), (12, range(3)), (14, range(2))):
    for seed in seeds:
        g = PL.grow(size, seed)
        for swap in (False, True):
            PLANE.append(("grown %d points, seed %d%s" % (size, seed, ", dual reading" if swap else ""),) + PL.to_space(g, swap))
for k in (5, 6, 7):
    for swap in (False, True):
        PLANE.append(("prism over a %d-cycle%s" % (2 * k, ", dual reading" if swap else ""),) + PL.to_space(PL.prism(k), swap))

# ------------------------------------------------------------------------------------------------ 1. point splits
info1 = collections.Counter()
ok1 = True
for name, H, s, n in PLANE:
    faces, corners = POT.faces_with_corners(H)
    sign = {(k, p): s[k][j] for k, L in enumerate(H) for j, p in enumerate(L)}
    par = collections.Counter()
    for (k, fi, p, q) in corners:
        par[fi] += 1 + (sign[(k, p)] ^ sign[(k, q)])
    kast = len(faces) == n + 2 and all(par[fi] % 2 == 1 for fi in range(len(faces)))
    ok1 &= kast
    info1["plane spaces with Kasteleyn signs (n + 2 faces, all odd)"] += kast
    for z in range(n):
        through = [k for k, L in enumerate(H) if z in L]
        port = {k: n + i for i, k in enumerate(through)}
        lines = [tuple(port[k] if q == z else q for q in L) for k, L in enumerate(H)]
        # faces of the split system, inherited from the embedding of H: the three faces at z merge into one
        at_z = {fi for fi, f in enumerate(faces) if ("p", z) in f}
        fpar = collections.Counter()
        for (k, fi, p, q) in corners:
            fpar["merged" if fi in at_z else fi] += 1 + (sign[(k, p)] ^ sign[(k, q)])
        matching = len(at_z) == 3 and len(fpar) == len(lines) and all(v % 2 == 1 for v in fpar.values())
        ok1 &= matching
        info1["point splits: as many faces as lines, all odd (a plane matching system)"] += matching
        info1["point splits"] += 1
        A = solve(lines, [list(x) for x in s], list(range(n + 3)))     # z itself is left free and unused
        cand = [q for q in range(n + 3) if q != z]
        c = pinnings(A, n + 3, lines, cand, lambda p, a: ("port" if p >= n else "point") + " as p, " + ("port" if a >= n else "point") + " as a")
        for k_, v in c.items():
            info1["pinnings: %s, type %s" % k_] += v
            ok1 &= k_[1] in ("(i)", "(ii)")
check("1 point splits are plane matching systems with access: on 26 plane knot spaces with Kasteleyn signs (census, grown, prisms; to 14 "
      "points), splitting any point into three ports, one per line through it, leaves as many faces as lines, all odd; and every pinning "
      "of a six-pattern line by two untied points (ports included) is of type (i) or (ii) relative to its first point",
      ok1 and info1["point splits"] > 0, dict(info1))


# ------------------------------------------------------------------------------------------------ 2-3. splices
def splice_case(H1, s1, n1, H2, s2, n2, plane1, plane2, info2, info3):
    li, pt = 0, 0
    ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, pt)
    L = H1[li]
    n_rest1 = len(H1) - 1
    relabel, k = {}, 0
    for p in range(n2):
        if p != pt:
            relabel[p] = n1 + k
            k += 1
    through = [i for i, l in enumerate(H2) if pt in l]
    others = [i for i, l in enumerate(H2) if pt not in l]
    h2index = others + through                     # glued line n_rest1 + j is H2's line h2index[j]
    tw = [ss[n_rest1 + len(others) + i][-1] for i in range(3)]
    sorig = [s2[t][list(H2[t]).index(pt)] for t in through]
    pts1 = list(range(n1))
    pts2 = sorted(relabel.values()) + sorted(ports)
    lines1, lines2 = list(range(n_rest1)), list(range(n_rest1, len(ls)))
    ok2 = ok3 = True
    for M in range(len(ls)):
        S = G.removal(ls, ss, n, M)
        A = np.array(S, dtype=np.int8)
        piece_of_M = "H1" if M < n_rest1 else "H2"
        # 2. the interface lemma
        if plane1:
            if piece_of_M == "H1":
                idx = M if M < li else M + 1
                pred, case = G.removal(H1, s1, n1, idx), "H1 piece, removal inside: H1 minus the removed line"
            else:
                pred, case = G.removal(H1, s1, n1, li), "H1 piece, removal outside: H1 minus the gluing line"
            same = {tuple(int(r[q]) for q in pts1) for r in A} == {tuple(int(b) for b in r) for r in pred}
            ok2 &= same
            info2[case + (" (equal)" if same else " (DIFFERENT)")] += 1
        if plane2:
            if piece_of_M == "H2":
                pred = G.removal(H2, s2, n2, h2index[M - n_rest1])
                mapped, consistent = set(), True
                for r in A:
                    x0 = [int(r[L[i]]) ^ tw[i] ^ sorig[i] for i in range(3)]
                    consistent &= len(set(x0)) == 1
                    mapped.add(tuple(x0[0] if p == pt else int(r[relabel[p]]) for p in range(n2)))
                same = consistent and mapped == {tuple(int(b) for b in r) for r in pred}
                case = "H2 piece, removal inside: H2 minus the removed line (ports read as the split point)"
            else:
                Q = solve([ls[i] for i in lines2], [ss[i] for i in lines2], pts2)
                proj = {tuple(int(r[q]) for q in pts2) for r in A}
                Qs = {tuple(int(b) for b in r) for r in Q}
                if proj == Qs:
                    same, case = True, "H2 piece, removal outside: the point split"
                else:
                    pidx = [pts2.index(q) for q in sorted(ports)]
                    Jeff = {tuple(t[i] for i in pidx) for t in proj}
                    same = proj == {t for t in Qs if tuple(t[i] for i in pidx) in Jeff}
                    case = "H2 piece, removal outside: the point split cut to %d port patterns" % len(Jeff)
            ok2 &= same
            info2[case + (" (equal)" if same else " (DIFFERENT)")] += 1
        # 3. access by piece
        for plane, piece, plines, ppts in ((plane1, "H1", lines1, set(pts1)), (plane2, "H2", lines2, set(pts2))):
            if not plane:
                continue
            c = pinnings(A, n, [ls[i] for i in plines if i != M], range(n),
                         lambda p, a: {(True, True): "both points in the piece", (False, False): "both points outside"}.get(
                             (p in ppts, a in ppts), "one point outside"))
            for (where, kind), v in c.items():
                info3["%s, removal %s the piece, %s: type %s" % ("plane piece", "inside" if piece_of_M == piece else "outside", where, kind)] += v
                if where == "both points in the piece":
                    ok3 &= kind in ("(i)", "(ii)")
    return ok2, ok3


info2, info3 = collections.Counter(), collections.Counter()
ok2 = ok3 = True
GROWN = [("grown %d points, seed %d" % (size, seed),) + PL.to_space(PL.grow(size, seed)) for size, seed in ((10, 0), (10, 1), (12, 0))]
pairs = []
for name, Hp, sp, np_ in GROWN:
    for idx in (21, 58):
        Hf, sf, nf = SP[idx]
        pairs.append((Hf, sf, nf, Hp, sp, np_, False, True))
        pairs.append((Hp, sp, np_, Hf, sf, nf, True, False))
H6, s6, n6 = SP[6]
Hp, sp, np_ = GROWN[0][1:]
pairs.append((H6, s6, n6, Hp, sp, np_, True, True))
pairs.append((Hp, sp, np_, H6, s6, n6, True, True))
for args in pairs:
    a2, a3 = splice_case(*args, info2, info3)
    ok2 &= a2
    ok3 &= a3
check("2 the interface lemma: on 14 splices (the Fano plane and census 58 against three grown plane spaces, both ways round, and census 6 "
      "against a grown plane space, both ways), at every removal, the solutions restricted to a plane piece are exactly those of its "
      "closure minus the removed line (removal inside the piece), or of the closure minus the gluing line, or the point split (removal "
      "outside)", ok2 and sum(info2.values()) > 0, dict(info2))
check("3 access is local: on the same splices, at every removal, every pinning of a six-pattern line of a plane piece by two points of that "
      "piece is of type (i) or (ii) relative to its first point; pinnings by points outside the piece are recorded", ok3, dict(info3))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
