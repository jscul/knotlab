"""Stress test one size past KNOTS-ALONE-20261111-001A-E001 (the pre-registration's stop rule).

- P5 one size past: every lattice torus with 25 <= V <= 30 that NAE reads faithfully, beta(0, v) against delta(0, v) + 1 for
  every v with delta in {1, 2, 3}, from the full list of NAE states (SAT enumeration), bonds of size <= 6.
- P2 and P4 one size past: every 6-regular surface with V = 17 and 18 (exhaustive SAT), NAE readings, Klein bottles included.

Run from the repository root with the workspace .venv; writes stress_test.json and stress_test_log.txt beside this file.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A",
                                "KNOTS-ALONE-20261111-001A-E001_knots_alone_census"))
import knots_alone as ka  # noqa: E402

LOG = open(os.path.join(HERE, "stress_test_log.txt"), "w")


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def least_bond(states, src, v, others, kmax):
    full = {}

    def is_full(vars_):
        key = tuple(sorted(vars_))
        if key not in full:
            full[key] = ka.pattern_count(states, key) == 1 << len(key)
        return full[key]

    rest = [w for w in others if w != v]
    for k in range(3, kmax + 1):
        for extra in itertools.combinations(rest, k - 2):
            S = (src, v) + extra
            if not is_full(S) and all(is_full([x for x in S if x != y]) for y in S):
                return k - 1
    return None


def main():
    t0 = time.time()
    out = {"P5": [], "P2P4": []}
    for V in range(25, 31):
        for T in ka.lattice_tori(V):
            r = ka.read_law_sat(V, T, ka.LAWS["NAE"])
            rec = {"V": V, "faithful": r.get("faithful"), "nonfacial_triangle": ka.has_nonfacial_triangle(V, T)}
            if r.get("faithful"):
                st = ka.enumerate_states_sat(V, T, ka.LAWS["NAE"], cap=2_000_000)
                if st is None:
                    rec["states"] = "over cap"
                else:
                    rec["states"] = int(len(st))
                    delta = ka.graph_distance(V, T, 0)
                    others = [w for w in range(V) if w != 0]
                    table = Counter()
                    for v in others:
                        if delta[v] <= 3:
                            table[(delta[v], least_bond(st, 0, v, others, 6))] += 1
                    rec["table"] = sorted([[d, b, n] for (d, b), n in table.items()], key=lambda x: (x[0], x[1] or 0))
                    rec["violations"] = [[d, b, n] for d, b, n in rec["table"] if b != d + 1]
            out["P5"].append(rec)
            log("P5 V", V, rec, round(time.time() - t0, 1), "s")
    for V in (17, 18):
        reps, n = ka.surface_worlds_sat(V, 6)
        for T in reps:
            r = ka.read_law_sat(V, T, ka.LAWS["NAE"])
            rec = {"V": V, "orientable": ka.orientable(T), "nonfacial_triangle": ka.has_nonfacial_triangle(V, T),
                   "three_colourable": ka.three_colouring(V, T) is not None, "NAE": r}
            out["P2P4"].append(rec)
            log("P2/P4 V", V, rec, round(time.time() - t0, 1), "s")
    out["P5 violations"] = [[r["V"]] + v for r in out["P5"] for v in r.get("violations", [])]
    out["P2 failures"] = [r for r in out["P2P4"] if not r["nonfacial_triangle"] and not r["NAE"].get("faithful")]
    out["Klein NAE allowed"] = sum(1 for r in out["P2P4"] if not r["orientable"] and r["NAE"]["allowed"])
    out["seconds"] = round(time.time() - t0, 1)
    log(json.dumps({k: out[k] for k in ("P5 violations", "P2 failures", "Klein NAE allowed", "seconds")}, default=str))
    with open(os.path.join(HERE, "stress_test.json"), "w") as f:
        json.dump(out, f, default=str)


if __name__ == "__main__":
    main()
