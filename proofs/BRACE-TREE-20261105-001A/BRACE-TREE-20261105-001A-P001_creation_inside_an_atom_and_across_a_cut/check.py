#!/usr/bin/env python3
"""Checks for BRACE-TREE-20261105-001A: creation inside an atom and across a cut.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes. About fifteen minutes."""
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
import brace_lib as BL  # noqa: E402

GL = BL.GL
T0 = time.time()
OUT = {}
ID = (0, 1, 2)
F, C = GL.FANO, GL.C58
g = lambda i: ("g", i)  # noqa: E731


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def designs():
    FB, CB = GL.base(*F), GL.base(*C)
    P4, P5 = GL.plane(GL.PL.prism(4)), GL.plane(GL.PL.prism(5))
    off0 = min(k for k, L in enumerate(F[0]) if 0 not in L)
    l0 = next(k for k, L in enumerate(P4.H) if 0 in L)
    return [
        ("the Fano plane, an atom at a point", (FB, [("X", "point", g(0), F, 0, ID)])),
        ("the Fano plane, an atom at a line", (FB, [("Y", "line", g(0), F, 0, ID)])),
        ("the Fano plane, atoms at a point and at a line off it", (FB, [("X", "point", g(0), F, 0, ID), ("Y", "line", g(off0), F, 0, ID)])),
        ("the Fano plane, atoms at two points", (FB, [("X", "point", g(0), F, 0, ID), ("W", "point", g(1), F, 0, ID)])),
        ("the Fano plane, an atom at a point and another on that atom", (FB, [("X", "point", g(0), F, 0, ID), ("Z", "point", ("X", 0), F, 0, ID)])),
        ("census 58, an atom at a point", (CB, [("X", "point", g(0), F, 0, ID)])),
        ("census 58, an atom at a line", (CB, [("Y", "line", g(1), F, 0, ID)])),
        ("prism(4), an atom at a point", (P4, [("X", "point", g(0), F, 0, ID)])),
        ("prism(4), an atom at a line", (P4, [("Y", "line", g(0), F, 0, ID)])),
        ("prism(4), an atom at a line and one at a point on it", (P4, [("X", "point", g(0), F, 0, ID), ("Y", "line", g(l0), F, 0, ID)])),
        ("prism(5), an atom at a point", (P5, [("X", "point", g(0), F, 0, ID)])),
        ("prism(5), an atom at a line", (P5, [("Y", "line", g(0), F, 0, ID)])),
    ]


def census_small(nmax=19):
    sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001B/NATIVE-GENUS-20261104-001B-P001_counting_and_locating_handles"))
    import check as NGB  # noqa: E402
    return [(name, S) for name, S, kinds in NGB.census() if S.n <= nmax]


