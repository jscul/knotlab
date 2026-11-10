#!/usr/bin/env python3
"""Stress test for NEST-ATOMS-20261110-001, one size past its tickets, by their own code:
1. ticket A's AND at every removed point of C(4, Fano) and C(4, thin) (host K_4), grown at the outer host K_2's L0;
2. ticket C's two-level address with the outer host K_3 instead of K_2 (composites C(2, leaf) at K_3's L0 and its farthest line),
   same targets, random.Random(104).
Writes stress_test.json next to this file.

    .venv/bin/python3 -B research/NEST-ATOMS-20261110-001/stress_test.py"""
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A_DIR = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
C_DIR = ROOT / "proofs/NEST-ATOMS-20261110-001C/NEST-ATOMS-20261110-001C-P001_a_two_level_address"
sys.path.insert(0, str(A_DIR))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    import itertools
    import spaces_lib as SP
    N, SL = SP.N, SP.SL
    t0 = time.time()
    SP.SPH[4] = SP.L.Sphere(SL.octahedral_sphere(4), "K_4")
    SP.SPH[3] = SP.SPH.get(3) or SP.L.Sphere(SL.octahedral_sphere(3), "K_3")
    out = {}
    # 1. the AND at every removed point of C(4, leaf)
    S2, s2 = SP.SPH[2].S, SP.SPH[2].s0
    L0 = SP.lines_of(2)[0]
    li = SP.SPH[2].K.lines.index(L0)
    own = sorted(p for p in itertools.product((0, 1), repeat=3) if not (p[0] ^ s2[3 * li] == p[1] ^ s2[3 * li + 1] == p[2] ^ s2[3 * li + 2]))
    res1 = {}
    for leaf in ("Fano", "thin"):
        C = SP.composite(4, SP.ATOMS[leaf], SP.lines_of(4))
        KC = C.K()
        kinds = SP.points_kind(C)
        CP = {g: C.group_parts(KC, g) for g in C.groups}
        tally = Counter()
        for P in KC.points:
            O = N.Nested(S2, s2)
            O.grow_closed(O.where[L0], C, P)
            K = O.K()
            pid = {t: i for i, t in enumerate(K.points)}
            ports0 = [pid[O.where[S2.side[L0][k][0]]] for k in range(3)]
            lines0 = O.group_parts(K, (0,))[0]
            ok = True
            for s in O.classes(K):
                rel = N.relation(K, s, lines0, ports0)
                sT = list(C.s)
                for ge, ce in O.last_back.items():
                    sT[ce] = s[ge]
                want = all(N.group_role(KC, sT, CP[q][0], CP[q][1]) == "line" for q in C.leaves())
                ok &= (rel == own) if want else (len(rel) == 8)
            tally[(kinds[P], ok)] += 1
        res1[leaf] = {str(k): v for k, v in tally.items()}
    out["1 AND at every removed point of C(4, leaf), leaves read on the closed composite"] = {
        "per leaf": res1, "holds everywhere": all("False" not in k for r in res1.values() for k in r)}
    print(json.dumps(out), round(time.time() - t0, 1), flush=True)
    # 2. ticket C with the outer host K_3
    Cmod = load("nest_c", C_DIR / "check.py")
    Q = Cmod.load("seq_lib", Cmod.DEPS[0])

    def role(K, Y, s, j):
        lines, outer, _ = Y.parts[j]
        return N.group_role(K, s, lines, outer)
    Q.LH.atom_role = role
    rng = random.Random(104)
    res2 = {}
    for leaf in ("Fano", "thin"):
        O = N.Nested(SP.SPH[3].S, SP.SPH[3].s0)
        for l in SP.lines_of(3):
            Cc = SP.C2(leaf)
            O.grow_closed(O.where[l], Cc, SP.standard_point(Cc))
        K = O.K()
        Y = Cmod.Shim(O, K)
        P = Q.C.Space(K, O.S)
        floor2 = abs(K.chi)
        levels = [Y.face_level(v) for v in range(K.V)]
        upper = [p for p in range(K.n) if O.path[K.points[p]] == ()]
        start = next(s for s in O.classes(K) if all(role(K, Y, s, j) == "transparent" for j in range(4)))
        model = K.sat(start)[1]
        cur = (sum(b << e for e, b in enumerate(start)), sum(int(model[p] > 0) << p for p in range(K.n)))
        outcomes, prev = [], Q.acting(K, Y, cur[0], 4)
        for target in Cmod.TARGETS:
            found, size = Q.search_from(Y, K, P, cur, set(target), 4, levels)
            if not found:
                outcomes.append("write failed")
                continue
            s, x = found
            x ^= 1 << rng.choice(upper)
            s, x, w = Q.m1(P, s, x, floor2, rng)
            after = Q.acting(K, Y, s, 4) if w == floor2 else None
            outcomes.append("held" if after == tuple(target) else "not at the floor" if after is None else "previous address" if after == prev else "other")
            prev = tuple(target)
            cur = (s, x) if w == floor2 else found
        res2[leaf] = dict(Counter(outcomes))
    out["2 ticket C with the outer host K_3"] = res2
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
