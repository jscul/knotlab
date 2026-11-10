#!/usr/bin/env python3
"""Checks for NATIVE-ATOM-20261110-001B: growth, then learning (research/NATIVE-ATOM-20261110-001/preregistration.md, ticket B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(106). B1 (exact): on K_2 and K_3 at the flat state of the first line-orbit representative, the uniform
rule with the Fano torus and with the thin torus (2,1,2), plain law 000: the grown atom's role and whether the grown space has a satisfying
state. B2 (computed): K_3 with two uniform thin (2,1,2) atoms (at l0 and the first line at the largest distance, every line orbit), from
the first satisfying state, ADDRESS-SEQ-20261110-001A's frozen search writes {0}, {1}, {0} in turn, each followed by a one-point disturbance
and M1."""
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
MULTI = "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/multi_lib.py"
DEPS = [SEQ + "/seq_lib.py", MULTI, "research/NATIVE-ATOM-20261110-001/preregistration.md",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def uniform(A, t):
    atom = A.Atom(t)
    atom.s = [0] * len(atom.s)
    assert atom.K.even_faces(atom.s) == []
    return atom


class Shim:
    def __init__(self, Y, K):
        self.Y = Y
        self.levels = [Y.info[t][0] for t in range(Y.S.nt)]
        self.parts = {j: Y.atom_parts(K, j) for j in range(len(Y.atoms))}

    def face_level(self, v):
        levs = {self.levels[t] for t in range(self.Y.S.nt) if v in self.Y.S.vert[t]}
        if levs == {"U"}:
            return "upper"
        return "atom %d" % next(iter(levs)) if len(levs) == 1 else "junction"


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    M = load("multi_lib", MULTI)
    A, G, SL = M.A, M.G, M.SL
    L = A.load("steer", DEPS[3])
    Q = load("seq_lib", DEPS[0])
    # B1
    rows1 = []
    for k in (2, 3):
        sph = L.Sphere(SL.octahedral_sphere(k), f"K_{k}")
        l0 = G.line_orbits(sph.S)[0][0]
        x = sph.flat_state(sph.K.lines.index(l0))
        for name, t in (("Fano", (7, 2, 1)), ("thin", (2, 1, 2))):
            g, _ = M.first_growth(sph.S, sph.s0, l0, uniform(A, t))
            s = g.completions[0]
            rel = g.relation(s)
            rows1.append({"sphere": f"K_{k}", "atom": name, "role": A.role(rel, g.own), "grown space satisfiable": g.K.sat(s)[0]})
    ok1 = all((r["role"] == "line" and not r["grown space satisfiable"]) if r["atom"] == "Fano" else (r["role"] == "transparent" and r["grown space satisfiable"]) for r in rows1)
    check("1 B1 (exact): the uniform rule grows the Fano atom acting (no satisfying state) and the thin atom transparent (growth resolves)", ok1, {"rows": rows1})
    # B2

    def rel_of(K, s, lines, ports):
        from pysat.solvers import Solver
        cl = []
        for i in lines:
            Lt = [A.lit(K, s, i, kk) for kk in range(3)]
            cl += [Lt, [-a for a in Lt]]
        with Solver(name="cadical153", bootstrap_with=cl) as so:
            return [pat for pat in __import__("itertools").product((0, 1), repeat=3)
                    if so.solve(assumptions=[(p + 1) if b else -(p + 1) for p, b in zip(ports, pat)])]

    def role2(K, Y, s, j):
        lines, _, ports, _, _ = Y.parts[j]
        return {6: "line", 8: "transparent"}.get(len(rel_of(K, s, lines, ports)), "other")
    Q.LH.atom_role = role2
    rng = random.Random(106)
    rows2 = []
    S3 = SL.octahedral_sphere(3)
    sph = L.Sphere(S3, "K_3")
    thin = uniform(A, (2, 1, 2))
    for l0 in G.line_orbits(S3)[0]:
        d = G.line_distance(S3, l0)
        l1 = min(t for t, dd in d.items() if dd == max(d.values()))
        Y = M.Spaced(S3, sph.s0)
        for l in (l0, l1):
            Y.grow(l, thin)
        K = Y.K()
        Sh = Shim(Y, K)
        P = Q.C.Space(K, Y.S)
        floor2 = abs(K.chi)
        levels = [Sh.face_level(v) for v in range(K.V)]
        upper = [p for p in range(K.n) if Sh.levels[K.points[p]] == "U"]
        ok, model = K.sat(Y.s)
        assert ok
        cur = (sum(b << e for e, b in enumerate(Y.s)), sum(int(model[p] > 0) << p for p in range(K.n)))
        start_roles = Q.acting(K, Sh, cur[0], 2)
        steps = []
        for target in ((0,), (1,), (0,)):
            found, size = Q.search_from(Sh, K, P, cur, set(target), 2, levels)
            st = {"target": target, "written": found is not None, "configurations": size}
            if found:
                st["acting after write"] = Q.acting(K, Sh, found[0], 2)
                s, x = found
                x ^= 1 << rng.choice(upper)
                s, x, w = Q.m1(P, s, x, floor2, rng)
                after = Q.acting(K, Sh, s, 2) if w == floor2 else None
                st["acting after disturbance"] = after
                st["held"] = after == target
                cur = (s, x) if w == floor2 else found
            steps.append(st)
        rows2.append({"l0": l0, "l1": l1, "acting at the start": start_roles, "steps": steps})
        print(round(time.time() - T0, 1), l0, start_roles, [(st["written"], st.get("acting after write"), st.get("held")) for st in steps], flush=True)
    allst = [st for r in rows2 for st in r["steps"]]
    check("2 B2 (computed): learning writes single addresses into uniform thin atoms", True,
          {"rows": rows2, "writes": len(allst), "written": sum(st["written"] for st in allst), "held": sum(bool(st.get("held")) for st in allst),
           "exact writes": sum(st.get("acting after write") == st["target"] for st in allst)})
    OUT["predictions"] = {"B1 held": ok1, "B2 every address written": all(st["written"] for st in allst),
                          "B2 every address held": all(st.get("held") for st in allst)}
    print(json.dumps(OUT["predictions"]), flush=True)
    OUT["seconds"] = round(time.time() - T0, 1)
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