def atom_lines(S, name):
    """an atom's lines, with the Fano line each one comes from"""
    return {k: S.lkey[k][1] for k in range(len(S.H)) if S.owner[k] == name}


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # ---------------------------------------------------------------------------------------- 1. the Fano plane and census 58 alone
        SF = GL.base(*F)
        rF = GL.matrix(SF, pool=pool)
        SC = GL.base(*C)
        rC = GL.matrix(SC, pool=pool)
        fano_rel = collections.Counter(BL.relation(rF, a, b) for a, b in itertools.combinations(range(7), 2))
        per_far = {fname: sum(1 for M in rF for L, v in rF[M].items() if v and v[i]) for i, (fname, Fs) in enumerate(GL.FARS)}
        two = [(a, b) for a, b in itertools.combinations(range(8), 2) if len(set(C[0][a]) & set(C[0][b])) == 2]
        c58_rel = {"lines sharing two points": collections.Counter(BL.relation(rC, a, b) for a, b in two),
                   "other pairs": collections.Counter(BL.relation(rC, a, b) for a, b in itertools.combinations(range(8), 2) if (a, b) not in two)}
        check("1 the Fano plane alone: every removal creates at every other line, so its seven lines form one block (21 of 21 pairs mutual); "
              "census 58 alone: its three pairs of lines sharing two points are silent", fano_rel == {"mutual": 21} and
              c58_rel["lines sharing two points"] == {"silent": 3},
              {"Fano pairs": dict(fano_rel), "Fano creating entries by far side (of 42)": per_far, "census 58": {k: dict(v) for k, v in c58_rel.items()},
               "census 58 pairs sharing two points": two})

        # ---------------------------------------------------------------------------------------- 2, 3. inside an atom
        D = designs()
        mats = {}
        for label, des in D:
            S = GL.build(des)
            assert len(GL.CL.solutions(S.H, S.s, S.n)) == 0
            mats[label] = (S, des, GL.matrix(S, pool=pool))
        info2, info3, ok2, ok3 = {}, {}, True, True
        for label, (S, des, r) in mats.items():
            for name, kind, key, atom, el, perm in des[1]:
                if atom is not F:
                    continue
                al = atom_lines(S, name)
                same = sum(1 for a, b in itertools.permutations(al, 2) if GL.creates(r, a, b) == GL.creates(rF, al[a], al[b]))
                tot = len(al) * (len(al) - 1)
                blocks = all(GL.creates(r, a, b) for a, b in itertools.permutations(al, 2))
                row = {"atom": name, "entries equal to the Fano plane's": "%d of %d" % (same, tot), "its lines form one block": blocks}
                if kind == "line":
                    info2["%s (%s)" % (label, name)] = row
                    ok2 &= same == tot and blocks
                else:
                    info3["%s (%s)" % (label, name)] = row
                    ok3 &= same == tot and blocks
        check("2 the block lemma for atoms attached at a line (proved: the rest forces the ports constant, so the screening lemma reduces "
              "creation among the atom's lines to the Fano plane's): checked on every design with such an atom", ok2, info2)
        check("3 atoms attached at a point (computed): creation among the atom's lines equals the Fano plane's, so they form a block", ok3, info3)

        # ---------------------------------------------------------------------------------------- 4. across a cut between two atoms
        cen = census_small()
        res_cen = [GL.matrix(S, pool=pool) for name, S in cen]
        spaces = [(label, S, r) for label, (S, des, r) in mats.items()] + [(name, S, r) for (name, S), r in zip(cen, res_cen)]
        table = collections.Counter()
        where = collections.defaultdict(set)
        ncuts = 0
        for label, S, r in spaces:
            owner, types, cuts = BL.braces(S)
            for k, (e, rcv, cutlines) in cuts.items():
                if types[e] != "heawood" or types[rcv] != "heawood":
                    continue
                ncuts += 1
                el = [l for l, b in owner.items() if b == e]
                rl = [l for l, b in owner.items() if b == rcv]
                for a in el:
                    for b in rl:
                        role = "cut line" if b in cutlines else "intact line"
                        rel = BL.relation(r, a, b)
                        table[(role, rel)] += 1
                        where[(role, rel)].add(label)
        info4 = {"(receiver's line, relation of an emitter line to it)": {"%s: %s" % k: v for k, v in sorted(table.items())},
                 "spaces": len(spaces), "cuts between two atoms": ncuts,
                 "spaces showing each case": {"%s: %s" % k: len(v) for k, v in sorted(where.items())}}
        roles = {role: {rel for (ro, rel) in table if ro == role} for role in ("cut line", "intact line")}
        ok4 = roles["intact line"] == {"backward"}
        info4["relations seen at cut lines"] = sorted(roles["cut line"])
        check("4 across a cut between two atoms (computed on the designs and every three-fold space up to 19 points): the receiver's intact "
              "lines create at the emitter's lines, and the emitter's removals never create at them (one-way, against the cut's direction)",
              ok4, info4)

        # ---------------------------------------------------------------------------------------- 5. lines sharing two points
        t5 = collections.Counter()
        for label, S, r in spaces:
            for a, b in itertools.combinations(range(len(S.H)), 2):
                if len(set(S.H[a]) & set(S.H[b])) == 2:
                    t5[BL.relation(r, a, b)] += 1
        check("5 lines sharing two points (doubled squares) never create at each other, in either direction, in the designs and the "
              "three-fold spaces up to 19 points",
              set(t5) == {"silent"}, {"pairs": dict(t5)})

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
