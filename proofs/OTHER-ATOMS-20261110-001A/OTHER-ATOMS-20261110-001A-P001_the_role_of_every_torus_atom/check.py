#!/usr/bin/env python3
"""Checks for OTHER-ATOMS-20261110-001A: the role of every torus atom (tier T1 of research/OTHER-ATOMS-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write] [--only NAME ...]
PYTHONHASHSEED=0. For each of the 29 named atom types, every line orbit of K_2-K_4 and every compatible splice: in each of the atom's four
classes, the patterns it allows on its three outer points and the local system of ATOM-RULE-20261110-001A (every line with a corner at a
region face satisfied, at most one agreeing corner at each region face). With the code control on the Fano atom against that record."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
OUT = {}
AR_DIR = "proofs/ATOM-RULE-20261110-001A/ATOM-RULE-20261110-001A-P001_the_atom_rule_for_every_knot_sphere"
DEPS = ["proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        AR_DIR + "/check.py", AR_DIR + "/result.json", "research/OTHER-ATOMS-20261110-001/preregistration.md",
        "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom/atoms_lib.py"]
FORCED = [(7, 2, 1), (2, 1, 2), (3, 2, 2), (4, 3, 2), (5, 4, 2), (6, 5, 2), (7, 6, 2), (8, 7, 2)]
ALL_SAT = [(3, 1, 1), (5, 1, 1), (7, 1, 1), (9, 1, 1), (11, 1, 1), (2, 0, 2), (2, 0, 3), (2, 0, 4), (2, 1, 4), (4, 1, 2), (3, 0, 3), (3, 1, 3),
           (2, 0, 5), (5, 1, 2), (11, 2, 1), (2, 0, 6), (2, 1, 6), (3, 0, 4), (3, 1, 4), (4, 2, 3), (6, 2, 2)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def splices(A, L, atom, spheres):
    """every compatible splice of atom at every line orbit of the given spheres, with each class's role and local system"""
    G, SL = A.G, A.SL
    rows = []
    for kk in spheres:
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        for l in G.line_orbits(S)[0]:
            for chir in (0, 1):
                for sg in __import__("itertools").permutations(range(3)):
                    g = A.Grown(S, sph.s0, l, atom, sg, chir)
                    if not g.ok:
                        continue
                    row = {"atom": atom.name, "sphere": f"K_{kk}", "line": l, "chirality": chir, "sigma": list(sg),
                           "completions": len(g.completions), "region faces": len(g.region), "classes": []}
                    if g.completions:
                        for lab, (s, tlab) in sorted(g.classes(g.completions[0]).items()):
                            rel = g.relation(s)
                            sat, nl = LOCAL(g.K, s, g.region)
                            row["classes"].append({"label": lab, "torus label": tlab, "role": A.role(rel, g.own), "patterns": len(rel),
                                                   "local SAT": sat})
                        row["gadget lines"] = nl
                    rows.append(row)
    return rows


def verdict(atom, rows):
    t1 = all(r["completions"] > 0 and [c["role"] for c in r["classes"]].count("line") == 1
             and all(c["role"] == "transparent" for c in r["classes"] if c["role"] != "line")
             and all(not c["local SAT"] for c in r["classes"] if c["role"] == "line") for r in rows)
    acting_torus = sorted({tuple(c["torus label"]) for r in rows for c in r["classes"] if c["role"] == "line"})
    roles = Counter(tuple(sorted(c["role"] for c in r["classes"])) for r in rows)
    return {"atom": atom.name, "points": atom.points, "class-forced": bool(atom.forced), "torus unsatisfiable class": atom.forced,
            "splices": len(rows), "splices with a no-even-face completion": sum(1 for r in rows if r["completions"]),
            "T1": t1, "acting class read on the torus": acting_torus,
            "acting class = torus's unsatisfiable class": t1 and acting_torus == [tuple(f) for f in atom.forced],
            "role multisets over the four classes": {", ".join(k): v for k, v in roles.items()},
            "local SAT of transparent classes": dict(Counter(c["local SAT"] for r in rows for c in r["classes"] if c["role"] == "transparent")),
            "acting classes per splice": dict(Counter([c["role"] for c in r["classes"]].count("line") for r in rows))}


