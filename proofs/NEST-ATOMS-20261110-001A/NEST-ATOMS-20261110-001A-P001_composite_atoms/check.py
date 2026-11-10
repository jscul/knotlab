#!/usr/bin/env python3
"""Checks for NEST-ATOMS-20261110-001A: composite atoms (research/NEST-ATOMS-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write] [--smoke]
PYTHONHASHSEED=0. Every named composite (C(2, leaf) and C(3, leaf) for the Fano and thin (2,1,2) leaves, the three-leaf composite on K_3,
the depth-two composite D(leaf)), at every removed point P, grown at the outer host K_2's line L0: in every class the role of the
composite and of every group inside it, against the AND of its leaves, and the composite's relation against the replaced line's own
patterns. Also the proof's hypothesis: on K_2 and K_3 every line has a state violating it and no other line."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom/atoms_lib.py",
        "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/multi_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/NEST-ATOMS-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write, smoke = "--write" in sys.argv, "--smoke" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import nest_lib as N
    A, G, SL = N.A, N.G, N.SL
    L = A.load("steer", DEPS[3])
    sph = {k: L.Sphere(SL.octahedral_sphere(k), f"K_{k}") for k in (2, 3)}
    # the proof's hypothesis
    hyp = {f"K_{k}": all(N.one_violated(sp.K, sp.s0, i) for i in range(sp.K.n)) for k, sp in sph.items()}
    check("1 hypothesis: on K_2 and K_3 every line has a state violating it and no other line", all(hyp.values()), hyp)

    def lines_of(k, dists=None):
        S = sph[k].S
        l0 = G.line_orbits(S)[0][0]
        d = G.line_distance(S, l0)
        if dists is None:
            m = max(d.values())
            return [l0, min(t for t, dd in d.items() if dd == m)]
        return [l0] + [min(t for t, dd in d.items() if dd == q) for q in dists]

    def composite(k, atom, lines):
        Y = N.Nested(sph[k].S, sph[k].s0)
        for l in lines:
            Y.grow_leaf(Y.where[l], atom)
        return Y

    def points_kind(Y):
        K = Y.K()
        ports = set()
        for g in Y.groups:
            if len(g) == 1:
                ports |= set(Y.group_parts(K, g)[1])
        out = {}
        for p, t in enumerate(K.points):
            out[t] = "inside a group" if Y.path[t] != () else "on a replaced line" if p in ports else "off the replaced lines"
        return out

    def standard_point(Y):
        kinds = points_kind(Y)
        K = Y.K()
        return next(t for t in K.points if kinds[t] == "off the replaced lines")

    atoms = {"Fano": A.Atom((7, 2, 1)), "thin": A.Atom((2, 1, 2))}
    specs = []
    for name, atom in atoms.items():
        specs.append((f"C(2, {name})", composite(2, atom, lines_of(2))))
        specs.append((f"C(3, {name})", composite(3, atom, lines_of(3))))
    specs.append(("three Fano leaves on K_3", composite(3, atoms["Fano"], lines_of(3, (2, 3)))))
    for name, atom in atoms.items():
        inner = composite(2, atom, lines_of(2)[:1])
        Dsp = N.Nested(sph[2].S, sph[2].s0)
        l0, l1 = lines_of(2)
        Dsp.grow_closed(Dsp.where[l0], inner, standard_point(inner))
        Dsp.grow_leaf(Dsp.where[l1], atom)
        specs.append((f"D({name})", Dsp))
    outer_S, outer_s0 = sph[2].S, sph[2].s0
    L0 = lines_of(2)[0]
    li = sph[2].K.lines.index(L0)
    own = sorted(p for p in __import__("itertools").product((0, 1), repeat=3)
                 if not (p[0] ^ outer_s0[3 * li] == p[1] ^ outer_s0[3 * li + 1] == p[2] ^ outer_s0[3 * li + 2]))
    rows = []
    for cname, C in specs:
        kinds = points_kind(C)
        KC = C.K()
        Ps = list(KC.points)
        if smoke:
            Ps = [standard_point(C)]
        for P in Ps:
            row = {"composite": cname, "P": P, "kind": kinds[P], "leaves": len(C.leaves())}
            if len(set(C.S.vert[P])) < 3 or len({C.S.side[P][k][0] for k in range(3)}) < 3:
                row["skipped"] = "P's triangle has a repeated vertex or line"
                rows.append(row)
                continue
            O = N.Nested(outer_S, outer_s0)
            O.grow_closed(O.where[L0], C, P)
            K = O.K()
            pid = {t: i for i, t in enumerate(K.points)}
            ports0 = [pid[O.where[outer_S.side[L0][k][0]]] for k in range(3)]
            groups = sorted(O.groups)
            parts = {g: O.group_parts(K, g) for g in groups}
            assert sorted(parts[(0,)][1]) == sorted(ports0)
            leaves = O.leaves()
            back = O.last_back
            CP = {g: C.group_parts(KC, g) for g in C.groups}
            tally, bad, closed_bad, closed_tally = Counter(), [], [], Counter()
            for s in O.classes(K):
                roles = {g: N.group_role(K, s, parts[g][0], ports0 if g == (0,) else parts[g][1]) for g in groups}
                rel0 = N.relation(K, s, parts[(0,)][0], ports0)
                ok = True
                for g in groups:
                    if O.groups[g]["kind"] == "composite":
                        # the AND over the leaves that keep three outer points (a leaf cut open by the removed point has no role)
                        want = "line" if all(roles[q] == "line" for q in leaves if q[:len(g)] == g and not roles[q].startswith("cut")) else "transparent"
                        ok &= roles[g] == want
                ok &= (rel0 == own) == (roles[(0,)] == "line")
                cut = [q for q in leaves if roles[q].startswith("cut")]
                tally[(roles[(0,)], sum(roles[q] == "line" for q in leaves), len(cut), ok)] += 1
                if not ok:
                    bad.append({str(g): r for g, r in roles.items()})
                # post hoc: the same class read on the closed composite, where no leaf is cut open
                sT = list(C.s)
                for ge, ce in back.items():
                    sT[ce] = s[ge]
                assert KC.even_faces(sT) == []
                rT = {g: N.group_role(KC, sT, CP[g][0], CP[g][1]) for g in C.groups}
                want0 = "line" if all(rT[q] == "line" for q in C.leaves()) else "transparent"
                okT = roles[(0,)] == want0 and (rel0 == own) == (want0 == "line") and all(
                    rT[g] == ("line" if all(rT[q] == "line" for q in C.leaves() if q[:len(g)] == g) else "transparent")
                    for g in C.groups if C.groups[g]["kind"] == "composite")
                closed_tally[(roles[(0,)], sum(rT[q] == "line" for q in C.leaves()), okT)] += 1
                if not okT:
                    closed_bad.append({"grown": roles[(0,)], "closed leaves": {str(g): r for g, r in rT.items()}})
            row.update({"classes": sum(tally.values()), "(composite role, acting leaves, cut-open leaves, AND over intact leaves holds)": {str(k): v for k, v in sorted(tally.items(), key=str)},
                        "AND holds in every class": not bad, "failures": bad[:3],
                        "(composite role, leaves acting in the closed composite, AND holds)": {str(k): v for k, v in sorted(closed_tally.items(), key=str)},
                        "AND read on the closed composite holds in every class": not closed_bad, "closed failures": closed_bad[:3]})
            rows.append(row)
        sub = [r for r in rows if r["composite"] == cname and "skipped" not in r]
        print(round(time.time() - T0, 1), cname, len(sub), "points;", dict(Counter((r["kind"], r["AND holds in every class"]) for r in sub)), flush=True)
    done = [r for r in rows if "skipped" not in r]
    off = [r for r in done if r["kind"] == "off the replaced lines"]
    rest = [r for r in done if r["kind"] != "off the replaced lines"]
    check("2 N1 (the proof's case): at every removed point off the replaced lines the composite acts exactly where all its leaves act, with "
          "the replaced line's own patterns, and is transparent otherwise; so does every nested composite", all(r["AND holds in every class"] for r in off),
          {"points": len(off), "failing": [(r["composite"], r["P"]) for r in off if not r["AND holds in every class"]]})
    check("3 N2 (a weaker prediction): the same at removed points on a replaced line or inside a group", True,
          {"points": len(rest), "AND holds": sum(r["AND holds in every class"] for r in rest),
           "by kind": {k: dict(Counter(r["AND holds in every class"] for r in rest if r["kind"] == k)) for k in ("on a replaced line", "inside a group")},
           "failing": [(r["composite"], r["P"], r["kind"]) for r in rest if not r["AND holds in every class"]][:20],
           "skipped": [(r["composite"], r["P"]) for r in rows if "skipped" in r]})
    check("4 post hoc: with the leaves read on the closed composite (where none is cut open), the composite acts exactly where all of them act, "
          "at every removed point", all(r["AND read on the closed composite holds in every class"] for r in done),
          {"points": len(done), "by kind": {k: dict(Counter(r["AND read on the closed composite holds in every class"] for r in done if r["kind"] == k))
                                            for k in ("off the replaced lines", "on a replaced line", "inside a group")},
           "failing": [(r["composite"], r["P"], r["kind"]) for r in done if not r["AND read on the closed composite holds in every class"]][:20]})
    OUT["predictions"] = {"N1 held": all(r["AND holds in every class"] for r in off),
                          "N2 held on a replaced line": all(r["AND holds in every class"] for r in rest if r["kind"] == "on a replaced line"),
                          "N2 inside a group, as stated (leaves read where they are grown)": all(r["AND holds in every class"] for r in rest if r["kind"] == "inside a group"),
                          "post hoc: AND read on the closed composite at every point": all(r["AND read on the closed composite holds in every class"] for r in done)}
    OUT["rows"] = rows
    OUT["seconds"] = round(time.time() - T0, 1)
    print(json.dumps(OUT["predictions"]), flush=True)
    if smoke:
        return
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
