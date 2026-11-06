#!/usr/bin/env python3
"""Checks for FACE-CLAIM-20261103-001B: the census of handles.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About fifteen minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import handles_lib as HL  # noqa: E402

G, HP, CL, PL, SP = HL.G, HL.HP, HL.CL, HL.PL, HL.SP
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def classes_of(hs, allowed):
    e = min(set(itertools.product((0, 1), repeat=3)) - set(allowed))

    def cls(w):
        d = [x ^ y for x, y in zip(w, e)]
        return d.index(1) if sum(d) == 1 else d.index(0)
    return cls


if __name__ == "__main__":
    # -------------------------------------------------------------------------------------------- 0. bindings
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. the spaces
    S = HL.spaces()
    info1 = collections.Counter()
    ok1 = True
    for name, (H, s, n), parts in S:
        ok1 &= G.fails_globally(H, s, n) and not PL.incidence_planar(H) and len(parts) == len(H)
        info1["spaces with %d points" % n] += 1
    geo = CL.Geometry(*HL.LADDER, 0)
    fsize = collections.Counter(fi for (k, fi, p, q) in geo.corners)
    ok1 &= fsize[geo.opp[2]] == 10 and fsize[geo.face_of_arc[(0, 1)]] == 10
    info1["ladder: corners of the face opposite the bottom port, and of the own arc between the other two"] = [fsize[geo.opp[2]], fsize[geo.face_of_arc[(0, 1)]]]
    check("1 the spaces: up to isomorphism, %d non-planar knot spaces (the census's two and the splices of the Fano plane with planar census "
          "spaces, both ways), each failing and minimally so; on the ladder the bottom port's opposite face and the other ports' own arc "
          "are the two long faces" % len(S), ok1 and len(S) == 24, dict(info1))

    # -------------------------------------------------------------------------------------------- 2-3. the census and the rule
    tasks = [(name, X, li, perm) for name, X, parts in S for li in range(len(X[0])) for perm in itertools.permutations(range(3))]
    with Pool(22) as pool:
        res = pool.map(HL.ladder_case, tasks, chunksize=2)
    parts = {name: p for name, X, p in S}
    info2, info3 = collections.Counter(), collections.Counter()
    ok2 = ok3 = True
    by = collections.defaultdict(dict)
    for r in res:
        used = {"opposite": r["halo bottom"] > 0, "own": r["halo top"] > 0}
        ok2 &= r["halo other"] == 0 and r["on bottom"] > 0 and r["on top"] > 0
        by[(r["name"], r["li"])][tuple(r["perm"])] = (used["opposite"], used["own"])
        for face in ("opposite", "own"):
            info3["%s face: claim rule %s, pipeline %s" % (face, r["rule"][face], used[face])] += 1
            info3["%s face: port form %s, pipeline %s" % (face, r["port rule"][face], used[face])] += 1
            ok3 &= r["rule"][face] == used[face] and r["port rule"][face] == used[face]
    sigs = collections.Counter()
    by_part = collections.defaultdict(collections.Counter)
    for (name, li), d in by.items():
        per = collections.defaultdict(set)
        for perm, v in d.items():
            per[perm[2]].add(v)
        ok2 &= all(len(v) == 1 for v in per.values()) and len(per) == 3
        sig = tuple(sorted(("O" if a else "-") + ("W" if b else "-") for (a, b) in (next(iter(per[k])) for k in range(3))))
        sigs[sig] += 1
        if "into" not in name:
            construction = name
        elif name.startswith("Fano"):
            construction = "the Fano plane minus a line spliced into a planar space"
        else:
            construction = "a planar space minus a line spliced into the Fano plane"
        by_part[(construction, parts[name][li])][sig] += 1
    info2["handles (space, removed line)"] = len(by)
    info2["(handle, port order) cases"] = len(res)
    info2["signatures: one entry per bottom port, O = opposite face used, W = own arc used"] = {" ".join(k): v for k, v in sigs.most_common()}
    info2["signatures by construction and part of the removed line"] = {"%s, %s" % k: {" ".join(s): v for s, v in c.items()}
                                                                       for k, c in sorted(by_part.items())}
    check("2 the census: on the ladder, every far halo line lies on the bottom face (the bottom port's opposite face) or the top face (the "
          "own arc of the other two ports); the faces used depend only on which port is at the bottom; nine signatures occur",
          ok2 and len(sigs) == 9, dict(info2))
    check("3 the claim rule and its port form agree with the pipeline on every handle, port order and face", ok3, dict(info3))

    # -------------------------------------------------------------------------------------------- 4. the Fano plane's pins
    HF, sF, nF = SP[21]
    info4 = collections.Counter()
    ok4 = True
    H2, s2, n2 = HL.LADDER
    for li in range(len(HF)):
        hs = HP.HaloSpace(HF, sF, li, H2, s2, n2, 0, G)
        allowed = sorted({w for (w, t) in hs.transfer(hs.nh)})
        cls = classes_of(hs, allowed)
        for M in range(hs.nh):
            meet = [hs.ports.index(q) for q in set(hs.lines[M]) & set(hs.ports)]
            ok4 &= len(meet) == 1
            a = meet[0]
            b, c = [i for i in range(3) if i != a]
            Hand = hs.handle(M)
            rows = [(tuple(int(r[q]) for q in hs.ports), r) for r in Hand]
            for p, q in itertools.combinations(hs.hpts, 2):
                for pv, qv in itertools.product((0, 1), repeat=2):
                    P = {w for w, r in rows if int(r[p]) == pv and int(r[q]) == qv} & set(allowed)
                    if len(P) == 1:
                        info4["pairs pinning one allowed pattern"] += 1
                        info4["... of the class of the port the removal meets"] += cls(next(iter(P))) == a
                        ok4 &= cls(next(iter(P))) == a
            for x in hs.hpts:
                for xv in (0, 1):
                    ex = set(allowed) - {w for w, r in rows if int(r[x]) == xv}
                    byc = collections.Counter(cls(w) for w in ex)
                    eb = [w for w in ex if cls(w) == b]
                    ec = [w for w in ex if cls(w) == c]
                    good = byc[b] == 1 and byc[c] == 1 and byc[a] <= 1 and (eb[0][b], eb[0][c]) != (ec[0][b], ec[0][c])
                    info4["single pins"] += 1
                    info4["single pins excluding one pattern of each other class (and at most one of the met port's), on different "
                          "values of those two ports"] += good
                    ok4 &= good
    check("4 the Fano plane: every removal meets the removed line at one port a; pairs that pin one allowed pattern pin a class-a pattern; "
          "every single pin excludes exactly one allowed pattern of each other class, on different values of those two ports, and at "
          "most one of class a. So a single pin always kills one claim of each own arc at a (one pattern each), and never a whole claim "
          "of the face opposite a (two patterns sharing the other two ports)", ok4, dict(info4))

    # -------------------------------------------------------------------------------------------- 5. census 58's two points
    H58 = SP[58][0]
    pair = [L for L in H58 if {3, 7} <= set(L)]
    thirds = sorted({q for L in pair for q in L} - {3, 7})
    info5 = collections.Counter()
    ok5 = len(pair) == 2 and thirds == [0, 5]
    for (name, li), d in by.items():
        if name != "census 58":
            continue
        for perm, (o, w) in d.items():
            bottom_point = H58[li][perm[2]]
            info5["(line, order) cases"] += 1
            info5["cases with the own arc used exactly when the bottom port is 0 or 5"] += w == (bottom_point in thirds)
            ok5 &= w == (bottom_point in thirds) and o
    check("5 census 58: its lines (5, 7, 3) and (7, 0, 3) share two points; the own arc is used exactly when the bottom port is one of "
          "their third points 0 and 5, and the opposite face always", ok5, dict(info5, **{"the two lines": pair, "their third points": thirds}))

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