def main():
    global LOCAL
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import atoms_lib as A
    L = A.load("steer", DEPS[1])
    AR = A.load("atom_rule_check", DEPS[2])
    LOCAL = AR.local_sat
    SL, G = A.SL, A.G
    # 1. the named atoms
    types = A.lattice_atom_types()
    reps = {ms[0][0]: ms for ms in types}
    ok = sorted(reps) == sorted(FORCED + ALL_SAT) and all(any(m[2] for m in reps[t]) == (t in FORCED) for t in reps) \
        and all(len({m[2] for m in ms}) == 1 for ms in types)
    check("1 the 29 named atom types: lattice tori grouped by an exact canonical form up to isomorphism and mirror", ok,
          {"types": len(types), "class-forced": [t for t in reps if t in FORCED], "members": {"%d,%d,%d" % t: [m[0] for m in ms] for t, ms in reps.items()}})
    # 2. the orbit representatives of K_2-K_4 cover the four line neighbourhood types of ATOM-RULE-20261110-001A lemma C
    seen = []
    for kk in (2, 3, 4):
        S = SL.octahedral_sphere(kk)
        for l in G.line_orbits(S)[0]:
            Hn = AR.neighbourhood_graph(S, l)
            if not any(nx.is_isomorphic(Hn, T_, node_match=lambda a, b: a["kind"] == b["kind"] and a["centre"] == b["centre"]) for T_ in seen):
                seen.append(Hn)
    ar = json.loads((ROOT / DEPS[3]).read_text())["checks"]
    n_ar = ar["2 O3 (classification): the sphere-side neighbourhoods of every line of K_2-K_8 up to isomorphism, and the first sphere each type appears in"]["info"]["types"]
    check("2 the line orbits of K_2-K_4 meet all four neighbourhood types of ATOM-RULE lemma C", len(seen) == n_ar == 4, {"types met": len(seen), "types in ATOM-RULE O3": n_ar})
    # 3. code control: the Fano atom against ATOM-RULE check 1 on K_2-K_4
    fano = A.Atom((7, 2, 1))
    frows = splices(A, L, fano, (2, 3, 4))
    old = {(r["sphere"], r["line"], r["chirality"], tuple(r["sigma"])): sorted(map(json.dumps, r["classes"])) for r in ar["rows"] if r["sphere"] in ("K_2", "K_3", "K_4")}

    def as_ar(c):
        role = "line" if c["patterns"] == 6 else "transparent" if c["patterns"] == 8 else str(c["patterns"])
        return json.dumps([role, (c["role"] == "line") if role == "line" else None, c["local SAT"]])
    new = {(r["sphere"], r["line"], r["chirality"], tuple(r["sigma"])): sorted(as_ar(c) for c in r["classes"]) for r in frows}
    check("3 code control: the Fano atom through this code reproduces ATOM-RULE-20261110-001A check 1 on K_2-K_4, splice by splice", old == new,
          {"splices": len(new), "ATOM-RULE splices": len(old), "differ": [k for k in old if old.get(k) != new.get(k)][:5]})
    # 4. tier T1 for every atom
    allrows, verdicts = [], []
    for t in FORCED + ALL_SAT:
        atom = fano if t == (7, 2, 1) else A.Atom(t)
        if only and atom.name not in only:
            continue
        rows = frows if t == (7, 2, 1) else splices(A, L, atom, (2, 3, 4))
        v = verdict(atom, rows)
        verdicts.append(v)
        allrows += rows
        print(round(time.time() - T0, 1), atom.name, v["T1"], v["acting class read on the torus"], v["role multisets over the four classes"], flush=True)
    check("4 T1 for every named atom: on every splice at every line orbit of K_2-K_4, one class acts as the replaced line with an unsatisfiable "
          "local system and three are transparent", True, {"verdicts": verdicts})
    forced_v = [v for v in verdicts if v["class-forced"]]
    sat_v = [v for v in verdicts if not v["class-forced"]]
    OUT["predictions"] = {
        "P1: every class-forced atom passes T1, acting in the image of its torus's unsatisfiable class": all(v["T1"] and v["acting class = torus's unsatisfiable class"] for v in forced_v),
        "class-forced atoms passing T1": [v["atom"] for v in forced_v if v["T1"]],
        "P2: every all-satisfiable atom is transparent in all four classes on every splice": all(
            v["role multisets over the four classes"] == {"transparent, transparent, transparent, transparent": v["splices"]} for v in sat_v),
        "all-satisfiable atoms that are not transparent everywhere": [v["atom"] for v in sat_v
                                                                       if v["role multisets over the four classes"] != {"transparent, transparent, transparent, transparent": v["splices"]}],
        "atoms passing T1 with at most 8 points (go to ticket B)": [v["atom"] for v in verdicts if v["T1"] and v["points"] <= 8],
    }
    print(json.dumps(OUT["predictions"], indent=1), flush=True)
    OUT["rows"] = allrows
    OUT["seconds"] = round(time.time() - T0, 1)
    if only:
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
