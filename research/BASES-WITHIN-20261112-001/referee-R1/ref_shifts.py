"""Referee BASES-WITHIN-R1: driver for shifts.c (the referee's own liveness test for O[I] with shifted stitches).
Build: gcc -O2 -march=native -o <dir>/shifts shifts.c, and set REF_SHIFTS_EXE=<dir>/shifts (default: ./shifts)."""
import os
import subprocess
from pathlib import Path

import ref_lib as R

HERE = Path(__file__).resolve().parent
EXE = os.environ.get("REF_SHIFTS_EXE", str(HERE / "shifts"))


def encode(h):
    P = h["P"]
    W = R.states(h)
    ints = [sum(b << i for i, b in enumerate(w)) for w in W]
    idx = {w: i for i, w in enumerate(W)}
    reps, seen = [], set()
    for o in h["orbits"]:
        w = tuple(int(o[i % len(o)]) for i in range(P))
        orbit = {tuple(w[(i + r) % P] for i in range(P)) for r in range(P)}
        if orbit & seen:
            continue
        mirror = {tuple(1 - x for x in v) for v in orbit}
        seen |= orbit | mirror
        reps.append(idx[w])
    return P, ints, reps


def header(h, n, E, free):
    P, ints, reps = encode(h)
    s = [f"{P} {len(ints)}", " ".join(map(str, ints)), f"{len(reps)} " + " ".join(map(str, reps)), f"{n} {len(E)}"]
    s += [f"{a} {b} {c}" for a, b, c in E]
    s.append(f"{len(free)} " + " ".join(f"{k} {p}" for k, p in free))
    return "\n".join(s) + "\n"


def exhaustive(h, n, E):
    free = R.incidence_tree(n, E)
    out = subprocess.run([EXE], input=header(h, n, E, free) + "0\n", capture_output=True, text=True, check=True).stdout
    lines = out.strip().split("\n")
    tot = lines[-1].split()
    return {"free shifts": len(free), "classes": int(tot[1]), "dead": int(tot[3]),
            "dead examples": [l.split()[1:] for l in lines[:-1]]}


def listed(h, n, E, assignments):
    s = header(h, n, E, []) + "1\n" + f"{len(assignments)}\n"
    s += "\n".join(" ".join(f"{a} {b} {c}" for (a, b, c) in sh) for sh in assignments) + "\n"
    out = subprocess.run([EXE], input=s, capture_output=True, text=True, check=True).stdout
    return [x == "1" for x in out.split()]
